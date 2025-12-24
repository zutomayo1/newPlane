# ==============================================================================
#   肉鸽（Roguelite）系统核心 - 升级、增益、局内成长
# ==============================================================================
import random
import pygame
import math
from config import *
from utils import sound_mgr, log_error, log_info, log_debug

# ==============================================================================
#   物品掉落系统（精简版 - 与现有ExperienceOrb共存）
# ==============================================================================

# 物品定义数据（只保留实用物品）
ITEM_TYPES = {
    # 恢复类
    "health": {
        "name": "医疗包", 
        "color": (0, 255, 100), 
        "value": 25,
        "icon": "+",
        "desc": "恢复25生命值"
    },
    "health_large": {
        "name": "大型医疗包", 
        "color": (0, 255, 150), 
        "value": 50,
        "icon": "++",
        "desc": "恢复50生命值"
    },
    "shield": {
        "name": "护盾充能", 
        "color": (100, 200, 255), 
        "value": 30,
        "icon": "S",
        "desc": "恢复30护盾值"
    },
    
    # 弹药类
    "ammo": {
        "name": "弹药箱", 
        "color": (255, 200, 0), 
        "value": 50,
        "icon": "A",
        "desc": "补充50弹药"
    },
    "ammo_large": {
        "name": "大型弹药箱", 
        "color": (255, 220, 50), 
        "value": 150,
        "icon": "AA",
        "desc": "大量补充弹药"
    },
    
    # 增益类（临时buff）
    "power_up": {
        "name": "火力强化", 
        "color": (255, 50, 50), 
        "value": 10,  # 持续时间(秒)
        "icon": "P",
        "desc": "攻击力+50%"
    },
    "speed_up": {
        "name": "速度强化", 
        "color": (50, 255, 255), 
        "value": 10,
        "icon": "V",
        "desc": "移动速度+30%"
    },
}

class Item:
    """游戏中掉落的物品（精简版 - 与ExperienceOrb共存）"""
    def __init__(self, item_type, x, y):
        self.type = item_type
        self.x = x
        self.y = y
        self.alive = True
        self.timer = 0
        self.lifetime = 600  # 10秒后消失
        
        # 加载物品数据
        if item_type in ITEM_TYPES:
            item_data = ITEM_TYPES[item_type]
            self.name = item_data["name"]
            self.color = item_data["color"]
            self.value = item_data["value"]
            self.icon = item_data.get("icon", "?")
            self.desc = item_data.get("desc", "")
        else:
            # 默认物品
            self.name = "未知物品"
            self.color = (255, 255, 255)
            self.value = 10
            self.icon = "?"
            self.desc = "未知效果"
        
        # 大小
        self.radius = 10
        
        # 物理属性（轻微弹跳）
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-2, 0)
        self.gravity = 0.15
        self.bounce = 0.4
    
    def update(self, target_x=None, target_y=None, magnet_range=150):
        """更新物品，实现吸取效果和物理效果"""
        self.timer += 1
        
        # 生命周期检查
        if self.timer >= self.lifetime:
            self.alive = False
            return
        
        # 吸取效果
        if target_x is not None and target_y is not None:
            dx = target_x - self.x
            dy = target_y - self.y
            dist = (dx**2 + dy**2) ** 0.5
            
            # 碰撞检测
            if dist < 30:
                self.alive = False
                return
            
            # 磁力吸取
            if dist < magnet_range:
                # 根据距离计算吸引速度
                speed = 8 if dist < magnet_range / 2 else 4
                if dist > 0:
                    self.x += dx / dist * speed
                    self.y += dy / dist * speed
                return
        
        # 物理模拟（未被吸引时）
        if self.timer < 60:  # 前60帧有物理效果
            self.vy += self.gravity
            self.x += self.vx
            self.y += self.vy
            
            # 地面反弹（使用固定值避免依赖HEIGHT）
            ground_level = 670  # 接近屏幕底部
            if self.y > ground_level:
                self.y = ground_level
                self.vy *= -self.bounce
                self.vx *= 0.8
                if abs(self.vy) < 0.5:
                    self.vy = 0
    
    def draw(self, surface):
        """绘制物品（根据类型绘制形象图案）"""
        if not self.alive:
            return
        
        # 闪烁效果（即将消失时）
        if self.timer > self.lifetime - 120:
            if (self.timer // 10) % 2 == 0:
                return
        
        # 轻微浮动和旋转
        float_offset = math.sin(self.timer * 0.08) * 3
        draw_y = int(self.y + float_offset)
        draw_x = int(self.x)
        rotation = (self.timer * 2) % 360
        pulse = math.sin(self.timer * 0.1) * 0.15 + 0.85
        
        # 外层脉冲光环
        glow_radius = int(self.radius * 2 * pulse)
        glow_surf = pygame.Surface((glow_radius * 3, glow_radius * 3), pygame.SRCALPHA)
        for i in range(4, 0, -1):
            alpha = int(40 * pulse / i)
            glow_color = (*self.color, alpha)
            pygame.draw.circle(glow_surf, glow_color, 
                             (glow_radius * 1.5, glow_radius * 1.5), 
                             glow_radius + i * 5)
        surface.blit(glow_surf, (draw_x - glow_radius * 1.5, draw_y - glow_radius * 1.5))
        
        # 根据类型绘制不同形状
        if self.type in ["health", "health_large"]:
            # 医疗包：红十字
            size = self.radius if self.type == "health" else self.radius * 1.3
            # 外框圆角矩形
            rect_surf = pygame.Surface((size * 2.2, size * 2.2), pygame.SRCALPHA)
            pygame.draw.rect(rect_surf, (255, 255, 255), (0, 0, size * 2.2, size * 2.2), border_radius=8)
            pygame.draw.rect(rect_surf, self.color, (3, 3, size * 2.2 - 6, size * 2.2 - 6), border_radius=6)
            surface.blit(rect_surf, (draw_x - size * 1.1, draw_y - size * 1.1))
            
            # 白色十字
            cross_w = size * 0.6
            cross_h = size * 0.2
            # 横
            pygame.draw.rect(surface, (255, 255, 255), 
                           (draw_x - cross_w/2, draw_y - cross_h/2, cross_w, cross_h))
            # 竖
            pygame.draw.rect(surface, (255, 255, 255), 
                           (draw_x - cross_h/2, draw_y - cross_w/2, cross_h, cross_w))
            
        elif self.type == "shield":
            # 护盾：盾牌形状
            # 盾牌轮廓点
            shield_points = [
                (draw_x, draw_y - self.radius * 1.2),  # 顶
                (draw_x + self.radius * 0.9, draw_y - self.radius * 0.6),
                (draw_x + self.radius * 0.9, draw_y + self.radius * 0.4),
                (draw_x, draw_y + self.radius * 1.2),  # 底尖
                (draw_x - self.radius * 0.9, draw_y + self.radius * 0.4),
                (draw_x - self.radius * 0.9, draw_y - self.radius * 0.6),
            ]
            # 阴影
            shadow_points = [(x + 2, y + 2) for x, y in shield_points]
            pygame.draw.polygon(surface, (0, 0, 0, 100), shadow_points)
            # 主体
            pygame.draw.polygon(surface, self.color, shield_points)
            pygame.draw.polygon(surface, (200, 230, 255), shield_points, 3)
            # 中心闪光
            pygame.draw.circle(surface, (255, 255, 255), (draw_x, draw_y), int(self.radius * 0.3))
            # 盾纹
            for i in range(-1, 2):
                pygame.draw.line(surface, (180, 220, 255), 
                               (draw_x + i * self.radius * 0.3, draw_y - self.radius * 0.6),
                               (draw_x + i * self.radius * 0.3, draw_y + self.radius * 0.6), 2)
            
        elif self.type in ["ammo", "ammo_large"]:
            # 弹药箱：子弹形状
            size = self.radius if self.type == "ammo" else self.radius * 1.3
            num_bullets = 3 if self.type == "ammo" else 5
            
            for i in range(num_bullets):
                offset = (i - (num_bullets - 1) / 2) * size * 0.5
                bullet_x = draw_x + offset
                bullet_y = draw_y
                
                # 子弹头（圆锥形）
                bullet_points = [
                    (bullet_x, bullet_y - size * 0.6),  # 尖端
                    (bullet_x - size * 0.2, bullet_y),
                    (bullet_x - size * 0.2, bullet_y + size * 0.4),
                    (bullet_x + size * 0.2, bullet_y + size * 0.4),
                    (bullet_x + size * 0.2, bullet_y),
                ]
                pygame.draw.polygon(surface, (255, 200, 0), bullet_points)
                pygame.draw.polygon(surface, (255, 255, 100), bullet_points, 2)
                
                # 弹壳
                pygame.draw.rect(surface, (180, 140, 0),
                               (bullet_x - size * 0.15, bullet_y + size * 0.4, size * 0.3, size * 0.4))
                pygame.draw.rect(surface, (220, 180, 0),
                               (bullet_x - size * 0.15, bullet_y + size * 0.4, size * 0.3, size * 0.4), 1)
            
        elif self.type == "power_up":
            # 火力强化：火焰/爆炸图标
            # 旋转光束
            for angle_offset in [0, 72, 144, 216, 288]:
                angle = math.radians(rotation + angle_offset)
                beam_len = self.radius * 1.5 * pulse
                end_x = draw_x + math.cos(angle) * beam_len
                end_y = draw_y + math.sin(angle) * beam_len
                pygame.draw.line(surface, (255, 100, 50), 
                               (draw_x, draw_y), (int(end_x), int(end_y)), 3)
            
            # 火焰形状（多层）
            for layer in range(3):
                flame_size = self.radius * (1.0 - layer * 0.25)
                flame_color = [(255, 50, 50), (255, 150, 0), (255, 255, 100)][layer]
                
                # 火焰点
                flame_points = []
                for i in range(5):
                    angle = math.radians(i * 72 - rotation * 2)
                    if i % 2 == 0:
                        r = flame_size
                    else:
                        r = flame_size * 0.5
                    px = draw_x + math.cos(angle) * r
                    py = draw_y + math.sin(angle) * r
                    flame_points.append((px, py))
                
                pygame.draw.polygon(surface, flame_color, flame_points)
            
            # 中心高光
            pygame.draw.circle(surface, (255, 255, 255), (draw_x, draw_y), int(self.radius * 0.3))
            
        elif self.type == "speed_up":
            # 速度强化：闪电/翅膀
            # 双翼形状
            wing_points_left = [
                (draw_x - self.radius * 0.3, draw_y),
                (draw_x - self.radius * 1.2, draw_y - self.radius * 0.6),
                (draw_x - self.radius * 1.4, draw_y),
                (draw_x - self.radius * 1.2, draw_y + self.radius * 0.6),
            ]
            wing_points_right = [
                (draw_x + self.radius * 0.3, draw_y),
                (draw_x + self.radius * 1.2, draw_y - self.radius * 0.6),
                (draw_x + self.radius * 1.4, draw_y),
                (draw_x + self.radius * 1.2, draw_y + self.radius * 0.6),
            ]
            
            # 绘制翅膀
            pygame.draw.polygon(surface, self.color, wing_points_left)
            pygame.draw.polygon(surface, (150, 255, 255), wing_points_left, 2)
            pygame.draw.polygon(surface, self.color, wing_points_right)
            pygame.draw.polygon(surface, (150, 255, 255), wing_points_right, 2)
            
            # 中心圆
            pygame.draw.circle(surface, (100, 255, 255), (draw_x, draw_y), int(self.radius * 0.8))
            pygame.draw.circle(surface, (255, 255, 255), (draw_x, draw_y), int(self.radius * 0.5))
            
            # 速度线
            for i in range(3):
                line_y = draw_y + (i - 1) * self.radius * 0.5
                pygame.draw.line(surface, (200, 255, 255),
                               (draw_x - self.radius * 0.4, line_y),
                               (draw_x + self.radius * 0.4, line_y), 2)
        
        # 粒子特效
        if self.timer % 10 == 0:
            angle = random.uniform(0, math.pi * 2)
            particle_x = draw_x + math.cos(angle) * self.radius * 1.2
            particle_y = draw_y + math.sin(angle) * self.radius * 1.2
            pygame.draw.circle(surface, (255, 255, 200), 
                             (int(particle_x), int(particle_y)), 2)


class ItemManager:
    """管理游戏中的物品（精简版 - 只管理特殊物品，不包括经验球）"""
    
    # 掉落概率配置（降低总体掉落率）
    DROP_CHANCES = {
        "health": 0.08,        # 8%掉血包
        "health_large": 0.02,  # 2%掉大血包
        "shield": 0.05,        # 5%掉护盾
        "ammo": 0.10,          # 10%掉弹药
        "ammo_large": 0.02,    # 2%掉大弹药
        "power_up": 0.015,     # 1.5%掉火力buff
        "speed_up": 0.015,     # 1.5%掉速度buff
    }
    
    def __init__(self):
        self.items = []
        self.total_drops = 0
        self.pickup_count = {}
        
    def spawn_item(self, item_type, x, y):
        """在指定位置生成物品"""
        if item_type not in ITEM_TYPES:
            return None
        item = Item(item_type, x, y)
        self.items.append(item)
        self.total_drops += 1
        return item
    
    def try_spawn_drop(self, x, y, force_type=None):
        """尝试掉落物品（概率性）"""
        if force_type:
            return self.spawn_item(force_type, x, y)
        
        # 随机判断是否掉落
        for item_type, chance in self.DROP_CHANCES.items():
            if random.random() < chance:
                # 添加随机偏移
                offset_x = random.uniform(-20, 20)
                offset_y = random.uniform(-20, 20)
                return self.spawn_item(item_type, x + offset_x, y + offset_y)
        
        return None
    
    def spawn_boss_drops(self, x, y):
        """Boss必定掉落好东西"""
        drops = []
        # Boss保底掉落（减少数量避免过多）
        drops.append(self.spawn_item("health_large", x - 20, y))
        drops.append(self.spawn_item("power_up", x + 20, y))
        return drops
    
    def update(self, player=None):
        """更新所有物品，处理吸取"""
        magnet_range = 150
        if player and hasattr(player, 'pickup_range'):
            magnet_range = player.pickup_range
        
        for item in self.items[:]:  # 使用切片避免迭代时修改列表
            if player:
                # 计算距离
                dx = player.rect.centerx - item.x
                dy = player.rect.centery - item.y
                dist = (dx**2 + dy**2) ** 0.5
                
                # 碰撞检测
                if dist < 30:
                    self.pickup_item(item, player)
                    continue
                
                # 更新物品（带吸取效果）
                item.update(player.rect.centerx, player.rect.centery, magnet_range)
            else:
                item.update()
        
        # 清理死亡物品
        self.items = [item for item in self.items if item.alive]
    
    def clear_all(self):
        """清除所有物品"""
        self.items.clear()
    
    def get_item_count(self):
        """获取当前物品数量"""
        return len(self.items)
    
    def pickup_item(self, item, player):
        """拾起物品，应用效果"""
        sound_mgr.play("item_pickup")
        
        # 统计拾取
        self.pickup_count[item.type] = self.pickup_count.get(item.type, 0) + 1
        
        # 恢复类物品
        if item.type in ["health", "health_large"]:
            old_hp = player.hp
            player.hp = min(player.max_hp, player.hp + item.value)
            actual_heal = player.hp - old_hp
            self._show_pickup_text(player, f"+{actual_heal} HP", (0, 255, 100))
            
        elif item.type == "shield":
            if hasattr(player, 'shield') and hasattr(player, 'max_shield'):
                old_shield = player.shield
                player.shield = min(player.max_shield, player.shield + item.value)
                actual_shield = player.shield - old_shield
                if actual_shield > 0:
                    self._show_pickup_text(player, f"+{actual_shield} 护盾", (100, 200, 255))
        
        # 弹药类物品
        elif item.type in ["ammo", "ammo_large"]:
            added = False
            if hasattr(player, 'weapon_slots') and player.current_slot < len(player.weapon_slots):
                slot = player.weapon_slots[player.current_slot]
                if slot and hasattr(slot, 'ammo') and hasattr(slot, 'max_ammo'):
                    old_ammo = slot.ammo
                    slot.ammo = min(slot.max_ammo, slot.ammo + item.value)
                    actual_ammo = slot.ammo - old_ammo
                    if actual_ammo > 0:
                        self._show_pickup_text(player, f"+{actual_ammo} 弹药", (255, 200, 0))
                        added = True
            if not added:
                self._show_pickup_text(player, "弹药箱", (255, 200, 0))
        
        # 增益类物品（临时buff）
        elif item.type == "power_up":
            self._apply_buff(player, "power", item.value)
            self._show_pickup_text(player, "火力强化!", (255, 50, 50))
            
        elif item.type == "speed_up":
            self._apply_buff(player, "speed", item.value)
            self._show_pickup_text(player, "速度强化!", (50, 255, 255))
        
        item.alive = False
    
    def _apply_buff(self, player, buff_type, duration):
        """应用临时增益效果（简化版）"""
        if not hasattr(player, 'active_buffs'):
            player.active_buffs = {}
        
        # 设置buff持续时间(帧数)
        buff_frames = duration * 60  # 秒转帧
        player.active_buffs[buff_type] = buff_frames
        
        # 存储原始值（如果是第一次获得此buff）
        if buff_type == "power":
            if not hasattr(player, '_original_damage'):
                player._original_damage = player.damage
            player.damage = int(player._original_damage * 1.5)  # +50%
        elif buff_type == "speed":
            if not hasattr(player, '_original_speed'):
                player._original_speed = player.speed
            player.speed = player._original_speed * 1.3  # +30%
    
    def update_buffs(self, player):
        """更新玩家的buff状态（需要在游戏循环中调用）"""
        if not hasattr(player, 'active_buffs'):
            return
        
        # 更新所有buff计时
        expired_buffs = []
        for buff_type, remaining_frames in list(player.active_buffs.items()):
            player.active_buffs[buff_type] -= 1
            
            if player.active_buffs[buff_type] <= 0:
                expired_buffs.append(buff_type)
        
        # 移除过期buff并恢复属性
        for buff_type in expired_buffs:
            del player.active_buffs[buff_type]
            
            if buff_type == "power" and hasattr(player, '_original_damage'):
                player.damage = player._original_damage
            elif buff_type == "speed" and hasattr(player, '_original_speed'):
                player.speed = player._original_speed
    
    def _show_pickup_text(self, player, text, color):
        """显示拾取文本"""
        try:
            from sprites import FloatingText
            FloatingText(player.rect.centerx, player.rect.top - 20, text, color)
        except:
            pass
    
    def draw(self, surface):
        """绘制所有物品"""
        for item in self.items:
            item.draw(surface)

# ==============================================================================
#   成就系统（Achievement）
# ==============================================================================
class Achievement:
    """成就类 - 豪华版"""
    # 稀有度颜色映射
    RARITY_COLORS = {
        "common": (180, 180, 180),      # 普通 - 银灰
        "rare": (100, 220, 100),         # 稀有 - 绿色
        "epic": (180, 100, 220),         # 史诗 - 紫色
        "legendary": (255, 215, 0),      # 传说 - 金色
    }
    
    # 分类图标映射
    CATEGORY_ICONS = {
        "combat": "⚔",
        "boss": "👹",
        "survival": "🛡",
        "plane": "✈",
        "roguelike": "🚪",
        "efficiency": "⚡",
        "milestone": "🎖",
        "secret": "🌙",
    }
    
    def __init__(self, achievement_id, name, description, icon_char="★", reward=100, category="combat", hidden=False, target=0):
        self.id = achievement_id
        self.name = name
        self.description = description
        self.icon_char = icon_char
        self.reward = reward
        self.category = category      # 分类
        self.hidden = hidden          # 是否隐藏成就
        self.target = target          # 目标值（用于进度显示）
        self.unlocked = False
        self.unlock_time = None
        self.unlock_date = None       # 解锁日期字符串
    
    @property
    def rarity(self):
        """根据奖励计算稀有度"""
        if self.reward >= 1000:
            return "legendary"
        elif self.reward >= 600:
            return "epic"
        elif self.reward >= 300:
            return "rare"
        return "common"
    
    @property
    def rarity_name(self):
        """稀有度中文名"""
        names = {"common": "普通", "rare": "稀有", "epic": "史诗", "legendary": "传说"}
        return names.get(self.rarity, "普通")
    
    @property
    def rarity_color(self):
        """获取稀有度对应颜色"""
        return self.RARITY_COLORS.get(self.rarity, (180, 180, 180))
    
    def unlock(self):
        """解锁成就"""
        if not self.unlocked:
            self.unlocked = True
            self.unlock_time = pygame.time.get_ticks()
            # 记录解锁日期
            import datetime
            self.unlock_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            sound_mgr.play("achievement")
            return True
        return False
    
    def get_progress(self, current_value):
        """获取进度百分比"""
        if self.target <= 0:
            return 100 if self.unlocked else 0
        return min(100, int(current_value / self.target * 100))


class AchievementManager:
    """管理成就系统 - 豪华版"""
    def __init__(self):
        self.achievements = self._init_achievements()
        self.stats = {
            # === 基础统计 ===
            "total_kills": 0,           # 总击杀数
            "total_damage": 0,          # 最大单次伤害
            "runs_completed": 0,        # 完成的游戏数
            "bosses_killed": 0,         # 击杀的BOSS数
            "max_wave": 0,              # 最高波数
            "max_combo": 0,             # 最高连击
            "upgrades_collected": 0,    # 收集的升级数
            "perfect_runs": 0,          # 完美通关（无伤）
            # === 新增统计 ===
            "total_score": 0,           # 累计总分
            "total_playtime": 0,        # 累计游戏时间（秒）
            "planes_used": [],          # 使用过的机体ID列表
            "skins_used": [],           # 使用过的涂装ID列表
            "rooms_cleared": 0,         # 清理的房间数
            "elite_kills": 0,           # 击杀精英数
            "items_collected": 0,       # 收集道具数
            "bullets_fired": 0,         # 发射子弹数
            "crits_dealt": 0,           # 单局暴击次数
            "max_crits": 0,             # 最高单局暴击
            "dodges": 0,                # 闪避次数
            "max_multi_kill": 0,        # 最大同时击杀数
            "unique_bosses": [],        # 击杀过的Boss类型
            "cards_collected": [],      # 收集过的卡牌类型
            "login_days": [],           # 登录日期列表
            "night_plays": 0,           # 深夜游玩次数
            "max_wingmen": 0,           # 最多同时僚机数
            "plane_runs": {},           # 每个机体完成的局数
            "session_kills": 0,         # 当前会话击杀（用于闪电战神）
            "session_time": 0,          # 当前会话时间
            "lowest_hp_boss_kill": 100, # 击杀Boss时最低血量百分比
            "boss_kill_time": 999,      # 最快击杀Boss时间（秒）
        }
        # 临时状态标记
        self.temp_perfect_run = True
        self.temp_no_heal = True
        self.temp_survivor = False
    
    def _init_achievements(self):
        """初始化成就列表 - 65个成就"""
        return {
            # =============== 战斗成就 (combat) - 16个 ===============
            "first_blood": Achievement("first_blood", "初次杀戮", "击杀第一个敌人", "🗡", 50, "combat", target=1),
            "killer_100": Achievement("killer_100", "百杀者", "累计击杀100个敌人", "⚔", 200, "combat", target=100),
            "killer_500": Achievement("killer_500", "千杀者", "累计击杀500个敌人", "⚔", 400, "combat", target=500),
            "killer_1000": Achievement("killer_1000", "屠杀者", "累计击杀1000个敌人", "⚔", 800, "combat", target=1000),
            "killer_10000": Achievement("killer_10000", "万人斩", "累计击杀10000个敌人", "💀", 1500, "combat", target=10000),
            "killer_100000": Achievement("killer_100000", "十万屠夫", "累计击杀100000个敌人", "☠", 3000, "combat", target=100000),
            
            "combo_50": Achievement("combo_50", "连击大师", "达成50连击", "⚡", 200, "combat", target=50),
            "combo_100": Achievement("combo_100", "连击王者", "达成100连击", "⚡", 500, "combat", target=100),
            "combo_200": Achievement("combo_200", "连击之神", "达成200连击", "⚡", 1000, "combat", target=200),
            
            "damage_1000": Achievement("damage_1000", "破坏者", "单次伤害超过1000", "💥", 200, "combat", target=1000),
            "damage_5000": Achievement("damage_5000", "毁灭者", "单次伤害超过5000", "💥", 600, "combat", target=5000),
            "damage_10000": Achievement("damage_10000", "灾厄降临", "单次伤害超过10000", "💥", 1200, "combat", target=10000),
            
            "crit_master": Achievement("crit_master", "暴击狂人", "单局暴击100次", "🎯", 400, "combat", target=100),
            "bullet_storm": Achievement("bullet_storm", "弹幕大师", "单局发射10000发子弹", "🔫", 350, "combat", target=10000),
            "multi_kill_10": Achievement("multi_kill_10", "群体毁灭", "同时消灭10个敌人", "💣", 300, "combat", target=10),
            "multi_kill_30": Achievement("multi_kill_30", "以多打少", "同时消灭30个敌人", "💣", 700, "combat", target=30),
            
            # =============== Boss成就 (boss) - 9个 ===============
            "first_boss": Achievement("first_boss", "首领战胜者", "完成第一次Boss战", "👑", 250, "boss", target=1),
            "boss_slayer": Achievement("boss_slayer", "Boss猎人", "击杀任意Boss", "👹", 300, "boss", target=1),
            "boss_5": Achievement("boss_5", "噩梦终结者", "累计击杀5个Boss", "👹", 600, "boss", target=5),
            "boss_20": Achievement("boss_20", "Boss杀手", "累计击杀20个Boss", "👹", 1000, "boss", target=20),
            "boss_50": Achievement("boss_50", "Boss专家", "累计击杀50个Boss", "👹", 2000, "boss", target=50),
            "boss_challenger": Achievement("boss_challenger", "挑战大师", "完成Boss挑战模式", "🏆", 1500, "boss"),
            "boss_all_clear": Achievement("boss_all_clear", "终极猎人", "击杀所有类型的Boss", "🏆", 2500, "boss"),
            "boss_speedkill": Achievement("boss_speedkill", "秒杀专家", "5秒内击杀Boss", "⚡", 800, "boss", target=5),
            "boss_clutch": Achievement("boss_clutch", "临危不惧", "血量低于10%时击杀Boss", "💪", 1200, "boss"),
            
            # =============== 生存成就 (survival) - 10个 ===============
            "survivor": Achievement("survivor", "幸存者", "完成任何一局游戏", "🛡", 100, "survival"),
            "wave_10": Achievement("wave_10", "十波生存", "存活至第10波", "🌊", 250, "survival", target=10),
            "wave_20": Achievement("wave_20", "二十波生存", "存活至第20波", "🌊", 500, "survival", target=20),
            "wave_30": Achievement("wave_30", "无穷斗士", "存活至第30波", "🌊", 1000, "survival", target=30),
            "wave_50": Achievement("wave_50", "永恒战士", "存活至第50波", "🌊", 2000, "survival", target=50),
            "perfect_run": Achievement("perfect_run", "完美者", "无伤完成一局游戏", "✨", 1500, "survival"),
            "no_heal": Achievement("no_heal", "坚定的战士", "全程不使用医疗包完成一局", "❤", 700, "survival"),
            "clutch_1hp": Achievement("clutch_1hp", "压线生存", "以1点HP完成一局", "💔", 1200, "survival"),
            "dodge_master": Achievement("dodge_master", "闪避专家", "单局闪避50次敌方攻击", "🌀", 400, "survival", target=50),
            "phoenix": Achievement("phoenix", "不死鸟", "使用复活3次后仍然通关", "🔥", 800, "survival"),
            
            # =============== 机体成就 (plane) - 8个 ===============
            "plane_variety": Achievement("plane_variety", "百变战士", "使用10种不同机体完成游戏", "✈", 600, "plane", target=10),
            "plane_master": Achievement("plane_master", "机体大师", "使用20种不同机体完成游戏", "✈", 1500, "plane", target=20),
            "plane_loyal": Achievement("plane_loyal", "专一飞行员", "用同一机体完成10局游戏", "💕", 400, "plane", target=10),
            "skin_collector": Achievement("skin_collector", "涂装达人", "使用10种不同涂装", "🎨", 350, "plane", target=10),
            "skin_fashionista": Achievement("skin_fashionista", "时尚先锋", "使用5种不同涂装完成游戏", "👗", 250, "plane", target=5),
            "drone_squad": Achievement("drone_squad", "天空统治者", "同时拥有3个僚机存活", "🤖", 400, "plane", target=3),
            "drone_master": Achievement("drone_master", "编队指挥官", "拥有4个僚机并完成一局", "🤖", 600, "plane", target=4),
            "drone_army": Achievement("drone_army", "机械军团", "同时拥有6个僚机", "🤖", 1000, "plane", target=6),
            
            # =============== Roguelike成就 (roguelike) - 9个 ===============
            "room_10": Achievement("room_10", "探索者", "完成10个房间", "🚪", 200, "roguelike", target=10),
            "room_30": Achievement("room_30", "迷宫行者", "完成30个房间", "🚪", 450, "roguelike", target=30),
            "room_100": Achievement("room_100", "迷宫大师", "完成100个房间", "🚪", 1000, "roguelike", target=100),
            "elite_hunter": Achievement("elite_hunter", "精英猎手", "击败10个精英敌人", "⭐", 300, "roguelike", target=10),
            "elite_slayer": Achievement("elite_slayer", "精英杀手", "击败50个精英敌人", "⭐", 700, "roguelike", target=50),
            "item_hoarder": Achievement("item_hoarder", "宝藏猎人", "收集50个道具", "📦", 350, "roguelike", target=50),
            "card_collector": Achievement("card_collector", "卡牌收藏家", "收集所有类型的升级卡牌", "🃏", 800, "roguelike"),
            "fully_loaded": Achievement("fully_loaded", "满配战神", "同时拥有10个升级增益", "💎", 700, "roguelike", target=10),
            "collector": Achievement("collector", "收藏家", "集齐所有升级卡牌类型", "📚", 900, "roguelike"),
            
            # =============== 效率成就 (efficiency) - 6个 ===============
            "rich": Achievement("rich", "暴富者", "单局获得100000分", "💰", 600, "efficiency", target=100000),
            "millionaire": Achievement("millionaire", "百万富翁", "累计获得1000000分", "💎", 1500, "efficiency", target=1000000),
            "speedrun": Achievement("speedrun", "闪电战士", "3分钟内获得50000分", "⚡", 450, "efficiency"),
            "fast_clear": Achievement("fast_clear", "急速前进", "2分钟内到达第10波", "🔥", 350, "efficiency"),
            "blitz_100": Achievement("blitz_100", "闪电战神", "1分钟内击杀100敌人", "⚡", 500, "efficiency", target=100),
            "marathon": Achievement("marathon", "马拉松", "单局游戏超过30分钟", "🏃", 500, "efficiency", target=1800),
            
            # =============== 里程碑成就 (milestone) - 7个 ===============
            "runs_10": Achievement("runs_10", "老兵", "累计游戏10局", "🎖", 200, "milestone", target=10),
            "runs_50": Achievement("runs_50", "资深飞行员", "累计游戏50局", "🎖", 500, "milestone", target=50),
            "runs_100": Achievement("runs_100", "百战老兵", "累计游戏100局", "🎖", 1000, "milestone", target=100),
            "playtime_1h": Achievement("playtime_1h", "入门玩家", "累计游戏时长1小时", "⏰", 150, "milestone", target=3600),
            "playtime_10h": Achievement("playtime_10h", "持久战", "累计游戏时长10小时", "⏰", 600, "milestone", target=36000),
            "playtime_100h": Achievement("playtime_100h", "时间领主", "累计游戏时长100小时", "⏰", 2000, "milestone", target=360000),
            "all_clear": Achievement("all_clear", "传奇飞行员", "解锁全部成就", "👑", 5000, "milestone"),
            
            # =============== 隐藏成就 (secret) - 6个 ===============
            "night_owl": Achievement("night_owl", "夜猫子", "在凌晨3点游玩", "🌙", 100, "secret", hidden=True),
            "pacifist": Achievement("pacifist", "和平主义者", "只使用僚机击杀完成一波", "☮", 400, "secret", hidden=True),
            "music_lover": Achievement("music_lover", "音乐鉴赏家", "听完所有BGM", "🎵", 200, "secret", hidden=True),
            "easter_egg": Achievement("easter_egg", "彩蛋猎人", "发现隐藏彩蛋", "🥚", 300, "secret", hidden=True),
            "lucky_7": Achievement("lucky_7", "幸运七", "分数正好是77777", "🍀", 777, "secret", hidden=True),
            "dedication": Achievement("dedication", "坚持不懈", "连续7天登录游戏", "📅", 600, "secret", hidden=True),
        }
    
    def check_achievements(self, player):
        """检查是否解锁成就 - 完整版"""
        unlocked = []
        
        # ===== 战斗成就 =====
        kills = self.stats["total_kills"]
        if kills >= 1 and self.achievements["first_blood"].unlock():
            unlocked.append("first_blood")
        if kills >= 100 and self.achievements["killer_100"].unlock():
            unlocked.append("killer_100")
        if kills >= 500 and self.achievements["killer_500"].unlock():
            unlocked.append("killer_500")
        if kills >= 1000 and self.achievements["killer_1000"].unlock():
            unlocked.append("killer_1000")
        if kills >= 10000 and self.achievements["killer_10000"].unlock():
            unlocked.append("killer_10000")
        if kills >= 100000 and self.achievements["killer_100000"].unlock():
            unlocked.append("killer_100000")
        
        # 连击检查
        combo = self.stats["max_combo"]
        if combo >= 50 and self.achievements["combo_50"].unlock():
            unlocked.append("combo_50")
        if combo >= 100 and self.achievements["combo_100"].unlock():
            unlocked.append("combo_100")
        if combo >= 200 and self.achievements["combo_200"].unlock():
            unlocked.append("combo_200")
        
        # 伤害检查
        dmg = self.stats["total_damage"]
        if dmg >= 1000 and self.achievements["damage_1000"].unlock():
            unlocked.append("damage_1000")
        if dmg >= 5000 and self.achievements["damage_5000"].unlock():
            unlocked.append("damage_5000")
        if dmg >= 10000 and self.achievements["damage_10000"].unlock():
            unlocked.append("damage_10000")
        
        # 暴击检查
        if self.stats["max_crits"] >= 100 and self.achievements["crit_master"].unlock():
            unlocked.append("crit_master")
        
        # 多杀检查
        multi = self.stats["max_multi_kill"]
        if multi >= 10 and self.achievements["multi_kill_10"].unlock():
            unlocked.append("multi_kill_10")
        if multi >= 30 and self.achievements["multi_kill_30"].unlock():
            unlocked.append("multi_kill_30")
        
        # ===== Boss成就 =====
        bosses = self.stats["bosses_killed"]
        if bosses >= 1:
            if self.achievements["boss_slayer"].unlock():
                unlocked.append("boss_slayer")
            if self.achievements["first_boss"].unlock():
                unlocked.append("first_boss")
        if bosses >= 5 and self.achievements["boss_5"].unlock():
            unlocked.append("boss_5")
        if bosses >= 20 and self.achievements["boss_20"].unlock():
            unlocked.append("boss_20")
        if bosses >= 50 and self.achievements["boss_50"].unlock():
            unlocked.append("boss_50")
        
        # 秒杀Boss
        if self.stats["boss_kill_time"] <= 5 and self.achievements["boss_speedkill"].unlock():
            unlocked.append("boss_speedkill")
        
        # 临危不惧
        if self.stats["lowest_hp_boss_kill"] <= 10 and self.achievements["boss_clutch"].unlock():
            unlocked.append("boss_clutch")
        
        # ===== 生存成就 =====
        wave = self.stats["max_wave"]
        if wave >= 10 and self.achievements["wave_10"].unlock():
            unlocked.append("wave_10")
        if wave >= 20 and self.achievements["wave_20"].unlock():
            unlocked.append("wave_20")
        if wave >= 30 and self.achievements["wave_30"].unlock():
            unlocked.append("wave_30")
        if wave >= 50 and self.achievements["wave_50"].unlock():
            unlocked.append("wave_50")
        
        # 僚机检查
        wingmen = self.stats.get("max_wingmen", 0)
        if hasattr(player, 'wingman_squadron') and player.wingman_squadron:
            wingmen = max(wingmen, len(player.wingman_squadron.wingmen))
            self.stats["max_wingmen"] = wingmen
        if wingmen >= 3 and self.achievements["drone_squad"].unlock():
            unlocked.append("drone_squad")
        if wingmen >= 4 and self.achievements["drone_master"].unlock():
            unlocked.append("drone_master")
        if wingmen >= 6 and self.achievements["drone_army"].unlock():
            unlocked.append("drone_army")
        
        # ===== 机体成就 =====
        planes_used = len(self.stats.get("planes_used", []))
        if planes_used >= 10 and self.achievements["plane_variety"].unlock():
            unlocked.append("plane_variety")
        if planes_used >= 20 and self.achievements["plane_master"].unlock():
            unlocked.append("plane_master")
        
        # 专一飞行员
        plane_runs = self.stats.get("plane_runs", {})
        if any(runs >= 10 for runs in plane_runs.values()):
            if self.achievements["plane_loyal"].unlock():
                unlocked.append("plane_loyal")
        
        # 涂装
        skins_used = len(self.stats.get("skins_used", []))
        if skins_used >= 10 and self.achievements["skin_collector"].unlock():
            unlocked.append("skin_collector")
        if skins_used >= 5 and self.achievements["skin_fashionista"].unlock():
            unlocked.append("skin_fashionista")
        
        # ===== Roguelike成就 =====
        rooms = self.stats.get("rooms_cleared", 0)
        if rooms >= 10 and self.achievements["room_10"].unlock():
            unlocked.append("room_10")
        if rooms >= 30 and self.achievements["room_30"].unlock():
            unlocked.append("room_30")
        if rooms >= 100 and self.achievements["room_100"].unlock():
            unlocked.append("room_100")
        
        elites = self.stats.get("elite_kills", 0)
        if elites >= 10 and self.achievements["elite_hunter"].unlock():
            unlocked.append("elite_hunter")
        if elites >= 50 and self.achievements["elite_slayer"].unlock():
            unlocked.append("elite_slayer")
        
        items = self.stats.get("items_collected", 0)
        if items >= 50 and self.achievements["item_hoarder"].unlock():
            unlocked.append("item_hoarder")
        
        # ===== 效率成就 =====
        total_score = self.stats.get("total_score", 0)
        if total_score >= 1000000 and self.achievements["millionaire"].unlock():
            unlocked.append("millionaire")
        
        # ===== 里程碑成就 =====
        runs = self.stats.get("runs_completed", 0)
        if runs >= 10 and self.achievements["runs_10"].unlock():
            unlocked.append("runs_10")
        if runs >= 50 and self.achievements["runs_50"].unlock():
            unlocked.append("runs_50")
        if runs >= 100 and self.achievements["runs_100"].unlock():
            unlocked.append("runs_100")
        
        playtime = self.stats.get("total_playtime", 0)
        if playtime >= 3600 and self.achievements["playtime_1h"].unlock():
            unlocked.append("playtime_1h")
        if playtime >= 36000 and self.achievements["playtime_10h"].unlock():
            unlocked.append("playtime_10h")
        if playtime >= 360000 and self.achievements["playtime_100h"].unlock():
            unlocked.append("playtime_100h")
        
        # ===== 隐藏成就 =====
        # 夜猫子检查
        import datetime
        now = datetime.datetime.now()
        if now.hour == 3 and self.achievements["night_owl"].unlock():
            unlocked.append("night_owl")
        
        # 连续登录检查
        login_days = self.stats.get("login_days", [])
        if len(login_days) >= 7:
            # 检查是否连续7天
            try:
                dates = sorted([datetime.datetime.strptime(d, "%Y-%m-%d") for d in login_days[-7:]])
                consecutive = all((dates[i+1] - dates[i]).days == 1 for i in range(6))
                if consecutive and self.achievements["dedication"].unlock():
                    unlocked.append("dedication")
            except:
                pass
        
        # ===== 游戏结束时的特殊成就 =====
        if self.temp_perfect_run and self.temp_survivor:
            if self.achievements["perfect_run"].unlock():
                unlocked.append("perfect_run")
        
        if self.temp_no_heal and self.temp_survivor:
            if self.achievements["no_heal"].unlock():
                unlocked.append("no_heal")
        
        if self.temp_survivor:
            if self.achievements["survivor"].unlock():
                unlocked.append("survivor")
        
        # ===== 全成就检查 =====
        total_ach = len(self.achievements) - 1  # 排除all_clear自身
        unlocked_count = sum(1 for a in self.achievements.values() if a.unlocked and a.id != "all_clear")
        if unlocked_count >= total_ach and self.achievements["all_clear"].unlock():
            unlocked.append("all_clear")
        
        return unlocked
    
    def get_progress(self, achievement_id):
        """获取成就进度"""
        if achievement_id not in self.achievements:
            return 0, 0
        
        ach = self.achievements[achievement_id]
        target = ach.target
        
        # 根据成就类型获取当前值
        progress_map = {
            "first_blood": self.stats["total_kills"],
            "killer_100": self.stats["total_kills"],
            "killer_500": self.stats["total_kills"],
            "killer_1000": self.stats["total_kills"],
            "killer_10000": self.stats["total_kills"],
            "killer_100000": self.stats["total_kills"],
            "combo_50": self.stats["max_combo"],
            "combo_100": self.stats["max_combo"],
            "combo_200": self.stats["max_combo"],
            "damage_1000": self.stats["total_damage"],
            "damage_5000": self.stats["total_damage"],
            "damage_10000": self.stats["total_damage"],
            "crit_master": self.stats.get("max_crits", 0),
            "multi_kill_10": self.stats.get("max_multi_kill", 0),
            "multi_kill_30": self.stats.get("max_multi_kill", 0),
            "first_boss": self.stats["bosses_killed"],
            "boss_slayer": self.stats["bosses_killed"],
            "boss_5": self.stats["bosses_killed"],
            "boss_20": self.stats["bosses_killed"],
            "boss_50": self.stats["bosses_killed"],
            "wave_10": self.stats["max_wave"],
            "wave_20": self.stats["max_wave"],
            "wave_30": self.stats["max_wave"],
            "wave_50": self.stats["max_wave"],
            "drone_squad": self.stats.get("max_wingmen", 0),
            "drone_master": self.stats.get("max_wingmen", 0),
            "drone_army": self.stats.get("max_wingmen", 0),
            "plane_variety": len(self.stats.get("planes_used", [])),
            "plane_master": len(self.stats.get("planes_used", [])),
            "skin_collector": len(self.stats.get("skins_used", [])),
            "room_10": self.stats.get("rooms_cleared", 0),
            "room_30": self.stats.get("rooms_cleared", 0),
            "room_100": self.stats.get("rooms_cleared", 0),
            "elite_hunter": self.stats.get("elite_kills", 0),
            "elite_slayer": self.stats.get("elite_kills", 0),
            "item_hoarder": self.stats.get("items_collected", 0),
            "millionaire": self.stats.get("total_score", 0),
            "runs_10": self.stats.get("runs_completed", 0),
            "runs_50": self.stats.get("runs_completed", 0),
            "runs_100": self.stats.get("runs_completed", 0),
            "playtime_1h": self.stats.get("total_playtime", 0),
            "playtime_10h": self.stats.get("total_playtime", 0),
            "playtime_100h": self.stats.get("total_playtime", 0),
        }
        
        current = progress_map.get(achievement_id, 0)
        return min(current, target) if target > 0 else (target if ach.unlocked else 0), target
    
    def get_achievements_by_category(self, category=None):
        """按分类获取成就列表"""
        if category is None:
            return list(self.achievements.values())
        return [a for a in self.achievements.values() if a.category == category]
    
    def get_top_achievements(self, count=5):
        """获取已解锁的最高奖励成就"""
        unlocked = [a for a in self.achievements.values() if a.unlocked]
        return sorted(unlocked, key=lambda x: x.reward, reverse=True)[:count]
    
    def get_category_stats(self):
        """获取各分类的解锁统计"""
        categories = {}
        for ach in self.achievements.values():
            cat = ach.category
            if cat not in categories:
                categories[cat] = {"total": 0, "unlocked": 0}
            categories[cat]["total"] += 1
            if ach.unlocked:
                categories[cat]["unlocked"] += 1
        return categories
    
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
        
        # 准备要保存的数据（包含解锁日期）
        unlocked_data = {}
        for ach_id, ach in self.achievements.items():
            if ach.unlocked:
                unlocked_data[ach_id] = {
                    "unlock_date": ach.unlock_date or "未知"
                }
        
        # 确保列表类型的stats可以序列化
        stats_copy = {}
        for key, value in self.stats.items():
            if isinstance(value, (list, dict)):
                stats_copy[key] = value
            else:
                stats_copy[key] = value
        
        data = {
            "stats": stats_copy,
            "unlocked": unlocked_data,
            "version": 2  # 新版本标记
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
                for key, value in data["stats"].items():
                    if key in self.stats:
                        self.stats[key] = value
                    else:
                        self.stats[key] = value  # 添加新的统计项
            
            # 恢复已解锁成就（兼容新旧格式）
            if "unlocked" in data:
                unlocked = data["unlocked"]
                if isinstance(unlocked, list):
                    # 旧格式：列表
                    for ach_id in unlocked:
                        if ach_id in self.achievements:
                            self.achievements[ach_id].unlocked = True
                elif isinstance(unlocked, dict):
                    # 新格式：字典带解锁日期
                    for ach_id, info in unlocked.items():
                        if ach_id in self.achievements:
                            self.achievements[ach_id].unlocked = True
                            if isinstance(info, dict):
                                self.achievements[ach_id].unlock_date = info.get("unlock_date")
            
            log_info(f"成就数据已从 {filename} 加载")
            return True
        except Exception as e:
            log_error(f"加载成就数据失败: {e}")
            return False
    
    def record_login(self):
        """记录今日登录"""
        import datetime
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if today not in self.stats.get("login_days", []):
            if "login_days" not in self.stats:
                self.stats["login_days"] = []
            self.stats["login_days"].append(today)
            # 只保留最近30天
            self.stats["login_days"] = self.stats["login_days"][-30:]
    
    def record_plane_usage(self, plane_id):
        """记录机体使用"""
        if plane_id not in self.stats.get("planes_used", []):
            if "planes_used" not in self.stats:
                self.stats["planes_used"] = []
            self.stats["planes_used"].append(plane_id)
        
        # 记录该机体完成的局数
        if "plane_runs" not in self.stats:
            self.stats["plane_runs"] = {}
        self.stats["plane_runs"][plane_id] = self.stats["plane_runs"].get(plane_id, 0) + 1
    
    def record_skin_usage(self, skin_id):
        """记录涂装使用"""
        if skin_id and skin_id not in self.stats.get("skins_used", []):
            if "skins_used" not in self.stats:
                self.stats["skins_used"] = []
            self.stats["skins_used"].append(skin_id)
    
    def record_boss_kill(self, boss_type, hp_percent, kill_time):
        """记录Boss击杀详情"""
        self.stats["bosses_killed"] += 1
        
        # 记录Boss类型
        if boss_type not in self.stats.get("unique_bosses", []):
            if "unique_bosses" not in self.stats:
                self.stats["unique_bosses"] = []
            self.stats["unique_bosses"].append(boss_type)
        
        # 记录最低血量击杀
        self.stats["lowest_hp_boss_kill"] = min(self.stats.get("lowest_hp_boss_kill", 100), hp_percent)
        
        # 记录最快击杀
        self.stats["boss_kill_time"] = min(self.stats.get("boss_kill_time", 999), kill_time)
    
    def add_score(self, score):
        """累加分数"""
        self.stats["total_score"] = self.stats.get("total_score", 0) + score
    
    def add_playtime(self, seconds):
        """累加游戏时间"""
        self.stats["total_playtime"] = self.stats.get("total_playtime", 0) + seconds
    
    def complete_run(self):
        """完成一局游戏"""
        self.stats["runs_completed"] = self.stats.get("runs_completed", 0) + 1
        self.temp_survivor = True

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
#   第一层：基础卡牌 (32种 - 每个流派8张)
# ==============================================================================
BASE_CARDS = {
    # ======== 弹幕流 (8张) - 专注火力覆盖和爆发伤害 ========
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
            {"level": 3, "effect": {"damage_mult": 0.3}, "desc": "伤害 +30%"},
            {"level": 4, "effect": {"bullet_count": 2}, "desc": "弹幕 +2"},
            {"level": 5, "effect": {"damage_mult": 0.5}, "desc": "伤害 +50%"}
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
            {"level": 3, "effect": {"split_damage": 0.2}, "desc": "分裂伤害 +20%"},
            {"level": 4, "effect": {"split_count": 2}, "desc": "分裂数 +2"},
            {"level": 5, "effect": {"split_damage": 0.3}, "desc": "分裂伤害 +30%"}
        ]
    },
    "explosive_round": {
        "name": "爆裂弹头",
        "category": "attack",
        "archetype": "barrage",
        "desc": "爆炸范围伤害",
        "base_effect": {"explosion_radius": 80, "explosion_mult": 0.6},
        "visual_seed": 1003,
        "pattern": "fractal",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"explosion_radius": 40}, "desc": "范围 +50%"},
            {"level": 3, "effect": {"explosion_mult": 0.3}, "desc": "爆炸伤害 +30%"},
            {"level": 4, "effect": {"explosion_radius": 60}, "desc": "范围 +75%"},
            {"level": 5, "effect": {"explosion_mult": 0.5}, "desc": "爆炸伤害 +50%"}
        ]
    },
    "rapid_fire": {
        "name": "极速射击",
        "category": "attack",
        "archetype": "barrage",
        "desc": "大幅提升射速，降低伤害",
        "base_effect": {"fire_rate_mult": 2.0, "damage_mult": -0.3},
        "visual_seed": 1004,
        "pattern": "wave",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"fire_rate_mult": 0.5}, "desc": "射速 +50%"},
            {"level": 3, "effect": {"damage_mult": 0.2}, "desc": "减伤惩罚降低"},
            {"level": 4, "effect": {"fire_rate_mult": 1.0}, "desc": "射速 +100%"},
            {"level": 5, "effect": {"damage_mult": 0.3}, "desc": "伤害恢复正常"}
        ]
    },
    "scatter_cannon": {
        "name": "散射炮",
        "category": "attack",
        "archetype": "barrage",
        "desc": "一次发射多发散弹",
        "base_effect": {"bullet_count": 5, "spread_angle": 30, "damage_mult": -0.2},
        "visual_seed": 1005,
        "pattern": "spiral",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"bullet_count": 2}, "desc": "散弹 +2"},
            {"level": 3, "effect": {"damage_mult": 0.1}, "desc": "伤害 +10%"},
            {"level": 4, "effect": {"bullet_count": 3}, "desc": "散弹 +3"},
            {"level": 5, "effect": {"spread_angle": -10}, "desc": "散射角度收窄"}
        ]
    },
    "ricochet_round": {
        "name": "弹跳弹",
        "category": "attack",
        "archetype": "barrage",
        "desc": "子弹碰壁反弹，可多次命中",
        "base_effect": {"bounce_count": 2, "bounce_damage": 0.8},
        "visual_seed": 1006,
        "pattern": "geometric",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"bounce_count": 1}, "desc": "反弹 +1"},
            {"level": 3, "effect": {"bounce_damage": 0.1}, "desc": "反弹伤害 +10%"},
            {"level": 4, "effect": {"bounce_count": 2}, "desc": "反弹 +2"},
            {"level": 5, "effect": {"bounce_damage": 0.2}, "desc": "反弹伤害 +20%"}
        ]
    },
    "cluster_bomb": {
        "name": "集束炸弹",
        "category": "attack",
        "archetype": "barrage",
        "desc": "子弹爆炸后释放小型炸弹",
        "base_effect": {"cluster_count": 5, "cluster_radius": 40},
        "visual_seed": 1007,
        "pattern": "fractal",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"cluster_count": 2}, "desc": "子弹药 +2"},
            {"level": 3, "effect": {"cluster_radius": 20}, "desc": "爆炸范围 +50%"},
            {"level": 4, "effect": {"cluster_count": 3}, "desc": "子弹药 +3"},
            {"level": 5, "effect": {"cluster_damage_mult": 0.3}, "desc": "子弹药伤害 +30%"}
        ]
    },
    "barrage_storm": {
        "name": "弹幕风暴",
        "category": "attack",
        "archetype": "barrage",
        "desc": "持续释放环形弹幕",
        "base_effect": {"storm_duration": 180, "storm_bullets": 20},
        "visual_seed": 1008,
        "pattern": "spiral",
        "rarity": 4,
        "upgrades": [
            {"level": 2, "effect": {"storm_bullets": 10}, "desc": "弹幕数 +50%"},
            {"level": 3, "effect": {"storm_duration": 120}, "desc": "持续时间 +2秒"},
            {"level": 4, "effect": {"storm_bullets": 20}, "desc": "弹幕数 +100%"},
            {"level": 5, "effect": {"storm_damage_mult": 0.5}, "desc": "风暴伤害 +50%"}
        ]
    },
    
    # ======== 狙击流 (8张) - 专注单体爆发和精准打击 ========
    "precision_beam": {
        "name": "精准光束",
        "category": "attack",
        "archetype": "sniper",
        "desc": "单发高伤穿透光束",
        "base_effect": {"damage_mult": 2.5, "pierce": 3, "fire_rate": 0.5},
        "visual_seed": 2001,
        "pattern": "geometric",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"pierce": 2}, "desc": "穿透 +2"},
            {"level": 3, "effect": {"damage_mult": 1.0}, "desc": "伤害 +40%"},
            {"level": 4, "effect": {"pierce": 3}, "desc": "穿透 +3"},
            {"level": 5, "effect": {"damage_mult": 1.5}, "desc": "伤害 +60%"}
        ]
    },
    "overcharge_shot": {
        "name": "超载射击",
        "category": "attack",
        "archetype": "sniper",
        "desc": "周期性发射超高威力子弹",
        "base_effect": {"overcharge_cooldown": 180, "overcharge_mult": 5.0},
        "visual_seed": 2002,
        "pattern": "wave",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"overcharge_mult": 2.0}, "desc": "超载倍率 ×7"},
            {"level": 3, "effect": {"overcharge_cooldown": -30}, "desc": "冷却时间 -17%"},
            {"level": 4, "effect": {"overcharge_mult": 3.0}, "desc": "超载倍率 ×10"},
            {"level": 5, "effect": {"overcharge_pierce": 999}, "desc": "超载穿透无限"}
        ]
    },
    "weakpoint_strike": {
        "name": "弱点打击",
        "category": "attack",
        "archetype": "sniper",
        "desc": "命中弱点造成额外暴击伤害",
        "base_effect": {"weakpoint_chance": 0.3, "weakpoint_mult": 3.0},
        "visual_seed": 2003,
        "pattern": "geometric",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"weakpoint_chance": 0.1}, "desc": "弱点率 +10%"},
            {"level": 3, "effect": {"weakpoint_mult": 1.0}, "desc": "弱点倍率 ×4"},
            {"level": 4, "effect": {"weakpoint_chance": 0.15}, "desc": "弱点率 +15%"},
            {"level": 5, "effect": {"weakpoint_mult": 2.0}, "desc": "弱点倍率 ×6"}
        ]
    },
    "armor_penetration": {
        "name": "破甲弹",
        "category": "attack",
        "archetype": "sniper",
        "desc": "无视敌人护甲造成真实伤害",
        "base_effect": {"armor_pen": 0.5, "bonus_vs_armor": 1.5},
        "visual_seed": 2004,
        "pattern": "fractal",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"armor_pen": 0.2}, "desc": "破甲 +20%"},
            {"level": 3, "effect": {"bonus_vs_armor": 0.5}, "desc": "对装甲 +50%"},
            {"level": 4, "effect": {"armor_pen": 0.2}, "desc": "破甲 +20%"},
            {"level": 5, "effect": {"armor_pen": 0.1, "bonus_vs_armor": 1.0}, "desc": "完全破甲"}
        ]
    },
    "railgun": {
        "name": "轨道炮",
        "category": "attack",
        "archetype": "sniper",
        "desc": "发射贯穿全屏的高速弹",
        "base_effect": {"pierce": 999, "damage_mult": 3.0, "fire_rate": 0.3},
        "visual_seed": 2005,
        "pattern": "geometric",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"damage_mult": 1.0}, "desc": "伤害 +33%"},
            {"level": 3, "effect": {"fire_rate": 0.1}, "desc": "冷却缩短"},
            {"level": 4, "effect": {"damage_mult": 1.5}, "desc": "伤害 +50%"},
            {"level": 5, "effect": {"railgun_explosion": 80}, "desc": "穿透时爆炸"}
        ]
    },
    "assassin_mark": {
        "name": "刺客标记",
        "category": "attack",
        "archetype": "sniper",
        "desc": "标记敌人，下次攻击必定暴击",
        "base_effect": {"mark_duration": 180, "mark_crit_mult": 4.0},
        "visual_seed": 2006,
        "pattern": "spiral",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"mark_crit_mult": 1.0}, "desc": "标记倍率 ×5"},
            {"level": 3, "effect": {"mark_duration": 120}, "desc": "标记持续 +2秒"},
            {"level": 4, "effect": {"mark_crit_mult": 2.0}, "desc": "标记倍率 ×7"},
            {"level": 5, "effect": {"mark_chain": 1}, "desc": "标记可传染"}
        ]
    },
    "execution": {
        "name": "处决",
        "category": "attack",
        "archetype": "sniper",
        "desc": "对低血量敌人造成巨额伤害",
        "base_effect": {"execute_threshold": 0.25, "execute_mult": 10.0},
        "visual_seed": 2007,
        "pattern": "fractal",
        "rarity": 4,
        "upgrades": [
            {"level": 2, "effect": {"execute_threshold": 0.05}, "desc": "阈值提升30%"},
            {"level": 3, "effect": {"execute_mult": 5.0}, "desc": "处决倍率 ×15"},
            {"level": 4, "effect": {"execute_threshold": 0.1}, "desc": "阈值提升40%"},
            {"level": 5, "effect": {"execute_instant_kill": True}, "desc": "低于10%秒杀"}
        ]
    },
    "sniper_focus": {
        "name": "狙击专注",
        "category": "attack",
        "archetype": "sniper",
        "desc": "静止不动时伤害持续提升",
        "base_effect": {"focus_per_sec": 0.2, "max_focus": 3.0},
        "visual_seed": 2008,
        "pattern": "wave",
        "rarity": 4,
        "upgrades": [
            {"level": 2, "effect": {"focus_per_sec": 0.1}, "desc": "专注速度 +50%"},
            {"level": 3, "effect": {"max_focus": 1.0}, "desc": "最大专注 ×4"},
            {"level": 4, "effect": {"focus_per_sec": 0.2}, "desc": "专注速度 +100%"},
            {"level": 5, "effect": {"max_focus": 2.0, "focus_crit": 0.5}, "desc": "满专注50%暴击"}
        ]
    },
    
    # ======== 控制流 (8张) - 专注场控和生存能力 ========
    "energy_shield": {
        "name": "能量护盾",
        "category": "defense",
        "archetype": "control",
        "desc": "吸收伤害的护盾",
        "base_effect": {"shield_amount": 50, "shield_regen": 2},
        "visual_seed": 3001,
        "pattern": "wave",
        "rarity": 1,
        "upgrades": [
            {"level": 2, "effect": {"shield_amount": 30}, "desc": "护盾值 +30"},
            {"level": 3, "effect": {"shield_regen": 2}, "desc": "回复速度 +2"},
            {"level": 4, "effect": {"shield_amount": 50}, "desc": "护盾值 +50"},
            {"level": 5, "effect": {"shield_regen": 3}, "desc": "回复速度 +3"}
        ]
    },
    "gravity_field": {
        "name": "引力场",
        "category": "control",
        "archetype": "control",
        "desc": "减速并吸引敌人",
        "base_effect": {"slow_mult": 0.4, "pull_strength": 2.0, "radius": 150},
        "visual_seed": 3002,
        "pattern": "spiral",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"slow_mult": 0.2}, "desc": "减速增强"},
            {"level": 3, "effect": {"radius": 70}, "desc": "范围 +70"},
            {"level": 4, "effect": {"slow_mult": 0.2}, "desc": "减速 +20%"},
            {"level": 5, "effect": {"pull_strength": 3.0}, "desc": "吸引力 ×2.5"}
        ]
    },
    "time_dilation": {
        "name": "时间膨胀",
        "category": "control",
        "archetype": "control",
        "desc": "减缓敌人移动和攻击",
        "base_effect": {"slow_area": 200, "time_factor": 0.5},
        "visual_seed": 3003,
        "pattern": "wave",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"time_factor": -0.2}, "desc": "减速更强"},
            {"level": 3, "effect": {"slow_area": 100}, "desc": "范围增大"},
            {"level": 4, "effect": {"time_factor": -0.2}, "desc": "时间流速 ×0.1"},
            {"level": 5, "effect": {"time_freeze_chance": 0.1}, "desc": "10%几率冻结"}
        ]
    },
    "frost_nova": {
        "name": "冰霜新星",
        "category": "control",
        "archetype": "control",
        "desc": "冻结区域内所有敌人",
        "base_effect": {"freeze_duration": 120, "freeze_radius": 100},
        "visual_seed": 3004,
        "pattern": "geometric",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"freeze_duration": 60}, "desc": "冻结时长 +50%"},
            {"level": 3, "effect": {"freeze_radius": 50}, "desc": "范围 +50"},
            {"level": 4, "effect": {"freeze_duration": 120}, "desc": "冻结时长 +2秒"},
            {"level": 5, "effect": {"freeze_shatter": 2.0}, "desc": "碎冰造成伤害"}
        ]
    },
    "armor_plating": {
        "name": "装甲镀层",
        "category": "defense",
        "archetype": "control",
        "desc": "减少受到的伤害",
        "base_effect": {"damage_reduction": 0.2, "max_hp_bonus": 50},
        "visual_seed": 3005,
        "pattern": "geometric",
        "rarity": 1,
        "upgrades": [
            {"level": 2, "effect": {"damage_reduction": 0.10}, "desc": "减伤 +10%"},
            {"level": 3, "effect": {"max_hp_bonus": 50}, "desc": "生命 +50"},
            {"level": 4, "effect": {"damage_reduction": 0.15}, "desc": "减伤 +15%"},
            {"level": 5, "effect": {"thorns_damage": 0.3}, "desc": "反伤30%"}
        ]
    },
    "regeneration": {
        "name": "生命再生",
        "category": "defense",
        "archetype": "control",
        "desc": "持续恢复生命",
        "base_effect": {"regen_rate": 5, "regen_interval": 300},
        "visual_seed": 3006,
        "pattern": "fractal",
        "rarity": 1,
        "upgrades": [
            {"level": 2, "effect": {"regen_rate": 3}, "desc": "回复量 +3"},
            {"level": 3, "effect": {"regen_interval": -100}, "desc": "间隔缩短"},
            {"level": 4, "effect": {"regen_rate": 5}, "desc": "回复量 +5"},
            {"level": 5, "effect": {"regen_combat": True}, "desc": "战斗中也回复"}
        ]
    },
    "phase_dodge": {
        "name": "相位闪避",
        "category": "defense",
        "archetype": "control",
        "desc": "概率完全闪避伤害",
        "base_effect": {"dodge_chance": 0.15},
        "visual_seed": 3007,
        "pattern": "spiral",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"dodge_chance": 0.10}, "desc": "闪避率 +10%"},
            {"level": 3, "effect": {"dodge_chance": 0.10}, "desc": "闪避率 +10%"},
            {"level": 4, "effect": {"dodge_invulnerable": 30}, "desc": "闪避后无敌0.5秒"},
            {"level": 5, "effect": {"dodge_chance": 0.15}, "desc": "闪避率 +15%"}
        ]
    },
    "stasis_field": {
        "name": "静滞力场",
        "category": "control",
        "archetype": "control",
        "desc": "创造完全静止敌人的力场",
        "base_effect": {"stasis_duration": 60, "stasis_radius": 120},
        "visual_seed": 3008,
        "pattern": "geometric",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"stasis_duration": 30}, "desc": "静滞时长 +50%"},
            {"level": 3, "effect": {"stasis_radius": 60}, "desc": "范围 +50%"},
            {"level": 4, "effect": {"stasis_damage_amp": 0.5}, "desc": "受伤+50%"},
            {"level": 5, "effect": {"stasis_duration": 60}, "desc": "静滞时长 +1秒"}
        ]
    },
    "void_barrier": {
        "name": "虚空屏障",
        "category": "defense",
        "archetype": "control",
        "desc": "生成吸收伤害的虚空壁垒",
        "base_effect": {"barrier_hp": 200, "barrier_recharge": 600},
        "visual_seed": 3009,
        "pattern": "fractal",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"barrier_hp": 100}, "desc": "屏障HP +100"},
            {"level": 3, "effect": {"barrier_recharge": -200}, "desc": "充能加速"},
            {"level": 4, "effect": {"barrier_hp": 200}, "desc": "屏障HP +200"},
            {"level": 5, "effect": {"barrier_reflect": 0.5}, "desc": "反射50%伤害"}
        ]
    },
    
    # ======== 召唤流 (8张) - 专注召唤物和辅助单位 ========
    "auto_turret": {
        "name": "自动炮塔",
        "category": "summon",
        "archetype": "summon",
        "desc": "在屏幕固定位置部署防御炮塔",
        "base_effect": {"turret_count": 2, "turret_damage": 0.6},
        "visual_seed": 4001,
        "pattern": "geometric",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"turret_count": 2}, "desc": "炮塔数 2→4"},
            {"level": 3, "effect": {"turret_damage": 0.4}, "desc": "炮塔伤害 ×1.0"},
            {"level": 4, "effect": {"turret_count": 2}, "desc": "炮塔数 4→6"},
            {"level": 5, "effect": {"turret_laser": True}, "desc": "升级为激光炮"}
        ]
    },
    "drone_swarm": {
        "name": "无人机群",
        "category": "summon",
        "archetype": "summon",
        "desc": "召唤跟随无人机",
        "base_effect": {"drone_count": 2, "drone_damage": 0.4},
        "visual_seed": 4002,
        "pattern": "spiral",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"drone_count": 1}, "desc": "无人机 +1"},
            {"level": 3, "effect": {"drone_damage": 0.2}, "desc": "伤害 +20%"},
            {"level": 4, "effect": {"drone_count": 2}, "desc": "无人机 +2"},
            {"level": 5, "effect": {"drone_kamikaze": True}, "desc": "无人机可自爆"}
        ]
    },
    "resource_magnet": {
        "name": "资源磁场",
        "category": "utility",
        "archetype": "summon",
        "desc": "自动吸引经验和物品",
        "base_effect": {"magnet_range": 200, "xp_mult": 1.2},
        "visual_seed": 4003,
        "pattern": "wave",
        "rarity": 1,
        "upgrades": [
            {"level": 2, "effect": {"magnet_range": 100}, "desc": "范围 +100"},
            {"level": 3, "effect": {"xp_mult": 0.3}, "desc": "经验 +30%"},
            {"level": 4, "effect": {"magnet_range": 150}, "desc": "范围 +150"},
            {"level": 5, "effect": {"magnet_instant": True}, "desc": "全屏瞬吸"}
        ]
    },
    "orbital_strike": {
        "name": "轨道打击",
        "category": "summon",
        "archetype": "summon",
        "desc": "召唤卫星轨道激光打击",
        "base_effect": {"strike_damage": 500, "strike_cooldown": 600},
        "visual_seed": 4004,
        "pattern": "geometric",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"strike_damage": 200}, "desc": "伤害 +200"},
            {"level": 3, "effect": {"strike_cooldown": -200}, "desc": "冷却 -33%"},
            {"level": 4, "effect": {"strike_count": 1}, "desc": "双重打击"},
            {"level": 5, "effect": {"strike_damage": 500}, "desc": "伤害 ×2"}
        ]
    },
    "healing_aura": {
        "name": "治疗光环",
        "category": "utility",
        "archetype": "summon",
        "desc": "持续恢复自身和僚机生命",
        "base_effect": {"heal_per_sec": 3, "aura_radius": 200},
        "visual_seed": 4005,
        "pattern": "wave",
        "rarity": 2,
        "upgrades": [
            {"level": 2, "effect": {"heal_per_sec": 2}, "desc": "回复 +2/秒"},
            {"level": 3, "effect": {"aura_radius": 100}, "desc": "范围 +100"},
            {"level": 4, "effect": {"heal_per_sec": 3}, "desc": "回复 +3/秒"},
            {"level": 5, "effect": {"heal_damage_boost": 0.2}, "desc": "治疗提供20%伤害"}
        ]
    },
    "guardian_angel": {
        "name": "守护天使",
        "category": "summon",
        "archetype": "summon",
        "desc": "召唤守护灵，死亡时复活",
        "base_effect": {"revive_hp": 0.5, "revive_cooldown": 3600},
        "visual_seed": 4006,
        "pattern": "spiral",
        "rarity": 4,
        "upgrades": [
            {"level": 2, "effect": {"revive_hp": 0.2}, "desc": "复活HP +20%"},
            {"level": 3, "effect": {"revive_cooldown": -1200}, "desc": "冷却 -20秒"},
            {"level": 4, "effect": {"revive_invulnerable": 180}, "desc": "复活后无敌3秒"},
            {"level": 5, "effect": {"revive_hp": 0.3}, "desc": "复活HP +30%"}
        ]
    },
    "minion_army": {
        "name": "召唤大军",
        "category": "summon",
        "archetype": "summon",
        "desc": "召唤小型战斗单位群",
        "base_effect": {"minion_count": 5, "minion_hp": 20, "minion_damage": 10},
        "visual_seed": 4007,
        "pattern": "fractal",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"minion_count": 2}, "desc": "召唤物 +2"},
            {"level": 3, "effect": {"minion_hp": 10, "minion_damage": 5}, "desc": "属性 +50%"},
            {"level": 4, "effect": {"minion_count": 3}, "desc": "召唤物 +3"},
            {"level": 5, "effect": {"minion_evolve": True}, "desc": "召唤物可进化"}
        ]
    },
    "support_station": {
        "name": "支援站",
        "category": "summon",
        "archetype": "summon",
        "desc": "部署补给站，提供持续增益",
        "base_effect": {"station_buff": 0.3, "station_radius": 250},
        "visual_seed": 4008,
        "pattern": "geometric",
        "rarity": 3,
        "upgrades": [
            {"level": 2, "effect": {"station_buff": 0.1}, "desc": "增益 +10%"},
            {"level": 3, "effect": {"station_radius": 100}, "desc": "范围 +100"},
            {"level": 4, "effect": {"station_buff": 0.2}, "desc": "增益 +20%"},
            {"level": 5, "effect": {"station_repair": True}, "desc": "额外回复护盾"}
        ]
    }
}

# ==============================================================================
#   第二层：参数卡牌（修饰器）- 20种
# ==============================================================================
MODIFIER_CARDS = {
    # ======== 数值类修饰器 (8种) ========
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
    "cooldown_reduction": {
        "name": "冷却缩减",
        "type": "numeric",
        "desc": "技能冷却 -30%",
        "effect": {"cooldown_mult": 0.7},
        "rarity": 2,
        "visual_seed": 5005
    },
    "efficiency_boost": {
        "name": "效率提升",
        "type": "numeric",
        "desc": "能耗降低25%，效果不变",
        "effect": {"efficiency_mult": 1.25},
        "rarity": 2,
        "visual_seed": 5006
    },
    "overcharge": {
        "name": "超载",
        "type": "numeric",
        "desc": "所有数值 +50%，冷却 +30%",
        "effect": {"all_stats_mult": 1.5, "cooldown_penalty": 1.3},
        "rarity": 3,
        "visual_seed": 5007
    },
    "miniaturize": {
        "name": "微型化",
        "type": "numeric",
        "desc": "冷却 -50%，伤害 -30%",
        "effect": {"cooldown_mult": 0.5, "damage_mult": 0.7},
        "rarity": 2,
        "visual_seed": 5008
    },
    
    # ======== 特性类修饰器 (12种) ========
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
        "desc": "暴击率 +20%，暴伤 ×2.5",
        "effect": {"crit_chance": 0.2, "crit_mult": 1.5},
        "rarity": 2,
        "visual_seed": 5106
    },
    "freeze_addon": {
        "name": "冰冻模块",
        "type": "trait",
        "desc": "攻击冰冻敌人",
        "effect": {"freeze": True, "freeze_duration": 60},
        "rarity": 2,
        "visual_seed": 5107
    },
    "burn_addon": {
        "name": "燃烧模块",
        "type": "trait",
        "desc": "攻击点燃敌人",
        "effect": {"burn": True, "burn_dps": 10, "burn_duration": 180},
        "rarity": 2,
        "visual_seed": 5108
    },
    "poison_addon": {
        "name": "剧毒模块",
        "type": "trait",
        "desc": "攻击中毒敌人",
        "effect": {"poison": True, "poison_dps": 15, "poison_duration": 240},
        "rarity": 2,
        "visual_seed": 5109
    },
    "knockback_addon": {
        "name": "击退模块",
        "type": "trait",
        "desc": "攻击击退敌人",
        "effect": {"knockback": True, "knockback_force": 10},
        "rarity": 1,
        "visual_seed": 5110
    },
    "multishot_addon": {
        "name": "多重射击",
        "type": "trait",
        "desc": "每次攻击额外发射2发",
        "effect": {"multishot": 2},
        "rarity": 3,
        "visual_seed": 5111
    },
    "recursive_addon": {
        "name": "递归模块",
        "type": "trait",
        "desc": "效果可叠加触发自身",
        "effect": {"recursive": True, "recursive_chance": 0.25},
        "rarity": 4,
        "visual_seed": 5112
    }
}

# ==============================================================================
#   第三层：协同卡牌（组合规则）- 24种协同效果
# ==============================================================================
SYNERGY_RULES = {
    # ======== 弹幕流协同 (6种) ========
    "barrage_initiate": {
        "name": "弹幕学徒",
        "desc": "子弹数 +3，散射角度 +20°",
        "trigger": {
            "archetype": "barrage",
            "count": 2,
            "cards": []
        },
        "effect": {"bullet_count_bonus": 3, "spread_angle": 20},
        "visual": {"color": (255, 150, 150), "particle_effect": "bullet_trail"},
        "rarity": 2
    },
    "barrage_master": {
        "name": "弹幕大师",
        "desc": "子弹数量 ×2，分裂次数 +1",
        "trigger": {
            "archetype": "barrage",
            "count": 3,
            "cards": []
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
    "explosive_hell": {
        "name": "爆裂地狱",
        "desc": "所有子弹爆炸，范围 +100%",
        "trigger": {
            "archetype": "barrage",
            "count": 3,
            "cards": ["explosive_round"],
            "modifiers": ["explosive_addon"]
        },
        "effect": {"all_bullets_explode": True, "explosion_radius_mult": 2.0},
        "visual": {"color": (255, 150, 0), "particle_effect": "explosive_trail"},
        "rarity": 4
    },
    "bullet_hell": {
        "name": "弹幕狂潮",
        "desc": "射速 ×3，子弹体积 -50%",
        "trigger": {
            "archetype": "barrage",
            "count": 4,
            "cards": ["rapid_fire", "scatter_cannon"]
        },
        "effect": {"fire_rate_mult": 3.0, "bullet_size": 0.5},
        "visual": {"color": (255, 200, 100), "particle_effect": "rapid_stream"},
        "rarity": 4
    },
    "chain_reaction": {
        "name": "连锁反应",
        "desc": "分裂弹也会分裂，最多3层",
        "trigger": {
            "archetype": "barrage",
            "count": 3,
            "cards": ["split_shot", "cluster_bomb"]
        },
        "effect": {"recursive_split": 3, "split_damage_mult": 1.2},
        "visual": {"color": (255, 100, 150), "particle_effect": "fractal_burst"},
        "rarity": 4
    },
    
    # ======== 狙击流协同 (6种) ========
    "sharpshooter": {
        "name": "神枪手",
        "desc": "暴击率 +25%，暴击伤害 ×3",
        "trigger": {
            "archetype": "sniper",
            "count": 2,
            "cards": []
        },
        "effect": {"crit_chance": 0.25, "crit_mult": 2.0},
        "visual": {"color": (150, 220, 255), "particle_effect": "precision_mark"},
        "rarity": 2
    },
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
    "deadeye": {
        "name": "死亡之眼",
        "desc": "100%暴击率，专注层数不再掉落",
        "trigger": {
            "archetype": "sniper",
            "count": 5,
            "cards": ["sniper_focus", "weakpoint_strike"]
        },
        "effect": {"crit_chance": 1.0, "focus_permanent": True},
        "visual": {"color": (0, 255, 255), "particle_effect": "perfect_aim"},
        "rarity": 5
    },
    "armor_buster": {
        "name": "装甲克星",
        "desc": "破甲100%，对Boss额外伤害 ×2",
        "trigger": {
            "archetype": "sniper",
            "count": 3,
            "cards": ["armor_penetration", "railgun"]
        },
        "effect": {"armor_pen": 1.0, "boss_damage_mult": 2.0},
        "visual": {"color": (255, 200, 0), "particle_effect": "armor_shatter"},
        "rarity": 4
    },
    "execution_master": {
        "name": "处决大师",
        "desc": "处决阈值提升至50%，即死",
        "trigger": {
            "archetype": "sniper",
            "count": 4,
            "cards": ["execution", "charged_shot"]
        },
        "effect": {"execute_threshold": 0.5, "execute_instant": True},
        "visual": {"color": (200, 0, 0), "particle_effect": "death_mark"},
        "rarity": 5
    },
    
    # ======== 控制流协同 (6种) ========
    "defensive_master": {
        "name": "防御专家",
        "desc": "最大生命 +100，减伤 +20%",
        "trigger": {
            "archetype": "control",
            "count": 2,
            "cards": []
        },
        "effect": {"max_hp_bonus": 100, "damage_reduction": 0.2},
        "visual": {"color": (200, 150, 255), "particle_effect": "shield_glow"},
        "rarity": 2
    },
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
    "fortress": {
        "name": "移动堡垒",
        "desc": "减伤50%，护盾×2，移速-30%",
        "trigger": {
            "archetype": "control",
            "count": 5,
            "cards": ["armor_plating", "energy_shield", "void_barrier"]
        },
        "effect": {"damage_reduction": 0.5, "shield_mult": 2.0, "speed_penalty": 0.7},
        "visual": {"color": (200, 100, 255), "particle_effect": "fortress_aura"},
        "rarity": 5
    },
    "immortal": {
        "name": "不朽之躯",
        "desc": "生命回复×3，死亡自动复活",
        "trigger": {
            "archetype": "control",
            "count": 4,
            "cards": ["regeneration", "guardian_angel"]
        },
        "effect": {"regen_mult": 3.0, "auto_revive": True},
        "visual": {"color": (255, 200, 255), "particle_effect": "divine_protection"},
        "rarity": 5
    },
    "absolute_zero": {
        "name": "绝对零度",
        "desc": "冰冻时长×3，冰碎伤害×5",
        "trigger": {
            "archetype": "control",
            "count": 4,
            "cards": ["frost_nova", "stasis_field"]
        },
        "effect": {"freeze_duration_mult": 3.0, "shatter_mult": 5.0},
        "visual": {"color": (100, 200, 255), "particle_effect": "ice_age"},
        "rarity": 4
    },
    
    # ======== 召唤流协同 (6种) ========
    "squad_leader": {
        "name": "编队长",
        "desc": "僚机 +1，僚机伤害 +30%",
        "trigger": {
            "archetype": "summon",
            "count": 2,
            "cards": []
        },
        "effect": {"drone_count": 1, "drone_damage_mult": 1.3},
        "visual": {"color": (150, 255, 200), "particle_effect": "formation_link"},
        "rarity": 2
    },
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
    "orbital_supremacy": {
        "name": "轨道霸权",
        "desc": "轨道打击冷却-50%，伤害×3",
        "trigger": {
            "archetype": "summon",
            "count": 3,
            "cards": ["orbital_strike", "auto_turret"]
        },
        "effect": {"strike_cooldown_mult": 0.5, "strike_damage_mult": 3.0},
        "visual": {"color": (255, 200, 100), "particle_effect": "satellite_network"},
        "rarity": 4
    },
    "necromancer": {
        "name": "死灵法师",
        "desc": "击杀敌人复生为己方单位",
        "trigger": {
            "archetype": "summon",
            "count": 4,
            "cards": ["minion_army", "guardian_angel"]
        },
        "effect": {"revive_enemy_chance": 0.25, "revived_hp": 0.5},
        "visual": {"color": (150, 0, 255), "particle_effect": "necromancy"},
        "rarity": 5
    },
    "swarm_intelligence": {
        "name": "集群智能",
        "desc": "每个召唤物使其他召唤物 +10% 伤害",
        "trigger": {
            "archetype": "summon",
            "count": 5,
            "cards": ["drone_swarm", "minion_army"]
        },
        "effect": {"swarm_synergy": 0.1, "max_swarm_bonus": 3.0},
        "visual": {"color": (0, 255, 200), "particle_effect": "hive_mind"},
        "rarity": 5
    },
    
    # ======== 混合流派协同 (6种) ========
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
    },
    "vampire_barrage": {
        "name": "吸血弹幕",
        "desc": "所有弹幕吸血，吸血率×2",
        "trigger": {
            "archetype": "barrage",
            "count": 3,
            "modifiers": ["lifesteal_addon"]
        },
        "effect": {"all_lifesteal": True, "lifesteal_mult": 2.0},
        "visual": {"color": (200, 0, 100), "particle_effect": "blood_feast"},
        "rarity": 4
    },
    "elemental_chaos": {
        "name": "元素混沌",
        "desc": "同时触发冰冻、燃烧、剧毒",
        "trigger": {
            "modifiers": ["freeze_addon", "burn_addon", "poison_addon"]
        },
        "effect": {"all_elements": True, "element_damage_mult": 1.5},
        "visual": {"color": (255, 150, 255), "particle_effect": "elemental_storm"},
        "rarity": 5
    },
    "glass_cannon": {
        "name": "玻璃大炮",
        "desc": "伤害×5，最大生命-50%",
        "trigger": {
            "archetype": "barrage",
            "count": 4,
            "archetype_exclude": ["control"]
        },
        "effect": {"damage_mult": 5.0, "max_hp_mult": 0.5},
        "visual": {"color": (255, 0, 0), "particle_effect": "glass_shatter"},
        "rarity": 5
    },
    "perfect_balance": {
        "name": "完美平衡",
        "desc": "拥有所有流派卡牌时，全属性 +100%",
        "trigger": {
            "archetype": "all",
            "archetypes_count": 4
        },
        "effect": {"all_stats_mult": 2.0},
        "visual": {"color": (255, 255, 255), "particle_effect": "harmony"},
        "rarity": 6
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
        """升级卡牌（最高5级）"""
        if self.type == "base" and self.level < 5:
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
            player.bullet_count = min(player.bullet_count, 30)  # 上限30发，避免卡顿
        if "bullet_count_mult" in effect:
            player.bullet_count = int(getattr(player, "bullet_count", 1) * effect["bullet_count_mult"])
            player.bullet_count = min(player.bullet_count, 30)  # 上限30发，避免卡顿
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
        
        # 弹幕流专属效果
        if "bounce_count" in effect:
            player.has_bounce = True
            player.bounce_count = getattr(player, "bounce_count", 0) + effect["bounce_count"]
        if "bounce_damage" in effect:
            player.bounce_damage_mult = getattr(player, "bounce_damage_mult", 1.0) * (1.0 + effect["bounce_damage"])
        if "cluster_count" in effect:
            player.has_cluster = True
            player.cluster_count = effect["cluster_count"]
            player.cluster_radius = effect.get("cluster_radius", 40)
        if "cluster_radius" in effect:
            player.cluster_radius = getattr(player, "cluster_radius", 40) + effect["cluster_radius"]
        if "storm_duration" in effect:
            player.has_storm = True
            player.storm_duration = effect["storm_duration"]
            player.storm_bullets = effect.get("storm_bullets", 20)
        
        # 狙击流专属效果
        if "overcharge_cooldown" in effect:
            player.has_overcharge = True
            player.overcharge_cooldown = getattr(player, "overcharge_cooldown", 180) + effect["overcharge_cooldown"]
            if "overcharge_mult" in effect:
                player.overcharge_mult = effect["overcharge_mult"]
        if "overcharge_mult" in effect:
            player.overcharge_mult = getattr(player, "overcharge_mult", 1.0) + effect["overcharge_mult"]
        if "overcharge_pierce" in effect:
            player.overcharge_pierce = effect["overcharge_pierce"]
        if "weakpoint_chance" in effect:
            player.weakpoint_chance = getattr(player, "weakpoint_chance", 0) + effect["weakpoint_chance"]
        if "weakpoint_mult" in effect:
            player.weakpoint_mult = getattr(player, "weakpoint_mult", 1.0) + effect["weakpoint_mult"]
        if "armor_pen" in effect:
            player.armor_penetration = getattr(player, "armor_penetration", 0) + effect["armor_pen"]
        if "bonus_vs_armor" in effect:
            player.bonus_vs_armor = getattr(player, "bonus_vs_armor", 0) + effect["bonus_vs_armor"]
        if "mark_duration" in effect:
            player.has_mark = True
            player.mark_duration = effect["mark_duration"]
            player.mark_crit_mult = effect.get("mark_crit_mult", 4.0)
        if "execute_threshold" in effect:
            player.has_execute = True
            player.execute_threshold = effect["execute_threshold"]
            player.execute_mult = effect.get("execute_mult", 10.0)
        if "focus_per_sec" in effect:
            player.has_focus = True
            player.focus_per_sec = effect["focus_per_sec"]
            player.max_focus = effect.get("max_focus", 3.0)
        
        # 控制流专属效果
        if "stasis_duration" in effect:
            player.has_stasis = True
            player.stasis_duration = effect["stasis_duration"]
            player.stasis_radius = effect.get("stasis_radius", 120)
        if "barrier_hp" in effect:
            player.has_barrier = True
            player.barrier_hp = effect["barrier_hp"]
            player.barrier_max_hp = effect["barrier_hp"]
            player.barrier_recharge = effect.get("barrier_recharge", 600)
        
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
        if "strike_damage" in effect:
            player.has_orbital_strike = True
            player.strike_damage = effect["strike_damage"]
            player.strike_cooldown = effect.get("strike_cooldown", 600)
            player.strike_timer = 0
        if "heal_per_sec" in effect:
            player.has_healing_aura = True
            player.heal_per_sec = effect["heal_per_sec"]
            player.aura_radius = effect.get("aura_radius", 200)
        if "revive_hp" in effect:
            player.has_revive = True
            # revive_hp是百分比，转换为实际血量
            revive_percent = effect["revive_hp"]
            player.revive_hp = int(player.max_hp * revive_percent)
            player.revive_cooldown = effect.get("revive_cooldown", 3600)
            player.revive_cooldown_timer = 3600  # 初始冷却完成
        if "minion_count" in effect:
            player.has_minions = True
            player.minion_count = effect["minion_count"]
            player.minion_hp = effect.get("minion_hp", 20)
            player.minion_damage = effect.get("minion_damage", 10)
        if "station_buff" in effect:
            player.has_station = True
            player.station_buff = effect["station_buff"]
            player.station_radius = effect.get("station_radius", 250)
        
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
        
        # 【新】添加协同combo提示
        try:
            import main
            if hasattr(main, 'synergy_combo_hints'):
                hint_text = f"💫 协同激活: {synergy_data['name']}"
                main.synergy_combo_hints.append((hint_text, 240, synergy_data.get('visual', {}).get('color', (255, 200, 0))))
        except Exception:
            pass
        
        # 应用协同效果
        if self._player_ref:
            effect = synergy_data["effect"]
            player = self._player_ref
            
            if "bullet_count_mult" in effect:
                player.bullet_count = int(player.bullet_count * effect["bullet_count_mult"])
                player.bullet_count = min(player.bullet_count, 30)  # 上限30发，避免卡顿
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

    def _pick_base_card(self, rarity_weights, preferred_archetype=None, exclude=None):
        """根据稀有度和偏好流派挑选基础卡牌"""
        exclude = exclude or set()
        candidates = []
        for card_id, card_data in BASE_CARDS.items():
            if card_id in exclude:
                continue
            if card_data.get("rarity") not in rarity_weights:
                continue
            if preferred_archetype and card_data.get("archetype") != preferred_archetype:
                continue
            candidates.append(card_id)
        if not candidates and preferred_archetype:
            return self._pick_base_card(rarity_weights, None, exclude)
        if not candidates:
            return None
        weights = [rarity_weights.get(BASE_CARDS[c]["rarity"], 0) for c in candidates]
        if sum(weights) <= 0:
            return random.choice(candidates)
        return random.choices(candidates, weights=weights, k=1)[0]

    def _pick_modifier_card(self, exclude=None):
        exclude = exclude or set()
        candidates = [mid for mid in MODIFIER_CARDS.keys() if mid not in exclude]
        return random.choice(candidates) if candidates else None

    def _pick_upgrade_candidate(self, exclude=None):
        exclude = exclude or set()
        upgradable = [
            card_id for card_id, card in self.owned_cards.items()
            if card.type == "base" and card.level < 5 and card_id not in exclude
        ]
        return random.choice(upgradable) if upgradable else None
    
    def trigger_levelup(self):
        """触发升级，生成3选1卡牌（支持1-6星）"""
        player = getattr(self, '_player_ref', None)
        if not player:
            return
        
        player_level = player.level
        
        # 根据等级调整稀有度权重（扩展到6星）
        rarity_weights = {1: 1.0, 2: 0.3, 3: 0.05, 4: 0.01, 5: 0.005, 6: 0.001}
        if player_level <= 5:
            # 1-5级：只出普通和稀有
            rarity_weights = {1: 1.0, 2: 0.2, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0}
        elif player_level <= 10:
            # 6-10级：开始出现史诗
            rarity_weights = {1: 0.7, 2: 0.5, 3: 0.1, 4: 0.0, 5: 0.0, 6: 0.0}
        elif player_level <= 15:
            # 11-15级：开始出现传说
            rarity_weights = {1: 0.5, 2: 0.7, 3: 0.2, 4: 0.05, 5: 0.0, 6: 0.0}
        elif player_level <= 20:
            # 16-20级：开始出现神话
            rarity_weights = {1: 0.3, 2: 0.6, 3: 0.5, 4: 0.1, 5: 0.02, 6: 0.0}
        else:
            # 21级+：可能出现至高
            rarity_weights = {1: 0.2, 2: 0.5, 3: 0.6, 4: 0.3, 5: 0.05, 6: 0.01}
        
        selected = []
        choice_keys = set()
        base_exclude, modifier_exclude, upgrade_exclude = set(), set(), set()

        def add_choice(choice):
            if not choice:
                return
            key = (choice["type"], choice["id"])
            if key in choice_keys:
                return
            selected.append(choice)
            choice_keys.add(key)
            if choice["type"] == "base":
                base_exclude.add(choice["id"])
            elif choice["type"] == "modifier":
                modifier_exclude.add(choice["id"])
            elif choice["type"] == "upgrade":
                upgrade_exclude.add(choice["id"])

        # 第一张：满足当前主流派，确保持续强化核心
        dominant_archetype = None
        if self.archetype_counts:
            dominant_archetype = max(self.archetype_counts.items(), key=lambda x: x[1])[0]
            if self.archetype_counts[dominant_archetype] == 0:
                dominant_archetype = None
        base_choice = self._pick_base_card(rarity_weights, dominant_archetype, base_exclude)
        if base_choice:
            add_choice({"type": "base", "id": base_choice})

        # 第二张：引导补足短板或提供新流派
        missing = [arc for arc, count in self.archetype_counts.items() if count == 0]
        fallback_arc = None
        if self.archetype_counts:
            fallback_arc = min(self.archetype_counts.items(), key=lambda x: x[1])[0]
        support_arc = missing[0] if missing else fallback_arc
        support_choice = self._pick_base_card(rarity_weights, support_arc, base_exclude)
        if support_choice:
            add_choice({"type": "base", "id": support_choice})

        # 第三张：优先给已有卡的升级，否则提供参数卡
        upgrade_target = self._pick_upgrade_candidate(upgrade_exclude)
        if upgrade_target:
            add_choice({"type": "upgrade", "id": upgrade_target})
        else:
            modifier_choice = self._pick_modifier_card(modifier_exclude)
            if modifier_choice:
                add_choice({"type": "modifier", "id": modifier_choice})

        # 兜底：确保总数达到3张
        guard_counter = 0
        while len(selected) < 3 and guard_counter < 6:
            guard_counter += 1
            fallback_base = self._pick_base_card(rarity_weights, None, base_exclude)
            if fallback_base:
                add_choice({"type": "base", "id": fallback_base})
                continue
            modifier_choice = self._pick_modifier_card(modifier_exclude)
            if modifier_choice:
                add_choice({"type": "modifier", "id": modifier_choice})
                continue
            upgrade_target = self._pick_upgrade_candidate(upgrade_exclude)
            if upgrade_target:
                add_choice({"type": "upgrade", "id": upgrade_target})
                continue
            break
        if not selected:
            fallback_id = random.choice(list(BASE_CARDS.keys()))
            selected.append({"type": "base", "id": fallback_id})
        
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
