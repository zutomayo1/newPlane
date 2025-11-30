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
from customization import customization_manager, PAINT_THEMES, EnhancedTrailEffect

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

# 加载设置并初始化背景管理器
game_settings = load_settings()
bg_manager = BackgroundManager(style=game_settings.get("background_style", "classic"))
# sound_mgr 来自 utils.py

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
codex_tab = 0 # 0:Plane, 1:Boss
codex_idx = 0
codex_scroll_y = 0 

# 涂装系统 - 重写版本
customization_scroll_y = 0
customization_plane_scroll_y = 0  # 飞机列表滚动
customization_selected_plane = None  # 当前选中的飞机ID
customization_msg = ""

# 背景设置
background_settings_scroll_y = 0
background_settings_selected = 0  # 当前选中的背景索引
customization_msg_timer = 0

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

def create_explosion(pos, color, count=10):
    """生成爆炸粒子效果"""
    for _ in range(count):
        Particle(pos, color, mode="spark")

def create_shockwave(pos, color, count=10):
    """生成冲击波效果"""
    for _ in range(count):
        Particle(pos, color, mode="shockwave")

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
        sound_mgr.play_music("normal")
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
        ("机体涂装", MAGENTA, "customization"),
        ("背景设置", (100, 200, 255), "background_settings"),
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
    """背景设置界面"""
    draw_text(screen, "背景设置", 40, WIDTH//2, 30, (100, 200, 255), glow=True)
    
    mx, my = pygame.mouse.get_pos()
    
    # 获取所有可用背景
    from systems import BackgroundManager
    bg_styles = BackgroundManager.BG_STYLES
    
    # 绘制背景选项卡
    card_w = 280
    card_h = 200
    cards_per_row = 4
    gap = 30
    start_x = (WIDTH - (cards_per_row * card_w + (cards_per_row - 1) * gap)) // 2
    start_y = 120
    
    # 创建可滚动区域
    scroll_area = pygame.Rect(0, start_y, WIDTH, HEIGHT - start_y - 100)
    screen.set_clip(scroll_area)
    
    i = 0
    for style_key, style_data in bg_styles.items():
        row = i // cards_per_row
        col = i % cards_per_row
        
        x = start_x + col * (card_w + gap)
        y = start_y + row * (card_h + gap) - background_settings_scroll_y
        
        card_rect = pygame.Rect(x, y, card_w, card_h)
        
        # 如果卡片不在可见区域内,跳过绘制
        if y + card_h < scroll_area.top or y > scroll_area.bottom:
            i += 1
            continue
        
        # 检查是否是当前选中的背景
        is_selected = (bg_manager.current_style == style_key)
        is_hover = card_rect.collidepoint(mx, my) and not is_selected
        is_keyboard_selected = (i == background_settings_selected)  # 键盘选中
        
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
        
        i += 1
    
    # 取消裁剪
    screen.set_clip(None)
    
    # 绘制滚动条
    total_rows = (len(bg_styles) + cards_per_row - 1) // cards_per_row
    content_height = total_rows * (card_h + gap)
    visible_height = scroll_area.height
    
    if content_height > visible_height:
        scrollbar_height = max(30, int(visible_height * visible_height / content_height))
        scrollbar_y = int(scroll_area.top + (background_settings_scroll_y / content_height) * visible_height)
        scrollbar_rect = pygame.Rect(WIDTH - 15, scrollbar_y, 10, scrollbar_height)
        pygame.draw.rect(screen, (100, 100, 100), scrollbar_rect, border_radius=5)
        
        # 滚动提示
        if background_settings_scroll_y > 0:
            draw_text(screen, "▲", 20, WIDTH - 10, scroll_area.top + 10, GRAY)
        if background_settings_scroll_y < content_height - visible_height:
            draw_text(screen, "▼", 20, WIDTH - 10, scroll_area.bottom - 20, GRAY)
    
    # 操作提示
    draw_text(screen, "点击卡片切换背景 | 方向键导航 | Enter确认", 16, WIDTH//2, HEIGHT - 110, (150, 150, 150))
    
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
    
    # Tabs
    c1 = CYAN if codex_tab == 0 else GRAY
    draw_cyber_rect(screen, r['tab_plane'], (30,30,40), fill=True)
    if codex_tab == 0: draw_cyber_rect(screen, r['tab_plane'], c1, border_width=2, fill=False)
    draw_text(screen, "机体数据", 18, r['tab_plane'].centerx, r['tab_plane'].centery-10, c1)
    
    c2 = RED if codex_tab == 1 else GRAY
    draw_cyber_rect(screen, r['tab_boss'], (30,30,40), fill=True)
    if codex_tab == 1: draw_cyber_rect(screen, r['tab_boss'], c2, border_width=2, fill=False)
    draw_text(screen, "领主图鉴", 18, r['tab_boss'].centerx, r['tab_boss'].centery-10, c2)
    
    # List View (Scrolled)
    if codex_tab == 0:
        keys = plane_keys
        db = PLANES
        color_theme = CYAN
    else:
        keys = list(BOSS_DB.keys())
        db = BOSS_DB
        color_theme = RED

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
        
        if codex_tab == 0: preview = get_plane_surf(key, PLANES.get(key, {}).get('visual', None))
        else: preview = get_boss_surf(key, data["color"])
        preview = pygame.transform.scale(preview, (150, 150))
        safe_blit(screen, preview, (cx - 75, cy))
        
        draw_text(screen, data["name"], 30, cx, cy + 170, data["color"], glow=True)
        draw_text(screen, data["desc"], 18, cx, cy + 210, WHITE)
        
        stats = []
        if codex_tab == 0:
            stats = [("生命", data["hp"], 200), ("速度", data["speed"]*10, 100), ("火力", data["damage"]*2, 200)]
        else:
            stats = [(k, v, 100) for k,v in data["stats"]]
            
        for j, (lbl, val, mxv) in enumerate(stats):
            y_off = cy + 260 + j*40
            draw_text(screen, lbl, 18, r['detail_area'].x + 150, y_off, WHITE, align="left")
            pygame.draw.rect(screen, (40,40,40), (r['detail_area'].x + 230, y_off+5, 200, 10))
            fill = min(200, (val/mxv)*200)
            pygame.draw.rect(screen, data["color"], (r['detail_area'].x + 230, y_off+5, fill, 10))

    hb = r['btn_back'].collidepoint(mx, my)
    draw_cyber_rect(screen, r['btn_back'], GRAY, fill=True)
    if hb: draw_cyber_rect(screen, r['btn_back'], WHITE, border_width=2, fill=False)
    draw_text(screen, "返回", 20, r['btn_back'].centerx, r['btn_back'].centery-10, WHITE)

def draw_gallery_ui():
    draw_text(screen, "战术图鉴", 40, WIDTH//2, 30, MAGENTA, glow=True)
    
    tab_labels = ["全部", "普通", "稀有", "史诗", "传说"]
    tab_colors = [WHITE, RARITY_COMMON, RARITY_RARE, RARITY_EPIC, RARITY_LEGEND]
    tab_w = 100
    start_tx = (WIDTH - (5 * tab_w + 40)) // 2
    mx, my = pygame.mouse.get_pos()
    
    for i, lbl in enumerate(tab_labels):
        rect = pygame.Rect(start_tx + i*(tab_w+10), 80, tab_w, 40)
        is_sel = (i == gallery_tab)
        c = tab_colors[i]
        draw_cyber_rect(screen, rect, (30,30,40), fill=True)
        if is_sel: draw_cyber_rect(screen, rect, c, border_width=2, fill=False)
        draw_text(screen, lbl, 18, rect.centerx, rect.centery-10, c if is_sel else GRAY)

    if gallery_tab == 0: items = UPGRADE_ITEMS
    else: items = [it for it in UPGRADE_ITEMS if it['rarity'] == gallery_tab - 1]
    
    start_y = 150
    cols = 4
    card_w = 240
    card_h = 140
    gap = 20
    start_gx = (WIDTH - (cols*card_w + (cols-1)*gap)) // 2
    
    items_per_page = 8
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
        draw_cyber_rect(screen, rect, (30,30,40), fill=True)
        draw_cyber_rect(screen, rect, rc, border_width=1, fill=False)
        pygame.draw.rect(screen, (*rc, 80), (x, y, card_w, 30))
        draw_text(screen, item['name'], 18, rect.centerx, y+5, WHITE)
        desc = item['desc']
        lines = [desc[k:k+14] for k in range(0, len(desc), 14)]
        for k, line in enumerate(lines):
            draw_text(screen, line, 16, rect.centerx, y+50+k*20, GRAY)

    back_btn = pygame.Rect(WIDTH//2 - 50, HEIGHT - 60, 100, 40)
    h = back_btn.collidepoint(mx, my)
    draw_cyber_rect(screen, back_btn, GRAY, fill=True)
    if h: draw_cyber_rect(screen, back_btn, WHITE, border_width=2, fill=False)
    draw_text(screen, "返回", 20, back_btn.centerx, back_btn.centery-10, WHITE)
    
    max_p = max(1, (len(items) + items_per_page - 1) // items_per_page)
    if max_p > 1:
        if gallery_page > 0:
            prev_btn = pygame.Rect(50, HEIGHT//2, 50, 50)
            draw_cyber_rect(screen, prev_btn, WHITE if prev_btn.collidepoint(mx,my) else GRAY, border_width=2, fill=False)
            draw_text(screen, "<", 30, prev_btn.centerx, prev_btn.centery-15, WHITE)
        if gallery_page < max_p - 1:
            next_btn = pygame.Rect(WIDTH-100, HEIGHT//2, 50, 50)
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

def draw_customization_ui():
    """绘制涂装自定义界面 - 重写版本"""
    global customization_selected_plane, customization_msg_timer, customization_tab, customization_scroll_y, customization_plane_scroll_y
    
    draw_text(screen, "机体涂装系统", 40, WIDTH//2, 30, MAGENTA, glow=True)
    currency_text = f"核心: {arsenal_save_data['currencies']['cores']}"
    draw_text(screen, currency_text, 20, WIDTH - 200, 30, GOLD, align="left")
    unlocked_count = customization_manager.get_unlocked_count()
    total_count = customization_manager.get_total_count()
    progress_text = f"已解锁: {unlocked_count}/{total_count}"
    draw_text(screen, progress_text, 18, WIDTH - 200, 60, CYAN, align="left")
    
    mx, my = pygame.mouse.get_pos()
    
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
        tabs = ["全部", "普通", "稀有", "史诗", "传说", "专属"]
        categories = [None, "common", "rare", "epic", "legendary", "exclusive"]
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
        for tid, theme in PAINT_THEMES.items():
            # 过滤掉其他飞机的专属涂装
            exclusive_plane = theme.get("exclusive_plane")
            if exclusive_plane and exclusive_plane != customization_selected_plane:
                continue

            if customization_tab == 0:
                filtered_themes.append((tid, theme))
            else:
                target_cat = categories[customization_tab]
                if theme.get("category") == target_cat:
                    filtered_themes.append((tid, theme))
        
        theme_y_start = 180
        
        # 列表裁剪区域
        list_view_rect = pygame.Rect(theme_list_area.x, theme_y_start, theme_list_area.width, theme_list_area.height - (theme_y_start - theme_list_area.y))
        screen.set_clip(list_view_rect)
        
        for i, (theme_id, theme) in enumerate(filtered_themes):
            card_rect = pygame.Rect(350, theme_y_start + i * 100 - customization_scroll_y, 560, 90)
            
            # 跳过不可见的卡片
            if card_rect.bottom < list_view_rect.top or card_rect.top > list_view_rect.bottom:
                continue
            
            is_unlocked = customization_manager.unlocked_themes.get(theme_id, False)
            is_equipped = customization_manager.get_equipped_theme(customization_selected_plane) == theme_id
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
        draw_text(screen, "涂装预览", 18, preview_area.centerx, preview_area.y + 10, MAGENTA)
        
        # 获取当前装备的涂装预览
        equipped_theme = customization_manager.get_equipped_theme(customization_selected_plane)
        visual = customization_manager.get_theme_visual(customization_selected_plane, PLANES[customization_selected_plane].get('visual', None))
        big_preview = get_plane_surf(customization_selected_plane, visual)
        big_preview = pygame.transform.scale(big_preview, (120, 120))
        safe_blit(screen, big_preview, (preview_area.centerx - 60, preview_area.y + 40))
    
    # 返回按钮 (移动到左上角，避免遮挡列表)
    back_btn = pygame.Rect(30, 30, 100, 40)
    h = back_btn.collidepoint(mx, my)
    draw_cyber_rect(screen, back_btn, GRAY, fill=True)
    if h: draw_cyber_rect(screen, back_btn, WHITE, border_width=2, fill=False)
    draw_text(screen, "返回", 20, back_btn.centerx, back_btn.centery - 10, WHITE)

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
    
    # 护盾条 (青色/CYAN) - 百分比基于max_hp计算
    # 护盾条 (青色/CYAN) - 百分比基于护盾上限计算
    shield_pct = (player.shield / max(1, player.max_shield) * 100) if player.max_shield > 0 else 0
    draw_slanted_bar(screen, bar_x, bar_y, bar_w, bar_h_base, shield_pct, CYBER_CYAN_BRIGHT, 
                     bg_color=(0, 40, 50), tilt=tilt, border_color=CYAN, border_width=1)
    draw_text(screen, "护盾", 16, label_x, bar_y - 1, CYBER_CYAN_BRIGHT, glow=True, align='left')
    draw_text(screen, f"{int(player.shield)}/{int(player.max_shield)}", 14, label_x + 45, bar_y + 1, WHITE, align='left')
    
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
    
    # 大招名字（清晰显示）- 增加间距
    ult_name = player.plane_data.get('ult_name', 'ULT')
    draw_text(screen, ult_name, 16, bottom_right_x, slot_y + 68, MAGENTA, align='right', glow=True)
    
    # 储能条（3格，放大，放在大招名字下方，作为视觉辅助）- 增加间距
    storage_y = slot_y + 92
    storage_max = 3
    storage_current = int(player.ult_charge / player.max_ult_charge * storage_max) if player.max_ult_charge > 0 else 0
    
    # 计算当前储存槽内的填充比例（用于部分填充最后一个槽）
    ult_ratio = player.ult_charge / player.max_ult_charge if player.max_ult_charge > 0 else 0
    partial_fill = (ult_ratio * storage_max) % 1.0  # 小数部分
    
    for j in range(storage_max):
        s_x = bottom_right_x - (storage_max - j) * 32 + 4
        s_rect = pygame.Rect(s_x, storage_y, 28, 22)
        
        if j < storage_current:
            # 完全填充的槽
            draw_cyber_rect(screen, s_rect, MAGENTA, alpha=200, border_width=2, fill=True)
            # 闪烁效果
            pulse = abs(math.sin(pygame.time.get_ticks() / 500))
            if pulse > 0.5:
                pygame.draw.rect(screen, CYBER_CYAN_BRIGHT, (s_x + 2, storage_y + 2, 24, 18), 1)
        elif j == storage_current:
            # 部分填充的槽 - 显示充能进度
            draw_cyber_rect(screen, s_rect, (60, 30, 60), alpha=200, border_width=2, fill=True)
            if partial_fill > 0.1:  # 只在有明显填充时显示
                fill_w = int(24 * partial_fill)
                pygame.draw.rect(screen, MAGENTA, (s_x + 2, storage_y + 2, fill_w, 18))
                # 进度闪烁
                pulse = abs(math.sin(pygame.time.get_ticks() / 300))
                if pulse > 0.4:
                    pygame.draw.rect(screen, CYBER_CYAN_BRIGHT, (s_x + 2, storage_y + 2, fill_w, 18), 1)
        else:
            # 空槽
            draw_cyber_rect(screen, s_rect, (40, 20, 40), alpha=150, border_width=1, fill=True)
    
    # 冷却时显示CD标签 - 增加间距
    if player.ult_cooldown > 0:
        cd_sec = player.ult_cooldown / 60.0
        draw_text(screen, f"CD {cd_sec:.1f}s", 11, bottom_right_x - 5, storage_y + 36, CYBER_RED_ALERT, align='right')
    
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
    
    # ===== 底部中央：BOSS血条 (如果有BOSS) =====
    if boss:
        boss_y = HEIGHT - 45
        boss_bar_w = 500
        boss_x = (WIDTH - boss_bar_w) // 2
        boss_bar_h = 12
        
        # BOSS名称 (炫光效果)
        draw_text(screen, f"BOSS: {boss.name}", 14, boss_x, boss_y - 20, CYBER_RED_ALERT, glow=True)
        
        # BOSS血条背景
        pygame.draw.rect(screen, (60, 15, 15), (boss_x, boss_y, boss_bar_w, boss_bar_h))
        pygame.draw.rect(screen, CYBER_RED_ALERT, (boss_x, boss_y, boss_bar_w, boss_bar_h), 2)
        
        # BOSS血条填充 (炫光渐变)
        boss_hp_pct = (boss.hp / boss.max_hp) * 100
        boss_fill = (boss_hp_pct / 100) * boss_bar_w
        if boss_fill > 0:
            pygame.draw.rect(screen, (255, 80, 80), (boss_x, boss_y, boss_fill, boss_bar_h))
            # 边缘炫光
            if boss_fill > 3:
                pygame.draw.line(screen, (255, 150, 150), (boss_x + boss_fill - 2, boss_y),
                               (boss_x + boss_fill - 2, boss_y + boss_bar_h), 2)
        
        # BOSS血量数值
        draw_text(screen, f"{int(boss.hp)}/{int(boss.max_hp)}", 11, boss_x + boss_bar_w//2 - 20, boss_y + 1, WHITE)
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
    
    draw_emoji_text(screen, "❤ 生命值", 16, left_x + 5, y_offset - 2, (255, 100, 100), align="left", glow=True)
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
    
    draw_emoji_text(screen, "🛡 护盾值", 16, left_x + 5, y_offset - 2, CYBER_AMBER, align="left", glow=True)
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
        
        # 名称
        draw_text(screen, name, 16, card_x + 10, card_y + 4, (200, 200, 200), align="left")
        
        # 数值
        draw_text(screen, value, 20, card_x + 10, card_y + 22, color, glow=True, align="left")

    # 【右侧】增益卡片 - 玻璃态射质感
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
    
    draw_text(screen, "战术增益列表", 22, right_x, right_y, MAGENTA, glow=True, align="left")
    
    buffs = getattr(player, 'buffs', []) or getattr(player, 'active_buffs', []) or []
    buff_start_y = right_y + 50
    
    if not buffs:
        # 无增益提示 - 更有设计感
        no_buff_y = buff_start_y + 150
        draw_text(screen, "╳", 48, right_x + 240, no_buff_y - 20, (80, 80, 80), align="center")
        draw_text(screen, "暂无战术增益", 18, right_x + 240, no_buff_y + 30, GRAY, align="center")
        draw_text(screen, "击败敌人升级获取", 14, right_x + 240, no_buff_y + 55, (100, 100, 100), align="center")
    else:
        # 增益列表 - 卡片式显示
        effect_data = []
        
        # 根据卡牌ID生成实际效果文本
        for buff_id in buffs[:8]:
            if buff_id == "homing":
                effect_data.append(("🎯 追踪等级", f"★{player.homing_level}", CYBER_LIME, "智能锁定系统"))
            elif buff_id == "pierce":
                effect_data.append(("⚡ 穿透次数", f"+{player.piercing}", CYBER_AMBER, "贯穿装甲弹药"))
            elif buff_id == "multi":
                effect_data.append(("✦ 子弹数量", f"×{player.bullet_count}", MAGENTA, "多管齐射模式"))
            elif buff_id == "dmg":
                dmg_boost = (player.damage / PLANES.get(player.plane_id, {}).get('damage', 1)) - 1
                effect_data.append(("⚔ 伤害提升", f"+{dmg_boost*100:.0f}%", RED, "火力强化协议"))
            elif buff_id == "crit":
                effect_data.append(("💥 暴击率", f"{player.crit_chance*100:.1f}%", CYBER_RED_ALERT, "致命打击系统"))
            elif buff_id == "spd":
                effect_data.append(("⏱ 射速提升", "✓", CYAN, "急速冷却装置"))
            elif buff_id == "hp_max":
                effect_data.append(("❤ 生命上限", f"+{int(player.max_hp - PLANES.get(player.plane_id, {}).get('hp', 100))}", CYBER_LIME, "结构强化改造"))
            elif buff_id == "bounce":
                effect_data.append(("↗ 弹跳次数", f"+{player.bounce_level}", MAGENTA, "反弹弹道系统"))
            elif buff_id == "drone":
                wingman_count = len(player.wingman_squadron.wingmen) if hasattr(player, 'wingman_squadron') and player.wingman_squadron else 0
                effect_data.append(("🛸 僚机数量", f"×{wingman_count}", CYAN, "无人机编队"))
            else:
                effect_data.append(("✓ 已获得", buff_id, GRAY, "未知增益"))
        
        # 显示增益卡片 - 2列布局
        for i, (effect_name, effect_value, color, desc) in enumerate(effect_data):
            col = i % 2
            row = i // 2
            
            buff_x = right_x + col * 250
            buff_y = buff_start_y + row * 52
            
            # 超出面板就停止
            if buff_y > right_y + 360:
                remaining = len(buffs) - i
                if remaining > 0:
                    more_rect = pygame.Rect(right_x + 160, buff_y - 5, 140, 30)
                    pygame.draw.rect(screen, (40, 40, 50, 200), more_rect, border_radius=8)
                    pygame.draw.rect(screen, GRAY, more_rect, 1, border_radius=8)
                    draw_text(screen, f"▼ 还有 {remaining} 项增益", 13, right_x + 230, buff_y + 5, GRAY, align="center")
                break
            
            # 卡片背景 - 玻璃质感
            bar_rect = pygame.Rect(buff_x - 8, buff_y - 18, 230, 44)
            card_surf = pygame.Surface((bar_rect.width, bar_rect.height), pygame.SRCALPHA)
            
            # 渐变背景
            for dy in range(bar_rect.height):
                grad_alpha = int(120 + 80 * (1 - dy / bar_rect.height))
                base_color = color[:3] if len(color) == 3 else color[:3]
                pygame.draw.line(card_surf, (base_color[0], base_color[1], base_color[2], grad_alpha // 3), 
                               (0, dy), (bar_rect.width, dy))
            safe_blit(screen, card_surf, (bar_rect.x, bar_rect.y))
            
            # 边框 - 发光
            glow_intensity = int(200 + 55 * math.sin(t / 500 + i * 0.5))
            glow_color = tuple(min(255, c) for c in color[:3]) if len(color) == 3 else color[:3]
            pygame.draw.rect(screen, (*glow_color, glow_intensity), bar_rect, 2, border_radius=8)
            
            # 高光
            pygame.draw.line(screen, (255, 255, 255, 80), 
                           (bar_rect.x + 10, bar_rect.y + 3), 
                           (bar_rect.x + bar_rect.width - 10, bar_rect.y + 3), 1)
            
            # 图标光晕
            icon_x = buff_x - 2
            icon_y = buff_y - 8
            pygame.draw.circle(screen, (*color[:3], 50), (icon_x, icon_y), 18)
            
            # 效果名称
            draw_text(screen, effect_name, 14, buff_x, buff_y - 10, WHITE, align="left", glow=True)
            
            # 描述文字
            draw_text(screen, desc, 10, buff_x, buff_y + 8, (180, 180, 180), align="left")
            
            # 数值 - 发光强调
            draw_text(screen, effect_value, 16, buff_x + 160, buff_y - 2, color, glow=True, align="right")

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
    """绘制升级选择 UI"""
    if not upgrade_options or len(upgrade_options) < 3:
        return
    if player is None:
        log_debug("draw_levelup_ui: player is None, skip")
        return
    
    # 半透明遮罩
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    safe_blit(screen, overlay, (0, 0))
    
    # 标题
    draw_text(screen, "选择升级增益", 48, WIDTH//2, 100, CYBER_AMBER, glow=True)
    
    # 3 个升级卡牌
    card_width = 280
    card_height = 400
    gap = 40
    total_width = 3 * card_width + 2 * gap
    start_x = (WIDTH - total_width) // 2
    start_y = 200
    
    try:
        from roguelite import BUFF_LIBRARY
        
        for i, buff_id in enumerate(upgrade_options):
            buff = BUFF_LIBRARY.get(buff_id)
            if not buff:
                continue
            
            card_x = start_x + i * (card_width + gap)
            card_rect = pygame.Rect(card_x, start_y, card_width, card_height)
            
            # 卡牌背景
            bg_color = (30, 30, 50)
            border_color = RARITY_COLORS[buff["rarity"]]
            draw_cyber_rect(screen, card_rect, bg_color, fill=True)
            border_width = 4 if i == upgrade_selected else 2
            draw_cyber_rect(screen, card_rect, border_color, border_width=border_width, fill=False)
            
            # 选中效果 - 高亮边框 + 闪光
            if i == upgrade_selected:
                glow_rect = pygame.Rect(card_x - 5, start_y - 5, card_width + 10, card_height + 10)
                draw_cyber_rect(screen, glow_rect, border_color, border_width=1, fill=False)
            
            # 稀有度标签
            rarity_text = RARITY_NAMES[buff["rarity"] + 1]
            draw_text(screen, rarity_text, 16, card_rect.centerx, card_rect.top + 20, border_color, glow=True)
            
            # 增益名称
            draw_text(screen, buff["name"], 24, card_rect.centerx, card_rect.top + 60, WHITE, glow=True)
            
            # 描述
            desc_lines = [buff["desc"][k:k+18] for k in range(0, len(buff["desc"]), 18)]
            desc_y = card_rect.top + 120
            for line in desc_lines:
                draw_text(screen, line, 16, card_rect.centerx, desc_y, GRAY)
                desc_y += 30
            
            # 选择提示
            if i == upgrade_selected:
                draw_text(screen, "◄ 已选择 ►", 18, card_rect.centerx, card_rect.bottom - 30, LIME, glow=True)
    
    except ImportError:
        draw_text(screen, "ERROR: 无法加载增益库", 24, WIDTH//2, HEIGHT//2, RED)
    
    # 底部提示
    draw_text(screen, "上下键切换    ENTER确认", 16, WIDTH//2, HEIGHT - 60, CYAN)



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
            initial_delay = 6
            repeat_rate = 3
            
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
                    total_items = len(plane_keys) if codex_tab == 0 else len(BOSS_DB)
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
                    # 背景设置滚动
                    from systems import BackgroundManager
                    bg_count = len(BackgroundManager.BG_STYLES)
                    cards_per_row = 4
                    card_h = 200
                    gap = 30
                    total_rows = (bg_count + cards_per_row - 1) // cards_per_row
                    content_h = total_rows * (card_h + gap)
                    view_h = HEIGHT - 120 - 100
                    max_scroll = max(0, content_h - view_h)
                    background_settings_scroll_y = max(0, min(background_settings_scroll_y - event.y * 30, max_scroll))

            # --- 键盘事件 ---
            if event.type == pygame.KEYDOWN:
                # 菜单子页：ESC 返回主菜单
                if event.key == pygame.K_ESCAPE and game_state in ["arsenal", "gallery", "codex", "leaderboard", "select_plane", "background_settings"]:
                    game_state = "menu"
                    main_menu_selected = 0
                    sound_mgr.play("select")
                    continue
                
                # 背景设置界面 键盘控制
                if game_state == "background_settings":
                    from systems import BackgroundManager
                    bg_count = len(BackgroundManager.BG_STYLES)
                    cards_per_row = 4
                    card_h = 200
                    gap = 30
                    
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
                    
                    # 自动滚动到选中项(对于方向键)
                    if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                        selected_row = background_settings_selected // cards_per_row
                        card_y_top = selected_row * (card_h + gap)
                        view_h = HEIGHT - 120 - 100
                        
                        # 如果选中项在视图上方
                        if card_y_top < background_settings_scroll_y:
                            background_settings_scroll_y = card_y_top
                        # 如果选中项在视图下方
                        elif card_y_top + card_h > background_settings_scroll_y + view_h:
                            background_settings_scroll_y = card_y_top + card_h - view_h
                    
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
                        # 玩家选择一个增益
                        if 0 <= upgrade_selected < len(upgrade_options):
                            buff_id = upgrade_options[upgrade_selected]
                            player.apply_buff(buff_id)
                            sound_mgr.play("levelup")
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
                                game_state = "menu"; sound_mgr.play_music("normal")
                        elif event.key == pygame.K_p:
                            is_paused = False; sound_mgr.play("select")
                        elif event.key == pygame.K_r:
                            reset_game(); is_paused = False; sound_mgr.play("select")
                    else:
                        if event.key == pygame.K_p:
                            is_paused = True; pause_menu_selected = 0; sound_mgr.play("select")
                        elif event.key == pygame.K_f:
                            player.use_ultimate()
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
                            elif act in ["arsenal", "gallery", "codex", "leaderboard", "achievements", "customization", "background_settings"]:
                                game_state = act
                                if act == "gallery": gallery_page = 0; gallery_tab = 0
                                if act == "codex": codex_tab = 0; codex_idx = 0; codex_scroll_y = 0
                                if act == "arsenal": arsenal_scroll_y = 0; arsenal_selected_weapon_idx = -1
                                if act == "achievements": achievement_page = 0
                                if act == "customization": customization_scroll_y = 0; customization_plane_scroll_y = 0; customization_selected_plane = None; customization_tab = 0
                                if act == "background_settings": background_settings_selected = 0
                
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
                            elif act in ["arsenal", "gallery", "codex", "leaderboard", "achievements", "customization", "background_settings"]: 
                                game_state = act
                                if act == "gallery": gallery_page = 0; gallery_tab = 0
                                if act == "codex": codex_tab = 0; codex_idx = 0; codex_scroll_y = 0
                                if act == "arsenal": arsenal_scroll_y = 0; arsenal_selected_weapon_idx = -1
                                if act == "achievements": achievement_page = 0
                                if act == "customization": customization_scroll_y = 0; customization_plane_scroll_y = 0; customization_selected_plane = None; customization_tab = 0
                                if act == "background_settings": background_settings_selected = 0
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
                    
                    # 计算卡片布局
                    card_w = 280
                    card_h = 200
                    cards_per_row = 4
                    gap = 30
                    start_x = (WIDTH - (cards_per_row * card_w + (cards_per_row - 1) * gap)) // 2
                    start_y = 120
                    
                    i = 0
                    for style_key in bg_styles.keys():
                        row = i // cards_per_row
                        col = i % cards_per_row
                        
                        x = start_x + col * (card_w + gap)
                        y = start_y + row * (card_h + gap) - background_settings_scroll_y
                        
                        card_rect = pygame.Rect(x, y, card_w, card_h)
                        
                        # 检查卡片是否在可见区域内且被点击
                        scroll_area_top = start_y
                        scroll_area_bottom = HEIGHT - 100
                        if y + card_h >= scroll_area_top and y <= scroll_area_bottom:
                            if card_rect.collidepoint(mx, my):
                                # 更新选中索引并切换背景
                                background_settings_selected = i
                                bg_manager.set_style(style_key)
                                save_settings(background_style=style_key)
                                sound_mgr.play("select")
                                log_info(f"背景已切换为: {style_key}")
                                break
                        
                        i += 1
                    
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
                    tb_w = 100; stx = (WIDTH-(5*tb_w+40))//2
                    for i in range(5):
                        if pygame.Rect(stx+i*(tb_w+10), 80, tb_w, 40).collidepoint(mx, my): gallery_tab=i; gallery_page=0
                    if pygame.Rect(50, HEIGHT//2, 50, 50).collidepoint(mx, my) and gallery_page > 0: gallery_page -= 1
                    if pygame.Rect(WIDTH-100, HEIGHT//2, 50, 50).collidepoint(mx, my): gallery_page += 1
                    if pygame.Rect(WIDTH//2-50, HEIGHT-60, 100, 40).collidepoint(mx, my):
                        if player and hasattr(player, 'achievement_manager'):
                            player.achievement_manager.save_to_file()
                        game_state = "menu"

                elif game_state == "codex":
                    sound_mgr.play("select")
                    r = CODEX_UI
                    if r['tab_plane'].collidepoint(mx, my): codex_tab=0; codex_idx=0; codex_scroll_y=0
                    if r['tab_boss'].collidepoint(mx, my): codex_tab=1; codex_idx=0; codex_scroll_y=0
                    if r['list_view'].collidepoint(mx, my):
                        offset_y = my - r['list_view'].y + codex_scroll_y
                        clicked_idx = int(offset_y // 45)
                        keys = plane_keys if codex_tab == 0 else list(BOSS_DB.keys())
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
                
                elif game_state == "customization":
                    # 返回按钮 (移动到左上角)
                    back_btn = pygame.Rect(30, 30, 100, 40)
                    if back_btn.collidepoint(mx, my):
                        sound_mgr.play("select")
                        customization_manager.save_data()
                        game_state = "menu"
                    
                    # 选择飞机
                    elif not customization_selected_plane or True:  # 总是允许选择飞机
                        # 考虑滚动偏移（与绘制逻辑保持一致）
                        plane_list_area = pygame.Rect(30, 100, 280, HEIGHT - 180)
                        list_content_rect = pygame.Rect(plane_list_area.x, plane_list_area.y + 40, plane_list_area.width, plane_list_area.height - 40)
                        plane_start_y = list_content_rect.y + 5 - customization_plane_scroll_y
                        plane_found = False
                        
                        # 仅在列表区域内检测点击（使用计算出的边界）
                        if list_content_rect.collidepoint(mx, my):
                            for i, plane_id in enumerate(plane_keys):
                                rect = pygame.Rect(40, plane_start_y + i * 45, 260, 40)
                                if rect.collidepoint(mx, my):
                                    sound_mgr.play("select")
                                    customization_selected_plane = plane_id
                                    plane_found = True
                                    break
                        
                        # 如果没有点击飞机，检查涂装按钮
                        if not plane_found and customization_selected_plane:
                            # --- 筛选涂装 (必须与绘制逻辑一致) ---
                            categories = [None, "common", "rare", "epic", "legendary", "exclusive"]
                            filtered_themes = []
                            for tid, theme in PAINT_THEMES.items():
                                # 过滤掉其他飞机的专属涂装
                                exclusive_plane = theme.get("exclusive_plane")
                                if exclusive_plane and exclusive_plane != customization_selected_plane:
                                    continue

                                if customization_tab == 0:
                                    filtered_themes.append((tid, theme))
                                else:
                                    target_cat = categories[customization_tab]
                                    if theme.get("category") == target_cat:
                                        filtered_themes.append((tid, theme))
                            
                            theme_y_start = 180
                            
                            # 遍历筛选后的列表
                            for i, (theme_id, theme) in enumerate(filtered_themes):
                                card_rect = pygame.Rect(350, theme_y_start + i * 100 - customization_scroll_y, 560, 90)
                                
                                # 跳过不可见的卡片 (虽然点击检测不一定需要剔除，但为了性能和逻辑一致性)
                                if card_rect.bottom < 100 or card_rect.top > HEIGHT - 80:
                                    continue
                                
                                is_unlocked = customization_manager.unlocked_themes.get(theme_id, False)
                                btn_x = card_rect.right - 120
                                btn_y = card_rect.y + 25
                                btn_rect = pygame.Rect(btn_x, btn_y, 100, 40)
                                
                                if btn_rect.collidepoint(mx, my):
                                    # 检查专属限制
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
                                        
                                        # 立即更新玩家实例的视觉效果 (如果玩家已存在)
                                        if player and player.plane_id == customization_selected_plane:
                                            try:
                                                new_visual = customization_manager.get_theme_visual(
                                                    customization_selected_plane, 
                                                    PLANES[customization_selected_plane].get('visual', None)
                                                )
                                                player.visual = new_visual
                                                # 重新生成玩家图像
                                                player.image = get_plane_surf(player.plane_id, player.visual)
                                                player.original_image = player.image.copy()
                                            except Exception as e:
                                                print(f"Error updating player visual: {e}")

                                    else:
                                        cost = theme.get("cost", 0)
                                        if arsenal_save_data['currencies']['cores'] >= cost:
                                            success, msg = customization_manager.unlock_theme(theme_id, arsenal_save_data)
                                            customization_msg = msg
                                            customization_msg_timer = 120
                                            if success:
                                                sound_mgr.play("powerup")
                                                save_arsenal()
                                            else:
                                                sound_mgr.play("warning")
                                        else:
                                            customization_msg = f"核心不足，需要 {cost}"
                                            customization_msg_timer = 120
                                            sound_mgr.play("warning")
                                    break
                
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
                            sound_mgr.play_music("normal")
                            sound_mgr.play("select")
                    else:
                        # 游戏进行中：处理点击攻击等逻辑
                        # 注意：这里不需要播放 "select" 音效，也不应该触发暂停
                        # 如果未来需要点击射击，代码写在这里
                        pass

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
                        all_sprites.update()
                        # 更新僚机编队
                        if player.wingman_squadron:
                            player.wingman_squadron.update(mobs)
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
                    
                    if len(mobs) < (10 if not boss else 3):
                        # ========== 改进的敌人刷新系统 ==========
                        # 基础生成率随等级指数增长：从2.5%逐步增至7%（降低早期压力）
                        base_spawn_rate = 0.025 + 0.045 * (1 - math.exp(-player.level / 20))
                        
                        if random.random() < base_spawn_rate:
                            # 根据分数段获取当前游戏阶段（0-4）
                            stage = min(4, score // 2000)
                            
                            # 阶段性敌人池定义 + 加权概率
                            # 格式: (敌人名称, 权重)
                            # 权重越高，出现概率越大
                            stage_pools = [
                                # 阶段0 (0-2000分): 学习期 - 简单敌人为主
                                [
                                    ("drone", 40),
                                    ("chaser", 35),
                                    ("sniper", 15),
                                    ("phantom", 10),
                                ],
                                # 阶段1 (2000-4000分): 过渡期 - 中等难度混合
                                [
                                    ("drone", 20),
                                    ("chaser", 25),
                                    ("tank", 20),
                                    ("spike", 18),
                                    ("sniper", 12),
                                    ("phantom", 5),
                                ],
                                # 阶段2 (4000-6000分): 挑战期 - 难度提升
                                [
                                    ("chaser", 15),
                                    ("tank", 20),
                                    ("spike", 18),
                                    ("wasp", 15),
                                    ("sentinel", 12),
                                    ("sniper", 12),
                                    ("phantom", 8),
                                ],
                                # 阶段3 (6000-8000分): 激烈期 - 高难度为主
                                [
                                    ("tank", 15),
                                    ("wasp", 15),
                                    ("sentinel", 18),
                                    ("glitch", 12),
                                    ("orbiter", 15),
                                    ("phantom", 10),
                                    ("spike", 10),
                                    ("sniper", 5),
                                ],
                                # 阶段4 (8000分+): 绝望期 - 混入最难敌人
                                [
                                    ("wasp", 10),
                                    ("sentinel", 15),
                                    ("glitch", 15),
                                    ("orbiter", 15),
                                    ("vortex", 18),
                                    ("phantom", 12),
                                    ("spike", 12),
                                    ("tank", 7),
                                ],
                            ]
                            
                            # 获取当前阶段敌人池
                            pool = stage_pools[stage]
                            
                            # 加权随机选择
                            enemies = [e[0] for e in pool]
                            weights = [e[1] for e in pool]
                            chosen_type = random.choices(enemies, weights=weights, k=1)[0]
                            
                            Enemy(chosen_type)
                    
                    hits = pygame.sprite.groupcollide(mobs, bullets, False, False)
                    for m, hit_bullets in hits.items():
                        for b in hit_bullets:
                            if b.is_enemy: continue
                            dmg = player.damage
                            if random.random() < player.crit_chance: dmg *= player.crit_mult
                            m.hp -= dmg
                            
                            # ===== 增强打击感（优化版） =====
                            # 1. 屏幕震动（基于伤害）
                            shake_intensity = max(1, min(3, int(dmg / 40)))  # 优化震动强度
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
                                    Particle(m.rect.center, GOLD, lifetime=20)
                                sound_mgr.play("hit")
                            else:
                                sound_mgr.play("hit")
                            
                            # 【新】战斗充能：每次伤害敌人时充能大招
                            ult_charge_gain = dmg / 10  # 伤害值的10%转化为大招能量
                            player.ult_charge = min(player.max_ult_charge, player.ult_charge + ult_charge_gain)
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
                                        Particle(m.rect.center, LIME, lifetime=15)
                                # 屏幕轻微震动
                                screen_shake_offset = apply_screen_shake(3)
                                sound_mgr.play("explosion")
                                
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
                                
                                if random.random() < 0.25:
                                    arsenal_save_data["currencies"]["cores"] += 1
                                    FloatingText(m.rect.centerx, m.rect.top-20, "核心+1", CYAN)
                                m.kill()
                    
                    if not player.is_dashing:
                        hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
                        hits.extend(pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_circle))
                        if hits:
                            dmg = 20
                            # ===== 增强受伤打击感 =====
                            # 屏幕震动反馈
                            screen_shake_offset = apply_screen_shake(8)
                            
                            if player.shield > 0:
                                player.shield -= dmg
                                if player.shield < 0: player.shield = 0
                                # 盾牌吸收时的蓝色特效（简化）
                                if random.random() < 0.3:  # 30%概率显示
                                    for _ in range(2):
                                        angle = random.uniform(0, math.pi * 2)
                                        speed = random.uniform(2, 3)
                                        Particle(player.rect.center, CYAN, lifetime=12)
                            else:
                                player.hp -= dmg
                                FloatingText(player.rect.centerx, player.rect.top, f"-{dmg}", RED)
                                # 受伤时的特效（简化）
                                if random.random() < 0.5:  # 50%概率显示
                                    for _ in range(2):
                                        angle = random.uniform(0, math.pi * 2)
                                        speed = random.uniform(2, 4)
                                        Particle(player.rect.center, RED, lifetime=12)
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
                                        upgrade_options = player.upgrade_manager.upgrade_choice.copy() if player.upgrade_manager.upgrade_choice else []
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
                            # 屏幕轻微震动
                            screen_shake_offset = apply_screen_shake(4)
                            
                            # 击中特效（减少和概率）
                            if random.random() < 0.3:
                                for _ in range(2):
                                    angle = random.uniform(0, math.pi * 2)
                                    speed = random.uniform(3, 5)
                                    Particle(boss.rect.center, (255, 150, 0), lifetime=15)
                            
                            # 音效反馈
                            sound_mgr.play("hit")
                            
                            if b.piercing <= 0: b.kill()
                            if boss.hp <= 0:
                                boss.kill(); boss = None; score += 10000
                                
                                # ===== Boss击杀特效（大幅简化） =====
                                # 屏幕震动
                                screen_shake_offset = apply_screen_shake(10)
                                
                                # 单次爆炸
                                create_explosion(boss.rect.center, (255, 120, 0), 10)
                                
                                # 少量粒子
                                if random.random() < 0.8:
                                    for _ in range(4):
                                        angle = random.uniform(0, math.pi * 2)
                                        speed = random.uniform(4, 7)
                                        Particle(boss.rect.center, GOLD, lifetime=25)
                                
                                # 音效
                                sound_mgr.play("nuke")
                                sound_mgr.play_music("normal")
                                
                                FloatingText(WIDTH//2, HEIGHT//2, "BOSS DEFEATED", GOLD)
                                
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
                safe_call_draw(draw_top_hud)
                # Boss挑战模式进度显示
                if boss_challenge_active and (game_state == "game" or game_state == "boss_challenge_play"):
                    challenge_font = pygame.font.SysFont("SimHei", 28)
                    progress_text = challenge_font.render(f"挑战进度: {boss_challenge_current}/{len(boss_challenge_order)}", True, CYAN)
                    screen.blit(progress_text, (20, HEIGHT - 80))
                safe_call_draw(draw_warning_indicator)  # BOSS警告闪烁边框
                safe_call_draw(draw_achievement_notifications)  # 成就通知
                
                # 显示FPS（中间上方）
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