# ==============================================================================
#   Roguelike 房间系统
# ==============================================================================
import pygame
import random
import math
from config import *
from utils import log_info, sound_mgr

# 图标渲染缓存（避免每帧重新渲染emoji导致掉帧）
_icon_cache = {}
_emoji_font = None

def get_emoji_font(size=20):
    """获取或创建emoji字体（缓存）"""
    global _emoji_font
    if _emoji_font is None or _emoji_font.get_height() != size:
        try:
            # 尝试多个字体，确保emoji和特殊字符都能显示
            _emoji_font = pygame.font.SysFont("segoeuisymbol,segoeuiemoji,segoeui,microsoftyaheui,simhei,arial", size)
        except:
            try:
                _emoji_font = pygame.font.SysFont("arial", size)
            except:
                _emoji_font = pygame.font.Font(None, size)
    return _emoji_font

def render_icon_cached(icon, size=20):
    """渲染图标并缓存（优化性能）"""
    cache_key = f"{icon}_{size}"
    if cache_key not in _icon_cache:
        font = get_emoji_font(size)
        _icon_cache[cache_key] = font.render(icon, True, (255, 255, 255))
    return _icon_cache[cache_key]

# 房间类型定义
class RoomType:
    COMBAT = "combat"           # 战斗房间
    SHOP = "shop"               # 商店房间
    TREASURE = "treasure"       # 宝箱房间
    BOSS = "boss"               # Boss房间
    REST = "rest"               # 休息房间
    ELITE = "elite"             # 精英战斗房间
    EVENT = "event"             # 随机事件房间

# 房间状态
class RoomState:
    LOCKED = "locked"           # 未解锁
    AVAILABLE = "available"     # 可进入
    CURRENT = "current"         # 当前房间
    CLEARED = "cleared"         # 已完成

class Room:
    """单个房间"""
    def __init__(self, room_type, depth, room_id):
        self.room_type = room_type
        self.depth = depth  # 房间深度（层数）
        self.room_id = room_id
        self.state = RoomState.LOCKED
        self.connections = []  # 连接到的下一层房间ID列表
        self.reward = None  # 房间奖励
        self.enemies_cleared = False
        self.visited = False
        
        # 根据房间类型初始化属性
        self._init_room_properties()
    
    def _init_room_properties(self):
        """根据房间类型初始化属性"""
        if self.room_type == RoomType.COMBAT:
            self.enemy_count = random.randint(5, 8) + self.depth
            self.difficulty_multiplier = 1.0 + self.depth * 0.1
        elif self.room_type == RoomType.ELITE:
            self.enemy_count = random.randint(3, 5) + self.depth
            self.difficulty_multiplier = 1.5 + self.depth * 0.15
        elif self.room_type == RoomType.BOSS:
            self.boss_type = self._get_boss_for_depth()
            self.difficulty_multiplier = 2.0 + self.depth * 0.2
        elif self.room_type == RoomType.SHOP:
            self.shop_items = self._generate_shop_items()
        elif self.room_type == RoomType.TREASURE:
            self.treasure_count = random.randint(1, 3)
        elif self.room_type == RoomType.REST:
            self.heal_amount = 50 + self.depth * 5
    
    def _get_boss_for_depth(self):
        """根据深度获取Boss类型"""
        boss_types = ["fortress", "void_reaper", "starborn", "vortex"]
        return boss_types[min(self.depth // 3, len(boss_types) - 1)]
    
    def _generate_shop_items(self):
        """生成商店物品"""
        items = []
        # 生成3-5个商品
        for _ in range(random.randint(3, 5)):
            item_type = random.choice(["health", "upgrade", "weapon", "buff"])
            price = random.randint(50, 200) + self.depth * 20
            items.append({
                "type": item_type,
                "price": price,
                "sold": False
            })
        return items
    
    def get_color(self):
        """获取房间颜色（用于地图显示）"""
        colors = {
            RoomType.COMBAT: (200, 200, 200),
            RoomType.SHOP: (255, 215, 0),
            RoomType.TREASURE: (0, 255, 200),
            RoomType.BOSS: (255, 50, 50),
            RoomType.REST: (100, 255, 100),
            RoomType.ELITE: (255, 150, 0),
            RoomType.EVENT: (200, 100, 255)
        }
        return colors.get(self.room_type, (150, 150, 150))
    
    def get_icon(self):
        """获取房间图标符号"""
        icons = {
            RoomType.COMBAT: "⚔",
            RoomType.SHOP: "$",
            RoomType.TREASURE: "♦",
            RoomType.BOSS: "☠",
            RoomType.REST: "♥",
            RoomType.ELITE: "★",
            RoomType.EVENT: "?"
        }
        return icons.get(self.room_type, "·")


class RoomManager:
    """房间管理器"""
    def __init__(self):
        self.rooms = {}  # {room_id: Room}
        self.current_room = None
        self.max_depth = 12  # 最大层数
        self.rooms_per_depth = 4  # 每层房间数
        self.player_path = []  # 玩家走过的路径
        self.map_visible = False  # 地图是否显示
        self.currency = 0  # 玩家货币
        
        # UI相关
        self.map_offset_x = 0
        self.map_offset_y = 0
        self.hovered_room = None
        self.transition_timer = 0
        self.transition_active = False
        self.next_room = None
        
        # 战斗状态
        self.enemies_spawned = False  # 当前房间是否已生成敌人
        self.room_completed = False  # 当前房间是否完成
        self.show_completion_ui = False  # 是否显示房间完成UI
        
        # 房间选择UI
        self.selected_next_room = 0  # 当前选中的下一个房间索引
        self.available_next_rooms = []  # 可选择的下一个房间列表
        
    def generate_map(self):
        """生成完整的房间地图"""
        self.rooms = {}
        room_counter = 0
        
        # 为每一层生成房间
        for depth in range(self.max_depth):
            # 确定这一层有多少个房间
            if depth == 0:
                # 起始层只有一个房间
                room_count = 1
            elif depth == self.max_depth - 1:
                # 最后一层是Boss房间
                room_count = 1
            else:
                room_count = self.rooms_per_depth
            
            # 生成这一层的房间
            for i in range(room_count):
                room_id = f"room_{depth}_{i}"
                room_type = self._determine_room_type(depth, i, room_count)
                room = Room(room_type, depth, room_id)
                self.rooms[room_id] = room
                room_counter += 1
        
        # 建立房间连接
        self._connect_rooms()
        
        # 设置起始房间
        start_room_id = "room_0_0"
        if start_room_id in self.rooms:
            self.current_room = self.rooms[start_room_id]
            self.current_room.state = RoomState.CURRENT
            self.player_path = [start_room_id]
            
            # 解锁连接的房间
            self._unlock_connected_rooms()
        
        log_info(f"生成房间地图: {room_counter}个房间，{self.max_depth}层")
    
    def _determine_room_type(self, depth, index, room_count):
        """确定房间类型"""
        # 起始房间
        if depth == 0:
            return RoomType.COMBAT
        
        # Boss房间（最后一层）
        if depth == self.max_depth - 1:
            return RoomType.BOSS
        
        # 每3层一个Boss房间
        if depth > 0 and depth % 4 == 3:
            if index == room_count // 2:  # 中间位置是Boss
                return RoomType.BOSS
        
        # 商店和休息房间（每层最多一个）
        if index == 0 and random.random() < 0.3:
            return RoomType.SHOP
        if index == room_count - 1 and random.random() < 0.25:
            return RoomType.REST
        
        # 其他房间随机分配
        rand = random.random()
        if rand < 0.6:
            return RoomType.COMBAT
        elif rand < 0.75:
            return RoomType.ELITE
        elif rand < 0.85:
            return RoomType.TREASURE
        else:
            return RoomType.EVENT
    
    def _connect_rooms(self):
        """建立房间之间的连接"""
        for depth in range(self.max_depth - 1):
            current_layer = [r for r in self.rooms.values() if r.depth == depth]
            next_layer = [r for r in self.rooms.values() if r.depth == depth + 1]
            
            if not current_layer or not next_layer:
                continue
            
            # 确保每个房间至少有一个连接
            for room in current_layer:
                # 连接到下一层的1-3个房间
                connection_count = min(random.randint(1, 3), len(next_layer))
                
                # 优先连接附近的房间
                available_next = next_layer.copy()
                random.shuffle(available_next)
                
                for _ in range(connection_count):
                    if available_next:
                        next_room = available_next.pop(0)
                        room.connections.append(next_room.room_id)
            
            # 确保下一层每个房间都可达
            for next_room in next_layer:
                has_connection = any(next_room.room_id in r.connections 
                                    for r in current_layer)
                if not has_connection and current_layer:
                    random.choice(current_layer).connections.append(next_room.room_id)
    
    def _unlock_connected_rooms(self):
        """解锁当前房间连接的房间"""
        if not self.current_room:
            return
        
        for room_id in self.current_room.connections:
            if room_id in self.rooms:
                room = self.rooms[room_id]
                if room.state == RoomState.LOCKED:
                    room.state = RoomState.AVAILABLE
    
    def enter_room(self, room_id):
        """进入指定房间"""
        if room_id not in self.rooms:
            return False
        
        room = self.rooms[room_id]
        
        # 检查是否可以进入
        if room.state != RoomState.AVAILABLE:
            return False
        
        # 设置房间转换
        self.transition_active = True
        self.transition_timer = 30  # 0.5秒转换动画
        self.next_room = room
        
        return True
    
    def complete_transition(self):
        """完成房间转换"""
        if not self.next_room:
            return
        
        # 标记当前房间为已完成
        if self.current_room:
            self.current_room.state = RoomState.CLEARED
        
        # 进入新房间
        self.current_room = self.next_room
        self.current_room.state = RoomState.CURRENT
        self.current_room.visited = True
        self.player_path.append(self.current_room.room_id)
        
        # 解锁连接的房间
        self._unlock_connected_rooms()
        
        # 重置房间状态
        self.enemies_spawned = False
        self.room_completed = False
        self.show_completion_ui = False
        
        # 播放音效
        sound_mgr.play_sound("levelup")
        
        # 重置转换状态
        self.transition_active = False
        self.next_room = None
        
        log_info(f"进入房间: {self.current_room.room_id} ({self.current_room.room_type})")
    
    def clear_current_room(self):
        """标记当前房间已清理（敌人全部消灭）"""
        if self.current_room:
            self.current_room.enemies_cleared = True
    
    def spawn_room_enemies(self, enemy_factory, mobs_group, all_sprites_group):
        """生成当前房间的敌人"""
        if not self.current_room or self.enemies_spawned:
            return
        
        room = self.current_room
        
        # 战斗房间和精英房间生成敌人
        if room.room_type in [RoomType.COMBAT, RoomType.ELITE]:
            enemy_count = room.enemy_count
            is_elite = room.room_type == RoomType.ELITE
            
            # 根据房间深度选择敌人类型（使用实际存在的敌人ID）
            available_enemies = ["scout_moth", "trooper_spear", "lurker_halo", "plasma_storm"]
            if room.depth >= 2:
                available_enemies.extend(["bomber_deepjelly", "jammer_amethyst", "shield_beeguard"])
            if room.depth >= 4:
                available_enemies.extend(["splitter_azurecore", "sniper_blackneedle", "weaver_dualwasp"])
            if room.depth >= 6:
                available_enemies.extend(["summoner_nethalo", "prism_voidprism", "guard_heavyanvil"])
            if room.depth >= 8:
                available_enemies.extend(["nestlord_livestarport", "weaver_dimensionspindle", "judge_dualpolar"])
            
            for i in range(enemy_count):
                enemy_type = random.choice(available_enemies)
                
                # 在屏幕外随机位置生成
                edge = random.choice(['top', 'left', 'right'])
                if edge == 'top':
                    x = random.randint(50, WIDTH - 50)
                    y = -50
                elif edge == 'left':
                    x = -50
                    y = random.randint(50, HEIGHT - 50)
                else:  # right
                    x = WIDTH + 50
                    y = random.randint(50, HEIGHT - 50)
                
                try:
                    # 使用正确的参数格式
                    override_config = {
                        'hp': int(100 * room.difficulty_multiplier),
                        'is_elite': is_elite
                    }
                    # create_enemy会自动将敌人添加到全局sprite组，无需手动添加
                    enemy = enemy_factory.create_enemy(
                        enemy_type, 
                        spawn_pos=(x, y),
                        override_config=override_config
                    )
                except Exception as e:
                    from utils import log_error
                    log_error(f"生成敌人失败 ({enemy_type}): {e}")
            
            self.enemies_spawned = True
            log_info(f"生成 {enemy_count} 个敌人 (精英: {is_elite}, 难度: {room.difficulty_multiplier:.1f}x)")
        
        # Boss房间生成Boss（由其他系统处理）
        elif room.room_type == RoomType.BOSS:
            self.enemies_spawned = True
            log_info(f"Boss房间: {room.boss_type}")
    
    def check_room_completion(self, mobs_group, boss=None):
        """检测当前房间是否完成，返回True时需要暂停游戏"""
        if not self.current_room or self.room_completed:
            return False
        
        room = self.current_room
        
        # 战斗房间：敌人全部消灭（跑出屏幕的也算完成）
        if room.room_type in [RoomType.COMBAT, RoomType.ELITE]:
            # 只要敌人已生成且屏幕上没有敌人了，就认为房间完成
            # 这样即使敌人跑出屏幕也不会阻止进度
            if len(mobs_group) == 0 and self.enemies_spawned:
                self.room_completed = True
                self.show_completion_ui = True
                room.enemies_cleared = True
                sound_mgr.play_sound("achievement")
                log_info(f"房间完成: {room.room_id}")
                return True  # 返回True表示需要暂停游戏
        
        # Boss房间：Boss被击败
        elif room.room_type == RoomType.BOSS:
            if boss is None and self.enemies_spawned:
                self.room_completed = True
                self.show_completion_ui = True
                room.enemies_cleared = True
                sound_mgr.play_sound("achievement")
                log_info(f"Boss房间完成: {room.room_id}")
                return True  # 返回True表示需要暂停游戏
        
        # 非战斗房间：进入即完成
        elif room.room_type in [RoomType.SHOP, RoomType.TREASURE, RoomType.REST, RoomType.EVENT]:
            if not self.room_completed:
                self.room_completed = True
                self.show_completion_ui = True
                return True  # 返回True表示需要暂停游戏
        
        return False
    
    def update(self):
        """更新房间系统"""
        if self.transition_active:
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                self.complete_transition()
    
    def draw_minimap(self, surface, x, y, width, height):
        """绘制小地图（右上角）"""
        # 半透明背景
        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        bg_surface.fill((20, 20, 40, 180))  # 70%透明度
        surface.blit(bg_surface, (x, y))
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (100, 100, 150), bg_rect, 2)
        
        # 标题
        try:
            font = pygame.font.SysFont("simhei,arial", 20)
        except:
            font = pygame.font.Font(None, 24)
        title = font.render("地图", True, (255, 255, 255))
        surface.blit(title, (x + 10, y + 5))
        
        if not self.current_room:
            return
        
        # 计算当前深度
        current_depth = self.current_room.depth
        
        # 只显示当前层和相邻层
        start_depth = max(0, current_depth - 1)
        end_depth = min(self.max_depth - 1, current_depth + 2)
        
        # 绘制房间
        room_size = 25
        spacing_x = 35
        spacing_y = 40
        
        for depth in range(start_depth, end_depth + 1):
            depth_rooms = [r for r in self.rooms.values() if r.depth == depth]
            
            for idx, room in enumerate(depth_rooms):
                # 计算位置
                relative_depth = depth - start_depth
                room_x = x + width // 2 - (len(depth_rooms) * spacing_x) // 2 + idx * spacing_x
                room_y = y + 40 + relative_depth * spacing_y
                
                # 绘制连接线
                if depth < end_depth:
                    for conn_id in room.connections:
                        if conn_id in self.rooms:
                            conn_room = self.rooms[conn_id]
                            if conn_room.depth == depth + 1:
                                conn_rooms = [r for r in self.rooms.values() if r.depth == depth + 1]
                                try:
                                    conn_idx = conn_rooms.index(conn_room)
                                    conn_x = x + width // 2 - (len(conn_rooms) * spacing_x) // 2 + conn_idx * spacing_x + room_size // 2
                                    conn_y = y + 40 + (relative_depth + 1) * spacing_y + room_size // 2
                                    
                                    line_color = (80, 80, 100) if room.state == RoomState.CLEARED else (60, 60, 80)
                                    pygame.draw.line(surface, line_color, 
                                                   (room_x + room_size // 2, room_y + room_size // 2),
                                                   (conn_x, conn_y), 2)
                                except ValueError:
                                    pass
                
                # 绘制房间节点
                room_rect = pygame.Rect(room_x, room_y, room_size, room_size)
                
                # 根据状态选择颜色
                if room.state == RoomState.CURRENT:
                    color = (255, 255, 100)
                    border_color = (255, 255, 0)
                    pygame.draw.rect(surface, color, room_rect)
                    pygame.draw.rect(surface, border_color, room_rect, 3)
                elif room.state == RoomState.CLEARED:
                    color = (100, 100, 100)
                    border_color = (150, 150, 150)
                    pygame.draw.rect(surface, color, room_rect)
                    pygame.draw.rect(surface, border_color, room_rect, 2)
                elif room.state == RoomState.AVAILABLE:
                    color = room.get_color()
                    pygame.draw.rect(surface, color, room_rect)
                    pygame.draw.rect(surface, (255, 255, 255), room_rect, 2)
                else:  # LOCKED
                    color = (40, 40, 50)
                    pygame.draw.rect(surface, color, room_rect)
                    pygame.draw.rect(surface, (80, 80, 90), room_rect, 1)
                
                # 绘制房间图标（使用缓存）
                icon_text = render_icon_cached(room.get_icon(), 18)
                icon_rect = icon_text.get_rect(center=room_rect.center)
                surface.blit(icon_text, icon_rect)
        
        # 显示当前深度
        try:
            depth_font = pygame.font.SysFont("simhei,arial", 18)
        except:
            depth_font = pygame.font.Font(None, 20)
        depth_text = depth_font.render(f"层数: {current_depth + 1}/{self.max_depth}", True, (200, 200, 200))
        surface.blit(depth_text, (x + 10, y + height - 25))
    
    def draw_fullmap(self, surface):
        """绘制完整地图界面（按M键显示）"""
        # 半透明背景
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((10, 10, 20))
        surface.blit(overlay, (0, 0))
        
        # 标题
        try:
            title_font = pygame.font.SysFont("simhei,arial", 42)
        except:
            title_font = pygame.font.Font(None, 48)
        title = title_font.render("房间地图", True, (255, 255, 100))
        title_rect = title.get_rect(center=(WIDTH // 2, 40))
        surface.blit(title, title_rect)
        
        # 提示文字
        try:
            hint_font = pygame.font.SysFont("simhei,arial", 20)
        except:
            hint_font = pygame.font.Font(None, 24)
        hint = hint_font.render("按 M 关闭地图 | 鼠标悬停查看房间详情", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(WIDTH // 2, 80))
        surface.blit(hint, hint_rect)
        
        # 计算布局
        map_area = pygame.Rect(50, 120, WIDTH - 100, HEIGHT - 200)
        room_size = 50
        spacing_x = 80
        spacing_y = 70
        
        # 绘制所有层
        for depth in range(self.max_depth):
            depth_rooms = [r for r in self.rooms.values() if r.depth == depth]
            
            for idx, room in enumerate(depth_rooms):
                # 计算位置
                room_x = map_area.x + map_area.width // 2 - (len(depth_rooms) * spacing_x) // 2 + idx * spacing_x
                room_y = map_area.y + depth * spacing_y
                
                # 绘制连接线
                for conn_id in room.connections:
                    if conn_id in self.rooms:
                        conn_room = self.rooms[conn_id]
                        conn_rooms = [r for r in self.rooms.values() if r.depth == conn_room.depth]
                        try:
                            conn_idx = conn_rooms.index(conn_room)
                            conn_x = map_area.x + map_area.width // 2 - (len(conn_rooms) * spacing_x) // 2 + conn_idx * spacing_x + room_size // 2
                            conn_y = map_area.y + conn_room.depth * spacing_y + room_size // 2
                            
                            line_color = (100, 100, 150) if room.state == RoomState.CLEARED else (60, 60, 80)
                            pygame.draw.line(surface, line_color,
                                           (room_x + room_size // 2, room_y + room_size // 2),
                                           (conn_x, conn_y), 3)
                        except ValueError:
                            pass
                
                # 绘制房间
                room_rect = pygame.Rect(room_x, room_y, room_size, room_size)
                
                # 检查鼠标悬停
                mouse_pos = pygame.mouse.get_pos()
                is_hovered = room_rect.collidepoint(mouse_pos)
                if is_hovered:
                    self.hovered_room = room
                
                # 根据状态绘制
                if room.state == RoomState.CURRENT:
                    color = (255, 255, 100)
                    border_color = (255, 255, 0)
                    border_width = 4
                elif room.state == RoomState.CLEARED:
                    color = (80, 80, 80)
                    border_color = (120, 120, 120)
                    border_width = 2
                elif room.state == RoomState.AVAILABLE:
                    color = room.get_color()
                    border_color = (255, 255, 255)
                    border_width = 3
                else:  # LOCKED
                    color = (30, 30, 40)
                    border_color = (60, 60, 70)
                    border_width = 1
                
                # 悬停效果
                if is_hovered:
                    color = tuple(min(255, c + 50) for c in color)
                    border_width += 1
                
                pygame.draw.rect(surface, color, room_rect)
                pygame.draw.rect(surface, border_color, room_rect, border_width)
                
                # 绘制图标（使用缓存）
                icon_text = render_icon_cached(room.get_icon(), 28)
                icon_rect = icon_text.get_rect(center=room_rect.center)
                surface.blit(icon_text, icon_rect)
        
        # 绘制图例
        self._draw_legend(surface, WIDTH - 250, 150)
        
        # 绘制悬停房间的详细信息
        if self.hovered_room:
            self._draw_room_tooltip(surface, self.hovered_room)
    
    def _draw_legend(self, surface, x, y):
        """绘制图例"""
        legend_bg = pygame.Rect(x, y, 220, 280)
        pygame.draw.rect(surface, (20, 20, 40), legend_bg)
        pygame.draw.rect(surface, (100, 100, 150), legend_bg, 2)
        
        try:
            font = pygame.font.SysFont("simhei,arial", 20)
        except:
            font = pygame.font.Font(None, 24)
        title = font.render("图例", True, (255, 255, 255))
        surface.blit(title, (x + 10, y + 10))
        
        legend_items = [
            (RoomType.COMBAT, "战斗"),
            (RoomType.ELITE, "精英战斗"),
            (RoomType.BOSS, "Boss"),
            (RoomType.SHOP, "商店"),
            (RoomType.TREASURE, "宝箱"),
            (RoomType.REST, "休息"),
            (RoomType.EVENT, "事件")
        ]
        
        try:
            small_font = pygame.font.SysFont("simhei,arial", 18)
        except:
            small_font = pygame.font.Font(None, 20)
        for i, (room_type, name) in enumerate(legend_items):
            item_y = y + 40 + i * 30
            
            # 颜色方块
            dummy_room = Room(room_type, 0, "dummy")
            color = dummy_room.get_color()
            color_rect = pygame.Rect(x + 15, item_y, 20, 20)
            pygame.draw.rect(surface, color, color_rect)
            pygame.draw.rect(surface, (255, 255, 255), color_rect, 1)
            
            # 图标（使用缓存）
            icon = dummy_room.get_icon()
            icon_text = render_icon_cached(icon, 18)
            surface.blit(icon_text, (x + 45, item_y + 2))
            
            # 名称
            name_text = small_font.render(name, True, (200, 200, 200))
            surface.blit(name_text, (x + 70, item_y + 2))
    
    def _draw_room_tooltip(self, surface, room):
        """绘制房间详细信息提示框"""
        mouse_pos = pygame.mouse.get_pos()
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 20
        
        # 防止超出屏幕
        tooltip_width = 250
        tooltip_height = 120
        if tooltip_x + tooltip_width > WIDTH:
            tooltip_x = mouse_pos[0] - tooltip_width - 20
        if tooltip_y + tooltip_height > HEIGHT:
            tooltip_y = mouse_pos[1] - tooltip_height - 20
        
        # 绘制背景
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(surface, (30, 30, 50), tooltip_rect)
        pygame.draw.rect(surface, (150, 150, 200), tooltip_rect, 2)
        
        # 房间信息
        try:
            font = pygame.font.SysFont("simhei,arial", 18)
        except:
            font = pygame.font.Font(None, 22)
        y_offset = tooltip_y + 10
        
        # 类型和状态
        type_names = {
            RoomType.COMBAT: "战斗房间",
            RoomType.ELITE: "精英战斗",
            RoomType.BOSS: "Boss房间",
            RoomType.SHOP: "商店",
            RoomType.TREASURE: "宝箱房间",
            RoomType.REST: "休息房间",
            RoomType.EVENT: "随机事件"
        }
        type_text = font.render(type_names.get(room.room_type, "未知"), True, room.get_color())
        surface.blit(type_text, (tooltip_x + 10, y_offset))
        y_offset += 25
        
        state_names = {
            RoomState.LOCKED: "未解锁",
            RoomState.AVAILABLE: "可进入",
            RoomState.CURRENT: "当前房间",
            RoomState.CLEARED: "已完成"
        }
        state_text = font.render(f"状态: {state_names.get(room.state, '未知')}", True, (200, 200, 200))
        surface.blit(state_text, (tooltip_x + 10, y_offset))
        y_offset += 22
        
        # 房间特定信息
        if room.room_type == RoomType.COMBAT:
            info_text = font.render(f"敌人数量: {room.enemy_count}", True, (200, 200, 200))
            surface.blit(info_text, (tooltip_x + 10, y_offset))
        elif room.room_type == RoomType.BOSS:
            info_text = font.render(f"Boss: {room.boss_type}", True, (255, 100, 100))
            surface.blit(info_text, (tooltip_x + 10, y_offset))
        elif room.room_type == RoomType.SHOP:
            info_text = font.render(f"商品: {len(room.shop_items)}件", True, (255, 215, 0))
            surface.blit(info_text, (tooltip_x + 10, y_offset))
        elif room.room_type == RoomType.REST:
            info_text = font.render(f"恢复: {room.heal_amount} HP", True, (100, 255, 100))
            surface.blit(info_text, (tooltip_x + 10, y_offset))
        
        y_offset += 22
        
        # 深度信息
        depth_text = font.render(f"层数: {room.depth + 1}", True, (150, 150, 200))
        surface.blit(depth_text, (tooltip_x + 10, y_offset))
    
    def draw_room_selection_ui(self, surface):
        """绘制房间选择UI（房间完成后）"""
        if not self.show_completion_ui or not self.current_room:
            return
        
        # 半透明背景
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # 标题
        try:
            title_font = pygame.font.SysFont("simhei,arial", 48)
            hint_font = pygame.font.SysFont("simhei,arial", 24)
            room_font = pygame.font.SysFont("simhei,arial", 28)
            desc_font = pygame.font.SysFont("simhei,arial", 20)
        except:
            title_font = pygame.font.Font(None, 48)
            hint_font = pygame.font.Font(None, 24)
            room_font = pygame.font.Font(None, 28)
            desc_font = pygame.font.Font(None, 20)
        
        title = title_font.render("房间完成！", True, (100, 255, 100))
        title_rect = title.get_rect(center=(WIDTH // 2, 100))
        surface.blit(title, title_rect)
        
        # 提示文字
        hint = hint_font.render("选择下一个房间", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(WIDTH // 2, 150))
        surface.blit(hint, hint_rect)
        
        # 获取可用的下一个房间
        if not self.available_next_rooms:
            self.available_next_rooms = []
            for room_id in self.current_room.connections:
                if room_id in self.rooms:
                    room = self.rooms[room_id]
                    if room.state == RoomState.AVAILABLE or room.state == RoomState.LOCKED:
                        self.available_next_rooms.append(room)
                        # 确保房间可用
                        if room.state == RoomState.LOCKED:
                            room.state = RoomState.AVAILABLE
        
        # 如果没有可选房间，显示胜利信息
        if not self.available_next_rooms:
            victory_text = title_font.render("恭喜通关！", True, (255, 215, 0))
            victory_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            surface.blit(victory_text, victory_rect)
            return
        
        # 绘制房间选项卡片
        card_width = 280
        card_height = 350
        gap = 40
        total_width = len(self.available_next_rooms) * card_width + (len(self.available_next_rooms) - 1) * gap
        start_x = (WIDTH - total_width) // 2
        card_y = 220
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, room in enumerate(self.available_next_rooms):
            card_x = start_x + i * (card_width + gap)
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            
            # 检查鼠标悬停
            is_hovered = card_rect.collidepoint(mouse_pos)
            is_selected = (i == self.selected_next_room)
            
            # 卡片背景
            bg_color = (60, 60, 80) if is_selected or is_hovered else (40, 40, 60)
            card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            pygame.draw.rect(card_surface, (*bg_color, 220), (0, 0, card_width, card_height), border_radius=10)
            surface.blit(card_surface, (card_x, card_y))
            
            # 边框
            border_color = (255, 255, 100) if is_selected else ((200, 200, 255) if is_hovered else (100, 100, 150))
            border_width = 4 if is_selected else (3 if is_hovered else 2)
            pygame.draw.rect(surface, border_color, card_rect, border_width, border_radius=10)
            
            # 房间图标（大号）
            icon_y = card_y + 50
            icon_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(icon_surface, room.get_color(), (50, 50), 45)
            pygame.draw.circle(icon_surface, (255, 255, 255), (50, 50), 45, 3)
            surface.blit(icon_surface, (card_x + (card_width - 100) // 2, icon_y))
            
            # 房间图标符号
            icon_text = render_icon_cached(room.get_icon(), 40)
            icon_rect = icon_text.get_rect(center=(card_x + card_width // 2, icon_y + 50))
            surface.blit(icon_text, icon_rect)
            
            # 房间类型名称
            type_names = {
                RoomType.COMBAT: "战斗房间",
                RoomType.ELITE: "精英战斗",
                RoomType.BOSS: "Boss房间",
                RoomType.SHOP: "商店",
                RoomType.TREASURE: "宝箱房间",
                RoomType.REST: "休息房间",
                RoomType.EVENT: "随机事件"
            }
            type_name = type_names.get(room.room_type, "未知房间")
            type_text = room_font.render(type_name, True, room.get_color())
            type_rect = type_text.get_rect(center=(card_x + card_width // 2, icon_y + 120))
            surface.blit(type_text, type_rect)
            
            # 房间描述
            y_offset = icon_y + 160
            descriptions = {
                RoomType.COMBAT: f"敌人: {room.enemy_count}",
                RoomType.ELITE: f"精英敌人: {room.enemy_count}",
                RoomType.BOSS: f"Boss: {room.boss_type}",
                RoomType.SHOP: f"商品: {len(room.shop_items)}件",
                RoomType.TREASURE: f"宝箱: {room.treasure_count}个",
                RoomType.REST: f"恢复: +{room.heal_amount} HP",
                RoomType.EVENT: "随机事件"
            }
            desc = descriptions.get(room.room_type, "")
            if desc:
                desc_text = desc_font.render(desc, True, (200, 200, 200))
                desc_rect = desc_text.get_rect(center=(card_x + card_width // 2, y_offset))
                surface.blit(desc_text, desc_rect)
                y_offset += 30
            
            # 难度提示
            diff_text = f"难度: {room.difficulty_multiplier:.1f}x"
            diff_color = (255, 100, 100) if room.difficulty_multiplier > 1.5 else ((255, 200, 100) if room.difficulty_multiplier > 1.0 else (100, 255, 100))
            diff_render = desc_font.render(diff_text, True, diff_color)
            diff_rect = diff_render.get_rect(center=(card_x + card_width // 2, y_offset))
            surface.blit(diff_render, diff_rect)
            
            # 选中提示
            if is_selected:
                select_hint = hint_font.render("按Enter确认", True, (255, 255, 100))
                select_rect = select_hint.get_rect(center=(card_x + card_width // 2, card_y + card_height - 30))
                surface.blit(select_hint, select_rect)
        
        # 底部提示
        control_hint = desc_font.render("← → 选择房间 | Enter 确认 | M 查看地图", True, (150, 150, 150))
        control_rect = control_hint.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        surface.blit(control_hint, control_rect)
