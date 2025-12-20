# -*- coding: utf-8 -*-
"""
晶体粉碎者·CRUSHER (Tool-System "CRUSHER")
Project Code: VOID_DRILL_MK2

原型致敬: Crystyl Crusher (Calamity Mod Endgame Mining Tool)

设计理念：几何晶体 + 重型工程机械 + 虚空紫
视觉关键词：空间钻探机、紫色水晶巨石、激光钻头、厚重装甲

核心机制：冲撞与射线 - 坦克型战机
特性：极高血量、碰撞减免、穿透射线

【建模要点】
- 机头：圆锥形紫色激光力场钻头，高速旋转
- 机身：块状结构，棱角分明，非常厚重
- 材质：深紫黑曜石外壳 + 发光紫水晶簇
- 充能槽：机身侧面电池式发光槽
- 特效：虚空紫能量场、钻头旋转光芒

6款涂装设计（高差异化）：
- crusher_default: 晶体粉碎者·虚空钻探 - 标准紫水晶+黑曜石
- crusher_crimson: 血晶矿脉·深红钻机 - 血红水晶+暗铁
- crusher_azure: 天穹晶石·蓝晶采掘 - 冰蓝水晶+银白
- crusher_emerald: 翡翠矿心·绿晶碎岩 - 翠绿水晶+深棕
- crusher_golden: 黄金矿王·帝皇钻机 - 金色水晶+黑金
- crusher_void: 虚空吞噬·终极毁灭 - 纯黑虚空+白光
"""
import pygame
import math

# =============================================================================
#   核心色值定义 (来自设计文档)
# =============================================================================

CRUSHER_COLORS = {
    "crystal_main": (138, 43, 226),    # #8A2BE2 蓝紫主色
    "hull_black": (25, 25, 25),        # #191919 乌黑外壳
    "laser_glow": (230, 230, 250),     # #E6E6FA 淡紫激光
    "void_purple": (75, 0, 130),       # 虚空紫
    "crystal_bright": (180, 100, 255), # 亮紫水晶
}

# =============================================================================
#   6款皮肤主题配置（高差异化）
# =============================================================================

CRUSHER_THEMES = {
    # ================= [默认涂装] 晶体粉碎者 =================
    "crusher_default": {
        "name": "晶体粉碎者·虚空钻探",
        "desc": "虚空深处的终极采矿机械",
        # 外壳色系：黑曜石
        "hull_main": (25, 25, 30),          # 乌黑主体
        "hull_light": (50, 50, 60),         # 高光
        "hull_dark": (12, 12, 18),          # 深阴影
        "hull_edge": (70, 70, 85),          # 边缘
        # 水晶色系：紫水晶
        "crystal": (138, 43, 226),          # 蓝紫主色
        "crystal_bright": (180, 120, 255),  # 亮紫
        "crystal_dark": (90, 20, 160),      # 暗紫
        "crystal_core": (230, 200, 255),    # 核心白紫
        # 激光/能量
        "laser": (230, 230, 250),           # 淡紫激光
        "laser_core": (255, 255, 255),      # 纯白核心
        "glow": (150, 80, 255),             # 紫光晕
        # 细节
        "charge_bar": (138, 43, 226),       # 充能槽
        "rivet": (80, 80, 100),             # 铆钉
        "vent": (15, 15, 20),               # 散热口
        # 差异化特效参数
        "drill_style": "standard",          # 标准钻头
        "crystal_count": 4,                 # 水晶数量
        "exhaust_style": "dual",            # 双引擎
        "aura_style": "hex",                # 六边形光环
        "spark_color": (180, 100, 255),     # 火花颜色
    },
    
    # ================= [血晶系列] 深红钻机 =================
    "crusher_crimson": {
        "name": "血晶矿脉·深红钻机",
        "desc": "染血的矿脉中诞生的恐怖机械",
        "hull_main": (45, 18, 22),          # 暗红铁
        "hull_light": (80, 35, 45),         # 血锈高光
        "hull_dark": (22, 8, 10),           # 深血色
        "hull_edge": (120, 45, 55),         # 锈红边
        "crystal": (220, 20, 50),           # 血红水晶
        "crystal_bright": (255, 60, 100),   # 亮血红
        "crystal_dark": (160, 5, 30),       # 暗血红
        "crystal_core": (255, 150, 180),    # 粉白核心
        "laser": (255, 80, 120),            # 红激光
        "laser_core": (255, 200, 210),      # 粉白核心
        "glow": (255, 30, 80),              # 红光晕
        "charge_bar": (220, 20, 50),
        "rivet": (110, 50, 60),
        "vent": (30, 8, 10),
        # 差异化特效：血滴效果
        "drill_style": "serrated",          # 锯齿钻头
        "crystal_count": 5,                 # 更多血晶
        "exhaust_style": "flame",           # 火焰尾焰
        "aura_style": "pulse",              # 脉冲光环
        "spark_color": (255, 50, 80),       # 血红火花
        "drip_effect": True,                # 血滴特效
    },
    
    # ================= [天穹系列] 蓝晶采掘 =================
    "crusher_azure": {
        "name": "天穹晶石·蓝晶采掘",
        "desc": "天空之城遗落的神圣采掘器",
        "hull_main": (70, 80, 100),         # 银蓝
        "hull_light": (120, 135, 160),      # 亮银蓝
        "hull_dark": (40, 48, 65),          # 深蓝灰
        "hull_edge": (160, 175, 200),       # 银白边
        "crystal": (30, 160, 255),          # 天蓝水晶
        "crystal_bright": (100, 210, 255),  # 亮冰蓝
        "crystal_dark": (10, 90, 180),      # 深蓝
        "crystal_core": (180, 235, 255),    # 冰白核心
        "laser": (130, 210, 255),           # 蓝激光
        "laser_core": (230, 248, 255),      # 冰白核心
        "glow": (60, 170, 255),             # 蓝光晕
        "charge_bar": (30, 160, 255),
        "rivet": (140, 150, 170),
        "vent": (35, 42, 58),
        # 差异化特效：冰晶效果
        "drill_style": "prism",             # 棱镜钻头
        "crystal_count": 6,                 # 六角冰晶
        "exhaust_style": "frost",           # 冰霜尾焰
        "aura_style": "snowflake",          # 雪花光环
        "spark_color": (150, 220, 255),     # 冰蓝火花
        "frost_effect": True,               # 冰霜特效
    },
    
    # ================= [翡翠系列] 绿晶碎岩 =================
    "crusher_emerald": {
        "name": "翡翠矿心·绿晶碎岩",
        "desc": "丛林深处的远古采矿巨兽",
        "hull_main": (55, 45, 28),          # 深棕
        "hull_light": (95, 80, 50),         # 棕高光
        "hull_dark": (32, 25, 14),          # 深褐
        "hull_edge": (125, 105, 70),        # 棕边
        "crystal": (30, 220, 40),           # 翠绿水晶
        "crystal_bright": (100, 255, 110),  # 亮绿
        "crystal_dark": (10, 150, 20),      # 深绿
        "crystal_core": (180, 255, 190),    # 浅绿核心
        "laser": (80, 255, 110),            # 绿激光
        "laser_core": (210, 255, 220),      # 浅绿核心
        "glow": (60, 230, 80),              # 绿光晕
        "charge_bar": (30, 220, 40),
        "rivet": (100, 85, 50),
        "vent": (25, 20, 10),
        # 差异化特效：藤蔓效果
        "drill_style": "organic",           # 有机钻头
        "crystal_count": 3,                 # 少量大水晶
        "exhaust_style": "nature",          # 自然尾焰
        "aura_style": "vine",               # 藤蔓光环
        "spark_color": (100, 255, 120),     # 绿色火花
        "vine_effect": True,                # 藤蔓特效
    },
    
    # ================= [黄金系列] 帝皇钻机 =================
    "crusher_golden": {
        "name": "黄金矿王·帝皇钻机",
        "desc": "传说中的黄金采掘之王",
        "hull_main": (35, 28, 18),          # 黑金
        "hull_light": (65, 55, 35),         # 暗金高光
        "hull_dark": (18, 14, 8),           # 极深
        "hull_edge": (100, 85, 50),         # 暗金边
        "crystal": (255, 210, 30),          # 金色水晶
        "crystal_bright": (255, 240, 100),  # 亮金
        "crystal_dark": (220, 160, 10),     # 深金
        "crystal_core": (255, 252, 180),    # 白金核心
        "laser": (255, 235, 80),            # 金激光
        "laser_core": (255, 255, 200),      # 亮金核心
        "glow": (255, 220, 60),             # 金光晕
        "charge_bar": (255, 210, 30),
        "rivet": (200, 165, 70),
        "vent": (22, 18, 8),
        # 差异化特效：皇冠效果
        "drill_style": "royal",             # 皇家钻头
        "crystal_count": 5,                 # 五芒星排列
        "exhaust_style": "golden",          # 金色尾焰
        "aura_style": "crown",              # 皇冠光环
        "spark_color": (255, 230, 100),     # 金色火花
        "crown_effect": True,               # 皇冠特效
    },
    
    # ================= [虚空系列] 终极毁灭 =================
    "crusher_void": {
        "name": "虚空吞噬·终极毁灭",
        "desc": "吞噬一切的虚空终极兵器",
        "hull_main": (5, 5, 10),            # 极黑
        "hull_light": (20, 20, 30),         # 微光
        "hull_dark": (0, 0, 3),             # 深渊黑
        "hull_edge": (40, 40, 55),          # 暗边
        "crystal": (220, 200, 255),         # 虚空白紫
        "crystal_bright": (255, 255, 255),  # 纯白
        "crystal_dark": (170, 150, 220),    # 淡紫
        "crystal_core": (255, 255, 255),    # 纯白核心
        "laser": (255, 255, 255),           # 白激光
        "laser_core": (255, 255, 255),      # 纯白核心
        "glow": (235, 215, 255),            # 白紫光晕
        "charge_bar": (220, 200, 255),
        "rivet": (35, 35, 50),
        "vent": (2, 2, 6),
        # 差异化特效：虚空裂隙
        "drill_style": "void",              # 虚空钻头
        "crystal_count": 4,                 # 四维水晶
        "exhaust_style": "void",            # 虚空尾焰
        "aura_style": "rift",               # 裂隙光环
        "spark_color": (255, 240, 255),     # 白色火花
        "rift_effect": True,                # 裂隙特效
        "invert_glow": True,                # 反转发光（黑洞效果）
    },
}

# 涂装样式列表
CRUSHER_STYLES = list(CRUSHER_THEMES.keys())


def is_crusher_style(style):
    """检查是否为CRUSHER涂装"""
    return style in CRUSHER_STYLES


def get_crusher_theme(style):
    """获取涂装主题"""
    return CRUSHER_THEMES.get(style, CRUSHER_THEMES["crusher_default"])


# =============================================================================
#   辅助绘制函数
# =============================================================================

def _draw_crystal_cluster(surf, cx, cy, theme, t, count=5, base_size=8):
    """绘制精细水晶簇 - 多层结构"""
    crystal = theme["crystal"]
    crystal_bright = theme["crystal_bright"]
    crystal_dark = theme["crystal_dark"]
    crystal_core = theme["crystal_core"]
    glow = theme["glow"]
    
    pulse = 1.0 + math.sin(t * 4) * 0.15
    
    # 水晶簇底座光晕
    glow_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    glow_pulse = abs(math.sin(t * 3))
    for g in range(3):
        g_r = base_size * 1.5 - g * 3 + glow_pulse * 2
        g_alpha = 40 - g * 12
        if g_alpha > 0:
            pygame.draw.circle(glow_surf, (*glow[:3], g_alpha), (int(cx), int(cy)), int(g_r))
    surf.blit(glow_surf, (0, 0))
    
    for i in range(count):
        angle = (i / count) * math.pi * 2 + t * 0.3
        dist = base_size * 0.6
        x = cx + math.cos(angle) * dist
        y = cy + math.sin(angle) * dist * 0.7
        
        # 水晶尺寸变化
        size = base_size * (0.6 + (i % 3) * 0.2) * pulse
        height = size * 2.2
        
        # ===== 水晶阴影投射 =====
        shadow_pts = [
            (x + 2, y + size * 0.6),
            (x - size * 0.4 + 2, y + size * 0.5),
            (x + size * 0.4 + 2, y + size * 0.5),
        ]
        shadow_pts = [(int(p[0]), int(p[1])) for p in shadow_pts]
        pygame.draw.polygon(surf, (0, 0, 0, 40), shadow_pts)
        
        # ===== 六棱柱水晶主体 =====
        # 底部六边形
        base_pts = []
        for j in range(6):
            ba = j * (math.pi / 3) + t * 0.2
            bx = x + math.cos(ba) * size * 0.5
            by = y + math.sin(ba) * size * 0.3 + size * 0.3
            base_pts.append((int(bx), int(by)))
        
        # 顶部六边形（收束）
        top_pts = []
        for j in range(6):
            ta = j * (math.pi / 3) + t * 0.2
            tx = x + math.cos(ta) * size * 0.15
            ty = y - height + math.sin(ta) * size * 0.1
            top_pts.append((int(tx), int(ty)))
        
        # 绘制六个侧面（从暗到亮）
        for j in range(6):
            j_next = (j + 1) % 6
            side_pts = [base_pts[j], base_pts[j_next], top_pts[j_next], top_pts[j]]
            
            # 根据面的朝向选择颜色
            if j in [0, 5]:
                side_color = crystal_bright  # 正面高光
            elif j in [1, 4]:
                side_color = crystal         # 侧面中间色
            else:
                side_color = crystal_dark    # 背面暗色
            
            pygame.draw.polygon(surf, side_color, side_pts)
            pygame.draw.polygon(surf, crystal_dark, side_pts, 1)
        
        # ===== 水晶顶部封顶（棱锥尖） =====
        apex = (int(x), int(y - height - size * 0.4))
        for j in range(6):
            j_next = (j + 1) % 6
            tip_pts = [top_pts[j], top_pts[j_next], apex]
            tip_color = crystal_bright if j < 2 else crystal
            pygame.draw.polygon(surf, tip_color, tip_pts)
        
        # ===== 水晶内部发光核心 =====
        core_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
        core_pulse = abs(math.sin(t * 5 + i))
        core_y = y - height * 0.4
        for c in range(3):
            c_r = size * 0.3 - c * size * 0.08 + core_pulse * 2
            c_alpha = 80 - c * 20
            pygame.draw.circle(core_surf, (*crystal_core[:3], c_alpha), 
                             (int(x), int(core_y)), max(1, int(c_r)))
        surf.blit(core_surf, (0, 0))
        
        # ===== 水晶折射线 =====
        # 内部折射光线
        refract_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
        pygame.draw.line(refract_surf, (*crystal_core[:3], 120),
                        (int(x), int(y - height - size * 0.3)),
                        (int(x - size * 0.3), int(y)), 1)
        pygame.draw.line(refract_surf, (*crystal_core[:3], 100),
                        (int(x), int(y - height - size * 0.3)),
                        (int(x + size * 0.2), int(y - height * 0.5)), 1)
        surf.blit(refract_surf, (0, 0))
        
        # ===== 水晶尖端闪光 =====
        tip_flash = abs(math.sin(t * 8 + i * 0.7))
        if tip_flash > 0.7:
            flash_size = int(2 + tip_flash * 3)
            pygame.draw.circle(surf, crystal_core, (int(x), int(y - height - size * 0.4)), flash_size)


def _draw_drill_head(surf, cx, cy, theme, t):
    """绘制精细激光钻头（根据涂装差异化）"""
    crystal = theme["crystal"]
    crystal_bright = theme["crystal_bright"]
    crystal_dark = theme["crystal_dark"]
    crystal_core = theme["crystal_core"]
    laser = theme["laser"]
    laser_core = theme["laser_core"]
    glow = theme["glow"]
    hull_main = theme["hull_main"]
    hull_light = theme["hull_light"]
    hull_dark = theme["hull_dark"]
    
    # 获取差异化参数
    drill_style = theme.get("drill_style", "standard")
    spark_color = theme.get("spark_color", crystal_bright)
    invert_glow = theme.get("invert_glow", False)
    
    drill_length = 28
    drill_base_r = 16
    rotation = t * 8  # 高速旋转
    
    # 根据钻头风格调整旋转速度
    if drill_style == "serrated":
        rotation = t * 12  # 锯齿钻头更快
    elif drill_style == "void":
        rotation = t * 5   # 虚空钻头更慢更诡异
    elif drill_style == "royal":
        rotation = t * 6   # 皇家钻头稳重
    
    # ===== 【第零层】钻头座基结构 =====
    mount_r = drill_base_r + 3
    mount_y = cy - 2
    
    # 连接座外环（根据风格调整形状）
    mount_pts = []
    mount_sides = 8 if drill_style != "prism" else 6  # 棱镜是六边形
    for i in range(mount_sides):
        ma = i * (math.pi * 2 / mount_sides) + rotation * 0.1
        mx = cx + math.cos(ma) * mount_r
        my = mount_y + math.sin(ma) * mount_r * 0.5
        mount_pts.append((int(mx), int(my)))
    pygame.draw.polygon(surf, hull_dark, mount_pts)
    pygame.draw.polygon(surf, hull_light, mount_pts, 2)
    
    # 连接座装甲板
    plate_count = 4 if drill_style != "organic" else 3  # 有机风格用三角
    for i in range(plate_count):
        plate_angle = i * (math.pi * 2 / plate_count) + math.pi / plate_count
        px = cx + math.cos(plate_angle) * (mount_r - 2)
        py = mount_y + math.sin(plate_angle) * (mount_r - 2) * 0.5
        pygame.draw.circle(surf, hull_main, (int(px), int(py)), 3)
        pygame.draw.circle(surf, hull_light, (int(px), int(py)), 2)
        pygame.draw.circle(surf, (255, 255, 255), (int(px - 1), int(py - 1)), 1)
    
    # ===== 【第一层】钻头外层光晕 =====
    glow_layers = 6 if not invert_glow else 4
    for i in range(glow_layers):
        glow_r = drill_base_r + 12 - i * 2
        glow_alpha = 50 - i * 8
        if glow_alpha > 0:
            glow_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
            if invert_glow:
                # 虚空涂装：黑洞效果，中心暗
                pygame.draw.circle(glow_surf, (0, 0, 0, glow_alpha), (cx, cy - 8), int(glow_r))
            else:
                pygame.draw.circle(glow_surf, (*glow[:3], glow_alpha), (cx, cy - 8), int(glow_r))
            surf.blit(glow_surf, (0, 0))
    
    # ===== 【第二层】多层能量力场锥体（根据风格差异化）=====
    cone_layers = 10
    for layer in range(cone_layers):
        layer_prog = layer / cone_layers
        layer_y = cy - 8 - layer_prog * drill_length
        layer_r = drill_base_r * (1 - layer_prog * 0.88)
        
        ring_alpha = int(180 - layer * 15)
        ring_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
        
        # 根据风格调整段数
        if drill_style == "serrated":
            segments = 8  # 锯齿形
        elif drill_style == "prism":
            segments = 6  # 六棱柱
        elif drill_style == "organic":
            segments = 5  # 不规则
        else:
            segments = 12
        
        for seg in range(segments):
            seg_angle = rotation + seg * (math.pi * 2 / segments) + layer * 0.4
            seg_x = cx + math.cos(seg_angle) * layer_r
            seg_y = layer_y + math.sin(seg_angle) * layer_r * 0.45
            
            # 能量点大小（锯齿风格更大）
            seg_size = max(2, int(5 - layer * 0.4))
            if drill_style == "serrated":
                seg_size = max(3, int(6 - layer * 0.3))
            
            color = crystal_core if seg % 3 == 0 else (crystal_bright if seg % 2 == 0 else crystal)
            pygame.draw.circle(ring_surf, (*color[:3], ring_alpha), 
                              (int(seg_x), int(seg_y)), seg_size)
            
            # 锯齿风格额外尖刺
            if drill_style == "serrated" and seg % 2 == 0:
                spike_len = 6 - layer * 0.5
                spike_x = seg_x + math.cos(seg_angle) * spike_len
                spike_y = seg_y + math.sin(seg_angle) * spike_len * 0.5
                pygame.draw.line(ring_surf, (*crystal[:3], ring_alpha),
                               (int(seg_x), int(seg_y)), (int(spike_x), int(spike_y)), 2)
            
            # 棱镜风格连线
            if drill_style == "prism" and seg < segments:
                next_angle = rotation + (seg + 1) * (math.pi * 2 / segments) + layer * 0.4
                next_x = cx + math.cos(next_angle) * layer_r
                next_y = layer_y + math.sin(next_angle) * layer_r * 0.45
                pygame.draw.line(ring_surf, (*crystal[:3], ring_alpha // 2),
                               (int(seg_x), int(seg_y)), (int(next_x), int(next_y)), 1)
        
        surf.blit(ring_surf, (0, 0))
        ring_alpha = int(180 - layer * 15)
        ring_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
        
        # 绘制旋转的能量段
        segments = 12
        for seg in range(segments):
            seg_angle = rotation + seg * (math.pi * 2 / segments) + layer * 0.4
            seg_x = cx + math.cos(seg_angle) * layer_r
            seg_y = layer_y + math.sin(seg_angle) * layer_r * 0.45
            
            # 能量点
            seg_size = max(2, int(5 - layer * 0.4))
            color = crystal_core if seg % 3 == 0 else (crystal_bright if seg % 2 == 0 else crystal)
            pygame.draw.circle(ring_surf, (*color[:3], ring_alpha), 
                              (int(seg_x), int(seg_y)), seg_size)
            
            # 能量粒子拖尾
            if seg % 2 == 0:
                trail_angle = seg_angle - 0.3
                trail_x = cx + math.cos(trail_angle) * layer_r
                trail_y = layer_y + math.sin(trail_angle) * layer_r * 0.45
                pygame.draw.line(ring_surf, (*crystal[:3], ring_alpha // 2),
                               (int(seg_x), int(seg_y)), (int(trail_x), int(trail_y)), 1)
        
        surf.blit(ring_surf, (0, 0))
        
        # 层间连接螺旋线
        if layer > 0:
            spiral_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
            for spiral in range(4):
                s_angle = rotation * 1.5 + spiral * (math.pi / 2) + layer * 0.6
                prev_layer_prog = (layer - 1) / cone_layers
                prev_y = cy - 8 - prev_layer_prog * drill_length
                prev_r = drill_base_r * (1 - prev_layer_prog * 0.88)
                prev_x = cx + math.cos(s_angle - 0.6) * prev_r
                cur_x = cx + math.cos(s_angle) * layer_r
                pygame.draw.line(spiral_surf, (*crystal[:3], 60),
                               (int(prev_x), int(prev_y)), (int(cur_x), int(layer_y)), 1)
            surf.blit(spiral_surf, (0, 0))
    
    # ===== 【第三层】钻头金属骨架 =====
    frame_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    for rib in range(6):
        rib_angle = rotation * 0.5 + rib * (math.pi / 3)
        # 骨架从底座到尖端
        rib_base_x = cx + math.cos(rib_angle) * (drill_base_r - 2)
        rib_base_y = cy - 5 + math.sin(rib_angle) * (drill_base_r - 2) * 0.4
        rib_tip_x = cx + math.cos(rib_angle) * 2
        rib_tip_y = cy - 8 - drill_length - 8
        
        # 骨架主线
        pygame.draw.line(frame_surf, (*hull_light[:3], 200),
                        (int(rib_base_x), int(rib_base_y)),
                        (int(rib_tip_x), int(rib_tip_y)), 2)
        pygame.draw.line(frame_surf, (*hull_main[:3], 150),
                        (int(rib_base_x + 1), int(rib_base_y)),
                        (int(rib_tip_x + 1), int(rib_tip_y)), 1)
    surf.blit(frame_surf, (0, 0))
    
    # ===== 【第四层】钻头核心激光柱 =====
    laser_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    laser_pulse = 1.0 + math.sin(t * 12) * 0.25
    
    # 激光外层螺旋
    for spiral in range(2):
        for seg in range(6):
            seg_prog = seg / 6
            seg_y = cy - 8 - seg_prog * (drill_length + 10)
            seg_angle = rotation * 3 + seg * 0.8 + spiral * math.pi
            seg_r = 4 * (1 - seg_prog * 0.7) * laser_pulse
            seg_x = cx + math.cos(seg_angle) * seg_r
            pygame.draw.circle(laser_surf, (*laser[:3], 120), (int(seg_x), int(seg_y)), 2)
    
    # 外层激光
    pygame.draw.line(laser_surf, (*laser[:3], 200), 
                    (cx, cy - 8), (cx, cy - 8 - drill_length - 10), int(6 * laser_pulse))
    # 中层激光
    pygame.draw.line(laser_surf, (*crystal_bright[:3], 220), 
                    (cx, cy - 8), (cx, cy - 8 - drill_length - 10), int(4 * laser_pulse))
    # 核心激光
    pygame.draw.line(laser_surf, (*laser_core[:3], 255), 
                    (cx, cy - 8), (cx, cy - 8 - drill_length - 10), int(2 * laser_pulse))
    
    surf.blit(laser_surf, (0, 0))
    
    # ===== 【第五层】钻头尖端闪光系统 =====
    tip_y = cy - 8 - drill_length - 10
    tip_pulse = abs(math.sin(t * 10))
    tip_r = int(4 + tip_pulse * 3)
    
    # 多层光晕
    for i in range(4):
        tip_glow_r = tip_r + (4 - i) * 3
        tip_alpha = 150 - i * 35
        pygame.draw.circle(surf, (*laser_core[:3], tip_alpha), (cx, int(tip_y)), tip_glow_r)
    
    # 十字闪光
    cross_len = int(6 + tip_pulse * 5)
    cross_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    pygame.draw.line(cross_surf, (*laser_core[:3], 200),
                    (cx - cross_len, int(tip_y)), (cx + cross_len, int(tip_y)), 2)
    pygame.draw.line(cross_surf, (*laser_core[:3], 200),
                    (cx, int(tip_y - cross_len)), (cx, int(tip_y + cross_len * 0.5)), 2)
    surf.blit(cross_surf, (0, 0))
    
    # 核心亮点
    pygame.draw.circle(surf, laser_core, (cx, int(tip_y)), tip_r)
    pygame.draw.circle(surf, (255, 255, 255), (cx, int(tip_y)), max(2, tip_r - 2))
    
    # ===== 【第六层】多层旋转能量环 =====
    ring_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    for ring in range(4):
        ring_y = cy - 10 - ring * 7
        ring_r = drill_base_r - ring * 2
        ring_alpha = 120 - ring * 25
        ring_speed = 1 + ring * 0.15
        
        # 精细虚线环
        for seg in range(12):
            seg_angle = rotation * ring_speed + seg * (math.pi / 6)
            if seg % 2 == 0:
                sx = cx + math.cos(seg_angle) * ring_r
                sy = ring_y + math.sin(seg_angle) * ring_r * 0.5
                ex = cx + math.cos(seg_angle + 0.25) * ring_r
                ey = ring_y + math.sin(seg_angle + 0.25) * ring_r * 0.5
                line_width = 2 if ring < 2 else 1
                pygame.draw.line(ring_surf, (*crystal[:3], ring_alpha), 
                               (int(sx), int(sy)), (int(ex), int(ey)), line_width)
                
                # 节点亮点
                if seg % 4 == 0:
                    pygame.draw.circle(ring_surf, (*crystal_bright[:3], ring_alpha),
                                      (int(sx), int(sy)), 2)
    
    surf.blit(ring_surf, (0, 0))
    
    # ===== 【第七层】能量粒子喷射 =====
    particle_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    for p in range(6):
        p_phase = (t * 2 + p * 0.5) % 1.0
        p_y = tip_y - 3 - p_phase * 15
        p_angle = rotation * 2 + p * (math.pi / 3)
        p_r = 2 + p_phase * 5
        p_x = cx + math.cos(p_angle) * p_r
        p_alpha = int(150 * (1 - p_phase))
        p_size = max(1, int(2 * (1 - p_phase)))
        pygame.draw.circle(particle_surf, (*crystal_core[:3], p_alpha),
                          (int(p_x), int(p_y)), p_size)
    surf.blit(particle_surf, (0, 0))


def _draw_blocky_hull(surf, cx, cy, theme, t):
    """绘制精细块状厚重机身 - 多层装甲系统"""
    hull_main = theme["hull_main"]
    hull_light = theme["hull_light"]
    hull_dark = theme["hull_dark"]
    hull_edge = theme["hull_edge"]
    rivet = theme["rivet"]
    vent = theme["vent"]
    crystal = theme["crystal"]
    crystal_dark = theme["crystal_dark"]
    glow = theme["glow"]
    
    # ===== 【底层阴影投射】=====
    shadow_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    shadow_pts = [
        (cx - 32, cy + 8),
        (cx - 35, cy + 28),
        (cx - 26, cy + 45),
        (cx + 26, cy + 45),
        (cx + 35, cy + 28),
        (cx + 32, cy + 8),
    ]
    shadow_pts = [(int(p[0] + 3), int(p[1] + 3)) for p in shadow_pts]
    pygame.draw.polygon(shadow_surf, (0, 0, 0, 50), shadow_pts)
    surf.blit(shadow_surf, (0, 0))
    
    # ===== 【主体装甲外壳 - 三层结构】=====
    # 最外层轮廓（粗犷块状）
    body_outer = [
        (cx - 30, cy - 6),      # 左上
        (cx - 35, cy + 8),      # 左中上
        (cx - 33, cy + 28),     # 左中下
        (cx - 24, cy + 42),     # 左下
        (cx, cy + 46),          # 底部中心
        (cx + 24, cy + 42),     # 右下
        (cx + 33, cy + 28),     # 右中下
        (cx + 35, cy + 8),      # 右中上
        (cx + 30, cy - 6),      # 右上
        (cx + 20, cy - 3),      # 右上内
        (cx, cy),               # 顶部中心（钻头连接）
        (cx - 20, cy - 3),      # 左上内
    ]
    body_outer = [(int(p[0]), int(p[1])) for p in body_outer]
    pygame.draw.polygon(surf, hull_dark, body_outer)
    
    # 主装甲层
    body_main = [
        (cx - 27, cy - 3),
        (cx - 31, cy + 8),
        (cx - 29, cy + 25),
        (cx - 20, cy + 38),
        (cx, cy + 42),
        (cx + 20, cy + 38),
        (cx + 29, cy + 25),
        (cx + 31, cy + 8),
        (cx + 27, cy - 3),
        (cx + 17, cy),
        (cx, cy + 3),
        (cx - 17, cy),
    ]
    body_main = [(int(p[0]), int(p[1])) for p in body_main]
    pygame.draw.polygon(surf, hull_main, body_main)
    
    # 高光装甲层
    body_highlight = [
        (cx - 22, cy + 2),
        (cx - 24, cy + 12),
        (cx - 20, cy + 28),
        (cx - 12, cy + 34),
        (cx, cy + 36),
        (cx + 12, cy + 34),
        (cx + 20, cy + 28),
        (cx + 24, cy + 12),
        (cx + 22, cy + 2),
        (cx + 12, cy + 5),
        (cx, cy + 7),
        (cx - 12, cy + 5),
    ]
    body_highlight = [(int(p[0]), int(p[1])) for p in body_highlight]
    pygame.draw.polygon(surf, hull_light, body_highlight)
    
    # ===== 【装甲板分块 - 精细化】=====
    # 顶部三角形装甲板
    top_armor = [
        (cx - 18, cy + 2),
        (cx, cy + 5),
        (cx + 18, cy + 2),
        (cx, cy - 2),
    ]
    top_armor = [(int(p[0]), int(p[1])) for p in top_armor]
    pygame.draw.polygon(surf, hull_light, top_armor)
    pygame.draw.polygon(surf, hull_edge, top_armor, 1)
    
    # 左侧装甲板组
    left_plates = [
        [(cx - 28, cy + 5), (cx - 22, cy + 3), (cx - 20, cy + 15), (cx - 26, cy + 18)],
        [(cx - 26, cy + 20), (cx - 20, cy + 17), (cx - 18, cy + 30), (cx - 24, cy + 32)],
    ]
    for plate in left_plates:
        plate = [(int(p[0]), int(p[1])) for p in plate]
        pygame.draw.polygon(surf, hull_main, plate)
        pygame.draw.polygon(surf, hull_edge, plate, 1)
    
    # 右侧装甲板组
    right_plates = [
        [(cx + 28, cy + 5), (cx + 22, cy + 3), (cx + 20, cy + 15), (cx + 26, cy + 18)],
        [(cx + 26, cy + 20), (cx + 20, cy + 17), (cx + 18, cy + 30), (cx + 24, cy + 32)],
    ]
    for plate in right_plates:
        plate = [(int(p[0]), int(p[1])) for p in plate]
        pygame.draw.polygon(surf, hull_main, plate)
        pygame.draw.polygon(surf, hull_edge, plate, 1)
    
    # 中央装甲板
    center_plates = [
        [(cx - 12, cy + 10), (cx + 12, cy + 10), (cx + 10, cy + 22), (cx - 10, cy + 22)],
        [(cx - 8, cy + 24), (cx + 8, cy + 24), (cx + 6, cy + 35), (cx - 6, cy + 35)],
    ]
    for plate in center_plates:
        plate = [(int(p[0]), int(p[1])) for p in plate]
        pygame.draw.polygon(surf, hull_light, plate)
        pygame.draw.polygon(surf, hull_edge, plate, 1)
    
    # ===== 【边缘高亮线 - 多层】=====
    pygame.draw.polygon(surf, hull_edge, body_outer, 2)
    # 内边缘
    inner_edge = [
        (cx - 24, cy + 3),
        (cx - 27, cy + 12),
        (cx - 24, cy + 28),
        (cx - 16, cy + 38),
        (cx, cy + 40),
        (cx + 16, cy + 38),
        (cx + 24, cy + 28),
        (cx + 27, cy + 12),
        (cx + 24, cy + 3),
    ]
    inner_edge = [(int(p[0]), int(p[1])) for p in inner_edge]
    pygame.draw.lines(surf, hull_light, False, inner_edge, 1)
    
    # ===== 【装甲分块线 - 更多细节】=====
    # 横向分割线
    for i in range(5):
        line_y = cy + 6 + i * 8
        left_x = cx - 28 + i * 2
        right_x = cx + 28 - i * 2
        pygame.draw.line(surf, hull_edge, (left_x, line_y), (right_x, line_y), 1)
    
    # 纵向分割线
    pygame.draw.line(surf, hull_edge, (cx, cy + 5), (cx, cy + 38), 1)
    pygame.draw.line(surf, hull_edge, (cx - 10, cy + 8), (cx - 8, cy + 36), 1)
    pygame.draw.line(surf, hull_edge, (cx + 10, cy + 8), (cx + 8, cy + 36), 1)
    
    # ===== 【铆钉系统 - 精细化】=====
    rivet_positions = [
        # 外圈大铆钉
        (cx - 25, cy + 10), (cx + 25, cy + 10),
        (cx - 23, cy + 22), (cx + 23, cy + 22),
        (cx - 18, cy + 34), (cx + 18, cy + 34),
        # 中圈铆钉
        (cx - 14, cy + 8), (cx + 14, cy + 8),
        (cx - 12, cy + 20), (cx + 12, cy + 20),
        (cx - 10, cy + 32), (cx + 10, cy + 32),
        # 底部铆钉
        (cx - 6, cy + 40), (cx + 6, cy + 40),
    ]
    for rx, ry in rivet_positions:
        # 铆钉凹槽
        pygame.draw.circle(surf, hull_dark, (int(rx), int(ry)), 4)
        # 铆钉主体
        pygame.draw.circle(surf, rivet, (int(rx), int(ry)), 3)
        # 铆钉高光
        pygame.draw.circle(surf, hull_light, (int(rx - 1), int(ry - 1)), 1)
    
    # 小铆钉
    small_rivets = [
        (cx - 30, cy + 15), (cx + 30, cy + 15),
        (cx - 28, cy + 28), (cx + 28, cy + 28),
        (cx - 20, cy + 5), (cx + 20, cy + 5),
    ]
    for rx, ry in small_rivets:
        pygame.draw.circle(surf, hull_dark, (int(rx), int(ry)), 2)
        pygame.draw.circle(surf, rivet, (int(rx), int(ry)), 1)
    
    # ===== 【散热口系统 - 精细化】=====
    for side in [-1, 1]:
        vent_x = cx + side * 28
        for i in range(5):
            vent_y = cy + 10 + i * 5
            # 散热口凹槽
            pygame.draw.rect(surf, hull_dark, (int(vent_x - 5), int(vent_y - 2), 10, 3))
            # 散热口格栅
            pygame.draw.rect(surf, vent, (int(vent_x - 4), int(vent_y - 1), 8, 2))
            # 散热口内光
            if i % 2 == 0:
                vent_glow = pygame.Surface((8, 2), pygame.SRCALPHA)
                vent_glow.fill((*crystal[:3], 60))
                surf.blit(vent_glow, (int(vent_x - 4), int(vent_y - 1)))
    
    # ===== 【机身中央能量核心窗口】=====
    core_x, core_y = cx, cy + 16
    # 窗口外框
    pygame.draw.circle(surf, hull_dark, (core_x, core_y), 8)
    pygame.draw.circle(surf, hull_edge, (core_x, core_y), 7)
    # 能量核心
    pygame.draw.circle(surf, crystal_dark, (core_x, core_y), 5)
    pygame.draw.circle(surf, crystal, (core_x, core_y), 4)
    # 核心高光
    pygame.draw.circle(surf, (255, 255, 255), (core_x - 1, core_y - 1), 2)
    
    # ===== 【侧翼装甲突起】=====
    for side in [-1, 1]:
        wing_x = cx + side * 32
        wing_pts = [
            (wing_x, cy + 15),
            (wing_x + side * 6, cy + 18),
            (wing_x + side * 8, cy + 25),
            (wing_x + side * 5, cy + 32),
            (wing_x, cy + 30),
        ]
        wing_pts = [(int(p[0]), int(p[1])) for p in wing_pts]
        pygame.draw.polygon(surf, hull_main, wing_pts)
        pygame.draw.polygon(surf, hull_edge, wing_pts, 1)
        # 侧翼高光
        pygame.draw.line(surf, hull_light, 
                        (int(wing_x + side * 2), cy + 17),
                        (int(wing_x + side * 4), cy + 28), 1)


def _draw_charge_slots(surf, cx, cy, theme, t, charge_level=0):
    """绘制精细充能槽（电池式发光槽）"""
    crystal = theme["crystal"]
    crystal_bright = theme["crystal_bright"]
    crystal_core = theme["crystal_core"]
    charge_bar = theme["charge_bar"]
    hull_dark = theme["hull_dark"]
    hull_main = theme["hull_main"]
    hull_light = theme["hull_light"]
    hull_edge = theme["hull_edge"]
    glow = theme["glow"]
    
    max_slots = 5
    slot_height = 9
    slot_width = 7
    slot_gap = 2
    
    for side in [-1, 1]:
        base_x = cx + side * 38
        base_y = cy + 3
        
        # ===== 充能槽外壳框架 =====
        frame_height = max_slots * (slot_height + slot_gap) + 6
        frame_pts = [
            (base_x - slot_width // 2 - 3, base_y - 3),
            (base_x + slot_width // 2 + 3, base_y - 3),
            (base_x + slot_width // 2 + 4, base_y + frame_height),
            (base_x - slot_width // 2 - 4, base_y + frame_height),
        ]
        frame_pts = [(int(p[0]), int(p[1])) for p in frame_pts]
        pygame.draw.polygon(surf, hull_dark, frame_pts)
        pygame.draw.polygon(surf, hull_edge, frame_pts, 1)
        
        # 框架内边
        inner_frame = [
            (base_x - slot_width // 2 - 1, base_y),
            (base_x + slot_width // 2 + 1, base_y),
            (base_x + slot_width // 2 + 2, base_y + frame_height - 4),
            (base_x - slot_width // 2 - 2, base_y + frame_height - 4),
        ]
        inner_frame = [(int(p[0]), int(p[1])) for p in inner_frame]
        pygame.draw.polygon(surf, hull_main, inner_frame, 1)
        
        for i in range(max_slots):
            slot_y = base_y + 2 + i * (slot_height + slot_gap)
            
            # ===== 槽位背景（凹槽效果）=====
            pygame.draw.rect(surf, hull_dark, 
                           (int(base_x - slot_width // 2 - 1), int(slot_y - 1), 
                            slot_width + 2, slot_height + 2),
                           border_radius=2)
            pygame.draw.rect(surf, (0, 0, 0), 
                           (int(base_x - slot_width // 2), int(slot_y), slot_width, slot_height),
                           border_radius=1)
            
            # ===== 充能状态 =====
            filled = i < charge_level
            if filled:
                # 已充能 - 多层发光效果
                pulse = abs(math.sin(t * 6 + i * 0.5))
                
                # 外层光晕
                glow_surf = pygame.Surface((slot_width + 8, slot_height + 8), pygame.SRCALPHA)
                glow_alpha = int(60 + pulse * 40)
                pygame.draw.rect(glow_surf, (*glow[:3], glow_alpha),
                               (0, 0, slot_width + 8, slot_height + 8), border_radius=3)
                surf.blit(glow_surf, (int(base_x - slot_width // 2 - 4), int(slot_y - 4)))
                
                # 能量填充
                fill_color = tuple(min(255, c + int(60 * pulse)) for c in charge_bar)
                pygame.draw.rect(surf, fill_color,
                               (int(base_x - slot_width // 2 + 1), int(slot_y + 1), 
                                slot_width - 2, slot_height - 2),
                               border_radius=1)
                
                # 核心亮条
                pygame.draw.rect(surf, crystal_bright,
                               (int(base_x - slot_width // 2 + 2), int(slot_y + 2), 
                                slot_width - 4, 2),
                               border_radius=1)
                
                # 能量波动线
                wave_y = slot_y + slot_height // 2 + int(math.sin(t * 8 + i) * 2)
                pygame.draw.line(surf, crystal_core,
                               (int(base_x - slot_width // 2 + 2), int(wave_y)),
                               (int(base_x + slot_width // 2 - 2), int(wave_y)), 1)
            else:
                # 未充能 - 脉动暗光
                pulse = abs(math.sin(t * 3 + i * 0.3))
                glow_alpha = int(25 + pulse * 25)
                glow_surf = pygame.Surface((slot_width, slot_height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*crystal[:3], glow_alpha),
                               (0, 0, slot_width, slot_height), border_radius=2)
                surf.blit(glow_surf, (int(base_x - slot_width // 2), int(slot_y)))
                
                # 暗色网格线
                for grid in range(3):
                    grid_y = slot_y + 2 + grid * 3
                    pygame.draw.line(surf, (*hull_edge[:3], 60),
                                   (int(base_x - slot_width // 2 + 1), int(grid_y)),
                                   (int(base_x + slot_width // 2 - 1), int(grid_y)), 1)
            
            # ===== 边框 =====
            pygame.draw.rect(surf, crystal,
                           (int(base_x - slot_width // 2), int(slot_y), slot_width, slot_height),
                           1, border_radius=2)
        
        # ===== 充能槽指示灯 =====
        indicator_y = base_y + frame_height - 2
        indicator_pulse = abs(math.sin(t * 4))
        if charge_level >= max_slots:
            # 满充 - 闪烁
            ind_color = crystal_core if indicator_pulse > 0.5 else crystal_bright
        else:
            ind_color = crystal if charge_level > 0 else hull_edge
        pygame.draw.circle(surf, ind_color, (int(base_x), int(indicator_y)), 3)
        pygame.draw.circle(surf, hull_dark, (int(base_x), int(indicator_y)), 3, 1)


def _draw_crystal_decorations(surf, cx, cy, theme, t):
    """绘制精细镶嵌水晶装饰"""
    crystal = theme["crystal"]
    crystal_bright = theme["crystal_bright"]
    crystal_dark = theme["crystal_dark"]
    crystal_core = theme["crystal_core"]
    glow = theme["glow"]
    hull_dark = theme["hull_dark"]
    hull_edge = theme["hull_edge"]
    
    # ===== 主水晶簇位置（带镶嵌框架）=====
    cluster_positions = [
        (cx - 16, cy + 14, 5),   # 左侧
        (cx + 16, cy + 14, 5),   # 右侧
        (cx, cy + 26, 7),        # 中央（主水晶）
    ]
    
    for clx, cly, size in cluster_positions:
        # 水晶镶嵌框架
        frame_r = size + 4
        # 八边形框架
        frame_pts = []
        for i in range(8):
            fa = i * (math.pi / 4) + math.pi / 8
            fx = clx + math.cos(fa) * frame_r
            fy = cly + math.sin(fa) * frame_r * 0.8
            frame_pts.append((int(fx), int(fy)))
        pygame.draw.polygon(surf, hull_dark, frame_pts)
        pygame.draw.polygon(surf, hull_edge, frame_pts, 1)
        
        # 绘制水晶簇
        _draw_crystal_cluster(surf, int(clx), int(cly), theme, t, count=4, base_size=size)
        
        # 水晶光晕
        glow_alpha = int(50 + abs(math.sin(t * 4)) * 40)
        glow_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
        for g in range(4):
            g_r = size + 8 - g * 2
            g_alpha = glow_alpha - g * 12
            if g_alpha > 0:
                pygame.draw.circle(glow_surf, (*glow[:3], g_alpha), (int(clx), int(cly)), g_r)
        surf.blit(glow_surf, (0, 0))
    
    # ===== 小型装饰水晶（分布在机身各处）=====
    small_crystal_pos = [
        (cx - 24, cy + 8, 3),
        (cx + 24, cy + 8, 3),
        (cx - 18, cy + 32, 3),
        (cx + 18, cy + 32, 3),
        (cx, cy + 38, 4),
    ]
    
    for scx, scy, sc_size in small_crystal_pos:
        # 简化小水晶
        sc_pulse = 1.0 + math.sin(t * 5 + scx * 0.1) * 0.2
        sc_height = sc_size * 2 * sc_pulse
        
        # 水晶菱形
        sc_pts = [
            (scx, scy - sc_height),
            (scx - sc_size * 0.5, scy),
            (scx, scy + sc_size * 0.3),
            (scx + sc_size * 0.5, scy),
        ]
        sc_pts = [(int(p[0]), int(p[1])) for p in sc_pts]
        pygame.draw.polygon(surf, crystal_dark, sc_pts)
        
        # 高光面
        hl_pts = [sc_pts[0], sc_pts[1], sc_pts[2]]
        pygame.draw.polygon(surf, crystal, hl_pts)
        
        # 核心线
        pygame.draw.line(surf, crystal_bright, 
                        (int(scx), int(scy - sc_height)), 
                        (int(scx), int(scy + sc_size * 0.2)), 1)
        
        # 小光晕
        if abs(math.sin(t * 3 + scy * 0.1)) > 0.7:
            pygame.draw.circle(surf, (*crystal_core[:3], 100), (int(scx), int(scy)), sc_size)
    
    # ===== 能量导管装饰线 =====
    conduit_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    conduit_pulse = abs(math.sin(t * 4))
    conduit_alpha = int(80 + conduit_pulse * 60)
    
    # 左侧导管
    pygame.draw.line(conduit_surf, (*crystal[:3], conduit_alpha),
                    (cx - 16, cy + 14), (cx - 10, cy + 22), 2)
    pygame.draw.line(conduit_surf, (*crystal[:3], conduit_alpha),
                    (cx - 10, cy + 22), (cx, cy + 26), 2)
    
    # 右侧导管
    pygame.draw.line(conduit_surf, (*crystal[:3], conduit_alpha),
                    (cx + 16, cy + 14), (cx + 10, cy + 22), 2)
    pygame.draw.line(conduit_surf, (*crystal[:3], conduit_alpha),
                    (cx + 10, cy + 22), (cx, cy + 26), 2)
    
    # 导管节点
    for node_pos in [(cx - 10, cy + 22), (cx + 10, cy + 22)]:
        pygame.draw.circle(conduit_surf, (*crystal_bright[:3], conduit_alpha),
                          (int(node_pos[0]), int(node_pos[1])), 2)
    
    surf.blit(conduit_surf, (0, 0))


def _draw_engine_exhaust(surf, cx, cy, theme, t):
    """绘制差异化引擎尾焰系统"""
    crystal = theme["crystal"]
    crystal_bright = theme["crystal_bright"]
    crystal_dark = theme["crystal_dark"]
    crystal_core = theme["crystal_core"]
    laser = theme["laser"]
    glow = theme["glow"]
    hull_dark = theme["hull_dark"]
    hull_main = theme["hull_main"]
    hull_light = theme["hull_light"]
    hull_edge = theme["hull_edge"]
    
    # 获取差异化参数
    exhaust_style = theme.get("exhaust_style", "dual")
    spark_color = theme.get("spark_color", crystal_bright)
    
    exhaust_y = cy + 44
    
    # 双引擎结构
    for side in [-1, 1]:
        ex = cx + side * 14
        
        # ===== 引擎外壳结构 =====
        engine_pts = [
            (ex - 8, cy + 35),
            (ex + 8, cy + 35),
            (ex + 10, cy + 42),
            (ex + 8, cy + 48),
            (ex - 8, cy + 48),
            (ex - 10, cy + 42),
        ]
        engine_pts = [(int(p[0]), int(p[1])) for p in engine_pts]
        pygame.draw.polygon(surf, hull_dark, engine_pts)
        pygame.draw.polygon(surf, hull_main, engine_pts, 2)
        
        # 引擎内圈
        pygame.draw.circle(surf, hull_dark, (int(ex), int(cy + 44)), 7)
        pygame.draw.circle(surf, hull_edge, (int(ex), int(cy + 44)), 6)
        pygame.draw.circle(surf, (0, 0, 0), (int(ex), int(cy + 44)), 5)
        
        # 引擎格栅
        for g in range(3):
            g_angle = t * 4 + g * (math.pi * 2 / 3)
            gx1 = ex + math.cos(g_angle) * 4
            gy1 = cy + 44 + math.sin(g_angle) * 4
            gx2 = ex + math.cos(g_angle + math.pi) * 4
            gy2 = cy + 44 + math.sin(g_angle + math.pi) * 4
            pygame.draw.line(surf, hull_light, (int(gx1), int(gy1)), (int(gx2), int(gy2)), 1)
        
        # ===== 差异化尾焰效果 =====
        flame_wave = math.sin(t * 12 + side * 0.5)
        
        if exhaust_style == "flame":
            # 血晶：火焰尾焰 - 更猛烈
            flame_length = 30 + flame_wave * 15
            flame_width = 9 + abs(flame_wave) * 4
            _draw_flame_exhaust(surf, ex, exhaust_y, flame_length, flame_width, crystal, crystal_bright, crystal_dark, glow, flame_wave, t)
            
        elif exhaust_style == "frost":
            # 天穹：冰霜尾焰 - 更柔和
            flame_length = 22 + flame_wave * 6
            flame_width = 6 + abs(flame_wave) * 2
            _draw_frost_exhaust(surf, ex, exhaust_y, flame_length, flame_width, crystal, crystal_bright, crystal_core, glow, flame_wave, t)
            
        elif exhaust_style == "nature":
            # 翡翠：自然尾焰 - 波动
            flame_length = 20 + math.sin(t * 8 + side) * 10
            flame_width = 6 + abs(math.sin(t * 6)) * 3
            _draw_nature_exhaust(surf, ex, exhaust_y, flame_length, flame_width, crystal, crystal_bright, crystal_dark, glow, t, side)
            
        elif exhaust_style == "golden":
            # 黄金：金色尾焰 - 华丽
            flame_length = 28 + flame_wave * 8
            flame_width = 8 + abs(flame_wave) * 3
            _draw_golden_exhaust(surf, ex, exhaust_y, flame_length, flame_width, crystal, crystal_bright, crystal_core, glow, flame_wave, t)
            
        elif exhaust_style == "void":
            # 虚空：暗能量尾焰 - 诡异
            flame_length = 25 + math.sin(t * 5) * 12
            flame_width = 7 + abs(math.sin(t * 3)) * 4
            _draw_void_exhaust(surf, ex, exhaust_y, flame_length, flame_width, crystal, glow, t, side)
            
        else:
            # 默认：标准尾焰
            flame_length = 25 + flame_wave * 10
            flame_width = 7 + abs(flame_wave) * 3
            _draw_standard_exhaust(surf, ex, exhaust_y, flame_length, flame_width, crystal, crystal_bright, crystal_dark, laser, glow, flame_wave, t)
    
    # ===== 中央辅助推进器 =====
    pygame.draw.circle(surf, hull_dark, (cx, cy + 44), 5)
    pygame.draw.circle(surf, hull_edge, (cx, cy + 44), 4)
    pygame.draw.circle(surf, (0, 0, 0), (cx, cy + 44), 3)
    
    center_wave = math.sin(t * 10)
    center_length = 12 + center_wave * 4
    center_pts = [
        (cx - 3, cy + 46),
        (cx + 3, cy + 46),
        (cx + center_wave, cy + 46 + center_length),
    ]
    center_pts = [(int(p[0]), int(p[1])) for p in center_pts]
    pygame.draw.polygon(surf, crystal, center_pts)
    
    core_center = [
        (cx - 1, cy + 47),
        (cx + 1, cy + 47),
        (cx, cy + 46 + center_length * 0.8),
    ]
    core_center = [(int(p[0]), int(p[1])) for p in core_center]
    pygame.draw.polygon(surf, crystal_bright, core_center)


def _draw_standard_exhaust(surf, ex, exhaust_y, flame_length, flame_width, crystal, crystal_bright, crystal_dark, laser, glow, flame_wave, t):
    """标准尾焰"""
    # 外层光晕
    glow_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    for i in range(5):
        glow_r = int(flame_width + 10 - i * 2)
        glow_alpha = 60 - i * 12
        if glow_alpha > 0:
            pygame.draw.ellipse(glow_surf, (*glow[:3], glow_alpha),
                               (int(ex - glow_r), int(exhaust_y), glow_r * 2, int(flame_length * 0.8)))
    surf.blit(glow_surf, (0, 0))
    
    # 三层尾焰
    for flame_layer in range(3):
        layer_width = flame_width - flame_layer * 2
        layer_length = flame_length - flame_layer * 3
        layer_wave = flame_wave * (1 - flame_layer * 0.2)
        
        flame_pts = [
            (ex - layer_width, exhaust_y),
            (ex + layer_width, exhaust_y),
            (ex + layer_width * 0.6 + layer_wave * 2, exhaust_y + layer_length * 0.6),
            (ex + layer_wave * 4, exhaust_y + layer_length),
            (ex - layer_width * 0.6 + layer_wave * 2, exhaust_y + layer_length * 0.6),
        ]
        flame_pts = [(int(p[0]), int(p[1])) for p in flame_pts]
        
        if flame_layer == 0:
            pygame.draw.polygon(surf, crystal_dark, flame_pts)
        elif flame_layer == 1:
            pygame.draw.polygon(surf, crystal, flame_pts)
        else:
            pygame.draw.polygon(surf, crystal_bright, flame_pts)
    
    # 核心亮焰
    core_pts = [
        (ex - 2, exhaust_y + 3),
        (ex + 2, exhaust_y + 3),
        (ex + flame_wave * 2, exhaust_y + flame_length * 0.85),
    ]
    core_pts = [(int(p[0]), int(p[1])) for p in core_pts]
    pygame.draw.polygon(surf, laser, core_pts)


def _draw_flame_exhaust(surf, ex, exhaust_y, flame_length, flame_width, crystal, crystal_bright, crystal_dark, glow, flame_wave, t):
    """火焰尾焰（血晶涂装）"""
    # 强烈光晕
    glow_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    for i in range(6):
        glow_r = int(flame_width + 12 - i * 2)
        glow_alpha = 80 - i * 12
        if glow_alpha > 0:
            pygame.draw.ellipse(glow_surf, (*glow[:3], glow_alpha),
                               (int(ex - glow_r), int(exhaust_y - 3), glow_r * 2, int(flame_length)))
    surf.blit(glow_surf, (0, 0))
    
    # 猛烈火焰（多尖）
    for spike in range(3):
        spike_offset = (spike - 1) * 4
        spike_length = flame_length * (1 - abs(spike - 1) * 0.2)
        spike_wave = math.sin(t * 15 + spike) * 3
        
        flame_pts = [
            (ex - flame_width * 0.6 + spike_offset, exhaust_y),
            (ex + flame_width * 0.6 + spike_offset, exhaust_y),
            (ex + spike_offset + spike_wave, exhaust_y + spike_length),
        ]
        flame_pts = [(int(p[0]), int(p[1])) for p in flame_pts]
        pygame.draw.polygon(surf, crystal, flame_pts)
    
    # 内核
    core_pts = [
        (ex - 3, exhaust_y + 2),
        (ex + 3, exhaust_y + 2),
        (ex + flame_wave, exhaust_y + flame_length * 0.7),
    ]
    core_pts = [(int(p[0]), int(p[1])) for p in core_pts]
    pygame.draw.polygon(surf, crystal_bright, core_pts)


def _draw_frost_exhaust(surf, ex, exhaust_y, flame_length, flame_width, crystal, crystal_bright, crystal_core, glow, flame_wave, t):
    """冰霜尾焰（天穹涂装）"""
    # 柔和冰晶光晕
    glow_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    for i in range(4):
        glow_r = int(flame_width + 8 - i * 2)
        glow_alpha = 50 - i * 10
        if glow_alpha > 0:
            pygame.draw.ellipse(glow_surf, (*glow[:3], glow_alpha),
                               (int(ex - glow_r), int(exhaust_y), glow_r * 2, int(flame_length * 0.9)))
    surf.blit(glow_surf, (0, 0))
    
    # 冰晶形态（六边形散布）
    for i in range(6):
        ice_phase = (t * 3 + i * 0.5) % 1.0
        ice_y = exhaust_y + ice_phase * flame_length
        ice_angle = t * 4 + i * (math.pi / 3)
        ice_r = flame_width * 0.4 * (1 - ice_phase * 0.5)
        ice_x = ex + math.cos(ice_angle) * ice_r
        ice_alpha = int(150 * (1 - ice_phase))
        ice_size = max(1, int(3 * (1 - ice_phase)))
        
        pygame.draw.circle(surf, (*crystal_core[:3], ice_alpha), (int(ice_x), int(ice_y)), ice_size)
    
    # 冰柱核心
    flame_pts = [
        (ex - flame_width * 0.5, exhaust_y),
        (ex + flame_width * 0.5, exhaust_y),
        (ex, exhaust_y + flame_length),
    ]
    flame_pts = [(int(p[0]), int(p[1])) for p in flame_pts]
    pygame.draw.polygon(surf, crystal_bright, flame_pts)


def _draw_nature_exhaust(surf, ex, exhaust_y, flame_length, flame_width, crystal, crystal_bright, crystal_dark, glow, t, side):
    """自然尾焰（翡翠涂装）"""
    # 波动光晕
    glow_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    for i in range(4):
        glow_r = int(flame_width + 6 - i * 1.5)
        glow_alpha = 45 - i * 10
        if glow_alpha > 0:
            pygame.draw.ellipse(glow_surf, (*glow[:3], glow_alpha),
                               (int(ex - glow_r), int(exhaust_y), glow_r * 2, int(flame_length * 0.8)))
    surf.blit(glow_surf, (0, 0))
    
    # 藤蔓状波动火焰
    vine_pts = [(ex, exhaust_y)]
    for seg in range(6):
        seg_prog = (seg + 1) / 6
        seg_y = exhaust_y + seg_prog * flame_length
        wave = math.sin(t * 6 + seg + side) * flame_width * 0.3
        vine_pts.append((int(ex + wave), int(seg_y)))
    vine_pts.append((ex, exhaust_y + flame_length))
    
    # 绘制藤蔓
    for i in range(len(vine_pts) - 1):
        pygame.draw.line(surf, crystal, vine_pts[i], vine_pts[i + 1], 3)
        pygame.draw.line(surf, crystal_bright, vine_pts[i], vine_pts[i + 1], 1)


def _draw_golden_exhaust(surf, ex, exhaust_y, flame_length, flame_width, crystal, crystal_bright, crystal_core, glow, flame_wave, t):
    """金色尾焰（黄金涂装）"""
    # 华丽光晕
    glow_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    for i in range(5):
        glow_r = int(flame_width + 10 - i * 2)
        glow_alpha = 70 - i * 12
        if glow_alpha > 0:
            pygame.draw.ellipse(glow_surf, (*glow[:3], glow_alpha),
                               (int(ex - glow_r), int(exhaust_y - 2), glow_r * 2, int(flame_length * 0.85)))
    surf.blit(glow_surf, (0, 0))
    
    # 皇家火焰（优雅曲线）
    flame_pts = [
        (ex - flame_width, exhaust_y),
        (ex + flame_width, exhaust_y),
        (ex + flame_width * 0.5 + flame_wave, exhaust_y + flame_length * 0.5),
        (ex + flame_wave * 2, exhaust_y + flame_length),
        (ex - flame_width * 0.5 + flame_wave, exhaust_y + flame_length * 0.5),
    ]
    flame_pts = [(int(p[0]), int(p[1])) for p in flame_pts]
    pygame.draw.polygon(surf, crystal, flame_pts)
    
    # 金色闪光粒子
    for i in range(4):
        p_phase = (t * 4 + i * 0.5) % 1.0
        p_y = exhaust_y + p_phase * flame_length * 0.8
        p_alpha = int(200 * (1 - p_phase))
        pygame.draw.circle(surf, (*crystal_core[:3], p_alpha), (int(ex), int(p_y)), 2)
    
    # 核心
    core_pts = [
        (ex - 2, exhaust_y + 3),
        (ex + 2, exhaust_y + 3),
        (ex, exhaust_y + flame_length * 0.8),
    ]
    core_pts = [(int(p[0]), int(p[1])) for p in core_pts]
    pygame.draw.polygon(surf, crystal_bright, core_pts)


def _draw_void_exhaust(surf, ex, exhaust_y, flame_length, flame_width, crystal, glow, t, side):
    """虚空尾焰（虚空涂装）"""
    # 暗能量波动（反向光晕）
    glow_surf = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    for i in range(4):
        glow_r = int(flame_width + 8 - i * 2)
        glow_alpha = 40 - i * 8
        if glow_alpha > 0:
            # 黑色核心向外渐变
            pygame.draw.ellipse(glow_surf, (0, 0, 0, glow_alpha),
                               (int(ex - glow_r), int(exhaust_y), glow_r * 2, int(flame_length * 0.7)))
    surf.blit(glow_surf, (0, 0))
    
    # 虚空裂隙效果
    rift_alpha = int(120 + math.sin(t * 5) * 50)
    for seg in range(5):
        seg_phase = (t * 2 + seg * 0.4 + side * 0.3) % 1.0
        seg_y = exhaust_y + seg_phase * flame_length
        seg_width = flame_width * (1 - seg_phase * 0.6)
        
        # 白色裂隙线
        pygame.draw.line(surf, (*crystal[:3], int(rift_alpha * (1 - seg_phase))),
                        (int(ex - seg_width), int(seg_y)),
                        (int(ex + seg_width), int(seg_y)), 1)
    
    # 中心白线
    pygame.draw.line(surf, (*crystal[:3], 180),
                    (ex, exhaust_y + 2),
                    (ex, int(exhaust_y + flame_length * 0.9)), 2)


# =============================================================================
#   威压效果系统
# =============================================================================

def _draw_pressure_aura(surf, cx, cy, theme, t):
    """绘制差异化威压光环"""
    crystal = theme["crystal"]
    crystal_dark = theme["crystal_dark"]
    crystal_bright = theme["crystal_bright"]
    glow = theme["glow"]
    
    # 获取差异化参数
    aura_style = theme.get("aura_style", "hex")
    
    doom_pulse = abs(math.sin(t * 2))
    size = surf.get_width()
    
    # ===== 深渊压迫背景 =====
    void_color = (15, 5, 25)
    for layer in range(5):
        doom_r = size * (0.50 - layer * 0.05) + math.sin(t * 0.8 + layer) * 5
        doom_alpha = int((50 - layer * 10) * doom_pulse)
        if doom_alpha > 0:
            pygame.draw.circle(surf, (*void_color, doom_alpha), (cx, cy), int(doom_r))
    
    # ===== 差异化光环效果 =====
    if aura_style == "pulse":
        # 血晶：脉冲波纹 - 强烈冲击波
        _draw_pulse_aura(surf, cx, cy, size, crystal, crystal_dark, crystal_bright, glow, t, doom_pulse)
        
    elif aura_style == "snowflake":
        # 天穹：雪花光环 - 六边形冰晶
        _draw_snowflake_aura(surf, cx, cy, size, crystal, crystal_dark, crystal_bright, glow, t, doom_pulse)
        
    elif aura_style == "vine":
        # 翡翠：藤蔓光环 - 自然波动
        _draw_vine_aura(surf, cx, cy, size, crystal, crystal_dark, crystal_bright, glow, t, doom_pulse)
        
    elif aura_style == "crown":
        # 黄金：皇冠光环 - 华丽辐射
        _draw_crown_aura(surf, cx, cy, size, crystal, crystal_dark, crystal_bright, glow, t, doom_pulse)
        
    elif aura_style == "rift":
        # 虚空：裂隙光环 - 暗能量
        _draw_rift_aura(surf, cx, cy, size, crystal, crystal_dark, crystal_bright, glow, t, doom_pulse)
        
    else:
        # 默认：六边形光环
        _draw_hex_aura(surf, cx, cy, size, crystal, crystal_dark, crystal_bright, glow, t, doom_pulse)
    
    # ===== 暗角效果 =====
    corner_alpha = int(55 * doom_pulse)
    for corner_x, corner_y in [(0, 0), (size, 0), (0, size), (size, size)]:
        for i in range(6):
            corner_r = int(size * 0.30 - i * size * 0.04)
            c_alpha = corner_alpha - i * 9
            if c_alpha > 0 and corner_r > 0:
                pygame.draw.circle(surf, (0, 0, 0, c_alpha), (corner_x, corner_y), corner_r)


def _draw_hex_aura(surf, cx, cy, size, crystal, crystal_dark, crystal_bright, glow, t, doom_pulse):
    """默认六边形光环（原色涂装）"""
    # 紫色恐惧涟漪
    for ring in range(6):
        ripple_phase = (t * 0.35 + ring * 0.18) % 1.0
        ripple_r = size * 0.10 + ripple_phase * size * 0.42
        ripple_alpha = int(70 * (1 - ripple_phase))
        if ripple_alpha > 5:
            pygame.draw.circle(surf, (*crystal[:3], ripple_alpha), (cx, cy), int(ripple_r), 2)
    
    # 能量光晕脉动
    for i in range(6):
        glow_r = int(size * 0.44 - i * size * 0.045 + 5 * math.sin(t * 1.5 + i * 0.3))
        glow_alpha = max(0, int(35 * doom_pulse) - i * 5)
        if glow_r > 0 and glow_alpha > 0:
            pygame.draw.circle(surf, (*glow[:3], glow_alpha), (cx, cy), glow_r)
    
    # 六边形几何
    for hex_layer in range(2):
        hex_r = size * (0.38 - hex_layer * 0.08) + math.sin(t * 1.2 + hex_layer) * 4
        hex_alpha = int((50 - hex_layer * 15) * doom_pulse)
        hex_rotation = t * (8 + hex_layer * 4)
        
        hex_pts = []
        for i in range(6):
            angle = math.radians(i * 60 + 30 + hex_rotation)
            hx = cx + math.cos(angle) * hex_r
            hy = cy + math.sin(angle) * hex_r * 0.85
            hex_pts.append((int(hx), int(hy)))
        
        pygame.draw.polygon(surf, (*crystal[:3], hex_alpha), hex_pts, 2)
        for pt in hex_pts:
            if hex_layer == 0:
                pygame.draw.circle(surf, (*crystal_bright[:3], hex_alpha), pt, 2)


def _draw_pulse_aura(surf, cx, cy, size, crystal, crystal_dark, crystal_bright, glow, t, doom_pulse):
    """脉冲波纹光环（血晶涂装）"""
    # 强烈冲击波涟漪
    for ring in range(8):
        ripple_phase = (t * 0.5 + ring * 0.12) % 1.0
        ripple_r = size * 0.08 + ripple_phase * size * 0.48
        ripple_alpha = int(90 * (1 - ripple_phase))
        thickness = max(1, int(3 * (1 - ripple_phase)))
        if ripple_alpha > 5:
            pygame.draw.circle(surf, (*crystal[:3], ripple_alpha), (cx, cy), int(ripple_r), thickness)
    
    # 中心脉动核心
    core_r = size * 0.12 + doom_pulse * size * 0.05
    for i in range(3):
        c_r = int(core_r - i * 4)
        c_alpha = int((80 - i * 20) * doom_pulse)
        if c_r > 0 and c_alpha > 0:
            pygame.draw.circle(surf, (*crystal_bright[:3], c_alpha), (cx, cy), c_r)


def _draw_snowflake_aura(surf, cx, cy, size, crystal, crystal_dark, crystal_bright, glow, t, doom_pulse):
    """雪花光环（天穹涂装）"""
    # 六角冰晶涟漪
    for ring in range(5):
        ripple_phase = (t * 0.25 + ring * 0.2) % 1.0
        ripple_r = size * 0.12 + ripple_phase * size * 0.38
        ripple_alpha = int(60 * (1 - ripple_phase))
        
        if ripple_alpha > 5:
            # 六角形涟漪
            hex_pts = []
            for i in range(6):
                angle = i * (math.pi / 3) + t * 0.5
                hx = cx + math.cos(angle) * ripple_r
                hy = cy + math.sin(angle) * ripple_r * 0.85
                hex_pts.append((int(hx), int(hy)))
            pygame.draw.polygon(surf, (*crystal[:3], ripple_alpha), hex_pts, 1)
    
    # 雪花臂
    for arm in range(6):
        arm_angle = arm * (math.pi / 3) + t * 0.3
        arm_length = size * 0.35 + math.sin(t * 2 + arm) * 5
        arm_alpha = int(50 * doom_pulse)
        
        end_x = cx + math.cos(arm_angle) * arm_length
        end_y = cy + math.sin(arm_angle) * arm_length * 0.85
        
        pygame.draw.line(surf, (*crystal[:3], arm_alpha), (cx, cy), (int(end_x), int(end_y)), 1)
        
        # 分叉
        for branch in [-1, 1]:
            branch_angle = arm_angle + branch * 0.5
            branch_len = arm_length * 0.4
            mid_x = cx + math.cos(arm_angle) * arm_length * 0.6
            mid_y = cy + math.sin(arm_angle) * arm_length * 0.6 * 0.85
            branch_end_x = mid_x + math.cos(branch_angle) * branch_len
            branch_end_y = mid_y + math.sin(branch_angle) * branch_len * 0.85
            pygame.draw.line(surf, (*crystal[:3], arm_alpha // 2), 
                           (int(mid_x), int(mid_y)), (int(branch_end_x), int(branch_end_y)), 1)


def _draw_vine_aura(surf, cx, cy, size, crystal, crystal_dark, crystal_bright, glow, t, doom_pulse):
    """藤蔓光环（翡翠涂装）"""
    # 波动涟漪
    for ring in range(5):
        ripple_phase = (t * 0.3 + ring * 0.2) % 1.0
        base_r = size * 0.10 + ripple_phase * size * 0.40
        ripple_alpha = int(55 * (1 - ripple_phase))
        
        if ripple_alpha > 5:
            # 波浪形涟漪
            wave_pts = []
            for i in range(24):
                angle = i * (math.pi / 12)
                wave = math.sin(angle * 3 + t * 4) * 5
                r = base_r + wave
                wx = cx + math.cos(angle) * r
                wy = cy + math.sin(angle) * r * 0.85
                wave_pts.append((int(wx), int(wy)))
            pygame.draw.polygon(surf, (*crystal[:3], ripple_alpha), wave_pts, 1)
    
    # 藤蔓卷须
    for vine in range(4):
        vine_angle = vine * (math.pi / 2) + t * 0.8
        for seg in range(8):
            seg_prog = seg / 8
            seg_r = size * 0.15 + seg_prog * size * 0.25
            wave = math.sin(t * 3 + seg * 0.8 + vine) * 8
            seg_angle = vine_angle + wave * 0.02
            
            vx = cx + math.cos(seg_angle) * seg_r
            vy = cy + math.sin(seg_angle) * seg_r * 0.85
            
            point_alpha = int(50 * doom_pulse * (1 - seg_prog * 0.5))
            point_size = max(1, int(3 * (1 - seg_prog)))
            pygame.draw.circle(surf, (*crystal[:3], point_alpha), (int(vx), int(vy)), point_size)


def _draw_crown_aura(surf, cx, cy, size, crystal, crystal_dark, crystal_bright, glow, t, doom_pulse):
    """皇冠光环（黄金涂装）"""
    # 华丽涟漪
    for ring in range(5):
        ripple_phase = (t * 0.35 + ring * 0.18) % 1.0
        ripple_r = size * 0.12 + ripple_phase * size * 0.40
        ripple_alpha = int(65 * (1 - ripple_phase))
        if ripple_alpha > 5:
            pygame.draw.circle(surf, (*crystal[:3], ripple_alpha), (cx, cy), int(ripple_r), 2)
    
    # 皇冠辐射
    for ray in range(12):
        ray_angle = ray * (math.pi / 6) + t * 1.5
        ray_length = size * 0.38 + math.sin(t * 2.5 + ray) * 8
        ray_alpha = int(55 * doom_pulse)
        
        ray_x = cx + math.cos(ray_angle) * ray_length
        ray_y = cy + math.sin(ray_angle) * ray_length * 0.85
        
        pygame.draw.line(surf, (*crystal[:3], ray_alpha), (cx, cy), (int(ray_x), int(ray_y)), 1)
        
        # 射线顶端宝石
        if ray % 2 == 0:
            pygame.draw.circle(surf, (*crystal_bright[:3], ray_alpha), (int(ray_x), int(ray_y)), 2)
    
    # 中心皇冠光芒
    for i in range(4):
        crown_r = int(size * 0.10 - i * 3 + math.sin(t * 3) * 3)
        crown_alpha = int((70 - i * 15) * doom_pulse)
        if crown_r > 0 and crown_alpha > 0:
            pygame.draw.circle(surf, (*glow[:3], crown_alpha), (cx, cy), crown_r)


def _draw_rift_aura(surf, cx, cy, size, crystal, crystal_dark, crystal_bright, glow, t, doom_pulse):
    """裂隙光环（虚空涂装）"""
    # 黑暗吞噬
    for layer in range(4):
        void_r = size * (0.45 - layer * 0.08) + math.sin(t * 0.6 + layer) * 4
        void_alpha = int((35 - layer * 8) * doom_pulse)
        if void_alpha > 0:
            pygame.draw.circle(surf, (0, 0, 0, void_alpha), (cx, cy), int(void_r))
    
    # 空间裂隙线
    for rift in range(6):
        rift_angle = rift * (math.pi / 3) + t * 0.4
        rift_length = size * 0.42 + math.sin(t * 1.5 + rift * 2) * 12
        rift_alpha = int(80 * doom_pulse)
        
        # 锯齿状裂隙
        prev_x, prev_y = cx, cy
        for seg in range(5):
            seg_prog = (seg + 1) / 5
            seg_r = seg_prog * rift_length
            jitter = math.sin(t * 8 + seg + rift) * 6
            seg_x = cx + math.cos(rift_angle + jitter * 0.1) * seg_r
            seg_y = cy + math.sin(rift_angle + jitter * 0.1) * seg_r * 0.85
            
            seg_alpha = int(rift_alpha * (1 - seg_prog * 0.4))
            pygame.draw.line(surf, (*crystal[:3], seg_alpha), 
                           (int(prev_x), int(prev_y)), (int(seg_x), int(seg_y)), 1)
            prev_x, prev_y = seg_x, seg_y
    
    # 中心虚空核心
    void_core_r = int(size * 0.08 + math.sin(t * 2) * 3)
    pygame.draw.circle(surf, (0, 0, 0, 100), (cx, cy), void_core_r + 3)
    pygame.draw.circle(surf, (*crystal[:3], int(120 * doom_pulse)), (cx, cy), void_core_r, 1)


def _draw_top_effects(surf, cx, cy, theme, t):
    """绘制差异化顶层动态效果"""
    crystal = theme["crystal"]
    crystal_bright = theme["crystal_bright"]
    crystal_core = theme["crystal_core"]
    laser = theme["laser"]
    laser_core = theme["laser_core"]
    glow = theme["glow"]
    
    # 获取差异化参数
    spark_color = theme.get("spark_color", crystal_core)
    drip_effect = theme.get("drip_effect", False)
    frost_effect = theme.get("frost_effect", False)
    vine_effect = theme.get("vine_effect", False)
    crown_effect = theme.get("crown_effect", False)
    rift_effect = theme.get("rift_effect", False)
    invert_glow = theme.get("invert_glow", False)
    
    doom_pulse = abs(math.sin(t * 2.5))
    size = surf.get_width()
    
    top_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # ===== 钻头射线威压（多层） =====
    beam_length = size * 0.30 + math.sin(t * 4) * 8
    beam_alpha = int(110 + doom_pulse * 90)
    
    # 根据invert_glow调整光柱颜色
    if invert_glow:
        # 虚空涂装：白色核心，黑色边缘
        beam_outer = (30, 30, 30)
        beam_inner = (220, 220, 255)
    else:
        beam_outer = laser
        beam_inner = laser_core
    
    # 光柱外晕
    for b in range(3):
        b_width = 8 - b * 2
        b_alpha = beam_alpha // (b + 2)
        pygame.draw.line(top_surf, (*beam_outer[:3], b_alpha), 
                        (cx, cy - 46), (cx, int(cy - 46 - beam_length)), b_width)
    
    # 光柱螺旋纹理
    for spiral in range(2):
        for seg in range(4):
            seg_prog = seg / 4
            seg_y = cy - 46 - seg_prog * beam_length
            seg_angle = t * 6 + seg * 1.0 + spiral * math.pi
            seg_r = 3 * (1 - seg_prog * 0.5)
            seg_x = cx + math.cos(seg_angle) * seg_r
            pygame.draw.circle(top_surf, (*crystal_bright[:3], 80),
                              (int(seg_x), int(seg_y)), 2)
    
    # 光柱核心
    pygame.draw.line(top_surf, (*beam_inner[:3], beam_alpha), 
                    (cx, cy - 46), (cx, int(cy - 46 - beam_length)), 3)
    
    # 尖端闪光系统
    tip_y = cy - 46 - beam_length
    pygame.draw.circle(top_surf, (255, 255, 255, beam_alpha), (cx, int(tip_y)), 5)
    pygame.draw.circle(top_surf, (255, 255, 255, beam_alpha // 2), (cx, int(tip_y)), 8)
    
    # 尖端十字光芒
    cross_len = int(10 + doom_pulse * 6)
    pygame.draw.line(top_surf, (255, 255, 255, 150),
                    (cx - cross_len, int(tip_y)), (cx + cross_len, int(tip_y)), 2)
    pygame.draw.line(top_surf, (255, 255, 255, 150),
                    (cx, int(tip_y - cross_len * 0.6)), (cx, int(tip_y + cross_len * 0.3)), 2)
    
    # ===== 能量脉冲波（多层） =====
    for i in range(4):
        pulse_phase = (t * 0.5 + i * 0.25) % 1.0
        pulse_r = size * 0.06 + pulse_phase * size * 0.28
        pulse_alpha = int(90 * (1 - pulse_phase) * doom_pulse)
        if pulse_alpha > 5:
            pygame.draw.circle(top_surf, (*crystal[:3], pulse_alpha), (cx, cy), int(pulse_r), 2)
    
    # ===== 差异化特殊效果 =====
    if drip_effect:
        # 血晶：滴落效果
        for drip in range(3):
            drip_phase = (t * 1.5 + drip * 0.8) % 1.0
            drip_x = cx - 15 + drip * 15
            drip_y = cy + 30 + drip_phase * 20
            drip_alpha = int(120 * (1 - drip_phase))
            drip_size = max(1, int(3 * (1 - drip_phase * 0.5)))
            pygame.draw.circle(top_surf, (*crystal[:3], drip_alpha), (int(drip_x), int(drip_y)), drip_size)
    
    if frost_effect:
        # 天穹：冰霜粒子
        for frost in range(4):
            frost_phase = (t * 2 + frost * 0.6) % 1.0
            frost_angle = frost * (math.pi / 2) + t * 1.5
            frost_r = 25 + frost_phase * 15
            frost_x = cx + math.cos(frost_angle) * frost_r
            frost_y = cy + math.sin(frost_angle) * frost_r * 0.7
            frost_alpha = int(100 * (1 - frost_phase))
            pygame.draw.circle(top_surf, (*crystal_bright[:3], frost_alpha), (int(frost_x), int(frost_y)), 2)
    
    if vine_effect:
        # 翡翠：藤蔓粒子
        for vine in range(3):
            vine_phase = (t * 1.2 + vine * 1.0) % 1.0
            wave = math.sin(t * 4 + vine) * 10
            vine_x = cx - 20 + vine * 20 + wave
            vine_y = cy + 25 + vine_phase * 25
            vine_alpha = int(100 * (1 - vine_phase))
            pygame.draw.circle(top_surf, (*crystal[:3], vine_alpha), (int(vine_x), int(vine_y)), 2)
    
    if crown_effect:
        # 黄金：皇冠粒子
        for crown in range(5):
            crown_angle = crown * (math.pi * 2 / 5) + t * 2
            crown_r = 28 + math.sin(t * 3 + crown) * 5
            crown_x = cx + math.cos(crown_angle) * crown_r
            crown_y = cy + math.sin(crown_angle) * crown_r * 0.6
            crown_alpha = int(150 * doom_pulse)
            pygame.draw.circle(top_surf, (*spark_color[:3], crown_alpha), (int(crown_x), int(crown_y)), 2)
    
    if rift_effect:
        # 虚空：裂隙闪烁
        for rift in range(4):
            rift_phase = (t * 0.8 + rift * 0.5) % 1.0
            rift_angle = rift * (math.pi / 2) + math.sin(t * 2) * 0.3
            rift_r = 20 + rift_phase * 20
            rift_x = cx + math.cos(rift_angle) * rift_r
            rift_y = cy + math.sin(rift_angle) * rift_r * 0.7
            rift_alpha = int(80 + math.sin(t * 8 + rift) * 40)
            pygame.draw.line(top_surf, (*crystal[:3], rift_alpha),
                           (int(rift_x - 4), int(rift_y)), (int(rift_x + 4), int(rift_y)), 1)
    
    # ===== 水晶闪烁系统 =====
    crystal_flash = int(200 + math.sin(t * 6) * 55)
    crystal_positions = [
        (cx - 16, cy + 14), (cx + 16, cy + 14), (cx, cy + 26),
        (cx - 24, cy + 8), (cx + 24, cy + 8),
    ]
    for idx, (pos_x, pos_y) in enumerate(crystal_positions):
        flash_phase = math.sin(t * 8 + idx * 0.8)
        if flash_phase > 0.3:
            flash_alpha = int(crystal_flash * flash_phase)
            pygame.draw.circle(top_surf, (255, 255, 255, flash_alpha), 
                              (int(pos_x), int(pos_y)), 4)
            pygame.draw.circle(top_surf, (*crystal_core[:3], flash_alpha // 2), 
                              (int(pos_x), int(pos_y)), 7)
    
    # ===== 机身边缘能量流 =====
    edge_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    edge_pulse = abs(math.sin(t * 3))
    edge_alpha = int(60 + edge_pulse * 40)
    
    # 左侧边缘流
    for e in range(4):
        e_phase = (t * 2 + e * 0.3) % 1.0
        e_y = cy + e_phase * 40
        e_x = cx - 30 + e_phase * 3
        pygame.draw.circle(edge_surf, (*crystal[:3], int(edge_alpha * (1 - e_phase))),
                          (int(e_x), int(e_y)), 2)
    
    # 右侧边缘流
    for e in range(4):
        e_phase = (t * 2 + e * 0.3 + 0.5) % 1.0
        e_y = cy + e_phase * 40
        e_x = cx + 30 - e_phase * 3
        pygame.draw.circle(edge_surf, (*crystal[:3], int(edge_alpha * (1 - e_phase))),
                          (int(e_x), int(e_y)), 2)
    
    surf.blit(edge_surf, (0, 0))
    surf.blit(top_surf, (0, 0))
    
    # ===== 随机能量火花（使用差异化颜色） =====
    spark_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    for spark in range(3):
        spark_phase = (t * 4 + spark * 1.5) % 3.0
        if spark_phase < 1.0:
            spark_angle = spark * 2.1 + t * 0.5
            spark_dist = 20 + spark_phase * 25
            spark_x = cx + math.cos(spark_angle) * spark_dist
            spark_y = cy + math.sin(spark_angle) * spark_dist * 0.7
            spark_alpha = int(150 * (1 - spark_phase))
            pygame.draw.circle(spark_surf, (*spark_color[:3], spark_alpha),
                              (int(spark_x), int(spark_y)), 2)
    surf.blit(spark_surf, (0, 0))


# =============================================================================
#   主绘制函数
# =============================================================================

_cache = {}


def _build_cache(size, style):
    """预渲染静态部分"""
    theme = get_crusher_theme(style)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    
    # 绘制静态机身（包含所有细节）
    _draw_blocky_hull(surf, cx, cy, theme, 0)
    _draw_crystal_decorations(surf, cx, cy, theme, 0)
    
    return surf


def draw_crusher_plane(surface, style, frame, damage_flash=0, shield_active=False, ult_charge=0):
    """绘制CRUSHER机体 - 精细化版本 - 静态缓存 + 动态效果层"""
    size = surface.get_width()
    cache_key = (size, style)
    theme = get_crusher_theme(style)
    
    # 获取或创建缓存
    if cache_key not in _cache:
        _cache[cache_key] = _build_cache(size, style)
    
    surface.fill((0, 0, 0, 0))
    
    t = frame * 0.1
    cx, cy = size // 2, size // 2
    
    # 受伤闪白
    if damage_flash > 0 and (damage_flash // 2) % 2 == 0:
        white_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # 精细闪白轮廓
        flash_pts = [
            (cx - 32, cy - 8),
            (cx - 38, cy + 10),
            (cx - 35, cy + 32),
            (cx - 26, cy + 48),
            (cx, cy + 52),
            (cx + 26, cy + 48),
            (cx + 35, cy + 32),
            (cx + 38, cy + 10),
            (cx + 32, cy - 8),
            (cx + 22, cy - 5),
            (cx, cy - 60),
            (cx - 22, cy - 5),
        ]
        flash_pts = [(int(p[0]), int(p[1])) for p in flash_pts]
        pygame.draw.polygon(white_surf, (255, 255, 255, 200), flash_pts)
        surface.blit(white_surf, (0, 0))
    else:
        # 第一层：威压背景
        _draw_pressure_aura(surface, cx, cy, theme, t)
        
        # 第二层：静态机身（缓存）
        surface.blit(_cache[cache_key], (0, 0))
        
        # 第三层：动态钻头
        _draw_drill_head(surface, cx, cy, theme, t)
        
        # 第四层：充能槽
        charge_level = int(ult_charge / 20)  # 0-100 -> 0-5
        _draw_charge_slots(surface, cx, cy, theme, t, charge_level)
        
        # 第五层：引擎尾焰
        _draw_engine_exhaust(surface, cx, cy, theme, t)
        
        # 第六层：顶层效果
        _draw_top_effects(surface, cx, cy, theme, t)
    
    # 护盾效果（精细化）
    if shield_active:
        shield_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 多层护盾
        for i in range(4):
            r = 48 - i * 5 + int(math.sin(frame * 0.2 + i * 0.3) * 3)
            shield_alpha = 70 - i * 15
            pygame.draw.circle(shield_surf, (*theme["crystal"][:3], shield_alpha), (cx, cy), r, 2)
        
        # 护盾六边形网格
        hex_r = 42 + int(math.sin(frame * 0.15) * 4)
        hex_pts = []
        for i in range(6):
            angle = i * (math.pi / 3) + frame * 0.05
            hx = cx + math.cos(angle) * hex_r
            hy = cy + math.sin(angle) * hex_r * 0.85
            hex_pts.append((int(hx), int(hy)))
        pygame.draw.polygon(shield_surf, (*theme["crystal_bright"][:3], 50), hex_pts, 1)
        
        # 护盾光点
        for pt in hex_pts:
            pygame.draw.circle(shield_surf, (*theme["crystal_core"][:3], 120), pt, 3)
        
        surface.blit(shield_surf, (0, 0))
    
    return surface
