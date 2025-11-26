# ==============================================================================
#   肉鸽（Roguelite）系统核心 - 升级、增益、局内成长
# ==============================================================================
import random
import pygame
import math
from config import *
from utils import sound_mgr, log_error

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
        "desc": "击杀敌人回复 10HP",
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
        "desc": "获得 2 个跟随僚机，独立射击",
        "rarity": 3,
        "type": "summon",
        "apply": lambda player: setattr(player, "drone_count", getattr(player, "drone_count", 0) + 2)
    },
    
    # ============ 进阶风险收益 ============
    "overload": {
        "name": "反应堆过载",
        "desc": "射速 +25%，生命 -10%",
        "rarity": 2,
        "type": "risk",
        "apply": lambda player: (
            setattr(player, "shoot_delay", max(40, player.shoot_delay * 0.75)),
            player.take_damage(player.max_hp * 0.1)
        )
    },
    "glass_cannon": {
        "name": "玻璃大炮",
        "desc": "伤害 ×2.0，生命上限 -50%",
        "rarity": 3,
        "type": "risk",
        "apply": lambda player: (
            setattr(player, "damage", player.damage * 2.0),
            setattr(player, "max_hp", max(50, player.max_hp // 2)),
            player.take_damage(player.max_hp)
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
        
    def trigger_levelup(self):
        """触发升级，随机选择 3 个不重复的增益"""
        available_buffs = list(BUFF_LIBRARY.keys())
        self.upgrade_choice = random.sample(available_buffs, min(3, len(available_buffs)))
        self.upgrade_choice_index = 0
        self.level_up_ready = True
        sound_mgr.play("levelup")
    
    def select_upgrade(self, choice_index):
        """玩家选择某个增益"""
        if 0 <= choice_index < len(self.upgrade_choice):
            buff_id = self.upgrade_choice[choice_index]
            self.apply_upgrade(buff_id)
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
        # 调用玩家的 on_buff_received 钩子（如果存在）
        if hasattr(player, "on_buff_received"):
            player.on_buff_received(buff_id, buff)
        return True
    except Exception as e:
        log_error(f"Failed to apply buff {buff_id}: {e}")
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
        # XP 需求每次升级乘以 1.2 (指数级增长)
        self.next_level_xp = int(self.next_level_xp * 1.2)
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
        "color": YELLOW
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
        # 吸血鬼：击杀回血
        if getattr(self.player, "has_vampire", False):
            self.player.heal(10)
        
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
    
    print("=== 肉鸽系统增益统计 ===")
    for rarity in range(4):
        count = stats.get(rarity, 0)
        print(f"稀有度 {rarity} ({RARITY_NAMES[rarity+1]}): {count} 个增益")
    print(f"总计: {len(BUFF_LIBRARY)} 个增益")
