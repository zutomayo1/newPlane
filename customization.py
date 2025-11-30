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
        "name": "突击者MK-II·机械飞升",
        "desc": "纳米机械装甲，双涡轮等离子推进器，机械零件悬浮环绕",
        "neon_color": (0, 255, 255),
        "accent_color": (255, 200, 0),
        "trail_color": (0, 220, 255),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "thruster",
        "particle_count": 80,
        "category": "exclusive",
        "trail_width": 8,
        "exclusive_plane": "striker",
        "model_style": "mech_wings",
        "animated": True,
    },
    "striker_stealth": {
        "name": "暗影相位虚空渗透",
        "desc": "相位扭曲力场，机身半透明化，暗影分身环绕，空间裂缝尾迹",
        "neon_color": (80, 80, 150),
        "accent_color": (150, 150, 200),
        "trail_color": (100, 100, 180),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "void",
        "particle_count": 70,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "striker",
        "model_style": "phase_shift",
        "animated": True,
    },
    "striker_overdrive": {
        "name": "核心熔毁·超新星爆发",
        "desc": "反应堆临界状态，机身裂痕流淌岩浆，持续爆炸火花，能量波纹扩散",
        "neon_color": (255, 50, 0),
        "accent_color": (255, 255, 100),
        "trail_color": (255, 150, 0),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "magma",
        "particle_count": 95,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "striker",
        "model_style": "critical_mass",
        "animated": True,
    },
    "striker_quantum": {
        "name": "量子纠缠·薛定谔之翼",
        "desc": "量子叠加态，机身同时存在多个位置，粒子风暴漩涡，时空裂隙",
        "neon_color": (150, 255, 255),
        "accent_color": (255, 150, 255),
        "trail_color": (200, 220, 255),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "glitch",
        "particle_count": 110,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "striker",
        "model_style": "quantum_flux",
        "animated": True,
    },
    "striker_holy": {
        "name": "圣光战士·天使降临",
        "desc": "神圣羽翼展开，光之使者形态，圣光柱贯穿天际，天使光环环绕",
        "neon_color": (255, 255, 220),
        "accent_color": (255, 255, 255),
        "trail_color": (255, 250, 230),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "holy",
        "particle_count": 88,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "striker",
        "model_style": "seraph_wings",
        "animated": True,
    },
    "striker_dragon": {
        "name": "赤龙之怒·九天神威",
        "desc": "东方神龙附体，金色龙鳞遍布，龙首机头，龙爪机翼，龙息烈焰喷涌",
        "neon_color": (220, 0, 0),
        "accent_color": (255, 215, 0),
        "trail_color": (255, 100, 0),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "flame",
        "particle_count": 108,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "striker",
        "model_style": "eastern_dragon",
        "animated": True,
    },
    "striker_infinity": {
        "name": "无尽锋刃·破碎虚空",
        "desc": "机身化为能量光剑，刀刃机翼撕裂空间，闪电链连接，等离子刃光",
        "neon_color": (0, 255, 255),
        "accent_color": (255, 0, 255),
        "trail_color": (150, 200, 255),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "electric",
        "particle_count": 120,
        "category": "exclusive",
        "trail_width": 16,
        "exclusive_plane": "striker",
        "model_style": "energy_blade",
        "animated": True,
    },
    
    # ========== 专属涂装 - Phantom (虚空幻影) ==========
    "phantom_void": {
        "name": "虚空行者·星空流浪者",
        "desc": "机身化作虚空，星云流动纹理，虚空裂痕环绕，大量黑色虚空粒子",
        "neon_color": (120, 0, 220),
        "accent_color": (200, 100, 255),
        "trail_color": (140, 50, 200),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "void",
        "particle_count": 72,
        "category": "exclusive",
        "trail_width": 10,
        "exclusive_plane": "phantom",
        "model_style": "void_walker",
        "animated": True,
    },
    "phantom_ghost": {
        "name": "幽灵形态·千幻魔影",
        "desc": "机身多层重影，幽灵分身浮现消散，魂火粒子浮游，灵魂锁链缠绕",
        "neon_color": (200, 200, 255),
        "accent_color": (240, 240, 255),
        "trail_color": (180, 180, 240),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "ghost",
        "particle_count": 72,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "phantom",
        "model_style": "multi_ghost",
        "animated": True,
    },
    "phantom_mirror": {
        "name": "镜像分身·万花筒分形",
        "desc": "水晶镜面机身无限分身，每个镜面反射光芝，钻石粒子漩涡，镜像迷宫",
        "neon_color": (240, 240, 240),
        "accent_color": (255, 255, 255),
        "trail_color": (220, 220, 250),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "sparkle",
        "particle_count": 92,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "phantom",
        "model_style": "kaleidoscope",
        "animated": True,
    },
    "phantom_nightmare": {
        "name": "噩梦使者·深渊恐惧",
        "desc": "扭曲触手从机身伸展，黑雾弥漫，恐惧眼睛闪烁，疑似生命体",
        "neon_color": (100, 0, 140),
        "accent_color": (170, 0, 170),
        "trail_color": (120, 0, 160),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "tentacle",
        "particle_count": 100,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "phantom",
        "model_style": "eldritch_horror",
        "animated": True,
    },
    "phantom_aurora": {
        "name": "极光幻影·北极天幕",
        "desc": "极光布幕缠绕机身，绒丽流光变幻，光苓粒子舞蹈，梦境般的彩光",
        "neon_color": (100, 255, 200),
        "accent_color": (255, 100, 255),
        "trail_color": (150, 220, 255),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "aurora",
        "particle_count": 85,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "phantom",
        "model_style": "aurora_borealis",
        "animated": True,
    },
    "phantom_time": {
        "name": "时空漫游·时间逆流者",
        "desc": "机身沙漏纹理流转，时间回溯特效，时空波纹扩散，过去分身显现",
        "neon_color": (200, 180, 255),
        "accent_color": (255, 220, 200),
        "trail_color": (220, 200, 240),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "hourglass",
        "particle_count": 96,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "phantom",
        "model_style": "chronos",
        "animated": True,
    },
    "phantom_matrix": {
        "name": "矩阵黑客·数据之神",
        "desc": "代码矩阵构成机体，数据流瀑布般倒注，矩阵雨暂留空中，黑客帝国",
        "neon_color": (0, 255, 50),
        "accent_color": (100, 255, 150),
        "trail_color": (30, 240, 70),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "matrix",
        "particle_count": 115,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "phantom",
        "model_style": "data_god",
        "animated": True,
    },
    
    # ========== 专属涂装 - Titan (钢铁泰坦) ==========
    "titan_fortress": {
        "name": "移动要塞·钢铁堡垒",
        "desc": "层叠装甲板覆盖，主炮、副炮林立，巨型防御塔形态，工业烟雾浓郁",
        "neon_color": (140, 140, 140),
        "accent_color": (200, 200, 200),
        "trail_color": (120, 120, 120),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "smoke",
        "particle_count": 95,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "titan",
        "model_style": "mega_fortress",
        "animated": True,
    },
    "titan_nuclear": {
        "name": "核动力泰坦·裂变反应堆",
        "desc": "反应堆核心暴露辉光，辐射波纹脉冲，核绿色粒子浮现，辐射警告符号",
        "neon_color": (0, 255, 120),
        "accent_color": (220, 255, 100),
        "trail_color": (120, 255, 60),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "toxic",
        "particle_count": 78,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "titan",
        "model_style": "nuclear_core",
        "animated": True,
    },
    "titan_volcano": {
        "name": "熔岩巨兽·火山之怒",
        "desc": "装甲板裂痕流淌岩浆，火山喷发爆炸火花，燃烧石块飞散，燔炎地狱",
        "neon_color": (255, 120, 0),
        "accent_color": (255, 220, 50),
        "trail_color": (255, 100, 0),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "magma",
        "particle_count": 108,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "titan",
        "model_style": "volcanic_rage",
        "animated": True,
    },
    "titan_mech": {
        "name": "机甲战神·钢铁巨人",
        "desc": "巨型机械关节活塞，液压缸伸缩，重型武器挂载，推进器群组喷射",
        "neon_color": (0, 180, 255),
        "accent_color": (255, 180, 0),
        "trail_color": (100, 200, 255),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "thruster",
        "particle_count": 92,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "titan",
        "model_style": "steel_giant",
        "animated": True,
    },
    "titan_crystal": {
        "name": "晶簇装甲永恒之冰",
        "desc": "水晶结构装甲层叠，光芒多重折射，冰晶粒子漩涡，钻石般闪耀",
        "neon_color": (150, 220, 255),
        "accent_color": (200, 255, 255),
        "trail_color": (180, 240, 255),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "sparkle",
        "particle_count": 88,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "titan",
        "model_style": "crystal",
        "animated": True,
    },
    "titan_demon": {
        "name": "恶魔战车·地狱领主",
        "desc": "地狱之门在机身开启，魔翼展开遮天，血浆飞溅，火焰地狱，魔魂咆哭",
        "neon_color": (180, 0, 0),
        "accent_color": (120, 0, 0),
        "trail_color": (200, 30, 0),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "blood",
        "particle_count": 102,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "titan",
        "model_style": "hell_lord",
        "animated": True,
    },
    "titan_orbital": {
        "name": "轨道轰炸机·天基武库",
        "desc": "卫星武器平台形态，等离子炮阵列，光束网络交织，天基打击特效",
        "neon_color": (240, 240, 255),
        "accent_color": (255, 255, 255),
        "trail_color": (220, 220, 255),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "plasma",
        "particle_count": 118,
        "category": "exclusive",
        "trail_width": 16,
        "exclusive_plane": "titan",
        "model_style": "space_station",
        "animated": True,
    },
    
    # ========== 专属涂装 - Thunderbird (雷霆战鹰) ==========
    "thunderbird_storm": {
        "name": "风暴之眼雷霆主宰",
        "desc": "乌云漩涡环绕，密集闪电链贯穿机身，雷电风暴核心，震耳雷鸣",
        "neon_color": (100, 100, 150),
        "accent_color": (200, 200, 255),
        "trail_color": (120, 120, 180),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "lightning",
        "particle_count": 78,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "thunderbird",
        "model_style": "storm",
        "animated": True,
    },
    "thunderbird_tesla": {
        "name": "特斯拉线圈电磁风暴",
        "desc": "高压线圈全机身分布，电弧网络交织，电磁脉冲爆发，等离子球环绕",
        "neon_color": (0, 100, 255),
        "accent_color": (100, 200, 255),
        "trail_color": (50, 150, 255),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "electric",
        "particle_count": 85,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "thunderbird",
        "model_style": "tesla",
        "animated": True,
    },
    "thunderbird_plasma": {
        "name": "等离子羽翼能量天使",
        "desc": "羽翼完全等离子化，能量羽毛飘散，等离子风暴漩涡，天使降临姿态",
        "neon_color": (255, 150, 255),
        "accent_color": (255, 200, 255),
        "trail_color": (230, 170, 255),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "plasma",
        "particle_count": 95,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "thunderbird",
        "model_style": "plasma",
        "animated": True,
    },
    "thunderbird_aurora": {
        "name": "极光战鹰北境之翼",
        "desc": "极光羽翼流动变幻，七彩光带飘扬，光之羽毛洒落，梦幻鸟形",
        "neon_color": (0, 255, 150),
        "accent_color": (100, 255, 200),
        "trail_color": (50, 240, 180),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "aurora",
        "particle_count": 82,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "thunderbird",
        "model_style": "aurora_bird",
        "animated": True,
    },
    "thunderbird_valkyrie": {
        "name": "女武神战争使者",
        "desc": "神圣光翼展开，战争女神形态，圣光羽毛暴雨，天界裁决之力",
        "neon_color": (255, 245, 220),
        "accent_color": (255, 255, 255),
        "trail_color": (255, 250, 230),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "holy",
        "particle_count": 92,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "thunderbird",
        "model_style": "valkyrie",
        "animated": True,
    },
    "thunderbird_phoenix": {
        "name": "雷电凤凰涅槃重生",
        "desc": "凤凰真身显现，雷火交融羽翼，浴火重生特效，凤鸣九天，烈焰羽毛漫天",
        "neon_color": (255, 200, 0),
        "accent_color": (255, 255, 100),
        "trail_color": (255, 220, 50),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "phoenix",
        "particle_count": 105,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "thunderbird",
        "model_style": "phoenix",
        "animated": True,
    },
    "thunderbird_cosmic": {
        "name": "宇宙雷神星云之翼",
        "desc": "星云羽翼璀璨，宇宙风暴漩涡，星辰粒子暴雨，银河光带尾迹，诸神黄昏",
        "neon_color": (150, 100, 255),
        "accent_color": (200, 150, 255),
        "trail_color": (180, 120, 255),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "galaxy",
        "particle_count": 118,
        "category": "exclusive",
        "trail_width": 16,
        "exclusive_plane": "thunderbird",
        "model_style": "cosmic",
        "animated": True,
    },
    
    # ========== 专属涂装 - Viper (剧毒蝰蛇) ==========
    "viper_cobra": {
        "name": "眼镜蛇毒牙致命",
        "desc": "眼镜蛇形态，毒牙尖锐致命，蛇信吐露，剧毒喷射",
        "neon_color": (100, 255, 0),
        "accent_color": (150, 255, 50),
        "trail_color": (120, 240, 20),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "toxic",
        "particle_count": 78,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "viper",
        "model_style": "cobra",
        "animated": True,
    },
    "viper_acid": {
        "name": "强酸腐蚀溶解一切",
        "desc": "强酸液体流淌，腐蚀烟雾升腾，酸液飞溅特效，金属溶解效果",
        "neon_color": (200, 255, 0),
        "accent_color": (255, 255, 100),
        "trail_color": (220, 255, 50),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "bubble",
        "particle_count": 82,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "viper",
        "model_style": "acid",
        "animated": True,
    },
    "viper_bio": {
        "name": "生化武器病毒扩散",
        "desc": "生化病毒容器外露，病毒云团扩散，感染粒子漂浮，生物危害符号闪烁",
        "neon_color": (0, 200, 100),
        "accent_color": (100, 255, 150),
        "trail_color": (50, 220, 120),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "tentacle",
        "particle_count": 90,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "viper",
        "model_style": "bio",
        "animated": True,
    },
    "viper_plasma": {
        "name": "等离子毒液能量腐蚀",
        "desc": "等离子态毒液，能量腐蚀一切，高能毒素，物质解离",
        "neon_color": (200, 0, 255),
        "accent_color": (255, 100, 255),
        "trail_color": (220, 50, 255),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "plasma",
        "particle_count": 92,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "viper",
        "model_style": "plasma_viper",
        "animated": True,
    },
    "viper_hydra": {
        "name": "九头蛇致命群蛇",
        "desc": "多头蛇形态，九条蛇影环绕，毒牙密布，群蛇撕咬特效，毒液暴雨",
        "neon_color": (0, 150, 50),
        "accent_color": (100, 200, 100),
        "trail_color": (50, 180, 80),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "toxic",
        "particle_count": 115,
        "category": "exclusive",
        "trail_width": 16,
        "exclusive_plane": "viper",
        "model_style": "hydra",
        "animated": True,
    },
    "viper_neon": {
        "name": "霓虹毒蛇致命诱惑",
        "desc": "霓虹毒液流动纹理，彩色毒雾飘散，荧光毒液粒子，致命美丽",
        "neon_color": (0, 255, 0),
        "accent_color": (100, 255, 0),
        "trail_color": (50, 255, 0),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "toxic",
        "particle_count": 88,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "viper",
        "model_style": "neon",
        "animated": True,
    },
    "viper_serpent_god": {
        "name": "蛇神降世巴蛇吞象",
        "desc": "上古蛇神降世，巴蛇吞象之力，蛇鳞闪耀，神话再现",
        "neon_color": (255, 215, 0),
        "accent_color": (255, 255, 100),
        "trail_color": (255, 230, 50),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "holy",
        "particle_count": 115,
        "category": "exclusive",
        "trail_width": 16,
        "exclusive_plane": "viper",
        "model_style": "serpent_god",
        "animated": True,
    },
    
    # ========== 专属涂装 - Specter (幽灵收割者) ==========
    "specter_reaper": {
        "name": "死神收割灵魂收集者",
        "desc": "死神镰刀形态，灵魂火焰飘荡，收割特效，亡魂哀嚎",
        "neon_color": (100, 0, 150),
        "accent_color": (180, 100, 200),
        "trail_color": (120, 50, 180),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "ghost",
        "particle_count": 80,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "specter",
        "model_style": "reaper",
        "animated": True,
    },
    "specter_assassin": {
        "name": "幽灵刺客无声夺命",
        "desc": "幽灵刺客形态，无声无息接近，致命一击，夺命于无形",
        "neon_color": (50, 50, 80),
        "accent_color": (100, 100, 150),
        "trail_color": (70, 70, 120),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "shadow",
        "particle_count": 75,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "specter",
        "model_style": "assassin",
        "animated": True,
    },
    "specter_wraith": {
        "name": "幽灵怨灵冤魂缠绕",
        "desc": "幽灵形态半透明，怨灵面孔浮现，灵魂锁链束缚，冤魂飘荡",
        "neon_color": (150, 255, 255),
        "accent_color": (200, 255, 255),
        "trail_color": (180, 255, 255),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "ghost",
        "particle_count": 85,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "specter",
        "model_style": "wraith",
        "animated": True,
    },
    "specter_sniper": {
        "name": "幽灵狙击远程收割",
        "desc": "幽灵狙击手形态，远距离精准射击，灵魂狙击，一发致命",
        "neon_color": (0, 150, 255),
        "accent_color": (100, 200, 255),
        "trail_color": (50, 180, 255),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "electric",
        "particle_count": 82,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "specter",
        "model_style": "sniper",
        "animated": True,
    },
    "specter_poltergeist": {
        "name": "骚灵现象灵异事件",
        "desc": "骚灵现象爆发，物体悬浮飞舞，灵异力量，超自然现象",
        "neon_color": (200, 100, 255),
        "accent_color": (255, 150, 255),
        "trail_color": (220, 120, 255),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "ghost",
        "particle_count": 90,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "specter",
        "model_style": "poltergeist",
        "animated": True,
    },
    "specter_angel": {
        "name": "死亡天使黑色羽翼",
        "desc": "死亡天使降临，黑色羽翼展开，天使审判，灵魂引渡",
        "neon_color": (30, 30, 50),
        "accent_color": (200, 200, 255),
        "trail_color": (100, 100, 180),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "shadow",
        "particle_count": 100,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "specter",
        "model_style": "fallen_angel",
        "animated": True,
    },
    "specter_void_hunter": {
        "name": "虚空猎手维度收割",
        "desc": "虚空猎手形态，跨维度狩猎，虚空镰刀，收割一切",
        "neon_color": (80, 0, 120),
        "accent_color": (150, 50, 180),
        "trail_color": (100, 20, 150),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "tentacle",
        "particle_count": 110,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "specter",
        "model_style": "void_hunter",
        "animated": True,
    },
    
    # ========== 专属涂装 - Aurora (极光女神) ==========
    # ========== 专属涂装 - Aurora (极光女神) ==========
    "aurora_goddess": {
        "name": "极光至尊女神真身",
        "desc": "极光女神真身显现，冰晶王座降临，极光天幕覆盖，冰雪风暴，世界冻结",
        "neon_color": (255, 255, 220),
        "accent_color": (255, 255, 255),
        "trail_color": (255, 255, 240),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "holy",
        "particle_count": 122,
        "category": "exclusive",
        "trail_width": 16,
        "exclusive_plane": "aurora",
        "model_style": "goddess",
        "animated": True,
    },
    "aurora_nebula": {
        "name": "星云之心宇宙梦境",
        "desc": "星云纹理流动，星尘粒子暴雨，宇宙梦境显现，星云美学",
        "neon_color": (150, 100, 255),
        "accent_color": (200, 150, 255),
        "trail_color": (180, 120, 255),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "galaxy",
        "particle_count": 82,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "aurora",
        "model_style": "nebula",
        "animated": True,
    },
    "aurora_ice_queen": {
        "name": "冰雪女王永冻领域",
        "desc": "冰晶王冠高耸，冰霜领域扩张，冰雪女王降临，永冻统治",
        "neon_color": (200, 240, 255),
        "accent_color": (220, 255, 255),
        "trail_color": (210, 250, 255),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "ice",
        "particle_count": 90,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "aurora",
        "model_style": "ice_queen",
        "animated": True,
    },
    "aurora_rainbow": {
        "name": "彩虹织者七色天桥",
        "desc": "七彩光芒交织，彩虹尾迹绚烂，彩虹桥架起，色彩风暴",
        "neon_color": (255, 255, 255),
        "accent_color": (255, 200, 255),
        "trail_color": (255, 255, 255),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "rainbow",
        "particle_count": 98,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "aurora",
        "model_style": "rainbow",
        "animated": True,
    },
    "aurora_prism": {
        "name": "棱镜光辉折射万象",
        "desc": "水晶棱镜结构，光芒无限折射，万象光辉，璀璨夺目",
        "neon_color": (180, 220, 255),
        "accent_color": (220, 255, 255),
        "trail_color": (200, 240, 255),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "sparkle",
        "particle_count": 105,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "aurora",
        "model_style": "prism",
        "animated": True,
    },
    "aurora_sakura": {
        "name": "樱花女神春之降临",
        "desc": "樱花暴雨飞舞，粉色花瓣海洋，春天女神显现，生命绽放",
        "neon_color": (255, 180, 200),
        "accent_color": (255, 220, 230),
        "trail_color": (255, 200, 220),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "sakura",
        "particle_count": 112,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "aurora",
        "model_style": "sakura",
        "animated": True,
    },
    "aurora_celestial": {
        "name": "天界使者神圣降临",
        "desc": "天使光环闪耀，圣洁羽翼展开，天界之门打开，神圣力量",
        "neon_color": (255, 250, 240),
        "accent_color": (255, 255, 255),
        "trail_color": (255, 252, 245),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "holy",
        "particle_count": 120,
        "category": "exclusive",
        "trail_width": 16,
        "exclusive_plane": "aurora",
        "model_style": "celestial",
        "animated": True,
    },
    
    # ========== 专属涂装 - Crimson (绯红之刃) ==========
    "crimson_blood": {
        "name": "绯红之刃血月降临",
        "desc": "血色光芒笼罩，血雾弥漫升腾，血液飞溅特效，嗜血气息",
        "neon_color": (180, 0, 0),
        "accent_color": (255, 50, 50),
        "trail_color": (200, 20, 20),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "blood",
        "particle_count": 80,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "crimson",
        "model_style": "blood",
        "animated": True,
    },
    "crimson_samurai": {
        "name": "绯红武士血刃斩魂",
        "desc": "武士刀刃闪耀，武士道精神，血刃快速斩击，一击毙命",
        "neon_color": (200, 0, 0),
        "accent_color": (255, 215, 0),
        "trail_color": (220, 20, 0),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "blade",
        "particle_count": 95,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "crimson",
        "model_style": "samurai",
        "animated": True,
    },
    "crimson_demon": {
        "name": "血魔降世魔王降临",
        "desc": "血魔之翼展开，血色魔纹遍布，魔王形态显现，血之君主",
        "neon_color": (120, 0, 0),
        "accent_color": (80, 0, 0),
        "trail_color": (150, 10, 0),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "flame",
        "particle_count": 110,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "crimson",
        "model_style": "demon",
        "animated": True,
    },
    "crimson_inferno": {
        "name": "地狱烈焰炼狱之火",
        "desc": "地狱火海燃烧，烈焰席卷一切，炼狱般高温，焚毁世界",
        "neon_color": (255, 80, 0),
        "accent_color": (255, 150, 0),
        "trail_color": (255, 100, 0),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "magma",
        "particle_count": 105,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "crimson",
        "model_style": "inferno",
        "animated": True,
    },
    "crimson_rose": {
        "name": "血玫瑰致命之美",
        "desc": "血红玫瑰绽放，带刺玫瑰丛生，美丽而致命，芬芳杀机",
        "neon_color": (200, 50, 80),
        "accent_color": (255, 100, 150),
        "trail_color": (220, 70, 100),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "sakura",
        "particle_count": 88,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "crimson",
        "model_style": "rose",
        "animated": True,
    },
    "crimson_dragon": {
        "name": "血龙咆哮龙息焚天",
        "desc": "血龙形态显现，龙息喷涌而出，血色龙鳞闪耀，龙威镇世",
        "neon_color": (220, 0, 0),
        "accent_color": (255, 215, 0),
        "trail_color": (240, 20, 0),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "blood",
        "particle_count": 112,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "crimson",
        "model_style": "dragon",
        "animated": True,
    },
    "crimson_vampire": {
        "name": "吸血鬼血族领主",
        "desc": "吸血蝙蝠环绕，血族纹章显现，血液吸收光束，暗夜猎食者",
        "neon_color": (100, 0, 50),
        "accent_color": (200, 0, 100),
        "trail_color": (150, 0, 70),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "blood",
        "particle_count": 85,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "crimson",
        "model_style": "vampire",
        "animated": True,
    },
    
    # ========== 专属涂装 - Stalker (星界潜行者) ==========
    "stalker_predator": {
        "name": "铁血战士热能追踪",
        "desc": "铁血战士形态，热能视觉追踪，等离子炮，狩猎荣耀",
        "neon_color": (100, 0, 150),
        "accent_color": (180, 100, 200),
        "trail_color": (120, 50, 180),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "tentacle",
        "particle_count": 80,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "stalker",
        "model_style": "predator",
        "animated": True,
    },
    "stalker_alien": {
        "name": "异形猎手完美生物",
        "desc": "异形生物形态，完美生物设计，酸性血液，致命猎杀",
        "neon_color": (50, 100, 0),
        "accent_color": (100, 180, 50),
        "trail_color": (70, 140, 20),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "toxic",
        "particle_count": 88,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "stalker",
        "model_style": "alien",
        "animated": True,
    },
    "stalker_chameleon": {
        "name": "变色龙完美伪装",
        "desc": "变色龙形态，完美环境伪装，色彩变幻，融入环境",
        "neon_color": (100, 150, 100),
        "accent_color": (150, 200, 150),
        "trail_color": (120, 180, 120),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "smoke",
        "particle_count": 72,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "stalker",
        "model_style": "chameleon",
        "animated": True,
    },
    "stalker_insect": {
        "name": "虫群潜行复眼侦测",
        "desc": "虫群形态，复眼全方位侦测，潜行猎杀，群体智慧",
        "neon_color": (0, 100, 50),
        "accent_color": (50, 150, 100),
        "trail_color": (20, 120, 70),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "tentacle",
        "particle_count": 95,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "stalker",
        "model_style": "insect",
        "animated": True,
    },
    "stalker_drone": {
        "name": "无人机群天罗地网",
        "desc": "无人机群部署，天罗地网监控，智能追踪，无处可逃",
        "neon_color": (200, 150, 0),
        "accent_color": (255, 200, 50),
        "trail_color": (220, 180, 20),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "matrix",
        "particle_count": 102,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "stalker",
        "model_style": "drone",
        "animated": True,
    },
    "stalker_void": {
        "name": "虚空潜伏无形存在",
        "desc": "虚空隐匿状态，存在感抹除，维度缝隙穿梭，虚无形态",
        "neon_color": (80, 0, 120),
        "accent_color": (150, 50, 180),
        "trail_color": (100, 20, 150),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "void",
        "particle_count": 88,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "stalker",
        "model_style": "void",
        "animated": True,
    },
    "stalker_xenomorph": {
        "name": "异形皇后终极猎食",
        "desc": "异形皇后显现，终极生物猎手，完美进化，生物链顶端",
        "neon_color": (20, 80, 20),
        "accent_color": (100, 150, 100),
        "trail_color": (50, 120, 50),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "toxic",
        "particle_count": 115,
        "category": "exclusive",
        "trail_width": 16,
        "exclusive_plane": "stalker",
        "model_style": "xenomorph",
        "animated": True,
    },
    
    # ========== 专属涂装 - Gaia (大地守护者) ==========
    "gaia_forest": {
        "name": "森林之母绿色守护",
        "desc": "森林植被覆盖，树冠枝叶繁茂，绿叶粒子飞扬，生命气息",
        "neon_color": (50, 150, 50),
        "accent_color": (100, 200, 100),
        "trail_color": (70, 180, 70),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "sakura",
        "particle_count": 85,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "gaia",
        "model_style": "forest",
        "animated": True,
    },
    "gaia_crystal": {
        "name": "水晶森林宝石丛林",
        "desc": "水晶树木丛生，宝石果实闪耀，晶莹剔透，光芒万丈",
        "neon_color": (0, 255, 200),
        "accent_color": (100, 255, 255),
        "trail_color": (50, 255, 220),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "sparkle",
        "particle_count": 85,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "gaia",
        "model_style": "crystal",
        "animated": True,
    },
    "gaia_rock": {
        "name": "岩石巨人大地之力",
        "desc": "岩石巨人形态，大地之力涌动，岩石粒子飞舞，坚不可摧",
        "neon_color": (100, 80, 60),
        "accent_color": (150, 120, 100),
        "trail_color": (120, 100, 80),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "smoke",
        "particle_count": 75,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "gaia",
        "model_style": "rock",
        "animated": True,
    },
    "gaia_elemental": {
        "name": "元素领主自然四元",
        "desc": "四元素环绕，地水火风交织，元素领主形态，自然之力",
        "neon_color": (100, 200, 150),
        "accent_color": (150, 255, 200),
        "trail_color": (120, 220, 180),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "sparkle",
        "particle_count": 92,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "gaia",
        "model_style": "elemental",
        "animated": True,
    },
    "gaia_overgrowth": {
        "name": "过度生长野性爆发",
        "desc": "植被疯狂生长，藤蔓肆意蔓延，野性力量爆发，自然失控",
        "neon_color": (0, 200, 50),
        "accent_color": (50, 255, 100),
        "trail_color": (20, 220, 70),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "toxic",
        "particle_count": 100,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "gaia",
        "model_style": "overgrowth",
        "animated": True,
    },
    "gaia_treant": {
        "name": "树人长老世界古树",
        "desc": "树人长老形态，世界古树降临，千年智慧，森林守护",
        "neon_color": (80, 120, 40),
        "accent_color": (120, 180, 80),
        "trail_color": (100, 150, 60),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "sakura",
        "particle_count": 108,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "gaia",
        "model_style": "treant",
        "animated": True,
    },
    "gaia_titan": {
        "name": "盖亚泰坦星球化身",
        "desc": "星球泰坦显现，盖亚意志具化，地壳板块浮动，星球之力",
        "neon_color": (150, 130, 100),
        "accent_color": (200, 180, 150),
        "trail_color": (180, 160, 130),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "smoke",
        "particle_count": 118,
        "category": "exclusive",
        "trail_width": 16,
        "exclusive_plane": "gaia",
        "model_style": "titan",
        "animated": True,
    },
    
    # ========== 专属涂装 - Weaver (虚空编织者) ==========
    "weaver_spider": {
        "name": "蜘蛛之网命运丝线",
        "desc": "蜘蛛结网形态，命运丝线编织，蛛网密布，困住猎物",
        "neon_color": (50, 0, 0),
        "accent_color": (150, 50, 50),
        "trail_color": (100, 20, 20),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "tentacle",
        "particle_count": 75,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "weaver",
        "model_style": "spider",
        "animated": True,
    },
    "weaver_web": {
        "name": "虚空编织命运之网",
        "desc": "命运丝线交织，虚空之网编织，丝线粒子飘舞，命运编织者",
        "neon_color": (200, 200, 200),
        "accent_color": (255, 255, 255),
        "trail_color": (220, 220, 220),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "matrix",
        "particle_count": 75,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "weaver",
        "model_style": "web",
        "animated": True,
    },
    "weaver_silk": {
        "name": "丝绸之路空间织布",
        "desc": "丝绸般空间编织，空间之路铺展，柔韧丝线，连接万物",
        "neon_color": (220, 220, 220),
        "accent_color": (255, 255, 255),
        "trail_color": (240, 240, 240),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "sparkle",
        "particle_count": 85,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "weaver",
        "model_style": "silk",
        "animated": True,
    },
    "weaver_network": {
        "name": "网络编织数据之网",
        "desc": "数据网络编织，信息之网扩散，网络节点，连接一切",
        "neon_color": (0, 150, 255),
        "accent_color": (100, 200, 255),
        "trail_color": (50, 180, 255),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "electric",
        "particle_count": 92,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "weaver",
        "model_style": "network",
        "animated": True,
    },
    "weaver_matrix": {
        "name": "矩阵编织代码之丝",
        "desc": "矩阵代码编织，程序丝线交织，源代码显现，世界重写",
        "neon_color": (0, 255, 0),
        "accent_color": (100, 255, 100),
        "trail_color": (50, 255, 50),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "matrix",
        "particle_count": 100,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "weaver",
        "model_style": "matrix",
        "animated": True,
    },
    "weaver_destiny": {
        "name": "命运编织因果之网",
        "desc": "命运之网显现，因果关系编织，命运线条交错，宿命难逃",
        "neon_color": (255, 215, 0),
        "accent_color": (255, 255, 200),
        "trail_color": (255, 230, 100),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "sparkle",
        "particle_count": 110,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "weaver",
        "model_style": "destiny",
        "animated": True,
    },
    "weaver_cosmic": {
        "name": "宇宙编织星河织布",
        "desc": "星河丝线编织，宇宙结构显化，星辰作为编织点，造物之手",
        "neon_color": (150, 100, 255),
        "accent_color": (200, 150, 255),
        "trail_color": (180, 120, 255),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "galaxy",
        "particle_count": 108,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "weaver",
        "model_style": "cosmic",
        "animated": True,
    },
    
    # ========== 专属涂装 - Solar (日冕耀斑) ==========
    "solar_sun_god": {
        "name": "太阳神拉之审判",
        "desc": "太阳神拉显现，太阳审判降临，神圣光芒普照，万物臣服",
        "neon_color": (255, 200, 0),
        "accent_color": (255, 255, 100),
        "trail_color": (255, 220, 50),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "flame",
        "particle_count": 108,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "solar",
        "model_style": "sun_god",
        "animated": True,
    },
    "solar_phoenix": {
        "name": "太阳凤凰永恒烈焰",
        "desc": "太阳凤凰涅槃，永恒烈焰燃烧，凤凰真火，不灭不休",
        "neon_color": (255, 100, 0),
        "accent_color": (255, 200, 0),
        "trail_color": (255, 150, 0),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "phoenix",
        "particle_count": 118,
        "category": "exclusive",
        "trail_width": 16,
        "exclusive_plane": "solar",
        "model_style": "phoenix",
        "animated": True,
    },
    "solar_fusion": {
        "name": "核聚变恒星之心",
        "desc": "核聚变反应爆发，氢氦燃烧特效，恒星内核能量，聚变光芒",
        "neon_color": (100, 150, 255),
        "accent_color": (200, 220, 255),
        "trail_color": (150, 180, 255),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "plasma",
        "particle_count": 95,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "solar",
        "model_style": "fusion",
        "animated": True,
    },
    "solar_flare": {
        "name": "日冕耀斑太阳风暴",
        "desc": "太阳耀斑爆发，日冕物质抛射，太阳风粒子暴雨，恒星能量",
        "neon_color": (255, 255, 200),
        "accent_color": (255, 255, 255),
        "trail_color": (255, 255, 220),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "flame",
        "particle_count": 82,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "solar",
        "model_style": "flare",
        "animated": True,
    },
    "solar_corona": {
        "name": "日冕王冠太阳之子",
        "desc": "日冕王冠显现，太阳光芒万丈，黄金光辉笼罩，太阳神形态",
        "neon_color": (255, 180, 100),
        "accent_color": (255, 220, 150),
        "trail_color": (255, 200, 120),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "plasma",
        "particle_count": 88,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "solar",
        "model_style": "corona",
        "animated": True,
    },
    "solar_supernova": {
        "name": "超新星恒星爆炸",
        "desc": "超新星爆炸序列，恒星崩解特效，能量波扩散，星云形成",
        "neon_color": (255, 255, 255),
        "accent_color": (255, 200, 255),
        "trail_color": (255, 230, 255),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "holy",
        "particle_count": 112,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "solar",
        "model_style": "supernova",
        "animated": True,
    },
    "solar_eclipse": {
        "name": "日全食光暗交替",
        "desc": "日全食现象，光暗瞬间转换，日冕边缘发光，贝利珠特效",
        "neon_color": (50, 50, 100),
        "accent_color": (255, 200, 0),
        "trail_color": (100, 100, 150),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "void",
        "particle_count": 102,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "solar",
        "model_style": "eclipse",
        "animated": True,
    },
    
    # ========== 专属涂装 - Arbiter (量子裁决者) ==========
    "arbiter_quantum": {
        "name": "量子裁决概率坍缩",
        "desc": "量子态叠加显现，概率云团漂浮，波函数坍缩，量子纠缠",
        "neon_color": (180, 100, 255),
        "accent_color": (220, 150, 255),
        "trail_color": (200, 120, 255),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "glitch",
        "particle_count": 80,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "arbiter",
        "model_style": "quantum",
        "animated": True,
    },
    "arbiter_fractal": {
        "name": "分形几何无限循环",
        "desc": "分形结构显现，几何无限递归，数学美学，完美对称",
        "neon_color": (255, 0, 255),
        "accent_color": (0, 255, 255),
        "trail_color": (200, 100, 255),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "electric",
        "particle_count": 92,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "arbiter",
        "model_style": "fractal",
        "animated": True,
    },
    "arbiter_law": {
        "name": "法则之书规则编写",
        "desc": "法则之书展开，规则条文显现，法则粒子环绕，规则执行",
        "neon_color": (255, 215, 0),
        "accent_color": (255, 255, 255),
        "trail_color": (255, 230, 100),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "holy",
        "particle_count": 85,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "arbiter",
        "model_style": "law",
        "animated": True,
    },
    "arbiter_balance": {
        "name": "平衡裁决天平永恒",
        "desc": "天平绝对平衡，公正秤杆显现，平衡粒子飘散，秩序维持",
        "neon_color": (128, 128, 128),
        "accent_color": (200, 200, 200),
        "trail_color": (150, 150, 150),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "smoke",
        "particle_count": 78,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "arbiter",
        "model_style": "balance",
        "animated": True,
    },
    "arbiter_judge": {
        "name": "终极审判公正天平",
        "desc": "审判天平显现，公正符文闪耀，裁决之光降临，法则之力",
        "neon_color": (255, 255, 200),
        "accent_color": (255, 255, 255),
        "trail_color": (255, 255, 220),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "holy",
        "particle_count": 85,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "arbiter",
        "model_style": "judge",
        "animated": True,
    },
    "arbiter_matrix": {
        "name": "矩阵主宰代码执行",
        "desc": "矩阵世界显现，代码洪流奔涌，程序执行特效，数字主宰",
        "neon_color": (0, 255, 100),
        "accent_color": (100, 255, 150),
        "trail_color": (50, 255, 120),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "matrix",
        "particle_count": 92,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "arbiter",
        "model_style": "matrix",
        "animated": True,
    },
    "arbiter_truth": {
        "name": "真理之眼洞察一切",
        "desc": "真理之眼睁开，洞察万物本质，真理光芒普照，一切明晰",
        "neon_color": (255, 255, 255),
        "accent_color": (255, 255, 220),
        "trail_color": (255, 255, 240),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "holy",
        "particle_count": 102,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "arbiter",
        "model_style": "truth",
        "animated": True,
    },
    
    # ========== 专属涂装 - Eclipse (日食幽灵) ==========
    "eclipse_moon": {
        "name": "血月当空月蚀之力",
        "desc": "血月高悬天空，月蚀能量降临，血色月光洒落，月神之力",
        "neon_color": (150, 0, 0),
        "accent_color": (255, 50, 50),
        "trail_color": (180, 20, 20),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "blood",
        "particle_count": 88,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "eclipse",
        "model_style": "moon",
        "animated": True,
    },
    "eclipse_void": {
        "name": "虚空日食黑洞边缘",
        "desc": "虚空黑洞显现，引力透镜效应，事件视界线，光线扭曲",
        "neon_color": (0, 0, 0),
        "accent_color": (100, 0, 150),
        "trail_color": (50, 0, 100),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "void",
        "particle_count": 85,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "eclipse",
        "model_style": "void",
        "animated": True,
    },
    "eclipse_shadow": {
        "name": "日食幽灵暗影吞噬",
        "desc": "日食阴影吞噬，黑暗吞食光明，暗影扩散特效，光暗界限",
        "neon_color": (30, 30, 50),
        "accent_color": (80, 80, 120),
        "trail_color": (50, 50, 80),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "shadow",
        "particle_count": 78,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "eclipse",
        "model_style": "shadow",
        "animated": True,
    },
    "eclipse_abyss": {
        "name": "深渊凝视虚无吞噬",
        "desc": "深渊裂缝开启，虚无力量涌出，凝视毁灭一切，深渊吞噬",
        "neon_color": (100, 0, 150),
        "accent_color": (180, 50, 200),
        "trail_color": (120, 20, 180),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "tentacle",
        "particle_count": 105,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "eclipse",
        "model_style": "abyss",
        "animated": True,
    },
    "eclipse_night": {
        "name": "永夜降临黑暗时代",
        "desc": "永恒黑夜降临，黑暗领域扩张，星光逐渐消逝，永恒夜幕",
        "neon_color": (20, 20, 40),
        "accent_color": (80, 80, 120),
        "trail_color": (40, 40, 70),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "shadow",
        "particle_count": 92,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "eclipse",
        "model_style": "night",
        "animated": True,
    },
    "eclipse_dual": {
        "name": "日月双食阴阳交替",
        "desc": "日月同时食相，阴阳力量交替，双重天象，天地失色",
        "neon_color": (150, 50, 180),
        "accent_color": (220, 100, 255),
        "trail_color": (180, 70, 220),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "electric",
        "particle_count": 95,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "eclipse",
        "model_style": "dual",
        "animated": True,
    },
    "eclipse_cosmos": {
        "name": "宇宙日食星际黑暗",
        "desc": "宇宙尺度日食，星际黑暗降临，星光全部遮蔽，宇宙寂灭",
        "neon_color": (80, 0, 120),
        "accent_color": (150, 100, 200),
        "trail_color": (100, 50, 150),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "galaxy",
        "particle_count": 115,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "eclipse",
        "model_style": "cosmos",
        "animated": True,
    },
    
    # ========== 专属涂装 - Prism (棱镜分光) ==========
    "prism_diamond": {
        "name": "钻石星辰完美折射",
        "desc": "钻石切割面显现，完美折射光芒，星辰般闪耀，光之宝石",
        "neon_color": (220, 220, 255),
        "accent_color": (255, 255, 255),
        "trail_color": (240, 240, 255),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "sparkle",
        "particle_count": 108,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "prism",
        "model_style": "diamond",
        "animated": True,
    },
    "prism_refraction": {
        "name": "多重折射光线迷宫",
        "desc": "光线多次折射，光学迷宫形成，光路复杂，眩目迷离",
        "neon_color": (200, 255, 255),
        "accent_color": (255, 200, 255),
        "trail_color": (220, 230, 255),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "rainbow",
        "particle_count": 85,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "prism",
        "model_style": "refraction",
        "animated": True,
    },
    "prism_laser": {
        "name": "激光矩阵光束网络",
        "desc": "激光矩阵布阵，光束网络交织，高能光束发射，光之武器",
        "neon_color": (255, 0, 100),
        "accent_color": (255, 100, 150),
        "trail_color": (255, 50, 120),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "electric",
        "particle_count": 90,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "prism",
        "model_style": "laser",
        "animated": True,
    },
    "prism_glass": {
        "name": "玻璃艺术透明美学",
        "desc": "玻璃艺术品形态，透明材质美学，光影交错，艺术结晶",
        "neon_color": (100, 255, 220),
        "accent_color": (150, 255, 255),
        "trail_color": (120, 255, 240),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "sparkle",
        "particle_count": 92,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "prism",
        "model_style": "glass",
        "animated": True,
    },
    "prism_crystal": {
        "name": "晶体共振光芒四射",
        "desc": "晶体结构共振，光芒四面发射，光的放大效应，晶莹璀璨",
        "neon_color": (180, 220, 255),
        "accent_color": (220, 255, 255),
        "trail_color": (200, 240, 255),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "ice",
        "particle_count": 88,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "prism",
        "model_style": "crystal",
        "animated": True,
    },
    "prism_rainbow": {
        "name": "棱镜分光七彩虹光",
        "desc": "光谱完全分离，七彩虹光闪耀，色彩粒子飞舞，光的盛宴",
        "neon_color": (255, 255, 255),
        "accent_color": (255, 200, 255),
        "trail_color": (255, 230, 255),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "rainbow",
        "particle_count": 75,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "prism",
        "model_style": "rainbow",
        "animated": True,
    },
    "prism_aurora": {
        "name": "极光棱镜光谱盛宴",
        "desc": "极光通过棱镜，光谱完全展开，色彩盛宴，绚烂夺目",
        "neon_color": (100, 255, 200),
        "accent_color": (200, 255, 255),
        "trail_color": (150, 255, 220),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "aurora",
        "particle_count": 110,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "prism",
        "model_style": "aurora",
        "animated": True,
    },
    
    # ========== 专属涂装 - Necro (死灵骑士) ==========
    "necro_lich": {
        "name": "巫妖王不死法师",
        "desc": "巫妖王形态显现，死亡魔法爆发，灵魂囚笼显现，不死之力",
        "neon_color": (100, 255, 100),
        "accent_color": (150, 255, 150),
        "trail_color": (120, 255, 120),
        "unlocked": False,
        "cost": 2000,
        "trail_style": "ghost",
        "particle_count": 85,
        "category": "exclusive",
        "trail_width": 11,
        "exclusive_plane": "necro",
        "model_style": "lich",
        "animated": True,
    },
    "necro_bone": {
        "name": "白骨王座骸骨帝王",
        "desc": "白骨王座显现，骸骨帝王登基，骨骼军团列阵，死亡统治",
        "neon_color": (200, 200, 200),
        "accent_color": (255, 255, 255),
        "trail_color": (220, 220, 220),
        "unlocked": False,
        "cost": 2200,
        "trail_style": "smoke",
        "particle_count": 88,
        "category": "exclusive",
        "trail_width": 12,
        "exclusive_plane": "necro",
        "model_style": "bone",
        "animated": True,
    },
    "necro_plague": {
        "name": "瘟疫传播死亡疫病",
        "desc": "瘟疫云团扩散，疾病粒子漂浮，感染特效显现，死亡瘟疫",
        "neon_color": (100, 255, 0),
        "accent_color": (150, 255, 50),
        "trail_color": (120, 255, 20),
        "unlocked": False,
        "cost": 2400,
        "trail_style": "toxic",
        "particle_count": 92,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "necro",
        "model_style": "plague",
        "animated": True,
    },
    "necro_soul": {
        "name": "灵魂收集魂瓶封印",
        "desc": "灵魂收集瓶显现，无数魂魄封印，灵魂能量涌动，亡魂哀嚎",
        "neon_color": (0, 220, 255),
        "accent_color": (100, 255, 255),
        "trail_color": (50, 240, 255),
        "unlocked": False,
        "cost": 2600,
        "trail_style": "ghost",
        "particle_count": 95,
        "category": "exclusive",
        "trail_width": 13,
        "exclusive_plane": "necro",
        "model_style": "soul",
        "animated": True,
    },
    "necro_reaper": {
        "name": "死神化身灵魂收割",
        "desc": "死神真身显化，灵魂收割镰刀，死亡宣判降临，生命终结",
        "neon_color": (150, 0, 150),
        "accent_color": (200, 100, 200),
        "trail_color": (180, 50, 180),
        "unlocked": False,
        "cost": 2800,
        "trail_style": "shadow",
        "particle_count": 110,
        "category": "exclusive",
        "trail_width": 15,
        "exclusive_plane": "necro",
        "model_style": "reaper",
        "animated": True,
    },
    "necro_vampire": {
        "name": "吸血鬼伯爵永夜不朽",
        "desc": "吸血鬼伯爵形态，蝙蝠群环绕，鲜血吸收，永夜不朽",
        "neon_color": (150, 0, 50),
        "accent_color": (200, 50, 100),
        "trail_color": (180, 20, 70),
        "unlocked": False,
        "cost": 3000,
        "trail_style": "blood",
        "particle_count": 105,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "necro",
        "model_style": "vampire",
        "animated": True,
    },
    "necro_undead": {
        "name": "不死军团永恒行军",
        "desc": "不死军团行军，永恒战争继续，亡者复苏特效，死而复生",
        "neon_color": (80, 120, 80),
        "accent_color": (150, 200, 150),
        "trail_color": (100, 160, 100),
        "unlocked": False,
        "cost": 3500,
        "trail_style": "ghost",
        "particle_count": 100,
        "category": "exclusive",
        "trail_width": 14,
        "exclusive_plane": "necro",
        "model_style": "undead",
        "animated": True,
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
