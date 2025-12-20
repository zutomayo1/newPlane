# -*- coding: utf-8 -*-
"""
绯红恶魔·SCARLET (Rogue-System "SCARLET")
Project Code: VAMPIRE_SPEAR_X

原型致敬: Scarlet Devil (Calamity Rogue Weapon / Touhou Reference)

设计理念：东方Project幻想风 + 高速截击机 + 吸血鬼美学
视觉关键词：红水晶长枪、蝙蝠粒子、菱形浮游盾、黄金镶边、哥特风

核心机制：潜行刺客 - 吸血 + 潜行一击
特性：极速长枪造型、红色残影、蝙蝠尾迹

【建模要点】
- 机身：极细长枪形态，像一根飞行的红水晶针
- 机头：锋利的三叉戟尖端，中央主刺+两侧副刺
- 材质：深红绯红矿晶体 + 抛光黄金外骨骼
- 机翼：两对菱形红水晶浮游盾，呈X形悬浮
- 驾驶舱：开放式力场，哥特式洋装驾驶员剪影
- 拖尾：蝙蝠状红色粒子喷射

6款涂装设计（高差异化）：
- scarlet_default: 绯红恶魔·猩红之枪 - 标准吸血鬼形态
- scarlet_lunar: 血月降临·红月之夜 - 血月背景+月蚀光环
- scarlet_golden: 黄金魔枪·神枪冈格尼尔 - 神圣金枪+北欧符文
- scarlet_mist: 红雾迷城·深红世界 - 时停迷雾+钟表元素
- scarlet_gothic: 哥特女仆·暗夜侍从 - 银月飞刀+暗夜星辰
- scarlet_destiny: 命运之枪·红色命运 - 命运丝线+宿命符文
"""
import pygame
import math
import random

# =============================================================================
#   核心色值定义 (来自设计文档)
# =============================================================================

SCARLET_COLORS = {
    "crimson": (220, 20, 60),      # #DC143C 猩红主色
    "gold": (255, 215, 0),         # #FFD700 黄金镶边
    "maroon": (128, 0, 0),         # #800000 栗色残影
    "dark_crimson": (139, 0, 0),   # 深红
    "bright_red": (255, 0, 0),     # 亮红
    "blood": (138, 7, 7),          # 血红
}

# =============================================================================
#   6款皮肤主题配置（高差异化）
# =============================================================================

SCARLET_THEMES = {
    # ================= [默认涂装] 绯红恶魔 =================
    "scarlet_default": {
        "name": "绯红恶魔·猩红之枪",
        "desc": "蕾米莉亚的魔枪，猩红的恶魔之力",
        "body": (220, 20, 60),         # 猩红主体
        "crystal": (180, 10, 50),      # 红水晶
        "gold_trim": (255, 215, 0),    # 黄金镶边
        "afterimage": (128, 0, 0),     # 残影栗色
        "bat_particle": (200, 30, 50), # 蝙蝠粒子
        "glow": (255, 50, 80),         # 红光晕
        "shield": (220, 20, 60, 180),  # 浮游盾
        "eye": (255, 0, 0),            # 恶魔之眼
    },
    # ================= [血月系列] 血月降临 =================
    "scarlet_lunar": {
        "name": "血月降临·红月之夜",
        "desc": "血月升起之时，吸血鬼的力量达到巅峰",
        "body": (139, 0, 0),           # 深红
        "crystal": (100, 0, 20),       # 暗红水晶
        "gold_trim": (255, 180, 100),  # 橙金
        "afterimage": (80, 0, 20),     # 深栗残影
        "bat_particle": (160, 20, 40), # 暗蝙蝠
        "glow": (180, 30, 60),         # 暗红光晕
        "shield": (139, 0, 0, 160),    # 血月盾
        "eye": (255, 100, 0),          # 橙红之眼
        "moon_color": (200, 50, 50),   # 血月颜色
    },
    # ================= [神枪系列] 冈格尼尔 =================
    "scarlet_golden": {
        "name": "黄金魔枪·神枪冈格尼尔",
        "desc": "投出必中的神枪，众神之父的武器",
        "body": (255, 215, 0),         # 黄金主体
        "crystal": (255, 200, 50),     # 金水晶
        "gold_trim": (255, 255, 220),  # 亮金镶边
        "afterimage": (200, 150, 0),   # 金残影
        "bat_particle": (255, 220, 80),# 金粒子（不是蝙蝠，是符文）
        "glow": (255, 240, 150),       # 金光晕
        "shield": (255, 215, 0, 180),  # 金盾
        "eye": (255, 255, 200),        # 神圣之眼
        "rune_color": (255, 250, 200), # 北欧符文
    },
    # ================= [红雾系列] 深红世界 =================
    "scarlet_mist": {
        "name": "红雾迷城·深红世界",
        "desc": "时间静止，世界被深红迷雾笼罩",
        "body": (180, 20, 50),         # 雾红
        "crystal": (150, 15, 40),      # 雾晶
        "gold_trim": (200, 180, 160),  # 苍白金
        "afterimage": (100, 30, 50),   # 雾残影
        "bat_particle": (220, 60, 80), # 雾蝙蝠
        "glow": (200, 80, 100),        # 雾光晕
        "shield": (180, 20, 50, 120),  # 迷雾盾
        "eye": (255, 200, 200),        # 迷雾之眼
        "clock_color": (220, 180, 160),# 时钟颜色
    },
    # ================= [哥特系列] 暗夜侍从 =================
    "scarlet_gothic": {
        "name": "哥特女仆·暗夜侍从",
        "desc": "完美优雅的女仆，暗夜中的银色飞刀",
        "body": (30, 20, 30),          # 暗黑
        "crystal": (60, 30, 50),       # 暗紫晶
        "gold_trim": (200, 180, 200),  # 银白边
        "afterimage": (50, 30, 60),    # 暗残影
        "bat_particle": (150, 80, 120),# 紫蝙蝠
        "glow": (180, 100, 150),       # 紫光晕
        "shield": (60, 40, 70, 160),   # 暗夜盾
        "eye": (200, 150, 220),        # 银紫之眼
        "knife_color": (220, 220, 240),# 飞刀银色
    },
    # ================= [命运系列] 红色命运 =================
    "scarlet_destiny": {
        "name": "命运之枪·红色命运",
        "desc": "命运已定，红色的丝线缠绕一切",
        "body": (255, 0, 50),          # 命运红
        "crystal": (220, 0, 40),       # 命运晶
        "gold_trim": (255, 220, 180),  # 命运金
        "afterimage": (180, 0, 30),    # 命运残影
        "bat_particle": (255, 40, 80), # 命运粒子
        "glow": (255, 100, 120),       # 命运光晕
        "shield": (255, 0, 50, 200),   # 命运盾
        "eye": (255, 255, 255),        # 命运之眼（纯白）
        "thread_color": (255, 50, 100),# 命运丝线
    },
}

# 涂装样式列表
SCARLET_STYLES = list(SCARLET_THEMES.keys())


def is_scarlet_style(style):
    """检查是否为SCARLET涂装"""
    return style in SCARLET_STYLES


def get_scarlet_theme(style):
    """获取涂装主题"""
    return SCARLET_THEMES.get(style, SCARLET_THEMES["scarlet_default"])


# =============================================================================
#   通用绘制辅助函数 - 高精度建模（参考Yharon/Cthulhu级别）
# =============================================================================

def _draw_blood_aura_background(s, cx, cy, t, theme):
    """
    绘制血色威压背景 - 类似Cthulhu的深渊涟漪
    吸血鬼的恐怖气息笼罩整个区域
    """
    glow = theme["glow"]
    body = theme["body"]
    
    # ===== 血色涟漪（多层扩散） =====
    for ring in range(5):
        ripple_r = 50 - ring * 8 + int(math.sin(t * 2 + ring * 0.5) * 4)
        ripple_alpha = max(0, 45 - ring * 8)
        if ripple_r > 0 and ripple_alpha > 0:
            ripple_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ripple_surf, (*body[:3], ripple_alpha), (cx, cy), ripple_r)
            s.blit(ripple_surf, (0, 0))
    
    # ===== 恐惧光晕（脉动） =====
    pulse = abs(math.sin(t * 2.5))
    for i in range(6):
        glow_r = int(55 - i * 7 + 5 * math.sin(t * 1.8 + i * 0.4))
        glow_alpha = max(0, int(35 * pulse) - i * 5)
        if glow_r > 0 and glow_alpha > 0:
            glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow[:3], glow_alpha), (cx, cy), glow_r)
            s.blit(glow_surf, (0, 0))
    
    # ===== 血雾粒子（飘散） =====
    mist_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(12):
        mist_angle = t * 0.3 + i * 0.52
        mist_r = 30 + i * 3 + math.sin(t * 1.5 + i) * 8
        mist_x = cx + math.cos(mist_angle) * mist_r
        mist_y = cy + math.sin(mist_angle * 0.7) * mist_r * 0.6
        mist_size = 8 + math.sin(t * 2 + i * 0.8) * 3
        mist_alpha = int(25 + math.sin(t * 3 + i) * 10)
        pygame.draw.circle(mist_surf, (*body[:3], mist_alpha), (int(mist_x), int(mist_y)), int(mist_size))
    s.blit(mist_surf, (0, 0))


def _draw_lance_body(s, cx, cy, t, theme, scale=1.0):
    """
    绘制极细长枪机身 - 三叉戟形态（Yharon级别建模）
    参考龙躯主装甲的多层设计：外层轮廓+内层装甲+装甲纹理+能量脉络
    """
    body_color = theme["body"]
    gold = theme["gold_trim"]
    crystal = theme["crystal"]
    glow = theme["glow"]
    
    # 颜色变体（参考Yharon）
    body_light = tuple(min(255, c + 50) for c in body_color)
    body_dark = tuple(max(0, c - 40) for c in body_color)
    body_shadow = tuple(max(0, c - 70) for c in body_color)
    crystal_light = tuple(min(255, c + 40) for c in crystal)
    
    # 动态参数
    pulse = 1.0 + math.sin(t * 4) * 0.08
    breath = math.sin(t * 2) * 2
    
    # ===== 【第一层】枪身外层装甲 =====
    outer_armor = [
        (cx, cy - 50 * scale),              # 枪尖
        (cx - 3 * scale, cy - 44 * scale),  # 尖端过渡
        (cx - 7 * scale, cy - 32 * scale),  # 左上肩
        (cx - 9 * scale, cy - 15 * scale),  # 左上腰
        (cx - 8 * scale, cy + 5 * scale),   # 左腰
        (cx - 7 * scale, cy + 20 * scale),  # 左下腰
        (cx - 5 * scale, cy + 34 * scale),  # 左尾根
        (cx, cy + 42 * scale),              # 尾尖
        (cx + 5 * scale, cy + 34 * scale),  # 右尾根
        (cx + 7 * scale, cy + 20 * scale),  # 右下腰
        (cx + 8 * scale, cy + 5 * scale),   # 右腰
        (cx + 9 * scale, cy - 15 * scale),  # 右上腰
        (cx + 7 * scale, cy - 32 * scale),  # 右上肩
        (cx + 3 * scale, cy - 44 * scale),  # 尖端过渡
    ]
    outer_armor = [(int(p[0]), int(p[1])) for p in outer_armor]
    pygame.draw.polygon(s, body_shadow, outer_armor)
    pygame.draw.polygon(s, gold, outer_armor, 2)
    
    # ===== 【第二层】内层装甲（高光区域） =====
    inner_armor = [
        (cx, cy - 47 * scale),
        (cx - 5 * scale, cy - 30 * scale),
        (cx - 6 * scale, cy - 10 * scale),
        (cx - 5 * scale, cy + 15 * scale),
        (cx - 3 * scale, cy + 32 * scale),
        (cx, cy + 38 * scale),
        (cx + 3 * scale, cy + 32 * scale),
        (cx + 5 * scale, cy + 15 * scale),
        (cx + 6 * scale, cy - 10 * scale),
        (cx + 5 * scale, cy - 30 * scale),
    ]
    inner_armor = [(int(p[0]), int(p[1])) for p in inner_armor]
    pygame.draw.polygon(s, body_dark, inner_armor)
    
    # ===== 【第三层】核心高光 =====
    core_highlight = [
        (cx, cy - 44 * scale),
        (cx - 3 * scale, cy - 25 * scale),
        (cx - 4 * scale, cy + 10 * scale),
        (cx, cy + 35 * scale),
        (cx + 4 * scale, cy + 10 * scale),
        (cx + 3 * scale, cy - 25 * scale),
    ]
    core_highlight = [(int(p[0]), int(p[1])) for p in core_highlight]
    pygame.draw.polygon(s, body_color, core_highlight)
    
    # ===== 装甲分节线（参考龙鳞） =====
    for i in range(7):
        seg_y = cy - 35 * scale + i * 11 * scale
        seg_width = 5 + i * 0.5 if i < 4 else 8 - (i - 4) * 1.5
        seg_width = max(2, seg_width) * scale
        
        # 分节装甲板
        pygame.draw.line(s, body_light, 
                        (int(cx - seg_width), int(seg_y)),
                        (int(cx + seg_width), int(seg_y)), 1)
        # 铆钉装饰
        if i % 2 == 0:
            pygame.draw.circle(s, gold, (int(cx - seg_width - 2), int(seg_y)), 2)
            pygame.draw.circle(s, gold, (int(cx + seg_width + 2), int(seg_y)), 2)
    
    # ===== 能量脉络（发光纹路） =====
    vein_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    vein_pulse = int(80 + math.sin(t * 5) * 40)
    # 中央主脉
    pygame.draw.line(vein_surf, (*glow[:3], vein_pulse), 
                    (int(cx), int(cy - 42 * scale)), (int(cx), int(cy + 32 * scale)), 2)
    # 分支脉络
    for i in range(4):
        vy = cy - 25 * scale + i * 15 * scale
        vx_offset = 3 + i * 0.5
        pygame.draw.line(vein_surf, (*glow[:3], vein_pulse // 2),
                        (int(cx), int(vy)), (int(cx - vx_offset * scale), int(vy + 8)), 1)
        pygame.draw.line(vein_surf, (*glow[:3], vein_pulse // 2),
                        (int(cx), int(vy)), (int(cx + vx_offset * scale), int(vy + 8)), 1)
    s.blit(vein_surf, (0, 0))
    
    # ===== 三叉戟 - 恶魔之矛（详细版） =====
    _draw_trident_head(s, cx, cy - 50 * scale, t, theme, scale, pulse)
    
    # ===== 恶魔之眼核心（参考Cthulhu邪神之眼） =====
    _draw_demon_eye(s, cx, cy - 8 * scale + breath, t, theme, scale)
    
    # ===== 枪尾装饰 =====
    tail_y = cy + 42 * scale
    # 尾部晶体
    pygame.draw.polygon(s, crystal, [
        (int(cx), int(tail_y + 8 * scale * pulse)),
        (int(cx - 4 * scale), int(tail_y)),
        (int(cx + 4 * scale), int(tail_y)),
    ])
    pygame.draw.polygon(s, gold, [
        (int(cx), int(tail_y + 8 * scale * pulse)),
        (int(cx - 4 * scale), int(tail_y)),
        (int(cx + 4 * scale), int(tail_y)),
    ], 1)


def _draw_trident_head(s, cx, cy, t, theme, scale, pulse):
    """
    绘制三叉戟枪头 - 恶魔之矛（详细版）
    中央主刺 + 两侧弯曲副刺 + 装饰环 + 能量光芒
    """
    body = theme["body"]
    gold = theme["gold_trim"]
    crystal = theme["crystal"]
    glow = theme["glow"]
    
    body_light = tuple(min(255, c + 60) for c in body)
    body_dark = tuple(max(0, c - 30) for c in body)
    
    # ===== 中央主刺（最长最锐利） =====
    main_len = 18 * scale * pulse
    main_spike = [
        (cx, cy - main_len),           # 极尖顶点
        (cx - 4 * scale, cy + 2 * scale),    # 左底
        (cx - 2 * scale, cy + 8 * scale),    # 左下
        (cx + 2 * scale, cy + 8 * scale),    # 右下
        (cx + 4 * scale, cy + 2 * scale),    # 右底
    ]
    main_spike = [(int(p[0]), int(p[1])) for p in main_spike]
    pygame.draw.polygon(s, body_dark, main_spike)
    pygame.draw.polygon(s, gold, main_spike, 1)
    
    # 主刺内部高光
    inner_spike = [
        (cx, cy - main_len + 3 * scale),
        (cx - 2 * scale, cy + 4 * scale),
        (cx + 2 * scale, cy + 4 * scale),
    ]
    inner_spike = [(int(p[0]), int(p[1])) for p in inner_spike]
    pygame.draw.polygon(s, body, inner_spike)
    
    # 主刺能量线
    pygame.draw.line(s, body_light, (int(cx), int(cy - main_len + 2)), (int(cx), int(cy + 5 * scale)), 1)
    
    # ===== 左侧副刺（向外弯曲） =====
    left_base_x = cx - 6 * scale
    left_base_y = cy + 5 * scale
    left_tip_x = cx - 18 * scale
    left_tip_y = cy - 10 * scale * pulse
    
    # 副刺主体（弧形）
    left_spike = [
        (left_tip_x, left_tip_y),
        (left_base_x - 2 * scale, left_base_y - 4 * scale),
        (left_base_x, left_base_y),
        (left_base_x + 2 * scale, left_base_y + 4 * scale),
        (cx - 4 * scale, cy + 10 * scale),
    ]
    left_spike = [(int(p[0]), int(p[1])) for p in left_spike]
    pygame.draw.polygon(s, body_dark, left_spike)
    pygame.draw.polygon(s, gold, left_spike, 1)
    
    # 副刺内高光
    pygame.draw.line(s, body, (int(left_tip_x + 2), int(left_tip_y + 2)), 
                    (int(left_base_x), int(left_base_y)), 2)
    
    # ===== 右侧副刺（镜像） =====
    right_base_x = cx + 6 * scale
    right_base_y = cy + 5 * scale
    right_tip_x = cx + 18 * scale
    right_tip_y = cy - 10 * scale * pulse
    
    right_spike = [
        (right_tip_x, right_tip_y),
        (right_base_x + 2 * scale, right_base_y - 4 * scale),
        (right_base_x, right_base_y),
        (right_base_x - 2 * scale, right_base_y + 4 * scale),
        (cx + 4 * scale, cy + 10 * scale),
    ]
    right_spike = [(int(p[0]), int(p[1])) for p in right_spike]
    pygame.draw.polygon(s, body_dark, right_spike)
    pygame.draw.polygon(s, gold, right_spike, 1)
    
    pygame.draw.line(s, body, (int(right_tip_x - 2), int(right_tip_y + 2)),
                    (int(right_base_x), int(right_base_y)), 2)
    
    # ===== 三叉戟连接环（双层金环） =====
    ring_y = cy + 10 * scale
    pygame.draw.circle(s, gold, (int(cx), int(ring_y)), int(8 * scale), 2)
    pygame.draw.circle(s, crystal, (int(cx), int(ring_y)), int(5 * scale))
    pygame.draw.circle(s, body_light, (int(cx), int(ring_y)), int(3 * scale))
    
    # ===== 刺尖能量光芒 =====
    tip_glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    tip_alpha = int(100 + math.sin(t * 6) * 50)
    
    # 主刺尖光芒
    pygame.draw.circle(tip_glow_surf, (*glow[:3], tip_alpha), (int(cx), int(cy - main_len)), 4)
    pygame.draw.circle(tip_glow_surf, (255, 255, 255, tip_alpha // 2), (int(cx), int(cy - main_len)), 2)
    
    # 副刺尖光芒
    pygame.draw.circle(tip_glow_surf, (*glow[:3], tip_alpha // 2), (int(left_tip_x), int(left_tip_y)), 3)
    pygame.draw.circle(tip_glow_surf, (*glow[:3], tip_alpha // 2), (int(right_tip_x), int(right_tip_y)), 3)
    
    s.blit(tip_glow_surf, (0, 0))


def _draw_demon_eye(s, cx, cy, t, theme, scale):
    """
    绘制恶魔之眼（参考Cthulhu邪神之眼）
    血丝 + 虹膜纹理 + 竖瞳 + 多层光晕 + 动态瞳孔
    """
    eye_color = theme.get("eye", (255, 0, 0))
    glow = theme["glow"]
    gold = theme["gold_trim"]
    
    eye_size = int(10 * scale)
    
    # ===== 眼眶发光（恐惧威压） =====
    for i in range(6):
        glow_r = eye_size + (6 - i) * 4
        alpha = 60 - i * 10
        if alpha > 0:
            glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow[:3], alpha), (int(cx), int(cy)), glow_r)
            s.blit(glow_surf, (0, 0))
    
    # ===== 眼白（略带病态黄） =====
    sclera = (220, 200, 180)
    pygame.draw.ellipse(s, sclera, (int(cx - eye_size), int(cy - eye_size * 0.6), 
                                    int(eye_size * 2), int(eye_size * 1.2)))
    
    # ===== 血丝（6条） =====
    bloodshot_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(8):
        angle = (i * 45 + t * 10) * 0.01745
        bx = cx + math.cos(angle) * eye_size * 0.85
        by = cy + math.sin(angle) * eye_size * 0.5
        pygame.draw.line(bloodshot_surf, (180, 40, 40, 120), (int(cx), int(cy)), (int(bx), int(by)), 1)
    s.blit(bloodshot_surf, (0, 0))
    
    # ===== 虹膜（带纹理） =====
    iris_r = int(eye_size * 0.6)
    wobble_x = math.sin(t * 1.5) * 1.5
    wobble_y = math.cos(t * 1.2) * 1
    iris_cx = int(cx + wobble_x)
    iris_cy = int(cy + wobble_y)
    
    pygame.draw.circle(s, eye_color, (iris_cx, iris_cy), iris_r)
    
    # 虹膜辐射纹
    iris_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(12):
        ring_angle = i * math.pi / 6 + t * 0.15
        rx = iris_cx + math.cos(ring_angle) * iris_r * 0.8
        ry = iris_cy + math.sin(ring_angle) * iris_r * 0.5
        iris_darker = tuple(max(0, c - 50) for c in eye_color)
        pygame.draw.line(iris_surf, (*iris_darker, 150), (iris_cx, iris_cy), (int(rx), int(ry)), 1)
    s.blit(iris_surf, (0, 0))
    
    # ===== 竖瞳（恶魔特征，会收缩） =====
    pupil_contract = abs(math.sin(t * 3)) * 2
    pupil_w = max(2, int(3 * scale - pupil_contract))
    pupil_h = int(eye_size * 0.9)
    
    pygame.draw.ellipse(s, (0, 0, 0), 
                       (iris_cx - pupil_w // 2, iris_cy - pupil_h // 2, pupil_w, pupil_h))
    
    # ===== 高光点 =====
    pygame.draw.circle(s, (255, 255, 255), (int(cx - eye_size * 0.3), int(cy - eye_size * 0.25)), 2)
    pygame.draw.circle(s, (255, 255, 255, 150), (int(cx + eye_size * 0.2), int(cy + eye_size * 0.15)), 1)
    
    # ===== 金边眼眶 =====
    pygame.draw.ellipse(s, gold, (int(cx - eye_size), int(cy - eye_size * 0.6),
                                  int(eye_size * 2), int(eye_size * 1.2)), 2)


def _draw_crystal_wings(s, cx, cy, t, theme, scale=1.0):
    """
    绘制菱形红水晶浮游盾 - X形排列（Providence级别）
    参考Providence的圣火羽翼和祭坛浮游炮
    4个大型浮游盾 + 能量连接 + 晶体内部纹理 + 旋转符文
    """
    crystal_color = theme["crystal"]
    gold = theme["gold_trim"]
    glow = theme["glow"]
    shield_color = theme.get("shield", (*crystal_color, 180))
    
    crystal_light = tuple(min(255, c + 50) for c in crystal_color)
    crystal_dark = tuple(max(0, c - 40) for c in crystal_color)
    
    # 浮动参数
    hover = math.sin(t * 2.5) * 5
    
    # X形排列的4个菱形浮游盾（更大更有压迫感）
    wing_configs = [
        (cx - 32, cy - 15, 25, 0.0),        # 左上（更远）
        (cx + 32, cy - 15, -25, 0.5),       # 右上
        (cx - 28, cy + 22, 155, 1.0),       # 左下
        (cx + 28, cy + 22, -155, 1.5),      # 右下
    ]
    
    for idx, (wx, wy, base_angle, phase) in enumerate(wing_configs):
        # 独立浮动（更大幅度）
        float_x = math.sin(t * 1.8 + phase) * 3
        float_y = math.sin(t * 2 + phase) * 4 + hover * (0.5 if idx < 2 else -0.5)
        wx += float_x
        wy += float_y
        
        # 菱形尺寸（更大）
        w_size = 16 * scale
        h_size = 26 * scale
        
        # 微旋转
        rotation = math.radians(base_angle + math.sin(t * 1.5 + phase) * 10)
        
        # 菱形四个顶点
        diamond_points = [
            (0, -h_size),   # 上尖
            (w_size, 0),    # 右尖
            (0, h_size),    # 下尖
            (-w_size, 0),   # 左尖
        ]
        
        # 旋转变换
        rotated = []
        for px, py in diamond_points:
            rx = px * math.cos(rotation) - py * math.sin(rotation)
            ry = px * math.sin(rotation) + py * math.cos(rotation)
            rotated.append((int(wx + rx), int(wy + ry)))
        
        # ===== 【第一层】外发光光晕 =====
        for i in range(4):
            glow_pts = []
            glow_scale = 1.0 + i * 0.12
            for px, py in diamond_points:
                rx = px * glow_scale * math.cos(rotation) - py * glow_scale * math.sin(rotation)
                ry = px * glow_scale * math.sin(rotation) + py * glow_scale * math.cos(rotation)
                glow_pts.append((int(wx + rx), int(wy + ry)))
            alpha = 50 - i * 12
            if alpha > 0:
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.polygon(glow_surf, (*glow[:3], alpha), glow_pts)
                s.blit(glow_surf, (0, 0))
        
        # ===== 【第二层】晶体主体（渐变） =====
        shield_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 外层（暗）
        if len(shield_color) == 4:
            pygame.draw.polygon(shield_surf, shield_color, rotated)
        else:
            pygame.draw.polygon(shield_surf, (*crystal_dark, 200), rotated)
        
        # 内层（亮）
        inner_scale = 0.7
        inner_pts = []
        for px, py in diamond_points:
            rx = px * inner_scale * math.cos(rotation) - py * inner_scale * math.sin(rotation)
            ry = px * inner_scale * math.sin(rotation) + py * inner_scale * math.cos(rotation)
            inner_pts.append((int(wx + rx), int(wy + ry)))
        pygame.draw.polygon(shield_surf, (*crystal_light, 180), inner_pts)
        
        s.blit(shield_surf, (0, 0))
        
        # ===== 【第三层】晶体内部纹理 =====
        texture_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        texture_alpha = int(120 + math.sin(t * 3 + phase) * 40)
        
        # 对角线
        pygame.draw.line(texture_surf, (*crystal_color, texture_alpha), rotated[0], rotated[2], 1)
        pygame.draw.line(texture_surf, (*crystal_color, texture_alpha), rotated[1], rotated[3], 1)
        
        # 内部菱形
        tiny_scale = 0.35
        tiny_pts = []
        for px, py in diamond_points:
            rx = px * tiny_scale * math.cos(rotation) - py * tiny_scale * math.sin(rotation)
            ry = px * tiny_scale * math.sin(rotation) + py * tiny_scale * math.cos(rotation)
            tiny_pts.append((int(wx + rx), int(wy + ry)))
        pygame.draw.polygon(texture_surf, (*crystal_light, texture_alpha), tiny_pts, 1)
        
        s.blit(texture_surf, (0, 0))
        
        # ===== 金边轮廓 =====
        pygame.draw.polygon(s, gold, rotated, 2)
        
        # ===== 中心能量核心 =====
        core_pulse = 1 + math.sin(t * 5 + phase) * 0.4
        core_r = int(5 * core_pulse)
        
        # 核心光晕
        for i in range(3):
            core_glow_r = core_r + (3 - i) * 3
            core_alpha = 80 - i * 25
            pygame.draw.circle(s, (*glow[:3], core_alpha), (int(wx), int(wy)), core_glow_r)
        
        pygame.draw.circle(s, glow, (int(wx), int(wy)), core_r)
        pygame.draw.circle(s, (255, 255, 255), (int(wx), int(wy)), max(1, core_r - 2))
        
        # ===== 能量连接线（到主体） =====
        line_alpha = int(80 + math.sin(t * 4 + phase) * 40)
        energy_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 双线连接
        pygame.draw.line(energy_surf, (*glow[:3], line_alpha), (int(wx), int(wy)), (int(cx), int(cy)), 2)
        pygame.draw.line(energy_surf, (255, 255, 255, line_alpha // 2), (int(wx), int(wy)), (int(cx), int(cy)), 1)
        
        # 能量粒子
        particle_count = 3
        for p in range(particle_count):
            progress = (t * 2 + phase + p * 0.3) % 1.0
            px = wx + (cx - wx) * progress
            py = wy + (cy - wy) * progress
            p_alpha = int(100 * (1 - abs(progress - 0.5) * 2))
            pygame.draw.circle(energy_surf, (*glow[:3], p_alpha), (int(px), int(py)), 2)
        
        s.blit(energy_surf, (0, 0))
        
        # ===== 浮游盾旋转符文 =====
        rune_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        rune_r = h_size * 0.6
        for i in range(4):
            rune_angle = t * 2 + phase + i * (math.pi / 2)
            rx = wx + math.cos(rune_angle) * rune_r
            ry = wy + math.sin(rune_angle) * rune_r
            rune_alpha = int(80 + math.sin(t * 4 + i) * 40)
            pygame.draw.circle(rune_surf, (*gold[:3], rune_alpha), (int(rx), int(ry)), 2)
        s.blit(rune_surf, (0, 0))


def _draw_afterimage(s, cx, cy, t, theme, scale=1.0):
    """
    绘制红色残影效果（增强版）
    8层渐变残影 + 速度线 + 残像闪烁
    """
    afterimage_color = theme["afterimage"]
    glow = theme["glow"]
    
    # ===== 多层残影（8层，更强的视觉拖尾） =====
    for i in range(8):
        # 残影位置偏移（向后+轻微抖动）
        offset_y = i * 7
        offset_x = math.sin(t * 6 - i * 0.6) * (i * 0.6)
        alpha = 160 - i * 20
        
        if alpha <= 0:
            continue
        
        ghost_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 残影轮廓（简化的枪身形状）
        ghost_points = [
            (cx + offset_x, cy - 48 * scale + offset_y),
            (cx + offset_x - 6 * scale, cy - 30 * scale + offset_y),
            (cx + offset_x - 7 * scale, cy + 10 * scale + offset_y),
            (cx + offset_x, cy + 38 * scale + offset_y),
            (cx + offset_x + 7 * scale, cy + 10 * scale + offset_y),
            (cx + offset_x + 6 * scale, cy - 30 * scale + offset_y),
        ]
        ghost_points = [(int(p[0]), int(p[1])) for p in ghost_points]
        
        # 残影颜色渐变（越远越暗越红）
        fade_r = min(255, afterimage_color[0] + i * 5)
        fade_g = max(0, afterimage_color[1] - i * 3)
        fade_b = max(0, afterimage_color[2] - i * 3)
        
        pygame.draw.polygon(ghost_surf, (fade_r, fade_g, fade_b, alpha), ghost_points)
        s.blit(ghost_surf, (0, 0))
    
    # ===== 速度线 =====
    speed_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(5):
        line_x = cx - 15 + i * 7 + math.sin(t * 8 + i) * 3
        line_y_start = cy + 20 + i * 3
        line_y_end = cy + 40 + i * 5 + math.sin(t * 5 + i) * 5
        line_alpha = 60 - i * 10
        pygame.draw.line(speed_surf, (*afterimage_color, line_alpha), 
                        (int(line_x), int(line_y_start)), (int(line_x), int(line_y_end)), 1)
    s.blit(speed_surf, (0, 0))


def _draw_bat_exhaust(s, cx, cy, t, theme, scale=1.0):
    """
    绘制蝙蝠状红色粒子尾迹（Yharon级别）
    参考Yharon的引擎尾焰设计：多层火焰 + 详细蝙蝠 + 蝙蝠群动态
    """
    bat_color = theme["bat_particle"]
    glow = theme["glow"]
    body = theme["body"]
    
    exhaust_y = cy + 42 * scale
    
    # ===== 尾部喷射核心（多层） =====
    exhaust_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    # 外层光晕
    for i in range(4):
        ex_r = 10 - i * 2
        ex_alpha = 60 - i * 15
        if ex_r > 0 and ex_alpha > 0:
            pygame.draw.circle(exhaust_surf, (*glow[:3], ex_alpha), (int(cx), int(exhaust_y)), ex_r)
    
    # 核心火焰
    flame_height = 12 + int(6 * math.sin(t * 8))
    flame_pts = [
        (cx - 5, exhaust_y - 2),
        (cx, exhaust_y + flame_height),
        (cx + 5, exhaust_y - 2),
    ]
    flame_pts = [(int(p[0]), int(p[1])) for p in flame_pts]
    pygame.draw.polygon(exhaust_surf, (*bat_color, 180), flame_pts)
    
    # 内焰
    inner_flame = [
        (cx - 2, exhaust_y),
        (cx, exhaust_y + flame_height - 4),
        (cx + 2, exhaust_y),
    ]
    inner_flame = [(int(p[0]), int(p[1])) for p in inner_flame]
    pygame.draw.polygon(exhaust_surf, (*glow, 200), inner_flame)
    
    s.blit(exhaust_surf, (0, 0))
    
    # ===== 蝙蝠群（12只，更详细） =====
    random.seed(int(t * 10) % 1000)
    
    for i in range(12):
        # 粒子生命周期
        age = (t * 2.2 + i * 0.22) % 2.8
        if age > 2.2:
            continue
        
        # 位置：从尾部向下飘散，带横向摆动
        progress = age / 2.2
        particle_y = exhaust_y + 5 + progress * 35
        spread = math.sin(t * 5 + i * 1.1) * (6 + progress * 18)
        particle_x = cx + spread
        
        # 蝙蝠尺寸（近大远小）
        bat_size = max(4, int((1 - progress * 0.5) * 10))
        alpha = int((1 - progress * 0.7) * 240)
        
        if alpha < 40:
            continue
        
        bat_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # ===== 详细蝙蝠形状 =====
        wing_span = bat_size * 2.8
        wing_flap = math.sin(t * 20 + i * 2.5) * (bat_size * 0.5)  # 翅膀拍动
        
        # 蝙蝠身体（椭圆）
        body_w = int(bat_size * 0.9)
        body_h = int(bat_size * 0.7)
        pygame.draw.ellipse(bat_surf, (*bat_color, alpha), 
                          (int(particle_x - body_w // 2), int(particle_y - body_h // 2), body_w, body_h))
        
        # 左翅膀（多边形，更详细）
        left_wing = [
            (particle_x - bat_size * 0.35, particle_y - bat_size * 0.1),
            (particle_x - wing_span * 0.5, particle_y - bat_size * 0.4 - wing_flap),
            (particle_x - wing_span, particle_y - wing_flap * 0.8),
            (particle_x - wing_span * 0.8, particle_y + bat_size * 0.3),
            (particle_x - wing_span * 0.5, particle_y + bat_size * 0.35),
            (particle_x - bat_size * 0.3, particle_y + bat_size * 0.25),
        ]
        left_wing = [(int(p[0]), int(p[1])) for p in left_wing]
        pygame.draw.polygon(bat_surf, (*bat_color, alpha), left_wing)
        
        # 右翅膀（镜像）
        right_wing = [
            (particle_x + bat_size * 0.35, particle_y - bat_size * 0.1),
            (particle_x + wing_span * 0.5, particle_y - bat_size * 0.4 - wing_flap),
            (particle_x + wing_span, particle_y - wing_flap * 0.8),
            (particle_x + wing_span * 0.8, particle_y + bat_size * 0.3),
            (particle_x + wing_span * 0.5, particle_y + bat_size * 0.35),
            (particle_x + bat_size * 0.3, particle_y + bat_size * 0.25),
        ]
        right_wing = [(int(p[0]), int(p[1])) for p in right_wing]
        pygame.draw.polygon(bat_surf, (*bat_color, alpha), right_wing)
        
        # 蝙蝠头部
        head_y = particle_y - bat_size * 0.45
        head_r = max(2, bat_size // 3)
        pygame.draw.circle(bat_surf, (*bat_color, alpha), (int(particle_x), int(head_y)), head_r)
        
        # 小耳朵（两个三角）
        ear_h = max(2, bat_size // 3)
        # 左耳
        pygame.draw.polygon(bat_surf, (*bat_color, alpha), [
            (int(particle_x - head_r * 0.6), int(head_y - head_r * 0.3)),
            (int(particle_x - head_r * 1.2), int(head_y - head_r - ear_h)),
            (int(particle_x - head_r * 0.2), int(head_y - head_r * 0.5)),
        ])
        # 右耳
        pygame.draw.polygon(bat_surf, (*bat_color, alpha), [
            (int(particle_x + head_r * 0.6), int(head_y - head_r * 0.3)),
            (int(particle_x + head_r * 1.2), int(head_y - head_r - ear_h)),
            (int(particle_x + head_r * 0.2), int(head_y - head_r * 0.5)),
        ])
        
        # 小眼睛（两个红点）
        eye_r = max(1, bat_size // 6)
        eye_alpha = min(255, alpha + 30)
        pygame.draw.circle(bat_surf, (*glow[:3], eye_alpha), (int(particle_x - head_r * 0.4), int(head_y)), eye_r)
        pygame.draw.circle(bat_surf, (*glow[:3], eye_alpha), (int(particle_x + head_r * 0.4), int(head_y)), eye_r)
        
        s.blit(bat_surf, (0, 0))
    
    # ===== 蝙蝠群尾迹光 =====
    trail_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(6):
        trail_y = exhaust_y + 10 + i * 8
        trail_alpha = 40 - i * 6
        trail_w = 12 - i * 1.5
        if trail_alpha > 0 and trail_w > 0:
            pygame.draw.ellipse(trail_surf, (*bat_color, trail_alpha),
                              (int(cx - trail_w), int(trail_y - 2), int(trail_w * 2), 5))
    s.blit(trail_surf, (0, 0))


def _draw_pressure_aura(s, cx, cy, t, theme, intensity=1.0):
    """
    绘制压迫感光环 - 恶魔威压（增强版）
    参考Providence的神圣几何：多层波纹 + 符文环 + 暗角效果
    """
    glow = theme["glow"]
    body = theme["body"]
    gold = theme["gold_trim"]
    
    # ===== 恐惧波纹（从中心向外扩散） =====
    for i in range(5):
        wave_progress = (t * 0.6 + i * 0.2) % 1.0
        wave_r = 15 + wave_progress * 45
        wave_alpha = int(80 * (1 - wave_progress) * intensity)
        
        if wave_alpha < 8:
            continue
        
        wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(wave_surf, (*glow[:3], wave_alpha), (int(cx), int(cy)), int(wave_r), 2)
        s.blit(wave_surf, (0, 0))
    
    # ===== 六芒星几何（神圣几何参考Providence） =====
    hex_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    hex_r = 48 + math.sin(t * 1.5) * 4
    hex_alpha = int(40 * intensity)
    
    for ring in range(2):
        ring_r = hex_r - ring * 10
        if ring_r > 0:
            hex_pts = []
            for i in range(6):
                angle = math.radians(i * 60 + 30 + t * 8)
                hx = cx + math.cos(angle) * ring_r
                hy = cy + math.sin(angle) * ring_r
                hex_pts.append((int(hx), int(hy)))
            pygame.draw.polygon(hex_surf, (*body[:3], hex_alpha - ring * 15), hex_pts, 1)
    s.blit(hex_surf, (0, 0))
    
    # ===== 暗角效果（四角暗化增加压迫感） =====
    corner_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    corner_alpha = int(40 * intensity)
    
    for corner_x, corner_y in [(0, 0), (120, 0), (0, 120), (120, 120)]:
        for i in range(6):
            corner_r = 35 - i * 5
            c_alpha = corner_alpha - i * 6
            if c_alpha > 0 and corner_r > 0:
                pygame.draw.circle(corner_surf, (0, 0, 0, c_alpha), (corner_x, corner_y), corner_r)
    s.blit(corner_surf, (0, 0))


# =============================================================================
#   独立涂装绘制函数 - 高差异化设计（Yharon/Cthulhu级别）
# =============================================================================

def draw_scarlet_default(s, cx, cy, w, h, t):
    """
    【默认涂装】绯红恶魔·猩红之枪
    核心配色：猩红晶体 + 黄金镶边
    特色元素：标准吸血鬼形态、恶魔之眼、血色威压、血雨飞溅
    
    设计理念：雷米莉亚·斯卡雷特的本体形态
    - 血腥威压笼罩全场
    - 鲜血环绕机体飞溅
    - 标准的吸血鬼形态展示
    """
    theme = get_scarlet_theme("scarlet_default")
    
    # ========== 第一层：血色威压背景 ==========
    _draw_blood_aura_background(s, cx, cy, t, theme)
    _draw_pressure_aura(s, cx, cy, t, theme, 1.0)
    
    # ========== 第二层：血雨飞溅（特色效果） ==========
    blood_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    # 12颗血滴环绕
    for i in range(12):
        drop_age = (t * 1.8 + i * 0.52) % 3.0
        drop_angle = t * 0.8 + i * (math.pi / 6)
        drop_r = 25 + drop_age * 15 + math.sin(t * 2 + i) * 3
        drop_x = cx + math.cos(drop_angle) * drop_r
        drop_y = cy + math.sin(drop_angle) * drop_r - 5 + drop_age * 8
        
        # 血滴大小随生命周期变化
        drop_size = max(2, int((3 - drop_age) * 3))
        drop_alpha = int((1 - drop_age / 3.0) * 200)
        
        if drop_alpha < 20:
            continue
        
        # 血滴主体（更详细的泪滴形）
        pygame.draw.circle(blood_surf, (200, 20, 40, drop_alpha), (int(drop_x), int(drop_y)), drop_size)
        
        # 血滴尾巴（拉长）
        tail_len = drop_size + 5 + int(drop_age * 2)
        tail_pts = [
            (int(drop_x), int(drop_y + drop_size)),
            (int(drop_x - drop_size * 0.6), int(drop_y + tail_len)),
            (int(drop_x + drop_size * 0.6), int(drop_y + tail_len)),
        ]
        pygame.draw.polygon(blood_surf, (180, 10, 30, drop_alpha - 30), tail_pts)
        
        # 血滴高光
        pygame.draw.circle(blood_surf, (255, 150, 150, drop_alpha // 2), 
                          (int(drop_x - drop_size * 0.3), int(drop_y - drop_size * 0.3)), max(1, drop_size // 3))
    
    # 溅射血点
    for i in range(20):
        splash_age = (t * 3 + i * 0.15) % 1.5
        splash_angle = t * 1.5 + i * 0.31
        splash_r = 15 + splash_age * 30
        splash_x = cx + math.cos(splash_angle) * splash_r
        splash_y = cy + math.sin(splash_angle) * splash_r
        splash_alpha = int((1 - splash_age / 1.5) * 120)
        
        if splash_alpha > 10:
            pygame.draw.circle(blood_surf, (220, 30, 50, splash_alpha), (int(splash_x), int(splash_y)), 1)
    
    s.blit(blood_surf, (0, 0))
    
    # ========== 第三层：残影 ==========
    _draw_afterimage(s, cx, cy, t, theme)
    
    # ========== 第四层：浮游盾 ==========
    _draw_crystal_wings(s, cx, cy, t, theme)
    
    # ========== 第五层：枪身主体 ==========
    _draw_lance_body(s, cx, cy, t, theme)
    
    # ========== 第六层：蝙蝠尾迹 ==========
    _draw_bat_exhaust(s, cx, cy, t, theme)
    
    # ========== 第七层：血腥光晕强化 ==========
    final_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
    glow_pulse = 1 + math.sin(t * 3) * 0.3
    for i in range(3):
        glow_r = int(8 * glow_pulse) + i * 4
        glow_alpha = 100 - i * 30
        pygame.draw.circle(final_glow, (255, 100, 100, glow_alpha), (int(cx), int(cy - 25)), glow_r)
    s.blit(final_glow, (0, 0))


def draw_scarlet_lunar(s, cx, cy, w, h, t):
    """
    【血月涂装】血月降临·红月之夜
    核心配色：深红 + 橙金
    特色元素：巨大血月背景、月蚀光环、血色潮汐、月面裂痕
    
    设计理念：红雾异变之夜的完美再现
    - 巨大血月笼罩整个画面
    - 月蚀产生不祥的暗影
    - 潮汐符文环绕脉动
    """
    theme = get_scarlet_theme("scarlet_lunar")
    
    # ========== 第一层：巨大血月背景（占据大半画面） ==========
    moon_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    moon_pulse = 1 + math.sin(t * 0.8) * 0.1
    moon_r = int(52 * moon_pulse)
    
    # 【月晕】多层渐变光晕（12层，从暗红到黑）
    for i in range(12):
        halo_r = moon_r + i * 5
        halo_alpha = 60 - i * 5
        if halo_alpha > 0:
            pygame.draw.circle(moon_surf, (120, 10, 20, halo_alpha), (int(cx), int(cy)), halo_r)
    
    # 【月面】三层月球表面
    # 外层：暗红
    pygame.draw.circle(moon_surf, (139, 20, 30, 200), (int(cx), int(cy)), moon_r)
    # 中层：血红渐变
    pygame.draw.circle(moon_surf, (180, 50, 60, 180), (int(cx), int(cy)), int(moon_r * 0.85))
    # 内层：亮红核心
    pygame.draw.circle(moon_surf, (200, 80, 80, 160), (int(cx), int(cy)), int(moon_r * 0.65))
    
    # 【月蚀】缓慢移动的暗影
    eclipse_x = math.sin(t * 0.3) * 12
    eclipse_y = math.cos(t * 0.4) * 6
    pygame.draw.circle(moon_surf, (30, 5, 15, 200), 
                      (int(cx + eclipse_x), int(cy + eclipse_y)), int(moon_r * 0.65))
    pygame.draw.circle(moon_surf, (50, 10, 20, 180), 
                      (int(cx + eclipse_x), int(cy + eclipse_y)), int(moon_r * 0.55))
    
    # 【月面纹理】环形山和裂痕
    for i in range(8):
        crater_angle = i * 0.79 + math.sin(t * 0.2 + i) * 0.1
        crater_dist = moon_r * (0.3 + (i % 3) * 0.15)
        crater_x = cx + math.cos(crater_angle) * crater_dist
        crater_y = cy + math.sin(crater_angle) * crater_dist
        crater_r = 5 + (i % 3) * 2
        crater_alpha = 80 + int(math.sin(t * 2 + i) * 20)
        
        # 环形山（内外圈）
        pygame.draw.circle(moon_surf, (80, 20, 35, crater_alpha), (int(crater_x), int(crater_y)), crater_r, 1)
        pygame.draw.circle(moon_surf, (100, 30, 40, crater_alpha // 2), (int(crater_x), int(crater_y)), crater_r - 2)
    
    # 【月面裂痕】辐射状裂纹
    for i in range(6):
        crack_angle = i * (math.pi / 3) + t * 0.05
        crack_len = moon_r * 0.7
        crack_start = moon_r * 0.15
        
        # 主裂纹
        cx1 = cx + math.cos(crack_angle) * crack_start
        cy1 = cy + math.sin(crack_angle) * crack_start
        cx2 = cx + math.cos(crack_angle) * crack_len
        cy2 = cy + math.sin(crack_angle) * crack_len
        crack_alpha = int(100 + math.sin(t * 3 + i) * 30)
        pygame.draw.line(moon_surf, (200, 80, 100, crack_alpha), (int(cx1), int(cy1)), (int(cx2), int(cy2)), 1)
        
        # 分支裂纹
        mid_x = (cx1 + cx2) / 2
        mid_y = (cy1 + cy2) / 2
        branch_angle = crack_angle + 0.5 - i * 0.1
        branch_end_x = mid_x + math.cos(branch_angle) * moon_r * 0.25
        branch_end_y = mid_y + math.sin(branch_angle) * moon_r * 0.25
        pygame.draw.line(moon_surf, (180, 60, 80, crack_alpha // 2), 
                        (int(mid_x), int(mid_y)), (int(branch_end_x), int(branch_end_y)), 1)
    
    s.blit(moon_surf, (0, 0))
    
    # ========== 第二层：血色潮汐波纹 ==========
    tide_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for wave in range(4):
        wave_progress = (t * 0.5 + wave * 0.25) % 1.0
        wave_r = moon_r + 5 + wave_progress * 15
        wave_alpha = int(80 * (1 - wave_progress))
        if wave_alpha > 5:
            pygame.draw.circle(tide_surf, (180, 50, 50, wave_alpha), (int(cx), int(cy)), int(wave_r), 2)
    s.blit(tide_surf, (0, 0))
    
    # ========== 第三层：残影 ==========
    _draw_afterimage(s, cx, cy, t, theme)
    
    # ========== 第四层：浮游盾 ==========
    _draw_crystal_wings(s, cx, cy, t, theme)
    
    # ========== 第五层：枪身 ==========
    _draw_lance_body(s, cx, cy, t, theme)
    
    # ========== 第六层：蝙蝠尾迹 ==========
    _draw_bat_exhaust(s, cx, cy, t, theme)
    
    # ========== 第七层：血潮符文环 ==========
    rune_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    rune_r = 42 + math.sin(t * 1.5) * 3
    
    # 双环符文
    for ring in range(2):
        ring_r = rune_r + ring * 6
        ring_alpha = 100 - ring * 30
        pygame.draw.circle(rune_surf, (200, 60, 70, ring_alpha // 2), (int(cx), int(cy)), int(ring_r), 1)
        
        # 符文点
        rune_count = 8 + ring * 4
        for i in range(rune_count):
            rune_angle = t * (0.3 - ring * 0.1) + i * (2 * math.pi / rune_count)
            rx = cx + math.cos(rune_angle) * ring_r
            ry = cy + math.sin(rune_angle) * ring_r
            
            rune_pulse = int(180 + math.sin(t * 4 + i) * 60)
            pygame.draw.circle(rune_surf, (200, 80, 80, rune_pulse), (int(rx), int(ry)), 2)
            
            # 符文间连接
            if ring == 0:
                next_angle = t * 0.3 + (i + 1) * (2 * math.pi / rune_count)
                nx = cx + math.cos(next_angle) * ring_r
                ny = cy + math.sin(next_angle) * ring_r
                pygame.draw.line(rune_surf, (180, 50, 60, rune_pulse // 2), 
                               (int(rx), int(ry)), (int(nx), int(ny)), 1)
    s.blit(rune_surf, (0, 0))


def draw_scarlet_golden(s, cx, cy, w, h, t):
    """
    【神枪涂装】黄金魔枪·神枪冈格尼尔
    核心配色：纯金 + 亮金
    特色元素：神圣光芒、北欧符文、奥丁之力、投出必中的神枪轨迹
    
    设计理念：北欧神话的奥丁之枪
    - 12道神圣光芒从中心辐射
    - 北欧Futhark符文环绕
    - 金色神力粒子取代蝙蝠
    - 命中注定的神枪气质
    """
    theme = get_scarlet_theme("scarlet_golden")
    
    # ========== 第一层：神圣光芒背景 ==========
    holy_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    # 金色光晕背景
    for i in range(8):
        halo_r = 55 - i * 6
        halo_alpha = 40 - i * 5
        if halo_alpha > 0 and halo_r > 0:
            pygame.draw.circle(holy_surf, (255, 215, 100, halo_alpha), (int(cx), int(cy)), halo_r)
    
    # 12道神圣光芒（辐射状）
    rays = 12
    for i in range(rays):
        ray_angle = t * 0.15 + i * (2 * math.pi / rays)
        ray_pulse = 1 + math.sin(t * 2 + i * 0.5) * 0.2
        ray_len = (45 + math.sin(t * 1.5 + i) * 8) * ray_pulse
        
        # 每道光芒由5段渐变组成
        for seg in range(5):
            seg_start = 12 + seg * 8
            seg_end = min(seg_start + 10, ray_len)
            seg_alpha = int((120 - seg * 22) * ray_pulse)
            seg_width = max(1, 4 - seg)
            
            if seg_alpha < 10 or seg_start >= ray_len:
                continue
            
            rx1 = cx + math.cos(ray_angle) * seg_start
            ry1 = cy + math.sin(ray_angle) * seg_start
            rx2 = cx + math.cos(ray_angle) * seg_end
            ry2 = cy + math.sin(ray_angle) * seg_end
            
            pygame.draw.line(holy_surf, (255, 230, 120, seg_alpha), 
                           (int(rx1), int(ry1)), (int(rx2), int(ry2)), seg_width)
        
        # 光芒尖端星点
        tip_x = cx + math.cos(ray_angle) * ray_len
        tip_y = cy + math.sin(ray_angle) * ray_len
        star_alpha = int(150 + math.sin(t * 4 + i) * 50)
        pygame.draw.circle(holy_surf, (255, 255, 200, star_alpha), (int(tip_x), int(tip_y)), 2)
    
    s.blit(holy_surf, (0, 0))
    
    # ========== 第二层：残影（金色） ==========
    _draw_afterimage(s, cx, cy, t, theme)
    
    # ========== 第三层：浮游盾 ==========
    _draw_crystal_wings(s, cx, cy, t, theme)
    
    # ========== 第四层：金枪身 ==========
    _draw_lance_body(s, cx, cy, t, theme)
    
    # ========== 第五层：神力粒子尾迹（取代蝙蝠） ==========
    particle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    # 尾部神圣火焰
    flame_y = cy + 42
    for i in range(4):
        flame_r = 8 - i * 2
        flame_alpha = 120 - i * 25
        if flame_r > 0 and flame_alpha > 0:
            pygame.draw.circle(particle_surf, (255, 200, 80, flame_alpha), (int(cx), int(flame_y)), flame_r)
    
    # 金色四角星粒子
    for i in range(15):
        age = (t * 2.2 + i * 0.18) % 2.0
        p_y = flame_y + age * 25
        p_x = cx + math.sin(t * 3 + i * 0.7) * (4 + age * 10)
        p_size = max(2, int((1 - age / 2.0) * 6))
        p_alpha = int((1 - age / 2.0) * 220)
        
        if p_alpha < 20:
            continue
        
        # 四角星形
        star_pts = [
            (p_x, p_y - p_size * 1.8),
            (p_x + p_size * 0.4, p_y - p_size * 0.4),
            (p_x + p_size * 1.8, p_y),
            (p_x + p_size * 0.4, p_y + p_size * 0.4),
            (p_x, p_y + p_size * 1.8),
            (p_x - p_size * 0.4, p_y + p_size * 0.4),
            (p_x - p_size * 1.8, p_y),
            (p_x - p_size * 0.4, p_y - p_size * 0.4),
        ]
        star_pts = [(int(px), int(py)) for px, py in star_pts]
        pygame.draw.polygon(particle_surf, (255, 240, 120, p_alpha), star_pts)
    
    s.blit(particle_surf, (0, 0))
    
    # ========== 第六层：北欧符文双环 ==========
    rune_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    # 外环
    outer_r = 48 + math.sin(t * 1.2) * 2
    pygame.draw.circle(rune_surf, (255, 240, 180, 80), (int(cx), int(cy)), int(outer_r), 2)
    
    # 内环
    inner_r = 38 + math.sin(t * 1.5) * 2
    pygame.draw.circle(rune_surf, (255, 250, 200, 60), (int(cx), int(cy)), int(inner_r), 1)
    
    # 北欧Futhark符文（更详细）
    futhark_runes = [
        # (角度, 符文形状点列表) - 简化版24符文中的6个
        (0, [(0, -5), (0, 5), (-3, 0), (0, -2)]),           # ᚠ Fehu (财富)
        (60, [(0, -5), (0, 5), (3, -2), (0, 0)]),           # ᚱ Raido (旅途)
        (120, [(-2, -5), (0, -5), (0, 5), (3, 0)]),         # ᚦ Thurisaz (雷神)
        (180, [(0, -5), (0, 5), (-3, -2), (-3, 2)]),        # ᚲ Kenaz (火炬)
        (240, [(-2, 5), (0, -5), (2, 5)]),                  # ᚷ Gebo (礼物)
        (300, [(0, -5), (0, 5), (-2, -3), (2, -3)]),        # ᛁ Isa (冰)
    ]
    
    for angle_deg, rune_shape in futhark_runes:
        rune_angle = math.radians(angle_deg) + t * 0.15
        rune_x = cx + math.cos(rune_angle) * outer_r
        rune_y = cy + math.sin(rune_angle) * outer_r
        rune_alpha = int(200 + math.sin(t * 3 + angle_deg) * 40)
        
        # 符文背景光晕
        pygame.draw.circle(rune_surf, (255, 230, 150, rune_alpha // 3), (int(rune_x), int(rune_y)), 6)
        
        # 绘制符文线条
        for j in range(len(rune_shape) - 1):
            x1, y1 = rune_shape[j]
            x2, y2 = rune_shape[j + 1]
            pygame.draw.line(rune_surf, (255, 250, 200, rune_alpha),
                           (int(rune_x + x1), int(rune_y + y1)), 
                           (int(rune_x + x2), int(rune_y + y2)), 2)
    
    s.blit(rune_surf, (0, 0))
    
    # ========== 第七层：神枪轨迹预言线 ==========
    # 表示"投出必中"的命中轨迹
    trajectory_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    traj_alpha = int(60 + math.sin(t * 2) * 30)
    
    # 向前延伸的瞄准线
    pygame.draw.line(trajectory_surf, (255, 240, 180, traj_alpha), 
                    (int(cx), int(cy - 50)), (int(cx), int(cy - 60)), 2)
    pygame.draw.line(trajectory_surf, (255, 240, 180, traj_alpha // 2), 
                    (int(cx), int(cy - 60)), (int(cx), int(cy - 70)), 1)
    
    # 命中十字准星
    cross_y = cy - 55
    cross_size = 6 + math.sin(t * 4) * 2
    pygame.draw.line(trajectory_surf, (255, 255, 200, traj_alpha), 
                    (int(cx - cross_size), int(cross_y)), (int(cx + cross_size), int(cross_y)), 1)
    pygame.draw.line(trajectory_surf, (255, 255, 200, traj_alpha), 
                    (int(cx), int(cross_y - cross_size)), (int(cx), int(cross_y + cross_size)), 1)
    
    s.blit(trajectory_surf, (0, 0))


def draw_scarlet_mist(s, cx, cy, w, h, t):
    """
    【红雾涂装】红雾迷城·深红世界
    核心配色：雾红 + 苍白金
    特色元素：时间静止迷雾、钟表元素、世界被深红笼罩、时空碎片
    
    设计理念：十六夜咲夜的时停能力
    - 深红迷雾弥漫整个世界
    - 巨大的静止钟表
    - 时空碎片悬浮
    - 一切都在时间冻结之中
    """
    theme = get_scarlet_theme("scarlet_mist")
    
    # ========== 第一层：深红迷雾笼罩 ==========
    mist_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    # 多层迷雾（3层，由远及近）
    for layer in range(3):
        layer_speed = 0.3 + layer * 0.15
        layer_alpha_base = 30 - layer * 8
        
        for i in range(18):
            mist_angle = t * layer_speed + i * 0.35 + layer * 0.5
            mist_base_r = 20 + layer * 15
            mist_r = mist_base_r + i * 2 + math.sin(t * 0.8 + i) * 10
            mist_x = cx + math.cos(mist_angle) * mist_r
            mist_y = cy + math.sin(mist_angle * 0.75) * mist_r * 0.7
            mist_size = 12 + layer * 4 + math.sin(t * 1.5 + i) * 5
            mist_alpha = layer_alpha_base + int(math.sin(t * 2 + i * 0.3) * 10)
            
            if mist_alpha > 5:
                pygame.draw.circle(mist_surf, (160, 30, 60, mist_alpha), 
                                 (int(mist_x), int(mist_y)), int(mist_size))
    
    # 迷雾边缘涡流
    for i in range(8):
        vortex_angle = t * 0.5 + i * (math.pi / 4)
        vortex_r = 50 + math.sin(t + i) * 5
        vx = cx + math.cos(vortex_angle) * vortex_r
        vy = cy + math.sin(vortex_angle) * vortex_r
        vortex_alpha = int(40 + math.sin(t * 3 + i) * 20)
        
        # 小漩涡
        for j in range(3):
            spiral_angle = vortex_angle + t * 2 + j * (2 * math.pi / 3)
            spiral_r = 5 + j * 2
            sx = vx + math.cos(spiral_angle) * spiral_r
            sy = vy + math.sin(spiral_angle) * spiral_r
            pygame.draw.circle(mist_surf, (180, 50, 80, vortex_alpha - j * 10), (int(sx), int(sy)), 2)
    
    s.blit(mist_surf, (0, 0))
    
    # ========== 第二层：时空碎片悬浮 ==========
    shard_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    for i in range(10):
        shard_angle = t * 0.2 + i * 0.63
        shard_r = 30 + (i % 3) * 12 + math.sin(t * 1.5 + i) * 5
        shard_x = cx + math.cos(shard_angle) * shard_r
        shard_y = cy + math.sin(shard_angle) * shard_r
        
        # 碎片浮动
        float_y = math.sin(t * 2 + i * 0.7) * 3
        shard_y += float_y
        
        # 三角形碎片
        shard_size = 4 + (i % 3) * 2
        shard_rotation = t * 1.5 + i * 0.8
        shard_alpha = int(120 + math.sin(t * 3 + i) * 40)
        
        shard_pts = []
        for j in range(3):
            pt_angle = shard_rotation + j * (2 * math.pi / 3)
            px = shard_x + math.cos(pt_angle) * shard_size
            py = shard_y + math.sin(pt_angle) * shard_size
            shard_pts.append((int(px), int(py)))
        
        pygame.draw.polygon(shard_surf, (200, 150, 160, shard_alpha), shard_pts)
        pygame.draw.polygon(shard_surf, (240, 200, 210, shard_alpha // 2), shard_pts, 1)
    
    s.blit(shard_surf, (0, 0))
    
    # ========== 第三层：残影 ==========
    _draw_afterimage(s, cx, cy, t, theme)
    
    # ========== 第四层：浮游盾 ==========
    _draw_crystal_wings(s, cx, cy, t, theme)
    
    # ========== 第五层：枪身 ==========
    _draw_lance_body(s, cx, cy, t, theme)
    
    # ========== 第六层：蝙蝠 ==========
    _draw_bat_exhaust(s, cx, cy, t, theme)
    
    # ========== 第七层：巨大静止钟表 ==========
    clock_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    clock_r = 46
    clock_alpha = int(100 + math.sin(t * 2) * 25)
    clock_glow = int(60 + math.sin(t * 3) * 20)
    
    # 钟表光晕
    for i in range(4):
        glow_r = clock_r + 4 + i * 3
        glow_a = clock_glow - i * 15
        if glow_a > 0:
            pygame.draw.circle(clock_surf, (220, 180, 160, glow_a), (int(cx), int(cy)), glow_r, 1)
    
    # 钟表外圈（双环）
    pygame.draw.circle(clock_surf, (220, 180, 160, clock_alpha), (int(cx), int(cy)), clock_r, 3)
    pygame.draw.circle(clock_surf, (200, 160, 140, clock_alpha // 2), (int(cx), int(cy)), clock_r - 4, 1)
    
    # 12个刻度（主刻度更粗）
    for i in range(12):
        tick_angle = i * (math.pi / 6) - math.pi / 2
        tick_inner = clock_r - 8
        tick_outer = clock_r - 3
        tx1 = cx + math.cos(tick_angle) * tick_inner
        ty1 = cy + math.sin(tick_angle) * tick_inner
        tx2 = cx + math.cos(tick_angle) * tick_outer
        ty2 = cy + math.sin(tick_angle) * tick_outer
        
        width = 3 if i % 3 == 0 else 1
        pygame.draw.line(clock_surf, (220, 180, 160, clock_alpha), 
                        (int(tx1), int(ty1)), (int(tx2), int(ty2)), width)
    
    # 分刻度（60个小点）
    for i in range(60):
        if i % 5 == 0:  # 跳过整点
            continue
        tick_angle = i * (math.pi / 30) - math.pi / 2
        tick_r = clock_r - 5
        tx = cx + math.cos(tick_angle) * tick_r
        ty = cy + math.sin(tick_angle) * tick_r
        pygame.draw.circle(clock_surf, (200, 160, 140, clock_alpha // 2), (int(tx), int(ty)), 1)
    
    # 时针（极慢转动，几乎静止）
    hour_angle = t * 0.03 - math.pi / 2
    hour_len = clock_r * 0.38
    pygame.draw.line(clock_surf, (180, 140, 120, clock_alpha),
                    (int(cx), int(cy)),
                    (int(cx + math.cos(hour_angle) * hour_len), 
                     int(cy + math.sin(hour_angle) * hour_len)), 4)
    
    # 分针（缓慢）
    min_angle = t * 0.12 - math.pi / 2
    min_len = clock_r * 0.58
    pygame.draw.line(clock_surf, (210, 170, 150, clock_alpha),
                    (int(cx), int(cy)),
                    (int(cx + math.cos(min_angle) * min_len), 
                     int(cy + math.sin(min_angle) * min_len)), 3)
    
    # 秒针（完全静止 - 时停！）
    sec_angle = math.pi * 0.3 - math.pi / 2  # 固定在某个角度
    sec_len = clock_r * 0.72
    # 秒针闪烁效果表示时间冻结
    sec_alpha = clock_alpha if int(t * 6) % 3 != 0 else clock_alpha // 2
    pygame.draw.line(clock_surf, (255, 100, 100, sec_alpha),
                    (int(cx), int(cy)),
                    (int(cx + math.cos(sec_angle) * sec_len), 
                     int(cy + math.sin(sec_angle) * sec_len)), 2)
    
    # 中心装饰（齿轮状）
    pygame.draw.circle(clock_surf, (220, 180, 160, clock_alpha), (int(cx), int(cy)), 5)
    pygame.draw.circle(clock_surf, (180, 140, 120, clock_alpha), (int(cx), int(cy)), 3)
    
    # 齿轮齿
    for i in range(8):
        gear_angle = t * 0.5 + i * (math.pi / 4)
        gx = cx + math.cos(gear_angle) * 7
        gy = cy + math.sin(gear_angle) * 7
        pygame.draw.rect(clock_surf, (200, 160, 140, clock_alpha),
                        (int(gx - 2), int(gy - 2), 4, 4))
    
    s.blit(clock_surf, (0, 0))
    
    # ========== 第八层：时停闪烁 ==========
    if int(t * 5) % 7 == 0:
        flash_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(flash_surf, (255, 220, 220, 25), (int(cx), int(cy)), 55)
        s.blit(flash_surf, (0, 0))


def draw_scarlet_gothic(s, cx, cy, w, h, t):
    """
    【哥特涂装】哥特女仆·暗夜侍从
    核心配色：暗黑 + 银白
    特色元素：银月飞刀、暗夜星辰、完美优雅的女仆风格、时停领域
    
    设计理念：完美女仆十六夜咲夜
    - 暗紫色星空背景
    - 银白色飞刀环绕
    - 银月光环
    - 暗夜的优雅与致命
    """
    theme = get_scarlet_theme("scarlet_gothic")
    
    # ========== 第一层：暗夜星空背景 ==========
    night_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    # 暗紫渐变背景（多层）
    for i in range(8):
        bg_r = 58 - i * 7
        bg_alpha = 50 - i * 6
        if bg_alpha > 0 and bg_r > 0:
            pygame.draw.circle(night_surf, (25, 15, 45, bg_alpha), (int(cx), int(cy)), bg_r)
    
    # 星辰（固定位置，闪烁）
    random.seed(42)
    for i in range(30):
        star_x = random.randint(8, 112)
        star_y = random.randint(8, 112)
        star_phase = random.random() * 6.28
        star_twinkle = 0.4 + 0.6 * math.sin(t * (3 + random.random() * 2) + star_phase)
        star_size = 1 + int(star_twinkle * (1 + random.random()))
        star_alpha = int(80 + star_twinkle * 120)
        
        # 星星颜色（白/淡蓝/淡紫）
        star_colors = [(220, 220, 255), (200, 200, 240), (230, 210, 240)]
        star_color = star_colors[i % 3]
        pygame.draw.circle(night_surf, (*star_color, star_alpha), (star_x, star_y), star_size)
        
        # 较亮的星有十字光芒
        if star_size >= 2:
            cross_len = star_size + 2
            cross_alpha = star_alpha // 3
            pygame.draw.line(night_surf, (*star_color, cross_alpha),
                           (star_x - cross_len, star_y), (star_x + cross_len, star_y), 1)
            pygame.draw.line(night_surf, (*star_color, cross_alpha),
                           (star_x, star_y - cross_len), (star_x, star_y + cross_len), 1)
    
    s.blit(night_surf, (0, 0))
    
    # ========== 第二层：银月光环 ==========
    moon_halo_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    moon_r = 48 + math.sin(t * 1.2) * 3
    
    # 月光渐变光晕
    for i in range(6):
        halo_r = moon_r + i * 4
        halo_alpha = 45 - i * 7
        if halo_alpha > 0:
            pygame.draw.circle(moon_halo_surf, (180, 170, 220, halo_alpha), (int(cx), int(cy)), int(halo_r), 1)
    
    # 银月环
    pygame.draw.circle(moon_halo_surf, (200, 190, 230, 70), (int(cx), int(cy)), int(moon_r), 2)
    
    s.blit(moon_halo_surf, (0, 0))
    
    # ========== 第三层：残影 ==========
    _draw_afterimage(s, cx, cy, t, theme)
    
    # ========== 第四层：浮游盾 ==========
    _draw_crystal_wings(s, cx, cy, t, theme)
    
    # ========== 第五层：暗色枪身 ==========
    _draw_lance_body(s, cx, cy, t, theme)
    
    # ========== 第六层：暗紫蝙蝠 ==========
    _draw_bat_exhaust(s, cx, cy, t, theme)
    
    # ========== 第七层：银色飞刀环绕（详细版） ==========
    knife_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    knife_color = theme.get("knife_color", (220, 220, 245))
    
    # 12把飞刀，双层环绕
    for ring in range(2):
        knife_count = 6 + ring * 2
        knife_r = 35 + ring * 10 + math.sin(t * 1.5 + ring) * 3
        
        for i in range(knife_count):
            knife_angle = t * (1.0 - ring * 0.3) + i * (2 * math.pi / knife_count)
            knife_x = cx + math.cos(knife_angle) * knife_r
            knife_y = cy + math.sin(knife_angle) * knife_r
            
            # 飞刀浮动
            float_offset = math.sin(t * 2.5 + i * 0.6 + ring) * 2.5
            knife_y += float_offset
            
            # 飞刀指向圆心
            point_angle = knife_angle + math.pi
            knife_len = 11 - ring * 2
            knife_width = 3.5 - ring * 0.5
            
            # 刀身（细长三角形 + 血槽）
            tip_x = knife_x + math.cos(point_angle) * knife_len
            tip_y = knife_y + math.sin(point_angle) * knife_len
            
            perp_angle = point_angle + math.pi / 2
            base1_x = knife_x + math.cos(perp_angle) * knife_width
            base1_y = knife_y + math.sin(perp_angle) * knife_width
            base2_x = knife_x - math.cos(perp_angle) * knife_width
            base2_y = knife_y - math.sin(perp_angle) * knife_width
            
            knife_pts = [
                (int(tip_x), int(tip_y)),
                (int(base1_x), int(base1_y)),
                (int(base2_x), int(base2_y)),
            ]
            knife_alpha = 200 - ring * 40
            pygame.draw.polygon(knife_surf, (*knife_color, knife_alpha), knife_pts)
            
            # 刀身高光（中线）
            mid_x = (knife_x + tip_x) / 2
            mid_y = (knife_y + tip_y) / 2
            pygame.draw.line(knife_surf, (255, 255, 255, knife_alpha - 50),
                            (int(knife_x), int(knife_y)), (int(mid_x), int(mid_y)), 1)
            
            # 刀刃边缘光泽
            pygame.draw.line(knife_surf, (240, 240, 255, knife_alpha - 30),
                            (int(tip_x), int(tip_y)), (int(base1_x), int(base1_y)), 1)
            
            # 刀柄（银色圆环）
            handle_x = knife_x - math.cos(point_angle) * 5
            handle_y = knife_y - math.sin(point_angle) * 5
            pygame.draw.circle(knife_surf, (160, 140, 180, knife_alpha), (int(handle_x), int(handle_y)), 3)
            pygame.draw.circle(knife_surf, (200, 180, 210, knife_alpha // 2), (int(handle_x), int(handle_y)), 2)
    
    s.blit(knife_surf, (0, 0))
    
    # ========== 第八层：飞刀轨迹残影 ==========
    trail_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for i in range(6):
        trail_angle = t * 0.8 + i * (math.pi / 3) + 0.3
        trail_r = 35
        for j in range(4):
            offset = j * 0.15
            trail_x = cx + math.cos(trail_angle - offset) * trail_r
            trail_y = cy + math.sin(trail_angle - offset) * trail_r
            trail_alpha = 50 - j * 12
            if trail_alpha > 0:
                pygame.draw.circle(trail_surf, (*knife_color[:3], trail_alpha), (int(trail_x), int(trail_y)), 2)
    s.blit(trail_surf, (0, 0))
    
    # ========== 第九层：女仆蝴蝶结装饰 ==========
    bow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    bow_y = cy - 35
    bow_pulse = 1 + math.sin(t * 3) * 0.1
    bow_alpha = 180
    
    # 蝴蝶结左翼
    left_bow = [
        (cx - 3, bow_y),
        (cx - 12 * bow_pulse, bow_y - 6),
        (cx - 8 * bow_pulse, bow_y),
        (cx - 12 * bow_pulse, bow_y + 6),
    ]
    left_bow = [(int(p[0]), int(p[1])) for p in left_bow]
    pygame.draw.polygon(bow_surf, (180, 100, 140, bow_alpha), left_bow)
    
    # 蝴蝶结右翼
    right_bow = [
        (cx + 3, bow_y),
        (cx + 12 * bow_pulse, bow_y - 6),
        (cx + 8 * bow_pulse, bow_y),
        (cx + 12 * bow_pulse, bow_y + 6),
    ]
    right_bow = [(int(p[0]), int(p[1])) for p in right_bow]
    pygame.draw.polygon(bow_surf, (180, 100, 140, bow_alpha), right_bow)
    
    # 蝴蝶结中心
    pygame.draw.circle(bow_surf, (200, 120, 160, bow_alpha), (int(cx), int(bow_y)), 4)
    pygame.draw.circle(bow_surf, (220, 150, 180, bow_alpha // 2), (int(cx), int(bow_y)), 2)
    
    s.blit(bow_surf, (0, 0))


def draw_scarlet_destiny(s, cx, cy, w, h, t):
    """
    【命运涂装】命运之枪·红色命运
    核心配色：命运红 + 命运金
    特色元素：命运丝线缠绕、宿命符文、红色命运之眼、命运齿轮
    
    设计理念：命运的不可逆转与宿命的重压
    - 命运丝线织成无法逃脱的网
    - 巨大的命运齿轮在背后转动
    - 宿命符文揭示不可更改的结局
    - 红色命运之眼洞察一切
    """
    theme = get_scarlet_theme("scarlet_destiny")
    
    # ========== 第一层：命运齿轮背景 ==========
    gear_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    # 巨大的主齿轮
    main_gear_r = 52
    gear_rotation = t * 0.15
    gear_alpha = int(50 + math.sin(t * 1.5) * 15)
    
    # 齿轮外圈
    pygame.draw.circle(gear_surf, (180, 60, 80, gear_alpha), (int(cx), int(cy)), main_gear_r, 2)
    pygame.draw.circle(gear_surf, (160, 50, 70, gear_alpha // 2), (int(cx), int(cy)), main_gear_r - 5, 1)
    
    # 齿轮齿（24齿）
    for i in range(24):
        tooth_angle = gear_rotation + i * (math.pi / 12)
        tooth_inner = main_gear_r - 3
        tooth_outer = main_gear_r + 5
        
        # 齿根
        t1_x = cx + math.cos(tooth_angle - 0.08) * tooth_inner
        t1_y = cy + math.sin(tooth_angle - 0.08) * tooth_inner
        # 齿尖左
        t2_x = cx + math.cos(tooth_angle - 0.05) * tooth_outer
        t2_y = cy + math.sin(tooth_angle - 0.05) * tooth_outer
        # 齿尖右
        t3_x = cx + math.cos(tooth_angle + 0.05) * tooth_outer
        t3_y = cy + math.sin(tooth_angle + 0.05) * tooth_outer
        # 齿根右
        t4_x = cx + math.cos(tooth_angle + 0.08) * tooth_inner
        t4_y = cy + math.sin(tooth_angle + 0.08) * tooth_inner
        
        tooth_pts = [(int(t1_x), int(t1_y)), (int(t2_x), int(t2_y)), 
                    (int(t3_x), int(t3_y)), (int(t4_x), int(t4_y))]
        pygame.draw.polygon(gear_surf, (180, 60, 80, gear_alpha), tooth_pts)
    
    # 内部辐条（6条）
    for i in range(6):
        spoke_angle = gear_rotation + i * (math.pi / 3)
        spoke_inner = 12
        spoke_outer = main_gear_r - 8
        
        sx1 = cx + math.cos(spoke_angle) * spoke_inner
        sy1 = cy + math.sin(spoke_angle) * spoke_inner
        sx2 = cx + math.cos(spoke_angle) * spoke_outer
        sy2 = cy + math.sin(spoke_angle) * spoke_outer
        
        pygame.draw.line(gear_surf, (200, 80, 100, gear_alpha), 
                        (int(sx1), int(sy1)), (int(sx2), int(sy2)), 2)
    
    # 中心轴承
    pygame.draw.circle(gear_surf, (180, 60, 80, gear_alpha), (int(cx), int(cy)), 10, 2)
    pygame.draw.circle(gear_surf, (160, 50, 70, gear_alpha // 2), (int(cx), int(cy)), 6)
    
    s.blit(gear_surf, (0, 0))
    
    # ========== 第二层：命运丝线网络（更复杂） ==========
    thread_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    thread_color = theme.get("thread_color", (255, 60, 100))
    
    # 生成丝线节点（16个点）
    thread_points = []
    for i in range(16):
        angle = t * 0.25 + i * (math.pi / 8)
        r = 32 + math.sin(t * 1.2 + i * 0.4) * 8 + (i % 3) * 4
        px = cx + math.cos(angle) * r
        py = cy + math.sin(angle) * r
        thread_points.append((px, py))
    
    # 命运丝线连接（复杂网络）
    for i, (px, py) in enumerate(thread_points):
        # 相邻连接
        for step in [1, 2, 4, 7]:
            next_idx = (i + step) % len(thread_points)
            nx, ny = thread_points[next_idx]
            
            thread_alpha = int((100 - step * 15) + math.sin(t * 3 + i * 0.5) * 30)
            if thread_alpha > 20:
                # 丝线抖动效果
                mid_x = (px + nx) / 2 + math.sin(t * 4 + i) * 2
                mid_y = (py + ny) / 2 + math.cos(t * 3 + i) * 2
                
                pygame.draw.line(thread_surf, (*thread_color[:3], thread_alpha),
                               (int(px), int(py)), (int(mid_x), int(mid_y)), 1)
                pygame.draw.line(thread_surf, (*thread_color[:3], thread_alpha),
                               (int(mid_x), int(mid_y)), (int(nx), int(ny)), 1)
        
        # 连接到中心的核心丝线
        if i % 2 == 0:
            core_alpha = int(80 + math.sin(t * 2.5 + i) * 25)
            pygame.draw.line(thread_surf, (*thread_color[:3], core_alpha),
                            (int(px), int(py)), (int(cx), int(cy)), 1)
        
        # 丝线节点（脉动）
        node_pulse = 1 + math.sin(t * 4 + i * 0.7) * 0.3
        node_alpha = int(150 + math.sin(t * 5 + i) * 50)
        node_r = int(3 * node_pulse)
        pygame.draw.circle(thread_surf, (*thread_color[:3], node_alpha), (int(px), int(py)), node_r)
    
    s.blit(thread_surf, (0, 0))
    
    # ========== 第三层：压迫感光环 ==========
    _draw_pressure_aura(s, cx, cy, t, theme, 1.2)
    
    # ========== 第四层：残影 ==========
    _draw_afterimage(s, cx, cy, t, theme)
    
    # ========== 第五层：命运之盾 ==========
    _draw_crystal_wings(s, cx, cy, t, theme)
    
    # ========== 第六层：命运之枪 ==========
    _draw_lance_body(s, cx, cy, t, theme)
    
    # ========== 第七层：命运粒子 ==========
    _draw_bat_exhaust(s, cx, cy, t, theme)
    
    # ========== 第八层：三重宿命符文环 ==========
    rune_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    for ring in range(3):
        rune_r = 38 + ring * 8 + math.sin(t * (1.8 - ring * 0.3)) * 2
        ring_alpha = 140 - ring * 35
        ring_speed = 0.2 - ring * 0.06
        
        # 符文环
        pygame.draw.circle(rune_surf, (255, 100, 120, ring_alpha // 3), (int(cx), int(cy)), int(rune_r), 2)
        
        # 符文数量
        rune_count = 6 + ring * 2
        for i in range(rune_count):
            rune_angle = t * ring_speed * (1 if ring % 2 == 0 else -1) + i * (2 * math.pi / rune_count)
            rx = cx + math.cos(rune_angle) * rune_r
            ry = cy + math.sin(rune_angle) * rune_r
            
            # 符文光晕
            rune_glow = int(100 + math.sin(t * 4 + i + ring) * 40)
            pygame.draw.circle(rune_surf, (255, 200, 150, rune_glow // 3), (int(rx), int(ry)), 5)
            
            # 符文核心
            rune_alpha = int(200 + math.sin(t * 5 + i) * 40)
            pygame.draw.circle(rune_surf, (255, 230, 200, rune_alpha), (int(rx), int(ry)), 3)
            
            # 符文光芒（十字）
            ray_len = 6 + ring
            ray_alpha = rune_alpha // 2
            for j in range(4):
                ray_angle = rune_angle + j * (math.pi / 2)
                ray_x = rx + math.cos(ray_angle) * ray_len
                ray_y = ry + math.sin(ray_angle) * ray_len
                pygame.draw.line(rune_surf, (255, 220, 180, ray_alpha),
                               (int(rx), int(ry)), (int(ray_x), int(ray_y)), 1)
    
    s.blit(rune_surf, (0, 0))
    
    # ========== 第九层：命运之眼（详细版） ==========
    eye_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    eye_y = cy - 25
    eye_pulse = 1 + math.sin(t * 2.5) * 0.2
    
    # 眼睛外光晕
    for i in range(5):
        eye_glow_r = int(14 * eye_pulse) + i * 3
        eye_glow_alpha = 60 - i * 12
        if eye_glow_alpha > 0:
            pygame.draw.circle(eye_surf, (255, 100, 100, eye_glow_alpha), (int(cx), int(eye_y)), eye_glow_r)
    
    # 眼白
    eye_w = int(12 * eye_pulse)
    eye_h = int(8 * eye_pulse)
    eye_rect = (int(cx - eye_w), int(eye_y - eye_h), eye_w * 2, eye_h * 2)
    pygame.draw.ellipse(eye_surf, (255, 240, 240, 200), eye_rect)
    
    # 虹膜
    iris_r = int(5 * eye_pulse)
    pygame.draw.circle(eye_surf, (200, 50, 80, 220), (int(cx), int(eye_y)), iris_r)
    pygame.draw.circle(eye_surf, (220, 80, 100, 200), (int(cx), int(eye_y)), iris_r - 1)
    
    # 竖瞳
    pupil_contract = 0.6 + math.sin(t * 3) * 0.15
    pupil_h = int(iris_r * 1.5 * pupil_contract)
    pupil_w = max(1, int(iris_r * 0.35))
    pygame.draw.ellipse(eye_surf, (20, 0, 10, 250),
                       (int(cx - pupil_w), int(eye_y - pupil_h), pupil_w * 2, pupil_h * 2))
    
    # 眼睛高光
    pygame.draw.circle(eye_surf, (255, 255, 255, 200), (int(cx - 2), int(eye_y - 2)), 2)
    
    s.blit(eye_surf, (0, 0))


# =============================================================================
#   渲染调度器
# =============================================================================

# 涂装绘制函数映射
SCARLET_DRAW_FUNCTIONS = {
    "scarlet_default": draw_scarlet_default,
    "scarlet_lunar": draw_scarlet_lunar,
    "scarlet_golden": draw_scarlet_golden,
    "scarlet_mist": draw_scarlet_mist,
    "scarlet_gothic": draw_scarlet_gothic,
    "scarlet_destiny": draw_scarlet_destiny,
}


def render_scarlet_skin(s, color, model_style, t, pid=None, static=False):
    """
    渲染SCARLET涂装
    
    Args:
        s: pygame Surface
        color: 基础颜色（可能被涂装覆盖）
        model_style: 涂装样式
        t: 时间（动画用）
        pid: 机体ID
        static: 是否静态渲染
    
    Returns:
        渲染后的Surface，如果不匹配返回None
    """
    if model_style not in SCARLET_STYLES:
        return None
    
    # 创建新Surface
    result = pygame.Surface((120, 120), pygame.SRCALPHA)
    
    # 获取绘制函数
    draw_func = SCARLET_DRAW_FUNCTIONS.get(model_style, draw_scarlet_default)
    
    # 执行绘制
    draw_func(result, 60, 60, 120, 120, t if not static else 0)
    
    return result


def _render_scarlet_base(s, t, pulse):
    """
    渲染SCARLET基础机体（无涂装）
    用于机体选择界面等
    """
    theme = get_scarlet_theme("scarlet_default")
    cx, cy = 60, 60
    
    # 基础渲染
    _draw_afterimage(s, cx, cy, t, theme)
    _draw_crystal_wings(s, cx, cy, t, theme)
    _draw_lance_body(s, cx, cy, t, theme)
    _draw_bat_exhaust(s, cx, cy, t, theme)


# 导出
__all__ = [
    'SCARLET_THEMES',
    'SCARLET_STYLES',
    'is_scarlet_style',
    'get_scarlet_theme',
    'render_scarlet_skin',
    '_render_scarlet_base',
    'draw_scarlet_default',
    'draw_scarlet_lunar',
    'draw_scarlet_golden',
    'draw_scarlet_mist',
    'draw_scarlet_gothic',
    'draw_scarlet_destiny',
]
