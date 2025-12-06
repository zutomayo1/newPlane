import pygame
import json
import os
import random
import math
from config import *
from utils import sound_mgr, log_error

# ==============================================================================
#   特效系统 (粒子、屏幕震动等)
# ==============================================================================
class ParticleEffect:
    """粒子效果类"""
    def __init__(self, x, y, particle_type="explosion", count=20):
        self.x = x
        self.y = y
        self.particles = []
        self.alive = True
        self.type = particle_type
        
        if particle_type == "explosion":
            for _ in range(count):
                angle = random.uniform(0, 2 * 3.14159)
                speed = random.uniform(2, 6)
                self.particles.append({
                    'x': x, 'y': y,
                    'vx': speed * __import__('math').cos(angle),
                    'vy': speed * __import__('math').sin(angle),
                    'life': random.uniform(20, 40),
                    'max_life': 40,
                    'color': (255, random.randint(100, 200), 0)  # 爆炸橙色
                })
        elif particle_type == "ice":
            for _ in range(count):
                angle = random.uniform(0, 2 * 3.14159)
                speed = random.uniform(1.5, 4)
                self.particles.append({
                    'x': x, 'y': y,
                    'vx': speed * __import__('math').cos(angle),
                    'vy': speed * __import__('math').sin(angle),
                    'life': random.uniform(30, 50),
                    'max_life': 50,
                    'color': (100, 200, 255)  # 冰蓝色
                })
        elif particle_type == "lightning":
            for _ in range(count):
                self.particles.append({
                    'x': x, 'y': y,
                    'vx': random.uniform(-3, 3),
                    'vy': random.uniform(-5, -1),
                    'life': random.uniform(15, 30),
                    'max_life': 30,
                    'color': (255, 255, 0)  # 闪电黄
                })
        elif particle_type == "heal":
            for _ in range(count):
                angle = random.uniform(0, 2 * 3.14159)
                speed = random.uniform(1, 3)
                self.particles.append({
                    'x': x, 'y': y,
                    'vx': speed * __import__('math').cos(angle),
                    'vy': speed * __import__('math').sin(angle),
                    'life': random.uniform(25, 40),
                    'max_life': 40,
                    'color': (0, 255, 100)  # 治疗绿
                })
    
    def update(self):
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.2  # 重力效果
            p['life'] -= 1
        
        self.particles = [p for p in self.particles if p['life'] > 0]
        if not self.particles:
            self.alive = False
    
    def draw(self, surface):
        for p in self.particles:
            if p['life'] > 0:
                alpha = int(255 * (p['life'] / p['max_life']))
                size = max(1, int(3 * (p['life'] / p['max_life'])))
                pygame.draw.circle(surface, p['color'], (int(p['x']), int(p['y'])), size)


class ScreenShake:
    """屏幕震动效果"""
    def __init__(self, duration=10, intensity=5):
        self.duration = duration
        self.intensity = intensity
        self.timer = duration
    
    def update(self):
        self.timer -= 1
        if self.timer < 0:
            self.timer = 0
    
    def get_offset(self):
        """获取当前摄像头偏移"""
        if self.timer <= 0:
            return (0, 0)
        progress = self.timer / self.duration
        import random as rnd
        return (int(rnd.uniform(-self.intensity, self.intensity) * progress),
                int(rnd.uniform(-self.intensity, self.intensity) * progress))
    
    def is_active(self):
        return self.timer > 0


class EffectManager:
    """管理所有特效"""
    def __init__(self):
        self.particles = []
        self.screen_shake = None
        self.active_effects = []
    
    def add_particle(self, x, y, effect_type="explosion", count=20):
        """添加粒子效果"""
        self.particles.append(ParticleEffect(x, y, effect_type, count))
    
    def trigger_shake(self, duration=8, intensity=4):
        """触发屏幕震动"""
        self.screen_shake = ScreenShake(duration, intensity)
    
    def update(self):
        """更新所有特效"""
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]
        
        if self.screen_shake:
            self.screen_shake.update()
    
    def draw(self, surface):
        """绘制所有粒子效果"""
        for p in self.particles:
            p.draw(surface)
    
    def get_shake_offset(self):
        """获取屏幕震动偏移"""
        if self.screen_shake and self.screen_shake.is_active():
            return self.screen_shake.get_offset()
        return (0, 0)

# ==============================================================================
#   数据存取
# ==============================================================================
def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return [{"name": "王牌机师", "score": 1000}, {"name": "老司机", "score": 800}, {"name": "萌新", "score": 500}]
    try:
        with open(LEADERBOARD_FILE, "r", encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_leaderboard(data):
    try:
        data.sort(key=lambda x: x["score"], reverse=True)
        data = data[:5]
        with open(LEADERBOARD_FILE, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except: pass

# 全局 arsenal 数据容器，将在 main.py 中初始化
arsenal_save_data = {
    "currencies": {"cores": 0, "chips": 0},
    "weapons": [],
    "loadout": [None, None, None]
}

def create_weapon(w_type):
    return {
        "id": f"{w_type}_{random.randint(1000,9999)}",
        "type": w_type,
        "stars": 1,
        "xp": 0,
        "tech_tree": {"3star": None, "5star": None}
    }

def load_arsenal():
    global arsenal_save_data
    if os.path.exists(ARSENAL_FILE):
        try:
            with open(ARSENAL_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                # 简单的合并逻辑，防止旧存档缺少字段
                for k, v in data.items():
                    arsenal_save_data[k] = v
        except Exception as e:
            log_error(f"Load arsenal failed: {e}")
            
    # 初始化默认武器
    if not arsenal_save_data["weapons"]:
        arsenal_save_data["weapons"].append(create_weapon("cannon"))
        arsenal_save_data["loadout"][0] = arsenal_save_data["weapons"][0]

def save_arsenal():
    try:
        with open(ARSENAL_FILE, "w", encoding='utf-8') as f:
            json.dump(arsenal_save_data, f, ensure_ascii=False)
    except: pass

# ==============================================================================
#   背景与环境 - 多样化元素系统
# ==============================================================================
class Nebula:
    """经典星云 - 支持主题颜色"""
    def __init__(self, theme_type="classic"):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.size = random.randint(150, 400)
        self.speed = random.uniform(0.5, 1.5)
        self.theme_type = theme_type
        self.color = self._get_theme_color(theme_type)
        self.alpha = random.randint(30, 80)

    def _get_theme_color(self, theme):
        """根据主题类型返回合适的颜色"""
        theme_colors = {
            "classic": [(0, 50, 100), (20, 0, 50), (0, 20, 40)],
            "blood": [(100, 0, 20), (80, 0, 40), (60, 0, 30)],
            "deep_space": [(10, 10, 30), (0, 20, 40), (5, 5, 50)],
            "sunset": [(255, 100, 50), (255, 150, 80), (200, 80, 40)],
            "aurora": [(0, 255, 150), (100, 255, 200), (50, 200, 255)],
            "dreamy": [(255, 100, 200), (200, 50, 150), (255, 150, 220)],
            "emerald": [(0, 200, 100), (0, 150, 80), (50, 255, 150)],
            "lavender": [(180, 120, 255), (150, 100, 200), (200, 150, 255)],
            "crystal": [(200, 0, 255), (150, 50, 200), (180, 80, 255)],
            "sapphire": [(0, 100, 255), (50, 150, 255), (0, 80, 200)]
        }
        colors = theme_colors.get(theme, theme_colors["classic"])
        return random.choice(colors)

    def update(self, speed_mult=1.0):
        self.y += self.speed * speed_mult
        if self.y - self.size > HEIGHT:
            self.y = -self.size
            self.x = random.randint(0, WIDTH)

    def draw(self, surf, color_override=None):
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        c = color_override if color_override else self.color
        pygame.draw.circle(s, (*c, self.alpha), (self.size, self.size), self.size)
        pygame.draw.circle(s, (*c, self.alpha//2), (self.size, self.size), int(self.size*0.7))
        surf.blit(s, (self.x - self.size, self.y - self.size), special_flags=pygame.BLEND_ADD)

class MatrixRain:
    """矩阵数字雨 - 优化版"""
    _font_cache = None  # 类级别字体缓存
    
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.uniform(3, 8)
        self.chars = "01"
        self.length = random.randint(3, 8)  # 减少长度提升性能
        self.alpha = random.randint(150, 255)
        self.char_list = [random.choice(self.chars) for _ in range(self.length)]  # 预生成字符
        self.frame_count = 0
        
        # 初始化字体缓存
        if MatrixRain._font_cache is None:
            try:
                MatrixRain._font_cache = pygame.font.SysFont("monospace", 14, bold=True)
            except:
                MatrixRain._font_cache = pygame.font.Font(None, 14)
    
    def update(self, speed_mult=1.0):
        self.y += self.speed * speed_mult
        self.frame_count += 1
        # 每10帧更新一次字符
        if self.frame_count % 10 == 0:
            self.char_list = [random.choice(self.chars) for _ in range(self.length)]
        
        if self.y > HEIGHT + self.length * 15:
            self.y = -self.length * 15
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        if MatrixRain._font_cache is None:
            return
        for i in range(self.length):
            alpha = int(self.alpha * (1 - i / self.length))
            if alpha > 20:  # 跳过太淡的字符
                try:
                    text = MatrixRain._font_cache.render(self.char_list[i], True, (0, 255, 0))
                    text.set_alpha(alpha)
                    surf.blit(text, (self.x, int(self.y + i * 15)))
                except: pass

class HexParticle:
    """六边形粒子"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, HEIGHT)
        self.size = random.randint(10, 30)
        self.speed = random.uniform(0.5, 2)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2, 2)
        self.alpha = random.randint(30, 100)
        self.color = random.choice([(255, 0, 180), (0, 255, 255), (255, 100, 255)])
    
    def update(self, speed_mult=1.0):
        self.y += self.speed * speed_mult
        self.rotation += self.rot_speed
        if self.y > HEIGHT + self.size:
            self.y = -self.size
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        import math
        s = pygame.Surface((self.size*3, self.size*3), pygame.SRCALPHA)
        points = []
        for i in range(6):
            angle = math.radians(60 * i + self.rotation)
            px = self.size*1.5 + self.size * math.cos(angle)
            py = self.size*1.5 + self.size * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(s, (*self.color, self.alpha), points, 2)
        surf.blit(s, (self.x - self.size*1.5, self.y - self.size*1.5))

class Bubble:
    """气泡 - 支持主题颜色"""
    def __init__(self, theme_type="underwater"):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + random.randint(0, 200)
        self.size = random.randint(20, 60)
        self.speed = random.uniform(1, 3)
        self.wobble = random.uniform(0, 6.28)
        self.wobble_speed = random.uniform(0.05, 0.15)
        self.alpha = random.randint(40, 100)
        self.theme_type = theme_type
        self.color = self._get_theme_color(theme_type)
    
    def _get_theme_color(self, theme):
        """根据主题返回气泡颜色"""
        theme_colors = {
            "underwater": (100, 150, 255),
            "toxic": (100, 255, 50),
            "coral": (255, 150, 180),
            "dreamy": (255, 180, 230)
        }
        return theme_colors.get(theme, (100, 150, 255))
    
    def update(self, speed_mult=1.0):
        self.y -= self.speed * speed_mult
        self.wobble += self.wobble_speed
        self.x += math.sin(self.wobble) * 2
        if self.y < -self.size:
            self.y = HEIGHT + self.size
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.alpha), (self.size, self.size), self.size, 3)
        # 高光
        light_color = tuple(min(255, c + 100) for c in self.color[:3])
        pygame.draw.circle(s, (*light_color, self.alpha//2), (self.size - self.size//4, self.size - self.size//4), self.size//4)
        surf.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class Ember:
    """火星 - 支持主题颜色"""
    def __init__(self, theme_type="lava"):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + random.randint(0, 200)
        self.size = random.randint(3, 12)
        self.speed = random.uniform(2, 6)
        self.alpha = random.randint(150, 255)
        self.flicker = random.uniform(0, 6.28)
        self.theme_type = theme_type
        self.color = self._get_theme_color(theme_type)
    
    def _get_theme_color(self, theme):
        """根据主题返回火星颜色"""
        theme_colors = {
            "lava": (255, 100, 0),
            "golden": (255, 220, 0),
            "fire": (255, 50, 0)
        }
        return theme_colors.get(theme, (255, 100, 0))
    
    def update(self, speed_mult=1.0):
        self.y -= self.speed * speed_mult
        self.x += random.uniform(-1, 1)
        self.flicker += 0.3
        self.alpha = int(200 + 55 * math.sin(self.flicker))
        if self.y < -self.size:
            self.y = HEIGHT + self.size
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        # 根据基础颜色生成渐变色
        base = self.color
        colors = [
            base,
            tuple(max(0, c - 50) for c in base),
            tuple(max(0, c - 100) for c in base)
        ]
        c = random.choice(colors)
        pygame.draw.circle(surf, (*c, min(255, self.alpha)), (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surf, (255, 255, 100, min(200, self.alpha//2)), (int(self.x), int(self.y)), self.size//2)

class Snowflake:
    """雪花 - 支持主题颜色"""
    def __init__(self, theme_type="winter"):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.size = random.randint(3, 8)
        self.speed = random.uniform(1, 3)
        self.drift = random.uniform(-0.5, 0.5)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-3, 3)
        self.theme_type = theme_type
        self.color = self._get_theme_color(theme_type)
    
    def _get_theme_color(self, theme):
        """根据主题返回雪花颜色"""
        theme_colors = {
            "winter": (200, 220, 255),
            "lavender": (220, 180, 255),
            "sapphire": (150, 200, 255)
        }
        return theme_colors.get(theme, (200, 220, 255))
    
    def update(self, speed_mult=1.0):
        self.y += self.speed * speed_mult
        self.x += self.drift
        self.rotation += self.rot_speed
        if self.y > HEIGHT:
            self.y = -10
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        import math
        # 绘制六角星形雪花
        for i in range(6):
            angle = math.radians(60 * i + self.rotation)
            x1 = self.x
            y1 = self.y
            x2 = self.x + self.size * math.cos(angle)
            y2 = self.y + self.size * math.sin(angle)
            pygame.draw.line(surf, self.color, (int(x1), int(y1)), (int(x2), int(y2)), 2)

class CodeLine:
    """代码行（复古风格）"""
    def __init__(self):
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(20, 50)
        self.text = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<>(){}[]", k=random.randint(10, 40)))
        self.alpha = random.randint(100, 200)
        self.age = 0
    
    def update(self, speed_mult=1.0):
        self.age += 1
        self.alpha = max(0, self.alpha - 2)
        if self.age > 100 or self.alpha <= 0:
            self.y = random.randint(0, HEIGHT)
            self.text = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<>(){}[]", k=random.randint(10, 40)))
            self.alpha = random.randint(100, 200)
            self.age = 0
    
    def draw(self, surf):
        try:
            font = pygame.font.SysFont("courier", 14, bold=True)
            text = font.render(self.text, True, (255, 100, 200))
            text.set_alpha(self.alpha)
            surf.blit(text, (20, self.y))
        except: pass

# 新背景元素类
class Cloud:
    """云朵 - 多层云海"""
    def __init__(self, layer=0):
        self.x = random.randint(-200, WIDTH + 200)
        self.y = HEIGHT // 2 + layer * 80 + random.randint(-40, 40)
        self.size = random.randint(100, 250) + layer * 30
        self.speed = 0.3 + layer * 0.2
        self.alpha = 180 - layer * 30
        self.color = [(255, 200, 150), (255, 180, 200), (200, 150, 255)][layer % 3]
    
    def update(self, speed_mult=1.0):
        self.x -= self.speed * speed_mult
        if self.x < -self.size * 2:
            self.x = WIDTH + self.size
    
    def draw(self, surf):
        s = pygame.Surface((self.size * 3, self.size * 2), pygame.SRCALPHA)
        for i in range(5):
            offset_x = i * self.size // 2
            pygame.draw.ellipse(s, (*self.color, self.alpha), 
                              (offset_x, self.size // 2, self.size, self.size))
        surf.blit(s, (int(self.x), int(self.y)))

class LightRay:
    """光线 - 旋转光束(太阳光)"""
    def __init__(self):
        self.angle = random.uniform(0, 360)
        self.length = random.randint(200, 400)
        self.width = random.randint(40, 80)
        self.alpha = random.randint(20, 50)
        self.rot_speed = random.uniform(0.1, 0.3)
    
    def update(self, speed_mult=1.0):
        self.angle += self.rot_speed
    
    def draw(self, surf):
        import math
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        rad = math.radians(self.angle)
        x1, y1 = WIDTH // 2, HEIGHT // 4
        x2 = x1 + self.length * math.cos(rad)
        y2 = y1 + self.length * math.sin(rad)
        points = [
            (x1 - self.width // 2 * math.sin(rad), y1 + self.width // 2 * math.cos(rad)),
            (x1 + self.width // 2 * math.sin(rad), y1 - self.width // 2 * math.cos(rad)),
            (x2 + self.width // 4 * math.sin(rad), y2 - self.width // 4 * math.cos(rad)),
            (x2 - self.width // 4 * math.sin(rad), y2 + self.width // 4 * math.cos(rad))
        ]
        pygame.draw.polygon(s, (255, 230, 150, self.alpha), points)
        surf.blit(s, (0, 0), special_flags=pygame.BLEND_ADD)

class UnderwaterBeam:
    """水下光束 - 从上方向下照射"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.width_top = random.randint(30, 60)
        self.width_bottom = random.randint(80, 150)
        self.alpha = random.randint(15, 35)
        self.sway = random.uniform(0, 6.28)
        self.sway_speed = random.uniform(0.02, 0.05)
        self.color = (100, 180, 220)  # 蓝白色水下光
    
    def update(self, speed_mult=1.0):
        self.sway += self.sway_speed
    
    def draw(self, surf):
        import math
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # 光束随水波摆动
        sway_offset = math.sin(self.sway) * 20
        x_top = self.x + sway_offset
        x_bottom = self.x + sway_offset * 2
        
        # 绘制梯形光束
        points = [
            (x_top - self.width_top // 2, 0),
            (x_top + self.width_top // 2, 0),
            (x_bottom + self.width_bottom // 2, HEIGHT),
            (x_bottom - self.width_bottom // 2, HEIGHT)
        ]
        pygame.draw.polygon(s, (*self.color, self.alpha), points)
        surf.blit(s, (0, 0), special_flags=pygame.BLEND_ADD)

class Lightning:
    """闪电"""
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = random.randint(100, WIDTH - 100)
        self.segments = []
        self.active = False
        self.timer = random.randint(60, 180)
        self.duration = 0
        self.generate()
    
    def generate(self):
        self.segments = []
        x, y = self.x, 0
        while y < HEIGHT:
            next_y = y + random.randint(30, 80)
            next_x = x + random.randint(-50, 50)
            self.segments.append(((x, y), (next_x, next_y)))
            x, y = next_x, next_y
    
    def update(self, speed_mult=1.0):
        if not self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = True
                self.duration = random.randint(3, 8)
                self.generate()
        else:
            self.duration -= 1
            if self.duration <= 0:
                self.active = False
                self.timer = random.randint(60, 180)
    
    def draw(self, surf):
        if self.active:
            for start, end in self.segments:
                pygame.draw.line(surf, (150, 200, 255), start, end, 3)
                pygame.draw.line(surf, (255, 255, 255), start, end, 1)

class RainDrop:
    """雨滴"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.uniform(15, 25)
        self.length = random.randint(10, 20)
    
    def update(self, speed_mult=1.0):
        self.y += self.speed * speed_mult
        self.x -= 3
        if self.y > HEIGHT:
            self.y = -20
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        pygame.draw.line(surf, (100, 120, 150, 150), 
                        (int(self.x), int(self.y)), 
                        (int(self.x - 3), int(self.y + self.length)), 2)

class Building:
    """建筑剪影"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT - random.randint(100, 300)
        self.width = random.randint(40, 120)
        self.height = HEIGHT - self.y
        self.windows = []
        self.speed = random.uniform(0.5, 1.5)
        # 生成窗户
        for wx in range(10, self.width - 10, 15):
            for wy in range(10, self.height - 10, 20):
                if random.random() > 0.3:
                    self.windows.append((wx, wy))
    
    def update(self, speed_mult=1.0):
        self.x -= self.speed * speed_mult
        if self.x < -self.width:
            self.x = WIDTH + random.randint(0, 200)
    
    def draw(self, surf):
        # 建筑主体
        pygame.draw.rect(surf, (20, 20, 40), (int(self.x), int(self.y), self.width, self.height))
        # 窗户灯光
        for wx, wy in self.windows:
            if random.random() > 0.05:  # 窗户随机闪烁
                color = (255, 200, 100) if random.random() > 0.8 else (200, 220, 255)
                pygame.draw.rect(surf, color, (int(self.x + wx), int(self.y + wy), 8, 12))

class AuroraWave:
    """极光波浪"""
    def __init__(self, layer=0):
        self.y_base = 100 + layer * 80
        self.points = []
        self.color = [(50, 255, 150), (150, 100, 255), (100, 150, 255)][layer % 3]
        self.alpha = 100 - layer * 15
        self.phase = random.uniform(0, 6.28)
        self.speed = 0.05 + layer * 0.02
        for x in range(0, WIDTH + 50, 50):
            self.points.append(x)
    
    def update(self, speed_mult=1.0):
        self.phase += self.speed
    
    def draw(self, surf):
        import math
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        points = []
        for x in self.points:
            y = self.y_base + 60 * math.sin(x * 0.01 + self.phase)
            points.append((x, y))
        if len(points) > 2:
            points.append((WIDTH, HEIGHT))
            points.insert(0, (0, HEIGHT))
            pygame.draw.polygon(s, (*self.color, self.alpha), points)
        surf.blit(s, (0, 0), special_flags=pygame.BLEND_ADD)

class Asteroid:
    """陨石"""
    def __init__(self):
        self.x = random.randint(-100, WIDTH + 100)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(20, 60)
        self.speed = random.uniform(1, 3)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2, 2)
        self.vx = random.uniform(-1, 1)
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.speed * speed_mult * 0.3
        self.rotation += self.rot_speed
        if self.x < -self.size or self.x > WIDTH + self.size:
            self.x = random.randint(-100, WIDTH + 100)
            self.y = -self.size
    
    def draw(self, surf):
        import math
        points = []
        for i in range(8):
            angle = math.radians(i * 45 + self.rotation)
            r = self.size * random.uniform(0.7, 1.0)
            px = self.x + r * math.cos(angle)
            py = self.y + r * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(surf, (80, 80, 90), points)
        pygame.draw.polygon(surf, (60, 60, 70), points, 2)

class VolcanoSmoke:
    """火山烟雾"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + random.randint(0, 100)
        self.size = random.randint(80, 200)
        self.speed = random.uniform(1, 3)
        self.alpha = random.randint(40, 100)
        self.color = random.choice([(80, 60, 60), (100, 80, 50), (60, 50, 40)])
        self.drift = random.uniform(-0.5, 0.5)
    
    def update(self, speed_mult=1.0):
        self.y -= self.speed * speed_mult
        self.x += self.drift
        self.size += 0.5
        self.alpha = max(0, self.alpha - 1)
        if self.y < -self.size or self.alpha <= 0:
            self.y = HEIGHT + random.randint(0, 50)
            self.x = random.randint(0, WIDTH)
            self.size = random.randint(80, 150)
            self.alpha = random.randint(60, 120)
    
    def draw(self, surf):
        s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.alpha), (int(self.size), int(self.size)), int(self.size))
        surf.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class MapleLeaf:
    """枫叶 - 螺旋飘落"""
    def __init__(self):
        self.x = random.randint(-50, WIDTH + 50)
        self.y = random.randint(-HEIGHT, 0)
        self.size = random.randint(8, 15)
        self.speed = random.uniform(2, 4)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-5, 5)
        self.sway = random.uniform(0, 6.28)
        self.sway_speed = random.uniform(0.05, 0.15)
        self.color = random.choice([(200, 50, 30), (220, 100, 20), (255, 150, 0)])
    
    def update(self, speed_mult=1.0):
        self.y += self.speed * speed_mult
        self.sway += self.sway_speed
        self.x += math.sin(self.sway) * 3
        self.rotation += self.rot_speed
        if self.y > HEIGHT + 20:
            self.y = -20
            self.x = random.randint(-50, WIDTH + 50)
    
    def draw(self, surf):
        import math
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        # 简化枫叶形状
        center = self.size
        pygame.draw.polygon(s, self.color, [
            (center, 0), (center - self.size//3, center),
            (0, center), (center, center + self.size//2),
            (self.size * 2, center), (center + self.size//3, center)
        ])
        rotated = pygame.transform.rotate(s, self.rotation)
        rect = rotated.get_rect(center=(self.x, self.y))
        surf.blit(rotated, rect)

class SaltCrystal:
    """盐晶 - 漂浮闪烁"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(3, 8)
        self.alpha = random.randint(100, 255)
        self.phase = random.uniform(0, 6.28)
        self.color_phase = random.uniform(0, 6.28)
        self.hue = random.uniform(0, 360)
        # 漂浮运动
        self.base_y = self.y
        self.float_phase = random.uniform(0, 6.28)
        self.float_speed = random.uniform(0.02, 0.05)
        self.float_amplitude = random.randint(20, 50)
        # 水平漂移
        self.drift_speed = random.uniform(-0.3, 0.3)
    
    def update(self, speed_mult=1.0):
        self.phase += 0.08
        self.color_phase += 0.02
        self.alpha = int(180 + 75 * math.sin(self.phase))
        
        # 垂直漂浮
        self.float_phase += self.float_speed
        self.y = self.base_y + math.sin(self.float_phase) * self.float_amplitude
        
        # 水平漂移
        self.x += self.drift_speed * speed_mult
        if self.x < -20:
            self.x = WIDTH + 20
            self.base_y = random.randint(0, HEIGHT)
        elif self.x > WIDTH + 20:
            self.x = -20
            self.base_y = random.randint(0, HEIGHT)
    
    def draw(self, surf):
        # 彩虹色渐变
        hue = (self.hue + self.color_phase * 20) % 360
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(hue / 360, 0.6, 1.0)
        color = (int(r * 255), int(g * 255), int(b * 255))
        
        # 主体光晕
        for i in range(3, 0, -1):
            alpha = self.alpha // (4 - i)
            pygame.draw.circle(surf, (*color, alpha), (int(self.x), int(self.y)), self.size * i // 2)
        
        # 核心亮点
        pygame.draw.circle(surf, (255, 255, 255, self.alpha), (int(self.x), int(self.y)), self.size // 2)
        
        # 十字星芒
        star_len = self.size * 3
        pygame.draw.line(surf, (*color, self.alpha // 2), 
                        (int(self.x - star_len), int(self.y)), 
                        (int(self.x + star_len), int(self.y)), 2)
        pygame.draw.line(surf, (*color, self.alpha // 2),
                        (int(self.x), int(self.y - star_len)),
                        (int(self.x), int(self.y + star_len)), 2)

class SaltWave:
    """盐湖波纹 - 镜面反射效果"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT // 2 + random.randint(-100, 100)
        self.radius = 0
        self.max_radius = random.randint(80, 150)
        self.speed = random.uniform(1.5, 3)
        self.alpha = 120
        self.color = random.choice([(200, 230, 255), (255, 200, 240), (200, 255, 240)])
    
    def update(self, speed_mult=1.0):
        self.radius += self.speed
        self.alpha = int(120 * (1 - self.radius / self.max_radius))
        if self.radius > self.max_radius:
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT // 2 + random.randint(-100, 100)
            self.radius = 0
            self.alpha = 120
    
    def draw(self, surf):
        if self.alpha > 10:
            pygame.draw.circle(surf, (*self.color, self.alpha), (int(self.x), int(self.y)), int(self.radius), 2)

class WarDebris:
    """战争残骸"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(15, 40)
        self.speed = random.uniform(0.3, 1.0)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-1, 1)
        self.color = random.choice([(80, 80, 90), (100, 70, 50), (60, 60, 65)])
    
    def update(self, speed_mult=1.0):
        self.y += self.speed * speed_mult
        self.rotation += self.rot_speed
        if self.y > HEIGHT + self.size:
            self.y = -self.size
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        # 绘制不规则碎片
        points = []
        for i in range(5):
            angle = math.radians(i * 72 + self.rotation)
            r = self.size * random.uniform(0.6, 1.0)
            points.append((self.x + r * math.cos(angle), self.y + r * math.sin(angle)))
        pygame.draw.polygon(surf, self.color, points)

class CrystalParticle:
    """水晶粒子 - 从水晶发射的光点"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, 6.28)
        speed = random.uniform(0.5, 2)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.randint(2, 4)
        self.life = random.randint(30, 80)
        self.max_life = self.life
        self.color = color
    
    def update(self, speed_mult=1.0):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0
    
    def draw(self, surf):
        alpha = int(255 * (self.life / self.max_life))
        pygame.draw.circle(surf, (*self.color, alpha), (int(self.x), int(self.y)), self.size)

class Crystal:
    """小水晶 - 低调动态飘落"""
    def __init__(self, from_top=True):
        self.x = random.randint(-50, WIDTH + 50)
        self.y = random.randint(-HEIGHT, 0)
        # 中等大小水晶
        self.size = random.randint(8, 14)
        # 飘落速度（参考枫叶）
        self.speed = random.uniform(1.5, 3)
        # 旋转
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-3, 3)
        # 摆动
        self.sway = random.uniform(0, 6.28)
        self.sway_speed = random.uniform(0.03, 0.1)
        # 蓝色系
        self.color = random.choice([(80, 150, 255), (60, 130, 240), (90, 160, 255), (70, 140, 250)])
        self.glow_phase = random.uniform(0, 6.28)
        self.alpha = random.randint(120, 200)
        
    def update(self, speed_mult=1.0):
        # 飘落移动
        self.y += self.speed * speed_mult
        
        # 左右摆动
        self.sway += self.sway_speed
        self.x += math.sin(self.sway) * 2
        
        # 旋转
        self.rotation += self.rot_speed
        
        # 发光脉冲（更柔和）
        self.glow_phase += 0.03
        self.alpha = int(100 + 50 * math.sin(self.glow_phase))
        
        # 重置位置
        if self.y > HEIGHT + 20:
            self.y = -20
            self.x = random.randint(-50, WIDTH + 50)
    
    def draw(self, surf):
        # 简单的菱形水晶（更低调）
        s = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        center = self.size * 1.5
        
        # 菱形形状
        points = [
            (center, center - self.size),
            (center + self.size * 0.7, center),
            (center, center + self.size),
            (center - self.size * 0.7, center)
        ]
        
        # 柔和的发光
        glow_alpha = self.alpha // 3
        pygame.draw.polygon(s, (*self.color, glow_alpha), points)
        
        # 水晶本体
        pygame.draw.polygon(s, (*self.color, self.alpha), points)
        
        # 旋转并绘制
        rotated = pygame.transform.rotate(s, self.rotation)
        rect = rotated.get_rect(center=(self.x, self.y))
        surf.blit(rotated, rect)

class TimeDistortion:
    """时空裂缝 - 扭曲空间撕裂效果"""
    def __init__(self):
        self.x = random.randint(150, WIDTH - 150)
        self.y = random.randint(150, HEIGHT - 150)
        self.angle = random.uniform(0, 3.14)
        self.length = random.randint(100, 200)
        self.width = random.randint(30, 60)
        self.phase = random.uniform(0, 6.28)
        self.rotation_speed = random.uniform(-0.02, 0.02)
        self.pulse_phase = random.uniform(0, 6.28)
        
        # 裂缝周围的扭曲环
        self.distortion_rings = []
        for i in range(5):
            self.distortion_rings.append({
                'offset': i * 20,
                'phase': random.uniform(0, 6.28)
            })
        
        # 吸入粒子
        self.particles = []
        self.particle_timer = 0
    
    def update(self, speed_mult=1.0):
        self.angle += self.rotation_speed
        self.phase += 0.05
        self.pulse_phase += 0.08
        
        # 更新扭曲环
        for ring in self.distortion_rings:
            ring['phase'] += 0.03
        
        # 生成被吸入的粒子
        self.particle_timer += 1
        if self.particle_timer > 5:
            self.particle_timer = 0
            spawn_dist = random.randint(150, 250)
            spawn_angle = random.uniform(0, 6.28)
            px = self.x + math.cos(spawn_angle) * spawn_dist
            py = self.y + math.sin(spawn_angle) * spawn_dist
            self.particles.append({
                'x': px, 'y': py, 
                'life': 100,
                'color': random.choice([(200, 50, 255), (150, 0, 255), (100, 0, 200)])
            })
        
        # 更新粒子 - 螺旋吸入
        for p in self.particles:
            dx = self.x - p['x']
            dy = self.y - p['y']
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 5:
                angle_to_center = math.atan2(dy, dx)
                spiral_angle = angle_to_center + 0.2  # 螺旋效果
                speed = 3 + (100 - dist) * 0.05
                p['x'] += math.cos(spiral_angle) * speed
                p['y'] += math.sin(spiral_angle) * speed
            p['life'] -= 1
        
        self.particles = [p for p in self.particles if p['life'] > 0]
    
    def draw(self, surf):
        # 绘制扭曲环
        for i, ring in enumerate(self.distortion_rings):
            ring_radius = 50 + ring['offset'] + int(15 * math.sin(ring['phase']))
            ring_alpha = int(80 - i * 15)
            
            # 扭曲椭圆
            for angle_offset in range(0, 360, 10):
                angle = math.radians(angle_offset)
                distortion = math.sin(angle * 3 + self.phase) * 10
                x = self.x + (ring_radius + distortion) * math.cos(angle)
                y = self.y + (ring_radius + distortion) * math.sin(angle)
                pygame.draw.circle(surf, (150, 0, 255, ring_alpha), (int(x), int(y)), 2)
        
        # 绘制核心裂缝
        crack_points = []
        segments = 12
        for i in range(segments + 1):
            t = i / segments
            offset_x = (t - 0.5) * self.length
            # 裂缝扭曲
            wave = math.sin(t * 6.28 * 2 + self.phase) * (self.width // 2)
            
            px = self.x + offset_x * math.cos(self.angle) - wave * math.sin(self.angle)
            py = self.y + offset_x * math.sin(self.angle) + wave * math.cos(self.angle)
            crack_points.append((px, py))
        
        # 裂缝外层光晕
        for offset in range(15, 0, -3):
            glow_points = []
            for px, py in crack_points:
                glow_points.append((px, py + offset))
            for px, py in reversed(crack_points):
                glow_points.append((px, py - offset))
            
            glow_alpha = int(80 - offset * 4)
            if len(glow_points) > 2:
                pygame.draw.polygon(surf, (100, 0, 200, glow_alpha), glow_points)
        
        # 裂缝核心
        core_width = int(self.width * (0.7 + 0.3 * math.sin(self.pulse_phase)))
        for i in range(len(crack_points) - 1):
            p1 = crack_points[i]
            p2 = crack_points[i + 1]
            pygame.draw.line(surf, (200, 0, 255), p1, p2, core_width)
            pygame.draw.line(surf, (255, 100, 255), p1, p2, core_width // 2)
        
        # 裂缝内部虚空
        void_alpha = int(150 + 105 * math.sin(self.pulse_phase * 2))
        for i in range(len(crack_points) - 1):
            p1 = crack_points[i]
            p2 = crack_points[i + 1]
            pygame.draw.line(surf, (50, 0, 80, void_alpha), p1, p2, core_width // 3)
        
        # 绘制被吸入的粒子
        for p in self.particles:
            alpha = int(255 * (p['life'] / 100))
            size = 3 + int(3 * (1 - p['life'] / 100))
            pygame.draw.circle(surf, (*p['color'], alpha), (int(p['x']), int(p['y'])), size)
            
            # 粒子拖尾
            trail_len = 10
            dx = self.x - p['x']
            dy = self.y - p['y']
            trail_angle = math.atan2(dy, dx) + 3.14
            trail_x = p['x'] + math.cos(trail_angle) * trail_len
            trail_y = p['y'] + math.sin(trail_angle) * trail_len
            pygame.draw.line(surf, (*p['color'], alpha // 2), 
                           (int(p['x']), int(p['y'])), 
                           (int(trail_x), int(trail_y)), 2)

class QuantumParticle:
    """量子粒子"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(2, 5)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.color = random.choice([(0, 255, 150), (200, 0, 255), (0, 200, 255)])
        self.alpha = random.randint(100, 255)
        self.phase = random.uniform(0, 6.28)
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.phase += 0.2
        self.alpha = int(150 + 105 * math.sin(self.phase))
        if self.x < 0 or self.x > WIDTH: self.vx *= -1
        if self.y < 0 or self.y > HEIGHT: self.vy *= -1
    
    def draw(self, surf):
        pygame.draw.circle(surf, (*self.color, self.alpha), (int(self.x), int(self.y)), self.size)

class RuinPillar:
    """遗迹石柱"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + random.randint(0, 100)
        self.width = random.randint(40, 80)
        self.height = random.randint(150, 300)
        self.speed = random.uniform(0.5, 1.5)
        self.color = (60, 80, 100)
    
    def update(self, speed_mult=1.0):
        self.y -= self.speed * speed_mult
        if self.y < -self.height:
            self.y = HEIGHT + random.randint(0, 50)
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        # 石柱
        pygame.draw.rect(surf, self.color, (int(self.x - self.width // 2), int(self.y - self.height), self.width, self.height))
        # 珊瑚装饰
        for i in range(3):
            coral_y = int(self.y - self.height * (0.3 + i * 0.3))
            pygame.draw.circle(surf, (255, 100, 50), (int(self.x), coral_y), 8)

class BioOrb:
    """生物发光球体"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(15, 40)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(0.2, 0.8)  # 向下漂浮
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.03, 0.08)
        self.color = random.choice([(0, 200, 180), (100, 220, 200), (50, 180, 255)])
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.pulse += self.pulse_speed
        if self.y > HEIGHT + self.size:
            self.y = -self.size
            self.x = random.randint(0, WIDTH)
        if self.x < -self.size: self.x = WIDTH + self.size
        if self.x > WIDTH + self.size: self.x = -self.size
    
    def draw(self, surf):
        pulse_size = int(self.size * (1 + 0.3 * math.sin(self.pulse)))
        alpha = int(150 + 100 * math.sin(self.pulse))
        glow = pygame.Surface((pulse_size * 3, pulse_size * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, alpha // 3), (pulse_size * 1.5, pulse_size * 1.5), pulse_size * 1.5)
        surf.blit(glow, (self.x - pulse_size * 1.5, self.y - pulse_size * 1.5))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), pulse_size)

class BioTentacle:
    """生物触手"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.base_y = random.choice([0, HEIGHT])  # 从顶部或底部延伸
        self.segments = 8
        self.length = random.randint(100, 200)
        self.wave_offset = random.uniform(0, 6.28)
        self.wave_speed = random.uniform(0.02, 0.05)
        self.color = (20, 150, 140)
    
    def update(self, speed_mult=1.0):
        self.wave_offset += self.wave_speed * speed_mult
    
    def draw(self, surf):
        points = []
        for i in range(self.segments + 1):
            t = i / self.segments
            y_offset = self.length * t
            x_wave = 30 * math.sin(self.wave_offset + t * 3)
            if self.base_y == 0:  # 从顶部
                points.append((self.x + x_wave, self.base_y + y_offset))
            else:  # 从底部
                points.append((self.x + x_wave, self.base_y - y_offset))
        if len(points) > 1:
            pygame.draw.lines(surf, self.color, False, points, 3)

class BioSpore:
    """生物孢子"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(2, 6)
        self.vx = random.uniform(-0.2, 0.2)
        self.vy = random.uniform(-0.5, -0.1)  # 向上漂浮
        self.alpha = random.randint(100, 200)
        self.color = (100, 255, 200)
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        if self.y < -10:
            self.y = HEIGHT + 10
            self.x = random.randint(0, WIDTH)
        if self.x < -10: self.x = WIDTH + 10
        if self.x > WIDTH + 10: self.x = -10
    
    def draw(self, surf):
        glow = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, self.alpha // 2), (self.size * 2, self.size * 2), self.size * 2)
        surf.blit(glow, (self.x - self.size * 2, self.y - self.size * 2))

class Gear:
    """齿轮"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(40, 100)
        self.teeth = random.randint(8, 16)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-0.5, 0.5)
        self.vx = random.uniform(-0.2, 0.2)
        self.vy = random.uniform(-0.2, 0.2)
        self.color = (120, 90, 60)
    
    def update(self, speed_mult=1.0):
        self.rotation += self.rot_speed * speed_mult
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        if self.x < -self.size: self.x = WIDTH + self.size
        if self.x > WIDTH + self.size: self.x = -self.size
        if self.y < -self.size: self.y = HEIGHT + self.size
        if self.y > HEIGHT + self.size: self.y = -self.size
    
    def draw(self, surf):
        # 绘制齿轮
        points = []
        for i in range(self.teeth * 2):
            angle = math.radians(i * 180 / self.teeth + self.rotation)
            r = self.size if i % 2 == 0 else self.size * 0.85
            points.append((self.x + r * math.cos(angle), self.y + r * math.sin(angle)))
        if len(points) > 2:
            pygame.draw.polygon(surf, self.color, points)
            pygame.draw.polygon(surf, (180, 140, 100), points, 2)
        pygame.draw.circle(surf, (60, 45, 30), (int(self.x), int(self.y)), int(self.size * 0.3))

class Chain:
    """链条"""
    def __init__(self):
        self.x1 = random.randint(0, WIDTH)
        self.y1 = random.randint(0, HEIGHT // 2)
        self.x2 = self.x1 + random.randint(-100, 100)
        self.y2 = self.y1 + random.randint(150, 300)
        self.links = 10
        self.swing = random.uniform(0, 6.28)
        self.swing_speed = random.uniform(0.02, 0.04)
        self.color = (100, 80, 60)
    
    def update(self, speed_mult=1.0):
        self.swing += self.swing_speed * speed_mult
    
    def draw(self, surf):
        for i in range(self.links):
            t = i / (self.links - 1)
            x = self.x1 + (self.x2 - self.x1) * t + 20 * math.sin(self.swing + t * 2)
            y = self.y1 + (self.y2 - self.y1) * t
            pygame.draw.circle(surf, self.color, (int(x), int(y)), 8)
            pygame.draw.circle(surf, (150, 120, 90), (int(x), int(y)), 8, 2)

class Cog:
    """小齿轮"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(10, 25)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2, 2)
        self.vy = random.uniform(0.3, 1.0)
        self.color = (150, 120, 80)
    
    def update(self, speed_mult=1.0):
        self.rotation += self.rot_speed * speed_mult
        self.y += self.vy * speed_mult
        if self.y > HEIGHT + self.size:
            self.y = -self.size
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        points = []
        for i in range(12):
            angle = math.radians(i * 30 + self.rotation)
            r = self.size if i % 2 == 0 else self.size * 0.7
            points.append((self.x + r * math.cos(angle), self.y + r * math.sin(angle)))
        pygame.draw.polygon(surf, self.color, points)

class InkDrop:
    """墨滴"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = -20
        self.size = random.randint(8, 20)
        self.vy = random.uniform(1.0, 3.0)
        self.spread = 0
        self.landed = False
        self.color = (30, 30, 40)
        self.cached_surf = None
        self.last_spread = -1
    
    def update(self, speed_mult=1.0):
        if not self.landed:
            self.y += self.vy * speed_mult
            if self.y > HEIGHT - 50:
                self.landed = True
                self.spread = self.size
        else:
            self.spread += 0.5
            if self.spread > self.size * 3:
                self.y = -20
                self.x = random.randint(0, WIDTH)
                self.landed = False
                self.spread = 0
                self.cached_surf = None
                self.last_spread = -1
    
    def draw(self, surf):
        if not self.landed:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size)
        else:
            # 缓存墨迹Surface，只在spread变化时重建
            if self.cached_surf is None or int(self.spread) != self.last_spread:
                self.last_spread = int(self.spread)
                size = int(self.spread * 2)
                self.cached_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                alpha = int(150 * (1 - (self.spread - self.size) / (self.size * 2)))
                pygame.draw.circle(self.cached_surf, (*self.color, max(0, alpha)), (int(self.spread), int(self.spread)), int(self.spread))
            surf.blit(self.cached_surf, (self.x - self.spread, HEIGHT - 50 - self.spread))

class BrushStroke:
    """笔触"""
    def __init__(self):
        self.points = []
        start_x = random.randint(0, WIDTH)
        start_y = random.randint(0, HEIGHT)
        for i in range(random.randint(5, 12)):
            self.points.append((
                start_x + i * random.randint(-30, 30),
                start_y + i * random.randint(-20, 20)
            ))
        self.alpha = random.randint(50, 150)
        self.color = (20, 20, 30)
        self.width = random.randint(3, 8)
        self.fade_speed = random.uniform(0.1, 0.3)
        self.cached_surf = None
        self.last_alpha = -1
        self._calculate_bounds()
    
    def _calculate_bounds(self):
        if len(self.points) > 0:
            xs = [p[0] for p in self.points]
            ys = [p[1] for p in self.points]
            self.min_x = max(0, int(min(xs)) - self.width - 2)
            self.min_y = max(0, int(min(ys)) - self.width - 2)
            self.max_x = min(WIDTH, int(max(xs)) + self.width + 2)
            self.max_y = min(HEIGHT, int(max(ys)) + self.width + 2)
            self.offset_points = [(p[0] - self.min_x, p[1] - self.min_y) for p in self.points]
        else:
            self.min_x = self.min_y = 0
            self.max_x = self.max_y = 1
            self.offset_points = []
    
    def update(self, speed_mult=1.0):
        self.alpha -= self.fade_speed * speed_mult
        if self.alpha < 0:
            # 重新生成
            self.points = []
            start_x = random.randint(0, WIDTH)
            start_y = random.randint(0, HEIGHT)
            for i in range(random.randint(5, 12)):
                self.points.append((
                    start_x + i * random.randint(-30, 30),
                    start_y + i * random.randint(-20, 20)
                ))
            self.alpha = random.randint(50, 150)
            self.cached_surf = None
            self.last_alpha = -1
            self._calculate_bounds()
    
    def draw(self, surf):
        if len(self.offset_points) > 1:
            # 只在alpha变化显著时重建Surface
            if self.cached_surf is None or abs(int(self.alpha) - self.last_alpha) > 5:
                self.last_alpha = int(self.alpha)
                w = self.max_x - self.min_x
                h = self.max_y - self.min_y
                self.cached_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                pygame.draw.lines(self.cached_surf, (*self.color, int(self.alpha)), False, self.offset_points, self.width)
            surf.blit(self.cached_surf, (self.min_x, self.min_y))

class PaperBird:
    """纸鸟"""
    def __init__(self):
        self.x = random.randint(-50, WIDTH + 50)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(1.0, 2.5)
        self.vy = random.uniform(-0.3, 0.3)
        self.size = random.randint(15, 30)
        self.flap = 0
        self.flap_speed = random.uniform(0.1, 0.2)
        self.color = (200, 180, 160)
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.flap += self.flap_speed * speed_mult
        if self.x > WIDTH + 50:
            self.x = -50
            self.y = random.randint(0, HEIGHT)
    
    def draw(self, surf):
        # 简单的纸鸟形状
        wing_offset = int(5 * math.sin(self.flap))
        points = [
            (self.x, self.y),  # 头部
            (self.x - self.size, self.y - self.size // 2 + wing_offset),  # 左翼
            (self.x - self.size // 2, self.y),  # 身体
            (self.x - self.size, self.y + self.size // 2 - wing_offset),  # 右翼
        ]
        pygame.draw.polygon(surf, self.color, points)
        pygame.draw.polygon(surf, (150, 140, 130), points, 2)

class Sakura:
    """樱花花瓣"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(1.0, 2.5)
        self.size = random.randint(6, 12)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2, 2)
        self.sway = random.uniform(0, 6.28)
        self.sway_speed = random.uniform(0.05, 0.15)
        self.color = random.choice([(255, 200, 220), (255, 180, 200), (255, 220, 230)])
    
    def update(self, speed_mult=1.0):
        self.sway += self.sway_speed * speed_mult
        self.x += (self.vx + math.sin(self.sway) * 0.5) * speed_mult
        self.y += self.vy * speed_mult
        self.rotation += self.rot_speed * speed_mult
        if self.y > HEIGHT + 20:
            self.y = -20
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        # 五瓣花瓣
        points = []
        for i in range(5):
            angle = math.radians(i * 72 + self.rotation)
            r = self.size if i % 2 == 0 else self.size * 0.4
            points.append((self.x + r * math.cos(angle), self.y + r * math.sin(angle)))
        pygame.draw.polygon(surf, self.color, points)

class Lantern:
    """灯笼"""
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.size = random.randint(20, 40)
        self.sway = random.uniform(0, 6.28)
        self.sway_speed = random.uniform(0.02, 0.05)
        self.glow = random.uniform(0, 6.28)
        self.glow_speed = random.uniform(0.03, 0.08)
        self.color = random.choice([(255, 100, 100), (255, 200, 100), (255, 50, 50)])
    
    def update(self, speed_mult=1.0):
        self.sway += self.sway_speed * speed_mult
        self.glow += self.glow_speed * speed_mult
    
    def draw(self, surf):
        x_offset = int(5 * math.sin(self.sway))
        glow_alpha = int(100 + 100 * math.sin(self.glow))
        # 发光效果
        glow_surf = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, glow_alpha // 2), (self.size * 1.5, self.size * 1.5), self.size * 1.5)
        surf.blit(glow_surf, (self.x + x_offset - self.size * 1.5, self.y - self.size * 1.5))
        # 灯笼主体
        pygame.draw.ellipse(surf, self.color, (self.x + x_offset - self.size // 2, self.y - self.size, self.size, self.size * 2))
        pygame.draw.line(surf, (200, 150, 100), (self.x + x_offset, self.y - self.size - 10), (self.x + x_offset, self.y - self.size), 2)

class Firefly:
    """萤火虫"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.size = random.randint(2, 4)
        self.glow = random.uniform(0, 6.28)
        self.glow_speed = random.uniform(0.1, 0.2)
        self.color = (150, 255, 100)
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.glow += self.glow_speed * speed_mult
        # 随机改变方向
        if random.random() < 0.02:
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(-0.5, 0.5)
        # 边界循环
        if self.x < 0: self.x = WIDTH
        if self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        if self.y > HEIGHT: self.y = 0
    
    def draw(self, surf):
        alpha = int(200 + 55 * math.sin(self.glow))
        glow_surf = pygame.Surface((self.size * 6, self.size * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, alpha // 3), (self.size * 3, self.size * 3), self.size * 3)
        surf.blit(glow_surf, (self.x - self.size * 3, self.y - self.size * 3))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size)

class Coral:
    """珊瑚"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.base_y = HEIGHT
        self.branches = random.randint(3, 6)
        self.height = random.randint(80, 150)
        self.sway = random.uniform(0, 6.28)
        self.sway_speed = random.uniform(0.02, 0.05)
        self.color = random.choice([(255, 100, 150), (100, 200, 255), (150, 100, 255)])
    
    def update(self, speed_mult=1.0):
        self.sway += self.sway_speed * speed_mult
    
    def draw(self, surf):
        # 绘制珊瑚分支
        for i in range(self.branches):
            angle = (i / self.branches) * 180 - 90
            sway_offset = 10 * math.sin(self.sway + i)
            branch_points = []
            for j in range(5):
                t = j / 4
                y = self.base_y - self.height * t
                x = self.x + (angle - 90) / 3 * t * 20 + sway_offset * t
                branch_points.append((x, y))
            if len(branch_points) > 1:
                pygame.draw.lines(surf, self.color, False, branch_points, 4)

class Jellyfish:
    """水母"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(20, 40)
        self.vy = random.uniform(-0.3, -0.1)
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.05, 0.1)
        self.tentacles = random.randint(6, 10)
        self.color = random.choice([(100, 150, 255), (150, 100, 255), (100, 255, 200)])
    
    def update(self, speed_mult=1.0):
        self.y += self.vy * speed_mult
        self.pulse += self.pulse_speed * speed_mult
        if self.y < -self.size * 2:
            self.y = HEIGHT + self.size * 2
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        pulse_size = int(self.size * (1 + 0.2 * math.sin(self.pulse)))
        # 身体
        alpha_surf = pygame.Surface((pulse_size * 2, pulse_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surf, (*self.color, 150), (pulse_size, pulse_size), pulse_size)
        surf.blit(alpha_surf, (self.x - pulse_size, self.y - pulse_size))
        # 触手
        for i in range(self.tentacles):
            angle = (i / self.tentacles) * 360
            wave = math.sin(self.pulse + i) * 10
            end_x = self.x + math.cos(math.radians(angle)) * wave
            end_y = self.y + self.size + 30
            pygame.draw.line(surf, self.color, (self.x, self.y + self.size), (end_x, end_y), 2)

class Bubble2:
    """泡泡（海洋版）"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(HEIGHT, HEIGHT + 100)
        self.size = random.randint(4, 12)
        self.vy = random.uniform(-1.0, -0.3)
        self.vx = random.uniform(-0.2, 0.2)
        self.alpha = random.randint(100, 200)
    
    def update(self, speed_mult=1.0):
        self.y += self.vy * speed_mult
        self.x += self.vx * speed_mult
        if self.y < -20:
            self.y = HEIGHT + 20
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        alpha_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surf, (200, 230, 255, self.alpha), (self.size, self.size), self.size)
        pygame.draw.circle(alpha_surf, (255, 255, 255, self.alpha), (self.size, self.size), self.size, 1)
        surf.blit(alpha_surf, (self.x - self.size, self.y - self.size))

class Sandstorm:
    """沙尘暴粒子"""
    def __init__(self):
        self.x = random.randint(-50, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.vx = random.uniform(3.0, 8.0)
        self.vy = random.uniform(-0.5, 0.5)
        self.alpha = random.randint(50, 150)
        self.color = random.choice([(200, 180, 140), (220, 200, 160), (180, 160, 120)])
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        if self.x > WIDTH + 50:
            self.x = -50
            self.y = random.randint(0, HEIGHT)
    
    def draw(self, surf):
        alpha_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surf, (*self.color, self.alpha), (self.size * 2, self.size * 2), self.size * 2)
        surf.blit(alpha_surf, (self.x - self.size * 2, self.y - self.size * 2))

class Dune:
    """沙丘"""
    def __init__(self):
        self.x = random.randint(-100, WIDTH)
        self.y = random.randint(HEIGHT // 2, HEIGHT)
        self.width = random.randint(100, 300)
        self.height = random.randint(40, 100)
        self.vx = random.uniform(0.2, 0.8)
        self.color = random.choice([(200, 180, 120), (220, 200, 140), (180, 160, 100)])
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        if self.x > WIDTH + 100:
            self.x = -100
            self.y = random.randint(HEIGHT // 2, HEIGHT)
    
    def draw(self, surf):
        # 绘制沙丘形状
        points = [
            (self.x - self.width // 2, self.y + self.height),
            (self.x - self.width // 4, self.y),
            (self.x + self.width // 4, self.y + self.height // 2),
            (self.x + self.width // 2, self.y + self.height)
        ]
        pygame.draw.polygon(surf, self.color, points)

class Cactus:
    """仙人掌（装饰）"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT - random.randint(60, 100)
        self.height = random.randint(40, 80)
        self.color = (80, 120, 80)
    
    def update(self, speed_mult=1.0):
        pass  # 静态装饰
    
    def draw(self, surf):
        # 主体
        pygame.draw.rect(surf, self.color, (self.x - 10, self.y, 20, self.height))
        # 侧枝
        pygame.draw.rect(surf, self.color, (self.x - 25, self.y + 20, 15, 25))
        pygame.draw.rect(surf, self.color, (self.x + 10, self.y + 15, 15, 30))

class Petal:
    """花瓣漩涡"""
    def __init__(self):
        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2
        self.angle = random.uniform(0, 360)
        self.distance = random.randint(50, 300)
        self.rotation_speed = random.uniform(0.5, 1.5)
        self.size = random.randint(8, 16)
        self.color = random.choice([(255, 150, 200), (200, 100, 255), (150, 200, 255)])
        self.spiral_speed = random.uniform(-0.3, -0.1)
    
    def update(self, speed_mult=1.0):
        self.angle += self.rotation_speed * speed_mult
        self.distance += self.spiral_speed * speed_mult
        if self.distance < 20:
            self.distance = 300
            self.angle = random.uniform(0, 360)
    
    def draw(self, surf):
        rad = math.radians(self.angle)
        x = self.center_x + self.distance * math.cos(rad)
        y = self.center_y + self.distance * math.sin(rad)
        alpha = int(200 * (self.distance / 300))
        alpha_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surf, (*self.color, alpha), (self.size, self.size), self.size)
        surf.blit(alpha_surf, (x - self.size, y - self.size))

class Butterfly:
    """蝴蝶"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-1.0, 1.0)
        self.vy = random.uniform(-1.0, 1.0)
        self.size = random.randint(10, 18)
        self.flap = random.uniform(0, 6.28)
        self.flap_speed = random.uniform(0.2, 0.4)
        self.color = random.choice([(255, 200, 100), (100, 200, 255), (255, 100, 200)])
        self.turn_timer = 0
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.flap += self.flap_speed * speed_mult
        self.turn_timer += speed_mult
        
        # 随机转向
        if self.turn_timer > 60:
            self.turn_timer = 0
            self.vx = random.uniform(-1.0, 1.0)
            self.vy = random.uniform(-1.0, 1.0)
        
        # 边界循环
        if self.x < -20: self.x = WIDTH + 20
        if self.x > WIDTH + 20: self.x = -20
        if self.y < -20: self.y = HEIGHT + 20
        if self.y > HEIGHT + 20: self.y = -20
    
    def draw(self, surf):
        wing_offset = int(self.size * 0.3 * math.sin(self.flap))
        # 左翼
        pygame.draw.ellipse(surf, self.color, (self.x - self.size - wing_offset, self.y - self.size // 2, self.size, self.size))
        # 右翼
        pygame.draw.ellipse(surf, self.color, (self.x + wing_offset, self.y - self.size // 2, self.size, self.size))
        # 身体
        pygame.draw.line(surf, (50, 50, 50), (self.x, self.y - self.size // 2), (self.x, self.y + self.size // 2), 3)

class WindLeaf:
    """风吹落叶"""
    def __init__(self):
        self.x = random.randint(-50, WIDTH + 50)
        self.y = random.randint(-100, HEIGHT)
        self.vx = random.uniform(2.0, 5.0)
        self.vy = random.uniform(0.5, 1.5)
        self.size = random.randint(8, 15)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-5, 5)
        self.color = random.choice([(180, 140, 80), (160, 120, 60), (200, 160, 100)])
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.rotation += self.rot_speed * speed_mult
        if self.x > WIDTH + 50 or self.y > HEIGHT + 50:
            self.x = random.randint(-50, 0)
            self.y = random.randint(-50, 0)
    
    def draw(self, surf):
        points = []
        for i in range(4):
            angle = math.radians(i * 90 + self.rotation)
            r = self.size if i % 2 == 0 else self.size * 0.6
            points.append((self.x + r * math.cos(angle), self.y + r * math.sin(angle)))
        pygame.draw.polygon(surf, self.color, points)

class Dandelion:
    """蒲公英种子"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.8, -0.2)
        self.size = random.randint(3, 6)
        self.float_offset = random.uniform(0, 6.28)
        self.float_speed = random.uniform(0.05, 0.1)
        self.color = (240, 240, 230)
    
    def update(self, speed_mult=1.0):
        self.float_offset += self.float_speed * speed_mult
        self.x += (self.vx + math.sin(self.float_offset) * 0.5) * speed_mult
        self.y += self.vy * speed_mult
        if self.y < -20:
            self.y = HEIGHT + 20
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        # 伞状结构
        for i in range(8):
            angle = math.radians(i * 45)
            end_x = self.x + self.size * 2 * math.cos(angle)
            end_y = self.y + self.size * 2 * math.sin(angle) - self.size
            pygame.draw.line(surf, self.color, (self.x, self.y - self.size), (end_x, end_y), 1)
        # 种子
        pygame.draw.circle(surf, (200, 180, 160), (int(self.x), int(self.y)), self.size // 2)

class Vine:
    """藤蔓"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = 0
        self.length = random.randint(100, 200)
        self.segments = 10
        self.sway = random.uniform(0, 6.28)
        self.sway_speed = random.uniform(0.03, 0.06)
        self.color = (60, 120, 60)
        self.leaf_positions = [random.randint(2, 8) for _ in range(3)]
    
    def update(self, speed_mult=1.0):
        self.sway += self.sway_speed * speed_mult
    
    def draw(self, surf):
        points = []
        for i in range(self.segments + 1):
            t = i / self.segments
            offset = 20 * math.sin(self.sway + t * 3) * t
            points.append((self.x + offset, self.y + self.length * t))
        
        if len(points) > 1:
            pygame.draw.lines(surf, self.color, False, points, 4)
            # 叶子
            for leaf_seg in self.leaf_positions:
                if leaf_seg < len(points):
                    lx, ly = points[leaf_seg]
                    pygame.draw.ellipse(surf, (80, 150, 80), (lx - 8, ly - 4, 16, 8))

class Mushroom:
    """发光蘑菇"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT - random.randint(20, 60)
        self.size = random.randint(15, 30)
        self.glow = random.uniform(0, 6.28)
        self.glow_speed = random.uniform(0.04, 0.08)
        self.color = random.choice([(100, 200, 255), (255, 100, 200), (200, 255, 100)])
    
    def update(self, speed_mult=1.0):
        self.glow += self.glow_speed * speed_mult
    
    def draw(self, surf):
        alpha = int(150 + 100 * math.sin(self.glow))
        # 发光效果
        glow_surf = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, alpha // 2), (self.size * 1.5, self.size * 1.5), self.size * 1.5)
        surf.blit(glow_surf, (self.x - self.size * 1.5, self.y - self.size - self.size * 1.5))
        # 蘑菇帽
        pygame.draw.circle(surf, self.color, (self.x, self.y - self.size), self.size)
        # 蘑菇柄
        pygame.draw.rect(surf, (200, 200, 200), (self.x - self.size // 4, self.y - self.size, self.size // 2, self.size))

class Prism:
    """三棱镜光线"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.angle = random.uniform(0, 360)
        self.length = random.randint(50, 150)
        self.width = random.randint(20, 40)
        self.rotation_speed = random.uniform(0.2, 0.5)
        self.colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
        self.alpha = random.randint(50, 120)
    
    def update(self, speed_mult=1.0):
        self.angle += self.rotation_speed * speed_mult
    
    def draw(self, surf):
        rad = math.radians(self.angle)
        alpha_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i, color in enumerate(self.colors):
            offset = (i - 3) * (self.width // 7)
            start_x = self.x + offset * math.cos(rad + math.pi/2)
            start_y = self.y + offset * math.sin(rad + math.pi/2)
            end_x = start_x + self.length * math.cos(rad)
            end_y = start_y + self.length * math.sin(rad)
            pygame.draw.line(alpha_surf, (*color, self.alpha), (start_x, start_y), (end_x, end_y), 3)
        surf.blit(alpha_surf, (0, 0))

class Particle:
    """彩虹粒子"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-1.0, 1.0)
        self.vy = random.uniform(-1.0, 1.0)
        self.size = random.randint(2, 5)
        self.color = random.choice([(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)])
        self.life = random.randint(100, 200)
        self.max_life = self.life
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.life -= speed_mult
        if self.life <= 0:
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)
            self.life = self.max_life
    
    def draw(self, surf):
        alpha = int(255 * (self.life / self.max_life))
        alpha_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surf, (*self.color, alpha), (self.size * 2, self.size * 2), self.size * 2)
        surf.blit(alpha_surf, (self.x - self.size * 2, self.y - self.size * 2))

class Feather:
    """羽毛"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-100, HEIGHT)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(0.5, 1.5)
        self.size = random.randint(12, 20)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-1.5, 1.5)
        self.sway = random.uniform(0, 6.28)
        self.sway_speed = random.uniform(0.08, 0.15)
        self.color = random.choice([(255, 255, 255), (240, 240, 250), (200, 220, 255)])
    
    def update(self, speed_mult=1.0):
        self.sway += self.sway_speed * speed_mult
        self.x += (self.vx + math.sin(self.sway) * 0.8) * speed_mult
        self.y += self.vy * speed_mult
        self.rotation += self.rot_speed * speed_mult
        if self.y > HEIGHT + 50:
            self.y = -50
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        # 羽毛形状
        rad = math.radians(self.rotation)
        points = []
        for i in range(7):
            t = i / 6
            offset = self.size * 0.4 * math.sin(t * math.pi)
            px = self.x + (t * self.size - self.size / 2) * math.cos(rad) - offset * math.sin(rad)
            py = self.y + (t * self.size - self.size / 2) * math.sin(rad) + offset * math.cos(rad)
            points.append((px, py))
        if len(points) > 2:
            pygame.draw.lines(surf, self.color, False, points, 3)

class Cloud2:
    """云朵"""
    def __init__(self):
        self.x = random.randint(-100, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(0.2, 0.8)
        self.size = random.randint(40, 80)
        self.circles = [(random.randint(-self.size, self.size), random.randint(-20, 20), random.randint(20, 40)) for _ in range(4)]
        self.alpha = random.randint(100, 180)
        self.color = (255, 255, 255)
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        if self.x > WIDTH + 100:
            self.x = -100
            self.y = random.randint(0, HEIGHT)
    
    def draw(self, surf):
        alpha_surf = pygame.Surface((self.size * 3, self.size * 2), pygame.SRCALPHA)
        for ox, oy, r in self.circles:
            pygame.draw.circle(alpha_surf, (*self.color, self.alpha), (self.size + ox, self.size // 2 + oy), r)
        surf.blit(alpha_surf, (self.x - self.size, self.y - self.size // 2))

class Bird:
    """飞鸟剪影"""
    def __init__(self):
        self.x = random.randint(-50, WIDTH)
        self.y = random.randint(0, HEIGHT // 2)
        self.vx = random.uniform(2.0, 4.0)
        self.size = random.randint(15, 25)
        self.flap = random.uniform(0, 6.28)
        self.flap_speed = random.uniform(0.15, 0.25)
        self.color = (50, 50, 50)
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.flap += self.flap_speed * speed_mult
        if self.x > WIDTH + 50:
            self.x = -50
            self.y = random.randint(0, HEIGHT // 2)
    
    def draw(self, surf):
        wing_y = int(self.size * 0.3 * math.sin(self.flap))
        # V字形飞鸟
        points = [
            (self.x, self.y),
            (self.x - self.size, self.y - self.size // 2 + wing_y),
            (self.x, self.y),
            (self.x + self.size, self.y - self.size // 2 - wing_y)
        ]
        pygame.draw.lines(surf, self.color, False, points, 2)

class Ripple:
    """涟漪"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = 0
        self.max_radius = random.randint(50, 100)
        self.speed = random.uniform(0.5, 1.0)
        self.life = 255
        self.color = random.choice([(100, 200, 255), (100, 255, 200), (200, 100, 255)])
    
    def update(self, speed_mult=1.0):
        self.radius += self.speed * speed_mult
        self.life = int(255 * (1 - self.radius / self.max_radius))
        if self.radius > self.max_radius:
            self.radius = 0
            self.life = 255
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)
    
    def draw(self, surf):
        if self.life > 0:
            alpha_surf = pygame.Surface((int(self.radius * 2 + 10), int(self.radius * 2 + 10)), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surf, (*self.color, self.life), (int(self.radius) + 5, int(self.radius) + 5), int(self.radius), 2)
            surf.blit(alpha_surf, (self.x - self.radius - 5, self.y - self.radius - 5))

class Koi:
    """锦鲤"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-1.5, 1.5)
        self.size = random.randint(20, 35)
        self.tail_sway = random.uniform(0, 6.28)
        self.tail_speed = random.uniform(0.1, 0.2)
        self.color = random.choice([(255, 150, 100), (255, 200, 200), (255, 255, 200)])
        self.turn_timer = 0
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.tail_sway += self.tail_speed * speed_mult
        self.turn_timer += speed_mult
        
        # 随机转向
        if self.turn_timer > 80:
            self.turn_timer = 0
            self.vx = random.uniform(-1.5, 1.5)
            self.vy = random.uniform(-1.5, 1.5)
        
        # 边界循环
        if self.x < -50: self.x = WIDTH + 50
        if self.x > WIDTH + 50: self.x = -50
        if self.y < -50: self.y = HEIGHT + 50
        if self.y > HEIGHT + 50: self.y = -50
    
    def draw(self, surf):
        # 身体
        pygame.draw.ellipse(surf, self.color, (self.x - self.size, self.y - self.size // 2, self.size * 2, self.size))
        # 尾巴
        tail_offset = int(10 * math.sin(self.tail_sway))
        tail_points = [
            (self.x - self.size, self.y),
            (self.x - self.size - 15, self.y - 10 + tail_offset),
            (self.x - self.size - 15, self.y + 10 + tail_offset)
        ]
        pygame.draw.polygon(surf, self.color, tail_points)

class Pollen:
    """花粉"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.size = random.randint(2, 4)
        self.float_offset = random.uniform(0, 6.28)
        self.float_speed = random.uniform(0.1, 0.2)
        self.color = random.choice([(255, 255, 150), (255, 200, 150), (255, 220, 180)])
    
    def update(self, speed_mult=1.0):
        self.float_offset += self.float_speed * speed_mult
        self.x += (self.vx + math.cos(self.float_offset) * 0.3) * speed_mult
        self.y += (self.vy + math.sin(self.float_offset) * 0.3) * speed_mult
        
        # 边界循环
        if self.x < 0: self.x = WIDTH
        if self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        if self.y > HEIGHT: self.y = 0
    
    def draw(self, surf):
        glow_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, 180), (self.size * 2, self.size * 2), self.size * 2)
        surf.blit(glow_surf, (self.x - self.size * 2, self.y - self.size * 2))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size)

class Mote:
    """尘埃光点"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-0.2, 0.2)
        self.vy = random.uniform(-0.8, -0.2)
        self.size = random.randint(1, 3)
        self.alpha = random.randint(100, 255)
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.05, 0.1)
        self.color = (255, 250, 230)
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.pulse += self.pulse_speed * speed_mult
        
        if self.y < -10:
            self.y = HEIGHT + 10
            self.x = random.randint(0, WIDTH)
        if self.x < -10: self.x = WIDTH + 10
        if self.x > WIDTH + 10: self.x = -10
    
    def draw(self, surf):
        alpha = int(self.alpha * (0.7 + 0.3 * math.sin(self.pulse)))
        glow_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, alpha), (self.size * 2, self.size * 2), self.size * 2)
        surf.blit(glow_surf, (self.x - self.size * 2, self.y - self.size * 2))

class HolyRay:
    """圣光光柱"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = 0
        self.width = random.randint(30, 60)
        self.height = random.randint(200, 400)
        self.alpha = random.randint(30, 80)
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.02, 0.05)
        self.color = (255, 250, 200)
    
    def update(self, speed_mult=1.0):
        self.pulse += self.pulse_speed * speed_mult
    
    def draw(self, surf):
        alpha = int(self.alpha * (0.8 + 0.2 * math.sin(self.pulse)))
        alpha_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # 渐变光柱
        for i in range(self.height):
            t = i / self.height
            current_alpha = int(alpha * (1 - t * 0.5))
            pygame.draw.line(alpha_surf, (*self.color, current_alpha), (0, i), (self.width, i))
        surf.blit(alpha_surf, (self.x - self.width // 2, self.y))

class Angel:
    """天使光环"""
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.radius = random.randint(40, 80)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(0.5, 1.5)
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.04, 0.08)
        self.float_offset = random.uniform(0, 6.28)
        self.float_speed = random.uniform(0.03, 0.06)
        self.color = (255, 240, 150)
    
    def update(self, speed_mult=1.0):
        self.rotation += self.rot_speed * speed_mult
        self.pulse += self.pulse_speed * speed_mult
        self.float_offset += self.float_speed * speed_mult
    
    def draw(self, surf):
        y_offset = 10 * math.sin(self.float_offset)
        alpha = int(180 + 75 * math.sin(self.pulse))
        
        # 外圈光环
        alpha_surf = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surf, (*self.color, alpha // 3), (self.radius * 1.5, self.radius * 1.5), int(self.radius * 1.2), 8)
        surf.blit(alpha_surf, (self.x - self.radius * 1.5, self.y + y_offset - self.radius * 1.5))
        
        # 内圈光环
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y + y_offset)), self.radius, 3)
        
        # 十字光
        for angle in [0, 90]:
            rad = math.radians(angle + self.rotation)
            end_x = self.x + self.radius * 0.7 * math.cos(rad)
            end_y = self.y + y_offset + self.radius * 0.7 * math.sin(rad)
            pygame.draw.line(surf, self.color, (self.x, self.y + y_offset), (end_x, end_y), 2)

class Pixel:
    """像素方块"""
    def __init__(self):
        self.x = random.randint(0, WIDTH // 20) * 20
        self.y = random.randint(0, HEIGHT // 20) * 20
        self.size = 20
        self.vy = random.choice([10, 20])
        self.color = random.choice([(255, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 0)])
        self.blink = random.randint(0, 30)
    
    def update(self, speed_mult=1.0):
        self.y += self.vy * speed_mult
        self.blink = (self.blink + 1) % 60
        if self.y > HEIGHT:
            self.y = -self.size
            self.x = random.randint(0, WIDTH // 20) * 20
    
    def draw(self, surf):
        if self.blink < 30:
            pygame.draw.rect(surf, self.color, (self.x, self.y, self.size, self.size))
            pygame.draw.rect(surf, (255, 255, 255), (self.x, self.y, self.size, self.size), 2)

class Glitch:
    """故障条纹"""
    def __init__(self):
        self.y = random.randint(0, HEIGHT)
        self.height = random.randint(5, 30)
        self.speed = random.uniform(10, 30)
        self.color = random.choice([(255, 0, 100), (0, 255, 200), (255, 255, 100)])
        self.offset = random.randint(-20, 20)
        self.life = random.randint(10, 30)
    
    def update(self, speed_mult=1.0):
        self.y += self.speed * speed_mult
        self.life -= speed_mult
        if self.y > HEIGHT or self.life <= 0:
            self.y = random.randint(-50, 0)
            self.life = random.randint(10, 30)
            self.offset = random.randint(-20, 20)
    
    def draw(self, surf):
        alpha = int(150 * (self.life / 30))
        rect_surf = pygame.Surface((WIDTH, self.height), pygame.SRCALPHA)
        pygame.draw.rect(rect_surf, (*self.color, alpha), (0, 0, WIDTH, self.height))
        surf.blit(rect_surf, (self.offset, self.y))

class DigitalRain:
    """数字雨"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.uniform(3, 8)
        self.chars = [str(random.randint(0, 1)) for _ in range(random.randint(5, 15))]
        self.color = (0, 255, 150)
    
    def update(self, speed_mult=1.0):
        self.y += self.speed * speed_mult
        if self.y > HEIGHT + len(self.chars) * 20:
            self.y = random.randint(-HEIGHT, 0)
            self.x = random.randint(0, WIDTH)
            self.chars = [str(random.randint(0, 1)) for _ in range(random.randint(5, 15))]
    
    def draw(self, surf):
        font = pygame.font.Font(None, 20)
        for i, char in enumerate(self.chars):
            alpha = int(255 * ((len(self.chars) - i) / len(self.chars)))
            text_surf = font.render(char, True, self.color)
            text_surf.set_alpha(alpha)
            surf.blit(text_surf, (self.x, self.y + i * 20))

class Portal:
    """传送门"""
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.radius = random.randint(40, 80)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(1, 3)
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.05, 0.1)
        self.color = random.choice([(100, 100, 255), (255, 100, 255), (100, 255, 255)])
    
    def update(self, speed_mult=1.0):
        self.rotation += self.rot_speed * speed_mult
        self.pulse += self.pulse_speed * speed_mult
    
    def draw(self, surf):
        pulse_radius = int(self.radius * (1 + 0.2 * math.sin(self.pulse)))
        # 多层圆环
        for i in range(5):
            r = pulse_radius - i * 8
            alpha = int(150 - i * 30)
            ring_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*self.color, alpha), (r, r), r, 3)
            surf.blit(ring_surf, (self.x - r, self.y - r))
        # 旋转线条
        for i in range(8):
            angle = math.radians(i * 45 + self.rotation)
            start_r = pulse_radius * 0.3
            end_r = pulse_radius * 0.8
            start_x = self.x + start_r * math.cos(angle)
            start_y = self.y + start_r * math.sin(angle)
            end_x = self.x + end_r * math.cos(angle)
            end_y = self.y + end_r * math.sin(angle)
            pygame.draw.line(surf, self.color, (start_x, start_y), (end_x, end_y), 2)

class Wormhole:
    """虫洞粒子"""
    def __init__(self):
        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2
        self.angle = random.uniform(0, 360)
        self.distance = random.randint(50, 300)
        self.speed = random.uniform(-2, -0.5)
        self.size = random.randint(2, 6)
        self.color = random.choice([(150, 100, 255), (100, 150, 255), (255, 100, 200)])
    
    def update(self, speed_mult=1.0):
        self.angle += random.uniform(-2, 2) * speed_mult
        self.distance += self.speed * speed_mult
        if self.distance < 10:
            self.distance = 300
            self.angle = random.uniform(0, 360)
    
    def draw(self, surf):
        rad = math.radians(self.angle)
        x = self.center_x + self.distance * math.cos(rad)
        y = self.center_y + self.distance * math.sin(rad)
        alpha = int(255 * (1 - self.distance / 300))
        glow_surf = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, alpha), (self.size * 1.5, self.size * 1.5), self.size * 1.5)
        surf.blit(glow_surf, (x - self.size * 1.5, y - self.size * 1.5))

class Distortion:
    """扭曲波纹"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = 0
        self.max_radius = random.randint(80, 150)
        self.speed = random.uniform(1, 2)
        self.color = random.choice([(100, 200, 255), (255, 100, 200), (100, 255, 200)])
    
    def update(self, speed_mult=1.0):
        self.radius += self.speed * speed_mult
        if self.radius > self.max_radius:
            self.radius = 0
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)
    
    def draw(self, surf):
        alpha = int(200 * (1 - self.radius / self.max_radius))
        if alpha > 0:
            ring_surf = pygame.Surface((int(self.radius * 2 + 10), int(self.radius * 2 + 10)), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*self.color, alpha), (int(self.radius) + 5, int(self.radius) + 5), int(self.radius), 3)
            surf.blit(ring_surf, (self.x - self.radius - 5, self.y - self.radius - 5))

class Origami:
    """折纸动物"""
    def __init__(self):
        self.x = random.randint(-50, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(0.5, 1.5)
        self.size = random.randint(20, 35)
        self.rotation = 0
        self.rot_speed = random.uniform(0.5, 1.5)
        self.shape = random.randint(0, 2)  # 不同折纸形状
        self.color = random.choice([(255, 200, 200), (200, 255, 200), (200, 200, 255)])
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.rotation += self.rot_speed * speed_mult
        if self.x > WIDTH + 50:
            self.x = -50
            self.y = random.randint(0, HEIGHT)
    
    def draw(self, surf):
        if self.shape == 0:  # 纸鹤
            points = [
                (self.x, self.y - self.size),
                (self.x - self.size, self.y),
                (self.x, self.y + self.size // 2),
                (self.x + self.size, self.y)
            ]
        elif self.shape == 1:  # 纸船
            points = [
                (self.x - self.size, self.y + self.size // 2),
                (self.x, self.y - self.size // 2),
                (self.x + self.size, self.y + self.size // 2),
                (self.x, self.y + self.size)
            ]
        else:  # 纸飞机
            points = [
                (self.x + self.size, self.y),
                (self.x - self.size // 2, self.y - self.size // 2),
                (self.x, self.y),
                (self.x - self.size // 2, self.y + self.size // 2)
            ]
        pygame.draw.polygon(surf, self.color, points)
        pygame.draw.polygon(surf, (150, 150, 150), points, 2)

class PaperWave:
    """纸浪"""
    def __init__(self):
        self.y = random.randint(0, HEIGHT)
        self.wave_offset = random.uniform(0, 6.28)
        self.wave_speed = random.uniform(0.05, 0.1)
        self.amplitude = random.randint(20, 40)
        self.color = (230, 230, 250)
        self.last_offset = None
        self.cached_surf = None
        self.min_y = max(0, self.y - self.amplitude - 10)
        self.max_y = min(HEIGHT, self.y + self.amplitude + 10)
    
    def update(self, speed_mult=1.0):
        self.wave_offset += self.wave_speed * speed_mult
    
    def draw(self, surf):
        # 只在偏移变化较大时重建Surface
        if self.cached_surf is None or self.last_offset is None or abs(self.wave_offset - self.last_offset) > 0.2:
            self.last_offset = self.wave_offset
            height = self.max_y - self.min_y
            self.cached_surf = pygame.Surface((WIDTH, height), pygame.SRCALPHA)
            points = []
            for x in range(0, WIDTH, 20):
                wave_y = self.amplitude * math.sin((x / 50) + self.wave_offset)
                points.append((x, wave_y + self.amplitude + 5))
            if len(points) > 1:
                pygame.draw.lines(self.cached_surf, self.color, False, points, 3)
        
        if self.cached_surf:
            surf.blit(self.cached_surf, (0, self.min_y))

class FoldLine:
    """折痕线"""
    def __init__(self):
        self.x1 = random.randint(0, WIDTH)
        self.y1 = random.randint(0, HEIGHT)
        self.x2 = random.randint(0, WIDTH)
        self.y2 = random.randint(0, HEIGHT)
        self.alpha = random.randint(50, 150)
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.03, 0.06)
        self.color = (200, 200, 220)
        self.last_alpha = None
        self.cached_surf = None
        # 计算线条边界
        self.min_x = max(0, min(self.x1, self.x2) - 5)
        self.max_x = min(WIDTH, max(self.x1, self.x2) + 5)
        self.min_y = max(0, min(self.y1, self.y2) - 5)
        self.max_y = min(HEIGHT, max(self.y1, self.y2) + 5)
    
    def update(self, speed_mult=1.0):
        self.pulse += self.pulse_speed * speed_mult
    
    def draw(self, surf):
        current_alpha = int(self.alpha * (0.7 + 0.3 * math.sin(self.pulse)))
        # 只在alpha变化超过阈值时重建
        if self.cached_surf is None or self.last_alpha is None or abs(current_alpha - self.last_alpha) > 5:
            self.last_alpha = current_alpha
            width = self.max_x - self.min_x
            height = self.max_y - self.min_y
            self.cached_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            local_x1 = self.x1 - self.min_x
            local_y1 = self.y1 - self.min_y
            local_x2 = self.x2 - self.min_x
            local_y2 = self.y2 - self.min_y
            pygame.draw.line(self.cached_surf, (*self.color, current_alpha), (local_x1, local_y1), (local_x2, local_y2), 2)
        
        if self.cached_surf:
            surf.blit(self.cached_surf, (self.min_x, self.min_y))

class Candle:
    """蜡烛火焰"""
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = HEIGHT - random.randint(30, 80)
        self.base_size = random.randint(12, 20)
        self.flicker = random.uniform(0, 6.28)
        self.flicker_speed = random.uniform(0.3, 0.5)
        self.color = (255, 180, 100)
        self.last_size = None
        self.cached_glow = None
    
    def update(self, speed_mult=1.0):
        self.flicker += self.flicker_speed * speed_mult
    
    def draw(self, surf):
        size = int(self.base_size * (0.9 + 0.2 * math.sin(self.flicker)))
        alpha = int(220 + 35 * math.sin(self.flicker * 2))
        # 只在尺寸变化时重建光晕
        if self.last_size != size:
            self.last_size = size
            self.cached_glow = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            pygame.draw.circle(self.cached_glow, (255, 200, 100, alpha // 3), (size * 2, size * 2), size * 2)
        
        if self.cached_glow:
            surf.blit(self.cached_glow, (self.x - size * 2, self.y - size * 3))
        # 火焰
        points = [
            (self.x, self.y - size * 2),
            (self.x - size // 2, self.y),
            (self.x + size // 2, self.y)
        ]
        pygame.draw.polygon(surf, (255, 220, 150), points)
        pygame.draw.polygon(surf, self.color, [(points[0][0], points[0][1] + 5), 
                                                 (points[1][0] + 3, points[1][1] - 3),
                                                 (points[2][0] - 3, points[2][1] - 3)])

class BookPage:
    """书页翻飞"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-100, HEIGHT)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(0.5, 1.5)
        self.width = random.randint(25, 40)
        self.height = random.randint(35, 55)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2, 2)
        self.color = (250, 245, 235)
        # 预渲染书页
        self.base_page = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.base_page, self.color, (0, 0, self.width, self.height))
        pygame.draw.rect(self.base_page, (200, 195, 185), (0, 0, self.width, self.height), 1)
        for i in range(3):
            y = 8 + i * 10
            pygame.draw.line(self.base_page, (180, 175, 165), (5, y), (self.width - 5, y), 1)
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.rotation += self.rot_speed * speed_mult
        if self.y > HEIGHT + 50:
            self.y = -50
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        rotated = pygame.transform.rotate(self.base_page, self.rotation)
        rect = rotated.get_rect(center=(self.x, self.y))
        surf.blit(rotated, rect)

class Quill:
    """羽毛笔痕迹"""
    def __init__(self):
        self.reset_points()
        self.alpha = random.randint(150, 255)
        self.fade_speed = random.uniform(0.5, 1.0)
        self.color = (60, 50, 40)
        self.cached_surf = None
        self.last_alpha = None
    
    def reset_points(self):
        start_x = random.randint(50, WIDTH - 50)
        start_y = random.randint(50, HEIGHT - 50)
        self.points = []
        for i in range(random.randint(8, 15)):
            self.points.append((
                start_x + i * random.randint(-15, 15),
                start_y + i * random.randint(-8, 8)
            ))
        # 计算边界
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        self.min_x = max(0, min(xs) - 5)
        self.max_x = min(WIDTH, max(xs) + 5)
        self.min_y = max(0, min(ys) - 5)
        self.max_y = min(HEIGHT, max(ys) + 5)
        self.cached_surf = None
    
    def update(self, speed_mult=1.0):
        self.alpha -= self.fade_speed * speed_mult
        if self.alpha < 0:
            self.reset_points()
            self.alpha = random.randint(150, 255)
    
    def draw(self, surf):
        if len(self.points) > 1:
            current_alpha = int(self.alpha)
            # 只在alpha变化超过阈值时重建
            if self.cached_surf is None or self.last_alpha is None or abs(current_alpha - self.last_alpha) > 10:
                self.last_alpha = current_alpha
                width = self.max_x - self.min_x
                height = self.max_y - self.min_y
                self.cached_surf = pygame.Surface((width, height), pygame.SRCALPHA)
                local_points = [(p[0] - self.min_x, p[1] - self.min_y) for p in self.points]
                pygame.draw.lines(self.cached_surf, (*self.color, current_alpha), False, local_points, 2)
            
            if self.cached_surf:
                surf.blit(self.cached_surf, (self.min_x, self.min_y))

class Satellite:
    """卫星"""
    def __init__(self):
        self.angle = random.uniform(0, 360)
        self.orbit_radius = random.randint(200, 350)
        self.speed = random.uniform(0.3, 0.8)
        self.size = random.randint(8, 15)
        self.blink = random.uniform(0, 6.28)
        self.blink_speed = random.uniform(0.1, 0.2)
        self.color = (200, 200, 220)
        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2
    
    def update(self, speed_mult=1.0):
        self.angle += self.speed * speed_mult
        self.blink += self.blink_speed * speed_mult
    
    def draw(self, surf):
        rad = math.radians(self.angle)
        x = self.center_x + self.orbit_radius * math.cos(rad)
        y = self.center_y + self.orbit_radius * math.sin(rad)
        
        # 卫星本体
        alpha = int(200 + 55 * math.sin(self.blink))
        pygame.draw.rect(surf, self.color, (x - self.size // 2, y - self.size // 2, self.size, self.size))
        # 太阳能板
        pygame.draw.rect(surf, (100, 150, 200), (x - self.size * 1.5, y - 3, self.size, 6))
        pygame.draw.rect(surf, (100, 150, 200), (x + self.size * 0.5, y - 3, self.size, 6))
        # 信号光
        glow_surf = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (200, 220, 255, alpha), (self.size * 1.5, self.size * 1.5), self.size)
        surf.blit(glow_surf, (x - self.size * 1.5, y - self.size * 1.5))

class SignalWave:
    """信号波"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = 0
        self.max_radius = random.randint(60, 120)
        self.speed = random.uniform(1.5, 2.5)
        self.color = (100, 200, 255)
    
    def update(self, speed_mult=1.0):
        self.radius += self.speed * speed_mult
        if self.radius > self.max_radius:
            self.radius = 0
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)
    
    def draw(self, surf):
        alpha = int(180 * (1 - self.radius / self.max_radius))
        if alpha > 0:
            for i in range(3):
                r = self.radius - i * 10
                if r > 0:
                    ring_surf = pygame.Surface((int(r * 2 + 10), int(r * 2 + 10)), pygame.SRCALPHA)
                    pygame.draw.circle(ring_surf, (*self.color, alpha // (i + 1)), (int(r) + 5, int(r) + 5), int(r), 2)
                    surf.blit(ring_surf, (self.x - r - 5, self.y - r - 5))

class DataStream:
    """数据流"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.target_x = random.randint(0, WIDTH)
        self.target_y = random.randint(0, HEIGHT)
        self.progress = 0
        self.speed = random.uniform(0.02, 0.05)
        self.particles = []
        for _ in range(5):
            self.particles.append(random.uniform(0, 1))
        self.color = random.choice([(100, 255, 200), (100, 200, 255), (255, 200, 100)])
    
    def update(self, speed_mult=1.0):
        self.progress += self.speed * speed_mult
        if self.progress > 1:
            self.progress = 0
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)
            self.target_x = random.randint(0, WIDTH)
            self.target_y = random.randint(0, HEIGHT)
    
    def draw(self, surf):
        # 连线
        alpha = 100
        pygame.draw.line(surf, (*self.color, alpha), (self.x, self.y), (self.target_x, self.target_y), 1)
        # 移动的粒子
        for p in self.particles:
            t = (self.progress + p * 0.2) % 1
            px = self.x + (self.target_x - self.x) * t
            py = self.y + (self.target_y - self.y) * t
            alpha = int(200 * (1 - abs(t - 0.5) * 2))
            glow_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, alpha), (4, 4), 4)
            surf.blit(glow_surf, (px - 4, py - 4))

class EnergyNode:
    """能量节点"""
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.radius = random.randint(15, 25)
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.08, 0.15)
        self.color = random.choice([(200, 100, 255), (150, 50, 255), (255, 100, 200)])
        self.rotation = 0
        self.rot_speed = random.uniform(0.5, 1.5)
        self.last_radius = None
        self.cached_rings = None
    
    def update(self, speed_mult=1.0):
        self.pulse += self.pulse_speed * speed_mult
        self.rotation += self.rot_speed * speed_mult
    
    def draw(self, surf):
        # 核心光球
        scale = 0.8 + 0.2 * math.sin(self.pulse)
        r = int(self.radius * scale)
        alpha = int(200 + 55 * math.sin(self.pulse * 2))
        
        # 只在半径变化时重建能量环
        if self.last_radius != r:
            self.last_radius = r
            max_r = r + 16
            self.cached_rings = pygame.Surface((max_r * 2 + 10, max_r * 2 + 10), pygame.SRCALPHA)
            for i in range(3):
                ring_r = r + i * 8
                pygame.draw.circle(self.cached_rings, (*self.color, alpha // (i + 2)), (max_r + 5, max_r + 5), ring_r, 2)
        
        if self.cached_rings:
            max_r = r + 16
            surf.blit(self.cached_rings, (self.x - max_r - 5, self.y - max_r - 5))
        
        # 核心
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), r)
        
        # 旋转的能量线（减少到四条）
        for angle in range(0, 360, 90):
            rad = math.radians(angle + self.rotation)
            x1 = self.x + r * math.cos(rad)
            y1 = self.y + r * math.sin(rad)
            x2 = self.x + (r + 15) * math.cos(rad)
            y2 = self.y + (r + 15) * math.sin(rad)
            pygame.draw.line(surf, (*self.color, 180), (x1, y1), (x2, y2), 2)

class LightningArc:
    """闪电弧"""
    def __init__(self):
        self.start_x = random.randint(0, WIDTH)
        self.start_y = random.randint(0, HEIGHT)
        self.end_x = random.randint(0, WIDTH)
        self.end_y = random.randint(0, HEIGHT)
        self.segments = []
        self.generate_arc()
        self.life = random.randint(10, 30)
        self.max_life = self.life
        self.color = random.choice([(150, 200, 255), (200, 150, 255), (255, 200, 150)])
    
    def generate_arc(self):
        self.segments = []
        steps = random.randint(8, 15)
        for i in range(steps + 1):
            t = i / steps
            x = self.start_x + (self.end_x - self.start_x) * t
            y = self.start_y + (self.end_y - self.start_y) * t
            # 添加随机偏移
            offset_x = random.uniform(-20, 20)
            offset_y = random.uniform(-20, 20)
            self.segments.append((x + offset_x, y + offset_y))
    
    def update(self, speed_mult=1.0):
        self.life -= speed_mult
        if self.life <= 0:
            self.start_x = random.randint(0, WIDTH)
            self.start_y = random.randint(0, HEIGHT)
            self.end_x = random.randint(0, WIDTH)
            self.end_y = random.randint(0, HEIGHT)
            self.generate_arc()
            self.life = random.randint(10, 30)
            self.max_life = self.life
    
    def draw(self, surf):
        if len(self.segments) > 1:
            alpha = int(255 * (self.life / self.max_life))
            # 先绘制辉光，再绘制主闪电（合并为一次循环）
            for i in range(len(self.segments) - 1):
                # 辉光
                pygame.draw.line(surf, (*self.color, min(100, alpha // 2)), 
                               self.segments[i], self.segments[i + 1], 6)
                # 主闪电
                pygame.draw.line(surf, (*self.color, min(255, alpha)), 
                               self.segments[i], self.segments[i + 1], 3)

class PowerCore:
    """能量核心"""
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.size = random.randint(30, 50)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(1, 3)
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.05, 0.1)
        self.color = (200, 50, 255)
        self.cached_rays = None
        self.last_size = None
    
    def update(self, speed_mult=1.0):
        self.rotation += self.rot_speed * speed_mult
        self.pulse += self.pulse_speed * speed_mult
    
    def draw(self, surf):
        scale = 0.85 + 0.15 * math.sin(self.pulse)
        size = int(self.size * scale)
        
        # 六边形核心
        points = []
        for i in range(6):
            angle = math.radians(60 * i + self.rotation)
            px = self.x + size * math.cos(angle)
            py = self.y + size * math.sin(angle)
            points.append((px, py))
        
        # 内部填充
        pygame.draw.polygon(surf, (100, 20, 150), points)
        # 边框
        pygame.draw.polygon(surf, self.color, points, 3)
        
        # 能量射线（使用局部Surface并缓存）
        if self.last_size != size:
            self.last_size = size
            ray_size = (size + 25) * 2
            self.cached_rays = pygame.Surface((ray_size, ray_size), pygame.SRCALPHA)
            center = ray_size // 2
            for i in range(6):
                angle = math.radians(60 * i)
                x1 = center + size * math.cos(angle)
                y1 = center + size * math.sin(angle)
                x2 = center + (size + 20) * math.cos(angle)
                y2 = center + (size + 20) * math.sin(angle)
                alpha = int(150 + 105 * math.sin(self.pulse + i))
                pygame.draw.line(self.cached_rays, (*self.color, alpha), (x1, y1), (x2, y2), 2)
        
        if self.cached_rays:
            ray_size = (size + 25) * 2
            # 旋转射线并绘制
            rotated = pygame.transform.rotate(self.cached_rays, -self.rotation)
            rect = rotated.get_rect(center=(self.x, self.y))
            surf.blit(rotated, rect)

class ClockGear:
    """时钟齿轮"""
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.radius = random.randint(20, 45)
        self.teeth = random.randint(12, 20)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-0.8, 0.8)
        if abs(self.rot_speed) < 0.2:
            self.rot_speed = 0.5
        self.color = (180, 150, 100)
        self.cached_gear = None
        self._build_gear()
    
    def _build_gear(self):
        size = int(self.radius * 2.5)
        self.cached_gear = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        # 绘制齿轮
        outer_points = []
        inner_points = []
        for i in range(self.teeth * 2):
            angle = math.radians(360 * i / (self.teeth * 2))
            if i % 2 == 0:
                r = self.radius
            else:
                r = self.radius * 0.85
            x = center + r * math.cos(angle)
            y = center + r * math.sin(angle)
            outer_points.append((x, y))
        
        # 内圈
        for i in range(12):
            angle = math.radians(30 * i)
            r = self.radius * 0.5
            x = center + r * math.cos(angle)
            y = center + r * math.sin(angle)
            inner_points.append((x, y))
        
        pygame.draw.polygon(self.cached_gear, self.color, outer_points)
        pygame.draw.polygon(self.cached_gear, (80, 70, 50), inner_points)
        pygame.draw.circle(self.cached_gear, (60, 50, 30), (center, center), int(self.radius * 0.2))
    
    def update(self, speed_mult=1.0):
        self.rotation += self.rot_speed * speed_mult
    
    def draw(self, surf):
        if self.cached_gear:
            rotated = pygame.transform.rotate(self.cached_gear, self.rotation)
            rect = rotated.get_rect(center=(self.x, self.y))
            surf.blit(rotated, rect)

class ClockHand:
    """时钟指针"""
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.length = random.randint(40, 80)
        self.angle = random.uniform(0, 360)
        self.speed = random.uniform(0.5, 2.0)
        self.width = random.randint(3, 6)
        self.color = (200, 170, 120)
    
    def update(self, speed_mult=1.0):
        self.angle += self.speed * speed_mult
    
    def draw(self, surf):
        rad = math.radians(self.angle)
        end_x = self.x + self.length * math.cos(rad)
        end_y = self.y + self.length * math.sin(rad)
        pygame.draw.line(surf, self.color, (self.x, self.y), (end_x, end_y), self.width)
        pygame.draw.circle(surf, (150, 130, 90), (int(self.x), int(self.y)), 8)

class RomanNumeral:
    """罗马数字"""
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.numeral = random.choice(['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'])
        self.alpha = random.randint(100, 200)
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.02, 0.05)
        self.color = (180, 160, 120)
        self.font_size = random.randint(24, 40)
    
    def update(self, speed_mult=1.0):
        self.pulse += self.pulse_speed * speed_mult
    
    def draw(self, surf):
        alpha = int(self.alpha * (0.8 + 0.2 * math.sin(self.pulse)))
        # 简化绘制：用矩形模拟罗马数字
        width = len(self.numeral) * 12
        num_surf = pygame.Surface((width, 30), pygame.SRCALPHA)
        for i, char in enumerate(self.numeral):
            x = i * 12
            if char == 'I':
                pygame.draw.rect(num_surf, (*self.color, alpha), (x + 4, 0, 4, 30))
            elif char in ['V', 'X']:
                pygame.draw.line(num_surf, (*self.color, alpha), (x, 0), (x + 8, 30), 4)
                pygame.draw.line(num_surf, (*self.color, alpha), (x + 8, 0), (x, 30), 4)
        surf.blit(num_surf, (self.x - width // 2, self.y - 15))

class Firefly:
    """萤火虫"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = random.uniform(-0.8, 0.8)
        self.brightness = random.uniform(0, 6.28)
        self.brightness_speed = random.uniform(0.15, 0.25)
        self.size = random.randint(3, 6)
        self.color = random.choice([(200, 255, 100), (255, 200, 100), (100, 255, 200)])
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.brightness += self.brightness_speed * speed_mult
        
        # 随机改变方向
        if random.random() < 0.02:
            self.vx = random.uniform(-0.8, 0.8)
            self.vy = random.uniform(-0.8, 0.8)
        
        if self.x < 0 or self.x > WIDTH:
            self.vx = -self.vx
        if self.y < 0 or self.y > HEIGHT:
            self.vy = -self.vy
    
    def draw(self, surf):
        alpha = int(200 * (0.5 + 0.5 * math.sin(self.brightness)))
        glow_size = self.size * 3
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, alpha // 3), (glow_size, glow_size), glow_size)
        surf.blit(glow_surf, (self.x - glow_size, self.y - glow_size))
        pygame.draw.circle(surf, (*self.color, alpha), (int(self.x), int(self.y)), self.size)

class MossClump:
    """苔藓丛"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT - random.randint(0, 60)
        self.width = random.randint(30, 60)
        self.height = random.randint(15, 30)
        self.sway = random.uniform(0, 6.28)
        self.sway_speed = random.uniform(0.02, 0.04)
        self.color = random.choice([(50, 150, 80), (40, 130, 70), (60, 140, 85)])
    
    def update(self, speed_mult=1.0):
        self.sway += self.sway_speed * speed_mult
    
    def draw(self, surf):
        offset = int(3 * math.sin(self.sway))
        # 绘制多个小椭圆模拟苔藓
        for i in range(5):
            x = self.x - self.width // 2 + i * (self.width // 5)
            y = self.y - random.randint(0, 5)
            w = self.width // 5 + 5
            h = self.height // 2 + random.randint(0, 5)
            pygame.draw.ellipse(surf, self.color, (x + offset, y, w, h))

class GlowSpore:
    """发光孢子"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vy = random.uniform(-0.3, -0.1)
        self.vx = random.uniform(-0.2, 0.2)
        self.size = random.randint(2, 5)
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.1, 0.2)
        self.color = random.choice([(150, 255, 150), (100, 255, 200), (200, 255, 150)])
    
    def update(self, speed_mult=1.0):
        self.y += self.vy * speed_mult
        self.x += self.vx * speed_mult
        self.pulse += self.pulse_speed * speed_mult
        
        if self.y < -10:
            self.y = HEIGHT + 10
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        alpha = int(180 * (0.6 + 0.4 * math.sin(self.pulse)))
        glow_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, alpha // 2), (self.size * 2, self.size * 2), self.size * 2)
        surf.blit(glow_surf, (self.x - self.size * 2, self.y - self.size * 2))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size)

class MusicNote:
    """音符"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = HEIGHT + random.randint(0, 100)
        self.vy = random.uniform(-1.5, -0.8)
        self.vx = random.uniform(-0.3, 0.3)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-3, 3)
        self.size = random.randint(15, 25)
        self.note_type = random.randint(0, 2)
        self.color = random.choice([(100, 200, 255), (255, 100, 200), (200, 255, 100)])
        self.alpha = 255
    
    def update(self, speed_mult=1.0):
        self.y += self.vy * speed_mult
        self.x += self.vx * speed_mult
        self.rotation += self.rot_speed * speed_mult
        
        if self.y < -50:
            self.y = HEIGHT + random.randint(0, 50)
            self.x = random.randint(0, WIDTH)
            self.alpha = 255
        
        # 渐隐效果
        if self.y < 100:
            self.alpha = int(255 * (self.y / 100))
    
    def draw(self, surf):
        note_surf = pygame.Surface((self.size * 2, self.size * 3), pygame.SRCALPHA)
        # 音符头
        pygame.draw.circle(note_surf, (*self.color, self.alpha), (self.size // 2, self.size * 2), self.size // 2)
        # 音符杆
        pygame.draw.line(note_surf, (*self.color, self.alpha), 
                        (self.size - 2, self.size * 2), (self.size - 2, self.size // 2), 3)
        # 音符旗
        if self.note_type == 0:
            pygame.draw.line(note_surf, (*self.color, self.alpha), 
                           (self.size - 2, self.size // 2), (self.size + 8, self.size), 3)
        elif self.note_type == 1:
            for i in range(2):
                pygame.draw.line(note_surf, (*self.color, self.alpha), 
                               (self.size - 2, self.size // 2 + i * 6), 
                               (self.size + 8, self.size + i * 6), 3)
        
        rotated = pygame.transform.rotate(note_surf, self.rotation)
        rect = rotated.get_rect(center=(self.x, self.y))
        surf.blit(rotated, rect)

class SoundWave:
    """声波"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = 0
        self.max_radius = random.randint(80, 150)
        self.speed = random.uniform(2, 3.5)
        self.color = random.choice([(150, 100, 255), (100, 255, 150), (255, 150, 100)])
        self.frequency = random.randint(4, 8)
    
    def update(self, speed_mult=1.0):
        self.radius += self.speed * speed_mult
        if self.radius > self.max_radius:
            self.radius = 0
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)
    
    def draw(self, surf):
        if self.radius < self.max_radius:
            alpha = int(200 * (1 - self.radius / self.max_radius))
            # 波纹状声波
            points = []
            for angle in range(0, 360, 10):
                rad = math.radians(angle)
                wave = math.sin(angle * self.frequency / 60) * 5
                r = self.radius + wave
                x = self.x + r * math.cos(rad)
                y = self.y + r * math.sin(rad)
                points.append((x, y))
            
            if len(points) > 2:
                wave_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(wave_surf, (*self.color, alpha), points, 3)
                surf.blit(wave_surf, (0, 0))

class Equalizer:
    """频谱柱"""
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.base_y = HEIGHT - 30
        self.width = random.randint(15, 25)
        self.target_height = random.randint(30, 120)
        self.current_height = 0
        self.speed = random.uniform(3, 6)
        self.color = random.choice([(255, 100, 150), (100, 255, 200), (255, 200, 100)])
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.1, 0.2)
    
    def update(self, speed_mult=1.0):
        self.pulse += self.pulse_speed * speed_mult
        
        # 随机变化目标高度
        if random.random() < 0.03:
            self.target_height = random.randint(30, 120)
        
        # 平滑过渡
        if self.current_height < self.target_height:
            self.current_height += self.speed * speed_mult
        elif self.current_height > self.target_height:
            self.current_height -= self.speed * speed_mult
    
    def draw(self, surf):
        height = int(self.current_height * (0.9 + 0.1 * math.sin(self.pulse)))
        # 渐变效果
        for i in range(int(height)):
            alpha = int(255 * (1 - i / (height + 1)))
            y = self.base_y - i
            color = tuple(min(255, c + 30) for c in self.color)
            pygame.draw.line(surf, (*color, alpha), 
                           (self.x, y), (self.x + self.width, y), 1)

class Torii:
    """鸟居"""
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.width = random.randint(80, 120)
        self.height = random.randint(100, 140)
        self.alpha = random.randint(120, 200)
        self.fade = random.uniform(0, 6.28)
        self.fade_speed = random.uniform(0.01, 0.03)
        self.color = (200, 50, 50)
    
    def update(self, speed_mult=1.0):
        self.fade += self.fade_speed * speed_mult
    
    def draw(self, surf):
        alpha = int(self.alpha * (0.8 + 0.2 * math.sin(self.fade)))
        # 上横梁（带翘起）
        top_y = self.y - self.height // 2
        points = [
            (self.x - self.width // 2 - 10, top_y),
            (self.x - self.width // 2, top_y - 8),
            (self.x, top_y - 10),
            (self.x + self.width // 2, top_y - 8),
            (self.x + self.width // 2 + 10, top_y)
        ]
        for i in range(len(points) - 1):
            pygame.draw.line(surf, (*self.color, alpha), points[i], points[i + 1], 8)
        
        # 下横梁
        mid_y = self.y
        pygame.draw.line(surf, (*self.color, alpha), 
                        (self.x - self.width // 2, mid_y), 
                        (self.x + self.width // 2, mid_y), 6)
        
        # 两根立柱
        pygame.draw.line(surf, (*self.color, alpha), 
                        (self.x - self.width // 3, top_y - 5), 
                        (self.x - self.width // 3, self.y + self.height // 2), 10)
        pygame.draw.line(surf, (*self.color, alpha), 
                        (self.x + self.width // 3, top_y - 5), 
                        (self.x + self.width // 3, self.y + self.height // 2), 10)

class PaperCharm:
    """纸符咒"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-100, HEIGHT)
        self.width = random.randint(20, 30)
        self.height = random.randint(60, 90)
        self.sway = random.uniform(0, 6.28)
        self.sway_speed = random.uniform(0.08, 0.15)
        self.vy = random.uniform(0.3, 0.8)
        self.color = (250, 240, 220)
    
    def update(self, speed_mult=1.0):
        self.y += self.vy * speed_mult
        self.sway += self.sway_speed * speed_mult
        if self.y > HEIGHT + 100:
            self.y = -100
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        offset = int(15 * math.sin(self.sway))
        # 纸符主体
        points = [
            (self.x + offset, self.y),
            (self.x + self.width + offset, self.y),
            (self.x + self.width + offset // 2, self.y + self.height),
            (self.x + offset // 2, self.y + self.height)
        ]
        pygame.draw.polygon(surf, self.color, points)
        pygame.draw.polygon(surf, (200, 180, 160), points, 2)
        # 符文线条
        for i in range(4):
            y = self.y + 15 + i * 15
            pygame.draw.line(surf, (180, 60, 60), 
                           (self.x + 5 + offset, y), 
                           (self.x + self.width - 5 + offset, y), 2)

class ShrineLight:
    """神社光晕"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = 0
        self.max_radius = random.randint(60, 100)
        self.speed = random.uniform(0.8, 1.5)
        self.color = (255, 200, 100)
        self.alpha_base = random.randint(80, 150)
    
    def update(self, speed_mult=1.0):
        self.radius += self.speed * speed_mult
        if self.radius > self.max_radius:
            self.radius = 0
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)
    
    def draw(self, surf):
        if self.radius < self.max_radius:
            alpha = int(self.alpha_base * (1 - self.radius / self.max_radius))
            glow_surf = pygame.Surface((int(self.radius * 2 + 10), int(self.radius * 2 + 10)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, alpha), 
                             (int(self.radius) + 5, int(self.radius) + 5), int(self.radius), 2)
            surf.blit(glow_surf, (self.x - self.radius - 5, self.y - self.radius - 5))

class TeaCup:
    """茶杯"""
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.size = random.randint(30, 50)
        self.steam_particles = []
        for _ in range(5):
            self.steam_particles.append({
                'offset_x': random.uniform(-5, 5),
                'y_offset': 0,
                'alpha': random.randint(100, 200),
                'speed': random.uniform(0.5, 1.2)
            })
        self.color = random.choice([(180, 220, 255), (255, 200, 180), (200, 255, 200)])
    
    def update(self, speed_mult=1.0):
        for particle in self.steam_particles:
            particle['y_offset'] -= particle['speed'] * speed_mult
            particle['alpha'] = max(0, particle['alpha'] - 1 * speed_mult)
            if particle['y_offset'] < -50 or particle['alpha'] <= 0:
                particle['y_offset'] = 0
                particle['alpha'] = random.randint(100, 200)
                particle['offset_x'] = random.uniform(-5, 5)
    
    def draw(self, surf):
        # 茶杯
        cup_rect = (self.x - self.size // 2, self.y, self.size, self.size // 2)
        pygame.draw.ellipse(surf, self.color, cup_rect)
        pygame.draw.ellipse(surf, (150, 150, 150), cup_rect, 2)
        # 杯把
        handle_rect = (self.x + self.size // 2 - 5, self.y + 5, 15, 20)
        pygame.draw.ellipse(surf, self.color, handle_rect, 3)
        
        # 蒸汽
        for particle in self.steam_particles:
            if particle['alpha'] > 0:
                px = self.x + particle['offset_x']
                py = self.y - 5 + particle['y_offset']
                alpha = int(particle['alpha'])
                glow_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (200, 200, 220, alpha), (6, 6), 6)
                surf.blit(glow_surf, (px - 6, py - 6))

class Pastry:
    """点心"""
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.size = random.randint(25, 40)
        self.rotation = random.uniform(0, 360)
        self.float_offset = random.uniform(0, 6.28)
        self.float_speed = random.uniform(0.03, 0.06)
        self.pastry_type = random.randint(0, 2)
        self.colors = [
            (255, 220, 180),  # 饼干色
            (255, 200, 200),  # 草莓色
            (200, 255, 200)   # 抹茶色
        ]
        self.color = self.colors[self.pastry_type]
    
    def update(self, speed_mult=1.0):
        self.float_offset += self.float_speed * speed_mult
    
    def draw(self, surf):
        float_y = self.y + 5 * math.sin(self.float_offset)
        
        if self.pastry_type == 0:  # 圆形饼干
            pygame.draw.circle(surf, self.color, (int(self.x), int(float_y)), self.size // 2)
            pygame.draw.circle(surf, (200, 180, 150), (int(self.x), int(float_y)), self.size // 2, 2)
            # 装饰点
            for angle in range(0, 360, 60):
                rad = math.radians(angle)
                px = self.x + (self.size // 3) * math.cos(rad)
                py = float_y + (self.size // 3) * math.sin(rad)
                pygame.draw.circle(surf, (180, 150, 120), (int(px), int(py)), 3)
        
        elif self.pastry_type == 1:  # 方形蛋糕
            rect = (self.x - self.size // 2, float_y - self.size // 2, self.size, self.size)
            pygame.draw.rect(surf, self.color, rect)
            pygame.draw.rect(surf, (255, 150, 150), rect, 2)
            # 奶油装饰
            pygame.draw.line(surf, (255, 255, 255), 
                           (self.x - self.size // 3, float_y), 
                           (self.x + self.size // 3, float_y), 3)
        
        else:  # 三角形点心
            points = []
            for i in range(3):
                angle = math.radians(120 * i + self.rotation)
                px = self.x + self.size // 2 * math.cos(angle)
                py = float_y + self.size // 2 * math.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(surf, self.color, points)
            pygame.draw.polygon(surf, (150, 200, 150), points, 2)

class TableCloth:
    """桌布图案"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(30, 50)
        self.pattern_type = random.randint(0, 2)
        self.alpha = random.randint(80, 150)
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.02, 0.04)
        self.color = random.choice([(200, 150, 150), (150, 200, 200), (200, 200, 150)])
    
    def update(self, speed_mult=1.0):
        self.pulse += self.pulse_speed * speed_mult
    
    def draw(self, surf):
        alpha = int(self.alpha * (0.7 + 0.3 * math.sin(self.pulse)))
        
        if self.pattern_type == 0:  # 花朵图案
            # 中心
            pygame.draw.circle(surf, (*self.color, alpha), (int(self.x), int(self.y)), 5)
            # 花瓣
            for angle in range(0, 360, 60):
                rad = math.radians(angle)
                px = self.x + self.size // 2 * math.cos(rad)
                py = self.y + self.size // 2 * math.sin(rad)
                pygame.draw.circle(surf, (*self.color, alpha), (int(px), int(py)), 8)
        
        elif self.pattern_type == 1:  # 格子图案
            for i in range(-1, 2):
                for j in range(-1, 2):
                    x = self.x + i * 15
                    y = self.y + j * 15
                    pygame.draw.rect(surf, (*self.color, alpha), (x - 5, y - 5, 10, 10), 1)
        
        else:  # 波点图案
            for i in range(4):
                angle = random.uniform(0, 6.28)
                r = random.randint(10, self.size // 2)
                px = self.x + r * math.cos(angle)
                py = self.y + r * math.sin(angle)
                pygame.draw.circle(surf, (*self.color, alpha), (int(px), int(py)), 4)

class BronzeCoin:
    """青铜钱币"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vy = random.uniform(0.3, 0.8)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-4, 4)
        self.size = random.randint(20, 35)
        self.shimmer = random.uniform(0, 6.28)
        self.shimmer_speed = random.uniform(0.05, 0.1)
        self.coin_type = random.randint(0, 2)
    
    def update(self, speed_mult=1.0):
        self.y += self.vy * speed_mult
        self.rotation += self.rot_speed * speed_mult
        self.shimmer += self.shimmer_speed * speed_mult
        
        if self.y > HEIGHT + 50:
            self.y = -50
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        # 青铜钱币
        coin_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        center = self.size
        
        # 钱币本体（青铜色）
        shimmer_value = int(30 * math.sin(self.shimmer))
        color = (180 + shimmer_value, 120 + shimmer_value, 80)
        pygame.draw.circle(coin_surf, color, (center, center), self.size - 2)
        pygame.draw.circle(coin_surf, (140, 90, 60), (center, center), self.size - 2, 2)
        
        # 方孔
        hole_size = self.size // 3
        pygame.draw.rect(coin_surf, (0, 0, 0, 0), 
                        (center - hole_size // 2, center - hole_size // 2, hole_size, hole_size))
        
        # 古代文字装饰（简化的线条）
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle)
            x = center + (self.size - 8) * math.cos(rad)
            y = center + (self.size - 8) * math.sin(rad)
            pygame.draw.circle(coin_surf, (100, 70, 50), (int(x), int(y)), 3)
        
        rotated = pygame.transform.rotate(coin_surf, self.rotation)
        rect = rotated.get_rect(center=(self.x, self.y))
        surf.blit(rotated, rect)

class AncientSeal:
    """古代印章"""
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.size = random.randint(30, 50)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(0.2, 0.5)
        self.glow = random.uniform(0, 6.28)
        self.glow_speed = random.uniform(0.03, 0.06)
        self.color = random.choice([(200, 80, 60), (180, 90, 70), (220, 100, 70)])
    
    def update(self, speed_mult=1.0):
        self.rotation += self.rot_speed * speed_mult
        self.glow += self.glow_speed * speed_mult
    
    def draw(self, surf):
        alpha = int(180 + 75 * math.sin(self.glow))
        
        # 印章外框（六边形）
        points = []
        for i in range(6):
            angle = math.radians(60 * i + self.rotation)
            px = self.x + self.size * math.cos(angle)
            py = self.y + self.size * math.sin(angle)
            points.append((px, py))
        
        pygame.draw.polygon(surf, (*self.color, alpha), points, 3)
        
        # 内部纹路（十字纹）
        pygame.draw.line(surf, (*self.color, alpha), 
                        (self.x - self.size // 2, self.y), 
                        (self.x + self.size // 2, self.y), 2)
        pygame.draw.line(surf, (*self.color, alpha), 
                        (self.x, self.y - self.size // 2), 
                        (self.x, self.y + self.size // 2), 2)
        
        # 中心圆
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size // 4)

class VerdigrisSpot:
    """铜锈斑点"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(5, 15)
        self.growth = 0
        self.max_growth = random.randint(10, 20)
        self.grow_speed = random.uniform(0.1, 0.3)
        self.fade = random.uniform(0, 6.28)
        self.fade_speed = random.uniform(0.02, 0.04)
    
    def update(self, speed_mult=1.0):
        if self.growth < self.max_growth:
            self.growth += self.grow_speed * speed_mult
        self.fade += self.fade_speed * speed_mult
    
    def draw(self, surf):
        progress = min(1, self.growth / self.max_growth)
        current_size = int(self.size * progress)
        alpha = int(150 * (0.7 + 0.3 * math.sin(self.fade)))
        
        # 铜绿色斑点
        for i in range(3):
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-3, 3)
            pygame.draw.circle(surf, (100, 180, 150, alpha), 
                             (int(self.x + offset_x), int(self.y + offset_y)), 
                             current_size - i * 2)

class ClayPot:
    """陶器"""
    def __init__(self):
        self.x = random.randint(80, WIDTH - 80)
        self.y = HEIGHT - random.randint(60, 100)
        self.width = random.randint(40, 60)
        self.height = random.randint(50, 80)
        self.rotation = random.uniform(-15, 15)
        self.shimmer = random.uniform(0, 6.28)
        self.shimmer_speed = random.uniform(0.02, 0.04)
        self.pot_type = random.randint(0, 2)
        self.color = random.choice([(180, 100, 70), (200, 120, 80), (160, 90, 65)])
    
    def update(self, speed_mult=1.0):
        self.shimmer += self.shimmer_speed * speed_mult
    
    def draw(self, surf):
        shimmer_value = int(20 * math.sin(self.shimmer))
        color = (self.color[0] + shimmer_value, self.color[1] + shimmer_value, self.color[2])
        
        if self.pot_type == 0:  # 瓶子
            # 瓶口
            pygame.draw.rect(surf, color, 
                           (self.x - self.width // 4, self.y - self.height, 
                            self.width // 2, self.height // 4))
            # 瓶身
            pygame.draw.ellipse(surf, color, 
                              (self.x - self.width // 2, self.y - self.height * 0.7, 
                               self.width, self.height * 0.7))
        elif self.pot_type == 1:  # 罐子
            pygame.draw.ellipse(surf, color, 
                              (self.x - self.width // 2, self.y - self.height, 
                               self.width, self.height))
        else:  # 盘子
            pygame.draw.ellipse(surf, color, 
                              (self.x - self.width // 2, self.y - self.height // 3, 
                               self.width, self.height // 3))
        
        # 陶器纹路
        for i in range(3):
            y = self.y - self.height + i * (self.height // 4)
            pygame.draw.line(surf, (self.color[0] - 30, self.color[1] - 30, self.color[2] - 20),
                           (self.x - self.width // 3, y), 
                           (self.x + self.width // 3, y), 2)

class PotteryWheel:
    """陶轮"""
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.radius = random.randint(30, 50)
        self.rotation = 0
        self.rot_speed = random.uniform(3, 6)
        self.clay_height = 0
        self.growing = True
        self.grow_speed = random.uniform(0.5, 1.0)
        self.max_height = random.randint(30, 60)
    
    def update(self, speed_mult=1.0):
        self.rotation += self.rot_speed * speed_mult
        
        if self.growing:
            self.clay_height += self.grow_speed * speed_mult
            if self.clay_height >= self.max_height:
                self.growing = False
        else:
            self.clay_height -= self.grow_speed * speed_mult * 0.5
            if self.clay_height <= 0:
                self.growing = True
                self.max_height = random.randint(30, 60)
    
    def draw(self, surf):
        # 陶轮基座
        pygame.draw.circle(surf, (120, 80, 60), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, (100, 70, 50), (int(self.x), int(self.y)), self.radius, 3)
        
        # 旋转线条（显示转动）
        for i in range(4):
            angle = math.radians(self.rotation + i * 90)
            x = self.x + self.radius * 0.7 * math.cos(angle)
            y = self.y + self.radius * 0.7 * math.sin(angle)
            pygame.draw.line(surf, (80, 60, 45), (self.x, self.y), (x, y), 2)
        
        # 成型中的陶土
        if self.clay_height > 0:
            clay_width = int(self.radius * 0.6)
            pygame.draw.ellipse(surf, (200, 120, 80), 
                              (self.x - clay_width, 
                               self.y - self.clay_height - 10, 
                               clay_width * 2, 20))
            pygame.draw.rect(surf, (180, 110, 70), 
                           (self.x - clay_width // 2, 
                            self.y - self.clay_height, 
                            clay_width, int(self.clay_height)))

class ClayRipple:
    """陶土波纹"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = 0
        self.max_radius = random.randint(50, 100)
        self.speed = random.uniform(1.0, 2.0)
        self.color = random.choice([(200, 140, 100), (220, 160, 120), (180, 120, 90)])
    
    def update(self, speed_mult=1.0):
        self.radius += self.speed * speed_mult
        if self.radius > self.max_radius:
            self.radius = 0
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)
    
    def draw(self, surf):
        if self.radius < self.max_radius:
            alpha = int(120 * (1 - self.radius / self.max_radius))
            for i in range(2):
                r = self.radius - i * 10
                if r > 0:
                    ring_surf = pygame.Surface((int(r * 2 + 10), int(r * 2 + 10)), pygame.SRCALPHA)
                    pygame.draw.circle(ring_surf, (*self.color, alpha // (i + 1)), 
                                     (int(r) + 5, int(r) + 5), int(r), 2)
                    surf.blit(ring_surf, (self.x - r - 5, self.y - r - 5))

class AmberGem:
    """琥珀宝石"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.3, 0.3)
        self.size = random.randint(15, 30)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-1, 1)
        self.glow = random.uniform(0, 6.28)
        self.glow_speed = random.uniform(0.05, 0.1)
        self.color = random.choice([(255, 180, 80), (255, 160, 60), (255, 200, 100)])
        # 内部的"古代生物"
        self.insect_type = random.randint(0, 2)
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.rotation += self.rot_speed * speed_mult
        self.glow += self.glow_speed * speed_mult
        
        if self.x < 0 or self.x > WIDTH:
            self.vx = -self.vx
        if self.y < 0 or self.y > HEIGHT:
            self.vy = -self.vy
    
    def draw(self, surf):
        glow_value = int(30 * math.sin(self.glow))
        color = (self.color[0], self.color[1] + glow_value, self.color[2])
        
        # 琥珀外形（不规则多边形）
        points = []
        for i in range(6):
            angle = math.radians(60 * i + self.rotation)
            r = self.size * random.uniform(0.8, 1.0)
            px = self.x + r * math.cos(angle)
            py = self.y + r * math.sin(angle)
            points.append((px, py))
        
        # 半透明效果
        pygame.draw.polygon(surf, color, points)
        pygame.draw.polygon(surf, (self.color[0] - 50, self.color[1] - 50, self.color[2] - 50), points, 2)
        
        # 内部"古代生物"形状
        if self.insect_type == 0:  # 虫子
            pygame.draw.line(surf, (100, 70, 40), 
                           (self.x - self.size // 3, self.y), 
                           (self.x + self.size // 3, self.y), 2)
            for i in range(3):
                x = self.x - self.size // 3 + i * (self.size // 3)
                pygame.draw.circle(surf, (80, 60, 30), (int(x), int(self.y)), 3)
        elif self.insect_type == 1:  # 叶子
            pygame.draw.ellipse(surf, (100, 80, 50), 
                              (self.x - self.size // 4, self.y - self.size // 3, 
                               self.size // 2, self.size * 2 // 3))
        else:  # 气泡
            for i in range(4):
                offset_x = random.randint(-self.size // 4, self.size // 4)
                offset_y = random.randint(-self.size // 4, self.size // 4)
                r = random.randint(2, 5)
                pygame.draw.circle(surf, (200, 150, 80), 
                                 (int(self.x + offset_x), int(self.y + offset_y)), r, 1)

class ResinDrop:
    """树脂滴"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = -random.randint(10, 50)
        self.vy = random.uniform(0.5, 1.2)
        self.length = random.randint(20, 40)
        self.wobble = random.uniform(0, 6.28)
        self.wobble_speed = random.uniform(0.08, 0.15)
        self.color = random.choice([(220, 160, 80), (240, 180, 100), (200, 140, 70)])
    
    def update(self, speed_mult=1.0):
        self.y += self.vy * speed_mult
        self.wobble += self.wobble_speed * speed_mult
        
        if self.y > HEIGHT + 50:
            self.y = -50
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surf):
        wobble_x = int(5 * math.sin(self.wobble))
        
        # 树脂滴形状
        points = [
            (self.x + wobble_x, self.y),
            (self.x - 8 + wobble_x, self.y + self.length // 3),
            (self.x + wobble_x, self.y + self.length),
            (self.x + 8 + wobble_x, self.y + self.length // 3)
        ]
        pygame.draw.polygon(surf, self.color, points)
        # 高光
        pygame.draw.line(surf, (255, 220, 150), 
                        (self.x + wobble_x - 3, self.y + 5), 
                        (self.x + wobble_x - 3, self.y + self.length // 2), 2)

class AncientTentacle:
    """古老触须"""
    def __init__(self):
        self.base_x = random.randint(0, WIDTH)
        self.base_y = HEIGHT
        self.segments = []
        self.segment_count = random.randint(8, 15)
        self.segment_length = random.randint(15, 25)
        
        # 生成触须节点
        x, y = self.base_x, self.base_y
        for i in range(self.segment_count):
            x += random.uniform(-5, 5)
            y -= self.segment_length
            self.segments.append({'x': x, 'y': y, 'sway': random.uniform(0, 6.28)})
        
        self.sway_speed = random.uniform(0.03, 0.06)
        self.color = random.choice([(150, 100, 60), (180, 120, 70), (140, 90, 55)])
    
    def update(self, speed_mult=1.0):
        for i, seg in enumerate(self.segments):
            seg['sway'] += self.sway_speed * speed_mult
            # 每个节点随波动移动
            offset = math.sin(seg['sway']) * (i + 1) * 2
            seg['current_x'] = seg['x'] + offset
    
    def draw(self, surf):
        # 绘制触须
        if len(self.segments) > 1:
            points = [(self.base_x, self.base_y)]
            for seg in self.segments:
                points.append((seg['current_x'] if 'current_x' in seg else seg['x'], seg['y']))
            
            # 绘制触须主体（渐变变细）
            for i in range(len(points) - 1):
                width = max(2, int(8 * (1 - i / len(points))))
                pygame.draw.line(surf, self.color, points[i], points[i + 1], width)
            
            # 绘制吸盘
            for i in range(0, len(self.segments), 2):
                seg = self.segments[i]
                x = seg['current_x'] if 'current_x' in seg else seg['x']
                y = seg['y']
                r = random.randint(3, 6)
                pygame.draw.circle(surf, (self.color[0] - 30, self.color[1] - 30, self.color[2] - 30), 
                                 (int(x), int(y)), r)

class TechCube:
    """科技立方体"""
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.size = random.randint(30, 60)
        self.rotation_x = random.uniform(0, 360)
        self.rotation_y = random.uniform(0, 360)
        self.rot_speed_x = random.uniform(0.5, 1.5)
        self.rot_speed_y = random.uniform(0.5, 1.5)
        self.pulse = random.uniform(0, 6.28)
        self.pulse_speed = random.uniform(0.05, 0.1)
        self.color = random.choice([(0, 255, 200), (200, 0, 255), (255, 200, 0)])
    
    def update(self, speed_mult=1.0):
        self.rotation_x += self.rot_speed_x * speed_mult
        self.rotation_y += self.rot_speed_y * speed_mult
        self.pulse += self.pulse_speed * speed_mult
    
    def draw(self, surf):
        # 简化的3D立方体投影
        scale = 0.9 + 0.1 * math.sin(self.pulse)
        s = int(self.size * scale)
        
        # 计算立方体顶点（简化的伪3D）
        offset = s // 3
        rad_x = math.radians(self.rotation_x)
        rad_y = math.radians(self.rotation_y)
        
        # 前面
        front = [
            (self.x - s // 2, self.y - s // 2),
            (self.x + s // 2, self.y - s // 2),
            (self.x + s // 2, self.y + s // 2),
            (self.x - s // 2, self.y + s // 2)
        ]
        
        # 后面（带偏移产生3D效果）
        back = [
            (self.x - s // 2 + offset, self.y - s // 2 - offset),
            (self.x + s // 2 + offset, self.y - s // 2 - offset),
            (self.x + s // 2 + offset, self.y + s // 2 - offset),
            (self.x - s // 2 + offset, self.y + s // 2 - offset)
        ]
        
        alpha = int(150 + 105 * math.sin(self.pulse))
        
        # 绘制边框
        pygame.draw.lines(surf, (*self.color, alpha), True, front, 2)
        pygame.draw.lines(surf, (*self.color, alpha // 2), True, back, 2)
        # 连接线
        for i in range(4):
            pygame.draw.line(surf, (*self.color, alpha // 3), front[i], back[i], 1)

class CircuitLine:
    """电路线"""
    def __init__(self):
        self.points = []
        start_x = random.randint(0, WIDTH)
        start_y = random.randint(0, HEIGHT)
        x, y = start_x, start_y
        
        # 生成直角电路路径
        for _ in range(random.randint(3, 6)):
            if random.random() < 0.5:
                x += random.randint(-100, 100)
            else:
                y += random.randint(-100, 100)
            x = max(0, min(WIDTH, x))
            y = max(0, min(HEIGHT, y))
            self.points.append((x, y))
        
        self.flow_pos = 0
        self.flow_speed = random.uniform(2, 4)
        self.color = random.choice([(0, 255, 150), (0, 150, 255), (255, 150, 0)])
    
    def update(self, speed_mult=1.0):
        self.flow_pos += self.flow_speed * speed_mult
        if self.flow_pos > len(self.points) * 30:
            self.flow_pos = 0
    
    def draw(self, surf):
        if len(self.points) > 1:
            # 绘制电路线
            pygame.draw.lines(surf, (*self.color, 100), False, self.points, 2)
            
            # 绘制流动的能量点
            total_len = 0
            segment_lens = []
            for i in range(len(self.points) - 1):
                dx = self.points[i + 1][0] - self.points[i][0]
                dy = self.points[i + 1][1] - self.points[i][1]
                length = math.sqrt(dx * dx + dy * dy)
                segment_lens.append(length)
                total_len += length
            
            if total_len > 0:
                current_len = self.flow_pos % total_len
                accumulated = 0
                for i, seg_len in enumerate(segment_lens):
                    if accumulated + seg_len >= current_len:
                        t = (current_len - accumulated) / seg_len
                        x = self.points[i][0] + t * (self.points[i + 1][0] - self.points[i][0])
                        y = self.points[i][1] + t * (self.points[i + 1][1] - self.points[i][1])
                        pygame.draw.circle(surf, self.color, (int(x), int(y)), 5)
                        break
                    accumulated += seg_len

class HologramShard:
    """全息碎片"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.size = random.randint(20, 40)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2, 2)
        self.glitch = random.uniform(0, 6.28)
        self.glitch_speed = random.uniform(0.1, 0.2)
        self.color = random.choice([(0, 255, 200), (255, 0, 200), (255, 200, 0)])
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.rotation += self.rot_speed * speed_mult
        self.glitch += self.glitch_speed * speed_mult
        
        if self.x < -50 or self.x > WIDTH + 50:
            self.vx = -self.vx
        if self.y < -50 or self.y > HEIGHT + 50:
            self.vy = -self.vy
    
    def draw(self, surf):
        # 故障效果
        offset = int(5 * math.sin(self.glitch * 3))
        alpha = int(150 + 105 * math.sin(self.glitch))
        
        # 绘制三角形碎片
        points = []
        for i in range(3):
            angle = math.radians(120 * i + self.rotation)
            px = self.x + self.size * math.cos(angle) + offset
            py = self.y + self.size * math.sin(angle)
            points.append((px, py))
        
        # 主碎片
        pygame.draw.polygon(surf, (*self.color, alpha), points)
        # 故障副本
        points_glitch = [(p[0] + offset * 2, p[1]) for p in points]
        pygame.draw.polygon(surf, (*self.color, alpha // 3), points_glitch, 2)

class SkyShard:
    """天空碎片"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(30, 80)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.3, 0.3)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-1, 1)
        self.color = (100, 20, 30)
    
    def update(self, speed_mult=1.0):
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.rotation += self.rot_speed
        if self.x < -self.size: self.x = WIDTH + self.size
        if self.x > WIDTH + self.size: self.x = -self.size
        if self.y < -self.size: self.y = HEIGHT + self.size
        if self.y > HEIGHT + self.size: self.y = -self.size
    
    def draw(self, surf):
        points = []
        for i in range(6):
            angle = math.radians(i * 60 + self.rotation)
            r = self.size * (0.8 if i % 2 == 0 else 0.5)
            points.append((self.x + r * math.cos(angle), self.y + r * math.sin(angle)))
        pygame.draw.polygon(surf, self.color, points)
        pygame.draw.polygon(surf, (150, 50, 80), points, 2)

class BackgroundManager:
    """全新背景系统 - 8种独特场景"""
    
    # 背景风格定义
    BG_STYLES = {
        "classic": {
            "name": "经典深空",
            "base_color": [10, 10, 18],
            "elements": {"stars": 200, "nebulae": 6},
            "grid_color": None,
            "element_type": "classic",
            "bgm": "normal"
        },
        "dawn_clouds": {
            "name": "晨曦云海",
            "base_color": [255, 180, 150],
            "elements": {"clouds": 15, "light_rays": 4, "stars": 50},
            "grid_color": None,
            "element_type": "dawn",
            "bgm": "ambient"
        },
        "thunderstorm": {
            "name": "雷暴云团",
            "base_color": [30, 35, 45],
            "elements": {"rain": 200, "lightning": 3, "clouds": 8},
            "grid_color": None,
            "element_type": "storm",
            "bgm": "intense"
        },
        "city_sky": {
            "name": "城市上空",
            "base_color": [40, 20, 60],
            "elements": {"buildings": 12, "stars": 100},
            "grid_color": None,
            "element_type": "urban",
            "bgm": "synthwave"
        },
        "aurora": {
            "name": "极光彩幕",
            "base_color": [5, 10, 15],
            "elements": {"aurora_waves": 4, "stars": 300},
            "grid_color": None,
            "element_type": "aurora",
            "bgm": "trance"
        },
        "deep_ocean": {
            "name": "深海裂谷",
            "base_color": [0, 20, 40],
            "elements": {"bubbles": 40, "stars": 80},
            "grid_color": None,
            "element_type": "ocean",
            "bgm": "mystery"
        },
        "space_battle": {
            "name": "太空战场",
            "base_color": [5, 5, 10],
            "elements": {"asteroids": 20, "stars": 400, "nebulae": 3},
            "grid_color": None,
            "element_type": "space",
            "bgm": "orchestra"
        },
        "volcano": {
            "name": "火山烟霾",
            "base_color": [40, 20, 10],
            "elements": {"volcano_smoke": 25, "embers": 60},
            "grid_color": None,
            "element_type": "volcano",
            "bgm": "metal"
        },
        "matrix": {
            "name": "数字矩阵",
            "base_color": [0, 8, 0],
            "elements": {"matrix_rain": 18, "hexagons": 12},
            "grid_color": (0, 255, 0),
            "element_type": "cyber",
            "bgm": "electronic"
        },
        "autumn_forest": {
            "name": "秋日枫林",
            "base_color": [80, 40, 20],  # 深棕基调
            "elements": {"maple_leaves": 80, "trees": 8},
            "grid_color": None,
            "element_type": "autumn",
            "gradient": [(60, 30, 15), (200, 100, 30), (255, 180, 50)],
            "bgm": "piano"
        },
        "salt_lake": {
            "name": "镜面盐湖",
            "base_color": [200, 220, 240],
            "elements": {"salt_crystals": 60, "salt_waves": 12, "stars": 30},
            "grid_color": None,
            "element_type": "salt",
            "gradient": [(180, 200, 255), (255, 200, 220), (200, 255, 240)],
            "bgm": "lofi"
        },
        "war_ruins": {
            "name": "战争废墟",
            "base_color": [50, 45, 50],
            "elements": {"debris": 30, "smoke": 20, "embers": 40},
            "grid_color": None,
            "element_type": "ruins",
            "gradient": [(80, 80, 90), (120, 80, 60), (60, 50, 45)],
            "bgm": "industrial"
        },
        "crystal_cave": {
            "name": "水晶洞穴",
            "base_color": [15, 5, 20],
            "elements": {"crystals_top": 12, "crystals_bottom": 12, "stars": 100},
            "grid_color": None,
            "element_type": "crystal",
            "gradient": [(25, 10, 35), (40, 20, 50), (30, 15, 40)],
            "bgm": "ethereal"
        },
        "candle_library": {
            "name": "烛火图书馆",
            "base_color": [15, 10, 5],
            "elements": {"candles": 15, "book_pages": 8, "quills": 5},
            "grid_color": None,
            "element_type": "library",
            "gradient": [(30, 20, 10), (50, 35, 20), (40, 25, 15)],
            "bgm": "calm"
        },
        "orbital_station": {
            "name": "轨道空间站",
            "base_color": [5, 10, 20],
            "elements": {"satellites": 6, "signal_waves": 12, "data_streams": 20, "stars": 150},
            "grid_color": (50, 100, 150),
            "element_type": "space_tech",
            "gradient": [(10, 20, 40), (30, 60, 100), (20, 40, 70)],
            "bgm": "chiptune"
        },
        "energy_matrix": {
            "name": "能量矩阵",
            "base_color": [10, 0, 20],
            "elements": {"energy_nodes": 12, "lightning_arcs": 8, "power_cores": 6},
            "grid_color": (150, 50, 255),
            "element_type": "energy",
            "gradient": [(20, 0, 40), (80, 20, 120), (150, 50, 200)],
            "bgm": "dubstep"
        },
        "clockwork_realm": {
            "name": "钟表领域",
            "base_color": [25, 20, 15],
            "elements": {"clock_gears": 15, "clock_hands": 8, "roman_numerals": 12},
            "grid_color": (120, 100, 70),
            "element_type": "steampunk",
            "gradient": [(40, 30, 20), (60, 50, 35), (50, 40, 25)],
            "bgm": "jazz"
        },
        "firefly_forest": {
            "name": "萤火森林",
            "base_color": [5, 15, 10],
            "elements": {"fireflies": 30, "moss_clumps": 12, "glow_spores": 25},
            "grid_color": None,
            "element_type": "nature",
            "gradient": [(10, 25, 15), (15, 40, 25), (10, 30, 20)],
            "bgm": "calm"
        },
        "symphony_hall": {
            "name": "交响乐厅",
            "base_color": [15, 10, 25],
            "elements": {"music_notes": 20, "sound_waves": 10, "equalizers": 8},
            "grid_color": (100, 80, 150),
            "element_type": "music",
            "gradient": [(25, 15, 40), (40, 25, 60), (30, 20, 50)],
            "bgm": "orchestra"
        },
        "shinto_shrine": {
            "name": "神道神社",
            "base_color": [20, 15, 25],
            "elements": {"torii": 4, "paper_charms": 15, "shrine_lights": 12},
            "grid_color": None,
            "element_type": "shrine",
            "gradient": [(30, 20, 35), (50, 35, 50), (40, 30, 45)],
            "bgm": "mystery"
        },
        "afternoon_tea": {
            "name": "下午茶时光",
            "base_color": [245, 235, 225],
            "elements": {"tea_cups": 8, "pastries": 15, "tablecloth_patterns": 12},
            "grid_color": (220, 200, 180),
            "element_type": "tea_time",
            "gradient": [(250, 240, 230), (255, 245, 235), (245, 235, 225)],
            "bgm": "calm"
        },
        "cyber_dimension": {
            "name": "赛博维度",
            "base_color": [5, 5, 15],
            "elements": {"tech_cubes": 10, "circuit_lines": 12, "hologram_shards": 15},
            "grid_color": (0, 200, 150),
            "element_type": "cyber",
            "gradient": [(10, 10, 25), (15, 20, 40), (10, 15, 30)],
            "bgm": "breakbeat"
        },
        "ancient_coin_shop": {
            "name": "古代钱币铺",
            "base_color": [25, 20, 15],
            "elements": {"bronze_coins": 20, "ancient_seals": 8, "verdigris_spots": 15},
            "grid_color": (180, 120, 80),
            "element_type": "ancient_coins",
            "gradient": [(40, 30, 20), (60, 45, 30), (50, 35, 25)],
            "bgm": "calm"
        },
        "pottery_workshop": {
            "name": "陶艺工坊",
            "base_color": [30, 20, 15],
            "elements": {"clay_pots": 10, "pottery_wheels": 4, "clay_ripples": 12},
            "grid_color": (200, 120, 80),
            "element_type": "pottery",
            "gradient": [(50, 35, 25), (70, 50, 35), (60, 40, 30)],
            "bgm": "calm"
        },
        "amber_forest": {
            "name": "琥珀森林",
            "base_color": [35, 25, 10],
            "elements": {"amber_gems": 15, "resin_drops": 20, "ancient_tentacles": 6},
            "grid_color": (255, 180, 80),
            "element_type": "amber",
            "gradient": [(60, 45, 20), (80, 60, 30), (70, 50, 25)],
            "bgm": "calm"
        },
        "quantum_foam": {
            "name": "量子泡沫",
            "base_color": [5, 15, 10],
            "elements": {"quantum_particles": 200, "hexagons": 15},
            "grid_color": (0, 255, 150),
            "element_type": "quantum",
            "gradient": [(0, 30, 20), (50, 200, 100), (150, 100, 200)],
            "bgm": "mystery"
        },
        "forgotten_city": {
            "name": "遗忘都市",
            "base_color": [20, 35, 50],
            "elements": {"ruin_pillars": 15, "bubbles": 60, "stars": 80},
            "grid_color": None,
            "element_type": "underwater_city",
            "gradient": [(10, 20, 40), (255, 120, 60), (50, 150, 80)],
            "bgm": "mystery"
        },
        "shattered_sky": {
            "name": "破碎天空",
            "base_color": [30, 10, 15],
            "elements": {"sky_shards": 25, "stars": 150, "nebulae": 3},
            "grid_color": None,
            "element_type": "shattered",
            "gradient": [(150, 30, 50), (80, 20, 50), (40, 10, 20)],
            "bgm": "epic"
        },
        "bioluminescent_abyss": {
            "name": "生物发光深渊",
            "base_color": [2, 8, 15],
            "elements": {"bio_orbs": 35, "tentacles": 8, "spores": 120},
            "grid_color": None,
            "element_type": "bioluminescent",
            "gradient": [(0, 15, 30), (0, 80, 120), (20, 200, 180)],
            "bgm": "mystery"
        },
        "clockwork_dimension": {
            "name": "齿轮维度",
            "base_color": [25, 20, 15],
            "elements": {"gears": 18, "chains": 12, "cogs": 40},
            "grid_color": (180, 140, 100),
            "element_type": "clockwork",
            "gradient": [(40, 30, 20), (120, 90, 60), (200, 150, 100)],
            "bgm": "industrial"
        },
        "paper_scroll": {
            "name": "墨染卷轴",
            "base_color": [230, 220, 200],
            "elements": {"ink_drops": 12, "brush_strokes": 6, "paper_birds": 5},
            "grid_color": None,
            "element_type": "paper",
            "gradient": [(245, 235, 220), (220, 200, 180), (200, 180, 160)],
            "bgm": "calm"
        },
        "sakura_night": {
            "name": "樱花之夜",
            "base_color": [20, 10, 40],
            "elements": {"sakura": 80, "lanterns": 8, "fireflies": 50},
            "grid_color": None,
            "element_type": "sakura",
            "gradient": [(30, 20, 50), (40, 20, 60), (20, 10, 40)],
            "bgm": "calm"
        },
        "ocean_depths": {
            "name": "深海秘境",
            "base_color": [0, 20, 40],
            "elements": {"corals": 12, "jellyfish": 8, "bubbles_ocean": 100},
            "grid_color": None,
            "element_type": "ocean",
            "gradient": [(0, 30, 60), (0, 20, 50), (0, 10, 30)],
            "bgm": "calm"
        },
        "desert_storm": {
            "name": "沙漠风暴",
            "base_color": [80, 70, 50],
            "elements": {"sandstorm": 150, "dunes": 8, "cacti": 6},
            "grid_color": None,
            "element_type": "desert",
            "gradient": [(120, 100, 60), (100, 80, 50), (80, 60, 40)],
            "bgm": "battle"
        },
        "spiral_garden": {
            "name": "螺旋花园",
            "base_color": [25, 15, 35],
            "elements": {"petals_spiral": 60, "butterflies": 15, "wind_leaves": 40},
            "grid_color": None,
            "element_type": "garden",
            "gradient": [(40, 25, 50), (60, 40, 70), (30, 20, 45)],
            "bgm": "calm"
        },
        "floating_meadow": {
            "name": "浮空草甸",
            "base_color": [100, 180, 220],
            "elements": {"dandelions": 80, "vines": 12, "mushrooms": 10},
            "grid_color": None,
            "element_type": "meadow",
            "gradient": [(120, 200, 240), (140, 220, 250), (100, 180, 220)],
            "bgm": "calm"
        },
        "rainbow_realm": {
            "name": "虹彩空间",
            "base_color": [20, 20, 20],
            "elements": {"prisms": 10, "rainbow_particles": 120},
            "grid_color": None,
            "element_type": "rainbow",
            "gradient": [(40, 40, 40), (60, 30, 60), (30, 60, 60)],
            "bgm": "mystery"
        },
        "heaven_bridge": {
            "name": "天际之桥",
            "base_color": [180, 220, 255],
            "elements": {"feathers": 50, "clouds_soft": 15, "birds": 12},
            "grid_color": None,
            "element_type": "heaven",
            "gradient": [(200, 230, 255), (220, 240, 255), (180, 220, 255)],
            "bgm": "calm"
        },
        "jade_pond": {
            "name": "碧玉池塘",
            "base_color": [100, 180, 160],
            "elements": {"ripples": 20, "koi": 8, "pollen": 60},
            "grid_color": None,
            "element_type": "pond",
            "gradient": [(120, 200, 180), (140, 220, 200), (100, 180, 160)],
            "bgm": "calm"
        },
        "holy_light": {
            "name": "圣光殿堂",
            "base_color": [250, 245, 230],
            "elements": {"motes": 100, "feathers": 30, "holy_rays": 8, "angels": 6},
            "grid_color": None,
            "element_type": "holy",
            "gradient": [(255, 250, 240), (255, 255, 245), (245, 240, 220)],
            "bgm": "mystery"
        },
        "pixel_world": {
            "name": "像素世界",
            "base_color": [15, 15, 30],
            "elements": {"pixels": 40, "glitches": 15, "digital_rain": 20},
            "grid_color": (50, 50, 100),
            "element_type": "pixel",
            "gradient": [(20, 20, 40), (30, 30, 50), (15, 15, 30)],
            "bgm": "cyber"
        },
        "void_portal": {
            "name": "虚空之门",
            "base_color": [5, 5, 15],
            "elements": {"portals": 6, "wormhole_particles": 80, "distortions": 12},
            "grid_color": None,
            "element_type": "void",
            "gradient": [(10, 10, 25), (15, 10, 30), (5, 5, 15)],
            "bgm": "mystery"
        },
        "paper_dream": {
            "name": "纸梦空间",
            "base_color": [245, 240, 235],
            "elements": {"origami": 12, "paper_waves": 4, "fold_lines": 8},
            "grid_color": None,
            "element_type": "paper_dream",
            "gradient": [(255, 250, 245), (250, 245, 240), (245, 240, 235)],
            "bgm": "calm"
        }
    }
    
    def __init__(self, style="classic"):
        self.current_style = style
        self.stars = []
        self.special_elements = []  # 存放各种特殊元素
        self.grid_y = 0
        self.grid_speed = 3.0
        self.current_bg = [10, 10, 18]
        self.target_bg = [10, 10, 18]
        self.nebula_color = (0, 50, 100)
        self.warp_effect = False
        
        # 初始化当前风格
        self.load_style(style)
    
    def load_style(self, style):
        """加载指定的背景风格 - 根据元素类型创建不同的对象"""
        if style not in self.BG_STYLES:
            style = "classic"
        
        self.current_style = style
        config = self.BG_STYLES[style]
        elements = config["elements"]
        
        # 切换背景音乐
        if "bgm" in config:
            from utils import sound_mgr
            sound_mgr.play_music(config["bgm"])
        
        # 清空所有元素
        self.stars = []
        self.special_elements = []
        
        # 根据配置创建不同类型的元素
        if "stars" in elements:
            for _ in range(elements["stars"]):
                self.stars.append({
                    'x': random.randint(0, WIDTH), 
                    'y': random.randint(0, HEIGHT), 
                    'speed': random.uniform(1.5, 6.0),
                    'size': random.randint(1, 3), 
                    'alpha': random.randint(100, 255)
                })
        
        # 获取元素类型用于颜色主题
        element_type = config.get("element_type", "classic")
        
        # 经典元素
        if "nebulae" in elements:
            for _ in range(elements["nebulae"]):
                self.special_elements.append(Nebula(element_type))
        
        if "hexagons" in elements:
            for _ in range(elements["hexagons"]):
                self.special_elements.append(HexParticle())
        
        if "bubbles" in elements:
            for _ in range(elements["bubbles"]):
                self.special_elements.append(Bubble(element_type))
        
        if "embers" in elements:
            for _ in range(elements["embers"]):
                self.special_elements.append(Ember(element_type))
        
        if "snowflakes" in elements:
            for _ in range(elements["snowflakes"]):
                self.special_elements.append(Snowflake(element_type))
        
        if "matrix_rain" in elements:
            for _ in range(elements["matrix_rain"]):
                self.special_elements.append(MatrixRain())
        
        if "code_lines" in elements:
            for _ in range(elements["code_lines"]):
                self.special_elements.append(CodeLine())
        
        # 新场景元素
        if "clouds" in elements:
            for i in range(elements["clouds"]):
                self.special_elements.append(Cloud(i % 3))
        
        if "light_rays" in elements:
            for _ in range(elements["light_rays"]):
                self.special_elements.append(LightRay())
        
        if "underwater_beams" in elements:
            for _ in range(elements["underwater_beams"]):
                self.special_elements.append(UnderwaterBeam())
        
        if "rain" in elements:
            for _ in range(elements["rain"]):
                self.special_elements.append(RainDrop())
        
        if "lightning" in elements:
            for _ in range(elements["lightning"]):
                self.special_elements.append(Lightning())
        
        if "buildings" in elements:
            for _ in range(elements["buildings"]):
                self.special_elements.append(Building())
        
        if "aurora_waves" in elements:
            for i in range(elements["aurora_waves"]):
                self.special_elements.append(AuroraWave(i))
        
        if "asteroids" in elements:
            for _ in range(elements["asteroids"]):
                self.special_elements.append(Asteroid())
        
        if "volcano_smoke" in elements:
            for _ in range(elements["volcano_smoke"]):
                self.special_elements.append(VolcanoSmoke())
        
        # 新增背景元素
        if "maple_leaves" in elements:
            for _ in range(elements["maple_leaves"]):
                self.special_elements.append(MapleLeaf())
        
        if "salt_crystals" in elements:
            for _ in range(elements["salt_crystals"]):
                self.special_elements.append(SaltCrystal())
        
        if "salt_waves" in elements:
            for _ in range(elements["salt_waves"]):
                self.special_elements.append(SaltWave())
        
        if "debris" in elements:
            for _ in range(elements["debris"]):
                self.special_elements.append(WarDebris())
        
        if "smoke" in elements:
            for _ in range(elements["smoke"]):
                self.special_elements.append(VolcanoSmoke())
        
        if "crystals_top" in elements:
            for _ in range(elements["crystals_top"]):
                self.special_elements.append(Crystal(from_top=True))
        
        if "crystals_bottom" in elements:
            for _ in range(elements["crystals_bottom"]):
                self.special_elements.append(Crystal(from_top=False))
        
        if "distortions" in elements:
            for _ in range(elements["distortions"]):
                self.special_elements.append(TimeDistortion())
        
        if "quantum_particles" in elements:
            for _ in range(elements["quantum_particles"]):
                self.special_elements.append(QuantumParticle())
        
        if "ruin_pillars" in elements:
            for _ in range(elements["ruin_pillars"]):
                self.special_elements.append(RuinPillar())
        
        if "sky_shards" in elements:
            for _ in range(elements["sky_shards"]):
                self.special_elements.append(SkyShard())
        
        # 生物发光深渊元素
        if "bio_orbs" in elements:
            for _ in range(elements["bio_orbs"]):
                self.special_elements.append(BioOrb())
        
        if "tentacles" in elements:
            for _ in range(elements["tentacles"]):
                self.special_elements.append(BioTentacle())
        
        if "spores" in elements:
            for _ in range(elements["spores"]):
                self.special_elements.append(BioSpore())
        
        # 齿轮维度元素
        if "gears" in elements:
            for _ in range(elements["gears"]):
                self.special_elements.append(Gear())
        
        if "chains" in elements:
            for _ in range(elements["chains"]):
                self.special_elements.append(Chain())
        
        if "cogs" in elements:
            for _ in range(elements["cogs"]):
                self.special_elements.append(Cog())
        
        # 墨染卷轴元素
        if "ink_drops" in elements:
            for _ in range(elements["ink_drops"]):
                self.special_elements.append(InkDrop())
        
        if "brush_strokes" in elements:
            for _ in range(elements["brush_strokes"]):
                self.special_elements.append(BrushStroke())
        
        if "paper_birds" in elements:
            for _ in range(elements["paper_birds"]):
                self.special_elements.append(PaperBird())
        
        # 樱花之夜元素
        if "sakura" in elements:
            for _ in range(elements["sakura"]):
                self.special_elements.append(Sakura())
        
        if "lanterns" in elements:
            for _ in range(elements["lanterns"]):
                self.special_elements.append(Lantern())
        
        if "fireflies" in elements:
            for _ in range(elements["fireflies"]):
                self.special_elements.append(Firefly())
        
        # 深海秘境元素
        if "corals" in elements:
            for _ in range(elements["corals"]):
                self.special_elements.append(Coral())
        
        if "jellyfish" in elements:
            for _ in range(elements["jellyfish"]):
                self.special_elements.append(Jellyfish())
        
        if "bubbles_ocean" in elements:
            for _ in range(elements["bubbles_ocean"]):
                self.special_elements.append(Bubble2())
        
        # 沙漠风暴元素
        if "sandstorm" in elements:
            for _ in range(elements["sandstorm"]):
                self.special_elements.append(Sandstorm())
        
        if "dunes" in elements:
            for _ in range(elements["dunes"]):
                self.special_elements.append(Dune())
        
        if "cacti" in elements:
            for _ in range(elements["cacti"]):
                self.special_elements.append(Cactus())
        
        # 螺旋花园元素
        if "petals_spiral" in elements:
            for _ in range(elements["petals_spiral"]):
                self.special_elements.append(Petal())
        
        if "butterflies" in elements:
            for _ in range(elements["butterflies"]):
                self.special_elements.append(Butterfly())
        
        if "wind_leaves" in elements:
            for _ in range(elements["wind_leaves"]):
                self.special_elements.append(WindLeaf())
        
        # 浮空草甸元素
        if "dandelions" in elements:
            for _ in range(elements["dandelions"]):
                self.special_elements.append(Dandelion())
        
        if "vines" in elements:
            for _ in range(elements["vines"]):
                self.special_elements.append(Vine())
        
        if "mushrooms" in elements:
            for _ in range(elements["mushrooms"]):
                self.special_elements.append(Mushroom())
        
        # 虹彩空间元素
        if "prisms" in elements:
            for _ in range(elements["prisms"]):
                self.special_elements.append(Prism())
        
        if "rainbow_particles" in elements:
            for _ in range(elements["rainbow_particles"]):
                self.special_elements.append(Particle())
        
        # 天际之桥元素
        if "feathers" in elements:
            for _ in range(elements["feathers"]):
                self.special_elements.append(Feather())
        
        if "clouds_soft" in elements:
            for _ in range(elements["clouds_soft"]):
                self.special_elements.append(Cloud2())
        
        if "birds" in elements:
            for _ in range(elements["birds"]):
                self.special_elements.append(Bird())
        
        # 碧玉池塘元素
        if "ripples" in elements:
            for _ in range(elements["ripples"]):
                self.special_elements.append(Ripple())
        
        if "koi" in elements:
            for _ in range(elements["koi"]):
                self.special_elements.append(Koi())
        
        if "pollen" in elements:
            for _ in range(elements["pollen"]):
                self.special_elements.append(Pollen())
        
        # 圣光殿堂元素
        if "motes" in elements:
            for _ in range(elements["motes"]):
                self.special_elements.append(Mote())
        
        if "holy_rays" in elements:
            for _ in range(elements["holy_rays"]):
                self.special_elements.append(HolyRay())
        
        if "angels" in elements:
            for _ in range(elements["angels"]):
                self.special_elements.append(Angel())
        
        # 像素世界元素
        if "pixels" in elements:
            for _ in range(elements["pixels"]):
                self.special_elements.append(Pixel())
        
        if "glitches" in elements:
            for _ in range(elements["glitches"]):
                self.special_elements.append(Glitch())
        
        if "digital_rain" in elements:
            for _ in range(elements["digital_rain"]):
                self.special_elements.append(DigitalRain())
        
        # 虚空之门元素
        if "portals" in elements:
            for _ in range(elements["portals"]):
                self.special_elements.append(Portal())
        
        if "wormhole_particles" in elements:
            for _ in range(elements["wormhole_particles"]):
                self.special_elements.append(Wormhole())
        
        if "distortions" in elements:
            for _ in range(elements["distortions"]):
                self.special_elements.append(Distortion())
        
        # 纸梦空间元素
        if "origami" in elements:
            for _ in range(elements["origami"]):
                self.special_elements.append(Origami())
        
        if "paper_waves" in elements:
            for _ in range(elements["paper_waves"]):
                self.special_elements.append(PaperWave())
        
        if "fold_lines" in elements:
            for _ in range(elements["fold_lines"]):
                self.special_elements.append(FoldLine())
        
        if "candles" in elements:
            for _ in range(elements["candles"]):
                self.special_elements.append(Candle())
        
        if "book_pages" in elements:
            for _ in range(elements["book_pages"]):
                self.special_elements.append(BookPage())
        
        if "quills" in elements:
            for _ in range(elements["quills"]):
                self.special_elements.append(Quill())
        
        if "satellites" in elements:
            for _ in range(elements["satellites"]):
                self.special_elements.append(Satellite())
        
        if "signal_waves" in elements:
            for _ in range(elements["signal_waves"]):
                self.special_elements.append(SignalWave())
        
        if "data_streams" in elements:
            for _ in range(elements["data_streams"]):
                self.special_elements.append(DataStream())
        
        if "energy_nodes" in elements:
            for _ in range(elements["energy_nodes"]):
                self.special_elements.append(EnergyNode())
        
        if "lightning_arcs" in elements:
            for _ in range(elements["lightning_arcs"]):
                self.special_elements.append(LightningArc())
        
        if "power_cores" in elements:
            for _ in range(elements["power_cores"]):
                self.special_elements.append(PowerCore())
        
        if "clock_gears" in elements:
            for _ in range(elements["clock_gears"]):
                self.special_elements.append(ClockGear())
        
        if "clock_hands" in elements:
            for _ in range(elements["clock_hands"]):
                self.special_elements.append(ClockHand())
        
        if "roman_numerals" in elements:
            for _ in range(elements["roman_numerals"]):
                self.special_elements.append(RomanNumeral())
        
        if "fireflies" in elements:
            for _ in range(elements["fireflies"]):
                self.special_elements.append(Firefly())
        
        if "moss_clumps" in elements:
            for _ in range(elements["moss_clumps"]):
                self.special_elements.append(MossClump())
        
        if "glow_spores" in elements:
            for _ in range(elements["glow_spores"]):
                self.special_elements.append(GlowSpore())
        
        if "music_notes" in elements:
            for _ in range(elements["music_notes"]):
                self.special_elements.append(MusicNote())
        
        if "sound_waves" in elements:
            for _ in range(elements["sound_waves"]):
                self.special_elements.append(SoundWave())
        
        if "equalizers" in elements:
            for _ in range(elements["equalizers"]):
                self.special_elements.append(Equalizer())
        
        if "torii" in elements:
            for _ in range(elements["torii"]):
                self.special_elements.append(Torii())
        
        if "paper_charms" in elements:
            for _ in range(elements["paper_charms"]):
                self.special_elements.append(PaperCharm())
        
        if "shrine_lights" in elements:
            for _ in range(elements["shrine_lights"]):
                self.special_elements.append(ShrineLight())
        
        if "tea_cups" in elements:
            for _ in range(elements["tea_cups"]):
                self.special_elements.append(TeaCup())
        
        if "pastries" in elements:
            for _ in range(elements["pastries"]):
                self.special_elements.append(Pastry())
        
        if "tablecloth_patterns" in elements:
            for _ in range(elements["tablecloth_patterns"]):
                self.special_elements.append(TableCloth())
        
        if "tech_cubes" in elements:
            for _ in range(elements["tech_cubes"]):
                self.special_elements.append(TechCube())
        
        if "circuit_lines" in elements:
            for _ in range(elements["circuit_lines"]):
                self.special_elements.append(CircuitLine())
        
        if "hologram_shards" in elements:
            for _ in range(elements["hologram_shards"]):
                self.special_elements.append(HologramShard())
        
        if "bronze_coins" in elements:
            for _ in range(elements["bronze_coins"]):
                self.special_elements.append(BronzeCoin())
        
        if "ancient_seals" in elements:
            for _ in range(elements["ancient_seals"]):
                self.special_elements.append(AncientSeal())
        
        if "verdigris_spots" in elements:
            for _ in range(elements["verdigris_spots"]):
                self.special_elements.append(VerdigrisSpot())
        
        if "clay_pots" in elements:
            for _ in range(elements["clay_pots"]):
                self.special_elements.append(ClayPot())
        
        if "pottery_wheels" in elements:
            for _ in range(elements["pottery_wheels"]):
                self.special_elements.append(PotteryWheel())
        
        if "clay_ripples" in elements:
            for _ in range(elements["clay_ripples"]):
                self.special_elements.append(ClayRipple())
        
        if "amber_gems" in elements:
            for _ in range(elements["amber_gems"]):
                self.special_elements.append(AmberGem())
        
        if "resin_drops" in elements:
            for _ in range(elements["resin_drops"]):
                self.special_elements.append(ResinDrop())
        
        if "ancient_tentacles" in elements:
            for _ in range(elements["ancient_tentacles"]):
                self.special_elements.append(AncientTentacle())
        
        # 设置基础颜色
        self.current_bg = config["base_color"].copy()
        self.target_bg = config["base_color"].copy()
    
    def set_style(self, style):
        """切换背景风格"""
        self.load_style(style)
    
    def get_style_name(self):
        """获取当前风格名称"""
        return self.BG_STYLES.get(self.current_style, {}).get("name", "未知")

    def update(self, boss_type=None, warning=False, speed_mult=1.0):
        self.warp_effect = False
        
        # 获取当前风格的配置
        config = self.BG_STYLES.get(self.current_style, self.BG_STYLES["classic"])
        
        # 根据BOSS类型改变背景色调
        if boss_type == "carrier": self.target_bg = [40, 10, 10]; self.nebula_color = (100, 20, 20)
        elif boss_type == "fortress": self.target_bg = [30, 25, 15]; self.nebula_color = (80, 60, 20)
        elif boss_type == "assassin": self.target_bg = [20, 0, 40]; self.nebula_color = (60, 0, 100); self.warp_effect = True; speed_mult *= 4.0
        elif boss_type == "seraphim": self.target_bg = [50, 50, 60]; self.nebula_color = (200, 180, 50)
        elif boss_type == "leviathan": self.target_bg = [20, 0, 30]; self.nebula_color = (80, 0, 120)
        elif boss_type == "overlord": self.target_bg = [0, 20, 20]; self.nebula_color = (0, 100, 100)
        elif boss_type == "ragnarok": self.target_bg = [50, 0, 0]; self.nebula_color = (255, 0, 0)
        elif boss_type == "hydra": self.target_bg = [0, 30, 0]; self.nebula_color = (0, 255, 0)
        elif boss_type == "chronos": self.target_bg = [0, 0, 50]; self.nebula_color = (100, 100, 255); self.warp_effect = True
        elif boss_type == "gazer": self.target_bg = [20, 0, 0]; self.nebula_color = EYE_RED
        elif boss_type == "lich": self.target_bg = [0, 20, 20]; self.nebula_color = GHOST_CYAN
        elif boss_type == "tempest": self.target_bg = [10, 10, 60]; self.nebula_color = WIND_BLUE; speed_mult *= 5.0
        elif warning:
            if (pygame.time.get_ticks() // 300) % 2 == 0: self.target_bg = [50, 0, 0]
            else: self.target_bg = [20, 0, 0]
        else:
            # 使用当前风格的基础颜色
            self.target_bg = config["base_color"].copy()
            # 根据背景类型设置默认星云颜色
            element_type = config.get("element_type", "classic")
            if element_type == "fire" or element_type == "lava":
                self.nebula_color = (255, 100, 0)
            elif element_type == "cyberpunk":
                self.nebula_color = (255, 0, 180)
            elif element_type == "underwater":
                self.nebula_color = (0, 100, 150)
            elif element_type == "winter":
                self.nebula_color = (150, 200, 255)
            else:
                self.nebula_color = (0, 50, 100)
            
        # 平滑过渡背景色
        for i in range(3):
            self.current_bg[i] += (self.target_bg[i] - self.current_bg[i]) * 0.05
            
        # 更新星星
        for s in self.stars:
            s['y'] += s['speed'] * speed_mult
            if s['y'] > HEIGHT: 
                s['y'] = 0
                s['x'] = random.randint(0, WIDTH)
        
        # 更新所有特殊元素
        for elem in self.special_elements:
            elem.update(speed_mult)
            
        self.grid_y = (self.grid_y + self.grid_speed * speed_mult) % 80

    def draw(self, surf):
        # 特殊背景渐变处理
        if self.current_style == "dawn_clouds":
            # 晨曦云海 - 橙粉色渐变
            for y in range(HEIGHT):
                ratio = y / HEIGHT
                r = int(255 * (1 - ratio) + 200 * ratio)
                g = int(180 * (1 - ratio) + 150 * ratio)
                b = int(150 * (1 - ratio) + 255 * ratio)
                pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
        elif self.current_style == "city_sky":
            # 城市上空 - 橙红到深蓝渐变
            for y in range(HEIGHT):
                ratio = y / HEIGHT
                r = int(60 * (1 - ratio) + 20 * ratio)
                g = int(30 * (1 - ratio) + 20 * ratio)
                b = int(80 * (1 - ratio) + 80 * ratio)
                pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
        else:
            # 普通填充
            surf.fill([int(c) for c in self.current_bg])
        
        config = self.BG_STYLES[self.current_style]
        elements = config["elements"]
        
        # 绘制网格线（如果启用）
        if "grid" in elements and elements["grid"] and config["grid_color"]:
            grid_alpha = 20
            grid_color = config["grid_color"] if not self.warp_effect else (255, 0, 255)
            
            # 纵向线
            for x in range(0, WIDTH, 100):
                s = pygame.Surface((2, HEIGHT), pygame.SRCALPHA)
                s.fill((*grid_color, grid_alpha))
                surf.blit(s, (x, 0))
                
            # 横向线
            for y in range(int(self.grid_y) - 80, HEIGHT, 80):
                s = pygame.Surface((WIDTH, 2), pygame.SRCALPHA)
                s.fill((*grid_color, grid_alpha))
                surf.blit(s, (0, y))
        
        # 绘制所有特殊元素
        for elem in self.special_elements:
            if isinstance(elem, Nebula):
                elem.draw(surf, self.nebula_color)
            else:
                elem.draw(surf)
        
        # 绘制星星
        for s in self.stars:
            if self.warp_effect:
                length = s['speed'] * 10
                pygame.draw.line(surf, (s['alpha'], s['alpha'], s['alpha']), (s['x'], s['y']), (s['x'], s['y'] - length), 1)
            else:
                pygame.draw.circle(surf, (s['alpha'], s['alpha'], s['alpha']), (s['x'], int(s['y'])), 1 if s['size']<2 else 2)

class BossManager:
    """Boss spawn and scheduling manager with progressive difficulty.
    Controls when a boss warning is shown and when the boss is spawned.
    Implements phase-based difficulty scaling and strategic boss selection.
    """
    def __init__(self, base_interval=5000, scaling_per_level=1000, warning_duration=180, min_interval=None, accel_per_spawn=200):
        self.base_interval = base_interval
        self.scaling_per_level = scaling_per_level
        self.warning_duration = warning_duration
        self.next_boss_score = base_interval
        self.pending = False
        self.warning_timer = 0
        self.cooldown = 0
        self.last_spawned = None
        # spawn acceleration and minimum interval limits
        self.spawn_count = 0
        self.accel_per_spawn = accel_per_spawn
        self.min_interval = min_interval if min_interval is not None else max(100, int(self.base_interval * 0.15))  # 更短的最小间隔
        
        # 阶段性难度系统
        self.game_phase = 0  # 0: Early, 1: Mid, 2: Late, 3: Endgame
        self.phase_thresholds = [3, 8, 15]  # 根据spawn_count切换阶段
        self.boss_difficulty_curve = []  # 记录难度曲线

    def get_game_phase(self):
        """根据生成次数返回当前游戏阶段"""
        if self.spawn_count < self.phase_thresholds[0]:
            return 0  # Early: 基础boss
        elif self.spawn_count < self.phase_thresholds[1]:
            return 1  # Mid: 中等难度
        elif self.spawn_count < self.phase_thresholds[2]:
            return 2  # Late: 高难度
        else:
            return 3  # Endgame: 极难boss

    def update(self, score, player_level, boss_exists=False):
        """Call every frame from main loop to update timers.
        Returns a tuple (warning_active, spawn_now)
        """
        spawn_now = False
        warning_active = False

        # Cooldown after spawn (no spawn during cooldown)
        if self.cooldown > 0:
            self.cooldown -= 1

        # If there is an active pending warning, count down
        if self.pending and self.warning_timer > 0:
            self.warning_timer -= 1
            warning_active = True
            if self.warning_timer <= 0:
                # timer finished -> spawn now if no boss exists
                if not boss_exists:
                    spawn_now = True
                    self.pending = False
                    self.last_spawned = score
                    # schedule next boss score
                    # increase spawn_count and shorten future intervals slightly
                    self.spawn_count += 1
                    
                    # 阶段性难度递减
                    phase = self.get_game_phase()
                    if phase == 0:  # Early
                        interval = max(self.min_interval, self.base_interval - self.spawn_count * self.accel_per_spawn * 0.8)
                    elif phase == 1:  # Mid
                        interval = max(self.min_interval, self.base_interval - self.spawn_count * self.accel_per_spawn * 1.0)
                    elif phase == 2:  # Late
                        interval = max(self.min_interval, self.base_interval - self.spawn_count * self.accel_per_spawn * 1.2)
                    else:  # Endgame
                        interval = max(self.min_interval, self.base_interval - self.spawn_count * self.accel_per_spawn * 1.5)
                    
                    self.next_boss_score += interval + (player_level * self.scaling_per_level)
                    # set a small cooldown to avoid immediate reschedule
                    self.cooldown = 600
        elif not self.pending and not boss_exists and score >= self.next_boss_score and self.cooldown <= 0:
            # Schedule warning and mark pending
            self.pending = True
            self.warning_timer = self.warning_duration
            warning_active = True

        return (warning_active, spawn_now)

    def spawn_boss(self, player_level=1, boss_type=None):
        """Return a new Boss instance with phase-based difficulty scaling.
        The main caller should add it to all_sprites and assign to global boss.
        """
        try:
            from sprites import Boss
            
            phase = self.get_game_phase()
            types = list(BOSS_DB.keys())
            # 如果传入boss_type则直接指定
            if boss_type is not None and boss_type in BOSS_DB:
                chosen = boss_type
                b = Boss(chosen)
                # 应用阶段性增强
                phase = self.get_game_phase()
                if phase >= 1:
                    health_mult = 1.0 + (phase - 1) * 0.25
                    b.health *= health_mult
                    b.max_health *= health_mult
                    b.speed_base *= (1.0 + (phase - 1) * 0.15)
                    b.fire_rate_mult *= (1.0 - (phase - 1) * 0.05)
                self.last_spawned = b
                return b
            # 无限模式自动包含所有Boss，包括新加的void_golem和abyss_queen
            
            # 计算每个boss的难度分数
            diffs = []
            for t in types:
                stats = BOSS_DB[t].get('stats', [])
                if stats:
                    # 计算平均难度
                    diff = sum([s[1] for s in stats]) / len(stats)
                else:
                    diff = 50
                diffs.append(max(1, diff))
            
            # 根据阶段调整权重
            if phase == 0:  # Early: 偏好低难度boss
                bias = 1.0 + player_level * 0.02
                scaled = [d * (0.5 + player_level * 0.02) for d in diffs]
            elif phase == 1:  # Mid: 平衡选择
                bias = 1.0 + player_level * 0.04
                scaled = [d * (0.8 + player_level * 0.04) for d in diffs]
            elif phase == 2:  # Late: 偏好高难度boss
                bias = 1.0 + player_level * 0.06
                scaled = [d * (1.2 + player_level * 0.06) for d in diffs]
            else:  # Endgame: 大幅提升强力boss概率
                bias = 1.0 + player_level * 0.08
                scaled = [d * (1.5 + player_level * 0.08) for d in diffs]
            
            total = sum(scaled)
            weights = [d / total for d in scaled]
            
            # 选择boss
            chosen = random.choices(types, weights=weights, k=1)[0]
            b = Boss(chosen)
            
            # 应用阶段性增强
            if phase >= 1:
                # Mid阶段开始增加boss属性
                health_mult = 1.0 + (phase - 1) * 0.25
                b.health *= health_mult
                b.max_health *= health_mult
                b.speed_base *= (1.0 + (phase - 1) * 0.15)
                b.fire_rate_mult *= (1.0 - (phase - 1) * 0.05)  # 提升射速
            
            self.last_spawned = b
            return b
        except Exception as e:
            log_error(f"Boss spawn failed: {e}")
            return None

    def reset(self):
        self.next_boss_score = self.base_interval
        self.pending = False
        self.warning_timer = 0
        self.cooldown = 0
        self.last_spawned = None
        self.spawn_count = 0
        self.game_phase = 0
        self.boss_difficulty_curve = []


def check_boss_system():
    """Simple check routine to validate the boss manager behavior.
    Returns a dict with basic pass/fail properties and helpful messages.
    """
    results = {
        'success': True,
        'messages': []
    }
    try:
        bm = BossManager(base_interval=100, scaling_per_level=10, warning_duration=3)
        # Should not be pending initially
        if bm.pending:
            results['success'] = False
            results['messages'].append('Initial pending True')
        # Simulate reaching threshold
        warning, spawn_now = bm.update(100, player_level=1, boss_exists=False)
        if not warning:
            results['success'] = False
            results['messages'].append('Warning not triggered on threshold')
        # Step through warning duration
        spawn_count = 0
        for i in range(5):
            warning, spawn = bm.update(100, player_level=1, boss_exists=False)
            if spawn: spawn_count += 1
        if spawn_count == 0:
            results['success'] = False
            results['messages'].append('Spawn did not occur after warning')
    except Exception as e:
        results['success'] = False
        results['messages'].append(f'Check failed: {e}')
    return results

# ==============================================================================
#   武器系统逻辑 (无绘图)
# ==============================================================================
class WeaponSystem:
    def __init__(self, data):
        self.data = data
        self.type = data['type']
        self.stats = WEAPON_TYPES[self.type]
        self.level = data['stars']
        
        # 运行时状态
        self.heat = 0.0
        self.energy = 100.0
        self.ammo = 10
        self.reload_timer = 0
        self.is_firing = False
        
        # === 数值成长公式 ===
        base_dmg_map = {
            "cannon": 20, "beam": 8, "explosive": 60, "missile": 35, "exotic": 15,
            "scatter": 18, "arc": 25, "sniper": 150, "blade": 40,
            "railgun": 200, "void": 15, "frost": 12, "swarm": 15,
            "pulse": 45, "vortex": 30, "gravity": 25, "wave": 35, "inferno": 28, "split": 50
        }
        growth_mult = 1 + (self.level - 1) * 0.3
        self.damage = base_dmg_map.get(self.type, 20) * growth_mult
        
        self.cooldown = 0
        
        # === 武器特性参数 ===
        if self.type == "cannon":
            self.max_heat = 100 + (self.level * 10)
            self.cool_rate = 1.0 + (self.level * 0.1)
            self.heat_per_shot = 5
            self.cooldown_max = 8
        elif self.type == "beam":
            self.max_energy = 100 + (self.level * 20)
            self.drain_rate = 2.0
            self.recharge_rate = 0.5 + (self.level * 0.1)
            self.cooldown_max = 1
        elif self.type == "explosive":
            self.max_ammo = 5 + int(self.level * 1.5)
            self.ammo = self.max_ammo
            self.reload_time = max(60, 120 - self.level * 5)
            self.cooldown_max = 40
        elif self.type == "missile":
            self.cooldown_max = max(30, 60 - self.level * 3)
        elif self.type == "exotic":
            self.cooldown_max = max(100, 180 - self.level * 10)
        elif self.type == "scatter": 
            self.max_ammo = 8 + self.level
            self.ammo = self.max_ammo
            self.reload_time = 60 
            self.cooldown_max = 30 
        elif self.type == "arc": 
            self.max_energy = 100
            self.drain_rate = 15 
            self.recharge_rate = 1.0
            self.cooldown_max = 15
        elif self.type == "sniper": 
            self.cooldown_max = 120 
        elif self.type == "blade": 
            self.cooldown_max = 50
        elif self.type == "railgun": self.cooldown_max = 150
        elif self.type == "void": 
            self.max_ammo = 4; self.ammo = self.max_ammo; self.reload_time = 100; self.cooldown_max = 60
        elif self.type == "frost":
            self.max_heat = 100; self.cool_rate = 1.5; self.heat_per_shot = 4; self.cooldown_max = 6
        elif self.type == "swarm": self.cooldown_max = 180
        # === 新武器配置 ===
        elif self.type == "pulse":
            self.max_energy = 120; self.drain_rate = 8; self.recharge_rate = 1.0; self.cooldown_max = 12
        elif self.type == "vortex":
            self.max_ammo = 6; self.ammo = self.max_ammo; self.reload_time = 80; self.cooldown_max = 20
        elif self.type == "gravity":
            self.max_energy = 100; self.drain_rate = 5; self.recharge_rate = 1.5; self.cooldown_max = 40
        elif self.type == "wave":
            self.max_heat = 80; self.cool_rate = 2.0; self.heat_per_shot = 3; self.cooldown_max = 10
        elif self.type == "inferno":
            self.max_energy = 150; self.drain_rate = 3; self.recharge_rate = 0.8; self.cooldown_max = 5
        elif self.type == "split":
            self.max_ammo = 4; self.ammo = self.max_ammo; self.reload_time = 90; self.cooldown_max = 35

    def update(self):
        if self.reload_timer > 0: self.reload_timer -= 1
        
        if self.type == "cannon":
            if not self.is_firing: self.heat = max(0, self.heat - self.cool_rate)
        elif self.type == "beam":
            if not self.is_firing: self.energy = min(self.max_energy, self.energy + self.recharge_rate)
        elif self.type == "explosive" or self.type == "scatter":
            if self.ammo <= 0 and self.reload_timer == 0:
                self.ammo = self.max_ammo 
        elif self.type == "arc":
            if not self.is_firing: self.energy = min(self.max_energy, self.energy + self.recharge_rate)
        # 新武器能量/弹药恢复
        elif self.type == "pulse":
            if not self.is_firing: self.energy = min(self.max_energy, self.energy + self.recharge_rate)
        elif self.type == "vortex" or self.type == "split":
            if self.ammo <= 0 and self.reload_timer == 0:
                self.ammo = self.max_ammo
        elif self.type == "gravity":
            if not self.is_firing: self.energy = min(self.max_energy, self.energy + self.recharge_rate)
        elif self.type == "wave":
            if not self.is_firing: self.heat = max(0, self.heat - self.cool_rate)
        elif self.type == "inferno":
            if not self.is_firing: self.energy = min(self.max_energy, self.energy + self.recharge_rate)

        self.is_firing = False 

    def can_shoot(self):
        if self.reload_timer > 0: return False
        if self.type == "cannon" and self.heat >= self.max_heat: return False
        if self.type == "beam" and self.energy <= 0: return False
        if (self.type == "explosive" or self.type == "scatter") and self.ammo <= 0: 
            self.reload_timer = self.reload_time 
            return False
        if self.type == "arc" and self.energy < self.drain_rate: return False
        # 新武器能量/弹药检查
        if self.type == "pulse" and self.energy < self.drain_rate: return False
        if (self.type == "vortex" or self.type == "split") and self.ammo <= 0:
            self.reload_timer = self.reload_time
            return False
        if self.type == "gravity" and self.energy < self.drain_rate: return False
        if self.type == "wave" and self.heat >= self.max_heat: return False
        if self.type == "inferno" and self.energy < self.drain_rate: return False
        return True

    def shoot(self, owner_rect, mobs_group, homing_lvl=0):
        # 实际的 Bullet 生成逻辑在 Player 类中调用 sprites 模块的类
        # 这里只处理数值消耗
        self.is_firing = True
        self.reload_timer = self.cooldown_max
        
        if self.type == "cannon": self.heat = min(self.max_heat, self.heat + self.heat_per_shot)
        elif self.type == "beam": self.energy -= self.drain_rate
        elif self.type == "explosive": self.ammo -= 1
        elif self.type == "scatter": self.ammo -= 1
        elif self.type == "arc": self.energy -= self.drain_rate
        elif self.type == "void": self.ammo -= 1
        elif self.type == "frost": self.heat = min(self.max_heat, self.heat + self.heat_per_shot)
        # 新武器消耗处理
        elif self.type == "pulse": self.energy -= self.drain_rate
        elif self.type == "vortex": self.ammo -= 1
        elif self.type == "gravity": self.energy -= self.drain_rate
        elif self.type == "wave": self.heat = min(self.max_heat, self.heat + self.heat_per_shot)
        elif self.type == "inferno": self.energy -= self.drain_rate
        elif self.type == "split": self.ammo -= 1