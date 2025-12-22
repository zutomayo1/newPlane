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
from roguelite import ItemManager
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
    'list_area': pygame.Rect(50, 80, 300, HEIGHT - 150),
    'slot_0': pygame.Rect(400, 150, 240, 80),
    'slot_1': pygame.Rect(400, 270, 240, 80),
    'slot_2': pygame.Rect(400, 390, 240, 80),
    'btn_research_normal': pygame.Rect(400, HEIGHT - 100, 200, 50),
    'btn_research_elite': pygame.Rect(620, HEIGHT - 100, 200, 50),
    'detail_area': pygame.Rect(WIDTH - 350, 80, 300, HEIGHT - 150),
    'btn_upgrade': pygame.Rect(WIDTH - 300, HEIGHT - 140, 200, 50),
    'btn_back': pygame.Rect(50, HEIGHT - 60, 100, 40)
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

# 成就菜单
achievement_page = 0

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

# 音效实验室
sound_lab_all_tracks = []
sound_lab_tracks = []
sound_lab_scroll_index = 0
sound_lab_selected = 0
sound_lab_now_playing = None
sound_lab_filter = "all"

# 音乐主题 & 动态音乐
dynamic_music_state = {"state": None, "intensity": 0.0}
dynamic_music_boss_phase = 0

# 暂停菜单状态
pause_menu_selected = 0  # 0: 继续, 1: 重新开始, 2: 退出战斗

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
    draw_text(screen, "音乐枢纽", 64, WIDTH//2, 90, CYAN, glow=True)
    back_rect = _get_audio_hub_back_rect()
    mx, my = pygame.mouse.get_pos()
    back_hover = back_rect.collidepoint(mx, my)
    draw_cyber_rect(screen, back_rect, (32, 34, 46) if back_hover else (20, 24, 32), alpha=240, fill=True)
    draw_cyber_rect(screen, back_rect, CYAN if back_hover else GRAY, border_width=2, fill=False)
    draw_text(screen, "返回主菜单", 24, back_rect.centerx, back_rect.centery - 10, WHITE if back_hover else GRAY)
    rects = _get_audio_hub_card_rects()
    for idx, (rect, option) in enumerate(zip(rects, AUDIO_HUB_OPTIONS)):
        hover = rect.collidepoint(mx, my)
        selected = (idx == audio_hub_selected)
        base_color = option["color"]
        bg = (
            (base_color[0]//2 + 30, base_color[1]//2 + 18, base_color[2]//2 + 25)
            if hover or selected else (20, 24, 36)
        )
        border = base_color if hover or selected else (70, 70, 90)
        draw_cyber_rect(screen, rect, bg, alpha=235, fill=True)
        draw_cyber_rect(screen, rect, border, border_width=4 if selected else 2, fill=False)
        draw_text(screen, option["title"], 42, rect.centerx, rect.y + 60, WHITE, glow=selected)
        draw_text(screen, option["tagline"], 24, rect.centerx, rect.y + 110, base_color)
        desc_lines = textwrap.wrap(option["desc"], width=18)
        text_y = rect.y + 160
        for line in desc_lines[:5]:
            draw_text(screen, line, 20, rect.centerx, text_y, GRAY)
            text_y += 28
        draw_text(screen, "点击进入", 20, rect.centerx, rect.bottom - 70, WHITE)
        if selected:
            draw_text(screen, "●", 28, rect.centerx, rect.bottom - 30, base_color)


def draw_music_library_ui():
    draw_text(screen, "音乐馆", 56, WIDTH//2, 60, CYAN, glow=True)
    list_rect, info_rect, controls = get_music_library_layout()
    draw_cyber_rect(screen, list_rect, (15, 20, 35), alpha=230, fill=True)
    draw_cyber_rect(screen, list_rect, CYAN, border_width=2, fill=False)
    draw_cyber_rect(screen, info_rect, (12, 16, 24), alpha=230, fill=True)
    draw_cyber_rect(screen, info_rect, MAGENTA, border_width=2, fill=False)
    draw_text(screen, f"曲目列表 ({len(music_library_tracks)})", 24, list_rect.x + 10, list_rect.y - 40, WHITE, align="left")
    draw_text(screen, "曲目信息", 24, info_rect.x + 10, info_rect.y - 40, WHITE, align="left")

    controls_layout = build_music_library_controls(list_rect)
    search_rect = controls_layout["search_rect"]
    sort_buttons = controls_layout["sort_buttons"]
    chips = controls_layout["filter_chips"]
    content_top = controls_layout["content_top"]

    mx, my = pygame.mouse.get_pos()

    # Search box
    search_hover = search_rect.collidepoint(mx, my)
    search_active = music_library_search_active
    draw_cyber_rect(
        screen,
        search_rect,
        (32, 38, 52) if (search_hover or search_active) else (22, 26, 34),
        alpha=235,
        fill=True,
    )
    draw_cyber_rect(
        screen,
        search_rect,
        CYAN if search_active else (CYAN if search_hover else GRAY),
        border_width=2,
        fill=False,
    )
    search_text = music_library_search_query or "搜索曲目 / 描述"
    color = WHITE if music_library_search_query else GRAY
    draw_text(screen, search_text, 18, search_rect.x + 10, search_rect.y + 8, color, align="left")

    # Sort buttons
    for mode, label, rect in sort_buttons:
        active = (mode == music_library_sort_mode)
        hover = rect.collidepoint(mx, my)
        bg = (35, 40, 60) if (active or hover) else (22, 24, 33)
        border = CYAN if active else (CYAN if hover else GRAY)
        draw_cyber_rect(screen, rect, bg, alpha=220, fill=True)
        draw_cyber_rect(screen, rect, border, border_width=2 if (active or hover) else 1, fill=False)
        draw_text(screen, label, 16, rect.centerx, rect.centery - 8, WHITE if active else (200, 200, 210))

    # Scene filter chips
    for key, label, rect in chips:
        active = (key == music_library_filter)
        hover = rect.collidepoint(mx, my)
        base_col = CYAN if active else (80, 90, 110)
        draw_cyber_rect(screen, rect, (30, 36, 50) if hover or active else (20, 24, 32), alpha=230, fill=True)
        draw_cyber_rect(screen, rect, base_col if (hover or active) else GRAY, border_width=1, fill=False)
        draw_text(screen, label, 18, rect.centerx, rect.centery - 8, WHITE if active else (200, 200, 210))

    padding = 12
    row_height = MUSIC_LIBRARY_ITEM_HEIGHT - 20
    visible_rows = _music_library_visible_rows()
    start_idx = music_library_scroll_index
    end_idx = min(len(music_library_tracks), start_idx + visible_rows)
    base_y = content_top

    if not music_library_tracks:
        msg = "未扫描到音乐文件" if getattr(sound_mgr, "enabled", True) else "音频系统未启用"
        draw_text(screen, msg, 24, list_rect.centerx, list_rect.centery, GRAY)
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
            bg_color = (40, 50, 70)
            if is_playing:
                bg_color = (55, 30, 30)
            if is_selected:
                bg_color = (65, 90, 130)
            draw_cyber_rect(screen, row_rect, bg_color, alpha=220, fill=True)
            border_color = CYAN if is_selected else (MAGENTA if is_playing else (60, 60, 80))
            draw_cyber_rect(screen, row_rect, border_color, border_width=2, fill=False)
            draw_text(screen, track["display"], 24, row_rect.x + 12, row_rect.y + 4, WHITE, align="left")
            source_line = _truncate_music_text(track["source"], 36)
            draw_text(screen, source_line, 18, row_rect.x + 12, row_rect.y + row_height - 18, GRAY, align="left")
            if is_playing:
                draw_text(screen, "播放中", 18, row_rect.right - 16, row_rect.centery - 10, LIME, align="right")

        if len(music_library_tracks) > visible_rows:
            scroll_track_h = list_rect.bottom - padding - base_y
            if scroll_track_h > 0:
                indicator_h = max(20, int(scroll_track_h * (visible_rows / len(music_library_tracks))))
                max_scroll = max(1, len(music_library_tracks) - visible_rows)
                indicator_y = base_y + int((scroll_track_h - indicator_h) * (music_library_scroll_index / max_scroll))
                pygame.draw.rect(screen, (50, 50, 70), (list_rect.right - 10, base_y, 4, scroll_track_h), border_radius=2)
                pygame.draw.rect(screen, CYAN, (list_rect.right - 10, indicator_y, 4, indicator_h), border_radius=2)

    draw_cyber_rect(screen, info_rect.inflate(-20, -20), (20, 28, 40), alpha=220, fill=True)
    info_inner = info_rect.inflate(-20, -20)
    info_y = info_inner.y + 10
    if 0 <= music_library_selected < len(music_library_tracks):
        current = music_library_tracks[music_library_selected]
        draw_text(screen, current["display"], 32, info_inner.x + 10, info_y, WHITE, align="left")
        info_y += 50
        draw_text(screen, f"内部ID：{current['id']}", 20, info_inner.x + 10, info_y, GRAY, align="left")
        info_y += 30
        draw_text(screen, "关联场景：", 20, info_inner.x + 10, info_y, CYBER_AMBER, align="left")
        info_y += 30
        full_text = "、".join(current.get("source_full", [])) or current.get("source", "未绑定场景")
        for line in _wrap_music_sources(full_text, limit=20, max_lines=8):
            draw_text(screen, line, 18, info_inner.x + 25, info_y, GRAY, align="left")
            info_y += 24
    else:
        draw_text(screen, "请选择一首曲目", 26, info_inner.centerx, info_inner.centery, GRAY)

    control_labels = {
        "stop": "恢复默认",
        "play": "播放选中",
        "back": "返回音乐选择",
    }
    mx, my = pygame.mouse.get_pos()
    for key, rect in controls.items():
        hover = rect.collidepoint(mx, my)
        draw_cyber_rect(screen, rect, (35, 40, 60) if hover else (20, 24, 36), alpha=230, fill=True)
        draw_cyber_rect(screen, rect, CYAN if hover else GRAY, border_width=2, fill=False)
        draw_text(screen, control_labels[key], 22, rect.centerx, rect.centery - 12, WHITE if hover else GRAY)

    now_playing_label = "当前播放："
    status_text = now_playing_label + (next((t["display"] for t in music_library_tracks if t["id"] == music_library_now_playing), _format_music_track_name(music_library_now_playing)) if music_library_now_playing else "默认菜单主题")
    status_color = LIME if music_library_now_playing else GRAY
    draw_text(screen, status_text, 22, WIDTH - 40, 30, status_color, align="right")

def draw_sound_lab_ui():
    draw_text(screen, "音效实验室", 56, WIDTH//2, 60, CYBER_AMBER, glow=True)
    list_rect, info_rect, controls = get_sound_lab_layout()
    draw_cyber_rect(screen, list_rect, (18, 20, 32), alpha=235, fill=True)
    draw_cyber_rect(screen, list_rect, CYBER_AMBER, border_width=2, fill=False)
    draw_cyber_rect(screen, info_rect, (14, 16, 26), alpha=235, fill=True)
    draw_cyber_rect(screen, info_rect, (255, 180, 80), border_width=2, fill=False)
    draw_text(screen, f"音效列表 ({len(sound_lab_tracks)})", 24, list_rect.x + 10, list_rect.y - 40, WHITE, align="left")
    draw_text(screen, "音效详情", 24, info_rect.x + 10, info_rect.y - 40, WHITE, align="left")

    mx, my = pygame.mouse.get_pos()
    chips, filter_band_height = get_sound_lab_filter_layout(list_rect)
    for key, label, rect in chips:
        active = (key == sound_lab_filter)
        hover = rect.collidepoint(mx, my)
        base_col = CYBER_AMBER if active else (120, 100, 70)
        draw_cyber_rect(screen, rect, (42, 32, 26) if hover or active else (24, 20, 18), alpha=230, fill=True)
        draw_cyber_rect(screen, rect, base_col if (hover or active) else GRAY, border_width=1, fill=False)
        draw_text(screen, label, 18, rect.centerx, rect.centery - 8, WHITE if active else (210, 200, 190))

    padding = 12
    visible_rows = _sound_lab_visible_rows()
    start_idx = sound_lab_scroll_index
    end_idx = min(len(sound_lab_tracks), start_idx + visible_rows)
    content_top = list_rect.y + padding + filter_band_height

    if not sound_lab_tracks:
        msg = "未加载到可用音效" if getattr(sound_mgr, "enabled", True) else "音频系统未启用"
        draw_text(screen, msg, 24, list_rect.centerx, list_rect.centery, GRAY)
    else:
        for row, idx in enumerate(range(start_idx, end_idx)):
            track = sound_lab_tracks[idx]
            row_rect = pygame.Rect(
                list_rect.x + padding,
                content_top + row * SOUND_LAB_ITEM_HEIGHT,
                list_rect.width - padding * 2,
                SOUND_LAB_ITEM_HEIGHT - 10,
            )
            is_selected = (idx == sound_lab_selected)
            is_playing = (sound_lab_now_playing == track["id"])
            bg_color = (46, 46, 64)
            if is_playing:
                bg_color = (60, 38, 38)
            if is_selected:
                bg_color = (70, 80, 110)
            draw_cyber_rect(screen, row_rect, bg_color, alpha=220, fill=True)
            border_color = CYBER_AMBER if is_selected else ((255, 120, 120) if is_playing else (70, 70, 90))
            draw_cyber_rect(screen, row_rect, border_color, border_width=2, fill=False)
            draw_text(screen, track["display"], 24, row_rect.x + 10, row_rect.y + 4, WHITE, align="left")
            draw_text(screen, track["category"], 18, row_rect.x + 10, row_rect.y + row_rect.height - 20, CYBER_AMBER, align="left")
            draw_text(screen, _truncate_music_text(track["desc"], 26), 16, row_rect.right - 10, row_rect.y + row_rect.height - 22, GRAY, align="right")

        if len(sound_lab_tracks) > visible_rows:
            scroll_track_h = list_rect.height - padding * 2 - filter_band_height
            if scroll_track_h > 0:
                indicator_h = max(20, int(scroll_track_h * (visible_rows / len(sound_lab_tracks))))
                max_scroll = max(1, len(sound_lab_tracks) - visible_rows)
                indicator_y = content_top + int((scroll_track_h - indicator_h) * (sound_lab_scroll_index / max_scroll))
                pygame.draw.rect(screen, (50, 50, 70), (list_rect.right - 8, content_top, 4, scroll_track_h), border_radius=2)
                pygame.draw.rect(screen, CYBER_AMBER, (list_rect.right - 8, indicator_y, 4, indicator_h), border_radius=2)

    draw_cyber_rect(screen, info_rect.inflate(-20, -20), (24, 26, 40), alpha=230, fill=True)
    info_inner = info_rect.inflate(-20, -20)
    info_y = info_inner.y + 10
    if 0 <= sound_lab_selected < len(sound_lab_tracks):
        current = sound_lab_tracks[sound_lab_selected]
        draw_text(screen, current["display"], 34, info_inner.x + 10, info_y, WHITE, align="left")
        info_y += 48
        draw_text(screen, f"类别：{current['category']}", 20, info_inner.x + 10, info_y, CYBER_AMBER, align="left")
        info_y += 28
        draw_text(screen, f"内部ID：{current['id']}", 20, info_inner.x + 10, info_y, GRAY, align="left")
        info_y += 32
        draw_text(screen, "描述：", 20, info_inner.x + 10, info_y, WHITE, align="left")
        info_y += 30
        desc_lines = textwrap.wrap(current["desc"], width=24)
        for line in desc_lines[:6]:
            draw_text(screen, line, 18, info_inner.x + 20, info_y, GRAY, align="left")
            info_y += 24
    else:
        draw_text(screen, "请选择一个音效", 26, info_inner.centerx, info_inner.centery, GRAY)

    control_labels = {
        "stop": "停止播放",
        "play": "播放选中",
        "back": "返回音乐选择",
    }
    for key, rect in controls.items():
        hover = rect.collidepoint(mx, my)
        draw_cyber_rect(screen, rect, (45, 40, 50) if hover else (25, 25, 35), alpha=230, fill=True)
        draw_cyber_rect(screen, rect, CYBER_AMBER if hover else GRAY, border_width=2, fill=False)
        draw_text(screen, control_labels[key], 22, rect.centerx, rect.centery - 12, WHITE if hover else GRAY)

    if sound_lab_now_playing:
        current_name = next((t["display"] for t in sound_lab_tracks if t["id"] == sound_lab_now_playing), _format_sfx_display(sound_lab_now_playing))
        draw_text(screen, f"当前音效：{current_name}", 22, WIDTH - 40, 30, CYBER_AMBER, align="right")
    else:
        draw_text(screen, "当前音效：无", 22, WIDTH - 40, 30, GRAY, align="right")


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
        
        # 图标
        icon_y = card_y + 50
        draw_text(screen, mode["icon"], 70, card_rect.centerx, icon_y, mode["title_color"])
        
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
    """绘制系统设置界面"""
    global settings_saved_timer, settings_saved_msg
    
    # 标题
    draw_text(screen, "系统设置", 48, WIDTH//2, 40, ORANGE, glow=True)
    
    # 保存提示
    if settings_saved_timer > 0:
        settings_saved_timer -= 1
        alpha = min(255, settings_saved_timer * 5)
        draw_text(screen, settings_saved_msg, 24, WIDTH//2, 90, LIME, glow=True)
    
    mx, my = pygame.mouse.get_pos()
    
    # 设置面板背景 - 增加高度
    panel_rect = pygame.Rect(WIDTH//2 - 450, 120, 900, HEIGHT - 220)
    draw_cyber_rect(screen, panel_rect, (10, 15, 25), alpha=230, fill=True)
    draw_cyber_rect(screen, panel_rect, CYAN, border_width=2, fill=False)
    
    # === 音量设置区域 ===
    start_y = 160
    slider_width = 400
    slider_height = 18
    
    volume_settings = [
        ("主音量", "master", sound_mgr.master_volume, CYAN),
        ("音乐音量", "music", sound_mgr.music_volume, MAGENTA),
        ("音效音量", "sfx", sound_mgr.sfx_volume, YELLOW)
    ]
    
    for idx, (label, key, value, color) in enumerate(volume_settings):
        y_pos = start_y + idx * 75
        
        # 标签
        draw_text(screen, label, 24, WIDTH//2 - 350, y_pos, WHITE)
        
        # 滑块轨道
        track_rect = pygame.Rect(WIDTH//2 - 350, y_pos + 30, slider_width, slider_height)
        pygame.draw.rect(screen, (40, 40, 50), track_rect, border_radius=10)
        pygame.draw.rect(screen, GRAY, track_rect, 2, border_radius=10)
        
        # 进度条
        progress_width = int(slider_width * value)
        if progress_width > 0:
            progress_rect = pygame.Rect(track_rect.x, track_rect.y, progress_width, slider_height)
            pygame.draw.rect(screen, color, progress_rect, border_radius=10)
        
        # 滑块手柄
        handle_x = track_rect.x + progress_width
        handle_y = track_rect.centery
        handle_radius = 15
        handle_pos = (handle_x, handle_y)
        
        # 检测是否悬停在手柄上
        is_hover = math.hypot(mx - handle_x, my - handle_y) < handle_radius + 5
        handle_color = WHITE if is_hover or settings_dragging == key else color
        
        pygame.draw.circle(screen, handle_color, handle_pos, handle_radius)
        pygame.draw.circle(screen, WHITE, handle_pos, handle_radius, 2)
        
        # 百分比显示
        percentage = int(value * 100)
        draw_text(screen, f"{percentage}%", 20, WIDTH//2 + 80, y_pos + 30, color)
    
    # === 其他设置 (左侧列) ===
    other_y = start_y + 230
    checkbox_size = 24
    
    # FPS显示开关
    fps_label = "显示FPS"
    fps_enabled = game_settings.get("show_fps", True)
    fps_checkbox = pygame.Rect(WIDTH//2 - 350, other_y, checkbox_size, checkbox_size)
    
    # 复选框
    pygame.draw.rect(screen, (40, 40, 50), fps_checkbox, border_radius=5)
    pygame.draw.rect(screen, CYAN if fps_enabled else GRAY, fps_checkbox, 2, border_radius=5)
    if fps_enabled:
        # 打勾
        pygame.draw.line(screen, CYAN, 
                        (fps_checkbox.x + 6, fps_checkbox.centery),
                        (fps_checkbox.centerx - 2, fps_checkbox.y + 20), 3)
        pygame.draw.line(screen, CYAN,
                        (fps_checkbox.centerx - 2, fps_checkbox.y + 20),
                        (fps_checkbox.x + 22, fps_checkbox.y + 8), 3)
    
    # 标签 - 紧贴复选框右侧，稍微上移
    draw_text(screen, fps_label, 22, fps_checkbox.right + 10, fps_checkbox.centery - 17, WHITE, align="left")
    
    # 屏幕震动开关
    shake_y = other_y + 40
    shake_label = "屏幕震动效果"
    shake_enabled = game_settings.get("screen_shake", True)
    shake_checkbox = pygame.Rect(WIDTH//2 - 350, shake_y, checkbox_size, checkbox_size)
    
    pygame.draw.rect(screen, (40, 40, 50), shake_checkbox, border_radius=5)
    pygame.draw.rect(screen, CYAN if shake_enabled else GRAY, shake_checkbox, 2, border_radius=5)
    if shake_enabled:
        pygame.draw.line(screen, CYAN,
                        (shake_checkbox.x + 6, shake_checkbox.centery),
                        (shake_checkbox.centerx - 2, shake_checkbox.y + 20), 3)
        pygame.draw.line(screen, CYAN,
                        (shake_checkbox.centerx - 2, shake_checkbox.y + 20),
                        (shake_checkbox.x + 22, shake_checkbox.y + 8), 3)
    
    # 标签 - 紧贴复选框右侧，稍微上移
    draw_text(screen, shake_label, 22, shake_checkbox.right + 10, shake_checkbox.centery - 17, WHITE, align="left")
    
    # 粒子效果质量 (按钮选择)
    particle_y = other_y + 80
    particle_label = "粒子效果质量"
    particle_quality = game_settings.get("particle_quality", "high")
    quality_options = ["low", "medium", "high"]
    quality_names = {"low": "低", "medium": "中", "high": "高"}
    
    draw_text(screen, particle_label, 22, WIDTH//2 - 350, particle_y - 10, WHITE, align="left")
    
    # 绘制三个选项按钮
    for i, quality in enumerate(quality_options):
        btn_x = WIDTH//2 - 350 + i * 75
        btn_rect = pygame.Rect(btn_x, particle_y + 20, 70, 32)
        is_selected = (particle_quality == quality)
        is_hover = btn_rect.collidepoint(mx, my)
        
        btn_color = LIME if is_selected else (YELLOW if is_hover else GRAY)
        pygame.draw.rect(screen, (40, 40, 50) if not is_selected else (0, 80, 0), btn_rect, border_radius=5)
        pygame.draw.rect(screen, btn_color, btn_rect, 2, border_radius=5)
        draw_text(screen, quality_names[quality], 18, btn_rect.centerx, btn_rect.centery - 10, WHITE if is_selected else GRAY)
    
    # 伤害数字显示
    damage_y = other_y + 145
    damage_label = "显示伤害数字"
    damage_enabled = game_settings.get("show_damage_numbers", True)
    damage_checkbox = pygame.Rect(WIDTH//2 - 350, damage_y, checkbox_size, checkbox_size)
    
    pygame.draw.rect(screen, (40, 40, 50), damage_checkbox, border_radius=5)
    pygame.draw.rect(screen, CYAN if damage_enabled else GRAY, damage_checkbox, 2, border_radius=5)
    if damage_enabled:
        pygame.draw.line(screen, CYAN,
                        (damage_checkbox.x + 6, damage_checkbox.centery),
                        (damage_checkbox.centerx - 2, damage_checkbox.y + 20), 3)
        pygame.draw.line(screen, CYAN,
                        (damage_checkbox.centerx - 2, damage_checkbox.y + 20),
                        (damage_checkbox.x + 22, damage_checkbox.y + 8), 3)
    
    # 标签 - 紧贴复选框右侧，稍微上移
    draw_text(screen, damage_label, 22, damage_checkbox.right + 10, damage_checkbox.centery - 17, WHITE, align="left")
    
    # 射击模式切换 (自动/手动)
    fire_y = other_y + 180
    fire_label = "射击模式"
    auto_fire = game_settings.get("auto_fire", True)
    fire_mode_options = [True, False]
    fire_mode_names = {True: "自动射击", False: "手动(空格)"}
    
    draw_text(screen, fire_label, 22, WIDTH//2 - 350, fire_y - 10, WHITE, align="left")
    
    # 绘制两个选项按钮
    for i, mode in enumerate(fire_mode_options):
        btn_x = WIDTH//2 - 350 + i * 110
        btn_rect = pygame.Rect(btn_x, fire_y + 15, 105, 30)
        is_selected = (auto_fire == mode)
        is_hover = btn_rect.collidepoint(mx, my)
        
        btn_color = LIME if is_selected else (YELLOW if is_hover else GRAY)
        pygame.draw.rect(screen, (40, 40, 50) if not is_selected else (0, 80, 0), btn_rect, border_radius=5)
        pygame.draw.rect(screen, btn_color, btn_rect, 2, border_radius=5)
        draw_text(screen, fire_mode_names[mode], 18, btn_rect.centerx, btn_rect.centery - 10, WHITE if is_selected else GRAY)
    
    # === 按钮区域 ===
    btn_y = HEIGHT - 60
    btn_width = 160
    btn_height = 45
    
    # 保存按钮
    save_btn = pygame.Rect(WIDTH//2 - btn_width - 100, btn_y, btn_width, btn_height)
    save_hover = save_btn.collidepoint(mx, my)
    draw_cyber_rect(screen, save_btn, LIME if save_hover else (0, 100, 0), alpha=200, fill=True)
    draw_cyber_rect(screen, save_btn, LIME, border_width=2, fill=False)
    draw_text(screen, "保存设置", 20, save_btn.centerx, save_btn.centery - 12, WHITE, glow=save_hover)
    
    # 恢复默认按钮
    reset_btn = pygame.Rect(WIDTH//2 - btn_width//2, btn_y, btn_width, btn_height)
    reset_hover = reset_btn.collidepoint(mx, my)
    draw_cyber_rect(screen, reset_btn, YELLOW if reset_hover else (100, 100, 0), alpha=200, fill=True)
    draw_cyber_rect(screen, reset_btn, YELLOW, border_width=2, fill=False)
    draw_text(screen, "恢复默认", 20, reset_btn.centerx, reset_btn.centery - 12, WHITE, glow=reset_hover)
    
    # 返回按钮
    back_btn = pygame.Rect(WIDTH//2 + 100, btn_y, btn_width, btn_height)
    back_hover = back_btn.collidepoint(mx, my)
    draw_cyber_rect(screen, back_btn, RED if back_hover else (100, 0, 0), alpha=200, fill=True)
    draw_cyber_rect(screen, back_btn, RED, border_width=2, fill=False)
    draw_text(screen, "返回", 20, back_btn.centerx, back_btn.centery - 12, WHITE, glow=back_hover)
    
    # 返回按钮引用（用于点击检测）
    return {
        'save': save_btn,
        'reset': reset_btn,
        'back': back_btn,
        'fps_checkbox': fps_checkbox,
        'shake_checkbox': shake_checkbox,
        'damage_checkbox': damage_checkbox,
        'particle_quality_btns': [
            (pygame.Rect(WIDTH//2 - 350 + i * 75, particle_y + 20, 70, 32), quality)
            for i, quality in enumerate(quality_options)
        ],
        'fire_mode_btns': [
            (pygame.Rect(WIDTH//2 - 350 + i * 110, other_y + 180 + 15, 105, 30), mode)
            for i, mode in enumerate([True, False])
        ],
        'sliders': [
            (pygame.Rect(WIDTH//2 - 350, start_y + 0*75 + 30, slider_width, slider_height), 'master'),
            (pygame.Rect(WIDTH//2 - 350, start_y + 1*75 + 30, slider_width, slider_height), 'music'),
            (pygame.Rect(WIDTH//2 - 350, start_y + 2*75 + 30, slider_width, slider_height), 'sfx')
        ]
    }

def draw_arsenal_ui():
    draw_text(screen, "轨道武器库", 40, WIDTH//2, 30, ORANGE, glow=True)
    draw_text(screen, f"核心: {arsenal_save_data['currencies']['cores']}", 20, WIDTH-250, 30, CYAN, align="left")
    draw_text(screen, f"芯片: {arsenal_save_data['currencies']['chips']}", 20, WIDTH-130, 30, YELLOW, align="left")

    if arsenal_msg_timer > 0:
        draw_text(screen, arsenal_msg, 24, WIDTH//2, 70, RED, glow=True)

    mx, my = pygame.mouse.get_pos()
    r = ARSENAL_UI

    # --- 左栏列表 (含滚动逻辑) ---
    draw_cyber_rect(screen, r['list_area'], (20,20,25), alpha=230, fill=True)

    # 设置剪裁区域，只在这个矩形内绘制列表内容
    screen.set_clip(r['list_area'])

    weapons = arsenal_save_data["weapons"]
    item_height = 60

    # 简单的可见性剔除
    start_y = r['list_area'].y + 10 - arsenal_scroll_y

    if not weapons:
        draw_text(screen, "暂无武器", 20, r['list_area'].centerx, r['list_area'].centery, GRAY)
    else:
        for i, w in enumerate(weapons):
            item_y = start_y + i * item_height
        
            # 如果项目完全跑出可视区域，就不绘制
            if item_y + 50 < r['list_area'].top or item_y > r['list_area'].bottom:
                continue
            
            item_rect = pygame.Rect(r['list_area'].x + 10, item_y, r['list_area'].width - 20, 50)
        
            info = WEAPON_TYPES[w['type']]
            is_sel = (i == arsenal_selected_weapon_idx)
            is_eq = (w in arsenal_save_data["loadout"])
        
            bg = (50, 50, 70) if is_sel else (30, 30, 40)
            draw_cyber_rect(screen, item_rect, bg, fill=True)
            if is_eq: pygame.draw.rect(screen, GREEN, item_rect, 2)
        
            draw_text(screen, info['name'], 18, item_rect.x+10, item_rect.y+12, info['color'], align="left")
            draw_text(screen, f"{w['stars']}★", 16, item_rect.right-10, item_rect.y+12, WHITE, align="right")

    # 绘制滚动条指示器 (简单版)
    total_h = len(weapons) * item_height
    view_h = r['list_area'].height
    if total_h > view_h:
        bar_h = max(20, (view_h / total_h) * view_h)
        bar_y = r['list_area'].y + (arsenal_scroll_y / total_h) * view_h
        pygame.draw.rect(screen, GRAY, (r['list_area'].right - 5, bar_y, 4, bar_h), border_radius=2)

    # 取消剪裁
    screen.set_clip(None)

    # 绘制边框覆盖
    draw_cyber_rect(screen, r['list_area'], GRAY, border_width=1, fill=False)

    # --- 中栏槽位 ---
    slots = [r['slot_0'], r['slot_1'], r['slot_2']]
    for i, slot_rect in enumerate(slots):
        draw_cyber_rect(screen, slot_rect, (30,30,40), fill=True)
        w = arsenal_save_data["loadout"][i]
        bc = GRAY
        if w:
            info = WEAPON_TYPES[w['type']]
            bc = info['color']
            draw_text(screen, info['name'], 20, slot_rect.centerx, slot_rect.y+20, bc)
            draw_text(screen, f"★{w['stars']}", 16, slot_rect.centerx, slot_rect.y+50, WHITE)
        else:
            draw_text(screen, "空槽位", 18, slot_rect.centerx, slot_rect.centery-10, GRAY)
        draw_cyber_rect(screen, slot_rect, bc, border_width=2, fill=False)
        draw_text(screen, f"槽位{chr(65+i)}", 14, slot_rect.x, slot_rect.y-20, GRAY, align="left")

    # --- 按钮 ---
    hn = r['btn_research_normal'].collidepoint(mx, my)
    he = r['btn_research_elite'].collidepoint(mx, my)

    draw_cyber_rect(screen, r['btn_research_normal'], (100,0,100) if hn else (60,0,60), fill=True)
    draw_text(screen, "标准研发（消耗20核心）", 16, r['btn_research_normal'].centerx, r['btn_research_normal'].centery-8, WHITE)

    draw_cyber_rect(screen, r['btn_research_elite'], (200,150,0) if he else (150,100,0), fill=True)
    draw_text(screen, "精密研发（消耗3芯片）", 16, r['btn_research_elite'].centerx, r['btn_research_elite'].centery-8, WHITE)

    # --- 右栏详情 ---
    draw_cyber_rect(screen, r['detail_area'], (15,15,20), fill=True)
    draw_cyber_rect(screen, r['detail_area'], CYAN, border_width=1, fill=False)

    if 0 <= arsenal_selected_weapon_idx < len(weapons):
        w = weapons[arsenal_selected_weapon_idx]
        info = WEAPON_TYPES[w['type']]
        cx = r['detail_area'].centerx
        y_start = r['detail_area'].y
    
        t = pygame.time.get_ticks() * 0.002
        pts = [(cx + math.cos(t+j*1.5)*40, y_start + 80 + math.sin(t+j*1.5)*30) for j in range(4)]
        pygame.draw.lines(screen, info['color'], True, pts, 3)
    
        draw_text(screen, info['name'], 28, cx, y_start+130, info['color'], glow=True)
        draw_text(screen, f"{w['stars']} 星级", 20, cx, y_start+170, WHITE)
        mult = 1 + (w['stars'] - 1) * 0.3
        draw_text(screen, f"伤害: {mult:.1f}x", 18, cx, y_start+200, LIME)
    
        desc = info['desc']
        lines = [desc[k:k+13] for k in range(0, len(desc), 13)]
        for k, line in enumerate(lines):
            draw_text(screen, line, 18, cx, y_start+240+k*25, GRAY)
    
        cost = w['stars'] * 10
        can_up = arsenal_save_data["currencies"]["cores"] >= cost
        h_up = r['btn_upgrade'].collidepoint(mx, my)
        c_up = LIME if can_up else RED
        draw_cyber_rect(screen, r['btn_upgrade'], (40,40,40), fill=True)
        draw_cyber_rect(screen, r['btn_upgrade'], c_up, border_width=2, fill=False)
        draw_text(screen, f"升级 (-{cost}核心)", 20, r['btn_upgrade'].centerx, r['btn_upgrade'].centery-10, c_up)
    else:
        draw_text(screen, "请选择左侧武器", 20, r['detail_area'].centerx, r['detail_area'].centery, GRAY)

    hb = r['btn_back'].collidepoint(mx, my)
    draw_cyber_rect(screen, r['btn_back'], GRAY, fill=True)
    if hb: draw_cyber_rect(screen, r['btn_back'], WHITE, border_width=2, fill=False)
    draw_text(screen, "返回", 20, r['btn_back'].centerx, r['btn_back'].centery-10, WHITE)

def draw_background_settings_ui():
    """背景设置界面 - 分页版本"""
    draw_text(screen, "背景设置", 40, WIDTH//2, 30, (100, 200, 255), glow=True)
    
    mx, my = pygame.mouse.get_pos()
    
    # 获取所有可用背景
    from systems import BackgroundManager
    bg_styles = BackgroundManager.BG_STYLES
    bg_list = list(bg_styles.items())
    
    # 分页配置
    cards_per_row = 4
    rows_per_page = 2
    cards_per_page = cards_per_row * rows_per_page  # 每页8个
    total_pages = (len(bg_list) + cards_per_page - 1) // cards_per_page
    
    # 确保页码有效
    global background_settings_page
    background_settings_page = max(0, min(background_settings_page, total_pages - 1))
    
    # 获取当前页的背景
    page_start = background_settings_page * cards_per_page
    page_end = min(page_start + cards_per_page, len(bg_list))
    page_items = bg_list[page_start:page_end]
    
    # 绘制页码指示器
    page_text = f"第 {background_settings_page + 1}/{total_pages} 页"
    draw_text(screen, page_text, 20, WIDTH//2, 80, CYAN)
    
    # 绘制背景选项卡
    card_w = 280
    card_h = 200
    gap = 30
    start_x = (WIDTH - (cards_per_row * card_w + (cards_per_row - 1) * gap)) // 2
    start_y = 130
    
    # 绘制当前页的背景卡片
    for local_idx, (style_key, style_data) in enumerate(page_items):
        global_idx = page_start + local_idx  # 全局索引
        row = local_idx // cards_per_row
        col = local_idx % cards_per_row
        
        x = start_x + col * (card_w + gap)
        y = start_y + row * (card_h + gap)
        
        card_rect = pygame.Rect(x, y, card_w, card_h)
        
        # 检查是否是当前选中的背景
        is_selected = (bg_manager.current_style == style_key)
        is_hover = card_rect.collidepoint(mx, my) and not is_selected
        is_keyboard_selected = (global_idx == background_settings_selected)  # 键盘选中
        
        # 绘制卡片背景
        if is_selected:
            # 当前使用的背景 - 蓝色高亮
            draw_cyber_rect(screen, card_rect, (50, 100, 150), fill=True)
            draw_cyber_rect(screen, card_rect, (100, 200, 255), border_width=3, fill=False)
        elif is_keyboard_selected:
            # 键盘选中但未应用
            draw_cyber_rect(screen, card_rect, (60, 60, 80), fill=True)
            draw_cyber_rect(screen, card_rect, YELLOW, border_width=3, fill=False)
        elif is_hover:
            # 鼠标悬停预览 - 轻微高亮,不改变背景
            draw_cyber_rect(screen, card_rect, (35, 35, 45), fill=True)
            draw_cyber_rect(screen, card_rect, (150, 150, 150), border_width=1, fill=False)
        else:
            # 默认状态
            draw_cyber_rect(screen, card_rect, (30, 30, 40), fill=True)
            draw_cyber_rect(screen, card_rect, GRAY, border_width=1, fill=False)
        
        # 绘制背景预览（小型版本）
        preview_surf = pygame.Surface((card_w - 20, 120))
        preview_surf.fill(style_data["base_color"])
        
        # 获取元素配置
        elements = style_data.get("elements", {})
        
        # 绘制一些星星作为预览
        star_count = elements.get("stars", 0)
        if star_count > 0:
            for _ in range(min(30, star_count // 5)):
                sx = random.randint(0, card_w - 20)
                sy = random.randint(0, 120)
                pygame.draw.circle(preview_surf, (200, 200, 200), (sx, sy), 1)
        
        # 如果有网格，绘制简化网格
        if elements.get("grid", False) and style_data.get("grid_color"):
            grid_color = style_data["grid_color"]
            for gx in range(0, card_w - 20, 40):
                pygame.draw.line(preview_surf, (*grid_color, 80), (gx, 0), (gx, 120), 1)
            for gy in range(0, 120, 40):
                pygame.draw.line(preview_surf, (*grid_color, 80), (0, gy), (card_w - 20, gy), 1)
        
        screen.blit(preview_surf, (x + 10, y + 10))
        
        # 绘制背景名称
        name_color = (100, 200, 255) if is_selected else WHITE
        draw_text(screen, style_data["name"], 24, card_rect.centerx, y + 150, name_color)
        
        # 绘制选中标记
        if is_selected:
            check_text = "✓ 当前使用"
            draw_text(screen, check_text, 18, card_rect.centerx, y + 175, LIME)
    
    # 绘制上一页/下一页按钮（放在卡片下方那一行的左右两侧）
    button_y = start_y + rows_per_page * (card_h + gap) + 30
    button_w = 100
    button_h = 50
    
    # 上一页按钮（左侧）
    prev_btn = pygame.Rect(80, button_y, button_w, button_h)
    if background_settings_page > 0:
        prev_hover = prev_btn.collidepoint(mx, my)
        prev_color = YELLOW if prev_hover else CYAN
        draw_cyber_rect(screen, prev_btn, (30, 30, 40), fill=True)
        draw_cyber_rect(screen, prev_btn, prev_color, border_width=2, fill=False)
        draw_text(screen, "上一页", 20, prev_btn.centerx, prev_btn.centery - 10, prev_color)
    else:
        draw_cyber_rect(screen, prev_btn, (20, 20, 25), fill=True)
        draw_cyber_rect(screen, prev_btn, GRAY, border_width=1, fill=False)
        draw_text(screen, "上一页", 20, prev_btn.centerx, prev_btn.centery - 10, GRAY)
    
    # 下一页按钮（右侧）
    next_btn = pygame.Rect(WIDTH - 180, button_y, button_w, button_h)
    if background_settings_page < total_pages - 1:
        next_hover = next_btn.collidepoint(mx, my)
        next_color = YELLOW if next_hover else CYAN
        draw_cyber_rect(screen, next_btn, (30, 30, 40), fill=True)
        draw_cyber_rect(screen, next_btn, next_color, border_width=2, fill=False)
        draw_text(screen, "下一页", 20, next_btn.centerx, next_btn.centery - 10, next_color)
    else:
        draw_cyber_rect(screen, next_btn, (20, 20, 25), fill=True)
        draw_cyber_rect(screen, next_btn, GRAY, border_width=1, fill=False)
        draw_text(screen, "下一页", 20, next_btn.centerx, next_btn.centery - 10, GRAY)
    
    # 操作提示
    draw_text(screen, "点击卡片切换背景 | 方向键导航 | Enter确认 | 鼠标滚轮翻页", 16, WIDTH//2, HEIGHT - 110, (150, 150, 150))
    
    # 返回按钮
    back_btn = pygame.Rect(WIDTH//2 - 60, HEIGHT - 80, 120, 50)
    hb = back_btn.collidepoint(mx, my)
    draw_cyber_rect(screen, back_btn, GRAY, fill=True)
    if hb: draw_cyber_rect(screen, back_btn, WHITE, border_width=2, fill=False)
    draw_text(screen, "返回", 22, back_btn.centerx, back_btn.centery-10, WHITE)

def draw_codex_ui():
    draw_text(screen, "机密档案", 40, WIDTH//2, 30, BLUE, glow=True)
    r = CODEX_UI
    mx, my = pygame.mouse.get_pos()
    
    # Tabs - 3个标签
    tab_width = 120
    tab_height = 40
    tab_y = 80
    tab_start_x = WIDTH//2 - (tab_width * 3 + 20) // 2
    
    # 机体数据标签
    tab_plane_rect = pygame.Rect(tab_start_x, tab_y, tab_width, tab_height)
    c1 = CYAN if codex_tab == 0 else GRAY
    draw_cyber_rect(screen, tab_plane_rect, (30,30,40), fill=True)
    if codex_tab == 0: draw_cyber_rect(screen, tab_plane_rect, c1, border_width=2, fill=False)
    draw_text(screen, "机体数据", 18, tab_plane_rect.centerx, tab_plane_rect.centery-10, c1)
    
    # 领主图鉴标签
    tab_boss_rect = pygame.Rect(tab_start_x + tab_width + 10, tab_y, tab_width, tab_height)
    c2 = RED if codex_tab == 1 else GRAY
    draw_cyber_rect(screen, tab_boss_rect, (30,30,40), fill=True)
    if codex_tab == 1: draw_cyber_rect(screen, tab_boss_rect, c2, border_width=2, fill=False)
    draw_text(screen, "领主图鉴", 18, tab_boss_rect.centerx, tab_boss_rect.centery-10, c2)
    
    # 敌人图鉴标签
    tab_enemy_rect = pygame.Rect(tab_start_x + (tab_width + 10) * 2, tab_y, tab_width, tab_height)
    c3 = ORANGE if codex_tab == 2 else GRAY
    draw_cyber_rect(screen, tab_enemy_rect, (30,30,40), fill=True)
    if codex_tab == 2: draw_cyber_rect(screen, tab_enemy_rect, c3, border_width=2, fill=False)
    draw_text(screen, "敌人图鉴", 18, tab_enemy_rect.centerx, tab_enemy_rect.centery-10, c3)
    
    # 保存标签矩形供点击检测使用
    r['tab_plane'] = tab_plane_rect
    r['tab_boss'] = tab_boss_rect
    r['tab_enemy'] = tab_enemy_rect

    def _enemy_preview(enemy_id: str, color: tuple) -> pygame.Surface:
        """使用真实敌人渲染逻辑生成图鉴预览。"""
        try:
            t = pygame.time.get_ticks() * 0.06  # 约等于游戏内每秒 60 tick 的节奏
            return build_enemy_preview_surface(enemy_id, t=t, box=180, color_override=color)
        except Exception:
            fallback = pygame.Surface((180, 180), pygame.SRCALPHA)
            pygame.draw.circle(fallback, color, (90, 90), 26, 2)
            return fallback
    
    # List View (Scrolled)
    if codex_tab == 0:
        keys = plane_keys
        db = PLANES
        color_theme = CYAN
    elif codex_tab == 1:
        keys = list(BOSS_DB.keys())
        db = BOSS_DB
        color_theme = RED
    else:  # codex_tab == 2
        from enemy_manager import enemy_type_manager
        enemy_data = enemy_type_manager.get_regular_types()
        keys = [e["id"] for e in enemy_data]
        db = {e["id"]: e for e in enemy_data}
        color_theme = ORANGE

    draw_cyber_rect(screen, r['list_view'], (20,20,25), fill=True)
    screen.set_clip(r['list_view'])
    start_y = r['list_view'].y + 5 - codex_scroll_y
    item_h = 45
    for i, key in enumerate(keys):
        y = start_y + i * item_h
        if y + item_h < r['list_view'].top or y > r['list_view'].bottom: continue
        item_rect = pygame.Rect(r['list_view'].x + 5, y, r['list_view'].width - 10, 40)
        is_sel = (i == codex_idx)
        if is_sel: draw_cyber_rect(screen, item_rect, (50,50,70), fill=True)
        draw_text(screen, db[key]["name"], 16, item_rect.centerx, item_rect.y+10, color_theme if is_sel else GRAY)
    screen.set_clip(None)

    # Detail View
    draw_cyber_rect(screen, r['detail_area'], (15,15,20), fill=True)
    draw_cyber_rect(screen, r['detail_area'], color_theme, border_width=1, fill=False)
    
    if 0 <= codex_idx < len(keys):
        key = keys[codex_idx]
        data = db[key]
        cx = r['detail_area'].centerx
        cy = r['detail_area'].y + 50
        
        # 绘制预览图
        if codex_tab == 0:
            preview = get_plane_surf(key, PLANES.get(key, {}).get('visual', None))
        elif codex_tab == 1:
            preview = get_boss_surf(key, data["color"])
        else:  # codex_tab == 2 - 敌人图鉴
            enemy_color = tuple(data.get("color", (200, 100, 100)))
            preview = _enemy_preview(key, enemy_color)
        
        if codex_tab != 2:
            preview = pygame.transform.scale(preview, (150, 150))

        pw, ph = preview.get_width(), preview.get_height()
        safe_blit(screen, preview, (cx - pw // 2, cy))

        name_y = cy + ph + 20
        draw_text(screen, data["name"], 30, cx, name_y, data.get("color", WHITE), glow=True)
        
        # 多行描述显示
        desc = data.get("desc", "")
        desc_lines = 0
        if desc:
            # 按字符宽度换行，每行约40个中文字符
            max_chars_per_line = 40
            lines = []
            for i in range(0, len(desc), max_chars_per_line):
                lines.append(desc[i:i+max_chars_per_line])
            
            desc_start = name_y + 40
            desc_lines = len(lines)
            for idx, line in enumerate(lines):
                draw_text(screen, line, 16, cx, desc_start + idx * 28, WHITE)
        
        stats = []
        if codex_tab == 0:
            stats = [("生命", data["hp"], 200), ("速度", data["speed"]*10, 100), ("火力", data["damage"]*2, 200)]
        elif codex_tab == 1:
            stats = [(k, v, 100) for k,v in data["stats"]]
        else:  # codex_tab == 2 - 敌人数据
            stats = [
                ("生命", data.get("hp", 50), 300),
                ("速度", int(data.get("speed", 2) * 20), 100),
                ("威胁", data.get("threat_level", 1), 5)
            ]
        
        # 敌人图鉴使用更紧凑的布局
        stat_spacing = 35 if codex_tab == 2 else 40

        desc_offset = desc_lines * 28 if desc_lines else 0
        stats_base = name_y + 70 + desc_offset

        for j, (lbl, val, mxv) in enumerate(stats):
            y_off = stats_base + j*stat_spacing
            draw_text(screen, lbl, 18, r['detail_area'].x + 150, y_off, WHITE, align="left")
            pygame.draw.rect(screen, (40,40,40), (r['detail_area'].x + 230, y_off+5, 200, 10))
            fill = min(200, (val/mxv)*200)
            pygame.draw.rect(screen, data.get("color", WHITE), (r['detail_area'].x + 230, y_off+5, fill, 10))
        
        # 敌人图鉴额外显示分数
        if codex_tab == 2:
            score_y = stats_base + len(stats) * stat_spacing + 5
            draw_text(screen, f"分数: {data.get('score', 100)}", 16, r['detail_area'].x + 150, score_y, GOLD, align="left")

    hb = r['btn_back'].collidepoint(mx, my)
    draw_cyber_rect(screen, r['btn_back'], GRAY, fill=True)
    if hb: draw_cyber_rect(screen, r['btn_back'], WHITE, border_width=2, fill=False)
    draw_text(screen, "返回", 20, r['btn_back'].centerx, r['btn_back'].centery-10, WHITE)

def draw_gallery_ui():
    draw_text(screen, "战术图鉴", 40, WIDTH//2, 30, MAGENTA, glow=True)
    mx, my = pygame.mouse.get_pos()
    
    # 按1-6星品质分类（扩展到神话和至高）
    tab_labels = ["全部", "1★", "2★", "3★", "4★", "5★", "6★"]
    tab_colors = [WHITE, (150, 150, 150), (100, 200, 255), (200, 100, 255), (255, 200, 50), (255, 100, 200), (255, 255, 255)]
    tab_w = 90
    start_tx = (WIDTH - (7 * tab_w + 60)) // 2
    
    for i, lbl in enumerate(tab_labels):
        rect = pygame.Rect(start_tx + i*(tab_w+10), 80, tab_w, 40)
        is_sel = (i == gallery_tab)
        c = tab_colors[i]
        draw_cyber_rect(screen, rect, (30,30,40), fill=True)
        if is_sel: draw_cyber_rect(screen, rect, c, border_width=2, fill=False)
        draw_text(screen, lbl, 16, rect.centerx, rect.centery-10, c if is_sel else GRAY)

    # 加载肉鸽卡牌数据
    from roguelite import BASE_CARDS, MODIFIER_CARDS, SYNERGY_RULES
    all_cards = []
    # 基础卡牌
    for key, card in BASE_CARDS.items():
        all_cards.append({"id": key, "name": card["name"], "rarity": card["rarity"], 
                        "desc": card.get("desc", ""), "type": "base", "data": card})
    # 参数卡牌
    for key, card in MODIFIER_CARDS.items():
        all_cards.append({"id": key, "name": card["name"], "rarity": card["rarity"],
                        "desc": card.get("desc", ""), "type": "modifier", "data": card})
    # 协同规则
    for key, synergy in SYNERGY_RULES.items():
        all_cards.append({"id": key, "name": synergy["name"], "rarity": synergy["rarity"],
                        "desc": synergy.get("desc", ""), "type": "synergy", "data": synergy})
    
    # 按品质筛选 (tab 0=全部, 1=1星, 2=2星, 3=3星, 4=4星, 5=5星, 6=6星)
    if gallery_tab == 0: 
        items = all_cards
    else: 
        items = [it for it in all_cards if it['rarity'] == gallery_tab]
    
    start_y = 140
    cols = 3  # 改为3列,让每个卡片更宽
    card_w = 360  # 增大卡片宽度
    card_h = 180  # 增大卡片高度
    gap = 30  # 增大间距
    start_gx = (WIDTH - (cols*card_w + (cols-1)*gap)) // 2
    
    items_per_page = 6  # 每页6个(2行×3列)
    start_idx = gallery_page * items_per_page
    end_idx = min(start_idx + items_per_page, len(items))
    
    if not items: draw_text(screen, "无相关数据", 24, WIDTH//2, HEIGHT//2, GRAY)
    
    for i in range(start_idx, end_idx):
        item = items[i]
        rel_i = i - start_idx
        r = rel_i // cols
        c = rel_i % cols
        x = start_gx + c * (card_w + gap)
        y = start_y + r * (card_h + gap)
        rect = pygame.Rect(x, y, card_w, card_h)
        rc = RARITY_COLORS[item['rarity']]
        # 渐变背景
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        for i in range(card_h):
            alpha = int(220 - i / card_h * 40)
            pygame.draw.rect(card_surf, (30, 30, 50, alpha), (0, i, card_w, 1))
        screen.blit(card_surf, (x, y))
        
        # 边框
        draw_cyber_rect(screen, rect, rc, border_width=2, fill=False)
        
        # 顶部标题栏
        pygame.draw.rect(screen, (*rc, 120), (x+2, y+2, card_w-4, 40))
        
        # 显示卡牌名称和品质星级
        stars = "★" * item['rarity']
        draw_text(screen, item['name'], 22, x+15, y+12, WHITE, align="left", glow=True)
        draw_text(screen, stars, 20, x+card_w-15, y+12, rc, align="right")
        
        # 显示卡牌类型标签和信息（右侧，避开图案）
        if "data" in item:
            type_label = {"base": "基础", "modifier": "参数", "synergy": "协同"}.get(item["type"], "")
            draw_text(screen, f"[{type_label}]", 15, x+100, y+52, rc, align="left")
            
            # 显示类别和流派
            card_data = item["data"]
            info_parts = []
            
            # 类别汉化
            if "category" in card_data:
                category_names = {
                    "attack": "攻击", "defense": "防御", 
                    "special": "特殊", "system": "系统",
                    "control": "控制", "summon": "召唤", "utility": "辅助"
                }
                cat_cn = category_names.get(card_data["category"], card_data["category"])
                info_parts.append(cat_cn)
            
            # 流派汉化
            if "archetype" in card_data:
                archetype_names = {
                    "barrage": "弹幕流", "sniper": "狙击流",
                    "control": "控制流", "summon": "召唤流"
                }
                arch_cn = archetype_names.get(card_data["archetype"], card_data["archetype"])
                info_parts.append(arch_cn)
            
            # 类型标签（参数卡）
            if "type" in card_data and item["type"] == "modifier":
                type_names = {"numeric": "数值", "trait": "特性"}
                type_cn = type_names.get(card_data["type"], card_data["type"])
                info_parts.append(type_cn)
            
            if info_parts:
                info_text = " · ".join(info_parts)
                draw_text(screen, info_text, 14, x+100, y+72, (180, 180, 200))
            
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

    back_btn = pygame.Rect(WIDTH//2 - 50, HEIGHT - 60, 100, 40)
    h = back_btn.collidepoint(mx, my)
    draw_cyber_rect(screen, back_btn, GRAY, fill=True)
    if h: draw_cyber_rect(screen, back_btn, WHITE, border_width=2, fill=False)
    draw_text(screen, "返回", 20, back_btn.centerx, back_btn.centery-10, WHITE)
    
    max_p = max(1, (len(items) + items_per_page - 1) // items_per_page)
    if max_p > 1:
        if gallery_page > 0:
            prev_btn = pygame.Rect(20, HEIGHT//2 - 25, 50, 50)
            draw_cyber_rect(screen, prev_btn, WHITE if prev_btn.collidepoint(mx,my) else GRAY, border_width=2, fill=False)
            draw_text(screen, "<", 30, prev_btn.centerx, prev_btn.centery-15, WHITE)
        if gallery_page < max_p - 1:
            next_btn = pygame.Rect(WIDTH-70, HEIGHT//2 - 25, 50, 50)
            draw_cyber_rect(screen, next_btn, WHITE if next_btn.collidepoint(mx,my) else GRAY, border_width=2, fill=False)
            draw_text(screen, ">", 30, next_btn.centerx, next_btn.centery-15, WHITE)
        draw_text(screen, f"页码 {gallery_page+1}/{max_p}", 18, WIDTH//2, HEIGHT - 100, GRAY)

def draw_select_plane_ui():
    draw_text(screen, "选择出击机体", 40, WIDTH//2, 50, CYAN, glow=True)
    mx, my = pygame.mouse.get_pos()

    left_arrow = pygame.Rect(100, HEIGHT//2 - 40, 60, 80)
    right_arrow = pygame.Rect(WIDTH-160, HEIGHT//2 - 40, 60, 80)
    draw_text(screen, "<", 60, left_arrow.centerx, left_arrow.y, WHITE if left_arrow.collidepoint(mx,my) else GRAY)
    draw_text(screen, ">", 60, right_arrow.centerx, right_arrow.y, WHITE if right_arrow.collidepoint(mx,my) else GRAY)

    pid = plane_keys[current_plane_idx]
    data = PLANES[pid]
    cx, cy = WIDTH//2, HEIGHT//2
    card_rect = pygame.Rect(cx - 200, cy - 200, 400, 400)
    draw_cyber_rect(screen, card_rect, (20,20,30), alpha=200, fill=True)
    draw_cyber_rect(screen, card_rect, data["color"], border_width=2, fill=False)

    # 获取当前装备的涂装预览
    visual = customization_manager.get_theme_visual(pid, PLANES.get(pid, {}).get('visual', None))
    preview = get_plane_surf(pid, visual)
    preview = pygame.transform.scale(preview, (180, 180))
    safe_blit(screen, preview, (cx - 90, cy - 200))

    draw_text(screen, data["name"], 36, cx, cy - 50, data["color"], glow=True)
    draw_text(screen, data["desc"], 18, cx, cy, GRAY)

    def draw_bar(label, val, max_v, y_off):
        draw_text(screen, label, 16, card_rect.x + 50, card_rect.y + y_off, WHITE, align="left")
        pygame.draw.rect(screen, (40,40,40), (card_rect.x + 120, card_rect.y + y_off + 5, 200, 8))
        fill = (val / max_v) * 200
        pygame.draw.rect(screen, data["color"], (card_rect.x + 120, card_rect.y + y_off + 5, fill, 8))
    draw_bar("速度", data["speed"], 10, 280)
    draw_bar("火力", data["damage"], 80, 310)
    draw_bar("装甲", data["hp"], 200, 340)

    start_btn = pygame.Rect(cx - 100, HEIGHT - 120, 200, 60)
    h = start_btn.collidepoint(mx, my)
    draw_cyber_rect(screen, start_btn, data["color"] if h else (50,50,50), fill=True)
    draw_text(screen, "确认出击", 24, start_btn.centerx, start_btn.centery-12, WHITE)

    # 调试信息：显示按钮矩形（仅用于测试）
    if h:
        draw_text(screen, "[按钮可点击]", 14, start_btn.centerx, start_btn.bottom + 10, CYAN)

    back_btn = pygame.Rect(50, HEIGHT - 80, 100, 40)
    h2 = back_btn.collidepoint(mx, my)
    draw_cyber_rect(screen, back_btn, GRAY, fill=True)
    if h2: draw_cyber_rect(screen, back_btn, WHITE, border_width=2, fill=False)
    draw_text(screen, "返回", 20, back_btn.centerx, back_btn.centery-10, WHITE)

def draw_boss_challenge_complete_ui():
    """Boss挑战模式完成界面，显示完成统计和奖励"""
    global boss_challenge_order, boss_challenge_current
    screen.fill((10, 10, 30))
    title_font = pygame.font.SysFont("SimHei", 56)
    font = pygame.font.SysFont("SimHei", 32)
    small_font = pygame.font.SysFont("SimHei", 24)
    
    title = title_font.render("🏆 挑战完成！🏆", True, GOLD)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
    
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
    """Boss挑战模式主界面，玩家可选择Boss顺序并开始挑战 - 赛博朋克风格，带动画效果和滚动"""
    global boss_challenge_selected, boss_challenge_order, boss_challenge_swap_timer, boss_challenge_pulse_timer, boss_challenge_scroll_offset
    
    # 动画计时器更新
    boss_challenge_pulse_timer = (boss_challenge_pulse_timer + 1) % 60
    
    # ====== 华丽背景效果 ======
    # 基础背景：深蓝色渐变
    screen.fill((10, 10, 25))
    for y in range(HEIGHT):
        alpha = int(20 * (y / HEIGHT))
        col = (10 + alpha//3, 10 + alpha//3, 25 + alpha)
        pygame.draw.line(screen, col, (0, y), (WIDTH, y))
    
    # 网格背景效果：远处的赛博朋克网格
    grid_size = 60
    grid_offset_x = int(boss_challenge_pulse_timer * 0.5) % grid_size
    grid_offset_y = int(boss_challenge_pulse_timer * 0.2) % grid_size
    for x in range(-grid_size, WIDTH + grid_size, grid_size):
        pygame.draw.line(screen, (20, 40, 60, 30), 
                        (x + grid_offset_x, 0), 
                        (x + grid_offset_x, HEIGHT), 1)
    for y in range(-grid_size, HEIGHT + grid_size, grid_size):
        pygame.draw.line(screen, (20, 40, 60, 30), 
                        (0, y + grid_offset_y), 
                        (WIDTH, y + grid_offset_y), 1)
    
    # 动态光束效果（从屏幕边缘投射）
    beam_angle = boss_challenge_pulse_timer / 60 * math.pi * 2
    for beam_idx in range(3):
        angle = beam_angle + (beam_idx * math.pi * 2 / 3)
        beam_start_x = WIDTH // 2 + int(500 * math.cos(angle))
        beam_start_y = HEIGHT // 2 + int(500 * math.sin(angle))
        beam_brightness = int(30 + 20 * math.sin(boss_challenge_pulse_timer / 60 * math.pi * 2))
        beam_color = (beam_brightness // 2, beam_brightness, beam_brightness)
        pygame.draw.line(screen, beam_color, 
                        (beam_start_x, beam_start_y), 
                        (WIDTH // 2, HEIGHT // 2), 1)
    
    # 粒子效果（随机发光星点）
    random.seed(boss_challenge_pulse_timer // 10)  # 使粒子位置稳定但变化
    particle_count = 40
    for i in range(particle_count):
        px = random.randint(0, WIDTH)
        py = random.randint(0, HEIGHT)
        # 脉冲大小
        pulse = math.sin(boss_challenge_pulse_timer / 60 * math.pi * 2 + i)
        particle_size = max(1, int(2 + pulse))
        particle_brightness = int(100 + 80 * pulse)
        particle_color = (particle_brightness // 3, particle_brightness // 2, particle_brightness)
        pygame.draw.circle(screen, particle_color, (px, py), particle_size)
    
    # 顶部和底部的光晕条
    top_glow_height = 80
    for y_offset in range(top_glow_height):
        glow_alpha = int(40 * (1 - y_offset / top_glow_height))
        glow_col = (glow_alpha // 3, glow_alpha, glow_alpha + 10)
        pygame.draw.line(screen, glow_col, (0, y_offset), (WIDTH, y_offset), 1)
    
    for y_offset in range(bottom_glow_height := 60):
        glow_alpha = int(40 * (1 - y_offset / bottom_glow_height))
        glow_col = (glow_alpha // 3, glow_alpha, glow_alpha + 10)
        pygame.draw.line(screen, glow_col, (0, HEIGHT - y_offset), (WIDTH, HEIGHT - y_offset), 1)
    
    title_font = pygame.font.SysFont("SimHei", 56)
    font = pygame.font.SysFont("SimHei", 28)
    small_font = pygame.font.SysFont("SimHei", 20)
    tiny_font = pygame.font.SysFont("SimHei", 16)
    
    # Boss列表
    boss_keys = list(BOSS_DB.keys())
    if not boss_challenge_order:
        boss_challenge_order = boss_keys[:]
    
    # 标题 + 光晕效果（脉冲）
    pulse_offset = int(5 * math.sin(boss_challenge_pulse_timer / 60 * math.pi * 2))
    title = title_font.render("⚔ Boss 挑战模式 ⚔", True, CYAN)
    title_glow = title_font.render("⚔ Boss 挑战模式 ⚔", True, (50, 180, 200))
    screen.blit(title_glow, (WIDTH//2 - title.get_width()//2 + 2 + pulse_offset//2, 45))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
    
    # 副标题
    subtitle = small_font.render(f"选择 {len(boss_challenge_order)} 个Boss的挑战顺序", True, (150, 150, 150))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 110))
    
    # 装饰线
    pygame.draw.line(screen, CYAN, (80, 155), (WIDTH-80, 155), 2)
    
    # 左列：Boss列表（卡片样式，可滚动）
    card_width = 380
    card_height = 50
    start_y = 180
    gap = 12
    max_visible = 8  # 最多显示8个Boss
    visible_height = max_visible * (card_height + gap)
    
    # 自动调整滚动偏移，确保选中项可见
    if boss_challenge_selected < boss_challenge_scroll_offset:
        boss_challenge_scroll_offset = boss_challenge_selected
    elif boss_challenge_selected >= boss_challenge_scroll_offset + max_visible:
        boss_challenge_scroll_offset = boss_challenge_selected - max_visible + 1
    
    # 绘制列表容器（带边框）
    list_container = pygame.Rect(60, start_y, card_width, visible_height + 10)
    pygame.draw.rect(screen, (20, 20, 35), list_container, 1)
    
    # 绘制可见的Boss卡片
    for i in range(boss_challenge_scroll_offset, min(boss_challenge_scroll_offset + max_visible, len(boss_challenge_order))):
        bkey = boss_challenge_order[i]
        boss_name = BOSS_DB[bkey]["name"]
        boss_color = BOSS_DB[bkey]["color"]
        boss_stats = BOSS_DB[bkey].get("stats", [])
        
        # 计算显示位置（相对于滚动）
        display_idx = i - boss_challenge_scroll_offset
        y_pos = start_y + 5 + display_idx * (card_height + gap)
        
        # 换位动画：如果这是被交换的项，加上偏移
        anim_offset = 0
        if boss_challenge_swap_timer > 0:
            anim_progress = 1 - (boss_challenge_swap_timer / 15)  # 15帧动画
            if anim_progress < 0:
                anim_progress = 0
            boss_challenge_swap_timer -= 1
        
        card_rect = pygame.Rect(60, y_pos + anim_offset, card_width, card_height)
        
        # 卡片背景
        if i == boss_challenge_selected:
            # 选中高亮：发光边框
            pygame.draw.rect(screen, boss_color, card_rect, 3)
            bg_color = (30, 30, 50)
            # 脉冲光晕
            pulse = int(2 * math.sin(boss_challenge_pulse_timer / 60 * math.pi * 2))
            pygame.draw.rect(screen, (boss_color[0]//3, boss_color[1]//3, boss_color[2]//3), card_rect, max(1, pulse + 1))
            # 左侧指示条（脉冲）
            indicator_width = max(2, int(3 + 2 * math.sin(boss_challenge_pulse_timer / 60 * math.pi * 2)))
            pygame.draw.rect(screen, boss_color, (card_rect.x - 5, card_rect.y, indicator_width, card_rect.height))
        else:
            pygame.draw.rect(screen, (40, 40, 60), card_rect, 1)
            bg_color = (20, 20, 35)
        
        pygame.draw.rect(screen, bg_color, card_rect, 0)
        
        # 序号 + Boss名称
        num_text = font.render(f"{i+1}.", True, CYAN)
        name_text = font.render(f"{boss_name}", True, boss_color)
        screen.blit(num_text, (card_rect.x + 12, card_rect.y + 10))
        screen.blit(name_text, (card_rect.x + 55, card_rect.y + 10))
        
        # Boss强度指示（星形）
        if boss_stats:
            avg_stat = sum([s[1] for s in boss_stats]) / len(boss_stats)
            stars = min(5, int(avg_stat/20))
            star_text = small_font.render(f"{'★' * stars}", True, (255, 200, 0))
            screen.blit(star_text, (card_rect.right - 80, card_rect.y + 12))
    
    # 滚动指示器
    if len(boss_challenge_order) > max_visible:
        scroll_bar_height = int((max_visible / len(boss_challenge_order)) * visible_height)
        scroll_pos = int((boss_challenge_scroll_offset / len(boss_challenge_order)) * visible_height)
        pygame.draw.rect(screen, (80, 80, 100), (card_width + 70, start_y + scroll_pos, 4, scroll_bar_height))
    
    # 右列：选中Boss详细信息卡片
    if boss_challenge_selected < len(boss_challenge_order):
        sel_bkey = boss_challenge_order[boss_challenge_selected]
        sel_boss = BOSS_DB[sel_bkey]
        
        # 信息卡片
        info_card_x = 480
        info_card_y = start_y
        info_card_width = 260
        info_card_height = visible_height + 10
        info_rect = pygame.Rect(info_card_x, info_card_y, info_card_width, info_card_height)
        
        # 卡片框架（脉冲效果）
        pulse_width = max(2, int(2 + 1 * math.sin(boss_challenge_pulse_timer / 60 * math.pi * 2)))
        pygame.draw.rect(screen, sel_boss["color"], info_rect, pulse_width)
        pygame.draw.rect(screen, (15, 15, 30), info_rect, 0)
        
        # Boss名称区域
        pygame.draw.line(screen, sel_boss["color"], (info_card_x + 10, info_card_y + 40), 
                        (info_card_x + info_card_width - 10, info_card_y + 40), 1)
        
        name_surf = font.render(sel_boss["name"], True, sel_boss["color"])
        screen.blit(name_surf, (info_card_x + 15, info_card_y + 8))
        
        # 描述文本
        desc = sel_boss.get("desc", "")
        desc_lines = [desc[i:i+13] for i in range(0, len(desc), 13)]  # 按长度换行
        desc_y = info_card_y + 55
        for line in desc_lines[:3]:
            if desc_y - info_card_y > 60:  # 最多显示3行
                break
            desc_surf = tiny_font.render(line, True, (200, 200, 200))
            screen.blit(desc_surf, (info_card_x + 12, desc_y))
            desc_y += 22
        
        # 属性显示
        stats = sel_boss.get("stats", [])
        attr_y = info_card_y + 130
        pygame.draw.line(screen, (80, 80, 100), (info_card_x + 10, attr_y - 5), 
                        (info_card_x + info_card_width - 10, attr_y - 5), 1)
        
        attr_label_y = attr_y
        for stat_name, stat_val in stats:
            # 属性标签
            label = tiny_font.render(stat_name, True, (180, 180, 200))
            screen.blit(label, (info_card_x + 12, attr_label_y))
            
            # 属性条
            bar_width = 160
            bar_height = 6
            bar_x = info_card_x + 90
            bar_y = attr_label_y + 2
            pygame.draw.rect(screen, (40, 40, 60), (bar_x, bar_y, bar_width, bar_height))
            
            # 填充
            fill_width = int(bar_width * (stat_val / 120))
            pygame.draw.rect(screen, sel_boss["color"], (bar_x, bar_y, fill_width, bar_height))
            
            # 数值
            val_text = tiny_font.render(str(stat_val), True, (255, 200, 100))
            screen.blit(val_text, (bar_x + bar_width + 8, attr_label_y))
            
            attr_label_y += 28
        
        # 阶段信息
        phases = sel_boss.get("phases", [])
        phase_y = attr_label_y + 15
        if phase_y - info_card_y < info_card_height - 30:  # 确保不超出卡片
            pygame.draw.line(screen, (80, 80, 100), (info_card_x + 10, phase_y - 5), 
                            (info_card_x + info_card_width - 10, phase_y - 5), 1)
            phase_label = tiny_font.render(f"战斗阶段: {len(phases)}", True, (180, 200, 255))
            screen.blit(phase_label, (info_card_x + 12, phase_y))
    
    # 装饰线
    pygame.draw.line(screen, CYAN, (80, start_y + visible_height + 30), 
                     (WIDTH-80, start_y + visible_height + 30), 2)
    
    # 操作提示面板
    tip_y = start_y + visible_height + 50
    pygame.draw.rect(screen, (20, 20, 40), (50, tip_y, WIDTH-100, 100), 1)
    pygame.draw.rect(screen, (10, 10, 20), (50, tip_y, WIDTH-100, 100), 0)
    
    tips = [
        "↑ ↓  选择序号    |    ← →  交换位置    |    Enter  开始挑战",
        "Esc 返回主菜单"
    ]
    
    for idx, tip in enumerate(tips):
        tip_text = small_font.render(tip, True, (180, 180, 200))
        screen.blit(tip_text, (70, tip_y + 15 + idx*30))

def draw_achievement_notifications():
    """绘制成就通知弹窗 - 从右侧弹出停留后弹回"""
    global achievement_notifications
    
    # 更新和绘制所有通知
    for i, (achievement, timer) in enumerate(achievement_notifications[:3]):  # 最多显示3个
        y = 80 + i * 100
        total_time = 180.0  # 3秒
        
        # 分三个阶段：弹入(60帧) + 停留(60帧) + 弹回(60帧)
        if timer > 120:  # 弹入阶段 (60-180帧)
            phase_progress = (total_time - timer) / 60.0  # 0 -> 1
            slide_x = WIDTH + 20 - int(380 * phase_progress)  # 从屏幕外滑入
            alpha = int(255 * min(1, phase_progress * 2))
        elif timer > 60:  # 停留阶段 (60-120帧)
            slide_x = WIDTH - 350
            alpha = 255
        else:  # 弹回阶段 (0-60帧)
            phase_progress = (60 - timer) / 60.0  # 0 -> 1
            slide_x = WIDTH - 350 + int(380 * phase_progress)  # 滑出屏幕
            alpha = int(255 * max(0, 1 - phase_progress * 2))
        
        # 绘制通知背景
        surface = pygame.Surface((360, 85), pygame.SRCALPHA)
        
        # 背景框 - 赛博朋克风格
        pygame.draw.rect(surface, (15, 30, 50, 220), (0, 0, 360, 85), border_radius=4)
        pygame.draw.rect(surface, (0, 255, 200, alpha), (0, 0, 360, 85), 2, border_radius=4)
        
        # 左侧装饰条 - 强调成就解锁
        pygame.draw.rect(surface, (0, 255, 200, alpha), (0, 0, 4, 85))
        
        # 绘制到屏幕
        screen.blit(surface, (slide_x, y))
        
        # 绘制文本内容
        text_x = slide_x + 20
        text_y = y + 10
        
        # 标题（无星装饰）- 向右移动30像素
        draw_text(screen, "成就解锁", 16, text_x + 30, text_y, LIME)
        
        # 成就名称（加粗效果通过多次绘制）
        draw_text(screen, achievement.name, 20, text_x, text_y + 28, WHITE, align="left")
        
        # 奖励分数
        draw_text(screen, f"+{achievement.reward} 分", 16, slide_x + 340, text_y + 28, YELLOW, align="right")
        
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
    """绘制成就菜单"""
    global player, achievement_page
    
    draw_text(screen, "成就", 40, WIDTH//2, 30, LIME, glow=True)
    
    # 获取成就管理器
    achievement_mgr = None
    if player and hasattr(player, 'achievement_manager'):
        achievement_mgr = player.achievement_manager
    
    if not achievement_mgr:
        draw_text(screen, "尚未开始游戏", 24, WIDTH//2, HEIGHT//2, GRAY)
    else:
        unlocked_count = sum(1 for a in achievement_mgr.achievements.values() if a.unlocked)
        total_count = len(achievement_mgr.achievements)
        draw_text(screen, f"已解锁: {unlocked_count}/{total_count}", 22, WIDTH//2, 80, CYAN)
        draw_text(screen, f"总奖励分数: {achievement_mgr.get_total_reward()}", 22, WIDTH//2, 110, YELLOW)
        
        # 成就列表
        start_y = 160
        ach_list = list(achievement_mgr.achievements.values())
        page_size = 6
        max_page = (len(ach_list) + page_size - 1) // page_size
        current_page = achievement_page % max_page if max_page > 0 else 0
        
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, len(ach_list))
        
        for i in range(start_idx, end_idx):
            ach = ach_list[i]
            y = start_y + (i - start_idx) * 80
            
            # 成就框
            rect = pygame.Rect(100, y, WIDTH - 200, 70)
            bg_color = (40, 50, 60) if ach.unlocked else (20, 20, 25)
            draw_cyber_rect(screen, rect, bg_color, fill=True)
            border_color = LIME if ach.unlocked else GRAY
            draw_cyber_rect(screen, rect, border_color, border_width=2, fill=False)
            
            # 图标
            icon_color = LIME if ach.unlocked else GRAY
            draw_text(screen, ach.icon_char, 28, 130, y + 20, icon_color)
            
            # 成就名称
            text_color = WHITE if ach.unlocked else (100, 100, 100)
            draw_text(screen, ach.name, 20, 200, y + 10, text_color, align="left")
            
            # 描述
            draw_text(screen, ach.description, 16, 200, y + 35, GRAY, align="left")
            
            # 奖励
            draw_text(screen, f"+{ach.reward} 分", 18, WIDTH - 150, y + 20, ORANGE if ach.unlocked else GRAY)
        
        # 分页显示
        if max_page > 1:
            draw_text(screen, f"第 {current_page + 1}/{max_page} 页", 18, WIDTH//2, HEIGHT - 120, GRAY)
            
            # 前后按钮
            if current_page > 0:
                prev_btn = pygame.Rect(WIDTH//2 - 200, HEIGHT - 100, 80, 40)
                h = prev_btn.collidepoint(pygame.mouse.get_pos())
                draw_cyber_rect(screen, prev_btn, CYAN if h else GRAY, fill=True)
                draw_text(screen, "上一页", 18, prev_btn.centerx, prev_btn.centery-10, WHITE if h else GRAY)
            
            if current_page < max_page - 1:
                next_btn = pygame.Rect(WIDTH//2 + 120, HEIGHT - 100, 80, 40)
                h = next_btn.collidepoint(pygame.mouse.get_pos())
                draw_cyber_rect(screen, next_btn, CYAN if h else GRAY, fill=True)
                draw_text(screen, "下一页", 18, next_btn.centerx, next_btn.centery-10, WHITE if h else GRAY)
    
    # 返回按钮
    back_btn = pygame.Rect(WIDTH//2 - 60, HEIGHT - 50, 120, 40)
    h = back_btn.collidepoint(pygame.mouse.get_pos())
    draw_cyber_rect(screen, back_btn, GRAY, fill=True)
    if h: draw_cyber_rect(screen, back_btn, WHITE, border_width=2, fill=False)
    draw_text(screen, "返回", 20, back_btn.centerx, back_btn.centery-10, WHITE)

def draw_leaderboard_ui():
    draw_text(screen, "排行榜", 40, WIDTH//2, 50, GOLD, glow=True)
    start_y = 150
    for i, entry in enumerate(leaderboard_data[:5]):
        y = start_y + i * 60
        rect = pygame.Rect(WIDTH//2 - 300, y, 600, 50)
        draw_cyber_rect(screen, rect, (30,30,40), fill=True)  
        color = GOLD if i == 0 else WHITE
        draw_text(screen, f"NO.{i+1}", 20, rect.x + 50, y + 15, color)
        draw_text(screen, entry.get("name", "Unknown"), 20, rect.centerx, y + 15, WHITE)
        draw_text(screen, str(entry.get("score", 0)), 20, rect.right - 50, y + 15, ORANGE)
    if not leaderboard_data: draw_text(screen, "暂无数据", 30, WIDTH//2, HEIGHT//2, GRAY)
    
    back_btn = pygame.Rect(WIDTH//2 - 60, HEIGHT - 100, 120, 50)
    h = back_btn.collidepoint(pygame.mouse.get_pos())
    draw_cyber_rect(screen, back_btn, GRAY, fill=True)
    if h: draw_cyber_rect(screen, back_btn, WHITE, border_width=2, fill=False)
    draw_text(screen, "返回", 24, back_btn.centerx, back_btn.centery-12, WHITE)

def handle_plane_customization_click(mx, my):
    """处理机体涂装点击事件"""
    global customization_selected_plane, customization_msg, customization_msg_timer, game_state
    
    print(f"[DEBUG] handle_plane_customization_click called: mx={mx}, my={my}, tab={customization_tab}, plane={customization_selected_plane}")
    
    # 返回按钮
    back_btn = pygame.Rect(WIDTH//2 - 60, HEIGHT - 80, 120, 50)
    if back_btn.collidepoint(mx, my):
        sound_mgr.play("select")
        customization_manager.save_data()
        game_state = "menu"
        return
    
    # 选择飞机
    plane_list_area = pygame.Rect(30, 100, 280, HEIGHT - 180)
    list_content_rect = pygame.Rect(plane_list_area.x, plane_list_area.y + 40, plane_list_area.width, plane_list_area.height - 40)
    plane_start_y = list_content_rect.y + 5 - customization_plane_scroll_y
    
    if list_content_rect.collidepoint(mx, my):
        for i, plane_id in enumerate(plane_keys):
            rect = pygame.Rect(40, plane_start_y + i * 45, 260, 40)
            if rect.collidepoint(mx, my):
                sound_mgr.play("select")
                customization_selected_plane = plane_id
                return
    
    # 涂装按钮点击
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
        
        theme_y_start = 180
        theme_list_area = pygame.Rect(330, 100, 600, HEIGHT - 180)
        list_view_rect = pygame.Rect(theme_list_area.x, theme_y_start, theme_list_area.width, theme_list_area.height - (theme_y_start - theme_list_area.y))
        
        for i, (theme_id, theme, is_bullet) in enumerate(filtered_themes):
            card_rect = pygame.Rect(350, theme_y_start + i * 100 - customization_scroll_y, 560, 90)
            
            if card_rect.bottom < list_view_rect.top or card_rect.top > list_view_rect.bottom:
                continue
            
            # 根据涂装类型检查解锁状态
            if is_bullet:
                is_unlocked = customization_manager.unlocked_bullet_themes.get(theme_id, False)
            else:
                is_unlocked = customization_manager.unlocked_themes.get(theme_id, False)
            btn_x = card_rect.right - 120
            btn_y = card_rect.y + 25
            btn_rect = pygame.Rect(btn_x, btn_y, 100, 40)
            
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
    
    # 槽位选择
    list_content_rect = pygame.Rect(30, 140, 280, HEIGHT - 220)
    wingman_start_y = list_content_rect.y + 5
    
    for i in range(4):
        rect = pygame.Rect(40, wingman_start_y + i * 60, 260, 55)
        if rect.collidepoint(mx, my):
            customization_selected_wingman = i
            return
    
    # 机体筛选按钮点击
    theme_list_area = pygame.Rect(330, 100, 600, HEIGHT - 180)
    filter_y = 140
    filter_btn_w = 55
    filter_btn_h = 25
    filter_start_x = theme_list_area.x + 5
    
    # "全部"按钮
    all_btn = pygame.Rect(filter_start_x, filter_y, filter_btn_w, filter_btn_h)
    if all_btn.collidepoint(mx, my):
        wingman_theme_filter = None
        customization_scroll_y = 0
        return
    
    # 第一行机体筛选按钮
    plane_keys_list = list(PLANES.keys())
    for pi, plane_id in enumerate(plane_keys_list[:10]):
        btn_x = filter_start_x + (pi + 1) * (filter_btn_w + 3)
        if btn_x + filter_btn_w > theme_list_area.right - 5:
            break
        plane_btn = pygame.Rect(btn_x, filter_y, filter_btn_w, filter_btn_h)
        if plane_btn.collidepoint(mx, my):
            wingman_theme_filter = plane_id
            customization_scroll_y = 0
            return
    
    # 第二行机体筛选按钮
    filter_y2 = filter_y + filter_btn_h + 3
    for pi, plane_id in enumerate(plane_keys_list[10:]):
        btn_x = filter_start_x + pi * (filter_btn_w + 3)
        if btn_x + filter_btn_w > theme_list_area.right - 5:
            break
        plane_btn = pygame.Rect(btn_x, filter_y2, filter_btn_w, filter_btn_h)
        if plane_btn.collidepoint(mx, my):
            wingman_theme_filter = plane_id
            customization_scroll_y = 0
            return
    
    # 涂装卡片点击
    theme_y_start = 200
    
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
        card_rect = pygame.Rect(350, theme_y_start + i * 100 - customization_scroll_y, 560, 90)
        
        if not card_rect.collidepoint(mx, my):
            continue
        
        is_unlocked = customization_manager.unlocked_themes.get(theme_id, False)
        current_equipped = customization_manager.equipped_wingman_themes.get(f"slot_{customization_selected_wingman}", "default")
        is_equipped = (current_equipped == theme_id)
        
        # 按钮区域
        btn_x = card_rect.right - 120
        btn_y = card_rect.y + 25
        btn_rect = pygame.Rect(btn_x, btn_y, 100, 40)
        
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
    """绘制涂装自定义界面"""
    global customization_mode, game_state
    
    mx, my = pygame.mouse.get_pos()
    
    # 左上角返回按钮
    back_btn = pygame.Rect(30, 30, 100, 40)
    hb = back_btn.collidepoint(mx, my)
    draw_cyber_rect(screen, back_btn, GRAY, fill=True)
    if hb: 
        draw_cyber_rect(screen, back_btn, WHITE, border_width=2, fill=False)
    draw_text(screen, "返回", 20, back_btn.centerx, back_btn.centery - 8, WHITE)
    
    # 处理返回按钮点击
    if hb and pygame.mouse.get_pressed()[0]:
        game_state = "menu"
        pygame.mouse.set_visible(True)
        return
    
    # 模式切换按钮（居中）
    mode_btn_y = 30
    plane_btn = pygame.Rect(WIDTH // 2 - 120, mode_btn_y, 100, 40)
    wingman_btn = pygame.Rect(WIDTH // 2 + 20, mode_btn_y, 100, 40)
    
    plane_active = (customization_mode == "plane")
    wingman_active = (customization_mode == "wingman")
    
    draw_cyber_rect(screen, plane_btn, (0, 100, 100) if plane_active else (40, 40, 50), fill=True)
    if plane_active:
        draw_cyber_rect(screen, plane_btn, CYAN, border_width=2, fill=False)
    draw_text(screen, "机体涂装", 18, plane_btn.centerx, plane_btn.centery - 8, CYAN if plane_active else WHITE)
    
    draw_cyber_rect(screen, wingman_btn, (0, 100, 100) if wingman_active else (40, 40, 50), fill=True)
    if wingman_active:
        draw_cyber_rect(screen, wingman_btn, CYAN, border_width=2, fill=False)
    draw_text(screen, "僚机涂装", 18, wingman_btn.centerx, wingman_btn.centery - 8, CYAN if wingman_active else WHITE)
    
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
    """绘制机体涂装界面"""
    global customization_selected_plane, customization_msg_timer, customization_tab, customization_scroll_y, customization_plane_scroll_y
    
    mx, my = pygame.mouse.get_pos()
    
    # 右上角显示核心和进度
    currency_text = f"核心: {arsenal_save_data['currencies']['cores']}"
    draw_text(screen, currency_text, 20, WIDTH - 200, 30, GOLD, align="left")
    unlocked_count = customization_manager.get_unlocked_count()
    total_count = customization_manager.get_total_count()
    progress_text = f"已解锁: {unlocked_count}/{total_count}"
    draw_text(screen, progress_text, 18, WIDTH - 200, 60, CYAN, align="left")
    
    # 左侧：飞机列表
    plane_list_area = pygame.Rect(30, 100, 280, HEIGHT - 180)
    draw_cyber_rect(screen, plane_list_area, (20, 20, 30), alpha=220, fill=True)
    draw_text(screen, "选择机体", 22, plane_list_area.centerx, 110, CYAN)
    
    # 列表内容区域（排除标题）
    list_content_rect = pygame.Rect(plane_list_area.x, plane_list_area.y + 40, plane_list_area.width, plane_list_area.height - 40)
    screen.set_clip(list_content_rect)
    
    plane_start_y = list_content_rect.y + 5 - customization_plane_scroll_y
    for i, plane_id in enumerate(plane_keys):
        plane_data = PLANES[plane_id]
        rect = pygame.Rect(40, plane_start_y + i * 45, 260, 40)
        
        # 简单的可见性剔除
        if rect.bottom < list_content_rect.top or rect.top > list_content_rect.bottom:
            continue
            
        equipped_theme = customization_manager.get_equipped_theme(plane_id)
        is_selected = (customization_selected_plane == plane_id)
        h = rect.collidepoint(mx, my) or is_selected
        bg_color = (plane_data["color"][0]//3, plane_data["color"][1]//3, plane_data["color"][2]//3) if h else (30, 30, 40)
        draw_cyber_rect(screen, rect, bg_color, fill=True)
        if is_selected: draw_cyber_rect(screen, rect, CYAN, border_width=2, fill=False)
        
        # 简单绘制飞机图标（使用当前装备的涂装）
        plane_visual = customization_manager.get_theme_visual(plane_id, PLANES[plane_id].get('visual', None))
        # 使用静态缓存模式
        icon = get_plane_surf(plane_id, plane_visual, static=True)
        icon = pygame.transform.scale(icon, (30, 30))
        safe_blit(screen, icon, (rect.x + 5, rect.y + 5))
        
        draw_text(screen, plane_data["name"], 16, rect.x + 130, rect.y + 8, WHITE, align="center")
        if equipped_theme != "default":
            # 容错处理：如果主题不存在，使用默认主题
            if equipped_theme in PAINT_THEMES:
                theme_name = PAINT_THEMES[equipped_theme]["name"]
                draw_text(screen, f"[{theme_name}]", 12, rect.x + 130, rect.y + 24, plane_data["color"], align="center")
            else:
                log_info(f"Theme {equipped_theme} not found for {plane_id}, resetting to default")
                customization_manager.equip_theme(plane_id, "default")
            
    screen.set_clip(None)

    # 右侧：涂装列表
    theme_list_area = pygame.Rect(330, 100, 600, HEIGHT - 180)
    draw_cyber_rect(screen, theme_list_area, (20, 20, 30), alpha=220, fill=True)
    
    if customization_selected_plane:
        plane_data = PLANES[customization_selected_plane]
        draw_text(screen, f"{plane_data['name']} - 涂装方案", 22, theme_list_area.centerx, 110, CYAN)
        
        # --- 分类标签页 ---
        tabs = ["全部", "普通", "稀有", "史诗", "传说", "专属", "子弹"]
        categories = [None, "common", "rare", "epic", "legendary", "exclusive", "bullet"]
        tab_w = 70
        tab_h = 30
        start_x = theme_list_area.x + 10
        tab_y = 140
        
        for i, tab_name in enumerate(tabs):
            tab_rect = pygame.Rect(start_x + i * (tab_w + 5), tab_y, tab_w, tab_h)
            is_active = (customization_tab == i)
            
            # 处理点击
            if tab_rect.collidepoint(mx, my) and pygame.mouse.get_pressed()[0]:
                if customization_tab != i:
                    customization_tab = i
                    customization_scroll_y = 0 # 切换标签重置滚动
            
            color = CYAN if is_active else GRAY
            draw_cyber_rect(screen, tab_rect, (40, 40, 50), fill=True)
            if is_active:
                draw_cyber_rect(screen, tab_rect, CYAN, border_width=2, fill=False)
            draw_text(screen, tab_name, 16, tab_rect.centerx, tab_rect.centery - 8, color)

        # --- 筛选涂装 ---
        filtered_themes = []
        
        # 判断是否为子弹涂装标签
        if customization_tab == 6:  # 子弹标签
            # 显示子弹涂装
            for tid, theme in BULLET_THEMES.items():
                # 过滤掉其他飞机的专属子弹涂装
                exclusive_plane = theme.get("exclusive_plane")
                if exclusive_plane and exclusive_plane != customization_selected_plane:
                    continue
                filtered_themes.append((tid, theme, True))  # True表示是子弹涂装
        else:
            # 显示机体涂装
            for tid, theme in PAINT_THEMES.items():
                # 过滤掉其他飞机的专属涂装
                exclusive_plane = theme.get("exclusive_plane")
                if exclusive_plane and exclusive_plane != customization_selected_plane:
                    continue

                if customization_tab == 0:
                    filtered_themes.append((tid, theme, False))  # False表示是机体涂装
                else:
                    target_cat = categories[customization_tab]
                    if theme.get("category") == target_cat:
                        filtered_themes.append((tid, theme, False))
        
        theme_y_start = 180
        
        # 列表裁剪区域
        list_view_rect = pygame.Rect(theme_list_area.x, theme_y_start, theme_list_area.width, theme_list_area.height - (theme_y_start - theme_list_area.y))
        screen.set_clip(list_view_rect)
        
        for i, (theme_id, theme, is_bullet) in enumerate(filtered_themes):
            card_rect = pygame.Rect(350, theme_y_start + i * 100 - customization_scroll_y, 560, 90)
            
            # 跳过不可见的卡片
            if card_rect.bottom < list_view_rect.top or card_rect.top > list_view_rect.bottom:
                continue
            
            # 根据涂装类型检查解锁状态
            if is_bullet:
                is_unlocked = customization_manager.unlocked_bullet_themes.get(theme_id, False)
            else:
                is_unlocked = customization_manager.unlocked_themes.get(theme_id, False)
            is_equipped = customization_manager.get_equipped_theme(customization_selected_plane, bullet=is_bullet) == theme_id
            
            # 调试：每隔一段时间打印一次装备状态
            if theme_id == "crystalfall_void":
                current_equipped = customization_manager.get_equipped_theme(customization_selected_plane, bullet=is_bullet)
                if pygame.time.get_ticks() % 3000 < 50:  # 每3秒打印一次
                    print(f"[DEBUG-UI] crystalfall_void: current_equipped={current_equipped}, is_equipped={is_equipped}")
            
            h = card_rect.collidepoint(mx, my)
            
            # 背景颜色
            if is_equipped:
                bg_color = (0, 100, 100)
            elif is_unlocked:
                bg_color = (40, 50, 40) if h else (30, 35, 30)
            else:
                bg_color = (50, 30, 30) if h else (30, 20, 20)
            
            draw_cyber_rect(screen, card_rect, bg_color, fill=True)
            
            # 品质颜色定义 (高对比度)
            cat = theme.get("category", "default")
            quality_colors = {
                "default": (150, 150, 150),
                "common": (220, 220, 220),
                "rare": (100, 150, 255),
                "epic": (200, 100, 255),
                "legendary": (255, 215, 0),
                "exclusive": (255, 50, 150)
            }
            q_color = quality_colors.get(cat, GRAY)
            
            # 边框
            if is_equipped:
                draw_cyber_rect(screen, card_rect, CYAN, border_width=3, fill=False)
                # 装备状态下额外显示品质色内框
                pygame.draw.rect(screen, q_color, card_rect.inflate(-8, -8), 1)
            elif h:
                draw_cyber_rect(screen, card_rect, WHITE, border_width=2, fill=False)
            else:
                draw_cyber_rect(screen, card_rect, q_color, border_width=1, fill=False)
            
            # 预览图（简化版本，不使用缓存）
            if is_bullet:
                # 子弹涂装预览
                draw_bullet_preview(screen, theme, card_rect.x + 10, card_rect.y + 15, 60, plane_id=customization_selected_plane)
            else:
                # 机体涂装预览
                if theme_id == "default":
                    visual = plane_data.get('visual', None)
                else:
                    visual = customization_manager.get_theme_visual(customization_selected_plane, plane_data.get('visual', None), preview_theme_id=theme_id)
                
                # 使用静态缓存模式
                preview = get_plane_surf(customization_selected_plane, visual, static=True)
                preview = pygame.transform.scale(preview, (60, 60))
                safe_blit(screen, preview, (card_rect.x + 10, card_rect.y + 15))
            
            # 信息文字 - 名称使用品质颜色
            info_x = card_rect.x + 85
            draw_text(screen, theme["name"], 18, info_x, card_rect.y + 10, q_color, align="left")
            draw_text(screen, theme["desc"], 14, info_x, card_rect.y + 32, GRAY, align="left")
            
            # 显示专属信息或尾迹信息
            exclusive_plane = theme.get("exclusive_plane")
            if exclusive_plane:
                p_name = PLANES.get(exclusive_plane, {}).get("name", exclusive_plane)
                draw_text(screen, f"专属机体: {p_name}", 12, info_x, card_rect.y + 52, MAGENTA, align="left")
            else:
                trail_style = theme.get("trail_style", "normal")
                draw_text(screen, f"尾迹: {trail_style}", 12, info_x, card_rect.y + 52, CYAN, align="left")
            
            # 按钮
            btn_x = card_rect.right - 120
            btn_y = card_rect.y + 25
            btn_rect = pygame.Rect(btn_x, btn_y, 100, 40)
            
            is_compatible = True
            if exclusive_plane and exclusive_plane != customization_selected_plane:
                is_compatible = False
            
            if not is_compatible:
                draw_text(screen, "机型不符", 16, btn_rect.centerx, btn_rect.centery - 8, RED)
            elif is_equipped:
                draw_text(screen, "已装备", 16, btn_rect.centerx, btn_rect.centery - 8, GREEN)
            elif is_unlocked:
                btn_h = btn_rect.collidepoint(mx, my)
                draw_cyber_rect(screen, btn_rect, CYAN if btn_h else (0, 100, 100), fill=True)
                draw_text(screen, "装备", 16, btn_rect.centerx, btn_rect.centery - 8, WHITE)
            else:
                cost = theme.get("cost", 0)
                can_afford = arsenal_save_data['currencies']['cores'] >= cost
                btn_h = btn_rect.collidepoint(mx, my) and can_afford
                btn_color = GOLD if (btn_h and can_afford) else (GRAY if not can_afford else ORANGE)
                draw_cyber_rect(screen, btn_rect, btn_color, fill=True)
                draw_text(screen, f"解锁 {cost}", 14, btn_rect.centerx, btn_rect.centery - 8, WHITE if can_afford else GRAY)
                
                if "requirement" in theme:
                    req_text = theme["requirement"]
                    draw_text(screen, req_text, 10, info_x, card_rect.y + 70, YELLOW, align="left")
        
        screen.set_clip(None)
        
    else:
        draw_text(screen, "← 请先选择一架飞机", 24, theme_list_area.centerx, theme_list_area.centery, GRAY)
    # 消息提示
    if customization_msg_timer > 0:
        msg_y = HEIGHT - 150
        msg_rect = pygame.Rect(WIDTH//2 - 200, msg_y, 400, 40)
        draw_cyber_rect(screen, msg_rect, (50, 50, 50), alpha=200, fill=True)
        draw_text(screen, customization_msg, 18, msg_rect.centerx, msg_rect.centery - 8, CYAN)
        customization_msg_timer -= 1
    
    # 大预览区
    if customization_selected_plane:
        preview_area = pygame.Rect(WIDTH - 350, HEIGHT - 250, 320, 180)
        draw_cyber_rect(screen, preview_area, (20, 20, 30), alpha=240, fill=True)
        
        if customization_tab == 6:  # 子弹标签
            draw_text(screen, "子弹预览", 18, preview_area.centerx, preview_area.y + 10, MAGENTA)
            
            # 获取当前装备的子弹涂装
            equipped_theme = customization_manager.get_equipped_theme(customization_selected_plane, bullet=True)
            theme = BULLET_THEMES.get(equipped_theme, BULLET_THEMES.get("default"))
            
            # 绘制大尺寸子弹预览
            preview_size = 120
            preview_x = preview_area.centerx - preview_size // 2
            preview_y = preview_area.y + 50
            draw_bullet_preview(screen, theme, preview_x, preview_y, preview_size, plane_id=customization_selected_plane)
            
            # 显示涂装名称
            draw_text(screen, theme.get("name", "标准子弹"), 16, preview_area.centerx, preview_area.bottom - 30, CYAN)
        else:
            draw_text(screen, "涂装预览", 18, preview_area.centerx, preview_area.y + 10, MAGENTA)
            
            # 获取当前装备的机体涂装预览
            equipped_theme = customization_manager.get_equipped_theme(customization_selected_plane)
            visual = customization_manager.get_theme_visual(customization_selected_plane, PLANES[customization_selected_plane].get('visual', None))
            big_preview = get_plane_surf(customization_selected_plane, visual)
            big_preview = pygame.transform.scale(big_preview, (120, 120))
            safe_blit(screen, big_preview, (preview_area.centerx - 60, preview_area.y + 40))
    

def draw_wingman_customization_ui():
    """绘制僚机涂装界面（结构与机体涂装界面完全相同）"""
    global customization_selected_wingman, customization_msg_timer, customization_tab, customization_scroll_y, customization_plane_scroll_y
    
    mx, my = pygame.mouse.get_pos()
    
    # 右上角显示核心
    currency_text = f"核心: {arsenal_save_data['currencies']['cores']}"
    draw_text(screen, currency_text, 20, WIDTH - 200, 30, GOLD, align="left")
    
    # 左侧：僚机槽位列表（4个槽位）
    wingman_list_area = pygame.Rect(30, 100, 280, HEIGHT - 180)
    draw_cyber_rect(screen, wingman_list_area, (20, 20, 30), alpha=220, fill=True)
    draw_text(screen, "选择僚机", 22, wingman_list_area.centerx, 110, CYAN)
    
    # 列表内容区域
    list_content_rect = pygame.Rect(wingman_list_area.x, wingman_list_area.y + 40, wingman_list_area.width, wingman_list_area.height - 40)
    screen.set_clip(list_content_rect)
    
    wingman_start_y = list_content_rect.y + 5
    wingman_slots = [
        {"id": 0, "name": "僚机 1"},
        {"id": 1, "name": "僚机 2"},
        {"id": 2, "name": "僚机 3"},
        {"id": 3, "name": "僚机 4"}
    ]
    
    for i, slot in enumerate(wingman_slots):
        rect = pygame.Rect(40, wingman_start_y + i * 60, 260, 55)
        
        equipped_theme = customization_manager.equipped_wingman_themes.get(f"slot_{slot['id']}", "default")
        is_selected = (customization_selected_wingman == slot['id'])
        h = rect.collidepoint(mx, my) or is_selected
        
        bg_color = (0, 80, 80) if is_selected else ((40, 50, 60) if h else (30, 30, 40))
        draw_cyber_rect(screen, rect, bg_color, fill=True)
        if is_selected: 
            draw_cyber_rect(screen, rect, CYAN, border_width=2, fill=False)
        
        # 左侧预览图（与机体涂装一样）
        if equipped_theme != "default" and equipped_theme in PAINT_THEMES:
            theme = PAINT_THEMES[equipped_theme]
            exclusive_plane = theme.get("exclusive_plane")
            if exclusive_plane and exclusive_plane in PLANES:
                visual = customization_manager.get_theme_visual(exclusive_plane, PLANES[exclusive_plane].get('visual', None), preview_theme_id=equipped_theme)
                icon = get_plane_surf(exclusive_plane, visual, static=True)
                icon = pygame.transform.scale(icon, (40, 40))
                safe_blit(screen, icon, (rect.x + 5, rect.y + 7))
        
        # 显示僚机编号（右移为预览图腾出空间）
        draw_text(screen, slot['name'], 16, rect.x + 150, rect.y + 12, WHITE, align="center")
        
        # 显示当前装备的涂装
        if equipped_theme != "default" and equipped_theme in PAINT_THEMES:
            theme = PAINT_THEMES[equipped_theme]
            theme_name = theme["name"]
            cat = theme.get("category", "default")
            quality_colors = {
                "default": (150, 150, 150),
                "common": (220, 220, 220),
                "rare": (100, 150, 255),
                "epic": (200, 100, 255),
                "legendary": (255, 215, 0),
                "exclusive": (255, 50, 150)
            }
            q_color = quality_colors.get(cat, GRAY)
            draw_text(screen, f"[{theme_name}]", 13, rect.x + 150, rect.y + 32, q_color, align="center")
        else:
            draw_text(screen, "[默认涂装]", 13, rect.x + 150, rect.y + 32, GRAY, align="center")
    
    screen.set_clip(None)
    
    # 右侧：涂装列表（仅显示专属涂装）
    theme_list_area = pygame.Rect(330, 100, 600, HEIGHT - 180)
    draw_cyber_rect(screen, theme_list_area, (20, 20, 30), alpha=220, fill=True)
    
    # 机体筛选标签
    filter_text = "全部机体" if wingman_theme_filter is None else PLANES[wingman_theme_filter]["name"]
    draw_text(screen, f"筛选: {filter_text}", 22, theme_list_area.centerx, 110, CYAN)
    
    # 机体筛选按钮行
    filter_y = 140
    filter_btn_w = 55
    filter_btn_h = 25
    filter_start_x = theme_list_area.x + 5
    
    # "全部"按钮
    all_btn = pygame.Rect(filter_start_x, filter_y, filter_btn_w, filter_btn_h)
    all_active = (wingman_theme_filter is None)
    draw_cyber_rect(screen, all_btn, (0, 100, 100) if all_active else (40, 40, 50), fill=True)
    if all_active:
        draw_cyber_rect(screen, all_btn, CYAN, border_width=1, fill=False)
    draw_text(screen, "全部", 12, all_btn.centerx, all_btn.centery - 6, CYAN if all_active else WHITE)
    
    # 机体筛选按钮（显示前10个机体）
    plane_keys_list = list(PLANES.keys())
    for pi, plane_id in enumerate(plane_keys_list[:10]):
        btn_x = filter_start_x + (pi + 1) * (filter_btn_w + 3)
        if btn_x + filter_btn_w > theme_list_area.right - 5:
            break
        plane_btn = pygame.Rect(btn_x, filter_y, filter_btn_w, filter_btn_h)
        is_active = (wingman_theme_filter == plane_id)
        draw_cyber_rect(screen, plane_btn, (0, 100, 100) if is_active else (40, 40, 50), fill=True)
        if is_active:
            draw_cyber_rect(screen, plane_btn, CYAN, border_width=1, fill=False)
        # 显示机体简称（取前2个字）
        short_name = PLANES[plane_id]["name"][:2]
        draw_text(screen, short_name, 11, plane_btn.centerx, plane_btn.centery - 6, CYAN if is_active else WHITE)
    
    # 第二行筛选按钮（剩余机体）
    filter_y2 = filter_y + filter_btn_h + 3
    for pi, plane_id in enumerate(plane_keys_list[10:]):
        btn_x = filter_start_x + pi * (filter_btn_w + 3)
        if btn_x + filter_btn_w > theme_list_area.right - 5:
            break
        plane_btn = pygame.Rect(btn_x, filter_y2, filter_btn_w, filter_btn_h)
        is_active = (wingman_theme_filter == plane_id)
        draw_cyber_rect(screen, plane_btn, (0, 100, 100) if is_active else (40, 40, 50), fill=True)
        if is_active:
            draw_cyber_rect(screen, plane_btn, CYAN, border_width=1, fill=False)
        short_name = PLANES[plane_id]["name"][:2]
        draw_text(screen, short_name, 11, plane_btn.centerx, plane_btn.centery - 6, CYAN if is_active else WHITE)
    
    # --- 筛选涂装（按机体筛选）---
    filtered_themes = []
    for tid, theme in PAINT_THEMES.items():
        exclusive_plane = theme.get("exclusive_plane")
        if not exclusive_plane:
            continue
        # 如果设置了筛选器，只显示对应机体的涂装
        if wingman_theme_filter is not None and exclusive_plane != wingman_theme_filter:
            continue
        filtered_themes.append((tid, theme))
    
    theme_y_start = 200
    
    # 列表裁剪区域
    list_view_rect = pygame.Rect(theme_list_area.x, theme_y_start, theme_list_area.width, theme_list_area.height - (theme_y_start - theme_list_area.y))
    screen.set_clip(list_view_rect)
    screen.set_clip(list_view_rect)
    
    for i, (theme_id, theme) in enumerate(filtered_themes):
        card_rect = pygame.Rect(350, theme_y_start + i * 100 - customization_scroll_y, 560, 90)
        
        # 跳过不可见的卡片
        if card_rect.bottom < list_view_rect.top or card_rect.top > list_view_rect.bottom:
            continue
        
        is_unlocked = customization_manager.unlocked_themes.get(theme_id, False)
        current_equipped = customization_manager.equipped_wingman_themes.get(f"slot_{customization_selected_wingman}", "default")
        is_equipped = (current_equipped == theme_id)
        h = card_rect.collidepoint(mx, my)
        
        # 背景颜色
        if is_equipped:
            bg_color = (0, 100, 100)
        elif is_unlocked:
            bg_color = (40, 50, 40) if h else (30, 35, 30)
        else:
            bg_color = (50, 30, 30) if h else (30, 20, 20)
        
        draw_cyber_rect(screen, card_rect, bg_color, fill=True)
        
        # 品质颜色定义
        cat = theme.get("category", "default")
        quality_colors = {
            "default": (150, 150, 150),
            "common": (220, 220, 220),
            "rare": (100, 150, 255),
            "epic": (200, 100, 255),
            "legendary": (255, 215, 0),
            "exclusive": (255, 50, 150)
        }
        q_color = quality_colors.get(cat, GRAY)
        
        # 边框
        if is_equipped:
            draw_cyber_rect(screen, card_rect, CYAN, border_width=3, fill=False)
            pygame.draw.rect(screen, q_color, card_rect.inflate(-8, -8), 1)
        elif h:
            draw_cyber_rect(screen, card_rect, WHITE, border_width=2, fill=False)
        else:
            draw_cyber_rect(screen, card_rect, q_color, border_width=1, fill=False)
        
        # 预览图（使用专属机体的视觉效果）
        exclusive_plane = theme.get("exclusive_plane")
        if exclusive_plane and exclusive_plane in PLANES:
            visual = customization_manager.get_theme_visual(exclusive_plane, PLANES[exclusive_plane].get('visual', None), preview_theme_id=theme_id)
            preview = get_plane_surf(exclusive_plane, visual, static=True)
            preview = pygame.transform.scale(preview, (60, 60))
            safe_blit(screen, preview, (card_rect.x + 10, card_rect.y + 15))
        
        # 信息文字
        info_x = card_rect.x + 85
        draw_text(screen, theme["name"], 18, info_x, card_rect.y + 10, q_color, align="left")
        draw_text(screen, theme["desc"], 14, info_x, card_rect.y + 32, GRAY, align="left")
        
        # 显示专属机体信息
        if exclusive_plane:
            p_name = PLANES.get(exclusive_plane, {}).get("name", exclusive_plane)
            draw_text(screen, f"专属: {p_name}", 12, info_x, card_rect.y + 52, MAGENTA, align="left")
        
        # 按钮
        btn_x = card_rect.right - 120
        btn_y = card_rect.y + 25
        btn_rect = pygame.Rect(btn_x, btn_y, 100, 40)
        
        if is_equipped:
            draw_text(screen, "已装备", 16, btn_rect.centerx, btn_rect.centery - 8, GREEN)
        elif is_unlocked:
            btn_h = btn_rect.collidepoint(mx, my)
            draw_cyber_rect(screen, btn_rect, CYAN if btn_h else (0, 100, 100), fill=True)
            draw_text(screen, "装备", 16, btn_rect.centerx, btn_rect.centery - 8, WHITE)
        else:
            cost = theme.get("cost", 0)
            btn_h = btn_rect.collidepoint(mx, my)
            can_afford = arsenal_save_data["currencies"]["cores"] >= cost
            btn_color = GOLD if (btn_h and can_afford) else ((80, 60, 0) if can_afford else (60, 30, 30))
            draw_cyber_rect(screen, btn_rect, btn_color, fill=True)
            draw_text(screen, f"{cost}", 14, btn_rect.centerx, btn_rect.centery - 8, WHITE if can_afford else RED)
    
    screen.set_clip(None)
    
    # 消息提示
    if customization_msg_timer > 0:
        msg_y = HEIGHT - 150
        msg_rect = pygame.Rect(WIDTH//2 - 200, msg_y, 400, 40)
        draw_cyber_rect(screen, msg_rect, (50, 50, 50), alpha=200, fill=True)
        draw_text(screen, customization_msg, 18, msg_rect.centerx, msg_rect.centery - 8, CYAN)
        customization_msg_timer -= 1
    
    # 大预览区（右下角）
    preview_area = pygame.Rect(WIDTH - 350, HEIGHT - 280, 320, 250)
    draw_cyber_rect(screen, preview_area, (20, 20, 30), alpha=240, fill=True)
    draw_text(screen, "涂装预览", 20, preview_area.centerx, preview_area.y + 15, MAGENTA)
    
    # 获取当前装备的涂装预览
    equipped_theme = customization_manager.equipped_wingman_themes.get(f"slot_{customization_selected_wingman}", "default")
    if equipped_theme != "default" and equipped_theme in PAINT_THEMES:
        theme = PAINT_THEMES[equipped_theme]
        exclusive_plane = theme.get("exclusive_plane")
        if exclusive_plane and exclusive_plane in PLANES:
            visual = customization_manager.get_theme_visual(exclusive_plane, PLANES[exclusive_plane].get('visual', None), preview_theme_id=equipped_theme)
            big_preview = get_plane_surf(exclusive_plane, visual)
            big_preview = pygame.transform.scale(big_preview, (150, 150))
            safe_blit(screen, big_preview, (preview_area.centerx - 75, preview_area.y + 50))
            
            # 显示涂装名称和专属机体
            draw_text(screen, theme["name"], 18, preview_area.centerx, preview_area.bottom - 35, CYAN)
            p_name = PLANES.get(exclusive_plane, {}).get("name", exclusive_plane)
            draw_text(screen, f"[{p_name}]", 14, preview_area.centerx, preview_area.bottom - 15, MAGENTA)
    else:
        # 显示默认涂装提示
        draw_text(screen, "未装备涂装", 16, preview_area.centerx, preview_area.centery, GRAY)


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
        
        # 背景框
        text_surf = pygame.font.SysFont("SimHei", 16).render(text, True, color)
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
    bar_w = 240
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
    
    # 绘制血量条（更宽）
    hp_bar_w = bar_w + 40
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
        boss_y = 130  # 顶部位置，避开玩家血条和属性图标
        boss_bar_w = 600
        boss_x = (WIDTH - boss_bar_w) // 2
        boss_bar_h = 20  # 增加高度使其更明显
        
        # BOSS血条容器背景（半透明黑色）
        container_padding = 15
        container_rect = pygame.Rect(boss_x - container_padding, boss_y - 35, 
                                     boss_bar_w + container_padding * 2, 65)
        draw_cyber_rect(screen, container_rect, (10, 10, 15), alpha=200, fill=True)
        
        # BOSS名称（居中，更大字体，多层阴影）
        boss_name_text = boss.name.upper()
        center_x = WIDTH // 2
        name_y = boss_y - 18
        # 外层红色光晕
        for offset_x, offset_y in [(-2, -2), (2, -2), (-2, 2), (2, 2), (-3, 0), (3, 0), (0, -3), (0, 3)]:
            draw_text(screen, boss_name_text, 16, center_x + offset_x, name_y + offset_y, (100, 0, 0))
        # 内层明亮描边
        for offset_x, offset_y in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            draw_text(screen, boss_name_text, 16, center_x + offset_x, name_y + offset_y, (255, 100, 100))
        # 主文字
        draw_text(screen, boss_name_text, 16, center_x, name_y, (255, 220, 220), glow=True)
        
        # BOSS血条外框（增强边框效果）
        border_rect = pygame.Rect(boss_x - 2, boss_y - 2, boss_bar_w + 4, boss_bar_h + 4)
        draw_cyber_rect(screen, border_rect, CYBER_RED_ALERT, border_width=2, fill=False)
        
        # BOSS血条背景（深色）
        pygame.draw.rect(screen, (30, 10, 10), (boss_x, boss_y, boss_bar_w, boss_bar_h))
        
        # BOSS血条填充（渐变效果）
        boss_hp_pct = max(0, min(1, boss.hp / boss.max_hp))
        boss_fill = int(boss_hp_pct * boss_bar_w)
        
        if boss_fill > 0:
            # 渐变色填充：从橙红到深红
            for i in range(boss_fill):
                ratio = i / boss_bar_w
                r = int(255 - ratio * 50)
                g = int(80 - ratio * 30)
                b = int(80 - ratio * 30)
                pygame.draw.line(screen, (r, g, b), 
                               (boss_x + i, boss_y), 
                               (boss_x + i, boss_y + boss_bar_h))
            
            # 血条顶部高光
            highlight_h = boss_bar_h // 3
            highlight_surf = pygame.Surface((boss_fill, highlight_h), pygame.SRCALPHA)
            highlight_surf.fill((255, 150, 150, 80))
            screen.blit(highlight_surf, (boss_x, boss_y))
            
            # 边缘发光线
            if boss_fill > 3:
                for offset in range(2):
                    pygame.draw.line(screen, (255, 200, 200, 150), 
                                   (boss_x + boss_fill - 1 - offset, boss_y),
                                   (boss_x + boss_fill - 1 - offset, boss_y + boss_bar_h))
        
        # BOSS血量数值（居中显示，使用百分比，增强质感）
        hp_text = f"{int(boss.hp):,} / {int(boss.max_hp):,}"
        hp_percent = f"({boss_hp_pct * 100:.1f}%)"
        hp_text_y = boss_y + boss_bar_h // 2 - 6
        percent_y = boss_y + boss_bar_h + 8
        
        # 血量数值 - 黑色描边 + 白色主体
        for offset_x, offset_y in [(-1, -1), (1, -1), (-1, 1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            draw_text(screen, hp_text, 12, center_x + offset_x, hp_text_y + offset_y, (0, 0, 0))
        draw_text(screen, hp_text, 12, center_x, hp_text_y, (255, 255, 255), glow=True)
        
        # 百分比 - 黑色描边 + 琥珀色主体
        for offset_x, offset_y in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            draw_text(screen, hp_percent, 10, center_x + offset_x, percent_y + offset_y, (20, 10, 0))
        draw_text(screen, hp_percent, 10, center_x, percent_y, CYBER_AMBER, glow=True)
        # Draw phase threshold markers
        try:
            phases = getattr(boss, 'phase_configs', boss.data.get('phases', []))
            for pidx, p in enumerate(phases):
                thresh = p.get('threshold', 0)
                tx = boss_x + int(boss_bar_w * thresh)
                pygame.draw.line(screen, (220, 220, 220), (tx, boss_y), (tx, boss_y + boss_bar_h), 2)
                # highlight current phase
                if pidx == boss.phase_index - 1:
                    # draw a subtle overlay for the phase
                    overlay_w = boss_bar_w - tx
                    s = pygame.Surface((overlay_w, boss_bar_h), pygame.SRCALPHA)
                    s.fill((*boss.visual.get('aura', (255,80,80)), 40) if boss.visual else (255,80,80,40))
                    safe_blit(screen, s, (tx, boss_y))
        except Exception:
            pass
        # Phase flash label
        if getattr(boss, 'phase_change_timer', 0) > 0:
            phase_label = f"PHASE {boss.phase_index}"
            draw_text(screen, phase_label, 18, boss_x + boss_bar_w//2, boss_y - 20, CYBER_AMBER, glow=True)

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
                    if event.key == pygame.K_LEFT:
                        current_plane_idx = (current_plane_idx - 1) % len(plane_keys)
                        sound_mgr.play("select")
                    elif event.key == pygame.K_RIGHT:
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
                            leaderboard_data.append({"name": name, "score": final_score})
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
                        # 先选飞机，再开始挑战
                        game_state = "boss_challenge_select_plane"
                        boss_challenge_plane_selected = 0
                        sound_mgr.play("select")
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                        game_state = "menu"; main_menu_selected = 0; sound_mgr.play("select")
                
                # Boss挑战模式飞机选择
                elif game_state == "boss_challenge_select_plane":
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # 确认选择，开始Boss挑战
                        selected_plane = plane_keys[current_plane_idx]
                        game_state = "boss_challenge_play"
                        boss_challenge_current = 0
                        boss_challenge_active = True
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
                
                # 成就菜单点击
                elif game_state == "achievements":
                    if player and hasattr(player, 'achievement_manager'):
                        ach_list = list(player.achievement_manager.achievements.values())
                        page_size = 6
                        max_page = (len(ach_list) + page_size - 1) // page_size
                        
                        if achievement_page > 0:
                            prev_btn = pygame.Rect(WIDTH//2 - 200, HEIGHT - 100, 80, 40)
                            if prev_btn.collidepoint(mx, my):
                                achievement_page = max(0, achievement_page - 1)
                        
                        if achievement_page < max_page - 1:
                            next_btn = pygame.Rect(WIDTH//2 + 120, HEIGHT - 100, 80, 40)
                            if next_btn.collidepoint(mx, my):
                                achievement_page += 1
                    
                    # 返回按钮
                    back_btn = pygame.Rect(WIDTH//2 - 60, HEIGHT - 50, 120, 40)
                    if back_btn.collidepoint(mx, my):
                        if player and hasattr(player, 'achievement_manager'):
                            player.achievement_manager.save_to_file()
                        game_state = "menu"; main_menu_selected = 0; sound_mgr.play("select")
                
                # 背景设置界面点击
                elif game_state == "background_settings":
                    from systems import BackgroundManager
                    bg_styles = BackgroundManager.BG_STYLES
                    bg_list = list(bg_styles.items())
                    
                    # 分页配置
                    card_w = 280
                    card_h = 200
                    cards_per_row = 4
                    cards_per_page = 8
                    gap = 30
                    start_x = (WIDTH - (cards_per_row * card_w + (cards_per_row - 1) * gap)) // 2
                    start_y = 130
                    
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
                    
                    # 上一页/下一页按钮（卡片下方那一行的左右两侧）
                    rows_per_page = 2
                    button_y = start_y + rows_per_page * (card_h + gap) + 30
                    button_w = 100
                    button_h = 50
                    total_pages = (len(bg_list) + cards_per_page - 1) // cards_per_page
                    
                    prev_btn = pygame.Rect(80, button_y, button_w, button_h)
                    next_btn = pygame.Rect(WIDTH - 180, button_y, button_w, button_h)
                    
                    if prev_btn.collidepoint(mx, my) and background_settings_page > 0:
                        background_settings_page -= 1
                        sound_mgr.play("select")
                    elif next_btn.collidepoint(mx, my) and background_settings_page < total_pages - 1:
                        background_settings_page += 1
                        sound_mgr.play("select")
                    
                    # 返回按钮
                    back_btn = pygame.Rect(WIDTH//2 - 60, HEIGHT - 80, 120, 50)
                    if back_btn.collidepoint(mx, my):
                        game_state = "menu"
                        main_menu_selected = 0
                        sound_mgr.play("select")

                elif game_state == "select_plane":
                    left_rect = pygame.Rect(100, HEIGHT//2-40, 60, 80)
                    right_rect = pygame.Rect(WIDTH-160, HEIGHT//2-40, 60, 80)
                    start_btn = pygame.Rect(WIDTH//2-100, HEIGHT-120, 200, 60)
                    back_btn = pygame.Rect(50, HEIGHT-80, 100, 40)
                    
                    if left_rect.collidepoint(mx, my):
                        current_plane_idx = (current_plane_idx-1)%len(plane_keys)
                        sound_mgr.play("select")
                    elif right_rect.collidepoint(mx, my):
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
                    
                elif game_state == "arsenal":
                    sound_mgr.play("select")
                    r = ARSENAL_UI
                    # 列表点击 (修正为支持滚动)
                    if r['list_area'].collidepoint(mx, my):
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
                    if pygame.Rect(20, HEIGHT//2 - 25, 50, 50).collidepoint(mx, my) and gallery_page > 0: 
                        gallery_page -= 1
                    if pygame.Rect(WIDTH-70, HEIGHT//2 - 25, 50, 50).collidepoint(mx, my): 
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
                    if r['list_view'].collidepoint(mx, my):
                        offset_y = my - r['list_view'].y + codex_scroll_y
                        clicked_idx = int(offset_y // 45)
                        if codex_tab == 0:
                            keys = plane_keys
                        elif codex_tab == 1:
                            keys = list(BOSS_DB.keys())
                        else:  # codex_tab == 2
                            from enemy_manager import enemy_type_manager
                            keys = [e["id"] for e in enemy_type_manager.get_regular_types()]
                        if 0 <= clicked_idx < len(keys): codex_idx = clicked_idx
                    if r['btn_back'].collidepoint(mx, my):
                        if player and hasattr(player, 'achievement_manager'):
                            player.achievement_manager.save_to_file()
                        game_state = "menu"

                elif game_state == "leaderboard":
                    sound_mgr.play("select")
                    if pygame.Rect(WIDTH//2-60, HEIGHT-100, 120, 50).collidepoint(mx, my):
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

            if event.type == pygame.MOUSEWHEEL:
                if game_state == "music_library":
                    scroll_music_library(-event.y)
                elif game_state == "sound_lab":
                    scroll_sound_lab(-event.y)
        
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
                            # 轨道1：波次事件系统
                            # ================================================================
                            if not boss and not wave_event_active:
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
                            
                            # 波次预警倒计时
                            if wave_event_active and wave_warning_timer > 0:
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
                            if not wave_event_active or wave_warning_timer <= 0:
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
                                boss.kill(); boss = None; score += 10000
                                
                                # ===== Boss击杀特效（大幅简化） =====
                                # 屏幕震动 - 减弱
                                screen_shake_offset = apply_screen_shake(4)
                                
                                # 单次爆炸
                                create_explosion(boss.rect.center, (255, 120, 0), 10)
                                
                                # 少量粒子
                                if random.random() < 0.8:
                                    for _ in range(4):
                                        angle = random.uniform(0, math.pi * 2)
                                        speed = random.uniform(4, 7)
                                        Particle(boss.rect.center, GOLD)
                                
                                # 音效
                                sound_mgr.play("nuke")
                                deactivate_boss_music()
                                try:
                                    activate_background_music(bg_manager.current_style)
                                except: pass
                                
                                FloatingText(WIDTH//2, HEIGHT//2, "BOSS DEFEATED", GOLD)
                                
                                # ========== Boss击杀奖励：物品掉落 ==========
                                if item_manager:
                                    item_manager.spawn_boss_drops(boss.rect.centerx, boss.rect.centery)
                                
                                # ========== Boss击杀奖励：大量经验 ==========
                                boss_xp_reward = 200 + player.level * 50  # 基础200 + 等级*50
                                for i in range(8):  # 掉落8个大经验球
                                    offset_x = random.randint(-80, 80)
                                    offset_y = random.randint(-60, 60)
                                    ExperienceOrb(boss.rect.centerx + offset_x, boss.rect.centery + offset_y, boss_xp_reward // 8)
                                FloatingText(boss.rect.centerx, boss.rect.top - 50, f"经验+{boss_xp_reward}", GOLD)
                                
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