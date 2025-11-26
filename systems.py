import pygame
import json
import os
import random
from config import *
from utils import sound_mgr, log_error

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
                'speed': random.uniform(0.5, 3.0), 
                'size': random.randint(1, 3), 
                'alpha': random.randint(100, 255)
            })
        self.nebulae = [Nebula() for _ in range(6)] # 增加星云数量
        self.grid_y = 0
        self.grid_speed = 1.0
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
            "railgun": 200, "void": 15, "frost": 12, "swarm": 15
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

        self.is_firing = False 

    def can_shoot(self):
        if self.reload_timer > 0: return False
        if self.type == "cannon" and self.heat >= self.max_heat: return False
        if self.type == "beam" and self.energy <= 0: return False
        if (self.type == "explosive" or self.type == "scatter") and self.ammo <= 0: 
            self.reload_timer = self.reload_time 
            return False
        if self.type == "arc" and self.energy < self.drain_rate: return False
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