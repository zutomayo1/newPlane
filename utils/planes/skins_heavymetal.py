# -*- coding: utf-8 -*-
"""
================================================================================
  🎸 维那斯万岁 · HEAVY METAL - 12涂装皮肤系统 (差异化增强版)
================================================================================
  机体类型: 重型飞行吉他战舰
  视觉风格: 工业金属 + 黑暗哥特 + 舞台威压
  
  12种涂装各有极大视觉差异 + 独特装饰元素：
  1. 死亡金属 - 纯黑 + 骷髅图案 + 紫色闪电尾焰
  2. 血腥狂欢 - 鲜红 + 血迹飞溅 + 血红火焰
  3. 电子蓝调 - 赛博蓝 + 电路纹路 + 电弧尾焰
  4. 黄金圣歌 - 土豪金 + 圣光光环 + 金色粒子
  5. 迷幻紫雾 - 荧光紫 + 漩涡图案 + 迷幻波纹
  6. 核废料   - 荧光绿 + 辐射符号 + 毒雾尾焰
  7. 冰封圣咏 - 冰蓝白 + 冰晶纹路 + 冰霜粒子
  8. 地狱烈焰 - 熔岩橙 + 裂纹岩浆 + 炽焰尾焰
  9. 午夜蓝调 - 深邃蓝 + 星星点缀 + 月光尾焰
  10. 彩虹桥  - 渐变彩虹 + 棱镜光芒 + 七彩尾焰
  11. 蒸汽朋克 - 黄铜 + 齿轮装饰 + 蒸汽尾焰
  12. 星际朋克 - 星云紫 + 星座图案 + 星尘尾焰
================================================================================
"""

import pygame
import math
import random
from typing import Tuple, List

# ============================================================
#   12涂装主题配色方案 - 差异化增强版
# ============================================================
HEAVYMETAL_THEMES = {
    # ========== 1. 死亡金属 - 纯黑哑光 + 骷髅 + 紫色闪电 ==========
    "default": {
        "name": "死亡金属",
        "body_main": (5, 5, 8),              # 极致纯黑
        "body_secondary": (15, 15, 20),
        "body_accent": (30, 30, 38),
        "body_edge": (50, 50, 65),
        "body_shadow": (0, 0, 0),
        "metal_highlight": (80, 80, 95),
        "metal_brush": (40, 40, 50),
        "chrome": (130, 130, 150),
        "worn_metal": (60, 55, 50),
        "neon_primary": (120, 40, 180),       # 暗紫强调
        "neon_secondary": (80, 200, 80),
        "neon_tertiary": (180, 50, 100),
        "glow_color": (100, 30, 150),
        "speaker_cone": (15, 15, 18),
        "speaker_surround": (25, 25, 30),
        "speaker_dust_cap": (40, 40, 48),
        "speaker_rim": (65, 65, 78),
        "speaker_grill": (8, 8, 10),
        "cabinet_tolex": (10, 8, 8),
        "cabinet_corner": (45, 42, 40),
        "fretboard": (40, 25, 12),
        "fretboard_inlay": (180, 175, 165),
        "fret_wire": (175, 170, 158),
        "string_steel": (195, 190, 180),
        "string_wound": (155, 135, 95),
        "tuner_body": (55, 52, 48),
        "tuner_button": (40, 38, 35),
        "pickup_cover": (30, 30, 35),
        "pickup_pole": (80, 78, 72),
        "bridge_metal": (115, 110, 100),
        "knob_body": (35, 35, 38),
        "knob_marker": (195, 190, 175),
        "exhaust_core": (180, 100, 255),      # 紫色尾焰核心
        "exhaust_outer": (100, 40, 180),      # 暗紫外焰
        "spark_color": (200, 150, 255),
        "guitar_shape": "flying_v",
        "headstock_style": "pointed",
        "finish": "matte",
        # 差异化装饰
        "decal_type": "skull",                # 骷髅图案
        "decal_color": (120, 40, 180),
        "string_glow": True,                  # 琴弦发光
        "string_glow_color": (150, 80, 220),
        "exhaust_style": "lightning",         # 闪电形尾焰
        "speaker_effect": "pulse_dark",       # 音箱暗脉冲
    },
    
    # ========== 2. 血腥狂欢 - 鲜血红 + 血迹飞溅 + 血红火焰 ==========
    "bloody": {
        "name": "血腥狂欢",
        "body_main": (120, 15, 15),           # 鲜红主色！
        "body_secondary": (80, 10, 10),
        "body_accent": (160, 30, 30),
        "body_edge": (200, 50, 50),
        "body_shadow": (40, 5, 5),
        "metal_highlight": (220, 100, 100),
        "metal_brush": (140, 50, 50),
        "chrome": (180, 120, 120),
        "worn_metal": (100, 60, 55),
        "neon_primary": (255, 50, 50),        # 血红高光
        "neon_secondary": (255, 120, 50),
        "neon_tertiary": (200, 30, 30),
        "glow_color": (255, 60, 60),
        "speaker_cone": (80, 25, 25),
        "speaker_surround": (100, 35, 35),
        "speaker_dust_cap": (130, 50, 50),
        "speaker_rim": (160, 70, 70),
        "speaker_grill": (50, 15, 15),
        "cabinet_tolex": (60, 15, 12),
        "cabinet_corner": (90, 50, 45),
        "fretboard": (30, 15, 10),
        "fretboard_inlay": (200, 180, 175),
        "fret_wire": (170, 140, 130),
        "string_steel": (195, 180, 175),
        "string_wound": (160, 120, 100),
        "tuner_body": (70, 40, 38),
        "tuner_button": (50, 28, 25),
        "pickup_cover": (60, 25, 22),
        "pickup_pole": (100, 65, 60),
        "bridge_metal": (130, 95, 88),
        "knob_body": (65, 32, 28),
        "knob_marker": (220, 195, 185),
        "exhaust_core": (255, 100, 50),       # 血焰核心
        "exhaust_outer": (200, 30, 10),       # 暗血外焰
        "spark_color": (255, 80, 50),
        "guitar_shape": "explorer",
        "headstock_style": "sharp",
        "finish": "gloss",
        # 差异化装饰
        "decal_type": "blood_splatter",       # 血迹飞溅
        "decal_color": (180, 20, 20),
        "string_glow": True,
        "string_glow_color": (255, 80, 80),   # 血红琴弦
        "exhaust_style": "dripping",          # 滴血形尾焰
        "speaker_effect": "heartbeat",        # 心跳脉动
        "body_pattern": "cracks",             # 裂纹图案
        "pattern_color": (200, 40, 40),
    },
    
    # ========== 3. 电子蓝调 - 赛博蓝 + 电路纹路 + 电弧尾焰 ==========
    "cyber": {
        "name": "电子蓝调",
        "body_main": (20, 80, 180),           # 亮蓝主色！
        "body_secondary": (15, 60, 140),
        "body_accent": (40, 120, 220),
        "body_edge": (80, 160, 255),
        "body_shadow": (10, 40, 100),
        "metal_highlight": (150, 200, 255),
        "metal_brush": (80, 140, 200),
        "chrome": (180, 220, 255),
        "worn_metal": (90, 130, 170),
        "neon_primary": (50, 180, 255),       # 电光蓝
        "neon_secondary": (150, 220, 255),
        "neon_tertiary": (30, 140, 220),
        "glow_color": (80, 200, 255),
        "speaker_cone": (30, 70, 130),
        "speaker_surround": (45, 95, 165),
        "speaker_dust_cap": (65, 125, 200),
        "speaker_rim": (100, 160, 230),
        "speaker_grill": (20, 50, 100),
        "cabinet_tolex": (25, 60, 120),
        "cabinet_corner": (70, 120, 180),
        "fretboard": (20, 50, 100),
        "fretboard_inlay": (200, 230, 255),
        "fret_wire": (170, 200, 240),
        "string_steel": (210, 230, 250),
        "string_wound": (160, 190, 230),
        "tuner_body": (60, 100, 160),
        "tuner_button": (45, 80, 130),
        "pickup_cover": (40, 85, 150),
        "pickup_pole": (100, 150, 210),
        "bridge_metal": (140, 180, 230),
        "knob_body": (55, 95, 155),
        "knob_marker": (220, 240, 255),
        "exhaust_core": (200, 240, 255),      # 电蓝核心
        "exhaust_outer": (50, 150, 255),      # 电弧外焰
        "spark_color": (180, 230, 255),
        "guitar_shape": "modern_v",
        "headstock_style": "futuristic",
        "finish": "gloss",
        # 差异化装饰
        "decal_type": "circuit",              # 电路纹路
        "decal_color": (100, 200, 255),
        "string_glow": True,
        "string_glow_color": (80, 200, 255),  # 电蓝琴弦
        "exhaust_style": "electric_arc",      # 电弧形尾焰
        "speaker_effect": "scanning",         # 扫描线效果
        "body_pattern": "circuit_lines",      # 电路板纹路
        "pattern_color": (80, 180, 255),
        "led_strips": True,                   # LED灯带
        "led_color": (0, 200, 255),
    },
    
    # ========== 4. 黄金圣歌 - 土豪金 + 圣光光环 + 金粒子 ==========
    "golden": {
        "name": "黄金圣歌",
        "body_main": (200, 170, 80),          # 亮金主色！
        "body_secondary": (160, 135, 60),
        "body_accent": (230, 200, 100),
        "body_edge": (255, 230, 140),
        "body_shadow": (100, 80, 30),
        "metal_highlight": (255, 245, 180),
        "metal_brush": (200, 175, 100),
        "chrome": (255, 250, 200),
        "worn_metal": (180, 155, 90),
        "neon_primary": (255, 220, 80),       # 金光
        "neon_secondary": (255, 200, 50),
        "neon_tertiary": (220, 180, 60),
        "glow_color": (255, 230, 100),
        "speaker_cone": (120, 100, 50),
        "speaker_surround": (150, 128, 68),
        "speaker_dust_cap": (180, 155, 88),
        "speaker_rim": (210, 185, 115),
        "speaker_grill": (80, 68, 35),
        "cabinet_tolex": (100, 85, 45),
        "cabinet_corner": (190, 165, 100),
        "fretboard": (60, 45, 20),
        "fretboard_inlay": (255, 248, 220),
        "fret_wire": (240, 225, 180),
        "string_steel": (250, 240, 210),
        "string_wound": (220, 195, 140),
        "tuner_body": (180, 155, 90),
        "tuner_button": (140, 120, 70),
        "pickup_cover": (120, 105, 60),
        "pickup_pole": (210, 190, 130),
        "bridge_metal": (240, 220, 165),
        "knob_body": (150, 130, 78),
        "knob_marker": (255, 250, 220),
        "exhaust_core": (255, 255, 200),      # 圣光核心
        "exhaust_outer": (255, 200, 50),      # 金色外焰
        "spark_color": (255, 245, 180),
        "guitar_shape": "les_paul",
        "headstock_style": "classic",
        "finish": "gloss",
        # 差异化装饰
        "decal_type": "halo",                 # 圣光光环
        "decal_color": (255, 230, 100),
        "string_glow": True,
        "string_glow_color": (255, 220, 120), # 金色琴弦
        "exhaust_style": "holy_flame",        # 圣焰尾焰
        "speaker_effect": "radiant",          # 光芒四射
        "body_pattern": "ornate_scroll",      # 华丽卷纹
        "pattern_color": (255, 235, 150),
        "particle_effect": "golden_dust",     # 金色粒子
    },
    
    # ========== 5. 迷幻紫雾 - 荧光紫 + 漩涡图案 + 迷幻波纹 ==========
    "psychedelic": {
        "name": "迷幻紫雾",
        "body_main": (160, 50, 200),          # 荧光紫主色！
        "body_secondary": (120, 35, 160),
        "body_accent": (200, 80, 240),
        "body_edge": (230, 120, 255),
        "body_shadow": (80, 25, 110),
        "metal_highlight": (240, 180, 255),
        "metal_brush": (180, 100, 220),
        "chrome": (250, 210, 255),
        "worn_metal": (140, 90, 160),
        "neon_primary": (255, 100, 255),      # 紫粉荧光
        "neon_secondary": (200, 50, 255),
        "neon_tertiary": (255, 150, 220),
        "glow_color": (255, 120, 255),
        "speaker_cone": (100, 45, 130),
        "speaker_surround": (130, 65, 165),
        "speaker_dust_cap": (165, 90, 200),
        "speaker_rim": (195, 120, 230),
        "speaker_grill": (65, 30, 90),
        "cabinet_tolex": (80, 35, 105),
        "cabinet_corner": (145, 95, 175),
        "fretboard": (50, 25, 70),
        "fretboard_inlay": (245, 210, 255),
        "fret_wire": (220, 180, 240),
        "string_steel": (235, 210, 250),
        "string_wound": (200, 160, 220),
        "tuner_body": (120, 75, 150),
        "tuner_button": (95, 60, 120),
        "pickup_cover": (90, 50, 120),
        "pickup_pole": (170, 120, 200),
        "bridge_metal": (200, 155, 230),
        "knob_body": (110, 70, 140),
        "knob_marker": (250, 225, 255),
        "exhaust_core": (255, 180, 255),      # 迷幻核心
        "exhaust_outer": (180, 50, 220),      # 紫雾外焰
        "spark_color": (255, 160, 255),
        "guitar_shape": "flying_v",
        "headstock_style": "wavy",
        "finish": "gloss",
        # 差异化装饰
        "decal_type": "spiral",               # 漩涡图案
        "decal_color": (255, 130, 255),
        "string_glow": True,
        "string_glow_color": (255, 100, 255), # 紫粉琴弦
        "exhaust_style": "wavy",              # 波纹形尾焰
        "speaker_effect": "hypnotic",         # 催眠脉动
        "body_pattern": "psychedelic_swirl",  # 迷幻漩涡
        "pattern_color": (200, 80, 255),
        "aura_effect": True,                  # 光晕效果
        "aura_colors": [(255, 100, 200), (200, 50, 255), (255, 150, 255)],
    },
    
    # ========== 6. 核废料 - 荧光绿 + 辐射符号 + 毒雾尾焰 ==========
    "toxic": {
        "name": "核废料",
        "body_main": (50, 200, 50),           # 荧光绿主色！
        "body_secondary": (35, 160, 35),
        "body_accent": (80, 240, 80),
        "body_edge": (120, 255, 120),
        "body_shadow": (25, 100, 25),
        "metal_highlight": (180, 255, 180),
        "metal_brush": (100, 200, 100),
        "chrome": (200, 255, 200),
        "worn_metal": (90, 150, 90),
        "neon_primary": (100, 255, 100),      # 荧光绿
        "neon_secondary": (180, 255, 80),
        "neon_tertiary": (60, 220, 60),
        "glow_color": (120, 255, 120),
        "speaker_cone": (50, 120, 50),
        "speaker_surround": (70, 155, 70),
        "speaker_dust_cap": (95, 190, 95),
        "speaker_rim": (130, 220, 130),
        "speaker_grill": (35, 80, 35),
        "cabinet_tolex": (40, 100, 40),
        "cabinet_corner": (100, 180, 100),
        "fretboard": (25, 60, 25),
        "fretboard_inlay": (210, 255, 210),
        "fret_wire": (180, 230, 180),
        "string_steel": (215, 245, 215),
        "string_wound": (170, 210, 170),
        "tuner_body": (80, 140, 80),
        "tuner_button": (60, 110, 60),
        "pickup_cover": (55, 110, 55),
        "pickup_pole": (130, 190, 130),
        "bridge_metal": (165, 220, 165),
        "knob_body": (70, 125, 70),
        "knob_marker": (225, 255, 225),
        "exhaust_core": (150, 255, 100),      # 毒绿核心
        "exhaust_outer": (50, 180, 30),       # 暗绿毒雾
        "spark_color": (130, 255, 100),
        "guitar_shape": "warlock",
        "headstock_style": "spiked",
        "finish": "matte",
        # 差异化装饰
        "decal_type": "radiation",            # 辐射符号
        "decal_color": (255, 255, 0),         # 警告黄
        "string_glow": True,
        "string_glow_color": (100, 255, 100), # 毒绿琴弦
        "exhaust_style": "toxic_cloud",       # 毒雾形尾焰
        "speaker_effect": "geiger",           # 盖革计数器效果
        "body_pattern": "hazard_stripes",     # 警示条纹
        "pattern_color": (255, 200, 0),
        "drip_effect": True,                  # 滴落效果
        "drip_color": (80, 255, 80),
    },
    
    # ========== 7. 冰封圣咏 - 冰蓝白 + 冰晶纹路 + 冰霜粒子 ==========
    "frost": {
        "name": "冰封圣咏",
        "body_main": (180, 220, 255),         # 冰蓝白主色！
        "body_secondary": (150, 195, 240),
        "body_accent": (200, 235, 255),
        "body_edge": (230, 248, 255),
        "body_shadow": (100, 150, 200),
        "metal_highlight": (245, 252, 255),
        "metal_brush": (200, 230, 250),
        "chrome": (250, 255, 255),
        "worn_metal": (170, 200, 230),
        "neon_primary": (150, 220, 255),      # 冰晶蓝
        "neon_secondary": (200, 245, 255),
        "neon_tertiary": (120, 200, 250),
        "glow_color": (180, 235, 255),
        "speaker_cone": (130, 175, 215),
        "speaker_surround": (160, 200, 235),
        "speaker_dust_cap": (190, 225, 250),
        "speaker_rim": (215, 240, 255),
        "speaker_grill": (90, 135, 175),
        "cabinet_tolex": (110, 155, 200),
        "cabinet_corner": (180, 215, 245),
        "fretboard": (80, 120, 160),
        "fretboard_inlay": (250, 255, 255),
        "fret_wire": (230, 245, 255),
        "string_steel": (245, 252, 255),
        "string_wound": (210, 230, 250),
        "tuner_body": (160, 195, 230),
        "tuner_button": (135, 170, 210),
        "pickup_cover": (125, 170, 215),
        "pickup_pole": (195, 225, 250),
        "bridge_metal": (225, 245, 255),
        "knob_body": (150, 190, 225),
        "knob_marker": (255, 255, 255),
        "exhaust_core": (230, 250, 255),      # 冰晶核心
        "exhaust_outer": (100, 180, 255),     # 冰蓝外焰
        "spark_color": (200, 240, 255),
        "guitar_shape": "iceman",
        "headstock_style": "crystalline",
        "finish": "gloss",
        # 差异化装饰
        "decal_type": "ice_crystal",          # 冰晶图案
        "decal_color": (200, 240, 255),
        "string_glow": True,
        "string_glow_color": (180, 230, 255), # 冰蓝琴弦
        "exhaust_style": "frost_breath",      # 冰霜吐息
        "speaker_effect": "frozen",           # 冰冻效果
        "body_pattern": "frost_cracks",       # 冰裂纹
        "pattern_color": (220, 245, 255),
        "particle_effect": "snowflakes",      # 雪花粒子
        "shimmer_effect": True,               # 闪烁效果
    },
    
    # ========== 8. 地狱烈焰 - 熔岩橙 + 裂纹岩浆 + 炽焰尾焰 ==========
    "hellfire": {
        "name": "地狱烈焰",
        "body_main": (220, 100, 20),          # 熔岩橙主色！
        "body_secondary": (180, 70, 15),
        "body_accent": (250, 140, 40),
        "body_edge": (255, 180, 80),
        "body_shadow": (120, 50, 10),
        "metal_highlight": (255, 210, 140),
        "metal_brush": (220, 140, 70),
        "chrome": (255, 230, 180),
        "worn_metal": (180, 120, 70),
        "neon_primary": (255, 150, 30),       # 烈焰橙
        "neon_secondary": (255, 200, 60),
        "neon_tertiary": (255, 100, 20),
        "glow_color": (255, 160, 50),
        "speaker_cone": (140, 75, 30),
        "speaker_surround": (175, 100, 45),
        "speaker_dust_cap": (210, 130, 65),
        "speaker_rim": (240, 165, 95),
        "speaker_grill": (100, 55, 25),
        "cabinet_tolex": (120, 65, 30),
        "cabinet_corner": (200, 140, 80),
        "fretboard": (60, 35, 18),
        "fretboard_inlay": (255, 235, 200),
        "fret_wire": (240, 210, 170),
        "string_steel": (250, 235, 210),
        "string_wound": (220, 185, 140),
        "tuner_body": (160, 105, 60),
        "tuner_button": (130, 85, 50),
        "pickup_cover": (120, 75, 40),
        "pickup_pole": (200, 150, 100),
        "bridge_metal": (235, 195, 145),
        "knob_body": (145, 95, 55),
        "knob_marker": (255, 245, 220),
        "exhaust_core": (255, 255, 150),      # 白炽核心
        "exhaust_outer": (255, 100, 20),      # 炽焰外焰
        "spark_color": (255, 200, 100),
        "guitar_shape": "bc_rich",
        "headstock_style": "demonic",
        "finish": "satin",
        # 差异化装饰
        "decal_type": "lava_cracks",          # 熔岩裂纹
        "decal_color": (255, 200, 50),
        "string_glow": True,
        "string_glow_color": (255, 150, 50),  # 炽焰琴弦
        "exhaust_style": "inferno",           # 地狱烈焰
        "speaker_effect": "eruption",         # 喷发效果
        "body_pattern": "magma_veins",        # 岩浆脉络
        "pattern_color": (255, 180, 80),
        "ember_effect": True,                 # 余烬效果
        "ember_color": (255, 120, 30),
    },
    
    # ========== 9. 午夜蓝调 - 深邃午夜蓝 + 星星点缀 + 月光尾焰 ==========
    "midnight": {
        "name": "午夜蓝调",
        "body_main": (15, 25, 80),            # 深邃蓝主色
        "body_secondary": (10, 18, 60),
        "body_accent": (25, 40, 110),
        "body_edge": (45, 65, 150),
        "body_shadow": (5, 10, 40),
        "metal_highlight": (100, 120, 200),
        "metal_brush": (60, 80, 140),
        "chrome": (140, 160, 220),
        "worn_metal": (80, 95, 150),
        "neon_primary": (80, 100, 220),       # 午夜蓝光
        "neon_secondary": (120, 140, 255),
        "neon_tertiary": (60, 80, 180),
        "glow_color": (90, 110, 230),
        "speaker_cone": (25, 40, 95),
        "speaker_surround": (40, 58, 125),
        "speaker_dust_cap": (60, 80, 155),
        "speaker_rim": (90, 115, 190),
        "speaker_grill": (18, 28, 70),
        "cabinet_tolex": (22, 35, 85),
        "cabinet_corner": (75, 100, 170),
        "fretboard": (15, 25, 60),
        "fretboard_inlay": (180, 195, 240),
        "fret_wire": (160, 175, 220),
        "string_steel": (195, 208, 245),
        "string_wound": (150, 168, 210),
        "tuner_body": (55, 75, 130),
        "tuner_button": (45, 60, 105),
        "pickup_cover": (40, 58, 110),
        "pickup_pole": (95, 115, 175),
        "bridge_metal": (135, 155, 210),
        "knob_body": (50, 68, 120),
        "knob_marker": (200, 215, 255),
        "exhaust_core": (200, 220, 255),      # 月光核心
        "exhaust_outer": (60, 90, 200),       # 午夜蓝外焰
        "spark_color": (180, 200, 255),
        "guitar_shape": "strat_style",
        "headstock_style": "sleek",
        "finish": "gloss",
        # 差异化装饰
        "decal_type": "stars",                # 星星图案
        "decal_color": (255, 255, 220),
        "string_glow": True,
        "string_glow_color": (150, 180, 255), # 月光琴弦
        "exhaust_style": "moonbeam",          # 月光尾焰
        "speaker_effect": "starlight",        # 星光闪烁
        "body_pattern": "constellation",      # 星座图案
        "pattern_color": (180, 200, 255),
        "star_field": True,                   # 星空背景
        "moon_phase": "crescent",             # 新月装饰
    },
    
    # ========== 10. 彩虹桥 - 渐变彩虹 + 棱镜光芒 + 七彩尾焰 ==========
    "rainbow": {
        "name": "彩虹桥",
        "body_main": (60, 60, 65),            # 深灰底色
        "body_secondary": (45, 45, 50),
        "body_accent": (80, 80, 88),
        "body_edge": (110, 110, 120),
        "body_shadow": (25, 25, 28),
        "metal_highlight": (160, 160, 175),
        "metal_brush": (100, 100, 112),
        "chrome": (190, 190, 205),
        "worn_metal": (120, 118, 125),
        "neon_primary": (255, 80, 80),        # 彩虹红
        "neon_secondary": (80, 255, 80),      # 彩虹绿
        "neon_tertiary": (80, 80, 255),       # 彩虹蓝
        "glow_color": (255, 200, 100),        # 彩虹黄
        "speaker_cone": (50, 50, 55),
        "speaker_surround": (70, 70, 78),
        "speaker_dust_cap": (95, 95, 105),
        "speaker_rim": (130, 130, 145),
        "speaker_grill": (35, 35, 40),
        "cabinet_tolex": (42, 42, 48),
        "cabinet_corner": (110, 110, 125),
        "fretboard": (40, 38, 45),
        "fretboard_inlay": (220, 220, 235),
        "fret_wire": (195, 195, 212),
        "string_steel": (225, 225, 240),
        "string_wound": (180, 180, 200),
        "tuner_body": (80, 80, 90),
        "tuner_button": (62, 62, 72),
        "pickup_cover": (58, 58, 68),
        "pickup_pole": (120, 120, 135),
        "bridge_metal": (165, 165, 185),
        "knob_body": (70, 70, 82),
        "knob_marker": (235, 235, 250),
        "exhaust_core": (255, 255, 255),      # 纯白核心
        "exhaust_outer": (255, 180, 100),     # 彩虹外焰
        "spark_color": (255, 220, 200),
        "guitar_shape": "superstrat",
        "headstock_style": "reverse",
        "finish": "gloss",
        "special_effect": "rainbow_gradient",  # 特殊效果标记
        # 差异化装饰
        "decal_type": "prism",                # 棱镜图案
        "decal_color": (255, 255, 255),
        "string_glow": True,
        "string_glow_color": (255, 255, 255), # 白光琴弦(会做彩虹处理)
        "exhaust_style": "rainbow_trail",     # 彩虹尾迹
        "speaker_effect": "disco",            # 迪斯科灯效
        "body_pattern": "rainbow_stripes",    # 彩虹条纹
        "rainbow_colors": [(255, 0, 0), (255, 127, 0), (255, 255, 0), 
                           (0, 255, 0), (0, 127, 255), (75, 0, 130), (148, 0, 211)],
        "prism_effect": True,                 # 棱镜分光
    },
    
    # ========== 11. 蒸汽朋克 - 黄铜 + 齿轮装饰 + 蒸汽尾焰 ==========
    "steampunk": {
        "name": "蒸汽朋克",
        "body_main": (165, 120, 60),          # 黄铜主色！
        "body_secondary": (140, 100, 50),
        "body_accent": (190, 145, 80),
        "body_edge": (220, 175, 110),
        "body_shadow": (90, 65, 35),
        "metal_highlight": (245, 215, 160),
        "metal_brush": (190, 155, 100),
        "chrome": (255, 235, 190),
        "worn_metal": (170, 140, 95),
        "neon_primary": (220, 170, 80),       # 黄铜光
        "neon_secondary": (255, 200, 100),
        "neon_tertiary": (200, 150, 70),
        "glow_color": (230, 185, 100),
        "speaker_cone": (120, 95, 55),
        "speaker_surround": (150, 120, 75),
        "speaker_dust_cap": (180, 148, 100),
        "speaker_rim": (210, 180, 130),
        "speaker_grill": (85, 68, 42),
        "cabinet_tolex": (105, 82, 52),
        "cabinet_corner": (190, 160, 115),
        "fretboard": (70, 52, 30),
        "fretboard_inlay": (250, 235, 205),
        "fret_wire": (230, 210, 175),
        "string_steel": (245, 235, 215),
        "string_wound": (210, 188, 150),
        "tuner_body": (165, 138, 95),
        "tuner_button": (140, 115, 78),
        "pickup_cover": (115, 95, 62),
        "pickup_pole": (195, 168, 125),
        "bridge_metal": (230, 205, 165),
        "knob_body": (145, 120, 82),
        "knob_marker": (255, 245, 225),
        "exhaust_core": (255, 255, 220),      # 蒸汽白核心
        "exhaust_outer": (200, 180, 140),     # 蒸汽黄外焰
        "spark_color": (240, 220, 180),
        "guitar_shape": "resonator",
        "headstock_style": "ornate",
        "finish": "aged",
        # 差异化装饰
        "decal_type": "gears",                # 齿轮图案
        "decal_color": (180, 150, 100),
        "string_glow": False,                 # 蒸汽朋克不发光
        "exhaust_style": "steam_puff",        # 蒸汽喷射
        "speaker_effect": "clockwork",        # 钟表机械
        "body_pattern": "rivets",             # 铆钉图案
        "pattern_color": (200, 170, 120),
        "gear_decorations": True,             # 齿轮装饰
        "pipe_vents": True,                   # 管道通风口
        "brass_trim": True,                   # 黄铜镶边
    },
    
    # ========== 12. 星际朋克 - 星云紫 + 星座图案 + 星尘尾焰 ==========
    "starpunk": {
        "name": "星际朋克",
        "body_main": (100, 50, 150),          # 星云紫主色
        "body_secondary": (80, 40, 120),
        "body_accent": (130, 70, 185),
        "body_edge": (170, 100, 220),
        "body_shadow": (50, 25, 80),
        "metal_highlight": (210, 160, 250),
        "metal_brush": (150, 100, 195),
        "chrome": (230, 195, 255),
        "worn_metal": (130, 95, 170),
        "neon_primary": (255, 100, 200),      # 星云粉
        "neon_secondary": (150, 100, 255),    # 星云紫
        "neon_tertiary": (255, 150, 220),
        "glow_color": (240, 130, 220),
        "speaker_cone": (80, 50, 115),
        "speaker_surround": (110, 72, 150),
        "speaker_dust_cap": (145, 98, 188),
        "speaker_rim": (180, 130, 220),
        "speaker_grill": (55, 35, 82),
        "cabinet_tolex": (68, 42, 100),
        "cabinet_corner": (150, 110, 195),
        "fretboard": (45, 30, 70),
        "fretboard_inlay": (235, 210, 255),
        "fret_wire": (210, 185, 240),
        "string_steel": (230, 215, 250),
        "string_wound": (195, 170, 225),
        "tuner_body": (115, 80, 155),
        "tuner_button": (92, 65, 130),
        "pickup_cover": (85, 58, 125),
        "pickup_pole": (160, 120, 200),
        "bridge_metal": (200, 165, 235),
        "knob_body": (105, 75, 145),
        "knob_marker": (245, 230, 255),
        "exhaust_core": (255, 200, 255),      # 星云粉核心
        "exhaust_outer": (150, 80, 220),      # 星紫外焰
        "spark_color": (230, 180, 255),
        "guitar_shape": "space_explorer",
        "headstock_style": "alien",
        "finish": "gloss",
        # 差异化装饰
        "decal_type": "nebula",               # 星云图案
        "decal_color": (255, 150, 220),
        "string_glow": True,
        "string_glow_color": (200, 150, 255), # 星紫琴弦
        "exhaust_style": "stardust",          # 星尘尾迹
        "speaker_effect": "warp",             # 曲速效果
        "body_pattern": "constellation",      # 星座图案
        "pattern_color": (255, 200, 255),
        "nebula_clouds": True,                # 星云云雾
        "star_particles": True,               # 星星粒子
        "comet_trail": True,                  # 彗星尾迹
    },
}


# ============================================================
#   差异化装饰元素绘制函数
# ============================================================
def _draw_theme_decorations(surface: pygame.Surface, cx: int, cy: int,
                            body_width: int, body_length: int, theme: dict,
                            scale: float, t: float, tilt_angle: float,
                            body_points: list) -> None:
    """根据主题绘制差异化装饰元素"""
    cos_a = math.cos(tilt_angle)
    sin_a = math.sin(tilt_angle)
    
    def rotate_point(px, py):
        dx, dy = px - cx, py - cy
        return (int(cx + dx * cos_a - dy * sin_a),
                int(cy + dx * sin_a + dy * cos_a))
    
    decal_type = theme.get("decal_type", None)
    decal_color = theme.get("decal_color", (255, 255, 255))
    pattern_type = theme.get("body_pattern", None)
    pattern_color = theme.get("pattern_color", (200, 200, 200))
    
    # ========== 琴身图案 ==========
    if decal_type == "skull":
        # 骷髅图案
        _draw_skull_decal(surface, cx, cy, scale, decal_color, t, tilt_angle)
    elif decal_type == "blood_splatter":
        # 血迹飞溅
        _draw_blood_splatter(surface, cx, cy, scale, decal_color, t, tilt_angle)
    elif decal_type == "circuit":
        # 电路纹路
        _draw_circuit_pattern(surface, cx, cy, body_width, body_length, scale, decal_color, t, tilt_angle)
    elif decal_type == "halo":
        # 圣光光环
        _draw_halo_effect(surface, cx, cy, scale, decal_color, t)
    elif decal_type == "spiral":
        # 漩涡图案
        _draw_spiral_pattern(surface, cx, cy, scale, decal_color, t, tilt_angle)
    elif decal_type == "radiation":
        # 辐射符号
        _draw_radiation_symbol(surface, cx, cy, scale, decal_color, t, tilt_angle)
    elif decal_type == "ice_crystal":
        # 冰晶图案
        _draw_ice_crystals(surface, cx, cy, scale, decal_color, t, tilt_angle)
    elif decal_type == "lava_cracks":
        # 熔岩裂纹
        _draw_lava_cracks(surface, cx, cy, body_width, scale, decal_color, t, tilt_angle)
    elif decal_type == "stars":
        # 星星点缀
        _draw_star_field(surface, cx, cy, body_width, body_length, scale, decal_color, t, tilt_angle)
    elif decal_type == "prism":
        # 棱镜效果
        _draw_prism_effect(surface, cx, cy, scale, t, tilt_angle)
    elif decal_type == "gears":
        # 齿轮装饰
        _draw_gear_decorations(surface, cx, cy, scale, decal_color, t, tilt_angle)
    elif decal_type == "nebula":
        # 星云图案
        _draw_nebula_effect(surface, cx, cy, scale, decal_color, t, tilt_angle)
    
    # ========== 特殊图案纹路 ==========
    if pattern_type == "cracks":
        _draw_crack_pattern(surface, cx, cy, body_width, scale, pattern_color, tilt_angle)
    elif pattern_type == "hazard_stripes":
        _draw_hazard_stripes(surface, cx, cy, body_width, scale, pattern_color, tilt_angle)
    elif pattern_type == "frost_cracks":
        _draw_frost_cracks(surface, cx, cy, body_width, scale, pattern_color, tilt_angle)
    elif pattern_type == "magma_veins":
        _draw_magma_veins(surface, cx, cy, body_width, scale, pattern_color, t, tilt_angle)
    elif pattern_type == "rainbow_stripes":
        rainbow_colors = theme.get("rainbow_colors", [(255,0,0),(0,255,0),(0,0,255)])
        _draw_rainbow_stripes(surface, cx, cy, body_width, scale, rainbow_colors, t, tilt_angle)
    elif pattern_type == "rivets":
        _draw_rivets(surface, cx, cy, body_width, body_length, scale, pattern_color, tilt_angle)


def _draw_skull_decal(surface: pygame.Surface, cx: int, cy: int, 
                      scale: float, color: tuple, t: float, tilt: float) -> None:
    """绘制骷髅图案"""
    cos_a, sin_a = math.cos(tilt), math.sin(tilt)
    def rot(px, py):
        dx, dy = px - cx, py - cy
        return (int(cx + dx*cos_a - dy*sin_a), int(cy + dx*sin_a + dy*cos_a))
    
    skull_size = int(12 * scale)
    # 骷髅轮廓 - 简化版
    # 头骨
    skull_cx, skull_cy = cx, cy + int(5 * scale)
    alpha = int(80 + 30 * math.sin(t * 2))
    
    # 头骨外形
    skull_pts = []
    for i in range(8):
        angle = i * math.pi / 4
        r = skull_size * (0.9 + 0.1 * math.sin(angle * 2))
        px = skull_cx + int(r * math.cos(angle))
        py = skull_cy + int(r * 0.8 * math.sin(angle))
        skull_pts.append(rot(px, py))
    
    pygame.draw.polygon(surface, (*color[:3], alpha), skull_pts)
    pygame.draw.polygon(surface, (*color[:3], alpha + 40), skull_pts, 1)
    
    # 眼睛
    eye_offset = int(4 * scale)
    eye_size = int(3 * scale)
    left_eye = rot(skull_cx - eye_offset, skull_cy - int(2 * scale))
    right_eye = rot(skull_cx + eye_offset, skull_cy - int(2 * scale))
    pygame.draw.circle(surface, (0, 0, 0), left_eye, eye_size)
    pygame.draw.circle(surface, (0, 0, 0), right_eye, eye_size)
    
    # 鼻子
    nose = rot(skull_cx, skull_cy + int(2 * scale))
    pygame.draw.polygon(surface, (0, 0, 0), [
        nose,
        rot(skull_cx - int(2 * scale), skull_cy + int(4 * scale)),
        rot(skull_cx + int(2 * scale), skull_cy + int(4 * scale))
    ])


def _draw_blood_splatter(surface: pygame.Surface, cx: int, cy: int,
                         scale: float, color: tuple, t: float, tilt: float) -> None:
    """绘制血迹飞溅效果"""
    cos_a, sin_a = math.cos(tilt), math.sin(tilt)
    def rot(px, py):
        dx, dy = px - cx, py - cy
        return (int(cx + dx*cos_a - dy*sin_a), int(cy + dx*sin_a + dy*cos_a))
    
    random.seed(42)  # 固定种子确保一致性
    alpha = int(100 + 30 * math.sin(t * 1.5))
    
    for _ in range(8):
        # 随机血滴位置
        ox = random.randint(-int(15*scale), int(15*scale))
        oy = random.randint(-int(20*scale), int(20*scale))
        splat_size = random.randint(int(2*scale), int(5*scale))
        
        pos = rot(cx + ox, cy + oy)
        pygame.draw.circle(surface, (*color[:3], alpha), pos, splat_size)
        
        # 血滴拖尾
        for j in range(3):
            drip_y = oy + (j + 1) * int(3 * scale)
            drip_pos = rot(cx + ox, cy + drip_y)
            drip_size = max(1, splat_size - j)
            pygame.draw.circle(surface, (*color[:3], alpha - j*20), drip_pos, drip_size)


def _draw_circuit_pattern(surface: pygame.Surface, cx: int, cy: int,
                          body_width: int, body_length: int, scale: float,
                          color: tuple, t: float, tilt: float) -> None:
    """绘制电路纹路"""
    cos_a, sin_a = math.cos(tilt), math.sin(tilt)
    def rot(px, py):
        dx, dy = px - cx, py - cy
        return (int(cx + dx*cos_a - dy*sin_a), int(cy + dx*sin_a + dy*cos_a))
    
    # 动态闪烁
    pulse = 0.5 + 0.5 * math.sin(t * 4)
    alpha = int(60 + 80 * pulse)
    line_color = (*color[:3], alpha)
    node_color = (*color[:3], int(alpha * 1.3))
    
    # 水平线路
    for i in range(-2, 3):
        y_off = i * int(8 * scale)
        start = rot(cx - int(12 * scale), cy + y_off)
        end = rot(cx + int(12 * scale), cy + y_off)
        pygame.draw.line(surface, line_color, start, end, max(1, int(scale)))
        
        # 节点
        for j in [-1, 0, 1]:
            node = rot(cx + j * int(8 * scale), cy + y_off)
            pygame.draw.circle(surface, node_color, node, max(2, int(2 * scale)))
    
    # 垂直连接
    for j in [-1, 0, 1]:
        x_off = j * int(8 * scale)
        for i in range(-1, 2):
            y1 = i * int(8 * scale)
            y2 = (i + 1) * int(8 * scale)
            start = rot(cx + x_off, cy + y1)
            end = rot(cx + x_off, cy + y2)
            pygame.draw.line(surface, line_color, start, end, max(1, int(scale)))


def _draw_halo_effect(surface: pygame.Surface, cx: int, cy: int,
                      scale: float, color: tuple, t: float) -> None:
    """绘制圣光光环效果"""
    # 多层光环
    for i in range(3):
        radius = int((15 + i * 8) * scale)
        alpha = int((60 - i * 15) * (0.7 + 0.3 * math.sin(t * 2 + i)))
        pygame.draw.circle(surface, (*color[:3], alpha), (cx, cy), radius, max(1, int(2 * scale)))
    
    # 光芒射线
    ray_count = 8
    for i in range(ray_count):
        angle = i * 2 * math.pi / ray_count + t * 0.5
        inner_r = int(10 * scale)
        outer_r = int(25 * scale + 5 * math.sin(t * 3 + i))
        start = (cx + int(inner_r * math.cos(angle)), cy + int(inner_r * math.sin(angle)))
        end = (cx + int(outer_r * math.cos(angle)), cy + int(outer_r * math.sin(angle)))
        alpha = int(80 + 40 * math.sin(t * 2 + i))
        pygame.draw.line(surface, (*color[:3], alpha), start, end, max(1, int(scale)))


def _draw_spiral_pattern(surface: pygame.Surface, cx: int, cy: int,
                         scale: float, color: tuple, t: float, tilt: float) -> None:
    """绘制漩涡图案"""
    # 旋转的漩涡
    points = []
    for i in range(40):
        angle = i * 0.3 + t * 2
        r = i * 0.5 * scale
        px = cx + int(r * math.cos(angle))
        py = cy + int(r * math.sin(angle))
        points.append((px, py))
    
    if len(points) > 1:
        alpha = int(80 + 30 * math.sin(t * 2))
        pygame.draw.lines(surface, (*color[:3], alpha), False, points, max(1, int(2 * scale)))


def _draw_radiation_symbol(surface: pygame.Surface, cx: int, cy: int,
                           scale: float, color: tuple, t: float, tilt: float) -> None:
    """绘制辐射符号"""
    cos_a, sin_a = math.cos(tilt), math.sin(tilt)
    def rot(px, py):
        dx, dy = px - cx, py - cy
        return (int(cx + dx*cos_a - dy*sin_a), int(cy + dx*sin_a + dy*cos_a))
    
    # 脉动效果
    pulse = 0.8 + 0.2 * math.sin(t * 3)
    alpha = int(120 * pulse)
    
    # 中心圆
    center_r = int(4 * scale)
    pygame.draw.circle(surface, (*color[:3], alpha), (cx, cy), center_r)
    
    # 三个扇形
    for i in range(3):
        base_angle = i * 2 * math.pi / 3 + t * 0.3
        inner_r = int(6 * scale)
        outer_r = int(14 * scale)
        arc_width = math.pi / 4
        
        # 绘制扇形
        pts = []
        for j in range(8):
            a = base_angle - arc_width/2 + arc_width * j / 7
            pts.append(rot(cx + int(inner_r * math.cos(a)), cy + int(inner_r * math.sin(a))))
        for j in range(8):
            a = base_angle + arc_width/2 - arc_width * j / 7
            pts.append(rot(cx + int(outer_r * math.cos(a)), cy + int(outer_r * math.sin(a))))
        
        if len(pts) >= 3:
            pygame.draw.polygon(surface, (*color[:3], alpha), pts)


def _draw_ice_crystals(surface: pygame.Surface, cx: int, cy: int,
                       scale: float, color: tuple, t: float, tilt: float) -> None:
    """绘制冰晶图案"""
    cos_a, sin_a = math.cos(tilt), math.sin(tilt)
    def rot(px, py):
        dx, dy = px - cx, py - cy
        return (int(cx + dx*cos_a - dy*sin_a), int(cy + dx*sin_a + dy*cos_a))
    
    alpha = int(100 + 30 * math.sin(t * 2))
    
    # 六角冰晶
    for i in range(6):
        angle = i * math.pi / 3
        length = int(12 * scale)
        end = rot(cx + int(length * math.cos(angle)), cy + int(length * math.sin(angle)))
        pygame.draw.line(surface, (*color[:3], alpha), (cx, cy), end, max(1, int(scale)))
        
        # 分支
        branch_len = int(5 * scale)
        mid_x = cx + int(length * 0.6 * math.cos(angle))
        mid_y = cy + int(length * 0.6 * math.sin(angle))
        for j in [-1, 1]:
            branch_angle = angle + j * math.pi / 4
            branch_end = rot(mid_x + int(branch_len * math.cos(branch_angle)),
                            mid_y + int(branch_len * math.sin(branch_angle)))
            mid_rot = rot(mid_x, mid_y)
            pygame.draw.line(surface, (*color[:3], alpha - 20), mid_rot, branch_end, max(1, int(scale * 0.7)))


def _draw_lava_cracks(surface: pygame.Surface, cx: int, cy: int,
                      body_width: int, scale: float, color: tuple, 
                      t: float, tilt: float) -> None:
    """绘制熔岩裂纹"""
    cos_a, sin_a = math.cos(tilt), math.sin(tilt)
    def rot(px, py):
        dx, dy = px - cx, py - cy
        return (int(cx + dx*cos_a - dy*sin_a), int(cy + dx*sin_a + dy*cos_a))
    
    random.seed(123)
    pulse = 0.7 + 0.3 * math.sin(t * 2)
    alpha = int(150 * pulse)
    
    # 主裂纹
    for _ in range(5):
        start_x = random.randint(-int(15*scale), int(15*scale))
        start_y = random.randint(-int(20*scale), int(20*scale))
        pts = [rot(cx + start_x, cy + start_y)]
        
        for i in range(4):
            dx = random.randint(-int(8*scale), int(8*scale))
            dy = random.randint(int(3*scale), int(8*scale))
            new_x = start_x + dx
            new_y = start_y + dy * (i + 1) // 2
            pts.append(rot(cx + new_x, cy + new_y))
        
        if len(pts) > 1:
            pygame.draw.lines(surface, (*color[:3], alpha), False, pts, max(1, int(2 * scale)))
            # 发光核心
            for pt in pts:
                glow_color = (255, 255, 200, int(alpha * 0.5))
                pygame.draw.circle(surface, glow_color, pt, max(1, int(scale)))


def _draw_star_field(surface: pygame.Surface, cx: int, cy: int,
                     body_width: int, body_length: int, scale: float,
                     color: tuple, t: float, tilt: float) -> None:
    """绘制星星点缀"""
    cos_a, sin_a = math.cos(tilt), math.sin(tilt)
    def rot(px, py):
        dx, dy = px - cx, py - cy
        return (int(cx + dx*cos_a - dy*sin_a), int(cy + dx*sin_a + dy*cos_a))
    
    random.seed(77)
    
    for i in range(12):
        ox = random.randint(-int(18*scale), int(18*scale))
        oy = random.randint(-int(25*scale), int(25*scale))
        star_pos = rot(cx + ox, cy + oy)
        
        # 闪烁
        twinkle = 0.5 + 0.5 * math.sin(t * 3 + i * 0.7)
        alpha = int(100 + 100 * twinkle)
        size = max(1, int((1 + twinkle) * scale))
        
        pygame.draw.circle(surface, (*color[:3], alpha), star_pos, size)
        
        # 十字光芒
        if twinkle > 0.7:
            for angle in [0, math.pi/2]:
                end1 = (star_pos[0] + int(size * 2 * math.cos(angle)), 
                        star_pos[1] + int(size * 2 * math.sin(angle)))
                end2 = (star_pos[0] - int(size * 2 * math.cos(angle)), 
                        star_pos[1] - int(size * 2 * math.sin(angle)))
                pygame.draw.line(surface, (*color[:3], alpha//2), end1, end2, 1)


def _draw_prism_effect(surface: pygame.Surface, cx: int, cy: int,
                       scale: float, t: float, tilt: float) -> None:
    """绘制棱镜分光效果"""
    # 彩虹色
    rainbow = [(255,0,0), (255,127,0), (255,255,0), (0,255,0), (0,127,255), (75,0,130), (148,0,211)]
    
    for i, color in enumerate(rainbow):
        angle = t + i * math.pi / 3.5
        length = int((10 + i * 2) * scale)
        end = (cx + int(length * math.cos(angle)), cy + int(length * math.sin(angle)))
        alpha = int(80 + 40 * math.sin(t * 2 + i))
        pygame.draw.line(surface, (*color, alpha), (cx, cy), end, max(1, int(2 * scale)))


def _draw_gear_decorations(surface: pygame.Surface, cx: int, cy: int,
                           scale: float, color: tuple, t: float, tilt: float) -> None:
    """绘制齿轮装饰"""
    cos_a, sin_a = math.cos(tilt), math.sin(tilt)
    def rot(px, py):
        dx, dy = px - cx, py - cy
        return (int(cx + dx*cos_a - dy*sin_a), int(cy + dx*sin_a + dy*cos_a))
    
    # 主齿轮
    gear_radius = int(10 * scale)
    teeth = 12
    alpha = int(120)
    
    gear_pts = []
    for i in range(teeth * 2):
        angle = i * math.pi / teeth + t * 0.5
        if i % 2 == 0:
            r = gear_radius
        else:
            r = gear_radius - int(3 * scale)
        px = cx + int(r * math.cos(angle))
        py = cy + int(r * math.sin(angle))
        gear_pts.append(rot(px, py))
    
    if len(gear_pts) >= 3:
        pygame.draw.polygon(surface, (*color[:3], alpha), gear_pts)
        pygame.draw.circle(surface, (*color[:3], alpha + 30), (cx, cy), int(3 * scale))
    
    # 小齿轮
    small_gear_pos = rot(cx + int(12 * scale), cy - int(8 * scale))
    small_r = int(5 * scale)
    small_teeth = 8
    small_pts = []
    for i in range(small_teeth * 2):
        angle = i * math.pi / small_teeth - t * 0.8
        if i % 2 == 0:
            r = small_r
        else:
            r = small_r - int(2 * scale)
        px = small_gear_pos[0] + int(r * math.cos(angle))
        py = small_gear_pos[1] + int(r * math.sin(angle))
        small_pts.append((px, py))
    
    if len(small_pts) >= 3:
        pygame.draw.polygon(surface, (*color[:3], alpha - 20), small_pts)


def _draw_nebula_effect(surface: pygame.Surface, cx: int, cy: int,
                        scale: float, color: tuple, t: float, tilt: float) -> None:
    """绘制星云效果"""
    random.seed(99)
    
    for i in range(6):
        ox = random.randint(-int(15*scale), int(15*scale))
        oy = random.randint(-int(20*scale), int(20*scale))
        
        # 呼吸效果
        pulse = 0.5 + 0.5 * math.sin(t * 1.5 + i * 0.5)
        size = int((5 + 3 * pulse) * scale)
        alpha = int(40 + 30 * pulse)
        
        # 渐变色云雾
        r = color[0] + random.randint(-30, 30)
        g = color[1] + random.randint(-30, 30)
        b = color[2] + random.randint(-30, 30)
        cloud_color = (max(0,min(255,r)), max(0,min(255,g)), max(0,min(255,b)), alpha)
        
        pygame.draw.circle(surface, cloud_color, (cx + ox, cy + oy), size)


def _draw_crack_pattern(surface: pygame.Surface, cx: int, cy: int,
                        body_width: int, scale: float, color: tuple, tilt: float) -> None:
    """绘制裂纹图案"""
    cos_a, sin_a = math.cos(tilt), math.sin(tilt)
    def rot(px, py):
        dx, dy = px - cx, py - cy
        return (int(cx + dx*cos_a - dy*sin_a), int(cy + dx*sin_a + dy*cos_a))
    
    random.seed(55)
    alpha = 80
    
    for _ in range(4):
        start = rot(cx + random.randint(-int(10*scale), int(10*scale)), 
                    cy + random.randint(-int(15*scale), int(15*scale)))
        pts = [start]
        for i in range(3):
            dx = random.randint(-int(6*scale), int(6*scale))
            dy = random.randint(int(2*scale), int(6*scale))
            pts.append((pts[-1][0] + dx, pts[-1][1] + dy))
        
        pygame.draw.lines(surface, (*color[:3], alpha), False, pts, 1)


def _draw_hazard_stripes(surface: pygame.Surface, cx: int, cy: int,
                         body_width: int, scale: float, color: tuple, tilt: float) -> None:
    """绘制警示条纹"""
    stripe_width = int(4 * scale)
    alpha = 100
    
    for i in range(-3, 4):
        x1 = cx - int(15 * scale) + i * stripe_width * 2
        x2 = x1 + stripe_width
        y1 = cy - int(5 * scale)
        y2 = cy + int(5 * scale)
        
        pts = [(x1, y1), (x2, y1), (x2 + stripe_width, y2), (x1 + stripe_width, y2)]
        pygame.draw.polygon(surface, (*color[:3], alpha), pts)


def _draw_frost_cracks(surface: pygame.Surface, cx: int, cy: int,
                       body_width: int, scale: float, color: tuple, tilt: float) -> None:
    """绘制冰裂纹"""
    random.seed(88)
    alpha = 70
    
    for _ in range(5):
        start = (cx + random.randint(-int(12*scale), int(12*scale)),
                 cy + random.randint(-int(18*scale), int(18*scale)))
        
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            length = random.randint(int(3*scale), int(8*scale))
            end = (start[0] + int(length * math.cos(angle)),
                   start[1] + int(length * math.sin(angle)))
            pygame.draw.line(surface, (*color[:3], alpha), start, end, 1)


def _draw_magma_veins(surface: pygame.Surface, cx: int, cy: int,
                      body_width: int, scale: float, color: tuple, 
                      t: float, tilt: float) -> None:
    """绘制岩浆脉络"""
    random.seed(111)
    pulse = 0.7 + 0.3 * math.sin(t * 2)
    alpha = int(120 * pulse)
    
    for _ in range(4):
        pts = []
        x = cx + random.randint(-int(12*scale), int(12*scale))
        y = cy - int(15 * scale)
        pts.append((x, y))
        
        for i in range(5):
            x += random.randint(-int(4*scale), int(4*scale))
            y += int(6 * scale)
            pts.append((x, y))
        
        if len(pts) > 1:
            pygame.draw.lines(surface, (*color[:3], alpha), False, pts, max(1, int(2 * scale)))


def _draw_rainbow_stripes(surface: pygame.Surface, cx: int, cy: int,
                          body_width: int, scale: float, colors: list,
                          t: float, tilt: float) -> None:
    """绘制彩虹条纹"""
    stripe_height = int(4 * scale)
    offset = int(t * 10) % (len(colors) * stripe_height)
    
    for i, color in enumerate(colors):
        y = cy - int(15 * scale) + i * stripe_height - offset
        if cy - int(20 * scale) <= y <= cy + int(20 * scale):
            alpha = 60
            pygame.draw.line(surface, (*color[:3], alpha), 
                            (cx - int(15*scale), y), 
                            (cx + int(15*scale), y), 
                            stripe_height)


def _draw_rivets(surface: pygame.Surface, cx: int, cy: int,
                 body_width: int, body_length: int, scale: float,
                 color: tuple, tilt: float) -> None:
    """绘制铆钉装饰"""
    cos_a, sin_a = math.cos(tilt), math.sin(tilt)
    def rot(px, py):
        dx, dy = px - cx, py - cy
        return (int(cx + dx*cos_a - dy*sin_a), int(cy + dx*sin_a + dy*cos_a))
    
    rivet_size = max(2, int(2 * scale))
    alpha = 150
    
    # 边缘铆钉
    positions = [
        (-15, -20), (-15, -10), (-15, 0), (-15, 10), (-15, 20),
        (15, -20), (15, -10), (15, 0), (15, 10), (15, 20),
    ]
    
    for ox, oy in positions:
        pos = rot(cx + int(ox * scale), cy + int(oy * scale))
        pygame.draw.circle(surface, (*color[:3], alpha), pos, rivet_size)
        # 高光
        highlight = (pos[0] - 1, pos[1] - 1)
        pygame.draw.circle(surface, (255, 255, 255, 80), highlight, max(1, rivet_size - 1))


def render_heavymetal_plane(surface: pygame.Surface, x: int, y: int, 
                            theme_name: str = "default", t: float = 0,
                            scale: float = 2.0) -> None:
    """
    渲染 HEAVY METAL 飞行吉他机体 - 完整展示版
    
    设计理念:
    - 完整的吉他造型：琴身+琴颈+琴头全部可见
    - 整体缩小并居中
    - 轻微倾斜增加动感
    """
    theme = HEAVYMETAL_THEMES.get(theme_name, HEAVYMETAL_THEMES["default"])
    cx, cy = int(x), int(y)
    
    # 大幅缩小整体比例，确保完整显示
    display_scale = scale * 0.5
    
    # 倾斜角度
    tilt_angle = -0.1  # 约6度
    cos_a = math.cos(tilt_angle)
    sin_a = math.sin(tilt_angle)
    
    def rotate_point(px, py, origin_x, origin_y):
        """绕原点旋转"""
        dx, dy = px - origin_x, py - origin_y
        return (
            int(origin_x + dx * cos_a - dy * sin_a),
            int(origin_y + dx * sin_a + dy * cos_a)
        )
    
    # 吉他各部分尺寸 - 更紧凑
    body_length = int(50 * display_scale)       # 琴身长度
    body_width = int(45 * display_scale)        # 琴身宽度  
    neck_length = int(40 * display_scale)       # 琴颈长度
    neck_width = int(10 * display_scale)        # 琴颈宽度
    headstock_length = int(18 * display_scale)  # 琴头长度
    speaker_size = int(22 * display_scale)      # 音箱尺寸
    
    # 计算吉他视觉中心
    # 琴头顶端到琴身底端的总高度
    total_guitar_height = headstock_length + neck_length + body_length
    
    # 让吉他视觉中心对准玩家中心
    # 视觉中心 = 玩家中心，所以琴身中心需要向下偏移
    # 琴身中心相对于吉他视觉中心的偏移 = (neck_length + headstock_length - body_length) / 2
    guitar_body_y = cy  # 琴身中心就在玩家中心
    
    # ============================================================
    #   第一层：音箱引擎 - 挂载在琴身两侧
    # ============================================================
    speaker_y = guitar_body_y + int(8 * display_scale)
    left_speaker = rotate_point(cx - int(38 * display_scale), speaker_y, cx, cy)
    right_speaker = rotate_point(cx + int(38 * display_scale), speaker_y, cx, cy)
    _draw_speaker_cabinet(surface, left_speaker[0], left_speaker[1], speaker_size, theme, t, display_scale, -1)
    _draw_speaker_cabinet(surface, right_speaker[0], right_speaker[1], speaker_size, theme, t, display_scale, 1)
    
    # ============================================================
    #   第二层：尾部推进火焰 (先画，在最底层)
    # ============================================================
    _draw_exhaust_rotated(surface, cx, guitar_body_y, body_length, theme, display_scale, t, tilt_angle, cx, cy)
    
    # ============================================================
    #   第三层：吉他琴身主体 - Flying V
    # ============================================================
    guitar_shape = theme.get("guitar_shape", "flying_v")
    body_points_raw = _get_guitar_body_points(cx, guitar_body_y, body_width, body_length, guitar_shape, display_scale)
    body_points = [rotate_point(p[0], p[1], cx, cy) for p in body_points_raw]
    
    # 琴身阴影
    shadow_offset = int(5 * display_scale)
    shadow_pts = [(p[0] + shadow_offset, p[1] + shadow_offset) for p in body_points]
    pygame.draw.polygon(surface, (*theme["body_shadow"][:3], 60), shadow_pts)
    
    # 琴身主体
    pygame.draw.polygon(surface, theme["body_main"], body_points)
    
    # 琴身内层
    inner_pts_raw = [(int(cx + (p[0] - cx) * 0.85), int(guitar_body_y + (p[1] - guitar_body_y) * 0.85)) for p in body_points_raw]
    inner_pts = [rotate_point(p[0], p[1], cx, cy) for p in inner_pts_raw]
    pygame.draw.polygon(surface, theme["body_secondary"], inner_pts)
    
    # 拉丝金属质感
    _draw_brushed_metal_texture_rotated(surface, cx, guitar_body_y, body_width, body_length, 
                                        theme, display_scale, tilt_angle)
    
    # 琴身边缘
    pygame.draw.polygon(surface, theme["body_edge"], body_points, int(2 * display_scale))
    
    # 内部装饰线
    accent_pts_raw = [(int(cx + (p[0] - cx) * 0.75), int(guitar_body_y + (p[1] - guitar_body_y) * 0.75)) for p in body_points_raw]
    accent_pts = [rotate_point(p[0], p[1], cx, cy) for p in accent_pts_raw]
    pygame.draw.polygon(surface, theme["body_accent"], accent_pts, 1)
    
    # ============================================================
    #   第四层：拾音器
    # ============================================================
    _draw_pickups_rotated(surface, cx, guitar_body_y, theme, display_scale, tilt_angle, cx, cy)
    
    # ============================================================
    #   第五层：琴桥与控制旋钮
    # ============================================================
    _draw_bridge_and_controls_rotated(surface, cx, guitar_body_y, theme, display_scale, t, tilt_angle, cx, cy)
    
    # ============================================================
    #   第六层：琴颈 - 从琴身向上延伸
    # ============================================================
    _draw_guitar_neck_rotated(surface, cx, guitar_body_y, body_length, neck_length, 
                              neck_width, theme, display_scale, t, tilt_angle, cx, cy)
    
    # ============================================================
    #   第七层：琴头 - 最顶端
    # ============================================================
    headstock_style = theme.get("headstock_style", "pointed")
    _draw_headstock_rotated(surface, cx, guitar_body_y, body_length, neck_length, 
                            headstock_length, theme, display_scale, headstock_style, t, tilt_angle, cx, cy)
    
    # ============================================================
    #   第八层：差异化装饰元素
    # ============================================================
    _draw_theme_decorations(surface, cx, guitar_body_y, body_width, body_length, 
                            theme, display_scale, t, tilt_angle, body_points)
    
    # ============================================================
    #   第九层：边缘轮廓微光
    # ============================================================
    glow_alpha = int(18 + 10 * math.sin(t * 2))
    pygame.draw.polygon(surface, (*theme["glow_color"][:3], glow_alpha), body_points, 2)


def _draw_headstock(surface: pygame.Surface, cx: int, cy: int, 
                    body_length: int, neck_length: int, theme: dict, 
                    scale: float, headstock_style: str, t: float) -> None:
    """绘制琴头 - 锐利凶悍"""
    headstock_y = cy - body_length // 2 - neck_length
    headstock_h = int(20 * scale)
    
    if headstock_style == "pointed":
        headstock_points = [
            (cx - int(24 * scale), headstock_y),
            (cx - int(30 * scale), headstock_y - headstock_h // 2),
            (cx - int(18 * scale), headstock_y - headstock_h),
            (cx, headstock_y - headstock_h - int(10 * scale)),
            (cx + int(18 * scale), headstock_y - headstock_h),
            (cx + int(30 * scale), headstock_y - headstock_h // 2),
            (cx + int(24 * scale), headstock_y),
        ]
    elif headstock_style == "sharp":
        headstock_points = [
            (cx - int(22 * scale), headstock_y),
            (cx - int(35 * scale), headstock_y - headstock_h),
            (cx - int(12 * scale), headstock_y - headstock_h - int(12 * scale)),
            (cx, headstock_y - headstock_h - int(8 * scale)),
            (cx + int(12 * scale), headstock_y - headstock_h - int(12 * scale)),
            (cx + int(35 * scale), headstock_y - headstock_h),
            (cx + int(22 * scale), headstock_y),
        ]
    elif headstock_style == "demonic":
        headstock_points = [
            (cx - int(20 * scale), headstock_y),
            (cx - int(32 * scale), headstock_y - headstock_h // 3),
            (cx - int(28 * scale), headstock_y - headstock_h),
            (cx - int(8 * scale), headstock_y - headstock_h - int(15 * scale)),
            (cx, headstock_y - headstock_h - int(8 * scale)),
            (cx + int(8 * scale), headstock_y - headstock_h - int(15 * scale)),
            (cx + int(28 * scale), headstock_y - headstock_h),
            (cx + int(32 * scale), headstock_y - headstock_h // 3),
            (cx + int(20 * scale), headstock_y),
        ]
    elif headstock_style == "classic":
        headstock_points = [
            (cx - int(20 * scale), headstock_y),
            (cx - int(24 * scale), headstock_y - headstock_h // 3),
            (cx - int(22 * scale), headstock_y - headstock_h),
            (cx, headstock_y - headstock_h - int(6 * scale)),
            (cx + int(22 * scale), headstock_y - headstock_h),
            (cx + int(24 * scale), headstock_y - headstock_h // 3),
            (cx + int(20 * scale), headstock_y),
        ]
    else:
        headstock_points = [
            (cx - int(22 * scale), headstock_y),
            (cx - int(28 * scale), headstock_y - headstock_h // 2),
            (cx - int(20 * scale), headstock_y - headstock_h),
            (cx, headstock_y - headstock_h - int(8 * scale)),
            (cx + int(20 * scale), headstock_y - headstock_h),
            (cx + int(28 * scale), headstock_y - headstock_h // 2),
            (cx + int(22 * scale), headstock_y),
        ]
    
    # 琴头阴影
    shadow_pts = [(p[0] + 3, p[1] + 3) for p in headstock_points]
    pygame.draw.polygon(surface, (*theme["body_shadow"][:3], 70), shadow_pts)
    
    # 琴头主体
    pygame.draw.polygon(surface, theme["body_main"], headstock_points)
    pygame.draw.polygon(surface, theme["body_edge"], headstock_points, 2)
    
    # 琴头装饰线
    inner_head = [(int(cx + (p[0] - cx) * 0.8), int(headstock_y - headstock_h // 2 + (p[1] - headstock_y + headstock_h // 2) * 0.8)) 
                  for p in headstock_points]
    pygame.draw.polygon(surface, theme["body_accent"], inner_head, 1)
    
    # Logo区域
    logo_y = headstock_y - headstock_h // 2
    pygame.draw.rect(surface, (*theme["neon_primary"][:3], 80),
                    (cx - int(16 * scale), logo_y - 2, int(32 * scale), int(4 * scale)), 
                    border_radius=1)
    
    # 调音旋钮 (Tuning Machines) - 两侧各3个
    tuner_body = theme.get("tuner_body", theme["body_accent"])
    tuner_button = theme.get("tuner_button", theme["body_main"])
    
    for side in [-1, 1]:
        for tuner in range(3):
            tuner_x = cx + side * int((14 + tuner * 7) * scale)
            tuner_y = headstock_y - headstock_h + int((tuner + 1) * 5 * scale)
            
            # 旋钮主体
            pygame.draw.circle(surface, tuner_body, (tuner_x, tuner_y), int(4 * scale))
            # 旋钮按钮
            pygame.draw.circle(surface, tuner_button, (tuner_x, tuner_y), int(2.5 * scale))
            # 金属高光
            pygame.draw.circle(surface, (*theme["metal_highlight"][:3], 60), 
                             (tuner_x - 1, tuner_y - 1), int(1.5 * scale))


def _draw_exhaust(surface: pygame.Surface, cx: int, cy: int, body_length: int,
                  theme: dict, scale: float, t: float) -> None:
    """绘制尾部推进 - 收敛但有力"""
    exhaust_y = cy + body_length // 2 + int(5 * scale)
    
    exhaust_positions = [
        (cx - int(20 * scale), 0.7),   # 左
        (cx, 1.0),                      # 中央
        (cx + int(20 * scale), 0.7),   # 右
    ]
    
    breath = 0.92 + 0.08 * math.sin(t * 2)
    
    for exhaust_x, intensity in exhaust_positions:
        # 喷口金属框
        nozzle_w = int(10 * scale * intensity)
        nozzle_h = int(6 * scale)
        
        pygame.draw.ellipse(surface, theme["body_edge"],
                           (exhaust_x - nozzle_w // 2 - 1, exhaust_y - nozzle_h // 2 - 1, 
                            nozzle_w + 2, nozzle_h + 2))
        pygame.draw.ellipse(surface, theme["body_shadow"],
                           (exhaust_x - nozzle_w // 2, exhaust_y - nozzle_h // 2, 
                            nozzle_w, nozzle_h))
        
        # 核心火焰 - 短而有力
        exhaust_core = theme.get("exhaust_core", (255, 200, 100))
        exhaust_outer = theme.get("exhaust_outer", (200, 80, 30))
        
        flame_length = int((18 + 8 * math.sin(t * 8)) * scale * intensity * breath)
        
        # 外层火焰
        outer_flame = [
            (exhaust_x - nozzle_w // 3, exhaust_y),
            (exhaust_x - nozzle_w // 4, exhaust_y + flame_length * 0.6),
            (exhaust_x + int(math.sin(t * 12) * 2), exhaust_y + flame_length),
            (exhaust_x + nozzle_w // 4, exhaust_y + flame_length * 0.6),
            (exhaust_x + nozzle_w // 3, exhaust_y),
        ]
        pygame.draw.polygon(surface, (*exhaust_outer[:3], 150), outer_flame)
        
        # 内层火焰
        inner_flame = [
            (exhaust_x - nozzle_w // 5, exhaust_y),
            (exhaust_x, exhaust_y + flame_length * 0.7),
            (exhaust_x + nozzle_w // 5, exhaust_y),
        ]
        pygame.draw.polygon(surface, (*exhaust_core[:3], 200), inner_flame)
        
        # 核心白光
        core_flame = [
            (exhaust_x - 2, exhaust_y),
            (exhaust_x, exhaust_y + flame_length * 0.4),
            (exhaust_x + 2, exhaust_y),
        ]
        pygame.draw.polygon(surface, (255, 255, 255, 220), core_flame)
        
        # 少量火花
        spark_color = theme.get("spark_color", exhaust_core)
        for spark in range(4):
            spark_rng = random.Random(int(t * 20) + spark + int(exhaust_x))
            spark_life = ((t * 40 + spark * 15) % 100) / 100
            spark_offset = int(spark_rng.random() * 12 - 6)
            spark_y_pos = exhaust_y + int(spark_life * 35 * scale * intensity)
            spark_x_pos = exhaust_x + spark_offset
            spark_size = max(1, int((2 - spark_life * 1.8) * scale))
            spark_alpha = int(180 * (1 - spark_life))
            
            if spark_alpha > 20:
                pygame.draw.circle(surface, (*spark_color[:3], spark_alpha),
                                 (spark_x_pos, spark_y_pos), spark_size)


# ============================================================
#   旋转版本的绘制函数 - 支持倾斜角度
# ============================================================

def _rotate_point(px: int, py: int, origin_x: int, origin_y: int, angle: float) -> Tuple[int, int]:
    """绕原点旋转一个点"""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    dx, dy = px - origin_x, py - origin_y
    return (
        int(origin_x + dx * cos_a - dy * sin_a),
        int(origin_y + dx * sin_a + dy * cos_a)
    )


def _draw_brushed_metal_texture_rotated(surface: pygame.Surface, cx: int, cy: int,
                                        body_width: int, body_length: int, theme: dict,
                                        scale: float, angle: float) -> None:
    """绘制拉丝金属质感 - 带旋转"""
    metal_brush = theme.get("metal_brush", (60, 58, 55))
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    for i in range(-8, 9, 2):
        line_offset = i * int(3 * scale)
        # 原始线段端点
        x1, y1 = cx + line_offset, cy - body_length // 3
        x2, y2 = cx + line_offset, cy + body_length // 3
        # 旋转
        rx1 = int(cx + (x1 - cx) * cos_a - (y1 - cy) * sin_a)
        ry1 = int(cy + (x1 - cx) * sin_a + (y1 - cy) * cos_a)
        rx2 = int(cx + (x2 - cx) * cos_a - (y2 - cy) * sin_a)
        ry2 = int(cy + (x2 - cx) * sin_a + (y2 - cy) * cos_a)
        
        pygame.draw.line(surface, (*metal_brush[:3], 40), (rx1, ry1), (rx2, ry2), 1)


def _draw_pickups_rotated(surface: pygame.Surface, cx: int, cy: int, theme: dict,
                          scale: float, angle: float, origin_x: int, origin_y: int) -> None:
    """绘制拾音器 - 带旋转"""
    pickup_color = theme.get("pickup_color", (25, 25, 28))
    pickup_pole = theme.get("pickup_pole", (90, 85, 75))
    pickup_cover = theme.get("pickup_cover", (45, 42, 38))
    
    pickup_positions = [int(-12 * scale), int(15 * scale)]  # 两个拾音器Y偏移
    
    for pickup_offset in pickup_positions:
        pickup_y = cy + pickup_offset
        pickup_w = int(28 * scale)
        pickup_h = int(12 * scale)
        
        # 拾音器四角
        corners = [
            (cx - pickup_w // 2, pickup_y - pickup_h // 2),
            (cx + pickup_w // 2, pickup_y - pickup_h // 2),
            (cx + pickup_w // 2, pickup_y + pickup_h // 2),
            (cx - pickup_w // 2, pickup_y + pickup_h // 2),
        ]
        rotated_corners = [_rotate_point(p[0], p[1], origin_x, origin_y, angle) for p in corners]
        
        # 拾音器底座
        pygame.draw.polygon(surface, pickup_color, rotated_corners)
        pygame.draw.polygon(surface, theme["body_edge"], rotated_corners, 1)
        
        # 拾音器盖板
        inner_corners = [
            (cx - pickup_w // 2 + 3, pickup_y - pickup_h // 2 + 2),
            (cx + pickup_w // 2 - 3, pickup_y - pickup_h // 2 + 2),
            (cx + pickup_w // 2 - 3, pickup_y + pickup_h // 2 - 2),
            (cx - pickup_w // 2 + 3, pickup_y + pickup_h // 2 - 2),
        ]
        rotated_inner = [_rotate_point(p[0], p[1], origin_x, origin_y, angle) for p in inner_corners]
        pygame.draw.polygon(surface, pickup_cover, rotated_inner)
        
        # 磁极 - 6个
        for pole in range(6):
            pole_x = cx - pickup_w // 2 + int((pole + 0.8) * pickup_w / 6.5)
            pole_pos = _rotate_point(pole_x, pickup_y, origin_x, origin_y, angle)
            pygame.draw.circle(surface, pickup_pole, pole_pos, int(2.5 * scale))
            # 高光
            pygame.draw.circle(surface, (*theme.get("metal_highlight", (180, 175, 165))[:3], 80),
                             (pole_pos[0] - 1, pole_pos[1] - 1), int(1.5 * scale))


def _draw_bridge_and_controls_rotated(surface: pygame.Surface, cx: int, cy: int,
                                      theme: dict, scale: float, t: float,
                                      angle: float, origin_x: int, origin_y: int) -> None:
    """绘制琴桥和控制旋钮 - 带旋转"""
    bridge_color = theme.get("bridge_color", (150, 145, 135))
    
    # 琴桥
    bridge_y = cy + int(28 * scale)
    bridge_w = int(26 * scale)
    bridge_h = int(8 * scale)
    
    bridge_corners = [
        (cx - bridge_w // 2, bridge_y - bridge_h // 2),
        (cx + bridge_w // 2, bridge_y - bridge_h // 2),
        (cx + bridge_w // 2, bridge_y + bridge_h // 2),
        (cx - bridge_w // 2, bridge_y + bridge_h // 2),
    ]
    rotated_bridge = [_rotate_point(p[0], p[1], origin_x, origin_y, angle) for p in bridge_corners]
    pygame.draw.polygon(surface, bridge_color, rotated_bridge)
    pygame.draw.polygon(surface, theme["body_edge"], rotated_bridge, 1)
    
    # 琴桥鞍座
    for saddle in range(6):
        saddle_x = cx - bridge_w // 2 + int((saddle + 0.8) * bridge_w / 6.5)
        saddle_pos = _rotate_point(saddle_x, bridge_y, origin_x, origin_y, angle)
        pygame.draw.circle(surface, theme["body_edge"], saddle_pos, int(2 * scale))
    
    # 控制旋钮
    knob_color = theme.get("knob_color", (40, 38, 35))
    knob_positions = [
        (cx + int(18 * scale), cy + int(35 * scale)),   # Volume
        (cx - int(18 * scale), cy + int(35 * scale)),   # Tone
    ]
    
    for kx, ky in knob_positions:
        knob_pos = _rotate_point(kx, ky, origin_x, origin_y, angle)
        knob_r = int(5 * scale)
        pygame.draw.circle(surface, knob_color, knob_pos, knob_r)
        pygame.draw.circle(surface, theme["body_edge"], knob_pos, knob_r, 1)
        # 旋钮标记
        pygame.draw.circle(surface, theme.get("neon_primary", (200, 50, 50)), knob_pos, int(1.5 * scale))


def _draw_guitar_neck_rotated(surface: pygame.Surface, cx: int, cy: int,
                              body_length: int, neck_length: int, neck_width: int,
                              theme: dict, scale: float, t: float,
                              angle: float, origin_x: int, origin_y: int) -> None:
    """绘制琴颈 - 带旋转，完整展示"""
    neck_start_y = cy - body_length // 2 + int(8 * scale)
    neck_end_y = cy - body_length // 2 - neck_length
    
    # 琴颈四角
    neck_corners = [
        (cx - neck_width // 2 - 2, neck_end_y),
        (cx + neck_width // 2 + 2, neck_end_y),
        (cx + neck_width // 2 + 2, neck_start_y),
        (cx - neck_width // 2 - 2, neck_start_y),
    ]
    rotated_neck = [_rotate_point(p[0], p[1], origin_x, origin_y, angle) for p in neck_corners]
    
    # 琴颈阴影
    shadow_neck = [(p[0] + 4, p[1] + 4) for p in rotated_neck]
    pygame.draw.polygon(surface, (*theme["body_shadow"][:3], 60), shadow_neck)
    
    # 琴颈背面（枫木色）
    pygame.draw.polygon(surface, theme["body_accent"], rotated_neck)
    
    # 指板
    fretboard_corners = [
        (cx - neck_width // 2, neck_end_y + 2),
        (cx + neck_width // 2, neck_end_y + 2),
        (cx + neck_width // 2, neck_start_y - 2),
        (cx - neck_width // 2, neck_start_y - 2),
    ]
    rotated_fretboard = [_rotate_point(p[0], p[1], origin_x, origin_y, angle) for p in fretboard_corners]
    fretboard_color = theme.get("fretboard", (45, 28, 15))
    pygame.draw.polygon(surface, fretboard_color, rotated_fretboard)
    
    # 品丝
    fret_count = 15
    fret_wire_color = theme.get("fret_wire", (180, 175, 160))
    for fret in range(fret_count):
        fret_y = neck_end_y + int((fret + 0.5) * (neck_start_y - neck_end_y) / fret_count)
        fret_left = _rotate_point(cx - neck_width // 2 + 1, fret_y, origin_x, origin_y, angle)
        fret_right = _rotate_point(cx + neck_width // 2 - 1, fret_y, origin_x, origin_y, angle)
        pygame.draw.line(surface, fret_wire_color, fret_left, fret_right, 2)
    
    # 品位标记
    inlay_color = theme.get("fretboard_inlay", (180, 175, 165))
    marker_frets = [3, 5, 7, 9, 12]
    for mf in marker_frets:
        if mf < fret_count:
            marker_y = neck_end_y + int((mf + 0.5) * (neck_start_y - neck_end_y) / fret_count)
            if mf == 12:
                pos1 = _rotate_point(cx - 4, marker_y, origin_x, origin_y, angle)
                pos2 = _rotate_point(cx + 4, marker_y, origin_x, origin_y, angle)
                pygame.draw.circle(surface, inlay_color, pos1, int(2.5 * scale))
                pygame.draw.circle(surface, inlay_color, pos2, int(2.5 * scale))
            else:
                pos = _rotate_point(cx, marker_y, origin_x, origin_y, angle)
                pygame.draw.circle(surface, inlay_color, pos, int(2.5 * scale))
    
    # 琴弦 - 6根真实钢弦
    string_steel = theme.get("string_steel", (200, 195, 185))
    string_wound = theme.get("string_wound", (160, 140, 100))
    
    for string in range(6):
        string_x = cx - neck_width // 2 + int((string + 0.8) * neck_width / 6.5)
        string_start = _rotate_point(string_x, neck_end_y, origin_x, origin_y, angle)
        string_end = _rotate_point(string_x, neck_start_y + int(50 * scale), origin_x, origin_y, angle)
        
        if string < 3:
            s_color = string_steel
            s_width = 1
        else:
            s_color = string_wound
            s_width = 2
        
        # 微弱振动
        vibrate = int(math.sin(t * 10 + string * 1.2) * 1.5)
        
        pygame.draw.line(surface, s_color, 
                        (string_start[0] + vibrate, string_start[1]),
                        string_end, s_width)
    
    # 琴颈边缘
    pygame.draw.polygon(surface, theme["body_edge"], rotated_neck, 2)


def _draw_headstock_rotated(surface: pygame.Surface, cx: int, cy: int,
                            body_length: int, neck_length: int, headstock_length: int,
                            theme: dict, scale: float, headstock_style: str, t: float,
                            angle: float, origin_x: int, origin_y: int) -> None:
    """绘制琴头 - 带旋转，锐利凶悍"""
    headstock_y = cy - body_length // 2 - neck_length
    headstock_h = headstock_length
    
    # 根据风格生成琴头形状
    if headstock_style == "pointed":
        headstock_pts = [
            (cx - int(18 * scale), headstock_y),
            (cx - int(26 * scale), headstock_y - headstock_h // 2),
            (cx - int(20 * scale), headstock_y - headstock_h),
            (cx - int(8 * scale), headstock_y - headstock_h - int(12 * scale)),
            (cx + int(8 * scale), headstock_y - headstock_h - int(12 * scale)),
            (cx + int(20 * scale), headstock_y - headstock_h),
            (cx + int(26 * scale), headstock_y - headstock_h // 2),
            (cx + int(18 * scale), headstock_y),
        ]
    elif headstock_style == "sharp":
        headstock_pts = [
            (cx - int(16 * scale), headstock_y),
            (cx - int(30 * scale), headstock_y - headstock_h * 0.7),
            (cx - int(22 * scale), headstock_y - headstock_h),
            (cx, headstock_y - headstock_h - int(18 * scale)),
            (cx + int(22 * scale), headstock_y - headstock_h),
            (cx + int(30 * scale), headstock_y - headstock_h * 0.7),
            (cx + int(16 * scale), headstock_y),
        ]
    elif headstock_style == "demonic":
        headstock_pts = [
            (cx - int(16 * scale), headstock_y),
            (cx - int(24 * scale), headstock_y - headstock_h // 3),
            (cx - int(28 * scale), headstock_y - headstock_h * 0.8),
            (cx - int(12 * scale), headstock_y - headstock_h - int(20 * scale)),  # 左角
            (cx, headstock_y - headstock_h - int(10 * scale)),
            (cx + int(12 * scale), headstock_y - headstock_h - int(20 * scale)),  # 右角
            (cx + int(28 * scale), headstock_y - headstock_h * 0.8),
            (cx + int(24 * scale), headstock_y - headstock_h // 3),
            (cx + int(16 * scale), headstock_y),
        ]
    elif headstock_style == "classic":
        headstock_pts = [
            (cx - int(16 * scale), headstock_y),
            (cx - int(20 * scale), headstock_y - headstock_h // 3),
            (cx - int(18 * scale), headstock_y - headstock_h),
            (cx, headstock_y - headstock_h - int(8 * scale)),
            (cx + int(18 * scale), headstock_y - headstock_h),
            (cx + int(20 * scale), headstock_y - headstock_h // 3),
            (cx + int(16 * scale), headstock_y),
        ]
    else:
        headstock_pts = [
            (cx - int(18 * scale), headstock_y),
            (cx - int(24 * scale), headstock_y - headstock_h // 2),
            (cx - int(18 * scale), headstock_y - headstock_h),
            (cx, headstock_y - headstock_h - int(10 * scale)),
            (cx + int(18 * scale), headstock_y - headstock_h),
            (cx + int(24 * scale), headstock_y - headstock_h // 2),
            (cx + int(18 * scale), headstock_y),
        ]
    
    # 旋转所有点
    rotated_headstock = [_rotate_point(p[0], p[1], origin_x, origin_y, angle) for p in headstock_pts]
    
    # 琴头阴影
    shadow_pts = [(p[0] + 5, p[1] + 5) for p in rotated_headstock]
    pygame.draw.polygon(surface, (*theme["body_shadow"][:3], 70), shadow_pts)
    
    # 琴头主体
    pygame.draw.polygon(surface, theme["body_main"], rotated_headstock)
    pygame.draw.polygon(surface, theme["body_edge"], rotated_headstock, 2)
    
    # 琴头装饰线
    inner_scale = 0.8
    inner_pts = [(int(cx + (p[0] - cx) * inner_scale), int(headstock_y - headstock_h // 2 + (p[1] - headstock_y + headstock_h // 2) * inner_scale)) for p in headstock_pts]
    rotated_inner = [_rotate_point(p[0], p[1], origin_x, origin_y, angle) for p in inner_pts]
    pygame.draw.polygon(surface, theme["body_accent"], rotated_inner, 1)
    
    # Logo区域
    logo_y = headstock_y - headstock_h // 2
    logo_pos = _rotate_point(cx, logo_y, origin_x, origin_y, angle)
    pygame.draw.circle(surface, (*theme.get("neon_primary", (200, 50, 50))[:3], 120), 
                      logo_pos, int(8 * scale))
    pygame.draw.circle(surface, theme["body_main"], logo_pos, int(5 * scale))
    
    # 调音旋钮 - 两侧各3个
    tuner_body = theme.get("tuner_body", theme["body_accent"])
    tuner_button = theme.get("tuner_button", theme["body_main"])
    
    for side in [-1, 1]:
        for tuner in range(3):
            tuner_x = cx + side * int((10 + tuner * 6) * scale)
            tuner_y = headstock_y - headstock_h + int((tuner + 1) * 5 * scale)
            tuner_pos = _rotate_point(tuner_x, tuner_y, origin_x, origin_y, angle)
            
            # 旋钮主体
            pygame.draw.circle(surface, tuner_body, tuner_pos, int(4 * scale))
            pygame.draw.circle(surface, tuner_button, tuner_pos, int(2.5 * scale))
            # 高光
            pygame.draw.circle(surface, (*theme.get("metal_highlight", (180, 175, 165))[:3], 60),
                             (tuner_pos[0] - 1, tuner_pos[1] - 1), int(1.5 * scale))


def _draw_exhaust_rotated(surface: pygame.Surface, cx: int, cy: int, body_length: int,
                          theme: dict, scale: float, t: float,
                          angle: float, origin_x: int, origin_y: int) -> None:
    """绘制尾部推进火焰 - 带旋转"""
    exhaust_y = cy + body_length // 2 + int(8 * scale)
    
    exhaust_positions = [
        (cx - int(18 * scale), 0.7),
        (cx, 1.0),
        (cx + int(18 * scale), 0.7),
    ]
    
    breath = 0.92 + 0.08 * math.sin(t * 2)
    
    for exhaust_x, intensity in exhaust_positions:
        exhaust_pos = _rotate_point(exhaust_x, exhaust_y, origin_x, origin_y, angle)
        
        # 喷口
        nozzle_r = int(5 * scale * intensity)
        pygame.draw.circle(surface, theme["body_edge"], exhaust_pos, nozzle_r + 2)
        pygame.draw.circle(surface, theme["body_shadow"], exhaust_pos, nozzle_r)
        
        # 火焰
        exhaust_core = theme.get("exhaust_core", (255, 200, 100))
        exhaust_outer = theme.get("exhaust_outer", (200, 80, 30))
        
        flame_length = int((20 + 10 * math.sin(t * 8)) * scale * intensity * breath)
        
        # 火焰方向（向下偏移旋转角度）
        flame_angle = angle + math.pi / 2  # 向下
        cos_f = math.cos(flame_angle)
        sin_f = math.sin(flame_angle)
        
        # 火焰端点
        flame_tip_x = exhaust_pos[0] + int(cos_f * flame_length)
        flame_tip_y = exhaust_pos[1] + int(sin_f * flame_length)
        
        # 外层火焰
        outer_w = nozzle_r
        perp_x = -sin_f * outer_w
        perp_y = cos_f * outer_w
        
        outer_flame = [
            (int(exhaust_pos[0] - perp_x), int(exhaust_pos[1] - perp_y)),
            (int(exhaust_pos[0] + perp_x), int(exhaust_pos[1] + perp_y)),
            (flame_tip_x + int(math.sin(t * 12) * 3), flame_tip_y + int(math.cos(t * 12) * 3)),
        ]
        pygame.draw.polygon(surface, (*exhaust_outer[:3], 150), outer_flame)
        
        # 内层火焰
        inner_w = nozzle_r * 0.5
        inner_perp_x = -sin_f * inner_w
        inner_perp_y = cos_f * inner_w
        inner_tip_x = exhaust_pos[0] + int(cos_f * flame_length * 0.7)
        inner_tip_y = exhaust_pos[1] + int(sin_f * flame_length * 0.7)
        
        inner_flame = [
            (int(exhaust_pos[0] - inner_perp_x), int(exhaust_pos[1] - inner_perp_y)),
            (int(exhaust_pos[0] + inner_perp_x), int(exhaust_pos[1] + inner_perp_y)),
            (inner_tip_x, inner_tip_y),
        ]
        pygame.draw.polygon(surface, (*exhaust_core[:3], 200), inner_flame)
        
        # 核心白光
        core_tip_x = exhaust_pos[0] + int(cos_f * flame_length * 0.4)
        core_tip_y = exhaust_pos[1] + int(sin_f * flame_length * 0.4)
        core_flame = [
            (exhaust_pos[0] - 2, exhaust_pos[1]),
            (exhaust_pos[0] + 2, exhaust_pos[1]),
            (core_tip_x, core_tip_y),
        ]
        pygame.draw.polygon(surface, (255, 255, 255, 220), core_flame)


def _hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """HSV转RGB"""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


# ============================================================
#   辅助渲染函数 - 压迫感强化版
# ============================================================

def _get_guitar_body_points(cx: int, cy: int, body_width: int, body_length: int, 
                            guitar_shape: str, scale: float) -> List[Tuple[int, int]]:
    """生成吉他琴身轮廓点 - 更锐利、更有攻击性"""
    
    if guitar_shape == "flying_v":
        # Flying V - 经典V字，更尖锐
        return [
            (cx, cy - body_length // 2 - int(8 * scale)),    # 顶尖(更尖)
            (cx - int(8 * scale), cy - body_length // 3),     # 左上内凹
            (cx - body_width // 2 - int(15 * scale), cy + body_length // 3 + int(5 * scale)),  # 左翼尖(更长)
            (cx - body_width // 3, cy + body_length // 2),    # 左下
            (cx, cy + body_length // 3 + int(5 * scale)),     # 中下V口
            (cx + body_width // 3, cy + body_length // 2),    # 右下
            (cx + body_width // 2 + int(15 * scale), cy + body_length // 3 + int(5 * scale)),  # 右翼尖
            (cx + int(8 * scale), cy - body_length // 3),     # 右上内凹
        ]
    elif guitar_shape == "explorer":
        # Explorer - 不对称尖锐，更具攻击性
        return [
            (cx - int(8 * scale), cy - body_length // 2),
            (cx - body_width // 2 - int(12 * scale), cy - body_length // 4),
            (cx - body_width // 2 - int(5 * scale), cy + body_length // 5),
            (cx - body_width // 3, cy + body_length // 2 + int(5 * scale)),
            (cx + body_width // 4, cy + body_length // 2),
            (cx + body_width // 2 + int(5 * scale), cy + body_length // 4),
            (cx + body_width // 2 + int(18 * scale), cy - body_length // 5),
            (cx + body_width // 3, cy - body_length // 2 + int(5 * scale)),
        ]
    elif guitar_shape == "bc_rich":
        # BC Rich - 恶魔造型，锯齿边缘
        return [
            (cx, cy - body_length // 2 - int(10 * scale)),
            (cx - body_width // 4, cy - body_length // 3),
            (cx - body_width // 2 - int(20 * scale), cy - body_length // 5),
            (cx - body_width // 2 - int(8 * scale), cy),
            (cx - body_width // 2 - int(15 * scale), cy + body_length // 4),
            (cx - body_width // 3, cy + body_length // 2 + int(10 * scale)),
            (cx, cy + body_length // 3),
            (cx + body_width // 3, cy + body_length // 2 + int(10 * scale)),
            (cx + body_width // 2 + int(15 * scale), cy + body_length // 4),
            (cx + body_width // 2 + int(8 * scale), cy),
            (cx + body_width // 2 + int(20 * scale), cy - body_length // 5),
            (cx + body_width // 4, cy - body_length // 3),
        ]
    elif guitar_shape == "warlock":
        # Warlock - 尖刺造型
        return [
            (cx, cy - body_length // 2 - int(5 * scale)),
            (cx - body_width // 2 - int(18 * scale), cy - body_length // 4),
            (cx - body_width // 3, cy),
            (cx - body_width // 2 - int(12 * scale), cy + body_length // 4),
            (cx - body_width // 4, cy + body_length // 2 + int(12 * scale)),
            (cx, cy + body_length // 3),
            (cx + body_width // 4, cy + body_length // 2 + int(12 * scale)),
            (cx + body_width // 2 + int(12 * scale), cy + body_length // 4),
            (cx + body_width // 3, cy),
            (cx + body_width // 2 + int(18 * scale), cy - body_length // 4),
        ]
    elif guitar_shape == "les_paul":
        # Les Paul - 经典圆润但厚重
        return [
            (cx - body_width // 3, cy - body_length // 2 + int(8 * scale)),
            (cx - body_width // 2 - int(5 * scale), cy - body_length // 4),
            (cx - body_width // 2 - int(8 * scale), cy),
            (cx - body_width // 2, cy + body_length // 3),
            (cx - body_width // 3, cy + body_length // 2 + int(3 * scale)),
            (cx + body_width // 3, cy + body_length // 2 + int(3 * scale)),
            (cx + body_width // 2, cy + body_length // 3),
            (cx + body_width // 2 + int(8 * scale), cy),
            (cx + body_width // 2 + int(5 * scale), cy - body_length // 4),
            (cx + body_width // 3, cy - body_length // 2 + int(8 * scale)),
        ]
    elif guitar_shape == "iceman":
        # Iceman - 冰锥造型
        return [
            (cx, cy - body_length // 2 - int(5 * scale)),
            (cx - body_width // 2 - int(5 * scale), cy - body_length // 4),
            (cx - body_width // 2 - int(12 * scale), cy + body_length // 5),
            (cx - body_width // 3, cy + body_length // 2 + int(5 * scale)),
            (cx, cy + body_length // 2 - int(8 * scale)),
            (cx + body_width // 3, cy + body_length // 2 + int(5 * scale)),
            (cx + body_width // 2 + int(12 * scale), cy + body_length // 5),
            (cx + body_width // 2 + int(5 * scale), cy - body_length // 4),
        ]
    else:
        # 默认 Modern V / Superstrat
        return [
            (cx - body_width // 4, cy - body_length // 2),
            (cx - body_width // 2 - int(8 * scale), cy - body_length // 4),
            (cx - body_width // 2 - int(10 * scale), cy + body_length // 5),
            (cx - body_width // 3, cy + body_length // 2 + int(3 * scale)),
            (cx + body_width // 3, cy + body_length // 2 + int(3 * scale)),
            (cx + body_width // 2 + int(10 * scale), cy + body_length // 5),
            (cx + body_width // 2 + int(8 * scale), cy - body_length // 4),
            (cx + body_width // 4, cy - body_length // 2),
        ]


def _draw_brushed_metal_texture(surface: pygame.Surface, cx: int, cy: int, 
                                 body_width: int, body_length: int, 
                                 theme: dict, scale: float) -> None:
    """绘制拉丝金属质感"""
    brush_color = theme.get("metal_brush", theme["body_accent"])
    # 水平拉丝线
    for i in range(-int(body_length // 3), int(body_length // 3), int(4 * scale)):
        line_y = cy + i
        line_alpha = 15 + random.randint(-5, 5)
        half_width = int(body_width * 0.35 * (1 - abs(i) / (body_length // 2)))
        if half_width > 0:
            pygame.draw.line(surface, (*brush_color[:3], max(5, line_alpha)),
                           (cx - half_width, line_y), (cx + half_width, line_y), 1)


def _draw_speaker_cabinet(surface: pygame.Surface, speaker_x: int, speaker_y: int,
                          speaker_size: int, theme: dict, t: float, scale: float, side: int) -> None:
    """绘制音箱柜 - 厚重如装甲"""
    speaker_w = speaker_size
    speaker_h = int(speaker_size * 1.5)
    
    # 音箱阴影 - 增加厚度感
    shadow_rect = pygame.Rect(
        speaker_x - speaker_w // 2 + 4,
        speaker_y - speaker_h // 2 + 4,
        speaker_w, speaker_h
    )
    pygame.draw.rect(surface, (*theme["body_shadow"][:3], 80), shadow_rect, border_radius=3)
    
    # 音箱主体 - 箱体蒙皮
    cabinet_rect = pygame.Rect(
        speaker_x - speaker_w // 2,
        speaker_y - speaker_h // 2,
        speaker_w, speaker_h
    )
    tolex_color = theme.get("cabinet_tolex", theme["body_main"])
    pygame.draw.rect(surface, tolex_color, cabinet_rect, border_radius=3)
    
    # 金属边框
    pygame.draw.rect(surface, theme["body_edge"], cabinet_rect, 2, border_radius=3)
    
    # 金属护角
    corner_color = theme.get("cabinet_corner", theme["chrome"])
    corner_size = int(8 * scale)
    corners = [
        (cabinet_rect.left, cabinet_rect.top),
        (cabinet_rect.right - corner_size, cabinet_rect.top),
        (cabinet_rect.left, cabinet_rect.bottom - corner_size),
        (cabinet_rect.right - corner_size, cabinet_rect.bottom - corner_size),
    ]
    for cx_c, cy_c in corners:
        pygame.draw.rect(surface, corner_color, (cx_c, cy_c, corner_size, corner_size), border_radius=2)
    
    # 网罩区域
    grill_rect = pygame.Rect(
        speaker_x - speaker_w // 2 + int(5 * scale),
        speaker_y - speaker_h // 2 + int(8 * scale),
        speaker_w - int(10 * scale),
        speaker_h - int(16 * scale)
    )
    pygame.draw.rect(surface, theme["speaker_grill"], grill_rect, border_radius=2)
    
    # 网罩编织纹理
    for gy in range(grill_rect.top, grill_rect.bottom, int(3 * scale)):
        pygame.draw.line(surface, (*theme["body_secondary"][:3], 40),
                        (grill_rect.left, gy), (grill_rect.right, gy), 1)
    for gx in range(grill_rect.left, grill_rect.right, int(3 * scale)):
        pygame.draw.line(surface, (*theme["body_secondary"][:3], 30),
                        (gx, grill_rect.top), (gx, grill_rect.bottom), 1)
    
    # 4个喇叭单元 (2x2)
    bass_pulse = 0.98 + 0.02 * abs(math.sin(t * 2))
    for row in range(2):
        for col in range(2):
            woofer_x = speaker_x + int((col - 0.5) * 16 * scale)
            woofer_y = speaker_y + int((row - 0.5) * 20 * scale)
            woofer_r = int(8 * scale)
            
            # 微弱震动
            vibrate = int(1 * scale * bass_pulse)
            
            # 喇叭金属框
            pygame.draw.circle(surface, theme["speaker_rim"], 
                             (woofer_x, woofer_y), woofer_r + vibrate + 2, 2)
            
            # 悬边
            pygame.draw.circle(surface, theme["speaker_surround"], 
                             (woofer_x, woofer_y), woofer_r + vibrate)
            
            # 锥盆
            cone_r = int(woofer_r * 0.72)
            pygame.draw.circle(surface, theme["speaker_cone"], 
                             (woofer_x, woofer_y), cone_r + vibrate)
            
            # 锥盆同心纹
            for ring in range(3):
                ring_r = cone_r - ring * int(2 * scale)
                if ring_r > 0:
                    pygame.draw.circle(surface, (*theme["speaker_rim"][:3], 30),
                                     (woofer_x, woofer_y), ring_r, 1)
            
            # 防尘帽
            pygame.draw.circle(surface, theme["speaker_dust_cap"], 
                             (woofer_x, woofer_y), int(woofer_r * 0.32))
            # 防尘帽高光
            pygame.draw.circle(surface, (*theme["metal_highlight"][:3], 60), 
                             (woofer_x - 1, woofer_y - 1), int(woofer_r * 0.18))
    
    # 顶部Logo条
    logo_y = speaker_y - speaker_h // 2 + int(4 * scale)
    pygame.draw.rect(surface, (*theme["neon_primary"][:3], 120),
                    (speaker_x - int(14 * scale), logo_y, int(28 * scale), int(3 * scale)), 
                    border_radius=1)


def _draw_pickups(surface: pygame.Surface, cx: int, cy: int, theme: dict, scale: float) -> None:
    """绘制拾音器 - 真实金属感"""
    pickup_positions = [cy - int(10 * scale), cy + int(15 * scale)]
    
    for pickup_idx, pickup_y in enumerate(pickup_positions):
        pickup_w = int(36 * scale)
        pickup_h = int(12 * scale)
        pickup_x = cx - pickup_w // 2
        
        # 拾音器底座阴影
        pygame.draw.rect(surface, (*theme["body_shadow"][:3], 80),
                        (pickup_x + 2, pickup_y - pickup_h // 2 + 2, pickup_w, pickup_h), 
                        border_radius=2)
        
        # 拾音器盖板
        pickup_cover = theme.get("pickup_cover", theme["body_accent"])
        pygame.draw.rect(surface, pickup_cover,
                        (pickup_x, pickup_y - pickup_h // 2, pickup_w, pickup_h), 
                        border_radius=2)
        
        # 拾音器边框
        pygame.draw.rect(surface, theme["body_edge"],
                        (pickup_x, pickup_y - pickup_h // 2, pickup_w, pickup_h), 
                        1, border_radius=2)
        
        # 磁极 (6个)
        pole_color = theme.get("pickup_pole", theme["chrome"])
        for pole in range(6):
            pole_x = pickup_x + int(4 * scale) + pole * int(5.5 * scale)
            pygame.draw.circle(surface, pole_color, (pole_x, pickup_y), int(2.5 * scale))
            # 磁极凹陷感
            pygame.draw.circle(surface, (*theme["body_shadow"][:3], 60), 
                             (pole_x + 1, pickup_y + 1), int(1.5 * scale))


def _draw_bridge_and_controls(surface: pygame.Surface, cx: int, cy: int, 
                               theme: dict, scale: float, t: float) -> None:
    """绘制琴桥和控制旋钮"""
    # 琴桥
    bridge_y = cy + int(28 * scale)
    bridge_w = int(35 * scale)
    bridge_h = int(10 * scale)
    bridge_color = theme.get("bridge_metal", theme["chrome"])
    
    # 琴桥阴影
    pygame.draw.rect(surface, (*theme["body_shadow"][:3], 60),
                    (cx - bridge_w // 2 + 2, bridge_y - bridge_h // 2 + 2, bridge_w, bridge_h),
                    border_radius=2)
    
    # 琴桥主体
    pygame.draw.rect(surface, bridge_color,
                    (cx - bridge_w // 2, bridge_y - bridge_h // 2, bridge_w, bridge_h),
                    border_radius=2)
    
    # 琴桥鞍座
    for saddle in range(6):
        saddle_x = cx - bridge_w // 2 + int(5 * scale) + saddle * int(5 * scale)
        pygame.draw.rect(surface, theme["metal_highlight"],
                        (saddle_x - 2, bridge_y - 4, 4, 8), border_radius=1)
    
    # 控制旋钮
    knob_positions = [
        (cx + int(22 * scale), cy + int(38 * scale)),   # Volume
        (cx + int(22 * scale), cy + int(52 * scale)),   # Tone
    ]
    knob_body = theme.get("knob_body", theme["body_accent"])
    knob_marker = theme.get("knob_marker", theme["chrome"])
    
    for kx, ky in knob_positions:
        knob_r = int(6 * scale)
        # 旋钮阴影
        pygame.draw.circle(surface, (*theme["body_shadow"][:3], 50), (kx + 1, ky + 1), knob_r)
        # 旋钮主体
        pygame.draw.circle(surface, knob_body, (kx, ky), knob_r)
        # 旋钮边缘
        pygame.draw.circle(surface, theme["body_edge"], (kx, ky), knob_r, 1)
        # 旋钮纹理（凹槽）
        for groove in range(12):
            groove_angle = groove * math.pi / 6
            gx1 = kx + int(math.cos(groove_angle) * (knob_r - 2))
            gy1 = ky + int(math.sin(groove_angle) * (knob_r - 2))
            gx2 = kx + int(math.cos(groove_angle) * knob_r)
            gy2 = ky + int(math.sin(groove_angle) * knob_r)
            pygame.draw.line(surface, (*theme["body_shadow"][:3], 80), (gx1, gy1), (gx2, gy2), 1)
        # 指示点
        pygame.draw.circle(surface, knob_marker, (kx, ky - knob_r + 3), 2)


def _draw_guitar_neck(surface: pygame.Surface, cx: int, cy: int, 
                      body_length: int, neck_length: int, neck_width: int,
                      theme: dict, scale: float, t: float) -> None:
    """绘制琴颈 - 粗壮有力，真实钢弦"""
    neck_start_y = cy - body_length // 2 + int(5 * scale)
    neck_end_y = cy - body_length // 2 - neck_length
    
    # 琴颈阴影
    pygame.draw.rect(surface, (*theme["body_shadow"][:3], 70),
                    (cx - neck_width // 2 + 3, neck_end_y + 3, neck_width, neck_length))
    
    # 琴颈背面（枫木）
    pygame.draw.rect(surface, theme["body_accent"],
                    (cx - neck_width // 2 - 2, neck_end_y, neck_width + 4, neck_length),
                    border_radius=2)
    
    # 指板（玫瑰木）
    fretboard_color = theme.get("fretboard", (45, 28, 15))
    pygame.draw.rect(surface, fretboard_color,
                    (cx - neck_width // 2, neck_end_y, neck_width, neck_length),
                    border_radius=1)
    
    # 品丝
    fret_count = 12
    fret_wire_color = theme.get("fret_wire", (180, 175, 160))
    for fret in range(fret_count):
        fret_y = neck_end_y + int((fret + 0.5) * neck_length / fret_count)
        pygame.draw.line(surface, fret_wire_color,
                        (cx - neck_width // 2 + 1, fret_y),
                        (cx + neck_width // 2 - 1, fret_y), 2)
    
    # 品位标记（珍珠镶嵌）
    inlay_color = theme.get("fretboard_inlay", (180, 175, 165))
    marker_frets = [3, 5, 7, 9, 12]
    for mf in marker_frets:
        if mf < fret_count:
            marker_y = neck_end_y + int((mf + 0.5) * neck_length / fret_count)
            if mf == 12:
                pygame.draw.circle(surface, inlay_color, (cx - 3, marker_y), 2)
                pygame.draw.circle(surface, inlay_color, (cx + 3, marker_y), 2)
            else:
                pygame.draw.circle(surface, inlay_color, (cx, marker_y), 2)
    
    # 真实钢弦 (6根)
    string_steel = theme.get("string_steel", (200, 195, 185))
    string_wound = theme.get("string_wound", (160, 140, 100))
    
    for string in range(6):
        string_x = cx - neck_width // 2 + int((string + 0.8) * neck_width / 6.5)
        # 高音弦(钢色) vs 低音弦(缠弦/铜色)
        if string < 3:
            s_color = string_steel
            s_width = 1
        else:
            s_color = string_wound
            s_width = 2
        
        # 微弱振动
        vibrate = math.sin(t * 8 + string * 1.5) * 0.8
        
        pygame.draw.line(surface, s_color,
                        (int(string_x + vibrate), neck_end_y),
                        (string_x, neck_start_y + int(30 * scale)), s_width)


# ============================================================
#   涂装样式列表 (用于注册)
# ============================================================
HEAVYMETAL_STYLES = [
    "heavymetal_default",    # 死亡金属
    "heavymetal_bloody",     # 血腥狂欢
    "heavymetal_cyber",      # 电子蓝调
    "heavymetal_golden",     # 黄金摇滚
    "heavymetal_psychedelic",# 迷幻紫雾
    "heavymetal_toxic",      # 毒液绿魔
    "heavymetal_frost",      # 冰霜金属
    "heavymetal_hellfire",   # 地狱火焰
    "heavymetal_midnight",   # 午夜蓝
    "heavymetal_rainbow",    # 彩虹棱镜
    "heavymetal_steampunk",  # 蒸汽朋克
    "heavymetal_starpunk",   # 星际朋克
]


def is_heavymetal_style(style: str) -> bool:
    """判断是否为HEAVY METAL涂装"""
    return style in HEAVYMETAL_STYLES


def get_heavymetal_theme(style: str) -> dict:
    """获取HEAVY METAL主题配置"""
    # 从样式名提取主题名 (去掉 heavymetal_ 前缀)
    if style.startswith("heavymetal_"):
        theme_name = style[11:]  # 去掉 "heavymetal_" 前缀
    else:
        theme_name = style
    return HEAVYMETAL_THEMES.get(theme_name, HEAVYMETAL_THEMES["default"])


def get_all_heavymetal_styles() -> List[str]:
    """获取所有HEAVY METAL涂装样式"""
    return HEAVYMETAL_STYLES.copy()


def render_heavymetal_skin(surface: pygame.Surface, color, x: int, y: int, 
                           w: int, h: int, frame: int, style: str) -> None:
    """
    渲染HEAVY METAL涂装 (兼容统一皮肤接口)
    
    Args:
        surface: 目标绘制表面
        color: 颜色参数 (未使用，保持接口兼容)
        x, y: 机体中心坐标
        w, h: 机体尺寸 (用于计算缩放)
        frame: 动画帧数
        style: 涂装样式名
    """
    # 从样式名提取主题名
    if style.startswith("heavymetal_"):
        theme_name = style[11:]
    else:
        theme_name = "default"
    
    # 计算时间参数和缩放
    t = frame * 0.016  # 约60fps
    scale = min(w, h) / 50.0  # 基于尺寸计算缩放
    
    render_heavymetal_plane(surface, x, y, theme_name, t, scale)


# ============================================================
#   快捷绘制函数
# ============================================================
def draw_heavymetal(surface: pygame.Surface, x: int, y: int, 
                    theme: str = "default", time_offset: float = 0,
                    scale: float = 2.0) -> None:
    """快捷绘制HEAVY METAL机体"""
    render_heavymetal_plane(surface, x, y, theme, time_offset, scale)


def _render_heavymetal_base(surface: pygame.Surface, t: float, pulse: float) -> None:
    """
    渲染HEAVY METAL基础机体 (用于get_plane_surf默认渲染)
    
    Args:
        surface: 120x120 的目标表面
        t: 时间参数
        pulse: 脉冲参数 (未使用)
    """
    # 在120x120的surface上渲染，中心60,60
    render_heavymetal_plane(surface, 60, 60, "default", t, 1.0)
