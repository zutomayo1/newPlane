import pygame
import sys
import random
import math
import traceback
import json
from config import *
from utils import *
from systems import *
from sprites import *
from customization import customization_manager, PAINT_THEMES, BULLET_THEMES, EnhancedTrailEffect
from enemies import enemy_factory, init_enemy_system

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

# 数值
score = 0
# boss_timer and scheduling managed by BossManager
global_time_freeze = 0
wave = 0  # 波数

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

# 图鉴
gallery_page = 0
gallery_tab = 0 # 0:All, 1-4:Rarity

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

# 暂停菜单状态
pause_menu_selected = 0  # 0: 继续, 1: 重新开始, 2: 退出战斗

# ==============================================================================
# 主菜单选择
main_menu_selected = 0  # 用于键盘导航


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
#   Boss挑战模式相关全局变量
# ===============================================================================
boss_challenge_selected = 0
boss_challenge_order = []
boss_challenge_current = 0
boss_challenge_active = False
boss_challenge_swap_timer = 0  # 换位动画计时器
boss_challenge_pulse_timer = 0  # 脉冲效果计时器
boss_challenge_scroll_offset = 0  # 列表滚动偏移
boss_challenge_key_repeat = {"up": 0, "down": 0, "left": 0, "right": 0}  # 键盘连按计时

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

def draw_bullet_preview(surface, theme, x, y, size=60):
    """绘制子弹涂装预览 - 根据特效真正区分视觉"""
    try:
        center_x = x + size // 2
        center_y = y + size // 2
        color = theme.get("color") or (255, 255, 255)
        particles = theme.get("particles", [])
        effects = theme.get("effects", [])
        
        # 根据特效绘制完全不同的形状
        if "gear_rotate" in effects:
            # 机械齿轮：六边形齿轮+旋转齿
            rotation = pygame.time.get_ticks() / 500
            # 绘制六边形主体
            points = []
            for i in range(6):
                angle = (i * 60 + rotation * 50) * 3.14159 / 180
                px = center_x + int(size//3 * math.cos(angle))
                py = center_y + int(size//3 * math.sin(angle))
                points.append((px, py))
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 255, 255), points, 2)
            # 绘制齿轮齿
            for i in range(6):
                angle = (i * 60 + rotation * 50) * 3.14159 / 180
                x1 = center_x + int(size//3 * math.cos(angle))
                y1 = center_y + int(size//3 * math.sin(angle))
                x2 = center_x + int(size//2.2 * math.cos(angle))
                y2 = center_y + int(size//2.2 * math.sin(angle))
                pygame.draw.line(surface, (200, 200, 200), (x1, y1), (x2, y2), 3)
        
        elif "phase_flicker" in effects:
            # 幽灵：波浪形半透明体
            alpha_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            alpha = int(128 + 64 * math.sin(pygame.time.get_ticks() / 200))
            # 绘制波浪形状
            points = []
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                radius = size//3 + size//8 * math.sin(i + pygame.time.get_ticks() / 100)
                px = size//2 + int(radius * math.cos(angle))
                py = size//2 + int(radius * math.sin(angle))
                points.append((px, py))
            pygame.draw.polygon(alpha_surf, (*color, alpha), points)
            surface.blit(alpha_surf, (x, y))
        
        elif "lava_crack" in effects:
            # 反应堆：裂开的方形+内部能量核心
            # 外层方形碎片
            fragments = [
                [(center_x-size//3, center_y-size//3), (center_x, center_y-size//2.5), (center_x-size//6, center_y-size//6)],
                [(center_x, center_y-size//2.5), (center_x+size//3, center_y-size//3), (center_x+size//6, center_y-size//6)],
                [(center_x+size//3, center_y-size//3), (center_x+size//2.5, center_y), (center_x+size//6, center_y+size//6)],
                [(center_x+size//2.5, center_y), (center_x+size//3, center_y+size//3), (center_x+size//6, center_y+size//6)]
            ]
            for frag in fragments:
                pygame.draw.polygon(surface, (100, 50, 50), frag)
                pygame.draw.polygon(surface, (255, 200, 0), frag, 2)
            # 中心发光核心
            pygame.draw.circle(surface, (255, 255, 0), (center_x, center_y), size//6)
            pygame.draw.circle(surface, color, (center_x, center_y), size//8)
        
        elif "quantum_shift" in effects:
            # 量子：三个菱形叠加
            offset = int(size//6 * math.sin(pygame.time.get_ticks() / 300))
            for i, dx in [(-offset, 180), (0, 255), (offset, 180)]:
                temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                # 绘制菱形
                diamond = [
                    (size//2 + dx, size//2 - size//4),
                    (size//2 + dx + size//4, size//2),
                    (size//2 + dx, size//2 + size//4),
                    (size//2 + dx - size//4, size//2)
                ]
                pygame.draw.polygon(temp_surf, (*color, dx), diamond)
                surface.blit(temp_surf, (x, y))
        
        elif "holy_ray" in effects:
            # 圣光：八芒星形
            # 绘制两个旋转45度的正方形形成八芒星
            for rotation in [0, 45]:
                points = []
                for i in range(4):
                    angle = (i * 90 + rotation) * 3.14159 / 180
                    px = center_x + int(size//2.8 * math.cos(angle))
                    py = center_y + int(size//2.8 * math.sin(angle))
                    points.append((px, py))
                pygame.draw.polygon(surface, color, points)
            # 中心圆
            pygame.draw.circle(surface, (255, 255, 220), (center_x, center_y), size//6)
        
        elif "dragon_breath" in effects:
            # 龙息：尖刺球体+向后喷射火焰
            # 中心球
            pygame.draw.circle(surface, color, (center_x, center_y), size//4)
            # 6个尖刺（向外突出）
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                x1 = center_x + int(size//4 * math.cos(angle))
                y1 = center_y + int(size//4 * math.sin(angle))
                x2 = center_x + int(size//2.2 * math.cos(angle))
                y2 = center_y + int(size//2.2 * math.sin(angle))
                # 绘制三角形尖刺
                angle_left = (angle - 0.3)
                angle_right = (angle + 0.3)
                px1 = center_x + int(size//4 * math.cos(angle_left))
                py1 = center_y + int(size//4 * math.sin(angle_left))
                px2 = center_x + int(size//4 * math.cos(angle_right))
                py2 = center_y + int(size//4 * math.sin(angle_right))
                pygame.draw.polygon(surface, (255, 100, 0), [(px1, py1), (x2, y2), (px2, py2)])
        
        elif "blade_orbit" in effects:
            # 光刃：三角形核心+3把长剑环绕
            # 中心三角形
            tri_points = [
                (center_x, center_y - size//6),
                (center_x - size//7, center_y + size//8),
                (center_x + size//7, center_y + size//8)
            ]
            pygame.draw.polygon(surface, color, tri_points)
            # 3把旋转剑
            for i in range(3):
                angle = (pygame.time.get_ticks() / 300 + i * 120) * 3.14159 / 180
                # 剑的起点和终点
                base_x = center_x + int(size//5 * math.cos(angle))
                base_y = center_y + int(size//5 * math.sin(angle))
                tip_x = center_x + int(size//2.2 * math.cos(angle))
                tip_y = center_y + int(size//2.2 * math.sin(angle))
                # 剑身（宽度渐变）
                perp_angle = angle + 3.14159/2
                w1 = size//15
                w2 = size//30
                sword_points = [
                    (base_x + int(w1 * math.cos(perp_angle)), base_y + int(w1 * math.sin(perp_angle))),
                    (tip_x + int(w2 * math.cos(perp_angle)), tip_y + int(w2 * math.sin(perp_angle))),
                    (tip_x - int(w2 * math.cos(perp_angle)), tip_y - int(w2 * math.sin(perp_angle))),
                    (base_x - int(w1 * math.cos(perp_angle)), base_y - int(w1 * math.sin(perp_angle)))
                ]
                pygame.draw.polygon(surface, (150, 200, 255), sword_points)
        
        # ========== Phantom 子弹形状 ==========
        elif "void_crack" in effects:
            # 虚空裂缝：不规则裂缝+黑洞漩涡
            # 中心黑洞
            for r in range(size//2, 0, -size//10):
                alpha = int(255 * (1 - r / (size//2)))
                temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size//2, size//2), r)
                surface.blit(temp_surf, (x, y))
            # 裂缝闪电
            for i in range(4):
                angle = (i * 90 + pygame.time.get_ticks() / 100) * 3.14159 / 180
                segments = []
                for j in range(4):
                    r = size//5 + j * size//10
                    px = center_x + int(r * math.cos(angle) + random.randint(-5, 5))
                    py = center_y + int(r * math.sin(angle) + random.randint(-5, 5))
                    segments.append((px, py))
                pygame.draw.lines(surface, (150, 0, 200), False, segments, 2)
        
        elif "ghost_face" in effects:
            # 幽灵面孔：脸型轮廓+眼睛+嘴巴
            # 脸型（椭圆形半透明）
            temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.ellipse(temp_surf, (*color, 150), (size//6, size//8, size*2//3, size*3//4))
            surface.blit(temp_surf, (x, y))
            # 眼睛（发光）
            eye_y = center_y - size//8
            pygame.draw.circle(surface, (255, 255, 255), (center_x - size//6, eye_y), size//10)
            pygame.draw.circle(surface, (255, 255, 255), (center_x + size//6, eye_y), size//10)
            pygame.draw.circle(surface, (100, 100, 255), (center_x - size//6, eye_y), size//15)
            pygame.draw.circle(surface, (100, 100, 255), (center_x + size//6, eye_y), size//15)
            # 嘴巴（哀嚎弧形）
            mouth_rect = pygame.Rect(center_x - size//4, center_y, size//2, size//3)
            pygame.draw.arc(surface, (200, 200, 255), mouth_rect, 0, 3.14159, 3)
        
        elif "crystal_prism" in effects:
            # 水晶棱镜：多面体+内部光线
            # 外层八面体
            top = (center_x, center_y - size//2.5)
            bottom = (center_x, center_y + size//2.5)
            mid_points = []
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                px = center_x + int(size//3.5 * math.cos(angle))
                py = center_y + int(size//3.5 * math.sin(angle))
                mid_points.append((px, py))
            # 绘制上半部分面
            for i in range(4):
                face = [top, mid_points[i], mid_points[(i+1)%4]]
                pygame.draw.polygon(surface, color, face)
                pygame.draw.polygon(surface, (255, 255, 255), face, 2)
            # 绘制下半部分面
            for i in range(4):
                face = [bottom, mid_points[i], mid_points[(i+1)%4]]
                pygame.draw.polygon(surface, color, face)
                pygame.draw.polygon(surface, (255, 255, 255), face, 2)
            # 内部光线
            for i in range(4):
                pygame.draw.line(surface, (255, 255, 255), top, mid_points[i], 1)
        
        elif "tentacle_crawl" in effects:
            # 触手蠕动：多条触须+恐惧之眼
            # 中心眼球
            pygame.draw.circle(surface, (150, 0, 150), (center_x, center_y), size//4)
            pygame.draw.circle(surface, (255, 0, 255), (center_x, center_y), size//6)
            pygame.draw.circle(surface, (50, 0, 50), (center_x, center_y), size//10)
            # 6条扭曲触手
            for i in range(6):
                angle_base = i * 60 * 3.14159 / 180
                segments = [(center_x, center_y)]
                for j in range(5):
                    angle = angle_base + math.sin((pygame.time.get_ticks() / 200 + i + j)) * 0.3
                    r = (j + 1) * size // 12
                    px = center_x + int(r * math.cos(angle))
                    py = center_y + int(r * math.sin(angle))
                    segments.append((px, py))
                # 触手宽度递减
                for k in range(len(segments)-1):
                    width = max(1, 6 - k)
                    pygame.draw.line(surface, color, segments[k], segments[k+1], width)
        
        elif "aurora_tail" in effects:
            # 极光彗星：流星体+彩虹尾迹
            # 彗星头部（亮白核心）
            pygame.draw.circle(surface, (255, 255, 255), (center_x + size//6, center_y), size//5)
            pygame.draw.circle(surface, color, (center_x + size//6, center_y), size//7)
            # 彩虹尾迹（波浪状）
            colors = [(255, 100, 100), (255, 255, 100), (100, 255, 100), (100, 255, 255), (100, 100, 255)]
            for i, trail_color in enumerate(colors):
                wave_points = []
                for j in range(8):
                    offset = math.sin((pygame.time.get_ticks() / 100 + j + i)) * size // 15
                    px = center_x + size//6 - j * size // 15
                    py = center_y + offset
                    wave_points.append((px, py))
                if len(wave_points) > 1:
                    pygame.draw.lines(surface, trail_color, False, wave_points, 3)
        
        elif "hourglass_flow" in effects:
            # 沙漏流转：沙漏形状+流沙粒子
            # 上半部分三角形
            top_tri = [
                (center_x, center_y),
                (center_x - size//3, center_y - size//2.5),
                (center_x + size//3, center_y - size//2.5)
            ]
            pygame.draw.polygon(surface, color, top_tri)
            pygame.draw.polygon(surface, (255, 255, 255), top_tri, 2)
            # 下半部分三角形
            bottom_tri = [
                (center_x, center_y),
                (center_x - size//3, center_y + size//2.5),
                (center_x + size//3, center_y + size//2.5)
            ]
            pygame.draw.polygon(surface, color, bottom_tri)
            pygame.draw.polygon(surface, (255, 255, 255), bottom_tri, 2)
            # 流沙粒子
            for i in range(5):
                offset = (pygame.time.get_ticks() / 30 + i * 10) % (size//2)
                py = center_y - size//2.5 + offset
                if py < center_y + size//2.5:
                    pygame.draw.circle(surface, (255, 230, 150), (center_x, int(py)), 2)
        
        elif "matrix_rain" in effects:
            # 矩阵代码雨：数字方块瀑布
            # 绘制代码列
            for col in range(5):
                x_pos = x + col * size // 5 + size // 10
                blocks = int((pygame.time.get_ticks() / 100 + col * 3) % 8)
                for row in range(blocks):
                    y_pos = y + row * size // 8
                    block_size = size // 12
                    alpha = int(255 * (1 - row / 8))
                    temp_surf = pygame.Surface((block_size, block_size), pygame.SRCALPHA)
                    temp_surf.fill((*color, alpha))
                    surface.blit(temp_surf, (x_pos, y_pos))
                    # 边框
                    pygame.draw.rect(surface, (0, 200, 0), (x_pos, y_pos, block_size, block_size), 1)
        
        # ========== Titan 子弹形状（大型、醒目）==========
        elif "shell_massive" in effects:
            # 巨型炮弹：圆柱形弹体+尖锐弹头
            # 弹体（圆柱）
            body_width = size // 2
            body_height = size
            body_rect = (center_x - body_width//2, center_y - size//3, body_width, body_height)
            pygame.draw.rect(surface, color, body_rect, border_radius=5)
            pygame.draw.rect(surface, (180, 180, 180), body_rect, 3, border_radius=5)
            # 弹头（三角锥）
            tip = [
                (center_x, center_y - size//1.8),
                (center_x - body_width//2, center_y - size//3),
                (center_x + body_width//2, center_y - size//3)
            ]
            pygame.draw.polygon(surface, (100, 100, 100), tip)
            pygame.draw.polygon(surface, (200, 200, 200), tip, 2)
            # 底部推进器纹路
            for i in range(3):
                y_line = center_y + size//3 + i * size//8
                pygame.draw.line(surface, (80, 80, 80), 
                               (center_x - body_width//2, y_line),
                               (center_x + body_width//2, y_line), 2)
        
        elif "nuclear_glow" in effects:
            # 核辐射：多层发光球体+辐射符号
            # 外层脉冲光环
            pulse = abs(math.sin(pygame.time.get_ticks() / 200))
            for i in range(3):
                radius = size//2 + int(i * size//6 * pulse)
                alpha = int(100 * (1 - i/3))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), radius)
                surface.blit(temp_surf, (x-size//2, y-size//2))
            # 中心核心球
            pygame.draw.circle(surface, (255, 255, 0), (center_x, center_y), size//4)
            pygame.draw.circle(surface, color, (center_x, center_y), size//5)
            # 辐射标志（三叶符号）
            for i in range(3):
                angle = (i * 120) * 3.14159 / 180
                segment_start = (
                    center_x + int(size//6 * math.cos(angle)),
                    center_y + int(size//6 * math.sin(angle))
                )
                segment_end = (
                    center_x + int(size//2.2 * math.cos(angle)),
                    center_y + int(size//2.2 * math.sin(angle))
                )
                pygame.draw.line(surface, (0, 0, 0), segment_start, segment_end, 5)
                pygame.draw.circle(surface, (0, 0, 0), segment_end, size//10)
        
        elif "magma_boulder" in effects:
            # 熔岩巨石：不规则岩石+裂缝发光
            # 主体不规则多边形
            import random
            random.seed(42)  # 固定随机种子保证稳定显示
            points = []
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                radius = size//2.5 + random.randint(-size//8, size//8)
                px = center_x + int(radius * math.cos(angle))
                py = center_y + int(radius * math.sin(angle))
                points.append((px, py))
            pygame.draw.polygon(surface, (80, 40, 0), points)
            pygame.draw.polygon(surface, color, points, 3)
            # 岩浆裂缝（发光）
            for i in range(4):
                x1 = center_x + random.randint(-size//4, size//4)
                y1 = center_y + random.randint(-size//4, size//4)
                x2 = x1 + random.randint(-size//6, size//6)
                y2 = y1 + random.randint(-size//6, size//6)
                pygame.draw.line(surface, (255, 255, 0), (x1, y1), (x2, y2), 3)
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 1)
        
        elif "rocket_thruster" in effects:
            # 机械火箭：圆柱体+尾部推进器
            # 火箭头部（圆锥）
            nose = [
                (center_x, center_y - size//2),
                (center_x - size//5, center_y - size//4),
                (center_x + size//5, center_y - size//4)
            ]
            pygame.draw.polygon(surface, (200, 200, 200), nose)
            # 火箭身（圆柱+窗口）
            body_rect = (center_x - size//5, center_y - size//4, size*2//5, size*3//4)
            pygame.draw.rect(surface, color, body_rect)
            pygame.draw.rect(surface, (255, 255, 255), body_rect, 2)
            # 窗口
            pygame.draw.circle(surface, (100, 200, 255), (center_x, center_y), size//8)
            # 尾部推进器火焰
            flame_height = int(size//4 * (1 + 0.3 * math.sin(pygame.time.get_ticks() / 100)))
            flame = [
                (center_x - size//5, center_y + size//2),
                (center_x, center_y + size//2 + flame_height),
                (center_x + size//5, center_y + size//2)
            ]
            pygame.draw.polygon(surface, (255, 200, 0), flame)
            pygame.draw.polygon(surface, (255, 100, 0), [
                (center_x - size//8, center_y + size//2),
                (center_x, center_y + size//2 + flame_height//2),
                (center_x + size//8, center_y + size//2)
            ])
        
        elif "ice_spike" in effects:
            # 冰晶巨刺：多棱锥形+透明质感
            # 主尖刺（四棱锥）
            tip = (center_x, center_y - size//2)
            base_points = [
                (center_x - size//4, center_y + size//4),
                (center_x + size//4, center_y + size//4),
                (center_x + size//3, center_y),
                (center_x - size//3, center_y)
            ]
            # 绘制四个侧面
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            for i in range(4):
                face = [tip, base_points[i], base_points[(i+1)%4]]
                pygame.draw.polygon(temp_surf, (*color, 180), face)
                pygame.draw.polygon(temp_surf, (255, 255, 255), face, 2)
            surface.blit(temp_surf, (x-size//2, y-size//2))
            # 冰晶闪光
            for i in range(3):
                angle = (i * 120) * 3.14159 / 180
                px = center_x + int(size//3 * math.cos(angle))
                py = center_y + int(size//3 * math.sin(angle))
                pygame.draw.circle(surface, (255, 255, 255), (px, py), 3)
        
        elif "demon_skull" in effects:
            # 恶魔骷髅：骷髅头+角+火焰
            # 头骨轮廓
            pygame.draw.ellipse(surface, (120, 0, 0), 
                              (center_x - size//3, center_y - size//3, size*2//3, size*2//3))
            pygame.draw.ellipse(surface, color, 
                              (center_x - size//3, center_y - size//3, size*2//3, size*2//3), 3)
            # 眼睛（空洞）
            pygame.draw.circle(surface, (0, 0, 0), (center_x - size//6, center_y - size//10), size//10)
            pygame.draw.circle(surface, (255, 0, 0), (center_x - size//6, center_y - size//10), size//10, 2)
            pygame.draw.circle(surface, (0, 0, 0), (center_x + size//6, center_y - size//10), size//10)
            pygame.draw.circle(surface, (255, 0, 0), (center_x + size//6, center_y - size//10), size//10, 2)
            # 鼻子（三角洞）
            nose = [
                (center_x, center_y + size//12),
                (center_x - size//15, center_y + size//6),
                (center_x + size//15, center_y + size//6)
            ]
            pygame.draw.polygon(surface, (0, 0, 0), nose)
            # 恶魔角
            for dx in [-size//3, size//3]:
                horn = [
                    (center_x + dx, center_y - size//4),
                    (center_x + dx + (size//8 if dx < 0 else -size//8), center_y - size//2),
                    (center_x + dx + (size//6 if dx < 0 else -size//6), center_y - size//4)
                ]
                pygame.draw.polygon(surface, (80, 0, 0), horn)
                pygame.draw.polygon(surface, color, horn, 2)
        
        elif "plasma_beam" in effects:
            # 轨道激光柱：十字光柱+瞄准圈
            # 中心发光核心
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//5)
            pygame.draw.circle(surface, color, (center_x, center_y), size//6)
            # 垂直光束
            beam_width = size // 10
            pygame.draw.rect(surface, (*color, 200), 
                           (center_x - beam_width//2, center_y - size//2, beam_width, size))
            # 水平光束
            pygame.draw.rect(surface, (*color, 200), 
                           (center_x - size//2, center_y - beam_width//2, size, beam_width))
            # 瞄准圈
            for radius in [size//2.5, size//2]:
                pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), radius, 2)
            # 十字准星角标
            marker_len = size // 8
            for angle in [45, 135, 225, 315]:
                rad = angle * 3.14159 / 180
                x1 = center_x + int(size//2.2 * math.cos(rad))
                y1 = center_y + int(size//2.2 * math.sin(rad))
                x2 = x1 + int(marker_len * math.cos(rad))
                y2 = y1 + int(marker_len * math.sin(rad))
                pygame.draw.line(surface, (255, 255, 255), (x1, y1), (x2, y2), 2)
        
        # ========== Thunderbird 子弹形状 ==========
        elif "lightning_bolt" in effects:
            # 闪电箭矢：之字形闪电
            segments = [
                (center_x, center_y - size//2),
                (center_x + size//8, center_y - size//4),
                (center_x - size//12, center_y),
                (center_x + size//10, center_y + size//4),
                (center_x, center_y + size//2)
            ]
            pygame.draw.lines(surface, (255, 255, 255), False, segments, 6)
            pygame.draw.lines(surface, color, False, segments, 3)
            # 电弧光晕
            for i in range(3):
                offset = i * 3
                offset_segments = [(x + offset, y) for x, y in segments]
                alpha = 100 - i * 30
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                if len(offset_segments) > 1:
                    pygame.draw.lines(temp_surf, (*color, alpha), False, 
                                    [(x - center_x + size, y - center_y + size) for x, y in offset_segments], 2)
                    surface.blit(temp_surf, (x - size, y - size))
        
        elif "tesla_coil" in effects:
            # 特斯拉线圈：螺旋线圈+电弧环
            # 中心核心
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
            pygame.draw.circle(surface, color, (center_x, center_y), size//8)
            # 螺旋线圈
            coil_points = []
            for i in range(20):
                angle = i * 18 * 3.14159 / 180
                radius = size//6 + (i / 20) * size//3
                phase = pygame.time.get_ticks() / 200
                px = center_x + int(radius * math.cos(angle + phase))
                py = center_y + int(radius * math.sin(angle + phase))
                coil_points.append((px, py))
            if len(coil_points) > 1:
                pygame.draw.lines(surface, color, False, coil_points, 3)
            # 电弧环
            for i in range(3):
                arc_radius = size//4 + i * size//8
                pygame.draw.circle(surface, color, (center_x, center_y), arc_radius, 2)
        
        elif "feather_shape" in effects:
            # 等离子羽毛：羽毛形状
            # 羽轴（中央线）
            pygame.draw.line(surface, (200, 200, 200), 
                           (center_x, center_y - size//2), 
                           (center_x, center_y + size//2), 4)
            # 羽丝（两侧）
            for i in range(8):
                y = center_y - size//2 + i * size//8
                width = int(size//3 * (1 - abs(i - 4) / 4))
                # 左侧羽丝
                pygame.draw.line(surface, color, 
                               (center_x, y), 
                               (center_x - width, y + size//16), 2)
                # 右侧羽丝
                pygame.draw.line(surface, color, 
                               (center_x, y), 
                               (center_x + width, y + size//16), 2)
            # 半透明羽毛轮廓
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            feather_outline = [
                (size, size//2),
                (size - size//3, size),
                (size, size*3//2),
                (size + size//3, size)
            ]
            pygame.draw.polygon(temp_surf, (*color, 100), feather_outline)
            surface.blit(temp_surf, (x - size//2, y - size//2))
        
        elif "aurora_blade" in effects:
            # 极光羽刃：彩虹刀刃
            # 刀刃形状（菱形刀）
            blade = [
                (center_x, center_y - size//2),
                (center_x + size//6, center_y),
                (center_x, center_y + size//2),
                (center_x - size//6, center_y)
            ]
            # 彩虹渐变填充
            colors_gradient = [
                (255, 0, 0), (255, 127, 0), (255, 255, 0),
                (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
            ]
            for i, grad_color in enumerate(colors_gradient):
                offset = i * 2
                temp_blade = [(x + offset, y) for x, y in blade]
                alpha = 150 - i * 15
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.polygon(temp_surf, (*grad_color, alpha), 
                                  [(x - center_x + size, y - center_y + size) for x, y in temp_blade])
                surface.blit(temp_surf, (x - size, y - size))
            pygame.draw.polygon(surface, (255, 255, 255), blade, 2)
        
        elif "holy_spear" in effects:
            # 女武神之矛：长矛形状
            # 矛杆
            shaft_width = size // 12
            pygame.draw.rect(surface, (180, 160, 140), 
                           (center_x - shaft_width//2, center_y, shaft_width, size//2))
            # 矛尖（三角锥）
            spear_tip = [
                (center_x, center_y - size//2),
                (center_x - size//6, center_y),
                (center_x + size//6, center_y)
            ]
            pygame.draw.polygon(surface, (220, 220, 240), spear_tip)
            pygame.draw.polygon(surface, color, spear_tip, 2)
            # 圣光环绕
            for i in range(3):
                angle = (pygame.time.get_ticks() / 300 + i * 120) * 3.14159 / 180
                glow_x = center_x + int(size//3 * math.cos(angle))
                glow_y = center_y + int(size//3 * math.sin(angle))
                pygame.draw.circle(surface, (255, 255, 200), (glow_x, glow_y), size//15)
        
        elif "phoenix_plume" in effects:
            # 凤凰火羽：火焰羽毛
            # 羽轴
            pygame.draw.line(surface, (255, 200, 0), 
                           (center_x, center_y - size//2), 
                           (center_x, center_y + size//2), 5)
            # 火焰羽丝
            for i in range(6):
                y = center_y - size//2 + i * size//6
                flame_width = int(size//2.5 * (1 - abs(i - 3) / 3))
                # 左侧火焰
                flame_points_l = [
                    (center_x, y),
                    (center_x - flame_width//2, y + size//12),
                    (center_x - flame_width, y + size//8),
                    (center_x - flame_width//2, y + size//10)
                ]
                pygame.draw.polygon(surface, (255, 100, 0), flame_points_l)
                pygame.draw.polygon(surface, (255, 200, 0), flame_points_l, 2)
                # 右侧火焰
                flame_points_r = [
                    (center_x, y),
                    (center_x + flame_width//2, y + size//12),
                    (center_x + flame_width, y + size//8),
                    (center_x + flame_width//2, y + size//10)
                ]
                pygame.draw.polygon(surface, (255, 100, 0), flame_points_r)
                pygame.draw.polygon(surface, (255, 200, 0), flame_points_r, 2)
        
        elif "nebula_feather" in effects:
            # 星云羽毛：星点羽毛
            # 羽轴
            pygame.draw.line(surface, (200, 150, 255), 
                           (center_x, center_y - size//2), 
                           (center_x, center_y + size//2), 3)
            # 羽丝
            for i in range(8):
                y = center_y - size//2 + i * size//8
                width = int(size//3 * (1 - abs(i - 4) / 4))
                pygame.draw.line(surface, color, 
                               (center_x, y), 
                               (center_x - width, y + size//16), 2)
                pygame.draw.line(surface, color, 
                               (center_x, y), 
                               (center_x + width, y + size//16), 2)
            # 星点装饰
            import random
            random.seed(123)
            for _ in range(12):
                star_x = center_x + random.randint(-size//3, size//3)
                star_y = center_y + random.randint(-size//2, size//2)
                star_size = random.randint(1, 3)
                pygame.draw.circle(surface, (255, 255, 255), (star_x, star_y), star_size)
        
        # ========== Viper 子弹形状 ==========
        elif "venom_fang" in effects:
            # 毒牙：尖锐三角形+滴落毒液
            # 牙齿主体（三角形）
            fang = [
                (center_x, center_y + size//2),
                (center_x - size//4, center_y - size//3),
                (center_x + size//4, center_y - size//3)
            ]
            pygame.draw.polygon(surface, (200, 200, 200), fang)
            pygame.draw.polygon(surface, color, fang, 3)
            # 毒液滴（三个小滴）
            for i in range(3):
                drop_y = center_y + size//2 + (i + 1) * size//8
                drop_x = center_x + (i - 1) * size//12
                # 泪滴形状
                pygame.draw.circle(surface, color, (drop_x, drop_y), size//12)
                pygame.draw.polygon(surface, color, [
                    (drop_x, drop_y - size//12),
                    (drop_x - size//20, drop_y),
                    (drop_x + size//20, drop_y)
                ])
        
        elif "acid_drop" in effects:
            # 强酸液滴：滴落的酸液
            # 主液滴
            pygame.draw.circle(surface, color, (center_x, center_y), size//3)
            pygame.draw.circle(surface, (255, 255, 100), (center_x, center_y), size//5)
            # 泪滴尖端
            drop_tip = [
                (center_x, center_y + size//3),
                (center_x - size//8, center_y + size//6),
                (center_x + size//8, center_y + size//6)
            ]
            pygame.draw.polygon(surface, color, drop_tip)
            # 腐蚀轨迹（向下的小滴）
            for i in range(4):
                trail_y = center_y + size//2 + i * size//10
                trail_size = size//15 - i * 2
                if trail_size > 0:
                    alpha = 200 - i * 40
                    temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surf, (*color, alpha), (size, int(trail_y - center_y + size)), trail_size)
                    surface.blit(temp_surf, (x - size, y - size))
        
        elif "biohazard_symbol" in effects:
            # 生化危机符号：三叶辐射标志
            # 中心圆
            pygame.draw.circle(surface, (0, 0, 0), (center_x, center_y), size//8)
            pygame.draw.circle(surface, color, (center_x, center_y), size//8, 2)
            # 三个扇形叶片
            for i in range(3):
                angle = (i * 120) * 3.14159 / 180
                # 外圆
                leaf_x = center_x + int(size//3 * math.cos(angle))
                leaf_y = center_y + int(size//3 * math.sin(angle))
                pygame.draw.circle(surface, color, (leaf_x, leaf_y), size//6)
                pygame.draw.circle(surface, (0, 0, 0), (leaf_x, leaf_y), size//10)
                # 连接线
                inner_x = center_x + int(size//8 * math.cos(angle))
                inner_y = center_y + int(size//8 * math.sin(angle))
                outer_x = center_x + int(size//4 * math.cos(angle))
                outer_y = center_y + int(size//4 * math.sin(angle))
                pygame.draw.line(surface, color, (inner_x, inner_y), (outer_x, outer_y), 4)
        
        elif "plasma_orb" in effects:
            # 等离子毒液球：紫色能量球+波纹
            # 多层脉冲波纹
            pulse = abs(math.sin(pygame.time.get_ticks() / 200))
            for i in range(3):
                radius = size//4 + int(i * size//8 * pulse)
                alpha = int(150 * (1 - i/3))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), radius)
                surface.blit(temp_surf, (x - size, y - size))
            # 核心球
            pygame.draw.circle(surface, (255, 100, 255), (center_x, center_y), size//5)
            pygame.draw.circle(surface, color, (center_x, center_y), size//6)
        
        elif "hydra_heads" in effects:
            # 九头蛇：中心+多个蛇头
            # 中心身体
            pygame.draw.circle(surface, (100, 150, 50), (center_x, center_y), size//4)
            pygame.draw.circle(surface, color, (center_x, center_y), size//4, 2)
            # 5个蛇头（简化为5头）
            for i in range(5):
                angle = (i * 72 - 90) * 3.14159 / 180
                head_x = center_x + int(size//2 * math.cos(angle))
                head_y = center_y + int(size//2 * math.sin(angle))
                # 蛇头（小三角）
                head_tip = [
                    (head_x + int(size//8 * math.cos(angle)), head_y + int(size//8 * math.sin(angle))),
                    (head_x + int(size//12 * math.cos(angle + 0.5)), head_y + int(size//12 * math.sin(angle + 0.5))),
                    (head_x + int(size//12 * math.cos(angle - 0.5)), head_y + int(size//12 * math.sin(angle - 0.5)))
                ]
                pygame.draw.polygon(surface, (150, 200, 50), head_tip)
                pygame.draw.polygon(surface, color, head_tip, 2)
                # 连接线（脖子）
                pygame.draw.line(surface, color, (center_x, center_y), (head_x, head_y), 2)
        
        elif "neon_glow" in effects:
            # 霓虹毒液：发光液滴
            # 主液滴+外发光
            for r in range(size//2, size//6, -size//12):
                alpha = int(180 * (1 - (size//2 - r) / (size//3)))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), r)
                surface.blit(temp_surf, (x - size, y - size))
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
            pygame.draw.circle(surface, color, (center_x, center_y), size//8)
            # 泪滴尖端
            tip = [
                (center_x, center_y + size//3),
                (center_x - size//10, center_y + size//8),
                (center_x + size//10, center_y + size//8)
            ]
            pygame.draw.polygon(surface, color, tip)
        
        elif "serpent_eye" in effects:
            # 蛇神之眼：竖瞳
            # 外眼轮廓
            pygame.draw.ellipse(surface, (255, 200, 0), 
                              (center_x - size//3, center_y - size//4, size*2//3, size//2))
            pygame.draw.ellipse(surface, color, 
                              (center_x - size//3, center_y - size//4, size*2//3, size//4), 3)
            # 竖瞳（细长椭圆）
            pupil_width = size // 10
            pupil_height = size // 3
            pygame.draw.ellipse(surface, (0, 0, 0), 
                              (center_x - pupil_width//2, center_y - pupil_height//2, pupil_width, pupil_height))
            # 眼神光
            pygame.draw.circle(surface, (255, 255, 200), (center_x - size//12, center_y - size//12), size//15)
        
        # ========== Specter 子弹形状 ==========
        elif "scythe_blade" in effects:
            # 死神镰刀：弯月形刀刃
            # 镰刀柄
            handle_start = (center_x, center_y + size//3)
            handle_end = (center_x, center_y + size//2)
            pygame.draw.line(surface, (80, 80, 80), handle_start, handle_end, 5)
            # 弯月刀刃（弧形）
            blade_rect = pygame.Rect(center_x - size//2, center_y - size//2, size, size)
            pygame.draw.arc(surface, color, blade_rect, 0, 3.14159, 5)
            pygame.draw.arc(surface, (200, 100, 255), blade_rect, 0, 3.14159, 2)
            # 刀尖
            tip_points = [
                (center_x - size//2, center_y),
                (center_x - size//2 - size//8, center_y - size//12),
                (center_x - size//2, center_y - size//6)
            ]
            pygame.draw.polygon(surface, color, tip_points)
        
        elif "shadow_dagger" in effects:
            # 暗影匕首：尖锐短刃
            # 刀刃（菱形）
            blade = [
                (center_x, center_y - size//2),
                (center_x + size//8, center_y),
                (center_x, center_y + size//4),
                (center_x - size//8, center_y)
            ]
            pygame.draw.polygon(surface, (100, 100, 150), blade)
            pygame.draw.polygon(surface, color, blade, 2)
            # 刀柄
            handle_rect = (center_x - size//12, center_y + size//4, size//6, size//4)
            pygame.draw.rect(surface, (50, 50, 80), handle_rect)
            # 暗影效果
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            for i in range(3):
                offset = i * 3
                shadow_blade = [(x + offset, y) for x, y in blade]
                pygame.draw.polygon(temp_surf, (*color, 80 - i*20), 
                                  [(x - center_x + size, y - center_y + size) for x, y in shadow_blade])
            surface.blit(temp_surf, (x - size, y - size))
        
        elif "wraith_chain" in effects:
            # 怨灵锁链：波浪形锁链
            # 锁链链节
            chain_segments = 6
            for i in range(chain_segments):
                y_pos = center_y - size//2 + i * size//6
                wave = int(size//8 * math.sin(pygame.time.get_ticks() / 200 + i))
                # 链环
                link_rect = (center_x - size//10 + wave, y_pos, size//5, size//8)
                pygame.draw.ellipse(surface, color, link_rect, 3)
                # 连接线
                if i < chain_segments - 1:
                    next_wave = int(size//8 * math.sin(pygame.time.get_ticks() / 200 + i + 1))
                    pygame.draw.line(surface, color, 
                                   (center_x + wave, y_pos + size//16),
                                   (center_x + next_wave, y_pos + size//6), 2)
        
        elif "sniper_round" in effects:
            # 狙击弹：流线型子弹
            # 弹头（尖锥）
            tip = [
                (center_x, center_y - size//2),
                (center_x - size//6, center_y - size//4),
                (center_x + size//6, center_y - size//4)
            ]
            pygame.draw.polygon(surface, (200, 200, 220), tip)
            pygame.draw.polygon(surface, color, tip, 2)
            # 弹体（圆柱）
            body_rect = (center_x - size//6, center_y - size//4, size//3, size*2//3)
            pygame.draw.rect(surface, (180, 180, 200), body_rect)
            pygame.draw.rect(surface, color, body_rect, 2)
            # 弹壳纹路
            for i in range(3):
                y_line = center_y - size//8 + i * size//8
                pygame.draw.line(surface, color, 
                               (center_x - size//6, y_line),
                               (center_x + size//6, y_line), 1)
        
        elif "poltergeist_cube" in effects:
            # 灵异魔方：旋转方块
            # 3D方块效果
            rotation = pygame.time.get_ticks() / 500
            cube_size = size // 3
            # 正面
            front_points = [
                (center_x - cube_size, center_y - cube_size),
                (center_x + cube_size, center_y - cube_size),
                (center_x + cube_size, center_y + cube_size),
                (center_x - cube_size, center_y + cube_size)
            ]
            pygame.draw.polygon(surface, color, front_points)
            pygame.draw.polygon(surface, (255, 255, 255), front_points, 2)
            # 上面（透视）
            top_points = [
                (center_x - cube_size, center_y - cube_size),
                (center_x + cube_size, center_y - cube_size),
                (center_x + cube_size + cube_size//3, center_y - cube_size - cube_size//3),
                (center_x - cube_size + cube_size//3, center_y - cube_size - cube_size//3)
            ]
            pygame.draw.polygon(surface, (*color, 150), top_points)
            pygame.draw.polygon(surface, (200, 150, 255), top_points, 2)
            # 右侧
            side_points = [
                (center_x + cube_size, center_y - cube_size),
                (center_x + cube_size + cube_size//3, center_y - cube_size - cube_size//3),
                (center_x + cube_size + cube_size//3, center_y + cube_size - cube_size//3),
                (center_x + cube_size, center_y + cube_size)
            ]
            pygame.draw.polygon(surface, (*color, 180), side_points)
            pygame.draw.polygon(surface, (220, 180, 255), side_points, 2)
        
        elif "fallen_wing" in effects:
            # 堕落天使：黑色羽翼
            # 左翼
            for i in range(5):
                feather_x = center_x - size//6 - i * size//8
                feather_y = center_y - size//4 + i * size//10
                feather = [
                    (feather_x, feather_y),
                    (feather_x - size//10, feather_y + size//6),
                    (feather_x + size//15, feather_y + size//8)
                ]
                pygame.draw.polygon(surface, (50, 50, 80), feather)
                pygame.draw.polygon(surface, color, feather, 1)
            # 右翼
            for i in range(5):
                feather_x = center_x + size//6 + i * size//8
                feather_y = center_y - size//4 + i * size//10
                feather = [
                    (feather_x, feather_y),
                    (feather_x + size//10, feather_y + size//6),
                    (feather_x - size//15, feather_y + size//8)
                ]
                pygame.draw.polygon(surface, (50, 50, 80), feather)
                pygame.draw.polygon(surface, color, feather, 1)
            # 中心光晕
            pygame.draw.circle(surface, (150, 150, 200), (center_x, center_y), size//8)
        
        elif "void_rift" in effects:
            # 虚空裂缝：空间裂痕
            # 主裂缝
            rift_segments = [
                (center_x, center_y - size//2),
                (center_x - size//8, center_y - size//6),
                (center_x + size//10, center_y + size//8),
                (center_x - size//12, center_y + size//3),
                (center_x, center_y + size//2)
            ]
            pygame.draw.lines(surface, (150, 0, 200), False, rift_segments, 4)
            pygame.draw.lines(surface, (200, 100, 255), False, rift_segments, 2)
            # 虚空漩涡
            for r in range(size//2, 0, -size//10):
                alpha = int(150 * (1 - r / (size//2)))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), r)
                surface.blit(temp_surf, (x - size, y - size))
            # 空间碎片
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                shard_x = center_x + int(size//3 * math.cos(angle))
                shard_y = center_y + int(size//3 * math.sin(angle))
                shard = [
                    (shard_x, shard_y - size//12),
                    (shard_x + size//15, shard_y + size//12),
                    (shard_x - size//15, shard_y + size//12)
                ]
                pygame.draw.polygon(surface, (100, 0, 150), shard)
        
        # ========== Aurora 子弹形状 ==========
        elif "goddess_aura" in effects:
            # 女神光辉：神圣光环+光晕
            # 中心神圣核心
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
            pygame.draw.circle(surface, color, (center_x, center_y), size//8)
            # 神圣光环（3层）
            for i in range(3):
                ring_radius = size//4 + i * size//8
                alpha = 200 - i * 50
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), ring_radius, 3)
                surface.blit(temp_surf, (x - size, y - size))
            # 光晕粒子
            for i in range(8):
                angle = (i * 45 + pygame.time.get_ticks() / 30) * 3.14159 / 180
                px = center_x + int(size//2.5 * math.cos(angle))
                py = center_y + int(size//2.5 * math.sin(angle))
                pygame.draw.circle(surface, (255, 255, 220), (px, py), size//20)
        
        elif "holy_rings" in effects:
            # 圣洁光环：多层旋转光环
            # 中心
            pygame.draw.circle(surface, (255, 255, 240), (center_x, center_y), size//8)
            # 旋转光环
            for i in range(4):
                angle_offset = (i * 90 + pygame.time.get_ticks() / 20) * 3.14159 / 180
                ring_radius = size//3 + i * size//12
                # 绘制弧形光环
                arc_points = []
                for a in range(0, 180, 10):
                    rad = (a + angle_offset) * 3.14159 / 180
                    px = center_x + int(ring_radius * math.cos(rad))
                    py = center_y + int(ring_radius * math.sin(rad))
                    arc_points.append((px, py))
                if len(arc_points) > 1:
                    pygame.draw.lines(surface, color, False, arc_points, 2)
        
        elif "nebula_swirl" in effects:
            # 星云漩涡：旋转星云
            # 星云中心
            pygame.draw.circle(surface, (200, 150, 255), (center_x, center_y), size//6)
            # 漩涡臂
            for arm in range(3):
                arm_points = []
                arm_offset = arm * 120
                for i in range(15):
                    angle = (i * 24 + arm_offset + pygame.time.get_ticks() / 50) * 3.14159 / 180
                    radius = size//8 + i * size//30
                    px = center_x + int(radius * math.cos(angle))
                    py = center_y + int(radius * math.sin(angle))
                    arm_points.append((px, py))
                if len(arm_points) > 1:
                    temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    pygame.draw.lines(temp_surf, (*color, 180), False, 
                                    [(x - center_x + size, y - center_y + size) for x, y in arm_points], 3)
                    surface.blit(temp_surf, (x - size, y - size))
        
        elif "star_sparkle" in effects:
            # 星辰闪烁：闪烁星点
            # 主星
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
            pygame.draw.circle(surface, color, (center_x, center_y), size//8)
            # 十字星芒
            for angle in [0, 90, 180, 270]:
                rad = angle * 3.14159 / 180
                x1 = center_x + int(size//8 * math.cos(rad))
                y1 = center_y + int(size//8 * math.sin(rad))
                x2 = center_x + int(size//2 * math.cos(rad))
                y2 = center_y + int(size//2 * math.sin(rad))
                pygame.draw.line(surface, (255, 255, 255), (x1, y1), (x2, y2), 3)
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 1)
            # 闪烁小星
            import random
            random.seed(int(pygame.time.get_ticks() / 200))
            for _ in range(6):
                sx = center_x + random.randint(-size//2, size//2)
                sy = center_y + random.randint(-size//2, size//2)
                star_size = random.randint(1, 3)
                pygame.draw.circle(surface, (255, 255, 255), (sx, sy), star_size)
        
        elif "ice_crown" in effects:
            # 冰雪王冠：冰晶王冠形状
            # 王冠底部（圆环）
            pygame.draw.circle(surface, color, (center_x, center_y), size//3, 3)
            # 冰晶尖刺（6个）
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                base_x = center_x + int(size//3 * math.cos(angle))
                base_y = center_y + int(size//3 * math.sin(angle))
                tip_x = center_x + int(size//2 * math.cos(angle))
                tip_y = center_y + int(size//2 * math.sin(angle))
                # 冰锥三角
                ice_spike = [
                    (tip_x, tip_y),
                    (base_x + int(size//15 * math.cos(angle + 1.5708)), base_y + int(size//15 * math.sin(angle + 1.5708))),
                    (base_x - int(size//15 * math.cos(angle + 1.5708)), base_y - int(size//15 * math.sin(angle + 1.5708)))
                ]
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.polygon(temp_surf, (*color, 200), 
                                  [(x - center_x + size, y - center_y + size) for x, y in ice_spike])
                surface.blit(temp_surf, (x - size, y - size))
                pygame.draw.polygon(surface, (255, 255, 255), ice_spike, 2)
        
        elif "frost_spikes" in effects:
            # 冰霜尖刺：多根冰刺
            # 中心冰核
            pygame.draw.circle(surface, (230, 245, 255), (center_x, center_y), size//8)
            # 冰刺（8根）
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                spike_length = size//2 + (i % 2) * size//8
                x1 = center_x + int(size//8 * math.cos(angle))
                y1 = center_y + int(size//8 * math.sin(angle))
                x2 = center_x + int(spike_length * math.cos(angle))
                y2 = center_y + int(spike_length * math.sin(angle))
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 4)
                pygame.draw.line(surface, (255, 255, 255), (x1, y1), (x2, y2), 1)
        
        elif "rainbow_beam" in effects:
            # 彩虹光束：七彩射线
            # 彩虹颜色
            rainbow_colors = [
                (255, 0, 0), (255, 127, 0), (255, 255, 0),
                (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
            ]
            # 射线束
            for i, rainbow_color in enumerate(rainbow_colors):
                angle = (i * 360 / 7) * 3.14159 / 180
                x1 = center_x + int(size//6 * math.cos(angle))
                y1 = center_y + int(size//6 * math.sin(angle))
                x2 = center_x + int(size//2 * math.cos(angle))
                y2 = center_y + int(size//2 * math.sin(angle))
                pygame.draw.line(surface, rainbow_color, (x1, y1), (x2, y2), 3)
            # 中心白光
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
        
        elif "chromatic_shift" in effects:
            # 彩虹折射：色彩变换
            # 主体（圆形）
            for i in range(7):
                rainbow_color = [
                    (255, 0, 0), (255, 127, 0), (255, 255, 0),
                    (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
                ][i]
                offset = i * 3
                alpha = 200 - i * 20
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*rainbow_color, alpha), (size + offset, size), size//4)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "prism_split" in effects:
            # 棱镜折射：菱形棱镜+折射光
            # 棱镜主体（菱形）
            prism = [
                (center_x, center_y - size//2),
                (center_x + size//3, center_y),
                (center_x, center_y + size//2),
                (center_x - size//3, center_y)
            ]
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surf, (*color, 180), 
                              [(x - center_x + size, y - center_y + size) for x, y in prism])
            surface.blit(temp_surf, (x - size, y - size))
            pygame.draw.polygon(surface, (255, 255, 255), prism, 2)
            # 折射光线
            for i in range(3):
                angle = (30 + i * 30) * 3.14159 / 180
                x1 = center_x + int(size//3 * math.cos(angle))
                y1 = center_y + int(size//3 * math.sin(angle))
                x2 = center_x + int(size//2 * math.cos(angle + 0.3))
                y2 = center_y + int(size//2 * math.sin(angle + 0.3))
                refract_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
                pygame.draw.line(surface, refract_colors[i], (x1, y1), (x2, y2), 2)
        
        elif "light_refract" in effects:
            # 光线折射：多条折射光
            # 中心光源
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//8)
            # 折射光线（8条）
            colors_cycle = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                # 第一段
                x1 = center_x + int(size//8 * math.cos(angle))
                y1 = center_y + int(size//8 * math.sin(angle))
                x2 = center_x + int(size//3 * math.cos(angle))
                y2 = center_y + int(size//3 * math.sin(angle))
                # 第二段（折射）
                angle2 = angle + 0.4
                x3 = x2 + int(size//4 * math.cos(angle2))
                y3 = y2 + int(size//4 * math.sin(angle2))
                line_color = colors_cycle[i % 4]
                pygame.draw.line(surface, line_color, (x1, y1), (x2, y2), 2)
                pygame.draw.line(surface, line_color, (x2, y2), (x3, y3), 2)
        
        elif "sakura_petal" in effects:
            # 樱花飞舞：樱花花瓣形状
            # 花瓣（5瓣）
            for i in range(5):
                angle = (i * 72 + pygame.time.get_ticks() / 50) * 3.14159 / 180
                # 花瓣形状（椭圆）
                petal_x = center_x + int(size//4 * math.cos(angle))
                petal_y = center_y + int(size//4 * math.sin(angle))
                petal_width = size // 5
                petal_height = size // 3
                # 旋转的椭圆
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                petal_rect = pygame.Rect(0, 0, petal_width, petal_height)
                petal_rect.center = (size + int(size//4 * math.cos(angle)), 
                                    size + int(size//4 * math.sin(angle)))
                pygame.draw.ellipse(temp_surf, (*color, 200), petal_rect)
                pygame.draw.ellipse(temp_surf, (255, 180, 200), petal_rect, 1)
                surface.blit(temp_surf, (x - size, y - size))
            # 花心
            pygame.draw.circle(surface, (255, 200, 220), (center_x, center_y), size//10)
        
        elif "petal_spin" in effects:
            # 樱花旋转：旋转花瓣
            # 螺旋飘落的花瓣
            for i in range(4):
                angle = (i * 90 + pygame.time.get_ticks() / 30) * 3.14159 / 180
                radius = size//3 + (i % 2) * size//8
                px = center_x + int(radius * math.cos(angle))
                py = center_y + int(radius * math.sin(angle))
                # 单个花瓣（泪滴形）
                petal = [
                    (px, py - size//12),
                    (px + size//20, py),
                    (px, py + size//10),
                    (px - size//20, py)
                ]
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.polygon(temp_surf, (*color, 220), 
                                  [(x - center_x + size, y - center_y + size) for x, y in petal])
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "celestial_ring" in effects:
            # 天界光环：天使光环
            # 主光环
            pygame.draw.circle(surface, (255, 250, 240), (center_x, center_y - size//4), size//2, 4)
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y - size//4), size//2, 2)
            # 身体（简化的人形光芒）
            pygame.draw.circle(surface, color, (center_x, center_y + size//8), size//6)
            # 光芒射线
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                x1 = center_x + int(size//6 * math.cos(angle))
                y1 = center_y + size//8 + int(size//6 * math.sin(angle))
                x2 = center_x + int(size//2.5 * math.cos(angle))
                y2 = center_y + size//8 + int(size//2.5 * math.sin(angle))
                pygame.draw.line(surface, (255, 250, 220), (x1, y1), (x2, y2), 2)
        
        elif "divine_blessing" in effects:
            # 神圣祝福：十字光芒+圣光
            # 十字光芒
            pygame.draw.line(surface, (255, 255, 240), 
                           (center_x, center_y - size//2), 
                           (center_x, center_y + size//2), 5)
            pygame.draw.line(surface, (255, 255, 240), 
                           (center_x - size//2, center_y), 
                           (center_x + size//2, center_y), 5)
            pygame.draw.line(surface, color, 
                           (center_x, center_y - size//2), 
                           (center_x, center_y + size//2), 2)
            pygame.draw.line(surface, color, 
                           (center_x - size//2, center_y), 
                           (center_x + size//2, center_y), 2)
            # 中心光核
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
            pygame.draw.circle(surface, color, (center_x, center_y), size//8)
            # 外圈圣光
            for i in range(4):
                alpha = 150 - i * 30
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), size//4 + i * size//12, 2)
                surface.blit(temp_surf, (x - size, y - size))
        
        # ========== Crimson 子弹形状 ==========
        elif "blood_blade" in effects:
            # 血月之刃：弯刀形状+血雾
            # 弯刀刀身（弧形）
            blade_points = []
            for i in range(15):
                angle = (i * 12 - 90) * 3.14159 / 180
                radius = size // 2
                px = center_x + int(radius * math.cos(angle))
                py = center_y + int(radius * math.sin(angle))
                blade_points.append((px, py))
            if len(blade_points) > 1:
                pygame.draw.lines(surface, color, False, blade_points, 5)
                pygame.draw.lines(surface, (255, 0, 0), False, blade_points, 2)
            # 刀尖
            pygame.draw.circle(surface, (150, 0, 0), (center_x, center_y - size//2), size//10)
            # 血雾粒子
            import random
            random.seed(int(pygame.time.get_ticks() / 100))
            for _ in range(5):
                mist_x = center_x + random.randint(-size//3, size//3)
                mist_y = center_y + random.randint(-size//3, size//3)
                mist_size = random.randint(2, 5)
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, 100), 
                                 (mist_x - x + size, mist_y - y + size), mist_size)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "crimson_mist" in effects:
            # 血雾弥漫：血色雾气
            # 中心血珠
            pygame.draw.circle(surface, (150, 0, 0), (center_x, center_y), size//6)
            # 血雾扩散
            for i in range(5):
                radius = size//4 + i * size//10
                alpha = 150 - i * 25
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), radius)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "katana_slash" in effects:
            # 武士刀气：斜斩刀光
            # 刀光轨迹（对角线）
            x1, y1 = center_x - size//2, center_y + size//2
            x2, y2 = center_x + size//2, center_y - size//2
            # 多层刀光
            for i in range(5):
                offset = i * 2
                alpha = 220 - i * 30
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, (*color, alpha), 
                               (x1 - center_x + size + offset, y1 - center_y + size - offset),
                               (x2 - center_x + size + offset, y2 - center_y + size - offset), 6 - i)
                surface.blit(temp_surf, (x - size, y - size))
            # 刀光闪烁
            pygame.draw.line(surface, (255, 255, 255), (x1, y1), (x2, y2), 2)
        
        elif "blade_flash" in effects:
            # 刀光闪烁：闪光效果
            # 主刀光
            pygame.draw.line(surface, color, 
                           (center_x - size//2, center_y), 
                           (center_x + size//2, center_y), 6)
            pygame.draw.line(surface, (255, 255, 255), 
                           (center_x - size//2, center_y), 
                           (center_x + size//2, center_y), 2)
            # 闪光粒子
            for i in range(4):
                flash_x = center_x + (i - 1.5) * size//4
                flash_y = center_y
                pygame.draw.circle(surface, (255, 255, 255), (int(flash_x), flash_y), size//15)
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, 150), 
                                 (int(flash_x) - x + size, flash_y - y + size), size//10)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "demon_claw" in effects:
            # 恶魔之爪：三爪撕裂
            # 爪痕（3条）
            for i in range(3):
                offset = (i - 1) * size//6
                x1 = center_x + offset - size//8
                y1 = center_y - size//2
                x2 = center_x + offset + size//8
                y2 = center_y + size//2
                pygame.draw.line(surface, (80, 0, 0), (x1, y1), (x2, y2), 6)
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 3)
                pygame.draw.line(surface, (200, 0, 0), (x1, y1), (x2, y2), 1)
        
        elif "blood_scratch" in effects:
            # 血色爪痕：爪痕+血滴
            # 爪痕
            for i in range(4):
                offset = (i - 1.5) * size//8
                x1 = center_x + offset
                y1 = center_y - size//2
                x2 = center_x + offset + size//10
                y2 = center_y + size//2
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 3)
            # 血滴
            for i in range(3):
                drop_x = center_x + (i - 1) * size//6
                drop_y = center_y + size//3
                pygame.draw.circle(surface, (150, 0, 0), (drop_x, drop_y), size//15)
                # 泪滴尾巴
                tail = [
                    (drop_x, drop_y + size//15),
                    (drop_x - size//30, drop_y + size//10),
                    (drop_x + size//30, drop_y + size//10)
                ]
                pygame.draw.polygon(surface, (150, 0, 0), tail)
        
        elif "hellfire_burst" in effects:
            # 地狱烈焰：火焰爆发
            # 中心火核
            pygame.draw.circle(surface, (255, 255, 0), (center_x, center_y), size//8)
            pygame.draw.circle(surface, color, (center_x, center_y), size//6)
            # 爆发火焰（8个火舌）
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                flame_length = size//2 + int(size//8 * math.sin(pygame.time.get_ticks() / 100 + i))
                x1 = center_x + int(size//8 * math.cos(angle))
                y1 = center_y + int(size//8 * math.sin(angle))
                x2 = center_x + int(flame_length * math.cos(angle))
                y2 = center_y + int(flame_length * math.sin(angle))
                # 火焰渐变
                for j in range(3):
                    flame_color = [(255, 200, 0), (255, 100, 0), (200, 0, 0)][j]
                    offset = j * 2
                    x2_offset = center_x + int((flame_length - offset * 5) * math.cos(angle))
                    y2_offset = center_y + int((flame_length - offset * 5) * math.sin(angle))
                    pygame.draw.line(surface, flame_color, (x1, y1), (x2_offset, y2_offset), 4 - j)
        
        elif "inferno_wave" in effects:
            # 炼狱波动：火焰波纹
            # 波纹（4层）
            for i in range(4):
                wave_radius = size//6 + i * size//8
                alpha = 200 - i * 40
                # 火焰色渐变
                wave_color = (255, 120 - i * 20, 0)
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*wave_color, alpha), (size, size), wave_radius, 3)
                surface.blit(temp_surf, (x - size, y - size))
            # 中心
            pygame.draw.circle(surface, (255, 255, 0), (center_x, center_y), size//8)
        
        elif "rose_petal" in effects:
            # 血玫瑰刺：玫瑰花瓣
            # 花瓣（5瓣）
            for i in range(5):
                angle = (i * 72) * 3.14159 / 180
                petal_x = center_x + int(size//3 * math.cos(angle))
                petal_y = center_y + int(size//3 * math.sin(angle))
                # 心形花瓣
                petal_rect = pygame.Rect(0, 0, size//4, size//3)
                petal_rect.center = (petal_x, petal_y)
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.ellipse(temp_surf, (*color, 200), 
                                  (petal_x - x - size//8 + size, petal_y - y - size//6 + size, size//4, size//3))
                surface.blit(temp_surf, (x - size, y - size))
                pygame.draw.ellipse(surface, (180, 30, 60), petal_rect, 1)
            # 花心
            pygame.draw.circle(surface, (150, 0, 40), (center_x, center_y), size//10)
        
        elif "thorn_spike" in effects:
            # 尖刺荆棘：尖刺放射
            # 中心
            pygame.draw.circle(surface, (150, 30, 60), (center_x, center_y), size//8)
            # 荆棘刺（12根）
            for i in range(12):
                angle = (i * 30) * 3.14159 / 180
                thorn_length = size//2 + (i % 3) * size//12
                x1 = center_x + int(size//8 * math.cos(angle))
                y1 = center_y + int(size//8 * math.sin(angle))
                x2 = center_x + int(thorn_length * math.cos(angle))
                y2 = center_y + int(thorn_length * math.sin(angle))
                # 尖刺（三角形）
                thorn_base = size // 15
                perp_angle = angle + 1.5708
                p1 = (x1 + int(thorn_base * math.cos(perp_angle)), 
                     y1 + int(thorn_base * math.sin(perp_angle)))
                p2 = (x1 - int(thorn_base * math.cos(perp_angle)), 
                     y1 - int(thorn_base * math.sin(perp_angle)))
                thorn = [(x2, y2), p1, p2]
                pygame.draw.polygon(surface, color, thorn)
                pygame.draw.polygon(surface, (200, 50, 80), thorn, 1)
        
        elif "dragon_breath" in effects:
            # 血龙吐息：龙形火焰
            # 龙头轮廓（简化）
            head = [
                (center_x - size//4, center_y - size//4),
                (center_x, center_y - size//2),
                (center_x + size//4, center_y - size//4),
                (center_x + size//6, center_y),
                (center_x - size//6, center_y)
            ]
            pygame.draw.polygon(surface, (150, 0, 0), head)
            pygame.draw.polygon(surface, color, head, 2)
            # 龙眼
            pygame.draw.circle(surface, (255, 200, 0), (center_x - size//12, center_y - size//6), size//20)
            pygame.draw.circle(surface, (255, 200, 0), (center_x + size//12, center_y - size//6), size//20)
            # 龙息火焰
            breath_points = [
                (center_x, center_y),
                (center_x - size//8, center_y + size//4),
                (center_x + size//12, center_y + size//3),
                (center_x - size//15, center_y + size//2)
            ]
            pygame.draw.lines(surface, (255, 100, 0), False, breath_points, 8)
            pygame.draw.lines(surface, (255, 200, 0), False, breath_points, 4)
        
        elif "blood_scale" in effects:
            # 血色龙鳞：龙鳞纹理
            # 鳞片（菱形阵列）
            for row in range(3):
                for col in range(3):
                    scale_x = center_x + (col - 1) * size//4
                    scale_y = center_y + (row - 1) * size//4
                    scale = [
                        (scale_x, scale_y - size//12),
                        (scale_x + size//15, scale_y),
                        (scale_x, scale_y + size//12),
                        (scale_x - size//15, scale_y)
                    ]
                    temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    pygame.draw.polygon(temp_surf, (*color, 180), 
                                      [(x - center_x + size, y - center_y + size) for x, y in scale])
                    surface.blit(temp_surf, (x - size, y - size))
                    pygame.draw.polygon(surface, (180, 0, 0), scale, 1)
        
        elif "bat_swarm" in effects:
            # 吸血蝠群：蝙蝠群飞
            # 蝙蝠（5只）
            for i in range(5):
                angle = (i * 72 + pygame.time.get_ticks() / 50) * 3.14159 / 180
                bat_x = center_x + int(size//3 * math.cos(angle))
                bat_y = center_y + int(size//3 * math.sin(angle))
                # 蝙蝠翅膀（简化V形）
                wing_span = size // 8
                left_wing = [
                    (bat_x, bat_y),
                    (bat_x - wing_span, bat_y - wing_span//2),
                    (bat_x - wing_span//2, bat_y + wing_span//4)
                ]
                right_wing = [
                    (bat_x, bat_y),
                    (bat_x + wing_span, bat_y - wing_span//2),
                    (bat_x + wing_span//2, bat_y + wing_span//4)
                ]
                pygame.draw.polygon(surface, color, left_wing)
                pygame.draw.polygon(surface, color, right_wing)
                # 蝙蝠身体
                pygame.draw.circle(surface, (80, 0, 40), (bat_x, bat_y), size//25)
        
        elif "vampire_drain" in effects:
            # 吸血吸取：血液流动
            # 中心血核
            pygame.draw.circle(surface, (120, 0, 50), (center_x, center_y), size//6)
            # 血液流（螺旋吸入）
            for i in range(8):
                angle = (i * 45 + pygame.time.get_ticks() / 20) * 3.14159 / 180
                radius_start = size // 2
                radius_end = size // 6
                # 流动轨迹
                flow_points = []
                for j in range(8):
                    progress = j / 8
                    radius = radius_start + (radius_end - radius_start) * progress
                    px = center_x + int(radius * math.cos(angle + progress * 3.14159))
                    py = center_y + int(radius * math.sin(angle + progress * 3.14159))
                    flow_points.append((px, py))
                if len(flow_points) > 1:
                    pygame.draw.lines(surface, color, False, flow_points, 2)
        
        # ========== Stalker 子弹形状 ==========
        elif "plasma_disc" in effects or "heat_trail" in effects:
            # 铁血飞盘：旋转飞盘+等离子
            # 飞盘主体（圆形+锯齿边）
            pygame.draw.circle(surface, (180, 0, 220), (center_x, center_y), size//3)
            # 锯齿边缘（8个三角）
            for i in range(8):
                angle = (i * 45 + pygame.time.get_ticks() / 20) * 3.14159 / 180
                x1 = center_x + int(size//3 * math.cos(angle))
                y1 = center_y + int(size//3 * math.sin(angle))
                x2 = center_x + int(size//2 * math.cos(angle))
                y2 = center_y + int(size//2 * math.sin(angle))
                # 三角锯齿
                angle_left = angle - 0.3
                angle_right = angle + 0.3
                p1 = (x1 + int(size//8 * math.cos(angle_left)), y1 + int(size//8 * math.sin(angle_left)))
                p2 = (x1 + int(size//8 * math.cos(angle_right)), y1 + int(size//8 * math.sin(angle_right)))
                pygame.draw.polygon(surface, color, [(x2, y2), p1, p2])
            # 中心等离子核
            pygame.draw.circle(surface, (255, 0, 255), (center_x, center_y), size//6)
            # 热能轨迹
            for i in range(3):
                trail_radius = size//3 + i * size//8
                alpha = 180 - i * 50
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), trail_radius, 2)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "acid_drop" in effects or "corrosive" in effects:
            # 异形酸液：液滴形状+腐蚀效果
            # 主液滴（泪滴形）
            drop_points = [
                (center_x, center_y - size//2),
                (center_x + size//3, center_y - size//6),
                (center_x + size//4, center_y + size//4),
                (center_x, center_y + size//2),
                (center_x - size//4, center_y + size//4),
                (center_x - size//3, center_y - size//6)
            ]
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surf, (*color, 220), 
                              [(x - center_x + size, y - center_y + size) for x, y in drop_points])
            surface.blit(temp_surf, (x - size, y - size))
            pygame.draw.polygon(surface, (150, 200, 0), drop_points, 2)
            # 腐蚀气泡
            import random
            random.seed(123)
            for _ in range(5):
                bubble_x = center_x + random.randint(-size//4, size//4)
                bubble_y = center_y + random.randint(-size//4, size//4)
                bubble_size = random.randint(2, 5)
                pygame.draw.circle(surface, (200, 255, 0), (bubble_x, bubble_y), bubble_size)
                pygame.draw.circle(surface, color, (bubble_x, bubble_y), bubble_size, 1)
        
        elif "color_shift" in effects or "stealth_flicker" in effects:
            # 变色迷彩：色彩变换效果
            # 主体（渐变色圆形）
            shift_colors = [(120, 180, 120), (80, 140, 180), (140, 120, 160), (100, 160, 100)]
            time_index = int(pygame.time.get_ticks() / 200) % len(shift_colors)
            current_color = shift_colors[time_index]
            # 多层渐变
            for i in range(4):
                radius = size//2 - i * size//10
                alpha = 220 - i * 40
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                blend_color = tuple(int(c * (1 - i * 0.2)) for c in current_color)
                pygame.draw.circle(temp_surf, (*blend_color, alpha), (size, size), radius)
                surface.blit(temp_surf, (x - size, y - size))
            # 隐形闪烁边缘
            for i in range(6):
                angle = (i * 60 + pygame.time.get_ticks() / 50) * 3.14159 / 180
                px = center_x + int(size//2.5 * math.cos(angle))
                py = center_y + int(size//2.5 * math.sin(angle))
                alpha = int(200 * abs(math.sin(pygame.time.get_ticks() / 100 + i)))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*current_color, alpha), (px - x + size, py - y + size), size//15)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "spore_burst" in effects or "swarm_split" in effects:
            # 虫群孢子：孢子扩散
            # 主孢子囊
            pygame.draw.circle(surface, (100, 140, 60), (center_x, center_y), size//4)
            pygame.draw.circle(surface, color, (center_x, center_y), size//4, 2)
            # 裂变纹理
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                x1 = center_x
                y1 = center_y
                x2 = center_x + int(size//4 * math.cos(angle))
                y2 = center_y + int(size//4 * math.sin(angle))
                pygame.draw.line(surface, (60, 100, 30), (x1, y1), (x2, y2), 2)
            # 扩散孢子（12个小孢子）
            for i in range(12):
                angle = (i * 30 + pygame.time.get_ticks() / 50) * 3.14159 / 180
                radius = size//2 + int(size//8 * math.sin(pygame.time.get_ticks() / 100 + i))
                spore_x = center_x + int(radius * math.cos(angle))
                spore_y = center_y + int(radius * math.sin(angle))
                spore_size = size // 20
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, 180), (spore_x - x + size, spore_y - y + size), spore_size)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "drone_tracking" in effects or "scanner_lock" in effects:
            # 追踪无人机：机械无人机形状
            # 无人机主体（十字形）
            # 横臂
            pygame.draw.rect(surface, (220, 170, 0), 
                           (center_x - size//2, center_y - size//12, size, size//6))
            # 竖臂
            pygame.draw.rect(surface, (220, 170, 0), 
                           (center_x - size//12, center_y - size//2, size//6, size))
            # 中心核心
            pygame.draw.circle(surface, (255, 200, 0), (center_x, center_y), size//6)
            pygame.draw.circle(surface, (200, 150, 0), (center_x, center_y), size//8)
            # 四个旋翼（圆圈）
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                rotor_x = center_x + int(size//2.5 * math.cos(angle))
                rotor_y = center_y + int(size//2.5 * math.sin(angle))
                pygame.draw.circle(surface, (180, 140, 0), (rotor_x, rotor_y), size//10, 2)
            # 扫描锁定线
            scan_angle = (pygame.time.get_ticks() / 20) * 3.14159 / 180
            x1 = center_x + int(size//6 * math.cos(scan_angle))
            y1 = center_y + int(size//6 * math.sin(scan_angle))
            x2 = center_x + int(size//1.8 * math.cos(scan_angle))
            y2 = center_y + int(size//1.8 * math.sin(scan_angle))
            pygame.draw.line(surface, (255, 0, 0), (x1, y1), (x2, y2), 2)
        
        elif "void_phase" in effects or "dimension_shift" in effects:
            # 虚空潜行：次元裂隙
            # 虚空裂隙（不规则裂痕）
            rift_points = [
                (center_x, center_y - size//2),
                (center_x - size//8, center_y - size//4),
                (center_x + size//10, center_y),
                (center_x - size//12, center_y + size//4),
                (center_x, center_y + size//2)
            ]
            pygame.draw.lines(surface, (150, 0, 200), False, rift_points, 4)
            pygame.draw.lines(surface, (200, 100, 255), False, rift_points, 2)
            # 虚空漩涡
            for i in range(4):
                radius = size//4 + i * size//10
                alpha = 180 - i * 40
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), radius, 2)
                surface.blit(temp_surf, (x - size, y - size))
            # 次元碎片
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                shard_x = center_x + int(size//3 * math.cos(angle))
                shard_y = center_y + int(size//3 * math.sin(angle))
                shard = [
                    (shard_x, shard_y - size//15),
                    (shard_x + size//20, shard_y + size//15),
                    (shard_x - size//20, shard_y + size//15)
                ]
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.polygon(temp_surf, (*color, 200), 
                                  [(x - center_x + size, y - center_y + size) for x, y in shard])
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "xenomorph_egg" in effects or "hive_spawn" in effects:
            # 异形卵巢：卵形+触手
            # 卵体（椭圆）
            egg_rect = pygame.Rect(center_x - size//3, center_y - size//2, size*2//3, size)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.ellipse(temp_surf, (*color, 220), 
                              (egg_rect.x - x + size, egg_rect.y - y + size, egg_rect.width, egg_rect.height))
            surface.blit(temp_surf, (x - size, y - size))
            pygame.draw.ellipse(surface, (60, 140, 60), egg_rect, 3)
            # 卵纹理（竖线）
            for i in range(5):
                line_x = center_x - size//4 + i * size//8
                pygame.draw.line(surface, (40, 100, 40), 
                               (line_x, center_y - size//2), 
                               (line_x, center_y + size//2), 1)
            # 顶部裂口（张开）
            opening = [
                (center_x - size//6, center_y - size//2),
                (center_x - size//4, center_y - size//1.5),
                (center_x, center_y - size//1.8),
                (center_x + size//4, center_y - size//1.5),
                (center_x + size//6, center_y - size//2)
            ]
            pygame.draw.lines(surface, (80, 180, 80), False, opening, 2)
            # 触手（4条）
            for i in range(4):
                angle = (i * 90 + 45) * 3.14159 / 180
                tentacle = []
                for j in range(5):
                    radius = size//3 + j * size//15
                    wave_offset = int(size//20 * math.sin(pygame.time.get_ticks() / 100 + i + j))
                    tx = center_x + int(radius * math.cos(angle)) + wave_offset
                    ty = center_y + int(radius * math.sin(angle))
                    tentacle.append((tx, ty))
                if len(tentacle) > 1:
                    pygame.draw.lines(surface, (60, 120, 60), False, tentacle, 2)
        
        # ========== Gaia 子弹形状 ==========
        elif "seed_spiral" in effects or "leaf_swirl" in effects:
            # 森林之种：种子螺旋+叶片
            # 种子核心
            pygame.draw.circle(surface, (100, 200, 100), (center_x, center_y), size//6)
            pygame.draw.circle(surface, color, (center_x, center_y), size//8)
            # 螺旋叶片（8片）
            for i in range(8):
                angle = (i * 45 + pygame.time.get_ticks() / 30) * 3.14159 / 180
                leaf_x = center_x + int(size//3 * math.cos(angle))
                leaf_y = center_y + int(size//3 * math.sin(angle))
                # 叶片形状（椭圆）
                leaf_rect = pygame.Rect(leaf_x - size//10, leaf_y - size//6, size//5, size//3)
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.ellipse(temp_surf, (*color, 200), 
                                  (leaf_rect.x - x + size, leaf_rect.y - y + size, leaf_rect.width, leaf_rect.height))
                surface.blit(temp_surf, (x - size, y - size))
                pygame.draw.ellipse(surface, (100, 220, 100), leaf_rect, 1)
        
        elif "crystal_facet" in effects or "gem_sparkle" in effects:
            # 水晶宝石：多面晶体
            # 主晶体（六边形）
            crystal_points = []
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                px = center_x + int(size//2 * math.cos(angle))
                py = center_y + int(size//2 * math.sin(angle))
                crystal_points.append((px, py))
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surf, (*color, 200), 
                              [(x - center_x + size, y - center_y + size) for x, y in crystal_points])
            surface.blit(temp_surf, (x - size, y - size))
            pygame.draw.polygon(surface, (0, 255, 220), crystal_points, 2)
            # 内部切面
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                x1 = center_x
                y1 = center_y
                x2 = center_x + int(size//2 * math.cos(angle))
                y2 = center_y + int(size//2 * math.sin(angle))
                pygame.draw.line(surface, (0, 220, 200), (x1, y1), (x2, y2), 1)
            # 宝石闪光
            for i in range(4):
                angle = (i * 90 + pygame.time.get_ticks() / 50) * 3.14159 / 180
                sparkle_x = center_x + int(size//3 * math.cos(angle))
                sparkle_y = center_y + int(size//3 * math.sin(angle))
                pygame.draw.circle(surface, (255, 255, 255), (sparkle_x, sparkle_y), size//20)
        
        elif "vine_coil" in effects or "thorn_barb" in effects:
            # 荆棘藤蔓：盘绕藤蔓+尖刺
            # 藤蔓主体（螺旋）
            vine_points = []
            for i in range(20):
                angle = (i * 18) * 3.14159 / 180
                radius = size//6 + (i / 20) * size//3
                vx = center_x + int(radius * math.cos(angle))
                vy = center_y + int(radius * math.sin(angle))
                vine_points.append((vx, vy))
            if len(vine_points) > 1:
                pygame.draw.lines(surface, (120, 160, 60), False, vine_points, 4)
                pygame.draw.lines(surface, color, False, vine_points, 2)
            # 荆棘刺（沿藤蔓）
            for i in range(0, len(vine_points), 4):
                if i < len(vine_points):
                    vx, vy = vine_points[i]
                    # 计算刺的方向
                    if i < len(vine_points) - 1:
                        next_x, next_y = vine_points[i + 1]
                        perp_angle = math.atan2(next_y - vy, next_x - vx) + 1.5708
                    else:
                        perp_angle = 0
                    thorn_x = vx + int(size//8 * math.cos(perp_angle))
                    thorn_y = vy + int(size//8 * math.sin(perp_angle))
                    # 刺（三角形）
                    thorn = [
                        (thorn_x, thorn_y),
                        (vx + int(size//15 * math.cos(perp_angle + 0.5)), vy + int(size//15 * math.sin(perp_angle + 0.5))),
                        (vx + int(size//15 * math.cos(perp_angle - 0.5)), vy + int(size//15 * math.sin(perp_angle - 0.5)))
                    ]
                    pygame.draw.polygon(surface, (140, 180, 70), thorn)
        
        elif "petal_storm" in effects or "bloom_burst" in effects:
            # 花瓣风暴：飞舞花瓣
            # 花心
            pygame.draw.circle(surface, (255, 200, 0), (center_x, center_y), size//8)
            # 飞舞花瓣（12片）
            for i in range(12):
                angle = (i * 30 + pygame.time.get_ticks() / 40) * 3.14159 / 180
                radius = size//4 + int(size//6 * math.sin(pygame.time.get_ticks() / 80 + i))
                petal_x = center_x + int(radius * math.cos(angle))
                petal_y = center_y + int(radius * math.sin(angle))
                # 花瓣（椭圆）
                petal_rect = pygame.Rect(petal_x - size//12, petal_y - size//8, size//6, size//4)
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.ellipse(temp_surf, (*color, 220), 
                                  (petal_rect.x - x + size, petal_rect.y - y + size, petal_rect.width, petal_rect.height))
                surface.blit(temp_surf, (x - size, y - size))
                pygame.draw.ellipse(surface, (255, 180, 220), petal_rect, 1)
        
        elif "rock_boulder" in effects or "earth_crack" in effects:
            # 大地之石：岩石形状
            # 岩石（不规则多边形）
            rock_points = [
                (center_x, center_y - size//2),
                (center_x + size//3, center_y - size//4),
                (center_x + size//2, center_y + size//6),
                (center_x + size//4, center_y + size//2),
                (center_x - size//4, center_y + size//2),
                (center_x - size//2, center_y + size//6),
                (center_x - size//3, center_y - size//4)
            ]
            pygame.draw.polygon(surface, (140, 120, 80), rock_points)
            pygame.draw.polygon(surface, color, rock_points, 3)
            # 岩石裂纹
            crack_lines = [
                [(center_x - size//6, center_y - size//4), (center_x + size//8, center_y)],
                [(center_x + size//10, center_y - size//6), (center_x - size//12, center_y + size//6)],
                [(center_x - size//8, center_y + size//8), (center_x + size//6, center_y + size//4)]
            ]
            for crack in crack_lines:
                pygame.draw.line(surface, (80, 60, 40), crack[0], crack[1], 2)
        
        elif "mushroom_cap" in effects or "spore_cloud" in effects:
            # 魔法蘑菇：蘑菇形状+孢子云
            # 蘑菇伞盖（半圆）
            cap_rect = pygame.Rect(center_x - size//2, center_y - size//2, size, size//1.5)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.ellipse(temp_surf, (*color, 220), 
                              (cap_rect.x - x + size, cap_rect.y - y + size, cap_rect.width, cap_rect.height))
            surface.blit(temp_surf, (x - size, y - size))
            pygame.draw.arc(surface, (220, 120, 255), cap_rect, 0, 3.14159, 3)
            # 蘑菇柄
            stalk_rect = (center_x - size//8, center_y, size//4, size//2)
            pygame.draw.rect(surface, (180, 150, 200), stalk_rect)
            # 蘑菇斑点
            import random
            random.seed(456)
            for _ in range(6):
                spot_x = center_x + random.randint(-size//3, size//3)
                spot_y = center_y - size//2 + random.randint(0, size//4)
                spot_size = random.randint(size//20, size//12)
                pygame.draw.circle(surface, (255, 200, 255), (spot_x, spot_y), spot_size)
            # 孢子云
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                cloud_x = center_x + int(size//1.5 * math.cos(angle))
                cloud_y = center_y + int(size//1.5 * math.sin(angle))
                cloud_size = size // 15
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, 150), (cloud_x - x + size, cloud_y - y + size), cloud_size)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "tree_rings" in effects or "ancient_runes" in effects:
            # 古树之心：年轮+符文
            # 树心（同心圆年轮）
            for i in range(5):
                ring_radius = size//6 + i * size//12
                pygame.draw.circle(surface, (130 - i * 10, 90 - i * 8, 40), (center_x, center_y), ring_radius, 2)
            # 中心
            pygame.draw.circle(surface, (180, 120, 60), (center_x, center_y), size//8)
            # 古代符文（8个符号）
            rune_symbols = []
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                rune_x = center_x + int(size//2.5 * math.cos(angle))
                rune_y = center_y + int(size//2.5 * math.sin(angle))
                # 简单符文形状（竖线+横线）
                pygame.draw.line(surface, (200, 150, 80), 
                               (rune_x, rune_y - size//15), 
                               (rune_x, rune_y + size//15), 2)
                pygame.draw.line(surface, (200, 150, 80), 
                               (rune_x - size//20, rune_y - size//20), 
                               (rune_x + size//20, rune_y - size//20), 2)
        
        # ========== Weaver 子弹形状 ==========
        elif "web_net" in effects or "spider_silk" in effects:
            # 蛛网陷阱：蛛网形状
            # 中心蛛网节点
            pygame.draw.circle(surface, (220, 220, 220), (center_x, center_y), size//8)
            pygame.draw.circle(surface, color, (center_x, center_y), size//10)
            # 蛛网放射线（8条）
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                x1 = center_x + int(size//8 * math.cos(angle))
                y1 = center_y + int(size//8 * math.sin(angle))
                x2 = center_x + int(size//2 * math.cos(angle))
                y2 = center_y + int(size//2 * math.sin(angle))
                pygame.draw.line(surface, (200, 200, 200), (x1, y1), (x2, y2), 2)
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 1)
            # 蛛网环圈（3层）
            for i in range(3):
                ring_radius = size//4 + i * size//8
                # 绘制八边形环
                web_points = []
                for j in range(8):
                    angle = (j * 45) * 3.14159 / 180
                    px = center_x + int(ring_radius * math.cos(angle))
                    py = center_y + int(ring_radius * math.sin(angle))
                    web_points.append((px, py))
                if len(web_points) > 1:
                    pygame.draw.lines(surface, (180, 180, 180), True, web_points, 1)
        
        elif "phase_shift" in effects or "dimension_warp" in effects:
            # 相位穿梭：重影效果
            # 主体（多层重影）
            shift_offsets = [(0, 0), (3, -2), (6, -4), (-3, -2)]
            for i, (dx, dy) in enumerate(shift_offsets):
                alpha = 220 - i * 40
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                # 菱形
                diamond = [
                    (size + dx, size//2 + dy),
                    (size*3//2 + dx, size + dy),
                    (size + dx, size*3//2 + dy),
                    (size//2 + dx, size + dy)
                ]
                pygame.draw.polygon(temp_surf, (*color, alpha), diamond)
                surface.blit(temp_surf, (x - size, y - size))
                if i == 0:
                    pygame.draw.polygon(surface, (200, 200, 220), 
                                      [(px + x - size, py + y - size) for px, py in diamond], 2)
            # 相位粒子
            for i in range(6):
                angle = (i * 60 + pygame.time.get_ticks() / 50) * 3.14159 / 180
                px = center_x + int(size//3 * math.cos(angle))
                py = center_y + int(size//3 * math.sin(angle))
                pygame.draw.circle(surface, (180, 180, 220), (px, py), size//20)
        
        elif "void_cocoon" in effects or "space_lock" in effects:
            # 虚空之茧：茧形封锁
            # 茧外壳（椭圆）
            cocoon_rect = pygame.Rect(center_x - size//3, center_y - size//2, size*2//3, size)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.ellipse(temp_surf, (*color, 200), 
                              (cocoon_rect.x - x + size, cocoon_rect.y - y + size, cocoon_rect.width, cocoon_rect.height))
            surface.blit(temp_surf, (x - size, y - size))
            pygame.draw.ellipse(surface, (120, 120, 180), cocoon_rect, 3)
            # 束缚线条（竖线）
            for i in range(6):
                line_x = center_x - size//4 + i * size//10
                pygame.draw.line(surface, (80, 80, 130), 
                               (line_x, center_y - size//2), 
                               (line_x, center_y + size//2), 2)
            # 虚空核心
            pygame.draw.circle(surface, (50, 50, 100), (center_x, center_y), size//8)
            # 空间扭曲环
            for i in range(3):
                wave_radius = size//6 + i * size//10
                alpha = 180 - i * 50
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), wave_radius, 2)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "time_thread" in effects or "slow_field" in effects:
            # 时间丝线：螺旋时钟
            # 时钟圆盘
            pygame.draw.circle(surface, (200, 200, 240), (center_x, center_y), size//3, 3)
            pygame.draw.circle(surface, color, (center_x, center_y), size//3, 1)
            # 时钟刻度（12个）
            for i in range(12):
                angle = (i * 30 - 90) * 3.14159 / 180
                x1 = center_x + int(size//4 * math.cos(angle))
                y1 = center_y + int(size//4 * math.sin(angle))
                x2 = center_x + int(size//3 * math.cos(angle))
                y2 = center_y + int(size//3 * math.sin(angle))
                width = 3 if i % 3 == 0 else 1
                pygame.draw.line(surface, (160, 160, 200), (x1, y1), (x2, y2), width)
            # 时针（减速效果）
            time_angle = (pygame.time.get_ticks() / 100) * 3.14159 / 180
            needle_x = center_x + int(size//4 * math.cos(time_angle))
            needle_y = center_y + int(size//4 * math.sin(time_angle))
            pygame.draw.line(surface, (100, 100, 150), (center_x, center_y), (needle_x, needle_y), 3)
            # 时间波纹
            for i in range(2):
                wave_r = size//2 + i * size//6 + int(size//10 * math.sin(pygame.time.get_ticks() / 100))
                alpha = 150 - i * 50
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), wave_r, 2)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "quantum_tangle" in effects or "entangle_web" in effects:
            # 量子纠缠：量子粒子连接
            # 中心量子核
            pygame.draw.circle(surface, (150, 220, 255), (center_x, center_y), size//6)
            pygame.draw.circle(surface, color, (center_x, center_y), size//8)
            # 量子粒子（6个）
            particles = []
            for i in range(6):
                angle = (i * 60 + pygame.time.get_ticks() / 40) * 3.14159 / 180
                px = center_x + int(size//2.5 * math.cos(angle))
                py = center_y + int(size//2.5 * math.sin(angle))
                particles.append((px, py))
                # 粒子球
                pygame.draw.circle(surface, (100, 180, 255), (px, py), size//12)
                pygame.draw.circle(surface, color, (px, py), size//15)
            # 纠缠连线（连接所有粒子）
            for i in range(len(particles)):
                for j in range(i + 1, len(particles)):
                    alpha = 150
                    temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    p1 = (particles[i][0] - x + size, particles[i][1] - y + size)
                    p2 = (particles[j][0] - x + size, particles[j][1] - y + size)
                    pygame.draw.line(temp_surf, (*color, alpha), p1, p2, 1)
                    surface.blit(temp_surf, (x - size, y - size))
            # 纠缠波动
            for px, py in particles:
                pulse_size = int(size//15 * (1 + 0.3 * math.sin(pygame.time.get_ticks() / 80)))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, 100), (px - x + size, py - y + size), pulse_size)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "shadow_weave" in effects or "dark_web" in effects:
            # 暗影编织：黑暗蛛网
            # 暗影中心
            pygame.draw.circle(surface, (30, 30, 60), (center_x, center_y), size//5)
            pygame.draw.circle(surface, color, (center_x, center_y), size//6)
            # 暗影射线（12条）
            for i in range(12):
                angle = (i * 30) * 3.14159 / 180
                # 不规则长度
                length = size//2 + (i % 3) * size//8
                x1 = center_x + int(size//6 * math.cos(angle))
                y1 = center_y + int(size//6 * math.sin(angle))
                x2 = center_x + int(length * math.cos(angle))
                y2 = center_y + int(length * math.sin(angle))
                # 渐变黑影
                for j in range(3):
                    alpha = 180 - j * 50
                    temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    offset = j * 2
                    pygame.draw.line(temp_surf, (*color, alpha), 
                                   (x1 - x + size + offset, y1 - y + size + offset),
                                   (x2 - x + size + offset, y2 - y + size + offset), 2)
                    surface.blit(temp_surf, (x - size, y - size))
            # 暗影粒子
            import random
            random.seed(789)
            for _ in range(8):
                sx = center_x + random.randint(-size//2, size//2)
                sy = center_y + random.randint(-size//2, size//2)
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (30, 30, 60, 150), (sx - x + size, sy - y + size), size//20)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "cosmic_web" in effects or "fate_thread" in effects:
            # 宇宙丝线：星系网络
            # 宇宙中心
            pygame.draw.circle(surface, (120, 170, 220), (center_x, center_y), size//6)
            pygame.draw.circle(surface, color, (center_x, center_y), size//8)
            # 星系节点（8个）
            nodes = []
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                nx = center_x + int(size//2.5 * math.cos(angle))
                ny = center_y + int(size//2.5 * math.sin(angle))
                nodes.append((nx, ny))
                # 星系节点
                pygame.draw.circle(surface, (80, 130, 180), (nx, ny), size//15)
                # 星光闪烁
                for j in range(4):
                    star_angle = (j * 90) * 3.14159 / 180
                    sx = nx + int(size//10 * math.cos(star_angle))
                    sy = ny + int(size//10 * math.sin(star_angle))
                    pygame.draw.line(surface, (150, 200, 255), (nx, ny), (sx, sy), 1)
            # 命运之线连接
            for i, (nx, ny) in enumerate(nodes):
                # 连接到中心
                pygame.draw.line(surface, (100, 150, 200), (center_x, center_y), (nx, ny), 2)
                # 连接到相邻节点
                next_node = nodes[(i + 1) % len(nodes)]
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, (*color, 150), 
                               (nx - x + size, ny - y + size),
                               (next_node[0] - x + size, next_node[1] - y + size), 1)
                surface.blit(temp_surf, (x - size, y - size))
        
        # ========== Solar 子弹形状 ==========
        elif "solar_flare" in effects or "light_burst" in effects:
            # 太阳耀斑：光芒爆发
            # 太阳核心
            pygame.draw.circle(surface, (255, 255, 100), (center_x, center_y), size//5)
            pygame.draw.circle(surface, color, (center_x, center_y), size//6)
            # 耀斑射线（16条）
            for i in range(16):
                angle = (i * 22.5) * 3.14159 / 180
                # 交替长度
                length = size//2 if i % 2 == 0 else size//1.5
                x1 = center_x + int(size//6 * math.cos(angle))
                y1 = center_y + int(size//6 * math.sin(angle))
                x2 = center_x + int(length * math.cos(angle))
                y2 = center_y + int(length * math.sin(angle))
                # 渐变光芒
                pygame.draw.line(surface, (255, 220, 0), (x1, y1), (x2, y2), 3)
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 1)
            # 光晕
            for i in range(3):
                halo_r = size//4 + i * size//8
                alpha = 180 - i * 50
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), halo_r)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "corona_ring" in effects or "plasma_loop" in effects:
            # 日冕光环：等离子环
            # 中心
            pygame.draw.circle(surface, (255, 200, 0), (center_x, center_y), size//6)
            # 日冕环（3层）
            for i in range(3):
                ring_r = size//3 + i * size//8
                ring_color = (255, 180 - i * 30, 0)
                alpha = 200 - i * 40
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*ring_color, alpha), (size, size), ring_r, 4)
                surface.blit(temp_surf, (x - size, y - size))
            # 等离子弧（4个）
            for i in range(4):
                angle = (i * 90 + pygame.time.get_ticks() / 50) * 3.14159 / 180
                arc_start = angle - 0.5
                arc_end = angle + 0.5
                arc_points = []
                for a in range(10):
                    arc_angle = arc_start + (arc_end - arc_start) * a / 10
                    px = center_x + int(size//2 * math.cos(arc_angle))
                    py = center_y + int(size//2 * math.sin(arc_angle))
                    arc_points.append((px, py))
                if len(arc_points) > 1:
                    pygame.draw.lines(surface, (255, 150, 0), False, arc_points, 3)
        
        elif "prominence_jet" in effects or "flame_tongue" in effects:
            # 日珥喷发：火焰喷射
            # 太阳主体
            pygame.draw.circle(surface, (255, 120, 0), (center_x, center_y), size//4)
            # 火焰喷射（6条）
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                # 火焰轨迹
                flame_points = []
                for j in range(8):
                    radius = size//4 + j * size//15
                    wave_offset = int(size//12 * math.sin(pygame.time.get_ticks() / 100 + i + j))
                    fx = center_x + int(radius * math.cos(angle)) + wave_offset
                    fy = center_y + int(radius * math.sin(angle))
                    flame_points.append((fx, fy))
                if len(flame_points) > 1:
                    # 多层火焰颜色
                    pygame.draw.lines(surface, (255, 200, 0), False, flame_points, 5)
                    pygame.draw.lines(surface, (255, 100, 0), False, flame_points, 3)
                    pygame.draw.lines(surface, color, False, flame_points, 1)
        
        elif "sunspot_vortex" in effects or "magnetic_storm" in effects:
            # 太阳黑子：磁场漩涡
            # 黑子核心
            pygame.draw.circle(surface, (100, 50, 0), (center_x, center_y), size//5)
            pygame.draw.circle(surface, color, (center_x, center_y), size//6)
            # 磁力线漩涡（3条螺旋）
            for arm in range(3):
                spiral_points = []
                arm_offset = arm * 120
                for i in range(15):
                    angle = (i * 24 + arm_offset + pygame.time.get_ticks() / 30) * 3.14159 / 180
                    radius = size//8 + i * size//30
                    sx = center_x + int(radius * math.cos(angle))
                    sy = center_y + int(radius * math.sin(angle))
                    spiral_points.append((sx, sy))
                if len(spiral_points) > 1:
                    pygame.draw.lines(surface, (255, 150, 0), False, spiral_points, 3)
                    pygame.draw.lines(surface, (200, 80, 0), False, spiral_points, 1)
            # 磁暴环
            for i in range(2):
                storm_r = size//3 + i * size//6
                alpha = 160 - i * 60
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (255, 100, 0, alpha), (size, size), storm_r, 3)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "fusion_core" in effects or "nuclear_pulse" in effects:
            # 核聚变核：聚变反应
            # 聚变核心（亮白）
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//8)
            pygame.draw.circle(surface, (255, 255, 200), (center_x, center_y), size//6)
            pygame.draw.circle(surface, color, (center_x, center_y), size//5)
            # 能量环（脉冲扩散）
            pulse_phase = (pygame.time.get_ticks() / 50) % 100 / 100
            for i in range(4):
                pulse_r = int((size//4 + i * size//6) * (1 + pulse_phase * 0.5))
                alpha = int((200 - i * 40) * (1 - pulse_phase))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (255, 255, 100, alpha), (size, size), pulse_r, 3)
                surface.blit(temp_surf, (x - size, y - size))
            # 聚变粒子
            for i in range(8):
                angle = (i * 45 + pygame.time.get_ticks() / 20) * 3.14159 / 180
                particle_r = size//3
                px = center_x + int(particle_r * math.cos(angle))
                py = center_y + int(particle_r * math.sin(angle))
                pygame.draw.circle(surface, (255, 255, 150), (px, py), size//20)
        
        elif "photon_stream" in effects or "light_particle" in effects:
            # 光子流束：光粒子流
            # 光源核心
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//8)
            pygame.draw.circle(surface, color, (center_x, center_y), size//10)
            # 光子粒子流（螺旋）
            for stream in range(4):
                stream_offset = stream * 90
                for i in range(12):
                    angle = (i * 30 + stream_offset + pygame.time.get_ticks() / 30) * 3.14159 / 180
                    radius = size//6 + i * size//30
                    px = center_x + int(radius * math.cos(angle))
                    py = center_y + int(radius * math.sin(angle))
                    particle_size = size//15 - i // 4
                    if particle_size > 0:
                        pygame.draw.circle(surface, (255, 255, 220), (px, py), particle_size)
                        temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                        pygame.draw.circle(temp_surf, (*color, 200), (px - x + size, py - y + size), particle_size + 2)
                        surface.blit(temp_surf, (x - size, y - size))
        
        elif "supernova_burst" in effects or "stellar_explosion" in effects:
            # 超新星爆发：毁灭爆炸
            # 超新星核心
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//10)
            pygame.draw.circle(surface, (255, 100, 0), (center_x, center_y), size//8)
            pygame.draw.circle(surface, color, (center_x, center_y), size//6)
            # 爆炸波（3层）
            explosion_phase = (pygame.time.get_ticks() / 40) % 100 / 100
            for i in range(3):
                blast_r = int((size//3 + i * size//5) * (1 + explosion_phase * 0.8))
                alpha = int((220 - i * 60) * (1 - explosion_phase * 0.8))
                blast_color = [(255, 0, 0), (255, 100, 0), (255, 200, 0)][i]
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*blast_color, alpha), (size, size), blast_r, 4)
                surface.blit(temp_surf, (x - size, y - size))
            # 爆炸碎片（12个）
            for i in range(12):
                angle = (i * 30 + explosion_phase * 360) * 3.14159 / 180
                debris_r = size//2 + int(explosion_phase * size//2)
                dx = center_x + int(debris_r * math.cos(angle))
                dy = center_y + int(debris_r * math.sin(angle))
                debris_size = int(size//12 * (1 - explosion_phase * 0.5))
                if debris_size > 0:
                    pygame.draw.circle(surface, (255, 150, 0), (dx, dy), debris_size)
        
        # ========== Arbiter 子弹形状 ==========
        elif "quant_cube" in effects or "quantum_matrix" in effects:
            # 量子立方：几何量子态
            # 立方体（正方形+透视线）
            cube_size = size//2
            pygame.draw.rect(surface, color, (center_x - cube_size//2, center_y - cube_size//2, cube_size, cube_size), 3)
            # 透视立方（后面的面）
            offset = size//6
            back_rect = (center_x - cube_size//2 + offset, center_y - cube_size//2 - offset, cube_size, cube_size)
            pygame.draw.rect(surface, (150, 80, 200), back_rect, 2)
            # 连接线（透视）
            corners = [
                (center_x - cube_size//2, center_y - cube_size//2),
                (center_x + cube_size//2, center_y - cube_size//2),
                (center_x + cube_size//2, center_y + cube_size//2),
                (center_x - cube_size//2, center_y + cube_size//2)
            ]
            back_corners = [
                (center_x - cube_size//2 + offset, center_y - cube_size//2 - offset),
                (center_x + cube_size//2 + offset, center_y - cube_size//2 - offset),
                (center_x + cube_size//2 + offset, center_y + cube_size//2 - offset),
                (center_x - cube_size//2 + offset, center_y + cube_size//2 - offset)
            ]
            for i in range(4):
                pygame.draw.line(surface, (120, 60, 180), corners[i], back_corners[i], 1)
            # 量子态粒子
            for i in range(8):
                angle = (i * 45 + pygame.time.get_ticks() / 40) * 3.14159 / 180
                px = center_x + int(size//3 * math.cos(angle))
                py = center_y + int(size//3 * math.sin(angle))
                pygame.draw.circle(surface, (200, 150, 255), (px, py), size//25)
        
        elif "fractal_shard" in effects or "split_multiply" in effects:
            # 分形碎片：自相似分裂
            # 主碎片（三角形）
            main_triangle = [
                (center_x, center_y - size//2),
                (center_x - size//2, center_y + size//2),
                (center_x + size//2, center_y + size//2)
            ]
            pygame.draw.polygon(surface, color, main_triangle, 3)
            # 分形子碎片（递归三角形）
            for i in range(3):
                angle = (i * 120 + pygame.time.get_ticks() / 50) * 3.14159 / 180
                fx = center_x + int(size//3 * math.cos(angle))
                fy = center_y + int(size//3 * math.sin(angle))
                sub_triangle = [
                    (fx, fy - size//6),
                    (fx - size//6, fy + size//6),
                    (fx + size//6, fy + size//6)
                ]
                pygame.draw.polygon(surface, (180, 100, 230), sub_triangle, 2)
            # 分裂线条
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                x1 = center_x + int(size//8 * math.cos(angle))
                y1 = center_y + int(size//8 * math.sin(angle))
                x2 = center_x + int(size//2 * math.cos(angle))
                y2 = center_y + int(size//2 * math.sin(angle))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, (*color, 150), (x1 - x + size, y1 - y + size), (x2 - x + size, y2 - y + size), 1)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "tesseract" in effects or "hypercube_projection" in effects:
            # 四维超立方：高维投影
            # 内立方
            inner_size = size//3
            inner_rect = (center_x - inner_size//2, center_y - inner_size//2, inner_size, inner_size)
            pygame.draw.rect(surface, (150, 100, 220), inner_rect, 3)
            # 外立方
            outer_size = size//1.5
            outer_rect = (center_x - outer_size//2, center_y - outer_size//2, outer_size, outer_size)
            pygame.draw.rect(surface, color, outer_rect, 3)
            # 连接线（4D投影）
            inner_corners = [
                (center_x - inner_size//2, center_y - inner_size//2),
                (center_x + inner_size//2, center_y - inner_size//2),
                (center_x + inner_size//2, center_y + inner_size//2),
                (center_x - inner_size//2, center_y + inner_size//2)
            ]
            outer_corners = [
                (center_x - outer_size//2, center_y - outer_size//2),
                (center_x + outer_size//2, center_y - outer_size//2),
                (center_x + outer_size//2, center_y + outer_size//2),
                (center_x - outer_size//2, center_y + outer_size//2)
            ]
            for i in range(4):
                pygame.draw.line(surface, (180, 120, 240), inner_corners[i], outer_corners[i], 2)
            # 高维粒子
            rotation = (pygame.time.get_ticks() / 50) % 360
            for i in range(4):
                angle = (i * 90 + rotation) * 3.14159 / 180
                px = center_x + int(size//2.5 * math.cos(angle))
                py = center_y + int(size//2.5 * math.sin(angle))
                pygame.draw.circle(surface, (200, 150, 255), (px, py), size//20)
        
        elif "matrix_rain" in effects or "code_cascade" in effects:
            # 矩阵代码雨：数字瀑布
            # 背景透明黑
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.rect(temp_surf, (0, 50, 20, 180), (0, 0, size*2, size*2))
            surface.blit(temp_surf, (x - size, y - size))
            # 代码流（竖线）
            import random
            random.seed(123)
            for i in range(8):
                line_x = center_x - size//2 + i * size//4
                for j in range(6):
                    code_y = center_y - size//2 + j * size//6
                    brightness = 100 + (j * 25)
                    code_char = random.choice([0, 1])
                    char_color = (0, brightness, 50)
                    # 简单方块代表字符
                    char_size = size//20
                    pygame.draw.rect(surface, char_color, (line_x - char_size//2, code_y - char_size//2, char_size, char_size))
            # 矩阵光芒
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                x1 = center_x + int(size//6 * math.cos(angle))
                y1 = center_y + int(size//6 * math.sin(angle))
                x2 = center_x + int(size//2 * math.cos(angle))
                y2 = center_y + int(size//2 * math.sin(angle))
                pygame.draw.line(surface, (0, 255, 100), (x1, y1), (x2, y2), 2)
        
        elif "geometric_wave" in effects or "angular_ripple" in effects:
            # 几何波纹：棱角扩散
            # 中心几何体（六边形）
            hex_points = []
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                px = center_x + int(size//4 * math.cos(angle))
                py = center_y + int(size//4 * math.sin(angle))
                hex_points.append((px, py))
            pygame.draw.polygon(surface, color, hex_points, 3)
            # 波纹环（3层）
            wave_phase = (pygame.time.get_ticks() / 60) % 100 / 100
            for i in range(3):
                wave_r = size//3 + i * size//8 + int(wave_phase * size//6)
                alpha = int((200 - i * 50) * (1 - wave_phase))
                wave_hex = []
                for j in range(6):
                    angle = (j * 60) * 3.14159 / 180
                    px = center_x + int(wave_r * math.cos(angle))
                    py = center_y + int(wave_r * math.sin(angle))
                    wave_hex.append((px, py))
                if len(wave_hex) > 1:
                    temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    adjusted_points = [(px - x + size, py - y + size) for px, py in wave_hex]
                    pygame.draw.lines(temp_surf, (*color, alpha), True, adjusted_points, 2)
                    surface.blit(temp_surf, (x - size, y - size))
        
        elif "quantum_entangle" in effects or "spooky_action" in effects:
            # 量子纠缠网：超距连接
            # 中心量子核
            pygame.draw.circle(surface, (255, 150, 255), (center_x, center_y), size//8)
            pygame.draw.circle(surface, color, (center_x, center_y), size//10)
            # 纠缠粒子（8个）
            particles = []
            for i in range(8):
                angle = (i * 45 + pygame.time.get_ticks() / 40) * 3.14159 / 180
                px = center_x + int(size//2.5 * math.cos(angle))
                py = center_y + int(size//2.5 * math.sin(angle))
                particles.append((px, py))
                pygame.draw.circle(surface, (200, 100, 220), (px, py), size//15)
            # 纠缠连线
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            for i in range(len(particles)):
                # 连接到对角粒子
                opposite = (i + 4) % len(particles)
                p1 = (particles[i][0] - x + size, particles[i][1] - y + size)
                p2 = (particles[opposite][0] - x + size, particles[opposite][1] - y + size)
                pygame.draw.line(temp_surf, (*color, 150), p1, p2, 2)
            surface.blit(temp_surf, (x - size, y - size))
            # 量子波动
            for px, py in particles:
                pulse_size = int(size//20 * (1 + 0.4 * math.sin(pygame.time.get_ticks() / 70)))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, 120), (px - x + size, py - y + size), pulse_size)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "collapse_star" in effects or "wavefunction_collapse" in effects:
            # 波函数坍缩：量子态收束
            # 坍缩前：多个重影态
            collapse_phase = (math.sin(pygame.time.get_ticks() / 100) + 1) / 2
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                spread = int(size//3 * (1 - collapse_phase))
                sx = center_x + int(spread * math.cos(angle))
                sy = center_y + int(spread * math.sin(angle))
                alpha = int(150 * (1 - collapse_phase))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (sx - x + size, sy - y + size), size//10)
                surface.blit(temp_surf, (x - size, y - size))
            # 坍缩后：确定态
            final_size = int(size//5 * collapse_phase)
            pygame.draw.circle(surface, (220, 180, 255), (center_x, center_y), final_size + 5)
            pygame.draw.circle(surface, color, (center_x, center_y), final_size)
            # 坍缩波
            for i in range(3):
                wave_r = int((size//4 + i * size//8) * collapse_phase)
                alpha = int((180 - i * 50) * collapse_phase)
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), wave_r, 2)
                surface.blit(temp_surf, (x - size, y - size))
        
        # ========== Eclipse 子弹形状 ==========
        elif "dual_core" in effects or "sync_resonance" in effects:
            # 双核心共振：双星系统
            core_offset = size//4
            # 左核心
            left_x = center_x - core_offset
            pygame.draw.circle(surface, (100, 50, 180), (left_x, center_y), size//6)
            pygame.draw.circle(surface, color, (left_x, center_y), size//8)
            # 右核心
            right_x = center_x + core_offset
            pygame.draw.circle(surface, (150, 80, 220), (right_x, center_y), size//6)
            pygame.draw.circle(surface, color, (right_x, center_y), size//8)
            # 共振波（连接线）
            resonance_width = int(3 + 2 * math.sin(pygame.time.get_ticks() / 80))
            pygame.draw.line(surface, (200, 100, 255), (left_x, center_y), (right_x, center_y), resonance_width)
            # 能量环
            for i in range(2):
                ring_r = size//3 + i * size//8
                alpha = 180 - i * 60
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), ring_r, 2)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "shadow_eclipse" in effects or "lunar_devour" in effects:
            # 影蚀之月：月影吞噬
            # 月盘
            pygame.draw.circle(surface, (180, 180, 200), (center_x, center_y), size//3)
            # 影子侵蚀（半圆）
            eclipse_phase = (math.sin(pygame.time.get_ticks() / 100) + 1) / 2
            shadow_offset = int(size//3 * eclipse_phase)
            shadow_x = center_x - shadow_offset
            pygame.draw.circle(surface, (30, 20, 50), (shadow_x, center_y), size//3)
            # 边缘光晕
            pygame.draw.circle(surface, color, (center_x, center_y), size//3, 3)
            # 日冕效果
            for i in range(8):
                angle = (i * 45) * 3.14159 / 180
                x1 = center_x + int(size//3 * math.cos(angle))
                y1 = center_y + int(size//3 * math.sin(angle))
                x2 = center_x + int(size//2 * math.cos(angle))
                y2 = center_y + int(size//2 * math.sin(angle))
                pygame.draw.line(surface, (120, 80, 160), (x1, y1), (x2, y2), 2)
        
        elif "corona_burst" in effects or "eclipse_ring" in effects:
            # 日冕爆发：日食边缘
            # 日食主体
            pygame.draw.circle(surface, (50, 30, 80), (center_x, center_y), size//4)
            # 日冕环（3层）
            for i in range(3):
                ring_r = size//3 + i * size//8
                ring_color = (100 + i * 30, 50 + i * 20, 180 + i * 20)
                alpha = 200 - i * 50
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*ring_color, alpha), (size, size), ring_r, 3)
                surface.blit(temp_surf, (x - size, y - size))
            # 爆发射线（12条）
            for i in range(12):
                angle = (i * 30 + pygame.time.get_ticks() / 50) * 3.14159 / 180
                length = size//3 if i % 2 == 0 else size//2
                x1 = center_x + int(size//4 * math.cos(angle))
                y1 = center_y + int(size//4 * math.sin(angle))
                x2 = center_x + int(length * math.cos(angle))
                y2 = center_y + int(length * math.sin(angle))
                pygame.draw.line(surface, (200, 100, 255), (x1, y1), (x2, y2), 2)
        
        elif "void_mirror" in effects or "shadow_clone" in effects:
            # 虚空镜像：影子复制
            # 主体
            pygame.draw.circle(surface, color, (center_x, center_y), size//5)
            pygame.draw.circle(surface, (150, 100, 200), (center_x, center_y), size//6)
            # 镜像（4个方向）
            mirror_offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            for i, (dx, dy) in enumerate(mirror_offsets):
                mirror_x = center_x + dx * size//3
                mirror_y = center_y + dy * size//3
                alpha = 150 - i * 20
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (mirror_x - x + size, mirror_y - y + size), size//8)
                surface.blit(temp_surf, (x - size, y - size))
            # 连接线
            for dx, dy in mirror_offsets:
                mirror_x = center_x + dx * size//3
                mirror_y = center_y + dy * size//3
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, (*color, 100), 
                               (center_x - x + size, center_y - y + size),
                               (mirror_x - x + size, mirror_y - y + size), 1)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "twilight_zone" in effects or "dusk_dawn_edge" in effects:
            # 黄昏地带：光暗边缘
            # 渐变背景（从亮到暗）
            for i in range(20):
                gradient_y = center_y - size//2 + i * size//10
                brightness = 200 - i * 10
                gradient_color = (brightness, brightness//2, brightness + 55)
                pygame.draw.line(surface, gradient_color, 
                               (center_x - size//2, gradient_y),
                               (center_x + size//2, gradient_y), size//10)
            # 边界线
            pygame.draw.line(surface, color, (center_x - size//2, center_y), (center_x + size//2, center_y), 4)
            # 光暗粒子
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                px = center_x + int(size//3 * math.cos(angle))
                py = center_y + int(size//3 * math.sin(angle))
                particle_color = (200, 150, 250) if py < center_y else (50, 30, 100)
                pygame.draw.circle(surface, particle_color, (px, py), size//18)
        
        elif "dark_matter" in effects or "invisible_mass" in effects:
            # 暗物质弹：不可见质量
            # 扭曲空间（波纹）
            for i in range(4):
                wave_r = size//6 + i * size//10
                alpha = 150 - i * 30
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (size, size), wave_r, 2)
                surface.blit(temp_surf, (x - size, y - size))
            # 暗物质核心（几乎不可见）
            pygame.draw.circle(surface, (50, 20, 100), (center_x, center_y), size//8)
            temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*color, 100), (size, size), size//6)
            surface.blit(temp_surf, (x - size, y - size))
            # 引力扭曲线
            for i in range(8):
                angle = (i * 45 + pygame.time.get_ticks() / 60) * 3.14159 / 180
                x1 = center_x + int(size//4 * math.cos(angle))
                y1 = center_y + int(size//4 * math.sin(angle))
                x2 = center_x + int(size//2 * math.cos(angle + 0.3))
                y2 = center_y + int(size//2 * math.sin(angle + 0.3))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, (*color, 120), 
                               (x1 - x + size, y1 - y + size),
                               (x2 - x + size, y2 - y + size), 1)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "black_sun" in effects or "anti_radiance" in effects:
            # 黑日降临：黑色太阳
            # 黑色核心
            pygame.draw.circle(surface, (20, 10, 30), (center_x, center_y), size//4)
            pygame.draw.circle(surface, color, (center_x, center_y), size//5)
            # 反光环（黑色光晕）
            for i in range(3):
                halo_r = size//3 + i * size//8
                alpha = 180 - i * 50
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (50, 20, 80, alpha), (size, size), halo_r, 4)
                surface.blit(temp_surf, (x - size, y - size))
            # 反向射线（吸收光线）
            for i in range(16):
                angle = (i * 22.5) * 3.14159 / 180
                x1 = center_x + int(size//2 * math.cos(angle))
                y1 = center_y + int(size//2 * math.sin(angle))
                x2 = center_x + int(size//4 * math.cos(angle))
                y2 = center_y + int(size//4 * math.sin(angle))
                # 从外向内绘制
                pygame.draw.line(surface, (80, 30, 120), (x1, y1), (x2, y2), 2)
            # 暗能量粒子
            for i in range(8):
                angle = (i * 45 + pygame.time.get_ticks() / 40) * 3.14159 / 180
                px = center_x + int(size//2.5 * math.cos(angle))
                py = center_y + int(size//2.5 * math.sin(angle))
                pygame.draw.circle(surface, (100, 30, 150), (px, py), size//20)
        
        # ========== Prism 子弹形状 ==========
        elif "rainbow_ray" in effects or "spectrum_split" in effects:
            # 彩虹射线：七色光芒
            # 彩虹核心
            rainbow_colors = [
                (255, 0, 0), (255, 127, 0), (255, 255, 0),
                (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
            ]
            # 彩虹射线（7条）
            for i, ray_color in enumerate(rainbow_colors):
                angle = (i * 51.4 + pygame.time.get_ticks() / 50) * 3.14159 / 180
                x1 = center_x + int(size//8 * math.cos(angle))
                y1 = center_y + int(size//8 * math.sin(angle))
                x2 = center_x + int(size//2 * math.cos(angle))
                y2 = center_y + int(size//2 * math.sin(angle))
                pygame.draw.line(surface, ray_color, (x1, y1), (x2, y2), 3)
            # 中心白光
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//8)
            pygame.draw.circle(surface, color, (center_x, center_y), size//10)
            # 光谱环
            for i in range(7):
                ring_color = rainbow_colors[i]
                ring_r = size//4 + i * size//35
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*ring_color, 150), (size, size), ring_r, 2)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "crystal_shard" in effects or "prism_fragment" in effects:
            # 水晶碎片：晶体折射
            # 中心水晶
            crystal_points = [
                (center_x, center_y - size//2),
                (center_x + size//3, center_y),
                (center_x, center_y + size//2),
                (center_x - size//3, center_y)
            ]
            pygame.draw.polygon(surface, (200, 240, 255), crystal_points)
            pygame.draw.polygon(surface, color, crystal_points, 3)
            # 碎片（周围小晶体）
            for i in range(6):
                angle = (i * 60 + pygame.time.get_ticks() / 60) * 3.14159 / 180
                sx = center_x + int(size//2.5 * math.cos(angle))
                sy = center_y + int(size//2.5 * math.sin(angle))
                shard_points = [
                    (sx, sy - size//8),
                    (sx + size//12, sy + size//12),
                    (sx - size//12, sy + size//12)
                ]
                pygame.draw.polygon(surface, (150, 220, 255), shard_points)
                pygame.draw.polygon(surface, color, shard_points, 2)
            # 光线折射效果
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                x1 = center_x + int(size//4 * math.cos(angle))
                y1 = center_y + int(size//4 * math.sin(angle))
                x2 = center_x + int(size//2 * math.cos(angle + 0.5))
                y2 = center_y + int(size//2 * math.sin(angle + 0.5))
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, (*color, 180), (x1 - x + size, y1 - y + size), (x2 - x + size, y2 - y + size), 2)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "refraction_beam" in effects or "light_bend" in effects:
            # 折射光束：曲线光束
            # 光源
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//8)
            pygame.draw.circle(surface, color, (center_x, center_y), size//10)
            # 折射光束（3条弯曲路径）
            for i in range(3):
                beam_angle = (i * 120) * 3.14159 / 180
                beam_points = []
                for j in range(8):
                    radius = size//8 + j * size//16
                    curve_offset = int(size//12 * math.sin(j * 0.5 + pygame.time.get_ticks() / 100))
                    bx = center_x + int(radius * math.cos(beam_angle)) + curve_offset
                    by = center_y + int(radius * math.sin(beam_angle))
                    beam_points.append((bx, by))
                if len(beam_points) > 1:
                    # 多层光束颜色
                    pygame.draw.lines(surface, (200, 230, 255), False, beam_points, 4)
                    pygame.draw.lines(surface, color, False, beam_points, 2)
            # 折射粒子
            for i in range(6):
                angle = (i * 60) * 3.14159 / 180
                px = center_x + int(size//3 * math.cos(angle))
                py = center_y + int(size//3 * math.sin(angle))
                pygame.draw.circle(surface, (150, 200, 255), (px, py), size//25)
        
        elif "laser_prism" in effects or "triangular_prism" in effects:
            # 激光棱镜：三棱镜
            # 棱镜主体（三角形）
            prism_triangle = [
                (center_x, center_y - size//3),
                (center_x + size//3, center_y + size//3),
                (center_x - size//3, center_y + size//3)
            ]
            pygame.draw.polygon(surface, (180, 230, 255), prism_triangle)
            pygame.draw.polygon(surface, color, prism_triangle, 3)
            # 入射光（白光）
            pygame.draw.line(surface, (255, 255, 255), (center_x - size//2, center_y - size//4), (center_x - size//6, center_y), 3)
            # 分光（彩虹射线）
            spectrum_colors = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (148, 0, 211)]
            for i, spec_color in enumerate(spectrum_colors):
                angle = -20 + i * 10
                rad = angle * 3.14159 / 180
                x1 = center_x + size//6
                y1 = center_y
                x2 = center_x + int(size//2 * math.cos(rad))
                y2 = center_y + int(size//2 * math.sin(rad))
                pygame.draw.line(surface, spec_color, (x1, y1), (x2, y2), 2)
        
        elif "aurora_split" in effects or "northern_light" in effects:
            # 极光分裂：北极光
            # 极光波纹
            aurora_colors = [(0, 255, 200), (100, 255, 150), (150, 255, 200)]
            wave_phase = (pygame.time.get_ticks() / 60) % 100 / 100
            for i in range(3):
                wave_y = center_y - size//2 + i * size//3 + int(wave_phase * size//4)
                # 波浪曲线
                wave_points = []
                for j in range(10):
                    wx = center_x - size//2 + j * size//9
                    wy = wave_y + int(size//10 * math.sin(j * 0.8 + wave_phase * 6.28))
                    wave_points.append((wx, wy))
                if len(wave_points) > 1:
                    alpha = 200 - i * 50
                    temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    adjusted_points = [(px - x + size, py - y + size) for px, py in wave_points]
                    pygame.draw.lines(temp_surf, (*aurora_colors[i], alpha), False, adjusted_points, 3)
                    surface.blit(temp_surf, (x - size, y - size))
            # 中心光球
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//8)
            pygame.draw.circle(surface, color, (center_x, center_y), size//10)
            # 极光粒子
            for i in range(8):
                angle = (i * 45 + pygame.time.get_ticks() / 50) * 3.14159 / 180
                px = center_x + int(size//3 * math.cos(angle))
                py = center_y + int(size//3 * math.sin(angle))
                pygame.draw.circle(surface, (120, 255, 200), (px, py), size//20)
        
        elif "hologram" in effects or "3d_projection" in effects:
            # 全息投影：3D影像
            # 全息网格
            grid_lines = 8
            for i in range(grid_lines):
                # 横线
                y_pos = center_y - size//2 + i * size//(grid_lines-1)
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, (*color, 120), 
                               (center_x - size//2 - x + size, y_pos - y + size),
                               (center_x + size//2 - x + size, y_pos - y + size), 1)
                surface.blit(temp_surf, (x - size, y - size))
                # 竖线
                x_pos = center_x - size//2 + i * size//(grid_lines-1)
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, (*color, 120),
                               (x_pos - x + size, center_y - size//2 - y + size),
                               (x_pos - x + size, center_y + size//2 - y + size), 1)
                surface.blit(temp_surf, (x - size, y - size))
            # 3D立方体（旋转）
            rotation = (pygame.time.get_ticks() / 50) % 360 * 3.14159 / 180
            cube_size = size//4
            cube_points_3d = [
                (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
            ]
            cube_points_2d = []
            for px, py, pz in cube_points_3d:
                # 简单旋转投影
                rx = px * math.cos(rotation) - pz * math.sin(rotation)
                rz = px * math.sin(rotation) + pz * math.cos(rotation)
                x2d = center_x + int(rx * cube_size)
                y2d = center_y + int(py * cube_size)
                cube_points_2d.append((x2d, y2d))
            # 绘制立方体边
            cube_edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
            for i, j in cube_edges:
                pygame.draw.line(surface, color, cube_points_2d[i], cube_points_2d[j], 2)
        
        elif "lens_flare" in effects or "optical_burst" in effects:
            # 镜头光晕：光学耀斑
            # 主光源（超亮）
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//6)
            pygame.draw.circle(surface, color, (center_x, center_y), size//8)
            # 光晕环（多层）
            for i in range(4):
                flare_r = size//5 + i * size//10
                alpha = 200 - i * 40
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (255, 255, 255, alpha), (size, size), flare_r)
                surface.blit(temp_surf, (x - size, y - size))
            # 光斑（6个）
            flare_spots = [0.3, 0.5, 0.7, 0.9, 1.1, 1.3]
            for i, dist in enumerate(flare_spots):
                spot_x = center_x + int(size//2 * dist * math.cos(i * 0.8))
                spot_y = center_y + int(size//2 * dist * math.sin(i * 0.8))
                spot_size = int(size//15 * (1.5 - dist * 0.5))
                if spot_size > 0:
                    temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surf, (*color, 180), (spot_x - x + size, spot_y - y + size), spot_size)
                    surface.blit(temp_surf, (x - size, y - size))
            # 十字光芒
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                x1 = center_x + int(size//8 * math.cos(angle))
                y1 = center_y + int(size//8 * math.sin(angle))
                x2 = center_x + int(size//1.5 * math.cos(angle))
                y2 = center_y + int(size//1.5 * math.sin(angle))
                pygame.draw.line(surface, (255, 255, 200), (x1, y1), (x2, y2), 3)
        
        # ========== Necro 子弹形状 ==========
        elif "soul_reaper" in effects or "death_scythe" in effects:
            # 灵魂收割：死神镰刀
            # 镰刀刃
            scythe_blade = [
                (center_x - size//6, center_y - size//3),
                (center_x + size//3, center_y - size//6),
                (center_x + size//4, center_y + size//8),
                (center_x - size//4, center_y)
            ]
            pygame.draw.polygon(surface, (200, 200, 220), scythe_blade)
            pygame.draw.polygon(surface, color, scythe_blade, 3)
            # 镰刀柄
            pygame.draw.line(surface, (100, 50, 80), (center_x, center_y), (center_x - size//4, center_y + size//2), 4)
            # 灵魂漩涡
            for i in range(6):
                angle = (i * 60 + pygame.time.get_ticks() / 40) * 3.14159 / 180
                spiral_r = size//4 + int(size//8 * (i / 6))
                sx = center_x + int(spiral_r * math.cos(angle))
                sy = center_y + int(spiral_r * math.sin(angle))
                alpha = 200 - i * 30
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*color, alpha), (sx - x + size, sy - y + size), size//20)
                surface.blit(temp_surf, (x - size, y - size))
        
        elif "blood_curse" in effects or "vampire_drain" in effects:
            # 鲜血诅咒：吸血魔法
            # 血滴核心
            pygame.draw.circle(surface, (180, 0, 80), (center_x, center_y), size//4)
            pygame.draw.circle(surface, color, (center_x, center_y), size//5)
            # 血滴形状（水滴）
            drop_points = []
            for i in range(16):
                angle = (i * 22.5 - 90) * 3.14159 / 180
                if i < 8:
                    radius = size//3
                else:
                    radius = size//4 + int(size//8 * math.sin((i - 8) * 0.785))
                px = center_x + int(radius * math.cos(angle))
                py = center_y + int(radius * math.sin(angle))
                drop_points.append((px, py))
            if len(drop_points) > 2:
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                adjusted_points = [(px - x + size, py - y + size) for px, py in drop_points]
                pygame.draw.polygon(temp_surf, (200, 0, 100, 180), adjusted_points)
                surface.blit(temp_surf, (x - size, y - size))
                pygame.draw.lines(surface, color, True, drop_points, 2)
            # 吸血触手
            for i in range(4):
                angle = (i * 90 + pygame.time.get_ticks() / 50) * 3.14159 / 180
                tendril_points = []
                for j in range(6):
                    radius = size//5 + j * size//15
                    wave = int(size//15 * math.sin(j * 0.8 + pygame.time.get_ticks() / 100))
                    tx = center_x + int(radius * math.cos(angle)) + wave
                    ty = center_y + int(radius * math.sin(angle))
                    tendril_points.append((tx, ty))
                if len(tendril_points) > 1:
                    pygame.draw.lines(surface, (150, 0, 70), False, tendril_points, 2)
        
        elif "bone_spike" in effects or "skeletal_weapon" in effects:
            # 白骨尖刺：骸骨武器
            # 骨刺主体（长三角）
            spike_points = [
                (center_x, center_y - size//2),
                (center_x + size//8, center_y + size//2),
                (center_x - size//8, center_y + size//2)
            ]
            pygame.draw.polygon(surface, (220, 220, 220), spike_points)
            pygame.draw.polygon(surface, color, spike_points, 3)
            # 骨节（横纹）
            for i in range(5):
                node_y = center_y - size//3 + i * size//6
                node_width = size//6 - i * size//40
                pygame.draw.line(surface, (180, 180, 180), 
                               (center_x - node_width, node_y),
                               (center_x + node_width, node_y), 2)
            # 骨刺尖端
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y - size//2), size//12)
            # 周围骨片
            for i in range(4):
                angle = (i * 90 + 45) * 3.14159 / 180
                bx = center_x + int(size//3 * math.cos(angle))
                by = center_y + int(size//3 * math.sin(angle))
                bone_shard = [
                    (bx, by - size//10),
                    (bx + size//15, by + size//15),
                    (bx - size//15, by + size//15)
                ]
                pygame.draw.polygon(surface, (200, 200, 200), bone_shard)
                pygame.draw.polygon(surface, color, bone_shard, 2)
        
        elif "plague_cloud" in effects or "pestilence_mist" in effects:
            # 瘟疫之云：病毒毒雾
            # 毒雾核心
            pygame.draw.circle(surface, (100, 150, 50), (center_x, center_y), size//5)
            pygame.draw.circle(surface, color, (center_x, center_y), size//6)
            # 毒雾扩散（多层云）
            import random
            random.seed(234)
            for i in range(12):
                angle = (i * 30 + random.randint(-15, 15)) * 3.14159 / 180
                cloud_r = size//4 + random.randint(0, size//8)
                cx = center_x + int(cloud_r * math.cos(angle))
                cy = center_y + int(cloud_r * math.sin(angle))
                cloud_size = size//10 + random.randint(0, size//15)
                alpha = 150 - i * 10
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (120, 180, 60, alpha), (cx - x + size, cy - y + size), cloud_size)
                surface.blit(temp_surf, (x - size, y - size))
            # 病毒粒子
            for i in range(8):
                angle = (i * 45 + pygame.time.get_ticks() / 60) * 3.14159 / 180
                px = center_x + int(size//3 * math.cos(angle))
                py = center_y + int(size//3 * math.sin(angle))
                # 病毒形状（十字）
                pygame.draw.line(surface, (80, 120, 40), (px - size//25, py), (px + size//25, py), 2)
                pygame.draw.line(surface, (80, 120, 40), (px, py - size//25), (px, py + size//25), 2)
        
        elif "death_mark" in effects or "doom_sigil" in effects:
            # 死亡印记：终结符文
            # 符文圆环
            pygame.draw.circle(surface, color, (center_x, center_y), size//3, 3)
            pygame.draw.circle(surface, (150, 0, 100), (center_x, center_y), size//4, 2)
            # 死亡标记（五角星）
            star_points = []
            for i in range(5):
                angle = (i * 72 - 90) * 3.14159 / 180
                px = center_x + int(size//4 * math.cos(angle))
                py = center_y + int(size//4 * math.sin(angle))
                star_points.append((px, py))
            # 绘制五角星（连接间隔点）
            if len(star_points) == 5:
                pygame.draw.line(surface, color, star_points[0], star_points[2], 3)
                pygame.draw.line(surface, color, star_points[2], star_points[4], 3)
                pygame.draw.line(surface, color, star_points[4], star_points[1], 3)
                pygame.draw.line(surface, color, star_points[1], star_points[3], 3)
                pygame.draw.line(surface, color, star_points[3], star_points[0], 3)
            # 符文文字（简化为线条）
            rune_symbols = [
                [(center_x - size//8, center_y - size//2), (center_x + size//8, center_y - size//2)],
                [(center_x - size//2, center_y), (center_x - size//4, center_y)],
                [(center_x + size//4, center_y), (center_x + size//2, center_y)],
                [(center_x, center_y + size//3), (center_x, center_y + size//2)]
            ]
            for line_start, line_end in rune_symbols:
                pygame.draw.line(surface, (180, 50, 120), line_start, line_end, 2)
        
        elif "ghost_chain" in effects or "spectral_shackle" in effects:
            # 幽灵锁链：灵魂枷锁
            # 锁链中心
            pygame.draw.circle(surface, (120, 80, 150), (center_x, center_y), size//6)
            pygame.draw.circle(surface, color, (center_x, center_y), size//8)
            # 锁链（4条）
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                chain_points = []
                for j in range(6):
                    radius = size//8 + j * size//15
                    # 锁链弧度
                    arc_offset = int(size//12 * math.sin(j * 0.6 + pygame.time.get_ticks() / 80))
                    cx = center_x + int(radius * math.cos(angle)) + arc_offset * (1 if i % 2 == 0 else -1)
                    cy = center_y + int(radius * math.sin(angle))
                    chain_points.append((cx, cy))
                if len(chain_points) > 1:
                    pygame.draw.lines(surface, (100, 70, 130), False, chain_points, 3)
                    # 锁链节点
                    for cx, cy in chain_points[::2]:
                        pygame.draw.circle(surface, (150, 100, 180), (cx, cy), size//25)
            # 枷锁环（4个）
            for i in range(4):
                angle = (i * 90 + 45) * 3.14159 / 180
                ring_x = center_x + int(size//2.5 * math.cos(angle))
                ring_y = center_y + int(size//2.5 * math.sin(angle))
                pygame.draw.circle(surface, (140, 90, 160), (ring_x, ring_y), size//15, 2)
        
        elif "necrotic_burst" in effects or "undead_explosion" in effects:
            # 死灵爆发：腐朽爆炸
            # 死灵核心
            pygame.draw.circle(surface, (180, 50, 120), (center_x, center_y), size//5)
            pygame.draw.circle(surface, color, (center_x, center_y), size//6)
            # 爆发波（3层）
            burst_phase = (pygame.time.get_ticks() / 50) % 100 / 100
            for i in range(3):
                burst_r = int((size//4 + i * size//6) * (1 + burst_phase * 0.6))
                alpha = int((200 - i * 50) * (1 - burst_phase * 0.7))
                burst_colors = [(150, 0, 100), (180, 50, 120), (200, 80, 140)]
                temp_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*burst_colors[i], alpha), (size, size), burst_r, 3)
                surface.blit(temp_surf, (x - size, y - size))
            # 死灵能量（8个骷髅头简化形状）
            for i in range(8):
                angle = (i * 45 + burst_phase * 360) * 3.14159 / 180
                skull_r = size//3 + int(burst_phase * size//3)
                sx = center_x + int(skull_r * math.cos(angle))
                sy = center_y + int(skull_r * math.sin(angle))
                skull_size = int(size//15 * (1 - burst_phase * 0.5))
                if skull_size > 0:
                    # 简化骷髅（圆形+眼睛）
                    pygame.draw.circle(surface, (200, 200, 200), (sx, sy), skull_size)
                    pygame.draw.circle(surface, (0, 0, 0), (sx - skull_size//3, sy - skull_size//4), skull_size//5)
                    pygame.draw.circle(surface, (0, 0, 0), (sx + skull_size//3, sy - skull_size//4), skull_size//5)
        
        else:
            # 默认：简单圆形
            pygame.draw.circle(surface, color, (center_x, center_y), size//3)
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//3, 2)
        
        # 不再绘制emoji符号，改用纯图形装饰
        # 在周围绘制小光点作为装饰
        for i in range(3):
            angle = (i * 120) * 3.14159 / 180
            px = center_x + int(size//2.2 * math.cos(angle))
            py = center_y + int(size//2.2 * math.sin(angle))
            pygame.draw.circle(surface, color, (px, py), 3)
            pygame.draw.circle(surface, (255, 255, 255), (px, py), 3, 1)
                
    except Exception as e:
        # 渲染失败时显示灰色圆形
        pygame.draw.circle(surface, (100, 100, 100), (x + size//2, y + size//2), size//4)

def reset_game():
    global player, boss, score
    global global_time_freeze, is_paused
    global upgrade_options, upgrade_selected, levelup_ready, frozen_screen, wave
    global upgrade_options, upgrade_selected, levelup_ready, frozen_screen, wave, tab_paused
    
    # reset_game() called
    
    is_paused = False 
    frozen_screen = None
    tab_paused = False
    upgrade_options = []
    upgrade_selected = 0
    levelup_ready = False
    
    all_sprites.empty()
    mobs.empty()
    bullets.empty()
    enemy_bullets.empty()
    powerups.empty()
    supplies.empty()
    
    score = 0
    boss = None
    boss_manager.reset()
    global_time_freeze = 0
    wave = 0
    
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
        current_bg_style = bg_manager.current_style
        bg_config = BackgroundManager.BG_STYLES.get(current_bg_style, {})
        bgm_track = bg_config.get("bgm", "normal")
        sound_mgr.play_music(bgm_track)
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
        ("Boss挑战模式", CYAN, "boss_challenge"),
        ("武器库", ORANGE, "arsenal"),
        ("涂装", MAGENTA, "customization"),
        ("背景设置", (100, 200, 255), "background_settings"),
        ("系统设置", (255, 150, 0), "settings"),
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

# ==============================================================================
#   UI 绘制
# ==============================================================================
def draw_menu_ui():
    # 标题字号缩小，居中更高
    scale = 1.0 + 0.03 * math.sin(pygame.time.get_ticks() * 0.003)
    title_font = get_font(int(60*scale), bold=True)
    glow = title_font.render("霓虹深空", True, (0, 100, 100))
    main = title_font.render("霓虹深空", True, CYAN)
    rect = main.get_rect(center=(WIDTH//2, 110))
    safe_blit(screen, glow, (rect.x+3, rect.y+3))
    safe_blit(screen, main, rect)

    mx, my = pygame.mouse.get_pos()
    buttons = get_menu_buttons()
    for i, (r, txt, col, act) in enumerate(buttons):
        is_hover = r.collidepoint(mx, my)
        is_selected = (i == main_menu_selected)
        is_active = is_hover or is_selected
        
        # 背景颜色
        bg = (col[0]//2, col[1]//2, col[2]//2) if is_active else (30, 30, 40)
        draw_cyber_rect(screen, r, bg, alpha=200, fill=True)
        
        # 边框颜色和宽度
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
        draw_text(screen, f"[ {txt} ]" if is_active else txt, 18, r.centerx, r.centery-8, WHITE if is_active else GRAY, glow=is_active)

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
    other_y = start_y + 250
    checkbox_size = 28
    
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
    shake_y = other_y + 50
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
    particle_y = other_y + 100
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
    damage_y = other_y + 180
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
            # 绘制敌人预览（有机战机风格）
            import math
            preview = pygame.Surface((150, 150), pygame.SRCALPHA)
            enemy_color = tuple(data.get("color", (200, 100, 100)))
            dark_color = tuple(max(0, c - 60) for c in enemy_color)
            light_color = tuple(min(255, c + 80) for c in enemy_color)
            center = 75
            
            enemy_id = key
            
            if enemy_id == "scout_moth":
                # 灰蛾侦察机：轻盈蛾翼造型
                # 细长机身
                pygame.draw.ellipse(preview, enemy_color, (center-8, 30, 16, 90))
                pygame.draw.ellipse(preview, light_color, (center-8, 30, 16, 90), 2)
                # 大型蛾翼（弧形）
                pygame.draw.arc(preview, enemy_color, (20, 45, 50, 60), 0.5, 2.6, 8)
                pygame.draw.arc(preview, enemy_color, (80, 45, 50, 60), 0.5, 2.6, 8)
                pygame.draw.arc(preview, light_color, (20, 45, 50, 60), 0.5, 2.6, 2)
                pygame.draw.arc(preview, light_color, (80, 45, 50, 60), 0.5, 2.6, 2)
                # 触角
                pygame.draw.line(preview, light_color, (center-5, 35), (center-15, 20), 2)
                pygame.draw.line(preview, light_color, (center+5, 35), (center+15, 20), 2)
                pygame.draw.circle(preview, (255, 200, 100), (center-15, 20), 3)
                pygame.draw.circle(preview, (255, 200, 100), (center+15, 20), 3)
                # 复眼
                pygame.draw.ellipse(preview, (200, 50, 50), (center-12, 38, 10, 14))
                pygame.draw.ellipse(preview, (200, 50, 50), (center+2, 38, 10, 14))
            elif enemy_id == "trooper_spear":
                # 赤矛突击机：矛头战机
                # 尖锐矛头
                pygame.draw.polygon(preview, enemy_color, [(center, 15), (center-20, 70), (center+20, 70)])
                pygame.draw.polygon(preview, light_color, [(center, 15), (center-20, 70), (center+20, 70)], 2)
                # 矛身
                pygame.draw.rect(preview, dark_color, (center-12, 70, 24, 50))
                pygame.draw.rect(preview, enemy_color, (center-10, 72, 20, 46))
                # 稳定翼
                pygame.draw.polygon(preview, dark_color, [(center-12, 90), (center-35, 115), (center-12, 120)])
                pygame.draw.polygon(preview, dark_color, [(center+12, 90), (center+35, 115), (center+12, 120)])
                pygame.draw.polygon(preview, light_color, [(center-12, 90), (center-35, 115), (center-12, 120)], 1)
                pygame.draw.polygon(preview, light_color, [(center+12, 90), (center+35, 115), (center+12, 120)], 1)
                # 推进器火焰
                pygame.draw.polygon(preview, (255, 150, 50), [(center-8, 120), (center, 135), (center+8, 120)])
            elif enemy_id == "lurker_halo":
                # 光环潜伏者：多环UFO
                # 主碟身
                pygame.draw.ellipse(preview, dark_color, (center-40, center-12, 80, 24))
                pygame.draw.ellipse(preview, enemy_color, (center-38, center-10, 76, 20))
                # 驾驶舱圆顶
                pygame.draw.arc(preview, light_color, (center-20, center-35, 40, 40), 3.14, 0, 15)
                pygame.draw.ellipse(preview, (100, 200, 255), (center-15, center-28, 30, 20))
                # 底部光环
                pygame.draw.ellipse(preview, (100, 255, 200), (center-30, center+5, 60, 15), 2)
                pygame.draw.ellipse(preview, (100, 255, 200), (center-25, center+12, 50, 12), 1)
                # 舷灯
                for x in [center-30, center-15, center, center+15, center+30]:
                    pygame.draw.circle(preview, (255, 255, 100), (x, center), 3)
            elif enemy_id == "bomber_deepjelly":
                # 深海水母轰炸机：水母造型
                # 伞盖
                pygame.draw.arc(preview, enemy_color, (center-35, 25, 70, 60), 3.14, 0, 25)
                pygame.draw.arc(preview, light_color, (center-35, 25, 70, 60), 3.14, 0, 3)
                # 内部纹理
                for i in range(3):
                    pygame.draw.arc(preview, dark_color, (center-30+i*5, 30+i*3, 60-i*10, 50-i*6), 3.14, 0, 2)
                # 触须（波浪形）
                for x_off in [-25, -12, 0, 12, 25]:
                    for y in range(75, 130, 8):
                        wave = int(5 * math.sin((y + x_off) * 0.2))
                        pygame.draw.circle(preview, light_color, (center + x_off + wave, y), 2)
                # 发光核心
                pygame.draw.circle(preview, (255, 200, 255), (center, 50), 10)
                pygame.draw.circle(preview, (255, 255, 255), (center, 50), 5)
            elif enemy_id == "jammer_amethyst":
                # 紫晶干扰机：晶体簇造型
                # 主晶体
                pygame.draw.polygon(preview, enemy_color, [(center, 20), (center+15, 55), (center+10, 100), (center-10, 100), (center-15, 55)])
                pygame.draw.polygon(preview, light_color, [(center, 20), (center+15, 55), (center+10, 100), (center-10, 100), (center-15, 55)], 2)
                # 侧晶体
                pygame.draw.polygon(preview, dark_color, [(center-20, 45), (center-35, 70), (center-25, 95), (center-15, 70)])
                pygame.draw.polygon(preview, dark_color, [(center+20, 45), (center+35, 70), (center+25, 95), (center+15, 70)])
                pygame.draw.polygon(preview, light_color, [(center-20, 45), (center-35, 70), (center-25, 95), (center-15, 70)], 1)
                pygame.draw.polygon(preview, light_color, [(center+20, 45), (center+35, 70), (center+25, 95), (center+15, 70)], 1)
                # 小晶体
                pygame.draw.polygon(preview, enemy_color, [(center-30, 60), (center-40, 80), (center-28, 85)])
                pygame.draw.polygon(preview, enemy_color, [(center+30, 60), (center+40, 80), (center+28, 85)])
                # 能量光芒
                pygame.draw.circle(preview, (200, 150, 255), (center, 60), 8)
            elif enemy_id == "shield_beeguard":
                # 蜂巢护卫：六边形蜂巢盾
                # 六边形主体
                hex_pts = []
                for i in range(6):
                    angle = 60 * i - 90
                    hx = center + int(35 * math.cos(math.radians(angle)))
                    hy = center + int(35 * math.sin(math.radians(angle)))
                    hex_pts.append((hx, hy))
                pygame.draw.polygon(preview, enemy_color, hex_pts)
                pygame.draw.polygon(preview, light_color, hex_pts, 3)
                # 简化蜂巢纹理 - 只画6个孔
                for i in range(6):
                    angle = 60 * i
                    hx = center + int(18 * math.cos(math.radians(angle)))
                    hy = center + int(18 * math.sin(math.radians(angle)))
                    pygame.draw.circle(preview, dark_color, (hx, hy), 6)
                    pygame.draw.circle(preview, (50, 50, 30), (hx, hy), 4)
                # 中心女王蜂
                pygame.draw.circle(preview, (255, 200, 50), (center, center), 10)
                pygame.draw.circle(preview, (255, 255, 150), (center, center), 5)
            elif enemy_id == "splitter_azurecore":
                # 分裂核心：可分裂球体
                # 主核心（带裂纹）
                pygame.draw.circle(preview, enemy_color, (center, center), 28)
                pygame.draw.circle(preview, light_color, (center, center), 28, 2)
                # 裂纹线
                for angle in [0, 72, 144, 216, 288]:
                    rad = math.radians(angle)
                    pygame.draw.line(preview, dark_color, (center, center), 
                                   (center + int(28*math.cos(rad)), center + int(28*math.sin(rad))), 2)
                # 预分裂子核
                for angle in [36, 108, 180, 252, 324]:
                    rad = math.radians(angle)
                    px = center + int(20 * math.cos(rad))
                    py = center + int(20 * math.sin(rad))
                    pygame.draw.circle(preview, light_color, (px, py), 6)
                # 能量核心
                pygame.draw.circle(preview, (150, 200, 255), (center, center), 10)
            elif enemy_id == "prism_voidprism":
                # 虚空棱镜：三棱镜造型
                # 三角棱镜主体
                pygame.draw.polygon(preview, enemy_color, [(center, 25), (center-40, 110), (center+40, 110)])
                pygame.draw.polygon(preview, light_color, [(center, 25), (center-40, 110), (center+40, 110)], 3)
                # 光线折射效果
                pygame.draw.line(preview, (255, 100, 100), (center-20, 30), (center-35, 100), 2)
                pygame.draw.line(preview, (100, 255, 100), (center, 35), (center, 105), 2)
                pygame.draw.line(preview, (100, 100, 255), (center+20, 30), (center+35, 100), 2)
                # 中心虚空
                pygame.draw.circle(preview, (20, 0, 40), (center, 70), 15)
                pygame.draw.circle(preview, (80, 50, 120), (center, 70), 10)
                pygame.draw.circle(preview, (150, 100, 200), (center, 70), 5)
            elif enemy_id == "sniper_blackneedle":
                # 黑针狙击手：细长针形
                # 超长针身
                pygame.draw.polygon(preview, enemy_color, [(center, 10), (center-6, 130), (center+6, 130)])
                pygame.draw.polygon(preview, light_color, [(center, 10), (center-6, 130), (center+6, 130)], 2)
                # 瞄准镜
                pygame.draw.circle(preview, dark_color, (center, 50), 12)
                pygame.draw.circle(preview, (255, 0, 0), (center, 50), 8)
                pygame.draw.line(preview, (255, 50, 50), (center-12, 50), (center+12, 50), 1)
                pygame.draw.line(preview, (255, 50, 50), (center, 38), (center, 62), 1)
                # 稳定鳍
                pygame.draw.polygon(preview, dark_color, [(center-6, 100), (center-25, 120), (center-6, 125)])
                pygame.draw.polygon(preview, dark_color, [(center+6, 100), (center+25, 120), (center+6, 125)])
            elif enemy_id == "weaver_dualwasp":
                # 双蜂织机：双体黄蜂
                # 左蜂
                pygame.draw.ellipse(preview, enemy_color, (30, 50, 25, 50))  # 腹部
                pygame.draw.circle(preview, enemy_color, (42, 45), 12)  # 头
                pygame.draw.polygon(preview, dark_color, [(30, 95), (25, 115), (35, 115)])  # 尾刺
                # 右蜂
                pygame.draw.ellipse(preview, enemy_color, (95, 50, 25, 50))
                pygame.draw.circle(preview, enemy_color, (108, 45), 12)
                pygame.draw.polygon(preview, dark_color, [(120, 95), (115, 115), (125, 115)])
                # 翅膀
                pygame.draw.ellipse(preview, (*light_color[:3], 100), (15, 40, 30, 15))
                pygame.draw.ellipse(preview, (*light_color[:3], 100), (105, 40, 30, 15))
                # 连接丝线
                for y in [55, 70, 85]:
                    pygame.draw.line(preview, (255, 255, 200), (55, y), (95, y), 1)
                # 眼睛
                pygame.draw.circle(preview, (255, 50, 50), (38, 42), 3)
                pygame.draw.circle(preview, (255, 50, 50), (112, 42), 3)
            elif enemy_id == "summoner_nethalo":
                # 虚空召唤者：魔法阵核心
                # 外圈魔法阵
                pygame.draw.circle(preview, enemy_color, (center, center), 40, 2)
                # 五芒星
                for i in range(5):
                    a1 = math.radians(90 + i * 72)
                    a2 = math.radians(90 + (i + 2) * 72)
                    x1, y1 = center + 35*math.cos(a1), center - 35*math.sin(a1)
                    x2, y2 = center + 35*math.cos(a2), center - 35*math.sin(a2)
                    pygame.draw.line(preview, light_color, (int(x1), int(y1)), (int(x2), int(y2)), 2)
                # 符文点
                for i in range(5):
                    a = math.radians(90 + i * 72)
                    px, py = center + 35*math.cos(a), center - 35*math.sin(a)
                    pygame.draw.circle(preview, (200, 100, 255), (int(px), int(py)), 5)
                # 中心召唤核心
                pygame.draw.circle(preview, dark_color, (center, center), 18)
                pygame.draw.circle(preview, (150, 50, 200), (center, center), 12)
                pygame.draw.circle(preview, (200, 150, 255), (center, center), 6)
            elif enemy_id == "guard_heavyanvil":
                # 重型铁砧：坦克造型
                # 履带
                pygame.draw.rect(preview, (60, 60, 70), (25, 85, 25, 40))
                pygame.draw.rect(preview, (60, 60, 70), (100, 85, 25, 40))
                for i in range(4):
                    pygame.draw.line(preview, (40, 40, 50), (25, 90+i*10), (50, 90+i*10), 2)
                    pygame.draw.line(preview, (40, 40, 50), (100, 90+i*10), (125, 90+i*10), 2)
                # 车身
                pygame.draw.rect(preview, enemy_color, (35, 60, 80, 45))
                pygame.draw.rect(preview, light_color, (35, 60, 80, 45), 2)
                # 炮塔
                pygame.draw.circle(preview, dark_color, (center, 70), 22)
                pygame.draw.circle(preview, enemy_color, (center, 70), 20)
                # 主炮
                pygame.draw.rect(preview, (80, 80, 90), (center-5, 25, 10, 45))
                pygame.draw.rect(preview, light_color, (center-5, 25, 10, 45), 1)
            elif enemy_id == "nestlord_livestarport":
                # 巢穴领主：蜘蛛母巢
                # 腹部
                pygame.draw.ellipse(preview, enemy_color, (center-30, center-10, 60, 50))
                pygame.draw.ellipse(preview, dark_color, (center-30, center-10, 60, 50), 2)
                # 头部
                pygame.draw.circle(preview, enemy_color, (center, center-25), 18)
                # 八条腿
                leg_angles = [-150, -120, -60, -30, 150, 120, 60, 30]
                for i, angle in enumerate(leg_angles):
                    rad = math.radians(angle)
                    x1 = center + int(25 * math.cos(rad))
                    y1 = center + int(20 * math.sin(rad))
                    x2 = center + int(50 * math.cos(rad))
                    y2 = center + int(45 * math.sin(rad))
                    pygame.draw.line(preview, dark_color, (x1, y1), (x2, y2), 3)
                # 眼睛群
                for dx, dy in [(-8, -28), (8, -28), (-5, -22), (5, -22), (0, -18)]:
                    pygame.draw.circle(preview, (255, 0, 0), (center+dx, center+dy), 3)
                # 卵囊
                for dx in [-20, 0, 20]:
                    pygame.draw.circle(preview, (200, 255, 200), (center+dx, center+25), 6)
            elif enemy_id == "weaver_dimensionspindle":
                # 维度纺锤：时空沙漏
                # 上半沙漏
                pygame.draw.polygon(preview, enemy_color, [(center-30, 25), (center+30, 25), (center+8, 75), (center-8, 75)])
                pygame.draw.polygon(preview, light_color, [(center-30, 25), (center+30, 25), (center+8, 75), (center-8, 75)], 2)
                # 下半沙漏
                pygame.draw.polygon(preview, enemy_color, [(center-8, 75), (center+8, 75), (center+30, 125), (center-30, 125)])
                pygame.draw.polygon(preview, light_color, [(center-8, 75), (center+8, 75), (center+30, 125), (center-30, 125)], 2)
                # 时间流沙
                for i in range(5):
                    y = 35 + i * 18
                    w = 20 - abs(i-2) * 6
                    pygame.draw.line(preview, (200, 200, 255), (center-w, y), (center+w, y), 1)
                # 中心奇点
                pygame.draw.circle(preview, (100, 150, 255), (center, center), 8)
                pygame.draw.circle(preview, (200, 220, 255), (center, center), 4)
            elif enemy_id == "judge_dualpolar":
                # 双极裁决者：阴阳造型
                # 主圆
                pygame.draw.circle(preview, enemy_color, (center, center), 35)
                # 阴阳分割
                pygame.draw.arc(preview, dark_color, (center-35, center-35, 70, 70), 1.57, 4.71, 35)
                # 小圆点
                pygame.draw.circle(preview, dark_color, (center, center-17), 10)
                pygame.draw.circle(preview, light_color, (center, center+17), 10)
                pygame.draw.circle(preview, light_color, (center, center-17), 4)
                pygame.draw.circle(preview, dark_color, (center, center+17), 4)
                # 外圈
                pygame.draw.circle(preview, light_color, (center, center), 35, 3)
                # 裁决光芒
                for angle in [0, 90, 180, 270]:
                    rad = math.radians(angle)
                    x = center + int(42 * math.cos(rad))
                    y = center + int(42 * math.sin(rad))
                    pygame.draw.line(preview, (255, 255, 200), (center + int(35*math.cos(rad)), center + int(35*math.sin(rad))), (x, y), 2)
            elif enemy_id == "annihilator_soleye":
                # 歼灭独眼：巨型眼球战舰
                # 眼球主体
                pygame.draw.circle(preview, (240, 240, 240), (center, center), 40)
                pygame.draw.circle(preview, enemy_color, (center, center), 40, 3)
                # 虹膜
                pygame.draw.circle(preview, enemy_color, (center, center), 25)
                # 瞳孔
                pygame.draw.circle(preview, (20, 20, 30), (center, center), 15)
                pygame.draw.circle(preview, (255, 50, 50), (center, center), 8)
                # 高光
                pygame.draw.circle(preview, (255, 255, 255), (center-12, center-12), 8)
                pygame.draw.circle(preview, (255, 255, 255), (center+5, center-8), 4)
                # 血丝
                for angle in [30, 150, 210, 330]:
                    rad = math.radians(angle)
                    pygame.draw.line(preview, (255, 100, 100), 
                                   (center + int(25*math.cos(rad)), center + int(25*math.sin(rad))),
                                   (center + int(38*math.cos(rad)), center + int(38*math.sin(rad))), 1)
            elif enemy_id == "chaos_discordantprism":
                # 混沌乱棱：不规则多面体
                # 随机多边形
                pts = [(center + int(35*math.cos(math.radians(i*51+10))), 
                       center + int(35*math.sin(math.radians(i*51+10)))) for i in range(7)]
                pygame.draw.polygon(preview, enemy_color, pts)
                pygame.draw.polygon(preview, light_color, pts, 2)
                # 内部混乱线
                pygame.draw.line(preview, (255, 100, 100), pts[0], pts[3], 2)
                pygame.draw.line(preview, (100, 255, 100), pts[1], pts[4], 2)
                pygame.draw.line(preview, (100, 100, 255), pts[2], pts[5], 2)
                pygame.draw.line(preview, (255, 255, 100), pts[3], pts[6], 2)
                # 混沌核心
                pygame.draw.circle(preview, (255, 200, 100), (center, center), 12)
                pygame.draw.circle(preview, (255, 100, 200), (center-4, center-4), 5)
                pygame.draw.circle(preview, (100, 255, 200), (center+4, center+4), 5)
            elif enemy_id == "phantom_voidstrider":
                # 幽灵漫步者：鬼魂造型
                # 幽灵主体（半透明渐变）
                for i in range(4):
                    alpha_surf = pygame.Surface((150, 150), pygame.SRCALPHA)
                    pygame.draw.ellipse(alpha_surf, (*enemy_color, 80-i*15), (center-25+i*3, 30+i*5, 50-i*6, 80-i*10))
                    preview.blit(alpha_surf, (0, 0))
                # 头部
                pygame.draw.circle(preview, enemy_color, (center, 45), 20)
                # 眼睛（空洞）
                pygame.draw.ellipse(preview, (0, 0, 0), (center-15, 38, 12, 16))
                pygame.draw.ellipse(preview, (0, 0, 0), (center+3, 38, 12, 16))
                pygame.draw.circle(preview, (200, 200, 255), (center-9, 46), 3)
                pygame.draw.circle(preview, (200, 200, 255), (center+9, 46), 3)
                # 飘动尾部
                pygame.draw.polygon(preview, (*light_color[:3], 100), [(center-20, 100), (center-30, 130), (center-10, 125)])
                pygame.draw.polygon(preview, (*light_color[:3], 100), [(center, 105), (center-5, 135), (center+5, 135), (center+10, 105)])
                pygame.draw.polygon(preview, (*light_color[:3], 100), [(center+20, 100), (center+30, 130), (center+10, 125)])
            # ========== 中期添加的敌人预览图 ==========
            elif enemy_id == "helix_drone":
                # 螺旋无人机：四旋翼设计
                import math
                # 中心机身
                pygame.draw.circle(preview, enemy_color, (center, center), 18)
                pygame.draw.circle(preview, light_color, (center, center), 18, 2)
                # 四个旋翼
                rotor_positions = [(center-30, center-30), (center+30, center-30),
                                  (center-30, center+30), (center+30, center+30)]
                for rx, ry in rotor_positions:
                    pygame.draw.circle(preview, dark_color, (rx, ry), 14)
                    pygame.draw.circle(preview, light_color, (rx, ry), 14, 2)
                    # 旋翼叶片
                    pygame.draw.line(preview, light_color, (rx-10, ry), (rx+10, ry), 2)
                    pygame.draw.line(preview, light_color, (rx, ry-10), (rx, ry+10), 2)
                # 连接臂
                for rx, ry in rotor_positions:
                    pygame.draw.line(preview, (80, 80, 90), (center, center), (rx, ry), 3)
                # 中心传感器
                pygame.draw.circle(preview, (200, 200, 255), (center, center), 8)
            elif enemy_id == "mirage_twin":
                # 幻影双子：对称镜像设计
                offset = 20
                for dx in [-offset, offset]:
                    pygame.draw.circle(preview, enemy_color, (center + dx, center), 18)
                    pygame.draw.circle(preview, light_color, (center + dx, center), 18, 2)
                    pygame.draw.circle(preview, (150, 200, 255), (center + dx, center), 8)
                # 连接能量桥
                pygame.draw.line(preview, light_color, (center - offset + 18, center), 
                                (center + offset - 18, center), 4)
                # 外层能量环
                pygame.draw.ellipse(preview, light_color, (center - 45, center - 25, 90, 50), 2)
            elif enemy_id == "pulse_mine":
                # 脉冲地雷：球形能量核心
                # 外层警告环
                pygame.draw.circle(preview, (255, 50, 0), (center, center), 35, 3)
                pygame.draw.circle(preview, (255, 100, 50), (center, center), 30, 2)
                # 内核
                pygame.draw.circle(preview, enemy_color, (center, center), 25)
                pygame.draw.circle(preview, (255, 150, 100), (center, center), 15)
                pygame.draw.circle(preview, (255, 200, 150), (center, center), 8)
                # 能量脉冲线
                import math
                for i in range(8):
                    angle = i * 45
                    rad = math.radians(angle)
                    x1 = center + int(15 * math.cos(rad))
                    y1 = center + int(15 * math.sin(rad))
                    x2 = center + int(30 * math.cos(rad))
                    y2 = center + int(30 * math.sin(rad))
                    pygame.draw.line(preview, (255, 180, 100), (x1, y1), (x2, y2), 2)
            elif enemy_id == "laser_turret":
                # 激光炮塔：固定炮台设计
                # 底座
                pygame.draw.rect(preview, (80, 80, 90), (center-30, center+15, 60, 25))
                pygame.draw.rect(preview, enemy_color, (center-30, center+15, 60, 25), 2)
                # 炮塔主体
                pygame.draw.circle(preview, enemy_color, (center, center), 25)
                pygame.draw.circle(preview, light_color, (center, center), 25, 3)
                # 炮管
                pygame.draw.rect(preview, (60, 60, 70), (center-5, center-40, 10, 40))
                pygame.draw.rect(preview, (255, 50, 50), (center-3, center-40, 6, 8))
                # 瞄准器
                pygame.draw.circle(preview, (255, 0, 0), (center, center-8), 5)
            elif enemy_id == "swarm_carrier":
                # 蜂群航母：蜂巢母舰设计
                import math
                hex_points = [(center + int(35 * math.cos(math.radians(i * 60))),
                              center + int(35 * math.sin(math.radians(i * 60)))) for i in range(6)]
                pygame.draw.polygon(preview, enemy_color, hex_points)
                pygame.draw.polygon(preview, light_color, hex_points, 3)
                # 蜂巢孔洞
                for i in range(6):
                    hx = center + int(18 * math.cos(math.radians(i * 60 + 30)))
                    hy = center + int(18 * math.sin(math.radians(i * 60 + 30)))
                    pygame.draw.circle(preview, dark_color, (hx, hy), 8)
                    pygame.draw.circle(preview, (80, 60, 20), (hx, hy), 5)
                # 中心孵化核心
                pygame.draw.circle(preview, (255, 200, 50), (center, center), 12)
                pygame.draw.circle(preview, (255, 220, 100), (center, center), 7)
            elif enemy_id == "gravity_anchor":
                # 重力锚：暗物质核心
                # 外层扭曲环
                pygame.draw.circle(preview, (80, 40, 120), (center, center), 35, 3)
                pygame.draw.circle(preview, (100, 50, 150), (center, center), 30, 2)
                # 暗物质核心
                pygame.draw.circle(preview, enemy_color, (center, center), 25)
                pygame.draw.circle(preview, (30, 10, 50), (center, center), 18)
                pygame.draw.circle(preview, (180, 100, 255), (center, center), 8)
                # 引力线
                import math
                for i in range(6):
                    angle = i * 60
                    rad = math.radians(angle)
                    x = center + int(40 * math.cos(rad))
                    y = center + int(40 * math.sin(rad))
                    pygame.draw.line(preview, (120, 60, 180), (center, center), (x, y), 2)
            elif enemy_id == "tesla_coil":
                # 特斯拉线圈：电弧塔
                # 底座
                pygame.draw.rect(preview, (80, 80, 100), (center-20, center+20, 40, 20))
                # 线圈主体
                pygame.draw.ellipse(preview, enemy_color, (center-15, center-25, 30, 50))
                pygame.draw.ellipse(preview, light_color, (center-15, center-25, 30, 50), 2)
                # 电弧顶部
                pygame.draw.circle(preview, (200, 255, 255), (center, center-30), 12)
                pygame.draw.circle(preview, (150, 220, 255), (center, center-30), 7)
                # 电弧线
                import math
                for i in range(4):
                    angle = i * 90 + 45
                    rad = math.radians(angle)
                    x = center + int(25 * math.cos(rad))
                    y = center - 30 + int(25 * math.sin(rad))
                    pygame.draw.line(preview, (200, 255, 255), (center, center-30), (x, y), 2)
            elif enemy_id == "void_leech":
                # 虚空水蛭：吸能体
                # 主体：蠕虫形
                pygame.draw.ellipse(preview, enemy_color, (center-20, center-35, 40, 70))
                pygame.draw.ellipse(preview, (50, 0, 80), (center-20, center-35, 40, 70), 3)
                # 吸能口
                pygame.draw.circle(preview, (100, 0, 150), (center, center-25), 12)
                pygame.draw.circle(preview, (200, 50, 255), (center, center-25), 7)
                pygame.draw.circle(preview, (255, 100, 255), (center, center-25), 3)
                # 能量纹路
                for i in range(3):
                    y = center - 10 + i * 20
                    pygame.draw.line(preview, (150, 50, 200), (center-12, y), (center+12, y), 2)
            elif enemy_id == "omega_sentinel":
                # 欧米茄哨兵：终极守卫
                # 主装甲
                pygame.draw.circle(preview, enemy_color, (center, center), 35)
                pygame.draw.circle(preview, (255, 200, 50), (center, center), 35, 4)
                # 希腊字母Ω
                pygame.draw.arc(preview, (255, 255, 200), (center-20, center-20, 40, 35), 
                               0.5, 2.6, 3)
                pygame.draw.line(preview, (255, 255, 200), (center-20, center+8), (center-20, center+20), 3)
                pygame.draw.line(preview, (255, 255, 200), (center+20, center+8), (center+20, center+20), 3)
                # 多个武器挂点
                import math
                for angle in [0, 90, 180, 270]:
                    rad = math.radians(angle)
                    wx = center + int(30 * math.cos(rad))
                    wy = center + int(30 * math.sin(rad))
                    pygame.draw.circle(preview, (200, 150, 0), (wx, wy), 6)
            elif enemy_id == "quantum_ghost":
                # 量子幽灵：概率云
                # 半透明主体
                for r in range(30, 10, -5):
                    alpha = int(150 * (1 - r / 30))
                    temp = pygame.Surface((150, 150), pygame.SRCALPHA)
                    pygame.draw.circle(temp, (*enemy_color, alpha), (center, center), r)
                    preview.blit(temp, (0, 0))
                # 量子闪烁点
                import math
                for i in range(6):
                    angle = i * 60
                    rad = math.radians(angle)
                    px = center + int(20 * math.cos(rad))
                    py = center + int(20 * math.sin(rad))
                    pygame.draw.circle(preview, (200, 255, 220), (px, py), 5)
                # 核心
                pygame.draw.circle(preview, (100, 255, 180), (center, center), 10)
            elif enemy_id == "nova_core":
                # 新星核心：超新星
                # 外层光晕
                pygame.draw.circle(preview, (255, 220, 150), (center, center), 35, 3)
                pygame.draw.circle(preview, (255, 200, 100), (center, center), 30, 2)
                # 恒星核心
                pygame.draw.circle(preview, enemy_color, (center, center), 25)
                pygame.draw.circle(preview, (255, 240, 180), (center, center), 18)
                pygame.draw.circle(preview, (255, 255, 220), (center, center), 10)
                # 耀斑
                import math
                for i in range(8):
                    angle = i * 45
                    rad = math.radians(angle)
                    x1 = center + int(25 * math.cos(rad))
                    y1 = center + int(25 * math.sin(rad))
                    x2 = center + int(40 * math.cos(rad))
                    y2 = center + int(40 * math.sin(rad))
                    pygame.draw.line(preview, (255, 200, 100), (x1, y1), (x2, y2), 3)
            # ========== 新增8种敌人预览图 ==========
            elif enemy_id == "plasma_storm":
                # 等离子风暴：电弧能量球
                # 外层电弧光晕
                pygame.draw.circle(preview, (50, 150, 200), (center, 75), 45, 3)
                pygame.draw.circle(preview, (80, 180, 230), (center, 75), 38, 2)
                # 中层能量球
                pygame.draw.circle(preview, enemy_color, (center, 75), 32)
                pygame.draw.circle(preview, (150, 230, 255), (center, 75), 25)
                # 内核
                pygame.draw.circle(preview, (200, 240, 255), (center, 75), 15)
                pygame.draw.circle(preview, (255, 255, 255), (center, 75), 8)
                # 电弧线条
                pygame.draw.line(preview, (100, 200, 255), (center - 35, 55), (center - 15, 75), 2)
                pygame.draw.line(preview, (100, 200, 255), (center + 15, 75), (center + 35, 95), 2)
                pygame.draw.line(preview, (100, 200, 255), (center, 40), (center + 10, 55), 2)
                pygame.draw.line(preview, (100, 200, 255), (center - 10, 95), (center, 110), 2)
            elif enemy_id == "meteor_crusher":
                # 陨星粉碎者：重装甲岩石战舰
                rock_points = [
                    (center, 25), (center + 25, 45), (center + 35, 75),
                    (center + 20, 110), (center - 5, 125), (center - 25, 105),
                    (center - 35, 70), (center - 20, 40)
                ]
                pygame.draw.polygon(preview, dark_color, rock_points)
                pygame.draw.polygon(preview, enemy_color, rock_points)
                pygame.draw.polygon(preview, (80, 60, 50), rock_points, 3)
                # 岩石裂纹
                pygame.draw.line(preview, (60, 40, 30), (center - 15, 50), (center + 10, 90), 2)
                pygame.draw.line(preview, (60, 40, 30), (center + 5, 55), (center - 10, 100), 2)
                # 发光核心
                pygame.draw.circle(preview, (255, 120, 80), (center, 75), 12)
                pygame.draw.circle(preview, (255, 180, 120), (center, 75), 7)
                # 四个炮口
                for angle in [45, 135, 225, 315]:
                    import math
                    rad = math.radians(angle)
                    px = center + int(25 * math.cos(rad))
                    py = 75 + int(25 * math.sin(rad))
                    pygame.draw.circle(preview, (255, 100, 50), (px, py), 6)
            elif enemy_id == "swarm_mother":
                # 蜂群母舰：生物蜂巢母舰
                pygame.draw.ellipse(preview, dark_color, (center - 40, 50, 80, 50))
                pygame.draw.ellipse(preview, enemy_color, (center - 38, 52, 76, 46))
                pygame.draw.ellipse(preview, light_color, (center - 40, 50, 80, 50), 2)
                # 蜂巢结构
                hex_positions = [(center-20, 65), (center, 60), (center+20, 65),
                                (center-20, 85), (center, 90), (center+20, 85)]
                for hx, hy in hex_positions:
                    pygame.draw.circle(preview, (100, 80, 20), (hx, hy), 8)
                    pygame.draw.circle(preview, (60, 50, 10), (hx, hy), 5)
                # 触角
                pygame.draw.line(preview, light_color, (center - 30, 55), (center - 40, 35), 3)
                pygame.draw.line(preview, light_color, (center + 30, 55), (center + 40, 35), 3)
                # 尾部产卵器
                pygame.draw.ellipse(preview, (220, 200, 80), (center - 10, 95, 20, 15))
            elif enemy_id == "pulse_bomber":
                # 脉冲轰炸者：能量球体
                pygame.draw.circle(preview, enemy_color, (center, 75), 30)
                pygame.draw.circle(preview, light_color, (center, 75), 30, 3)
                # 能量脉冲环
                pygame.draw.circle(preview, light_color, (center, 75), 40, 2)
                pygame.draw.circle(preview, (150, 230, 255), (center, 75), 48, 1)
                # 内部能量核
                pygame.draw.circle(preview, (200, 255, 255), (center, 75), 15)
                pygame.draw.circle(preview, (255, 255, 255), (center, 75), 8)
                # 脉冲射线
                import math
                for i in range(8):
                    angle = i * 45
                    rad = math.radians(angle)
                    x1 = center + int(20 * math.cos(rad))
                    y1 = 75 + int(20 * math.sin(rad))
                    x2 = center + int(35 * math.cos(rad))
                    y2 = 75 + int(35 * math.sin(rad))
                    pygame.draw.line(preview, light_color, (x1, y1), (x2, y2), 2)
            elif enemy_id == "laser_sentinel":
                # 激光哨兵：红色激光眼球
                pygame.draw.circle(preview, (80, 80, 90), (center, 75), 35)
                pygame.draw.circle(preview, (100, 100, 110), (center, 75), 35, 3)
                pygame.draw.circle(preview, (200, 30, 30), (center, 75), 25)
                pygame.draw.circle(preview, enemy_color, (center, 75), 25, 2)
                pygame.draw.circle(preview, (150, 20, 20), (center, 75), 18)
                pygame.draw.circle(preview, (255, 100, 100), (center, 75), 10)
                pygame.draw.circle(preview, (255, 200, 200), (center, 75), 5)
                # 激光瞄准十字
                pygame.draw.line(preview, (255, 50, 50), (center - 45, 75), (center - 28, 75), 2)
                pygame.draw.line(preview, (255, 50, 50), (center + 28, 75), (center + 45, 75), 2)
                pygame.draw.line(preview, (255, 50, 50), (center, 30), (center, 47), 2)
                pygame.draw.line(preview, (255, 50, 50), (center, 103), (center, 120), 2)
            elif enemy_id == "shadow_assassin":
                # 暗影刺客：隐匿三角飞镖
                points = [(center, 25), (center - 35, 110), (center, 85), (center + 35, 110)]
                pygame.draw.polygon(preview, dark_color, points)
                pygame.draw.polygon(preview, enemy_color, points)
                pygame.draw.polygon(preview, (100, 40, 130), points, 3)
                # 暗影效果层
                for i in range(3):
                    alpha_surf = pygame.Surface((150, 150), pygame.SRCALPHA)
                    offset = i * 3
                    shadow_points = [(center, 25 + offset), (center - 35 + offset, 110), 
                                    (center, 85), (center + 35 - offset, 110)]
                    pygame.draw.polygon(alpha_surf, (*enemy_color[:3], 60 - i * 15), shadow_points)
                    preview.blit(alpha_surf, (0, 0))
                # 核心能量
                pygame.draw.circle(preview, (150, 80, 180), (center, 70), 10)
                pygame.draw.circle(preview, (200, 150, 220), (center, 70), 5)
            elif enemy_id == "minelayer_drone":
                # 布雷无人机：工业风格
                pygame.draw.rect(preview, dark_color, (center - 25, 50, 50, 40))
                pygame.draw.rect(preview, enemy_color, (center - 23, 52, 46, 36))
                pygame.draw.rect(preview, light_color, (center - 25, 50, 50, 40), 2)
                # 布雷舱门
                pygame.draw.rect(preview, (100, 100, 30), (center - 15, 80, 30, 15))
                pygame.draw.line(preview, (80, 80, 20), (center, 80), (center, 95), 2)
                # 推进器
                pygame.draw.rect(preview, (80, 80, 90), (center - 35, 55, 10, 20))
                pygame.draw.rect(preview, (80, 80, 90), (center + 25, 55, 10, 20))
                # 推进火焰
                pygame.draw.polygon(preview, (255, 150, 50), 
                                  [(center - 35, 75), (center - 45, 65), (center - 35, 55)])
                pygame.draw.polygon(preview, (255, 150, 50), 
                                  [(center + 35, 75), (center + 45, 65), (center + 35, 55)])
                # 警示灯
                pygame.draw.circle(preview, (255, 200, 0), (center, 58), 6)
                pygame.draw.circle(preview, (255, 255, 150), (center, 58), 3)
            elif enemy_id == "gatling_fortress":
                # 加特林堡垒：重型六边形堡垒
                import math
                hex_points = [(center + int(40 * math.cos(math.radians(i * 60 - 90))),
                              75 + int(40 * math.sin(math.radians(i * 60 - 90)))) for i in range(6)]
                pygame.draw.polygon(preview, dark_color, hex_points)
                pygame.draw.polygon(preview, enemy_color, hex_points)
                pygame.draw.polygon(preview, (80, 80, 100), hex_points, 4)
                # 内层装甲
                inner_hex = [(center + int(25 * math.cos(math.radians(i * 60 - 90))),
                             75 + int(25 * math.sin(math.radians(i * 60 - 90)))) for i in range(6)]
                pygame.draw.polygon(preview, (120, 120, 140), inner_hex, 2)
                # 加特林炮管组
                for i in range(6):
                    angle = i * 60
                    rad = math.radians(angle)
                    bx = center + int(12 * math.cos(rad))
                    pygame.draw.rect(preview, (60, 60, 70), (bx - 3, 30, 6, 30))
                    pygame.draw.circle(preview, (255, 200, 50), (bx, 30), 4)
                # 中心旋转机构
                pygame.draw.circle(preview, (150, 150, 160), (center, 55), 12)
                pygame.draw.circle(preview, (100, 100, 110), (center, 55), 8)
                # 弹药指示灯
                pygame.draw.circle(preview, (255, 50, 50), (center - 12, 95), 4)
                pygame.draw.circle(preview, (50, 255, 50), (center + 12, 95), 4)
            else:
                # 默认：梭形战机
                pygame.draw.polygon(preview, dark_color, [(center, 25), (55, 75), (center, 125), (95, 75)])
                pygame.draw.polygon(preview, enemy_color, [(center, 30), (55, 75), (center, 120), (95, 75)])
                pygame.draw.polygon(preview, light_color, [(center, 30), (55, 75), (center, 120), (95, 75)], 2)
        
        if codex_tab != 2:
            preview = pygame.transform.scale(preview, (150, 150))
        safe_blit(screen, preview, (cx - 75, cy))
        
        draw_text(screen, data["name"], 30, cx, cy + 170, data.get("color", WHITE), glow=True)
        
        # 多行描述显示
        desc = data.get("desc", "")
        desc_lines = 0
        if desc:
            # 按字符宽度换行，每行约40个中文字符
            max_chars_per_line = 40
            lines = []
            for i in range(0, len(desc), max_chars_per_line):
                lines.append(desc[i:i+max_chars_per_line])
            
            desc_y = cy + 210
            desc_lines = len(lines)
            for line in lines:
                draw_text(screen, line, 16, cx, desc_y, WHITE)
                desc_y += 28
        
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
        
        # 根据描述行数动态调整统计信息位置
        desc_offset = (desc_lines - 1) * 28 if desc_lines > 1 else 0
            
        for j, (lbl, val, mxv) in enumerate(stats):
            y_off = cy + 260 + desc_offset + j*stat_spacing
            draw_text(screen, lbl, 18, r['detail_area'].x + 150, y_off, WHITE, align="left")
            pygame.draw.rect(screen, (40,40,40), (r['detail_area'].x + 230, y_off+5, 200, 10))
            fill = min(200, (val/mxv)*200)
            pygame.draw.rect(screen, data.get("color", WHITE), (r['detail_area'].x + 230, y_off+5, fill, 10))
        
        # 敌人图鉴额外显示分数
        if codex_tab == 2:
            score_y = cy + 260 + desc_offset + len(stats) * stat_spacing + 5
            draw_text(screen, f"分数: {data.get('score', 100)}", 16, r['detail_area'].x + 150, score_y, GOLD, align="left")

    hb = r['btn_back'].collidepoint(mx, my)
    draw_cyber_rect(screen, r['btn_back'], GRAY, fill=True)
    if hb: draw_cyber_rect(screen, r['btn_back'], WHITE, border_width=2, fill=False)
    draw_text(screen, "返回", 20, r['btn_back'].centerx, r['btn_back'].centery-10, WHITE)

def draw_gallery_ui():
    draw_text(screen, "战术图鉴", 40, WIDTH//2, 30, MAGENTA, glow=True)
    mx, my = pygame.mouse.get_pos()
    
    # 按1-4星品质分类
    tab_labels = ["全部", "1★普通", "2★稀有", "3★史诗", "4★传说"]
    tab_colors = [WHITE, (150, 150, 150), (100, 200, 255), (200, 100, 255), (255, 200, 50)]
    tab_w = 110
    start_tx = (WIDTH - (5 * tab_w + 40)) // 2
    
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
    
    # 按品质筛选 (tab 0=全部, 1=1星, 2=2星, 3=3星, 4=4星)
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
        
        # 显示卡牌类型标签
        if "data" in item:
            type_label = {"base": "基础", "modifier": "参数", "synergy": "协同"}.get(item["type"], "")
            draw_text(screen, f"[{type_label}]", 15, x+15, y+48, rc, align="left")
            
            # 显示类别和流派
            card_data = item["data"]
            info_parts = []
            
            # 类别汉化
            if "category" in card_data:
                category_names = {
                    "attack": "攻击", "defense": "防御", 
                    "special": "特殊", "system": "系统"
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
                draw_text(screen, info_text, 14, x+120, y+48, (180, 180, 200))
            
            # 显示效果 - 属性名全面汉化
            attr_names = {
                "bullet_count": "弹幕", "damage_mult": "伤害", "speed_mult": "速度",
                "split_count": "分裂", "split_damage": "分裂伤", "pierce": "穿透",
                "fire_rate": "射速", "explosion_radius": "爆炸范围", "explosion_mult": "爆炸伤害",
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
                "summon_count_mult": "召唤数量倍率", "summon_ai": "AI模式",
                "bullet_count_mult": "弹幕倍率", "all_bullets_explode": "全弹爆炸",
                "infinite_pierce": "无限穿透", "slow_on_hit": "击中减速", "global_slow": "全局减速",
                "split_level": "分裂层数"
            }
            
            # 解析效果
            desc_lines = []
            if "base_effect" in card_data:
                effect = card_data["base_effect"]
                for k, v in list(effect.items())[:3]:
                    if isinstance(v, (int, float)):
                        cn_name = attr_names.get(k, k)
                        if "mult" in k or "chance" in k or k.endswith("_mult"):
                            if v >= 1:
                                desc_lines.append(f"{cn_name}+{int((v-1)*100)}%")
                            else:
                                desc_lines.append(f"{cn_name}×{v:.1f}")
                        elif isinstance(v, bool):
                            if v:
                                desc_lines.append(cn_name)
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
                                desc_lines.append(f"{cn_name}×{v:.1f}")
                            else:
                                desc_lines.append(f"{cn_name}+{v}")
            
            # 卡牌描述 - 更大更清晰
            desc = item.get('desc', '')
            if desc:
                # 分行显示描述
                lines = [desc[k:k+22] for k in range(0, len(desc), 22)][:2]
                for k, line in enumerate(lines):
                    draw_text(screen, line, 16, x+15, y+75+k*22, (200, 200, 220), align="left")
            
            # 显示效果信息
            if desc_lines:
                effect_y = y+120 if desc else y+85
                effect_text = " ".join(desc_lines[:3])  # 最多显示3个效果
                lines = [effect_text[k:k+24] for k in range(0, len(effect_text), 24)][:2]
                for k, line in enumerate(lines):
                    draw_text(screen, line, 15, x+15, effect_y+k*20, (150, 220, 255), align="left")
            
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
        categories = [None, "common", "rare", "epic", "legendary", "exclusive"]
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
        
        for i, (theme_id, theme, is_bullet) in enumerate(filtered_themes):
            card_rect = pygame.Rect(350, theme_y_start + i * 100 - customization_scroll_y, 560, 90)
            
            if card_rect.bottom < 100 or card_rect.top > HEIGHT - 80:
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
                exclusive_plane = theme.get("exclusive_plane")
                if exclusive_plane and exclusive_plane != customization_selected_plane:
                    customization_msg = f"该涂装仅限 {PLANES[exclusive_plane]['name']} 使用"
                    customization_msg_timer = 120
                    sound_mgr.play("warning")
                    continue

                if is_unlocked:
                    success, msg = customization_manager.equip_theme(customization_selected_plane, theme_id)
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
                draw_bullet_preview(screen, theme, card_rect.x + 10, card_rect.y + 15, 60)
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
            draw_bullet_preview(screen, theme, preview_x, preview_y, preview_size)
            
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

def draw_top_hud():
    """绘制四角布局HUD: 顶左(倾斜条+数值) + 顶右(积分/时间) + 底左(主炮/飞机/核心) + 底右(武器/大招) + 底部(经验条)"""
    if player is None:
        return
    
    # ===== 顶部左侧：护盾/血量/推进器三个倾斜进度条 + 数值标签 =====
    bar_x = 12
    bar_y = 10
    bar_w = 280
    bar_h_base = 13
    bar_gap = 28  # 增加间距从 22 到 28，防止条形重合
    tilt = 12
    label_x = bar_x + bar_w + 16
    hp_label_x = bar_x + bar_w + 80  # 血量文字更靠右，避免被血量条覆盖
    
    # 护盾条 (青色/CYAN) - 百分比基于护盾上限计算,若无上限则以max_hp为上限
    shield_max = player.max_shield if player.max_shield > 0 else player.max_hp
    shield_pct = (player.shield / max(1, shield_max) * 100) if shield_max > 0 else 0
    draw_slanted_bar(screen, bar_x, bar_y, bar_w, bar_h_base, shield_pct, CYBER_CYAN_BRIGHT, 
                     bg_color=(0, 40, 50), tilt=tilt, border_color=CYAN, border_width=1)
    draw_text(screen, "护盾", 16, label_x, bar_y - 1, CYBER_CYAN_BRIGHT, glow=True, align='left')
    # 只在有护盾或有max_shield时显示数值
    if player.shield > 0 or player.max_shield > 0:
        display_max = player.max_shield if player.max_shield > 0 else player.max_hp
        draw_text(screen, f"{int(player.shield)}/{int(display_max)}", 14, label_x + 45, bar_y + 1, WHITE, align='left')
    else:
        draw_text(screen, "--/--", 14, label_x + 45, bar_y + 1, (100, 100, 100), align='left')
    
    # 血量条 (红色，更长更粗)
    hp_pct = (player.hp / player.max_hp * 100) if player.max_hp > 0 else 0
    hp_color = CYBER_RED_ALERT if hp_pct < 30 else (CYBER_AMBER if hp_pct < 60 else CYBER_LIME)
    draw_slanted_bar(screen, bar_x, bar_y + bar_gap, bar_w + 60, int(bar_h_base * 1.8), hp_pct, hp_color, 
                     bg_color=(50, 15, 15), tilt=tilt, border_color=CYBER_RED_ALERT, border_width=1)
    draw_text(screen, "生命", 16, hp_label_x, bar_y + bar_gap + 2, hp_color, glow=True, align='left')
    draw_text(screen, f"{int(player.hp)}/{int(player.max_hp)}", 14, hp_label_x + 45, bar_y + bar_gap + 4, WHITE, align='left')
    
    # 推进器条 (紫色/MAGENTA)
    thruster_pct = (player.dash_energy / player.max_dash_energy * 100) if player.max_dash_energy > 0 else 0
    draw_slanted_bar(screen, bar_x, bar_y + bar_gap*2, bar_w, bar_h_base, thruster_pct, MAGENTA, 
                     bg_color=(40, 15, 40), tilt=tilt, border_color=MAGENTA, border_width=1)
    draw_text(screen, "推进", 16, label_x, bar_y + bar_gap*2 - 1, MAGENTA, glow=True, align='left')
    draw_text(screen, f"{int(player.dash_energy)}/{int(player.max_dash_energy)}", 14, label_x + 45, bar_y + bar_gap*2 + 1, WHITE, align='left')
    
    # 【霓虹突击者】超载层数显示
    if hasattr(player, 'plane_id') and player.plane_id == "striker":
        if hasattr(player, 'overdrive_hits') and player.overdrive_hits > 0:
            overdrive_pct = (player.overdrive_hits / 10) * 100  # 最大10层
            # 超载条 (青色渐变到金色)
            overdrive_color = CYAN if player.overdrive_hits < 10 else GOLD
            draw_slanted_bar(screen, bar_x, bar_y + bar_gap*3, bar_w, bar_h_base, overdrive_pct, overdrive_color, 
                           bg_color=(20, 40, 50), tilt=tilt, border_color=overdrive_color, border_width=1)
            # 标签和层数
            bonus_text = f"+{int(player.overdrive_bonus * 100)}%"
            draw_text(screen, "超载", 16, label_x, bar_y + bar_gap*3 - 1, overdrive_color, glow=True, align='left')
            draw_text(screen, f"{player.overdrive_hits}/10 ({bonus_text})", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
    
    # 【幽灵收割者】灵魂数量显示
    if hasattr(player, 'plane_id') and player.plane_id == "specter":
        souls = getattr(player, 'souls', 0)
        if souls > 0:
            soul_pct = (souls / 30) * 100  # 最大30灵魂
            # 灵魂条 (紫色)
            soul_color = (150, 100, 255) if souls < 30 else (200, 150, 255)
            draw_slanted_bar(screen, bar_x, bar_y + bar_gap*3, bar_w, bar_h_base, soul_pct, soul_color, 
                           bg_color=(30, 20, 50), tilt=tilt, border_color=soul_color, border_width=1)
            # 计算加成
            crit_bonus = int(souls * 2)  # 暴击率加成
            dmg_bonus = int(souls * 5)   # 暴击伤害加成
            draw_text(screen, "灵魂", 16, label_x, bar_y + bar_gap*3 - 1, soul_color, glow=True, align='left')
            draw_text(screen, f"{souls}/30 (暴击+{crit_bonus}%)", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
    
    # 【绯红之刃】鲜血狂热层数显示
    if hasattr(player, 'plane_id') and player.plane_id == "crimson":
        stacks = getattr(player, 'blood_stacks', 0)
        if stacks > 0:
            max_stacks = max(1, getattr(player, 'max_blood_stacks', 25))
            stack_ratio = stacks / max_stacks
            bar_pct = stack_ratio * 100
            blood_color = (int(150 + 80 * stack_ratio), int(40 + 120 * stack_ratio), int(60 + 80 * stack_ratio))
            draw_slanted_bar(screen, bar_x, bar_y + bar_gap*3, bar_w, bar_h_base, bar_pct, blood_color, 
                             bg_color=(40, 10, 20), tilt=tilt, border_color=blood_color, border_width=1)
            lifesteal_pct = int((0.04 + 0.12 * stack_ratio) * 100)
            draw_text(screen, "血契", 16, label_x, bar_y + bar_gap*3 - 1, blood_color, glow=True, align='left')
            draw_text(screen, f"{stacks}/{max_stacks} (吸血{lifesteal_pct}%)", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
    
    # 【星界潜行者】暗影标记数显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "stalker":
        marks = getattr(player, 'shadow_marks', 0)
        max_marks = max(1, getattr(player, 'max_shadow_marks', 8))
        mark_ratio = marks / max_marks if marks > 0 else 0
        bar_pct = mark_ratio * 100
        mark_color = (int(75 + 50 * mark_ratio), int(0 + 80 * mark_ratio), int(130 + 80 * mark_ratio)) if marks > 0 else (60, 40, 100)
        draw_slanted_bar(screen, bar_x, bar_y + bar_gap*3, bar_w, bar_h_base, bar_pct, mark_color, 
                         bg_color=(20, 10, 40), tilt=tilt, border_color=mark_color, border_width=1)
        dmg_bonus_pct = int(marks * 4)
        draw_text(screen, "星痕", 16, label_x, bar_y + bar_gap*3 - 1, mark_color, glow=True, align='left')
        draw_text(screen, f"{marks}/{max_marks} (伤害+{dmg_bonus_pct}%)", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
    
    # 【大地守护者】大地怒气显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "gaia":
        fury = getattr(player, 'earth_fury', 0)
        max_fury = max(1, getattr(player, 'max_earth_fury', 100))
        fury_ratio = fury / max_fury if fury > 0 else 0
        bar_pct = fury_ratio * 100
        fury_color = (int(60 + 100 * fury_ratio), int(140 + 80 * fury_ratio), int(40 + 60 * fury_ratio)) if fury > 0 else (50, 100, 40)
        draw_slanted_bar(screen, bar_x, bar_y + bar_gap*3, bar_w, bar_h_base, bar_pct, fury_color, 
                         bg_color=(20, 35, 15), tilt=tilt, border_color=fury_color, border_width=1)
        armor_pct = int(fury_ratio * 50)
        dmg_pct = int(fury_ratio * 80)
        atk_spd_pct = int(fury_ratio * 30)
        draw_text(screen, "怒气", 16, label_x, bar_y + bar_gap*3 - 1, fury_color, glow=True, align='left')
        draw_text(screen, f"{int(fury)} (护{armor_pct}%/伤{dmg_pct}%/速{atk_spd_pct}%)", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
    
    # 【钢铁泰坦】过载能量 + 装甲显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "titan":
        overload = getattr(player, 'titan_overload', 0)
        armor_stacks = getattr(player, 'titan_armor_stacks', 0)
        max_overload = max(1, getattr(player, 'max_titan_overload', 100))
        overload_ratio = overload / max_overload if overload > 0 else 0
        bar_pct = overload_ratio * 100
        overload_color = (int(200 + 55 * overload_ratio), int(120 - 60 * overload_ratio), int(50 - 50 * overload_ratio)) if overload > 0 else (150, 100, 50)
        draw_slanted_bar(screen, bar_x, bar_y + bar_gap*3, bar_w, bar_h_base, bar_pct, overload_color, 
                         bg_color=(40, 20, 10), tilt=tilt, border_color=overload_color, border_width=1)
        armor_reduction = int(armor_stacks * 8)
        status = "★就绪!" if overload >= 100 else f"{int(overload)}%"
        draw_text(screen, "过载", 16, label_x, bar_y + bar_gap*3 - 1, overload_color, glow=True, align='left')
        draw_text(screen, f"{status} (装甲{armor_stacks}层/-{armor_reduction}%伤)", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
    
    # 【虚空编织者】维度织网显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "weaver":
        webbed = getattr(player, 'weaver_webbed_count', 0)
        bar_pct = min(100, webbed * 12.5)  # 8个满
        web_color = (int(140 + 40 * (webbed/8)), int(140 + 40 * (webbed/8)), int(140 + 40 * (webbed/8))) if webbed > 0 else (100, 100, 100)
        draw_slanted_bar(screen, bar_x, bar_y + bar_gap*3, bar_w, bar_h_base, bar_pct, web_color, 
                         bg_color=(30, 30, 35), tilt=tilt, border_color=web_color, border_width=1)
        dmg_bonus = int(webbed * 6)
        draw_text(screen, "织网", 16, label_x, bar_y + bar_gap*3 - 1, web_color, glow=True, align='left')
        draw_text(screen, f"{webbed}个敌人被网 (+{dmg_bonus}%伤害)", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
    
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
        draw_slanted_bar(screen, bar_x, bar_y + bar_gap*3, bar_w, bar_h_base, bar_pct, heat_color, 
                         bg_color=(40, 20, 10), tilt=tilt, border_color=heat_color, border_width=1)
        dmg_bonus = int(heat_ratio * 60)
        if is_overheat:
            cooldown = getattr(player, 'solar_overheat_timer', 0)
            draw_text(screen, "过热", 16, label_x, bar_y + bar_gap*3 - 1, (255, 50, 0), glow=True, align='left')
            draw_text(screen, f"冷却中... ({cooldown//60}.{cooldown%60//6}秒)", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
        else:
            draw_text(screen, "热量", 16, label_x, bar_y + bar_gap*3 - 1, heat_color, glow=True, align='left')
            draw_text(screen, f"{int(heat)}% (+{dmg_bonus}%伤害)", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
    
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
        draw_slanted_bar(screen, bar_x, bar_y + bar_gap*3, bar_w, bar_h_base, bar_pct, quantum_color, 
                         bg_color=(30, 15, 40), tilt=tilt, border_color=quantum_color, border_width=1)
        if is_ready:
            draw_text(screen, "坍缩", 16, label_x, bar_y + bar_gap*3 - 1, (255, 150, 255), glow=True, align='left')
            draw_text(screen, "就绪! 下次攻击爆发!", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
        else:
            draw_text(screen, "量子", 16, label_x, bar_y + bar_gap*3 - 1, quantum_color, glow=True, align='left')
            draw_text(screen, f"{int(quantum)}%", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
    
    # 【日食幽灵】光暗交替显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "eclipse":
        phase = getattr(player, 'eclipse_phase', 'light')
        timer = getattr(player, 'eclipse_phase_timer', 0)
        shield = getattr(player, 'eclipse_shield', 0)
        phase_progress = timer / 300 * 100
        if phase == "light":
            light_bonus = int(getattr(player, 'eclipse_light_bonus', 0) * 100)
            phase_color = (255, 220, 100)
            draw_slanted_bar(screen, bar_x, bar_y + bar_gap*3, bar_w, bar_h_base, phase_progress, phase_color, 
                             bg_color=(40, 35, 15), tilt=tilt, border_color=phase_color, border_width=1)
            draw_text(screen, "光态", 16, label_x, bar_y + bar_gap*3 - 1, phase_color, glow=True, align='left')
            draw_text(screen, f"+{light_bonus}%伤害 ({int(5-timer/60)}秒)", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
        else:
            max_shield = getattr(player, 'max_eclipse_shield', 50)
            shield_pct = (shield / max_shield) * 100 if max_shield > 0 else 0
            phase_color = (100, 50, 180)
            draw_slanted_bar(screen, bar_x, bar_y + bar_gap*3, bar_w, bar_h_base, shield_pct, phase_color, 
                             bg_color=(20, 15, 35), tilt=tilt, border_color=phase_color, border_width=1)
            draw_text(screen, "暗态", 16, label_x, bar_y + bar_gap*3 - 1, phase_color, glow=True, align='left')
            draw_text(screen, f"护盾:{int(shield)} ({int(5-timer/60)}秒)", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
    
    # 【棱镜分光】折射风暴显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "prism":
        chain = getattr(player, 'prism_chain_count', 0)
        max_chain = getattr(player, 'prism_max_chain', 0)
        bar_pct = (chain / 5) * 100  # 5次满
        colors = [(100, 180, 255), (140, 140, 255), (180, 100, 255), (255, 100, 180), (255, 180, 100)]
        prism_color = colors[min(chain, len(colors)-1)] if chain > 0 else (80, 120, 160)
        draw_slanted_bar(screen, bar_x, bar_y + bar_gap*3, bar_w, bar_h_base, bar_pct, prism_color, 
                         bg_color=(25, 30, 40), tilt=tilt, border_color=prism_color, border_width=1)
        dmg_bonus = int(chain * 15)
        chain_text = f"折射x{chain}" if chain > 0 else "就绪"
        draw_text(screen, "棱镜", 16, label_x, bar_y + bar_gap*3 - 1, prism_color, glow=True, align='left')
        draw_text(screen, f"{chain_text} (+{dmg_bonus}%) 最高:{max_chain}", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
    
    # 【死灵骑士】亡灵军团显示 - 常驻
    if hasattr(player, 'plane_id') and player.plane_id == "necro":
        ghosts = getattr(player, 'necro_ghosts', [])
        ghost_count = len(ghosts)
        max_ghosts = getattr(player, 'max_necro_ghosts', 6)
        total_damage = int(getattr(player, 'necro_ghost_damage', 0))
        bar_pct = (ghost_count / max_ghosts) * 100
        necro_color = (int(150 + 50 * (ghost_count / max_ghosts)), 50, int(100 + 55 * (ghost_count / max_ghosts))) if ghost_count > 0 else (120, 50, 80)
        draw_slanted_bar(screen, bar_x, bar_y + bar_gap*3, bar_w, bar_h_base, bar_pct, necro_color, 
                         bg_color=(30, 15, 25), tilt=tilt, border_color=necro_color, border_width=1)
        draw_text(screen, "亡灵", 16, label_x, bar_y + bar_gap*3 - 1, necro_color, glow=True, align='left')
        draw_text(screen, f"{ghost_count}/{max_ghosts} 总伤害:{total_damage}", 14, label_x + 45, bar_y + bar_gap*3 + 1, WHITE, align='left')
    
    # ===== 顶部右侧：积分和时间（创意特效面板） =====
    score_value_x = WIDTH - 24  # 数值右对齐位置
    score_y = 12
    label_x_right = score_value_x - 140  # 标签固定位置
    
    # 【得分区域】创意显示
    score_box_y = score_y
    score_box_h = 50
    score_box_w = 155
    score_box_x = label_x_right - 8
    
    # 背景框 + 渐变效果
    pygame.draw.rect(screen, (10, 10, 30), (score_box_x, score_box_y, score_box_w, score_box_h))
    pygame.draw.rect(screen, SCORE_ORANGE, (score_box_x, score_box_y, score_box_w, score_box_h), 2)
    
    # 顶部装饰线条 - 闪烁动画
    deco_brightness = int(100 + 155 * abs(math.sin(pygame.time.get_ticks() / 400)))
    pygame.draw.line(screen, (deco_brightness, int(deco_brightness * 0.6), 0), 
                    (score_box_x + 2, score_box_y + 2), (score_box_x + score_box_w - 2, score_box_y + 2), 2)
    
    # 得分标签 + 数值
    draw_text(screen, "得分", 14, label_x_right, score_box_y + 8, SCORE_ORANGE, align='left')
    
    # 得分数值 - 跳动效果 + 发光
    pulse_y = int(3 * math.sin(pygame.time.get_ticks() / 300))
    score_text = f"{int(score):,}"  # 千位分隔符
    # 外层阴影
    draw_text(screen, score_text, 35, score_value_x + 2, score_y + 5 + pulse_y, (100, 50, 0), align='right', glow=False)
    # 主体 + 发光
    draw_text(screen, score_text, 35, score_value_x, score_y + 3 + pulse_y, SCORE_ORANGE, glow=True, align='right')
    
    # 【时间区域】创意显示
    time_box_y = score_y + 56
    time_box_h = 50
    time_box_w = 155
    time_box_x = label_x_right - 8
    
    # 背景框 + 渐变效果
    pygame.draw.rect(screen, (10, 10, 30), (time_box_x, time_box_y, time_box_w, time_box_h))
    pygame.draw.rect(screen, CYAN, (time_box_x, time_box_y, time_box_w, time_box_h), 2)
    
    # 顶部装饰线条 - 同步闪烁
    pygame.draw.line(screen, (0, deco_brightness, deco_brightness), 
                    (time_box_x + 2, time_box_y + 2), (time_box_x + time_box_w - 2, time_box_y + 2), 2)
    
    # 时间标签 + 数值
    draw_text(screen, "时间", 14, label_x_right, time_box_y + 8, CYAN, align='left')
    
    # 时间 MM:SS 格式
    elapsed_sec = int(pygame.time.get_ticks() / 1000)
    elapsed_min = elapsed_sec // 60
    elapsed_sec_remain = elapsed_sec % 60
    time_text = f"{elapsed_min:02d}:{elapsed_sec_remain:02d}"
    
    # 时间数值 - 闪烁脉冲
    time_pulse = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() / 500)
    time_size = int(32 * time_pulse)
    draw_text(screen, time_text, time_size, score_value_x, time_box_y + 4, CYAN, glow=True, align='right')
    
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
    
    # ===== 底部右侧：武器库 / 三个武器槽 / 大招 / 储能条 =====
    bottom_right_x = WIDTH - 24
    bottom_right_y = HEIGHT - 165  # 与左侧对齐
    
    # 三个武器槽（隔一点距离，放大）
    slot_w = 40
    slot_h = 40
    slot_gap = 8
    slot_total_w = slot_w * 3 + slot_gap * 2
    slot_start_x = bottom_right_x - slot_total_w - 12
    slot_y = bottom_right_y + 22
    
    # 僚机标签 - 显示当前僚机信息
    wingman_count = len(player.wingman_squadron.wingmen) if player.wingman_squadron else 0
    wingman_max = player.max_wingmen if hasattr(player, 'max_wingmen') else 4
    wingman_text = f"僚机 {wingman_count}/{wingman_max}"
    second_weapon_x = slot_start_x + 1 * (slot_w + slot_gap) + slot_w // 2
    draw_text(screen, wingman_text, 13, second_weapon_x, slot_y - 18, CYAN, glow=True, align='center')
    
    # 僚机编队脉冲效果 - 青色闪烁
    wingman_pulse = abs(math.sin(pygame.time.get_ticks() / 600))
    wingman_color = (0, 100 + int(155 * wingman_pulse), 200)  # 青色脉冲
    pygame.draw.line(screen, wingman_color, (second_weapon_x - 30, slot_y - 25), (second_weapon_x + 30, slot_y - 25), 2)
    
    for i in range(3):
        slot_x = slot_start_x + i * (slot_w + slot_gap)
        slot_rect = pygame.Rect(slot_x, slot_y, slot_w, slot_h)
        weapon = player.weapon_slots[i] if i < len(player.weapon_slots) else None
        is_current = (i == player.current_slot)  # 检查是否为当前使用的武器
        
        if weapon:
            # Weapon box with color
            w_info = WEAPON_TYPES.get(weapon.type, {})
            col = w_info.get('color', (100, 100, 100))
            # 显示武器名称首字
            w_name = w_info.get('name', '？')[:2]
            draw_text(screen, w_name, 14, slot_rect.centerx, slot_rect.centery - 4, WHITE, align='center')
        else:
            col = (60, 60, 60)
        
        # 当前使用的武器槽添加发光效果
        border_color = CYBER_LIME if is_current else (100, 100, 100)
        border_width = 3 if is_current else 2
        alpha_val = 220 if is_current else 200
        
        draw_cyber_rect(screen, slot_rect, col, alpha=alpha_val, border_width=border_width, fill=True)
        
        # CD冷却显示：在武器槽上方显示CD数字
        if weapon and weapon.cooldown > 0:
            cd_remaining = weapon.cooldown / 30  # 转换为秒（假设每秒30帧）
            draw_text(screen, f"{cd_remaining:.1f}s", 10, slot_rect.centerx, slot_rect.top - 14, CYBER_RED_ALERT, align='center')
            # 在槽上显示半透明黑色遮罩表示冷却中
            cd_overlay = pygame.Surface((slot_w, slot_h), pygame.SRCALPHA)
            cd_overlay.fill((0, 0, 0, 100))
            screen.blit(cd_overlay, (slot_x, slot_y))
        
        # 当前武器槽添加额外的发光框
        if is_current:
            glow_rect = pygame.Rect(slot_x - 3, slot_y - 3, slot_w + 6, slot_h + 6)
            draw_cyber_rect(screen, glow_rect, CYBER_LIME, alpha=100, border_width=1, fill=False)
    
    # ===== 大招能量条系统（连续进度条设计）=====
    ult_bar_width = 140  # 能量条宽度
    ult_bar_x = bottom_right_x - ult_bar_width  # 右对齐
    
    # --- 主大招 [F] ---
    ult_name = player.plane_data.get('ult_name', 'ULT')
    ult1_y = slot_y + 40  # 上移30像素
    
    # 主大招标签和百分比
    ult_ratio = player.ult_charge / player.max_ult_charge if player.max_ult_charge > 0 else 0
    ult_pct = int(ult_ratio * 100)
    ult_ready = ult_ratio >= 1.0 and player.ult_cooldown <= 0
    
    # 标签颜色：满能量时高亮
    label_color = CYBER_CYAN_BRIGHT if ult_ready else MAGENTA
    draw_text(screen, f"[F] {ult_name}", 12, ult_bar_x, ult1_y, label_color, align='left', glow=ult_ready)
    
    # 主大招能量条（高度14）
    bar1_y = ult1_y + 14
    bar1_h = 14
    bar1_rect = pygame.Rect(ult_bar_x, bar1_y, ult_bar_width, bar1_h)
    
    # 背景
    pygame.draw.rect(screen, (40, 20, 50), bar1_rect)
    pygame.draw.rect(screen, (80, 40, 90), bar1_rect, 1)
    
    # 填充
    if ult_ratio > 0:
        fill_w = int(ult_bar_width * min(ult_ratio, 1.0))
        fill_rect = pygame.Rect(ult_bar_x, bar1_y, fill_w, bar1_h)
        
        if ult_ready:
            # 满能量：渐变+闪烁效果
            pulse = abs(math.sin(pygame.time.get_ticks() / 200))
            glow_color = (200 + int(55 * pulse), 50 + int(50 * pulse), 200 + int(55 * pulse))
            pygame.draw.rect(screen, glow_color, fill_rect)
            # 发光边框
            pygame.draw.rect(screen, CYBER_CYAN_BRIGHT, fill_rect, 2)
        else:
            # 充能中：紫红色渐变
            pygame.draw.rect(screen, MAGENTA, fill_rect)
            # 充能动画条纹
            stripe_offset = (pygame.time.get_ticks() // 50) % 10
            for sx in range(ult_bar_x + stripe_offset, ult_bar_x + fill_w, 10):
                if sx < ult_bar_x + fill_w - 2:
                    pygame.draw.line(screen, (255, 150, 255), (sx, bar1_y + 2), (sx + 4, bar1_y + bar1_h - 2), 1)
    
    # 百分比文字
    pct_color = CYBER_CYAN_BRIGHT if ult_ready else WHITE
    draw_text(screen, f"{ult_pct}%", 12, ult_bar_x + ult_bar_width + 5, bar1_y + 2, pct_color, align='left')
    
    # 冷却显示
    if player.ult_cooldown > 0:
        cd_sec = player.ult_cooldown / 60.0
        # 冷却遮罩
        cd_overlay = pygame.Surface((ult_bar_width, bar1_h), pygame.SRCALPHA)
        cd_overlay.fill((0, 0, 0, 150))
        screen.blit(cd_overlay, (ult_bar_x, bar1_y))
        draw_text(screen, f"CD {cd_sec:.1f}s", 11, ult_bar_x + ult_bar_width // 2, bar1_y + 2, CYBER_RED_ALERT, align='center')
    
    # --- 副大招 [G] ---
    ult2_names = {
        "striker": "欧米伽激光", "phantom": "分身乱舞", "titan": "陨石轰炸",
        "thunderbird": "连锁闪电", "viper": "酸雨倾盆", "specter": "亡魂哀嚎",
        "aurora": "极光冲击波", "crimson": "刀刃风暴", "stalker": "引力陷阱",
        "gaia": "岩石护盾", "weaver": "蛛网陷阱", "solar": "太阳耀斑",
        "arbiter": "数据腐蚀", "eclipse": "暗物质爆发", "prism": "彩虹碎裂",
        "necro": "生命汲取", "void": "虚空撕裂"
    }
    ult2_name = ult2_names.get(player.plane_id, '次级技能')
    ult2_y = bar1_y + bar1_h + 3
    
    # 副大招标签和百分比
    ult2_ratio = player.ult2_charge / player.max_ult2_charge if player.max_ult2_charge > 0 else 0
    ult2_pct = int(ult2_ratio * 100)
    ult2_ready = ult2_ratio >= 1.0 and player.ult2_cooldown <= 0
    
    # 标签颜色
    label2_color = CYBER_LIME if ult2_ready else CYAN
    draw_text(screen, f"[G] {ult2_name}", 11, ult_bar_x, ult2_y, label2_color, align='left', glow=ult2_ready)
    
    # 副大招能量条（高度12）
    bar2_y = ult2_y + 13
    bar2_h = 12
    bar2_rect = pygame.Rect(ult_bar_x, bar2_y, ult_bar_width, bar2_h)
    
    # 背景
    pygame.draw.rect(screen, (20, 40, 50), bar2_rect)
    pygame.draw.rect(screen, (40, 80, 100), bar2_rect, 1)
    
    # 填充
    if ult2_ratio > 0:
        fill_w = int(ult_bar_width * min(ult2_ratio, 1.0))
        fill_rect = pygame.Rect(ult_bar_x, bar2_y, fill_w, bar2_h)
        
        if ult2_ready:
            # 满能量：闪烁
            pulse = abs(math.sin(pygame.time.get_ticks() / 250))
            glow_color = (50 + int(50 * pulse), 200 + int(55 * pulse), 200 + int(55 * pulse))
            pygame.draw.rect(screen, glow_color, fill_rect)
            pygame.draw.rect(screen, CYBER_LIME, fill_rect, 1)
        else:
            # 充能中：青色
            pygame.draw.rect(screen, CYAN, fill_rect)
            # 充能动画
            stripe_offset = (pygame.time.get_ticks() // 60) % 8
            for sx in range(ult_bar_x + stripe_offset, ult_bar_x + fill_w, 8):
                if sx < ult_bar_x + fill_w - 2:
                    pygame.draw.line(screen, (150, 255, 255), (sx, bar2_y + 1), (sx + 3, bar2_y + bar2_h - 1), 1)
    
    # 百分比文字
    pct2_color = CYBER_LIME if ult2_ready else WHITE
    draw_text(screen, f"{ult2_pct}%", 10, ult_bar_x + ult_bar_width + 5, bar2_y + 1, pct2_color, align='left')
    
    # 冷却显示
    if player.ult2_cooldown > 0:
        cd_sec = player.ult2_cooldown / 60.0
        cd_overlay = pygame.Surface((ult_bar_width, bar2_h), pygame.SRCALPHA)
        cd_overlay.fill((0, 0, 0, 150))
        screen.blit(cd_overlay, (ult_bar_x, bar2_y))
        draw_text(screen, f"CD {cd_sec:.1f}s", 10, ult_bar_x + ult_bar_width // 2, bar2_y + 1, CYBER_RED_ALERT, align='center')
    
    # --- 第三大招 [C] ---
    ult3_names = {
        "striker": "等离子漩涡", "phantom": "镜像分裂", "titan": "地震冲击",
        "thunderbird": "球状闪电", "viper": "腐蚀云雾", "specter": "灵魂风暴",
        "aurora": "北极光", "crimson": "刀刃旋风", "stalker": "重力炸弹",
        "gaia": "水晶屏障", "weaver": "蜘蛛群袭", "solar": "太阳光束",
        "arbiter": "病毒感染", "eclipse": "虚空坍缩", "prism": "光之棱镜",
        "necro": "灵魂收割", "void": "等离子漩涡"
    }
    ult3_name = ult3_names.get(player.plane_id, '终极技能')
    ult3_y = bar2_y + bar2_h + 3
    
    # 第三大招标签和百分比
    ult3_ratio = player.ult3_charge / player.max_ult3_charge if player.max_ult3_charge > 0 else 0
    ult3_pct = int(ult3_ratio * 100)
    ult3_ready = ult3_ratio >= 1.0 and player.ult3_cooldown <= 0
    
    # 标签颜色（橙黄色主题）
    label3_color = (255, 200, 50) if ult3_ready else (255, 165, 0)
    draw_text(screen, f"[C] {ult3_name}", 11, ult_bar_x, ult3_y, label3_color, align='left', glow=ult3_ready)
    
    # 第三大招能量条（高度12）
    bar3_y = ult3_y + 13
    bar3_h = 12
    bar3_rect = pygame.Rect(ult_bar_x, bar3_y, ult_bar_width, bar3_h)
    
    # 背景
    pygame.draw.rect(screen, (50, 40, 20), bar3_rect)
    pygame.draw.rect(screen, (100, 80, 40), bar3_rect, 1)
    
    # 填充
    if ult3_ratio > 0:
        fill_w = int(ult_bar_width * min(ult3_ratio, 1.0))
        fill_rect = pygame.Rect(ult_bar_x, bar3_y, fill_w, bar3_h)
        
        if ult3_ready:
            # 满能量：闪烁
            pulse = abs(math.sin(pygame.time.get_ticks() / 200))
            glow_color = (255, 180 + int(75 * pulse), 50 + int(50 * pulse))
            pygame.draw.rect(screen, glow_color, fill_rect)
            pygame.draw.rect(screen, (255, 220, 100), fill_rect, 1)
        else:
            # 充能中：橙色
            pygame.draw.rect(screen, (255, 165, 0), fill_rect)
            # 充能动画
            stripe_offset = (pygame.time.get_ticks() // 70) % 8
            for sx in range(ult_bar_x + stripe_offset, ult_bar_x + fill_w, 8):
                if sx < ult_bar_x + fill_w - 2:
                    pygame.draw.line(screen, (255, 220, 150), (sx, bar3_y + 1), (sx + 3, bar3_y + bar3_h - 1), 1)
    
    # 百分比文字
    pct3_color = (255, 220, 100) if ult3_ready else WHITE
    draw_text(screen, f"{ult3_pct}%", 10, ult_bar_x + ult_bar_width + 5, bar3_y + 1, pct3_color, align='left')
    
    # 冷却显示
    if player.ult3_cooldown > 0:
        cd_sec = player.ult3_cooldown / 60.0
        cd_overlay = pygame.Surface((ult_bar_width, bar3_h), pygame.SRCALPHA)
        cd_overlay.fill((0, 0, 0, 150))
        screen.blit(cd_overlay, (ult_bar_x, bar3_y))
        draw_text(screen, f"CD {cd_sec:.1f}s", 10, ult_bar_x + ult_bar_width // 2, bar3_y + 1, CYBER_RED_ALERT, align='center')
    
    # ===== 底部：厚的经验条，左侧显示等级 =====
    exp_bar_y = HEIGHT - 14
    exp_bar_h = 12
    exp_val = player.xp if hasattr(player, 'xp') else 0
    exp_max = player.next_level_xp if hasattr(player, 'next_level_xp') else 100
    exp_pct = (exp_val / exp_max * 100) if exp_max > 0 else 0
    
    # 背景
    pygame.draw.rect(screen, (15, 25, 15), (0, exp_bar_y, WIDTH, exp_bar_h))
    # 填充
    exp_fill_w = int((exp_pct / 100) * WIDTH)
    if exp_fill_w > 0:
        pygame.draw.rect(screen, CYBER_LIME, (0, exp_bar_y, exp_fill_w, exp_bar_h))
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
    
    # 底部属性组 - 紧凑卡片式
    stats_y = y_offset + 70
    
    # 火力 & 暴击率 - 并排显示
    stat_cards = [
        ("火力", f"{player.damage:.1f}", MAGENTA),
        ("暴击", f"{player.crit_chance * 100:.0f}%", (255, 100, 50)),
        ("穿透", f"{player.piercing if hasattr(player, 'piercing') else 0}", CYAN),
        ("弹数", f"{player.bullet_count if hasattr(player, 'bullet_count') else 1}", CYBER_LIME)
    ]
    
    for i, (name, value, color) in enumerate(stat_cards):
        col = i % 2
        row = i // 2
        
        card_x = left_x + col * 210
        card_y = stats_y + row * 52
        
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
        
        # 显示卡牌 - 2列布局
        for i, (card_name, card_level, card_color) in enumerate(card_display_list[:8]):  # 最多显示8张
            col = i % 2
            row = i // 2
            
            card_x = right_x + col * 255
            card_y = card_list_y + 25 + row * 38
            
            # 超出面板就停止
            if card_y > right_y + 360:
                remaining = len(card_display_list) - i
                if remaining > 0:
                    more_rect = pygame.Rect(right_x + 180, card_y - 5, 140, 30)
                    pygame.draw.rect(screen, (40, 40, 50, 200), more_rect, border_radius=8)
                    pygame.draw.rect(screen, GRAY, more_rect, 1, border_radius=8)
                    draw_text(screen, f"▼ 还有 {remaining} 张卡牌", 12, right_x + 250, card_y + 5, GRAY, align="center")
                break
            
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
    draw_text(screen, "▂▃▅ 选择升级卡牌 ▅▃▂", int(48 * title_scale), WIDTH//2, 100, title_color, glow=True)
    
    # 副标题
    subtitle_alpha = int(150 + 50 * abs(math.sin(t / 300)))
    draw_text(screen, f"等级 {player.level} → {player.level + 1}", 20, WIDTH//2, 145, (*LIME[:3], subtitle_alpha))
    
    # 3 个升级卡牌
    card_width = 300
    card_height = 440
    gap = 50
    total_width = 3 * card_width + 2 * gap
    start_x = (WIDTH - total_width) // 2
    start_y = 190
    
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
            
            # 卡牌图标/装饰
            icon_y = card_y + 70
            icon_size = 60
            icon_color = (*border_color[:3], 150)
            
            # 根据卡牌类型绘制不同图标
            if "attack" in card_data.get("category", ""):
                # 攻击图标 - 剑
                pygame.draw.polygon(screen, icon_color, [
                    (card_rect.centerx, icon_y - icon_size//2),
                    (card_rect.centerx - icon_size//3, icon_y + icon_size//2),
                    (card_rect.centerx + icon_size//3, icon_y + icon_size//2)
                ])
            elif "defense" in card_data.get("category", ""):
                # 防御图标 - 盾
                pygame.draw.ellipse(screen, icon_color, 
                    (card_rect.centerx - icon_size//2, icon_y - icon_size//2, icon_size, icon_size))
            elif "special" in card_data.get("category", ""):
                # 特殊图标 - 星星
                points = []
                for angle in range(0, 360, 72):
                    rad = math.radians(angle - 90)
                    px = card_rect.centerx + math.cos(rad) * icon_size // 2
                    py = icon_y + math.sin(rad) * icon_size // 2
                    points.append((px, py))
                pygame.draw.polygon(screen, icon_color, points)
            else:
                # 默认图标 - 齿轮
                pygame.draw.circle(screen, icon_color, (card_rect.centerx, icon_y), icon_size // 2, 3)
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    px = card_rect.centerx + math.cos(rad) * icon_size // 2
                    py = icon_y + math.sin(rad) * icon_size // 2
                    pygame.draw.circle(screen, icon_color, (int(px), int(py)), 5)
            
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
                if game_state == "customization":
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
                # 菜单子页：ESC 返回主菜单
                if event.key == pygame.K_ESCAPE and game_state in ["arsenal", "gallery", "codex", "leaderboard", "select_plane", "background_settings", "settings", "achievements", "customization"]:
                    game_state = "menu"
                    main_menu_selected = 0
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
                    if is_paused:
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
                                # 菜单使用normal BGM
                                sound_mgr.play_music("normal")
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
                        elif event.key == pygame.K_SPACE:
                            if player.skill_cd <= 0:
                                player.skill_cd = player.max_skill_cd
                                sound_mgr.play("dash")
                                create_shockwave(player.rect.center, CYAN, 20)
                                for m in mobs:
                                    if math.hypot(m.rect.centerx-player.rect.centerx, m.rect.centery-player.rect.centery) < 300:
                                        m.hp -= 200
                                        Particle(m.rect.center, CYAN)

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
                            elif act == "select_plane": game_state = "select_plane"; current_plane_idx = 0
                            elif act == "boss_challenge": game_state = "boss_challenge"; boss_challenge_selected = 0; boss_challenge_order = list(BOSS_DB.keys())
                            elif act in ["arsenal", "gallery", "codex", "leaderboard", "achievements", "customization", "background_settings", "settings"]:
                                game_state = act
                                if act == "gallery": gallery_page = 0; gallery_tab = 0
                                if act == "codex": codex_tab = 0; codex_idx = 0; codex_scroll_y = 0
                                if act == "arsenal": arsenal_scroll_y = 0; arsenal_selected_weapon_idx = -1
                                if act == "achievements": achievement_page = 0
                                if act == "customization": customization_scroll_y = 0; customization_plane_scroll_y = 0; customization_selected_plane = None; customization_tab = 0
                                if act == "background_settings": background_settings_selected = 0
                                if act == "settings": settings_dragging = None; settings_saved_timer = 0
                
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
                            sound_mgr.play_music("boss")
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
                
                if game_state == "menu":
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
                                game_state = "select_plane"
                                current_plane_idx = 0
                                log_info(f"Game state changed to: {game_state}")
                            elif act == "boss_challenge":
                                game_state = "boss_challenge"
                                boss_challenge_selected = 0
                                boss_challenge_order = list(BOSS_DB.keys())
                                log_info(f"Game state changed to: {game_state}")
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
                        game_state = "menu"
                    
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
                    # 5个稀有度标签点击检测: 全部/1星/2星/3星/4星
                    tab_width = 110
                    tab_gap = 10
                    total_tab_width = 5 * tab_width + 4 * tab_gap  # 5个标签,4个间隙
                    start_tab_x = (WIDTH - total_tab_width) // 2
                    
                    # 检测5个标签的点击
                    for i in range(5):
                        tab_x = start_tab_x + i * (tab_width + tab_gap)
                        tab_rect = pygame.Rect(tab_x, 80, tab_width, 40)
                        if tab_rect.collidepoint(mx, my):
                            gallery_tab = i  # 0=全部, 1=1星, 2=2星, 3=3星, 4=4星
                            gallery_page = 0
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
                            show_damage_numbers=game_settings.get("show_damage_numbers", True)
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
                    if levelup_paused and levelup_ready and upgrade_options:
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
                            # 菜单使用normal BGM
                            sound_mgr.play_music("normal")
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
            # drawing game view
            if is_paused:
                # TAB 发起的暂停使用专门的处理：按住 TAB 显示属性面板，释放恢复
                if tab_paused:
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
                else:
                    # 常规由 P / 菜单触发的暂停界面（原有行为）
                    all_sprites.draw(screen)
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

                    menu_items = [(btn_resume, "继续行动"), (btn_reset, "重新开始"), (btn_menu, "退出战斗")]
                    for i, (btn, txt) in enumerate(menu_items):
                        h = btn.collidepoint(mx, my) or (i == pause_menu_selected)
                        draw_cyber_rect(screen, btn, (60, 60, 80) if h else (40, 40, 50), fill=True)
                        border_color = CYAN if i == pause_menu_selected else (WHITE if h else GRAY)
                        border_width = 3 if i == pause_menu_selected else 2
                        draw_cyber_rect(screen, btn, border_color, border_width=border_width, fill=False)
                        draw_text(screen, txt, 24, btn.centerx, btn.centery - 12, WHITE if h else GRAY)

                    draw_text(screen, "按 P/R 操作或使用方向键+Enter", 18, WIDTH // 2, HEIGHT - 50, GRAY)

            else:
                # Auto Fire
                if not levelup_paused:
                    player.shoot()
                
                if global_time_freeze > 0:
                    global_time_freeze -= 1
                    # 【改进】时间冻结期间，处理敌方子弹的冻结状态
                    for eb in enemy_bullets:
                        eb.frozen = True
                    player.update()
                    
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
                                    if enemy.hp <= 0:
                                        score += 100 if enemy.is_elite else 20
                                        create_explosion(enemy.rect.center, (0, 255, 100), 5)
                                        sound_mgr.play("explosion")
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
                        
                        # 【霓虹突击者】超载模式计时器衰减
                        if hasattr(player, 'plane_id') and player.plane_id == "striker":
                            if hasattr(player, 'overdrive_timer') and player.overdrive_timer > 0:
                                player.overdrive_timer -= 1
                                if player.overdrive_timer <= 0:
                                    # 超载重置
                                    player.overdrive_hits = 0
                                    player.overdrive_bonus = 0
                        
                        # 【虚空幻影】相位无敌计时器衰减
                        if hasattr(player, 'phase_invuln') and player.phase_invuln > 0:
                            player.phase_invuln -= 1
                            # 无敌期间的视觉效果 - 紫色光环
                            if player.phase_invuln > 0 and random.random() < 0.3:
                                angle = random.uniform(0, math.pi * 2)
                                dist = random.uniform(15, 25)
                                px = player.rect.centerx + math.cos(angle) * dist
                                py = player.rect.centery + math.sin(angle) * dist
                                Particle((int(px), int(py)), MAGENTA)
                        
                        # 【幽灵收割者】灵魂衰减（每2秒流失1个灵魂）
                        if hasattr(player, 'plane_id') and player.plane_id == "specter":
                            if hasattr(player, 'souls') and player.souls > 0:
                                if not hasattr(player, 'soul_decay_timer'):
                                    player.soul_decay_timer = 0
                                player.soul_decay_timer += 1
                                if player.soul_decay_timer >= 120:  # 2秒
                                    player.soul_decay_timer = 0
                                    player.souls = max(0, player.souls - 1)
                    # Boss spawn logic: handled by boss_manager
                    warning_active, spawn_now = boss_manager.update(score, player.level, boss_exists=bool(boss))
                    if warning_active and not boss:
                        # Trigger visual/sound warning once
                        sound_mgr.stop_music(); sound_mgr.play("warning")
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
                            sound_mgr.play_music("boss")
                    
                    if len(mobs) < (12 if not boss else 4):
                        # ========== 全新敌人生成系统 v2.0 ==========
                        # 支持全部37种敌人，分6个阶段逐步解锁
                        
                        # 基础生成率：2.5% ~ 8%
                        base_spawn_rate = 0.025 + 0.055 * (1 - math.exp(-player.level / 15))
                        
                        # 波次系统：每隔一段时间有小概率触发编队生成
                        wave_chance = 0.08 if score > 3000 else 0.03
                        is_wave_spawn = random.random() < wave_chance
                        
                        if random.random() < base_spawn_rate or is_wave_spawn:
                            # 根据分数段获取当前游戏阶段（0-5）
                            stage = min(5, score // 1500)
                            
                            # ========== 全部37种敌人分阶段池 ==========
                            # 格式: (敌人ID, 权重)
                            stage_pools = [
                                # 阶段0 (0-1500分): 入门期 - 一级普通敌人
                                [
                                    ("scout_moth", 35),           # 侦察机·灰蛾
                                    ("trooper_spear", 30),        # 突击兵·赤矛
                                    ("lurker_halo", 20),          # 徘徊者·光环盘
                                    ("plasma_storm", 15),         # 等离子风暴
                                ],
                                # 阶段1 (1500-3000分): 成长期 - 更多一级敌人
                                [
                                    ("scout_moth", 20),
                                    ("trooper_spear", 22),
                                    ("lurker_halo", 15),
                                    ("bomber_deepjelly", 18),     # 轰炸艇·深水母
                                    ("jammer_amethyst", 12),      # 干扰者·紫菱
                                    ("shield_beeguard", 8),       # 盾卫机
                                    ("plasma_storm", 5),
                                ],
                                # 阶段2 (3000-4500分): 挑战期 - 二级敌人登场
                                [
                                    ("trooper_spear", 12),
                                    ("bomber_deepjelly", 15),
                                    ("jammer_amethyst", 10),
                                    ("shield_beeguard", 10),
                                    ("splitter_azurecore", 15),   # 裂解者·蔚蓝核心
                                    ("sniper_blackneedle", 12),   # 狙击手·黑针
                                    ("weaver_dualwasp", 10),      # 编织者·双生黄蜂
                                    ("helix_drone", 8),           # 螺旋无人机
                                    ("mirage_twin", 8),           # 幻影双子
                                ],
                                # 阶段3 (4500-6000分): 激烈期 - 更多二级+中级敌人
                                [
                                    ("bomber_deepjelly", 8),
                                    ("splitter_azurecore", 12),
                                    ("sniper_blackneedle", 12),
                                    ("weaver_dualwasp", 10),
                                    ("summoner_nethalo", 10),     # 召唤师·母巢光环
                                    ("prism_voidprism", 10),      # 折射棱镜
                                    ("guard_heavyanvil", 8),      # 脉冲守卫
                                    ("pulse_mine", 6),            # 脉冲地雷
                                    ("laser_turret", 8),          # 激光炮塔
                                    ("swarm_carrier", 6),         # 蜂群航母
                                    ("meteor_crusher", 5),        # 陨星粉碎者
                                    ("swarm_mother", 5),          # 蜂群母舰
                                ],
                                # 阶段4 (6000-7500分): 困难期 - 三级敌人+新增敌人
                                [
                                    ("sniper_blackneedle", 8),
                                    ("prism_voidprism", 10),
                                    ("guard_heavyanvil", 10),
                                    ("nestlord_livestarport", 8), # 巢穴领主
                                    ("weaver_dimensionspindle", 8),# 时空编织者
                                    ("judge_dualpolar", 8),       # 镜像仲裁者
                                    ("gravity_anchor", 7),        # 重力锚
                                    ("tesla_coil", 8),            # 特斯拉线圈
                                    ("pulse_bomber", 7),          # 脉冲轰炸者
                                    ("laser_sentinel", 8),        # 激光哨兵
                                    ("shadow_assassin", 6),       # 暗影刺客
                                    ("minelayer_drone", 6),       # 布雷无人机
                                    ("gatling_fortress", 6),      # 加特林堡垒
                                ],
                                # 阶段5 (7500分+): 地狱期 - 全部顶级敌人
                                [
                                    ("guard_heavyanvil", 6),
                                    ("nestlord_livestarport", 8),
                                    ("weaver_dimensionspindle", 8),
                                    ("judge_dualpolar", 8),
                                    ("annihilator_soleye", 8),    # 湮灭光束舰
                                    ("chaos_discordantprism", 8), # 混沌信标
                                    ("phantom_voidstrider", 8),   # 相位幽影
                                    ("void_leech", 7),            # 虚空水蛭
                                    ("omega_sentinel", 6),        # 欧米茄哨兵
                                    ("quantum_ghost", 7),         # 量子幽灵
                                    ("nova_core", 6),             # 新星核心
                                    ("laser_sentinel", 6),
                                    ("shadow_assassin", 7),
                                    ("gatling_fortress", 7),
                                ],
                            ]
                            
                            # 获取当前阶段敌人池
                            pool = stage_pools[stage]
                            
                            # 加权随机选择
                            enemies = [e[0] for e in pool]
                            weights = [e[1] for e in pool]
                            
                            # 波次生成：一次生成2-4个同类敌人
                            if is_wave_spawn and len(mobs) < 8:
                                spawn_count = random.randint(2, 4)
                                chosen_type = random.choices(enemies, weights=weights, k=1)[0]
                                for i in range(spawn_count):
                                    enemy_factory.create_enemy(chosen_type)
                            else:
                                # 普通单个生成
                                chosen_type = random.choices(enemies, weights=weights, k=1)[0]
                                enemy_factory.create_enemy(chosen_type)
                    
                    hits = pygame.sprite.groupcollide(mobs, bullets, False, False)
                    for m, hit_bullets in hits.items():
                        for b in hit_bullets:
                            if b.is_enemy: continue
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
                            
                            if random.random() < crit_chance: dmg *= crit_mult
                            m.hp -= dmg
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
                            ult_charge_gain = dmg / 10  # 伤害值的10%转化为大招能量
                            player.ult_charge = min(player.max_ult_charge, player.ult_charge + ult_charge_gain)
                            # 【新】同时充能第二大招（G键）
                            player.ult2_charge = min(player.max_ult2_charge, player.ult2_charge + ult_charge_gain * 0.8)
                            # 【新】同时充能第三大招（C键）
                            player.ult3_charge = min(player.max_ult3_charge, player.ult3_charge + ult_charge_gain * 0.6)
                            
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
                                        pygame.draw.line(screen, YELLOW, 
                                                       current_target.rect.center, 
                                                       nearest_enemy.rect.center, 2)
                                        
                                        # 造成连锁伤害
                                        nearest_enemy.hp -= chain_damage
                                        FloatingText(nearest_enemy.rect.centerx, nearest_enemy.rect.top - 10, 
                                                   f"-{int(chain_damage)}", YELLOW)
                                        
                                        # 闪电特效（优化：减少粒子）
                                        if random.random() < 0.5:
                                            Particle(nearest_enemy.rect.center, YELLOW)
                                        
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
                            
                            # 【霓虹突击者】固有能力：超载模式 - 连续命中提升伤害
                            if hasattr(player, 'plane_id') and player.plane_id == "striker":
                                # 初始化超载计数器
                                if not hasattr(player, 'overdrive_hits'):
                                    player.overdrive_hits = 0
                                    player.overdrive_timer = 0
                                    player.overdrive_bonus = 0
                                
                                # 命中增加超载层数（最多10层）
                                player.overdrive_hits = min(10, player.overdrive_hits + 1)
                                player.overdrive_timer = 90  # 1.5秒内不命中则重置
                                player.overdrive_bonus = player.overdrive_hits * 0.08  # 每层+8%伤害
                                
                                # 超载视觉效果 - 青色能量
                                if player.overdrive_hits >= 3:
                                    for _ in range(2):
                                        angle = random.uniform(0, math.pi * 2)
                                        dist = random.uniform(8, 20)
                                        px = m.rect.centerx + math.cos(angle) * dist
                                        py = m.rect.centery + math.sin(angle) * dist
                                        Particle((int(px), int(py)), CYAN)
                            
                            # 【虚空幻影】固有能力：相位闪避 - 攻击时有几率获得短暂无敌
                            if hasattr(player, 'plane_id') and player.plane_id == "phantom":
                                # 15%概率触发相位闪避
                                if random.random() < 0.15:
                                    # 获得30帧（0.5秒）无敌
                                    if not hasattr(player, 'phase_invuln'):
                                        player.phase_invuln = 0
                                    player.phase_invuln = 30
                                    # 相位特效 - 紫色闪烁
                                    for _ in range(5):
                                        angle = random.uniform(0, math.pi * 2)
                                        dist = random.uniform(10, 30)
                                        px = player.rect.centerx + math.cos(angle) * dist
                                        py = player.rect.centery + math.sin(angle) * dist
                                        Particle((int(px), int(py)), MAGENTA)
                            
                            # 【极光女神】固有能力：极光领域 - 命中敌人时减速周围敌人
                            if hasattr(player, 'plane_id') and player.plane_id == "aurora":
                                # 25%概率触发极光领域
                                if random.random() < 0.25:
                                    aurora_radius = 120  # 极光范围
                                    slow_duration = 90   # 减速持续1.5秒
                                    slow_amount = 0.4    # 减速40%
                                    
                                    # 对范围内所有敌人施加减速
                                    for enemy in mobs:
                                        dist = math.hypot(
                                            enemy.rect.centerx - m.rect.centerx,
                                            enemy.rect.centery - m.rect.centery
                                        )
                                        if dist <= aurora_radius:
                                            if not hasattr(enemy, 'aurora_slow'):
                                                enemy.aurora_slow = 0
                                                enemy.aurora_slow_mult = 1.0
                                            enemy.aurora_slow = slow_duration
                                            enemy.aurora_slow_mult = slow_amount
                                    
                                    # 极光领域视觉效果 - 青色光环扩散
                                    pygame.draw.circle(screen, TEAL, m.rect.center, int(aurora_radius), 2)
                                    for _ in range(6):
                                        angle = random.uniform(0, math.pi * 2)
                                        dist = random.uniform(20, aurora_radius * 0.8)
                                        px = m.rect.centerx + math.cos(angle) * dist
                                        py = m.rect.centery + math.sin(angle) * dist
                                        Particle((int(px), int(py)), TEAL)
                            
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
                            if m.hp <= 0:
                                score += 100 if m.is_elite else 20
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
                                    "vortex": 20
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
                                
                                # 触发击杀效果 (吸血、能量虹吸、裂变反应等)
                                corpse_effect = player.on_kill_enemy(m)
                                if corpse_effect:
                                    create_explosion(corpse_effect["pos"], ORANGE, 8)
                                
                                # 【幽灵收割者】固有能力：灵魂收割 - 击杀敌人收集灵魂
                                if hasattr(player, 'plane_id') and player.plane_id == "specter":
                                    if not hasattr(player, 'souls'):
                                        player.souls = 0
                                    # 精英敌人给2个灵魂，普通敌人给1个
                                    soul_gain = 2 if m.is_elite else 1
                                    player.souls = min(30, player.souls + soul_gain)  # 最多30灵魂
                                    # 灵魂特效 - 紫色幽灵粒子飞向玩家
                                    for _ in range(3):
                                        Particle(m.rect.center, (150, 100, 255))
                                
                                if random.random() < 0.25:
                                    arsenal_save_data["currencies"]["cores"] += 1
                                    FloatingText(m.rect.centerx, m.rect.top-20, "核心+1", CYAN)
                                m.kill()
                    
                    if not player.is_dashing:
                        hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
                        hits.extend(pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_circle))
                        if hits:
                            # 【虚空幻影】相位无敌检查
                            if hasattr(player, 'phase_invuln') and player.phase_invuln > 0:
                                # 无敌状态，免疫伤害
                                FloatingText(player.rect.centerx, player.rect.top, "相位!", MAGENTA)
                                # 相位特效
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
                            
                            dmg = 20
                            # ===== 增强受伤打击感 =====
                            # 屏幕震动反馈 - 减弱
                            screen_shake_offset = apply_screen_shake(3)
                            
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
                            
                            if player.shield > 0:
                                player.shield -= dmg
                                if player.shield < 0: player.shield = 0
                                # 盾牌吸收时的蓝色特效（简化）
                                if random.random() < 0.3:  # 30%概率显示
                                    for _ in range(2):
                                        angle = random.uniform(0, math.pi * 2)
                                        speed = random.uniform(2, 3)
                                        Particle(player.rect.center, CYAN)
                            else:
                                player.hp -= dmg
                                FloatingText(player.rect.centerx, player.rect.top, f"-{dmg}", RED)
                                # 受伤时的特效（简化）
                                if random.random() < 0.5:  # 50%概率显示
                                    for _ in range(2):
                                        angle = random.uniform(0, math.pi * 2)
                                        speed = random.uniform(2, 4)
                                        Particle(player.rect.center, RED)
                                sound_mgr.play("hit")
                                if player.hp <= 0:
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
                                # 恢复背景BGM
                                try:
                                    current_bg_style = bg_manager.current_style
                                    bg_config = BackgroundManager.BG_STYLES.get(current_bg_style, {})
                                    bgm_track = bg_config.get("bgm", "normal")
                                    sound_mgr.play_music(bgm_track)
                                except: pass
                                
                                FloatingText(WIDTH//2, HEIGHT//2, "BOSS DEFEATED", GOLD)
                                
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
                                        # 继续无限模式或返回菜单
                
                # ========== 先绘制尾迹（在飞机下层）==========
                if player is not None:
                    safe_call_draw(player.draw_trail, screen)
                
                safe_call_draw(all_sprites.draw, screen)
                
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
                    # Boss挑战模式进度显示
                    if boss_challenge_active and (game_state == "game" or game_state == "boss_challenge_play"):
                        challenge_font = pygame.font.SysFont("SimHei", 28)
                        progress_text = challenge_font.render(f"挑战进度: {boss_challenge_current}/{len(boss_challenge_order)}", True, CYAN)
                        screen.blit(progress_text, (20, HEIGHT - 80))
                    safe_call_draw(draw_warning_indicator)  # BOSS警告闪烁边框
                
                # 成就通知始终显示
                safe_call_draw(draw_achievement_notifications)
                
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