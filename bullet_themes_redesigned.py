# ==============================================================================
#   子弹涂装主题 - 完全重新设计版本
#   每个子弹都有独特的视觉元素和特效，真正契合机体涂装
# ==============================================================================

BULLET_THEMES_REDESIGNED = {
    # 默认
    "default": {
        "name": "标准子弹",
        "desc": "基础能量弹",
        "cost": 0,
        "visual": {
            "base_shape": "circle",
            "pattern": None,
            "animation": None,
        },
        "colors": {
            "primary": None,  # 使用机体颜色
            "secondary": None,
            "glow": (255, 255, 200),
        },
        "effects": [],
        "particles": [],
        "category": "default",
    },
    
    # ========== Striker 系列 ==========
    "striker_mk2_bullet": {
        "name": "纳米机械组件",
        "desc": "子弹由悬浮的纳米齿轮、螺丝、螺栓组成，不断旋转重组",
        "cost": 2000,
        "visual": {
            "base_shape": "composite",
            "pattern": "mech_parts",  # 显示齿轮+螺丝+螺栓
            "animation": "rotate_parts",  # 零件旋转
            "symbols": ["⚙", "🔩", "⚡"],  # Unicode机械符号
        },
        "colors": {
            "primary": (0, 255, 255),
            "secondary": (255, 200, 0),
            "glow": (100, 200, 255),
        },
        "effects": ["spark_trail", "metal_shine"],
        "particles": ["metal_fragment", "electric_spark"],
        "category": "exclusive",
        "exclusive_plane": "striker",
    },
    
    "striker_stealth_bullet": {
        "name": "相位暗影",
        "desc": "半透明幽灵形态，不断闪烁消失，留下虚空裂痕尾迹",
        "cost": 2200,
        "visual": {
            "base_shape": "oval",
            "pattern": "phase_flicker",  # 闪烁效果
            "animation": "fade_in_out",
            "opacity": 0.6,  # 半透明
        },
        "colors": {
            "primary": (80, 80, 150),
            "secondary": (100, 100, 180),
            "glow": (150, 150, 200),
        },
        "effects": ["phase_flicker", "void_crack_trail"],
        "particles": ["shadow_wisp"],
        "category": "exclusive",
        "exclusive_plane": "striker",
    },
    
    "striker_overdrive_bullet": {
        "name": "反应堆过载核心",
        "desc": "裂开的能量核心，裂缝中流淌岩浆，持续掉落燃烧碎片",
        "cost": 2400,
        "visual": {
            "base_shape": "cracked_sphere",
            "pattern": "reactor_cracks",  # 显示裂纹
            "animation": "pulse_glow",  # 脉冲发光
            "crack_lines": 5,  # 5条裂纹
        },
        "colors": {
            "primary": (255, 50, 0),
            "secondary": (255, 150, 0),
            "glow": (255, 200, 100),
        },
        "effects": ["lava_flow", "explosive_pulse"],
        "particles": ["molten_drop", "fire_spark"],
        "category": "exclusive",
        "exclusive_plane": "striker",
    },
    
    "striker_quantum_bullet": {
        "name": "量子叠加态",
        "desc": "子弹同时存在于3个位置，不断闪烁跳跃，粒子风暴环绕",
        "cost": 2600,
        "visual": {
            "base_shape": "triple_orb",  # 3个重叠的球体
            "pattern": "quantum_blur",
            "animation": "position_shift",  # 位置跳跃
            "echo_count": 3,
        },
        "colors": {
            "primary": (150, 255, 255),
            "secondary": (200, 220, 255),
            "glow": (255, 255, 255),
        },
        "effects": ["quantum_glitch", "position_echo"],
        "particles": ["quantum_particle"],
        "category": "exclusive",
        "exclusive_plane": "striker",
    },
    
    "striker_holy_bullet": {
        "name": "圣光十字",
        "desc": "金色十字光芒，四向射出光束，天使羽毛环绕飘落",
        "cost": 2800,
        "visual": {
            "base_shape": "cross",
            "pattern": "holy_cross",  # 十字图案
            "animation": "light_rays",  # 光芒射线
            "ray_count": 4,
        },
        "colors": {
            "primary": (255, 255, 220),
            "secondary": (255, 250, 230),
            "glow": (255, 255, 255),
        },
        "effects": ["holy_ray", "divine_glow"],
        "particles": ["feather", "light_mote"],
        "category": "exclusive",
        "exclusive_plane": "striker",
    },
    
    "striker_dragon_bullet": {
        "name": "东方神龙吐息",
        "desc": "龙首图案，金色龙鳞纹理，喷涌龙息火焰",
        "cost": 3000,
        "visual": {
            "base_shape": "dragon_head",
            "pattern": "dragon_scale",  # 龙鳞纹理
            "animation": "breath_flame",
            "symbols": ["龍"],  # 龙字
        },
        "colors": {
            "primary": (220, 0, 0),
            "secondary": (255, 215, 0),
            "glow": (255, 150, 0),
        },
        "effects": ["dragon_breath", "scale_shimmer"],
        "particles": ["fire_breath", "gold_scale"],
        "category": "exclusive",
        "exclusive_plane": "striker",
    },
    
    "striker_infinity_bullet": {
        "name": "无限刃光",
        "desc": "光剑形态，周围环绕旋转的光刃，闪电链连接",
        "cost": 3500,
        "visual": {
            "base_shape": "blade",
            "pattern": "energy_blade",
            "animation": "spin_blades",  # 刀刃旋转
            "blade_count": 3,
        },
        "colors": {
            "primary": (0, 255, 255),
            "secondary": (255, 0, 255),
            "glow": (150, 200, 255),
        },
        "effects": ["lightning_arc", "blade_trail"],
        "particles": ["electric_spark", "blade_fragment"],
        "category": "exclusive",
        "exclusive_plane": "striker",
    },
    
    # ========== Phantom 系列 ==========
    "phantom_void_bullet": {
        "name": "虚空裂痕",
        "desc": "黑色裂缝形态，星云在裂缝中流动，虚空粒子逸散",
        "cost": 2000,
        "visual": {
            "base_shape": "crack",
            "pattern": "void_crack",  # 裂痕图案
            "animation": "nebula_flow",  # 星云流动
        },
        "colors": {
            "primary": (120, 0, 220),
            "secondary": (140, 50, 200),
            "glow": (180, 100, 255),
        },
        "effects": ["void_distortion", "nebula_swirl"],
        "particles": ["void_particle", "star_dust"],
        "category": "exclusive",
        "exclusive_plane": "phantom",
    },
    
    "phantom_ghost_bullet": {
        "name": "幽灵面孔",
        "desc": "显示幽灵脸部轮廓，表情随机变化，魂火粒子飘荡",
        "cost": 2200,
        "visual": {
            "base_shape": "ghost_face",
            "pattern": "face_expression",  # 表情图案
            "animation": "expression_change",  # 表情变化
            "symbols": ["👻", "💀"],  # 幽灵符号
        },
        "colors": {
            "primary": (200, 200, 255),
            "secondary": (180, 180, 240),
            "glow": (220, 220, 255),
        },
        "effects": ["soul_fire", "ghostly_fade"],
        "particles": ["soul_wisp", "spectral_flame"],
        "category": "exclusive",
        "exclusive_plane": "phantom",
    },
    
    "phantom_mirror_bullet": {
        "name": "万花筒水晶",
        "desc": "多面水晶体，每个面反射不同镜像，不断旋转折射光芒",
        "cost": 2400,
        "visual": {
            "base_shape": "polyhedron",
            "pattern": "mirror_facet",  # 镜面
            "animation": "rotate_refract",  # 旋转折射
            "facet_count": 8,
        },
        "colors": {
            "primary": (240, 240, 240),
            "secondary": (220, 220, 250),
            "glow": (255, 255, 255),
        },
        "effects": ["mirror_reflect", "prism_ray"],
        "particles": ["crystal_shard", "light_prism"],
        "category": "exclusive",
        "exclusive_plane": "phantom",
    },
    
    "phantom_nightmare_bullet": {
        "name": "深渊触手",
        "desc": "中心是恐惧之眼，触手在周围蠕动，黑雾弥漫",
        "cost": 2600,
        "visual": {
            "base_shape": "eye_tentacle",
            "pattern": "tentacle_eye",  # 眼睛+触手
            "animation": "tentacle_wriggle",  # 触手蠕动
            "tentacle_count": 4,
        },
        "colors": {
            "primary": (100, 0, 140),
            "secondary": (120, 0, 160),
            "glow": (170, 0, 220),
        },
        "effects": ["dark_mist", "fear_aura"],
        "particles": ["black_smoke", "fear_eye"],
        "category": "exclusive",
        "exclusive_plane": "phantom",
    },
    
    "phantom_aurora_bullet": {
        "name": "极光流星",
        "desc": "七彩光带缠绕，如同极光流动，光粒子螺旋舞蹈",
        "cost": 2800,
        "visual": {
            "base_shape": "comet",
            "pattern": "aurora_ribbon",  # 极光光带
            "animation": "ribbon_flow",  # 光带流动
        },
        "colors": {
            "primary": (100, 255, 200),
            "secondary": (150, 220, 255),
            "glow": (200, 255, 255),
            "rainbow": True,  # 使用彩虹色
        },
        "effects": ["aurora_wave", "rainbow_trail"],
        "particles": ["light_mote", "color_wisp"],
        "category": "exclusive",
        "exclusive_plane": "phantom",
    },
    
    "phantom_time_bullet": {
        "name": "时空回溯",
        "desc": "沙漏形态，沙粒在两端流动，留下时间波纹和残影",
        "cost": 3000,
        "visual": {
            "base_shape": "hourglass",
            "pattern": "sand_flow",  # 沙粒流动
            "animation": "time_rewind",  # 时间倒流
            "symbols": ["⏳", "🕰"],  # 时间符号
        },
        "colors": {
            "primary": (200, 180, 255),
            "secondary": (220, 200, 240),
            "glow": (240, 220, 255),
        },
        "effects": ["time_ripple", "afterimage_trail"],
        "particles": ["sand_particle", "time_fragment"],
        "category": "exclusive",
        "exclusive_plane": "phantom",
    },
    
    "phantom_matrix_bullet": {
        "name": "数字矩阵",
        "desc": "子弹由绿色的1和0字符组成，飞行时留下数字雨瀑布",
        "cost": 3500,
        "visual": {
            "base_shape": "text_cluster",
            "pattern": "binary_code",  # 二进制代码
            "animation": "digit_scroll",  # 数字滚动
            "symbols": ["1", "0"],  # 数字符号
            "text_size": 12,
        },
        "colors": {
            "primary": (0, 255, 50),
            "secondary": (30, 240, 70),
            "glow": (100, 255, 100),
        },
        "effects": ["matrix_rain", "code_glitch"],
        "particles": ["digit_particle", "code_fragment"],
        "category": "exclusive",
        "exclusive_plane": "phantom",
    },
    
    # ========== Titan 系列 ==========
    "titan_fortress_bullet": {
        "name": "装甲炮弹",
        "desc": "装甲板拼接的炮弹，带有铆钉图案，尾部喷射黑烟",
        "cost": 2000,
        "visual": {
            "base_shape": "shell",
            "pattern": "armor_plating",  # 装甲纹理
            "animation": "smoke_trail",
            "symbols": ["⚫", "▪"],  # 铆钉符号
        },
        "colors": {
            "primary": (140, 140, 140),
            "secondary": (120, 120, 120),
            "glow": (160, 160, 160),
        },
        "effects": ["smoke_exhaust", "metal_texture"],
        "particles": ["smoke_cloud", "metal_rivet"],
        "category": "exclusive",
        "exclusive_plane": "titan",
    },
    
    "titan_nuclear_bullet": {
        "name": "核辐射球",
        "desc": "核心发光脉动，辐射波纹扩散，放射性警告符号闪烁",
        "cost": 2200,
        "visual": {
            "base_shape": "sphere",
            "pattern": "radiation_symbol",  # 辐射标志
            "animation": "pulse_radiation",  # 辐射脉冲
            "symbols": ["☢"],  # 辐射符号
        },
        "colors": {
            "primary": (0, 255, 120),
            "secondary": (120, 255, 60),
            "glow": (200, 255, 100),
        },
        "effects": ["radiation_wave", "toxic_glow"],
        "particles": ["radiation_particle", "toxic_cloud"],
        "category": "exclusive",
        "exclusive_plane": "titan",
    },
    
    "titan_volcano_bullet": {
        "name": "熔岩巨石",
        "desc": "燃烧的不规则岩石，表面裂纹流淌岩浆，掉落火星",
        "cost": 2400,
        "visual": {
            "base_shape": "irregular_rock",
            "pattern": "lava_cracks",  # 岩浆裂纹
            "animation": "lava_pulse",
        },
        "colors": {
            "primary": (255, 120, 0),
            "secondary": (255, 100, 0),
            "glow": (255, 200, 50),
        },
        "effects": ["lava_drip", "ember_burst"],
        "particles": ["molten_drop", "fire_ember"],
        "category": "exclusive",
        "exclusive_plane": "titan",
    },
    
    "titan_mech_bullet": {
        "name": "机甲火箭",
        "desc": "火箭形态，尾部推进器喷射蓝色等离子，带有机械细节",
        "cost": 2600,
        "visual": {
            "base_shape": "rocket",
            "pattern": "mech_detail",  # 机械细节
            "animation": "thruster_burn",  # 推进器燃烧
        },
        "colors": {
            "primary": (0, 180, 255),
            "secondary": (100, 200, 255),
            "glow": (150, 220, 255),
        },
        "effects": ["plasma_thrust", "mech_exhaust"],
        "particles": ["plasma_particle", "exhaust_trail"],
        "category": "exclusive",
        "exclusive_plane": "titan",
    },
    
    "titan_crystal_bullet": {
        "name": "永恒冰刺",
        "desc": "巨大的冰晶尖刺，表面闪烁钻石光泽，冰霜扩散",
        "cost": 2800,
        "visual": {
            "base_shape": "ice_spike",
            "pattern": "crystal_facet",  # 水晶面
            "animation": "frost_spread",  # 冰霜扩散
        },
        "colors": {
            "primary": (150, 220, 255),
            "secondary": (180, 240, 255),
            "glow": (200, 250, 255),
        },
        "effects": ["frost_aura", "crystal_shine"],
        "particles": ["ice_shard", "frost_mist"],
        "category": "exclusive",
        "exclusive_plane": "titan",
    },
    
    "titan_demon_bullet": {
        "name": "恶魔头骨",
        "desc": "燃烧的恶魔头骨，眼窝中红光闪烁，血浆飞溅",
        "cost": 3000,
        "visual": {
            "base_shape": "skull",
            "pattern": "demon_skull",  # 恶魔头骨
            "animation": "eye_glow",  # 眼睛发光
            "symbols": ["💀", "👹"],  # 头骨符号
        },
        "colors": {
            "primary": (180, 0, 0),
            "secondary": (200, 30, 0),
            "glow": (255, 50, 50),
        },
        "effects": ["demon_aura", "blood_splatter"],
        "particles": ["blood_drop", "demon_flame"],
        "category": "exclusive",
        "exclusive_plane": "titan",
    },
    
    "titan_orbital_bullet": {
        "name": "天基光束",
        "desc": "垂直的等离子光柱，周围环绕卫星轨道环，光网交织",
        "cost": 3500,
        "visual": {
            "base_shape": "beam",
            "pattern": "orbital_ring",  # 轨道环
            "animation": "orbit_spin",  # 轨道旋转
        },
        "colors": {
            "primary": (240, 240, 255),
            "secondary": (220, 220, 255),
            "glow": (255, 255, 255),
        },
        "effects": ["plasma_column", "orbital_strike"],
        "particles": ["plasma_arc", "satellite_fragment"],
        "category": "exclusive",
        "exclusive_plane": "titan",
    },
}

# 注意：这只是前21个涂装的重新设计
# 还需要为其他机体(Thunderbird, Viper, Specter, Aurora, Crimson, Stalker, Gaia)
# 以及基础机体(vanguard, reaper, tempest, nexus, blaze, frost, necro)创建类似的详细设计
