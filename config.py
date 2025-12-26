import pygame
import os
import json

# ==============================================================================
#   屏幕与系统设置
# ==============================================================================
WIDTH = 1280
HEIGHT = 720
FPS = 120

# 存档目录 - 所有玩家数据保存在此
SAVES_DIR = "saves"
os.makedirs(SAVES_DIR, exist_ok=True)

# 文件路径配置（存档类）
LEADERBOARD_FILE = os.path.join(SAVES_DIR, "leaderboard.json")
ARSENAL_FILE = os.path.join(SAVES_DIR, "arsenal.json")
KEY_BINDINGS_FILE = os.path.join(SAVES_DIR, "key_bindings.json")
ACHIEVEMENTS_FILE = os.path.join(SAVES_DIR, "achievements.json")
TALENT_SAVE_FILE = os.path.join(SAVES_DIR, "talent_data.json")
CUSTOMIZATION_FILE = os.path.join(SAVES_DIR, "customization.json")
DAILY_QUESTS_FILE = os.path.join(SAVES_DIR, "daily_quests.json")
GAME_SETTINGS_FILE = os.path.join(SAVES_DIR, "game_settings.json")

# ==============================================================================
#   按键映射系统
# ==============================================================================
# 默认按键配置
DEFAULT_KEY_BINDINGS = {
    # 移动
    "move_up": [pygame.K_UP, pygame.K_w],
    "move_down": [pygame.K_DOWN, pygame.K_s],
    "move_left": [pygame.K_LEFT, pygame.K_a],
    "move_right": [pygame.K_RIGHT, pygame.K_d],
    # 战斗
    "shoot": [pygame.K_SPACE],
    "dash": [pygame.K_LSHIFT, pygame.K_RSHIFT],
    # 武器切换
    "weapon_prev": [pygame.K_q],
    "weapon_next": [pygame.K_e],
    # 技能
    "skill_1": [pygame.K_1],
    "skill_2": [pygame.K_2],
    "skill_3": [pygame.K_3],
    "skill_switch": [pygame.K_t],
    # 大招
    "ultimate_1": [pygame.K_f],
    "ultimate_2": [pygame.K_g],
    "ultimate_3": [pygame.K_c],
    "ultimate_4": [pygame.K_r],
    # 系统
    "pause": [pygame.K_ESCAPE, pygame.K_p],
    "map": [pygame.K_m],
    "tab_info": [pygame.K_TAB],
    "confirm": [pygame.K_RETURN, pygame.K_KP_ENTER],
    "cancel": [pygame.K_ESCAPE, pygame.K_BACKSPACE],
}

# 按键动作名称（用于UI显示）
KEY_ACTION_NAMES = {
    "move_up": "向上移动",
    "move_down": "向下移动",
    "move_left": "向左移动",
    "move_right": "向右移动",
    "shoot": "射击",
    "dash": "冲刺",
    "weapon_prev": "切换上一武器",
    "weapon_next": "切换下一武器",
    "skill_1": "技能1",
    "skill_2": "技能2",
    "skill_3": "技能3",
    "skill_switch": "切换技能模式",
    "ultimate_1": "大招1",
    "ultimate_2": "大招2",
    "ultimate_3": "大招3",
    "ultimate_4": "大招4",
    "pause": "暂停",
    "map": "打开地图",
    "tab_info": "显示信息",
    "confirm": "确认",
    "cancel": "取消/返回",
}

# 按键分组（用于UI分类显示）
KEY_ACTION_GROUPS = {
    "移动": ["move_up", "move_down", "move_left", "move_right"],
    "战斗": ["shoot", "dash"],
    "武器": ["weapon_prev", "weapon_next"],
    "大招": ["ultimate_1", "ultimate_2", "ultimate_3", "ultimate_4"],
    "系统": ["pause", "map", "tab_info", "confirm", "cancel"],
}

# 高级按键分组（默认隐藏，需开启开关才显示）
KEY_ACTION_GROUPS_ADVANCED = {
    "特殊机体": ["skill_1", "skill_2", "skill_3", "skill_switch"],
}

# 按键名称映射（用于显示）
def get_key_name(key_code):
    """获取按键的显示名称"""
    key_names = {
        pygame.K_UP: "↑", pygame.K_DOWN: "↓",
        pygame.K_LEFT: "←", pygame.K_RIGHT: "→",
        pygame.K_SPACE: "空格",
        pygame.K_LSHIFT: "左Shift", pygame.K_RSHIFT: "右Shift",
        pygame.K_LCTRL: "左Ctrl", pygame.K_RCTRL: "右Ctrl",
        pygame.K_LALT: "左Alt", pygame.K_RALT: "右Alt",
        pygame.K_TAB: "Tab", pygame.K_RETURN: "回车",
        pygame.K_ESCAPE: "Esc", pygame.K_BACKSPACE: "退格",
        pygame.K_DELETE: "Delete", pygame.K_INSERT: "Insert",
        pygame.K_HOME: "Home", pygame.K_END: "End",
        pygame.K_PAGEUP: "PgUp", pygame.K_PAGEDOWN: "PgDn",
        pygame.K_F1: "F1", pygame.K_F2: "F2", pygame.K_F3: "F3",
        pygame.K_F4: "F4", pygame.K_F5: "F5", pygame.K_F6: "F6",
        pygame.K_F7: "F7", pygame.K_F8: "F8", pygame.K_F9: "F9",
        pygame.K_F10: "F10", pygame.K_F11: "F11", pygame.K_F12: "F12",
    }
    if key_code in key_names:
        return key_names[key_code]
    # 尝试获取按键字符
    try:
        name = pygame.key.name(key_code)
        if len(name) == 1:
            return name.upper()
        return name.capitalize()
    except:
        return f"键{key_code}"

class KeyBindingManager:
    """按键绑定管理器"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.bindings = {}
        self.load_bindings()
    
    def load_bindings(self):
        """加载按键绑定"""
        try:
            if os.path.exists(KEY_BINDINGS_FILE):
                with open(KEY_BINDINGS_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                # 合并保存的和默认的
                self.bindings = DEFAULT_KEY_BINDINGS.copy()
                for action, keys in saved.items():
                    if action in self.bindings:
                        self.bindings[action] = keys
            else:
                self.bindings = DEFAULT_KEY_BINDINGS.copy()
        except Exception as e:
            print(f"加载按键绑定失败: {e}")
            self.bindings = DEFAULT_KEY_BINDINGS.copy()
    
    def save_bindings(self):
        """保存按键绑定"""
        try:
            with open(KEY_BINDINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.bindings, f, indent=2)
            return True
        except Exception as e:
            print(f"保存按键绑定失败: {e}")
            return False
    
    def reset_to_default(self):
        """重置为默认按键"""
        self.bindings = DEFAULT_KEY_BINDINGS.copy()
        self.save_bindings()
    
    def set_binding(self, action, key_index, new_key):
        """设置按键绑定
        action: 动作名称
        key_index: 第几个按键 (0 或 1)
        new_key: 新的按键代码
        """
        if action not in self.bindings:
            return False
        
        # 检查是否与其他动作冲突
        for other_action, keys in self.bindings.items():
            if other_action != action and new_key in keys:
                # 从其他动作中移除这个按键
                self.bindings[other_action] = [k for k in keys if k != new_key]
        
        # 设置新按键
        while len(self.bindings[action]) <= key_index:
            self.bindings[action].append(0)
        self.bindings[action][key_index] = new_key
        
        # 移除空按键
        self.bindings[action] = [k for k in self.bindings[action] if k != 0]
        
        self.save_bindings()
        return True
    
    def is_action_pressed(self, keys, action):
        """检查动作是否被按下
        keys: pygame.key.get_pressed() 的返回值
        action: 动作名称
        """
        if action not in self.bindings:
            return False
        for key in self.bindings[action]:
            if key and keys[key]:
                return True
        return False
    
    def is_action_key(self, event_key, action):
        """检查事件按键是否匹配某个动作
        event_key: event.key 的值
        action: 动作名称
        """
        if action not in self.bindings:
            return False
        return event_key in self.bindings[action]
    
    def is_any_action_key(self, event_key, actions):
        """检查事件按键是否匹配任一动作
        event_key: event.key 的值
        actions: 动作名称列表
        """
        for action in actions:
            if self.is_action_key(event_key, action):
                return True
        return False
    
    def get_action_keys(self, action):
        """获取动作绑定的按键列表"""
        return self.bindings.get(action, [])
    
    def get_action_key_names(self, action):
        """获取动作按键的显示名称"""
        keys = self.get_action_keys(action)
        return [get_key_name(k) for k in keys if k]

# 全局按键管理器实例
key_binding_manager = None

def get_key_binding_manager():
    """获取按键管理器单例"""
    global key_binding_manager
    if key_binding_manager is None:
        key_binding_manager = KeyBindingManager()
    return key_binding_manager

# ==============================================================================
#   颜色定义 - 赛博朋克霓虹视觉规范
# ==============================================================================
# 核心背景色
CYBER_DEEP_BLACK = (5, 10, 20)      # 深空黑 #050A14
CYBER_MIDNIGHT = (0, 5, 16)          # 午夜蓝 #000510
CYBER_GRID_LINE = (20, 60, 80)       # 淡蓝色网格线

# 主色调 - 极光青/电光蓝
CYBER_CYAN = (0, 255, 255)           # 极光青 #00FFFF
CYBER_CYAN_BRIGHT = (0, 229, 255)   # 电光蓝 #00E5FF

# 警告/敌对色 - 警报红
CYBER_RED_ALERT = (255, 51, 51)     # 警报红 #FF3333
CYBER_RED_DANGER = (255, 0, 0)       # 纯红 #FF0000

# 辅助色
CYBER_LIME = (0, 255, 0)             # 荧光绿 #00FF00
CYBER_AMBER = (255, 215, 0)          # 琥珀黄 #FFD700

# 传统颜色定义（向后兼容）
BLACK = (10, 10, 18)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
LABEL_GRAY = (144, 164, 174)  # #90A4AE
DARK_BG = (5, 10, 20, 230)           # 更新为赛博深空黑
STATS_BG = (5, 10, 20, 240)          # 更新为赛博深空黑

CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
LIME = (50, 255, 50)
GREEN = (0, 255, 0)
YELLOW = (255, 230, 0)
ORANGE = (255, 165, 0)
RED = (255, 60, 60)
BLUE = (60, 100, 255)
SHIELD_BLUE = (100, 200, 255)
HOMING_COLOR = (100, 255, 100)
NEON_GREEN = (0, 255, 128)
GOLD = (255, 215, 0)
ALERT_RED = (255, 0, 50)
TEAL = (0, 128, 128)
DEEP_PURPLE = (80, 0, 120)
CRIMSON = (220, 20, 60)
INDIGO = (75, 0, 130)
FOREST = (34, 139, 34)
WEB_GRAY = (176, 196, 222)
BRIGHT_ORANGE = (255, 69, 0)
NEON_PURPLE = (148, 0, 211)
SCORE_CYAN = (0, 188, 212)  # #00BCD4
SCORE_ORANGE = (255, 107, 0)  # #FF6B00
BADGE_RED = (211, 47, 47)  # #D32F2F
CORE_GRAD_START = (123, 31, 162)  # #7B1FA2
CORE_GRAD_END = (224, 64, 251)  # #E040FB
EYE_RED = (200, 0, 0)
GHOST_CYAN = (180, 255, 255)
WIND_BLUE = (135, 206, 250)
DARK_RED = (100, 0, 0)
DARK_PURPLE = (30, 0, 40)
PURPLE = (150, 50, 255)

# 品质颜色 (1-4星)
RARITY_1_STAR = (150, 150, 150)    # 1星-普通 (灰色)
RARITY_2_STAR = (100, 200, 255)    # 2星-稀有 (蓝色)
RARITY_3_STAR = (200, 100, 255)    # 3星-史诗 (紫色)
RARITY_4_STAR = (255, 200, 50)     # 4星-传说 (金色)
RARITY_5_STAR = (255, 100, 200)    # 5星-神话 (粉紫色)
RARITY_6_STAR = (255, 255, 255)    # 6星-至高 (纯白色)

# 保持兼容旧名称
RARITY_COMMON = RARITY_1_STAR
RARITY_RARE = RARITY_2_STAR
RARITY_EPIC = RARITY_3_STAR
RARITY_LEGEND = RARITY_4_STAR
RARITY_MYTHIC = RARITY_5_STAR
RARITY_SUPREME = RARITY_6_STAR

RARITY_NAMES = ["全部", "1星普通", "2星稀有", "3星史诗", "4星传说", "5星神话", "6星至高"]
RARITY_COLORS = [WHITE, RARITY_1_STAR, RARITY_2_STAR, RARITY_3_STAR, RARITY_4_STAR, RARITY_5_STAR, RARITY_6_STAR]

# ==============================================================================
#   精灵组 (全局单例，防止循环引用)
# ==============================================================================
# 这些组将在其他模块中被引用
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
supplies = pygame.sprite.Group()

# ==============================================================================
#   游戏数据 (机体、物品、BOSS)
# ==============================================================================

# 硬编码的机体数据作为备用 (fallback)
# 正式数据从 data/planes/*.json 加载
_FALLBACK_PLANES = {
    "striker": { "name": "霓虹突击者", "desc": "均衡型战机，擅长持续输出", "hp": 260, "speed": 4.0, "damage": 18, "delay": 180, "color": CYAN, "ult_name": "毁灭光束", "ult_color": CYAN, "bullet_type": "beam", "visual": {"neon_color": CYBER_CYAN_BRIGHT, "accent_color": CYBER_AMBER, "trail_color": CYAN, "ability": "overdrive"} },
    "phantom": { "name": "虚空幻影", "desc": "高机动高射速，终极控制", "hp": 245, "speed": 4.6, "damage": 14, "delay": 150, "color": MAGENTA, "ult_name": "时空冻结", "ult_color": MAGENTA, "bullet_type": "shard", "visual": {"neon_color": MAGENTA, "accent_color": WHITE, "trail_color": MAGENTA, "ability": "phase_shift"} },
    "titan": { "name": "钢铁泰坦", "desc": "重装甲高火力，全屏核爆", "hp": 290, "speed": 3.2, "damage": 26, "delay": 245, "color": ORANGE, "ult_name": "战术核弹", "ult_color": ORANGE, "bullet_type": "rocket", "visual": {"neon_color": CYBER_AMBER, "accent_color": ORANGE, "trail_color": ORANGE, "ability": "armor_plating"} },
    "thunderbird": { "name": "雷霆战鹰", "desc": "发射连锁闪电，召唤雷暴", "hp": 260, "speed": 4.3, "damage": 18, "delay": 175, "color": YELLOW, "ult_name": "雷神降世", "ult_color": YELLOW, "bullet_type": "lightning" },
    "viper": { "name": "剧毒蝰蛇", "desc": "发射腐蚀酸液，持续伤害", "hp": 260, "speed": 3.8, "damage": 18, "delay": 196, "color": LIME, "ult_name": "腐蚀毒雾", "ult_color": LIME, "bullet_type": "acid" },
    "specter": { "name": "幽灵收割者", "desc": "隐形狙击，单发高伤", "hp": 245, "speed": 4.3, "damage": 35, "delay": 320, "color": (150, 100, 255), "ult_name": "死神降临", "ult_color": (150, 100, 255), "bullet_type": "spectral" },
    "aurora": { "name": "极光女神", "desc": "范围打击，控场专家", "hp": 265, "speed": 3.8, "damage": 18, "delay": 160, "color": TEAL, "ult_name": "极光天幕", "ult_color": TEAL, "bullet_type": "aurora_prism", "visual": {"neon_color": TEAL, "accent_color": CYBER_LIME, "trail_color": TEAL, "ability": "area_field"} },
    "crimson": { "name": "绯红之刃", "desc": "近战爆发型，高射速短程光刃", "hp": 250, "speed": 4.5, "damage": 20, "delay": 160, "color": CRIMSON, "ult_name": "鲜血新月", "ult_color": CRIMSON, "bullet_type": "blade" },
    "stalker": { "name": "星界潜行者", "desc": "异星科技，自动追踪星镖", "hp": 250, "speed": 4.2, "damage": 16, "delay": 175, "color": INDIGO, "ult_name": "群星坠落", "ult_color": INDIGO, "bullet_type": "star" },
    "gaia": { "name": "大地守护者", "desc": "坚韧防御型，越战越强的岩石荆棘", "hp": 285, "speed": 3.2, "damage": 22, "delay": 180, "color": FOREST, "ult_name": "自然之怒", "ult_color": FOREST, "bullet_type": "thorn" },
    "weaver": { "name": "虚空编织者", "desc": "控制型，相位蛛网穿透减速", "hp": 255, "speed": 3.9, "damage": 16, "delay": 180, "color": WEB_GRAY, "ult_name": "维度陷阱", "ult_color": WEB_GRAY, "bullet_type": "web" },
    "solar": { "name": "日冕耀斑", "desc": "近战喷火，高频灼烧", "hp": 255, "speed": 4.2, "damage": 10, "delay": 55, "color": BRIGHT_ORANGE, "ult_name": "超新星爆发", "ult_color": BRIGHT_ORANGE, "bullet_type": "flame" },
    "arbiter": { "name": "量子裁决者", "desc": "几何科技，分裂碎片", "hp": 250, "speed": 4.0, "damage": 18, "delay": 196, "color": NEON_PURPLE, "ult_name": "矩阵重置", "ult_color": NEON_PURPLE, "bullet_type": "quant" },
    "eclipse": { "name": "日食幽灵", "desc": "双核心战机，双线射击吸收伤害", "hp": 260, "speed": 4.2, "damage": 14, "delay": 150, "color": (50, 30, 80), "ult_name": "黑日降临", "ult_color": (100, 50, 180), "bullet_type": "shadow", "visual": {"neon_color": (100, 50, 180), "accent_color": (200, 100, 255), "trail_color": (100, 50, 180), "ability": "dual_core"} },
    "prism": { "name": "棱镜分光", "desc": "分裂射击型，一发三道散射", "hp": 255, "speed": 4.2, "damage": 14, "delay": 175, "color": (100, 180, 255), "ult_name": "光谱爆裂", "ult_color": (0, 255, 200), "bullet_type": "prism", "visual": {"neon_color": (0, 255, 200), "accent_color": (100, 200, 255), "trail_color": (100, 180, 255), "ability": "split_fire"} },
    "necro": { "name": "死灵骑士", "desc": "吸血型战机，伤害转化为治疗", "hp": 270, "speed": 3.6, "damage": 17, "delay": 175, "color": (150, 50, 100), "ult_name": "亡灵收割", "ult_color": (200, 50, 150), "bullet_type": "spectral", "visual": {"neon_color": (200, 50, 150), "accent_color": (100, 0, 100), "trail_color": (150, 50, 100), "ability": "lifesteal"} },
    "wormhole": { "name": "混沌虫洞", "desc": "虫洞传送型，子弹从敌人背后虫洞出现", "hp": 245, "speed": 4.8, "damage": 16, "delay": 175, "color": (180, 0, 255), "ult_name": "维度坍缩", "ult_color": (255, 0, 255), "bullet_type": "wormhole", "visual": {"neon_color": (180, 0, 255), "accent_color": (0, 255, 180), "trail_color": (120, 0, 200), "ability": "dimension_rift"} },
    "chronos": { "name": "永恒时计·卡珊德拉", "desc": "掌控时空之力，三相大招操纵过去现在未来", "hp": 245, "speed": 4.4, "damage": 20, "delay": 180, "color": (100, 220, 255), "ult_name": "时空三相", "ult_color": (0, 200, 255), "bullet_type": "chrono", "visual": {"neon_color": (100, 220, 255), "accent_color": (255, 200, 100), "trail_color": (50, 180, 255), "ability": "time_trinity"} },
    "mirage": { "name": "幻镜·万华", "desc": "召唤镜像分身协同作战，分身复制攻击形成弹幕矩阵", "hp": 245, "speed": 4.6, "damage": 15, "delay": 165, "color": (200, 150, 255), "ult_name": "无限镜界", "ult_color": (220, 180, 255), "bullet_type": "mirror", "visual": {"neon_color": (200, 150, 255), "accent_color": (255, 200, 255), "trail_color": (180, 120, 255), "ability": "mirror_dance"} },
    "gambit": { "name": "命运赌徒·艾斯", "desc": "每次攻击随机触发效果，暴击连锁可一发清屏", "hp": 255, "speed": 4.4, "damage": 18, "delay": 180, "color": (255, 215, 0), "ult_name": "命运轮盘", "ult_color": (255, 200, 50), "bullet_type": "card", "visual": {"neon_color": (255, 215, 0), "accent_color": (255, 50, 50), "trail_color": (255, 180, 0), "ability": "fortune_wheel"} },
    "puppeteer": { "name": "牵线木偶师·玛丽奥", "desc": "操控敌人的傀儡师，命中敌人叠加傀儡标记，满层后控制敌人为你作战", "hp": 250, "speed": 4.2, "damage": 16, "delay": 170, "color": (180, 100, 150), "ult_name": "傀儡剧场", "ult_color": (220, 120, 180), "bullet_type": "puppet_string", "visual": {"neon_color": (180, 100, 150), "accent_color": (255, 200, 100), "trail_color": (150, 80, 120), "ability": "puppet_master"} },
    "pandemic": { "name": "末日瘟神·零号", "desc": "病毒传播者，感染在敌群中连锁传播并变异进化，敌人越多越强", "hp": 250, "speed": 4.0, "damage": 15, "delay": 175, "color": (100, 200, 80), "ult_name": "终末审判", "ult_color": (150, 255, 100), "bullet_type": "virus", "visual": {"neon_color": (100, 200, 80), "accent_color": (200, 255, 100), "trail_color": (80, 180, 60), "ability": "plague_spread"} },
    "omega": { "name": "终末神兵·奥米茄", "desc": "融合所有机体精华的终极形态，攻击自动切换七种属性，大招召唤全属性审判", "hp": 280, "speed": 4.8, "damage": 28, "delay": 160, "color": (255, 255, 255), "ult_name": "终焉审判", "ult_color": (255, 220, 255), "bullet_type": "omega_fusion", "visual": {"neon_color": (255, 255, 255), "accent_color": (255, 200, 100), "trail_color": (200, 180, 255), "ability": "omega_fusion"} },
    "genesis": { "name": "创世之翼·起源", "desc": "宇宙原初之力的化身，攻击创造与毁灭并存，大招重塑战场引发宇宙大爆炸", "hp": 270, "speed": 5.0, "damage": 25, "delay": 150, "color": (255, 200, 100), "ult_name": "创世纪元", "ult_color": (255, 230, 150), "bullet_type": "genesis_star", "visual": {"neon_color": (255, 200, 100), "accent_color": (255, 100, 200), "trail_color": (255, 180, 80), "ability": "creation_destruction"} },
    "truth": { "name": "至尊·世界的真相", "desc": "洞察万物本质的终极存在，攻击揭示敌人弱点，真言之眼看穿一切虚假，三大神谕重塑现实", "hp": 290, "speed": 4.6, "damage": 30, "delay": 165, "color": (255, 255, 255), "ult_name": "真理显现", "ult_color": (255, 215, 0), "bullet_type": "truth_revelation", "visual": {"neon_color": (255, 255, 255), "accent_color": (255, 215, 0), "trail_color": (200, 200, 200), "ability": "eye_of_truth"} },
    "asura": { "name": "修罗·斩龙者", "desc": "六臂战神的化身，剑气纵横斩尽苍穹，三道剑气轮斩敌群", "hp": 255, "speed": 5.0, "damage": 28, "delay": 150, "color": (180, 50, 50), "ult_name": "修罗斩", "ult_color": (255, 80, 80), "bullet_type": "sword_slash", "visual": {"neon_color": (180, 50, 50), "accent_color": (255, 100, 60), "trail_color": (200, 80, 80), "ability": "asura_rage"} },
    "dragoon": { "name": "龙骑士·雷因哈特", "desc": "古代龙骑士团的最后传承者，枪气连刺变化多端", "hp": 275, "speed": 4.6, "damage": 32, "delay": 175, "color": (100, 150, 220), "ult_name": "天龙突刺", "ult_color": (120, 180, 255), "bullet_type": "lance_thrust", "visual": {"neon_color": (100, 150, 220), "accent_color": (200, 220, 255), "trail_color": (80, 130, 200), "ability": "dragon_charge"} },
    "origami": { "name": "折纸鹤·零式", "desc": "千羽化形的和平使者，12枚钛刃扇形散射三段弹射，召唤纸鹤群协同作战，折跃复活守护全队", "hp": 240, "speed": 5.2, "damage": 16, "delay": 145, "color": (245, 245, 250), "ult_name": "纸鹤群", "ult_color": (255, 255, 255), "bullet_type": "origami_blade", "visual": {"neon_color": (245, 245, 250), "accent_color": (255, 100, 200), "trail_color": (200, 220, 255), "ability": "fold_revival"} },
    "helios": { "name": "星渊火陨·赫利俄斯", "desc": "超远程AOE轰炸，抛物线火雨弹落地分裂燃烧区，流星群覆盖全场", "hp": 260, "speed": 3.8, "damage": 28, "delay": 900, "color": (255, 100, 20), "ult_name": "流星群", "ult_color": (255, 80, 0), "bullet_type": "meteor", "visual": {"neon_color": (255, 100, 20), "accent_color": (30, 20, 40), "trail_color": (255, 150, 50), "ability": "meteor_shower"} },
    "frostflare": { "name": "极昼寒界·霜曜", "desc": "远程直线冻结，极寒激光穿透2次并减速，命中3次冻结目标2秒", "hp": 250, "speed": 4.0, "damage": 22, "delay": 400, "color": (100, 200, 255), "ult_name": "零度射线", "ult_color": (150, 220, 255), "bullet_type": "frost_laser", "visual": {"neon_color": (100, 200, 255), "accent_color": (220, 240, 255), "trail_color": (150, 220, 255), "ability": "zero_degree"} },
    "nova": { "name": "苍穹轨断·诺娃", "desc": "超远程单点狙击，电磁轨道弹无衰减贯穿全屏，蓄力1秒可穿盾暴击", "hp": 245, "speed": 3.6, "damage": 70, "delay": 1200, "color": (200, 220, 255), "ult_name": "充能击穿", "ult_color": (100, 150, 255), "bullet_type": "railgun", "visual": {"neon_color": (200, 220, 255), "accent_color": (50, 100, 200), "trail_color": (150, 180, 255), "ability": "charge_pierce"} },
    "spectrum": { "name": "天幕虹裂·光谱", "desc": "远程扇形覆盖，7道彩虹光束并行，3道同点命中额外真伤", "hp": 255, "speed": 4.4, "damage": 15, "delay": 180, "color": (200, 200, 220), "ult_name": "光谱叠加", "ult_color": (255, 200, 255), "bullet_type": "rainbow_beam", "visual": {"neon_color": (200, 200, 220), "accent_color": (255, 100, 200), "trail_color": (180, 180, 200), "ability": "spectrum_stack"} },
    "darkstring": { "name": "幽影穿心·冥弦", "desc": "远程标记狙杀，亚音速标记弹可二次暴击，标记3秒内穿墙必暴", "hp": 245, "speed": 4.6, "damage": 65, "delay": 1100, "color": (40, 40, 50), "ult_name": "绝杀狙击", "ult_color": (255, 50, 50), "bullet_type": "mark_shot", "visual": {"neon_color": (40, 40, 50), "accent_color": (255, 50, 50), "trail_color": (80, 80, 100), "ability": "deathmark"} },
    "thornvine": { "name": "棘刺藤骨·荆穹", "desc": "远程骨蔓鞭射，命中后缠绕目标2s持续抽打，受击5次藤骨断裂生成次级短鞭追踪攻击", "hp": 265, "speed": 3.8, "damage": 19, "delay": 600, "color": (240, 240, 230), "ult_charge_rate": 2.5, "ult_name": "骨蔓分裂", "ult_color": (180, 50, 50), "bullet_type": "bone_whip", "visual": {"neon_color": (240, 240, 230), "accent_color": (180, 50, 50), "trail_color": (200, 180, 160), "ability": "vine_split"} },
    "starblade": { "name": "浮游刃环·星镰", "desc": "远程巡航环刃，飞出后悬停水平往返扫割，可召回瞬间加速暴击×1.8", "hp": 250, "speed": 4.3, "damage": 24, "delay": 500, "color": (200, 210, 230), "ult_charge_rate": 2.0, "ult_name": "回环暴击", "ult_color": (100, 180, 255), "bullet_type": "ring_blade", "visual": {"neon_color": (200, 210, 230), "accent_color": (100, 180, 255), "trail_color": (150, 180, 220), "ability": "blade_recall"} },
    "acidswamp": { "name": "酸蚀喷溅·腐沼", "desc": "远程抛物酸囊，落地碎裂6股酸液溅射寻敌附着DOT，3股命中同目标合成酸沼池", "hp": 260, "speed": 4.0, "damage": 18, "delay": 450, "color": (150, 255, 80), "ult_charge_rate": 2.5, "ult_name": "酸液汇合", "ult_color": (100, 200, 50), "bullet_type": "acid_blob", "visual": {"neon_color": (150, 255, 80), "accent_color": (50, 50, 30), "trail_color": (120, 200, 60), "ability": "acid_merge"} },
    "crystalfall": { "name": "晶簇射流·晶瀑", "desc": "远程晶簇扇喷，箭矢落地竖立成晶柱持续穿刺，2柱间距<200px自动连接成水晶墙", "hp": 255, "speed": 4.2, "damage": 20, "delay": 400, "color": (180, 120, 220), "ult_charge_rate": 2.0, "ult_name": "晶簇连锁", "ult_color": (200, 150, 255), "bullet_type": "crystal_arrow", "visual": {"neon_color": (180, 120, 220), "accent_color": (100, 150, 180), "trail_color": (160, 100, 200), "ability": "crystal_link"} },
    "sporeveil": { "name": "孢子幕炮·菌幕", "desc": "远程孢子幕覆盖，炮弹最高点炸开成伞状孢子云持续DOT降命中，累计伤害生成子孢子链式传播", "hp": 265, "speed": 3.9, "damage": 17, "delay": 550, "color": (100, 180, 100), "ult_charge_rate": 2.5, "ult_name": "孢子繁殖", "ult_color": (150, 220, 150), "bullet_type": "spore_shell", "visual": {"neon_color": (100, 180, 100), "accent_color": (240, 250, 240), "trail_color": (80, 150, 80), "ability": "spore_chain"} },
    "cthulhu": { "name": "月蚀星骸·克苏鲁", "desc": "月虹激光贯穿全屏，命中后生成月眼二段真伤，叠加蚀印触发月蚀削弱和星骸剥离", "hp": 290, "speed": 4.6, "damage": 32, "delay": 180, "color": (100, 80, 180), "ult_name": "月蚀降临", "ult_color": (150, 120, 220), "bullet_type": "moon_laser", "visual": {"neon_color": (100, 150, 220), "accent_color": (160, 100, 200), "trail_color": (130, 130, 200), "ability": "eclipse_mark"} },
    "turu": { "name": "巨石核拳·图鲁", "desc": "远程岩核飞拳穿透2次，命中爆裂AOE；巨石充能满格可卸甲强化", "hp": 300, "speed": 3.8, "damage": 35, "delay": 600, "color": (120, 115, 110), "ult_name": "岩拳暴雨", "ult_color": (255, 120, 40), "bullet_type": "rock_fist", "visual": {"neon_color": (255, 120, 40), "accent_color": (120, 115, 110), "trail_color": (180, 100, 30), "ability": "rock_charge"} },
    "staradia": { "name": "辉耀天女·斯塔德", "desc": "虹幕连闪，月虹光梭命中展开辉耀残痕光板，再次普攻激活发射真伤皇辉束；5层升格展开皇辉领域", "hp": 270, "speed": 4.8, "damage": 35, "delay": 140, "color": (255, 180, 220), "ult_name": "皇辉暴雨", "ult_color": (255, 215, 120), "bullet_type": "moon_shuttle", "visual": {"neon_color": (255, 180, 220), "accent_color": (255, 215, 120), "trail_color": (255, 200, 230), "ability": "radiant_ascension"} },
    "dukefishron": { "name": "深渊龙鱼·猪公爵", "desc": "鲨龙卷横扫深渊，水矛命中生成龙卷吸扯+小鲨追踪，再次普攻激活爆炸掉落深渊泡回能", "hp": 285, "speed": 4.6, "damage": 28, "delay": 150, "color": (30, 80, 180), "ult_name": "龙鱼海啸", "ult_color": (255, 120, 180), "bullet_type": "abyss_spear", "visual": {"neon_color": (30, 80, 180), "accent_color": (255, 120, 180), "trail_color": (50, 100, 200), "ability": "shark_tornado"} },
    "slime": { "name": "末世星凝·史莱姆", "desc": "零瞬移漂浮战机，1.4屏超远攻击范围，重力域链式吸附+星凝减益叠层+凝胶子核追踪弹幕", "hp": 280, "speed": 4.4, "damage": 28, "delay": 160, "color": (120, 80, 200), "ult_name": "星陨踩踏", "ult_color": (60, 140, 220), "bullet_type": "star_gel", "visual": {"neon_color": (120, 80, 200), "accent_color": (60, 140, 220), "trail_color": (100, 120, 210), "ability": "gravity_chain"}, "skills": {"skill1": {"name": "星陨踩踏", "desc": "跳跃蓄力后向下重踩，落地时360°散射星炎激光，致命冲击波扩散"}, "skill2": {"name": "星炎水晶", "desc": "部署6颗延迟追踪星炎水晶，短暂悬停后追踪敌人造成高伤害"}, "skill3": {"name": "星凝子体", "desc": "召唤3只自主追踪的星凝子体，接触敌人时自爆造成范围伤害"}} },
    "oro": { "name": "终噬星链·奥罗", "desc": "神明吞噬者零瞬移完全体，1.6屏千节链生长+激光栅十字轰炸+黑洞终噬三维打击", "hp": 300, "speed": 4.4, "damage": 32, "delay": 140, "color": (80, 20, 120), "ult_name": "终噬降临", "ult_color": (200, 50, 80), "bullet_type": "void_chain", "visual": {"neon_color": (80, 20, 120), "accent_color": (200, 50, 80), "trail_color": (120, 40, 160), "ability": "chain_devour"}, "skills": {"skill1": {"name": "千节连生·终噬开幕", "desc": "2s内连续9道链段，每道立即生长至5节形成千节墙，结束后同步爆炸"}, "skill2": {"name": "激光栅风暴·终噬栅灭", "desc": "所有链节4s持续释放十字激光栅，结束时超大范围真伤爆炸"}, "skill3": {"name": "终噬黑洞·终噬闭幕", "desc": "悬浮升空后终噬核心坠地，生成超大黑洞5s持续吞噬，掉落双倍吞噬核"}} },
    "yharon": { "name": "狱炎神龙·犽戎", "desc": "丛林龙王的钢铁化身，日耀喷流+神龙冲拳+炼狱边界浮游炮，构建炼狱力场压制一切", "hp": 300, "speed": 3.8, "damage": 38, "delay": 120, "color": (0, 100, 50), "ult_name": "千兆核爆", "ult_color": (255, 69, 0), "bullet_type": "flare_stream", "visual": {"neon_color": (0, 100, 50), "accent_color": (255, 69, 0), "trail_color": (255, 215, 0), "ability": "border_field"}, "skills": {"skill1": {"name": "千兆核爆", "desc": "火柱从边缘汇聚推挤敌人，中心引爆日蚀之火全屏清屏"}, "skill2": {"name": "龙群盛宴", "desc": "召唤两只机械大黄蜂冲撞敌人并释放环形弹幕"}, "skill3": {"name": "宿敌升天", "desc": "化为巨龙笼罩全屏，光标所指天降地狱火柱"}} },
        "providence": { "name": "亵渎天神·普罗维登斯", "desc": "神圣几何堡垒，三对晶体盾翼可合拢防御回血，圣神爆碎滞留炸弹+亵渎之矛开路+治愈守卫护驾", "hp": 300, "speed": 3.2, "damage": 30, "delay": 220, "color": (255, 215, 0), "ult_name": "熔融之雨", "ult_color": (255, 105, 180), "bullet_type": "holy_shard", "visual": {"neon_color": (255, 215, 0), "accent_color": (255, 105, 180), "trail_color": (255, 165, 0), "ability": "cocoon_mode"}, "skills": {"skill1": {"name": "熔融之雨", "desc": "天降熔岩球覆盖全屏，造成大范围灼烧伤害"}, "skill2": {"name": "神圣射线", "desc": "扇形扫射激光，左右摆动持续伤害"}, "skill3": {"name": "超新星爆发", "desc": "化为神圣太阳，六芒星阵法+晶体阵列+圣光射线360度爆发"}} },
    "goliath": { "name": "瘟疫使者·歌莉娅", "desc": "柴油朋克重型轰炸机，瘟疫导弹滞留毒云+机械蜂群自爆追踪+全屏瘟疫轰炸覆盖", "hp": 290, "speed": 3.6, "damage": 32, "delay": 250, "color": (85, 107, 47), "ult_name": "饱和轰炸", "ult_color": (57, 255, 20), "bullet_type": "plague_missile", "visual": {"neon_color": (85, 107, 47), "accent_color": (57, 255, 20), "trail_color": (100, 150, 80), "ability": "plague_aura"}, "skills": {"skill1": {"name": "饱和轰炸", "desc": "数十枚瘟疫炸弹波浪式覆盖全屏，地毯式打击"}, "skill2": {"name": "瘟疫核弹", "desc": "投下巨型核弹，蘑菇云清屏毁灭一切"}, "skill3": {"name": "盖亚之死", "desc": "15秒废土领域，敌人HP上限-50%，大幅减速"}} },
    "sepulcher": { "name": "至尊灾厄·终末王座", "desc": "哥特式黑曜石祭坛，硫磺火矢折射弹幕+双子魔君僚机+骷髅尾巴浮游炮，擦弹积累暴怒值提升火力", "hp": 220, "speed": 4.2, "damage": 45, "delay": 80, "color": (26, 26, 26), "ult_name": "狱火方阵", "ult_color": (220, 20, 60), "bullet_type": "brimstone_bolt", "visual": {"neon_color": (220, 20, 60), "accent_color": (255, 69, 0), "trail_color": (180, 30, 30), "ability": "calamity_aura"}, "skills": {"skill1": {"name": "狱火方阵", "desc": "火墙缩圈困敌，骷髅尾巴脱离反弹绞杀"}, "skill2": {"name": "天降灾厄", "desc": "血红天空降下硫磺火球暴雨，全屏轰炸"}, "skill3": {"name": "湮灭之眼", "desc": "灾厄之眼暴睁，1/3屏宽毁灭光束持续5秒"}} },
    "galaxia": { "name": "宇宙之弧·Galaxia", "desc": "宇宙之弧泰拉之刃的剪刀变形机甲，近战剪切攻击+30%弹反系统+撕裂全屏的时空之刃", "hp": 260, "speed": 4.5, "damage": 35, "delay": 60, "color": (75, 0, 130), "ult_name": "次元斩击", "ult_color": (147, 112, 219), "bullet_type": "scissor_slash", "visual": {"neon_color": (147, 112, 219), "accent_color": (255, 215, 0), "trail_color": (138, 43, 226), "ability": "parry_system"}, "skills": {"skill1": {"name": "次元斩击", "desc": "三道紫光剪切波纹从上到下撕裂全屏"}, "skill2": {"name": "星系陷阱", "desc": "剪刀旋转在屏幕中心引力聚敌，释放星座弹幕"}, "skill3": {"name": "苍穹撕裂", "desc": "巨型剪刀撕开屏幕，星辰从裂缝中喷涌而出"}} },
    "magnus": { "name": "真理之书·MAGNUS", "desc": "魔典飞行堡垒，奥术飞弹追踪+法术轮盘三系魔法+书页护盾+真理魔法阵", "hp": 275, "speed": 4.2, "damage": 28, "delay": 180, "color": (100, 60, 150), "ult_name": "真理魔法阵", "ult_color": (255, 215, 100), "bullet_type": "arcane_missile", "visual": {"neon_color": (100, 150, 220), "accent_color": (255, 215, 100), "trail_color": (120, 80, 180), "ability": "spell_roulette"}, "skills": {"skill1": {"name": "极寒暴风雪", "desc": "召唤冰晶雨覆盖全屏，冻结敌人5秒"}, "skill2": {"name": "远古亡灵召唤", "desc": "巨型骷髅头追踪冲撞，造成80点伤害"}, "skill3": {"name": "真理魔法阵", "desc": "展开金色魔法阵持续灼烧+定身敌人"}} },
    "heavymetal": { "name": "维那斯万岁·HEAVY METAL", "desc": "飞行双颈电吉他堡垒，音符弹幕+强力和弦冲击波+舞台俯冲+死亡金属独奏全屏音波", "hp": 265, "speed": 4.4, "damage": 32, "delay": 90, "color": (148, 0, 211), "ult_name": "死亡金属独奏", "ult_color": (0, 255, 0), "bullet_type": "note_blaster", "visual": {"neon_color": (148, 0, 211), "accent_color": (0, 255, 0), "trail_color": (255, 0, 128), "ability": "bpm_sync"}, "skills": {"skill1": {"name": "强力和弦", "desc": "90°扇形冲击波清弹+击退敌人"}, "skill2": {"name": "舞台俯冲", "desc": "火焰流星从天而降，200伤害+150像素爆炸"}, "skill3": {"name": "死亡金属独奏", "desc": "全屏音波持续伤害+敌人混乱效果"}} },
    "scarlet": { "name": "绯红恶魔·SCARLET", "desc": "东方幻想风高速截击机，潜行刺客机制+吸血被动+迷雾闪烁瞬移+绯红不夜城弹幕+命运之枪+深红世界时停斩击", "hp": 240, "speed": 5.2, "damage": 38, "delay": 70, "color": (220, 20, 60), "ult_name": "迷雾闪烁", "ult_color": (255, 215, 0), "bullet_type": "scarlet_lance", "visual": {"neon_color": (220, 20, 60), "accent_color": (255, 215, 0), "trail_color": (128, 0, 0), "ability": "stealth_meter"}, "skills": {"skill1": {"name": "迷雾闪烁", "desc": "化作红雾瞬移，过程无敌并对穿过的敌人造成伤害"}, "skill2": {"name": "绯红不夜城", "desc": "东方弹幕风格高密度规则弹幕花纹覆盖全屏"}, "skill3": {"name": "命运之枪", "desc": "投掷贯穿全屏的巨大红色光枪，在尽头爆炸"}, "skill4": {"name": "深红世界", "desc": "时停领域展开，分身斩击全屏敌人，造成大量伤害"}} },
    "zenith": { "name": "分形天顶·ZENITH", "desc": "终极剑阵回旋镖母舰，十余把泰拉名剑环绕旋转形成力场，回旋剑刃穿透攻击+分形护盾格挡+棱镜合体巨剑斩击", "hp": 280, "speed": 4.8, "damage": 35, "delay": 100, "color": (75, 0, 130), "ult_name": "天顶霸主", "ult_color": (255, 255, 255), "bullet_type": "throwing_sword", "visual": {"neon_color": (75, 0, 130), "accent_color": (255, 255, 255), "trail_color": (255, 0, 255), "ability": "fractal_shield"}, "skills": {"skill1": {"name": "泰拉光束", "desc": "召唤绿色泰拉刃幻影，发射全屏绿色剑气波"}, "skill2": {"name": "喵星人轰炸", "desc": "召唤大量彩虹猫头疯狂反弹，留下彩虹轨迹"}, "skill3": {"name": "天顶霸主", "desc": "化作分形圆环，所有剑以鬼畜速度全屏乱舞，背景崩坏成像素碎片"}} },
    "viscerator": { "name": "光之在解·VISCERATOR", "desc": "双推进粒子加速炮机体，EXO科技结晶。追踪光流攻击+火花积累爆炸+推进器反转冲击+毁灭之光", "hp": 270, "speed": 4.6, "damage": 32, "delay": 85, "color": (47, 79, 79), "ult_name": "推进器反转", "ult_color": (255, 20, 147), "bullet_type": "exo_stream", "visual": {"neon_color": (255, 20, 147), "accent_color": (127, 255, 0), "trail_color": (47, 79, 79), "ability": "spark_accumulation"}, "skills": {"skill1": {"name": "推进器反转", "desc": "向后释放锥形光爆，击退敌人并清除弹幕"}, "skill2": {"name": "归束轰击", "desc": "双引擎光流汇聚成穿透光束，贯穿全屏"}, "skill3": {"name": "星流过载", "desc": "召唤环绕棱镜，自动发射追踪激光持续伤害"}, "skill4": {"name": "毁灭之光", "desc": "DNA双螺旋激光旋转扫射全屏，造成毁灭性伤害"}} },
    "crusher": { "name": "晶体粉碎者·CRUSHER", "desc": "重型太空采矿舰，晶体钻头激光切割器。荒芜光束穿透攻击+相位冲撞破盾+牵引光束拉敌+共振破碎全屏震爆+核心过载终极", "hp": 300, "speed": 3.8, "damage": 30, "delay": 120, "color": (138, 43, 226), "ult_name": "相位冲撞", "ult_color": (230, 230, 250), "bullet_type": "desolation_beam", "visual": {"neon_color": (138, 43, 226), "accent_color": (230, 230, 250), "trail_color": (25, 25, 25), "ability": "collision_resist"}, "skills": {"skill1": {"name": "相位冲撞", "desc": "向前相位冲刺，过程无敌并击穿敌人护盾"}, "skill2": {"name": "牵引光束", "desc": "扇形牵引波将敌人拉向玩家并减速"}, "skill3": {"name": "共振破碎", "desc": "全屏晶体震爆，伤害所有敌人并清除敌弹"}, "skill4": {"name": "次元坍缩", "desc": "巨型晶体钻头从天而降，撞击全屏产生毁灭性爆炸，护甲层数越高伤害越大"}} },
    "sdmg": { "name": "星际海豚·S.D.M.G.", "desc": "生物机械海豚加特林，叶绿弹道弱追踪+过热超频系统+海星雷吸附爆炸+鲨卷风导弹齐射+月球领主幻影手掌+轨道轰炸毁灭光束", "hp": 255, "speed": 4.8, "damage": 24, "delay": 17, "color": (0, 255, 255), "ult_name": "鲨卷风", "ult_color": (192, 192, 192), "bullet_type": "chlorophyte_tracer", "visual": {"neon_color": (0, 255, 255), "accent_color": (192, 192, 192), "trail_color": (100, 200, 255), "ability": "overheat_system"}, "skills": {"skill1": {"name": "海星雷", "desc": "发射旋转海星炸弹，吸附敌人后延迟爆炸"}, "skill2": {"name": "鲨卷风", "desc": "发射数十枚鲨鱼导弹，形成龙卷风轨迹"}, "skill3": {"name": "月球领主之凝视", "desc": "召唤幻影手掌跟随，持续发射穿透光球"}, "skill4": {"name": "轨道轰炸", "desc": "召唤轨道炮瞄准，多道垂直毁灭光束从天而降"}} }
}

# ==============================================================================
#   从 JSON 加载 PLANES 数据（优先使用 JSON，失败时回退到硬编码）
# ==============================================================================

def _load_planes_from_json():
    """
    尝试从 JSON 文件加载机体数据
    
    Returns:
        加载的 PLANES 字典，失败时返回 _FALLBACK_PLANES
    """
    try:
        from utils.asset_manager import asset_manager
        loaded = asset_manager.load_planes_dict(_FALLBACK_PLANES)
        if loaded:
            return loaded
    except Exception as e:
        print(f"[config] Failed to load planes from JSON: {e}, using fallback")
    return _FALLBACK_PLANES

# PLANES 字典 - 从 JSON 加载，JSON 不可用时使用硬编码备用
PLANES = _load_planes_from_json()

# 硬编码的 Boss 数据作为备用 (fallback)
_FALLBACK_BOSS_DB = {
    # Boss 1: 菌生蟹皇 - 重型生物坦克，六足震地，孢子地雷+菌丝波浪
    "fungal_colossus": {
        "name": "菌生蟹皇",
        "desc": "迟缓但致命的重型生物坦克，背负古代利维坦头骨，每一步都伴随震动。",
        "color": (30, 80, 120),
        "stats": [("装甲", 120), ("毁灭", 75), ("机动", 15)],
        "visual": {"core_color": (30, 80, 120), "aura": (60, 180, 200), "phase_effect": "ground_shake"},
        "phases": [
            {"threshold": 0.8, "effect": {"type": "spore_saturation", "count": 5}, "fire_rate_mult": 0.9},
            {"threshold": 0.5, "effect": {"type": "mycelium_wave", "count": 2}, "fire_rate_mult": 0.75},
            {"threshold": 0.25, "effect": {"type": "ground_shake", "count": 3}, "fire_rate_mult": 0.6}
        ]
    },
    # Boss 2: 旱海狂鲨 - 突袭刺客，利用屏幕外空间进行突袭
    "dune_reaper": {
        "name": "旱海狂鲨",
        "desc": "利用屏幕外空间进行突袭的刺客，无眼锯齿口器，身体漏出流沙与能量光。",
        "color": (180, 140, 60),
        "stats": [("装甲", 65), ("毁灭", 90), ("机动", 95)],
        "visual": {"core_color": (180, 140, 60), "aura": (220, 180, 80), "phase_effect": "sand_trail"},
        "phases": [
            {"threshold": 0.75, "effect": {"type": "blindspot_rush", "count": 3}, "fire_rate_mult": 0.85},
            {"threshold": 0.45, "effect": {"type": "quicksand_vortex", "count": 1}, "fire_rate_mult": 0.7},
            {"threshold": 0.2, "effect": {"type": "blindspot_rush", "count": 5}, "fire_rate_mult": 0.5}
        ]
    },
    # Boss 3: 歌莉娅女王 - 高机动空中轰炸机，弹幕密度极大
    "plague_empress": {
        "name": "歌莉娅女王",
        "desc": "高机动的空中轰炸机，腹部透明离心机翻滚毒液，翅膀挂载多管导弹巢。",
        "color": (85, 180, 47),
        "stats": [("装甲", 70), ("毁灭", 95), ("机动", 85)],
        "visual": {"core_color": (85, 180, 47), "aura": (57, 255, 20), "phase_effect": "toxic_trail"},
        "phases": [
            {"threshold": 0.8, "effect": {"type": "matrix_bombing", "count": 4}, "fire_rate_mult": 0.9},
            {"threshold": 0.5, "effect": {"type": "matrix_bombing", "count": 3}, "fire_rate_mult": 0.75},
            {"threshold": 0.25, "effect": {"type": "matrix_bombing", "count": 5}, "fire_rate_mult": 0.55}
        ]
    },
    # Boss 4: 毁灭魔像 - 阵地战，极高血量，几乎填满屏幕
    "flesh_totem": {
        "name": "毁灭魔像",
        "desc": "由古代黑砖和鲜活肌肉缝合而成，双臂是悬浮石拳，只有一只巨大电子眼。",
        "color": (60, 20, 20),
        "stats": [("装甲", 150), ("毁灭", 80), ("机动", 5)],
        "visual": {"core_color": (60, 20, 20), "aura": (180, 30, 30), "phase_effect": "blood_seep"},
        "phases": [
            {"threshold": 0.85, "effect": {"type": "rocket_fist", "count": 2}, "fire_rate_mult": 0.9},
            {"threshold": 0.55, "effect": {"type": "stone_pillar_cage", "count": 3}, "fire_rate_mult": 0.7},
            {"threshold": 0.3, "effect": {"type": "rocket_fist", "count": 4}, "fire_rate_mult": 0.5}
        ]
    },
    # Boss 5: 星神游龙 - 多判定点激光阵列，20节浮游单元
    "star_serpent": {
        "name": "星神游龙",
        "desc": "半透明黑曜石晶体，内部封印流动星云，20节分离浮游单元靠引力场维持蛇形。",
        "color": (100, 50, 150),
        "stats": [("装甲", 80), ("毁灭", 100), ("机动", 70)],
        "visual": {"core_color": (100, 50, 150), "aura": (200, 100, 255), "phase_effect": "nebula_flow"},
        "phases": [
            {"threshold": 0.8, "effect": {"type": "star_position_laser", "count": 5}, "fire_rate_mult": 0.85},
            {"threshold": 0.5, "effect": {"type": "fission_charge", "count": 2}, "fire_rate_mult": 0.7},
            {"threshold": 0.25, "effect": {"type": "star_position_laser", "count": 8}, "fire_rate_mult": 0.5}
        ]
    },
    # Boss 6: 终焉巨械·阿瑞斯 - 武器切换与组合技，纳米液态金属
    "exo_ares": {
        "name": "终焉巨械·阿瑞斯",
        "desc": "完美纳米液态金属表面，骷髅核心周围悬浮四条机械触手，RGB霓虹光带。",
        "color": (200, 200, 220),
        "stats": [("装甲", 90), ("毁灭", 110), ("机动", 60)],
        "visual": {"core_color": (200, 200, 220), "aura": (255, 100, 255), "phase_effect": "rgb_pulse"},
        "phases": [
            {"threshold": 0.8, "effect": {"type": "weapon_roulette", "count": 4}, "fire_rate_mult": 0.9},
            {"threshold": 0.5, "effect": {"type": "clock_beam", "count": 4}, "fire_rate_mult": 0.7},
            {"threshold": 0.2, "effect": {"type": "weapon_roulette", "count": 6}, "fire_rate_mult": 0.5}
        ]
    },
    # Boss 7: 亵渎天神 - 贪刀惩罚与治疗干扰，视觉致盲
    "radiance_goddess": {
        "name": "亵渎天神",
        "desc": "燃烧的熔岩心脏被三对彩色玻璃晶体翼包裹，全身散发金色粒子尘埃。",
        "color": (255, 215, 0),
        "stats": [("装甲", 85), ("毁灭", 85), ("机动", 25)],
        "visual": {"core_color": (255, 215, 0), "aura": (255, 180, 100), "phase_effect": "holy_radiance"},
        "phases": [
            {"threshold": 0.8, "effect": {"type": "cocoon_defense", "count": 3}, "fire_rate_mult": 0.95},
            {"threshold": 0.5, "effect": {"type": "holy_judgment", "count": 5}, "fire_rate_mult": 0.7},
            {"threshold": 0.25, "effect": {"type": "fractal_beam", "count": 6}, "fire_rate_mult": 0.5}
        ]
    },
    # Boss 8: 维度之噬 - 必杀技与反应速度测试，碰头即死
    "dimension_devourer": {
        "name": "维度之噬",
        "desc": "Vantablack绝对黑装甲吸收所有光线，极长身躯延伸至屏幕外，颚部张开是紫色漩涡。",
        "color": (20, 0, 40),
        "stats": [("装甲", 75), ("毁灭", 120), ("机动", 90)],
        "visual": {"core_color": (20, 0, 40), "aura": (120, 0, 200), "phase_effect": "dimension_crack"},
        "phases": [
            {"threshold": 0.75, "effect": {"type": "dimension_charge", "count": 3}, "fire_rate_mult": 0.85},
            {"threshold": 0.45, "effect": {"type": "laser_cage", "count": 6}, "fire_rate_mult": 0.65},
            {"threshold": 0.2, "effect": {"type": "dimension_charge", "count": 5}, "fire_rate_mult": 0.45}
        ]
    },
    # Boss 9: 暴君犽戎 - 限制场地内的极速肉搏
    "infernal_dragon": {
        "name": "暴君犽戎",
        "desc": "原始红色龙鳞与金色机械骨骼的结合体，心脏是金源泰斯拉反应堆，翅膀是日耀火焰。",
        "color": (255, 69, 0),
        "stats": [("装甲", 85), ("毁灭", 100), ("机动", 100)],
        "visual": {"core_color": (255, 69, 0), "aura": (255, 200, 50), "phase_effect": "inferno_aura"},
        "phases": [
            {"threshold": 0.8, "effect": {"type": "sonic_dash", "count": 3}, "fire_rate_mult": 0.85},
            {"threshold": 0.5, "effect": {"type": "scorched_earth", "count": 8}, "fire_rate_mult": 0.65},
            {"threshold": 0.2, "effect": {"type": "sonic_dash", "count": 5}, "fire_rate_mult": 0.45}
        ]
    },
    # Boss 10: 熵之化身 - 规则破坏与最终考验，打破第四面墙
    "entropy_avatar": {
        "name": "熵之化身",
        "desc": "漂浮虚空的苍白巨人躯干，胸口手心额头三只真理之眼，触手化为光纤数据线。",
        "color": (220, 220, 230),
        "stats": [("装甲", 100), ("毁灭", 100), ("机动", 10)],
        "visual": {"core_color": (220, 220, 230), "aura": (255, 255, 255), "phase_effect": "ui_interference"},
        "phases": [
            {"threshold": 0.8, "effect": {"type": "phantom_deathray", "count": 1}, "fire_rate_mult": 0.9},
            {"threshold": 0.5, "effect": {"type": "life_drain", "count": 3}, "fire_rate_mult": 0.7},
            {"threshold": 0.2, "effect": {"type": "phantom_deathray", "count": 2}, "fire_rate_mult": 0.5}
        ]
    },
    # Boss 11: 绝音夜煞 - 声波可视化战斗，听觉压迫
    "sonic_banshee": {
        "name": "绝音夜煞",
        "desc": "覆盖漆黑吸音绒毛，胸腔是惨白骨质扬声器。无脸，只有大嘴和无底扩音喇叭喉咙。",
        "color": (30, 30, 50),
        "stats": [("装甲", 70), ("毁灭", 95), ("机动", 85)],
        "visual": {"core_color": (30, 30, 50), "aura": (200, 200, 255), "phase_effect": "sonic_distortion"},
        "phases": [
            {"threshold": 0.8, "effect": {"type": "echo_pulse", "count": 3}, "fire_rate_mult": 0.9},
            {"threshold": 0.5, "effect": {"type": "sonic_scream", "count": 5}, "fire_rate_mult": 0.7},
            {"threshold": 0.25, "effect": {"type": "sonic_distortion", "count": 6}, "fire_rate_mult": 0.5}
        ]
    },
    # Boss 12: 棱镜核心 - 光线折射与激光网
    "prism_overlord": {
        "name": "棱镜核心",
        "desc": "悬浮正二十面体，每面幻彩镜面，内封雷电球。6块浮游折射盾如钻石切面般璀璨。",
        "color": (150, 220, 255),
        "stats": [("装甲", 95), ("毁灭", 110), ("机动", 20)],
        "visual": {"core_color": (150, 220, 255), "aura": (255, 180, 255), "phase_effect": "prism_refract"},
        "phases": [
            {"threshold": 0.8, "effect": {"type": "prism_laser", "count": 4}, "fire_rate_mult": 0.85},
            {"threshold": 0.5, "effect": {"type": "mirror_shield", "count": 3}, "fire_rate_mult": 0.7},
            {"threshold": 0.25, "effect": {"type": "laser_web", "count": 6}, "fire_rate_mult": 0.5}
        ]
    },
    # Boss 13: 腐朽剑圣 - 极快攻速与格挡机制
    "rotting_kensei": {
        "name": "腐朽剑圣",
        "desc": "残破战国盔甲，缝隙中钻出红色寄生触手。40米野太刀生锈却泛妖异紫光，攻击留下水墨残影。",
        "color": (80, 30, 80),
        "stats": [("装甲", 65), ("毁灭", 130), ("机动", 110)],
        "visual": {"core_color": (80, 30, 80), "aura": (200, 100, 255), "phase_effect": "ink_trail"},
        "phases": [
            {"threshold": 0.8, "effect": {"type": "blade_storm", "count": 4}, "fire_rate_mult": 0.8},
            {"threshold": 0.5, "effect": {"type": "iai_slash", "count": 2}, "fire_rate_mult": 0.6},
            {"threshold": 0.25, "effect": {"type": "death_blade", "count": 5}, "fire_rate_mult": 0.4}
        ]
    },
    # Boss 14: 悖论时钟 - 时间流速控制与倒带
    "paradox_clockwork": {
        "name": "悖论时钟",
        "desc": "黄铜齿轮与蒸汽管道构成的机械天使，背后巨大表盘光环。脸是破碎怀表，手握沙漏法杖。",
        "color": (200, 160, 60),
        "stats": [("装甲", 90), ("毁灭", 85), ("机动", 40)],
        "visual": {"core_color": (200, 160, 60), "aura": (255, 220, 100), "phase_effect": "time_distort"},
        "phases": [
            {"threshold": 0.8, "effect": {"type": "time_slow", "count": 3}, "fire_rate_mult": 0.9},
            {"threshold": 0.5, "effect": {"type": "stasis_field", "count": 4}, "fire_rate_mult": 0.7},
            {"threshold": 0.25, "effect": {"type": "time_rewind", "count": 2}, "fire_rate_mult": 0.5}
        ]
    },
    # Boss 15: 熔核巨兽 - 地形破坏与岩浆漫灌
    "molten_behemoth": {
        "name": "熔核巨兽",
        "desc": "活过来的火山，皮肤是冷却黑曜石，裂缝流淌高亮橙色岩浆。下半身融化在地面，在岩浆池中游泳。",
        "color": (255, 80, 20),
        "stats": [("装甲", 140), ("毁灭", 100), ("机动", 10)],
        "visual": {"core_color": (255, 80, 20), "aura": (255, 180, 50), "phase_effect": "lava_surge"},
        "phases": [
            {"threshold": 0.8, "effect": {"type": "lava_wave", "count": 4}, "fire_rate_mult": 0.9},
            {"threshold": 0.5, "effect": {"type": "meteor_rain", "count": 5}, "fire_rate_mult": 0.7},
            {"threshold": 0.25, "effect": {"type": "eruption", "count": 6}, "fire_rate_mult": 0.5}
        ]
    }
}

# ==============================================================================
#   从 JSON 加载 BOSS_DB 数据
# ==============================================================================

def _load_boss_db_from_json():
    """
    尝试从 JSON 文件加载 Boss 数据
    """
    try:
        from utils.asset_manager import asset_manager
        loaded = asset_manager.load_boss_db(_FALLBACK_BOSS_DB)
        if loaded:
            return loaded
    except Exception as e:
        print(f"[config] Failed to load bosses from JSON: {e}, using fallback")
    return _FALLBACK_BOSS_DB

# BOSS_DB 字典 - 从 JSON 加载，JSON 不可用时使用硬编码备用
BOSS_DB = _load_boss_db_from_json()
BOSS_KEYS = list(BOSS_DB.keys())

WEAPON_TYPES = {
    "cannon": {"name": "赤热机炮", "type": "热能", "desc": "高射速，持续射击会导致过热。", "color": RED},
    "beam": {"name": "聚焦光束", "type": "能量", "desc": "持续照射，消耗能量槽。", "color": CYAN},
    "explosive": {"name": "等离子雷", "type": "爆破", "desc": "范围伤害，弹药有限需装填。", "color": ORANGE},
    "missile": {"name": "毒蛇导弹", "type": "追踪", "desc": "自动追踪，发射后有冷却。", "color": LIME},
    "exotic": {"name": "奇点透镜", "type": "特种", "desc": "特殊效果，极长冷却。", "color": MAGENTA},
    "scatter": {"name": "碎星霰弹", "type": "动能", "desc": "扇形发射多枚弹片，近战爆发极高。", "color": (200, 200, 200)},
    "arc": {"name": "弧光电涌", "type": "电磁", "desc": "发射连锁闪电，自动跳跃攻击。", "color": YELLOW},
    "sniper": {"name": "量子狙击", "type": "穿透", "desc": "极慢射速，无限穿透，单发毁灭。", "color": (0, 100, 255)},
    "blade": {"name": "回旋利刃", "type": "切割", "desc": "发射回旋飞刃，二段伤害。", "color": CRIMSON},
    "railgun": {"name": "磁轨炮", "type": "贯穿", "desc": "电磁加速，瞬间贯穿直线所有敌人。", "color": (0, 255, 255)},
    "void": {"name": "虚空裂隙", "type": "力场", "desc": "发射缓慢移动的黑洞球，持续伤害。", "color": (100, 0, 200)},
    "frost": {"name": "极寒冰刺", "type": "控制", "desc": "高射速冰弹，命中后冻结敌人。", "color": (200, 255, 255)},
    "swarm": {"name": "蜂群导弹", "type": "全弹", "desc": "一次性发射大量微型导弹。", "color": (255, 100, 150)},
    "pulse": {"name": "脉冲波", "type": "冲击", "desc": "发射扩散冲击波，近距离伤害倍增。", "color": (0, 200, 200)},
    "vortex": {"name": "次元漩涡", "type": "扭曲", "desc": "发射减速漩涡，敌人陷入后移动缓慢。", "color": (200, 0, 255)},
    "gravity": {"name": "重力眼", "type": "引力", "desc": "吸引周围敌人，缓慢但持续伤害。", "color": (150, 50, 200)},
    "wave": {"name": "能量海啸", "type": "推进", "desc": "发射推进波，击退敌人并造成伤害。", "color": (100, 255, 200)},
    "inferno": {"name": "地狱烈焰", "type": "灼烧", "desc": "持续燃烧效果，敌人陷入火焰中持续掉血。", "color": (255, 100, 0)},
    "split": {"name": "分裂弹头", "type": "爆裂", "desc": "击中后分裂成多发子弹，链式传播。", "color": (255, 200, 0)},
}


SYNERGIES = {
    frozenset(["cannon", "missile"]): {"name": "穿甲爆破", "desc": "穿透+1，爆炸范围+20%"},
    frozenset(["beam", "exotic"]): {"name": "能量过载", "desc": "伤害+15%，射速+10%"},
    frozenset(["scatter", "blade"]): {"name": "近身格斗", "desc": "近战伤害+30%，弹射速度+20%"},
    frozenset(["arc", "sniper"]): {"name": "电磁轨道", "desc": "暴击率+10%，子弹飞行速度+30%"},
}

# ==============================================================================
#   UI主题系统
# ==============================================================================
UI_THEMES = {
    "cyberpunk": {
        "name": "赛博朋克",
        "desc": "霓虹闪烁的未来都市风格",
        "primary": (0, 255, 255),      # 主色调 - 青色
        "secondary": (255, 0, 255),    # 次要色 - 品红
        "accent": (255, 215, 0),       # 强调色 - 金色
        "background": (5, 10, 20),     # 背景色
        "panel": (15, 25, 40),         # 面板色
        "text": (255, 255, 255),       # 文本色
        "text_dim": (120, 130, 150),   # 暗淡文本
        "success": (0, 255, 100),      # 成功色
        "warning": (255, 200, 0),      # 警告色
        "danger": (255, 60, 60),       # 危险色
        "border": (60, 80, 100),       # 边框色
        "glow": True,                  # 是否有发光效果
    },
    "retro": {
        "name": "复古街机",
        "desc": "怀旧的像素游戏风格",
        "primary": (255, 200, 0),      # 主色调 - 黄色
        "secondary": (255, 100, 50),   # 次要色 - 橙红
        "accent": (100, 255, 100),     # 强调色 - 绿色
        "background": (20, 12, 28),    # 背景色 - 深紫
        "panel": (40, 25, 50),         # 面板色
        "text": (255, 255, 200),       # 文本色 - 暖白
        "text_dim": (150, 130, 100),   # 暗淡文本
        "success": (100, 255, 100),    # 成功色
        "warning": (255, 200, 50),     # 警告色
        "danger": (255, 80, 80),       # 危险色
        "border": (100, 80, 60),       # 边框色
        "glow": False,                 # 无发光效果
    },
    "military": {
        "name": "军事战术",
        "desc": "硬核的军用HUD风格",
        "primary": (0, 255, 128),      # 主色调 - 军绿
        "secondary": (200, 180, 100),  # 次要色 - 沙漠色
        "accent": (255, 100, 0),       # 强调色 - 橙色
        "background": (10, 15, 10),    # 背景色 - 深绿
        "panel": (20, 30, 20),         # 面板色
        "text": (200, 255, 200),       # 文本色 - 淡绿
        "text_dim": (100, 130, 100),   # 暗淡文本
        "success": (0, 255, 0),        # 成功色
        "warning": (255, 255, 0),      # 警告色
        "danger": (255, 50, 50),       # 危险色
        "border": (60, 80, 60),        # 边框色
        "glow": False,                 # 无发光效果
    },
    "neon_pink": {
        "name": "霓虹粉红",
        "desc": "充满活力的粉色主题",
        "primary": (255, 100, 200),    # 主色调 - 粉色
        "secondary": (150, 50, 255),   # 次要色 - 紫色
        "accent": (0, 255, 255),       # 强调色 - 青色
        "background": (20, 5, 25),     # 背景色 - 深紫
        "panel": (40, 15, 50),         # 面板色
        "text": (255, 230, 250),       # 文本色
        "text_dim": (150, 100, 140),   # 暗淡文本
        "success": (150, 255, 150),    # 成功色
        "warning": (255, 200, 100),    # 警告色
        "danger": (255, 80, 120),      # 危险色
        "border": (100, 50, 100),      # 边框色
        "glow": True,                  # 有发光效果
    },
    "ice": {
        "name": "极地冰霜",
        "desc": "清冷的冰雪世界风格",
        "primary": (150, 220, 255),    # 主色调 - 冰蓝
        "secondary": (200, 180, 255),  # 次要色 - 淡紫
        "accent": (255, 255, 255),     # 强调色 - 白色
        "background": (10, 20, 35),    # 背景色 - 深蓝
        "panel": (20, 35, 55),         # 面板色
        "text": (230, 245, 255),       # 文本色
        "text_dim": (100, 140, 170),   # 暗淡文本
        "success": (100, 255, 200),    # 成功色
        "warning": (255, 220, 150),    # 警告色
        "danger": (255, 100, 150),     # 危险色
        "border": (60, 100, 140),      # 边框色
        "glow": True,                  # 有发光效果
    },
}

# 当前主题（默认赛博朋克）
current_theme = "cyberpunk"

def get_theme():
    """获取当前主题配置"""
    return UI_THEMES.get(current_theme, UI_THEMES["cyberpunk"])

def set_theme(theme_id):
    """设置当前主题"""
    global current_theme
    if theme_id in UI_THEMES:
        current_theme = theme_id
        return True
    return False


# ==============================================================================
#   星轨天赋阵系统
# ==============================================================================

TALENT_TREE = {
    # ==================== 毁灭星轨 ====================
    "destruction": {
        "name": "毁灭星轨",
        "subtitle": "歼灭一切",
        "color": RED,
        "icon": "🔴",
        "branches": {
            # 爆发分支
            "burst": {
                "name": "爆发",
                "talents": {
                    "sharp": {
                        "name": "锐利", "icon": "🗡️", "max_level": 5,
                        "desc": "基础伤害 +{value}%",
                        "values": [5, 10, 15, 20, 25],
                        "costs": [5, 10, 15, 20, 25],
                        "effect": {"damage_mult": [0.05, 0.10, 0.15, 0.20, 0.25]},
                        "tier": 1
                    },
                    "heavy": {
                        "name": "重击", "icon": "💥", "max_level": 5,
                        "desc": "暴击率 +{value}%",
                        "values": [4, 8, 12, 16, 20],
                        "costs": [10, 15, 20, 25, 30],
                        "effect": {"crit_chance": [0.04, 0.08, 0.12, 0.16, 0.20]},
                        "tier": 2, "requires": "sharp"
                    },
                    "fatal": {
                        "name": "致命", "icon": "☠️", "max_level": 5,
                        "desc": "暴击伤害 +{value}%",
                        "values": [20, 40, 60, 80, 100],
                        "costs": [15, 20, 25, 30, 40],
                        "effect": {"crit_damage": [0.20, 0.40, 0.60, 0.80, 1.00]},
                        "tier": 3, "requires": "heavy"
                    },
                    "execute": {
                        "name": "处决", "icon": "💀", "max_level": 5,
                        "desc": "敌人<30%血时伤害 +{value}%",
                        "values": [15, 30, 45, 60, 75],
                        "costs": [25, 30, 40, 50, 60],
                        "effect": {"execute_damage": [0.15, 0.30, 0.45, 0.60, 0.75]},
                        "tier": 4, "requires": "fatal"
                    },
                }
            },
            # 持续分支
            "sustained": {
                "name": "持续",
                "talents": {
                    "swift": {
                        "name": "迅捷", "icon": "⚡", "max_level": 5,
                        "desc": "射速 +{value}%",
                        "values": [6, 12, 18, 24, 30],
                        "costs": [5, 10, 15, 20, 25],
                        "effect": {"fire_rate": [0.06, 0.12, 0.18, 0.24, 0.30]},
                        "tier": 1
                    },
                    "precise": {
                        "name": "精准", "icon": "🎯", "max_level": 5,
                        "desc": "弹速 +{value}%",
                        "values": [10, 20, 30, 40, 50],
                        "costs": [10, 15, 20, 25, 30],
                        "effect": {"bullet_speed": [0.10, 0.20, 0.30, 0.40, 0.50]},
                        "tier": 2, "requires": "swift"
                    },
                    "pierce": {
                        "name": "穿透", "icon": "🔗", "max_level": 5,
                        "desc": "穿透 +{value}",
                        "values": [1, 1, 2, 2, 3],
                        "costs": [15, 20, 25, 30, 40],
                        "effect": {"pierce": [1, 1, 2, 2, 3]},
                        "tier": 3, "requires": "precise"
                    },
                    "endless": {
                        "name": "无尽", "icon": "♾️", "max_level": 5,
                        "desc": "击杀回复{value}%能量",
                        "values": [1, 2, 3, 4, 5],
                        "costs": [25, 30, 40, 50, 60],
                        "effect": {"kill_energy": [0.01, 0.02, 0.03, 0.04, 0.05]},
                        "tier": 4, "requires": "pierce"
                    },
                }
            },
            # 特效分支
            "effect": {
                "name": "特效",
                "talents": {
                    "burn": {
                        "name": "灼烧", "icon": "🔥", "max_level": 5,
                        "desc": "攻击附带燃烧({value}s)",
                        "values": [2, 3, 4, 5, 6],
                        "costs": [5, 10, 15, 20, 25],
                        "effect": {"burn_duration": [2, 3, 4, 5, 6]},
                        "tier": 1
                    },
                    "freeze": {
                        "name": "冰封", "icon": "❄️", "max_level": 5,
                        "desc": "攻击{value}%几率冻结1s",
                        "values": [5, 10, 15, 20, 25],
                        "costs": [10, 15, 20, 25, 30],
                        "effect": {"freeze_chance": [0.05, 0.10, 0.15, 0.20, 0.25]},
                        "tier": 2, "requires": "burn"
                    },
                    "thunder": {
                        "name": "雷击", "icon": "⚡", "max_level": 5,
                        "desc": "攻击{value}%几率连锁闪电",
                        "values": [8, 12, 16, 20, 25],
                        "costs": [15, 20, 25, 30, 40],
                        "effect": {"chain_chance": [0.08, 0.12, 0.16, 0.20, 0.25]},
                        "tier": 3, "requires": "freeze"
                    },
                    "void_strike": {
                        "name": "虚空", "icon": "🌀", "max_level": 5,
                        "desc": "攻击{value}%几率双倍伤害",
                        "values": [3, 5, 7, 9, 12],
                        "costs": [25, 30, 40, 50, 60],
                        "effect": {"double_damage_chance": [0.03, 0.05, 0.07, 0.09, 0.12]},
                        "tier": 4, "requires": "thunder"
                    },
                }
            },
        },
        "ultimate": {
            "name": "歼星者", "icon": "🔥",
            "desc": "狂暴状态伤害+50%，持续+3s，冷却-30%",
            "effect": {"rage_damage": 0.50, "rage_duration": 3, "rage_cooldown": 0.30},
            "requires_t4": True
        },
    },
    
    # ==================== 守护星轨 ====================
    "guardian": {
        "name": "守护星轨",
        "subtitle": "坚不可摧",
        "color": CYAN,
        "icon": "🔵",
        "branches": {
            # 护盾分支
            "shield": {
                "name": "护盾",
                "talents": {
                    "capacitor": {
                        "name": "电容", "icon": "🔋", "max_level": 5,
                        "desc": "护盾容量 +{value}%",
                        "values": [10, 20, 30, 40, 50],
                        "costs": [5, 10, 15, 20, 25],
                        "effect": {"shield_capacity": [0.10, 0.20, 0.30, 0.40, 0.50]},
                        "tier": 1
                    },
                    "recharge": {
                        "name": "充能", "icon": "⚡", "max_level": 5,
                        "desc": "护盾回复 +{value}%",
                        "values": [15, 30, 45, 60, 75],
                        "costs": [10, 15, 20, 25, 30],
                        "effect": {"shield_regen": [0.15, 0.30, 0.45, 0.60, 0.75]},
                        "tier": 2, "requires": "capacitor"
                    },
                    "reflect": {
                        "name": "反射", "icon": "🪞", "max_level": 5,
                        "desc": "护盾反弹{value}%伤害",
                        "values": [5, 10, 15, 20, 25],
                        "costs": [15, 20, 25, 30, 40],
                        "effect": {"shield_reflect": [0.05, 0.10, 0.15, 0.20, 0.25]},
                        "tier": 3, "requires": "recharge"
                    },
                    "crystallize": {
                        "name": "晶化", "icon": "💠", "max_level": 5,
                        "desc": "护盾满时减伤 +{value}%",
                        "values": [15, 20, 25, 30, 35],
                        "costs": [25, 30, 40, 50, 60],
                        "effect": {"full_shield_reduction": [0.15, 0.20, 0.25, 0.30, 0.35]},
                        "tier": 4, "requires": "reflect"
                    },
                }
            },
            # 生命分支
            "vitality": {
                "name": "生命",
                "talents": {
                    "sturdy": {
                        "name": "强壮", "icon": "💚", "max_level": 5,
                        "desc": "最大生命 +{value}%",
                        "values": [8, 16, 24, 32, 40],
                        "costs": [5, 10, 15, 20, 25],
                        "effect": {"max_hp": [0.08, 0.16, 0.24, 0.32, 0.40]},
                        "tier": 1
                    },
                    "regen": {
                        "name": "再生", "icon": "💗", "max_level": 5,
                        "desc": "每3s回复{value}%生命",
                        "values": [1, 1.5, 2, 2.5, 3],
                        "costs": [10, 15, 20, 25, 30],
                        "effect": {"hp_regen_percent": [0.01, 0.015, 0.02, 0.025, 0.03]},
                        "tier": 2, "requires": "sturdy"
                    },
                    "leech": {
                        "name": "汲取", "icon": "🩸", "max_level": 5,
                        "desc": "击杀回复{value}%生命",
                        "values": [1, 2, 3, 4, 5],
                        "costs": [15, 20, 25, 30, 40],
                        "effect": {"kill_heal": [0.01, 0.02, 0.03, 0.04, 0.05]},
                        "tier": 3, "requires": "regen"
                    },
                    "unyielding": {
                        "name": "不屈", "icon": "♻️", "max_level": 5,
                        "desc": "血量<25%时减伤 +{value}%",
                        "values": [10, 15, 20, 25, 30],
                        "costs": [25, 30, 40, 50, 60],
                        "effect": {"low_hp_reduction": [0.10, 0.15, 0.20, 0.25, 0.30]},
                        "tier": 4, "requires": "leech"
                    },
                }
            },
            # 闪避分支
            "evasion": {
                "name": "闪避",
                "talents": {
                    "agile": {
                        "name": "灵巧", "icon": "🏃", "max_level": 5,
                        "desc": "移动速度 +{value}%",
                        "values": [5, 10, 15, 20, 25],
                        "costs": [5, 10, 15, 20, 25],
                        "effect": {"move_speed": [0.05, 0.10, 0.15, 0.20, 0.25]},
                        "tier": 1
                    },
                    "dodge": {
                        "name": "闪避", "icon": "💨", "max_level": 5,
                        "desc": "闪避率 +{value}%",
                        "values": [3, 6, 9, 12, 15],
                        "costs": [10, 15, 20, 25, 30],
                        "effect": {"dodge_chance": [0.03, 0.06, 0.09, 0.12, 0.15]},
                        "tier": 2, "requires": "agile"
                    },
                    "afterimage": {
                        "name": "残影", "icon": "👻", "max_level": 5,
                        "desc": "闪避后{value}s无敌",
                        "values": [0.3, 0.5, 0.7, 0.9, 1.2],
                        "costs": [15, 20, 25, 30, 40],
                        "effect": {"dodge_invuln": [0.3, 0.5, 0.7, 0.9, 1.2]},
                        "tier": 3, "requires": "dodge"
                    },
                    "surge": {
                        "name": "涌动", "icon": "🌊", "max_level": 5,
                        "desc": "被击后移速+{value}% 2s",
                        "values": [20, 30, 40, 50, 60],
                        "costs": [25, 30, 40, 50, 60],
                        "effect": {"hit_speed_boost": [0.20, 0.30, 0.40, 0.50, 0.60]},
                        "tier": 4, "requires": "afterimage"
                    },
                }
            },
        },
        "ultimate": {
            "name": "不朽堡垒", "icon": "🛡️",
            "desc": "每局首次致死伤害改为剩余1HP，获得3s无敌",
            "effect": {"death_save": True, "save_invuln": 3},
            "requires_t4": True
        },
    },
    
    # ==================== 命运星轨 ====================
    "destiny": {
        "name": "命运星轨",
        "subtitle": "命运编织",
        "color": YELLOW,
        "icon": "🟡",
        "branches": {
            # 成长分支
            "growth": {
                "name": "成长",
                "talents": {
                    "scholar": {
                        "name": "学识", "icon": "📚", "max_level": 5,
                        "desc": "经验获取 +{value}%",
                        "values": [8, 16, 24, 32, 40],
                        "costs": [5, 10, 15, 20, 25],
                        "effect": {"exp_mult": [0.08, 0.16, 0.24, 0.32, 0.40]},
                        "tier": 1
                    },
                    "magnet": {
                        "name": "磁力", "icon": "🧲", "max_level": 5,
                        "desc": "拾取范围 +{value}%",
                        "values": [20, 40, 60, 80, 100],
                        "costs": [10, 15, 20, 25, 30],
                        "effect": {"pickup_range": [0.20, 0.40, 0.60, 0.80, 1.00]},
                        "tier": 2, "requires": "scholar"
                    },
                    "treasure": {
                        "name": "宝藏", "icon": "💎", "max_level": 5,
                        "desc": "掉落率 +{value}%",
                        "values": [5, 10, 15, 20, 25],
                        "costs": [15, 20, 25, 30, 40],
                        "effect": {"drop_rate": [0.05, 0.10, 0.15, 0.20, 0.25]},
                        "tier": 3, "requires": "magnet"
                    },
                    "starshine": {
                        "name": "星耀", "icon": "⭐", "max_level": 5,
                        "desc": "升级{value}%几率额外+1级",
                        "values": [10, 15, 20, 25, 30],
                        "costs": [25, 30, 40, 50, 60],
                        "effect": {"double_levelup": [0.10, 0.15, 0.20, 0.25, 0.30]},
                        "tier": 4, "requires": "treasure"
                    },
                }
            },
            # 幸运分支
            "fortune": {
                "name": "幸运",
                "talents": {
                    "lucky": {
                        "name": "幸运", "icon": "🍀", "max_level": 5,
                        "desc": "稀有卡概率 +{value}%",
                        "values": [5, 10, 15, 20, 25],
                        "costs": [5, 10, 15, 20, 25],
                        "effect": {"rare_chance": [0.05, 0.10, 0.15, 0.20, 0.25]},
                        "tier": 1
                    },
                    "draw": {
                        "name": "抽牌", "icon": "🃏", "max_level": 5,
                        "desc": "选卡数量 +{value}",
                        "values": [0, 0, 1, 1, 1],
                        "costs": [10, 15, 20, 25, 30],
                        "effect": {"extra_choices": [0, 0, 1, 1, 1]},
                        "tier": 2, "requires": "lucky"
                    },
                    "sparkle": {
                        "name": "闪耀", "icon": "✨", "max_level": 5,
                        "desc": "每{value}次选卡必出金卡",
                        "values": [5, 4, 3, 2, 2],
                        "costs": [15, 20, 25, 30, 40],
                        "effect": {"gold_pity": [5, 4, 3, 2, 2]},
                        "tier": 3, "requires": "draw"
                    },
                    "gambler": {
                        "name": "赌运", "icon": "🎰", "max_level": 5,
                        "desc": "卡牌效果{value}%几率翻倍",
                        "values": [5, 8, 12, 16, 20],
                        "costs": [25, 30, 40, 50, 60],
                        "effect": {"card_double": [0.05, 0.08, 0.12, 0.16, 0.20]},
                        "tier": 4, "requires": "sparkle"
                    },
                }
            },
            # 僚机分支
            "wingman": {
                "name": "僚机",
                "talents": {
                    "synergy": {
                        "name": "协同", "icon": "👥", "max_level": 5,
                        "desc": "僚机伤害 +{value}%",
                        "values": [10, 20, 30, 40, 50],
                        "costs": [5, 10, 15, 20, 25],
                        "effect": {"wingman_damage": [0.10, 0.20, 0.30, 0.40, 0.50]},
                        "tier": 1
                    },
                    "sync": {
                        "name": "同步", "icon": "🔄", "max_level": 5,
                        "desc": "僚机射速 +{value}%",
                        "values": [10, 20, 30, 40, 50],
                        "costs": [10, 15, 20, 25, 30],
                        "effect": {"wingman_fire_rate": [0.10, 0.20, 0.30, 0.40, 0.50]},
                        "tier": 2, "requires": "synergy"
                    },
                    "formation": {
                        "name": "编队", "icon": "🛸", "max_level": 5,
                        "desc": "僚机上限 +{value}",
                        "values": [0, 0, 1, 1, 2],
                        "costs": [15, 20, 25, 30, 40],
                        "effect": {"wingman_max": [0, 0, 1, 1, 2]},
                        "tier": 3, "requires": "sync"
                    },
                    "resonance": {
                        "name": "共鸣", "icon": "🌐", "max_level": 5,
                        "desc": "僚机继承{value}%属性",
                        "values": [30, 40, 50, 60, 70],
                        "costs": [25, 30, 40, 50, 60],
                        "effect": {"wingman_inherit": [0.30, 0.40, 0.50, 0.60, 0.70]},
                        "tier": 4, "requires": "formation"
                    },
                }
            },
        },
        "ultimate": {
            "name": "命运织者", "icon": "🌟",
            "desc": "选卡可免费刷新一次，商店价格-20%",
            "effect": {"free_reroll": 1, "shop_discount": 0.20},
            "requires_t4": True
        },
    },
}

# 超限核心
ULTIMATE_CORES = {
    "star_resonance": {
        "name": "星轨共鸣", "icon": "⭐",
        "desc": "所有已解锁天赋效果 +25%",
        "effect": {"talent_boost": 0.25},
        "requires_points": 45  # 三条路线各15点
    },
    "fate_control": {
        "name": "命运掌控", "icon": "🎯",
        "desc": "开局可选1张金卡携带",
        "effect": {"start_gold_card": 1},
        "requires_points": 45
    },
    "infinite_potential": {
        "name": "无限潜能", "icon": "♾️",
        "desc": "等级上限+5，每级额外属性",
        "effect": {"level_cap": 5, "level_bonus": 0.02},
        "requires_points": 45
    },
}

# 路线共鸣（点满20点解锁）
PATH_RESONANCE = {
    "destruction": {
        "name": "毁灭共鸣",
        "desc": "连续击杀叠加伤害，最高+30%",
        "effect": {"kill_streak_damage": 0.30},
        "requires_points": 20
    },
    "guardian": {
        "name": "守护共鸣",
        "desc": "受伤后3秒内减伤逐渐增加，最高+25%",
        "effect": {"damage_taken_reduction": 0.25},
        "requires_points": 20
    },
    "destiny": {
        "name": "命运共鸣",
        "desc": "每拾取5个道具，下次选卡+1选择",
        "effect": {"pickup_extra_choice": 5},
        "requires_points": 20
    },
}