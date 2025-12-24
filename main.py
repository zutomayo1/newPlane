import pygame
import os
import sys
import math
import random
import json
import traceback
import textwrap
from utils import *
from systems import *
from sprites import *
from customization import customization_manager, PAINT_THEMES, BULLET_THEMES, EnhancedTrailEffect
from enemies import enemy_factory, init_enemy_system, build_enemy_preview_surface
from roguelite import ItemManager, AchievementManager
from room_system import RoomManager, RoomType, RoomState
from music_catalog import resolve_music_metadata, MUSIC_FILTER_CHOICES

# ==============================================================================
#   全局初始化
# ==============================================================================
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("霓虹深空：无限进化 (最终完美版)")
clock = pygame.time.Clock()

# 加载数据
try:
    load_arsenal()
    leaderboard_data = load_leaderboard()
except Exception as e:
    log_error(f"数据加载警告: {e}")
    leaderboard_data = []

# 初始化敌人系统
try:
    init_enemy_system()
    enemy_factory.load_from_json('enemy_types.json')
except Exception as e:
    log_error(f"敌人系统初始化失败: {e}")

# 加载设置并初始化背景管理器
game_settings = load_settings()
bg_manager = BackgroundManager(style=game_settings.get("background_style", "classic"))
# sound_mgr 来自 utils.py
# 应用音量设置
sound_mgr.set_master_volume(game_settings.get("master_volume", 1.0))
sound_mgr.set_music_volume(game_settings.get("music_volume", 0.5))
sound_mgr.set_sfx_volume(game_settings.get("sfx_volume", 0.8))
# 播放主菜单音乐
MENU_THEME_PRESETS = {
    "menu_home": {"track": "cinematic", "intensity": 0.35},
    "mode_select": {"track": "epic", "intensity": 0.55},
    "audio_hub": {"track": "calm", "intensity": 0.4},
    "select_plane": {"track": "mystery", "intensity": 0.48},
}

current_menu_theme = None


def apply_menu_theme(theme_key, force=False):
    global current_menu_theme
    preset = MENU_THEME_PRESETS.get(theme_key, MENU_THEME_PRESETS["menu_home"])
    if current_menu_theme == theme_key and not force:
        return
    music_director.set_state(
        "menu",
        intensity=preset.get("intensity", 0.4),
        override_track=preset.get("track"),
        layers_enabled=True,
    )
    current_menu_theme = theme_key


apply_menu_theme("menu_home", force=True)

# ==============================================================================
#   UI 布局常量
# ==============================================================================
# 武器库布局常量
ARSENAL_UI = {
    'list_area': pygame.Rect(30, 70, 340, HEIGHT - 120),
    'slot_0': pygame.Rect(395, 120, 280, 95),
    'slot_1': pygame.Rect(395, 235, 280, 95),
    'slot_2': pygame.Rect(395, 350, 280, 95),
    'btn_research_normal': pygame.Rect(395, HEIGHT - 115, 135, 55),
    'btn_research_elite': pygame.Rect(540, HEIGHT - 115, 135, 55),
    'detail_area': pygame.Rect(WIDTH - 380, 70, 350, HEIGHT - 120),
    'btn_upgrade': pygame.Rect(WIDTH - 330, HEIGHT - 135, 250, 55),
    'btn_back': pygame.Rect(30, HEIGHT - 55, 110, 45)
}

# 机密档案布局常量
CODEX_UI = {
    'tab_plane': pygame.Rect(50, 90, 150, 40),
    'tab_boss': pygame.Rect(200, 90, 150, 40),
    'list_view': pygame.Rect(50, 140, 300, HEIGHT - 220), 
    'detail_area': pygame.Rect(370, 140, WIDTH - 420, HEIGHT - 220),
    'btn_back': pygame.Rect(WIDTH - 120, HEIGHT - 60, 100, 40)
}

# ==============================================================================
#   全局游戏状态
# ==============================================================================
game_state = "menu"
is_paused = False
frozen_screen = None
tab_paused = False  # 标记是否是TAB暂停
levelup_paused = False  # 标记是否为升级UI暂停
game_over_timer = 0
final_score = 0
player_name = ""
screen_shake_offset = (0, 0)

# 实体
player = None
boss = None
from systems import BossManager
boss_manager = BossManager()
item_manager = None  # 物品掉落管理器
room_manager = None  # 房间系统管理器
boss_music_active = False
boss_challenge_music_active = False

# 数值
score = 0
# boss_timer and scheduling managed by BossManager
global_time_freeze = 0
wave = 0  # 波数

# ============================================================================
# 普通模式敌人生成系统
# ============================================================================
normal_spawn_timer = 0
normal_spawn_cycle = []
wave_event_timer = 0          # 波次事件冷却计时
wave_event_active = False     # 波次事件进行中
wave_warning_timer = 0        # 波次预警计时
current_stage = 1             # 当前难度阶段 (1-5)
last_kill_timer = 0           # 上次击杀后经过的帧数
no_damage_timer = 0           # 无伤计时
recent_enemy_types = []       # 最近生成的敌人类型（用于反单调）

# 敌人分级体系
ENEMY_TIERS = {
    # T1 轻型 (威胁值 5-8)
    "T1": {
        "enemies": ["wisp", "plague_drone", "void_hunter"],
        "threat": (5, 8),
        "tags": ["swarm", "flanker"],
    },
    # T2 标准 (威胁值 10-15)
    "T2": {
        "enemies": ["bulwark", "orbiter", "skeletal_interceptor", "phantasmal_splitter"],
        "threat": (10, 15),
        "tags": ["tank", "ranged"],
    },
    # T3 精英 (威胁值 18-25)
    "T3": {
        "enemies": ["armored_centurion", "frost_webber", "storm_javelin", "rail_shredder"],
        "threat": (18, 25),
        "tags": ["tank", "support", "ranged"],
    },
    # T4 高威胁 (威胁值 28-40)
    "T4": {
        "enemies": ["astra_fragger", "ember_siege", "cryo_lancer", "arc_overseer", "ion_veil", "resonance_breaker", "lumen_shade"],
        "threat": (28, 40),
        "tags": ["ranged", "support"],
    },
}

# 阶段解锁配置
STAGE_CONFIG = {
    1: {"score": 0,    "tiers": ["T1"], "max_enemies": 6,  "spawn_sides": False, "spawn_bottom": False},
    2: {"score": 500,  "tiers": ["T1", "T2"], "max_enemies": 8,  "spawn_sides": False, "spawn_bottom": False},
    3: {"score": 1500, "tiers": ["T1", "T2", "T3"], "max_enemies": 10, "spawn_sides": True,  "spawn_bottom": False},
    4: {"score": 3000, "tiers": ["T1", "T2", "T3", "T4"], "max_enemies": 12, "spawn_sides": True,  "spawn_bottom": True},
    5: {"score": 6000, "tiers": ["T1", "T2", "T3", "T4"], "max_enemies": 14, "spawn_sides": True,  "spawn_bottom": True},
}

# 波次事件模板
WAVE_TEMPLATES = [
    {"name": "swarm_rush", "min_score": 500, "composition": [("T1", 6, 8)], "spawn_mode": "top_fan", "warning": "蜂群来袭!"},
    {"name": "pincer_attack", "min_score": 1200, "composition": [("T2", 3, 4)], "spawn_mode": "sides", "warning": "两侧夹击!"},
    {"name": "heavy_push", "min_score": 2000, "composition": [("T3", 2, 2), ("T1", 3, 4)], "spawn_mode": "top_slow", "warning": "重装推进!"},
    {"name": "sniper_surround", "min_score": 3000, "composition": [("T3", 3, 4)], "spawn_mode": "corners", "warning": "精准打击!"},
    {"name": "full_assault", "min_score": 5000, "composition": [("T2", 2, 3), ("T3", 2, 2), ("T4", 1, 2)], "spawn_mode": "all", "warning": "全面进攻!"},
]

# 选人
selected_plane = "striker"
current_plane_idx = 0
plane_keys = list(PLANES.keys())

# --- UI 状态 ---
# 武器库 (新增滚动变量)
arsenal_scroll_y = 0 
arsenal_selected_weapon_idx = -1
arsenal_msg = ""
arsenal_msg_timer = 0
arsenal_dragging_scrollbar = False  # 滚动条拖动状态
arsenal_drag_start_y = 0
arsenal_drag_start_scroll = 0

# 飞机选择界面滚动
plane_select_scroll_y = 0
plane_select_dragging_scrollbar = False  # 滚动条拖动状态
plane_select_drag_start_y = 0
plane_select_drag_start_scroll = 0

# 涂装系统
customization_selected_plane = None

# 设置界面
settings_dragging = None  # 当前拖动的滑块 ('master', 'music', 'sfx')
settings_saved_msg = ""   # 保存提示消息
settings_saved_timer = 0  # 提示消息计时器
customization_scroll_y = 0
customization_plane_scroll_y = 0
customization_msg = ""
customization_msg_timer = 0
customization_tab = 0  # 0:全部, 1:经典, 2:霓虹, 3:史诗, 4:特效, 5:传说
customization_dragging_scrollbar = False  # 涂装列表滚动条拖动
customization_drag_start_y = 0
customization_drag_start_scroll = 0
customization_plane_dragging_scrollbar = False  # 机体列表滚动条拖动
customization_plane_drag_start_y = 0
customization_plane_drag_start_scroll = 0

# 成就菜单 - 豪华版
achievement_page = 0
achievement_category = "all"  # all, combat, boss, survival, plane, roguelike, efficiency, milestone, secret
achievement_selected = None   # 当前选中的成就ID
achievement_scroll_y = 0      # 滚动偏移
achievement_dragging_scrollbar = False  # 是否正在拖动滚动条
achievement_drag_start_y = 0  # 拖动起始位置
achievement_drag_start_scroll = 0  # 拖动起始滚动位置

# 全局字体缓存（避免每帧创建字体，显著提升性能）
_font_cache = {}

def get_cached_font(name, size):
    """获取缓存的字体对象（全局通用）"""
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(name, size)
    return _font_cache[key]

# 成就界面缓存（保留向后兼容）
_ach_fonts = _font_cache  # 共享同一缓存
_ach_mgr_cache = None

def get_ach_font(name, size):
    """获取缓存的字体对象（向后兼容）"""
    return get_cached_font(name, size)

def get_cached_achievement_mgr():
    """获取缓存的成就管理器"""
    global _ach_mgr_cache
    import os
    if _ach_mgr_cache is None and os.path.exists("achievements.json"):
        _ach_mgr_cache = AchievementManager()
        _ach_mgr_cache.load_from_file("achievements.json")
    return _ach_mgr_cache

# 成就通知队列
achievement_notifications = []  # [(achievement_obj, timer), ...]

# 【新】协同提示队列
synergy_notifications = []  # [(synergy_data, timer, triggered_time), ...]

# 【新】协同combo提示队列
synergy_combo_hints = []  # [(hint_text, timer, color), ...]

# 图鉴
gallery_page = 0
gallery_tab = 0 # 0:All, 1-6:Rarity (1★-6★)
gallery_hover_card = None  # 悬停的卡牌ID，用于显示详细Tooltip

# 档案
codex_tab = 0 # 0:Plane, 1:Boss, 2:Enemy
codex_idx = 0
codex_scroll_y = 0 
codex_dragging_scrollbar = False  # 图鉴滚动条拖动
codex_drag_start_y = 0
codex_drag_start_scroll = 0

# 涂装系统
customization_scroll_y = 0
customization_plane_scroll_y = 0  # 飞机列表滚动
customization_selected_plane = None  # 当前选中的飞机ID
customization_msg = ""
customization_msg_timer = 0
customization_tab = 0
customization_mode = "plane"  # "plane" 或 "wingman"
customization_selected_wingman = 0  # 当前选中的僚机槽位 (0-3)
wingman_theme_filter = None  # 僚机涂装筛选器 (None=全部, plane_id=按机体筛选)

# 背景设置
background_settings_page = 0  # 当前页码
background_settings_selected = 0  # 当前选中的背景索引

# 音乐馆
music_library_all_tracks = []
music_library_tracks = []
music_library_scroll_index = 0
music_library_selected = 0
music_library_now_playing = None
music_library_status_msg = ""
music_library_status_timer = 0
music_library_filter = "all"
music_library_sort_mode = "default"
music_library_search_query = ""
music_library_search_active = False
music_library_dragging_scrollbar = False  # 滚动条拖动状态
music_library_drag_start_y = 0
music_library_drag_start_scroll = 0

# 音效实验室
sound_lab_all_tracks = []
sound_lab_tracks = []
sound_lab_scroll_index = 0
sound_lab_selected = 0
sound_lab_now_playing = None
sound_lab_filter = "all"
sound_lab_dragging_scrollbar = False  # 滚动条拖动状态
sound_lab_drag_start_y = 0
sound_lab_drag_start_scroll = 0

# 音乐主题 & 动态音乐
dynamic_music_state = {"state": None, "intensity": 0.0}
dynamic_music_boss_phase = 0

# 暂停菜单状态
pause_menu_selected = 0  # 0: 继续, 1: 重新开始, 2: 退出战斗

# 排行榜系统
leaderboard_mode = "normal"  # "normal", "roguelike", "boss_challenge"
leaderboard_sort_by = "score"  # "score", "kills", "time", "wave"
leaderboard_scroll_y = 0
leaderboard_stats_tab = 0  # 0: 排行榜, 1: 个人统计
leaderboard_dragging_scrollbar = False  # 排行榜滚动条拖动
leaderboard_drag_start_y = 0
leaderboard_drag_start_scroll = 0

# 排行榜UI缓存（性能优化）
_leaderboard_cache = {
    "bg_surface": None,        # 背景缓存（六边形网格+星空）
    "bg_size": (0, 0),         # 缓存时的屏幕尺寸
    "fonts": {},               # 字体缓存
    "gradient_surfaces": {},   # 渐变Surface缓存
    "last_update": 0,          # 上次动态更新时间
}

def _get_lb_font(name, size):
    """获取缓存的字体"""
    key = (name, size)
    if key not in _leaderboard_cache["fonts"]:
        _leaderboard_cache["fonts"][key] = pygame.font.SysFont(name, size)
    return _leaderboard_cache["fonts"][key]

def _get_lb_gradient(key, width, height, colors, alpha_range=(255, 0)):
    """获取缓存的渐变Surface"""
    cache_key = (key, width, height)
    if cache_key not in _leaderboard_cache["gradient_surfaces"]:
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        # 处理单色或双色情况
        color1 = colors[0]
        color2 = colors[1] if len(colors) > 1 else colors[0]
        for y in range(height):
            ratio = y / height if height > 0 else 0
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            alpha = int(alpha_range[0] * (1 - ratio) + alpha_range[1] * ratio)
            pygame.draw.line(surf, (r, g, b, alpha), (0, y), (width, y))
        _leaderboard_cache["gradient_surfaces"][cache_key] = surf
    return _leaderboard_cache["gradient_surfaces"][cache_key]

def _get_lb_background():
    """获取缓存的背景（六边形网格）"""
    if (_leaderboard_cache["bg_surface"] is None or 
        _leaderboard_cache["bg_size"] != (WIDTH, HEIGHT)):
        # 创建静态背景
        bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        bg.fill((5, 8, 15))
        
        # 六边形网格
        hex_alpha = 18
        hex_color = (hex_alpha, int(hex_alpha * 1.5), hex_alpha // 2)
        hex_size = 60
        for row in range(-1, HEIGHT // hex_size + 2):
            for col in range(-1, WIDTH // hex_size + 2):
                cx = col * hex_size * 1.5 + (row % 2) * hex_size * 0.75
                cy = row * hex_size * 0.866
                points = []
                for angle in range(6):
                    px = cx + hex_size * 0.4 * math.cos(math.radians(60 * angle + 30))
                    py = cy + hex_size * 0.4 * math.sin(math.radians(60 * angle + 30))
                    points.append((px, py))
                if len(points) >= 3:
                    pygame.draw.polygon(bg, hex_color, points, 1)
        
        _leaderboard_cache["bg_surface"] = bg
        _leaderboard_cache["bg_size"] = (WIDTH, HEIGHT)
    return _leaderboard_cache["bg_surface"]

def _reload_leaderboard_data():
    """重新加载排行榜数据"""
    global leaderboard_data, leaderboard_mode, leaderboard_sort_by, leaderboard_stats_tab
    leaderboard_data = load_leaderboard()
    leaderboard_mode = "normal"
    leaderboard_sort_by = "score"
    leaderboard_stats_tab = 0

# 游戏统计（每局记录）
game_stats = {
    "kills": 0,
    "boss_kills": 0,
    "start_time": 0,
    "survival_time": 0,
}

# 房间系统状态
show_full_map = False  # 是否显示完整地图
map_paused = False  # 标记是否是M键地图暂停
room_completion_paused = False  # 房间完成后暂停锁

# ==============================================================================
# 主菜单选择
main_menu_selected = 0  # 用于键盘导航
audio_hub_selected = 0  # 音乐入口界面的选项索引


def save_achievements_to_file(filename="achievements.json"):
    """辅助函数：在有玩家和成就管理时保存成就数据"""
    try:
        if player and hasattr(player, 'achievement_manager'):
            player.achievement_manager.save_to_file(filename)
    except Exception as e:
        log_error(f"保存成就失败: {e}")

# ==============================================================================
#   肉鸽系统相关全局变量
# ==============================================================================
upgrade_options = []  # 升级选择的 3 个选项 [buff_id, ...]
upgrade_selected = 0  # 当前选中的升级索引 (0/1/2)
levelup_ready = False  # 是否显示升级选择 UI
frozen_screen = None  # 升级时冻结的游戏画面

# ==============================================================================
#   Boss挑战模式相关全局变量
# ==============================================================================
# ===============================================================================
#   游戏模式相关全局变量
# ===============================================================================
# 游戏模式: "normal" = 普通模式（波次敌人）, "roguelike" = 房间模式
game_mode = "normal"  
mode_select_selected = 0  # 模式选择界面的键盘选中索引 (0=普通, 1=房间, 2=Boss挑战)

# Boss挑战模式相关全局变量
# ===============================================================================
boss_challenge_selected = 0
boss_challenge_order = []
boss_challenge_current = 0
boss_challenge_active = False
boss_challenge_swap_timer = 0  # 换位动画计时器
boss_challenge_pulse_timer = 0  # 脉冲效果计时器
boss_challenge_scroll_offset = 0  # 列表滚动偏移
boss_challenge_key_repeat = {"up": 0, "down": 0, "left": 0, "right": 0}  # 键盘连按计时
boss_challenge_enabled = {}  # Boss启用状态字典 {boss_key: True/False}
boss_challenge_preset = 0  # 当前预设模式 (0=自定义, 1=快速战3, 2=标准战5, 3=持久战10, 4=全Boss战)

# 属性面板卡牌列表滚动
stats_panel_card_scroll = 0  # 卡牌列表滚动偏移（0表示顶部）

# ==============================================================================
#   辅助函数
# ==============================================================================

def safe_call_draw(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception:
        arg_types = tuple(type(a).__name__ for a in args)
        try:
            log_error(f"{fn.__name__} draw error: arg types={arg_types}, kwargs_keys={list(kwargs.keys())}")
        except Exception:
            log_error(f"{fn.__name__} draw error: (failed to log arg details)")
        log_error(traceback.format_exc())
        return None

def draw_game_hud():
    """Backward-compatible alias for draw_top_hud, protected by error handling."""
    safe_call_draw(draw_top_hud)

def should_spawn_particle():
    """根据粒子质量设置决定是否生成粒子"""
    quality = game_settings.get("particle_quality", "high")
    if quality == "high":
        return True
    elif quality == "medium":
        return random.random() < 0.5  # 50%概率
    else:  # low
        return random.random() < 0.2  # 20%概率

def create_explosion(pos, color, count=10):
    """生成爆炸粒子效果"""
    quality = game_settings.get("particle_quality", "high")
    if quality == "medium":
        count = count // 2
    elif quality == "low":
        count = max(2, count // 5)
    
    for _ in range(count):
        if should_spawn_particle():
            Particle(pos, color, mode="spark")

def create_shockwave(pos, color, count=10):
    """生成冲击波效果"""
    quality = game_settings.get("particle_quality", "high")
    if quality == "medium":
        count = count // 2
    elif quality == "low":
        count = max(1, count // 5)
    
    for _ in range(count):
        if should_spawn_particle():
            Particle(pos, color, mode="shockwave")

def draw_bullet_preview(surface, theme, x, y, size=60, plane_id=None):
    """绘制子弹涂装预览 - 已模块化到 utils/bullets/"""
    from utils.bullets import draw_bullet_preview as _draw_bullet_preview
    _draw_bullet_preview(surface, theme, x, y, size, plane_id)


def activate_background_music(style_key=None):
    """根据背景风格切换探索阶段BGM"""
    style = style_key or bg_manager.current_style
    config = BackgroundManager.BG_STYLES.get(style, {})
    track = config.get("bgm", "normal")
    element_type = config.get("element_type", "classic")
    intensity = BackgroundManager.resolve_bgm_intensity(element_type)
    music_director.set_state("explore", intensity=intensity, override_track=track)


def deactivate_boss_music():
    """关闭Boss音乐图层并回到上一层级"""
    global boss_music_active
    if boss_music_active:
        music_director.pop_state()
        boss_music_active = False


def deactivate_boss_challenge_music():
    """关闭Boss挑战音乐状态（自动先关闭Boss音乐）"""
    global boss_challenge_music_active
    deactivate_boss_music()
    if boss_challenge_music_active:
        music_director.pop_state()
        boss_challenge_music_active = False


MUSIC_LIBRARY_ITEM_HEIGHT = 64

MUSIC_FILTER_OPTIONS = MUSIC_FILTER_CHOICES

MUSIC_SORT_OPTIONS = [
    ("default", "默认"),
    ("name", "名称"),
    ("bpm", "BPM"),
    ("mood", "情绪"),
]

MUSIC_SEARCH_MAX_LEN = 48
SOUND_LAB_FILTERS = [
    ("all", "全部"),
    ("weapon", "武器"),
    ("combat", "战斗"),
    ("system", "系统"),
    ("action", "动作"),
    ("effect", "特效"),
    ("support", "支援"),
]

SFX_CATEGORY_CODES = {
    "武器": "weapon",
    "战斗": "combat",
    "系统": "system",
    "动作": "action",
    "特效": "effect",
    "支援": "support",
    "终极": "combat",
}

def update_dynamic_game_music():
    global dynamic_music_state, dynamic_music_boss_phase
    if game_state not in ("game", "boss_challenge_play"):
        if dynamic_music_state["state"] is not None:
            dynamic_music_state = {"state": None, "intensity": 0.0}
        dynamic_music_boss_phase = 0
        return
    target_state = "boss" if boss else "combat"
    base_intensity = 0.45 + min(0.35, wave * 0.02)
    if player and getattr(player, "max_hp", 0):
        hp_ratio = max(0.0, min(1.0, player.hp / player.max_hp))
        if hp_ratio < 0.35:
            base_intensity += 0.12
        elif hp_ratio < 0.6:
            base_intensity += 0.05
    if boss and hasattr(boss, "phase"):
        try:
            phase = int(getattr(boss, "phase", 1) or 1)
        except Exception:
            phase = 1
        if phase >= 2:
            base_intensity += 0.1
        if phase > dynamic_music_boss_phase:
            # scheme E: phase transition stinger (only once per phase)
            music_director.pause_for_stinger(
                "stinger_boss_phase",
                resume_state=target_state,
                resume_intensity=0.9,
                silence_ms=900,
            )
            dynamic_music_boss_phase = phase
    else:
        dynamic_music_boss_phase = 0
    intensity = max(0.3, min(0.95, base_intensity))
    state_changed = dynamic_music_state["state"] != target_state
    intensity_changed = abs(dynamic_music_state["intensity"] - intensity) > 0.05
    if state_changed or intensity_changed:
        music_director.set_state(target_state, intensity=intensity, layers_enabled=True)
        dynamic_music_state = {"state": target_state, "intensity": intensity}


def _format_music_track_name(track_id):
    if not track_id:
        return "未知曲目"
    parts = track_id.split("_")
    display_parts = []
    for part in parts:
        if not part:
            continue
        if len(part) <= 3:
            display_parts.append(part.upper())
        else:
            display_parts.append(part.capitalize())
    return " ".join(display_parts) if display_parts else track_id.upper()


def _truncate_music_text(text, limit=36):
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit - 1] + "…"


def _wrap_music_sources(text, limit=18, max_lines=4):
    if not text:
        return ["未绑定场景"]
    lines = textwrap.wrap(text, width=limit, break_long_words=True, break_on_hyphens=False)
    if not lines:
        lines = [text[:limit]]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        if not lines[-1].endswith("…"):
            lines[-1] = lines[-1][:-1] + "…"
    return lines


def _collect_music_track_sources():
    sources = {}
    try:
        for style, cfg in BackgroundManager.BG_STYLES.items():
            track = cfg.get("bgm")
            if not track:
                continue
            sources.setdefault(track, set()).add(cfg.get("name", style))
    except Exception as exc:
        log_error(f"收集音乐来源失败: {exc}")
    sources.setdefault("boss", set()).add("Boss战斗主题")
    sources.setdefault("intense", set()).add("紧张战斗段")
    sources.setdefault("epic", set()).add("史诗事件")
    sources.setdefault("cinematic", set()).add("主菜单")
    return {k: sorted(v) for k, v in sources.items()}


def _build_music_library_tracks():
    if not getattr(sound_mgr, "file_paths", None):
        return []
    sources = _collect_music_track_sources()
    tracks = []
    for key in sorted(sound_mgr.file_paths.keys()):
        if not key.startswith("bgm_"):
            continue
        track_id = key[4:]
        display = _format_music_track_name(track_id)
        meta = resolve_music_metadata(track_id)
        tags = sources.get(track_id, [])
        short_tags = tags[:2]
        if not tags:
            source_label = "未绑定场景"
        elif len(tags) > 2:
            source_label = "、".join(short_tags) + " 等"
        else:
            source_label = "、".join(short_tags)
        tracks.append({
            "id": track_id,
            "display": display,
            "source": source_label,
            "source_full": list(tags),
            "metadata": meta,
            "tags": meta.get("tags", []),
        })
    return tracks


def enter_music_library():
    global music_library_all_tracks, music_library_filter
    global music_library_status_msg, music_library_status_timer
    global music_library_sort_mode
    global music_library_search_query, music_library_search_active
    music_library_all_tracks = _build_music_library_tracks()
    music_library_filter = "all"
    music_library_sort_mode = "default"
    music_library_search_query = ""
    music_library_search_active = False
    rebuild_music_library_view()
    _queue_selected_music_library_track()
    if not getattr(sound_mgr, "enabled", True):
        set_music_library_message("音频系统未启用，无法试听", 240)
    elif not music_library_tracks:
        set_music_library_message("未找到可用的BGM文件", 240)
    else:
        set_music_library_message("↑/↓选择，Enter播放，Space恢复默认", 240)


def rebuild_music_library_view(preserve_track_id=None):
    global music_library_tracks, music_library_selected, music_library_scroll_index
    global music_library_sort_mode, music_library_search_query
    if not music_library_all_tracks:
        music_library_tracks = []
        music_library_selected = 0
        music_library_scroll_index = 0
        return
    query = music_library_search_query.strip().lower()
    filtered = []
    for track in music_library_all_tracks:
        tags = track.get("tags", [])
        if music_library_filter != "all" and music_library_filter not in tags:
            continue
        meta = track.get("metadata") or {}
        if query:
            haystack = "|".join([
                track.get("display", ""),
                track.get("id", ""),
                meta.get("mood", ""),
                meta.get("description", ""),
            ]).lower()
            if query not in haystack:
                continue
        filtered.append(track)

    if music_library_sort_mode == "name":
        filtered.sort(key=lambda t: t.get("display", ""))
    elif music_library_sort_mode == "bpm":
        filtered.sort(key=lambda t: ((t.get("metadata") or {}).get("bpm", 0), t.get("display", "")))
    elif music_library_sort_mode == "mood":
        filtered.sort(key=lambda t: ((t.get("metadata") or {}).get("mood", ""), t.get("display", "")))

    music_library_tracks = filtered
    target_idx = 0
    if preserve_track_id:
        for idx, track in enumerate(filtered):
            if track["id"] == preserve_track_id:
                target_idx = idx
                break
    music_library_selected = min(target_idx, max(0, len(filtered) - 1)) if filtered else 0
    music_library_scroll_index = 0
    ensure_music_library_visible()
    _queue_selected_music_library_track()


def apply_music_library_filter(filter_key):
    global music_library_filter
    if filter_key == music_library_filter:
        return
    prev_track = None
    if 0 <= music_library_selected < len(music_library_tracks):
        prev_track = music_library_tracks[music_library_selected]["id"]
    music_library_filter = filter_key
    rebuild_music_library_view(preserve_track_id=prev_track)


def cycle_music_library_filter(step):
    global music_library_filter
    if not MUSIC_FILTER_OPTIONS:
        return
    keys = [key for key, _ in MUSIC_FILTER_OPTIONS]
    try:
        idx = keys.index(music_library_filter)
    except ValueError:
        idx = 0
    new_key = keys[(idx + step) % len(keys)]
    apply_music_library_filter(new_key)


def set_music_library_sort_mode(mode):
    global music_library_sort_mode
    valid = {key for key, _ in MUSIC_SORT_OPTIONS}
    if mode not in valid or mode == music_library_sort_mode:
        return
    prev_track = None
    if 0 <= music_library_selected < len(music_library_tracks):
        prev_track = music_library_tracks[music_library_selected]["id"]
    music_library_sort_mode = mode
    rebuild_music_library_view(preserve_track_id=prev_track)


def set_music_library_search_query(text):
    global music_library_search_query
    normalized = text[:MUSIC_SEARCH_MAX_LEN]
    if normalized == music_library_search_query:
        return
    music_library_search_query = normalized
    rebuild_music_library_view()


def _apply_music_library_exit_music():
    if music_library_now_playing:
        music_director.set_state(
            "menu",
            intensity=0.4,
            override_track=music_library_now_playing,
            immediate=True,
            force=True,
            layers_enabled=False,
        )
    else:
        music_director.set_state("menu", intensity=0.25)


def return_to_audio_hub_from_music_library():
    global game_state, audio_hub_selected
    game_state = "audio_hub"
    audio_hub_selected = 0
    _apply_music_library_exit_music()


def return_to_menu_from_music_library():
    global game_state, main_menu_selected
    game_state = "menu"
    main_menu_selected = 0
    _apply_music_library_exit_music()


def set_music_library_message(msg, duration=180):
    global music_library_status_msg, music_library_status_timer
    music_library_status_msg = msg
    music_library_status_timer = duration


def play_music_library_track(index):
    global music_library_now_playing
    if not getattr(sound_mgr, "enabled", True):
        set_music_library_message("当前环境未启用声音播放", 240)
        return
    if not (0 <= index < len(music_library_tracks)):
        set_music_library_message("没有可播放的曲目", 180)
        return
    track = music_library_tracks[index]
    music_director.set_state(
        "menu",
        intensity=0.5,
        override_track=track["id"],
        immediate=True,
        force=True,
        layers_enabled=False,
    )
    music_library_now_playing = track["id"]
    set_music_library_message(f"正在播放：{track['display']}", 300)


def stop_music_library_track():
    global music_library_now_playing
    music_library_now_playing = None
    music_director.set_state("menu", intensity=0.25, force=True)
    set_music_library_message("已恢复默认菜单音乐", 200)


def get_music_library_layout():
    list_rect = pygame.Rect(80, 170, 500, HEIGHT - 260)
    info_rect = pygame.Rect(620, 170, WIDTH - 700, HEIGHT - 260)
    btn_y = HEIGHT - 70
    controls = {
        "stop": pygame.Rect(WIDTH // 2 - 240, btn_y, 140, 40),
        "play": pygame.Rect(WIDTH // 2 - 70, btn_y, 140, 40),
        "back": pygame.Rect(WIDTH // 2 + 100, btn_y, 140, 40),
    }
    return list_rect, info_rect, controls


def get_music_filter_layout(list_rect=None, start_y=None):
    if list_rect is None:
        list_rect, _, _ = get_music_library_layout()
    chip_w = 88
    chip_h = 26
    gap = 10
    start_x = list_rect.x + 12
    max_x = list_rect.right - 12
    x = start_x
    y = start_y if start_y is not None else list_rect.y + 10
    chips = []
    for key, label in MUSIC_FILTER_OPTIONS:
        if x + chip_w > max_x:
            x = start_x
            y += chip_h + 8
        rect = pygame.Rect(x, y, chip_w, chip_h)
        chips.append((key, label, rect))
        x += chip_w + gap
    base_y = start_y if start_y is not None else list_rect.y
    band_height = 0
    if chips:
        max_bottom = max(rect.bottom for _, _, rect in chips)
        band_height = max(0, max_bottom - base_y + 8)
    return chips, band_height


def build_music_library_controls(list_rect=None):
    if list_rect is None:
        list_rect, _, _ = get_music_library_layout()
    padding = 12
    search_rect = pygame.Rect(list_rect.right - 12 - 240, list_rect.y + padding, 240, 30)
    sort_y = search_rect.bottom + 6
    sort_buttons = []
    btn_w = 74
    btn_h = 24
    btn_x = list_rect.x + padding
    for mode, label in MUSIC_SORT_OPTIONS:
        rect = pygame.Rect(btn_x, sort_y, btn_w, btn_h)
        sort_buttons.append((mode, label, rect))
        btn_x += btn_w + 8
    chips_start = sort_y + btn_h + 8
    chips, chip_height = get_music_filter_layout(list_rect, start_y=chips_start)
    chips_bottom = chips[-1][2].bottom if chips else (sort_y + btn_h)
    max_bottom = max(search_rect.bottom, sort_y + btn_h, chips_bottom)
    control_bottom = max_bottom + padding
    content_top = min(list_rect.bottom, control_bottom)
    return {
        "search_rect": search_rect,
        "sort_buttons": sort_buttons,
        "filter_chips": chips,
        "content_top": content_top,
    }


def _music_library_visible_rows():
    list_rect, _, _ = get_music_library_layout()
    controls = build_music_library_controls(list_rect)
    header_height = max(0, controls["content_top"] - list_rect.y)
    usable_height = max(0, list_rect.height - header_height - 12)
    return max(1, usable_height // MUSIC_LIBRARY_ITEM_HEIGHT)


def ensure_music_library_visible():
    global music_library_scroll_index
    visible = _music_library_visible_rows()
    max_start = max(0, len(music_library_tracks) - visible)
    if music_library_selected < music_library_scroll_index:
        music_library_scroll_index = music_library_selected
    elif music_library_selected >= music_library_scroll_index + visible:
        music_library_scroll_index = music_library_selected - visible + 1
    music_library_scroll_index = max(0, min(max_start, music_library_scroll_index))


def _queue_music_library_prewarm(track_id: str | None):
    if not track_id:
        return
    try:
        if getattr(sound_mgr, "enabled", False) and hasattr(sound_mgr, "queue_bgm_prewarm"):
            sound_mgr.queue_bgm_prewarm(track_id)
    except Exception:
        return


def _queue_selected_music_library_track():
    try:
        if 0 <= music_library_selected < len(music_library_tracks):
            _queue_music_library_prewarm(music_library_tracks[music_library_selected].get("id"))
    except Exception:
        return


def move_music_library_selection(delta):
    global music_library_selected
    if not music_library_tracks:
        music_library_selected = 0
        music_library_scroll_index = 0
        return
    music_library_selected = max(0, min(len(music_library_tracks) - 1, music_library_selected + delta))
    ensure_music_library_visible()
    _queue_selected_music_library_track()


def scroll_music_library(delta):
    global music_library_scroll_index
    if not music_library_tracks:
        music_library_scroll_index = 0
        return
    visible = _music_library_visible_rows()
    max_start = max(0, len(music_library_tracks) - visible)
    music_library_scroll_index = max(0, min(max_start, music_library_scroll_index + delta))


SOUND_LAB_ITEM_HEIGHT = 60

SFX_METADATA = {
    "shoot": {"name": "主炮射击", "category": "武器", "desc": "基础武器的连续射击音效"},
    "explosion": {"name": "爆炸冲击", "category": "战斗", "desc": "大范围爆炸或导弹命中的反馈"},
    "hit": {"name": "命中反馈", "category": "战斗", "desc": "敌方受击或护盾破碎时的提示音"},
    "levelup": {"name": "升级提示", "category": "系统", "desc": "升级和奖励的正向提示音效"},
    "warning": {"name": "警告信号", "category": "系统", "desc": "高危状态或Boss预警"},
    "laser": {"name": "激光蓄能", "category": "武器", "desc": "高能激光充能并发射的音效"},
    "dash": {"name": "闪避冲刺", "category": "动作", "desc": "玩家触发位移/闪避时的反馈"},
    "graze": {"name": "擦弹奖励", "category": "动作", "desc": "擦弹判定成功时的提示"},
    "select": {"name": "菜单选择", "category": "UI", "desc": "菜单或界面选中项的轻反馈"},
    "zap": {"name": "电弧脉冲", "category": "特效", "desc": "带有电流质感的短促脉冲"},
    "sniper_charge": {"name": "狙击蓄力", "category": "武器", "desc": "狙击或强力射击的蓄力过程"},
    "freeze": {"name": "冰封冲击", "category": "特效", "desc": "时间冻结或冰冻技能的音效"},
    "nuke": {"name": "核爆引信", "category": "终极", "desc": "终极技能或核爆触发时的沉重音"},
    "gameover": {"name": "任务失败", "category": "系统", "desc": "结算或失败画面播放的提示曲"},
    "blackhole": {"name": "黑洞漩涡", "category": "特效", "desc": "空间扭曲或黑洞技能的音效"},
    "achievement": {"name": "成就解锁", "category": "系统", "desc": "成就完成时的庆祝提示"},
    "item_pickup": {"name": "拾取奖励", "category": "系统", "desc": "道具或资源拾取时的提示"},
    "critical": {"name": "暴击提示", "category": "战斗", "desc": "暴击发生时的高亮音效"},
    "heal": {"name": "治疗脉冲", "category": "支援", "desc": "治疗或恢复效果的提示"},
    "shield": {"name": "护盾激活", "category": "支援", "desc": "护盾开启或刷新时的音效"},
}


def _format_sfx_display(effect_id):
    meta = SFX_METADATA.get(effect_id)
    if meta and meta.get("name"):
        return meta["name"]
    parts = effect_id.split("_")
    return " ".join(part.capitalize() for part in parts) if parts else effect_id


def _get_sfx_category(effect_id):
    meta = SFX_METADATA.get(effect_id)
    return meta.get("category", "通用反馈") if meta else "通用反馈"


def _get_sfx_desc(effect_id):
    meta = SFX_METADATA.get(effect_id)
    return meta.get("desc", "暂无详细描述，该音效用于通用反馈。") if meta else "暂无详细描述，该音效用于通用反馈。"


def _build_sound_lab_tracks():
    if not getattr(sound_mgr, "sounds", None):
        return []
    tracks = []
    for effect_id in sorted(sound_mgr.sounds.keys()):
        if effect_id.startswith("bgm_"):
            continue
        display = _format_sfx_display(effect_id)
        category = _get_sfx_category(effect_id)
        desc = _get_sfx_desc(effect_id)
        category_code = SFX_CATEGORY_CODES.get(category, "system")
        tracks.append({
            "id": effect_id,
            "display": display,
            "category": category,
             "category_code": category_code,
            "desc": desc,
        })
    return tracks


def enter_sound_lab():
    global sound_lab_all_tracks, sound_lab_filter
    sound_lab_all_tracks = _build_sound_lab_tracks()
    sound_lab_filter = "all"
    rebuild_sound_lab_view()


def return_to_audio_hub_from_sound_lab():
    global game_state, audio_hub_selected
    stop_sound_lab_effect()
    game_state = "audio_hub"
    audio_hub_selected = 1


def return_to_menu_from_sound_lab():
    global game_state, main_menu_selected
    stop_sound_lab_effect()
    game_state = "menu"
    main_menu_selected = 0


def play_sound_lab_effect(index):
    global sound_lab_now_playing
    if not getattr(sound_mgr, "enabled", True):
        return
    if not (0 <= index < len(sound_lab_tracks)):
        return
    effect_id = sound_lab_tracks[index]["id"]
    sound_lab_now_playing = effect_id
    sound_mgr.play(effect_id)


def stop_sound_lab_effect():
    global sound_lab_now_playing
    if not sound_lab_now_playing:
        return
    channel = sound_mgr.sound_channels.get(sound_lab_now_playing)
    if channel:
        try:
            channel.stop()
        except Exception:
            pass
    sound_lab_now_playing = None


def get_sound_lab_layout():
    list_rect = pygame.Rect(80, 170, 440, HEIGHT - 260)
    info_rect = pygame.Rect(560, 170, WIDTH - 640, HEIGHT - 260)
    btn_y = HEIGHT - 70
    controls = {
        "stop": pygame.Rect(WIDTH // 2 - 260, btn_y, 140, 40),
        "play": pygame.Rect(WIDTH // 2 - 80, btn_y, 140, 40),
        "back": pygame.Rect(WIDTH // 2 + 100, btn_y, 140, 40),
    }
    return list_rect, info_rect, controls


def get_sound_lab_filter_layout(list_rect=None):
    if list_rect is None:
        list_rect, _, _ = get_sound_lab_layout()
    chip_w = 94
    chip_h = 26
    gap = 8
    start_x = list_rect.x + 12
    max_x = list_rect.right - 12
    x = start_x
    y = list_rect.y + 10
    chips = []
    for key, label in SOUND_LAB_FILTERS:
        if x + chip_w > max_x:
            x = start_x
            y += chip_h + 8
        rect = pygame.Rect(x, y, chip_w, chip_h)
        chips.append((key, label, rect))
        x += chip_w + gap
    band_height = 0
    if chips:
        max_bottom = max(rect.bottom for _, _, rect in chips)
        band_height = max(0, max_bottom - list_rect.y + 8)
    return chips, band_height


def _sound_lab_visible_rows():
    list_rect, _, _ = get_sound_lab_layout()
    _, band_height = get_sound_lab_filter_layout(list_rect)
    usable_height = max(0, list_rect.height - band_height - 24)
    return max(1, usable_height // SOUND_LAB_ITEM_HEIGHT)


def ensure_sound_lab_visible():
    global sound_lab_scroll_index
    visible = _sound_lab_visible_rows()
    max_start = max(0, len(sound_lab_tracks) - visible)
    if sound_lab_selected < sound_lab_scroll_index:
        sound_lab_scroll_index = sound_lab_selected
    elif sound_lab_selected >= sound_lab_scroll_index + visible:
        sound_lab_scroll_index = sound_lab_selected - visible + 1
    sound_lab_scroll_index = max(0, min(max_start, sound_lab_scroll_index))


def move_sound_lab_selection(delta):
    global sound_lab_selected
    if not sound_lab_tracks:
        sound_lab_selected = 0
        sound_lab_scroll_index = 0
        return
    sound_lab_selected = max(0, min(len(sound_lab_tracks) - 1, sound_lab_selected + delta))
    ensure_sound_lab_visible()


def scroll_sound_lab(delta):
    global sound_lab_scroll_index
    if not sound_lab_tracks:
        sound_lab_scroll_index = 0
        return
    visible = _sound_lab_visible_rows()
    max_start = max(0, len(sound_lab_tracks) - visible)
    sound_lab_scroll_index = max(0, min(max_start, sound_lab_scroll_index + delta))


def rebuild_sound_lab_view(preserve_track_id=None):
    global sound_lab_tracks, sound_lab_selected, sound_lab_scroll_index
    if not sound_lab_all_tracks:
        sound_lab_tracks = []
        sound_lab_selected = 0
        sound_lab_scroll_index = 0
        return
    filtered = [t for t in sound_lab_all_tracks if sound_lab_filter == "all" or t.get("category_code") == sound_lab_filter]
    sound_lab_tracks = filtered
    target_idx = 0
    if preserve_track_id:
        for idx, track in enumerate(filtered):
            if track["id"] == preserve_track_id:
                target_idx = idx
                break
    sound_lab_selected = min(target_idx, max(0, len(filtered) - 1)) if filtered else 0
    sound_lab_scroll_index = 0
    ensure_sound_lab_visible()


def apply_sound_lab_filter(filter_key):
    global sound_lab_filter
    if filter_key == sound_lab_filter:
        return
    prev_track = None
    if 0 <= sound_lab_selected < len(sound_lab_tracks):
        prev_track = sound_lab_tracks[sound_lab_selected]["id"]
    sound_lab_filter = filter_key
    rebuild_sound_lab_view(preserve_track_id=prev_track)


def cycle_sound_lab_filter(step):
    global sound_lab_filter
    if not SOUND_LAB_FILTERS:
        return
    keys = [key for key, _ in SOUND_LAB_FILTERS]
    try:
        idx = keys.index(sound_lab_filter)
    except ValueError:
        idx = 0
    new_key = keys[(idx + step) % len(keys)]
    apply_sound_lab_filter(new_key)

def reset_game():
    global player, boss, score, item_manager, room_manager
    global global_time_freeze, is_paused
    global upgrade_options, upgrade_selected, levelup_ready, frozen_screen, wave
    global upgrade_options, upgrade_selected, levelup_ready, frozen_screen, wave, tab_paused
    global map_paused, show_full_map, room_completion_paused
    global boss_music_active, boss_challenge_music_active
    global normal_spawn_timer, normal_spawn_cycle
    global wave_event_timer, wave_event_active, wave_warning_timer
    global current_stage, last_kill_timer, no_damage_timer, recent_enemy_types
    global game_stats
    
    # reset_game() called
    
    is_paused = False 
    frozen_screen = None
    tab_paused = False
    map_paused = False
    show_full_map = False
    room_completion_paused = False
    upgrade_options = []
    upgrade_selected = 0
    levelup_ready = False
    
    # 初始化游戏统计
    game_stats = {
        "kills": 0,
        "boss_kills": 0,
        "start_time": pygame.time.get_ticks(),
        "survival_time": 0,
    }
    
    all_sprites.empty()
    mobs.empty()
    bullets.empty()
    enemy_bullets.empty()
    powerups.empty()
    supplies.empty()
    
    # 初始化物品掉落系统
    item_manager = ItemManager()
    
    # 初始化房间系统（仅房间模式）
    if game_mode == "roguelike":
        # 从第一张地图开始（线性顺序：星域迷航 -> 赛博迷城 -> 噩梦深渊）
        room_manager = RoomManager()  # 不指定theme，自动从第一张开始
        room_manager.generate_map()
        log_info(f"房间模式开始 - 第一张地图: {room_manager.get_theme_name()} ({room_manager.get_map_progress()})")
    else:
        room_manager = None
    
    score = 0
    boss = None
    boss_manager.reset()
    deactivate_boss_challenge_music()
    boss_music_active = False
    boss_challenge_music_active = False
    global_time_freeze = 0
    wave = 0
    normal_spawn_timer = 0
    normal_spawn_cycle = []
    wave_event_timer = 0
    wave_event_active = False
    wave_warning_timer = 0
    current_stage = 1
    last_kill_timer = 0
    no_damage_timer = 0
    recent_enemy_types = []
    
    try:
        # 获取玩家选择的涂装
        custom_visual = customization_manager.get_theme_visual(
            selected_plane,
            PLANES[selected_plane].get('visual', None)
        )
    except Exception as e:
        print(f"涂装加载错误: {e}")
        custom_visual = None
    
    player = Player(selected_plane, custom_visual=custom_visual)
    
    # 初始化肉鸽系统
    player.init_roguelite_systems()
    
    # 加载成就数据
    if hasattr(player, 'achievement_manager'):
        player.achievement_manager.load_from_file("achievements.json")
    
    all_sprites.add(player)
    
    try:
        # 使用当前背景对应的BGM
        activate_background_music(bg_manager.current_style)
    except Exception as e:
        print(f"音乐播放错误: {e}")
    # reset_game() done

def get_menu_buttons():
    cx = WIDTH // 2
    start_y = 200
    btn_h = 36
    gap = 8
    buttons = []
    data = [
        ("开始游戏", YELLOW, "select_plane"),
        ("武器库", ORANGE, "arsenal"),
        ("涂装", MAGENTA, "customization"),
        ("背景设置", (100, 200, 255), "background_settings"),
        ("系统设置", (255, 150, 0), "settings"),
        ("音乐", CYAN, "audio_hub"),
        ("战术图鉴", MAGENTA, "gallery"),
        ("机密档案", BLUE, "codex"),
        ("成就", LIME, "achievements"),
        ("排行榜", CYAN, "leaderboard"),
        ("退出", RED, "quit")
    ]
    for i, (txt, col, act) in enumerate(data):
        r = pygame.Rect(cx - 110, start_y + i*(btn_h+gap), 220, btn_h)
        buttons.append((r, txt, col, act))
    return buttons


AUDIO_HUB_OPTIONS = [
    {
        "id": "music_library",
        "title": "音乐馆",
        "tagline": "原声殿堂",
        "desc": "浏览所有BGM并试听不同场景的音乐氛围。",
        "color": CYAN,
    },
    {
        "id": "sound_lab",
        "title": "音效实验室",
        "tagline": "战术声场",
        "desc": "预览战斗与系统音效，微调节奏与反馈。",
        "color": CYBER_AMBER,
    },
]


def enter_audio_hub():
    global game_state, audio_hub_selected
    audio_hub_selected = 0
    game_state = "audio_hub"


def _get_audio_hub_card_rects():
    card_w = 360
    card_h = 380
    gap = 60
    total = len(AUDIO_HUB_OPTIONS)
    start_x = (WIDTH - (card_w * total + gap * (total - 1))) // 2
    card_y = 210
    rects = []
    for i in range(total):
        x = start_x + i * (card_w + gap)
        rects.append(pygame.Rect(x, card_y, card_w, card_h))
    return rects


def _get_audio_hub_back_rect():
    return pygame.Rect(WIDTH//2 - 120, HEIGHT - 120, 240, 48)


def _activate_audio_hub_option(index):
    global game_state
    if not (0 <= index < len(AUDIO_HUB_OPTIONS)):
        return
    option_id = AUDIO_HUB_OPTIONS[index]["id"]
    if option_id == "music_library":
        game_state = "music_library"
        enter_music_library()
    elif option_id == "sound_lab":
        game_state = "sound_lab"
        enter_sound_lab()


def draw_menu_ui():
    scale = 1.0 + 0.03 * math.sin(pygame.time.get_ticks() * 0.003)
    title_font = get_font(int(60 * scale), bold=True)
    glow = title_font.render("霓虹深空", True, (0, 100, 100))
    main = title_font.render("霓虹深空", True, CYAN)
    rect = main.get_rect(center=(WIDTH // 2, 110))
    safe_blit(screen, glow, (rect.x + 3, rect.y + 3))
    safe_blit(screen, main, rect)

    mx, my = pygame.mouse.get_pos()
    buttons = get_menu_buttons()
    for i, (r, txt, col, act) in enumerate(buttons):
        is_hover = r.collidepoint(mx, my)
        is_selected = (i == main_menu_selected)
        is_active = is_hover or is_selected

        bg = (col[0] // 2, col[1] // 2, col[2] // 2) if is_active else (30, 30, 40)
        draw_cyber_rect(screen, r, bg, alpha=200, fill=True)

        if is_selected:
            border_col = CYAN
            border_w = 3
        elif is_hover:
            border_col = col
            border_w = 2
        else:
            border_col = GRAY
            border_w = 1

        draw_cyber_rect(screen, r, border_col, border_width=border_w, fill=False)
        draw_text(
            screen,
            f"[ {txt} ]" if is_active else txt,
            18,
            r.centerx,
            r.centery - 8,
            WHITE if is_active else GRAY,
            glow=is_active,
        )


def draw_audio_hub_ui():
    """绘制音乐枢纽界面 - 赛博朋克风格"""
    t = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    
    # ====== 背景 ======
    screen.fill((6, 10, 18))
    
    # 动态网格背景
    grid_alpha = int(15 + 8 * math.sin(t / 1200))
    for gx in range(0, WIDTH, 80):
        pygame.draw.line(screen, (0, grid_alpha, grid_alpha * 2), (gx, 0), (gx, HEIGHT), 1)
    for gy in range(0, HEIGHT, 80):
        pygame.draw.line(screen, (0, grid_alpha, grid_alpha * 2), (0, gy), (WIDTH, gy), 1)
    
    # 音波装饰线（水平波动）
    wave_y = 160
    for i in range(0, WIDTH, 8):
        wave_offset = math.sin((i + t * 0.1) * 0.02) * 15
        pygame.draw.circle(screen, (0, 60, 80), (i, int(wave_y + wave_offset)), 2)
    
    # 角落装饰 - 音符主题
    corner_size = 35
    corner_color = (0, 180, 220)
    pygame.draw.lines(screen, corner_color, False, [(0, corner_size), (0, 0), (corner_size, 0)], 2)
    pygame.draw.lines(screen, corner_color, False, [(WIDTH - corner_size, 0), (WIDTH - 1, 0), (WIDTH - 1, corner_size)], 2)
    pygame.draw.lines(screen, corner_color, False, [(0, HEIGHT - corner_size), (0, HEIGHT - 1), (corner_size, HEIGHT - 1)], 2)
    pygame.draw.lines(screen, corner_color, False, [(WIDTH - corner_size, HEIGHT - 1), (WIDTH - 1, HEIGHT - 1), (WIDTH - 1, HEIGHT - corner_size)], 2)
    
    # ====== 标题区 ======
    title_glow = int(180 + 60 * math.sin(t / 600))
    # 标题背景条
    title_bar = pygame.Rect(0, 25, WIDTH, 55)
    title_bg = pygame.Surface((WIDTH, 55), pygame.SRCALPHA)
    pygame.draw.rect(title_bg, (0, 35, 55, 140), (0, 0, WIDTH, 55))
    screen.blit(title_bg, (0, 25))
    pygame.draw.line(screen, (0, title_glow, title_glow), (80, 80), (WIDTH - 80, 80), 2)
    
    # 标题文字 - 音符装饰
    title_font = pygame.font.SysFont("SimHei", 48)
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 32)
    
    title_surf = title_font.render("音乐枢纽", True, (0, title_glow, title_glow))
    note_left = emoji_font.render("🎵", True, (0, title_glow - 40, title_glow - 20))
    note_right = emoji_font.render("🎶", True, (0, title_glow - 40, title_glow - 20))
    
    title_x = WIDTH//2 - title_surf.get_width()//2
    screen.blit(note_left, (title_x - 50, 38))
    screen.blit(title_surf, (title_x, 35))
    screen.blit(note_right, (title_x + title_surf.get_width() + 15, 38))
    
    # 副标题
    draw_text(screen, "探索霓虹深空的声音世界", 18, WIDTH//2, 100, (80, 120, 140))
    
    # ====== 功能卡片 ======
    rects = _get_audio_hub_card_rects()
    for idx, (rect, option) in enumerate(zip(rects, AUDIO_HUB_OPTIONS)):
        hover = rect.collidepoint(mx, my)
        selected = (idx == audio_hub_selected)
        base_color = option["color"]
        
        # 卡片背景 - 渐变效果
        if hover or selected:
            bg = (base_color[0]//3 + 20, base_color[1]//3 + 15, base_color[2]//3 + 20)
            # 发光效果
            glow_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (base_color[0]//4, base_color[1]//4, base_color[2]//4, 80), 
                           (0, 0, rect.width + 20, rect.height + 20), border_radius=8)
            screen.blit(glow_surf, (rect.x - 10, rect.y - 10))
        else:
            bg = (15, 20, 32)
        
        draw_cyber_rect(screen, rect, bg, alpha=245, fill=True)
        
        # 边框动画
        border_width = 3 if selected else (2 if hover else 1)
        border_color = base_color if (hover or selected) else (50, 60, 75)
        draw_cyber_rect(screen, rect, border_color, border_width=border_width, fill=False)
        
        # 顶部装饰条
        deco_rect = pygame.Rect(rect.x + 10, rect.y + 8, rect.width - 20, 4)
        pygame.draw.rect(screen, base_color if (hover or selected) else (40, 50, 65), deco_rect, border_radius=2)
        
        # 图标区域
        icon_y = rect.y + 50
        icon_size = 60
        icon_rect = pygame.Rect(rect.centerx - icon_size//2, icon_y, icon_size, icon_size)
        pygame.draw.rect(screen, (base_color[0]//6, base_color[1]//6, base_color[2]//6), icon_rect, border_radius=8)
        pygame.draw.rect(screen, base_color if (hover or selected) else (60, 70, 90), icon_rect, 2, border_radius=8)
        
        # 图标
        icon_font = pygame.font.SysFont("Segoe UI Emoji", 32)
        icon_text = "🎵" if option["id"] == "music_library" else "🔊"
        icon_surf = icon_font.render(icon_text, True, WHITE)
        screen.blit(icon_surf, (icon_rect.centerx - icon_surf.get_width()//2, icon_rect.centery - icon_surf.get_height()//2))
        
        # 标题
        title_color = WHITE if (hover or selected) else (200, 200, 210)
        draw_text(screen, option["title"], 36, rect.centerx, rect.y + 130, title_color, glow=(hover or selected))
        
        # 标语
        draw_text(screen, option["tagline"], 20, rect.centerx, rect.y + 170, base_color)
        
        # 分隔线
        sep_y = rect.y + 195
        pygame.draw.line(screen, (40, 50, 65), (rect.x + 30, sep_y), (rect.x + rect.width - 30, sep_y), 1)
        
        # 描述
        desc_lines = textwrap.wrap(option["desc"], width=16)
        text_y = rect.y + 215
        for line in desc_lines[:4]:
            draw_text(screen, line, 17, rect.centerx, text_y, (140, 150, 165))
            text_y += 26
        
        # 进入按钮
        btn_rect = pygame.Rect(rect.centerx - 60, rect.bottom - 65, 120, 36)
        btn_hover = btn_rect.collidepoint(mx, my)
        btn_bg = (base_color[0]//3, base_color[1]//3, base_color[2]//3) if btn_hover else (25, 30, 42)
        draw_cyber_rect(screen, btn_rect, btn_bg, alpha=230, fill=True)
        draw_cyber_rect(screen, btn_rect, base_color if btn_hover else (70, 80, 100), border_width=1, fill=False)
        # 分开渲染符号和文字
        btn_text_col = WHITE if btn_hover else (180, 180, 190)
        btn_emoji_font = pygame.font.SysFont("Segoe UI Emoji", 16)
        btn_text_font = pygame.font.SysFont("SimHei", 16)
        btn_icon_surf = btn_emoji_font.render("▸", True, btn_text_col)
        btn_label_surf = btn_text_font.render(" 进入", True, btn_text_col)
        btn_total_w = btn_icon_surf.get_width() + btn_label_surf.get_width()
        screen.blit(btn_icon_surf, (btn_rect.centerx - btn_total_w//2, btn_rect.centery - btn_icon_surf.get_height()//2))
        screen.blit(btn_label_surf, (btn_rect.centerx - btn_total_w//2 + btn_icon_surf.get_width(), btn_rect.centery - btn_label_surf.get_height()//2))
        
        # 选中指示器
        if selected:
            indicator_y = rect.bottom - 18
            pygame.draw.circle(screen, base_color, (rect.centerx, indicator_y), 5)
            pygame.draw.circle(screen, WHITE, (rect.centerx, indicator_y), 3)
    
    # ====== 返回按钮 ======
    back_rect = _get_audio_hub_back_rect()
    back_hover = back_rect.collidepoint(mx, my)
    back_bg = (40, 35, 50) if back_hover else (20, 22, 32)
    draw_cyber_rect(screen, back_rect, back_bg, alpha=235, fill=True)
    draw_cyber_rect(screen, back_rect, CYAN if back_hover else (60, 70, 85), border_width=2, fill=False)
    # 分开渲染符号和文字
    back_text_col = WHITE if back_hover else (150, 160, 170)
    back_emoji_font = pygame.font.SysFont("Segoe UI Emoji", 18)
    back_text_font = pygame.font.SysFont("SimHei", 18)
    back_icon_surf = back_emoji_font.render("◀", True, back_text_col)
    back_label_surf = back_text_font.render(" 返回主菜单", True, back_text_col)
    back_total_w = back_icon_surf.get_width() + back_label_surf.get_width()
    screen.blit(back_icon_surf, (back_rect.centerx - back_total_w//2, back_rect.centery - back_icon_surf.get_height()//2))
    screen.blit(back_label_surf, (back_rect.centerx - back_total_w//2 + back_icon_surf.get_width(), back_rect.centery - back_label_surf.get_height()//2))
    
    # 底部装饰线
    pygame.draw.line(screen, (0, 60, 80), (100, HEIGHT - 50), (WIDTH - 100, HEIGHT - 50), 1)


def draw_music_library_ui():
    """绘制音乐馆界面 - 赛博朋克风格"""
    t = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    
    # ====== 背景 ======
    screen.fill((6, 10, 18))
    
    # 动态网格背景
    grid_alpha = int(12 + 6 * math.sin(t / 1000))
    for gx in range(0, WIDTH, 70):
        pygame.draw.line(screen, (0, grid_alpha, grid_alpha * 2), (gx, 0), (gx, HEIGHT), 1)
    for gy in range(0, HEIGHT, 70):
        pygame.draw.line(screen, (0, grid_alpha, grid_alpha * 2), (0, gy), (WIDTH, gy), 1)
    
    # 角落装饰
    corner_size = 28
    corner_color = (0, 150, 200)
    pygame.draw.lines(screen, corner_color, False, [(0, corner_size), (0, 0), (corner_size, 0)], 2)
    pygame.draw.lines(screen, corner_color, False, [(WIDTH - corner_size, 0), (WIDTH - 1, 0), (WIDTH - 1, corner_size)], 2)
    pygame.draw.lines(screen, corner_color, False, [(0, HEIGHT - corner_size), (0, HEIGHT - 1), (corner_size, HEIGHT - 1)], 2)
    pygame.draw.lines(screen, corner_color, False, [(WIDTH - corner_size, HEIGHT - 1), (WIDTH - 1, HEIGHT - 1), (WIDTH - 1, HEIGHT - corner_size)], 2)
    
    # ====== 标题区 ======
    title_glow = int(180 + 55 * math.sin(t / 500))
    title_bar = pygame.Rect(0, 8, WIDTH, 48)
    title_bg = pygame.Surface((WIDTH, 48), pygame.SRCALPHA)
    pygame.draw.rect(title_bg, (0, 35, 55, 130), (0, 0, WIDTH, 48))
    screen.blit(title_bg, (0, 8))
    pygame.draw.line(screen, (0, title_glow, title_glow), (60, 56), (WIDTH - 60, 56), 2)
    
    # 标题文字
    title_font = pygame.font.SysFont("SimHei", 38)
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 28)
    title_surf = title_font.render("音乐馆", True, (0, title_glow, title_glow))
    note_left = emoji_font.render("🎵", True, (0, title_glow - 30, title_glow - 15))
    note_right = emoji_font.render("🎶", True, (0, title_glow - 30, title_glow - 15))
    title_x = WIDTH//2 - title_surf.get_width()//2
    screen.blit(note_left, (title_x - 42, 16))
    screen.blit(title_surf, (title_x, 15))
    screen.blit(note_right, (title_x + title_surf.get_width() + 10, 16))
    
    # ====== 布局获取 ======
    list_rect, info_rect, controls = get_music_library_layout()
    
    # ====== 左侧列表区 ======
    # 列表标题条
    list_title_rect = pygame.Rect(list_rect.x, list_rect.y - 32, list_rect.width, 28)
    draw_cyber_rect(screen, list_title_rect, (0, 40, 60), alpha=200, fill=True)
    # 分开渲染符号和文字
    list_title_emoji = pygame.font.SysFont("Segoe UI Emoji", 13)
    list_title_text = pygame.font.SysFont("SimHei", 13)
    list_icon = list_title_emoji.render("◇", True, CYAN)
    list_label = list_title_text.render(f" 曲目列表 ({len(music_library_tracks)})", True, CYAN)
    list_total = list_icon.get_width() + list_label.get_width()
    screen.blit(list_icon, (list_title_rect.centerx - list_total//2, list_title_rect.y + 6))
    screen.blit(list_label, (list_title_rect.centerx - list_total//2 + list_icon.get_width(), list_title_rect.y + 6))
    
    # 列表背景
    draw_cyber_rect(screen, list_rect, (10, 16, 28), alpha=240, fill=True)
    draw_cyber_rect(screen, list_rect, (40, 80, 100), border_width=1, fill=False)
    # 左边高亮条
    pygame.draw.rect(screen, CYAN, (list_rect.x, list_rect.y, 3, list_rect.height))
    
    # ====== 右侧信息区 ======
    info_title_rect = pygame.Rect(info_rect.x, info_rect.y - 32, info_rect.width, 28)
    draw_cyber_rect(screen, info_title_rect, (50, 30, 60), alpha=200, fill=True)
    # 分开渲染符号和文字
    info_title_emoji = pygame.font.SysFont("Segoe UI Emoji", 13)
    info_title_text = pygame.font.SysFont("SimHei", 13)
    info_icon = info_title_emoji.render("◆", True, MAGENTA)
    info_label = info_title_text.render(" 曲目信息", True, MAGENTA)
    info_total = info_icon.get_width() + info_label.get_width()
    screen.blit(info_icon, (info_title_rect.centerx - info_total//2, info_title_rect.y + 6))
    screen.blit(info_label, (info_title_rect.centerx - info_total//2 + info_icon.get_width(), info_title_rect.y + 6))
    
    draw_cyber_rect(screen, info_rect, (12, 14, 22), alpha=240, fill=True)
    draw_cyber_rect(screen, info_rect, (80, 50, 90), border_width=1, fill=False)
    pygame.draw.rect(screen, MAGENTA, (info_rect.x, info_rect.y, 3, info_rect.height))

    # ====== 控制区域 ======
    controls_layout = build_music_library_controls(list_rect)
    search_rect = controls_layout["search_rect"]
    sort_buttons = controls_layout["sort_buttons"]
    chips = controls_layout["filter_chips"]
    content_top = controls_layout["content_top"]

    # 搜索框
    search_hover = search_rect.collidepoint(mx, my)
    search_active = music_library_search_active
    search_bg = (25, 35, 50) if (search_hover or search_active) else (18, 22, 32)
    draw_cyber_rect(screen, search_rect, search_bg, alpha=240, fill=True)
    border_col = CYAN if search_active else ((0, 120, 150) if search_hover else (50, 60, 75))
    draw_cyber_rect(screen, search_rect, border_col, border_width=2 if search_active else 1, fill=False)
    # 搜索图标
    search_icon_font = pygame.font.SysFont("Segoe UI Emoji", 14)
    search_icon = search_icon_font.render("🔍", True, GRAY)
    screen.blit(search_icon, (search_rect.x + 8, search_rect.y + 8))
    search_text = music_library_search_query or "搜索曲目 / 描述..."
    color = WHITE if music_library_search_query else (100, 110, 125)
    draw_text(screen, search_text, 16, search_rect.x + 32, search_rect.y + 8, color, align="left")

    # 排序按钮
    for mode, label, rect in sort_buttons:
        active = (mode == music_library_sort_mode)
        hover = rect.collidepoint(mx, my)
        bg = (30, 50, 70) if active else ((25, 35, 50) if hover else (18, 22, 32))
        border = CYAN if active else ((0, 100, 130) if hover else (45, 55, 70))
        draw_cyber_rect(screen, rect, bg, alpha=230, fill=True)
        draw_cyber_rect(screen, rect, border, border_width=2 if active else 1, fill=False)
        text_col = WHITE if active else ((200, 210, 220) if hover else (140, 150, 165))
        draw_text(screen, label, 14, rect.centerx, rect.centery - 7, text_col)

    # 场景过滤标签
    for key, label, rect in chips:
        active = (key == music_library_filter)
        hover = rect.collidepoint(mx, my)
        if active:
            bg = (0, 60, 80)
            border = CYAN
        elif hover:
            bg = (20, 35, 50)
            border = (0, 100, 130)
        else:
            bg = (15, 20, 30)
            border = (45, 55, 70)
        draw_cyber_rect(screen, rect, bg, alpha=235, fill=True)
        draw_cyber_rect(screen, rect, border, border_width=1, fill=False)
        text_col = WHITE if active else ((190, 200, 210) if hover else (120, 130, 145))
        draw_text(screen, label, 16, rect.centerx, rect.centery - 7, text_col)

    # ====== 曲目列表 ======
    padding = 10
    row_height = MUSIC_LIBRARY_ITEM_HEIGHT - 18
    visible_rows = _music_library_visible_rows()
    start_idx = music_library_scroll_index
    end_idx = min(len(music_library_tracks), start_idx + visible_rows)
    base_y = content_top

    if not music_library_tracks:
        msg = "未扫描到音乐文件" if getattr(sound_mgr, "enabled", True) else "音频系统未启用"
        draw_text(screen, msg, 22, list_rect.centerx, list_rect.centery, (80, 90, 105))
    else:
        for row, idx in enumerate(range(start_idx, end_idx)):
            track = music_library_tracks[idx]
            row_rect = pygame.Rect(
                list_rect.x + padding,
                base_y + row * MUSIC_LIBRARY_ITEM_HEIGHT,
                list_rect.width - padding * 2,
                row_height,
            )
            is_selected = (idx == music_library_selected)
            is_playing = (music_library_now_playing == track["id"])
            
            # 行背景颜色
            if is_selected:
                bg_color = (30, 60, 90)
            elif is_playing:
                bg_color = (50, 25, 35)
            else:
                bg_color = (18, 24, 36) if row % 2 == 0 else (22, 28, 40)
            
            draw_cyber_rect(screen, row_rect, bg_color, alpha=230, fill=True)
            
            # 边框
            if is_selected:
                draw_cyber_rect(screen, row_rect, CYAN, border_width=2, fill=False)
                pygame.draw.rect(screen, CYAN, (row_rect.x, row_rect.y + 2, 3, row_rect.height - 4))
            elif is_playing:
                draw_cyber_rect(screen, row_rect, (200, 80, 120), border_width=1, fill=False)
            
            # 曲目名称
            name_color = WHITE if is_selected else ((255, 200, 220) if is_playing else (200, 205, 215))
            draw_text(screen, track["display"], 20, row_rect.x + 14, row_rect.y + 6, name_color, align="left")
            
            # 场景来源
            source_line = _truncate_music_text(track["source"], 32)
            draw_text(screen, source_line, 14, row_rect.x + 14, row_rect.y + row_height - 16, (90, 100, 115), align="left")
            
            # 播放状态
            if is_playing:
                # 播放图标 + 文字分开渲染
                play_emoji_font = pygame.font.SysFont("Segoe UI Emoji", 12)
                play_text_font = pygame.font.SysFont("SimHei", 12)
                icon_surf = play_emoji_font.render("▶", True, LIME)
                text_surf = play_text_font.render(" 播放中", True, LIME)
                total_w = icon_surf.get_width() + text_surf.get_width()
                screen.blit(icon_surf, (row_rect.right - 14 - total_w, row_rect.centery - icon_surf.get_height()//2))
                screen.blit(text_surf, (row_rect.right - 14 - total_w + icon_surf.get_width(), row_rect.centery - text_surf.get_height()//2))

        # 滚动条
        if len(music_library_tracks) > visible_rows:
            scroll_track_h = list_rect.bottom - padding - base_y
            if scroll_track_h > 0:
                indicator_h = max(30, int(scroll_track_h * (visible_rows / len(music_library_tracks))))
                max_scroll = max(1, len(music_library_tracks) - visible_rows)
                indicator_y = base_y + int((scroll_track_h - indicator_h) * (music_library_scroll_index / max_scroll))
                
                # 轨道
                scroll_bar_x = list_rect.right - 10
                pygame.draw.rect(screen, (30, 40, 55), (scroll_bar_x, base_y, 8, scroll_track_h), border_radius=4)
                
                # 滑块 - 拖动时高亮
                thumb_rect = pygame.Rect(scroll_bar_x, indicator_y, 8, indicator_h)
                is_hover = thumb_rect.inflate(8, 0).collidepoint(mx, my)
                thumb_color = (100, 220, 255) if (music_library_dragging_scrollbar or is_hover) else CYAN
                pygame.draw.rect(screen, thumb_color, thumb_rect, border_radius=4)

    # ====== 曲目详情面板 ======
    info_inner = info_rect.inflate(-24, -24)
    draw_cyber_rect(screen, info_inner, (16, 22, 35), alpha=220, fill=True)
    
    info_y = info_inner.y + 12
    if 0 <= music_library_selected < len(music_library_tracks):
        current = music_library_tracks[music_library_selected]
        
        # 曲目名称
        draw_text(screen, current["display"], 28, info_inner.x + 12, info_y, WHITE, align="left")
        info_y += 45
        
        # 分隔线
        pygame.draw.line(screen, (50, 60, 80), (info_inner.x + 10, info_y), (info_inner.right - 10, info_y), 1)
        info_y += 15
        
        # ID信息
        draw_text(screen, "内部ID", 14, info_inner.x + 12, info_y, (80, 100, 120), align="left")
        draw_text(screen, current['id'], 16, info_inner.x + 12, info_y + 18, (150, 160, 175), align="left")
        info_y += 50
        
        # 关联场景
        scene_emoji = pygame.font.SysFont("Segoe UI Emoji", 14)
        scene_text = pygame.font.SysFont("SimHei", 14)
        scene_icon = scene_emoji.render("◈", True, CYBER_AMBER)
        scene_label = scene_text.render(" 关联场景", True, CYBER_AMBER)
        screen.blit(scene_icon, (info_inner.x + 12, info_y))
        screen.blit(scene_label, (info_inner.x + 12 + scene_icon.get_width(), info_y))
        info_y += 28
        full_text = "、".join(current.get("source_full", [])) or current.get("source", "未绑定场景")
        for line in _wrap_music_sources(full_text, limit=18, max_lines=6):
            draw_text(screen, line, 15, info_inner.x + 20, info_y, (130, 140, 155), align="left")
            info_y += 22
    else:
        draw_text(screen, "请选择一首曲目", 22, info_inner.centerx, info_inner.centery, (80, 90, 105))

    # ====== 控制按钮 ======
    control_labels = {
        "stop": ("⏹", "恢复默认"),
        "play": ("▶", "播放选中"),
        "back": ("◀", "返回"),
    }
    ctrl_emoji_font = pygame.font.SysFont("Segoe UI Emoji", 16)
    ctrl_text_font = pygame.font.SysFont("SimHei", 16)
    for key, rect in controls.items():
        hover = rect.collidepoint(mx, my)
        icon, label = control_labels[key]
        
        if hover:
            bg = (35, 50, 70)
            border = CYAN
        else:
            bg = (18, 24, 36)
            border = (50, 65, 85)
        
        draw_cyber_rect(screen, rect, bg, alpha=235, fill=True)
        draw_cyber_rect(screen, rect, border, border_width=2 if hover else 1, fill=False)
        
        # 图标 + 文字分开渲染
        text_col = WHITE if hover else (150, 160, 175)
        icon_surf = ctrl_emoji_font.render(icon, True, text_col)
        label_surf = ctrl_text_font.render(label, True, text_col)
        total_w = icon_surf.get_width() + 6 + label_surf.get_width()
        start_x = rect.centerx - total_w // 2
        screen.blit(icon_surf, (start_x, rect.centery - icon_surf.get_height()//2))
        screen.blit(label_surf, (start_x + icon_surf.get_width() + 6, rect.centery - label_surf.get_height()//2))

    # ====== 当前播放状态 ======
    status_bar = pygame.Rect(WIDTH - 350, 10, 340, 36)
    draw_cyber_rect(screen, status_bar, (15, 25, 40), alpha=200, fill=True)
    status_emoji_font = pygame.font.SysFont("Segoe UI Emoji", 14)
    status_text_font = pygame.font.SysFont("SimHei", 14)
    if music_library_now_playing:
        track_name = next((t["display"] for t in music_library_tracks if t["id"] == music_library_now_playing), _format_music_track_name(music_library_now_playing))
        emoji_surf = status_emoji_font.render("🎧", True, LIME)
        text_surf = status_text_font.render(f" 当前播放：{track_name}", True, LIME)
        total_w = emoji_surf.get_width() + text_surf.get_width()
        screen.blit(emoji_surf, (status_bar.right - 10 - total_w, status_bar.y + 10))
        screen.blit(text_surf, (status_bar.right - 10 - total_w + emoji_surf.get_width(), status_bar.y + 10))
    else:
        emoji_surf = status_emoji_font.render("🎧", True, (100, 110, 125))
        text_surf = status_text_font.render(" 当前播放：默认菜单主题", True, (100, 110, 125))
        total_w = emoji_surf.get_width() + text_surf.get_width()
        screen.blit(emoji_surf, (status_bar.right - 10 - total_w, status_bar.y + 10))
        screen.blit(text_surf, (status_bar.right - 10 - total_w + emoji_surf.get_width(), status_bar.y + 10))

def draw_sound_lab_ui():
    """绘制音效实验室界面 - 赛博朋克风格"""
    t = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    
    # ====== 背景 ======
    screen.fill((10, 8, 14))
    
    # 动态网格背景 - 琥珀色调
    grid_alpha = int(12 + 6 * math.sin(t / 900))
    for gx in range(0, WIDTH, 70):
        pygame.draw.line(screen, (grid_alpha * 2, grid_alpha, 0), (gx, 0), (gx, HEIGHT), 1)
    for gy in range(0, HEIGHT, 70):
        pygame.draw.line(screen, (grid_alpha * 2, grid_alpha, 0), (0, gy), (WIDTH, gy), 1)
    
    # 音波装饰 - 脉冲效果
    pulse_alpha = int(30 + 20 * math.sin(t / 300))
    for i in range(3):
        wave_y = 140 + i * 8
        for x in range(0, WIDTH, 12):
            wave_h = int(4 + 3 * math.sin((x + t * 0.15 + i * 50) * 0.03))
            pygame.draw.rect(screen, (pulse_alpha + 20, pulse_alpha, 0), (x, wave_y - wave_h, 6, wave_h * 2), border_radius=1)
    
    # 角落装饰 - 琥珀主题
    corner_size = 28
    corner_color = (200, 150, 50)
    pygame.draw.lines(screen, corner_color, False, [(0, corner_size), (0, 0), (corner_size, 0)], 2)
    pygame.draw.lines(screen, corner_color, False, [(WIDTH - corner_size, 0), (WIDTH - 1, 0), (WIDTH - 1, corner_size)], 2)
    pygame.draw.lines(screen, corner_color, False, [(0, HEIGHT - corner_size), (0, HEIGHT - 1), (corner_size, HEIGHT - 1)], 2)
    pygame.draw.lines(screen, corner_color, False, [(WIDTH - corner_size, HEIGHT - 1), (WIDTH - 1, HEIGHT - 1), (WIDTH - 1, HEIGHT - corner_size)], 2)
    
    # ====== 标题区 ======
    title_glow = int(180 + 55 * math.sin(t / 500))
    title_bar = pygame.Rect(0, 8, WIDTH, 48)
    title_bg = pygame.Surface((WIDTH, 48), pygame.SRCALPHA)
    pygame.draw.rect(title_bg, (55, 40, 20, 130), (0, 0, WIDTH, 48))
    screen.blit(title_bg, (0, 8))
    pygame.draw.line(screen, (title_glow, int(title_glow * 0.7), 0), (60, 56), (WIDTH - 60, 56), 2)
    
    # 标题文字
    title_font = pygame.font.SysFont("SimHei", 38)
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 28)
    title_surf = title_font.render("音效实验室", True, (title_glow, int(title_glow * 0.7), 0))
    icon_left = emoji_font.render("🔊", True, (title_glow - 30, int((title_glow - 30) * 0.7), 0))
    icon_right = emoji_font.render("🎚", True, (title_glow - 30, int((title_glow - 30) * 0.7), 0))
    title_x = WIDTH//2 - title_surf.get_width()//2
    screen.blit(icon_left, (title_x - 42, 16))
    screen.blit(title_surf, (title_x, 15))
    screen.blit(icon_right, (title_x + title_surf.get_width() + 10, 16))
    
    # ====== 布局获取 ======
    list_rect, info_rect, controls = get_sound_lab_layout()
    
    # ====== 左侧列表区 ======
    list_title_rect = pygame.Rect(list_rect.x, list_rect.y - 32, list_rect.width, 28)
    draw_cyber_rect(screen, list_title_rect, (60, 45, 20), alpha=200, fill=True)
    # 分开渲染符号和文字
    lab_list_emoji = pygame.font.SysFont("Segoe UI Emoji", 13)
    lab_list_text = pygame.font.SysFont("SimHei", 13)
    lab_list_icon = lab_list_emoji.render("◇", True, CYBER_AMBER)
    lab_list_label = lab_list_text.render(f" 音效列表 ({len(sound_lab_tracks)})", True, CYBER_AMBER)
    lab_list_total = lab_list_icon.get_width() + lab_list_label.get_width()
    screen.blit(lab_list_icon, (list_title_rect.centerx - lab_list_total//2, list_title_rect.y + 6))
    screen.blit(lab_list_label, (list_title_rect.centerx - lab_list_total//2 + lab_list_icon.get_width(), list_title_rect.y + 6))
    
    draw_cyber_rect(screen, list_rect, (14, 12, 18), alpha=240, fill=True)
    draw_cyber_rect(screen, list_rect, (80, 60, 40), border_width=1, fill=False)
    pygame.draw.rect(screen, CYBER_AMBER, (list_rect.x, list_rect.y, 3, list_rect.height))
    
    # ====== 右侧信息区 ======
    info_title_rect = pygame.Rect(info_rect.x, info_rect.y - 32, info_rect.width, 28)
    draw_cyber_rect(screen, info_title_rect, (70, 50, 25), alpha=200, fill=True)
    # 分开渲染符号和文字
    lab_info_emoji = pygame.font.SysFont("Segoe UI Emoji", 13)
    lab_info_text = pygame.font.SysFont("SimHei", 13)
    lab_info_icon = lab_info_emoji.render("◆", True, (255, 180, 80))
    lab_info_label = lab_info_text.render(" 音效详情", True, (255, 180, 80))
    lab_info_total = lab_info_icon.get_width() + lab_info_label.get_width()
    screen.blit(lab_info_icon, (info_title_rect.centerx - lab_info_total//2, info_title_rect.y + 6))
    screen.blit(lab_info_label, (info_title_rect.centerx - lab_info_total//2 + lab_info_icon.get_width(), info_title_rect.y + 6))
    
    draw_cyber_rect(screen, info_rect, (12, 10, 16), alpha=240, fill=True)
    draw_cyber_rect(screen, info_rect, (90, 65, 35), border_width=1, fill=False)
    pygame.draw.rect(screen, (255, 180, 80), (info_rect.x, info_rect.y, 3, info_rect.height))

    # ====== 分类过滤标签 ======
    chips, filter_band_height = get_sound_lab_filter_layout(list_rect)
    for key, label, rect in chips:
        active = (key == sound_lab_filter)
        hover = rect.collidepoint(mx, my)
        if active:
            bg = (70, 50, 25)
            border = CYBER_AMBER
        elif hover:
            bg = (45, 35, 20)
            border = (180, 130, 50)
        else:
            bg = (22, 18, 14)
            border = (60, 50, 35)
        draw_cyber_rect(screen, rect, bg, alpha=235, fill=True)
        draw_cyber_rect(screen, rect, border, border_width=1, fill=False)
        text_col = WHITE if active else ((220, 200, 180) if hover else (140, 120, 100))
        draw_text(screen, label, 16, rect.centerx, rect.centery - 7, text_col)

    # ====== 音效列表 ======
    padding = 10
    visible_rows = _sound_lab_visible_rows()
    start_idx = sound_lab_scroll_index
    end_idx = min(len(sound_lab_tracks), start_idx + visible_rows)
    content_top = list_rect.y + padding + filter_band_height

    if not sound_lab_tracks:
        msg = "未加载到可用音效" if getattr(sound_mgr, "enabled", True) else "音频系统未启用"
        draw_text(screen, msg, 22, list_rect.centerx, list_rect.centery, (100, 90, 75))
    else:
        for row, idx in enumerate(range(start_idx, end_idx)):
            track = sound_lab_tracks[idx]
            row_rect = pygame.Rect(
                list_rect.x + padding,
                content_top + row * SOUND_LAB_ITEM_HEIGHT,
                list_rect.width - padding * 2,
                SOUND_LAB_ITEM_HEIGHT - 8,
            )
            is_selected = (idx == sound_lab_selected)
            is_playing = (sound_lab_now_playing == track["id"])
            
            # 行背景
            if is_selected:
                bg_color = (50, 40, 25)
            elif is_playing:
                bg_color = (55, 30, 30)
            else:
                bg_color = (18, 15, 20) if row % 2 == 0 else (22, 18, 24)
            
            draw_cyber_rect(screen, row_rect, bg_color, alpha=230, fill=True)
            
            # 边框
            if is_selected:
                draw_cyber_rect(screen, row_rect, CYBER_AMBER, border_width=2, fill=False)
                pygame.draw.rect(screen, CYBER_AMBER, (row_rect.x, row_rect.y + 2, 3, row_rect.height - 4))
            elif is_playing:
                draw_cyber_rect(screen, row_rect, (200, 100, 100), border_width=1, fill=False)
            
            # 音效名称
            name_color = WHITE if is_selected else ((255, 200, 200) if is_playing else (200, 195, 185))
            draw_text(screen, track["display"], 20, row_rect.x + 14, row_rect.y + 4, name_color, align="left")
            
            # 类别标签
            cat_color = CYBER_AMBER if is_selected else (180, 140, 60)
            draw_text(screen, track["category"], 14, row_rect.x + 14, row_rect.y + row_rect.height - 16, cat_color, align="left")
            
            # 描述预览
            desc_text = _truncate_music_text(track["desc"], 22)
            draw_text(screen, desc_text, 12, row_rect.right - 12, row_rect.y + row_rect.height - 16, (100, 95, 85), align="right")

        # 滚动条
        if len(sound_lab_tracks) > visible_rows:
            scroll_track_h = list_rect.height - padding * 2 - filter_band_height
            if scroll_track_h > 0:
                indicator_h = max(30, int(scroll_track_h * (visible_rows / len(sound_lab_tracks))))
                max_scroll = max(1, len(sound_lab_tracks) - visible_rows)
                indicator_y = content_top + int((scroll_track_h - indicator_h) * (sound_lab_scroll_index / max_scroll))
                
                # 轨道
                scroll_bar_x = list_rect.right - 10
                pygame.draw.rect(screen, (40, 35, 28), (scroll_bar_x, content_top, 8, scroll_track_h), border_radius=4)
                
                # 滑块 - 拖动时高亮
                thumb_rect = pygame.Rect(scroll_bar_x, indicator_y, 8, indicator_h)
                is_hover = thumb_rect.inflate(8, 0).collidepoint(mx, my)
                thumb_color = (255, 200, 100) if (sound_lab_dragging_scrollbar or is_hover) else CYBER_AMBER
                pygame.draw.rect(screen, thumb_color, thumb_rect, border_radius=4)

    # ====== 音效详情面板 ======
    info_inner = info_rect.inflate(-24, -24)
    draw_cyber_rect(screen, info_inner, (20, 18, 25), alpha=220, fill=True)
    
    info_y = info_inner.y + 12
    if 0 <= sound_lab_selected < len(sound_lab_tracks):
        current = sound_lab_tracks[sound_lab_selected]
        
        # 音效名称
        draw_text(screen, current["display"], 28, info_inner.x + 12, info_y, WHITE, align="left")
        info_y += 42
        
        # 分隔线
        pygame.draw.line(screen, (60, 50, 35), (info_inner.x + 10, info_y), (info_inner.right - 10, info_y), 1)
        info_y += 15
        
        # 类别
        draw_text(screen, "类别", 14, info_inner.x + 12, info_y, (100, 90, 70), align="left")
        draw_text(screen, current['category'], 18, info_inner.x + 12, info_y + 20, CYBER_AMBER, align="left")
        info_y += 55
        
        # ID
        draw_text(screen, "内部ID", 14, info_inner.x + 12, info_y, (100, 90, 70), align="left")
        draw_text(screen, current['id'], 14, info_inner.x + 12, info_y + 18, (140, 130, 115), align="left")
        info_y += 50
        
        # 描述
        desc_emoji = pygame.font.SysFont("Segoe UI Emoji", 14)
        desc_text = pygame.font.SysFont("SimHei", 14)
        desc_icon = desc_emoji.render("◈", True, (200, 160, 80))
        desc_label = desc_text.render(" 描述", True, (200, 160, 80))
        screen.blit(desc_icon, (info_inner.x + 12, info_y))
        screen.blit(desc_label, (info_inner.x + 12 + desc_icon.get_width(), info_y))
        info_y += 28
        desc_lines = textwrap.wrap(current["desc"], width=22)
        for line in desc_lines[:5]:
            draw_text(screen, line, 15, info_inner.x + 20, info_y, (140, 135, 120), align="left")
            info_y += 22
    else:
        draw_text(screen, "请选择一个音效", 22, info_inner.centerx, info_inner.centery, (100, 90, 75))

    # ====== 控制按钮 ======
    control_labels = {
        "stop": ("⏹", "停止播放"),
        "play": ("▶", "播放选中"),
        "back": ("◀", "返回"),
    }
    ctrl_emoji_font = pygame.font.SysFont("Segoe UI Emoji", 16)
    ctrl_text_font = pygame.font.SysFont("SimHei", 16)
    for key, rect in controls.items():
        hover = rect.collidepoint(mx, my)
        icon, label = control_labels[key]
        
        if hover:
            bg = (55, 45, 30)
            border = CYBER_AMBER
        else:
            bg = (22, 18, 26)
            border = (70, 55, 40)
        
        draw_cyber_rect(screen, rect, bg, alpha=235, fill=True)
        draw_cyber_rect(screen, rect, border, border_width=2 if hover else 1, fill=False)
        
        # 图标 + 文字分开渲染
        text_col = WHITE if hover else (160, 145, 125)
        icon_surf = ctrl_emoji_font.render(icon, True, text_col)
        label_surf = ctrl_text_font.render(label, True, text_col)
        total_w = icon_surf.get_width() + 6 + label_surf.get_width()
        start_x = rect.centerx - total_w // 2
        screen.blit(icon_surf, (start_x, rect.centery - icon_surf.get_height()//2))
        screen.blit(label_surf, (start_x + icon_surf.get_width() + 6, rect.centery - label_surf.get_height()//2))

    # ====== 当前播放状态 ======
    status_bar = pygame.Rect(WIDTH - 320, 10, 310, 36)
    draw_cyber_rect(screen, status_bar, (30, 25, 18), alpha=200, fill=True)
    status_emoji_font = pygame.font.SysFont("Segoe UI Emoji", 14)
    status_text_font = pygame.font.SysFont("SimHei", 14)
    if sound_lab_now_playing:
        current_name = next((t["display"] for t in sound_lab_tracks if t["id"] == sound_lab_now_playing), _format_sfx_display(sound_lab_now_playing))
        emoji_surf = status_emoji_font.render("🔊", True, CYBER_AMBER)
        text_surf = status_text_font.render(f" 当前音效：{current_name}", True, CYBER_AMBER)
        total_w = emoji_surf.get_width() + text_surf.get_width()
        screen.blit(emoji_surf, (status_bar.right - 10 - total_w, status_bar.y + 10))
        screen.blit(text_surf, (status_bar.right - 10 - total_w + emoji_surf.get_width(), status_bar.y + 10))
    else:
        emoji_surf = status_emoji_font.render("🔇", True, (100, 90, 75))
        text_surf = status_text_font.render(" 当前音效：无", True, (100, 90, 75))
        total_w = emoji_surf.get_width() + text_surf.get_width()
        screen.blit(emoji_surf, (status_bar.right - 10 - total_w, status_bar.y + 10))
        screen.blit(text_surf, (status_bar.right - 10 - total_w + emoji_surf.get_width(), status_bar.y + 10))


def draw_mode_select_ui():
    """绘制游戏模式选择UI"""
    # 标题
    t = pygame.time.get_ticks()
    scale = 1.0 + 0.05 * math.sin(t * 0.003)
    draw_text(screen, "选择游戏模式", int(54 * scale), WIDTH//2, 80, CYAN, glow=True)
    
    mx, my = pygame.mouse.get_pos()
    
    # 三个模式卡片
    card_width = 380
    card_height = 480
    gap = 40
    start_x = (WIDTH - (card_width * 3 + gap * 2)) // 2
    card_y = 180
    
    modes = [
        {
            "id": "normal",
            "name": "普通模式",
            "title_color": YELLOW,
            "icon": "⚔",
            "features": [
                "经典波次战斗",
                "无尽敌人来袭", 
                "分数决定强度",
                "传统射击体验",
                "适合新手入门"
            ],
            "difficulty": "★★☆☆☆"
        },
        {
            "id": "roguelike",
            "name": "房间模式",
            "title_color": MAGENTA,
            "icon": "🗺",
            "features": [
                "Roguelike房间",
                "地图随机生成",
                "策略路线选择",
                "房间奖励系统",
                "高难度挑战"
            ],
            "difficulty": "★★★★☆"
        },
        {
            "id": "boss_challenge",
            "name": "Boss挑战",
            "title_color": CYAN,
            "icon": "👑",
            "features": [
                "连续Boss战斗",
                "自定义Boss顺序",
                "极限生存考验",
                "测试战斗技巧",
                "终极挑战模式"
            ],
            "difficulty": "★★★★★"
        }
    ]
    
    for i, mode in enumerate(modes):
        card_x = start_x + i * (card_width + gap)
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        
        # 检测悬停和键盘选中
        is_hover = card_rect.collidepoint(mx, my)
        is_keyboard_selected = (i == mode_select_selected)
        is_current_mode = False  # 不显示"当前模式"标记，避免默认高亮
        
        # 卡片背景
        if is_hover or is_keyboard_selected:
            bg_color = (35, 45, 55)
            border_color = mode["title_color"]
            border_width = 3
        else:
            bg_color = (25, 30, 40)
            # 默认状态下也使用各自的主题色作为边框
            border_color = mode["title_color"]
            border_width = 2
        
        draw_cyber_rect(screen, card_rect, bg_color, alpha=230, fill=True)
        draw_cyber_rect(screen, card_rect, border_color, border_width=border_width, fill=False)
        
        # 图标 (使用emoji字体单独渲染)
        icon_y = card_y + 50
        emoji_font_icon = pygame.font.SysFont("Segoe UI Emoji", 70)
        icon_surf = emoji_font_icon.render(mode["icon"], True, mode["title_color"])
        screen.blit(icon_surf, (card_rect.centerx - icon_surf.get_width()//2, icon_y - icon_surf.get_height()//2))
        
        # 模式名称 (选中时发光)
        name_y = icon_y + 80
        draw_text(screen, mode["name"], 32, card_rect.centerx, name_y, mode["title_color"], glow=(is_hover or is_keyboard_selected))
        
        # 难度
        difficulty_y = name_y + 45
        draw_text(screen, f"难度: {mode['difficulty']}", 18, card_rect.centerx, difficulty_y, GRAY)
        
        # 特性列表
        features_start_y = difficulty_y + 45
        for j, feature in enumerate(mode["features"]):
            feature_y = features_start_y + j * 32
            draw_text(screen, f"• {feature}", 18, card_rect.centerx, feature_y, WHITE)
        
        # 选中标记（仅鼠标悬停时显示提示）
        if is_hover:
            hint_y = card_y + card_height - 50
            pulse = int(150 + 105 * abs(math.sin(t / 300)))
            draw_text(screen, "点击选择", 24, card_rect.centerx, hint_y, (*WHITE[:3], pulse))
    
    # 返回按钮
    back_btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 60, 200, 50)
    is_back_hover = back_btn_rect.collidepoint(mx, my)
    draw_cyber_rect(screen, back_btn_rect, (50, 20, 20) if is_back_hover else (30, 30, 40), alpha=200, fill=True)
    draw_cyber_rect(screen, back_btn_rect, RED if is_back_hover else GRAY, border_width=2, fill=False)
    draw_text(screen, "返回主菜单 [ESC]", 20, back_btn_rect.centerx, back_btn_rect.y + 18, WHITE if is_back_hover else GRAY)

def draw_settings_ui():
    """绘制系统设置界面 - 豪华赛博朋克风格"""
    global settings_saved_timer, settings_saved_msg
    
    t = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    
    # ====== 深空背景 ======
    screen.fill((8, 12, 22))
    
    # 动态网格背景
    grid_alpha = 15
    grid_color = (grid_alpha, int(grid_alpha * 1.5), grid_alpha * 2)
    grid_size = 40
    offset = int(t / 100) % grid_size
    for x in range(-offset, WIDTH + grid_size, grid_size):
        pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT))
    for y in range(-offset, HEIGHT + grid_size, grid_size):
        pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y))
    
    # 装饰性粒子
    for i in range(30):
        px = (i * 97 + int(t / 40)) % WIDTH
        py = (i * 61 + int(t / 60)) % HEIGHT
        p_alpha = int(40 + 30 * math.sin(t / 400 + i))
        pygame.draw.circle(screen, (p_alpha, p_alpha, int(p_alpha * 1.5)), (px, py), 1)
    
    # 边框发光
    glow_intensity = int(100 + 40 * math.sin(t / 500))
    border_color = (20, glow_intensity, int(glow_intensity * 1.2))
    pygame.draw.rect(screen, border_color, (0, 0, WIDTH, 3))
    pygame.draw.rect(screen, border_color, (0, HEIGHT - 3, WIDTH, 3))
    
    # ====== 豪华标题区 ======
    title_panel = pygame.Rect(WIDTH//2 - 200, 15, 400, 55)
    title_bg = pygame.Surface((400, 55), pygame.SRCALPHA)
    for ty in range(55):
        alpha = int(180 - ty * 2)
        pygame.draw.line(title_bg, (20, 40, 60, alpha), (0, ty), (400, ty))
    screen.blit(title_bg, title_panel.topleft)
    pygame.draw.rect(screen, CYAN, title_panel, 2, border_radius=8)
    
    # 标题文字（动态发光）
    title_glow = int(255 * (0.8 + 0.2 * math.sin(t / 300)))
    title_color = (title_glow, title_glow, title_glow)
    title_font = pygame.font.SysFont("SimHei", 38)
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 32)
    gear_emoji = emoji_font.render("⚙️", True, CYAN)
    title_surf = title_font.render(" 系统设置 ", True, title_color)
    total_w = gear_emoji.get_width() + title_surf.get_width() + gear_emoji.get_width()
    start_x = WIDTH//2 - total_w//2
    screen.blit(gear_emoji, (start_x, 26))
    screen.blit(title_surf, (start_x + gear_emoji.get_width(), 22))
    screen.blit(gear_emoji, (start_x + gear_emoji.get_width() + title_surf.get_width(), 26))
    
    # 保存提示（浮动动画）
    if settings_saved_timer > 0:
        settings_saved_timer -= 1
        msg_alpha = min(255, settings_saved_timer * 8)
        msg_y = 78 - int(5 * math.sin(t / 100))
        msg_font = pygame.font.SysFont("SimHei", 22)
        msg_surf = msg_font.render(settings_saved_msg, True, LIME)
        msg_surf.set_alpha(msg_alpha)
        screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, msg_y))
    
    # ====== 主设置面板 ======
    panel_rect = pygame.Rect(WIDTH//2 - 460, 100, 920, HEIGHT - 190)
    panel_bg = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    for py in range(panel_rect.height):
        alpha = int(200 - py * 0.12)
        pygame.draw.line(panel_bg, (12, 18, 30, alpha), (0, py), (panel_rect.width, py))
    screen.blit(panel_bg, panel_rect.topleft)
    pygame.draw.rect(screen, (60, 90, 120), panel_rect, 2, border_radius=12)
    inner = panel_rect.inflate(-8, -8)
    pygame.draw.rect(screen, (30, 50, 70), inner, 1, border_radius=10)
    
    # ====== 音量设置区域 ======
    section_x = panel_rect.x + 40
    section_y = panel_rect.y + 25
    
    # 音量区域标题
    vol_title_rect = pygame.Rect(section_x, section_y, 350, 35)
    pygame.draw.rect(screen, (20, 50, 70, 180), vol_title_rect, border_radius=6)
    pygame.draw.rect(screen, CYAN, vol_title_rect, 1, border_radius=6)
    vol_font = pygame.font.SysFont("SimHei", 20)
    vol_emoji = pygame.font.SysFont("Segoe UI Emoji", 18)
    vol_icon = vol_emoji.render("🔊", True, CYAN)
    vol_text = vol_font.render(" 音量控制", True, CYAN)
    screen.blit(vol_icon, (section_x + 12, section_y + 7))
    screen.blit(vol_text, (section_x + 38, section_y + 6))
    
    start_y = section_y + 50
    slider_width = 380
    slider_height = 14
    
    volume_settings = [
        ("🎚️", "主音量", "master", sound_mgr.master_volume, CYAN, (0, 180, 220)),
        ("🎵", "音乐音量", "music", sound_mgr.music_volume, MAGENTA, (200, 50, 200)),
        ("🔔", "音效音量", "sfx", sound_mgr.sfx_volume, YELLOW, (220, 180, 0))
    ]
    
    for idx, (emoji, label, key, value, color, glow_color) in enumerate(volume_settings):
        y_pos = start_y + idx * 65
        
        # 标签背景卡片
        card_rect = pygame.Rect(section_x, y_pos - 5, slider_width + 120, 55)
        card_hover = card_rect.collidepoint(mx, my)
        card_bg_color = (25, 35, 50) if card_hover else (18, 25, 40)
        pygame.draw.rect(screen, card_bg_color, card_rect, border_radius=8)
        pygame.draw.rect(screen, color if card_hover else (60, 70, 90), card_rect, 1, border_radius=8)
        
        # Emoji和标签
        emoji_surf = vol_emoji.render(emoji, True, color)
        label_surf = vol_font.render(label, True, WHITE)
        screen.blit(emoji_surf, (section_x + 12, y_pos + 5))
        screen.blit(label_surf, (section_x + 42, y_pos + 5))
        
        # 滑块轨道
        track_rect = pygame.Rect(section_x + 15, y_pos + 32, slider_width, slider_height)
        pygame.draw.rect(screen, (30, 35, 45), track_rect, border_radius=7)
        
        # 进度条（渐变效果）
        progress_width = int(slider_width * value)
        if progress_width > 0:
            progress_surf = pygame.Surface((progress_width, slider_height), pygame.SRCALPHA)
            for px in range(progress_width):
                ratio = px / slider_width
                r = int(glow_color[0] * ratio + 40)
                g = int(glow_color[1] * ratio + 40)
                b = int(glow_color[2] * ratio + 40)
                pygame.draw.line(progress_surf, (r, g, b, 220), (px, 0), (px, slider_height))
            screen.blit(progress_surf, track_rect.topleft)
            # 发光边缘
            pygame.draw.rect(screen, color, pygame.Rect(track_rect.x, track_rect.y, progress_width, slider_height), 1, border_radius=7)
        
        # 滑块手柄
        handle_x = track_rect.x + progress_width
        handle_y = track_rect.centery
        handle_radius = 11
        
        is_hover = math.hypot(mx - handle_x, my - handle_y) < handle_radius + 5
        is_dragging = settings_dragging == key
        
        # 手柄外圈发光
        if is_hover or is_dragging:
            pygame.draw.circle(screen, (*color[:3], 80), (handle_x, handle_y), handle_radius + 6)
        
        # 手柄主体
        handle_color = WHITE if is_dragging else (color if is_hover else (180, 180, 180))
        pygame.draw.circle(screen, handle_color, (handle_x, handle_y), handle_radius)
        pygame.draw.circle(screen, WHITE, (handle_x, handle_y), handle_radius, 2)
        pygame.draw.circle(screen, color, (handle_x, handle_y), 5)  # 中心点
        
        # 百分比显示
        percentage = int(value * 100)
        pct_font = pygame.font.SysFont("Impact", 22)
        pct_surf = pct_font.render(f"{percentage}%", True, color)
        screen.blit(pct_surf, (section_x + slider_width + 45, y_pos + 18))
    
    # ====== 游戏设置区域（右侧）======
    right_x = panel_rect.x + 520
    right_y = panel_rect.y + 25
    
    # 游戏设置标题
    game_title_rect = pygame.Rect(right_x, right_y, 350, 35)
    pygame.draw.rect(screen, (50, 30, 20, 180), game_title_rect, border_radius=6)
    pygame.draw.rect(screen, ORANGE, game_title_rect, 1, border_radius=6)
    game_icon = vol_emoji.render("🎮", True, ORANGE)
    game_text = vol_font.render(" 游戏设置", True, ORANGE)
    screen.blit(game_icon, (right_x + 12, right_y + 7))
    screen.blit(game_text, (right_x + 38, right_y + 6))
    
    other_y = right_y + 50
    checkbox_size = 26
    label_font = pygame.font.SysFont("SimHei", 18)
    
    # 设置项列表
    checkbox_settings = [
        ("fps", "📊", "显示FPS计数器", game_settings.get("show_fps", True), CYAN),
        ("shake", "📳", "屏幕震动效果", game_settings.get("screen_shake", True), MAGENTA),
        ("damage", "💥", "显示伤害数字", game_settings.get("show_damage_numbers", True), YELLOW),
    ]
    
    checkboxes = {}
    for idx, (key, emoji, label, enabled, color) in enumerate(checkbox_settings):
        y_pos = other_y + idx * 45
        
        # 设置项卡片
        item_rect = pygame.Rect(right_x, y_pos - 5, 350, 40)
        item_hover = item_rect.collidepoint(mx, my)
        pygame.draw.rect(screen, (25, 30, 40) if item_hover else (18, 22, 32), item_rect, border_radius=6)
        pygame.draw.rect(screen, color if enabled else (50, 55, 65), item_rect, 1, border_radius=6)
        
        # 复选框
        cb_rect = pygame.Rect(right_x + 12, y_pos + 2, checkbox_size, checkbox_size)
        checkboxes[key] = cb_rect
        
        # 复选框背景
        cb_bg_color = (color[0]//4, color[1]//4, color[2]//4) if enabled else (30, 35, 45)
        pygame.draw.rect(screen, cb_bg_color, cb_rect, border_radius=5)
        pygame.draw.rect(screen, color if enabled else (70, 75, 85), cb_rect, 2, border_radius=5)
        
        # 勾选标记
        if enabled:
            pygame.draw.line(screen, color, (cb_rect.x + 6, cb_rect.centery), (cb_rect.centerx - 1, cb_rect.bottom - 6), 3)
            pygame.draw.line(screen, color, (cb_rect.centerx - 1, cb_rect.bottom - 6), (cb_rect.right - 5, cb_rect.y + 6), 3)
        
        # Emoji和标签
        emoji_surf = vol_emoji.render(emoji, True, color if enabled else GRAY)
        label_surf = label_font.render(label, True, WHITE if enabled else (120, 120, 130))
        screen.blit(emoji_surf, (cb_rect.right + 10, y_pos + 3))
        screen.blit(label_surf, (cb_rect.right + 38, y_pos + 7))
    
    # ====== 粒子效果质量 ======
    particle_y = other_y + 145
    particle_rect = pygame.Rect(right_x, particle_y - 5, 350, 75)
    pygame.draw.rect(screen, (18, 22, 32), particle_rect, border_radius=6)
    pygame.draw.rect(screen, (60, 70, 90), particle_rect, 1, border_radius=6)
    
    particle_icon = vol_emoji.render("✨", True, LIME)
    particle_label = label_font.render("粒子效果质量", True, WHITE)
    screen.blit(particle_icon, (right_x + 12, particle_y + 3))
    screen.blit(particle_label, (right_x + 40, particle_y + 5))
    
    particle_quality = game_settings.get("particle_quality", "high")
    quality_options = ["low", "medium", "high"]
    quality_names = {"low": "低", "medium": "中", "high": "高"}
    quality_colors = {"low": (100, 100, 100), "medium": YELLOW, "high": LIME}
    
    particle_btns = []
    for i, quality in enumerate(quality_options):
        btn_x = right_x + 15 + i * 110
        btn_rect = pygame.Rect(btn_x, particle_y + 35, 100, 30)
        particle_btns.append((btn_rect, quality))
        is_selected = (particle_quality == quality)
        is_hover = btn_rect.collidepoint(mx, my)
        
        btn_bg = quality_colors[quality] if is_selected else ((50, 55, 65) if is_hover else (30, 35, 45))
        if is_selected:
            btn_bg = (btn_bg[0]//3, btn_bg[1]//3, btn_bg[2]//3)
        pygame.draw.rect(screen, btn_bg, btn_rect, border_radius=5)
        pygame.draw.rect(screen, quality_colors[quality] if is_selected or is_hover else (60, 65, 75), btn_rect, 2, border_radius=5)
        
        btn_text = label_font.render(quality_names[quality], True, quality_colors[quality] if is_selected else (WHITE if is_hover else GRAY))
        screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width()//2, btn_rect.centery - btn_text.get_height()//2))
    
    # ====== 射击模式 ======
    fire_y = other_y + 230
    fire_rect = pygame.Rect(right_x, fire_y - 5, 350, 75)
    pygame.draw.rect(screen, (18, 22, 32), fire_rect, border_radius=6)
    pygame.draw.rect(screen, (60, 70, 90), fire_rect, 1, border_radius=6)
    
    fire_icon = vol_emoji.render("🔫", True, RED)
    fire_label = label_font.render("射击模式", True, WHITE)
    screen.blit(fire_icon, (right_x + 12, fire_y + 3))
    screen.blit(fire_label, (right_x + 40, fire_y + 5))
    
    auto_fire = game_settings.get("auto_fire", True)
    fire_options = [(True, "自动射击", LIME), (False, "手动(空格)", ORANGE)]
    
    fire_btns = []
    for i, (mode, name, color) in enumerate(fire_options):
        btn_x = right_x + 15 + i * 165
        btn_rect = pygame.Rect(btn_x, fire_y + 35, 155, 30)
        fire_btns.append((btn_rect, mode))
        is_selected = (auto_fire == mode)
        is_hover = btn_rect.collidepoint(mx, my)
        
        btn_bg = (color[0]//4, color[1]//4, color[2]//4) if is_selected else ((50, 55, 65) if is_hover else (30, 35, 45))
        pygame.draw.rect(screen, btn_bg, btn_rect, border_radius=5)
        pygame.draw.rect(screen, color if is_selected or is_hover else (60, 65, 75), btn_rect, 2, border_radius=5)
        
        btn_text = label_font.render(name, True, color if is_selected else (WHITE if is_hover else GRAY))
        screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width()//2, btn_rect.centery - btn_text.get_height()//2))
    
    # ====== 底部按钮区域 ======
    btn_y = HEIGHT - 75
    btn_width = 150
    btn_height = 48
    
    # 保存按钮
    save_btn = pygame.Rect(WIDTH//2 - btn_width - 120, btn_y, btn_width, btn_height)
    save_hover = save_btn.collidepoint(mx, my)
    save_bg = pygame.Surface((btn_width, btn_height), pygame.SRCALPHA)
    for by in range(btn_height):
        alpha = 200 - by * 2
        color = (0, 120 if save_hover else 80, 0)
        pygame.draw.line(save_bg, (*color, alpha), (0, by), (btn_width, by))
    screen.blit(save_bg, save_btn.topleft)
    pygame.draw.rect(screen, LIME if save_hover else (0, 150, 0), save_btn, 2, border_radius=8)
    if save_hover:
        pygame.draw.rect(screen, (100, 255, 100, 50), save_btn.inflate(4, 4), 2, border_radius=10)
    save_font = pygame.font.SysFont("SimHei", 20)
    save_icon = vol_emoji.render("💾", True, LIME)
    save_text = save_font.render(" 保存", True, WHITE)
    screen.blit(save_icon, (save_btn.centerx - 35, btn_y + 12))
    screen.blit(save_text, (save_btn.centerx - 10, btn_y + 12))
    
    # 恢复默认按钮
    reset_btn = pygame.Rect(WIDTH//2 - btn_width//2, btn_y, btn_width, btn_height)
    reset_hover = reset_btn.collidepoint(mx, my)
    reset_bg = pygame.Surface((btn_width, btn_height), pygame.SRCALPHA)
    for by in range(btn_height):
        alpha = 200 - by * 2
        color = (120 if reset_hover else 80, 100 if reset_hover else 60, 0)
        pygame.draw.line(reset_bg, (*color, alpha), (0, by), (btn_width, by))
    screen.blit(reset_bg, reset_btn.topleft)
    pygame.draw.rect(screen, YELLOW if reset_hover else (180, 150, 0), reset_btn, 2, border_radius=8)
    if reset_hover:
        pygame.draw.rect(screen, (255, 255, 100, 50), reset_btn.inflate(4, 4), 2, border_radius=10)
    reset_icon = vol_emoji.render("🔄", True, YELLOW)
    reset_text = save_font.render(" 重置", True, WHITE)
    screen.blit(reset_icon, (reset_btn.centerx - 35, btn_y + 12))
    screen.blit(reset_text, (reset_btn.centerx - 10, btn_y + 12))
    
    # 返回按钮
    back_btn = pygame.Rect(WIDTH//2 + 120, btn_y, btn_width, btn_height)
    back_hover = back_btn.collidepoint(mx, my)
    back_bg = pygame.Surface((btn_width, btn_height), pygame.SRCALPHA)
    for by in range(btn_height):
        alpha = 200 - by * 2
        color = (120 if back_hover else 80, 30, 30)
        pygame.draw.line(back_bg, (*color, alpha), (0, by), (btn_width, by))
    screen.blit(back_bg, back_btn.topleft)
    pygame.draw.rect(screen, RED if back_hover else (180, 50, 50), back_btn, 2, border_radius=8)
    if back_hover:
        pygame.draw.rect(screen, (255, 100, 100, 50), back_btn.inflate(4, 4), 2, border_radius=10)
    back_icon = vol_emoji.render("◀", True, RED)
    back_text = save_font.render(" 返回", True, WHITE)
    screen.blit(back_icon, (back_btn.centerx - 35, btn_y + 12))
    screen.blit(back_text, (back_btn.centerx - 10, btn_y + 12))
    
    # 返回UI元素引用
    return {
        'save': save_btn,
        'reset': reset_btn,
        'back': back_btn,
        'fps_checkbox': checkboxes['fps'],
        'shake_checkbox': checkboxes['shake'],
        'damage_checkbox': checkboxes['damage'],
        'particle_quality_btns': particle_btns,
        'fire_mode_btns': fire_btns,
        'sliders': [
            (pygame.Rect(section_x + 15, start_y + 0*65 + 32, slider_width, slider_height), 'master'),
            (pygame.Rect(section_x + 15, start_y + 1*65 + 32, slider_width, slider_height), 'music'),
            (pygame.Rect(section_x + 15, start_y + 2*65 + 32, slider_width, slider_height), 'sfx')
        ]
    }

def draw_arsenal_ui():
    """绘制武器库界面 - 精致典雅风格（放大版）"""
    global arsenal_selected_weapon_idx
    
    t = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    
    # ====== 深邃背景 ======
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(8 + ratio * 6)
        g = int(10 + ratio * 8)
        b = int(16 + ratio * 10)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    # 精致的装饰线条
    accent_gold = (180, 150, 90)
    accent_gold_dim = (90, 75, 45)
    
    # 顶部金色细线
    pygame.draw.line(screen, accent_gold_dim, (30, 58), (WIDTH - 30, 58), 1)
    pygame.draw.circle(screen, accent_gold, (30, 58), 3)
    pygame.draw.circle(screen, accent_gold, (WIDTH - 30, 58), 3)
    
    # ====== 标题 ======
    title_font = pygame.font.SysFont("SimHei", 32)
    title_surf = title_font.render("轨道武器库", True, (230, 225, 210))
    screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 15))
    
    # 标题下装饰
    title_w = title_surf.get_width()
    pygame.draw.line(screen, accent_gold, (WIDTH//2 - title_w//2 - 30, 52), (WIDTH//2 - 40, 52), 1)
    pygame.draw.line(screen, accent_gold, (WIDTH//2 + 40, 52), (WIDTH//2 + title_w//2 + 30, 52), 1)
    
    # 货币显示 - 右上角精致徽章
    cores = arsenal_save_data['currencies']['cores']
    chips = arsenal_save_data['currencies']['chips']
    
    # 核心徽章
    core_x = WIDTH - 220
    pygame.draw.polygon(screen, (20, 35, 45), [(core_x, 18), (core_x + 95, 18), (core_x + 88, 42), (core_x + 7, 42)])
    pygame.draw.polygon(screen, (60, 120, 140), [(core_x, 18), (core_x + 95, 18), (core_x + 88, 42), (core_x + 7, 42)], 1)
    curr_font = pygame.font.SysFont("SimHei", 14)
    core_label = curr_font.render("核心", True, (80, 140, 160))
    screen.blit(core_label, (core_x + 10, 23))
    core_val = pygame.font.SysFont("SimHei", 15).render(str(cores), True, (140, 200, 220))
    screen.blit(core_val, (core_x + 52, 22))
    
    # 芯片徽章
    chip_x = WIDTH - 115
    pygame.draw.polygon(screen, (35, 30, 20), [(chip_x, 18), (chip_x + 95, 18), (chip_x + 88, 42), (chip_x + 7, 42)])
    pygame.draw.polygon(screen, accent_gold_dim, [(chip_x, 18), (chip_x + 95, 18), (chip_x + 88, 42), (chip_x + 7, 42)], 1)
    chip_label = curr_font.render("芯片", True, accent_gold_dim)
    screen.blit(chip_label, (chip_x + 10, 23))
    chip_val = pygame.font.SysFont("SimHei", 15).render(str(chips), True, accent_gold)
    screen.blit(chip_val, (chip_x + 52, 22))
    
    # 消息提示
    if arsenal_msg_timer > 0:
        msg_font = pygame.font.SysFont("SimHei", 16)
        msg_surf = msg_font.render(arsenal_msg, True, (220, 120, 120))
        screen.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, 60))
    
    r = ARSENAL_UI
    weapons = arsenal_save_data["weapons"]
    
    # ====== 左栏：武器列表 ======
    list_area = r['list_area']
    
    # 面板背景
    panel_bg = pygame.Surface((list_area.width, list_area.height), pygame.SRCALPHA)
    for py in range(list_area.height):
        alpha = 225
        shade = int(12 + (py / list_area.height) * 4)
        pygame.draw.line(panel_bg, (shade, shade + 2, shade + 6, alpha), (0, py), (list_area.width, py))
    screen.blit(panel_bg, list_area.topleft)
    
    # 精致边框 - 双线效果
    pygame.draw.rect(screen, (25, 30, 40), list_area, 1)
    inner_rect = list_area.inflate(-4, -4)
    pygame.draw.rect(screen, (40, 50, 65), inner_rect, 1)
    
    # 顶部标题栏
    header_h = 38
    header_rect = pygame.Rect(list_area.x + 2, list_area.y + 2, list_area.width - 4, header_h)
    pygame.draw.rect(screen, (22, 28, 38), header_rect)
    pygame.draw.line(screen, accent_gold_dim, (header_rect.x, header_rect.bottom), (header_rect.right, header_rect.bottom), 1)
    
    header_font = pygame.font.SysFont("SimHei", 15)
    header_text = header_font.render(f"武器仓库", True, (160, 155, 140))
    screen.blit(header_text, (list_area.x + 18, list_area.y + 10))
    count_text = header_font.render(f"{len(weapons)}", True, accent_gold)
    screen.blit(count_text, (list_area.right - 35, list_area.y + 10))
    
    # 列表内容区
    list_inner = pygame.Rect(list_area.x + 3, list_area.y + header_h + 5, list_area.width - 10, list_area.height - header_h - 10)
    screen.set_clip(list_inner)
    
    item_height = 65
    start_y = list_inner.y - arsenal_scroll_y
    
    if not weapons:
        empty_font = pygame.font.SysFont("SimHei", 16)
        empty_surf = empty_font.render("暂无武器", True, (60, 65, 75))
        screen.blit(empty_surf, (list_area.centerx - empty_surf.get_width() // 2, list_area.centery))
    else:
        for i, w in enumerate(weapons):
            item_y = start_y + i * item_height
            
            if item_y + item_height < list_inner.top - 10 or item_y > list_inner.bottom + 10:
                continue
            
            item_rect = pygame.Rect(list_inner.x + 2, item_y, list_inner.width - 8, item_height - 5)
            info = WEAPON_TYPES[w['type']]
            is_sel = (i == arsenal_selected_weapon_idx)
            is_eq = (w in arsenal_save_data["loadout"])
            is_hov = item_rect.collidepoint(mx, my) and not is_sel
            
            # 卡片背景
            card_bg = pygame.Surface((item_rect.width, item_rect.height), pygame.SRCALPHA)
            if is_sel:
                for cy in range(item_rect.height):
                    ratio = cy / item_rect.height
                    cr = int(info['color'][0] * 0.12 + 18)
                    cg = int(info['color'][1] * 0.12 + 20)
                    cb = int(info['color'][2] * 0.12 + 28)
                    pygame.draw.line(card_bg, (cr, cg, cb, 250), (0, cy), (item_rect.width, cy))
            elif is_hov:
                for cy in range(item_rect.height):
                    pygame.draw.line(card_bg, (22, 26, 35, 240), (0, cy), (item_rect.width, cy))
            else:
                for cy in range(item_rect.height):
                    pygame.draw.line(card_bg, (16, 19, 26, 230), (0, cy), (item_rect.width, cy))
            screen.blit(card_bg, item_rect.topleft)
            
            # 边框
            if is_sel:
                pygame.draw.rect(screen, info['color'], item_rect, 1)
                pygame.draw.rect(screen, info['color'], (item_rect.x, item_rect.y + 5, 4, item_rect.height - 10))
            elif is_hov:
                pygame.draw.rect(screen, (55, 65, 80), item_rect, 1)
            
            # 武器图标 - 精致的菱形框
            icon_cx = item_rect.x + 32
            icon_cy = item_rect.centery
            icon_size = 18
            diamond = [(icon_cx, icon_cy - icon_size), (icon_cx + icon_size, icon_cy), 
                       (icon_cx, icon_cy + icon_size), (icon_cx - icon_size, icon_cy)]
            pygame.draw.polygon(screen, info['color'], diamond)
            pygame.draw.polygon(screen, (255, 255, 255, 80), diamond, 1)
            
            # 武器名称
            name_font = pygame.font.SysFont("SimHei", 17)
            name_col = (235, 230, 220) if is_sel else ((200, 195, 185) if is_hov else (140, 135, 125))
            name_surf = name_font.render(info['name'], True, name_col)
            screen.blit(name_surf, (item_rect.x + 58, item_rect.y + 10))
            
            # 星级 - 精致小菱形
            star_y = item_rect.y + 38
            for si in range(5):
                sx = item_rect.x + 62 + si * 16
                if si < w['stars']:
                    pts = [(sx, star_y - 5), (sx + 5, star_y), (sx, star_y + 5), (sx - 5, star_y)]
                    pygame.draw.polygon(screen, accent_gold, pts)
                else:
                    pts = [(sx, star_y - 4), (sx + 4, star_y), (sx, star_y + 4), (sx - 4, star_y)]
                    pygame.draw.polygon(screen, (40, 42, 50), pts)
            
            # 已装备标记
            if is_eq:
                eq_x = item_rect.right - 50
                eq_y = item_rect.centery - 8
                pygame.draw.rect(screen, (25, 50, 35), (eq_x, eq_y, 42, 18), border_radius=3)
                pygame.draw.rect(screen, (70, 130, 90), (eq_x, eq_y, 42, 18), 1, border_radius=3)
                eq_font = pygame.font.SysFont("SimHei", 11)
                eq_text = eq_font.render("装备中", True, (100, 180, 120))
                screen.blit(eq_text, (eq_x + 4, eq_y + 2))
                pygame.draw.rect(screen, (70, 130, 90), (eq_x, eq_y, 32, 14), 1, border_radius=2)
                eq_font = pygame.font.SysFont("SimHei", 9)
                eq_text = eq_font.render("装备中", True, (100, 180, 120))
                screen.blit(eq_text, (eq_x + 3, eq_y + 1))
    
    screen.set_clip(None)
    
    # 滚动条 - 精致细长
    total_h = len(weapons) * item_height
    view_h = list_inner.height
    if total_h > view_h:
        track_x = list_area.right - 8
        track_y = list_inner.y + 2
        track_h = list_inner.height - 4
        thumb_h = max(25, int(track_h * view_h / total_h))
        thumb_y = track_y + int((track_h - thumb_h) * arsenal_scroll_y / max(1, total_h - view_h))
        
        pygame.draw.rect(screen, (25, 30, 40), (track_x, track_y, 4, track_h), border_radius=2)
        pygame.draw.rect(screen, accent_gold_dim, (track_x, thumb_y, 4, thumb_h), border_radius=2)
    
    # ====== 中栏：装备配置 ======
    mid_x = 375
    
    # 区域标题
    sec_font = pygame.font.SysFont("SimHei", 13)
    sec_text = sec_font.render("装备配置", True, (160, 155, 140))
    screen.blit(sec_text, (mid_x, 88))
    pygame.draw.line(screen, accent_gold_dim, (mid_x + 70, 96), (mid_x + 255, 96), 1)
    pygame.draw.circle(screen, accent_gold, (mid_x + 255, 96), 2)
    
    slots = [r['slot_0'], r['slot_1'], r['slot_2']]
    slot_names = ["主武装", "副武装", "辅助系统"]
    
    for i, (slot_rect, sname) in enumerate(zip(slots, slot_names)):
        w = arsenal_save_data["loadout"][i]
        is_hov = slot_rect.collidepoint(mx, my)
        
        # 槽位背景 - 精致渐变
        slot_bg = pygame.Surface((slot_rect.width, slot_rect.height), pygame.SRCALPHA)
        for sy in range(slot_rect.height):
            ratio = sy / slot_rect.height
            shade = int(18 + ratio * 6)
            pygame.draw.line(slot_bg, (shade, shade + 2, shade + 4, 240), (0, sy), (slot_rect.width, sy))
        screen.blit(slot_bg, slot_rect.topleft)
        
        if w:
            info = WEAPON_TYPES[w['type']]
            # 左边武器色条
            pygame.draw.rect(screen, info['color'], (slot_rect.x, slot_rect.y, 4, slot_rect.height))
            border_col = (60, 70, 85) if not is_hov else (80, 90, 105)
        else:
            border_col = (40, 45, 55) if not is_hov else (55, 60, 70)
        
        # 双线边框
        pygame.draw.rect(screen, (25, 30, 40), slot_rect, 1)
        pygame.draw.rect(screen, border_col, slot_rect.inflate(-3, -3), 1)
        
        # 槽位标签
        label_font = pygame.font.SysFont("SimHei", 12)
        label_surf = label_font.render(f"[{chr(65+i)}] {sname}", True, (100, 95, 85))
        screen.blit(label_surf, (slot_rect.x + 10, slot_rect.y - 18))
        
        if w:
            info = WEAPON_TYPES[w['type']]
            
            # 武器图标 - 菱形
            icon_cx = slot_rect.x + 35
            icon_cy = slot_rect.centery
            diamond = [(icon_cx, icon_cy - 20), (icon_cx + 20, icon_cy), 
                       (icon_cx, icon_cy + 20), (icon_cx - 20, icon_cy)]
            pygame.draw.polygon(screen, info['color'], diamond)
            pygame.draw.polygon(screen, (255, 255, 255, 50), diamond, 1)
            
            # 武器名
            wname_font = pygame.font.SysFont("SimHei", 17)
            wname_surf = wname_font.render(info['name'], True, (220, 215, 205))
            screen.blit(wname_surf, (slot_rect.x + 65, slot_rect.y + 20))
            
            # 星级菱形
            for si in range(w['stars']):
                sx = slot_rect.x + 68 + si * 14
                sy = slot_rect.y + 55
                pts = [(sx, sy - 5), (sx + 5, sy), (sx, sy + 5), (sx - 5, sy)]
                pygame.draw.polygon(screen, accent_gold, pts)
            
            # 倍率
            mult = 1 + (w['stars'] - 1) * 0.3
            mult_font = pygame.font.SysFont("SimHei", 13)
            mult_surf = mult_font.render(f"×{mult:.1f}", True, (120, 160, 120))
            screen.blit(mult_surf, (slot_rect.right - 45, slot_rect.centery - 7))
        else:
            empty_font = pygame.font.SysFont("SimHei", 14)
            empty_surf = empty_font.render("- 空 -", True, (50, 55, 65))
            screen.blit(empty_surf, (slot_rect.centerx - empty_surf.get_width() // 2, slot_rect.centery - 8))
    
    # 研发区域
    research_y = HEIGHT - 148
    sec_text2 = sec_font.render("武器研发", True, (160, 155, 140))
    screen.blit(sec_text2, (mid_x, research_y))
    pygame.draw.line(screen, accent_gold_dim, (mid_x + 75, research_y + 8), (mid_x + 270, research_y + 8), 1)
    pygame.draw.circle(screen, accent_gold, (mid_x + 270, research_y + 8), 2)
    
    # 标准研发按钮
    btn_normal = r['btn_research_normal']
    hn = btn_normal.collidepoint(mx, my)
    can_normal = cores >= 20
    
    # 按钮渐变背景
    btn_bg = pygame.Surface((btn_normal.width, btn_normal.height), pygame.SRCALPHA)
    for by in range(btn_normal.height):
        ratio = by / btn_normal.height
        if can_normal:
            shade = int(30 + ratio * 8) if hn else int(22 + ratio * 6)
            pygame.draw.line(btn_bg, (shade - 5, shade, shade + 15, 245), (0, by), (btn_normal.width, by))
        else:
            shade = int(20 + ratio * 4)
            pygame.draw.line(btn_bg, (shade, shade, shade + 2, 230), (0, by), (btn_normal.width, by))
    screen.blit(btn_bg, btn_normal.topleft)
    
    border_n = (80, 100, 140) if can_normal else (45, 50, 60)
    pygame.draw.rect(screen, (25, 30, 40), btn_normal, 1)
    pygame.draw.rect(screen, border_n, btn_normal.inflate(-3, -3), 1)
    
    btn_font = pygame.font.SysFont("SimHei", 15)
    btn_text = btn_font.render("标准研发", True, (200, 200, 210) if can_normal else (80, 85, 95))
    screen.blit(btn_text, (btn_normal.x + btn_normal.width//2 - btn_text.get_width()//2, btn_normal.y + 12))
    cost_font = pygame.font.SysFont("SimHei", 12)
    cost_text = cost_font.render("消耗 20 核心", True, (100, 150, 180) if can_normal else (55, 60, 70))
    screen.blit(cost_text, (btn_normal.x + btn_normal.width//2 - cost_text.get_width()//2, btn_normal.y + 35))
    
    # 精密研发按钮
    btn_elite = r['btn_research_elite']
    he = btn_elite.collidepoint(mx, my)
    can_elite = chips >= 3
    
    btn_bg2 = pygame.Surface((btn_elite.width, btn_elite.height), pygame.SRCALPHA)
    for by in range(btn_elite.height):
        ratio = by / btn_elite.height
        if can_elite:
            shade = int(30 + ratio * 8) if he else int(24 + ratio * 6)
            pygame.draw.line(btn_bg2, (shade + 8, shade + 2, shade - 10, 245), (0, by), (btn_elite.width, by))
        else:
            shade = int(20 + ratio * 4)
            pygame.draw.line(btn_bg2, (shade + 2, shade, shade - 2, 230), (0, by), (btn_elite.width, by))
    screen.blit(btn_bg2, btn_elite.topleft)
    
    border_e = accent_gold_dim if can_elite else (45, 42, 38)
    pygame.draw.rect(screen, (30, 28, 25), btn_elite, 1)
    pygame.draw.rect(screen, border_e, btn_elite.inflate(-3, -3), 1)
    
    btn_text2 = btn_font.render("精密研发", True, (210, 200, 180) if can_elite else (85, 80, 70))
    screen.blit(btn_text2, (btn_elite.x + btn_elite.width//2 - btn_text2.get_width()//2, btn_elite.y + 12))
    cost_text2 = cost_font.render("消耗 3 芯片", True, accent_gold_dim if can_elite else (60, 55, 45))
    screen.blit(cost_text2, (btn_elite.x + btn_elite.width//2 - cost_text2.get_width()//2, btn_elite.y + 35))
    
    # ====== 右栏：武器详情 ======
    detail_area = r['detail_area']
    
    # 面板背景
    detail_bg = pygame.Surface((detail_area.width, detail_area.height), pygame.SRCALPHA)
    for dy in range(detail_area.height):
        ratio = dy / detail_area.height
        shade = int(14 + ratio * 5)
        pygame.draw.line(detail_bg, (shade, shade + 1, shade + 4, 235), (0, dy), (detail_area.width, dy))
    screen.blit(detail_bg, detail_area.topleft)
    
    # 双线边框
    pygame.draw.rect(screen, (25, 30, 40), detail_area, 1)
    pygame.draw.rect(screen, (45, 55, 70), detail_area.inflate(-4, -4), 1)
    
    if 0 <= arsenal_selected_weapon_idx < len(weapons):
        w = weapons[arsenal_selected_weapon_idx]
        info = WEAPON_TYPES[w['type']]
        
        # 顶部武器色条
        pygame.draw.rect(screen, info['color'], (detail_area.x + 2, detail_area.y + 2, detail_area.width - 4, 3))
        
        cx = detail_area.centerx
        base_y = detail_area.y
        
        # 武器图标区域 - 大号菱形
        icon_y = base_y + 85
        icon_size = 45
        
        # 外层装饰环
        outer_size = icon_size + 14
        outer_diamond = [(cx, icon_y - outer_size), (cx + outer_size, icon_y),
                         (cx, icon_y + outer_size), (cx - outer_size, icon_y)]
        pygame.draw.polygon(screen, (30, 35, 45), outer_diamond)
        pygame.draw.polygon(screen, (50, 60, 75), outer_diamond, 1)
        
        # 内层图标
        inner_diamond = [(cx, icon_y - icon_size), (cx + icon_size, icon_y),
                         (cx, icon_y + icon_size), (cx - icon_size, icon_y)]
        pygame.draw.polygon(screen, info['color'], inner_diamond)
        pygame.draw.polygon(screen, (255, 255, 255, 60), inner_diamond, 2)
        
        # 武器名称
        name_y = icon_y + icon_size + 28
        name_font = pygame.font.SysFont("SimHei", 24)
        name_surf = name_font.render(info['name'], True, (235, 230, 220))
        screen.blit(name_surf, (cx - name_surf.get_width() // 2, name_y))
        
        # 名称下装饰线
        line_w = name_surf.get_width() + 50
        pygame.draw.line(screen, accent_gold_dim, (cx - line_w//2, name_y + 35), (cx - 10, name_y + 35), 1)
        pygame.draw.line(screen, accent_gold_dim, (cx + 10, name_y + 35), (cx + line_w//2, name_y + 35), 1)
        pygame.draw.circle(screen, accent_gold, (cx, name_y + 35), 4)
        
        # 星级
        star_y = name_y + 58
        for si in range(5):
            sx = cx - 42 + si * 21
            if si < w['stars']:
                pts = [(sx, star_y - 8), (sx + 8, star_y), (sx, star_y + 8), (sx - 8, star_y)]
                pygame.draw.polygon(screen, accent_gold, pts)
                pygame.draw.polygon(screen, (255, 240, 180), pts, 1)
            else:
                pts = [(sx, star_y - 6), (sx + 6, star_y), (sx, star_y + 6), (sx - 6, star_y)]
                pygame.draw.polygon(screen, (35, 38, 48), pts)
                pygame.draw.polygon(screen, (55, 60, 70), pts, 1)
        
        # 属性区域
        stat_y = star_y + 32
        stat_rect = pygame.Rect(detail_area.x + 20, stat_y, detail_area.width - 40, 90)
        pygame.draw.rect(screen, (18, 22, 30), stat_rect)
        pygame.draw.rect(screen, (40, 48, 60), stat_rect, 1)
        
        stat_font = pygame.font.SysFont("SimHei", 14)
        mult = 1 + (w['stars'] - 1) * 0.3
        
        # 伤害
        pygame.draw.line(screen, (35, 40, 50), (stat_rect.x + 12, stat_y + 28), (stat_rect.right - 12, stat_y + 28), 1)
        dmg_label = stat_font.render("伤害倍率", True, (110, 105, 95))
        screen.blit(dmg_label, (stat_rect.x + 15, stat_y + 8))
        dmg_val = stat_font.render(f"×{mult:.2f}", True, (140, 180, 140))
        screen.blit(dmg_val, (stat_rect.right - 60, stat_y + 8))
        
        # 等级
        pygame.draw.line(screen, (35, 40, 50), (stat_rect.x + 12, stat_y + 56), (stat_rect.right - 12, stat_y + 56), 1)
        lvl_label = stat_font.render("强化等级", True, (110, 105, 95))
        screen.blit(lvl_label, (stat_rect.x + 15, stat_y + 34))
        lvl_val = stat_font.render(f"Lv.{w['stars']}", True, accent_gold)
        screen.blit(lvl_val, (stat_rect.right - 55, stat_y + 34))
        
        # 类型
        type_label = stat_font.render("武器类型", True, (110, 105, 95))
        screen.blit(type_label, (stat_rect.x + 15, stat_y + 62))
        type_val = stat_font.render(w['type'], True, info['color'])
        screen.blit(type_val, (stat_rect.right - 60, stat_y + 62))
        
        # 描述
        desc_y = stat_y + 105
        desc_font = pygame.font.SysFont("SimHei", 13)
        desc = info['desc']
        desc_lines = textwrap.wrap(desc, width=16)
        for di, dline in enumerate(desc_lines[:3]):
            dsurf = desc_font.render(dline, True, (120, 115, 105))
            screen.blit(dsurf, (detail_area.x + 25, desc_y + di * 20))
        
        # 升级按钮
        btn_upgrade = r['btn_upgrade']
        h_up = btn_upgrade.collidepoint(mx, my)
        cost = w['stars'] * 10
        can_up = cores >= cost and w['stars'] < 5
        
        # 按钮渐变
        up_bg = pygame.Surface((btn_upgrade.width, btn_upgrade.height), pygame.SRCALPHA)
        for uy in range(btn_upgrade.height):
            ratio = uy / btn_upgrade.height
            if can_up:
                shade = int(28 + ratio * 8) if h_up else int(22 + ratio * 6)
                pygame.draw.line(up_bg, (shade - 5, shade + 5, shade - 2, 245), (0, uy), (btn_upgrade.width, uy))
            elif w['stars'] >= 5:
                shade = int(25 + ratio * 5)
                pygame.draw.line(up_bg, (shade + 5, shade + 3, shade - 5, 230), (0, uy), (btn_upgrade.width, uy))
            else:
                shade = int(20 + ratio * 4)
                pygame.draw.line(up_bg, (shade, shade, shade, 220), (0, uy), (btn_upgrade.width, uy))
        screen.blit(up_bg, btn_upgrade.topleft)
        
        if w['stars'] >= 5:
            border_up = accent_gold_dim
            pygame.draw.rect(screen, (35, 32, 25), btn_upgrade, 1)
        elif can_up:
            border_up = (80, 130, 90)
            pygame.draw.rect(screen, (25, 35, 30), btn_upgrade, 1)
        else:
            border_up = (50, 50, 55)
            pygame.draw.rect(screen, (25, 28, 32), btn_upgrade, 1)
        pygame.draw.rect(screen, border_up, btn_upgrade.inflate(-3, -3), 1)
        
        up_font = pygame.font.SysFont("SimHei", 15)
        if w['stars'] >= 5:
            up_text = up_font.render("已达满级", True, accent_gold)
            screen.blit(up_text, (btn_upgrade.centerx - up_text.get_width() // 2, btn_upgrade.centery - 9))
        else:
            up_text = up_font.render("升级强化", True, (200, 210, 200) if can_up else (90, 90, 95))
            screen.blit(up_text, (btn_upgrade.centerx - up_text.get_width() // 2, btn_upgrade.y + 12))
            up_cost = cost_font.render(f"消耗 {cost} 核心", True, (100, 160, 120) if can_up else (65, 70, 75))
            screen.blit(up_cost, (btn_upgrade.centerx - up_cost.get_width() // 2, btn_upgrade.y + 34))
    else:
        hint_font = pygame.font.SysFont("SimHei", 15)
        hint_surf = hint_font.render("选择武器查看详情", True, (70, 75, 85))
        screen.blit(hint_surf, (detail_area.centerx - hint_surf.get_width() // 2, detail_area.centery - 10))
    
    # ====== 返回按钮 ======
    btn_back = r['btn_back']
    hb = btn_back.collidepoint(mx, my)
    
    back_bg = pygame.Surface((btn_back.width, btn_back.height), pygame.SRCALPHA)
    for by in range(btn_back.height):
        ratio = by / btn_back.height
        shade = int(28 + ratio * 6) if hb else int(20 + ratio * 5)
        pygame.draw.line(back_bg, (shade + 5, shade - 2, shade - 2, 240), (0, by), (btn_back.width, by))
    screen.blit(back_bg, btn_back.topleft)
    
    pygame.draw.rect(screen, (30, 25, 25), btn_back, 1)
    pygame.draw.rect(screen, (100, 70, 70) if hb else (65, 50, 50), btn_back.inflate(-3, -3), 1)
    
    back_font = pygame.font.SysFont("SimHei", 14)
    back_surf = back_font.render("返回", True, (180, 175, 170) if hb else (130, 125, 120))
    screen.blit(back_surf, (btn_back.centerx - back_surf.get_width() // 2, btn_back.centery - 8))

def draw_background_settings_ui():
    """背景设置界面 - 使用当前装备的背景"""
    global background_settings_page
    
    t = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    
    # ====== 使用当前装备的背景 ======
    bg_manager.draw(screen)
    
    # 添加半透明遮罩让UI更清晰
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))
    
    # 边框装饰
    glow_intensity = int(80 + 40 * math.sin(t / 400))
    border_color = (glow_intensity // 2, glow_intensity, int(glow_intensity * 1.3))
    pygame.draw.rect(screen, border_color, (0, 0, WIDTH, 2))
    pygame.draw.rect(screen, border_color, (0, HEIGHT - 2, WIDTH, 2))
    
    # 角落霓虹装饰
    corner_size = 40
    for corner in [(0, 0, 1, 1), (WIDTH, 0, -1, 1), (0, HEIGHT, 1, -1), (WIDTH, HEIGHT, -1, -1)]:
        cx, cy, dx, dy = corner
        pygame.draw.line(screen, CYAN, (cx, cy + dy * 3), (cx, cy + dy * corner_size), 2)
        pygame.draw.line(screen, CYAN, (cx + dx * 3, cy), (cx + dx * corner_size, cy), 2)
    
    # ====== 豪华标题区 ======
    title_panel = pygame.Rect(WIDTH//2 - 180, 12, 360, 50)
    title_bg = pygame.Surface((360, 50), pygame.SRCALPHA)
    for ty in range(50):
        alpha = int(180 - ty * 2.5)
        pygame.draw.line(title_bg, (15, 40, 60, alpha), (0, ty), (360, ty))
    screen.blit(title_bg, title_panel.topleft)
    pygame.draw.rect(screen, CYAN, title_panel, 2, border_radius=8)
    
    # 标题动态发光
    title_glow = int(255 * (0.8 + 0.2 * math.sin(t / 300)))
    title_color = (title_glow // 2, title_glow, title_glow)
    
    title_font = pygame.font.SysFont("SimHei", 34)
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 28)
    icon_l = emoji_font.render("🎨", True, CYAN)
    title_surf = title_font.render(" 背景设置 ", True, title_color)
    icon_r = emoji_font.render("🖼️", True, CYAN)
    total_w = icon_l.get_width() + title_surf.get_width() + icon_r.get_width()
    start_x = WIDTH//2 - total_w//2
    screen.blit(icon_l, (start_x, 22))
    screen.blit(title_surf, (start_x + icon_l.get_width(), 20))
    screen.blit(icon_r, (start_x + icon_l.get_width() + title_surf.get_width(), 22))
    
    # 获取背景数据
    from systems import BackgroundManager
    bg_styles = BackgroundManager.BG_STYLES
    bg_list = list(bg_styles.items())
    
    # 分页配置
    cards_per_row = 4
    rows_per_page = 2
    cards_per_page = cards_per_row * rows_per_page
    total_pages = (len(bg_list) + cards_per_page - 1) // cards_per_page
    background_settings_page = max(0, min(background_settings_page, total_pages - 1))
    
    # 页码指示器（豪华版）
    page_indicator_rect = pygame.Rect(WIDTH//2 - 80, 70, 160, 28)
    pygame.draw.rect(screen, (20, 35, 50), page_indicator_rect, border_radius=14)
    pygame.draw.rect(screen, (60, 100, 140), page_indicator_rect, 1, border_radius=14)
    
    page_font = pygame.font.SysFont("SimHei", 16)
    page_text = page_font.render(f"◀  {background_settings_page + 1} / {total_pages}  ▶", True, CYAN)
    screen.blit(page_text, (page_indicator_rect.centerx - page_text.get_width()//2, 
                           page_indicator_rect.centery - page_text.get_height()//2))
    
    # 获取当前页数据
    page_start = background_settings_page * cards_per_page
    page_end = min(page_start + cards_per_page, len(bg_list))
    page_items = bg_list[page_start:page_end]
    
    # ====== 背景卡片区域 ======
    card_w = 270
    card_h = 195
    gap = 25
    start_x = (WIDTH - (cards_per_row * card_w + (cards_per_row - 1) * gap)) // 2
    start_y = 110
    
    for local_idx, (style_key, style_data) in enumerate(page_items):
        global_idx = page_start + local_idx
        row = local_idx // cards_per_row
        col = local_idx % cards_per_row
        
        x = start_x + col * (card_w + gap)
        y = start_y + row * (card_h + gap)
        
        card_rect = pygame.Rect(x, y, card_w, card_h)
        is_selected = (bg_manager.current_style == style_key)
        is_hover = card_rect.collidepoint(mx, my) and not is_selected
        is_keyboard_selected = (global_idx == background_settings_selected)
        
        # 卡片背景（带渐变）
        card_bg = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        if is_selected:
            for cy in range(card_h):
                alpha = int(200 - cy * 0.5)
                pygame.draw.line(card_bg, (30, 80, 120, alpha), (0, cy), (card_w, cy))
        elif is_keyboard_selected:
            for cy in range(card_h):
                alpha = int(180 - cy * 0.5)
                pygame.draw.line(card_bg, (60, 50, 20, alpha), (0, cy), (card_w, cy))
        elif is_hover:
            for cy in range(card_h):
                alpha = int(160 - cy * 0.4)
                pygame.draw.line(card_bg, (40, 50, 60, alpha), (0, cy), (card_w, cy))
        else:
            for cy in range(card_h):
                alpha = int(140 - cy * 0.3)
                pygame.draw.line(card_bg, (20, 25, 35, alpha), (0, cy), (card_w, cy))
        screen.blit(card_bg, (x, y))
        
        # 卡片边框
        if is_selected:
            pygame.draw.rect(screen, CYAN, card_rect, 3, border_radius=10)
            # 发光效果
            glow_rect = card_rect.inflate(6, 6)
            pygame.draw.rect(screen, (0, 150, 200, 80), glow_rect, 2, border_radius=12)
        elif is_keyboard_selected:
            pygame.draw.rect(screen, YELLOW, card_rect, 3, border_radius=10)
        elif is_hover:
            pygame.draw.rect(screen, (120, 140, 160), card_rect, 2, border_radius=10)
        else:
            pygame.draw.rect(screen, (50, 60, 80), card_rect, 1, border_radius=10)
        
        # 预览区域
        preview_rect = pygame.Rect(x + 10, y + 10, card_w - 20, 115)
        preview_surf = pygame.Surface((preview_rect.width, preview_rect.height))
        preview_surf.fill(style_data["base_color"])
        
        # 绘制预览元素
        elements = style_data.get("elements", {})
        star_count = elements.get("stars", 0)
        if star_count > 0:
            random.seed(global_idx)  # 固定随机种子使预览一致
            for _ in range(min(40, star_count // 4)):
                sx = random.randint(0, preview_rect.width)
                sy = random.randint(0, preview_rect.height)
                pygame.draw.circle(preview_surf, (180, 180, 200), (sx, sy), 1)
        
        if elements.get("grid", False) and style_data.get("grid_color"):
            grid_color = style_data["grid_color"]
            for gx in range(0, preview_rect.width, 30):
                pygame.draw.line(preview_surf, (*grid_color[:3], 60), (gx, 0), (gx, preview_rect.height), 1)
            for gy in range(0, preview_rect.height, 30):
                pygame.draw.line(preview_surf, (*grid_color[:3], 60), (0, gy), (preview_rect.width, gy), 1)
        
        screen.blit(preview_surf, preview_rect.topleft)
        pygame.draw.rect(screen, (60, 80, 100), preview_rect, 1, border_radius=5)
        
        # 背景名称
        name_font = pygame.font.SysFont("SimHei", 20)
        name_color = CYAN if is_selected else (YELLOW if is_keyboard_selected else WHITE)
        name_surf = name_font.render(style_data["name"], True, name_color)
        screen.blit(name_surf, (card_rect.centerx - name_surf.get_width()//2, y + 135))
        
        # 选中状态标记
        if is_selected:
            status_font = pygame.font.SysFont("SimHei", 14)
            check_emoji = emoji_font.render("✓", True, LIME)
            status_text = status_font.render(" 使用中", True, LIME)
            total_w = check_emoji.get_width() + status_text.get_width()
            screen.blit(check_emoji, (card_rect.centerx - total_w//2, y + 162))
            screen.blit(status_text, (card_rect.centerx - total_w//2 + check_emoji.get_width(), y + 168))
    
    # ====== 翻页按钮 ======
    button_y = start_y + rows_per_page * (card_h + gap) + 20
    button_w = 120
    button_h = 45
    
    # 上一页按钮
    prev_btn = pygame.Rect(60, button_y, button_w, button_h)
    if background_settings_page > 0:
        prev_hover = prev_btn.collidepoint(mx, my)
        prev_bg = pygame.Surface((button_w, button_h), pygame.SRCALPHA)
        for by in range(button_h):
            alpha = 180 - by * 2
            color = (40, 80, 100) if prev_hover else (25, 50, 70)
            pygame.draw.line(prev_bg, (*color, alpha), (0, by), (button_w, by))
        screen.blit(prev_bg, prev_btn.topleft)
        pygame.draw.rect(screen, CYAN if prev_hover else (60, 120, 160), prev_btn, 2, border_radius=8)
        
        prev_font = pygame.font.SysFont("SimHei", 18)
        prev_icon = emoji_font.render("◀", True, CYAN if prev_hover else WHITE)
        prev_text = prev_font.render(" 上一页", True, WHITE)
        screen.blit(prev_icon, (prev_btn.centerx - 40, button_y + 10))
        screen.blit(prev_text, (prev_btn.centerx - 20, button_y + 12))
    else:
        pygame.draw.rect(screen, (25, 30, 40), prev_btn, border_radius=8)
        pygame.draw.rect(screen, (50, 55, 65), prev_btn, 1, border_radius=8)
        prev_font = pygame.font.SysFont("SimHei", 18)
        prev_text = prev_font.render("◀ 上一页", True, (80, 85, 95))
        screen.blit(prev_text, (prev_btn.centerx - prev_text.get_width()//2, button_y + 12))
    
    # 下一页按钮
    next_btn = pygame.Rect(WIDTH - 60 - button_w, button_y, button_w, button_h)
    if background_settings_page < total_pages - 1:
        next_hover = next_btn.collidepoint(mx, my)
        next_bg = pygame.Surface((button_w, button_h), pygame.SRCALPHA)
        for by in range(button_h):
            alpha = 180 - by * 2
            color = (40, 80, 100) if next_hover else (25, 50, 70)
            pygame.draw.line(next_bg, (*color, alpha), (0, by), (button_w, by))
        screen.blit(next_bg, next_btn.topleft)
        pygame.draw.rect(screen, CYAN if next_hover else (60, 120, 160), next_btn, 2, border_radius=8)
        
        next_font = pygame.font.SysFont("SimHei", 18)
        next_text = next_font.render("下一页 ", True, WHITE)
        next_icon = emoji_font.render("▶", True, CYAN if next_hover else WHITE)
        screen.blit(next_text, (next_btn.centerx - 35, button_y + 12))
        screen.blit(next_icon, (next_btn.centerx + 20, button_y + 10))
    else:
        pygame.draw.rect(screen, (25, 30, 40), next_btn, border_radius=8)
        pygame.draw.rect(screen, (50, 55, 65), next_btn, 1, border_radius=8)
        next_font = pygame.font.SysFont("SimHei", 18)
        next_text = next_font.render("下一页 ▶", True, (80, 85, 95))
        screen.blit(next_text, (next_btn.centerx - next_text.get_width()//2, button_y + 12))
    
    # ====== 操作提示 ======
    tip_font = pygame.font.SysFont("SimHei", 14)
    tip_text = tip_font.render("● 点击卡片切换背景  |  ◆ 方向键导航  |  ◇ Enter确认  |  ● 滚轮翻页", True, (100, 110, 130))
    screen.blit(tip_text, (WIDTH//2 - tip_text.get_width()//2, HEIGHT - 100))
    
    # ====== 返回按钮 ======
    back_btn = pygame.Rect(WIDTH//2 - 70, HEIGHT - 70, 140, 45)
    back_hover = back_btn.collidepoint(mx, my)
    
    back_bg = pygame.Surface((140, 45), pygame.SRCALPHA)
    for by in range(45):
        alpha = 180 - by * 2
        color = (100, 40, 40) if back_hover else (60, 30, 30)
        pygame.draw.line(back_bg, (*color, alpha), (0, by), (140, by))
    screen.blit(back_bg, back_btn.topleft)
    pygame.draw.rect(screen, RED if back_hover else (150, 60, 60), back_btn, 2, border_radius=8)
    if back_hover:
        pygame.draw.rect(screen, (200, 80, 80, 50), back_btn.inflate(4, 4), 2, border_radius=10)
    
    back_font = pygame.font.SysFont("SimHei", 18)
    back_icon = emoji_font.render("◀", True, RED if back_hover else WHITE)
    back_text = back_font.render(" 返回", True, WHITE)
    screen.blit(back_icon, (back_btn.centerx - 30, back_btn.centery - 12))
    screen.blit(back_text, (back_btn.centerx - 5, back_btn.centery - 10))

def draw_codex_ui():
    """绘制机密档案界面 - 赛博朋克风格"""
    r = CODEX_UI
    mx, my = pygame.mouse.get_pos()
    t = pygame.time.get_ticks()
    
    # ====== 背景 ======
    screen.fill((8, 12, 22))
    
    # 动态网格背景
    grid_alpha = int(20 + 10 * math.sin(t / 1000))
    for gx in range(0, WIDTH, 60):
        pygame.draw.line(screen, (0, grid_alpha, grid_alpha * 2), (gx, 0), (gx, HEIGHT), 1)
    for gy in range(0, HEIGHT, 60):
        pygame.draw.line(screen, (0, grid_alpha, grid_alpha * 2), (0, gy), (WIDTH, gy), 1)
    
    # 扫描线效果
    scan_y = (t // 20) % HEIGHT
    pygame.draw.line(screen, (0, 60, 80, 100), (0, scan_y), (WIDTH, scan_y), 2)
    
    # 角落装饰
    corner_size = 30
    corner_color = (0, 150, 200)
    # 左上
    pygame.draw.lines(screen, corner_color, False, [(0, corner_size), (0, 0), (corner_size, 0)], 2)
    # 右上
    pygame.draw.lines(screen, corner_color, False, [(WIDTH - corner_size, 0), (WIDTH - 1, 0), (WIDTH - 1, corner_size)], 2)
    # 左下
    pygame.draw.lines(screen, corner_color, False, [(0, HEIGHT - corner_size), (0, HEIGHT - 1), (corner_size, HEIGHT - 1)], 2)
    # 右下
    pygame.draw.lines(screen, corner_color, False, [(WIDTH - corner_size, HEIGHT - 1), (WIDTH - 1, HEIGHT - 1), (WIDTH - 1, HEIGHT - corner_size)], 2)
    
    # ====== 标题区 ======
    title_glow = int(200 + 55 * math.sin(t / 500))
    # 标题背景条
    title_bar = pygame.Rect(0, 10, WIDTH, 50)
    title_bg = pygame.Surface((WIDTH, 50), pygame.SRCALPHA)
    pygame.draw.rect(title_bg, (0, 40, 60, 150), (0, 0, WIDTH, 50))
    screen.blit(title_bg, (0, 10))
    pygame.draw.line(screen, (0, title_glow, title_glow), (50, 60), (WIDTH - 50, 60), 2)
    
    # 标题文字 - 分开渲染符号和文字
    codex_title_emoji = pygame.font.SysFont("Segoe UI Emoji", 28)
    codex_title_text = pygame.font.SysFont("SimHei", 36)
    codex_icon_l = codex_title_emoji.render("◆", True, (0, title_glow, title_glow))
    codex_title = codex_title_text.render(" 机密档案 ", True, (0, title_glow, title_glow))
    codex_icon_r = codex_title_emoji.render("◆", True, (0, title_glow, title_glow))
    codex_total_w = codex_icon_l.get_width() + codex_title.get_width() + codex_icon_r.get_width()
    codex_start_x = WIDTH//2 - codex_total_w//2
    screen.blit(codex_icon_l, (codex_start_x, 24))
    screen.blit(codex_title, (codex_start_x + codex_icon_l.get_width(), 20))
    screen.blit(codex_icon_r, (codex_start_x + codex_icon_l.get_width() + codex_title.get_width(), 24))
    
    # ====== 标签栏 ======
    tab_width = 140
    tab_height = 42
    tab_y = 75
    tab_start_x = WIDTH//2 - (tab_width * 3 + 30) // 2
    
    tab_configs = [
        ("机体数据", CYAN),
        ("领主图鉴", RED),
        ("敌人图鉴", ORANGE)
    ]
    
    for i, (label, color) in enumerate(tab_configs):
        tab_rect = pygame.Rect(tab_start_x + i * (tab_width + 15), tab_y, tab_width, tab_height)
        is_selected = (codex_tab == i)
        is_hover = tab_rect.collidepoint(mx, my)
        
        # 标签背景
        if is_selected:
            bg_color = (color[0]//4, color[1]//4, color[2]//4)
            draw_cyber_rect(screen, tab_rect, bg_color, alpha=220, fill=True)
            draw_cyber_rect(screen, tab_rect, color, border_width=2, fill=False)
            # 底部高亮条
            pygame.draw.line(screen, color, (tab_rect.left + 5, tab_rect.bottom - 2), 
                           (tab_rect.right - 5, tab_rect.bottom - 2), 3)
        else:
            bg_color = (25, 30, 40) if is_hover else (18, 22, 32)
            draw_cyber_rect(screen, tab_rect, bg_color, alpha=200, fill=True)
            draw_cyber_rect(screen, tab_rect, (60, 70, 80) if is_hover else (40, 50, 60), border_width=1, fill=False)
        
        # 标签文字
        text_color = color if is_selected else (GRAY if not is_hover else WHITE)
        draw_text(screen, label, 18, tab_rect.centerx, tab_rect.centery - 8, text_color)
        
        # 保存标签矩形
        if i == 0: r['tab_plane'] = tab_rect
        elif i == 1: r['tab_boss'] = tab_rect
        else: r['tab_enemy'] = tab_rect

    def _enemy_preview(enemy_id: str, color: tuple) -> pygame.Surface:
        """使用真实敌人渲染逻辑生成图鉴预览。"""
        try:
            t = pygame.time.get_ticks() * 0.06
            return build_enemy_preview_surface(enemy_id, t=t, box=180, color_override=color)
        except Exception:
            fallback = pygame.Surface((180, 180), pygame.SRCALPHA)
            pygame.draw.circle(fallback, color, (90, 90), 26, 2)
            return fallback
    
    # ====== 数据准备 ======
    if codex_tab == 0:
        keys = plane_keys
        db = PLANES
        color_theme = CYAN
        theme_name = "机体"
    elif codex_tab == 1:
        keys = list(BOSS_DB.keys())
        db = BOSS_DB
        color_theme = RED
        theme_name = "领主"
    else:
        from enemy_manager import enemy_type_manager
        enemy_data = enemy_type_manager.get_regular_types()
        keys = [e["id"] for e in enemy_data]
        db = {e["id"]: e for e in enemy_data}
        color_theme = ORANGE
        theme_name = "敌人"

    # ====== 左侧列表区 ======
    list_rect = r['list_view']
    
    # 列表标题
    list_title_rect = pygame.Rect(list_rect.x, list_rect.y - 30, list_rect.width, 28)
    draw_cyber_rect(screen, list_title_rect, (color_theme[0]//6, color_theme[1]//6, color_theme[2]//6), alpha=200, fill=True)
    draw_text(screen, f"◇ {theme_name}列表 ({len(keys)})", 14, list_title_rect.centerx, list_title_rect.y + 5, color_theme)
    
    # 列表背景
    draw_cyber_rect(screen, list_rect, (12, 16, 24), alpha=240, fill=True)
    draw_cyber_rect(screen, list_rect, (40, 50, 65), border_width=1, fill=False)
    
    # 列表内容
    screen.set_clip(list_rect)
    start_y = list_rect.y + 8 - codex_scroll_y
    item_h = 48
    
    for i, key in enumerate(keys):
        y = start_y + i * item_h
        if y + item_h < list_rect.top or y > list_rect.bottom: 
            continue
            
        item_rect = pygame.Rect(list_rect.x + 6, y, list_rect.width - 12, item_h - 4)
        is_sel = (i == codex_idx)
        is_hover = item_rect.collidepoint(mx, my) and not is_sel
        
        if is_sel:
            # 选中项 - 发光边框
            sel_bg = (color_theme[0]//5, color_theme[1]//5, color_theme[2]//5)
            draw_cyber_rect(screen, item_rect, sel_bg, alpha=220, fill=True)
            draw_cyber_rect(screen, item_rect, color_theme, border_width=2, fill=False)
            # 左侧指示条
            pygame.draw.rect(screen, color_theme, (item_rect.x, item_rect.y + 4, 4, item_rect.height - 8))
        elif is_hover:
            draw_cyber_rect(screen, item_rect, (35, 40, 55), alpha=180, fill=True)
            draw_cyber_rect(screen, item_rect, (70, 80, 100), border_width=1, fill=False)
        
        # 序号
        idx_color = color_theme if is_sel else (60, 70, 85)
        draw_text(screen, f"{i+1:02d}", 12, item_rect.x + 20, item_rect.y + 12, idx_color)
        
        # 名称
        name_color = WHITE if is_sel else (GRAY if not is_hover else (200, 200, 210))
        draw_text(screen, db[key]["name"], 16, item_rect.x + 50, item_rect.y + 10, name_color, align="left")
        
    screen.set_clip(None)
    
    # 滚动条
    if len(keys) * item_h > list_rect.height:
        scroll_height = list_rect.height - 10
        content_height = len(keys) * item_h
        thumb_height = max(30, int(scroll_height * list_rect.height / content_height))
        thumb_y = list_rect.y + 5 + int((scroll_height - thumb_height) * codex_scroll_y / (content_height - list_rect.height))
        
        # 滚动条轨道
        pygame.draw.rect(screen, (30, 35, 45), (list_rect.right - 8, list_rect.y + 5, 4, scroll_height), border_radius=2)
        # 滚动条滑块
        pygame.draw.rect(screen, color_theme, (list_rect.right - 8, thumb_y, 4, thumb_height), border_radius=2)

    # ====== 右侧详情区 ======
    detail_rect = r['detail_area']
    
    # 详情区标题
    detail_title_rect = pygame.Rect(detail_rect.x, detail_rect.y - 30, detail_rect.width, 28)
    draw_cyber_rect(screen, detail_title_rect, (color_theme[0]//6, color_theme[1]//6, color_theme[2]//6), alpha=200, fill=True)
    draw_text(screen, "◆ 详细资料", 14, detail_title_rect.centerx, detail_title_rect.y + 5, color_theme)
    
    # 详情区背景
    draw_cyber_rect(screen, detail_rect, (10, 14, 22), alpha=240, fill=True)
    draw_cyber_rect(screen, detail_rect, color_theme, border_width=1, fill=False)
    
    # 内边框装饰
    inner_rect = detail_rect.inflate(-20, -20)
    pygame.draw.rect(screen, (color_theme[0]//4, color_theme[1]//4, color_theme[2]//4), inner_rect, 1)
    
    if 0 <= codex_idx < len(keys):
        key = keys[codex_idx]
        data = db[key]
        cx = detail_rect.centerx
        cy = detail_rect.y + 60
        
        # 预览图区域背景
        preview_bg_rect = pygame.Rect(cx - 90, cy - 10, 180, 180)
        pygame.draw.rect(screen, (20, 25, 35), preview_bg_rect, border_radius=8)
        pygame.draw.rect(screen, (color_theme[0]//3, color_theme[1]//3, color_theme[2]//3), preview_bg_rect, 2, border_radius=8)
        
        # 绘制预览图
        if codex_tab == 0:
            preview = get_plane_surf(key, PLANES.get(key, {}).get('visual', None))
        elif codex_tab == 1:
            preview = get_boss_surf(key, data["color"])
        else:
            enemy_color = tuple(data.get("color", (200, 100, 100)))
            preview = _enemy_preview(key, enemy_color)
        
        if codex_tab != 2:
            preview = pygame.transform.scale(preview, (150, 150))

        pw, ph = preview.get_width(), preview.get_height()
        safe_blit(screen, preview, (cx - pw // 2, cy + 5))

        # 名称区
        name_y = cy + 180
        # 名称背景条
        name_bg = pygame.Rect(detail_rect.x + 20, name_y - 5, detail_rect.width - 40, 40)
        pygame.draw.rect(screen, (color_theme[0]//6, color_theme[1]//6, color_theme[2]//6), name_bg, border_radius=4)
        
        entity_color = data.get("color", color_theme)
        draw_text(screen, data["name"], 28, cx, name_y + 5, entity_color, glow=True)
        
        # 描述区
        desc = data.get("desc", "")
        desc_lines = 0
        if desc:
            max_chars_per_line = 38
            lines = []
            for i in range(0, len(desc), max_chars_per_line):
                lines.append(desc[i:i+max_chars_per_line])
            
            desc_start = name_y + 50
            desc_lines = len(lines)
            for idx, line in enumerate(lines):
                draw_text(screen, line, 14, cx, desc_start + idx * 24, (180, 190, 200))
        
        # 属性区
        stats = []
        if codex_tab == 0:
            stats = [("生命", data["hp"], 200, LIME), ("速度", data["speed"]*10, 100, CYAN), ("火力", data["damage"]*2, 200, ORANGE)]
        elif codex_tab == 1:
            stats = [(k, v, 100, color_theme) for k,v in data["stats"]]
        else:
            stats = [
                ("生命", data.get("hp", 50), 300, LIME),
                ("速度", int(data.get("speed", 2) * 20), 100, CYAN),
                ("威胁", data.get("threat_level", 1), 5, RED)
            ]
        
        stat_spacing = 38
        desc_offset = desc_lines * 24 if desc_lines else 0
        stats_base = name_y + 80 + desc_offset
        
        # 属性标题
        draw_text(screen, "— 属性数据 —", 12, cx, stats_base - 15, (80, 90, 110))
        
        for j, stat_data in enumerate(stats):
            if len(stat_data) == 4:
                lbl, val, mxv, stat_color = stat_data
            else:
                lbl, val, mxv = stat_data
                stat_color = color_theme
                
            y_off = stats_base + j * stat_spacing + 10
            
            # 属性标签
            draw_text(screen, lbl, 16, detail_rect.x + 80, y_off, WHITE, align="left")
            
            # 属性条背景
            bar_x = detail_rect.x + 140
            bar_w = 200
            pygame.draw.rect(screen, (30, 35, 45), (bar_x, y_off + 4, bar_w, 14), border_radius=3)
            
            # 属性条填充
            fill = min(bar_w, int((val / mxv) * bar_w))
            if fill > 0:
                fill_rect = pygame.Rect(bar_x, y_off + 4, fill, 14)
                pygame.draw.rect(screen, stat_color, fill_rect, border_radius=3)
                # 高光
                pygame.draw.line(screen, (255, 255, 255, 100), (bar_x + 2, y_off + 6), (bar_x + fill - 2, y_off + 6), 1)
            
            # 数值
            draw_text(screen, str(int(val)), 14, bar_x + bar_w + 30, y_off, stat_color)
        
        # 敌人图鉴额外显示分数
        if codex_tab == 2:
            score_y = stats_base + len(stats) * stat_spacing + 20
            draw_text(screen, f"击杀分数: {data.get('score', 100)}", 16, cx, score_y, GOLD)

    # ====== 返回按钮 ======
    back_btn = r['btn_back']
    hb = back_btn.collidepoint(mx, my)
    
    if hb:
        draw_cyber_rect(screen, back_btn, (60, 30, 30), alpha=220, fill=True)
        draw_cyber_rect(screen, back_btn, RED, border_width=2, fill=False)
        btn_text_color = WHITE
    else:
        draw_cyber_rect(screen, back_btn, (30, 30, 40), alpha=200, fill=True)
        draw_cyber_rect(screen, back_btn, (80, 80, 100), border_width=1, fill=False)
        btn_text_color = GRAY
    
    draw_text(screen, "返回", 18, back_btn.centerx, back_btn.centery - 8, btn_text_color)

def draw_gallery_ui():
    """绘制战术图鉴界面 - 赛博朋克风格"""
    mx, my = pygame.mouse.get_pos()
    t = pygame.time.get_ticks()
    
    # ====== 背景 ======
    screen.fill((8, 12, 22))
    
    # 动态网格背景
    grid_alpha = int(20 + 10 * math.sin(t / 1000))
    for gx in range(0, WIDTH, 60):
        pygame.draw.line(screen, (grid_alpha, 0, grid_alpha * 2), (gx, 0), (gx, HEIGHT), 1)
    for gy in range(0, HEIGHT, 60):
        pygame.draw.line(screen, (grid_alpha, 0, grid_alpha * 2), (0, gy), (WIDTH, gy), 1)
    
    # 扫描线效果
    scan_y = (t // 25) % HEIGHT
    pygame.draw.line(screen, (80, 0, 60, 100), (0, scan_y), (WIDTH, scan_y), 2)
    
    # 角落装饰
    corner_size = 30
    corner_color = (200, 0, 150)
    pygame.draw.lines(screen, corner_color, False, [(0, corner_size), (0, 0), (corner_size, 0)], 2)
    pygame.draw.lines(screen, corner_color, False, [(WIDTH - corner_size, 0), (WIDTH - 1, 0), (WIDTH - 1, corner_size)], 2)
    pygame.draw.lines(screen, corner_color, False, [(0, HEIGHT - corner_size), (0, HEIGHT - 1), (corner_size, HEIGHT - 1)], 2)
    pygame.draw.lines(screen, corner_color, False, [(WIDTH - corner_size, HEIGHT - 1), (WIDTH - 1, HEIGHT - 1), (WIDTH - 1, HEIGHT - corner_size)], 2)
    
    # ====== 标题区 ======
    title_glow = int(200 + 55 * math.sin(t / 500))
    title_bar = pygame.Rect(0, 10, WIDTH, 50)
    title_bg = pygame.Surface((WIDTH, 50), pygame.SRCALPHA)
    pygame.draw.rect(title_bg, (40, 0, 60, 150), (0, 0, WIDTH, 50))
    screen.blit(title_bg, (0, 10))
    pygame.draw.line(screen, (title_glow, 0, title_glow), (50, 60), (WIDTH - 50, 60), 2)
    
    title_font = pygame.font.SysFont("SimHei", 36)
    title_surf = title_font.render("◆ 战术图鉴 ◆", True, (title_glow, 0, title_glow))
    screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 20))
    
    # ====== 标签栏 ======
    tab_labels = ["全部", "1★", "2★", "3★", "4★", "5★", "6★"]
    tab_colors = [WHITE, (150, 150, 150), (100, 200, 255), (200, 100, 255), (255, 200, 50), (255, 100, 200), (255, 255, 255)]
    tab_w = 95
    tab_h = 38
    start_tx = (WIDTH - (7 * tab_w + 60)) // 2
    
    for i, lbl in enumerate(tab_labels):
        rect = pygame.Rect(start_tx + i*(tab_w+10), 75, tab_w, tab_h)
        is_sel = (i == gallery_tab)
        is_hover = rect.collidepoint(mx, my)
        c = tab_colors[i]
        
        if is_sel:
            bg_color = (c[0]//5, c[1]//5, c[2]//5)
            draw_cyber_rect(screen, rect, bg_color, alpha=220, fill=True)
            draw_cyber_rect(screen, rect, c, border_width=2, fill=False)
            pygame.draw.line(screen, c, (rect.left + 5, rect.bottom - 2), (rect.right - 5, rect.bottom - 2), 3)
        else:
            bg_color = (30, 25, 40) if is_hover else (20, 18, 30)
            draw_cyber_rect(screen, rect, bg_color, alpha=200, fill=True)
            draw_cyber_rect(screen, rect, (70, 60, 80) if is_hover else (45, 40, 55), border_width=1, fill=False)
        
        text_color = c if is_sel else (GRAY if not is_hover else WHITE)
        draw_text(screen, lbl, 16, rect.centerx, rect.centery - 8, text_color)

    # 加载肉鸽卡牌数据
    from roguelite import BASE_CARDS, MODIFIER_CARDS, SYNERGY_RULES
    all_cards = []
    for key, card in BASE_CARDS.items():
        all_cards.append({"id": key, "name": card["name"], "rarity": card["rarity"], 
                        "desc": card.get("desc", ""), "type": "base", "data": card})
    for key, card in MODIFIER_CARDS.items():
        all_cards.append({"id": key, "name": card["name"], "rarity": card["rarity"],
                        "desc": card.get("desc", ""), "type": "modifier", "data": card})
    for key, synergy in SYNERGY_RULES.items():
        all_cards.append({"id": key, "name": synergy["name"], "rarity": synergy["rarity"],
                        "desc": synergy.get("desc", ""), "type": "synergy", "data": synergy})
    
    if gallery_tab == 0: 
        items = all_cards
    else: 
        items = [it for it in all_cards if it['rarity'] == gallery_tab]
    
    # ====== 卡牌网格 ======
    start_y = 130
    cols = 3
    card_w = 360
    card_h = 180
    gap = 30
    start_gx = (WIDTH - (cols*card_w + (cols-1)*gap)) // 2
    
    items_per_page = 6
    start_idx = gallery_page * items_per_page
    end_idx = min(start_idx + items_per_page, len(items))
    
    if not items: 
        draw_text(screen, "暂无相关数据", 28, WIDTH//2, HEIGHT//2, GRAY)
        draw_text(screen, "请选择其他分类", 18, WIDTH//2, HEIGHT//2 + 40, (80, 80, 100))
    
    for i in range(start_idx, end_idx):
        item = items[i]
        rel_i = i - start_idx
        r = rel_i // cols
        c = rel_i % cols
        x = start_gx + c * (card_w + gap)
        y = start_y + r * (card_h + gap)
        rect = pygame.Rect(x, y, card_w, card_h)
        rc = RARITY_COLORS[item['rarity']]
        
        # 卡牌背景 - 渐变效果
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        for j in range(card_h):
            alpha = int(220 - j / card_h * 50)
            grad_color = (rc[0]//10, rc[1]//10, rc[2]//10, alpha)
            pygame.draw.rect(card_surf, grad_color, (0, j, card_w, 1))
        screen.blit(card_surf, (x, y))
        
        # 卡牌边框
        draw_cyber_rect(screen, rect, rc, border_width=2, fill=False)
        
        # 顶部标题栏
        title_bar_rect = pygame.Rect(x+2, y+2, card_w-4, 42)
        pygame.draw.rect(screen, (*rc, 100), title_bar_rect, border_radius=4)
        pygame.draw.line(screen, rc, (x + 10, y + 44), (x + card_w - 10, y + 44), 1)
        
        # 卡牌名称和品质星级
        stars = "★" * item['rarity']
        draw_text(screen, item['name'], 22, x+15, y+12, WHITE, align="left", glow=True)
        draw_text(screen, stars, 18, x+card_w-15, y+14, rc, align="right")
        
        # 卡牌类型和信息
        if "data" in item:
            type_label = {"base": "基础", "modifier": "参数", "synergy": "协同"}.get(item["type"], "")
            type_bg = pygame.Rect(x + 10, y + 50, 50, 20)
            pygame.draw.rect(screen, (*rc, 80), type_bg, border_radius=3)
            draw_text(screen, type_label, 13, type_bg.centerx, type_bg.y + 2, rc)
            
            card_data = item["data"]
            info_parts = []
            
            if "category" in card_data:
                category_names = {
                    "attack": "攻击", "defense": "防御", 
                    "special": "特殊", "system": "系统",
                    "control": "控制", "summon": "召唤", "utility": "辅助"
                }
                cat_cn = category_names.get(card_data["category"], card_data["category"])
                info_parts.append(cat_cn)
            
            if "archetype" in card_data:
                archetype_names = {
                    "barrage": "弹幕流", "sniper": "狙击流",
                    "control": "控制流", "summon": "召唤流"
                }
                arch_cn = archetype_names.get(card_data["archetype"], card_data["archetype"])
                info_parts.append(arch_cn)
            
            if "type" in card_data and item["type"] == "modifier":
                type_names = {"numeric": "数值", "trait": "特性"}
                type_cn = type_names.get(card_data["type"], card_data["type"])
                info_parts.append(type_cn)
            
            if info_parts:
                info_text = " · ".join(info_parts)
                draw_text(screen, info_text, 13, x+70, y+52, (160, 160, 180))
            
            # 显示效果 - 属性名全面汉化（包含所有76张卡牌的属性）
            attr_names = {
                # 基础属性
                "bullet_count": "弹幕", "damage_mult": "伤害", "speed_mult": "速度",
                "split_count": "分裂", "split_damage": "分裂伤", "pierce": "穿透",
                "fire_rate": "射速", "fire_rate_mult": "射速倍率",
                "explosion_radius": "爆炸范围", "explosion_mult": "爆炸伤害",
                "slow_duration": "减速时长", "freeze_chance": "冻结率", "hp_mult": "生命",
                "shield": "护盾", "armor": "护甲", "dodge_chance": "闪避率",
                "regen_rate": "回复", "drone_count": "无人机", "drone_damage": "无人机伤害",
                "crit_chance": "暴击率", "crit_mult": "暴击伤害", "lifesteal": "吸血",
                "projectile_speed": "弹速", "range_mult": "射程", "cooldown_reduction": "冷却",
                "shield_amount": "护盾值", "shield_regen": "护盾回复", "damage_reduction": "减伤",
                "max_hp_bonus": "最大生命", "regen_interval": "回复间隔", "slow_mult": "减速",
                "pull_strength": "吸引", "radius": "范围", "slow_area": "减速区域",
                "time_factor": "时间因子", "chain_count": "连锁数", "chain_damage": "连锁伤害",
                "freeze_duration": "冻结时长", "freeze_radius": "冻结范围", "chaos_chance": "混沌率",
                "chaos_mult": "混沌倍率", "turret_count": "炮塔数", "turret_damage": "炮塔伤害",
                "magnet_range": "吸引范围", "xp_mult": "经验倍率", "homing": "追踪",
                "homing_strength": "追踪强度", "explosion": "爆炸", "chain": "连锁",
                "chain_targets": "连锁目标", "pierce_bonus": "穿透加成", "duration_mult": "持续时长",
                "control_range_mult": "控制范围", "spread_angle": "散射角度", 
                "summon_count": "召唤数", "summon_damage_mult": "召唤伤害", 
                "summon_count_mult": "召唤倍率", "summon_ai": "AI模式",
                "bullet_count_mult": "弹幕倍率", "all_bullets_explode": "全弹爆炸",
                "infinite_pierce": "无限穿透", "slow_on_hit": "击中减速", "global_slow": "全局减速",
                "split_level": "分裂层数",
                # 弹幕流专属
                "bounce_count": "反弹", "bounce_damage": "反弹伤害",
                "cluster_count": "子弹药", "cluster_radius": "子弹药范围", "cluster_damage_mult": "子弹药伤害",
                "storm_duration": "风暴时长", "storm_bullets": "风暴弹幕", "storm_damage_mult": "风暴伤害",
                # 狙击流专属
                "overcharge_cooldown": "超载冷却", "overcharge_mult": "超载倍率", "overcharge_pierce": "超载穿透",
                "weakpoint_chance": "弱点率", "weakpoint_mult": "弱点倍率",
                "armor_pen": "破甲", "bonus_vs_armor": "对装甲加成",
                "railgun_explosion": "轨道爆炸",
                "mark_duration": "标记时长", "mark_crit_mult": "标记倍率", "mark_chain": "标记传染",
                "execute_threshold": "处决阈值", "execute_mult": "处决倍率", "execute_instant_kill": "秒杀",
                "focus_per_sec": "专注速度", "max_focus": "最大专注", "focus_crit": "专注暴击",
                # 控制流专属
                "time_freeze_chance": "冻结几率", "freeze_shatter": "碎冰伤害",
                "thorns_damage": "反伤",
                "regen_combat": "战斗回复",
                "dodge_invulnerable": "闪避无敌",
                "stasis_duration": "静滞时长", "stasis_radius": "静滞范围", "stasis_damage_amp": "静滞易伤",
                "barrier_hp": "屏障值", "barrier_recharge": "屏障充能", "barrier_reflect": "屏障反射",
                # 召唤流专属
                "turret_laser": "激光炮",
                "drone_kamikaze": "无人机自爆",
                "magnet_instant": "瞬吸",
                "strike_damage": "打击伤害", "strike_cooldown": "打击冷却", "strike_count": "打击次数",
                "heal_per_sec": "回复/秒", "aura_radius": "光环范围", "heal_damage_boost": "治疗加伤",
                "revive_hp": "复活生命", "revive_cooldown": "复活冷却", "revive_invulnerable": "复活无敌",
                "minion_count": "召唤物", "minion_hp": "召唤物生命", "minion_damage": "召唤物伤害", "minion_evolve": "召唤物进化",
                "station_buff": "支援增益", "station_radius": "支援范围", "station_repair": "支援修复",
                # 修饰符专属
                "efficiency_mult": "效率倍率",
                "all_stats_mult": "全属性", "cooldown_penalty": "冷却惩罚", "cooldown_mult": "冷却倍率",
                "burn": "燃烧", "burn_dps": "燃烧伤害", "burn_duration": "燃烧时长",
                "poison": "剧毒", "poison_dps": "中毒伤害", "poison_duration": "中毒时长",
                "knockback": "击退", "knockback_force": "击退力度",
                "multishot": "多重射击",
                "recursive": "递归", "recursive_chance": "递归几率",
                # 协同效果专属
                "bullet_count_bonus": "弹幕加成",
                "bullet_size": "弹幕大小",
                "recursive_split": "递归分裂", "split_damage_mult": "分裂伤害",
                "focus_permanent": "永久专注",
                "boss_damage_mult": "对Boss伤害",
                "execute_instant": "即死",
                "shield_mult": "护盾倍率", "speed_penalty": "移速惩罚",
                "regen_mult": "回复倍率", "auto_revive": "自动复活",
                "freeze_duration_mult": "冻结倍率", "shatter_mult": "碎冰倍率",
                "drone_damage_mult": "无人机伤害",
                "strike_cooldown_mult": "打击冷却", "strike_damage_mult": "打击伤害",
                "revive_enemy_chance": "复生几率", "revived_hp": "复生生命",
                "swarm_synergy": "集群协同", "max_swarm_bonus": "最大集群加成",
                "all_lifesteal": "全体吸血", "lifesteal_mult": "吸血倍率",
                "all_elements": "全元素", "element_damage_mult": "元素伤害",
                "max_hp_mult": "最大生命倍率"
            }
            
            # 解析效果
            desc_lines = []
            if "base_effect" in card_data:
                effect = card_data["base_effect"]
                for k, v in list(effect.items())[:3]:
                    cn_name = attr_names.get(k, k)
                    if isinstance(v, bool):
                        if v:
                            desc_lines.append(cn_name)
                    elif isinstance(v, (int, float)):
                        if "mult" in k or "chance" in k or k.endswith("_mult"):
                            if v >= 1:
                                desc_lines.append(f"{cn_name}+{int((v-1)*100)}%")
                            else:
                                desc_lines.append(f"{cn_name}×{v:.1f}")
                        else:
                            desc_lines.append(f"{cn_name}+{v}")
            elif "effect" in card_data:
                effect = card_data["effect"]
                if isinstance(effect, dict):
                    for k, v in list(effect.items())[:3]:
                        cn_name = attr_names.get(k, k)
                        if isinstance(v, bool):
                            if v:
                                desc_lines.append(cn_name)
                        elif isinstance(v, (int, float)):
                            if "mult" in k or "chance" in k:
                                if v >= 1:
                                    desc_lines.append(f"{cn_name}+{int((v-1)*100)}%")
                                else:
                                    desc_lines.append(f"{cn_name}×{v:.1f}")
                            else:
                                desc_lines.append(f"{cn_name}+{v}")
            
            # 显示效果信息（弹幕+、伤害+等）
            if desc_lines:
                effect_y = y+130
                effect_text = " ".join(desc_lines[:3])  # 最多显示3个效果
                lines = [effect_text[k:k+24] for k in range(0, len(effect_text), 24)][:2]
                for k, line in enumerate(lines):
                    draw_text(screen, line, 15, x+15, effect_y+k*20, (150, 220, 255), align="left")
            
            # 卡牌描述 - 更大更清晰
            desc = item.get('desc', '')
            if desc:
                # 分行显示描述
                lines = [desc[k:k+22] for k in range(0, len(desc), 22)][:2]
                for k, line in enumerate(lines):
                    draw_text(screen, line, 16, x+15, y+95+k*22, (200, 200, 220), align="left")
            
            # 【修改】不再自动悬停，由点击触发
            
            # 显示升级信息（基础卡）
            if item["type"] == "base" and "upgrades" in card_data and card_data["upgrades"]:
                upgrade_info = f"可升级至Lv.{len(card_data['upgrades']) + 1}"
                draw_text(screen, upgrade_info, 13, x+15, y+card_h-25, (100, 255, 150), align="left")
            
            # 显示协同触发条件（协同卡）
            if item["type"] == "synergy" and "trigger" in card_data:
                trigger = card_data["trigger"]
                if "archetype" in trigger and "count" in trigger:
                    arch_names = {"barrage": "弹幕", "sniper": "狙击", "control": "控制", "summon": "召唤"}
                    arch = arch_names.get(trigger["archetype"], trigger["archetype"])
                    trigger_text = f"需要{trigger['count']}张{arch}卡"
                    draw_text(screen, trigger_text, 13, x+15, y+card_h-25, (255, 220, 100), align="left")

    # 【新】Tooltip详细信息面板 - 大字体优化版
    if gallery_hover_card:
        # 预先导入，避免在循环中重复导入
        from roguelite import BASE_CARDS, MODIFIER_CARDS
        
        tooltip_h = 420  # 更高以容纳大字体
        tooltip_rect = pygame.Rect(20, HEIGHT - tooltip_h - 60, WIDTH - 40, tooltip_h)
        # 半透明背景
        tooltip_surf = pygame.Surface((tooltip_rect.width, tooltip_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(tooltip_surf, (5, 10, 20, 250), (0, 0, tooltip_rect.width, tooltip_rect.height), border_radius=15)
        screen.blit(tooltip_surf, (tooltip_rect.x, tooltip_rect.y))
        
        # 边框颜色根据稀有度 - 加粗
        rarity_idx = gallery_hover_card['rarity']
        # RARITY_COLORS: [WHITE(0全部), 1星, 2星, 3星, 4星, 5星, 6星]
        # rarity 值 1-6 直接对应索引 1-6
        if 0 <= rarity_idx < len(RARITY_COLORS):
            rarity_color = RARITY_COLORS[rarity_idx]
        else:
            rarity_color = CYAN
        pygame.draw.rect(screen, rarity_color, tooltip_rect, 4, border_radius=15)
        
        # 标题区域 - 带背景条
        title_bg = pygame.Rect(tooltip_rect.x + 10, tooltip_rect.y + 10, tooltip_rect.width - 20, 50)
        pygame.draw.rect(screen, (*rarity_color[:3], 60), title_bg, border_radius=10)
        pygame.draw.rect(screen, rarity_color, title_bg, 2, border_radius=10)
        
        # 标题行 - 更大更醒目
        title_y = tooltip_rect.y + 28
        card_name = gallery_hover_card['name']
        # RARITY_NAMES: ["全部", "1星普通", "2星稀有", "3星史诗", "4星传说", "5星神话", "6星至高"]
        # rarity 值 1-6 需要加 0（因为索引 0 是"全部"，索引 1-6 是 1-6 星）
        # 实际上 rarity=1 应该用索引 1，所以直接用 rarity 值即可
        rarity_idx = gallery_hover_card['rarity']
        if 0 < rarity_idx < len(RARITY_NAMES):
            card_rarity = RARITY_NAMES[rarity_idx]
        else:
            card_rarity = f"{rarity_idx}星"
        card_type = {"base": "基础", "modifier": "参数", "synergy": "协同"}.get(gallery_hover_card['type'], "")
        draw_text(screen, card_name, 28, tooltip_rect.centerx - 150, title_y, WHITE, glow=True, align="left")
        draw_text(screen, f"[{card_rarity}]", 20, tooltip_rect.centerx + 80, title_y, rarity_color, align="left")
        draw_text(screen, f"<{card_type}>", 18, tooltip_rect.centerx + 200, title_y, (180, 180, 200), align="left")
        
        # 完整描述 - 更大字体
        desc = gallery_hover_card.get('desc', '')
        desc_y = tooltip_rect.y + 75
        desc_lines = [desc[k:k+70] for k in range(0, len(desc), 70)][:2]
        for line in desc_lines:
            draw_text(screen, line, 18, tooltip_rect.x + 25, desc_y, (230, 230, 250), align="left")
            desc_y += 26
        
        # 分隔线
        line_y = desc_y + 8
        pygame.draw.line(screen, rarity_color, (tooltip_rect.x + 20, line_y), (tooltip_rect.right - 20, line_y), 2)
        
        # 三栏布局
        col_width = (tooltip_rect.width - 80) // 3
        left_x = tooltip_rect.x + 30
        mid_x = left_x + col_width + 20
        right_x = mid_x + col_width + 20
        content_y = line_y + 15
        
        # === 左栏：基础属性 ===
        if 'data' in gallery_hover_card:
            card_data = gallery_hover_card['data']
            
            # 左栏标题
            draw_text(screen, "▌基础属性", 19, left_x, content_y, CYAN, align="left", glow=True)
            attr_y = content_y + 30
            
            # 显示所有属性 - 大字体清晰显示
            effect = card_data.get('base_effect') or card_data.get('effect', {})
            if isinstance(effect, dict):
                attr_count = 0
                for k, v in effect.items():
                    if attr_y > tooltip_rect.y + tooltip_rect.height - 25:  # 防止溢出
                        break
                    cn_name = attr_names.get(k, k)
                    if isinstance(v, bool):
                        if v:
                            draw_text(screen, f"✓ {cn_name}", 16, left_x, attr_y, (150, 255, 150), align="left")
                            attr_y += 24
                            attr_count += 1
                    elif isinstance(v, (int, float)):
                        if 'mult' in k or 'chance' in k:
                            val_text = f"+{int((v-1)*100)}%" if v >= 1 else f"×{v:.1f}"
                        else:
                            val_text = f"+{v}"
                        draw_text(screen, f"{cn_name}", 15, left_x, attr_y, (180, 180, 200), align="left")
                        draw_text(screen, val_text, 16, left_x + 120, attr_y, (100, 220, 255), align="left", glow=True)
                        attr_y += 24
                        attr_count += 1
                    elif isinstance(v, str):
                        draw_text(screen, f"{cn_name}: {v}", 15, left_x, attr_y, (255, 220, 150), align="left")
                        attr_y += 24
                        attr_count += 1
                
                if attr_count == 0:
                    draw_text(screen, "（无数值效果）", 15, left_x, attr_y, GRAY, align="left")
            
            # === 中栏：升级路径/触发条件 ===
            if gallery_hover_card['type'] == 'base':
                draw_text(screen, "▌升级路径", 19, mid_x, content_y, (255, 200, 100), align="left", glow=True)
            elif gallery_hover_card['type'] == 'synergy':
                draw_text(screen, "▌触发条件", 19, mid_x, content_y, (255, 150, 255), align="left", glow=True)
            else:
                draw_text(screen, "▌使用说明", 19, mid_x, content_y, (150, 200, 255), align="left", glow=True)
            
            upgrade_y = content_y + 30
            
            # 基础卡：显示升级路径
            if gallery_hover_card['type'] == 'base' and 'upgrades' in card_data:
                upgrades = card_data['upgrades']
                for i, upgrade in enumerate(upgrades[:10]):  # 显示所有升级
                    if upgrade_y > tooltip_rect.y + tooltip_rect.height - 25:
                        break
                    level = i + 2  # 从Lv.2开始
                    upgrade_desc = upgrade.get('desc', '')
                    
                    # 等级标签 - 更大更醒目
                    level_color = (80 + i * 25, 180, 255 - i * 15)
                    draw_text(screen, f"Lv{level}", 15, mid_x, upgrade_y, level_color, align="left", glow=True)
                    
                    # 升级效果 - 大字体
                    effect_text = upgrade_desc[:28]
                    draw_text(screen, effect_text, 14, mid_x + 42, upgrade_y, (220, 230, 245), align="left")
                    upgrade_y += 24
            
            # 协同卡：显示触发条件
            elif gallery_hover_card['type'] == 'synergy' and 'trigger' in card_data:
                trigger = card_data['trigger']
                
                # 流派要求
                if 'archetype' in trigger:
                    arch_names = {"barrage": "弹幕流", "sniper": "狙击流", "control": "控制流", "summon": "召唤流", "all": "全流派"}
                    arch = arch_names.get(trigger['archetype'], trigger['archetype'])
                    
                    # 兼容 count 和 archetypes_count 两种格式
                    if 'archetypes_count' in trigger:
                        # 需要多个不同流派
                        count = trigger['archetypes_count']
                        draw_text(screen, f"需要拥有 {count} 个", 16, mid_x, upgrade_y, (200, 200, 220), align="left")
                        upgrade_y += 24
                        draw_text(screen, "不同流派的卡牌", 16, mid_x, upgrade_y, (255, 220, 100), align="left", glow=True)
                        upgrade_y += 28
                    elif 'count' in trigger:
                        # 需要指定数量的某流派卡牌
                        count = trigger['count']
                        draw_text(screen, f"需要 {count} 张", 16, mid_x, upgrade_y, (200, 200, 220), align="left")
                        draw_text(screen, arch, 17, mid_x + 90, upgrade_y, (255, 220, 100), align="left", glow=True)
                        upgrade_y += 28
                
                # 特定卡牌要求
                if 'cards' in trigger and trigger['cards']:
                    draw_text(screen, "需要特定卡牌:", 15, mid_x, upgrade_y, (255, 180, 100), align="left")
                    upgrade_y += 24
                    for card_id in trigger['cards'][:6]:
                        if upgrade_y > tooltip_rect.y + tooltip_rect.height - 25:
                            break
                        card_name = BASE_CARDS.get(card_id, {}).get('name', card_id)
                        draw_text(screen, f"· {card_name}", 14, mid_x + 10, upgrade_y, (210, 210, 230), align="left")
                        upgrade_y += 22
                
                # 修饰符要求
                if 'modifiers' in trigger and trigger['modifiers']:
                    draw_text(screen, "需要修饰符:", 15, mid_x, upgrade_y, (255, 180, 100), align="left")
                    upgrade_y += 24
                    for mod_id in trigger['modifiers'][:4]:
                        if upgrade_y > tooltip_rect.y + tooltip_rect.height - 25:
                            break
                        mod_name = MODIFIER_CARDS.get(mod_id, {}).get('name', mod_id)
                        draw_text(screen, f"· {mod_name}", 14, mid_x + 10, upgrade_y, (210, 210, 230), align="left")
                        upgrade_y += 22
            
            # 参数卡：显示类型和效果说明
            elif gallery_hover_card['type'] == 'modifier':
                mod_type = card_data.get('type', '')
                type_names = {"numeric": "数值型", "trait": "特性型"}
                type_name = type_names.get(mod_type, mod_type)
                draw_text(screen, f"类型: {type_name}", 16, mid_x, upgrade_y, (200, 220, 255), align="left")
                upgrade_y += 28
                
                draw_text(screen, "可修饰基础卡牌", 15, mid_x, upgrade_y, (200, 200, 220), align="left")
                upgrade_y += 24
                draw_text(screen, "改变数值或添加特性", 14, mid_x, upgrade_y, GRAY, align="left")
            
            # === 右栏：流派与分类信息 ===
            draw_text(screen, "▌卡牌信息", 19, right_x, content_y, (150, 255, 200), align="left", glow=True)
            info_y = content_y + 30
            
            # 流派标签
            if 'archetype' in card_data:
                arch_names = {"barrage": "弹幕流", "sniper": "狙击流", "control": "控制流", "summon": "召唤流"}
                arch_colors = {"barrage": (255, 100, 100), "sniper": (100, 200, 255), "control": (150, 100, 255), "summon": (100, 255, 150)}
                arch = card_data['archetype']
                arch_name = arch_names.get(arch, arch)
                arch_color = arch_colors.get(arch, WHITE)
                
                draw_text(screen, "流派:", 15, right_x, info_y, (180, 180, 200), align="left")
                draw_text(screen, arch_name, 18, right_x + 55, info_y, arch_color, align="left", glow=True)
                info_y += 28
            
            # 类别标签
            if 'category' in card_data:
                cat_names = {
                    "attack": "攻击", "defense": "防御", 
                    "special": "特殊", "system": "系统",
                    "control": "控制", "summon": "召唤", 
                    "utility": "辅助", "support": "支援"
                }
                category = cat_names.get(card_data['category'], card_data['category'])
                draw_text(screen, "类别:", 15, right_x, info_y, (180, 180, 200), align="left")
                draw_text(screen, category, 18, right_x + 55, info_y, (255, 220, 100), align="left", glow=True)
                info_y += 28
            
            # 视觉种子（用于生成独特图案）
            if 'visual_seed' in card_data:
                draw_text(screen, f"ID: #{card_data['visual_seed']}", 13, right_x, info_y, GRAY, align="left")
                info_y += 24
            
            # 已拥有提示
            if player and hasattr(player, 'upgrade_manager') and player.upgrade_manager:
                card_id = gallery_hover_card.get('id')
                if card_id in player.upgrade_manager.owned_cards:
                    owned_card = player.upgrade_manager.owned_cards[card_id]
                    level = owned_card.level if hasattr(owned_card, 'level') else 1
                    info_y += 10
                    draw_text(screen, "✓ 已拥有", 17, right_x, info_y, (100, 255, 100), align="left", glow=True)
                    info_y += 26
                    draw_text(screen, f"当前等级: Lv.{level}", 15, right_x, info_y, (150, 255, 150), align="left")

    # ====== 返回按钮 ======
    back_btn = pygame.Rect(WIDTH//2 - 55, HEIGHT - 55, 110, 42)
    h = back_btn.collidepoint(mx, my)
    
    if h:
        draw_cyber_rect(screen, back_btn, (60, 20, 50), alpha=220, fill=True)
        draw_cyber_rect(screen, back_btn, MAGENTA, border_width=2, fill=False)
        btn_text_color = WHITE
    else:
        draw_cyber_rect(screen, back_btn, (30, 25, 40), alpha=200, fill=True)
        draw_cyber_rect(screen, back_btn, (100, 80, 120), border_width=1, fill=False)
        btn_text_color = GRAY
    
    draw_text(screen, "返回", 18, back_btn.centerx, back_btn.centery - 8, btn_text_color)
    
    # ====== 翻页控制 ======
    max_p = max(1, (len(items) + items_per_page - 1) // items_per_page)
    if max_p > 1:
        # 上一页按钮 - 贴近左边缘
        if gallery_page > 0:
            prev_btn = pygame.Rect(8, HEIGHT//2 - 30, 50, 60)
            prev_hover = prev_btn.collidepoint(mx, my)
            if prev_hover:
                draw_cyber_rect(screen, prev_btn, (50, 30, 60), alpha=200, fill=True)
                draw_cyber_rect(screen, prev_btn, MAGENTA, border_width=2, fill=False)
            else:
                draw_cyber_rect(screen, prev_btn, (25, 20, 35), alpha=180, fill=True)
                draw_cyber_rect(screen, prev_btn, (80, 60, 100), border_width=1, fill=False)
            arrow_font = pygame.font.SysFont("Segoe UI Emoji", 28)
            arrow_color = WHITE if prev_hover else GRAY
            arrow_surf = arrow_font.render("◀", True, arrow_color)
            screen.blit(arrow_surf, (prev_btn.centerx - arrow_surf.get_width()//2, prev_btn.centery - arrow_surf.get_height()//2))
        
        # 下一页按钮 - 贴近右边缘
        if gallery_page < max_p - 1:
            next_btn = pygame.Rect(WIDTH - 58, HEIGHT//2 - 30, 50, 60)
            next_hover = next_btn.collidepoint(mx, my)
            if next_hover:
                draw_cyber_rect(screen, next_btn, (50, 30, 60), alpha=200, fill=True)
                draw_cyber_rect(screen, next_btn, MAGENTA, border_width=2, fill=False)
            else:
                draw_cyber_rect(screen, next_btn, (25, 20, 35), alpha=180, fill=True)
                draw_cyber_rect(screen, next_btn, (80, 60, 100), border_width=1, fill=False)
            arrow_font = pygame.font.SysFont("Segoe UI Emoji", 28)
            arrow_color = WHITE if next_hover else GRAY
            arrow_surf = arrow_font.render("▶", True, arrow_color)
            screen.blit(arrow_surf, (next_btn.centerx - arrow_surf.get_width()//2, next_btn.centery - arrow_surf.get_height()//2))
        
        # 页码显示
        page_bg = pygame.Rect(WIDTH//2 - 60, HEIGHT - 100, 120, 28)
        pygame.draw.rect(screen, (20, 15, 30, 180), page_bg, border_radius=5)
        draw_text(screen, f"第 {gallery_page+1} / {max_p} 页", 16, WIDTH//2, HEIGHT - 92, (150, 130, 180))

def draw_select_plane_ui():
    """绘制机体选择界面 - 简洁现代风格"""
    global current_plane_idx
    
    t = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    pulse = 0.5 + 0.5 * math.sin(t / 500)
    
    # ====== 背景 ======
    screen.fill((8, 12, 24))
    
    # 粒子星空
    random.seed(123)
    for i in range(60):
        sx = random.randint(0, WIDTH)
        sy = random.randint(0, HEIGHT)
        brightness = int(60 + 40 * math.sin(t / 400 + i * 0.5))
        pygame.draw.circle(screen, (brightness, brightness, brightness + 20), (sx, sy), 1)
    
    # 扫描线效果
    scan_y = (t // 20) % HEIGHT
    pygame.draw.line(screen, (0, 40, 60, 30), (0, scan_y), (WIDTH, scan_y), 1)
    
    # ====== 标题 ======
    title_y = 35
    # emoji字体
    try:
        emoji_font_lg = pygame.font.SysFont("Segoe UI Emoji", 32)
        rocket_emoji = emoji_font_lg.render("🚀", True, CYAN)
    except:
        rocket_emoji = None
    
    title_font = pygame.font.SysFont("SimHei", 36)
    title_surf = title_font.render("选择出击机体", True, WHITE)
    
    if rocket_emoji:
        total_w = rocket_emoji.get_width() + title_surf.get_width() + rocket_emoji.get_width() + 20
        tx = WIDTH // 2 - total_w // 2
        screen.blit(rocket_emoji, (tx, title_y - 5))
        screen.blit(title_surf, (tx + rocket_emoji.get_width() + 10, title_y))
        screen.blit(rocket_emoji, (tx + rocket_emoji.get_width() + title_surf.get_width() + 20, title_y - 5))
    else:
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, title_y))
    
    # 标题下划线
    line_w = 200 + int(40 * pulse)
    pygame.draw.line(screen, CYAN, (WIDTH//2 - line_w//2, 75), (WIDTH//2 + line_w//2, 75), 2)
    
    # ====== 布局参数 ======
    content_y = 90
    content_h = HEIGHT - 170
    margin = 20
    gap = 12
    
    # 两栏布局：左侧列表 + 右侧详情
    list_width = 280
    detail_width = WIDTH - margin * 2 - list_width - gap
    
    list_x = margin
    detail_x = list_x + list_width + gap
    
    # ====== 左栏：机体列表 ======
    list_rect = pygame.Rect(list_x, content_y, list_width, content_h)
    pygame.draw.rect(screen, (12, 18, 32), list_rect, border_radius=8)
    pygame.draw.rect(screen, (40, 60, 90), list_rect, 2, border_radius=8)
    
    # 列表标题栏
    header_rect = pygame.Rect(list_x, content_y, list_width, 36)
    pygame.draw.rect(screen, (20, 35, 55), header_rect, border_top_left_radius=8, border_top_right_radius=8)
    draw_text(screen, f"可用机体 ({len(plane_keys)})", 14, list_x + list_width // 2, content_y + 10, CYAN)
    
    # 机体卡片
    card_h = 50
    card_gap = 6
    list_inner_y = content_y + 42
    list_inner_h = content_h - 48
    max_visible = list_inner_h // (card_h + card_gap)
    
    # 滚动
    scroll_offset = max(0, min(current_plane_idx - max_visible // 2, len(plane_keys) - max_visible))
    
    for i in range(scroll_offset, min(scroll_offset + max_visible, len(plane_keys))):
        pid = plane_keys[i]
        pdata = PLANES[pid]
        idx = i - scroll_offset
        cy = list_inner_y + idx * (card_h + card_gap)
        card = pygame.Rect(list_x + 8, cy, list_width - 16, card_h)
        
        is_sel = (i == current_plane_idx)
        is_hov = card.collidepoint(mx, my) and not is_sel
        
        # 卡片背景
        if is_sel:
            pygame.draw.rect(screen, (pdata["color"][0]//5, pdata["color"][1]//5, pdata["color"][2]//5), card, border_radius=6)
            pygame.draw.rect(screen, pdata["color"], card, 2, border_radius=6)
            # 选中指示器
            pygame.draw.rect(screen, pdata["color"], (card.x, card.y + 8, 4, card.height - 16), border_radius=2)
        elif is_hov:
            pygame.draw.rect(screen, (25, 35, 55), card, border_radius=6)
            pygame.draw.rect(screen, (80, 100, 130), card, 1, border_radius=6)
        else:
            pygame.draw.rect(screen, (15, 22, 38), card, border_radius=6)
        
        # 颜色点
        pygame.draw.circle(screen, pdata["color"], (card.x + 22, card.y + card_h // 2), 8)
        pygame.draw.circle(screen, WHITE, (card.x + 22, card.y + card_h // 2), 8, 1)
        
        # 名称
        name_col = WHITE if is_sel else ((200, 210, 230) if is_hov else (140, 150, 170))
        name_font = pygame.font.SysFont("SimHei", 15)
        name_surf = name_font.render(pdata["name"], True, name_col)
        screen.blit(name_surf, (card.x + 40, card.y + 8))
        
        # 简要属性
        small_font = pygame.font.SysFont("SimHei", 10)
        stats_text = f"HP:{pdata['hp']}  ATK:{pdata['damage']}  SPD:{pdata['speed']}"
        stats_col = (100, 110, 130) if not is_sel else (150, 160, 180)
        stats_surf = small_font.render(stats_text, True, stats_col)
        screen.blit(stats_surf, (card.x + 40, card.y + 28))
    
    # 滚动条
    if len(plane_keys) > max_visible:
        track_h = list_inner_h - 10
        thumb_h = max(30, int(track_h * max_visible / len(plane_keys)))
        thumb_y = list_inner_y + 5 + int((track_h - thumb_h) * scroll_offset / max(1, len(plane_keys) - max_visible))
        pygame.draw.rect(screen, (30, 40, 60), (list_x + list_width - 10, list_inner_y + 5, 4, track_h), border_radius=2)
        pygame.draw.rect(screen, CYAN, (list_x + list_width - 10, thumb_y, 4, thumb_h), border_radius=2)
    
    # ====== 右栏：机体详情 ======
    pid = plane_keys[current_plane_idx]
    pdata = PLANES[pid]
    pcolor = pdata["color"]
    
    detail_rect = pygame.Rect(detail_x, content_y, detail_width, content_h)
    pygame.draw.rect(screen, (12, 18, 32), detail_rect, border_radius=8)
    # 动态边框
    border_col = (min(255, pcolor[0] + int(20 * pulse)), min(255, pcolor[1] + int(20 * pulse)), min(255, pcolor[2] + int(20 * pulse)))
    pygame.draw.rect(screen, border_col, detail_rect, 2, border_radius=8)
    
    # 详情区分为左右两半
    detail_left_w = detail_width // 2 - 10
    detail_right_x = detail_x + detail_width // 2 + 10
    detail_right_w = detail_width // 2 - 20
    
    # === 左半：预览 + 名称 + 描述 ===
    preview_cx = detail_x + detail_left_w // 2 + 20
    preview_cy = content_y + 120
    
    # 光晕
    glow_r = int(90 + 20 * pulse)
    glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
    for r in range(glow_r, 0, -3):
        alpha = int(40 * (1 - r / glow_r))
        pygame.draw.circle(glow_surf, (*pcolor, alpha), (glow_r, glow_r), r)
    screen.blit(glow_surf, (preview_cx - glow_r, preview_cy - glow_r))
    
    # 机体图像
    visual = customization_manager.get_theme_visual(pid, PLANES.get(pid, {}).get('visual', None))
    plane_img = get_plane_surf(pid, visual)
    img_size = int(140 + 8 * pulse)
    plane_img = pygame.transform.scale(plane_img, (img_size, img_size))
    screen.blit(plane_img, (preview_cx - img_size // 2, preview_cy - img_size // 2))
    
    # 机体名称
    name_y = preview_cy + img_size // 2 + 25
    name_font = pygame.font.SysFont("SimHei", 28)
    name_surf = name_font.render(pdata["name"], True, pcolor)
    screen.blit(name_surf, (preview_cx - name_surf.get_width() // 2, name_y))
    
    # 名称装饰线
    line_w = name_surf.get_width() + 40
    pygame.draw.line(screen, pcolor, (preview_cx - line_w // 2, name_y + 35), (preview_cx + line_w // 2, name_y + 35), 2)
    pygame.draw.circle(screen, pcolor, (preview_cx - line_w // 2, name_y + 35), 4)
    pygame.draw.circle(screen, pcolor, (preview_cx + line_w // 2, name_y + 35), 4)
    
    # 描述
    desc_y = name_y + 50
    desc_font = pygame.font.SysFont("SimHei", 13)
    desc_lines = textwrap.wrap(pdata["desc"], width=18)
    for i, line in enumerate(desc_lines[:3]):
        desc_surf = desc_font.render(line, True, (160, 170, 190))
        screen.blit(desc_surf, (preview_cx - desc_surf.get_width() // 2, desc_y + i * 20))
    
    # 终极技能
    ult_y = desc_y + 75
    ult_name = pdata.get("ult_name", "未知技能")
    ult_color = pdata.get("ult_color", pcolor)
    
    ult_box = pygame.Rect(detail_x + 25, ult_y, detail_left_w - 10, 45)
    pygame.draw.rect(screen, (ult_color[0]//8, ult_color[1]//8, ult_color[2]//8), ult_box, border_radius=6)
    pygame.draw.rect(screen, ult_color, ult_box, 1, border_radius=6)
    
    # 终极技能标签 + emoji
    try:
        ult_emoji_font = pygame.font.SysFont("Segoe UI Emoji", 16)
        ult_emoji = ult_emoji_font.render("⚡", True, ult_color)
        screen.blit(ult_emoji, (ult_box.x + 10, ult_box.y + 12))
    except:
        pass
    
    ult_label_font = pygame.font.SysFont("SimHei", 11)
    ult_label = ult_label_font.render("终极技能", True, (120, 130, 150))
    screen.blit(ult_label, (ult_box.x + 32, ult_box.y + 6))
    
    ult_name_font = pygame.font.SysFont("SimHei", 16)
    ult_name_surf = ult_name_font.render(ult_name, True, ult_color)
    screen.blit(ult_name_surf, (ult_box.x + 32, ult_box.y + 22))
    
    # === 右半：属性 + 战术信息 ===
    stat_y = content_y + 25
    
    # 属性标题
    stat_title_font = pygame.font.SysFont("SimHei", 14)
    stat_title = stat_title_font.render("◆ 能力属性", True, CYAN)
    screen.blit(stat_title, (detail_right_x, stat_y))
    pygame.draw.line(screen, (40, 60, 80), (detail_right_x + 80, stat_y + 8), (detail_x + detail_width - 25, stat_y + 8), 1)
    
    # emoji字体
    try:
        stat_emoji_font = pygame.font.SysFont("Segoe UI Emoji", 14)
    except:
        stat_emoji_font = None
    
    # 属性条
    bar_y = stat_y + 30
    bar_w = detail_right_w - 50
    bar_h = 14
    
    def draw_attr_bar(emoji, label, val, max_val, y, color):
        # emoji
        if stat_emoji_font:
            e_surf = stat_emoji_font.render(emoji, True, color)
            screen.blit(e_surf, (detail_right_x, y))
        # 标签
        lbl_font = pygame.font.SysFont("SimHei", 12)
        lbl_surf = lbl_font.render(label, True, (140, 150, 170))
        screen.blit(lbl_surf, (detail_right_x + 22, y + 1))
        # 进度条背景
        bar_rect = pygame.Rect(detail_right_x + 60, y + 2, bar_w, bar_h)
        pygame.draw.rect(screen, (25, 32, 50), bar_rect, border_radius=3)
        # 填充
        fill_w = int(bar_w * min(1, val / max_val))
        if fill_w > 0:
            fill_rect = pygame.Rect(detail_right_x + 60, y + 2, fill_w, bar_h)
            pygame.draw.rect(screen, color, fill_rect, border_radius=3)
        # 数值
        val_font = pygame.font.SysFont("SimHei", 11)
        val_text = f"{val:.1f}" if isinstance(val, float) else str(val)
        val_surf = val_font.render(val_text, True, color)
        screen.blit(val_surf, (detail_right_x + 65 + bar_w, y + 1))
    
    draw_attr_bar("⚡", "速度", pdata["speed"], 6.0, bar_y, LIME)
    draw_attr_bar("🔥", "火力", pdata["damage"], 50, bar_y + 28, ORANGE)
    draw_attr_bar("🛡", "装甲", pdata["hp"], 320, bar_y + 56, CYAN)
    draw_attr_bar("💫", "射速", 1000 / pdata["delay"], 18, bar_y + 84, MAGENTA)
    
    # 战术信息
    tact_y = bar_y + 130
    tact_title = stat_title_font.render("◆ 战术信息", True, (100, 120, 160))
    screen.blit(tact_title, (detail_right_x, tact_y))
    pygame.draw.line(screen, (40, 50, 70), (detail_right_x + 80, tact_y + 8), (detail_x + detail_width - 25, tact_y + 8), 1)
    
    # 弹药类型
    info_y = tact_y + 28
    info_font = pygame.font.SysFont("SimHei", 12)
    bullet_type = pdata.get("bullet_type", "standard").replace("_", " ").upper()
    
    info_label = info_font.render("弹药:", True, (100, 110, 130))
    screen.blit(info_label, (detail_right_x, info_y))
    info_val = info_font.render(bullet_type, True, pcolor)
    screen.blit(info_val, (detail_right_x + 45, info_y))
    
    # 特殊能力
    visual_data = pdata.get("visual", {})
    ability = visual_data.get("ability", "standard").replace("_", " ").title()
    
    info_label2 = info_font.render("能力:", True, (100, 110, 130))
    screen.blit(info_label2, (detail_right_x, info_y + 22))
    info_val2 = info_font.render(ability, True, (170, 180, 200))
    screen.blit(info_val2, (detail_right_x + 45, info_y + 22))
    
    # 综合评级
    total_power = pdata["speed"] * 12 + pdata["damage"] * 1.2 + pdata["hp"] / 2.5
    if total_power > 170:
        rank, rank_col = "S", GOLD
    elif total_power > 145:
        rank, rank_col = "A", MAGENTA
    elif total_power > 120:
        rank, rank_col = "B", CYAN
    else:
        rank, rank_col = "C", GRAY
    
    rank_y = info_y + 60
    rank_label = info_font.render("评级:", True, (100, 110, 130))
    screen.blit(rank_label, (detail_right_x, rank_y))
    rank_font = pygame.font.SysFont("SimHei", 32)
    rank_surf = rank_font.render(rank, True, rank_col)
    screen.blit(rank_surf, (detail_right_x + 50, rank_y - 8))
    
    # 技能列表（如有）
    skills = pdata.get("skills", {})
    if skills:
        skill_y = rank_y + 50
        skill_title = stat_title_font.render("◆ 技能组", True, YELLOW)
        screen.blit(skill_title, (detail_right_x, skill_y))
        pygame.draw.line(screen, (60, 55, 30), (detail_right_x + 60, skill_y + 8), (detail_x + detail_width - 25, skill_y + 8), 1)
        
        sk_y = skill_y + 22
        sk_font = pygame.font.SysFont("SimHei", 11)
        for sk_key, sk_data in list(skills.items())[:3]:
            sk_name = sk_data.get("name", sk_key)
            sk_box = pygame.Rect(detail_right_x, sk_y, detail_right_w - 10, 24)
            pygame.draw.rect(screen, (22, 28, 42), sk_box, border_radius=4)
            pygame.draw.rect(screen, (60, 65, 85), sk_box, 1, border_radius=4)
            sk_surf = sk_font.render(sk_name, True, (150, 160, 180))
            screen.blit(sk_surf, (sk_box.x + 8, sk_box.y + 5))
            sk_y += 28
    
    # ====== 底部按钮 ======
    btn_y = HEIGHT - 65
    
    # 左右导航
    nav_btn_w = 70
    nav_btn_h = 45
    
    # 箭头字体（使用支持箭头符号的字体）
    try:
        arrow_emoji_font = pygame.font.SysFont("Segoe UI Symbol", 24)
    except:
        arrow_emoji_font = pygame.font.SysFont("SimHei", 24)
    
    left_btn = pygame.Rect(list_x, btn_y, nav_btn_w, nav_btn_h)
    left_hov = left_btn.collidepoint(mx, my)
    pygame.draw.rect(screen, (35, 45, 65) if left_hov else (20, 28, 45), left_btn, border_radius=6)
    pygame.draw.rect(screen, CYAN if left_hov else (50, 60, 80), left_btn, 2, border_radius=6)
    # 使用纯文本箭头代替Unicode符号
    left_arrow = arrow_emoji_font.render("<", True, WHITE if left_hov else GRAY)
    screen.blit(left_arrow, (left_btn.centerx - left_arrow.get_width() // 2, left_btn.centery - left_arrow.get_height() // 2 - 4))
    draw_text(screen, "A", 10, left_btn.centerx, left_btn.bottom - 10, (80, 90, 110))
    
    right_btn = pygame.Rect(list_x + list_width - nav_btn_w, btn_y, nav_btn_w, nav_btn_h)
    right_hov = right_btn.collidepoint(mx, my)
    pygame.draw.rect(screen, (35, 45, 65) if right_hov else (20, 28, 45), right_btn, border_radius=6)
    pygame.draw.rect(screen, CYAN if right_hov else (50, 60, 80), right_btn, 2, border_radius=6)
    right_arrow = arrow_emoji_font.render(">", True, WHITE if right_hov else GRAY)
    screen.blit(right_arrow, (right_btn.centerx - right_arrow.get_width() // 2, right_btn.centery - right_arrow.get_height() // 2 - 4))
    draw_text(screen, "D", 10, right_btn.centerx, right_btn.bottom - 10, (80, 90, 110))
    
    # 确认出击按钮
    start_btn_w = 220
    start_btn_h = 50
    start_btn = pygame.Rect(detail_x + detail_width // 2 - start_btn_w // 2, btn_y - 2, start_btn_w, start_btn_h)
    start_hov = start_btn.collidepoint(mx, my)
    
    if start_hov:
        pygame.draw.rect(screen, (pcolor[0]//2, pcolor[1]//2, pcolor[2]//2), start_btn, border_radius=8)
        pygame.draw.rect(screen, pcolor, start_btn, 3, border_radius=8)
    else:
        pygame.draw.rect(screen, (pcolor[0]//5, pcolor[1]//5, pcolor[2]//5), start_btn, border_radius=8)
        pygame.draw.rect(screen, pcolor, start_btn, 2, border_radius=8)
    
    start_font = pygame.font.SysFont("SimHei", 22)
    start_text = start_font.render("确认出击", True, WHITE)
    screen.blit(start_text, (start_btn.centerx - start_text.get_width() // 2, start_btn.centery - 14))
    hint_font = pygame.font.SysFont("SimHei", 10)
    hint_text = hint_font.render("[ENTER]", True, (130, 140, 160))
    screen.blit(hint_text, (start_btn.centerx - hint_text.get_width() // 2, start_btn.bottom - 14))
    
    # 返回按钮
    back_btn = pygame.Rect(detail_x + detail_width - 90, btn_y, 85, nav_btn_h)
    back_hov = back_btn.collidepoint(mx, my)
    pygame.draw.rect(screen, (50, 30, 35) if back_hov else (28, 22, 28), back_btn, border_radius=6)
    pygame.draw.rect(screen, RED if back_hov else (70, 50, 55), back_btn, 2, border_radius=6)
    back_font = pygame.font.SysFont("SimHei", 15)
    back_text = back_font.render("返回", True, WHITE if back_hov else (140, 130, 135))
    screen.blit(back_text, (back_btn.centerx - back_text.get_width() // 2, back_btn.centery - 10))
    esc_text = hint_font.render("[ESC]", True, (100, 85, 90))
    screen.blit(esc_text, (back_btn.centerx - esc_text.get_width() // 2, back_btn.bottom - 12))
    
    # 底部提示
    tip_font = pygame.font.SysFont("SimHei", 11)
    tip_text = tip_font.render("A/D或↑↓切换机体  |  点击列表选择  |  ENTER确认  |  ESC返回", True, (60, 70, 90))
    screen.blit(tip_text, (WIDTH // 2 - tip_text.get_width() // 2, HEIGHT - 18))

def draw_boss_challenge_complete_ui():
    """Boss挑战模式完成界面，显示完成统计和奖励"""
    global boss_challenge_order, boss_challenge_current
    screen.fill((10, 10, 30))
    title_font = pygame.font.SysFont("SimHei", 56)
    font = pygame.font.SysFont("SimHei", 32)
    small_font = pygame.font.SysFont("SimHei", 24)
    emoji_font_title = pygame.font.SysFont("Segoe UI Emoji", 56)
    
    # 分开渲染emoji和文字
    trophy_emoji = emoji_font_title.render("🏆", True, GOLD)
    title_text = title_font.render(" 挑战完成！ ", True, GOLD)
    title_width = trophy_emoji.get_width() * 2 + title_text.get_width()
    title_x = WIDTH//2 - title_width//2
    screen.blit(trophy_emoji, (title_x, 60))
    screen.blit(title_text, (title_x + trophy_emoji.get_width(), 60))
    screen.blit(trophy_emoji, (title_x + trophy_emoji.get_width() + title_text.get_width(), 60))
    
    y = 180
    # 显示挑战数据
    draw_text(screen, f"完成了 {len(boss_challenge_order)} 个Boss的挑战！", 36, WIDTH//2, y, CYAN, glow=True)
    y += 80
    draw_text(screen, "挑战顺序:", 28, WIDTH//2, y, WHITE)
    y += 50
    
    # 列出所有Boss
    for i, boss_key in enumerate(boss_challenge_order):
        boss_name = BOSS_DB[boss_key]["name"]
        col = BOSS_DB[boss_key]["color"]
        txt = font.render(f"✓ {boss_name}", True, col)
        screen.blit(txt, (WIDTH//2 - 150, y + i*45))
    
    # 奖励提示
    y = HEIGHT - 150
    draw_text(screen, "特殊成就已解锁！", 28, WIDTH//2, y, GOLD, glow=True)
    draw_text(screen, "按 Enter 返回主菜单，按 Esc 继续游戏", 20, WIDTH//2, HEIGHT - 80, GRAY)

def draw_boss_challenge_ui():
    """Boss挑战模式主界面 - 赛博朋克风格 + 预设模式"""
    global boss_challenge_selected, boss_challenge_order, boss_challenge_swap_timer, boss_challenge_pulse_timer, boss_challenge_scroll_offset
    global boss_challenge_enabled, boss_challenge_preset
    
    # 动画计时器更新
    boss_challenge_pulse_timer = (boss_challenge_pulse_timer + 1) % 360
    t = boss_challenge_pulse_timer / 360.0
    pulse = 0.5 + 0.5 * math.sin(t * math.pi * 2)  # 0-1 脉冲
    
    # ====== 背景 ======
    screen.fill((5, 8, 18))
    
    # 动态星空背景
    random.seed(42)
    for i in range(60):
        sx = random.randint(0, WIDTH)
        sy = random.randint(0, HEIGHT)
        base_b = random.randint(50, 140)
        twinkle = int(30 * math.sin(t * math.pi * 4 + i * 0.5))
        brightness = max(30, min(180, base_b + twinkle))
        size = 1 if i % 3 else 2
        pygame.draw.circle(screen, (brightness, brightness, brightness + 30), (sx, sy), size)
    
    # 背景装饰网格线
    for gx in range(0, WIDTH, 80):
        alpha = int(15 + 10 * math.sin(t * math.pi * 2 + gx * 0.02))
        pygame.draw.line(screen, (0, alpha, alpha), (gx, 0), (gx, HEIGHT), 1)
    for gy in range(0, HEIGHT, 80):
        alpha = int(15 + 10 * math.sin(t * math.pi * 2 + gy * 0.02))
        pygame.draw.line(screen, (0, alpha, alpha), (0, gy), (WIDTH, gy), 1)
    
    # Boss列表初始化
    boss_keys = list(BOSS_DB.keys())
    if not boss_challenge_enabled:
        boss_challenge_enabled = {k: True for k in boss_keys}
    if not boss_challenge_order:
        boss_challenge_order = boss_keys[:]
    
    # 获取已启用的Boss列表
    enabled_bosses = [k for k in boss_challenge_order if boss_challenge_enabled.get(k, True)]
    enabled_count = len(enabled_bosses)
    
    mx, my = pygame.mouse.get_pos()
    
    # ====== 标题区 ======
    title_glow = int(180 + 40 * pulse)
    # 分离渲染: emoji用专用字体，文字用常规字体
    title_emoji_font = pygame.font.SysFont("Segoe UI Emoji", 44)
    title_text_font = pygame.font.SysFont("SimHei", 44)
    sword_emoji = title_emoji_font.render("⚔", True, (0, title_glow, title_glow))
    title_text = title_text_font.render(" BOSS 挑战模式 ", True, (0, title_glow, title_glow))
    total_w = sword_emoji.get_width() * 2 + title_text.get_width()
    title_start_x = WIDTH//2 - total_w//2
    screen.blit(sword_emoji, (title_start_x, 40 - sword_emoji.get_height()//2))
    screen.blit(title_text, (title_start_x + sword_emoji.get_width(), 40 - title_text.get_height()//2))
    screen.blit(sword_emoji, (title_start_x + sword_emoji.get_width() + title_text.get_width(), 40 - sword_emoji.get_height()//2))
    
    # ====== 预设模式按钮 ======
    preset_emojis = ["⚙️", "🎯", "⚔️", "🔥", "💀"]
    preset_labels = ["自定义", "快速战", "标准战", "持久战", "全Boss"]
    preset_counts = [0, 3, 5, 10, len(boss_keys)]  # 0表示自定义
    preset_colors = [(100, 100, 100), LIME, CYAN, ORANGE, RED]
    preset_btn_w = 95
    preset_btn_h = 32
    preset_start_x = WIDTH//2 - (len(preset_labels) * preset_btn_w + (len(preset_labels)-1) * 8) // 2
    preset_y = 72
    
    # emoji字体
    try:
        emoji_font = pygame.font.SysFont("Segoe UI Emoji", 14)
    except:
        emoji_font = pygame.font.SysFont("Arial", 14)
    
    for i, (emoji, label, count, color) in enumerate(zip(preset_emojis, preset_labels, preset_counts, preset_colors)):
        btn_x = preset_start_x + i * (preset_btn_w + 8)
        btn_rect = pygame.Rect(btn_x, preset_y, preset_btn_w, preset_btn_h)
        is_selected = (boss_challenge_preset == i)
        is_hover = btn_rect.collidepoint(mx, my)
        
        # 按钮背景
        if is_selected:
            bg_col = (color[0]//3, color[1]//3, color[2]//3)
            draw_cyber_rect(screen, btn_rect, bg_col, alpha=220, cut_size=5, fill=True)
            draw_cyber_rect(screen, btn_rect, color, cut_size=5, border_width=2, fill=False)
        elif is_hover:
            draw_cyber_rect(screen, btn_rect, (40, 50, 70), alpha=200, cut_size=5, fill=True)
            draw_cyber_rect(screen, btn_rect, color, cut_size=5, border_width=1, fill=False)
        else:
            draw_cyber_rect(screen, btn_rect, (20, 28, 45), alpha=180, cut_size=5, fill=True)
            draw_cyber_rect(screen, btn_rect, (60, 70, 90), cut_size=5, border_width=1, fill=False)
        
        # 按钮文字 - emoji用专用字体渲染
        text_col = WHITE if is_selected else (color if is_hover else (150, 160, 180))
        # 渲染emoji
        emoji_surf = emoji_font.render(emoji, True, text_col)
        emoji_x = btn_rect.centerx - emoji_surf.get_width()//2 - 22
        screen.blit(emoji_surf, (emoji_x, btn_rect.centery - emoji_surf.get_height()//2))
        # 渲染文字标签
        draw_text(screen, label, 13, btn_rect.centerx + 8, btn_rect.centery - 7, text_col, glow=is_selected)
        # 数量提示
        if count > 0:
            draw_text(screen, f"×{count}", 10, btn_rect.centerx, btn_rect.bottom - 10, (120, 130, 150))
    
    # 标题下装饰线
    line_w = 300 + int(50 * pulse)
    pygame.draw.line(screen, CYAN, (WIDTH//2 - line_w//2, 108), (WIDTH//2 + line_w//2, 108), 1)
    
    # ====== 三栏布局 ======
    content_y = 118
    content_height = HEIGHT - 195
    
    # 左栏：Boss列表
    left_x = 28
    left_width = 268
    
    # 中栏：Boss详情
    mid_x = left_x + left_width + 10
    mid_width = 282
    
    # 右栏：挑战预览
    right_x = mid_x + mid_width + 10
    right_width = WIDTH - right_x - 28
    
    # ====== 左栏：Boss列表 ======
    card_height = 46
    gap = 4
    max_visible = int((content_height - 38) / (card_height + gap))
    visible_height = max_visible * (card_height + gap)
    
    # 自动滚动
    if boss_challenge_selected < boss_challenge_scroll_offset:
        boss_challenge_scroll_offset = boss_challenge_selected
    elif boss_challenge_selected >= boss_challenge_scroll_offset + max_visible:
        boss_challenge_scroll_offset = boss_challenge_selected - max_visible + 1
    
    # 列表面板 - 赛博风格 + 角落装饰
    list_panel = pygame.Rect(left_x, content_y, left_width, content_height)
    draw_cyber_rect(screen, list_panel, (12, 18, 32), alpha=230, fill=True)
    draw_cyber_rect(screen, list_panel, CYAN, border_width=2, fill=False)
    
    # 角落装饰
    corner_size = 8
    pygame.draw.line(screen, CYAN, (left_x, content_y + corner_size), (left_x, content_y), 2)
    pygame.draw.line(screen, CYAN, (left_x, content_y), (left_x + corner_size, content_y), 2)
    pygame.draw.line(screen, CYAN, (left_x + left_width - corner_size, content_y + content_height), (left_x + left_width, content_y + content_height), 2)
    pygame.draw.line(screen, CYAN, (left_x + left_width, content_y + content_height - corner_size), (left_x + left_width, content_y + content_height), 2)
    
    # 面板标题 + 装饰
    draw_text(screen, "◆ 挑战顺序", 15, left_x + left_width//2, content_y + 12, CYAN)
    pygame.draw.line(screen, (0, 80, 80), (left_x + 15, content_y + 30), (left_x + left_width - 15, content_y + 30), 1)
    
    # Boss卡片
    card_start_y = content_y + 38
    
    for i in range(boss_challenge_scroll_offset, min(boss_challenge_scroll_offset + max_visible, len(boss_challenge_order))):
        bkey = boss_challenge_order[i]
        boss_data = BOSS_DB[bkey]
        boss_color = boss_data["color"]
        is_enabled = boss_challenge_enabled.get(bkey, True)
        
        display_idx = i - boss_challenge_scroll_offset
        card_y = card_start_y + display_idx * (card_height + gap)
        card_rect = pygame.Rect(left_x + 8, card_y, left_width - 20, card_height)
        
        is_selected = (i == boss_challenge_selected)
        is_hovered = card_rect.collidepoint(mx, my) and not is_selected
        
        # 禁用状态灰化
        display_color = boss_color if is_enabled else (60, 60, 70)
        
        # 卡片背景 - 赛博风格 + 动态效果
        if is_selected:
            # 选中状态 - 呼吸光效
            glow_alpha = int(180 + 40 * pulse)
            bg_col = (display_color[0]//3, display_color[1]//3, display_color[2]//3)
            draw_cyber_rect(screen, card_rect, bg_col, alpha=220 if is_enabled else 150, cut_size=6, fill=True)
            border_col = (min(255, display_color[0] + int(30 * pulse)), 
                         min(255, display_color[1] + int(30 * pulse)), 
                         min(255, display_color[2] + int(30 * pulse)))
            draw_cyber_rect(screen, card_rect, border_col, cut_size=6, border_width=2, fill=False)
            # 左侧指示条
            pygame.draw.rect(screen, display_color, (card_rect.x, card_rect.y + 4, 3, card_rect.height - 8), border_radius=1)
        elif is_hovered:
            draw_cyber_rect(screen, card_rect, (35, 45, 70), alpha=200 if is_enabled else 120, cut_size=6, fill=True)
            draw_cyber_rect(screen, card_rect, CYAN if is_enabled else (80, 80, 90), cut_size=6, border_width=1, fill=False)
        else:
            draw_cyber_rect(screen, card_rect, (18, 24, 40), alpha=180 if is_enabled else 100, cut_size=6, fill=True)
            draw_cyber_rect(screen, card_rect, (60, 70, 90) if is_enabled else (40, 45, 55), cut_size=6, border_width=1, fill=False)
        
        # 勾选框
        checkbox_x = card_rect.x + 12
        checkbox_y = card_rect.y + card_height // 2 - 8
        checkbox_rect = pygame.Rect(checkbox_x, checkbox_y, 16, 16)
        pygame.draw.rect(screen, (50, 60, 80), checkbox_rect, border_radius=3)
        pygame.draw.rect(screen, display_color if is_enabled else (80, 80, 90), checkbox_rect, 2, border_radius=3)
        if is_enabled:
            # 绘制勾选标记
            pygame.draw.line(screen, LIME, (checkbox_x + 3, checkbox_y + 8), (checkbox_x + 6, checkbox_y + 12), 2)
            pygame.draw.line(screen, LIME, (checkbox_x + 6, checkbox_y + 12), (checkbox_x + 13, checkbox_y + 4), 2)
        
        # 序号圆圈 (移到勾选框右边)
        num_cx = card_rect.x + 38
        num_cy = card_rect.y + card_height // 2
        if is_selected:
            pygame.draw.circle(screen, display_color, (num_cx, num_cy), 12)
            pygame.draw.circle(screen, WHITE if is_enabled else (120, 120, 130), (num_cx, num_cy), 8)
            # 显示在已启用列表中的序号
            enabled_idx = enabled_bosses.index(bkey) + 1 if bkey in enabled_bosses else "-"
            draw_text(screen, str(enabled_idx), 11, num_cx, num_cy - 6, display_color)
        else:
            pygame.draw.circle(screen, (40, 50, 70), (num_cx, num_cy), 10, 1)
            enabled_idx = enabled_bosses.index(bkey) + 1 if bkey in enabled_bosses else "-"
            draw_text(screen, str(enabled_idx), 10, num_cx, num_cy - 5, GRAY if not is_hovered else CYAN)
        
        # 名称
        name_color = (WHITE if is_enabled else (100, 100, 110)) if is_selected else (CYAN if is_hovered and is_enabled else ((150, 160, 180) if is_enabled else (80, 85, 95)))
        draw_text(screen, boss_data["name"], 16, card_rect.x + 58, card_rect.y + 14, name_color, align="left", glow=is_selected and is_enabled)
        
        # 威胁指示条 - 渐变色
        stats = boss_data.get("stats", [])
        if stats:
            total = sum([s[1] for s in stats])
            threat = min(5, max(1, total // 55))
            threat_colors = [LIME, CYAN, YELLOW, ORANGE, RED]
            for ti in range(threat):
                col = boss_color if is_selected else threat_colors[min(ti, 4)]
                pygame.draw.rect(screen, col, (card_rect.right - 58 + ti * 11, card_rect.y + 15, 7, 16), border_radius=2)
            # 空槽
            for ti in range(threat, 5):
                pygame.draw.rect(screen, (35, 45, 60), (card_rect.right - 58 + ti * 11, card_rect.y + 15, 7, 16), border_radius=2)
                pygame.draw.rect(screen, (50, 60, 80), (card_rect.right - 58 + ti * 11, card_rect.y + 15, 7, 16), 1, border_radius=2)
    
    # 滚动条
    if len(boss_challenge_order) > max_visible:
        scroll_h = max(25, int(visible_height * max_visible / len(boss_challenge_order)))
        scroll_y = int(card_start_y + (visible_height - scroll_h) * boss_challenge_scroll_offset / max(1, len(boss_challenge_order) - max_visible))
        pygame.draw.rect(screen, (25, 35, 55), (left_x + left_width - 8, card_start_y, 4, visible_height), border_radius=2)
        pygame.draw.rect(screen, CYAN, (left_x + left_width - 8, scroll_y, 4, scroll_h), border_radius=2)
    
    # ====== 中栏：Boss详情 ======
    if boss_challenge_selected < len(boss_challenge_order):
        sel_key = boss_challenge_order[boss_challenge_selected]
        sel_boss = BOSS_DB[sel_key]
        boss_color = sel_boss["color"]
        
        # 详情面板 - 赛博风格 + 角落装饰
        detail_panel = pygame.Rect(mid_x, content_y, mid_width, content_height)
        draw_cyber_rect(screen, detail_panel, (12, 18, 32), alpha=230, fill=True)
        
        # 动态边框颜色
        border_pulse = (min(255, boss_color[0] + int(20 * pulse)),
                       min(255, boss_color[1] + int(20 * pulse)),
                       min(255, boss_color[2] + int(20 * pulse)))
        draw_cyber_rect(screen, detail_panel, border_pulse, border_width=2, fill=False)
        
        # 角落装饰
        pygame.draw.line(screen, boss_color, (mid_x + mid_width - corner_size, content_y), (mid_x + mid_width, content_y), 2)
        pygame.draw.line(screen, boss_color, (mid_x + mid_width, content_y), (mid_x + mid_width, content_y + corner_size), 2)
        
        # Boss名称 + 装饰
        draw_text(screen, sel_boss["name"], 26, mid_x + mid_width//2, content_y + 22, boss_color, glow=True)
        
        # 名称下划线装饰
        name_line_w = 120 + int(20 * pulse)
        pygame.draw.line(screen, boss_color, (mid_x + mid_width//2 - name_line_w//2, content_y + 48), 
                        (mid_x + mid_width//2 + name_line_w//2, content_y + 48), 2)
        pygame.draw.circle(screen, boss_color, (mid_x + mid_width//2 - name_line_w//2, content_y + 48), 3)
        pygame.draw.circle(screen, boss_color, (mid_x + mid_width//2 + name_line_w//2, content_y + 48), 3)
        
        # 描述框
        desc_box = pygame.Rect(mid_x + 12, content_y + 55, mid_width - 24, 65)
        draw_cyber_rect(screen, desc_box, (20, 28, 45), alpha=180, cut_size=5, fill=True)
        draw_cyber_rect(screen, desc_box, (60, 80, 110), cut_size=5, border_width=1, fill=False)
        
        desc = sel_boss.get("desc", "")
        desc_y = content_y + 62
        for i in range(0, len(desc), 17):
            line = desc[i:i+17]
            draw_text(screen, line, 13, mid_x + mid_width//2, desc_y, (170, 180, 200))
            desc_y += 18
            if desc_y > content_y + 115:
                break
        
        # 属性区
        attr_y = content_y + 128
        draw_text(screen, "◇ 能力指数", 14, mid_x + 20, attr_y, CYAN, align="left")
        pygame.draw.line(screen, (0, 60, 60), (mid_x + 90, attr_y + 8), (mid_x + mid_width - 15, attr_y + 8), 1)
        attr_y += 22
        
        stats = sel_boss.get("stats", [])
        stat_icons = {"装甲": "◈", "毁灭": "◆", "机动": "◇"}
        for stat_name, stat_val in stats:
            # 图标 + 标签
            icon = stat_icons.get(stat_name, "●")
            draw_text(screen, f"{icon} {stat_name}", 13, mid_x + 20, attr_y, (130, 150, 180), align="left")
            
            # 进度条背景
            bar_x = mid_x + 75
            bar_w = 140
            bar_h = 14
            draw_cyber_rect(screen, (bar_x, attr_y + 1, bar_w, bar_h), (25, 32, 50), alpha=200, cut_size=3, fill=True)
            
            # 进度条填充
            fill_w = int(bar_w * min(1, stat_val / 150))
            if stat_val < 50:
                bar_col = CYAN
            elif stat_val < 90:
                bar_col = LIME
            else:
                bar_col = MAGENTA
            
            if fill_w > 4:
                draw_cyber_rect(screen, (bar_x, attr_y + 1, fill_w, bar_h), bar_col, alpha=230, cut_size=3, fill=True)
                # 高光
                pygame.draw.line(screen, WHITE, (bar_x + 2, attr_y + 3), (bar_x + fill_w - 3, attr_y + 3), 1)
            
            # 数值
            draw_text(screen, str(stat_val), 14, bar_x + bar_w + 18, attr_y, bar_col, glow=(stat_val >= 90))
            attr_y += 26
        
        # 阶段信息
        phases = sel_boss.get("phases", [])
        phase_y = attr_y + 8
        draw_text(screen, f"◇ 战斗阶段: {len(phases)}", 14, mid_x + 20, phase_y, CYAN, align="left")
        pygame.draw.line(screen, (0, 60, 60), (mid_x + 115, phase_y + 8), (mid_x + mid_width - 15, phase_y + 8), 1)
        
        # 阶段条
        phase_bar_y = phase_y + 22
        phase_bar_w = mid_width - 35
        phase_bar_h = 20
        draw_cyber_rect(screen, (mid_x + 18, phase_bar_y, phase_bar_w, phase_bar_h), (25, 32, 50), alpha=200, cut_size=4, fill=True)
        
        prev = 1.0
        phase_cols = [LIME, YELLOW, ORANGE, RED]
        phase_labels = ["P1", "P2", "P3", "终"]
        for idx, phase in enumerate(phases):
            th = phase.get("threshold", 0)
            start = int(phase_bar_w * (1 - prev))
            end = int(phase_bar_w * (1 - th))
            col = phase_cols[min(idx, 3)]
            if end - start > 3:
                pygame.draw.rect(screen, col, (mid_x + 18 + start, phase_bar_y, end - start, phase_bar_h))
                # 阶段标签
                if end - start > 20:
                    draw_text(screen, phase_labels[min(idx, 3)], 11, mid_x + 18 + start + (end - start)//2, phase_bar_y + 3, (30, 30, 30))
            prev = th
        
        # 最后阶段
        if phases:
            start = int(phase_bar_w * (1 - phases[-1].get("threshold", 0)))
            pygame.draw.rect(screen, RED, (mid_x + 18 + start, phase_bar_y, phase_bar_w - start, phase_bar_h))
            if phase_bar_w - start > 20:
                draw_text(screen, "狂", 11, mid_x + 18 + start + (phase_bar_w - start)//2, phase_bar_y + 3, (30, 30, 30))
        
        # Boss预览 - 使用真实Boss图像
        preview_y = phase_bar_y + 60
        preview_cx = mid_x + mid_width // 2
        preview_size = 150  # 预览尺寸
        preview_cy = preview_y + preview_size // 2 + 10
        
        # 外层光环背景（动态）
        ring_size = preview_size // 2 + 15 + int(5 * pulse)
        
        # 多层光环效果
        for i in range(3):
            alpha_ring = 60 - i * 20
            ring_col = (min(255, boss_color[0]//3 + i*10), 
                       min(255, boss_color[1]//3 + i*10), 
                       min(255, boss_color[2]//3 + i*10))
            pygame.draw.circle(screen, ring_col, (preview_cx, preview_cy), ring_size + i*8, 2)
        
        # 装饰粒子环
        for angle in range(0, 360, 30):
            rad = math.radians(angle + boss_challenge_pulse_timer * 0.5)
            particle_dist = ring_size + 18 + int(3 * math.sin(boss_challenge_pulse_timer * 0.03 + angle * 0.1))
            dx = int(math.cos(rad) * particle_dist)
            dy = int(math.sin(rad) * particle_dist)
            particle_size = 2 + int(abs(pulse))
            pygame.draw.circle(screen, boss_color, (preview_cx + dx, preview_cy + dy), particle_size)
        
        # 内部发光背景
        glow_surf = pygame.Surface((preview_size + 40, preview_size + 40), pygame.SRCALPHA)
        for r in range(preview_size//2 + 20, 0, -3):
            alpha = int(80 * (1 - r / (preview_size//2 + 20)))
            glow_col = (boss_color[0], boss_color[1], boss_color[2], alpha)
            pygame.draw.circle(glow_surf, glow_col, (preview_size//2 + 20, preview_size//2 + 20), r)
        screen.blit(glow_surf, (preview_cx - preview_size//2 - 20, preview_cy - preview_size//2 - 20))
        
        # 获取并绘制真实Boss图像
        boss_surf = get_boss_surf(sel_key, boss_color, sel_boss.get("visual"))
        # 缩放到合适大小
        scaled_boss = pygame.transform.smoothscale(boss_surf, (preview_size, preview_size))
        screen.blit(scaled_boss, (preview_cx - preview_size//2, preview_cy - preview_size//2))
        
        # 边框装饰
        pygame.draw.circle(screen, boss_color, (preview_cx, preview_cy), preview_size//2 + 5, 2)
    
    # ====== 右栏：挑战预览/统计 ======
    right_panel = pygame.Rect(right_x, content_y, right_width, content_height)
    draw_cyber_rect(screen, right_panel, (12, 18, 32), alpha=230, fill=True)
    
    # 动态边框
    magenta_pulse = (min(255, 255 + int(20 * pulse)), int(50 * pulse), min(255, 255 + int(20 * pulse)))
    draw_cyber_rect(screen, right_panel, magenta_pulse, border_width=2, fill=False)
    
    # 角落装饰
    pygame.draw.line(screen, MAGENTA, (right_x, content_y + content_height - corner_size), (right_x, content_y + content_height), 2)
    pygame.draw.line(screen, MAGENTA, (right_x, content_y + content_height), (right_x + corner_size, content_y + content_height), 2)
    
    # 标题
    draw_text(screen, f"◆ 挑战预览 ({len(enabled_bosses)})", 15, right_x + right_width//2, content_y + 12, MAGENTA)
    pygame.draw.line(screen, (80, 0, 80), (right_x + 15, content_y + 30), (right_x + right_width - 15, content_y + 30), 1)
    
    # 挑战顺序预览（只显示已启用的Boss小图标）
    preview_y = content_y + 38
    icon_size = 30
    icons_per_row = max(1, (right_width - 16) // (icon_size + 5))
    
    for i, bkey in enumerate(enabled_bosses):
        boss_data = BOSS_DB[bkey]
        boss_color = boss_data["color"]
        
        row = i // icons_per_row
        col = i % icons_per_row
        ix = right_x + 8 + col * (icon_size + 5)
        iy = preview_y + row * (icon_size + 5)
        
        # 小图标 - 赛博风格
        # 检查是否是当前选中的Boss
        is_current = (bkey == boss_challenge_order[boss_challenge_selected] if boss_challenge_selected < len(boss_challenge_order) else False)
        
        icon_rect = pygame.Rect(ix, iy, icon_size, icon_size)
        
        # 当前选中 - 动态光环
        if is_current:
            glow_rect = icon_rect.inflate(6 + int(2 * pulse), 6 + int(2 * pulse))
            draw_cyber_rect(screen, glow_rect, boss_color, alpha=200, cut_size=5, fill=False, border_width=2)
        
        bg_col = (boss_color[0]//3, boss_color[1]//3, boss_color[2]//3) if is_current else (25, 30, 45)
        draw_cyber_rect(screen, icon_rect, bg_col, alpha=200, cut_size=4, fill=True)
        draw_cyber_rect(screen, icon_rect, boss_color if is_current else (60, 70, 90), cut_size=4, border_width=1, fill=False)
        
        # 序号
        num_col = WHITE if is_current else (100, 110, 130)
        draw_text(screen, str(i + 1), 11, ix + icon_size//2, iy + icon_size//2 - 5, num_col, glow=is_current)
    
    # 统计信息框
    stat_y = preview_y + ((len(enabled_bosses) + icons_per_row - 1) // icons_per_row) * (icon_size + 5) + 12
    
    # 分隔装饰
    pygame.draw.line(screen, MAGENTA, (right_x + 12, stat_y), (right_x + right_width - 12, stat_y), 1)
    pygame.draw.circle(screen, MAGENTA, (right_x + 12, stat_y), 2)
    pygame.draw.circle(screen, MAGENTA, (right_x + right_width - 12, stat_y), 2)
    stat_y += 15
    
    # 计算总难度 - 只计算已启用的Boss
    total_armor = sum(BOSS_DB[k].get("stats", [(0,0)])[0][1] if BOSS_DB[k].get("stats") else 0 for k in enabled_bosses)
    total_damage = sum(BOSS_DB[k].get("stats", [(0,0),(0,0)])[1][1] if len(BOSS_DB[k].get("stats", [])) > 1 else 0 for k in enabled_bosses)
    
    stats_info = [
        ("◈", "已选Boss", f"{len(enabled_bosses)}/{len(boss_challenge_order)}", CYAN),
        ("◆", "总装甲值", f"{total_armor}", LIME),
        ("◇", "总毁灭力", f"{total_damage}", ORANGE),
        ("○", "预计时长", f"{len(enabled_bosses) * 2}~{len(enabled_bosses) * 4}分", (150, 160, 180)),
    ]
    
    # 统计背景框
    stat_box = pygame.Rect(right_x + 8, stat_y - 5, right_width - 16, len(stats_info) * 22 + 10)
    draw_cyber_rect(screen, stat_box, (18, 25, 42), alpha=180, cut_size=5, fill=True)
    
    stat_emoji_font = pygame.font.SysFont("Segoe UI Emoji", 12)
    for icon, label, value, col in stats_info:
        # emoji图标单独渲染
        icon_surf = stat_emoji_font.render(icon, True, (120, 130, 150))
        screen.blit(icon_surf, (right_x + 18, stat_y - icon_surf.get_height()//2))
        draw_text(screen, label, 12, right_x + 18 + icon_surf.get_width() + 2, stat_y, (120, 130, 150), align="left")
        draw_text(screen, value, 13, right_x + right_width - 18, stat_y, col, align="right", glow=(col != (150, 160, 180)))
        stat_y += 22
    
    # 难度评级
    stat_y += 12
    pygame.draw.line(screen, MAGENTA, (right_x + 12, stat_y - 5), (right_x + right_width - 12, stat_y - 5), 1)
    
    difficulty = min(5, max(1, (total_armor + total_damage) // 200))
    diff_labels = ["轻松", "普通", "困难", "噩梦", "地狱"]
    diff_colors = [LIME, CYAN, YELLOW, ORANGE, RED]
    
    draw_text(screen, "◆ 难度评级", 13, right_x + 18, stat_y, (120, 130, 150), align="left")
    draw_text(screen, diff_labels[difficulty - 1], 15, right_x + right_width - 18, stat_y, diff_colors[difficulty - 1], align="right", glow=True)
    
    # 难度条 - 更精致
    stat_y += 26
    bar_total_w = right_width - 36
    bar_w = bar_total_w // 5
    for i in range(5):
        bx = right_x + 18 + i * bar_w
        bar_rect = pygame.Rect(bx, stat_y, bar_w - 3, 16)
        if i < difficulty:
            draw_cyber_rect(screen, bar_rect, diff_colors[i], alpha=230, cut_size=3, fill=True)
            # 高光
            pygame.draw.line(screen, WHITE, (bx + 2, stat_y + 2), (bx + bar_w - 6, stat_y + 2), 1)
        else:
            draw_cyber_rect(screen, bar_rect, (28, 35, 52), alpha=180, cut_size=3, fill=True)
            draw_cyber_rect(screen, bar_rect, (50, 60, 80), cut_size=3, border_width=1, fill=False)
    
    # ====== 底部：开始按钮 ======
    btn_y = HEIGHT - 60
    btn_width = 240
    btn_height = 50
    btn_x = WIDTH // 2 - btn_width // 2
    btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
    
    btn_hover = btn_rect.collidepoint(mx, my)
    can_start = len(enabled_bosses) > 0  # 至少选择1个Boss才能开始
    
    # 按钮光晕效果
    if btn_hover and can_start:
        glow_rect = btn_rect.inflate(8 + int(4 * pulse), 8 + int(4 * pulse))
        draw_cyber_rect(screen, glow_rect, CYAN, alpha=80, fill=True)
    
    # 赛博风格按钮
    if can_start:
        btn_bg = (50, 80, 130) if btn_hover else (25, 40, 70)
        btn_border = (0, 255, 255) if btn_hover else (80, 160, 220)
    else:
        btn_bg = (40, 40, 50)
        btn_border = (80, 80, 100)
    draw_cyber_rect(screen, btn_rect, btn_bg, alpha=240, fill=True)
    draw_cyber_rect(screen, btn_rect, btn_border, border_width=3 if btn_hover and can_start else 2, fill=False)
    
    # 按钮装饰
    pygame.draw.line(screen, btn_border, (btn_x + 15, btn_y + btn_height//2), (btn_x + 30, btn_y + btn_height//2), 2)
    pygame.draw.line(screen, btn_border, (btn_x + btn_width - 30, btn_y + btn_height//2), (btn_x + btn_width - 15, btn_y + btn_height//2), 2)
    
    if can_start:
        # 分离渲染: ▶◀用emoji字体
        btn_color = WHITE if btn_hover else CYAN
        btn_emoji_font = pygame.font.SysFont("Segoe UI Emoji", 22)
        btn_text_font = pygame.font.SysFont("SimHei", 22)
        left_arrow = btn_emoji_font.render("▶", True, btn_color)
        right_arrow = btn_emoji_font.render("◀", True, btn_color)
        btn_txt = btn_text_font.render(f" 开始挑战 ({len(enabled_bosses)}) ", True, btn_color)
        btn_total_w = left_arrow.get_width() + btn_txt.get_width() + right_arrow.get_width()
        btn_start_x = btn_rect.centerx - btn_total_w//2
        btn_y_pos = btn_rect.centery - left_arrow.get_height()//2
        screen.blit(left_arrow, (btn_start_x, btn_y_pos))
        screen.blit(btn_txt, (btn_start_x + left_arrow.get_width(), btn_rect.centery - btn_txt.get_height()//2))
        screen.blit(right_arrow, (btn_start_x + left_arrow.get_width() + btn_txt.get_width(), btn_y_pos))
    else:
        draw_text(screen, "请至少选择1个Boss", 18, btn_rect.centerx, btn_rect.centery - 9, (120, 120, 130))

def draw_achievement_notifications():
    """绘制成就通知弹窗 - 豪华版：从右侧弹出停留后弹回"""
    global achievement_notifications
    
    t = pygame.time.get_ticks()
    
    # 更新和绘制所有通知
    for i, (achievement, timer) in enumerate(achievement_notifications[:3]):  # 最多显示3个
        y = 80 + i * 110
        total_time = 180.0  # 3秒
        
        # 分三个阶段：弹入(60帧) + 停留(60帧) + 弹回(60帧)
        if timer > 120:  # 弹入阶段 (60-180帧)
            phase_progress = (total_time - timer) / 60.0  # 0 -> 1
            # 缓动函数：ease-out
            ease_progress = 1 - (1 - phase_progress) ** 3
            slide_x = WIDTH + 20 - int(400 * ease_progress)
            alpha = int(255 * min(1, phase_progress * 2))
        elif timer > 60:  # 停留阶段 (60-120帧)
            slide_x = WIDTH - 380
            alpha = 255
        else:  # 弹回阶段 (0-60帧)
            phase_progress = (60 - timer) / 60.0  # 0 -> 1
            # 缓动函数：ease-in
            ease_progress = phase_progress ** 2
            slide_x = WIDTH - 380 + int(400 * ease_progress)
            alpha = int(255 * max(0, 1 - phase_progress * 2))
        
        # 绘制通知背景
        surface = pygame.Surface((380, 95), pygame.SRCALPHA)
        
        # 背景框 - 渐变效果 + 金色高亮
        for sy in range(95):
            bg_alpha = int(220 * (alpha / 255))
            ratio = sy / 95
            r = int(20 + 15 * ratio)
            g = int(35 + 20 * ratio)
            b = int(55 + 25 * ratio)
            pygame.draw.line(surface, (r, g, b, bg_alpha), (0, sy), (380, sy))
        
        # 外边框 - 金色发光
        glow_alpha = int(alpha * 0.4)
        pygame.draw.rect(surface, (255, 200, 50, glow_alpha), (0, 0, 380, 95), 3, border_radius=8)
        pygame.draw.rect(surface, (255, 220, 100, alpha), (0, 0, 380, 95), 2, border_radius=6)
        
        # 左侧金色装饰条
        pygame.draw.rect(surface, (255, 200, 50, alpha), (0, 0, 5, 95), border_radius=2)
        
        # 内部光效（脉冲）
        pulse = int(30 + 20 * math.sin(t / 150))
        pygame.draw.rect(surface, (255, 220, 100, pulse), (5, 5, 370, 85), 1, border_radius=4)
        
        # 绘制到屏幕
        screen.blit(surface, (slide_x, y))
        
        # 绘制星星装饰（使用缓存字体）
        star_font = get_ach_font("Segoe UI Emoji", 22)
        star_left = star_font.render("⭐", True, GOLD)
        screen.blit(star_left, (slide_x + 15, y + 12))
        
        # 标题
        title_font = get_ach_font("SimHei", 16)
        title_text = title_font.render("成就解锁!", True, GOLD)
        screen.blit(title_text, (slide_x + 45, y + 15))
        
        # 成就名称（大字）
        name_font = get_ach_font("SimHei", 22)
        name_text = name_font.render(achievement.name, True, WHITE)
        screen.blit(name_text, (slide_x + 20, y + 40))
        
        # 稀有度标签
        rarity_font = get_ach_font("SimHei", 13)
        rarity_text = rarity_font.render(f"【{achievement.rarity_name}】", True, achievement.rarity_color)
        screen.blit(rarity_text, (slide_x + 25 + name_text.get_width(), y + 45))
        
        # 奖励分数（右下角）
        reward_emoji = get_ach_font("Segoe UI Emoji", 14)
        reward_font = get_ach_font("SimHei", 16)
        gem_icon = reward_emoji.render("💎", True, GOLD)
        reward_text = reward_font.render(f"+{achievement.reward:,}", True, GOLD)
        screen.blit(gem_icon, (slide_x + 300, y + 65))
        screen.blit(reward_text, (slide_x + 322, y + 67))
        
        # 底部装饰线
        line_alpha = int(100 * (alpha / 255))
        pygame.draw.line(screen, (255, 200, 50, line_alpha), (slide_x + 20, y + 88), (slide_x + 360, y + 88), 1)
        
        # 递减计时器
        achievement_notifications[achievement_notifications.index((achievement, timer))] = (achievement, timer - 1)
    
    # 移除已过期的通知
    achievement_notifications[:] = [(a, t) for a, t in achievement_notifications if t > 0]

def draw_synergy_notifications():
    """【新】绘制协同触发通知 - 屏幕中心爆发式提示"""
    global synergy_notifications
    
    for i, (synergy_data, timer, _) in enumerate(synergy_notifications[:2]):  # 最多显示2个
        total_time = 150.0  # 2.5秒
        progress = (total_time - timer) / total_time  # 0 -> 1
        
        # 三阶段动画：爆发(30帧) + 停留(90帧) + 淡出(30帧)
        if timer > 120:  # 爆发阶段
            scale = 0.3 + progress * 7.0  # 快速放大
            alpha = int(255 * min(1, progress * 10))
        elif timer > 30:  # 停留阶段
            scale = 1.0
            alpha = 255
        else:  # 淡出阶段
            scale = 1.0 + (1 - timer / 30.0) * 0.2  # 轻微放大
            alpha = int(255 * (timer / 30.0))
        
        # 位置 - 屏幕中心偏上，多个协同错开显示
        y_offset = HEIGHT // 3 + i * 80
        center_x = WIDTH // 2
        center_y = y_offset
        
        # 背景光晕效果
        if timer > 120:
            glow_radius = int(150 * progress * 3)
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            glow_color = synergy_data.get('visual', {}).get('color', (255, 200, 0))
            pygame.draw.circle(glow_surf, (*glow_color, min(80, int(alpha * 0.3))), 
                             (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (center_x - glow_radius, center_y - glow_radius))
        
        # 协同名称 - 大字
        name_size = int(32 * scale)
        name_color = synergy_data.get('visual', {}).get('color', (255, 200, 0))
        draw_text(screen, synergy_data['name'], name_size, center_x, center_y - 20, 
                 (*name_color, alpha), glow=True)
        
        # 协同描述 - 小字
        desc_size = int(16 * min(1, scale))
        draw_text(screen, synergy_data.get('desc', ''), desc_size, center_x, center_y + 25, 
                 (255, 255, 255, alpha))
        
        # 装饰粒子效果
        if timer > 120 and random.random() < 0.3:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(50, 150)
            px = center_x + math.cos(angle) * dist
            py = center_y + math.sin(angle) * dist
            Particle((int(px), int(py)), name_color)
        
        # 递减计时器
        idx = synergy_notifications.index((synergy_data, timer, _))
        synergy_notifications[idx] = (synergy_data, timer - 1, _)
    
    # 移除已过期的通知
    synergy_notifications[:] = [(s, t, time) for s, t, time in synergy_notifications if t > 0]

def draw_achievements_ui():
    """绘制成就殿堂 - 至尊豪华版"""
    global player, achievement_page, achievement_category, achievement_selected, achievement_scroll_y
    
    try:
        _draw_achievements_ui_inner()
    except Exception as e:
        # 防止渲染异常导致界面卡死（参考Bug #002/#003）
        log_error(f"成就界面渲染异常: {e}")
        import traceback
        traceback.print_exc()
        # 显示错误提示并允许返回
        screen.fill((20, 20, 30))
        draw_text(screen, "成就界面加载出错", 24, WIDTH//2, HEIGHT//2 - 30, (255, 100, 100))
        draw_text(screen, f"错误: {str(e)[:50]}", 16, WIDTH//2, HEIGHT//2 + 10, GRAY)
        draw_text(screen, "按 ESC 返回主菜单", 18, WIDTH//2, HEIGHT//2 + 50, WHITE)

def _draw_achievements_ui_inner():
    """成就界面内部渲染（被try-except包裹）"""
    global player, achievement_page, achievement_category, achievement_selected, achievement_scroll_y
    
    t = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    
    # ========== 布局常量 (1280x720) ==========
    MARGIN = 30           # 边距
    HEADER_H = 70         # 标题区高度（增大）
    STATS_H = 45          # 统计栏高度（增大）
    TAB_H = 45            # 分类标签高度
    FOOTER_H = 70         # 底部区高度
    CONTENT_GAP = 8       # 内容间距
    
    # 计算内容区域
    content_top = MARGIN + HEADER_H + STATS_H + TAB_H + CONTENT_GAP
    content_bottom = HEIGHT - FOOTER_H - MARGIN
    content_h = content_bottom - content_top
    
    # ====== 豪华深空背景 ======
    screen.fill((5, 8, 15))
    
    # 动态星云背景层
    for i in range(3):
        nebula_x = WIDTH // 2 + int(150 * math.sin(t / 3000 + i * 2))
        nebula_y = HEIGHT // 2 + int(100 * math.cos(t / 2500 + i * 1.5))
        nebula_size = 250 + int(50 * math.sin(t / 2000 + i))
        nebula_surf = pygame.Surface((nebula_size * 2, nebula_size * 2), pygame.SRCALPHA)
        nebula_colors = [(40, 20, 60), (20, 40, 60), (50, 30, 40)]
        for r in range(nebula_size, 0, -5):
            alpha = int(15 * (1 - r / nebula_size))
            pygame.draw.circle(nebula_surf, (*nebula_colors[i], alpha), (nebula_size, nebula_size), r)
        screen.blit(nebula_surf, (nebula_x - nebula_size, nebula_y - nebula_size))
    
    # 动态星空粒子（多层次）
    for i in range(60):
        star_x = (i * 137 + int(t / (40 + i % 30))) % WIDTH
        star_y = (i * 89 + int(t / (60 + i % 40))) % HEIGHT
        depth = (i % 3) + 1  # 深度层次
        star_alpha = int((40 + 30 * depth) + 30 * math.sin(t / (300 + i * 10) + i))
        # 使用确定性计算避免闪烁
        star_size = 2 if (depth >= 2 and i % 7 == 0) else 1
        star_color = (star_alpha, int(star_alpha * 1.05), int(star_alpha * 1.2))
        pygame.draw.circle(screen, star_color, (star_x, star_y), star_size)
    
    # 流星效果（偶尔出现）
    if (t // 100) % 80 < 3:
        meteor_progress = ((t // 100) % 80) / 3.0
        meteor_x = int(200 + meteor_progress * 400)
        meteor_y = int(50 + meteor_progress * 150)
        for trail in range(8):
            trail_alpha = int(180 * (1 - trail / 8))
            trail_x = meteor_x - trail * 15
            trail_y = meteor_y - trail * 6
            pygame.draw.circle(screen, (255, 220, 150, trail_alpha), (trail_x, trail_y), 3 - trail // 3)
    
    # 六边形网格背景（淡雅）
    hex_alpha = int(12 + 6 * math.sin(t / 1500))
    hex_color = (hex_alpha, int(hex_alpha * 1.3), int(hex_alpha * 0.8))
    hex_size = 80
    for row in range(-1, HEIGHT // hex_size + 2):
        for col in range(-1, WIDTH // hex_size + 2):
            cx = col * hex_size * 1.5 + (row % 2) * hex_size * 0.75
            cy = row * hex_size * 0.866
            points = []
            for angle in range(6):
                px = cx + hex_size * 0.35 * math.cos(math.radians(60 * angle + 30))
                py = cy + hex_size * 0.35 * math.sin(math.radians(60 * angle + 30))
                points.append((px, py))
            if len(points) >= 3:
                pygame.draw.polygon(screen, hex_color, points, 1)
    
    # 边框发光装饰
    glow_intensity = int(120 + 60 * math.sin(t / 500))
    border_color = (int(glow_intensity * 0.9), glow_intensity, int(glow_intensity * 0.5))
    pygame.draw.rect(screen, border_color, (0, 0, WIDTH, 2))
    pygame.draw.rect(screen, border_color, (0, HEIGHT - 2, WIDTH, 2))
    
    # 角落霓虹装饰
    corner_size = 40
    for corner in [(0, 0, 1, 1), (WIDTH, 0, -1, 1), (0, HEIGHT, 1, -1), (WIDTH, HEIGHT, -1, -1)]:
        cx, cy, dx, dy = corner
        pygame.draw.line(screen, GOLD, (cx, cy + dy * 3), (cx, cy + dy * corner_size), 2)
        pygame.draw.line(screen, GOLD, (cx + dx * 3, cy), (cx + dx * corner_size, cy), 2)
        pygame.draw.circle(screen, (255, 200, 50), (cx + dx * 6, cy + dy * 6), 2)
    
    # 获取成就管理器（使用缓存）
    achievement_mgr = None
    if player and hasattr(player, 'achievement_manager'):
        achievement_mgr = player.achievement_manager
    else:
        achievement_mgr = get_cached_achievement_mgr()
    
    # ====== 豪华标题区 ======
    title_panel = pygame.Rect(WIDTH//2 - 220, 12, 440, 58)
    # 标题背景渐变
    title_bg = pygame.Surface((440, 58), pygame.SRCALPHA)
    for ty in range(58):
        alpha = int(180 - ty * 2.5)
        pygame.draw.line(title_bg, (50, 45, 20, alpha), (0, ty), (440, ty))
    screen.blit(title_bg, title_panel.topleft)
    # 标题边框
    pygame.draw.rect(screen, GOLD, title_panel, 2, border_radius=8)
    # 内发光
    inner_rect = title_panel.inflate(-6, -6)
    pygame.draw.rect(screen, (255, 220, 100, 40), inner_rect, 1, border_radius=6)
    
    # 标题文字带光晕
    title_glow = int(255 * (0.85 + 0.15 * math.sin(t / 350)))
    title_y = MARGIN
    emoji_font = get_ach_font("Segoe UI Emoji", 32)
    title_font = get_ach_font("SimHei", 36)
    trophy_left = emoji_font.render("🏆", True, (title_glow, int(title_glow * 0.85), 0))
    title_text = title_font.render("成就殿堂", True, (title_glow, int(title_glow * 0.85), 0))
    trophy_right = emoji_font.render("🏆", True, (title_glow, int(title_glow * 0.85), 0))
    total_w = trophy_left.get_width() + 15 + title_text.get_width() + 15 + trophy_right.get_width()
    start_x = WIDTH//2 - total_w//2
    screen.blit(trophy_left, (start_x, title_y + 3))
    screen.blit(title_text, (start_x + trophy_left.get_width() + 15, title_y))
    screen.blit(trophy_right, (start_x + trophy_left.get_width() + 15 + title_text.get_width() + 15, title_y + 3))
    
    # 标题下方装饰线
    line_y = title_y + 50
    line_w = 350
    pygame.draw.line(screen, (80, 70, 35), (WIDTH//2 - line_w//2, line_y), (WIDTH//2 + line_w//2, line_y), 1)
    # 中心菱形装饰
    diamond_x = WIDTH // 2
    pygame.draw.polygon(screen, GOLD, [(diamond_x, line_y - 5), (diamond_x + 6, line_y), (diamond_x, line_y + 5), (diamond_x - 6, line_y)])
    
    if not achievement_mgr:
        # 未加载状态 - 美化版
        empty_surf = pygame.Surface((400, 200), pygame.SRCALPHA)
        pygame.draw.rect(empty_surf, (25, 28, 38, 200), (0, 0, 400, 200), border_radius=15)
        pygame.draw.rect(empty_surf, (100, 100, 120), (0, 0, 400, 200), 2, border_radius=15)
        screen.blit(empty_surf, (WIDTH//2 - 200, HEIGHT//2 - 100))
        
        empty_emoji = get_ach_font("Segoe UI Emoji", 48)
        empty_icon = empty_emoji.render("🎮", True, (80, 85, 100))
        screen.blit(empty_icon, (WIDTH//2 - empty_icon.get_width()//2, HEIGHT//2 - 70))
        draw_text(screen, "尚未开始游戏", 22, WIDTH//2, HEIGHT//2 + 10, (150, 155, 170))
        draw_text(screen, "成就数据将在游戏后加载", 16, WIDTH//2, HEIGHT//2 + 40, GRAY)
        
        back_btn = pygame.Rect(WIDTH//2 - 70, HEIGHT//2 + 75, 140, 42)
        h = back_btn.collidepoint(mx, my)
        pygame.draw.rect(screen, (40, 45, 55) if not h else (60, 65, 80), back_btn, border_radius=10)
        pygame.draw.rect(screen, GOLD if h else (100, 100, 120), back_btn, 2, border_radius=10)
        draw_text(screen, "返 回", 18, back_btn.centerx, back_btn.centery - 9, WHITE)
        return
    
    # ====== 豪华统计栏 ======
    stats_y = MARGIN + HEADER_H
    stats_panel = pygame.Rect(MARGIN + 10, stats_y, WIDTH - MARGIN * 2 - 20, 40)
    # 统计栏背景
    stats_bg = pygame.Surface((stats_panel.width, stats_panel.height), pygame.SRCALPHA)
    pygame.draw.rect(stats_bg, (20, 25, 35, 200), (0, 0, stats_panel.width, stats_panel.height), border_radius=8)
    screen.blit(stats_bg, stats_panel.topleft)
    pygame.draw.rect(screen, (60, 65, 80), stats_panel, 1, border_radius=8)
    
    stats_font = get_ach_font("SimHei", 17)
    stats_emoji = get_ach_font("Segoe UI Emoji", 16)
    
    unlocked_count = sum(1 for a in achievement_mgr.achievements.values() if a.unlocked)
    total_count = len(achievement_mgr.achievements)
    percent = int(unlocked_count / total_count * 100) if total_count > 0 else 0
    total_reward = achievement_mgr.get_total_reward()
    legendary_count = sum(1 for a in achievement_mgr.achievements.values() if a.unlocked and a.rarity == "legendary")
    legendary_total = sum(1 for a in achievement_mgr.achievements.values() if a.rarity == "legendary")
    
    # 左：解锁进度 + 进度条
    trophy_icon = stats_emoji.render("🏆", True, CYAN)
    prog_text = stats_font.render(f"已解锁 {unlocked_count}/{total_count}", True, CYAN)
    screen.blit(trophy_icon, (stats_panel.x + 15, stats_y + 8))
    screen.blit(prog_text, (stats_panel.x + 40, stats_y + 10))
    
    # 小进度条
    prog_bar_x = stats_panel.x + 175
    prog_bar_w = 120
    prog_bar_h = 10
    pygame.draw.rect(screen, (40, 45, 55), (prog_bar_x, stats_y + 15, prog_bar_w, prog_bar_h), border_radius=5)
    fill_w = int(prog_bar_w * percent / 100)
    if fill_w > 0:
        # 渐变填充
        fill_surf = pygame.Surface((fill_w, prog_bar_h), pygame.SRCALPHA)
        for px in range(fill_w):
            ratio = px / prog_bar_w
            color = (int(80 + 175 * ratio), int(200 - 50 * ratio), int(220 - 100 * ratio))
            pygame.draw.line(fill_surf, color, (px, 0), (px, prog_bar_h))
        screen.blit(fill_surf, (prog_bar_x, stats_y + 15))
        # 边框高光
        pygame.draw.rect(screen, CYAN, (prog_bar_x, stats_y + 15, fill_w, prog_bar_h), 1, border_radius=5)
    percent_text = get_ach_font("SimHei", 11)
    pct_surf = percent_text.render(f"{percent}%", True, WHITE)
    screen.blit(pct_surf, (prog_bar_x + prog_bar_w + 8, stats_y + 12))
    
    # 中：总奖励
    gem_icon = stats_emoji.render("💎", True, GOLD)
    reward_text = stats_font.render(f"总奖励 {total_reward:,}分", True, GOLD)
    mid_x = WIDTH // 2 - 80
    screen.blit(gem_icon, (mid_x, stats_y + 8))
    screen.blit(reward_text, (mid_x + 28, stats_y + 10))
    
    # 右：传说成就
    star_icon = stats_emoji.render("⭐", True, (255, 180, 50))
    rare_text = stats_font.render(f"传说成就 {legendary_count}/{legendary_total}", True, (255, 180, 50))
    screen.blit(star_icon, (stats_panel.right - 200, stats_y + 8))
    screen.blit(rare_text, (stats_panel.right - 172, stats_y + 10))
    
    # ====== 豪华分类标签 ======
    categories = [
        ("all", "📚", "全部", (100, 180, 255)),
        ("combat", "⚔️", "战斗", (255, 80, 80)),
        ("boss", "👹", "Boss", (220, 100, 220)),
        ("survival", "🛡️", "生存", (80, 200, 80)),
        ("plane", "✈️", "机体", (80, 180, 240)),
        ("roguelike", "🚪", "肉鸽", (220, 160, 80)),
        ("milestone", "🏅", "里程碑", (200, 200, 80)),
        ("secret", "🌙", "隐藏", (150, 120, 180)),
    ]
    
    tab_y = MARGIN + HEADER_H + STATS_H + 5
    tab_h = 38
    tab_emoji_font = get_ach_font("Segoe UI Emoji", 16)
    tab_font = get_ach_font("SimHei", 15)
    
    # 计算所有标签总宽度来居中
    tab_widths = []
    for cat_id, cat_emoji, cat_name, _ in categories:
        emoji_surf = tab_emoji_font.render(cat_emoji, True, WHITE)
        text_surf = tab_font.render(cat_name, True, WHITE)
        tab_widths.append(emoji_surf.get_width() + text_surf.get_width() + 26)
    total_tabs_w = sum(tab_widths) + 6 * (len(categories) - 1)
    tab_start_x = (WIDTH - total_tabs_w) // 2
    
    for i, (cat_id, cat_emoji, cat_name, cat_color) in enumerate(categories):
        tab_w = tab_widths[i]
        tab_rect = pygame.Rect(tab_start_x, tab_y, tab_w, tab_h)
        is_selected = (achievement_category == cat_id)
        is_hover = tab_rect.collidepoint(mx, my)
        
        # 标签背景 - 渐变效果
        tab_bg = pygame.Surface((tab_w, tab_h), pygame.SRCALPHA)
        if is_selected:
            for ty in range(tab_h):
                alpha = int(200 - ty * 3)
                r, g, b = cat_color
                pygame.draw.line(tab_bg, (r//3, g//3, b//3, alpha), (0, ty), (tab_w, ty))
            screen.blit(tab_bg, tab_rect.topleft)
            pygame.draw.rect(screen, cat_color, tab_rect, 2, border_radius=6)
            # 底部高亮条
            pygame.draw.rect(screen, cat_color, (tab_rect.x + 8, tab_rect.bottom - 3, tab_rect.width - 16, 3), border_radius=2)
            # 发光效果
            glow_rect = tab_rect.inflate(3, 3)
            pygame.draw.rect(screen, (*cat_color, 60), glow_rect, 1, border_radius=8)
        elif is_hover:
            pygame.draw.rect(tab_bg, (50, 55, 68, 220), (0, 0, tab_w, tab_h), border_radius=6)
            screen.blit(tab_bg, tab_rect.topleft)
            pygame.draw.rect(screen, (140, 145, 160), tab_rect, 1, border_radius=6)
        else:
            pygame.draw.rect(tab_bg, (28, 32, 42, 200), (0, 0, tab_w, tab_h), border_radius=6)
            screen.blit(tab_bg, tab_rect.topleft)
            pygame.draw.rect(screen, (55, 60, 75), tab_rect, 1, border_radius=6)
        
        # 标签内容
        text_color = cat_color if is_selected else (WHITE if is_hover else (160, 165, 180))
        emoji_s = tab_emoji_font.render(cat_emoji, True, text_color)
        text_s = tab_font.render(cat_name, True, text_color)
        total_content_w = emoji_s.get_width() + 4 + text_s.get_width()
        content_start = tab_rect.x + (tab_w - total_content_w) // 2
        screen.blit(emoji_s, (content_start, tab_rect.y + 9))
        screen.blit(text_s, (content_start + emoji_s.get_width() + 4, tab_rect.y + 10))
        
        tab_start_x += tab_w + 6
    
    # ====== 内容区：左边收藏墙 + 右边详情 ======
    wall_w = int((WIDTH - MARGIN * 3) * 0.58)  # 58%给收藏墙
    detail_w = WIDTH - MARGIN * 3 - wall_w
    
    wall_rect = pygame.Rect(MARGIN, content_top, wall_w, content_h)
    detail_rect = pygame.Rect(MARGIN * 2 + wall_w, content_top, detail_w, content_h)
    
    # --- 收藏墙（豪华版）---
    wall_bg = pygame.Surface((wall_rect.width, wall_rect.height), pygame.SRCALPHA)
    # 渐变背景
    for wy in range(wall_rect.height):
        alpha = int(240 - wy * 0.15)
        pygame.draw.line(wall_bg, (15, 18, 28, alpha), (0, wy), (wall_rect.width, wy))
    screen.blit(wall_bg, wall_rect.topleft)
    # 双层边框
    pygame.draw.rect(screen, (70, 75, 95), wall_rect, 2, border_radius=12)
    inner_wall = wall_rect.inflate(-6, -6)
    pygame.draw.rect(screen, (40, 45, 60), inner_wall, 1, border_radius=10)
    
    # 获取当前分类的成就
    if achievement_category == "all":
        filtered_achievements = list(achievement_mgr.achievements.values())
    else:
        filtered_achievements = achievement_mgr.get_achievements_by_category(achievement_category)
    
    # 网格布局（更大的徽章）
    grid_cell = 95
    grid_gap = 12
    grid_cols = max(1, (wall_w - 40) // (grid_cell + grid_gap))  # 至少1列，防止除零
    grid_start_x = wall_rect.x + (wall_w - grid_cols * (grid_cell + grid_gap) + grid_gap) // 2
    grid_start_y = wall_rect.y + 18
    
    # 绘制成就徽章网格
    emoji_icon_font = get_ach_font("Segoe UI Emoji", 34)
    check_emoji_font = get_ach_font("Segoe UI Emoji", 15)
    name_font = get_ach_font("SimHei", 11)
    cat_emojis = {"combat": "⚔️", "boss": "👹", "survival": "🛡️", "plane": "✈️", "roguelike": "🚪", "efficiency": "⚡", "milestone": "🏅", "secret": "🌙"}
    
    # 裁剪区域 - 防止badge溢出wall_rect边界
    clip_rect = pygame.Rect(wall_rect.x, wall_rect.y, wall_rect.width, wall_rect.height - 35)
    old_clip = screen.get_clip()
    screen.set_clip(clip_rect)
    
    for i, ach in enumerate(filtered_achievements):
        col = i % grid_cols
        row = i // grid_cols
        
        bx = grid_start_x + col * (grid_cell + grid_gap)
        by = grid_start_y + row * (grid_cell + grid_gap) - achievement_scroll_y
        
        # 跳过不在可见区域的
        if by < wall_rect.y - grid_cell or by > wall_rect.bottom:
            continue
        
        badge_rect = pygame.Rect(bx, by, grid_cell, grid_cell)
        is_hover = badge_rect.collidepoint(mx, my) and wall_rect.collidepoint(mx, my)
        is_selected = (achievement_selected == ach.id)
        
        # 徽章背景（渐变）
        badge_bg = pygame.Surface((grid_cell, grid_cell), pygame.SRCALPHA)
        if ach.unlocked:
            rarity_bg = {
                "legendary": [(80, 65, 15), (50, 40, 10)], 
                "epic": [(60, 35, 70), (40, 20, 50)], 
                "rare": [(25, 55, 35), (15, 40, 25)], 
                "common": [(40, 45, 55), (30, 35, 45)]
            }
            bg_colors = rarity_bg.get(ach.rarity, [(40, 45, 55), (30, 35, 45)])
        else:
            bg_colors = [(30, 32, 38), (22, 24, 30)]
        
        for grad_y in range(grid_cell):
            ratio = grad_y / grid_cell
            r = int(bg_colors[0][0] * (1 - ratio) + bg_colors[1][0] * ratio)
            g = int(bg_colors[0][1] * (1 - ratio) + bg_colors[1][1] * ratio)
            b = int(bg_colors[0][2] * (1 - ratio) + bg_colors[1][2] * ratio)
            pygame.draw.line(badge_bg, (r, g, b, 230), (0, grad_y), (grid_cell, grad_y))
        
        # 圆角遮罩效果
        pygame.draw.rect(badge_bg, (0, 0, 0, 0), (0, 0, grid_cell, grid_cell), border_radius=10)
        screen.blit(badge_bg, badge_rect.topleft)
        pygame.draw.rect(screen, (0, 0, 0, 0), badge_rect, border_radius=10)
        
        # 边框（多层效果）
        if is_selected:
            # 选中态 - 金色发光
            glow_rect = badge_rect.inflate(6, 6)
            pygame.draw.rect(screen, (*GOLD, 80), glow_rect, 2, border_radius=12)
            pygame.draw.rect(screen, GOLD, badge_rect, 3, border_radius=10)
        elif is_hover:
            pygame.draw.rect(screen, WHITE, badge_rect, 2, border_radius=10)
        elif ach.unlocked:
            pygame.draw.rect(screen, ach.rarity_color, badge_rect, 2, border_radius=10)
            # 内发光
            inner_badge = badge_rect.inflate(-4, -4)
            pygame.draw.rect(screen, (*ach.rarity_color, 40), inner_badge, 1, border_radius=8)
        else:
            pygame.draw.rect(screen, (55, 58, 68), badge_rect, 1, border_radius=10)
        
        # 图标
        if ach.unlocked or not ach.hidden:
            icon_color = ach.rarity_color if ach.unlocked else (90, 92, 100)
            icon_char = cat_emojis.get(ach.category, "⭐")
            icon_surf = emoji_icon_font.render(icon_char, True, icon_color)
        else:
            icon_surf = emoji_icon_font.render("❓", True, (65, 68, 75))
        screen.blit(icon_surf, (bx + grid_cell//2 - icon_surf.get_width()//2, by + 8))
        
        # 勾选标记（更精致）
        if ach.unlocked:
            check_bg = pygame.Surface((22, 22), pygame.SRCALPHA)
            pygame.draw.circle(check_bg, (30, 180, 80, 200), (11, 11), 10)
            screen.blit(check_bg, (bx + grid_cell - 24, by + grid_cell - 24))
            check = check_emoji_font.render("✓", True, WHITE)
            screen.blit(check, (bx + grid_cell - 20, by + grid_cell - 22))
        
        # 稀有度指示点（传说成就）
        if ach.rarity == "legendary":
            for dot in range(3):
                dot_x = bx + 10 + dot * 8
                dot_color = GOLD if ach.unlocked else (80, 70, 40)
                pygame.draw.circle(screen, dot_color, (dot_x, by + grid_cell - 10), 3)
        
        # 名称
        if ach.hidden and not ach.unlocked:
            short_name = "???"
        else:
            short_name = ach.name[:6] if len(ach.name) > 6 else ach.name
        name_color = WHITE if ach.unlocked else (80, 82, 90)
        name_surf = name_font.render(short_name, True, name_color)
        screen.blit(name_surf, (bx + grid_cell//2 - name_surf.get_width()//2, by + 50))
    
    # 恢复裁剪区域
    screen.set_clip(old_clip)
    
    # --- 滚动条指示器（美化版）---
    rows = (len(filtered_achievements) + grid_cols - 1) // grid_cols
    total_content_h = rows * (grid_cell + grid_gap)
    view_h = wall_rect.height - TAB_H - 60
    if total_content_h > view_h:
        scroll_bar_x = wall_rect.right - 14
        scroll_bar_y = grid_start_y
        scroll_bar_h = view_h
        max_scroll = total_content_h - view_h
        # 滚动条轨道
        pygame.draw.rect(screen, (35, 40, 52), (scroll_bar_x, scroll_bar_y, 8, scroll_bar_h), border_radius=4)
        # 滚动条滑块（渐变）
        thumb_h = max(35, int(scroll_bar_h * view_h / total_content_h))
        thumb_y = scroll_bar_y + int((scroll_bar_h - thumb_h) * achievement_scroll_y / max_scroll) if max_scroll > 0 else scroll_bar_y
        thumb_surf = pygame.Surface((8, thumb_h), pygame.SRCALPHA)
        for ty in range(thumb_h):
            ratio = ty / thumb_h
            r = int(100 + 40 * (1 - ratio))
            g = int(110 + 50 * (1 - ratio))
            b = int(140 + 60 * (1 - ratio))
            pygame.draw.line(thumb_surf, (r, g, b, 220), (0, ty), (8, ty))
        screen.blit(thumb_surf, (scroll_bar_x, thumb_y))
        pygame.draw.rect(screen, (150, 160, 190), (scroll_bar_x, thumb_y, 8, thumb_h), 1, border_radius=4)
    
    # 收藏墙底部分类统计（美化版）
    cat_label_font = get_ach_font("SimHei", 14)
    cat_emoji_font = get_ach_font("Segoe UI Emoji", 12)
    if achievement_category == "all":
        cat_label = f"全部成就 {unlocked_count}/{total_count}"
        cat_emoji = "📚"
    else:
        cat_stats = achievement_mgr.get_category_stats().get(achievement_category, {"unlocked": 0, "total": 0})
        cat_names = {"combat": "战斗", "boss": "Boss", "survival": "生存", "plane": "机体", "roguelike": "肉鸽", "efficiency": "效率", "milestone": "里程碑", "secret": "隐藏"}
        cat_emojis_map = {"combat": "⚔️", "boss": "👹", "survival": "🛡️", "plane": "✈️", "roguelike": "🚪", "efficiency": "⚡", "milestone": "🏅", "secret": "🌙"}
        cat_label = f"{cat_names.get(achievement_category, achievement_category)}成就 {cat_stats['unlocked']}/{cat_stats['total']}"
        cat_emoji = cat_emojis_map.get(achievement_category, "📚")
    
    emoji_surf = cat_emoji_font.render(cat_emoji, True, (140, 145, 165))
    cat_label_surf = cat_label_font.render(cat_label, True, (140, 145, 165))
    screen.blit(emoji_surf, (wall_rect.x + 15, wall_rect.bottom - 28))
    screen.blit(cat_label_surf, (wall_rect.x + 38, wall_rect.bottom - 26))
    
    # --- 详情面板（豪华版）---
    detail_bg = pygame.Surface((detail_rect.width, detail_rect.height), pygame.SRCALPHA)
    # 渐变背景
    for dy in range(detail_rect.height):
        alpha = int(235 - dy * 0.12)
        pygame.draw.line(detail_bg, (20, 24, 35, alpha), (0, dy), (detail_rect.width, dy))
    screen.blit(detail_bg, detail_rect.topleft)
    # 双层边框
    pygame.draw.rect(screen, (80, 85, 105), detail_rect, 2, border_radius=12)
    inner_detail = detail_rect.inflate(-6, -6)
    pygame.draw.rect(screen, (45, 50, 65), inner_detail, 1, border_radius=10)
    
    selected_ach = None
    if achievement_selected and achievement_selected in achievement_mgr.achievements:
        selected_ach = achievement_mgr.achievements[achievement_selected]
    
    if selected_ach:
        px = detail_rect.x + 25
        py = detail_rect.y + 22
        
        # 稀有度标签（带背景）
        rarity_font = get_ach_font("SimHei", 15)
        rarity_text = f"【{selected_ach.rarity_name}】"
        rarity_surf = rarity_font.render(rarity_text, True, selected_ach.rarity_color)
        rarity_bg = pygame.Surface((rarity_surf.get_width() + 16, 26), pygame.SRCALPHA)
        pygame.draw.rect(rarity_bg, (*selected_ach.rarity_color, 40), (0, 0, rarity_surf.get_width() + 16, 26), border_radius=5)
        screen.blit(rarity_bg, (px - 8, py - 3))
        screen.blit(rarity_surf, (px, py))
        
        # 成就名称（大字+图标）
        py += 35
        name_font = get_ach_font("SimHei", 26)
        emoji_font = get_ach_font("Segoe UI Emoji", 24)
        icon_char = cat_emojis.get(selected_ach.category, "⭐")
        icon_surf = emoji_font.render(icon_char, True, selected_ach.rarity_color if selected_ach.unlocked else GRAY)
        name_surf = name_font.render(selected_ach.name, True, WHITE if selected_ach.unlocked else (140, 140, 150))
        screen.blit(icon_surf, (px, py))
        screen.blit(name_surf, (px + 40, py))
        
        # 优雅分隔线
        py += 48
        line_w = detail_rect.width - 50
        pygame.draw.line(screen, (50, 55, 70), (px, py), (px + line_w, py), 1)
        # 中心装饰
        mid_x = px + line_w // 2
        pygame.draw.circle(screen, selected_ach.rarity_color if selected_ach.unlocked else (80, 85, 100), (mid_x, py), 4)
        pygame.draw.circle(screen, (30, 35, 48), (mid_x, py), 2)
        
        # 描述区域（带引号装饰）
        py += 18
        desc_font = get_ach_font("SimHei", 17)
        desc_text = "完成特定条件解锁..." if (selected_ach.hidden and not selected_ach.unlocked) else selected_ach.description
        
        # 引号装饰 - 简化版，避免字体渲染问题
        desc_surf = desc_font.render(desc_text, True, (190, 195, 210))
        screen.blit(desc_surf, (px + 5, py + 5))
        
        # 进度条（豪华版）
        py += 55
        current, target = achievement_mgr.get_progress(selected_ach.id)
        if target > 0:
            bar_w = detail_rect.width - 55
            bar_h = 26
            # 进度条背景
            bar_bg = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
            pygame.draw.rect(bar_bg, (30, 35, 48, 220), (0, 0, bar_w, bar_h), border_radius=13)
            screen.blit(bar_bg, (px, py))
            pygame.draw.rect(screen, (55, 60, 78), (px, py, bar_w, bar_h), 1, border_radius=13)
            
            fill_ratio = min(current / target, 1.0)
            fill_w = int((bar_w - 4) * fill_ratio)
            if fill_w > 0:
                # 渐变填充
                fill_surf = pygame.Surface((fill_w, bar_h - 4), pygame.SRCALPHA)
                for fx in range(fill_w):
                    ratio = fx / bar_w
                    if selected_ach.unlocked:
                        r, g, b = selected_ach.rarity_color
                        color = (int(r * 0.7 + r * 0.3 * ratio), int(g * 0.7 + g * 0.3 * ratio), int(b * 0.7 + b * 0.3 * ratio))
                    else:
                        color = (int(60 + 40 * ratio), int(100 + 50 * ratio), int(80 + 40 * ratio))
                    pygame.draw.line(fill_surf, (*color, 230), (fx, 0), (fx, bar_h - 4))
                screen.blit(fill_surf, (px + 2, py + 2))
                # 高光效果
                pygame.draw.line(screen, (255, 255, 255, 60), (px + 2, py + 4), (px + fill_w, py + 4), 1)
            
            # 进度文字
            progress_font = get_ach_font("SimHei", 14)
            progress_text = f"{current:,} / {target:,}"
            percent_text = f"({int(fill_ratio * 100)}%)"
            progress_surf = progress_font.render(progress_text, True, WHITE)
            percent_surf = progress_font.render(percent_text, True, (180, 185, 200))
            screen.blit(progress_surf, (px + bar_w//2 - (progress_surf.get_width() + percent_surf.get_width() + 5)//2, py + 5))
            screen.blit(percent_surf, (px + bar_w//2 - (progress_surf.get_width() + percent_surf.get_width() + 5)//2 + progress_surf.get_width() + 5, py + 5))
        
        # 信息区域（卡片式）
        py += 50
        info_card = pygame.Rect(px, py, detail_rect.width - 50, 95)
        info_bg = pygame.Surface((info_card.width, info_card.height), pygame.SRCALPHA)
        pygame.draw.rect(info_bg, (28, 32, 45, 200), (0, 0, info_card.width, info_card.height), border_radius=10)
        screen.blit(info_bg, info_card.topleft)
        pygame.draw.rect(screen, (55, 60, 78), info_card, 1, border_radius=10)
        
        info_font = get_ach_font("SimHei", 16)
        info_emoji = get_ach_font("Segoe UI Emoji", 16)
        
        # 奖励
        info_y = py + 12
        gift_icon = info_emoji.render("🎁", True, ORANGE if selected_ach.unlocked else (120, 100, 80))
        reward_label = info_font.render("奖励: ", True, (140, 145, 160))
        reward_value = info_font.render(f"+{selected_ach.reward:,}分", True, ORANGE if selected_ach.unlocked else (120, 100, 80))
        screen.blit(gift_icon, (px + 15, info_y))
        screen.blit(reward_label, (px + 42, info_y + 2))
        screen.blit(reward_value, (px + 95, info_y + 2))
        
        # 状态/日期
        info_y += 28
        if selected_ach.unlocked and selected_ach.unlock_date:
            cal_icon = info_emoji.render("📅", True, (100, 180, 180))
            date_label = info_font.render("解锁于: ", True, (140, 145, 160))
            date_value = info_font.render(selected_ach.unlock_date, True, (100, 180, 180))
            screen.blit(cal_icon, (px + 15, info_y))
            screen.blit(date_label, (px + 42, info_y + 2))
            screen.blit(date_value, (px + 115, info_y + 2))
        elif selected_ach.unlocked:
            check_icon = info_emoji.render("✅", True, LIME)
            status_text = info_font.render("已解锁", True, LIME)
            screen.blit(check_icon, (px + 15, info_y))
            screen.blit(status_text, (px + 42, info_y + 2))
        else:
            lock_icon = info_emoji.render("🔒", True, (110, 100, 90))
            status_text = info_font.render("未解锁 - 继续努力!", True, (110, 100, 90))
            screen.blit(lock_icon, (px + 15, info_y))
            screen.blit(status_text, (px + 42, info_y + 2))
        
        # 分类
        info_y += 28
        cat_names = {"combat": "战斗", "boss": "Boss", "survival": "生存", "plane": "机体", "roguelike": "肉鸽", "efficiency": "效率", "milestone": "里程碑", "secret": "隐藏"}
        folder_icon = info_emoji.render("📁", True, (130, 140, 160))
        cat_label = info_font.render("分类: ", True, (140, 145, 160))
        cat_value = info_font.render(cat_names.get(selected_ach.category, selected_ach.category), True, (150, 160, 180))
        screen.blit(folder_icon, (px + 15, info_y))
        screen.blit(cat_label, (px + 42, info_y + 2))
        screen.blit(cat_value, (px + 95, info_y + 2))
        
    else:
        # 未选中提示（美化版）
        hint_y = detail_rect.centery - 50
        
        # 装饰图标
        hint_emoji = get_ach_font("Segoe UI Emoji", 56)
        pointer_icon = hint_emoji.render("👈", True, (70, 75, 95))
        screen.blit(pointer_icon, (detail_rect.centerx - pointer_icon.get_width()//2, hint_y - 30))
        
        hint_font = get_ach_font("SimHei", 20)
        hint_text = hint_font.render("点击左侧徽章查看详情", True, (110, 115, 135))
        screen.blit(hint_text, (detail_rect.centerx - hint_text.get_width()//2, hint_y + 45))
        
        hint_sub_font = get_ach_font("SimHei", 14)
        hint_sub = hint_sub_font.render("完成成就获取丰厚奖励", True, (80, 85, 100))
        screen.blit(hint_sub, (detail_rect.centerx - hint_sub.get_width()//2, hint_y + 75))
    
    # ====== 豪华底部区 ======
    footer_y = HEIGHT - FOOTER_H
    
    # 底部面板背景
    footer_panel = pygame.Rect(MARGIN, footer_y + 5, WIDTH - MARGIN * 2, 55)
    footer_bg = pygame.Surface((footer_panel.width, footer_panel.height), pygame.SRCALPHA)
    pygame.draw.rect(footer_bg, (18, 22, 32, 220), (0, 0, footer_panel.width, footer_panel.height), border_radius=10)
    screen.blit(footer_bg, footer_panel.topleft)
    pygame.draw.rect(screen, (55, 60, 78), footer_panel, 1, border_radius=10)
    
    # 统计数据（图标+文字）
    bottom_font = get_ach_font("SimHei", 15)
    bottom_emoji = get_ach_font("Segoe UI Emoji", 14)
    stats = achievement_mgr.stats
    
    stat_items = [
        ("💀", "击杀", stats.get('total_kills', 0), ORANGE),
        ("👹", "Boss", stats.get('bosses_killed', 0), MAGENTA),
        ("🌊", "最高波次", stats.get('max_wave', 0), CYAN),
        ("🎮", "游戏局数", stats.get('runs_completed', 0), LIME),
    ]
    
    stat_x = footer_panel.x + 25
    for emoji_char, label, value, color in stat_items:
        emoji_surf = bottom_emoji.render(emoji_char, True, color)
        label_surf = bottom_font.render(f"{label}: ", True, (130, 135, 155))
        value_surf = bottom_font.render(f"{value:,}" if isinstance(value, int) and value >= 1000 else str(value), True, color)
        
        screen.blit(emoji_surf, (stat_x, footer_y + 22))
        screen.blit(label_surf, (stat_x + 22, footer_y + 24))
        screen.blit(value_surf, (stat_x + 22 + label_surf.get_width(), footer_y + 24))
        
        stat_x += emoji_surf.get_width() + label_surf.get_width() + value_surf.get_width() + 40
    
    # 返回按钮（豪华版）
    back_btn = pygame.Rect(WIDTH - MARGIN - 130, footer_y + 12, 110, 40)
    h = back_btn.collidepoint(mx, my)
    
    # 按钮背景渐变
    btn_bg = pygame.Surface((back_btn.width, back_btn.height), pygame.SRCALPHA)
    if h:
        for by in range(back_btn.height):
            alpha = int(200 - by * 3)
            pygame.draw.line(btn_bg, (70, 65, 35, alpha), (0, by), (back_btn.width, by))
    else:
        for by in range(back_btn.height):
            alpha = int(180 - by * 2)
            pygame.draw.line(btn_bg, (40, 45, 55, alpha), (0, by), (back_btn.width, by))
    screen.blit(btn_bg, back_btn.topleft)
    
    # 按钮边框
    pygame.draw.rect(screen, GOLD if h else (100, 105, 125), back_btn, 2, border_radius=10)
    if h:
        glow_btn = back_btn.inflate(4, 4)
        pygame.draw.rect(screen, (*GOLD, 50), glow_btn, 1, border_radius=12)
    
    # 按钮文字
    back_emoji = get_ach_font("Segoe UI Emoji", 16)
    back_font = get_ach_font("SimHei", 17)
    arrow_surf = back_emoji.render("◀", True, GOLD if h else WHITE)
    back_text = back_font.render(" 返回", True, GOLD if h else WHITE)
    total_btn_w = arrow_surf.get_width() + back_text.get_width()
    screen.blit(arrow_surf, (back_btn.centerx - total_btn_w//2, back_btn.centery - arrow_surf.get_height()//2))
    screen.blit(back_text, (back_btn.centerx - total_btn_w//2 + arrow_surf.get_width(), back_btn.centery - back_text.get_height()//2))

def draw_leaderboard_ui():
    """绘制排行榜界面 - 赛博朋克风格 豪华版（性能优化版）"""
    global leaderboard_mode, leaderboard_sort_by, leaderboard_scroll_y, leaderboard_stats_tab
    
    t = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    
    # ====== 缓存的静态背景 ======
    screen.blit(_get_lb_background(), (0, 0))
    
    # 动态星空粒子（保留完整特效）
    for i in range(80):
        star_x = (i * 137 + int(t / 50)) % WIDTH
        star_y = (i * 89 + int(t / 80)) % HEIGHT
        star_alpha = int(80 + 60 * math.sin(t / 300 + i))
        star_size = 1 if i % 3 else 2
        star_color = (star_alpha, star_alpha, int(star_alpha * 1.2))
        pygame.draw.circle(screen, star_color, (star_x, star_y), star_size)
    
    # 流光扫描线（降低更新频率 - 每3帧更新一次位置计算）
    scan_y = int((t / 15) % (HEIGHT + 100)) - 50
    scan_color = (200, 180, 50, 35)
    pygame.draw.rect(screen, scan_color[:3], (0, scan_y, WIDTH, 2))
    
    # 边框发光装饰（动态）
    glow_intensity = int(150 + 80 * math.sin(t / 400))
    border_color = (glow_intensity, int(glow_intensity * 0.85), 20)
    # 顶部横条
    pygame.draw.rect(screen, border_color, (0, 0, WIDTH, 3))
    pygame.draw.rect(screen, (border_color[0]//3, border_color[1]//3, 10), (0, 3, WIDTH, 2))
    # 底部横条
    pygame.draw.rect(screen, border_color, (0, HEIGHT - 3, WIDTH, 3))
    pygame.draw.rect(screen, (border_color[0]//3, border_color[1]//3, 10), (0, HEIGHT - 5, WIDTH, 2))
    
    # 角落霓虹装饰
    corner_size = 50
    for corner in [(0, 0, 1, 1), (WIDTH, 0, -1, 1), (0, HEIGHT, 1, -1), (WIDTH, HEIGHT, -1, -1)]:
        cx, cy, dx, dy = corner
        pygame.draw.line(screen, GOLD, (cx, cy + dy * 5), (cx, cy + dy * corner_size), 2)
        pygame.draw.line(screen, GOLD, (cx + dx * 5, cy), (cx + dx * corner_size, cy), 2)
        pygame.draw.circle(screen, (255, 200, 50), (cx + dx * 8, cy + dy * 8), 3)
    
    # ====== 豪华标题区（使用缓存渐变）======
    title_panel = pygame.Rect(WIDTH//2 - 250, 12, 500, 55)
    title_bg = _get_lb_gradient("title", 500, 55, [(60, 50, 20), (40, 35, 15)], (180, 100))
    screen.blit(title_bg, title_panel.topleft)
    pygame.draw.rect(screen, GOLD, title_panel, 2, border_radius=5)
    # 内发光
    inner_rect = title_panel.inflate(-6, -6)
    pygame.draw.rect(screen, (255, 220, 100), inner_rect, 1, border_radius=3)
    
    # 标题文字（使用缓存字体，动态颜色）
    title_glow = int(255 * (0.8 + 0.2 * math.sin(t / 300)))
    title_emoji = _get_lb_font("Segoe UI Emoji", 36)
    title_text = _get_lb_font("SimHei", 42)
    trophy = title_emoji.render("🏆", True, (title_glow, int(title_glow * 0.85), 0))
    title = title_text.render(" 荣耀战绩 ", True, (title_glow, int(title_glow * 0.85), 0))
    trophy2 = title_emoji.render("🏆", True, (title_glow, int(title_glow * 0.85), 0))
    total_w = trophy.get_width() + title.get_width() + trophy2.get_width()
    start_x = WIDTH//2 - total_w//2
    screen.blit(trophy, (start_x, 22))
    screen.blit(title, (start_x + trophy.get_width(), 18))
    screen.blit(trophy2, (start_x + trophy.get_width() + title.get_width(), 22))
    
    # 标题下方装饰线
    line_y = 70
    line_w = 400
    pygame.draw.line(screen, (80, 70, 30), (WIDTH//2 - line_w//2, line_y), (WIDTH//2 + line_w//2, line_y), 1)
    # 中心菱形
    diamond_x = WIDTH // 2
    pygame.draw.polygon(screen, GOLD, [(diamond_x, line_y - 5), (diamond_x + 6, line_y), (diamond_x, line_y + 5), (diamond_x - 6, line_y)])
    
    # ====== 主标签栏（排行榜 / 个人统计）======
    main_tab_y = 82
    main_tabs = [("📋", "排行榜", 0), ("📊", "个人统计", 1)]
    main_tab_width = 160
    main_tab_start = WIDTH//2 - (main_tab_width * 2 + 30) // 2
    
    for i, (emoji, label, idx) in enumerate(main_tabs):
        tab_rect = pygame.Rect(main_tab_start + i * (main_tab_width + 30), main_tab_y, main_tab_width, 40)
        is_selected = (leaderboard_stats_tab == idx)
        is_hover = tab_rect.collidepoint(mx, my)
        
        # 标签背景 - 简化为纯色
        if is_selected:
            pygame.draw.rect(screen, (60, 55, 25), tab_rect, border_radius=8)
            pygame.draw.rect(screen, GOLD, tab_rect, 2, border_radius=8)
            # 底部高亮条
            pygame.draw.rect(screen, GOLD, (tab_rect.x + 10, tab_rect.bottom - 3, tab_rect.width - 20, 3), border_radius=2)
        else:
            pygame.draw.rect(screen, (35, 32, 28) if is_hover else (25, 23, 20), tab_rect, border_radius=8)
            pygame.draw.rect(screen, (100, 90, 70) if is_hover else (60, 55, 45), tab_rect, 1, border_radius=8)
        
        # 分开渲染emoji和文字
        text_col = GOLD if is_selected else (WHITE if is_hover else (160, 150, 130))
        emoji_font = _get_lb_font("Segoe UI Emoji", 18)
        text_font = _get_lb_font("SimHei", 18)
        emoji_surf = emoji_font.render(emoji, True, text_col)
        text_surf = text_font.render(label, True, text_col)
        total_w = emoji_surf.get_width() + 5 + text_surf.get_width()
        start_x = tab_rect.centerx - total_w // 2
        screen.blit(emoji_surf, (start_x, tab_rect.centery - emoji_surf.get_height()//2))
        screen.blit(text_surf, (start_x + emoji_surf.get_width() + 5, tab_rect.centery - text_surf.get_height()//2))
    
    if leaderboard_stats_tab == 0:
        # ====== 模式切换标签 ======
        mode_y = 135
        modes = [("⚔", "普通模式", "normal", YELLOW), ("🏠", "房间模式", "roguelike", MAGENTA), ("👹", "Boss挑战", "boss_challenge", CYAN)]
        mode_tab_width = 140
        mode_start = WIDTH//2 - (mode_tab_width * 3 + 40) // 2
        
        for i, (emoji, label, mode_id, color) in enumerate(modes):
            tab_rect = pygame.Rect(mode_start + i * (mode_tab_width + 20), mode_y, mode_tab_width, 35)
            is_selected = (leaderboard_mode == mode_id)
            is_hover = tab_rect.collidepoint(mx, my)
            
            if is_selected:
                # 选中态：纯色背景
                pygame.draw.rect(screen, (color[0]//4, color[1]//4, color[2]//4), tab_rect, border_radius=6)
                pygame.draw.rect(screen, color, tab_rect, 2, border_radius=6)
            else:
                pygame.draw.rect(screen, (35, 33, 30) if is_hover else (25, 23, 20), tab_rect, border_radius=6)
                pygame.draw.rect(screen, (90, 85, 75) if is_hover else (55, 50, 45), tab_rect, 1, border_radius=6)
            
            # 分开渲染emoji和文字
            text_col = color if is_selected else (WHITE if is_hover else (140, 135, 125))
            emoji_font = _get_lb_font("Segoe UI Emoji", 15)
            text_font = _get_lb_font("SimHei", 14)
            emoji_surf = emoji_font.render(emoji, True, text_col)
            text_surf = text_font.render(label, True, text_col)
            total_w = emoji_surf.get_width() + 3 + text_surf.get_width()
            start_x = tab_rect.centerx - total_w // 2
            screen.blit(emoji_surf, (start_x, tab_rect.centery - emoji_surf.get_height()//2))
            screen.blit(text_surf, (start_x + emoji_surf.get_width() + 3, tab_rect.centery - text_surf.get_height()//2))
        
        # ====== 排序选项 ======
        sort_y = 182
        sort_options = [("🎯", "分数", "score"), ("💀", "击杀", "kills"), ("⏱", "时间", "time"), ("🌊", "波次", "wave")]
        sort_btn_w = 90
        sort_start = WIDTH//2 - (sort_btn_w * 4 + 45) // 2
        
        # 排序标签
        sort_label_font = _get_lb_font("SimHei", 14)
        sort_label = sort_label_font.render("排序方式：", True, (100, 95, 85))
        screen.blit(sort_label, (sort_start - 80, sort_y + 8))
        
        for i, (emoji, label, sort_id) in enumerate(sort_options):
            btn_rect = pygame.Rect(sort_start + i * (sort_btn_w + 15), sort_y, sort_btn_w, 30)
            is_selected = (leaderboard_sort_by == sort_id)
            is_hover = btn_rect.collidepoint(mx, my)
            
            if is_selected:
                pygame.draw.rect(screen, (55, 50, 30), btn_rect, border_radius=5)
                pygame.draw.rect(screen, GOLD, btn_rect, 2, border_radius=5)
            else:
                pygame.draw.rect(screen, (35, 32, 28) if is_hover else (22, 20, 18), btn_rect, border_radius=5)
                pygame.draw.rect(screen, (70, 65, 55) if is_hover else (45, 42, 38), btn_rect, 1, border_radius=5)
            
            # 分开渲染emoji和文字
            text_col = GOLD if is_selected else (WHITE if is_hover else (130, 125, 115))
            emoji_font = _get_lb_font("Segoe UI Emoji", 13)
            text_font = _get_lb_font("SimHei", 13)
            emoji_surf = emoji_font.render(emoji, True, text_col)
            text_surf = text_font.render(label, True, text_col)
            total_w = emoji_surf.get_width() + 3 + text_surf.get_width()
            start_x = btn_rect.centerx - total_w // 2
            screen.blit(emoji_surf, (start_x, btn_rect.centery - emoji_surf.get_height()//2))
            screen.blit(text_surf, (start_x + emoji_surf.get_width() + 3, btn_rect.centery - text_surf.get_height()//2))
        
        # ====== 排行榜主面板 ======
        list_rect = pygame.Rect(WIDTH//2 - 480, 225, 960, HEIGHT - 320)
        
        # 面板背景渐变（使用缓存）
        panel_bg = _get_lb_gradient("panel_bg", list_rect.width, list_rect.height, [(15, 18, 28)], (220, int(220 - list_rect.height * 0.15)))
        screen.blit(panel_bg, list_rect.topleft)
        
        # 面板边框（双层）
        pygame.draw.rect(screen, (80, 75, 55), list_rect, 2, border_radius=10)
        inner = list_rect.inflate(-8, -8)
        pygame.draw.rect(screen, (45, 42, 35), inner, 1, border_radius=8)
        
        # 表头区域（使用缓存）
        header_rect = pygame.Rect(list_rect.x + 5, list_rect.y + 5, list_rect.width - 10, 35)
        header_bg = _get_lb_gradient("header_bg", header_rect.width, 35, [(40, 38, 30)], (200, 200))
        screen.blit(header_bg, header_rect.topleft)
        
        # 表头文字
        header_y = list_rect.y + 15
        headers = [("排名", 70), ("玩家", 180), ("机体", 150), ("分数", 130), ("击杀", 90), ("时间", 90), ("波次", 80), ("日期", 150)]
        header_x = list_rect.x + 25
        header_font = _get_lb_font("SimHei", 15)
        for label, width in headers:
            text_surf = header_font.render(label, True, (140, 135, 120))
            screen.blit(text_surf, (header_x + width//2 - text_surf.get_width()//2, header_y))
            header_x += width
        
        # 表头分隔线
        pygame.draw.line(screen, (60, 55, 45), (list_rect.x + 20, list_rect.y + 45), (list_rect.right - 20, list_rect.y + 45), 1)
        
        # 获取当前模式的数据
        mode_data = leaderboard_data.get(leaderboard_mode, [])
        
        # 排序
        if leaderboard_sort_by == "score":
            mode_data = sorted(mode_data, key=lambda x: x.get("score", 0), reverse=True)
        elif leaderboard_sort_by == "kills":
            mode_data = sorted(mode_data, key=lambda x: x.get("kills", 0), reverse=True)
        elif leaderboard_sort_by == "time":
            mode_data = sorted(mode_data, key=lambda x: x.get("survival_time", 0), reverse=True)
        elif leaderboard_sort_by == "wave":
            mode_data = sorted(mode_data, key=lambda x: x.get("wave", 0) + x.get("rooms", 0), reverse=True)
        
        # 显示记录（支持滚动）
        row_height = 55
        content_y = list_rect.y + 55
        content_height = list_rect.height - 70  # 内容区域高度
        visible_rows = content_height // row_height
        total_rows = len(mode_data)
        total_content_height = total_rows * row_height
        max_scroll = max(0, total_content_height - content_height)
        
        # 限制滚动范围
        leaderboard_scroll_y = max(0, min(leaderboard_scroll_y, max_scroll))
        
        # 创建裁剪区域
        content_rect = pygame.Rect(list_rect.x, content_y, list_rect.width, content_height)
        
        if not mode_data:
            # 空状态
            empty_emoji = _get_lb_font("Segoe UI Emoji", 60)
            empty_text = empty_emoji.render("🎮", True, (60, 55, 50))
            screen.blit(empty_text, (list_rect.centerx - empty_text.get_width()//2, list_rect.centery - 60))
            draw_text(screen, "暂无战绩记录", 28, list_rect.centerx, list_rect.centery + 20, (90, 85, 75))
            draw_text(screen, "完成游戏后将在此展示你的荣耀", 16, list_rect.centerx, list_rect.centery + 55, (65, 60, 55))
        else:
            # 设置裁剪区域
            screen.set_clip(content_rect)
            
            # 计算起始索引优化渲染
            start_idx = max(0, int(leaderboard_scroll_y // row_height) - 1)
            end_idx = min(total_rows, start_idx + visible_rows + 3)
            
            for i in range(start_idx, end_idx):
                entry = mode_data[i]
                row_y = content_y + i * row_height - leaderboard_scroll_y
                
                # 跳过不可见的行
                if row_y + row_height < content_rect.y or row_y > content_rect.bottom:
                    continue
                    
                row_rect = pygame.Rect(list_rect.x + 12, row_y, list_rect.width - 44, row_height - 6)
                
                # 排名特效
                if i == 0:  # 金牌
                    rank_color = GOLD
                    row_bg_colors = [(70, 60, 25), (50, 45, 20)]
                    glow_color = (255, 215, 0, 40)
                elif i == 1:  # 银牌
                    rank_color = (200, 200, 215)
                    row_bg_colors = [(50, 50, 60), (40, 40, 48)]
                    glow_color = (200, 200, 220, 30)
                elif i == 2:  # 铜牌
                    rank_color = (200, 140, 90)
                    row_bg_colors = [(50, 40, 30), (40, 32, 25)]
                    glow_color = (200, 140, 90, 25)
                else:
                    rank_color = (140, 135, 125)
                    row_bg_colors = [(28, 30, 38), (24, 26, 34)] if i % 2 == 0 else [(32, 34, 42), (28, 30, 38)]
                    glow_color = None
                
                # 行背景渐变
                row_bg = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
                for ry in range(row_rect.height):
                    ratio = ry / row_rect.height
                    r = int(row_bg_colors[0][0] * (1 - ratio) + row_bg_colors[1][0] * ratio)
                    g = int(row_bg_colors[0][1] * (1 - ratio) + row_bg_colors[1][1] * ratio)
                    b = int(row_bg_colors[0][2] * (1 - ratio) + row_bg_colors[1][2] * ratio)
                    pygame.draw.line(row_bg, (r, g, b, 230), (0, ry), (row_rect.width, ry))
                screen.blit(row_bg, row_rect.topleft)
                
                # 前三名发光边框
                if i < 3:
                    pygame.draw.rect(screen, rank_color, row_rect, 2, border_radius=8)
                    if glow_color:
                        glow_rect = row_rect.inflate(4, 4)
                        pygame.draw.rect(screen, glow_color[:3], glow_rect, 1, border_radius=10)
                else:
                    pygame.draw.rect(screen, (50, 48, 42), row_rect, 1, border_radius=6)
                
                # 数据显示
                col_x = list_rect.x + 25
                row_center_y = row_y + row_height // 2 - 3
                
                # 排名（带奖牌emoji）
                rank_emoji = _get_lb_font("Segoe UI Emoji", 22)
                if i == 0:
                    rank_surf = rank_emoji.render("🥇", True, GOLD)
                elif i == 1:
                    rank_surf = rank_emoji.render("🥈", True, (200, 200, 215))
                elif i == 2:
                    rank_surf = rank_emoji.render("🥉", True, (200, 140, 90))
                else:
                    rank_font = _get_lb_font("SimHei", 20)
                    rank_surf = rank_font.render(f"#{i+1}", True, rank_color)
                screen.blit(rank_surf, (col_x + 20, row_center_y - rank_surf.get_height()//2 + 3))
                col_x += 70
                
                # 玩家名（高亮）
                name_font = _get_lb_font("SimHei", 18)
                name_surf = name_font.render(entry.get("name", "未知")[:10], True, WHITE)
                screen.blit(name_surf, (col_x + 90 - name_surf.get_width()//2, row_center_y - name_surf.get_height()//2 + 3))
                col_x += 180
                
                # 机体
                plane_id = entry.get("plane", "unknown")
                plane_name = PLANES.get(plane_id, {}).get("name", plane_id)[:7]
                plane_font = _get_lb_font("SimHei", 15)
                plane_surf = plane_font.render(plane_name, True, CYAN)
                screen.blit(plane_surf, (col_x + 75 - plane_surf.get_width()//2, row_center_y - plane_surf.get_height()//2 + 3))
                col_x += 150
                
                # 分数（金色高亮）
                score_font = _get_lb_font("SimHei", 18)
                score_surf = score_font.render(f"{entry.get('score', 0):,}", True, GOLD)
                screen.blit(score_surf, (col_x + 65 - score_surf.get_width()//2, row_center_y - score_surf.get_height()//2 + 3))
                col_x += 130
                
                # 击杀
                kills_font = _get_lb_font("SimHei", 16)
                kills_surf = kills_font.render(str(entry.get("kills", 0)), True, ORANGE)
                screen.blit(kills_surf, (col_x + 45 - kills_surf.get_width()//2, row_center_y - kills_surf.get_height()//2 + 3))
                col_x += 90
                
                # 时间
                survival = entry.get("survival_time", 0)
                time_str = f"{survival//60}:{survival%60:02d}"
                time_font = _get_lb_font("SimHei", 16)
                time_surf = time_font.render(time_str, True, (150, 200, 255))
                screen.blit(time_surf, (col_x + 45 - time_surf.get_width()//2, row_center_y - time_surf.get_height()//2 + 3))
                col_x += 90
                
                # 波次/房间
                wave_val = entry.get("wave", 0) or entry.get("rooms", 0)
                wave_font = _get_lb_font("SimHei", 16)
                wave_surf = wave_font.render(str(wave_val), True, LIME)
                screen.blit(wave_surf, (col_x + 40 - wave_surf.get_width()//2, row_center_y - wave_surf.get_height()//2 + 3))
                col_x += 80
                
                # 日期
                date_str = entry.get("date", "")[:10]
                date_font = _get_lb_font("SimHei", 13)
                date_surf = date_font.render(date_str, True, (110, 108, 100))
                screen.blit(date_surf, (col_x + 75 - date_surf.get_width()//2, row_center_y - date_surf.get_height()//2 + 3))
            
            # 取消裁剪
            screen.set_clip(None)
            
            # ====== 滚动条 ======
            scrollbar_x = list_rect.right - 18
            scrollbar_track_rect = pygame.Rect(scrollbar_x, content_rect.y + 5, 10, content_height - 10)
            
            # 计算滑块大小和位置
            thumb_ratio = content_height / max(total_content_height, 1)
            thumb_height = max(30, int(scrollbar_track_rect.height * thumb_ratio))
            scroll_ratio = leaderboard_scroll_y / max_scroll if max_scroll > 0 else 0
            thumb_y = scrollbar_track_rect.y + int((scrollbar_track_rect.height - thumb_height) * scroll_ratio)
            scrollbar_thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 10, thumb_height)
            
            # 存储滚动条信息供点击处理使用（无论是否显示都需要存储）
            _leaderboard_cache["scrollbar_info"] = {
                "track_rect": scrollbar_track_rect,
                "thumb_rect": scrollbar_thumb_rect,
                "max_scroll": max_scroll,
                "content_height": content_height,
                "total_content_height": total_content_height
            }
            
            # 只有内容超出时才绘制滚动条
            if total_content_height > content_height:
                # 检测悬停
                is_thumb_hover = scrollbar_thumb_rect.collidepoint(mx, my)
                is_track_hover = scrollbar_track_rect.collidepoint(mx, my)
                
                # 绘制轨道
                track_color = (50, 48, 42) if is_track_hover else (35, 33, 30)
                pygame.draw.rect(screen, track_color, scrollbar_track_rect, border_radius=5)
                
                # 绘制滑块
                if leaderboard_dragging_scrollbar:
                    thumb_color = (220, 180, 60)  # 拖动时金色
                elif is_thumb_hover:
                    thumb_color = (180, 150, 50)  # 悬停时亮金色
                else:
                    thumb_color = (120, 100, 40)  # 普通状态暗金色
                pygame.draw.rect(screen, thumb_color, scrollbar_thumb_rect, border_radius=5)
                
                # 滑块高光
                highlight_rect = pygame.Rect(scrollbar_thumb_rect.x + 2, scrollbar_thumb_rect.y + 2, 
                                            scrollbar_thumb_rect.width - 4, 3)
                pygame.draw.rect(screen, (255, 220, 100), highlight_rect, border_radius=2)
    
    else:
        # ====== 个人统计面板（豪华版）======
        stats_rect = pygame.Rect(WIDTH//2 - 420, 135, 840, HEIGHT - 290)
        
        # 面板背景渐变（使用缓存）
        stats_bg = _get_lb_gradient("stats_bg", stats_rect.width, stats_rect.height, [(12, 15, 25)], (220, int(220 - stats_rect.height * 0.12)))
        screen.blit(stats_bg, stats_rect.topleft)
        
        # 边框
        pygame.draw.rect(screen, (70, 65, 50), stats_rect, 2, border_radius=12)
        inner = stats_rect.inflate(-8, -8)
        pygame.draw.rect(screen, (40, 38, 32), inner, 1, border_radius=10)
        
        player_stats = leaderboard_data.get("player_stats", {})
        
        # 统计标题（使用缓存）
        title_rect = pygame.Rect(stats_rect.x + 20, stats_rect.y + 15, stats_rect.width - 40, 45)
        title_bg = _get_lb_gradient("stats_title_bg", title_rect.width, 45, [(30, 40, 55)], (180, 180))
        screen.blit(title_bg, title_rect.topleft)
        
        stats_emoji = _get_lb_font("Segoe UI Emoji", 28)
        stats_text = _get_lb_font("SimHei", 30)
        icon = stats_emoji.render("📊", True, CYAN)
        title = stats_text.render(" 战斗生涯统计", True, CYAN)
        screen.blit(icon, (title_rect.x + 20, title_rect.y + 8))
        screen.blit(title, (title_rect.x + 20 + icon.get_width(), title_rect.y + 7))
        
        pygame.draw.line(screen, (50, 60, 75), (stats_rect.x + 30, stats_rect.y + 70), (stats_rect.right - 30, stats_rect.y + 70), 1)
        
        # 统计项卡片
        stat_items = [
            ("🎮", "总游戏次数", str(player_stats.get("total_games", 0)) + " 局", CYAN, (20, 50, 60)),
            ("💀", "总击杀数", f"{player_stats.get('total_kills', 0):,} 敌人", ORANGE, (60, 40, 20)),
            ("⏱", "总游戏时间", f"{player_stats.get('total_time', 0) // 3600}小时{(player_stats.get('total_time', 0) % 3600) // 60}分钟", (150, 200, 255), (30, 45, 60)),
            ("🏆", "历史最高分", f"{player_stats.get('best_score', 0):,} 分", GOLD, (60, 50, 20)),
            ("✈", "最爱机体", PLANES.get(player_stats.get("favorite_plane", ""), {}).get("name", "暂无数据") if player_stats.get("favorite_plane") else "暂无数据", MAGENTA, (50, 30, 50)),
        ]
        
        item_y = stats_rect.y + 75
        for emoji_char, label, value, color, bg_tint in stat_items:
            # 卡片背景 - 压缩高度
            item_rect = pygame.Rect(stats_rect.x + 50, item_y, stats_rect.width - 100, 50)
            item_bg = pygame.Surface((item_rect.width, 50), pygame.SRCALPHA)
            for iy in range(50):
                alpha = int(200 - iy * 2.5)
                tint = (bg_tint[0] + iy//4, bg_tint[1] + iy//4, bg_tint[2] + iy//4)
                pygame.draw.line(item_bg, (*tint, alpha), (0, iy), (item_rect.width, iy))
            screen.blit(item_bg, item_rect.topleft)
            pygame.draw.rect(screen, color, item_rect, 1, border_radius=6)
            
            # 左侧色条
            pygame.draw.rect(screen, color, (item_rect.x, item_rect.y + 8, 3, item_rect.height - 16), border_radius=2)
            
            # Emoji图标
            item_emoji = _get_lb_font("Segoe UI Emoji", 24)
            icon_surf = item_emoji.render(emoji_char, True, color)
            screen.blit(icon_surf, (item_rect.x + 20, item_rect.centery - icon_surf.get_height()//2))
            
            # 标签
            label_font = _get_lb_font("SimHei", 16)
            label_surf = label_font.render(label, True, (170, 165, 155))
            screen.blit(label_surf, (item_rect.x + 65, item_rect.centery - label_surf.get_height()//2))
            
            # 数值（右对齐）
            value_font = _get_lb_font("SimHei", 20)
            value_surf = value_font.render(value, True, color)
            screen.blit(value_surf, (item_rect.right - 25 - value_surf.get_width(), item_rect.centery - value_surf.get_height()//2))
            
            item_y += 50
        
        # 机体使用统计 - 颁奖典礼领奖台样式
        usage = player_stats.get("plane_usage", {})
        remaining_h = stats_rect.bottom - item_y - 55
        
        if usage:  # 只要有使用数据就显示
            # 分隔线
            pygame.draw.line(screen, (50, 60, 75), (stats_rect.x + 30, item_y), (stats_rect.right - 30, item_y), 1)
            item_y += 5
            
            # 取前3个机体
            sorted_usage = sorted(usage.items(), key=lambda x: x[1], reverse=True)[:3]
            total_count = sum(count for _, count in sorted_usage)
            
            # 动态计算领奖台高度（根据剩余空间）
            max_height = min(75, remaining_h - 40)
            
            # 领奖台配置 [emoji, 颜色, 台高度比例]
            podium_config = [
                ("🥇", GOLD, 1.0),           # 第1名在中间，最高
                ("🥈", (200, 200, 220), 0.73),  # 第2名在左边
                ("🥉", (205, 140, 85), 0.53),   # 第3名在右边
            ]
            
            # 计算领奖台区域
            podium_width = 90
            podium_gap = 8
            total_width = podium_width * 3 + podium_gap * 2
            start_x = stats_rect.x + (stats_rect.width - total_width) // 2
            base_y = item_y + remaining_h - 5  # 领奖台底部对齐
            
            # 按显示顺序绘制 (左2 中1 右3)
            display_order = [1, 0, 2]  # 第二名、第一名、第三名的索引
            
            for display_idx, rank_idx in enumerate(display_order):
                if rank_idx >= len(sorted_usage):
                    continue
                    
                plane_id, count = sorted_usage[rank_idx]
                emoji, color, height_ratio = podium_config[rank_idx]
                height = int(max_height * height_ratio)
                plane_name = PLANES.get(plane_id, {}).get("name", plane_id)
                
                # 计算位置
                px = start_x + display_idx * (podium_width + podium_gap)
                podium_top = base_y - height
                
                # 领奖台
                podium_rect = pygame.Rect(px, podium_top, podium_width, height)
                
                # 渐变背景
                podium_surf = pygame.Surface((podium_width, height), pygame.SRCALPHA)
                for py in range(height):
                    ratio = py / max(height, 1)
                    r = int(color[0] * 0.3 * (1 - ratio * 0.5))
                    g = int(color[1] * 0.3 * (1 - ratio * 0.5))
                    b = int(color[2] * 0.3 * (1 - ratio * 0.5))
                    alpha = 200 - int(ratio * 50)
                    pygame.draw.line(podium_surf, (r, g, b, alpha), (0, py), (podium_width, py))
                screen.blit(podium_surf, podium_rect.topleft)
                
                # 领奖台边框
                pygame.draw.rect(screen, color, podium_rect, 2, border_radius=4)
                
                # 顶部高光
                pygame.draw.line(screen, color, (px + 5, podium_top + 2), (px + podium_width - 5, podium_top + 2), 2)
                
                # 排名数字（大号）
                rank_num = str(rank_idx + 1)
                num_font = _get_lb_font("Impact", 24)
                num_surf = num_font.render(rank_num, True, color)
                num_x = px + (podium_width - num_surf.get_width()) // 2
                num_y = podium_top + 3
                screen.blit(num_surf, (num_x, num_y))
                
                # 机体名（在排名数字下方）
                name_font = _get_lb_font("SimHei", 13)
                display_name = plane_name if len(plane_name) <= 6 else plane_name[:5] + ".."
                name_surf = name_font.render(display_name, True, WHITE)
                name_x = px + (podium_width - name_surf.get_width()) // 2
                name_y = podium_top + 28
                screen.blit(name_surf, (name_x, name_y))  # 直接显示，不加条件
                
                # 使用次数（在机体名下方）
                if total_count > 0:
                    percent = int(count / total_count * 100)
                    count_text = f"{count}次({percent}%)"
                    count_font = _get_lb_font("SimHei", 10)
                    count_surf = count_font.render(count_text, True, (180, 175, 165))
                    count_x = px + (podium_width - count_surf.get_width()) // 2
                    count_y = podium_top + 46
                    if height > 55:  # 只有高度足够才显示次数
                        screen.blit(count_surf, (count_x, count_y))
                
                # 奖牌图标（在领奖台上方）
                medal_font = _get_lb_font("Segoe UI Emoji", 20)
                medal_surf = medal_font.render(emoji, True, color)
                medal_x = px + (podium_width - medal_surf.get_width()) // 2
                medal_y = podium_top - 28
                screen.blit(medal_surf, (medal_x, medal_y))
    
    # ====== 返回按钮（豪华版）======
    back_btn = pygame.Rect(WIDTH//2 - 80, HEIGHT - 75, 160, 50)
    back_hover = back_btn.collidepoint(mx, my)
    
    # 按钮背景渐变
    btn_bg = pygame.Surface((160, 50), pygame.SRCALPHA)
    for by in range(50):
        alpha = int(220 - by * 2)
        color = (60, 55, 35) if back_hover else (35, 32, 25)
        pygame.draw.line(btn_bg, (*color, alpha), (0, by), (160, by))
    screen.blit(btn_bg, back_btn.topleft)
    
    # 按钮边框
    pygame.draw.rect(screen, GOLD if back_hover else (100, 90, 60), back_btn, 2, border_radius=10)
    if back_hover:
        glow_btn = back_btn.inflate(6, 6)
        pygame.draw.rect(screen, (255, 200, 50, 50), glow_btn, 2, border_radius=12)
    
    # 返回按钮文字
    back_emoji = _get_lb_font("Segoe UI Emoji", 18)
    back_text = _get_lb_font("SimHei", 20)
    icon_surf = back_emoji.render("◀", True, GOLD if back_hover else (180, 170, 140))
    text_surf = back_text.render(" 返回", True, GOLD if back_hover else (180, 170, 140))
    total_w = icon_surf.get_width() + text_surf.get_width()
    screen.blit(icon_surf, (back_btn.centerx - total_w//2, back_btn.centery - icon_surf.get_height()//2))
    screen.blit(text_surf, (back_btn.centerx - total_w//2 + icon_surf.get_width(), back_btn.centery - text_surf.get_height()//2))

def handle_plane_customization_click(mx, my):
    """处理机体涂装点击事件"""
    global customization_selected_plane, customization_msg, customization_msg_timer, game_state
    
    print(f"[DEBUG] handle_plane_customization_click called: mx={mx}, my={my}, tab={customization_tab}, plane={customization_selected_plane}")
    
    # 返回按钮已移到主界面的draw_customization_ui中处理
    
    # 选择飞机 - 必须与绘制代码一致！
    plane_list_area = pygame.Rect(25, 115, 290, HEIGHT - 195)
    list_content_rect = pygame.Rect(plane_list_area.x, plane_list_area.y + 48, plane_list_area.width, plane_list_area.height - 48)
    plane_start_y = list_content_rect.y + 5 - customization_plane_scroll_y
    
    if list_content_rect.collidepoint(mx, my):
        for i, plane_id in enumerate(plane_keys):
            rect = pygame.Rect(plane_list_area.x + 8, plane_start_y + i * 52, plane_list_area.width - 16, 48)
            if rect.collidepoint(mx, my):
                sound_mgr.play("select")
                customization_selected_plane = plane_id
                return
    
    # 涂装按钮点击 - 必须与绘制代码一致！
    if customization_selected_plane:
        categories = [None, "common", "rare", "epic", "legendary", "exclusive", "bullet"]
        filtered_themes = []
        
        if customization_tab == 6:  # 子弹标签
            for tid, theme in BULLET_THEMES.items():
                exclusive_plane = theme.get("exclusive_plane")
                if exclusive_plane and exclusive_plane != customization_selected_plane:
                    continue
                filtered_themes.append((tid, theme, True))
        else:
            for tid, theme in PAINT_THEMES.items():
                exclusive_plane = theme.get("exclusive_plane")
                if exclusive_plane and exclusive_plane != customization_selected_plane:
                    continue
                if customization_tab == 0:
                    filtered_themes.append((tid, theme, False))
                else:
                    target_cat = categories[customization_tab]
                    if theme.get("category") == target_cat:
                        filtered_themes.append((tid, theme, False))
        
        # 涂装列表区域 - 必须与绘制代码一致！
        theme_list_area = pygame.Rect(330, 115, 620, HEIGHT - 195)
        theme_y_start = theme_list_area.y + 85
        list_view_rect = pygame.Rect(theme_list_area.x, theme_y_start, theme_list_area.width, theme_list_area.height - 85)
        
        for i, (theme_id, theme, is_bullet) in enumerate(filtered_themes):
            # 卡片尺寸 - 必须与绘制代码一致！
            card_rect = pygame.Rect(theme_list_area.x + 10, theme_y_start + i * 95 - customization_scroll_y, theme_list_area.width - 20, 88)
            
            if card_rect.bottom < list_view_rect.top or card_rect.top > list_view_rect.bottom:
                continue
            
            # 根据涂装类型检查解锁状态
            if is_bullet:
                is_unlocked = customization_manager.unlocked_bullet_themes.get(theme_id, False)
            else:
                is_unlocked = customization_manager.unlocked_themes.get(theme_id, False)
            
            # 按钮尺寸 - 必须与绘制代码一致！
            btn_w = 95
            btn_h = 36
            btn_rect = pygame.Rect(card_rect.right - btn_w - 12, card_rect.y + 26, btn_w, btn_h)
            
            if btn_rect.collidepoint(mx, my):
                print(f"[DEBUG] 点击涂装按钮: theme_id={theme_id}, plane={customization_selected_plane}")
                print(f"[DEBUG] is_bullet={is_bullet}, is_unlocked={is_unlocked}")
                exclusive_plane = theme.get("exclusive_plane")
                print(f"[DEBUG] exclusive_plane={exclusive_plane}")
                if exclusive_plane and exclusive_plane != customization_selected_plane:
                    customization_msg = f"该涂装仅限 {PLANES[exclusive_plane]['name']} 使用"
                    customization_msg_timer = 120
                    sound_mgr.play("warning")
                    continue

                if is_unlocked:
                    print(f"[DEBUG] 调用 equip_theme: plane={customization_selected_plane}, theme={theme_id}, is_bullet={is_bullet}")
                    success, msg = customization_manager.equip_theme(customization_selected_plane, theme_id, bullet=is_bullet)
                    print(f"[DEBUG] equip_theme 返回: success={success}, msg={msg}")
                    customization_msg = msg
                    customization_msg_timer = 120
                    sound_mgr.play("powerup" if success else "warning")
                    
                    if player and player.plane_id == customization_selected_plane:
                        try:
                            new_visual = customization_manager.get_theme_visual(
                                customization_selected_plane, 
                                PLANES[customization_selected_plane].get('visual', None)
                            )
                            player.visual = new_visual
                        except Exception as e:
                            log_error(f"Failed to update player visual: {e}")
                else:
                    cost = theme.get("cost", 0)
                    if arsenal_save_data["currencies"]["cores"] >= cost:
                        arsenal_save_data["currencies"]["cores"] -= cost
                        # 保存arsenal数据
                        with open("arsenal.json", "w", encoding="utf-8") as f:
                            json.dump(arsenal_save_data, f, ensure_ascii=False, indent=2)
                        customization_manager.unlock_theme(theme_id)
                        customization_msg = f"已解锁 {theme['name']}！"
                        customization_msg_timer = 120
                        sound_mgr.play("powerup")
                    else:
                        customization_msg = f"核心不足！需要 {cost} 核心"
                        customization_msg_timer = 120
                        sound_mgr.play("warning")
                break


def handle_wingman_customization_click(mx, my):
    """处理僚机涂装界面的点击事件"""
    global customization_selected_wingman, customization_msg, customization_msg_timer, wingman_theme_filter, customization_scroll_y
    
    # 槽位选择 - 必须与绘制代码一致！
    wingman_list_area = pygame.Rect(25, 115, 290, HEIGHT - 195)
    list_content_rect = pygame.Rect(wingman_list_area.x, wingman_list_area.y + 48, wingman_list_area.width, wingman_list_area.height - 48)
    wingman_start_y = list_content_rect.y + 5
    
    for i in range(4):
        rect = pygame.Rect(wingman_list_area.x + 8, wingman_start_y + i * 70, wingman_list_area.width - 16, 65)
        if rect.collidepoint(mx, my):
            customization_selected_wingman = i
            return
    
    # 机体筛选按钮点击 - 必须与绘制代码一致！
    theme_list_area = pygame.Rect(330, 115, 620, HEIGHT - 195)
    filter_y = theme_list_area.y + 48
    filter_btn_w = 52
    filter_btn_h = 24
    filter_start_x = theme_list_area.x + 10
    
    # "全部"按钮
    all_btn = pygame.Rect(filter_start_x, filter_y, filter_btn_w, filter_btn_h)
    if all_btn.collidepoint(mx, my):
        wingman_theme_filter = None
        customization_scroll_y = 0
        return
    
    # 第一行机体筛选按钮
    plane_keys_list = list(PLANES.keys())
    for pi, plane_id in enumerate(plane_keys_list[:10]):
        btn_x = filter_start_x + (pi + 1) * (filter_btn_w + 4)
        if btn_x + filter_btn_w > theme_list_area.right - 10:
            break
        plane_btn = pygame.Rect(btn_x, filter_y, filter_btn_w, filter_btn_h)
        if plane_btn.collidepoint(mx, my):
            wingman_theme_filter = plane_id
            customization_scroll_y = 0
            return
    
    # 第二行机体筛选按钮
    filter_y2 = filter_y + filter_btn_h + 4
    for pi, plane_id in enumerate(plane_keys_list[10:]):
        btn_x = filter_start_x + pi * (filter_btn_w + 4)
        if btn_x + filter_btn_w > theme_list_area.right - 10:
            break
        plane_btn = pygame.Rect(btn_x, filter_y2, filter_btn_w, filter_btn_h)
        if plane_btn.collidepoint(mx, my):
            wingman_theme_filter = plane_id
            customization_scroll_y = 0
            return
    
    # 涂装卡片点击 - 必须与绘制代码一致！
    theme_y_start = theme_list_area.y + 105
    
    # 筛选涂装（按机体筛选）
    filtered_themes = []
    for tid, theme in PAINT_THEMES.items():
        exclusive_plane = theme.get("exclusive_plane")
        if not exclusive_plane:
            continue
        if wingman_theme_filter is not None and exclusive_plane != wingman_theme_filter:
            continue
        filtered_themes.append((tid, theme))
    
    for i, (theme_id, theme) in enumerate(filtered_themes):
        # 卡片尺寸 - 必须与绘制代码一致！
        card_rect = pygame.Rect(theme_list_area.x + 10, theme_y_start + i * 95 - customization_scroll_y, theme_list_area.width - 20, 88)
        
        if not card_rect.collidepoint(mx, my):
            continue
        
        is_unlocked = customization_manager.unlocked_themes.get(theme_id, False)
        current_equipped = customization_manager.equipped_wingman_themes.get(f"slot_{customization_selected_wingman}", "default")
        is_equipped = (current_equipped == theme_id)
        
        # 按钮区域 - 必须与绘制代码一致！
        btn_w = 95
        btn_h = 36
        btn_rect = pygame.Rect(card_rect.right - btn_w - 12, card_rect.y + 26, btn_w, btn_h)
        
        if btn_rect.collidepoint(mx, my):
            if is_unlocked and not is_equipped:
                # 装备涂装
                customization_manager.equipped_wingman_themes[f"slot_{customization_selected_wingman}"] = theme_id
                customization_manager.save_data()
                customization_msg = f"已为僚机槽位 {customization_selected_wingman + 1} 装备 {theme['name']}！"
                customization_msg_timer = 120
                sound_mgr.play("powerup")
            elif not is_unlocked:
                # 解锁涂装
                cost = theme.get("cost", 0)
                if arsenal_save_data["currencies"]["cores"] >= cost:
                    arsenal_save_data["currencies"]["cores"] -= cost
                    with open("arsenal.json", "w", encoding="utf-8") as f:
                        json.dump(arsenal_save_data, f, ensure_ascii=False, indent=2)
                    customization_manager.unlock_theme(theme_id)
                    customization_msg = f"已解锁 {theme['name']}！"
                    customization_msg_timer = 120
                    sound_mgr.play("powerup")
                else:
                    customization_msg = f"核心不足！需要 {cost} 核心"
                    customization_msg_timer = 120
                    sound_mgr.play("warning")
            break

def draw_customization_ui():
    """绘制涂装自定义界面 - 豪华赛博朋克风格"""
    global customization_mode, game_state
    
    t = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    
    # ====== 动态深空背景 ======
    screen.fill((5, 8, 15))
    
    # 动态星空粒子
    for i in range(40):
        px = (i * 79 + int(t / 60)) % WIDTH
        py = (i * 53 + int(t / 80)) % HEIGHT
        p_alpha = int(40 + 35 * math.sin(t / 400 + i * 0.5))
        size = 1 if i % 3 else 2
        p_color = (p_alpha, int(p_alpha * 1.2), int(p_alpha * 1.8))
        pygame.draw.circle(screen, p_color, (px, py), size)
    
    # 网格背景
    grid_alpha = 12
    grid_color = (grid_alpha, int(grid_alpha * 1.5), grid_alpha * 2)
    grid_size = 50
    offset = int(t / 150) % grid_size
    for x in range(-offset, WIDTH + grid_size, grid_size):
        pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT))
    for y in range(-offset, HEIGHT + grid_size, grid_size):
        pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y))
    
    # 边框发光
    glow_intensity = int(80 + 40 * math.sin(t / 500))
    border_color = (glow_intensity // 3, glow_intensity, int(glow_intensity * 1.2))
    pygame.draw.rect(screen, border_color, (0, 0, WIDTH, 2))
    pygame.draw.rect(screen, border_color, (0, HEIGHT - 2, WIDTH, 2))
    
    # 角落霓虹装饰
    corner_size = 50
    for corner in [(0, 0, 1, 1), (WIDTH, 0, -1, 1), (0, HEIGHT, 1, -1), (WIDTH, HEIGHT, -1, -1)]:
        cx, cy, dx, dy = corner
        pygame.draw.line(screen, CYAN, (cx, cy + dy * 3), (cx, cy + dy * corner_size), 2)
        pygame.draw.line(screen, CYAN, (cx + dx * 3, cy), (cx + dx * corner_size, cy), 2)
    
    # ====== 左上角返回按钮（豪华版）======
    back_btn = pygame.Rect(25, 20, 110, 42)
    hb = back_btn.collidepoint(mx, my)
    
    back_bg = pygame.Surface((110, 42), pygame.SRCALPHA)
    for by in range(42):
        alpha = 180 - by * 3
        color = (100, 40, 40) if hb else (50, 25, 35)
        pygame.draw.line(back_bg, (*color, alpha), (0, by), (110, by))
    screen.blit(back_bg, back_btn.topleft)
    pygame.draw.rect(screen, RED if hb else (150, 60, 80), back_btn, 2, border_radius=8)
    if hb:
        pygame.draw.rect(screen, (200, 80, 80, 60), back_btn.inflate(4, 4), 2, border_radius=10)
    
    back_font = pygame.font.SysFont("SimHei", 18)
    back_text = back_font.render("◀ 返回", True, WHITE)
    screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2, back_btn.centery - back_text.get_height()//2))
    
    # 处理返回按钮点击
    if hb and pygame.mouse.get_pressed()[0]:
        game_state = "menu"
        pygame.mouse.set_visible(True)
        return
    
    # ====== 中央标题区 ======
    title_panel = pygame.Rect(WIDTH//2 - 200, 15, 400, 52)
    title_bg = pygame.Surface((400, 52), pygame.SRCALPHA)
    for ty in range(52):
        alpha = int(180 - ty * 2.5)
        pygame.draw.line(title_bg, (15, 35, 55, alpha), (0, ty), (400, ty))
    screen.blit(title_bg, title_panel.topleft)
    pygame.draw.rect(screen, MAGENTA, title_panel, 2, border_radius=8)
    
    title_glow = int(255 * (0.85 + 0.15 * math.sin(t / 350)))
    title_color = (title_glow, int(title_glow * 0.7), title_glow)
    title_font = pygame.font.SysFont("SimHei", 32)
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 26)
    icon_l = emoji_font.render("🎨", True, MAGENTA)
    title_surf = title_font.render(" 涂装工坊 ", True, title_color)
    icon_r = emoji_font.render("✨", True, CYAN)
    total_w = icon_l.get_width() + title_surf.get_width() + icon_r.get_width()
    start_x = WIDTH//2 - total_w//2
    screen.blit(icon_l, (start_x, 24))
    screen.blit(title_surf, (start_x + icon_l.get_width(), 22))
    screen.blit(icon_r, (start_x + icon_l.get_width() + title_surf.get_width(), 24))
    
    # ====== 模式切换按钮（豪华版）======
    mode_btn_y = 25
    btn_w = 130
    btn_h = 40
    plane_btn = pygame.Rect(WIDTH // 2 - btn_w - 85, mode_btn_y + 50, btn_w, btn_h)
    wingman_btn = pygame.Rect(WIDTH // 2 + 85, mode_btn_y + 50, btn_w, btn_h)
    
    plane_active = (customization_mode == "plane")
    wingman_active = (customization_mode == "wingman")
    plane_hover = plane_btn.collidepoint(mx, my)
    wingman_hover = wingman_btn.collidepoint(mx, my)
    
    # 机体涂装按钮
    plane_bg = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
    for by in range(btn_h):
        alpha = 180 - by * 3
        if plane_active:
            color = (0, 100, 120)
        elif plane_hover:
            color = (40, 70, 90)
        else:
            color = (25, 40, 55)
        pygame.draw.line(plane_bg, (*color, alpha), (0, by), (btn_w, by))
    screen.blit(plane_bg, plane_btn.topleft)
    pygame.draw.rect(screen, CYAN if plane_active else ((80, 140, 180) if plane_hover else (50, 70, 90)), plane_btn, 2, border_radius=8)
    if plane_active:
        pygame.draw.rect(screen, (0, 200, 220, 40), plane_btn.inflate(4, 4), 2, border_radius=10)
    
    plane_font = pygame.font.SysFont("SimHei", 17)
    plane_icon = emoji_font.render("✈", True, CYAN if plane_active else WHITE)
    plane_text = plane_font.render(" 机体涂装", True, CYAN if plane_active else WHITE)
    screen.blit(plane_icon, (plane_btn.x + 12, plane_btn.centery - 10))
    screen.blit(plane_text, (plane_btn.x + 38, plane_btn.centery - 10))
    
    # 僚机涂装按钮
    wingman_bg = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
    for by in range(btn_h):
        alpha = 180 - by * 3
        if wingman_active:
            color = (100, 60, 100)
        elif wingman_hover:
            color = (70, 45, 70)
        else:
            color = (40, 30, 50)
        pygame.draw.line(wingman_bg, (*color, alpha), (0, by), (btn_w, by))
    screen.blit(wingman_bg, wingman_btn.topleft)
    pygame.draw.rect(screen, MAGENTA if wingman_active else ((150, 80, 150) if wingman_hover else (80, 50, 80)), wingman_btn, 2, border_radius=8)
    if wingman_active:
        pygame.draw.rect(screen, (200, 100, 200, 40), wingman_btn.inflate(4, 4), 2, border_radius=10)
    
    wingman_icon = emoji_font.render("👥", True, MAGENTA if wingman_active else WHITE)
    wingman_text = plane_font.render(" 僚机涂装", True, MAGENTA if wingman_active else WHITE)
    screen.blit(wingman_icon, (wingman_btn.x + 12, wingman_btn.centery - 10))
    screen.blit(wingman_text, (wingman_btn.x + 42, wingman_btn.centery - 10))
    
    # 处理按钮点击
    if plane_btn.collidepoint(mx, my) and pygame.mouse.get_pressed()[0]:
        if customization_mode != "plane":
            customization_mode = "plane"
    elif wingman_btn.collidepoint(mx, my) and pygame.mouse.get_pressed()[0]:
        if customization_mode != "wingman":
            customization_mode = "wingman"
    
    # 根据模式绘制不同的UI
    if customization_mode == "plane":
        draw_plane_customization_ui()
    else:
        draw_wingman_customization_ui()


def draw_plane_customization_ui():
    """绘制机体涂装界面 - 豪华赛博朋克风格"""
    global customization_selected_plane, customization_msg_timer, customization_tab, customization_scroll_y, customization_plane_scroll_y
    
    t = pygame.time.get_ticks()
    mx, my = pygame.mouse.get_pos()
    
    # ====== 预加载所有字体（性能优化）======
    font_18 = get_cached_font("SimHei", 18)
    font_17 = get_cached_font("SimHei", 17)
    font_16 = get_cached_font("SimHei", 16)
    font_15 = get_cached_font("SimHei", 15)
    font_14 = get_cached_font("SimHei", 14)
    font_13 = get_cached_font("SimHei", 13)
    font_12 = get_cached_font("SimHei", 12)
    font_11 = get_cached_font("SimHei", 11)
    font_10 = get_cached_font("SimHei", 10)
    emoji_16 = get_cached_font("Segoe UI Emoji", 16)
    emoji_12 = get_cached_font("Segoe UI Emoji", 12)
    
    # ====== 右上角资源显示（豪华版）======
    res_panel = pygame.Rect(WIDTH - 280, 20, 250, 70)
    res_bg = pygame.Surface((250, 70), pygame.SRCALPHA)
    for ry in range(70):
        alpha = int(160 - ry * 1.5)
        pygame.draw.line(res_bg, (20, 35, 50, alpha), (0, ry), (250, ry))
    screen.blit(res_bg, res_panel.topleft)
    pygame.draw.rect(screen, (60, 100, 140), res_panel, 1, border_radius=8)
    
    # 核心数量
    core_icon = emoji_16.render("💎", True, GOLD)
    core_text = font_18.render(f"核心: {arsenal_save_data['currencies']['cores']}", True, GOLD)
    screen.blit(core_icon, (res_panel.x + 15, res_panel.y + 12))
    screen.blit(core_text, (res_panel.x + 42, res_panel.y + 12))
    
    # 解锁进度
    unlocked_count = customization_manager.get_unlocked_count()
    total_count = customization_manager.get_total_count()
    progress_pct = unlocked_count / total_count if total_count > 0 else 0
    
    progress_icon = emoji_16.render("📊", True, CYAN)
    progress_text = font_18.render(f"解锁: {unlocked_count}/{total_count}", True, CYAN)
    screen.blit(progress_icon, (res_panel.x + 15, res_panel.y + 40))
    screen.blit(progress_text, (res_panel.x + 42, res_panel.y + 40))
    
    # 进度条
    bar_x = res_panel.x + 140
    bar_w = 95
    bar_h = 8
    pygame.draw.rect(screen, (30, 40, 55), (bar_x, res_panel.y + 45, bar_w, bar_h), border_radius=4)
    fill_w = int(bar_w * progress_pct)
    if fill_w > 0:
        pygame.draw.rect(screen, CYAN, (bar_x, res_panel.y + 45, fill_w, bar_h), border_radius=4)
    
    # ====== 左侧：飞机列表面板（豪华版）======
    plane_list_area = pygame.Rect(25, 115, 290, HEIGHT - 195)
    
    # 面板背景渐变
    plane_bg = pygame.Surface((plane_list_area.width, plane_list_area.height), pygame.SRCALPHA)
    for py in range(plane_list_area.height):
        alpha = int(200 - py * 0.1)
        pygame.draw.line(plane_bg, (12, 18, 30, alpha), (0, py), (plane_list_area.width, py))
    screen.blit(plane_bg, plane_list_area.topleft)
    pygame.draw.rect(screen, (50, 80, 120), plane_list_area, 2, border_radius=10)
    
    # 面板标题
    title_rect = pygame.Rect(plane_list_area.x + 10, plane_list_area.y + 8, plane_list_area.width - 20, 32)
    pygame.draw.rect(screen, (20, 45, 70, 200), title_rect, border_radius=6)
    pygame.draw.rect(screen, CYAN, title_rect, 1, border_radius=6)
    
    list_icon = emoji_16.render("✈", True, CYAN)
    list_title = font_18.render(" 选择机体", True, CYAN)
    screen.blit(list_icon, (title_rect.x + 15, title_rect.y + 6))
    screen.blit(list_title, (title_rect.x + 38, title_rect.y + 6))
    
    # 列表内容区域
    list_content_rect = pygame.Rect(plane_list_area.x, plane_list_area.y + 48, plane_list_area.width, plane_list_area.height - 48)
    screen.set_clip(list_content_rect)
    
    plane_start_y = list_content_rect.y + 5 - customization_plane_scroll_y
    for i, plane_id in enumerate(plane_keys):
        plane_data = PLANES[plane_id]
        rect = pygame.Rect(plane_list_area.x + 8, plane_start_y + i * 52, plane_list_area.width - 16, 48)
        
        # 可见性剔除
        if rect.bottom < list_content_rect.top or rect.top > list_content_rect.bottom:
            continue
            
        equipped_theme = customization_manager.get_equipped_theme(plane_id)
        is_selected = (customization_selected_plane == plane_id)
        is_hover = rect.collidepoint(mx, my)
        
        # 卡片背景渐变
        card_bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for cy in range(rect.height):
            alpha = 180 - cy * 2
            if is_selected:
                color = (plane_data["color"][0]//3, plane_data["color"][1]//3, plane_data["color"][2]//3)
            elif is_hover:
                color = (40, 55, 75)
            else:
                color = (25, 32, 45)
            pygame.draw.line(card_bg, (*color, alpha), (0, cy), (rect.width, cy))
        screen.blit(card_bg, rect.topleft)
        
        # 边框
        if is_selected:
            pygame.draw.rect(screen, CYAN, rect, 2, border_radius=8)
            pygame.draw.rect(screen, plane_data["color"], rect.inflate(-6, -6), 1, border_radius=6)
        elif is_hover:
            pygame.draw.rect(screen, (80, 120, 160), rect, 1, border_radius=8)
        else:
            pygame.draw.rect(screen, (50, 60, 80), rect, 1, border_radius=8)
        
        # 飞机图标
        plane_visual = customization_manager.get_theme_visual(plane_id, PLANES[plane_id].get('visual', None))
        icon = get_plane_surf(plane_id, plane_visual, static=True)
        icon = pygame.transform.scale(icon, (36, 36))
        safe_blit(screen, icon, (rect.x + 8, rect.y + 6))
        
        # 机体名称
        name_surf = font_15.render(plane_data["name"], True, WHITE if is_selected else (200, 200, 210))
        screen.blit(name_surf, (rect.x + 52, rect.y + 8))
        
        # 装备的涂装名称
        if equipped_theme != "default":
            if equipped_theme in PAINT_THEMES:
                theme_name = PAINT_THEMES[equipped_theme]["name"]
                cat = PAINT_THEMES[equipped_theme].get("category", "default")
                quality_colors = {"default": (150, 150, 150), "common": (200, 200, 200), "rare": (100, 150, 255), "epic": (200, 100, 255), "legendary": (255, 215, 0), "exclusive": (255, 80, 150)}
                q_color = quality_colors.get(cat, GRAY)
                theme_surf = font_12.render(f"[{theme_name}]", True, q_color)
                screen.blit(theme_surf, (rect.x + 52, rect.y + 28))
            else:
                customization_manager.equip_theme(plane_id, "default")
        else:
            theme_surf = font_12.render("[默认涂装]", True, (100, 105, 115))
            screen.blit(theme_surf, (rect.x + 52, rect.y + 28))
            
    screen.set_clip(None)

    # ====== 右侧：涂装列表面板（豪华版）======
    theme_list_area = pygame.Rect(330, 115, 620, HEIGHT - 195)
    
    # 面板背景渐变
    theme_bg = pygame.Surface((theme_list_area.width, theme_list_area.height), pygame.SRCALPHA)
    for ty in range(theme_list_area.height):
        alpha = int(200 - ty * 0.08)
        pygame.draw.line(theme_bg, (12, 18, 30, alpha), (0, ty), (theme_list_area.width, ty))
    screen.blit(theme_bg, theme_list_area.topleft)
    pygame.draw.rect(screen, (60, 90, 130), theme_list_area, 2, border_radius=10)
    
    if customization_selected_plane:
        plane_data = PLANES[customization_selected_plane]
        
        # 面板标题
        panel_title_rect = pygame.Rect(theme_list_area.x + 10, theme_list_area.y + 8, theme_list_area.width - 20, 32)
        pygame.draw.rect(screen, (25, 50, 75, 200), panel_title_rect, border_radius=6)
        pygame.draw.rect(screen, plane_data["color"], panel_title_rect, 1, border_radius=6)
        
        panel_icon = emoji_16.render("🎨", True, plane_data["color"])
        panel_title = font_17.render(f" {plane_data['name']} - 涂装方案", True, WHITE)
        screen.blit(panel_icon, (panel_title_rect.x + 12, panel_title_rect.y + 6))
        screen.blit(panel_title, (panel_title_rect.x + 38, panel_title_rect.y + 7))
        
        # ====== 分类标签页（豪华版）======
        tabs = ["全部", "普通", "稀有", "史诗", "传说", "专属", "子弹"]
        categories = [None, "common", "rare", "epic", "legendary", "exclusive", "bullet"]
        tab_colors = [CYAN, (200, 200, 200), (100, 150, 255), (200, 100, 255), (255, 215, 0), (255, 80, 150), ORANGE]
        tab_w = 78
        tab_h = 28
        start_x = theme_list_area.x + 12
        tab_y = theme_list_area.y + 48
        
        for i, tab_name in enumerate(tabs):
            tab_rect = pygame.Rect(start_x + i * (tab_w + 6), tab_y, tab_w, tab_h)
            is_active = (customization_tab == i)
            is_hover = tab_rect.collidepoint(mx, my)
            
            # 处理点击
            if is_hover and pygame.mouse.get_pressed()[0]:
                if customization_tab != i:
                    customization_tab = i
                    customization_scroll_y = 0
            
            # 标签背景
            tab_bg = pygame.Surface((tab_w, tab_h), pygame.SRCALPHA)
            for ty in range(tab_h):
                alpha = 160 - ty * 4
                if is_active:
                    color = (tab_colors[i][0]//4, tab_colors[i][1]//4, tab_colors[i][2]//4)
                elif is_hover:
                    color = (45, 55, 70)
                else:
                    color = (30, 38, 50)
                pygame.draw.line(tab_bg, (*color, alpha), (0, ty), (tab_w, ty))
            screen.blit(tab_bg, tab_rect.topleft)
            
            # 边框
            border_color = tab_colors[i] if is_active else ((80, 100, 130) if is_hover else (50, 60, 75))
            pygame.draw.rect(screen, border_color, tab_rect, 2 if is_active else 1, border_radius=6)
            
            # 文字
            tab_text = font_13.render(tab_name, True, tab_colors[i] if is_active else (WHITE if is_hover else (160, 165, 175)))
            screen.blit(tab_text, (tab_rect.centerx - tab_text.get_width()//2, tab_rect.centery - tab_text.get_height()//2))

        # ====== 筛选涂装 ======
        filtered_themes = []
        
        if customization_tab == 6:  # 子弹标签
            for tid, theme in BULLET_THEMES.items():
                exclusive_plane = theme.get("exclusive_plane")
                if exclusive_plane and exclusive_plane != customization_selected_plane:
                    continue
                filtered_themes.append((tid, theme, True))
        else:
            for tid, theme in PAINT_THEMES.items():
                exclusive_plane = theme.get("exclusive_plane")
                if exclusive_plane and exclusive_plane != customization_selected_plane:
                    continue

                if customization_tab == 0:
                    filtered_themes.append((tid, theme, False))
                else:
                    target_cat = categories[customization_tab]
                    if theme.get("category") == target_cat:
                        filtered_themes.append((tid, theme, False))
        
        theme_y_start = theme_list_area.y + 85
        
        # 列表裁剪区域
        list_view_rect = pygame.Rect(theme_list_area.x, theme_y_start, theme_list_area.width, theme_list_area.height - 85)
        screen.set_clip(list_view_rect)
        
        for i, (theme_id, theme, is_bullet) in enumerate(filtered_themes):
            card_rect = pygame.Rect(theme_list_area.x + 10, theme_y_start + i * 95 - customization_scroll_y, theme_list_area.width - 20, 88)
            
            # 跳过不可见的卡片
            if card_rect.bottom < list_view_rect.top or card_rect.top > list_view_rect.bottom:
                continue
            
            # 根据涂装类型检查解锁状态
            if is_bullet:
                is_unlocked = customization_manager.unlocked_bullet_themes.get(theme_id, False)
            else:
                is_unlocked = customization_manager.unlocked_themes.get(theme_id, False)
            is_equipped = customization_manager.get_equipped_theme(customization_selected_plane, bullet=is_bullet) == theme_id
            
            is_hover = card_rect.collidepoint(mx, my)
            
            # 品质颜色定义
            cat = theme.get("category", "default")
            quality_colors = {
                "default": (150, 150, 150),
                "common": (220, 220, 220),
                "rare": (100, 150, 255),
                "epic": (200, 100, 255),
                "legendary": (255, 215, 0),
                "exclusive": (255, 80, 150)
            }
            q_color = quality_colors.get(cat, GRAY)
            
            # 卡片背景渐变
            card_bg = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
            for cy in range(card_rect.height):
                alpha = 180 - cy
                if is_equipped:
                    color = (0, q_color[1]//4, q_color[2]//4)
                elif is_unlocked:
                    color = (25, 40, 35) if is_hover else (20, 32, 28)
                else:
                    color = (45, 30, 35) if is_hover else (35, 25, 28)
                pygame.draw.line(card_bg, (*color, alpha), (0, cy), (card_rect.width, cy))
            screen.blit(card_bg, card_rect.topleft)
            
            # 边框
            if is_equipped:
                pygame.draw.rect(screen, CYAN, card_rect, 2, border_radius=10)
                pygame.draw.rect(screen, q_color, card_rect.inflate(-6, -6), 1, border_radius=8)
                # 装备标识发光
                glow_alpha = int(80 + 40 * math.sin(t / 200))
                glow_rect = card_rect.inflate(4, 4)
                pygame.draw.rect(screen, (*CYAN[:3], glow_alpha), glow_rect, 2, border_radius=12)
            elif is_hover:
                pygame.draw.rect(screen, (100, 130, 170), card_rect, 2, border_radius=10)
            else:
                pygame.draw.rect(screen, (q_color[0]//2, q_color[1]//2, q_color[2]//2), card_rect, 1, border_radius=10)
            
            # 预览图区域背景
            preview_bg = pygame.Rect(card_rect.x + 8, card_rect.y + 10, 68, 68)
            pygame.draw.rect(screen, (15, 20, 30), preview_bg, border_radius=6)
            pygame.draw.rect(screen, (50, 60, 80), preview_bg, 1, border_radius=6)
            
            # 预览图
            if is_bullet:
                draw_bullet_preview(screen, theme, card_rect.x + 12, card_rect.y + 14, 60, plane_id=customization_selected_plane)
            else:
                if theme_id == "default":
                    visual = plane_data.get('visual', None)
                else:
                    visual = customization_manager.get_theme_visual(customization_selected_plane, plane_data.get('visual', None), preview_theme_id=theme_id)
                preview = get_plane_surf(customization_selected_plane, visual, static=True)
                preview = pygame.transform.scale(preview, (60, 60))
                safe_blit(screen, preview, (card_rect.x + 12, card_rect.y + 14))
            
            # 信息区域
            info_x = card_rect.x + 88
            
            # 涂装名称（带品质色）
            name_surf = font_16.render(theme["name"], True, q_color)
            screen.blit(name_surf, (info_x, card_rect.y + 10))
            
            # 品质标签
            cat_names = {"default": "默认", "common": "普通", "rare": "稀有", "epic": "史诗", "legendary": "传说", "exclusive": "专属"}
            cat_name = cat_names.get(cat, "未知")
            cat_surf = font_11.render(f"[{cat_name}]", True, q_color)
            screen.blit(cat_surf, (info_x + name_surf.get_width() + 8, card_rect.y + 13))
            
            # 描述
            desc_surf = font_13.render(theme["desc"][:28] + ("..." if len(theme["desc"]) > 28 else ""), True, (150, 155, 170))
            screen.blit(desc_surf, (info_x, card_rect.y + 32))
            
            # 专属/尾迹信息
            exclusive_plane = theme.get("exclusive_plane")
            if exclusive_plane:
                p_name = PLANES.get(exclusive_plane, {}).get("name", exclusive_plane)
                info_surf = font_11.render(f"◆ 专属: {p_name}", True, MAGENTA)
                screen.blit(info_surf, (info_x, card_rect.y + 52))
            else:
                trail_style = theme.get("trail_style", "normal")
                info_surf = font_11.render(f"◇ 尾迹: {trail_style}", True, CYAN)
                screen.blit(info_surf, (info_x, card_rect.y + 52))
            
            # ====== 操作按钮（豪华版）======
            btn_w = 95
            btn_h = 36
            btn_rect = pygame.Rect(card_rect.right - btn_w - 12, card_rect.y + 26, btn_w, btn_h)
            
            is_compatible = True
            if exclusive_plane and exclusive_plane != customization_selected_plane:
                is_compatible = False
            
            btn_hover = btn_rect.collidepoint(mx, my)
            
            if not is_compatible:
                # 机型不符
                pygame.draw.rect(screen, (50, 30, 30), btn_rect, border_radius=6)
                pygame.draw.rect(screen, (100, 50, 50), btn_rect, 1, border_radius=6)
                btn_text = font_13.render("机型不符", True, (150, 80, 80))
                screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width()//2, btn_rect.centery - btn_text.get_height()//2))
            elif is_equipped:
                # 已装备
                equip_bg = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
                for by in range(btn_h):
                    alpha = 150 - by * 3
                    pygame.draw.line(equip_bg, (0, 80, 60, alpha), (0, by), (btn_w, by))
                screen.blit(equip_bg, btn_rect.topleft)
                pygame.draw.rect(screen, LIME, btn_rect, 2, border_radius=6)
                btn_text = font_14.render("✓ 已装备", True, LIME)
                screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width()//2, btn_rect.centery - btn_text.get_height()//2))
            elif is_unlocked:
                # 可装备
                equip_bg = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
                for by in range(btn_h):
                    alpha = 180 - by * 3
                    color = (0, 120, 140) if btn_hover else (0, 80, 100)
                    pygame.draw.line(equip_bg, (*color, alpha), (0, by), (btn_w, by))
                screen.blit(equip_bg, btn_rect.topleft)
                pygame.draw.rect(screen, CYAN if btn_hover else (60, 140, 180), btn_rect, 2, border_radius=6)
                if btn_hover:
                    pygame.draw.rect(screen, (0, 200, 220, 50), btn_rect.inflate(4, 4), 2, border_radius=8)
                btn_text = font_14.render("装备", True, WHITE)
                screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width()//2, btn_rect.centery - btn_text.get_height()//2))
            else:
                # 需解锁
                cost = theme.get("cost", 0)
                can_afford = arsenal_save_data['currencies']['cores'] >= cost
                
                unlock_bg = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
                for by in range(btn_h):
                    alpha = 180 - by * 3
                    if can_afford:
                        color = (140, 100, 0) if btn_hover else (100, 70, 0)
                    else:
                        color = (60, 40, 40)
                    pygame.draw.line(unlock_bg, (*color, alpha), (0, by), (btn_w, by))
                screen.blit(unlock_bg, btn_rect.topleft)
                
                border_color = GOLD if (btn_hover and can_afford) else ((180, 140, 0) if can_afford else (80, 60, 60))
                pygame.draw.rect(screen, border_color, btn_rect, 2, border_radius=6)
                if btn_hover and can_afford:
                    pygame.draw.rect(screen, (255, 215, 0, 50), btn_rect.inflate(4, 4), 2, border_radius=8)
                
                text_color = GOLD if can_afford else (120, 100, 100)
                gem_surf = emoji_12.render("💎", True, text_color)
                cost_surf = font_13.render(f" {cost}", True, text_color)
                total_w = gem_surf.get_width() + cost_surf.get_width()
                start_x = btn_rect.centerx - total_w//2
                screen.blit(gem_surf, (start_x, btn_rect.centery - gem_surf.get_height()//2))
                screen.blit(cost_surf, (start_x + gem_surf.get_width(), btn_rect.centery - cost_surf.get_height()//2))
                
                # 需求提示
                if "requirement" in theme:
                    req_surf = font_10.render(theme["requirement"], True, YELLOW)
                    screen.blit(req_surf, (info_x, card_rect.y + 68))
        
        screen.set_clip(None)
        
    else:
        # 未选择机体提示
        font_22 = get_cached_font("SimHei", 22)
        hint_surf = font_22.render("← 请先选择一架机体", True, (100, 110, 130))
        screen.blit(hint_surf, (theme_list_area.centerx - hint_surf.get_width()//2, theme_list_area.centery - 20))
        
    # ====== 消息提示（豪华版）======
    if customization_msg_timer > 0:
        msg_y = HEIGHT - 140
        msg_rect = pygame.Rect(WIDTH//2 - 220, msg_y, 440, 45)
        
        msg_bg = pygame.Surface((440, 45), pygame.SRCALPHA)
        for my_offset in range(45):
            alpha = 200 - my_offset * 2
            pygame.draw.line(msg_bg, (20, 50, 70, alpha), (0, my_offset), (440, my_offset))
        screen.blit(msg_bg, msg_rect.topleft)
        pygame.draw.rect(screen, CYAN, msg_rect, 2, border_radius=8)
        
        msg_surf = font_17.render(customization_msg, True, WHITE)
        screen.blit(msg_surf, (msg_rect.centerx - msg_surf.get_width()//2, msg_rect.centery - msg_surf.get_height()//2))
        customization_msg_timer -= 1
    
    # ====== 大预览区（豪华版）======
    if customization_selected_plane:
        preview_area = pygame.Rect(WIDTH - 340, HEIGHT - 230, 310, 200)
        
        # 预览背景
        preview_bg = pygame.Surface((preview_area.width, preview_area.height), pygame.SRCALPHA)
        for py in range(preview_area.height):
            alpha = int(220 - py * 0.5)
            pygame.draw.line(preview_bg, (10, 15, 25, alpha), (0, py), (preview_area.width, py))
        screen.blit(preview_bg, preview_area.topleft)
        pygame.draw.rect(screen, (60, 90, 130), preview_area, 2, border_radius=12)
        
        if customization_tab == 6:  # 子弹标签
            # 子弹预览标题
            preview_title = pygame.Rect(preview_area.x + 10, preview_area.y + 8, preview_area.width - 20, 28)
            pygame.draw.rect(screen, (50, 30, 60, 180), preview_title, border_radius=6)
            pygame.draw.rect(screen, MAGENTA, preview_title, 1, border_radius=6)
            
            title_icon = emoji_16.render("💫", True, MAGENTA)
            title_text = font_15.render(" 子弹预览", True, MAGENTA)
            screen.blit(title_icon, (preview_title.x + 10, preview_title.y + 4))
            screen.blit(title_text, (preview_title.x + 32, preview_title.y + 5))
            
            # 获取当前装备的子弹涂装
            equipped_theme = customization_manager.get_equipped_theme(customization_selected_plane, bullet=True)
            theme = BULLET_THEMES.get(equipped_theme, BULLET_THEMES.get("default"))
            
            # 绘制大尺寸子弹预览
            preview_size = 100
            preview_x = preview_area.centerx - preview_size // 2
            preview_y = preview_area.y + 50
            draw_bullet_preview(screen, theme, preview_x, preview_y, preview_size, plane_id=customization_selected_plane)
            
            # 显示涂装名称
            name_surf = font_15.render(theme.get("name", "标准子弹"), True, CYAN)
            screen.blit(name_surf, (preview_area.centerx - name_surf.get_width()//2, preview_area.bottom - 35))
        else:
            # 机体预览标题
            preview_title = pygame.Rect(preview_area.x + 10, preview_area.y + 8, preview_area.width - 20, 28)
            pygame.draw.rect(screen, (30, 50, 70, 180), preview_title, border_radius=6)
            pygame.draw.rect(screen, CYAN, preview_title, 1, border_radius=6)
            
            title_icon = emoji_16.render("✈", True, CYAN)
            title_text = font_15.render(" 涂装预览", True, CYAN)
            screen.blit(title_icon, (preview_title.x + 10, preview_title.y + 4))
            screen.blit(title_text, (preview_title.x + 32, preview_title.y + 5))
            
            # 获取当前装备的机体涂装预览
            equipped_theme = customization_manager.get_equipped_theme(customization_selected_plane)
            visual = customization_manager.get_theme_visual(customization_selected_plane, PLANES[customization_selected_plane].get('visual', None))
            big_preview = get_plane_surf(customization_selected_plane, visual)
            big_preview = pygame.transform.scale(big_preview, (130, 130))
            safe_blit(screen, big_preview, (preview_area.centerx - 65, preview_area.y + 45))
            
            # 显示涂装名称
            if equipped_theme in PAINT_THEMES:
                theme_data = PAINT_THEMES[equipped_theme]
                cat = theme_data.get("category", "default")
                quality_colors = {"default": (150, 150, 150), "common": (200, 200, 200), "rare": (100, 150, 255), "epic": (200, 100, 255), "legendary": (255, 215, 0), "exclusive": (255, 80, 150)}
                q_color = quality_colors.get(cat, GRAY)
                name_surf = font_14.render(theme_data["name"], True, q_color)
                screen.blit(name_surf, (preview_area.centerx - name_surf.get_width()//2, preview_area.bottom - 20))
            else:
                name_surf = font_14.render("默认涂装", True, (120, 125, 140))
                screen.blit(name_surf, (preview_area.centerx - name_surf.get_width()//2, preview_area.bottom - 20))
    

def draw_wingman_customization_ui():
    """绘制僚机涂装界面（结构与机体涂装界面完全相同）"""
    global customization_selected_wingman, customization_msg_timer, customization_tab, customization_scroll_y, customization_plane_scroll_y
    
    mx, my = pygame.mouse.get_pos()
    
    t = pygame.time.get_ticks()
    
    # ====== 预加载所有字体（性能优化）======
    font_18 = get_cached_font("SimHei", 18)
    font_17 = get_cached_font("SimHei", 17)
    font_16 = get_cached_font("SimHei", 16)
    font_15 = get_cached_font("SimHei", 15)
    font_14 = get_cached_font("SimHei", 14)
    font_13 = get_cached_font("SimHei", 13)
    font_12 = get_cached_font("SimHei", 12)
    font_11 = get_cached_font("SimHei", 11)
    font_10 = get_cached_font("SimHei", 10)
    font_28 = get_cached_font("SimHei", 28)
    emoji_16 = get_cached_font("Segoe UI Emoji", 16)
    emoji_15 = get_cached_font("Segoe UI Emoji", 15)
    emoji_12 = get_cached_font("Segoe UI Emoji", 12)
    
    # ====== 右上角资源显示（豪华版）======
    res_panel = pygame.Rect(WIDTH - 230, 20, 200, 45)
    res_bg = pygame.Surface((200, 45), pygame.SRCALPHA)
    for ry in range(45):
        alpha = int(160 - ry * 2)
        pygame.draw.line(res_bg, (20, 35, 50, alpha), (0, ry), (200, ry))
    screen.blit(res_bg, res_panel.topleft)
    pygame.draw.rect(screen, (60, 100, 140), res_panel, 1, border_radius=8)
    
    core_icon = emoji_15.render("💎", True, GOLD)
    core_text = font_17.render(f"核心: {arsenal_save_data['currencies']['cores']}", True, GOLD)
    screen.blit(core_icon, (res_panel.x + 15, res_panel.y + 12))
    screen.blit(core_text, (res_panel.x + 40, res_panel.y + 12))
    
    # ====== 左侧：僚机槽位列表（豪华版）======
    wingman_list_area = pygame.Rect(25, 115, 290, HEIGHT - 195)
    
    # 面板背景渐变
    wingman_bg = pygame.Surface((wingman_list_area.width, wingman_list_area.height), pygame.SRCALPHA)
    for wy in range(wingman_list_area.height):
        alpha = int(200 - wy * 0.1)
        pygame.draw.line(wingman_bg, (12, 18, 30, alpha), (0, wy), (wingman_list_area.width, wy))
    screen.blit(wingman_bg, wingman_list_area.topleft)
    pygame.draw.rect(screen, (80, 60, 120), wingman_list_area, 2, border_radius=10)
    
    # 面板标题
    title_rect = pygame.Rect(wingman_list_area.x + 10, wingman_list_area.y + 8, wingman_list_area.width - 20, 32)
    pygame.draw.rect(screen, (40, 30, 60, 200), title_rect, border_radius=6)
    pygame.draw.rect(screen, MAGENTA, title_rect, 1, border_radius=6)
    
    list_icon = emoji_15.render("👥", True, MAGENTA)
    list_title = font_18.render(" 选择僚机", True, MAGENTA)
    screen.blit(list_icon, (title_rect.x + 15, title_rect.y + 6))
    screen.blit(list_title, (title_rect.x + 42, title_rect.y + 6))
    
    # 列表内容区域
    list_content_rect = pygame.Rect(wingman_list_area.x, wingman_list_area.y + 48, wingman_list_area.width, wingman_list_area.height - 48)
    screen.set_clip(list_content_rect)
    
    wingman_start_y = list_content_rect.y + 5
    wingman_slots = [
        {"id": 0, "name": "僚机槽位 1", "icon": "①"},
        {"id": 1, "name": "僚机槽位 2", "icon": "②"},
        {"id": 2, "name": "僚机槽位 3", "icon": "③"},
        {"id": 3, "name": "僚机槽位 4", "icon": "④"}
    ]
    
    for i, slot in enumerate(wingman_slots):
        rect = pygame.Rect(wingman_list_area.x + 8, wingman_start_y + i * 70, wingman_list_area.width - 16, 65)
        
        equipped_theme = customization_manager.equipped_wingman_themes.get(f"slot_{slot['id']}", "default")
        is_selected = (customization_selected_wingman == slot['id'])
        is_hover = rect.collidepoint(mx, my)
        
        # 卡片背景渐变
        card_bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for cy in range(rect.height):
            alpha = 180 - cy * 2
            if is_selected:
                color = (50, 40, 80)
            elif is_hover:
                color = (40, 50, 70)
            else:
                color = (25, 30, 45)
            pygame.draw.line(card_bg, (*color, alpha), (0, cy), (rect.width, cy))
        screen.blit(card_bg, rect.topleft)
        
        # 边框
        if is_selected:
            pygame.draw.rect(screen, MAGENTA, rect, 2, border_radius=8)
            glow_alpha = int(60 + 30 * math.sin(t / 200))
            pygame.draw.rect(screen, (*MAGENTA[:3], glow_alpha), rect.inflate(4, 4), 2, border_radius=10)
        elif is_hover:
            pygame.draw.rect(screen, (100, 80, 140), rect, 1, border_radius=8)
        else:
            pygame.draw.rect(screen, (60, 55, 80), rect, 1, border_radius=8)
        
        # 左侧预览图
        if equipped_theme != "default" and equipped_theme in PAINT_THEMES:
            theme = PAINT_THEMES[equipped_theme]
            exclusive_plane = theme.get("exclusive_plane")
            if exclusive_plane and exclusive_plane in PLANES:
                visual = customization_manager.get_theme_visual(exclusive_plane, PLANES[exclusive_plane].get('visual', None), preview_theme_id=equipped_theme)
                icon = get_plane_surf(exclusive_plane, visual, static=True)
                icon = pygame.transform.scale(icon, (50, 50))
                safe_blit(screen, icon, (rect.x + 8, rect.y + 8))
        else:
            # 默认空槽位图标
            slot_icon = font_28.render(slot["icon"], True, (80, 80, 100))
            screen.blit(slot_icon, (rect.x + 20, rect.y + 18))
        
        # 僚机编号
        name_surf = font_15.render(slot['name'], True, WHITE if is_selected else (200, 200, 210))
        screen.blit(name_surf, (rect.x + 68, rect.y + 12))
        
        # 显示当前装备的涂装
        if equipped_theme != "default" and equipped_theme in PAINT_THEMES:
            theme = PAINT_THEMES[equipped_theme]
            theme_name = theme["name"]
            cat = theme.get("category", "default")
            quality_colors = {"default": (150, 150, 150), "common": (200, 200, 200), "rare": (100, 150, 255), "epic": (200, 100, 255), "legendary": (255, 215, 0), "exclusive": (255, 80, 150)}
            q_color = quality_colors.get(cat, GRAY)
            theme_surf = font_12.render(f"[{theme_name}]", True, q_color)
            screen.blit(theme_surf, (rect.x + 68, rect.y + 35))
        else:
            theme_surf = font_12.render("[未装备涂装]", True, (100, 105, 115))
            screen.blit(theme_surf, (rect.x + 68, rect.y + 35))
    
    screen.set_clip(None)
    
    # ====== 右侧：涂装列表面板（豪华版）======
    theme_list_area = pygame.Rect(330, 115, 620, HEIGHT - 195)
    
    # 面板背景渐变
    theme_bg = pygame.Surface((theme_list_area.width, theme_list_area.height), pygame.SRCALPHA)
    for ty in range(theme_list_area.height):
        alpha = int(200 - ty * 0.08)
        pygame.draw.line(theme_bg, (12, 18, 30, alpha), (0, ty), (theme_list_area.width, ty))
    screen.blit(theme_bg, theme_list_area.topleft)
    pygame.draw.rect(screen, (60, 90, 130), theme_list_area, 2, border_radius=10)
    
    # 面板标题
    panel_title_rect = pygame.Rect(theme_list_area.x + 10, theme_list_area.y + 8, theme_list_area.width - 20, 32)
    pygame.draw.rect(screen, (25, 50, 75, 200), panel_title_rect, border_radius=6)
    pygame.draw.rect(screen, CYAN, panel_title_rect, 1, border_radius=6)
    
    filter_text = "全部机体" if wingman_theme_filter is None else PLANES[wingman_theme_filter]["name"]
    panel_icon = emoji_15.render("🎨", True, CYAN)
    panel_title = font_16.render(f" 筛选: {filter_text}", True, CYAN)
    screen.blit(panel_icon, (panel_title_rect.x + 12, panel_title_rect.y + 6))
    screen.blit(panel_title, (panel_title_rect.x + 35, panel_title_rect.y + 7))
    
    # ====== 机体筛选按钮行（豪华版）======
    filter_y = theme_list_area.y + 48
    filter_btn_w = 52
    filter_btn_h = 24
    filter_start_x = theme_list_area.x + 10
    
    # "全部"按钮（豪华版）
    all_btn = pygame.Rect(filter_start_x, filter_y, filter_btn_w, filter_btn_h)
    all_active = (wingman_theme_filter is None)
    all_hover = all_btn.collidepoint(mx, my)
    
    all_bg = pygame.Surface((filter_btn_w, filter_btn_h), pygame.SRCALPHA)
    for by in range(filter_btn_h):
        alpha = 150 - by * 4
        if all_active:
            color = (0, 80, 100)
        elif all_hover:
            color = (40, 55, 70)
        else:
            color = (30, 38, 50)
        pygame.draw.line(all_bg, (*color, alpha), (0, by), (filter_btn_w, by))
    screen.blit(all_bg, all_btn.topleft)
    pygame.draw.rect(screen, CYAN if all_active else ((70, 100, 130) if all_hover else (50, 60, 75)), all_btn, 1, border_radius=5)
    
    all_text = font_11.render("全部", True, CYAN if all_active else WHITE)
    screen.blit(all_text, (all_btn.centerx - all_text.get_width()//2, all_btn.centery - all_text.get_height()//2))
    
    # 机体筛选按钮（豪华版）
    plane_keys_list = list(PLANES.keys())
    for pi, plane_id in enumerate(plane_keys_list[:10]):
        btn_x = filter_start_x + (pi + 1) * (filter_btn_w + 4)
        if btn_x + filter_btn_w > theme_list_area.right - 10:
            break
        plane_btn = pygame.Rect(btn_x, filter_y, filter_btn_w, filter_btn_h)
        is_active = (wingman_theme_filter == plane_id)
        is_hover = plane_btn.collidepoint(mx, my)
        
        btn_bg = pygame.Surface((filter_btn_w, filter_btn_h), pygame.SRCALPHA)
        for by in range(filter_btn_h):
            alpha = 150 - by * 4
            if is_active:
                color = (PLANES[plane_id]["color"][0]//4, PLANES[plane_id]["color"][1]//4, PLANES[plane_id]["color"][2]//4)
            elif is_hover:
                color = (40, 50, 65)
            else:
                color = (28, 35, 48)
            pygame.draw.line(btn_bg, (*color, alpha), (0, by), (filter_btn_w, by))
        screen.blit(btn_bg, plane_btn.topleft)
        
        border_color = PLANES[plane_id]["color"] if is_active else ((70, 90, 120) if is_hover else (45, 55, 70))
        pygame.draw.rect(screen, border_color, plane_btn, 1, border_radius=5)
        
        short_name = PLANES[plane_id]["name"][:2]
        btn_text = font_10.render(short_name, True, PLANES[plane_id]["color"] if is_active else (WHITE if is_hover else (170, 175, 185)))
        screen.blit(btn_text, (plane_btn.centerx - btn_text.get_width()//2, plane_btn.centery - btn_text.get_height()//2))
    
    # 第二行筛选按钮（豪华版）
    filter_y2 = filter_y + filter_btn_h + 4
    for pi, plane_id in enumerate(plane_keys_list[10:]):
        btn_x = filter_start_x + pi * (filter_btn_w + 4)
        if btn_x + filter_btn_w > theme_list_area.right - 10:
            break
        plane_btn = pygame.Rect(btn_x, filter_y2, filter_btn_w, filter_btn_h)
        is_active = (wingman_theme_filter == plane_id)
        is_hover = plane_btn.collidepoint(mx, my)
        
        btn_bg = pygame.Surface((filter_btn_w, filter_btn_h), pygame.SRCALPHA)
        for by in range(filter_btn_h):
            alpha = 150 - by * 4
            if is_active:
                color = (PLANES[plane_id]["color"][0]//4, PLANES[plane_id]["color"][1]//4, PLANES[plane_id]["color"][2]//4)
            elif is_hover:
                color = (40, 50, 65)
            else:
                color = (28, 35, 48)
            pygame.draw.line(btn_bg, (*color, alpha), (0, by), (filter_btn_w, by))
        screen.blit(btn_bg, plane_btn.topleft)
        
        border_color = PLANES[plane_id]["color"] if is_active else ((70, 90, 120) if is_hover else (45, 55, 70))
        pygame.draw.rect(screen, border_color, plane_btn, 1, border_radius=5)
        
        short_name = PLANES[plane_id]["name"][:2]
        btn_text = font_10.render(short_name, True, PLANES[plane_id]["color"] if is_active else (WHITE if is_hover else (170, 175, 185)))
        screen.blit(btn_text, (plane_btn.centerx - btn_text.get_width()//2, plane_btn.centery - btn_text.get_height()//2))
    
    # ====== 筛选涂装 ======
    filtered_themes = []
    for tid, theme in PAINT_THEMES.items():
        exclusive_plane = theme.get("exclusive_plane")
        if not exclusive_plane:
            continue
        if wingman_theme_filter is not None and exclusive_plane != wingman_theme_filter:
            continue
        filtered_themes.append((tid, theme))
    
    theme_y_start = theme_list_area.y + 105
    
    # 列表裁剪区域
    list_view_rect = pygame.Rect(theme_list_area.x, theme_y_start, theme_list_area.width, theme_list_area.height - 105)
    screen.set_clip(list_view_rect)
    
    for i, (theme_id, theme) in enumerate(filtered_themes):
        card_rect = pygame.Rect(theme_list_area.x + 10, theme_y_start + i * 95 - customization_scroll_y, theme_list_area.width - 20, 88)
        
        # 跳过不可见的卡片
        if card_rect.bottom < list_view_rect.top or card_rect.top > list_view_rect.bottom:
            continue
        
        is_unlocked = customization_manager.unlocked_themes.get(theme_id, False)
        current_equipped = customization_manager.equipped_wingman_themes.get(f"slot_{customization_selected_wingman}", "default")
        is_equipped = (current_equipped == theme_id)
        is_hover = card_rect.collidepoint(mx, my)
        
        # 品质颜色定义
        cat = theme.get("category", "default")
        quality_colors = {"default": (150, 150, 150), "common": (220, 220, 220), "rare": (100, 150, 255), "epic": (200, 100, 255), "legendary": (255, 215, 0), "exclusive": (255, 80, 150)}
        q_color = quality_colors.get(cat, GRAY)
        
        # 卡片背景渐变
        card_bg = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
        for cy in range(card_rect.height):
            alpha = 180 - cy
            if is_equipped:
                color = (0, q_color[1]//4, q_color[2]//4)
            elif is_unlocked:
                color = (25, 40, 35) if is_hover else (20, 32, 28)
            else:
                color = (45, 30, 35) if is_hover else (35, 25, 28)
            pygame.draw.line(card_bg, (*color, alpha), (0, cy), (card_rect.width, cy))
        screen.blit(card_bg, card_rect.topleft)
        
        # 边框
        if is_equipped:
            pygame.draw.rect(screen, MAGENTA, card_rect, 2, border_radius=10)
            pygame.draw.rect(screen, q_color, card_rect.inflate(-6, -6), 1, border_radius=8)
            glow_alpha = int(80 + 40 * math.sin(t / 200))
            pygame.draw.rect(screen, (*MAGENTA[:3], glow_alpha), card_rect.inflate(4, 4), 2, border_radius=12)
        elif is_hover:
            pygame.draw.rect(screen, (100, 130, 170), card_rect, 2, border_radius=10)
        else:
            pygame.draw.rect(screen, (q_color[0]//2, q_color[1]//2, q_color[2]//2), card_rect, 1, border_radius=10)
        
        # 预览图区域
        preview_bg = pygame.Rect(card_rect.x + 8, card_rect.y + 10, 68, 68)
        pygame.draw.rect(screen, (15, 20, 30), preview_bg, border_radius=6)
        pygame.draw.rect(screen, (50, 60, 80), preview_bg, 1, border_radius=6)
        
        # 预览图
        exclusive_plane = theme.get("exclusive_plane")
        if exclusive_plane and exclusive_plane in PLANES:
            visual = customization_manager.get_theme_visual(exclusive_plane, PLANES[exclusive_plane].get('visual', None), preview_theme_id=theme_id)
            preview = get_plane_surf(exclusive_plane, visual, static=True)
            preview = pygame.transform.scale(preview, (60, 60))
            safe_blit(screen, preview, (card_rect.x + 12, card_rect.y + 14))
        
        # 信息区域
        info_x = card_rect.x + 88
        
        # 涂装名称
        name_surf = font_16.render(theme["name"], True, q_color)
        screen.blit(name_surf, (info_x, card_rect.y + 10))
        
        # 品质标签
        cat_names = {"default": "默认", "common": "普通", "rare": "稀有", "epic": "史诗", "legendary": "传说", "exclusive": "专属"}
        cat_name = cat_names.get(cat, "未知")
        cat_surf = font_11.render(f"[{cat_name}]", True, q_color)
        screen.blit(cat_surf, (info_x + name_surf.get_width() + 8, card_rect.y + 13))
        
        # 描述
        desc_surf = font_13.render(theme["desc"][:28] + ("..." if len(theme["desc"]) > 28 else ""), True, (150, 155, 170))
        screen.blit(desc_surf, (info_x, card_rect.y + 32))
        
        # 专属机体信息
        if exclusive_plane:
            p_name = PLANES.get(exclusive_plane, {}).get("name", exclusive_plane)
            info_surf = font_11.render(f"◆ 专属: {p_name}", True, MAGENTA)
            screen.blit(info_surf, (info_x, card_rect.y + 52))
        
        # ====== 操作按钮（豪华版）======
        btn_w = 95
        btn_h = 36
        btn_rect = pygame.Rect(card_rect.right - btn_w - 12, card_rect.y + 26, btn_w, btn_h)
        btn_hover = btn_rect.collidepoint(mx, my)
        
        if is_equipped:
            equip_bg = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            for by in range(btn_h):
                alpha = 150 - by * 3
                pygame.draw.line(equip_bg, (60, 40, 80, alpha), (0, by), (btn_w, by))
            screen.blit(equip_bg, btn_rect.topleft)
            pygame.draw.rect(screen, LIME, btn_rect, 2, border_radius=6)
            btn_text = font_14.render("✓ 已装备", True, LIME)
            screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width()//2, btn_rect.centery - btn_text.get_height()//2))
        elif is_unlocked:
            equip_bg = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            for by in range(btn_h):
                alpha = 180 - by * 3
                color = (80, 50, 100) if btn_hover else (50, 35, 70)
                pygame.draw.line(equip_bg, (*color, alpha), (0, by), (btn_w, by))
            screen.blit(equip_bg, btn_rect.topleft)
            pygame.draw.rect(screen, MAGENTA if btn_hover else (120, 70, 140), btn_rect, 2, border_radius=6)
            if btn_hover:
                pygame.draw.rect(screen, (200, 100, 200, 50), btn_rect.inflate(4, 4), 2, border_radius=8)
            btn_text = font_14.render("装备", True, WHITE)
            screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width()//2, btn_rect.centery - btn_text.get_height()//2))
        else:
            cost = theme.get("cost", 0)
            can_afford = arsenal_save_data["currencies"]["cores"] >= cost
            
            unlock_bg = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            for by in range(btn_h):
                alpha = 180 - by * 3
                if can_afford:
                    color = (140, 100, 0) if btn_hover else (100, 70, 0)
                else:
                    color = (60, 40, 40)
                pygame.draw.line(unlock_bg, (*color, alpha), (0, by), (btn_w, by))
            screen.blit(unlock_bg, btn_rect.topleft)
            
            border_color = GOLD if (btn_hover and can_afford) else ((180, 140, 0) if can_afford else (80, 60, 60))
            pygame.draw.rect(screen, border_color, btn_rect, 2, border_radius=6)
            
            text_color = GOLD if can_afford else (120, 100, 100)
            gem_surf = emoji_12.render("💎", True, text_color)
            cost_surf = font_13.render(f" {cost}", True, text_color)
            total_w = gem_surf.get_width() + cost_surf.get_width()
            start_x = btn_rect.centerx - total_w//2
            screen.blit(gem_surf, (start_x, btn_rect.centery - gem_surf.get_height()//2))
            screen.blit(cost_surf, (start_x + gem_surf.get_width(), btn_rect.centery - cost_surf.get_height()//2))
    
    screen.set_clip(None)
    
    # ====== 消息提示（豪华版）======
    if customization_msg_timer > 0:
        msg_y = HEIGHT - 140
        msg_rect = pygame.Rect(WIDTH//2 - 220, msg_y, 440, 45)
        
        msg_bg = pygame.Surface((440, 45), pygame.SRCALPHA)
        for my_offset in range(45):
            alpha = 200 - my_offset * 2
            pygame.draw.line(msg_bg, (40, 30, 60, alpha), (0, my_offset), (440, my_offset))
        screen.blit(msg_bg, msg_rect.topleft)
        pygame.draw.rect(screen, MAGENTA, msg_rect, 2, border_radius=8)
        
        msg_surf = font_17.render(customization_msg, True, WHITE)
        screen.blit(msg_surf, (msg_rect.centerx - msg_surf.get_width()//2, msg_rect.centery - msg_surf.get_height()//2))
        customization_msg_timer -= 1
    
    # ====== 大预览区（豪华版）======
    preview_area = pygame.Rect(WIDTH - 340, HEIGHT - 260, 310, 230)
    
    # 预览背景
    preview_bg = pygame.Surface((preview_area.width, preview_area.height), pygame.SRCALPHA)
    for py in range(preview_area.height):
        alpha = int(220 - py * 0.5)
        pygame.draw.line(preview_bg, (15, 12, 25, alpha), (0, py), (preview_area.width, py))
    screen.blit(preview_bg, preview_area.topleft)
    pygame.draw.rect(screen, (100, 70, 130), preview_area, 2, border_radius=12)
    
    # 预览标题
    preview_title = pygame.Rect(preview_area.x + 10, preview_area.y + 8, preview_area.width - 20, 28)
    pygame.draw.rect(screen, (50, 35, 70, 180), preview_title, border_radius=6)
    pygame.draw.rect(screen, MAGENTA, preview_title, 1, border_radius=6)
    
    title_icon = emoji_15.render("👥", True, MAGENTA)
    title_text = font_15.render(" 涂装预览", True, MAGENTA)
    screen.blit(title_icon, (preview_title.x + 10, preview_title.y + 4))
    screen.blit(title_text, (preview_title.x + 35, preview_title.y + 5))
    
    # 获取当前装备的涂装预览
    equipped_theme = customization_manager.equipped_wingman_themes.get(f"slot_{customization_selected_wingman}", "default")
    if equipped_theme != "default" and equipped_theme in PAINT_THEMES:
        theme = PAINT_THEMES[equipped_theme]
        exclusive_plane = theme.get("exclusive_plane")
        if exclusive_plane and exclusive_plane in PLANES:
            visual = customization_manager.get_theme_visual(exclusive_plane, PLANES[exclusive_plane].get('visual', None), preview_theme_id=equipped_theme)
            big_preview = get_plane_surf(exclusive_plane, visual)
            big_preview = pygame.transform.scale(big_preview, (140, 140))
            safe_blit(screen, big_preview, (preview_area.centerx - 70, preview_area.y + 50))
            
            # 涂装名称（带品质色）
            cat = theme.get("category", "default")
            quality_colors = {"default": (150, 150, 150), "common": (200, 200, 200), "rare": (100, 150, 255), "epic": (200, 100, 255), "legendary": (255, 215, 0), "exclusive": (255, 80, 150)}
            q_color = quality_colors.get(cat, GRAY)
            
            name_surf = font_15.render(theme["name"], True, q_color)
            screen.blit(name_surf, (preview_area.centerx - name_surf.get_width()//2, preview_area.bottom - 45))
            
            # 专属机体
            p_name = PLANES.get(exclusive_plane, {}).get("name", exclusive_plane)
            plane_surf = font_12.render(f"[{p_name}]", True, MAGENTA)
            screen.blit(plane_surf, (preview_area.centerx - plane_surf.get_width()//2, preview_area.bottom - 22))
    else:
        # 未装备涂装提示
        hint_surf = font_16.render("未装备涂装", True, (100, 90, 120))
        screen.blit(hint_surf, (preview_area.centerx - hint_surf.get_width()//2, preview_area.centery + 20))


def draw_bar(x, y, w, h, current, max_val, color, bg_color=(30,30,40), border_color=None):
    """绘制进度条 (赛博朋克风格)"""
    # 背景
    pygame.draw.rect(screen, bg_color, (x, y, w, h))
    # 进度
    fill = (current / max_val) * w if max_val > 0 else 0
    pygame.draw.rect(screen, color, (x, y, fill, h))
    # 边框
    if border_color:
        pygame.draw.rect(screen, border_color, (x, y, w, h), 1)

def draw_stat_bar(x, y, label, current, max_val, color, label_width=100):
    """绘制带标签的属性条"""
    bar_w = 200
    bar_h = 12
    
    # 标签
    draw_text(screen, label, 12, x, y-10, (150, 150, 200))
    
    # 进度条
    draw_bar(x, y, bar_w, bar_h, current, max_val, color, (20, 20, 30), CYAN)
    
    # 数值文本
    txt = f"{int(current)}/{int(max_val)}"
    draw_text(screen, txt, 10, x + bar_w + 10, y, WHITE)

# ==============================================================================
#   赛博朋克视觉效果函数
# ==============================================================================

def draw_tactical_grid(surf):
    """绘制战术网格背景（淡蓝色网格线，覆盖全屏）"""
    grid_spacing = 40
    line_color = CYBER_GRID_LINE
    
    # 竖线
    for x in range(0, WIDTH + grid_spacing, grid_spacing):
        pygame.draw.line(surf, line_color, (x, 0), (x, HEIGHT), 1)
    
    # 横线
    for y in range(0, HEIGHT + grid_spacing, grid_spacing):
        pygame.draw.line(surf, line_color, (0, y), (WIDTH, y), 1)

# Use `draw_cyber_rect` from `utils.py` to avoid duplicate implementations and signature drift

def draw_neon_line(surf, start_pos, end_pos, color, width=2):
    """绘制霓虹线条"""
    pygame.draw.line(surf, color, start_pos, end_pos, width)

def apply_screen_shake(intensity=5):
    """应用屏幕抖动效果（返回抖动偏移）"""
    return (random.randint(-intensity, intensity), random.randint(-intensity, intensity))

def draw_boss_themed_background(surf, boss, game_tick):
    """为Boss战斗绘制对应主题的华丽背景和特效"""
    if not boss:
        draw_tactical_grid(surf)
        return
    
    boss_type = getattr(boss, 'type', 'carrier')
    boss_color = BOSS_DB.get(boss_type, {}).get('color', CYAN)
    
    # ===== 各Boss特色背景主题 =====
    if boss_type == "carrier":  # 毁灭者级·虚空母舰 - 红色虚空舰队主题
        # 背景：深红色渐变
        for y in range(HEIGHT):
            alpha = int(30 * (y / HEIGHT))
            col = (40 + alpha, 10, 10 + alpha//2)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        # 动态无人机轨迹（虚线）
        for i in range(5):
            offset = (game_tick + i * 12) % WIDTH
            pygame.draw.line(surf, (180, 30, 30, 50), (offset, HEIGHT//3 + i*30), 
                           (offset + 100, HEIGHT//3 + i*30), 1)
        
    elif boss_type == "fortress":  # 不朽级·钢铁堡垒 - 橙色工业堡垒主题
        # 背景：深橙色工业风格
        for y in range(HEIGHT):
            alpha = int(25 * (y / HEIGHT))
            col = (50 + alpha, 35 + alpha//2, 10)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        # 工业网格（更密集）
        grid_size = 30
        grid_offset = (game_tick * 0.5) % grid_size
        for x in range(0, WIDTH, grid_size):
            pygame.draw.line(surf, (100, 70, 20), (x + grid_offset, 0), (x + grid_offset, HEIGHT), 1)
        # 炮台光束
        for i in range(3):
            angle = (game_tick + i * 120) / 180 * math.pi
            ex = int(WIDTH//2 + 300 * math.cos(angle))
            ey = int(HEIGHT//2 + 300 * math.sin(angle))
            pygame.draw.line(surf, (255, 140, 0), (WIDTH//2, HEIGHT//2), (ex, ey), 2)
        
    elif boss_type == "assassin":  # 幻影级·虚空刺客 - 紫红色隐秘主题
        # 背景：深紫色隐秘主题
        for y in range(HEIGHT):
            alpha = int(35 * (y / HEIGHT))
            col = (50 + alpha//2, 10, 50 + alpha)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        # 随机闪烁暗影
        for i in range(15):
            shadow_x = (game_tick + i * 50) % (WIDTH + 100) - 50
            shadow_y = random.randint(0, HEIGHT)
            alpha = int(50 * math.sin(game_tick / 30 + i * 0.5))
            pygame.draw.circle(surf, (100 + alpha, 30, 100 + alpha), (shadow_x, shadow_y), 30)
        
    elif boss_type == "seraphim":  # 审判级·炽天使 - 金色圣光主题
        # 背景：深金色圣光主题
        for y in range(HEIGHT):
            alpha = int(30 * (y / HEIGHT))
            col = (60 + alpha, 50 + alpha//2, 20)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        # 从上方投射的圣光光束
        for i in range(6):
            angle = (i / 6) * math.pi * 2 + game_tick / 100
            bx = int(WIDTH//2 + 200 * math.cos(angle))
            intensity = int(100 * abs(math.sin(game_tick / 60 + i)))
            pygame.draw.line(surf, (220 + intensity//2, 180 + intensity//3, 80), 
                           (bx, 0), (WIDTH//2, HEIGHT), 1)
        
    elif boss_type == "leviathan":  # 深渊巨兽·利维坦 - 紫色深渊主题
        # 背景：深紫色深渊主题
        for y in range(HEIGHT):
            alpha = int(35 * (y / HEIGHT))
            col = (40 + alpha//3, 10, 60 + alpha)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        # 波纹效果（深渊脉动）
        for i in range(8):
            cy = (game_tick * 2 + i * 40) % HEIGHT
            radius = 50 + int(30 * math.sin(game_tick / 40))
            pygame.draw.circle(surf, (100, 30, 150, 30), (WIDTH//2, cy), radius, 2)
        
    elif boss_type == "overlord":  # 蜂群主宰·奥伯龙 - 青色蜂群主题
        # 背景：深青色蜂群主题
        for y in range(HEIGHT):
            alpha = int(30 * (y / HEIGHT))
            col = (10, 50 + alpha, 60 + alpha)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        # 蜂群轨迹（六边形飞行路径）
        for i in range(12):
            angle = (game_tick + i * 30) / 180 * math.pi
            x = int(WIDTH//2 + 150 * math.cos(angle))
            y = int(HEIGHT//2 + 150 * math.sin(angle))
            pygame.draw.circle(surf, (0, 200, 200), (x, y), 3)
        
    elif boss_type == "ragnarok":  # 终焉机神·诸神黄昏 - 深红色末日主题
        # 背景：血红色末日主题（炽热）
        for y in range(HEIGHT):
            alpha = int(40 * (y / HEIGHT))
            col = (80 + alpha, 10, 5)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        # 破坏性闪电网络
        for i in range(8):
            x_start = random.randint(0, WIDTH)
            y_start = random.randint(0, HEIGHT)
            x_end = x_start + random.randint(-150, 150)
            y_end = y_start + random.randint(-150, 150)
            pygame.draw.line(surf, (255, 50, 0), (x_start, y_start), (x_end, y_end), 1)
        
    elif boss_type == "hydra":  # 九头蛇·剧毒领主 - 绿色毒液主题
        # 背景：深绿色毒液主题
        for y in range(HEIGHT):
            alpha = int(30 * (y / HEIGHT))
            col = (10, 50 + alpha, 20 + alpha//2)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        # 毒液流动效果
        for i in range(6):
            py = (game_tick * 1.5 + i * 60) % HEIGHT
            pygame.draw.line(surf, (0, 200, 0), (0, py), (WIDTH, py + int(30 * math.sin(game_tick/50 + i))), 2)
        
    elif boss_type == "chronos":  # 时之主·克洛诺斯 - 蓝色时间主题
        # 背景：深蓝色时间主题
        for y in range(HEIGHT):
            alpha = int(30 * (y / HEIGHT))
            col = (30 + alpha, 50 + alpha, 80 + alpha)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        # 时间轮盘（旋转的同心圆）
        for i in range(5):
            angle = (game_tick / 100 + i * 0.4) * math.pi * 2
            radius = 100 + i * 40
            points = []
            for j in range(12):
                px = int(WIDTH//2 + radius * math.cos(angle + j * math.pi / 6))
                py = int(HEIGHT//2 + radius * math.sin(angle + j * math.pi / 6))
                points.append((px, py))
            if len(points) > 1:
                for k in range(len(points)):
                    pygame.draw.line(surf, (100, 150, 255), points[k], points[(k+1) % len(points)], 1)
        
    elif boss_type == "gazer":  # 深渊凝视者 - 红色凝视主题
        # 背景：深红色凝视主题
        for y in range(HEIGHT):
            alpha = int(35 * (y / HEIGHT))
            col = (70 + alpha, 10, 10)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        # 眼睛瞳孔扫描线
        for i in range(8):
            angle = (game_tick / 100 + i * math.pi / 4) * 2
            ex = int(WIDTH//2 + 250 * math.cos(angle))
            ey = int(HEIGHT//2 + 250 * math.sin(angle))
            pygame.draw.line(surf, (255, 0, 0), (WIDTH//2, HEIGHT//2), (ex, ey), 1)
        
    elif boss_type == "lich":  # 赛博巫妖 - 青绿色诅咒主题
        # 背景：青绿色诅咒主题
        for y in range(HEIGHT):
            alpha = int(30 * (y / HEIGHT))
            col = (50 + alpha//2, 80 + alpha, 80 + alpha)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        # 飘浮的诅咒符文
        for i in range(12):
            cx = (game_tick * 0.8 + i * 40) % (WIDTH + 100) - 50
            cy = (game_tick * 0.3 + i * 35) % HEIGHT
            brightness = int(100 * abs(math.sin(game_tick / 80 + i)))
            pygame.draw.circle(surf, (100 + brightness, 200 + brightness//2, 200 + brightness//2), (cx, cy), 4)
        
    elif boss_type == "tempest":  # 风暴引擎 - 蓝色暴风主题
        # 背景：深蓝色暴风主题
        for y in range(HEIGHT):
            alpha = int(30 * (y / HEIGHT))
            col = (30 + alpha, 60 + alpha, 100 + alpha)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        # 风力线动画
        for i in range(10):
            wind_y = (game_tick * 3 + i * 30) % HEIGHT
            wave_offset = int(50 * math.sin(game_tick / 40 + i * 0.3))
            pygame.draw.line(surf, (100, 150, 220), (wave_offset, wind_y), (WIDTH + wave_offset, wind_y), 1)
        
    elif boss_type == "void_golem":  # 虚空魔像 - 紫色齿轮机械主题（升级版）
        # 背景：炫彩紫色机械主题
        for y in range(HEIGHT):
            alpha = int(40 * (y / HEIGHT))
            # 更亮的紫色渐变
            col = (80 + alpha, 20 + alpha//2, 150 + alpha)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        
        # 背景网格：发光的机械网格
        grid_size = 50
        for x in range(0, WIDTH + grid_size, grid_size):
            brightness = int(100 + 80 * math.sin(game_tick / 80 + x / 100))
            pygame.draw.line(surf, (brightness // 2, 30, brightness), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT + grid_size, grid_size):
            brightness = int(100 + 80 * math.sin(game_tick / 80 + y / 100))
            pygame.draw.line(surf, (brightness // 2, 30, brightness), (0, y), (WIDTH, y), 1)
        
        # 旋转的齿轮图案（增强版）
        for gear_idx in range(4):
            gear_angle = (game_tick / 80 + gear_idx * math.pi / 2) * 2  # 更快的旋转
            gear_x = WIDTH // 2 + [180, -180, 0, 0][gear_idx]
            gear_y = HEIGHT // 2 + [0, 0, 180, -180][gear_idx]
            
            # 外光晕
            glow_radius = 100 + int(30 * math.sin(game_tick / 60))
            pygame.draw.circle(surf, (100, 0, 200, 50), (gear_x, gear_y), glow_radius, 3)
            
            # 绘制齿轮（更大）
            for tooth in range(12):
                tooth_angle = gear_angle + tooth * math.pi / 6
                x1 = int(gear_x + 50 * math.cos(tooth_angle))
                y1 = int(gear_y + 50 * math.sin(tooth_angle))
                x2 = int(gear_x + 80 * math.cos(tooth_angle))
                y2 = int(gear_y + 80 * math.sin(tooth_angle))
                # 齿轮渐变颜色
                tooth_color = (200 + int(55 * math.sin(gear_angle + tooth)), 0, 255)
                pygame.draw.line(surf, tooth_color, (x1, y1), (x2, y2), 2)
            
            # 齿轮圆盘（带渐变）
            pygame.draw.circle(surf, (180, 0, 255), (gear_x, gear_y), 40, 3)
            pygame.draw.circle(surf, (150, 0, 220), (gear_x, gear_y), 25, 2)
            
            # 中心能量核
            core_brightness = int(200 + 55 * math.sin(game_tick / 50))
            pygame.draw.circle(surf, (core_brightness, 100, 255), (gear_x, gear_y), 12)
        
        # 能量脉冲波纹
        for wave_idx in range(3):
            wave_radius = (game_tick * 2 + wave_idx * 60) % 500
            wave_alpha = int(150 * (1 - wave_radius / 500))
            if wave_alpha > 0:
                pygame.draw.circle(surf, (150 + wave_alpha//3, 50, 200), (WIDTH//2, HEIGHT//2), wave_radius, 2)
        
    elif boss_type == "abyss_queen":  # 星渊女王 - 星系主题（升级版）
        # 背景：炫彩星系主题
        for y in range(HEIGHT):
            alpha = int(45 * (y / HEIGHT))
            # 更亮的紫蓝色渐变
            col = (100 + alpha//2, 40 + alpha//3, 180 + alpha)
            pygame.draw.line(surf, col, (0, y), (WIDTH, y), 1)
        
        # 星光网格背景
        for i in range(8):
            angle = i * math.pi / 4
            for dist in range(100, WIDTH, 100):
                x = int(WIDTH//2 + dist * math.cos(angle))
                y = int(HEIGHT//2 + dist * math.sin(angle))
                if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                    brightness = int(80 + 70 * math.sin(game_tick / 100 + i + dist / 50))
                    pygame.draw.circle(surf, (brightness, brightness // 2, 200), (x, y), 2)
        
        # 旋转的星体轨道（更华丽）
        for orbit_idx in range(3):
            orbit_speed = 120 - orbit_idx * 30
            orbit_radius = 80 + orbit_idx * 60
            orbit_angle = (game_tick / orbit_speed) * 2 * math.pi
            
            # 轨道线
            orbit_brightness = int(100 + 100 * math.sin(game_tick / 80 + orbit_idx))
            pygame.draw.circle(surf, (orbit_brightness, orbit_brightness // 2, 200), (WIDTH//2, HEIGHT//2), orbit_radius, 1)
            
            # 轨道上的星体
            for star_idx in range(6):
                star_angle = orbit_angle + star_idx * math.pi / 3
                sx = int(WIDTH//2 + orbit_radius * math.cos(star_angle))
                sy = int(HEIGHT//2 + orbit_radius * math.sin(star_angle))
                star_size = 4 + orbit_idx
                brightness = int(150 + 105 * math.sin(game_tick / 40 + star_idx))
                star_color = (brightness, brightness // 3, 230)
                pygame.draw.circle(surf, star_color, (sx, sy), star_size)
                # 星体光晕
                pygame.draw.circle(surf, (brightness // 2, 0, 180), (sx, sy), star_size + 3, 1)
        
        # 中央王冠星体（脉动）
        center_size = 20 + int(15 * math.sin(game_tick / 50))
        center_brightness = int(200 + 55 * math.sin(game_tick / 60))
        pygame.draw.circle(surf, (center_brightness, center_brightness // 2, 255), (WIDTH//2, HEIGHT//2), center_size)
        pygame.draw.circle(surf, (255, 150, 255), (WIDTH//2, HEIGHT//2), center_size - 8)
        
        # 星尘粒子（改进版 - 更多颜色）
        random.seed(game_tick // 80)
        for dust in range(50):  # 增加到50个
            dust_x = random.randint(0, WIDTH)
            dust_y = random.randint(0, HEIGHT)
            dust_bright = int(100 + 80 * math.sin(game_tick / 50 + dust * 0.3))
            # 多彩星尘
            if dust % 3 == 0:
                dust_color = (dust_bright, dust_bright // 2, 200)  # 蓝紫
            elif dust % 3 == 1:
                dust_color = (dust_bright // 2, dust_bright, 230)  # 青蓝
            else:
                dust_color = (dust_bright, dust_bright // 3, 255)  # 纯紫
            pygame.draw.circle(surf, dust_color, (dust_x, dust_y), 1)
    
    else:
        # 默认绘制网格
        draw_tactical_grid(surf)

def draw_warning_indicator():
    """绘制BOSS警告指示器（屏幕边框闪烁）"""
    # Use boss_manager warning state
    try:
        if not (boss_manager.pending or getattr(boss_manager, 'warning_timer', 0) > 0):
            return
    except Exception:
        # fallback: no boss warning manager, simply return
        return
    
    # 闪烁效果
    blink = (pygame.time.get_ticks() // 100) % 2 == 0
    if not blink:
        return
    
    # 上下左右边框
    border_width = 4
    border_color = CYBER_RED_ALERT
    
    pygame.draw.line(screen, border_color, (0, 0), (WIDTH, 0), border_width)  # 上
    pygame.draw.line(screen, border_color, (0, HEIGHT-border_width), (WIDTH, HEIGHT-border_width), border_width)  # 下
    pygame.draw.line(screen, border_color, (0, 0), (0, HEIGHT), border_width)  # 左
    pygame.draw.line(screen, border_color, (WIDTH-border_width, 0), (WIDTH-border_width, HEIGHT), border_width)  # 右

def draw_game_stats():
    """【新】绘制游戏内实时统计面板（右上角小面板）"""
    if player is None or not hasattr(player, 'stats'):
        return
    
    # 面板位置和大小 - 调整到得分/时间面板下方
    panel_w, panel_h = 170, 155
    panel_x = WIDTH - panel_w - 8
    panel_y = 135  # 在得分和时间面板下方（调整位置避免重叠）
    
    # 斜切角背景（与其他HUD风格统一）
    cut = 10
    bg_points = [
        (panel_x + cut, panel_y),
        (panel_x + panel_w, panel_y),
        (panel_x + panel_w, panel_y + panel_h - cut),
        (panel_x + panel_w - cut, panel_y + panel_h),
        (panel_x, panel_y + panel_h),
        (panel_x, panel_y + cut)
    ]
    
    # 渐变背景
    panel_surf = pygame.Surface((panel_w + 10, panel_h + 10), pygame.SRCALPHA)
    for i in range(panel_h):
        ratio = i / max(1, panel_h - 1)
        r = int(12 + 8 * ratio)
        g = int(18 + 12 * ratio)
        b = int(30 + 10 * ratio)
        pygame.draw.line(panel_surf, (r, g, b, 180), (0, i), (panel_w, i))
    
    # 裁剪为多边形
    mask = pygame.Surface((panel_w + 10, panel_h + 10), pygame.SRCALPHA)
    local_points = [(p[0] - panel_x, p[1] - panel_y) for p in bg_points]
    pygame.draw.polygon(mask, (255, 255, 255, 255), local_points)
    panel_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(panel_surf, (panel_x, panel_y))
    
    # 边框 - 青色
    pygame.draw.polygon(screen, (60, 180, 200), bg_points, 1)
    
    # 顶部装饰线
    pygame.draw.line(screen, (100, 220, 255), (panel_x + cut + 2, panel_y + 2), (panel_x + panel_w - 2, panel_y + 2), 1)
    
    # 角落装饰
    pygame.draw.line(screen, (80, 200, 220), (panel_x, panel_y + cut), (panel_x, panel_y + cut + 8), 2)
    pygame.draw.line(screen, (80, 200, 220), (panel_x + panel_w - cut, panel_y + panel_h), (panel_x + panel_w - cut - 8, panel_y + panel_h), 2)
    
    # 标题 - 带装饰（使用高质感渲染）
    title_x = panel_x + panel_w // 2
    from utils.ui import draw_premium_text
    draw_premium_text(screen, "战况统计", 12, title_x, panel_y + 4, (140, 240, 255), style="neon")
    
    # 分隔线 - 渐变效果
    for i in range(panel_w - 20):
        ratio = 1 - abs(i - (panel_w - 20) / 2) / ((panel_w - 20) / 2)
        alpha = int(150 * ratio)
        pygame.draw.line(screen, (60 + int(60 * ratio), 180 + int(40 * ratio), 220), (panel_x + 10 + i, panel_y + 21), (panel_x + 11 + i, panel_y + 21), 1)
    
    # 统计数据
    stats = player.stats
    y_offset = panel_y + 27
    line_height = 19
    label_x = panel_x + 10
    value_x = panel_x + panel_w - 10
    icon_x = label_x + 2
    text_x = label_x + 18
    
    # 绘制小图标的辅助函数
    def draw_stat_icon(cx, cy, icon_type, color):
        if icon_type == "skull":
            # 骷髅 - 简化为圆+十字
            pygame.draw.circle(screen, color, (cx, cy), 5)
            pygame.draw.circle(screen, (30, 30, 40), (cx - 2, cy - 1), 1)
            pygame.draw.circle(screen, (30, 30, 40), (cx + 2, cy - 1), 1)
        elif icon_type == "target":
            # 靶心
            pygame.draw.circle(screen, color, (cx, cy), 5, 1)
            pygame.draw.circle(screen, color, (cx, cy), 2)
        elif icon_type == "star":
            # 星星
            pts = []
            for i in range(5):
                angle = math.radians(-90 + i * 72)
                pts.append((cx + int(5 * math.cos(angle)), cy + int(5 * math.sin(angle))))
            pygame.draw.polygon(screen, color, pts)
        elif icon_type == "bolt":
            # 闪电
            pts = [(cx, cy - 5), (cx - 2, cy), (cx + 1, cy), (cx - 1, cy + 5), (cx + 3, cy - 1), (cx, cy - 1)]
            pygame.draw.polygon(screen, color, pts)
        elif icon_type == "flame":
            # 火焰
            pygame.draw.ellipse(screen, color, (cx - 3, cy - 4, 6, 8))
            pygame.draw.ellipse(screen, (255, 220, 100), (cx - 2, cy - 2, 4, 5))
        elif icon_type == "clock":
            # 时钟
            pygame.draw.circle(screen, color, (cx, cy), 5, 1)
            pygame.draw.line(screen, color, (cx, cy), (cx, cy - 3), 1)
            pygame.draw.line(screen, color, (cx, cy), (cx + 2, cy + 1), 1)
    
    # 击杀数
    kills = stats.get('kills', 0)
    draw_stat_icon(icon_x, y_offset + 6, "skull", (220, 80, 80))
    draw_premium_text(screen, "击杀", 10, text_x, y_offset, (200, 200, 210), align="left", style="cyber")
    kill_color = (255, 100, 100) if kills >= 50 else ((255, 200, 100) if kills >= 20 else (210, 210, 220))
    kill_style = "neon" if kills >= 50 else ("glow" if kills >= 20 else "cyber")
    draw_premium_text(screen, f"{kills}", 12, value_x, y_offset, kill_color, align="right", style=kill_style)
    y_offset += line_height

    # 命中率
    shots = stats.get('shots_fired', 0)
    hits = stats.get('hits', 0)
    accuracy = (hits / shots * 100) if shots > 0 else 0
    draw_stat_icon(icon_x, y_offset + 6, "target", (100, 220, 100))
    draw_premium_text(screen, "命中", 10, text_x, y_offset, (200, 200, 210), align="left", style="cyber")
    acc_color = (100, 255, 120) if accuracy >= 70 else ((255, 230, 80) if accuracy >= 40 else (160, 160, 170))
    acc_style = "neon" if accuracy >= 70 else ("glow" if accuracy >= 40 else "cyber")
    draw_premium_text(screen, f"{accuracy:.1f}%", 12, value_x, y_offset, acc_color, align="right", style=acc_style)
    y_offset += line_height
    
    # 暴击率
    crits = stats.get('crits', 0)
    crit_rate = (crits / hits * 100) if hits > 0 else 0
    draw_stat_icon(icon_x, y_offset + 6, "star", (255, 200, 80))
    draw_premium_text(screen, "暴击", 10, text_x, y_offset, (200, 200, 210), align="left", style="cyber")
    crit_color = (255, 100, 100) if crit_rate >= 30 else ((255, 180, 80) if crit_rate >= 15 else (160, 160, 170))
    crit_style = "neon" if crit_rate >= 30 else ("glow" if crit_rate >= 15 else "cyber")
    draw_premium_text(screen, f"{crit_rate:.1f}%", 12, value_x, y_offset, crit_color, align="right", style=crit_style)
    y_offset += line_height
    
    # 当前连击
    combo = stats.get('current_combo', 0)
    max_combo = stats.get('max_combo', 0)
    draw_stat_icon(icon_x, y_offset + 6, "bolt", (255, 230, 80))
    if combo > 0:
        draw_premium_text(screen, "连击", 10, text_x, y_offset, (200, 200, 210), align="left", style="cyber")
        combo_color = (255, 80 + min(175, int(combo * 10)), 80) if combo >= 10 else (255, 230, 80)
        combo_style = "neon" if combo >= 10 else "glow"
        draw_premium_text(screen, f"{combo}x", 12, value_x, y_offset, combo_color, align="right", style=combo_style)
    else:
        draw_premium_text(screen, "最高", 10, text_x, y_offset, (130, 130, 140), align="left", style="cyber")
        draw_premium_text(screen, f"{max_combo}x", 12, value_x, y_offset, (130, 130, 140), align="right", style="cyber")
    y_offset += line_height
    
    # DPS
    draw_stat_icon(icon_x, y_offset + 6, "flame", (255, 160, 50))
    draw_premium_text(screen, "DPS", 10, text_x, y_offset, (200, 200, 210), align="left", style="cyber")
    if stats.get('time_played', 0) > 0:
        time_sec = stats['time_played'] / 60
        dps = stats.get('damage_dealt', 0) / max(1, time_sec)
        dps_color = (255, 140, 50) if dps >= 1000 else ((255, 200, 100) if dps >= 500 else (190, 190, 200))
        dps_style = "neon" if dps >= 1000 else ("glow" if dps >= 500 else "cyber")
        draw_premium_text(screen, f"{int(dps)}", 12, value_x, y_offset, dps_color, align="right", style=dps_style)
    else:
        draw_premium_text(screen, "0", 12, value_x, y_offset, (130, 130, 140), align="right", style="cyber")
    y_offset += line_height
    
    # 存活时间
    time_sec = stats.get('time_played', 0) / 60
    minutes = int(time_sec // 60)
    seconds = int(time_sec % 60)
    draw_stat_icon(icon_x, y_offset + 6, "clock", (80, 210, 230))
    draw_premium_text(screen, "存活", 10, text_x, y_offset, (200, 200, 210), align="left", style="cyber")
    time_color = (100, 230, 255) if minutes >= 5 else ((150, 210, 230) if minutes >= 2 else (190, 190, 200))
    time_style = "neon" if minutes >= 5 else ("glow" if minutes >= 2 else "cyber")
    draw_premium_text(screen, f"{minutes:02d}:{seconds:02d}", 12, value_x, y_offset, time_color, align="right", style=time_style)

def draw_synergy_combo_hints():
    """【新】绘制协同combo提示"""
    global synergy_combo_hints
    
    for i, (text, timer, color) in enumerate(synergy_combo_hints[:3]):
        alpha = min(255, int(255 * (timer / 240.0)))
        y_pos = 250 + i * 40
        
        # 分离emoji和文字渲染
        emoji_font = pygame.font.SysFont("Segoe UI Emoji", 16)
        text_font = pygame.font.SysFont("SimHei", 16)
        
        # 检查是否以emoji开头
        if text.startswith("💫"):
            emoji_part = "💫"
            text_part = text[1:]  # 去掉emoji
            emoji_surf = emoji_font.render(emoji_part, True, color)
            text_surf = text_font.render(text_part, True, color)
            total_width = emoji_surf.get_width() + text_surf.get_width()
            total_height = max(emoji_surf.get_height(), text_surf.get_height())
            
            # 组合surface
            combined_surf = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
            combined_surf.blit(emoji_surf, (0, (total_height - emoji_surf.get_height()) // 2))
            combined_surf.blit(text_surf, (emoji_surf.get_width(), (total_height - text_surf.get_height()) // 2))
            text_surf = combined_surf
        else:
            text_surf = text_font.render(text, True, color)
        
        text_rect = text_surf.get_rect(center=(WIDTH // 2, y_pos))
        
        bg_rect = text_rect.inflate(30, 20)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (20, 30, 40, min(200, alpha)), (0, 0, bg_rect.width, bg_rect.height), border_radius=8)
        pygame.draw.rect(bg_surf, (*color, alpha), (0, 0, bg_rect.width, bg_rect.height), 2, border_radius=8)
        screen.blit(bg_surf, bg_rect.topleft)
        
        # 文字
        text_surf.set_alpha(alpha)
        screen.blit(text_surf, text_rect)
        
        # 更新计时器
        idx = synergy_combo_hints.index((text, timer, color))
        synergy_combo_hints[idx] = (text, timer - 1, color)
    
    # 移除过期提示
    synergy_combo_hints[:] = [(t, tm, c) for t, tm, c in synergy_combo_hints if tm > 0]

def draw_top_hud():
    """绘制四角布局HUD: 顶左(倾斜条+数值) + 顶右(积分/时间) + 底左(主炮/飞机/核心) + 底右(武器/大招) + 底部(经验条)"""
    if player is None:
        return
    
    from utils.ui import draw_premium_bar, draw_status_icon, draw_premium_ult_bar, draw_premium_weapon_slot, draw_wingman_indicator, draw_premium_text
    
    # ===== 顶部左侧：高级HUD面板 =====
    panel_x = 8
    panel_y = 6
    
    # 进度条参数
    bar_x = panel_x + 32
    bar_y = panel_y + 12
    bar_w = 180  # 缩短条宽度
    bar_h = 16
    bar_gap = 30
    
    # 获取动画帧
    anim_frame = pygame.time.get_ticks() // 16
    
    # === 护盾条 (青色) ===
    shield_max = player.max_shield if player.max_shield > 0 else player.max_hp
    shield_pct = (player.shield / max(1, shield_max) * 100) if shield_max > 0 else 0
    
    # 绘制护盾图标
    draw_status_icon(screen, panel_x + 8, bar_y - 2, 20, "shield", CYBER_CYAN_BRIGHT, anim_frame)
    
    # 绘制护盾条
    draw_premium_bar(screen, bar_x, bar_y, bar_w, bar_h, shield_pct, CYBER_CYAN_BRIGHT,
                     bg_color=(10, 35, 45), glow=True, animate_frame=anim_frame)
    
    # 护盾数值
    label_x = bar_x + bar_w + 20
    if player.shield > 0 or player.max_shield > 0:
        display_max = player.max_shield if player.max_shield > 0 else player.max_hp
        draw_text(screen, f"{int(player.shield)}/{int(display_max)}", 15, label_x, bar_y, WHITE, align='left', glow=False)
    else:
        draw_text(screen, "-- / --", 15, label_x, bar_y, (80, 80, 80), align='left')
    
    # === 血量条 (根据血量变色) ===
    hp_pct = (player.hp / player.max_hp * 100) if player.max_hp > 0 else 0
    if hp_pct < 25:
        hp_color = CYBER_RED_ALERT
        hp_pulse = True
    elif hp_pct < 50:
        hp_color = CYBER_AMBER
        hp_pulse = False
    else:
        hp_color = CYBER_LIME
        hp_pulse = False
    
    bar_y2 = bar_y + bar_gap
    
    # 绘制心形图标
    draw_status_icon(screen, panel_x + 8, bar_y2 - 2, 20, "heart", hp_color, anim_frame if hp_pulse else 0)
    
    # 绘制血量条（稍宽）
    hp_bar_w = bar_w + 20
    draw_premium_bar(screen, bar_x, bar_y2, hp_bar_w, int(bar_h * 1.3), hp_pct, hp_color,
                     bg_color=(40, 15, 15), glow=hp_pct < 50, animate_frame=anim_frame if hp_pulse else 0)
    
    # 血量数值
    hp_label_x = bar_x + hp_bar_w + 20
    draw_text(screen, f"{int(player.hp)}/{int(player.max_hp)}", 16, hp_label_x, bar_y2 + 1, WHITE, align='left', glow=hp_pulse)
    
    # === 推进器条 (紫色) ===
    thruster_pct = (player.dash_energy / player.max_dash_energy * 100) if player.max_dash_energy > 0 else 0
    bar_y3 = bar_y2 + bar_gap + 4
    
    # 绘制闪电图标
    draw_status_icon(screen, panel_x + 8, bar_y3 - 2, 20, "bolt", MAGENTA, anim_frame)
    
    # 绘制推进器条
    draw_premium_bar(screen, bar_x, bar_y3, bar_w, bar_h, thruster_pct, MAGENTA,
                     bg_color=(35, 15, 40), glow=thruster_pct > 80, animate_frame=anim_frame)
    
    # 推进器数值
    draw_text(screen, f"{int(player.dash_energy)}/{int(player.max_dash_energy)}", 15, label_x, bar_y3, WHITE, align='left')
    
    # ===== 特殊机体资源条 =====
    special_bar_y = bar_y3 + bar_gap
    
    # 【绯红之刃】鲜血狂热层数显示
    if hasattr(player, 'plane_id') and player.plane_id == "crimson":
        stacks = getattr(player, 'blood_stacks', 0)
        if stacks > 0:
            max_stacks = max(1, getattr(player, 'max_blood_stacks', 25))
            stack_ratio = stacks / max_stacks
            bar_pct = stack_ratio * 100
            blood_color = (int(150 + 80 * stack_ratio), int(40 + 120 * stack_ratio), int(60 + 80 * stack_ratio))
            draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "skull", blood_color, anim_frame)
            draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, blood_color,
                             bg_color=(40, 10, 20), glow=stack_ratio > 0.5, animate_frame=anim_frame)
            lifesteal_pct = int((0.04 + 0.12 * stack_ratio) * 100)
            draw_text(screen, f"{stacks}/{max_stacks} (吸血{lifesteal_pct}%)", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【绯红恶魔·SCARLET】鲜血层数 + 潜行状态显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "scarlet":
        blood_stacks = getattr(player, 'scarlet_blood_stacks', 0)
        max_blood = max(1, getattr(player, 'scarlet_max_blood', 10))
        is_stealth = getattr(player, 'scarlet_stealth_mode', False)
        blood_ratio = blood_stacks / max_blood
        bar_pct = blood_ratio * 100
        
        # 颜色根据状态变化
        if is_stealth:
            flash = abs(math.sin(pygame.time.get_ticks() / 80))
            scarlet_color = (int(180 + 75 * flash), int(20 + 30 * flash), int(60 + 40 * flash))
        else:
            scarlet_color = (int(180 + 40 * blood_ratio), int(20 + 60 * blood_ratio), int(60 + 60 * blood_ratio)) if blood_stacks > 0 else (150, 30, 50)
        
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "skull", scarlet_color, anim_frame)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, scarlet_color,
                         bg_color=(50, 10, 20), glow=is_stealth, animate_frame=anim_frame)
        
        lifesteal_pct = int(blood_ratio * 15)
        dmg_bonus = int(blood_ratio * 30)
        
        if is_stealth:
            draw_text(screen, f"潜行中! 暴击待发", 15, label_x, special_bar_y, (255, 150, 180), glow=True, align='left')
        else:
            draw_text(screen, f"{int(blood_stacks)}/{max_blood} (吸血{lifesteal_pct}%)", 15, label_x, special_bar_y, WHITE, align='left')
        
        # 【深红世界】第四大招显示
        ult4_bar_y = special_bar_y + bar_gap
        ult4_charge = getattr(player, 'ult4_charge', 0)
        max_ult4 = getattr(player, 'max_ult4_charge', 100)
        ult4_cd = getattr(player, 'ult4_cooldown', 0)
        ult4_ratio = ult4_charge / max_ult4 if max_ult4 > 0 else 0
        ult4_ready = ult4_ratio >= 1.0 and ult4_cd <= 0
        ult4_pct = ult4_ratio * 100
        
        if ult4_ready:
            ult4_color = (255, 80, 120)
            ult4_text = "[R] 深红世界 就绪!"
        elif ult4_cd > 0:
            ult4_color = (100, 40, 50)
            ult4_text = f"[R] CD {ult4_cd / 60.0:.1f}s"
        else:
            ult4_color = (int(150 + 105 * ult4_ratio), int(30 + 50 * ult4_ratio), int(50 + 80 * ult4_ratio))
            ult4_text = f"[R] 深红世界 {int(ult4_pct)}%"
        
        draw_status_icon(screen, panel_x + 8, ult4_bar_y - 2, 20, "flame", ult4_color, anim_frame if ult4_ready else 0)
        draw_premium_bar(screen, bar_x, ult4_bar_y, bar_w, int(bar_h * 0.8), ult4_pct, ult4_color,
                         bg_color=(40, 10, 20), glow=ult4_ready, animate_frame=anim_frame if ult4_ready else 0)
        draw_text(screen, ult4_text, 14, label_x, ult4_bar_y, ult4_color if ult4_ready else WHITE, glow=ult4_ready, align='left')
    
    # 【星界潜行者】暗影标记数显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "stalker":
        marks = getattr(player, 'shadow_marks', 0)
        max_marks = max(1, getattr(player, 'max_shadow_marks', 8))
        mark_ratio = marks / max_marks if marks > 0 else 0
        bar_pct = mark_ratio * 100
        mark_color = (int(75 + 50 * mark_ratio), int(0 + 80 * mark_ratio), int(130 + 80 * mark_ratio)) if marks > 0 else (60, 40, 100)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "star", mark_color, anim_frame)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, mark_color,
                         bg_color=(20, 10, 40), glow=mark_ratio > 0.7, animate_frame=anim_frame)
        dmg_bonus_pct = int(marks * 4)
        draw_text(screen, f"{marks}/{max_marks} (伤害+{dmg_bonus_pct}%)", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【大地守护者】大地怒气显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "gaia":
        fury = getattr(player, 'earth_fury', 0)
        max_fury = max(1, getattr(player, 'max_earth_fury', 100))
        fury_ratio = fury / max_fury if fury > 0 else 0
        bar_pct = fury_ratio * 100
        fury_color = (int(60 + 100 * fury_ratio), int(140 + 80 * fury_ratio), int(40 + 60 * fury_ratio)) if fury > 0 else (50, 100, 40)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "flame", fury_color, anim_frame)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, fury_color,
                         bg_color=(20, 35, 15), glow=fury_ratio > 0.8, animate_frame=anim_frame)
        armor_pct = int(fury_ratio * 50)
        dmg_pct = int(fury_ratio * 80)
        draw_text(screen, f"{int(fury)} (护{armor_pct}%/伤{dmg_pct}%)", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【钢铁泰坦】过载能量 + 装甲显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "titan":
        overload = getattr(player, 'titan_overload', 0)
        armor_stacks = getattr(player, 'titan_armor_stacks', 0)
        max_overload = max(1, getattr(player, 'max_titan_overload', 100))
        overload_ratio = overload / max_overload if overload > 0 else 0
        bar_pct = overload_ratio * 100
        overload_color = (int(200 + 55 * overload_ratio), int(120 - 60 * overload_ratio), int(50 - 50 * overload_ratio)) if overload > 0 else (150, 100, 50)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "bolt", overload_color, anim_frame)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, overload_color,
                         bg_color=(40, 20, 10), glow=overload_ratio > 0.9, animate_frame=anim_frame)
        armor_reduction = int(armor_stacks * 8)
        status = "★就绪!" if overload >= 100 else f"{int(overload)}%"
        draw_text(screen, f"{status} (装甲{armor_stacks}层)", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【虚空编织者】维度织网显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "weaver":
        webbed = getattr(player, 'weaver_webbed_count', 0)
        bar_pct = min(100, webbed * 12.5)
        web_color = (int(140 + 40 * (webbed/8)), int(140 + 40 * (webbed/8)), int(140 + 40 * (webbed/8))) if webbed > 0 else (100, 100, 100)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "star", web_color, anim_frame)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, web_color,
                         bg_color=(30, 30, 35), glow=webbed > 4, animate_frame=anim_frame)
        dmg_bonus = int(webbed * 6)
        draw_text(screen, f"{webbed}网 (+{dmg_bonus}%伤)", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【日冕耀斑】灼热核心显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "solar":
        heat = getattr(player, 'solar_heat', 0)
        is_overheat = getattr(player, 'solar_overheat', False)
        max_heat = max(1, getattr(player, 'max_solar_heat', 100))
        heat_ratio = heat / max_heat if heat > 0 else 0
        bar_pct = heat_ratio * 100
        if is_overheat:
            flash = abs(math.sin(pygame.time.get_ticks() / 100)) 
            heat_color = (int(200 + 55 * flash), int(50 * flash), 0)
        elif heat > 0:
            heat_color = (int(200 + 55 * heat_ratio), int(150 - 100 * heat_ratio), int(50 - 50 * heat_ratio))
        else:
            heat_color = (180, 120, 50)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "flame", heat_color, anim_frame if is_overheat else 0)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, heat_color,
                         bg_color=(40, 20, 10), glow=is_overheat or heat_ratio > 0.8, animate_frame=anim_frame)
        dmg_bonus = int(heat_ratio * 60)
        if is_overheat:
            cooldown = getattr(player, 'solar_overheat_timer', 0)
            draw_text(screen, f"过热! 冷却中...", 15, label_x, special_bar_y, (255, 100, 50), glow=True, align='left')
        else:
            draw_text(screen, f"{int(heat)}% (+{dmg_bonus}%伤)", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【量子裁决者】量子叠加态显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "arbiter":
        quantum = getattr(player, 'arbiter_quantum', 0)
        is_ready = getattr(player, 'arbiter_collapse_ready', False)
        max_quantum = max(1, getattr(player, 'max_arbiter_quantum', 100))
        bar_pct = (quantum / max_quantum) * 100 if not is_ready else 100
        if is_ready:
            flash = abs(math.sin(pygame.time.get_ticks() / 80))
            quantum_color = (int(150 + 105 * flash), int(50 + 50 * flash), int(200 + 55 * flash))
        elif quantum > 0:
            quantum_color = (int(120 + 80 * (quantum/max_quantum)), 50, int(180 + 75 * (quantum/max_quantum)))
        else:
            quantum_color = (100, 50, 150)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "star", quantum_color, anim_frame if is_ready else 0)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, quantum_color,
                         bg_color=(30, 15, 40), glow=is_ready, animate_frame=anim_frame if is_ready else 0)
        if is_ready:
            draw_text(screen, "坍缩就绪!", 15, label_x, special_bar_y, (255, 150, 255), glow=True, align='left')
        else:
            draw_text(screen, f"量子态 {int(quantum)}%", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【日食幽灵】光暗交替显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "eclipse":
        phase = getattr(player, 'eclipse_phase', 'light')
        timer = getattr(player, 'eclipse_phase_timer', 0)
        shield = getattr(player, 'eclipse_shield', 0)
        phase_progress = timer / 300 * 100
        if phase == "light":
            light_bonus = int(getattr(player, 'eclipse_light_bonus', 0) * 100)
            phase_color = (255, 220, 100)
            draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "star", phase_color, anim_frame)
            draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, phase_progress, phase_color,
                             bg_color=(40, 35, 15), glow=True, animate_frame=anim_frame)
            draw_text(screen, f"光态 +{light_bonus}%伤", 15, label_x, special_bar_y, phase_color, glow=True, align='left')
        else:
            max_shield = getattr(player, 'max_eclipse_shield', 50)
            shield_pct = (shield / max_shield) * 100 if max_shield > 0 else 0
            phase_color = (100, 50, 180)
            draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "shield", phase_color, anim_frame)
            draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, shield_pct, phase_color,
                             bg_color=(20, 15, 35), glow=True, animate_frame=anim_frame)
            draw_text(screen, f"暗态 护盾:{int(shield)}", 15, label_x, special_bar_y, phase_color, glow=True, align='left')
    
    # 【棱镜分光】折射风暴显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "prism":
        chain = getattr(player, 'prism_chain_count', 0)
        max_chain = getattr(player, 'prism_max_chain', 0)
        bar_pct = (chain / 5) * 100
        colors = [(100, 180, 255), (140, 140, 255), (180, 100, 255), (255, 100, 180), (255, 180, 100)]
        prism_color = colors[min(chain, len(colors)-1)] if chain > 0 else (80, 120, 160)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "star", prism_color, anim_frame)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, prism_color,
                         bg_color=(25, 30, 40), glow=chain > 3, animate_frame=anim_frame)
        dmg_bonus = int(chain * 15)
        draw_text(screen, f"折射x{chain} (+{dmg_bonus}%)", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【死灵骑士】亡灵军团显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "necro":
        ghosts = getattr(player, 'necro_ghosts', [])
        ghost_count = len(ghosts)
        max_ghosts = getattr(player, 'max_necro_ghosts', 6)
        total_damage = int(getattr(player, 'necro_ghost_damage', 0))
        bar_pct = (ghost_count / max_ghosts) * 100
        necro_color = (int(150 + 50 * (ghost_count / max_ghosts)), 50, int(100 + 55 * (ghost_count / max_ghosts))) if ghost_count > 0 else (120, 50, 80)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "skull", necro_color, anim_frame)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, necro_color,
                         bg_color=(30, 15, 25), glow=ghost_count > 3, animate_frame=anim_frame)
        draw_text(screen, f"{ghost_count}/{max_ghosts} 伤害:{total_damage}", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【霓虹突击者】超载引擎显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "striker":
        charge = getattr(player, 'striker_charge', 0)
        max_charge = max(1, getattr(player, 'max_striker_charge', 100))
        is_overdrive = getattr(player, 'striker_overdrive', False)
        bar_pct = (charge / max_charge) * 100
        if is_overdrive:
            flash = abs(math.sin(pygame.time.get_ticks() / 80))
            striker_color = (int(100 + 155 * flash), int(200 + 55 * flash), int(200 + 55 * flash))
        else:
            striker_color = (int(80 + 120 * (charge/max_charge)), int(180 + 75 * (charge/max_charge)), 220) if charge > 0 else (60, 150, 180)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "bolt", striker_color, anim_frame if is_overdrive else 0)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, striker_color,
                       bg_color=(20, 40, 50), glow=is_overdrive, animate_frame=anim_frame if is_overdrive else 0)
        if is_overdrive:
            timer = getattr(player, 'striker_overdrive_timer', 0)
            draw_text(screen, f"超载激活! ({timer//60}s)", 15, label_x, special_bar_y, (100, 255, 255), glow=True, align='left')
        else:
            draw_text(screen, f"超载 {int(charge)}%", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【虚空幻影】相位漂移显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "phantom":
        phase = getattr(player, 'phantom_phase', 0)
        max_phase = max(1, getattr(player, 'max_phantom_phase', 100))
        is_intangible = getattr(player, 'phantom_intangible', False)
        bar_pct = (phase / max_phase) * 100
        if is_intangible:
            flash = abs(math.sin(pygame.time.get_ticks() / 60))
            phantom_color = (int(200 + 55 * flash), int(100 + 100 * flash), 255)
        elif phase >= 50:
            phantom_color = (180, 80, 255)
        else:
            phantom_color = (int(120 + 60 * (phase/max_phase)), int(50 + 30 * (phase/max_phase)), int(180 + 75 * (phase/max_phase))) if phase > 0 else (100, 50, 150)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "star", phantom_color, anim_frame if is_intangible else 0)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, phantom_color,
                       bg_color=(30, 15, 45), glow=is_intangible, animate_frame=anim_frame if is_intangible else 0)
        if is_intangible:
            draw_text(screen, f"相位无敌中!", 15, label_x, special_bar_y, (255, 150, 255), glow=True, align='left')
        else:
            status = "可激活!" if phase >= 50 else f"{int(phase)}%"
            draw_text(screen, f"相位 {status}", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【雷霆战鹰】雷暴连锁显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "thunderbird":
        charge = getattr(player, 'thunder_charge', 0)
        max_charge = max(1, getattr(player, 'max_thunder_charge', 100))
        bar_pct = (charge / max_charge) * 100
        is_ready = charge >= max_charge
        if is_ready:
            flash = abs(math.sin(pygame.time.get_ticks() / 80))
            thunder_color = (int(200 + 55 * flash), int(200 + 55 * flash), int(100 * flash))
        else:
            thunder_color = (int(200 + 55 * (charge/max_charge)), int(200 + 55 * (charge/max_charge)), 50) if charge > 0 else (180, 180, 50)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "bolt", thunder_color, anim_frame if is_ready else 0)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, thunder_color,
                       bg_color=(35, 35, 15), glow=is_ready, animate_frame=anim_frame if is_ready else 0)
        if is_ready:
            draw_text(screen, "雷暴就绪!", 15, label_x, special_bar_y, (255, 255, 100), glow=True, align='left')
        else:
            draw_text(screen, f"电荷 {int(charge)}%", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【剧毒蝰蛇】剧毒累积显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "viper":
        poison = getattr(player, 'viper_total_poison', 0)
        bar_pct = min(100, poison * 5)
        if poison >= 15:
            venom_color = (80, 255, 80)
        else:
            venom_color = (int(100 + 80 * (poison/20)), int(200 + 55 * (poison/20)), int(100 + 80 * (poison/20))) if poison > 0 else (80, 180, 80)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "skull", venom_color, anim_frame)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, venom_color,
                       bg_color=(20, 40, 20), glow=poison >= 15, animate_frame=anim_frame)
        draw_text(screen, f"毒素 {poison}层", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【幽灵收割者】死神印记显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "specter":
        focus_time = getattr(player, 'specter_focus_time', 0)
        stealth = getattr(player, 'specter_stealth', 0)
        has_target = getattr(player, 'specter_focus', None) is not None
        bar_pct = (focus_time / 180) * 100 if has_target else 0
        if stealth > 0:
            flash = abs(math.sin(pygame.time.get_ticks() / 80))
            specter_color = (int(100 + 100 * flash), int(50 + 50 * flash), int(200 + 55 * flash))
        elif focus_time > 120:
            specter_color = (200, 100, 255)
        else:
            specter_color = (int(100 + 60 * (focus_time/180)), int(50 + 30 * (focus_time/180)), int(180 + 75 * (focus_time/180))) if focus_time > 0 else (100, 50, 160)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "star", specter_color, anim_frame if stealth > 0 else 0)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, specter_color,
                       bg_color=(30, 20, 50), glow=stealth > 0, animate_frame=anim_frame if stealth > 0 else 0)
        if stealth > 0:
            draw_text(screen, f"隐身中!", 15, label_x, special_bar_y, (200, 150, 255), glow=True, align='left')
        else:
            dmg_mult = int((1.0 + (focus_time / 180) * 1.0) * 100) if has_target else 100
            draw_text(screen, f"印记 {dmg_mult}%伤", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【极光女神】极光共鸣显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "aurora":
        orbs = getattr(player, 'aurora_orbs', [])
        orb_count = len(orbs)
        max_orbs = getattr(player, 'max_aurora_orbs', 5)
        bar_pct = (orb_count / max_orbs) * 100
        if orb_count >= max_orbs:
            flash = abs(math.sin(pygame.time.get_ticks() / 120))
            aurora_color = (int(100 * flash), int(200 + 55 * flash), int(180 + 75 * flash))
        else:
            aurora_color = (int(80 * (orb_count/max_orbs)), int(180 + 75 * (orb_count/max_orbs)), int(160 + 95 * (orb_count/max_orbs))) if orb_count > 0 else (60, 160, 140)
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "star", aurora_color, anim_frame)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, aurora_color,
                       bg_color=(20, 40, 35), glow=orb_count >= max_orbs, animate_frame=anim_frame)
        draw_text(screen, f"极光 {orb_count}/{max_orbs}球", 15, label_x, special_bar_y, WHITE, align='left')
    
    # 【混沌虫洞】裂缝能量显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "wormhole":
        rift_energy = getattr(player, 'rift_energy', 0)
        max_rift = getattr(player, 'max_rift_energy', 100)
        portals = getattr(player, 'rift_portals', [])
        portal_count = len(portals)
        bar_pct = (rift_energy / max_rift) * 100
        
        if rift_energy >= 90:
            flash = abs(math.sin(pygame.time.get_ticks() / 60))
            rift_color = (int(200 + 55 * flash), int(50 * flash), int(200 + 55 * flash))
        elif rift_energy >= 70:
            rift_color = (220, 80, 255)
        else:
            rift_color = (int(120 + 100 * (rift_energy/max_rift)), int(30 + 50 * (rift_energy/max_rift)), int(150 + 105 * (rift_energy/max_rift))) if rift_energy > 0 else (100, 30, 120)
        
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "star", rift_color, anim_frame if rift_energy >= 90 else 0)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, rift_color,
                       bg_color=(30, 10, 40), glow=rift_energy >= 70, animate_frame=anim_frame if rift_energy >= 90 else 0)
        
        if rift_energy >= 90:
            status_text = f"裂缝波动就绪!"
        elif portal_count > 0:
            status_text = f"{int(rift_energy)}% 门:{portal_count}"
        else:
            status_text = f"裂缝 {int(rift_energy)}%"
        
        draw_text(screen, status_text, 15, label_x, special_bar_y, rift_color if rift_energy >= 90 else WHITE, glow=rift_energy >= 90, align='left')
    
    # 【时之回响·克洛诺斯】时间回溯显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "chronos":
        time_charge = getattr(player, 'chronos_charge', 0)
        max_time = getattr(player, 'max_chronos_charge', 100)
        echo_stacks = getattr(player, 'chronos_echo_stacks', 0)
        is_rewinding = getattr(player, 'chronos_rewinding', False)
        bar_pct = (time_charge / max_time) * 100
        
        if is_rewinding:
            flash = abs(math.sin(pygame.time.get_ticks() / 50))
            chronos_color = (int(100 + 155 * flash), int(220 * flash), int(255 * flash))
        elif time_charge >= 80:
            flash = abs(math.sin(pygame.time.get_ticks() / 100))
            chronos_color = (int(100 + 50 * flash), int(220 + 35 * flash), 255)
        elif time_charge >= 50:
            chronos_color = (80, 200, 255)
        else:
            chronos_color = (int(60 + 40 * (time_charge/max_time)), int(180 + 40 * (time_charge/max_time)), int(230 + 25 * (time_charge/max_time))) if time_charge > 0 else (60, 180, 230)
        
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "star", chronos_color, anim_frame if is_rewinding else 0)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, chronos_color,
                       bg_color=(20, 40, 60), glow=is_rewinding or time_charge >= 80, animate_frame=anim_frame if is_rewinding else 0)
        
        if is_rewinding:
            status_text = f"时间回溯中!"
        elif time_charge >= 80:
            status_text = f"回溯就绪!"
        elif echo_stacks > 0:
            status_text = f"时流{int(time_charge)}% 回响x{echo_stacks}"
        else:
            status_text = f"时流 {int(time_charge)}%"
        
        draw_text(screen, status_text, 15, label_x, special_bar_y, chronos_color if is_rewinding or time_charge >= 80 else WHITE, glow=is_rewinding, align='left')
    
    # 【辉耀天女·斯塔德】皇辉层数显示 - 被动伤害加成
    if hasattr(player, 'plane_id') and player.plane_id == "staradia":
        radiant_stacks = getattr(player, 'radiant_stacks', 0)
        max_stacks = 5
        domain_active = getattr(player, 'radiant_domain_active', False)
        remnants = getattr(player, 'remnant_count', 0)
        bar_pct = (radiant_stacks / max_stacks) * 100
        
        t = pygame.time.get_ticks() / 1000
        if domain_active:
            flash = abs(math.sin(pygame.time.get_ticks() / 50))
            hue_shift = (pygame.time.get_ticks() / 20) % 360
            r = int(200 + 55 * abs(math.sin(math.radians(hue_shift))))
            g = int(180 + 75 * abs(math.sin(math.radians(hue_shift + 120))))
            b = int(150 + 105 * abs(math.sin(math.radians(hue_shift + 240))))
            radiant_color = (min(255, r), min(255, g), min(255, b))
        elif radiant_stacks >= 5:
            flash = abs(math.sin(pygame.time.get_ticks() / 80))
            radiant_color = (int(255), int(200 + 55 * flash), int(100 * flash))
        elif radiant_stacks >= 3:
            radiant_color = (255, int(180 + 40 * (radiant_stacks/max_stacks)), int(80 + 40 * (radiant_stacks/max_stacks)))
        else:
            radiant_color = (int(180 + 75 * (radiant_stacks/max_stacks)), int(150 + 50 * (radiant_stacks/max_stacks)), int(80 + 40 * (radiant_stacks/max_stacks))) if radiant_stacks > 0 else (160, 130, 70)
        
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "star", radiant_color, anim_frame if domain_active else 0)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, radiant_color,
                       bg_color=(40, 30, 15), glow=domain_active or radiant_stacks >= 5, animate_frame=anim_frame if domain_active else 0)
        
        if domain_active:
            status_text = "★领域激活★"
        else:
            buff_pct = int(radiant_stacks * 10)
            status_text = f"皇辉{radiant_stacks}/{max_stacks} (+{buff_pct}%)"
            if remnants > 0:
                status_text += f" 残影:{remnants}"
        
        draw_text(screen, status_text, 15, label_x, special_bar_y, radiant_color if domain_active else WHITE, glow=domain_active, align='left')
    
    # 【深渊龙鱼·猪公爵】龙卷/深渊泡状态显示
    if hasattr(player, 'plane_id') and player.plane_id == "dukefishron":
        active_tornados = len(getattr(player, 'active_tornados', []))
        refract_ready = getattr(player, 'duke_refract_ready', False)
        tsunami_active = getattr(player, 'duke_tsunami_active', False)
        
        max_tornados = 5
        bar_pct = (min(active_tornados, max_tornados) / max_tornados) * 100
        
        if tsunami_active:
            flash = abs(math.sin(pygame.time.get_ticks() / 50))
            duke_color = (int(80 + 175 * flash), int(150 + 105 * flash), int(200 + 55 * flash))
        elif active_tornados >= 3:
            duke_color = (30, 100, 220)
        else:
            duke_color = (30, 80, 180)
        
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "flame", (255, 120, 180), anim_frame if tsunami_active else 0)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, duke_color,
                       bg_color=(10, 20, 40), glow=tsunami_active, animate_frame=anim_frame if tsunami_active else 0)
        
        if tsunami_active:
            status_text = "★海啸滑翔★"
        else:
            status_text = f"龙卷x{active_tornados}"
            if refract_ready:
                status_text += " 🫧"
        
        draw_text(screen, status_text, 15, label_x, special_bar_y, (255, 120, 180) if tsunami_active else WHITE, glow=tsunami_active, align='left')
    
    # 【分形天顶·ZENITH】剑阵状态显示
    if hasattr(player, 'plane_id') and player.plane_id == "zenith":
        sword_array = getattr(player, 'zenith_sword_array', None)
        shield = getattr(player, 'zenith_shield', None)
        
        available_swords = 12
        if sword_array:
            available_swords = sword_array.get_available_count() if hasattr(sword_array, 'get_available_count') else 12
        
        shield_durability = 100
        max_durability = 100
        if shield:
            shield_durability = getattr(shield, 'durability', 100)
            max_durability = getattr(shield, 'max_durability', 100)
        
        shield_ratio = shield_durability / max_durability if max_durability > 0 else 1.0
        bar_pct = (available_swords / 12) * 100
        
        hue_shift = (pygame.time.get_ticks() / 15) % 360
        if available_swords >= 10:
            r = int(120 + 135 * abs(math.sin(math.radians(hue_shift))))
            g = int(100 + 155 * abs(math.sin(math.radians(hue_shift + 120))))
            b = int(180 + 75 * abs(math.sin(math.radians(hue_shift + 240))))
            zenith_color = (min(255, r), min(255, g), min(255, b))
        elif available_swords >= 6:
            zenith_color = (150, 80, 220)
        else:
            sword_ratio = available_swords / 12
            zenith_color = (int(80 + 70 * sword_ratio), int(40 + 40 * sword_ratio), int(130 + 90 * sword_ratio))
        
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "star", zenith_color, anim_frame)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, zenith_color,
                       bg_color=(20, 10, 35), glow=available_swords >= 10, animate_frame=anim_frame)
        
        shield_pct = int(shield_ratio * 100)
        status_text = f"{available_swords}/12剑 护盾{shield_pct}%"
        
        draw_text(screen, status_text, 15, label_x, special_bar_y, zenith_color if available_swords >= 10 else WHITE, glow=available_swords >= 10, align='left')
        
        # 【棱镜折射】第四大招显示
        ult4_bar_y = special_bar_y + bar_gap
        ult4_charge = getattr(player, 'ult4_charge', 0)
        max_ult4 = getattr(player, 'max_ult4_charge', 100)
        ult4_cd = getattr(player, 'ult4_cooldown', 0)
        ult4_ratio = ult4_charge / max_ult4 if max_ult4 > 0 else 0
        ult4_ready = ult4_ratio >= 1.0 and ult4_cd <= 0
        ult4_pct = ult4_ratio * 100
        
        if ult4_ready:
            ult4_color = (200, 100, 255)
            ult4_text = "[R] 棱镜折射 就绪!"
        elif ult4_cd > 0:
            ult4_color = (60, 40, 80)
            ult4_text = f"[R] CD {ult4_cd / 60.0:.1f}s"
        else:
            ult4_color = (int(100 + 100 * ult4_ratio), int(50 * ult4_ratio), int(150 + 105 * ult4_ratio))
            ult4_text = f"[R] 棱镜折射 {int(ult4_pct)}%"
        
        draw_status_icon(screen, panel_x + 8, ult4_bar_y - 2, 20, "star", ult4_color, anim_frame if ult4_ready else 0)
        draw_premium_bar(screen, bar_x, ult4_bar_y, bar_w, int(bar_h * 0.8), ult4_pct, ult4_color,
                         bg_color=(20, 10, 35), glow=ult4_ready, animate_frame=anim_frame if ult4_ready else 0)
        draw_text(screen, ult4_text, 14, label_x, ult4_bar_y, ult4_color if ult4_ready else WHITE, glow=ult4_ready, align='left')
    
    # 【光之在解·VISCERATOR】光子火花显示 - 被动累积系统
    if hasattr(player, 'plane_id') and player.plane_id == "viscerator":
        spark_manager = getattr(player, 'viscerator_spark_manager', None)
        
        # 计算所有敌人身上的火花总数
        total_sparks = 0
        max_spark_enemy = None
        max_sparks = 0
        
        if spark_manager:
            for eid, count in spark_manager.sparks.items():
                total_sparks += count
                if count > max_sparks:
                    max_sparks = count
        
        spark_threshold = 8
        bar_pct = (max_sparks / spark_threshold) * 100 if max_sparks > 0 else 0
        
        # 颜色基于最大火花数
        if max_sparks >= 6:
            flash = abs(math.sin(pygame.time.get_ticks() / 80))
            # 粉色和绿色交替闪烁
            if int(pygame.time.get_ticks() / 200) % 2 == 0:
                spark_color = (int(255), int(20 + 127 * flash), int(147 + 50 * flash))  # 深粉
            else:
                spark_color = (int(127 + 80 * flash), int(255), int(0))  # 黄绿
        elif max_sparks >= 3:
            ratio = max_sparks / spark_threshold
            spark_color = (int(200 + 55 * ratio), int(80 + 100 * ratio), int(120 + 80 * ratio))
        else:
            spark_color = (180, 100, 130) if max_sparks > 0 else (100, 60, 80)
        
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "bolt", spark_color, anim_frame if max_sparks >= 6 else 0)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, spark_color,
                       bg_color=(30, 15, 25), glow=max_sparks >= 6, animate_frame=anim_frame if max_sparks >= 6 else 0)
        
        if max_sparks >= 6:
            status_text = f"光子临界! {max_sparks}/{spark_threshold}"
        elif total_sparks > 0:
            status_text = f"火花 {max_sparks}/{spark_threshold} 总计:{total_sparks}"
        else:
            status_text = "光子火花待累积"
        
        draw_text(screen, status_text, 15, label_x, special_bar_y, spark_color if max_sparks >= 6 else WHITE, glow=max_sparks >= 6, align='left')
        
        # 【毁灭之光】第四大招显示
        ult4_bar_y = special_bar_y + bar_gap
        ult4_charge = getattr(player, 'ult4_charge', 0)
        max_ult4 = getattr(player, 'max_ult4_charge', 100)
        ult4_cd = getattr(player, 'ult4_cooldown', 0)
        ult4_ratio = ult4_charge / max_ult4 if max_ult4 > 0 else 0
        ult4_ready = ult4_ratio >= 1.0 and ult4_cd <= 0
        ult4_pct = ult4_ratio * 100
        
        if ult4_ready:
            flash = abs(math.sin(pygame.time.get_ticks() / 80))
            ult4_color = (int(255), int(20 + 100 * flash), int(147 + 50 * flash))
            ult4_text = "[R] 毁灭之光 就绪!"
        elif ult4_cd > 0:
            ult4_color = (80, 40, 60)
            ult4_text = f"[R] CD {ult4_cd / 60.0:.1f}s"
        else:
            ult4_color = (int(180 + 75 * ult4_ratio), int(20 + 80 * ult4_ratio), int(100 + 47 * ult4_ratio))
            ult4_text = f"[R] 毁灭之光 {int(ult4_pct)}%"
        
        draw_status_icon(screen, panel_x + 8, ult4_bar_y - 2, 20, "flame", ult4_color, anim_frame if ult4_ready else 0)
        draw_premium_bar(screen, bar_x, ult4_bar_y, bar_w, int(bar_h * 0.8), ult4_pct, ult4_color,
                         bg_color=(30, 10, 20), glow=ult4_ready, animate_frame=anim_frame if ult4_ready else 0)
        draw_text(screen, ult4_text, 14, label_x, ult4_bar_y, ult4_color if ult4_ready else WHITE, glow=ult4_ready, align='left')
    
    # 【晶体粉碎者·CRUSHER】撞击护甲显示 - 被动减伤 + R技能
    if hasattr(player, 'plane_id') and player.plane_id == "crusher":
        armor_stacks = getattr(player, 'crusher_armor_stacks', 0)
        max_armor = getattr(player, 'crusher_max_armor', 20)
        
        armor_ratio = armor_stacks / max_armor if max_armor > 0 else 0
        bar_pct = armor_ratio * 100
        
        # 颜色基于护甲层数（紫色系）
        if armor_stacks >= 15:
            flash = abs(math.sin(pygame.time.get_ticks() / 80))
            crusher_color = (int(138 + 80 * flash), int(43 + 60 * flash), int(226 + 29 * flash))
        elif armor_stacks >= 8:
            crusher_color = (int(120 + 40 * armor_ratio), int(30 + 30 * armor_ratio), int(200 + 56 * armor_ratio))
        else:
            crusher_color = (int(100 + 38 * armor_ratio), int(20 + 23 * armor_ratio), int(180 + 46 * armor_ratio)) if armor_stacks > 0 else (80, 20, 140)
        
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "shield", crusher_color, anim_frame if armor_stacks >= 15 else 0)
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, bar_pct, crusher_color,
                       bg_color=(25, 10, 40), glow=armor_stacks >= 15, animate_frame=anim_frame if armor_stacks >= 15 else 0)
        
        reduction_pct = int(armor_stacks * 2)
        if armor_stacks >= 15:
            status_text = f"晶甲满载! {armor_stacks}/{max_armor} (-{reduction_pct}%)"
        elif armor_stacks > 0:
            status_text = f"晶甲 {armor_stacks}/{max_armor} (减伤{reduction_pct}%)"
        else:
            status_text = "晶体护甲待激活"
        
        draw_text(screen, status_text, 15, label_x, special_bar_y, crusher_color if armor_stacks >= 15 else WHITE, glow=armor_stacks >= 15, align='left')
        
        # 【核心过载】第四大招显示
        ult4_bar_y = special_bar_y + bar_gap
        ult4_charge = getattr(player, 'ult4_charge', 0)
        max_ult4 = getattr(player, 'max_ult4_charge', 100)
        ult4_cd = getattr(player, 'ult4_cooldown', 0)
        ult4_ratio = ult4_charge / max_ult4 if max_ult4 > 0 else 0
        ult4_ready = ult4_ratio >= 1.0 and ult4_cd <= 0
        ult4_pct = ult4_ratio * 100
        
        # R技能伤害加成（基于护甲层数）
        dmg_bonus = int(armor_stacks * 15)
        
        if ult4_ready:
            flash = abs(math.sin(pygame.time.get_ticks() / 80))
            ult4_color = (int(138 + 80 * flash), int(43 + 60 * flash), int(226 + 29 * flash))
            ult4_text = f"[R] 次元坍缩 就绪! (+{dmg_bonus}%)"
        elif ult4_cd > 0:
            ult4_color = (60, 20, 100)
            ult4_text = f"[R] CD {ult4_cd / 60.0:.1f}s"
        else:
            ult4_color = (int(100 + 38 * ult4_ratio), int(30 + 13 * ult4_ratio), int(180 + 46 * ult4_ratio))
            ult4_text = f"[R] 次元坍缩 {int(ult4_pct)}% (+{dmg_bonus}%)"
        
        draw_status_icon(screen, panel_x + 8, ult4_bar_y - 2, 20, "flame", ult4_color, anim_frame if ult4_ready else 0)
        draw_premium_bar(screen, bar_x, ult4_bar_y, bar_w, int(bar_h * 0.8), ult4_pct, ult4_color,
                         bg_color=(25, 10, 40), glow=ult4_ready, animate_frame=anim_frame if ult4_ready else 0)
        draw_text(screen, ult4_text, 14, label_x, ult4_bar_y, ult4_color if ult4_ready else WHITE, glow=ult4_ready, align='left')
    
    # 【星际海豚·S.D.M.G.】过热系统显示 - 过热超频机制
    if hasattr(player, 'plane_id') and player.plane_id == "sdmg":
        from utils.bullets.sdmg_bullets import OverheatManager
        overheat_mgr = OverheatManager.get_instance(player)
        heat = overheat_mgr.heat
        max_heat = overheat_mgr.max_heat
        is_overheated = overheat_mgr.is_overheated
        is_overcharge = overheat_mgr.is_overcharge_active
        
        heat_ratio = heat / max_heat if max_heat > 0 else 0
        heat_pct = heat_ratio * 100
        
        # 颜色基于过热状态（青/红色系）
        if is_overcharge:
            flash = abs(math.sin(pygame.time.get_ticks() / 60))
            sdmg_color = (int(255 * flash), int(200 + 55 * flash), int(100 * (1 - flash)))
            status_text = f"★超频中★ 伤害+50%"
        elif is_overheated:
            flash = abs(math.sin(pygame.time.get_ticks() / 80))
            sdmg_color = (int(200 + 55 * flash), int(50 * flash), int(50 * flash))
            status_text = f"过热! 冷却中..."
        elif heat_ratio > 0.8:
            sdmg_color = (255, int(100 + 60 * (1 - heat_ratio)), 50)
            status_text = f"热量 {int(heat_pct)}% 接近过热!"
        elif heat_ratio > 0.5:
            sdmg_color = (255, int(180 - 80 * heat_ratio), 80)
            status_text = f"热量 {int(heat_pct)}% 高效火控 +30%射速"
        else:
            sdmg_color = (0, 255, 255)
            status_text = f"热量 {int(heat_pct)}%" if heat > 0 else "加特林就绪"
        
        draw_status_icon(screen, panel_x + 8, special_bar_y - 2, 20, "flame", sdmg_color, anim_frame if is_overcharge else 0)
        zone_start_ratio, zone_end_ratio = 0.5, 0.9
        zone_w = max(0, zone_end_ratio - zone_start_ratio)
        if zone_w > 0:
            zone_surface = pygame.Surface((int(bar_w * zone_w), bar_h), pygame.SRCALPHA)
            zone_surface.fill((40, 140, 200, 55))
            screen.blit(zone_surface, (bar_x + int(bar_w * zone_start_ratio), special_bar_y))
            marker_color = (120, 220, 255)
            pygame.draw.line(screen, marker_color,
                             (bar_x + int(bar_w * zone_start_ratio), special_bar_y - 3),
                             (bar_x + int(bar_w * zone_start_ratio), special_bar_y + bar_h + 3), 1)
            pygame.draw.line(screen, marker_color,
                             (bar_x + int(bar_w * zone_end_ratio), special_bar_y - 3),
                             (bar_x + int(bar_w * zone_end_ratio), special_bar_y + bar_h + 3), 1)
            if zone_start_ratio <= heat_ratio < zone_end_ratio:
                draw_text(screen, "高效热区", 13,
                          bar_x + int(bar_w * zone_start_ratio) + 4,
                          special_bar_y - 16, marker_color, align='left')
        draw_premium_bar(screen, bar_x, special_bar_y, bar_w, bar_h, heat_pct, sdmg_color,
                       bg_color=(20, 35, 40), glow=is_overcharge, animate_frame=anim_frame if is_overcharge else 0)
        draw_text(screen, status_text, 15, label_x, special_bar_y, sdmg_color if is_overcharge else WHITE, glow=is_overcharge, align='left')
        
        # 【轨道轰炸】第四大招显示
        ult4_bar_y = special_bar_y + bar_gap
        ult4_charge = getattr(player, 'ult4_charge', 0)
        max_ult4 = getattr(player, 'max_ult4_charge', 100)
        ult4_cd = getattr(player, 'ult4_cooldown', 0)
        ult4_ratio = ult4_charge / max_ult4 if max_ult4 > 0 else 0
        ult4_ready = ult4_ratio >= 1.0 and ult4_cd <= 0
        ult4_pct = ult4_ratio * 100
        
        if ult4_ready:
            flash = abs(math.sin(pygame.time.get_ticks() / 80))
            ult4_color = (int(200 + 55 * flash), int(150 + 50 * flash), int(50 + 50 * flash))
            ult4_text = f"[R] 轨道轰炸 就绪!"
        elif ult4_cd > 0:
            ult4_color = (100, 80, 40)
            ult4_text = f"[R] CD {ult4_cd / 60.0:.1f}s"
        else:
            ult4_color = (int(150 + 105 * ult4_ratio), int(100 + 100 * ult4_ratio), int(50 + 50 * ult4_ratio))
            ult4_text = f"[R] 轨道轰炸 {int(ult4_pct)}%"
        
        draw_status_icon(screen, panel_x + 8, ult4_bar_y - 2, 20, "star", ult4_color, anim_frame if ult4_ready else 0)
        draw_premium_bar(screen, bar_x, ult4_bar_y, bar_w, int(bar_h * 0.8), ult4_pct, ult4_color,
                         bg_color=(30, 25, 15), glow=ult4_ready, animate_frame=anim_frame if ult4_ready else 0)
        draw_text(screen, ult4_text, 14, label_x, ult4_bar_y, ult4_color if ult4_ready else WHITE, glow=ult4_ready, align='left')
    
    # ===== 顶部右侧：高级积分和时间面板 =====
    anim_frame = pygame.time.get_ticks() // 16
    panel_right_x = WIDTH - 170
    panel_right_y = 8
    panel_w = 162
    
    # ========== 得分面板 ==========
    score_panel_h = 52
    
    # 面板背景 - 渐变 + 斜切角
    score_surf = pygame.Surface((panel_w + 20, score_panel_h + 10), pygame.SRCALPHA)
    cut = 12  # 斜切角大小
    
    # 六边形背景点
    score_bg_points = [
        (cut, 0), (panel_w, 0), (panel_w + cut, cut), 
        (panel_w + cut, score_panel_h), (panel_w, score_panel_h + cut), 
        (cut, score_panel_h + cut), (0, score_panel_h), (0, cut)
    ]
    
    # 渐变填充
    for i in range(score_panel_h + cut):
        ratio = i / max(1, score_panel_h + cut - 1)
        r = int(25 + 15 * ratio)
        g = int(15 + 10 * (1 - ratio))
        b = int(10 + 20 * ratio)
        pygame.draw.line(score_surf, (r, g, b, 220), (0, i), (panel_w + cut, i))
    
    # 裁剪为多边形
    mask = pygame.Surface((panel_w + 20, score_panel_h + 10), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), score_bg_points)
    score_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(score_surf, (panel_right_x - 5, panel_right_y))
    
    # 边框 - 橙色主题
    score_border_points = [(panel_right_x - 5 + p[0], panel_right_y + p[1]) for p in score_bg_points]
    pygame.draw.polygon(screen, (255, 140, 40), score_border_points, 2)
    
    # 顶部装饰线 - 脉冲发光
    pulse = abs(math.sin(pygame.time.get_ticks() / 350))
    deco_color = (200 + int(55 * pulse), 120 + int(50 * pulse), 20)
    pygame.draw.line(screen, deco_color, 
                     (panel_right_x + cut - 3, panel_right_y + 3), 
                     (panel_right_x + panel_w - 5, panel_right_y + 3), 2)
    
    # 角落装饰
    corner_color = (255, 180, 80)
    # 左上角
    pygame.draw.line(screen, corner_color, (panel_right_x - 5, panel_right_y + cut), 
                     (panel_right_x - 5, panel_right_y + cut + 12), 2)
    # 右下角
    pygame.draw.line(screen, corner_color, (panel_right_x + panel_w + cut - 5, panel_right_y + score_panel_h), 
                     (panel_right_x + panel_w + cut - 5, panel_right_y + score_panel_h - 12), 2)
    
    # 得分标签
    from utils.ui import draw_premium_text
    draw_premium_text(screen, "SCORE", 10, panel_right_x + 2, panel_right_y + 6, (255, 200, 120), align='left', style="cyber")
    
    # 得分图标 - 星形
    icon_surf = pygame.Surface((18, 18), pygame.SRCALPHA)
    # 外层发光
    pygame.draw.polygon(icon_surf, (255, 180, 50, 100), [(9, 0), (11, 6), (17, 7), (12, 11), (14, 17), (9, 14), (4, 17), (6, 11), (1, 7), (7, 6)])
    pygame.draw.polygon(icon_surf, (255, 220, 80), [(9, 2), (10, 6), (15, 7), (11, 10), (13, 15), (9, 12), (5, 15), (7, 10), (3, 7), (8, 6)])
    screen.blit(icon_surf, (panel_right_x + panel_w - 8, panel_right_y + 3))
    
    # 得分数值 - 大字体 + 跳动效果 + 高质感渲染
    bounce = int(2 * math.sin(pygame.time.get_ticks() / 250))
    score_text = f"{int(score):,}"
    
    # 根据分数选择渲染风格
    if score >= 100000:
        score_color = (255, 255, 150)  # 金色发光
        score_style = "neon"
    elif score >= 50000:
        score_color = (255, 200, 80)
        score_style = "glow"
    else:
        score_color = (255, 180, 50)
        score_style = "metal"
    
    draw_premium_text(screen, score_text, 28, panel_right_x + panel_w, panel_right_y + 18 + bounce, score_color, align='right', style=score_style)
    
    # ========== 时间面板 ==========
    time_panel_y = panel_right_y + score_panel_h + 12
    time_panel_h = 48
    
    # 面板背景
    time_surf = pygame.Surface((panel_w + 20, time_panel_h + 10), pygame.SRCALPHA)
    
    time_bg_points = [
        (cut, 0), (panel_w, 0), (panel_w + cut, cut), 
        (panel_w + cut, time_panel_h), (panel_w, time_panel_h + cut), 
        (cut, time_panel_h + cut), (0, time_panel_h), (0, cut)
    ]
    
    # 渐变填充 - 青色主题
    for i in range(time_panel_h + cut):
        ratio = i / max(1, time_panel_h + cut - 1)
        r = int(10 + 10 * ratio)
        g = int(25 + 15 * (1 - ratio))
        b = int(35 + 15 * ratio)
        pygame.draw.line(time_surf, (r, g, b, 220), (0, i), (panel_w + cut, i))
    
    # 裁剪
    mask2 = pygame.Surface((panel_w + 20, time_panel_h + 10), pygame.SRCALPHA)
    pygame.draw.polygon(mask2, (255, 255, 255, 255), time_bg_points)
    time_surf.blit(mask2, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(time_surf, (panel_right_x - 5, time_panel_y))
    
    # 边框 - 青色主题
    time_border_points = [(panel_right_x - 5 + p[0], time_panel_y + p[1]) for p in time_bg_points]
    pygame.draw.polygon(screen, (80, 200, 220), time_border_points, 2)
    
    # 顶部装饰线
    time_pulse = abs(math.sin(pygame.time.get_ticks() / 400 + 1))
    time_deco_color = (50 + int(50 * time_pulse), 180 + int(50 * time_pulse), 220 + int(35 * time_pulse))
    pygame.draw.line(screen, time_deco_color, 
                     (panel_right_x + cut - 3, time_panel_y + 3), 
                     (panel_right_x + panel_w - 5, time_panel_y + 3), 2)
    
    # 角落装饰
    time_corner_color = (100, 220, 255)
    pygame.draw.line(screen, time_corner_color, (panel_right_x - 5, time_panel_y + cut), 
                     (panel_right_x - 5, time_panel_y + cut + 10), 2)
    pygame.draw.line(screen, time_corner_color, (panel_right_x + panel_w + cut - 5, time_panel_y + time_panel_h), 
                     (panel_right_x + panel_w + cut - 5, time_panel_y + time_panel_h - 10), 2)
    
    # 时间标签
    draw_premium_text(screen, "TIME", 10, panel_right_x + 2, time_panel_y + 5, (140, 230, 255), align='left', style="cyber")
    
    # 时间图标 - 简易时钟（增强）
    clock_cx = panel_right_x + panel_w
    clock_cy = time_panel_y + 12
    # 外圈发光
    pygame.draw.circle(screen, (60, 180, 220, 80), (clock_cx, clock_cy), 9, 1)
    pygame.draw.circle(screen, (100, 220, 255), (clock_cx, clock_cy), 7, 1)
    # 中心点
    pygame.draw.circle(screen, (150, 255, 255), (clock_cx, clock_cy), 2)
    clock_angle = (pygame.time.get_ticks() / 1000) % 60 * 6  # 秒针角度
    import math as m
    needle_x = clock_cx + int(4 * m.sin(m.radians(clock_angle)))
    needle_y = clock_cy - int(4 * m.cos(m.radians(clock_angle)))
    pygame.draw.line(screen, (180, 255, 255), (clock_cx, clock_cy), (needle_x, needle_y), 2)
    
    # 时间 MM:SS
    elapsed_sec = int(pygame.time.get_ticks() / 1000)
    elapsed_min = elapsed_sec // 60
    elapsed_sec_remain = elapsed_sec % 60
    time_text = f"{elapsed_min:02d}:{elapsed_sec_remain:02d}"
    
    # 冒号闪烁效果
    colon_visible = (pygame.time.get_ticks() // 500) % 2 == 0
    if colon_visible:
        display_time = time_text
    else:
        display_time = f"{elapsed_min:02d} {elapsed_sec_remain:02d}"
    
    # 时间数值 - 根据时间变化风格
    if elapsed_min >= 10:
        time_color = (180, 255, 255)  # 清亮的青色
        time_style = "neon"
    elif elapsed_min >= 5:
        time_color = (120, 240, 255)
        time_style = "glow"
    else:
        time_color = (100, 220, 255)
        time_style = "metal"
    
    draw_premium_text(screen, display_time, 26, panel_right_x + panel_w, time_panel_y + 16, time_color, align='right', style=time_style)
    
    # ===== 底部左侧：主炮 / 飞机建模 / 核心（往上移以避免与等级重合） =====
    bottom_left_x = 12
    bottom_left_y = HEIGHT - 180  # 往上移 15px
    
    # 飞机小建模 - 重构为多层复杂几何形状
    frame_x = bottom_left_x - 5
    frame_y = bottom_left_y + 28
    frame_w = 80
    frame_h = 80
    
    # 外层：八边形边框 (赛博朋克风格多层结构)
    offset = 8
    outer_points = [
        (frame_x + frame_w // 2 - offset, frame_y),                    # 上中
        (frame_x + frame_w - offset, frame_y + offset),               # 上右
        (frame_x + frame_w, frame_y + frame_h // 2),                  # 右中
        (frame_x + frame_w - offset, frame_y + frame_h - offset),     # 下右
        (frame_x + frame_w // 2 + offset, frame_y + frame_h),         # 下中
        (frame_x + offset, frame_y + frame_h - offset),               # 下左
        (frame_x, frame_y + frame_h // 2),                            # 左中
        (frame_x + offset, frame_y + offset)                          # 上左
    ]
    pygame.draw.polygon(screen, (30, 60, 100), outer_points)  # 深蓝色填充
    pygame.draw.polygon(screen, (100, 200, 255), outer_points, 1)  # 浅青色边框
    
    # 恢复棱形圆圈 - 青色边框
    diamond_points = [
        (frame_x + frame_w // 2, frame_y),
        (frame_x + frame_w, frame_y + frame_h // 2),
        (frame_x + frame_w // 2, frame_y + frame_h),
        (frame_x, frame_y + frame_h // 2)
    ]
    pygame.draw.polygon(screen, CYAN, diamond_points, 2)
    
    # 中层：菱形框架 (黄色/紫色交替)
    mid_points = [
        (frame_x + frame_w // 2, frame_y + 2),
        (frame_x + frame_w - 4, frame_y + frame_h // 2),
        (frame_x + frame_w // 2, frame_y + frame_h - 2),
        (frame_x + 4, frame_y + frame_h // 2)
    ]
    pygame.draw.polygon(screen, (200, 100, 200), mid_points, 2)  # 紫色菱形边框
    
    # 内层：飞机模型 + 炫彩背景圆
    plane_center_x = bottom_left_x + 35
    plane_center_y = bottom_left_y + 68
    
    # 绘制脉冲光圈背景
    pulse = abs(math.sin(pygame.time.get_ticks() / 400))
    glow_radius = int(45 + 8 * pulse)
    glow_color = (50 + int(100 * pulse), 100 + int(50 * pulse), 150 + int(50 * pulse))
    pygame.draw.circle(screen, glow_color, (plane_center_x, plane_center_y), glow_radius, 1)
    pygame.draw.circle(screen, (glow_color[0] // 2, glow_color[1] // 2, glow_color[2] // 2), 
                       (plane_center_x, plane_center_y), glow_radius - 2, 1)
    
    # 绘制彩色装饰点 (5个点环绕)
    import math as math_module
    for i in range(5):
        angle = (pygame.time.get_ticks() / 2000) + (i * 2 * math_module.pi / 5)
        point_x = int(plane_center_x + 50 * math_module.cos(angle))
        point_y = int(plane_center_y + 50 * math_module.sin(angle))
        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100), (255, 100, 255)]
        pygame.draw.circle(screen, colors[i], (point_x, point_y), 3)
    
    # 绘制飞机模型
    try:
        plane_surf = get_plane_surf(player.plane_id, player.visual)
        if plane_surf:
            plane_small = pygame.transform.scale(plane_surf, (70, 70))
            screen.blit(plane_small, (bottom_left_x, bottom_left_y + 33))
    except Exception as e:
        log_debug(f"Failed to draw plane model: {e}")
    
    # 主炮标签 - 展示在飞机正上方
    draw_text(screen, "主炮", 16, bottom_left_x + 35, bottom_left_y + 15, WHITE, glow=True, align='center')
    
    # 主炮背景框 - 装饰线条
    main_gun_pulse = abs(math.sin(pygame.time.get_ticks() / 500))
    main_gun_color = (100 + int(155 * main_gun_pulse), 50, 50)  # 脉冲效果
    pygame.draw.line(screen, main_gun_color, (bottom_left_x + 10, bottom_left_y + 12), (bottom_left_x + 60, bottom_left_y + 12), 2)
    
    # ===== 底部右侧：高级武器库 / 武器槽 / 大招能量条 =====
    animate_frame = pygame.time.get_ticks() // 16  # 动画帧计数
    bottom_right_x = WIDTH - 24
    bottom_right_y = HEIGHT - 195  # 上移30像素
    
    # --- 武器槽系统 ---
    slot_size = 42
    slot_gap = 10
    slot_total_w = slot_size * 3 + slot_gap * 2
    slot_start_x = bottom_right_x - slot_total_w - 8
    slot_y = bottom_right_y + 20
    
    # 僚机指示器（使用新组件）
    wingman_count = len(player.wingman_squadron.wingmen) if player.wingman_squadron else 0
    wingman_max = player.max_wingmen if hasattr(player, 'max_wingmen') else 4
    wingman_center_x = slot_start_x + slot_total_w // 2
    draw_wingman_indicator(screen, wingman_center_x, slot_y - 12, wingman_count, wingman_max, animate_frame)
    
    # 武器槽（使用新的高级组件）
    for i in range(3):
        slot_x = slot_start_x + i * (slot_size + slot_gap)
        weapon = player.weapon_slots[i] if i < len(player.weapon_slots) else None
        is_current = (i == player.current_slot)
        
        weapon_info = None
        cooldown = 0
        if weapon:
            w_info = WEAPON_TYPES.get(weapon.type, {})
            weapon_info = {
                'name': w_info.get('name', '？'),
                'color': w_info.get('color', (80, 80, 100))
            }
            if weapon.cooldown > 0:
                cooldown = weapon.cooldown / 30.0
        
        draw_premium_weapon_slot(screen, slot_x, slot_y, slot_size, weapon_info, 
                                  is_current=is_current, cooldown=cooldown, animate_frame=animate_frame)
    
    # --- 大招能量条系统（使用新的高级进度条）---
    ult_bar_width = 150
    ult_bar_x = bottom_right_x - ult_bar_width - 4
    
    # [F] 主大招
    ult_name = player.plane_data.get('ult_name', 'ULT')
    ult1_y = slot_y + slot_size + 8
    
    ult_ratio = player.ult_charge / player.max_ult_charge if player.max_ult_charge > 0 else 0
    ult_pct = int(ult_ratio * 100)
    ult_ready = ult_ratio >= 1.0 and player.ult_cooldown <= 0
    ult_cd = player.ult_cooldown / 60.0 if player.ult_cooldown > 0 else 0
    
    # 标签
    label_color = (200, 150, 255) if ult_ready else (180, 100, 220)
    draw_text(screen, f"[F] {ult_name}", 12, ult_bar_x, ult1_y, label_color, align='left', glow=ult_ready)
    
    # 能量条
    bar1_y = ult1_y + 15
    bar1_h = 14
    draw_premium_ult_bar(screen, ult_bar_x, bar1_y, ult_bar_width, bar1_h, ult_pct, 
                          (200, 80, 220), ult_name, "[F]", ready=ult_ready, 
                          cooldown=ult_cd, animate_frame=animate_frame)
    
    # 百分比
    pct_color = (220, 180, 255) if ult_ready else (180, 180, 200)
    draw_text(screen, f"{ult_pct}%", 11, ult_bar_x + ult_bar_width + 12, bar1_y + 1, pct_color, align='left')
    
    # [G] 副大招
    ult2_names = {
        "striker": "欧米伽激光", "phantom": "分身乱舞", "titan": "陨石轰炸",
        "thunderbird": "连锁闪电", "viper": "酸雨倾盆", "specter": "亡魂哀嚎",
        "aurora": "极光冲击波", "crimson": "刀刃风暴", "stalker": "引力陷阱",
        "gaia": "岩石护盾", "weaver": "蛛网陷阱", "solar": "太阳耀斑",
        "arbiter": "数据腐蚀", "eclipse": "暗物质爆发", "prism": "彩虹碎裂",
        "necro": "生命汲取", "void": "虚空撕裂", "wormhole": "虫洞链接",
        "chronos": "时光冻结", "mirage": "幻影分身", "gambit": "爆裂连锁",
        "puppeteer": "偶线操控", "pandemic": "病毒变异",
        "omega": "七曜轮转", "genesis": "毁灭之形",
        "truth": "真言审判", "asura": "六臂天刑", "dragoon": "龙骑冲锋",
        "origami": "纸鹤群舞", "helios": "流星轰炸", "frostflare": "极寒风暴",
        "nova": "充能穿甲", "spectrum": "光谱叠加", "darkstring": "暗影标记",
        "thornvine": "荆棘缠绕", "starblade": "星刃回旋", "acidswamp": "酸沼扩散",
        "crystalfall": "晶簇连锁", "sporeveil": "孢子繁殖",
        "cthulhu": "月蚀审判", "turu": "岩拳连击", "staradia": "皇辉残影",
        "dukefishron": "鲨龙追踪", "slime": "星炎水晶", "oro": "激光栅风暴",
        "yharon": "龙群盛宴", "scarlet": "绯红不夜城",
        "providence": "神圣射线", "goliath": "瘟疫核弹", "sepulcher": "天降灾厄",
        "galaxia": "星系陷阱", "magnus": "远古亡灵召唤", "heavymetal": "舞台俯冲",
        "zenith": "传奇剑舞", "viscerator": "归束轰击",
        "sdmg": "鲨卷风"
    }
    ult2_name = ult2_names.get(player.plane_id, '次级技能')
    ult2_y = bar1_y + bar1_h + 4
    
    ult2_ratio = player.ult2_charge / player.max_ult2_charge if player.max_ult2_charge > 0 else 0
    ult2_pct = int(ult2_ratio * 100)
    ult2_ready = ult2_ratio >= 1.0 and player.ult2_cooldown <= 0
    ult2_cd = player.ult2_cooldown / 60.0 if player.ult2_cooldown > 0 else 0
    
    # 标签
    label2_color = (100, 255, 200) if ult2_ready else (80, 200, 180)
    draw_text(screen, f"[G] {ult2_name}", 11, ult_bar_x, ult2_y, label2_color, align='left', glow=ult2_ready)
    
    # 能量条
    bar2_y = ult2_y + 14
    bar2_h = 12
    draw_premium_ult_bar(screen, ult_bar_x, bar2_y, ult_bar_width, bar2_h, ult2_pct,
                          (60, 200, 180), ult2_name, "[G]", ready=ult2_ready,
                          cooldown=ult2_cd, animate_frame=animate_frame)
    
    # 百分比
    pct2_color = (150, 255, 220) if ult2_ready else (150, 200, 190)
    draw_text(screen, f"{ult2_pct}%", 10, ult_bar_x + ult_bar_width + 12, bar2_y + 1, pct2_color, align='left')
    
    # [C] 第三大招
    ult3_names = {
        "striker": "等离子漩涡", "phantom": "镜像分裂", "titan": "地震冲击",
        "thunderbird": "球状闪电", "viper": "腐蚀云雾", "specter": "灵魂风暴",
        "aurora": "北极光", "crimson": "刀刃旋风", "stalker": "重力炸弹",
        "gaia": "水晶屏障", "weaver": "蜘蛛群袭", "solar": "太阳光束",
        "arbiter": "病毒感染", "eclipse": "虚空坍缩", "prism": "光之棱镜",
        "necro": "灵魂收割", "void": "等离子漩涡", "wormhole": "时空逆流",
        "chronos": "时空回溯", "mirage": "全息影印", "gambit": "命运翻转",
        "puppeteer": "人偶军团", "pandemic": "全球感染",
        "omega": "元素融合", "genesis": "创世大爆炸",
        "truth": "天启裁决", "asura": "修罗怒斩", "dragoon": "苍龙天翔",
        "origami": "千羽化形", "helios": "流星群", "frostflare": "绝对零度",
        "nova": "毁灭射线", "spectrum": "七彩极光", "darkstring": "绝杀狙击",
        "thornvine": "骨蔓分裂", "starblade": "星镰乱舞", "acidswamp": "腐蚀大潮",
        "crystalfall": "晶瀑倾泻", "sporeveil": "菌海爆发",
        "cthulhu": "星骸剥离", "turu": "巨石核爆", "staradia": "皇辉领域",
        "dukefishron": "海啸滑翔", "slime": "星凝子体", "oro": "终噬黑洞",
        "yharon": "宿敌升天", "scarlet": "命运之枪",
        "providence": "超新星爆发", "goliath": "盖亚之死", "sepulcher": "湮灭之眼",
        "galaxia": "苍穹撕裂", "magnus": "真理魔法阵", "heavymetal": "死亡金属独奏",
        "zenith": "终极剑阵", "viscerator": "星流过载",
        "sdmg": "月球领主之凝视"
    }
    ult3_name = ult3_names.get(player.plane_id, '终极技能')
    ult3_y = bar2_y + bar2_h + 4
    
    ult3_ratio = player.ult3_charge / player.max_ult3_charge if player.max_ult3_charge > 0 else 0
    ult3_pct = int(ult3_ratio * 100)
    ult3_ready = ult3_ratio >= 1.0 and player.ult3_cooldown <= 0
    ult3_cd = player.ult3_cooldown / 60.0 if player.ult3_cooldown > 0 else 0
    
    # 标签
    label3_color = (255, 200, 100) if ult3_ready else (255, 180, 80)
    draw_text(screen, f"[C] {ult3_name}", 11, ult_bar_x, ult3_y, label3_color, align='left', glow=ult3_ready)
    
    # 能量条
    bar3_y = ult3_y + 14
    bar3_h = 12
    draw_premium_ult_bar(screen, ult_bar_x, bar3_y, ult_bar_width, bar3_h, ult3_pct,
                          (255, 160, 60), ult3_name, "[C]", ready=ult3_ready,
                          cooldown=ult3_cd, animate_frame=animate_frame)
    
    # 百分比
    pct3_color = (255, 220, 150) if ult3_ready else (200, 180, 150)
    draw_text(screen, f"{ult3_pct}%", 10, ult_bar_x + ult_bar_width + 12, bar3_y + 1, pct3_color, align='left')
    
    # ===== 底部：经验条 =====
    exp_bar_y = HEIGHT - 14
    exp_bar_h = 12
    exp_val = player.xp if hasattr(player, 'xp') else 0
    exp_max = player.next_level_xp if hasattr(player, 'next_level_xp') else 100
    exp_pct = (exp_val / exp_max * 100) if exp_max > 0 else 0
    
    # 渐变背景
    for i in range(exp_bar_h):
        ratio = i / max(1, exp_bar_h - 1)
        r = int(10 + 15 * ratio)
        g = int(20 + 10 * ratio)
        b = int(15 + 15 * ratio)
        pygame.draw.line(screen, (r, g, b), (0, exp_bar_y + i), (WIDTH, exp_bar_y + i))
    
    # 填充 - 带光泽效果
    exp_fill_w = int((exp_pct / 100) * WIDTH)
    if exp_fill_w > 0:
        # 主色填充
        for i in range(exp_bar_h):
            ratio = i / max(1, exp_bar_h - 1)
            brightness = 1.0 + (0.5 - abs(ratio - 0.3)) * 0.4
            r = min(255, int(80 * brightness))
            g = min(255, int(255 * brightness))
            b = min(255, int(100 * brightness))
            pygame.draw.line(screen, (r, g, b), (0, exp_bar_y + i), (exp_fill_w, exp_bar_y + i))
        # 顶部高光
        pygame.draw.line(screen, (200, 255, 200, 150), (0, exp_bar_y + 1), (exp_fill_w, exp_bar_y + 1))
    # 边框

    pygame.draw.rect(screen, CYAN, (0, exp_bar_y, WIDTH, exp_bar_h), 1)
    
    # 等级文本靠左，EXP条上方（放大字体，往上移）
    draw_text(screen, f"等级{int(player.level)}", 20, 8, exp_bar_y - 30, CYBER_AMBER, glow=True, align='left')
    
    # ===== 顶部中央：BOSS血条 (如果有BOSS) =====
    if boss:
        boss_y = 75  # 顶部居中位置，在FPS显示下方
        boss_bar_w = 480
        boss_x = (WIDTH - boss_bar_w) // 2  # 居中
        boss_bar_h = 14  # 更细的血条
        center_x = WIDTH // 2  # 中心点居中
        
        # 获取Boss类型对应的血条风格
        boss_type = getattr(boss, 'type', 'default')
        boss_color = getattr(boss, 'data', {}).get('color', (255, 80, 80))
        
        # 10种独特的血条风格配置
        BOSS_BAR_STYLES = {
            # 菌生蟹皇 - 孢子/菌丝风格（青绿色+有机纹理）
            'fungal_colossus': {
                'primary': (60, 180, 200),
                'secondary': (30, 80, 120),
                'glow': (100, 220, 220),
                'pattern': 'organic',  # 有机波纹
                'border': (40, 150, 170),
                'particles': True,
            },
            # 旱海狂鲨 - 沙漠风格（金黄色+沙尘效果）
            'dune_reaper': {
                'primary': (220, 180, 80),
                'secondary': (140, 100, 40),
                'glow': (255, 220, 120),
                'pattern': 'sand',  # 沙粒纹理
                'border': (200, 160, 60),
                'particles': True,
            },
            # 歌莉娅女王 - 毒蜂风格（荧光绿+六边形）
            'plague_empress': {
                'primary': (57, 255, 20),
                'secondary': (20, 120, 10),
                'glow': (120, 255, 80),
                'pattern': 'hex',  # 六边形蜂巢
                'border': (80, 200, 40),
                'particles': True,
            },
            # 毁灭魔像 - 血肉风格（深红色+血管纹理）
            'flesh_totem': {
                'primary': (180, 30, 30),
                'secondary': (80, 10, 10),
                'glow': (255, 60, 60),
                'pattern': 'veins',  # 血管纹理
                'border': (150, 20, 20),
                'particles': True,
            },
            # 星神游龙 - 星空风格（紫色+星光闪烁）
            'star_serpent': {
                'primary': (200, 100, 255),
                'secondary': (80, 40, 150),
                'glow': (230, 150, 255),
                'pattern': 'stars',  # 星光闪烁
                'border': (180, 80, 220),
                'particles': True,
            },
            # 终焉巨械·阿瑞斯 - 机械风格（RGB霓虹+电路板）
            'exo_ares': {
                'primary': (255, 100, 255),
                'secondary': (100, 40, 100),
                'glow': (255, 150, 255),
                'pattern': 'circuit',  # 电路板纹理
                'border': (220, 80, 220),
                'particles': True,
            },
            # 亵渎天神 - 神圣风格（金色+光环）
            'radiance_goddess': {
                'primary': (255, 215, 0),
                'secondary': (180, 140, 0),
                'glow': (255, 240, 150),
                'pattern': 'holy',  # 神圣光芒
                'border': (255, 200, 50),
                'particles': True,
            },
            # 维度之噬 - 虚空风格（深紫色+扭曲效果）
            'dimension_devourer': {
                'primary': (120, 0, 200),
                'secondary': (40, 0, 80),
                'glow': (180, 80, 255),
                'pattern': 'void',  # 虚空扭曲
                'border': (100, 0, 180),
                'particles': True,
            },
            # 暴君犽戎 - 炎龙风格（火焰橙红+火焰纹理）
            'infernal_dragon': {
                'primary': (255, 100, 0),
                'secondary': (180, 40, 0),
                'glow': (255, 180, 50),
                'pattern': 'flame',  # 火焰纹理
                'border': (255, 120, 20),
                'particles': True,
            },
            # 熵之化身 - 真理风格（纯白+黑暗交织）
            'entropy_avatar': {
                'primary': (255, 255, 255),
                'secondary': (40, 40, 50),
                'glow': (255, 255, 255),
                'pattern': 'truth',  # 真理符文
                'border': (200, 200, 220),
                'particles': True,
            },
        }
        
        # 获取当前Boss的风格，如果没有则使用默认
        style = BOSS_BAR_STYLES.get(boss_type, {
            'primary': boss_color,
            'secondary': (boss_color[0]//3, boss_color[1]//3, boss_color[2]//3),
            'glow': (min(255, boss_color[0]+50), min(255, boss_color[1]+50), min(255, boss_color[2]+50)),
            'pattern': 'default',
            'border': boss_color,
            'particles': False,
        })
        
        t = pygame.time.get_ticks()
        pulse = math.sin(t * 0.005) * 0.5 + 0.5
        
        # BOSS血条容器背景（半透明+动态边框）
        container_padding = 15
        container_rect = pygame.Rect(boss_x - container_padding, boss_y - 28, 
                                     boss_bar_w + container_padding * 2, 55)
        
        # 容器背景渐变
        bg_surf = pygame.Surface((container_rect.width, container_rect.height), pygame.SRCALPHA)
        for i in range(container_rect.height):
            alpha = int(180 + 40 * (i / container_rect.height))
            r = int(style['secondary'][0] * 0.3)
            g = int(style['secondary'][1] * 0.3)
            b = int(style['secondary'][2] * 0.3)
            pygame.draw.line(bg_surf, (r, g, b, alpha), (0, i), (container_rect.width, i))
        screen.blit(bg_surf, container_rect.topleft)
        
        # 动态边框
        border_pulse = int(pulse * 30)
        border_col = (min(255, style['border'][0] + border_pulse),
                     min(255, style['border'][1] + border_pulse),
                     min(255, style['border'][2] + border_pulse))
        draw_cyber_rect(screen, container_rect, border_col, border_width=2, fill=False)
        
        # 角落装饰
        corner = 12
        for cx, cy, dx, dy in [(container_rect.left, container_rect.top, 1, 1),
                               (container_rect.right, container_rect.top, -1, 1),
                               (container_rect.left, container_rect.bottom, 1, -1),
                               (container_rect.right, container_rect.bottom, -1, -1)]:
            pygame.draw.line(screen, style['glow'], (cx, cy), (cx + dx*corner, cy), 2)
            pygame.draw.line(screen, style['glow'], (cx, cy), (cx, cy + dy*corner), 2)
        
        # BOSS名称（居中，风格化）
        boss_name_text = boss.name.upper()
        name_y = boss_y - 22
        
        # 名称光晕
        for offset in range(3, 0, -1):
            glow_alpha = 100 - offset * 30
            glow_col = (style['glow'][0], style['glow'][1], style['glow'][2])
            for ox, oy in [(-offset, 0), (offset, 0), (0, -offset), (0, offset)]:
                draw_text(screen, boss_name_text, 18, center_x + ox, name_y + oy, glow_col)
        draw_text(screen, boss_name_text, 18, center_x, name_y, WHITE, glow=True)
        
        # 血条外框装饰
        bar_border = pygame.Rect(boss_x - 3, boss_y - 3, boss_bar_w + 6, boss_bar_h + 6)
        
        # 外层光晕
        glow_surf = pygame.Surface((boss_bar_w + 20, boss_bar_h + 20), pygame.SRCALPHA)
        for r in range(10, 0, -2):
            alpha = int(30 * (1 - r/10))
            pygame.draw.rect(glow_surf, (*style['glow'], alpha), 
                           (10-r, 10-r, boss_bar_w + r*2, boss_bar_h + r*2), border_radius=4)
        screen.blit(glow_surf, (boss_x - 10, boss_y - 10))
        
        # 血条边框
        pygame.draw.rect(screen, style['border'], bar_border, 2, border_radius=4)
        
        # 血条背景
        bg_rect = pygame.Rect(boss_x, boss_y, boss_bar_w, boss_bar_h)
        pygame.draw.rect(screen, style['secondary'], bg_rect, border_radius=3)
        
        # BOSS血条填充
        boss_hp_pct = max(0, min(1, boss.hp / boss.max_hp))
        boss_fill = int(boss_hp_pct * boss_bar_w)
        
        if boss_fill > 0:
            # 创建血条填充表面
            fill_surf = pygame.Surface((boss_fill, boss_bar_h), pygame.SRCALPHA)
            
            # 根据不同风格绘制纹理
            pattern = style['pattern']
            
            if pattern == 'organic':
                # 有机波纹纹理
                for i in range(boss_fill):
                    wave = math.sin(i * 0.1 + t * 0.003) * 0.3 + 0.7
                    r = int(style['primary'][0] * wave)
                    g = int(style['primary'][1] * wave)
                    b = int(style['primary'][2] * wave)
                    pygame.draw.line(fill_surf, (r, g, b), (i, 0), (i, boss_bar_h))
                # 菌丝装饰
                for i in range(0, boss_fill, 20):
                    y_off = int(math.sin(i * 0.2 + t * 0.002) * 5)
                    pygame.draw.circle(fill_surf, style['glow'], (i, boss_bar_h//2 + y_off), 3)
                    
            elif pattern == 'sand':
                # 沙粒纹理
                for i in range(boss_fill):
                    noise = random.random() * 0.3 + 0.7 if (t // 100) % 5 == 0 else 0.85
                    r = int(style['primary'][0] * noise)
                    g = int(style['primary'][1] * noise)
                    b = int(style['primary'][2] * noise)
                    pygame.draw.line(fill_surf, (r, g, b), (i, 0), (i, boss_bar_h))
                # 沙尘粒子
                for _ in range(5):
                    px = random.randint(0, boss_fill-1)
                    py = random.randint(0, boss_bar_h-1)
                    pygame.draw.circle(fill_surf, style['glow'], (px, py), 1)
                    
            elif pattern == 'hex':
                # 六边形蜂巢纹理
                fill_surf.fill(style['primary'])
                hex_size = 12
                for row in range(0, boss_bar_h + hex_size, hex_size):
                    offset = (row // hex_size) % 2 * (hex_size // 2)
                    for col in range(-hex_size, boss_fill + hex_size, hex_size):
                        cx, cy = col + offset, row
                        pygame.draw.polygon(fill_surf, style['secondary'], 
                            [(cx + hex_size//2, cy), (cx + hex_size//4, cy + hex_size//2),
                             (cx - hex_size//4, cy + hex_size//2), (cx - hex_size//2, cy),
                             (cx - hex_size//4, cy - hex_size//2), (cx + hex_size//4, cy - hex_size//2)], 1)
                             
            elif pattern == 'veins':
                # 血管纹理
                fill_surf.fill(style['primary'])
                for i in range(3):
                    points = []
                    y_base = boss_bar_h // 2 + (i - 1) * 6
                    for x in range(0, boss_fill, 8):
                        y = y_base + int(math.sin(x * 0.1 + t * 0.002 + i) * 4)
                        points.append((x, y))
                    if len(points) > 1:
                        pygame.draw.lines(fill_surf, style['secondary'], False, points, 2)
                        
            elif pattern == 'stars':
                # 星光闪烁
                for i in range(boss_fill):
                    brightness = 0.7 + math.sin(i * 0.05 + t * 0.004) * 0.3
                    r = int(style['primary'][0] * brightness)
                    g = int(style['primary'][1] * brightness)
                    b = int(style['primary'][2] * brightness)
                    pygame.draw.line(fill_surf, (r, g, b), (i, 0), (i, boss_bar_h))
                # 闪烁星星
                for i in range(8):
                    sx = (t // 50 + i * 73) % boss_fill
                    sy = (i * 3) % boss_bar_h
                    star_pulse = math.sin(t * 0.01 + i) * 0.5 + 0.5
                    if star_pulse > 0.7:
                        pygame.draw.circle(fill_surf, WHITE, (sx, sy), 2)
                        
            elif pattern == 'circuit':
                # 电路板纹理
                fill_surf.fill(style['primary'])
                # RGB流光
                for i in range(boss_fill):
                    rgb_phase = (i + t // 10) % 60
                    if rgb_phase < 20:
                        col = (255, 50, 50)
                    elif rgb_phase < 40:
                        col = (50, 255, 50)
                    else:
                        col = (50, 50, 255)
                    pygame.draw.line(fill_surf, col, (i, 0), (i, 2))
                    pygame.draw.line(fill_surf, col, (i, boss_bar_h-2), (i, boss_bar_h))
                # 电路线
                for i in range(0, boss_fill, 30):
                    pygame.draw.line(fill_surf, style['glow'], (i, boss_bar_h//2 - 4), (i + 15, boss_bar_h//2 - 4), 1)
                    pygame.draw.line(fill_surf, style['glow'], (i + 15, boss_bar_h//2 - 4), (i + 15, boss_bar_h//2 + 4), 1)
                    
            elif pattern == 'holy':
                # 神圣光芒
                for i in range(boss_fill):
                    brightness = 0.8 + math.sin(i * 0.02 + t * 0.003) * 0.2
                    r = int(style['primary'][0] * brightness)
                    g = int(style['primary'][1] * brightness)
                    b = int(style['primary'][2] * brightness)
                    pygame.draw.line(fill_surf, (r, g, b), (i, 0), (i, boss_bar_h))
                # 光柱
                for i in range(0, boss_fill, 40):
                    ray_x = (i + t // 20) % boss_fill
                    pygame.draw.line(fill_surf, WHITE, (ray_x, 0), (ray_x, boss_bar_h), 2)
                    
            elif pattern == 'void':
                # 虚空扭曲
                for i in range(boss_fill):
                    distort = math.sin(i * 0.15 + t * 0.005) * math.cos(i * 0.08 - t * 0.003)
                    brightness = 0.6 + distort * 0.4
                    r = int(style['primary'][0] * brightness)
                    g = int(style['primary'][1] * brightness)
                    b = int(style['primary'][2] * brightness)
                    pygame.draw.line(fill_surf, (r, g, b), (i, 0), (i, boss_bar_h))
                # 虚空裂缝
                for i in range(3):
                    crack_x = (t // 30 + i * 200) % boss_fill
                    pygame.draw.line(fill_surf, (0, 0, 0), (crack_x, 0), (crack_x + 5, boss_bar_h), 2)
                    
            elif pattern == 'flame':
                # 火焰纹理
                for i in range(boss_fill):
                    flame_y = int(math.sin(i * 0.2 + t * 0.01) * 3 + math.sin(i * 0.1 - t * 0.008) * 2)
                    brightness = 0.8 + random.random() * 0.2
                    r = int(min(255, style['primary'][0] * brightness))
                    g = int(style['primary'][1] * brightness * 0.8)
                    b = int(style['primary'][2] * brightness * 0.5)
                    pygame.draw.line(fill_surf, (r, g, b), (i, max(0, flame_y)), (i, boss_bar_h))
                # 火星
                for _ in range(4):
                    fx = random.randint(0, boss_fill - 1)
                    fy = random.randint(0, 5)
                    pygame.draw.circle(fill_surf, (255, 255, 100), (fx, fy), 2)
                    
            elif pattern == 'truth':
                # 真理符文 - 黑白交织
                for i in range(boss_fill):
                    phase = math.sin(i * 0.05 + t * 0.002) * 0.5 + 0.5
                    r = int(255 * phase + 40 * (1 - phase))
                    g = int(255 * phase + 40 * (1 - phase))
                    b = int(255 * phase + 50 * (1 - phase))
                    pygame.draw.line(fill_surf, (r, g, b), (i, 0), (i, boss_bar_h))
                # 眼睛符号
                eye_x = boss_fill // 2
                pygame.draw.ellipse(fill_surf, (0, 0, 0), (eye_x - 15, boss_bar_h//2 - 6, 30, 12), 2)
                pygame.draw.circle(fill_surf, (0, 0, 0), (eye_x, boss_bar_h//2), 4)
                    
            else:
                # 默认渐变
                for i in range(boss_fill):
                    ratio = i / boss_bar_w
                    r = int(style['primary'][0] * (1 - ratio * 0.3))
                    g = int(style['primary'][1] * (1 - ratio * 0.3))
                    b = int(style['primary'][2] * (1 - ratio * 0.3))
                    pygame.draw.line(fill_surf, (r, g, b), (i, 0), (i, boss_bar_h))
            
            # 顶部高光
            highlight_surf = pygame.Surface((boss_fill, boss_bar_h // 3), pygame.SRCALPHA)
            highlight_surf.fill((*style['glow'], 60))
            fill_surf.blit(highlight_surf, (0, 0))
            
            # 边缘发光
            if boss_fill > 3:
                edge_glow = pygame.Surface((6, boss_bar_h), pygame.SRCALPHA)
                for i in range(6):
                    alpha = int(150 * (1 - i / 6))
                    pygame.draw.line(edge_glow, (*style['glow'], alpha), (i, 0), (i, boss_bar_h))
                fill_surf.blit(edge_glow, (boss_fill - 6, 0))
            
            # 绘制填充
            screen.blit(fill_surf, (boss_x, boss_y))
        
        # 粒子效果
        if style['particles'] and boss_fill > 10:
            for i in range(3):
                px = boss_x + boss_fill - 5 + random.randint(-3, 3)
                py = boss_y + random.randint(0, boss_bar_h)
                particle_col = style['glow']
                pygame.draw.circle(screen, particle_col, (px, py), random.randint(1, 2))
        
        # BOSS血量数值
        hp_text = f"{int(boss.hp):,} / {int(boss.max_hp):,}"
        hp_percent = f"({boss_hp_pct * 100:.1f}%)"
        hp_text_y = boss_y + boss_bar_h // 2 - 6
        percent_y = boss_y + boss_bar_h + 10
        
        # 血量数值 - 描边 + 主体
        for ox, oy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            draw_text(screen, hp_text, 13, center_x + ox, hp_text_y + oy, (0, 0, 0))
        draw_text(screen, hp_text, 13, center_x, hp_text_y, WHITE, glow=True)
        
        # 百分比
        for ox, oy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            draw_text(screen, hp_percent, 11, center_x + ox, percent_y + oy, (0, 0, 0))
        draw_text(screen, hp_percent, 11, center_x, percent_y, style['glow'], glow=True)
        
        # 阶段分隔线
        try:
            phases = getattr(boss, 'phase_configs', boss.data.get('phases', []))
            for pidx, p in enumerate(phases):
                thresh = p.get('threshold', 0)
                tx = boss_x + int(boss_bar_w * thresh)
                # 分隔线
                pygame.draw.line(screen, WHITE, (tx, boss_y - 2), (tx, boss_y + boss_bar_h + 2), 2)
                # 阶段标记
                phase_marker = ['I', 'II', 'III', 'IV'][min(pidx, 3)]
                draw_text(screen, phase_marker, 9, tx, boss_y - 8, style['glow'])
        except Exception:
            pass
        
        # 阶段转换闪烁
        if getattr(boss, 'phase_change_timer', 0) > 0:
            phase_label = f"⚠ PHASE {boss.phase_index} ⚠"
            flash = int((t // 100) % 2)
            label_col = style['glow'] if flash else WHITE
            draw_text(screen, phase_label, 20, center_x, boss_y - 55, label_col, glow=True)

def draw_player_stats_panel():
    """绘制按 TAB 时显示的玩家属性面板（覆盖全屏，但保留背景冻结图像）。"""
    if player is None:
        log_debug("draw_player_stats_panel: player is None, skip")
        return
    
    # 为Emoji定义专用字体
    def draw_emoji_text(surf, text, size, x, y, color, align="center", glow=False):
        emoji_font = pygame.font.SysFont(["segoe ui emoji", "apple color emoji", "noto color emoji"], int(size), bold=True)
        text_surf = emoji_font.render(text, True, color)
        text_rect = text_surf.get_rect()
        if align == "center": text_rect.midtop = (x, y)
        elif align == "left": text_rect.topleft = (x, y)
        elif align == "right": text_rect.topright = (x, y)
        
        if glow:
            glow_surf = emoji_font.render(text, True, (color[0]//2, color[1]//2, color[2]//2))
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                surf.blit(glow_surf, (text_rect.x + dx, text_rect.y + dy))
        surf.blit(text_surf, text_rect)
        return text_rect
    
    # 背景模糊遮罩 + 渐变效果
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    safe_blit(screen, overlay, (0, 0))
    
    # 动态粒子背景
    t = pygame.time.get_ticks()
    for i in range(15):
        particle_x = (t / 20 + i * 80) % WIDTH
        particle_y = (t / 30 + i * 60) % HEIGHT
        particle_alpha = int(30 + 20 * math.sin(t / 500 + i))
        pygame.draw.circle(screen, (0, 200, 255, particle_alpha), (int(particle_x), int(particle_y)), 3)

    # 面板主体 - 更大更宽
    panel_w, panel_h = 1100, 600
    panel_x = (WIDTH - panel_w) // 2
    panel_y = (HEIGHT - panel_h) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
    
    # 多层阴影效果
    for offset in range(8, 0, -2):
        shadow_rect = panel_rect.inflate(offset, offset)
        shadow_alpha = 20 - offset * 2
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, shadow_alpha), shadow_surf.get_rect(), border_radius=15)
        safe_blit(screen, shadow_surf, (shadow_rect.x, shadow_rect.y))
    
    # 渐变背景
    for i in range(panel_h):
        gradient_factor = i / panel_h
        color = (
            int(15 + 10 * gradient_factor),
            int(20 + 15 * gradient_factor),
            int(30 + 20 * gradient_factor)
        )
        pygame.draw.line(screen, color, (panel_x, panel_y + i), (panel_x + panel_w, panel_y + i))
    
    # 动态边框 - 流光效果
    border_glow = int(150 + 105 * abs(math.sin(t / 300)))
    draw_cyber_rect(screen, panel_rect, (0, border_glow, border_glow + 50), border_width=4, fill=False)
    
    # 内层边框
    inner_rect = panel_rect.inflate(-10, -10)
    draw_cyber_rect(screen, inner_rect, (0, 150, 200, 80), border_width=1, fill=False)
    
    # 四角装饰
    corner_size = 30
    corner_color = (0, 255, 255)
    corners = [
        (panel_x, panel_y),  # 左上
        (panel_x + panel_w, panel_y),  # 右上
        (panel_x, panel_y + panel_h),  # 左下
        (panel_x + panel_w, panel_y + panel_h)  # 右下
    ]
    for i, (cx, cy) in enumerate(corners):
        angle_offset = t / 400 + i * 1.57
        pulse = 1 + 0.2 * math.sin(angle_offset)
        if i == 0:  # 左上
            pygame.draw.line(screen, corner_color, (cx, cy), (cx + corner_size * pulse, cy), 3)
            pygame.draw.line(screen, corner_color, (cx, cy), (cx, cy + corner_size * pulse), 3)
        elif i == 1:  # 右上
            pygame.draw.line(screen, corner_color, (cx, cy), (cx - corner_size * pulse, cy), 3)
            pygame.draw.line(screen, corner_color, (cx, cy), (cx, cy + corner_size * pulse), 3)
        elif i == 2:  # 左下
            pygame.draw.line(screen, corner_color, (cx, cy), (cx + corner_size * pulse, cy), 3)
            pygame.draw.line(screen, corner_color, (cx, cy), (cx, cy - corner_size * pulse), 3)
        else:  # 右下
            pygame.draw.line(screen, corner_color, (cx, cy), (cx - corner_size * pulse, cy), 3)
            pygame.draw.line(screen, corner_color, (cx, cy), (cx, cy - corner_size * pulse), 3)
    
    # 顶部装饰条 - 扫描线效果
    scan_y = (t / 15) % 80
    for dy in range(0, 80, 5):
        alpha = max(0, 100 - abs(scan_y - dy) * 3)
        pygame.draw.line(screen, (0, 200, 255, alpha), 
                        (panel_x + 20, panel_y + 25 + dy), 
                        (panel_x + panel_w - 20, panel_y + 25 + dy), 1)
    
    # 标题背景 - 玻璃质感
    title_bg = pygame.Rect(panel_x + 20, panel_y + 25, panel_w - 40, 60)
    title_surf = pygame.Surface((title_bg.width, title_bg.height), pygame.SRCALPHA)
    pygame.draw.rect(title_surf, (20, 40, 60, 180), title_surf.get_rect(), border_radius=10)
    safe_blit(screen, title_surf, (title_bg.x, title_bg.y))
    pygame.draw.rect(screen, (0, 200, 255), title_bg, 2, border_radius=10)
    
    # 分隔线 - 发光
    pygame.draw.line(screen, (0, 150, 200), (panel_x + 25, panel_y + 95), (panel_x + panel_w - 25, panel_y + 95), 3)
    pygame.draw.line(screen, (0, 255, 255, 100), (panel_x + 25, panel_y + 96), (panel_x + panel_w - 25, panel_y + 96), 1)

    # 标题 - 多重发光
    title_pulse = 1.0 + 0.1 * math.sin(t / 300)
    draw_text(screen, "战斗单元属性数据库", int(38 * title_pulse), panel_rect.centerx, panel_y + 48, CYAN, glow=True)

    # 【左侧】玩家属性卡片 - 玻璃态射质感
    left_x = panel_x + 40
    top_y = panel_y + 120
    
    # 左侧卡片背景
    left_card = pygame.Rect(left_x - 15, top_y - 15, 450, 420)
    card_surf = pygame.Surface((left_card.width, left_card.height), pygame.SRCALPHA)
    pygame.draw.rect(card_surf, (25, 35, 50, 200), card_surf.get_rect(), border_radius=12)
    safe_blit(screen, card_surf, (left_card.x, left_card.y))
    
    # 卡片边框 - 渐变色
    border_color = (0, int(150 + 50 * math.sin(t / 400)), 255)
    pygame.draw.rect(screen, border_color, left_card, 2, border_radius=12)
    
    # 顶部高光
    pygame.draw.line(screen, (255, 255, 255, 50), 
                    (left_card.x + 20, left_card.y + 5), 
                    (left_card.x + left_card.width - 20, left_card.y + 5), 2)
    
    draw_text(screen, "核心属性", 22, left_x, top_y, CYBER_LIME, glow=True, align="left")
    
    # 等级 - 大号显示
    level_box = pygame.Rect(left_x - 5, top_y + 40, 420, 60)
    level_surf = pygame.Surface((level_box.width, level_box.height), pygame.SRCALPHA)
    pygame.draw.rect(level_surf, (0, 50, 80, 150), level_surf.get_rect(), border_radius=10)
    safe_blit(screen, level_surf, (level_box.x, level_box.y))
    pygame.draw.rect(screen, (0, 200, 255), level_box, 2, border_radius=10)
    
    draw_text(screen, "等级", 20, left_x + 10, top_y + 52, CYAN, align="left", glow=True)
    level_pulse = 1.0 + 0.12 * math.sin(t / 400)
    level_size = int(42 * level_pulse)
    
    # 等级数字 - 带光晕，垂直居中对齐
    level_y_center = top_y + 50
    level_glow_size = int(level_size * 1.5)
    for offset in range(level_glow_size, level_size, -2):
        glow_alpha = int(30 * (1 - (offset - level_size) / (level_glow_size - level_size)))
        draw_text(screen, f"{int(player.level)}", offset, left_x + 360, level_y_center - offset // 2, (*CYBER_LIME[:3], glow_alpha), align="right")
    draw_text(screen, f"{int(player.level)}", level_size, left_x + 360, level_y_center - level_size // 2, CYBER_LIME, glow=True, align="right")
    
    # 经验条 - 增强版
    y_offset = top_y + 115
    xp_ratio = min(1.0, player.xp / max(1, player.next_level_xp))
    
    draw_text(screen, "经验值", 16, left_x + 5, y_offset - 2, (200, 200, 200), align="left")
    draw_text(screen, f"{int(player.xp)}/{int(player.next_level_xp)}", 11, left_x + 360, y_offset - 2, GRAY, align="right")
    
    # 经验条背景
    xp_bar_bg = pygame.Rect(left_x + 5, y_offset + 18, 405, 20)
    pygame.draw.rect(screen, (20, 30, 40), xp_bar_bg, border_radius=10)
    pygame.draw.rect(screen, (50, 80, 100), xp_bar_bg, 2, border_radius=10)
    
    # 经验条填充 - 渐变色
    if xp_ratio > 0:
        xp_fill_width = int(401 * xp_ratio)
        xp_fill = pygame.Rect(left_x + 7, y_offset + 20, xp_fill_width, 16)
        for i in range(xp_fill.height):
            color_factor = i / xp_fill.height
            color = (
                int(0 + 100 * color_factor),
                int(200 - 50 * color_factor),
                255
            )
            pygame.draw.line(screen, color, (xp_fill.x, xp_fill.y + i), (xp_fill.x + xp_fill.width, xp_fill.y + i))
        # 闪光效果
        shine_x = int(xp_fill.x + (t / 10) % xp_fill.width)
        pygame.draw.line(screen, (255, 255, 255, 150), (shine_x, xp_fill.y), (shine_x, xp_fill.y + xp_fill.height), 2)
    
    # 百分比显示
    draw_text(screen, f"{xp_ratio*100:.1f}%", 13, left_x + 210, y_offset + 24, WHITE, glow=True)
    
    # 生命值 - 增强版
    y_offset += 60
    hp_ratio = player.hp / max(1, player.max_hp)
    
    draw_text(screen, "生命值", 16, left_x + 5, y_offset - 2, (255, 100, 100), align="left", glow=True)
    draw_text(screen, f"{int(player.hp)}/{int(player.max_hp)}", 11, left_x + 360, y_offset - 2, GRAY, align="right")
    
    hp_bar_bg = pygame.Rect(left_x + 5, y_offset + 18, 405, 20)
    pygame.draw.rect(screen, (30, 20, 20), hp_bar_bg, border_radius=10)
    pygame.draw.rect(screen, (100, 30, 30), hp_bar_bg, 2, border_radius=10)
    
    if hp_ratio > 0:
        hp_fill_width = int(401 * hp_ratio)
        hp_fill = pygame.Rect(left_x + 7, y_offset + 20, hp_fill_width, 16)
        # 根据血量变色
        if hp_ratio > 0.6:
            hp_color = (50, 255, 100)  # 绿色
        elif hp_ratio > 0.3:
            hp_color = (255, 200, 0)   # 黄色
        else:
            hp_color = (255, 50, 50)   # 红色
            # 低血量闪烁
            if int(t / 200) % 2 == 0:
                hp_color = (255, 100, 100)
        
        for i in range(hp_fill.height):
            color_factor = i / hp_fill.height
            color = tuple(int(c * (0.7 + 0.3 * color_factor)) for c in hp_color)
            pygame.draw.line(screen, color, (hp_fill.x, hp_fill.y + i), (hp_fill.x + hp_fill.width, hp_fill.y + i))
        
        # 脉冲效果
        pulse_size = int(5 * abs(math.sin(t / 500)))
        pygame.draw.line(screen, (255, 255, 255, 100), 
                        (hp_fill.x + hp_fill.width - pulse_size, hp_fill.y), 
                        (hp_fill.x + hp_fill.width - pulse_size, hp_fill.y + hp_fill.height), 3)
    
    draw_text(screen, f"{hp_ratio*100:.0f}%", 13, left_x + 210, y_offset + 24, WHITE, glow=True)
    
    # 复活冷却 - 如果有复活能力
    if hasattr(player, 'revive_hp') and player.revive_hp > 0:
        y_offset += 60
        revive_cooldown = getattr(player, 'revive_cooldown', 3600)
        revive_timer = getattr(player, 'revive_cooldown_timer', 0)
        revive_ratio = revive_timer / max(1, revive_cooldown)
        
        # 冷却完成与未完成的不同显示
        if revive_ratio >= 1.0:
            revive_color = (255, 215, 0)  # 金色 - 准备就绪
            status_text = "就绪"
        else:
            revive_color = (120, 120, 120)  # 灰色 - 冷却中
            status_text = f"{(1-revive_ratio)*100:.0f}%"
        
        draw_text(screen, "复活冷却", 16, left_x + 5, y_offset - 2, revive_color, align="left", glow=revive_ratio >= 1.0)
        draw_text(screen, status_text, 11, left_x + 360, y_offset - 2, revive_color, align="right")
        
        revive_bar_bg = pygame.Rect(left_x + 5, y_offset + 18, 405, 20)
        pygame.draw.rect(screen, (30, 25, 20), revive_bar_bg, border_radius=10)
        pygame.draw.rect(screen, (80, 70, 40), revive_bar_bg, 2, border_radius=10)
        
        if revive_ratio > 0:
            revive_fill_width = int(401 * min(1.0, revive_ratio))
            revive_fill = pygame.Rect(left_x + 7, y_offset + 20, revive_fill_width, 16)
            
            # 渐变填充
            for i in range(revive_fill.height):
                color_factor = i / revive_fill.height
                if revive_ratio >= 1.0:
                    # 金色渐变 + 闪烁
                    glow_intensity = int(255 * (0.8 + 0.2 * abs(math.sin(t / 300))))
                    color = (glow_intensity, int(215 * (0.7 + 0.3 * color_factor)), 0)
                else:
                    # 灰色渐变
                    color = tuple(int(c * (0.7 + 0.3 * color_factor)) for c in revive_color)
                pygame.draw.line(screen, color, (revive_fill.x, revive_fill.y + i), (revive_fill.x + revive_fill.width, revive_fill.y + i))
            
            # 完成时的光芒效果
            if revive_ratio >= 1.0:
                pulse_size = int(8 * abs(math.sin(t / 400)))
                pygame.draw.line(screen, (255, 255, 255, 150), 
                                (revive_fill.x + revive_fill.width - pulse_size, revive_fill.y), 
                                (revive_fill.x + revive_fill.width - pulse_size, revive_fill.y + revive_fill.height), 4)
        
        draw_text(screen, f"{min(100, revive_ratio*100):.0f}%", 13, left_x + 210, y_offset + 24, WHITE, glow=True)
    
    # 能量护盾 - 如果有
    if hasattr(player, 'barrier_current_hp') and hasattr(player, 'barrier_hp'):
        y_offset += 60
        barrier_max = getattr(player, 'barrier_hp', 50)
        barrier_current = getattr(player, 'barrier_current_hp', 0)
        barrier_ratio = barrier_current / max(1, barrier_max)
        
        draw_text(screen, "能量护盾", 16, left_x + 5, y_offset - 2, (0, 200, 255), align="left", glow=True)
        draw_text(screen, f"{int(barrier_current)}/{int(barrier_max)}", 11, left_x + 360, y_offset - 2, GRAY, align="right")
        
        barrier_bar_bg = pygame.Rect(left_x + 5, y_offset + 18, 405, 20)
        pygame.draw.rect(screen, (0, 20, 30), barrier_bar_bg, border_radius=10)
        pygame.draw.rect(screen, (0, 100, 150), barrier_bar_bg, 2, border_radius=10)
        
        if barrier_ratio > 0:
            barrier_fill_width = int(401 * barrier_ratio)
            barrier_fill = pygame.Rect(left_x + 7, y_offset + 20, barrier_fill_width, 16)
            
            # 科技蓝渐变
            for i in range(barrier_fill.height):
                color_factor = i / barrier_fill.height
                color = (0, int(200 * (0.7 + 0.3 * color_factor)), int(255 * (0.8 + 0.2 * color_factor)))
                pygame.draw.line(screen, color, (barrier_fill.x, barrier_fill.y + i), 
                               (barrier_fill.x + barrier_fill.width, barrier_fill.y + i))
            
            # 能量流动效果
            flow_offset = int((t / 10) % barrier_fill.width)
            pygame.draw.line(screen, (100, 255, 255, 180), 
                           (barrier_fill.x + flow_offset, barrier_fill.y), 
                           (barrier_fill.x + flow_offset, barrier_fill.y + barrier_fill.height), 2)
        
        draw_text(screen, f"{barrier_ratio*100:.0f}%", 13, left_x + 210, y_offset + 24, WHITE, glow=True)
    
    # 护盾 - 增强版
    y_offset += 60
    shield_ratio = player.shield / max(1, player.max_hp)
    
    draw_text(screen, "护盾值", 16, left_x + 5, y_offset - 2, CYBER_AMBER, align="left", glow=True)
    draw_text(screen, f"{int(player.shield)}/{int(player.max_hp)}", 11, left_x + 360, y_offset - 2, GRAY, align="right")
    
    shield_bar_bg = pygame.Rect(left_x + 5, y_offset + 18, 405, 20)
    pygame.draw.rect(screen, (30, 25, 15), shield_bar_bg, border_radius=10)
    pygame.draw.rect(screen, (100, 80, 30), shield_bar_bg, 2, border_radius=10)
    
    if shield_ratio > 0:
        shield_fill_width = int(401 * shield_ratio)
        shield_fill = pygame.Rect(left_x + 7, y_offset + 20, shield_fill_width, 16)
        for i in range(shield_fill.height):
            color_factor = i / shield_fill.height
            color = (
                int(255 - 100 * color_factor),
                int(200 - 50 * color_factor),
                int(50 + 50 * color_factor)
            )
            pygame.draw.line(screen, color, (shield_fill.x, shield_fill.y + i), (shield_fill.x + shield_fill.width, shield_fill.y + i))
        
        # 能量波纹
        wave_x = int((t / 8) % 20)
        for wx in range(shield_fill.x, shield_fill.x + shield_fill.width, 20):
            if wx + wave_x < shield_fill.x + shield_fill.width:
                pygame.draw.line(screen, (255, 255, 150, 100), 
                               (wx + wave_x, shield_fill.y), 
                               (wx + wave_x, shield_fill.y + shield_fill.height), 1)
    
    draw_text(screen, f"{shield_ratio*100:.0f}%", 13, left_x + 210, y_offset + 24, WHITE, glow=True)
    
    # 底部属性组 - 紧凑卡片式（扩展到8个属性）
    # 确保不会超出面板底部 - 限制最大Y位置
    max_bottom_y = panel_y + panel_h - 30  # 面板底部留30像素边距
    stats_y = min(y_offset + 55, max_bottom_y - 200)  # 减少间距从70到55，确保至少200像素显示属性
    
    # 新增属性检测
    wingmen_count = len(getattr(player, 'wingmen', []))
    turret_count = getattr(player, 'turret_count', 0) if hasattr(player, 'has_turrets') and player.has_turrets else 0
    
    # 火力 & 暴击率 - 并排显示（4行x2列=8个属性）
    stat_cards = [
        ("火力", f"{player.damage:.1f}", MAGENTA),
        ("暴击", f"{player.crit_chance * 100:.0f}%", (255, 100, 50)),
        ("穿透", f"{player.piercing if hasattr(player, 'piercing') else 0}", CYAN),
        ("弹数", f"{player.bullet_count if hasattr(player, 'bullet_count') else 1}", CYBER_LIME),
        ("闪避", f"{getattr(player, 'dodge_chance', 0) * 100:.0f}%", (150, 255, 200)),
        ("减伤", f"{getattr(player, 'damage_reduction', 0) * 100:.0f}%", (100, 200, 255)),
        ("无人机", f"{wingmen_count}", (255, 200, 100)),
        ("炮塔", f"{turret_count}", (200, 150, 255))
    ]
    
    for i, (name, value, color) in enumerate(stat_cards):
        col = i % 2
        row = i // 2
        
        card_x = left_x + col * 210
        card_y = stats_y + row * 43  # 减少行高从48到43
        
        # 小卡片背景
        mini_card = pygame.Rect(card_x - 5, card_y - 5, 200, 44)
        mini_surf = pygame.Surface((mini_card.width, mini_card.height), pygame.SRCALPHA)
        pygame.draw.rect(mini_surf, (30, 30, 40, 180), mini_surf.get_rect(), border_radius=8)
        safe_blit(screen, mini_surf, (mini_card.x, mini_card.y))
        
        # 边框
        glow_val = int(150 + 50 * math.sin(t / 600 + i * 0.8))
        pygame.draw.rect(screen, (*color[:3], glow_val), mini_card, 2, border_radius=8)
        
        # 名称 - 左对齐
        draw_text(screen, name, 16, card_x + 5, card_y + 3, (200, 200, 200), align="left")
        
        # 数值 - 右对齐
        draw_text(screen, value, 20, card_x + 175, card_y + 4, color, glow=True, align="right")

    # 【右侧】卡牌系统 - 玻璃态射质感
    right_x = panel_x + 540
    right_y = top_y
    
    # 右侧卡片背景
    right_card = pygame.Rect(right_x - 15, right_y - 15, 540, 420)
    right_surf = pygame.Surface((right_card.width, right_card.height), pygame.SRCALPHA)
    pygame.draw.rect(right_surf, (50, 25, 50, 200), right_surf.get_rect(), border_radius=12)
    safe_blit(screen, right_surf, (right_card.x, right_card.y))
    
    # 卡片边框 - 紫色系
    border_color2 = (int(200 + 50 * math.sin(t / 500)), 0, 255)
    pygame.draw.rect(screen, border_color2, right_card, 2, border_radius=12)
    
    # 顶部高光
    pygame.draw.line(screen, (255, 255, 255, 50), 
                    (right_card.x + 20, right_card.y + 5), 
                    (right_card.x + right_card.width - 20, right_card.y + 5), 2)
    
    draw_text(screen, "战术卡牌系统", 22, right_x, right_y, MAGENTA, glow=True, align="left")
    
    # 获取卡牌数据
    upgrade_manager = getattr(player, 'upgrade_manager', None)
    owned_cards = upgrade_manager.owned_cards if upgrade_manager else {}
    active_synergies = upgrade_manager.active_synergies if upgrade_manager else []
    archetype_counts = upgrade_manager.archetype_counts if upgrade_manager else {}
    
    buff_start_y = right_y + 50
    
    if not owned_cards:
        # 无卡牌提示 - 更有设计感
        no_buff_y = buff_start_y + 150
        draw_text(screen, "╳", 48, right_x + 240, no_buff_y - 20, (80, 80, 80), align="center")
        draw_text(screen, "暂无战术卡牌", 18, right_x + 240, no_buff_y + 30, GRAY, align="center")
        draw_text(screen, "升级获取卡牌", 14, right_x + 240, no_buff_y + 55, (100, 100, 100), align="center")
    else:
        # ===== 第一区：协同效果显示 =====
        if active_synergies:
            synergy_section_y = buff_start_y
            draw_text(screen, "▶ 激活协同", 16, right_x, synergy_section_y, CYBER_AMBER, glow=True, align="left")
            
            from roguelite import SYNERGY_RULES
            for i, synergy_id in enumerate(active_synergies[:2]):  # 最多显示2个
                synergy = SYNERGY_RULES.get(synergy_id, {})
                synergy_name = synergy.get("name", synergy_id)
                synergy_desc = synergy.get("desc", "")
                synergy_color = synergy.get("visual", {}).get("color", CYBER_LIME)
                
                syn_y = synergy_section_y + 25 + i * 42
                
                # 协同卡片背景
                syn_rect = pygame.Rect(right_x - 5, syn_y - 5, 510, 38)
                syn_surf = pygame.Surface((syn_rect.width, syn_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(syn_surf, (60, 40, 80, 180), syn_surf.get_rect(), border_radius=8)
                safe_blit(screen, syn_surf, (syn_rect.x, syn_rect.y))
                
                # 边框 - 金色发光
                glow_val = int(200 + 55 * math.sin(t / 400 + i * 0.8))
                pygame.draw.rect(screen, (*synergy_color, glow_val), syn_rect, 2, border_radius=8)
                
                # 协同名称
                draw_text(screen, f"⚡ {synergy_name}", 14, right_x + 5, syn_y + 2, synergy_color, glow=True, align="left")
                
                # 协同描述
                draw_text(screen, synergy_desc, 10, right_x + 5, syn_y + 20, (200, 200, 200), align="left")
            
            # 更新卡牌列表起始位置
            buff_start_y = synergy_section_y + 25 + len(active_synergies[:2]) * 42 + 20
        
        # ===== 第二区：原型统计 =====
        archetype_y = buff_start_y
        draw_text(screen, "▶ 构筑类型", 16, right_x, archetype_y, CYAN, glow=True, align="left")
        
        # 原型翻译
        archetype_names = {
            "barrage": "弹幕流",
            "sniper": "狙击流",
            "control": "控制流",
            "summon": "召唤流"
        }
        
        # 显示原型数量 - 4个并排小卡片
        archetype_items = [
            (archetype, archetype_names.get(archetype, archetype), count)
            for archetype, count in archetype_counts.items()
        ]
        
        for i, (archetype, name, count) in enumerate(archetype_items[:4]):
            col = i % 4
            arch_x = right_x + col * 125
            arch_y = archetype_y + 25
            
            # 小卡片
            arch_rect = pygame.Rect(arch_x - 5, arch_y - 5, 115, 30)
            arch_surf = pygame.Surface((arch_rect.width, arch_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(arch_surf, (40, 50, 60, 160), arch_surf.get_rect(), border_radius=6)
            safe_blit(screen, arch_surf, (arch_rect.x, arch_rect.y))
            pygame.draw.rect(screen, CYAN, arch_rect, 1, border_radius=6)
            
            # 显示名称和数量
            draw_text(screen, name, 11, arch_x + 2, arch_y + 2, (200, 200, 200), align="left")
            draw_text(screen, f"×{count}", 14, arch_x + 95, arch_y + 4, CYAN, glow=True, align="right")
        
        # ===== 第三区：拥有卡牌列表 =====
        card_list_y = archetype_y + 70
        draw_text(screen, "▶ 拥有卡牌", 16, right_x, card_list_y, MAGENTA, glow=True, align="left")
        
        from roguelite import BASE_CARDS, MODIFIER_CARDS
        
        # 获取卡牌数据并排序（按等级降序）
        card_display_list = []
        for card_id, card_obj in owned_cards.items():
            card_data = BASE_CARDS.get(card_id) or MODIFIER_CARDS.get(card_id)
            if card_data:
                card_name = card_data.get("name", card_id)
                card_level = card_obj.level
                card_category = card_data.get("category", "modifier")
                
                # 分类颜色
                category_colors = {
                    "attack": (255, 100, 100),
                    "defense": (100, 200, 255),
                    "special": (200, 100, 255),
                    "system": (100, 255, 150),
                    "modifier": CYBER_AMBER
                }
                card_color = category_colors.get(card_category, GRAY)
                
                card_display_list.append((card_name, card_level, card_color))
        
        # 按等级排序
        card_display_list.sort(key=lambda x: x[1], reverse=True)
        
        # 显示卡牌 - 2列布局，支持滚动
        max_visible_rows = 7  # 最多显示7行（14张卡）
        start_index = stats_panel_card_scroll
        end_index = min(start_index + max_visible_rows * 2, len(card_display_list))
        
        for i, (card_name, card_level, card_color) in enumerate(card_display_list[start_index:end_index]):
            col = i % 2
            row = i // 2
            
            card_x = right_x + col * 255
            card_y = card_list_y + 25 + row * 38
            
            # 卡片背景 - 玻璃质感
            bar_rect = pygame.Rect(card_x - 8, card_y - 8, 245, 34)
            card_surf = pygame.Surface((bar_rect.width, bar_rect.height), pygame.SRCALPHA)
            
            # 渐变背景
            for dy in range(bar_rect.height):
                grad_alpha = int(100 + 60 * (1 - dy / bar_rect.height))
                base_color = card_color[:3] if len(card_color) == 3 else card_color[:3]
                pygame.draw.line(card_surf, (base_color[0], base_color[1], base_color[2], grad_alpha // 4), 
                               (0, dy), (bar_rect.width, dy))
            safe_blit(screen, card_surf, (bar_rect.x, bar_rect.y))
            
            # 边框 - 发光
            glow_intensity = int(180 + 75 * math.sin(t / 600 + i * 0.6))
            glow_color = tuple(min(255, c) for c in card_color[:3]) if len(card_color) == 3 else card_color[:3]
            pygame.draw.rect(screen, (*glow_color, glow_intensity), bar_rect, 2, border_radius=8)
            
            # 高光
            pygame.draw.line(screen, (255, 255, 255, 60), 
                           (bar_rect.x + 10, bar_rect.y + 3), 
                           (bar_rect.x + bar_rect.width - 10, bar_rect.y + 3), 1)
            
            # 等级标签 - 左侧圆形
            level_circle_x = card_x - 2
            level_circle_y = card_y + 5
            pygame.draw.circle(screen, (*card_color[:3], 100), (level_circle_x, level_circle_y), 14)
            pygame.draw.circle(screen, card_color, (level_circle_x, level_circle_y), 14, 2)
            draw_text(screen, f"{card_level}", 14, level_circle_x, level_circle_y - 7, WHITE, glow=True, align="center")
            
            # 卡牌名称
            draw_text(screen, card_name, 13, card_x + 22, card_y, WHITE, align="left", glow=True)
            
            # 等级星星
            star_text = "★" * min(card_level, 3)
            draw_text(screen, star_text, 11, card_x + 22, card_y + 16, card_color, align="left")
        
        # 滚动提示
        total_cards = len(card_display_list)
        if total_cards > max_visible_rows * 2:
            scroll_hint_y = card_list_y + 25 + max_visible_rows * 38 + 5
            # 上翻提示
            if stats_panel_card_scroll > 0:
                draw_text(screen, "▲ 滚轮向上", 11, right_x + 250, card_list_y + 10, (150, 150, 150), align="center")
            # 下翻提示
            if stats_panel_card_scroll + max_visible_rows * 2 < total_cards:
                draw_text(screen, "▼ 滚轮向下", 11, right_x + 250, scroll_hint_y, (150, 150, 150), align="center")
            # 显示进度
            progress_text = f"{start_index + 1}-{end_index} / {total_cards}"
            draw_text(screen, progress_text, 10, right_x + 470, card_list_y + 5, GRAY, align="right")

    # 底部提示条 - 动态背景
    hint_y = panel_y + panel_h - 45
    hint_bg = pygame.Rect(panel_x + 30, hint_y - 10, panel_w - 60, 35)
    hint_surf = pygame.Surface((hint_bg.width, hint_bg.height), pygame.SRCALPHA)
    
    # 渐变背景
    for i in range(hint_bg.height):
        alpha = int(100 - i * 2)
        pygame.draw.line(hint_surf, (0, 100, 150, alpha), (0, i), (hint_bg.width, i))
    safe_blit(screen, hint_surf, (hint_bg.x, hint_bg.y))
    
    # 边框
    pygame.draw.rect(screen, (0, 200, 255, 150), hint_bg, 2, border_radius=8)
    
    # 左右箭头动画
    arrow_offset = int(15 * math.sin(t / 300))
    arrow_alpha = int(200 + 55 * math.sin(t / 400))
    pygame.draw.polygon(screen, (0, 255, 255, arrow_alpha), [
        (panel_x + 60 - arrow_offset, hint_y + 6),
        (panel_x + 50 - arrow_offset, hint_y + 12),
        (panel_x + 60 - arrow_offset, hint_y + 18)
    ])
    pygame.draw.polygon(screen, (0, 255, 255, arrow_alpha), [
        (panel_x + panel_w - 60 + arrow_offset, hint_y + 6),
        (panel_x + panel_w - 50 + arrow_offset, hint_y + 12),
        (panel_x + panel_w - 60 + arrow_offset, hint_y + 18)
    ])
    
    # 提示文字 - 脉冲效果
    pulse_alpha = int(150 + 105 * abs(math.sin(t / 500)))
    hint_color = (0, pulse_alpha, 255)
    draw_text(screen, "按住 [TAB] 查看面板", 16, panel_rect.centerx - 100, hint_y + 2, hint_color, glow=True)
    draw_text(screen, "释放 [TAB] 恢复战斗", 16, panel_rect.centerx + 100, hint_y + 2, hint_color, glow=True)

def draw_levelup_ui():
    """绘制升级选择 UI (美化版)"""
    if not upgrade_options or len(upgrade_options) < 3:
        return
    if player is None:
        log_debug("draw_levelup_ui: player is None, skip")
        return
    
    t = pygame.time.get_ticks()
    
    # 渐变遮罩背景
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(HEIGHT):
        alpha = int(150 + 50 * (y / HEIGHT))
        overlay.fill((0, 0, 10, alpha), (0, y, WIDTH, 1))
    safe_blit(screen, overlay, (0, 0))
    
    # 动态粒子背景
    for _ in range(15):
        px = random.randint(0, WIDTH)
        py = random.randint(0, HEIGHT)
        pr = random.randint(1, 3)
        particle_alpha = int(50 + 50 * abs(math.sin(t / 1000 + px + py)))
        pygame.draw.circle(screen, (*CYAN[:3], particle_alpha), (px, py), pr)
    
    # 标题 - 发光脉冲效果
    title_scale = 1.0 + 0.1 * abs(math.sin(t / 400))
    title_alpha = int(200 + 55 * abs(math.sin(t / 500)))
    title_color = (*CYBER_AMBER[:3], title_alpha)
    draw_text(screen, "▂▃▅ 选择升级卡牌 ▅▃▂", int(48 * title_scale), WIDTH//2, 70, title_color, glow=True)
    
    # 副标题
    subtitle_alpha = int(150 + 50 * abs(math.sin(t / 300)))
    draw_text(screen, f"等级 {player.level} → {player.level + 1}", 20, WIDTH//2, 120, (*LIME[:3], subtitle_alpha))
    
    # 【新】流派统计信息
    if hasattr(player, 'upgrade_manager') and player.upgrade_manager:
        archetype_counts = {"barrage": 0, "sniper": 0, "control": 0, "summon": 0}
        for card_id, card in player.upgrade_manager.owned_cards.items():
            if hasattr(card, 'archetype'):
                arch = card.archetype
                if arch in archetype_counts:
                    archetype_counts[arch] += 1
        
        # 流派统计条
        stats_y = 145
        stats_bg = pygame.Rect(WIDTH // 2 - 350, stats_y, 700, 35)
        pygame.draw.rect(screen, (20, 25, 35, 200), stats_bg, border_radius=10)
        pygame.draw.rect(screen, CYAN, stats_bg, 2, border_radius=10)
        
        arch_colors = {
            "barrage": (255, 100, 100),
            "sniper": (100, 200, 255),
            "control": (150, 100, 255),
            "summon": (100, 255, 150)
        }
        arch_names = {
            "barrage": "弹幕",
            "sniper": "狙击",
            "control": "控制",
            "summon": "召唤"
        }
        
        x_offset = stats_bg.x + 30
        for arch, count in archetype_counts.items():
            if count > 0:
                color = arch_colors[arch]
                name = arch_names[arch]
                draw_text(screen, f"{name}×{count}", 16, x_offset, stats_bg.centery, color, glow=True)
                x_offset += 130
        
        # 推荐提示
        max_arch = max(archetype_counts, key=archetype_counts.get)
        if archetype_counts[max_arch] >= 3:
            recommend_y = stats_y + 40
            rec_text = f"主流派: {arch_names[max_arch]}流 - 建议选择同流派卡牌获得协同效果"
            draw_text(screen, rec_text, 14, WIDTH // 2, recommend_y, (255, 200, 100))
    
    # 3 个升级卡牌
    card_width = 300
    card_height = 440
    gap = 50
    total_width = 3 * card_width + 2 * gap
    start_x = (WIDTH - total_width) // 2
    start_y = 230  # 【调整】向下移动40像素为流派统计腾出空间
    
    try:
        from roguelite import BASE_CARDS, MODIFIER_CARDS
        
        for i, card_id in enumerate(upgrade_options):
            # 查找卡牌 (可能在基础卡或修饰符卡中)
            card_data = BASE_CARDS.get(card_id) or MODIFIER_CARDS.get(card_id)
            if not card_data:
                continue
            
            card_x = start_x + i * (card_width + gap)
            
            # 卡牌浮动动画
            hover_offset = 0
            if i == upgrade_selected:
                hover_offset = int(-10 + 5 * math.sin(t / 200))
            
            card_y = start_y + hover_offset
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            
            # 稀有度颜色
            border_color = RARITY_COLORS[card_data["rarity"]]
            
            # 选中时的外发光
            if i == upgrade_selected:
                glow_radius = int(10 + 5 * abs(math.sin(t / 150)))
                for r in range(glow_radius, 0, -2):
                    alpha = int(80 * (1 - r / glow_radius))
                    glow_surf = pygame.Surface((card_width + r*2, card_height + r*2), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (*border_color[:3], alpha), (0, 0, card_width + r*2, card_height + r*2), border_radius=15)
                    safe_blit(screen, glow_surf, (card_x - r, card_y - r))
            
            # 卡牌主体 - 渐变背景
            card_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            for cy in range(card_height):
                grad_ratio = cy / card_height
                bg_r = int(20 + 30 * grad_ratio)
                bg_g = int(20 + 20 * grad_ratio)
                bg_b = int(40 + 30 * grad_ratio)
                pygame.draw.rect(card_surf, (bg_r, bg_g, bg_b, 240), (0, cy, card_width, 1))
            safe_blit(screen, card_surf, (card_x, card_y))
            
            # 边框 - 多层效果
            border_width = 5 if i == upgrade_selected else 3
            pygame.draw.rect(screen, border_color, card_rect, border_width, border_radius=12)
            
            # 内边框
            inner_rect = card_rect.inflate(-8, -8)
            inner_alpha = int(100 + 50 * abs(math.sin(t / 400 + i)))
            pygame.draw.rect(screen, (*border_color[:3], inner_alpha), inner_rect, 1, border_radius=10)
            
            # 顶部装饰条
            top_bar = pygame.Rect(card_x, card_y, card_width, 50)
            top_overlay = pygame.Surface((card_width, 50), pygame.SRCALPHA)
            top_overlay.fill((*border_color[:3], 80))
            safe_blit(screen, top_overlay, (card_x, card_y))
            
            # 稀有度标签 - 六边形背景
            rarity_text = RARITY_NAMES[card_data["rarity"] + 1]
            rarity_bg = pygame.Surface((140, 35), pygame.SRCALPHA)
            pygame.draw.polygon(rarity_bg, (*border_color[:3], 200), [
                (10, 0), (130, 0), (140, 17.5), (130, 35), (10, 35), (0, 17.5)
            ])
            safe_blit(screen, rarity_bg, (card_rect.centerx - 70, card_y + 10))
            draw_text(screen, f"★ {rarity_text} ★", 18, card_rect.centerx, card_y + 22, WHITE, glow=True)
            
            # 顶部装饰图标
            icon_y = card_y + 80
            category = card_data.get("category", "")
            if category == "attack":
                # 三角形（攻击）
                pts = [(card_rect.centerx, icon_y - 15), (card_rect.centerx - 15, icon_y + 10), (card_rect.centerx + 15, icon_y + 10)]
                pygame.draw.polygon(screen, (*border_color[:3], 100), pts)
            elif category == "defense":
                # 盾牌形状（防御）
                pygame.draw.ellipse(screen, (*border_color[:3], 100),
                                  (card_rect.centerx - 20, icon_y - 10, 40, 30))
            elif category == "special":
                # 星形（特殊）
                for j in range(5):
                    angle = j * 2 * math.pi / 5 - math.pi / 2
                    px = card_rect.centerx + 20 * math.cos(angle)
                    py = icon_y + 20 * math.sin(angle)
                    pygame.draw.line(screen, (*border_color[:3], 100),
                                   (card_rect.centerx, icon_y), (px, py), 2)
            else:
                # 圆形（默认）
                pygame.draw.circle(screen, (*border_color[:3], 100),
                                 (card_rect.centerx, icon_y), 25)
            
            # 卡牌名称 - 加粗效果
            name_y = card_y + 150
            draw_text(screen, card_data["name"], 26, card_rect.centerx, name_y, WHITE, glow=True)
            draw_text(screen, card_data["name"], 26, card_rect.centerx + 1, name_y + 1, (*WHITE[:3], 100))
            
            # 分隔线
            line_y = name_y + 30
            pygame.draw.line(screen, (*border_color[:3], 150), 
                (card_x + 30, line_y), (card_x + card_width - 30, line_y), 2)
            
            # 描述 - 更好的排版
            desc_lines = [card_data["desc"][k:k+16] for k in range(0, len(card_data["desc"]), 16)]
            desc_y = line_y + 25
            for line in desc_lines[:3]:  # 最多3行
                draw_text(screen, line, 18, card_rect.centerx, desc_y, (200, 200, 220))
                desc_y += 28
            
            # 效果预览
            effect_y = card_rect.bottom - 90
            effect_text = "效果："
            if "base_effect" in card_data:
                effects = []
                for k, v in list(card_data["base_effect"].items())[:2]:
                    if "mult" in k:
                        effects.append(f"+{int((v-1)*100)}%")
                    elif isinstance(v, (int, float)) and v > 0:
                        effects.append(f"+{v}")
                if effects:
                    effect_text += " ".join(effects)
            draw_text(screen, effect_text, 16, card_rect.centerx, effect_y, CYBER_AMBER)
            
            # 选择提示 - 动态箭头
            if i == upgrade_selected:
                arrow_offset = int(3 * math.sin(t / 150))
                select_y = card_rect.bottom - 40
                draw_text(screen, "◄", 24, card_rect.centerx - 60 + arrow_offset, select_y, LIME, glow=True)
                draw_text(screen, "已选中", 22, card_rect.centerx, select_y, LIME, glow=True)
                draw_text(screen, "►", 24, card_rect.centerx + 60 - arrow_offset, select_y, LIME, glow=True)
                
                # 选中闪光
                if t % 1000 < 100:
                    flash_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
                    flash_alpha = int(50 * (1 - (t % 1000) / 100))
                    flash_surf.fill((*WHITE[:3], flash_alpha))
                    safe_blit(screen, flash_surf, (card_x, card_y))
            
            # 悬停时的数字序号
            number_color = border_color if i == upgrade_selected else (100, 100, 120)
            draw_text(screen, str(i + 1), 32, card_x + 25, card_y + card_height - 25, number_color, glow=True)
    
    except ImportError as e:
        draw_text(screen, f"ERROR: 无法加载卡牌库 {e}", 24, WIDTH//2, HEIGHT//2, RED)
    
    # 底部提示 - 分段颜色
    hint_y = HEIGHT - 60
    draw_text(screen, "◄ ►", 20, WIDTH//2 - 200, hint_y, CYAN, glow=True)
    draw_text(screen, "切换", 18, WIDTH//2 - 170, hint_y, WHITE)
    draw_text(screen, "ENTER", 20, WIDTH//2 - 60, hint_y, LIME, glow=True)
    draw_text(screen, "确认", 18, WIDTH//2 - 20, hint_y, WHITE)
    draw_text(screen, "鼠标", 20, WIDTH//2 + 80, hint_y, CYBER_AMBER, glow=True)
    draw_text(screen, "点击选择", 18, WIDTH//2 + 130, hint_y, WHITE)



# ==============================================================================
#   主循环
# ==============================================================================
while True:
    try:
        clock.tick(FPS)
        music_director.update()
        update_dynamic_game_music()
        if music_library_status_timer > 0:
            music_library_status_timer -= 1
            if music_library_status_timer == 0:
                music_library_status_msg = ""
        if game_state in ("menu", "audio_hub", "music_library", "sound_lab") and music_director.current_state != "menu":
            music_director.set_state("menu", intensity=0.25)
        screen.fill(CYBER_DEEP_BLACK)  # 深空黑背景
        
        # 绘制背景（游戏或Boss战斗）
        if game_state == "game" or game_state == "boss_challenge_play":
            # 使用Boss主题背景（如果有Boss）
            if boss:
                draw_boss_themed_background(screen, boss, pygame.time.get_ticks())
            else:
                draw_tactical_grid(screen)
        
        try:
            bg_manager.update(boss_type=boss.type if boss else None, warning=(boss_manager.pending or boss_manager.warning_timer > 0))
            bg_manager.draw(screen)
        except Exception as e:
            log_error(f"BG Manager error: {e}")
        if arsenal_msg_timer > 0: arsenal_msg_timer -= 1
        
        # ========== Boss挑战模式：持续按键处理 ==========
        if game_state == "boss_challenge":
            keys = pygame.key.get_pressed()
            # 初始延迟：100ms，重复速率：60ms
            initial_delay = 6  # 100ms at 60FPS
            repeat_rate = 3    # 60ms at 60FPS
            
            if keys[pygame.K_UP]:
                boss_challenge_key_repeat["up"] += 1
                if boss_challenge_key_repeat["up"] == 1 or (boss_challenge_key_repeat["up"] > initial_delay and (boss_challenge_key_repeat["up"] - initial_delay) % repeat_rate == 0):
                    boss_challenge_selected = max(0, boss_challenge_selected - 1)
                    sound_mgr.play("select")
            else:
                boss_challenge_key_repeat["up"] = 0
            
            if keys[pygame.K_DOWN]:
                boss_challenge_key_repeat["down"] += 1
                if boss_challenge_key_repeat["down"] == 1 or (boss_challenge_key_repeat["down"] > initial_delay and (boss_challenge_key_repeat["down"] - initial_delay) % repeat_rate == 0):
                    boss_challenge_selected = min(len(boss_challenge_order)-1, boss_challenge_selected + 1)
                    sound_mgr.play("select")
            else:
                boss_challenge_key_repeat["down"] = 0
            
            if keys[pygame.K_LEFT]:
                boss_challenge_key_repeat["left"] += 1
                if boss_challenge_key_repeat["left"] == 1 and boss_challenge_selected > 0:
                    boss_challenge_swap_timer = 15
                    boss_challenge_order[boss_challenge_selected], boss_challenge_order[boss_challenge_selected-1] = boss_challenge_order[boss_challenge_selected-1], boss_challenge_order[boss_challenge_selected]
                    boss_challenge_selected -= 1
                    sound_mgr.play("select")
            else:
                boss_challenge_key_repeat["left"] = 0
            
            if keys[pygame.K_RIGHT]:
                boss_challenge_key_repeat["right"] += 1
                if boss_challenge_key_repeat["right"] == 1 and boss_challenge_selected < len(boss_challenge_order)-1:
                    boss_challenge_swap_timer = 15
                    boss_challenge_order[boss_challenge_selected], boss_challenge_order[boss_challenge_selected+1] = boss_challenge_order[boss_challenge_selected+1], boss_challenge_order[boss_challenge_selected]
                    boss_challenge_selected += 1
                    sound_mgr.play("select")
            else:
                boss_challenge_key_repeat["right"] = 0
        
        # ========== Boss挑战模式飞机选择：持续按键处理 ==========
        if game_state == "boss_challenge_select_plane":
            keys = pygame.key.get_pressed()
            initial_delay = 20  # 增加到约333ms，避免误触
            repeat_rate = 8     # 增加到约133ms，减慢连续切换速度
            
            if keys[pygame.K_LEFT]:
                boss_challenge_key_repeat["left"] += 1
                if boss_challenge_key_repeat["left"] == 1 or (boss_challenge_key_repeat["left"] > initial_delay and (boss_challenge_key_repeat["left"] - initial_delay) % repeat_rate == 0):
                    current_plane_idx = (current_plane_idx - 1) % len(plane_keys)
                    sound_mgr.play("select")
            else:
                boss_challenge_key_repeat["left"] = 0
            
            if keys[pygame.K_RIGHT]:
                boss_challenge_key_repeat["right"] += 1
                if boss_challenge_key_repeat["right"] == 1 or (boss_challenge_key_repeat["right"] > initial_delay and (boss_challenge_key_repeat["right"] - initial_delay) % repeat_rate == 0):
                    current_plane_idx = (current_plane_idx + 1) % len(plane_keys)
                    sound_mgr.play("select")
            else:
                boss_challenge_key_repeat["right"] = 0
        
        events = pygame.event.get()
        mx, my = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.QUIT:
                # 在退出前保存成就数据
                if player and hasattr(player, 'achievement_manager'):
                    player.achievement_manager.save_to_file()
                pygame.quit(); sys.exit()
            
            # --- 滚轮事件 (通用) ---
            if event.type == pygame.MOUSEWHEEL:
                if room_manager and show_full_map and game_state in ["game", "boss_challenge_play"]:
                    room_manager.adjust_map_zoom(event.y * 0.08)
                    continue
                # Boss挑战模式：滚轮滚动列表
                if game_state == "boss_challenge":
                    if event.y > 0:  # 向上滚动
                        boss_challenge_selected = max(0, boss_challenge_selected - 1)
                    elif event.y < 0:  # 向下滚动
                        boss_challenge_selected = min(len(boss_challenge_order) - 1, boss_challenge_selected + 1)
                    sound_mgr.play("select")
                    continue
                # 属性面板滚动（TAB暂停时）
                if tab_paused and game_state in ["game", "boss_challenge_play"]:
                    if hasattr(player, 'upgrade_manager') and player.upgrade_manager:
                        owned_cards = player.upgrade_manager.owned_cards
                        max_scroll = max(0, len(owned_cards) - 14)  # 14张可见
                        stats_panel_card_scroll = max(0, min(stats_panel_card_scroll - event.y * 2, max_scroll))
                elif game_state == "customization":
                    mx, my = pygame.mouse.get_pos()
                    if mx < 330:
                        # 飞机列表滚动
                        customization_plane_scroll_y = max(0, customization_plane_scroll_y - event.y * 30)
                    else:
                        # 涂装列表滚动
                        customization_scroll_y = max(0, customization_scroll_y - event.y * 30)
                elif game_state == "codex":
                    if codex_tab == 0:
                        total_items = len(plane_keys)
                    elif codex_tab == 1:
                        total_items = len(BOSS_DB)
                    else:  # codex_tab == 2
                        from enemy_manager import enemy_type_manager
                        total_items = len(enemy_type_manager.get_regular_types())
                    content_h = total_items * 45
                    view_h = CODEX_UI['list_view'].height
                    max_scroll = max(0, content_h - view_h)
                    codex_scroll_y = max(0, min(codex_scroll_y - event.y * 30, max_scroll))
                    
                elif game_state == "arsenal":
                    # 新增：武器库滚动逻辑
                    total_items = len(arsenal_save_data["weapons"])
                    item_h = 60
                    content_h = total_items * item_h
                    view_h = ARSENAL_UI['list_area'].height
                    max_scroll = max(0, content_h - view_h)
                    arsenal_scroll_y = max(0, min(arsenal_scroll_y - event.y * 30, max_scroll))
                    
                elif game_state == "background_settings":
                    # 背景设置分页切换（鼠标滚轮）
                    from systems import BackgroundManager
                    bg_count = len(BackgroundManager.BG_STYLES)
                    cards_per_page = 8
                    total_pages = (bg_count + cards_per_page - 1) // cards_per_page
                    
                    if event.y < 0:  # 向上滚动 - 下一页
                        background_settings_page = min(background_settings_page + 1, total_pages - 1)
                    else:  # 向下滚动 - 上一页
                        background_settings_page = max(background_settings_page - 1, 0)
                
                elif game_state in ["select_plane", "boss_challenge_select_plane"]:
                    # 飞机选择界面滚动
                    card_h = 50
                    card_gap = 6
                    content_y = 90
                    content_h_val = HEIGHT - 170
                    list_inner_h = content_h_val - 48
                    max_visible = list_inner_h // (card_h + card_gap)
                    total_planes = len(plane_keys)
                    
                    if event.y > 0:  # 向上滚动
                        current_plane_idx = max(0, current_plane_idx - 1)
                    elif event.y < 0:  # 向下滚动
                        current_plane_idx = min(total_planes - 1, current_plane_idx + 1)
                    sound_mgr.play("select")
                    
                elif game_state == "achievements":
                    # 成就墙滚动（参数与绘制一致）
                    achievement_mgr = get_cached_achievement_mgr()
                    if achievement_mgr:
                        if achievement_category == "all":
                            filtered = list(achievement_mgr.achievements.values())
                        else:
                            filtered = achievement_mgr.get_achievements_by_category(achievement_category)
                        # 计算grid参数（与绘制一致）
                        grid_cell = 95
                        grid_gap = 12
                        MARGIN = 30
                        wall_w = int((WIDTH - MARGIN * 3) * 0.58)
                        grid_cols = max(1, int((wall_w - 40) // (grid_cell + grid_gap)))
                        rows = (len(filtered) + grid_cols - 1) // grid_cols
                        # 计算内容和可见高度（与绘制一致）
                        HEADER_H, STATS_H, TAB_H, FOOTER_H, CONTENT_GAP = 70, 45, 45, 70, 8
                        content_top = MARGIN + HEADER_H + STATS_H + TAB_H + CONTENT_GAP
                        wall_h = HEIGHT - MARGIN - content_top - FOOTER_H
                        view_h = wall_h - TAB_H - 60
                        content_h = rows * (grid_cell + grid_gap)
                        max_scroll = max(0, content_h - view_h)
                        achievement_scroll_y = max(0, min(achievement_scroll_y - event.y * 40, max_scroll))

            # --- 键盘事件 ---
            if event.type == pygame.KEYDOWN:
                # 【新】游戏结束时按R快速重开
                if game_state == "gameover" and event.key == pygame.K_r:
                    reset_game()
                    game_state = "game"
                    music_director.set_state("combat", intensity=0.8, immediate=True, force=True)
                    sound_mgr.play("select")
                    continue
                
                # 菜单子页：ESC 返回主菜单
                if event.key == pygame.K_ESCAPE and game_state in ["arsenal", "gallery", "codex", "leaderboard", "background_settings", "settings", "achievements", "customization"]:
                    game_state = "menu"
                    main_menu_selected = 0
                    music_director.set_state("menu", intensity=0.25)
                    sound_mgr.play("select")
                    continue
                
                # 背景设置界面 键盘控制
                if game_state == "background_settings":
                    from systems import BackgroundManager
                    bg_count = len(BackgroundManager.BG_STYLES)
                    cards_per_row = 4
                    cards_per_page = 8
                    total_pages = (bg_count + cards_per_page - 1) // cards_per_page
                    
                    if event.key == pygame.K_LEFT:
                        background_settings_selected = (background_settings_selected - 1) % bg_count
                        sound_mgr.play("select")
                    elif event.key == pygame.K_RIGHT:
                        background_settings_selected = (background_settings_selected + 1) % bg_count
                        sound_mgr.play("select")
                    elif event.key == pygame.K_UP:
                        background_settings_selected = (background_settings_selected - cards_per_row) % bg_count
                        sound_mgr.play("select")
                    elif event.key == pygame.K_DOWN:
                        background_settings_selected = (background_settings_selected + cards_per_row) % bg_count
                        sound_mgr.play("select")
                    
                    # 自动切换到选中项所在的页
                    if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                        selected_page = background_settings_selected // cards_per_page
                        background_settings_page = selected_page
                    
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # 切换到选中的背景
                        style_keys = list(BackgroundManager.BG_STYLES.keys())
                        if 0 <= background_settings_selected < len(style_keys):
                            style_key = style_keys[background_settings_selected]
                            bg_manager.set_style(style_key)
                            save_settings(background_style=style_key)
                            sound_mgr.play("select")
                            log_info(f"背景已切换为: {style_key}")
                    continue
                
                # 飞机选择界面 键盘控制
                if game_state == "select_plane":
                    if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w):
                        current_plane_idx = (current_plane_idx - 1) % len(plane_keys)
                        sound_mgr.play("select")
                    elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s):
                        current_plane_idx = (current_plane_idx + 1) % len(plane_keys)
                        sound_mgr.play("select")
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        selected_plane = plane_keys[current_plane_idx]
                        print(f"选择飞机: {selected_plane}")
                        # player selected via keyboard
                        try:
                            print("开始reset_game...")
                            reset_game()
                            print("reset_game完成，切换到游戏状态")
                            game_state = "game"
                            # game state changed to game
                        except Exception as e:
                            print(f"❌ reset_game失败: {e}")
                            log_error(f"reset_game failed: {e}")
                            traceback.print_exc()
                            game_state = "menu"
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "mode_select"
                        sound_mgr.play("select")
                    continue

                # 升级选择 UI 键盘控制
                if levelup_ready and upgrade_options:
                    if event.key == pygame.K_LEFT:
                        upgrade_selected = (upgrade_selected - 1) % len(upgrade_options)
                        sound_mgr.play("select")
                    elif event.key == pygame.K_RIGHT:
                        upgrade_selected = (upgrade_selected + 1) % len(upgrade_options)
                        sound_mgr.play("select")
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # 玩家选择一个卡牌
                        if player and hasattr(player, 'upgrade_manager'):
                            try:
                                player.upgrade_manager.select_upgrade(upgrade_selected)
                                sound_mgr.play("levelup")
                            except Exception as e:
                                log_error(f"Failed to select upgrade: {e}")
                        # 重置升级状态并恢复游戏
                        upgrade_options = []
                        upgrade_selected = 0
                        levelup_ready = False
                        is_paused = False
                        levelup_paused = False
                        frozen_screen = None
                    continue

                # 输入名字状态键盘控制
                if game_state == "input_name":
                    # modify global player_name
                    try:
                        if event.key == pygame.K_BACKSPACE:
                            player_name = player_name[:-1]
                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            # Save to leaderboard and go back to menu
                            name = player_name.strip() or "匿名"
                            
                            # 计算存活时间
                            survival_time = (pygame.time.get_ticks() - game_stats.get("start_time", 0)) // 1000
                            
                            # 确定游戏模式
                            if boss_challenge_active or (hasattr(boss_manager, 'boss_challenge_queue') and boss_manager.boss_challenge_queue):
                                current_mode = "boss_challenge"
                            elif room_manager is not None:
                                current_mode = "roguelike"
                            else:
                                current_mode = "normal"
                            
                            # 构建完整记录
                            import datetime
                            entry = {
                                "name": name,
                                "score": final_score,
                                "plane": selected_plane,
                                "kills": game_stats.get("kills", 0),
                                "boss_kills": game_stats.get("boss_kills", 0),
                                "survival_time": survival_time,
                                "wave": wave,
                                "rooms": room_manager.total_rooms_cleared if room_manager else 0,
                                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                            
                            # 使用新的添加函数
                            add_leaderboard_entry(leaderboard_data, current_mode, entry)
                            save_leaderboard(leaderboard_data)
                            
                            # 保存成就
                            if player and hasattr(player, 'achievement_manager'):
                                player.achievement_manager.save_to_file()
                            player_name = ""
                            game_state = "menu"
                            frozen_screen = None
                        else:
                            ch = event.unicode
                            if ch and ch.isprintable() and len(player_name) < 12:
                                player_name += ch
                    except Exception as e:
                        log_error(f"input_name handler error: {e}")
                    continue

                # TAB 键按下：显示属性面板并暂停游戏（游戏中和Boss挑战模式都支持）
                if event.key == pygame.K_TAB and (game_state == "game" or game_state == "boss_challenge_play") and not levelup_ready:
                    is_paused = True
                    tab_paused = True
                    if frozen_screen is None:
                        frozen_screen = screen.copy()
                    else:
                        frozen_screen = screen.copy()
                    sound_mgr.play("select")
                    continue

                # 游戏内键盘：P 暂停 (在 game 中), ESC 在 game 中不做任何事
                if game_state == "game" or game_state == "boss_challenge_play":
                    # 商店UI输入处理（最高优先级）
                    if room_manager and room_manager.show_shop_ui:
                        if event.key == pygame.K_LEFT:
                            room_manager.shop_selected = max(0, room_manager.shop_selected - 1)
                            sound_mgr.play("select")
                        elif event.key == pygame.K_RIGHT:
                            room_manager.shop_selected = min(len(room_manager.shop_items) - 1, room_manager.shop_selected + 1)
                            sound_mgr.play("select")
                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            # 尝试购买物品
                            purchased = room_manager.try_purchase_item(room_manager.shop_selected)
                            if purchased:
                                # 应用购买的物品效果
                                item_type = purchased["type"]
                                value = purchased["value"]
                                if item_type == "heal":
                                    player.hp = min(player.max_hp, player.hp + value)
                                elif item_type == "exp":
                                    player.gain_exp(value)
                                elif item_type == "item" and item_manager:
                                    for _ in range(value):
                                        item_manager.try_spawn_drop(player.rect.centerx, player.rect.centery)
                                elif item_type == "card":
                                    for _ in range(value):
                                        player.gain_exp(player.exp_to_next_level)
                        elif event.key == pygame.K_ESCAPE:
                            # 离开商店
                            room_manager.close_shop()
                            room_rewards = room_manager._finish_room()
                            room_completion_paused = True
                            # 保持暂停状态以显示房间完成UI
                            if frozen_screen is None:
                                frozen_screen = screen.copy()
                            sound_mgr.play("select")
                    # 房间选择UI输入处理
                    elif room_manager and room_manager.show_completion_ui:
                        if event.key == pygame.K_LEFT and room_manager.available_next_rooms:
                            room_manager.selected_next_room = max(0, room_manager.selected_next_room - 1)
                            sound_mgr.play("select")
                        elif event.key == pygame.K_RIGHT and room_manager.available_next_rooms:
                            room_manager.selected_next_room = min(len(room_manager.available_next_rooms) - 1, room_manager.selected_next_room + 1)
                            sound_mgr.play("select")
                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            # 确认选择房间或进入下一地图
                            log_info(f"Enter按下 - available_next_rooms数量: {len(room_manager.available_next_rooms)}, 当前房间类型: {room_manager.current_room.room_type if room_manager.current_room else 'None'}")
                            
                            if room_manager.available_next_rooms:
                                # 有下一房间，正常选择
                                selected_room = room_manager.available_next_rooms[room_manager.selected_next_room]
                                room_manager.enter_room(selected_room.room_id)
                                room_manager.show_completion_ui = False
                                room_manager.selected_next_room = 0
                                room_manager.available_next_rooms = []
                                room_completion_paused = False
                                # 恢复游戏状态
                                is_paused = False
                                frozen_screen = None
                                sound_mgr.play("levelup")
                            elif room_manager.current_room and room_manager.current_room.room_type == RoomType.BOSS:
                                # Boss房间完成且没有下一房间
                                log_info(f"Boss房间完成检测: is_final_map={room_manager.is_final_map()}, current_map_index={room_manager.current_map_index}, total_maps={len(room_manager.map_sequence)}")
                                if not room_manager.is_final_map():
                                    # 进入下一张地图
                                    if room_manager.advance_to_next_map():
                                        room_manager.show_completion_ui = False
                                        room_completion_paused = False
                                        is_paused = False
                                        frozen_screen = None
                                        sound_mgr.play("achievement")
                                        log_info(f"进入下一张地图: {room_manager.get_theme_name()}")
                                else:
                                    # 已经是最后一张地图，真正通关
                                    room_manager.show_completion_ui = False
                                    room_completion_paused = False
                                    is_paused = False
                                    frozen_screen = None
                                    game_state = "gameover"
                                    music_director.pause_for_stinger(
                                        "stinger_victory",
                                        resume_state="victory",
                                        resume_intensity=0.7,
                                        silence_ms=1400,
                                    )
                                    sound_mgr.play("achievement")
                    elif event.key == pygame.K_m and room_manager and game_mode == "roguelike":
                        show_full_map = not show_full_map
                        if show_full_map:
                            # 打开地图时暂停游戏并冻结画面
                            map_paused = True
                            is_paused = True
                            if frozen_screen is None:
                                frozen_screen = screen.copy()
                        else:
                            # 关闭地图时恢复游戏
                            map_paused = False
                            is_paused = False
                            frozen_screen = None
                        sound_mgr.play("select")
                    # 地图缩放控制（地图打开时）
                    elif show_full_map and room_manager and game_mode == "roguelike":
                        if event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                            room_manager.adjust_map_zoom(0.08)
                            sound_mgr.play("select")
                            continue
                        elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                            room_manager.adjust_map_zoom(-0.08)
                            sound_mgr.play("select")
                            continue
                    elif is_paused:
                        if event.key == pygame.K_UP:
                            pause_menu_selected = (pause_menu_selected - 1) % 3
                            sound_mgr.play("select")
                        elif event.key == pygame.K_DOWN:
                            pause_menu_selected = (pause_menu_selected + 1) % 3
                            sound_mgr.play("select")
                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            sound_mgr.play("select")
                            if pause_menu_selected == 0:
                                is_paused = False
                            elif pause_menu_selected == 1:
                                reset_game(); is_paused = False
                            elif pause_menu_selected == 2:
                                # 保存成就并返回菜单
                                if player and hasattr(player, 'achievement_manager'):
                                    player.achievement_manager.save_to_file()
                                game_state = "menu"
                                # 菜单使用电影配乐
                                music_director.set_state("menu", intensity=0.25)
                        elif event.key == pygame.K_p:
                            is_paused = False; sound_mgr.play("select")
                        elif event.key == pygame.K_r:
                            reset_game(); is_paused = False; sound_mgr.play("select")
                    else:
                        if event.key == pygame.K_p:
                            is_paused = True; pause_menu_selected = 0; sound_mgr.play("select")
                        elif event.key == pygame.K_f:
                            player.use_ultimate()
                        elif event.key == pygame.K_g:
                            # G键释放第二大招
                            player.use_secondary_ultimate()
                        elif event.key == pygame.K_c:
                            # C键释放第三大招
                            player.use_tertiary_ultimate()
                        elif event.key == pygame.K_r:
                            # R键释放第四大招
                            player.use_quaternary_ultimate()
                        elif event.key == pygame.K_SPACE:
                            if player.skill_cd <= 0:
                                player.skill_cd = player.max_skill_cd
                                sound_mgr.play("dash")
                                create_shockwave(player.rect.center, CYAN, 20)
                                for m in mobs:
                                    if math.hypot(m.rect.centerx-player.rect.centerx, m.rect.centery-player.rect.centery) < 300:
                                        m.hp -= 200
                                        Particle(m.rect.center, CYAN)

                # 模式选择界面
                elif game_state == "mode_select":
                    if event.key == pygame.K_ESCAPE:
                        game_state = "menu"
                        sound_mgr.play("select")
                    elif event.key == pygame.K_LEFT:
                        mode_select_selected = (mode_select_selected - 1) % 3
                        sound_mgr.play("select")
                    elif event.key == pygame.K_RIGHT:
                        mode_select_selected = (mode_select_selected + 1) % 3
                        sound_mgr.play("select")
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        modes = ["normal", "roguelike", "boss_challenge"]
                        selected_mode = modes[mode_select_selected]
                        sound_mgr.play("select")
                        if selected_mode == "boss_challenge":
                            game_state = "boss_challenge"
                            boss_challenge_selected = 0
                            boss_challenge_order = list(BOSS_DB.keys())
                            log_info(f"进入Boss挑战模式")
                        else:
                            game_mode = selected_mode
                            game_state = "select_plane"
                            current_plane_idx = 0
                            log_info(f"游戏模式选择: {selected_mode}")
                
                # 主菜单导航：上下键 + Enter 确认
                elif game_state == "menu":
                    if event.key == pygame.K_UP:
                        main_menu_selected = (main_menu_selected - 1) % len(get_menu_buttons()); sound_mgr.play("select")
                    elif event.key == pygame.K_DOWN:
                        main_menu_selected = (main_menu_selected + 1) % len(get_menu_buttons()); sound_mgr.play("select")
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        buttons = get_menu_buttons()
                        if 0 <= main_menu_selected < len(buttons):
                            r, txt, col, act = buttons[main_menu_selected]
                            sound_mgr.play("select")
                            if act == "quit":
                                if player and hasattr(player, 'achievement_manager'):
                                    player.achievement_manager.save_to_file()
                                pygame.quit(); sys.exit()
                            elif act == "select_plane": game_state = "mode_select"
                            elif act == "audio_hub":
                                enter_audio_hub()
                            elif act in ["arsenal", "gallery", "codex", "leaderboard", "achievements", "customization", "background_settings", "settings"]:
                                game_state = act
                                if act == "gallery": gallery_page = 0; gallery_tab = 0
                                if act == "codex": codex_tab = 0; codex_idx = 0; codex_scroll_y = 0
                                if act == "arsenal": arsenal_scroll_y = 0; arsenal_selected_weapon_idx = -1
                                if act == "achievements": achievement_page = 0
                                if act == "customization": customization_scroll_y = 0; customization_plane_scroll_y = 0; customization_selected_plane = None; customization_tab = 0
                                if act == "background_settings": background_settings_selected = 0
                                if act == "settings": settings_dragging = None; settings_saved_timer = 0

                elif game_state == "audio_hub":
                    if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        game_state = "menu"; sound_mgr.play("select")
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        audio_hub_selected = (audio_hub_selected - 1) % len(AUDIO_HUB_OPTIONS)
                        sound_mgr.play("select")
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        audio_hub_selected = (audio_hub_selected + 1) % len(AUDIO_HUB_OPTIONS)
                        sound_mgr.play("select")
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        sound_mgr.play("select")
                        _activate_audio_hub_option(audio_hub_selected)

                elif game_state == "music_library":
                    if music_library_search_active:
                        handled = False
                        if event.key == pygame.K_ESCAPE:
                            music_library_search_active = False
                            handled = True
                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            music_library_search_active = False
                            handled = True
                        elif event.key == pygame.K_BACKSPACE:
                            set_music_library_search_query(music_library_search_query[:-1])
                            handled = True
                        elif event.key == pygame.K_DELETE:
                            set_music_library_search_query("")
                            handled = True
                        else:
                            ch = getattr(event, "unicode", "")
                            if ch and ch.isprintable() and ch not in ("\r", "\n"):
                                set_music_library_search_query(music_library_search_query + ch)
                                handled = True
                        if handled:
                            continue

                    if event.key == pygame.K_ESCAPE:
                        return_to_audio_hub_from_music_library(); sound_mgr.play("select")
                    elif event.key == pygame.K_BACKSPACE:
                        return_to_menu_from_music_library(); sound_mgr.play("select")
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        move_music_library_selection(-1); sound_mgr.play("select")
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        move_music_library_selection(1); sound_mgr.play("select")
                    elif event.key == pygame.K_q:
                        cycle_music_library_filter(-1); sound_mgr.play("select")
                    elif event.key == pygame.K_e:
                        cycle_music_library_filter(1); sound_mgr.play("select")
                    elif event.key == pygame.K_PAGEUP:
                        move_music_library_selection(-_music_library_visible_rows()); sound_mgr.play("select")
                    elif event.key == pygame.K_PAGEDOWN:
                        move_music_library_selection(_music_library_visible_rows()); sound_mgr.play("select")
                    elif event.key == pygame.K_HOME:
                        music_library_selected = 0
                        ensure_music_library_visible()
                        sound_mgr.play("select")
                    elif event.key == pygame.K_END:
                        if music_library_tracks:
                            music_library_selected = len(music_library_tracks) - 1
                            ensure_music_library_visible()
                            sound_mgr.play("select")
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        play_music_library_track(music_library_selected)
                    elif event.key == pygame.K_SPACE:
                        stop_music_library_track()
                elif game_state == "sound_lab":
                    if event.key == pygame.K_ESCAPE:
                        return_to_audio_hub_from_sound_lab(); sound_mgr.play("select")
                    elif event.key == pygame.K_BACKSPACE:
                        return_to_menu_from_sound_lab(); sound_mgr.play("select")
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        move_sound_lab_selection(-1); sound_mgr.play("select")
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        move_sound_lab_selection(1); sound_mgr.play("select")
                    elif event.key == pygame.K_q:
                        cycle_sound_lab_filter(-1); sound_mgr.play("select")
                    elif event.key == pygame.K_e:
                        cycle_sound_lab_filter(1); sound_mgr.play("select")
                    elif event.key == pygame.K_PAGEUP:
                        move_sound_lab_selection(-_sound_lab_visible_rows()); sound_mgr.play("select")
                    elif event.key == pygame.K_PAGEDOWN:
                        move_sound_lab_selection(_sound_lab_visible_rows()); sound_mgr.play("select")
                    elif event.key == pygame.K_HOME:
                        sound_lab_selected = 0
                        ensure_sound_lab_visible()
                        sound_mgr.play("select")
                    elif event.key == pygame.K_END:
                        if sound_lab_tracks:
                            sound_lab_selected = len(sound_lab_tracks) - 1
                            ensure_sound_lab_visible()
                            sound_mgr.play("select")
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        play_sound_lab_effect(sound_lab_selected)
                    elif event.key == pygame.K_SPACE:
                        stop_sound_lab_effect()
                
                # Boss挑战模式导航（仅处理Enter和Esc，上下左右由持续按键处理）
                elif game_state == "boss_challenge":
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # 先选飞机，再开始挑战 (需要至少选择1个Boss)
                        enabled_bosses = [k for k in boss_challenge_order if boss_challenge_enabled.get(k, True)]
                        if len(enabled_bosses) > 0:
                            game_state = "boss_challenge_select_plane"
                            boss_challenge_plane_selected = 0
                            sound_mgr.play("select")
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                        game_state = "menu"; main_menu_selected = 0; sound_mgr.play("select")
                    elif event.key == pygame.K_SPACE:
                        # 空格键切换当前选中Boss的启用状态
                        if boss_challenge_selected < len(boss_challenge_order):
                            bkey = boss_challenge_order[boss_challenge_selected]
                            boss_challenge_enabled[bkey] = not boss_challenge_enabled.get(bkey, True)
                            boss_challenge_preset = 0  # 切换到自定义模式
                            sound_mgr.play("select")
                    elif event.key in (pygame.K_1, pygame.K_KP1):
                        boss_challenge_preset = 0; sound_mgr.play("select")  # 自定义
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        # 快速战 - 随机3个
                        boss_challenge_preset = 1
                        boss_keys = list(BOSS_DB.keys())
                        selected = random.sample(boss_keys, min(3, len(boss_keys)))
                        boss_challenge_enabled = {k: (k in selected) for k in boss_keys}
                        sound_mgr.play("select")
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        # 标准战 - 随机5个
                        boss_challenge_preset = 2
                        boss_keys = list(BOSS_DB.keys())
                        selected = random.sample(boss_keys, min(5, len(boss_keys)))
                        boss_challenge_enabled = {k: (k in selected) for k in boss_keys}
                        sound_mgr.play("select")
                    elif event.key in (pygame.K_4, pygame.K_KP4):
                        # 持久战 - 随机10个
                        boss_challenge_preset = 3
                        boss_keys = list(BOSS_DB.keys())
                        selected = random.sample(boss_keys, min(10, len(boss_keys)))
                        boss_challenge_enabled = {k: (k in selected) for k in boss_keys}
                        sound_mgr.play("select")
                    elif event.key in (pygame.K_5, pygame.K_KP5):
                        # 全Boss战
                        boss_challenge_preset = 4
                        boss_keys = list(BOSS_DB.keys())
                        boss_challenge_enabled = {k: True for k in boss_keys}
                        sound_mgr.play("select")
                
                # Boss挑战模式飞机选择
                elif game_state == "boss_challenge_select_plane":
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # 确认选择，开始Boss挑战
                        selected_plane = plane_keys[current_plane_idx]
                        game_state = "boss_challenge_play"
                        boss_challenge_current = 0
                        boss_challenge_active = True
                        # 生成已启用Boss的挑战顺序
                        enabled_bosses = [k for k in boss_challenge_order if boss_challenge_enabled.get(k, True)]
                        boss_challenge_order[:] = enabled_bosses  # 更新为只包含启用的Boss
                        try:
                            reset_game()
                            if not boss_challenge_music_active:
                                music_director.push_state("boss_challenge", intensity=0.85, immediate=True)
                                boss_challenge_music_active = True
                            # 立即生成第一个Boss
                            if boss_challenge_active and boss_challenge_current < len(boss_challenge_order):
                                boss_type = boss_challenge_order[boss_challenge_current]
                                candidate = boss_manager.spawn_boss(player.level, boss_type=boss_type)
                                boss_challenge_current += 1
                                if candidate:
                                    boss = candidate
                                    all_sprites.add(boss)
                        except Exception as e:
                            log_error(f"Failed to start boss challenge: {e}")
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                        # 返回Boss选择时重置order为全部Boss
                        boss_challenge_order[:] = list(BOSS_DB.keys())
                        game_state = "boss_challenge"; sound_mgr.play("select")
                
                # 成就菜单导航
                elif game_state == "achievements":
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        achievement_page = max(0, achievement_page - 1); sound_mgr.play("select")
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        achievement_page += 1; sound_mgr.play("select")
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                        game_state = "menu"; main_menu_selected = 0
                
                # 涂装界面导航
                elif game_state == "customization":
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                        customization_manager.save_data()
                        game_state = "menu"; main_menu_selected = 0; sound_mgr.play("select")


            # --- 鼠标点击事件 (严格区分状态，防止冲突) ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(f"鼠标点击事件，当前状态: {game_state}, 位置: ({mx}, {my})")
                
                # 模式选择界面点击
                if game_state == "mode_select":
                    card_width = 380
                    card_height = 480
                    gap = 40
                    start_x = (WIDTH - (card_width * 3 + gap * 2)) // 2
                    card_y = 180
                    
                    # 检测模式卡片点击
                    modes = ["normal", "roguelike", "boss_challenge"]
                    for i, mode_id in enumerate(modes):
                        card_x = start_x + i * (card_width + gap)
                        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                        if card_rect.collidepoint(mx, my):
                            mode_select_selected = i  # 更新键盘选中索引
                            sound_mgr.play("select")
                            if mode_id == "boss_challenge":
                                # Boss挑战模式：进入Boss选择界面
                                game_state = "boss_challenge"
                                boss_challenge_selected = 0
                                boss_challenge_order = list(BOSS_DB.keys())
                                log_info(f"进入Boss挑战模式")
                            else:
                                # 普通模式和房间模式：选择飞机
                                game_mode = mode_id
                                game_state = "select_plane"
                                current_plane_idx = 0
                                log_info(f"游戏模式选择: {mode_id}")
                            break
                    
                    # 返回按钮
                    back_btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 60, 200, 50)
                    if back_btn_rect.collidepoint(mx, my):
                        game_state = "menu"
                        sound_mgr.play("select")
                
                # Boss挑战模式：鼠标操作
                elif game_state == "boss_challenge":
                    # 布局参数（与绘制函数一致）
                    content_y = 118
                    left_x = 28
                    left_width = 268
                    card_height = 46
                    gap = 4
                    max_visible = int((HEIGHT - 195 - 38) / (card_height + gap))
                    card_start_y = content_y + 38
                    
                    # 检测预设按钮点击
                    preset_btn_w = 95
                    preset_btn_h = 32
                    preset_start_x = WIDTH//2 - (5 * preset_btn_w + 4 * 8) // 2
                    preset_y = 72
                    preset_counts = [0, 3, 5, 10, len(BOSS_DB)]
                    
                    preset_clicked = False
                    if event.button == 1:
                        for pi in range(5):
                            btn_x = preset_start_x + pi * (preset_btn_w + 8)
                            btn_rect = pygame.Rect(btn_x, preset_y, preset_btn_w, preset_btn_h)
                            if btn_rect.collidepoint(mx, my):
                                preset_clicked = True
                                boss_challenge_preset = pi
                                boss_keys = list(BOSS_DB.keys())
                                if pi == 0:  # 自定义 - 不改变
                                    pass
                                elif pi == 4:  # 全Boss
                                    boss_challenge_enabled = {k: True for k in boss_keys}
                                else:  # 随机选择指定数量
                                    count = preset_counts[pi]
                                    selected = random.sample(boss_keys, min(count, len(boss_keys)))
                                    boss_challenge_enabled = {k: (k in selected) for k in boss_keys}
                                sound_mgr.play("select")
                                break
                    
                    # 检测Boss列表点击
                    clicked_card = False
                    if not preset_clicked:
                        for display_idx in range(min(max_visible, len(boss_challenge_order) - boss_challenge_scroll_offset)):
                            i = boss_challenge_scroll_offset + display_idx
                            card_y = card_start_y + display_idx * (card_height + gap)
                            card_rect = pygame.Rect(left_x + 8, card_y, left_width - 20, card_height)
                            
                            # 勾选框区域
                            checkbox_rect = pygame.Rect(left_x + 8 + 12, card_y + card_height // 2 - 8, 16, 16)
                            
                            if card_rect.collidepoint(mx, my):
                                clicked_card = True
                                bkey = boss_challenge_order[i]
                                
                                if checkbox_rect.collidepoint(mx, my) and event.button == 1:
                                    # 点击勾选框 - 切换启用状态
                                    boss_challenge_enabled[bkey] = not boss_challenge_enabled.get(bkey, True)
                                    boss_challenge_preset = 0  # 切换到自定义模式
                                    sound_mgr.play("select")
                                elif event.button == 1:  # 左键选择
                                    if boss_challenge_selected == i:
                                        # 双击同一项：开始挑战
                                        enabled_bosses = [k for k in boss_challenge_order if boss_challenge_enabled.get(k, True)]
                                        if len(enabled_bosses) > 0:
                                            game_state = "boss_challenge_select_plane"
                                            boss_challenge_plane_selected = 0
                                    else:
                                        boss_challenge_selected = i
                                    sound_mgr.play("select")
                                elif event.button == 3:  # 右键切换启用
                                    boss_challenge_enabled[bkey] = not boss_challenge_enabled.get(bkey, True)
                                    boss_challenge_preset = 0
                                    sound_mgr.play("select")
                                break
                    
                    # 检测开始挑战按钮
                    if not clicked_card and not preset_clicked and event.button == 1:
                        btn_width = 240
                        btn_height = 50
                        btn_x = WIDTH // 2 - btn_width // 2
                        btn_y = HEIGHT - 60
                        start_btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
                        if start_btn_rect.collidepoint(mx, my):
                            enabled_bosses = [k for k in boss_challenge_order if boss_challenge_enabled.get(k, True)]
                            if len(enabled_bosses) > 0:
                                game_state = "boss_challenge_select_plane"
                                boss_challenge_plane_selected = 0
                                sound_mgr.play("select")
                
                elif game_state == "menu":
                    buttons = get_menu_buttons()
                    for idx, (r, txt, col, act) in enumerate(buttons):
                        if r.collidepoint(mx, my):
                            main_menu_selected = idx  # 更新键盘选中索引
                            log_info(f"Menu button clicked: {txt} (action={act})")
                            sound_mgr.play("select")
                            if act == "quit":
                                if player and hasattr(player, 'achievement_manager'):
                                    player.achievement_manager.save_to_file()
                                pygame.quit(); sys.exit()
                            elif act == "select_plane":
                                game_state = "mode_select"  # 先选择模式
                                log_info(f"Game state changed to: {game_state}")
                            elif act == "audio_hub":
                                enter_audio_hub()
                                log_info("Game state changed to: audio_hub")
                            elif act in ["arsenal", "gallery", "codex", "leaderboard", "achievements", "customization", "background_settings", "settings"]: 
                                game_state = act
                                if act == "gallery": gallery_page = 0; gallery_tab = 0
                                if act == "codex": codex_tab = 0; codex_idx = 0; codex_scroll_y = 0
                                if act == "arsenal": arsenal_scroll_y = 0; arsenal_selected_weapon_idx = -1
                                if act == "achievements": achievement_page = 0
                                if act == "customization": customization_scroll_y = 0; customization_plane_scroll_y = 0; customization_selected_plane = None; customization_tab = 0
                                if act == "background_settings": background_settings_selected = 0
                                if act == "settings": settings_dragging = None; settings_saved_timer = 0
                                if act == "leaderboard":
                                    _reload_leaderboard_data()
                                log_info(f"Game state changed to: {game_state}")
                            break

                elif game_state == "audio_hub":
                    card_rects = _get_audio_hub_card_rects()
                    if event.button == 1:
                        clicked = False
                        for idx, rect in enumerate(card_rects):
                            if rect.collidepoint(mx, my):
                                audio_hub_selected = idx
                                sound_mgr.play("select")
                                _activate_audio_hub_option(idx)
                                clicked = True
                                break
                        if not clicked:
                            back_rect = _get_audio_hub_back_rect()
                            if back_rect.collidepoint(mx, my):
                                game_state = "menu"
                                sound_mgr.play("select")

                elif game_state == "music_library":
                    list_rect, info_rect, controls = get_music_library_layout()
                    layout = build_music_library_controls(list_rect)
                    search_rect = layout["search_rect"]
                    sort_buttons = layout["sort_buttons"]
                    chips = layout["filter_chips"]
                    content_top = layout["content_top"]
                    if event.button == 1:
                        if search_rect.collidepoint(mx, my):
                            music_library_search_active = True
                            sound_mgr.play("select")
                            continue
                        else:
                            music_library_search_active = False
                        sort_clicked = False
                        for mode, _, rect in sort_buttons:
                            if rect.collidepoint(mx, my):
                                set_music_library_sort_mode(mode)
                                sound_mgr.play("select")
                                sort_clicked = True
                                break
                        if sort_clicked:
                            continue
                        chip_clicked = False
                        for key, _, rect in chips:
                            if rect.collidepoint(mx, my):
                                apply_music_library_filter(key)
                                sound_mgr.play("select")
                                chip_clicked = True
                                break
                        if chip_clicked:
                            continue
                        
                        # === 滚动条点击检测 ===
                        visible_rows = _music_library_visible_rows()
                        if len(music_library_tracks) > visible_rows:
                            padding = 10
                            base_y = content_top
                            scroll_track_h = list_rect.bottom - padding - base_y
                            if scroll_track_h > 0:
                                indicator_h = max(30, int(scroll_track_h * (visible_rows / len(music_library_tracks))))
                                max_scroll = max(1, len(music_library_tracks) - visible_rows)
                                indicator_y = base_y + int((scroll_track_h - indicator_h) * (music_library_scroll_index / max_scroll))
                                scroll_bar_x = list_rect.right - 10
                                
                                thumb_rect = pygame.Rect(scroll_bar_x - 4, indicator_y, 16, indicator_h)
                                track_rect = pygame.Rect(scroll_bar_x - 4, base_y, 16, scroll_track_h)
                                
                                if thumb_rect.collidepoint(mx, my):
                                    music_library_dragging_scrollbar = True
                                    music_library_drag_start_y = my
                                    music_library_drag_start_scroll = music_library_scroll_index
                                    continue
                                elif track_rect.collidepoint(mx, my):
                                    # 点击轨道跳转
                                    click_ratio = (my - base_y) / scroll_track_h
                                    music_library_scroll_index = int(click_ratio * max_scroll)
                                    music_library_scroll_index = max(0, min(max_scroll, music_library_scroll_index))
                                    continue
                        
                        if list_rect.collidepoint(mx, my) and music_library_tracks and my >= content_top:
                            rel_y = my - content_top
                            if rel_y >= 0:
                                idx = music_library_scroll_index + rel_y // MUSIC_LIBRARY_ITEM_HEIGHT
                                if 0 <= idx < len(music_library_tracks):
                                    if idx != music_library_selected:
                                        music_library_selected = idx
                                        ensure_music_library_visible()
                                        _queue_selected_music_library_track()
                                        sound_mgr.play("select")
                                    else:
                                        play_music_library_track(idx)
                        elif controls["play"].collidepoint(mx, my):
                            play_music_library_track(music_library_selected)
                        elif controls["stop"].collidepoint(mx, my):
                            stop_music_library_track()
                        elif controls["back"].collidepoint(mx, my):
                            sound_mgr.play("select")
                            return_to_audio_hub_from_music_library()
                elif game_state == "sound_lab":
                    list_rect, info_rect, controls = get_sound_lab_layout()
                    if event.button == 1:
                        chips, filter_band_height = get_sound_lab_filter_layout(list_rect)
                        content_top = list_rect.y + 12 + filter_band_height
                        
                        # === 滚动条点击检测 ===
                        visible_rows = _sound_lab_visible_rows()
                        if len(sound_lab_tracks) > visible_rows:
                            padding = 10
                            scroll_track_h = list_rect.height - padding * 2 - filter_band_height
                            if scroll_track_h > 0:
                                indicator_h = max(30, int(scroll_track_h * (visible_rows / len(sound_lab_tracks))))
                                max_scroll = max(1, len(sound_lab_tracks) - visible_rows)
                                indicator_y = content_top + int((scroll_track_h - indicator_h) * (sound_lab_scroll_index / max_scroll))
                                scroll_bar_x = list_rect.right - 10
                                
                                thumb_rect = pygame.Rect(scroll_bar_x - 4, indicator_y, 16, indicator_h)
                                track_rect = pygame.Rect(scroll_bar_x - 4, content_top, 16, scroll_track_h)
                                
                                if thumb_rect.collidepoint(mx, my):
                                    sound_lab_dragging_scrollbar = True
                                    sound_lab_drag_start_y = my
                                    sound_lab_drag_start_scroll = sound_lab_scroll_index
                                    continue
                                elif track_rect.collidepoint(mx, my):
                                    # 点击轨道跳转
                                    click_ratio = (my - content_top) / scroll_track_h
                                    sound_lab_scroll_index = int(click_ratio * max_scroll)
                                    sound_lab_scroll_index = max(0, min(max_scroll, sound_lab_scroll_index))
                                    continue
                        
                        if list_rect.collidepoint(mx, my):
                            if my < content_top:
                                for key, _, rect in chips:
                                    if rect.collidepoint(mx, my):
                                        apply_sound_lab_filter(key)
                                        sound_mgr.play("select")
                                        break
                            elif sound_lab_tracks:
                                rel_y = my - content_top
                                if rel_y >= 0:
                                    idx = sound_lab_scroll_index + rel_y // SOUND_LAB_ITEM_HEIGHT
                                    if 0 <= idx < len(sound_lab_tracks):
                                        if idx != sound_lab_selected:
                                            sound_lab_selected = idx
                                            ensure_sound_lab_visible()
                                            sound_mgr.play("select")
                                        else:
                                            play_sound_lab_effect(idx)
                        elif controls["play"].collidepoint(mx, my):
                            play_sound_lab_effect(sound_lab_selected)
                        elif controls["stop"].collidepoint(mx, my):
                            stop_sound_lab_effect()
                        elif controls["back"].collidepoint(mx, my):
                            sound_mgr.play("select")
                            return_to_audio_hub_from_sound_lab()
                
                # 成就菜单点击 - 豪华版
                elif game_state == "achievements":
                    MARGIN = 30  # 定义在外部以便返回按钮使用
                    achievement_mgr = get_cached_achievement_mgr()
                    
                    if not achievement_mgr:
                        # 未加载状态 - 中央返回按钮
                        back_btn_empty = pygame.Rect(WIDTH//2 - 70, HEIGHT//2 + 75, 140, 42)
                        if back_btn_empty.collidepoint(mx, my):
                            game_state = "menu"; main_menu_selected = 0; sound_mgr.play("select")
                    
                    if achievement_mgr:
                        # 与绘制函数完全一致的布局常量
                        MARGIN = 30
                        HEADER_H = 70
                        STATS_H = 45
                        TAB_H = 45
                        FOOTER_H = 70
                        CONTENT_GAP = 8
                        
                        # 分类标签位置（在content_top之上）
                        tab_y = MARGIN + HEADER_H + STATS_H + 5
                        tab_h = 38
                        
                        # 分类标签点击
                        categories = [
                            ("all", "📚", "全部"),
                            ("combat", "⚔️", "战斗"),
                            ("boss", "👹", "Boss"),
                            ("survival", "🛡️", "生存"),
                            ("plane", "✈️", "机体"),
                            ("roguelike", "🚪", "肉鸽"),
                            ("milestone", "🏅", "里程碑"),
                            ("secret", "🌙", "隐藏"),
                        ]
                        tab_emoji_font = get_ach_font("Segoe UI Emoji", 16)
                        tab_font = get_ach_font("SimHei", 15)
                        
                        # 计算标签位置（居中）
                        total_tabs_w = 0
                        for cat_id, cat_emoji, cat_name in categories:
                            es = tab_emoji_font.render(cat_emoji, True, WHITE)
                            ts = tab_font.render(cat_name, True, WHITE)
                            total_tabs_w += es.get_width() + ts.get_width() + 26 + 6
                        total_tabs_w -= 6
                        tab_start_x = (WIDTH - total_tabs_w) // 2
                        
                        current_x = tab_start_x
                        for cat_id, cat_emoji, cat_name in categories:
                            es = tab_emoji_font.render(cat_emoji, True, WHITE)
                            ts = tab_font.render(cat_name, True, WHITE)
                            tab_w = es.get_width() + ts.get_width() + 26
                            tab_rect = pygame.Rect(current_x, tab_y, tab_w, tab_h)
                            if tab_rect.collidepoint(mx, my):
                                achievement_category = cat_id
                                achievement_selected = None
                                achievement_scroll_y = 0
                                sound_mgr.play("select")
                                break
                            current_x += tab_w + 6
                        
                        # 内容区布局
                        content_top = MARGIN + HEADER_H + STATS_H + TAB_H + CONTENT_GAP
                        content_h = HEIGHT - MARGIN - content_top - FOOTER_H
                        wall_w = int((WIDTH - MARGIN * 3) * 0.58)
                        wall_rect = pygame.Rect(MARGIN, content_top, wall_w, content_h)
                        
                        # 成就徽章网格点击（参数与绘制一致）
                        grid_cell = 95
                        grid_gap = 12
                        grid_cols = max(1, int((wall_w - 40) // (grid_cell + grid_gap)))  # 至少1列，防止除零
                        grid_start_x = wall_rect.x + (wall_w - grid_cols * (grid_cell + grid_gap) + grid_gap) // 2
                        grid_start_y = wall_rect.y + 18
                        
                        # 获取当前分类的成就（提前获取，供徽章点击和滚动条使用）
                        if achievement_category == "all":
                            filtered_achievements = list(achievement_mgr.achievements.values())
                        else:
                            filtered_achievements = achievement_mgr.get_achievements_by_category(achievement_category)
                        
                        # 徽章区域 (裁剪区域内)
                        badge_area = pygame.Rect(wall_rect.x, wall_rect.y, wall_rect.width, wall_rect.height - 30)
                        
                        if badge_area.collidepoint(mx, my):
                            for i, ach in enumerate(filtered_achievements):
                                col = i % grid_cols
                                row = i // grid_cols
                                
                                bx = grid_start_x + col * (grid_cell + grid_gap)
                                by = grid_start_y + row * (grid_cell + grid_gap) - achievement_scroll_y
                                
                                badge_rect = pygame.Rect(bx, by, grid_cell, grid_cell)
                                if badge_rect.collidepoint(mx, my) and badge_area.collidepoint(mx, my):
                                    achievement_selected = ach.id
                                    sound_mgr.play("select")
                                    break
                        
                        # 滚动条拖动开始检测
                        rows = (len(filtered_achievements) + grid_cols - 1) // grid_cols
                        total_content_h = rows * (grid_cell + grid_gap)
                        view_h = wall_rect.height - TAB_H - 60
                        if total_content_h > view_h:
                            scroll_bar_x = wall_rect.right - 14
                            scroll_bar_y = grid_start_y
                            scroll_bar_h = view_h
                            max_scroll = total_content_h - view_h
                            thumb_h = max(35, int(scroll_bar_h * view_h / total_content_h))
                            thumb_y = scroll_bar_y + int((scroll_bar_h - thumb_h) * achievement_scroll_y / max_scroll) if max_scroll > 0 else scroll_bar_y
                            
                            # 检测是否点击在滚动条滑块上
                            scrollbar_rect = pygame.Rect(scroll_bar_x - 4, thumb_y, 16, thumb_h)
                            if scrollbar_rect.collidepoint(mx, my):
                                achievement_dragging_scrollbar = True
                                achievement_drag_start_y = my
                                achievement_drag_start_scroll = achievement_scroll_y
                            # 点击滚动条轨道则跳转
                            elif pygame.Rect(scroll_bar_x - 4, scroll_bar_y, 16, scroll_bar_h).collidepoint(mx, my):
                                # 计算点击位置对应的滚动值
                                click_ratio = (my - scroll_bar_y) / scroll_bar_h
                                achievement_scroll_y = int(click_ratio * max_scroll)
                                achievement_scroll_y = max(0, min(achievement_scroll_y, max_scroll))
                    
                    # 返回按钮 - 右下角，与绘制代码一致
                    FOOTER_H = 70
                    footer_y = HEIGHT - FOOTER_H
                    back_btn = pygame.Rect(WIDTH - MARGIN - 130, footer_y + 12, 110, 40)
                    if back_btn.collidepoint(mx, my):
                        if achievement_mgr:
                            achievement_mgr.save_to_file()
                        game_state = "menu"; main_menu_selected = 0; sound_mgr.play("select")
                
                # 背景设置界面点击
                elif game_state == "background_settings":
                    from systems import BackgroundManager
                    bg_styles = BackgroundManager.BG_STYLES
                    bg_list = list(bg_styles.items())
                    
                    # 分页配置 - 必须与绘制代码一致！
                    card_w = 270
                    card_h = 195
                    cards_per_row = 4
                    rows_per_page = 2
                    cards_per_page = cards_per_row * rows_per_page
                    gap = 25
                    start_x = (WIDTH - (cards_per_row * card_w + (cards_per_row - 1) * gap)) // 2
                    start_y = 110
                    
                    # 获取当前页的背景
                    page_start = background_settings_page * cards_per_page
                    page_end = min(page_start + cards_per_page, len(bg_list))
                    page_items = bg_list[page_start:page_end]
                    
                    # 检查卡片点击
                    for local_idx, (style_key, _) in enumerate(page_items):
                        global_idx = page_start + local_idx
                        row = local_idx // cards_per_row
                        col = local_idx % cards_per_row
                        
                        x = start_x + col * (card_w + gap)
                        y = start_y + row * (card_h + gap)
                        
                        card_rect = pygame.Rect(x, y, card_w, card_h)
                        
                        if card_rect.collidepoint(mx, my):
                            # 更新选中索引并切换背景
                            background_settings_selected = global_idx
                            bg_manager.set_style(style_key)
                            save_settings(background_style=style_key)
                            sound_mgr.play("select")
                            log_info(f"背景已切换为: {style_key}")
                            break
                    
                    # 翻页按钮 - 必须与绘制代码一致！
                    button_y = start_y + rows_per_page * (card_h + gap) + 20
                    button_w = 120
                    button_h = 45
                    total_pages = (len(bg_list) + cards_per_page - 1) // cards_per_page
                    
                    prev_btn = pygame.Rect(60, button_y, button_w, button_h)
                    next_btn = pygame.Rect(WIDTH - 60 - button_w, button_y, button_w, button_h)
                    
                    if prev_btn.collidepoint(mx, my) and background_settings_page > 0:
                        background_settings_page -= 1
                        sound_mgr.play("select")
                    elif next_btn.collidepoint(mx, my) and background_settings_page < total_pages - 1:
                        background_settings_page += 1
                        sound_mgr.play("select")
                    
                    # 返回按钮 - 必须与绘制代码一致！
                    back_btn = pygame.Rect(WIDTH//2 - 70, HEIGHT - 70, 140, 45)
                    if back_btn.collidepoint(mx, my):
                        game_state = "menu"
                        main_menu_selected = 0
                        sound_mgr.play("select")

                elif game_state == "select_plane":
                    # 新UI布局参数 - 必须与绘制代码一致！
                    content_y = 90
                    content_h = HEIGHT - 170
                    margin = 20
                    gap = 12
                    list_width = 280
                    list_x = margin
                    detail_width = WIDTH - margin * 2 - list_width - gap
                    detail_x = list_x + list_width + gap
                    btn_y = HEIGHT - 65
                    nav_btn_w = 70
                    nav_btn_h = 45
                    
                    # 左侧导航箭头
                    left_btn = pygame.Rect(list_x, btn_y, nav_btn_w, nav_btn_h)
                    # 右侧导航箭头
                    right_btn = pygame.Rect(list_x + list_width - nav_btn_w, btn_y, nav_btn_w, nav_btn_h)
                    # 确认出击按钮
                    start_btn = pygame.Rect(detail_x + detail_width // 2 - 110, btn_y - 2, 220, 50)
                    # 返回按钮
                    back_btn = pygame.Rect(detail_x + detail_width - 90, btn_y, 85, nav_btn_h)
                    
                    # 滚动条参数计算
                    card_h = 50
                    card_gap = 6
                    list_inner_y = content_y + 42
                    list_inner_h = content_h - 48
                    max_visible = list_inner_h // (card_h + card_gap)
                    total_planes = len(plane_keys)
                    scroll_offset = max(0, min(current_plane_idx - max_visible // 2, total_planes - max_visible))
                    
                    # 滚动条点击/拖动检测
                    if total_planes > max_visible:
                        track_h = list_inner_h - 10
                        thumb_h = max(30, int(track_h * max_visible / total_planes))
                        thumb_y = list_inner_y + 5 + int((track_h - thumb_h) * scroll_offset / max(1, total_planes - max_visible))
                        scrollbar_rect = pygame.Rect(list_x + list_width - 12, thumb_y, 8, thumb_h)
                        track_rect = pygame.Rect(list_x + list_width - 12, list_inner_y + 5, 8, track_h)
                        
                        if scrollbar_rect.collidepoint(mx, my):
                            # 点击滑块开始拖动
                            plane_select_dragging_scrollbar = True
                            plane_select_drag_start_y = my
                            plane_select_drag_start_scroll = current_plane_idx
                        elif track_rect.collidepoint(mx, my):
                            # 点击轨道跳转
                            click_ratio = (my - (list_inner_y + 5)) / track_h
                            current_plane_idx = int(click_ratio * total_planes)
                            current_plane_idx = max(0, min(current_plane_idx, total_planes - 1))
                            sound_mgr.play("select")
                    
                    # 机体列表点击检测
                    list_rect = pygame.Rect(list_x, content_y, list_width - 15, content_h)  # 留出滚动条空间
                    if list_rect.collidepoint(mx, my):
                        for i in range(scroll_offset, min(scroll_offset + max_visible, total_planes)):
                            idx = i - scroll_offset
                            cy = list_inner_y + idx * (card_h + card_gap)
                            card = pygame.Rect(list_x + 8, cy, list_width - 26, card_h)
                            if card.collidepoint(mx, my):
                                current_plane_idx = i
                                sound_mgr.play("select")
                                break
                    elif left_btn.collidepoint(mx, my):
                        current_plane_idx = (current_plane_idx-1)%len(plane_keys)
                        sound_mgr.play("select")
                    elif right_btn.collidepoint(mx, my):
                        current_plane_idx = (current_plane_idx+1)%len(plane_keys)
                        sound_mgr.play("select")
                    elif start_btn.collidepoint(mx, my):
                        selected_plane = plane_keys[current_plane_idx]
                        sound_mgr.play("select")
                        try:
                            reset_game()
                            game_state = "game"
                        except Exception as e:
                            log_error(f"reset_game failed: {e}")
                            game_state = "menu"
                    elif back_btn.collidepoint(mx, my):
                        sound_mgr.play("select")
                        game_state = "mode_select"
                
                elif game_state == "boss_challenge_select_plane":
                    # 新UI布局参数 - 必须与绘制代码一致！
                    content_y = 90
                    content_h = HEIGHT - 170
                    margin = 20
                    gap = 12
                    list_width = 280
                    list_x = margin
                    detail_width = WIDTH - margin * 2 - list_width - gap
                    detail_x = list_x + list_width + gap
                    btn_y = HEIGHT - 65
                    nav_btn_w = 70
                    nav_btn_h = 45
                    
                    # 左侧导航箭头
                    left_btn = pygame.Rect(list_x, btn_y, nav_btn_w, nav_btn_h)
                    # 右侧导航箭头
                    right_btn = pygame.Rect(list_x + list_width - nav_btn_w, btn_y, nav_btn_w, nav_btn_h)
                    # 确认出击按钮
                    start_btn = pygame.Rect(detail_x + detail_width // 2 - 110, btn_y - 2, 220, 50)
                    # 返回按钮
                    back_btn = pygame.Rect(detail_x + detail_width - 90, btn_y, 85, nav_btn_h)
                    
                    # 滚动条参数计算
                    card_h = 50
                    card_gap = 6
                    list_inner_y = content_y + 42
                    list_inner_h = content_h - 48
                    max_visible = list_inner_h // (card_h + card_gap)
                    total_planes = len(plane_keys)
                    scroll_offset = max(0, min(current_plane_idx - max_visible // 2, total_planes - max_visible))
                    
                    # 滚动条点击/拖动检测
                    if total_planes > max_visible:
                        track_h = list_inner_h - 10
                        thumb_h = max(30, int(track_h * max_visible / total_planes))
                        thumb_y = list_inner_y + 5 + int((track_h - thumb_h) * scroll_offset / max(1, total_planes - max_visible))
                        scrollbar_rect = pygame.Rect(list_x + list_width - 12, thumb_y, 8, thumb_h)
                        track_rect = pygame.Rect(list_x + list_width - 12, list_inner_y + 5, 8, track_h)
                        
                        if scrollbar_rect.collidepoint(mx, my):
                            # 点击滑块开始拖动
                            plane_select_dragging_scrollbar = True
                            plane_select_drag_start_y = my
                            plane_select_drag_start_scroll = current_plane_idx
                        elif track_rect.collidepoint(mx, my):
                            # 点击轨道跳转
                            click_ratio = (my - (list_inner_y + 5)) / track_h
                            current_plane_idx = int(click_ratio * total_planes)
                            current_plane_idx = max(0, min(current_plane_idx, total_planes - 1))
                            sound_mgr.play("select")
                    
                    # 机体列表点击检测
                    list_rect = pygame.Rect(list_x, content_y, list_width - 15, content_h)  # 留出滚动条空间
                    if list_rect.collidepoint(mx, my):
                        for i in range(scroll_offset, min(scroll_offset + max_visible, total_planes)):
                            idx = i - scroll_offset
                            cy = list_inner_y + idx * (card_h + card_gap)
                            card = pygame.Rect(list_x + 8, cy, list_width - 26, card_h)
                            if card.collidepoint(mx, my):
                                current_plane_idx = i
                                sound_mgr.play("select")
                                break
                    elif left_btn.collidepoint(mx, my):
                        current_plane_idx = (current_plane_idx-1)%len(plane_keys)
                        sound_mgr.play("select")
                    elif right_btn.collidepoint(mx, my):
                        current_plane_idx = (current_plane_idx+1)%len(plane_keys)
                        sound_mgr.play("select")
                    elif start_btn.collidepoint(mx, my):
                        # 确认选择，开始Boss挑战
                        selected_plane = plane_keys[current_plane_idx]
                        game_state = "boss_challenge_play"
                        boss_challenge_current = 0
                        boss_challenge_active = True
                        enabled_bosses = [k for k in boss_challenge_order if boss_challenge_enabled.get(k, True)]
                        boss_challenge_order[:] = enabled_bosses
                        sound_mgr.play("select")
                        try:
                            reset_game()
                            if not boss_challenge_music_active:
                                music_director.push_state("boss_challenge", intensity=0.85, immediate=True)
                                boss_challenge_music_active = True
                            if boss_challenge_active and boss_challenge_current < len(boss_challenge_order):
                                boss_type = boss_challenge_order[boss_challenge_current]
                                candidate = boss_manager.spawn_boss(player.level, boss_type=boss_type)
                                boss_challenge_current += 1
                                if candidate:
                                    boss = candidate
                                    all_sprites.add(boss)
                        except Exception as e:
                            log_error(f"Failed to start boss challenge: {e}")
                    elif back_btn.collidepoint(mx, my):
                        # 返回Boss选择时重置order为全部Boss
                        boss_challenge_order[:] = list(BOSS_DB.keys())
                        game_state = "boss_challenge"
                        sound_mgr.play("select")
                    
                elif game_state == "arsenal":
                    sound_mgr.play("select")
                    r = ARSENAL_UI
                    weapons = arsenal_save_data["weapons"]
                    item_height = 60
                    total_h = len(weapons) * item_height
                    view_h = r['list_area'].height
                    max_scroll = max(0, total_h - view_h)
                    
                    # 滚动条拖动检测
                    if total_h > view_h:
                        bar_h = max(20, (view_h / total_h) * view_h)
                        bar_y = r['list_area'].y + (arsenal_scroll_y / total_h) * view_h if total_h > 0 else r['list_area'].y
                        scrollbar_rect = pygame.Rect(r['list_area'].right - 8, bar_y, 8, bar_h)
                        track_rect = pygame.Rect(r['list_area'].right - 8, r['list_area'].y, 8, view_h)
                        
                        if scrollbar_rect.collidepoint(mx, my):
                            # 点击滑块开始拖动
                            arsenal_dragging_scrollbar = True
                            arsenal_drag_start_y = my
                            arsenal_drag_start_scroll = arsenal_scroll_y
                        elif track_rect.collidepoint(mx, my):
                            # 点击轨道跳转
                            click_ratio = (my - r['list_area'].y) / view_h
                            arsenal_scroll_y = int(click_ratio * max_scroll)
                            arsenal_scroll_y = max(0, min(arsenal_scroll_y, max_scroll))
                    
                    # 列表点击 (修正为支持滚动)
                    if r['list_area'].collidepoint(mx, my) and mx < r['list_area'].right - 10:
                        # 计算相对于列表内容顶部的坐标
                        click_offset = my - (r['list_area'].y + 10) + arsenal_scroll_y
                        idx = click_offset // 60
                        # 确保点击有效范围
                        if 0 <= idx < len(arsenal_save_data["weapons"]):
                            arsenal_selected_weapon_idx = int(idx)
                            
                    # 槽位
                    slots = [r['slot_0'], r['slot_1'], r['slot_2']]
                    for i, s in enumerate(slots):
                        if s.collidepoint(mx, my):
                            if 0 <= arsenal_selected_weapon_idx < len(arsenal_save_data["weapons"]):
                                arsenal_save_data["loadout"][i] = arsenal_save_data["weapons"][arsenal_selected_weapon_idx]
                            else: arsenal_save_data["loadout"][i] = None
                            save_arsenal()
                    # 研发
                    pool = None; cc = 0; ch = 0
                    if r['btn_research_normal'].collidepoint(mx, my):
                        if arsenal_save_data["currencies"]["cores"] >= 20: cc=20; pool=list(WEAPON_TYPES.keys())
                        else: sound_mgr.play("warning")
                    elif r['btn_research_elite'].collidepoint(mx, my):
                        if arsenal_save_data["currencies"]["chips"] >= 3: ch=3; pool=["railgun", "void", "frost", "swarm"]
                        else: sound_mgr.play("warning")
                    if pool:
                        arsenal_save_data["currencies"]["cores"] -= cc
                        arsenal_save_data["currencies"]["chips"] -= ch
                        nt = random.choice(pool)
                        dup = False
                        for w in arsenal_save_data["weapons"]:
                            if w["type"] == nt: dup = True; break
                        if dup:
                            arsenal_save_data["currencies"]["cores"] += 20
                            arsenal_msg = f"重复武器 {WEAPON_TYPES[nt]['name']}，已返还20核心"; arsenal_msg_timer = 180
                            sound_mgr.play("select")
                        else:
                            nw = create_weapon(nt); arsenal_save_data["weapons"].append(nw)
                            arsenal_msg = f"研发成功: {WEAPON_TYPES[nt]['name']}"; arsenal_msg_timer = 180
                            sound_mgr.play("levelup")
                        save_arsenal()
                    # 升级
                    if r['btn_upgrade'].collidepoint(mx, my) and 0 <= arsenal_selected_weapon_idx < len(arsenal_save_data["weapons"]):
                        w = arsenal_save_data["weapons"][arsenal_selected_weapon_idx]
                        cost = w['stars'] * 10
                        if arsenal_save_data["currencies"]["cores"] >= cost:
                            arsenal_save_data["currencies"]["cores"] -= cost; w['stars'] += 1
                            save_arsenal(); sound_mgr.play("levelup")
                        else: sound_mgr.play("warning")
                    if r['btn_back'].collidepoint(mx, my):
                        if player and hasattr(player, 'achievement_manager'):
                            player.achievement_manager.save_to_file()
                        game_state = "menu"

                elif game_state == "gallery":
                    sound_mgr.play("select")
                    # 7个稀有度标签点击检测: 全部/1星/2星/3星/4星/5星/6星
                    tab_width = 90
                    tab_gap = 10
                    total_tab_width = 7 * tab_width + 6 * tab_gap  # 7个标签,6个间隙
                    start_tab_x = (WIDTH - total_tab_width) // 2
                    
                    # 检测7个标签的点击
                    tab_clicked = False
                    for i in range(7):
                        tab_x = start_tab_x + i * (tab_width + tab_gap)
                        tab_rect = pygame.Rect(tab_x, 80, tab_width, 40)
                        if tab_rect.collidepoint(mx, my):
                            gallery_tab = i  # 0=全部, 1=1星, 2=2星, 3=3星, 4=4星, 5=5星, 6=6星
                            gallery_page = 0
                            gallery_hover_card = None  # 切换标签时清除选中
                            tab_clicked = True
                            break
                    
                    # 【新】检测卡牌点击 - 点击卡牌显示/隐藏Tooltip
                    if not tab_clicked:
                        # 获取当前页的卡牌列表（复制draw_gallery_ui的逻辑）
                        from roguelite import BASE_CARDS, MODIFIER_CARDS, SYNERGY_RULES
                        all_cards = []
                        for key, card in BASE_CARDS.items():
                            all_cards.append({"id": key, "name": card["name"], "rarity": card["rarity"],
                                            "desc": card.get("desc", ""), "type": "base", "data": card})
                        for key, mod in MODIFIER_CARDS.items():
                            all_cards.append({"id": key, "name": mod["name"], "rarity": mod["rarity"],
                                            "desc": mod.get("desc", ""), "type": "modifier", "data": mod})
                        for key, synergy in SYNERGY_RULES.items():
                            all_cards.append({"id": key, "name": synergy["name"], "rarity": synergy["rarity"],
                                            "desc": synergy.get("desc", ""), "type": "synergy", "data": synergy})
                        
                        # 按品质筛选（与draw_gallery_ui完全一致）
                        if gallery_tab == 0:
                            items = all_cards
                        else:
                            # gallery_tab 1-6 对应 rarity 1-6
                            items = [c for c in all_cards if c["rarity"] == gallery_tab]
                        
                        # 分页（3列布局，每页6个）
                        cols = 3
                        card_w = 360
                        card_h = 180
                        gap = 30
                        start_gx = (WIDTH - (cols * card_w + (cols - 1) * gap)) // 2
                        start_y = 140
                        
                        items_per_page = 6
                        start_idx = gallery_page * items_per_page
                        end_idx = min(start_idx + items_per_page, len(items))
                        
                        # 检测卡牌点击
                        for i in range(start_idx, end_idx):
                            item = items[i]
                            rel_i = i - start_idx
                            row = rel_i // cols
                            col = rel_i % cols
                            x = start_gx + col * (card_w + gap)
                            y = start_y + row * (card_h + gap)
                            
                            if pygame.Rect(x, y, card_w, card_h).collidepoint(mx, my):
                                # 点击卡牌：如果已选中则取消，否则选中
                                if gallery_hover_card and gallery_hover_card.get('id') == item['id']:
                                    gallery_hover_card = None
                                else:
                                    gallery_hover_card = item
                                break
                    
                    # 翻页按钮
                    if pygame.Rect(8, HEIGHT//2 - 30, 50, 60).collidepoint(mx, my) and gallery_page > 0: 
                        gallery_page -= 1
                    if pygame.Rect(WIDTH-58, HEIGHT//2 - 30, 50, 60).collidepoint(mx, my): 
                        gallery_page += 1
                    
                    # 返回按钮
                    if pygame.Rect(WIDTH//2-50, HEIGHT-60, 100, 40).collidepoint(mx, my):
                        if player and hasattr(player, 'achievement_manager'):
                            player.achievement_manager.save_to_file()
                        game_state = "menu"

                elif game_state == "codex":
                    sound_mgr.play("select")
                    r = CODEX_UI
                    if r['tab_plane'].collidepoint(mx, my): codex_tab=0; codex_idx=0; codex_scroll_y=0
                    if r['tab_boss'].collidepoint(mx, my): codex_tab=1; codex_idx=0; codex_scroll_y=0
                    if r.get('tab_enemy') and r['tab_enemy'].collidepoint(mx, my): codex_tab=2; codex_idx=0; codex_scroll_y=0
                    
                    # 计算滚动相关参数
                    if codex_tab == 0:
                        keys = plane_keys
                    elif codex_tab == 1:
                        keys = list(BOSS_DB.keys())
                    else:
                        from enemy_manager import enemy_type_manager
                        keys = [e["id"] for e in enemy_type_manager.get_regular_types()]
                    
                    item_h = 45
                    list_rect = r['list_view']
                    content_height = len(keys) * item_h
                    scroll_height = list_rect.height - 10
                    max_scroll = max(0, content_height - list_rect.height)
                    
                    # 滚动条拖动检测
                    if content_height > list_rect.height:
                        thumb_height = max(30, int(scroll_height * list_rect.height / content_height))
                        thumb_y = list_rect.y + 5 + int((scroll_height - thumb_height) * codex_scroll_y / max_scroll) if max_scroll > 0 else list_rect.y + 5
                        scrollbar_rect = pygame.Rect(list_rect.right - 10, thumb_y, 8, thumb_height)
                        track_rect = pygame.Rect(list_rect.right - 10, list_rect.y + 5, 8, scroll_height)
                        
                        if scrollbar_rect.collidepoint(mx, my):
                            codex_dragging_scrollbar = True
                            codex_drag_start_y = my
                            codex_drag_start_scroll = codex_scroll_y
                        elif track_rect.collidepoint(mx, my):
                            click_ratio = (my - list_rect.y - 5) / scroll_height
                            codex_scroll_y = int(click_ratio * max_scroll)
                            codex_scroll_y = max(0, min(codex_scroll_y, max_scroll))
                    
                    if r['list_view'].collidepoint(mx, my) and mx < list_rect.right - 12:
                        offset_y = my - r['list_view'].y + codex_scroll_y
                        clicked_idx = int(offset_y // 45)
                        if 0 <= clicked_idx < len(keys): codex_idx = clicked_idx
                    if r['btn_back'].collidepoint(mx, my):
                        if player and hasattr(player, 'achievement_manager'):
                            player.achievement_manager.save_to_file()
                        game_state = "menu"

                elif game_state == "leaderboard":
                    sound_mgr.play("select")
                    
                    # 主标签栏（排行榜 / 个人统计）- 更新位置匹配UI
                    main_tab_y = 82
                    main_tab_width = 160
                    main_tab_start = WIDTH//2 - (main_tab_width * 2 + 30) // 2
                    for i in range(2):
                        tab_rect = pygame.Rect(main_tab_start + i * (main_tab_width + 30), main_tab_y, main_tab_width, 40)
                        if tab_rect.collidepoint(mx, my):
                            leaderboard_stats_tab = i
                            leaderboard_scroll_y = 0  # 切换标签时重置滚动
                    
                    # 仅在排行榜标签下处理模式和排序
                    if leaderboard_stats_tab == 0:
                        # 滚动条拖动检测
                        scrollbar_info = _leaderboard_cache.get("scrollbar_info")
                        if scrollbar_info:
                            thumb_rect = scrollbar_info["thumb_rect"]
                            track_rect = scrollbar_info["track_rect"]
                            max_scroll = scrollbar_info["max_scroll"]
                            
                            if thumb_rect.collidepoint(mx, my):
                                # 开始拖动滑块
                                leaderboard_dragging_scrollbar = True
                                leaderboard_drag_start_y = my
                                leaderboard_drag_start_scroll = leaderboard_scroll_y
                            elif track_rect.collidepoint(mx, my):
                                # 点击轨道跳转
                                track_height = track_rect.height - thumb_rect.height
                                if track_height > 0:
                                    click_ratio = (my - track_rect.y - thumb_rect.height / 2) / track_height
                                    click_ratio = max(0, min(1, click_ratio))
                                    leaderboard_scroll_y = int(click_ratio * max_scroll)
                        
                        # 模式切换标签
                        mode_y = 135
                        modes = ["normal", "roguelike", "boss_challenge"]
                        mode_tab_width = 140
                        mode_start = WIDTH//2 - (mode_tab_width * 3 + 40) // 2
                        for i, mode_id in enumerate(modes):
                            tab_rect = pygame.Rect(mode_start + i * (mode_tab_width + 20), mode_y, mode_tab_width, 35)
                            if tab_rect.collidepoint(mx, my):
                                leaderboard_mode = mode_id
                                leaderboard_scroll_y = 0  # 切换模式时重置滚动
                        
                        # 排序选项
                        sort_y = 182
                        sort_options = ["score", "kills", "time", "wave"]
                        sort_btn_w = 90
                        sort_start = WIDTH//2 - (sort_btn_w * 4 + 45) // 2
                        for i, sort_id in enumerate(sort_options):
                            btn_rect = pygame.Rect(sort_start + i * (sort_btn_w + 15), sort_y, sort_btn_w, 30)
                            if btn_rect.collidepoint(mx, my):
                                leaderboard_sort_by = sort_id
                    
                    # 返回按钮
                    back_btn = pygame.Rect(WIDTH//2 - 80, HEIGHT - 75, 160, 50)
                    if back_btn.collidepoint(mx, my):
                        if player and hasattr(player, 'achievement_manager'):
                            player.achievement_manager.save_to_file()
                        game_state = "menu"
                
                elif game_state == "settings":
                    # 获取UI元素
                    settings_ui = draw_settings_ui()
                    
                    # 保存按钮
                    if settings_ui['save'].collidepoint(mx, my):
                        # 保存设置到文件
                        save_settings(
                            master_volume=sound_mgr.master_volume,
                            music_volume=sound_mgr.music_volume,
                            sfx_volume=sound_mgr.sfx_volume,
                            show_fps=game_settings.get("show_fps", True),
                            screen_shake=game_settings.get("screen_shake", True),
                            particle_quality=game_settings.get("particle_quality", "high"),
                            show_damage_numbers=game_settings.get("show_damage_numbers", True),
                            auto_fire=game_settings.get("auto_fire", True)
                        )
                        settings_saved_msg = "设置已保存!"
                        settings_saved_timer = 60
                        sound_mgr.play("levelup")
                    
                    # 恢复默认按钮
                    elif settings_ui['reset'].collidepoint(mx, my):
                        sound_mgr.set_master_volume(1.0)
                        sound_mgr.set_music_volume(0.5)
                        sound_mgr.set_sfx_volume(0.8)
                        game_settings["show_fps"] = True
                        game_settings["screen_shake"] = True
                        game_settings["particle_quality"] = "high"
                        game_settings["show_damage_numbers"] = True
                        game_settings["auto_fire"] = True
                        settings_saved_msg = "已恢复默认设置!"
                        settings_saved_timer = 60
                        sound_mgr.play("select")
                    
                    # 返回按钮
                    elif settings_ui['back'].collidepoint(mx, my):
                        game_state = "menu"
                        main_menu_selected = 0
                        sound_mgr.play("select")
                    
                    # FPS复选框
                    elif settings_ui['fps_checkbox'].collidepoint(mx, my):
                        game_settings["show_fps"] = not game_settings.get("show_fps", True)
                        sound_mgr.play("select")
                    
                    # 屏幕震动复选框
                    elif settings_ui['shake_checkbox'].collidepoint(mx, my):
                        game_settings["screen_shake"] = not game_settings.get("screen_shake", True)
                        sound_mgr.play("select")
                    
                    # 伤害数字复选框
                    elif settings_ui['damage_checkbox'].collidepoint(mx, my):
                        game_settings["show_damage_numbers"] = not game_settings.get("show_damage_numbers", True)
                        sound_mgr.play("select")
                    
                    # 粒子质量按钮
                    else:
                        clicked_quality = False
                        for btn_rect, quality in settings_ui['particle_quality_btns']:
                            if btn_rect.collidepoint(mx, my):
                                game_settings["particle_quality"] = quality
                                sound_mgr.play("select")
                                clicked_quality = True
                                break
                        
                        # 射击模式按钮
                        if not clicked_quality:
                            for btn_rect, mode in settings_ui['fire_mode_btns']:
                                if btn_rect.collidepoint(mx, my):
                                    game_settings["auto_fire"] = mode
                                    sound_mgr.play("select")
                                    clicked_quality = True
                                    break
                        
                        # 检查滑块点击
                        if not clicked_quality:
                            for slider_rect, key in settings_ui['sliders']:
                                if slider_rect.collidepoint(mx, my):
                                    settings_dragging = key
                                    # 立即更新音量到点击位置
                                    new_value = (mx - slider_rect.x) / slider_rect.width
                                    new_value = max(0.0, min(1.0, new_value))
                                    if key == 'master':
                                        sound_mgr.set_master_volume(new_value)
                                    elif key == 'music':
                                        sound_mgr.set_music_volume(new_value)
                                    elif key == 'sfx':
                                        sound_mgr.set_sfx_volume(new_value)
                                        sound_mgr.play("select")  # 播放音效测试
                                    break
                
                elif game_state == "customization":
                    # 根据模式处理点击
                    if customization_mode == "plane":
                        handle_plane_customization_click(mx, my)
                    else:
                        handle_wingman_customization_click(mx, my)
                
                # --- 游戏中的点击逻辑 (彻底修复输入冲突) ---
                elif game_state == "game" or game_state == "boss_challenge_play":
                    # 商店UI点击处理
                    if room_manager and room_manager.show_shop_ui and room_manager.shop_items:
                        card_width = 260
                        card_height = 280
                        gap = 30
                        total_width = len(room_manager.shop_items) * card_width + (len(room_manager.shop_items) - 1) * gap
                        start_x = (WIDTH - total_width) // 2
                        card_y = 200
                        
                        for i, item in enumerate(room_manager.shop_items):
                            card_x = start_x + i * (card_width + gap)
                            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                            if card_rect.collidepoint(mx, my):
                                # 尝试购买
                                purchased = room_manager.try_purchase_item(i)
                                if purchased:
                                    # 应用购买的物品效果
                                    item_type = purchased["type"]
                                    value = purchased["value"]
                                    if item_type == "heal":
                                        player.hp = min(player.max_hp, player.hp + value)
                                    elif item_type == "exp":
                                        player.gain_exp(value)
                                    elif item_type == "item" and item_manager:
                                        for _ in range(value):
                                            item_manager.try_spawn_drop(player.rect.centerx, player.rect.centery)
                                    elif item_type == "card":
                                        for _ in range(value):
                                            player.gain_exp(player.exp_to_next_level)
                                break
                    # 房间选择UI点击处理
                    elif room_manager and room_manager.show_completion_ui and room_manager.available_next_rooms:
                        # 根据房间数量调整卡片大小（与room_system.py保持一致）
                        num_rooms = len(room_manager.available_next_rooms)
                        if num_rooms <= 3:
                            card_width, card_height, gap = 280, 360, 40
                        elif num_rooms == 4:
                            card_width, card_height, gap = 240, 340, 30
                        else:  # 5个或更多
                            card_width, card_height, gap = 200, 320, 25
                        
                        total_width = num_rooms * card_width + (num_rooms - 1) * gap
                        start_x = (WIDTH - total_width) // 2
                        card_y = 210
                        
                        for i, room in enumerate(room_manager.available_next_rooms):
                            card_x = start_x + i * (card_width + gap)
                            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                            if card_rect.collidepoint(mx, my):
                                # 选择房间
                                room_manager.enter_room(room.room_id)
                                room_manager.show_completion_ui = False
                                room_manager.selected_next_room = 0
                                room_manager.available_next_rooms = []
                                # 恢复游戏状态
                                is_paused = False
                                frozen_screen = None
                                sound_mgr.play("levelup")
                                break
                    elif levelup_paused and levelup_ready and upgrade_options:
                        # Handle click on upgrade cards
                        sound_mgr.play("select")
                        card_width = 280
                        card_height = 400
                        gap = 40
                        total_width = 3 * card_width + 2 * gap
                        start_x = (WIDTH - total_width) // 2
                        start_y = 200
                        for i, buff_id in enumerate(upgrade_options):
                            card_x = start_x + i * (card_width + gap)
                            card_rect = pygame.Rect(card_x, start_y, card_width, card_height)
                            if card_rect.collidepoint(mx, my):
                                # Apply upgrade
                                if player and hasattr(player, 'upgrade_manager'):
                                    try:
                                        player.upgrade_manager.select_upgrade(i)
                                        sound_mgr.play("levelup")
                                    except Exception as e:
                                        log_error(f"Failed to select upgrade by click: {e}")
                                # Resume game
                                upgrade_options = []
                                upgrade_selected = 0
                                levelup_ready = False
                                is_paused = False
                                levelup_paused = False
                                frozen_screen = None
                                break
                    elif is_paused:
                        # 仅在暂停时处理菜单点击
                        cx, cy = WIDTH//2, HEIGHT//2
                        if pygame.Rect(cx-100, cy-60, 200, 50).collidepoint(mx, my):
                            is_paused = False  # 恢复
                            sound_mgr.play("select")
                        elif pygame.Rect(cx-100, cy+10, 200, 50).collidepoint(mx, my):
                            reset_game()  # 重来
                            is_paused = False
                            sound_mgr.play("select")
                        elif pygame.Rect(cx-100, cy+80, 200, 50).collidepoint(mx, my):
                            game_state = "menu" # 退出
                            # 菜单使用电影配乐
                            music_director.set_state("menu", intensity=0.25)
                            sound_mgr.play("select")
                    else:
                        # 游戏进行中：处理点击攻击等逻辑
                        # 注意：这里不需要播放 "select" 音效，也不应该触发暂停
                        # 如果未来需要点击射击，代码写在这里
                        pass
            
            # 鼠标释放事件
            if event.type == pygame.MOUSEBUTTONUP:
                if game_state == "settings" and settings_dragging:
                    settings_dragging = None
                # 成就滚动条拖动结束
                if game_state == "achievements":
                    achievement_dragging_scrollbar = False
                # 武器库滚动条拖动结束
                if game_state == "arsenal":
                    arsenal_dragging_scrollbar = False
                # 图鉴滚动条拖动结束
                if game_state == "codex":
                    codex_dragging_scrollbar = False
                # 音乐馆滚动条拖动结束
                if game_state == "music_library":
                    music_library_dragging_scrollbar = False
                # 音效实验室滚动条拖动结束
                if game_state == "sound_lab":
                    sound_lab_dragging_scrollbar = False
                # 排行榜滚动条拖动结束
                if game_state == "leaderboard":
                    leaderboard_dragging_scrollbar = False
                # 飞机选择界面滚动条拖动结束
                if game_state in ["select_plane", "boss_challenge_select_plane"]:
                    plane_select_dragging_scrollbar = False

            if event.type == pygame.MOUSEWHEEL:
                if game_state == "music_library":
                    scroll_music_library(-event.y)
                elif game_state == "sound_lab":
                    scroll_sound_lab(-event.y)
                elif game_state == "leaderboard" and leaderboard_stats_tab == 0:
                    # 排行榜滚轮滚动
                    scroll_amount = -event.y * 40
                    scrollbar_info = _leaderboard_cache.get("scrollbar_info")
                    if scrollbar_info:
                        max_scroll = scrollbar_info["max_scroll"]
                        leaderboard_scroll_y = max(0, min(leaderboard_scroll_y + scroll_amount, max_scroll))
        
        # 鼠标拖动更新 (在事件循环外持续检测)
        if game_state == "settings" and settings_dragging:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:  # 左键按下
                mx, my = pygame.mouse.get_pos()
                start_y = 160
                slider_width = 400
                
                # 根据拖动的滑块类型计算对应的轨道
                slider_index = {'master': 0, 'music': 1, 'sfx': 2}.get(settings_dragging, 0)
                y_pos = start_y + slider_index * 75
                track_rect = pygame.Rect(WIDTH//2 - 350, y_pos + 30, slider_width, 18)
                
                # 计算新值
                new_value = (mx - track_rect.x) / track_rect.width
                new_value = max(0.0, min(1.0, new_value))
                
                # 更新对应的音量
                if settings_dragging == 'master':
                    sound_mgr.set_master_volume(new_value)
                elif settings_dragging == 'music':
                    sound_mgr.set_music_volume(new_value)
                elif settings_dragging == 'sfx':
                    sound_mgr.set_sfx_volume(new_value)
            else:
                settings_dragging = None
        
        # 成就滚动条拖动更新 (在事件循环外持续检测)
        if game_state == "achievements" and achievement_dragging_scrollbar:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:  # 左键按下
                mx, my = pygame.mouse.get_pos()
                achievement_mgr = get_cached_achievement_mgr()
                if achievement_mgr:
                    # 计算布局参数（与绘制一致）
                    MARGIN = 30
                    HEADER_H, STATS_H, TAB_H, FOOTER_H, CONTENT_GAP = 70, 45, 45, 70, 8
                    grid_cell, grid_gap = 95, 12
                    wall_w = int((WIDTH - MARGIN * 3) * 0.58)
                    grid_cols = max(1, int((wall_w - 40) // (grid_cell + grid_gap)))
                    content_top = MARGIN + HEADER_H + STATS_H + TAB_H + CONTENT_GAP
                    wall_h = HEIGHT - MARGIN - content_top - FOOTER_H
                    grid_start_y = content_top + 18
                    view_h = wall_h - TAB_H - 60
                    
                    # 获取成就数量
                    if achievement_category == "all":
                        filtered = list(achievement_mgr.achievements.values())
                    else:
                        filtered = achievement_mgr.get_achievements_by_category(achievement_category)
                    rows = (len(filtered) + grid_cols - 1) // grid_cols
                    total_content_h = rows * (grid_cell + grid_gap)
                    max_scroll = max(0, total_content_h - view_h)
                    
                    if max_scroll > 0:
                        scroll_bar_h = view_h
                        thumb_h = max(35, int(scroll_bar_h * view_h / total_content_h))
                        
                        # 计算拖动偏移
                        delta_y = my - achievement_drag_start_y
                        scroll_ratio = delta_y / (scroll_bar_h - thumb_h) if (scroll_bar_h - thumb_h) > 0 else 0
                        new_scroll = achievement_drag_start_scroll + scroll_ratio * max_scroll
                        achievement_scroll_y = max(0, min(int(new_scroll), max_scroll))
            else:
                achievement_dragging_scrollbar = False

        # 飞机选择界面滚动条拖动更新
        if game_state in ["select_plane", "boss_challenge_select_plane"] and plane_select_dragging_scrollbar:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                mx, my = pygame.mouse.get_pos()
                # 布局参数
                content_y = 90
                content_h = HEIGHT - 170
                list_inner_y = content_y + 42
                list_inner_h = content_h - 48
                card_h = 50
                card_gap = 6
                max_visible = list_inner_h // (card_h + card_gap)
                total_planes = len(plane_keys)
                
                if total_planes > max_visible:
                    track_h = list_inner_h - 10
                    thumb_h = max(30, int(track_h * max_visible / total_planes))
                    
                    # 计算拖动偏移
                    delta_y = my - plane_select_drag_start_y
                    scroll_ratio = delta_y / (track_h - thumb_h) if (track_h - thumb_h) > 0 else 0
                    new_idx = plane_select_drag_start_scroll + int(scroll_ratio * total_planes)
                    current_plane_idx = max(0, min(new_idx, total_planes - 1))
            else:
                plane_select_dragging_scrollbar = False

        # 武器库滚动条拖动更新
        if game_state == "arsenal" and arsenal_dragging_scrollbar:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                mx, my = pygame.mouse.get_pos()
                r = ARSENAL_UI
                weapons = arsenal_save_data["weapons"]
                item_height = 60
                total_h = len(weapons) * item_height
                view_h = r['list_area'].height
                max_scroll = max(0, total_h - view_h)
                
                if max_scroll > 0:
                    bar_h = max(20, (view_h / total_h) * view_h)
                    delta_y = my - arsenal_drag_start_y
                    scroll_ratio = delta_y / (view_h - bar_h) if (view_h - bar_h) > 0 else 0
                    new_scroll = arsenal_drag_start_scroll + scroll_ratio * max_scroll
                    arsenal_scroll_y = max(0, min(int(new_scroll), max_scroll))
            else:
                arsenal_dragging_scrollbar = False

        # 图鉴滚动条拖动更新
        if game_state == "codex" and codex_dragging_scrollbar:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                mx, my = pygame.mouse.get_pos()
                r = CODEX_UI
                list_rect = r['list_view']
                
                if codex_tab == 0:
                    keys = plane_keys
                elif codex_tab == 1:
                    keys = list(BOSS_DB.keys())
                else:
                    from enemy_manager import enemy_type_manager
                    keys = [e["id"] for e in enemy_type_manager.get_regular_types()]
                
                item_h = 45
                content_height = len(keys) * item_h
                scroll_height = list_rect.height - 10
                max_scroll = max(0, content_height - list_rect.height)
                
                if max_scroll > 0:
                    thumb_height = max(30, int(scroll_height * list_rect.height / content_height))
                    delta_y = my - codex_drag_start_y
                    scroll_ratio = delta_y / (scroll_height - thumb_height) if (scroll_height - thumb_height) > 0 else 0
                    new_scroll = codex_drag_start_scroll + scroll_ratio * max_scroll
                    codex_scroll_y = max(0, min(int(new_scroll), max_scroll))
            else:
                codex_dragging_scrollbar = False

        # 音乐馆滚动条拖动更新
        if game_state == "music_library" and music_library_dragging_scrollbar:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                mx, my = pygame.mouse.get_pos()
                list_rect, _, _ = get_music_library_layout()
                layout = build_music_library_controls(list_rect)
                content_top = layout["content_top"]
                padding = 10
                base_y = content_top
                
                visible_rows = _music_library_visible_rows()
                scroll_track_h = list_rect.bottom - padding - base_y
                max_scroll = max(1, len(music_library_tracks) - visible_rows)
                
                if scroll_track_h > 0 and max_scroll > 0:
                    indicator_h = max(30, int(scroll_track_h * (visible_rows / len(music_library_tracks))))
                    delta_y = my - music_library_drag_start_y
                    scroll_ratio = delta_y / (scroll_track_h - indicator_h) if (scroll_track_h - indicator_h) > 0 else 0
                    new_scroll = music_library_drag_start_scroll + scroll_ratio * max_scroll
                    music_library_scroll_index = max(0, min(int(new_scroll), max_scroll))
            else:
                music_library_dragging_scrollbar = False

        # 音效实验室滚动条拖动更新
        if game_state == "sound_lab" and sound_lab_dragging_scrollbar:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                mx, my = pygame.mouse.get_pos()
                list_rect, _, _ = get_sound_lab_layout()
                _, filter_band_height = get_sound_lab_filter_layout(list_rect)
                content_top = list_rect.y + 12 + filter_band_height
                padding = 10
                
                visible_rows = _sound_lab_visible_rows()
                scroll_track_h = list_rect.height - padding * 2 - filter_band_height
                max_scroll = max(1, len(sound_lab_tracks) - visible_rows)
                
                if scroll_track_h > 0 and max_scroll > 0:
                    indicator_h = max(30, int(scroll_track_h * (visible_rows / len(sound_lab_tracks))))
                    delta_y = my - sound_lab_drag_start_y
                    scroll_ratio = delta_y / (scroll_track_h - indicator_h) if (scroll_track_h - indicator_h) > 0 else 0
                    new_scroll = sound_lab_drag_start_scroll + scroll_ratio * max_scroll
                    sound_lab_scroll_index = max(0, min(int(new_scroll), max_scroll))
            else:
                sound_lab_dragging_scrollbar = False

        # 排行榜滚动条拖动更新
        if game_state == "leaderboard" and leaderboard_dragging_scrollbar:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                mx, my = pygame.mouse.get_pos()
                scrollbar_info = _leaderboard_cache.get("scrollbar_info")
                if scrollbar_info:
                    track_rect = scrollbar_info["track_rect"]
                    thumb_rect = scrollbar_info["thumb_rect"]
                    max_scroll = scrollbar_info["max_scroll"]
                    
                    if max_scroll > 0:
                        track_height = track_rect.height - thumb_rect.height
                        delta_y = my - leaderboard_drag_start_y
                        scroll_ratio = delta_y / track_height if track_height > 0 else 0
                        new_scroll = leaderboard_drag_start_scroll + scroll_ratio * max_scroll
                        leaderboard_scroll_y = max(0, min(int(new_scroll), max_scroll))
            else:
                leaderboard_dragging_scrollbar = False

        if game_state == "menu": 
            draw_menu_ui()
        elif game_state == "audio_hub":
            draw_audio_hub_ui()
        elif game_state == "music_library":
            draw_music_library_ui()
        elif game_state == "sound_lab":
            draw_sound_lab_ui()
        elif game_state == "mode_select":
            draw_mode_select_ui()
        elif game_state == "select_plane": 
            draw_select_plane_ui()
            # drawing select plane page
        elif game_state == "boss_challenge":
            draw_boss_challenge_ui()
        elif game_state == "boss_challenge_select_plane":
            draw_select_plane_ui()
        elif game_state == "arsenal": 
            draw_arsenal_ui()
        elif game_state == "background_settings":
            draw_background_settings_ui()
        elif game_state == "gallery": 
            draw_gallery_ui()
        elif game_state == "codex": 
            draw_codex_ui()
        elif game_state == "gameover":
            # 保持最后一帧画面
            if frozen_screen is None:
                try:
                    frozen_screen = screen.copy()
                    red = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    red.fill((50, 0, 0, 100))
                    frozen_screen.blit(red, (0,0))
                except Exception:
                    frozen_screen = None
            if frozen_screen:
                safe_blit(screen, frozen_screen, (0,0))

            # 文字动画
            draw_text(screen, "MISSION FAILED", 60, WIDTH/2, HEIGHT/2 - 50, RED, glow=True)
            draw_text(screen, "机体信号丢失...", 20, WIDTH/2, HEIGHT/2 + 20, WHITE)
            
            # 【新】快速重开提示
            pulse = int(200 + 55 * abs(math.sin(pygame.time.get_ticks() / 400)))
            draw_text(screen, "按 [R] 快速重开", 24, WIDTH/2, HEIGHT/2 + 80, (pulse, pulse, 100), glow=True)
            draw_text(screen, "或等待进入排行榜...", 16, WIDTH/2, HEIGHT/2 + 120, GRAY)

            # 自动倒计时跳转
            game_over_timer += 1
            if game_over_timer > 120: # 2秒后 (60FPS * 2)
                game_state = "input_name"
                player_name = ""
                frozen_screen = None

        elif game_state == "input_name":
            # 背景
            screen.fill(BLACK)
            try:
                bg_manager.draw(screen)
            except Exception:
                pass
            # 标题
            draw_text(screen, "记录黑匣子数据", 40, WIDTH/2, 200, CYAN, glow=True)
            draw_text(screen, f"最终得分: {int(final_score)}", 30, WIDTH/2, 260, YELLOW)
            # 输入框
            box_w, box_h = 300, 60
            box_x, box_y = (WIDTH - box_w)//2, 400
            draw_cyber_rect(screen, (box_x, box_y, box_w, box_h), (30, 30, 40), fill=True)
            draw_cyber_rect(screen, (box_x, box_y, box_w, box_h), CYAN, border_width=2, fill=False)
            # 显示玩家输入的名字 (加个光标效果)
            cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            display_text = player_name + cursor
            draw_text(screen, display_text, 36, WIDTH/2, box_y + 15, WHITE)
            # 提示
            draw_text(screen, "输入代号并按 [ENTER] 确认", 18, WIDTH/2, box_y + 80, GRAY)

        elif game_state == "achievements":
            draw_achievements_ui()
        elif game_state == "settings":
            draw_settings_ui()
        elif game_state == "leaderboard": 
            draw_leaderboard_ui()
        elif game_state == "customization":
            draw_customization_ui()
        elif game_state == "game" or game_state == "boss_challenge_play":
            if room_completion_paused and not is_paused:
                is_paused = True
            # drawing game view
            if is_paused:
                # M键地图暂停：显示地图界面
                if map_paused:
                    # 显示冻结的游戏画面作为背景
                    if frozen_screen:
                        screen.blit(frozen_screen, (0, 0))
                    # 显示地图
                    if show_full_map and room_manager:
                        safe_call_draw(lambda: room_manager.draw_fullmap(screen))
                # TAB 发起的暂停使用专门的处理：按住 TAB 显示属性面板，释放恢复
                elif tab_paused:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_TAB]:
                        # 如果存在冻结屏幕，用它作为背景
                        if frozen_screen:
                            try:
                                safe_blit(screen, frozen_screen, (0, 0))
                            except Exception:
                                s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                                s.fill((0, 0, 0, 150))
                                safe_blit(screen, s, (0, 0))
                        safe_call_draw(draw_player_stats_panel)
                    else:
                        # TAB 已释放：清理并恢复
                        tab_paused = False
                        frozen_screen = None
                        is_paused = False
                elif room_manager and room_manager.show_shop_ui:
                    # 商店界面：显示冻结画面作为背景
                    if frozen_screen:
                        safe_blit(screen, frozen_screen, (0, 0))
                    else:
                        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                        s.fill((0, 0, 0, 180))
                        safe_blit(screen, s, (0, 0))
                    # 在暂停分支中直接绘制商店UI
                    safe_call_draw(lambda: room_manager.draw_shop_ui(screen))
                elif room_manager and room_manager.show_completion_ui:
                    # 房间完成时仅冻结画面，交由房间UI渲染
                    if frozen_screen:
                        safe_blit(screen, frozen_screen, (0, 0))
                    else:
                        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                        s.fill((0, 0, 0, 180))
                        safe_blit(screen, s, (0, 0))
                    # 在暂停分支中直接绘制房间选择UI
                    safe_call_draw(lambda: room_manager.draw_room_selection_ui(screen))
                else:
                    # 常规由 P / 菜单触发的暂停界面（原有行为）
                    all_sprites.draw(screen)
                    # 绘制物品
                    if item_manager:
                        item_manager.draw(screen)
                    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    s.fill((0, 0, 0, 150))
                    safe_blit(screen, s, (0, 0))
                    draw_text(screen, "PAUSED", 60, WIDTH // 2, HEIGHT // 2 - 180, WHITE, glow=True)

                    # 绘制暂停菜单按钮（支持键盘导航）
                    cx, cy = WIDTH // 2, HEIGHT // 2
                    btn_resume = pygame.Rect(cx - 100, cy - 60, 200, 50)
                    btn_reset = pygame.Rect(cx - 100, cy + 10, 200, 50)
                    btn_menu = pygame.Rect(cx - 100, cy + 80, 200, 50)

                    mx, my = pygame.mouse.get_pos()

                    menu_items = [(btn_resume, "继续行动", "[ESC]"), (btn_reset, "重新开始", "[R]"), (btn_menu, "退出战斗", "[Q]")]
                    for i, (btn, txt, hotkey) in enumerate(menu_items):
                        h = btn.collidepoint(mx, my) or (i == pause_menu_selected)
                        draw_cyber_rect(screen, btn, (60, 60, 80) if h else (40, 40, 50), fill=True)
                        border_color = CYAN if i == pause_menu_selected else (WHITE if h else GRAY)
                        border_width = 3 if i == pause_menu_selected else 2
                        draw_cyber_rect(screen, btn, border_color, border_width=border_width, fill=False)
                        draw_text(screen, txt, 24, btn.centerx - 40, btn.centery - 12, WHITE if h else GRAY)
                        # 【新】快捷键提示
                        draw_text(screen, hotkey, 16, btn.centerx + 70, btn.centery - 12, (150, 150, 150))

                    draw_text(screen, "按 P 继续 / 方向键+Enter 选择 / TAB 查看面板", 18, WIDTH // 2, HEIGHT - 50, GRAY)

            else:
                # 射击逻辑：自动或手动
                if not levelup_paused:
                    auto_fire = game_settings.get("auto_fire", True)
                    if auto_fire:
                        # 自动射击
                        player.shoot()
                    else:
                        # 手动射击（按住空格键）
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_SPACE]:
                            player.shoot()
                
                if global_time_freeze > 0:
                    global_time_freeze -= 1
                    # 【改进】时间冻结期间，处理敌方子弹的冻结状态
                    for eb in enemy_bullets:
                        eb.frozen = True
                    player.update()
                    # 【统计】时间计数和连击衰减
                    player.stats['time_played'] += 1
                    if player.stats['combo_timer'] > 0:
                        player.stats['combo_timer'] -= 1
                        if player.stats['combo_timer'] == 0:
                            player.stats['current_combo'] = 0
                    
                    # === 新卡牌系统：持续效果更新 ===
                    
                    # 6. 轨道打击 - 定时激光攻击
                    if hasattr(player, 'has_orbital_strike') and player.has_orbital_strike:
                        if not hasattr(player, 'strike_timer'):
                            player.strike_timer = 0
                        
                        player.strike_timer += 1
                        strike_cooldown = getattr(player, 'strike_cooldown', 600)
                        
                        if player.strike_timer >= strike_cooldown:
                            player.strike_timer = 0
                            # 选择最近的敌人
                            if mobs:
                                target = min(mobs, key=lambda e: math.hypot(
                                    e.rect.centerx - player.rect.centerx,
                                    e.rect.centery - player.rect.centery
                                ))
                                strike_damage = getattr(player, 'strike_damage', 500)
                                target.hp -= strike_damage
                                # 视觉效果 - 激光从天而降
                                pygame.draw.line(screen, (255, 255, 255), 
                                               (target.rect.centerx, 0), 
                                               target.rect.center, 8)
                                pygame.draw.line(screen, (255, 200, 0), 
                                               (target.rect.centerx, 0), 
                                               target.rect.center, 4)
                                pygame.draw.circle(screen, (255, 255, 255), target.rect.center, 80, 4)
                                FloatingText(target.rect.centerx, target.rect.top - 40, 
                                           f"轨道打击 -{int(strike_damage)}", (255, 200, 0))
                                for _ in range(15):
                                    Particle(target.rect.center, (255, 200, 0))
                    
                    # 7. 治疗光环 - 持续回复
                    if hasattr(player, 'has_healing_aura') and player.has_healing_aura:
                        if not hasattr(player, 'heal_timer'):
                            player.heal_timer = 0
                        
                        player.heal_timer += 1
                        if player.heal_timer >= 60:  # 每秒回复
                            player.heal_timer = 0
                            heal_amount = getattr(player, 'heal_per_sec', 3)
                            aura_radius = getattr(player, 'aura_radius', 200)
                            
                            # 回复玩家
                            if player.hp < player.max_hp:
                                player.hp = min(player.max_hp, player.hp + heal_amount)
                                FloatingText(player.rect.centerx, player.rect.top - 20, 
                                           f"+{heal_amount}", (100, 255, 100))
                            
                            # 回复僚机
                            if hasattr(player, 'wingmen'):
                                for wingman in player.wingmen:
                                    if hasattr(wingman, 'hp') and hasattr(wingman, 'max_hp'):
                                        if wingman.hp < wingman.max_hp:
                                            wingman.hp = min(wingman.max_hp, wingman.hp + heal_amount)
                            
                            # 光环视觉效果（增强）
                            aura_t = pygame.time.get_ticks() / 600
                            # 持续可见的脉动光环
                            for i in range(3):
                                wave_radius = int(aura_radius * (0.6 + i * 0.2 + math.sin(aura_t + i) * 0.1))
                                wave_alpha = int(60 - i * 15)
                                wave_surf = pygame.Surface((wave_radius*2, wave_radius*2), pygame.SRCALPHA)
                                pygame.draw.circle(wave_surf, (100, 255, 150, wave_alpha),
                                                 (wave_radius, wave_radius), wave_radius, 3)
                                screen.blit(wave_surf, (player.rect.centerx - wave_radius,
                                                       player.rect.centery - wave_radius))
                            # 治疗粒子效果
                            if random.random() < 0.2:
                                angle = random.uniform(0, math.pi * 2)
                                dist = random.uniform(0, aura_radius * 0.8)
                                px = player.rect.centerx + math.cos(angle) * dist
                                py = player.rect.centery + math.sin(angle) * dist
                                Particle((int(px), int(py)), (100, 255, 150))
                    
                    # 8. 超载射击 - 周期性高威力子弹
                    if hasattr(player, 'has_overcharge') and player.has_overcharge:
                        if not hasattr(player, 'overcharge_timer'):
                            player.overcharge_timer = 0
                        
                        overcharge_cooldown = getattr(player, 'overcharge_cooldown', 180)  # 3秒
                        overcharge_mult = getattr(player, 'overcharge_mult', 5.0)
                        overcharge_pierce = getattr(player, 'overcharge_pierce', 0)
                        
                        player.overcharge_timer += 1
                        
                        # 充能提示（最后1秒）
                        if player.overcharge_timer >= overcharge_cooldown - 60 and player.overcharge_timer % 10 == 0:
                            pygame.draw.circle(screen, (255, 200, 0), player.rect.center, 
                                             30 + (60 - (overcharge_cooldown - player.overcharge_timer)) // 2, 2)
                        
                        if player.overcharge_timer >= overcharge_cooldown:
                            player.overcharge_timer = 0
                            
                            # 发射超载子弹
                            from sprites import Bullet
                            overcharge_bullet = Bullet(
                                player.rect.centerx, 
                                player.rect.top,
                                color=(255, 215, 0),
                                b_type="beam",
                                piercing=overcharge_pierce if overcharge_pierce > 0 else player.piercing,
                                homing=player.homing_level,
                                bounce=getattr(player, 'bounce_count', 0),
                                bounce_damage=getattr(player, 'bounce_damage', 1.0)
                            )
                            overcharge_bullet.speed = -30
                            overcharge_bullet.damage = int(player.damage * overcharge_mult)
                            
                            # 超载特效
                            FloatingText(player.rect.centerx, player.rect.top - 30,
                                       f"超载 ×{int(overcharge_mult)}", (255, 215, 0), font_size=24)
                            # 冲击波
                            for r in range(3):
                                radius = 30 + r * 15
                                pygame.draw.circle(screen, (255, 215, 0, 200 - r * 60),
                                                 player.rect.center, radius, 3)
                            # 金色粒子
                            for _ in range(15):
                                angle = random.uniform(0, math.pi * 2)
                                distance = random.uniform(20, 50)
                                px = player.rect.centerx + math.cos(angle) * distance
                                py = player.rect.centery + math.sin(angle) * distance
                                Particle((int(px), int(py)), (255, 215, 0))
                            
                            sound_mgr.play("powerup")
                    
                    # 9. 专注系统 - 静止时累积专注
                    if hasattr(player, 'has_focus') and player.has_focus:
                        if not hasattr(player, 'focus_stationary_time'):
                            player.focus_stationary_time = 0
                            player.current_focus = 0
                        
                        # 检测是否移动
                        if abs(player.vel.x) < 0.1 and abs(player.vel.y) < 0.1:
                            player.focus_stationary_time += 1
                            focus_per_sec = getattr(player, 'focus_per_sec', 0.2)
                            max_focus = getattr(player, 'max_focus', 3.0)
                            
                            if player.focus_stationary_time >= 60:  # 每秒
                                player.focus_stationary_time = 0
                                player.current_focus = min(max_focus, 
                                                          player.current_focus + focus_per_sec)
                                
                                # 应用专注伤害加成
                                if not hasattr(player, 'base_damage'):
                                    player.base_damage = player.damage
                                player.damage = player.base_damage * (1 + player.current_focus)
                                
                                # 视觉提示
                                if player.current_focus > 0:
                                    focus_color = (255, int(255 * (1 - player.current_focus / max_focus)), 0)
                                    pygame.draw.circle(screen, focus_color, player.rect.center, 
                                                     30, 2)
                        else:
                            # 移动时专注衰减
                            player.current_focus = max(0, player.current_focus - 0.05)
                            if hasattr(player, 'base_damage'):
                                player.damage = player.base_damage * (1 + player.current_focus)
                    
                    # 【新】复活冷却计时器
                    if hasattr(player, 'revive_hp') and player.revive_hp > 0:
                        if not hasattr(player, 'revive_cooldown_timer'):
                            player.revive_cooldown_timer = 0
                        # 每帧递增冷却计时器
                        revive_cooldown = getattr(player, 'revive_cooldown', 3600)
                        if player.revive_cooldown_timer < revive_cooldown:
                            player.revive_cooldown_timer += 1
                    
                    # 10. 弹幕风暴 - 持续圆形弹幕
                    if hasattr(player, 'has_storm') and player.has_storm:
                        if not hasattr(player, 'storm_active'):
                            player.storm_active = False
                            player.storm_timer = 0
                            player.storm_cooldown_timer = 0
                            player.storm_angle = 0
                        
                        storm_cooldown = 1200  # 20秒CD
                        
                        if not player.storm_active:
                            player.storm_cooldown_timer += 1
                            if player.storm_cooldown_timer >= storm_cooldown:
                                player.storm_active = True
                                player.storm_timer = 0
                                player.storm_cooldown_timer = 0
                                FloatingText(player.rect.centerx, player.rect.top - 40, 
                                           "弹幕风暴!", (255, 150, 0), font_size=28)
                        else:
                            storm_duration = getattr(player, 'storm_duration', 240)  # 4秒持续（优化）
                            storm_bullets = getattr(player, 'storm_bullets', 12)  # 减少数量避免卡顿
                            
                            player.storm_timer += 1
                            
                            # 每帧发射多发子弹形成环形
                            if player.storm_timer % 12 == 0:  # 每0.2秒（优化间隔）
                                angle_step = 360 / storm_bullets
                                for i in range(storm_bullets):
                                    angle = player.storm_angle + (i * angle_step)
                                    from sprites import Bullet
                                    b = Bullet(player.rect.centerx, player.rect.centery, 
                                             angle=angle, color=(255, 180, 0), b_type="star",
                                             bounce=getattr(player, 'bounce_count', 0),
                                             bounce_damage=getattr(player, 'bounce_damage', 1.0))
                                    b.speed = -15
                                    # 风暴子弹伤害为30%
                                    if hasattr(b, 'damage'):
                                        b.damage = int(player.damage * 0.3)
                                
                                player.storm_angle = (player.storm_angle + 15) % 360
                                
                                # 视觉：旋转圆环
                                for j in range(3):
                                    radius = 40 + j * 20
                                    pygame.draw.circle(screen, (255, 200 - j * 50, 0, 150), 
                                                     player.rect.center, radius, 2)
                            
                            if player.storm_timer >= storm_duration:
                                player.storm_active = False
                    
                    # 11. 时空静滞场 - 完全冻结
                    if hasattr(player, 'has_stasis') and player.has_stasis:
                        if not hasattr(player, 'stasis_timer'):
                            player.stasis_timer = 0
                        
                        stasis_cooldown = 900  # 15秒CD
                        player.stasis_timer += 1
                        
                        if player.stasis_timer >= stasis_cooldown:
                            player.stasis_timer = 0
                            stasis_duration = getattr(player, 'stasis_duration', 180)  # 3秒冻结
                            stasis_radius = getattr(player, 'stasis_radius', 120)
                            
                            frozen_count = 0
                            for enemy in mobs:
                                dist = math.hypot(enemy.rect.centerx - player.rect.centerx,
                                                enemy.rect.centery - player.rect.centery)
                                if dist <= stasis_radius:
                                    enemy.frozen_timer = stasis_duration
                                    frozen_count += 1
                                    # 紫色冻结粒子
                                    for _ in range(8):
                                        Particle(enemy.rect.center, (180, 0, 255))
                            
                            if frozen_count > 0:
                                FloatingText(player.rect.centerx, player.rect.top - 30,
                                           f"时空静滞 {frozen_count}", (200, 100, 255), font_size=22)
                                # 时空波纹
                                for r in range(3):
                                    radius = stasis_radius + r * 20
                                    pygame.draw.circle(screen, (180, 0, 255, 180 - r * 50),
                                                     player.rect.center, radius, 3)
                    
                    # 12. 能量护盾系统
                    if hasattr(player, 'has_barrier') and player.has_barrier:
                        if not hasattr(player, 'barrier_current_hp'):
                            player.barrier_current_hp = getattr(player, 'barrier_hp', 50)
                            player.barrier_recharge_timer = 0
                        
                        barrier_max = getattr(player, 'barrier_hp', 50)
                        barrier_recharge_delay = getattr(player, 'barrier_recharge', 600)  # 10秒
                        
                        # 护盾充能
                        if player.barrier_current_hp < barrier_max:
                            player.barrier_recharge_timer += 1
                            if player.barrier_recharge_timer >= barrier_recharge_delay:
                                recharge_amount = 1
                                player.barrier_current_hp = min(barrier_max, 
                                                               player.barrier_current_hp + recharge_amount)
                                # 充能完成
                                if player.barrier_current_hp >= barrier_max:
                                    FloatingText(player.rect.centerx, player.rect.top - 20,
                                               "护盾充能", (0, 200, 255), font_size=16)
                                    player.barrier_recharge_timer = 0
                        
                        # 护盾视觉
                        if player.barrier_current_hp > 0:
                            barrier_ratio = player.barrier_current_hp / barrier_max
                            barrier_alpha = int(100 * barrier_ratio)
                            barrier_radius = 35
                            barrier_surface = pygame.Surface((barrier_radius * 2, barrier_radius * 2), 
                                                            pygame.SRCALPHA)
                            pygame.draw.circle(barrier_surface, (0, 200, 255, barrier_alpha),
                                             (barrier_radius, barrier_radius), barrier_radius)
                            screen.blit(barrier_surface, 
                                      (player.rect.centerx - barrier_radius, 
                                       player.rect.centery - barrier_radius))
                    
                    # 13. 召唤仆从
                    if hasattr(player, 'has_minions') and player.has_minions:
                        if not hasattr(player, 'minions'):
                            player.minions = []
                            player.minion_spawn_timer = 0
                        
                        minion_count = getattr(player, 'minion_count', 3)
                        minion_hp = getattr(player, 'minion_hp', 20)
                        minion_damage = getattr(player, 'minion_damage', 10)
                        
                        # 生成仆从
                        if len(player.minions) < minion_count:
                            player.minion_spawn_timer += 1
                            if player.minion_spawn_timer >= 120:  # 每2秒生成1个
                                player.minion_spawn_timer = 0
                                angle = random.uniform(0, 360)
                                distance = 50
                                minion_x = player.rect.centerx + math.cos(math.radians(angle)) * distance
                                minion_y = player.rect.centery + math.sin(math.radians(angle)) * distance
                                
                                minion = {
                                    'x': minion_x,
                                    'y': minion_y,
                                    'hp': minion_hp,
                                    'max_hp': minion_hp,
                                    'damage': minion_damage,
                                    'angle': angle,
                                    'orbit_angle': angle,
                                    'shoot_timer': 0
                                }
                                player.minions.append(minion)
                                FloatingText(int(minion_x), int(minion_y), 
                                           "召唤!", (255, 200, 255), font_size=14)
                        
                        # 更新仆从
                        for minion in player.minions[:]:
                            if minion['hp'] <= 0:
                                player.minions.remove(minion)
                                continue
                            
                            # 环绕玩家
                            minion['orbit_angle'] += 2
                            orbit_radius = 60
                            target_x = player.rect.centerx + math.cos(math.radians(minion['orbit_angle'])) * orbit_radius
                            target_y = player.rect.centery + math.sin(math.radians(minion['orbit_angle'])) * orbit_radius
                            
                            minion['x'] += (target_x - minion['x']) * 0.1
                            minion['y'] += (target_y - minion['y']) * 0.1
                            
                            # 自动攻击
                            minion['shoot_timer'] += 1
                            if minion['shoot_timer'] >= 30:  # 每0.5秒
                                minion['shoot_timer'] = 0
                                if mobs:
                                    nearest = min(mobs, key=lambda m: math.hypot(
                                        m.rect.centerx - minion['x'],
                                        m.rect.centery - minion['y']
                                    ))
                                    if math.hypot(nearest.rect.centerx - minion['x'],
                                                nearest.rect.centery - minion['y']) < 300:
                                        dx = nearest.rect.centerx - minion['x']
                                        dy = nearest.rect.centery - minion['y']
                                        angle = math.degrees(math.atan2(dy, dx))
                                        
                                        from sprites import Bullet
                                        b = Bullet(int(minion['x']), int(minion['y']), 
                                                 angle=angle, color=(255, 150, 255), 
                                                 b_type="orb", piercing=0)
                                        b.speed = -12
                                        b.damage = minion['damage']
                            
                            # 绘制仆从（增强视觉）
                            minion_x_int = int(minion['x'])
                            minion_y_int = int(minion['y'])
                            
                            # 外层发光光晕
                            glow_t = pygame.time.get_ticks() / 500
                            for i in range(3):
                                radius = 12 + i * 4 + abs(math.sin(glow_t)) * 3
                                alpha = 100 - i * 30
                                glow_surf = pygame.Surface((radius*2+2, radius*2+2), pygame.SRCALPHA)
                                pygame.draw.circle(glow_surf, (255, 100, 255, alpha), 
                                                 (radius+1, radius+1), int(radius))
                                screen.blit(glow_surf, (minion_x_int - radius - 1, 
                                                       minion_y_int - radius - 1))
                            
                            # 主体 - 渐变核心
                            for r in range(10, 0, -2):
                                alpha = 255 - r * 15
                                pygame.draw.circle(screen, (255, 150 - r * 5, 255, alpha), 
                                                 (minion_x_int, minion_y_int), r)
                            
                            # 能量核心
                            pygame.draw.circle(screen, (255, 255, 255), 
                                             (minion_x_int, minion_y_int), 3)
                            
                            # 旋转能量环
                            ring_angle = (pygame.time.get_ticks() / 30 + minion['orbit_angle']) % 360
                            for i in range(4):
                                angle_rad = math.radians(ring_angle + i * 90)
                                px = minion_x_int + math.cos(angle_rad) * 10
                                py = minion_y_int + math.sin(angle_rad) * 10
                                pygame.draw.circle(screen, (255, 200, 255), (int(px), int(py)), 2)
                            
                            # 外边框
                            pygame.draw.circle(screen, (255, 200, 255),
                                             (minion_x_int, minion_y_int), 11, 2)
                            # HP条
                            if minion['hp'] < minion['max_hp']:
                                hp_ratio = minion['hp'] / minion['max_hp']
                                bar_w = 16
                                bar_h = 3
                                bar_x = int(minion['x']) - bar_w // 2
                                bar_y = int(minion['y']) - 15
                                pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_w, bar_h))
                                pygame.draw.rect(screen, (255, 0, 100), 
                                               (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))
                    
                    # 14. 支援站点
                    if hasattr(player, 'has_station') and player.has_station:
                        if not hasattr(player, 'station'):
                            player.station = None
                            player.station_spawn_timer = 0
                        
                        # 生成站点（10秒CD）
                        if player.station is None:
                            player.station_spawn_timer += 1
                            if player.station_spawn_timer >= 600:
                                player.station = {
                                    'x': player.rect.centerx,
                                    'y': player.rect.centery,
                                    'duration': 1800,  # 30秒持续
                                    'timer': 0
                                }
                                FloatingText(player.rect.centerx, player.rect.centery,
                                           "支援站点", (0, 255, 200), font_size=20)
                                player.station_spawn_timer = 0
                        
                        # 更新站点
                        if player.station:
                            player.station['timer'] += 1
                            
                            if player.station['timer'] >= player.station['duration']:
                                player.station = None
                            else:
                                station_x = player.station['x']
                                station_y = player.station['y']
                                station_radius = getattr(player, 'station_radius', 250)
                                station_buff = getattr(player, 'station_buff', 0.5)
                                
                                # 检查玩家是否在范围内
                                dist_to_player = math.hypot(player.rect.centerx - station_x,
                                                           player.rect.centery - station_y)
                                if dist_to_player <= station_radius:
                                    # 应用增益（1.5倍伤害）
                                    if not hasattr(player, 'station_buffed'):
                                        player.base_damage_before_station = player.damage
                                        player.station_buffed = True
                                    player.damage = player.base_damage_before_station * (1 + station_buff)
                                else:
                                    if hasattr(player, 'station_buffed') and player.station_buffed:
                                        player.damage = player.base_damage_before_station
                                        player.station_buffed = False
                                
                                # 绘制站点（增强视觉）
                                station_t = pygame.time.get_ticks() / 400
                                
                                # 外层光晕（脉动）
                                for i in range(4):
                                    glow_radius = 20 + i * 8 + abs(math.sin(station_t)) * 5
                                    glow_alpha = 80 - i * 20
                                    glow_surf = pygame.Surface((glow_radius*2+2, glow_radius*2+2), pygame.SRCALPHA)
                                    pygame.draw.circle(glow_surf, (0, 255, 200, glow_alpha), 
                                                     (glow_radius+1, glow_radius+1), int(glow_radius))
                                    screen.blit(glow_surf, (station_x - glow_radius - 1, 
                                                           station_y - glow_radius - 1))
                                
                                # 底座主体 - 渐变
                                for r in range(15, 0, -3):
                                    alpha = 255 - r * 10
                                    pygame.draw.circle(screen, (0, 180 + (15-r)*5, 150 + (15-r)*7, alpha), 
                                                     (station_x, station_y), r)
                                
                                # 能量核心
                                pygame.draw.circle(screen, (255, 255, 255), 
                                                 (station_x, station_y), 5)
                                
                                # 旋转能量环
                                ring_angle = (pygame.time.get_ticks() / 20) % 360
                                for i in range(6):
                                    angle_rad = math.radians(ring_angle + i * 60)
                                    px = station_x + math.cos(angle_rad) * 18
                                    py = station_y + math.sin(angle_rad) * 18
                                    pygame.draw.circle(screen, (0, 255, 200), (int(px), int(py)), 3)
                                
                                # 十字天线
                                cross_size = 12
                                pygame.draw.line(screen, (0, 255, 200),
                                               (station_x - cross_size, station_y),
                                               (station_x + cross_size, station_y), 4)
                                pygame.draw.line(screen, (0, 255, 200),
                                               (station_x, station_y - cross_size),
                                               (station_x, station_y + cross_size), 4)
                                
                                # 外边框
                                pygame.draw.circle(screen, (0, 255, 200),
                                                 (station_x, station_y), 20, 3)
                                
                                # 范围圈（持续可见，透明度变化）
                                range_alpha = int(50 + 30 * abs(math.sin(station_t * 1.5)))
                                range_surf = pygame.Surface((station_radius*2, station_radius*2), pygame.SRCALPHA)
                                pygame.draw.circle(range_surf, (0, 255, 200, range_alpha),
                                                 (station_radius, station_radius), station_radius, 3)
                                screen.blit(range_surf, (station_x - station_radius, 
                                                        station_y - station_radius))
                    
                    # 【新】冰霜新星：周期性范围冻结
                    if hasattr(player, 'card_effect_processor'):
                        frost_result = player.card_effect_processor.update(1)
                        if frost_result and frost_result.get("frost_nova"):
                            freeze_duration = getattr(player, 'freeze_duration', 120)
                            freeze_radius = getattr(player, 'freeze_radius', 100)
                            
                            # 冻结范围内所有敌人
                            frozen_count = 0
                            for enemy in mobs:
                                dist = math.hypot(
                                    enemy.rect.centerx - player.rect.centerx,
                                    enemy.rect.centery - player.rect.centery
                                )
                                if dist <= freeze_radius:
                                    enemy.frozen_timer = freeze_duration
                                    frozen_count += 1
                            
                            if frozen_count > 0:
                                # 冰霜新星视觉效果 - 增强版
                                # 1. 多层冰霜冲击波(扩散动画效果)
                                for r in range(3):
                                    radius = int(freeze_radius * (0.3 + r * 0.35))
                                    thickness = 4 - r
                                    alpha_color = (100 + r * 50, 200 + r * 20, 255)
                                    pygame.draw.circle(screen, alpha_color, player.rect.center, radius, thickness)
                                
                                # 2. 大量冰晶粒子(密集效果)
                                for _ in range(50):
                                    angle = random.uniform(0, math.pi * 2)
                                    dist = random.uniform(freeze_radius * 0.3, freeze_radius)
                                    px = player.rect.centerx + math.cos(angle) * dist
                                    py = player.rect.centery + math.sin(angle) * dist
                                    Particle((int(px), int(py)), CYAN)
                                
                                # 3. 冻结敌人上方显示冰晶标记
                                for enemy in mobs:
                                    if enemy.frozen_timer > 0:
                                        FloatingText(enemy.rect.centerx, enemy.rect.top - 20, "❄", CYAN)
                                
                                # 4. 中心爆发特效
                                for _ in range(15):
                                    Particle(player.rect.center, (200, 230, 255))
                                
                                sound_mgr.play("powerup")
                    
                    for s in all_sprites:
                        if isinstance(s, (Particle, FloatingText, FinalBeam, TimeSlash, NukeExplosion, AuroraCurtain, DeathScythe, BlackHole)): s.update()
                else:
                    # 时间冻结结束，解冻敌方子弹
                    for eb in enemy_bullets:
                        eb.frozen = False
                    if levelup_paused:
                        # During level-up selection, freeze entities (enemies, bullets, player), but allow UI particles/text to animate
                        for s in list(all_sprites):
                            if isinstance(s, (Particle, FloatingText, FinalBeam, TimeSlash, NukeExplosion, AuroraCurtain, DeathScythe, BlackHole)):
                                try:
                                    s.update()
                                except Exception:
                                    pass
                    else:
                        # 应用时间膨胀效果到敌人
                        time_factor = getattr(player, 'time_factor', 1.0)
                        for enemy in mobs:
                            # 应用时间减速：timer 增速会被减缓，导致攻击/移动更慢
                            # 现在敌人会在 timer % X == 0 时攻击，time_factor < 1 时会延长间隔
                            enemy.time_slow_factor = time_factor
                        
                        all_sprites.update()
                        
                        # 【修复】检测被技能杀死的敌人（take_damage导致hp<=0但未经子弹碰撞处理）
                        for m in list(mobs):
                            if m.hp <= 0 and not getattr(m, '_death_rewarded', False):
                                m._death_rewarded = True  # 标记已处理，防止重复
                                
                                # 加分
                                score += 100 if m.is_elite else 20
                                
                                # 游戏统计 - 击杀数
                                game_stats["kills"] = game_stats.get("kills", 0) + 1
                                
                                # 重置击杀计时
                                last_kill_timer = 0
                                
                                # 【统计】记录击杀和更新连击
                                player.stats['kills'] += 1
                                player.stats['current_combo'] += 1
                                player.stats['combo_timer'] = 180
                                if player.stats['current_combo'] > player.stats['max_combo']:
                                    player.stats['max_combo'] = player.stats['current_combo']
                                
                                # 击杀特效
                                create_explosion(m.rect.center, CYAN, 5)
                                sound_mgr.play("explosion")
                                
                                # 经验掉落
                                enemy_strength_map = {
                                    "wisp": 6,
                                    "orbiter": 10,
                                    "bulwark": 12,
                                }
                                base_xp = enemy_strength_map.get(m.type, 5)
                                elite_multiplier = 3.0 if m.is_elite else 1.0
                                level_multiplier = 1.0 + (player.level - 1) * 0.10
                                xp_amount = max(5, int(base_xp * elite_multiplier * level_multiplier))
                                ExperienceOrb(m.rect.centerx, m.rect.centery, xp_amount)
                                FloatingText(m.rect.centerx, m.rect.top - 30, f"经验+{xp_amount}", LIME)
                                
                                # 物品掉落
                                if item_manager:
                                    item_manager.try_spawn_drop(m.rect.centerx, m.rect.centery)
                                
                                # 核心掉落
                                if random.random() < 0.25:
                                    arsenal_save_data["currencies"]["cores"] += 1
                                    FloatingText(m.rect.centerx, m.rect.top-20, "核心+1", CYAN)
                                
                                # 成就系统
                                if player and hasattr(player, 'achievement_manager'):
                                    player.achievement_manager.add_kill(1)
                                    new_achievements = player.achievement_manager.check_achievements(player)
                                    if new_achievements:
                                        sound_mgr.play("achievement")
                                        for ach_id in new_achievements:
                                            ach = player.achievement_manager.achievements[ach_id]
                                            achievement_notifications.append((ach, 180))
                                
                                # 触发击杀效果
                                corpse_effect = player.on_kill_enemy(m)
                                if corpse_effect:
                                    create_explosion(corpse_effect["pos"], ORANGE, 8)
                                
                                m.kill()
                        
                        # 【至尊灾厄】擦弹检测 - 敌弹接近但未命中时增加暴怒值
                        if hasattr(player, 'plane_id') and player.plane_id == "sepulcher":
                            graze_radius = getattr(player, 'sepulcher_graze_radius', 80)
                            core_radius = 15  # 核心判定点半径
                            px, py = player.rect.center
                            for eb in enemy_bullets:
                                if hasattr(eb, 'sepulcher_grazed'):
                                    continue  # 已擦过的不再计算
                                dist = math.hypot(eb.rect.centerx - px, eb.rect.centery - py)
                                if core_radius < dist < graze_radius:
                                    # 擦弹成功
                                    eb.sepulcher_grazed = True
                                    if hasattr(player, '_add_sepulcher_fury'):
                                        player._add_sepulcher_fury(5)  # 每次擦弹+5暴怒
                                    # 擦弹特效
                                    Particle((eb.rect.centerx, eb.rect.centery), (220, 20, 60))
                        
                        # 【统计】时间计数和连击衰减
                        player.stats['time_played'] += 1
                        if player.stats['combo_timer'] > 0:
                            player.stats['combo_timer'] -= 1
                            if player.stats['combo_timer'] == 0:
                                player.stats['current_combo'] = 0
                        
                        # 更新刷怪系统计时器
                        last_kill_timer += 1
                        no_damage_timer += 1
                        
                        # 更新物品掉落系统
                        if item_manager:
                            item_manager.update(player)
                            item_manager.update_buffs(player)
                        
                        # 更新房间系统（仅房间模式）
                        if room_manager and game_mode == "roguelike":
                            room_manager.update()
                            
                            # 生成房间敌人
                            if not boss_challenge_active:  # Boss挑战模式不使用房间系统
                                room_manager.spawn_room_enemies(enemy_factory, mobs, all_sprites, [boss], boss_manager)
                                # 更新波次刷怪
                                room_manager.update_wave_spawning(enemy_factory, mobs)
                            
                            # 处理非战斗房间（宝箱、休息、事件、商店等）
                            if not boss_challenge_active:
                                non_combat_data = room_manager.handle_non_combat_room()
                                if non_combat_data:
                                    action = non_combat_data.get("action")
                                    
                                    # 商店房间特殊处理
                                    if action == "shop":
                                        room_manager.show_shop_ui = True
                                        room_manager.shop_items = non_combat_data.get("shop_items", [])
                                        room_manager.shop_selected = 0
                                        is_paused = True
                                        if frozen_screen is None:
                                            frozen_screen = screen.copy()
                                    else:
                                        # 完成非战斗房间并获取奖励
                                        room_rewards = room_manager._finish_room()
                                        
                                        # 应用房间基础奖励
                                        if "exp" in room_rewards:
                                            player.gain_exp(room_rewards["exp"])
                                        if "score" in room_rewards:
                                            score += room_rewards["score"]
                                            room_manager.currency += room_rewards["score"]  # 积分也加入商店货币
                                        if "heal" in room_rewards:
                                            player.hp = min(player.max_hp, player.hp + room_rewards["heal"])
                                        if "item" in room_rewards and item_manager:
                                            for _ in range(room_rewards["item"]):
                                                item_manager.try_spawn_drop(player.rect.centerx, player.rect.centery)
                                        if "card" in room_rewards:
                                            for _ in range(room_rewards["card"]):
                                                player.gain_exp(player.exp_to_next_level)
                                        
                                        # 应用事件特殊奖励
                                        if "event_data" in non_combat_data:
                                            event_rewards = non_combat_data["event_data"].get("奖励", {})
                                            if "exp" in event_rewards:
                                                player.gain_exp(event_rewards["exp"])
                                            if "heal" in event_rewards:
                                                player.hp = min(player.max_hp, player.hp + event_rewards["heal"])
                                            if "score" in event_rewards:
                                                score += event_rewards["score"]
                                                room_manager.currency += event_rewards["score"]  # 积分也加入商店货币
                                            if "item" in event_rewards and item_manager:
                                                for _ in range(event_rewards["item"]):
                                                    item_manager.try_spawn_drop(player.rect.centerx, player.rect.centery)
                                        
                                        # 触发房间完成UI
                                        room_completion_paused = True
                                        map_paused = False
                                        show_full_map = False
                                        tab_paused = False
                                        is_paused = True
                                        if frozen_screen is None:
                                            frozen_screen = screen.copy()
                            
                            # 检测房间完成（如果完成，暂停游戏显示选择UI）
                            if not boss_challenge_active:
                                room_rewards = room_manager.check_room_completion(mobs, boss)
                                if room_rewards is not None:
                                    # 应用房间奖励
                                    if "exp" in room_rewards:
                                        player.gain_exp(room_rewards["exp"])
                                    if "score" in room_rewards:
                                        score += room_rewards["score"]
                                        room_manager.currency += room_rewards["score"]  # 积分也加入商店货币
                                    if "heal" in room_rewards:
                                        player.hp = min(player.max_hp, player.hp + room_rewards["heal"])
                                    if "item" in room_rewards and item_manager:
                                        # 在玩家位置生成物品
                                        for _ in range(room_rewards["item"]):
                                            item_manager.try_spawn_drop(player.rect.centerx, player.rect.centery)
                                    if "card" in room_rewards:
                                        # 触发卡牌选择（通过经验值触发升级）
                                        for _ in range(room_rewards["card"]):
                                            player.gain_exp(player.exp_to_next_level)
                                    
                                    # 房间完成，暂停游戏
                                    room_completion_paused = True
                                    map_paused = False
                                    show_full_map = False
                                    tab_paused = False
                                    is_paused = True
                                    if frozen_screen is None:
                                        frozen_screen = screen.copy()
                        
                        # 【剧毒蝰蛇】处理敌人的中毒效果
                        for enemy in mobs:
                            if hasattr(enemy, 'poison_timer') and enemy.poison_timer > 0:
                                enemy.poison_timer -= 1
                                # 检查毒伤害tick（每30帧=0.5秒触发一次）
                                if not hasattr(enemy, 'poison_tick_cd'):
                                    enemy.poison_tick_cd = 0
                                enemy.poison_tick_cd += 1
                                if enemy.poison_tick_cd >= 30:  # 每0.5秒
                                    enemy.poison_tick_cd = 0
                                    poison_dmg = getattr(enemy, 'poison_damage', 5)
                                    enemy.hp -= poison_dmg
                                    # 毒伤害文字（绿色）
                                    FloatingText(enemy.rect.centerx, enemy.rect.top - 10, 
                                               f"-{int(poison_dmg)}", (0, 255, 100))
                                    # 毒伤害粒子
                                    Particle(enemy.rect.center, (0, 200, 80))
                                    # 检查是否因中毒死亡
                                    if enemy.hp <= 0 and not getattr(enemy, '_death_rewarded', False):
                                        enemy._death_rewarded = True
                                        score += 100 if enemy.is_elite else 20
                                        game_stats["kills"] = game_stats.get("kills", 0) + 1
                                        create_explosion(enemy.rect.center, (0, 255, 100), 5)
                                        sound_mgr.play("explosion")
                                        # 随机掉落物品
                                        if item_manager:
                                            item_manager.try_spawn_drop(enemy.rect.centerx, enemy.rect.centery)
                                        enemy.kill()
                            
                            # 【极光女神】处理极光减速效果
                            if hasattr(enemy, 'aurora_slow') and enemy.aurora_slow > 0:
                                enemy.aurora_slow -= 1
                                # 应用减速效果
                                slow_mult = getattr(enemy, 'aurora_slow_mult', 0.4)
                                enemy.time_slow_factor = min(enemy.time_slow_factor, slow_mult)
                                # 减速视觉效果 - 偶尔显示青色粒子
                                if random.random() < 0.1:
                                    Particle(enemy.rect.center, TEAL)
                            
                            # 【大地守护者】处理荆棘缠绕效果
                            if hasattr(enemy, 'entangle_timer') and enemy.entangle_timer > 0:
                                enemy.entangle_timer -= 1
                                # 定身效果：完全停止移动
                                enemy.time_slow_factor = 0
                                # 持续伤害（每30帧=0.5秒）
                                if enemy.entangle_timer % 30 == 0:
                                    entangle_dmg = getattr(enemy, 'entangle_damage', 8)
                                    enemy.hp -= entangle_dmg
                                    FloatingText(enemy.rect.centerx, enemy.rect.top - 10, 
                                               f"-{int(entangle_dmg)}", FOREST)
                                # 缠绕视觉 - 绿色藤蔓粒子
                                if random.random() < 0.15:
                                    Particle(enemy.rect.center, FOREST)
                        
                        # 更新僚机编队
                        if player.wingman_squadron:
                            player.wingman_squadron.update(mobs)
                        # 更新固定炮塔
                        if hasattr(player, 'turrets') and player.turrets:
                            for turret in player.turrets:
                                turret.update()
                        
                        # 【修复】更新卡牌效果处理器（生命恢复、冰霜新星等）
                        if hasattr(player, 'card_effect_processor'):
                            effect_result = player.card_effect_processor.update(1)
                            if effect_result and effect_result.get("frost_nova"):
                                freeze_duration = getattr(player, 'freeze_duration', 120)
                                freeze_radius = getattr(player, 'freeze_radius', 100)
                                # 冻结范围内所有敌人
                                for enemy in mobs:
                                    dist = math.hypot(
                                        enemy.rect.centerx - player.rect.centerx,
                                        enemy.rect.centery - player.rect.centery
                                    )
                                    if dist <= freeze_radius:
                                        enemy.frozen_timer = freeze_duration
                                        Particle(enemy.rect.center, (150, 200, 255))
                        
                        # Boss spawn logic: handled by boss_manager
                        warning_active, spawn_now = boss_manager.update(score, player.level, boss_exists=bool(boss))
                        if warning_active and not boss:
                            # Trigger visual/sound warning once
                            music_director.pause_for_stinger("warning", resume_state="combat", resume_intensity=0.85)
                            # destroy current mobs for dramatic effect
                            for m in list(mobs): create_explosion(m.rect.center, ORANGE, 6); m.kill()
                        if spawn_now and not boss:
                            # Boss挑战模式：依次生成指定的Boss
                            if boss_challenge_active and boss_challenge_current < len(boss_challenge_order):
                                boss_type = boss_challenge_order[boss_challenge_current]
                                candidate = boss_manager.spawn_boss(player.level, boss_type=boss_type)
                                boss_challenge_current += 1
                            else:
                                candidate = boss_manager.spawn_boss(player.level)
                            if candidate:
                                boss = candidate
                                all_sprites.add(boss)
                                if not boss_music_active:
                                    music_director.push_state("boss", intensity=1.0, override_track="funk")
                                    boss_music_active = True
                        
                        # ================================================================
                        # 敌人生成系统：双轨制（持续刷新 + 波次事件）
                        # ================================================================
                        if game_mode == "normal" or boss_challenge_active:
                            # --- 阶段更新 ---
                            for stage_num in sorted(STAGE_CONFIG.keys(), reverse=True):
                                if score >= STAGE_CONFIG[stage_num]["score"]:
                                    if current_stage < stage_num:
                                        current_stage = stage_num
                                        # 阶段提升提示
                                        FloatingText(WIDTH // 2, HEIGHT // 3, f"威胁等级 {stage_num}", (255, 100, 100))
                                    break
                            
                            stage_cfg = STAGE_CONFIG.get(current_stage, STAGE_CONFIG[1])
                            max_cap = stage_cfg["max_enemies"] if not boss else 4
                            allowed = max(0, max_cap - len(mobs))
                            
                            # --- 动态难度调节 ---
                            hp_ratio = player.hp / player.max_hp if player.max_hp > 0 else 1.0
                            difficulty_mult = 1.0
                            if hp_ratio < 0.3:
                                difficulty_mult = 0.6  # 低血量时放缓刷怪
                            elif no_damage_timer > 600:  # 10秒无伤
                                difficulty_mult = 1.3  # 加快刷怪
                            
                            # --- 辅助函数 ---
                            def get_spawn_position(mode: str) -> tuple:
                                """根据刷新模式返回生成位置"""
                                if mode == "top" or mode == "top_fan":
                                    return (random.randint(60, WIDTH - 60), -70)
                                elif mode == "sides":
                                    side = random.choice(["left", "right"])
                                    if side == "left":
                                        return (-70, random.randint(100, HEIGHT - 100))
                                    else:
                                        return (WIDTH + 70, random.randint(100, HEIGHT - 100))
                                elif mode == "bottom":
                                    return (random.randint(60, WIDTH - 60), HEIGHT + 70)
                                elif mode == "corners":
                                    corner = random.choice(["tl", "tr", "bl", "br"])
                                    if corner == "tl":
                                        return (-70, -70)
                                    elif corner == "tr":
                                        return (WIDTH + 70, -70)
                                    elif corner == "bl":
                                        return (-70, HEIGHT + 70)
                                    else:
                                        return (WIDTH + 70, HEIGHT + 70)
                                elif mode == "all":
                                    return get_spawn_position(random.choice(["top", "sides", "bottom"]))
                                elif mode == "top_slow":
                                    return (random.randint(100, WIDTH - 100), -70)
                                else:
                                    return (random.randint(60, WIDTH - 60), -70)
                            
                            def pick_enemy_from_tier(tier: str) -> str:
                                """从指定等级随机选择敌人，避免连续重复"""
                                tier_data = ENEMY_TIERS.get(tier, ENEMY_TIERS["T1"])
                                pool = tier_data["enemies"]
                                # 过滤掉最近出现的敌人
                                filtered = [e for e in pool if e not in recent_enemy_types[-3:]]
                                if not filtered:
                                    filtered = pool
                                return random.choice(filtered)
                            
                            def pick_weighted_spawn_mode() -> str:
                                """根据当前阶段选择刷新位置"""
                                if current_stage <= 2:
                                    return "top"
                                elif current_stage == 3:
                                    roll = random.random()
                                    if roll < 0.7:
                                        return "top"
                                    else:
                                        return "sides"
                                else:  # 阶段4-5
                                    roll = random.random()
                                    if roll < 0.5:
                                        return "top"
                                    elif roll < 0.8:
                                        return "sides"
                                    else:
                                        return "bottom"
                            
                            def pick_tier_weighted() -> str:
                                """根据当前阶段加权选择敌人等级"""
                                available = stage_cfg["tiers"]
                                if current_stage == 1:
                                    return "T1"
                                elif current_stage == 2:
                                    return random.choices(["T1", "T2"], weights=[60, 40], k=1)[0] if "T2" in available else "T1"
                                elif current_stage == 3:
                                    return random.choices(["T1", "T2", "T3"], weights=[35, 40, 25], k=1)[0]
                                elif current_stage == 4:
                                    return random.choices(["T1", "T2", "T3", "T4"], weights=[20, 35, 30, 15], k=1)[0]
                                else:  # 阶段5
                                    return random.choices(["T1", "T2", "T3", "T4"], weights=[15, 30, 30, 25], k=1)[0]
                            
                            # ================================================================
                            # 轨道1：波次事件系统（Boss Rush模式禁用）
                            # ================================================================
                            if not boss_challenge_active and not boss and not wave_event_active:
                                wave_event_timer += 1
                                wave_cooldown = int(1800 * difficulty_mult)  # 约30秒，低血量时延长
                                
                                if wave_event_timer >= wave_cooldown:
                                    # 筛选可用波次模板
                                    available_waves = [w for w in WAVE_TEMPLATES if score >= w["min_score"]]
                                    if available_waves:
                                        chosen_wave = random.choice(available_waves)
                                        wave_event_active = True
                                        wave_warning_timer = 120  # 2秒预警
                                        wave_event_timer = 0
                                        # 预警提示
                                        FloatingText(WIDTH // 2, HEIGHT // 4, chosen_wave["warning"], (255, 200, 0))
                                        sound_mgr.play("warning") if hasattr(sound_mgr, 'play') else None
                            
                            # 波次预警倒计时（Boss Rush模式跳过）
                            if not boss_challenge_active and wave_event_active and wave_warning_timer > 0:
                                wave_warning_timer -= 1
                                # 屏幕边缘闪烁效果
                                if wave_warning_timer % 20 < 10:
                                    pygame.draw.rect(screen, (255, 50, 50), (0, 0, WIDTH, 4))
                                    pygame.draw.rect(screen, (255, 50, 50), (0, HEIGHT - 4, WIDTH, 4))
                                
                                if wave_warning_timer <= 0:
                                    # 执行波次生成
                                    available_waves = [w for w in WAVE_TEMPLATES if score >= w["min_score"]]
                                    if available_waves:
                                        chosen_wave = random.choice(available_waves)
                                        spawn_mode = chosen_wave["spawn_mode"]
                                        for tier, min_count, max_count in chosen_wave["composition"]:
                                            count = random.randint(min_count, max_count)
                                            for _ in range(count):
                                                enemy_type = pick_enemy_from_tier(tier)
                                                pos = get_spawn_position(spawn_mode)
                                                enemy_factory.create_enemy(enemy_type, spawn_pos=pos)
                                                recent_enemy_types.append(enemy_type)
                                                if len(recent_enemy_types) > 10:
                                                    recent_enemy_types.pop(0)
                                    wave_event_active = False
                            
                            # ================================================================
                            # 轨道2：持续刷新层
                            # ================================================================
                            # Boss挑战模式禁止生成非Boss敌人
                            if boss_challenge_active:
                                pass  # Boss Rush模式只打Boss，不刷小怪
                            elif not wave_event_active or wave_warning_timer <= 0:
                                normal_spawn_timer += 1
                                
                                # 动态刷新间隔
                                base_interval = max(48, 90 - min(42, score // 150))
                                if len(mobs) < 4:
                                    base_interval = max(36, base_interval - 18)
                                spawn_interval = int(base_interval * difficulty_mult)
                                
                                # 调试输出（每秒一次）
                                if normal_spawn_timer % 60 == 0:
                                    print(f"[刷怪] 阶段{current_stage} | 分数{score} | 敌人{len(mobs)}/{max_cap} | 间隔{spawn_interval} | 计时{normal_spawn_timer}")
                                
                                # Boss挑战模式使用固定高威胁池
                                if boss_challenge_active:
                                    if normal_spawn_timer >= spawn_interval and allowed > 0:
                                        normal_spawn_timer = 0
                                        batch = min(allowed, 2 if len(mobs) < max_cap // 2 else 1)
                                        for _ in range(batch):
                                            enemy_type = pick_enemy_from_tier("T4")
                                            pos = get_spawn_position(pick_weighted_spawn_mode())
                                            enemy_factory.create_enemy(enemy_type, spawn_pos=pos)
                                            recent_enemy_types.append(enemy_type)
                                            if len(recent_enemy_types) > 10:
                                                recent_enemy_types.pop(0)
                                else:
                                    # 普通模式：根据阶段选择敌人
                                    if normal_spawn_timer >= spawn_interval and allowed > 0:
                                        normal_spawn_timer = 0
                                        batch = 1
                                        if len(mobs) < 4:
                                            batch = 2
                                        elif score > 2000 and random.random() < 0.3:
                                            batch = 2
                                        batch = min(batch, allowed)
                                        
                                        for _ in range(batch):
                                            tier = pick_tier_weighted()
                                            enemy_type = pick_enemy_from_tier(tier)
                                            spawn_mode = pick_weighted_spawn_mode()
                                            pos = get_spawn_position(spawn_mode)
                                            enemy_factory.create_enemy(enemy_type, spawn_pos=pos)
                                            recent_enemy_types.append(enemy_type)
                                            if len(recent_enemy_types) > 10:
                                                recent_enemy_types.pop(0)
                    
                    hits = pygame.sprite.groupcollide(mobs, bullets, False, False)
                    for m, hit_bullets in hits.items():
                        for b in hit_bullets:
                            if b.is_enemy: continue
                            if getattr(b, 'is_melee', False): continue  # 跳过近战武器，它们自己处理碰撞
                            if getattr(b, 'is_special_bullet', False): continue  # 跳过特殊子弹（如悬停爆炸弹），它们自己处理伤害
                            dmg = player.damage
                            
                            # 【霓虹突击者】超载伤害加成
                            if hasattr(player, 'plane_id') and player.plane_id == "striker":
                                if hasattr(player, 'overdrive_bonus') and player.overdrive_bonus > 0:
                                    dmg *= (1 + player.overdrive_bonus)
                            
                            # 【幽灵收割者】灵魂加成：暴击率和暴击伤害
                            crit_chance = player.crit_chance
                            crit_mult = player.crit_mult
                            if hasattr(player, 'plane_id') and player.plane_id == "specter":
                                souls = getattr(player, 'souls', 0)
                                # 每个灵魂 +2% 暴击率，+5% 暴击伤害
                                crit_chance += souls * 0.02  # 最多 +60% 暴击率
                                crit_mult += souls * 0.05    # 最多 +150% 暴击伤害
                            
                            # 【星界潜行者】暗影标记额外伤害
                            if hasattr(player, 'plane_id') and player.plane_id == "stalker":
                                # 被标记敌人受到额外伤害
                                if hasattr(m, 'shadow_mark') and m.shadow_mark > 0:
                                    mark_bonus = 1 + m.shadow_mark * 0.08  # 每层标记+8%伤害
                                    dmg *= mark_bonus
                                # 全局标记加成
                                if hasattr(player, 'shadow_mark_dmg_bonus') and player.shadow_mark_dmg_bonus > 0:
                                    dmg *= (1 + player.shadow_mark_dmg_bonus)
                            
                            # 【虚空编织者】维度织网伤害加成
                            if hasattr(player, 'plane_id') and player.plane_id == "weaver":
                                # 被网敌人受额外伤害
                                if hasattr(m, 'weaver_web_timer') and m.weaver_web_timer > 0:
                                    dmg *= 1.25  # 被网敌人+25%伤害
                                # 全局网加成
                                if hasattr(player, 'weaver_web_damage_bonus') and player.weaver_web_damage_bonus > 0:
                                    dmg *= (1 + player.weaver_web_damage_bonus)
                            
                            # 【大地守护者】大地之力伤害加成
                            if hasattr(player, 'plane_id') and player.plane_id == "gaia":
                                if hasattr(player, 'earth_dmg_bonus') and player.earth_dmg_bonus > 0:
                                    dmg *= (1 + player.earth_dmg_bonus)
                            
                            # 【钢铁泰坦】过载弹爆炸伤害
                            if hasattr(player, 'plane_id') and player.plane_id == "titan":
                                if getattr(b, 'is_titan_empowered', False):
                                    dmg *= 2.5  # 过载弹伤害x2.5
                                    # 爆炸范围伤害
                                    explosion_radius = 120
                                    explosion_dmg = dmg * 0.6
                                    for enemy in list(mobs):
                                        if enemy != m:
                                            dist = math.hypot(enemy.rect.centerx - b.rect.centerx, 
                                                            enemy.rect.centery - b.rect.centery)
                                            if dist <= explosion_radius:
                                                enemy.hp -= explosion_dmg
                                                FloatingText(enemy.rect.centerx, enemy.rect.top - 10, 
                                                           f"-{int(explosion_dmg)}", ORANGE)
                                                Particle(enemy.rect.center, (255, 150, 50))
                                    # 爆炸视觉
                                    pygame.draw.circle(screen, (255, 200, 100), b.rect.center, int(explosion_radius), 3)
                                    for _ in range(6):
                                        Particle(b.rect.center, ORANGE)
                            
                            # === 新卡牌系统：高级效果 ===
                            
                            # 1. 弱点打击 - 额外暴击判定
                            if hasattr(player, 'weakpoint_chance') and player.weakpoint_chance > 0:
                                if random.random() < player.weakpoint_chance:
                                    weakpoint_mult = getattr(player, 'weakpoint_mult', 3.0)
                                    dmg *= weakpoint_mult
                                    FloatingText(m.rect.centerx, m.rect.top - 30, "弱点!", (255, 200, 0))
                                    for _ in range(3):
                                        Particle(m.rect.center, (255, 255, 0))
                            
                            # 2. 破甲 - 无视敌人护甲
                            if hasattr(player, 'armor_penetration') and player.armor_penetration > 0:
                                # 假设敌人有armor属性，破甲减少其效果
                                if hasattr(m, 'armor') and m.armor > 0:
                                    armor_reduction = m.armor * (1 - player.armor_penetration)
                                    dmg *= (1 + (m.armor - armor_reduction) * 0.01)  # 每点破甲1%额外伤害
                                # 对装甲单位额外伤害
                                if hasattr(player, 'bonus_vs_armor') and getattr(m, 'has_armor', False):
                                    dmg *= (1 + player.bonus_vs_armor)
                            
                            # 3. 标记系统 - 标记敌人并在下次攻击暴击
                            if hasattr(player, 'has_mark') and player.has_mark:
                                if not hasattr(m, 'marked_by_player'):
                                    m.marked_by_player = True
                                    m.mark_timer = player.mark_duration
                                    FloatingText(m.rect.centerx, m.rect.top - 20, "标记!", (255, 0, 255))
                                elif m.marked_by_player and m.mark_timer > 0:
                                    # 标记目标受到暴击
                                    dmg *= player.mark_crit_mult
                                    m.marked_by_player = False
                                    FloatingText(m.rect.centerx, m.rect.top - 30, "标记暴击!", (255, 100, 255))
                            
                            # 4. 处决 - 对低血量目标巨额伤害
                            if hasattr(player, 'has_execute') and player.has_execute:
                                hp_ratio = m.hp / m.max_hp if hasattr(m, 'max_hp') and m.max_hp > 0 else 1.0
                                if hp_ratio <= player.execute_threshold:
                                    dmg *= player.execute_mult
                                    FloatingText(m.rect.centerx, m.rect.top - 40, "处决!", (200, 0, 0))
                                    for _ in range(5):
                                        Particle(m.rect.center, (255, 0, 0))
                                    # 秒杀效果
                                    if hasattr(player, 'execute_instant_kill') and player.execute_instant_kill:
                                        if hp_ratio <= 0.1:
                                            dmg = m.hp + 1000  # 确保击杀
                            
                            # 应用暴击
                            is_crit = random.random() < crit_chance
                            if is_crit:
                                dmg *= crit_mult
                                # 【统计】记录暴击
                                player.stats['crits'] += 1
                            
                            # 【统计】记录命中和伤害
                            player.stats['hits'] += 1
                            player.stats['damage_dealt'] += int(dmg)
                            
                            # 应用伤害
                            shield_timer = getattr(m, 'ally_shield_timer', 0)
                            shield_reduction = getattr(m, 'ally_shield_strength', 0.0)
                            if shield_timer > 0 and shield_reduction > 0:
                                dmg *= max(0.0, 1.0 - min(0.9, shield_reduction))
                                FloatingText(m.rect.centerx, m.rect.top - 20, "护幕", (120, 220, 255))
                            m.hp -= dmg
                            
                            # === 新卡牌系统：命中后效果 ===
                            
                            # 5. 集束炸弹 - 子弹爆炸后释放子弹药
                            if hasattr(player, 'has_cluster') and player.has_cluster:
                                cluster_count = getattr(player, 'cluster_count', 5)
                                cluster_radius = getattr(player, 'cluster_radius', 40)
                                # 生成环形子弹药
                                for i in range(cluster_count):
                                    angle = (360 / cluster_count) * i
                                    rad = math.radians(angle)
                                    cluster_x = b.rect.centerx + math.cos(rad) * 30
                                    cluster_y = b.rect.centery + math.sin(rad) * 30
                                    # 创建小型爆炸子弹
                                    cluster_bullet = Bullet(cluster_x, cluster_y, angle, False, 0, (255, 150, 0))
                                    cluster_bullet.damage = dmg * 0.3  # 子弹药伤害30%
                                    cluster_bullet.is_cluster_child = True
                                # 视觉效果
                                for _ in range(8):
                                    Particle(b.rect.center, (255, 200, 0))
                                FloatingText(b.rect.centerx, b.rect.centery, "集束!", (255, 150, 0))
                            
                            if hasattr(player, 'plane_id') and player.plane_id == "crimson":
                                if hasattr(player, 'apply_crimson_blood'):
                                    player.apply_crimson_blood(m, dmg, b.rect.center)
                            
                            # 【星界潜行者】暗影标记：命中时施加标记
                            if hasattr(player, 'plane_id') and player.plane_id == "stalker":
                                if hasattr(player, 'apply_stalker_mark'):
                                    player.apply_stalker_mark(m, dmg, b.rect.center)
                            
                            # 【大地守护者】荆棘缠绕：命中时几率缠绕敌人
                            if hasattr(player, 'plane_id') and player.plane_id == "gaia":
                                if hasattr(player, 'apply_gaia_entangle'):
                                    player.apply_gaia_entangle(m, dmg, b.rect.center)
                            
                            # 【虚空编织者】维度织网：命中时施加网缚
                            if hasattr(player, 'plane_id') and player.plane_id == "weaver":
                                if hasattr(player, 'apply_weaver_web'):
                                    player.apply_weaver_web(m, dmg, b.rect.center)
                            
                            # 【日冕耀斑】热量伤害加成
                            if hasattr(player, 'plane_id') and player.plane_id == "solar":
                                heat_ratio = getattr(player, 'solar_heat', 0) / max(1, getattr(player, 'max_solar_heat', 100))
                                dmg *= (1 + heat_ratio * 0.6)  # 最高60%伤害加成
                            
                            # 【量子裁决者】量子叠加态
                            if hasattr(player, 'plane_id') and player.plane_id == "arbiter":
                                # 积累量子能量
                                if hasattr(player, 'gain_arbiter_quantum'):
                                    player.gain_arbiter_quantum(8)
                                # 检查是否触发坑缩
                                if getattr(b, 'is_collapse_shot', False):
                                    if hasattr(player, 'trigger_quantum_collapse'):
                                        collapse_dmg = player.trigger_quantum_collapse(m, b.rect.center)
                                        dmg += collapse_dmg
                            
                            # 【日食幽灵】光暗交替效果
                            if hasattr(player, 'plane_id') and player.plane_id == "eclipse":
                                phase = getattr(player, 'eclipse_phase', 'light')
                                if phase == "light":
                                    # 光态：伤害加成
                                    light_bonus = getattr(player, 'eclipse_light_bonus', 0)
                                    dmg *= (1 + light_bonus)
                                else:
                                    # 暗态：伤害转化为护盾
                                    if hasattr(player, 'gain_eclipse_shield'):
                                        player.gain_eclipse_shield(dmg * 0.15)  # 15%伤害转护盾
                            
                            # 【棱镜分光】折射风暴
                            if hasattr(player, 'plane_id') and player.plane_id == "prism":
                                if hasattr(player, 'apply_prism_hit'):
                                    player.apply_prism_hit(m, b, b.rect.center)
                                # 折射子弹伤害加成
                                if getattr(b, 'damage_mult', 1) > 1:
                                    dmg *= getattr(b, 'damage_mult', 1)
                            
                            # 【霓虹突击者】超载引擎积累
                            if hasattr(player, 'plane_id') and player.plane_id == "striker":
                                if hasattr(player, 'gain_striker_charge'):
                                    player.gain_striker_charge(3)
                            
                            # 【雷霆战鹰】雷暴连锁
                            if hasattr(player, 'plane_id') and player.plane_id == "thunderbird":
                                if hasattr(player, 'gain_thunder_charge'):
                                    player.gain_thunder_charge(5)
                                if hasattr(player, 'trigger_chain_lightning'):
                                    lightning_paths = player.trigger_chain_lightning(b.rect.center)
                                    for start_pos, end_pos in lightning_paths:
                                        pygame.draw.line(screen, (120, 200, 255), start_pos, end_pos, 3)
                                        if random.random() < 0.5:
                                            Particle(end_pos, (120, 200, 255))
                            
                            # 【剧毒蝰蛇】剧毒累积
                            if hasattr(player, 'plane_id') and player.plane_id == "viper":
                                if hasattr(player, 'apply_viper_poison'):
                                    player.apply_viper_poison(m, dmg)
                            
                            # 【幽灵收割者】死神印记
                            if hasattr(player, 'plane_id') and player.plane_id == "specter":
                                if hasattr(player, 'update_specter_focus'):
                                    player.update_specter_focus(m)
                                if hasattr(player, 'get_specter_damage_mult'):
                                    dmg *= player.get_specter_damage_mult(m)
                            
                            # 【极光女神】极光共鸣
                            if hasattr(player, 'plane_id') and player.plane_id == "aurora":
                                if hasattr(player, 'spawn_aurora_orb'):
                                    player.spawn_aurora_orb(b.rect.center)
                            
                            # 【瘟疫使者】每10次命中生成毒云
                            if hasattr(player, 'plane_id') and player.plane_id == "goliath":
                                if player.stats['hits'] % 10 == 0:
                                    from utils.bullets.goliath_bullets import PlagueCloud
                                    style = player._get_goliath_style() if hasattr(player, '_get_goliath_style') else "goliath_default"
                                    cloud = PlagueCloud(m.rect.centerx, m.rect.centery, player.damage * 0.3, player, style, duration=180)
                                    FloatingText(m.rect.centerx, m.rect.centery - 20, "瘟疫爆发!", (57, 255, 20))
                            
                            # ===== 增强打击感（优化版） =====
                            # 1. 屏幕震动（基于伤害）- 减弱
                            shake_intensity = max(0, min(1, int(dmg / 80)))  # 减少震动强度
                            if shake_intensity > 0:
                                screen_shake_offset = apply_screen_shake(shake_intensity)
                            
                            # 2. 基础特效
                            DamageNumber(m.rect.centerx, m.rect.top, dmg, dmg > player.damage)
                            if random.random() < 0.7:  # 70%概率显示粒子
                                Particle(b.rect.center, b.color)
                            
                            # 3. 暴击特效（减少频率）
                            if dmg > player.damage and random.random() < 0.4:  # 40%概率显示暰击特效
                                for _ in range(1):  # 仅1个粒子
                                    angle = random.uniform(0, math.pi * 2)
                                    speed = random.uniform(3, 5)
                                    Particle(m.rect.center, GOLD)
                                sound_mgr.play("hit")
                            else:
                                sound_mgr.play("hit")
                            
                            # 【新】战斗充能：每次伤害敌人时充能大招
                            # 获取机体专属充能速率倍率（部分机体有加速充能）
                            ult_charge_rate = getattr(player, 'ult_charge_rate', 1.0)
                            ult_charge_gain = (dmg / 10) * ult_charge_rate  # 伤害值的10%转化为大招能量，乘以充能速率
                            player.ult_charge = min(player.max_ult_charge, player.ult_charge + ult_charge_gain)
                            # 【新】同时充能第二大招（G键）
                            player.ult2_charge = min(player.max_ult2_charge, player.ult2_charge + ult_charge_gain * 0.8)
                            # 【新】同时充能第三大招（C键）
                            player.ult3_charge = min(player.max_ult3_charge, player.ult3_charge + ult_charge_gain * 0.6)
                            # 【新】同时充能第四大招（R键）- SCARLET/ZENITH/VISCERATOR/SDMG专属
                            if hasattr(player, 'plane_id') and player.plane_id in ("scarlet", "zenith", "viscerator", "sdmg"):
                                player.ult4_charge = min(player.max_ult4_charge, player.ult4_charge + ult_charge_gain * 0.4)
                            
                            # 【优化】分裂射击：子弹击中敌人时生成分裂子弹（分裂弹不再分裂）
                            if hasattr(player, 'split_count') and player.split_count > 0:
                                # 检查是否是分裂子弹（分裂子弹不再继续分裂，防止性能问题）
                                if not getattr(b, 'is_split', False):
                                    # 添加分裂冷却，避免同一帧大量分裂
                                    split_cooldown = getattr(player, '_split_cooldown', 0)
                                    current_time = pygame.time.get_ticks()
                                    if current_time - split_cooldown >= 50:  # 50ms冷却
                                        player._split_cooldown = current_time
                                        split_damage_mult = getattr(player, 'split_damage', 0.5)
                                        # 限制最大分裂数为4，防止过多子弹
                                        actual_split_count = min(int(player.split_count), 4)
                                        for i in range(actual_split_count):
                                            angle = (360 / actual_split_count) * i  # 均匀分布角度
                                            Bullet(b.rect.centerx, b.rect.centery, angle=angle,
                                                   color=b.color, b_type=b.b_type, piercing=0, is_split=True)  # 标记为分裂子弹
                            
                            # 【新】连锁闪电：子弹击中敌人后跳跃到附近其他敌人
                            # 雷霆战鹰(thunderbird)自带连锁闪电效果，或通过卡牌获得
                            has_chain = (hasattr(player, 'has_chain_lightning') and player.has_chain_lightning) or \
                                       (hasattr(player, 'plane_id') and player.plane_id == "thunderbird")
                            if has_chain:
                                # 雷霆战鹰自带3次连锁，卡牌可以增加
                                base_chain = 3 if (hasattr(player, 'plane_id') and player.plane_id == "thunderbird") else 0
                                chain_count = base_chain + getattr(player, 'chain_count', 0)
                                chain_damage_mult = getattr(player, 'chain_damage', 0.7)  # 提高连锁伤害
                                chain_range = 250  # 增加连锁范围
                                lightning_color = (120, 200, 255) if getattr(player, 'plane_id', None) == "thunderbird" else YELLOW
                                
                                current_target = m
                                chain_damage = dmg * chain_damage_mult
                                chained_enemies = {m}  # 记录已连锁的敌人,避免重复
                                
                                for jump in range(int(chain_count)):
                                    # 查找范围内最近的未连锁敌人
                                    nearest_enemy = None
                                    min_dist = chain_range
                                    
                                    for enemy in mobs:
                                        if enemy not in chained_enemies and enemy.hp > 0:
                                            dist = math.hypot(
                                                enemy.rect.centerx - current_target.rect.centerx,
                                                enemy.rect.centery - current_target.rect.centery
                                            )
                                            if dist < min_dist:
                                                min_dist = dist
                                                nearest_enemy = enemy
                                    
                                    if nearest_enemy:
                                        # 绘制闪电连线特效
                                        pygame.draw.line(screen, lightning_color, 
                                                       current_target.rect.center, 
                                                       nearest_enemy.rect.center, 2)
                                        
                                        # 造成连锁伤害
                                        nearest_enemy.hp -= chain_damage
                                        FloatingText(nearest_enemy.rect.centerx, nearest_enemy.rect.top - 10, 
                                                   f"-{int(chain_damage)}", lightning_color)
                                        
                                        # 闪电特效（优化：减少粒子）
                                        if random.random() < 0.5:
                                            Particle(nearest_enemy.rect.center, lightning_color)
                                        
                                        chained_enemies.add(nearest_enemy)
                                        current_target = nearest_enemy
                                        chain_damage *= chain_damage_mult  # 每次跳跃衰减
                                    else:
                                        break  # 没有可跳跃的目标,结束连锁
                            
                            # 【剧毒蝰蛇】固有能力：普攻附带毒素，造成持续伤害
                            if hasattr(player, 'plane_id') and player.plane_id == "viper":
                                # 给敌人施加中毒效果（持续3秒，每0.5秒伤害一次）
                                if not hasattr(m, 'poison_timer'):
                                    m.poison_timer = 0
                                    m.poison_damage = 0
                                # 叠加/刷新毒伤害
                                poison_dmg_per_tick = max(5, dmg * 0.15)  # 每次毒伤 = 15%伤害或至少5点
                                m.poison_timer = 180  # 3秒毒持续时间 (60fps * 3)
                                m.poison_damage = poison_dmg_per_tick
                                m.poison_tick_cd = 0  # 毒伤害间隔计时
                                # 中毒视觉效果 - 绿色粒子
                                for _ in range(3):
                                    angle = random.uniform(0, math.pi * 2)
                                    dist = random.uniform(5, 15)
                                    px = m.rect.centerx + math.cos(angle) * dist
                                    py = m.rect.centery + math.sin(angle) * dist
                                    Particle((int(px), int(py)), (0, 255, 100))
                            
                            # 【优化】爆炸模块：子弹击中时产生范围爆炸伤害
                            if hasattr(player, 'has_area_dmg') and player.has_area_dmg:
                                explosion_radius = getattr(player, 'explosion_radius', 60)
                                explosion_mult = getattr(player, 'explosion_mult', 0.6)
                                explosion_damage = dmg * explosion_mult
                                
                                # 爆炸视觉效果（简化）
                                # 1. 单层爆炸圆环
                                pygame.draw.circle(screen, (255, 200, 0), b.rect.center, int(explosion_radius), 2)
                                
                                # 2. 爆炸粒子（大幅减少）
                                for _ in range(4):
                                    angle = random.uniform(0, math.pi * 2)
                                    dist = random.uniform(0, explosion_radius * 0.6)
                                    px = b.rect.centerx + math.cos(angle) * dist
                                    py = b.rect.centery + math.sin(angle) * dist
                                    Particle((int(px), int(py)), (255, 150, 0))
                                
                                # 3. 对范围内敌人造成爆炸伤害
                                explosion_hits = 0
                                for enemy in mobs:
                                    if enemy != m:  # 不重复伤害已被击中的敌人
                                        dist = math.hypot(
                                            enemy.rect.centerx - b.rect.centerx,
                                            enemy.rect.centery - b.rect.centery
                                        )
                                        if dist <= explosion_radius:
                                            enemy.hp -= explosion_damage
                                            FloatingText(enemy.rect.centerx, enemy.rect.top - 15, 
                                                       f"-{int(explosion_damage)}", (255, 150, 0))
                                            explosion_hits += 1
                                
                                if explosion_hits > 0:
                                    sound_mgr.play("hit")
                            
                            if b.piercing <= 0: b.kill()
                            else: b.piercing -= 1
                            if m.hp <= 0 and not getattr(m, '_death_rewarded', False):
                                m._death_rewarded = True  # 标记已处理，防止重复奖励
                                score += 100 if m.is_elite else 20
                                game_stats["kills"] = game_stats.get("kills", 0) + 1
                                # 【统计】记录击杀和更新连击
                                player.stats['kills'] += 1
                                player.stats['current_combo'] += 1
                                player.stats['combo_timer'] = 180  # 3秒连击窗口
                                if player.stats['current_combo'] > player.stats['max_combo']:
                                    player.stats['max_combo'] = player.stats['current_combo']
                                # 【音效增强】连击音效反馈
                                if player.stats['current_combo'] >= 10:
                                    sound_mgr.play("powerup")
                                elif player.stats['current_combo'] >= 5:
                                    sound_mgr.play("select")
                                # 击杀特效（简化版）
                                create_explosion(m.rect.center, CYAN, 5)  # 优化粒子数
                                # 仅在精英敌人死亡时显示额外粒子
                                if m.is_elite and random.random() < 0.5:
                                    for _ in range(2):
                                        angle = random.uniform(0, math.pi * 2)
                                        speed = random.uniform(4, 6)
                                        Particle(m.rect.center, LIME)
                                # 屏幕轻微震动 - 减弱
                                screen_shake_offset = apply_screen_shake(1)
                                sound_mgr.play("explosion")
                                
                                # 【死灵骑士】击杀召唤亡灵
                                if hasattr(player, 'plane_id') and player.plane_id == "necro":
                                    if hasattr(player, 'gain_necro_soul'):
                                        player.gain_necro_soul(m.rect.center)
                                
                                # 【辉耀天女】击杀彩虹碎裂特效
                                if hasattr(player, 'plane_id') and player.plane_id == "staradia":
                                    from utils.bullets.staradia_bullets import spawn_rainbow_crash
                                    style = getattr(player, 'model_style', 'default')
                                    enemy_size = max(m.rect.width, m.rect.height)
                                    spawn_rainbow_crash(m.rect.centerx, m.rect.centery, enemy_size, style)
                                
                                # 【深渊龙鱼·猪公爵】击杀深海漩涡特效
                                if hasattr(player, 'plane_id') and player.plane_id == "dukefishron":
                                    from utils.bullets.dukefishron_bullets import spawn_duke_kill_effect
                                    enemy_size = max(m.rect.width, m.rect.height) / 50.0
                                    spawn_duke_kill_effect(m.rect.centerx, m.rect.centery, enemy_size)
                                
                                # 【至尊灾厄】击杀触发墓穴亡魂
                                if hasattr(player, 'plane_id') and player.plane_id == "sepulcher":
                                    from utils.bullets.sepulcher_bullets import SepulcherSkull
                                    style = player._get_sepulcher_style() if hasattr(player, '_get_sepulcher_style') else "sepulcher_default"
                                    SepulcherSkull(m.rect.centerx, m.rect.centery, player.damage * 0.8, player, style)
                                
                                # ========== 成就系统：记录击杀 ==========
                                if player and hasattr(player, 'achievement_manager'):
                                    player.achievement_manager.add_kill(1)
                                    new_achievements = player.achievement_manager.check_achievements(player)
                                    if new_achievements:
                                        sound_mgr.play("achievement")
                                        for ach_id in new_achievements:
                                            ach = player.achievement_manager.achievements[ach_id]
                                            log_info(f"解锁成就: {ach.name}")
                                            achievement_notifications.append((ach, 180))  # 3秒显示
                                        # 立即保存成就数据，防止数据丢失
                                        try:
                                            player.achievement_manager.save_to_file()
                                        except Exception:
                                            log_error("保存成就时发生错误")
                                
                                # ========== 肉鸽系统：击杀敌人效果 ==========
                                # 根据敌人强度计算掉落经验（改进公式）
                                enemy_strength_map = {
                                    "drone": 5,
                                    "chaser": 6,
                                    "phantom": 7,
                                    "wasp": 8,
                                    "glitch": 8,
                                    "spike": 9,
                                    "sniper": 10,
                                    "tank": 12,
                                    "orbiter": 13,
                                    "sentinel": 14,
                                    "vortex": 20,
                                    "astra_fragger": 18,
                                    "ember_siege": 20,
                                    "ion_veil": 22,
                                    "resonance_breaker": 18,
                                    "cryo_lancer": 18,
                                    "arc_overseer": 19,
                                    "lumen_shade": 19,
                                }
                                base_xp = enemy_strength_map.get(m.type, 5)
                                
                                # 敌人类型加成（基于复杂度）
                                type_multiplier = {
                                    "drone": 1.0,
                                    "chaser": 1.1,
                                    "tank": 1.3,
                                    "wasp": 1.2,
                                    "sniper": 1.25,
                                    "glitch": 1.1,
                                    "sentinel": 1.35,
                                    "phantom": 1.15,
                                    "spike": 1.2,
                                    "orbiter": 1.3,
                                    "vortex": 1.5
                                }.get(m.type, 1.0)
                                
                                # 精英敌人加成 (提高到30%)
                                elite_multiplier = 3.0 if m.is_elite else 1.0
                                
                                # 难度加成 (玩家等级越高，敌人越强) - 提高到10%使升级更顺畅
                                level_multiplier = 1.0 + (player.level - 1) * 0.10
                                
                                # 最终经验计算
                                xp_amount = int(base_xp * type_multiplier * elite_multiplier * level_multiplier)
                                xp_amount = max(5, xp_amount)  # 最少5经验
                                
                                ExperienceOrb(m.rect.centerx, m.rect.centery, xp_amount)
                                FloatingText(m.rect.centerx, m.rect.top - 30, f"经验+{xp_amount}", LIME)
                                
                                # 物品掉落（普通敌人）
                                if item_manager:
                                    item_manager.try_spawn_drop(m.rect.centerx, m.rect.centery)
                                
                                # 触发击杀效果 (吸血、能量虹吸、裂变反应等)
                                corpse_effect = player.on_kill_enemy(m)
                                if corpse_effect:
                                    create_explosion(corpse_effect["pos"], ORANGE, 8)
                                
                                # 【幽灵收割者】击杀后触发隐身
                                if hasattr(player, 'plane_id') and player.plane_id == "specter":
                                    if hasattr(player, 'trigger_specter_stealth'):
                                        player.trigger_specter_stealth()
                                
                                # 【死灵骑士】击杀召唤亡灵
                                if hasattr(player, 'plane_id') and player.plane_id == "necro":
                                    if hasattr(player, 'gain_necro_soul'):
                                        player.gain_necro_soul(m.rect.center)
                                
                                if random.random() < 0.25:
                                    arsenal_save_data["currencies"]["cores"] += 1
                                    FloatingText(m.rect.centerx, m.rect.top-20, "核心+1", CYAN)
                                m.kill()
                    
                    # 【新】敌人子弹打中仆从
                    if hasattr(player, 'minions'):
                        for minion in player.minions[:]:
                            minion_rect = pygame.Rect(int(minion['x']) - 8, int(minion['y']) - 8, 16, 16)
                            for bullet in enemy_bullets:
                                if minion_rect.colliderect(bullet.rect):
                                    hit_damage = getattr(bullet, 'damage', 10)
                                    minion['hp'] -= hit_damage
                                    bullet.kill()
                                    FloatingText(int(minion['x']), int(minion['y']) - 10,
                                               f"-{int(hit_damage)}", (255, 100, 100), font_size=12)
                                    effect_payload = getattr(bullet, 'effect_data', None)
                                    if effect_payload and effect_payload.get('type') == 'chain':
                                        jumps = effect_payload.get('jumps', 0)
                                        chain_damage = effect_payload.get('minion_damage', hit_damage)
                                        for other in player.minions:
                                            if jumps <= 0:
                                                break
                                            if other is minion:
                                                continue
                                            other['hp'] -= chain_damage
                                            FloatingText(int(other['x']), int(other['y']) - 8,
                                                       f"-{int(chain_damage)}", (120, 200, 255), font_size=12)
                                            if other['hp'] <= 0:
                                                for _ in range(5):
                                                    Particle((int(other['x']), int(other['y'])), (120, 200, 255))
                                            jumps -= 1
                                    if minion['hp'] <= 0:
                                        for _ in range(5):
                                            Particle((int(minion['x']), int(minion['y'])), (255, 100, 255))
                                    break
                    
                    if not player.is_dashing:
                        hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
                        bullet_hits = []
                        pending_effects = []  # list[(effect_payload, source_sprite)]
                        max_bullet_damage = 0
                        for eb in pygame.sprite.spritecollide(player, enemy_bullets, False, pygame.sprite.collide_circle):
                            hit_cd = getattr(eb, '_hit_cd', 0)
                            if hit_cd > 0:
                                continue
                            max_bullet_damage = max(max_bullet_damage, int(getattr(eb, 'damage', 20)))
                            effect_payload = getattr(eb, 'effect_data', None)
                            if effect_payload:
                                pending_effects.append((effect_payload, eb))
                            bullet_hits.append(eb)
                            if getattr(eb, 'persistent', False):
                                eb._hit_cd = getattr(eb, 'hit_cooldown', 12)
                            else:
                                eb.kill()
                        hits.extend(bullet_hits)
                        if hits:
                            # 【晶体粉碎者】牵引光束无敌检查
                            if getattr(player, 'tractor_immune', False):
                                FloatingText(player.rect.centerx, player.rect.top, "牵引护盾!", (138, 43, 226))
                                for _ in range(3):
                                    Particle(player.rect.center, (138, 43, 226))
                                continue  # 免疫伤害
                            
                            # 【瘟疫使者·歌莉娅】瘟疫冲锋无敌帧检查
                            if hasattr(player, 'plane_id') and player.plane_id == "goliath":
                                if getattr(player, 'goliath_invincible', 0) > 0:
                                    FloatingText(player.rect.centerx, player.rect.top, "无敌!", (57, 255, 20))
                                    for _ in range(3):
                                        Particle(player.rect.center, (57, 255, 20))
                                    continue  # 免疫伤害
                            
                            # 【虚空幻影】相位无敌检查
                            if hasattr(player, 'plane_id') and player.plane_id == "phantom":
                                if getattr(player, 'phantom_intangible', False):
                                    FloatingText(player.rect.centerx, player.rect.top, "相位!", MAGENTA)
                                    for _ in range(3):
                                        Particle(player.rect.center, MAGENTA)
                                    continue  # 免疫伤害
                            
                            # 【新】相位闪避：概率完全闪避伤害
                            dodge_chance = getattr(player, 'dodge_chance', 0)
                            if dodge_chance > 0 and random.random() < dodge_chance:
                                FloatingText(player.rect.centerx, player.rect.top, "DODGE!", CYAN)
                                sound_mgr.play("powerup")
                                # 闪避特效
                                for _ in range(5):
                                    angle = random.uniform(0, math.pi * 2)
                                    Particle(player.rect.center, CYAN)
                                continue  # 完全闪避,不受伤
                            
                            dmg = max(20, max_bullet_damage)

                            for eff, source in pending_effects:
                                etype = eff.get("type")
                                if etype == "poison":
                                    player.hazard_slow_mult = min(player.hazard_slow_mult, eff.get("slow_mult", 1.0))
                                    player.hazard_slow_timer = max(player.hazard_slow_timer, eff.get("slow_duration", 0))
                                    player.poison_dot_damage = max(player.poison_dot_damage, eff.get("dot_damage", 0))
                                    player.poison_dot_timer = max(player.poison_dot_timer, eff.get("dot_duration", 0))
                                    player.poison_tick_cd = eff.get("tick_cd", 18)
                                    dmg = max(dmg, eff.get("damage", dmg))
                                elif etype in ("wall", "impact", "shield", "shrapnel"):
                                    dmg = max(dmg, eff.get("damage", dmg))
                                elif etype == "grab":
                                    player.grab_timer = max(player.grab_timer, eff.get("grab_duration", 0))
                                    player.grab_pull = eff.get("grab_pull", 2.5)
                                    anchor = eff.get("anchor")
                                    if anchor is None and source is not None and hasattr(source, "rect"):
                                        try:
                                            anchor = (int(source.rect.centerx), int(source.rect.centery))
                                        except Exception:
                                            anchor = None
                                    if anchor is None:
                                        anchor = (player.rect.centerx, player.rect.centery - 80)
                                    player.grab_anchor = anchor
                                    dmg = max(dmg, eff.get("damage", dmg))
                                elif etype == "burn":
                                    player.burn_timer = max(player.burn_timer, eff.get("dot_duration", 150))
                                    player.burn_damage = max(player.burn_damage, eff.get("dot_damage", 4))
                                    player.burn_tick_cd = eff.get("tick_cd", 15)
                                    player.hazard_slow_mult = min(player.hazard_slow_mult, eff.get("slow_mult", player.hazard_slow_mult))
                                    player.hazard_slow_timer = max(player.hazard_slow_timer, eff.get("slow_duration", 0))
                                    dmg = max(dmg, eff.get("damage", dmg))
                                elif etype == "freeze":
                                    player.freeze_timer = max(player.freeze_timer, eff.get("freeze_duration", 60))
                                    player.hazard_slow_mult = min(player.hazard_slow_mult, eff.get("slow_mult", player.hazard_slow_mult))
                                    player.hazard_slow_timer = max(player.hazard_slow_timer, eff.get("slow_duration", 0))
                                    dmg = max(dmg, eff.get("damage", dmg))
                                elif etype == "emp":
                                    player.emp_timer = max(player.emp_timer, eff.get("emp_duration", 90))
                                    drain = eff.get("drain_energy", 30)
                                    player.dash_energy = max(0, player.dash_energy - drain)
                                    if hasattr(player, "barrier_current_hp"):
                                        player.barrier_current_hp = max(0, player.barrier_current_hp - drain)
                                    dmg = max(dmg, eff.get("damage", dmg))
                                elif etype == "sonic":
                                    player.sonic_timer = max(player.sonic_timer, eff.get("silence_duration", 45))
                                    player.armor_break_timer = max(player.armor_break_timer, eff.get("armor_break", 90))
                                    player.hazard_slow_mult = min(player.hazard_slow_mult, eff.get("slow_mult", 0.8))
                                    player.hazard_slow_timer = max(player.hazard_slow_timer, eff.get("slow_duration", 0))
                                    dmg = max(dmg, eff.get("damage", dmg))
                                elif etype == "chain":
                                    jumps = eff.get("jumps", 0)
                                    minion_damage = eff.get("minion_damage", eff.get("damage", dmg))
                                    player_damage = eff.get("player_damage", eff.get("damage", dmg))
                                    if jumps > 0 and hasattr(player, "minions") and player.minions:
                                        for minion in player.minions[:]:
                                            if jumps <= 0:
                                                break
                                            minion["hp"] -= minion_damage
                                            FloatingText(int(minion["x"]), int(minion["y"]) - 8, f"-{int(minion_damage)}", (120, 200, 255), font_size=12)
                                            if minion["hp"] <= 0:
                                                for _ in range(5):
                                                    Particle((int(minion["x"]), int(minion["y"])), (120, 200, 255))
                                            jumps -= 1
                                    dmg = max(dmg, player_damage)
                                elif etype == "whiteout":
                                    player.whiteout_timer = max(player.whiteout_timer, eff.get("whiteout_duration", eff.get("duration", 150)))
                                    player.whiteout_intensity = max(player.whiteout_intensity, eff.get("whiteout_intensity", 0.6))
                                    slow_mult = eff.get("slow_mult", player.hazard_slow_mult)
                                    player.hazard_slow_mult = min(player.hazard_slow_mult, slow_mult)
                                    player.hazard_slow_timer = max(player.hazard_slow_timer, eff.get("slow_duration", 0))
                                    dmg = max(dmg, eff.get("damage", dmg))
                                elif etype == "parasite":
                                    player.parasite_timer = max(player.parasite_timer, eff.get("duration", 220))
                                    player.parasite_damage = max(player.parasite_damage, eff.get("tick_damage", eff.get("dot_damage", 4)))
                                    player.parasite_tick_cd = eff.get("tick_cd", 36)
                                    dmg = max(dmg, eff.get("damage", dmg))
                                elif etype == "mirror":
                                    duration = eff.get("duration", eff.get("mirror_duration", 180))
                                    player.mirror_timer = max(player.mirror_timer, duration)
                                    fb = eff.get("feedback_damage", eff.get("damage", 0))
                                    player.mirror_feedback_damage = max(player.mirror_feedback_damage, fb)
                                    tick_cd = max(6, eff.get("tick_cd", 18))
                                    player.mirror_tick_cd = tick_cd
                                    if player.mirror_tick_timer <= 0:
                                        player.mirror_tick_timer = tick_cd
                                    dmg = max(dmg, eff.get("damage", dmg))
                                elif etype == "phase_lock":
                                    duration = eff.get("duration", 90)
                                    player.phase_lock_timer = max(player.phase_lock_timer, duration)
                                    player.phase_lock_displacement = max(player.phase_lock_displacement, float(eff.get("displacement", 24.0)))
                                    pulse_cd = max(6, eff.get("pulse_cd", 18))
                                    player.phase_lock_pulse_cd = pulse_cd
                                    if player.phase_lock_pulse_timer <= 0 or player.phase_lock_pulse_timer > pulse_cd:
                                        player.phase_lock_pulse_timer = max(4, pulse_cd // 2)
                                    anchor = eff.get("anchor")
                                    if not anchor and source is not None and hasattr(source, "rect"):
                                        anchor = (int(source.rect.centerx), int(source.rect.centery))
                                    if anchor:
                                        try:
                                            origin = (int(anchor[0]), int(anchor[1]))
                                        except Exception:
                                            origin = (player.rect.centerx, player.rect.centery)
                                        player.phase_lock_anchor = origin
                                    player.phase_lock_invert = bool(eff.get("invert", False))
                                    dmg = max(dmg, eff.get("damage", dmg))
                                elif etype == "spore_root":
                                    duration = eff.get("duration", 0)
                                    player.spore_root_timer = max(player.spore_root_timer, duration)
                                    player.spore_root_damage = max(player.spore_root_damage, eff.get("tick_damage", eff.get("dot_damage", 0)))
                                    player.spore_root_tick_cd = max(8, eff.get("tick_cd", 24))
                                    if player.spore_root_tick_timer <= 0:
                                        player.spore_root_tick_timer = player.spore_root_tick_cd
                                    slow = eff.get("slow_mult")
                                    if slow is not None:
                                        player.spore_root_slow_mult = min(player.spore_root_slow_mult, float(slow))
                                    dmg = max(dmg, eff.get("damage", dmg))
                                elif etype == "solar_burn":
                                    duration = eff.get("duration", eff.get("burn_duration", 0))
                                    player.solar_burn_timer = max(player.solar_burn_timer, duration)
                                    player.solar_burn_damage = max(player.solar_burn_damage, eff.get("tick_damage", eff.get("damage", 0)))
                                    player.solar_burn_tick_cd = max(4, eff.get("tick_cd", 12))
                                    if player.solar_burn_tick_timer <= 0:
                                        player.solar_burn_tick_timer = player.solar_burn_tick_cd
                                    dmg = max(dmg, eff.get("damage", dmg))
                            # ===== 增强受伤打击感 =====
                            # 屏幕震动反馈 - 减弱
                            screen_shake_offset = apply_screen_shake(3)
                            
                            if getattr(player, 'armor_break_timer', 0) > 0:
                                dmg = int(dmg * 1.25)

                            # 【大地守护者】护甲减伤 + 积蓄怒气
                            if hasattr(player, 'plane_id') and player.plane_id == "gaia":
                                armor_reduction = getattr(player, 'earth_armor_bonus', 0)
                                dmg = int(dmg * (1 - armor_reduction))
                                if hasattr(player, 'gain_earth_fury'):
                                    player.gain_earth_fury(25)  # 受伤积蓄怒气（增强）
                            
                            # 【钢铁泰坦】装甲减伤 + 积蓄装甲层数
                            if hasattr(player, 'plane_id') and player.plane_id == "titan":
                                armor_stacks = getattr(player, 'titan_armor_stacks', 0)
                                armor_reduction = armor_stacks * 0.08  # 每层减伤8%，最高40%
                                dmg = int(dmg * (1 - armor_reduction))
                                if hasattr(player, 'gain_titan_armor'):
                                    player.gain_titan_armor()
                            
                            # 【幽灵收割者】隐身减伤
                            if hasattr(player, 'plane_id') and player.plane_id == "specter":
                                if getattr(player, 'specter_stealth', 0) > 0:
                                    dmg = int(dmg * 0.25)  # 隐身时减伤75%
                                    FloatingText(player.rect.centerx, player.rect.top - 15, "隐匿!", (150, 100, 255))
                            
                            # 【日食幽灵】暗影护盾优先抵消伤害
                            if hasattr(player, 'plane_id') and player.plane_id == "eclipse":
                                eclipse_shield = getattr(player, 'eclipse_shield', 0)
                                if eclipse_shield > 0:
                                    absorbed = min(eclipse_shield, dmg)
                                    player.eclipse_shield -= absorbed
                                    dmg -= absorbed
                                    if absorbed > 0:
                                        FloatingText(player.rect.centerx, player.rect.top - 15, 
                                                   f"护盾-{int(absorbed)}", (100, 50, 180))
                                        Particle(player.rect.center, (100, 50, 180))
                            
                            # 【新】先扣除能量护盾
                            if hasattr(player, 'barrier_current_hp') and player.barrier_current_hp > 0:
                                barrier_absorbed = min(player.barrier_current_hp, dmg)
                                player.barrier_current_hp -= barrier_absorbed
                                dmg -= barrier_absorbed
                                FloatingText(player.rect.centerx, player.rect.top - 20,
                                           f"护盾-{int(barrier_absorbed)}", (0, 200, 255))
                                Particle(player.rect.center, (0, 200, 255))
                                # 重置充能计时器
                                if hasattr(player, 'barrier_recharge_timer'):
                                    player.barrier_recharge_timer = 0
                            
                            if dmg > 0 and player.shield > 0:
                                player.shield -= dmg
                                if player.shield < 0: player.shield = 0
                                # 盾牌吸收时的蓝色特效（简化）
                                if random.random() < 0.3:  # 30%概率显示
                                    for _ in range(2):
                                        angle = random.uniform(0, math.pi * 2)
                                        speed = random.uniform(2, 3)
                                        Particle(player.rect.center, CYAN)
                            elif dmg > 0:
                                player.hp -= dmg
                                no_damage_timer = 0  # 重置无伤计时
                                FloatingText(player.rect.centerx, player.rect.top, f"-{dmg}", RED)
                                # 受伤时的特效（简化）
                                if random.random() < 0.5:  # 50%概率显示
                                    for _ in range(2):
                                        angle = random.uniform(0, math.pi * 2)
                                        speed = random.uniform(2, 4)
                                        Particle(player.rect.center, RED)
                                sound_mgr.play("hit")
                                if player.hp <= 0:
                                    # 检查复活机制
                                    if hasattr(player, 'revive_hp') and player.revive_hp > 0:
                                        # 初始化复活冷却计时器
                                        if not hasattr(player, 'revive_cooldown_timer'):
                                            player.revive_cooldown_timer = 0
                                        
                                        # 获取复活冷却时间（单位：帧，默认3600帧=60秒）
                                        revive_cooldown = getattr(player, 'revive_cooldown', 3600)
                                        
                                        # 检查冷却是否完成
                                        if player.revive_cooldown_timer >= revive_cooldown:
                                            # 执行复活
                                            player.hp = player.revive_hp
                                            player.revive_cooldown_timer = 0  # 重置冷却
                                            
                                            # 复活无敌时间（180帧=3秒）
                                            if not hasattr(player, 'invincible_timer'):
                                                player.invincible_timer = 0
                                            player.invincible_timer = 180
                                            
                                            # 复活特效
                                            FloatingText(player.rect.centerx, player.rect.top - 30, "复活!", (255, 215, 0), font_size=32)
                                            # 金色光环粒子
                                            for i in range(50):
                                                angle = random.uniform(0, math.pi * 2)
                                                distance = random.uniform(20, 80)
                                                px = player.rect.centerx + math.cos(angle) * distance
                                                py = player.rect.centery + math.sin(angle) * distance
                                                Particle((int(px), int(py)), (255, 215, 0))
                                            
                                            # 清除周围敌人
                                            for m in mobs:
                                                dist = math.hypot(m.rect.centerx - player.rect.centerx, 
                                                                m.rect.centery - player.rect.centery)
                                                if dist < 200:
                                                    m.hp = 0
                                                    for _ in range(5):
                                                        Particle(m.rect.center, (255, 100, 100))
                                            
                                            sound_mgr.play("powerup")
                                        else:
                                            # 冷却未完成，正常死亡
                                            game_state = "gameover"
                                            final_score = score
                                            game_over_timer = 0
                                            player_name = ""
                                            # Capture final frozen screen to show for 2s animation
                                            try:
                                                frozen_screen = screen.copy()
                                            except Exception:
                                                frozen_screen = None
                                            # 保存成就
                                            if player and hasattr(player, 'achievement_manager'):
                                                player.achievement_manager.save_to_file()
                                            # Boss挑战模式失败时重置标志
                                            boss_challenge_active = False
                                            music_director.pause_for_stinger(
                                                "stinger_defeat",
                                                resume_state="defeat",
                                                resume_intensity=0.25,
                                                silence_ms=1400,
                                            )
                                            deactivate_boss_challenge_music()
                                            sound_mgr.play("gameover")
                                    else:
                                        # 无复活能力，正常死亡
                                        game_state = "gameover"
                                        final_score = score
                                        game_over_timer = 0
                                        player_name = ""
                                        # Capture final frozen screen to show for 2s animation
                                        try:
                                            frozen_screen = screen.copy()
                                        except Exception:
                                            frozen_screen = None
                                        # 保存成就
                                        if player and hasattr(player, 'achievement_manager'):
                                            player.achievement_manager.save_to_file()
                                        # Boss挑战模式失败时重置标志
                                        boss_challenge_active = False
                                        music_director.pause_for_stinger(
                                            "stinger_defeat",
                                            resume_state="defeat",
                                            resume_intensity=0.25,
                                            silence_ms=1400,
                                        )
                                        deactivate_boss_challenge_music()
                                        sound_mgr.play("gameover")
                    
                    # ========== 经验球拾取 ==========
                    xp_orbs = [s for s in all_sprites if isinstance(s, ExperienceOrb)]
                    for orb in xp_orbs:
                        # 检查是否碰到玩家或在吸取范围内
                        dist_to_player = math.hypot(orb.rect.centerx - player.rect.centerx, 
                                                    orb.rect.centery - player.rect.centery)
                        
                        # 使用玩家的拾取范围而不是固定值
                        player_pickup_range = getattr(player, 'pickup_range', 150)
                        
                        if dist_to_player < 40 or dist_to_player < player_pickup_range or pygame.sprite.spritecollide(player, pygame.sprite.Group(orb), False):
                            # 触发吸取动画而不是直接消失
                            if not orb.being_absorbed:
                                orb.being_absorbed = True
                                orb.absorption_frames = 0
                                orb.target_x = player.rect.centerx
                                orb.target_y = player.rect.centery
                                
                                # 玩家获得经验
                                prev_level = player.level
                                new_level = player.add_xp(orb.amount)
                                FloatingText(orb.rect.centerx, orb.rect.centery, f"经验 {orb.amount}", YELLOW)
                                sound_mgr.play("select")
                                
                                # 检查是否升级（仅在实际升一级时弹卡）
                                if new_level > prev_level and player.upgrade_manager:
                                    # 确保upgrade_choice已生成
                                    if not player.upgrade_manager.upgrade_choice:
                                        player.upgrade_manager.trigger_levelup()
                                    
                                    if player.upgrade_manager.level_up_ready and player.upgrade_manager.upgrade_choice:
                                        levelup_ready = True
                                        # 提取卡牌ID作为upgrade_options
                                        upgrade_options = [choice["id"] for choice in player.upgrade_manager.upgrade_choice]
                                        upgrade_selected = 0
                                        sound_mgr.play("levelup")
                                        # Pause the game and show frozen screen during level up
                                        # Don't trigger the generic pause menu; instead pause only entities
                                        is_paused = False
                                        levelup_paused = True
                                        if frozen_screen is None:
                                            frozen_screen = screen.copy()
                    
                    if boss:
                        bhits = pygame.sprite.spritecollide(boss, bullets, False)
                        for b in bhits:
                            if b.is_enemy: continue
                            damage = player.damage * 0.5
                            boss.hp -= damage
                            boss._hit_flash_timer = 10  # 设置闪白效果
                            
                            # 【新增】打Boss也充能大招
                            ult_charge_rate = getattr(player, 'ult_charge_rate', 1.0)
                            ult_charge_gain = (damage / 8) * ult_charge_rate  # Boss充能略多一点
                            player.ult_charge = min(player.max_ult_charge, player.ult_charge + ult_charge_gain)
                            player.ult2_charge = min(player.max_ult2_charge, player.ult2_charge + ult_charge_gain * 0.8)
                            player.ult3_charge = min(player.max_ult3_charge, player.ult3_charge + ult_charge_gain * 0.6)
                            if hasattr(player, 'plane_id') and player.plane_id in ("scarlet", "zenith", "viscerator", "sdmg"):
                                player.ult4_charge = min(player.max_ult4_charge, player.ult4_charge + ult_charge_gain * 0.4)
                            
                            # 【新增】机体特效触发（对Boss生效）
                            # 【霓虹突击者】过载充能
                            if hasattr(player, 'plane_id') and player.plane_id == "striker":
                                if hasattr(player, 'gain_striker_charge'):
                                    player.gain_striker_charge(3)
                            
                            # 【雷霆战鹰】雷暴充能
                            if hasattr(player, 'plane_id') and player.plane_id == "thunderbird":
                                if hasattr(player, 'gain_thunder_charge'):
                                    player.gain_thunder_charge(5)
                            
                            # 【剧毒蝰蛇】毒素叠加
                            if hasattr(player, 'plane_id') and player.plane_id == "viper":
                                if hasattr(player, 'apply_viper_poison'):
                                    player.apply_viper_poison(boss, damage)
                            
                            # 【幽灵收割者】死神印记（对Boss也生效）
                            if hasattr(player, 'plane_id') and player.plane_id == "specter":
                                if hasattr(player, 'update_specter_focus'):
                                    player.update_specter_focus(boss)
                            
                            # 【极光女神】极光共鸣
                            if hasattr(player, 'plane_id') and player.plane_id == "aurora":
                                if hasattr(player, 'spawn_aurora_orb'):
                                    player.spawn_aurora_orb(b.rect.center)
                            
                            # 【绯红恶魔】鲜血层数累积
                            if hasattr(player, 'plane_id') and player.plane_id == "scarlet":
                                if hasattr(player, 'gain_blood_stack'):
                                    player.gain_blood_stack(1)
                            
                            # 【吸血效果】打Boss也能吸血
                            lifesteal = getattr(player, 'lifesteal', 0)
                            if lifesteal > 0:
                                heal_amount = damage * lifesteal
                                player.hp = min(player.max_hp, player.hp + heal_amount)
                                if heal_amount > 1 and random.random() < 0.3:
                                    FloatingText(player.rect.centerx, player.rect.top - 20, f"+{int(heal_amount)}", LIME)
                            
                            # 【统计更新】记录命中
                            player.stats['hits'] += 1
                            player.stats['damage_dealt'] += damage
                            
                            # 【连锁闪电】打Boss也能触发连锁到附近小怪
                            has_chain = (hasattr(player, 'has_chain_lightning') and player.has_chain_lightning) or \
                                       (hasattr(player, 'plane_id') and player.plane_id == "thunderbird")
                            if has_chain and len(mobs) > 0:
                                base_chain = 3 if (hasattr(player, 'plane_id') and player.plane_id == "thunderbird") else 0
                                chain_count = base_chain + getattr(player, 'chain_count', 0)
                                chain_damage_mult = getattr(player, 'chain_damage', 0.7)
                                chain_range = 300  # Boss连锁范围更大
                                lightning_color = (120, 200, 255) if getattr(player, 'plane_id', None) == "thunderbird" else YELLOW
                                
                                current_pos = boss.rect.center
                                chain_damage = damage * chain_damage_mult
                                chained_enemies = set()
                                
                                for jump in range(int(chain_count)):
                                    nearest_enemy = None
                                    min_dist = chain_range
                                    for enemy in mobs:
                                        if enemy not in chained_enemies and enemy.hp > 0:
                                            dist = math.hypot(enemy.rect.centerx - current_pos[0], enemy.rect.centery - current_pos[1])
                                            if dist < min_dist:
                                                min_dist = dist
                                                nearest_enemy = enemy
                                    if nearest_enemy:
                                        pygame.draw.line(screen, lightning_color, current_pos, nearest_enemy.rect.center, 2)
                                        nearest_enemy.hp -= chain_damage
                                        FloatingText(nearest_enemy.rect.centerx, nearest_enemy.rect.top - 10, f"-{int(chain_damage)}", lightning_color)
                                        if random.random() < 0.5:
                                            Particle(nearest_enemy.rect.center, lightning_color)
                                        chained_enemies.add(nearest_enemy)
                                        current_pos = nearest_enemy.rect.center
                                        chain_damage *= chain_damage_mult
                                    else:
                                        break
                            
                            # 【爆炸伤害】打Boss也能触发范围爆炸伤害周围小怪
                            if hasattr(player, 'has_area_dmg') and player.has_area_dmg and len(mobs) > 0:
                                explosion_radius = getattr(player, 'explosion_radius', 80)
                                explosion_mult = getattr(player, 'explosion_mult', 0.5)
                                explosion_damage = damage * explosion_mult
                                
                                pygame.draw.circle(screen, (255, 200, 0), b.rect.center, int(explosion_radius), 2)
                                for _ in range(3):
                                    angle = random.uniform(0, math.pi * 2)
                                    dist = random.uniform(0, explosion_radius * 0.5)
                                    px = b.rect.centerx + math.cos(angle) * dist
                                    py = b.rect.centery + math.sin(angle) * dist
                                    Particle((int(px), int(py)), (255, 150, 0))
                                
                                for enemy in mobs:
                                    dist = math.hypot(enemy.rect.centerx - b.rect.centerx, enemy.rect.centery - b.rect.centery)
                                    if dist <= explosion_radius:
                                        enemy.hp -= explosion_damage
                                        FloatingText(enemy.rect.centerx, enemy.rect.top - 15, f"-{int(explosion_damage)}", (255, 150, 0))
                            
                            # 【伤害数字显示】
                            DamageNumber(boss.rect.centerx, boss.rect.top, damage, False)
                            
                            # ===== 增强Boss打击感（优化版） =====
                            # 屏幕轻微震动 - 减弱
                            screen_shake_offset = apply_screen_shake(2)
                            
                            # 击中特效（减少和概率）
                            if random.random() < 0.3:
                                for _ in range(2):
                                    angle = random.uniform(0, math.pi * 2)
                                    speed = random.uniform(3, 5)
                                    Particle(boss.rect.center, (255, 150, 0))
                            
                            # 音效反馈
                            sound_mgr.play("hit")
                            
                            if b.piercing <= 0: b.kill()
                            if boss.hp <= 0:
                                # 先保存Boss位置，再kill
                                boss_death_x = boss.rect.centerx
                                boss_death_y = boss.rect.centery
                                boss_death_top = boss.rect.top
                                boss_death_center = boss.rect.center
                                boss.kill()
                                boss = None
                                score += 10000
                                
                                # ===== Boss击杀特效（大幅简化） =====
                                # 屏幕震动 - 减弱
                                screen_shake_offset = apply_screen_shake(4)
                                
                                # 单次爆炸
                                create_explosion(boss_death_center, (255, 120, 0), 10)
                                
                                # 少量粒子
                                if random.random() < 0.8:
                                    for _ in range(4):
                                        angle = random.uniform(0, math.pi * 2)
                                        speed = random.uniform(4, 7)
                                        Particle(boss_death_center, GOLD)
                                
                                # 音效
                                sound_mgr.play("nuke")
                                deactivate_boss_music()
                                try:
                                    activate_background_music(bg_manager.current_style)
                                except: pass
                                
                                FloatingText(WIDTH//2, HEIGHT//2, "BOSS DEFEATED", GOLD)
                                
                                # ========== Boss击杀奖励：物品掉落 ==========
                                if item_manager:
                                    item_manager.spawn_boss_drops(boss_death_x, boss_death_y)
                                
                                # ========== Boss击杀奖励：大量经验 ==========
                                boss_xp_reward = 200 + player.level * 50  # 基础200 + 等级*50
                                for i in range(8):  # 掉落8个大经验球
                                    offset_x = random.randint(-80, 80)
                                    offset_y = random.randint(-60, 60)
                                    ExperienceOrb(boss_death_x + offset_x, boss_death_y + offset_y, boss_xp_reward // 8)
                                FloatingText(boss_death_x, boss_death_top - 50, f"经验+{boss_xp_reward}", GOLD)
                                
                                # ========== Boss击杀奖励：触发卡牌选择 ==========
                                if player.upgrade_manager:
                                    player.upgrade_manager.trigger_levelup()  # 强制触发卡牌选择
                                    if player.upgrade_manager.upgrade_choice:
                                        levelup_ready = True
                                        upgrade_options = [choice["id"] for choice in player.upgrade_manager.upgrade_choice]
                                        upgrade_selected = 0
                                        levelup_paused = True
                                        if frozen_screen is None:
                                            frozen_screen = screen.copy()
                                        FloatingText(WIDTH//2, HEIGHT//2 - 50, "Boss奖励卡牌!", CYAN)
                                
                                # ========== 成就系统：Boss击杀 ==========
                                if player and hasattr(player, 'achievement_manager'):
                                    player.achievement_manager.stats["bosses_killed"] += 1
                                    new_achievements = player.achievement_manager.check_achievements(player)
                                    if new_achievements:
                                        sound_mgr.play("achievement")
                                        for ach_id in new_achievements:
                                            ach = player.achievement_manager.achievements[ach_id]
                                            log_info(f"解锁成就: {ach.name}")
                                            achievement_notifications.append((ach, 180))  # 3秒显示
                                        try:
                                            player.achievement_manager.save_to_file()
                                        except Exception:
                                            log_error("保存成就时发生错误")
                                
                                # ========== 排行榜统计：Boss击杀 ==========
                                game_stats["boss_kills"] += 1
                                
                                # Boss挑战模式逻辑：检查是否所有Boss都通关
                                if boss_challenge_active:
                                    if boss_challenge_current >= len(boss_challenge_order):
                                        # 挑战全部完成，获得特殊成就奖励
                                        log_info("恭喜！完成所有Boss挑战！")
                                        # 触发Boss挑战完成成就
                                        if hasattr(player, 'achievement_manager'):
                                            if player.achievement_manager.achievements["boss_challenger"].unlock():
                                                achievement_notifications.append((player.achievement_manager.achievements["boss_challenger"], 180))
                                                sound_mgr.play("achievement")
                                            # 统计击杀的Boss类型
                                            unique_bosses = set(boss_challenge_order)
                                            total_bosses = set(BOSS_DB.keys())
                                            if unique_bosses == total_bosses and player.achievement_manager.achievements["boss_all_clear"].unlock():
                                                achievement_notifications.append((player.achievement_manager.achievements["boss_all_clear"], 180))
                                                sound_mgr.play("achievement")
                                            player.achievement_manager.save_to_file()
                                        boss_challenge_active = False
                                        deactivate_boss_challenge_music()
                                        # 继续无限模式或返回菜单
                
                # ========== 先绘制尾迹（在飞机下层）==========
                if player is not None:
                    safe_call_draw(player.draw_trail, screen)
                
                safe_call_draw(all_sprites.draw, screen)
                
                # 绘制物品掉落
                if item_manager:
                    item_manager.draw(screen)
                
                if player is not None:
                    safe_call_draw(player.draw_auras, screen)
                    # 绘制僚机编队和轨道
                    if player.wingman_squadron:
                        # 绘制僚机转动轨道
                        if player.wingman_squadron.wingmen:
                            pygame.draw.circle(screen, (50, 150, 150), player.rect.center, 100, 1)
                        # 绘制僚机
                        safe_call_draw(player.wingman_squadron.draw, screen)
                    
                    # 【死灵骑士】绘制亡灵
                    if hasattr(player, 'necro_ghosts') and player.necro_ghosts:
                        for ghost in player.necro_ghosts:
                            gx, gy = int(ghost['x']), int(ghost['y'])
                            # 亡灵本体 - 半透明紫红色圆形
                            ghost_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
                            alpha = 150 + int(50 * math.sin(pygame.time.get_ticks() / 200))
                            pygame.draw.circle(ghost_surf, (180, 60, 120, alpha), (12, 12), 10)
                            pygame.draw.circle(ghost_surf, (255, 100, 180, alpha), (12, 12), 6)
                            # 眼睛
                            pygame.draw.circle(ghost_surf, (255, 255, 255, alpha), (9, 10), 2)
                            pygame.draw.circle(ghost_surf, (255, 255, 255, alpha), (15, 10), 2)
                            screen.blit(ghost_surf, (gx - 12, gy - 12))
                            # 生命条
                            lifetime_pct = ghost['lifetime'] / 600
                            bar_w = 20
                            pygame.draw.rect(screen, (60, 30, 50), (gx - 10, gy - 18, bar_w, 3))
                            pygame.draw.rect(screen, (200, 80, 150), (gx - 10, gy - 18, int(bar_w * lifetime_pct), 3))
                    
                    # 绘制固定位置防御炮塔
                    if hasattr(player, 'turrets') and player.turrets:
                        for turret in player.turrets:
                            turret.draw(screen)

                    # 新危害视觉反馈覆盖
                    if getattr(player, 'whiteout_intensity', 0) > 0:
                        intensity = min(1.0, player.whiteout_intensity)
                        whiteout_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                        whiteout_layer.fill((255, 255, 255, int(140 * intensity)))
                        screen.blit(whiteout_layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                        scan = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                        offset = int((pygame.time.get_ticks() * 0.15) % HEIGHT)
                        pygame.draw.rect(scan, (255, 255, 255, int(90 * intensity)), (0, offset, WIDTH, 10))
                        screen.blit(scan, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                    if getattr(player, 'parasite_timer', 0) > 0 and getattr(player, 'parasite_damage', 0) > 0:
                        haze = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                        strength = min(1.0, 0.4 + player.parasite_damage / 8.0)
                        haze.fill((40, 70, 50, int(100 * strength)))
                        screen.blit(haze, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        swarm = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                        tick = pygame.time.get_ticks() / 400
                        for idx in range(6):
                            ang = tick + idx * 1.05
                            radius = 160 + idx * 18
                            px = player.rect.centerx + math.cos(ang) * radius
                            py = player.rect.centery + math.sin(ang) * radius * 0.6
                            pygame.draw.circle(swarm, (140, 220, 140, 120), (int(px), int(py)), 8)
                        screen.blit(swarm, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                else:
                    log_debug("Main loop: player is None; skipping player draws")
                
                # ========== Boss视觉冲击力增强（每个Boss独特效果）==========
                if boss:
                    game_tick = pygame.time.get_ticks()
                    boss_hp_ratio = boss.hp / boss.max_hp
                    
                    # ========== 全局Boss威压效果 ==========
                    # 1. 暗角压迫效果 - 屏幕边缘变暗
                    vignette_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    vignette_intensity = int(60 + 40 * (1 - boss_hp_ratio))  # 血越少越暗
                    for edge in range(60):
                        edge_alpha = int(vignette_intensity * (1 - edge / 60))
                        pygame.draw.rect(vignette_surf, (0, 0, 0, edge_alpha), (edge, edge, WIDTH - edge * 2, HEIGHT - edge * 2), 1)
                    screen.blit(vignette_surf, (0, 0))
                    
                    # 2. Boss威压光环 - 巨大脉冲光圈
                    boss_color = boss.data.get('color', (255, 100, 100))
                    aura_pulse = int(30 * math.sin(game_tick / 200))
                    aura_base_r = 180 + aura_pulse
                    # 外层模糊光晕
                    for glow_layer in range(5):
                        glow_r = aura_base_r + glow_layer * 15
                        glow_alpha = int(40 - glow_layer * 7)
                        glow_surf = pygame.Surface((glow_r * 2 + 20, glow_r * 2 + 20), pygame.SRCALPHA)
                        pygame.draw.circle(glow_surf, (*boss_color[:3], glow_alpha), (glow_r + 10, glow_r + 10), glow_r)
                        screen.blit(glow_surf, (boss.rect.centerx - glow_r - 10, boss.rect.centery - glow_r - 10))
                    
                    # 3. 威压涟漪 - 从Boss向外扩散的冲击波
                    ripple_cycle = (game_tick % 2000) / 2000  # 2秒一个周期
                    ripple_r = int(50 + ripple_cycle * 250)
                    ripple_alpha = int(120 * (1 - ripple_cycle))
                    if ripple_alpha > 10:
                        pygame.draw.circle(screen, (*boss_color[:3], ripple_alpha), boss.rect.center, ripple_r, 3)
                    
                    # 4. 空间扭曲线条 - 放射状能量线
                    for ray in range(12):
                        ray_angle = math.radians(ray * 30 + game_tick / 50)
                        ray_length = 200 + int(50 * math.sin(game_tick / 100 + ray))
                        ray_end_x = int(boss.rect.centerx + ray_length * math.cos(ray_angle))
                        ray_end_y = int(boss.rect.centery + ray_length * math.sin(ray_angle))
                        ray_alpha = int(60 + 40 * math.sin(game_tick / 80 + ray))
                        pygame.draw.line(screen, (*boss_color[:3],), boss.rect.center, (ray_end_x, ray_end_y), 1)
                    
                    # ===== 虚空母舰 =====
                    if boss.type == "carrier":
                        # 红色能量脉冲光晕
                        glow_radius = 100 + int(50 * math.sin(game_tick / 80))
                        pygame.draw.circle(screen, (255, 80, 80), boss.rect.center, glow_radius, 4)
                        pygame.draw.circle(screen, (200, 30, 30), boss.rect.center, glow_radius - 20, 2)
                        # 旋转的能量环
                        for ring in range(3):
                            ring_angle = (game_tick / 100 + ring * 120) / 180 * math.pi
                            ring_radius = 80 + ring * 20
                            for i in range(8):
                                angle = ring_angle + i * math.pi / 4
                                x = int(boss.rect.centerx + ring_radius * math.cos(angle))
                                y = int(boss.rect.centery + ring_radius * math.sin(angle))
                                pygame.draw.circle(screen, (255, 100, 100), (x, y), 3)
                    
                    # ===== 钢铁堡垒 =====
                    elif boss.type == "fortress":
                        # 橙色方形脉冲
                        pulse_size = 150 + int(40 * math.sin(game_tick / 60))
                        pygame.draw.rect(screen, (255, 140, 0), pygame.Rect(boss.rect.centerx - pulse_size//2, 
                                                                            boss.rect.centery - pulse_size//2, 
                                                                            pulse_size, pulse_size), 3)
                        # 旋转的炮台指示线
                        for cannon in range(4):
                            angle = (game_tick / 150 + cannon * 90) / 180 * math.pi
                            ex = boss.rect.centerx + int(150 * math.cos(angle))
                            ey = boss.rect.centery + int(150 * math.sin(angle))
                            pygame.draw.line(screen, (255, 160, 50), boss.rect.center, (ex, ey), 3)
                    
                    # ===== 虚空刺客 =====
                    elif boss.type == "assassin":
                        # 紫色闪现效果
                        flash = int(100 * abs(math.sin(game_tick / 40)))
                        pygame.draw.circle(screen, (150 + flash//2, 0, 150 + flash//2), boss.rect.center, 120, 2)
                        # 随机闪现虚影
                        for i in range(3):
                            offset_x = int(60 * math.sin(game_tick / 100 + i * 120))
                            offset_y = int(60 * math.cos(game_tick / 100 + i * 120))
                            shadow_alpha = int(100 * (1 - i / 3))
                            s = pygame.Surface((60, 60), pygame.SRCALPHA)
                            pygame.draw.rect(s, (150, 0, 180, shadow_alpha), s.get_rect())
                            safe_blit(screen, s, (boss.rect.x + offset_x - 30, boss.rect.y + offset_y - 30))
                    
                    # ===== 炽天使 =====
                    elif boss.type == "seraphim":
                        # 金色圣光射线
                        light_count = 12
                        for i in range(light_count):
                            angle = (i / light_count) * math.pi * 2 + game_tick / 200
                            radius = 130
                            brightness = int(200 + 55 * math.sin(game_tick / 100 + i))
                            ex = boss.rect.centerx + int(radius * math.cos(angle))
                            ey = boss.rect.centery + int(radius * math.sin(angle))
                            pygame.draw.line(screen, (brightness, brightness - 50, 50), boss.rect.center, (ex, ey), 2)
                    
                    # ===== 深渊巨兽 =====
                    elif boss.type == "leviathan":
                        # 紫色深渊波纹
                        for wave in range(4):
                            wave_radius = 80 + (game_tick * 2 + wave * 30) % 150
                            wave_alpha = int(180 * (1 - (wave_radius - 80) / 150))
                            pygame.draw.circle(screen, (120, 30, 180), boss.rect.center, wave_radius, 2)
                        # 触手阴影
                        for tentacle in range(3):
                            angle = (game_tick / 200 + tentacle * 120) / 180 * math.pi
                            ex = boss.rect.centerx + int(200 * math.cos(angle))
                            ey = boss.rect.centery + int(200 * math.sin(angle))
                            pygame.draw.line(screen, (100, 30, 150), boss.rect.center, (ex, ey), 4)
                    
                    # ===== 蜂群主宰 =====
                    elif boss.type == "overlord":
                        # 青色蜂群轨迹
                        for hive_ring in range(3):
                            ring_radius = 80 + hive_ring * 40
                            bee_count = 6 + hive_ring * 2
                            for bee in range(bee_count):
                                angle = (game_tick / (150 - hive_ring * 20) + bee * 2 * math.pi / bee_count)
                                bx = int(boss.rect.centerx + ring_radius * math.cos(angle))
                                by = int(boss.rect.centery + ring_radius * math.sin(angle))
                                pygame.draw.circle(screen, (0, 200, 200), (bx, by), 2 + hive_ring)
                    
                    # ===== 终焉机神 =====
                    elif boss.type == "ragnarok":
                        # 血红色闪电爆炸
                        lightning_count = 10
                        for i in range(lightning_count):
                            angle = (i / lightning_count) * math.pi * 2
                            length = 150 + int(50 * math.sin(game_tick / 60 + i))
                            ex = boss.rect.centerx + int(length * math.cos(angle))
                            ey = boss.rect.centery + int(length * math.sin(angle))
                            pygame.draw.line(screen, (255, 50, 0), boss.rect.center, (ex, ey), 3)
                        # 中心炽热球
                        core_size = 30 + int(15 * math.sin(game_tick / 50))
                        pygame.draw.circle(screen, (255, 100, 0), boss.rect.center, core_size)
                    
                    # ===== 九头蛇 =====
                    elif boss.type == "hydra":
                        # 绿色毒液喷射
                        for head in range(3):
                            angle = (head / 3) * math.pi * 2 + game_tick / 100
                            head_x = boss.rect.centerx + int(100 * math.cos(angle))
                            head_y = boss.rect.centery + int(100 * math.sin(angle))
                            # 从头部喷出毒液
                            for jet in range(5):
                                jet_angle = angle + (jet - 2) * 0.3
                                jet_length = 80
                                jex = head_x + int(jet_length * math.cos(jet_angle))
                                jey = head_y + int(jet_length * math.sin(jet_angle))
                                pygame.draw.line(screen, (0, 200, 0), (head_x, head_y), (jex, jey), 2)
                    
                    # ===== 时之主 =====
                    elif boss.type == "chronos":
                        # 蓝色时间轮盘
                        clock_radius = 120
                        # 外轮盘（快速旋转）
                        for i in range(12):
                            angle = (game_tick / 100 + i / 12 * math.pi * 2)
                            x1 = int(boss.rect.centerx + clock_radius * math.cos(angle))
                            y1 = int(boss.rect.centery + clock_radius * math.sin(angle))
                            x2 = int(boss.rect.centerx + (clock_radius - 30) * math.cos(angle))
                            y2 = int(boss.rect.centery + (clock_radius - 30) * math.sin(angle))
                            pygame.draw.line(screen, (100, 150, 255), (x1, y1), (x2, y2), 2)
                        # 内轮盘（反向慢速旋转）
                        inner_radius = 80
                        for i in range(8):
                            angle = (-game_tick / 200 + i / 8 * math.pi * 2)
                            x = int(boss.rect.centerx + inner_radius * math.cos(angle))
                            y = int(boss.rect.centery + inner_radius * math.sin(angle))
                            pygame.draw.circle(screen, (150, 200, 255), (x, y), 3)
                    
                    # ===== 深渊凝视者 =====
                    elif boss.type == "gazer":
                        # 红色扫描射线
                        for scan in range(3):
                            angle = (game_tick / 100 + scan * 120) / 180 * math.pi
                            ex = boss.rect.centerx + int(250 * math.cos(angle))
                            ey = boss.rect.centery + int(250 * math.sin(angle))
                            pygame.draw.line(screen, (255, 0, 0), boss.rect.center, (ex, ey), 3)
                        # 眼睛瞳孔收缩
                        pupil_size = 40 + int(15 * math.sin(game_tick / 80))
                        pygame.draw.circle(screen, (255, 50, 50), boss.rect.center, pupil_size)
                    
                    # ===== 赛博巫妖 =====
                    elif boss.type == "lich":
                        # 青绿色诅咒光圈
                        for curse_layer in range(4):
                            layer_size = 100 + curse_layer * 35
                            layer_alpha = int(150 * (1 - curse_layer / 4))
                            pygame.draw.circle(screen, (100, 200, 200), boss.rect.center, layer_size, 2)
                        # 飘浮符文
                        for rune in range(6):
                            angle = (game_tick / 150 + rune * 60) / 180 * math.pi
                            rx = int(boss.rect.centerx + 120 * math.cos(angle))
                            ry = int(boss.rect.centery + 120 * math.sin(angle))
                            pygame.draw.polygon(screen, (180, 240, 240), [(rx, ry-10), (rx+10, ry+10), (rx-10, ry+10)])
                    
                    # ===== 风暴引擎 =====
                    elif boss.type == "tempest":
                        # 蓝色风力线旋转
                        for wind_layer in range(3):
                            layer_speed = 100 - wind_layer * 20
                            angle = (game_tick / layer_speed) * math.pi * 2
                            for blade in range(4):
                                blade_angle = angle + blade * math.pi / 2
                                length = 100 + wind_layer * 40
                                bx = int(boss.rect.centerx + length * math.cos(blade_angle))
                                by = int(boss.rect.centery + length * math.sin(blade_angle))
                                pygame.draw.line(screen, (140, 200, 255), boss.rect.center, (bx, by), 2 + wind_layer)
                    
                    # ===== 虚空魔像 =====
                    elif boss.type == "void_golem":
                        # 紫色齿轮旋转
                        for gear in range(4):
                            gear_angle = (game_tick / 100 + gear * 90) / 180 * math.pi
                            gear_radius = 100 + gear * 30
                            # 齿轮齿片
                            for tooth in range(12):
                                tooth_angle = gear_angle + tooth * math.pi / 6
                                r1 = 40 + gear * 20
                                r2 = 60 + gear * 20
                                x1 = int(boss.rect.centerx + r1 * math.cos(tooth_angle))
                                y1 = int(boss.rect.centery + r1 * math.sin(tooth_angle))
                                x2 = int(boss.rect.centerx + r2 * math.cos(tooth_angle))
                                y2 = int(boss.rect.centery + r2 * math.sin(tooth_angle))
                                pygame.draw.line(screen, (200, 0, 255), (x1, y1), (x2, y2), 2)
                        # 中心能量核
                        core_size = 30 + int(20 * math.sin(game_tick / 80))
                        pygame.draw.circle(screen, (255, 150, 255), boss.rect.center, core_size)
                    
                    # ===== 星渊女王 =====
                    elif boss.type == "abyss_queen":
                        # 多层星体轨道
                        for orbit in range(3):
                            orbit_speed = 150 - orbit * 40
                            orbit_angle = (game_tick / orbit_speed) * math.pi * 2
                            orbit_radius = 100 + orbit * 50
                            # 轨道线
                            pygame.draw.circle(screen, (180, 100, 255), boss.rect.center, orbit_radius, 1)
                            # 轨道上的星体
                            for star_num in range(5):
                                star_angle = orbit_angle + star_num * 2 * math.pi / 5
                                sx = int(boss.rect.centerx + orbit_radius * math.cos(star_angle))
                                sy = int(boss.rect.centery + orbit_radius * math.sin(star_angle))
                                star_size = 3 + orbit
                                brightness = int(150 + 105 * math.sin(game_tick / 60 + star_num))
                                pygame.draw.circle(screen, (brightness, brightness // 2, 230), (sx, sy), star_size)
                        # 中央王冠
                        crown_size = 40 + int(15 * math.sin(game_tick / 80))
                        pygame.draw.circle(screen, (255, 200, 255), boss.rect.center, crown_size)
                    
                    # ===== 绝音夜煞 =====
                    elif boss.type == "sonic_banshee":
                        # 音波同心圆冲击 - 快速扩散
                        for wave_num in range(4):
                            wave_offset = (game_tick / 20 + wave_num * 80) % 300
                            wave_r = int(30 + wave_offset)
                            wave_alpha = int(200 * (1 - wave_offset / 300))
                            if wave_alpha > 10:
                                pygame.draw.circle(screen, (150, 50, 200), boss.rect.center, wave_r, 4)
                        # 扭曲的声波线条
                        for line in range(16):
                            angle = math.radians(line * 22.5 + game_tick / 30)
                            distort = int(20 * math.sin(game_tick / 40 + line))
                            end_x = int(boss.rect.centerx + (150 + distort) * math.cos(angle))
                            end_y = int(boss.rect.centery + (150 + distort) * math.sin(angle))
                            pygame.draw.line(screen, (180, 80, 220), boss.rect.center, (end_x, end_y), 2)
                        # 黑暗吞噬效果 - 中心变暗
                        dark_surf = pygame.Surface((160, 160), pygame.SRCALPHA)
                        for dark_r in range(80, 0, -5):
                            dark_alpha = int(100 * (1 - dark_r / 80))
                            pygame.draw.circle(dark_surf, (10, 5, 15, dark_alpha), (80, 80), dark_r)
                        screen.blit(dark_surf, (boss.rect.centerx - 80, boss.rect.centery - 80))
                    
                    # ===== 棱镜核心 =====
                    elif boss.type == "prism_overlord":
                        # 幻彩光环 - 彩虹色旋转
                        for prism_ring in range(6):
                            ring_angle = math.radians(game_tick / 60 + prism_ring * 60)
                            ring_r = 100 + prism_ring * 25
                            hue = (prism_ring * 60 + int(game_tick / 10)) % 360
                            ring_color = pygame.Color(0)
                            ring_color.hsva = (hue, 100, 100, 100)
                            pygame.draw.circle(screen, ring_color, boss.rect.center, ring_r, 2)
                        # 折射光束 - 从中心射出的彩色光线
                        for beam in range(12):
                            beam_angle = math.radians(beam * 30 + game_tick / 25)
                            beam_hue = (beam * 30 + int(game_tick / 8)) % 360
                            beam_color = pygame.Color(0)
                            beam_color.hsva = (beam_hue, 80, 100, 100)
                            beam_end_x = int(boss.rect.centerx + 200 * math.cos(beam_angle))
                            beam_end_y = int(boss.rect.centery + 200 * math.sin(beam_angle))
                            pygame.draw.line(screen, beam_color, boss.rect.center, (beam_end_x, beam_end_y), 3)
                        # 中心白色闪光
                        flash_size = 25 + int(15 * math.sin(game_tick / 50))
                        pygame.draw.circle(screen, (255, 255, 255), boss.rect.center, flash_size)
                    
                    # ===== 腐朽剑圣 =====
                    elif boss.type == "rotting_kensei":
                        # 剑气斩痕 - 随机闪现的斜线
                        slash_phase = (game_tick // 300) % 3
                        slash_progress = (game_tick % 300) / 300
                        if slash_progress < 0.3:
                            slash_alpha = int(255 * slash_progress / 0.3)
                            slash_length = int(300 * slash_progress / 0.3)
                            slash_angle = math.radians(-45 + slash_phase * 30)
                            sx = boss.rect.centerx + int(slash_length * math.cos(slash_angle) / 2)
                            sy = boss.rect.centery + int(slash_length * math.sin(slash_angle) / 2)
                            ex = boss.rect.centerx - int(slash_length * math.cos(slash_angle) / 2)
                            ey = boss.rect.centery - int(slash_length * math.sin(slash_angle) / 2)
                            pygame.draw.line(screen, (255, 100, 100), (sx, sy), (ex, ey), 5)
                            pygame.draw.line(screen, (255, 200, 200), (sx, sy), (ex, ey), 2)
                        # 腐败气息 - 红色毒雾
                        for fog in range(8):
                            fog_angle = math.radians(fog * 45 + game_tick / 100)
                            fog_dist = 80 + int(40 * math.sin(game_tick / 80 + fog))
                            fog_x = int(boss.rect.centerx + fog_dist * math.cos(fog_angle))
                            fog_y = int(boss.rect.centery + fog_dist * math.sin(fog_angle))
                            fog_r = 15 + int(10 * math.sin(game_tick / 60 + fog))
                            fog_surf = pygame.Surface((fog_r * 2, fog_r * 2), pygame.SRCALPHA)
                            pygame.draw.circle(fog_surf, (150, 30, 30, 80), (fog_r, fog_r), fog_r)
                            screen.blit(fog_surf, (fog_x - fog_r, fog_y - fog_r))
                        # 寄生触手蠕动
                        for tentacle in range(5):
                            t_angle = math.radians(tentacle * 72 + game_tick / 120)
                            t_base_x = boss.rect.centerx + int(60 * math.cos(t_angle))
                            t_base_y = boss.rect.centery + int(60 * math.sin(t_angle))
                            t_points = [(t_base_x, t_base_y)]
                            for seg in range(4):
                                seg_x = t_base_x + int((30 + seg * 20) * math.cos(t_angle + math.sin(game_tick / 50 + seg) * 0.5))
                                seg_y = t_base_y + int((30 + seg * 20) * math.sin(t_angle + math.sin(game_tick / 50 + seg) * 0.5))
                                t_points.append((seg_x, seg_y))
                            pygame.draw.lines(screen, (200, 50, 50), False, t_points, 4)
                    
                    # ===== 悖论时钟 =====
                    elif boss.type == "paradox_clockwork":
                        # 巨大时钟表盘
                        dial_r = 150
                        pygame.draw.circle(screen, (205, 165, 95), boss.rect.center, dial_r, 3)
                        pygame.draw.circle(screen, (185, 145, 75), boss.rect.center, dial_r - 10, 2)
                        # 刻度
                        for hour in range(12):
                            h_angle = math.radians(hour * 30 - 90)
                            h_inner = dial_r - 20
                            h_outer = dial_r - 5
                            hx1 = int(boss.rect.centerx + h_inner * math.cos(h_angle))
                            hy1 = int(boss.rect.centery + h_inner * math.sin(h_angle))
                            hx2 = int(boss.rect.centerx + h_outer * math.cos(h_angle))
                            hy2 = int(boss.rect.centery + h_outer * math.sin(h_angle))
                            pygame.draw.line(screen, (220, 180, 100), (hx1, hy1), (hx2, hy2), 3)
                        # 疯狂旋转的指针
                        hour_angle = math.radians(game_tick / 50 - 90)
                        minute_angle = math.radians(game_tick / 15 - 90)
                        second_angle = math.radians(game_tick / 3 - 90)
                        pygame.draw.line(screen, (80, 50, 30), boss.rect.center, 
                                       (boss.rect.centerx + int(60 * math.cos(hour_angle)),
                                        boss.rect.centery + int(60 * math.sin(hour_angle))), 5)
                        pygame.draw.line(screen, (100, 70, 40), boss.rect.center,
                                       (boss.rect.centerx + int(100 * math.cos(minute_angle)),
                                        boss.rect.centery + int(100 * math.sin(minute_angle))), 3)
                        pygame.draw.line(screen, (180, 50, 50), boss.rect.center,
                                       (boss.rect.centerx + int(130 * math.cos(second_angle)),
                                        boss.rect.centery + int(130 * math.sin(second_angle))), 2)
                        # 齿轮旋转光环
                        for gear_ring in range(3):
                            gear_r = 170 + gear_ring * 30
                            gear_rot = game_tick / (60 + gear_ring * 20) * (1 if gear_ring % 2 == 0 else -1)
                            for tooth in range(20):
                                tooth_angle = math.radians(tooth * 18 + gear_rot * 50)
                                tx = int(boss.rect.centerx + gear_r * math.cos(tooth_angle))
                                ty = int(boss.rect.centery + gear_r * math.sin(tooth_angle))
                                pygame.draw.circle(screen, (185, 145, 75), (tx, ty), 4)
                        # 时间裂痕
                        for crack in range(6):
                            crack_angle = math.radians(crack * 60 + 15)
                            for seg in range(5):
                                seg_start = 30 + seg * 25
                                seg_end = 50 + seg * 25
                                cx1 = int(boss.rect.centerx + seg_start * math.cos(crack_angle + math.sin(seg) * 0.2))
                                cy1 = int(boss.rect.centery + seg_start * math.sin(crack_angle + math.sin(seg) * 0.2))
                                cx2 = int(boss.rect.centerx + seg_end * math.cos(crack_angle + math.sin(seg + 1) * 0.2))
                                cy2 = int(boss.rect.centery + seg_end * math.sin(crack_angle + math.sin(seg + 1) * 0.2))
                                pygame.draw.line(screen, (255, 220, 150), (cx1, cy1), (cx2, cy2), 1)
                    
                    # ===== 熔核巨兽 =====
                    elif boss.type == "molten_behemoth":
                        # 熔岩光环 - 橙红色脉动
                        for lava_ring in range(4):
                            lava_r = 120 + lava_ring * 35 + int(15 * math.sin(game_tick / 60 + lava_ring))
                            lava_alpha = int(150 - lava_ring * 30)
                            pygame.draw.circle(screen, (255, 100 + lava_ring * 20, 30), boss.rect.center, lava_r, 4)
                        # 岩浆喷发粒子
                        for eruption in range(12):
                            e_angle = math.radians(eruption * 30 + game_tick / 40)
                            e_dist = 80 + int(60 * abs(math.sin(game_tick / 100 + eruption)))
                            e_x = int(boss.rect.centerx + e_dist * math.cos(e_angle))
                            e_y = int(boss.rect.centery + e_dist * math.sin(e_angle))
                            e_size = 8 + int(6 * math.sin(game_tick / 50 + eruption))
                            pygame.draw.circle(screen, (255, 150, 50), (e_x, e_y), e_size)
                            pygame.draw.circle(screen, (255, 220, 100), (e_x, e_y), e_size - 3)
                        # 热浪扭曲 - 上升的热气
                        for heat in range(8):
                            heat_x = boss.rect.centerx - 80 + heat * 23
                            heat_y_base = boss.rect.centery - 100
                            heat_offset = int(15 * math.sin(game_tick / 30 + heat))
                            for wave_seg in range(5):
                                wy = heat_y_base - wave_seg * 25
                                wx = heat_x + int(10 * math.sin(game_tick / 40 + wave_seg + heat))
                                wave_alpha = int(80 * (1 - wave_seg / 5))
                                wave_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                                pygame.draw.ellipse(wave_surf, (255, 200, 100, wave_alpha), (0, 5, 20, 10))
                                screen.blit(wave_surf, (wx - 10, wy - 10))
                        # 中心熔岩核
                        core_pulse = int(20 * math.sin(game_tick / 40))
                        pygame.draw.circle(screen, (255, 80, 20), boss.rect.center, 50 + core_pulse)
                        pygame.draw.circle(screen, (255, 180, 80), boss.rect.center, 35 + core_pulse)
                        pygame.draw.circle(screen, (255, 255, 200), boss.rect.center, 20 + core_pulse)
                    
                    # 通用效果：enraged闪烁和被击中闪白
                    if boss.enraged:
                        flash_intensity = int(100 * abs(math.sin(game_tick / 50)))
                        s = pygame.Surface((boss.rect.width + 40, boss.rect.height + 40), pygame.SRCALPHA)
                        pygame.draw.rect(s, (255, 50, 50, flash_intensity), (0, 0, s.get_width(), s.get_height()), 5)
                        safe_blit(screen, s, (boss.rect.x - 20, boss.rect.y - 20))
                    
                    if hasattr(boss, '_hit_flash_timer') and boss._hit_flash_timer > 0:
                        flash_alpha = int(150 * (boss._hit_flash_timer / 10))
                        s = pygame.Surface(boss.image.get_size(), pygame.SRCALPHA)
                        pygame.draw.rect(s, (255, 255, 255, flash_alpha), s.get_rect())
                        safe_blit(screen, s, boss.rect)
                        boss._hit_flash_timer -= 1
                
                # ========== 赛博朋克视觉反馈 ==========
                # warning and top HUD drawn after possible screen shake
                if len(mobs) == 0 and wave > 1:
                    # ========== 成就系统：波数更新 ==========
                    if player and hasattr(player, 'achievement_manager'):
                        player.achievement_manager.update_max_wave(wave)
                        new_achievements = player.achievement_manager.check_achievements(player)
                        if new_achievements:
                            sound_mgr.play("achievement")
                            for ach_id in new_achievements:
                                ach = player.achievement_manager.achievements[ach_id]
                                log_info(f"解锁成就: {ach.name}")
                                achievement_notifications.append((ach, 180))  # 3秒显示
                            try:
                                player.achievement_manager.save_to_file()
                            except Exception:
                                log_error("保存成就时发生错误")
                    
                # ========== 肉鸽系统：绘制升级 UI 和被动增益更新 ==========
                if levelup_ready:
                    safe_call_draw(draw_levelup_ui)
                
                # 每帧更新被动增益
                safe_call_draw(player.update_buffs)
                # If boss phase transitioned recently, perform screen shake
                if boss and getattr(boss, 'phase_change_timer', 0) > 0:
                    # Decrease boss timer
                    boss.phase_change_timer -= 1
                    # Calculate shake offset
                    mag = getattr(boss, 'phase_change_magnitude', 6)
                    off_x = random.randint(-mag, mag)
                    off_y = random.randint(-mag, mag)
                    # Capture current screen and blit back with offset, leaving HUD to draw after
                    tmp = screen.copy()
                    screen.fill(CYBER_DEEP_BLACK)
                    screen.blit(tmp, (off_x, off_y))
                
                # Draw HUD and warning indicator after shake so they stay fixed on screen
                # 只在非升级UI时显示HUD
                if not levelup_ready:
                    safe_call_draw(draw_top_hud)
                    # 【新】显示实时统计面板
                    safe_call_draw(draw_game_stats)
                    # Boss挑战模式进度显示
                    if boss_challenge_active and (game_state == "game" or game_state == "boss_challenge_play"):
                        challenge_font = pygame.font.SysFont("SimHei", 28)
                        progress_text = challenge_font.render(f"挑战进度: {boss_challenge_current}/{len(boss_challenge_order)}", True, CYAN)
                        screen.blit(progress_text, (20, HEIGHT - 80))
                    safe_call_draw(draw_warning_indicator)  # BOSS警告闪烁边框
                    # 【新】房间系统小地图（仅房间模式显示）
                    if room_manager and game_mode == "roguelike" and not boss_challenge_active:
                        safe_call_draw(lambda: room_manager.draw_minimap(screen, 10, 200, 200, 160))
                
                # 成就通知始终显示
                safe_call_draw(draw_achievement_notifications)
                
                # 【新】协同触发通知 - 屏幕中心爆发提示
                safe_call_draw(draw_synergy_notifications)
                
                # 【新】协同combo提示
                safe_call_draw(draw_synergy_combo_hints)
                
                # 注意：商店UI和房间选择UI已在暂停分支中绘制，此处不重复绘制
                
                # 奖励飘字动画（房间模式）
                if room_manager and game_mode == "roguelike":
                    safe_call_draw(lambda: room_manager.draw_reward_floaters(screen))
                    # 波次信息UI
                    if not room_manager.show_completion_ui and not is_paused:
                        safe_call_draw(lambda: room_manager.draw_wave_info(screen))
                
                # 显示FPS（中间上方）- 根据设置决定是否显示
                if game_settings.get("show_fps", True):
                    current_fps = clock.get_fps()
                    fps_color = GREEN if current_fps >= 100 else YELLOW if current_fps >= 60 else RED
                    fps_text = pygame.font.SysFont("Arial", 32, bold=True).render(f"FPS: {int(current_fps)}", True, fps_color)
                    fps_rect = fps_text.get_rect(center=(WIDTH // 2, 30))
                    screen.blit(fps_text, fps_rect)

        pygame.display.flip()

    except Exception as e:
        # Log main loop exceptions to file
        log_error("Main Loop Error:")
        log_error(traceback.format_exc())