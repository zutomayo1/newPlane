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

bg_manager = BackgroundManager()
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

# 实体
player = None
boss = None

# 数值
score = 0
combo_count = 0
combo_timer = 0
max_combo_time = 120
boss_warning_timer = 0
next_boss_score = 5000
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

# 图鉴
gallery_page = 0
gallery_tab = 0 # 0:All, 1-4:Rarity

# 档案
codex_tab = 0 # 0:Plane, 1:Boss
codex_idx = 0
codex_scroll_y = 0 

# 暂停菜单状态
pause_menu_selected = 0  # 0: 继续, 1: 重新开始, 2: 退出战斗

# ==============================================================================
# 主菜单选择
main_menu_selected = 0  # 用于键盘导航

# ==============================================================================
#   肉鸽系统相关全局变量
# ==============================================================================
upgrade_options = []  # 升级选择的 3 个选项 [buff_id, ...]
upgrade_selected = 0  # 当前选中的升级索引 (0/1/2)
levelup_ready = False  # 是否显示升级选择 UI
frozen_screen = None  # 升级时冻结的游戏画面

# ==============================================================================
#   辅助函数
# ==============================================================================

def safe_call_draw(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception:
        log_error(f"{fn.__name__} draw error:")
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
    global player, boss, score, combo_count, combo_timer
    global boss_warning_timer, next_boss_score, global_time_freeze, is_paused
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
    combo_count = 0
    combo_timer = 0
    boss_warning_timer = 0
    next_boss_score = 5000
    global_time_freeze = 0
    wave = 0
    boss = None
    
    player = Player(selected_plane)
    
    # 初始化肉鸽系统
    player.init_roguelite_systems()
    
    all_sprites.add(player)
    
    sound_mgr.play_music("normal")
    # reset_game() done

def get_menu_buttons():
    cx = WIDTH // 2
    start_y = 300
    btn_h = 50
    gap = 20
    buttons = []
    data = [
        ("开始游戏", YELLOW, "select_plane"),
        ("武器库", ORANGE, "arsenal"),
        ("战术图鉴", MAGENTA, "gallery"),
        ("机密档案", BLUE, "codex"),
        ("排行榜", CYAN, "leaderboard"),
        ("退出", RED, "quit")
    ]
    for i, (txt, col, act) in enumerate(data):
        r = pygame.Rect(cx - 120, start_y + i*(btn_h+gap), 240, btn_h)
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
    draw_text(screen, "无限进化 中文版", 24, WIDTH//2, 170, WHITE, glow=True)

    mx, my = pygame.mouse.get_pos()
    buttons = get_menu_buttons()
    btn_gap = 32
    for i, (r, txt, col, act) in enumerate(buttons):
        # 按钮间距加大，字号适中
        r.y = 220 + i * (r.height + btn_gap)
        h = r.collidepoint(mx, my) or (i == main_menu_selected)
        bg = (col[0]//2, col[1]//2, col[2]//2) if h else (30, 30, 40)
        draw_cyber_rect(screen, r, bg, alpha=200, fill=True)
        border_col = (CYAN if i == main_menu_selected else col) if h else GRAY
        border_w = 3 if i == main_menu_selected else 2
        draw_cyber_rect(screen, r, border_col, border_width=border_w, fill=False)
        draw_text(screen, f"[ {txt} ]" if h else txt, 22, r.centerx, r.centery-10, WHITE if h else GRAY, glow=h)

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
            draw_text(screen, f"Lv.{w['stars']}", 16, slot_rect.centerx, slot_rect.y+50, WHITE)
        else:
            draw_text(screen, "空槽位", 18, slot_rect.centerx, slot_rect.centery-10, GRAY)
        draw_cyber_rect(screen, slot_rect, bc, border_width=2, fill=False)
        draw_text(screen, f"SLOT {chr(65+i)}", 14, slot_rect.x, slot_rect.y-20, GRAY, align="left")

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
        
        if codex_tab == 0: preview = get_plane_surf(key)
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

    preview = get_plane_surf(pid)
    preview = pygame.transform.scale(preview, (180, 180))
    safe_blit(screen, preview, (cx - 90, cy - 200))

    draw_text(screen, data["name"], 36, cx, cy + 20, data["color"], glow=True)
    draw_text(screen, data["desc"], 18, cx, cy + 70, GRAY)

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

def draw_combo_indicator(kill_count):
    """绘制连击指示器（左侧大字体）"""
    if kill_count < 2:
        return
    
    combo_text = f"{kill_count} 连击!"
    combo_color = CYBER_AMBER if kill_count < 5 else CYBER_RED_ALERT
    
    # 闪烁效果
    alpha_val = int(200 + 55 * math.sin(pygame.time.get_ticks() * 0.015))
    
    # 创建临时surface
    temp_surf = pygame.Surface((400, 100), pygame.SRCALPHA)
    temp_surf.set_alpha(alpha_val)
    
    # 绘制连击文字
    font = pygame.font.SysFont(['arial'], 60, bold=True)
    text_img = font.render(combo_text, True, combo_color)
    text_glow = font.render(combo_text, True, combo_color)
    
    # 发光效果（多层渲染）
    for offset in range(4, 0, -1):
        glow_alpha = int(100 - offset * 20)
        glow_img = font.render(combo_text, True, combo_color)
        glow_img.set_alpha(glow_alpha)
        temp_surf.blit(glow_img, (offset, offset))
    
    temp_surf.blit(text_img, (0, 0))
    safe_blit(screen, temp_surf, (40, 200))

def draw_warning_indicator():
    """绘制BOSS警告指示器（屏幕边框闪烁）"""
    if boss_warning_timer <= 0:
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
    """绘制精简的顶部HUD (仅显示关键信息)"""
    hud_h = 50
    
    # 顶部渐变背景 (从深蓝到透明)
    top_bg = pygame.Surface((WIDTH, hud_h), pygame.SRCALPHA)
    # 绘制渐变效果
    for i in range(hud_h):
        alpha = int(220 * (1 - i/hud_h))
        color = (5, 15, 35, alpha)
        pygame.draw.line(top_bg, color, (0, i), (WIDTH, i))
    safe_blit(screen, top_bg, (0, 0))
    
    # 顶部霓虹线条
    pygame.draw.line(screen, CYBER_CYAN, (0, hud_h), (WIDTH, hud_h), 2)
    pygame.draw.line(screen, CYBER_CYAN_BRIGHT, (0, hud_h+1), (WIDTH, hud_h+1), 1)
    
    # ===== 左侧：等级和经验 =====
    level_x = 20
    level_y = 8
    draw_text(screen, f"LV.{int(player.level)}", 18, level_x, level_y, CYBER_AMBER, glow=True)
    
    # 经验条 (荧光绿炫光)
    exp_bar_x = level_x + 60
    exp_bar_w = 300
    exp_bar_y = level_y + 8
    exp_val = player.xp if hasattr(player, 'xp') else 0
    exp_max = player.next_level_xp if hasattr(player, 'next_level_xp') else 100
    
    # 背景条
    pygame.draw.rect(screen, (20, 30, 20), (exp_bar_x, exp_bar_y, exp_bar_w, 10))
    pygame.draw.rect(screen, (50, 100, 50), (exp_bar_x, exp_bar_y, exp_bar_w, 10), 1)
    
    # 经验条填充 (带炫光)
    exp_fill = (exp_val / exp_max) * exp_bar_w
    if exp_fill > 0:
        pygame.draw.rect(screen, CYBER_LIME, (exp_bar_x, exp_bar_y, exp_fill, 10))
        # 炫光边缘
        if exp_fill > 5:
            pygame.draw.line(screen, (200, 255, 150), (exp_bar_x + exp_fill - 2, exp_bar_y), 
                           (exp_bar_x + exp_fill - 2, exp_bar_y + 10), 2)
    
    exp_txt = f"{int(exp_val)}/{int(exp_max)}"
    draw_text(screen, exp_txt, 10, exp_bar_x + exp_bar_w + 10, exp_bar_y - 1, CYBER_LIME)
    
    # ===== 中央：波数和敌人数 =====
    center_x = WIDTH // 2
    draw_text(screen, f"第 {int(wave)} 波", 16, center_x - 30, level_y, CYBER_CYAN, glow=True)
    draw_text(screen, f"敌人: {len(mobs)}", 14, center_x + 40, level_y, CYBER_RED_ALERT)
    
    # ===== 右侧：生命值和大招 =====
    right_x = WIDTH - 200
    
    # 生命值
    hp_bar_x = right_x
    hp_bar_w = 90
    hp_bar_y = level_y + 8
    hp_pct = (player.hp / player.max_hp) * 100 if player.max_hp > 0 else 0
    hp_color = CYBER_RED_ALERT if hp_pct < 30 else CYBER_AMBER if hp_pct < 60 else CYBER_LIME
    
    pygame.draw.rect(screen, (40, 15, 15), (hp_bar_x, hp_bar_y, hp_bar_w, 10))
    pygame.draw.rect(screen, hp_color, (hp_bar_x, hp_bar_y, hp_bar_w, 10), 1)
    pygame.draw.rect(screen, hp_color, (hp_bar_x, hp_bar_y, (hp_pct/100)*hp_bar_w, 10))
    draw_text(screen, "HP", 10, hp_bar_x - 15, hp_bar_y - 1, WHITE)
    
    # 大招能量
    ult_bar_x = right_x + 110
    ult_bar_w = 90
    ult_pct = (player.ult_charge / player.max_ult_charge) * 100
    ult_color = MAGENTA
    
    pygame.draw.rect(screen, (30, 10, 30), (ult_bar_x, hp_bar_y, ult_bar_w, 10))
    pygame.draw.rect(screen, ult_color, (ult_bar_x, hp_bar_y, ult_bar_w, 10), 1)
    pygame.draw.rect(screen, ult_color, (ult_bar_x, hp_bar_y, (ult_pct/100)*ult_bar_w, 10))
    draw_text(screen, "ULT", 10, ult_bar_x - 15, hp_bar_y - 1, WHITE)
    
    # 分数和时间 (右上角小字)
    draw_text(screen, f"得分: {int(score)}", 12, WIDTH - 150, level_y, CYBER_AMBER)
    draw_text(screen, f"用时: {int(pygame.time.get_ticks()/1000)}s", 11, WIDTH - 150, level_y + 18, WHITE)
    
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

def draw_player_stats_panel():
    """绘制按 TAB 时显示的玩家属性面板（覆盖全屏，但保留背景冻结图像）。"""
    if player is None:
        log_debug("draw_player_stats_panel: player is None, skip")
        return
    # 背景半透明覆盖
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    safe_blit(screen, overlay, (0, 0))

    # 面板主体
    panel_w, panel_h = 720, 520
    panel_x = (WIDTH - panel_w) // 2
    panel_y = (HEIGHT - panel_h) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
    draw_cyber_rect(screen, panel_rect, (18, 18, 28), fill=True)
    draw_cyber_rect(screen, panel_rect, CYAN, border_width=2, fill=False)

    # 标题
    draw_text(screen, "玩家属性面板 (按住 TAB 查看)", 30, panel_rect.centerx, panel_rect.y + 20, CYBER_AMBER, glow=True)

    # 基本属性区（左侧）
    left_x = panel_x + 40
    top_y = panel_y + 80
    draw_text(screen, f"等级: {int(player.level)}", 22, left_x, top_y, WHITE, align="left")
    draw_text(screen, f"经验: {int(player.xp)}/{int(player.next_level_xp)}", 18, left_x, top_y + 30, CYBER_LIME, align="left")
    draw_stat_bar(left_x, top_y + 70, "生命", player.hp, player.max_hp, CYBER_RED_ALERT)
    draw_stat_bar(left_x, top_y + 110, "护盾", player.shield, player.max_hp, CYBER_AMBER)
    draw_stat_bar(left_x, top_y + 150, "火力", player.damage, player.base_damage if hasattr(player, 'base_damage') else max(1, player.damage), CYBER_LIME)
    draw_stat_bar(left_x, top_y + 190, "暴击", player.crit_chance * 100, 100, CYBER_AMBER)

    # 右侧：被动与增益
    right_x = panel_x + panel_w - 340
    ry = top_y
    draw_text(screen, "被动 / 增益", 20, right_x, ry, WHITE, align="left")
    ry += 30
    # 简单列表显示 player.buffs 或 player.active_buffs
    buffs = getattr(player, 'buffs', []) or getattr(player, 'active_buffs', []) or []
    if not buffs:
        draw_text(screen, "无被动增益", 16, right_x, ry, GRAY, align="left")
    else:
        for i, b in enumerate(buffs[:8]):
            name = b if isinstance(b, str) else b.get('name', str(b))
            draw_text(screen, f"- {name}", 16, right_x, ry + i*26, WHITE, align="left")

    # 底部提示
    draw_text(screen, "释放 TAB 恢复游戏", 16, panel_rect.centerx, panel_rect.bottom - 30, GRAY)

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
    draw_text(screen, "↑ ↓ 切换    ENTER 确认", 18, WIDTH//2, HEIGHT - 60, CYAN)

# ==============================================================================
#   主循环
# ==============================================================================
while True:
    try:
        clock.tick(FPS)
        screen.fill(CYBER_DEEP_BLACK)  # 深空黑背景
        
        # 绘制战术网格（仅在游戏中）
        if game_state == "game":
            draw_tactical_grid(screen)
        
        try:
            bg_manager.update(boss_type=boss.type if boss else None, warning=(boss_warning_timer > 0))
            bg_manager.draw(screen)
        except Exception as e:
            log_error(f"BG Manager error: {e}")
        if arsenal_msg_timer > 0: arsenal_msg_timer -= 1
        
        events = pygame.event.get()
        mx, my = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            
            # --- 滚轮事件 (通用) ---
            if event.type == pygame.MOUSEWHEEL:
                if game_state == "codex":
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

            # --- 键盘事件 ---
            if event.type == pygame.KEYDOWN:
                # 菜单子页：ESC 返回主菜单
                if event.key == pygame.K_ESCAPE and game_state in ["arsenal", "gallery", "codex", "leaderboard", "select_plane"]:
                    game_state = "menu"
                    main_menu_selected = 0
                    sound_mgr.play("select")
                    continue
                
                # 快速测试：在选择飞机界面按 ENTER 确认
                if game_state == "select_plane" and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    selected_plane = plane_keys[current_plane_idx]
                    # player selected via keyboard
                    try:
                        reset_game()
                        game_state = "game"
                        # game state changed to game
                    except Exception as e:
                        log_error(f"reset_game failed: {e}")
                        traceback.print_exc()
                        log_error(f"reset_game failed: {e}")
                        game_state = "menu"
                    continue

                # 升级选择 UI 键盘控制
                if levelup_ready and upgrade_options:
                    if event.key == pygame.K_UP:
                        upgrade_selected = (upgrade_selected - 1) % len(upgrade_options)
                        sound_mgr.play("select")
                    elif event.key == pygame.K_DOWN:
                        upgrade_selected = (upgrade_selected + 1) % len(upgrade_options)
                        sound_mgr.play("select")
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # 玩家选择一个增益
                        if 0 <= upgrade_selected < len(upgrade_options):
                            buff_id = upgrade_options[upgrade_selected]
                            player.apply_buff(buff_id)
                            sound_mgr.play("levelup")
                            # 重置升级状态
                            upgrade_options = []
                            upgrade_selected = 0
                            levelup_ready = False
                    continue

                # TAB 键按下：显示属性面板并暂停游戏（仅在游戏中，且不在升级UI时）
                if event.key == pygame.K_TAB and game_state == "game" and not levelup_ready:
                    is_paused = True
                    tab_paused = True
                    if frozen_screen is None:
                        frozen_screen = screen.copy()
                    else:
                        frozen_screen = screen.copy()
                    sound_mgr.play("select")
                    continue

                # 游戏内键盘：P 暂停 (在 game 中), ESC 在 game 中不做任何事
                if game_state == "game":
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
                            if act == "quit": pygame.quit(); sys.exit()
                            elif act == "select_plane": game_state = "select_plane"; current_plane_idx = 0
                            elif act in ["arsenal", "gallery", "codex", "leaderboard"]:
                                game_state = act
                                if act == "gallery": gallery_page = 0; gallery_tab = 0
                                if act == "codex": codex_tab = 0; codex_idx = 0; codex_scroll_y = 0
                                if act == "arsenal": arsenal_scroll_y = 0; arsenal_selected_weapon_idx = -1


            # --- 鼠标点击事件 (严格区分状态，防止冲突) ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                if game_state == "menu":
                    sound_mgr.play("select")
                    for r, txt, col, act in get_menu_buttons():
                        if r.collidepoint(mx, my):
                            if act == "quit": pygame.quit(); sys.exit()
                            elif act == "select_plane": game_state = "select_plane"; current_plane_idx = 0
                            elif act in ["arsenal", "gallery", "codex", "leaderboard"]: 
                                game_state = act
                                if act == "gallery": gallery_page = 0; gallery_tab = 0
                                if act == "codex": codex_tab = 0; codex_idx = 0; codex_scroll_y = 0
                                if act == "arsenal": arsenal_scroll_y = 0; arsenal_selected_weapon_idx = -1

                elif game_state == "select_plane":
                    sound_mgr.play("select")
                    left_rect = pygame.Rect(100, HEIGHT//2-40, 60, 80)
                    right_rect = pygame.Rect(WIDTH-160, HEIGHT//2-40, 60, 80)
                    start_btn = pygame.Rect(WIDTH//2-100, HEIGHT-120, 200, 60)
                    back_btn = pygame.Rect(50, HEIGHT-80, 100, 40)
                    
                    # click detection
                    
                    if left_rect.collidepoint(mx, my):
                        current_plane_idx = (current_plane_idx-1)%len(plane_keys)
                        # left arrow clicked
                    elif right_rect.collidepoint(mx, my):
                        current_plane_idx = (current_plane_idx+1)%len(plane_keys)
                        # right arrow clicked
                    elif start_btn.collidepoint(mx, my):
                        selected_plane = plane_keys[current_plane_idx]
                        # starting game with selected plane
                        try:
                            reset_game()
                            game_state = "game"
                            # game state changed to game
                        except Exception as e:
                            log_error(f"reset_game failed: {e}")
                            traceback.print_exc()
                            log_error(f"reset_game failed: {e}")
                            game_state = "menu"  # 出错时返回菜单
                    elif back_btn.collidepoint(mx, my):
                        game_state = "menu"
                        # returned to menu
                    
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
                    if r['btn_back'].collidepoint(mx, my): game_state = "menu"

                elif game_state == "gallery":
                    sound_mgr.play("select")
                    tb_w = 100; stx = (WIDTH-(5*tb_w+40))//2
                    for i in range(5):
                        if pygame.Rect(stx+i*(tb_w+10), 80, tb_w, 40).collidepoint(mx, my): gallery_tab=i; gallery_page=0
                    if pygame.Rect(50, HEIGHT//2, 50, 50).collidepoint(mx, my) and gallery_page > 0: gallery_page -= 1
                    if pygame.Rect(WIDTH-100, HEIGHT//2, 50, 50).collidepoint(mx, my): gallery_page += 1
                    if pygame.Rect(WIDTH//2-50, HEIGHT-60, 100, 40).collidepoint(mx, my): game_state = "menu"

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
                    if r['btn_back'].collidepoint(mx, my): game_state = "menu"

                elif game_state == "leaderboard":
                    sound_mgr.play("select")
                    if pygame.Rect(WIDTH//2-60, HEIGHT-100, 120, 50).collidepoint(mx, my): game_state = "menu"
                
                # --- 游戏中的点击逻辑 (彻底修复输入冲突) ---
                elif game_state == "game":
                    if is_paused:
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
        elif game_state == "arsenal": 
            draw_arsenal_ui()
        elif game_state == "gallery": 
            draw_gallery_ui()
        elif game_state == "codex": 
            draw_codex_ui()
        elif game_state == "leaderboard": 
            draw_leaderboard_ui()
        elif game_state == "game":
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
                        draw_player_stats_panel()
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
                    draw_text(screen, "PAUSED", 60, WIDTH // 2, HEIGHT // 2 - 100, WHITE, glow=True)

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
                player.shoot()
                
                if global_time_freeze > 0:
                    global_time_freeze -= 1
                    player.update()
                    for s in all_sprites:
                        if isinstance(s, (Particle, FloatingText, FinalBeam, TimeSlash, NukeExplosion, AuroraCurtain, DeathScythe, BlackHole)): s.update()
                else:
                    all_sprites.update()
                    if boss_warning_timer > 0:
                        boss_warning_timer -= 1
                        if boss_warning_timer == 0: boss = Boss(); sound_mgr.play_music("boss")
                    elif not boss and score >= next_boss_score:
                        boss_warning_timer = 180; sound_mgr.stop_music(); sound_mgr.play("warning")
                        next_boss_score += 5000 + (player.level * 1000)
                        for m in mobs: create_explosion(m.rect.center, ORANGE, 10); m.kill()
                    
                    if len(mobs) < (12 if not boss else 4):
                        if random.random() < (0.03 + player.level * 0.002):
                            pool = ["drone", "chaser"]
                            if score > 1000: pool.append("sniper")
                            if score > 2000: pool.append("tank")
                            if score > 3000: pool.append("wasp")
                            if score > 5000: pool.append("glitch")
                            Enemy(random.choice(pool))
                    
                    hits = pygame.sprite.groupcollide(mobs, bullets, False, False)
                    for m, hit_bullets in hits.items():
                        for b in hit_bullets:
                            if b.is_enemy: continue
                            dmg = player.damage
                            if random.random() < player.crit_chance: dmg *= player.crit_mult
                            m.hp -= dmg
                            DamageNumber(m.rect.centerx, m.rect.top, dmg, dmg > player.damage)
                            sound_mgr.play("hit"); Particle(b.rect.center, b.color)
                            if b.piercing <= 0: b.kill()
                            else: b.piercing -= 1
                            if m.hp <= 0:
                                score += 100 if m.is_elite else 20
                                create_explosion(m.rect.center, CYAN, 15); sound_mgr.play("explosion")
                                
                                # ========== 肉鸽系统：击杀敌人效果 ==========
                                # 生成经验球而不是直接给经验
                                xp_amount = 10 if m.is_elite else 5
                                ExperienceOrb(m.rect.centerx, m.rect.centery, xp_amount)
                                FloatingText(m.rect.centerx, m.rect.top - 30, f"EXP+{xp_amount}", LIME)
                                
                                # 触发击杀效果 (吸血、能量虹吸、裂变反应等)
                                corpse_effect = player.on_kill_enemy(m)
                                if corpse_effect:
                                    create_explosion(corpse_effect["pos"], ORANGE, 20)
                                
                                if random.random() < 0.2:
                                    arsenal_save_data["currencies"]["cores"] += 1
                                    FloatingText(m.rect.centerx, m.rect.top-20, "核心+1", CYAN)
                                m.kill()
                    
                    if not player.is_dashing:
                        hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
                        hits.extend(pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_circle))
                        if hits:
                            dmg = 20
                            if player.shield > 0:
                                player.shield -= dmg
                                if player.shield < 0: player.shield = 0
                            else:
                                player.hp -= dmg
                                FloatingText(player.rect.centerx, player.rect.top, f"-{dmg}", RED)
                                sound_mgr.play("hit")
                                if player.hp <= 0: game_state = "menu"; sound_mgr.play("gameover")
                    
                    # ========== 经验球拾取 ==========
                    xp_orbs = [s for s in all_sprites if isinstance(s, ExperienceOrb)]
                    for orb in xp_orbs:
                        # 检查是否碰到玩家或在吸取范围内
                        dist_to_player = math.hypot(orb.rect.centerx - player.rect.centerx, 
                                                    orb.rect.centery - player.rect.centery)
                        
                        if dist_to_player < 40 or pygame.sprite.spritecollide(player, pygame.sprite.Group(orb), False):
                            # 玩家获得经验
                            prev_level = player.level
                            new_level = player.add_xp(orb.amount)
                            FloatingText(orb.rect.centerx, orb.rect.centery, f"EXP {orb.amount}", YELLOW)
                            sound_mgr.play("select")
                            
                            # 检查是否升级（仅在实际升一级时弹卡）
                            if new_level > prev_level and player.upgrade_manager and player.upgrade_manager.level_up_ready:
                                levelup_ready = True
                                upgrade_options = player.upgrade_manager.upgrade_choice
                                upgrade_selected = 0
                                sound_mgr.play("levelup")
                            
                            orb.kill()
                        elif dist_to_player < orb.pickup_range:
                            # 在吸取范围内但未接触：显示视觉提示（可选）
                            pass
                    
                    if boss:
                        bhits = pygame.sprite.spritecollide(boss, bullets, False)
                        for b in bhits:
                            if b.is_enemy: continue
                            boss.hp -= player.damage * 0.5
                            if b.piercing <= 0: b.kill()
                            if boss.hp <= 0:
                                boss.kill(); boss = None; score += 10000
                                sound_mgr.play("nuke"); sound_mgr.play_music("normal")
                                FloatingText(WIDTH//2, HEIGHT//2, "BOSS DEFEATED", GOLD)
                
                safe_call_draw(all_sprites.draw, screen)
                safe_call_draw(player.draw_trail, screen)
                safe_call_draw(player.draw_auras, screen)
                safe_call_draw(draw_top_hud)
                
                # ========== 赛博朋克视觉反馈 ==========
                safe_call_draw(draw_warning_indicator)  # BOSS警告闪烁边框
                if len(mobs) == 0 and wave > 1:
                    safe_call_draw(draw_combo_indicator, int(score // 100))  # 连击指示器
                
                # ========== 肉鸽系统：绘制升级 UI 和被动增益更新 ==========
                if levelup_ready:
                    safe_call_draw(draw_levelup_ui)
                
                # 每帧更新被动增益
                safe_call_draw(player.update_buffs)

        pygame.display.flip()

    except Exception as e:
        # Log main loop exceptions to file
        log_error("Main Loop Error:")
        log_error(traceback.format_exc())