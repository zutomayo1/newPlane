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
            player.score += item.value
            log_info(f"获得 {item.value} 经验值，总分数: {player.score}")
        
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
#   增益系统数据定义
# ==============================================================================
# 所有可获得的增益效果，分为多个类别

BUFF_LIBRARY = {
    # ============ 基础属性类增益 ============
    "dmg": {
        "name": "火力强化",
        "desc": "伤害 ×1.3",
        "rarity": 0,
        "type": "stat",
        "apply": lambda player: setattr(player, "damage", player.damage * 1.3)
    },
    "spd": {
        "name": "极速装填",
        "desc": "射速 ×1.15 (射击延迟减少)",
        "rarity": 0,
        "type": "stat",
        "apply": lambda player: setattr(player, "shoot_delay", max(40, player.shoot_delay * 0.85))
    },
    "hp_heal": {
        "name": "纳米修复",
        "desc": "回复 50 生命",
        "rarity": 0,
        "type": "stat",
        "apply": lambda player: player.heal(50)
    },
    "hp_max": {
        "name": "钛金装甲",
        "desc": "生命上限 +100",
        "rarity": 0,
        "type": "stat",
        "apply": lambda player: setattr(player, "max_hp", player.max_hp + 100) or player.heal(100)
    },
    "magnet": {
        "name": "强力磁场",
        "desc": "拾取范围 ×1.5",
        "rarity": 0,
        "type": "stat",
        "apply": lambda player: setattr(player, "pickup_range", getattr(player, "pickup_range", 150) * 1.5)
    },
    "execute": {
        "name": "斩杀协议",
        "desc": "低血敌人更容易被击杀",
        "rarity": 0,
        "type": "stat",
        "apply": lambda player: setattr(player, "execute_threshold", getattr(player, "execute_threshold", 0.2) + 0.05)
    },
    
    # ============ 子弹机制类增益 ============
    "multi": {
        "name": "散射模块",
        "desc": "子弹数量 +1",
        "rarity": 1,
        "type": "mechanic",
        "apply": lambda player: setattr(player, "bullet_count", player.bullet_count + 1)
    },
    "pierce": {
        "name": "钨芯弹头",
        "desc": "穿透次数 +1",
        "rarity": 1,
        "type": "mechanic",
        "apply": lambda player: setattr(player, "piercing", player.piercing + 1)
    },
    "bounce": {
        "name": "量子反射",
        "desc": "弹跳次数 +1",
        "rarity": 1,
        "type": "mechanic",
        "apply": lambda player: setattr(player, "bounce_level", player.bounce_level + 1)
    },
    "homing": {
        "name": "智能弹道",
        "desc": "所有子弹自动追踪",
        "rarity": 2,
        "type": "mechanic",
        "apply": lambda player: setattr(player, "homing_level", player.homing_level + 1)
    },
    
    # ============ 防御类增益 ============
    "shield": {
        "name": "偏导护盾",
        "desc": "获得 20 点护盾",
        "rarity": 1,
        "type": "defense",
        "apply": lambda player: setattr(player, "shield", player.shield + 20)
    },
    "armor": {
        "name": "活性装甲",
        "desc": "受伤害 -15%",
        "rarity": 1,
        "type": "defense",
        "apply": lambda player: setattr(player, "damage_reduction", player.damage_reduction + 0.15)
    },
    "regen": {
        "name": "纳米再生",
        "desc": "每 5 秒回复 5HP（被动）",
        "rarity": 1,
        "type": "defense",
        "apply": lambda player: setattr(player, "has_regen", True)
    },
    "dodge": {
        "name": "幻影引擎",
        "desc": "闪避率 +15%",
        "rarity": 2,
        "type": "defense",
        "apply": lambda player: setattr(player, "dodge_chance", getattr(player, "dodge_chance", 0) + 0.15)
    },
    
    # ============ 暴击与精度 ============
    "crit_dmg": {
        "name": "弱点分析",
        "desc": "暴击伤害 ×2.0",
        "rarity": 1,
        "type": "crit",
        "apply": lambda player: setattr(player, "crit_mult", player.crit_mult * 2.0)
    },
    "crit_chance": {
        "name": "幸运星",
        "desc": "暴击率 +20%",
        "rarity": 1,
        "type": "crit",
        "apply": lambda player: setattr(player, "crit_chance", player.crit_chance + 0.20)
    },
    "sniper": {
        "name": "鹰眼瞄准",
        "desc": "射程与飞行速度 +30%",
        "rarity": 1,
        "type": "crit",
        "apply": lambda player: setattr(player, "bullet_speed_mult", getattr(player, "bullet_speed_mult", 1.0) * 1.3)
    },
    
    # ============ 特效触发类增益 ============
    "frost": {
        "name": "冰霜新星",
        "desc": "攻击有 30% 概率冻结敌人",
        "rarity": 2,
        "type": "effect",
        "apply": lambda player: setattr(player, "has_frost", True)
    },
    "lightning": {
        "name": "雷神之锤",
        "desc": "攻击触发连锁闪电（跳跃3格）",
        "rarity": 2,
        "type": "effect",
        "apply": lambda player: setattr(player, "has_lightning", True)
    },
    "corpse": {
        "name": "裂变反应",
        "desc": "敌人死亡产生爆炸",
        "rarity": 2,
        "type": "effect",
        "apply": lambda player: setattr(player, "has_corpse_explosion", True)
    },
    "vampire": {
        "name": "鲜血渴望",
        "desc": "击杀敌人回复 8HP",
        "rarity": 2,
        "type": "effect",
        "apply": lambda player: setattr(player, "has_vampire", True)
    },
    "area_dmg": {
        "name": "聚能爆破",
        "desc": "所有攻击附带爆炸（50%主伤害）",
        "rarity": 3,
        "type": "effect",
        "apply": lambda player: setattr(player, "has_area_dmg", True)
    },
    "blackhole": {
        "name": "奇点发生器",
        "desc": "攻击 20% 概率生成黑洞吸引敌人",
        "rarity": 3,
        "type": "effect",
        "apply": lambda player: setattr(player, "has_blackhole", True)
    },
    
    # ============ 僚机与辅助 ============
    "drone": {
        "name": "浮游炮组",
        "desc": "获得 2 个跟随僚机，独立射击 (上限4个)",
        "rarity": 3,
        "type": "summon",
        "apply": lambda player: add_wingmen_to_player(player, 2)
    },
    
    # ============ 进阶风险收益 ============
    "overload": {
        "name": "反应堆过载",
        "desc": "射速 +15%，生命 -8%",
        "rarity": 2,
        "type": "risk",
        "apply": lambda player: (
            setattr(player, "shoot_delay", max(40, player.shoot_delay * 0.85)),
            player.take_damage(int(player.max_hp * 0.08))
        )
    },
    "glass_cannon": {
        "name": "玻璃大炮",
        "desc": "伤害 ×1.6，生命上限 -30%",
        "rarity": 3,
        "type": "risk",
        "apply": lambda player: (
            setattr(player, "damage", player.damage * 1.6),
            setattr(player, "max_hp", max(50, int(player.max_hp * 0.7))),
            player.take_damage(int(player.max_hp * 0.2))
        )
    },
    "blood_pact": {
        "name": "鲜血契约",
        "desc": "每秒扣 1 血，伤害 +2% （被动）",
        "rarity": 3,
        "type": "risk",
        "apply": lambda player: setattr(player, "has_blood_pact", True)
    },
    
    # ============ 传奇增益 ============
    "bullet_storm": {
        "name": "弹幕风暴",
        "desc": "子弹数量 +2，范围密集覆盖",
        "rarity": 3,
        "type": "legendary",
        "apply": lambda player: setattr(player, "bullet_count", player.bullet_count + 2)
    },
    "freeze_burn": {
        "name": "寒冰灼烧",
        "desc": "冻结敌人受到双倍伤害",
        "rarity": 2,
        "type": "legendary",
        "apply": lambda player: setattr(player, "has_freeze_burn", True)
    },
    "cluster_bomb": {
        "name": "集束炸弹",
        "desc": "爆炸范围 ×1.5，碎片伤害 +50%",
        "rarity": 1,
        "type": "legendary",
        "apply": lambda player: setattr(player, "explosion_mult", getattr(player, "explosion_mult", 1.0) * 1.5)
    },
    "energy_siphon": {
        "name": "能量虹吸",
        "desc": "击杀敌人恢复 5% 大招能量",
        "rarity": 2,
        "type": "legendary",
        "apply": lambda player: setattr(player, "has_energy_siphon", True)
    },
    "giant_slayer": {
        "name": "巨人杀手",
        "desc": "对 BOSS/精英伤害 +50%",
        "rarity": 2,
        "type": "legendary",
        "apply": lambda player: setattr(player, "boss_damage_mult", getattr(player, "boss_damage_mult", 1.0) * 1.5)
    },
    "time_warp": {
        "name": "时间扭曲",
        "desc": "所有冷却缩减 20%（射速+25%, 大招冷却-20%）",
        "rarity": 3,
        "type": "legendary",
        "apply": lambda player: (
            setattr(player, "shoot_delay", player.shoot_delay * 0.8),
            setattr(player, "cooldown_reduction", getattr(player, "cooldown_reduction", 0) + 0.2)
        )
    },
}

# ==============================================================================
#   升级管理类
# ==============================================================================
class UpgradeManager:
    """管理升级触发、选择、应用的核心系统"""
    
    def __init__(self):
        self.current_upgrades = []  # 玩家已获得的增益列表 [buff_id, buff_id, ...]
        self.upgrade_choice = None  # 当前选择界面的 3 个升级选项
        self.upgrade_choice_index = 0  # 玩家选中的索引 (0/1/2)
        self.level_up_ready = False  # 是否需要显示升级选择
        self._player_ref = None  # 玩家对象引用，用于获取等级信息
        
    def set_player_ref(self, player):
        """设置对玩家对象的引用（在 Player init 时调用）"""
        self._player_ref = player
    
    def trigger_levelup(self):
        """触发升级，随机选择 3 个不重复的增益
        
        特殊机制：如果玩家僚机数 < 4，则自动保证一个选项为drone卡牌
        """
        player = getattr(self, '_player_ref', None)
        if not player:
            return
        
        player_level = player.level
        
        # 检查僚机保底机制：玩家僚机数少于4时，优先提供drone卡牌
        wingman_count = len(player.wingman_squadron.wingmen) if player.wingman_squadron else 0
        has_drone_guarantee = wingman_count < 4
        
        # Calculate weights for each rarity based on player level
        # 【优化】调整权重分配,使高品质升级更容易出现
        base_weights = {0: 1.0, 1: 0.5, 2: 0.1, 3: 0.0}
        if player_level <= 5:
            base_weights = {0: 1.0, 1: 0.4, 2: 0.08, 3: 0.0}
        elif player_level <= 10:
            base_weights = {0: 0.7, 1: 0.8, 2: 0.3, 3: 0.08}
        elif player_level <= 15:
            base_weights = {0: 0.3, 1: 1.0, 2: 0.6, 3: 0.15}
        elif player_level <= 20:
            base_weights = {0: 0.15, 1: 0.6, 2: 1.0, 3: 0.4}
        else:
            base_weights = {0: 0.08, 1: 0.3, 2: 0.7, 3: 1.0}
        
        # Group buffs by rarity
        buffs_by_rarity = {}
        for bid, buff in BUFF_LIBRARY.items():
            rarity = buff.get("rarity", 0)
            if rarity not in buffs_by_rarity:
                buffs_by_rarity[rarity] = []
            buffs_by_rarity[rarity].append(bid)
        
        # Selection logic with drone guarantee
        candidate_buffs = list(BUFF_LIBRARY.keys())
        weights = [base_weights.get(BUFF_LIBRARY[b]['rarity'], 0.0) for b in candidate_buffs]
        selected = []
        
        # First pick: drone guarantee if wingman_count < 4
        if has_drone_guarantee and "drone" in candidate_buffs:
            selected.append("drone")
            idx = candidate_buffs.index("drone")
            weights[idx] = 0
        
        # Pick remaining 2-3 options (depending on whether drone was guaranteed)
        remaining_picks = 3 - len(selected)
        
        for _ in range(remaining_picks):
            total = sum(weights)
            if total <= 0:
                # fallback simple random pick among remaining
                remaining = [b for b in candidate_buffs if b not in selected]
                if not remaining:
                    break
                pick = random.choice(remaining)
                selected.append(pick)
                idx = candidate_buffs.index(pick)
                weights[idx] = 0
                continue
            
            # choose by weights
            pick = random.choices(candidate_buffs, weights=weights, k=1)[0]
            
            # Ensure it's not already selected
            attempt = 0
            while pick in selected and attempt < 6:
                idx = candidate_buffs.index(pick)
                weights[idx] = 0
                total = sum(weights)
                if total <= 0:
                    break
                pick = random.choices(candidate_buffs, weights=weights, k=1)[0]
                attempt += 1
            
            if pick in selected:
                # fallback
                remaining = [b for b in candidate_buffs if b not in selected]
                if not remaining:
                    break
                pick = random.choice(remaining)
            
            selected.append(pick)
            idx = candidate_buffs.index(pick)
            weights[idx] = 0
        
        self.upgrade_choice = selected
        self.upgrade_choice_index = 0
        self.level_up_ready = True
        sound_mgr.play("levelup")
    
    def select_upgrade(self, choice_index):
        """玩家选择某个增益"""
        if 0 <= choice_index < len(self.upgrade_choice):
            buff_id = self.upgrade_choice[choice_index]
            self.apply_upgrade(buff_id)
            # If we have a player reference, apply the buff to the player immediately
            if self._player_ref:
                apply_buff_to_player(self._player_ref, buff_id)
            self.upgrade_choice = None
            self.level_up_ready = False
            return True
        return False
    
    def apply_upgrade(self, buff_id):
        """应用增益到玩家，返回增益对象"""
        if buff_id not in BUFF_LIBRARY:
            log_error(f"Unknown buff: {buff_id}")
            return None
        
        buff_data = BUFF_LIBRARY[buff_id]
        self.current_upgrades.append(buff_id)
        # apply to player ref as well (if set)
        if self._player_ref:
            apply_buff_to_player(self._player_ref, buff_id)
        return buff_data
    
    def get_active_buffs(self):
        """获取当前生效的所有增益ID列表"""
        return self.current_upgrades.copy()
    
    def reset(self):
        """重置升级管理器（新局开始时调用）"""
        self.current_upgrades = []
        self.upgrade_choice = None
        self.upgrade_choice_index = 0
        self.level_up_ready = False

# ==============================================================================
#   增益应用工具函数
# ==============================================================================
def apply_buff_to_player(player, buff_id):
    """对玩家应用指定增益"""
    if buff_id not in BUFF_LIBRARY:
        log_error(f"Unknown buff: {buff_id}")
        return False
    
    buff = BUFF_LIBRARY[buff_id]
    try:
        buff["apply"](player)
        
        # 【新增】将卡牌ID添加到玩家的buffs列表（用于UI显示）
        if hasattr(player, 'buffs'):
            if buff_id not in player.buffs:
                player.buffs.append(buff_id)
        
        # 调用玩家的 on_buff_received 钩子（如果存在）
        if hasattr(player, "on_buff_received"):
            player.on_buff_received(buff_id, buff)
        return True
    except Exception as e:
        import traceback
        log_error(f"Failed to apply buff {buff_id}: {e}")
        log_error(traceback.format_exc())
        return False

def get_buff_info(buff_id):
    """获取增益的完整信息"""
    return BUFF_LIBRARY.get(buff_id, None)

def get_buffs_by_rarity(rarity):
    """按稀有度获取增益列表"""
    return [bid for bid, buff in BUFF_LIBRARY.items() if buff["rarity"] == rarity]

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
    """创建经验球掉落物体（应在 sprites.py 中定义 XPOrb 类）"""
    # 这个函数返回要创建的数据，由调用者在 main.py 中创建实体
    return {
        "type": "xp_orb",
        "pos": pos,
        "amount": amount,
        "color": BLUE
    }

def create_buff_drop(pos, buff_id):
    """创建增益卡牌掉落物体"""
    buff = BUFF_LIBRARY.get(buff_id)
    if not buff:
        return None
    
    return {
        "type": "buff_card",
        "pos": pos,
        "buff_id": buff_id,
        "color": RARITY_COLORS[buff["rarity"]],
        "name": buff["name"]
    }

# ==============================================================================
#   运行时增益效果处理
# ==============================================================================
class BuffProcessor:
    """处理被动增益和状态性增益的持续效果"""
    
    def __init__(self, player):
        self.player = player
        self.regen_timer = 0  # 纳米再生计时器
        self.blood_pact_timer = 0  # 鲜血契约计时器
        
    def update(self, dt=1):
        """每帧更新，处理持续性增益"""
        # 纳米再生：每 5 秒回复 5 HP
        if getattr(self.player, "has_regen", False):
            self.regen_timer += dt
            if self.regen_timer >= 300:  # 300 帧 = 5 秒（60 FPS）
                self.player.heal(5)
                self.regen_timer = 0
        
        # 鲜血契约：每秒扣 1 血
        if getattr(self.player, "has_blood_pact", False):
            self.blood_pact_timer += dt
            if self.blood_pact_timer >= 60:  # 60 帧 = 1 秒
                self.player.take_damage(1)
                self.blood_pact_timer = 0
    
    def on_kill_enemy(self, enemy):
        """击杀敌人时触发效果"""
        # 吸血鬼：击杀回血（平衡调整：10→8）
        if getattr(self.player, "has_vampire", False):
            self.player.heal(8)
        
        # 能量虹吸：击杀回复大招能量
        if getattr(self.player, "has_energy_siphon", False):
            self.player.ult_charge = min(
                self.player.max_ult_charge,
                self.player.ult_charge + self.player.max_ult_charge * 0.05
            )
        
        # 裂变反应：敌人死亡爆炸（需在外部调用 create_explosion）
        if getattr(self.player, "has_corpse_explosion", False):
            # 返回需要创建的爆炸信息，由调用者处理
            return {
                "type": "corpse_explosion",
                "pos": enemy.rect.center,
                "damage": self.player.damage * 0.5,
                "radius": 100
            }
        
        return None
    
    def on_bullet_hit(self, bullet, target):
        """子弹击中敌人时触发效果"""
        # 冻结新星：30% 概率冻结
        if getattr(self.player, "has_frost", False) and random.random() < 0.3:
            target.frozen_timer = 120  # 冻结 120 帧
        
        # 雷神之锤：连锁闪电
        if getattr(self.player, "has_lightning", False):
            self._trigger_chain_lightning(target)
        
        # 寒冰灼烧：冻结敌人受到双倍伤害
        if getattr(self.player, "has_freeze_burn", False) and getattr(target, "is_frozen", False):
            # 下次伤害会加倍（由调用者在计算伤害时检查此 flag）
            target.damage_multiplier = 2.0
    
    def _trigger_chain_lightning(self, initial_target, chain_count=3, visited=None):
        """递归触发连锁闪电"""
        if visited is None:
            visited = set()
        
        if chain_count <= 0:
            return
        
        visited.add(id(initial_target))
        
        # 查找最近的敌人
        from config import mobs  # 局部导入防止循环引用
        nearest = None
        nearest_dist = 300  # 跳跃范围
        
        for m in mobs:
            if id(m) in visited:
                continue
            dist = math.hypot(
                m.rect.centerx - initial_target.rect.centerx,
                m.rect.centery - initial_target.rect.centery
            )
            if dist < nearest_dist:
                nearest = m
                nearest_dist = dist
        
        if nearest:
            damage = self.player.damage * 0.5
            nearest.hp -= damage
            # 创建闪电视觉效果（由调用者通过 LightningBolt 处理）
            try:
                from sprites import LightningBolt
                LightningBolt(initial_target.rect.center, nearest.rect.center)
            except:
                pass
            # 递归继续链
            self._trigger_chain_lightning(nearest, chain_count - 1, visited)

# ==============================================================================
#   数值工具函数
# ==============================================================================
def calculate_damage(base_damage, player, is_critical=False, target=None):
    """计算最终伤害值，考虑所有增益修饰"""
    damage = base_damage * base_damage
    
    # 暴击倍率
    if is_critical:
        damage *= player.crit_mult
    
    # 装甲减伤（目标方向）
    if target and hasattr(target, "armor"):
        damage *= (1 - target.armor * 0.1)
    
    # 玻璃大炮风险收益（伤害翻倍，已在获取增益时应用）
    
    # Boss 伤害加成
    if target and getattr(target, "is_boss", False):
        damage *= player.boss_damage_mult
    
    # 寒冰灼烧冻结加倍
    if target and getattr(target, "damage_multiplier", 1.0) > 1.0:
        damage *= target.damage_multiplier
        target.damage_multiplier = 1.0  # 重置
    
    return damage

# ==============================================================================
#   升级卡牌信息生成
# ==============================================================================
def get_upgrade_card_info(buff_id):
    """获取升级卡牌显示信息"""
    buff = BUFF_LIBRARY.get(buff_id)
    if not buff:
        return None
    
    return {
        "id": buff_id,
        "name": buff["name"],
        "desc": buff["desc"],
        "rarity": buff["rarity"],
        "color": RARITY_COLORS[buff["rarity"]]
    }

# ==============================================================================
#   调试与统计
# ==============================================================================
def get_all_buff_names():
    """获取所有增益名称列表"""
    return {bid: buff["name"] for bid, buff in BUFF_LIBRARY.items()}

def print_buff_stats():
    """打印所有增益统计信息"""
    stats = {}
    for buff_id, buff in BUFF_LIBRARY.items():
        rarity = buff["rarity"]
        if rarity not in stats:
            stats[rarity] = 0
        stats[rarity] += 1
    
    log_info("=== 肉鸽系统增益统计 ===")
    for rarity in range(4):
        count = stats.get(rarity, 0)
        log_info(f"稀有度 {rarity} ({RARITY_NAMES[rarity+1]}): {count} 个增益")
    log_info(f"总计: {len(BUFF_LIBRARY)} 个增益")
