import pygame
import math
import random
from config import *
from config import get_key_binding_manager
from utils import sound_mgr, draw_text, get_plane_surf, get_boss_surf, draw_cyber_rect, log_error, procedural_interceptor_surface, procedural_juggernaut_surface, procedural_swarmer_surface
from systems import arsenal_save_data, create_weapon, WeaponSystem
from talent_system import talent_manager

# ==============================================================================
#   特效与辅助实体
# ==============================================================================
# 【性能优化】粒子系统计数器
_particle_count = 0
MAX_PARTICLES = 300  # 最大粒子数量限制

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, color, mode="spark"):
        global _particle_count
        # 【性能优化】超过限制时随机丢弃部分粒子
        if _particle_count >= MAX_PARTICLES:
            if random.random() < 0.7:  # 70%概率丢弃
                return
        
        super().__init__()
        all_sprites.add(self)
        _particle_count += 1
        self.mode = mode
        self.color = color
        # allow optional parameters for size/speed/life
        self.life = random.randint(15, 30)  # 减少生命周期
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
        self._update_visuals()
    
    def kill(self):
        """【性能优化】覆盖kill方法以减少粒子计数"""
        global _particle_count
        _particle_count = max(0, _particle_count - 1)
        super().kill()
    
    def _update_visuals(self):
        """【性能优化】将视觉更新分离到单独方法"""
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
    def __init__(self, x, y, text, color, font_size=24):
        super().__init__()
        all_sprites.add(self)
        # 避免循环引用 utils.get_font，这里直接使用pygame.font
        font = pygame.font.SysFont(["microsoftyahei", "simhei", "arial"], font_size, bold=True)
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


class DimensionCollapse(pygame.sprite.Sprite):
    """混沌虫洞·维度坍缩 - 全屏虫洞爆发"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120  # 持续2秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.wormholes = []
        self.hit_count = 0
        sound_mgr.play("nuke")
        
        # 在屏幕上创建8个虫洞
        for i in range(8):
            angle = i * (math.pi / 4)
            distance = 200
            wx = WIDTH // 2 + math.cos(angle) * distance
            wy = HEIGHT // 2 + math.sin(angle) * distance
            self.wormholes.append({
                'x': wx,
                'y': wy,
                'radius': 10,
                'rotation': 0,
                'active': True,
                'damage_ticks': 0
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            # 最终爆炸
            for wh in self.wormholes:
                NukeExplosion(center=(int(wh['x']), int(wh['y'])))
            FloatingText(WIDTH // 2, HEIGHT // 2 - 100, f"🌀维度坍缩 x{self.hit_count}", (180, 0, 255))
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        # 更新虫洞
        for wh in self.wormholes:
            wh['radius'] = min(80, wh['radius'] + 1.5)
            wh['rotation'] += 0.15
            
            # 绘制虫洞
            wx, wy = int(wh['x']), int(wh['y'])
            radius = wh['radius']
            
            # 多层旋转环
            for layer in range(5, 0, -1):
                layer_radius = radius * (layer / 5)
                layer_rotation = wh['rotation'] * (1 if layer % 2 else -1)
                
                # 螺旋点
                points = []
                for i in range(12):
                    angle = layer_rotation + (i / 12) * 2 * math.pi
                    distortion = math.sin(self.life * 0.1 + i) * 3
                    px = wx + math.cos(angle) * (layer_radius + distortion)
                    py = wy + math.sin(angle) * (layer_radius + distortion)
                    points.append((px, py))
                
                if len(points) >= 3:
                    layer_r = int(180 * (layer / 5))
                    layer_g = int(255 * (1 - layer / 5))
                    layer_b = 255
                    pygame.draw.polygon(self.image, (layer_r, layer_g, layer_b), points, 2)
            
            # 虫洞伤害判定
            wh['damage_ticks'] += 1
            if wh['damage_ticks'] >= 10:  # 每10帧判定一次
                wh['damage_ticks'] = 0
                for m in list(mobs):
                    dist = math.hypot(m.rect.centerx - wx, m.rect.centery - wy)
                    if dist < radius:
                        dmg = 150
                        m.hp -= dmg
                        self.hit_count += 1
                        FloatingText(m.rect.centerx, m.rect.top - 20, f"-{dmg}", (255, 0, 255))
                        # 吸引效果
                        angle_to_wh = math.atan2(wy - m.rect.centery, wx - m.rect.centerx)
                        m.rect.x += math.cos(angle_to_wh) * 3
                        m.rect.y += math.sin(angle_to_wh) * 3
                        # 粒子效果
                        if random.random() < 0.3:
                            Particle(m.rect.center, (180, 0, 255), mode='star')
        
        # 虫洞间连线
        if self.life % 4 == 0:
            for i, wh1 in enumerate(self.wormholes):
                if i < len(self.wormholes) - 1:
                    wh2 = self.wormholes[i + 1]
                    pygame.draw.line(self.image, (100, 0, 200, 100), 
                                   (int(wh1['x']), int(wh1['y'])),
                                   (int(wh2['x']), int(wh2['y'])), 2)
        
        # 中心坍缩效果
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        collapse_radius = 150 + abs(math.sin(self.life * 0.1)) * 50
        pygame.draw.circle(self.image, (255, 0, 255, 80), (center_x, center_y), int(collapse_radius), 3)

class WormholeLink(pygame.sprite.Sprite):
    """混沌虫洞·虫洞链接 - G键第二大招：创建传送门对"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180  # 持续3秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.portal_pairs = []
        self.hit_count = 0
        self.teleport_cooldown = 0
        sound_mgr.play("nuke")
        
        # 创建4对传送门(共8个)
        for i in range(4):
            angle1 = i * (math.pi / 2)
            angle2 = angle1 + math.pi  # 对面位置
            distance = 250
            
            # 入口虫洞
            p1_x = WIDTH // 2 + math.cos(angle1) * distance
            p1_y = HEIGHT // 2 + math.sin(angle1) * distance
            
            # 出口虫洞
            p2_x = WIDTH // 2 + math.cos(angle2) * distance
            p2_y = HEIGHT // 2 + math.sin(angle2) * distance
            
            self.portal_pairs.append({
                'entrance': {'x': p1_x, 'y': p1_y, 'radius': 5, 'rotation': 0},
                'exit': {'x': p2_x, 'y': p2_y, 'radius': 5, 'rotation': 0},
                'link_alpha': 0
            })
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            FloatingText(WIDTH // 2, HEIGHT // 2 - 100, f"🌀虫洞链接 x{self.hit_count}", (0, 255, 180))
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        # 更新冷却
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1
        
        # 更新传送门对
        for pair in self.portal_pairs:
            entrance = pair['entrance']
            exit_portal = pair['exit']
            
            # 扩大半径
            entrance['radius'] = min(60, entrance['radius'] + 0.8)
            exit_portal['radius'] = min(60, exit_portal['radius'] + 0.8)
            entrance['rotation'] += 0.12
            exit_portal['rotation'] -= 0.12
            
            # 绘制入口虫洞(紫色)
            self._draw_portal(entrance, (180, 0, 255))
            
            # 绘制出口虫洞(青色)
            self._draw_portal(exit_portal, (0, 255, 180))
            
            # 绘制连接线
            pair['link_alpha'] = (pair['link_alpha'] + 5) % 255
            if self.life % 3 == 0:
                pygame.draw.line(self.image, (100, 100, 200, 100),
                               (int(entrance['x']), int(entrance['y'])),
                               (int(exit_portal['x']), int(exit_portal['y'])), 2)
            
            # 传送判定(每5帧一次)
            if self.life % 5 == 0 and self.teleport_cooldown <= 0:
                for m in list(mobs):
                    # 检测是否进入入口
                    dist_to_entrance = math.hypot(m.rect.centerx - entrance['x'], 
                                                 m.rect.centery - entrance['y'])
                    if dist_to_entrance < entrance['radius']:
                        # 传送到出口
                        m.rect.centerx = int(exit_portal['x'])
                        m.rect.centery = int(exit_portal['y'])
                        # 造成伤害
                        dmg = 80
                        m.hp -= dmg
                        self.hit_count += 1
                        FloatingText(m.rect.centerx, m.rect.top - 20, f"-{dmg}", (0, 255, 180))
                        # 特效
                        for _ in range(8):
                            Particle(m.rect.center, (180, 0, 255), mode='spark')
                        self.teleport_cooldown = 3  # 短暂冷却
                        break
    
    def _draw_portal(self, portal, color):
        """绘制单个传送门"""
        px, py = int(portal['x']), int(portal['y'])
        radius = portal['radius']
        rotation = portal['rotation']
        
        # 绘制旋转螺旋
        for layer in range(4, 0, -1):
            layer_radius = radius * (layer / 4)
            points = []
            for i in range(8):
                angle = rotation + (i / 8) * 2 * math.pi
                distortion = math.sin(self.life * 0.08 + i) * 2
                ppx = px + math.cos(angle) * (layer_radius + distortion)
                ppy = py + math.sin(angle) * (layer_radius + distortion)
                points.append((ppx, ppy))
            
            if len(points) >= 3:
                alpha = int(200 * (layer / 4))
                layer_color = (color[0], color[1], color[2])
                pygame.draw.polygon(self.image, layer_color, points, 2)
        
        # 中心光点
        pygame.draw.circle(self.image, (255, 255, 255), (px, py), 3)

class TimeReversal(pygame.sprite.Sprite):
    """混沌虫洞·时空逆流 - C键第三大招：时空倒流"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 90  # 持续1.5秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.affected_enemies = {}  # 记录敌人初始位置
        self.hit_count = 0
        sound_mgr.play("nuke")
        
        # 记录所有敌人的当前位置
        for m in mobs:
            self.affected_enemies[m] = {
                'start_x': m.rect.centerx,
                'start_y': m.rect.centery,
                'pushed_distance': 0
            }
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            FloatingText(WIDTH // 2, HEIGHT // 2 - 100, f"⏪时空逆流 x{self.hit_count}", (120, 0, 200))
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        # 绘制时空漩涡效果
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        for ring in range(5, 0, -1):
            ring_radius = ring * 80 + abs(math.sin(self.life * 0.15)) * 20
            ring_alpha = int(150 * (ring / 5))
            # 逆时针旋转螺旋
            points = []
            for i in range(24):
                angle = -(self.life * 0.1) + (i / 24) * 2 * math.pi
                distortion = math.cos(self.life * 0.12 + i * 0.5) * 15
                rx = center_x + math.cos(angle) * (ring_radius + distortion)
                ry = center_y + math.sin(angle) * (ring_radius + distortion)
                points.append((rx, ry))
            
            if len(points) >= 3:
                ring_color = (int(120 * (ring / 5)), 0, int(200 * (ring / 5)))
                pygame.draw.lines(self.image, ring_color, False, points, 3)
        
        # 时钟刻度
        for i in range(12):
            angle = (i / 12) * 2 * math.pi - self.life * 0.05
            tick_len = 30
            start_r = 280
            sx = center_x + math.cos(angle) * start_r
            sy = center_y + math.sin(angle) * start_r
            ex = center_x + math.cos(angle) * (start_r + tick_len)
            ey = center_y + math.sin(angle) * (start_r + tick_len)
            pygame.draw.line(self.image, (150, 50, 200), (int(sx), int(sy)), (int(ex), int(ey)), 2)
        
        # 对敌人施加时空倒流效果
        for m in list(self.affected_enemies.keys()):
            if m not in mobs:  # 敌人已死亡
                continue
            
            info = self.affected_enemies[m]
            
            # 推回效果：向起始位置推
            dx = info['start_x'] - m.rect.centerx
            dy = info['start_y'] - m.rect.centery
            distance = math.hypot(dx, dy)
            
            if distance > 5:
                # 推回速度
                push_speed = 4
                m.rect.x += int((dx / distance) * push_speed) if distance > 0 else 0
                m.rect.y += int((dy / distance) * push_speed) if distance > 0 else 0
                info['pushed_distance'] += push_speed
                
                # 每推回一定距离造成伤害
                if info['pushed_distance'] >= 20:
                    dmg = 50
                    m.hp -= dmg
                    self.hit_count += 1
                    FloatingText(m.rect.centerx, m.rect.top - 20, f"-{dmg}", (120, 0, 200))
                    info['pushed_distance'] = 0
                    # 粒子效果
                    if random.random() < 0.4:
                        Particle(m.rect.center, (150, 50, 200), mode='spark')
            
            # 减速效果：修改敌人速度(如果有speedx/speedy属性)
            if hasattr(m, 'speedy'):
                m.speedy = max(-1, m.speedy * 0.5)
            if hasattr(m, 'speedx'):
                m.speedx *= 0.5
        
        # 中心时钟符号
        pygame.draw.circle(self.image, (200, 100, 255), (center_x, center_y), 15, 3)
        # 逆时针箭头
        arrow_angle = -self.life * 0.2
        arrow_len = 12
        arrow_x = center_x + math.cos(arrow_angle) * arrow_len
        arrow_y = center_y + math.sin(arrow_angle) * arrow_len
        pygame.draw.line(self.image, (200, 100, 255), (center_x, center_y), 
                        (int(arrow_x), int(arrow_y)), 2)

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
    def __init__(self, x, y, angle=0, is_enemy=False, piercing=0, color=YELLOW, homing=0, bounce=0, b_type="beam", bullet_theme=None, is_split=False, bounce_damage=1.0, damage=0, speed=None):
        super().__init__()
        self.is_enemy = is_enemy
        self.piercing = piercing
        self.homing = homing
        self.bounce = bounce
        self.bounce_damage = bounce_damage  # 【新】弹跳伤害倍数（每次弹跳后伤害衰减）
        self.damage = damage  # 【新】子弹基础伤害
        self.color = color
        self.b_type = b_type
        self.timer = 0
        self._custom_speed = speed  # 【新】自定义速度参数
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
            # ========== Boss 专用子弹类型 ==========
            elif b_type == "spore_mine":  # 孢子地雷 - 菌生蟹皇
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (80, 180, 120), (10, 10), 8)
                pygame.draw.circle(self.image, (120, 220, 160), (10, 10), 6)
                pygame.draw.circle(self.image, (200, 255, 200), (10, 10), 3)
                # 孢子触须
                for i in range(4):
                    angle = i * math.pi / 2
                    x = 10 + int(6 * math.cos(angle))
                    y = 10 + int(6 * math.sin(angle))
                    pygame.draw.line(self.image, (60, 140, 100), (10, 10), (x, y), 2)
                self.speed = 0
            elif b_type == "mycelium_wave":  # 菌丝波浪 - 菌生蟹皇
                self.image = pygame.Surface((18, 12), pygame.SRCALPHA)
                pygame.draw.arc(self.image, (60, 150, 100), (0,0,18,12), 0, 3.14, 3)
                pygame.draw.arc(self.image, (100, 200, 140), (2,2,14,8), 0, 3.14, 2)
                self.speed = 4
            elif b_type == "sandstorm":  # 沙尘暴 - 旱海狂鲨
                self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (200, 170, 100, 150), (12, 12), 10)
                pygame.draw.circle(self.image, (220, 190, 120), (12, 12), 10, 2)
                for i in range(6):
                    angle = i * math.pi / 3
                    x = 12 + int(6 * math.cos(angle))
                    y = 12 + int(6 * math.sin(angle))
                    pygame.draw.circle(self.image, (180, 150, 80), (x, y), 2)
                self.speed = 3
            elif b_type == "rock_shard":  # 岩石碎片 - 旱海狂鲨
                self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, (140, 100, 60), [(7,0), (14,6), (10,14), (4,14), (0,6)])
                pygame.draw.polygon(self.image, (180, 140, 80), [(7,0), (14,6), (10,14), (4,14), (0,6)], 1)
                self.speed = 5
            elif b_type == "plague_bomb":  # 瘟疫炸弹 - 歌莉娅女王
                self.image = pygame.Surface((18, 18), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (80, 180, 40), (9, 9), 7)
                pygame.draw.circle(self.image, (120, 220, 60), (9, 9), 5)
                pygame.draw.circle(self.image, (200, 255, 100), (9, 9), 2)
                self.speed = 4
            elif b_type == "kamikaze_bee":  # 自爆工蜂 - 歌莉娅女王
                self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
                pygame.draw.ellipse(self.image, (255, 200, 50), (3, 4, 8, 6))
                pygame.draw.line(self.image, (50, 50, 50), (5, 7), (3, 3), 1)
                pygame.draw.line(self.image, (50, 50, 50), (9, 7), (11, 3), 1)
                pygame.draw.circle(self.image, (255, 50, 50), (7, 7), 2)
                self.speed = 3
            elif b_type == "rocket_fist":  # 火箭飞拳 - 毁灭魔像
                self.image = pygame.Surface((18, 22), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (100, 60, 40), (3, 0, 12, 16))
                pygame.draw.rect(self.image, (140, 80, 50), (3, 0, 12, 16), 2)
                pygame.draw.polygon(self.image, (255, 100, 50), [(5, 16), (9, 22), (13, 16)])
                self.speed = 6
            elif b_type == "stone_pillar":  # 石柱囚笼 - 毁灭魔像
                self.image = pygame.Surface((16, 40), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (80, 60, 50), (2, 0, 12, 40))
                pygame.draw.rect(self.image, (120, 90, 70), (2, 0, 12, 40), 2)
                self.speed = 0
            elif b_type == "blood_spike":  # 血刺 - 毁灭魔像
                self.image = pygame.Surface((8, 20), pygame.SRCALPHA)
                pygame.draw.polygon(self.image, (180, 30, 30), [(4, 0), (8, 20), (0, 20)])
                pygame.draw.polygon(self.image, (255, 80, 80), [(4, 0), (8, 20), (0, 20)], 1)
                self.speed = 5
            elif b_type == "star_laser":  # 星位激光 - 星神游龙
                self.image = pygame.Surface((6, 30), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (200, 150, 255), (1, 0, 4, 30))
                pygame.draw.rect(self.image, (255, 200, 255), (2, 0, 2, 30))
                self.speed = 0
            elif b_type == "nebula":  # 星云 - 星神游龙
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (150, 100, 200, 150), (10, 10), 8)
                pygame.draw.circle(self.image, (200, 150, 255), (10, 10), 5)
                pygame.draw.circle(self.image, (255, 200, 255), (10, 10), 2)
                self.speed = 4
            elif b_type == "gauss_bomb":  # 高斯炮弹 - 终焉巨械
                self.image = pygame.Surface((22, 22), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 100, 50), (11, 11), 9)
                pygame.draw.circle(self.image, (255, 200, 100), (11, 11), 6)
                pygame.draw.circle(self.image, (255, 255, 200), (11, 11), 3)
                self.speed = 6
            elif b_type == "tesla_arc":  # 特斯拉电弧 - 终焉巨械
                self.image = pygame.Surface((16, 30), pygame.SRCALPHA)
                points = [(8, 0), (4, 10), (12, 18), (8, 30)]
                pygame.draw.lines(self.image, (255, 255, 100), False, points, 3)
                pygame.draw.lines(self.image, (255, 255, 255), False, points, 1)
                self.speed = 12
            elif b_type == "laser_blade":  # 激光刀 - 终焉巨械
                self.image = pygame.Surface((10, 28), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (255, 100, 100), (2, 0, 6, 28))
                pygame.draw.rect(self.image, (255, 200, 200), (3, 0, 4, 28))
                self.speed = 8
            elif b_type == "clock_beam":  # 时钟光束 - 终焉巨械
                self.image = pygame.Surface((8, 40), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (200, 200, 220), (2, 0, 4, 40))
                pygame.draw.rect(self.image, (255, 255, 255), (3, 0, 2, 40))
                self.speed = 10
            elif b_type == "holy_orb":  # 圣茧光球 - 亵渎天神
                self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 220, 150), (8, 8), 6)
                pygame.draw.circle(self.image, (255, 255, 200), (8, 8), 4)
                pygame.draw.circle(self.image, (255, 255, 255), (8, 8), 2)
                self.speed = 2
            elif b_type == "holy_judgment":  # 圣光审判 - 亵渎天神
                self.image = pygame.Surface((10, 35), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (255, 200, 100), (2, 0, 6, 35))
                pygame.draw.rect(self.image, (255, 255, 200), (3, 0, 4, 35))
                self.speed = 4
            elif b_type == "dimension_warning":  # 维度预警 - 维度之噬
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (150, 0, 200), (10, 10), 8, 2)
                pygame.draw.circle(self.image, (200, 50, 255), (10, 10), 4)
                self.speed = 15
            elif b_type == "laser_cage":  # 激光牢笼 - 维度之噬
                self.image = pygame.Surface((6, 50), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (150, 0, 200), (1, 0, 4, 50))
                pygame.draw.rect(self.image, (200, 100, 255), (2, 0, 2, 50))
                self.speed = 0
            elif b_type == "sonic_boom":  # 音爆冲击 - 暴君犽戎
                self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 100, 50, 150), (12, 12), 10, 3)
                pygame.draw.circle(self.image, (255, 200, 100), (12, 12), 6)
                self.speed = 10
            elif b_type == "inferno_meteor":  # 焦土陨石 - 暴君犽戎
                self.image = pygame.Surface((18, 22), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (200, 80, 20), (9, 11), 8)
                pygame.draw.circle(self.image, (255, 150, 50), (9, 11), 5)
                pygame.draw.polygon(self.image, (255, 200, 100), [(6, 0), (9, 6), (12, 0)])
                self.speed = 6
            elif b_type == "phantom_deathray":  # 幻影死光 - 熵之化身
                self.image = pygame.Surface((10, 60), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (255, 255, 255, 200), (2, 0, 6, 60))
                pygame.draw.rect(self.image, (200, 200, 255), (3, 0, 4, 60))
                self.speed = 0
            elif b_type == "life_drain":  # 生命汲取 - 熵之化身
                self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 255, 255, 180), (8, 8), 6)
                pygame.draw.circle(self.image, (200, 200, 255), (8, 8), 4)
                pygame.draw.circle(self.image, (150, 150, 255), (8, 8), 2)
                self.speed = 3
            # ========== Boss 11: 绝音夜煞 子弹类型 ==========
            elif b_type == "echo_pulse":  # 回声脉冲 - 声呐波
                self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (180, 180, 255, 100), (10, 10), 9, 2)
                pygame.draw.circle(self.image, (220, 220, 255, 150), (10, 10), 6, 2)
                pygame.draw.circle(self.image, (255, 255, 255), (10, 10), 3)
                self.speed = 3
            elif b_type == "sonic_scream":  # 尖啸音波 - 锥形声波
                self.image = pygame.Surface((24, 12), pygame.SRCALPHA)
                points = [(0, 6), (24, 0), (24, 12)]
                pygame.draw.polygon(self.image, (200, 200, 255, 180), points)
                pygame.draw.polygon(self.image, (255, 255, 255), points, 2)
                self.speed = 5
            # ========== Boss 12: 棱镜核心 子弹类型 ==========
            elif b_type == "prism_laser":  # 棱镜激光 - 彩虹折射
                self.image = pygame.Surface((8, 40), pygame.SRCALPHA)
                colors = [(255, 100, 100), (255, 200, 100), (100, 255, 100), (100, 200, 255), (200, 100, 255)]
                for i, c in enumerate(colors):
                    pygame.draw.rect(self.image, c, (i + 1, 0, 2, 40))
                self.speed = 8
            elif b_type == "refract_orb":  # 折射光球
                self.image = pygame.Surface((18, 18), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 180, 255, 150), (9, 9), 8)
                pygame.draw.circle(self.image, (200, 255, 255), (9, 9), 5)
                pygame.draw.circle(self.image, (255, 255, 255), (9, 9), 3)
                self.speed = 4
            # ========== Boss 13: 腐朽剑圣 子弹类型 ==========
            elif b_type == "blade_wave":  # 剑气波
                self.image = pygame.Surface((30, 8), pygame.SRCALPHA)
                pygame.draw.arc(self.image, (200, 100, 255), (0, 0, 30, 8), 0, 3.14, 3)
                pygame.draw.line(self.image, (255, 200, 255), (0, 4), (30, 4), 2)
                self.speed = 5
            elif b_type == "iai_slash":  # 居合斩 - 即死横斩
                self.image = pygame.Surface((60, 6), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (200, 50, 255), (0, 1, 60, 4))
                pygame.draw.rect(self.image, (255, 150, 255), (0, 2, 60, 2))
                pygame.draw.circle(self.image, (255, 255, 255), (55, 3), 3)
                self.speed = 20
            # ========== Boss 14: 悖论时钟 子弹类型 ==========
            elif b_type == "stasis_orb":  # 凝滞球 - 时间减速
                self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 220, 100, 150), (8, 8), 7)
                pygame.draw.circle(self.image, (200, 160, 60), (8, 8), 5, 2)
                pygame.draw.line(self.image, (255, 255, 200), (8, 8), (8, 3), 2)
                pygame.draw.line(self.image, (255, 255, 200), (8, 8), (12, 8), 1)
                self.speed = 2
            elif b_type == "frozen_bullet":  # 冻结弹幕 - 蓄力后发射
                self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 200, 50, 100), (7, 7), 6)
                pygame.draw.circle(self.image, (255, 240, 150), (7, 7), 4)
                pygame.draw.circle(self.image, (255, 255, 255), (7, 7), 2)
                self.speed = 0
                self._frozen_timer = 90  # 1.5秒后激活
            elif b_type == "gear_projectile":  # 齿轮弹
                self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (180, 140, 60), (8, 8), 7)
                pygame.draw.circle(self.image, (220, 180, 80), (8, 8), 5)
                for i in range(6):
                    angle = i * 60
                    x = 8 + int(6 * math.cos(math.radians(angle)))
                    y = 8 + int(6 * math.sin(math.radians(angle)))
                    pygame.draw.rect(self.image, (140, 100, 40), (x-1, y-1, 3, 3))
                self.speed = 4
            # ========== Boss 15: 熔核巨兽 子弹类型 ==========
            elif b_type == "lava_wave":  # 岩浆波
                self.image = pygame.Surface((20, 12), pygame.SRCALPHA)
                pygame.draw.ellipse(self.image, (255, 100, 20), (0, 0, 20, 12))
                pygame.draw.ellipse(self.image, (255, 200, 50), (4, 2, 12, 8))
                pygame.draw.ellipse(self.image, (255, 255, 150), (8, 4, 4, 4))
                self.speed = 3
            elif b_type == "molten_meteor":  # 熔岩陨石
                self.image = pygame.Surface((22, 26), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (100, 40, 20), (11, 15), 10)
                pygame.draw.circle(self.image, (200, 80, 30), (11, 15), 7)
                # 火焰尾迹
                pygame.draw.polygon(self.image, (255, 150, 50), [(8, 5), (11, 12), (14, 5), (11, 0)])
                pygame.draw.polygon(self.image, (255, 200, 100), [(9, 4), (11, 10), (13, 4)])
                self.speed = 5
            elif b_type == "lava_burst":  # 岩浆喷射
                self.image = pygame.Surface((10, 20), pygame.SRCALPHA)
                pygame.draw.ellipse(self.image, (255, 80, 20), (0, 0, 10, 20))
                pygame.draw.ellipse(self.image, (255, 180, 50), (2, 4, 6, 12))
                pygame.draw.ellipse(self.image, (255, 255, 150), (3, 8, 4, 6))
                self.speed = 6
            else: 
                # 默认敌方子弹，红色
                self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
                pygame.draw.circle(self.image, CYBER_RED_ALERT, (7,7), 5)
                pygame.draw.circle(self.image, CYBER_RED_ALERT, (7,7), 5, 1)
                pygame.draw.circle(self.image, WHITE, (7,7), 2)
            
            # 【新增】如果传入了自定义速度参数，使用自定义速度
            if self._custom_speed is not None:
                self.speed = self._custom_speed
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
                self.image = pygame.Surface((10, 22), pygame.SRCALPHA)
                pygame.draw.rect(self.image, ORANGE, (2, 7, 6, 12))
                pygame.draw.rect(self.image, CYBER_AMBER, (2, 7, 6, 12), 1)
                pygame.draw.polygon(self.image, CYBER_AMBER, [(2,7), (5,0), (8,7)])
                pygame.draw.rect(self.image, (255, 80, 0), (3, 19, 4, 3))
                pygame.draw.circle(self.image, WHITE, (5, 13), 2)
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
                
            elif b_type == "chrono":  # 17. Chronos - 时之回响（时钟指针子弹）
                self.image = pygame.Surface((24, 36), pygame.SRCALPHA)
                # 时钟外圈
                pygame.draw.circle(self.image, (100, 220, 255), (12, 18), 10, 2)
                pygame.draw.circle(self.image, (50, 180, 255), (12, 18), 8)
                # 时针和分针
                pygame.draw.line(self.image, (255, 200, 100), (12, 18), (12, 10), 3)
                pygame.draw.line(self.image, WHITE, (12, 18), (16, 18), 2)
                # 能量尾迹
                for i in range(3):
                    y_offset = 26 + i * 4
                    alpha = 200 - i * 60
                    glow = pygame.Surface((24, 36), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (100, 220, 255, alpha), (12, y_offset), 6 - i * 2)
                    self.image.blit(glow, (0, 0))
                self.speed = -20
                # 时间子弹特性
                self.chrono_freeze_timer = 0  # 时停计时器
                self.chrono_delayed = False  # 是否延迟爆发
            
            elif b_type == "mirror":  # 18. Mirage - 幻镜棱镜子弹
                self.image = pygame.Surface((24, 32), pygame.SRCALPHA)
                # 三角棱镜形状
                prism_pts = [(12, 2), (2, 28), (22, 28)]
                # 半透明填充
                prism_surf = pygame.Surface((24, 32), pygame.SRCALPHA)
                pygame.draw.polygon(prism_surf, (*color[:3], 180), prism_pts)
                self.image.blit(prism_surf, (0, 0))
                # 边框发光
                pygame.draw.polygon(self.image, (255, 220, 255), prism_pts, 2)
                # 内部折射线
                pygame.draw.line(self.image, (255, 200, 255, 150), (12, 2), (12, 22), 1)
                # 核心光点
                pygame.draw.circle(self.image, (255, 255, 255), (12, 12), 4)
                pygame.draw.circle(self.image, color, (12, 12), 3)
                self.speed = -18
                
            elif b_type == "card":  # 19. Gambit - 扑克牌子弹
                self.image = pygame.Surface((20, 28), pygame.SRCALPHA)
                # 卡牌形状
                card_rect = (2, 2, 16, 24)
                pygame.draw.rect(self.image, (255, 255, 255), card_rect, border_radius=2)
                pygame.draw.rect(self.image, (255, 215, 0), card_rect, 2, border_radius=2)
                # 随机花色（♠♥♦♣）
                suit = random.choice(['spade', 'heart', 'diamond', 'club'])
                if suit == 'spade':
                    # 黑桃
                    pygame.draw.polygon(self.image, (0, 0, 0), [(10, 6), (6, 14), (14, 14)])
                    pygame.draw.circle(self.image, (0, 0, 0), (10, 12), 4)
                    pygame.draw.rect(self.image, (0, 0, 0), (9, 14, 3, 6))
                elif suit == 'heart':
                    # 红心
                    pygame.draw.circle(self.image, (255, 50, 50), (8, 10), 4)
                    pygame.draw.circle(self.image, (255, 50, 50), (12, 10), 4)
                    pygame.draw.polygon(self.image, (255, 50, 50), [(4, 11), (10, 20), (16, 11)])
                elif suit == 'diamond':
                    # 方块
                    diamond_pts = [(10, 6), (5, 13), (10, 20), (15, 13)]
                    pygame.draw.polygon(self.image, (255, 50, 50), diamond_pts)
                else:
                    # 梅花
                    pygame.draw.circle(self.image, (0, 0, 0), (10, 8), 3)
                    pygame.draw.circle(self.image, (0, 0, 0), (7, 12), 3)
                    pygame.draw.circle(self.image, (0, 0, 0), (13, 12), 3)
                    pygame.draw.rect(self.image, (0, 0, 0), (9, 14, 3, 6))
                self.speed = -16
                self.card_suit = suit
            
            elif b_type == "omega_fusion":  # 20. Omega - 终末神兵（七芒星融合弹）
                t = pygame.time.get_ticks() / 1000.0
                self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
                center = 16
                # 七属性颜色
                element_colors = [
                    (255, 80, 30),    # 炎红
                    (100, 200, 255),  # 冰蓝
                    (255, 255, 100),  # 雷黄
                    (150, 255, 80),   # 毒绿
                    (255, 255, 255),  # 圣白
                    (150, 50, 200),   # 暗紫
                    (255, 200, 100),  # 元金
                ]
                # 七芒星外轮廓
                for i in range(7):
                    angle1 = (i * 360 / 7) * math.pi / 180
                    angle2 = ((i + 3) * 360 / 7) * math.pi / 180
                    x1 = center + int(math.cos(angle1) * 14)
                    y1 = center + int(math.sin(angle1) * 14)
                    x2 = center + int(math.cos(angle2) * 14)
                    y2 = center + int(math.sin(angle2) * 14)
                    pygame.draw.line(self.image, element_colors[i], (x1, y1), (x2, y2), 2)
                    # 顶点光球
                    pygame.draw.circle(self.image, element_colors[i], (x1, y1), 3)
                # 核心（白色发光）
                pygame.draw.circle(self.image, (255, 255, 255), (center, center), 8)
                pygame.draw.circle(self.image, color, (center, center), 6)
                pygame.draw.circle(self.image, (255, 255, 200), (center, center), 3)
                self.speed = -25
                
            elif b_type == "genesis_star":  # 21. Genesis - 创世之翼（宇宙创世弹）
                self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
                center = 15
                # 宇宙扩散环
                for ring in range(4):
                    ring_r = 4 + ring * 3
                    alpha = 220 - ring * 50
                    ring_color = (
                        int(255 - ring * 20),
                        int(200 - ring * 30),
                        int(100 + ring * 30)
                    )
                    pygame.draw.circle(self.image, ring_color, (center, center), ring_r, 2)
                # 星系旋臂
                for arm in range(4):
                    arm_angle = arm * 90 * math.pi / 180
                    for seg in range(5):
                        progress = seg / 4
                        seg_angle = arm_angle + progress * math.pi / 2
                        r = progress * 12
                        ax = center + int(math.cos(seg_angle) * r)
                        ay = center + int(math.sin(seg_angle) * r)
                        pygame.draw.circle(self.image, (255, 220, 150), (ax, ay), 2)
                # 核心
                pygame.draw.circle(self.image, (255, 200, 100), (center, center), 6)
                pygame.draw.circle(self.image, (255, 255, 200), (center, center), 4)
                pygame.draw.circle(self.image, (255, 255, 255), (center, center), 2)
                self.speed = -24
            
            elif b_type == "truth_revelation":  # 22. Truth - 至尊·世界的真相（真言之眼弹）
                TRUTH_WHITE = (255, 255, 255)
                TRUTH_BLACK = (20, 20, 30)
                TRUTH_GOLD = (255, 215, 0)
                
                self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
                center = 14
                
                # 外层光环
                pygame.draw.circle(self.image, TRUTH_GOLD, (center, center), 12, 2)
                
                # 眼睛形态
                eye_pts = [
                    (center - 10, center),
                    (center - 5, center - 6),
                    (center, center - 7),
                    (center + 5, center - 6),
                    (center + 10, center),
                    (center + 5, center + 6),
                    (center, center + 7),
                    (center - 5, center + 6),
                ]
                pygame.draw.polygon(self.image, TRUTH_WHITE, eye_pts)
                pygame.draw.polygon(self.image, TRUTH_GOLD, eye_pts, 2)
                
                # 虹膜
                pygame.draw.circle(self.image, TRUTH_GOLD, (center, center), 5)
                
                # 瞳孔
                pygame.draw.circle(self.image, TRUTH_BLACK, (center, center), 3)
                
                # 高光
                pygame.draw.circle(self.image, TRUTH_WHITE, (center - 2, center - 1), 1)
                
                self.speed = -26
            
            elif b_type == "sword_slash":  # 23. Asura - 修罗·斩龙者（剑气斩击）
                ASURA_RED = (180, 50, 50)
                ASURA_CRIMSON = (255, 80, 80)
                ASURA_GOLD = (255, 200, 100)
                
                self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
                center = 24
                
                # 扇形剑气效果
                # 外层剑气（深红）
                arc_pts_outer = []
                for i in range(9):
                    angle = math.radians(-45 + i * 10)
                    x = center + int(20 * math.cos(angle))
                    y = center + int(20 * math.sin(angle))
                    arc_pts_outer.append((x, y))
                arc_pts_outer.append((center, center))
                pygame.draw.polygon(self.image, ASURA_RED, arc_pts_outer)
                
                # 中层剑气（鲜红）
                arc_pts_mid = []
                for i in range(9):
                    angle = math.radians(-45 + i * 10)
                    x = center + int(15 * math.cos(angle))
                    y = center + int(15 * math.sin(angle))
                    arc_pts_mid.append((x, y))
                arc_pts_mid.append((center, center))
                pygame.draw.polygon(self.image, ASURA_CRIMSON, arc_pts_mid)
                
                # 内层剑气（金色核心）
                arc_pts_inner = []
                for i in range(9):
                    angle = math.radians(-45 + i * 10)
                    x = center + int(8 * math.cos(angle))
                    y = center + int(8 * math.sin(angle))
                    arc_pts_inner.append((x, y))
                arc_pts_inner.append((center, center))
                pygame.draw.polygon(self.image, ASURA_GOLD, arc_pts_inner)
                
                # 剑刃边缘线
                for offset in [-45, 45]:
                    angle = math.radians(offset)
                    x1, y1 = center, center
                    x2 = center + int(22 * math.cos(angle))
                    y2 = center + int(22 * math.sin(angle))
                    pygame.draw.line(self.image, (255, 255, 255), (x1, y1), (x2, y2), 2)
                
                # 核心发光点
                pygame.draw.circle(self.image, (255, 255, 255), (center, center), 3)
                
                self.speed = -28
            
            elif b_type == "lance_thrust":  # 24. Dragoon - 龙骑士·雷因哈特（枪刺突击）
                DRAGOON_BLUE = (100, 150, 220)
                DRAGOON_LIGHT = (180, 210, 255)
                DRAGOON_WHITE = (255, 255, 255)
                
                self.image = pygame.Surface((20, 56), pygame.SRCALPHA)
                center_x = 10
                
                # 长枪主体（上到下）
                # 枪尖（锐利三角形）
                tip_pts = [
                    (center_x, 0),
                    (center_x - 6, 14),
                    (center_x + 6, 14)
                ]
                pygame.draw.polygon(self.image, DRAGOON_WHITE, tip_pts)
                pygame.draw.polygon(self.image, DRAGOON_BLUE, tip_pts, 2)
                
                # 枪刃装饰
                blade_pts = [
                    (center_x - 8, 14),
                    (center_x - 4, 10),
                    (center_x, 14),
                    (center_x + 4, 10),
                    (center_x + 8, 14),
                    (center_x + 4, 18),
                    (center_x - 4, 18)
                ]
                pygame.draw.polygon(self.image, DRAGOON_BLUE, blade_pts)
                
                # 枪杆
                pygame.draw.rect(self.image, DRAGOON_LIGHT, (center_x - 3, 18, 6, 32))
                pygame.draw.rect(self.image, DRAGOON_BLUE, (center_x - 3, 18, 6, 32), 1)
                
                # 枪杆装饰环
                for y in [24, 34, 44]:
                    pygame.draw.rect(self.image, DRAGOON_BLUE, (center_x - 4, y, 8, 3))
                
                # 能量光芒（枪尖周围）
                for angle in [-30, 0, 30]:
                    rad = math.radians(angle - 90)
                    x1 = center_x + int(4 * math.cos(rad))
                    y1 = 8 + int(4 * math.sin(rad))
                    x2 = center_x + int(10 * math.cos(rad))
                    y2 = 8 + int(10 * math.sin(rad))
                    pygame.draw.line(self.image, (200, 230, 255), (x1, y1), (x2, y2), 1)
                
                # 核心发光
                pygame.draw.circle(self.image, DRAGOON_WHITE, (center_x, 10), 2)
                
                self.speed = -24
                
            else:  # 默认（紫红幽能，与Specter共用）
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
        
        # ========== Staradia 辉耀天女·斯塔德 子弹形状 (12种独特设计) ==========
        staradia_effects = [
            "rainbow_trail", "prismatic_shimmer", "blade_slash", "prism_shatter",
            "prismatic_split", "spiral_drill", "twilight_gradient", "sunset_trail",
            "aurora_ripple", "polar_light", "constellation_trail", "meteor_shower",
            "dawn_break", "hope_light", "petal_dance", "moon_scatter",
            "fury_explosion", "instant_kill", "dream_float", "starlight_burst",
            "solar_spin", "flame_dance", "void_tear", "space_rend"
        ]
        if any(effect in effects for effect in staradia_effects):
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            
            # 1. 虚空裂隙 - 暗紫撕裂形态
            if "void_tear" in effects or "space_rend" in effects:
                pygame.draw.circle(self.image, (80, 30, 120, 200), (center, center), size//3)
                for i in range(6):
                    angle = i * math.pi / 3
                    spike_len = size//2.5
                    sx = center + int(math.cos(angle) * spike_len)
                    sy = center + int(math.sin(angle) * spike_len)
                    pygame.draw.line(self.image, (120, 40, 100), (center, center), (sx, sy), 2)
                pygame.draw.circle(self.image, (100, 50, 150, 100), (center, center), size//2.5, 2)
                pygame.draw.circle(self.image, (150, 80, 180), (center, center), 3)
            
            # 2. 女皇光剑 - 白色月牙刀刃
            elif "blade_slash" in effects or "prism_shatter" in effects:
                pygame.draw.arc(self.image, (255, 255, 255), (center-size//2, center-size//2, size, size), 0.5, 2.6, 6)
                pygame.draw.arc(self.image, (*color, 200), (center-size//2+2, center-size//2+2, size-4, size-4), 0.5, 2.6, 3)
                # 棱镜碎片
                for i in range(4):
                    px = center + int(math.cos(i * 1.5) * size//3)
                    py = center + int(math.sin(i * 1.5) * size//3)
                    pygame.draw.circle(self.image, (255, 200, 255, 150), (px, py), 2)
            
            # 3. 棱镜光枪 - 彩虹长矛
            elif "prismatic_split" in effects or "spiral_drill" in effects:
                lance_pts = [(center, center - size), (center + size//4, center + size//2), (center - size//4, center + size//2)]
                pygame.draw.polygon(self.image, (*color, 220), lance_pts)
                pygame.draw.polygon(self.image, (255, 255, 255), lance_pts, 2)
                # 彩虹条纹
                rainbow = [(255,100,100), (255,255,100), (100,255,100), (100,255,255), (100,100,255), (255,100,255)]
                for i, rc in enumerate(rainbow):
                    y = center - size//2 + i * size//6
                    pygame.draw.line(self.image, rc, (center - size//6, y), (center + size//6, y), 2)
            
            # 4. 暮星流矢 - 紫金渐变流星箭
            elif "twilight_gradient" in effects or "sunset_trail" in effects:
                arrow_pts = [(center, center - size*3//4), (center + size//3, center + size//3), (center, center), (center - size//3, center + size//3)]
                pygame.draw.polygon(self.image, (180, 100, 220, 220), arrow_pts)
                pygame.draw.polygon(self.image, (255, 200, 100), arrow_pts, 2)
                # 金色尾焰
                for i in range(3):
                    pygame.draw.circle(self.image, (255, 200, 100, 150 - i*40), (center, center + size//3 + i*4), 3-i)
            
            # 5. 极光涟漪 - 青绿波纹环
            elif "aurora_ripple" in effects or "polar_light" in effects:
                for i in range(4):
                    r = size//3 + i * 3
                    alpha = 180 - i * 40
                    pygame.draw.circle(self.image, (*color, alpha), (center, center), r, 2)
                pygame.draw.circle(self.image, (200, 255, 240), (center, center), size//5)
            
            # 6. 星矢天箭 - 星座连线箭
            elif "constellation_trail" in effects or "meteor_shower" in effects:
                # 箭头
                arrow_pts = [(center, center - size*2//3), (center + size//4, center + size//4), (center - size//4, center + size//4)]
                pygame.draw.polygon(self.image, (*color, 220), arrow_pts)
                # 星座点
                stars = [(center, center - size//2), (center + size//4, center - size//4), (center - size//4, center)]
                for sx, sy in stars:
                    pygame.draw.circle(self.image, (255, 255, 255), (int(sx), int(sy)), 2)
                # 连线
                pygame.draw.lines(self.image, (150, 180, 255, 120), False, stars, 1)
            
            # 7. 曙光破晓 - 金橙光束
            elif "dawn_break" in effects or "hope_light" in effects:
                # 光芒主体
                beam_pts = [(center, center - size*3//4), (center + size//5, center + size//3), (center - size//5, center + size//3)]
                pygame.draw.polygon(self.image, (255, 180, 100, 220), beam_pts)
                # 放射光芒
                for i in range(5):
                    angle = -math.pi/2 + (i - 2) * 0.3
                    rx = center + int(math.cos(angle) * size//2)
                    ry = center - size//4 + int(math.sin(angle) * size//3)
                    pygame.draw.line(self.image, (255, 220, 150, 150), (center, center - size//4), (rx, ry), 2)
            
            # 8. 月华花瓣 - 樱花瓣形
            elif "petal_dance" in effects or "moon_scatter" in effects:
                # 花瓣形状
                petal_pts = [(center, center - size//2), (center + size//3, center), (center, center + size//3), (center - size//3, center)]
                pygame.draw.polygon(self.image, (255, 220, 240, 200), petal_pts)
                pygame.draw.polygon(self.image, (255, 180, 200), petal_pts, 2)
                # 中心
                pygame.draw.circle(self.image, (255, 200, 220), (center, center), size//6)
            
            # 9. 虹怒轰击 - 愤怒爆发球
            elif "fury_explosion" in effects or "instant_kill" in effects:
                # 核心
                pygame.draw.circle(self.image, (255, 80, 120), (center, center), size//2.5)
                pygame.draw.circle(self.image, (255, 200, 50), (center, center), size//4)
                # 爆发尖刺
                for i in range(8):
                    angle = i * math.pi / 4
                    sx = center + int(math.cos(angle) * size//1.8)
                    sy = center + int(math.sin(angle) * size//1.8)
                    pygame.draw.line(self.image, (255, 100, 100), (center, center), (sx, sy), 3)
                pygame.draw.circle(self.image, (255, 255, 200), (center, center), size//6)
            
            # 10. 梦境泡沫 - 淡紫泡泡
            elif "dream_float" in effects or "starlight_burst" in effects:
                # 多层泡泡
                pygame.draw.circle(self.image, (220, 180, 255, 80), (center, center), size//2)
                pygame.draw.circle(self.image, (230, 200, 255, 120), (center, center), size//2.5)
                pygame.draw.circle(self.image, (240, 220, 255, 180), (center, center), size//3.5)
                # 高光
                pygame.draw.circle(self.image, (255, 255, 255, 200), (center - size//6, center - size//6), size//8)
                pygame.draw.circle(self.image, (220, 180, 255), (center, center), size//2, 2)
            
            # 11. 太阳舞步 - 旋转太阳轮
            elif "solar_spin" in effects or "flame_dance" in effects:
                # 太阳核心
                pygame.draw.circle(self.image, (255, 200, 50), (center, center), size//3)
                pygame.draw.circle(self.image, (255, 255, 150), (center, center), size//5)
                # 火焰光芒
                for i in range(8):
                    angle = i * math.pi / 4
                    inner_r = size//3
                    outer_r = size//1.8
                    ix = center + int(math.cos(angle) * inner_r)
                    iy = center + int(math.sin(angle) * inner_r)
                    ox = center + int(math.cos(angle) * outer_r)
                    oy = center + int(math.sin(angle) * outer_r)
                    pygame.draw.line(self.image, (255, 120, 30), (ix, iy), (ox, oy), 3)
                    pygame.draw.line(self.image, (255, 200, 80), (ix, iy), (ox, oy), 1)
            
            # 默认: 月虹光梭 - 菱形
            else:
                # 外层光晕
                for i in range(3):
                    glow_r = size//2 + 3 - i * 2
                    glow_alpha = 60 - i * 15
                    pygame.draw.circle(self.image, (*color, glow_alpha), (center, center), glow_r)
                # 菱形主体
                diamond_h = int(size * 0.7)
                diamond_w = int(size * 0.4)
                diamond_points = [(center, center - diamond_h), (center + diamond_w, center), (center, center + diamond_h), (center - diamond_w, center)]
                pygame.draw.polygon(self.image, (*color, 220), diamond_points)
                inner_scale = 0.6
                inner_pts = [(center + (px - center) * inner_scale, center + (py - center) * inner_scale) for px, py in diamond_points]
                pygame.draw.polygon(self.image, (255, 215, 120), inner_pts)
                pygame.draw.circle(self.image, (255, 215, 120), (center, center - diamond_h), 3)
                pygame.draw.circle(self.image, (255, 255, 255), (center, center - diamond_h), 2)
            
            self.speed = -20
            return
        
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
        
        # ========== Wormhole 混沌虫洞子弹 ==========
        elif "water_vortex" in effects or "spiral_ascend" in effects:
            # 季风暴雨·水龙卷
            self.image = pygame.Surface((size*2, size*3), pygame.SRCALPHA)
            center_x = size
            center_y = size * 3 // 2
            # 水龙卷螺旋体（5层）
            for i in range(5):
                layer_y = center_y + size//2 - i * size//5
                layer_r = size//4 + i * size//10
                # 螺旋波纹
                spiral_points = []
                for j in range(8):
                    angle = (j * 45 + i * 25) * 3.14159 / 180
                    px = center_x + int(layer_r * math.cos(angle))
                    py = layer_y
                    spiral_points.append((px, py))
                if len(spiral_points) > 1:
                    pygame.draw.lines(self.image, (100 + i*10, 180 + i*10, 240 - i*20), False, spiral_points, 3 - i//2)
            # 水滴飞溅粒子（8个）
            import random
            random.seed(789)
            for i in range(8):
                angle = (i * 45 + random.randint(-15, 15)) * 3.14159 / 180
                splash_dist = size//3 + random.randint(0, size//6)
                sx = center_x + int(splash_dist * math.cos(angle))
                sy = center_y + random.randint(-size//4, size//4)
                drop_size = size//15 + random.randint(0, size//20)
                # 水滴形状
                pygame.draw.circle(self.image, (100, 180, 240, 200), (sx, sy), drop_size)
                pygame.draw.circle(self.image, (150, 220, 255), (sx, sy - drop_size//3), drop_size//2)
            # 中心漩涡
            pygame.draw.circle(self.image, (80, 150, 220), (center_x, center_y), size//6)
            pygame.draw.circle(self.image, (100, 200, 255), (center_x, center_y), size//8)
            self.speed = -16
        
        elif "heat_shimmer" in effects or "distortion_wave" in effects:
            # 沙漠幻影·蜃景
            self.image = pygame.Surface((size*3, size*2), pygame.SRCALPHA)
            center_x = size * 3 // 2
            center_y = size
            # 波浪扭曲效果（6层波纹）
            for i in range(6):
                wave_y = center_y + (i - 2.5) * size//6
                wave_points = []
                for x in range(0, size*3, size//10):
                    wave_offset = int(size//8 * math.sin((x + i*size//4) * 0.3))
                    wave_points.append((x, wave_y + wave_offset))
                if len(wave_points) > 1:
                    alpha = 180 - i * 25
                    pygame.draw.lines(self.image, (255, 200 - i*10, 120 + i*5, alpha), False, wave_points, 2)
            # 幻影虚像（半透明重叠圆）
            for i in range(3):
                offset_x = (i - 1) * size//6
                illusion_alpha = 150 - i * 40
                pygame.draw.circle(self.image, (255, 220, 150, illusion_alpha), (center_x + offset_x, center_y), size//4)
                pygame.draw.circle(self.image, (255, 200, 100, illusion_alpha), (center_x + offset_x, center_y), size//5, 2)
            # 热浪粒子（金色闪烁点）
            random.seed(890)
            for i in range(10):
                px = center_x + random.randint(-size, size)
                py = center_y + random.randint(-size//2, size//2)
                pygame.draw.circle(self.image, (255, 230, 150, random.randint(100, 200)), (px, py), size//30)
            self.speed = -15
        
        elif "growing_branches" in effects or "leaf_orbit" in effects:
            # 盆栽之心·微观树
            self.image = pygame.Surface((size*3, size*3), pygame.SRCALPHA)
            center = size * 3 // 2
            # 树根基座
            pygame.draw.rect(self.image, (100, 80, 60), (center - size//4, center + size//3, size//2, size//6))
            # 主树干（蜷曲）
            trunk_points = []
            for i in range(8):
                trunk_y = center + size//3 - i * size//10
                trunk_x = center + int(size//8 * math.sin(i * 0.6))
                trunk_points.append((trunk_x, trunk_y))
            if len(trunk_points) > 1:
                pygame.draw.lines(self.image, (80, 60, 40), False, trunk_points, size//15)
            # 枝干（4条）
            for i in range(4):
                branch_angle = (i * 90 + 45) * 3.14159 / 180
                branch_start_x = center + int(size//12 * math.sin(i * 0.6))
                branch_start_y = center - i * size//12
                branch_points = [(branch_start_x, branch_start_y)]
                for j in range(3):
                    bx = branch_start_x + int((j+1) * size//6 * math.cos(branch_angle + math.sin(j)*0.3))
                    by = branch_start_y - int((j+1) * size//12 * math.sin(branch_angle + math.sin(j)*0.3))
                    branch_points.append((bx, by))
                if len(branch_points) > 1:
                    pygame.draw.lines(self.image, (100, 80, 60), False, branch_points, size//25)
            # 绿叶环绕（12片）
            for i in range(12):
                leaf_angle = (i * 30) * 3.14159 / 180
                leaf_dist = size//4 + size//6 * math.sin(i * 0.5)
                lx = center + int(leaf_dist * math.cos(leaf_angle))
                ly = center + int(leaf_dist * math.sin(leaf_angle))
                # 叶片（椭圆）
                leaf_surf = pygame.Surface((size//8, size//6), pygame.SRCALPHA)
                pygame.draw.ellipse(leaf_surf, (60 + i*5, 120 + i*3, 80), (0, 0, size//8, size//6))
                pygame.draw.ellipse(leaf_surf, (40 + i*3, 100 + i*2, 60), (0, 0, size//8, size//6), 1)
                self.image.blit(leaf_surf, (lx - size//16, ly - size//12))
            # 禅意光环
            pygame.draw.circle(self.image, (60, 120, 80, 80), (center, center), size//2, 3)
            self.speed = -14
        
        elif "warm_glow" in effects or "candle_flicker" in effects:
            # 纸灯笼·温光
            self.image = pygame.Surface((size*3, size*3), pygame.SRCALPHA)
            center = size * 3 // 2
            # 六边形灯笼外框
            hex_points = []
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                hx = center + int(size//2 * math.cos(angle))
                hy = center + int(size//2 * math.sin(angle))
                hex_points.append((hx, hy))
            # 灯笼外壳（纸质纹理）
            pygame.draw.polygon(self.image, (255, 220, 150, 220), hex_points)
            pygame.draw.polygon(self.image, (255, 200, 100), hex_points, 3)
            # 纸质纹理线条
            for i in range(6):
                pygame.draw.line(self.image, (240, 200, 130, 150), (center, center), hex_points[i], 2)
            # 温暖光晕（3层）
            for i in range(3):
                glow_r = size//4 + i * size//6
                glow_alpha = 120 - i * 30
                temp_surf = pygame.Surface((size*3, size*3), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (255, 220, 100, glow_alpha), (center, center), glow_r)
                self.image.blit(temp_surf, (0, 0))
            # 烛火核心（摇曳效果通过多层实现）
            flame_size = size//6
            for i in range(3):
                flame_y_offset = int(size//20 * math.sin(i * 1.5))
                flame_color = [(255, 200, 80), (255, 150, 50), (255, 100, 0)][i]
                pygame.draw.ellipse(self.image, flame_color, 
                                  (center - flame_size//2, center - flame_size + flame_y_offset, 
                                   flame_size, flame_size*2))
            # 明亮中心点
            pygame.draw.circle(self.image, (255, 255, 200), (center, center), size//15)
            self.speed = -13
        
        elif "faceted_crystal" in effects or "inner_glow_pulse" in effects:
            # 晶洞爆裂·紫晶
            self.image = pygame.Surface((size*3, size*3), pygame.SRCALPHA)
            center = size * 3 // 2
            # 多面晶体结构（12面）
            crystal_points = []
            for i in range(12):
                angle = (i * 30) * 3.14159 / 180
                # 交替半径创造尖锐棱角
                radius = size//2 if i % 2 == 0 else size//3
                cx = center + int(radius * math.cos(angle))
                cy = center + int(radius * math.sin(angle))
                crystal_points.append((cx, cy))
            # 晶体外壳
            pygame.draw.polygon(self.image, (180, 100, 240, 220), crystal_points)
            pygame.draw.polygon(self.image, (160, 80, 220), crystal_points, 3)
            # 内部晶面（6个三角形）
            for i in range(0, 12, 2):
                triangle = [(center, center), crystal_points[i], crystal_points[(i+2) % 12]]
                inner_color = (140 + i*5, 60 + i*3, 200 + i*3, 150)
                pygame.draw.polygon(self.image, inner_color, triangle)
            # 内部紫光脉动（3层渐变圆）
            for i in range(3):
                pulse_r = size//8 + i * size//12
                pulse_alpha = 200 - i * 50
                pygame.draw.circle(self.image, (180, 100, 240, pulse_alpha), (center, center), pulse_r)
            # 裂纹闪光（8条）
            for i in range(8):
                crack_angle = (i * 45) * 3.14159 / 180
                crack_start = size//4
                crack_end = size//2
                for j in range(2, 5):
                    crack_r = crack_start + j * (crack_end - crack_start) // 5
                    crack_x = center + int(crack_r * math.cos(crack_angle))
                    crack_y = center + int(crack_r * math.sin(crack_angle))
                    crack_brightness = 255 - j * 30
                    pygame.draw.circle(self.image, (crack_brightness, crack_brightness//2, 255), (crack_x, crack_y), size//40)
            # 外部光芒（6道）
            for i in range(6):
                ray_angle = (i * 60) * 3.14159 / 180
                ray_end_x = center + int(size * math.cos(ray_angle))
                ray_end_y = center + int(size * math.sin(ray_angle))
                pygame.draw.line(self.image, (200, 120, 255, 150), (center, center), (ray_end_x, ray_end_y), 2)
            self.speed = -15
        
        elif "carved_runes" in effects or "tribal_aura" in effects:
            # 图腾柱·古灵
            self.image = pygame.Surface((size*2, size*4), pygame.SRCALPHA)
            center_x = size
            # 图腾柱主体（竖直矩形，3段）
            for i in range(3):
                segment_y = size//2 + i * size
                segment_h = size - size//10
                # 图腾段
                pygame.draw.rect(self.image, (180 - i*15, 120 - i*10, 60 - i*5), 
                               (center_x - size//4, segment_y, size//2, segment_h))
                pygame.draw.rect(self.image, (200 - i*15, 150 - i*10, 100 - i*10), 
                               (center_x - size//4, segment_y, size//2, segment_h), 3)
                # 雕刻纹路（横纹）
                for j in range(4):
                    carve_y = segment_y + j * segment_h // 4
                    pygame.draw.line(self.image, (120 - i*10, 80 - i*5, 40), 
                                   (center_x - size//5, carve_y), (center_x + size//5, carve_y), 2)
                # 图腾面孔（简化眼睛）
                eye_y = segment_y + segment_h // 2
                pygame.draw.circle(self.image, (255, 220, 150), (center_x - size//8, eye_y), size//15)
                pygame.draw.circle(self.image, (255, 220, 150), (center_x + size//8, eye_y), size//15)
                pygame.draw.circle(self.image, (100, 60, 20), (center_x - size//8, eye_y), size//25)
                pygame.draw.circle(self.image, (100, 60, 20), (center_x + size//8, eye_y), size//25)
            # 部落符文发光（8个环绕符号）
            for i in range(8):
                rune_angle = (i * 45) * 3.14159 / 180
                rune_dist = size//3
                rune_y = size * 2 + int(rune_dist * math.sin(rune_angle))
                rune_x = center_x + int(rune_dist * math.cos(rune_angle))
                # 符文（简化为星形光点）
                pygame.draw.circle(self.image, (255, 220, 100), (rune_x, rune_y), size//20)
                pygame.draw.circle(self.image, (255, 255, 150), (rune_x, rune_y), size//30)
            # 古老能量环绕（3个圆环）
            for i in range(3):
                aura_y = size + i * size
                aura_r = size//3 + i * size//12
                pygame.draw.circle(self.image, (200, 150, 100, 100 - i*20), (center_x, aura_y), aura_r, 2)
            self.speed = -14
        
        elif "ancient_text" in effects or "time_echo" in effects:
            # 遗迹石碑·古文
            self.image = pygame.Surface((size*2, size*3), pygame.SRCALPHA)
            center_x = size
            center_y = size * 3 // 2
            # 破碎石板形状（不规则多边形）
            tablet_points = [
                (center_x - size//3, center_y - size//2),
                (center_x + size//3, center_y - size//2 + size//10),
                (center_x + size//2, center_y),
                (center_x + size//3, center_y + size//2),
                (center_x - size//4, center_y + size//2 - size//10),
                (center_x - size//2, center_y - size//10)
            ]
            # 石板主体
            pygame.draw.polygon(self.image, (100, 110, 140), tablet_points)
            pygame.draw.polygon(self.image, (130, 140, 170), tablet_points, 3)
            # 古老文字符号（8个）
            text_symbols = [
                [(0, -1), (0, 1)],  # 竖线
                [(-1, -1), (1, 1)],  # 斜线
                [(0, 0)],  # 点
                [(-1, 0), (0, -1), (1, 0), (0, 1)],  # 十字
            ]
            for i in range(8):
                text_x = center_x + (i % 3 - 1) * size//6
                text_y = center_y + (i // 3 - 1) * size//5
                symbol = text_symbols[i % len(text_symbols)]
                for dx, dy in symbol:
                    sx = text_x + dx * size//30
                    sy = text_y + dy * size//30
                    if len(symbol) == 1:
                        pygame.draw.circle(self.image, (200, 180, 150), (sx, sy), size//40)
                    else:
                        pygame.draw.line(self.image, (200, 180, 150), (text_x, text_y), (sx, sy), 2)
            # 历史光影回响（波纹）
            for i in range(3):
                echo_r = size//4 + i * size//8
                echo_alpha = 120 - i * 30
                pygame.draw.ellipse(self.image, (150, 160, 190, echo_alpha), 
                                  (center_x - echo_r, center_y - echo_r//2, echo_r*2, echo_r), 2)
            # 岁月裂痕发光（5条）
            for i in range(5):
                crack_start_x = center_x + random.randint(-size//4, size//4)
                crack_start_y = center_y + random.randint(-size//3, size//3)
                crack_angle = random.uniform(0, 6.28)
                crack_len = size//6
                crack_end_x = crack_start_x + int(crack_len * math.cos(crack_angle))
                crack_end_y = crack_start_y + int(crack_len * math.sin(crack_angle))
                pygame.draw.line(self.image, (180, 200, 230), (crack_start_x, crack_start_y), 
                               (crack_end_x, crack_end_y), 2)
                # 裂痕发光点
                for j in range(3):
                    glow_x = crack_start_x + int(j * crack_len//3 * math.cos(crack_angle))
                    glow_y = crack_start_y + int(j * crack_len//3 * math.sin(crack_angle))
                    pygame.draw.circle(self.image, (200, 220, 255), (glow_x, glow_y), size//50)
            self.speed = -15
        
        # ========== Chronos 子弹 ==========
        elif "time_ripple" in effects or "chrono_freeze" in effects:
            # 时钟表盘子弹
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 时钟圆盘
            pygame.draw.circle(self.image, (200, 200, 230), (center, center), size//2)
            pygame.draw.circle(self.image, color, (center, center), size//2, 3)
            # 时钟刻度（12个）
            for i in range(12):
                angle = (i * 30 - 90) * 3.14159 / 180
                x1 = center + int(size//2.5 * math.cos(angle))
                y1 = center + int(size//2.5 * math.sin(angle))
                x2 = center + int(size//2 * math.cos(angle))
                y2 = center + int(size//2 * math.sin(angle))
                width = 3 if i % 3 == 0 else 2
                pygame.draw.line(self.image, (100, 100, 160), (x1, y1), (x2, y2), width)
            # 时针（向上指）
            time_angle = -90 * 3.14159 / 180
            needle_x = center + int(size//3 * math.cos(time_angle))
            needle_y = center + int(size//3 * math.sin(time_angle))
            pygame.draw.line(self.image, (60, 60, 120), (center, center), (needle_x, needle_y), 4)
            # 时间波纹（3层）
            for i in range(3):
                ripple_r = size//2 + size//8 + i * size//6
                pygame.draw.circle(self.image, (*color, 150 - i * 40), (center, center), ripple_r, 2)
            # 冻结标记（蓝色冰晶）
            if "chrono_freeze" in effects:
                for i in range(4):
                    angle = (i * 90 + 45) * 3.14159 / 180
                    fx = center + int(size//1.8 * math.cos(angle))
                    fy = center + int(size//1.8 * math.sin(angle))
                    ice_points = [
                        (fx, fy - size//12),
                        (fx + size//15, fy),
                        (fx, fy + size//12),
                        (fx - size//15, fy)
                    ]
                    pygame.draw.polygon(self.image, (150, 200, 255), ice_points)
            self.speed = -14
            
        elif "reverse_trail" in effects or "time_rewind" in effects:
            # 逆转螺旋子弹
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 逆时针螺旋（2条臂）
            for arm in range(2):
                spiral_points = []
                arm_offset = arm * 180
                for i in range(12):
                    # 逆时针角度（负值）
                    angle = -(i * 30 + arm_offset) * 3.14159 / 180
                    radius = size//6 + i * size//30
                    sx = center + int(radius * math.cos(angle))
                    sy = center + int(radius * math.sin(angle))
                    spiral_points.append((sx, sy))
                if len(spiral_points) > 1:
                    pygame.draw.lines(self.image, (180, 150, 255), False, spiral_points, 4)
                    pygame.draw.lines(self.image, color, False, spiral_points, 2)
            # 中心倒转标记
            pygame.draw.circle(self.image, (200, 170, 255), (center, center), size//5)
            pygame.draw.circle(self.image, color, (center, center), size//6)
            # 倒转箭头（⏪）
            arrow_left = [
                (center - size//8, center),
                (center - size//4, center - size//10),
                (center - size//4, center + size//10)
            ]
            arrow_right = [
                (center + size//12, center),
                (center - size//12, center - size//10),
                (center - size//12, center + size//10)
            ]
            pygame.draw.polygon(self.image, (100, 70, 150), arrow_left)
            pygame.draw.polygon(self.image, (100, 70, 150), arrow_right)
            self.speed = -15
            
        elif "season_cycle" in effects or "day_night_shift" in effects:
            # 纪元日历子弹
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 日历页面
            page_rect = (center - size//1.5, center - size//1.3, size*4//3, size*5//3)
            pygame.draw.rect(self.image, (240, 240, 250), page_rect, border_radius=int(size//10))
            pygame.draw.rect(self.image, color, page_rect, 3, border_radius=int(size//10))
            # 四季色块（4象限）
            season_colors = [(120, 220, 120), (255, 200, 80), (200, 120, 80), (220, 220, 255)]
            for i, season_color in enumerate(season_colors):
                angle = (i * 90) * 3.14159 / 180
                quarter_x = center + int(size//4 * math.cos(angle + 0.785))
                quarter_y = center + int(size//4 * math.sin(angle + 0.785))
                pygame.draw.circle(self.image, season_color, (quarter_x, quarter_y), size//8)
            # 昼夜标记（太阳月亮）
            if "day_night_shift" in effects:
                # 太阳（左上）
                sun_x, sun_y = center - size//3, center - size//3
                pygame.draw.circle(self.image, (255, 255, 100), (sun_x, sun_y), size//12)
                for j in range(8):
                    ray_angle = (j * 45) * 3.14159 / 180
                    ray_x = sun_x + int(size//7 * math.cos(ray_angle))
                    ray_y = sun_y + int(size//7 * math.sin(ray_angle))
                    pygame.draw.line(self.image, (255, 255, 100), (sun_x, sun_y), (ray_x, ray_y), 2)
                # 月亮（右下）
                moon_x, moon_y = center + size//3, center + size//3
                pygame.draw.circle(self.image, (200, 200, 240), (moon_x, moon_y), size//12)
                pygame.draw.circle(self.image, (180, 180, 220), (moon_x - size//20, moon_y), size//14)
            self.speed = -13
            
        elif "sand_flow" in effects or "hourglass_flip" in effects:
            # 沙漏子弹
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 沙漏外框
            hourglass_top = [
                (center - size//2, center - size),
                (center + size//2, center - size),
                (center + size//8, center)
            ]
            hourglass_bottom = [
                (center - size//8, center),
                (center - size//2, center + size),
                (center + size//2, center + size)
            ]
            pygame.draw.polygon(self.image, (200, 180, 140), hourglass_top)
            pygame.draw.polygon(self.image, (200, 180, 140), hourglass_bottom)
            pygame.draw.polygon(self.image, color, hourglass_top, 3)
            pygame.draw.polygon(self.image, color, hourglass_bottom, 3)
            # 中心收缩点
            pygame.draw.circle(self.image, (160, 140, 100), (center, center), size//12)
            # 流动的沙子（上半部少，下半部多）
            import random
            random.seed(789)
            # 上半部分沙粒（较少）
            for _ in range(8):
                sx = center + random.randint(-size//3, size//3)
                sy = center - size + random.randint(size//6, size//2)
                pygame.draw.circle(self.image, (220, 200, 120), (sx, sy), size//40)
            # 下半部分沙粒（较多）
            for _ in range(20):
                sx = center + random.randint(-size//3, size//3)
                sy = center + random.randint(size//6, size)
                pygame.draw.circle(self.image, (220, 200, 120), (sx, sy), size//40)
            # 翻转标记（双向箭头）
            if "hourglass_flip" in effects:
                pygame.draw.line(self.image, (180, 160, 120), (center - size//6, center - size//8), 
                               (center + size//6, center - size//8), 3)
                pygame.draw.line(self.image, (180, 160, 120), (center - size//6, center + size//8), 
                               (center + size//6, center + size//8), 3)
                # 箭头
                pygame.draw.polygon(self.image, (180, 160, 120), [
                    (center + size//6, center - size//8), 
                    (center + size//8, center - size//5), 
                    (center + size//8, center - size//20)
                ])
                pygame.draw.polygon(self.image, (180, 160, 120), [
                    (center - size//6, center + size//8), 
                    (center - size//8, center + size//20), 
                    (center - size//8, center + size//5)
                ])
            self.speed = -14
            
        elif "space_crack" in effects or "causality_break" in effects:
            # 悖论漩涡子弹
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 无限符号基础（∞）
            left_loop_center = (center - size//3, center)
            right_loop_center = (center + size//3, center)
            # 左环
            pygame.draw.circle(self.image, (*color, 200), left_loop_center, size//3, 4)
            # 右环
            pygame.draw.circle(self.image, (*color, 200), right_loop_center, size//3, 4)
            # 中心连接点
            pygame.draw.circle(self.image, color, (center, center), size//6)
            # 时空裂痕（放射状）
            if "space_crack" in effects:
                import random
                random.seed(456)
                for _ in range(12):
                    crack_angle = random.uniform(0, 6.28)
                    crack_start = size//2
                    crack_end = size//2 + size//3
                    x1 = center + int(crack_start * math.cos(crack_angle))
                    y1 = center + int(crack_start * math.sin(crack_angle))
                    x2 = center + int(crack_end * math.cos(crack_angle))
                    y2 = center + int(crack_end * math.sin(crack_angle))
                    pygame.draw.line(self.image, (200, 150, 255, 180), (x1, y1), (x2, y2), 2)
            # 因果破碎效果（闪电状）
            if "causality_break" in effects:
                for i in range(6):
                    angle = (i * 60) * 3.14159 / 180
                    bolt_points = [(center, center)]
                    for j in range(4):
                        import random
                        random.seed(100 + i * 10 + j)
                        radius = (j + 1) * size//8
                        offset = random.randint(-size//12, size//12)
                        bx = center + int(radius * math.cos(angle)) + offset
                        by = center + int(radius * math.sin(angle)) + offset
                        bolt_points.append((bx, by))
                    if len(bolt_points) > 1:
                        pygame.draw.lines(self.image, (255, 200, 255), False, bolt_points, 2)
            self.speed = -16
            
        elif "echo_trail" in effects or "resonance" in effects:
            # 回声波纹子弹
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 主波形核心
            pygame.draw.circle(self.image, (180, 200, 255), (center, center), size//4)
            pygame.draw.circle(self.image, color, (center, center), size//5)
            # 波纹（5层）
            for i in range(5):
                wave_r = size//3 + i * size//8
                alpha = 220 - i * 40
                # 波纹用虚线效果
                for angle_deg in range(0, 360, 20):
                    angle = angle_deg * 3.14159 / 180
                    x1 = center + int(wave_r * math.cos(angle))
                    y1 = center + int(wave_r * math.sin(angle))
                    x2 = center + int((wave_r + size//20) * math.cos(angle))
                    y2 = center + int((wave_r + size//20) * math.sin(angle))
                    pygame.draw.line(self.image, (*color, alpha), (x1, y1), (x2, y2), 2)
            # 共振标记（音叉）
            if "resonance" in effects:
                fork_y = center - size//2
                # 音叉柄
                pygame.draw.rect(self.image, (160, 180, 220), (center - size//30, fork_y, size//15, size//3))
                # 音叉两臂
                left_arm = [
                    (center - size//8, fork_y - size//6),
                    (center - size//8, fork_y),
                    (center - size//20, fork_y)
                ]
                right_arm = [
                    (center + size//8, fork_y - size//6),
                    (center + size//8, fork_y),
                    (center + size//20, fork_y)
                ]
                pygame.draw.lines(self.image, (160, 180, 220), False, left_arm, 3)
                pygame.draw.lines(self.image, (160, 180, 220), False, right_arm, 3)
                # 振动波纹（3层）
                for j in range(3):
                    vib_r = size//10 + j * size//15
                    pygame.draw.circle(self.image, (180, 200, 240, 180 - j * 50), 
                                     (center, fork_y - size//6), vib_r, 2)
            self.speed = -14
            
        elif "infinite_loop" in effects or "holy_glow" in effects:
            # 永恒莫比乌斯子弹
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 莫比乌斯环（8字形扭曲）
            # 绘制两个相交的圆形路径
            for loop in range(2):
                loop_center_x = center + (size//3 if loop == 0 else -size//3)
                loop_center_y = center
                # 主环
                pygame.draw.circle(self.image, (*color, 220), (loop_center_x, loop_center_y), size//2.5, 5)
                # 内环（制造扭曲感）
                pygame.draw.circle(self.image, (240, 240, 255, 150), (loop_center_x, loop_center_y), size//4, 3)
            # 中心交点强调
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//8)
            pygame.draw.circle(self.image, color, (center, center), size//10)
            # 环上的运动点（6个）
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                # 点在左右环上交替
                loop_x = center + (size//3 if i % 2 == 0 else -size//3)
                px = loop_x + int(size//2.5 * math.cos(angle))
                py = center + int(size//2.5 * math.sin(angle))
                pygame.draw.circle(self.image, (200, 200, 255), (px, py), size//20)
            # 神圣光辉（外发光）
            if "holy_glow" in effects:
                for i in range(4):
                    glow_r = size + i * size//6
                    alpha = 120 - i * 30
                    pygame.draw.circle(self.image, (255, 255, 255, alpha), (center, center), glow_r, 3)
            self.speed = -17
        
        # ========== Puppeteer (牵线木偶师) 子弹涂装 ==========
        elif "soul_string" in effects or "silk_manipulation" in effects:
            # 灵魂丝线弹 - 缠绕的提线，发光丝线
            self.image = pygame.Surface((size*2, size*3), pygame.SRCALPHA)
            center_x, center_y = size, size * 3 // 2
            # 多条交织丝线
            for strand in range(5):
                strand_offset = (strand - 2) * size//8
                strand_points = []
                for i in range(10):
                    wave = math.sin(i * 0.8 + strand * 0.5) * size//6
                    px = center_x + strand_offset + wave
                    py = center_y - size + i * size//5
                    strand_points.append((int(px), int(py)))
                if len(strand_points) > 1:
                    # 发光丝线
                    pygame.draw.lines(self.image, (200, 150, 220, 180), False, strand_points, 3)
                    pygame.draw.lines(self.image, color, False, strand_points, 1)
            # 丝线末端的钩子
            for hook_x in [center_x - size//4, center_x, center_x + size//4]:
                hook_points = [(hook_x, center_y + size//2), (hook_x - size//12, center_y + size//2 + size//8), 
                              (hook_x + size//12, center_y + size//2 + size//8)]
                pygame.draw.lines(self.image, (180, 130, 200), False, hook_points, 2)
            # 顶部控制结
            pygame.draw.circle(self.image, (220, 180, 240), (center_x, center_y - size), size//6)
            self.speed = -14
            
        elif "pierce_soul" in effects or "voodoo_curse" in effects:
            # 巫毒针弹 - 长针+诅咒符文
            self.image = pygame.Surface((size*2, size*3), pygame.SRCALPHA)
            center_x, center_y = size, size * 3 // 2
            # 长针主体
            needle_points = [(center_x, center_y - size), (center_x + size//10, center_y + size//2), 
                            (center_x - size//10, center_y + size//2)]
            pygame.draw.polygon(self.image, (60, 60, 70), needle_points)
            pygame.draw.polygon(self.image, color, needle_points, 2)
            # 针头发光
            pygame.draw.circle(self.image, (255, 100, 100), (center_x, center_y - size), size//8)
            # 缠绕的红线
            for i in range(6):
                wrap_y = center_y - size//2 + i * size//6
                wrap_width = size//4 - abs(i - 3) * size//15
                pygame.draw.arc(self.image, (200, 50, 50), (center_x - wrap_width, wrap_y - size//15, wrap_width*2, size//8), 0, 3.14, 2)
            # 诅咒符文（小型）
            rune_y = center_y + size//4
            pygame.draw.circle(self.image, (150, 50, 80, 150), (center_x, rune_y), size//6, 2)
            self.speed = -15
            
        elif "puppet_swarm" in effects or "string_burst" in effects:
            # 迷你木偶弹 - 小傀儡形态
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 木偶头部（圆形）
            pygame.draw.circle(self.image, (240, 220, 200), (center, center - size//4), size//3)
            pygame.draw.circle(self.image, color, (center, center - size//4), size//3, 2)
            # X眼睛
            eye_size = size//10
            for ex in [center - size//6, center + size//6]:
                ey = center - size//4
                pygame.draw.line(self.image, (60, 60, 60), (ex - eye_size, ey - eye_size), (ex + eye_size, ey + eye_size), 2)
                pygame.draw.line(self.image, (60, 60, 60), (ex - eye_size, ey + eye_size), (ex + eye_size, ey - eye_size), 2)
            # 木偶身体
            body_rect = (center - size//4, center, size//2, size//2)
            pygame.draw.rect(self.image, (220, 200, 180), body_rect)
            pygame.draw.rect(self.image, color, body_rect, 2)
            # 悬挂的丝线
            for string_x in [center - size//6, center, center + size//6]:
                pygame.draw.line(self.image, (200, 180, 220), (string_x, center - size//2 - size//4), (string_x, center - size//3), 1)
            self.speed = -13
            
        elif "control_link" in effects or "master_will" in effects:
            # 十字控制弹 - 木制十字架控制器
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 十字架主体
            cross_color = (180, 150, 80)
            # 垂直部分
            pygame.draw.rect(self.image, cross_color, (center - size//10, center - size//2, size//5, size))
            # 水平部分
            pygame.draw.rect(self.image, cross_color, (center - size//2.5, center - size//4, size*4//5, size//5))
            # 木纹
            pygame.draw.line(self.image, (160, 130, 60), (center, center - size//2), (center, center + size//2), 1)
            pygame.draw.line(self.image, (160, 130, 60), (center - size//2.5, center - size//8), (center + size//2.5, center - size//8), 1)
            # 金色边框
            pygame.draw.rect(self.image, color, (center - size//10, center - size//2, size//5, size), 2)
            pygame.draw.rect(self.image, color, (center - size//2.5, center - size//4, size*4//5, size//5), 2)
            # 悬挂的丝线（4条）
            for i, offset in enumerate([(-size//3, size//4), (size//3, size//4), (-size//6, size//3), (size//6, size//3)]):
                start_x = center + offset[0]
                pygame.draw.line(self.image, (220, 200, 180), (start_x, center + size//10), (start_x, center + offset[1] + size//4), 1)
            self.speed = -14
            
        elif "soul_wail" in effects or "ghost_bind" in effects:
            # 灵魂碎片弹 - 半透明灵魂
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 灵魂主体（半透明）
            ghost_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            # 飘动的灵魂形状
            ghost_points = [(center, center - size//2)]
            for i in range(8):
                angle = -0.5 + i * 0.25
                radius = size//3 + (i % 2) * size//10
                gx = center + int(radius * math.sin(angle))
                gy = center - size//4 + i * size//8
                ghost_points.append((gx, gy))
            ghost_points.append((center, center + size//2))
            pygame.draw.polygon(ghost_surf, (150, 200, 255, 150), ghost_points)
            pygame.draw.polygon(ghost_surf, color, ghost_points, 2)
            self.image.blit(ghost_surf, (0, 0))
            # 空洞的眼睛
            for ex in [center - size//6, center + size//6]:
                pygame.draw.circle(self.image, (50, 100, 150), (ex, center - size//4), size//10)
            # 张开的嘴（哀嚎）
            pygame.draw.ellipse(self.image, (30, 80, 130), (center - size//8, center, size//4, size//6))
            self.speed = -15
            
        elif "web_spread" in effects or "sticky_trap" in effects:
            # 蛛网陷阱弹 - 球形蛛网
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 蛛网同心圆（3层）
            for ring in range(3):
                ring_r = size//4 + ring * size//6
                pygame.draw.circle(self.image, (220, 220, 230, 200 - ring * 50), (center, center), ring_r, 2)
            # 蛛网辐射线（8条）
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                end_x = center + int(size//2 * math.cos(angle))
                end_y = center + int(size//2 * math.sin(angle))
                pygame.draw.line(self.image, color, (center, center), (end_x, end_y), 2)
            # 中心粘液点
            pygame.draw.circle(self.image, (200, 200, 220), (center, center), size//8)
            # 粘性液滴（随机位置）
            import random
            random.seed(123)
            for _ in range(6):
                drop_angle = random.random() * 6.28
                drop_r = size//4 + random.randint(0, size//4)
                dx = center + int(drop_r * math.cos(drop_angle))
                dy = center + int(drop_r * math.sin(drop_angle))
                pygame.draw.circle(self.image, (230, 230, 240, 180), (dx, dy), size//15)
            self.speed = -12
            
        elif "fate_cut" in effects or "life_sever" in effects:
            # 命运剪刀弹 - 剪刀形态
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 剪刀左刃
            left_blade = [(center - size//8, center - size//2), (center - size//3, center + size//4), 
                         (center - size//6, center + size//4), (center, center - size//4)]
            pygame.draw.polygon(self.image, (100, 100, 120), left_blade)
            pygame.draw.polygon(self.image, color, left_blade, 2)
            # 剪刀右刃
            right_blade = [(center + size//8, center - size//2), (center + size//3, center + size//4), 
                          (center + size//6, center + size//4), (center, center - size//4)]
            pygame.draw.polygon(self.image, (100, 100, 120), right_blade)
            pygame.draw.polygon(self.image, color, right_blade, 2)
            # 铆钉
            pygame.draw.circle(self.image, (60, 60, 70), (center, center - size//4), size//10)
            pygame.draw.circle(self.image, (150, 150, 160), (center, center - size//4), size//15)
            # 刃口发光
            pygame.draw.line(self.image, (200, 200, 220), (center - size//8, center - size//2), (center - size//3, center + size//4), 1)
            pygame.draw.line(self.image, (200, 200, 220), (center + size//8, center - size//2), (center + size//3, center + size//4), 1)
            self.speed = -16
        
        # ========== Pandemic (末日瘟神) 子弹涂装 ==========
        elif "spike_attach" in effects or "infect_spread" in effects:
            # 刺突病毒弹 - 冠状病毒形态
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 病毒球体
            pygame.draw.circle(self.image, (80, 200, 80), (center, center), size//3)
            pygame.draw.circle(self.image, color, (center, center), size//3, 2)
            # 刺突蛋白（12个）
            for i in range(12):
                angle = (i * 30) * 3.14159 / 180
                spike_base_r = size//3
                spike_end_r = size//2
                base_x = center + int(spike_base_r * math.cos(angle))
                base_y = center + int(spike_base_r * math.sin(angle))
                end_x = center + int(spike_end_r * math.cos(angle))
                end_y = center + int(spike_end_r * math.sin(angle))
                # 刺突杆
                pygame.draw.line(self.image, (100, 220, 100), (base_x, base_y), (end_x, end_y), 2)
                # 刺突头（球形）
                pygame.draw.circle(self.image, (120, 255, 120), (end_x, end_y), size//12)
            # 中心RNA标记
            pygame.draw.circle(self.image, (50, 150, 50), (center, center), size//6)
            self.speed = -14
            
        elif "nerve_poison" in effects or "paralyze" in effects:
            # 神经毒素弹 - 紫色毒液滴
            self.image = pygame.Surface((size*2, size*3), pygame.SRCALPHA)
            center_x, center_y = size, size * 3 // 2
            # 毒液滴形状
            drop_points = [(center_x, center_y - size)]  # 顶部尖端
            # 曲线边缘
            for i in range(10):
                t = i / 9
                # 贝塞尔曲线近似
                bulge = math.sin(t * 3.14159) * size//2
                dx = center_x + bulge if i < 5 else center_x - bulge + size
                dy = center_y - size + t * size * 1.5
                drop_points.append((int(dx), int(dy)))
            pygame.draw.polygon(self.image, (180, 80, 200), drop_points)
            pygame.draw.polygon(self.image, color, drop_points, 2)
            # 毒性气泡
            for bubble in [(center_x - size//6, center_y - size//4), (center_x + size//8, center_y), (center_x - size//10, center_y + size//4)]:
                pygame.draw.circle(self.image, (200, 100, 220, 150), bubble, size//10)
            # 骷髅标记
            skull_y = center_y - size//3
            pygame.draw.circle(self.image, (220, 180, 230), (center_x, skull_y), size//8)
            pygame.draw.circle(self.image, (100, 50, 120), (center_x - size//15, skull_y - size//20), size//25)
            pygame.draw.circle(self.image, (100, 50, 120), (center_x + size//15, skull_y - size//20), size//25)
            self.speed = -14
            
        elif "fungal_growth" in effects or "parasitic_burst" in effects:
            # 真菌孢子弹 - 蘑菇孢子云
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 孢子云主体
            for cloud in range(8):
                cloud_angle = (cloud * 45) * 3.14159 / 180
                cloud_r = size//4 + (cloud % 3) * size//10
                cx = center + int(cloud_r * math.cos(cloud_angle) * 0.5)
                cy = center + int(cloud_r * math.sin(cloud_angle) * 0.5)
                cloud_size = size//6 + (cloud % 2) * size//12
                pygame.draw.circle(self.image, (150, 100, 80, 180), (cx, cy), cloud_size)
            # 中心蘑菇
            # 菌柄
            pygame.draw.rect(self.image, (180, 150, 120), (center - size//12, center, size//6, size//3))
            # 菌盖
            pygame.draw.ellipse(self.image, (130, 80, 60), (center - size//4, center - size//6, size//2, size//3))
            pygame.draw.ellipse(self.image, color, (center - size//4, center - size//6, size//2, size//3), 2)
            # 斑点
            for spot in [(center - size//8, center - size//12), (center + size//10, center)]:
                pygame.draw.circle(self.image, (200, 150, 100), spot, size//15)
            self.speed = -13
            
        elif "hazard_mark" in effects or "quarantine_zone" in effects:
            # 生化标志弹 - 旋转生化符号
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 背景警示圆
            pygame.draw.circle(self.image, (255, 200, 0), (center, center), size//2)
            pygame.draw.circle(self.image, (40, 40, 40), (center, center), size//2, 3)
            # 生化危害符号
            pygame.draw.circle(self.image, (40, 40, 40), (center, center), size//8)
            # 三片扇叶
            for blade in range(3):
                blade_angle = (blade * 120 - 90) * 3.14159 / 180
                # 扇形
                arc_points = [(center, center)]
                for arc in range(8):
                    arc_a = blade_angle - 0.4 + arc * 0.1
                    arc_r = size//3
                    ax = center + int(arc_r * math.cos(arc_a))
                    ay = center + int(arc_r * math.sin(arc_a))
                    arc_points.append((ax, ay))
                pygame.draw.polygon(self.image, color, arc_points)
                # 内切口
                cut_points = [(center, center)]
                for cut in range(5):
                    cut_a = blade_angle - 0.2 + cut * 0.08
                    cut_r = size//5
                    cutx = center + int(cut_r * math.cos(cut_a))
                    cuty = center + int(cut_r * math.sin(cut_a))
                    cut_points.append((cutx, cuty))
                pygame.draw.polygon(self.image, (255, 200, 0), cut_points)
            self.speed = -14
            
        elif "cell_corrupt" in effects or "blood_infect" in effects:
            # 感染细胞弹 - 变异红细胞
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 红细胞形状（双凹圆盘）
            pygame.draw.ellipse(self.image, (200, 80, 80), (center - size//2, center - size//3, size, size*2//3))
            # 中心凹陷
            pygame.draw.ellipse(self.image, (150, 50, 50), (center - size//4, center - size//6, size//2, size//3))
            pygame.draw.ellipse(self.image, color, (center - size//2, center - size//3, size, size*2//3), 2)
            # 感染斑点（绿色病变）
            infection_spots = [(center - size//4, center - size//8), (center + size//6, center), 
                              (center - size//8, center + size//8), (center + size//4, center - size//6)]
            for spot in infection_spots:
                pygame.draw.circle(self.image, (100, 180, 80), spot, size//12)
            # 变异触须
            for tendril in range(4):
                angle = (tendril * 90 + 45) * 3.14159 / 180
                start_x = center + int(size//3 * math.cos(angle))
                start_y = center + int(size//5 * math.sin(angle))
                end_x = center + int(size//2 * math.cos(angle))
                end_y = center + int(size//3 * math.sin(angle))
                pygame.draw.line(self.image, (80, 150, 60), (start_x, start_y), (end_x, end_y), 2)
            self.speed = -14
            
        elif "gene_mutate" in effects or "evolve_adapt" in effects:
            # 变异株弹 - DNA双螺旋
            self.image = pygame.Surface((size*2, size*3), pygame.SRCALPHA)
            center_x, center_y = size, size * 3 // 2
            # DNA双螺旋
            helix_colors = [(200, 100, 255), (100, 200, 255)]
            for strand in range(2):
                strand_offset = 3.14159 if strand == 1 else 0
                strand_points = []
                for i in range(15):
                    t = i / 14
                    wave_x = math.sin(t * 6.28 + strand_offset) * size//3
                    py = center_y - size + t * size * 1.5
                    strand_points.append((int(center_x + wave_x), int(py)))
                if len(strand_points) > 1:
                    pygame.draw.lines(self.image, helix_colors[strand], False, strand_points, 3)
            # 碱基对连接
            for i in range(0, 15, 2):
                t = i / 14
                x1 = center_x + int(math.sin(t * 6.28) * size//3)
                x2 = center_x + int(math.sin(t * 6.28 + 3.14159) * size//3)
                y = center_y - size + t * size * 1.5
                pygame.draw.line(self.image, (150, 150, 200), (int(x1), int(y)), (int(x2), int(y)), 2)
            # 变异闪光点
            pygame.draw.circle(self.image, color, (center_x, center_y), size//8)
            self.speed = -15
            
        elif "extinction_touch" in effects or "omega_doom" in effects:
            # 灭绝病原弹 - Ω终末病毒
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 黑暗核心
            pygame.draw.circle(self.image, (20, 20, 25), (center, center), size//2)
            pygame.draw.circle(self.image, (50, 0, 0), (center, center), size//2, 3)
            # Ω符号
            omega_points = []
            for i in range(16):
                t = i / 15
                angle = -0.5 + t * 4
                radius = size//3
                if i < 14:
                    ox = center + int(radius * math.cos(angle))
                    oy = center + int(radius * math.sin(angle) * 0.7)
                    omega_points.append((ox, oy))
            if len(omega_points) > 2:
                pygame.draw.lines(self.image, (150, 0, 0), False, omega_points, 4)
            # Ω两脚
            pygame.draw.line(self.image, (150, 0, 0), (center - size//4, center + size//6), (center - size//4, center + size//3), 4)
            pygame.draw.line(self.image, (150, 0, 0), (center + size//4, center + size//6), (center + size//4, center + size//3), 4)
            # 死亡光环
            for ring in range(3):
                ring_r = size//2 + ring * size//8
                alpha = 150 - ring * 40
                pygame.draw.circle(self.image, (100, 0, 0, alpha), (center, center), ring_r, 2)
            self.speed = -16
        
        # ========== Omega 终极机体子弹涂装 ==========
        elif "omega_fusion" in effects or "divine_judgment" in effects:
            # 七属性融合弹 - 七芒星
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            element_colors = [
                (255, 80, 30), (100, 200, 255), (255, 255, 100),
                (150, 255, 80), (255, 255, 255), (150, 50, 200), (255, 200, 100)
            ]
            # 七芒星
            for i in range(7):
                angle1 = (i * 360 / 7) * math.pi / 180
                angle2 = ((i + 3) * 360 / 7) * math.pi / 180
                x1 = center + int(math.cos(angle1) * size//1.5)
                y1 = center + int(math.sin(angle1) * size//1.5)
                x2 = center + int(math.cos(angle2) * size//1.5)
                y2 = center + int(math.sin(angle2) * size//1.5)
                pygame.draw.line(self.image, element_colors[i], (x1, y1), (x2, y2), 2)
                pygame.draw.circle(self.image, element_colors[i], (x1, y1), size//8)
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//4)
            pygame.draw.circle(self.image, color, (center, center), size//5)
            self.speed = -18
            
        elif "void_collapse" in effects:
            # 虚空坍缩弹 - 黑洞漩涡
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 吸收螺旋
            for spiral in range(4):
                pts = []
                for seg in range(12):
                    progress = seg / 11
                    angle = (spiral * 90 - progress * 270) * math.pi / 180
                    r = (1 - progress) * size//1.5
                    pts.append((center + math.cos(angle) * r, center + math.sin(angle) * r))
                if len(pts) > 1:
                    pygame.draw.lines(self.image, (100, 0, 150), False, pts, 2)
            # 黑洞核心
            pygame.draw.circle(self.image, (20, 0, 30), (center, center), size//4)
            pygame.draw.circle(self.image, (80, 0, 120), (center, center), size//4, 2)
            self.speed = -16
            
        elif "aurora_cascade" in effects:
            # 极光瀑布弹 - 彩虹波浪
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            aurora_colors = [(255, 100, 150), (255, 200, 100), (200, 255, 100), 
                           (100, 255, 200), (100, 200, 255), (150, 100, 255)]
            for layer in range(5):
                pts = []
                for i in range(16):
                    angle = (i * 22.5) * math.pi / 180
                    wave = 3 * math.sin(i * 0.5 + layer)
                    r = size//2 - layer * 3 + wave
                    pts.append((center + math.cos(angle) * r, center + math.sin(angle) * r))
                pygame.draw.polygon(self.image, (*aurora_colors[layer % 6], 180 - layer * 30), pts)
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//5)
            self.speed = -17
            
        elif "celestial_strike" in effects:
            # 天界打击弹 - 蓝金光轮
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 双层光轮
            for layer in range(2):
                for spoke in range(12):
                    angle = (spoke * 30 + layer * 15) * math.pi / 180
                    x2 = center + int(math.cos(angle) * size//1.5)
                    y2 = center + int(math.sin(angle) * size//1.5)
                    spoke_color = (255, 215, 100) if (spoke + layer) % 3 == 0 else (80, 150, 255)
                    pygame.draw.line(self.image, spoke_color, (center, center), (x2, y2), 2)
            pygame.draw.circle(self.image, (80, 150, 255), (center, center), size//4)
            pygame.draw.circle(self.image, (255, 215, 100), (center, center), size//5)
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//8)
            self.speed = -17
            
        elif "infernal_blast" in effects:
            # 地狱爆破弹 - 红黑火焰
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            flame_colors = [(255, 50, 0), (255, 150, 50), (255, 200, 50)]
            # 火焰旋涡
            for ring in range(3):
                for flame in range(8):
                    angle = (flame * 45 + ring * 15) * math.pi / 180
                    flame_len = size//2 - ring * 4
                    fx = center + int(math.cos(angle) * flame_len)
                    fy = center + int(math.sin(angle) * flame_len)
                    tri = [
                        (center + math.cos(angle + 0.3) * (flame_len * 0.3), center + math.sin(angle + 0.3) * (flame_len * 0.3)),
                        (fx, fy),
                        (center + math.cos(angle - 0.3) * (flame_len * 0.3), center + math.sin(angle - 0.3) * (flame_len * 0.3))
                    ]
                    pygame.draw.polygon(self.image, flame_colors[(flame + ring) % 3], tri)
            pygame.draw.circle(self.image, (150, 0, 0), (center, center), size//4)
            pygame.draw.circle(self.image, (255, 100, 0), (center, center), size//6)
            self.speed = -16
            
        elif "primal_force" in effects:
            # 原始神力弹 - 自然叶片
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 叶片环绕
            for i in range(8):
                angle = (i * 45) * math.pi / 180
                lx = center + int(math.cos(angle) * size//2)
                ly = center + int(math.sin(angle) * size//2)
                leaf_angle = angle + math.pi / 2
                leaf_pts = [
                    (lx, ly),
                    (lx + math.cos(leaf_angle + 0.3) * 8, ly + math.sin(leaf_angle + 0.3) * 8),
                    (lx + math.cos(angle) * 10, ly + math.sin(angle) * 10),
                    (lx + math.cos(leaf_angle - 0.3) * 8, ly + math.sin(leaf_angle - 0.3) * 8),
                ]
                pygame.draw.polygon(self.image, (50, 200, 80) if i % 2 == 0 else (255, 215, 0), leaf_pts)
            pygame.draw.circle(self.image, (139, 90, 43), (center, center), size//4)
            pygame.draw.circle(self.image, (50, 200, 80), (center, center), size//5)
            pygame.draw.circle(self.image, (255, 215, 0), (center, center), size//8)
            self.speed = -15
        
        # ========== Genesis 终极机体子弹涂装 ==========
        elif "genesis_star" in effects or "cosmic_origin" in effects:
            # 创世之星弹 - 宇宙扩散
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 扩散环
            for ring in range(4):
                ring_r = size//6 + ring * size//8
                ring_color = (255 - ring * 15, 200 - ring * 20, 100 + ring * 30)
                pygame.draw.circle(self.image, ring_color, (center, center), ring_r, 2)
            # 星系旋臂
            for arm in range(4):
                for seg in range(8):
                    progress = seg / 7
                    angle = (arm * 90 + progress * 120) * math.pi / 180
                    r = progress * size//2
                    pygame.draw.circle(self.image, (255, 220, 150), (int(center + math.cos(angle) * r), int(center + math.sin(angle) * r)), 2)
            pygame.draw.circle(self.image, (255, 200, 100), (center, center), size//4)
            pygame.draw.circle(self.image, (255, 255, 200), (center, center), size//6)
            self.speed = -17
            
        elif "solar_birth" in effects:
            # 太阳诞生弹 - 金红炽焰
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 日冕喷发
            for flare in range(10):
                angle = (flare * 36) * math.pi / 180
                flare_len = size//3 + size//8
                fx = center + int(math.cos(angle) * flare_len)
                fy = center + int(math.sin(angle) * flare_len)
                tri = [
                    (center + math.cos(angle + 0.2) * size//4, center + math.sin(angle + 0.2) * size//4),
                    (fx, fy),
                    (center + math.cos(angle - 0.2) * size//4, center + math.sin(angle - 0.2) * size//4)
                ]
                colors = [(255, 80, 30), (255, 150, 0), (255, 200, 50)]
                pygame.draw.polygon(self.image, colors[flare % 3], tri)
            pygame.draw.circle(self.image, (255, 150, 0), (center, center), size//4)
            pygame.draw.circle(self.image, (255, 200, 50), (center, center), size//5)
            pygame.draw.circle(self.image, (255, 255, 200), (center, center), size//8)
            self.speed = -16
            
        elif "nebula_seed" in effects:
            # 星云种子弹 - 紫粉梦幻
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            nebula_colors = [(200, 150, 255), (255, 150, 200), (150, 180, 255)]
            # 气体云
            for layer in range(4):
                for blob in range(6):
                    angle = (blob * 60 + layer * 15) * math.pi / 180
                    blob_r = size//4 + layer * size//12
                    bx = center + int(math.cos(angle) * blob_r)
                    by = center + int(math.sin(angle) * blob_r)
                    pygame.draw.circle(self.image, (*nebula_colors[(layer + blob) % 3], 120 - layer * 25), (bx, by), size//8)
            pygame.draw.circle(self.image, (200, 150, 255), (center, center), size//5)
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//10)
            self.speed = -16
            
        elif "void_creation" in effects:
            # 虚无创生弹 - 黑白太极
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 太极圆
            pygame.draw.circle(self.image, (200, 200, 200), (center, center), size//2)
            # 黑半
            pts = [(center, center)]
            for i in range(181):
                angle = (i + 180) * math.pi / 180
                pts.append((center + int(math.cos(angle) * size//2), center + int(math.sin(angle) * size//2)))
            pygame.draw.polygon(self.image, (30, 30, 30), pts)
            # 小圆
            pygame.draw.circle(self.image, (255, 255, 255), (center, center - size//4), size//6)
            pygame.draw.circle(self.image, (30, 30, 30), (center, center + size//4), size//6)
            pygame.draw.circle(self.image, (30, 30, 30), (center, center - size//4), size//12)
            pygame.draw.circle(self.image, (255, 255, 255), (center, center + size//4), size//12)
            self.speed = -15
            
        elif "life_spark" in effects:
            # 生命火花弹 - DNA螺旋
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            helix_colors = [(50, 200, 100), (255, 215, 100)]
            for strand in range(2):
                pts = []
                for i in range(12):
                    progress = i / 11
                    angle = progress * math.pi * 2 + strand * math.pi
                    hx = center + int(math.cos(angle) * size//3)
                    hy = center - size//2 + int(progress * size)
                    pts.append((hx, hy))
                if len(pts) > 1:
                    pygame.draw.lines(self.image, helix_colors[strand], False, pts, 3)
            pygame.draw.circle(self.image, (255, 215, 100), (center, center), size//5)
            pygame.draw.circle(self.image, (50, 200, 100), (center, center), size//8)
            self.speed = -16
            
        elif "chaos_burst" in effects:
            # 混沌爆发弹 - 多彩风暴
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            chaos_colors = [(255, 50, 50), (255, 150, 50), (255, 255, 50), 
                          (50, 255, 50), (50, 255, 255), (50, 50, 255), (255, 50, 255)]
            # 混沌尖刺
            for burst in range(12):
                angle = (burst * 30) * math.pi / 180
                burst_len = size//4 + size//6
                bx = center + int(math.cos(angle) * burst_len)
                by = center + int(math.sin(angle) * burst_len)
                spike = [
                    (center + math.cos(angle) * size//6, center + math.sin(angle) * size//6),
                    (bx + math.cos(angle + 0.3) * 4, by + math.sin(angle + 0.3) * 4),
                    (bx, by),
                    (bx + math.cos(angle - 0.3) * 4, by + math.sin(angle - 0.3) * 4),
                ]
                pygame.draw.polygon(self.image, chaos_colors[burst % 7], spike)
            pygame.draw.circle(self.image, chaos_colors[0], (center, center), size//4)
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//8)
            self.speed = -17
        
        # ========== Truth 至尊·世界的真相 子弹涂装 ==========
        elif "eye_of_truth" in effects or "truth_gaze" in effects:
            # 真言之眼弹 - 洞察一切
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 眼睛轮廓
            pygame.draw.ellipse(self.image, (255, 215, 0), 
                              (center - size//2, center - size//3, size, size*2//3), 4)
            # 眼白
            pygame.draw.ellipse(self.image, (255, 255, 255), 
                              (center - size//2 + 4, center - size//3 + 4, size - 8, size*2//3 - 8))
            # 虹膜
            pygame.draw.circle(self.image, (255, 215, 0), (center, center), size//5)
            # 瞳孔
            pygame.draw.circle(self.image, (20, 20, 30), (center, center), size//8)
            # 高光
            pygame.draw.circle(self.image, (255, 255, 255), (center - size//10, center - size//15), size//15)
            self.speed = -16
            
        elif "yin_yang_balance" in effects or "duality_core" in effects:
            # 阴阳平衡弹 - 太极之核
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            taiji_r = size//2
            # 阴阳鱼
            for i in range(2):
                is_yang = (i == 0)
                fish_color = (255, 255, 255) if is_yang else (20, 20, 30)
                start = i * 180
                # 半圆
                pts = [(center, center)]
                for j in range(19):
                    angle = (start + j * 10) * math.pi / 180
                    pts.append((center + math.cos(angle) * taiji_r, center + math.sin(angle) * taiji_r))
                pygame.draw.polygon(self.image, fish_color, pts)
                # 小圆
                sm_angle = (start + 90) * math.pi / 180
                sx = center + math.cos(sm_angle) * (taiji_r // 2)
                sy = center + math.sin(sm_angle) * (taiji_r // 2)
                pygame.draw.circle(self.image, fish_color, (int(sx), int(sy)), taiji_r // 2)
                # 鱼眼
                eye_color = (20, 20, 30) if is_yang else (255, 255, 255)
                pygame.draw.circle(self.image, eye_color, (int(sx), int(sy)), taiji_r // 6)
            # 金边
            pygame.draw.circle(self.image, (255, 215, 0), (center, center), taiji_r + 3, 3)
            self.speed = -15
            
        elif "truth_revelation" in effects or "absolute_insight" in effects:
            # 真理显现弹 - 全知之眼
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 多层眼环
            for ring in range(3):
                ring_r = size//4 + ring * size//8
                ring_color = (255, 215, 0) if ring % 2 == 0 else (255, 255, 255)
                pygame.draw.circle(self.image, ring_color, (center, center), ring_r, 2)
            # 中心瞳孔
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//5)
            pygame.draw.circle(self.image, (255, 215, 0), (center, center), size//6)
            pygame.draw.circle(self.image, (20, 20, 30), (center, center), size//10)
            # 审视射线（8条）
            for i in range(8):
                angle = (i * 45) * math.pi / 180
                x1 = center + int(size//5 * math.cos(angle))
                y1 = center + int(size//5 * math.sin(angle))
                x2 = center + int(size//1.5 * math.cos(angle))
                y2 = center + int(size//1.5 * math.sin(angle))
                pygame.draw.line(self.image, (255, 215, 0), (x1, y1), (x2, y2), 2)
            self.speed = -17
            
        elif "judgment_verdict" in effects or "truth_sentence" in effects:
            # 审判裁决弹 - 真言天平
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 天平横梁
            pygame.draw.line(self.image, (255, 215, 0), (center - size//2, center), (center + size//2, center), 4)
            # 天平支点
            pygame.draw.polygon(self.image, (255, 215, 0), [
                (center, center - size//4),
                (center - size//10, center),
                (center + size//10, center)
            ])
            # 左盘（白）
            pygame.draw.circle(self.image, (255, 255, 255), (center - size//3, center + size//4), size//6)
            pygame.draw.line(self.image, (200, 200, 200), (center - size//3, center), (center - size//3, center + size//4), 2)
            # 右盘（黑）
            pygame.draw.circle(self.image, (20, 20, 30), (center + size//3, center + size//4), size//6)
            pygame.draw.line(self.image, (100, 100, 100), (center + size//3, center), (center + size//3, center + size//4), 2)
            # 中心之眼
            pygame.draw.circle(self.image, (255, 215, 0), (center, center - size//4), size//10)
            pygame.draw.circle(self.image, (20, 20, 30), (center, center - size//4), size//20)
            self.speed = -15
            
        elif "yin_bolt" in effects or "shadow_truth" in effects:
            # 阴极弹 - 暗影真言
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 黑暗核心
            pygame.draw.circle(self.image, (20, 20, 30), (center, center), size//3)
            pygame.draw.circle(self.image, (40, 40, 50), (center, center), size//4)
            # 暗影射线
            for i in range(6):
                angle = (i * 60) * math.pi / 180
                x2 = center + int(size//1.5 * math.cos(angle))
                y2 = center + int(size//1.5 * math.sin(angle))
                pygame.draw.line(self.image, (60, 60, 80), (center, center), (x2, y2), 3)
            # 金色轮廓
            pygame.draw.circle(self.image, (255, 215, 0), (center, center), size//3, 2)
            self.speed = -14
            
        elif "yang_bolt" in effects or "light_truth" in effects:
            # 阳极弹 - 光明真言
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 光明核心
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//3)
            pygame.draw.circle(self.image, (255, 255, 200), (center, center), size//4)
            # 光芒射线
            for i in range(8):
                angle = (i * 45) * math.pi / 180
                x2 = center + int(size//1.5 * math.cos(angle))
                y2 = center + int(size//1.5 * math.sin(angle))
                pygame.draw.line(self.image, (255, 255, 230), (center, center), (x2, y2), 3)
            # 金色轮廓
            pygame.draw.circle(self.image, (255, 215, 0), (center, center), size//3, 2)
            self.speed = -18
            
        elif "rune_circle" in effects or "truth_seal" in effects:
            # 真言符文环弹
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 符文环
            pygame.draw.circle(self.image, (255, 215, 0), (center, center), size//2, 3)
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//3, 2)
            # 符文点
            for i in range(12):
                angle = (i * 30) * math.pi / 180
                rx = center + int(size//2.5 * math.cos(angle))
                ry = center + int(size//2.5 * math.sin(angle))
                pygame.draw.circle(self.image, (255, 215, 0), (rx, ry), size//15)
            # 中心之眼
            pygame.draw.circle(self.image, (255, 255, 255), (center, center), size//6)
            pygame.draw.circle(self.image, (255, 215, 0), (center, center), size//8)
            pygame.draw.circle(self.image, (20, 20, 30), (center, center), size//16)
            self.speed = -16
        
        # ========== Cthulhu 克苏鲁专属子弹形状 ==========
        elif "moon_laser" in effects:
            # 月虹激光
            self.image = pygame.Surface((size, size*2), pygame.SRCALPHA)
            cx = size // 2
            # 激光核心
            pygame.draw.rect(self.image, (100, 150, 220), (cx - 3, 0, 6, size*2))
            pygame.draw.rect(self.image, (255, 255, 255), (cx - 1, 0, 2, size*2))
            # 边缘
            pygame.draw.line(self.image, (160, 100, 200), (cx - 4, 0), (cx - 4, size*2), 1)
            pygame.draw.line(self.image, (160, 100, 200), (cx + 4, 0), (cx + 4, size*2), 1)
            self.speed = -16
            
        elif "moon_eye" in effects:
            # 月能眼珠
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 眼白
            pygame.draw.ellipse(self.image, (220, 210, 200), (center - size//2, center - size//4, size, size//2))
            # 虹膜
            pygame.draw.circle(self.image, (80, 150, 130), (center, center), size//4)
            # 瞳孔
            pygame.draw.ellipse(self.image, (10, 15, 10), (center - 2, center - size//6, 4, size//3))
            # 高光
            pygame.draw.circle(self.image, (255, 255, 255), (center - size//8, center - size//10), 2)
            self.speed = -14
            
        elif "eldritch_horror" in effects:
            # 远古恐惧 - 非欧几何
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 不规则多边形
            points = []
            for i in range(7):
                angle = (i * 360 / 7) * math.pi / 180
                r = size // 2 + (i % 2) * size // 6
                px = center + int(r * math.cos(angle))
                py = center + int(r * math.sin(angle))
                points.append((px, py))
            pygame.draw.polygon(self.image, (60, 50, 70), points)
            pygame.draw.polygon(self.image, (160, 100, 200), points, 1)
            # 眼睛
            pygame.draw.circle(self.image, (200, 200, 180), (center, center), 3)
            pygame.draw.circle(self.image, (10, 10, 10), (center, center), 1)
            self.speed = -13
            
        elif "blood_tentacle" in effects:
            # 血肉触手
            self.image = pygame.Surface((size, size*2), pygame.SRCALPHA)
            cx = size // 2
            # 主体
            pygame.draw.line(self.image, (150, 60, 80), (cx, 0), (cx, size*2), 6)
            pygame.draw.line(self.image, (200, 100, 120), (cx, 0), (cx, size*2), 2)
            # 吸盘
            for i in range(3):
                y = size // 2 + i * size // 2
                pygame.draw.circle(self.image, (100, 40, 60), (cx + 4, y), 3)
            self.speed = -12
            
        elif "madness_orb" in effects:
            # 疯狂之眸
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 光晕
            pygame.draw.circle(self.image, (180, 100, 200, 80), (center, center), size//2)
            # 核心
            pygame.draw.circle(self.image, (200, 180, 220), (center, center), size//3)
            pygame.draw.circle(self.image, (160, 80, 200), (center, center), size//4)
            # 眼
            pygame.draw.circle(self.image, (10, 10, 15), (center, center), 2)
            self.speed = -14
            
        elif "abyssal_maw" in effects:
            # 深渊巨口
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 嘴巴
            pygame.draw.ellipse(self.image, (30, 20, 40), (center - size//2, center - size//3, size, size*2//3))
            # 牙齿
            for i in [-3, 0, 3]:
                pygame.draw.polygon(self.image, (220, 220, 200),
                                   [(center + i - 2, center - size//3),
                                    (center + i + 2, center - size//3),
                                    (center + i, center)])
            self.speed = -11
            
        elif "nightmare_shard" in effects:
            # 噩梦碎片
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 五角碎片
            points = []
            for i in range(5):
                angle = (i * 72 - 90) * math.pi / 180
                r = size // 2 if i % 2 == 0 else size // 4
                px = center + int(r * math.cos(angle))
                py = center + int(r * math.sin(angle))
                points.append((px, py))
            pygame.draw.polygon(self.image, (40, 20, 50), points)
            pygame.draw.polygon(self.image, (180, 100, 200), points, 1)
            self.speed = -15
            
        elif "cosmic_worm" in effects:
            # 宇宙蠕虫
            self.image = pygame.Surface((size, size*3), pygame.SRCALPHA)
            cx = size // 2
            # 虫体
            for i in range(8):
                y = i * size // 3
                thickness = max(2, 5 - i // 2)
                pygame.draw.circle(self.image, (160 - i*10, 120 - i*8, 140 - i*8), (cx, y), thickness)
            self.speed = -13
            
        elif "ritual_sigil" in effects:
            # 仪式符文
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 外环
            pygame.draw.circle(self.image, (180, 140, 80), (center, center), size//2, 1)
            # 五芒星
            star_points = []
            for i in [0, 2, 4, 1, 3]:
                angle = (i * 72 - 90) * math.pi / 180
                px = center + int(size//2 * 0.8 * math.cos(angle))
                py = center + int(size//2 * 0.8 * math.sin(angle))
                star_points.append((px, py))
            pygame.draw.lines(self.image, (200, 160, 100), True, star_points, 1)
            self.speed = -14
            
        elif "deep_one_spawn" in effects:
            # 深潜者幼体
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 卵囊
            pygame.draw.ellipse(self.image, (60, 120, 100, 180), (center - size//3, center - size//2, size*2//3, size))
            pygame.draw.ellipse(self.image, (40, 80, 60), (center - size//3, center - size//2, size*2//3, size), 1)
            # 胚胎
            pygame.draw.circle(self.image, (80, 150, 130), (center, center), 3)
            self.speed = -12
            
        elif "shoggoth_blob" in effects:
            # 修格斯残块
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 不定形
            points = []
            for i in range(10):
                angle = (i * 36) * math.pi / 180
                r = size // 2 + random.randint(-3, 3)
                px = center + int(r * math.cos(angle))
                py = center + int(r * math.sin(angle))
                points.append((px, py))
            pygame.draw.polygon(self.image, (30, 35, 30), points)
            # 眼睛
            for _ in range(3):
                ex = center + random.randint(-5, 5)
                ey = center + random.randint(-5, 5)
                pygame.draw.circle(self.image, (180, 180, 160), (ex, ey), 2)
            self.speed = -10
            
        elif "yog_bubble" in effects:
            # 犹格泡沫
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            center = size
            # 泡沫层
            for i in range(3):
                pygame.draw.circle(self.image, (200, 200, 220, 150 - i*40), (center, center), size//2 - i*3, 1)
            # 核心
            pygame.draw.circle(self.image, (200, 200, 220), (center, center), size//4)
            pygame.draw.circle(self.image, (100, 120, 150), (center, center), size//6)
            self.speed = -13
            
        else:
            # 默认子弹
            self.image = pygame.Surface((size, size*2), pygame.SRCALPHA)
            pygame.draw.rect(self.image, color, (size//4, 0, size//2, size*2))
            pygame.draw.circle(self.image, (255, 255, 255), (size//2, size//2), size//4)
            self.speed = -15

    def update(self):
        self.timer += 1
        
        # 【悖论时钟】冻结弹幕延迟激活机制
        if hasattr(self, '_frozen_timer') and self._frozen_timer > 0:
            self._frozen_timer -= 1
            if self._frozen_timer == 0:
                # 激活：向下方飞行
                self.speed = 8
                rad = math.radians(90)  # 向下
                self.vel = pygame.math.Vector2(math.cos(rad) * self.speed, math.sin(rad) * self.speed)
            return  # 冻结期间不移动
        
        # 【修复】静止敌方子弹（speed=0）生命周期限制，防止无限堆积导致卡死
        if self.is_enemy and hasattr(self, 'speed') and self.speed == 0:
            if self.timer > 180:  # 3秒后销毁静止子弹
                self.kill()
                return
        
        # 【修复】敌方子弹生命周期上限，防止无限堆积
        if self.is_enemy and self.timer > 600:  # 10秒后强制销毁
            self.kill()
            return
        
        # 【Chronos】延迟出现效果
        if hasattr(self, 'spawn_delay') and self.spawn_delay > 0:
            self.spawn_delay -= 1
            if self.spawn_delay > 0:
                return  # 还未到出现时间，暂停更新
        
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
        
        # 【Wormhole】螺旋运动
        if hasattr(self, 'spiral_phase') and hasattr(self, 'spiral_amplitude'):
            self.spiral_phase += 5  # 螺旋速度
            spiral_offset_x = int(self.spiral_amplitude * math.cos(self.spiral_phase * 3.14159 / 180))
            # 先按速度移动
            self.pos += self.vel * speed_factor
            # 再添加螺旋偏移
            self.pos.x += spiral_offset_x * 0.3  # 水平螺旋
            self.rect.center = self.pos
            return  # 螺旋子弹使用特殊移动，直接返回
        
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
        
        # ========== Cthulhu 克苏鲁专属子弹效果 ==========
        elif "moon_laser" in effects:
            # 月虹激光 - 蓝紫色贯穿光束
            pulse = 0.8 + 0.2 * abs(math.sin(t * 3))
            new_image = pygame.Surface((base_w + 12, base_h + 20), pygame.SRCALPHA)
            cx, cy = (base_w + 12) // 2, (base_h + 20) // 2
            
            # 多层光晕
            for i in range(4):
                layer_alpha = int(150 * pulse * (1 - i * 0.2))
                layer_w = 6 + i * 3
                pygame.draw.rect(new_image, (100, 150, 220, layer_alpha),
                               (cx - layer_w // 2, 0, layer_w, base_h + 16))
            
            # 月虹边缘
            pygame.draw.line(new_image, (160, 100, 200, 180), (cx - 4, 0), (cx - 4, base_h + 16), 2)
            pygame.draw.line(new_image, (160, 100, 200, 180), (cx + 4, 0), (cx + 4, base_h + 16), 2)
            
            new_image.blit(self._base_image, (6, 0))
            self._update_bullet_image(new_image)
            
        elif "moon_eye" in effects:
            # 月能眼珠 - 诡异追踪眼球
            blink = abs(math.sin(t * 2))
            new_image = pygame.Surface((base_w + 16, base_h + 16), pygame.SRCALPHA)
            cx, cy = (base_w + 16) // 2, (base_h + 16) // 2
            
            # 眼白
            eye_h = int(8 * blink) if blink > 0.3 else 3
            pygame.draw.ellipse(new_image, (220, 210, 200), (cx - 8, cy - eye_h // 2, 16, eye_h))
            
            # 虹膜（追踪动画）
            if blink > 0.3:
                look_x = int(math.sin(t) * 2)
                pygame.draw.circle(new_image, (80, 150, 130), (cx + look_x, cy), 4)
                # 竖瞳
                pygame.draw.ellipse(new_image, (10, 15, 10), (cx + look_x - 1, cy - 3, 2, 6))
            
            # 血丝
            for i in range(4):
                angle = i * 90 + self.timer * 2
                bx = cx + int(math.cos(math.radians(angle)) * 6)
                by = cy + int(math.sin(math.radians(angle)) * 3)
                pygame.draw.line(new_image, (180, 50, 50, 100), (cx, cy), (bx, by), 1)
            
            self._update_bullet_image(new_image)
            
        elif "eldritch_horror" in effects:
            # 远古恐惧 - 非欧几何扭曲
            warp = math.sin(t * 2)
            new_image = pygame.Surface((base_w + 16, base_h + 16), pygame.SRCALPHA)
            cx, cy = (base_w + 16) // 2, (base_h + 16) // 2
            
            # 扭曲的多边形
            points = []
            for i in range(7):
                angle = i * (360 / 7) + self.timer * 3
                r = 6 + int(warp * 3) + (i % 2) * 2
                px = cx + int(math.cos(math.radians(angle)) * r)
                py = cy + int(math.sin(math.radians(angle)) * r)
                points.append((px, py))
            pygame.draw.polygon(new_image, (60, 50, 70), points)
            pygame.draw.polygon(new_image, (160, 100, 200), points, 1)
            
            # 小眼睛
            for i in range(3):
                ex = cx + int(math.cos(t + i * 2) * 3)
                ey = cy + int(math.sin(t + i * 2) * 3)
                pygame.draw.circle(new_image, (200, 200, 180), (ex, ey), 2)
                pygame.draw.circle(new_image, (10, 10, 10), (ex, ey), 1)
            
            self._update_bullet_image(new_image)
            
        elif "blood_tentacle" in effects:
            # 血肉触手 - 蠕动吸盘
            wave = math.sin(t * 4)
            new_image = pygame.Surface((base_w + 14, base_h + 20), pygame.SRCALPHA)
            cx = (base_w + 14) // 2
            
            # 触手主体
            points = []
            for i in range(8):
                y = i * 3
                x_offset = int(wave * 3 * math.sin(i * 0.8))
                points.append((cx + x_offset, y))
            if len(points) >= 2:
                pygame.draw.lines(new_image, (150, 60, 80), False, points, 6)
                pygame.draw.lines(new_image, (200, 100, 120), False, points, 2)
            
            # 吸盘
            for i in range(2, 7, 2):
                sy = i * 3
                sx = cx + int(wave * 3 * math.sin(i * 0.8))
                pygame.draw.circle(new_image, (100, 40, 60), (sx + 4, sy), 3)
                pygame.draw.circle(new_image, (60, 20, 30), (sx + 4, sy), 2)
            
            self._update_bullet_image(new_image)
            
        elif "madness_orb" in effects:
            # 疯狂之眸 - SAN值归零球
            pulse = 0.7 + 0.3 * abs(math.sin(t * 2.5))
            color_shift = self.timer * 0.1
            new_image = pygame.Surface((base_w + 16, base_h + 16), pygame.SRCALPHA)
            cx, cy = (base_w + 16) // 2, (base_h + 16) // 2
            
            # 诡异颜色脉动
            r = int(160 + math.sin(color_shift) * 40)
            g = int(80 + math.cos(color_shift * 0.7) * 40)
            b = int(200 + math.sin(color_shift * 1.3) * 30)
            
            # 光晕
            for i in range(3):
                glow_r = int(8 * pulse) - i * 2
                if glow_r > 0:
                    pygame.draw.circle(new_image, (r, g, b, 100 - i * 30), (cx, cy), glow_r)
            
            # 核心眼
            pygame.draw.circle(new_image, (200, 180, 220), (cx, cy), 5)
            pygame.draw.circle(new_image, (r, g, b), (cx, cy), 3)
            pygame.draw.circle(new_image, (10, 10, 15), (cx, cy), 1)
            
            self._update_bullet_image(new_image)
            
        elif "abyssal_maw" in effects:
            # 深渊巨口 - 獠牙利齿
            chomp = abs(math.sin(t * 5)) * 0.5 + 0.5
            new_image = pygame.Surface((base_w + 16, base_h + 16), pygame.SRCALPHA)
            cx, cy = (base_w + 16) // 2, (base_h + 16) // 2
            
            # 嘴巴
            mouth_h = int(10 * chomp)
            pygame.draw.ellipse(new_image, (30, 20, 40), (cx - 8, cy - mouth_h // 2, 16, mouth_h))
            
            # 獠牙
            if chomp > 0.4:
                # 上牙
                for i in [-4, 0, 4]:
                    pygame.draw.polygon(new_image, (220, 220, 200),
                                       [(cx + i - 2, cy - mouth_h // 2),
                                        (cx + i + 2, cy - mouth_h // 2),
                                        (cx + i, cy)])
                # 下牙
                for i in [-3, 3]:
                    pygame.draw.polygon(new_image, (200, 200, 180),
                                       [(cx + i - 1, cy + mouth_h // 2),
                                        (cx + i + 1, cy + mouth_h // 2),
                                        (cx + i, cy)])
            
            # 舌头
            pygame.draw.ellipse(new_image, (150, 50, 80), (cx - 3, cy, 6, 4))
            
            self._update_bullet_image(new_image)
            
        elif "nightmare_shard" in effects:
            # 噩梦碎片 - 恐惧结晶
            spin = self.timer * 5
            new_image = pygame.Surface((base_w + 14, base_h + 14), pygame.SRCALPHA)
            cx, cy = (base_w + 14) // 2, (base_h + 14) // 2
            
            # 旋转碎片
            points = []
            for i in range(5):
                angle = spin + i * 72
                r = 7 if i % 2 == 0 else 4
                px = cx + int(math.cos(math.radians(angle)) * r)
                py = cy + int(math.sin(math.radians(angle)) * r)
                points.append((px, py))
            pygame.draw.polygon(new_image, (40, 20, 50), points)
            pygame.draw.polygon(new_image, (180, 100, 200), points, 1)
            
            # 内部恐惧之眼
            pygame.draw.circle(new_image, (100, 80, 120), (cx, cy), 2)
            
            self._update_bullet_image(new_image)
            
        elif "cosmic_worm" in effects:
            # 宇宙蠕虫 - S形扭动
            wave = math.sin(t * 4)
            new_image = pygame.Surface((base_w + 12, base_h + 24), pygame.SRCALPHA)
            cx = (base_w + 12) // 2
            
            # 虫体
            segments = []
            for i in range(10):
                y = i * 2 + 2
                x_offset = int(math.sin(t * 3 + i * 0.5) * 4)
                segments.append((cx + x_offset, y))
            
            # 身体渐变
            for i in range(len(segments) - 1):
                thickness = max(2, 5 - i // 2)
                prog = i / len(segments)
                r = int(160 - prog * 60)
                g = int(120 - prog * 40)
                b = int(140 - prog * 40)
                pygame.draw.line(new_image, (r, g, b), segments[i], segments[i + 1], thickness)
            
            # 头部
            if len(segments) > 0:
                pygame.draw.circle(new_image, (180, 140, 160), segments[0], 3)
            
            self._update_bullet_image(new_image)
            
        elif "ritual_sigil" in effects:
            # 仪式符文 - 旋转召唤阵
            spin = self.timer * 2
            new_image = pygame.Surface((base_w + 16, base_h + 16), pygame.SRCALPHA)
            cx, cy = (base_w + 16) // 2, (base_h + 16) // 2
            
            # 外环
            pygame.draw.circle(new_image, (180, 140, 80), (cx, cy), 7, 1)
            
            # 五芒星
            star_points = []
            star_order = [0, 2, 4, 1, 3]
            for i in star_order:
                angle = spin + i * 72 - 90
                px = cx + int(math.cos(math.radians(angle)) * 6)
                py = cy + int(math.sin(math.radians(angle)) * 6)
                star_points.append((px, py))
            if len(star_points) >= 5:
                pygame.draw.lines(new_image, (200, 160, 100), True, star_points, 1)
            
            # 中心符号
            pygame.draw.circle(new_image, (220, 180, 120), (cx, cy), 2)
            
            self._update_bullet_image(new_image)
            
        elif "deep_one_spawn" in effects:
            # 深潜者幼体 - 鱼人卵囊
            pulse = 0.8 + 0.2 * abs(math.sin(t * 3))
            new_image = pygame.Surface((base_w + 14, base_h + 14), pygame.SRCALPHA)
            cx, cy = (base_w + 14) // 2, (base_h + 14) // 2
            
            # 卵囊外壳
            pygame.draw.ellipse(new_image, (60, 120, 100, 180), (cx - 6, cy - 7, 12, 14))
            pygame.draw.ellipse(new_image, (40, 80, 60), (cx - 6, cy - 7, 12, 14), 1)
            
            # 内部胚胎
            embryo_y = cy + int(math.sin(t * 2) * 2)
            pygame.draw.circle(new_image, (80, 150, 130), (cx, embryo_y), 3)
            # 眼睛
            pygame.draw.circle(new_image, (10, 10, 10), (cx - 1, embryo_y - 1), 1)
            pygame.draw.circle(new_image, (10, 10, 10), (cx + 1, embryo_y - 1), 1)
            
            self._update_bullet_image(new_image)
            
        elif "shoggoth_blob" in effects:
            # 修格斯残块 - 不定形变化
            new_image = pygame.Surface((base_w + 18, base_h + 18), pygame.SRCALPHA)
            cx, cy = (base_w + 18) // 2, (base_h + 18) // 2
            
            # 不定形主体
            points = []
            for i in range(12):
                angle = i * 30 + self.timer * 2
                r = 6 + int(math.sin(t * 3 + i) * 3)
                px = cx + int(math.cos(math.radians(angle)) * r)
                py = cy + int(math.sin(math.radians(angle)) * r)
                points.append((px, py))
            pygame.draw.polygon(new_image, (30, 35, 30), points)
            pygame.draw.polygon(new_image, (50, 60, 50), points, 1)
            
            # 随机眼睛
            for i in range(4):
                ex = cx + int(math.cos(t + i * 1.5) * 4)
                ey = cy + int(math.sin(t * 0.8 + i * 1.5) * 4)
                pygame.draw.circle(new_image, (180, 180, 160), (ex, ey), 2)
                pygame.draw.circle(new_image, (10, 10, 10), (ex, ey), 1)
            
            self._update_bullet_image(new_image)
            
        elif "yog_bubble" in effects:
            # 犹格泡沫 - 时空气泡
            pulse = 0.7 + 0.3 * abs(math.sin(t * 2))
            new_image = pygame.Surface((base_w + 16, base_h + 16), pygame.SRCALPHA)
            cx, cy = (base_w + 16) // 2, (base_h + 16) // 2
            
            # 多层泡沫
            for i in range(3):
                bubble_r = int((8 - i * 2) * pulse)
                alpha = 150 - i * 40
                pygame.draw.circle(new_image, (200, 200, 220, alpha), (cx, cy), bubble_r, 1)
            
            # 核心（全知之眼）
            pygame.draw.circle(new_image, (200, 200, 220), (cx, cy), 4)
            pygame.draw.circle(new_image, (100, 120, 150), (cx, cy), 2)
            
            # 无限符号
            inf_phase = self.timer * 0.1
            for j in range(8):
                ix = cx + int(math.cos(inf_phase + j * 0.8) * 2)
                iy = cy + int(math.sin((inf_phase + j * 0.8) * 2) * 1)
                pygame.draw.circle(new_image, (255, 255, 255, 100), (ix, iy), 1)
            
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
        
        # 反弹逻辑 - 【增强】支持bounce_damage倍数
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
            elif self.rect.bottom > HEIGHT:
                self.vel.y *= -1
                self.pos.y = HEIGHT - self.rect.height
                bounced = True
                
            if bounced: 
                self.bounce -= 1
                
                # 【新】弹跳伤害衰减：每次弹跳应用bounce_damage倍数
                if hasattr(self, 'bounce_damage') and self.bounce_damage < 1.0:
                    if hasattr(self, 'damage'):
                        self.damage = int(self.damage * self.bounce_damage)
                
                # 【优化】减少弹跳粒子避免掉帧（从5个减到2个）
                from sprites import Particle
                for _ in range(2):
                    Particle(self.rect.center, (150, 255, 255))
                
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
        
        # ========== 【星轨天赋阵】天赋燃烧效果处理 ==========
        if hasattr(self, 'talent_burn_timer') and self.talent_burn_timer > 0:
            self.talent_burn_timer -= 1
            if not hasattr(self, 'talent_burn_tick'):
                self.talent_burn_tick = 0
            self.talent_burn_tick += 1
            if self.talent_burn_tick >= 30:  # 每0.5秒造成一次伤害
                self.talent_burn_tick = 0
                burn_dmg = getattr(self, 'talent_burn_damage', 0)
                if burn_dmg > 0:
                    self.hp -= burn_dmg
                    FloatingText(self.rect.centerx, self.rect.top - 15, f"-{int(burn_dmg)}", (255, 100, 0))
                    # 燃烧粒子效果
                    if random.random() < 0.5:
                        Particle(self.rect.center, (255, 100, 0))
        
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
        base_surf = get_boss_surf(self.type, color, data.get('visual', None))
        # 放大Boss尺寸增强压迫感 - 从240放大到320
        self.image = pygame.transform.smoothscale(base_surf, (320, 320))
        self.rect = self.image.get_rect(midbottom=(WIDTH/2, -80))
        
        # 入场震撼效果
        self._entrance_timer = 120  # 2秒入场动画
        self._entrance_scale = 0.3  # 从小放大
        
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
        
        # 入场动画效果
        if hasattr(self, '_entrance_timer') and self._entrance_timer > 0:
            self._entrance_timer -= 1
            # 从小到大的缩放效果
            progress = 1 - (self._entrance_timer / 120)
            self._entrance_scale = 0.3 + 0.7 * progress
            # 重新生成放大后的图像
            base_size = 320
            current_size = int(base_size * self._entrance_scale)
            if current_size > 20:
                base_surf = get_boss_surf(self.type, self.data["color"], self.visual)
                self.image = pygame.transform.smoothscale(base_surf, (current_size, current_size))
                old_center = self.rect.center
                self.rect = self.image.get_rect(center=old_center)
            # 入场时屏幕震动
            if self._entrance_timer > 80:
                self.phase_change_timer = 3
                self.phase_change_magnitude = 8
            
        if self.state == "enter":
            self.rect.y += 2
            if self.rect.top > 50:
                self.state = "fight"
                self.start_y = self.rect.y
                # 入场完成时大震动
                self.phase_change_timer = 30
                self.phase_change_magnitude = 15
        elif self.state == "fight":
            self.shoot_timer += 1
            threshold = (30 if self.enraged else 60) * self.shoot_modifier
            
            # 丰富的攻击模式：每个Boss都有独特的多阶段弹幕
            if self.shoot_timer > threshold:
                self.shoot_timer = 0
                
                # ========== Boss 1: 菌生蟹皇 - 重型生物坦克 ==========
                if self.type == "fungal_colossus":
                    if self.phase_index == 0:  # 阶段1：孢子饱和 - 全屏悬浮孢子地雷
                        for i in range(5):  # 减少到5个
                            x = random.randint(50, WIDTH-50)
                            y = random.randint(80, HEIGHT//2)
                            Bullet(x, y, angle=0, speed=0, is_enemy=True, b_type="spore_mine")
                    elif self.phase_index == 1:  # 阶段2：菌丝波浪 - 左右贴地高波浪弹幕
                        for side in [-1, 1]:
                            for i in range(4):  # 减少到4个
                                Bullet(self.rect.centerx, self.rect.bottom, angle=side*45 + i*8*side, speed=4, is_enemy=True, b_type="mycelium_wave")
                    else:  # 阶段3：混合攻击 - 孢子+波浪同时（大幅减少数量）
                        for i in range(6):  # 从20减少到6
                            x = random.randint(50, WIDTH-50)
                            y = random.randint(80, HEIGHT//2)
                            Bullet(x, y, angle=0, speed=0, is_enemy=True, b_type="spore_mine")
                        for side in [-1, 1]:
                            for i in range(4):  # 从10减少到4
                                Bullet(self.rect.centerx, self.rect.bottom, angle=side*50 + i*10*side, speed=5, is_enemy=True, b_type="mycelium_wave")
                    # 特殊移动：跳跃至玩家头顶
                    if hasattr(self, '_jump_cooldown'):
                        self._jump_cooldown -= 1
                    else:
                        self._jump_cooldown = 0
                    if self._jump_cooldown <= 0:
                        self._jump_cooldown = 180  # 3秒冷却
                        # 屏幕震动效果
                        self.phase_change_timer = 30
                        self.phase_change_magnitude = 12
                        
                # ========== Boss 2: 旱海狂鲨 - 突袭刺客 ==========
                elif self.type == "dune_reaper":
                    if self.phase_index == 0:  # 阶段1：盲点突袭 - 从屏幕边缘冲出
                        # 发射沙尘暴减速区弹幕
                        for i in range(5):
                            angle = random.randint(0, 360)
                            Bullet(self.rect.centerx, self.rect.centery, angle=angle, speed=3, is_enemy=True, b_type="sandstorm")
                    elif self.phase_index == 1:  # 阶段2：流沙漩涡 - 向心引力+岩石碎片
                        for i in range(0, 360, 30):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, speed=5, is_enemy=True, b_type="rock_shard")
                    else:  # 阶段3：狂暴突袭
                        for i in range(0, 360, 45):  # 减少到8个
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, speed=6, is_enemy=True, b_type="rock_shard")
                        for i in range(4):  # 减少到4个
                            angle = random.randint(0, 360)
                            Bullet(self.rect.centerx, self.rect.centery, angle=angle, speed=2, is_enemy=True, b_type="sandstorm")
                    # 特殊移动：钻入背景层，快速移动
                    if random.random() < 0.02:  # 2%几率触发瞬移
                        self.rect.x = random.randint(100, WIDTH-200)
                        self.rect.y = random.randint(50, 200)
                        Particle((self.rect.centerx, self.rect.centery), (220, 180, 80), mode='star')
                        
                # ========== Boss 3: 歌莉娅女王 - 空中轰炸机 ==========
                elif self.type == "plague_empress":
                    if self.phase_index == 0:  # 阶段1：矩阵轰炸 - 网格状瘟疫炸弹
                        for row in range(3):
                            for col in range(5):
                                x = 150 + col * 200
                                Bullet(x, self.rect.bottom, angle=0, speed=4, is_enemy=True, b_type="plague_bomb")
                    elif self.phase_index == 1:  # 阶段2：蜂群拦截 - 自爆工蜂
                        for i in range(6):
                            angle = -60 + i * 20
                            Bullet(self.rect.centerx, self.rect.centery, angle=angle, speed=3, is_enemy=True, b_type="kamikaze_bee")
                    else:  # 阶段3：饱和攻击（减少数量）
                        for col in range(4):  # 减少到4个
                            x = 150 + col * 220
                            Bullet(x, self.rect.bottom, angle=random.randint(-10, 10), speed=5, is_enemy=True, b_type="plague_bomb")
                        for i in range(4):  # 减少到4个
                            angle = random.randint(-90, 90)
                            Bullet(self.rect.centerx, self.rect.centery, angle=angle, speed=4, is_enemy=True, b_type="kamikaze_bee")
                    # 保持在玩家斜上方45度
                    self.rect.y = min(150, self.rect.y)
                    
                # ========== Boss 4: 毁灭魔像 - 阵地推进 ==========
                elif self.type == "flesh_totem":
                    if self.phase_index == 0:  # 阶段1：火箭飞拳 - 回旋镖石拳
                        for side in [-1, 1]:
                            Bullet(self.rect.centerx + side*80, self.rect.centery, angle=side*30, speed=6, is_enemy=True, b_type="rocket_fist")
                    elif self.phase_index == 1:  # 阶段2：石柱囚笼（减少数量）
                        for i in range(-2, 3):  # 减少到5个
                            if i != 0:
                                Bullet(self.rect.centerx + i*180, self.rect.bottom + 50, angle=0, speed=0, is_enemy=True, b_type="stone_pillar")
                        # 激光扫描
                        Bullet(self.rect.centerx, self.rect.centery, angle=0, speed=8, is_enemy=True, b_type="laser_barrage")
                    else:  # 阶段3：全力压制（减少数量）
                        for side in [-1, 1]:
                            Bullet(self.rect.centerx + side*80, self.rect.centery, angle=side*30, speed=7, is_enemy=True, b_type="rocket_fist")
                        for i in range(-2, 3):  # 减少到5个
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*20, speed=5, is_enemy=True, b_type="blood_spike")
                    # 缓慢推进
                    if not hasattr(self, '_advance_x'):
                        self._advance_x = 100
                    self.rect.x = self._advance_x + math.sin(pygame.time.get_ticks()*0.0005) * 50
                    
                # ========== Boss 5: 星神游龙 - 多判定点激光阵列 ==========
                elif self.type == "star_serpent":
                    if self.phase_index == 0:  # 阶段1：星位激光（减少数量）
                        for i in range(0, 360, 45):  # 从18度改为45度
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=0, is_enemy=True, b_type="star_laser")
                        self.angle += 5
                    elif self.phase_index == 1:  # 阶段2：裂变冲撞（减少数量）
                        for i in range(0, 360, 60):  # 从36度改为60度
                            Bullet(self.rect.centerx - 100, self.rect.centery, angle=i, speed=4, is_enemy=True, b_type="nebula")
                            Bullet(self.rect.centerx + 100, self.rect.centery, angle=i + 30, speed=4, is_enemy=True, b_type="star")
                    else:  # 阶段3：星云风暴（减少数量）
                        for i in range(0, 360, 30):  # 从12度间隔改为30度
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=5, is_enemy=True, b_type="star_laser")
                        self.angle += 8
                    # 环绕移动
                    t = pygame.time.get_ticks() * 0.001
                    self.rect.centerx = WIDTH//2 + math.cos(t) * 250
                    self.rect.centery = 180 + math.sin(t*0.7) * 80
                    
                # ========== Boss 6: 终焉巨械·阿瑞斯 - 武器切换 ==========
                elif self.type == "exo_ares":
                    weapon_cycle = (pygame.time.get_ticks() // 2000) % 4  # 每2秒切换武器
                    if self.phase_index == 0:  # 阶段1：武器轮盘
                        if weapon_cycle == 0:  # 高斯炮 - 大范围爆炸
                            Bullet(self.rect.centerx, self.rect.centery, angle=0, speed=6, is_enemy=True, b_type="gauss_bomb")
                        elif weapon_cycle == 1:  # 特斯拉线圈 - 闪电
                            for i in range(-2, 3):
                                Bullet(self.rect.centerx, self.rect.centery, angle=i*25, speed=12, is_enemy=True, b_type="tesla_arc")
                        elif weapon_cycle == 2:  # 激光刀 - 横扫
                            for i in range(-4, 5):
                                Bullet(self.rect.centerx, self.rect.centery, angle=i*10, speed=8, is_enemy=True, b_type="laser_blade")
                        else:  # 等离子喷口
                            for i in range(8):
                                Bullet(self.rect.centerx, self.rect.centery, angle=random.randint(-45, 45), speed=5, is_enemy=True, b_type="plasma")
                    elif self.phase_index == 1:  # 阶段2：时钟光束 - 四道旋转激光
                        for arm in range(4):
                            Bullet(self.rect.centerx, self.rect.centery, angle=self.angle + arm*90, speed=10, is_enemy=True, b_type="clock_beam")
                        self.angle += 3
                    else:  # 阶段3：全武器同时发射
                        Bullet(self.rect.centerx, self.rect.centery, angle=0, speed=6, is_enemy=True, b_type="gauss_bomb")
                        for i in range(-2, 3):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*30, speed=12, is_enemy=True, b_type="tesla_arc")
                        for arm in range(4):
                            Bullet(self.rect.centerx, self.rect.centery, angle=self.angle + arm*90, speed=8, is_enemy=True, b_type="clock_beam")
                        self.angle += 5
                    # 核心保持屏幕中央
                    self.rect.centerx = WIDTH//2 + math.sin(pygame.time.get_ticks()*0.0008) * 60
                    self.rect.centery = 180
                    
                # ========== Boss 7: 亵渎天神 - 贪刀惩罚 ==========
                elif self.type == "radiance_goddess":
                    if self.phase_index == 0:  # 阶段1：圣茧防御 - 密集慢速弹幕
                        for i in range(0, 360, 15):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=2, is_enemy=True, b_type="holy_orb")
                        self.angle += 7
                    elif self.phase_index == 1:  # 阶段2：圣光审判 - 分形几何射线
                        base_angles = [0, 60, 120, 180, 240, 300]
                        for base in base_angles:
                            Bullet(self.rect.centerx, self.rect.centery, angle=base + self.angle, speed=4, is_enemy=True, b_type="holy_judgment")
                            # 分支射线
                            Bullet(self.rect.centerx, self.rect.centery, angle=base + self.angle + 20, speed=3, is_enemy=True, b_type="holy_light")
                            Bullet(self.rect.centerx, self.rect.centery, angle=base + self.angle - 20, speed=3, is_enemy=True, b_type="holy_light")
                        self.angle += 4
                    else:  # 阶段3：神圣审判（减少数量）
                        for i in range(0, 360, 30):  # 从10度改为30度
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=2.5, is_enemy=True, b_type="holy_orb")
                        for i in range(0, 360, 60):  # 从30度改为60度
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle*2, speed=5, is_enemy=True, b_type="holy_judgment")
                        self.angle += 3
                    # 缓慢移动或静止
                    self.rect.centerx = WIDTH//2 + math.sin(pygame.time.get_ticks()*0.0003) * 100
                    self.rect.centery = 200
                    
                # ========== Boss 8: 维度之噬 - 必杀测试 ==========
                elif self.type == "dimension_devourer":
                    if self.phase_index == 0:  # 阶段1：维度冲撞预警
                        # 紫色预警线弹幕
                        for i in range(3):
                            angle = random.choice([0, 45, 90, 135, 180, 225, 270, 315])
                            Bullet(self.rect.centerx, self.rect.centery, angle=angle, speed=15, is_enemy=True, b_type="dimension_warning")
                    elif self.phase_index == 1:  # 阶段2：激光牢笼（减少数量）
                        for i in range(0, 360, 60):  # 从30度改为60度
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=0, is_enemy=True, b_type="laser_cage")
                        self.angle += 2
                    else:  # 阶段3：维度崩塌（减少数量）
                        for i in range(0, 360, 45):  # 从20度改为45度
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=8, is_enemy=True, b_type="void_spike")
                        self.angle += 6
                    # 大部分时间在屏幕外游走
                    if random.random() < 0.03:
                        self.rect.centerx = random.randint(100, WIDTH-100)
                        self.rect.centery = random.randint(80, 250)
                        Particle((self.rect.centerx, self.rect.centery), (120, 0, 200), mode='shockwave')
                        
                # ========== Boss 9: 暴君犽戎 - 极速肉搏 ==========
                elif self.type == "infernal_dragon":
                    if self.phase_index == 0:  # 阶段1：音爆冲刺
                        for i in range(-3, 4):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*15, speed=10, is_enemy=True, b_type="sonic_boom")
                    elif self.phase_index == 1:  # 阶段2：焦土轰炸（减少数量）
                        for i in range(6):  # 从15减少到6
                            x = random.randint(50, WIDTH-50)
                            Bullet(x, 0, angle=0, speed=6, is_enemy=True, b_type="inferno_meteor")
                    else:  # 阶段3：狂暴龙息（减少数量）
                        for i in range(8):  # 从20减少到8
                            x = random.randint(50, WIDTH-50)
                            Bullet(x, 0, angle=random.randint(-10, 10), speed=8, is_enemy=True, b_type="inferno_meteor")
                        for i in range(-3, 4):  # 减少
                            Bullet(self.rect.centerx, self.rect.centery, angle=i*15, speed=12, is_enemy=True, b_type="sonic_boom")
                    # 疯狂近身压制 - 快速移动
                    t = pygame.time.get_ticks() * 0.003
                    self.rect.centerx = WIDTH//2 + math.cos(t) * 300
                    self.rect.centery = 150 + math.sin(t*1.5) * 100
                    
                # ========== Boss 10: 熵之化身 - 规则破坏 ==========
                elif self.type == "entropy_avatar":
                    if self.phase_index == 0:  # 阶段1：幻影死光 - 巨大激光柱缓慢扫过
                        Bullet(self.rect.centerx, self.rect.centery, angle=self.angle, speed=0, is_enemy=True, b_type="phantom_deathray")
                        self.angle += 1.5  # 缓慢旋转
                    elif self.phase_index == 1:  # 阶段2：生命汲取 - 全屏白色弹幕+吸血
                        for i in range(0, 360, 20):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=3, is_enemy=True, b_type="life_drain")
                        self.angle += 5
                    else:  # 阶段3：终极审判（减少数量）
                        # 只保留一只真理之眼
                        Bullet(self.rect.centerx, self.rect.centery, angle=self.angle, speed=0, is_enemy=True, b_type="phantom_deathray")
                        for i in range(0, 360, 40):  # 从15度改为40度
                            Bullet(self.rect.centerx, self.rect.centery, angle=i, speed=4, is_enemy=True, b_type="life_drain")
                        self.angle += 2
                    # 悬停不动，完全依靠眼球精确打击
                    self.rect.centerx = WIDTH//2
                    self.rect.centery = 180
                
                # ========== Boss 11: 绝音夜煞 - 声波可视化 ==========
                elif self.type == "sonic_banshee":
                    if self.phase_index == 0:  # 阶段1：回声定位 - 声呐波探测
                        # 发射扩散声波环
                        for i in range(0, 360, 60):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=3, is_enemy=True, b_type="echo_pulse")
                        self.angle += 10
                    elif self.phase_index == 1:  # 阶段2：爆音咆哮 - 锥形声波
                        # 向下方发射锥形高频声波
                        for i in range(-40, 41, 10):
                            Bullet(self.rect.centerx, self.rect.centery, angle=90 + i, speed=5, is_enemy=True, b_type="sonic_scream")
                    else:  # 阶段3：死亡尖啸 - 全屏声波扭曲
                        for i in range(0, 360, 30):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=4, is_enemy=True, b_type="sonic_scream")
                        # 额外的回声追踪弹
                        for i in range(3):
                            Bullet(self.rect.centerx, self.rect.centery, angle=random.randint(0, 360), speed=2, is_enemy=True, b_type="echo_pulse")
                        self.angle += 15
                    # 悬挂在顶部，左右摆动
                    self.rect.centery = 80
                    self.rect.centerx = WIDTH//2 + math.sin(pygame.time.get_ticks()*0.002) * 200
                    
                # ========== Boss 12: 棱镜核心 - 光线折射 ==========
                elif self.type == "prism_overlord":
                    if self.phase_index == 0:  # 阶段1：光路折射 - 激光网
                        # 发射主激光，模拟折射效果
                        for i in range(6):
                            angle = i * 60 + self.angle
                            Bullet(self.rect.centerx, self.rect.centery, angle=angle, speed=8, is_enemy=True, b_type="prism_laser")
                        self.angle += 5
                    elif self.phase_index == 1:  # 阶段2：镜像反制 - 反弹光弹
                        # 发射折射光弹
                        for i in range(0, 360, 45):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=4, is_enemy=True, b_type="refract_orb")
                        self.angle += 8
                    else:  # 阶段3：棱镜风暴 - 满屏激光
                        for i in range(0, 360, 20):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=6, is_enemy=True, b_type="prism_laser")
                        for i in range(4):
                            Bullet(self.rect.centerx, self.rect.centery, angle=random.randint(0, 360), speed=3, is_enemy=True, b_type="refract_orb")
                        self.angle += 3
                    # 缓慢移动，模拟浮空
                    t = pygame.time.get_ticks() * 0.0005
                    self.rect.centerx = WIDTH//2 + math.cos(t) * 100
                    self.rect.centery = 160 + math.sin(t * 1.5) * 40
                    
                # ========== Boss 13: 腐朽剑圣 - 极速剑气 ==========
                elif self.type == "rotting_kensei":
                    if self.phase_index == 0:  # 阶段1：剑刃风暴 - 圆形剑气领域
                        for i in range(0, 360, 30):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=5, is_enemy=True, b_type="blade_wave")
                        self.angle += 12
                    elif self.phase_index == 1:  # 阶段2：居合·断空 - 横向即死斩
                        # 水平线大范围斩击
                        for i in range(-3, 4):
                            Bullet(0, self.rect.centery + i * 15, angle=0, speed=20, is_enemy=True, b_type="iai_slash")
                        # 警告线
                        Particle((WIDTH//2, self.rect.centery), (200, 50, 255), mode='pulse')
                    else:  # 阶段3：死亡乱舞 - 疯狂连斩
                        for i in range(0, 360, 20):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=8, is_enemy=True, b_type="blade_wave")
                        # 突刺追踪
                        Bullet(self.rect.centerx, self.rect.centery, angle=random.randint(60, 120), speed=15, is_enemy=True, b_type="iai_slash")
                        self.angle += 20
                    # 快速移动，追击玩家
                    t = pygame.time.get_ticks() * 0.003
                    self.rect.centerx = WIDTH//2 + math.cos(t) * 280
                    self.rect.centery = 180 + math.sin(t * 1.2) * 100
                    
                # ========== Boss 14: 悖论时钟 - 时间操控 ==========
                elif self.type == "paradox_clockwork":
                    if self.phase_index == 0:  # 阶段1：时间减速弹 - 凝滞力场
                        for i in range(0, 360, 45):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=2, is_enemy=True, b_type="stasis_orb")
                        self.angle += 6
                    elif self.phase_index == 1:  # 阶段2：凝滞力场 - 蓄力弹幕
                        # 发射停滞在空中的弹幕
                        for i in range(5):
                            x = random.randint(100, WIDTH-100)
                            y = random.randint(100, HEIGHT//2)
                            Bullet(x, y, angle=90, speed=0, is_enemy=True, b_type="frozen_bullet")
                        # 齿轮弹幕
                        for i in range(0, 360, 60):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=4, is_enemy=True, b_type="gear_projectile")
                        self.angle += 4
                    else:  # 阶段3：时间风暴 - 多层旋转弹幕
                        # 顺时针层
                        for i in range(0, 360, 40):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i + self.angle, speed=3, is_enemy=True, b_type="gear_projectile")
                        # 逆时针层
                        for i in range(0, 360, 40):
                            Bullet(self.rect.centerx, self.rect.centery, angle=i - self.angle*2, speed=5, is_enemy=True, b_type="stasis_orb")
                        self.angle += 5
                    # 保持中央，缓慢旋转
                    self.rect.centerx = WIDTH//2
                    self.rect.centery = 180
                    
                # ========== Boss 15: 熔核巨兽 - 岩浆地形 ==========
                elif self.type == "molten_behemoth":
                    if self.phase_index == 0:  # 阶段1：岩浆海啸 - 上升岩浆
                        # 底部发射上升岩浆弹
                        for i in range(5):
                            x = random.randint(50, WIDTH-50)
                            Bullet(x, HEIGHT + 20, angle=-90, speed=3, is_enemy=True, b_type="lava_wave")
                    elif self.phase_index == 1:  # 阶段2：陨石天降 - 岩石雨
                        for i in range(6):
                            x = random.randint(50, WIDTH-50)
                            Bullet(x, -20, angle=90 + random.randint(-20, 20), speed=5, is_enemy=True, b_type="molten_meteor")
                    else:  # 阶段3：火山喷发 - 全方位攻击
                        # 岩浆喷射
                        for i in range(-60, 61, 15):
                            Bullet(self.rect.centerx, self.rect.centery, angle=-90 + i, speed=6, is_enemy=True, b_type="lava_burst")
                        # 陨石雨
                        for i in range(4):
                            x = random.randint(50, WIDTH-50)
                            Bullet(x, -20, angle=90, speed=7, is_enemy=True, b_type="molten_meteor")
                    # 呆在屏幕下方
                    self.rect.centery = HEIGHT - 120
                    self.rect.centerx = WIDTH//2 + math.sin(pygame.time.get_ticks()*0.0008) * 150
                        
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
            # spawn - 只创建粒子效果，不生成实际敌人（避免卡顿）
            spawn_cfg = phase_cfg.get('spawn')
            if spawn_cfg:
                cnt = min(spawn_cfg.get('count', 1), 3)  # 最多3个粒子
                for i in range(cnt):
                    Particle((self.rect.centerx + random.randint(-80, 80), self.rect.centery + random.randint(20, 80)), self.visual.get('core_color', CYAN) if self.visual else CYBER_AMBER, mode='star')
            # effect - 限制粒子数量
            eff = phase_cfg.get('effect')
            if eff:
                eff_type = eff.get('type')
                eff_count = min(eff.get('count', 3), 8)  # 最多8个粒子效果
                for i in range(eff_count):
                    if eff_type == 'wind_gusts':
                        Particle((self.rect.centerx + random.randint(-100, 100), self.rect.centery + random.randint(-20, 20)), WIND_BLUE, mode='pulse')
                    elif eff_type == 'storm_burst':
                        Particle((self.rect.centerx + random.randint(-80, 80), self.rect.centery + random.randint(-40, 40)), WIND_BLUE, mode='bloom')
                    elif eff_type == 'teleport_dash':
                        Particle((self.rect.centerx, self.rect.centery), MAGENTA, mode='star')
                        self.rect.x = random.randint(100, WIDTH-100)
                    # ===== 新Boss阶段效果 =====
                    elif eff_type == 'spore_saturation':
                        Particle((self.rect.centerx + random.randint(-120, 120), self.rect.centery + random.randint(-60, 60)), (60, 180, 200), mode='bloom')
                    elif eff_type == 'mycelium_wave':
                        Particle((self.rect.centerx + random.randint(-80, 80), self.rect.bottom), (30, 80, 120), mode='pulse')
                    elif eff_type == 'ground_shake':
                        self.phase_change_magnitude = 15
                        Particle((self.rect.centerx, self.rect.bottom + 20), (100, 80, 60), mode='shockwave')
                    elif eff_type == 'blindspot_rush':
                        Particle((random.randint(0, WIDTH), random.randint(0, HEIGHT)), (220, 180, 80), mode='star')
                    elif eff_type == 'quicksand_vortex':
                        Particle((self.rect.centerx, self.rect.centery), (180, 140, 60), mode='shockwave')
                    elif eff_type == 'matrix_bombing':
                        Particle((self.rect.centerx + random.randint(-100, 100), self.rect.bottom), (57, 255, 20), mode='bloom')
                    elif eff_type == 'rocket_fist':
                        Particle((self.rect.centerx + random.choice([-80, 80]), self.rect.centery), (180, 30, 30), mode='star')
                    elif eff_type == 'stone_pillar_cage':
                        Particle((self.rect.centerx + random.randint(-150, 150), self.rect.bottom + 30), (60, 20, 20), mode='pulse')
                    elif eff_type == 'star_position_laser':
                        Particle((self.rect.centerx + random.randint(-60, 60), self.rect.centery + random.randint(-60, 60)), (200, 100, 255), mode='star')
                    elif eff_type == 'fission_charge':
                        Particle((self.rect.centerx - 100, self.rect.centery), (100, 50, 150), mode='shockwave')
                        Particle((self.rect.centerx + 100, self.rect.centery), (100, 50, 150), mode='shockwave')
                    elif eff_type == 'weapon_roulette':
                        Particle((self.rect.centerx + random.randint(-50, 50), self.rect.centery + random.randint(-50, 50)), (255, 100, 255), mode='star')
                    elif eff_type == 'clock_beam':
                        Particle((self.rect.centerx, self.rect.centery), (200, 200, 220), mode='bloom')
                    elif eff_type == 'cocoon_defense':
                        Particle((self.rect.centerx, self.rect.centery), (255, 215, 0), mode='pulse')
                    elif eff_type == 'holy_judgment' or eff_type == 'fractal_beam':
                        Particle((self.rect.centerx + random.randint(-80, 80), self.rect.centery + random.randint(-80, 80)), (255, 180, 100), mode='bloom')
                    elif eff_type == 'dimension_charge':
                        Particle((random.randint(0, WIDTH), random.randint(0, HEIGHT//3)), (120, 0, 200), mode='star')
                    elif eff_type == 'laser_cage':
                        Particle((self.rect.centerx, self.rect.centery), (20, 0, 40), mode='shockwave')
                    elif eff_type == 'sonic_dash':
                        Particle((self.rect.centerx, self.rect.centery), (255, 200, 50), mode='star')
                    elif eff_type == 'scorched_earth':
                        Particle((random.randint(50, WIDTH-50), random.randint(0, 100)), (255, 69, 0), mode='bloom')
                    elif eff_type == 'phantom_deathray':
                        Particle((self.rect.centerx, self.rect.centery), (255, 255, 255), mode='pulse')
                    elif eff_type == 'life_drain':
                        Particle((self.rect.centerx + random.randint(-40, 40), self.rect.centery + random.randint(-40, 40)), (220, 220, 230), mode='star')
                    # ===== 新Boss 11-15 阶段效果 =====
                    elif eff_type == 'echo_pulse':
                        Particle((self.rect.centerx + random.randint(-60, 60), self.rect.centery + random.randint(-40, 40)), (180, 180, 255), mode='pulse')
                    elif eff_type == 'sonic_scream':
                        Particle((self.rect.centerx, self.rect.centery), (200, 200, 255), mode='shockwave')
                    elif eff_type == 'sonic_distortion':
                        for j in range(3):
                            Particle((random.randint(0, WIDTH), random.randint(0, HEIGHT//2)), (220, 220, 255), mode='pulse')
                    elif eff_type == 'prism_laser':
                        Particle((self.rect.centerx + random.randint(-50, 50), self.rect.centery + random.randint(-30, 30)), (255, 180, 255), mode='star')
                    elif eff_type == 'mirror_shield':
                        Particle((self.rect.centerx, self.rect.centery), (200, 255, 255), mode='bloom')
                    elif eff_type == 'laser_web':
                        Particle((random.randint(50, WIDTH-50), random.randint(50, 200)), (255, 200, 255), mode='star')
                    elif eff_type == 'blade_storm':
                        Particle((self.rect.centerx + random.randint(-80, 80), self.rect.centery + random.randint(-60, 60)), (200, 100, 255), mode='star')
                    elif eff_type == 'iai_slash':
                        Particle((WIDTH//2, self.rect.centery), (200, 50, 255), mode='shockwave')
                    elif eff_type == 'death_blade':
                        for j in range(2):
                            Particle((random.randint(0, WIDTH), self.rect.centery + random.randint(-20, 20)), (255, 150, 255), mode='pulse')
                    elif eff_type == 'time_slow':
                        Particle((self.rect.centerx, self.rect.centery), (255, 220, 100), mode='bloom')
                    elif eff_type == 'stasis_field':
                        Particle((random.randint(100, WIDTH-100), random.randint(100, HEIGHT//2)), (255, 240, 150), mode='pulse')
                    elif eff_type == 'time_rewind':
                        for j in range(4):
                            Particle((self.rect.centerx + random.randint(-40, 40), self.rect.centery + random.randint(-40, 40)), (200, 160, 60), mode='star')
                    elif eff_type == 'lava_wave':
                        Particle((random.randint(50, WIDTH-50), HEIGHT - 50), (255, 100, 20), mode='bloom')
                    elif eff_type == 'meteor_rain':
                        Particle((random.randint(50, WIDTH-50), 0), (255, 150, 50), mode='star')
                    elif eff_type == 'eruption':
                        for j in range(3):
                            Particle((self.rect.centerx + random.randint(-80, 80), self.rect.centery + random.randint(-60, 60)), (255, 80, 20), mode='bloom')
            # fire rate change
            if 'fire_rate_mult' in phase_cfg:
                # Set modifier directly (don't stack multiplicatively across phases)
                self.shoot_modifier = phase_cfg.get('fire_rate_mult', self.shoot_modifier)
        else:
            # 新Boss默认阶段效果
            if self.type == 'fungal_colossus':
                self.phase_change_magnitude = 15
                for i in range(5 + idx*3):
                    Particle((self.rect.centerx + random.randint(-100, 100), self.rect.centery + random.randint(-50, 50)), (60, 180, 200), mode='bloom')
            elif self.type == 'dune_reaper':
                for i in range(4 + idx*2):
                    Particle((random.randint(0, WIDTH), random.randint(0, HEIGHT//2)), (220, 180, 80), mode='star')
            elif self.type == 'plague_empress':
                for i in range(6 + idx*2):
                    Particle((self.rect.centerx + random.randint(-80, 80), self.rect.bottom + random.randint(0, 40)), (57, 255, 20), mode='bloom')
            elif self.type == 'flesh_totem':
                self.phase_change_magnitude = 12
                for i in range(4 + idx*2):
                    Particle((self.rect.centerx + random.randint(-60, 60), self.rect.centery + random.randint(-40, 40)), (180, 30, 30), mode='pulse')
            elif self.type == 'star_serpent':
                for i in range(8 + idx*3):
                    Particle((self.rect.centerx + random.randint(-100, 100), self.rect.centery + random.randint(-80, 80)), (200, 100, 255), mode='star')
            elif self.type == 'exo_ares':
                for i in range(6 + idx*2):
                    Particle((self.rect.centerx + random.randint(-60, 60), self.rect.centery + random.randint(-60, 60)), (255, 100, 255), mode='star')
            elif self.type == 'radiance_goddess':
                for i in range(10 + idx*3):
                    Particle((self.rect.centerx + random.randint(-80, 80), self.rect.centery + random.randint(-80, 80)), (255, 215, 0), mode='bloom')
            elif self.type == 'dimension_devourer':
                for i in range(5 + idx*2):
                    Particle((random.randint(0, WIDTH), random.randint(0, HEIGHT//2)), (120, 0, 200), mode='shockwave')
            elif self.type == 'infernal_dragon':
                self.phase_change_magnitude = 10
                for i in range(8 + idx*3):
                    Particle((self.rect.centerx + random.randint(-100, 100), self.rect.centery + random.randint(-60, 60)), (255, 69, 0), mode='bloom')
            elif self.type == 'entropy_avatar':
                for i in range(6 + idx*2):
                    Particle((self.rect.centerx + random.randint(-50, 50), self.rect.centery + random.randint(-50, 50)), (255, 255, 255), mode='star')
            # ===== 新Boss 11-15 默认阶段效果 =====
            elif self.type == 'sonic_banshee':
                for i in range(5 + idx*2):
                    Particle((self.rect.centerx + random.randint(-80, 80), self.rect.centery + random.randint(-40, 40)), (200, 200, 255), mode='pulse')
            elif self.type == 'prism_overlord':
                for i in range(6 + idx*2):
                    Particle((self.rect.centerx + random.randint(-60, 60), self.rect.centery + random.randint(-60, 60)), (255, 180, 255), mode='star')
            elif self.type == 'rotting_kensei':
                self.phase_change_magnitude = 10
                for i in range(4 + idx*3):
                    Particle((self.rect.centerx + random.randint(-100, 100), self.rect.centery + random.randint(-80, 80)), (200, 100, 255), mode='star')
            elif self.type == 'paradox_clockwork':
                for i in range(5 + idx*2):
                    Particle((self.rect.centerx + random.randint(-50, 50), self.rect.centery + random.randint(-50, 50)), (255, 220, 100), mode='bloom')
            elif self.type == 'molten_behemoth':
                self.phase_change_magnitude = 15
                for i in range(6 + idx*3):
                    Particle((self.rect.centerx + random.randint(-100, 100), self.rect.centery + random.randint(-60, 60)), (255, 80, 20), mode='bloom')
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
        self.bullet_theme_id = None  # 保存涂装ID
        try:
            from customization import customization_manager, BULLET_THEMES
            equipped_bullet_id = customization_manager.get_equipped_theme(plane_id, bullet=True)
            
            # 如果没有装备涂装或装备的是默认涂装，尝试使用该机体的免费专属涂装
            if not equipped_bullet_id or equipped_bullet_id == "default":
                # 查找该机体的免费专属涂装
                for theme_id, theme_data in BULLET_THEMES.items():
                    if (theme_data.get('exclusive_plane') == plane_id and 
                        theme_data.get('cost', 0) == 0 and
                        theme_data.get('color')):  # 确保有颜色定义
                        equipped_bullet_id = theme_id
                        break
            
            if equipped_bullet_id and equipped_bullet_id in BULLET_THEMES:
                theme = BULLET_THEMES[equipped_bullet_id]
                # 确保涂装有有效的颜色
                if theme.get('color'):
                    self.bullet_theme = theme
                    self.bullet_theme_id = equipped_bullet_id
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
        if self.plane_id == "sdmg":
            self.sdmg_base_delay = self.shoot_delay
            self.sdmg_deploy_mine_on_cooldown = False
            self.sdmg_mine_spawned_this_cooldown = False
            self.sdmg_overheat_steam_timer = 0
        self.ult_charge_rate = self.plane_data.get("ult_charge_rate", 1.0)  # 大招充能速率倍率

        # 敌方持续效果状态
        self.hazard_slow_timer = 0
        self.hazard_slow_mult = 1.0
        self.poison_dot_timer = 0
        self.poison_dot_damage = 0
        self.poison_tick_cd = 0
        self.grab_timer = 0
        self.grab_anchor = None
        self.grab_pull = 0.0
        self.burn_timer = 0
        self.burn_damage = 0
        self.burn_tick_cd = 0
        self.freeze_timer = 0
        self.is_frozen = False
        self.emp_timer = 0
        self.sonic_timer = 0
        self.armor_break_timer = 0
        self.whiteout_timer = 0
        self.whiteout_intensity = 0.0
        self.parasite_timer = 0
        self.parasite_damage = 0
        self.parasite_tick_cd = 0
        self.mirror_timer = 0
        self.mirror_feedback_damage = 0
        self.mirror_tick_cd = 0
        self.mirror_tick_timer = 0
        self.mirror_fire_cd = 0
        self.phase_lock_timer = 0
        self.phase_lock_anchor = None
        self.phase_lock_displacement = 0.0
        self.phase_lock_pulse_cd = 0
        self.phase_lock_pulse_timer = 0
        self.phase_lock_invert = False
        self.spore_root_timer = 0
        self.spore_root_damage = 0
        self.spore_root_tick_cd = 0
        self.spore_root_tick_timer = 0
        self.spore_root_slow_mult = 1.0
        self.solar_burn_timer = 0
        self.solar_burn_damage = 0
        self.solar_burn_tick_cd = 0
        self.solar_burn_tick_timer = 0
        
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
        
        # ========== 【Goliath 瘟疫冲锋】双击检测系统 ==========
        self.goliath_key_released = True  # 按键是否已释放
        self.goliath_last_tap_key = None  # 上次按下的方向键
        self.goliath_tap_timer = 0        # 双击窗口计时器
        self.goliath_double_tap_window = 18  # 18帧内视为双击（约0.3秒）
        self.goliath_dash_cooldown = 0    # 冲锋冷却
        self.goliath_invincible = 0       # 瘟疫冲锋无敌帧计时器
        
        # ========== 【Sepulcher 至尊灾厄】系统 ==========
        self.sepulcher_fury = 0           # 暴怒值 (0-100)
        self.sepulcher_max_fury = 100     # 最大暴怒值
        self.sepulcher_fury_active = False  # 暴怒激活状态
        self.sepulcher_fury_timer = 0     # 暴怒持续时间
        self.sepulcher_charge_timer = 0   # 双子魔君蓄力计时
        self.sepulcher_brothers_active = False  # 双子魔君是否激活
        self.sepulcher_skull_tail = None  # 骷髅尾巴实例
        self.sepulcher_aura = None        # 灾厄力场实例
        self.sepulcher_halo = None        # 魔法阵光环实例
        self.sepulcher_graze_radius = 80  # 擦弹检测半径
        
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
        
        # ========== 【新增】第四大招系统（E键） ==========
        self.ult4_charge = 0
        self.max_ult4_charge = 100  # 第四大招：只能储存1次
        self.ult4_cooldown = 0
        self.ult4_max_cooldown = 180  # 冷却3秒
        
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
        
        # 【新增】游戏统计数据
        self.stats = {
            'kills': 0,              # 总击杀数
            'damage_dealt': 0,       # 总造成伤害
            'shots_fired': 0,        # 发射子弹数
            'hits': 0,               # 命中次数
            'crits': 0,              # 暴击次数
            'time_played': 0,        # 游戏时间（帧数）
            'max_combo': 0,          # 最高连击
            'current_combo': 0,      # 当前连击
            'combo_timer': 0,        # 连击计时器（180帧=3秒内需再次击杀）
        }
        
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
        
        # 【混沌虫洞】维度裂缝状态
        self.rift_energy = 0          # 裂缝能量
        self.max_rift_energy = 100    # 最大裂缝能量
        self.rift_portals = []        # 活跃虫洞列表
        self.max_rift_portals = 3     # 最大同时存在虫洞数
        self.rift_teleport_cooldown = 0  # 传送冷却
        
        # 【时之回响·克洛诺斯】时间系统状态
        self.chronos_charge = 0       # 时间能量
        self.max_chronos_charge = 100 # 最大时间能量
        self.chronos_echo_stacks = 0  # 时间回响层数（叠加伤害）
        self.max_chronos_echoes = 5   # 最大回响层数
        self.chronos_rewinding = False  # 是否正在回溯
        self.chronos_rewind_timer = 0   # 回溯持续时间
        self.chronos_position_history = []  # 位置历史记录（用于回溯）
        self.max_history_length = 180   # 记录3秒历史（60帧/秒 × 3）
        self.chronos_frozen_bullets = []  # 时停的子弹列表
        
        # 【幻镜·万华】镜像分身系统
        self.mirage_mirror_count = 0       # 当前分身数量
        self.max_mirage_mirrors = 3        # 最大分身数
        self.mirage_sync_level = 0         # 同步等级（0-5，影响分身伤害）
        self.active_mirrors = []           # 活跃分身位置列表 [(x, y), ...]
        self.mirror_duration = 0           # 分身持续时间
        self.mirror_cooldown = 0           # 召唤冷却
        self.mirage_refraction_bonus = 0   # 折射加成
        
        # 【命运赌徒·艾斯】赌博系统
        self.gambit_luck_meter = 50        # 运气值（0-100，50为中性）
        self.gambit_combo_streak = 0       # 连击数
        self.gambit_jackpot_count = 0      # 累计大奖次数
        self.gambit_total_rolls = 0        # 总掷骰次数
        self.gambit_next_crit = False      # 下次必定暴击
        self.gambit_fortune_wheel_active = False  # 命运轮盘大招是否激活
        self.gambit_wheel_bonus = 1.0      # 轮盘加成倍率
        
        # ========== 【星轨天赋阵】天赋效果存储 ==========
        self.talent_effects = {}           # 存储计算后的天赋效果
        self.base_damage = self.damage     # 保存基础伤害
        self.base_speed = self.speed       # 保存基础速度
        self.base_max_hp = self.max_hp     # 保存基础生命
        self.base_shoot_delay = self.shoot_delay  # 保存基础射击间隔
        self.base_crit_chance = self.crit_chance  # 保存基础暴击率
        self.base_crit_mult = self.crit_mult      # 保存基础暴击伤害
        
        # 天赋触发状态
        self.talent_burn_duration = 0      # 燃烧持续时间（天赋）
        self.talent_freeze_chance = 0.0    # 冻结几率（天赋）
        self.talent_chain_chance = 0.0     # 连锁闪电几率（天赋）
        self.talent_double_damage_chance = 0.0  # 双倍伤害几率（天赋）
        self.talent_dodge_chance = 0.0     # 闪避率（天赋）
        self.talent_dodge_invuln = 0.0     # 闪避后无敌时间（天赋）
        self.talent_execute_damage = 0.0   # 处决伤害加成（天赋）
        self.talent_kill_energy = 0.0      # 击杀回复能量（天赋）
        self.talent_kill_heal = 0.0        # 击杀回复生命（天赋）
        self.talent_exp_mult = 0.0         # 经验倍率加成（天赋）
        self.talent_pickup_range = 0.0     # 拾取范围加成（天赋）
        self.talent_drop_rate = 0.0        # 掉落率加成（天赋）
        self.talent_wingman_damage = 0.0   # 僚机伤害加成（天赋）
        self.talent_wingman_fire_rate = 0.0  # 僚机射速加成（天赋）
        self.talent_wingman_max = 0        # 僚机上限加成（天赋）
        self.talent_shield_capacity = 0.0  # 护盾容量加成（天赋）
        self.talent_shield_regen = 0.0     # 护盾回复加成（天赋）
        self.talent_shield_reflect = 0.0   # 护盾反弹伤害（天赋）
        self.talent_hp_regen_timer = 0     # 生命回复计时器
        self.talent_hp_regen_percent = 0.0 # 生命回复百分比（天赋）
        self.talent_low_hp_reduction = 0.0 # 低血量减伤（天赋）
        self.talent_full_shield_reduction = 0.0  # 满护盾减伤（天赋）
        self.talent_hit_speed_boost = 0.0  # 被击后移速加成（天赋）
        self.talent_hit_speed_timer = 0    # 被击后移速持续时间
        self.talent_rare_chance = 0.0      # 稀有卡概率加成（天赋）
        self.talent_extra_choices = 0      # 选卡数量加成（天赋）
        self.talent_gold_pity = 0          # 金卡保底（天赋）
        self.talent_double_levelup = 0.0   # 双倍升级几率（天赋）
        self.talent_card_double = 0.0      # 卡牌效果翻倍几率（天赋）
        
        # 终极效果
        self.ultimate_destruction_active = False  # 毁灭终极
        self.ultimate_guardian_death_save = False # 守护终极（死亡豁免）
        self.ultimate_destiny_free_reroll = 0     # 命运终极（免费刷新）
        
        # 应用天赋效果
        self.apply_talent_effects()

    def apply_talent_effects(self):
        """应用星轨天赋阵效果"""
        # 获取天赋效果
        self.talent_effects = talent_manager.calculate_effects()
        effects = self.talent_effects
        
        # ==================== 毁灭星轨效果 ====================
        # 基础伤害加成
        damage_mult = effects.get("damage_mult", 0)
        self.damage = self.base_damage * (1 + damage_mult)
        
        # 暴击率加成
        crit_bonus = effects.get("crit_chance", 0)
        self.crit_chance = self.base_crit_chance + crit_bonus
        
        # 暴击伤害加成
        crit_dmg_bonus = effects.get("crit_damage", 0)
        self.crit_mult = self.base_crit_mult + crit_dmg_bonus
        
        # 射速加成（减少射击间隔）
        fire_rate = effects.get("fire_rate", 0)
        self.shoot_delay = max(1, int(self.base_shoot_delay * (1 - fire_rate)))
        
        # 子弹速度加成
        self.bullet_speed_mult = 1.0 + effects.get("bullet_speed", 0)
        
        # 穿透加成
        self.piercing = int(effects.get("pierce", 0))
        
        # 特效触发
        self.talent_burn_duration = effects.get("burn_duration", 0)
        self.talent_freeze_chance = effects.get("freeze_chance", 0)
        self.talent_chain_chance = effects.get("chain_chance", 0)
        self.talent_double_damage_chance = effects.get("double_damage_chance", 0)
        self.talent_execute_damage = effects.get("execute_damage", 0)
        self.talent_kill_energy = effects.get("kill_energy", 0)
        
        # ==================== 守护星轨效果 ====================
        # 护盾容量加成
        shield_capacity = effects.get("shield_capacity", 0)
        self.talent_shield_capacity = shield_capacity
        if shield_capacity > 0:
            # 基础护盾为50，按比例提升
            base_shield = 50
            self.max_shield = int(base_shield * (1 + shield_capacity))
            self.shield = min(self.shield, self.max_shield)
        
        # 护盾回复/反射
        self.talent_shield_regen = effects.get("shield_regen", 0)
        self.talent_shield_reflect = effects.get("shield_reflect", 0)
        self.talent_full_shield_reduction = effects.get("full_shield_reduction", 0)
        
        # 最大生命加成
        hp_bonus = effects.get("max_hp", 0)
        if hp_bonus > 0:
            old_max = self.max_hp
            self.max_hp = int(self.base_max_hp * (1 + hp_bonus))
            # 按比例恢复当前生命
            if old_max > 0:
                self.hp = int(self.hp * self.max_hp / old_max)
        
        # 生命回复
        self.talent_hp_regen_percent = effects.get("hp_regen_percent", 0)
        self.talent_kill_heal = effects.get("kill_heal", 0)
        self.talent_low_hp_reduction = effects.get("low_hp_reduction", 0)
        
        # 移动速度加成
        speed_bonus = effects.get("move_speed", 0)
        self.speed = self.base_speed * (1 + speed_bonus)
        
        # 闪避相关
        self.talent_dodge_chance = effects.get("dodge_chance", 0)
        self.talent_dodge_invuln = effects.get("dodge_invuln", 0)
        self.talent_hit_speed_boost = effects.get("hit_speed_boost", 0)
        
        # ==================== 命运星轨效果 ====================
        # 经验/成长
        self.talent_exp_mult = effects.get("exp_mult", 0)
        self.talent_pickup_range = effects.get("pickup_range", 0)
        self.talent_drop_rate = effects.get("drop_rate", 0)
        self.talent_double_levelup = effects.get("double_levelup", 0)
        
        # 拾取范围应用
        if self.talent_pickup_range > 0:
            base_pickup = 150
            self.pickup_range = base_pickup * (1 + self.talent_pickup_range)
        
        # 幸运/卡牌
        self.talent_rare_chance = effects.get("rare_chance", 0)
        self.talent_extra_choices = int(effects.get("extra_choices", 0))
        self.talent_gold_pity = int(effects.get("gold_pity", 0)) if effects.get("gold_pity", 0) > 0 else 0
        self.talent_card_double = effects.get("card_double", 0)
        
        # 僚机加成
        self.talent_wingman_damage = effects.get("wingman_damage", 0)
        self.talent_wingman_fire_rate = effects.get("wingman_fire_rate", 0)
        self.talent_wingman_max = int(effects.get("wingman_max", 0))
        if self.talent_wingman_max > 0:
            self.max_wingmen = 4 + self.talent_wingman_max
        
        # ==================== 终极效果 ====================
        # 毁灭终极：歼星者
        if "ultimate_destruction_rage_damage" in effects:
            self.ultimate_destruction_active = True
        
        # 守护终极：不朽堡垒（死亡豁免）
        if "ultimate_guardian_death_save" in effects:
            self.ultimate_guardian_death_save = True
        
        # 命运终极：命运织者（免费刷新）
        if "ultimate_destiny_free_reroll" in effects:
            self.ultimate_destiny_free_reroll = effects.get("ultimate_destiny_free_reroll", 0)
        
        # ==================== 路线共鸣效果 ====================
        # 毁灭共鸣：连杀叠加伤害
        self.resonance_destruction_active = "resonance_destruction_kill_streak_damage" in effects
        if self.resonance_destruction_active:
            self.resonance_kill_streak = 0  # 连杀计数
            self.resonance_kill_streak_max_bonus = effects.get("resonance_destruction_kill_streak_damage", 0.30)
            self.resonance_kill_streak_timer = 0  # 连杀计时器（3秒内无击杀重置）
        
        # 守护共鸣：受伤后减伤递增
        self.resonance_guardian_active = "resonance_guardian_damage_taken_reduction" in effects
        if self.resonance_guardian_active:
            self.resonance_damage_timer = 0  # 受伤后计时
            self.resonance_damage_max_reduction = effects.get("resonance_guardian_damage_taken_reduction", 0.25)
        
        # 命运共鸣：拾取计数器
        self.resonance_destiny_active = "resonance_destiny_pickup_extra_choice" in effects
        if self.resonance_destiny_active:
            self.resonance_pickup_count = 0  # 拾取计数
            self.resonance_pickup_threshold = effects.get("resonance_destiny_pickup_extra_choice", 5)
            self.resonance_extra_choice_ready = False  # 下次选卡+1

    def update(self):
        # ========== 【星轨天赋阵】实时效果处理 ==========
        # 生命回复（每3秒回复一次）
        if self.talent_hp_regen_percent > 0:
            self.talent_hp_regen_timer += 1
            if self.talent_hp_regen_timer >= 180:  # 3秒 = 180帧
                self.talent_hp_regen_timer = 0
                heal_amount = int(self.max_hp * self.talent_hp_regen_percent)
                if self.hp < self.max_hp and heal_amount > 0:
                    self.hp = min(self.max_hp, self.hp + heal_amount)
                    FloatingText(self.rect.centerx, self.rect.top - 30, f"+{heal_amount}", (100, 255, 150))
        
        # 护盾回复（有护盾容量时缓慢回复）
        if self.talent_shield_regen > 0 and self.max_shield > 0:
            if self.shield < self.max_shield:
                # 基础回复速度0.1/帧，天赋加成后
                regen_rate = 0.1 * (1 + self.talent_shield_regen)
                self.shield = min(self.max_shield, self.shield + regen_rate)
        
        # 被击后移速加成计时器
        if self.talent_hit_speed_timer > 0:
            self.talent_hit_speed_timer -= 1
            if self.talent_hit_speed_timer <= 0:
                # 移速恢复正常
                self.speed = self.base_speed * (1 + self.talent_effects.get("move_speed", 0))
        
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
        # 【新】第四大招冷却更新（E键）
        if self.ult4_cooldown > 0: self.ult4_cooldown -= 1
        
        # 武器更新
        if self.switch_cooldown > 0: self.switch_cooldown -= 1
        for w in self.weapon_slots:
            if w: w.update()

        # 危害状态维护：毒与减速、束缚
        if self.hazard_slow_timer > 0:
            self.hazard_slow_timer -= 1
            if self.hazard_slow_timer == 0:
                self.hazard_slow_mult = 1.0
        if self.poison_dot_timer > 0:
            self.poison_dot_timer -= 1
            if self.poison_tick_cd > 0:
                self.poison_tick_cd -= 1
            if self.poison_tick_cd <= 0:
                if self.poison_dot_damage > 0:
                    self.hp -= self.poison_dot_damage
                    FloatingText(self.rect.centerx, self.rect.top - 10, f"-{int(self.poison_dot_damage)}", (80, 200, 120))
                self.poison_tick_cd = 20
        if self.grab_timer > 0:
            self.grab_timer -= 1
        else:
            self.grab_anchor = None
        if self.burn_timer > 0:
            self.burn_timer -= 1
            if self.burn_tick_cd > 0:
                self.burn_tick_cd -= 1
            if self.burn_tick_cd <= 0 and self.burn_damage > 0:
                self.hp -= self.burn_damage
                FloatingText(self.rect.centerx, self.rect.top - 18, f"-{int(self.burn_damage)}", ORANGE)
                self.burn_tick_cd = 15
        if self.freeze_timer > 0:
            self.freeze_timer -= 1
            self.is_frozen = True
        else:
            self.is_frozen = False
        if self.emp_timer > 0:
            self.emp_timer -= 1
            if self.emp_timer % 30 == 0:
                FloatingText(self.rect.centerx, self.rect.top - 30, "EMP", (120, 220, 255))
        if self.sonic_timer > 0:
            self.sonic_timer -= 1
        if self.armor_break_timer > 0:
            self.armor_break_timer -= 1
        if self.whiteout_timer > 0:
            self.whiteout_timer -= 1
            self.whiteout_intensity = min(1.0, self.whiteout_intensity + 0.02)
        else:
            self.whiteout_intensity = max(0.0, self.whiteout_intensity - 0.03)
        if self.parasite_timer > 0:
            self.parasite_timer -= 1
            if self.parasite_tick_cd > 0:
                self.parasite_tick_cd -= 1
            if self.parasite_tick_cd <= 0 and self.parasite_damage > 0:
                self.hp -= self.parasite_damage
                FloatingText(self.rect.centerx, self.rect.top - 26, f"-{int(self.parasite_damage)}", (140, 220, 140))
                self.parasite_tick_cd = 36
        else:
            self.parasite_damage = 0
        if self.mirror_timer > 0:
            self.mirror_timer -= 1
            if self.mirror_tick_cd > 0:
                if self.mirror_tick_timer <= 0:
                    self._trigger_mirror_feedback("pulse")
                    self.mirror_tick_timer = self.mirror_tick_cd
                else:
                    self.mirror_tick_timer -= 1
            if self.mirror_fire_cd > 0:
                self.mirror_fire_cd -= 1
        else:
            self.mirror_feedback_damage = 0
            self.mirror_tick_timer = 0
            self.mirror_fire_cd = 0
        if self.phase_lock_timer > 0:
            self.phase_lock_timer -= 1
            if self.phase_lock_pulse_cd > 0:
                if self.phase_lock_pulse_timer <= 0:
                    self._apply_phase_lock_pulse()
                else:
                    self.phase_lock_pulse_timer -= 1
        else:
            self.phase_lock_anchor = None
            self.phase_lock_displacement = 0.0
            self.phase_lock_pulse_timer = 0
        if self.spore_root_timer > 0:
            self.spore_root_timer -= 1
            if self.spore_root_tick_timer > 0:
                self.spore_root_tick_timer -= 1
            else:
                self._apply_spore_root_tick()
        else:
            self.spore_root_damage = 0
            self.spore_root_slow_mult = 1.0
            self.spore_root_tick_timer = 0
        if self.solar_burn_timer > 0:
            self.solar_burn_timer -= 1
            if self.solar_burn_tick_timer > 0:
                self.solar_burn_tick_timer -= 1
            else:
                self._apply_solar_burn_tick()
            self.whiteout_intensity = max(self.whiteout_intensity, 0.35)
        else:
            self.solar_burn_damage = 0
            self.solar_burn_tick_timer = 0

        # 移动逻辑 (支持按键重映射) - 改进版支持流畅对角线移动
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0
        
        # 获取按键管理器
        kb = get_key_binding_manager()
        
        # 使用按键管理器检测移动
        if kb.is_action_pressed(keys, "move_left"): dx -= self.speed
        if kb.is_action_pressed(keys, "move_right"): dx += self.speed
        if kb.is_action_pressed(keys, "move_up"): dy -= self.speed
        if kb.is_action_pressed(keys, "move_down"): dy += self.speed
        
        # 对角线移动标准化（避免对角线速度过快）
        if dx != 0 and dy != 0:
            move_length = math.sqrt(dx*dx + dy*dy)
            dx = dx / move_length * self.speed
            dy = dy / move_length * self.speed

        if self.is_frozen:
            dx = 0
            dy = 0

        if self.emp_timer > 0:
            dx *= 0.3
            dy *= 0.3

        # 危害减速
        if self.hazard_slow_mult < 1.0:
            dx *= self.hazard_slow_mult
            dy *= self.hazard_slow_mult
        if self.spore_root_timer > 0 and self.spore_root_slow_mult < 1.0:
            dx *= self.spore_root_slow_mult
            dy *= self.spore_root_slow_mult

        # 束缚/牵引：禁止自身移动并朝锚点被拉扯
        if self.grab_timer > 0 and self.grab_anchor:
            dx = 0
            dy = 0
            anchor_vec = pygame.Vector2(self.grab_anchor)
            delta = anchor_vec - pygame.Vector2(self.rect.center)
            if delta.length_squared() > 1:
                step = delta.normalize() * max(0.5, self.grab_pull)
                dx += step.x
                dy += step.y
        
        # ========== 【Goliath 瘟疫冲锋】检测双击 ==========
        if self.plane_id == "goliath":
            # 更新冷却
            if self.goliath_dash_cooldown > 0:
                self.goliath_dash_cooldown -= 1
            # 更新无敌帧
            if self.goliath_invincible > 0:
                self.goliath_invincible -= 1
            
            # 检测当前按下的方向键（使用按键管理器）
            current_key = None
            if kb.is_action_pressed(keys, "move_left"): current_key = 'left'
            elif kb.is_action_pressed(keys, "move_right"): current_key = 'right'
            elif kb.is_action_pressed(keys, "move_up"): current_key = 'up'
            elif kb.is_action_pressed(keys, "move_down"): current_key = 'down'
            
            # 双击检测逻辑：按下->释放->快速再按
            if current_key:
                if self.goliath_key_released:  # 如果之前已释放
                    if (current_key == self.goliath_last_tap_key and 
                        self.goliath_tap_timer > 0 and 
                        self.goliath_dash_cooldown <= 0):
                        # 双击成功！触发瘟疫冲锋
                        self._trigger_plague_dash(current_key)
                        self.goliath_last_tap_key = None
                        self.goliath_tap_timer = 0
                        self.goliath_dash_cooldown = 30  # 0.5秒冷却
                    else:
                        # 记录这次按下
                        self.goliath_last_tap_key = current_key
                        self.goliath_tap_timer = self.goliath_double_tap_window
                    self.goliath_key_released = False
            else:
                # 按键释放
                self.goliath_key_released = True
            
            # 倒计时
            if self.goliath_tap_timer > 0:
                self.goliath_tap_timer -= 1
            else:
                self.goliath_last_tap_key = None
        
        # 冲刺
        # Overdrive temporary buff handling
        if self.overdrive_timer > 0:
            self.overdrive_timer -= 1
            if self.overdrive_timer == 0:
                # Reset damage when overdrive ends
                self.damage = self.plane_data['damage']
        
        # 冲刺条件：需要足够的能量（>=80/100）且有移动方向（使用按键管理器）
        if kb.is_action_pressed(keys, "dash") and self.dash_energy >= 80 and (dx!=0 or dy!=0) and self.emp_timer <= 0 and not self.is_frozen:
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
        # 【混沌虫洞】维度裂缝状态维护
        self._update_wormhole_state()
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
        # 【星际海豚】过热系统状态维护
        self._update_sdmg_state()

        # 切换武器
        if self.switch_cooldown <= 0:
            if kb.is_action_pressed(keys, "weapon_prev"):
                self.current_slot = (self.current_slot - 1) % 3
                self.switch_cooldown = 60
                sound_mgr.play("select")
            elif kb.is_action_pressed(keys, "weapon_next"):
                self.current_slot = (self.current_slot + 1) % 3
                self.switch_cooldown = 60
                sound_mgr.play("select")
        
        # 【MAGNUS】法术轮盘切换（技能切换键）
        if self.plane_id == "magnus" and hasattr(self, 'magnus_initialized') and self.magnus_initialized:
            if not hasattr(self, 'magnus_switch_cooldown'):
                self.magnus_switch_cooldown = 0
            if self.magnus_switch_cooldown > 0:
                self.magnus_switch_cooldown -= 1
            if kb.is_action_pressed(keys, "skill_switch") and self.magnus_switch_cooldown <= 0:
                self.magnus_spell_mode = (self.magnus_spell_mode + 1) % 4
                self.magnus_switch_cooldown = 30  # 0.5秒冷却
                spell_name = self.magnus_spell_names[self.magnus_spell_mode]
                FloatingText(self.rect.centerx, self.rect.top - 30, f"⚡{spell_name}魔法", (255, 215, 100))
                sound_mgr.play("select")

        # 【HEAVY METAL】技能控制
        if self.plane_id == "heavymetal":
            from utils.bullets.heavymetal_bullets import PowerChordWave, StageDiveMeteor, DeathMetalSolo
            
            # 初始化技能冷却
            if not hasattr(self, 'heavymetal_skill_cooldowns'):
                self.heavymetal_skill_cooldowns = {'1': 0, '2': 0, '3': 0}
            
            # 更新冷却
            for key in self.heavymetal_skill_cooldowns:
                if self.heavymetal_skill_cooldowns[key] > 0:
                    self.heavymetal_skill_cooldowns[key] -= 1
            
            cx, cy = self.rect.centerx, self.rect.centery
            
            # 技能1 - 强力和弦 (冷却2秒)
            if kb.is_action_pressed(keys, "skill_1") and self.heavymetal_skill_cooldowns['1'] <= 0:
                PowerChordWave(cx, cy, damage=self.damage * 1.5)
                self.heavymetal_skill_cooldowns['1'] = 120
                FloatingText(cx, cy - 40, "🎸 POWER CHORD!", (255, 100, 0))
                sound_mgr.play("explosion")
            
            # 技能2 - 舞台俯冲 (冷却5秒)
            if kb.is_action_pressed(keys, "skill_2") and self.heavymetal_skill_cooldowns['2'] <= 0:
                StageDiveMeteor(cx, cy - 200, cx, cy + 100, damage=self.damage * 5)
                self.heavymetal_skill_cooldowns['2'] = 300
                FloatingText(cx, cy - 40, "🔥 STAGE DIVE!", (255, 50, 0))
                sound_mgr.play("explosion")
            
            # 技能3 - 死亡金属独奏 (冷却10秒)
            if kb.is_action_pressed(keys, "skill_3") and self.heavymetal_skill_cooldowns['3'] <= 0:
                DeathMetalSolo(cx, cy, damage_per_tick=self.damage // 6)
                self.heavymetal_skill_cooldowns['3'] = 600
                FloatingText(cx, cy - 40, "💀 DEATH METAL SOLO!", (148, 0, 211))
                sound_mgr.play("ult")

    def shoot(self):
        now = pygame.time.get_ticks()
        if self.emp_timer > 0:
            return
        effective_delay = self.shoot_delay
        if self.sonic_timer > 0:
            effective_delay = int(self.shoot_delay * 1.5)
        
        # 1. 主炮射击 (保持不变)
        if now - self.last_shot > effective_delay:
            self.last_shot = now
            self._handle_mirror_on_fire()
            self._fire_main_gun()
            sound_mgr.play("shoot")
            # 【统计】记录射击次数
            self.stats['shots_fired'] += 1
            
        # 【改动】副武器现在由僚机使用，玩家只使用主武器
        # 副武器逻辑已转移到 wingman.py 中的 Wingman 类

    def _handle_mirror_on_fire(self):
        if self.mirror_timer <= 0 or self.mirror_feedback_damage <= 0:
            return
        if self.mirror_fire_cd > 0:
            return
        self._trigger_mirror_feedback("fire")
        base_cd = self.mirror_tick_cd or 18
        self.mirror_fire_cd = max(6, base_cd // 2)
        self.mirror_tick_timer = max(self.mirror_tick_timer, base_cd // 3)

    def _trigger_mirror_feedback(self, reason="pulse"):
        if self.mirror_feedback_damage <= 0:
            return
        self.hp -= self.mirror_feedback_damage
        FloatingText(self.rect.centerx, self.rect.top - 18, "镜像反噬", (180, 200, 255))
        for _ in range(3):
            jitter = (random.randint(-8, 8), random.randint(-8, 8))
            Particle((self.rect.centerx + jitter[0], self.rect.centery + jitter[1]), (200, 220, 255))

    def _apply_phase_lock_pulse(self):
        anchor = self.phase_lock_anchor or (self.rect.centerx, self.rect.centery)
        displacement = float(self.phase_lock_displacement or 0)
        if displacement <= 0:
            self.phase_lock_pulse_timer = self.phase_lock_pulse_cd or 18
            return
        anchor_vec = pygame.Vector2(anchor)
        pos = pygame.Vector2(self.rect.center)
        delta = pos - anchor_vec
        if delta.length_squared() <= 1:
            delta = pygame.Vector2(0, -1)
        else:
            delta = delta.normalize()
        if self.phase_lock_invert:
            delta *= -1
        pos += delta * displacement
        self.rect.centerx = int(pos.x)
        self.rect.centery = int(pos.y)
        self.rect.clamp_ip(screen_rect)
        FloatingText(self.rect.centerx, self.rect.top - 22, "相位锁", (160, 210, 255))
        self.phase_lock_pulse_timer = self.phase_lock_pulse_cd or 18

    def _apply_spore_root_tick(self):
        tick = self.spore_root_damage
        self.spore_root_tick_timer = self.spore_root_tick_cd or 24
        if tick <= 0:
            return
        self.hp -= tick
        FloatingText(self.rect.centerx, self.rect.top - 20, f"-{int(tick)}", (120, 200, 150))
        Particle(self.rect.center, (90, 160, 110))

    def _apply_solar_burn_tick(self):
        tick = self.solar_burn_damage
        self.solar_burn_tick_timer = self.solar_burn_tick_cd or 12
        if tick <= 0:
            return
        self.hp -= tick
        FloatingText(self.rect.centerx, self.rect.top - 14, f"-{int(tick)}", (255, 200, 110))
        Particle(self.rect.center, (255, 180, 90))

    def _get_staradia_style(self):
        """获取Staradia涂装样式名称，从bullet_theme_id中提取"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            # 格式: "staradia_xxx" -> 提取 "xxx"
            # 例如: "staradia_void_rift" -> "void_rift"
            #       "staradia_prismatic" -> "prismatic"
            #       "staradia_void_empress" -> "void_empress"
            if theme_id.startswith("staradia_"):
                return theme_id[9:]  # 移除 "staradia_" 前缀
        return "default"

    def _get_duke_style(self):
        """获取Duke Fishron涂装样式名称，从bullet_theme_id中提取"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            # 格式: "duke_xxx" -> 提取 "xxx" 对应涂装
            # 例如: "duke_abyss_spear" -> "abyss"
            #       "duke_default" -> "default"
            if theme_id.startswith("duke_"):
                rest = theme_id[5:]  # 移除 "duke_" 前缀
                # 检查各种模式匹配
                if rest.startswith("abyss"):
                    return "abyss"
                elif rest.startswith("rage"):
                    return "rage"
                elif rest.startswith("storm"):
                    return "storm"
                elif rest.startswith("coral"):
                    return "coral"
                elif rest.startswith("void"):
                    return "void_sea"
                elif rest.startswith("tsunami"):
                    return "tsunami"
                elif rest.startswith("phantom"):
                    return "phantom"
                elif rest.startswith("blood"):
                    return "blood_moon"
                elif rest.startswith("tropical"):
                    return "tropical"
                elif rest.startswith("frost"):
                    return "frost"
                elif rest.startswith("golden") or rest.startswith("imperial"):
                    return "golden"
        return "default"

    def _get_slime_style(self):
        """获取Slime涂装样式名称，从bullet_theme_id中提取"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            # 格式: "slime_xxx_gel" -> 提取 "xxx"
            # 例如: "slime_cosmic_gel" -> "cosmic"
            #       "slime_void_gel" -> "void"
            #       "slime_star_gel" -> "default"
            if theme_id.startswith("slime_"):
                rest = theme_id[6:]  # 移除 "slime_" 前缀
                # 移除 "_gel" 后缀如果有
                if rest.endswith("_gel"):
                    rest = rest[:-4]
                # 检查各种涂装
                if rest == "star":
                    return "default"
                elif rest == "cosmic":
                    return "cosmic"
                elif rest == "void":
                    return "void"
                elif rest == "crystal":
                    return "crystal"
                elif rest == "toxic":
                    return "toxic"
                elif rest == "royal":
                    return "royal"
                elif rest == "blood":
                    return "blood"
                elif rest == "ice":
                    return "ice"
                elif rest == "flame":
                    return "flame"
                elif rest == "phantom":
                    return "phantom"
                elif rest == "rainbow":
                    return "rainbow"
                elif rest == "abyss":
                    return "abyss"
        return "default"

    def _get_oro_style(self):
        """获取Oro涂装样式名称，从bullet_theme_id中提取"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            # 格式: "oro_xxx_chain" -> 提取 "xxx"
            # 例如: "oro_crimson_chain" -> "crimson"
            #       "oro_void_chain" -> "void"
            #       "oro_default_chain" -> "default"
            if theme_id.startswith("oro_"):
                rest = theme_id[4:]  # 移除 "oro_" 前缀
                # 移除 "_chain" 后缀如果有
                if rest.endswith("_chain"):
                    rest = rest[:-6]
                # 检查各种涂装
                style_map = {
                    "default": "default", "crimson": "crimson", "void": "void",
                    "inferno": "inferno", "frost": "frost", "toxic": "toxic",
                    "royal": "royal", "phantom": "phantom", "blood": "blood",
                    "cosmic": "cosmic", "abyss": "abyss", "golden": "golden"
                }
                return style_map.get(rest, "default")
        return "default"

    def _get_yharon_style(self):
        """获取Yharon涂装样式名称，从bullet_theme_id中提取"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            # 格式: "yharon_xxx_flare" -> 提取 "xxx"
            # 例如: "yharon_inferno_flare" -> "inferno"
            #       "yharon_solar_flare" -> "solar"
            #       "yharon_default_flare" -> "default"
            if theme_id.startswith("yharon_"):
                rest = theme_id[7:]  # 移除 "yharon_" 前缀
                # 移除 "_flare" 后缀如果有
                if rest.endswith("_flare"):
                    rest = rest[:-6]
                # 检查各种涂装
                style_map = {
                    "default": "default", "inferno": "inferno", "solar": "solar",
                    "jungle": "jungle", "eclipse": "eclipse", "frost": "frost",
                    "storm": "storm", "bloodmoon": "bloodmoon", "void": "void",
                    "providence": "providence", "exo": "exo", "calamitas": "calamitas"
                }
                return style_map.get(rest, "default")
        return "default"

    def _get_providence_style(self):
        """获取Providence涂装样式名称"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            if theme_id.startswith("providence_"):
                # 涂装ID到样式的映射
                # "providence_xxx_shard" -> "providence_xxx"
                # 特殊情况: "providence_holy_shard" -> "providence_default"
                if theme_id == "providence_holy_shard":
                    return "providence_default"
                if theme_id.endswith("_shard"):
                    return theme_id[:-6]  # 去掉 "_shard"
                return theme_id
        # 从visual中获取model_style
        if hasattr(self, 'visual') and self.visual:
            model_style = self.visual.get('model_style', '')
            if model_style.startswith('providence_'):
                return model_style
        return "providence_default"

    def _get_goliath_style(self):
        """获取Goliath涂装样式名称"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            if theme_id.startswith("goliath_"):
                # "goliath_xxx_missile" -> "goliath_xxx"
                if theme_id == "goliath_plague_missile":
                    return "goliath_default"
                if theme_id.endswith("_missile"):
                    return theme_id[:-8]  # 去掉 "_missile"
                return theme_id
        # 从visual中获取model_style
        if hasattr(self, 'visual') and self.visual:
            model_style = self.visual.get('model_style', '')
            if model_style.startswith('goliath_'):
                return model_style
        return "goliath_default"

    def _get_sepulcher_style(self):
        """获取Sepulcher涂装样式名称"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            if theme_id.startswith("sepulcher_"):
                if theme_id == "sepulcher_brimstone_bolt":
                    return "sepulcher_default"
                if theme_id.endswith("_bolt"):
                    return theme_id[:-5]
                return theme_id
        if hasattr(self, 'visual') and self.visual:
            model_style = self.visual.get('model_style', '')
            if model_style.startswith('sepulcher_'):
                return model_style
        return "sepulcher_default"

    def _get_galaxia_style(self):
        """获取Galaxia涂装样式名称"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            if theme_id.startswith("galaxia_"):
                # 移除后缀（如果有）
                clean_id = theme_id.replace("galaxia_", "")
                if clean_id.endswith("_star") or clean_id.endswith("_slash"):
                    return clean_id.rsplit("_", 1)[0]
                return clean_id
        if hasattr(self, 'visual') and self.visual:
            model_style = self.visual.get('model_style', '')
            if model_style.startswith('galaxia_'):
                return model_style.replace("galaxia_", "")
        return "default"

    def _get_magnus_style(self):
        """获取Magnus涂装样式名称"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            if theme_id.startswith("magnus_"):
                return theme_id  # 直接返回完整样式名
        if hasattr(self, 'visual') and self.visual:
            model_style = self.visual.get('model_style', '')
            if model_style.startswith('magnus_'):
                return model_style
        return "magnus_default"

    def _get_heavymetal_style(self):
        """获取HeavyMetal涂装样式名称"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            if theme_id.startswith("heavymetal_"):
                return theme_id
        if hasattr(self, 'visual') and self.visual:
            model_style = self.visual.get('model_style', '')
            if model_style.startswith('heavymetal_'):
                return model_style
        return "heavymetal_default"

    def _get_scarlet_style(self):
        """获取Scarlet涂装样式名称"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            if theme_id.startswith("scarlet_"):
                return theme_id
        if hasattr(self, 'visual') and self.visual:
            model_style = self.visual.get('model_style', '')
            if model_style.startswith('scarlet_'):
                return model_style
        return "scarlet_default"

    def _get_zenith_style(self):
        """获取Zenith涂装样式名称"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            if theme_id.startswith("zenith_"):
                return theme_id
        if hasattr(self, 'visual') and self.visual:
            model_style = self.visual.get('model_style', '')
            if model_style.startswith('zenith_'):
                return model_style
        return "zenith_default"

    def _get_viscerator_style(self):
        """获取Viscerator涂装样式名称"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            if theme_id.startswith("viscerator_"):
                return theme_id
        if hasattr(self, 'visual') and self.visual:
            model_style = self.visual.get('model_style', '')
            if model_style.startswith('viscerator_'):
                return model_style
        return "viscerator_default"

    def _get_crusher_style(self):
        """获取Crusher涂装样式名称"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            if theme_id.startswith("crusher_"):
                return theme_id
        if hasattr(self, 'visual') and self.visual:
            model_style = self.visual.get('model_style', '')
            if model_style.startswith('crusher_'):
                return model_style
        return "crusher_default"

    def _get_sdmg_style(self):
        """获取SDMG涂装样式名称"""
        if hasattr(self, 'bullet_theme_id') and self.bullet_theme_id:
            theme_id = self.bullet_theme_id
            if theme_id.startswith("sdmg_"):
                return theme_id
        if hasattr(self, 'visual') and self.visual:
            model_style = self.visual.get('model_style', '')
            if model_style.startswith('sdmg_'):
                return model_style
        return "sdmg_default"


    def _init_sepulcher_systems(self):
        """初始化Sepulcher的特殊系统"""
        from utils.bullets.sepulcher_bullets import SkullTail, CalamityAura, MagicHalo
        style = self._get_sepulcher_style()
        self.sepulcher_skull_tail = SkullTail(self, style)
        self.sepulcher_aura = CalamityAura(self, style)
        self.sepulcher_halo = MagicHalo(self, style)

    def _update_sepulcher_systems(self):
        """更新Sepulcher的特殊系统"""
        # 更新暴怒计时器
        if self.sepulcher_fury_active:
            self.sepulcher_fury_timer -= 1
            if self.sepulcher_fury_timer <= 0:
                self.sepulcher_fury_active = False
                self.sepulcher_fury = 0
        
        # 更新骷髅尾巴
        if self.sepulcher_skull_tail:
            self.sepulcher_skull_tail.update()
        
        # 更新光环
        if self.sepulcher_aura:
            self.sepulcher_aura.update()
        
        # 更新魔法阵（随暴怒值旋转加速）
        if self.sepulcher_halo:
            fury_ratio = self.sepulcher_fury / self.sepulcher_max_fury
            self.sepulcher_halo.update(fury_ratio)

    def _add_sepulcher_fury(self, amount):
        """增加暴怒值（擦弹时调用）"""
        if self.sepulcher_fury_active:
            return  # 暴怒激活时不再积累
        
        self.sepulcher_fury = min(self.sepulcher_max_fury, self.sepulcher_fury + amount)
        
        # 暴怒值满，激活暴怒状态
        if self.sepulcher_fury >= self.sepulcher_max_fury:
            self.sepulcher_fury_active = True
            self.sepulcher_fury_timer = 300  # 5秒
            FloatingText(self.rect.centerx, self.rect.top - 30, "💀暴怒激活!", (220, 20, 60))
        
        # 擦弹闪烁效果
        if self.sepulcher_aura:
            self.sepulcher_aura.flash()

    def _render_sepulcher_effects(self, surface):
        """渲染Sepulcher的特效"""
        # 渲染骷髅尾巴
        if self.sepulcher_skull_tail:
            self.sepulcher_skull_tail.render(surface)
        
        # 渲染灾厄力场
        if self.sepulcher_aura:
            self.sepulcher_aura.render(surface)
        
        # 渲染魔法阵光环
        if self.sepulcher_halo:
            self.sepulcher_halo.render(surface)

    def _trigger_plague_dash(self, direction):
        """【Goliath 瘟疫冲锋】双击触发的高机动动作"""
        from utils.bullets.goliath_bullets import PlagueCloud
        import random
        
        style = self._get_goliath_style()
        theme = {}
        try:
            from utils.planes.skins_goliath import get_goliath_theme
            theme = get_goliath_theme(style)
        except:
            theme = {"toxic": (57, 255, 20), "smoke": (50, 60, 40)}
        
        # 在原地生成一团毒雾（陷阱）
        for _ in range(3):
            cloud_x = self.rect.centerx + random.randint(-30, 30)
            cloud_y = self.rect.centery + random.randint(-20, 20)
            PlagueCloud(cloud_x, cloud_y, self.damage * 0.15, owner=self, style=style, duration=180)
        
        # 产生毒雾视觉效果
        from sprites import Particle
        for _ in range(20):
            Particle(self.rect.center, theme.get("toxic", (57, 255, 20)), mode='spark')
        
        # 计算瞬移方向
        dash_dist = 120
        if direction == 'left': self.rect.x -= dash_dist
        elif direction == 'right': self.rect.x += dash_dist
        elif direction == 'up': self.rect.y -= dash_dist
        elif direction == 'down': self.rect.y += dash_dist
        
        # 边界限制
        self.rect.clamp_ip(screen_rect)
        
        # 扣除能量
        self.dash_energy = max(0, self.dash_energy - 30)
        
        # 设置无敌帧（15帧约0.25秒）
        self.goliath_invincible = 15
        
        # 音效
        sound_mgr.play("dash")

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
        
        # ========== 17. 混沌虫洞 - 维度传送射击 ==========
        elif pid == "wormhole":
            # 虫洞特性：螺旋式传送弹幕，击中敌人会从其他敌人背后传送出子弹
            rift_energy = getattr(self, 'rift_energy', 0)
            max_rift = getattr(self, 'max_rift_energy', 100)
            rift_ratio = rift_energy / max(1, max_rift)
            
            # 每次射击积累裂缝能量
            if hasattr(self, 'gain_rift_energy'):
                self.gain_rift_energy(8)  # 约12-13次射击满能量
            
            # 当裂缝能量较高时，发射增强弹
            is_enhanced = rift_ratio > 0.7
            
            # 螺旋式发射（模拟维度扭曲）
            for i in range(cnt):
                # 计算螺旋偏移
                spiral_angle = (i * 60 + pygame.time.get_ticks() / 30) % 360
                spiral_radius = 30
                offset_x = int(spiral_radius * math.cos(spiral_angle * 3.14159 / 180))
                offset_y = int(spiral_radius * math.sin(spiral_angle * 3.14159 / 180) * 0.3)  # 椭圆螺旋
                
                bullet = Bullet(self.rect.centerx + offset_x, self.rect.top + offset_y,
                       color=(180, 0, 255) if not is_enhanced else (255, 0, 255), 
                       b_type="wormhole", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                bullet.is_wormhole_bullet = True
                bullet.wormhole_enhanced = is_enhanced
                # 标记来源玩家，用于虫洞传送
                bullet.source_player = self
                # 添加螺旋运动属性
                bullet.spiral_phase = spiral_angle
                bullet.spiral_amplitude = 20 if not is_enhanced else 30  # 螺旋幅度
                
                # 增强弹：更快，更强，螺旋更大
                if is_enhanced:
                    bullet.speed = -16
                    bullet.damage_mult = 1.5
            
            # 高能量时发射六芒星裂缝波（环形扩散）
            if rift_ratio > 0.9:
                # 六个方向形成虫洞环
                for i in range(6):
                    angle = i * 60 - 90  # -90度让正上方也有一发
                    bullet = Bullet(self.rect.centerx, self.rect.top, angle=angle,
                           color=(0, 255, 180), b_type="wormhole", piercing=self.piercing + 2, homing=homing_value, bullet_theme=self.bullet_theme)
                    bullet.is_wormhole_bullet = True
                    bullet.is_rift_wave = True
                    bullet.source_player = self
                    bullet.speed = -13  # 环形波速度适中
        
        # ========== 18. 永恒时计 - 时间回溯三连射 ==========
        elif pid == "chronos":
            # 时间特性：发射后会产生时间回声，形成三重时间线攻击（过去-现在-未来）
            time_energy = getattr(self, 'chronos_time_energy', 0)
            max_time = getattr(self, 'max_time_energy', 100)
            time_ratio = time_energy / max(1, max_time)
            echo_stacks = getattr(self, 'chronos_echo_stacks', 0)
            
            # 回声强化：每层回声增加额外子弹
            extra_bullets = min(2, echo_stacks // 3)  # 每3层回声+1发
            total_cnt = cnt + extra_bullets
            
            for i in range(total_cnt):
                offset_x = (i - (total_cnt-1)/2) * 18
                
                # 主时间线子弹（蓝色）
                main_bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=(100, 220, 255), b_type="chrono", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                main_bullet.is_chronos_bullet = True
                main_bullet.time_phase = 0  # 主时间线
                
                # 时间能量高时产生回声子弹（过去和未来）
                if time_ratio > 0.4:
                    # 过去回声（淡蓝色，稍微延迟发射）
                    past_bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                           color=(150, 200, 255), b_type="chrono", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                    past_bullet.is_chronos_bullet = True
                    past_bullet.time_phase = -1  # 过去
                    past_bullet.spawn_delay = 5  # 5帧后出现
                    past_bullet.rect.y += 30  # 稍微靠后
                
                if time_ratio > 0.7:
                    # 未来回声（金色，提前发射）
                    future_bullet = Bullet(self.rect.centerx + offset_x, self.rect.top - 30,
                           color=(255, 200, 100), b_type="chrono", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                    future_bullet.is_chronos_bullet = True
                    future_bullet.time_phase = 1  # 未来
                    future_bullet.speed = -18  # 更快
            
            # 高时间能量时额外发射时钟指针弹幕
            if time_ratio > 0.9:
                # 12个方向的时钟刻度弹（只发射4个主方向）
                for hour in range(0, 12, 3):  # 4个主方向（12点、3点、6点、9点）
                    angle = hour * 30 - 90  # 转换为角度
                    bullet = Bullet(self.rect.centerx, self.rect.top, angle=angle,
                           color=(200, 255, 255), b_type="chrono", piercing=self.piercing + 1, homing=homing_value, bullet_theme=self.bullet_theme)
                    bullet.is_chronos_bullet = True
                    bullet.is_clock_hand = True
                    bullet.speed = -14
        
        # ========== 19. 幻镜分身 - 镜像矩阵射击 ==========
        elif pid == "mirage":
            # 镜像特性：召唤分身协同射击，分身复制主体攻击形成弹幕矩阵
            mirror_count = getattr(self, 'mirage_mirror_count', 0)  # 当前分身数量
            mirror_sync = getattr(self, 'mirage_sync_level', 0)  # 同步等级
            
            # 主体射击（三角棱镜弹）
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 16
                
                # 主弹（紫色棱镜）
                main_bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=(200, 150, 255), b_type="mirror", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                main_bullet.is_mirage_bullet = True
                main_bullet.is_main_shot = True
            
            # 分身射击（每个分身复制一份主体攻击）
            mirrors = getattr(self, 'active_mirrors', [])
            for mirror_i, mirror_pos in enumerate(mirrors):
                if mirror_pos:
                    # 分身子弹（半透明，伤害略低）
                    for i in range(cnt):
                        offset_x = (i - (cnt-1)/2) * 16
                        mirror_bullet = Bullet(mirror_pos[0] + offset_x, mirror_pos[1] - 20,
                               color=(220, 180, 255), b_type="mirror", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                        mirror_bullet.is_mirage_bullet = True
                        mirror_bullet.is_mirror_shot = True
                        mirror_bullet.damage_mult = 0.5 + mirror_sync * 0.1  # 同步等级越高，分身伤害越高
                        mirror_bullet.alpha = 180  # 半透明
            
            # 高同步时发射折射光线（三个方向）
            if mirror_sync >= 3:
                for refract_angle in [-20, 0, 20]:
                    refract_bullet = Bullet(self.rect.centerx, self.rect.top, angle=refract_angle,
                           color=(255, 200, 255), b_type="mirror", piercing=self.piercing + 1, homing=homing_value, bullet_theme=self.bullet_theme)
                    refract_bullet.is_mirage_bullet = True
                    refract_bullet.is_refract_ray = True
                    refract_bullet.speed = -16
        
        # ========== 20. 命运赌徒 - 随机效果射击 ==========
        elif pid == "gambit":
            # 赌徒特性：每次射击随机触发不同效果，可能大赚或小亏
            luck_meter = getattr(self, 'gambit_luck_meter', 50)  # 运气值（0-100）
            combo_streak = getattr(self, 'gambit_combo_streak', 0)  # 连击数
            
            # 掷骰决定本次射击效果
            roll = random.randint(1, 100)
            
            # 运气值影响掷骰结果
            adjusted_roll = roll + (luck_meter - 50) // 5  # 运气高时更容易触发好效果
            
            # 根据结果决定效果
            if adjusted_roll >= 95:  # 大奖！暴击连锁
                # 发射5发高伤害金色子弹
                for i in range(5):
                    angle = (i - 2) * 15
                    jackpot_bullet = Bullet(self.rect.centerx, self.rect.top, angle=angle,
                           color=(255, 215, 0), b_type="card", piercing=self.piercing + 2, homing=homing_value, bullet_theme=self.bullet_theme)
                    jackpot_bullet.is_gambit_bullet = True
                    jackpot_bullet.is_jackpot = True
                    jackpot_bullet.damage_mult = 3.0  # 三倍伤害
                    jackpot_bullet.speed = -18
                # 显示特效
                if hasattr(self, 'show_gambit_effect'):
                    self.show_gambit_effect("JACKPOT!", (255, 215, 0))
            
            elif adjusted_roll >= 75:  # 好运：双倍子弹
                for i in range(cnt * 2):
                    offset_x = (i - (cnt-1)) * 12
                    lucky_bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                           color=(255, 200, 50), b_type="card", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                    lucky_bullet.is_gambit_bullet = True
                    lucky_bullet.damage_mult = 1.5
            
            elif adjusted_roll >= 40:  # 普通：正常射击
                for i in range(cnt):
                    offset_x = (i - (cnt-1)/2) * 18
                    normal_bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                           color=(255, 215, 0), b_type="card", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                    normal_bullet.is_gambit_bullet = True
            
            elif adjusted_roll >= 15:  # 小霉：子弹减半但追踪
                half_cnt = max(1, cnt // 2)
                for i in range(half_cnt):
                    offset_x = (i - (half_cnt-1)/2) * 18
                    tracking_bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                           color=(200, 150, 50), b_type="card", piercing=self.piercing, homing=min(1.0, homing_value + 0.5), bullet_theme=self.bullet_theme)
                    tracking_bullet.is_gambit_bullet = True
            
            else:  # 霉运：只发一发但下次必暴击
                single_bullet = Bullet(self.rect.centerx, self.rect.top,
                       color=(150, 100, 50), b_type="card", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                single_bullet.is_gambit_bullet = True
                # 设置下次必定暴击
                self.gambit_next_crit = True
            
            # 连击机制：连续好结果增加运气
            if adjusted_roll >= 75:
                self.gambit_combo_streak = combo_streak + 1
                self.gambit_luck_meter = min(100, luck_meter + 5)
            elif adjusted_roll < 40:
                self.gambit_combo_streak = 0
                self.gambit_luck_meter = max(0, luck_meter - 3)
        
        # ========== 21. 牵线木偶师 - 傀儡标记射击 ==========
        elif pid == "puppeteer":
            # 发射傀儡丝线子弹，命中敌人叠加傀儡标记
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 18
                string_bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=(180, 100, 150), b_type="puppet_string", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                string_bullet.is_puppet_string = True
                string_bullet.puppet_stack_power = 1  # 每次命中叠加1层标记
                
            # 检查并更新傀儡状态
            if not hasattr(self, 'puppet_enemies'):
                self.puppet_enemies = {}  # {enemy: {"stacks": int, "controlled": bool}}
            
            # 控制的敌人跟随玩家移动方向
            for enemy, data in list(self.puppet_enemies.items()):
                if not enemy.alive():
                    del self.puppet_enemies[enemy]
                    continue
                if data.get("controlled"):
                    # 傀儡敌人跟随玩家方向移动，并对其他敌人造成接触伤害
                    enemy.puppet_controlled = True
                    enemy.speedx = getattr(self, 'last_move_x', 0) * 0.5
                    enemy.speedy = getattr(self, 'last_move_y', 0) * 0.5
        
        # ========== 22. 末日瘟神 - 感染子弹 ==========
        elif pid == "pandemic":
            # 发射病毒感染子弹
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 18
                virus_bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=(100, 200, 80), b_type="virus", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                virus_bullet.is_virus_bullet = True
                virus_bullet.infection_power = 1  # 感染等级
            
            # 初始化感染系统
            if not hasattr(self, 'infected_enemies'):
                self.infected_enemies = {}  # {enemy: {"level": int, "damage_stack": float, "timer": int}}
                self.pandemic_mutation_level = 0  # 变异等级
                self.pandemic_spread_count = 0  # 传播次数
            
            # 处理感染和变异
            self._update_pandemic_infections()
        
        # ========== 23. 终末神兵·奥米茄 - 七属性融合射击 ==========
        elif pid == "omega":
            # 终极机体Omega：七属性循环 + 融合终极弹
            # 初始化Omega专属属性
            if not hasattr(self, 'omega_element_index'):
                self.omega_element_index = 0  # 当前属性索引
                self.omega_fusion_charge = 0  # 融合能量
                self.omega_fusion_max = 100
                self.omega_elements = [
                    {"name": "火", "color": (255, 80, 30), "effect": "burn"},
                    {"name": "冰", "color": (100, 200, 255), "effect": "freeze"},
                    {"name": "雷", "color": (255, 255, 100), "effect": "chain"},
                    {"name": "毒", "color": (150, 255, 80), "effect": "poison"},
                    {"name": "光", "color": (255, 255, 255), "effect": "holy"},
                    {"name": "暗", "color": (150, 50, 200), "effect": "void"},
                    {"name": "元", "color": (255, 200, 100), "effect": "arcane"},
                ]
            
            current_element = self.omega_elements[self.omega_element_index]
            self.omega_fusion_charge += 5  # 每次射击积累融合能量
            
            # 当融合能量满时，发射七属性融合终极弹
            if self.omega_fusion_charge >= self.omega_fusion_max:
                self.omega_fusion_charge = 0
                FloatingText(self.rect.centerx, self.rect.top - 40, "◆七曜融合◆", (255, 220, 180))
                
                # 七属性同时发射！形成七芒星阵
                for i, elem in enumerate(self.omega_elements):
                    angle = i * (360 / 7) - 90
                    fusion_bullet = Bullet(self.rect.centerx, self.rect.top, angle=angle,
                           color=elem["color"], b_type="omega_fusion", piercing=self.piercing + 3, homing=homing_value, bullet_theme=self.bullet_theme)
                    fusion_bullet.is_omega_fusion = True
                    fusion_bullet.omega_element = elem["effect"]
                    fusion_bullet.damage_mult = 2.5
                    fusion_bullet.speed = -14
                
                # 中心发射超大融合弹
                center_bullet = Bullet(self.rect.centerx, self.rect.top, angle=0,
                       color=(255, 255, 255), b_type="omega_fusion", piercing=self.piercing + 10, homing=homing_value, bullet_theme=self.bullet_theme)
                center_bullet.is_omega_ultimate_bullet = True
                center_bullet.damage_mult = 5.0
                center_bullet.speed = -10
                
                # 特效
                for _ in range(15):
                    Particle(self.rect.center, random.choice([e["color"] for e in self.omega_elements]))
            else:
                # 普通射击：当前属性子弹 + 双翼辅助弹
                for i in range(cnt):
                    offset_x = (i - (cnt-1)/2) * 20
                    main_bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                           color=current_element["color"], b_type="omega_fusion", piercing=self.piercing + 1, homing=homing_value, bullet_theme=self.bullet_theme)
                    main_bullet.is_omega_element = True
                    main_bullet.omega_element = current_element["effect"]
                
                # 两侧辅助弹（下一属性预兆）
                next_element = self.omega_elements[(self.omega_element_index + 1) % 7]
                for side in [-1, 1]:
                    side_bullet = Bullet(self.rect.centerx + side * 35, self.rect.top + 10, angle=side * 8,
                           color=next_element["color"], b_type="omega_fusion", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                    side_bullet.is_omega_element = True
                    side_bullet.omega_element = next_element["effect"]
                    side_bullet.damage_mult = 0.6
            
            # 切换到下一个属性
            self.omega_element_index = (self.omega_element_index + 1) % 7
        
        # ========== 24. 创世之翼·起源 - 创造与毁灭双形态 ==========
        elif pid == "genesis":
            # 终极机体Genesis：创造/毁灭双形态切换
            if not hasattr(self, 'genesis_form'):
                self.genesis_form = "creation"  # creation 或 destruction
                self.genesis_form_energy = 0
                self.genesis_max_energy = 80
                self.genesis_big_bang_charge = 0  # 大爆炸能量
            
            self.genesis_form_energy += 3
            self.genesis_big_bang_charge += 2
            
            if self.genesis_form == "creation":
                # 创造形态：生成光球护盾，治疗型子弹
                creation_gold = (255, 220, 100)
                creation_white = (255, 255, 220)
                
                # 主弹：星尘光矢（扇形展开）
                for i in range(cnt + 2):
                    angle = -20 + i * (40 / (cnt + 1))
                    star_bullet = Bullet(self.rect.centerx, self.rect.top, angle=angle,
                           color=creation_gold, b_type="genesis_star", piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)
                    star_bullet.is_genesis_creation = True
                    star_bullet.creation_heal = True  # 击杀有概率恢复HP
                
                # 光环护卫弹（围绕玩家的光球）
                for i in range(3):
                    orbit_angle = (pygame.time.get_ticks() / 10 + i * 120) % 360
                    ox = self.rect.centerx + math.cos(orbit_angle * 0.01745) * 45
                    oy = self.rect.centery + math.sin(orbit_angle * 0.01745) * 45
                    orbit_bullet = Bullet(ox, oy, angle=random.uniform(-180, 180),
                           color=creation_white, b_type="genesis_star", piercing=0, homing=0.5, bullet_theme=self.bullet_theme)
                    orbit_bullet.is_genesis_orb = True
                    orbit_bullet.speed = -8
                    orbit_bullet.damage_mult = 0.5
                
            else:
                # 毁灭形态：高伤害范围爆炸弹
                destruct_red = (255, 50, 80)
                destruct_purple = (200, 50, 150)
                
                # 主弹：毁灭炮（直线高伤）
                for i in range(max(1, cnt - 1)):
                    offset_x = (i - (cnt-2)/2) * 25
                    destroy_bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                           color=destruct_red, b_type="genesis_star", piercing=self.piercing + 3, homing=homing_value, bullet_theme=self.bullet_theme)
                    destroy_bullet.is_genesis_destruction = True
                    destroy_bullet.damage_mult = 1.8
                    destroy_bullet.speed = -16
                
                # 虚空裂隙弹（追踪爆炸）
                void_bullet = Bullet(self.rect.centerx, self.rect.top - 5,
                       color=destruct_purple, b_type="genesis_star", piercing=self.piercing + 2, homing=min(1.0, homing_value + 0.6), bullet_theme=self.bullet_theme)
                void_bullet.is_genesis_void = True
                void_bullet.explode_on_hit = True
                void_bullet.damage_mult = 1.5
            
            # 能量满时自动切换形态 + 发射形态转换波
            if self.genesis_form_energy >= self.genesis_max_energy:
                self.genesis_form_energy = 0
                old_form = self.genesis_form
                self.genesis_form = "destruction" if old_form == "creation" else "creation"
                
                form_name = "毁灭" if self.genesis_form == "destruction" else "创造"
                form_color = (255, 80, 100) if self.genesis_form == "destruction" else (255, 220, 100)
                FloatingText(self.rect.centerx, self.rect.top - 35, f"◆{form_name}形态◆", form_color)
                
                # 形态转换波（环形爆发）
                for i in range(12):
                    wave_angle = i * 30
                    wave_bullet = Bullet(self.rect.centerx, self.rect.centery, angle=wave_angle,
                           color=form_color, b_type="genesis_star", piercing=self.piercing + 1, homing=0, bullet_theme=self.bullet_theme)
                    wave_bullet.is_genesis_wave = True
                    wave_bullet.damage_mult = 1.2
                    wave_bullet.speed = -12
                
                for _ in range(12):
                    Particle(self.rect.center, form_color)
            
            # 大爆炸能量满时触发小型创世爆发
            if self.genesis_big_bang_charge >= 200:
                self.genesis_big_bang_charge = 0
                FloatingText(self.rect.centerx, self.rect.top - 50, "★创世之光★", (255, 255, 200))
                # 发射24方向星爆
                for i in range(24):
                    burst_angle = i * 15
                    burst_color = (255, 220, 100) if i % 2 == 0 else (255, 100, 150)
                    burst_bullet = Bullet(self.rect.centerx, self.rect.centery, angle=burst_angle,
                           color=burst_color, b_type="genesis_star", piercing=self.piercing + 2, homing=0.3, bullet_theme=self.bullet_theme)
                    burst_bullet.is_genesis_burst = True
                    burst_bullet.damage_mult = 2.0
                    burst_bullet.speed = -15
                for _ in range(20):
                    Particle(self.rect.center, random.choice([(255, 220, 100), (255, 100, 150), (255, 255, 255)]))
        
        # ========== 25. 至尊·世界的真相 - 真言之眼揭示一切 ==========
        elif pid == "truth":
            # 终极机体Truth：真言之眼系统 - 标记敌人"真相"状态，暴露弱点
            TRUTH_WHITE = (255, 255, 255)
            TRUTH_BLACK = (20, 20, 30)
            TRUTH_GOLD = (255, 215, 0)
            
            # 初始化Truth专属属性
            if not hasattr(self, 'truth_eye_charge'):
                self.truth_eye_charge = 0  # 真言之眼能量
                self.truth_eye_max = 100
                self.truth_marked_enemies = {}  # 被标记的敌人
                self.truth_revelation_mode = False  # 真理显现模式
                self.truth_yin_yang_balance = 0  # 阴阳平衡值 (-100~100)
            
            self.truth_eye_charge += 4
            
            # 根据阴阳平衡决定子弹属性
            if self.truth_yin_yang_balance > 30:
                # 阳盛：白色光明弹，高伤害
                bullet_color = TRUTH_WHITE
                bullet_effect = "yang"
                damage_mult = 1.5
                self.truth_yin_yang_balance -= 8
            elif self.truth_yin_yang_balance < -30:
                # 阴盛：黑色暗影弹，追踪+减速
                bullet_color = TRUTH_BLACK
                bullet_effect = "yin"
                damage_mult = 1.0
                self.truth_yin_yang_balance += 8
            else:
                # 平衡：金色真理弹，标记敌人
                bullet_color = TRUTH_GOLD
                bullet_effect = "balance"
                damage_mult = 1.2
            
            # 主弹：真言之矢
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 18
                main_bullet = Bullet(self.rect.centerx + offset_x, self.rect.top,
                       color=bullet_color, b_type="truth_revelation", 
                       piercing=self.piercing + 1, homing=homing_value + 0.2, bullet_theme=self.bullet_theme)
                main_bullet.is_truth_bullet = True
                main_bullet.truth_effect = bullet_effect
                main_bullet.damage_mult = damage_mult
                
                # 平衡弹有标记敌人的能力
                if bullet_effect == "balance":
                    main_bullet.can_mark_truth = True
            
            # 两侧辅助弹：阴阳双弹
            yin_bullet = Bullet(self.rect.centerx - 40, self.rect.top + 5, angle=-15,
                   color=TRUTH_BLACK, b_type="truth_revelation", 
                   piercing=self.piercing, homing=homing_value + 0.3, bullet_theme=self.bullet_theme)
            yin_bullet.is_truth_yin = True
            yin_bullet.damage_mult = 0.7
            yin_bullet.speed = -12
            
            yang_bullet = Bullet(self.rect.centerx + 40, self.rect.top + 5, angle=15,
                   color=TRUTH_WHITE, b_type="truth_revelation", 
                   piercing=self.piercing, homing=homing_value + 0.3, bullet_theme=self.bullet_theme)
            yang_bullet.is_truth_yang = True
            yang_bullet.damage_mult = 0.7
            yang_bullet.speed = -12
            
            # 阴阳平衡随机波动
            self.truth_yin_yang_balance += random.randint(-5, 5)
            self.truth_yin_yang_balance = max(-100, min(100, self.truth_yin_yang_balance))
            
            # 真言之眼满能量：触发真理揭示
            if self.truth_eye_charge >= self.truth_eye_max:
                self.truth_eye_charge = 0
                self.truth_revelation_mode = True
                FloatingText(self.rect.centerx, self.rect.top - 45, "◆真言开眼◆", TRUTH_GOLD)
                
                # 全屏扫描：标记所有敌人
                for m in mobs:
                    self.truth_marked_enemies[m] = {"timer": 300, "weakness": 1.5}
                    FloatingText(m.rect.centerx, m.rect.top - 15, "☉真相☉", TRUTH_GOLD)
                
                # 发射真理之眼（大型追踪弹）
                eye_bullet = Bullet(self.rect.centerx, self.rect.top - 10,
                       color=TRUTH_GOLD, b_type="truth_revelation", 
                       piercing=self.piercing + 8, homing=0.8, bullet_theme=self.bullet_theme)
                eye_bullet.is_truth_eye = True
                eye_bullet.damage_mult = 4.0
                eye_bullet.speed = -8
                
                # 八方真言弹
                for i in range(8):
                    reveal_angle = i * 45
                    reveal_bullet = Bullet(self.rect.centerx, self.rect.centery, angle=reveal_angle,
                           color=TRUTH_GOLD, b_type="truth_revelation", 
                           piercing=self.piercing + 2, homing=0.4, bullet_theme=self.bullet_theme)
                    reveal_bullet.is_truth_revelation = True
                    reveal_bullet.damage_mult = 2.0
                    reveal_bullet.speed = -14
                
                for _ in range(16):
                    Particle(self.rect.center, random.choice([TRUTH_GOLD, TRUTH_WHITE, TRUTH_BLACK]))
            
            # 更新被标记敌人
            for enemy, data in list(self.truth_marked_enemies.items()):
                if not enemy.alive():
                    del self.truth_marked_enemies[enemy]
                    continue
                data["timer"] -= 1
                if data["timer"] <= 0:
                    del self.truth_marked_enemies[enemy]
        
        # ========== 26. 修罗·斩龙者 - 六道剑气轮斩 ==========
        elif pid == "asura":
            # 初始化剑气轮转角度
            if not hasattr(self, 'asura_spin_angle'):
                self.asura_spin_angle = 0
            
            base_damage = self.damage * 1.0
            cx, cy = self.rect.centerx, self.rect.top
            
            # 6道剑气，轮转发射（每次射击转动60度）
            for i in range(6):
                angle = self.asura_spin_angle + i * 60
                rad = math.radians(angle - 90)
                offset_x = math.cos(rad) * 20
                offset_y = math.sin(rad) * 10
                # 只发射前方180度范围内的剑气
                if -90 <= (angle % 360 - 180) <= 90 or angle % 360 < 90 or angle % 360 > 270:
                    fire_angle = (angle % 360) - 180  # 转换为发射角度
                    if -60 <= fire_angle <= 60:  # 前方120度扇形
                        SwordQi(cx + offset_x, cy + offset_y, 
                               color=(255, 80 + i*20, 80), 
                               damage=base_damage, 
                               angle=fire_angle * 0.5)
            
            # 轮转角度递增
            self.asura_spin_angle = (self.asura_spin_angle + 30) % 360
        
        # ========== 27. 龙骑士·雷因哈特 - 龙牙连刺 ==========
        elif pid == "dragoon":
            # 初始化连刺计数
            if not hasattr(self, 'dragoon_thrust_count'):
                self.dragoon_thrust_count = 0
            
            base_damage = self.damage * 1.2
            cx, cy = self.rect.centerx, self.rect.top
            
            # 交替发射模式：单刺 -> 双刺 -> 三连刺 -> 循环
            pattern = self.dragoon_thrust_count % 6
            
            if pattern < 2:
                # 单刺：中央一道强力枪气
                LanceQi(cx, cy, color=(150, 200, 255), damage=base_damage * 1.5)
            elif pattern < 4:
                # 双刺：左右交叉
                offset = 25 if pattern == 2 else -25
                LanceQi(cx + offset, cy, color=(100, 180, 255), damage=base_damage * 1.2)
            else:
                # 三连刺：快速三发
                for i in range(3):
                    LanceQi(cx + (i-1) * 18, cy - i * 8, 
                           color=(180, 220, 255), damage=base_damage * 0.9)
            
            self.dragoon_thrust_count += 1
        
        # ========== 28. 折纸鹤·零式 - 千羽散 ==========
        elif pid == "origami":
            from utils.bullets.origami_bullets import OrigamiBlade
            
            # 5枚扇形散射的折纸刃
            blade_count = 5
            base_damage = self.damage
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 扇形角度范围（-70° 到 -110°，即向上发射的扇形）
            angle_start = -110
            angle_end = -70
            angle_step = (angle_end - angle_start) / (blade_count - 1)
            
            for i in range(blade_count):
                angle = angle_start + i * angle_step
                # 每个刃略微随机偏移增加散射感
                angle += random.uniform(-3, 3)
                blade = OrigamiBlade(cx, cy, angle, base_damage, owner=self, bounce_count=3)
                all_sprites.add(blade)
                bullets.add(blade)
        
        # ========== 29. 星渊火陨·赫利俄斯 - 抛物线陨石 ==========
        elif pid == "helios":
            from utils.bullets.helios_bullets import MeteorBullet
            
            # 抛物线火雨弹 - 随机落点
            base_damage = self.damage
            cx, cy = self.rect.centerx, self.rect.top
            
            # 目标位置 - 屏幕前方随机
            target_x = cx + random.randint(-80, 80)
            target_y = random.randint(100, 400)
            
            meteor = MeteorBullet(cx, cy, target_x, target_y, base_damage, owner=self)
            all_sprites.add(meteor)
            bullets.add(meteor)
        
        # ========== 30. 极昼寒界·霜曜 - 极寒激光 ==========
        elif pid == "frostflare":
            from utils.bullets.frostflare_bullets import FrostLaser
            
            base_damage = self.damage
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 发射极寒激光
            laser = FrostLaser(cx, cy, base_damage, owner=self)
            all_sprites.add(laser)
            bullets.add(laser)
        
        # ========== 31. 苍穹轨断·诺娃 - 电磁轨道弹 ==========
        elif pid == "nova":
            from utils.bullets.nova_bullets import RailgunBullet
            
            base_damage = self.damage
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 检查是否蓄力（简化版，蓄力由射击间隔体现）
            bullet = RailgunBullet(cx, cy, base_damage, owner=self, charged=False)
            all_sprites.add(bullet)
            bullets.add(bullet)
        
        # ========== 32. 天幕虹裂·光谱 - 7道彩虹光束 ==========
        elif pid == "spectrum":
            from utils.bullets.spectrum_bullets import RainbowBeam
            
            base_damage = self.damage
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 7道并行彩虹光束
            for i in range(7):
                angle = -90 + (i - 3) * 8  # 扇形展开
                beam = RainbowBeam(cx, cy, angle, base_damage, i, owner=self)
                all_sprites.add(beam)
                bullets.add(beam)
        
        # ========== 33. 幽影穿心·冥弦 - 标记弹 ==========
        elif pid == "darkstring":
            from utils.bullets.darkstring_bullets import MarkShot
            
            base_damage = self.damage
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 发射标记弹
            shot = MarkShot(cx, cy, base_damage, owner=self)
            all_sprites.add(shot)
            bullets.add(shot)
        
        # ========== 34. 棘刺藤骨·荆穹 - 骨蔓鞭射击 ==========
        elif pid == "thornvine":
            from utils.bullets.thornvine_bullets import BoneWhip
            
            base_damage = self.damage
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 发射骨蔓鞭（弧线飞行的多节鞭）
            whip = BoneWhip(cx, cy, base_damage, owner=self)
            all_sprites.add(whip)
            bullets.add(whip)
        
        # ========== 35. 浮游刃环·星镰 - 环刃巡航 ==========
        elif pid == "starblade":
            from utils.bullets.starblade_bullets import RingBlade
            
            base_damage = self.damage
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 发射环刃（悬停扫割后召回）
            blade = RingBlade(cx, cy, base_damage, owner=self)
            all_sprites.add(blade)
            bullets.add(blade)
        
        # ========== 36. 酸蚀喷溅·腐沼 - 抛物酸囊 ==========
        elif pid == "acidswamp":
            from utils.bullets.acidswamp_bullets import AcidBlob
            
            base_damage = self.damage
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 目标位置 - 前方随机
            target_x = cx + random.randint(-60, 60)
            target_y = random.randint(100, 350)
            
            # 发射抛物酸囊
            blob = AcidBlob(cx, cy, target_x, target_y, base_damage, owner=self)
            all_sprites.add(blob)
            bullets.add(blob)
        
        # ========== 37. 晶簇射流·晶瀑 - 晶簇扇喷 ==========
        elif pid == "crystalfall":
            from utils.bullets.crystalfall_bullets import CrystalArrow
            
            base_damage = self.damage
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 3枚扇形散射的晶矢
            for i in range(3):
                angle = -90 + (i - 1) * 20  # -110, -90, -70 度
                angle += random.uniform(-5, 5)
                arrow = CrystalArrow(cx, cy, angle, base_damage, owner=self)
                all_sprites.add(arrow)
                bullets.add(arrow)
        
        # ========== 38. 孢子幕炮·菌幕 - 抛物孢子壳 ==========
        elif pid == "sporeveil":
            from utils.bullets.sporeveil_bullets import SporeShell
            
            base_damage = self.damage
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 目标位置 - 前方
            target_x = cx + random.randint(-40, 40)
            target_y = random.randint(150, 350)
            
            # 发射孢子壳
            shell = SporeShell(cx, cy, target_x, target_y, base_damage, owner=self)
            all_sprites.add(shell)
            bullets.add(shell)
        
        # ========== 39. 月蚀星骸·克苏鲁 - 月虹激光+月眼+蚀印 ==========
        elif pid == "cthulhu":
            from utils.bullets.cthulhu_bullets import MoonLaser, MoonEye
            
            base_damage = self.damage
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 初始化蚀印计数器
            if not hasattr(self, 'eclipse_mark_counter'):
                self.eclipse_mark_counter = 0
            
            # 主武器：月虹激光 - 贯穿全屏（传递子弹涂装）
            laser = MoonLaser(cx, cy, base_damage, owner=self, bullet_theme=self.bullet_theme)
            all_sprites.add(laser)
            bullets.add(laser)
            
            # 每3发激光生成一个月眼
            self.eclipse_mark_counter += 1
            if self.eclipse_mark_counter >= 3:
                self.eclipse_mark_counter = 0
                # 月眼 - 追踪最近敌人（传递子弹涂装）
                eye = MoonEye(cx, cy, base_damage * 0.6, owner=self, bullet_theme=self.bullet_theme)
                all_sprites.add(eye)
                bullets.add(eye)
        
        # ========== 40. 巨石核拳·图鲁 - 岩核飞拳+穿透+AOE ==========
        elif pid == "turu":
            from utils.bullets.turu_bullets import RockFist
            
            base_damage = self.damage
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 初始化巨石充能系统
            if not hasattr(self, 'rock_charge'):
                self.rock_charge = 0
            if not hasattr(self, 'armor_mode'):
                self.armor_mode = True  # True=有甲, False=卸甲状态
            if not hasattr(self, 'unarmor_timer'):
                self.unarmor_timer = 0
            if not hasattr(self, 'base_speed'):
                self.base_speed = self.speed
            if not hasattr(self, 'base_damage'):
                self.base_damage_turu = self.damage
            
            # 卸甲状态更新
            if not self.armor_mode:
                self.unarmor_timer -= 1
                if self.unarmor_timer <= 0:
                    # 恢复有甲状态
                    self.armor_mode = True
                    self.speed = self.base_speed
                    self.damage = self.base_damage_turu
                    # 提示
                    if hasattr(self, 'rect'):
                        from sprites import FloatingText
                        FloatingText(self.rect.centerx, self.rect.top - 30, "🛡️ 护甲恢复", (120, 115, 110))
            
            # 巨石充能满4格时自动触发卸甲强化
            if self.rock_charge >= 4 and self.armor_mode:
                self.armor_mode = False
                self.unarmor_timer = 300  # 5秒卸甲状态（60fps * 5）
                self.rock_charge = 0  # 消耗充能
                # 卸甲强化效果：速度+50%，伤害+80%
                self.speed = self.base_speed * 1.5
                self.damage = int(self.base_damage_turu * 1.8)
                # 提示
                if hasattr(self, 'rect'):
                    from sprites import FloatingText
                    FloatingText(self.rect.centerx, self.rect.top - 30, "⚡ 卸甲强化!", (255, 120, 40))
            
            # 发射岩核飞拳（卸甲状态伤害已提升）
            fist = RockFist(cx, cy, self.damage, owner=self, bullet_theme=self.bullet_theme)
            all_sprites.add(fist)
            bullets.add(fist)
        
        # ========== 41. 辉耀天女·斯塔德 - 月虹光梭+辉耀残痕 ==========
        elif pid == "staradia":
            from utils.bullets.staradia_bullets import MoonRainbowShuttle, RadiantRemnant
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 初始化皇辉升格系统
            if not hasattr(self, 'radiant_stacks'):
                self.radiant_stacks = 0  # 皇辉层数 0-5
            if not hasattr(self, 'radiant_domain_active'):
                self.radiant_domain_active = False  # 皇辉领域激活
            if not hasattr(self, 'radiant_domain_timer'):
                self.radiant_domain_timer = 0  # 皇辉领域持续时间
            if not hasattr(self, 'remnant_timer'):
                self.remnant_timer = 0  # 残痕生成计时
            if not hasattr(self, 'remnant_count'):
                self.remnant_count = 0  # 当前残影数量
            
            # 皇辉层数提供伤害加成：每层+10%
            radiant_mult = 1.0 + self.radiant_stacks * 0.10
            base_damage = int(self.damage * radiant_mult)
            
            # 获取涂装样式
            style = self._get_staradia_style()
            
            # 皇辉领域激活时的增强效果
            enhanced = self.radiant_domain_active
            
            # 发射3发月虹光梭（皇辉领域+1发）
            shuttle_count = 4 if enhanced else 3
            for i in range(shuttle_count):
                offset_x = (i - (shuttle_count - 1) / 2) * 25
                shuttle = MoonRainbowShuttle(cx + offset_x, cy, base_damage, owner=self, style=style)
                all_sprites.add(shuttle)
                bullets.add(shuttle)
            
            # 每5发子弹生成一个辉耀残痕（皇辉领域时每3发）
            self.remnant_timer += 1
            remnant_interval = 3 if enhanced else 5
            if self.remnant_timer >= remnant_interval:
                self.remnant_timer = 0
                # 在玩家前方随机位置生成残痕
                remnant_x = cx + random.randint(-80, 80)
                remnant_y = cy - random.randint(50, 150)
                remnant = RadiantRemnant(remnant_x, remnant_y, owner=self, enhanced=enhanced, style=style)
                all_sprites.add(remnant)
                self.remnant_count += 1  # 增加残影计数
        
        # ========== 42. 深渊龙鱼·猪公爵 - 深渊水矛+鲨龙卷 ==========
        elif pid == "dukefishron":
            from utils.bullets.dukefishron_bullets import AbyssSpear, SharkTornado
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 初始化猪公爵系统
            if not hasattr(self, 'active_tornados'):
                self.active_tornados = []  # 当前活跃的鲨龙卷
            if not hasattr(self, 'duke_refract_ready'):
                self.duke_refract_ready = False  # 折射泡准备
            if not hasattr(self, 'duke_dive_charge'):
                self.duke_dive_charge = 0  # 俯冲充能
            if not hasattr(self, 'duke_tsunami_active'):
                self.duke_tsunami_active = False  # 海啸激活
            if not hasattr(self, 'duke_tsunami_speed_bonus'):
                self.duke_tsunami_speed_bonus = 0  # 海啸速度加成
            
            # 获取涂装样式
            style = self._get_duke_style()
            
            # 检查是否有活跃龙卷可激活爆炸
            if self.active_tornados:
                # 激活最老的龙卷爆炸
                oldest = self.active_tornados[0]
                if oldest and hasattr(oldest, 'activate_explosion'):
                    oldest.activate_explosion()
                    # 龙卷爆炸不发射新水矛
                    return
            
            # 发射深渊水矛
            is_refract = self.duke_refract_ready
            if is_refract:
                self.duke_refract_ready = False
                # 折射泡模式：发射折射水矛
                spear = AbyssSpear(cx, cy, self.damage, owner=self, style=style, is_refract=True)
                all_sprites.add(spear)
                bullets.add(spear)
                # 提示
                from sprites import FloatingText
                FloatingText(cx, cy - 30, "🫧折射!", (100, 180, 255))
            else:
                # 普通水矛
                spear = AbyssSpear(cx, cy, self.damage, owner=self, style=style, is_refract=False)
                all_sprites.add(spear)
                bullets.add(spear)
        
        # ========== 43. 末世星凝·史莱姆 - 星凝弹+凝胶子核+重力域 ==========
        elif pid == "slime":
            from utils.bullets.slime_bullets import StarGelBullet, MiniStarGelBullet, GravityDomain
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 获取涂装样式
            style = self._get_slime_style()
            
            # 初始化史莱姆系统
            if not hasattr(self, 'slime_gel_stacks'):
                self.slime_gel_stacks = 0  # 星凝叠层
            if not hasattr(self, 'slime_domain_timer'):
                self.slime_domain_timer = 0  # 重力域冷却
            if not hasattr(self, 'slime_burst_ready'):
                self.slime_burst_ready = False  # 爆发准备
            
            # 发射主弹 - 星凝弹
            main_bullet = StarGelBullet(cx, cy, self.damage, owner=self, style=style)
            all_sprites.add(main_bullet)
            bullets.add(main_bullet)
            
            # 每3发释放凝胶子核
            self.slime_gel_stacks += 1
            if self.slime_gel_stacks >= 3:
                self.slime_gel_stacks = 0
                # 左右各发射一枚凝胶子核
                for offset in [-25, 25]:
                    mini = MiniStarGelBullet(cx + offset, cy + 10, self.damage * 0.4, owner=self, style=style)
                    all_sprites.add(mini)
                    bullets.add(mini)
            
            # 重力域冷却（每2秒可放置一个）
            self.slime_domain_timer += 1
            if self.slime_domain_timer >= 120:  # 2秒冷却
                self.slime_domain_timer = 0
                # 在前方随机位置放置重力域
                domain_x = cx + random.randint(-60, 60)
                domain_y = cy - random.randint(80, 150)
                domain = GravityDomain(domain_x, domain_y, owner=self, style=style)
                all_sprites.add(domain)
        
        # ========== 44. 终噬星链·奥罗 - 虚空链弹+链节+激光栅 ==========
        elif pid == "oro":
            from utils.bullets.oro_bullets import VoidChainBullet, ChainNode, LaserGrid
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 获取涂装样式
            style = self._get_oro_style()
            
            # 初始化奥罗系统
            if not hasattr(self, 'oro_chain_stacks'):
                self.oro_chain_stacks = 0  # 链节叠层
            if not hasattr(self, 'oro_laser_timer'):
                self.oro_laser_timer = 0  # 激光栅冷却
            if not hasattr(self, 'oro_void_energy'):
                self.oro_void_energy = 0  # 虚空能量
            
            # 发射主弹 - 虚空链弹（1.6屏超远距离）
            main_bullet = VoidChainBullet(cx, cy, self.damage, owner=self, style=style)
            all_sprites.add(main_bullet)
            bullets.add(main_bullet)
            
            # 每6发释放链节（驻场3秒，减少生成频率）
            self.oro_chain_stacks += 1
            if self.oro_chain_stacks >= 6:
                self.oro_chain_stacks = 0
                # 在弹道中间位置放置链节
                node_y = cy - 200
                node = ChainNode(cx, node_y, self.damage * 0.5, owner=self, style=style)
                all_sprites.add(node)
                bullets.add(node)
            
            # 激光栅冷却（每2.5秒发射一次十字激光）
            self.oro_laser_timer += 1
            if self.oro_laser_timer >= 150:  # 2.5秒冷却
                self.oro_laser_timer = 0
                # 在前方发射激光栅
                laser_y = cy - 150
                laser = LaserGrid(cx, laser_y, self.damage * 0.3, owner=self, style=style)
                all_sprites.add(laser)
                bullets.add(laser)
        
        # ========== 45. 狱炎神龙·犽戎 - 日耀喷流+浮游炮+龙息 ==========
        elif pid == "yharon":
            from utils.bullets.yharon_bullets import (FlareStreamBullet, BorderDrone, 
                                                      JungleBreath)
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            
            # 获取涂装样式
            style = self._get_yharon_style()
            
            # 初始化犽戎系统
            if not hasattr(self, 'yharon_border_drones'):
                # 创建炼狱边界浮游炮
                self.yharon_border_drones = []
                for side in ["left", "right"]:
                    drone = BorderDrone(self, side, style)
                    self.yharon_border_drones.append(drone)
            if not hasattr(self, 'yharon_kill_count'):
                self.yharon_kill_count = 0  # 击杀计数（每10杀触发丛林龙息）
            if not hasattr(self, 'yharon_fire_timer'):
                self.yharon_fire_timer = 0  # 浮游炮开火计时
            if not hasattr(self, 'is_firing'):
                self.is_firing = False
            
            self.is_firing = True  # 标记正在开火
            
            # 发射主弹 - 日耀喷流（双发扇形）
            for angle_offset in [-8, 8]:
                bullet = FlareStreamBullet(cx, cy, self.damage, angle=-90 + angle_offset, 
                                          owner=self, style=style)
            
            # 浮游炮辅助射击
            self.yharon_fire_timer += 1
            if self.yharon_fire_timer >= 10:  # 每10帧浮游炮辅助开火
                self.yharon_fire_timer = 0
                for drone in self.yharon_border_drones:
                    if drone.alive():
                        drone.fire_assist()
        
        # ========== 46. 亵渎天神·普罗维登斯 - 神圣碎片+亵渎之矛 ==========
        elif pid == "providence":
            from utils.bullets.providence_bullets import (HolyShardBullet, ProfanedSpearBullet,
                                                          HealerGuardian, CocoonShield)
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            style = self._get_providence_style()
            
            # 初始化茧化模式系统
            if not hasattr(self, 'cocoon_mode_active'):
                self.cocoon_mode_active = False
                self.cocoon_shield = None
                self.cocoon_guardians = []
                self.providence_stationary_timer = 0
                self.last_pos = (self.rect.x, self.rect.y)
            
            # 检测静止状态（茧化模式）
            if (self.rect.x, self.rect.y) == self.last_pos:
                self.providence_stationary_timer += 1
                if self.providence_stationary_timer >= 60 and not self.cocoon_mode_active:  # 静止1秒触发
                    self.cocoon_mode_active = True
                    # 创建护盾和守卫
                    self.cocoon_shield = CocoonShield(self, style)
                    for i in range(4):
                        g = HealerGuardian(self, i, 4, style)
                        self.cocoon_guardians.append(g)
            else:
                self.providence_stationary_timer = 0
                if self.cocoon_mode_active:
                    self.cocoon_mode_active = False
                    if self.cocoon_shield:
                        self.cocoon_shield.deactivate()
                    for g in self.cocoon_guardians:
                        if g.alive():
                            g.kill()
                    self.cocoon_guardians = []
            
            self.last_pos = (self.rect.x, self.rect.y)
            
            # 茧化模式时恢复生命
            if self.cocoon_mode_active:
                self.hp = min(self.max_hp, self.hp + self.max_hp * 0.03 / 60)  # 3% HP/秒
            
            # 主武器：神圣碎片（悬停炸弹）
            HolyShardBullet(cx, cy, self.damage, angle=-90, owner=self, style=style)
            
            # 副武器：亵渎之矛（每3发穿透矛）
            if not hasattr(self, 'providence_spear_counter'):
                self.providence_spear_counter = 0
            self.providence_spear_counter += 1
            if self.providence_spear_counter >= 3:
                self.providence_spear_counter = 0
                ProfanedSpearBullet(cx - 15, cy, self.damage * 0.7, angle=-90, owner=self, style=style)
                ProfanedSpearBullet(cx + 15, cy, self.damage * 0.7, angle=-90, owner=self, style=style)
        
        # ========== 47. 瘟疫使者·歌莉娅 - 瘟疫导弹+病毒尘埃 ==========
        elif pid == "goliath":
            from utils.bullets.goliath_bullets import (PlagueMissileBullet, PlagueDrone, PlagueCloud, PlagueDust)
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            style = self._get_goliath_style()
            
            # 初始化瘟疫系统
            if not hasattr(self, 'goliath_drones'):
                self.goliath_drones = []
                self.goliath_dust_timer = 0
                self.goliath_last_pos = (self.rect.centerx, self.rect.centery)
            
            # ========== 被动：瘟疫感染 - 路径残留病毒尘埃 ==========
            # 移动时在路径上留下病毒尘埃
            current_pos = (self.rect.centerx, self.rect.centery)
            dx = current_pos[0] - self.goliath_last_pos[0]
            dy = current_pos[1] - self.goliath_last_pos[1]
            move_dist = (dx*dx + dy*dy) ** 0.5
            
            self.goliath_dust_timer += 1
            if move_dist > 5 and self.goliath_dust_timer >= 8:  # 移动时每8帧生成尘埃
                self.goliath_dust_timer = 0
                # 在身后生成病毒尘埃
                dust_x = self.rect.centerx + random.randint(-20, 20)
                dust_y = self.rect.centery + random.randint(10, 30)
                PlagueDust(dust_x, dust_y, self.damage * 0.05, owner=self, style=style)
            
            self.goliath_last_pos = current_pos
            
            # 更新无人机存活状态
            self.goliath_drones = [d for d in self.goliath_drones if d.alive()]
            
            # 主武器：瘟疫巡航导弹（爆炸后留下毒云）
            PlagueMissileBullet(cx, cy, self.damage, angle=-90, owner=self, style=style)
        
        # ========== 48. 至尊灾厄·终末王座 - 硫磺火矢+骷髅尾巴 ==========
        elif pid == "sepulcher":
            from utils.bullets.sepulcher_bullets import (BrimstoneBolt, TheBrothersSkill,
                                                         SkullTail, CalamityAura, MagicHalo)
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            style = self._get_sepulcher_style()
            
            # 初始化Sepulcher系统
            if not hasattr(self, 'sepulcher_initialized') or not self.sepulcher_initialized:
                self._init_sepulcher_systems()
                self.sepulcher_initialized = True
            
            # 更新Sepulcher系统
            self._update_sepulcher_systems()
            
            # 暴怒状态下射速提升50%
            fire_rate_mult = 1.5 if self.sepulcher_fury_active else 1.0
            
            # 主武器：硫磺火矢（折射激光）
            # 高频双发
            BrimstoneBolt(cx - 15, cy, self.damage, angle=-90, owner=self, style=style)
            BrimstoneBolt(cx + 15, cy, self.damage, angle=-90, owner=self, style=style)
            
            # 暴怒状态额外射击
            if self.sepulcher_fury_active:
                for _ in range(2):
                    offset = random.randint(-30, 30)
                    BrimstoneBolt(cx + offset, cy, self.damage * 0.6, 
                                 angle=-90 + random.randint(-10, 10), owner=self, style=style)
        
        # ========== 49. 方舟·苍穹 - 宇宙剪刃+星辰剪切 ==========
        elif pid == "galaxia":
            from utils.bullets.galaxia_bullets import SplitStar, CosmicScissorBullet
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            style = self._get_galaxia_style()
            
            # 初始化GALAXIA系统
            if not hasattr(self, 'galaxia_initialized') or not self.galaxia_initialized:
                self.galaxia_snip_range = 80  # 剪切范围
                self.galaxia_parry_chance = 0.3  # 弹反概率
                self.galaxia_initialized = True
            
            # 主武器：宇宙剪刃（双发交叉）
            CosmicScissorBullet(cx - 12, cy, self.damage, angle=-85, owner=self, style=style)
            CosmicScissorBullet(cx + 12, cy, self.damage, angle=-95, owner=self, style=style)
            
            # 被动：星辰剪切（近战范围攻击）
            # 在前方扇形区域检测敌人
            for mob in mobs:
                if hasattr(mob, 'rect'):
                    dx = mob.rect.centerx - cx
                    dy = mob.rect.centery - cy
                    dist = math.hypot(dx, dy)
                    
                    # 范围内且在前方60度扇形内
                    if dist < self.galaxia_snip_range and dy < 0:
                        angle_to_mob = math.degrees(math.atan2(dy, dx))
                        if -120 <= angle_to_mob <= -60:  # 前方扇形
                            if hasattr(mob, 'take_damage'):
                                mob.take_damage(self.damage * 0.4)
                                
                                # 命中产生裂变星体
                                if random.random() < 0.5:
                                    # 找个新目标
                                    target = None
                                    for other_mob in mobs:
                                        if other_mob != mob and hasattr(other_mob, 'rect'):
                                            target = other_mob
                                            break
                                    SplitStar(cx, cy, target, self.damage * 0.2, style=style)
        
        # ========== 50. 真理之书·MAGNUS - 奥术飞弹+法术轮盘 ==========
        elif pid == "magnus":
            from utils.bullets.magnus_bullets import (ArcaneMissileBullet, FireballBullet, 
                                                      FrostWaveBullet, LightningChainBullet,
                                                      PageGuardBullet)
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            style = self._get_magnus_style()
            
            # 初始化MAGNUS系统
            if not hasattr(self, 'magnus_initialized') or not self.magnus_initialized:
                self.magnus_mana = 0                    # 法力值（用于过载）
                self.magnus_max_mana = 100              # 最大法力
                self.magnus_overload = False            # 过载状态
                self.magnus_overload_timer = 0         # 过载持续时间
                self.magnus_spell_mode = 0              # 法术轮盘：0=奥术 1=火 2=冰 3=雷
                self.magnus_spell_names = ["奥术", "火焰", "冰霜", "闪电"]
                self.magnus_page_shield = 6             # 书页护盾数量
                self.magnus_last_shoot = 0             # 上次射击时间
                self.magnus_initialized = True
            
            # ========== 被动：法力过载 - 不射击时充能 ==========
            now = pygame.time.get_ticks()
            if now - self.magnus_last_shoot > 1000:  # 1秒不射击开始充能
                if not self.magnus_overload:
                    self.magnus_mana = min(self.magnus_max_mana, self.magnus_mana + 2)
                    # 满法力触发过载
                    if self.magnus_mana >= self.magnus_max_mana:
                        self.magnus_overload = True
                        self.magnus_overload_timer = 180  # 3秒过载
                        FloatingText(cx, cy - 40, "⚡法力过载!", (255, 215, 100))
            
            self.magnus_last_shoot = now
            
            # 更新过载状态
            if self.magnus_overload:
                self.magnus_overload_timer -= 1
                if self.magnus_overload_timer <= 0:
                    self.magnus_overload = False
                    self.magnus_mana = 0
            
            # 根据当前法术模式发射
            spell = self.magnus_spell_mode
            is_overloaded = self.magnus_overload
            
            if spell == 0:  # 奥术飞弹
                # 过载时三倍弹幕
                shot_count = 3 if is_overloaded else 1
                for s in range(shot_count):
                    for i in range(cnt):
                        offset_x = (i - (cnt-1)/2) * 20 + (s - 1) * 10
                        angle_offset = (s - 1) * 8
                        ArcaneMissileBullet(cx + offset_x, cy, 
                                           angle=-1.57 + math.radians(angle_offset),
                                           damage=self.damage,
                                           element="arcane", 
                                           overloaded=is_overloaded)
            
            elif spell == 1:  # 火球术
                shot_count = 3 if is_overloaded else 1
                for s in range(shot_count):
                    angle_offset = (s - 1) * 15
                    FireballBullet(cx, cy, 
                                  angle=-1.57 + math.radians(angle_offset),
                                  damage=self.damage * 1.5)
            
            elif spell == 2:  # 冰霜波
                # 扇形散射
                spread = 7 if is_overloaded else 5
                for i in range(spread):
                    angle = -45 + i * (90 / (spread - 1))
                    FrostWaveBullet(cx, cy,
                                   angle=-1.57 + math.radians(angle),
                                   damage=self.damage * 0.6)
            
            elif spell == 3:  # 闪电链
                # 寻找最近敌人
                nearest = None
                nearest_dist = 300
                for mob in mobs:
                    if hasattr(mob, 'rect') and hasattr(mob, 'alive') and mob.alive():
                        dist = math.hypot(mob.rect.centerx - cx, mob.rect.centery - cy)
                        if dist < nearest_dist:
                            nearest_dist = dist
                            nearest = mob
                
                chain_count = 5 if is_overloaded else 3
                LightningChainBullet(cx, cy, target=nearest,
                                    damage=self.damage * 0.8,
                                    chain_count=chain_count)
        
        # ========== 51. 维那斯万岁·HEAVY METAL - 音符弹幕+节奏攻击 ==========
        elif pid == "heavymetal":
            from utils.bullets.heavymetal_bullets import (NoteBullet, PowerChordWave,
                                                          EncoreFirework, StageDiveMeteor,
                                                          EchoClone, DeathMetalSolo,
                                                          spawn_encore_fireworks)
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            style = self._get_heavymetal_style()
            
            # 初始化HEAVY METAL系统
            if not hasattr(self, 'heavymetal_initialized') or not self.heavymetal_initialized:
                self.heavymetal_combo = 0               # 连击数
                self.heavymetal_max_combo = 100         # 满连击触发Encore
                self.heavymetal_bpm = 120               # 节拍速度
                self.heavymetal_beat_timer = 0          # 节拍计时
                self.heavymetal_on_beat = False         # 是否在节拍上
                self.heavymetal_rhythm_bonus = 1.0      # 节奏加成
                self.heavymetal_echo_clones = []        # 回声克隆列表
                self.heavymetal_initialized = True
            
            # ========== 被动：BPM同步 - 踩准节拍增加伤害 ==========
            self.heavymetal_beat_timer += 1
            beat_interval = 60 * 60 // self.heavymetal_bpm  # 帧数间隔
            beat_phase = self.heavymetal_beat_timer % beat_interval
            
            # 在节拍前后5帧内视为踩准
            on_beat_window = 5
            self.heavymetal_on_beat = beat_phase < on_beat_window or beat_phase > beat_interval - on_beat_window
            
            if self.heavymetal_on_beat:
                self.heavymetal_rhythm_bonus = 1.5  # 50%伤害加成
            else:
                self.heavymetal_rhythm_bonus = max(1.0, self.heavymetal_rhythm_bonus - 0.05)
            
            # 发射音符弹幕
            note_damage = self.damage * self.heavymetal_rhythm_bonus
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 18
                # 不同音符类型 (整数索引)
                note_type_index = i % 4
                nb = NoteBullet(cx + offset_x, cy, 
                          damage=note_damage,
                          note_type=note_type_index,
                          on_beat=self.heavymetal_on_beat)
            
            # 命中时增加连击
            self.heavymetal_combo = min(self.heavymetal_max_combo, self.heavymetal_combo + 1)
            
            # 满连击触发Encore烟火
            if self.heavymetal_combo >= self.heavymetal_max_combo:
                self.heavymetal_combo = 0
                spawn_encore_fireworks(cx, cy, count=16, damage=int(self.damage * 2))
                FloatingText(cx, cy - 50, "🎆 ENCORE!", (255, 200, 50))
        
        # ========== 52. 绯红恶魔·SCARLET - 魔枪投掷+吸血 ==========
        elif pid == "scarlet":
            from utils.bullets.scarlet_bullets import ScarletLanceBullet
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            style = self._get_scarlet_style() if hasattr(self, '_get_scarlet_style') else "scarlet_default"
            
            # 初始化SCARLET系统
            if not hasattr(self, 'scarlet_initialized') or not self.scarlet_initialized:
                self.scarlet_blood_stacks = 0          # 鲜血层数
                self.scarlet_max_blood = 10            # 最大层数
                self.scarlet_stealth_mode = False      # 潜行状态
                self.scarlet_initialized = True
            
            # 发射魔枪投掷
            for i in range(cnt):
                offset_x = (i - (cnt-1)/2) * 15
                lance = ScarletLanceBullet(cx + offset_x, cy, 
                                          damage=self.damage,
                                          owner=self,
                                          style=style)
                all_sprites.add(lance)
                bullets.add(lance)
            
            # 累计鲜血层数
            self.scarlet_blood_stacks = min(self.scarlet_max_blood, self.scarlet_blood_stacks + 0.1)
        
        # ========== 53. 分形天顶·ZENITH - 天顶剑影（椭圆轨迹） ==========
        elif pid == "zenith":
            from utils.bullets.zenith_bullets import (ThrowingSwordBullet, FractalShield,
                                                      get_sword_array, clear_sword_array)
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            style = self._get_zenith_style() if hasattr(self, '_get_zenith_style') else "zenith_default"
            
            # 初始化天顶系统
            if not hasattr(self, 'zenith_initialized') or not self.zenith_initialized:
                self.zenith_sword_array = get_sword_array(self, style)
                self.zenith_shield = FractalShield(self, style)
                self.zenith_initialized = True
                self.zenith_sword_count = 0  # 剑计数器
            
            # 发射天顶剑影 - 椭圆轨迹飞行，第一把剑不追踪
            self.zenith_sword_count = getattr(self, 'zenith_sword_count', 0) + 1
            is_first = (self.zenith_sword_count % 3 == 1)  # 每3把剑中第1把不追踪
            sword = ThrowingSwordBullet(cx, cy, self.damage, owner=self, 
                                        style=style, sword_array=self.zenith_sword_array,
                                        is_first=is_first)
        
        # ========== 54. 光之在解·VISCERATOR - 追踪光流（软管追踪） ==========
        elif pid == "viscerator":
            from utils.bullets.viscerator_bullets import (
                ExoStreamBullet, SparkStickManager, fire_exo_stream
            )
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            style = self._get_viscerator_style() if hasattr(self, '_get_viscerator_style') else "viscerator_default"
            
            # 初始化光流系统
            if not hasattr(self, 'viscerator_initialized') or not self.viscerator_initialized:
                self.viscerator_spark_manager = SparkStickManager()
                self.viscerator_initialized = True
                self.viscerator_stream_side = 0  # 左右交替
            
            # 发射追踪光流 - 像软管一样弯曲追踪敌人
            self.viscerator_stream_side = 1 - getattr(self, 'viscerator_stream_side', 0)
            offset_x = 18 if self.viscerator_stream_side == 0 else -18
            fire_exo_stream(cx + offset_x, cy, self.damage, self, style)
        
        # ========== 55. 晶体粉碎者·CRUSHER - 荒芜光束（瞬发穿透） ==========
        elif pid == "crusher":
            from utils.bullets.crusher_bullets import DesolationBeamBullet
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            style = self._get_crusher_style() if hasattr(self, '_get_crusher_style') else "crusher_default"
            
            # 初始化CRUSHER系统
            if not hasattr(self, 'crusher_initialized') or not self.crusher_initialized:
                self.crusher_beam_side = 0           # 光束左右交替
                self.crusher_armor_stacks = 0        # 晶体护甲层数
                self.crusher_max_armor = 20          # 最大护甲层数
                self.crusher_initialized = True
            
            # 发射荒芜光束 - 瞬发穿透
            self.crusher_beam_side = 1 - self.crusher_beam_side
            offset_x = 15 if self.crusher_beam_side == 0 else -15
            beam = DesolationBeamBullet(cx + offset_x, cy, self.damage, self, style)
            all_sprites.add(beam)
            bullets.add(beam)
            
            # 每次射击累积R技能能量（每次+1.5%，约67次满）
            self.ult4_charge = min(self.max_ult4_charge, self.ult4_charge + 1.5)
        
        # ========== 56. 星际海豚·S.D.M.G. - 叶绿曳光弹（弱追踪高射速） ==========
        elif pid == "sdmg":
            from utils.bullets.sdmg_bullets import ChlorophyteTracerBullet, OverheatManager
            
            cx, cy = self.rect.centerx, self.rect.top - 5
            style = self._get_sdmg_style() if hasattr(self, '_get_sdmg_style') else "sdmg_default"
            
            # 获取或创建过热系统实例
            overheat_mgr = OverheatManager.get_instance(self)
            
            # 初始化辅助变量
            if not hasattr(self, 'sdmg_gatling_angle'):
                self.sdmg_gatling_angle = 0
            
            # 检查是否过热（不再更新，因为会在其他地方更新）
            if overheat_mgr.overheated:
                # 过热状态，播放蒸汽效果但不射击
                if random.random() < 0.3:
                    Particle((cx + random.randint(-15, 15), cy + 20), (200, 200, 200), mode='spark')
                return
            
            # 可以射击 - 添加热量
            overheat_mgr.add_heat()
            
            # 获取散射惩罚
            spread_penalty = overheat_mgr.get_spread_penalty()
            spread = random.uniform(-spread_penalty, spread_penalty)
            
            # 旋转枪管视觉效果
            self.sdmg_gatling_angle += 0.5
            
            # 发射叶绿曳光弹
            bullet = ChlorophyteTracerBullet(cx, cy, self.damage, self, style, spread)
            all_sprites.add(bullet)
            bullets.add(bullet)
            
            # 弹壳粒子效果
            if random.random() < 0.4:
                shell_x = cx + random.randint(-10, 10)
                shell_y = cy + 30
                Particle((shell_x, shell_y), (255, 215, 0), mode='spark')
        
        # 默认情况
        else:
            cnt = self.bullet_count
            start_x = self.rect.centerx - (cnt-1)*10
            for i in range(cnt):
                Bullet(start_x + i*20, self.rect.top, color=color, b_type=b_type, 
                       piercing=self.piercing, homing=homing_value, bullet_theme=self.bullet_theme)

    def _update_pandemic_infections(self):
        """更新末日瘟神的感染系统"""
        if not hasattr(self, 'infected_enemies'):
            return
        
        # 处理每个感染的敌人
        for enemy, data in list(self.infected_enemies.items()):
            if not enemy.alive():
                # 敌人死亡时传播感染
                self._spread_infection(enemy, data["level"])
                del self.infected_enemies[enemy]
                continue
            
            # 累积潜伏伤害
            data["timer"] += 1
            base_dmg = self.damage * 0.1 * data["level"]
            # 变异加成
            mutation_bonus = 1 + self.pandemic_mutation_level * 0.15
            data["damage_stack"] += base_dmg * mutation_bonus
            
            # 每3秒爆发一次潜伏伤害
            if data["timer"] >= 180:  # 3秒
                burst_damage = data["damage_stack"]
                enemy.hp -= burst_damage
                FloatingText(enemy.rect.centerx, enemy.rect.top - 10, 
                           f"☣️{int(burst_damage)}", (150, 255, 100))
                data["damage_stack"] = 0
                data["timer"] = 0
        
        # 变异进化：每传播5次变异一次
        if self.pandemic_spread_count >= 5:
            self.pandemic_spread_count = 0
            self.pandemic_mutation_level = min(10, self.pandemic_mutation_level + 1)
            # 随机变异效果
            mutation_effects = ["damage", "slow", "armor_break", "spread_range"]
            effect = random.choice(mutation_effects)
            if not hasattr(self, 'pandemic_mutations'):
                self.pandemic_mutations = {}
            self.pandemic_mutations[effect] = self.pandemic_mutations.get(effect, 0) + 1
            FloatingText(self.rect.centerx, self.rect.top - 30, 
                       f"🧬变异Lv.{self.pandemic_mutation_level}", (200, 255, 100))
    
    def _spread_infection(self, source_enemy, level):
        """感染传播"""
        if not hasattr(self, 'pandemic_mutations'):
            self.pandemic_mutations = {}
        
        spread_range = 120 + self.pandemic_mutations.get("spread_range", 0) * 30
        new_level = min(5, level + 1)
        
        for enemy in list(mobs):
            if enemy == source_enemy or enemy in self.infected_enemies:
                continue
            dist = math.hypot(enemy.rect.centerx - source_enemy.rect.centerx,
                            enemy.rect.centery - source_enemy.rect.centery)
            if dist < spread_range:
                self.infected_enemies[enemy] = {
                    "level": new_level,
                    "damage_stack": 0,
                    "timer": 0
                }
                self.pandemic_spread_count += 1
                FloatingText(enemy.rect.centerx, enemy.rect.top - 10, 
                           "☣️感染!", (100, 255, 80))
    
    def _update_puppet_system(self):
        """更新傀儡师的傀儡系统"""
        if not hasattr(self, 'puppet_enemies'):
            return
        
        for enemy, data in list(self.puppet_enemies.items()):
            if not enemy.alive():
                del self.puppet_enemies[enemy]
                continue
            
            if data.get("controlled"):
                # 被控制的敌人对其他敌人造成接触伤害
                for other in list(mobs):
                    if other == enemy or other in self.puppet_enemies:
                        continue
                    dist = math.hypot(enemy.rect.centerx - other.rect.centerx,
                                    enemy.rect.centery - other.rect.centery)
                    if dist < 50:
                        contact_damage = self.damage * 0.5
                        other.hp -= contact_damage
                        FloatingText(other.rect.centerx, other.rect.top - 10, 
                                   f"🎭{int(contact_damage)}", (180, 100, 150))

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
        # 冷却检查
        if self.ult_cooldown > 0:
            return  # 冷却中，无法释放
        
        if self.ult_charge >= 100:
            self.ult_charge -= 100
            # 设置冷却计时
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
            
            elif pid == "wormhole":
                # 维度坍缩：全屏虫洞爆发
                DimensionCollapse(self)
            
            elif pid == "chronos":
                # 【过去之影】时间回溯：回到3秒前的位置状态，恢复HP，清除debuff
                ChronosPastShadow(self)
            
            elif pid == "mirage":
                # 【无限镜界】召唤最大数量分身并全部同时发射强力光束
                MirageInfinityRealm(self)
            
            elif pid == "gambit":
                # 【命运轮盘】启动赌博轮盘，随机触发超强效果
                GambitFortuneWheel(self)
            
            elif pid == "puppeteer":
                # 【全场魅惑】魅惑50%的敌人成为傀儡
                PuppeteerMassCharm(self)
            
            elif pid == "pandemic":
                # 【零号毒株】全屏感染+变异等级+3
                PandemicPatientZero(self)
            
            elif pid == "omega":
                # 【终焉审判】七属性同时爆发的终极制裁
                OmegaFinalJudgment(self)
            
            elif pid == "genesis":
                # 【创世纪元】宇宙大爆炸重塑战场
                GenesisBigBang(self)
            
            elif pid == "truth":
                # 【真理显现】全知之眼审视一切，揭示并制裁所有敌人
                TruthRevelation(self)
            
            elif pid == "asura":
                # 【六臂天斩】召唤六只巨大剑臂进行全屏斩击
                AsuraSixArmSlash(self)
            
            elif pid == "dragoon":
                # 【天龙俯冲】从天而降的强力突刺
                DragoonSkyDive(self)
            
            elif pid == "origami":
                # 【纸鹤群】召唤7只AI纸鹤无人机协同作战
                OrigamiCraneSwarm(self)
            
            elif pid == "helios":
                # 【流星群】召唤7颗陨石覆盖全场
                from utils.bullets.helios_bullets import MeteorShower
                MeteorShower(self)
            
            elif pid == "frostflare":
                # 【零度射线】发射跟踪冻结射线
                from utils.bullets.frostflare_bullets import ZeroDegreeRay
                ZeroDegreeRay(self)
            
            elif pid == "nova":
                # 【充能击穿】发射3发超级轨道弹
                from utils.bullets.nova_bullets import ChargePierceUlt
                ChargePierceUlt(self)
            
            elif pid == "spectrum":
                # 【光谱叠加】全屏横扫彩虹弹幕
                from utils.bullets.spectrum_bullets import SpectrumStackUlt
                SpectrumStackUlt(self)
            
            elif pid == "darkstring":
                # 【绝杀狙击】处决所有被标记的敌人
                from utils.bullets.darkstring_bullets import DeathSniperUlt
                DeathSniperUlt(self)
            
            elif pid == "thornvine":
                # 【荆棘风暴】释放5波藤骨鞭旋风
                from utils.bullets.thornvine_bullets import ThornStorm
                ThornStorm(self)
            
            elif pid == "starblade":
                # 【刃环风暴】召唤7个环刃不同高度横扫
                from utils.bullets.starblade_bullets import BladeStorm
                BladeStorm(self)
            
            elif pid == "acidswamp":
                # 【酸液洪流】释放12枚酸囊覆盖全场
                from utils.bullets.acidswamp_bullets import AcidFlood
                AcidFlood(self)
            
            elif pid == "crystalfall":
                # 【晶暴射流】5波8箭晶簇覆盖全场
                from utils.bullets.crystalfall_bullets import CrystalStorm
                CrystalStorm(self)
            
            elif pid == "sporeveil":
                # 【孢子绽放】释放6个大型孢子云幕
                from utils.bullets.sporeveil_bullets import SporeBloom
                SporeBloom(self)
            
            elif pid == "cthulhu":
                # 【月蚀降临】三段大招：月虹解放→星骸召唤→月蚀降临
                from utils.bullets.cthulhu_bullets import EclipseDescent
                EclipseDescent(self)
            
            elif pid == "turu":
                # 【岩拳暴雨】2秒内连射6枚巨型岩核拳
                from utils.bullets.turu_bullets import RockFistBarrage
                RockFistBarrage(self)
            
            elif pid == "staradia":
                # 【皇辉暴雨】2秒内连续9道皇辉束
                from utils.bullets.staradia_bullets import RadiantStorm
                # 提取涂装样式
                style = self._get_staradia_style()
                storm = RadiantStorm(self.rect.centerx, self.rect.centery, owner=self, style=style)
                all_sprites.add(storm)
            
            elif pid == "dukefishron":
                # 【鲨龙卷暴雨】2秒内连续生成7道鲨龙卷
                from utils.bullets.dukefishron_bullets import SharkTornadoStorm
                style = self._get_duke_style()
                storm = SharkTornadoStorm(owner=self, style=style)
                all_sprites.add(storm)
            
            elif pid == "slime":
                # 【星陨踩踏】跃起后猛砸，落地360度激光散射（参考Aureus跳跃踩踏）
                from utils.bullets.slime_bullets import StarStompSkill
                style = self._get_slime_style()
                skill = StarStompSkill(self.rect.centerx, self.rect.centery, owner=self, style=style)
                all_sprites.add(skill)
            
            elif pid == "oro":
                # 【宇宙坍缩·维度网格】F技能：节段解离飞向四边，构建激光网格向中心收缩
                from utils.bullets.oro_bullets import DimensionGridSkill
                style = self._get_oro_style()
                skill = DimensionGridSkill(self.rect.centerx, self.rect.centery, self.damage * 3, owner=self, style=style)
                all_sprites.add(skill)
            
            elif pid == "yharon":
                # 【千兆核爆】F技能：火柱从四周收缩推挤敌人，中心引爆
                from utils.bullets.yharon_bullets import GigaNukeSkill
                style = self._get_yharon_style()
                skill = GigaNukeSkill(self.rect.centerx, self.rect.centery, self.damage * 3, owner=self, style=style)
                all_sprites.add(skill)
            
            elif pid == "providence":
                # 【熔融之雨】F技能：天降熔岩球，覆盖全屏
                from utils.bullets.providence_bullets import create_molten_rain
                style = self._get_providence_style()
                create_molten_rain(self, self.damage * 2, style, count=20)
            
            elif pid == "goliath":
                # 【饱和轰炸】F技能：瘟疫炸弹波浪式覆盖全屏
                from utils.bullets.goliath_bullets import CarpetBombingSkill
                style = self._get_goliath_style()
                skill = CarpetBombingSkill(owner=self, damage=self.damage * 2.5, style=style)
                all_sprites.add(skill)
            
            elif pid == "sepulcher":
                # 【狱火方阵】F技能：火墙缩圈+骷髅反弹绞杀
                from utils.bullets.sepulcher_bullets import InfernalBoxSkill
                style = self._get_sepulcher_style()
                skill = InfernalBoxSkill(owner=self, damage=self.damage * 3, style=style)
                # skill有自己的render方法，需要特殊处理
                if not hasattr(self, 'sepulcher_active_skills'):
                    self.sepulcher_active_skills = []
                self.sepulcher_active_skills.append(skill)
            
            elif pid == "galaxia":
                # 【次元斩】F技能：三道全屏紫色裂痕切割
                from utils.bullets.galaxia_bullets import DimensionalSlashSkill
                style = self._get_galaxia_style()
                skill = DimensionalSlashSkill(self.rect.centerx, self.rect.centery, 
                                             self.damage * 2.5, style=style)
                all_sprites.add(skill)
            
            elif pid == "magnus":
                # 【禁忌篇章·暴风雪】F技能：全屏冰锥雨+冻结敌人
                from utils.bullets.magnus_bullets import BlizzardSkill
                skill = BlizzardSkill(self.rect.centerx, self.rect.centery)
                all_sprites.add(skill)
            
            elif pid == "heavymetal":
                # 【死亡金属独奏】F技能：全屏音波持续伤害+敌人混乱
                from utils.bullets.heavymetal_bullets import DeathMetalSoloUlt
                style = self._get_heavymetal_style()
                skill = DeathMetalSoloUlt(self.rect.centerx, self.rect.centery, 
                                          damage=self.damage * 0.5, owner=self, style=style)
                all_sprites.add(skill)
            
            elif pid == "scarlet":
                # 【迷雾闪烁】F技能：化作红雾瞬移，过程无敌+伤害敌人
                from utils.bullets.scarlet_bullets import MistBlinkSkill
                import pygame
                mouse_pos = pygame.mouse.get_pos()
                target_y = max(100, mouse_pos[1] if mouse_pos[1] < 500 else self.rect.centery - 150)
                target_pos = (mouse_pos[0], target_y)
                style = self._get_scarlet_style() if hasattr(self, '_get_scarlet_style') else "scarlet_default"
                skill = MistBlinkSkill(self, target_pos, self.damage * 2, style=style)
                all_sprites.add(skill)
            
            elif pid == "zenith":
                # 【泰拉光束】F技能：召唤绿色泰拉刃幻影，发射全屏剑气波
                from utils.bullets.zenith_bullets import TerraBeamSkill
                style = self._get_zenith_style() if hasattr(self, '_get_zenith_style') else "zenith_default"
                skill = TerraBeamSkill(self, self.damage * 2, style=style)
                all_sprites.add(skill)
            
            elif pid == "viscerator":
                # 【推进器反转】F技能：向后释放锥形光爆，击退敌人并清弹
                from utils.bullets.viscerator_bullets import fire_reverse_thrust
                style = self._get_viscerator_style() if hasattr(self, '_get_viscerator_style') else "viscerator_default"
                fire_reverse_thrust(self.rect.centerx, self.rect.centery, self.damage * 1.5, self, style)
            
            elif pid == "crusher":
                # 【相位冲撞】F技能：向前相位冲刺，破盾+无敌+击穿敌人
                from utils.bullets.crusher_bullets import WarpDashEffect
                style = self._get_crusher_style() if hasattr(self, '_get_crusher_style') else "crusher_default"
                skill = WarpDashEffect(self, self.damage * 2, style=style)
                all_sprites.add(skill)
            
            elif pid == "sdmg":
                # 【海星雷】F技能：发射旋转海星炸弹，吸附敌人后延迟爆炸
                from utils.bullets.sdmg_bullets import StarfishMine
                style = self._get_sdmg_style() if hasattr(self, '_get_sdmg_style') else "sdmg_default"
                mine = StarfishMine(self.rect.centerx, self.rect.top, self.damage * 2, self, style)
                all_sprites.add(mine)
            
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

    def on_sdmg_overheat(self):
        """SDMG进入过热冷却时的回调"""
        if self.plane_id != "sdmg":
            return
        self.sdmg_deploy_mine_on_cooldown = True
        self.sdmg_mine_spawned_this_cooldown = False
        self.sdmg_overheat_steam_timer = 0
        FloatingText(self.rect.centerx, self.rect.top - 25, "冷却3秒", CYAN)

    def _sdmg_spawn_cooldown_mine(self):
        if self.plane_id != "sdmg" or getattr(self, 'sdmg_mine_spawned_this_cooldown', False):
            return
        from utils.bullets.sdmg_bullets import StarfishMine
        style = self._get_sdmg_style() if hasattr(self, '_get_sdmg_style') else "sdmg_default"
        StarfishMine(self.rect.centerx, self.rect.top, self.damage * 2, self, style)
        FloatingText(self.rect.centerx, self.rect.top - 45, "海星雷部署", CYAN)
        self.sdmg_mine_spawned_this_cooldown = True

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

    def gain_rift_energy(self, amount):
        """混沌虫洞射击时积累裂缝能量"""
        if self.plane_id != "wormhole":
            return
        self.rift_energy = min(self.max_rift_energy, self.rift_energy + amount)
        energy_ratio = self.rift_energy / self.max_rift_energy
        
        # 能量满时产生视觉效果
        if self.rift_energy >= self.max_rift_energy and random.random() < 0.15:
            FloatingText(self.rect.centerx, self.rect.top - 20, "⚡裂缝就绪!", (180, 0, 255))
            Particle(self.rect.center, (255, 0, 255))
        
        # 能量越高，虫洞特效越明显
        if energy_ratio > 0.5 and random.random() < 0.1:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(15, 30)
            px = self.rect.centerx + math.cos(angle) * dist
            py = self.rect.centery + math.sin(angle) * dist
            Particle((int(px), int(py)), (0, 255, 180))
    
    def _update_wormhole_state(self):
        """每帧更新虫洞状态"""
        if self.plane_id != "wormhole":
            return
        
        # 裂缝能量自然衰减（慢速）
        if self.rift_energy > 0:
            self.rift_energy = max(0, self.rift_energy - 0.3)
        
        # 更新传送冷却
        if self.rift_teleport_cooldown > 0:
            self.rift_teleport_cooldown -= 1
        
        # 清理过期虫洞
        self.rift_portals = [p for p in self.rift_portals if p.alive()]
        
        # 维度裂缝被动：高能量时随机传送敌弹
        if self.rift_energy > 70 and random.random() < 0.02:
            if enemy_bullets:
                bullet = random.choice(list(enemy_bullets))
                # 创建传送特效
                for _ in range(5):
                    Particle(bullet.rect.center, (180, 0, 255), mode='star')
                # 传送到随机位置
                bullet.rect.x = random.randint(50, WIDTH - 50)
                bullet.rect.y = random.randint(50, HEIGHT // 2)
                # 视觉反馈
                if random.random() < 0.3:
                    FloatingText(bullet.rect.centerx, bullet.rect.centery, "传送!", (255, 0, 255))

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

    def _update_sdmg_state(self):
        """每帧更新星际海豚的过热系统"""
        if self.plane_id != "sdmg":
            return
        from utils.bullets.sdmg_bullets import OverheatManager
        overheat_mgr = OverheatManager.get_instance(self)
        overheat_mgr.update()
        base_delay = getattr(self, 'sdmg_base_delay', self.plane_data["delay"])
        max_heat = max(1.0, overheat_mgr.max_heat)
        heat_ratio = overheat_mgr.heat / max_heat
        if overheat_mgr.overheated:
            self.shoot_delay = max(5, int(base_delay * 1.1))
            self.sdmg_overheat_steam_timer = getattr(self, 'sdmg_overheat_steam_timer', 0) + 1
            if self.sdmg_overheat_steam_timer % 6 == 0:
                puff = (self.rect.centerx + random.randint(-18, 18), self.rect.centery + random.randint(-10, 15))
                Particle(puff, (210, 210, 215), mode='pulse')
            if getattr(self, 'sdmg_deploy_mine_on_cooldown', False) and not getattr(self, 'sdmg_mine_spawned_this_cooldown', False):
                self._sdmg_spawn_cooldown_mine()
        elif 0.5 <= heat_ratio < 0.9:
            boosted_delay = max(5, int(base_delay * 0.7))
            self.shoot_delay = boosted_delay
            self.sdmg_deploy_mine_on_cooldown = False
            self.sdmg_mine_spawned_this_cooldown = False
            self.sdmg_overheat_steam_timer = 0
        else:
            self.shoot_delay = base_delay
            self.sdmg_deploy_mine_on_cooldown = False
            self.sdmg_mine_spawned_this_cooldown = False
            self.sdmg_overheat_steam_timer = 0

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
                "void": "虚空撕裂",
                "wormhole": "虫洞链接",
                "chronos": "现在之锁",
                "mirage": "万花镜像",
                "gambit": "骰子审判",
                "puppeteer": "命运丝网",
                "pandemic": "强制变异",
                "omega": "元素轮转",
                "genesis": "星辰陨落",
                "truth": "阴阳逆转",
                "cthulhu": "深渊触手",
                "turu": "巨石护盾",
                "staradia": "月虹轨道炮",
                "dukefishron": "深渊泡风暴",
                "slime": "星炎水晶",
                "oro": "终焉吞噬",
                "yharon": "狱炎风暴",
                "providence": "圣耀爆发",
                "goliath": "奇点坍缩",
                "sepulcher": "天降灾厄",
                "galaxia": "星系陷阱",
                "magnus": "远古之灵",
                "heavymetal": "回音墙",
                "viscerator": "粒子风暴",
                "crusher": "牵引光束"
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
            
            elif pid == "wormhole":
                # 虫洞链接：创建传送门对
                WormholeLink(self)
            
            elif pid == "chronos":
                # 【现在之锁】时间停滞：冻结敌人和子弹，创造时停领域
                ChronosPresentLock(self)
            
            elif pid == "mirage":
                # 【万花镜像】召唤万花筒镜像矩阵，折射攻击
                MirageKaleidoscope(self)
            
            elif pid == "gambit":
                # 【骰子审判】投掷巨大骰子决定敌人命运
                GambitDiceJudgment(self)
            
            elif pid == "puppeteer":
                # 【命运丝网】所有敌人连线，伤害传递
                PuppeteerFateWeb(self)
            
            elif pid == "pandemic":
                # 【强制变异】立即触发5次变异
                PandemicForceMutation(self)
            
            elif pid == "omega":
                # 【元素轮转】七属性循环攻击，每种属性附加独特效果
                OmegaElementalCycle(self)
            
            elif pid == "genesis":
                # 【星辰陨落】召唤陨石群轰炸敌人
                GenesisMeteorShower(self)
            
            elif pid == "truth":
                # 【阴阳逆转】切换阴阳极性，释放对应属性波动
                TruthYinYangReverse(self)
            
            elif pid == "asura":
                # 【怒火焚天】进入狂暴状态，全屏剑气风暴
                AsuraRageMode(self)
            
            elif pid == "dragoon":
                # 【万枪齐发】召唤无数长枪从天而降
                DragoonLanceStorm(self)
            
            elif pid == "origami":
                # 【千羽护盾】召唤1000根羽毛形成切割墙
                OrigamiFeatherShield(self)
            
            elif pid == "helios":
                # 【日冕风暴】在自身周围生成多个燃烧区
                from utils.bullets.helios_bullets import BurnZone
                for i in range(5):
                    offset_x = random.randint(-100, 100)
                    offset_y = random.randint(-80, 80)
                    zone = BurnZone(
                        self.rect.centerx + offset_x,
                        self.rect.centery + offset_y,
                        self.damage * 2,
                        duration=180
                    )
                    bullets.add(zone)
                    all_sprites.add(zone)
            
            elif pid == "frostflare":
                # 【极寒护盾】瞬间冻结周围敌人
                for enemy in mobs:
                    if hasattr(enemy, 'rect'):
                        dist = math.sqrt((enemy.rect.centerx - self.rect.centerx)**2 + 
                                        (enemy.rect.centery - self.rect.centery)**2)
                        if dist < 200:
                            enemy.frozen_timer = getattr(enemy, 'frozen_timer', 0) + 180  # 3秒冻结
                            for _ in range(5):
                                Particle(enemy.rect.center, (150, 200, 255), mode='spark')
            
            elif pid == "nova":
                # 【电磁脉冲】释放EMP波清弹并眩晕敌人
                enemy_bullets.empty()
                for enemy in mobs:
                    if hasattr(enemy, 'rect'):
                        enemy.stun_timer = getattr(enemy, 'stun_timer', 0) + 120
                        Particle(enemy.rect.center, (200, 200, 255), mode='shockwave')
                Particle(self.rect.center, (150, 180, 255), mode='shockwave')
            
            elif pid == "spectrum":
                # 【光谱增幅】临时增加攻击力，释放彩虹冲击波
                self.spectrum_amp_timer = getattr(self, 'spectrum_amp_timer', 0) + 300  # 5秒增幅
                self.spectrum_amp_mult = 1.5
                rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
                # 更多视觉效果
                for i in range(7):
                    for j in range(3):
                        Particle(self.rect.center, rainbow_colors[i], mode='spark')
                # 释放一圈彩虹子弹
                from utils.bullets.spectrum_bullets import RainbowBeam
                for i in range(14):
                    angle = i * (360 / 14) - 90
                    beam = RainbowBeam(self.rect.centerx, self.rect.centery, angle, self.damage * 1.5, i % 7, owner=self)
                    all_sprites.add(beam)
                    bullets.add(beam)
            
            elif pid == "darkstring":
                # 【死亡标记】标记所有可见敌人
                from utils.bullets.darkstring_bullets import DeathMark
                for enemy in mobs:
                    if hasattr(enemy, 'rect') and not getattr(enemy, 'death_mark', False):
                        enemy.death_mark = True
                        enemy.death_mark_timer = 300  # 5秒标记
                        mark = DeathMark(enemy)
                        all_sprites.add(mark)
            
            elif pid == "cthulhu":
                # 【深渊触手】从屏幕边缘伸出12条巨型触手抓取敌人
                from utils.bullets.cthulhu_bullets import AbyssalTentacles
                AbyssalTentacles(self)
            
            elif pid == "turu":
                # 【巨石护盾】展开环形岩壁抵挡弹幕
                from utils.bullets.turu_bullets import RockShield
                RockShield(self)
            
            elif pid == "staradia":
                # 【月虹轨道炮】全屏彩虹光柱贯穿
                from utils.bullets.staradia_bullets import MoonRainbowRail
                style = self._get_staradia_style()
                rail = MoonRainbowRail(self.rect.centerx, self.rect.centery, owner=self, style=style)
                all_sprites.add(rail)
            
            elif pid == "dukefishron":
                # 【深渊泡风暴】减速区域+追踪弹
                from utils.bullets.dukefishron_bullets import AbyssBubbleStorm
                style = self._get_duke_style()
                storm = AbyssBubbleStorm(self.rect.centerx, self.rect.centery - 100, 
                                        owner=self, style=style)
                all_sprites.add(storm)
            
            elif pid == "slime":
                # 【星炎水晶】发射追踪水晶弹，延迟追踪后加速冲刺（参考Aureus星炎水晶）
                from utils.bullets.slime_bullets import AstralCrystalSkill
                style = self._get_slime_style()
                skill = AstralCrystalSkill(self.rect.centerx, self.rect.centery, owner=self, style=style)
                all_sprites.add(skill)
            
            elif pid == "oro":
                # 【弑神冲袭·现实撕裂】G技能：极速Z字冲撞，无敌状态，留下时空裂痕
                from utils.bullets.oro_bullets import GodSlayerSkill
                style = self._get_oro_style()
                skill = GodSlayerSkill(self.rect.centerx, self.rect.centery, self.damage * 5, owner=self, style=style)
                all_sprites.add(skill)
            
            elif pid == "yharon":
                # 【龙群盛宴】G技能：召唤两只机械大黄蜂僚机
                from utils.bullets.yharon_bullets import DraconicSwarmSkill
                style = self._get_yharon_style()
                skill = DraconicSwarmSkill(self.rect.centerx, self.rect.centery, self.damage * 2, owner=self, style=style)
                all_sprites.add(skill)
            
            elif pid == "providence":
                # 【神圣射线】G技能：扇形扫射激光
                from utils.bullets.providence_bullets import create_holy_ray
                style = self._get_providence_style()
                skill = create_holy_ray(self, self.damage * 2, style)
            
            elif pid == "goliath":
                # 【瘟疫核弹】G技能：投下巨型核弹，蘑菇云清屏
                from utils.bullets.goliath_bullets import PlagueNukeSkill
                style = self._get_goliath_style()
                skill = PlagueNukeSkill(owner=self, damage=self.damage * 4, style=style)
                all_sprites.add(skill)
            
            elif pid == "sepulcher":
                # 【天降灾厄】G技能：硫磺火球暴雨全屏轰炸
                from utils.bullets.sepulcher_bullets import RainOfCalamitySkill
                style = self._get_sepulcher_style()
                skill = RainOfCalamitySkill(owner=self, damage=self.damage * 2.5, style=style)
                if not hasattr(self, 'sepulcher_active_skills'):
                    self.sepulcher_active_skills = []
                self.sepulcher_active_skills.append(skill)
            
            elif pid == "galaxia":
                # 【星系陷阱】G技能：剪刀旋转+引力+星座弹幕
                from utils.bullets.galaxia_bullets import GalaxyTrapSkill
                style = self._get_galaxia_style()
                skill = GalaxyTrapSkill(self.rect.centerx, self.rect.centery,
                                       self.damage * 2, style=style)
                all_sprites.add(skill)
            
            elif pid == "magnus":
                # 【召唤·远古之灵】G技能：召唤巨大骷髅头冲撞全场
                from utils.bullets.magnus_bullets import AncientSpiritSkill
                skill = AncientSpiritSkill(self.rect.centerx, self.rect.centery)
                all_sprites.add(skill)
            
            elif pid == "heavymetal":
                # 【回音墙】G技能：多层声波护盾，反弹子弹+持续伤害
                from utils.bullets.heavymetal_bullets import EchoWallSkill
                style = self._get_heavymetal_style()
                skill = EchoWallSkill(self.rect.centerx, self.rect.centery,
                                     damage=self.damage * 2, owner=self, style=style)
                all_sprites.add(skill)
            
            elif pid == "scarlet":
                # 【绯红不夜城】G技能：东方弹幕风格高密度规则弹幕覆盖全屏
                from utils.bullets.scarlet_bullets import ScarletMeisterSkill
                style = self._get_scarlet_style() if hasattr(self, '_get_scarlet_style') else "scarlet_default"
                skill = ScarletMeisterSkill(self.rect.centerx, self.rect.centery,
                                           damage=self.damage * 1.5, owner=self, style=style)
                all_sprites.add(skill)
            
            elif pid == "zenith":
                # 【喵星人轰炸】G技能：召唤大量彩虹猫头疯狂反弹
                from utils.bullets.zenith_bullets import MeowmereBombSkill
                style = self._get_zenith_style() if hasattr(self, '_get_zenith_style') else "zenith_default"
                skill = MeowmereBombSkill(self, self.damage * 1.5, style=style)
                all_sprites.add(skill)
            
            elif pid == "viscerator":
                # 【粒子风暴】G技能：12方向粉绿双色高速粒子扩散
                from utils.bullets.viscerator_bullets import fire_focus_beam
                style = self._get_viscerator_style() if hasattr(self, '_get_viscerator_style') else "viscerator_default"
                fire_focus_beam(self.rect.centerx, self.rect.top, self.damage * 2, self, style)
            
            elif pid == "crusher":
                # 【牵引光束】G技能：扇形牵引波，将敌人拉向玩家并减速
                from utils.bullets.crusher_bullets import TractorBeamEffect
                style = self._get_crusher_style() if hasattr(self, '_get_crusher_style') else "crusher_default"
                skill = TractorBeamEffect(self, self.damage * 1.5, style=style)
                all_sprites.add(skill)
            
            elif pid == "sdmg":
                # 【鲨卷风】G技能：发射数十枚鲨鱼导弹，形成龙卷风轨迹
                from utils.bullets.sdmg_bullets import SharknadoSkill
                style = self._get_sdmg_style() if hasattr(self, '_get_sdmg_style') else "sdmg_default"
                SharknadoSkill.activate(self, style)
                FloatingText(self.rect.centerx, self.rect.top - 50, "★ 鲨卷风 ★", (192, 192, 192))
            
            else:
                # 通用：清弹
                enemy_bullets.empty()
                for _ in range(8):
                    Particle(self.rect.center, self.plane_data["color"], mode='shockwave')

    def use_tertiary_ultimate(self):
        """第三大招（C键释放）"""
        pid = self.plane_id
        
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
                "void": "等离子漩涡",
                "wormhole": "时空逆流",
                "chronos": "未来之视",
                "mirage": "虚实颠倒",
                "gambit": "全押梭哈",
                "puppeteer": "傀儡剧场",
                "pandemic": "终末审判",
                "omega": "属性共鸣",
                "genesis": "新星诞生",
                "truth": "绝对审判",
                "asura": "斩龙绝杀",
                "dragoon": "龙魂冲锋",
                "origami": "千羽护盾",
                "helios": "太阳坠落",
                "frostflare": "绝对零度",
                "nova": "轨道炮击",
                "spectrum": "虹光终焉",
                "darkstring": "命运终结",
                "cthulhu": "疯狂领域",
                "turu": "图鲁跃砸",
                "staradia": "皇辉领域",
                "dukefishron": "龙鱼海啸",
                "slime": "星凝子体",
                "oro": "灭世之环",
                "yharon": "地狱风暴",
                "providence": "圣光净化",
                "goliath": "终极爆破",
                "sepulcher": "硫火审判",
                "galaxia": "苍穹撕裂",
                "magnus": "真理之圆",
                "heavymetal": "地狱开场",
                "scarlet": "命运之枪",
                "zenith": "天顶霸主",
                "viscerator": "星流过载",
                "crusher": "共振破碎"
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
            
            elif pid == "wormhole":
                # 时空逆流：时空倒流
                TimeReversal(self)
            
            elif pid == "chronos":
                # 【未来之视】预知未来：显示敌人轨迹，自动瞄准，增加伤害
                ChronosFutureVision(self)
            
            elif pid == "mirage":
                # 【虚实颠倒】与分身交换位置，分身爆炸
                MirageRealitySwap(self)
            
            elif pid == "gambit":
                # 【全押梭哈】把所有运气值押注，触发超级效果
                GambitAllIn(self)
            
            elif pid == "puppeteer":
                # 【傀儡剧场】召唤击杀过的精英敌人复制体为你战斗
                PuppeteerPuppetTheater(self)
            
            elif pid == "pandemic":
                # 【终末审判】所有感染敌人的潜伏伤害立即爆发，爆发伤害+200%
                PandemicFinalJudgment(self)
            
            elif pid == "omega":
                # 【属性共鸣】七属性同时爆发环形冲击波
                OmegaElementalResonance(self)
            
            elif pid == "genesis":
                # 【新星诞生】在敌人位置创造超新星爆炸
                GenesisSupernovaBlast(self)
            
            elif pid == "truth":
                # 【绝对审判】对所有标记敌人执行真理裁决
                TruthAbsoluteJudgment(self)
            
            elif pid == "asura":
                # 【斩龙绝杀】汇聚所有剑意进行一击必杀
                AsuraDragonSlayer(self)
            
            elif pid == "dragoon":
                # 【龙魂冲锋】化身巨龙进行贯穿冲锋
                DragoonDragonCharge(self)
            
            elif pid == "origami":
                # 【千羽护盾】召唤纸鹤护盾反弹子弹
                OrigamiFeatherShield(self)
            
            elif pid == "helios":
                # 【太阳坠落】召唤巨型陨石从天而降
                from utils.bullets.helios_bullets import SunFall
                SunFall(self)
            
            elif pid == "frostflare":
                # 【绝对零度】全屏冻结所有敌人
                from utils.bullets.frostflare_bullets import AbsoluteZero
                AbsoluteZero(self)
            
            elif pid == "nova":
                # 【轨道炮击】召唤卫星轨道炮轰炸
                from utils.bullets.nova_bullets import OrbitalStrike
                OrbitalStrike(self)
            
            elif pid == "spectrum":
                # 【虹光终焉】释放全屏彩虹爆发
                from utils.bullets.spectrum_bullets import RainbowApocalypse
                RainbowApocalypse(self)
            
            elif pid == "darkstring":
                # 【命运终结】所有标记敌人立即死亡
                from utils.bullets.darkstring_bullets import FateEnder
                FateEnder(self)
            
            elif pid == "cthulhu":
                # 【疯狂领域】释放精神污染波动，敌人SAN值归零后混乱
                from utils.bullets.cthulhu_bullets import MadnessAura
                MadnessAura(self)
            
            elif pid == "turu":
                # 【图鲁跃砸】远程定位跳跃砸地，震荡波击飞+减速
                from utils.bullets.turu_bullets import TuruLeapSlam
                TuruLeapSlam(self)
            
            elif pid == "staradia":
                # 【皇辉领域】C技能正常充能，皇辉层数提供伤害加成
                from utils.bullets.staradia_bullets import RadiantDomain
                style = self._get_staradia_style()
                domain = RadiantDomain(self.rect.centerx, self.rect.centery, owner=self, style=style)
                all_sprites.add(domain)
                self.radiant_domain_timer = 360  # 6秒领域持续
            
            elif pid == "dukefishron":
                # 【龙鱼海啸】3屏滑翔+海啸墙
                from utils.bullets.dukefishron_bullets import DragonFishTsunami
                style = self._get_duke_style()
                tsunami = DragonFishTsunami(owner=self, style=style)
                all_sprites.add(tsunami)
            
            elif pid == "slime":
                # 【星凝子体】传送+召唤自爆子体（参考Aureus Spawn）
                from utils.bullets.slime_bullets import AureusSpawnSkill
                style = self._get_slime_style()
                skill = AureusSpawnSkill(self.rect.centerx, self.rect.centery, owner=self, style=style)
                all_sprites.add(skill)
            
            elif pid == "oro":
                # 【视界线·衬尾蛇】C技能：螺旋形成光环，中心擕开微型黑洞吞噬一切
                from utils.bullets.oro_bullets import OuroborosSkill
                style = self._get_oro_style()
                skill = OuroborosSkill(self.rect.centerx, self.rect.centery, self.damage * 4, owner=self, style=style)
                all_sprites.add(skill)
            
            elif pid == "yharon":
                # 【魔君之证·宿敌升天】C技能：巨龙笼罩，天降地狱火柱
                from utils.bullets.yharon_bullets import EnemyAscendedSkill
                style = self._get_yharon_style()
                skill = EnemyAscendedSkill(self.rect.centerx, self.rect.centery, self.damage * 4, owner=self, style=style)
                all_sprites.add(skill)
            
            elif pid == "providence":
                # 【超新星爆发】C技能：360度星辰弹幕+时停效果
                from utils.bullets.providence_bullets import create_supernova
                style = self._get_providence_style()
                skill = create_supernova(self, self.damage * 3, style)
            
            elif pid == "goliath":
                # 【盖亚之死】C技能：15秒废土领域，敌人HP上限-50%+大幅减速
                from utils.bullets.goliath_bullets import DeathOfGaiaSkill
                style = self._get_goliath_style()
                skill = DeathOfGaiaSkill(owner=self, damage=self.damage * 3, style=style)
                all_sprites.add(skill)
            
            elif pid == "sepulcher":
                # 【湮灭之眼】C技能：1/3屏宽毁灭光束持续5秒
                from utils.bullets.sepulcher_bullets import EyeOfOblivionSkill
                style = self._get_sepulcher_style()
                skill = EyeOfOblivionSkill(owner=self, damage=self.damage * 5, style=style)
                if not hasattr(self, 'sepulcher_active_skills'):
                    self.sepulcher_active_skills = []
                self.sepulcher_active_skills.append(skill)
            
            elif pid == "galaxia":
                # 【苍穹撕裂】C技能：巨型剪刀撕裂屏幕+星辰喷发
                from utils.bullets.galaxia_bullets import BigRipSkill
                style = self._get_galaxia_style()
                skill = BigRipSkill(self.rect.centerx, self.rect.centery,
                                   self.damage * 3, style=style)
                all_sprites.add(skill)
            
            elif pid == "magnus":
                # 【真理之圆】C技能：最终魔法阵持续灼烧+定身
                from utils.bullets.magnus_bullets import CircleOfTruthSkill
                skill = CircleOfTruthSkill(self.rect.centerx, self.rect.centery)
                all_sprites.add(skill)
            
            elif pid == "heavymetal":
                # 【地狱开场】C技能：全屏火焰+烟火+音波大爆炸
                from utils.bullets.heavymetal_bullets import HellishOpenerSkill
                style = self._get_heavymetal_style()
                skill = HellishOpenerSkill(self.rect.centerx, self.rect.centery,
                                          damage=self.damage * 3, owner=self, style=style)
                all_sprites.add(skill)
            
            elif pid == "scarlet":
                # 【命运之枪】C技能：投掷贯穿全屏的巨大红色光枪
                from utils.bullets.scarlet_bullets import GungnirSpearSkill
                style = self._get_scarlet_style() if hasattr(self, '_get_scarlet_style') else "scarlet_default"
                skill = GungnirSpearSkill(self.rect.centerx, self.rect.centery,
                                         damage=self.damage * 4, owner=self, style=style)
                all_sprites.add(skill)
                FloatingText(self.rect.centerx, self.rect.top - 50, "★ 命运之枪 ★", (220, 20, 60))
            
            elif pid == "zenith":
                # 【天顶霸主】C技能：所有剑以鬼畜速度全屏乱舞
                from utils.bullets.zenith_bullets import ZenithOverdriveSkill
                style = self._get_zenith_style() if hasattr(self, '_get_zenith_style') else "zenith_default"
                skill = ZenithOverdriveSkill(self, self.damage * 2, style=style)
                all_sprites.add(skill)
                FloatingText(self.rect.centerx, self.rect.top - 50, "★ 天顶霸主 ★", (75, 0, 130))
            
            elif pid == "viscerator":
                # 【星流过载】C技能：召唤环绕棱镜，自动发射追踪激光
                from utils.bullets.viscerator_bullets import create_exo_overload
                style = self._get_viscerator_style() if hasattr(self, '_get_viscerator_style') else "viscerator_default"
                create_exo_overload(self, self.damage * 1.5, style)
                FloatingText(self.rect.centerx, self.rect.top - 50, "★ 星流过载 ★", (255, 20, 147))
            
            elif pid == "crusher":
                # 【共振破碎】C技能：全屏晶体震爆，伤害所有敌人+清除敌弹
                from utils.bullets.crusher_bullets import ResonanceBreakEffect
                style = self._get_crusher_style() if hasattr(self, '_get_crusher_style') else "crusher_default"
                skill = ResonanceBreakEffect(self, self.damage * 3, style=style)
                all_sprites.add(skill)
                FloatingText(self.rect.centerx, self.rect.top - 50, "★ 共振破碎 ★", (138, 43, 226))
            
            elif pid == "sdmg":
                # 【月球领主之凝视】C技能：召唤幻影手掌跟随，持续发射穿透光球
                from utils.bullets.sdmg_bullets import MoonLordGazeSkill
                style = self._get_sdmg_style() if hasattr(self, '_get_sdmg_style') else "sdmg_default"
                MoonLordGazeSkill.activate(self, style)
                FloatingText(self.rect.centerx, self.rect.top - 50, "★ 月球领主之凝视 ★", (100, 255, 200))
            
            else:
                # 通用：全屏伤害
                for m in list(mobs):
                    m.hp -= 100
                    Particle(m.rect.center, self.plane_data["color"], mode='shockwave')

    def use_quaternary_ultimate(self):
        """第四大招（E键释放）"""
        pid = self.plane_id
        
        # 冷却检查
        if self.ult4_cooldown > 0:
            return
        
        if self.ult4_charge >= self.max_ult4_charge:
            self.ult4_charge = 0  # 消耗全部能量
            self.ult4_cooldown = self.ult4_max_cooldown
            
            sound_mgr.play("laser")
            
            if pid == "scarlet":
                # 【深红世界】E技能（终极大招）：时间停止+影分身斜击所有敌人
                from utils.bullets.scarlet_bullets import CrimsonWorldUltimate
                style = self._get_scarlet_style() if hasattr(self, '_get_scarlet_style') else "scarlet_default"
                skill = CrimsonWorldUltimate(owner=self, damage=self.damage * 5)
                all_sprites.add(skill)
                FloatingText(self.rect.centerx, self.rect.top - 50, "★ 深红世界 ★", (255, 50, 80))
            
            elif pid == "zenith":
                # 【棱镜折射】E技能（蓄力终极）：所有剑合体成巨剑劈砍
                from utils.bullets.zenith_bullets import PrismBreakSkill
                style = self._get_zenith_style() if hasattr(self, '_get_zenith_style') else "zenith_default"
                skill = PrismBreakSkill(self, self.damage * 5, style=style)
                all_sprites.add(skill)
                FloatingText(self.rect.centerx, self.rect.top - 50, "★ 棱镜折射 ★", (255, 0, 255))
            
            elif pid == "viscerator":
                # 【光子湮灭】R技能（终极大招）：交叉激光雨 + 中心爆炸
                from utils.bullets.viscerator_bullets import fire_light_of_destruction
                style = self._get_viscerator_style() if hasattr(self, '_get_viscerator_style') else "viscerator_default"
                fire_light_of_destruction(self, self.damage * 4, style)
                FloatingText(self.rect.centerx, self.rect.top - 50, "★ 光子湮灭 ★", (255, 20, 147))
            
            elif pid == "crusher":
                # 【核心过载】R技能（终极大招）：释放积累的护甲能量，巨型钻头冲击波
                from utils.bullets.crusher_bullets import CoreMeltdownEffect
                style = self._get_crusher_style() if hasattr(self, '_get_crusher_style') else "crusher_default"
                armor_stacks = getattr(self, 'crusher_armor_stacks', 0)
                skill = CoreMeltdownEffect(self, self.damage * 5, style=style, armor_stacks=armor_stacks)
                all_sprites.add(skill)
                # 消耗所有护甲层数
                self.crusher_armor_stacks = 0
                FloatingText(self.rect.centerx, self.rect.top - 50, "★ 次元坍缩 ★", (138, 43, 226))
            
            elif pid == "sdmg":
                # 【轨道轰炸】R技能（终极大招）：卫星激光从天而降，扫荡全屏
                from utils.bullets.sdmg_bullets import OrbitalStrikeSkill
                style = self._get_sdmg_style() if hasattr(self, '_get_sdmg_style') else "sdmg_default"
                OrbitalStrikeSkill.activate(self, style)
                FloatingText(self.rect.centerx, self.rect.top - 50, "★ 轨道轰炸 ★", (255, 200, 100))
            
            else:
                # 通用：冲刺攻击
                for m in list(mobs):
                    if hasattr(m, 'hp'):
                        m.hp -= 50
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

        # 【新】从玩家属性读取弹跳参数
        player_bounce = getattr(self, 'bounce_count', 0)
        player_bounce_damage = getattr(self, 'bounce_damage', 1.0)

        # 计算追踪等级加成
        if w_type == "missile": h_lvl += 5
        elif w_type == "arc": h_lvl += 3
        elif w_type == "swarm": h_lvl += 8

        # --- 发射逻辑移植 ---
        if w_type == "cannon":
            Bullet(x, y, color=color, b_type="needle", homing=h_lvl, bounce=player_bounce, bounce_damage=player_bounce_damage)
            sound_mgr.play("shoot")
        elif w_type == "beam":
            Bullet(x, y, color=color, b_type="beam", homing=h_lvl, bounce=player_bounce, bounce_damage=player_bounce_damage)
        elif w_type == "explosive":
            b = Bullet(x, y, color=color, b_type="plasma", homing=h_lvl, bounce=player_bounce, bounce_damage=player_bounce_damage)
            b.speed = -6
        elif w_type == "missile":
            Bullet(x, y, homing=h_lvl, color=color, b_type="rocket", bounce=player_bounce, bounce_damage=player_bounce_damage)
            sound_mgr.play("shoot")
        elif w_type == "exotic":
            for i in range(0, 360, 45): 
                Bullet(x, y, angle=i, color=color, b_type="star", homing=h_lvl, bounce=player_bounce, bounce_damage=player_bounce_damage)
            sound_mgr.play("zap")
        elif w_type == "scatter":
            sound_mgr.play("shoot")
            for i in range(-2, 3):
                b = Bullet(x, y, angle=i*10, color=color, b_type="shard", homing=h_lvl, bounce=player_bounce, bounce_damage=player_bounce_damage)
                b.speed = -10
        elif w_type == "arc":
            sound_mgr.play("zap")
            Bullet(x, y, homing=h_lvl, color=color, b_type="lightning", bounce=player_bounce, bounce_damage=player_bounce_damage)
        elif w_type == "sniper":
            sound_mgr.play("sniper_charge")
            b = Bullet(x, y, color=color, b_type="needle", piercing=999, homing=h_lvl, bounce=player_bounce, bounce_damage=player_bounce_damage)
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
            b = Bullet(x, y, color=color, b_type="beam", piercing=999, bounce=player_bounce, bounce_damage=player_bounce_damage)
            b.speed = -40
        elif w_type == "void":
            b = Bullet(x, y, color=color, b_type="orb", piercing=10, bounce=player_bounce, bounce_damage=player_bounce_damage)
            b.speed = -3
            sound_mgr.play("blackhole")
        elif w_type == "frost":
            Bullet(x, y, color=color, b_type="shard", homing=h_lvl, bounce=player_bounce, bounce_damage=player_bounce_damage)
            sound_mgr.play("shoot")
        elif w_type == "swarm":
            sound_mgr.play("shoot")
            for i in range(8):
                angle = random.randint(-45, 45)
                b = Bullet(x, y, angle=angle, color=color, b_type="rocket", homing=h_lvl, bounce=player_bounce, bounce_damage=player_bounce_damage)
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
        # ========== 【星轨天赋阵】闪避判定 ==========
        if hasattr(self, 'talent_dodge_chance') and self.talent_dodge_chance > 0:
            if random.random() < self.talent_dodge_chance:
                # 闪避成功
                FloatingText(self.rect.centerx, self.rect.centery - 20, "闪避!", (150, 200, 255))
                # 闪避后无敌效果
                if hasattr(self, 'talent_dodge_invuln') and self.talent_dodge_invuln > 0:
                    self.overdrive_timer = max(self.overdrive_timer, int(self.talent_dodge_invuln * 60))
                return self.hp
        
        # ========== 【星轨天赋阵】减伤计算 ==========
        talent_reduction = 0
        # 低血量减伤
        if hasattr(self, 'talent_low_hp_reduction') and self.talent_low_hp_reduction > 0:
            if self.hp / self.max_hp < 0.25:
                talent_reduction += self.talent_low_hp_reduction
        # 满护盾减伤
        if hasattr(self, 'talent_full_shield_reduction') and self.talent_full_shield_reduction > 0:
            if self.max_shield > 0 and self.shield >= self.max_shield:
                talent_reduction += self.talent_full_shield_reduction
        
        # 应用天赋减伤
        if talent_reduction > 0:
            amount = amount * (1 - min(0.8, talent_reduction))  # 最大80%减伤
        
        # CRUSHER特殊机制：撞击护甲（受到伤害时积累层数，减少受到的伤害）
        if hasattr(self, 'plane_id') and self.plane_id == "crusher":
            # 确保护甲系统已初始化
            if not hasattr(self, 'crusher_initialized') or not self.crusher_initialized:
                self.crusher_armor_stacks = 0
                self.crusher_max_armor = 20  # 最大20层
                self.crusher_initialized = True
            
            # 每次受击增加1层护甲
            if self.crusher_armor_stacks < self.crusher_max_armor:
                self.crusher_armor_stacks += 1
                # 显示护甲增加提示
                if self.crusher_armor_stacks % 5 == 0:  # 每5层显示一次
                    FloatingText(self.rect.centerx, self.rect.centery - 20, 
                               f"晶甲+{self.crusher_armor_stacks}", (138, 43, 226))
            
            # 每层护甲减少2%伤害
            armor_reduction = self.crusher_armor_stacks * 0.02
            amount = amount * (1 - armor_reduction)
        
        # 装甲减伤
        reduced = amount * (1 - self.damage_reduction)
        
        # 先扣护盾
        if self.shield > 0:
            shield_absorb = min(self.shield, reduced)
            self.shield -= shield_absorb
            reduced -= shield_absorb
            
            # ========== 【星轨天赋阵】护盾反弹伤害 ==========
            if hasattr(self, 'talent_shield_reflect') and self.talent_shield_reflect > 0:
                reflect_damage = shield_absorb * self.talent_shield_reflect
                if reflect_damage > 0:
                    # 创建反弹伤害效果（在后续调用位置处理）
                    if not hasattr(self, 'pending_reflect_damage'):
                        self.pending_reflect_damage = 0
                    self.pending_reflect_damage += reflect_damage
        
        # ========== 【星轨天赋阵】被击后移速加成 ==========
        if hasattr(self, 'talent_hit_speed_boost') and self.talent_hit_speed_boost > 0:
            self.talent_hit_speed_timer = 120  # 2秒
            speed_bonus = self.talent_effects.get("move_speed", 0)
            self.speed = self.base_speed * (1 + speed_bonus + self.talent_hit_speed_boost)
        
        # ========== 【星轨天赋阵】守护终极：不朽堡垒 ==========
        if hasattr(self, 'ultimate_guardian_death_save') and self.ultimate_guardian_death_save:
            if self.hp - reduced <= 0 and not hasattr(self, '_death_save_used'):
                self._death_save_used = True
                self.hp = 1
                self.overdrive_timer = 180  # 3秒无敌
                FloatingText(self.rect.centerx, self.rect.centery, "不朽堡垒!", CYAN)
                return 1
        
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
        # ========== 【星轨天赋阵】击杀效果 ==========
        # 击杀回复生命
        if hasattr(self, 'talent_kill_heal') and self.talent_kill_heal > 0:
            heal = int(self.max_hp * self.talent_kill_heal)
            if heal > 0 and self.hp < self.max_hp:
                self.hp = min(self.max_hp, self.hp + heal)
                FloatingText(self.rect.centerx, self.rect.top - 20, f"+{heal}", (100, 255, 150))
        
        # 击杀回复能量（大招能量）
        if hasattr(self, 'talent_kill_energy') and self.talent_kill_energy > 0:
            energy = int(self.max_ult_charge * self.talent_kill_energy)
            if energy > 0:
                self.ult_charge = min(self.max_ult_charge, self.ult_charge + energy)
                # 也给副大招充能
                self.ult2_charge = min(self.max_ult2_charge, self.ult2_charge + energy // 2)
        
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


# ==================== Chronos时间系大招 ====================

class ChronosPastShadow(pygame.sprite.Sprite):
    """【过去之影】时间回溯 - Q键主大招
    回到3秒前的位置和状态，恢复HP，清除debuff，获得3秒无敌"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180  # 特效持续3秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("blackhole")
        
        # 回溯效果
        self.rewind_active = True
        self.owner.chronos_rewinding = True
        self.owner.chronos_rewind_timer = 180
        
        # 读取历史记录
        if len(self.owner.chronos_position_history) > 0:
            # 获取3秒前的状态（180帧前）
            past_state = self.owner.chronos_position_history[0]
            self.past_pos = past_state.get('pos', (self.owner.rect.centerx, self.owner.rect.centery))
            self.past_hp = past_state.get('hp', self.owner.hp)
            
            # 保存当前位置用于轨迹显示
            self.current_pos = (self.owner.rect.centerx, self.owner.rect.centery)
            
            # 执行回溯
            self.owner.rect.center = self.past_pos
            self.owner.hp = min(self.past_hp + 50, self.owner.max_hp)  # 额外恢复50HP
            
            # 清除所有敌方子弹
            enemy_bullets.empty()
            
            # 无敌时间
            self.owner.invincible_timer = 180  # 3秒无敌
            
            # 时间回响层数+2
            self.owner.chronos_echo_stacks = min(
                self.owner.chronos_echo_stacks + 2,
                self.owner.max_chronos_echoes
            )
            
            FloatingText(WIDTH // 2, HEIGHT // 2 - 100, "⏪ 时间回溯！", (100, 220, 255))
        else:
            # 没有历史记录，只提供基础效果
            self.past_pos = (self.owner.rect.centerx, self.owner.rect.centery)
            self.current_pos = self.past_pos
            self.owner.hp = min(self.owner.hp + 50, self.owner.max_hp)
            self.owner.invincible_timer = 120
            FloatingText(WIDTH // 2, HEIGHT // 2 - 100, "⏪ 时光治愈！", (100, 220, 255))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.owner.chronos_rewinding = False
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        # 时钟倒转特效
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        
        # 大时钟外圈
        clock_radius = 150 + abs(math.sin(self.life * 0.05)) * 30
        pygame.draw.circle(self.image, (100, 220, 255), (center_x, center_y), int(clock_radius), 4)
        pygame.draw.circle(self.image, (50, 180, 255), (center_x, center_y), int(clock_radius - 10), 2)
        
        # 逆时针旋转的时针
        angle = -(self.life * 0.15)  # 逆时针
        hand_len = clock_radius - 20
        end_x = center_x + math.cos(angle) * hand_len
        end_y = center_y + math.sin(angle) * hand_len
        pygame.draw.line(self.image, (255, 200, 100), (center_x, center_y), (end_x, end_y), 8)
        
        # 时间粒子回流
        particle_count = 30
        for i in range(particle_count):
            progress = (self.life * 0.02 + i * 0.1) % 1.0
            particle_angle = i * (360 / particle_count) * 0.01745
            particle_dist = 200 * (1 - progress)  # 向中心收缩
            px = center_x + math.cos(particle_angle) * particle_dist
            py = center_y + math.sin(particle_angle) * particle_dist
            particle_size = int(8 * progress)
            if particle_size > 0:
                pygame.draw.circle(self.image, (100, 220, 255), (int(px), int(py)), particle_size)
        
        # 历史轨迹显示
        if hasattr(self, 'past_pos') and hasattr(self, 'current_pos'):
            pygame.draw.line(self.image, (255, 200, 100, 150), self.current_pos, self.past_pos, 3)


class ChronosPresentLock(pygame.sprite.Sprite):
    """【现在之锁】时间停滞 - G键第二大招
    冻结敌人和子弹5秒，创造时停领域，玩家攻速+100%"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 300  # 持续5秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.frozen_enemies = []
        self.frozen_bullets = []
        sound_mgr.play("zap")
        
        # 冻结所有敌人和子弹
        for m in mobs:
            if not hasattr(m, 'time_frozen'):
                m.time_frozen = True
                m.frozen_timer = 300
                self.frozen_enemies.append(m)
        
        for eb in enemy_bullets:
            if not hasattr(eb, 'time_frozen'):
                eb.time_frozen = True
                eb.frozen_timer = 300
                self.frozen_bullets.append(eb)
        
        # 玩家攻速加倍
        self.owner.shoot_delay_backup = self.owner.shoot_delay
        self.owner.shoot_delay = self.owner.shoot_delay // 2
        
        # 时间回响层数+1
        self.owner.chronos_echo_stacks = min(
            self.owner.chronos_echo_stacks + 1,
            self.owner.max_chronos_echoes
        )
        
        FloatingText(WIDTH // 2, HEIGHT // 2 - 100, "⏸ 时间停滞！", (255, 200, 100))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            # 解除冻结
            for m in self.frozen_enemies:
                if hasattr(m, 'time_frozen'):
                    m.time_frozen = False
            for eb in self.frozen_bullets:
                if hasattr(eb, 'time_frozen'):
                    eb.time_frozen = False
            
            # 恢复攻速
            if hasattr(self.owner, 'shoot_delay_backup'):
                self.owner.shoot_delay = self.owner.shoot_delay_backup
            
            FloatingText(WIDTH // 2, HEIGHT // 2 - 100, "▶ 时间恢复", (150, 200, 255))
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        # 时停领域特效
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        
        # 扩散的时停波纹
        for ring in range(5):
            ring_progress = (self.life * 0.03 + ring * 0.2) % 1.0
            ring_radius = int(100 + ring_progress * 300)
            ring_alpha = int(120 * (1 - ring_progress))
            if ring_alpha > 0:
                pygame.draw.circle(self.image, (255, 200, 100, ring_alpha), 
                                 (center_x, center_y), ring_radius, 3)
        
        # 时钟刻度环
        clock_radius = 200
        for hour in range(12):
            angle = (hour * 30 - 90) * 0.01745
            tick_len = 15 if hour % 3 == 0 else 10
            outer_x = center_x + math.cos(angle) * clock_radius
            outer_y = center_y + math.sin(angle) * clock_radius
            inner_x = center_x + math.cos(angle) * (clock_radius - tick_len)
            inner_y = center_y + math.sin(angle) * (clock_radius - tick_len)
            pygame.draw.line(self.image, (255, 200, 100), 
                           (outer_x, outer_y), (inner_x, inner_y), 3)
        
        # 冻结粒子效果
        if self.life % 3 == 0:
            for m in self.frozen_enemies[:5]:  # 只显示前5个
                if m in mobs:
                    Particle(m.rect.center, (200, 240, 255), mode='star')


class ChronosFutureVision(pygame.sprite.Sprite):
    """【未来之视】预知未来 - C键第三大招
    显示敌人3秒后轨迹，自动瞄准，全伤害+50%，持续8秒"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 480  # 持续8秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.predicted_paths = {}
        sound_mgr.play("laser")
        
        # 伤害增幅
        self.owner.future_vision_active = True
        self.owner.damage_backup = self.owner.damage
        self.owner.damage = int(self.owner.damage * 1.5)
        
        # 预测所有敌人的轨迹
        for m in mobs:
            if hasattr(m, 'rect'):
                # 简单预测：基于当前速度外推
                predicted_points = []
                current_x, current_y = m.rect.centerx, m.rect.centery
                
                for frame in range(60):  # 预测1秒
                    # 假设敌人直线移动
                    future_x = current_x
                    future_y = current_y + frame * 2  # 假设向下移动
                    predicted_points.append((int(future_x), int(future_y)))
                
                self.predicted_paths[id(m)] = predicted_points
        
        # 时间回响层数+1
        self.owner.chronos_echo_stacks = min(
            self.owner.chronos_echo_stacks + 1,
            self.owner.max_chronos_echoes
        )
        
        FloatingText(WIDTH // 2, HEIGHT // 2 - 100, "⏩ 预知未来！", (255, 255, 100))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            # 取消效果
            self.owner.future_vision_active = False
            if hasattr(self.owner, 'damage_backup'):
                self.owner.damage = self.owner.damage_backup
            
            FloatingText(WIDTH // 2, HEIGHT // 2 - 100, "⏺ 未来收束", (180, 180, 255))
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        # 绘制预测轨迹
        for mob_id, path in list(self.predicted_paths.items()):
            # 检查敌人是否还存在
            mob_exists = any(id(m) == mob_id for m in mobs)
            if not mob_exists:
                continue
            
            # 绘制虚线轨迹
            if len(path) > 1:
                for i in range(0, len(path) - 1, 3):  # 虚线效果
                    if i + 1 < len(path):
                        pygame.draw.line(self.image, (255, 255, 100, 100), 
                                       path[i], path[i + 1], 2)
        
        # 未来之眼特效
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        
        # 三角形眼睛
        eye_size = 60 + abs(math.sin(self.life * 0.1)) * 20
        eye_points = [
            (center_x, center_y - eye_size),
            (center_x - eye_size * 0.866, center_y + eye_size * 0.5),
            (center_x + eye_size * 0.866, center_y + eye_size * 0.5)
        ]
        pygame.draw.polygon(self.image, (255, 255, 100), eye_points, 3)
        
        # 眼睛中心
        pygame.draw.circle(self.image, (255, 255, 200), (center_x, center_y), 15)
        pygame.draw.circle(self.image, (100, 100, 50), (center_x, center_y), 8)
        
        # 视线扫描线
        scan_angle = self.life * 0.1
        for i in range(3):
            angle = scan_angle + i * (math.pi * 2 / 3)
            end_x = center_x + math.cos(angle) * 250
            end_y = center_y + math.sin(angle) * 250
            pygame.draw.line(self.image, (255, 255, 100, 80), 
                           (center_x, center_y), (end_x, end_y), 2)


class MirageInfinityRealm(pygame.sprite.Sprite):
    """【无限镜界】幻镜分身大招 - 召唤分身矩阵，全员同时发射光束"""
    def __init__(self, owner):
        super().__init__(all_sprites)
        self.owner = owner
        self.life = 180  # 3秒持续
        self.phase = 0  # 0=召唤分身, 1=蓄力, 2=齐射
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # 清除敌方子弹
        enemy_bullets.empty()
        
        # 生成5个分身位置（五芒星）
        self.mirrors = []
        center_x, center_y = owner.rect.centerx, owner.rect.centery
        for i in range(5):
            angle = (i * 72 - 90) * 3.14159 / 180
            mirror_x = center_x + int(150 * math.cos(angle))
            mirror_y = center_y + int(100 * math.sin(angle))
            self.mirrors.append({
                'x': mirror_x, 'y': mirror_y,
                'alpha': 0, 'beam_active': False
            })
        
        # 更新玩家分身列表
        owner.active_mirrors = [(m['x'], m['y']) for m in self.mirrors]
        owner.mirage_mirror_count = 5
        owner.mirage_sync_level = 5  # 满同步
        
        # 显示大招名
        FloatingText(owner.rect.centerx, owner.rect.top - 40, "「无限镜界」", (220, 180, 255))
    
    def update(self):
        self.life -= 1
        self.image.fill((0, 0, 0, 0))
        
        if self.life <= 0:
            self.owner.active_mirrors = []
            self.owner.mirage_mirror_count = 0
            self.kill()
            return
        
        progress = 1 - self.life / 180
        
        # 阶段1：分身出现（0-0.3）
        if progress < 0.3:
            spawn_progress = progress / 0.3
            for mirror in self.mirrors:
                mirror['alpha'] = int(255 * spawn_progress)
                # 绘制半透明分身
                self._draw_mirror(mirror, spawn_progress)
        
        # 阶段2：蓄力（0.3-0.5）
        elif progress < 0.5:
            charge_progress = (progress - 0.3) / 0.2
            for mirror in self.mirrors:
                mirror['alpha'] = 255
                self._draw_mirror(mirror, 1.0)
                # 蓄力光环
                ring_r = int(20 + charge_progress * 30)
                pygame.draw.circle(self.image, (200, 150, 255, int(150 * charge_progress)), 
                                 (mirror['x'], mirror['y']), ring_r, 3)
        
        # 阶段3：齐射（0.5-1.0）
        else:
            beam_progress = (progress - 0.5) / 0.5
            for i, mirror in enumerate(self.mirrors):
                self._draw_mirror(mirror, 1.0)
                # 发射光束
                beam_len = 600
                beam_color = (220, 180, 255)
                beam_width = int(8 + beam_progress * 6)
                # 光束向上发射
                pygame.draw.rect(self.image, beam_color, 
                               (mirror['x'] - beam_width//2, mirror['y'] - beam_len, beam_width, beam_len))
                # 光束光晕
                glow_surf = pygame.Surface((beam_width * 3, beam_len), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*beam_color, 100), (0, 0, beam_width * 3, beam_len))
                self.image.blit(glow_surf, (mirror['x'] - beam_width * 1.5, mirror['y'] - beam_len))
                
                # 造成伤害
                if self.life % 10 == 0:
                    beam_rect = pygame.Rect(mirror['x'] - beam_width, 0, beam_width * 2, mirror['y'])
                    for mob in mobs:
                        if beam_rect.colliderect(mob.rect):
                            mob.take_damage(self.owner.damage * 0.8)
        
        # 连接线（五芒星）
        for i in range(5):
            start = (self.mirrors[i]['x'], self.mirrors[i]['y'])
            end = (self.mirrors[(i + 2) % 5]['x'], self.mirrors[(i + 2) % 5]['y'])
            pygame.draw.line(self.image, (200, 150, 255, 150), start, end, 2)
    
    def _draw_mirror(self, mirror, scale):
        """绘制分身"""
        x, y, alpha = mirror['x'], mirror['y'], mirror['alpha']
        size = int(30 * scale)
        # 三角棱镜形状
        pts = [(x, y - size), (x - size * 0.7, y + size * 0.5), (x + size * 0.7, y + size * 0.5)]
        mirror_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(mirror_surf, (200, 150, 255, alpha), pts)
        pygame.draw.polygon(mirror_surf, (255, 220, 255, alpha), pts, 2)
        self.image.blit(mirror_surf, (0, 0))


class GambitFortuneWheel(pygame.sprite.Sprite):
    """【命运轮盘】赌徒大招 - 旋转轮盘，随机触发超强效果"""
    def __init__(self, owner):
        super().__init__(all_sprites)
        self.owner = owner
        self.life = 150  # 2.5秒
        self.phase = 0  # 0=轮盘旋转, 1=停止, 2=触发效果
        self.spin_speed = 20  # 旋转速度
        self.spin_angle = 0
        self.result = None  # 最终结果
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # 清除敌方子弹
        enemy_bullets.empty()
        
        # 6种可能的结果
        self.outcomes = [
            {"name": "JACKPOT", "color": (255, 215, 0), "effect": "全屏金币雨，所有敌人受到5倍伤害"},
            {"name": "TRIPLE", "color": (255, 100, 100), "effect": "三倍伤害持续10秒"},
            {"name": "SHIELD", "color": (100, 200, 255), "effect": "获得无敌护盾5秒"},
            {"name": "BURST", "color": (255, 150, 50), "effect": "发射36发全方位子弹"},
            {"name": "HEAL", "color": (100, 255, 100), "effect": "回复50%最大生命"},
            {"name": "WILD", "color": (200, 100, 255), "effect": "随机触发以上任意两种"}
        ]
        
        # 随机决定结果（运气值影响概率）
        luck = owner.gambit_luck_meter
        if luck >= 80:
            weights = [30, 25, 15, 15, 10, 5]  # 高运气更容易JACKPOT
        elif luck >= 50:
            weights = [15, 20, 20, 20, 15, 10]  # 中等运气均衡
        else:
            weights = [5, 15, 25, 20, 25, 10]  # 低运气更容易SHIELD/HEAL
        
        self.final_result_idx = random.choices(range(6), weights=weights)[0]
        
        # 显示大招名
        FloatingText(owner.rect.centerx, owner.rect.top - 40, "「命运轮盘」", (255, 215, 0))
    
    def update(self):
        self.life -= 1
        self.image.fill((0, 0, 0, 0))
        
        if self.life <= 0:
            self.kill()
            return
        
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        wheel_radius = 150
        
        # 阶段1：轮盘旋转（life > 60）
        if self.life > 60:
            self.spin_angle += self.spin_speed
            self.spin_speed = max(2, self.spin_speed - 0.15)  # 逐渐减速
        
        # 阶段2：停止并显示结果（life 60-30）
        elif self.life > 30:
            if self.result is None:
                self.result = self.outcomes[self.final_result_idx]
                FloatingText(center_x, center_y - 50, self.result["name"], self.result["color"])
        
        # 阶段3：触发效果（life <= 30）
        else:
            if self.life == 30:
                self._trigger_effect()
        
        # 绘制轮盘
        self._draw_wheel(center_x, center_y, wheel_radius)
        
        # 绘制指针
        pointer_pts = [(center_x, center_y - wheel_radius - 20),
                      (center_x - 15, center_y - wheel_radius - 40),
                      (center_x + 15, center_y - wheel_radius - 40)]
        pygame.draw.polygon(self.image, (255, 215, 0), pointer_pts)
        pygame.draw.polygon(self.image, (255, 255, 255), pointer_pts, 2)
    
    def _draw_wheel(self, cx, cy, radius):
        """绘制轮盘"""
        # 6个扇区
        for i, outcome in enumerate(self.outcomes):
            start_angle = (i * 60 + self.spin_angle) * 3.14159 / 180
            end_angle = ((i + 1) * 60 + self.spin_angle) * 3.14159 / 180
            
            # 扇形
            points = [(cx, cy)]
            for ang in range(int(start_angle * 57.3), int(end_angle * 57.3) + 1, 5):
                ang_rad = ang * 0.01745
                points.append((cx + math.cos(ang_rad) * radius, 
                             cy + math.sin(ang_rad) * radius))
            if len(points) > 2:
                pygame.draw.polygon(self.image, outcome["color"], points)
                pygame.draw.polygon(self.image, (255, 255, 255), points, 2)
        
        # 中心圆
        pygame.draw.circle(self.image, (50, 50, 50), (cx, cy), 30)
        pygame.draw.circle(self.image, (255, 215, 0), (cx, cy), 30, 3)
        pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 15)
    
    def _trigger_effect(self):
        """触发轮盘效果"""
        result_idx = self.final_result_idx
        owner = self.owner
        
        if result_idx == 0:  # JACKPOT - 全屏金币雨
            for mob in mobs:
                mob.take_damage(owner.damage * 5)
            owner.gambit_luck_meter = 100
            owner.gambit_jackpot_count += 1
            # 金币粒子
            for _ in range(50):
                x = random.randint(50, WIDTH - 50)
                y = random.randint(50, HEIGHT - 200)
                Particle((x, y), (255, 215, 0), mode='spark')
        
        elif result_idx == 1:  # TRIPLE - 三倍伤害
            owner.gambit_wheel_bonus = 3.0
            # 设置持续时间（通过外部计时）
        
        elif result_idx == 2:  # SHIELD - 无敌护盾
            owner.shield = owner.max_shield * 3
            owner.invincible_timer = 300  # 5秒无敌
        
        elif result_idx == 3:  # BURST - 全方位射击
            for angle in range(0, 360, 10):
                bullet = Bullet(owner.rect.centerx, owner.rect.centery, angle=angle,
                       color=(255, 215, 0), b_type="card", piercing=3)
                bullet.is_gambit_bullet = True
                bullet.damage_mult = 2.0
                bullet.speed = -15
        
        elif result_idx == 4:  # HEAL - 回复生命
            heal_amount = owner.max_hp * 0.5
            owner.hp = min(owner.max_hp, owner.hp + heal_amount)
            FloatingText(owner.rect.centerx, owner.rect.centery, f"+{int(heal_amount)} HP", (100, 255, 100))
        
        elif result_idx == 5:  # WILD - 随机两种
            # 触发两种随机效果
            effects = random.sample([0, 1, 2, 3, 4], 2)
            for eff in effects:
                if eff == 0:
                    for mob in mobs:
                        mob.take_damage(owner.damage * 3)
                elif eff == 1:
                    owner.gambit_wheel_bonus = 2.0
                elif eff == 2:
                    owner.shield = owner.max_shield * 2
                elif eff == 3:
                    for angle in range(0, 360, 20):
                        bullet = Bullet(owner.rect.centerx, owner.rect.centery, angle=angle,
                               color=(200, 100, 255), b_type="card", piercing=2)
                        bullet.speed = -14
                elif eff == 4:
                    owner.hp = min(owner.max_hp, owner.hp + owner.max_hp * 0.3)


# ==================== Mirage幻镜系大招（G/C键） ====================

class MirageKaleidoscope(pygame.sprite.Sprite):
    """【万花镜像】G键第二大招 - 召唤万花筒镜像矩阵，折射攻击覆盖全屏"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 240  # 4秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("zap")
        
        # 清除敌方子弹
        enemy_bullets.empty()
        
        # 创建万花筒镜像阵列（8个方向）
        self.kaleidoscope_mirrors = []
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        for i in range(8):
            angle = i * 45 * 0.01745
            mirror_x = center_x + int(200 * math.cos(angle))
            mirror_y = center_y + int(150 * math.sin(angle))
            self.kaleidoscope_mirrors.append({
                'x': mirror_x, 'y': mirror_y,
                'angle': i * 45, 'rotation': 0
            })
        
        # 增加同步等级
        owner.mirage_sync_level = min(owner.mirage_sync_level + 2, 5)
        
        FloatingText(WIDTH // 2, HEIGHT // 2 - 100, "✦ 万花镜界 ✦", (200, 150, 255))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        
        # 旋转万花筒
        rotation_speed = 2
        for mirror in self.kaleidoscope_mirrors:
            mirror['rotation'] += rotation_speed
        
        # 绘制万花筒图案
        for i, mirror in enumerate(self.kaleidoscope_mirrors):
            mx, my = mirror['x'], mirror['y']
            rot = mirror['rotation']
            
            # 棱镜形状
            size = 35
            pts = []
            for j in range(3):
                ang = (rot + j * 120) * 0.01745
                pts.append((mx + math.cos(ang) * size, my + math.sin(ang) * size))
            pygame.draw.polygon(self.image, (200, 150, 255, 180), pts)
            pygame.draw.polygon(self.image, (255, 200, 255), pts, 2)
            
            # 折射光线
            if self.life % 8 == 0:
                for mob in mobs:
                    if random.random() < 0.3:
                        # 从镜像发射折射光线
                        pygame.draw.line(self.image, (220, 180, 255), 
                                       (mx, my), mob.rect.center, 2)
                        mob.take_damage(self.owner.damage * 0.4)
                        Particle(mob.rect.center, (200, 150, 255), mode='spark')
        
        # 中心连线形成万花筒图案
        for i in range(8):
            start = (self.kaleidoscope_mirrors[i]['x'], self.kaleidoscope_mirrors[i]['y'])
            end = (self.kaleidoscope_mirrors[(i + 1) % 8]['x'], self.kaleidoscope_mirrors[(i + 1) % 8]['y'])
            pygame.draw.line(self.image, (180, 120, 255, 150), start, end, 2)
            # 跨越连线
            end2 = (self.kaleidoscope_mirrors[(i + 3) % 8]['x'], self.kaleidoscope_mirrors[(i + 3) % 8]['y'])
            pygame.draw.line(self.image, (220, 150, 255, 100), start, end2, 1)
        
        # 中心光环
        pulse = abs(math.sin(self.life * 0.1)) * 30
        pygame.draw.circle(self.image, (200, 150, 255, 100), (center_x, center_y), int(50 + pulse), 3)


class MirageRealitySwap(pygame.sprite.Sprite):
    """【虚实颠倒】C键第三大招 - 与所有分身交换位置，分身原位爆炸"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120  # 2秒
        self.phase = 0  # 0=准备, 1=交换, 2=爆炸
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("blackhole")
        
        # 清除敌方子弹
        enemy_bullets.empty()
        
        # 记录当前分身位置（用于爆炸）
        self.mirror_positions = list(owner.active_mirrors) if owner.active_mirrors else []
        self.original_pos = (owner.rect.centerx, owner.rect.centery)
        
        # 如果没有分身，创建3个临时分身位置
        if not self.mirror_positions:
            for i in range(3):
                angle = (i * 120 - 90) * 0.01745
                mx = owner.rect.centerx + int(120 * math.cos(angle))
                my = owner.rect.centery + int(80 * math.sin(angle))
                self.mirror_positions.append((mx, my))
        
        # 选择一个分身位置传送
        if self.mirror_positions:
            self.swap_target = random.choice(self.mirror_positions)
        else:
            self.swap_target = self.original_pos
        
        # 玩家获得短暂无敌
        owner.invincible_timer = 60
        
        FloatingText(WIDTH // 2, HEIGHT // 2 - 100, "★ 虚实颠倒 ★", (255, 200, 255))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        progress = 1 - self.life / 120
        
        # 阶段1：虚影闪烁（0-0.3）
        if progress < 0.3:
            # 玩家和分身都闪烁
            if self.life % 4 < 2:
                for pos in self.mirror_positions:
                    pygame.draw.circle(self.image, (200, 150, 255, 150), pos, 30)
        
        # 阶段2：交换（0.3-0.5）
        elif progress < 0.5:
            if self.phase == 0:
                self.phase = 1
                # 执行交换
                self.owner.rect.center = self.swap_target
                FloatingText(self.owner.rect.centerx, self.owner.rect.centery - 30, "✦", (255, 255, 255))
        
        # 阶段3：爆炸（0.5-1.0）
        else:
            if self.phase == 1:
                self.phase = 2
                # 所有分身位置爆炸
                for pos in self.mirror_positions:
                    # 爆炸伤害
                    for mob in mobs:
                        dist = math.sqrt((mob.rect.centerx - pos[0])**2 + (mob.rect.centery - pos[1])**2)
                        if dist < 150:
                            damage = self.owner.damage * 2 * (1 - dist / 150)
                            mob.take_damage(damage)
                    # 爆炸特效
                    for _ in range(10):
                        Particle(pos, (200, 150, 255), mode='spark')
            
            # 绘制爆炸波纹
            explosion_progress = (progress - 0.5) / 0.5
            for pos in self.mirror_positions:
                ring_radius = int(explosion_progress * 150)
                alpha = int(200 * (1 - explosion_progress))
                if alpha > 0:
                    pygame.draw.circle(self.image, (220, 180, 255, alpha), pos, ring_radius, 4)


# ==================== Gambit赌徒系大招（G/C键） ====================

class GambitDiceJudgment(pygame.sprite.Sprite):
    """【骰子审判】G键第二大招 - 投掷巨大骰子，点数决定敌人命运"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180  # 3秒
        self.phase = 0  # 0=投掷, 1=滚动, 2=判定
        self.dice_value = 0
        self.roll_timer = 60  # 滚动时间
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("powerup")
        
        # 清除敌方子弹
        enemy_bullets.empty()
        
        # 骰子位置
        self.dice_x = WIDTH // 2
        self.dice_y = HEIGHT // 2
        self.dice_rotation = 0
        
        # 运气影响最终点数
        luck = owner.gambit_luck_meter
        if luck >= 80:
            self.final_value = random.choices([4, 5, 6], weights=[20, 30, 50])[0]
        elif luck >= 50:
            self.final_value = random.randint(2, 6)
        else:
            self.final_value = random.choices([1, 2, 3, 4, 5, 6], weights=[30, 25, 20, 15, 7, 3])[0]
        
        FloatingText(WIDTH // 2, HEIGHT // 2 - 150, "◆ 骰子审判 ◆", (255, 215, 0))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        # 阶段1：滚动（life > 120）
        if self.life > 120:
            self.roll_timer -= 1
            self.dice_rotation += 15
            self.dice_value = random.randint(1, 6)  # 快速变化
            
            # 绘制滚动的骰子
            self._draw_dice(self.dice_x, self.dice_y, 80, self.dice_value, self.dice_rotation)
        
        # 阶段2：减速停止（life 120-90）
        elif self.life > 90:
            slow_progress = (120 - self.life) / 30
            self.dice_rotation += 15 * (1 - slow_progress)
            
            # 逐渐显示最终值
            if random.random() < slow_progress:
                self.dice_value = self.final_value
            else:
                self.dice_value = random.randint(1, 6)
            
            self._draw_dice(self.dice_x, self.dice_y, 80, self.dice_value, self.dice_rotation)
        
        # 阶段3：判定生效（life <= 90）
        else:
            self.dice_value = self.final_value
            self._draw_dice(self.dice_x, self.dice_y, 80, self.dice_value, 0)
            
            # 只在第一帧触发效果
            if self.life == 90:
                self._apply_judgment()
    
    def _draw_dice(self, x, y, size, value, rotation):
        """绘制骰子"""
        # 骰子主体（白色方块）
        half = size // 2
        dice_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(dice_surf, (255, 255, 255), (0, 0, size, size), border_radius=10)
        pygame.draw.rect(dice_surf, (200, 200, 200), (0, 0, size, size), 3, border_radius=10)
        
        # 点数
        dot_color = (50, 50, 50)
        dot_r = size // 10
        center = size // 2
        offset = size // 4
        
        dot_positions = {
            1: [(center, center)],
            2: [(offset, offset), (size - offset, size - offset)],
            3: [(offset, offset), (center, center), (size - offset, size - offset)],
            4: [(offset, offset), (offset, size - offset), (size - offset, offset), (size - offset, size - offset)],
            5: [(offset, offset), (offset, size - offset), (center, center), (size - offset, offset), (size - offset, size - offset)],
            6: [(offset, offset), (offset, center), (offset, size - offset), (size - offset, offset), (size - offset, center), (size - offset, size - offset)]
        }
        
        for pos in dot_positions.get(value, []):
            pygame.draw.circle(dice_surf, dot_color, pos, dot_r)
        
        # 旋转并绘制
        rotated = pygame.transform.rotate(dice_surf, rotation)
        rot_rect = rotated.get_rect(center=(x, y))
        self.image.blit(rotated, rot_rect)
        
        # 光晕效果
        glow_colors = {1: (255, 0, 0), 2: (255, 100, 0), 3: (255, 200, 0), 
                      4: (200, 255, 0), 5: (0, 255, 100), 6: (255, 215, 0)}
        glow_color = glow_colors.get(value, (255, 255, 255))
        pygame.draw.circle(self.image, (*glow_color, 50), (x, y), size + 20, 5)
    
    def _apply_judgment(self):
        """应用骰子判定效果"""
        owner = self.owner
        value = self.final_value
        
        FloatingText(self.dice_x, self.dice_y - 60, f"[ {value} ]", (255, 215, 0))
        
        if value == 1:  # 蛇眼 - 不幸但获得补偿
            owner.gambit_luck_meter = min(100, owner.gambit_luck_meter + 30)
            owner.gambit_next_crit = True
            FloatingText(self.dice_x, self.dice_y + 60, "蛇眼！下次必暴击！", (255, 100, 100))
        
        elif value == 2:  # 小点 - 轻微效果
            for mob in mobs:
                mob.take_damage(owner.damage * 0.5)
            FloatingText(self.dice_x, self.dice_y + 60, "小点...", (255, 150, 100))
        
        elif value == 3:  # 中等 - 标准伤害
            for mob in mobs:
                mob.take_damage(owner.damage * 1.5)
            FloatingText(self.dice_x, self.dice_y + 60, "不错！", (255, 200, 100))
        
        elif value == 4:  # 好点 - 强化伤害
            for mob in mobs:
                mob.take_damage(owner.damage * 2.5)
            owner.gambit_combo_streak += 1
            FloatingText(self.dice_x, self.dice_y + 60, "好运！", (200, 255, 100))
        
        elif value == 5:  # 大点 - 强力效果
            for mob in mobs:
                mob.take_damage(owner.damage * 3.5)
            owner.gambit_luck_meter = min(100, owner.gambit_luck_meter + 15)
            FloatingText(self.dice_x, self.dice_y + 60, "大吉！", (100, 255, 100))
        
        elif value == 6:  # 豹子 - 超级效果
            for mob in mobs:
                mob.take_damage(owner.damage * 5)
            owner.gambit_jackpot_count += 1
            owner.gambit_luck_meter = 100
            owner.hp = min(owner.max_hp, owner.hp + owner.max_hp * 0.3)
            FloatingText(self.dice_x, self.dice_y + 60, "★ JACKPOT! ★", (255, 215, 0))
            for _ in range(30):
                Particle((random.randint(100, WIDTH-100), random.randint(100, HEIGHT-200)), 
                        (255, 215, 0), mode='spark')


class GambitAllIn(pygame.sprite.Sprite):
    """【全押梭哈】C键第三大招 - 把所有运气值押上，触发超级效果"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180  # 3秒
        self.phase = 0
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        
        # 清除敌方子弹
        enemy_bullets.empty()
        
        # 获取当前运气值并全押
        self.bet_luck = owner.gambit_luck_meter
        owner.gambit_luck_meter = 0  # 清空运气值
        
        # 根据押注的运气值决定效果强度
        self.multiplier = 1 + self.bet_luck / 25  # 最高5倍
        
        # 随机决定结果（但高运气值增加成功率）
        success_rate = 0.3 + self.bet_luck / 200  # 30%-80%成功率
        self.is_success = random.random() < success_rate
        
        # 扑克牌展示
        self.cards = []
        for i in range(5):
            self.cards.append({
                'x': 150 + i * 100,
                'y': HEIGHT // 2,
                'suit': random.choice(['♠', '♥', '♦', '♣']),
                'value': random.choice(['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']),
                'revealed': False,
                'flip_time': 30 + i * 15
            })
        
        FloatingText(WIDTH // 2, HEIGHT // 2 - 150, f"★ ALL IN! ({int(self.bet_luck)}) ★", (255, 50, 50))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        progress = 1 - self.life / 180
        
        # 阶段1：翻牌（0-0.5）
        if progress < 0.5:
            flip_progress = progress / 0.5
            for i, card in enumerate(self.cards):
                if 180 - self.life > card['flip_time']:
                    card['revealed'] = True
                self._draw_card(card)
        
        # 阶段2：判定效果（0.5-1.0）
        else:
            # 显示所有牌
            for card in self.cards:
                card['revealed'] = True
                self._draw_card(card)
            
            # 首次触发效果
            if self.phase == 0:
                self.phase = 1
                self._apply_result()
        
        # 金币粒子效果
        if self.life % 5 == 0:
            x = random.randint(100, WIDTH - 100)
            y = random.randint(50, HEIGHT - 200)
            Particle((x, y), (255, 215, 0), mode='star')
    
    def _draw_card(self, card):
        """绘制扑克牌"""
        x, y = card['x'], card['y']
        w, h = 60, 80
        
        if card['revealed']:
            # 正面
            pygame.draw.rect(self.image, (255, 255, 255), (x - w//2, y - h//2, w, h), border_radius=5)
            pygame.draw.rect(self.image, (100, 100, 100), (x - w//2, y - h//2, w, h), 2, border_radius=5)
            
            # 花色颜色
            suit_color = (255, 50, 50) if card['suit'] in ['♥', '♦'] else (50, 50, 50)
            
            # 简化显示（花色在中心）
            # 由于没有字体，用形状表示
            if card['suit'] == '♠':
                pts = [(x, y - 15), (x - 12, y + 5), (x + 12, y + 5)]
                pygame.draw.polygon(self.image, suit_color, pts)
            elif card['suit'] == '♥':
                pygame.draw.circle(self.image, suit_color, (x - 6, y - 5), 8)
                pygame.draw.circle(self.image, suit_color, (x + 6, y - 5), 8)
                pts = [(x - 12, y - 2), (x, y + 15), (x + 12, y - 2)]
                pygame.draw.polygon(self.image, suit_color, pts)
            elif card['suit'] == '♦':
                pts = [(x, y - 15), (x - 12, y), (x, y + 15), (x + 12, y)]
                pygame.draw.polygon(self.image, suit_color, pts)
            else:  # ♣
                pygame.draw.circle(self.image, suit_color, (x, y - 10), 8)
                pygame.draw.circle(self.image, suit_color, (x - 8, y + 2), 8)
                pygame.draw.circle(self.image, suit_color, (x + 8, y + 2), 8)
        else:
            # 背面
            pygame.draw.rect(self.image, (50, 50, 150), (x - w//2, y - h//2, w, h), border_radius=5)
            pygame.draw.rect(self.image, (255, 215, 0), (x - w//2, y - h//2, w, h), 2, border_radius=5)
            # 背面花纹
            pygame.draw.rect(self.image, (70, 70, 180), (x - w//2 + 5, y - h//2 + 5, w - 10, h - 10), border_radius=3)
    
    def _apply_result(self):
        """应用全押结果"""
        owner = self.owner
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        
        if self.is_success:
            # 大成功！
            FloatingText(center_x, center_y + 80, "★ WINNER! ★", (255, 215, 0))
            
            # 超级伤害
            for mob in mobs:
                mob.take_damage(owner.damage * self.multiplier * 3)
            
            # 返还运气值并获得奖励
            owner.gambit_luck_meter = min(100, self.bet_luck + 30)
            owner.gambit_jackpot_count += 1
            
            # 回复生命
            owner.hp = min(owner.max_hp, owner.hp + owner.max_hp * 0.4)
            
            # 短暂无敌
            owner.invincible_timer = 180
            
            # 发射36发金色子弹
            for angle in range(0, 360, 10):
                bullet = Bullet(owner.rect.centerx, owner.rect.centery, angle=angle,
                       color=(255, 215, 0), b_type="card", piercing=5)
                bullet.speed = -16
                bullet.damage_mult = self.multiplier
            
            # 金币雨特效
            for _ in range(50):
                Particle((random.randint(50, WIDTH-50), random.randint(50, HEIGHT-200)), 
                        (255, 215, 0), mode='spark')
        
        else:
            # 失败...但不是完全没有
            FloatingText(center_x, center_y + 80, "惜败...", (150, 150, 150))
            
            # 仍然造成一些伤害
            for mob in mobs:
                mob.take_damage(owner.damage * 0.5)
            
            # 返还部分运气值
            owner.gambit_luck_meter = self.bet_luck * 0.3
            
            # 下次必暴击作为补偿
            owner.gambit_next_crit = True
            
            FloatingText(center_x, center_y + 110, "下次必暴击！", (255, 200, 100))


# =====================================================================
#   Puppeteer (牵线木偶师) 大招实现
# =====================================================================

class PuppeteerMassCharm(pygame.sprite.Sprite):
    """【全场魅惑】X键大招 - 魅惑50%的敌人成为傀儡"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180
        self.phase = 0
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        
        enemy_bullets.empty()
        
        if not hasattr(owner, 'puppet_enemies'):
            owner.puppet_enemies = {}
        
        all_mobs = list(mobs)
        charm_count = max(1, len(all_mobs) // 2)
        targets = random.sample(all_mobs, min(charm_count, len(all_mobs))) if all_mobs else []
        
        self.charmed_enemies = []
        for enemy in targets:
            owner.puppet_enemies[enemy] = {"stacks": 3, "controlled": True}
            enemy.puppet_controlled = True
            self.charmed_enemies.append(enemy)
            FloatingText(enemy.rect.centerx, enemy.rect.top - 20, "🎭魅惑!", (180, 100, 150))
        
        FloatingText(owner.rect.centerx, owner.rect.top - 40, f"「全场魅惑」×{len(targets)}", (220, 120, 180))
        
        self.strings = []
        for enemy in self.charmed_enemies:
            self.strings.append({'start': owner.rect.center, 'end': enemy.rect.center, 'alpha': 255})
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        for i, string in enumerate(self.strings):
            if i < len(self.charmed_enemies) and self.charmed_enemies[i].alive():
                string['end'] = self.charmed_enemies[i].rect.center
            string['alpha'] = int(255 * self.life / 180)
            start, end = string['start'], string['end']
            mid_x = (start[0] + end[0]) // 2 + int(20 * math.sin(self.life / 10))
            mid_y = (start[1] + end[1]) // 2
            pygame.draw.line(self.image, (180, 100, 150, string['alpha']), start, (mid_x, mid_y), 2)
            pygame.draw.line(self.image, (180, 100, 150, string['alpha']), (mid_x, mid_y), end, 2)
        
        for enemy in self.charmed_enemies:
            if enemy.alive():
                pygame.draw.circle(self.image, (180, 100, 150, 100), enemy.rect.center, 30, 2)
                cx, cy = enemy.rect.center
                pygame.draw.line(self.image, (220, 150, 180), (cx - 15, cy), (cx + 15, cy), 2)
                pygame.draw.line(self.image, (220, 150, 180), (cx, cy - 15), (cx, cy + 15), 2)


class PuppeteerFateWeb(pygame.sprite.Sprite):
    """【命运丝网】G键大招 - 所有敌人连线，伤害传递"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 240
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        enemy_bullets.empty()
        
        self.web_enemies = list(mobs)
        self.hp_snapshot = {enemy: enemy.hp for enemy in self.web_enemies}
        self.transfer_rate = 0.5
        
        FloatingText(owner.rect.centerx, owner.rect.top - 40, "「命运丝网」", (180, 100, 150))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        for enemy in list(self.web_enemies):
            if not enemy.alive():
                self.web_enemies.remove(enemy)
                death_damage = self.owner.damage * 2
                for other in self.web_enemies:
                    if other.alive():
                        other.hp -= death_damage
                        FloatingText(other.rect.centerx, other.rect.top - 10, f"🕸️{int(death_damage)}", (180, 100, 150))
                continue
            
            old_hp = self.hp_snapshot.get(enemy, enemy.hp)
            if enemy.hp < old_hp:
                damage_taken = old_hp - enemy.hp
                transfer_damage = damage_taken * self.transfer_rate
                for other in self.web_enemies:
                    if other != enemy and other.alive():
                        other.hp -= transfer_damage
            self.hp_snapshot[enemy] = enemy.hp
        
        pulse = abs(math.sin(self.life / 15))
        for i, enemy1 in enumerate(self.web_enemies):
            for enemy2 in self.web_enemies[i+1:]:
                if enemy1.alive() and enemy2.alive():
                    alpha = int(150 * pulse)
                    pygame.draw.line(self.image, (180, 100, 150, alpha), enemy1.rect.center, enemy2.rect.center, 1)
        
        for enemy in self.web_enemies:
            if enemy.alive():
                pygame.draw.circle(self.image, (220, 150, 180, 200), enemy.rect.center, 8)
                pygame.draw.circle(self.image, (180, 100, 150), enemy.rect.center, 8, 2)


class PuppeteerPuppetTheater(pygame.sprite.Sprite):
    """【傀儡剧场】C键大招 - 召唤击杀过的敌人复制体为你战斗"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 450
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        enemy_bullets.empty()
        
        self.puppets = []
        puppet_types = ["chaser", "tank", "sniper"]
        for i, ptype in enumerate(puppet_types):
            angle = (i * 120 + 90) * 3.14159 / 180
            px = owner.rect.centerx + int(100 * math.cos(angle))
            py = owner.rect.centery + int(100 * math.sin(angle))
            self.puppets.append({'type': ptype, 'x': px, 'y': py, 'hp': 200, 'fire_timer': 0, 'target': None})
        
        FloatingText(owner.rect.centerx, owner.rect.top - 40, "「傀儡剧场」", (220, 120, 180))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        owner = self.owner
        
        for puppet in self.puppets:
            angle = (self.puppets.index(puppet) * 120 + self.life) * 3.14159 / 180
            target_x = owner.rect.centerx + int(80 * math.cos(angle))
            target_y = owner.rect.centery + int(80 * math.sin(angle))
            puppet['x'] += (target_x - puppet['x']) * 0.1
            puppet['y'] += (target_y - puppet['y']) * 0.1
            px, py = int(puppet['x']), int(puppet['y'])
            
            puppet['fire_timer'] -= 1
            if puppet['fire_timer'] <= 0 and mobs:
                nearest = min(mobs, key=lambda m: math.hypot(m.rect.centerx - px, m.rect.centery - py))
                angle_to_target = math.atan2(nearest.rect.centery - py, nearest.rect.centerx - px)
                angle_deg = angle_to_target * 180 / 3.14159
                puppet_bullet = Bullet(px, py, angle=angle_deg - 90, color=(180, 100, 150), b_type="puppet_string", piercing=1)
                puppet_bullet.speed = -12
                puppet_bullet.damage_mult = 1.5
                puppet['fire_timer'] = 30
            
            pygame.draw.rect(self.image, (180, 100, 150), (px - 3, py - 20, 6, 40))
            pygame.draw.rect(self.image, (180, 100, 150), (px - 15, py - 5, 30, 6))
            pygame.draw.circle(self.image, (220, 180, 200), (px, py - 25), 10)
            pygame.draw.circle(self.image, (180, 100, 150), (px, py - 25), 10, 2)
            pygame.draw.line(self.image, (100, 50, 80), (px - 4, py - 28), (px + 4, py - 22), 2)
            pygame.draw.line(self.image, (100, 50, 80), (px + 4, py - 28), (px - 4, py - 22), 2)
            pygame.draw.line(self.image, (180, 100, 150, 150), owner.rect.center, (px, py - 25), 1)


# =====================================================================
#   Pandemic (末日瘟神) 大招实现
# =====================================================================

class PandemicPatientZero(pygame.sprite.Sprite):
    """【零号毒株】X键大招 - 全屏感染+变异等级+3"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 150
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        enemy_bullets.empty()
        
        if not hasattr(owner, 'infected_enemies'):
            owner.infected_enemies = {}
            owner.pandemic_mutation_level = 0
            owner.pandemic_spread_count = 0
            owner.pandemic_mutations = {}
        
        for enemy in mobs:
            if enemy not in owner.infected_enemies:
                owner.infected_enemies[enemy] = {"level": 3, "damage_stack": 0, "timer": 0}
                FloatingText(enemy.rect.centerx, enemy.rect.top - 10, "☣️零号!", (150, 255, 100))
        
        owner.pandemic_mutation_level = min(10, owner.pandemic_mutation_level + 3)
        
        self.particles = []
        for _ in range(100):
            self.particles.append({
                'x': owner.rect.centerx, 'y': owner.rect.centery,
                'vx': random.uniform(-8, 8), 'vy': random.uniform(-8, 8),
                'life': random.randint(60, 120)
            })
        
        FloatingText(owner.rect.centerx, owner.rect.top - 40, f"「零号毒株」变异Lv.{owner.pandemic_mutation_level}", (100, 255, 80))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= 0.98
            p['vy'] *= 0.98
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            alpha = int(255 * p['life'] / 120)
            size = int(3 + p['life'] / 30)
            pygame.draw.circle(self.image, (100, 255, 80, alpha), (int(p['x']), int(p['y'])), size)
        
        for enemy in list(mobs):
            if hasattr(self.owner, 'infected_enemies') and enemy in self.owner.infected_enemies:
                pulse = abs(math.sin(self.life / 10))
                radius = 20 + int(10 * pulse)
                pygame.draw.circle(self.image, (100, 255, 80, 100), enemy.rect.center, radius, 2)
                pygame.draw.circle(self.image, (150, 255, 100), enemy.rect.center, 5)


class PandemicForceMutation(pygame.sprite.Sprite):
    """【强制变异】G键大招 - 立即触发5次变异"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120
        self.mutation_timer = 0
        self.mutations_triggered = 0
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        enemy_bullets.empty()
        
        if not hasattr(owner, 'pandemic_mutation_level'):
            owner.pandemic_mutation_level = 0
            owner.pandemic_mutations = {}
        
        self.helix_phase = 0
        FloatingText(owner.rect.centerx, owner.rect.top - 40, "「强制变异」", (200, 255, 100))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        self.helix_phase += 0.15
        
        self.mutation_timer += 1
        if self.mutation_timer >= 20 and self.mutations_triggered < 5:
            self.mutation_timer = 0
            self.mutations_triggered += 1
            self.owner.pandemic_mutation_level = min(10, self.owner.pandemic_mutation_level + 1)
            
            effects = ["damage", "slow", "armor_break", "spread_range", "dot_power"]
            effect = random.choice(effects)
            if not hasattr(self.owner, 'pandemic_mutations'):
                self.owner.pandemic_mutations = {}
            self.owner.pandemic_mutations[effect] = self.owner.pandemic_mutations.get(effect, 0) + 1
            
            effect_names = {"damage": "伤害+", "slow": "减速+", "armor_break": "破甲+", "spread_range": "传播+", "dot_power": "毒伤+"}
            FloatingText(self.owner.rect.centerx + random.randint(-50, 50), self.owner.rect.centery - 30, f"🧬{effect_names[effect]}", (150, 255, 100))
        
        center_x = WIDTH // 2
        for i in range(30):
            y = 100 + i * 20
            offset = 50 * math.sin(self.helix_phase + i * 0.3)
            x1, x2 = center_x - offset, center_x + offset
            pygame.draw.circle(self.image, (100, 255, 80), (int(x1), y), 6)
            pygame.draw.circle(self.image, (150, 255, 100), (int(x2), y), 6)
            if i % 2 == 0:
                pygame.draw.line(self.image, (200, 255, 150), (int(x1), y), (int(x2), y), 2)
        
        level = self.owner.pandemic_mutation_level
        for i in range(level):
            x = 50 + i * 25
            pygame.draw.circle(self.image, (100, 255, 80), (x, 50), 8)
            pygame.draw.circle(self.image, (200, 255, 150), (x, 50), 8, 2)


class PandemicFinalJudgment(pygame.sprite.Sprite):
    """【终末审判】C键大招 - 所有感染敌人的潜伏伤害立即爆发，爆发伤害+200%"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 90
        self.phase = 0
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        enemy_bullets.empty()
        
        self.total_damage = 0
        self.explosions = []
        FloatingText(owner.rect.centerx, owner.rect.top - 40, "「终末审判」", (255, 100, 100))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        if self.phase == 0:
            self.phase = 1
            if hasattr(self.owner, 'infected_enemies'):
                for enemy, data in list(self.owner.infected_enemies.items()):
                    if enemy.alive():
                        burst_damage = (data["damage_stack"] + self.owner.damage * data["level"]) * 3.0
                        enemy.hp -= burst_damage
                        self.total_damage += burst_damage
                        self.explosions.append({'x': enemy.rect.centerx, 'y': enemy.rect.centery, 'radius': 10, 'max_radius': 60, 'alpha': 255})
                        FloatingText(enemy.rect.centerx, enemy.rect.top - 20, f"☠️{int(burst_damage)}", (255, 50, 50))
                        data["damage_stack"] = 0
                        data["timer"] = 0
                FloatingText(WIDTH // 2, HEIGHT // 2, f"总爆发伤害: {int(self.total_damage)}", (255, 100, 100))
        
        for exp in self.explosions[:]:
            exp['radius'] += 3
            exp['alpha'] = int(255 * (1 - exp['radius'] / exp['max_radius']))
            if exp['radius'] >= exp['max_radius']:
                self.explosions.remove(exp)
                continue
            pygame.draw.circle(self.image, (100, 255, 80, exp['alpha'] // 2), (exp['x'], exp['y']), int(exp['radius']))
            pygame.draw.circle(self.image, (255, 100, 80, exp['alpha']), (exp['x'], exp['y']), int(exp['radius']), 3)
            if exp['alpha'] > 100:
                cx, cy = exp['x'], exp['y']
                pygame.draw.circle(self.image, (255, 255, 255), (cx, cy - 5), 8)
                pygame.draw.circle(self.image, (0, 0, 0), (cx - 3, cy - 6), 2)
                pygame.draw.circle(self.image, (0, 0, 0), (cx + 3, cy - 6), 2)
                pygame.draw.line(self.image, (0, 0, 0), (cx - 2, cy), (cx + 2, cy), 2)


# =====================================================================
# 终极机体专属大招
# =====================================================================

class OmegaFinalJudgment(pygame.sprite.Sprite):
    """【终焉审判】Omega大招 - 七属性同时爆发的终极制裁"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 240  # 4秒持续
        self.phase = 0
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        enemy_bullets.empty()
        
        # 七属性定义
        self.elements = [
            {"name": "炎", "color": (255, 80, 30), "angle": 0},
            {"name": "冰", "color": (100, 200, 255), "angle": 51.4},
            {"name": "雷", "color": (255, 255, 100), "angle": 102.8},
            {"name": "毒", "color": (150, 255, 80), "angle": 154.3},
            {"name": "圣", "color": (255, 255, 255), "angle": 205.7},
            {"name": "暗", "color": (150, 50, 200), "angle": 257.1},
            {"name": "元", "color": (255, 200, 100), "angle": 308.6},
        ]
        
        self.rotation = 0
        self.scale = 0
        self.beams = []  # 激光束
        self.hit_enemies = {}
        self.judgment_phase = 0  # 0=聚集 1=旋转 2=审判 3=爆发
        
        FloatingText(owner.rect.centerx, owner.rect.top - 60, "◆◆◆ 终焉审判 ◆◆◆", (255, 220, 180))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        cx, cy = WIDTH // 2, HEIGHT // 2
        
        # 阶段1: 七芒星聚集 (60帧)
        if self.life > 180:
            self.judgment_phase = 0
            self.scale = min(1.0, (240 - self.life) / 60)
            self.rotation += 3
            
            # 绘制聚集中的七芒星
            star_r = 150 * self.scale
            for i, elem in enumerate(self.elements):
                angle = (elem["angle"] + self.rotation) * 0.01745
                x = cx + math.cos(angle) * star_r
                y = cy + math.sin(angle) * star_r
                
                # 元素符文
                size = int(20 * self.scale)
                pts = []
                for j in range(6):
                    a = (j * 60 + self.rotation * 2) * 0.01745
                    pts.append((x + math.cos(a) * size, y + math.sin(a) * size))
                pygame.draw.polygon(self.image, elem["color"], pts)
                pygame.draw.polygon(self.image, (255, 255, 255), pts, 2)
                
                # 连接线到中心
                pygame.draw.line(self.image, (*elem["color"], 150), (x, y), (cx, cy), 2)
        
        # 阶段2: 高速旋转 (60帧)
        elif self.life > 120:
            self.judgment_phase = 1
            self.rotation += 15
            
            # 旋转加速的七芒星
            for i, elem in enumerate(self.elements):
                angle = (elem["angle"] + self.rotation) * 0.01745
                x = cx + math.cos(angle) * 150
                y = cy + math.sin(angle) * 150
                
                # 快速旋转光尾
                for trail in range(5):
                    trail_angle = (elem["angle"] + self.rotation - trail * 15) * 0.01745
                    tx = cx + math.cos(trail_angle) * 150
                    ty = cy + math.sin(trail_angle) * 150
                    alpha = 200 - trail * 40
                    pygame.draw.circle(self.image, (*elem["color"], alpha), (int(tx), int(ty)), 15 - trail * 2)
                
                pygame.draw.circle(self.image, elem["color"], (int(x), int(y)), 18)
                pygame.draw.circle(self.image, (255, 255, 255), (int(x), int(y)), 18, 3)
        
        # 阶段3: 审判激光 (80帧)
        elif self.life > 40:
            self.judgment_phase = 2
            self.rotation += 5
            
            # 七道审判激光扫射
            for i, elem in enumerate(self.elements):
                angle = (elem["angle"] + self.rotation) * 0.01745
                
                # 激光起点
                start_x = cx + math.cos(angle) * 60
                start_y = cy + math.sin(angle) * 60
                
                # 激光终点（延伸到屏幕边缘）
                end_x = cx + math.cos(angle) * 800
                end_y = cy + math.sin(angle) * 800
                
                # 多层激光效果
                for w, alpha in [(20, 50), (14, 100), (8, 180), (4, 255)]:
                    pygame.draw.line(self.image, (*elem["color"], alpha), 
                                   (start_x, start_y), (end_x, end_y), w)
                
                # 激光核心（白色）
                pygame.draw.line(self.image, (255, 255, 255, 200), 
                               (start_x, start_y), (end_x, end_y), 2)
                
                # 伤害检测
                for m in list(mobs):
                    mx, my = m.rect.center
                    # 点到线距离
                    dist = abs((end_y - start_y) * mx - (end_x - start_x) * my + 
                              end_x * start_y - end_y * start_x) / max(1, math.hypot(end_x - start_x, end_y - start_y))
                    if dist < 35:
                        key = (m, i)
                        if key not in self.hit_enemies:
                            self.hit_enemies[key] = 0
                        if self.hit_enemies[key] < 8:  # 每个属性最多命中8次
                            m.hp -= 80
                            self.hit_enemies[key] += 1
                            FloatingText(m.rect.centerx, m.rect.top - 10, f"Ω{elem['name']}", elem["color"])
                            Particle(m.rect.center, elem["color"])
            
            # 中心核心
            core_pulse = abs(math.sin(self.life * 0.2)) * 20
            for r in range(3):
                pygame.draw.circle(self.image, (255, 255, 255, 200 - r * 50), 
                                 (cx, cy), int(40 + core_pulse - r * 10))
        
        # 阶段4: 终焉爆发 (40帧)
        else:
            self.judgment_phase = 3
            explosion_scale = (40 - self.life) / 40
            
            # 七属性同心圆爆发
            for i, elem in enumerate(self.elements):
                ring_r = 50 + explosion_scale * 400 + i * 30
                alpha = int(255 * (1 - explosion_scale))
                
                # 元素环
                pts = []
                for j in range(60):
                    a = (j * 6 + i * 10) * 0.01745
                    pts.append((cx + math.cos(a) * ring_r, cy + math.sin(a) * ring_r))
                if len(pts) > 2:
                    pygame.draw.lines(self.image, (*elem["color"], alpha), True, pts, 4)
            
            # 最终伤害波
            if self.life == 35:
                for m in list(mobs):
                    m.hp -= 300
                    FloatingText(m.rect.centerx, m.rect.top - 30, "终焉!", (255, 255, 255))
                    for _ in range(5):
                        Particle(m.rect.center, random.choice([e["color"] for e in self.elements]))
            
            # 中心闪光
            flash_alpha = int(255 * (1 - explosion_scale * 0.5))
            pygame.draw.circle(self.image, (255, 255, 255, flash_alpha), (cx, cy), int(60 * (1 - explosion_scale * 0.5)))


class GenesisBigBang(pygame.sprite.Sprite):
    """【创世纪元】Genesis大招 - 宇宙大爆炸重塑战场"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 300  # 5秒持续
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        enemy_bullets.empty()
        
        self.phase = 0  # 0=坍缩 1=奇点 2=大爆炸 3=创世
        self.singularity_size = 200
        self.explosion_radius = 0
        self.stars = []  # 新生星辰
        self.nebula_clouds = []  # 星云
        self.galaxies = []  # 星系
        self.hit_enemies = set()
        
        # 生成星云云团
        for _ in range(20):
            self.nebula_clouds.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'vx': 0, 'vy': 0,
                'color': random.choice([
                    (255, 200, 150), (200, 150, 255), (150, 200, 255), 
                    (255, 150, 200), (200, 255, 150)
                ]),
                'size': random.randint(30, 80),
                'alpha': random.randint(100, 200)
            })
        
        FloatingText(owner.rect.centerx, owner.rect.top - 60, "◆◆◆ 创世纪元 ◆◆◆", (255, 220, 150))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        cx, cy = WIDTH // 2, HEIGHT // 2
        
        # 阶段1: 宇宙坍缩 (80帧) - 所有物质向中心聚集
        if self.life > 220:
            self.phase = 0
            progress = (300 - self.life) / 80
            self.singularity_size = 200 * (1 - progress * 0.9)
            
            # 星云向中心收缩
            for cloud in self.nebula_clouds:
                dx = cx - cloud['x']
                dy = cy - cloud['y']
                dist = max(1, math.hypot(dx, dy))
                cloud['vx'] += dx / dist * 0.5
                cloud['vy'] += dy / dist * 0.5
                cloud['x'] += cloud['vx']
                cloud['y'] += cloud['vy']
                cloud['size'] = max(5, cloud['size'] - 0.3)
                
                # 绘制收缩的星云
                surf = pygame.Surface((int(cloud['size']*2), int(cloud['size']*2)), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*cloud['color'], int(cloud['alpha'] * (1-progress))), 
                                 (int(cloud['size']), int(cloud['size'])), int(cloud['size']))
                self.image.blit(surf, (int(cloud['x'] - cloud['size']), int(cloud['y'] - cloud['size'])))
            
            # 敌人也被吸向中心
            for m in mobs:
                dx = cx - m.rect.centerx
                dy = cy - m.rect.centery
                dist = max(1, math.hypot(dx, dy))
                pull = 3 * progress
                m.rect.x += int(dx / dist * pull)
                m.rect.y += int(dy / dist * pull)
            
            # 收缩光环
            for ring in range(5):
                ring_r = self.singularity_size + ring * 20
                alpha = int(200 * (1 - progress))
                pygame.draw.circle(self.image, (255, 220, 150, alpha), (cx, cy), int(ring_r), 2)
        
        # 阶段2: 奇点形成 (40帧) - 极度压缩
        elif self.life > 180:
            self.phase = 1
            pulse = abs(math.sin((220 - self.life) * 0.3)) * 15
            
            # 奇点：极亮的点
            for layer in range(8):
                r = 5 + layer * 3 + pulse
                alpha = 255 - layer * 30
                pygame.draw.circle(self.image, (255, 255, 255, alpha), (cx, cy), int(r))
            
            # 周围的扭曲线
            for i in range(12):
                angle = (i * 30 + self.life * 10) * 0.01745
                length = 30 + pulse * 2
                sx = cx + math.cos(angle) * 20
                sy = cy + math.sin(angle) * 20
                ex = cx + math.cos(angle) * length
                ey = cy + math.sin(angle) * length
                pygame.draw.line(self.image, (255, 255, 200), (sx, sy), (ex, ey), 2)
            
            # 时空扭曲环
            distort = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for ring in range(3):
                ring_r = 40 + ring * 15
                pts = []
                for j in range(36):
                    a = (j * 10 + self.life * 20) * 0.01745
                    wobble = 5 * math.sin(j * 0.5 + self.life * 0.5)
                    pts.append((cx + math.cos(a) * (ring_r + wobble), cy + math.sin(a) * (ring_r + wobble)))
                pygame.draw.lines(distort, (255, 200, 100, 150), True, pts, 2)
            self.image.blit(distort, (0, 0))
        
        # 阶段3: 大爆炸 (100帧) - 宇宙诞生
        elif self.life > 80:
            self.phase = 2
            progress = (180 - self.life) / 100
            self.explosion_radius = progress * 600
            
            # 大爆炸冲击波
            wave_colors = [
                (255, 255, 255), (255, 255, 200), (255, 220, 150),
                (255, 180, 100), (255, 150, 80), (200, 100, 50)
            ]
            for i, color in enumerate(wave_colors):
                wave_r = self.explosion_radius - i * 30
                if wave_r > 0:
                    alpha = int(255 * (1 - progress * 0.5))
                    pygame.draw.circle(self.image, (*color, alpha), (cx, cy), int(wave_r), max(1, 8 - i))
            
            # 生成新星
            if random.random() < 0.3 and len(self.stars) < 50:
                angle = random.uniform(0, 360) * 0.01745
                dist = self.explosion_radius * random.uniform(0.3, 0.9)
                self.stars.append({
                    'x': cx + math.cos(angle) * dist,
                    'y': cy + math.sin(angle) * dist,
                    'vx': math.cos(angle) * random.uniform(2, 6),
                    'vy': math.sin(angle) * random.uniform(2, 6),
                    'size': random.randint(3, 8),
                    'color': random.choice([
                        (255, 255, 255), (255, 255, 200), (200, 200, 255),
                        (255, 200, 200), (200, 255, 200)
                    ]),
                    'twinkle': random.uniform(0, 6.28)
                })
            
            # 绘制飞散的星辰
            for star in self.stars:
                star['x'] += star['vx']
                star['y'] += star['vy']
                star['twinkle'] += 0.2
                
                twinkle_size = star['size'] + 2 * abs(math.sin(star['twinkle']))
                pygame.draw.circle(self.image, star['color'], 
                                 (int(star['x']), int(star['y'])), int(twinkle_size))
                # 星光十字
                pygame.draw.line(self.image, (*star['color'], 150),
                               (int(star['x'] - twinkle_size * 2), int(star['y'])),
                               (int(star['x'] + twinkle_size * 2), int(star['y'])), 1)
                pygame.draw.line(self.image, (*star['color'], 150),
                               (int(star['x']), int(star['y'] - twinkle_size * 2)),
                               (int(star['x']), int(star['y'] + twinkle_size * 2)), 1)
            
            # 伤害敌人
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                if dist < self.explosion_radius and m not in self.hit_enemies:
                    self.hit_enemies.add(m)
                    m.hp -= 250
                    FloatingText(m.rect.centerx, m.rect.top - 20, "创世!", (255, 220, 150))
                    for _ in range(3):
                        Particle(m.rect.center, random.choice([(255, 220, 100), (255, 150, 200), (200, 200, 255)]))
            
            # 中心余辉
            core_r = 60 * (1 - progress * 0.8)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), int(core_r))
        
        # 阶段4: 创世完成 (80帧) - 新宇宙形成
        else:
            self.phase = 3
            fade = self.life / 80
            
            # 继续绘制星辰
            for star in self.stars:
                star['vx'] *= 0.98
                star['vy'] *= 0.98
                star['x'] += star['vx']
                star['y'] += star['vy']
                star['twinkle'] += 0.15
                
                twinkle_size = star['size'] + 2 * abs(math.sin(star['twinkle']))
                alpha = int(255 * fade)
                pygame.draw.circle(self.image, (*star['color'][:3], alpha), 
                                 (int(star['x']), int(star['y'])), int(twinkle_size))
            
            # 生成星系漩涡
            if random.random() < 0.1 and len(self.galaxies) < 5:
                self.galaxies.append({
                    'x': random.randint(100, WIDTH - 100),
                    'y': random.randint(100, HEIGHT - 100),
                    'rotation': random.uniform(0, 360),
                    'size': random.randint(40, 80),
                    'arms': random.randint(2, 4)
                })
            
            # 绘制星系
            for galaxy in self.galaxies:
                galaxy['rotation'] += 2
                for arm in range(galaxy['arms']):
                    arm_pts = []
                    for seg in range(15):
                        progress_seg = seg / 14
                        angle = (arm * (360 / galaxy['arms']) + progress_seg * 180 + galaxy['rotation']) * 0.01745
                        r = progress_seg * galaxy['size']
                        arm_pts.append((
                            galaxy['x'] + math.cos(angle) * r,
                            galaxy['y'] + math.sin(angle) * r
                        ))
                    alpha = int(180 * fade)
                    if len(arm_pts) > 1:
                        pygame.draw.lines(self.image, (200, 180, 255, alpha), False, arm_pts, 2)
                # 星系核心
                pygame.draw.circle(self.image, (255, 255, 200, int(200 * fade)), 
                                 (galaxy['x'], galaxy['y']), 8)
            
            # 持续治疗玩家
            if self.life % 20 == 0 and hasattr(self.owner, 'hp'):
                heal = 5
                self.owner.hp = min(self.owner.max_hp, self.owner.hp + heal)
                FloatingText(self.owner.rect.centerx, self.owner.rect.centery - 20, f"+{heal}", (100, 255, 150))


# ========== Omega 第二大招：元素轮转 ==========
class OmegaElementalCycle(pygame.sprite.Sprite):
    """【元素轮转】七属性循环攻击，每种属性附加独特效果"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180  # 3秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        
        # 七属性
        self.elements = [
            {"name": "炎", "color": (255, 80, 30), "effect": "burn"},
            {"name": "冰", "color": (100, 200, 255), "effect": "freeze"},
            {"name": "雷", "color": (255, 255, 100), "effect": "chain"},
            {"name": "毒", "color": (150, 255, 80), "effect": "poison"},
            {"name": "圣", "color": (255, 255, 255), "effect": "heal"},
            {"name": "暗", "color": (150, 50, 200), "effect": "weaken"},
            {"name": "元", "color": (255, 200, 100), "effect": "amplify"},
        ]
        self.current_element = 0
        self.rotation = 0
        self.projectiles = []
        
        FloatingText(owner.rect.centerx, owner.rect.top - 50, "◆ 元素轮转 ◆", (255, 220, 180))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        self.rotation += 5
        cx, cy = self.owner.rect.centerx, self.owner.rect.centery
        
        # 每25帧切换元素并发射
        if self.life % 25 == 0:
            elem = self.elements[self.current_element]
            self.current_element = (self.current_element + 1) % 7
            
            # 向最近敌人发射元素弹
            target = None
            min_dist = float('inf')
            for m in mobs:
                dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                if dist < min_dist:
                    min_dist = dist
                    target = m
            
            if target:
                angle = math.atan2(target.rect.centery - cy, target.rect.centerx - cx)
            else:
                angle = -math.pi / 2  # 向上
            
            self.projectiles.append({
                'x': cx, 'y': cy,
                'vx': math.cos(angle) * 12,
                'vy': math.sin(angle) * 12,
                'element': elem,
                'life': 60
            })
            
            FloatingText(cx, cy - 30, f"Ω{elem['name']}", elem['color'])
        
        # 绘制环绕的元素符文
        for i, elem in enumerate(self.elements):
            angle = (i * 360 / 7 + self.rotation) * math.pi / 180
            ex = cx + math.cos(angle) * 60
            ey = cy + math.sin(angle) * 60
            
            # 高亮当前元素
            size = 15 if i == self.current_element else 10
            pygame.draw.circle(self.image, elem['color'], (int(ex), int(ey)), size)
            if i == self.current_element:
                pygame.draw.circle(self.image, (255, 255, 255), (int(ex), int(ey)), size + 3, 2)
        
        # 更新和绘制元素弹
        for proj in self.projectiles[:]:
            proj['x'] += proj['vx']
            proj['y'] += proj['vy']
            proj['life'] -= 1
            
            if proj['life'] <= 0 or proj['x'] < 0 or proj['x'] > WIDTH or proj['y'] < 0 or proj['y'] > HEIGHT:
                self.projectiles.remove(proj)
                continue
            
            # 绘制元素弹
            elem = proj['element']
            px, py = int(proj['x']), int(proj['y'])
            
            # 带尾迹的元素弹
            for trail in range(4):
                trail_x = px - proj['vx'] * trail * 0.3
                trail_y = py - proj['vy'] * trail * 0.3
                alpha = 200 - trail * 50
                pygame.draw.circle(self.image, (*elem['color'][:3], alpha), 
                                 (int(trail_x), int(trail_y)), 10 - trail * 2)
            
            pygame.draw.circle(self.image, elem['color'], (px, py), 12)
            pygame.draw.circle(self.image, (255, 255, 255), (px, py), 6)
            
            # 碰撞检测
            for m in list(mobs):
                if math.hypot(m.rect.centerx - px, m.rect.centery - py) < 30:
                    m.hp -= 120
                    
                    # 属性特效
                    effect = elem['effect']
                    if effect == "burn":
                        # 燃烧：持续伤害
                        if not hasattr(m, 'burn_tick'):
                            m.burn_tick = 0
                        m.burn_tick = 90
                        FloatingText(m.rect.centerx, m.rect.top - 10, "燃烧!", (255, 100, 50))
                    elif effect == "freeze":
                        # 冻结：减速
                        if hasattr(m, 'speed'):
                            m.speed = max(0.5, m.speed * 0.5)
                        FloatingText(m.rect.centerx, m.rect.top - 10, "冻结!", (100, 200, 255))
                    elif effect == "chain":
                        # 连锁：对周围敌人造成伤害
                        for other in mobs:
                            if other != m:
                                dist = math.hypot(other.rect.centerx - m.rect.centerx, 
                                                other.rect.centery - m.rect.centery)
                                if dist < 100:
                                    other.hp -= 40
                                    pygame.draw.line(self.image, (255, 255, 100), 
                                                   m.rect.center, other.rect.center, 2)
                        FloatingText(m.rect.centerx, m.rect.top - 10, "连锁!", (255, 255, 100))
                    elif effect == "poison":
                        # 毒素：标记
                        if not hasattr(m, 'poison_tick'):
                            m.poison_tick = 0
                        m.poison_tick = 120
                        FloatingText(m.rect.centerx, m.rect.top - 10, "剧毒!", (150, 255, 80))
                    elif effect == "heal":
                        # 圣光：治疗玩家
                        if hasattr(self.owner, 'hp'):
                            self.owner.hp = min(self.owner.max_hp, self.owner.hp + 20)
                        FloatingText(m.rect.centerx, m.rect.top - 10, "神圣!", (255, 255, 255))
                    elif effect == "weaken":
                        # 暗影：削弱防御
                        FloatingText(m.rect.centerx, m.rect.top - 10, "虚弱!", (150, 50, 200))
                    elif effect == "amplify":
                        # 元素：伤害放大
                        m.hp -= 60  # 额外伤害
                        FloatingText(m.rect.centerx, m.rect.top - 10, "增幅!", (255, 200, 100))
                    
                    Particle(m.rect.center, elem['color'])
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    break


# ========== Omega 第三大招：属性共鸣 ==========
class OmegaElementalResonance(pygame.sprite.Sprite):
    """【属性共鸣】七属性同时爆发环形冲击波"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120  # 2秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        enemy_bullets.empty()
        
        self.elements = [
            {"name": "炎", "color": (255, 80, 30)},
            {"name": "冰", "color": (100, 200, 255)},
            {"name": "雷", "color": (255, 255, 100)},
            {"name": "毒", "color": (150, 255, 80)},
            {"name": "圣", "color": (255, 255, 255)},
            {"name": "暗", "color": (150, 50, 200)},
            {"name": "元", "color": (255, 200, 100)},
        ]
        self.wave_radius = 0
        self.hit_enemies = set()
        
        FloatingText(owner.rect.centerx, owner.rect.top - 50, "★ 属性共鸣 ★", (255, 220, 180))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.owner.rect.centerx, self.owner.rect.centery
        
        # 冲击波扩展
        self.wave_radius += 8
        
        # 七层元素环
        for i, elem in enumerate(self.elements):
            ring_r = self.wave_radius - i * 15
            if ring_r > 0:
                # 绘制元素波纹
                alpha = max(0, 200 - self.wave_radius // 3)
                
                # 波浪形环
                pts = []
                for j in range(72):
                    angle = j * 5 * math.pi / 180
                    wobble = 5 * math.sin(j * 0.3 + self.life * 0.2 + i)
                    r = ring_r + wobble
                    pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
                
                if len(pts) > 2:
                    pygame.draw.lines(self.image, (*elem['color'][:3], alpha), True, pts, 4)
        
        # 中心聚能球
        core_size = 30 + 10 * abs(math.sin(self.life * 0.2))
        for i, elem in enumerate(self.elements):
            angle = (i * 360 / 7 + self.life * 5) * math.pi / 180
            ex = cx + math.cos(angle) * (core_size - 10)
            ey = cy + math.sin(angle) * (core_size - 10)
            pygame.draw.circle(self.image, elem['color'], (int(ex), int(ey)), 8)
        pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), int(core_size // 2))
        
        # 伤害敌人
        for m in list(mobs):
            dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
            if abs(dist - self.wave_radius) < 40 and m not in self.hit_enemies:
                self.hit_enemies.add(m)
                m.hp -= 200
                FloatingText(m.rect.centerx, m.rect.top - 20, "共鸣!", (255, 220, 180))
                for elem in self.elements:
                    Particle((m.rect.centerx + random.randint(-20, 20), 
                            m.rect.centery + random.randint(-20, 20)), elem['color'])


# ========== Genesis 第二大招：星辰陨落 ==========
class GenesisMeteorShower(pygame.sprite.Sprite):
    """【星辰陨落】召唤陨石群轰炸敌人"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180  # 3秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        
        self.meteors = []
        self.explosions = []
        
        FloatingText(owner.rect.centerx, owner.rect.top - 50, "◆ 星辰陨落 ◆", (255, 200, 100))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        # 生成新陨石
        if self.life > 60 and random.random() < 0.15:
            # 瞄准敌人或随机位置
            target_x = random.randint(50, WIDTH - 50)
            target_y = random.randint(100, HEIGHT - 100)
            
            if mobs and random.random() < 0.7:
                target = random.choice(list(mobs))
                target_x = target.rect.centerx
                target_y = target.rect.centery
            
            self.meteors.append({
                'x': target_x + random.randint(-100, 100),
                'y': -50,
                'target_x': target_x,
                'target_y': target_y,
                'size': random.randint(20, 40),
                'color': random.choice([
                    (255, 200, 100), (255, 150, 50), (255, 100, 30), (200, 150, 100)
                ]),
                'speed': random.uniform(8, 12),
                'trail': []
            })
        
        # 更新陨石
        for meteor in self.meteors[:]:
            # 计算方向
            dx = meteor['target_x'] - meteor['x']
            dy = meteor['target_y'] - meteor['y']
            dist = max(1, math.hypot(dx, dy))
            
            meteor['x'] += (dx / dist) * meteor['speed']
            meteor['y'] += (dy / dist) * meteor['speed']
            
            # 记录尾迹
            meteor['trail'].append((meteor['x'], meteor['y']))
            if len(meteor['trail']) > 10:
                meteor['trail'].pop(0)
            
            # 绘制尾迹
            for i, pos in enumerate(meteor['trail']):
                alpha = int(200 * (i / len(meteor['trail'])))
                size = int(meteor['size'] * 0.5 * (i / len(meteor['trail'])))
                pygame.draw.circle(self.image, (*meteor['color'][:3], alpha), 
                                 (int(pos[0]), int(pos[1])), max(2, size))
            
            # 绘制陨石
            mx, my = int(meteor['x']), int(meteor['y'])
            # 外焰
            pygame.draw.circle(self.image, (255, 100, 30), (mx, my), meteor['size'] + 5)
            # 陨石本体
            pygame.draw.circle(self.image, meteor['color'], (mx, my), meteor['size'])
            # 高光
            pygame.draw.circle(self.image, (255, 255, 200), (mx - meteor['size']//4, my - meteor['size']//4), 
                             meteor['size'] // 3)
            
            # 到达目标或超出屏幕
            if dist < 20 or meteor['y'] > HEIGHT:
                # 爆炸
                self.explosions.append({
                    'x': meteor['x'], 'y': meteor['y'],
                    'radius': 0, 'max_radius': meteor['size'] * 3,
                    'color': meteor['color']
                })
                
                # 伤害敌人
                for m in list(mobs):
                    m_dist = math.hypot(m.rect.centerx - meteor['x'], m.rect.centery - meteor['y'])
                    if m_dist < meteor['size'] * 3:
                        damage = int(150 * (1 - m_dist / (meteor['size'] * 3)))
                        m.hp -= damage
                        FloatingText(m.rect.centerx, m.rect.top - 10, f"-{damage}", meteor['color'])
                        Particle(m.rect.center, meteor['color'])
                
                self.meteors.remove(meteor)
        
        # 更新爆炸
        for exp in self.explosions[:]:
            exp['radius'] += 10
            if exp['radius'] > exp['max_radius']:
                self.explosions.remove(exp)
                continue
            
            # 绘制爆炸环
            alpha = int(200 * (1 - exp['radius'] / exp['max_radius']))
            pygame.draw.circle(self.image, (*exp['color'][:3], alpha), 
                             (int(exp['x']), int(exp['y'])), int(exp['radius']), 4)


# ========== Genesis 第三大招：新星诞生 ==========
class GenesisSupernovaBlast(pygame.sprite.Sprite):
    """【新星诞生】在敌人位置创造超新星爆炸"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 150  # 2.5秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        enemy_bullets.empty()
        
        # 在每个敌人位置标记超新星
        self.supernovas = []
        for m in list(mobs):
            self.supernovas.append({
                'x': m.rect.centerx,
                'y': m.rect.centery,
                'phase': 0,  # 0=聚集 1=爆发 2=余辉
                'timer': 0,
                'radius': 0,
                'target': m
            })
        
        # 如果没有敌人，随机生成几个
        if not self.supernovas:
            for _ in range(5):
                self.supernovas.append({
                    'x': random.randint(100, WIDTH - 100),
                    'y': random.randint(100, HEIGHT - 200),
                    'phase': 0, 'timer': 0, 'radius': 0, 'target': None
                })
        
        FloatingText(owner.rect.centerx, owner.rect.top - 50, "★ 新星诞生 ★", (255, 220, 150))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        for nova in self.supernovas:
            nova['timer'] += 1
            x, y = int(nova['x']), int(nova['y'])
            
            # 阶段0：能量聚集 (40帧)
            if nova['phase'] == 0:
                progress = nova['timer'] / 40
                
                # 聚集光线
                for i in range(12):
                    angle = (i * 30 + nova['timer'] * 5) * math.pi / 180
                    length = 80 * (1 - progress)
                    sx = x + math.cos(angle) * length
                    sy = y + math.sin(angle) * length
                    pygame.draw.line(self.image, (255, 255, 200, 200), (sx, sy), (x, y), 2)
                
                # 中心聚能
                core_r = 5 + progress * 15
                pygame.draw.circle(self.image, (255, 255, 255), (x, y), int(core_r))
                pygame.draw.circle(self.image, (255, 220, 150), (x, y), int(core_r * 0.7))
                
                if nova['timer'] >= 40:
                    nova['phase'] = 1
                    nova['timer'] = 0
            
            # 阶段1：超新星爆发 (30帧)
            elif nova['phase'] == 1:
                progress = nova['timer'] / 30
                nova['radius'] = progress * 120
                
                # 爆发光环
                colors = [(255, 255, 255), (255, 255, 200), (255, 220, 150), 
                         (255, 180, 100), (255, 150, 80)]
                for i, color in enumerate(colors):
                    ring_r = nova['radius'] - i * 10
                    if ring_r > 0:
                        alpha = int(255 * (1 - progress * 0.5))
                        pygame.draw.circle(self.image, (*color, alpha), (x, y), int(ring_r), max(1, 6 - i))
                
                # 中心亮点
                pygame.draw.circle(self.image, (255, 255, 255), (x, y), int(20 * (1 - progress)))
                
                # 喷射物质
                for i in range(8):
                    angle = (i * 45) * math.pi / 180
                    jet_len = nova['radius'] + 20
                    jx = x + math.cos(angle) * jet_len
                    jy = y + math.sin(angle) * jet_len
                    pygame.draw.line(self.image, (255, 200, 100), (x, y), (jx, jy), 3)
                    pygame.draw.circle(self.image, (255, 255, 200), (int(jx), int(jy)), 5)
                
                # 伤害敌人
                for m in list(mobs):
                    dist = math.hypot(m.rect.centerx - x, m.rect.centery - y)
                    if dist < nova['radius']:
                        # 每帧造成伤害
                        m.hp -= 8
                        if nova['timer'] % 10 == 0:
                            Particle(m.rect.center, (255, 220, 150))
                
                if nova['timer'] >= 30:
                    nova['phase'] = 2
                    nova['timer'] = 0
                    # 最终爆炸伤害
                    if nova['target'] and nova['target'] in mobs:
                        nova['target'].hp -= 150
                        FloatingText(nova['target'].rect.centerx, nova['target'].rect.top - 20, 
                                   "超新星!", (255, 220, 150))
            
            # 阶段2：星云余辉 (50帧)
            elif nova['phase'] == 2:
                fade = 1 - nova['timer'] / 50
                
                # 扩散星云
                nebula_r = 120 + nova['timer'] * 2
                nebula_colors = [(255, 200, 150), (200, 150, 255), (150, 200, 255)]
                
                for i, color in enumerate(nebula_colors):
                    nr = nebula_r - i * 20
                    if nr > 0:
                        alpha = int(100 * fade)
                        pygame.draw.circle(self.image, (*color, alpha), (x, y), int(nr), 2)
                
                # 新生小星星
                if nova['timer'] % 5 == 0:
                    for _ in range(3):
                        angle = random.uniform(0, 2 * math.pi)
                        dist = random.uniform(20, nebula_r)
                        sx = x + math.cos(angle) * dist
                        sy = y + math.sin(angle) * dist
                        pygame.draw.circle(self.image, (255, 255, 200, int(200 * fade)), 
                                         (int(sx), int(sy)), random.randint(1, 3))
                
                if nova['timer'] >= 50:
                    self.supernovas.remove(nova)


# ========== Truth 至尊·世界的真相 大招类 ==========

class TruthRevelation(pygame.sprite.Sprite):
    """【真理显现】V键大招 - 全知之眼审视一切，揭示并制裁所有敌人"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 300  # 5秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        enemy_bullets.empty()
        
        # 颜色定义
        self.TRUTH_WHITE = (255, 255, 255)
        self.TRUTH_BLACK = (20, 20, 30)
        self.TRUTH_GOLD = (255, 215, 0)
        
        self.phase = 0  # 0=眼睛睁开 1=扫描 2=审判 3=消散
        self.eye_open = 0  # 眼睛睁开程度 0-1
        self.scan_angle = 0  # 扫描角度
        self.judgment_targets = []  # 审判目标
        self.hit_enemies = set()
        
        FloatingText(owner.rect.centerx, owner.rect.top - 60, "◆◆◆ 真理显现 ◆◆◆", self.TRUTH_GOLD)
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        cx, cy = WIDTH // 2, HEIGHT // 3
        
        # 阶段1: 眼睛睁开 (60帧)
        if self.life > 240:
            self.phase = 0
            self.eye_open = min(1.0, (300 - self.life) / 60)
            
            # 绘制巨大的眼睛
            eye_w = 300 * self.eye_open
            eye_h = 120 * self.eye_open
            
            # 眼眶
            if eye_h > 5:
                pygame.draw.ellipse(self.image, self.TRUTH_GOLD, 
                                  (cx - eye_w//2, cy - eye_h//2, eye_w, eye_h), 5)
                
                # 眼白
                pygame.draw.ellipse(self.image, self.TRUTH_WHITE, 
                                  (cx - eye_w//2 + 10, cy - eye_h//2 + 5, eye_w - 20, eye_h - 10))
                
                # 虹膜
                iris_r = int(40 * self.eye_open)
                pygame.draw.circle(self.image, self.TRUTH_GOLD, (cx, cy), iris_r)
                
                # 瞳孔
                pupil_r = int(20 * self.eye_open)
                pygame.draw.circle(self.image, self.TRUTH_BLACK, (cx, cy), pupil_r)
                
                # 高光
                pygame.draw.circle(self.image, self.TRUTH_WHITE, (cx - 15, cy - 10), int(8 * self.eye_open))
        
        # 阶段2: 扫描全屏 (100帧)
        elif self.life > 140:
            self.phase = 1
            self.scan_angle += 6
            
            # 保持眼睛
            eye_w, eye_h = 300, 120
            pygame.draw.ellipse(self.image, self.TRUTH_GOLD, 
                              (cx - eye_w//2, cy - eye_h//2, eye_w, eye_h), 5)
            pygame.draw.ellipse(self.image, self.TRUTH_WHITE, 
                              (cx - eye_w//2 + 10, cy - eye_h//2 + 5, eye_w - 20, eye_h - 10))
            pygame.draw.circle(self.image, self.TRUTH_GOLD, (cx, cy), 40)
            pygame.draw.circle(self.image, self.TRUTH_BLACK, (cx, cy), 20)
            pygame.draw.circle(self.image, self.TRUTH_WHITE, (cx - 15, cy - 10), 8)
            
            # 扫描光束
            for i in range(3):
                beam_angle = (self.scan_angle + i * 120) * math.pi / 180
                beam_len = 600
                bx = cx + math.cos(beam_angle) * beam_len
                by = cy + math.sin(beam_angle) * beam_len
                
                # 多层光束
                for w, alpha in [(30, 50), (20, 100), (10, 180), (4, 255)]:
                    pygame.draw.line(self.image, (*self.TRUTH_GOLD, alpha), (cx, cy), (int(bx), int(by)), w)
            
            # 扫描到的敌人被标记
            for m in list(mobs):
                mx, my = m.rect.center
                enemy_angle = math.atan2(my - cy, mx - cx)
                for i in range(3):
                    beam_angle = (self.scan_angle + i * 120) * math.pi / 180
                    angle_diff = abs(enemy_angle - beam_angle)
                    if angle_diff > math.pi:
                        angle_diff = 2 * math.pi - angle_diff
                    if angle_diff < 0.3 and m not in self.judgment_targets:
                        self.judgment_targets.append(m)
                        FloatingText(mx, my - 20, "☉揭示☉", self.TRUTH_GOLD)
        
        # 阶段3: 审判 (100帧)
        elif self.life > 40:
            self.phase = 2
            progress = (140 - self.life) / 100
            
            # 眼睛变红
            eye_w, eye_h = 300, 120
            pygame.draw.ellipse(self.image, (255, 100, 50), 
                              (cx - eye_w//2, cy - eye_h//2, eye_w, eye_h), 5)
            pygame.draw.ellipse(self.image, self.TRUTH_WHITE, 
                              (cx - eye_w//2 + 10, cy - eye_h//2 + 5, eye_w - 20, eye_h - 10))
            pygame.draw.circle(self.image, (255, 100, 50), (cx, cy), 40)
            pygame.draw.circle(self.image, self.TRUTH_BLACK, (cx, cy), 20)
            
            # 对每个标记的敌人发射审判光线
            for m in self.judgment_targets:
                if m.alive() and m not in self.hit_enemies:
                    mx, my = m.rect.center
                    
                    # 审判光线
                    for w, alpha in [(15, 80), (10, 150), (5, 255)]:
                        pygame.draw.line(self.image, (*self.TRUTH_GOLD, alpha), (cx, cy), (mx, my), w)
                    
                    # 目标标记
                    pygame.draw.circle(self.image, self.TRUTH_GOLD, (mx, my), 30, 3)
                    pygame.draw.line(self.image, self.TRUTH_GOLD, (mx - 20, my), (mx + 20, my), 2)
                    pygame.draw.line(self.image, self.TRUTH_GOLD, (mx, my - 20), (mx, my + 20), 2)
                    
                    # 持续伤害
                    if self.life % 10 == 0:
                        m.hp -= 35
                        Particle(m.rect.center, self.TRUTH_GOLD)
            
            # 最终审判
            if self.life == 50:
                for m in self.judgment_targets:
                    if m.alive():
                        self.hit_enemies.add(m)
                        m.hp -= 200
                        FloatingText(m.rect.centerx, m.rect.top - 30, "真理裁决!", self.TRUTH_GOLD)
                        for _ in range(5):
                            Particle(m.rect.center, random.choice([self.TRUTH_GOLD, self.TRUTH_WHITE]))
        
        # 阶段4: 眼睛闭合 (40帧)
        else:
            self.phase = 3
            close_progress = (40 - self.life) / 40
            
            eye_w = 300 * (1 - close_progress)
            eye_h = 120 * (1 - close_progress)
            
            if eye_h > 5:
                pygame.draw.ellipse(self.image, self.TRUTH_GOLD, 
                                  (cx - eye_w//2, cy - eye_h//2, eye_w, eye_h), int(5 * (1 - close_progress)))


class TruthYinYangReverse(pygame.sprite.Sprite):
    """【阴阳逆转】F键大招 - 切换阴阳极性，释放对应属性波动"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180  # 3秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        
        self.TRUTH_WHITE = (255, 255, 255)
        self.TRUTH_BLACK = (20, 20, 30)
        self.TRUTH_GOLD = (255, 215, 0)
        
        # 判断当前阴阳状态并逆转
        if hasattr(owner, 'truth_yin_yang_balance'):
            self.is_yang = owner.truth_yin_yang_balance >= 0
            owner.truth_yin_yang_balance = -owner.truth_yin_yang_balance  # 逆转
        else:
            self.is_yang = True
        
        self.rotation = 0
        self.wave_radius = 0
        self.projectiles = []
        
        mode_name = "阳极" if self.is_yang else "阴极"
        mode_color = self.TRUTH_WHITE if self.is_yang else self.TRUTH_BLACK
        FloatingText(owner.rect.centerx, owner.rect.top - 50, f"◆ {mode_name}逆转 ◆", mode_color)
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.owner.rect.centerx, self.owner.rect.centery
        self.rotation += 8
        
        # 太极旋转
        taiji_r = 80
        
        # 阴阳鱼
        for i in range(2):
            color = self.TRUTH_WHITE if (i == 0) == self.is_yang else self.TRUTH_BLACK
            start_angle = self.rotation + i * 180
            
            # 半圆
            pts = [(cx, cy)]
            for j in range(19):
                angle = (start_angle + j * 10) * math.pi / 180
                pts.append((cx + math.cos(angle) * taiji_r, cy + math.sin(angle) * taiji_r))
            pygame.draw.polygon(self.image, color, pts)
            
            # 小圆
            small_angle = (start_angle + 90) * math.pi / 180
            sx = cx + math.cos(small_angle) * (taiji_r // 2)
            sy = cy + math.sin(small_angle) * (taiji_r // 2)
            pygame.draw.circle(self.image, color, (int(sx), int(sy)), taiji_r // 2)
            
            # 鱼眼
            eye_color = self.TRUTH_BLACK if color == self.TRUTH_WHITE else self.TRUTH_WHITE
            pygame.draw.circle(self.image, eye_color, (int(sx), int(sy)), taiji_r // 6)
        
        # 外圈
        pygame.draw.circle(self.image, self.TRUTH_GOLD, (cx, cy), taiji_r + 5, 4)
        
        # 发射弹幕
        if self.life % 15 == 0:
            for i in range(8):
                angle = self.rotation + i * 45
                color = self.TRUTH_WHITE if self.is_yang else self.TRUTH_BLACK
                self.projectiles.append({
                    'x': cx, 'y': cy,
                    'angle': angle,
                    'speed': 10,
                    'color': color,
                    'life': 60
                })
        
        # 更新弹幕
        for proj in self.projectiles[:]:
            rad = proj['angle'] * math.pi / 180
            proj['x'] += math.cos(rad) * proj['speed']
            proj['y'] += math.sin(rad) * proj['speed']
            proj['life'] -= 1
            
            if proj['life'] <= 0:
                self.projectiles.remove(proj)
                continue
            
            # 绘制
            px, py = int(proj['x']), int(proj['y'])
            pygame.draw.circle(self.image, proj['color'], (px, py), 12)
            pygame.draw.circle(self.image, self.TRUTH_GOLD, (px, py), 12, 2)
            
            # 碰撞
            for m in list(mobs):
                if math.hypot(m.rect.centerx - px, m.rect.centery - py) < 25:
                    damage = 80 if self.is_yang else 60
                    m.hp -= damage
                    
                    if self.is_yang:
                        FloatingText(m.rect.centerx, m.rect.top - 10, "阳!", self.TRUTH_WHITE)
                    else:
                        # 阴极：减速
                        if hasattr(m, 'speed'):
                            m.speed = max(0.5, m.speed * 0.6)
                        FloatingText(m.rect.centerx, m.rect.top - 10, "阴!", self.TRUTH_BLACK)
                    
                    Particle(m.rect.center, proj['color'])
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    break


class TruthAbsoluteJudgment(pygame.sprite.Sprite):
    """【绝对审判】G键大招 - 对所有敌人执行真理裁决"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180  # 3秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        sound_mgr.play("nuke")
        enemy_bullets.empty()
        
        self.TRUTH_WHITE = (255, 255, 255)
        self.TRUTH_BLACK = (20, 20, 30)
        self.TRUTH_GOLD = (255, 215, 0)
        
        # 收集所有敌人作为审判目标
        self.targets = []
        for m in list(mobs):
            # 检查是否被标记（增加伤害）
            is_marked = False
            if hasattr(owner, 'truth_marked_enemies') and m in owner.truth_marked_enemies:
                is_marked = True
            self.targets.append({
                'enemy': m,
                'x': m.rect.centerx,
                'y': m.rect.centery,
                'marked': is_marked,
                'judged': False
            })
        
        self.judgment_wave = 0
        self.symbols = []  # 真言符文
        
        # 生成环绕符文
        for i in range(12):
            angle = i * 30
            self.symbols.append({
                'angle': angle,
                'dist': 150,
                'char': ['真', '理', '审', '判', '至', '尊', '洞', '察', '揭', '示', '裁', '决'][i]
            })
        
        FloatingText(owner.rect.centerx, owner.rect.top - 50, "★ 绝对审判 ★", self.TRUTH_GOLD)
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        cx, cy = WIDTH // 2, HEIGHT // 2
        
        # 背景暗化
        dark_alpha = min(150, (180 - self.life) * 3)
        pygame.draw.rect(self.image, (0, 0, 0, dark_alpha), (0, 0, WIDTH, HEIGHT))
        
        # 旋转符文环
        for sym in self.symbols:
            sym['angle'] += 2
            rad = sym['angle'] * math.pi / 180
            sx = cx + math.cos(rad) * sym['dist']
            sy = cy + math.sin(rad) * sym['dist']
            
            # 符文光点
            pygame.draw.circle(self.image, self.TRUTH_GOLD, (int(sx), int(sy)), 15)
            pygame.draw.circle(self.image, self.TRUTH_WHITE, (int(sx), int(sy)), 10)
        
        # 中央之眼
        eye_size = 60 + 10 * abs(math.sin(self.life * 0.1))
        pygame.draw.ellipse(self.image, self.TRUTH_GOLD, 
                          (cx - eye_size, cy - eye_size//2, eye_size * 2, eye_size), 5)
        pygame.draw.ellipse(self.image, self.TRUTH_WHITE, 
                          (cx - eye_size + 5, cy - eye_size//2 + 3, eye_size * 2 - 10, eye_size - 6))
        pygame.draw.circle(self.image, self.TRUTH_GOLD, (cx, cy), 25)
        pygame.draw.circle(self.image, self.TRUTH_BLACK, (cx, cy), 15)
        pygame.draw.circle(self.image, self.TRUTH_WHITE, (cx - 8, cy - 5), 5)
        
        # 审判目标
        self.judgment_wave += 1
        
        for i, target in enumerate(self.targets):
            enemy = target['enemy']
            if not enemy.alive():
                continue
            
            tx, ty = enemy.rect.centerx, enemy.rect.centery
            
            # 瞄准线
            pygame.draw.line(self.image, (*self.TRUTH_GOLD, 150), (cx, cy), (tx, ty), 2)
            
            # 目标环
            ring_pulse = abs(math.sin(self.life * 0.2 + i))
            ring_r = 25 + 10 * ring_pulse
            pygame.draw.circle(self.image, self.TRUTH_GOLD, (tx, ty), int(ring_r), 3)
            
            # 标记增强显示
            if target['marked']:
                pygame.draw.circle(self.image, (255, 100, 50), (tx, ty), int(ring_r + 10), 2)
            
            # 执行审判
            if not target['judged']:
                # 按波次审判
                wave_delay = i * 5
                if self.judgment_wave > wave_delay and self.judgment_wave <= wave_delay + 30:
                    # 审判光柱
                    pillar_h = (self.judgment_wave - wave_delay) * 20
                    pygame.draw.rect(self.image, (*self.TRUTH_GOLD, 200), 
                                   (tx - 15, ty - pillar_h, 30, pillar_h))
                    pygame.draw.rect(self.image, self.TRUTH_WHITE, 
                                   (tx - 10, ty - pillar_h, 20, pillar_h))
                    
                    # 伤害
                    if (self.judgment_wave - wave_delay) % 10 == 0:
                        base_damage = 50
                        if target['marked']:
                            base_damage = int(base_damage * 1.5)  # 标记增伤
                        enemy.hp -= base_damage
                        Particle(enemy.rect.center, self.TRUTH_GOLD)
                
                elif self.judgment_wave > wave_delay + 30:
                    target['judged'] = True
                    # 最终审判
                    final_damage = 100
                    if target['marked']:
                        final_damage = int(final_damage * 2.0)
                        FloatingText(tx, ty - 30, "真相裁决!", (255, 100, 50))
                    else:
                        FloatingText(tx, ty - 30, "审判!", self.TRUTH_GOLD)
                    enemy.hp -= final_damage
                    for _ in range(8):
                        Particle(enemy.rect.center, random.choice([self.TRUTH_GOLD, self.TRUTH_WHITE]))

# ========== ����ն���� ���� ==========

class AsuraSixArmSlash(pygame.sprite.Sprite):
    """����������ն - �ٻ���ֻ�޴󽣱۽���ȫ��ն�� (V��)"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 90
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.hit_enemies = {}
        self.ASURA_RED = (180, 50, 50)
        self.ASURA_CRIMSON = (255, 80, 80)
        self.ASURA_GOLD = (255, 200, 100)
        self.arms = []
        for i in range(6):
            self.arms.append({'angle': i * 60, 'length': 0, 'max_length': 350, 'phase': 'extend', 'slash_angle': 0, 'color': self.ASURA_RED if i % 2 == 0 else self.ASURA_CRIMSON})
        sound_mgr.play("laser")
        if hasattr(owner, 'asura_sword_qi'):
            owner.asura_sword_qi = min(owner.asura_sword_qi_max, owner.asura_sword_qi + 30)
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.owner.rect.center
        eye_pulse = math.sin(self.life * 0.3) * 10 + 50
        pygame.draw.circle(self.image, self.ASURA_GOLD, (cx, cy), int(eye_pulse), 3)
        pygame.draw.circle(self.image, self.ASURA_CRIMSON, (cx, cy), int(eye_pulse * 0.7), 2)
        pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 8)
        for arm in self.arms:
            if arm['phase'] == 'extend':
                arm['length'] = min(arm['max_length'], arm['length'] + 20)
                if arm['length'] >= arm['max_length']: arm['phase'] = 'slash'
            elif arm['phase'] == 'slash':
                arm['slash_angle'] += 8
                if arm['slash_angle'] >= 90: arm['phase'] = 'retract'
            elif arm['phase'] == 'retract':
                arm['length'] = max(0, arm['length'] - 15)
            base_angle = arm['angle'] + arm['slash_angle']
            rad = math.radians(base_angle)
            tip_x = cx + math.cos(rad) * arm['length']
            tip_y = cy + math.sin(rad) * arm['length']
            points = []
            for t in range(int(arm['length'] // 10) + 1):
                prog = t / max(1, arm['length'] // 10)
                r = arm['length'] * prog
                px = cx + math.cos(rad) * r
                py = cy + math.sin(rad) * r
                points.append((px, py))
            if len(points) > 2:
                pygame.draw.lines(self.image, arm['color'], False, points, 8)
                pygame.draw.lines(self.image, (255, 200, 180), False, points, 4)
                pygame.draw.lines(self.image, (255, 255, 255), False, points, 2)
            pygame.draw.circle(self.image, self.ASURA_GOLD, (int(tip_x), int(tip_y)), 10)
            pygame.draw.circle(self.image, (255, 255, 255), (int(tip_x), int(tip_y)), 5)
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                if dist < arm['length']:
                    angle_to_enemy = math.degrees(math.atan2(m.rect.centery - cy, m.rect.centerx - cx))
                    angle_diff = abs((angle_to_enemy - base_angle + 180) % 360 - 180)
                    if angle_diff < 20:
                        if m not in self.hit_enemies: self.hit_enemies[m] = 0
                        self.hit_enemies[m] += 1
                        if self.hit_enemies[m] % 3 == 1:
                            m.hp -= 180
                            FloatingText(m.rect.centerx, m.rect.top - 20, "ն!", self.ASURA_GOLD)
                            Particle(m.rect.center, arm['color'])
        if self.life % 5 == 0:
            for arm in self.arms:
                rad = math.radians(arm['angle'] + arm['slash_angle'])
                for dist in range(50, int(arm['length']), 50):
                    px = cx + math.cos(rad) * dist
                    py = cy + math.sin(rad) * dist
                    Particle((px, py), self.ASURA_RED)


class AsuraRageMode(pygame.sprite.Sprite):
    """����ŭ����� - �����״̬��ȫ�������籩 (F��)"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 120
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.ASURA_RED = (180, 50, 50)
        self.ASURA_CRIMSON = (255, 80, 80)
        self.ASURA_GOLD = (255, 200, 100)
        self.sword_waves = []
        self.wave_timer = 0
        sound_mgr.play("nuke")
        if hasattr(owner, 'asura_rage_mode'):
            owner.asura_rage_mode = True
            owner.asura_rage_timer = 300
            owner.asura_sword_qi = owner.asura_sword_qi_max
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.owner.rect.center
        rage_intensity = (120 - self.life) / 120
        for r in range(3):
            ring_r = 100 + r * 80 + int(math.sin(self.life * 0.2) * 20)
            alpha = int(100 * (1 - r * 0.3) * rage_intensity)
            ring_surf = pygame.Surface((ring_r * 2, ring_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*self.ASURA_RED, alpha), (ring_r, ring_r), ring_r, 5)
            self.image.blit(ring_surf, (cx - ring_r, cy - ring_r))
        self.wave_timer += 1
        if self.wave_timer >= 8:
            self.wave_timer = 0
            for i in range(12):
                angle = i * 30 + random.randint(-10, 10)
                self.sword_waves.append({'x': cx, 'y': cy, 'angle': angle, 'speed': 15 + random.randint(0, 5), 'life': 40, 'size': random.randint(30, 50)})
        for wave in self.sword_waves[:]:
            wave['life'] -= 1
            if wave['life'] <= 0: self.sword_waves.remove(wave); continue
            rad = math.radians(wave['angle'])
            wave['x'] += math.cos(rad) * wave['speed']
            wave['y'] += math.sin(rad) * wave['speed']
            wx, wy = int(wave['x']), int(wave['y'])
            wave_pts = []
            for t in range(5):
                prog = t / 4
                dist = wave['size'] * (1 - prog)
                px = wx - math.cos(rad) * dist
                py = wy - math.sin(rad) * dist
                wave_pts.append((int(px), int(py)))
            if len(wave_pts) > 1:
                pygame.draw.lines(self.image, self.ASURA_CRIMSON, False, wave_pts, 6)
                pygame.draw.lines(self.image, self.ASURA_GOLD, False, wave_pts, 3)
            for m in list(mobs):
                if math.hypot(m.rect.centerx - wx, m.rect.centery - wy) < 40:
                    m.hp -= 60
                    Particle(m.rect.center, self.ASURA_CRIMSON)
        mark_size = 60 + int(math.sin(self.life * 0.5) * 10)
        pygame.draw.circle(self.image, self.ASURA_GOLD, (cx, cy), mark_size, 4)
        for i in range(6):
            angle = i * 60 + self.life * 3
            rad = math.radians(angle)
            px = cx + math.cos(rad) * mark_size
            py = cy + math.sin(rad) * mark_size
            pygame.draw.circle(self.image, (255, 255, 255), (int(px), int(py)), 8)


class AsuraDragonSlayer(pygame.sprite.Sprite):
    """����ն����ɱ - ������н������һ����ɱ (G��)"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 100
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.ASURA_RED = (180, 50, 50)
        self.ASURA_CRIMSON = (255, 80, 80)
        self.ASURA_GOLD = (255, 200, 100)
        self.slash_targets = []
        self.slash_lines = []
        sound_mgr.play("nuke")
        for m in list(mobs):
            self.slash_targets.append({'enemy': m, 'x': m.rect.centerx, 'y': m.rect.centery, 'marked': False, 'slashed': False})
        if hasattr(owner, 'asura_sword_qi'):
            self.qi_bonus = owner.asura_sword_qi / 100
            owner.asura_sword_qi = 0
        else:
            self.qi_bonus = 0.5
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.owner.rect.center
        if self.life > 70:
            charge_prog = (100 - self.life) / 30
            for target in self.slash_targets:
                if target['enemy'].alive():
                    target['x'] = target['enemy'].rect.centerx
                    target['y'] = target['enemy'].rect.centery
                line_alpha = int(200 * charge_prog)
                tx, ty = target['x'], target['y']
                pygame.draw.line(self.image, (*self.ASURA_RED, min(255, line_alpha)), (cx, cy), (tx, ty), 2)
                if not target['marked']:
                    mark_r = 40 - int(30 * charge_prog)
                    pygame.draw.circle(self.image, self.ASURA_CRIMSON, (tx, ty), mark_r, 2)
                    if charge_prog >= 0.9:
                        target['marked'] = True
                        FloatingText(tx, ty - 20, "����", self.ASURA_GOLD)
            charge_r = int(100 * charge_prog)
            pygame.draw.circle(self.image, self.ASURA_GOLD, (cx, cy), charge_r, 3)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), int(charge_r * 0.5))
        elif self.life > 30:
            for i, target in enumerate(self.slash_targets):
                if target['slashed']: continue
                delay = i * 2
                if (70 - self.life) < delay: continue
                tx, ty = target['x'], target['y']
                slash_dist = math.hypot(tx - cx, ty - cy)
                current_dist = slash_dist * min(1.0, (70 - self.life - delay) / 10)
                angle = math.atan2(ty - cy, tx - cx)
                sx = cx + math.cos(angle) * current_dist
                sy = cy + math.sin(angle) * current_dist
                pygame.draw.line(self.image, self.ASURA_GOLD, (cx, cy), (sx, sy), 4)
                pygame.draw.line(self.image, (255, 255, 255), (cx, cy), (sx, sy), 2)
                pygame.draw.circle(self.image, self.ASURA_CRIMSON, (int(sx), int(sy)), 15)
                if current_dist >= slash_dist - 20:
                    target['slashed'] = True
                    self.slash_lines.append({'x1': cx, 'y1': cy, 'x2': tx, 'y2': ty, 'life': 30})
                    if target['enemy'].alive():
                        damage = int(500 * (1 + self.qi_bonus))
                        target['enemy'].hp -= damage
                        FloatingText(tx, ty - 30, "ն��!", self.ASURA_GOLD)
                        for _ in range(10): Particle((tx, ty), self.ASURA_CRIMSON)
        else:
            for line in self.slash_lines[:]:
                line['life'] -= 1
                if line['life'] <= 0: self.slash_lines.remove(line); continue
                alpha = int(255 * (line['life'] / 30))
                pygame.draw.line(self.image, (*self.ASURA_RED, alpha), (line['x1'], line['y1']), (line['x2'], line['y2']), 3)
            if self.life == 29:
                for _ in range(30): Particle(self.owner.rect.center, random.choice([self.ASURA_RED, self.ASURA_CRIMSON, self.ASURA_GOLD]))


# ========== ����ʿ������� ���� ==========

class DragoonSkyDive(pygame.sprite.Sprite):
    """����ʿ�������� - ���������ǿ��ͻ�� (V��)"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 80
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.DRAGOON_BLUE = (100, 150, 220)
        self.DRAGOON_LIGHT = (180, 210, 255)
        self.DRAGOON_WHITE = (255, 255, 255)
        self.DRAGOON_GOLD = (255, 220, 150)
        self.dive_y = 0
        self.impact_wave = 0
        self.hit_enemies = set()
        self.start_x = owner.rect.centerx
        self.start_y = owner.rect.centery
        sound_mgr.play("laser")
        if hasattr(owner, 'dragoon_sky_dive'):
            owner.dragoon_sky_dive = True
            owner.dragoon_dive_timer = 180
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.image.fill((0, 0, 0, 0))
        if self.life > 60:
            rise_prog = (80 - self.life) / 20
            self.dive_y = -200 * rise_prog
            cx = self.start_x
            cy = self.start_y + self.dive_y
            for r in range(3):
                ring_r = 30 + r * 20
                alpha = int(200 * (1 - r * 0.3))
                pygame.draw.circle(self.image, (*self.DRAGOON_LIGHT, alpha), (cx, int(cy)), ring_r, 2)
            for i in range(5):
                trail_y = cy + i * 30
                trail_alpha = int(200 * (1 - i * 0.2))
                pygame.draw.circle(self.image, (*self.DRAGOON_BLUE, trail_alpha), (cx, int(trail_y)), 15 - i * 2)
        elif self.life > 20:
            dive_prog = (60 - self.life) / 40
            self.dive_y = -200 + 400 * dive_prog
            cx = self.start_x
            cy = self.start_y + self.dive_y
            lance_len = 150
            pygame.draw.polygon(self.image, self.DRAGOON_GOLD, [(cx, cy - lance_len), (cx - 15, cy), (cx + 15, cy)])
            pygame.draw.polygon(self.image, self.DRAGOON_WHITE, [(cx, cy - lance_len + 20), (cx - 8, cy - 10), (cx + 8, cy - 10)])
            for i in range(10):
                line_x = cx + random.randint(-50, 50)
                line_y = cy - random.randint(50, 200)
                pygame.draw.line(self.image, self.DRAGOON_LIGHT, (line_x, line_y), (line_x, line_y + 50), 2)
            for m in list(mobs):
                if m in self.hit_enemies: continue
                if abs(m.rect.centerx - cx) < 60 and abs(m.rect.centery - cy) < 100:
                    m.hp -= 300
                    self.hit_enemies.add(m)
                    FloatingText(m.rect.centerx, m.rect.top - 20, "ͻ��!", self.DRAGOON_GOLD)
                    for _ in range(8): Particle(m.rect.center, self.DRAGOON_LIGHT)
        else:
            self.impact_wave += 15
            cx = self.start_x
            cy = self.start_y + 200
            wave_alpha = int(200 * (self.life / 20))
            pygame.draw.circle(self.image, (*self.DRAGOON_GOLD, wave_alpha), (cx, int(cy)), self.impact_wave, 5)
            pygame.draw.circle(self.image, (*self.DRAGOON_WHITE, wave_alpha // 2), (cx, int(cy)), self.impact_wave + 20, 3)
            for m in list(mobs):
                dist = math.hypot(m.rect.centerx - cx, m.rect.centery - cy)
                if abs(dist - self.impact_wave) < 30 and m not in self.hit_enemies:
                    m.hp -= 150
                    self.hit_enemies.add(m)
                    Particle(m.rect.center, self.DRAGOON_LIGHT)


class DragoonLanceStorm(pygame.sprite.Sprite):
    """����ʿ��ǹ�뷢 - �ٻ�������ǹ������� (F��)"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 100
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.DRAGOON_BLUE = (100, 150, 220)
        self.DRAGOON_LIGHT = (180, 210, 255)
        self.DRAGOON_WHITE = (255, 255, 255)
        self.DRAGOON_GOLD = (255, 220, 150)
        self.lances = []
        self.spawn_timer = 0
        sound_mgr.play("nuke")
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.image.fill((0, 0, 0, 0))
        self.spawn_timer += 1
        if self.spawn_timer >= 5 and self.life > 30:
            self.spawn_timer = 0
            for _ in range(random.randint(3, 5)):
                if mobs and random.random() < 0.7:
                    target = random.choice(list(mobs))
                    tx, ty = target.rect.centerx, target.rect.centery
                else:
                    tx = random.randint(50, WIDTH - 50)
                    ty = random.randint(100, HEIGHT - 100)
                self.lances.append({'x': tx + random.randint(-30, 30), 'y': -50, 'target_y': ty, 'speed': random.randint(15, 25), 'hit': False, 'impact_life': 0})
        for lance in self.lances[:]:
            if lance['hit']:
                lance['impact_life'] -= 1
                if lance['impact_life'] <= 0: self.lances.remove(lance); continue
                alpha = int(255 * (lance['impact_life'] / 15))
                pygame.draw.circle(self.image, (*self.DRAGOON_GOLD, alpha), (int(lance['x']), int(lance['target_y'])), 20 - lance['impact_life'])
            else:
                lance['y'] += lance['speed']
                lx, ly = int(lance['x']), int(lance['y'])
                pygame.draw.polygon(self.image, self.DRAGOON_WHITE, [(lx, ly - 40), (lx - 5, ly), (lx + 5, ly)])
                pygame.draw.polygon(self.image, self.DRAGOON_BLUE, [(lx, ly - 40), (lx - 5, ly), (lx + 5, ly)], 2)
                for i in range(3):
                    trail_alpha = int(150 * (1 - i * 0.3))
                    pygame.draw.line(self.image, (*self.DRAGOON_LIGHT, trail_alpha), (lx, ly - 40 - i * 20), (lx, ly - 40 - i * 20 - 15), 2)
                if lance['y'] >= lance['target_y']:
                    lance['hit'] = True
                    lance['impact_life'] = 15
                    for m in list(mobs):
                        dist = math.hypot(m.rect.centerx - lance['x'], m.rect.centery - lance['target_y'])
                        if dist < 50:
                            m.hp -= 120
                            FloatingText(m.rect.centerx, m.rect.top - 15, "��!", self.DRAGOON_LIGHT)
                            Particle(m.rect.center, self.DRAGOON_BLUE)


class DragoonDragonCharge(pygame.sprite.Sprite):
    """����ʿ������ - �����������йᴩ��� (G��)"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 90
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.DRAGOON_BLUE = (100, 150, 220)
        self.DRAGOON_LIGHT = (180, 210, 255)
        self.DRAGOON_WHITE = (255, 255, 255)
        self.DRAGOON_GOLD = (255, 220, 150)
        self.rush_progress = 0
        self.hit_enemies = set()
        self.dragon_trail = []
        sound_mgr.play("nuke")
        if hasattr(owner, 'dragoon_lance_level'):
            owner.dragoon_lance_level = min(owner.dragoon_max_lance_level, owner.dragoon_lance_level + 2)
        
    def update(self):
        self.life -= 1
        if self.life <= 0: self.kill(); return
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.owner.rect.center
        if self.life > 70:
            charge_prog = (90 - self.life) / 20
            dragon_r = int(150 * charge_prog)
            for i in range(3):
                ring_alpha = int(150 * (1 - i * 0.3) * charge_prog)
                r = dragon_r + i * 30
                pygame.draw.circle(self.image, (*self.DRAGOON_LIGHT, ring_alpha), (cx, cy), r, 3)
            eye_y = cy - int(50 * charge_prog)
            pygame.draw.circle(self.image, self.DRAGOON_GOLD, (cx - 30, eye_y), 10)
            pygame.draw.circle(self.image, self.DRAGOON_GOLD, (cx + 30, eye_y), 10)
            pygame.draw.circle(self.image, (255, 255, 255), (cx - 30, eye_y), 5)
            pygame.draw.circle(self.image, (255, 255, 255), (cx + 30, eye_y), 5)
            if self.life == 71: FloatingText(cx, cy - 80, "�������", self.DRAGOON_GOLD)
        elif self.life > 20:
            self.rush_progress += 20
            rush_y = cy - self.rush_progress
            self.dragon_trail.append({'x': cx, 'y': rush_y, 'life': 20})
            head_y = max(-100, rush_y)
            pygame.draw.polygon(self.image, self.DRAGOON_GOLD, [(cx, head_y - 50), (cx - 40, head_y + 20), (cx + 40, head_y + 20)])
            pygame.draw.polygon(self.image, self.DRAGOON_WHITE, [(cx, head_y - 30), (cx - 20, head_y + 10), (cx + 20, head_y + 10)])
            pygame.draw.polygon(self.image, self.DRAGOON_LIGHT, [(cx - 30, head_y), (cx - 50, head_y - 40), (cx - 20, head_y - 10)])
            pygame.draw.polygon(self.image, self.DRAGOON_LIGHT, [(cx + 30, head_y), (cx + 50, head_y - 40), (cx + 20, head_y - 10)])
            for trail in self.dragon_trail[:]:
                trail['life'] -= 1
                if trail['life'] <= 0: self.dragon_trail.remove(trail); continue
                alpha = int(200 * (trail['life'] / 20))
                size = int(40 * (trail['life'] / 20))
                pygame.draw.ellipse(self.image, (*self.DRAGOON_BLUE, alpha), (trail['x'] - size, trail['y'] - size//2, size*2, size))
            for m in list(mobs):
                if m in self.hit_enemies: continue
                if abs(m.rect.centerx - cx) < 80:
                    if m.rect.centery <= cy and m.rect.centery >= rush_y - 50:
                        m.hp -= 400
                        self.hit_enemies.add(m)
                        FloatingText(m.rect.centerx, m.rect.top - 30, "����!", self.DRAGOON_GOLD)
                        for _ in range(12): Particle(m.rect.center, self.DRAGOON_LIGHT)
        else:
            fade_alpha = int(200 * (self.life / 20))
            for trail in self.dragon_trail[:]:
                trail['life'] -= 1
                if trail['life'] <= 0: self.dragon_trail.remove(trail); continue
                alpha = min(fade_alpha, int(150 * (trail['life'] / 20)))
                size = int(30 * (trail['life'] / 20))
                pygame.draw.ellipse(self.image, (*self.DRAGOON_GOLD, alpha), (trail['x'] - size, trail['y'] - size//2, size*2, size))
            if self.life == 19:
                FloatingText(cx, cy - 50, "龙影归来!", self.DRAGOON_GOLD)
                if hasattr(self.owner, 'hp'): self.owner.hp = min(getattr(self.owner, 'max_hp', 200), self.owner.hp + 30)


# ============================================================================
# 剑气/枪气子弹系统 - Asura 修罗剑气 和 Dragoon 龙骑枪气
# ============================================================================

class SwordQi(pygame.sprite.Sprite):
    """修罗剑气 - 向前飞行的剑形弹幕"""
    
    def __init__(self, x, y, color=(255, 80, 80), damage=30, angle=0):
        super().__init__()
        all_sprites.add(self)
        bullets.add(self)
        
        self.damage = damage
        self.piercing = 2
        self.is_enemy = False
        
        # 创建剑气图像
        self.image = pygame.Surface((10, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, color, [(5, 0), (0, 35), (10, 35)])
        pygame.draw.polygon(self.image, (255, 255, 255), [(5, 5), (3, 30), (7, 30)])
        
        # 旋转
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, -angle)
        
        self.rect = self.image.get_rect(center=(x, y))
        
        # 速度
        rad = math.radians(angle - 90)
        self.vx = math.cos(rad) * 12
        self.vy = math.sin(rad) * 12
    
    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.bottom < -50 or self.rect.top > HEIGHT + 50:
            self.kill()
        if self.rect.right < -50 or self.rect.left > WIDTH + 50:
            self.kill()


class LanceQi(pygame.sprite.Sprite):
    """龙骑枪气 - 向前飞行的枪形弹幕"""
    
    def __init__(self, x, y, color=(150, 200, 255), damage=40):
        super().__init__()
        all_sprites.add(self)
        bullets.add(self)
        
        self.damage = damage
        self.piercing = 3
        self.is_enemy = False
        
        # 创建枪气图像
        self.image = pygame.Surface((8, 50), pygame.SRCALPHA)
        # 枪头
        pygame.draw.polygon(self.image, color, [(4, 0), (0, 15), (8, 15)])
        # 枪身
        pygame.draw.rect(self.image, color, (2, 15, 4, 35))
        pygame.draw.rect(self.image, (255, 255, 255), (3, 15, 2, 35))
        
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.vy = -14
    
    def update(self):
        self.rect.y += self.vy
        if self.rect.bottom < -50:
            self.kill()


# ============================================================================
# 折纸鹤·零式大招 - 纸鹤群 & 千羽护盾
# ============================================================================

class OrigamiCraneSwarm(pygame.sprite.Sprite):
    """折纸鹤大招 - 纸鹤群：召唤7只AI纸鹤无人机 (V键)"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 360  # 6秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # 颜色
        self.ORIGAMI_WHITE = (245, 245, 250)
        self.ORIGAMI_RAINBOW = [(255, 100, 100), (255, 200, 100), (255, 255, 100),
                                (100, 255, 100), (100, 200, 255), (100, 100, 255), (200, 100, 255)]
        
        # 生成7只纸鹤
        self.cranes = []
        cx, cy = owner.rect.center
        for i in range(7):
            angle = (i / 7) * math.pi * 2
            spawn_x = cx + math.cos(angle) * 80
            spawn_y = cy - 30 + math.sin(angle) * 40
            crane = {
                'x': float(spawn_x),
                'y': float(spawn_y),
                'target_x': spawn_x,
                'target_y': spawn_y,
                'wing_angle': random.uniform(0, math.pi * 2),
                'color_idx': i,
                'fire_timer': random.randint(0, 30),
                'alpha': 0  # 渐入
            }
            self.cranes.append(crane)
        
        self.spawn_effect = 30  # 召唤特效持续时间
        sound_mgr.play("laser")
        FloatingText(cx, cy - 60, "纸鹤群!", (255, 255, 255))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        # 召唤特效
        if self.spawn_effect > 0:
            self.spawn_effect -= 1
            cx, cy = self.owner.rect.center
            for i in range(7):
                ring_alpha = int(200 * (self.spawn_effect / 30))
                ring_r = int((30 - self.spawn_effect) * 3)
                pygame.draw.circle(self.image, (*self.ORIGAMI_RAINBOW[i], ring_alpha), 
                                  (int(self.cranes[i]['x']), int(self.cranes[i]['y'])), ring_r, 2)
        
        # 更新和绘制纸鹤
        for i, crane in enumerate(self.cranes):
            # 渐入/渐出效果
            if self.life > 300:
                crane['alpha'] = min(255, crane['alpha'] + 15)
            elif self.life < 60:
                crane['alpha'] = int(255 * (self.life / 60))
            
            # 跟随玩家阵型
            if self.owner and hasattr(self.owner, 'rect'):
                formation_angle = (i / 7) * math.pi * 2 + (360 - self.life) * 0.02
                formation_r = 60 + math.sin((360 - self.life) * 0.05) * 15
                crane['target_x'] = self.owner.rect.centerx + math.cos(formation_angle) * formation_r
                crane['target_y'] = self.owner.rect.centery - 30 + math.sin(formation_angle) * formation_r * 0.5
            
            # 平滑移动
            crane['x'] += (crane['target_x'] - crane['x']) * 0.12
            crane['y'] += (crane['target_y'] - crane['y']) * 0.12
            
            # 翅膀动画
            crane['wing_angle'] += 0.25
            wing_offset = math.sin(crane['wing_angle']) * 4
            
            # 绘制纸鹤
            cx, cy = int(crane['x']), int(crane['y'])
            color = (*self.ORIGAMI_RAINBOW[i], crane['alpha'])
            white = (*self.ORIGAMI_WHITE, crane['alpha'])
            
            # 机身
            body = [(cx, cy - 12), (cx - 8, cy), (cx, cy + 6), (cx + 8, cy)]
            pygame.draw.polygon(self.image, white[:3], body)
            
            # 左翅
            left_wing = [(cx - 8, cy), (cx - 22 - wing_offset, cy - 3), (cx - 18 - wing_offset, cy + 5)]
            pygame.draw.polygon(self.image, white[:3], left_wing)
            
            # 右翅
            right_wing = [(cx + 8, cy), (cx + 22 + wing_offset, cy - 3), (cx + 18 + wing_offset, cy + 5)]
            pygame.draw.polygon(self.image, white[:3], right_wing)
            
            # 折痕（彩虹色）
            pygame.draw.line(self.image, color[:3], (cx, cy - 10), (cx, cy + 4), 1)
            pygame.draw.line(self.image, color[:3], (cx - 6, cy), (cx - 18 - wing_offset, cy + 2), 1)
            pygame.draw.line(self.image, color[:3], (cx + 6, cy), (cx + 18 + wing_offset, cy + 2), 1)
            
            # 攻击逻辑
            crane['fire_timer'] += 1
            if crane['fire_timer'] >= 40 and crane['alpha'] > 200:  # 0.67秒攻击一次
                crane['fire_timer'] = 0
                # 寻找最近敌人
                if mobs:
                    nearest = None
                    nearest_dist = 999999
                    for m in mobs:
                        dist = math.hypot(m.rect.centerx - crane['x'], m.rect.centery - crane['y'])
                        if dist < nearest_dist:
                            nearest_dist = dist
                            nearest = m
                    
                    if nearest:
                        # 发射小型纸镖
                        from utils.bullets.origami_bullets import CraneBullet
                        crane_dmg = int(self.owner.damage * 0.35)
                        bullet = CraneBullet(crane['x'], crane['y'], 
                                           nearest.rect.centerx, nearest.rect.centery, crane_dmg)
                        all_sprites.add(bullet)
                        bullets.add(bullet)


class OrigamiFeatherShield(pygame.sprite.Sprite):
    """折纸鹤大招 - 千羽护盾：1000根羽毛形成切割墙 (F键)"""
    def __init__(self, owner):
        super().__init__()
        all_sprites.add(self)
        self.owner = owner
        self.life = 180  # 3秒
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # 颜色
        self.feather_count = 100  # 简化为100根，每根代表10根
        self.feathers = []
        
        # 生成羽毛 - 水平切割墙
        cx, cy = owner.rect.centerx, owner.rect.centery - 80
        wall_width = 350
        for i in range(self.feather_count):
            fx = cx - wall_width // 2 + (i / self.feather_count) * wall_width
            fy = cy + random.uniform(-15, 15)
            self.feathers.append({
                'x': float(fx),
                'y': float(fy),
                'base_x': fx - cx,  # 相对于中心的位置
                'angle': random.uniform(-20, 20),
                'phase': random.uniform(0, math.pi * 2),
                'hue': (i * 3.6) % 360  # 虹彩
            })
        
        self.wall_y = cy
        self.hit_cooldown = {}
        self.damage = owner.damage * 0.8
        
        sound_mgr.play("nuke")
        FloatingText(cx, cy - 40, "千羽护盾!", (255, 255, 255))
    
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        # 计算透明度（淡出）
        alpha = 255 if self.life > 30 else int(255 * (self.life / 30))
        
        # 跟随玩家
        cx = self.owner.rect.centerx
        cy = self.owner.rect.centery - 80
        
        # 更新和绘制羽毛
        for i, f in enumerate(self.feathers):
            # 位置跟随玩家
            f['x'] = cx + f['base_x']
            f['y'] = cy + math.sin(f['phase'] + (180 - self.life) * 0.1) * 8
            
            # 虹彩颜色
            hue = (f['hue'] + (180 - self.life) * 2) % 360
            r = int(200 + 55 * math.sin(math.radians(hue)))
            g = int(200 + 55 * math.sin(math.radians(hue + 120)))
            b = int(200 + 55 * math.sin(math.radians(hue + 240)))
            color = (r, g, b, alpha)
            
            # 羽毛形状
            angle = f['angle'] + math.sin((180 - self.life) * 0.05 + i * 0.1) * 15
            rad = math.radians(angle)
            length = 15
            
            fx, fy = int(f['x']), int(f['y'])
            points = [
                (fx + math.cos(rad) * length, fy + math.sin(rad) * length),
                (fx + math.cos(rad + math.pi/2) * 2, fy + math.sin(rad + math.pi/2) * 2),
                (fx - math.cos(rad) * length * 0.4, fy - math.sin(rad) * length * 0.4),
                (fx - math.cos(rad + math.pi/2) * 2, fy - math.sin(rad + math.pi/2) * 2)
            ]
            
            pygame.draw.polygon(self.image, color[:3], points)
        
        # 伤害检测 - 水平墙
        wall_rect = pygame.Rect(cx - 180, cy - 20, 360, 40)
        
        for enemy_id in list(self.hit_cooldown.keys()):
            self.hit_cooldown[enemy_id] -= 1
            if self.hit_cooldown[enemy_id] <= 0:
                del self.hit_cooldown[enemy_id]
        
        for m in list(mobs):
            if m.rect.colliderect(wall_rect):
                enemy_id = id(m)
                if enemy_id not in self.hit_cooldown:
                    m.hp -= self.damage
                    self.hit_cooldown[enemy_id] = 12  # 冷却
                    # 击中特效
                    for _ in range(3):
                        Particle(m.rect.center, (255, 255, 255))
        
        # 清除敌弹
        for eb in list(enemy_bullets):
            if eb.rect.colliderect(wall_rect):
                eb.kill()
                Particle((eb.rect.centerx, eb.rect.centery), (200, 220, 255))
