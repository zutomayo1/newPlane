import pygame
import json
import os
import random
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
#   背景与环境
# ==============================================================================
class Nebula:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.size = random.randint(150, 400) # 增大星云尺寸适配宽屏
        self.speed = random.uniform(0.5, 1.5)
        self.color = random.choice([(0, 50, 100), (20, 0, 50), (0, 20, 40)])
        self.alpha = random.randint(30, 80)

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

class BackgroundManager:
    def __init__(self):
        self.stars = []
        # 增加星星数量适配宽屏
        for _ in range(200):
            self.stars.append({
                'x': random.randint(0, WIDTH), 
                'y': random.randint(0, HEIGHT), 
                'speed': random.uniform(1.5, 6.0),  # 星星速度提升3倍
                'size': random.randint(1, 3), 
                'alpha': random.randint(100, 255)
            })
        self.nebulae = [Nebula() for _ in range(6)] # 增加星云数量
        self.grid_y = 0
        self.grid_speed = 3.0  # 网格速度提升3倍
        self.current_bg = [10, 10, 18]
        self.target_bg = [10, 10, 18]
        self.nebula_color = (0, 50, 100)
        self.warp_effect = False

    def update(self, boss_type=None, warning=False, speed_mult=1.0):
        self.warp_effect = False
        
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
            self.target_bg = [10, 10, 20]; self.nebula_color = (0, 40, 80)
            
        # 平滑过渡背景色
        for i in range(3):
            self.current_bg[i] += (self.target_bg[i] - self.current_bg[i]) * 0.05
            
        # 更新星星
        for s in self.stars:
            s['y'] += s['speed'] * speed_mult
            if s['y'] > HEIGHT: 
                s['y'] = 0
                s['x'] = random.randint(0, WIDTH)
                
        # 更新星云
        for n in self.nebulae:
            n.update(speed_mult)
            
        self.grid_y = (self.grid_y + self.grid_speed * speed_mult) % 80

    def draw(self, surf):
        surf.fill([int(c) for c in self.current_bg])
        
        # 绘制网格线
        grid_alpha = 20
        grid_color = (0, 255, 255) if not self.warp_effect else (255, 0, 255)
        
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
            
        for n in self.nebulae:
            n.draw(surf, self.nebula_color)
            
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