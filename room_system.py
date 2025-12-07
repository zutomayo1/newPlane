"""Room mode 2.0 - procedural acts, encounters, and UI."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import pygame

from config import HEIGHT, WIDTH
from utils import log_info, log_error, sound_mgr


class RoomType:
    COMBAT = "combat"
    ELITE = "elite"
    BOSS = "boss"
    SHOP = "shop"
    TREASURE = "treasure"
    REST = "rest"
    EVENT = "event"

    ALL = (COMBAT, ELITE, BOSS, SHOP, TREASURE, REST, EVENT)
    DISPLAY = {
        COMBAT: ("战斗", "⚔", (200, 200, 200)),
        ELITE: ("精英", "★", (255, 140, 0)),
        BOSS: ("Boss", "☠", (255, 70, 70)),
        SHOP: ("商店", "$", (255, 215, 0)),
        TREASURE: ("宝箱", "♦", (0, 255, 200)),
        REST: ("休息", "♥", (110, 255, 110)),
        EVENT: ("事件", "?", (200, 100, 255)),
    }


class RoomState:
    LOCKED = "locked"
    AVAILABLE = "available"
    CURRENT = "current"
    CLEARED = "cleared"


# 地图主题配置 - 三套不同的主题
MAP_THEMES = {
    "starfield": {
        "name": "星域迷航",
        "acts": [
            {
                "name": "恒星碎片地带",
                "depth": (0, 2),
                "theme": (80, 120, 180),
                "weights": {
                    RoomType.COMBAT: 0.6,
                    RoomType.TREASURE: 0.15,
                    RoomType.REST: 0.1,
                    RoomType.EVENT: 0.1,
                    RoomType.SHOP: 0.05,
                },
                "mutators": ["磁暴雾", "星尘加护"],
            },
            {
                "name": "深空共振",
                "depth": (2, 4),
                "theme": (120, 70, 180),
                "weights": {
                    RoomType.COMBAT: 0.35,
                    RoomType.ELITE: 0.25,
                    RoomType.EVENT: 0.15,
                    RoomType.TREASURE: 0.1,
                    RoomType.SHOP: 0.1,
                    RoomType.REST: 0.05,
                },
                "mutators": ["引力风暴", "相位噪声"],
            },
            {
                "name": "零点奇域",
                "depth": (4, 5),
                "theme": (200, 100, 120),
                "weights": {
                    RoomType.COMBAT: 0.2,
                    RoomType.ELITE: 0.4,
                    RoomType.EVENT: 0.15,
                    RoomType.TREASURE: 0.15,
                    RoomType.REST: 0.05,
                    RoomType.SHOP: 0.05,
                },
                "mutators": ["虚空反响", "裂隙蚀刻"],
            },
        ]
    },
    "cyberpunk": {
        "name": "赛博迷城",
        "acts": [
            {
                "name": "霓虹街区",
                "depth": (0, 2),
                "theme": (255, 0, 150),
                "weights": {
                    RoomType.COMBAT: 0.55,
                    RoomType.TREASURE: 0.15,
                    RoomType.REST: 0.1,
                    RoomType.EVENT: 0.15,
                    RoomType.SHOP: 0.05,
                },
                "mutators": ["数据风暴", "电磁干扰"],
            },
            {
                "name": "暗网节点",
                "depth": (2, 4),
                "theme": (0, 255, 200),
                "weights": {
                    RoomType.COMBAT: 0.4,
                    RoomType.ELITE: 0.2,
                    RoomType.EVENT: 0.15,
                    RoomType.TREASURE: 0.1,
                    RoomType.SHOP: 0.1,
                    RoomType.REST: 0.05,
                },
                "mutators": ["病毒入侵", "系统崩溃"],
            },
            {
                "name": "主机核心",
                "depth": (4, 5),
                "theme": (255, 200, 0),
                "weights": {
                    RoomType.COMBAT: 0.25,
                    RoomType.ELITE: 0.35,
                    RoomType.EVENT: 0.2,
                    RoomType.TREASURE: 0.1,
                    RoomType.REST: 0.05,
                    RoomType.SHOP: 0.05,
                },
                "mutators": ["防火墙", "量子加密"],
            },
        ]
    },
    "nightmare": {
        "name": "噩梦深渊",
        "acts": [
            {
                "name": "幽暗边缘",
                "depth": (0, 2),
                "theme": (100, 50, 120),
                "weights": {
                    RoomType.COMBAT: 0.6,
                    RoomType.TREASURE: 0.1,
                    RoomType.REST: 0.15,
                    RoomType.EVENT: 0.1,
                    RoomType.SHOP: 0.05,
                },
                "mutators": ["暗影侵蚀", "恐惧蔓延"],
            },
            {
                "name": "扭曲回廊",
                "depth": (2, 4),
                "theme": (150, 0, 80),
                "weights": {
                    RoomType.COMBAT: 0.3,
                    RoomType.ELITE: 0.3,
                    RoomType.EVENT: 0.15,
                    RoomType.TREASURE: 0.1,
                    RoomType.SHOP: 0.1,
                    RoomType.REST: 0.05,
                },
                "mutators": ["疯狂低语", "现实裂痕"],
            },
            {
                "name": "深渊之心",
                "depth": (4, 5),
                "theme": (80, 0, 0),
                "weights": {
                    RoomType.COMBAT: 0.2,
                    RoomType.ELITE: 0.45,
                    RoomType.EVENT: 0.15,
                    RoomType.TREASURE: 0.1,
                    RoomType.REST: 0.05,
                    RoomType.SHOP: 0.05,
                },
                "mutators": ["末日启示", "灵魂湮灭"],
            },
        ]
    }
}

# 当前使用的主题（默认）
CURRENT_MAP_THEME = "starfield"

# 兼容旧代码：从当前主题提取ACT配置
def get_current_acts():
    return MAP_THEMES[CURRENT_MAP_THEME]["acts"]

ACT_BLUEPRINTS: Sequence[Dict] = get_current_acts()

FINAL_DEPTH = 4  # 最后一层的索引（从0开始，所以总共5层：0,1,2,3,4）
ROOMS_PER_DEPTH = (1, 5, 5, 5, 1)  # 每层更多房间（5层）
MIN_CONNECTIONS = 1
MAX_CONNECTIONS = 4  # 增加最大连接数
MAP_ZOOM_MIN = 0.6  # 减小最小缩放，适应更宽的地图
MAP_ZOOM_MAX = 1.2
BASE_ROOM_SIZE = 48  # 轻微减小房间大小
BASE_SPACING_X = 85  # 调整横向间距
BASE_SPACING_Y = 100  # 增加纵向间距

DIFFICULTY_TABLE = {
    RoomType.COMBAT: (5, 8, 1.0),
    RoomType.ELITE: (3, 5, 1.6),
    RoomType.BOSS: (1, 1, 3.0),
}

REWARD_PRESETS = {
    RoomType.COMBAT: {"exp": (20, 40), "score": (100, 200)},
    RoomType.ELITE: {"exp": (50, 80), "score": (300, 500), "card": 1},
    RoomType.BOSS: {"exp": (100, 150), "score": (800, 1200), "card": 2},
    RoomType.TREASURE: {"item": 1},
    RoomType.SHOP: {"shop_access": True},
    RoomType.REST: {"heal": (30, 60)},
    RoomType.EVENT: {"random": True},
}

# 商店物品配置
SHOP_ITEMS = [
    {"name": "生命恢复包", "desc": "恢复50点生命", "price": 300, "type": "heal", "value": 50},
    {"name": "经验提升", "desc": "获得100点经验", "price": 400, "type": "exp", "value": 100},
    {"name": "随机物品", "desc": "获得1个随机物品", "price": 500, "type": "item", "value": 1},
    {"name": "卡牌选择", "desc": "立即获得1次升级选择", "price": 600, "type": "card", "value": 1},
]

# 房间修饰符（简化版）
ROOM_MODIFIERS = {
    "double_reward": {"name": "双倍奖励", "reward_mult": 2.0, "difficulty_add": 0.3},
    "elite_boost": {"name": "精英强化", "reward_mult": 1.8, "difficulty_add": 0.6},
    "speed_bonus": {"name": "速战速决", "reward_mult": 1.5, "difficulty_add": 0.2},
}

REWARD_LABELS = {
    "exp": "经验",
    "score": "积分",
    "card": "卡牌选择",
    "item": "随机物品",
    "heal": "生命",
    "shop_access": "商店",
    "random": "随机事件",
}


@dataclass
class RoomNode:
    room_id: str
    depth: int
    room_type: str
    difficulty: float
    act_name: str
    mutator: Optional[str]
    reward_hint: Dict
    state: str = RoomState.LOCKED
    connections: List[str] = field(default_factory=list)
    preview: Dict = field(default_factory=dict)
    visited: bool = False
    theme_color: Tuple[int, int, int] = (50, 70, 120)
    is_secret: bool = False  # 是否是秘密房间
    modifier: Optional[str] = None  # 房间修饰符

    def color(self) -> Tuple[int, int, int]:
        return RoomType.DISPLAY.get(self.room_type, ("", "·", (140, 140, 140)))[2]

    def icon(self) -> str:
        return RoomType.DISPLAY.get(self.room_type, ("", "·", (140, 140, 140)))[1]


_icon_cache: Dict[Tuple[str, int], pygame.Surface] = {}


def _render_icon_cached(symbol: str, size: int) -> pygame.Surface:
    key = (symbol, size)
    if key not in _icon_cache:
        try:
            font = pygame.font.SysFont(
                "segoeuisymbol,segoeuiemoji,segoeui,microsoftyaheiu,simhei,arial", size
            )
        except Exception:
            font = pygame.font.Font(None, size)
        _icon_cache[key] = font.render(symbol, True, (255, 255, 255))
    return _icon_cache[key]


def _pick_room_type(depth: int) -> str:
    for act in ACT_BLUEPRINTS:
        if act["depth"][0] <= depth < act["depth"][1]:
            weights = act["weights"]
            break
    else:
        weights = {RoomType.COMBAT: 1.0}
    r = random.random()
    cumulative = 0.0
    for room_type, value in weights.items():
        cumulative += value
        if r <= cumulative:
            return room_type
    return RoomType.COMBAT


def _room_reward_hint(room_type: str) -> Dict:
    hint = REWARD_PRESETS.get(room_type, {}).copy()
    if "credits" in hint:
        low, high = hint["credits"]
        hint["credits"] = int((low + high) / 2)
    if "heal" in hint:
        low, high = hint["heal"]
        hint["heal"] = int((low + high) / 2)
    return hint


def _format_reward_hint(hint: Dict) -> str:
    parts: List[str] = []
    for key, value in hint.items():
        label = REWARD_LABELS.get(key, key)
        if isinstance(value, bool):
            parts.append(label)
        elif isinstance(value, (int, float)):
            sign = "+" if value >= 0 else ""
            if key == "heal":
                parts.append(f"{label}{sign}{int(value)}")
            elif key == "card":
                parts.append(f"{label}×{int(value)}")
            elif key == "item":
                parts.append(f"{label}×{int(value)}")
            else:
                parts.append(f"{label}{sign}{int(value)}")
        elif isinstance(value, (tuple, list)) and len(value) == 2:
            parts.append(f"{label}{value[0]}~{value[1]}")
        else:
            parts.append(f"{label}")
    return "、".join(parts) if parts else "未知奖励"


def _truncate_text(font, text: str, max_width: int) -> str:
    """截断文字以适应指定宽度，超出部分用...代替"""
    if font.size(text)[0] <= max_width:
        return text
    
    # 逐个字符减少直到适合
    for i in range(len(text), 0, -1):
        truncated = text[:i] + "..."
        if font.size(truncated)[0] <= max_width:
            return truncated
    
    return "..."


def _difficulty_for_room(room_type: str, depth: int) -> float:
    base_min, base_max, base_mult = DIFFICULTY_TABLE.get(room_type, (0, 0, 1.0))
    scale = 1.0 + depth * 0.15
    enemies = random.randint(base_min, base_max) if base_min else 0
    return round(base_mult * scale, 2) if enemies else base_mult * scale


def _act_name_for_depth(depth: int) -> str:
    for act in ACT_BLUEPRINTS:
        if act["depth"][0] <= depth < act["depth"][1]:
            return act["name"]
    return "？？？"


def _mutator_for_depth(depth: int) -> Optional[str]:
    for act in ACT_BLUEPRINTS:
        if act["depth"][0] <= depth < act["depth"][1]:
            return random.choice(act["mutators"])
    return None


def _theme_color_for_depth(depth: int) -> Tuple[int, int, int]:
    for act in ACT_BLUEPRINTS:
        if act["depth"][0] <= depth < act["depth"][1]:
            return act.get("theme", (60, 80, 120))
    return (60, 80, 120)


def _blend_color(color: Tuple[int, int, int], alpha: float, base: Tuple[int, int, int] = (20, 20, 30)) -> Tuple[int, int, int]:
    alpha = max(0.0, min(1.0, alpha))
    return tuple(int(base[i] * (1 - alpha) + color[i] * alpha) for i in range(3))


def _auto_fullmap_scale(map_area: pygame.Rect, all_rooms: Dict[str, RoomNode]) -> float:
    max_nodes = max((len([r for r in all_rooms.values() if r.depth == depth]) for depth in range(len(ROOMS_PER_DEPTH))), default=1)
    required_w = max_nodes * BASE_SPACING_X + BASE_ROOM_SIZE
    required_h = (len(ROOMS_PER_DEPTH) - 1) * BASE_SPACING_Y + BASE_ROOM_SIZE
    scale_w = map_area.width / max(1, required_w)
    scale_h = map_area.height / max(1, required_h)
    return min(1.0, scale_w, scale_h)


class RoomManager:
    def __init__(self, theme: str = None) -> None:
        self.rooms: Dict[str, RoomNode] = {}
        self.current_room: Optional[RoomNode] = None
        self.player_path: List[str] = []
        self.transition_timer = 0
        self.transition_active = False
        self.next_room: Optional[RoomNode] = None
        self.enemies_spawned = False
        self.room_completed = False
        self.show_completion_ui = False
        self.non_combat_room_ready = False
        # 地图主题和进度
        self.theme = theme or CURRENT_MAP_THEME
        self.map_sequence = ["starfield", "cyberpunk", "nightmare"]  # 线性顺序
        self.current_map_index = 0  # 当前地图索引
        if theme:
            # 如果指定了主题，找到它在序列中的位置
            try:
                self.current_map_index = self.map_sequence.index(theme)
            except ValueError:
                self.current_map_index = 0
                self.theme = self.map_sequence[0]
        else:
            self.theme = self.map_sequence[0]  # 从第一张地图开始
        self._update_theme()
        self.available_next_rooms: List[RoomNode] = []
        self.selected_next_room = 0
        self.map_visible = False
        self.hovered_room: Optional[RoomNode] = None
        self.currency = 0
        self.map_zoom = 1.0
        self.target_zoom = 1.0  # 目标缩放值
        self.zoom_speed = 0.15  # 缩放动画速度
        self.show_shop_ui = False
        self.shop_items: List[Dict] = []
        self.shop_selected = 0
        # Boss房间动画
        self.boss_anim_timer = 0
        # 奖励动画
        self.reward_floaters: List[Dict] = []  # {"text": str, "x": float, "y": float, "vy": float, "alpha": int, "color": tuple}
        # 动态难度
        self.performance_score = 1.0  # 玩家表现评分
        self.room_start_time = 0
        self.damage_taken_in_room = 0
        # 波次刷怪系统
        self.current_wave = 0
        self.total_waves = 0
        self.wave_spawn_timer = 0
        self.wave_spawn_delay = 180  # 每波之间的间隔（帧）
        self.enemies_in_current_wave = 0
        self.total_enemies_spawned = 0
        self.max_concurrent_enemies = 8  # 同时存在的最大敌人数
    
    def _update_theme(self) -> None:
        """更新当前主题配置"""
        global ACT_BLUEPRINTS
        if self.theme in MAP_THEMES:
            ACT_BLUEPRINTS = MAP_THEMES[self.theme]["acts"]
        else:
            self.theme = CURRENT_MAP_THEME
            ACT_BLUEPRINTS = MAP_THEMES[CURRENT_MAP_THEME]["acts"]
    
    def set_theme(self, theme: str) -> bool:
        """切换地图主题"""
        if theme not in MAP_THEMES:
            return False
        self.theme = theme
        self._update_theme()
        return True
    
    def get_theme_name(self) -> str:
        """获取当前主题名称"""
        return MAP_THEMES.get(self.theme, {}).get("name", "未知主题")
    
    def get_map_progress(self) -> str:
        """获取地图进度信息"""
        return f"{self.current_map_index + 1}/{len(self.map_sequence)}"
    
    def is_final_map(self) -> bool:
        """判断是否是最后一张地图"""
        return self.current_map_index >= len(self.map_sequence) - 1
    
    def advance_to_next_map(self) -> bool:
        """进入下一张地图，返回True表示成功，False表示已是最后一张"""
        if self.is_final_map():
            return False
        
        self.current_map_index += 1
        self.theme = self.map_sequence[self.current_map_index]
        self._update_theme()
        
        # 重置地图状态
        self.rooms.clear()
        self.current_room = None
        self.player_path.clear()
        self.enemies_spawned = False
        self.room_completed = False
        self.show_completion_ui = False
        self.available_next_rooms.clear()
        self.selected_next_room = 0
        
        # 生成新地图
        self.generate_map()
        return True

    def generate_map(self) -> None:
        self.rooms.clear()
        for depth, node_count in enumerate(ROOMS_PER_DEPTH):
            for idx in range(node_count):
                room_id = f"room_{depth}_{idx}"
                if depth == FINAL_DEPTH:
                    room_type = RoomType.BOSS
                elif depth == 0:
                    room_type = RoomType.COMBAT
                else:
                    room_type = _pick_room_type(depth)
                node = RoomNode(
                    room_id=room_id,
                    depth=depth,
                    room_type=room_type,
                    difficulty=_difficulty_for_room(room_type, depth),
                    act_name=_act_name_for_depth(depth),
                    mutator=_mutator_for_depth(depth),
                    reward_hint=_room_reward_hint(room_type),
                    theme_color=_theme_color_for_depth(depth),
                )
                if depth == 0:
                    node.state = RoomState.CURRENT
                    self.current_room = node
                self.rooms[room_id] = node
        self._connect_rooms()
        self.player_path = [self.current_room.room_id] if self.current_room else []
        self._unlock_connected_rooms()
        
        # 调试：检查Boss房间
        boss_rooms = [r for r in self.rooms.values() if r.room_type == RoomType.BOSS]
        for boss in boss_rooms:
            log_info(f"Boss房间: {boss.room_id}, depth={boss.depth}, connections={len(boss.connections)}")
        
        log_info(f"房间模式生成完成: {len(self.rooms)} rooms, FINAL_DEPTH={FINAL_DEPTH}")

    def _connect_rooms(self) -> None:
        for depth in range(len(ROOMS_PER_DEPTH) - 1):
            current = [r for r in self.rooms.values() if r.depth == depth]
            nxt = [r for r in self.rooms.values() if r.depth == depth + 1]
            if not current or not nxt:
                continue
            for node in current:
                count = random.randint(MIN_CONNECTIONS, min(MAX_CONNECTIONS, len(nxt)))
                picks = random.sample(nxt, count)
                node.connections = [p.room_id for p in picks]
            for target in nxt:
                inbound = any(target.room_id in node.connections for node in current)
                if not inbound:
                    random.choice(current).connections.append(target.room_id)

    def _unlock_connected_rooms(self) -> None:
        if not self.current_room:
            return
        for room_id in self.current_room.connections:
            node = self.rooms.get(room_id)
            if node and node.state == RoomState.LOCKED:
                node.state = RoomState.AVAILABLE

    def adjust_map_zoom(self, delta: float) -> None:
        if abs(delta) < 1e-6:
            return
        scale = 1.0 + delta
        if scale <= 0:
            return
        # 设置目标缩放值而不是直接修改
        self.target_zoom *= scale
        self.target_zoom = max(MAP_ZOOM_MIN, min(MAP_ZOOM_MAX, self.target_zoom))

    def enter_room(self, room_id: str) -> bool:
        node = self.rooms.get(room_id)
        if not node or node.state not in (RoomState.AVAILABLE, RoomState.CURRENT):
            return False
        self.transition_active = True
        self.transition_timer = 30
        self.next_room = node
        return True

    def complete_transition(self) -> None:
        if not self.next_room:
            return
        if self.current_room:
            self.current_room.state = RoomState.CLEARED
        self.current_room = self.next_room
        self.current_room.state = RoomState.CURRENT
        self.current_room.visited = True
        self.player_path.append(self.current_room.room_id)
        self.next_room = None
        self.transition_active = False
        self.enemies_spawned = False
        self.room_completed = False
        self.show_completion_ui = False
        self.non_combat_room_ready = False
        self.show_shop_ui = False
        self.shop_items.clear()
        self.available_next_rooms.clear()
        self.selected_next_room = 0
        # 重置波次系统
        self.current_wave = 0
        self.total_waves = 0
        self.wave_spawn_timer = 0
        self.enemies_in_current_wave = 0
        self.total_enemies_spawned = 0
        self._unlock_connected_rooms()
        sound_mgr.play_sound("levelup")
        log_info(f"进入房间: {self.current_room.room_id} ({self.current_room.room_type})")

    def clear_current_room(self) -> None:
        if self.current_room:
            self.current_room.state = RoomState.CLEARED

    def spawn_room_enemies(self, enemy_factory, mobs_group, all_sprites, boss_ref=None, boss_manager=None) -> None:
        """初始化房间刷怪系统（波次模式）"""
        if not self.current_room or self.enemies_spawned:
            return
        
        room = self.current_room
        
        # 非战斗房间
        if room.room_type not in (RoomType.COMBAT, RoomType.ELITE, RoomType.BOSS):
            log_info(f"非战斗房间 {room.room_id} 无需生成敌人")
            self.enemies_spawned = True
            self.non_combat_room_ready = True
            return
        
        # 初始化波次系统
        self._init_wave_system(room)
        
        # 保存引用供后续使用
        self.all_sprites = all_sprites
        self.boss_ref = boss_ref
        self.boss_manager = boss_manager
        
        # 生成第一波敌人（Boss房间需要特殊处理）
        self._spawn_next_wave(enemy_factory, mobs_group, boss_ref, boss_manager)
        
        self.enemies_spawned = True
        log_info(f"房间 {room.room_id} 刷怪系统初始化完成: {self.total_waves}波，难度 {room.difficulty:.2f}")
    
    def _init_wave_system(self, room: RoomNode) -> None:
        """初始化波次系统参数"""
        # 根据房间类型设置波次数量
        if room.room_type == RoomType.BOSS:
            self.total_waves = 5  # Boss房间5波
            self.wave_spawn_delay = 240
            self.max_concurrent_enemies = 6
        elif room.room_type == RoomType.ELITE:
            self.total_waves = 4  # 精英房间4波
            self.wave_spawn_delay = 200
            self.max_concurrent_enemies = 7
        else:
            # 普通战斗房间：根据难度和深度决定波次
            base_waves = 3
            difficulty_bonus = 1 if room.difficulty > 2.5 else 0
            depth_bonus = room.depth // 2
            self.total_waves = min(6, base_waves + difficulty_bonus + depth_bonus)
            self.wave_spawn_delay = 180
            self.max_concurrent_enemies = 8
        
        self.current_wave = 0
        self.wave_spawn_timer = 0
        self.total_enemies_spawned = 0
    
    def _spawn_next_wave(self, enemy_factory, mobs_group, boss_ref=None, boss_manager=None) -> None:
        """生成下一波敌人"""
        if not self.current_room or self.current_wave >= self.total_waves:
            return
        
        room = self.current_room
        self.current_wave += 1
        
        # Boss房间第一波：生成真正的Boss（如果提供了boss_manager）
        if room.room_type == RoomType.BOSS and self.current_wave == 1 and boss_manager:
            try:
                # 从boss_manager的可用Boss中随机选一个
                import random as rnd
                available_bosses = list(boss_manager.boss_db.keys())
                if available_bosses:
                    boss_key = rnd.choice(available_bosses)
                    boss_data = boss_manager.boss_db[boss_key]
                    
                    # 生成Boss
                    from sprites import Boss
                    if boss_ref is not None and isinstance(boss_ref, list) and len(boss_ref) > 0:
                        new_boss = Boss(boss_key, boss_data, room.difficulty)
                        boss_ref[0] = new_boss
                        # 将Boss添加到精灵组
                        if hasattr(self, 'all_sprites') and self.all_sprites:
                            self.all_sprites.add(new_boss)
                        log_info(f"Boss房间生成Boss: {boss_key}, 难度倍数: {room.difficulty:.2f}")
                    return  # Boss生成后,第一波不生成其他敌人
            except Exception as e:
                log_error(f"生成Boss失败: {e}")
        
        # 敌人池
        light_pool = ["scout_moth", "trooper_spear", "lurker_halo", "bomber_deepjelly", "shield_beeguard", "weaver_dualwasp"]
        heavy_pool = ["plasma_storm", "jammer_amethyst", "splitter_azurecore", "sniper_blackneedle", "summoner_nethalo", "prism_voidprism", "guard_heavyanvil", "judge_dualpolar"]
        
        # 基础属性
        base_hp = 80 + int(room.difficulty * 45)
        base_damage = 10 + room.difficulty * 3.5
        
        # 波次难度递增
        wave_mult = 1.0 + (self.current_wave - 1) * 0.15
        
        # 计算本波敌人数量
        if room.room_type == RoomType.BOSS:
            # Boss房间：第2-5波生成支援敌人
            spawn_count = random.randint(2, 3)
            enemy_pool = heavy_pool
            is_elite = True
            hp_mult = 1.5 * wave_mult
            dmg_mult = 1.3 * wave_mult
        elif room.room_type == RoomType.ELITE:
            # 精英房间：混合精英和普通
            spawn_count = random.randint(3, 5)
            enemy_pool = heavy_pool if random.random() < 0.6 else light_pool
            is_elite = random.random() < 0.5
            hp_mult = (1.5 if is_elite else 1.0) * wave_mult
            dmg_mult = (1.3 if is_elite else 1.0) * wave_mult
        else:
            # 普通房间：前期轻型，后期混合
            base_count = 4 + room.depth
            spawn_count = random.randint(max(3, base_count - 2), base_count + 2)
            
            # 后面的波次更多重型敌人
            heavy_chance = 0.2 + (self.current_wave / self.total_waves) * 0.4
            enemy_pool = heavy_pool if random.random() < heavy_chance else light_pool
            is_elite = random.random() < 0.15 * self.current_wave
            hp_mult = (1.4 if is_elite else 1.0) * wave_mult
            dmg_mult = (1.2 if is_elite else 1.0) * wave_mult
        
        # 生成敌人
        spawned_count = 0
        summary: Dict[str, int] = {}
        
        for _ in range(spawn_count):
            enemy_type = random.choice(enemy_pool)
            summary[enemy_type] = summary.get(enemy_type, 0) + 1
            
            # 随机边缘生成
            edge = random.choice(["top", "left", "right", "bottom"])
            if edge == "top":
                x, y = random.randint(60, WIDTH - 60), -70
            elif edge == "bottom":
                x, y = random.randint(60, WIDTH - 60), HEIGHT + 70
            elif edge == "left":
                x, y = -70, random.randint(60, HEIGHT - 60)
            else:
                x, y = WIDTH + 70, random.randint(60, HEIGHT - 60)
            
            try:
                enemy_factory.create_enemy(
                    enemy_type,
                    spawn_pos=(x, y),
                    override_config={
                        "hp": int(base_hp * hp_mult),
                        "is_elite": is_elite,
                        "damage": int(base_damage * dmg_mult),
                    },
                )
                spawned_count += 1
                self.total_enemies_spawned += 1
            except Exception as exc:
                log_error(f"生成敌人失败 {enemy_type}: {exc}")
        
        self.enemies_in_current_wave = spawned_count
        summary_text = ", ".join(f"{k}×{v}" for k, v in summary.items())
        log_info(f"第 {self.current_wave}/{self.total_waves} 波: 生成 {spawned_count} 名敌人 ({summary_text})")
    
    def update_wave_spawning(self, enemy_factory, mobs_group) -> None:
        """更新波次刷怪（每帧调用）"""
        if not self.current_room or self.room_completed:
            return
        
        if self.current_wave >= self.total_waves:
            return  # 所有波次已生成
        
        # 检查是否需要生成下一波
        current_enemy_count = len(mobs_group)
        
        # 条件1：当前敌人数量低于上限
        # 条件2：距离上一波已经过了足够时间
        self.wave_spawn_timer += 1
        
        if current_enemy_count < self.max_concurrent_enemies // 2:
            # 敌人数量少，快速刷新下一波
            if self.wave_spawn_timer >= 60:
                self._spawn_next_wave(enemy_factory, mobs_group, self.boss_ref, self.boss_manager)
                self.wave_spawn_timer = 0
        elif current_enemy_count == 0 and self.current_wave < self.total_waves:
            # 清空了所有敌人,立即刷新下一波
            self._spawn_next_wave(enemy_factory, mobs_group, self.boss_ref, self.boss_manager)
            self.wave_spawn_timer = 0
        elif self.wave_spawn_timer >= self.wave_spawn_delay:
            # 达到时间间隔,刷新下一波
            if current_enemy_count < self.max_concurrent_enemies:
                self._spawn_next_wave(enemy_factory, mobs_group, self.boss_ref, self.boss_manager)
                self.wave_spawn_timer = 0

    def check_room_completion(self, mobs_group, boss=None) -> Optional[Dict]:
        """检查房间是否完成，返回奖励字典（完成）或None（未完成）"""
        if not self.current_room or self.room_completed:
            return None
        
        room = self.current_room
        
        # 战斗房间：需要清空所有敌人 AND 完成所有波次
        if room.room_type in (RoomType.COMBAT, RoomType.ELITE):
            if self.enemies_spawned and len(mobs_group) == 0 and self.current_wave >= self.total_waves:
                rewards = self._finish_room()
                log_info(f"房间完成: {room.room_id}, 共消灭 {self.total_enemies_spawned} 名敌人")
                return rewards
        
        # Boss房间：需要击败Boss AND 完成所有波次
        elif room.room_type == RoomType.BOSS:
            if boss is None and self.enemies_spawned and len(mobs_group) == 0 and self.current_wave >= self.total_waves:
                rewards = self._finish_room()
                log_info(f"Boss房间完成: {room.room_id}, 共消灭 {self.total_enemies_spawned} 名敌人")
                return rewards
        
        # 非战斗房间已经在handle_non_combat_room中处理，这里不重复
        return None

    def handle_non_combat_room(self) -> Optional[Dict]:
        """处理非战斗房间（宝箱、休息、商店、事件）并返回是否需要显示UI"""
        if not self.current_room or not hasattr(self, 'non_combat_room_ready') or not self.non_combat_room_ready:
            return None
        
        room_type = self.current_room.room_type
        result = {"type": room_type}
        
        if room_type == RoomType.TREASURE:
            # 宝箱房间：返回需要显示UI的信号
            result["action"] = "open_chest"
            result["message"] = "发现一个神秘宝箱！"
        elif room_type == RoomType.REST:
            # 休息房间：返回需要显示UI的信号
            result["action"] = "rest"
            result["message"] = "一个安全的休息区域。"
        elif room_type == RoomType.SHOP:
            # 商店房间：生成商店物品列表
            result["action"] = "shop"
            result["message"] = "欢迎光临商店！"
            # 随机选择3-4个商品
            num_items = random.randint(3, 4)
            result["shop_items"] = random.sample(SHOP_ITEMS, min(num_items, len(SHOP_ITEMS)))
        elif room_type == RoomType.EVENT:
            # 随机事件
            events = [
                {"标题": "神秘信号", "内容": "接收到一条古老的信号。", "奖励": {"exp": 30}},
                {"标题": "废弃补给站", "内容": "发现一些有用的物资。", "奖励": {"heal": 40}},
                {"标题": "能量异常", "内容": "空间中涌动着奇异的能量。", "奖励": {"score": 300}},
                {"标题": "古代遗迹", "内容": "一处古老文明的遗迹。", "奖励": {"item": 1}},
            ]
            event = random.choice(events)
            result["action"] = "event"
            result["event_data"] = event
        
        self.non_combat_room_ready = False
        return result
    
    def _finish_room(self) -> Dict:
        """完成房间并返回奖励数据"""
        if self.room_completed:
            return {}  # 已经完成，不重复奖励
        
        self.room_completed = True
        self.show_completion_ui = True
        self.enemies_spawned = True
        sound_mgr.play_sound("achievement")
        
        # 返回实际奖励数据
        rewards = {}
        if self.current_room:
            hint = self.current_room.reward_hint
            # 随机化范围奖励
            for key, value in hint.items():
                if isinstance(value, tuple) and len(value) == 2:
                    rewards[key] = random.randint(value[0], value[1])
                else:
                    rewards[key] = value
        
        # 创建奖励动画
        self._create_reward_floaters(rewards)
        
        return rewards
    
    def _create_reward_floaters(self, rewards: Dict) -> None:
        """创建奖励飘字动画"""
        center_x, center_y = WIDTH // 2, HEIGHT // 3
        
        for idx, (key, value) in enumerate(rewards.items()):
            label = REWARD_LABELS.get(key, key)
            if isinstance(value, (int, float)):
                text = f"+{label} {int(value)}"
            elif isinstance(value, bool):
                text = f"+{label}"
            else:
                text = f"+{label}"
            
            # 散布在中心附近
            offset_x = random.randint(-120, 120)
            offset_y = idx * 35
            
            self.reward_floaters.append({
                "text": text,
                "x": center_x + offset_x,
                "y": center_y + offset_y,
                "vy": -1.2,
                "alpha": 255,
                "color": (255, 255, 100) if "score" in key.lower() else (150, 255, 150),
                "lifetime": 80
            })

    def update(self) -> None:
        if self.transition_active:
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                self.complete_transition()
        
        # 平滑缩放动画
        if abs(self.map_zoom - self.target_zoom) > 0.001:
            self.map_zoom += (self.target_zoom - self.map_zoom) * self.zoom_speed
        else:
            self.map_zoom = self.target_zoom
        
        # Boss房间动画计时器
        self.boss_anim_timer = (self.boss_anim_timer + 1) % 120
        
        # 更新奖励飘字动画
        for floater in self.reward_floaters[:]:
            floater["y"] += floater["vy"]
            floater["lifetime"] -= 1
            floater["alpha"] = int(255 * (floater["lifetime"] / 80))
            if floater["lifetime"] <= 0:
                self.reward_floaters.remove(floater)
    
    def try_purchase_item(self, item_index: int) -> Optional[Dict]:
        """尝试购买商店物品，返回购买结果"""
        if not self.show_shop_ui or item_index >= len(self.shop_items):
            return None
        
        item = self.shop_items[item_index]
        price = item["price"]
        
        if self.currency >= price:
            self.currency -= price
            # 移除已购买物品
            purchased_item = self.shop_items.pop(item_index)
            # 调整选中索引
            if self.shop_selected >= len(self.shop_items) and self.shop_selected > 0:
                self.shop_selected -= 1
            sound_mgr.play_sound("levelup")
            return purchased_item
        else:
            sound_mgr.play_sound("hit")
            return None
    
    def close_shop(self) -> None:
        """关闭商店并完成房间"""
        self.show_shop_ui = False
        self.shop_items.clear()
        self.shop_selected = 0
        # 不在这里调用_finish_room，由main.py负责

    def _draw_room_node(self, surface: pygame.Surface, rect: pygame.Rect, node: RoomNode, highlight: bool = False) -> None:
        base_color = node.color()
        border = (255, 255, 255)
        status = node.state
        
        # Boss房间特殊效果
        is_boss = node.room_type == RoomType.BOSS
        if is_boss and status != RoomState.CLEARED:
            # 脉动效果：使用sin波形
            import math
            pulse = abs(math.sin(self.boss_anim_timer * 0.05))
            glow_alpha = int(80 + 60 * pulse)
            glow_size = int(6 + 4 * pulse)
            
            # 绘制外发光
            glow_rect = rect.inflate(glow_size * 2, glow_size * 2)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*base_color, glow_alpha), glow_surf.get_rect(), border_radius=8)
            surface.blit(glow_surf, glow_rect.topleft)
        
        if status == RoomState.CURRENT:
            fill = tuple(min(255, c + 40) for c in base_color)
            border = (255, 255, 120)
            width = 4
        elif status == RoomState.CLEARED:
            fill = tuple(max(60, c // 2) for c in base_color)
            width = 2
        elif status == RoomState.AVAILABLE:
            fill = tuple(min(255, c + 30) for c in base_color)
            width = 3
        else:
            fill = (40, 40, 50)
            border = (90, 90, 110)
            width = 2
        
        if highlight:
            width += 1
            fill = tuple(min(255, c + 30) for c in fill)
        
        # Boss房间额外的边框效果
        if is_boss and status != RoomState.CLEARED:
            import math
            pulse = abs(math.sin(self.boss_anim_timer * 0.05))
            border = tuple(int(c + (255 - c) * pulse * 0.5) for c in base_color)
            width = max(width, 4)
        
        pygame.draw.rect(surface, fill, rect, border_radius=6)
        pygame.draw.rect(surface, border, rect, width, border_radius=6)
        icon_surface = _render_icon_cached(node.icon(), min(28, rect.width - 8))
        icon_rect = icon_surface.get_rect(center=rect.center)
        surface.blit(icon_surface, icon_rect)
    
    def draw_reward_floaters(self, surface: pygame.Surface) -> None:
        """绘制奖励飘字动画"""
        if not self.reward_floaters:
            return
        
        font = pygame.font.SysFont("simhei,arial", 32, bold=True)
        for floater in self.reward_floaters:
            if floater["alpha"] > 0:
                text_surf = font.render(floater["text"], True, floater["color"])
                text_surf.set_alpha(floater["alpha"])
                text_rect = text_surf.get_rect(center=(int(floater["x"]), int(floater["y"])))
                # 添加阴影效果
                shadow_surf = font.render(floater["text"], True, (0, 0, 0))
                shadow_surf.set_alpha(floater["alpha"] // 2)
                surface.blit(shadow_surf, (text_rect.x + 2, text_rect.y + 2))
                surface.blit(text_surf, text_rect)
    
    def draw_wave_info(self, surface: pygame.Surface) -> None:
        """绘制波次信息UI"""
        if not self.current_room or self.room_completed:
            return
        
        # 只在战斗房间显示
        if self.current_room.room_type not in (RoomType.COMBAT, RoomType.ELITE, RoomType.BOSS):
            return
        
        if self.total_waves <= 0:
            return
        
        # 绘制波次信息框 - 右侧中间位置
        info_w, info_h = 180, 70
        info_x, info_y = WIDTH - info_w - 20, HEIGHT // 2 - info_h // 2
        
        # 半透明背景
        info_surf = pygame.Surface((info_w, info_h), pygame.SRCALPHA)
        info_surf.fill((30, 30, 50, 220))
        surface.blit(info_surf, (info_x, info_y))
        
        # 边框
        pygame.draw.rect(surface, (150, 180, 255), (info_x, info_y, info_w, info_h), 3, border_radius=10)
        
        # 文字
        font = pygame.font.SysFont("simhei,arial", 22, bold=True)
        small_font = pygame.font.SysFont("simhei,arial", 17)
        
        # 标题
        title_text = small_font.render("敌人波次", True, (180, 200, 255))
        surface.blit(title_text, (info_x + 10, info_y + 8))
        
        # 波次进度 - 大号显示
        wave_text = f"{self.current_wave}/{self.total_waves}"
        wave_color = (150, 255, 150) if self.current_wave >= self.total_waves else (255, 220, 150)
        wave_render = font.render(wave_text, True, wave_color)
        surface.blit(wave_render, (info_x + 15, info_y + 32))
        
        # 如果还有下一波，显示倒计时
        if self.current_wave < self.total_waves:
            time_to_next = max(0, self.wave_spawn_delay - self.wave_spawn_timer)
            if time_to_next > 0:
                seconds = time_to_next // 60
                next_text = small_font.render(f"下波: {seconds}s", True, (200, 200, 220))
                surface.blit(next_text, (info_x + info_w - 85, info_y + 35))

    def draw_minimap(self, surface, x, y, width, height) -> None:
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        theme_color = self.current_room.theme_color if self.current_room else (40, 40, 60)
        top_color = _blend_color(theme_color, 0.65)
        bottom_color = _blend_color(theme_color, 0.35)
        for row in range(height):
            ratio = row / max(1, height - 1)
            color = [int(top_color[i] * (1 - ratio) + bottom_color[i] * ratio) for i in range(3)]
            pygame.draw.line(bg, (*color, 220), (0, row), (width, row))
        surface.blit(bg, (x, y))
        pygame.draw.rect(surface, (90, 90, 130), (x, y, width, height), 2)
        if not self.current_room:
            return
        font = pygame.font.SysFont("simhei,arial", 20)
        small_font = pygame.font.SysFont("simhei,arial", 13)
        header_h = 32
        
        # 标题
        surface.blit(font.render("地图", True, (255, 255, 255)), (x + 10, y + 5))
        
        # 显示主题名称和进度（右上角小字）
        theme_name = self.get_theme_name()
        progress = self.get_map_progress()
        theme_text = small_font.render(f"{theme_name} ({progress})", True, (180, 180, 200))
        surface.blit(theme_text, (x + width - theme_text.get_width() - 8, y + 6))
        
        footer_h = 28
        content_h = height - header_h - footer_h
        focus_depth = self.current_room.depth
        candidate_depths = [focus_depth - 1, focus_depth, focus_depth + 1]
        visible_depths = [d for d in candidate_depths if 0 <= d <= FINAL_DEPTH]
        room_size = 22
        spacing_x = 36
        rows = max(1, len(visible_depths) - 1)
        spacing_y = content_h // rows if rows else 0
        for relative, depth in enumerate(visible_depths):
            depth_nodes = [r for r in self.rooms.values() if r.depth == depth]
            if not depth_nodes:
                continue
            node_center_y = y + header_h + (spacing_y * relative if rows else content_h // 2)
            node_y = int(node_center_y - room_size / 2)
            half_span = spacing_x * (len(depth_nodes) - 1) / 2
            center_x = x + width / 2
            for idx, node in enumerate(depth_nodes):
                node_center_x = center_x - half_span + idx * spacing_x
                node_rect = pygame.Rect(int(node_center_x - room_size / 2), node_y, room_size, room_size)
                self._draw_room_node(surface, node_rect, node)
                if depth < FINAL_DEPTH:
                    for conn_id in node.connections:
                        target = self.rooms.get(conn_id)
                        if target and target.depth == depth + 1 and target.depth in visible_depths:
                            target_nodes = [r for r in self.rooms.values() if r.depth == depth + 1]
                            if not target_nodes:
                                continue
                            try:
                                target_idx = target_nodes.index(target)
                            except ValueError:
                                continue
                            next_half_span = spacing_x * (len(target_nodes) - 1) / 2
                            target_center_x = center_x - next_half_span + target_idx * spacing_x
                            next_center_y = y + header_h + ((relative + 1) * spacing_y if rows else content_h // 2)
                            pygame.draw.line(
                                surface,
                                (70, 70, 100),
                                (int(node_center_x), int(node_center_y)),
                                (int(target_center_x), int(next_center_y)),
                                2,
                            )
        depth_text = font.render(f"层数 {self.current_room.depth + 1}/{len(ROOMS_PER_DEPTH)}", True, (225, 225, 225))
        surface.blit(depth_text, (x + 10, y + height - footer_h + 5))

    def draw_fullmap(self, surface) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        theme_color = self.current_room.theme_color if self.current_room else (30, 40, 70)
        overlay_color = _blend_color(theme_color, 0.4, base=(5, 5, 12))
        overlay.fill((*overlay_color, 235))
        surface.blit(overlay, (0, 0))
        font = pygame.font.SysFont("simhei,arial", 42)
        title = font.render("房间地图", True, (255, 255, 150))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 50)))
        
        # 显示主题名称和进度
        theme_font = pygame.font.SysFont("simhei,arial", 24)
        theme_name = self.get_theme_name()
        progress = self.get_map_progress()
        theme_text = theme_font.render(f"[ {theme_name} · {progress} ]", True, (150, 200, 255))
        surface.blit(theme_text, theme_text.get_rect(center=(WIDTH // 2, 88)))
        
        hint_font = pygame.font.SysFont("simhei,arial", 22)
        hint = hint_font.render("按 M 关闭地图 · 滚轮/± 缩放", True, (200, 200, 200))
        surface.blit(hint, hint.get_rect(center=(WIDTH // 2, 118)))
        map_area = pygame.Rect(80, 150, WIDTH - 160, HEIGHT - 260)
        base_scale = _auto_fullmap_scale(map_area, self.rooms)
        user_zoom = max(MAP_ZOOM_MIN, min(MAP_ZOOM_MAX, self.map_zoom))
        effective_zoom = base_scale * user_zoom
        room_size = max(28, min(100, int(BASE_ROOM_SIZE * effective_zoom)))
        spacing_x = max(room_size + 12, int(BASE_SPACING_X * effective_zoom))
        spacing_y = max(room_size + 8, int(BASE_SPACING_Y * effective_zoom))
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_room = None
        for depth in range(len(ROOMS_PER_DEPTH)):
            depth_nodes = [r for r in self.rooms.values() if r.depth == depth]
            for idx, node in enumerate(depth_nodes):
                half_span = spacing_x * (len(depth_nodes) - 1) / 2
                center_x = map_area.x + map_area.width / 2 - half_span + idx * spacing_x
                center_y = map_area.y + depth * spacing_y
                node_rect = pygame.Rect(int(center_x - room_size / 2), int(center_y - room_size / 2), room_size, room_size)
                hovered = node_rect.collidepoint(mouse_pos)
                if hovered:
                    self.hovered_room = node
                self._draw_room_node(surface, node_rect, node, hovered)
                for conn_id in node.connections:
                    target = self.rooms.get(conn_id)
                    if not target:
                        continue
                    target_nodes = [r for r in self.rooms.values() if r.depth == target.depth]
                    try:
                        target_idx = target_nodes.index(target)
                    except ValueError:
                        continue
                    target_half_span = spacing_x * (len(target_nodes) - 1) / 2
                    target_center_x = map_area.x + map_area.width / 2 - target_half_span + target_idx * spacing_x
                    target_center_y = map_area.y + target.depth * spacing_y
                    progress_line = node.visited and (target.visited or target.state == RoomState.CURRENT)
                    line_color = (120, 255, 200) if progress_line else (90, 90, 140)
                    line_width = 4 if progress_line else 2
                    if target.state == RoomState.AVAILABLE and not progress_line:
                        line_color = (120, 180, 255)
                        line_width = 3
                    pygame.draw.line(
                        surface,
                        line_color,
                        (int(center_x), int(center_y)),
                        (int(target_center_x), int(target_center_y)),
                        line_width,
                    )
        self._draw_legend(surface, WIDTH - 260, 150)
        if self.hovered_room:
            self._draw_room_tooltip(surface, self.hovered_room)
        if self.current_room:
            info_rect = pygame.Rect(80, HEIGHT - 80, WIDTH - 160, 60)
            info_surface = pygame.Surface((info_rect.width, info_rect.height), pygame.SRCALPHA)
            info_surface.fill((25, 35, 60, 210))
            surface.blit(info_surface, info_rect.topleft)
            pygame.draw.rect(surface, (130, 180, 255), info_rect, 2, border_radius=10)
            info_font = pygame.font.SysFont("simhei,arial", 22)
            current = self.current_room
            info_text = f"{current.act_name} · 层 {current.depth + 1}/{len(ROOMS_PER_DEPTH)}"
            mutator = current.mutator or "无变体"
            reward_hint = _format_reward_hint(current.reward_hint)
            surface.blit(info_font.render(info_text, True, (210, 230, 255)), (info_rect.x + 14, info_rect.y + 6))
            mutator_text = info_font.render(f"变体: {mutator}", True, (180, 200, 255))
            surface.blit(mutator_text, (info_rect.x + 14, info_rect.y + 30))
            reward_text = info_font.render(f"奖励: {reward_hint}", True, (170, 255, 200))
            reward_rect = reward_text.get_rect(midleft=(info_rect.centerx, info_rect.y + info_rect.height // 2))
            surface.blit(reward_text, reward_rect)
            zoom_text = info_font.render(f"缩放 {user_zoom:.1f}x", True, (200, 220, 255))
            surface.blit(zoom_text, (info_rect.right - 150, info_rect.y + 6))

    def _draw_legend(self, surface, x, y) -> None:
        panel = pygame.Rect(x, y, 230, 340)
        legend_surface = pygame.Surface(panel.size, pygame.SRCALPHA)
        legend_surface.fill((18, 24, 46, 230))
        surface.blit(legend_surface, panel.topleft)
        pygame.draw.rect(surface, (120, 150, 220), panel, 2, border_radius=12)
        title_font = pygame.font.SysFont("simhei,arial", 22)
        surface.blit(title_font.render("图例", True, (255, 255, 255)), (x + 14, y + 12))
        caption_font = pygame.font.SysFont("simhei,arial", 16)
        surface.blit(caption_font.render("房型 & 状态", True, (170, 190, 255)), (x + 14, y + 34))

        row_font = pygame.font.SysFont("simhei,arial", 17)
        for idx, key in enumerate(RoomType.ALL):
            name, icon, color = RoomType.DISPLAY[key]
            row_y = y + 60 + idx * 26
            circle_center = (x + 26, row_y + 12)
            pygame.draw.circle(surface, (35, 45, 70), circle_center, 13)
            pygame.draw.circle(surface, color, circle_center, 11)
            pygame.draw.circle(surface, (255, 255, 255), circle_center, 11, 2)
            icon_surface = _render_icon_cached(icon, 18)
            icon_rect = icon_surface.get_rect(center=circle_center)
            surface.blit(icon_surface, icon_rect)
            surface.blit(row_font.render(name, True, (215, 225, 245)), (x + 48, row_y + 2))

        pygame.draw.line(surface, (80, 100, 160), (x + 14, y + 230), (x + panel.width - 14, y + 230), 1)
        state_font = pygame.font.SysFont("simhei,arial", 16)
        state_styles = {
            RoomState.CURRENT: ((90, 90, 40), (255, 255, 150), "当前房间"),
            RoomState.CLEARED: ((40, 70, 50), (100, 180, 120), "已清理"),
            RoomState.AVAILABLE: ((50, 60, 90), (140, 200, 255), "可前往"),
            RoomState.LOCKED: ((30, 30, 40), (90, 90, 120), "未解锁"),
        }
        for idx, (state, (fill, border, label)) in enumerate(state_styles.items()):
            rect = pygame.Rect(x + 18, y + 245 + idx * 28, 28, 20)
            pygame.draw.rect(surface, fill, rect, border_radius=4)
            pygame.draw.rect(surface, border, rect, 2, border_radius=4)
            surface.blit(state_font.render(label, True, (200, 210, 230)), (rect.right + 8, rect.y + 2))

        path_y = y + panel.height - 60
        pygame.draw.line(surface, (115, 240, 200), (x + 20, path_y), (x + 90, path_y), 4)
        surface.blit(state_font.render("已探索路线", True, (190, 220, 210)), (x + 105, path_y - 10))
        pygame.draw.line(surface, (90, 90, 140), (x + 20, path_y + 24), (x + 90, path_y + 24), 2)
        surface.blit(state_font.render("未知连接", True, (160, 170, 200)), (x + 105, path_y + 14))

    def _draw_room_tooltip(self, surface, node: RoomNode) -> None:
        tooltip_w, tooltip_h = 320, 180
        mx, my = pygame.mouse.get_pos()
        tx = mx + 24 if mx + tooltip_w < WIDTH else mx - tooltip_w - 24
        ty = my + 24 if my + tooltip_h < HEIGHT else my - tooltip_h - 24
        rect = pygame.Rect(tx, ty, tooltip_w, tooltip_h)
        # 半透明背景
        tooltip_surf = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
        tooltip_surf.fill((25, 30, 50, 240))
        surface.blit(tooltip_surf, (tx, ty))
        pygame.draw.rect(surface, (150, 180, 255), rect, 3, border_radius=8)
        
        font = pygame.font.SysFont("simhei,arial", 20)
        small_font = pygame.font.SysFont("simhei,arial", 18)
        header = f"{node.act_name} · 层 {node.depth + 1}"
        surface.blit(font.render(header, True, node.color()), (tx + 12, ty + 10))
        surface.blit(font.render(f"类型: {RoomType.DISPLAY[node.room_type][0]}", True, (220, 220, 220)), (tx + 12, ty + 36))
        surface.blit(font.render(f"难度 {node.difficulty:.1f}x", True, (255, 160, 120)), (tx + 12, ty + 62))
        
        if node.mutator:
            surface.blit(small_font.render(f"变体: {node.mutator}", True, (200, 180, 255)), (tx + 12, ty + 88))
        
        # 显示具体奖励数值（从范围中取中间值）
        y_offset = ty + (114 if node.mutator else 90)
        reward_title = small_font.render("预期奖励:", True, (180, 255, 180))
        surface.blit(reward_title, (tx + 12, y_offset))
        y_offset += 24
        
        for key, value in node.reward_hint.items():
            label = REWARD_LABELS.get(key, key)
            if isinstance(value, (tuple, list)) and len(value) == 2:
                # 显示范围的平均值
                avg_value = (value[0] + value[1]) // 2
                reward_text = small_font.render(f"  • {label}: ~{avg_value}", True, (200, 255, 200))
            elif isinstance(value, (int, float)):
                reward_text = small_font.render(f"  • {label}: {int(value)}", True, (200, 255, 200))
            elif isinstance(value, bool):
                reward_text = small_font.render(f"  • {label}", True, (200, 255, 200))
            else:
                reward_text = small_font.render(f"  • {label}", True, (200, 255, 200))
            surface.blit(reward_text, (tx + 12, y_offset))
            y_offset += 22

    def draw_room_selection_ui(self, surface) -> None:
        if not self.show_completion_ui or not self.current_room:
            return
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        title_font = pygame.font.SysFont("simhei,arial", 48)
        hint_font = pygame.font.SysFont("simhei,arial", 24)
        room_font = pygame.font.SysFont("simhei,arial", 28)
        desc_font = pygame.font.SysFont("simhei,arial", 20)
        
        # 显示当前房间类型的特殊标题
        room_type = self.current_room.room_type
        if room_type == RoomType.TREASURE:
            title = title_font.render("宝箱房间完成！", True, (0, 255, 200))
        elif room_type == RoomType.REST:
            title = title_font.render("休息完毕！", True, (110, 255, 110))
        elif room_type == RoomType.EVENT:
            title = title_font.render("事件结束！", True, (200, 100, 255))
        else:
            title = title_font.render("房间完成！", True, (110, 255, 110))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 110)))
        
        # 先检查是否是Boss房间且需要切换地图
        is_boss_completed = self.current_room.room_type == RoomType.BOSS and not self.current_room.connections
        
        # 只有非Boss房间或有连接的Boss房间才尝试填充下一房间列表
        if not is_boss_completed and not self.available_next_rooms:
            for room_id in self.current_room.connections:
                node = self.rooms.get(room_id)
                if node:
                    if node.state == RoomState.LOCKED:
                        node.state = RoomState.AVAILABLE
                    self.available_next_rooms.append(node)
        
        # 显示提示文字
        if self.available_next_rooms:
            hint = hint_font.render("选择下一个房间", True, (220, 220, 220))
            surface.blit(hint, hint.get_rect(center=(WIDTH // 2, 160)))
        
        if not self.available_next_rooms:
            # 检查是否完成了当前地图
            if self.current_room.room_type == RoomType.BOSS:
                if self.is_final_map():
                    # 最后一张地图通关
                    victory = title_font.render("恭喜全部通关！", True, (255, 220, 120))
                    surface.blit(victory, victory.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
                    subtitle = hint_font.render("你已征服所有地图！", True, (200, 255, 200))
                    surface.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
                else:
                    # 当前地图通关，准备进入下一张
                    next_theme = MAP_THEMES.get(self.map_sequence[self.current_map_index + 1], {}).get("name", "未知")
                    victory = title_font.render(f"{self.get_theme_name()} 通关！", True, (255, 220, 120))
                    surface.blit(victory, victory.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
                    progress = hint_font.render(f"地图进度: {self.get_map_progress()}", True, (200, 200, 255))
                    surface.blit(progress, progress.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10)))
                    next_map = hint_font.render(f"下一张地图: {next_theme}", True, (150, 255, 200))
                    surface.blit(next_map, next_map.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))
                    continue_hint = desc_font.render("按 Enter 继续冒险", True, (255, 255, 150))
                    surface.blit(continue_hint, continue_hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80)))
            else:
                victory = title_font.render("恭喜通关！", True, (255, 220, 120))
                surface.blit(victory, victory.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            return
        
        # 根据房间数量调整卡片大小和字体
        num_rooms = len(self.available_next_rooms)
        if num_rooms <= 3:
            card_w, card_h, gap = 280, 360, 40
            detail_font_size = 18
        elif num_rooms == 4:
            card_w, card_h, gap = 240, 340, 30
            detail_font_size = 17
        else:  # 5个或更多
            card_w, card_h, gap = 200, 320, 25
            detail_font_size = 16
        
        # 根据卡片大小创建合适的字体
        detail_font = pygame.font.SysFont("simhei,arial", detail_font_size)
        text_max_width = card_w - 20  # 左右各留10px边距
        
        total = num_rooms * card_w + (num_rooms - 1) * gap
        start_x = (WIDTH - total) // 2
        card_y = 210
        mouse_pos = pygame.mouse.get_pos()
        for idx, node in enumerate(self.available_next_rooms):
            card_x = start_x + idx * (card_w + gap)
            rect = pygame.Rect(card_x, card_y, card_w, card_h)
            hovered = rect.collidepoint(mouse_pos)
            selected = idx == self.selected_next_room
            bg_color = (60, 60, 80) if selected or hovered else (35, 35, 55)
            pygame.draw.rect(surface, bg_color, rect, border_radius=12)
            border = (255, 255, 130) if selected else ((200, 200, 255) if hovered else (90, 90, 140))
            pygame.draw.rect(surface, border, rect, 3 if hovered else 2, border_radius=12)
            icon_circle = pygame.Surface((110, 110), pygame.SRCALPHA)
            pygame.draw.circle(icon_circle, node.color(), (55, 55), 54)
            pygame.draw.circle(icon_circle, (255, 255, 255), (55, 55), 54, 3)
            surface.blit(icon_circle, (card_x + card_w // 2 - 55, card_y + 30))
            icon = _render_icon_cached(node.icon(), 42)
            surface.blit(icon, icon.get_rect(center=(card_x + card_w // 2, card_y + 85)))
            name_text = room_font.render(RoomType.DISPLAY[node.room_type][0], True, node.color())
            surface.blit(name_text, name_text.get_rect(center=(card_x + card_w // 2, card_y + 150)))
            y_offset = card_y + 190
            detail_lines = [
                f"难度 {node.difficulty:.1f}x",
                f"奖励: {_format_reward_hint(node.reward_hint)}",
            ]
            if node.mutator:
                detail_lines.append(f"变体: {node.mutator}")
            for line in detail_lines:
                # 截断过长的文字
                truncated_line = _truncate_text(detail_font, line, text_max_width)
                line_text = detail_font.render(truncated_line, True, (210, 210, 220))
                surface.blit(line_text, line_text.get_rect(center=(card_x + card_w // 2, y_offset)))
                y_offset += 28 if num_rooms >= 5 else 30
            if selected:
                select_hint = hint_font.render("Enter 确认", True, (255, 255, 150))
                surface.blit(select_hint, select_hint.get_rect(center=(card_x + card_w // 2, card_y + card_h - 30)))
        bottom_hint = desc_font.render("← → 选择 | Enter 确认 | M 地图", True, (180, 180, 200))
        surface.blit(bottom_hint, bottom_hint.get_rect(center=(WIDTH // 2, HEIGHT - 60)))
    
    def draw_shop_ui(self, surface: pygame.Surface) -> None:
        """绘制商店UI"""
        if not self.show_shop_ui:
            return
        
        # 半透明遮罩
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        title_font = pygame.font.SysFont("simhei,arial", 48)
        hint_font = pygame.font.SysFont("simhei,arial", 24)
        item_font = pygame.font.SysFont("simhei,arial", 28)
        desc_font = pygame.font.SysFont("simhei,arial", 20)
        
        # 标题
        title = title_font.render("商店", True, (255, 215, 0))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 80)))
        
        # 显示当前积分
        currency_text = hint_font.render(f"当前积分: {int(self.currency)}", True, (255, 255, 150))
        surface.blit(currency_text, currency_text.get_rect(center=(WIDTH // 2, 140)))
        
        if not self.shop_items:
            # 售罄特效：绘制一个大的"售罄"标志
            soldout_box = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
            box_surf = pygame.Surface((400, 200), pygame.SRCALPHA)
            box_surf.fill((60, 40, 40, 220))
            surface.blit(box_surf, soldout_box.topleft)
            pygame.draw.rect(surface, (200, 100, 100), soldout_box, 3, border_radius=15)
            
            soldout_font = pygame.font.SysFont("simhei,arial", 56, bold=True)
            no_items = soldout_font.render("商店售罄", True, (255, 180, 180))
            surface.blit(no_items, no_items.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
            
            thanks_text = hint_font.render("感谢惠顾！", True, (200, 200, 220))
            surface.blit(thanks_text, thanks_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))
            
            exit_hint = desc_font.render("按 ESC 离开商店", True, (255, 255, 150))
            surface.blit(exit_hint, exit_hint.get_rect(center=(WIDTH // 2, HEIGHT - 60)))
            return
        
        # 绘制商品卡片
        card_w, card_h, gap = 260, 280, 30
        total_width = len(self.shop_items) * card_w + (len(self.shop_items) - 1) * gap
        start_x = (WIDTH - total_width) // 2
        card_y = 200
        
        mouse_pos = pygame.mouse.get_pos()
        
        for idx, item in enumerate(self.shop_items):
            card_x = start_x + idx * (card_w + gap)
            rect = pygame.Rect(card_x, card_y, card_w, card_h)
            hovered = rect.collidepoint(mouse_pos)
            selected = idx == self.shop_selected
            
            # 检查是否买得起
            can_afford = self.currency >= item["price"]
            
            # 背景色
            if not can_afford:
                bg_color = (40, 40, 50)
            elif selected or hovered:
                bg_color = (70, 70, 90)
            else:
                bg_color = (50, 50, 70)
            
            pygame.draw.rect(surface, bg_color, rect, border_radius=10)
            
            # 边框
            if selected:
                border_color = (255, 215, 0) if can_afford else (150, 150, 150)
            elif hovered:
                border_color = (200, 200, 255) if can_afford else (120, 120, 140)
            else:
                border_color = (100, 100, 140) if can_afford else (80, 80, 90)
            
            pygame.draw.rect(surface, border_color, rect, 3 if (selected or hovered) else 2, border_radius=10)
            
            # 物品名称
            name_color = (255, 255, 255) if can_afford else (120, 120, 120)
            name_text = item_font.render(item["name"], True, name_color)
            surface.blit(name_text, name_text.get_rect(center=(card_x + card_w // 2, card_y + 40)))
            
            # 物品描述
            desc_color = (200, 200, 200) if can_afford else (100, 100, 100)
            desc_text = desc_font.render(item["desc"], True, desc_color)
            surface.blit(desc_text, desc_text.get_rect(center=(card_x + card_w // 2, card_y + 100)))
            
            # 价格
            price_color = (255, 215, 0) if can_afford else (150, 100, 100)
            price_text = hint_font.render(f"{item['price']} 积分", True, price_color)
            surface.blit(price_text, price_text.get_rect(center=(card_x + card_w // 2, card_y + 160)))
            
            # 购买提示
            if selected and can_afford:
                buy_hint = desc_font.render("Enter 购买", True, (150, 255, 150))
                surface.blit(buy_hint, buy_hint.get_rect(center=(card_x + card_w // 2, card_y + card_h - 30)))
            elif selected and not can_afford:
                buy_hint = desc_font.render("积分不足", True, (255, 100, 100))
                surface.blit(buy_hint, buy_hint.get_rect(center=(card_x + card_w // 2, card_y + card_h - 30)))
        
        # 底部提示
        bottom_hint = desc_font.render("← → 选择 | Enter 购买 | ESC 离开", True, (180, 180, 200))
        surface.blit(bottom_hint, bottom_hint.get_rect(center=(WIDTH // 2, HEIGHT - 60)))
