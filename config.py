import pygame
import os

# ==============================================================================
#   屏幕与系统设置
# ==============================================================================
WIDTH = 1280
HEIGHT = 720
FPS = 120

# 文件路径配置
LEADERBOARD_FILE = "leaderboard.json"
ARSENAL_FILE = "arsenal.json"

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

PLANES = {
    "striker": { "name": "霓虹突击者", "desc": "均衡型战机，擅长持续输出", "hp": 160, "speed": 4.0, "damage": 18, "delay": 180, "color": CYAN, "ult_name": "毁灭光束", "ult_color": CYAN, "bullet_type": "beam", "visual": {"neon_color": CYBER_CYAN_BRIGHT, "accent_color": CYBER_AMBER, "trail_color": CYAN, "ability": "overdrive"} },
    "phantom": { "name": "虚空幻影", "desc": "高机动高射速，终极控制", "hp": 145, "speed": 4.6, "damage": 14, "delay": 150, "color": MAGENTA, "ult_name": "时空冻结", "ult_color": MAGENTA, "bullet_type": "shard", "visual": {"neon_color": MAGENTA, "accent_color": WHITE, "trail_color": MAGENTA, "ability": "phase_shift"} },
    "titan": { "name": "钢铁泰坦", "desc": "重装甲高火力，全屏核爆", "hp": 190, "speed": 3.2, "damage": 26, "delay": 245, "color": ORANGE, "ult_name": "战术核弹", "ult_color": ORANGE, "bullet_type": "rocket", "visual": {"neon_color": CYBER_AMBER, "accent_color": ORANGE, "trail_color": ORANGE, "ability": "armor_plating"} },
    "thunderbird": { "name": "雷霆战鹰", "desc": "发射连锁闪电，召唤雷暴", "hp": 160, "speed": 4.3, "damage": 18, "delay": 175, "color": YELLOW, "ult_name": "雷神降世", "ult_color": YELLOW, "bullet_type": "lightning" },
    "viper": { "name": "剧毒蝰蛇", "desc": "发射腐蚀酸液，持续伤害", "hp": 160, "speed": 3.8, "damage": 18, "delay": 196, "color": LIME, "ult_name": "腐蚀毒雾", "ult_color": LIME, "bullet_type": "acid" },
    "specter": { "name": "幽灵收割者", "desc": "隐形狙击，单发高伤", "hp": 145, "speed": 4.3, "damage": 35, "delay": 320, "color": (150, 100, 255), "ult_name": "死神降临", "ult_color": (150, 100, 255), "bullet_type": "spectral" },
    "aurora": { "name": "极光女神", "desc": "范围打击，控场专家", "hp": 165, "speed": 3.8, "damage": 18, "delay": 160, "color": TEAL, "ult_name": "极光天幕", "ult_color": TEAL, "bullet_type": "aurora_prism", "visual": {"neon_color": TEAL, "accent_color": CYBER_LIME, "trail_color": TEAL, "ability": "area_field"} },
    "crimson": { "name": "绯红之刃", "desc": "近战爆发型，高射速短程光刃", "hp": 150, "speed": 4.5, "damage": 20, "delay": 160, "color": CRIMSON, "ult_name": "鲜血新月", "ult_color": CRIMSON, "bullet_type": "blade" },
    "stalker": { "name": "星界潜行者", "desc": "异星科技，自动追踪星镖", "hp": 150, "speed": 4.2, "damage": 16, "delay": 175, "color": INDIGO, "ult_name": "群星坠落", "ult_color": INDIGO, "bullet_type": "star" },
    "gaia": { "name": "大地守护者", "desc": "坚韧防御型，越战越强的岩石荆棘", "hp": 185, "speed": 3.2, "damage": 22, "delay": 180, "color": FOREST, "ult_name": "自然之怒", "ult_color": FOREST, "bullet_type": "thorn" },
    "weaver": { "name": "虚空编织者", "desc": "控制型，相位蛛网穿透减速", "hp": 155, "speed": 3.9, "damage": 16, "delay": 180, "color": WEB_GRAY, "ult_name": "维度陷阱", "ult_color": WEB_GRAY, "bullet_type": "web" },
    "solar": { "name": "日冕耀斑", "desc": "近战喷火，高频灼烧", "hp": 155, "speed": 4.2, "damage": 10, "delay": 55, "color": BRIGHT_ORANGE, "ult_name": "超新星爆发", "ult_color": BRIGHT_ORANGE, "bullet_type": "flame" },
    "arbiter": { "name": "量子裁决者", "desc": "几何科技，分裂碎片", "hp": 150, "speed": 4.0, "damage": 18, "delay": 196, "color": NEON_PURPLE, "ult_name": "矩阵重置", "ult_color": NEON_PURPLE, "bullet_type": "quant" },
    "eclipse": { "name": "日食幽灵", "desc": "双核心战机，双线射击吸收伤害", "hp": 160, "speed": 4.2, "damage": 14, "delay": 150, "color": (50, 30, 80), "ult_name": "黑日降临", "ult_color": (100, 50, 180), "bullet_type": "shadow", "visual": {"neon_color": (100, 50, 180), "accent_color": (200, 100, 255), "trail_color": (100, 50, 180), "ability": "dual_core"} },
    "prism": { "name": "棱镜分光", "desc": "分裂射击型，一发三道散射", "hp": 155, "speed": 4.2, "damage": 14, "delay": 175, "color": (100, 180, 255), "ult_name": "光谱爆裂", "ult_color": (0, 255, 200), "bullet_type": "prism", "visual": {"neon_color": (0, 255, 200), "accent_color": (100, 200, 255), "trail_color": (100, 180, 255), "ability": "split_fire"} },
    "necro": { "name": "死灵骑士", "desc": "吸血型战机，伤害转化为治疗", "hp": 170, "speed": 3.6, "damage": 17, "delay": 175, "color": (150, 50, 100), "ult_name": "亡灵收割", "ult_color": (200, 50, 150), "bullet_type": "spectral", "visual": {"neon_color": (200, 50, 150), "accent_color": (100, 0, 100), "trail_color": (150, 50, 100), "ability": "lifesteal"} },
    "wormhole": { "name": "混沌虫洞", "desc": "虫洞传送型，子弹从敌人背后虫洞出现", "hp": 145, "speed": 4.8, "damage": 16, "delay": 175, "color": (180, 0, 255), "ult_name": "维度坍缩", "ult_color": (255, 0, 255), "bullet_type": "wormhole", "visual": {"neon_color": (180, 0, 255), "accent_color": (0, 255, 180), "trail_color": (120, 0, 200), "ability": "dimension_rift"} },
    "chronos": { "name": "永恒时计·卡珊德拉", "desc": "掌控时空之力，三相大招操纵过去现在未来", "hp": 145, "speed": 4.4, "damage": 20, "delay": 180, "color": (100, 220, 255), "ult_name": "时空三相", "ult_color": (0, 200, 255), "bullet_type": "chrono", "visual": {"neon_color": (100, 220, 255), "accent_color": (255, 200, 100), "trail_color": (50, 180, 255), "ability": "time_trinity"} },
    "mirage": { "name": "幻镜·万华", "desc": "召唤镜像分身协同作战，分身复制攻击形成弹幕矩阵", "hp": 145, "speed": 4.6, "damage": 15, "delay": 165, "color": (200, 150, 255), "ult_name": "无限镜界", "ult_color": (220, 180, 255), "bullet_type": "mirror", "visual": {"neon_color": (200, 150, 255), "accent_color": (255, 200, 255), "trail_color": (180, 120, 255), "ability": "mirror_dance"} },
    "gambit": { "name": "命运赌徒·艾斯", "desc": "每次攻击随机触发效果，暴击连锁可一发清屏", "hp": 155, "speed": 4.4, "damage": 18, "delay": 180, "color": (255, 215, 0), "ult_name": "命运轮盘", "ult_color": (255, 200, 50), "bullet_type": "card", "visual": {"neon_color": (255, 215, 0), "accent_color": (255, 50, 50), "trail_color": (255, 180, 0), "ability": "fortune_wheel"} },
    "puppeteer": { "name": "牵线木偶师·玛丽奥", "desc": "操控敌人的傀儡师，命中敌人叠加傀儡标记，满层后控制敌人为你作战", "hp": 150, "speed": 4.2, "damage": 16, "delay": 170, "color": (180, 100, 150), "ult_name": "傀儡剧场", "ult_color": (220, 120, 180), "bullet_type": "puppet_string", "visual": {"neon_color": (180, 100, 150), "accent_color": (255, 200, 100), "trail_color": (150, 80, 120), "ability": "puppet_master"} },
    "pandemic": { "name": "末日瘟神·零号", "desc": "病毒传播者，感染在敌群中连锁传播并变异进化，敌人越多越强", "hp": 150, "speed": 4.0, "damage": 15, "delay": 175, "color": (100, 200, 80), "ult_name": "终末审判", "ult_color": (150, 255, 100), "bullet_type": "virus", "visual": {"neon_color": (100, 200, 80), "accent_color": (200, 255, 100), "trail_color": (80, 180, 60), "ability": "plague_spread"} },
    "omega": { "name": "终末神兵·奥米茄", "desc": "融合所有机体精华的终极形态，攻击自动切换七种属性，大招召唤全属性审判", "hp": 180, "speed": 4.8, "damage": 28, "delay": 160, "color": (255, 255, 255), "ult_name": "终焉审判", "ult_color": (255, 220, 255), "bullet_type": "omega_fusion", "visual": {"neon_color": (255, 255, 255), "accent_color": (255, 200, 100), "trail_color": (200, 180, 255), "ability": "omega_fusion"} },
    "genesis": { "name": "创世之翼·起源", "desc": "宇宙原初之力的化身，攻击创造与毁灭并存，大招重塑战场引发宇宙大爆炸", "hp": 170, "speed": 5.0, "damage": 25, "delay": 150, "color": (255, 200, 100), "ult_name": "创世纪元", "ult_color": (255, 230, 150), "bullet_type": "genesis_star", "visual": {"neon_color": (255, 200, 100), "accent_color": (255, 100, 200), "trail_color": (255, 180, 80), "ability": "creation_destruction"} },
    "truth": { "name": "至尊·世界的真相", "desc": "洞察万物本质的终极存在，攻击揭示敌人弱点，真言之眼看穿一切虚假，三大神谕重塑现实", "hp": 190, "speed": 4.6, "damage": 30, "delay": 165, "color": (255, 255, 255), "ult_name": "真理显现", "ult_color": (255, 215, 0), "bullet_type": "truth_revelation", "visual": {"neon_color": (255, 255, 255), "accent_color": (255, 215, 0), "trail_color": (200, 200, 200), "ability": "eye_of_truth"} },
    "asura": { "name": "修罗·斩龙者", "desc": "六臂战神的化身，剑气纵横斩尽苍穹，三道剑气轮斩敌群", "hp": 155, "speed": 5.0, "damage": 28, "delay": 150, "color": (180, 50, 50), "ult_name": "修罗斩", "ult_color": (255, 80, 80), "bullet_type": "sword_slash", "visual": {"neon_color": (180, 50, 50), "accent_color": (255, 100, 60), "trail_color": (200, 80, 80), "ability": "asura_rage"} },
    "dragoon": { "name": "龙骑士·雷因哈特", "desc": "古代龙骑士团的最后传承者，枪气连刺变化多端", "hp": 175, "speed": 4.6, "damage": 32, "delay": 175, "color": (100, 150, 220), "ult_name": "天龙突刺", "ult_color": (120, 180, 255), "bullet_type": "lance_thrust", "visual": {"neon_color": (100, 150, 220), "accent_color": (200, 220, 255), "trail_color": (80, 130, 200), "ability": "dragon_charge"} },
    "origami": { "name": "折纸鹤·零式", "desc": "千羽化形的和平使者，12枚钛刃扇形散射三段弹射，召唤纸鹤群协同作战，折跃复活守护全队", "hp": 140, "speed": 5.2, "damage": 16, "delay": 145, "color": (245, 245, 250), "ult_name": "纸鹤群", "ult_color": (255, 255, 255), "bullet_type": "origami_blade", "visual": {"neon_color": (245, 245, 250), "accent_color": (255, 100, 200), "trail_color": (200, 220, 255), "ability": "fold_revival"} },
    "helios": { "name": "星渊火陨·赫利俄斯", "desc": "超远程AOE轰炸，抛物线火雨弹落地分裂燃烧区，流星群覆盖全场", "hp": 160, "speed": 3.8, "damage": 28, "delay": 900, "color": (255, 100, 20), "ult_name": "流星群", "ult_color": (255, 80, 0), "bullet_type": "meteor", "visual": {"neon_color": (255, 100, 20), "accent_color": (30, 20, 40), "trail_color": (255, 150, 50), "ability": "meteor_shower"} },
    "frostflare": { "name": "极昼寒界·霜曜", "desc": "远程直线冻结，极寒激光穿透2次并减速，命中3次冻结目标2秒", "hp": 150, "speed": 4.0, "damage": 22, "delay": 400, "color": (100, 200, 255), "ult_name": "零度射线", "ult_color": (150, 220, 255), "bullet_type": "frost_laser", "visual": {"neon_color": (100, 200, 255), "accent_color": (220, 240, 255), "trail_color": (150, 220, 255), "ability": "zero_degree"} },
    "nova": { "name": "苍穹轨断·诺娃", "desc": "超远程单点狙击，电磁轨道弹无衰减贯穿全屏，蓄力1秒可穿盾暴击", "hp": 145, "speed": 3.6, "damage": 70, "delay": 1200, "color": (200, 220, 255), "ult_name": "充能击穿", "ult_color": (100, 150, 255), "bullet_type": "railgun", "visual": {"neon_color": (200, 220, 255), "accent_color": (50, 100, 200), "trail_color": (150, 180, 255), "ability": "charge_pierce"} },
    "spectrum": { "name": "天幕虹裂·光谱", "desc": "远程扇形覆盖，7道彩虹光束并行，3道同点命中额外真伤", "hp": 155, "speed": 4.4, "damage": 15, "delay": 180, "color": (200, 200, 220), "ult_name": "光谱叠加", "ult_color": (255, 200, 255), "bullet_type": "rainbow_beam", "visual": {"neon_color": (200, 200, 220), "accent_color": (255, 100, 200), "trail_color": (180, 180, 200), "ability": "spectrum_stack"} },
    "darkstring": { "name": "幽影穿心·冥弦", "desc": "远程标记狙杀，亚音速标记弹可二次暴击，标记3秒内穿墙必暴", "hp": 145, "speed": 4.6, "damage": 65, "delay": 1100, "color": (40, 40, 50), "ult_name": "绝杀狙击", "ult_color": (255, 50, 50), "bullet_type": "mark_shot", "visual": {"neon_color": (40, 40, 50), "accent_color": (255, 50, 50), "trail_color": (80, 80, 100), "ability": "deathmark"} },
    "thornvine": { "name": "棘刺藤骨·荆穹", "desc": "远程骨蔓鞭射，命中后缠绕目标2s持续抽打，受击5次藤骨断裂生成次级短鞭追踪攻击", "hp": 165, "speed": 3.8, "damage": 19, "delay": 600, "color": (240, 240, 230), "ult_charge_rate": 2.5, "ult_name": "骨蔓分裂", "ult_color": (180, 50, 50), "bullet_type": "bone_whip", "visual": {"neon_color": (240, 240, 230), "accent_color": (180, 50, 50), "trail_color": (200, 180, 160), "ability": "vine_split"} },
    "starblade": { "name": "浮游刃环·星镰", "desc": "远程巡航环刃，飞出后悬停水平往返扫割，可召回瞬间加速暴击×1.8", "hp": 150, "speed": 4.3, "damage": 24, "delay": 500, "color": (200, 210, 230), "ult_charge_rate": 2.0, "ult_name": "回环暴击", "ult_color": (100, 180, 255), "bullet_type": "ring_blade", "visual": {"neon_color": (200, 210, 230), "accent_color": (100, 180, 255), "trail_color": (150, 180, 220), "ability": "blade_recall"} },
    "acidswamp": { "name": "酸蚀喷溅·腐沼", "desc": "远程抛物酸囊，落地碎裂6股酸液溅射寻敌附着DOT，3股命中同目标合成酸沼池", "hp": 160, "speed": 4.0, "damage": 18, "delay": 450, "color": (150, 255, 80), "ult_charge_rate": 2.5, "ult_name": "酸液汇合", "ult_color": (100, 200, 50), "bullet_type": "acid_blob", "visual": {"neon_color": (150, 255, 80), "accent_color": (50, 50, 30), "trail_color": (120, 200, 60), "ability": "acid_merge"} },
    "crystalfall": { "name": "晶簇射流·晶瀑", "desc": "远程晶簇扇喷，箭矢落地竖立成晶柱持续穿刺，2柱间距<200px自动连接成水晶墙", "hp": 155, "speed": 4.2, "damage": 20, "delay": 400, "color": (180, 120, 220), "ult_charge_rate": 2.0, "ult_name": "晶簇连锁", "ult_color": (200, 150, 255), "bullet_type": "crystal_arrow", "visual": {"neon_color": (180, 120, 220), "accent_color": (100, 150, 180), "trail_color": (160, 100, 200), "ability": "crystal_link"} },
    "sporeveil": { "name": "孢子幕炮·菌幕", "desc": "远程孢子幕覆盖，炮弹最高点炸开成伞状孢子云持续DOT降命中，累计伤害生成子孢子链式传播", "hp": 165, "speed": 3.9, "damage": 17, "delay": 550, "color": (100, 180, 100), "ult_charge_rate": 2.5, "ult_name": "孢子繁殖", "ult_color": (150, 220, 150), "bullet_type": "spore_shell", "visual": {"neon_color": (100, 180, 100), "accent_color": (240, 250, 240), "trail_color": (80, 150, 80), "ability": "spore_chain"} },
    "cthulhu": { "name": "月蚀星骸·克苏鲁", "desc": "月虹激光贯穿全屏，命中后生成月眼二段真伤，叠加蚀印触发月蚀削弱和星骸剥离", "hp": 190, "speed": 4.6, "damage": 32, "delay": 180, "color": (100, 80, 180), "ult_name": "月蚀降临", "ult_color": (150, 120, 220), "bullet_type": "moon_laser", "visual": {"neon_color": (100, 150, 220), "accent_color": (160, 100, 200), "trail_color": (130, 130, 200), "ability": "eclipse_mark"} },
    "turu": { "name": "巨石核拳·图鲁", "desc": "远程岩核飞拳穿透2次，命中爆裂AOE；巨石充能满格可卸甲强化", "hp": 200, "speed": 3.8, "damage": 35, "delay": 600, "color": (120, 115, 110), "ult_name": "岩拳暴雨", "ult_color": (255, 120, 40), "bullet_type": "rock_fist", "visual": {"neon_color": (255, 120, 40), "accent_color": (120, 115, 110), "trail_color": (180, 100, 30), "ability": "rock_charge"} },
    "staradia": { "name": "辉耀天女·斯塔德", "desc": "虹幕连闪，月虹光梭命中展开辉耀残痕光板，再次普攻激活发射真伤皇辉束；5层升格展开皇辉领域", "hp": 170, "speed": 4.8, "damage": 35, "delay": 140, "color": (255, 180, 220), "ult_name": "皇辉暴雨", "ult_color": (255, 215, 120), "bullet_type": "moon_shuttle", "visual": {"neon_color": (255, 180, 220), "accent_color": (255, 215, 120), "trail_color": (255, 200, 230), "ability": "radiant_ascension"} },
    "dukefishron": { "name": "深渊龙鱼·猪公爵", "desc": "鲨龙卷横扫深渊，水矛命中生成龙卷吸扯+小鲨追踪，再次普攻激活爆炸掉落深渊泡回能", "hp": 185, "speed": 4.6, "damage": 28, "delay": 150, "color": (30, 80, 180), "ult_name": "龙鱼海啸", "ult_color": (255, 120, 180), "bullet_type": "abyss_spear", "visual": {"neon_color": (30, 80, 180), "accent_color": (255, 120, 180), "trail_color": (50, 100, 200), "ability": "shark_tornado"} },
    "slime": { "name": "末世星凝·史莱姆", "desc": "零瞬移漂浮战机，1.4屏超远攻击范围，重力域链式吸附+星凝减益叠层+凝胶子核追踪弹幕", "hp": 180, "speed": 4.4, "damage": 28, "delay": 160, "color": (120, 80, 200), "ult_name": "星陨踩踏", "ult_color": (60, 140, 220), "bullet_type": "star_gel", "visual": {"neon_color": (120, 80, 200), "accent_color": (60, 140, 220), "trail_color": (100, 120, 210), "ability": "gravity_chain"}, "skills": {"skill1": {"name": "星陨踩踏", "desc": "跳跃蓄力后向下重踩，落地时360°散射星炎激光，致命冲击波扩散"}, "skill2": {"name": "星炎水晶", "desc": "部署6颗延迟追踪星炎水晶，短暂悬停后追踪敌人造成高伤害"}, "skill3": {"name": "星凝子体", "desc": "召唤3只自主追踪的星凝子体，接触敌人时自爆造成范围伤害"}} },
    "oro": { "name": "终噬星链·奥罗", "desc": "神明吞噬者零瞬移完全体，1.6屏千节链生长+激光栅十字轰炸+黑洞终噬三维打击", "hp": 200, "speed": 4.4, "damage": 32, "delay": 140, "color": (80, 20, 120), "ult_name": "终噬降临", "ult_color": (200, 50, 80), "bullet_type": "void_chain", "visual": {"neon_color": (80, 20, 120), "accent_color": (200, 50, 80), "trail_color": (120, 40, 160), "ability": "chain_devour"}, "skills": {"skill1": {"name": "千节连生·终噬开幕", "desc": "2s内连续9道链段，每道立即生长至5节形成千节墙，结束后同步爆炸"}, "skill2": {"name": "激光栅风暴·终噬栅灭", "desc": "所有链节4s持续释放十字激光栅，结束时超大范围真伤爆炸"}, "skill3": {"name": "终噬黑洞·终噬闭幕", "desc": "悬浮升空后终噬核心坠地，生成超大黑洞5s持续吞噬，掉落双倍吞噬核"}} }
}

BOSS_DB = {
    "carrier": { "name": "毁灭者级·虚空母舰", "desc": "虚空舰队的核心旗舰。", "color": RED, "stats": [("装甲", 80), ("毁灭", 60), ("机动", 20)], "visual": {"core_color": RED, "aura": (180, 20, 20), "phase_effect": "drone_spawns"}, "phases":[{"threshold":0.75, "spawn":{"type":"drone","count":2}, "fire_rate_mult":0.9}, {"threshold":0.5, "spawn":{"type":"drone","count":4}, "fire_rate_mult":0.75}, {"threshold":0.25, "spawn":{"type":"chaser","count":4}, "fire_rate_mult":0.6}]},
    "fortress": { "name": "不朽级·钢铁堡垒", "desc": "轨道防御系统的终极形态。", "color": ORANGE, "stats": [("装甲", 100), ("毁灭", 75), ("机动", 5)], "visual": {"core_color": ORANGE, "aura": (120, 70, 40), "phase_effect": "turret_barrage"}, "phases": [{"threshold":0.75, "spawn":{"type":"sniper","count":2}, "fire_rate_mult":0.9, "effect":{"type":"pulse","count":2}}, {"threshold":0.5, "spawn":{"type":"tank","count":1}, "fire_rate_mult":0.7, "effect":{"type":"bloom","count":2}}, {"threshold":0.25, "spawn":{"type":"sniper","count":3}, "fire_rate_mult":0.6}]},
    "assassin": { "name": "幻影级·虚空刺客", "desc": "高机动型精英单位。", "color": MAGENTA, "stats": [("装甲", 40), ("毁灭", 85), ("机动", 100)], "visual": {"core_color": MAGENTA, "aura": (120, 0, 120), "phase_effect": "teleport_dash"}, "phases": [{"threshold":0.6, "effect":{"type":"teleport_dash","intensity":2}, "fire_rate_mult":0.85}, {"threshold":0.3, "effect":{"type":"teleport_dash","intensity":4}, "fire_rate_mult":0.7}]},
    "seraphim": { "name": "审判级·炽天使", "desc": "高阶审判机甲。", "color": GOLD, "stats": [("装甲", 70), ("毁灭", 90), ("机动", 50)], "visual": {"core_color": GOLD, "aura": (220, 180, 100)}, "phases":[{"threshold":0.7, "spawn":{"type":"sniper","count":2}, "effect":{"type":"bloom","count":2}, "fire_rate_mult":0.85}, {"threshold":0.35, "spawn":{"type":"tank","count":1}, "fire_rate_mult":0.6}, {"threshold":0.15, "spawn":{"type":"spike","count":3}, "fire_rate_mult":0.5}]},
    "leviathan": { "name": "深渊巨兽·利维坦", "desc": "生物与机械的扭曲结合体。", "color": DEEP_PURPLE, "stats": [("装甲", 90), ("毁灭", 80), ("机动", 30)], "visual": {"core_color": DEEP_PURPLE, "aura": (120, 30, 200)}, "phases":[{"threshold":0.75, "spawn":{"type":"glitch","count":3}, "effect":{"type":"pulse","count":3}, "fire_rate_mult":0.9}, {"threshold":0.45, "spawn":{"type":"wasp","count":3}, "fire_rate_mult":0.7}]},
    "overlord": { "name": "蜂群主宰·奥伯龙", "desc": "蜂群意识的集合体。", "color": CYAN, "stats": [("装甲", 60), ("毁灭", 50), ("机动", 40)], "visual":{"core_color": CYAN, "aura": (0,180,200)}, "phases":[{"threshold":0.8, "spawn":{"type":"wasp","count":4}, "fire_rate_mult":0.9}, {"threshold":0.5, "spawn":{"type":"wasp","count":7}, "fire_rate_mult":0.75}]},
    "ragnarok": { "name": "终焉机神·诸神黄昏", "desc": "毁灭文明的终极兵器。", "color": CRIMSON, "stats": [("装甲", 95), ("毁灭", 100), ("机动", 10)], "visual": {"core_color": CRIMSON, "aura": (140, 0, 10)}, "phases":[{"threshold":0.7, "spawn":{"type":"tank","count":2}, "fire_rate_mult":0.85}, {"threshold":0.4, "spawn":{"type":"sniper","count":3}, "fire_rate_mult":0.6}, {"threshold":0.2, "spawn":{"type":"ragnarok_core","count":1}, "fire_rate_mult":0.5}]},
    "hydra": { "name": "九头蛇·剧毒领主", "desc": "基因突变的生化噩梦。", "color": NEON_GREEN, "stats": [("装甲", 85), ("毁灭", 70), ("机动", 45)], "visual": {"core_color": NEON_GREEN, "aura": (0,200,0)}, "phases":[{"threshold":0.75, "spawn":{"type":"glitch","count":4}, "effect":{"type":"bloom","count":2}, "fire_rate_mult":0.9}, {"threshold":0.45, "spawn":{"type":"drone","count":6}, "fire_rate_mult":0.7}]},
    "chronos": { "name": "时之主·克洛诺斯", "desc": "神秘的古代遗物守护者。", "color": (100, 150, 255), "stats": [("装甲", 75), ("毁灭", 85), ("机动", 80)], "visual": {"core_color": (100, 150, 255), "aura": (120, 160, 255)}, "phases":[{"threshold":0.7, "effect":{"type":"time_pulse","count":3}, "fire_rate_mult":0.9}, {"threshold":0.4, "effect":{"type":"chronos_burst","count":4}, "fire_rate_mult":0.6}]},
    "gazer": { "name": "深渊凝视者", "desc": "来自维度的观察者。", "color": EYE_RED, "stats": [("装甲", 60), ("毁灭", 95), ("机动", 5)], "visual": {"core_color": EYE_RED, "aura": (200, 0, 0)}, "phases":[{"threshold":0.8, "effect":{"type":"gaze_beams","count":3}, "fire_rate_mult":0.9}, {"threshold":0.45, "effect":{"type":"gaze_pulse","count":6}, "fire_rate_mult":0.6}]},
    "lich": { "name": "赛博巫妖", "desc": "被病毒侵蚀的AI核心。", "color": GHOST_CYAN, "stats": [("装甲", 50), ("毁灭", 80), ("机动", 70)], "visual": {"core_color": GHOST_CYAN, "aura": (180,240,240)}, "phases":[{"threshold":0.75, "spawn":{"type":"glitch","count":6}, "effect":{"type":"curse_pulse","count":3}, "fire_rate_mult":0.9}, {"threshold":0.45, "spawn":{"type":"glitch","count":8}, "fire_rate_mult":0.6}]},
    "tempest": { "name": "风暴引擎", "desc": "失控的气象控制器。", "color": WIND_BLUE, "stats": [("装甲", 85), ("毁灭", 65), ("机动", 60)], "visual": {"core_color": WIND_BLUE, "aura": (140, 200, 255), "phase_effect": "wind_gusts"}, "phases": [{"threshold":0.75, "effect":{"type":"wind_gusts","count":5}}, {"threshold":0.5, "effect":{"type":"storm_burst","count":8, "fire_rate_mult":0.6}}]}
    ,
    "void_golem": {
        "name": "虚空魔像",
        "desc": "机械与虚空能量的融合体，拥有多阶段变形与强力弹幕。",
        "color": (80, 0, 120),
        "stats": [("装甲", 120), ("毁灭", 90), ("机动", 35)],
        "visual": {"core_color": (80, 0, 120), "aura": (120, 0, 180), "phase_effect": "gear_energy"},
        "phases": [
            {"threshold": 0.8, "spawn": {"type": "drone", "count": 3}, "effect": {"type": "gear_spin", "count": 4}, "fire_rate_mult": 0.85},
            {"threshold": 0.55, "effect": {"type": "energy_wave", "count": 2}, "fire_rate_mult": 0.7},
            {"threshold": 0.3, "spawn": {"type": "chaser", "count": 5}, "effect": {"type": "core_burst", "count": 3}, "fire_rate_mult": 0.55}
        ]
    },
    "abyss_queen": {
        "name": "星渊女王",
        "desc": "星空与深渊的主宰，能召唤星体与释放星爆弹幕。",
        "color": (120, 60, 200),
        "stats": [("装甲", 100), ("毁灭", 110), ("机动", 60)],
        "visual": {"core_color": (120, 60, 200), "aura": (180, 80, 255), "phase_effect": "star_dust"},
        "phases": [
            {"threshold": 0.85, "spawn": {"type": "starling", "count": 4}, "effect": {"type": "star_dust", "count": 6}, "fire_rate_mult": 0.9},
            {"threshold": 0.6, "spawn": {"type": "star_guard", "count": 2}, "effect": {"type": "queen_invis", "count": 1}, "fire_rate_mult": 0.7},
            {"threshold": 0.35, "effect": {"type": "star_burst", "count": 3}, "fire_rate_mult": 0.5}
        ]
    }
}
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