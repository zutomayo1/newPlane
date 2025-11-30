"""
涂装自定义系统 - 重写版本
简化实现，提高性能和稳定性
"""
import pygame
import json
import os
import random
import math
from config import *

# ==============================================================================
#   涂装主题配置 - 扩展版本
# ==============================================================================

# 涂装主题定义
PAINT_THEMES = {
    # ========== 默认涂装 ==========
    "default": {
        "name": "原厂配色",
        "desc": "飞机的标准配色方案",
        "cost": 0,
        "trail_style": "normal",
        "category": "default",
        "trail_width": 2,
    },
    
    # ========== 普通品质 (Common) - 基础变色 ==========
    "common_red": {
        "name": "赤红涂装",
        "desc": "经典的红色战机涂装",
        "neon_color": (255, 50, 50),
        "accent_color": (255, 100, 100),
        "trail_color": (255, 0, 0),
        "unlocked": False,
        "cost": 300,
        "trail_style": "normal",
        "particle_count": 8,
        "category": "common",
        "trail_width": 2,
    },
    "common_blue": {
        "name": "深海蓝装",
        "desc": "沉稳的蓝色涂装",
        "neon_color": (50, 100, 255),
        "accent_color": (100, 150, 255),
        "trail_color": (0, 100, 255),
        "unlocked": False,
        "cost": 300,
        "trail_style": "normal",
        "particle_count": 8,
        "category": "common",
        "trail_width": 2,
    },
    "common_green": {
        "name": "森林绿装",
        "desc": "自然的绿色涂装",
        "neon_color": (50, 255, 50),
        "accent_color": (100, 255, 100),
        "trail_color": (0, 200, 0),
        "unlocked": False,
        "cost": 300,
        "trail_style": "normal",
        "particle_count": 8,
        "category": "common",
        "trail_width": 2,
    },
    
    # ========== 稀有品质 (Rare) - 带基础特效 ==========
    "rare_gold": {
        "name": "黄金战机",
        "desc": "闪耀的金色涂装，带有星火特效",
        "neon_color": (255, 215, 0),
        "accent_color": (255, 255, 200),
        "trail_color": (255, 200, 0),
        "unlocked": False,
        "cost": 800,
        "trail_style": "sparkle",
        "particle_count": 15,
        "category": "rare",
        "trail_width": 3,
    },
    "rare_purple": {
        "name": "紫电战机",
        "desc": "神秘的紫色涂装，带有电弧特效",
        "neon_color": (200, 0, 255),
        "accent_color": (255, 100, 255),
        "trail_color": (180, 0, 255),
        "unlocked": False,
        "cost": 800,
        "trail_style": "electric",
        "particle_count": 15,
        "category": "rare",
        "trail_width": 3,
    },
    "rare_cyan": {
        "name": "青光战机",
        "desc": "高科技感的青色涂装，带有等离子特效",
        "neon_color": (0, 255, 255),
        "accent_color": (200, 255, 255),
        "trail_color": (0, 200, 255),
        "unlocked": False,
        "cost": 800,
        "trail_style": "plasma",
        "particle_count": 15,
        "category": "rare",
        "trail_width": 3,
    },
    
    # ========== 史诗品质 (Epic) - 高级特效 ==========
    "epic_magma": {
        "name": "熔岩核心",
        "desc": "炽热的熔岩涂装，散发滚烫热浪",
        "neon_color": (255, 80, 0),
        "accent_color": (255, 150, 0),
        "trail_color": (255, 50, 0),
        "unlocked": False,
        "cost": 1500,
        "trail_style": "magma",
        "particle_count": 20,
        "category": "epic",
        "trail_width": 4,
    },
    "epic_frost": {
        "name": "极地冰霜",
        "desc": "冰冷的冰晶涂装，冰雪环绕",
        "neon_color": (200, 240, 255),
        "accent_color": (220, 255, 255),
        "trail_color": (180, 230, 255),
        "unlocked": False,
        "cost": 1500,
        "trail_style": "ice",
        "particle_count": 20,
        "category": "epic",
        "trail_width": 4,
    },
    "epic_shadow": {
        "name": "暗影幽灵",
        "desc": "幽暗的黑色涂装，阴影缭绕",
        "neon_color": (30, 30, 30),
        "accent_color": (80, 80, 80),
        "trail_color": (50, 50, 50),
        "unlocked": False,
        "cost": 1500,
        "trail_style": "shadow",
        "particle_count": 20,
        "category": "epic",
        "trail_width": 4,
    },
    
    # ========== 传说品质 (Legendary) - 顶级特效 ==========
    "legend_rainbow": {
        "name": "光之棱镜",
        "desc": "折射七彩光芒的梦幻涂装",
        "neon_color": (255, 255, 255),
        "accent_color": (255, 255, 255),
        "trail_color": (255, 255, 255),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "rainbow",
        "particle_count": 30,
        "animated": True,
        "category": "legendary",
        "trail_width": 5,
    },
    "legend_phoenix": {
        "name": "浴火凤凰",
        "desc": "涅槃重生的火焰涂装，凤凰环绕",
        "neon_color": (255, 100, 0),
        "accent_color": (255, 200, 0),
        "trail_color": (255, 150, 0),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "phoenix",
        "particle_count": 35,
        "animated": True,
        "category": "legendary",
        "trail_width": 6,
    },
    "legend_nebula": {
        "name": "星云漫游",
        "desc": "星云与星尘环绕的宇宙涂装",
        "neon_color": (150, 100, 255),
        "accent_color": (200, 150, 255),
        "trail_color": (180, 120, 255),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "galaxy",
        "particle_count": 35,
        "animated": True,
        "category": "legendary",
        "trail_width": 6,
    },
    
    # ========== 专属涂装 - Striker (霓虹突击者) ==========
    "striker_mk2": {
        "name": "突击者MK-II",
        "desc": "强化型突击战机，装甲升级，推进器增强",
        "neon_color": (0, 255, 255),
        "accent_color": (255, 200, 0),
        "trail_color": (0, 220, 255),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "thruster",
        "particle_count": 25,
        "category": "exclusive",
        "trail_width": 4,
        "exclusive_plane": "striker",
        "model_style": "enhanced",
        "animated": True,
    },
    "striker_stealth": {
        "name": "隐形突击",
        "desc": "隐形涂层，雷达不可见，半透明机身",
        "neon_color": (20, 20, 40),
        "accent_color": (80, 80, 120),
        "trail_color": (40, 40, 80),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "smoke",
        "particle_count": 15,
        "category": "exclusive",
        "trail_width": 3,
        "exclusive_plane": "striker",
        "model_style": "stealth",
        "animated": True,
    },
    "striker_overdrive": {
        "name": "超频核心",
        "desc": "能量核心过载，红色警告线条遍布机身",
        "neon_color": (255, 0, 0),
        "accent_color": (255, 255, 0),
        "trail_color": (255, 100, 0),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "flame",
        "particle_count": 30,
        "category": "exclusive",
        "trail_width": 5,
        "exclusive_plane": "striker",
        "model_style": "overdrive",
        "animated": True,
    },
    "striker_quantum": {
        "name": "量子跃迁",
        "desc": "量子态机身，闪烁不定，粒子环绕",
        "neon_color": (200, 255, 255),
        "accent_color": (255, 200, 255),
        "trail_color": (180, 230, 255),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "glitch",
        "particle_count": 28,
        "category": "exclusive",
        "trail_width": 4,
        "exclusive_plane": "striker",
        "model_style": "quantum",
        "animated": True,
    },
    "striker_holy": {
        "name": "圣光战士",
        "desc": "神圣的白金涂装，圣光环绕",
        "neon_color": (255, 255, 200),
        "accent_color": (255, 255, 255),
        "trail_color": (255, 245, 220),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "holy",
        "particle_count": 32,
        "category": "exclusive",
        "trail_width": 5,
        "exclusive_plane": "striker",
        "model_style": "divine",
        "animated": True,
    },
    "striker_dragon": {
        "name": "赤龙之怒",
        "desc": "龙鳞纹理，龙形能量尾迹",
        "neon_color": (200, 0, 0),
        "accent_color": (255, 150, 0),
        "trail_color": (220, 50, 0),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "blood",
        "particle_count": 35,
        "category": "exclusive",
        "trail_width": 6,
        "exclusive_plane": "striker",
        "model_style": "dragon",
        "animated": True,
    },
    "striker_infinity": {
        "name": "无尽锋刃",
        "desc": "能量刀刃形态，机翼化作光刃",
        "neon_color": (100, 255, 255),
        "accent_color": (255, 100, 255),
        "trail_color": (150, 200, 255),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "electric",
        "particle_count": 40,
        "category": "exclusive",
        "trail_width": 6,
        "exclusive_plane": "striker",
        "model_style": "blade",
        "animated": True,
    },
    
    # ========== 专属涂装 - Phantom (虚空幻影) ==========
    "phantom_void": {
        "name": "虚空行者",
        "desc": "融入虚空，机身呈现星空纹理",
        "neon_color": (100, 0, 200),
        "accent_color": (180, 100, 255),
        "trail_color": (120, 50, 180),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "void",
        "particle_count": 25,
        "category": "exclusive",
        "trail_width": 4,
        "exclusive_plane": "phantom",
        "model_style": "void",
        "animated": True,
    },
    "phantom_ghost": {
        "name": "幽灵形态",
        "desc": "半透明机身，鬼影重重",
        "neon_color": (200, 200, 255),
        "accent_color": (220, 220, 255),
        "trail_color": (180, 180, 240),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "ghost",
        "particle_count": 20,
        "category": "exclusive",
        "trail_width": 3,
        "exclusive_plane": "phantom",
        "model_style": "ghost",
        "animated": True,
    },
    "phantom_mirror": {
        "name": "镜像分身",
        "desc": "水晶镜面机身，产生幻影分身",
        "neon_color": (220, 220, 220),
        "accent_color": (255, 255, 255),
        "trail_color": (200, 200, 230),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "sparkle",
        "particle_count": 30,
        "category": "exclusive",
        "trail_width": 4,
        "exclusive_plane": "phantom",
        "model_style": "mirror",
        "animated": True,
    },
    "phantom_nightmare": {
        "name": "噩梦使者",
        "desc": "黑暗扭曲的能量形态，恐怖气息",
        "neon_color": (80, 0, 120),
        "accent_color": (150, 0, 150),
        "trail_color": (100, 0, 140),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "tentacle",
        "particle_count": 28,
        "category": "exclusive",
        "trail_width": 5,
        "exclusive_plane": "phantom",
        "model_style": "nightmare",
        "animated": True,
    },
    "phantom_aurora": {
        "name": "极光幻影",
        "desc": "极光色彩流动的机身，梦幻迷离",
        "neon_color": (100, 255, 200),
        "accent_color": (255, 100, 255),
        "trail_color": (150, 200, 255),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "aurora",
        "particle_count": 32,
        "category": "exclusive",
        "trail_width": 5,
        "exclusive_plane": "phantom",
        "model_style": "aurora",
        "animated": True,
    },
    "phantom_time": {
        "name": "时空漫游",
        "desc": "时间沙漏纹理，时空扭曲特效",
        "neon_color": (200, 180, 255),
        "accent_color": (255, 220, 200),
        "trail_color": (220, 200, 240),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "hourglass",
        "particle_count": 35,
        "category": "exclusive",
        "trail_width": 6,
        "exclusive_plane": "phantom",
        "model_style": "time",
        "animated": True,
    },
    "phantom_matrix": {
        "name": "矩阵黑客",
        "desc": "数字代码构成的机身，绿色矩阵雨",
        "neon_color": (0, 255, 0),
        "accent_color": (100, 255, 100),
        "trail_color": (50, 220, 50),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "matrix",
        "particle_count": 40,
        "category": "exclusive",
        "trail_width": 4,
        "exclusive_plane": "phantom",
        "model_style": "matrix",
        "animated": True,
    },
    
    # ========== 专属涂装 - Titan (钢铁泰坦) ==========
    "titan_fortress": {
        "name": "移动要塞",
        "desc": "超重装甲，炮塔林立，钢铁堡垒",
        "neon_color": (120, 120, 120),
        "accent_color": (180, 180, 180),
        "trail_color": (100, 100, 100),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "smoke",
        "particle_count": 30,
        "category": "exclusive",
        "trail_width": 6,
        "exclusive_plane": "titan",
        "model_style": "fortress",
        "animated": True,
    },
    "titan_nuclear": {
        "name": "核动力泰坦",
        "desc": "核反应堆外露，放射性光芒",
        "neon_color": (0, 255, 100),
        "accent_color": (200, 255, 100),
        "trail_color": (100, 255, 50),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "toxic",
        "particle_count": 28,
        "category": "exclusive",
        "trail_width": 5,
        "exclusive_plane": "titan",
        "model_style": "nuclear",
        "animated": True,
    },
    "titan_volcano": {
        "name": "熔岩巨兽",
        "desc": "岩浆流动的装甲，火山爆发特效",
        "neon_color": (255, 100, 0),
        "accent_color": (255, 200, 0),
        "trail_color": (255, 80, 0),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "magma",
        "particle_count": 35,
        "category": "exclusive",
        "trail_width": 6,
        "exclusive_plane": "titan",
        "model_style": "volcano",
        "animated": True,
    },
    "titan_mech": {
        "name": "机甲战神",
        "desc": "机械关节外露，重型武装",
        "neon_color": (0, 150, 255),
        "accent_color": (255, 150, 0),
        "trail_color": (100, 180, 255),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "thruster",
        "particle_count": 32,
        "category": "exclusive",
        "trail_width": 5,
        "exclusive_plane": "titan",
        "model_style": "mech",
        "animated": True,
    },
    "titan_crystal": {
        "name": "晶簇装甲",
        "desc": "水晶装甲覆盖，折射光芒",
        "neon_color": (150, 220, 255),
        "accent_color": (200, 255, 255),
        "trail_color": (180, 240, 255),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "sparkle",
        "particle_count": 30,
        "category": "exclusive",
        "trail_width": 5,
        "exclusive_plane": "titan",
        "model_style": "crystal",
        "animated": True,
    },
    "titan_demon": {
        "name": "恶魔战车",
        "desc": "地狱火焰与黑暗能量，恶魔之翼",
        "neon_color": (150, 0, 0),
        "accent_color": (100, 0, 0),
        "trail_color": (180, 20, 0),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "blood",
        "particle_count": 35,
        "category": "exclusive",
        "trail_width": 6,
        "exclusive_plane": "titan",
        "model_style": "demon",
        "animated": True,
    },
    "titan_orbital": {
        "name": "轨道轰炸机",
        "desc": "卫星武器系统，轨道打击装置",
        "neon_color": (220, 220, 255),
        "accent_color": (255, 255, 255),
        "trail_color": (200, 200, 255),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "plasma",
        "particle_count": 40,
        "category": "exclusive",
        "trail_width": 7,
        "exclusive_plane": "titan",
        "model_style": "orbital",
        "animated": True,
    },
    
    # ========== 专属涂装 - Thunderbird (雷霆战鹰) ==========
    "thunderbird_storm": {
        "name": "风暴之眼",
        "desc": "乌云环绕，闪电缠绕机身",
        "neon_color": (100, 100, 150),
        "accent_color": (200, 200, 255),
        "trail_color": (120, 120, 180),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "lightning",
        "particle_count": 30,
        "category": "exclusive",
        "trail_width": 4,
        "exclusive_plane": "thunderbird",
        "model_style": "storm",
        "animated": True,
    },
    "thunderbird_tesla": {
        "name": "特斯拉线圈",
        "desc": "电弧发生器外露，高压电流",
        "neon_color": (0, 100, 255),
        "accent_color": (100, 200, 255),
        "trail_color": (50, 150, 255),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "electric",
        "particle_count": 35,
        "category": "exclusive",
        "trail_width": 3,
        "exclusive_plane": "thunderbird",
        "model_style": "tesla",
        "animated": True,
    },
    "thunderbird_plasma": {
        "name": "等离子羽翼",
        "desc": "等离子能量形态的机翼",
        "neon_color": (255, 150, 255),
        "accent_color": (255, 200, 255),
        "trail_color": (230, 170, 255),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "plasma",
        "particle_count": 32,
        "category": "exclusive",
        "trail_width": 5,
        "exclusive_plane": "thunderbird",
        "model_style": "plasma",
        "animated": True,
    },
    "thunderbird_aurora": {
        "name": "极光战鹰",
        "desc": "极光色彩的能量羽翼，光带飘扬",
        "neon_color": (0, 255, 150),
        "accent_color": (100, 255, 200),
        "trail_color": (50, 240, 180),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "aurora",
        "particle_count": 28,
        "category": "exclusive",
        "trail_width": 4,
        "exclusive_plane": "thunderbird",
        "model_style": "aurora_bird",
        "animated": True,
    },
    "thunderbird_valkyrie": {
        "name": "女武神",
        "desc": "神话战士形态，圣光之翼",
        "neon_color": (255, 245, 220),
        "accent_color": (255, 255, 255),
        "trail_color": (255, 250, 230),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "holy",
        "particle_count": 35,
        "category": "exclusive",
        "trail_width": 5,
        "exclusive_plane": "thunderbird",
        "model_style": "valkyrie",
        "animated": True,
    },
    "thunderbird_phoenix": {
        "name": "雷电凤凰",
        "desc": "凤凰形态，雷火交织",
        "neon_color": (255, 200, 0),
        "accent_color": (255, 255, 100),
        "trail_color": (255, 220, 50),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "phoenix",
        "particle_count": 40,
        "category": "exclusive",
        "trail_width": 6,
        "exclusive_plane": "thunderbird",
        "model_style": "phoenix",
        "animated": True,
    },
    "thunderbird_cosmic": {
        "name": "宇宙雷神",
        "desc": "星空能量羽翼，宇宙风暴",
        "neon_color": (150, 100, 255),
        "accent_color": (200, 150, 255),
        "trail_color": (180, 120, 255),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "galaxy",
        "particle_count": 45,
        "category": "exclusive",
        "trail_width": 6,
        "exclusive_plane": "thunderbird",
        "model_style": "cosmic",
        "animated": True,
    },
    
    # ========== 专属涂装 - Viper (剧毒蝰蛇) ==========
    "viper_cobra": {
        "name": "眼镜蛇王",
        "desc": "蛇鳞纹理，毒液滴落",
        "neon_color": (100, 255, 0),
        "accent_color": (150, 255, 50),
        "trail_color": (120, 240, 20),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "toxic",
        "particle_count": 25,
        "category": "exclusive",
        "trail_width": 4,
        "exclusive_plane": "viper",
        "model_style": "cobra",
        "animated": True,
    },
    "viper_acid": {
        "name": "强酸溶解",
        "desc": "腐蚀性酸液覆盖，冒着毒烟",
        "neon_color": (200, 255, 0),
        "accent_color": (255, 255, 100),
        "trail_color": (220, 255, 50),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "bubble",
        "particle_count": 30,
        "category": "exclusive",
        "trail_width": 4,
        "exclusive_plane": "viper",
        "model_style": "acid",
        "animated": True,
    },
    "viper_bio": {
        "name": "生化兵器",
        "desc": "生物组织与机械融合，活体机身",
        "neon_color": (0, 200, 100),
        "accent_color": (100, 255, 150),
        "trail_color": (50, 220, 120),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "tentacle",
        "particle_count": 28,
        "category": "exclusive",
        "trail_width": 5,
        "exclusive_plane": "viper",
        "model_style": "bio",
        "animated": True,
    },
    "viper_plasma": {
        "name": "等离子毒素",
        "desc": "紫色等离子毒雾，剧毒能量",
        "neon_color": (200, 0, 255),
        "accent_color": (255, 100, 255),
        "trail_color": (220, 50, 255),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "plasma",
        "particle_count": 32,
        "category": "exclusive",
        "trail_width": 5,
        "exclusive_plane": "viper",
        "model_style": "plasma_viper",
        "animated": True,
    },
    "viper_hydra": {
        "name": "九头蛇",
        "desc": "多头蛇形态，蛇头装饰",
        "neon_color": (0, 150, 50),
        "accent_color": (100, 200, 100),
        "trail_color": (50, 180, 80),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "toxic",
        "particle_count": 35,
        "category": "exclusive",
        "trail_width": 6,
        "exclusive_plane": "viper",
        "model_style": "hydra",
        "animated": True,
    },
    "viper_neon": {
        "name": "霓虹毒蛇",
        "desc": "荧光绿涂装，放射性毒素",
        "neon_color": (0, 255, 0),
        "accent_color": (100, 255, 0),
        "trail_color": (50, 255, 0),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "toxic",
        "particle_count": 38,
        "category": "exclusive",
        "trail_width": 5,
        "exclusive_plane": "viper",
        "model_style": "neon",
        "animated": True,
    },
    "viper_serpent_god": {
        "name": "蛇神降临",
        "desc": "古老蛇神的化身，神话图腾",
        "neon_color": (255, 215, 0),
        "accent_color": (255, 255, 100),
        "trail_color": (255, 230, 50),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "holy",
        "particle_count": 40,
        "category": "exclusive",
        "trail_width": 6,
        "exclusive_plane": "viper",
        "model_style": "serpent_god",
        "animated": True,
    },
    
    # ========== 专属涂装 - Specter (幽灵收割者) ==========
    "specter_reaper": {
        "name": "死神之镰",
        "desc": "镰刀形态机翼，死神黑袍",
        "neon_color": (100, 0, 150),
        "accent_color": (180, 100, 200),
        "trail_color": (120, 50, 180),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "ghost",
        "particle_count": 25,
        "category": "exclusive",
        "trail_width": 4,
        "exclusive_plane": "specter",
        "model_style": "reaper",
        "animated": True,
    },
    "specter_assassin": {
        "name": "暗影刺客",
        "desc": "忍者形态，暗器装饰",
        "neon_color": (50, 50, 80),
        "accent_color": (100, 100, 150),
        "trail_color": (70, 70, 120),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "shadow",
        "particle_count": 20,
        "category": "exclusive",
        "trail_width": 3,
        "exclusive_plane": "specter",
        "model_style": "assassin",
        "animated": True,
    },
    "specter_wraith": {
        "name": "幽冥怨灵",
        "desc": "怨灵形态，灵魂锁链",
        "neon_color": (150, 255, 255),
        "accent_color": (200, 255, 255),
        "trail_color": (180, 255, 255),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "ghost",
        "particle_count": 28,
        "category": "exclusive",
        "trail_width": 4,
        "exclusive_plane": "specter",
        "model_style": "wraith",
        "animated": True,
    },
    "specter_sniper": {
        "name": "鹰眼狙击",
        "desc": "狙击镜装饰，超长枪管",
        "neon_color": (0, 150, 255),
        "accent_color": (100, 200, 255),
        "trail_color": (50, 180, 255),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "electric",
        "particle_count": 22,
        "category": "exclusive",
        "trail_width": 2,
        "exclusive_plane": "specter",
        "model_style": "sniper",
        "animated": True,
    },
    "specter_poltergeist": {
        "name": "骚灵现象",
        "desc": "混乱能量，物体漂浮",
        "neon_color": (200, 100, 255),
        "accent_color": (255, 150, 255),
        "trail_color": (220, 120, 255),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "ghost",
        "particle_count": 30,
        "category": "exclusive",
        "trail_width": 5,
        "exclusive_plane": "specter",
        "model_style": "poltergeist",
        "animated": True,
    },
    "specter_angel": {
        "name": "堕落天使",
        "desc": "黑色天使翅膀，神圣堕落",
        "neon_color": (30, 30, 50),
        "accent_color": (200, 200, 255),
        "trail_color": (100, 100, 180),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "shadow",
        "particle_count": 35,
        "category": "exclusive",
        "trail_width": 6,
        "exclusive_plane": "specter",
        "model_style": "fallen_angel",
        "animated": True,
    },
    "specter_void_hunter": {
        "name": "虚空猎手",
        "desc": "异次元生物形态，虚空触手",
        "neon_color": (80, 0, 120),
        "accent_color": (150, 50, 180),
        "trail_color": (100, 20, 150),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "tentacle",
        "particle_count": 40,
        "category": "exclusive",
        "trail_width": 6,
        "exclusive_plane": "specter",
        "model_style": "void_hunter",
        "animated": True,
    },
    
    # ========== 专属涂装 - Aurora (极光女神) ==========
    "aurora_goddess": {
        "name": "深海蔚蓝",
        "desc": "深邃海洋的神秘蓝色",
        "neon_color": (0, 50, 255),
        "accent_color": (100, 150, 255),
        "trail_color": (50, 100, 255),
        "unlocked": False,
        "cost": 500,
        "trail_style": "water",
        "particle_count": 12,
        "category": "classic",
        "trail_width": 3,
    },
    "classic_gold": {
        "name": "辉煌金装",
        "desc": "闪耀着财富光芒的黄金涂装",
        "neon_color": (255, 215, 0),
        "accent_color": (255, 255, 220),
        "trail_color": (255, 200, 0),
        "unlocked": False,
        "cost": 800,
        "trail_style": "sparkle",
        "particle_count": 20,
        "category": "classic",
        "trail_width": 3,
    },
    
    # --- 霓虹系列 (高饱和度，发光感) ---
    "neon_purple": {
        "name": "赛博紫电",
        "desc": "夜之城的霓虹脉冲",
        "neon_color": (220, 0, 255),
        "accent_color": (255, 100, 255),
        "trail_color": (200, 0, 255),
        "unlocked": False,
        "cost": 1000,
        "trail_style": "electric",
        "particle_count": 18,
        "category": "neon",
        "trail_width": 2,
    },
    "neon_cyan": {
        "name": "量子青光",
        "desc": "高能粒子流的青色辉光",
        "neon_color": (0, 255, 255),
        "accent_color": (200, 255, 255),
        "trail_color": (0, 200, 255),
        "unlocked": False,
        "cost": 1000,
        "trail_style": "plasma",
        "particle_count": 20,
        "category": "neon",
        "trail_width": 4,
    },
    "neon_lime": {
        "name": "生化荧光",
        "desc": "极度危险的放射性绿色",
        "neon_color": (50, 255, 0),
        "accent_color": (150, 255, 100),
        "trail_color": (100, 255, 0),
        "unlocked": False,
        "cost": 1000,
        "trail_style": "toxic",
        "particle_count": 15,
        "category": "neon",
        "trail_width": 3,
    },

    # --- 史诗系列 (独特质感) ---
    "stealth_black": {
        "name": "幽灵行动",
        "desc": "几乎无法被雷达侦测的隐形涂装",
        "neon_color": (20, 20, 20),
        "accent_color": (60, 60, 60),
        "trail_color": (40, 40, 40),
        "unlocked": False,
        "cost": 1500,
        "trail_style": "smoke",
        "particle_count": 10,
        "category": "epic",
        "trail_width": 4,
    },
    "midnight_phantom": {
        "name": "午夜幻影",
        "desc": "如黑夜中的魅影般穿梭",
        "neon_color": (0, 0, 50),
        "accent_color": (20, 20, 80),
        "trail_color": (10, 10, 60),
        "unlocked": False,
        "cost": 1800,
        "trail_style": "shadow",
        "particle_count": 12,
        "category": "epic",
        "trail_width": 4,
    },
    "magma_core": {
        "name": "熔岩核心",
        "desc": "地心深处的毁灭性热能",
        "neon_color": (255, 50, 0),
        "accent_color": (100, 20, 0),
        "trail_color": (200, 40, 0),
        "unlocked": False,
        "cost": 1800,
        "trail_style": "magma",
        "particle_count": 18,
        "category": "epic",
        "trail_width": 5,
    },
    "crystal_white": {
        "name": "极地冰霜",
        "desc": "由永恒之冰打造的晶体装甲",
        "neon_color": (240, 255, 255),
        "accent_color": (200, 255, 255),
        "trail_color": (220, 255, 255),
        "unlocked": False,
        "cost": 1200,
        "trail_style": "ice",
        "particle_count": 15,
        "category": "epic",
        "trail_width": 2,
    },
    "rainbow_spectrum": {
        "name": "光之棱镜",
        "desc": "折射出所有可见光的梦幻涂装",
        "neon_color": (255, 255, 255),
        "accent_color": (255, 255, 255),
        "trail_color": (255, 255, 255),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "rainbow",
        "particle_count": 25,
        "animated": True,
        "category": "epic",
        "trail_width": 5,
    },
    "aurora_borealis": {
        "name": "极光之夜",
        "desc": "绚丽的极光在机翼上流淌",
        "neon_color": (0, 255, 128),
        "accent_color": (100, 0, 255),
        "trail_color": (50, 200, 150),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "aurora",
        "particle_count": 20,
        "category": "epic",
        "trail_width": 4,
    },
    "vampire_lord": {
        "name": "鲜血领主",
        "desc": "渴望鲜血的暗夜贵族",
        "neon_color": (180, 0, 0),
        "accent_color": (50, 0, 0),
        "trail_color": (150, 0, 0),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "blood",
        "particle_count": 15,
        "category": "epic",
        "trail_width": 3,
    },
    
    # --- 特效系列 (强烈的视觉风格) ---
    "vapor_wave": {
        "name": "蒸汽波",
        "desc": "A E S T H E T I C",
        "neon_color": (255, 105, 180),
        "accent_color": (0, 255, 255),
        "trail_color": (255, 0, 255),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "retro",
        "particle_count": 15,
        "category": "special",
        "trail_width": 3,
    },
    "bubble_pop": {
        "name": "糖果泡泡",
        "desc": "甜蜜而致命的粉色气泡",
        "neon_color": (255, 105, 180),
        "accent_color": (255, 182, 193),
        "trail_color": (255, 105, 180),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "bubble",
        "particle_count": 22,
        "category": "special",
        "trail_width": 3,
    },
    "pixel_retro": {
        "name": "8-Bit 勇者",
        "desc": "像素世界的复古情怀",
        "neon_color": (255, 165, 0),
        "accent_color": (255, 215, 0),
        "trail_color": (255, 140, 0),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "pixel",
        "particle_count": 16,
        "category": "special",
        "trail_width": 4,
    },
    "matrix_code": {
        "name": "黑客帝国",
        "desc": "数据流构成的虚拟实体",
        "neon_color": (0, 255, 0),
        "accent_color": (50, 255, 50),
        "trail_color": (0, 200, 0),
        "unlocked": False,
        "cost": 2500,
        "trail_style": "matrix",
        "particle_count": 25,
        "category": "special",
        "trail_width": 2,
    },
    "sakura_fall": {
        "name": "千本樱",
        "desc": "漫天飞舞的樱花雨",
        "neon_color": (255, 192, 203),
        "accent_color": (255, 240, 245),
        "trail_color": (255, 180, 190),
        "unlocked": False,
        "cost": 2500,
        "trail_style": "sakura",
        "particle_count": 20,
        "category": "special",
        "trail_width": 3,
    },
    "cyber_glitch": {
        "name": "系统崩溃",
        "desc": "E̶R̶R̶O̶R̶... 致命错误",
        "neon_color": (255, 0, 255),
        "accent_color": (0, 255, 255),
        "trail_color": (255, 255, 255),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "glitch",
        "particle_count": 15,
        "category": "special",
        "trail_width": 3,
    },
    "time_traveler": {
        "name": "时之沙",
        "desc": "流逝的时间在指尖滑落",
        "neon_color": (255, 215, 0),
        "accent_color": (192, 192, 192),
        "trail_color": (218, 165, 32),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "hourglass",
        "particle_count": 18,
        "category": "special",
        "trail_width": 2,
    },
    "mecha_warrior": {
        "name": "机甲战神",
        "desc": "重装机甲的推进器火焰",
        "neon_color": (0, 100, 255),
        "accent_color": (255, 100, 0),
        "trail_color": (0, 200, 255),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "thruster",
        "particle_count": 20,
        "category": "special",
        "trail_width": 4,
    },
    "abyssal_watcher": {
        "name": "深渊监视者",
        "desc": "来自深海的不可名状之物",
        "neon_color": (0, 0, 100),
        "accent_color": (100, 0, 150),
        "trail_color": (50, 0, 100),
        "unlocked": False,
        "cost": 2900,
        "trail_style": "tentacle",
        "particle_count": 12,
        "category": "special",
        "trail_width": 5,
    },
    
    # --- 传说系列 (极致奢华) ---
    "thunder_lord": {
        "name": "雷霆领主",
        "desc": "掌控九天雷霆的审判者",
        "neon_color": (100, 100, 255),
        "accent_color": (200, 200, 255),
        "trail_color": (50, 50, 255),
        "unlocked": False,
        "cost": 4000,
        "trail_style": "lightning",
        "particle_count": 25,
        "requirement": "击败5个Boss",
        "category": "legendary",
        "trail_width": 4,
    },
    "cosmic_nebula": {
        "name": "星云漫游",
        "desc": "诞生于垂死恒星的尘埃之中",
        "neon_color": (150, 0, 200),
        "accent_color": (0, 0, 50),
        "trail_color": (100, 0, 150),
        "unlocked": False,
        "cost": 4500,
        "trail_style": "galaxy",
        "particle_count": 35,
        "requirement": "达到30波",
        "category": "legendary",
        "trail_width": 6,
    },
    "phoenix_reborn": {
        "name": "浴火凤凰",
        "desc": "涅槃重生的不死神鸟",
        "neon_color": (255, 50, 0),
        "accent_color": (255, 200, 0),
        "trail_color": (255, 100, 0),
        "unlocked": False,
        "cost": 5500,
        "trail_style": "phoenix",
        "particle_count": 40,
        "requirement": "无伤通关任意Boss",
        "category": "legendary",
        "trail_width": 6,
    },
    "divine_judgement": {
        "name": "神圣审判",
        "desc": "天使降临，净化世间一切罪恶",
        "neon_color": (255, 255, 255),
        "accent_color": (255, 215, 0),
        "trail_color": (255, 255, 200),
        "unlocked": False,
        "cost": 6000,
        "trail_style": "holy",
        "particle_count": 30,
        "requirement": "累计击杀5000敌人",
        "category": "legendary",
        "trail_width": 5,
    },
    "ace_commander": {
        "name": "至尊统帅",
        "desc": "统御战场的无上威严",
        "neon_color": (255, 0, 0),
        "accent_color": (255, 215, 0),
        "trail_color": (255, 50, 50),
        "unlocked": False,
        "cost": 5000,
        "trail_style": "solar", # Changed from crown to solar as crown was not implemented
        "particle_count": 30,
        "requirement": "击败10个Boss",
        "category": "legendary",
        "trail_width": 5,
    },
    "void_darkness": {
        "name": "深渊凝视",
        "desc": "当你凝视深渊时...",
        "neon_color": (50, 0, 100),
        "accent_color": (100, 0, 200),
        "trail_color": (70, 0, 140),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "void",
        "particle_count": 25,
        "requirement": "达到50波",
        "category": "legendary",
        "trail_width": 6,
    },
    "solar_flare": {
        "name": "恒星爆发",
        "desc": "超新星爆发般的毁灭能量",
        "neon_color": (255, 100, 0),
        "accent_color": (255, 255, 0),
        "trail_color": (255, 140, 0),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "solar",
        "particle_count": 30,
        "requirement": "累计造成100000伤害",
        "category": "legendary",
        "trail_width": 5,
    },
}

# ==============================================================================
#   涂装管理器
# ==============================================================================

class CustomizationManager:
    def __init__(self):
        self.save_file = "customization.json"
        self.unlocked_themes = {"default": True}
        self.equipped_themes = {}
        self.load_data()
    
    def load_data(self):
        """从文件加载涂装数据"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.unlocked_themes = data.get("unlocked_themes", {"default": True})
                    self.equipped_themes = data.get("equipped_themes", {})
                    
                    # 清理不存在的主题
                    invalid_unlocked = [tid for tid in self.unlocked_themes if tid not in PAINT_THEMES]
                    invalid_equipped = [pid for pid, tid in self.equipped_themes.items() if tid not in PAINT_THEMES]
                    
                    if invalid_unlocked or invalid_equipped:
                        print(f"清理无效主题: unlocked={invalid_unlocked}, equipped={invalid_equipped}")
                        for tid in invalid_unlocked:
                            del self.unlocked_themes[tid]
                        for pid in invalid_equipped:
                            self.equipped_themes[pid] = "default"
                        self.save_data()  # 保存清理后的数据
            except Exception as e:
                print(f"涂装数据加载失败: {e}")
    
    def save_data(self):
        """保存涂装数据到文件"""
        try:
            data = {
                "unlocked_themes": self.unlocked_themes,
                "equipped_themes": self.equipped_themes
            }
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"涂装数据保存失败: {e}")
    
    def unlock_theme(self, theme_id, arsenal_data):
        """解锁涂装"""
        if theme_id in PAINT_THEMES:
            theme = PAINT_THEMES[theme_id]
            cost = theme.get("cost", 0)
            
            if self.unlocked_themes.get(theme_id, False):
                return False, "涂装已解锁"
            
            current_cores = arsenal_data["currencies"]["cores"]
            if current_cores < cost:
                return False, f"核心不足，需要 {cost}，当前 {current_cores}"
            
            arsenal_data["currencies"]["cores"] -= cost
            self.unlocked_themes[theme_id] = True
            self.save_data()
            return True, f"成功解锁 {theme['name']}"
        return False, "涂装不存在"
    
    def equip_theme(self, plane_id, theme_id):
        """为飞机装备涂装"""
        if not self.unlocked_themes.get(theme_id, False):
            return False, "涂装未解锁"
        
        theme = PAINT_THEMES.get(theme_id)
        if theme and "exclusive_plane" in theme:
            if theme["exclusive_plane"] != plane_id:
                return False, f"该涂装仅限 {theme['exclusive_plane']} 使用"

        self.equipped_themes[plane_id] = theme_id
        self.save_data()
        return True, f"涂装已装备"
    
    def get_equipped_theme(self, plane_id):
        """获取飞机当前装备的涂装ID"""
        return self.equipped_themes.get(plane_id, "default")
    
    def get_theme_visual(self, plane_id, default_visual, preview_theme_id=None):
        """获取飞机的涂装视觉数据"""
        if preview_theme_id:
            theme_id = preview_theme_id
        else:
            theme_id = self.get_equipped_theme(plane_id)
            
        theme = PAINT_THEMES.get(theme_id, PAINT_THEMES["default"])
        
        if theme_id == "default":
            return default_visual
        
        if default_visual:
            visual = default_visual.copy()
        else:
            visual = {}
        
        if "neon_color" in theme: visual["neon_color"] = theme["neon_color"]
        if "accent_color" in theme: visual["accent_color"] = theme["accent_color"]
        if "trail_color" in theme: visual["trail_color"] = theme["trail_color"]
        if "model_style" in theme: visual["model_style"] = theme["model_style"]
        
        visual["trail_style"] = theme.get("trail_style", "normal")
        visual["particle_count"] = theme.get("particle_count", 8)
        visual["animated"] = theme.get("animated", False)
        visual["trail_width"] = theme.get("trail_width", 2)
        
        return visual
    
    def get_unlocked_count(self):
        return sum(1 for unlocked in self.unlocked_themes.values() if unlocked)
    
    def get_total_count(self):
        return len(PAINT_THEMES)

# ==============================================================================
#   尾迹效果绘制系统
# ==============================================================================

class EnhancedTrailEffect:
    """增强型尾迹效果"""
    
    @staticmethod
    def draw_trail(surf, trail_positions, visual, alpha_gradient=True):
        """绘制增强尾迹效果"""
        if len(trail_positions) < 2:
            return
        
        trail_style = visual.get("trail_style", "normal")
        trail_color = visual.get("trail_color", CYAN)
        particle_count = visual.get("particle_count", 8)
        width = visual.get("trail_width", 2)
        
        # 根据样式选择绘制方法
        if trail_style == "flame":
            EnhancedTrailEffect._draw_flame_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "electric":
            EnhancedTrailEffect._draw_electric_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "plasma":
            EnhancedTrailEffect._draw_plasma_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "rainbow":
            EnhancedTrailEffect._draw_rainbow_trail(surf, trail_positions, particle_count, width)
        elif trail_style == "sparkle":
            EnhancedTrailEffect._draw_sparkle_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "smoke":
            EnhancedTrailEffect._draw_smoke_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "ice":
            EnhancedTrailEffect._draw_ice_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "void":
            EnhancedTrailEffect._draw_void_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "solar":
            EnhancedTrailEffect._draw_solar_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "matrix":
            EnhancedTrailEffect._draw_matrix_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "sakura":
            EnhancedTrailEffect._draw_sakura_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "glitch":
            EnhancedTrailEffect._draw_glitch_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "pixel":
            EnhancedTrailEffect._draw_pixel_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "bubble":
            EnhancedTrailEffect._draw_bubble_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "toxic":
            EnhancedTrailEffect._draw_toxic_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "galaxy":
            EnhancedTrailEffect._draw_galaxy_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "magma":
            EnhancedTrailEffect._draw_magma_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "lightning":
            EnhancedTrailEffect._draw_lightning_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "shadow":
            EnhancedTrailEffect._draw_shadow_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "retro":
            EnhancedTrailEffect._draw_retro_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "aurora":
            EnhancedTrailEffect._draw_aurora_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "blood":
            EnhancedTrailEffect._draw_blood_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "hourglass":
            EnhancedTrailEffect._draw_hourglass_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "thruster":
            EnhancedTrailEffect._draw_thruster_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "tentacle":
            EnhancedTrailEffect._draw_tentacle_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "phoenix":
            EnhancedTrailEffect._draw_phoenix_trail(surf, trail_positions, trail_color, particle_count, width)
        elif trail_style == "holy":
            EnhancedTrailEffect._draw_holy_trail(surf, trail_positions, trail_color, particle_count, width)
        else:
            EnhancedTrailEffect._draw_normal_trail(surf, trail_positions, trail_color, alpha_gradient, width)
    
    @staticmethod
    def _draw_normal_trail(surf, positions, color, alpha_gradient, width):
        if alpha_gradient:
            for i in range(len(positions) - 1):
                alpha = int(255 * (i + 1) / len(positions))
                temp_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, (*color, alpha), positions[i], positions[i + 1], width)
                surf.blit(temp_surf, (0, 0))
        else:
            pygame.draw.lines(surf, color, False, positions, width)
    
    @staticmethod
    def _draw_flame_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            alpha = int(200 * i / len(positions))
            if alpha < 50: continue
            for _ in range(max(1, count // 3)):
                offset_x = random.randint(int(-5*scale), int(5*scale))
                offset_y = random.randint(int(-5*scale), int(5*scale))
                px, py = pos[0] + offset_x, pos[1] + offset_y
                size = random.randint(int(2*scale), int(4*scale))
                flame_color = (min(255, color[0] + 50), max(0, color[1] - 30), 0)
                pygame.draw.circle(surf, (*flame_color, alpha), (int(px), int(py)), size)
    
    @staticmethod
    def _draw_electric_trail(surf, positions, color, count, width):
        # Electric usually thin, but we can scale jitter
        for i in range(len(positions) - 1):
            if random.random() < 0.3:
                start, end = positions[i], positions[i + 1]
                mid_x = (start[0] + end[0]) // 2 + random.randint(-10, 10)
                mid_y = (start[1] + end[1]) // 2 + random.randint(-10, 10)
                pygame.draw.line(surf, color, start, (mid_x, mid_y), max(1, width // 2))
                pygame.draw.line(surf, color, (mid_x, mid_y), end, max(1, width // 2))
    
    @staticmethod
    def _draw_plasma_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            alpha = int(180 * i / len(positions))
            if alpha < 40: continue
            size = int((3 + (i % 3)) * scale)
            pygame.draw.circle(surf, (*color, alpha), (int(pos[0]), int(pos[1])), size)
            glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, alpha // 3), (size * 2, size * 2), size * 2)
            surf.blit(glow_surf, (int(pos[0]) - size * 2, int(pos[1]) - size * 2))
    
    @staticmethod
    def _draw_rainbow_trail(surf, positions, count, width):
        rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (139, 0, 255)]
        for i in range(len(positions) - 1):
            color_idx = i % len(rainbow_colors)
            color = rainbow_colors[color_idx]
            pygame.draw.line(surf, color, positions[i], positions[i + 1], width)
    
    @staticmethod
    def _draw_sparkle_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            if random.random() < 0.5:
                size = random.randint(1, int(3*scale))
                sparkle_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
                pygame.draw.circle(surf, sparkle_color, (int(pos[0]), int(pos[1])), size)
                if size > 1:
                    pygame.draw.line(surf, sparkle_color, (pos[0] - 3*scale, pos[1]), (pos[0] + 3*scale, pos[1]), 1)
                    pygame.draw.line(surf, sparkle_color, (pos[0], pos[1] - 3*scale), (pos[0], pos[1] + 3*scale), 1)
    
    @staticmethod
    def _draw_smoke_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            alpha = max(30, int(100 * i / len(positions)))
            size = int((4 + (len(positions) - i) // 5) * scale)
            smoke_color = (color[0] // 2, color[1] // 2, color[2] // 2)
            pygame.draw.circle(surf, (*smoke_color, alpha), (int(pos[0]), int(pos[1])), size)
    
    @staticmethod
    def _draw_ice_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            if random.random() < 0.4:
                size = random.randint(int(2*scale), int(4*scale))
                ice_color = (min(255, color[0] + 20), min(255, color[1] + 20), 255)
                points = [(pos[0], pos[1] - size), (pos[0] + size, pos[1]), (pos[0], pos[1] + size), (pos[0] - size, pos[1])]
                pygame.draw.polygon(surf, ice_color, points, 1)
    
    @staticmethod
    def _draw_void_trail(surf, positions, color, count, width):
        for i in range(len(positions) - 1):
            alpha = int(150 * i / len(positions))
            if alpha < 30: continue
            pygame.draw.line(surf, (*color, alpha), positions[i], positions[i + 1], width)
            dark_color = (max(0, color[0] - 40), 0, max(0, color[2] - 40))
            pygame.draw.line(surf, (*dark_color, alpha // 2), positions[i], positions[i + 1], width + 2)
    
    @staticmethod
    def _draw_solar_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            alpha = int(220 * i / len(positions))
            if alpha < 60: continue
            core_size = int(4 * scale)
            pygame.draw.circle(surf, (255, 255, 200, alpha), (int(pos[0]), int(pos[1])), core_size)
            for _ in range(count // 4):
                angle = random.uniform(0, 2 * 3.14159)
                dist = random.randint(int(5*scale), int(12*scale))
                gx = int(pos[0] + dist * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
                gy = int(pos[1] + dist * pygame.math.Vector2(1, 0).rotate_rad(angle).y)
                pygame.draw.circle(surf, (*color, alpha // 2), (gx, gy), max(1, int(2*scale)))

    @staticmethod
    def _draw_matrix_trail(surf, positions, color, count, width):
        """矩阵代码尾迹"""
        scale = width / 2
        for i, pos in enumerate(positions):
            if i % 3 != 0: continue
            alpha = int(255 * i / len(positions))
            # 绘制小的二进制代码块
            size = int(3 * scale)
            rect = pygame.Rect(pos[0], pos[1], size, size*2)
            pygame.draw.rect(surf, (*color, alpha), rect)
            if random.random() < 0.2:
                pygame.draw.rect(surf, (200, 255, 200, alpha), rect.inflate(-1, -1))

    @staticmethod
    def _draw_sakura_trail(surf, positions, color, count, width):
        """樱花尾迹"""
        scale = width / 2
        for i, pos in enumerate(positions):
            if i % 2 != 0: continue
            alpha = int(200 * i / len(positions))
            if alpha < 50: continue
            # 模拟花瓣形状
            size = int(4 * scale)
            offset_x = math.sin(i * 0.5) * 5
            p_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.ellipse(p_surf, (*color, alpha), (0, 0, size*2, size))
            # 旋转花瓣
            rot_surf = pygame.transform.rotate(p_surf, i * 20)
            surf.blit(rot_surf, (pos[0] + offset_x - size, pos[1] - size))

    @staticmethod
    def _draw_glitch_trail(surf, positions, color, count, width):
        """故障尾迹"""
        for i in range(len(positions) - 1):
            alpha = int(200 * i / len(positions))
            start, end = positions[i], positions[i+1]
            # 随机水平偏移
            offset = random.randint(-3, 3) if random.random() < 0.3 else 0
            start = (start[0] + offset, start[1])
            end = (end[0] + offset, end[1])
            
            # 随机颜色偏移 (RGB分离)
            if random.random() < 0.1:
                pygame.draw.line(surf, (255, 0, 0, alpha), (start[0]-2, start[1]), (end[0]-2, end[1]), width)
                pygame.draw.line(surf, (0, 255, 255, alpha), (start[0]+2, start[1]), (end[0]+2, end[1]), width)
            else:
                pygame.draw.line(surf, (*color, alpha), start, end, width)

    @staticmethod
    def _draw_pixel_trail(surf, positions, color, count, width):
        """像素尾迹"""
        scale = width / 2
        for i, pos in enumerate(positions):
            if i % 2 != 0: continue
            alpha = int(255 * i / len(positions))
            size = int(6 * scale)
            # 对齐到网格
            grid_x = int(pos[0] // size) * size
            grid_y = int(pos[1] // size) * size
            pygame.draw.rect(surf, (*color, alpha), (grid_x, grid_y, size, size))

    @staticmethod
    def _draw_bubble_trail(surf, positions, color, count, width):
        """泡泡尾迹"""
        scale = width / 2
        for i, pos in enumerate(positions):
            if i % 3 != 0: continue
            alpha = int(150 * i / len(positions))
            size = int((3 + (i % 4)) * scale)
            # 绘制空心圆
            pygame.draw.circle(surf, (*color, alpha), (int(pos[0]), int(pos[1])), size, 1)
            # 高光点
            pygame.draw.circle(surf, (255, 255, 255, alpha), (int(pos[0] - size*0.3), int(pos[1] - size*0.3)), 1)

    @staticmethod
    def _draw_toxic_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            alpha = int(180 * i / len(positions))
            if alpha < 40: continue
            size = int((4 + (i % 3)) * scale)
            # Draw biohazard-ish bubbles/clouds
            pygame.draw.circle(surf, (*color, alpha), (int(pos[0]), int(pos[1])), size)
            if random.random() < 0.2:
                pygame.draw.circle(surf, (50, 255, 50, alpha), (int(pos[0]), int(pos[1])), size // 2)

    @staticmethod
    def _draw_galaxy_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            alpha = int(150 * i / len(positions))
            if alpha < 30: continue
            # Nebula cloud
            size = int((6 + (i % 5)) * scale)
            pygame.draw.circle(surf, (*color, alpha // 2), (int(pos[0]), int(pos[1])), size)
            # Stars
            if random.random() < 0.4:
                star_color = (255, 255, 255) if random.random() < 0.8 else (255, 255, 0)
                pygame.draw.circle(surf, (*star_color, alpha), (int(pos[0] + random.randint(-5, 5)), int(pos[1] + random.randint(-5, 5))), 1)

    @staticmethod
    def _draw_magma_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            alpha = int(255 * i / len(positions))
            if alpha < 50: continue
            # Dark core
            pygame.draw.circle(surf, (50, 0, 0, alpha), (int(pos[0]), int(pos[1])), int(5 * scale))
            # Fire rim
            if i % 2 == 0:
                pygame.draw.circle(surf, (*color, alpha // 2), (int(pos[0]), int(pos[1])), int(8 * scale), 2)

    @staticmethod
    def _draw_lightning_trail(surf, positions, color, count, width):
        # Heavy lightning
        if len(positions) < 2: return
        points = []
        for i in range(len(positions)):
            offset = random.randint(int(-5*width), int(5*width))
            points.append((positions[i][0] + offset, positions[i][1] + offset))
        
        if len(points) > 1:
            pygame.draw.lines(surf, color, False, points, int(width))
            pygame.draw.lines(surf, (255, 255, 255), False, points, 1)

    @staticmethod
    def _draw_shadow_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            alpha = int(100 * i / len(positions))
            size = int(6 * scale)
            # Shadow clones
            if i % 4 == 0:
                s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*color, alpha), (size, size), size)
                surf.blit(s, (pos[0]-size, pos[1]-size))

    @staticmethod
    def _draw_retro_trail(surf, positions, color, count, width):
        # Grid lines
        scale = width / 2
        for i in range(len(positions) - 1):
            alpha = int(200 * i / len(positions))
            start, end = positions[i], positions[i+1]
            pygame.draw.line(surf, (*color, alpha), start, end, int(width))
            # Horizontal lines
            if i % 5 == 0:
                pygame.draw.line(surf, (255, 0, 255, alpha), (start[0]-10*scale, start[1]), (start[0]+10*scale, start[1]), 1)

    @staticmethod
    def _draw_aurora_trail(surf, positions, color, count, width):
        scale = width / 2
        for i in range(len(positions) - 1):
            alpha = int(150 * i / len(positions))
            if alpha < 30: continue
            # Wavy bands
            offset = math.sin(i * 0.2) * 10 * scale
            p1 = (positions[i][0] + offset, positions[i][1])
            p2 = (positions[i+1][0] + offset, positions[i+1][1])
            pygame.draw.line(surf, (*color, alpha), p1, p2, int(width * 2))
            pygame.draw.line(surf, (100, 255, 200, alpha // 2), (p1[0]+5, p1[1]), (p2[0]+5, p2[1]), int(width))

    @staticmethod
    def _draw_blood_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            alpha = int(200 * i / len(positions))
            if alpha < 50: continue
            # Dripping effect
            drop_len = random.randint(0, int(10 * scale))
            pygame.draw.line(surf, (*color, alpha), pos, (pos[0], pos[1] + drop_len), int(width))
            pygame.draw.circle(surf, (*color, alpha), (int(pos[0]), int(pos[1] + drop_len)), int(width))

    @staticmethod
    def _draw_hourglass_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            if i % 2 != 0: continue
            alpha = int(200 * i / len(positions))
            # Sand particles
            size = int(2 * scale)
            pygame.draw.rect(surf, (*color, alpha), (pos[0], pos[1], size, size))
            if random.random() < 0.3:
                offset_y = random.randint(0, int(20 * scale))
                pygame.draw.rect(surf, (*color, alpha // 2), (pos[0], pos[1] + offset_y, 1, 1))

    @staticmethod
    def _draw_thruster_trail(surf, positions, color, count, width):
        scale = width / 2
        for i in range(len(positions) - 1):
            alpha = int(255 * i / len(positions))
            # Intense core
            pygame.draw.line(surf, (255, 255, 255, alpha), positions[i], positions[i+1], int(width))
            # Outer glow
            pygame.draw.line(surf, (*color, alpha // 2), positions[i], positions[i+1], int(width * 3))

    @staticmethod
    def _draw_tentacle_trail(surf, positions, color, count, width):
        scale = width / 2
        for i in range(len(positions) - 1):
            alpha = int(180 * i / len(positions))
            if alpha < 40: continue
            # Wiggle
            wiggle = math.sin(i * 0.5) * 5 * scale
            p1 = (positions[i][0] + wiggle, positions[i][1])
            p2 = (positions[i+1][0] + wiggle, positions[i+1][1])
            pygame.draw.line(surf, (*color, alpha), p1, p2, int(width * 1.5))
            # Suckers
            if i % 4 == 0:
                pygame.draw.circle(surf, (200, 100, 255, alpha), (int(p1[0]), int(p1[1])), int(width))

    @staticmethod
    def _draw_phoenix_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            alpha = int(200 * i / len(positions))
            if alpha < 50: continue
            # Wing shape particles
            wing_span = int(15 * scale * (i / len(positions)))
            pygame.draw.circle(surf, (*color, alpha), (int(pos[0]), int(pos[1])), int(width))
            # Left wing
            pygame.draw.line(surf, (255, 100, 0, alpha // 2), pos, (pos[0] - wing_span, pos[1] - wing_span), 1)
            # Right wing
            pygame.draw.line(surf, (255, 100, 0, alpha // 2), pos, (pos[0] + wing_span, pos[1] - wing_span), 1)

    @staticmethod
    def _draw_holy_trail(surf, positions, color, count, width):
        scale = width / 2
        for i, pos in enumerate(positions):
            if i % 5 != 0: continue
            alpha = int(200 * i / len(positions))
            # Cross shape
            size = int(6 * scale)
            pygame.draw.line(surf, (*color, alpha), (pos[0], pos[1] - size), (pos[0], pos[1] + size), 2)
            pygame.draw.line(surf, (*color, alpha), (pos[0] - size, pos[1]), (pos[0] + size, pos[1]), 2)
            # Halo
            pygame.draw.circle(surf, (255, 255, 200, alpha // 3), (int(pos[0]), int(pos[1])), size * 2, 1)

# 全局涂装管理器实例
customization_manager = CustomizationManager()
