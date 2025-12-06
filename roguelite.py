# ==============================================================================
#   肉鸽（Roguelite）系统核心 - 升级、增益、局内成长
# ==============================================================================
import random
import pygame
import math
from config import *
from utils import sound_mgr, log_error, log_info, log_debug

# ==============================================================================
#   物品系统（掉落战利品）
# ==============================================================================
class Item:
    """游戏中掉落的物品"""
    def __init__(self, item_type, x, y, rarity=1):
        self.type = item_type  # "health", "ammo", "core", "chip", "gold"
        self.x = x
        self.y = y
        self.rarity = rarity  # 1-3星，影响品质和收益
        self.radius = 8 + rarity * 2
        self.alive = True
        
        # 物品属性
        self.item_data = {
            "health": {"name": "医疗包", "color": (0, 255, 100), "value": 25},
            "ammo": {"name": "弹药箱", "color": (255, 200, 0), "value": 3},
            "core": {"name": "核心片段", "color": (0, 150, 255), "value": 1},
            "chip": {"name": "芯片", "color": (200, 0, 255), "value": 1},
            "gold": {"name": "经验值", "color": (255, 215, 0), "value": 50},
        }
        
        if item_type in self.item_data:
            self.name = self.item_data[item_type]["name"]
            self.color = self.item_data[item_type]["color"]
            self.value = self.item_data[item_type]["value"] + rarity * 5
    
    def update(self, target_x=None, target_y=None):
        """更新物品，实现吸取效果"""
        if target_x is not None and target_y is not None:
            # 物品被吸取时向目标移动
            dx = target_x - self.x
            dy = target_y - self.y
            dist = (dx**2 + dy**2) ** 0.5
            if dist < 2:
                self.alive = False
                return
            if dist > 0:
                self.x += dx / dist * 6
                self.y += dy / dist * 6
    
    def draw(self, surface):
        """绘制物品"""
        if self.alive:
            # 绘制物品圆形
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            # 绘制外圆环（闪烁效果）
            import math as m
            glow = int(3 + 2 * m.sin(pygame.time.get_ticks() / 100))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius + glow, 1)


class ItemManager:
    """管理游戏中的物品"""
    def __init__(self):
        self.items = []
    
    def spawn_item(self, item_type, x, y, rarity=1):
        """在指定位置生成物品"""
        item = Item(item_type, x, y, rarity)
        self.items.append(item)
        return item
    
    def spawn_random_drop(self, x, y, rarity=1):
        """生成随机掉落物品"""
        drop_table = ["health", "ammo", "gold", "gold", "core", "chip"]
        item_type = random.choice(drop_table)
        return self.spawn_item(item_type, x, y, rarity)
    
    def update(self, player=None):
        """更新所有物品，处理吸取"""
        for item in self.items:
            if player:
                # 计算是否在吸取范围内 (200 像素)
                dx = player.x - item.x
                dy = player.y - item.y
                dist = (dx**2 + dy**2) ** 0.5
                
                if dist < 200:
                    # 在吸取范围内
                    item.update(player.x, player.y)
                else:
                    item.update()
                
                # 碰撞检测
                if dist < 30:
                    self.pickup_item(item, player)
            else:
                item.update()
        
        self.items = [item for item in self.items if item.alive]
    
    def pickup_item(self, item, player):
        """拾起物品，应用效果"""
        sound_mgr.play("item_pickup")
        
        if item.type == "health":
            heal_amount = item.value
            old_hp = player.hp
            player.hp = min(player.max_hp, player.hp + heal_amount)
            log_info(f"玩家获得 {heal_amount} HP，当前: {player.hp}/{player.max_hp}")
        
        elif item.type == "ammo":
            if hasattr(player, 'weapon_slots') and player.weapon_slots[player.current_slot]:
                slot = player.weapon_slots[player.current_slot]
                if hasattr(slot, 'ammo'):
                    slot.ammo = min(slot.ammo_max, slot.ammo + item.value)
        
        elif item.type == "core":
            if hasattr(player, 'upgrade_manager'):
                player.upgrade_manager.current_upgrades.append("core")
                log_info(f"玩家获得核心片段，总数: {sum(1 for u in player.upgrade_manager.current_upgrades if u == 'core')}")
        
        elif item.type == "chip":
            if hasattr(player, 'upgrade_manager'):
                player.upgrade_manager.current_upgrades.append("chip")
        
        elif item.type == "gold":
            # 增加经验值并同步分数
            if hasattr(player, 'add_xp'):
                player.add_xp(item.value)
                log_info(f"获得 {item.value} 经验值，当前等级: {player.level}, XP: {player.xp}/{player.next_level_xp}")
            else:
                player.score += item.value
                log_info(f"获得 {item.value} 分数，总分数: {player.score}")
        
        item.alive = False
    
    def draw(self, surface):
        """绘制所有物品"""
        for item in self.items:
            item.draw(surface)

# ==============================================================================
#   成就系统（Achievement）
# ==============================================================================
class Achievement:
    """成就类"""
    def __init__(self, achievement_id, name, description, icon_char="★", reward=100):
        self.id = achievement_id
        self.name = name
        self.description = description
        self.icon_char = icon_char
        self.reward = reward  # 完成成就获得的分数
        self.unlocked = False
        self.unlock_time = None
    
    def unlock(self):
        """解锁成就"""
        if not self.unlocked:
            self.unlocked = True
            self.unlock_time = pygame.time.get_ticks()
            sound_mgr.play("achievement")
            return True
        return False


class AchievementManager:
    """管理成就系统"""
    def __init__(self):
        self.achievements = self._init_achievements()
        self.stats = {
            "total_kills": 0,           # 总击杀数
            "total_damage": 0,          # 总伤害
            "runs_completed": 0,        # 完成的游戏数
            "bosses_killed": 0,         # 击杀的BOSS数
            "max_wave": 0,              # 最高波数
            "max_combo": 0,             # 最高连击
            "upgrades_collected": 0,    # 收集的升级数
            "perfect_runs": 0,          # 完美通关（无伤）
        }
    
    def _init_achievements(self):
        """初始化成就列表"""
        return {
            # 基础成就
            "first_blood": Achievement("first_blood", "初次杀戮", "击杀第一个敌人", "◆", 50),
            "killer_100": Achievement("killer_100", "百杀者", "累计击杀100个敌人", "◇", 200),
            "killer_500": Achievement("killer_500", "千杀者", "累计击杀500个敌人", "◇", 500),
            "killer_1000": Achievement("killer_1000", "屠杀者", "累计击杀1000个敌人", "◇", 1000),
            
            # Boss相关
            "boss_slayer": Achievement("boss_slayer", "Boss猎人", "击杀任意Boss", "⬟", 300),
            "boss_master": Achievement("boss_master", "噩梦终结者", "击杀5个Boss", "⬟", 800),
            "boss_challenger": Achievement("boss_challenger", "挑战大师", "完成Boss挑战模式", "👑", 1500),
            "boss_all_clear": Achievement("boss_all_clear", "终极猎人", "击杀所有类型的Boss", "🏆", 2000),
            
            # 波数相关
            "wave_10": Achievement("wave_10", "十波生存", "存活至第10波", "⬢", 250),
            "wave_20": Achievement("wave_20", "二十波生存", "存活至第20波", "⬢", 500),
            "wave_30": Achievement("wave_30", "无穷斗士", "存活至第30波", "⬢", 1200),
            
            # 连击相关
            "combo_50": Achievement("combo_50", "连击大师", "达成50连击", "⚡", 200),
            "combo_100": Achievement("combo_100", "连击王者", "达成100连击", "⚡", 500),
            
            # 伤害相关
            "damage_1000": Achievement("damage_1000", "破坏者", "单次伤害超过1000", "💥", 200),
            "damage_5000": Achievement("damage_5000", "毁灭者", "单次伤害超过5000", "💥", 600),
            
            # 完美游戏
            "perfect_run": Achievement("perfect_run", "完美者", "无伤完成一局游戏", "✓", 1000),
            "no_heal": Achievement("no_heal", "坚定的战士", "全程不使用医疗包完成一局", "❤", 700),
            
            # 收集相关
            "collector": Achievement("collector", "收藏家", "集齐所有升级卡牌类型", "📚", 800),
            "rich": Achievement("rich", "暴富者", "游戏中获得100000分", "💰", 600),
            
            # 速度相关
            "speedrun": Achievement("speedrun", "闪电战士", "3分钟内获得50000分", "⚡", 400),
            "fast_clear": Achievement("fast_clear", "急速前进", "2分钟内到达第10波", "🔥", 350),
            
            # 编队相关
            "drone_master": Achievement("drone_master", "编队指挥官", "拥有4个僚机并完成一局", "🎯", 500),
            "drone_squad": Achievement("drone_squad", "天空统治者", "同时拥有3个僚机存活", "🎯", 400),
            
            # 特殊成就
            "first_boss": Achievement("first_boss", "首领战胜者", "完成第一次Boss战", "👑", 250),
            "survivor": Achievement("survivor", "幸存者", "完成任何一局游戏", "🛡", 100),
        }
    
    def check_achievements(self, player):
        """检查是否解锁成就"""
        unlocked = []
        
        # 击杀数检查
        if self.stats["total_kills"] >= 1:
            if self.achievements["first_blood"].unlock():
                unlocked.append("first_blood")
        if self.stats["total_kills"] >= 100:
            if self.achievements["killer_100"].unlock():
                unlocked.append("killer_100")
        if self.stats["total_kills"] >= 500:
            if self.achievements["killer_500"].unlock():
                unlocked.append("killer_500")
        if self.stats["total_kills"] >= 1000:
            if self.achievements["killer_1000"].unlock():
                unlocked.append("killer_1000")
        
        # Boss击杀检查
        if self.stats["bosses_killed"] >= 1:
            if self.achievements["boss_slayer"].unlock():
                unlocked.append("boss_slayer")
            if self.achievements["first_boss"].unlock():
                unlocked.append("first_boss")
        if self.stats["bosses_killed"] >= 5:
            if self.achievements["boss_master"].unlock():
                unlocked.append("boss_master")
        
        # 波数检查
        if self.stats["max_wave"] >= 10:
            if self.achievements["wave_10"].unlock():
                unlocked.append("wave_10")
        if self.stats["max_wave"] >= 20:
            if self.achievements["wave_20"].unlock():
                unlocked.append("wave_20")
        if self.stats["max_wave"] >= 30:
            if self.achievements["wave_30"].unlock():
                unlocked.append("wave_30")
        
        # 连击检查
        if self.stats["max_combo"] >= 50:
            if self.achievements["combo_50"].unlock():
                unlocked.append("combo_50")
        if self.stats["max_combo"] >= 100:
            if self.achievements["combo_100"].unlock():
                unlocked.append("combo_100")
        
        # 伤害检查
        if self.stats["total_damage"] >= 1000:
            if self.achievements["damage_1000"].unlock():
                unlocked.append("damage_1000")
        if self.stats["total_damage"] >= 5000:
            if self.achievements["damage_5000"].unlock():
                unlocked.append("damage_5000")
        
        # 僚机检查
        if hasattr(player, 'wingman_squadron') and player.wingman_squadron:
            if len(player.wingman_squadron.wingmen) >= 4:
                if self.achievements["drone_master"].unlock():
                    unlocked.append("drone_master")
            if len(player.wingman_squadron.wingmen) >= 3:
                if self.achievements["drone_squad"].unlock():
                    unlocked.append("drone_squad")
        
        # 特殊成就标记（需要在游戏结束时检查）
        if hasattr(self, 'temp_perfect_run') and self.temp_perfect_run:
            if self.achievements["perfect_run"].unlock():
                unlocked.append("perfect_run")
        
        if hasattr(self, 'temp_no_heal') and self.temp_no_heal:
            if self.achievements["no_heal"].unlock():
                unlocked.append("no_heal")
        
        if hasattr(self, 'temp_survivor') and self.temp_survivor:
            if self.achievements["survivor"].unlock():
                unlocked.append("survivor")
        
        return unlocked
    
    def unlock_achievement(self, achievement_id):
        """手动解锁成就"""
        if achievement_id in self.achievements:
            return self.achievements[achievement_id].unlock()
        return False
    
    def add_kill(self, count=1):
        """记录击杀"""
        self.stats["total_kills"] += count
    
    def add_damage(self, damage):
        """记录伤害"""
        self.stats["total_damage"] += damage
    
    def update_max_wave(self, wave):
        """更新最高波数"""
        self.stats["max_wave"] = max(self.stats["max_wave"], wave)
    
    def get_total_reward(self):
        """获取所有已解锁成就的总奖励"""
        return sum(ach.reward for ach in self.achievements.values() if ach.unlocked)
    
    def get_unlocked_achievements(self):
        """获取所有已解锁的成就"""
        return [ach for ach in self.achievements.values() if ach.unlocked]
    
    def update_achievements(self, player, wave=None):
        """在游戏中实时更新成就状态"""
        if player is None:
            return []
        
        # 更新波数
        if wave is not None:
            self.update_max_wave(wave)
        
        # 检查所有成就条件
        return self.check_achievements(player)
    
    def add_boss_kill(self):
        """记录Boss击杀"""
        self.stats["bosses_killed"] += 1
    
    def save_to_file(self, filename="achievements.json"):
        """将成就数据保存到JSON文件"""
        import json
        import os
        
        # 准备要保存的数据
        data = {
            "stats": self.stats,
            "unlocked": [ach_id for ach_id, ach in self.achievements.items() if ach.unlocked]
        }
        
        try:
            # 确保目录存在
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            log_info(f"成就数据已保存到 {filename}")
            return True
        except Exception as e:
            log_error(f"保存成就数据失败: {e}")
            return False
    
    def load_from_file(self, filename="achievements.json"):
        """从JSON文件加载成就数据"""
        import json
        import os
        
        if not os.path.exists(filename):
            log_info(f"成就文件不存在: {filename}")
            return False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 恢复统计数据
            if "stats" in data:
                self.stats.update(data["stats"])
            
            # 恢复已解锁成就
            if "unlocked" in data:
                for ach_id in data["unlocked"]:
                    if ach_id in self.achievements:
                        self.achievements[ach_id].unlocked = True
            
            log_info(f"成就数据已从 {filename} 加载")
            return True
        except Exception as e:
            log_error(f"加载成就数据失败: {e}")
            return False

# ==============================================================================
#   僚机创建函数（供增益卡牌调用）
# ==============================================================================

def add_wingmen_to_player(player, count=2):
    """为玩家添加僚机
    
    :param player: 玩家对象
    :param count: 要添加的僚机数量
    :return: 实际添加的僚机数量
    """
    print(f"[DEBUG] add_wingmen_to_player 开始, count={count}")
    if not hasattr(player, 'wingman_squadron') or player.wingman_squadron is None:
        # 如果编队系统还没初始化，先初始化
        try:
            from wingman import WingmanSquadron
            print("[DEBUG] 初始化 wingman_squadron")
            player.wingman_squadron = WingmanSquadron(player, max_wingmen=player.max_wingmen)
            print("[DEBUG] wingman_squadron 初始化完成")
        except Exception as e:
            print(f"[DEBUG] 导入wingman失败: {e}")
            import traceback
            traceback.print_exc()
            log_error("无法导入wingman模块")
            return 0
    
    # 获取涂装配置（直接从 customization 模块读取文件）
    equipped_wingman_themes = {}
    try:
        import json
        import os
        save_file = "customization.json"
        if os.path.exists(save_file):
            with open(save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                equipped_wingman_themes = data.get("equipped_wingman_themes", {})
        print(f"[DEBUG] 获取僚机涂装配置成功: {equipped_wingman_themes}")
    except Exception as e:
        print(f"[DEBUG] 获取涂装配置失败: {e}")
    
    added = 0
    for _ in range(count):
        # 为僚机创建副武器，使用玩家当前选中的武器
        print(f"[DEBUG] 创建僚机武器...")
        wingman_weapon = create_wingman_weapon(player)
        
        # 获取当前槽位的涂装
        slot_index = len(player.wingman_squadron.wingmen)
        paint_theme_id = equipped_wingman_themes.get(f"slot_{slot_index}", "default")
        print(f"[DEBUG] 僚机涂装: slot_{slot_index} -> {paint_theme_id}")
        
        # 添加带武器的僚机
        print(f"[DEBUG] 添加僚机...")
        if player.wingman_squadron.add_wingman(wingman_weapon, paint_theme_id=paint_theme_id):
            added += 1
            player.wingman_count += 1
            print(f"[DEBUG] 僚机添加成功, added={added}")
        else:
            print(f"[DEBUG] 僚机添加失败，达到上限")
            break  # 达到上限
    
    print(f"[DEBUG] add_wingmen_to_player 完成, added={added}")
    log_info(f"玩家获得 {added} 个僚机，当前僚机数: {player.wingman_count}")
    return added


def add_weapon_card(player, weapon_type):
    """为玩家添加武器卡牌，升级现有武器或添加新武器
    
    :param player: 玩家对象
    :param weapon_type: 武器类型字符串 (如 'cannon', 'beam' 等)
    :return: 是否成功
    """
    if not hasattr(player, 'weapon_slots') or not player.weapon_slots:
        return False
    
    try:
        from systems import WeaponSystem
        
        # 检查玩家是否已有该武器
        weapon_found = False
        for i, slot in enumerate(player.weapon_slots):
            if slot and slot.get('type') == weapon_type:
                # 升级现有武器
                slot['stars'] = min(slot.get('stars', 1) + 1, 10)
                # 重新初始化武器系统以应用等级变化
                player.weapon_slots[i] = WeaponSystem(slot)
                weapon_found = True
                log_info(f"玩家的 {weapon_type} 武器升级到星数 {slot['stars']}")
                break
        
        if not weapon_found:
            # 添加新武器到空槽位
            from config import WEAPON_TYPES
            
            if weapon_type not in WEAPON_TYPES:
                log_error(f"未知的武器类型: {weapon_type}")
                return False
            
            weapon_data = {
                'type': weapon_type,
                'stars': 1,
                'name': WEAPON_TYPES[weapon_type]['name']
            }
            
            # 寻找空槽位
            empty_slot_found = False
            for i, slot in enumerate(player.weapon_slots):
                if not slot:
                    player.weapon_slots[i] = WeaponSystem(weapon_data)
                    empty_slot_found = True
                    log_info(f"玩家在槽位 {i} 获得新武器: {weapon_type}")
                    break
            
            if not empty_slot_found:
                # 没有空槽位，替换当前槽位的武器
                player.weapon_slots[player.current_slot] = WeaponSystem(weapon_data)
                log_info(f"玩家用新武器 {weapon_type} 替换了当前槽位")
        
        return True
    except Exception as e:
        log_error(f"添加武器卡牌失败: {e}")
        return False


def create_wingman_weapon(player=None):
    """创建僚机专用的副武器
    
    :param player: 玩家对象，如果提供则复制玩家当前武器
    :return: WeaponSystem对象
    """
    from systems import WeaponSystem
    
    # 如果提供了玩家对象，尝试复制玩家的当前武器
    if player and hasattr(player, 'weapon_slots') and player.weapon_slots:
        try:
            # 获取玩家当前选中的武器
            current_weapon = player.weapon_slots[player.current_slot]
            
            if current_weapon:
                # 深拷贝玩家的武器配置
                import copy
                wingman_weapon = copy.deepcopy(current_weapon)
                # 降低僚机武器的冷却时间（减半）
                if hasattr(wingman_weapon, 'cooldown_max'):
                    wingman_weapon.cooldown_max = max(1, wingman_weapon.cooldown_max // 2)
                return wingman_weapon
        except (IndexError, AttributeError) as e:
            log_error(f"获取玩家武器失败: {e}，使用默认武器")
    
    # 如果没有玩家对象或玩家没有武器，使用基础炮台武器
    weapon_data = {
        'type': 'cannon',
        'stars': 1,
        'name': '副炮'
    }
    
    try:
        weapon = WeaponSystem(weapon_data)
        weapon.name = '副炮'
        # 降低默认僚机武器的冷却时间
        if hasattr(weapon, 'cooldown_max'):
            weapon.cooldown_max = max(1, weapon.cooldown_max // 2)
        return weapon
    except Exception as e:
        log_error(f"创建僚机武器失败: {e}")
        return None

# ==============================================================================
#   全新三层卡牌系统 - 基础定义
# ==============================================================================

# 卡牌流派定义
CARD_ARCHETYPES = {
    "barrage": {"name": "弹幕流", "color": (255, 100, 100), "icon": "◆"},
    "sniper": {"name": "狙击流", "color": (100, 200, 255), "icon": "◇"},
    "control": {"name": "控制流", "color": (150, 100, 255), "icon": "◈"},
    "summon": {"name": "召唤流", "color": (100, 255, 150), "icon": "◉"}
}

# 程序化生成算法模板
def generate_card_pattern(seed, pattern_type="wave"):
    """程序化生成卡牌视觉图案
    
    Args:
        seed: 随机种子（卡牌ID的哈希值）
        pattern_type: 图案类型 (wave, spiral, geometric, fractal)
    
    Returns:
        dict: 包含图案参数的字典
    """
    random.seed(seed)
    
    if pattern_type == "wave":
        return {
            "type": "wave",
            "frequency": random.uniform(2.0, 8.0),
            "amplitude": random.uniform(5.0, 20.0),
            "phase": random.uniform(0, 2 * math.pi),
            "formula": f"y = {random.uniform(5, 20):.1f} * sin({random.uniform(2, 8):.1f}x + {random.uniform(0, 6.28):.2f})"
        }
    elif pattern_type == "spiral":
        return {
            "type": "spiral",
            "rotation": random.uniform(0.1, 0.5),
            "expansion": random.uniform(1.0, 3.0),
            "arms": random.randint(2, 6),
            "formula": f"r = {random.uniform(1, 3):.1f}θ, arms={random.randint(2, 6)}"
        }
    elif pattern_type == "geometric":
        sides = random.choice([3, 4, 5, 6, 8])
        return {
            "type": "geometric",
            "sides": sides,
            "scale": random.uniform(0.8, 1.5),
            "rotation": random.uniform(0, 360),
            "formula": f"n-gon: n={sides}, scale={random.uniform(0.8, 1.5):.2f}"
        }
    else:  # fractal
        return {
            "type": "fractal",
            "iterations": random.randint(3, 6),
            "scale_factor": random.uniform(0.4, 0.7),
            "angle": random.uniform(15, 45),
            "formula": f"fractal: iter={random.randint(3, 6)}, scale={random.uniform(0.4, 0.7):.2f}"
        }

# ==============================================================================
#   第一层：基础卡牌 (16种)
# ==============================================================================
BASE_CARDS = {
    # ======== 攻击类 (4种) ========
    "linear_trajectory": {
        "name": "线性弹道",
        "category": "attack",
        "archetype": "barrage",
        "desc": "发射直线高速弹幕",
        "base_effect": {"bullet_count": 1, "damage_mult": 0.0, "speed_mult": 0.0},
        "visual_seed": 1001,
        "pattern": "wave",
        "rarity": 1,
        "upgrades": [
            {"level": 2, "effect": {"bullet_count": 1}, "desc": "弹幕 +1"},
            {"level": 3, "effect": {"damage_mult": 0.3}, "desc": "伤害 +30%"}
        ]
    },
    "split_shot": {
        "name": "分裂射击",
        "category": "attack",
        "archetype": "barrage",
        "desc": "子弹击中后分裂成多发",
        "base_effect": {"split_count": 2, "split_damage": 0.5},
        "visual_seed": 1002,
        "pattern": "spiral",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"split_count": 1}, "desc": "分裂数 +1"},
            {"level": 3, "effect": {"split_damage": 0.2}, "desc": "分裂伤害 +20%"}
        ]
    },
    "precision_beam": {
        "name": "精准光束",
        "category": "attack",
        "archetype": "sniper",
        "desc": "单发高伤穿透光束",
        "base_effect": {"damage_mult": 2.5, "pierce": 3, "fire_rate": 0.5},
        "visual_seed": 1003,
        "pattern": "geometric",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"pierce": 2}, "desc": "穿透 +2"},
            {"level": 3, "effect": {"damage_mult": 1.0}, "desc": "伤害 +40%"}
        ]
    },
    "explosive_round": {
        "name": "爆裂弹头",
        "category": "attack",
        "archetype": "barrage",
        "desc": "爆炸范围伤害",
        "base_effect": {"explosion_radius": 80, "explosion_mult": 0.6},
        "visual_seed": 1004,
        "pattern": "fractal",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"explosion_radius": 40}, "desc": "范围 +50%"},
            {"level": 3, "effect": {"explosion_mult": 0.3}, "desc": "爆炸伤害 +30%"}
        ]
    },
    
    # ======== 防御类 (4种) ========
    "energy_shield": {
        "name": "能量护盾",
        "category": "defense",
        "archetype": "control",
        "desc": "吸收伤害的护盾",
        "base_effect": {"shield_amount": 50, "shield_regen": 2},
        "visual_seed": 2001,
        "pattern": "wave",
        "rarity": 1,
        "upgrades": [
            {"level": 2, "effect": {"shield_amount": 30}, "desc": "护盾值 +30"},
            {"level": 3, "effect": {"shield_regen": 2}, "desc": "回复速度 +2"}
        ]
    },
    "phase_dodge": {
        "name": "相位闪避",
        "category": "defense",
        "archetype": "control",
        "desc": "概率完全闪避伤害",
        "base_effect": {"dodge_chance": 0.15},
        "visual_seed": 2002,
        "pattern": "spiral",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"dodge_chance": 0.10}, "desc": "闪避率 +10%"},
            {"level": 3, "effect": {"dodge_chance": 0.10}, "desc": "闪避率 +10%"}
        ]
    },
    "armor_plating": {
        "name": "装甲镀层",
        "category": "defense",
        "archetype": "control",
        "desc": "减少受到的伤害",
        "base_effect": {"damage_reduction": 0.2, "max_hp_bonus": 50},
        "visual_seed": 2003,
        "pattern": "geometric",
        "rarity": 1,
        "upgrades": [
            {"level": 2, "effect": {"damage_reduction": 0.10}, "desc": "减伤 +10%"},
            {"level": 3, "effect": {"max_hp_bonus": 50}, "desc": "生命 +50"}
        ]
    },
    "regeneration": {
        "name": "生命再生",
        "category": "defense",
        "archetype": "control",
        "desc": "持续恢复生命",
        "base_effect": {"regen_rate": 5, "regen_interval": 300},
        "visual_seed": 2004,
        "pattern": "fractal",
        "rarity": 1,
        "upgrades": [
            {"level": 2, "effect": {"regen_rate": 3}, "desc": "回复量 +3"},
            {"level": 3, "effect": {"regen_interval": -100}, "desc": "间隔缩短"}
        ]
    },
    
    # ======== 特殊类 (4种) ========
    "gravity_field": {
        "name": "引力场",
        "category": "special",
        "archetype": "control",
        "desc": "减速并吸引敌人",
        "base_effect": {"slow_mult": 0.4, "pull_strength": 2.0, "radius": 150},
        "visual_seed": 3001,
        "pattern": "spiral",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"slow_mult": 0.2}, "desc": "减速增强"},
            {"level": 3, "effect": {"radius": 70}, "desc": "范围 +70"}
        ]
    },
    "time_dilation": {
        "name": "时间膨胀",
        "category": "special",
        "archetype": "control",
        "desc": "减缓敌人移动和攻击",
        "base_effect": {"slow_area": 200, "time_factor": 0.5},
        "visual_seed": 3002,
        "pattern": "wave",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"time_factor": -0.2}, "desc": "减速更强"},
            {"level": 3, "effect": {"slow_area": 100}, "desc": "范围增大"}
        ]
    },
    "chain_lightning": {
        "name": "连锁闪电",
        "category": "special",
        "archetype": "barrage",
        "desc": "攻击跳跃至多个敌人",
        "base_effect": {"chain_count": 3, "chain_damage": 0.6},
        "visual_seed": 3003,
        "pattern": "fractal",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"chain_count": 2}, "desc": "跳跃 +2"},
            {"level": 3, "effect": {"chain_damage": 0.2}, "desc": "链伤 +20%"}
        ]
    },
    "frost_nova": {
        "name": "冰霜新星",
        "category": "special",
        "archetype": "control",
        "desc": "冻结区域内所有敌人",
        "base_effect": {"freeze_duration": 120, "freeze_radius": 100},
        "visual_seed": 3004,
        "pattern": "geometric",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"freeze_duration": 60}, "desc": "冻结时长 +50%"},
            {"level": 3, "effect": {"freeze_radius": 50}, "desc": "范围 +50"}
        ]
    },
    
    # ======== 系统类 (4种) ========
    "chaos_injection": {
        "name": "混沌注入",
        "category": "system",
        "archetype": "barrage",
        "desc": "随机触发强力效果",
        "base_effect": {"chaos_chance": 0.2, "chaos_mult": 2.0},
        "visual_seed": 4001,
        "pattern": "fractal",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"chaos_chance": 0.1}, "desc": "触发率 +10%"},
            {"level": 3, "effect": {"chaos_mult": 1.0}, "desc": "效果倍率 +1.0"}
        ]
    },
    "auto_turret": {
        "name": "自动炮塔",
        "category": "system",
        "archetype": "summon",
        "desc": "在屏幕固定位置部署防御炮塔",
        "base_effect": {"turret_count": 2, "turret_damage": 0.6},
        "visual_seed": 4002,
        "pattern": "geometric",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"turret_count": 2}, "desc": "炮塔数 2→4"},
            {"level": 3, "effect": {"turret_damage": 0.4}, "desc": "炮塔伤害 ×1.0"}
        ]
    },
    "drone_swarm": {
        "name": "无人机群",
        "category": "system",
        "archetype": "summon",
        "desc": "召唤跟随无人机",
        "base_effect": {"drone_count": 2, "drone_damage": 0.4},
        "visual_seed": 4003,
        "pattern": "spiral",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"drone_count": 1}, "desc": "无人机 +1"},
            {"level": 3, "effect": {"drone_damage": 0.2}, "desc": "伤害 +20%"}
        ]
    },
    "resource_magnet": {
        "name": "资源磁场",
        "category": "system",
        "archetype": "summon",
        "desc": "自动吸引经验和物品",
        "base_effect": {"magnet_range": 200, "xp_mult": 1.2},
        "visual_seed": 4004,
        "pattern": "wave",
        "rarity": 1,
        "upgrades": [
            {"level": 2, "effect": {"magnet_range": 100}, "desc": "范围 +100"},
            {"level": 3, "effect": {"xp_mult": 0.3}, "desc": "经验 +30%"}
        ]
    }
}

# ==============================================================================
#   第二层：参数卡牌（修饰器）
# ==============================================================================
MODIFIER_CARDS = {
    # ======== 数值类修饰器 ========
    "power_boost": {
        "name": "强度增幅",
        "type": "numeric",
        "desc": "伤害 +25%",
        "effect": {"damage_mult": 0.25},
        "rarity": 1,
        "visual_seed": 5001
    },
    "range_extend": {
        "name": "范围拓展",
        "type": "numeric",
        "desc": "作用范围 +40%",
        "effect": {"range_mult": 1.4},
        "rarity": 1,
        "visual_seed": 5002
    },
    "speed_up": {
        "name": "速度提升",
        "type": "numeric",
        "desc": "弹速/频率 +30%",
        "effect": {"speed_mult": 0.3},
        "rarity": 1,
        "visual_seed": 5003
    },
    "duration_extend": {
        "name": "持续延长",
        "type": "numeric",
        "desc": "效果时长 +50%",
        "effect": {"duration_mult": 1.5},
        "rarity": 1,
        "visual_seed": 5004
    },
    
    # ======== 特性类修饰器 ========
    "homing_addon": {
        "name": "追踪模块",
        "type": "trait",
        "desc": "子弹自动追踪敌人",
        "effect": {"homing": True, "homing_strength": 0.5},
        "rarity": 2,
        "visual_seed": 5101
    },
    "explosive_addon": {
        "name": "爆炸模块",
        "type": "trait",
        "desc": "添加爆炸效果",
        "effect": {"explosion": True, "explosion_radius": 60},
        "rarity": 2,
        "visual_seed": 5102
    },
    "pierce_addon": {
        "name": "穿透模块",
        "type": "trait",
        "desc": "添加穿透能力",
        "effect": {"pierce": 2},
        "rarity": 2,
        "visual_seed": 5103
    },
    "lifesteal_addon": {
        "name": "吸血模块",
        "type": "trait",
        "desc": "伤害转化为治疗",
        "effect": {"lifesteal": 0.15},
        "rarity": 2,
        "visual_seed": 5104
    },
    "chain_addon": {
        "name": "连锁模块",
        "type": "trait",
        "desc": "添加连锁跳跃",
        "effect": {"chain": True, "chain_targets": 2},
        "rarity": 2,
        "visual_seed": 5105
    },
    "crit_addon": {
        "name": "暴击模块",
        "type": "trait",
        "desc": "暴击率 +20%",
        "effect": {"crit_chance": 0.2, "crit_mult": 1.5},
        "rarity": 2,
        "visual_seed": 5106
    }
}

# ==============================================================================
#   第三层：协同卡牌（组合规则）
# ==============================================================================
SYNERGY_RULES = {
    # ======== 弹幕流协同 ========
    "barrage_master": {
        "name": "弹幕大师",
        "desc": "子弹数量 ×2，分裂次数 +1",
        "trigger": {
            "archetype": "barrage",
            "count": 3,
            "cards": []  # 任意3张弹幕流卡牌
        },
        "effect": {"bullet_count_mult": 2.0, "split_level": 1},
        "visual": {"color": (255, 100, 100), "particle_effect": "barrage_burst"},
        "rarity": 3
    },
    "barrage_overlord": {
        "name": "弹幕霸主",
        "desc": "子弹数量 ×3，全屏弹幕",
        "trigger": {
            "archetype": "barrage",
            "count": 5,
            "cards": []
        },
        "effect": {"bullet_count_mult": 3.0, "spread_angle": 360},
        "visual": {"color": (255, 50, 50), "particle_effect": "bullet_storm"},
        "rarity": 4
    },
    
    # ======== 狙击流协同 ========
    "sniper_elite": {
        "name": "精英狙击",
        "desc": "穿透 +5，伤害 +80%",
        "trigger": {
            "archetype": "sniper",
            "count": 3,
            "cards": []
        },
        "effect": {"pierce_bonus": 5, "damage_mult": 1.8},
        "visual": {"color": (100, 200, 255), "particle_effect": "sniper_focus"},
        "rarity": 3
    },
    "one_shot_kill": {
        "name": "一击必杀",
        "desc": "单次伤害 ×5，暴击率 +50%",
        "trigger": {
            "archetype": "sniper",
            "count": 4,
            "cards": ["precision_beam"]
        },
        "effect": {"damage_mult": 5.0, "crit_chance": 0.5},
        "visual": {"color": (50, 150, 255), "particle_effect": "critical_strike"},
        "rarity": 4
    },
    
    # ======== 控制流协同 ========
    "crowd_control": {
        "name": "群体控制",
        "desc": "控制范围 +100%，持续时间 +50%",
        "trigger": {
            "archetype": "control",
            "count": 3,
            "cards": []
        },
        "effect": {"control_range_mult": 2.0, "duration_mult": 1.5},
        "visual": {"color": (150, 100, 255), "particle_effect": "control_aura"},
        "rarity": 3
    },
    "time_freeze": {
        "name": "时空冻结",
        "desc": "全屏减速80%，持续5秒",
        "trigger": {
            "archetype": "control",
            "count": 4,
            "cards": ["time_dilation", "frost_nova"]
        },
        "effect": {"global_slow": 0.8, "slow_duration": 300},
        "visual": {"color": (100, 100, 255), "particle_effect": "time_stop"},
        "rarity": 4
    },
    
    # ======== 召唤流协同 ========
    "summoner": {
        "name": "召唤师",
        "desc": "召唤物数量 +2，伤害 +50%",
        "trigger": {
            "archetype": "summon",
            "count": 3,
            "cards": []
        },
        "effect": {"summon_count": 2, "summon_damage_mult": 1.5},
        "visual": {"color": (100, 255, 150), "particle_effect": "summon_gate"},
        "rarity": 3
    },
    "army_commander": {
        "name": "军团指挥",
        "desc": "召唤物数量 ×2，智能协同攻击",
        "trigger": {
            "archetype": "summon",
            "count": 5,
            "cards": []
        },
        "effect": {"summon_count_mult": 2.0, "summon_ai": "coordinated"},
        "visual": {"color": (50, 255, 100), "particle_effect": "army_formation"},
        "rarity": 4
    },
    
    # ======== 混合协同 ========
    "explosive_barrage": {
        "name": "爆裂弹幕",
        "desc": "所有子弹附带爆炸",
        "trigger": {
            "cards": ["linear_trajectory", "explosive_round"],
            "modifiers": ["explosive_addon"]
        },
        "effect": {"all_bullets_explode": True, "explosion_radius": 80},
        "visual": {"color": (255, 150, 0), "particle_effect": "explosive_trail"},
        "rarity": 3
    },
    "piercing_laser": {
        "name": "穿刺激光",
        "desc": "光束无限穿透，击中减速",
        "trigger": {
            "cards": ["precision_beam"],
            "modifiers": ["pierce_addon"]
        },
        "effect": {"infinite_pierce": True, "slow_on_hit": 0.5},
        "visual": {"color": (0, 255, 255), "particle_effect": "laser_trail"},
        "rarity": 3
    }
}

# ==============================================================================
#   卡牌实例类
# ==============================================================================
class Card:
    """卡牌实例，可以是基础卡、参数卡或协同卡"""
    
    def __init__(self, card_id, card_type="base"):
        self.id = card_id
        self.type = card_type  # "base", "modifier", "synergy"
        self.level = 1
        self.modifiers = []  # 附加的参数卡列表
        
        # 根据类型加载数据
        if card_type == "base":
            self.data = BASE_CARDS.get(card_id, {})
        elif card_type == "modifier":
            self.data = MODIFIER_CARDS.get(card_id, {})
        elif card_type == "synergy":
            self.data = SYNERGY_RULES.get(card_id, {})
        else:
            self.data = {}
        
        # 生成视觉图案
        self.pattern = generate_card_pattern(
            self.data.get("visual_seed", hash(card_id)),
            self.data.get("pattern", "wave")
        )
        
        # 计算最终效果
        self.final_effect = self._calculate_effect()
    
    def _calculate_effect(self):
        """计算卡牌的最终效果（包括升级和参数加成）"""
        effect = self.data.get("base_effect", {}).copy()
        
        # 应用升级效果
        if self.type == "base" and self.level > 1:
            upgrades = self.data.get("upgrades", [])
            for upgrade in upgrades:
                if upgrade["level"] <= self.level:
                    for key, value in upgrade["effect"].items():
                        if key in effect:
                            if isinstance(value, (int, float)):
                                effect[key] += value
                            else:
                                effect[key] = value
                        else:
                            effect[key] = value
        
        # 应用参数卡效果
        for mod_id in self.modifiers:
            if mod_id in MODIFIER_CARDS:
                mod_effect = MODIFIER_CARDS[mod_id]["effect"]
                for key, value in mod_effect.items():
                    if key == "damage_mult" or key == "speed_mult":
                        # damage_mult和speed_mult使用加法(参数卡的值是增量)
                        effect[key] = effect.get(key, 0) + value
                    elif key == "range_mult":
                        # range_mult特殊处理:增强所有范围相关属性
                        for range_key in ["radius", "explosion_radius", "freeze_radius", "magnet_range", "slow_area"]:
                            if range_key in effect:
                                effect[range_key] *= value
                    elif key.endswith("_mult") and key in effect:
                        # 其他倍率属性相乘
                        effect[key] *= value
                    elif key.endswith("_mult"):
                        # 尝试匹配基础属性
                        base_key = key.replace("_mult", "")
                        if base_key in effect:
                            effect[base_key] *= value
                    else:
                        # 非倍率属性累加
                        effect[key] = effect.get(key, 0) + value
        
        return effect
    
    def add_modifier(self, modifier_id):
        """添加参数卡"""
        if len(self.modifiers) < 3 and modifier_id in MODIFIER_CARDS:
            self.modifiers.append(modifier_id)
            self.final_effect = self._calculate_effect()
            return True
        return False
    
    def upgrade(self):
        """升级卡牌"""
        if self.type == "base" and self.level < 3:
            self.level += 1
            self.final_effect = self._calculate_effect()
            return True
        return False
    
    def get_display_name(self):
        """获取显示名称（含等级）"""
        name = self.data.get("name", self.id)
        if self.type == "base" and self.level > 1:
            return f"{name} Lv.{self.level}"
        return name
    
    def get_formula(self):
        """获取数学指纹"""
        return self.pattern.get("formula", "未定义")

# ==============================================================================
#   升级管理类（重写）
# ==============================================================================
class UpgradeManager:
    """管理新卡牌系统的升级、选择、协同检测"""
    
    def __init__(self):
        self.owned_cards = {}  # {card_id: Card对象}
        self.active_synergies = []  # 当前激活的协同列表
        self.upgrade_choice = None  # 当前选择界面的 3 个选项
        self.upgrade_choice_index = 0
        self.level_up_ready = False
        self._player_ref = None
        
        # 流派统计
        self.archetype_counts = {
            "barrage": 0,
            "sniper": 0,
            "control": 0,
            "summon": 0
        }
        
    def set_player_ref(self, player):
        """设置对玩家对象的引用"""
        self._player_ref = player
    
    def add_card(self, card_id, card_type="base"):
        """添加新卡牌到卡组"""
        if card_id in self.owned_cards:
            # 已有卡牌，尝试升级
            return self.owned_cards[card_id].upgrade()
        else:
            # 新卡牌
            card = Card(card_id, card_type)
            self.owned_cards[card_id] = card
            
            # 更新流派统计
            if card_type == "base":
                archetype = card.data.get("archetype", "")
                if archetype in self.archetype_counts:
                    self.archetype_counts[archetype] += 1
            
            # 检查协同触发
            self._check_synergies()
            
            # 应用卡牌效果到玩家
            if self._player_ref:
                self._apply_card_to_player(card)
            
            return True
    
    def _apply_card_to_player(self, card):
        """将卡牌效果应用到玩家"""
        player = self._player_ref
        effect = card.final_effect
        
        # 攻击类效果
        if "bullet_count" in effect:
            player.bullet_count = getattr(player, "bullet_count", 1) + effect["bullet_count"]
        if "bullet_count_mult" in effect:
            player.bullet_count = int(getattr(player, "bullet_count", 1) * effect["bullet_count_mult"])
        if "damage_mult" in effect:
            player.damage *= (1.0 + effect["damage_mult"])
        if "pierce" in effect:
            player.piercing = getattr(player, "piercing", 0) + effect["pierce"]
        if "pierce_bonus" in effect:
            player.piercing = getattr(player, "piercing", 0) + effect["pierce_bonus"]
        if "infinite_pierce" in effect and effect["infinite_pierce"]:
            player.piercing = 999
        if "split_count" in effect:
            # split_count取最大值(多张卡以最大分裂数为准)
            player.split_count = max(getattr(player, "split_count", 0), effect["split_count"])
        if "split_damage" in effect:
            # split_damage累加(多张卡叠加伤害)
            player.split_damage = getattr(player, "split_damage", 0) + effect["split_damage"]
        if "split_level" in effect:
            player.split_level = getattr(player, "split_level", 0) + effect["split_level"]
        if "fire_rate" in effect:
            player.delay = int(player.delay / effect["fire_rate"])  # fire_rate=0.5表示射速减半,delay要翻倍
        if "speed_mult" in effect:
            player.bullet_speed = getattr(player, "bullet_speed", 10) * (1.0 + effect["speed_mult"])
        if "explosion_radius" in effect:
            player.has_area_dmg = True
            player.explosion_radius = max(getattr(player, "explosion_radius", 0), effect["explosion_radius"])
        if "explosion_mult" in effect:
            player.explosion_mult = getattr(player, "explosion_mult", 0.0) + effect["explosion_mult"]
        if "explosion" in effect and effect["explosion"]:
            player.has_area_dmg = True
            explosion_radius = effect.get("explosion_radius", 60)
            player.explosion_radius = max(getattr(player, "explosion_radius", 0), explosion_radius)
        if "all_bullets_explode" in effect and effect["all_bullets_explode"]:
            player.has_area_dmg = True
            player.explosion_radius = effect.get("explosion_radius", 80)
        
        # 防御类效果
        if "shield_amount" in effect:
            shield_add = effect["shield_amount"]
            player.shield = getattr(player, "shield", 0) + shield_add
            player.max_shield = getattr(player, "max_shield", 0) + shield_add
        if "shield_regen" in effect:
            player.shield_regen = getattr(player, "shield_regen", 0) + effect["shield_regen"]
            player.has_shield_regen = True
        if "dodge_chance" in effect:
            player.dodge_chance = getattr(player, "dodge_chance", 0) + effect["dodge_chance"]
        if "damage_reduction" in effect:
            player.damage_reduction = getattr(player, "damage_reduction", 0) + effect["damage_reduction"]
        if "max_hp_bonus" in effect:
            player.max_hp += effect["max_hp_bonus"]
        if "regen_rate" in effect:
            player.has_regen = True
            player.regen_rate = getattr(player, "regen_rate", 0) + effect["regen_rate"]
            # 如果是第一次获得再生效果,初始化间隔
            if not hasattr(player, "regen_interval"):
                player.regen_interval = effect.get("regen_interval", 300)
        if "regen_interval" in effect and hasattr(player, "regen_interval"):
            # 间隔使用最小值(间隔越小回复越快)
            player.regen_interval = min(player.regen_interval, player.regen_interval + effect["regen_interval"])
        if "lifesteal" in effect:
            player.has_lifesteal = True
            player.lifesteal = getattr(player, "lifesteal", 0) + effect["lifesteal"]
        
        # 控制类效果
        if "slow_mult" in effect:
            player.has_gravity_field = True
            player.gravity_slow = getattr(player, "gravity_slow", 1.0) * effect["slow_mult"]  # 乘法叠加减速
            player.gravity_radius = max(getattr(player, "gravity_radius", 0), effect.get("radius", 150))
        if "slow_area" in effect:
            player.slow_area = effect["slow_area"]
            player.has_slow_field = True
        if "slow_on_hit" in effect:
            player.slow_on_hit = effect["slow_on_hit"]
        if "slow_duration" in effect:
            player.slow_duration = effect["slow_duration"]
        if "global_slow" in effect:
            player.has_time_field = True
            player.time_slow = effect["global_slow"]
        if "freeze_duration" in effect:
            player.has_frost = True
            player.freeze_duration = getattr(player, "freeze_duration", 0) + effect["freeze_duration"]
        if "freeze_radius" in effect:
            player.freeze_radius = max(getattr(player, "freeze_radius", 0), effect["freeze_radius"])
        if "pull_strength" in effect:
            player.pull_strength = getattr(player, "pull_strength", 0) + effect["pull_strength"]
        if "time_factor" in effect:
            # time_factor: 敌人速度因子 (1.0=正常, 0.5=50%速度)
            # base effect中是直接值，升级中是增量(通常为负数表示进一步减速)
            current = getattr(player, "time_factor", 1.0)
            # 如果已经不是1.0了（表示已有卡牌应用），则累加；否则直接赋值
            if current == 1.0:
                player.time_factor = effect["time_factor"]
            else:
                player.time_factor = current + effect["time_factor"]
        
        # 特殊效果
        if "chain_count" in effect:
            player.has_chain_lightning = True
            player.chain_count = getattr(player, "chain_count", 0) + effect["chain_count"]
            if "chain_damage" in effect:
                player.chain_damage = getattr(player, "chain_damage", 0.0) + effect["chain_damage"]
        if "chain" in effect and effect["chain"]:
            player.has_chain_lightning = True
            # 如果尚未设置chain_count，则初始化为2；否则保留已存在值
            if not hasattr(player, "chain_count"):
                player.chain_count = 2
        if "chain_targets" in effect:
            # chain_targets 表示增加的跳跃数量，累加而非覆盖
            player.chain_count = getattr(player, "chain_count", 0) + effect["chain_targets"]
        if "homing" in effect and effect["homing"]:
            player.has_homing = True
            if "homing_strength" in effect:
                player.homing_strength = getattr(player, "homing_strength", 0.0) + effect["homing_strength"]
            else:
                player.homing_strength = getattr(player, "homing_strength", 0.0) + 0.15
            print(f"[卡牌效果] 应用追踪卡牌: has_homing=True, homing_strength={player.homing_strength}")
        elif "homing_strength" in effect:
            player.homing_strength = getattr(player, "homing_strength", 0.0) + effect["homing_strength"]
            print(f"[卡牌效果] 应用追踪强度: homing_strength={player.homing_strength}")
        if "crit_chance" in effect:
            player.crit_chance = getattr(player, "crit_chance", 0) + effect["crit_chance"]
        if "crit_mult" in effect:
            # crit_mult should multiply the existing crit multiplier (keep default if absent)
            player.crit_mult = getattr(player, "crit_mult", 1.0) * effect["crit_mult"]
        if "range_mult" in effect:
            player.bullet_range = getattr(player, "bullet_range", 1000) * effect["range_mult"]
        if "duration_mult" in effect:
            if hasattr(player, "freeze_duration"):
                player.freeze_duration = int(player.freeze_duration * effect["duration_mult"])
            if hasattr(player, "slow_duration"):
                player.slow_duration = int(player.slow_duration * effect["duration_mult"])
        if "control_range_mult" in effect:
            if hasattr(player, "gravity_radius"):
                player.gravity_radius = int(player.gravity_radius * effect["control_range_mult"])
            if hasattr(player, "freeze_radius"):
                player.freeze_radius = int(player.freeze_radius * effect["control_range_mult"])
        if "spread_angle" in effect:
            player.spread_angle = effect["spread_angle"]
        
        # 召唤类效果
        if "drone_count" in effect:
            add_wingmen_to_player(player, effect["drone_count"])
        if "drone_damage" in effect:
            player.drone_damage_mult = getattr(player, "drone_damage_mult", 0.0) + effect["drone_damage"]
        if "turret_count" in effect:
            player.has_turrets = True
            player.turret_count = effect["turret_count"]
            player.turret_damage = effect.get("turret_damage", 0.6)
            # 立即生成炮塔
            if hasattr(player, 'spawn_turrets'):
                player.spawn_turrets()
        if "summon_count" in effect:
            add_wingmen_to_player(player, effect["summon_count"])
        if "summon_damage_mult" in effect:
            player.summon_damage_mult = effect["summon_damage_mult"]
        if "summon_count_mult" in effect:
            current_wingmen = len(getattr(player, "wingmen", []))
            add_wingmen_to_player(player, int(current_wingmen * (effect["summon_count_mult"] - 1)))
        if "summon_ai" in effect:
            player.summon_ai_mode = effect["summon_ai"]
        
        # 系统类效果
        if "magnet_range" in effect:
            # 吸引范围取最大值
            player.pickup_range = max(getattr(player, "pickup_range", 100), effect["magnet_range"])
        if "xp_mult" in effect:
            # 经验倍率累加增量部分(如1.2倍=基础1.0+增量0.2)
            current_mult = getattr(player, "xp_multiplier", 1.0)
            added_mult = effect["xp_mult"] - 1.0 if effect["xp_mult"] >= 1.0 else effect["xp_mult"]
            player.xp_multiplier = current_mult + added_mult
        if "chaos_chance" in effect:
            player.has_chaos = True
            # chaos_chance是概率，应该累加
            player.chaos_chance = getattr(player, "chaos_chance", 0.0) + effect["chaos_chance"]
        if "chaos_mult" in effect:
            # chaos_mult是伤害倍率，应该乘法叠加（保留默认值为1.0）
            player.chaos_mult = getattr(player, "chaos_mult", 1.0) * effect["chaos_mult"]
    
    def _check_synergies(self):
        """检查是否触发新的协同效果"""
        new_synergies = []
        
        for synergy_id, synergy_data in SYNERGY_RULES.items():
            if synergy_id in self.active_synergies:
                continue
            
            trigger = synergy_data["trigger"]
            
            # 检查流派数量触发
            if "archetype" in trigger and "count" in trigger:
                archetype = trigger["archetype"]
                required_count = trigger["count"]
                if self.archetype_counts.get(archetype, 0) >= required_count:
                    # 检查特定卡牌要求
                    specific_cards = trigger.get("cards", [])
                    if not specific_cards or all(card in self.owned_cards for card in specific_cards):
                        new_synergies.append(synergy_id)
            
            # 检查特定卡牌组合触发
            elif "cards" in trigger:
                required_cards = trigger["cards"]
                if all(card in self.owned_cards for card in required_cards):
                    # 检查参数卡要求
                    required_mods = trigger.get("modifiers", [])
                    if not required_mods or self._check_modifier_requirements(required_mods):
                        new_synergies.append(synergy_id)
        
        # 激活新协同
        for synergy_id in new_synergies:
            self._activate_synergy(synergy_id)
    
    def _check_modifier_requirements(self, required_mods):
        """检查是否满足参数卡要求"""
        for card in self.owned_cards.values():
            for mod in required_mods:
                if mod in card.modifiers:
                    return True
        return False
    
    def _activate_synergy(self, synergy_id):
        """激活协同效果"""
        if synergy_id not in SYNERGY_RULES:
            return
        
        self.active_synergies.append(synergy_id)
        synergy_data = SYNERGY_RULES[synergy_id]
        
        # 播放协同触发音效
        sound_mgr.play("achievement")
        
        # 应用协同效果
        if self._player_ref:
            effect = synergy_data["effect"]
            player = self._player_ref
            
            if "bullet_count_mult" in effect:
                player.bullet_count = int(player.bullet_count * effect["bullet_count_mult"])
            if "damage_mult" in effect:
                player.damage *= effect["damage_mult"]
            if "pierce_bonus" in effect:
                player.piercing += effect["pierce_bonus"]
            if "crit_chance" in effect:
                player.crit_chance = getattr(player, "crit_chance", 0) + effect["crit_chance"]
            if "control_range_mult" in effect:
                if hasattr(player, "gravity_radius"):
                    player.gravity_radius *= effect["control_range_mult"]
                if hasattr(player, "freeze_radius"):
                    player.freeze_radius = int(player.freeze_radius * effect["control_range_mult"])
            if "duration_mult" in effect:
                if hasattr(player, "freeze_duration"):
                    player.freeze_duration = int(player.freeze_duration * effect["duration_mult"])
                if hasattr(player, "slow_duration"):
                    player.slow_duration = int(player.slow_duration * effect["duration_mult"])
            if "summon_count" in effect:
                add_wingmen_to_player(player, effect["summon_count"])
            if "summon_count_mult" in effect:
                # 增加现有召唤物数量
                current_wingmen = len(getattr(player, "wingmen", []))
                add_wingmen_to_player(player, int(current_wingmen * (effect["summon_count_mult"] - 1)))
            if "summon_damage_mult" in effect:
                player.summon_damage_mult = effect["summon_damage_mult"]
            if "summon_ai" in effect:
                player.summon_ai_mode = effect["summon_ai"]
            if "all_bullets_explode" in effect:
                player.has_area_dmg = True
                player.explosion_radius = effect.get("explosion_radius", 80)
            if "split_level" in effect:
                # split_level 转换为增加 split_count
                player.split_count = getattr(player, "split_count", 0) + effect["split_level"]
            if "spread_angle" in effect:
                player.spread_angle = effect["spread_angle"]
            if "global_slow" in effect:
                player.has_time_field = True
                player.time_slow = effect["global_slow"]
            if "slow_duration" in effect:
                player.slow_duration = effect["slow_duration"]
            if "infinite_pierce" in effect and effect["infinite_pierce"]:
                # 无限穿透：设置穿透为一个很大的数值
                player.piercing = 999
            if "slow_on_hit" in effect:
                player.slow_on_hit = effect["slow_on_hit"]
        
        log_info(f"协同触发！【{synergy_data['name']}】: {synergy_data['desc']}")
    
    def trigger_levelup(self):
        """触发升级，生成3选1卡牌"""
        player = getattr(self, '_player_ref', None)
        if not player:
            return
        
        player_level = player.level
        
        # 根据等级调整稀有度权重
        rarity_weights = {1: 1.0, 2: 0.3, 3: 0.05}
        if player_level <= 5:
            rarity_weights = {1: 1.0, 2: 0.2, 3: 0.0}
        elif player_level <= 10:
            rarity_weights = {1: 0.7, 2: 0.5, 3: 0.1}
        elif player_level <= 15:
            rarity_weights = {1: 0.5, 2: 0.7, 3: 0.2}
        else:
            rarity_weights = {1: 0.3, 2: 0.6, 3: 0.5}
        
        # 选择3张卡牌
        selected = []
        
        for i in range(3):
            # 70%基础卡，20%参数卡，10%已有卡升级
            roll = random.random()
            
            if roll < 0.7:
                # 基础卡
                candidates = [
                    card_id for card_id, card_data in BASE_CARDS.items()
                    if card_data["rarity"] in rarity_weights
                ]
                weights = [rarity_weights.get(BASE_CARDS[c]["rarity"], 0) for c in candidates]
                if candidates:
                    card_id = random.choices(candidates, weights=weights, k=1)[0]
                    selected.append({"type": "base", "id": card_id})
            
            elif roll < 0.9:
                # 参数卡
                candidates = list(MODIFIER_CARDS.keys())
                if candidates:
                    card_id = random.choice(candidates)
                    selected.append({"type": "modifier", "id": card_id})
            
            else:
                # 升级已有卡
                upgradable = [
                    card_id for card_id, card in self.owned_cards.items()
                    if card.type == "base" and card.level < 3
                ]
                if upgradable:
                    card_id = random.choice(upgradable)
                    selected.append({"type": "upgrade", "id": card_id})
                else:
                    # 没有可升级的，给基础卡
                    candidates = list(BASE_CARDS.keys())
                    if candidates:
                        card_id = random.choice(candidates)
                        selected.append({"type": "base", "id": card_id})
        
        self.upgrade_choice = selected
        self.upgrade_choice_index = 0
        self.level_up_ready = True
        sound_mgr.play("levelup")
    
    def select_upgrade(self, choice_index):
        """玩家选择某张卡牌"""
        if not self.upgrade_choice or choice_index >= len(self.upgrade_choice):
            return False
        
        choice = self.upgrade_choice[choice_index]
        choice_type = choice["type"]
        card_id = choice["id"]
        
        if choice_type == "upgrade":
            # 升级已有卡
            if card_id in self.owned_cards:
                self.owned_cards[card_id].upgrade()
        else:
            # 添加新卡
            self.add_card(card_id, choice_type)
        
        self.upgrade_choice = None
        self.level_up_ready = False
        return True
    
    def get_build_summary(self):
        """获取构建总结"""
        return {
            "total_cards": len(self.owned_cards),
            "archetypes": self.archetype_counts.copy(),
            "synergies": len(self.active_synergies),
            "dominant_archetype": max(self.archetype_counts.items(), key=lambda x: x[1])[0] if self.archetype_counts else None
        }
    
    def reset(self):
        """重置升级管理器"""
        self.owned_cards.clear()
        self.active_synergies.clear()
        self.upgrade_choice = None
        self.upgrade_choice_index = 0
        self.level_up_ready = False
        self.archetype_counts = {k: 0 for k in self.archetype_counts}

# ==============================================================================
#   卡牌工具函数
# ==============================================================================
def get_card_info(card_id, card_type="base"):
    """获取卡牌完整信息"""
    if card_type == "base":
        return BASE_CARDS.get(card_id, None)
    elif card_type == "modifier":
        return MODIFIER_CARDS.get(card_id, None)
    elif card_type == "synergy":
        return SYNERGY_RULES.get(card_id, None)
    return None

def get_cards_by_archetype(archetype):
    """按流派获取基础卡牌列表"""
    return [
        card_id for card_id, card_data in BASE_CARDS.items()
        if card_data.get("archetype") == archetype
    ]

def get_cards_by_category(category):
    """按类别获取基础卡牌列表"""
    return [
        card_id for card_id, card_data in BASE_CARDS.items()
        if card_data.get("category") == category
    ]

# ==============================================================================
#   经验与升级系统
# ==============================================================================
class ExperienceSystem:
    """管理 XP 和等级"""
    
    def __init__(self, player):
        self.player = player
        self.xp_collected = 0  # 当前收集的 XP
        self.next_level_xp = 100  # 升级所需 XP 门槛
        self.level = 1
        self.level_ups = []  # 记录所有升级时机
        
    def add_xp(self, amount):
        """增加 XP，检查是否升级"""
        self.xp_collected += amount
        
        while self.xp_collected >= self.next_level_xp:
            self.xp_collected -= self.next_level_xp
            self.level_up()
        
        return self.level
    
    def level_up(self):
        """执行升级逻辑"""
        self.level += 1
        # 改为对数级增长 - XP需求 = 50 × (1.15 ^ (level-1))
        # 这样早期升级快，后期升级变慢，形成更自然的难度曲线
        self.next_level_xp = int(50 * (1.15 ** (self.level - 1)))
        self.level_ups.append({
            "level": self.level,
            "xp_threshold": self.next_level_xp,
            "timestamp": pygame.time.get_ticks()
        })
        
        # 触发升级选择 UI
        if hasattr(self.player, "upgrade_manager"):
            self.player.upgrade_manager.trigger_levelup()
        
        return self.level
    
    def get_progress_percent(self):
        """获取当前升级进度百分比（0-100）"""
        if self.next_level_xp == 0:
            return 0
        prev_xp = 0
        return int((self.xp_collected / self.next_level_xp) * 100)

# ==============================================================================
#   掉落物品管理（经验球）
# ==============================================================================
def create_xp_drop(pos, amount=1):
    """创建经验球掉落物体"""
    return {
        "type": "xp_orb",
        "pos": pos,
        "amount": amount,
        "color": BLUE
    }

def create_card_drop(pos, card_id, card_type="base"):
    """创建卡牌掉落物体"""
    card_info = get_card_info(card_id, card_type)
    if not card_info:
        return None
    
    rarity = card_info.get("rarity", 1)
    return {
        "type": "card_drop",
        "pos": pos,
        "card_id": card_id,
        "card_type": card_type,
        "color": RARITY_COLORS[min(rarity, len(RARITY_COLORS)-1)],
        "name": card_info.get("name", card_id)
    }

# ==============================================================================
#   卡牌效果处理器
# ==============================================================================
class CardEffectProcessor:
    """处理卡牌的持续性和触发性效果"""
    
    def __init__(self, player):
        self.player = player
        self.regen_timer = 0
        self.chaos_timer = 0
        self.shield_regen_timer = 0
        
    def update(self, dt=1):
        """每帧更新，处理持续性效果"""
        # 生命再生
        if getattr(self.player, "has_regen", False):
            self.regen_timer += dt
            regen_interval = getattr(self.player, "regen_interval", 300)
            if self.regen_timer >= regen_interval:
                heal_amount = getattr(self.player, "regen_rate", 5)
                self.player.heal(heal_amount)
                self.regen_timer = 0
        
        # 【修复】护盾恢复
        if getattr(self.player, "has_shield_regen", False):
            self.shield_regen_timer += dt
            shield_regen_interval = 120  # 2秒恢复一次
            if self.shield_regen_timer >= shield_regen_interval:
                shield_regen = getattr(self.player, "shield_regen", 1)
                max_shield = getattr(self.player, "max_shield", 0)
                if max_shield > 0 and self.player.shield < max_shield:
                    self.player.shield = min(max_shield, self.player.shield + shield_regen)
                self.shield_regen_timer = 0
        
        # 冰霜新星：周期性范围冻结
        if getattr(self.player, "has_frost", False):
            if not hasattr(self, "frost_timer"):
                self.frost_timer = 0
            self.frost_timer += dt
            frost_interval = 180  # 3秒触发一次(120帧=2秒,改为3秒更平衡)
            if self.frost_timer >= frost_interval:
                self.frost_timer = 0
                # 返回冰霜新星触发标记
                return {"frost_nova": True}
    
    def on_kill_enemy(self, enemy):
        """击杀敌人时触发效果"""
        effects = []
        
        # 吸血效果
        if getattr(self.player, "has_lifesteal", False):
            lifesteal = getattr(self.player, "lifesteal", 0.15)
            heal = int(self.player.damage * lifesteal)
            self.player.heal(heal)
        
        # 裂变反应
        if getattr(self.player, "has_corpse_explosion", False):
            effects.append({
                "type": "corpse_explosion",
                "pos": enemy.rect.center,
                "damage": self.player.damage * 0.5,
                "radius": 100
            })
        
        # 能量虹吸
        if getattr(self.player, "has_energy_siphon", False):
            self.player.ult_charge = min(
                self.player.max_ult_charge,
                self.player.ult_charge + self.player.max_ult_charge * 0.05
            )
        
        return effects
    
    def on_bullet_hit(self, bullet, target):
        """子弹击中敌人时触发效果"""
        effects = []
        
        # 冻结效果
        if getattr(self.player, "has_frost", False):
            freeze_duration = getattr(self.player, "freeze_duration", 120)
            target.frozen_timer = freeze_duration
        
        # 连锁闪电
        if getattr(self.player, "has_chain_lightning", False):
            chain_count = getattr(self.player, "chain_count", 3)
            chain_damage = getattr(self.player, "chain_damage", 0.6)
            effects.append({
                "type": "chain_lightning",
                "start": target,
                "chain_count": chain_count,
                "damage_mult": chain_damage
            })
        
        # 混沌触发
        if getattr(self.player, "has_chaos", False):
            chaos_chance = getattr(self.player, "chaos_chance", 0.0)
            if random.random() < chaos_chance:
                chaos_mult = getattr(self.player, "chaos_mult", 1.0)
                extra_damage = self.player.damage * (chaos_mult - 1.0)
                target.hp -= extra_damage
                effects.append({
                    "type": "chaos_proc",
                    "pos": target.rect.center,
                    "damage": extra_damage
                })
        
        return effects

# ==============================================================================
#   数值工具函数
# ==============================================================================
def calculate_damage(base_damage, player, is_critical=False, target=None):
    """计算最终伤害值"""
    damage = base_damage
    
    # 暴击倍率
    if is_critical:
        damage *= getattr(player, "crit_mult", 1.5)
    
    # 减伤
    if target and hasattr(target, "armor"):
        damage *= (1 - target.armor * 0.1)
    
    # Boss伤害加成
    if target and getattr(target, "is_boss", False):
        damage *= getattr(player, "boss_damage_mult", 1.0)
    
    return damage

# ==============================================================================
#   调试与统计
# ==============================================================================
def get_all_card_names():
    """获取所有卡牌名称列表"""
    cards = {}
    for card_id, card_data in BASE_CARDS.items():
        cards[card_id] = card_data["name"]
    for card_id, card_data in MODIFIER_CARDS.items():
        cards[card_id] = card_data["name"]
    for card_id, card_data in SYNERGY_RULES.items():
        cards[card_id] = card_data["name"]
    return cards

def print_card_stats():
    """打印卡牌系统统计信息"""
    log_info("=== 新卡牌系统统计 ===")
    log_info(f"基础卡牌: {len(BASE_CARDS)} 张")
    log_info(f"参数卡牌: {len(MODIFIER_CARDS)} 张")
    log_info(f"协同规则: {len(SYNERGY_RULES)} 个")
    
    # 统计流派分布
    archetype_count = {}
    for card_data in BASE_CARDS.values():
        arch = card_data.get("archetype", "unknown")
        archetype_count[arch] = archetype_count.get(arch, 0) + 1
    
    log_info("流派分布:")
    for arch, count in archetype_count.items():
        log_info(f"  {arch}: {count} 张")

# ==============================================================================
#   视觉反馈系统
# ==============================================================================
class CardVisualEffect:
    """卡牌视觉效果管理器"""
    
    def __init__(self):
        self.particles = []  # 粒子效果列表
        self.flashes = []  # 闪光效果列表
        self.connections = []  # 连接线效果列表
        self.screen_shake = 0  # 屏幕震动强度
        
    def add_card_acquire_effect(self, pos, card_rarity=1):
        """添加获得卡牌时的金色闪光效果"""
        # 创建粒子爆发
        color = RARITY_COLORS[min(card_rarity, len(RARITY_COLORS)-1)]
        particle_count = 20 + card_rarity * 10
        
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            self.particles.append({
                "x": pos[0],
                "y": pos[1],
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "color": color,
                "life": 60,
                "max_life": 60,
                "size": random.uniform(3, 8)
            })
        
        # 添加闪光
        self.flashes.append({
            "pos": pos,
            "color": color,
            "size": 0,
            "max_size": 150 + card_rarity * 50,
            "life": 30
        })
        
        # 播放音效
        sound_mgr.play("item_pickup")
    
    def add_synergy_effect(self, card_positions):
        """添加协同触发时的连接光效"""
        # 在卡牌之间创建连接线
        for i in range(len(card_positions)):
            for j in range(i+1, len(card_positions)):
                self.connections.append({
                    "start": card_positions[i],
                    "end": card_positions[j],
                    "color": (255, 215, 0),
                    "life": 90,
                    "thickness": 3
                })
        
        # 屏幕震动
        self.screen_shake = 10
        
        # 粒子效果
        center_x = sum(p[0] for p in card_positions) / len(card_positions)
        center_y = sum(p[1] for p in card_positions) / len(card_positions)
        
        for _ in range(50):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 10)
            self.particles.append({
                "x": center_x,
                "y": center_y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "color": (255, 215, 0),
                "life": 80,
                "max_life": 80,
                "size": random.uniform(4, 10)
            })
        
        # 播放特殊音效
        sound_mgr.play("achievement")
    
    def add_powerful_combo_effect(self, pos):
        """添加使用强力组合时的特效"""
        # 屏幕震动
        self.screen_shake = 15
        
        # 爆炸性粒子
        for _ in range(100):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            self.particles.append({
                "x": pos[0],
                "y": pos[1],
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "color": random.choice([(255, 100, 100), (255, 215, 0), (100, 200, 255)]),
                "life": 100,
                "max_life": 100,
                "size": random.uniform(5, 12)
            })
        
        # 巨大闪光
        self.flashes.append({
            "pos": pos,
            "color": (255, 255, 255),
            "size": 0,
            "max_size": 300,
            "life": 40
        })
    
    def update(self):
        """更新所有视觉效果"""
        # 更新粒子
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.2  # 重力
            p["life"] -= 1
        self.particles = [p for p in self.particles if p["life"] > 0]
        
        # 更新闪光
        for f in self.flashes:
            f["size"] += (f["max_size"] - f["size"]) * 0.2
            f["life"] -= 1
        self.flashes = [f for f in self.flashes if f["life"] > 0]
        
        # 更新连接线
        for c in self.connections:
            c["life"] -= 1
        self.connections = [c for c in self.connections if c["life"] > 0]
        
        # 衰减屏幕震动
        if self.screen_shake > 0:
            self.screen_shake *= 0.9
            if self.screen_shake < 0.5:
                self.screen_shake = 0
    
    def draw(self, surface):
        """绘制所有视觉效果"""
        # 绘制连接线
        for c in self.connections:
            alpha = int(255 * (c["life"] / 90))
            color = (*c["color"], alpha)
            # 绘制发光效果（多层）
            for i in range(3):
                thickness = c["thickness"] + (3 - i) * 2
                try:
                    pygame.draw.line(surface, c["color"], c["start"], c["end"], thickness)
                except:
                    pass
        
        # 绘制闪光
        for f in self.flashes:
            alpha = int(255 * (f["life"] / 30) * (1 - f["size"] / f["max_size"]))
            if alpha > 0:
                size = int(f["size"])
                color = (*f["color"][:3], alpha)
                # 绘制多层光晕
                for i in range(3):
                    radius = size + i * 10
                    try:
                        s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                        pygame.draw.circle(s, color, (radius, radius), radius)
                        surface.blit(s, (f["pos"][0] - radius, f["pos"][1] - radius))
                    except:
                        pass
        
        # 绘制粒子
        for p in self.particles:
            alpha = int(255 * (p["life"] / p["max_life"]))
            if alpha > 0:
                color = (*p["color"][:3], alpha)
                try:
                    pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), int(p["size"]))
                except:
                    pass
    
    def get_screen_shake_offset(self):
        """获取屏幕震动偏移量"""
        if self.screen_shake > 0:
            return (
                random.randint(-int(self.screen_shake), int(self.screen_shake)),
                random.randint(-int(self.screen_shake), int(self.screen_shake))
            )
        return (0, 0)

# 全局视觉效果管理器
card_visual_fx = CardVisualEffect()

# ==============================================================================
#   卡牌UI渲染函数
# ==============================================================================
def draw_card_choice_ui(surface, upgrade_manager, selected_index=0):
    """绘制卡牌选择界面（升级时的3选1）"""
    if not upgrade_manager.upgrade_choice:
        return
    
    screen_w, screen_h = surface.get_size()
    card_width = 280
    card_height = 400
    spacing = 40
    total_width = card_width * 3 + spacing * 2
    start_x = (screen_w - total_width) // 2
    card_y = (screen_h - card_height) // 2
    
    # 绘制半透明背景
    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    # 绘制标题
    font_title = pygame.font.Font(None, 64)
    title_text = font_title.render("选择一张卡牌", True, (255, 215, 0))
    title_rect = title_text.get_rect(center=(screen_w // 2, 80))
    surface.blit(title_text, title_rect)
    
    # 绘制3张卡牌
    for i, choice in enumerate(upgrade_manager.upgrade_choice):
        card_x = start_x + i * (card_width + spacing)
        is_selected = (i == selected_index)
        
        _draw_single_card(surface, choice, card_x, card_y, card_width, card_height, is_selected)

def _draw_single_card(surface, card_choice, x, y, width, height, is_selected):
    """绘制单张卡牌"""
    card_type = card_choice["type"]
    card_id = card_choice["id"]
    
    # 获取卡牌数据
    if card_type == "upgrade":
        card_info = BASE_CARDS.get(card_id, {})
        is_upgrade = True
    else:
        card_info = get_card_info(card_id, card_type)
        is_upgrade = False
    
    if not card_info:
        return
    
    # 获取稀有度和颜色
    rarity = card_info.get("rarity", 1)
    rarity_color = RARITY_COLORS[min(rarity, len(RARITY_COLORS)-1)]
    
    # 选中时的发光效果
    if is_selected:
        # 绘制外发光
        glow_surf = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*rarity_color, 100), (0, 0, width + 20, height + 20), border_radius=15)
        surface.blit(glow_surf, (x - 10, y - 10))
    
    # 卡牌背景
    card_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(card_surf, (20, 25, 35, 250), (0, 0, width, height), border_radius=10)
    pygame.draw.rect(card_surf, rarity_color, (0, 0, width, height), 3, border_radius=10)
    
    # 绘制程序化图案
    if "visual_seed" in card_info:
        pattern = generate_card_pattern(card_info["visual_seed"], card_info.get("pattern", "wave"))
        _draw_pattern_on_card(card_surf, pattern, width, height, rarity_color)
    
    # 卡牌名称
    font_name = pygame.font.Font(None, 36)
    name_text = card_info.get("name", card_id)
    if is_upgrade:
        name_text += " ▲"
    name_surf = font_name.render(name_text, True, rarity_color)
    name_rect = name_surf.get_rect(center=(width // 2, 40))
    card_surf.blit(name_surf, name_rect)
    
    # 类别/流派标签
    font_small = pygame.font.Font(None, 24)
    if card_type == "base":
        archetype = card_info.get("archetype", "")
        if archetype in CARD_ARCHETYPES:
            arch_data = CARD_ARCHETYPES[archetype]
            tag_text = f"{arch_data['icon']} {arch_data['name']}"
            tag_surf = font_small.render(tag_text, True, arch_data["color"])
            tag_rect = tag_surf.get_rect(center=(width // 2, 75))
            card_surf.blit(tag_surf, tag_rect)
    elif card_type == "modifier":
        mod_type = card_info.get("type", "")
        tag_text = f"【{mod_type}】"
        tag_surf = font_small.render(tag_text, True, (200, 200, 200))
        tag_rect = tag_surf.get_rect(center=(width // 2, 75))
        card_surf.blit(tag_surf, tag_rect)
    
    # 描述文本
    font_desc = pygame.font.Font(None, 28)
    desc = card_info.get("desc", "")
    desc_lines = _wrap_text(desc, font_desc, width - 40)
    desc_y = 120
    for line in desc_lines:
        desc_surf = font_desc.render(line, True, (220, 220, 220))
        desc_rect = desc_surf.get_rect(center=(width // 2, desc_y))
        card_surf.blit(desc_surf, desc_rect)
        desc_y += 35
    
    # 数学指纹
    if "visual_seed" in card_info:
        pattern = generate_card_pattern(card_info["visual_seed"], card_info.get("pattern", "wave"))
        formula = pattern.get("formula", "")
        font_formula = pygame.font.Font(None, 20)
        formula_surf = font_formula.render(formula, True, (100, 150, 200))
        formula_rect = formula_surf.get_rect(center=(width // 2, height - 30))
        card_surf.blit(formula_surf, formula_rect)
    
    surface.blit(card_surf, (x, y))

def _draw_pattern_on_card(surface, pattern, width, height, color):
    """在卡牌上绘制程序化图案"""
    pattern_type = pattern["type"]
    
    # 创建半透明图案层
    pattern_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    
    if pattern_type == "wave":
        freq = pattern["frequency"]
        amp = pattern["amplitude"]
        phase = pattern["phase"]
        for x in range(0, width, 3):
            y = int(height // 2 + amp * math.sin(freq * x / 50 + phase))
            if 0 <= y < height:
                pygame.draw.circle(pattern_surf, (*color, 50), (x, y), 2)
    
    elif pattern_type == "spiral":
        rotation = pattern["rotation"]
        expansion = pattern["expansion"]
        center_x, center_y = width // 2, height // 2 + 50
        for t in range(0, 360, 5):
            angle = math.radians(t)
            r = expansion * t / 60
            x = int(center_x + r * math.cos(angle + rotation * t))
            y = int(center_y + r * math.sin(angle + rotation * t))
            if 0 <= x < width and 0 <= y < height:
                pygame.draw.circle(pattern_surf, (*color, 60), (x, y), 2)
    
    elif pattern_type == "geometric":
        sides = pattern["sides"]
        scale = pattern["scale"]
        rot = pattern["rotation"]
        center_x, center_y = width // 2, height // 2 + 50
        radius = 60 * scale
        points = []
        for i in range(sides):
            angle = math.radians(360 * i / sides + rot)
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            points.append((x, y))
        if len(points) > 2:
            pygame.draw.polygon(pattern_surf, (*color, 40), points, 2)
    
    elif pattern_type == "fractal":
        # 简化的分形图案
        center_x, center_y = width // 2, height // 2 + 50
        iterations = pattern["iterations"]
        for i in range(iterations):
            size = 80 * (0.6 ** i)
            pygame.draw.circle(pattern_surf, (*color, 40 // (i+1)), (center_x, center_y), int(size), 1)
    
    surface.blit(pattern_surf, (0, 0))

def _wrap_text(text, font, max_width):
    """文本换行"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

def draw_build_progress_ui(surface, upgrade_manager, x, y):
    """绘制构建进度UI"""
    if not upgrade_manager:
        return
    
    build_info = upgrade_manager.get_build_summary()
    
    # 背景框
    bg_width, bg_height = 300, 200
    bg_surf = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
    pygame.draw.rect(bg_surf, (0, 0, 0, 200), (0, 0, bg_width, bg_height), border_radius=10)
    pygame.draw.rect(bg_surf, (100, 150, 200), (0, 0, bg_width, bg_height), 2, border_radius=10)
    
    # 标题
    font_title = pygame.font.Font(None, 32)
    title_surf = font_title.render("构建进度", True, (255, 215, 0))
    bg_surf.blit(title_surf, (10, 10))
    
    # 流派统计
    font_normal = pygame.font.Font(None, 24)
    y_offset = 50
    for archetype, count in build_info["archetypes"].items():
        if archetype in CARD_ARCHETYPES:
            arch_data = CARD_ARCHETYPES[archetype]
            text = f"{arch_data['icon']} {arch_data['name']}: {count}"
            text_surf = font_normal.render(text, True, arch_data["color"])
            bg_surf.blit(text_surf, (20, y_offset))
            y_offset += 30
    
    # 协同数
    synergy_text = f"协同效果: {build_info['synergies']}"
    synergy_surf = font_normal.render(synergy_text, True, (255, 215, 0))
    bg_surf.blit(synergy_surf, (20, y_offset))
    
    # 主导流派
    if build_info["dominant_archetype"]:
        dom_arch = build_info["dominant_archetype"]
        if dom_arch in CARD_ARCHETYPES:
            dom_text = f"主流派: {CARD_ARCHETYPES[dom_arch]['name']}"
            dom_surf = font_normal.render(dom_text, True, CARD_ARCHETYPES[dom_arch]["color"])
            bg_surf.blit(dom_surf, (20, y_offset + 30))
    
    surface.blit(bg_surf, (x, y))

# ==============================================================================
#   Boss奖励系统
# ==============================================================================
def grant_boss_reward(upgrade_manager):
    """Boss战胜利后给予传奇卡牌奖励"""
    # 从稀有度3的基础卡中随机选择
    legendary_cards = [
        card_id for card_id, card_data in BASE_CARDS.items()
        if card_data.get("rarity", 1) == 3
    ]
    
    if legendary_cards:
        card_id = random.choice(legendary_cards)
        upgrade_manager.add_card(card_id, "base")
        
        # 视觉效果
        card_visual_fx.add_card_acquire_effect((WIDTH // 2, HEIGHT // 2), 3)
        card_visual_fx.add_powerful_combo_effect((WIDTH // 2, HEIGHT // 2))
        
        log_info(f"Boss奖励：获得传奇卡牌【{BASE_CARDS[card_id]['name']}】")
        return card_id
    
    return None

def grant_elite_reward(upgrade_manager):
    """精英怪击杀后有概率给予稀有卡牌"""
    if random.random() < 0.5:  # 50%概率
        rare_cards = [
            card_id for card_id, card_data in BASE_CARDS.items()
            if card_data.get("rarity", 1) == 2
        ]
        
        if rare_cards:
            card_id = random.choice(rare_cards)
            upgrade_manager.add_card(card_id, "base")
            
            # 视觉效果
            card_visual_fx.add_card_acquire_effect((WIDTH // 2, HEIGHT // 2), 2)
            
            log_info(f"精英奖励：获得稀有卡牌【{BASE_CARDS[card_id]['name']}】")
            return card_id
    
    return None

# ==============================================================================
#   动态难度系统
# ==============================================================================
class DynamicDifficultySystem:
    """根据玩家卡组强度动态调整难度"""
    
    def __init__(self):
        self.base_difficulty = 1.0
        self.build_strength_multiplier = 1.0
        
    def calculate_build_strength(self, upgrade_manager):
        """计算玩家卡组强度"""
        if not upgrade_manager:
            return 1.0
        
        strength = 1.0
        
        # 基础卡数量贡献
        card_count = len(upgrade_manager.owned_cards)
        strength += card_count * 0.05
        
        # 卡牌等级贡献
        total_levels = sum(card.level for card in upgrade_manager.owned_cards.values())
        strength += total_levels * 0.03
        
        # 协同效果贡献
        synergy_count = len(upgrade_manager.active_synergies)
        strength += synergy_count * 0.15
        
        # 流派专精贡献
        build_info = upgrade_manager.get_build_summary()
        if build_info["dominant_archetype"]:
            dominant_count = build_info["archetypes"].get(build_info["dominant_archetype"], 0)
            if dominant_count >= 3:
                strength += 0.2  # 流派专精加成
            if dominant_count >= 5:
                strength += 0.3  # 深度专精加成
        
        # 限制最大倍率
        strength = min(strength, 2.5)
        
        return strength
    
    def update_difficulty(self, upgrade_manager):
        """更新难度倍率"""
        self.build_strength_multiplier = self.calculate_build_strength(upgrade_manager)
        
    def get_enemy_stat_multiplier(self):
        """获取敌人属性倍率"""
        # 敌人属性增幅 = 1.0 + (卡组强度 - 1.0) * 0.5
        # 例如：卡组强度2.0时，敌人属性变为1.5倍
        return 1.0 + (self.build_strength_multiplier - 1.0) * 0.5
    
    def get_spawn_rate_multiplier(self):
        """获取刷怪速率倍率"""
        # 刷怪速率略微增加
        return 1.0 + (self.build_strength_multiplier - 1.0) * 0.3

# 全局难度系统实例
dynamic_difficulty = DynamicDifficultySystem()

# ==============================================================================
#   跨局进度保存系统
# ==============================================================================
class MetaProgressionSystem:
    """管理跨局的永久进度"""
    
    def __init__(self):
        self.permanent_unlocks = []  # 永久解锁的能力
        self.total_runs = 0  # 总游戏次数
        self.best_build = None  # 最佳构建记录
        self.legacy_points = 0  # 遗产点数
        
    def end_run(self, upgrade_manager, final_score, wave_reached):
        """结束一局游戏，记录数据并给予奖励"""
        self.total_runs += 1
        
        # 记录最佳构建
        build_info = upgrade_manager.get_build_summary()
        if not self.best_build or final_score > self.best_build.get("score", 0):
            self.best_build = {
                "score": final_score,
                "wave": wave_reached,
                "cards": len(upgrade_manager.owned_cards),
                "synergies": len(upgrade_manager.active_synergies),
                "archetype": build_info.get("dominant_archetype", "mixed")
            }
        
        # 计算遗产点数奖励
        points_earned = wave_reached * 10 + final_score // 1000
        self.legacy_points += points_earned
        
        # 根据表现解锁永久能力
        self._check_permanent_unlocks(wave_reached, build_info)
        
        log_info(f"本局结束：获得{points_earned}遗产点数，总计{self.legacy_points}")
        
        return points_earned
    
    def _check_permanent_unlocks(self, wave, build_info):
        """检查是否解锁新的永久能力"""
        # 示例：达到波数30解锁起始护盾
        if wave >= 30 and "starting_shield" not in self.permanent_unlocks:
            self.permanent_unlocks.append("starting_shield")
            log_info("永久解锁：起始护盾（开局获得20点护盾）")
        
        # 示例：完成5次游戏解锁起始卡牌
        if self.total_runs >= 5 and "starting_card" not in self.permanent_unlocks:
            self.permanent_unlocks.append("starting_card")
            log_info("永久解锁：起始卡牌（开局随机获得一张稀有卡）")
    
    def apply_starting_bonuses(self, player, upgrade_manager):
        """应用开局加成"""
        if "starting_shield" in self.permanent_unlocks:
            player.shield = 20
        
        if "starting_card" in self.permanent_unlocks:
            rare_cards = [
                card_id for card_id, card_data in BASE_CARDS.items()
                if card_data.get("rarity", 1) == 2
            ]
            if rare_cards:
                card_id = random.choice(rare_cards)
                upgrade_manager.add_card(card_id, "base")
                log_info(f"起始卡牌：【{BASE_CARDS[card_id]['name']}】")
    
    def save_to_file(self, filename="meta_progress.json"):
        """保存跨局进度"""
        import json
        data = {
            "permanent_unlocks": self.permanent_unlocks,
            "total_runs": self.total_runs,
            "best_build": self.best_build,
            "legacy_points": self.legacy_points
        }
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            log_error(f"保存跨局进度失败: {e}")
            return False
    
    def load_from_file(self, filename="meta_progress.json"):
        """加载跨局进度"""
        import json
        import os
        if not os.path.exists(filename):
            return False
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.permanent_unlocks = data.get("permanent_unlocks", [])
            self.total_runs = data.get("total_runs", 0)
            self.best_build = data.get("best_build", None)
            self.legacy_points = data.get("legacy_points", 0)
            return True
        except Exception as e:
            log_error(f"加载跨局进度失败: {e}")
            return False

# 全局跨局进度系统
meta_progression = MetaProgressionSystem()
