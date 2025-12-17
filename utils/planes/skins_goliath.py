# -*- coding: utf-8 -*-
"""
瘟疫使者·歌莉娅 (Goliath) 涂装系统
原型：Terraria Calamity Mod - The Plaguebringer Goliath
风格：柴油朋克 + 生化恐怖 + 军事废土 - 巨型蜂后仿生轰炸机
"""
import pygame
import math
import random

# ==================== 12种涂装主题 ====================
GOLIATH_THEMES = {
    # 默认涂装 - 瘟疫使者原型
    "goliath_default": {
        "name": "瘟疫使者",
        "armor": (85, 107, 47),      # 橄榄绿 Olive Drab #556B2F
        "toxic": (57, 255, 20),      # 酸性绿 Acid Green #39FF14
        "rust": (139, 69, 19),       # 锈褐 Rust Brown #8B4513
        "eye": (255, 0, 0),          # 红色单眼
        "smoke": (50, 60, 40),       # 黑绿烟雾
        "glow": (100, 255, 100),     # 荧光绿发光
    },
    
    # 【军事变体系列】
    "goliath_nuclear": {
        "name": "核冬幽魂",
        "armor": (60, 60, 60),       # 铅灰
        "toxic": (255, 255, 0),      # 辐射黄
        "rust": (80, 80, 60),        # 灰锈
        "eye": (255, 200, 0),        # 警告黄眼
        "smoke": (100, 100, 50),     # 硫磺烟
        "glow": (255, 255, 100),     # 辐射光
    },
    
    "goliath_desert": {
        "name": "沙漠风暴",
        "armor": (194, 178, 128),    # 沙漠迷彩
        "toxic": (200, 150, 50),     # 沙尘黄
        "rust": (160, 120, 80),      # 沙锈
        "eye": (255, 100, 50),       # 橙红眼
        "smoke": (180, 160, 120),    # 沙尘烟
        "glow": (255, 200, 100),     # 沙漠光
    },
    
    "goliath_arctic": {
        "name": "极地猎手",
        "armor": (200, 210, 220),    # 雪地白
        "toxic": (100, 200, 255),    # 冰蓝毒
        "rust": (150, 160, 170),     # 冻锈
        "eye": (0, 200, 255),        # 冰蓝眼
        "smoke": (180, 200, 220),    # 寒霜烟
        "glow": (150, 220, 255),     # 冰光
    },
    
    # 【生化变异系列】
    "goliath_necrosis": {
        "name": "坏疽腐蚀",
        "armor": (60, 50, 40),       # 腐肉黑
        "toxic": (180, 255, 100),    # 腐烂绿
        "rust": (100, 60, 40),       # 血锈
        "eye": (255, 150, 0),        # 脓黄眼
        "smoke": (80, 100, 60),      # 腐气
        "glow": (200, 255, 150),     # 腐光
    },
    
    "goliath_pandemic": {
        "name": "末日瘟神",
        "armor": (40, 30, 50),       # 暗紫黑
        "toxic": (200, 50, 255),     # 病毒紫
        "rust": (80, 50, 60),        # 紫锈
        "eye": (255, 0, 100),        # 病变红眼
        "smoke": (100, 50, 120),     # 毒雾紫
        "glow": (220, 100, 255),     # 病毒光
    },
    
    "goliath_spore": {
        "name": "孢子母巢",
        "armor": (80, 100, 60),      # 菌绿
        "toxic": (255, 200, 50),     # 孢子黄
        "rust": (100, 80, 50),       # 菌锈
        "eye": (255, 220, 100),      # 孢子眼
        "smoke": (120, 150, 80),     # 孢子云
        "glow": (255, 230, 100),     # 孢子光
    },
    
    # 【工业废土系列】
    "goliath_chemical": {
        "name": "化工泄漏",
        "armor": (100, 100, 110),    # 工业灰
        "toxic": (0, 255, 200),      # 化学青
        "rust": (120, 80, 60),       # 化锈
        "eye": (0, 255, 150),        # 化学眼
        "smoke": (80, 120, 100),     # 化学烟
        "glow": (100, 255, 200),     # 化学光
    },
    
    "goliath_refinery": {
        "name": "炼油厂魔",
        "armor": (50, 40, 30),       # 油污黑
        "toxic": (255, 100, 0),      # 燃油橙
        "rust": (80, 50, 30),        # 油锈
        "eye": (255, 150, 50),       # 火焰眼
        "smoke": (30, 30, 30),       # 黑烟
        "glow": (255, 180, 50),      # 火光
    },
    
    # 【异形变种系列】
    "goliath_hive": {
        "name": "异虫女皇",
        "armor": (120, 80, 40),      # 甲壳棕
        "toxic": (255, 200, 0),      # 蜂蜜黄
        "rust": (80, 60, 30),        # 壳锈
        "eye": (255, 50, 50),        # 复眼红
        "smoke": (150, 120, 60),     # 花粉烟
        "glow": (255, 220, 100),     # 蜂光
    },
    
    "goliath_xenomorph": {
        "name": "异形寄生",
        "armor": (20, 20, 30),       # 异形黑
        "toxic": (100, 255, 100),    # 酸血绿
        "rust": (40, 40, 50),        # 暗锈
        "eye": (200, 200, 255),      # 银白眼
        "smoke": (50, 80, 50),       # 酸烟
        "glow": (150, 255, 150),     # 酸光
    },
    
    "goliath_crimson": {
        "name": "血疫狂潮",
        "armor": (100, 30, 30),      # 血红
        "toxic": (255, 50, 100),     # 血毒红
        "rust": (80, 20, 20),        # 血锈
        "eye": (255, 255, 0),        # 狂热黄眼
        "smoke": (150, 50, 50),      # 血雾
        "glow": (255, 100, 100),     # 血光
    },
}


def get_goliath_theme(style):
    """获取歌莉娅涂装主题"""
    # 处理短名称转换
    if style == "default":
        style = "goliath_default"
    elif not style.startswith("goliath_") and f"goliath_{style}" in GOLIATH_THEMES:
        style = f"goliath_{style}"
    
    if style in GOLIATH_THEMES:
        return GOLIATH_THEMES[style]
    return GOLIATH_THEMES["goliath_default"]


def get_goliath_skin_list():
    """获取所有涂装列表"""
    return list(GOLIATH_THEMES.keys())


def get_goliath_skin_info(style):
    """获取涂装详细信息"""
    theme = get_goliath_theme(style)
    return {
        "id": style,
        "name": theme["name"],
        "colors": {
            "armor": theme["armor"],
            "toxic": theme["toxic"],
            "rust": theme["rust"]
        }
    }


# 完整涂装样式列表（带 goliath_ 前缀）
GOLIATH_STYLES = [
    "goliath_default", "goliath_nuclear", "goliath_desert", "goliath_arctic",
    "goliath_necrosis", "goliath_pandemic", "goliath_spore", "goliath_chemical",
    "goliath_refinery", "goliath_hive", "goliath_xenomorph", "goliath_crimson",
    "default"  # 也支持短名称
]


def is_goliath_style(style):
    """检查是否为歌莉娅涂装"""
    if style in GOLIATH_STYLES:
        return True
    # 也检查短名称
    if style in GOLIATH_THEMES:
        return True
    return False


# ==================== 涂装绘制调度 ====================
def draw_goliath(surface, color, x, y, w, h, frame, style="goliath_default"):
    """绘制歌莉娅机体 - 根据涂装调用专属绘制"""
    # 处理短名称转换
    if style == "default":
        style = "goliath_default"
    elif not style.startswith("goliath_") and f"goliath_{style}" in GOLIATH_THEMES:
        style = f"goliath_{style}"
    
    drawers = {
        "goliath_default": draw_default_goliath,
        "goliath_nuclear": draw_nuclear_goliath,
        "goliath_desert": draw_desert_goliath,
        "goliath_arctic": draw_arctic_goliath,
        "goliath_necrosis": draw_necrosis_goliath,
        "goliath_pandemic": draw_pandemic_goliath,
        "goliath_spore": draw_spore_goliath,
        "goliath_chemical": draw_chemical_goliath,
        "goliath_refinery": draw_refinery_goliath,
        "goliath_hive": draw_hive_goliath,
        "goliath_xenomorph": draw_xenomorph_goliath,
        "goliath_crimson": draw_crimson_goliath,
    }
    drawer = drawers.get(style, draw_default_goliath)
    drawer(surface, x, y, w, h, frame, style)


def render_goliath_skin(surface, color, x, y, w, h, frame, style):
    """渲染歌莉娅涂装"""
    draw_goliath(surface, color, x, y, w, h, frame, style)


# ==================== 通用绘制辅助函数 ====================
def _draw_goliath_body(surface, x, y, w, h, frame, theme):
    """
    绘制歌莉娅主体 - 瘟疫蜂后仿生重型轰炸机
    七层精细绘制：毒雾背景→喷气背包→六足骨架→机甲胸腹→弹舱肚→单眼头→翼装挂载
    """
    armor = theme["armor"]
    toxic = theme["toxic"]
    rust = theme["rust"]
    eye_color = theme["eye"]
    smoke = theme["smoke"]
    glow = theme["glow"]
    
    # 颜色变体
    armor_light = tuple(min(255, c + 40) for c in armor)
    armor_dark = tuple(max(0, c - 40) for c in armor)
    armor_shadow = tuple(max(0, c - 70) for c in armor)
    toxic_bright = tuple(min(255, c + 60) for c in toxic)
    toxic_dark = tuple(max(0, c - 60) for c in toxic)
    rust_light = tuple(min(255, c + 30) for c in rust)
    rust_dark = tuple(max(0, c - 40) for c in rust)
    
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # ========== 【第一层】瘟疫毒雾背景 ==========
    # 毒气扩散光晕
    for ring in range(5):
        ring_r = int(50 - ring * 8 + 5 * math.sin(t * 1.2 + ring * 0.5))
        ring_alpha = max(0, 25 - ring * 5)
        if ring_r > 0:
            glow_surf = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*toxic, ring_alpha), (ring_r + 2, ring_r + 2), ring_r)
            surface.blit(glow_surf, (cx - ring_r - 2, cy - ring_r - 2))
    
    # 六边形生化警戒网格
    hex_radius = 45 + 4 * math.sin(t * 0.8)
    for ring in range(2):
        ring_r = hex_radius - ring * 15
        if ring_r > 0:
            hex_pts = []
            for i in range(6):
                angle = math.radians(i * 60 + t * 3)
                hx = cx + math.cos(angle) * ring_r
                hy = cy + math.sin(angle) * ring_r * 0.7
                hex_pts.append((int(hx), int(hy)))
            pygame.draw.polygon(surface, (*toxic, 15 - ring * 5), hex_pts, 1)
    
    # ========== 【第二层】喷气背包系统 ==========
    jetpack_cx = cx
    jetpack_cy = cy - int(h * 0.28)
    
    # 背包主壳 - 军用箱式设计
    pack_w, pack_h = int(w * 0.55), int(h * 0.28)
    pack_pts = [
        (jetpack_cx - pack_w//2 + 5, jetpack_cy - pack_h//2),        # 左上
        (jetpack_cx + pack_w//2 - 5, jetpack_cy - pack_h//2),        # 右上
        (jetpack_cx + pack_w//2, jetpack_cy - pack_h//2 + 8),        # 右上角
        (jetpack_cx + pack_w//2, jetpack_cy + pack_h//2 - 5),        # 右下角
        (jetpack_cx + pack_w//2 - 8, jetpack_cy + pack_h//2),        # 右下
        (jetpack_cx - pack_w//2 + 8, jetpack_cy + pack_h//2),        # 左下
        (jetpack_cx - pack_w//2, jetpack_cy + pack_h//2 - 5),        # 左下角
        (jetpack_cx - pack_w//2, jetpack_cy - pack_h//2 + 8),        # 左上角
    ]
    pygame.draw.polygon(surface, armor_dark, pack_pts)
    pygame.draw.polygon(surface, armor_shadow, pack_pts, 2)
    
    # 背包顶部进气口
    intake_w = int(pack_w * 0.6)
    pygame.draw.rect(surface, armor_shadow, 
                    (jetpack_cx - intake_w//2, jetpack_cy - pack_h//2 - 4, intake_w, 6))
    # 进气格栅
    for i in range(5):
        gx = jetpack_cx - intake_w//2 + 6 + i * int(intake_w / 5)
        pygame.draw.line(surface, armor, (gx, jetpack_cy - pack_h//2 - 3), 
                        (gx, jetpack_cy - pack_h//2 + 1), 1)
    
    # 双推进器喷口
    for side in [-1, 1]:
        nozzle_x = jetpack_cx + side * int(pack_w * 0.28)
        nozzle_y = jetpack_cy + int(pack_h * 0.3)
        
        # 喷口外壳（圆锥形）
        nozzle_r = int(w * 0.08)
        pygame.draw.circle(surface, rust, (nozzle_x, nozzle_y), nozzle_r + 2)
        pygame.draw.circle(surface, rust_dark, (nozzle_x, nozzle_y), nozzle_r)
        pygame.draw.circle(surface, (20, 20, 20), (nozzle_x, nozzle_y), nozzle_r - 3)
        
        # 喷口内环纹
        for ring in range(3):
            pygame.draw.circle(surface, (*rust_light, 100), (nozzle_x, nozzle_y), nozzle_r - 1 - ring * 2, 1)
        
        # 推进火焰（多层渐变）
        flame_base_len = int(h * 0.2)
        flame_len = int(flame_base_len * (1 + 0.4 * math.sin(t * 10 + side)))
        
        for layer in range(5):
            f_len = flame_len - layer * 5
            f_width = nozzle_r - 1 - layer * 1.5
            f_alpha = 255 - layer * 40
            
            if f_len > 0 and f_width > 1:
                # 火焰颜色渐变：绿->黄->白
                if layer < 2:
                    f_color = toxic
                elif layer < 4:
                    f_color = toxic_bright
                else:
                    f_color = (255, 255, 200)
                
                flame_pts = [
                    (int(nozzle_x - f_width), nozzle_y + 2),
                    (int(nozzle_x + f_width), nozzle_y + 2),
                    (int(nozzle_x + side * 2), nozzle_y + f_len),
                ]
                pygame.draw.polygon(surface, (*f_color, f_alpha), flame_pts)
        
        # 火焰粒子
        for i in range(3):
            p_offset = random.randint(-3, 3) if 'random' in dir() else int(3 * math.sin(t * 15 + i))
            p_y = nozzle_y + flame_len + 5 + i * 4
            p_size = 3 - i
            if p_size > 0:
                pygame.draw.circle(surface, (*toxic_bright, 150 - i * 40), 
                                  (nozzle_x + p_offset, p_y), p_size)
    
    # 背包中央毒气罐
    tank_x, tank_y = jetpack_cx, jetpack_cy
    tank_w, tank_h = int(pack_w * 0.25), int(pack_h * 0.7)
    pygame.draw.ellipse(surface, armor, (tank_x - tank_w//2, tank_y - tank_h//2, tank_w, tank_h))
    # 毒液可见窗
    window_h = int(tank_h * 0.5)
    liquid_level = int(window_h * (0.6 + 0.2 * math.sin(t * 2)))
    pygame.draw.rect(surface, (30, 30, 30), (tank_x - 4, tank_y - window_h//2, 8, window_h))
    pygame.draw.rect(surface, toxic, (tank_x - 3, tank_y - window_h//2 + (window_h - liquid_level), 6, liquid_level))
    # 气泡
    for i in range(2):
        bubble_y = tank_y - window_h//2 + int((window_h - liquid_level) + liquid_level * (0.3 + 0.3 * i) + 3 * math.sin(t * 5 + i))
        pygame.draw.circle(surface, toxic_bright, (tank_x + (i - 1) * 2, int(bubble_y)), 1)
    
    # ========== 【第三层】六足/蜂腿骨架（机械昆虫腿） ==========
    leg_base_y = cy + int(h * 0.05)
    
    for leg_idx in range(6):
        # 三对腿：前、中、后
        if leg_idx < 2:
            leg_y = leg_base_y - int(h * 0.15)
            leg_len = int(w * 0.25)
            leg_angle_base = -30
        elif leg_idx < 4:
            leg_y = leg_base_y
            leg_len = int(w * 0.3)
            leg_angle_base = 0
        else:
            leg_y = leg_base_y + int(h * 0.12)
            leg_len = int(w * 0.22)
            leg_angle_base = 25
        
        side = 1 if leg_idx % 2 == 1 else -1
        leg_x = cx + side * int(w * 0.22)
        
        # 腿部摆动
        swing = 5 * math.sin(t * 3 + leg_idx * 0.6)
        leg_angle = math.radians(leg_angle_base + side * 45 + swing)
        
        # 第一节（股节）
        joint1_x = leg_x + int(math.cos(leg_angle) * leg_len * 0.5) * side
        joint1_y = leg_y + int(math.sin(leg_angle) * leg_len * 0.3)
        pygame.draw.line(surface, armor, (leg_x, leg_y), (joint1_x, joint1_y), 4)
        pygame.draw.circle(surface, rust, (leg_x, leg_y), 4)
        pygame.draw.circle(surface, rust, (joint1_x, joint1_y), 3)
        
        # 第二节（胫节）
        joint2_angle = leg_angle + math.radians(30 * side)
        joint2_x = joint1_x + int(math.cos(joint2_angle) * leg_len * 0.4) * side
        joint2_y = joint1_y + int(math.sin(joint2_angle) * leg_len * 0.5) + 5
        pygame.draw.line(surface, armor_dark, (joint1_x, joint1_y), (joint2_x, joint2_y), 3)
        
        # 腿尖（跗节）- 尖刺
        pygame.draw.line(surface, rust, (joint2_x, joint2_y), 
                        (joint2_x + side * 5, joint2_y + 8), 2)
        
        # 腿部毒液管道
        pygame.draw.line(surface, (*toxic, 120), (leg_x, leg_y), (joint1_x, joint1_y), 1)
    
    # ========== 【第四层】机甲胸腹主体 ==========
    # 胸甲（上半身护甲）
    thorax_w, thorax_h = int(w * 0.65), int(h * 0.38)
    thorax_y = cy - int(h * 0.08)
    
    thorax_pts = [
        (cx, thorax_y - thorax_h//2),                           # 顶部尖
        (cx + thorax_w//4, thorax_y - thorax_h//2 + 8),         # 右上
        (cx + thorax_w//2, thorax_y - thorax_h//4),             # 右肩
        (cx + thorax_w//2 - 5, thorax_y + thorax_h//4),         # 右腰
        (cx + thorax_w//3, thorax_y + thorax_h//2),             # 右底
        (cx - thorax_w//3, thorax_y + thorax_h//2),             # 左底
        (cx - thorax_w//2 + 5, thorax_y + thorax_h//4),         # 左腰
        (cx - thorax_w//2, thorax_y - thorax_h//4),             # 左肩
        (cx - thorax_w//4, thorax_y - thorax_h//2 + 8),         # 左上
    ]
    pygame.draw.polygon(surface, armor, thorax_pts)
    pygame.draw.polygon(surface, armor_light, thorax_pts, 2)
    
    # 胸甲分割线和铆钉
    pygame.draw.line(surface, armor_shadow, (cx, thorax_y - thorax_h//2 + 5), 
                    (cx, thorax_y + thorax_h//2 - 5), 2)
    
    for side in [-1, 1]:
        # 侧面装甲板
        plate_pts = [
            (cx + side * thorax_w//4, thorax_y - thorax_h//3),
            (cx + side * (thorax_w//2 - 3), thorax_y - thorax_h//6),
            (cx + side * (thorax_w//2 - 8), thorax_y + thorax_h//4),
            (cx + side * thorax_w//4, thorax_y + thorax_h//3),
        ]
        pygame.draw.polygon(surface, armor_dark, plate_pts)
        pygame.draw.polygon(surface, (*armor_shadow, 150), plate_pts, 1)
        
        # 铆钉阵列
        for i in range(4):
            rivet_x = cx + side * (thorax_w//4 + 5)
            rivet_y = thorax_y - thorax_h//3 + 5 + i * int(thorax_h * 0.2)
            pygame.draw.circle(surface, rust, (rivet_x, rivet_y), 2)
            pygame.draw.circle(surface, rust_light, (rivet_x - 1, rivet_y - 1), 1)
    
    # 危险条纹（黄黑警戒）
    stripe_y = thorax_y + thorax_h//4
    stripe_w = thorax_w - 20
    for i in range(8):
        sx = cx - stripe_w//2 + i * int(stripe_w / 8)
        if i % 2 == 0:
            pygame.draw.rect(surface, (200, 180, 0), (sx, stripe_y, int(stripe_w / 8), 6))
        else:
            pygame.draw.rect(surface, (30, 30, 30), (sx, stripe_y, int(stripe_w / 8), 6))
    
    # 毒液渗漏效果
    for i in range(4):
        drip_x = cx - int(w * 0.2) + i * int(w * 0.13)
        drip_start = thorax_y + thorax_h//3
        drip_len = int(h * 0.08 * (1 + 0.5 * math.sin(t * 2.5 + i * 0.8)))
        
        # 渗漏线
        for seg in range(int(drip_len / 3)):
            seg_y = drip_start + seg * 3
            seg_alpha = 180 - seg * 20
            if seg_alpha > 0:
                pygame.draw.circle(surface, (*toxic, seg_alpha), (drip_x, seg_y), 2)
        # 滴液末端
        pygame.draw.circle(surface, toxic, (drip_x, drip_start + drip_len), 3)
        pygame.draw.circle(surface, toxic_bright, (drip_x - 1, drip_start + drip_len - 1), 1)
    
    # ========== 【第五层】玻璃腹舱（弹药库可视） ==========
    belly_y = cy + int(h * 0.22)
    belly_w, belly_h = int(w * 0.55), int(h * 0.32)
    
    # 舱体外框
    pygame.draw.ellipse(surface, armor_shadow, 
                       (cx - belly_w//2 - 2, belly_y - belly_h//2 - 2, belly_w + 4, belly_h + 4))
    
    # 玻璃外壳（半透明）
    belly_surf = pygame.Surface((belly_w, belly_h), pygame.SRCALPHA)
    pygame.draw.ellipse(belly_surf, (*armor, 120), (0, 0, belly_w, belly_h))
    surface.blit(belly_surf, (cx - belly_w//2, belly_y - belly_h//2))
    
    # 内部毒液
    inner_w, inner_h = int(belly_w * 0.88), int(belly_h * 0.88)
    liquid_surf = pygame.Surface((inner_w, inner_h), pygame.SRCALPHA)
    pygame.draw.ellipse(liquid_surf, (*toxic, 100), (0, 0, inner_w, inner_h))
    surface.blit(liquid_surf, (cx - inner_w//2, belly_y - inner_h//2))
    
    # 液面波纹
    wave_offset = int(5 * math.sin(t * 3))
    for wave in range(3):
        wave_y_pos = belly_y - inner_h//4 + wave * 8 + wave_offset
        wave_alpha = 80 - wave * 20
        wave_width = inner_w - wave * 10
        if wave_alpha > 0:
            pygame.draw.arc(surface, (*glow, wave_alpha),
                          (cx - wave_width//2, wave_y_pos - 5, wave_width, 10),
                          0, math.pi, 2)
    
    # 内部导弹阵列（5枚）
    for i in range(5):
        missile_x = cx - int(w * 0.18) + i * int(w * 0.09)
        missile_y = belly_y + int(h * 0.02)
        
        # 导弹主体
        pygame.draw.ellipse(surface, (*armor, 180), 
                           (missile_x - 4, missile_y - 10, 8, 20))
        # 弹头（红色）
        pygame.draw.polygon(surface, (*eye_color, 200), [
            (missile_x, missile_y - 12),
            (missile_x - 3, missile_y - 8),
            (missile_x + 3, missile_y - 8),
        ])
        # 尾翼
        pygame.draw.line(surface, (*rust, 180), (missile_x - 4, missile_y + 8), (missile_x - 6, missile_y + 12), 2)
        pygame.draw.line(surface, (*rust, 180), (missile_x + 4, missile_y + 8), (missile_x + 6, missile_y + 12), 2)
        # 生化标志
        pygame.draw.circle(surface, (*toxic, 220), (missile_x, missile_y), 2)
    
    # 舱门铰链
    for side in [-1, 1]:
        hinge_x = cx + side * (belly_w//2 - 8)
        for i in range(3):
            hinge_y = belly_y - belly_h//4 + i * int(belly_h * 0.25)
            pygame.draw.circle(surface, rust, (hinge_x, hinge_y), 3)
            pygame.draw.circle(surface, rust_dark, (hinge_x, hinge_y), 2)
    
    # ========== 【第六层】单眼机械昆虫头 ==========
    head_y = cy - int(h * 0.38)
    head_w, head_h = int(w * 0.42), int(h * 0.26)
    
    # 头部主体 - 昆虫头形状
    head_pts = [
        (cx, head_y - head_h//2 - 5),                    # 顶尖
        (cx + head_w//3, head_y - head_h//2 + 5),        # 右上
        (cx + head_w//2, head_y - head_h//6),            # 右眼眶
        (cx + head_w//2 - 5, head_y + head_h//3),        # 右颊
        (cx + head_w//4, head_y + head_h//2),            # 右下颚
        (cx, head_y + head_h//2 + 5),                    # 下巴
        (cx - head_w//4, head_y + head_h//2),            # 左下颚
        (cx - head_w//2 + 5, head_y + head_h//3),        # 左颊
        (cx - head_w//2, head_y - head_h//6),            # 左眼眶
        (cx - head_w//3, head_y - head_h//2 + 5),        # 左上
    ]
    pygame.draw.polygon(surface, armor, head_pts)
    pygame.draw.polygon(surface, armor_light, head_pts, 2)
    
    # 头甲分割线
    pygame.draw.line(surface, armor_shadow, (cx, head_y - head_h//2), (cx, head_y + head_h//2), 1)
    for side in [-1, 1]:
        pygame.draw.line(surface, armor_dark, 
                        (cx + side * head_w//4, head_y - head_h//3),
                        (cx + side * head_w//3, head_y + head_h//4), 1)
    
    # 触角（短机械天线）
    for side in [-1, 1]:
        ant_x = cx + side * head_w//4
        ant_y = head_y - head_h//2
        # 触角基座
        pygame.draw.circle(surface, rust, (ant_x, ant_y), 3)
        # 触角杆
        ant_tip_x = ant_x + side * 8
        ant_tip_y = ant_y - 12
        pygame.draw.line(surface, armor_dark, (ant_x, ant_y), (ant_tip_x, ant_tip_y), 2)
        # 触角尖端发光
        ant_glow = int(2 + 1 * math.sin(t * 6 + side))
        pygame.draw.circle(surface, toxic, (ant_tip_x, ant_tip_y), ant_glow)
    
    # 巨大单眼（瘟疫视觉）
    eye_cx, eye_cy = cx, head_y - int(head_h * 0.05)
    eye_outer_r = int(head_w * 0.35)
    eye_inner_r = int(eye_outer_r * 0.75)
    
    # 眼眶（金属环）
    pygame.draw.circle(surface, armor_shadow, (eye_cx, eye_cy), eye_outer_r + 3)
    pygame.draw.circle(surface, rust, (eye_cx, eye_cy), eye_outer_r + 1, 3)
    
    # 镜头底层（深黑）
    pygame.draw.circle(surface, (15, 15, 20), (eye_cx, eye_cy), eye_outer_r)
    
    # 瘟疫之眼（脉动效果）
    eye_pulse = 0.7 + 0.3 * math.sin(t * 3.5)
    
    # 红色辐射光晕
    for ring in range(4):
        ring_r = int((eye_inner_r - ring * 4) * eye_pulse)
        ring_alpha = int((200 - ring * 40) * eye_pulse)
        if ring_r > 0:
            pygame.draw.circle(surface, (*eye_color, ring_alpha), (eye_cx, eye_cy), ring_r)
    
    # 核心瞳孔
    pupil_r = int(eye_inner_r * 0.4 * eye_pulse)
    pygame.draw.circle(surface, (50, 0, 0), (eye_cx, eye_cy), pupil_r + 2)
    pygame.draw.circle(surface, (20, 0, 0), (eye_cx, eye_cy), pupil_r)
    
    # 瞳孔十字准星
    cross_len = int(eye_inner_r * 0.6)
    pygame.draw.line(surface, (*eye_color, 180), (eye_cx - cross_len, eye_cy), (eye_cx + cross_len, eye_cy), 1)
    pygame.draw.line(surface, (*eye_color, 180), (eye_cx, eye_cy - cross_len), (eye_cx, eye_cy + cross_len), 1)
    
    # 眼球高光
    highlight_x = eye_cx - int(eye_outer_r * 0.25)
    highlight_y = eye_cy - int(eye_outer_r * 0.25)
    pygame.draw.circle(surface, (255, 255, 255, 200), (highlight_x, highlight_y), 3)
    pygame.draw.circle(surface, (255, 200, 200, 150), (highlight_x + 2, highlight_y + 4), 2)
    
    # 镜头边缘反光
    pygame.draw.arc(surface, (*armor_light, 100), 
                   (eye_cx - eye_outer_r, eye_cy - eye_outer_r, eye_outer_r * 2, eye_outer_r * 2),
                   math.pi * 0.8, math.pi * 1.2, 2)
    
    # 口器/机炮阵列
    mouth_y = head_y + int(head_h * 0.35)
    for i in range(5):
        gun_x = cx - 10 + i * 5
        gun_len = 8 + (2 - abs(i - 2)) * 3
        pygame.draw.rect(surface, rust_dark, (gun_x - 1, mouth_y, 3, gun_len))
        pygame.draw.rect(surface, (30, 30, 30), (gun_x, mouth_y + gun_len - 2, 1, 3))
    
    # ========== 【第七层】翼装武器挂载 ==========
    wing_y = cy - int(h * 0.02)
    wing_span = int(w * 0.48)
    
    for side in [-1, 1]:
        wing_root_x = cx + side * int(w * 0.2)
        
        # 主翼型面
        wing_pts = [
            (wing_root_x, wing_y - 8),                                    # 前缘根部
            (wing_root_x + side * int(wing_span * 0.3), wing_y - 10),     # 前缘中
            (wing_root_x + side * wing_span, wing_y - 5),                 # 翼尖前
            (wing_root_x + side * wing_span, wing_y + 8),                 # 翼尖后
            (wing_root_x + side * int(wing_span * 0.4), wing_y + 12),     # 后缘中
            (wing_root_x, wing_y + 10),                                   # 后缘根部
        ]
        pygame.draw.polygon(surface, armor, wing_pts)
        pygame.draw.polygon(surface, armor_light, wing_pts, 2)
        
        # 翼面加强筋
        for rib in range(4):
            rib_x = wing_root_x + side * int(wing_span * (0.15 + rib * 0.22))
            pygame.draw.line(surface, armor_dark, (rib_x, wing_y - 6), (rib_x, wing_y + 8), 1)
        
        # 翼尖毒液喷嘴
        tip_x = wing_root_x + side * wing_span
        pygame.draw.circle(surface, rust, (tip_x, wing_y + 2), 4)
        pygame.draw.circle(surface, toxic, (tip_x, wing_y + 2), 2)
        
        # 武器挂架（3个挂点）
        for pylon_idx in range(3):
            pylon_x = wing_root_x + side * int(wing_span * (0.25 + pylon_idx * 0.25))
            pylon_y = wing_y + 15
            
            # 挂架支柱
            pygame.draw.line(surface, armor_dark, (pylon_x, wing_y + 10), (pylon_x, pylon_y), 2)
            
            # 挂载物（交替：导弹、炸弹、无人机舱）
            if pylon_idx == 1:
                # 中央：大型瘟疫炸弹
                bomb_w, bomb_h = 10, 22
                pygame.draw.ellipse(surface, armor_dark, 
                                   (pylon_x - bomb_w//2, pylon_y, bomb_w, bomb_h))
                # 炸弹尾翼
                pygame.draw.polygon(surface, rust, [
                    (pylon_x - 6, pylon_y + bomb_h - 5),
                    (pylon_x + 6, pylon_y + bomb_h - 5),
                    (pylon_x, pylon_y + bomb_h + 5),
                ])
                # 生化标志
                pygame.draw.circle(surface, toxic, (pylon_x, pylon_y + bomb_h//2), 4)
                pygame.draw.circle(surface, (30, 30, 30), (pylon_x, pylon_y + bomb_h//2), 2)
            else:
                # 侧面：小型导弹
                missile_h = 18
                pygame.draw.ellipse(surface, armor, 
                                   (pylon_x - 3, pylon_y, 6, missile_h))
                # 导弹头
                pygame.draw.polygon(surface, eye_color, [
                    (pylon_x, pylon_y + missile_h + 4),
                    (pylon_x - 3, pylon_y + missile_h),
                    (pylon_x + 3, pylon_y + missile_h),
                ])
    
    # ========== 【第八层】细节增强 ==========
    # 整体毒气发光效果
    glow_surf = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
    glow_intensity = int(20 + 10 * math.sin(t * 2))
    pygame.draw.ellipse(glow_surf, (*glow, glow_intensity), 
                       (10, int(h * 0.3), w, int(h * 0.5)))
    surface.blit(glow_surf, (x - 10, y - 10), special_flags=pygame.BLEND_RGBA_ADD)
    
    # 排气烟雾粒子
    for i in range(6):
        smoke_x = cx + int(15 * math.sin(t * 2 + i * 1.2))
        smoke_y = cy + int(h * 0.45) + i * 8 + int(5 * math.sin(t * 3 + i))
        smoke_size = 4 + i
        smoke_alpha = max(0, 60 - i * 10)
        if smoke_alpha > 0:
            pygame.draw.circle(surface, (*smoke, smoke_alpha), (smoke_x, smoke_y), smoke_size)


def _draw_toxic_particles(surface, x, y, w, h, frame, theme):
    """绘制毒气粒子效果"""
    toxic = theme["toxic"]
    t = frame * 0.1
    
    cx, cy = x + w // 2, y + h // 2
    
    for i in range(8):
        angle = t + i * math.pi / 4
        dist = int(w * 0.4 + w * 0.1 * math.sin(t * 2 + i))
        px = cx + int(math.cos(angle) * dist)
        py = cy + int(math.sin(angle) * dist * 0.6)
        
        size = int(3 + 2 * math.sin(t * 3 + i * 0.5))
        alpha = int(100 + 50 * math.sin(t * 2 + i))
        
        pygame.draw.circle(surface, (*toxic, alpha), (px, py), size)


def _draw_smoke_trail(surface, x, y, w, h, frame, theme):
    """绘制烟雾拖尾"""
    smoke = theme["smoke"]
    t = frame * 0.05
    
    cx = x + w // 2
    base_y = y + int(h * 0.8)
    
    for i in range(5):
        offset_x = int(10 * math.sin(t * 2 + i * 0.5))
        offset_y = i * 8
        size = int(8 - i * 1.2)
        alpha = int(150 - i * 25)
        
        if size > 0 and alpha > 0:
            pygame.draw.circle(surface, (*smoke, alpha), 
                             (cx + offset_x, base_y + offset_y), size)


def _draw_hazard_stripes(surface, x, y, w, h, theme):
    """绘制危险条纹"""
    # 黄黑警告条纹
    stripe_w = 6
    stripe_count = w // stripe_w
    
    for i in range(stripe_count):
        if i % 2 == 0:
            color = (255, 200, 0, 150)
        else:
            color = (30, 30, 30, 150)
        pygame.draw.rect(surface, color, 
                        (x + i * stripe_w, y + h - 8, stripe_w, 6))


# ==================== 默认涂装：瘟疫使者 ====================
def draw_default_goliath(surface, x, y, w, h, frame, style):
    """
    默认涂装 - 瘟疫使者原型（军用生化轰炸机）
    特色：经典军用蜂后，橄榄绿装甲+酸性绿毒液
    独特元素：旋转生化标志、军用星徽、弹药计数器、战术HUD、军用条纹
    """
    theme = get_goliath_theme(style)
    armor = theme["armor"]
    toxic = theme["toxic"]
    rust = theme["rust"]
    eye_color = theme["eye"]
    glow = theme["glow"]
    
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 【独特背景1】军用雷达扫描波
    radar_cx, radar_cy = cx, cy
    for ring in range(4):
        radar_r = int(w * 0.5 - ring * 12)
        radar_alpha = int(20 - ring * 4)
        if radar_r > 0 and radar_alpha > 0:
            pygame.draw.circle(surface, (*toxic, radar_alpha), (radar_cx, radar_cy), radar_r, 1)
    # 扫描线
    scan_angle = t * 3
    scan_len = int(w * 0.5)
    scan_end_x = cx + int(math.cos(scan_angle) * scan_len)
    scan_end_y = cy + int(math.sin(scan_angle) * scan_len * 0.5)
    pygame.draw.line(surface, (*toxic, 60), (cx, cy), (scan_end_x, scan_end_y), 2)
    
    # 基础烟雾
    _draw_smoke_trail(surface, x, y, w, h, frame, theme)
    
    # 主体绘制
    _draw_goliath_body(surface, x, y, w, h, frame, theme)
    
    # 【独特元素1】大型旋转生化危险标志
    bio_cx, bio_cy = cx, cy + int(h * 0.2)
    bio_r = int(w * 0.14)
    
    # 外圈发光
    for glow_ring in range(3):
        glow_r = bio_r + 5 + glow_ring * 3
        glow_alpha = int(40 - glow_ring * 12)
        pygame.draw.circle(surface, (*toxic, glow_alpha), (bio_cx, bio_cy), glow_r)
    
    # 黑底圆盘
    pygame.draw.circle(surface, (20, 20, 20), (bio_cx, bio_cy), bio_r + 2)
    pygame.draw.circle(surface, (255, 200, 0), (bio_cx, bio_cy), bio_r, 3)
    
    # 旋转三叶草
    for i in range(3):
        leaf_angle = math.radians(i * 120 - 90) + t * 1.5
        # 扇形叶片
        for arc in range(12):
            arc_angle = leaf_angle - 0.35 + arc * 0.06
            arc_r = bio_r * (0.4 + 0.45 * (1 - abs(arc - 6) / 6))
            ax = bio_cx + int(math.cos(arc_angle) * arc_r)
            ay = bio_cy + int(math.sin(arc_angle) * arc_r)
            pygame.draw.circle(surface, (255, 200, 0), (ax, ay), 3)
    pygame.draw.circle(surface, (20, 20, 20), (bio_cx, bio_cy), int(bio_r * 0.25))
    
    # 【独特元素2】军用星徽
    for side in [-1, 1]:
        star_x = cx + side * int(w * 0.38)
        star_y = cy - int(h * 0.05)
        star_r = 10
        # 五角星
        star_pts = []
        for i in range(10):
            angle = -math.pi/2 + i * math.pi / 5
            r = star_r if i % 2 == 0 else star_r * 0.4
            star_pts.append((star_x + int(math.cos(angle) * r), 
                           star_y + int(math.sin(angle) * r)))
        pygame.draw.polygon(surface, (240, 240, 240), star_pts)
        pygame.draw.polygon(surface, armor, star_pts, 1)
        # 星徽圆环
        pygame.draw.circle(surface, (240, 240, 240), (star_x, star_y), star_r + 4, 2)
    
    # 【独特元素3】弹药计数器显示
    ammo_x, ammo_y = cx - int(w * 0.18), cy - int(h * 0.28)
    pygame.draw.rect(surface, (20, 25, 20), (ammo_x - 15, ammo_y - 8, 30, 16))
    pygame.draw.rect(surface, toxic, (ammo_x - 15, ammo_y - 8, 30, 16), 1)
    # LED数字模拟
    digit_val = int((t * 10) % 100)
    for d in range(2):
        dx = ammo_x - 8 + d * 12
        # 7段显示简化
        pygame.draw.rect(surface, toxic, (dx, ammo_y - 5, 8, 2))  # 上
        pygame.draw.rect(surface, toxic, (dx, ammo_y - 1, 8, 2))  # 中
        pygame.draw.rect(surface, toxic, (dx, ammo_y + 3, 8, 2))  # 下
    
    # 【独特元素4】战术HUD准星
    hud_y = cy - int(h * 0.1)
    # 十字准星
    pygame.draw.line(surface, (*toxic, 150), (cx - 20, hud_y), (cx - 8, hud_y), 2)
    pygame.draw.line(surface, (*toxic, 150), (cx + 8, hud_y), (cx + 20, hud_y), 2)
    pygame.draw.line(surface, (*toxic, 150), (cx, hud_y - 15), (cx, hud_y - 5), 2)
    pygame.draw.line(surface, (*toxic, 150), (cx, hud_y + 5), (cx, hud_y + 15), 2)
    # 角标
    for corner in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        cx_off = cx + corner[0] * 15
        cy_off = hud_y + corner[1] * 12
        pygame.draw.line(surface, (*toxic, 120), (cx_off, cy_off), 
                        (cx_off - corner[0] * 6, cy_off), 1)
        pygame.draw.line(surface, (*toxic, 120), (cx_off, cy_off), 
                        (cx_off, cy_off - corner[1] * 5), 1)
    
    # 【独特元素5】军用迷彩斑块
    camo_spots = [
        (cx - 22, cy - 18, 15, 10), (cx + 18, cy - 12, 12, 14),
        (cx - 12, cy + 8, 18, 9), (cx + 15, cy + 15, 14, 11),
    ]
    for spot_x, spot_y, sw, sh in camo_spots:
        spot_color = tuple(max(0, c - 25) for c in armor)
        spot_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        pygame.draw.ellipse(spot_surf, (*spot_color, 100), (0, 0, sw, sh))
        surface.blit(spot_surf, (spot_x - sw//2, spot_y - sh//2))
    
    # 【独特元素6】危险条纹（前后双条）
    for stripe_y in [cy + int(h * 0.35), cy - int(h * 0.32)]:
        stripe_w = int(w * 0.65)
        for i in range(12):
            sx = cx - stripe_w//2 + i * int(stripe_w / 12)
            stripe_color = (255, 200, 0) if i % 2 == 0 else (30, 30, 30)
            pygame.draw.rect(surface, stripe_color, (sx, stripe_y, int(stripe_w / 12) + 1, 4))
    
    # 毒气粒子
    _draw_toxic_particles(surface, x, y, w, h, frame, theme)


# ==================== 核冬幽魂涂装 ====================
def draw_nuclear_goliath(surface, x, y, w, h, frame, style):
    """
    核冬幽魂 - 核末日幸存者（切尔诺贝利风格）
    特色：铅灰防辐射装甲、辐射黄警告、盖革计数器、核冬天灰烬
    独特元素：巨型辐射标志、核弹挂载、辐射云、盖革仪表、铅板装甲、灰烬雪
    """
    theme = get_goliath_theme(style)
    armor = theme["armor"]
    toxic = theme["toxic"]  # 辐射黄
    rust = theme["rust"]
    eye_color = theme["eye"]
    glow = theme["glow"]
    
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 【独特背景1】核冬天灰烬雪
    for i in range(30):
        ash_x = cx + int((w * 0.8) * math.sin(t * 0.5 + i * 0.21))
        ash_y = y + int(h * 1.2 * ((t * 0.15 + i * 0.033) % 1))
        ash_size = 2 + (i % 3)
        ash_alpha = int(100 - (i % 4) * 20)
        pygame.draw.circle(surface, (80, 80, 75, ash_alpha), (ash_x, ash_y), ash_size)
    
    # 【独特背景2】辐射衰变粒子云
    for i in range(15):
        decay_angle = t * 0.4 + i * 0.42
        decay_dist = int(w * 0.48 + w * 0.12 * math.sin(t * 1.5 + i * 0.6))
        decay_x = cx + int(math.cos(decay_angle) * decay_dist)
        decay_y = cy + int(math.sin(decay_angle) * decay_dist * 0.45)
        decay_size = int(4 + 3 * math.sin(t * 2.5 + i))
        decay_alpha = int(70 + 40 * math.sin(t + i * 0.5))
        # 辐射粒子发光
        pygame.draw.circle(surface, (*toxic, decay_alpha), (decay_x, decay_y), decay_size)
        pygame.draw.circle(surface, (*glow, decay_alpha // 2), (decay_x, decay_y), decay_size + 2)
    
    # 主体绘制
    _draw_goliath_body(surface, x, y, w, h, frame, theme)
    
    # 【独特元素1】巨型旋转辐射标志（双层）
    rad_cx, rad_cy = cx, cy + int(h * 0.18)
    rad_r = int(w * 0.16)
    
    # 外层光晕
    for glow_ring in range(4):
        pygame.draw.circle(surface, (*toxic, 30 - glow_ring * 7), 
                          (rad_cx, rad_cy), rad_r + 8 + glow_ring * 4)
    
    # 黄色外圈（双线）
    pygame.draw.circle(surface, toxic, (rad_cx, rad_cy), rad_r + 3, 2)
    pygame.draw.circle(surface, toxic, (rad_cx, rad_cy), rad_r, 3)
    
    # 旋转三叶草（精细版）
    for i in range(3):
        leaf_angle = t * 2.5 + i * 2 * math.pi / 3
        # 精细扇形
        for arc in range(15):
            a = leaf_angle - 0.5 + arc * 0.07
            # 叶片形状曲线
            curve = 1 - abs(arc - 7) / 7
            r = rad_r * (0.3 + 0.55 * curve)
            px = rad_cx + int(math.cos(a) * r)
            py = rad_cy + int(math.sin(a) * r)
            pygame.draw.circle(surface, toxic, (px, py), int(3 + 2 * curve))
    
    pygame.draw.circle(surface, (15, 15, 15), (rad_cx, rad_cy), int(rad_r * 0.22))
    pygame.draw.circle(surface, toxic, (rad_cx, rad_cy), int(rad_r * 0.22), 1)
    
    # 【独特元素2】盖革计数器仪表盘
    gauge_x, gauge_y = cx + int(w * 0.22), cy - int(h * 0.22)
    gauge_r = 12
    
    # 仪表盘背景
    pygame.draw.circle(surface, (30, 30, 25), (gauge_x, gauge_y), gauge_r + 2)
    pygame.draw.circle(surface, rust, (gauge_x, gauge_y), gauge_r + 2, 2)
    
    # 刻度线
    for i in range(12):
        tick_angle = -math.pi * 0.8 + i * math.pi * 1.6 / 11
        tick_start = gauge_r - 3
        tick_end = gauge_r
        tx1 = gauge_x + int(math.cos(tick_angle) * tick_start)
        ty1 = gauge_y + int(math.sin(tick_angle) * tick_start)
        tx2 = gauge_x + int(math.cos(tick_angle) * tick_end)
        ty2 = gauge_y + int(math.sin(tick_angle) * tick_end)
        pygame.draw.line(surface, toxic, (tx1, ty1), (tx2, ty2), 1)
    
    # 指针（剧烈摆动）
    needle_angle = -math.pi * 0.8 + (math.sin(t * 8) * 0.5 + 0.5) * math.pi * 1.6
    needle_x = gauge_x + int(math.cos(needle_angle) * (gauge_r - 4))
    needle_y = gauge_y + int(math.sin(needle_angle) * (gauge_r - 4))
    pygame.draw.line(surface, (255, 50, 50), (gauge_x, gauge_y), (needle_x, needle_y), 2)
    pygame.draw.circle(surface, rust, (gauge_x, gauge_y), 2)
    
    # 【独特元素3】多组警告灯阵列
    warning_positions = [
        (cx - int(w * 0.28), cy - int(h * 0.18)),
        (cx + int(w * 0.28), cy - int(h * 0.18)),
        (cx - int(w * 0.32), cy + int(h * 0.05)),
        (cx + int(w * 0.32), cy + int(h * 0.05)),
    ]
    for idx, (lx, ly) in enumerate(warning_positions):
        # 灯座
        pygame.draw.circle(surface, (50, 50, 45), (lx, ly), 7)
        pygame.draw.circle(surface, rust, (lx, ly), 7, 1)
        # 疯狂闪烁（不同相位）
        blink_phase = t * 12 + idx * 1.5
        blink = int(abs(math.sin(blink_phase)) * 255)
        lamp_color = (255, blink, 0) if idx % 2 == 0 else (blink, 255, 0)
        pygame.draw.circle(surface, lamp_color, (lx, ly), 5)
        # 光晕
        if blink > 180:
            glow_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*toxic, 60), (12, 12), 12)
            surface.blit(glow_surf, (lx - 12, ly - 12))
    
    # 【独特元素4】铅板装甲贴片阵列
    plate_positions = [
        (cx - 20, cy - 25), (cx + 15, cy - 22), (cx - 25, cy - 5),
        (cx + 22, cy - 8), (cx - 18, cy + 15), (cx + 18, cy + 12),
    ]
    for px, py in plate_positions:
        plate_w, plate_h = 14 + random.randint(-2, 2), 10 + random.randint(-2, 2)
        # 铅板
        pygame.draw.rect(surface, (55, 55, 50), (px - plate_w//2, py - plate_h//2, plate_w, plate_h))
        pygame.draw.rect(surface, (70, 70, 65), (px - plate_w//2, py - plate_h//2, plate_w, plate_h), 1)
        # 四角铆钉
        for corner in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            rx = px + corner[0] * (plate_w//2 - 2)
            ry = py + corner[1] * (plate_h//2 - 2)
            pygame.draw.circle(surface, rust, (rx, ry), 2)
            pygame.draw.circle(surface, (100, 90, 70), (rx - 1, ry - 1), 1)
    
    # 【独特元素5】核弹挂载（精细版）
    for side in [-1, 1]:
        nuke_x = cx + side * int(w * 0.4)
        nuke_y = cy + int(h * 0.1)
        
        # 核弹主体
        pygame.draw.ellipse(surface, (50, 50, 48), (nuke_x - 7, nuke_y - 2, 14, 32))
        pygame.draw.ellipse(surface, (65, 65, 60), (nuke_x - 7, nuke_y - 2, 14, 32), 1)
        
        # 弹头（红色）
        pygame.draw.polygon(surface, (180, 50, 50), [
            (nuke_x, nuke_y - 8),
            (nuke_x - 5, nuke_y + 2),
            (nuke_x + 5, nuke_y + 2),
        ])
        
        # 尾翼
        for fin_side in [-1, 1]:
            pygame.draw.polygon(surface, (60, 60, 55), [
                (nuke_x + fin_side * 6, nuke_y + 25),
                (nuke_x + fin_side * 10, nuke_y + 32),
                (nuke_x + fin_side * 6, nuke_y + 30),
            ])
        
        # 辐射标志
        pygame.draw.circle(surface, toxic, (nuke_x, nuke_y + 12), 5)
        for i in range(3):
            leaf_a = i * 2 * math.pi / 3 - math.pi / 2
            lx = nuke_x + int(math.cos(leaf_a) * 3)
            ly = nuke_y + 12 + int(math.sin(leaf_a) * 3)
            pygame.draw.circle(surface, toxic, (lx, ly), 2)
        pygame.draw.circle(surface, (30, 30, 30), (nuke_x, nuke_y + 12), 2)
    
    # 【独特元素6】辐射污染区标记
    contamination_y = cy + int(h * 0.35)
    pygame.draw.rect(surface, (30, 30, 25), (cx - int(w * 0.35), contamination_y - 8, int(w * 0.7), 16))
    # 黑黄交替
    for i in range(14):
        stripe_x = cx - int(w * 0.35) + i * int(w * 0.05)
        color = toxic if i % 2 == 0 else (30, 30, 30)
        pygame.draw.rect(surface, color, (stripe_x, contamination_y - 6, int(w * 0.05), 12))


# ==================== 沙漠风暴涂装 ====================
def draw_desert_goliath(surface, x, y, w, h, frame, style):
    """
    沙漠风暴 - 海湾战争沙漠突袭者
    特色：多层沙漠迷彩、沙尘龙卷、灼热空气、阿拉伯风格图腾
    独特元素：六边形迷彩网格、沙漠蝎子涂装、太阳神徽、沙尘龙卷、热力学扭曲
    """
    theme = get_goliath_theme(style)
    armor = theme["armor"]  # 沙漠黄
    toxic = theme["toxic"]  # 沙尘色
    rust = theme["rust"]
    eye_color = theme["eye"]
    glow = theme["glow"]
    
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 【独特背景1】沙尘龙卷风
    tornado_cx = cx + int(15 * math.sin(t * 0.8))
    for layer in range(5):
        tornado_y = cy + int(h * 0.5) - layer * 18
        tornado_r = int(25 - layer * 4 + 5 * math.sin(t * 2 + layer))
        # 沙尘环
        for i in range(12):
            sand_angle = t * (3 + layer * 0.5) + i * 0.52 + layer * 0.3
            sand_x = tornado_cx + int(math.cos(sand_angle) * tornado_r)
            sand_y = tornado_y + int(math.sin(sand_angle) * tornado_r * 0.3)
            sand_size = int(4 - layer * 0.5 + 2 * math.sin(t * 4 + i))
            sand_alpha = int(120 - layer * 20)
            pygame.draw.circle(surface, (*toxic, sand_alpha), (sand_x, sand_y), max(1, sand_size))
    
    # 【独特背景2】热力学空气扭曲
    for wave_layer in range(6):
        wave_y = cy - int(h * 0.4) - wave_layer * 12
        wave_pts = []
        wave_amplitude = 5 + wave_layer
        for j in range(16):
            wx = cx - int(w * 0.5) + j * int(w / 15)
            wy = wave_y + int(wave_amplitude * math.sin(t * 5 + j * 0.4 + wave_layer * 0.5))
            wave_pts.append((wx, wy))
        if len(wave_pts) >= 2:
            wave_alpha = int(50 - wave_layer * 7)
            pygame.draw.lines(surface, (*armor, wave_alpha), False, wave_pts, 1)
    
    # 主体绘制
    _draw_goliath_body(surface, x, y, w, h, frame, theme)
    
    # 【独特元素1】六边形沙漠数码迷彩网格
    camo_colors = [
        (194, 178, 128),  # 亮沙
        (170, 155, 110),  # 中沙
        (140, 120, 85),   # 暗沙
        (120, 100, 70),   # 棕褐
    ]
    hex_size = 8
    for row in range(-4, 5):
        for col in range(-5, 6):
            hx = cx + col * int(hex_size * 1.5) + (row % 2) * int(hex_size * 0.75)
            hy = cy + row * int(hex_size * 1.3)
            
            # 只在机身范围内绘制
            dist = math.sqrt((hx - cx)**2 + ((hy - cy) * 1.5)**2)
            if dist < w * 0.38:
                hex_pts = []
                for i in range(6):
                    angle = i * math.pi / 3
                    hex_pts.append((
                        hx + int(math.cos(angle) * hex_size * 0.45),
                        hy + int(math.sin(angle) * hex_size * 0.45)
                    ))
                # 随机迷彩颜色
                color_idx = (row + col + int(t)) % 4
                pygame.draw.polygon(surface, (*camo_colors[color_idx], 90), hex_pts)
    
    # 【独特元素2】沙漠蝎子涂装（精细版）
    scorp_x, scorp_y = cx - int(w * 0.18), cy + int(h * 0.15)
    
    # 蝎子身体
    pygame.draw.ellipse(surface, (100, 80, 50), (scorp_x - 8, scorp_y - 4, 16, 8))
    pygame.draw.ellipse(surface, (80, 60, 40), (scorp_x - 6, scorp_y + 2, 12, 6))
    
    # 蝎子尾巴（S形曲线）
    tail_pts = []
    for i in range(10):
        curve = math.sin(i * 0.4) * 6
        tx = scorp_x + 10 + i * 2.5
        ty = scorp_y - 2 - i * 1.5 - curve
        tail_pts.append((int(tx), int(ty)))
    if len(tail_pts) >= 2:
        pygame.draw.lines(surface, (90, 70, 45), False, tail_pts, 3)
    
    # 毒刺
    stinger = tail_pts[-1]
    pygame.draw.polygon(surface, eye_color, [
        (stinger[0] + 5, stinger[1] - 8),
        (stinger[0] - 2, stinger[1] + 2),
        (stinger[0] + 3, stinger[1] + 2),
    ])
    
    # 蝎钳
    for side in [-1, 1]:
        claw_x = scorp_x - 10 + side * 5
        claw_y = scorp_y - 2
        pygame.draw.ellipse(surface, (100, 80, 50), (claw_x - 6, claw_y - 3, 8, 5))
        pygame.draw.ellipse(surface, (90, 70, 45), (claw_x - 8, claw_y - 4, 5, 4))
    
    # 【独特元素3】太阳神徽（埃及风格）
    sun_x, sun_y = cx + int(w * 0.2), cy - int(h * 0.18)
    sun_r = 10
    
    # 太阳盘
    pygame.draw.circle(surface, (255, 180, 50), (sun_x, sun_y), sun_r)
    pygame.draw.circle(surface, (255, 220, 100), (sun_x, sun_y), sun_r - 3)
    
    # 光芒
    for i in range(12):
        ray_angle = t * 0.5 + i * math.pi / 6
        ray_inner = sun_r + 2
        ray_outer = sun_r + 8 + int(3 * math.sin(t * 3 + i))
        rx1 = sun_x + int(math.cos(ray_angle) * ray_inner)
        ry1 = sun_y + int(math.sin(ray_angle) * ray_inner)
        rx2 = sun_x + int(math.cos(ray_angle) * ray_outer)
        ry2 = sun_y + int(math.sin(ray_angle) * ray_outer)
        pygame.draw.line(surface, (255, 200, 80), (rx1, ry1), (rx2, ry2), 2 if i % 2 == 0 else 1)
    
    # 【独特元素4】阿拉伯几何图腾
    pattern_x, pattern_y = cx + int(w * 0.25), cy + int(h * 0.08)
    pattern_r = 12
    
    # 八角星图案
    for layer in range(2):
        star_pts = []
        for i in range(8):
            angle = i * math.pi / 4 + layer * math.pi / 8
            r = pattern_r if layer == 0 else pattern_r * 0.5
            star_pts.append((
                pattern_x + int(math.cos(angle) * r),
                pattern_y + int(math.sin(angle) * r)
            ))
        pygame.draw.polygon(surface, (*toxic, 180 - layer * 60), star_pts, 2 - layer)
    
    # 【独特元素5】干旱龟裂纹理
    crack_positions = [
        (cx - 20, cy - 10), (cx + 15, cy + 5), (cx - 5, cy + 20),
    ]
    for crack_cx, crack_cy in crack_positions:
        # 主裂纹
        for i in range(5):
            crack_angle = i * 1.25 + crack_cx * 0.01
            crack_len = int(12 + 6 * math.sin(i + crack_cy * 0.05))
            end_x = crack_cx + int(math.cos(crack_angle) * crack_len)
            end_y = crack_cy + int(math.sin(crack_angle) * crack_len)
            pygame.draw.line(surface, (100, 85, 60), (crack_cx, crack_cy), (end_x, end_y), 1)
            
            # 分支裂纹
            for j in range(2):
                branch_angle = crack_angle + (j - 0.5) * 0.8
                branch_len = crack_len * 0.5
                bx = end_x + int(math.cos(branch_angle) * branch_len)
                by = end_y + int(math.sin(branch_angle) * branch_len)
                pygame.draw.line(surface, (110, 90, 65, 150), (end_x, end_y), (bx, by), 1)
    
    # 【独特元素6】沙尘拖尾
    trail_y = cy + int(h * 0.42)
    for i in range(8):
        trail_x = cx + int(20 * math.sin(t * 2 + i * 0.8))
        trail_y_off = trail_y + i * 6
        trail_size = int(10 - i * 0.8 + 3 * math.sin(t * 3 + i))
        trail_alpha = int(100 - i * 11)
        if trail_size > 0 and trail_alpha > 0:
            pygame.draw.circle(surface, (*toxic, trail_alpha), (trail_x, trail_y_off), trail_size)


# ==================== 极地猎手涂装 ====================
def draw_arctic_goliath(surface, x, y, w, h, frame, style):
    """
    极地猎手 - 南极科考站末日幸存者（冰封死神）
    特色：极地白迷彩、深冰蓝冷冻剂、暴风雪、冰川裂隙
    独特元素：精细雪花暴风雪、北极熊爪痕、冰川碎片、极光天幕、冰晶护盾、冷冻喷雾
    """
    theme = get_goliath_theme(style)
    armor = theme["armor"]  # 雪白
    toxic = theme["toxic"]  # 冰蓝
    rust = theme["rust"]    # 冻锈
    eye_color = theme["eye"]
    glow = theme["glow"]
    
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 【独特背景1】极光天幕（动态彩色波浪）
    aurora_colors = [
        (100, 255, 180), (120, 220, 255), (180, 150, 255), 
        (100, 255, 220), (150, 200, 255),
    ]
    for layer, acolor in enumerate(aurora_colors):
        aurora_pts = []
        aurora_y = y - 10 + layer * 8
        for j in range(20):
            ax = x - 10 + j * int(w / 18)
            wave1 = 8 * math.sin(t * 1.5 + j * 0.3 + layer * 0.5)
            wave2 = 4 * math.sin(t * 2.5 + j * 0.5 + layer)
            ay = aurora_y + wave1 + wave2
            aurora_pts.append((ax, int(ay)))
        if len(aurora_pts) >= 2:
            aurora_alpha = int(50 - layer * 8)
            pygame.draw.lines(surface, (*acolor, aurora_alpha), False, aurora_pts, 3)
    
    # 【独特背景2】精细暴风雪粒子
    for i in range(35):
        # 不同大小的雪花
        snow_type = i % 4
        snow_x = cx + int((w * 0.8) * math.sin(t * 2.5 + i * 0.28))
        snow_y = y + int(h * 1.3 * ((t * 0.4 + i * 0.028) % 1))
        
        if snow_type == 0:
            # 大型雪花（六角形）
            snow_r = 4 + int(2 * math.sin(t + i))
            for j in range(6):
                flake_angle = j * math.pi / 3 + t * 0.5
                fx = snow_x + int(math.cos(flake_angle) * snow_r)
                fy = snow_y + int(math.sin(flake_angle) * snow_r)
                pygame.draw.line(surface, (255, 255, 255, 180), (snow_x, snow_y), (fx, fy), 1)
                # 分支
                for k in [-0.5, 0.5]:
                    bx = snow_x + int(math.cos(flake_angle) * snow_r * 0.6)
                    by = snow_y + int(math.sin(flake_angle) * snow_r * 0.6)
                    bbx = bx + int(math.cos(flake_angle + k) * snow_r * 0.4)
                    bby = by + int(math.sin(flake_angle + k) * snow_r * 0.4)
                    pygame.draw.line(surface, (255, 255, 255, 120), (bx, by), (bbx, bby), 1)
        else:
            # 小雪粒
            snow_size = 2 + (i % 2)
            pygame.draw.circle(surface, (255, 255, 255, 150 - i % 50), (snow_x, snow_y), snow_size)
    
    # 主体绘制
    _draw_goliath_body(surface, x, y, w, h, frame, theme)
    
    # 【独特元素1】冰川碎片装甲覆盖
    ice_shards = [
        (cx - 22, cy - 20, 18, 12, 0.3), (cx + 18, cy - 15, 15, 14, -0.2),
        (cx - 15, cy + 5, 20, 10, 0.1), (cx + 22, cy + 8, 14, 16, -0.4),
        (cx - 8, cy + 22, 16, 12, 0.2), (cx + 5, cy - 28, 12, 18, -0.1),
    ]
    for sx, sy, sw, sh, angle in ice_shards:
        # 冰块多边形
        pts = [
            (sx - sw//2, sy - sh//3),
            (sx + sw//3, sy - sh//2),
            (sx + sw//2, sy),
            (sx + sw//4, sy + sh//2),
            (sx - sw//3, sy + sh//3),
        ]
        # 旋转
        rotated_pts = []
        for px, py in pts:
            dx, dy = px - sx, py - sy
            rx = sx + dx * math.cos(angle) - dy * math.sin(angle)
            ry = sy + dx * math.sin(angle) + dy * math.cos(angle)
            rotated_pts.append((int(rx), int(ry)))
        
        pygame.draw.polygon(surface, (180, 220, 255, 120), rotated_pts)
        pygame.draw.polygon(surface, (*toxic, 180), rotated_pts, 2)
        # 冰内反光
        pygame.draw.line(surface, (255, 255, 255, 100), rotated_pts[0], rotated_pts[2], 1)
    
    # 【独特元素2】北极熊爪痕涂装
    claw_x, claw_y = cx - int(w * 0.15), cy + int(h * 0.12)
    for claw in range(4):
        claw_start_x = claw_x + claw * 8
        claw_start_y = claw_y - 10
        claw_end_x = claw_start_x + 5
        claw_end_y = claw_y + 15
        # 爪痕（渐变粗细）
        for seg in range(8):
            seg_start_y = claw_start_y + seg * 3
            seg_end_y = seg_start_y + 4
            seg_width = 3 - seg // 3
            pygame.draw.line(surface, (60, 70, 80), 
                           (claw_start_x + seg * 0.5, seg_start_y),
                           (claw_start_x + seg * 0.6, seg_end_y), seg_width)
        # 爪尖
        pygame.draw.circle(surface, (80, 90, 100), (int(claw_end_x), int(claw_end_y)), 2)
    
    # 【独特元素3】六角冰晶护盾阵列
    shield_positions = [
        (cx - int(w * 0.35), cy - int(h * 0.1)),
        (cx + int(w * 0.35), cy - int(h * 0.1)),
        (cx - int(w * 0.38), cy + int(h * 0.15)),
        (cx + int(w * 0.38), cy + int(h * 0.15)),
    ]
    for idx, (shield_x, shield_y) in enumerate(shield_positions):
        shield_size = int(12 + 4 * math.sin(t * 2 + idx))
        shield_alpha = int(150 + 50 * math.sin(t * 3 + idx * 0.5))
        
        # 多层六角形
        for layer in range(3):
            layer_size = shield_size - layer * 3
            layer_alpha = shield_alpha - layer * 40
            if layer_size > 0 and layer_alpha > 0:
                hex_pts = []
                for j in range(6):
                    ha = j * math.pi / 3 + t * 0.3 + idx * 0.2
                    hex_pts.append((
                        shield_x + int(math.cos(ha) * layer_size),
                        shield_y + int(math.sin(ha) * layer_size * 0.7)
                    ))
                pygame.draw.polygon(surface, (*toxic, layer_alpha), hex_pts, 2 - layer)
        
        # 核心发光
        pygame.draw.circle(surface, (*glow, 100), (shield_x, shield_y), 4)
    
    # 【独特元素4】冰锥武器群（精细版）
    for side in [-1, 1]:
        icicle_base_x = cx + side * int(w * 0.42)
        icicle_base_y = cy + int(h * 0.05)
        
        # 多个冰锥
        for ic in range(3):
            ic_x = icicle_base_x + side * (ic - 1) * 6
            ic_y = icicle_base_y + ic * 8
            ic_len = 25 - ic * 5
            
            # 冰锥主体
            ic_pts = [
                (ic_x - 4 + ic, ic_y),
                (ic_x + 4 - ic, ic_y),
                (ic_x + side * (2 - ic), ic_y + ic_len),
            ]
            pygame.draw.polygon(surface, (200, 230, 255), ic_pts)
            pygame.draw.polygon(surface, toxic, ic_pts, 1)
            
            # 内部纹理
            for stripe in range(3):
                sy = ic_y + 4 + stripe * int(ic_len / 4)
                sw = 4 - stripe - ic
                if sw > 0:
                    pygame.draw.line(surface, (240, 250, 255, 180), 
                                   (ic_x - sw, sy), (ic_x + sw, sy), 1)
    
    # 【独特元素5】冷冻喷雾系统
    spray_positions = [
        (cx - int(w * 0.2), cy + int(h * 0.35)),
        (cx + int(w * 0.2), cy + int(h * 0.35)),
    ]
    for spray_x, spray_y in spray_positions:
        for i in range(10):
            spray_angle = math.pi / 2 + (i - 5) * 0.15 + math.sin(t * 5 + i) * 0.1
            spray_dist = 8 + i * 4 + int(5 * math.sin(t * 4 + i * 0.5))
            sx = spray_x + int(math.cos(spray_angle) * spray_dist * 0.3)
            sy = spray_y + int(math.sin(spray_angle) * spray_dist)
            spray_size = 6 - i * 0.4
            spray_alpha = int(150 - i * 14)
            if spray_size > 0 and spray_alpha > 0:
                pygame.draw.circle(surface, (*toxic, spray_alpha), (sx, sy), int(spray_size))
    
    # 【独特元素6】霜冻结晶网络
    frost_cx, frost_cy = cx, cy
    for branch in range(6):
        branch_angle = branch * math.pi / 3 + t * 0.1
        branch_len = int(w * 0.25)
        
        # 主干
        end_x = frost_cx + int(math.cos(branch_angle) * branch_len)
        end_y = frost_cy + int(math.sin(branch_angle) * branch_len * 0.6)
        pygame.draw.line(surface, (*toxic, 60), (frost_cx, frost_cy), (end_x, end_y), 1)
        
        # 分支
        for sub in range(3):
            sub_start = 0.3 + sub * 0.25
            sub_x = frost_cx + int(math.cos(branch_angle) * branch_len * sub_start)
            sub_y = frost_cy + int(math.sin(branch_angle) * branch_len * 0.6 * sub_start)
            for side in [-1, 1]:
                sub_angle = branch_angle + side * 0.6
                sub_len = branch_len * 0.2
                sub_end_x = sub_x + int(math.cos(sub_angle) * sub_len)
                sub_end_y = sub_y + int(math.sin(sub_angle) * sub_len * 0.6)
                pygame.draw.line(surface, (*toxic, 40), (sub_x, sub_y), (sub_end_x, sub_end_y), 1)


# ==================== 坏疽腐蚀涂装 ====================
def draw_necrosis_goliath(surface, x, y, w, h, frame, style):
    """
    坏疽腐蚀 - 生化武器泄漏导致的腐烂机体（恐怖坏疽症）
    特色：腐肉黑装甲、脓液黄绿渗出、组织坏死、蛆虫蠕动
    独特元素：巨型腐烂孔洞、骨骼暴露、脓液瀑布、蛆虫集群、坏死蔓延、腐败烟雾
    """
    theme = get_goliath_theme(style)
    armor = theme["armor"]  # 腐肉黑
    toxic = theme["toxic"]  # 脓液绿
    rust = theme["rust"]    # 血锈
    eye_color = theme["eye"]  # 脓黄
    
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 【独特背景1】腐败烟雾弥漫
    for layer in range(4):
        for i in range(8):
            smoke_angle = t * 0.2 + i * 0.8 + layer * 0.3
            smoke_dist = int(w * 0.45 + w * 0.15 * math.sin(t * 0.8 + i + layer))
            smoke_x = cx + int(math.cos(smoke_angle) * smoke_dist)
            smoke_y = cy + int(math.sin(smoke_angle) * smoke_dist * 0.4) - layer * 5
            smoke_size = int(15 - layer * 3 + 5 * math.sin(t + i * 0.5))
            smoke_alpha = int(50 - layer * 10)
            
            if smoke_size > 0 and smoke_alpha > 0:
                # 多层腐败绿烟
                pygame.draw.circle(surface, (80, 100, 40, smoke_alpha), 
                                 (smoke_x, smoke_y), smoke_size)
                pygame.draw.circle(surface, (*toxic, smoke_alpha // 2), 
                                 (smoke_x, smoke_y - 3), smoke_size - 3)
    
    # 【独特背景2】苍蝇群环绕
    for i in range(15):
        fly_angle = t * 3 + i * 0.42
        fly_dist = int(w * 0.35 + 10 * math.sin(t * 5 + i * 0.7))
        fly_x = cx + int(math.cos(fly_angle) * fly_dist)
        fly_y = cy + int(math.sin(fly_angle) * fly_dist * 0.5) + int(8 * math.sin(t * 8 + i))
        
        # 苍蝇身体
        pygame.draw.circle(surface, (30, 30, 35), (fly_x, fly_y), 2)
        # 翅膀（闪烁）
        wing_phase = int(t * 20 + i * 5) % 2
        if wing_phase == 0:
            pygame.draw.ellipse(surface, (150, 150, 160, 100), 
                              (fly_x - 3, fly_y - 2, 3, 4))
            pygame.draw.ellipse(surface, (150, 150, 160, 100), 
                              (fly_x + 1, fly_y - 2, 3, 4))
    
    # 主体绘制
    _draw_goliath_body(surface, x, y, w, h, frame, theme)
    
    # 【独特元素1】巨型腐烂孔洞（带骨骼暴露）
    hole_positions = [
        (cx - 15, cy - 20, 12, True), (cx + 20, cy - 12, 10, True),
        (cx - 10, cy + 10, 14, True), (cx + 12, cy + 22, 11, False),
        (cx - 22, cy + 3, 8, False), (cx + 6, cy - 30, 9, False),
        (cx + 25, cy + 5, 7, False), (cx - 18, cy + 25, 10, True),
    ]
    for hx, hy, hr, has_bone in hole_positions:
        # 黑色深渊
        pygame.draw.circle(surface, (8, 5, 2), (hx, hy), hr)
        
        # 腐烂边缘（多层）
        for edge in range(3):
            edge_r = hr + 2 + edge * 2
            edge_color = (60 + edge * 20, 40 + edge * 15, 25 + edge * 10)
            pygame.draw.circle(surface, edge_color, (hx, hy), edge_r, 1)
        
        # 骨骼暴露
        if has_bone:
            bone_color = (220, 210, 180)
            for bone_seg in range(3):
                bone_angle = -0.3 + bone_seg * 0.3
                bx1 = hx + int(math.cos(bone_angle) * hr * 0.3)
                by1 = hy + int(math.sin(bone_angle) * hr * 0.3)
                bx2 = hx + int(math.cos(bone_angle) * hr * 1.2)
                by2 = hy + int(math.sin(bone_angle) * hr * 0.8)
                pygame.draw.line(surface, bone_color, (bx1, by1), (bx2, by2), 2)
                # 骨节
                pygame.draw.circle(surface, (200, 190, 160), (bx2, by2), 2)
        
        # 脓液渗出流
        drip_count = hr // 3 + 1
        for d in range(drip_count):
            drip_x = hx + (d - drip_count // 2) * 3
            drip_len = int(hr * 2 + 8 * math.sin(t * 2 + hx * 0.1 + d))
            for ds in range(int(drip_len / 2)):
                d_y = hy + hr + ds * 2
                d_alpha = int(200 - ds * 15)
                d_size = max(1, 3 - ds // 3)
                if d_alpha > 0:
                    pygame.draw.circle(surface, (*toxic, d_alpha), (drip_x, d_y), d_size)
    
    # 【独特元素2】坏死斑块蔓延网络
    necrosis_center = [(cx - 20, cy - 5), (cx + 18, cy + 8), (cx, cy + 25)]
    for ncx, ncy in necrosis_center:
        # 中心坏死区
        pygame.draw.circle(surface, (25, 18, 10), (ncx, ncy), 12)
        pygame.draw.circle(surface, (50, 35, 20), (ncx, ncy), 14, 2)
        
        # 坏死蔓延脉络
        for branch in range(6):
            branch_angle = branch * math.pi / 3 + t * 0.1 + ncx * 0.02
            branch_len = int(18 + 6 * math.sin(t + branch))
            
            # 主脉
            pts = [(ncx, ncy)]
            for seg in range(4):
                seg_len = branch_len * (seg + 1) / 4
                seg_x = ncx + int(math.cos(branch_angle + math.sin(seg * 0.5) * 0.3) * seg_len)
                seg_y = ncy + int(math.sin(branch_angle + math.sin(seg * 0.5) * 0.3) * seg_len * 0.7)
                pts.append((seg_x, seg_y))
            
            if len(pts) >= 2:
                pygame.draw.lines(surface, (70, 50, 30, 150), False, pts, 2)
            
            # 坏死末端
            pygame.draw.circle(surface, (40, 25, 15), pts[-1], 3)
    
    # 【独特元素3】蛆虫集群（密集蠕动）
    maggot_clusters = [
        (cx - 10, cy + 15, 8), (cx + 15, cy + 10, 6),
        (cx - 18, cy - 8, 5), (cx + 8, cy + 28, 7),
        (cx + 22, cy + 20, 6), (cx - 5, cy - 22, 4),
    ]
    for cluster_x, cluster_y, count in maggot_clusters:
        for m in range(count):
            # 每条蛆虫的位置
            mx = cluster_x + (m % 3 - 1) * 4 + int(2 * math.sin(t * 4 + m))
            my = cluster_y + (m // 3) * 3 + int(2 * math.cos(t * 3 + m * 0.7))
            
            # 蛆虫身体（6段蠕动）
            worm_pts = []
            for seg in range(6):
                wx = mx + seg * 1.5 + int(math.sin(t * 10 + seg * 0.6 + m * 0.3) * 1.5)
                wy = my + int(math.cos(t * 8 + seg * 0.4 + m * 0.5) * 1)
                worm_pts.append((int(wx), int(wy)))
            
            if len(worm_pts) >= 2:
                # 身体渐变（头粗尾细）
                for seg in range(len(worm_pts) - 1):
                    seg_width = 3 - seg // 2
                    pygame.draw.line(surface, (230, 220, 190), 
                                   worm_pts[seg], worm_pts[seg + 1], max(1, seg_width))
                
                # 头部
                pygame.draw.circle(surface, (210, 200, 170), worm_pts[-1], 2)
                # 深色口器
                pygame.draw.circle(surface, (60, 50, 40), worm_pts[-1], 1)
    
    # 【独特元素4】脓液瀑布系统
    waterfall_positions = [
        (cx - int(w * 0.2), cy - int(h * 0.1), 20),
        (cx + int(w * 0.15), cy, 25),
        (cx, cy + int(h * 0.15), 18),
    ]
    for wf_x, wf_y, wf_width in waterfall_positions:
        # 流出口
        pygame.draw.ellipse(surface, (60, 80, 40), 
                          (wf_x - wf_width // 4, wf_y - 3, wf_width // 2, 6))
        
        # 瀑布主体
        for stream in range(wf_width // 4):
            stream_x = wf_x - wf_width // 8 + stream * 2
            stream_phase = (t * 2 + stream * 0.3) % 1
            
            for drop in range(12):
                drop_y = wf_y + drop * 4 + int(stream_phase * 8)
                drop_alpha = int(180 - drop * 14)
                drop_size = 4 - drop // 4
                
                if drop_alpha > 0 and drop_size > 0:
                    wobble = int(2 * math.sin(t * 5 + drop * 0.5 + stream))
                    pygame.draw.circle(surface, (*toxic, drop_alpha), 
                                     (stream_x + wobble, drop_y), drop_size)
    
    # 【独特元素5】腐肉撕裂纹理
    for i in range(10):
        tear_x = cx - int(w * 0.35) + i * int(w * 0.07)
        tear_y_start = cy - int(h * 0.25)
        
        # 撕裂主线
        tear_pts = [(tear_x, tear_y_start)]
        for seg in range(6):
            jitter_x = int(4 * math.sin(i * 0.7 + seg * 0.8))
            jitter_y = 8 + int(4 * math.cos(i * 0.5 + seg))
            tear_pts.append((
                tear_pts[-1][0] + jitter_x,
                tear_pts[-1][1] + jitter_y
            ))
        
        pygame.draw.lines(surface, (80, 50, 35, 180), False, tear_pts, 2)
        
        # 撕裂边缘肉瓣
        for pt in tear_pts[1:-1]:
            flap_side = 1 if (i % 2 == 0) else -1
            pygame.draw.polygon(surface, (100, 70, 50, 120), [
                pt,
                (pt[0] + flap_side * 5, pt[1] + 2),
                (pt[0] + flap_side * 3, pt[1] + 6),
            ])
    
    # 【独特元素6】恶臭气体标识
    stink_x, stink_y = cx + int(w * 0.25), cy - int(h * 0.3)
    for wave in range(3):
        wave_pts = []
        wave_offset = wave * 6
        for j in range(8):
            wx = stink_x - 10 + j * 3
            wy = stink_y - wave_offset + int(3 * math.sin(t * 4 + j * 0.5 + wave))
            wave_pts.append((wx, wy))
        if len(wave_pts) >= 2:
            wave_alpha = int(120 - wave * 35)
            pygame.draw.lines(surface, (*toxic, wave_alpha), False, wave_pts, 2)


# ==================== 末日瘟神涂装 ====================
def draw_pandemic_goliath(surface, x, y, w, h, frame, style):
    """
    末日瘟神 - 终极生化恐怖，世界末日的瘟疫化身（天启灭世）
    特色：暗紫黑装甲、病毒紫光芒、冠状病毒粒子、死亡光环
    独特元素：精细冠状病毒、骷髅死神标志、末日钟面、瘟疫气旋、感染网络、死亡粒子
    """
    theme = get_goliath_theme(style)
    armor = theme["armor"]  # 暗紫黑
    toxic = theme["toxic"]  # 病毒紫
    rust = theme["rust"]
    eye_color = theme["eye"]  # 病变红
    glow = theme["glow"]
    
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 【独特背景1】死亡气旋（多层螺旋）
    for layer in range(4):
        spiral_pts = []
        for i in range(25):
            spiral_angle = t * 0.5 + i * 0.25 + layer * math.pi / 2
            spiral_r = int(w * 0.15 + i * int(w * 0.015) + layer * 5)
            sx = cx + int(math.cos(spiral_angle) * spiral_r)
            sy = cy + int(math.sin(spiral_angle) * spiral_r * 0.5)
            spiral_pts.append((sx, sy))
        if len(spiral_pts) >= 2:
            spiral_alpha = int(60 - layer * 12)
            pygame.draw.lines(surface, (*toxic, spiral_alpha), False, spiral_pts, 2)
    
    # 【独特背景2】死亡粒子云
    for i in range(30):
        particle_angle = t * 0.3 + i * 0.21
        particle_dist = int(w * 0.4 + w * 0.15 * math.sin(t * 1.5 + i * 0.5))
        px = cx + int(math.cos(particle_angle) * particle_dist)
        py = cy + int(math.sin(particle_angle) * particle_dist * 0.4)
        
        # 粒子大小脉动
        p_size = int(3 + 2 * math.sin(t * 3 + i * 0.4))
        p_alpha = int(80 + 40 * math.sin(t * 2 + i * 0.3))
        
        # 死亡紫色
        pygame.draw.circle(surface, (*toxic, p_alpha), (px, py), p_size)
        # 核心亮点
        if p_size > 2:
            pygame.draw.circle(surface, (*glow, p_alpha // 2), (px, py), p_size - 1)
    
    # 主体绘制
    _draw_goliath_body(surface, x, y, w, h, frame, theme)
    
    # 【独特元素1】精细冠状病毒粒子群
    virus_positions = [
        (cx - 38, cy - 18, 9), (cx + 42, cy - 10, 8), (cx - 28, cy + 32, 10),
        (cx + 32, cy + 28, 7), (cx, cy - 42, 8), (cx - 42, cy + 12, 6),
        (cx + 38, cy + 42, 9), (cx + 18, cy - 38, 7), (cx - 15, cy + 45, 8),
    ]
    for vx, vy, virus_r in virus_positions:
        pulse_r = virus_r + int(2 * math.sin(t * 3 + vx * 0.1))
        
        # 病毒外壳（双层）
        pygame.draw.circle(surface, (*toxic, 150), (vx, vy), pulse_r + 2, 1)
        pygame.draw.circle(surface, (*toxic, 220), (vx, vy), pulse_r)
        
        # 内部RNA螺旋
        for helix in range(2):
            helix_pts = []
            for hp in range(6):
                ha = t * 2 + hp * 0.5 + helix * math.pi
                hr = pulse_r * 0.5
                hx = vx + int(math.cos(ha) * hr * 0.6)
                hy = vy + int(math.sin(ha) * hr * 0.3)
                helix_pts.append((hx, hy))
            if len(helix_pts) >= 2:
                pygame.draw.lines(surface, (*glow, 180), False, helix_pts, 1)
        
        # 冠状突刺（精细版，带渐变）
        spike_count = 12
        for i in range(spike_count):
            spike_angle = t * 0.5 + i * 2 * math.pi / spike_count + vx * 0.05
            spike_len = pulse_r + 5 + int(2 * math.sin(t * 4 + i))
            
            # 突刺主体（渐粗）
            for seg in range(3):
                seg_start = pulse_r * 0.5 + seg * (spike_len - pulse_r * 0.5) / 3
                seg_end = pulse_r * 0.5 + (seg + 1) * (spike_len - pulse_r * 0.5) / 3
                sx1 = vx + int(math.cos(spike_angle) * seg_start)
                sy1 = vy + int(math.sin(spike_angle) * seg_start)
                sx2 = vx + int(math.cos(spike_angle) * seg_end)
                sy2 = vy + int(math.sin(spike_angle) * seg_end)
                pygame.draw.line(surface, (*toxic, 200 - seg * 40), (sx1, sy1), (sx2, sy2), 2 - seg)
            
            # 突刺末端球（三层）
            spike_tip_x = vx + int(math.cos(spike_angle) * spike_len)
            spike_tip_y = vy + int(math.sin(spike_angle) * spike_len)
            pygame.draw.circle(surface, (*glow, 200), (spike_tip_x, spike_tip_y), 3)
            pygame.draw.circle(surface, (*toxic, 255), (spike_tip_x, spike_tip_y), 2)
            pygame.draw.circle(surface, (255, 200, 255), (spike_tip_x, spike_tip_y), 1)
    
    # 【独特元素2】骷髅死神标志
    skull_x, skull_y = cx - int(w * 0.18), cy + int(h * 0.12)
    
    # 骷髅轮廓
    pygame.draw.ellipse(surface, (60, 50, 70), (skull_x - 10, skull_y - 12, 20, 24))
    pygame.draw.ellipse(surface, toxic, (skull_x - 10, skull_y - 12, 20, 24), 2)
    
    # 眼眶
    for side in [-1, 1]:
        eye_x = skull_x + side * 5
        eye_y = skull_y - 3
        pygame.draw.ellipse(surface, (15, 10, 20), (eye_x - 4, eye_y - 3, 8, 6))
        # 眼中红光
        pygame.draw.circle(surface, (*eye_color, 200), (eye_x, eye_y), 2)
    
    # 鼻孔
    pygame.draw.polygon(surface, (15, 10, 20), [
        (skull_x, skull_y + 4), (skull_x - 3, skull_y + 8), (skull_x + 3, skull_y + 8)
    ])
    
    # 牙齿
    for tooth in range(5):
        tx = skull_x - 6 + tooth * 3
        pygame.draw.rect(surface, (200, 190, 180), (tx, skull_y + 10, 2, 4))
    
    # 交叉骨头
    for bone_angle in [-0.4, 0.4]:
        bone_x1 = skull_x + int(math.cos(bone_angle + math.pi) * 18)
        bone_y1 = skull_y + 12 + int(math.sin(bone_angle + math.pi) * 10)
        bone_x2 = skull_x + int(math.cos(bone_angle) * 18)
        bone_y2 = skull_y + 12 + int(math.sin(bone_angle) * 10)
        pygame.draw.line(surface, (200, 190, 180), (bone_x1, bone_y1), (bone_x2, bone_y2), 3)
        # 骨头末端球
        for bx, by in [(bone_x1, bone_y1), (bone_x2, bone_y2)]:
            pygame.draw.circle(surface, (220, 210, 200), (bx, by), 3)
    
    # 【独特元素3】末日钟面（精细版）
    clock_x, clock_y = cx + int(w * 0.2), cy - int(h * 0.22)
    clock_r = 14
    
    # 钟面底盘
    pygame.draw.circle(surface, (25, 20, 35), (clock_x, clock_y), clock_r + 3)
    pygame.draw.circle(surface, toxic, (clock_x, clock_y), clock_r + 3, 2)
    pygame.draw.circle(surface, (40, 35, 55), (clock_x, clock_y), clock_r)
    
    # 刻度（12个）
    for i in range(12):
        mark_angle = i * math.pi / 6 - math.pi / 2
        m_inner = clock_r - 3
        m_outer = clock_r - 1
        mx1 = clock_x + int(math.cos(mark_angle) * m_inner)
        my1 = clock_y + int(math.sin(mark_angle) * m_inner)
        mx2 = clock_x + int(math.cos(mark_angle) * m_outer)
        my2 = clock_y + int(math.sin(mark_angle) * m_outer)
        pygame.draw.line(surface, (*glow, 200), (mx1, my1), (mx2, my2), 1 if i % 3 else 2)
    
    # 时针（接近12点 - 末日）
    hour_angle = -math.pi / 2 + 0.05 * math.sin(t)  # 微微颤抖
    hx = clock_x + int(math.cos(hour_angle) * (clock_r - 5))
    hy = clock_y + int(math.sin(hour_angle) * (clock_r - 5))
    pygame.draw.line(surface, (*eye_color, 255), (clock_x, clock_y), (hx, hy), 2)
    
    # 分针
    minute_angle = -math.pi / 2 + 0.1 + 0.03 * math.sin(t * 2)
    minx = clock_x + int(math.cos(minute_angle) * (clock_r - 3))
    miny = clock_y + int(math.sin(minute_angle) * (clock_r - 3))
    pygame.draw.line(surface, (*eye_color, 200), (clock_x, clock_y), (minx, miny), 1)
    
    # 中心点
    pygame.draw.circle(surface, glow, (clock_x, clock_y), 2)
    
    # 【独特元素4】感染蔓延网络（精细版）
    for branch in range(8):
        spread_angle = t * 0.2 + branch * math.pi / 4
        
        # 主干
        main_pts = [(cx, cy)]
        for seg in range(6):
            seg_len = 8 + seg * 6
            seg_wobble = 0.2 * math.sin(t * 2 + seg * 0.4 + branch)
            next_x = main_pts[-1][0] + int(math.cos(spread_angle + seg_wobble) * seg_len)
            next_y = main_pts[-1][1] + int(math.sin(spread_angle + seg_wobble) * seg_len * 0.5)
            main_pts.append((next_x, next_y))
        
        # 绘制主干（渐变透明）
        for j in range(len(main_pts) - 1):
            seg_alpha = int(180 * (1 - j / len(main_pts)))
            seg_width = 3 - j // 2
            if seg_width > 0:
                pygame.draw.line(surface, (*toxic, seg_alpha), main_pts[j], main_pts[j+1], seg_width)
        
        # 分支
        for j, pt in enumerate(main_pts[2:-1], 2):
            for side in [-1, 1]:
                sub_angle = spread_angle + side * 0.7
                sub_len = 12 - j * 2
                if sub_len > 3:
                    sub_x = pt[0] + int(math.cos(sub_angle) * sub_len)
                    sub_y = pt[1] + int(math.sin(sub_angle) * sub_len * 0.5)
                    sub_alpha = int(120 * (1 - j / len(main_pts)))
                    pygame.draw.line(surface, (*toxic, sub_alpha), pt, (sub_x, sub_y), 1)
                    # 末端感染点
                    pygame.draw.circle(surface, (*glow, sub_alpha), (sub_x, sub_y), 2)
    
    # 【独特元素5】瘟疫能量脉冲波
    for wave in range(3):
        pulse_phase = (t * 1.5 + wave * 0.7) % (2 * math.pi)
        pulse_r = int(w * 0.1 + w * 0.25 * (pulse_phase / (2 * math.pi)))
        pulse_alpha = int(150 * (1 - pulse_phase / (2 * math.pi)))
        
        if pulse_alpha > 10:
            pygame.draw.circle(surface, (*glow, pulse_alpha), (cx, cy), pulse_r, 2)
    
    # 【独特元素6】警告文字区域
    warning_x, warning_y = cx, cy + int(h * 0.38)
    warning_width = int(w * 0.5)
    
    # 警告条背景
    pygame.draw.rect(surface, (40, 20, 50), 
                    (warning_x - warning_width // 2, warning_y - 6, warning_width, 12))
    pygame.draw.rect(surface, toxic, 
                    (warning_x - warning_width // 2, warning_y - 6, warning_width, 12), 1)
    
    # 滚动的警告条纹
    stripe_offset = int((t * 20) % 10)
    for stripe in range(warning_width // 10 + 2):
        sx = warning_x - warning_width // 2 + stripe * 10 - stripe_offset
        if warning_x - warning_width // 2 <= sx < warning_x + warning_width // 2:
            pygame.draw.line(surface, (*eye_color, 180), 
                           (sx, warning_y - 5), (sx + 5, warning_y + 5), 2)


# ==================== 孢子母巢涂装 ====================
def draw_spore_goliath(surface, x, y, w, h, frame, style):
    """
    孢子母巢 - 真菌寄生的生物兵器（虫族母舰）
    特色：菌绿装甲、孢子黄喷发、蘑菇生长、菌丝网络
    独特元素：精细蘑菇群落、多层菌丝网、孢子瀑布、发光菌盖、真菌脉络、污染光环
    """
    theme = get_goliath_theme(style)
    armor = theme["armor"]  # 菌绿
    toxic = theme["toxic"]  # 孢子黄
    rust = theme["rust"]    # 菌锈
    eye_color = theme["eye"]  # 孢子眼
    glow = theme["glow"]
    
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 【独特背景1】孢子瀑布（大量上升孢子）
    for layer in range(3):
        for i in range(15):
            spore_base_x = cx - int(w * 0.4) + i * int(w * 0.055)
            spore_phase = (t * 0.5 + i * 0.08 + layer * 0.15) % 1
            spore_y = cy + int(h * 0.5) - int(h * 1.2 * spore_phase)
            spore_x = spore_base_x + int(8 * math.sin(t * 2 + i * 0.5 + layer))
            
            spore_size = int(3 + layer + 2 * math.sin(t * 3 + i * 0.4))
            spore_alpha = int(150 - layer * 40 - spore_phase * 80)
            
            if spore_alpha > 0:
                pygame.draw.circle(surface, (*toxic, spore_alpha), (spore_x, spore_y), spore_size)
                # 孢子尾迹
                if layer == 0:
                    tail_len = int(8 * spore_phase)
                    pygame.draw.line(surface, (*toxic, spore_alpha // 2), 
                                   (spore_x, spore_y), (spore_x, spore_y + tail_len), 1)
    
    # 【独特背景2】真菌烟雾氛围
    for i in range(10):
        fog_angle = t * 0.15 + i * 0.63
        fog_dist = int(w * 0.5 + w * 0.1 * math.sin(t * 0.5 + i))
        fog_x = cx + int(math.cos(fog_angle) * fog_dist)
        fog_y = cy + int(math.sin(fog_angle) * fog_dist * 0.4)
        fog_size = int(20 + 10 * math.sin(t * 0.8 + i * 0.3))
        fog_alpha = int(40 + 20 * math.sin(t + i * 0.2))
        pygame.draw.circle(surface, (*armor, fog_alpha), (fog_x, fog_y), fog_size)
    
    # 主体绘制
    _draw_goliath_body(surface, x, y, w, h, frame, theme)
    
    # 【独特元素1】精细蘑菇群落（多种类型）
    mushroom_data = [
        # (x, y, type, size)  type: 0=普通蘑菇, 1=毒蘑菇, 2=发光菌, 3=灵芝
        (cx - 22, cy - 18, 0, 1.2), (cx + 18, cy - 12, 1, 1.0),
        (cx - 12, cy + 8, 2, 1.3), (cx + 25, cy + 10, 0, 0.9),
        (cx - 8, cy + 25, 1, 1.1), (cx + 10, cy - 28, 2, 0.8),
        (cx - 28, cy + 2, 3, 1.0), (cx + 30, cy - 5, 3, 0.9),
        (cx, cy + 32, 0, 1.4), (cx - 18, cy + 18, 2, 1.0),
    ]
    for mx, my, mtype, mscale in mushroom_data:
        stem_h = int(10 * mscale)
        cap_w = int(14 * mscale)
        
        if mtype == 0:  # 普通蘑菇
            # 茎
            pygame.draw.rect(surface, (130, 120, 90), (mx - 2, my, 4, stem_h))
            # 帽
            pygame.draw.ellipse(surface, toxic, (mx - cap_w//2, my - cap_w//3, cap_w, int(cap_w * 0.5)))
            # 斑点
            for spot in range(4):
                sx = mx - cap_w//3 + spot * int(cap_w/4)
                sy = my - int(cap_w * 0.12)
                pygame.draw.circle(surface, (255, 255, 220), (sx, sy), int(2 * mscale))
            # 菌褶
            for fold in range(6):
                fx = mx - cap_w//3 + fold * int(cap_w/5)
                pygame.draw.line(surface, (100, 90, 60), (fx, my), (fx, my + 3), 1)
                
        elif mtype == 1:  # 毒蘑菇（红帽白点）
            pygame.draw.rect(surface, (200, 190, 170), (mx - 2, my, 4, stem_h))
            pygame.draw.ellipse(surface, (200, 50, 60), (mx - cap_w//2, my - cap_w//3, cap_w, int(cap_w * 0.5)))
            for spot in range(5):
                sx = mx - cap_w//3 + int(spot * cap_w/5)
                sy = my - int(cap_w * 0.15) + (spot % 2) * 3
                pygame.draw.circle(surface, (255, 255, 255), (sx, sy), int(2 * mscale))
                
        elif mtype == 2:  # 发光菌
            pygame.draw.rect(surface, (80, 100, 70), (mx - 2, my, 4, stem_h))
            # 发光光环
            glow_pulse = int(4 * mscale * (1 + 0.3 * math.sin(t * 3 + mx * 0.1)))
            pygame.draw.circle(surface, (*glow, 80), (mx, my - int(cap_w * 0.15)), cap_w // 2 + glow_pulse)
            pygame.draw.ellipse(surface, glow, (mx - cap_w//2, my - cap_w//3, cap_w, int(cap_w * 0.5)))
            
        elif mtype == 3:  # 灵芝（扇形）
            pygame.draw.rect(surface, (100, 60, 40), (mx - 1, my, 3, stem_h))
            # 扇形帽
            fan_pts = [(mx, my)]
            for fa in range(7):
                fan_angle = -math.pi * 0.7 + fa * math.pi * 0.23
                fan_r = cap_w * 0.6
                fan_pts.append((
                    mx + int(math.cos(fan_angle) * fan_r),
                    my - int(math.sin(fan_angle) * fan_r * 0.5)
                ))
            pygame.draw.polygon(surface, (150, 80, 50), fan_pts)
            pygame.draw.polygon(surface, (180, 100, 60), fan_pts, 1)
            # 年轮纹
            for ring in range(3):
                ring_r = cap_w * 0.2 * (ring + 1)
                pygame.draw.arc(surface, (120, 60, 35), 
                              (mx - int(ring_r), my - int(ring_r * 0.4), int(ring_r * 2), int(ring_r * 0.8)),
                              math.pi * 0.2, math.pi * 0.8, 1)
    
    # 【独特元素2】多层菌丝网络
    mycelium_layers = [
        [(cx - 28, cy + 18), (cx + 30, cy + 15), (cx - 18, cy - 22), (cx + 20, cy - 20), (cx, cy + 30)],
        [(cx - 35, cy - 5), (cx + 35, cy + 5), (cx - 10, cy + 35), (cx + 15, cy - 32)],
    ]
    for layer_idx, layer in enumerate(mycelium_layers):
        layer_alpha = 120 - layer_idx * 40
        # 连接菌丝
        for i, node1 in enumerate(layer):
            for j, node2 in enumerate(layer):
                if i < j:
                    dist = abs(node1[0] - node2[0]) + abs(node1[1] - node2[1])
                    if dist < 80:
                        # 贝塞尔曲线菌丝
                        ctrl_x = (node1[0] + node2[0]) // 2 + int(15 * math.sin(t * 0.8 + i + j))
                        ctrl_y = (node1[1] + node2[1]) // 2 + int(10 * math.cos(t * 0.6 + i * j * 0.1))
                        
                        pts = []
                        for seg in range(8):
                            st = seg / 7
                            px = int((1-st)**2 * node1[0] + 2*(1-st)*st * ctrl_x + st**2 * node2[0])
                            py = int((1-st)**2 * node1[1] + 2*(1-st)*st * ctrl_y + st**2 * node2[1])
                            pts.append((px, py))
                        if len(pts) >= 2:
                            pygame.draw.lines(surface, (*armor, layer_alpha), False, pts, 1)
            
            # 节点（菌核）
            node_pulse = int(4 + 2 * math.sin(t * 2.5 + i + layer_idx))
            pygame.draw.circle(surface, (*glow, 150), node1, node_pulse)
            pygame.draw.circle(surface, toxic, node1, node_pulse - 2)
    
    # 【独特元素3】孢子爆发系统（周期性）
    for burst_idx in range(3):
        burst_x = cx - int(w * 0.2) + burst_idx * int(w * 0.2)
        burst_y = cy + int(h * 0.25)
        burst_phase = (t * 1.2 + burst_idx * 0.7) % (2 * math.pi)
        
        if burst_phase < math.pi:  # 爆发期
            burst_intensity = math.sin(burst_phase)
            
            # 爆发中心光晕
            pygame.draw.circle(surface, (*glow, int(100 * burst_intensity)), 
                             (burst_x, burst_y), int(8 * burst_intensity))
            
            # 放射孢子
            for i in range(16):
                spore_angle = i * math.pi / 8 + t * 0.5
                spore_dist = int(25 * burst_intensity)
                spore_x = burst_x + int(math.cos(spore_angle) * spore_dist)
                spore_y = burst_y + int(math.sin(spore_angle) * spore_dist * 0.6)
                spore_size = int(4 * burst_intensity)
                if spore_size > 0:
                    pygame.draw.circle(surface, (*toxic, int(220 * burst_intensity)), 
                                     (spore_x, spore_y), spore_size)
    
    # 【独特元素4】真菌脉络纹理
    for vein_idx in range(8):
        vein_start_x = cx - int(w * 0.35) + vein_idx * int(w * 0.1)
        vein_start_y = cy - int(h * 0.3)
        
        vein_pts = [(vein_start_x, vein_start_y)]
        for seg in range(7):
            next_x = vein_pts[-1][0] + int(6 * math.sin(vein_idx * 0.8 + seg * 0.6))
            next_y = vein_pts[-1][1] + 10 + int(3 * math.cos(vein_idx * 0.5 + seg))
            vein_pts.append((next_x, next_y))
        
        # 主脉
        if len(vein_pts) >= 2:
            pygame.draw.lines(surface, (*armor, 100), False, vein_pts, 2)
        
        # 分支
        for seg_idx, pt in enumerate(vein_pts[1:-1], 1):
            if seg_idx % 2 == 0:
                for side in [-1, 1]:
                    branch_angle = math.pi / 2 + side * 0.6
                    branch_len = 8
                    branch_x = pt[0] + int(math.cos(branch_angle) * branch_len) * side
                    branch_y = pt[1] + int(math.sin(branch_angle) * branch_len * 0.5)
                    pygame.draw.line(surface, (*armor, 70), pt, (branch_x, branch_y), 1)
    
    # 【独特元素5】真菌污染区域（脉动光环）
    for ring in range(4):
        ring_phase = t * 0.8 + ring * 0.5
        ring_r = int(w * 0.25 + w * 0.15 * math.sin(ring_phase) + ring * 12)
        ring_alpha = int(50 - ring * 12)
        if ring_r > 0 and ring_alpha > 0:
            pygame.draw.circle(surface, (*toxic, ring_alpha), (cx, cy), ring_r, 2)
    
    # 【独特元素6】孢子囊挂载
    for side in [-1, 1]:
        sac_x = cx + side * int(w * 0.4)
        sac_y = cy + int(h * 0.1)
        sac_w, sac_h = 12, 18
        
        # 孢子囊主体
        pygame.draw.ellipse(surface, (*armor, 200), 
                          (sac_x - sac_w//2, sac_y - sac_h//2, sac_w, sac_h))
        pygame.draw.ellipse(surface, toxic, 
                          (sac_x - sac_w//2, sac_y - sac_h//2, sac_w, sac_h), 2)
        
        # 内部孢子可见
        for inner in range(4):
            inner_x = sac_x + (inner % 2 - 0.5) * 4
            inner_y = sac_y + (inner // 2 - 0.5) * 5
            inner_pulse = int(2 + math.sin(t * 4 + inner + side) * 1)
            pygame.draw.circle(surface, (*glow, 180), (int(inner_x), int(inner_y)), inner_pulse)
        
        # 连接茎
        pygame.draw.line(surface, armor, (sac_x, sac_y + sac_h // 2), 
                        (sac_x - side * 5, sac_y + sac_h // 2 + 8), 2)


# ==================== 化工泄漏涂装 ====================
def draw_chemical_goliath(surface, x, y, w, h, frame, style):
    """
    化工泄漏 - 化学工厂事故后的污染机体（切尔诺贝利之兽）
    特色：工业灰装甲、化学青液体、分子结构、腐蚀痕迹
    独特元素：多分子结构、GHS警告组、深度腐蚀坑、烧瓶试管组、化学管道、酸雾系统
    """
    theme = get_goliath_theme(style)
    armor = theme["armor"]  # 工业灰
    toxic = theme["toxic"]  # 化学青
    rust = theme["rust"]    # 化锈
    eye_color = theme["eye"]
    glow = theme["glow"]
    
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 【独特背景1】酸雾弥漫层
    for layer in range(3):
        for i in range(12):
            fog_angle = t * 0.2 + i * 0.52 + layer * 0.3
            fog_dist = int(w * 0.45 + w * 0.1 * math.sin(t * 0.6 + i + layer))
            fog_x = cx + int(math.cos(fog_angle) * fog_dist)
            fog_y = cy + int(math.sin(fog_angle) * fog_dist * 0.4) - layer * 10
            fog_size = int(18 - layer * 4 + 6 * math.sin(t * 0.8 + i * 0.3))
            fog_alpha = int(60 - layer * 15)
            if fog_size > 0 and fog_alpha > 0:
                pygame.draw.circle(surface, (*toxic, fog_alpha), (fog_x, fog_y), fog_size)
    
    # 【独特背景2】化学蒸汽上升
    for i in range(18):
        vapor_x = cx + int((w * 0.5) * math.sin(t * 0.6 + i * 0.35))
        vapor_phase = (t * 0.4 + i * 0.056) % 1
        vapor_y = cy + int(h * 0.4) - int(h * 0.8 * vapor_phase)
        vapor_size = int(5 + 4 * math.sin(t + i * 0.3) + vapor_phase * 3)
        vapor_alpha = int(100 * (1 - vapor_phase))
        if vapor_alpha > 0:
            pygame.draw.circle(surface, (*toxic, vapor_alpha), (vapor_x, vapor_y), vapor_size)
    
    # 主体绘制
    _draw_goliath_body(surface, x, y, w, h, frame, theme)
    
    # 【独特元素1】多分子结构标志
    # 苯环
    benzene_cx, benzene_cy = cx - int(w * 0.22), cy + int(h * 0.12)
    benzene_r = int(w * 0.07)
    benzene_pts = []
    for i in range(6):
        angle = i * math.pi / 3 - math.pi / 6 + t * 0.1
        benzene_pts.append((
            benzene_cx + int(math.cos(angle) * benzene_r),
            benzene_cy + int(math.sin(angle) * benzene_r)
        ))
    pygame.draw.polygon(surface, (*toxic, 220), benzene_pts, 2)
    # 苯环内圈
    pygame.draw.circle(surface, (*toxic, 150), (benzene_cx, benzene_cy), benzene_r - 4, 1)
    # 碳原子标记
    for pt in benzene_pts:
        pygame.draw.circle(surface, glow, pt, 2)
    
    # 水分子 H2O
    water_cx, water_cy = cx + int(w * 0.05), cy - int(h * 0.25)
    # 氧原子
    pygame.draw.circle(surface, (255, 100, 100), (water_cx, water_cy), 6)
    # 氢原子
    for side in [-1, 1]:
        h_angle = side * 0.9 + math.pi / 2
        hx = water_cx + int(math.cos(h_angle) * 10)
        hy = water_cy + int(math.sin(h_angle) * 8)
        pygame.draw.circle(surface, (200, 200, 255), (hx, hy), 4)
        pygame.draw.line(surface, (150, 150, 200), (water_cx, water_cy), (hx, hy), 2)
    
    # 甲烷 CH4 (四面体)
    methane_cx, methane_cy = cx + int(w * 0.22), cy + int(h * 0.15)
    pygame.draw.circle(surface, (80, 80, 80), (methane_cx, methane_cy), 5)  # 碳
    for i in range(4):
        h_angle = t * 0.2 + i * math.pi / 2
        h_dist = 9
        hx = methane_cx + int(math.cos(h_angle) * h_dist)
        hy = methane_cy + int(math.sin(h_angle) * h_dist * 0.7)
        pygame.draw.circle(surface, (200, 200, 255), (hx, hy), 3)
        pygame.draw.line(surface, (150, 150, 180), (methane_cx, methane_cy), (hx, hy), 1)
    
    # 【独特元素2】GHS警告标志组
    ghs_positions = [
        (cx - int(w * 0.08), cy - int(h * 0.22), "skull"),     # 骷髅
        (cx + int(w * 0.15), cy - int(h * 0.18), "flame"),     # 火焰
        (cx + int(w * 0.28), cy - int(h * 0.08), "corrosive"), # 腐蚀
    ]
    for ghs_x, ghs_y, ghs_type in ghs_positions:
        # 菱形框
        warn_size = 10
        warn_pts = [
            (ghs_x, ghs_y - warn_size),
            (ghs_x + warn_size, ghs_y),
            (ghs_x, ghs_y + warn_size),
            (ghs_x - warn_size, ghs_y),
        ]
        pygame.draw.polygon(surface, (255, 255, 255), warn_pts)
        pygame.draw.polygon(surface, (255, 0, 0), warn_pts, 2)
        
        if ghs_type == "skull":
            pygame.draw.circle(surface, (30, 30, 30), (ghs_x, ghs_y - 2), 4)
            pygame.draw.line(surface, (30, 30, 30), (ghs_x, ghs_y + 2), (ghs_x, ghs_y + 6), 2)
            pygame.draw.line(surface, (30, 30, 30), (ghs_x - 4, ghs_y + 4), (ghs_x + 4, ghs_y + 4), 1)
        elif ghs_type == "flame":
            flame_pts = [(ghs_x, ghs_y - 5), (ghs_x + 4, ghs_y + 4), (ghs_x, ghs_y + 2), (ghs_x - 4, ghs_y + 4)]
            pygame.draw.polygon(surface, (255, 100, 0), flame_pts)
        elif ghs_type == "corrosive":
            # 腐蚀液滴
            pygame.draw.polygon(surface, (30, 30, 30), [
                (ghs_x, ghs_y - 4), (ghs_x + 3, ghs_y + 3), (ghs_x - 3, ghs_y + 3)
            ])
            pygame.draw.rect(surface, (30, 30, 30), (ghs_x - 4, ghs_y + 4, 8, 2))
    
    # 【独特元素3】深度腐蚀坑系统
    corrosion_data = [
        (cx - 18, cy - 10, 12, 3), (cx + 20, cy + 8, 10, 2),
        (cx - 10, cy + 20, 14, 4), (cx + 12, cy - 22, 9, 2),
        (cx - 25, cy + 12, 11, 3), (cx + 28, cy - 5, 8, 2),
        (cx, cy + 28, 10, 3),
    ]
    for corr_x, corr_y, corr_r, depth in corrosion_data:
        # 多层腐蚀坑
        for layer in range(depth):
            layer_r = corr_r - layer * 2
            if layer_r > 0:
                layer_color = (50 - layer * 12, 55 - layer * 12, 60 - layer * 12)
                pygame.draw.circle(surface, layer_color, (corr_x, corr_y + layer), layer_r)
        
        # 坑边腐蚀纹理
        for edge in range(8):
            edge_angle = edge * math.pi / 4 + t * 0.2
            edge_len = corr_r + 3 + int(2 * math.sin(t + edge))
            ex = corr_x + int(math.cos(edge_angle) * edge_len)
            ey = corr_y + int(math.sin(edge_angle) * edge_len)
            pygame.draw.line(surface, rust, (corr_x, corr_y), (ex, ey), 1)
        
        # 酸液池
        acid_r = corr_r - depth - 1
        if acid_r > 0:
            pygame.draw.circle(surface, (*toxic, 200), (corr_x, corr_y + depth), acid_r)
            # 气泡群
            for bubble in range(3):
                bx = corr_x + int((acid_r * 0.5) * math.sin(t * 6 + bubble * 2 + corr_x))
                by = corr_y + depth - int(3 * abs(math.sin(t * 4 + bubble + corr_y)))
                pygame.draw.circle(surface, (*glow, 220), (bx, by), 2)
    
    # 【独特元素4】化学容器阵列
    for idx, side in enumerate([-1, 1]):
        # 烧瓶
        flask_x = cx + side * int(w * 0.35)
        flask_y = cy - int(h * 0.05)
        
        # 瓶身（锥形）
        flask_pts = [
            (flask_x - 8, flask_y + 20),
            (flask_x + 8, flask_y + 20),
            (flask_x + 3, flask_y),
            (flask_x - 3, flask_y),
        ]
        pygame.draw.polygon(surface, (180, 200, 210, 150), flask_pts)
        pygame.draw.polygon(surface, (220, 230, 240), flask_pts, 1)
        
        # 瓶颈
        pygame.draw.rect(surface, (180, 200, 210), (flask_x - 2, flask_y - 8, 4, 8))
        pygame.draw.rect(surface, (220, 230, 240), (flask_x - 2, flask_y - 8, 4, 8), 1)
        
        # 内部液体（不同颜色）
        liquid_colors = [(0, 255, 200), (255, 150, 0)] if idx == 0 else [(200, 0, 255), (0, 200, 100)]
        liquid_color = liquid_colors[int(t) % 2]
        liquid_h = int(15 + 3 * math.sin(t * 2 + side))
        liquid_pts = [
            (flask_x - 6, flask_y + 18),
            (flask_x + 6, flask_y + 18),
            (flask_x + int(3 * liquid_h / 15), flask_y + 20 - liquid_h),
            (flask_x - int(3 * liquid_h / 15), flask_y + 20 - liquid_h),
        ]
        pygame.draw.polygon(surface, (*liquid_color, 180), liquid_pts)
        
        # 气泡
        for b in range(3):
            bub_x = flask_x + int(4 * math.sin(t * 5 + b * 2))
            bub_y = flask_y + 15 - b * 5 - int(3 * ((t * 0.5 + b * 0.2) % 1))
            pygame.draw.circle(surface, (255, 255, 255, 150), (bub_x, bub_y), 2)
    
    # 【独特元素5】化学管道网络
    pipe_nodes = [
        (cx - int(w * 0.3), cy - int(h * 0.15)),
        (cx - int(w * 0.1), cy - int(h * 0.1)),
        (cx + int(w * 0.1), cy),
        (cx + int(w * 0.25), cy + int(h * 0.1)),
    ]
    for i in range(len(pipe_nodes) - 1):
        # 管道
        pygame.draw.line(surface, armor, pipe_nodes[i], pipe_nodes[i + 1], 4)
        pygame.draw.line(surface, (armor[0] + 30, armor[1] + 30, armor[2] + 30), 
                        pipe_nodes[i], pipe_nodes[i + 1], 2)
        # 管道接头
        pygame.draw.circle(surface, rust, pipe_nodes[i], 5)
        pygame.draw.circle(surface, (armor[0] + 20, armor[1] + 20, armor[2] + 20), pipe_nodes[i], 3)
    pygame.draw.circle(surface, rust, pipe_nodes[-1], 5)
    
    # 管道内流动指示
    flow_pos = (t * 0.5) % 1
    flow_idx = int(flow_pos * (len(pipe_nodes) - 1))
    if flow_idx < len(pipe_nodes) - 1:
        sub_pos = (flow_pos * (len(pipe_nodes) - 1)) % 1
        fx = int(pipe_nodes[flow_idx][0] + (pipe_nodes[flow_idx + 1][0] - pipe_nodes[flow_idx][0]) * sub_pos)
        fy = int(pipe_nodes[flow_idx][1] + (pipe_nodes[flow_idx + 1][1] - pipe_nodes[flow_idx][1]) * sub_pos)
        pygame.draw.circle(surface, glow, (fx, fy), 4)
    
    # 【独特元素6】化学反应区域
    reaction_x, reaction_y = cx, cy + int(h * 0.35)
    
    # 反应基座
    pygame.draw.ellipse(surface, armor, (reaction_x - 20, reaction_y - 5, 40, 10))
    
    # 反应火花
    for spark in range(8):
        spark_angle = t * 3 + spark * math.pi / 4
        spark_dist = int(15 + 8 * math.sin(t * 5 + spark))
        spark_x = reaction_x + int(math.cos(spark_angle) * spark_dist)
        spark_y = reaction_y - 10 + int(math.sin(spark_angle) * spark_dist * 0.4)
        spark_color = (255, 200 + int(55 * math.sin(t * 8 + spark)), 100)
        pygame.draw.circle(surface, spark_color, (spark_x, spark_y), 2)


# ==================== 炼油厂魔涂装 ====================
def draw_refinery_goliath(surface, x, y, w, h, frame, style):
    """
    炼油厂魔 - 石油工业的黑色恶魔（德州石油巨兽）
    特色：油污黑装甲、燃油橙火焰、浓烟滚滚、工业管道
    独特元素：精细火焰系统、多层烟柱、工业管网、油井塔架、油污纹理、热浪折射
    """
    theme = get_goliath_theme(style)
    armor = theme["armor"]  # 油污黑
    toxic = theme["toxic"]  # 燃油橙
    rust = theme["rust"]    # 油锈
    eye_color = theme["eye"]
    smoke = theme["smoke"]
    glow = theme["glow"]
    
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 【独特背景1】多层烟柱系统
    smoke_stacks = [
        (cx - int(w * 0.3), 5, (40, 35, 30)),
        (cx, 7, (50, 45, 40)),
        (cx + int(w * 0.3), 4, (35, 30, 25)),
    ]
    for col_x, density, s_color in smoke_stacks:
        for layer in range(3):
            for i in range(density + layer * 2):
                smoke_phase = (t * 0.25 + i * 0.06 + layer * 0.1) % 1
                smoke_y = cy - int(h * 0.25) - int(h * 0.8 * smoke_phase)
                smoke_x = col_x + int(15 * math.sin(t * 1.5 + i * 0.4 + layer))
                smoke_size = int(10 + i * 2 + layer * 3 + smoke_phase * 10 + 4 * math.sin(t + i))
                smoke_alpha = int((200 - layer * 50) * (1 - smoke_phase))
                if smoke_alpha > 0:
                    pygame.draw.circle(surface, (*s_color, smoke_alpha), (smoke_x, smoke_y), smoke_size)
    
    # 【独特背景2】热浪扭曲层
    for layer in range(4):
        heat_pts = []
        heat_y_base = cy - int(h * 0.4) - layer * 12
        for j in range(20):
            hx = cx - int(w * 0.5) + j * int(w * 0.053)
            hy = heat_y_base + int(5 * math.sin(t * 6 + j * 0.4 + layer * 0.7))
            heat_pts.append((hx, hy))
        if len(heat_pts) >= 2:
            heat_alpha = int(50 - layer * 10)
            if heat_alpha > 0:
                pygame.draw.lines(surface, (*toxic, heat_alpha), False, heat_pts, 1)
    
    # 主体绘制
    _draw_goliath_body(surface, x, y, w, h, frame, theme)
    
    # 【独特元素1】精细火焰喷射系统
    flame_positions = [
        (cx - int(w * 0.18), cy + int(h * 0.32), 1.2),
        (cx + int(w * 0.18), cy + int(h * 0.32), 1.2),
        (cx, cy + int(h * 0.38), 1.5),
    ]
    for fx, fy, f_scale in flame_positions:
        # 多层火焰（7层渐变）
        for layer in range(7):
            flame_h = int((30 - layer * 4) * f_scale + 10 * math.sin(t * 12 + layer * 0.5))
            flame_w = int((14 - layer * 2) * f_scale)
            
            # 颜色渐变：暗红->红->橙->黄->白
            if layer < 2:
                flame_color = (180, 40, 0)
            elif layer < 3:
                flame_color = (255, 80, 0)
            elif layer < 5:
                flame_color = toxic
            elif layer < 6:
                flame_color = (255, 220, 80)
            else:
                flame_color = (255, 255, 200)
            
            # 火焰形状
            wobble = int(4 * math.sin(t * 15 + layer * 0.8))
            flame_pts = [
                (fx - flame_w, fy),
                (fx + flame_w, fy),
                (fx + flame_w * 0.3 + wobble, fy + flame_h * 0.6),
                (fx + wobble * 0.5, fy + flame_h),
                (fx - flame_w * 0.3 + wobble, fy + flame_h * 0.6),
            ]
            pygame.draw.polygon(surface, flame_color, flame_pts)
        
        # 火星飞溅
        for spark in range(6):
            spark_angle = math.pi / 2 + (spark - 3) * 0.3 + math.sin(t * 4 + spark) * 0.2
            spark_dist = int(25 * f_scale + 10 * math.sin(t * 8 + spark * 2))
            sx = fx + int(math.cos(spark_angle) * spark_dist * 0.5)
            sy = fy + int(math.sin(spark_angle) * spark_dist)
            spark_size = int(3 - abs(spark - 2.5))
            pygame.draw.circle(surface, (255, 200 + int(55 * math.sin(t * 10 + spark)), 50), 
                             (sx, sy), max(1, spark_size))
    
    # 【独特元素2】工业管道网络
    pipe_system = [
        # 主管道
        ((cx - int(w * 0.4), cy - int(h * 0.2)), (cx - int(w * 0.4), cy + int(h * 0.25)), 7),
        ((cx + int(w * 0.4), cy - int(h * 0.2)), (cx + int(w * 0.4), cy + int(h * 0.25)), 7),
        # 横管
        ((cx - int(w * 0.4), cy - int(h * 0.1)), (cx - int(w * 0.15), cy - int(h * 0.05)), 5),
        ((cx + int(w * 0.4), cy - int(h * 0.1)), (cx + int(w * 0.15), cy - int(h * 0.05)), 5),
        ((cx - int(w * 0.15), cy + int(h * 0.1)), (cx + int(w * 0.15), cy + int(h * 0.1)), 4),
    ]
    for (x1, y1), (x2, y2), width in pipe_system:
        # 管道阴影
        pygame.draw.line(surface, (25, 22, 18), (x1 + 2, y1 + 2), (x2 + 2, y2 + 2), width)
        # 管道主体
        pygame.draw.line(surface, (55, 50, 42), (x1, y1), (x2, y2), width)
        # 高光
        pygame.draw.line(surface, (75, 70, 60), (x1, y1), (x2, y2), max(1, width // 3))
    
    # 管道接头和阀门
    joints = [
        (cx - int(w * 0.4), cy - int(h * 0.2), True),
        (cx - int(w * 0.4), cy - int(h * 0.1), False),
        (cx - int(w * 0.4), cy + int(h * 0.25), True),
        (cx + int(w * 0.4), cy - int(h * 0.2), True),
        (cx + int(w * 0.4), cy - int(h * 0.1), False),
        (cx + int(w * 0.4), cy + int(h * 0.25), True),
    ]
    for jx, jy, is_valve in joints:
        pygame.draw.circle(surface, (65, 58, 48), (jx, jy), 6)
        pygame.draw.circle(surface, rust, (jx, jy), 4)
        if is_valve:
            # 阀门手柄
            valve_angle = t * 0.5 if jx < cx else -t * 0.5
            vx = jx + int(math.cos(valve_angle) * 8)
            vy = jy + int(math.sin(valve_angle) * 4)
            pygame.draw.line(surface, (100, 90, 75), (jx, jy), (vx, vy), 3)
            pygame.draw.circle(surface, (120, 110, 90), (vx, vy), 3)
    
    # 【独特元素3】油井塔架
    for side in [-1, 1]:
        tower_x = cx + side * int(w * 0.32)
        tower_y = cy - int(h * 0.35)
        tower_h = int(h * 0.3)
        tower_w = int(w * 0.08)
        
        # 塔架支柱
        pygame.draw.line(surface, (50, 45, 38), 
                        (tower_x - tower_w, tower_y + tower_h), (tower_x, tower_y), 3)
        pygame.draw.line(surface, (50, 45, 38), 
                        (tower_x + tower_w, tower_y + tower_h), (tower_x, tower_y), 3)
        pygame.draw.line(surface, (50, 45, 38), 
                        (tower_x - tower_w, tower_y + tower_h), (tower_x + tower_w, tower_y + tower_h), 2)
        
        # 横梁
        for beam in range(4):
            beam_y = tower_y + beam * (tower_h // 4)
            beam_w = tower_w * (1 - beam * 0.2)
            pygame.draw.line(surface, (40, 35, 28), 
                           (int(tower_x - beam_w), beam_y), (int(tower_x + beam_w), beam_y), 2)
        
        # 抽油机头
        pump_angle = t * 2 * side
        pump_head_x = tower_x + int(math.sin(pump_angle) * 8)
        pump_head_y = tower_y - 5 + int(abs(math.cos(pump_angle)) * 5)
        pygame.draw.line(surface, (70, 65, 55), (tower_x, tower_y), (pump_head_x, pump_head_y), 4)
        pygame.draw.circle(surface, (80, 75, 65), (pump_head_x, pump_head_y), 5)
    
    # 【独特元素4】油污滴落与油渍
    for i in range(8):
        drip_x = cx - int(w * 0.3) + i * int(w * 0.085)
        drip_start = cy + int(h * 0.08)
        drip_phase = (t * 0.7 + i * 0.15) % 1
        drip_y = drip_start + int(h * 0.35 * drip_phase)
        
        # 油污拖尾
        for seg in range(6):
            seg_y = drip_y - seg * 4
            seg_alpha = int(220 - seg * 30 - 80 * drip_phase)
            seg_size = 4 - seg // 2
            if seg_alpha > 0 and seg_y > drip_start and seg_size > 0:
                pygame.draw.circle(surface, (20, 18, 12, seg_alpha), (drip_x, seg_y), seg_size)
        
        # 油滴主体
        drop_size = int(5 * (1 - drip_phase * 0.4))
        pygame.draw.circle(surface, (15, 12, 8), (drip_x, drip_y), drop_size)
        pygame.draw.circle(surface, (50, 45, 38), (drip_x - 1, drip_y - 1), max(1, drop_size // 2))
    
    # 油渍痕迹
    stain_positions = [
        (cx - 20, cy + 5, 18, 10), (cx + 15, cy - 8, 15, 12),
        (cx - 8, cy + 20, 20, 8), (cx + 25, cy + 12, 12, 14),
    ]
    for sx, sy, sw, sh in stain_positions:
        pygame.draw.ellipse(surface, (25, 22, 18, 100), (sx - sw//2, sy - sh//2, sw, sh))
    
    # 【独特元素5】警告火焰标志
    sign_x, sign_y = cx, cy + int(h * 0.2)
    sign_size = 16
    
    # 三角警告牌
    sign_pts = [
        (sign_x, sign_y - sign_size),
        (sign_x - sign_size, sign_y + sign_size // 2),
        (sign_x + sign_size, sign_y + sign_size // 2),
    ]
    pygame.draw.polygon(surface, (255, 220, 0), sign_pts)
    pygame.draw.polygon(surface, (30, 30, 30), sign_pts, 2)
    
    # 火焰图标
    flame_icon = [
        (sign_x, sign_y - 8),
        (sign_x - 5, sign_y + 5),
        (sign_x - 2, sign_y + 2),
        (sign_x, sign_y + 6),
        (sign_x + 2, sign_y + 2),
        (sign_x + 5, sign_y + 5),
    ]
    pygame.draw.polygon(surface, (255, 100, 0), flame_icon)
    
    # 【独特元素6】油桶挂载
    for side in [-1, 1]:
        barrel_x = cx + side * int(w * 0.42)
        barrel_y = cy + int(h * 0.05)
        
        # 油桶主体
        pygame.draw.ellipse(surface, armor, (barrel_x - 6, barrel_y - 10, 12, 20))
        pygame.draw.ellipse(surface, (armor[0] + 15, armor[1] + 15, armor[2] + 15), 
                          (barrel_x - 6, barrel_y - 10, 12, 20), 1)
        
        # 桶箍
        for hoop in range(3):
            hoop_y = barrel_y - 8 + hoop * 8
            pygame.draw.line(surface, rust, (barrel_x - 6, hoop_y), (barrel_x + 6, hoop_y), 2)
        
        # 桶盖
        pygame.draw.ellipse(surface, (armor[0] + 20, armor[1] + 20, armor[2] + 20), 
                          (barrel_x - 5, barrel_y - 12, 10, 5))
        
        # 易燃标记
        pygame.draw.polygon(surface, toxic, [
            (barrel_x, barrel_y - 3),
            (barrel_x - 3, barrel_y + 4),
            (barrel_x + 3, barrel_y + 4),
        ])


# ==================== 异虫女皇涂装 ====================
def draw_hive_goliath(surface, x, y, w, h, frame, style):
    """
    异虫女皇 - 异形蜂巢的统治者（虫族利维坦）
    特色：蜂巢金装甲、蜂蜜黄毒素、六边形蜂巢结构、蜂群环绕
    独特元素：精细蜂巢网格、多层蜂群、蜂王冠冕、蜜腺系统、虫卵舱、信息素波
    """
    theme = get_goliath_theme(style)
    armor = theme["armor"]  # 蜂巢金
    toxic = theme["toxic"]  # 蜂蜜黄
    rust = theme["rust"]    # 蜂蜡色
    eye_color = theme["eye"]
    glow = theme["glow"]
    
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 【独特背景1】信息素波动场
    for wave in range(5):
        wave_phase = (t * 0.8 + wave * 0.4) % (2 * math.pi)
        wave_r = int(w * 0.15 + w * 0.35 * (wave_phase / (2 * math.pi)))
        wave_alpha = int(60 * (1 - wave_phase / (2 * math.pi)))
        if wave_alpha > 5:
            pygame.draw.circle(surface, (*toxic, wave_alpha), (cx, cy), wave_r, 2)
    
    # 【独特背景2】飘散花粉/孢子
    for i in range(20):
        pollen_angle = t * 0.15 + i * 0.31
        pollen_dist = int(w * 0.5 + w * 0.15 * math.sin(t * 0.5 + i * 0.4))
        pollen_x = cx + int(math.cos(pollen_angle) * pollen_dist)
        pollen_y = cy + int(math.sin(pollen_angle) * pollen_dist * 0.4) - int(15 * ((t * 0.2 + i * 0.05) % 1))
        pollen_size = int(2 + math.sin(t * 2 + i * 0.3))
        pollen_alpha = int(80 + 40 * math.sin(t + i * 0.2))
        pygame.draw.circle(surface, (*toxic, pollen_alpha), (pollen_x, pollen_y), pollen_size)
    
    # 主体绘制
    _draw_goliath_body(surface, x, y, w, h, frame, theme)
    
    # 【独特元素1】精细蜂巢六边形网格
    cell_size = int(w * 0.045)
    for row in range(-4, 5):
        for col in range(-5, 6):
            hx = cx + col * int(cell_size * 1.5) + (row % 2) * int(cell_size * 0.75)
            hy = cy + row * int(cell_size * 1.25)
            
            dist_from_center = math.sqrt((hx - cx)**2 + ((hy - cy) * 1.6)**2)
            if dist_from_center < w * 0.38:
                # 六边形蜂室
                cell_pts = []
                for i in range(6):
                    angle = i * math.pi / 3
                    cell_pts.append((
                        hx + int(math.cos(angle) * cell_size * 0.42),
                        hy + int(math.sin(angle) * cell_size * 0.42)
                    ))
                
                # 蜂巢内容物（随机类型）
                cell_type = (row * 7 + col * 11) % 5
                if cell_type == 0:
                    # 空蜂室
                    pygame.draw.polygon(surface, (30, 25, 18, 150), cell_pts)
                elif cell_type == 1:
                    # 蜂蜜填充
                    pygame.draw.polygon(surface, (*toxic, 150), cell_pts)
                    pygame.draw.polygon(surface, (*glow, 80), cell_pts, 1)
                elif cell_type == 2:
                    # 蜂卵
                    pygame.draw.polygon(surface, (40, 35, 25, 120), cell_pts)
                    pygame.draw.circle(surface, (250, 245, 220), (hx, hy), int(cell_size * 0.25))
                elif cell_type == 3:
                    # 花粉储存
                    pygame.draw.polygon(surface, (200, 150, 50, 150), cell_pts)
                else:
                    # 幼虫
                    pygame.draw.polygon(surface, (40, 35, 25, 120), cell_pts)
                    larva_wobble = int(2 * math.sin(t * 4 + row + col))
                    pygame.draw.ellipse(surface, (240, 230, 200), 
                                      (hx - 3 + larva_wobble, hy - 2, 6, 4))
                
                # 蜂蜡边框
                pygame.draw.polygon(surface, (*rust, 180), cell_pts, 1)
    
    # 【独特元素2】多层蜂群环绕
    # 内圈工蜂
    for i in range(10):
        bee_angle = t * 2.5 + i * 2 * math.pi / 10
        bee_dist = int(w * 0.42 + w * 0.05 * math.sin(t * 4 + i))
        bee_x = cx + int(math.cos(bee_angle) * bee_dist)
        bee_y = cy + int(math.sin(bee_angle) * bee_dist * 0.45)
        
        # 精细蜜蜂
        # 头部
        pygame.draw.circle(surface, (30, 25, 18), (bee_x - 4, bee_y), 2)
        # 胸部
        pygame.draw.ellipse(surface, (40, 35, 25), (bee_x - 3, bee_y - 2, 4, 4))
        # 腹部（条纹）
        pygame.draw.ellipse(surface, toxic, (bee_x + 1, bee_y - 3, 7, 6))
        for stripe in range(3):
            stripe_x = bee_x + 2 + stripe * 2
            pygame.draw.line(surface, (30, 25, 18), (stripe_x, bee_y - 2), (stripe_x, bee_y + 2), 1)
        # 翅膀
        wing_alpha = int(180 + 75 * math.sin(t * 25 + i))
        pygame.draw.ellipse(surface, (255, 255, 255, wing_alpha), (bee_x - 2, bee_y - 6, 6, 4))
        pygame.draw.ellipse(surface, (255, 255, 255, wing_alpha - 30), (bee_x, bee_y - 5, 5, 3))
        # 腿
        for leg in range(3):
            leg_x = bee_x + leg * 2
            pygame.draw.line(surface, (30, 25, 18), (leg_x, bee_y + 2), (leg_x + 1, bee_y + 4), 1)
    
    # 外圈兵蜂（更大）
    for i in range(6):
        bee_angle = -t * 1.5 + i * 2 * math.pi / 6
        bee_dist = int(w * 0.55 + w * 0.08 * math.sin(t * 3 + i))
        bee_x = cx + int(math.cos(bee_angle) * bee_dist)
        bee_y = cy + int(math.sin(bee_angle) * bee_dist * 0.4)
        
        # 兵蜂（大型）
        pygame.draw.circle(surface, (35, 30, 22), (bee_x - 5, bee_y), 3)
        pygame.draw.ellipse(surface, (45, 40, 30), (bee_x - 4, bee_y - 3, 6, 6))
        pygame.draw.ellipse(surface, toxic, (bee_x + 2, bee_y - 4, 10, 8))
        for stripe in range(4):
            stripe_x = bee_x + 3 + stripe * 2
            pygame.draw.line(surface, (35, 30, 22), (stripe_x, bee_y - 3), (stripe_x, bee_y + 3), 1)
        # 大翅膀
        wing_alpha = int(160 + 80 * math.sin(t * 22 + i))
        pygame.draw.ellipse(surface, (255, 255, 255, wing_alpha), (bee_x - 3, bee_y - 8, 10, 6))
    
    # 【独特元素3】蜂王冠冕（精细版）
    crown_x, crown_y = cx, cy - int(h * 0.4)
    
    # 冠冕底座
    pygame.draw.ellipse(surface, rust, (crown_x - 18, crown_y + 8, 36, 8))
    pygame.draw.ellipse(surface, toxic, (crown_x - 18, crown_y + 8, 36, 8), 1)
    
    # 冠冕尖峰
    peaks = [
        (crown_x - 14, crown_y + 6, 10),
        (crown_x - 7, crown_y + 4, 14),
        (crown_x, crown_y, 18),
        (crown_x + 7, crown_y + 4, 14),
        (crown_x + 14, crown_y + 6, 10),
    ]
    for px, py, peak_h in peaks:
        peak_pts = [(px - 4, crown_y + 10), (px + 4, crown_y + 10), (px, crown_y + 10 - peak_h)]
        pygame.draw.polygon(surface, toxic, peak_pts)
        pygame.draw.polygon(surface, (255, 220, 100), peak_pts, 1)
    
    # 宝石
    gem_positions = [(crown_x - 7, crown_y + 5), (crown_x, crown_y + 1), (crown_x + 7, crown_y + 5)]
    for gx, gy in gem_positions:
        gem_pulse = int(3 + math.sin(t * 3 + gx * 0.1) * 1)
        pygame.draw.circle(surface, eye_color, (gx, gy), gem_pulse)
        pygame.draw.circle(surface, (255, 255, 200), (gx - 1, gy - 1), max(1, gem_pulse // 2))
    
    # 【独特元素4】蜜腺系统
    gland_positions = [
        (cx - int(w * 0.25), cy + int(h * 0.12)),
        (cx + int(w * 0.25), cy + int(h * 0.12)),
    ]
    for gx, gy in gland_positions:
        # 蜜腺主体
        pygame.draw.ellipse(surface, (*armor, 200), (gx - 8, gy - 12, 16, 24))
        pygame.draw.ellipse(surface, rust, (gx - 8, gy - 12, 16, 24), 2)
        
        # 内部蜂蜜可见
        honey_level = int(18 * (0.6 + 0.2 * math.sin(t * 0.5)))
        pygame.draw.ellipse(surface, (*toxic, 180), (gx - 6, gy + 10 - honey_level, 12, honey_level))
        
        # 滴落
        drip_phase = (t * 0.8 + gx * 0.01) % 1
        if drip_phase < 0.5:
            drip_y = gy + 12 + int(20 * drip_phase * 2)
            drip_size = int(4 * (1 - drip_phase))
            pygame.draw.circle(surface, toxic, (gx, drip_y), max(1, drip_size))
    
    # 【独特元素5】虫卵舱
    egg_positions = [
        (cx - int(w * 0.35), cy + int(h * 0.05)),
        (cx + int(w * 0.35), cy + int(h * 0.05)),
    ]
    for ex, ey in egg_positions:
        # 卵舱外壳
        pygame.draw.ellipse(surface, (60, 55, 45), (ex - 10, ey - 15, 20, 30))
        pygame.draw.ellipse(surface, rust, (ex - 10, ey - 15, 20, 30), 2)
        
        # 内部卵
        for egg in range(4):
            egg_x = ex + (egg % 2 - 0.5) * 6
            egg_y = ey - 8 + (egg // 2) * 10
            egg_wobble = int(1.5 * math.sin(t * 3 + egg))
            pygame.draw.ellipse(surface, (250, 245, 230), 
                              (int(egg_x) - 3 + egg_wobble, int(egg_y) - 4, 6, 8))
            pygame.draw.ellipse(surface, (200, 190, 170), 
                              (int(egg_x) - 3 + egg_wobble, int(egg_y) - 4, 6, 8), 1)
    
    # 【独特元素6】蜂巢入口（精细版）
    entrance_x, entrance_y = cx, cy + int(h * 0.32)
    entrance_size = int(w * 0.12)
    
    # 六边形入口
    entrance_pts = []
    for i in range(6):
        angle = i * math.pi / 3 + math.pi / 6
        entrance_pts.append((
            entrance_x + int(math.cos(angle) * entrance_size),
            entrance_y + int(math.sin(angle) * entrance_size)
        ))
    
    # 入口层次
    for layer in range(3):
        layer_size = entrance_size - layer * 4
        layer_pts = []
        for i in range(6):
            angle = i * math.pi / 3 + math.pi / 6
            layer_pts.append((
                entrance_x + int(math.cos(angle) * layer_size),
                entrance_y + int(math.sin(angle) * layer_size)
            ))
        layer_color = (30 - layer * 8, 25 - layer * 7, 18 - layer * 5)
        pygame.draw.polygon(surface, layer_color, layer_pts)
    
    pygame.draw.polygon(surface, rust, entrance_pts, 2)
    
    # 入口发光
    inner_pulse = int(5 + 3 * math.sin(t * 2))
    pygame.draw.circle(surface, (*glow, 120), (entrance_x, entrance_y), inner_pulse)


# ==================== 异形寄生涂装 ====================
def draw_xenomorph_goliath(surface, x, y, w, h, frame, style):
    """
    异形寄生 - 外星寄生生物入侵的机体（LV-426噩梦）
    特色：生物金属黑、酸液绿、异形骨骼结构、寄生触手
    独特元素：精细异形头、多节脊椎、分段尾巴、酸液系统、面部抱抱虫、外骨骼甲
    """
    theme = get_goliath_theme(style)
    armor = theme["armor"]  # 生物金属
    toxic = theme["toxic"]  # 酸液绿
    rust = theme["rust"]
    eye_color = theme["eye"]
    glow = theme["glow"]
    
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 【独特背景1】酸液腐蚀雾气
    for layer in range(3):
        for i in range(10):
            acid_angle = t * 0.3 + i * 0.63 + layer * 0.4
            acid_dist = int(w * 0.42 + w * 0.12 * math.sin(t * 1.2 + i + layer))
            acid_x = cx + int(math.cos(acid_angle) * acid_dist)
            acid_y = cy + int(math.sin(acid_angle) * acid_dist * 0.45) - layer * 8
            acid_size = int(6 - layer + 4 * math.sin(t * 2 + i * 0.5))
            acid_alpha = int(70 - layer * 20 + 30 * math.sin(t + i))
            if acid_alpha > 0:
                pygame.draw.circle(surface, (*toxic, acid_alpha), (acid_x, acid_y), acid_size)
    
    # 【独特背景2】酸液滴落雨
    for i in range(12):
        drip_x = cx + int((w * 0.5) * math.sin(i * 0.52 + t * 0.1))
        drip_phase = (t * 0.6 + i * 0.083) % 1
        drip_y = y + int(h * 1.2 * drip_phase)
        drip_size = int(3 + 2 * (1 - drip_phase))
        drip_alpha = int(180 * (1 - drip_phase))
        if drip_alpha > 0:
            pygame.draw.circle(surface, (*toxic, drip_alpha), (drip_x, drip_y), drip_size)
            # 尾迹
            if drip_phase > 0.1:
                pygame.draw.line(surface, (*toxic, drip_alpha // 2), 
                               (drip_x, drip_y - int(15 * drip_phase)), (drip_x, drip_y), 1)
    
    # 主体绘制
    _draw_goliath_body(surface, x, y, w, h, frame, theme)
    
    # 【独特元素1】精细异形延长头骨
    skull_x, skull_y = cx, cy - int(h * 0.42)
    skull_len = int(w * 0.4)
    
    # 主头颅（前部）
    skull_pts = [
        (skull_x, skull_y - 10),
        (skull_x - 12, skull_y - 2),
        (skull_x - 16, skull_y + 12),
        (skull_x - 10, skull_y + 22),
        (skull_x, skull_y + 18),
        (skull_x + 10, skull_y + 22),
        (skull_x + 16, skull_y + 12),
        (skull_x + 12, skull_y - 2),
    ]
    pygame.draw.polygon(surface, armor, skull_pts)
    pygame.draw.polygon(surface, (35, 40, 48), skull_pts, 2)
    
    # 延长后脑（管状）
    for seg in range(8):
        seg_y = skull_y - 10 - seg * int(skull_len / 8)
        seg_width = int(8 - seg * 0.6)
        if seg_width > 0:
            pygame.draw.ellipse(surface, armor, 
                              (skull_x - seg_width, seg_y - 3, seg_width * 2, 6))
            # 骨骼脊
            pygame.draw.line(surface, (55, 60, 70), 
                           (skull_x - seg_width + 2, seg_y), (skull_x + seg_width - 2, seg_y), 1)
    
    # 头骨纹理线
    for ridge in range(6):
        ridge_x_offset = int(4 * math.sin(ridge * 0.8))
        ridge_y = skull_y + 5 + ridge * 3
        pygame.draw.line(surface, (50, 55, 65), 
                        (skull_x - 10 + ridge_x_offset, ridge_y), 
                        (skull_x + 10 - ridge_x_offset, ridge_y), 1)
    
    # 内颌（第二嘴）
    inner_jaw_y = skull_y + 16 + int(3 * math.sin(t * 4))
    pygame.draw.ellipse(surface, (25, 28, 35), (skull_x - 5, inner_jaw_y, 10, 6))
    # 内颌牙齿
    for tooth in range(4):
        tx = skull_x - 4 + tooth * 3
        pygame.draw.line(surface, (200, 200, 210), (tx, inner_jaw_y + 2), (tx, inner_jaw_y + 5), 1)
    
    # 【独特元素2】多节外露脊椎
    spine_start_y = cy - int(h * 0.18)
    for i in range(10):
        spine_y = spine_start_y + i * 7
        spine_width = int(7 - i * 0.3 + 2 * math.sin(t * 0.5 + i * 0.2))
        
        # 椎骨主体
        pygame.draw.ellipse(surface, (55, 60, 68), 
                           (cx - spine_width, spine_y - 4, spine_width * 2, 8))
        # 椎骨中心凹槽
        pygame.draw.ellipse(surface, (35, 40, 48), 
                           (cx - spine_width + 3, spine_y - 2, spine_width * 2 - 6, 4))
        
        # 横突
        for side in [-1, 1]:
            tp_pts = [
                (cx + side * spine_width, spine_y),
                (cx + side * (spine_width + 6), spine_y - 3),
                (cx + side * (spine_width + 5), spine_y + 3),
            ]
            pygame.draw.polygon(surface, (45, 50, 58), tp_pts)
        
        # 棘突（向后）
        pygame.draw.polygon(surface, (50, 55, 63), [
            (cx, spine_y - 4),
            (cx - 2, spine_y - 8 - i % 2),
            (cx + 2, spine_y - 8 - i % 2),
        ])
    
    # 【独特元素3】分段异形尾巴
    tail_start_x = cx
    tail_start_y = cy + int(h * 0.38)
    tail_pts = [(tail_start_x, tail_start_y)]
    
    for seg in range(15):
        seg_angle = math.sin(t * 2.5 + seg * 0.35) * 0.4 + seg * 0.08
        seg_len = 7 - seg * 0.2
        seg_x = tail_pts[-1][0] + int(math.cos(seg_angle) * seg_len)
        seg_y = tail_pts[-1][1] + int(math.sin(seg_angle) * 2) + 5
        tail_pts.append((seg_x, seg_y))
    
    # 尾巴分段绘制
    for i in range(len(tail_pts) - 1):
        seg_width = max(1, 6 - i // 3)
        # 段间隙
        if i % 2 == 0:
            pygame.draw.line(surface, armor, tail_pts[i], tail_pts[i+1], seg_width)
            # 脊骨突起
            mid_x = (tail_pts[i][0] + tail_pts[i+1][0]) // 2
            mid_y = (tail_pts[i][1] + tail_pts[i+1][1]) // 2
            pygame.draw.circle(surface, (60, 65, 75), (mid_x, mid_y - 2), 2)
        else:
            pygame.draw.line(surface, (40, 45, 55), tail_pts[i], tail_pts[i+1], seg_width - 1)
    
    # 尾巴尖刺（精细版）
    tail_tip = tail_pts[-1]
    blade_len = 20
    blade_pts = [
        (tail_tip[0] - 5, tail_tip[1]),
        (tail_tip[0] + 5, tail_tip[1]),
        (tail_tip[0] + 3, tail_tip[1] + blade_len * 0.6),
        (tail_tip[0], tail_tip[1] + blade_len),
        (tail_tip[0] - 3, tail_tip[1] + blade_len * 0.6),
    ]
    pygame.draw.polygon(surface, (70, 80, 95), blade_pts)
    pygame.draw.polygon(surface, toxic, blade_pts, 1)
    # 刀刃边缘光
    pygame.draw.line(surface, (100, 110, 130), blade_pts[0], blade_pts[3], 1)
    pygame.draw.line(surface, (100, 110, 130), blade_pts[1], blade_pts[3], 1)
    
    # 【独特元素4】酸液喷溅系统
    acid_sources = [
        (cx - int(w * 0.28), cy + int(h * 0.08)),
        (cx + int(w * 0.28), cy + int(h * 0.08)),
        (cx, cy + int(h * 0.25)),
    ]
    for src_x, src_y in acid_sources:
        # 酸液喷口
        pygame.draw.circle(surface, (40, 50, 45), (src_x, src_y), 5)
        pygame.draw.circle(surface, toxic, (src_x, src_y), 3)
        
        # 喷射酸液流
        for stream in range(4):
            stream_angle = math.pi / 2 + (stream - 1.5) * 0.4 + math.sin(t * 3 + stream) * 0.2
            for drop in range(6):
                drop_dist = 8 + drop * 5 + int(3 * math.sin(t * 5 + drop + stream))
                drop_x = src_x + int(math.cos(stream_angle) * drop_dist * 0.3)
                drop_y = src_y + int(math.sin(stream_angle) * drop_dist)
                drop_alpha = int(200 - drop * 30)
                drop_size = 4 - drop // 2
                if drop_alpha > 0 and drop_size > 0:
                    pygame.draw.circle(surface, (*toxic, drop_alpha), (drop_x, drop_y), drop_size)
        
        # 地面腐蚀痕
        corr_y = src_y + 35
        pygame.draw.ellipse(surface, (*toxic, 80), (src_x - 10, corr_y - 3, 20, 6))
    
    # 【独特元素5】面部抱脸虫装饰
    facehugger_x, facehugger_y = cx + int(w * 0.18), cy - int(h * 0.15)
    
    # 抱脸虫身体
    pygame.draw.ellipse(surface, (60, 55, 50), (facehugger_x - 8, facehugger_y - 5, 16, 10))
    # 腿（8条）
    for leg in range(8):
        leg_side = -1 if leg < 4 else 1
        leg_idx = leg % 4
        leg_angle = leg_side * (0.3 + leg_idx * 0.25) + math.sin(t * 4 + leg) * 0.15
        leg_x1 = facehugger_x + leg_side * 6
        leg_y1 = facehugger_y + (leg_idx - 1.5) * 2
        leg_x2 = leg_x1 + int(math.cos(leg_angle) * 10)
        leg_y2 = leg_y1 + int(math.sin(leg_angle) * 6)
        pygame.draw.line(surface, (50, 45, 40), (leg_x1, leg_y1), (leg_x2, leg_y2), 2)
        # 腿末端钩
        pygame.draw.circle(surface, (70, 65, 58), (leg_x2, leg_y2), 2)
    # 尾巴
    fh_tail_pts = [(facehugger_x, facehugger_y + 5)]
    for seg in range(5):
        fh_tail_pts.append((
            fh_tail_pts[-1][0] + int(3 * math.sin(t * 3 + seg)),
            fh_tail_pts[-1][1] + 4
        ))
    if len(fh_tail_pts) >= 2:
        pygame.draw.lines(surface, (55, 50, 45), False, fh_tail_pts, 2)
    
    # 【独特元素6】外骨骼装甲板
    armor_plates = [
        (cx - int(w * 0.22), cy - int(h * 0.05), 15, 20, -0.2),
        (cx + int(w * 0.22), cy - int(h * 0.05), 15, 20, 0.2),
        (cx - int(w * 0.18), cy + int(h * 0.15), 12, 16, -0.1),
        (cx + int(w * 0.18), cy + int(h * 0.15), 12, 16, 0.1),
    ]
    for px, py, pw, ph, angle in armor_plates:
        # 装甲板多边形
        plate_pts = [
            (px - pw // 2, py - ph // 3),
            (px + pw // 2, py - ph // 2),
            (px + pw // 2 + 3, py + ph // 3),
            (px, py + ph // 2),
            (px - pw // 2 - 3, py + ph // 3),
        ]
        # 旋转
        rotated_pts = []
        for pt_x, pt_y in plate_pts:
            dx, dy = pt_x - px, pt_y - py
            rx = px + dx * math.cos(angle) - dy * math.sin(angle)
            ry = py + dx * math.sin(angle) + dy * math.cos(angle)
            rotated_pts.append((int(rx), int(ry)))
        
        pygame.draw.polygon(surface, armor, rotated_pts)
        pygame.draw.polygon(surface, (50, 55, 65), rotated_pts, 2)
        # 装甲纹路
        pygame.draw.line(surface, (60, 65, 75), rotated_pts[0], rotated_pts[2], 1)
        pygame.draw.line(surface, (60, 65, 75), rotated_pts[1], rotated_pts[4], 1)


# ==================== 血疫狂潮涂装 ====================
def draw_crimson_goliath(surface, x, y, w, h, frame, style):
    """
    血疫狂潮 - 血腥瘟疫的化身（血月屠夫）
    特色：暗红装甲、血红毒素、血管脉络、心跳脉动
    独特元素：精细心脏、立体血管网、脉搏冲击波、血液喷涌、血池涟漪、血字诅咒
    """
    theme = get_goliath_theme(style)
    armor = theme["armor"]  # 暗红
    toxic = theme["toxic"]  # 血红
    rust = theme["rust"]
    eye_color = theme["eye"]
    glow = theme["glow"]
    
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 【独特背景1】血雾弥漫层
    for layer in range(3):
        for i in range(10):
            blood_angle = t * 0.25 + i * 0.63 + layer * 0.35
            blood_dist = int(w * 0.48 + w * 0.12 * math.sin(t * 1.1 + i * 0.4 + layer))
            blood_x = cx + int(math.cos(blood_angle) * blood_dist)
            blood_y = cy + int(math.sin(blood_angle) * blood_dist * 0.45) - layer * 10
            blood_size = int(8 - layer * 2 + 4 * math.sin(t * 2.2 + i * 0.35))
            blood_alpha = int(60 - layer * 18 + 25 * math.sin(t + i * 0.28))
            if blood_alpha > 0:
                pygame.draw.circle(surface, (*toxic, blood_alpha), (blood_x, blood_y), blood_size)
    
    # 【独特背景2】血滴雨
    for i in range(15):
        rain_x = cx + int((w * 0.55) * math.sin(i * 0.42 + t * 0.08))
        rain_phase = (t * 0.8 + i * 0.067) % 1
        rain_y = y + int(h * 1.3 * rain_phase)
        rain_size = int(4 + 2 * (1 - rain_phase))
        rain_alpha = int(200 * (1 - rain_phase * 0.7))
        if rain_alpha > 0:
            pygame.draw.circle(surface, (*toxic, rain_alpha), (rain_x, rain_y), rain_size)
            # 血滴尾迹
            tail_len = int(12 * rain_phase)
            if tail_len > 2:
                pygame.draw.line(surface, (*toxic, rain_alpha // 2), 
                               (rain_x, rain_y - tail_len), (rain_x, rain_y), 2)
    
    # 主体绘制
    _draw_goliath_body(surface, x, y, w, h, frame, theme)
    
    # 【独特元素1】精细暴露心脏
    heart_x, heart_y = cx, cy + int(h * 0.1)
    
    # 心跳脉动（复杂波形）
    heartbeat_phase = (t * 3.5) % (2 * math.pi)
    # 双峰心跳
    beat1 = max(0, math.sin(heartbeat_phase * 2)) if heartbeat_phase < math.pi else 0
    beat2 = max(0, math.sin((heartbeat_phase - 0.3) * 2)) if 0.3 < heartbeat_phase < math.pi + 0.3 else 0
    heartbeat = 1 + 0.12 * beat1 + 0.08 * beat2
    
    heart_size = int(w * 0.13 * heartbeat)
    
    # 心脏阴影
    pygame.draw.circle(surface, (60, 15, 15), 
                      (heart_x - int(heart_size * 0.45) + 3, heart_y - int(heart_size * 0.25) + 3), 
                      int(heart_size * 0.72))
    pygame.draw.circle(surface, (60, 15, 15), 
                      (heart_x + int(heart_size * 0.45) + 3, heart_y - int(heart_size * 0.25) + 3), 
                      int(heart_size * 0.72))
    
    # 左右心室
    pygame.draw.circle(surface, toxic, 
                      (heart_x - int(heart_size * 0.45), heart_y - int(heart_size * 0.25)), 
                      int(heart_size * 0.72))
    pygame.draw.circle(surface, toxic, 
                      (heart_x + int(heart_size * 0.45), heart_y - int(heart_size * 0.25)), 
                      int(heart_size * 0.72))
    
    # 心尖（精细版）
    heart_tip_pts = [
        (heart_x - int(heart_size * 0.95), heart_y - int(heart_size * 0.08)),
        (heart_x - int(heart_size * 0.5), heart_y + int(heart_size * 0.4)),
        (heart_x, heart_y + int(heart_size * 1.25)),
        (heart_x + int(heart_size * 0.5), heart_y + int(heart_size * 0.4)),
        (heart_x + int(heart_size * 0.95), heart_y - int(heart_size * 0.08)),
    ]
    pygame.draw.polygon(surface, toxic, heart_tip_pts)
    
    # 心脏表面血管
    heart_veins = [
        [(heart_x - 8, heart_y - 10), (heart_x - 12, heart_y), (heart_x - 8, heart_y + 12)],
        [(heart_x + 8, heart_y - 10), (heart_x + 12, heart_y), (heart_x + 8, heart_y + 12)],
        [(heart_x, heart_y - 12), (heart_x - 3, heart_y + 5), (heart_x, heart_y + 18)],
    ]
    for vein in heart_veins:
        if len(vein) >= 2:
            pygame.draw.lines(surface, (120, 25, 25), False, vein, 2)
    
    # 心脏高光
    pygame.draw.circle(surface, (*glow, 180), 
                      (heart_x - int(heart_size * 0.35), heart_y - int(heart_size * 0.4)), 
                      int(heart_size * 0.28))
    
    # 心脏轮廓
    pygame.draw.circle(surface, (90, 18, 18), 
                      (heart_x - int(heart_size * 0.45), heart_y - int(heart_size * 0.25)), 
                      int(heart_size * 0.72), 2)
    pygame.draw.circle(surface, (90, 18, 18), 
                      (heart_x + int(heart_size * 0.45), heart_y - int(heart_size * 0.25)), 
                      int(heart_size * 0.72), 2)
    
    # 【独特元素2】立体血管网络
    # 主动脉和静脉
    main_vessels = [
        # (起点, 方向角度, 长度, 宽度, 分支数, 类型)
        ((heart_x - 8, heart_y - 18), -0.8, 45, 5, 4, "artery"),
        ((heart_x + 8, heart_y - 18), -2.3, 45, 5, 4, "artery"),
        ((heart_x - 15, heart_y - 5), -0.4, 50, 4, 3, "vein"),
        ((heart_x + 15, heart_y - 5), -2.7, 50, 4, 3, "vein"),
        ((heart_x - 5, heart_y + 20), 0.3, 40, 4, 3, "artery"),
        ((heart_x + 5, heart_y + 20), 2.8, 40, 4, 3, "artery"),
    ]
    
    for (vx, vy), base_angle, length, width, branches, vessel_type in main_vessels:
        # 血管脉动
        pulse_offset = 0.15 * math.sin(heartbeat_phase + vx * 0.05) if vessel_type == "artery" else 0
        
        # 主干
        vessel_pts = [(vx, vy)]
        for seg in range(6):
            seg_angle = base_angle + 0.25 * math.sin(t * 1.5 + seg * 0.4 + vx * 0.1) + pulse_offset
            seg_len = length / 6
            vessel_pts.append((
                int(vessel_pts[-1][0] + math.cos(seg_angle) * seg_len),
                int(vessel_pts[-1][1] + math.sin(seg_angle) * seg_len)
            ))
        
        # 绘制主干（带脉动粗细变化）
        for j in range(len(vessel_pts) - 1):
            seg_width = max(1, width - j // 2)
            pulse_width = seg_width + int(2 * beat1) if vessel_type == "artery" else seg_width
            
            # 动脉鲜红，静脉暗红
            if vessel_type == "artery":
                v_color = (min(255, toxic[0] + int(40 * beat1)), toxic[1] - 10, toxic[2] - 10)
            else:
                v_color = (toxic[0] - 30, toxic[1] - 20, toxic[2])
            
            pygame.draw.line(surface, v_color, vessel_pts[j], vessel_pts[j + 1], pulse_width)
        
        # 分支
        for b in range(branches):
            if len(vessel_pts) > 2:
                branch_start = vessel_pts[2 + b % (len(vessel_pts) - 2)]
                for side in [-1, 1]:
                    branch_angle = base_angle + side * 0.6 + 0.2 * math.sin(t + b)
                    branch_end = (
                        branch_start[0] + int(math.cos(branch_angle) * 15),
                        branch_start[1] + int(math.sin(branch_angle) * 15)
                    )
                    pygame.draw.line(surface, (140, 30, 30), branch_start, branch_end, 2)
                    # 毛细血管
                    for cap in range(2):
                        cap_angle = branch_angle + (cap - 0.5) * 0.8
                        cap_end = (
                            branch_end[0] + int(math.cos(cap_angle) * 8),
                            branch_end[1] + int(math.sin(cap_angle) * 8)
                        )
                        pygame.draw.line(surface, (120, 25, 25), branch_end, cap_end, 1)
    
    # 【独特元素3】脉搏冲击波
    for wave in range(4):
        pulse_wave_phase = (t * 2.5 + wave * 0.5) % (2 * math.pi)
        wave_r = int(w * 0.12 + w * 0.3 * (pulse_wave_phase / (2 * math.pi)))
        wave_alpha = int(180 * (1 - pulse_wave_phase / (2 * math.pi)))
        
        if wave_alpha > 10:
            pygame.draw.circle(surface, (*toxic, wave_alpha), (heart_x, heart_y), wave_r, 3)
            # 波纹扭曲效果
            if wave_r > 20:
                for distort in range(8):
                    d_angle = distort * math.pi / 4 + pulse_wave_phase
                    d_x = heart_x + int(math.cos(d_angle) * wave_r)
                    d_y = heart_y + int(math.sin(d_angle) * wave_r * 0.5)
                    pygame.draw.circle(surface, (*toxic, wave_alpha // 2), (d_x, d_y), 3)
    
    # 【独特元素4】血液喷涌效果
    spurt_positions = [
        (cx - int(w * 0.32), cy - int(h * 0.08)),
        (cx + int(w * 0.32), cy - int(h * 0.08)),
        (cx, cy + int(h * 0.28)),
    ]
    for sp_x, sp_y in spurt_positions:
        # 喷射相位
        spurt_phase = (t * 2 + sp_x * 0.02) % 1
        
        if spurt_phase < 0.4:  # 喷射期
            spurt_intensity = spurt_phase / 0.4
            
            for stream in range(5):
                stream_angle = math.pi / 2 + (stream - 2) * 0.25 + math.sin(t * 6 + stream) * 0.15
                for drop in range(8):
                    drop_dist = int(spurt_intensity * (15 + drop * 6))
                    drop_x = sp_x + int(math.cos(stream_angle) * drop_dist * 0.4)
                    drop_y = sp_y + int(math.sin(stream_angle) * drop_dist)
                    drop_alpha = int(220 * spurt_intensity - drop * 25)
                    drop_size = int(5 * spurt_intensity - drop * 0.4)
                    if drop_alpha > 0 and drop_size > 0:
                        pygame.draw.circle(surface, (*toxic, drop_alpha), (drop_x, drop_y), drop_size)
    
    # 【独特元素5】血池与涟漪（精细版）
    pool_y = cy + int(h * 0.4)
    pool_w = int(w * 0.7)
    pool_h = int(h * 0.1)
    
    # 血池主体（多层）
    for layer in range(3):
        layer_w = pool_w - layer * 15
        layer_h = pool_h - layer * 3
        layer_alpha = 120 - layer * 35
        layer_y = pool_y - layer * 2
        if layer_w > 0 and layer_h > 0:
            pygame.draw.ellipse(surface, (*toxic, layer_alpha), 
                              (cx - layer_w // 2, layer_y, layer_w, layer_h))
    
    # 涟漪
    for ripple in range(4):
        ripple_phase = (t * 1.2 + ripple * 0.4) % 1
        ripple_r = int(pool_w * 0.35 * ripple_phase)
        ripple_alpha = int(100 * (1 - ripple_phase))
        if ripple_alpha > 0 and ripple_r > 0:
            pygame.draw.ellipse(surface, (*toxic, ripple_alpha), 
                              (cx - ripple_r, pool_y + pool_h // 2 - ripple_r // 4, 
                               ripple_r * 2, ripple_r // 2), 2)
    
    # 【独特元素6】血字诅咒符文
    rune_x, rune_y = cx + int(w * 0.22), cy - int(h * 0.25)
    rune_pulse = 1 + 0.2 * math.sin(t * 2)
    
    # 简化的血字符文（十字架变体）
    rune_size = int(12 * rune_pulse)
    pygame.draw.line(surface, toxic, 
                    (rune_x, rune_y - rune_size), (rune_x, rune_y + rune_size), 3)
    pygame.draw.line(surface, toxic, 
                    (rune_x - rune_size, rune_y - rune_size // 2), 
                    (rune_x + rune_size, rune_y - rune_size // 2), 3)
    # 符文尖角
    for corner in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        cx_off = rune_x + corner[0] * rune_size
        cy_off = rune_y + corner[1] * rune_size // 2
        pygame.draw.line(surface, (*glow, 180), (cx_off, cy_off), 
                        (cx_off + corner[0] * 4, cy_off + corner[1] * 4), 2)
    
    # 符文发光
    pygame.draw.circle(surface, (*glow, int(80 * rune_pulse)), (rune_x, rune_y), rune_size + 5)
    
    # 危险条纹
    _draw_hazard_stripes(surface, x, y, w, h, theme)
