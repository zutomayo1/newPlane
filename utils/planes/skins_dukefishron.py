# -*- coding: utf-8 -*-
"""
深渊龙鱼·猪公爵 - 涂装模块

泰拉瑞亚最具压迫感的BOSS之一：猪龙鱼公爵
融合了鲨鱼的凶残、猪的怪异、龙的威严
每个涂装都有独特的恐怖美学
"""
import pygame
import math
import random

# 猪公爵涂装样式列表
DUKEFISHRON_STYLES = [
    "duke_default",      # 深海君主 - 经典蓝粉配色+獠牙利齿
    "duke_abyss",        # 深渊猎手 - 琵琶鱼灯笼+压缩形态
    "duke_rage",         # 狂暴形态 - 第三阶段全红+裂痕喷血
    "duke_storm",        # 雷霆风暴 - 龙卷风环绕+电弧缠身
    "duke_coral",        # 珊瑚领主 - 活珊瑚覆甲+寄生生物
    "duke_void_sea",     # 虚空之海 - 次元裂隙+星空鳞片
    "duke_tsunami",      # 海啸化身 - 水体半透明+浪涛血肉
    "duke_phantom",      # 幽魂遗骸 - 骨骼暴露+幽灵残影
    "duke_blood_moon",   # 血月狂潮 - 全身眼球+血泪横流
    "duke_tropical",     # 热带噩梦 - 剧毒色彩+箭毒蛙纹
    "duke_frost",        # 霜骨巨兽 - 冰封尸骸+冰晶刺甲
    "duke_golden",       # 黄金暴君 - 远古帝王+珠宝镶嵌
]


def is_dukefishron_style(model_style):
    """检查是否为猪公爵涂装"""
    return model_style in DUKEFISHRON_STYLES


def draw_duke(surface, color, x, y, w, h, frame=0, style="duke_default"):
    """绘制猪公爵"""
    renderers = {
        "duke_default": _draw_duke_default,
        "duke_abyss": _draw_duke_abyss,
        "duke_rage": _draw_duke_rage,
        "duke_storm": _draw_duke_storm,
        "duke_coral": _draw_duke_coral,
        "duke_void_sea": _draw_duke_void_sea,
        "duke_tsunami": _draw_duke_tsunami,
        "duke_phantom": _draw_duke_phantom,
        "duke_blood_moon": _draw_duke_blood_moon,
        "duke_tropical": _draw_duke_tropical,
        "duke_frost": _draw_duke_frost,
        "duke_golden": _draw_duke_golden,
    }
    draw_func = renderers.get(style, _draw_duke_default)
    draw_func(surface, color, x, y, w, h, frame)


# =============================================================================
#   核心辅助函数 - 猪龙鱼的恐怖元素
# =============================================================================

def _draw_shark_maw(s, cx, cy, w, h, t, teeth_col=(255,255,255), gum_col=(180,40,60)):
    """鲨鱼巨口 - 多排锯齿利牙"""
    maw_w, maw_h = int(w * 0.7), int(h * 0.3)
    # 上颚
    pygame.draw.arc(s, gum_col, (cx - maw_w//2, cy - maw_h, maw_w, maw_h * 2), 0, math.pi, 4)
    # 下颚 - 微张
    jaw_open = abs(math.sin(t * 0.15)) * 8
    pygame.draw.arc(s, gum_col, (cx - maw_w//2, int(cy + jaw_open), maw_w, maw_h), math.pi, 2*math.pi, 4)
    
    # 多排锯齿 - 上排
    for row in range(2):
        for i in range(9):
            angle = math.pi * (0.1 + i * 0.1)
            tx = cx + math.cos(angle) * (maw_w//2 - row * 4)
            ty = cy - math.sin(angle) * (maw_h//2 - row * 3)
            t_len = 8 - row * 3
            pygame.draw.polygon(s, teeth_col, [
                (int(tx - 2), int(ty)),
                (int(tx), int(ty + t_len)),
                (int(tx + 2), int(ty))
            ])
    # 下排
    for i in range(7):
        tx = cx - maw_w//2 + 8 + i * (maw_w - 16) // 6
        ty = cy + jaw_open + 2
        pygame.draw.polygon(s, teeth_col, [
            (int(tx - 2), int(ty)),
            (int(tx), int(ty - 6)),
            (int(tx + 2), int(ty))
        ])


def _draw_pig_snout(s, cx, cy, size, t, skin_col, nostril_col):
    """猪鼻 - 扭曲的鼻孔+粘液"""
    snout_w, snout_h = int(size * 1.4), int(size * 0.9)
    # 鼻梁隆起
    pygame.draw.ellipse(s, skin_col, (cx - snout_w//2, cy - snout_h//2, snout_w, snout_h))
    # 鼻孔 - 不对称扭曲
    for side in [-1, 1]:
        nx = cx + side * size * 0.35
        ny = cy + math.sin(t * 0.2 + side) * 2
        pygame.draw.ellipse(s, nostril_col, (int(nx) - 5, int(ny) - 4, 10, 8))
        # 鼻孔深处
        pygame.draw.ellipse(s, (max(0, nostril_col[0]-40), max(0, nostril_col[1]-30), max(0, nostril_col[2]-30)),
                           (int(nx) - 3, int(ny) - 2, 6, 4))
    # 粘液滴落
    drip = (t * 2) % 40
    if drip < 20:
        pygame.draw.ellipse(s, (180, 200, 160, 180), (cx - 2, int(cy + snout_h//2 + drip), 4, 6))


def _draw_dragon_horn(s, base_x, base_y, length, angle, t, col1, col2, segments=5):
    """龙角 - 弯曲分节+脊刺"""
    points = []
    for i in range(segments + 1):
        prog = i / segments
        curve = math.sin(prog * math.pi * 0.6) * length * 0.15
        px = base_x + math.cos(math.radians(angle)) * length * prog
        py = base_y - math.sin(math.radians(angle)) * length * prog - curve
        points.append((int(px), int(py)))
    
    if len(points) >= 2:
        # 角体
        for i in range(len(points) - 1):
            thick = max(2, int(8 * (1 - i / len(points))))
            prog = i / len(points)
            blend_col = (
                int(col1[0] * (1 - prog) + col2[0] * prog),
                int(col1[1] * (1 - prog) + col2[1] * prog),
                int(col1[2] * (1 - prog) + col2[2] * prog)
            )
            pygame.draw.line(s, blend_col, points[i], points[i + 1], thick)
        
        # 角刺
        for i in range(1, len(points) - 1):
            spike_len = 4 * (1 - i / len(points))
            sx, sy = points[i]
            pygame.draw.line(s, col2, (sx, sy), (int(sx + spike_len), int(sy - spike_len * 2)), 2)


def _draw_fishron_eye(s, cx, cy, size, t, iris_col, rage=False):
    """龙鱼之眼 - 愤怒竖瞳+血丝"""
    # 眼眶凹陷
    pygame.draw.ellipse(s, (20, 20, 30), (cx - size - 3, cy - size * 0.7 - 2, size * 2 + 6, size * 1.4 + 4))
    # 眼白
    sclera = (255, 230, 200) if not rage else (255, 200, 180)
    pygame.draw.ellipse(s, sclera, (cx - size, cy - size * 0.7, size * 2, size * 1.4))
    
    # 血丝 - 狂暴时更多
    blood_count = 8 if rage else 4
    for i in range(blood_count):
        angle = (i * (360 / blood_count) + t * 10) * 0.01745
        bx = cx + math.cos(angle) * size * 0.8
        by = cy + math.sin(angle) * size * 0.5
        pygame.draw.line(s, (200, 60, 60) if rage else (180, 80, 80), (cx, cy), (int(bx), int(by)), 1)
    
    # 虹膜
    iris_r = int(size * 0.6)
    wobble = math.sin(t * 0.8) * 2
    pygame.draw.circle(s, iris_col, (int(cx + wobble), cy), iris_r)
    
    # 竖瞳 - 狂暴时收缩
    pupil_w = 3 if rage else 5
    pupil_h = int(size * 0.9)
    pygame.draw.ellipse(s, (0, 0, 0), (int(cx - pupil_w//2 + wobble), cy - pupil_h//2, pupil_w, pupil_h))
    
    # 高光
    pygame.draw.circle(s, (255, 255, 255), (int(cx - size * 0.3), int(cy - size * 0.25)), 3)
    if rage:
        # 狂暴时眼角渗血
        pygame.draw.line(s, (180, 30, 30), (cx + size, cy), (int(cx + size + 6), int(cy + 4)), 2)


def _draw_dorsal_fin(s, cx, cy, w, h, t, main_col, accent_col, segments=6):
    """背鳍 - 锯齿龙脊+膜"""
    points = [(cx - w * 0.3, cy)]
    for i in range(segments):
        prog = i / (segments - 1)
        spike_x = cx - w * 0.25 + w * 0.5 * prog
        wave = math.sin(t * 0.15 + i * 0.8) * 4
        spike_h = h * (0.7 + math.sin(prog * math.pi) * 0.3) + wave
        points.append((int(spike_x), int(cy - spike_h)))
        if i < segments - 1:
            points.append((int(spike_x + w * 0.04), int(cy - spike_h * 0.5)))
    points.append((cx + w * 0.3, cy))
    
    # 鳍膜
    pygame.draw.polygon(s, main_col, points)
    # 骨刺高光
    for i in range(segments):
        prog = i / (segments - 1)
        spike_x = cx - w * 0.25 + w * 0.5 * prog
        wave = math.sin(t * 0.15 + i * 0.8) * 4
        spike_h = h * (0.7 + math.sin(prog * math.pi) * 0.3) + wave
        pygame.draw.line(s, accent_col, (int(spike_x), cy), (int(spike_x), int(cy - spike_h)), 2)


def _draw_pectoral_fin(s, base_x, base_y, length, angle, t, col, side=1):
    """胸鳍 - 龙翼形态"""
    flap = math.sin(t * 0.2 + side * 0.5) * 15
    angle_rad = math.radians(angle + flap * side)
    
    points = [
        (base_x, base_y),
        (int(base_x + math.cos(angle_rad - 0.3) * length * 0.6), int(base_y + math.sin(angle_rad - 0.3) * length * 0.6)),
        (int(base_x + math.cos(angle_rad) * length), int(base_y + math.sin(angle_rad) * length)),
        (int(base_x + math.cos(angle_rad + 0.2) * length * 0.8), int(base_y + math.sin(angle_rad + 0.2) * length * 0.8)),
        (int(base_x + math.cos(angle_rad + 0.5) * length * 0.5), int(base_y + math.sin(angle_rad + 0.5) * length * 0.5)),
    ]
    pygame.draw.polygon(s, col, points)
    # 翼骨
    for i in range(3):
        prog = 0.3 + i * 0.25
        end_x = base_x + math.cos(angle_rad + (i - 1) * 0.15) * length * prog
        end_y = base_y + math.sin(angle_rad + (i - 1) * 0.15) * length * prog
        pygame.draw.line(s, (min(255, col[0]+30), min(255, col[1]+30), min(255, col[2]+30)),
                        (base_x, base_y), (int(end_x), int(end_y)), 2)


def _draw_tail_fin(s, cx, cy, w, h, t, col):
    """尾鳍 - 三叉戟形"""
    wave = math.sin(t * 0.12) * 8
    points = [
        (cx, cy),
        (cx - w * 0.15 + wave * 0.3, cy + h * 0.15),
        (cx - w * 0.35 + wave, cy + h * 0.4),
        (cx - w * 0.15 + wave * 0.5, cy + h * 0.25),
        (cx + wave * 0.2, cy + h * 0.35),
        (cx + w * 0.15 - wave * 0.5, cy + h * 0.25),
        (cx + w * 0.35 - wave, cy + h * 0.4),
        (cx + w * 0.15 - wave * 0.3, cy + h * 0.15),
    ]
    pygame.draw.polygon(s, col, [(int(p[0]), int(p[1])) for p in points])


def _draw_duke_base(surface, cx, cy, w, h, frame, colors, effects=None):
    """基础猪龙鱼绘制 - 所有涂装共用的结构"""
    main, accent, highlight, belly_c, eye_c = colors
    
    # 确保坐标是整数
    cx, cy = int(cx), int(cy)
    
    swim = math.sin(frame * 0.15) * 3
    fin_flap = math.sin(frame * 0.2) * 8
    
    # === 尾鳍 - 三叉戟形 ===
    tail_base = cy + h * 0.25
    tail_pts = [
        (cx, tail_base),
        (cx - w * 0.15, tail_base + h * 0.15),
        (cx - w * 0.28 + swim, tail_base + h * 0.32),
        (cx - w * 0.12, tail_base + h * 0.22),
        (cx, tail_base + h * 0.28),
        (cx + w * 0.12, tail_base + h * 0.22),
        (cx + w * 0.28 - swim, tail_base + h * 0.32),
        (cx + w * 0.15, tail_base + h * 0.15),
    ]
    pygame.draw.polygon(surface, main, tail_pts)
    pygame.draw.polygon(surface, accent, tail_pts, 2)
    
    # === 背鳍 - 锯齿龙脊 ===
    for i in range(4):
        dx = (i - 1.5) * w * 0.08
        spine_h = h * (0.28 + i * 0.04) + abs(swim) * (1 + i * 0.15)
        spine_pts = [
            (cx + dx - w * 0.04, cy - h * 0.08),
            (cx + dx, cy - spine_h),
            (cx + dx + w * 0.04, cy - h * 0.08),
        ]
        pygame.draw.polygon(surface, accent if i % 2 else main, spine_pts)
    
    # === 胸鳍 - 龙翼形 ===
    # 左翼
    left_fin = [
        (cx - w * 0.28, cy - h * 0.05),
        (cx - w * 0.52, cy + fin_flap - h * 0.08),
        (cx - w * 0.48, cy + fin_flap + h * 0.05),
        (cx - w * 0.38, cy + h * 0.12),
        (cx - w * 0.25, cy + h * 0.08),
    ]
    pygame.draw.polygon(surface, main, left_fin)
    pygame.draw.polygon(surface, highlight, left_fin, 1)
    # 翼骨
    pygame.draw.line(surface, accent, (cx - w * 0.28, cy - h * 0.02),
                    (cx - w * 0.48, cy + fin_flap - h * 0.02), 2)
    
    # 右翼
    right_fin = [
        (cx + w * 0.28, cy - h * 0.05),
        (cx + w * 0.52, cy - fin_flap - h * 0.08),
        (cx + w * 0.48, cy - fin_flap + h * 0.05),
        (cx + w * 0.38, cy + h * 0.12),
        (cx + w * 0.25, cy + h * 0.08),
    ]
    pygame.draw.polygon(surface, main, right_fin)
    pygame.draw.polygon(surface, highlight, right_fin, 1)
    pygame.draw.line(surface, accent, (cx + w * 0.28, cy - h * 0.02),
                    (cx + w * 0.48, cy - fin_flap - h * 0.02), 2)
    
    # === 主体 - 流线型鱼身 ===
    body_w, body_h = int(w * 0.58), int(h * 0.48)
    body_rect = (cx - body_w // 2, cy - body_h // 2 + swim, body_w, body_h)
    pygame.draw.ellipse(surface, main, body_rect)
    
    # 腹部高光
    belly_w, belly_h = int(body_w * 0.65), int(body_h * 0.45)
    pygame.draw.ellipse(surface, belly_c,
                       (cx - belly_w // 2, cy + h * 0.02 + swim, belly_w, belly_h))
    
    # 鳞片纹理
    for i in range(6):
        sx = cx - w * 0.18 + i * w * 0.07
        sy = cy + h * 0.08 + swim
        pygame.draw.arc(surface, highlight, (sx - 5, sy - 3, 10, 6), 0, math.pi, 1)
    
    # === 头部 - 猪龙混合 ===
    head_r = int(w * 0.26)
    head_y = cy - h * 0.16 + swim
    pygame.draw.circle(surface, main, (cx, int(head_y)), head_r)
    
    # 猪鼻
    snout_w, snout_h = int(w * 0.22), int(h * 0.14)
    snout_y = head_y - h * 0.1
    pygame.draw.ellipse(surface, accent,
                       (cx - snout_w // 2, int(snout_y) - snout_h // 2, snout_w, snout_h))
    # 鼻孔
    pygame.draw.circle(surface, (max(0, accent[0]-60), max(0, accent[1]-40), max(0, accent[2]-40)),
                      (cx - 7, int(snout_y)), 4)
    pygame.draw.circle(surface, (max(0, accent[0]-60), max(0, accent[1]-40), max(0, accent[2]-40)),
                      (cx + 7, int(snout_y)), 4)
    
    # === 眼睛 - 凶恶龙眼 ===
    eye_r = 9
    eye_y = head_y + 4
    for ex in [-14, 14]:
        # 眼白
        pygame.draw.circle(surface, (255, 255, 255), (cx + ex, int(eye_y)), eye_r)
        # 虹膜
        pygame.draw.circle(surface, eye_c, (cx + ex, int(eye_y)), eye_r - 2)
        # 瞳孔 - 竖瞳
        pygame.draw.ellipse(surface, (0, 0, 0),
                           (cx + ex - 2, int(eye_y) - 5, 4, 10))
        # 高光
        pygame.draw.circle(surface, (255, 255, 255), (cx + ex - 3, int(eye_y) - 3), 2)
    
    # === 獠牙 ===
    fang_len = 10
    for fx in [-9, 9]:
        pygame.draw.polygon(surface, (255, 255, 255), [
            (cx + fx - 3, int(head_y) + head_r - 6),
            (cx + fx, int(head_y) + head_r + fang_len),
            (cx + fx + 3, int(head_y) + head_r - 6),
        ])
    
    # === 龙角 - 向后弯曲 ===
    for side in [-1, 1]:
        horn_base_x = cx + side * w * 0.18
        horn_base_y = head_y - head_r * 0.4
        horn_pts = [
            (horn_base_x, horn_base_y),
            (horn_base_x + side * w * 0.08, horn_base_y - h * 0.12),
            (horn_base_x + side * w * 0.22, horn_base_y - h * 0.22),
            (horn_base_x + side * w * 0.12, horn_base_y - h * 0.08),
        ]
        pygame.draw.polygon(surface, accent, horn_pts)
        pygame.draw.polygon(surface, highlight, horn_pts, 1)
    
    return swim, head_y, head_r


def _draw_duke_default(surface, color, x, y, w, h, frame):
    """默认涂装 - 深海君主：经典猪龙鱼公爵的恐怖威严"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    swim = math.sin(t * 3) * 4
    
    # 颜色方案
    body_main = (35, 85, 180)       # 深海蓝
    body_accent = (255, 120, 175)   # 龙鱼粉
    belly = (180, 210, 240)         # 银白腹
    horn_col = (200, 100, 150)      # 角色
    eye_col = (255, 80, 120)        # 愤怒红眼
    
    # === 尾鳍 - 三叉强力 ===
    _draw_tail_fin(surface, cx, cy + h * 0.22 + swim, w, h * 0.5, t, body_accent)
    
    # === 背鳍 - 锯齿龙脊 ===
    _draw_dorsal_fin(surface, cx, cy - h * 0.1 + swim, w * 0.8, h * 0.4, t, body_main, body_accent)
    
    # === 胸鳍 - 龙翼 ===
    _draw_pectoral_fin(surface, cx - w * 0.22, cy + swim, w * 0.45, 200, t, body_main, -1)
    _draw_pectoral_fin(surface, cx + w * 0.22, cy + swim, w * 0.45, -20, t, body_main, 1)
    
    # === 流线型身躯 ===
    body_w, body_h = int(w * 0.6), int(h * 0.5)
    pygame.draw.ellipse(surface, body_main, 
                       (cx - body_w//2, int(cy - body_h//2 + swim), body_w, body_h))
    # 腹部
    pygame.draw.ellipse(surface, belly,
                       (cx - body_w//3, int(cy + swim), body_w * 2//3, body_h//3))
    # 鳞片纹理
    for row in range(3):
        for i in range(5):
            sx = cx - w * 0.18 + i * w * 0.09
            sy = cy - h * 0.05 + row * h * 0.08 + swim
            pygame.draw.arc(surface, (min(255, body_main[0]+40), min(255, body_main[1]+40), min(255, body_main[2]+40)),
                          (int(sx) - 6, int(sy) - 3, 12, 6), 0, math.pi, 1)
    
    # === 头部 - 巨大威压 ===
    head_r = int(w * 0.28)
    head_y = cy - h * 0.18 + swim
    pygame.draw.circle(surface, body_main, (cx, int(head_y)), head_r)
    # 头部高光
    pygame.draw.circle(surface, (min(255, body_main[0]+30), min(255, body_main[1]+30), min(255, body_main[2]+30)),
                      (cx - head_r//3, int(head_y - head_r//3)), head_r//3)
    
    # === 猪鼻 - 扭曲怪异 ===
    _draw_pig_snout(surface, cx, int(head_y - h * 0.08), 14, t, body_accent, (100, 40, 60))
    
    # === 巨口獠牙 ===
    _draw_shark_maw(surface, cx, int(head_y + head_r * 0.6), w * 0.35, h * 0.15, t)
    
    # === 龙眼 - 凶恶注视 ===
    for side in [-1, 1]:
        _draw_fishron_eye(surface, cx + side * 16, int(head_y + 4), 10, t, eye_col)
    
    # === 弯曲龙角 ===
    _draw_dragon_horn(surface, cx - w * 0.18, int(head_y - head_r * 0.5), w * 0.3, 120, t, horn_col, body_accent)
    _draw_dragon_horn(surface, cx + w * 0.18, int(head_y - head_r * 0.5), w * 0.3, 60, t, horn_col, body_accent)
    
    # === 特效：海水气泡 ===
    for i in range(4):
        bx = cx + math.sin(t * 2 + i * 1.5) * w * 0.25
        by = cy + h * 0.35 + (frame + i * 20) % 30
        pygame.draw.circle(surface, (180, 220, 255, 150), (int(bx), int(by)), 4 - i % 3)


def _draw_duke_abyss(surface, color, x, y, w, h, frame):
    """深渊猎手 - 琵琶鱼形态：诱饵灯笼+压缩变形的深海怪物"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    swim = math.sin(t * 2) * 3
    pulse = abs(math.sin(t * 1.5)) * 0.4 + 0.6
    
    # 深渊配色 - 极致黑暗
    body_main = (15, 12, 45)        # 深渊黑紫
    body_accent = (80, 40, 120)     # 暗紫
    biolum = (120, 200, 255)        # 生物荧光蓝
    biolum_pink = (255, 100, 200)   # 生物荧光粉
    eye_glow = (200, 255, 255)      # 发光眼
    
    # === 深海压力变形 - 更扁平的身躯 ===
    body_w, body_h = int(w * 0.65), int(h * 0.38)
    pygame.draw.ellipse(surface, body_main,
                       (cx - body_w//2, int(cy - body_h//2 + swim), body_w, body_h))
    
    # === 萎缩的鳍 - 深海退化 ===
    for side in [-1, 1]:
        fin_pts = [
            (cx + side * w * 0.28, int(cy + swim)),
            (cx + side * w * 0.42, int(cy - h * 0.05 + swim)),
            (cx + side * w * 0.38, int(cy + h * 0.12 + swim)),
        ]
        pygame.draw.polygon(surface, body_accent, fin_pts)
    
    # === 头部 - 巨口深渊鱼 ===
    head_r = int(w * 0.32)
    head_y = cy - h * 0.12 + swim
    pygame.draw.circle(surface, body_main, (cx, int(head_y)), head_r)
    
    # === 琵琶鱼灯笼 - 诱饵发光器 ===
    lantern_base_x = cx
    lantern_base_y = head_y - head_r - 5
    lantern_stalk_end = lantern_base_y - h * 0.25
    # 灯笼柄 - 弯曲
    stalk_pts = []
    for i in range(8):
        prog = i / 7
        sx = lantern_base_x + math.sin(t + prog * 3) * 6
        sy = lantern_base_y - prog * (lantern_base_y - lantern_stalk_end)
        stalk_pts.append((int(sx), int(sy)))
    pygame.draw.lines(surface, body_accent, False, stalk_pts, 3)
    # 发光诱饵
    lure_x, lure_y = stalk_pts[-1]
    glow_r = int(12 * pulse)
    glow_surf = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*biolum, int(60 * pulse)), (glow_r * 2, glow_r * 2), glow_r * 2)
    pygame.draw.circle(glow_surf, (*biolum, int(120 * pulse)), (glow_r * 2, glow_r * 2), glow_r)
    pygame.draw.circle(glow_surf, (255, 255, 255), (glow_r * 2, glow_r * 2), glow_r // 2)
    surface.blit(glow_surf, (lure_x - glow_r * 2, lure_y - glow_r * 2))
    
    # === 巨口 - 深渊猎食者 ===
    maw_y = head_y + head_r * 0.4
    maw_open = abs(math.sin(t * 0.8)) * 12
    # 上颚
    pygame.draw.arc(surface, (60, 30, 80), (cx - w * 0.28, int(maw_y - h * 0.1), int(w * 0.56), int(h * 0.2)), 0, math.pi, 5)
    # 下颚
    pygame.draw.arc(surface, (60, 30, 80), (cx - w * 0.28, int(maw_y + maw_open), int(w * 0.56), int(h * 0.12)), math.pi, 2*math.pi, 5)
    # 透明尖牙 - 深海鱼特征
    for i in range(11):
        tx = cx - w * 0.24 + i * w * 0.048
        fang_len = 10 + (5 - abs(i - 5)) * 2  # 中间更长
        pygame.draw.polygon(surface, (200, 220, 255), [
            (int(tx - 2), int(maw_y)),
            (int(tx), int(maw_y + fang_len)),
            (int(tx + 2), int(maw_y))
        ])
    
    # === 微小发光眼 - 深海适应 ===
    for side in [-1, 1]:
        ex = cx + side * 14
        ey = int(head_y - 2)
        pygame.draw.circle(surface, (20, 20, 40), (ex, ey), 8)  # 眼眶
        pygame.draw.circle(surface, eye_glow, (ex, ey), 5)
        pygame.draw.circle(surface, (255, 255, 255), (ex - 2, ey - 2), 2)
    
    # === 身体发光器官 ===
    for i in range(6):
        organ_x = cx - w * 0.2 + i * w * 0.08
        organ_y = cy + h * 0.08 + swim + math.sin(t * 2 + i) * 2
        org_col = biolum if i % 2 == 0 else biolum_pink
        org_r = int(5 * pulse)
        pygame.draw.circle(surface, (*org_col, int(180 * pulse)), (int(organ_x), int(organ_y)), org_r)
        pygame.draw.circle(surface, (255, 255, 255), (int(organ_x), int(organ_y)), org_r // 2)
    
    # === 退化龙角 - 变成触须 ===
    for side in [-1, 1]:
        for t_off in range(3):
            tx = cx + side * (w * 0.12 + t_off * 8)
            ty = head_y - head_r * 0.6
            t_len = 18 - t_off * 4
            wave = math.sin(t * 2 + t_off + side) * 8
            end_x = tx + side * wave
            end_y = ty - t_len
            pygame.draw.line(surface, body_accent, (int(tx), int(ty)), (int(end_x), int(end_y)), 2)
            pygame.draw.circle(surface, biolum, (int(end_x), int(end_y)), int(3 * pulse))


def _draw_duke_rage(surface, color, x, y, w, h, frame):
    """狂暴形态 - 第三阶段：浑身裂痕喷涌血光的暴走状态"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 狂暴抖动
    shake_x = random.randint(-3, 3)
    shake_y = random.randint(-2, 2)
    cx += shake_x
    cy += shake_y
    
    rage_pulse = abs(math.sin(t * 4)) * 0.5 + 0.5
    
    # 狂暴配色 - 血红主调
    body_main = (140, 25, 35)       # 血肉红
    body_accent = (200, 40, 60)     # 鲜血
    wound_col = (255, 100, 50)      # 伤口发光
    blood_col = (120, 10, 20)       # 暗血
    eye_col = (255, 255, 100)       # 狂怒黄眼
    
    # === 血雾背景 ===
    blood_mist = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(12):
        mx = random.randint(0, w)
        my = random.randint(0, h)
        mr = random.randint(8, 20)
        pygame.draw.circle(blood_mist, (140, 20, 30, 30), (mx, my), mr)
    surface.blit(blood_mist, (x - shake_x, y - shake_y))
    
    # === 尾鳍 - 破损撕裂 ===
    tail_y = cy + h * 0.22
    tail_pts = [
        (cx, tail_y), (cx - w * 0.12, tail_y + h * 0.12),
        (cx - w * 0.32, tail_y + h * 0.38),  # 撕裂延长
        (cx - w * 0.08, tail_y + h * 0.2),
        (cx, tail_y + h * 0.32),
        (cx + w * 0.08, tail_y + h * 0.2),
        (cx + w * 0.32, tail_y + h * 0.38),
        (cx + w * 0.12, tail_y + h * 0.12),
    ]
    pygame.draw.polygon(surface, body_accent, [(int(p[0]), int(p[1])) for p in tail_pts])
    # 尾鳍撕裂
    for i in range(3):
        tear_x = cx + (i - 1) * w * 0.1
        tear_y = tail_y + h * 0.15 + i * 5
        pygame.draw.line(surface, blood_col, (int(tear_x), int(tear_y)), (int(tear_x + 5), int(tear_y + 12)), 2)
    
    # === 背鳍 - 断裂龙脊 ===
    for i in range(5):
        spine_x = cx - w * 0.15 + i * w * 0.075
        spine_h = h * (0.25 + random.random() * 0.1)
        # 断裂的脊刺
        pygame.draw.polygon(surface, body_accent, [
            (int(spine_x - 4), int(cy - h * 0.08)),
            (int(spine_x), int(cy - spine_h)),
            (int(spine_x + 4), int(cy - h * 0.08))
        ])
        # 脊刺发光裂痕
        pygame.draw.line(surface, wound_col, (int(spine_x), int(cy - h * 0.08)), (int(spine_x), int(cy - spine_h * 0.7)), 2)
    
    # === 胸鳍 - 撕裂龙翼 ===
    for side in [-1, 1]:
        fin_base_x = cx + side * w * 0.25
        flap = math.sin(t * 4 + side) * 20  # 剧烈拍打
        fin_pts = [
            (fin_base_x, cy),
            (int(fin_base_x + side * w * 0.35), int(cy + flap - h * 0.1)),
            (int(fin_base_x + side * w * 0.3), int(cy + flap + h * 0.08)),
            (int(fin_base_x + side * w * 0.15), int(cy + h * 0.1)),
        ]
        pygame.draw.polygon(surface, body_main, fin_pts)
        # 鳍膜撕裂孔
        for j in range(2):
            hx = fin_base_x + side * w * (0.15 + j * 0.08)
            hy = cy + flap * 0.5 + j * 3
            pygame.draw.circle(surface, blood_col, (int(hx), int(hy)), 4)
    
    # === 身躯 - 裂痕遍布 ===
    body_w, body_h = int(w * 0.62), int(h * 0.52)
    pygame.draw.ellipse(surface, body_main,
                       (cx - body_w//2, cy - body_h//2, body_w, body_h))
    # 身体裂痕网络
    for i in range(8):
        crack_x = cx - w * 0.2 + random.random() * w * 0.4
        crack_y = cy - h * 0.1 + random.random() * h * 0.25
        crack_len = 10 + random.random() * 15
        crack_angle = random.random() * math.pi
        end_x = crack_x + math.cos(crack_angle) * crack_len
        end_y = crack_y + math.sin(crack_angle) * crack_len
        pygame.draw.line(surface, wound_col, (int(crack_x), int(crack_y)), (int(end_x), int(end_y)), 2)
        # 裂痕分叉
        if random.random() > 0.5:
            branch_len = crack_len * 0.5
            branch_angle = crack_angle + (random.random() - 0.5) * 1.2
            pygame.draw.line(surface, (255, 150, 80),
                           (int(end_x), int(end_y)),
                           (int(end_x + math.cos(branch_angle) * branch_len), 
                            int(end_y + math.sin(branch_angle) * branch_len)), 1)
    
    # === 头部 - 扭曲狂暴 ===
    head_r = int(w * 0.3)
    head_y = cy - h * 0.16
    pygame.draw.circle(surface, body_main, (cx, int(head_y)), head_r)
    
    # 头部裂痕
    for i in range(5):
        hc_start = (cx + random.randint(-head_r//2, head_r//2), int(head_y + random.randint(-head_r//2, head_r//2)))
        hc_end = (hc_start[0] + random.randint(-10, 10), hc_start[1] + random.randint(-10, 10))
        pygame.draw.line(surface, wound_col, hc_start, hc_end, 2)
    
    # === 巨口嘶吼 - 张开到极限 ===
    maw_y = head_y + head_r * 0.5
    pygame.draw.arc(surface, (80, 20, 30), (cx - w * 0.3, int(maw_y - h * 0.12), int(w * 0.6), int(h * 0.25)), 0, math.pi, 6)
    pygame.draw.arc(surface, (80, 20, 30), (cx - w * 0.3, int(maw_y + 10), int(w * 0.6), int(h * 0.15)), math.pi, 2*math.pi, 6)
    # 獠牙
    for i in range(10):
        tx = cx - w * 0.26 + i * w * 0.058
        fang_len = 12 + abs(5 - i) * 1.5
        pygame.draw.polygon(surface, (255, 220, 200), [
            (int(tx - 3), int(maw_y + 2)),
            (int(tx), int(maw_y + fang_len)),
            (int(tx + 3), int(maw_y + 2))
        ])
    
    # === 狂暴之眼 - 收缩瞳孔+血泪 ===
    for side in [-1, 1]:
        _draw_fishron_eye(surface, cx + side * 18, int(head_y + 2), 11, t, eye_col, rage=True)
        # 血泪
        for tear in range(3):
            ty = head_y + 10 + tear * 8 + (frame * 0.5) % 20
            pygame.draw.ellipse(surface, (180, 30, 40), (cx + side * 18 - 2, int(ty), 4, 6))
    
    # === 断裂龙角 ===
    for side in [-1, 1]:
        horn_x = cx + side * w * 0.2
        horn_y = head_y - head_r * 0.5
        # 断裂的角
        pygame.draw.polygon(surface, body_accent, [
            (int(horn_x), int(horn_y)),
            (int(horn_x + side * 12), int(horn_y - 20)),
            (int(horn_x + side * 8), int(horn_y - 8)),
        ])
        # 断面发光
        pygame.draw.circle(surface, wound_col, (int(horn_x + side * 12), int(horn_y - 20)), 4)
    
    # === 喷涌血雾 ===
    for i in range(5):
        spray_x = cx + random.randint(-int(w * 0.3), int(w * 0.3))
        spray_y = cy + random.randint(-int(h * 0.25), int(h * 0.2))
        spray_r = int(6 * rage_pulse)
        pygame.draw.circle(surface, (200, 40, 50, 180), (int(spray_x), int(spray_y)), spray_r)


def _draw_duke_storm(surface, color, x, y, w, h, frame):
    """雷霆风暴 - 龙卷风环绕+电弧缠身的风暴领主"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    swim = math.sin(t * 3) * 3
    
    # 风暴配色
    body_main = (50, 100, 180)      # 风暴蓝
    body_accent = (100, 180, 255)   # 电光青
    lightning = (255, 255, 200)     # 闪电黄
    cloud_col = (80, 100, 140)      # 雷云
    eye_col = (255, 255, 180)       # 闪电眼
    
    # === 环绕龙卷风 ===
    tornado_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for tornado_i in range(3):
        t_angle = t * 2 + tornado_i * 2.1
        t_dist = w * 0.42
        t_cx = w // 2 + math.cos(t_angle) * t_dist
        t_cy = h // 2 + math.sin(t_angle) * t_dist * 0.4
        # 龙卷风漏斗
        for ring in range(8):
            ring_y = t_cy - 20 + ring * 6
            ring_r = 4 + ring * 2.5
            ring_alpha = 150 - ring * 15
            twist = math.sin(t * 4 + ring * 0.5) * 5
            pygame.draw.ellipse(tornado_surf, (*cloud_col, ring_alpha),
                              (int(t_cx - ring_r + twist), int(ring_y), int(ring_r * 2), 5))
    surface.blit(tornado_surf, (x, y))
    
    # === 雷云背景 ===
    for i in range(5):
        cloud_x = cx + math.sin(t + i * 1.3) * w * 0.35
        cloud_y = cy - h * 0.3 + math.cos(t * 0.5 + i) * 10
        pygame.draw.ellipse(surface, cloud_col,
                          (int(cloud_x - 15), int(cloud_y - 8), 30, 16))
    
    # === 尾鳍 - 风暴之尾 ===
    tail_wave = math.sin(t * 4) * 12
    tail_pts = [
        (cx, cy + h * 0.2 + swim),
        (cx - w * 0.1 + tail_wave * 0.3, cy + h * 0.3 + swim),
        (cx - w * 0.28 + tail_wave, cy + h * 0.45 + swim),
        (cx, cy + h * 0.38 + swim),
        (cx + w * 0.28 - tail_wave, cy + h * 0.45 + swim),
        (cx + w * 0.1 - tail_wave * 0.3, cy + h * 0.3 + swim),
    ]
    pygame.draw.polygon(surface, body_accent, [(int(p[0]), int(p[1])) for p in tail_pts])
    
    # === 背鳍 - 闪电脊 ===
    _draw_dorsal_fin(surface, cx, cy - h * 0.08 + swim, w * 0.75, h * 0.38, t, body_main, lightning)
    
    # === 胸鳍 - 风暴之翼 ===
    _draw_pectoral_fin(surface, cx - w * 0.22, cy + swim, w * 0.5, 195, t, body_accent, -1)
    _draw_pectoral_fin(surface, cx + w * 0.22, cy + swim, w * 0.5, -15, t, body_accent, 1)
    
    # === 身躯 - 电弧缠绕 ===
    body_w, body_h = int(w * 0.58), int(h * 0.48)
    pygame.draw.ellipse(surface, body_main,
                       (cx - body_w//2, int(cy - body_h//2 + swim), body_w, body_h))
    
    # 电弧网络
    for i in range(6):
        arc_start_x = cx - w * 0.2 + random.random() * w * 0.4
        arc_start_y = cy + swim + random.randint(-int(h * 0.15), int(h * 0.15))
        arc_pts = [(int(arc_start_x), int(arc_start_y))]
        for j in range(4):
            arc_pts.append((
                int(arc_pts[-1][0] + random.randint(-8, 8)),
                int(arc_pts[-1][1] + random.randint(3, 8))
            ))
        pygame.draw.lines(surface, lightning, False, arc_pts, 2)
    
    # === 头部 ===
    head_r = int(w * 0.27)
    head_y = cy - h * 0.17 + swim
    pygame.draw.circle(surface, body_main, (cx, int(head_y)), head_r)
    
    # === 猪鼻 ===
    _draw_pig_snout(surface, cx, int(head_y - h * 0.07), 12, t, body_accent, (60, 80, 120))
    
    # === 巨口 ===
    _draw_shark_maw(surface, cx, int(head_y + head_r * 0.55), w * 0.3, h * 0.12, t)
    
    # === 闪电眼 ===
    flash = (frame % 12) < 3
    for side in [-1, 1]:
        ex, ey = cx + side * 15, int(head_y + 3)
        pygame.draw.circle(surface, (30, 50, 80), (ex, ey), 10)
        pygame.draw.circle(surface, (255, 255, 255) if flash else eye_col, (ex, ey), 7)
        pygame.draw.ellipse(surface, (0, 0, 0), (ex - 2, ey - 6, 4, 12))
        if flash:
            # 闪电从眼睛射出
            for bolt in range(2):
                bolt_end_x = ex + side * (15 + bolt * 10)
                bolt_end_y = ey + random.randint(-8, 8)
                pygame.draw.line(surface, lightning, (ex, ey), (bolt_end_x, bolt_end_y), 2)
    
    # === 雷电龙角 ===
    for side in [-1, 1]:
        horn_x = cx + side * w * 0.16
        horn_y = head_y - head_r * 0.45
        _draw_dragon_horn(surface, int(horn_x), int(horn_y), w * 0.28, 90 + side * 30, t, body_accent, lightning)
        # 角尖放电
        tip_x = horn_x + side * w * 0.15
        tip_y = horn_y - h * 0.22
        if (frame + side * 5) % 8 < 3:
            for bolt in range(3):
                b_angle = random.random() * math.pi * 2
                b_len = 8 + random.random() * 8
                pygame.draw.line(surface, lightning,
                               (int(tip_x), int(tip_y)),
                               (int(tip_x + math.cos(b_angle) * b_len), int(tip_y + math.sin(b_angle) * b_len)), 1)
    
    # === 主闪电 ===
    if (frame % 20) < 4:
        bolt_x = cx + random.randint(-int(w * 0.3), int(w * 0.3))
        bolt_pts = [(bolt_x, int(cy - h * 0.45))]
        for i in range(5):
            bolt_pts.append((bolt_pts[-1][0] + random.randint(-12, 12), bolt_pts[-1][1] + int(h * 0.15)))
        pygame.draw.lines(surface, (255, 255, 255), False, bolt_pts, 3)
        pygame.draw.lines(surface, lightning, False, bolt_pts, 1)


def _draw_duke_coral(surface, color, x, y, w, h, frame):
    """珊瑚领主 - 活珊瑚覆甲+寄生生物的礁石巨兽"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    swim = math.sin(t * 2.5) * 3
    
    # 珊瑚礁配色
    body_main = (40, 150, 140)      # 礁石青
    coral_pink = (255, 120, 140)    # 珊瑚粉
    coral_orange = (255, 160, 80)   # 珊瑚橙
    coral_purple = (180, 100, 180)  # 珊瑚紫
    algae_green = (80, 180, 100)    # 藻类绿
    eye_col = (255, 180, 200)       # 粉眼
    
    # === 尾鳍 - 珊瑚生长 ===
    tail_y = cy + h * 0.2 + swim
    tail_pts = [
        (cx, tail_y), (cx - w * 0.12, tail_y + h * 0.12),
        (cx - w * 0.25, tail_y + h * 0.35),
        (cx - w * 0.08, tail_y + h * 0.22),
        (cx, tail_y + h * 0.28),
        (cx + w * 0.08, tail_y + h * 0.22),
        (cx + w * 0.25, tail_y + h * 0.35),
        (cx + w * 0.12, tail_y + h * 0.12),
    ]
    pygame.draw.polygon(surface, body_main, [(int(p[0]), int(p[1])) for p in tail_pts])
    # 尾鳍上的珊瑚
    for i in range(4):
        c_x = cx + (i - 1.5) * w * 0.08
        c_y = tail_y + h * 0.2 + i * 3
        col = [coral_pink, coral_orange, coral_purple][i % 3]
        # 珊瑚分枝
        for branch in range(3):
            b_angle = -math.pi/2 + (branch - 1) * 0.4
            b_len = 8 + branch * 2
            pygame.draw.line(surface, col, (int(c_x), int(c_y)),
                           (int(c_x + math.cos(b_angle) * b_len), int(c_y + math.sin(b_angle) * b_len)), 3)
            pygame.draw.circle(surface, col, (int(c_x + math.cos(b_angle) * b_len), int(c_y + math.sin(b_angle) * b_len)), 3)
    
    # === 背鳍 - 珊瑚林 ===
    for i in range(6):
        spine_x = cx - w * 0.18 + i * w * 0.072
        spine_h = h * (0.2 + math.sin(i * 0.8) * 0.08) + abs(math.sin(t + i)) * 4
        col = [coral_pink, coral_orange, coral_purple, algae_green][i % 4]
        # 珊瑚主干
        pygame.draw.line(surface, col, (int(spine_x), int(cy - h * 0.05 + swim)),
                        (int(spine_x), int(cy - spine_h + swim)), 4)
        # 珊瑚息肉
        for p in range(3):
            p_y = cy - h * 0.05 - spine_h * (p + 1) / 4 + swim
            p_offset = math.sin(t * 2 + p) * 3
            pygame.draw.circle(surface, col, (int(spine_x + p_offset), int(p_y)), 4)
    
    # === 胸鳍 - 海扇珊瑚 ===
    for side in [-1, 1]:
        fin_cx = cx + side * w * 0.3
        fin_cy = cy + swim
        # 扇形珊瑚
        for ray in range(7):
            r_angle = (ray - 3) * 0.15 + side * math.pi / 2
            r_len = w * 0.22 + math.sin(t + ray) * 5
            pygame.draw.line(surface, coral_orange,
                           (int(fin_cx), int(fin_cy)),
                           (int(fin_cx + math.cos(r_angle) * r_len), int(fin_cy + math.sin(r_angle) * r_len)), 2)
        # 扇面填充
        fan_pts = [(int(fin_cx), int(fin_cy))]
        for ray in range(7):
            r_angle = (ray - 3) * 0.15 + side * math.pi / 2
            r_len = w * 0.2
            fan_pts.append((int(fin_cx + math.cos(r_angle) * r_len), int(fin_cy + math.sin(r_angle) * r_len)))
        pygame.draw.polygon(surface, (*coral_pink, 120), fan_pts)
    
    # === 身躯 - 礁石质感 ===
    body_w, body_h = int(w * 0.58), int(h * 0.48)
    pygame.draw.ellipse(surface, body_main,
                       (cx - body_w//2, int(cy - body_h//2 + swim), body_w, body_h))
    # 珊瑚覆盖
    for i in range(8):
        c_x = cx - w * 0.2 + random.random() * w * 0.4
        c_y = cy - h * 0.1 + random.random() * h * 0.25 + swim
        col = [coral_pink, coral_orange, coral_purple][i % 3]
        pygame.draw.circle(surface, col, (int(c_x), int(c_y)), random.randint(3, 6))
    # 藻类条纹
    for i in range(5):
        a_x = cx - w * 0.18 + i * w * 0.09
        a_y = cy + h * 0.05 + swim
        pygame.draw.arc(surface, algae_green, (int(a_x) - 6, int(a_y) - 3, 12, 6), 0, math.pi, 2)
    
    # === 头部 ===
    head_r = int(w * 0.26)
    head_y = cy - h * 0.16 + swim
    pygame.draw.circle(surface, body_main, (cx, int(head_y)), head_r)
    # 头部珊瑚装饰
    for i in range(4):
        d_angle = -math.pi/3 + i * math.pi/6
        d_x = cx + math.cos(d_angle) * head_r * 0.7
        d_y = head_y + math.sin(d_angle) * head_r * 0.5
        col = [coral_pink, coral_orange][i % 2]
        pygame.draw.circle(surface, col, (int(d_x), int(d_y)), 5)
    
    # === 猪鼻 - 海绵质 ===
    snout_w, snout_h = 22, 14
    snout_y = head_y - h * 0.08
    pygame.draw.ellipse(surface, coral_orange, (cx - snout_w//2, int(snout_y) - snout_h//2, snout_w, snout_h))
    # 海绵孔
    for i in range(5):
        hx = cx - 8 + i * 4
        hy = snout_y + random.randint(-3, 3)
        pygame.draw.circle(surface, (200, 100, 80), (int(hx), int(hy)), 2)
    
    # === 眼睛 ===
    for side in [-1, 1]:
        _draw_fishron_eye(surface, cx + side * 14, int(head_y + 4), 9, t, eye_col)
    
    # === 珊瑚龙角 ===
    for side in [-1, 1]:
        horn_x = cx + side * w * 0.16
        horn_y = head_y - head_r * 0.4
        # 珊瑚角
        for branch in range(4):
            b_angle = math.pi/2 + side * 0.3 + (branch - 1.5) * 0.25
            b_len = 15 + branch * 5
            col = [coral_pink, coral_orange, coral_purple][branch % 3]
            pygame.draw.line(surface, col, (int(horn_x), int(horn_y)),
                           (int(horn_x + math.cos(b_angle) * b_len * side), int(horn_y - math.sin(b_angle) * b_len)), 3)
            pygame.draw.circle(surface, col,
                             (int(horn_x + math.cos(b_angle) * b_len * side), int(horn_y - math.sin(b_angle) * b_len)), 4)
    
    # === 寄生小鱼群 ===
    for i in range(5):
        fish_x = cx + w * 0.35 + math.sin(t * 2 + i * 1.2) * 15
        fish_y = cy - h * 0.1 + i * 12 + math.cos(t * 1.5 + i) * 8
        pygame.draw.ellipse(surface, (255, 200, 100), (int(fish_x) - 5, int(fish_y) - 3, 10, 6))
        pygame.draw.circle(surface, (0, 0, 0), (int(fish_x + 3), int(fish_y)), 2)
    
    # === 巨口 ===
    _draw_shark_maw(surface, cx, int(head_y + head_r * 0.6), w * 0.3, h * 0.12, t,
                    teeth_col=(255, 240, 220), gum_col=(200, 100, 120))


def _draw_duke_void_sea(surface, color, x, y, w, h, frame):
    """虚空之海 - 次元裂隙中的星空鳞片巨兽"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    swim = math.sin(t * 2) * 4
    void_pulse = abs(math.sin(t * 1.2)) * 0.4 + 0.6
    
    # 虚空配色
    body_main = (10, 8, 35)         # 虚空黑
    void_purple = (80, 40, 140)     # 虚空紫
    void_pink = (180, 80, 200)      # 裂隙粉
    star_col = (200, 180, 255)      # 星光
    eye_col = (255, 100, 255)       # 虚空眼
    
    # === 虚空残影层 ===
    ghost_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for layer in range(5):
        offset = layer * 6
        alpha = 80 - layer * 15
        ghost_scale = 1 - layer * 0.05
        ghost_w = int(w * 0.5 * ghost_scale)
        ghost_h = int(h * 0.4 * ghost_scale)
        pygame.draw.ellipse(ghost_surf, (*void_purple, alpha),
                          (w//2 - ghost_w//2, int(h * 0.4 + offset - ghost_h//2), ghost_w, ghost_h))
    surface.blit(ghost_surf, (x, y))
    
    # === 次元裂隙背景 ===
    for i in range(6):
        rift_x = cx + math.sin(t + i * 1.1) * w * 0.4
        rift_y = cy + math.cos(t * 0.7 + i) * h * 0.3
        rift_len = 15 + random.random() * 20
        rift_angle = random.random() * math.pi
        pygame.draw.line(surface, void_pink,
                        (int(rift_x), int(rift_y)),
                        (int(rift_x + math.cos(rift_angle) * rift_len), int(rift_y + math.sin(rift_angle) * rift_len)), 2)
    
    # === 尾鳍 - 虚空拖尾 ===
    tail_y = cy + h * 0.2 + swim
    tail_pts = [
        (cx, tail_y), (cx - w * 0.1, tail_y + h * 0.1),
        (cx - w * 0.3, tail_y + h * 0.4),
        (cx - w * 0.05, tail_y + h * 0.2),
        (cx, tail_y + h * 0.35),
        (cx + w * 0.05, tail_y + h * 0.2),
        (cx + w * 0.3, tail_y + h * 0.4),
        (cx + w * 0.1, tail_y + h * 0.1),
    ]
    pygame.draw.polygon(surface, body_main, [(int(p[0]), int(p[1])) for p in tail_pts])
    pygame.draw.polygon(surface, void_purple, [(int(p[0]), int(p[1])) for p in tail_pts], 2)
    
    # === 背鳍 ===
    _draw_dorsal_fin(surface, cx, cy - h * 0.08 + swim, w * 0.7, h * 0.35, t, body_main, void_purple)
    
    # === 胸鳍 - 虚空之翼 ===
    for side in [-1, 1]:
        fin_cx = cx + side * w * 0.24
        _draw_pectoral_fin(surface, fin_cx, int(cy + swim), w * 0.42, 180 + side * 20, t, void_purple, side)
    
    # === 身躯 - 星空鳞片 ===
    body_w, body_h = int(w * 0.58), int(h * 0.48)
    pygame.draw.ellipse(surface, body_main,
                       (cx - body_w//2, int(cy - body_h//2 + swim), body_w, body_h))
    # 星空纹理
    for i in range(25):
        star_x = cx - w * 0.25 + random.random() * w * 0.5
        star_y = cy - h * 0.2 + random.random() * h * 0.4 + swim
        star_r = 1 + random.random() * 2
        star_bright = random.random()
        pygame.draw.circle(surface, (*star_col, int(150 + star_bright * 105)), (int(star_x), int(star_y)), int(star_r))
    # 星云条纹
    for i in range(3):
        nebula_y = cy - h * 0.1 + i * h * 0.1 + swim
        nebula_alpha = int(60 * void_pulse)
        nebula_col = void_pink if i % 2 == 0 else void_purple
        pygame.draw.line(surface, (*nebula_col, nebula_alpha),
                        (cx - w * 0.22, int(nebula_y)), (cx + w * 0.22, int(nebula_y)), 3)
    
    # === 头部 ===
    head_r = int(w * 0.27)
    head_y = cy - h * 0.16 + swim
    pygame.draw.circle(surface, body_main, (cx, int(head_y)), head_r)
    pygame.draw.circle(surface, void_purple, (cx, int(head_y)), head_r, 2)
    # 头部星星
    for i in range(8):
        hs_angle = i * math.pi / 4 + t
        hs_dist = head_r * 0.6
        hs_x = cx + math.cos(hs_angle) * hs_dist
        hs_y = head_y + math.sin(hs_angle) * hs_dist * 0.7
        pygame.draw.circle(surface, star_col, (int(hs_x), int(hs_y)), 2)
    
    # === 猪鼻 ===
    _draw_pig_snout(surface, cx, int(head_y - h * 0.07), 12, t, void_purple, (30, 20, 60))
    
    # === 虚空之眼 - 多重瞳孔 ===
    for side in [-1, 1]:
        ex, ey = cx + side * 15, int(head_y + 3)
        pygame.draw.circle(surface, (20, 15, 50), (ex, ey), 11)
        pygame.draw.circle(surface, eye_col, (ex, ey), 8)
        # 虚空涟漪
        for ring in range(3):
            ring_r = 3 + ring * 3
            pygame.draw.circle(surface, (*void_purple, 150 - ring * 40), (ex, ey), ring_r, 1)
        # 中心黑洞
        pygame.draw.circle(surface, (0, 0, 0), (ex, ey), 4)
        pygame.draw.circle(surface, (255, 255, 255), (ex - 2, ey - 2), 2)
    
    # === 虚空龙角 - 能量晶体 ===
    for side in [-1, 1]:
        horn_x = cx + side * w * 0.17
        horn_y = head_y - head_r * 0.45
        # 晶体角
        crystal_pts = [
            (horn_x, horn_y),
            (horn_x + side * 5, horn_y - 15),
            (horn_x + side * 12, horn_y - 28),
            (horn_x + side * 8, horn_y - 18),
            (horn_x + side * 15, horn_y - 22),
        ]
        pygame.draw.lines(surface, void_pink, False, [(int(p[0]), int(p[1])) for p in crystal_pts], 3)
        # 晶体尖端发光
        pygame.draw.circle(surface, star_col, (int(horn_x + side * 12), int(horn_y - 28)), int(4 * void_pulse))
    
    # === 巨口 ===
    _draw_shark_maw(surface, cx, int(head_y + head_r * 0.55), w * 0.28, h * 0.1, t,
                    teeth_col=(180, 160, 220), gum_col=(50, 30, 80))
    
    # === 虚空能量流 ===
    for i in range(4):
        flow_x = cx + math.sin(t * 2 + i * 1.5) * w * 0.3
        flow_y = cy + h * 0.3 + i * 8
        pygame.draw.circle(surface, (*void_pink, int(120 * void_pulse)), (int(flow_x), int(flow_y)), int(5 * void_pulse))


def _draw_duke_tsunami(surface, color, x, y, w, h, frame):
    """海啸化身 - 水体半透明+浪涛构成的毁灭之浪"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    wave = math.sin(t * 3) * 6
    surge = abs(math.sin(t * 2)) * 0.3 + 0.7
    
    # 海啸配色
    deep_blue = (15, 60, 140)       # 深海蓝
    wave_cyan = (80, 180, 220)      # 浪花青
    foam_white = (220, 245, 255)    # 白沫
    spray_col = (150, 210, 240)     # 水雾
    eye_col = (180, 240, 255)       # 海洋眼
    
    # === 巨浪背景 ===
    wave_bg = pygame.Surface((w, h), pygame.SRCALPHA)
    for layer in range(4):
        wave_y_base = h * 0.3 + layer * 12
        wave_pts = [(0, int(wave_y_base))]
        for wx in range(0, w + 10, 8):
            wy = wave_y_base + math.sin((wx * 0.08 + t * 4 - layer * 0.5)) * (8 + layer * 2)
            wave_pts.append((wx, int(wy)))
        wave_pts.append((w, h))
        wave_pts.append((0, h))
        wave_alpha = 60 - layer * 12
        pygame.draw.polygon(wave_bg, (*wave_cyan, wave_alpha), wave_pts)
    surface.blit(wave_bg, (x, y))
    
    # === 尾鳍 - 浪涛形态 ===
    tail_y = cy + h * 0.18 + wave
    tail_pts = []
    for i in range(12):
        angle = math.pi * 0.3 + i * math.pi * 0.4 / 11
        dist = w * 0.35 + math.sin(t * 3 + i * 0.5) * 8
        tx = cx + math.cos(angle) * dist * 0.3
        ty = tail_y + math.sin(angle) * dist
        tail_pts.append((int(tx), int(ty)))
    pygame.draw.polygon(surface, deep_blue, tail_pts)
    # 浪花边缘
    pygame.draw.lines(surface, foam_white, False, tail_pts, 2)
    
    # === 背鳍 - 浪尖 ===
    for i in range(5):
        crest_x = cx - w * 0.15 + i * w * 0.075
        crest_h = h * (0.3 + math.sin(t * 4 + i) * 0.1) + abs(wave) * 0.5
        # 浪尖三角
        crest_pts = [
            (int(crest_x - 6), int(cy - h * 0.05 + wave)),
            (int(crest_x), int(cy - crest_h + wave)),
            (int(crest_x + 6), int(cy - h * 0.05 + wave)),
        ]
        pygame.draw.polygon(surface, wave_cyan, crest_pts)
        # 浪尖白沫
        pygame.draw.circle(surface, foam_white, (int(crest_x), int(cy - crest_h + wave + 4)), 4)
    
    # === 胸鳍 - 浪臂 ===
    for side in [-1, 1]:
        fin_base = (cx + side * w * 0.22, cy + wave)
        wave_arm_pts = [fin_base]
        for seg in range(6):
            prog = (seg + 1) / 6
            arm_wave = math.sin(t * 3 + seg * 0.8) * 10
            arm_x = fin_base[0] + side * w * 0.4 * prog + arm_wave * side
            arm_y = fin_base[1] + h * 0.1 * prog - abs(arm_wave) * 0.5
            wave_arm_pts.append((int(arm_x), int(arm_y)))
        pygame.draw.lines(surface, deep_blue, False, wave_arm_pts, 6)
        pygame.draw.lines(surface, foam_white, False, wave_arm_pts, 2)
    
    # === 身躯 - 水体半透明 ===
    body_surf = pygame.Surface((int(w * 0.7), int(h * 0.6)), pygame.SRCALPHA)
    body_w, body_h = int(w * 0.58), int(h * 0.48)
    pygame.draw.ellipse(body_surf, (*deep_blue, int(200 * surge)),
                       (int(w * 0.35 - body_w//2), int(h * 0.3 - body_h//2), body_w, body_h))
    # 内部涟漪
    for ring in range(3):
        ring_r = body_w // 3 - ring * 8
        pygame.draw.ellipse(body_surf, (*wave_cyan, 80 - ring * 20),
                          (int(w * 0.35 - ring_r), int(h * 0.3 - ring_r * 0.8), ring_r * 2, int(ring_r * 1.6)), 2)
    surface.blit(body_surf, (x, int(y + wave)))
    
    # === 头部 ===
    head_r = int(w * 0.27)
    head_y_pos = cy - h * 0.16 + wave
    pygame.draw.circle(surface, deep_blue, (cx, int(head_y_pos)), head_r)
    # 水面反光
    pygame.draw.arc(surface, foam_white,
                   (cx - head_r + 5, int(head_y_pos - head_r + 5), head_r * 2 - 10, head_r),
                   0.2, math.pi - 0.2, 2)
    
    # === 猪鼻 - 水泡鼻 ===
    snout_y = head_y_pos - h * 0.08
    pygame.draw.ellipse(surface, wave_cyan, (cx - 11, int(snout_y) - 7, 22, 14))
    # 水泡鼻孔
    for side in [-1, 1]:
        bubble_x = cx + side * 6
        pygame.draw.circle(surface, foam_white, (int(bubble_x), int(snout_y)), 5)
        pygame.draw.circle(surface, (255, 255, 255), (int(bubble_x - 1), int(snout_y - 1)), 2)
    
    # === 海洋之眼 ===
    for side in [-1, 1]:
        ex, ey = cx + side * 15, int(head_y_pos + 4)
        pygame.draw.circle(surface, deep_blue, (ex, ey), 10)
        pygame.draw.circle(surface, eye_col, (ex, ey), 7)
        # 涟漪瞳孔
        pygame.draw.circle(surface, deep_blue, (ex, ey), 4)
        pygame.draw.circle(surface, (255, 255, 255), (ex - 2, ey - 2), 2)
    
    # === 水流龙角 ===
    for side in [-1, 1]:
        horn_x = cx + side * w * 0.16
        horn_y = head_y_pos - head_r * 0.5
        # 水柱角
        for seg in range(5):
            seg_y = horn_y - seg * 8
            seg_w = 6 - seg
            wave_off = math.sin(t * 4 + seg) * 4
            pygame.draw.ellipse(surface, wave_cyan,
                              (int(horn_x + side * wave_off - seg_w), int(seg_y - 3), seg_w * 2, 6))
        # 顶部水花
        for drop in range(3):
            d_angle = -math.pi/2 + (drop - 1) * 0.4
            d_x = horn_x + side * wave_off + math.cos(d_angle) * 8
            d_y = horn_y - 40 + math.sin(d_angle) * 5
            pygame.draw.circle(surface, foam_white, (int(d_x), int(d_y)), 3)
    
    # === 巨口 ===
    _draw_shark_maw(surface, cx, int(head_y_pos + head_r * 0.55), w * 0.28, h * 0.11, t,
                    teeth_col=(220, 240, 255), gum_col=(40, 80, 140))
    
    # === 飞溅水滴 ===
    for i in range(8):
        drop_x = cx + math.sin(t * 3 + i * 0.8) * w * 0.4
        drop_y = cy - h * 0.4 + abs(math.sin(t * 2 + i * 1.2)) * h * 0.3
        drop_r = 2 + abs(math.sin(t + i)) * 2
        pygame.draw.circle(surface, foam_white, (int(drop_x), int(drop_y)), int(drop_r))


def _draw_duke_phantom(surface, color, x, y, w, h, frame):
    """幽魂遗骸 - 骨骼暴露+幽灵残影的亡者龙鱼"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    float_y = math.sin(t * 1.5) * 8
    ghost_pulse = abs(math.sin(t * 1.2)) * 0.3 + 0.7
    
    # 幽魂配色
    bone_white = (220, 215, 200)    # 骨白
    ghost_blue = (120, 180, 220)    # 幽蓝
    soul_cyan = (150, 230, 255)     # 魂火青
    rot_green = (80, 120, 80)       # 腐烂绿
    eye_col = (100, 220, 255)       # 幽魂眼
    
    # === 幽灵残影层 ===
    ghost_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for layer in range(6):
        offset = layer * 8
        alpha = 50 - layer * 8
        g_y = h * 0.4 + offset + float_y
        g_w = w * (0.5 - layer * 0.03)
        pygame.draw.ellipse(ghost_surf, (*ghost_blue, alpha),
                          (int(w//2 - g_w//2), int(g_y), int(g_w), int(h * 0.25)))
    surface.blit(ghost_surf, (x, y))
    
    # === 尾鳍 - 骨质残骸 ===
    tail_y = cy + h * 0.2 + float_y
    # 尾骨
    for i in range(4):
        bone_x = cx + (i - 1.5) * 10
        bone_y = tail_y + i * 8
        pygame.draw.line(surface, bone_white, (int(bone_x), int(bone_y)), (int(bone_x), int(bone_y + 15)), 3)
        pygame.draw.circle(surface, bone_white, (int(bone_x), int(bone_y + 15)), 3)
    # 残留鳍膜
    fin_pts = [
        (cx - 20, tail_y + 10), (cx - 35, tail_y + 40), (cx, tail_y + 30),
        (cx + 35, tail_y + 40), (cx + 20, tail_y + 10)
    ]
    pygame.draw.polygon(surface, (*ghost_blue, int(100 * ghost_pulse)), [(int(p[0]), int(p[1])) for p in fin_pts])
    
    # === 脊椎骨 - 暴露 ===
    spine_start = cy - h * 0.08 + float_y
    for i in range(7):
        vert_x = cx + math.sin(t + i * 0.5) * 3
        vert_y = spine_start - i * 7
        pygame.draw.circle(surface, bone_white, (int(vert_x), int(vert_y)), 5)
        if i > 0:
            prev_x = cx + math.sin(t + (i-1) * 0.5) * 3
            prev_y = spine_start - (i-1) * 7
            pygame.draw.line(surface, bone_white, (int(prev_x), int(prev_y)), (int(vert_x), int(vert_y)), 3)
    
    # === 肋骨架 ===
    for i in range(4):
        rib_y = cy - h * 0.05 + i * 10 + float_y
        for side in [-1, 1]:
            rib_end_x = cx + side * (w * 0.25 - i * 5)
            rib_end_y = rib_y + 8
            pygame.draw.line(surface, bone_white, (cx, int(rib_y)), (int(rib_end_x), int(rib_end_y)), 2)
    
    # === 胸鳍 - 骨翼 ===
    for side in [-1, 1]:
        wing_base = (cx + side * w * 0.2, int(cy + float_y))
        # 翼骨
        for bone in range(4):
            b_angle = math.pi * (0.4 + bone * 0.15) * side
            b_len = w * 0.35 - bone * 8
            b_end = (wing_base[0] + math.cos(b_angle) * b_len, wing_base[1] + math.sin(b_angle) * b_len)
            pygame.draw.line(surface, bone_white, wing_base, (int(b_end[0]), int(b_end[1])), 3)
            pygame.draw.circle(surface, bone_white, (int(b_end[0]), int(b_end[1])), 2)
        # 幽灵翼膜
        wing_pts = [wing_base]
        for bone in range(4):
            b_angle = math.pi * (0.4 + bone * 0.15) * side
            b_len = w * 0.32 - bone * 8
            wing_pts.append((int(wing_base[0] + math.cos(b_angle) * b_len), int(wing_base[1] + math.sin(b_angle) * b_len)))
        pygame.draw.polygon(surface, (*ghost_blue, int(60 * ghost_pulse)), wing_pts)
    
    # === 半腐烂身躯 ===
    body_surf = pygame.Surface((int(w * 0.7), int(h * 0.6)), pygame.SRCALPHA)
    body_w, body_h = int(w * 0.5), int(h * 0.4)
    pygame.draw.ellipse(body_surf, (*ghost_blue, int(120 * ghost_pulse)),
                       (int(w * 0.35 - body_w//2), int(h * 0.3 - body_h//2), body_w, body_h))
    # 腐烂斑块
    for i in range(5):
        rot_x = int(w * 0.35 - w * 0.15 + random.random() * w * 0.3)
        rot_y = int(h * 0.3 - h * 0.1 + random.random() * h * 0.2)
        pygame.draw.circle(body_surf, (*rot_green, 100), (rot_x, rot_y), random.randint(4, 8))
    surface.blit(body_surf, (x, int(y + float_y)))
    
    # === 头骨 ===
    head_r = int(w * 0.26)
    head_y = cy - h * 0.18 + float_y
    pygame.draw.circle(surface, bone_white, (cx, int(head_y)), head_r)
    # 头骨裂纹
    for i in range(4):
        crack_angle = i * math.pi / 2 + 0.3
        crack_len = head_r * 0.6
        pygame.draw.line(surface, (180, 170, 160),
                        (cx, int(head_y)),
                        (int(cx + math.cos(crack_angle) * crack_len), int(head_y + math.sin(crack_angle) * crack_len)), 1)
    
    # === 空洞猪鼻 ===
    snout_y = head_y - h * 0.06
    pygame.draw.ellipse(surface, (180, 175, 165), (cx - 10, int(snout_y) - 6, 20, 12))
    # 黑洞鼻孔
    pygame.draw.circle(surface, (30, 30, 40), (cx - 5, int(snout_y)), 5)
    pygame.draw.circle(surface, (30, 30, 40), (cx + 5, int(snout_y)), 5)
    
    # === 幽魂之眼 - 空洞中的魂火 ===
    for side in [-1, 1]:
        ex, ey = cx + side * 14, int(head_y + 2)
        # 空眼眶
        pygame.draw.circle(surface, (50, 50, 60), (ex, ey), 10)
        # 魂火
        fire_h = int(10 + abs(math.sin(t * 3)) * 6)
        flame_pts = [
            (ex - 4, ey + 3), (ex - 2, ey - fire_h), (ex, ey - fire_h - 4),
            (ex + 2, ey - fire_h), (ex + 4, ey + 3)
        ]
        pygame.draw.polygon(surface, soul_cyan, flame_pts)
        pygame.draw.polygon(surface, (255, 255, 255), [
            (ex - 2, ey), (ex, ey - fire_h * 0.6), (ex + 2, ey)
        ])
    
    # === 断角 ===
    for side in [-1, 1]:
        horn_x = cx + side * w * 0.16
        horn_y = head_y - head_r * 0.4
        # 断裂的骨角
        pygame.draw.polygon(surface, bone_white, [
            (int(horn_x), int(horn_y)),
            (int(horn_x + side * 8), int(horn_y - 18)),
            (int(horn_x + side * 12), int(horn_y - 12)),
            (int(horn_x + side * 5), int(horn_y - 5)),
        ])
        # 断面
        pygame.draw.line(surface, (150, 145, 135), (int(horn_x + side * 8), int(horn_y - 18)), (int(horn_x + side * 12), int(horn_y - 12)), 2)
    
    # === 残牙 ===
    jaw_y = head_y + head_r * 0.5
    for i in range(5):
        if random.random() > 0.3:  # 部分牙齿缺失
            tx = cx - 12 + i * 6
            pygame.draw.polygon(surface, bone_white, [
                (tx - 2, int(jaw_y)), (tx, int(jaw_y + 8)), (tx + 2, int(jaw_y))
            ])
    
    # === 飘散魂火 ===
    for i in range(4):
        soul_x = cx + math.sin(t * 2 + i * 1.5) * w * 0.35
        soul_y = cy - h * 0.3 + math.cos(t * 1.5 + i) * h * 0.2 + float_y
        soul_r = int(5 * ghost_pulse)
        pygame.draw.circle(surface, (*soul_cyan, int(150 * ghost_pulse)), (int(soul_x), int(soul_y)), soul_r)
        pygame.draw.circle(surface, (255, 255, 255), (int(soul_x), int(soul_y)), soul_r // 2)


def _draw_duke_blood_moon(surface, color, x, y, w, h, frame):
    """血月狂潮 - 全身眼球+血泪横流的邪神化身"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    swim = math.sin(t * 2.5) * 4
    blood_pulse = abs(math.sin(t * 1.8)) * 0.4 + 0.6
    
    # 血月配色
    blood_red = (140, 25, 35)       # 血肉红
    dark_blood = (80, 15, 25)       # 暗血
    blood_bright = (220, 60, 80)    # 鲜血
    vein_col = (100, 20, 30)        # 血管
    eye_yellow = (255, 220, 80)     # 血月黄眼
    
    # === 血月光环背景 ===
    moon_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    moon_r = int(w * 0.45 * blood_pulse)
    pygame.draw.circle(moon_surf, (120, 20, 30, 40), (w//2, h//2), moon_r)
    pygame.draw.circle(moon_surf, (180, 40, 50, 60), (w//2, h//2), int(moon_r * 0.7))
    pygame.draw.circle(moon_surf, (220, 60, 70, 80), (w//2, h//2), int(moon_r * 0.4))
    surface.blit(moon_surf, (x, y))
    
    # === 尾鳍 - 血肉撕裂 ===
    tail_y = cy + h * 0.2 + swim
    tail_pts = [
        (cx, tail_y), (cx - w * 0.12, tail_y + h * 0.12),
        (cx - w * 0.3, tail_y + h * 0.38),
        (cx - w * 0.08, tail_y + h * 0.2),
        (cx, tail_y + h * 0.3),
        (cx + w * 0.08, tail_y + h * 0.2),
        (cx + w * 0.3, tail_y + h * 0.38),
        (cx + w * 0.12, tail_y + h * 0.12),
    ]
    pygame.draw.polygon(surface, blood_red, [(int(p[0]), int(p[1])) for p in tail_pts])
    # 尾鳍眼睛
    for i in range(3):
        eye_x = cx + (i - 1) * 15
        eye_y = tail_y + h * 0.18 + i * 5
        pygame.draw.circle(surface, (255, 230, 200), (int(eye_x), int(eye_y)), 6)
        pygame.draw.circle(surface, eye_yellow, (int(eye_x), int(eye_y)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(eye_x), int(eye_y)), 2)
    
    # === 背鳍 - 血肉脊刺 ===
    for i in range(5):
        spine_x = cx - w * 0.15 + i * w * 0.075
        spine_h = h * (0.28 + math.sin(t + i) * 0.05)
        pygame.draw.polygon(surface, blood_bright, [
            (int(spine_x - 5), int(cy - h * 0.06 + swim)),
            (int(spine_x), int(cy - spine_h + swim)),
            (int(spine_x + 5), int(cy - h * 0.06 + swim))
        ])
        # 脊刺上的眼睛
        if i % 2 == 0:
            eye_y_pos = cy - spine_h * 0.6 + swim
            pygame.draw.circle(surface, eye_yellow, (int(spine_x), int(eye_y_pos)), 4)
            pygame.draw.circle(surface, (0, 0, 0), (int(spine_x), int(eye_y_pos)), 2)
    
    # === 胸鳍 - 血翼 ===
    for side in [-1, 1]:
        _draw_pectoral_fin(surface, cx + side * w * 0.22, int(cy + swim), w * 0.45, 190 + side * 10, t, blood_red, side)
        # 翼上眼睛
        for j in range(2):
            wing_eye_x = cx + side * (w * 0.32 + j * 12)
            wing_eye_y = cy + swim + j * 8
            pygame.draw.circle(surface, (255, 230, 200), (int(wing_eye_x), int(wing_eye_y)), 5)
            pygame.draw.circle(surface, eye_yellow, (int(wing_eye_x), int(wing_eye_y)), 3)
            pygame.draw.circle(surface, (0, 0, 0), (int(wing_eye_x), int(wing_eye_y)), 1)
    
    # === 身躯 - 遍布眼球 ===
    body_w, body_h = int(w * 0.58), int(h * 0.5)
    pygame.draw.ellipse(surface, blood_red,
                       (cx - body_w//2, int(cy - body_h//2 + swim), body_w, body_h))
    # 血管网络
    for i in range(8):
        v_start = (cx + random.randint(-body_w//3, body_w//3), int(cy + random.randint(-body_h//4, body_h//4) + swim))
        v_end = (v_start[0] + random.randint(-15, 15), v_start[1] + random.randint(-15, 15))
        pygame.draw.line(surface, vein_col, v_start, v_end, 2)
    # 身体眼睛阵列
    for i in range(7):
        eye_angle = i * math.pi * 2 / 7 + t * 0.5
        eye_dist = body_w * 0.3
        eye_x = cx + math.cos(eye_angle) * eye_dist * 0.8
        eye_y = cy + math.sin(eye_angle) * eye_dist * 0.5 + swim
        eye_size = 5 + abs(math.sin(t + i)) * 3
        pygame.draw.circle(surface, (255, 230, 200), (int(eye_x), int(eye_y)), int(eye_size))
        pygame.draw.circle(surface, eye_yellow, (int(eye_x), int(eye_y)), int(eye_size * 0.7))
        # 瞳孔看向中心
        pupil_off_x = (cx - eye_x) * 0.1
        pupil_off_y = (cy - eye_y) * 0.1
        pygame.draw.circle(surface, (0, 0, 0), (int(eye_x + pupil_off_x), int(eye_y + pupil_off_y)), int(eye_size * 0.3))
    
    # === 头部 ===
    head_r = int(w * 0.28)
    head_y = cy - h * 0.17 + swim
    pygame.draw.circle(surface, blood_red, (cx, int(head_y)), head_r)
    
    # === 主眼 - 巨大血月之眼 ===
    for side in [-1, 1]:
        ex, ey = cx + side * 16, int(head_y + 3)
        pygame.draw.circle(surface, (255, 230, 200), (ex, ey), 12)
        # 血丝
        for j in range(6):
            b_angle = j * math.pi / 3 + t
            bx = ex + math.cos(b_angle) * 10
            by = ey + math.sin(b_angle) * 8
            pygame.draw.line(surface, (180, 40, 50), (ex, ey), (int(bx), int(by)), 1)
        pygame.draw.circle(surface, eye_yellow, (ex, ey), 8)
        # 收缩竖瞳
        pupil_h = int(10 * blood_pulse)
        pygame.draw.ellipse(surface, (0, 0, 0), (ex - 2, ey - pupil_h//2, 4, pupil_h))
        pygame.draw.circle(surface, (255, 255, 255), (ex - 3, ey - 4), 2)
        # 血泪
        for tear in range(3):
            tear_y = ey + 12 + tear * 10 + (frame * 0.8 + side * 20) % 25
            pygame.draw.ellipse(surface, blood_bright, (ex - 2, int(tear_y), 4, 8))
    
    # === 猪鼻 - 血肉溃烂 ===
    snout_y = head_y - h * 0.07
    pygame.draw.ellipse(surface, blood_bright, (cx - 12, int(snout_y) - 7, 24, 14))
    pygame.draw.circle(surface, dark_blood, (cx - 6, int(snout_y)), 5)
    pygame.draw.circle(surface, dark_blood, (cx + 6, int(snout_y)), 5)
    # 鼻孔滴血
    pygame.draw.ellipse(surface, blood_bright, (cx - 8, int(snout_y) + 5, 4, 8))
    pygame.draw.ellipse(surface, blood_bright, (cx + 4, int(snout_y) + 6, 4, 7))
    
    # === 血角 ===
    for side in [-1, 1]:
        horn_x = cx + side * w * 0.17
        horn_y = head_y - head_r * 0.45
        _draw_dragon_horn(surface, int(horn_x), int(horn_y), w * 0.28, 90 + side * 25, t, blood_bright, (255, 100, 100))
        # 角上的眼睛
        pygame.draw.circle(surface, eye_yellow, (int(horn_x + side * 10), int(horn_y - 15)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(horn_x + side * 10), int(horn_y - 15)), 2)
    
    # === 巨口 ===
    _draw_shark_maw(surface, cx, int(head_y + head_r * 0.55), w * 0.3, h * 0.12, t,
                    teeth_col=(255, 240, 220), gum_col=(100, 25, 35))
    
    # === 飘散血滴 ===
    for i in range(10):
        drop_x = cx + math.sin(t * 2 + i) * w * 0.4
        drop_y = cy + h * 0.35 + (frame + i * 15) % 40
        drop_r = int(4 * blood_pulse)
        pygame.draw.circle(surface, blood_bright, (int(drop_x), int(drop_y)), drop_r)


def _draw_duke_tropical(surface, color, x, y, w, h, frame):
    """热带噩梦 - 剧毒色彩+箭毒蛙纹的致命美丽"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    swim = math.sin(t * 3) * 3
    
    # 热带毒物配色 - 警戒色
    poison_yellow = (255, 220, 50)   # 剧毒黄
    toxic_orange = (255, 140, 30)    # 毒橙
    warning_red = (255, 60, 80)      # 警戒红
    venom_purple = (180, 50, 200)    # 毒紫
    deadly_blue = (50, 180, 255)     # 致命蓝
    body_black = (25, 25, 35)        # 深黑底
    eye_col = (255, 80, 150)         # 毒眼
    
    # === 尾鳍 - 毒纹 ===
    tail_y = cy + h * 0.2 + swim
    tail_pts = [
        (cx, tail_y), (cx - w * 0.12, tail_y + h * 0.12),
        (cx - w * 0.28, tail_y + h * 0.38),
        (cx - w * 0.08, tail_y + h * 0.22),
        (cx, tail_y + h * 0.3),
        (cx + w * 0.08, tail_y + h * 0.22),
        (cx + w * 0.28, tail_y + h * 0.38),
        (cx + w * 0.12, tail_y + h * 0.12),
    ]
    pygame.draw.polygon(surface, body_black, [(int(p[0]), int(p[1])) for p in tail_pts])
    # 毒纹条纹
    for i in range(4):
        stripe_y = tail_y + h * 0.1 + i * 8
        stripe_col = [poison_yellow, toxic_orange, warning_red, venom_purple][i]
        pygame.draw.line(surface, stripe_col, (int(cx - 15 + i * 3), int(stripe_y)), (int(cx + 15 - i * 3), int(stripe_y)), 3)
    
    # === 背鳍 - 毒刺 ===
    for i in range(6):
        spine_x = cx - w * 0.18 + i * w * 0.072
        spine_h = h * (0.3 + abs(math.sin(t + i)) * 0.08)
        col = [poison_yellow, toxic_orange, warning_red, venom_purple, deadly_blue, poison_yellow][i]
        # 毒刺
        pygame.draw.polygon(surface, body_black, [
            (int(spine_x - 5), int(cy - h * 0.06 + swim)),
            (int(spine_x), int(cy - spine_h + swim)),
            (int(spine_x + 5), int(cy - h * 0.06 + swim))
        ])
        # 毒刺尖端
        pygame.draw.circle(surface, col, (int(spine_x), int(cy - spine_h + swim)), 5)
        # 滴落毒液
        if i % 2 == 0:
            drip_y = cy - spine_h + swim + 10 + abs(math.sin(t * 2 + i)) * 8
            pygame.draw.ellipse(surface, col, (int(spine_x - 2), int(drip_y), 4, 6))
    
    # === 胸鳍 - 警戒翼 ===
    for side in [-1, 1]:
        fin_base = (cx + side * w * 0.22, int(cy + swim))
        fin_pts = [
            fin_base,
            (int(fin_base[0] + side * w * 0.38), int(fin_base[1] - h * 0.08)),
            (int(fin_base[0] + side * w * 0.35), int(fin_base[1] + h * 0.1)),
            (int(fin_base[0] + side * w * 0.15), int(fin_base[1] + h * 0.08)),
        ]
        pygame.draw.polygon(surface, body_black, fin_pts)
        # 翼上毒斑
        for j in range(3):
            spot_x = fin_base[0] + side * (w * 0.15 + j * 12)
            spot_y = fin_base[1] + j * 3
            spot_col = [poison_yellow, toxic_orange, venom_purple][j]
            pygame.draw.circle(surface, spot_col, (int(spot_x), int(spot_y)), 6)
            pygame.draw.circle(surface, body_black, (int(spot_x), int(spot_y)), 3)
    
    # === 身躯 - 箭毒蛙纹 ===
    body_w, body_h = int(w * 0.58), int(h * 0.5)
    pygame.draw.ellipse(surface, body_black,
                       (cx - body_w//2, int(cy - body_h//2 + swim), body_w, body_h))
    # 毒纹图案
    pattern_colors = [poison_yellow, toxic_orange, warning_red, venom_purple, deadly_blue]
    for i in range(12):
        p_angle = i * math.pi / 6 + t * 0.3
        p_dist = body_w * 0.35 * (0.5 + abs(math.sin(p_angle * 2)) * 0.5)
        p_x = cx + math.cos(p_angle) * p_dist * 0.8
        p_y = cy + math.sin(p_angle) * p_dist * 0.5 + swim
        p_col = pattern_colors[i % 5]
        p_size = 5 + abs(math.sin(t + i)) * 3
        pygame.draw.circle(surface, p_col, (int(p_x), int(p_y)), int(p_size))
    # 中央大斑
    for ring in range(3):
        ring_col = [poison_yellow, toxic_orange, body_black][ring]
        pygame.draw.circle(surface, ring_col, (cx, int(cy + swim)), 12 - ring * 4)
    
    # === 头部 ===
    head_r = int(w * 0.27)
    head_y = cy - h * 0.17 + swim
    pygame.draw.circle(surface, body_black, (cx, int(head_y)), head_r)
    # 头部毒纹
    for i in range(4):
        stripe_angle = i * math.pi / 4 - math.pi / 8
        s_x1 = cx + math.cos(stripe_angle) * head_r * 0.4
        s_y1 = head_y + math.sin(stripe_angle) * head_r * 0.4
        s_x2 = cx + math.cos(stripe_angle) * head_r * 0.9
        s_y2 = head_y + math.sin(stripe_angle) * head_r * 0.6
        pygame.draw.line(surface, [poison_yellow, toxic_orange, venom_purple, deadly_blue][i],
                        (int(s_x1), int(s_y1)), (int(s_x2), int(s_y2)), 4)
    
    # === 毒鼻 ===
    snout_y = head_y - h * 0.07
    pygame.draw.ellipse(surface, toxic_orange, (cx - 11, int(snout_y) - 6, 22, 12))
    pygame.draw.circle(surface, body_black, (cx - 5, int(snout_y)), 4)
    pygame.draw.circle(surface, body_black, (cx + 5, int(snout_y)), 4)
    
    # === 毒眼 ===
    for side in [-1, 1]:
        ex, ey = cx + side * 15, int(head_y + 3)
        pygame.draw.circle(surface, poison_yellow, (ex, ey), 10)
        pygame.draw.circle(surface, eye_col, (ex, ey), 7)
        pygame.draw.ellipse(surface, (0, 0, 0), (ex - 2, ey - 6, 4, 12))
        pygame.draw.circle(surface, (255, 255, 255), (ex - 3, ey - 3), 2)
    
    # === 毒角 ===
    for side in [-1, 1]:
        horn_x = cx + side * w * 0.16
        horn_y = head_y - head_r * 0.45
        # 毒刺角
        for seg in range(4):
            seg_y = horn_y - seg * 10
            seg_col = [body_black, venom_purple, toxic_orange, poison_yellow][seg]
            pygame.draw.circle(surface, seg_col, (int(horn_x + side * seg * 3), int(seg_y)), 5 - seg)
    
    # === 獠牙 ===
    maw_y = head_y + head_r * 0.55
    for i in range(6):
        tx = cx - 15 + i * 6
        pygame.draw.polygon(surface, (255, 255, 255), [
            (tx - 2, int(maw_y)), (tx, int(maw_y + 10)), (tx + 2, int(maw_y))
        ])
        # 毒液
        if i % 2 == 0:
            pygame.draw.circle(surface, venom_purple, (tx, int(maw_y + 12)), 3)
    
    # === 毒气粒子 ===
    for i in range(5):
        gas_x = cx + math.sin(t * 2 + i * 1.3) * w * 0.4
        gas_y = cy - h * 0.35 + math.cos(t * 1.5 + i) * h * 0.15
        gas_col = pattern_colors[i % 5]
        pygame.draw.circle(surface, (*gas_col, 100), (int(gas_x), int(gas_y)), int(6 + abs(math.sin(t + i)) * 4))


def _draw_duke_frost(surface, color, x, y, w, h, frame):
    """霜骨巨兽 - 冰封尸骸+冰晶刺甲的冰河遗物"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    swim = math.sin(t * 2) * 3
    frost_pulse = abs(math.sin(t * 1.5)) * 0.3 + 0.7
    
    # 冰霜配色
    ice_blue = (100, 180, 220)      # 冰蓝
    frost_white = (220, 240, 255)   # 霜白
    deep_ice = (60, 120, 180)       # 深冰
    frozen_flesh = (150, 180, 200)  # 冻肉
    crystal_col = (200, 235, 255)   # 水晶
    eye_col = (180, 230, 255)       # 冰眼
    
    # === 冰雾背景 ===
    mist_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(8):
        mx = w // 2 + math.sin(t + i * 0.8) * w * 0.3
        my = h // 2 + math.cos(t * 0.7 + i) * h * 0.25
        mr = 15 + abs(math.sin(t + i)) * 10
        pygame.draw.circle(mist_surf, (200, 230, 255, 30), (int(mx), int(my)), int(mr))
    surface.blit(mist_surf, (x, y))
    
    # === 尾鳍 - 冰晶碎片 ===
    tail_y = cy + h * 0.2 + swim
    # 冰碎尾鳍
    for i in range(5):
        shard_x = cx + (i - 2) * 12
        shard_y = tail_y + abs(i - 2) * 8
        shard_h = 25 - abs(i - 2) * 5
        shard_pts = [
            (shard_x - 4, shard_y),
            (shard_x, shard_y + shard_h),
            (shard_x + 4, shard_y),
            (shard_x, shard_y - 5),
        ]
        pygame.draw.polygon(surface, crystal_col, [(int(p[0]), int(p[1])) for p in shard_pts])
        pygame.draw.polygon(surface, frost_white, [(int(p[0]), int(p[1])) for p in shard_pts], 1)
    
    # === 背鳍 - 冰晶刺甲 ===
    for i in range(7):
        crystal_x = cx - w * 0.2 + i * w * 0.067
        crystal_h = h * (0.25 + math.sin(i * 0.7) * 0.1) + abs(math.sin(t + i)) * 5
        # 主冰晶
        pts = [
            (crystal_x - 5, cy - h * 0.05 + swim),
            (crystal_x - 2, cy - crystal_h + swim),
            (crystal_x + 2, cy - crystal_h + swim),
            (crystal_x + 5, cy - h * 0.05 + swim),
        ]
        pygame.draw.polygon(surface, deep_ice, [(int(p[0]), int(p[1])) for p in pts])
        pygame.draw.polygon(surface, frost_white, [(int(p[0]), int(p[1])) for p in pts], 1)
        # 晶体反光
        pygame.draw.line(surface, (255, 255, 255), 
                        (int(crystal_x - 1), int(cy - crystal_h * 0.3 + swim)),
                        (int(crystal_x - 1), int(cy - crystal_h * 0.7 + swim)), 1)
    
    # === 胸鳍 - 冰翼 ===
    for side in [-1, 1]:
        fin_base = (cx + side * w * 0.22, int(cy + swim))
        # 冰晶翼
        wing_pts = [fin_base]
        for seg in range(5):
            seg_angle = math.pi * (0.35 + seg * 0.08) * side
            seg_len = w * (0.35 - seg * 0.05)
            wing_pts.append((
                int(fin_base[0] + math.cos(seg_angle) * seg_len),
                int(fin_base[1] + math.sin(seg_angle) * seg_len)
            ))
        pygame.draw.polygon(surface, (*deep_ice, 180), wing_pts)
        pygame.draw.lines(surface, frost_white, True, wing_pts, 2)
        # 翼骨冰晶
        for seg in range(3):
            bone_angle = math.pi * (0.4 + seg * 0.1) * side
            bone_len = w * 0.3
            bone_end = (fin_base[0] + math.cos(bone_angle) * bone_len, fin_base[1] + math.sin(bone_angle) * bone_len)
            pygame.draw.line(surface, crystal_col, fin_base, (int(bone_end[0]), int(bone_end[1])), 3)
    
    # === 身躯 - 冻结肌肉 ===
    body_w, body_h = int(w * 0.58), int(h * 0.48)
    pygame.draw.ellipse(surface, frozen_flesh,
                       (cx - body_w//2, int(cy - body_h//2 + swim), body_w, body_h))
    # 冰裂纹
    for i in range(6):
        crack_start = (cx + random.randint(-body_w//3, body_w//3), int(cy + random.randint(-body_h//4, body_h//4) + swim))
        crack_end = (crack_start[0] + random.randint(-12, 12), crack_start[1] + random.randint(-12, 12))
        pygame.draw.line(surface, ice_blue, crack_start, crack_end, 2)
    # 冰晶覆盖
    for i in range(5):
        ice_x = cx - w * 0.15 + i * w * 0.075
        ice_y = cy + h * 0.08 + swim
        pygame.draw.polygon(surface, crystal_col, [
            (int(ice_x), int(ice_y - 8)), (int(ice_x - 4), int(ice_y)), (int(ice_x + 4), int(ice_y))
        ])
    
    # === 头部 - 冰封 ===
    head_r = int(w * 0.27)
    head_y = cy - h * 0.17 + swim
    pygame.draw.circle(surface, frozen_flesh, (cx, int(head_y)), head_r)
    # 冰霜覆盖
    frost_arc_rect = (cx - head_r, int(head_y - head_r), head_r * 2, head_r * 2)
    pygame.draw.arc(surface, frost_white, frost_arc_rect, 0.3, math.pi - 0.3, 3)
    
    # === 冰鼻 ===
    snout_y = head_y - h * 0.07
    pygame.draw.ellipse(surface, ice_blue, (cx - 11, int(snout_y) - 6, 22, 12))
    # 冻结鼻孔
    pygame.draw.circle(surface, deep_ice, (cx - 5, int(snout_y)), 4)
    pygame.draw.circle(surface, deep_ice, (cx + 5, int(snout_y)), 4)
    # 鼻息冰雾
    for i in range(3):
        breath_y = snout_y - 5 - i * 6
        breath_x = cx + math.sin(t * 3 + i) * 4
        pygame.draw.circle(surface, (*frost_white, 150 - i * 40), (int(breath_x), int(breath_y)), 4 - i)
    
    # === 冰眼 ===
    for side in [-1, 1]:
        ex, ey = cx + side * 15, int(head_y + 3)
        pygame.draw.circle(surface, frost_white, (ex, ey), 10)
        pygame.draw.circle(surface, eye_col, (ex, ey), 7)
        # 冰晶瞳孔
        pygame.draw.polygon(surface, deep_ice, [
            (ex, ey - 5), (ex - 3, ey), (ex, ey + 5), (ex + 3, ey)
        ])
        pygame.draw.circle(surface, (255, 255, 255), (ex - 2, ey - 2), 2)
    
    # === 冰晶龙角 ===
    for side in [-1, 1]:
        horn_x = cx + side * w * 0.16
        horn_y = head_y - head_r * 0.45
        # 大冰晶角
        crystal_pts = [
            (horn_x, horn_y),
            (horn_x + side * 3, horn_y - 20),
            (horn_x + side * 8, horn_y - 35),
            (horn_x + side * 5, horn_y - 25),
            (horn_x + side * 12, horn_y - 28),
            (horn_x + side * 6, horn_y - 15),
        ]
        pygame.draw.polygon(surface, crystal_col, [(int(p[0]), int(p[1])) for p in crystal_pts])
        pygame.draw.polygon(surface, (255, 255, 255), [(int(p[0]), int(p[1])) for p in crystal_pts], 1)
    
    # === 冰牙 ===
    maw_y = head_y + head_r * 0.55
    for i in range(7):
        tx = cx - 18 + i * 6
        fang_h = 10 + abs(3 - i) * 1.5
        pygame.draw.polygon(surface, frost_white, [
            (tx - 2, int(maw_y)), (tx, int(maw_y + fang_h)), (tx + 2, int(maw_y))
        ])
    
    # === 霜花粒子 ===
    for i in range(8):
        flake_x = cx + math.sin(t * 2 + i * 0.9) * w * 0.45
        flake_y = cy + math.cos(t * 1.5 + i * 1.1) * h * 0.35
        # 六角雪花
        for ray in range(6):
            ray_angle = ray * math.pi / 3
            ray_len = 4 * frost_pulse
            pygame.draw.line(surface, (255, 255, 255),
                           (int(flake_x), int(flake_y)),
                           (int(flake_x + math.cos(ray_angle) * ray_len), int(flake_y + math.sin(ray_angle) * ray_len)), 1)


def _draw_duke_golden(surface, color, x, y, w, h, frame):
    """黄金暴君 - 远古帝王+珠宝镶嵌的深海至尊"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    swim = math.sin(t * 2.5) * 3
    gold_shine = abs(math.sin(t * 1.8)) * 0.4 + 0.6
    
    # 黄金配色
    gold_main = (220, 175, 50)      # 皇金
    gold_bright = (255, 220, 100)   # 亮金
    gold_dark = (180, 140, 30)      # 暗金
    gold_white = (255, 250, 220)    # 金光
    ruby_col = (220, 40, 60)        # 红宝石
    sapphire_col = (50, 120, 220)   # 蓝宝石
    emerald_col = (50, 200, 100)    # 绿宝石
    eye_col = (255, 100, 50)        # 烈焰眼
    
    # === 金光背景 ===
    glow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    glow_r = int(w * 0.5 * gold_shine)
    pygame.draw.circle(glow_surf, (255, 220, 100, 30), (w//2, h//2), glow_r)
    pygame.draw.circle(glow_surf, (255, 240, 150, 50), (w//2, h//2), int(glow_r * 0.6))
    surface.blit(glow_surf, (x, y))
    
    # === 尾鳍 - 黄金扇 ===
    tail_y = cy + h * 0.2 + swim
    tail_pts = [
        (cx, tail_y), (cx - w * 0.1, tail_y + h * 0.1),
        (cx - w * 0.3, tail_y + h * 0.4),
        (cx - w * 0.05, tail_y + h * 0.2),
        (cx, tail_y + h * 0.32),
        (cx + w * 0.05, tail_y + h * 0.2),
        (cx + w * 0.3, tail_y + h * 0.4),
        (cx + w * 0.1, tail_y + h * 0.1),
    ]
    pygame.draw.polygon(surface, gold_main, [(int(p[0]), int(p[1])) for p in tail_pts])
    pygame.draw.polygon(surface, gold_bright, [(int(p[0]), int(p[1])) for p in tail_pts], 2)
    # 尾鳍宝石
    for i in range(3):
        gem_x = cx + (i - 1) * 18
        gem_y = tail_y + h * 0.22 + abs(i - 1) * 8
        gem_col = [ruby_col, sapphire_col, emerald_col][i]
        pygame.draw.circle(surface, gem_col, (int(gem_x), int(gem_y)), 5)
        pygame.draw.circle(surface, gold_bright, (int(gem_x), int(gem_y)), 5, 1)
        pygame.draw.circle(surface, (255, 255, 255), (int(gem_x - 1), int(gem_y - 1)), 1)
    
    # === 背鳍 - 黄金冠刺 ===
    for i in range(6):
        spine_x = cx - w * 0.17 + i * w * 0.068
        spine_h = h * (0.3 + math.sin(i * 0.6) * 0.08)
        # 金刺
        pygame.draw.polygon(surface, gold_main, [
            (int(spine_x - 5), int(cy - h * 0.06 + swim)),
            (int(spine_x), int(cy - spine_h + swim)),
            (int(spine_x + 5), int(cy - h * 0.06 + swim))
        ])
        pygame.draw.polygon(surface, gold_bright, [
            (int(spine_x - 5), int(cy - h * 0.06 + swim)),
            (int(spine_x), int(cy - spine_h + swim)),
            (int(spine_x + 5), int(cy - h * 0.06 + swim))
        ], 1)
        # 刺顶宝石
        gem_col = [ruby_col, sapphire_col, emerald_col][i % 3]
        pygame.draw.circle(surface, gem_col, (int(spine_x), int(cy - spine_h + swim + 5)), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(spine_x - 1), int(cy - spine_h + swim + 4)), 1)
    
    # === 胸鳍 - 黄金龙翼 ===
    for side in [-1, 1]:
        fin_base = (cx + side * w * 0.22, int(cy + swim))
        fin_pts = [
            fin_base,
            (int(fin_base[0] + side * w * 0.4), int(fin_base[1] - h * 0.1)),
            (int(fin_base[0] + side * w * 0.38), int(fin_base[1] + h * 0.08)),
            (int(fin_base[0] + side * w * 0.2), int(fin_base[1] + h * 0.1)),
        ]
        pygame.draw.polygon(surface, gold_main, fin_pts)
        pygame.draw.polygon(surface, gold_bright, fin_pts, 2)
        # 翼骨金线
        for bone in range(3):
            bone_end = (fin_base[0] + side * w * (0.15 + bone * 0.1), fin_base[1] + bone * 3)
            pygame.draw.line(surface, gold_bright, fin_base, (int(bone_end[0]), int(bone_end[1])), 2)
        # 翼上宝石
        for j in range(2):
            wing_gem_x = fin_base[0] + side * (w * 0.2 + j * 15)
            wing_gem_y = fin_base[1] + j * 5
            pygame.draw.circle(surface, sapphire_col, (int(wing_gem_x), int(wing_gem_y)), 4)
            pygame.draw.circle(surface, (255, 255, 255), (int(wing_gem_x - 1), int(wing_gem_y - 1)), 1)
    
    # === 身躯 - 黄金鳞甲 ===
    body_w, body_h = int(w * 0.58), int(h * 0.5)
    pygame.draw.ellipse(surface, gold_main,
                       (cx - body_w//2, int(cy - body_h//2 + swim), body_w, body_h))
    # 金鳞纹理
    for row in range(3):
        for i in range(5):
            scale_x = cx - w * 0.18 + i * w * 0.09
            scale_y = cy - h * 0.08 + row * h * 0.1 + swim
            pygame.draw.arc(surface, gold_bright,
                          (int(scale_x - 7), int(scale_y - 4), 14, 8), 0, math.pi, 2)
    # 腹部金带
    pygame.draw.ellipse(surface, gold_bright,
                       (cx - body_w//3, int(cy + h * 0.02 + swim), body_w * 2//3, body_h//4))
    # 身体宝石镶嵌
    gem_positions = [(0, -0.08), (-0.12, 0), (0.12, 0), (0, 0.1)]
    for i, (gx, gy) in enumerate(gem_positions):
        gem_abs_x = cx + w * gx
        gem_abs_y = cy + h * gy + swim
        gem_col = [ruby_col, sapphire_col, emerald_col, ruby_col][i]
        pygame.draw.circle(surface, gem_col, (int(gem_abs_x), int(gem_abs_y)), 6)
        pygame.draw.circle(surface, gold_bright, (int(gem_abs_x), int(gem_abs_y)), 6, 1)
        pygame.draw.circle(surface, (255, 255, 255), (int(gem_abs_x - 2), int(gem_abs_y - 2)), 2)
    
    # === 头部 ===
    head_r = int(w * 0.28)
    head_y = cy - h * 0.17 + swim
    pygame.draw.circle(surface, gold_main, (cx, int(head_y)), head_r)
    pygame.draw.circle(surface, gold_bright, (cx, int(head_y)), head_r, 2)
    # 头部高光
    pygame.draw.arc(surface, gold_white,
                   (cx - head_r + 5, int(head_y - head_r + 5), head_r * 2 - 10, head_r - 5),
                   0.2, math.pi - 0.2, 2)
    
    # === 黄金猪鼻 ===
    snout_y = head_y - h * 0.07
    pygame.draw.ellipse(surface, gold_bright, (cx - 12, int(snout_y) - 7, 24, 14))
    pygame.draw.ellipse(surface, gold_dark, (cx - 12, int(snout_y) - 7, 24, 14), 2)
    pygame.draw.circle(surface, gold_dark, (cx - 5, int(snout_y)), 4)
    pygame.draw.circle(surface, gold_dark, (cx + 5, int(snout_y)), 4)
    # 鼻环
    pygame.draw.circle(surface, gold_bright, (cx, int(snout_y + 5)), 6, 2)
    pygame.draw.circle(surface, ruby_col, (cx, int(snout_y + 5)), 3)
    
    # === 帝王皇冠 ===
    crown_y = head_y - head_r - 3
    crown_pts = [
        (cx - 20, crown_y + 12),
        (cx - 20, crown_y + 6),
        (cx - 14, crown_y - 2),
        (cx - 8, crown_y + 4),
        (cx, crown_y - 10),
        (cx + 8, crown_y + 4),
        (cx + 14, crown_y - 2),
        (cx + 20, crown_y + 6),
        (cx + 20, crown_y + 12),
    ]
    pygame.draw.polygon(surface, gold_main, [(int(p[0]), int(p[1])) for p in crown_pts])
    pygame.draw.polygon(surface, gold_bright, [(int(p[0]), int(p[1])) for p in crown_pts], 2)
    # 皇冠宝石
    pygame.draw.circle(surface, ruby_col, (cx, int(crown_y - 5)), 5)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 1, int(crown_y - 6)), 2)
    pygame.draw.circle(surface, sapphire_col, (cx - 14, int(crown_y)), 3)
    pygame.draw.circle(surface, sapphire_col, (cx + 14, int(crown_y)), 3)
    pygame.draw.circle(surface, emerald_col, (cx - 8, int(crown_y + 3)), 3)
    pygame.draw.circle(surface, emerald_col, (cx + 8, int(crown_y + 3)), 3)
    
    # === 黄金龙眼 ===
    for side in [-1, 1]:
        ex, ey = cx + side * 16, int(head_y + 3)
        pygame.draw.circle(surface, gold_white, (ex, ey), 10)
        pygame.draw.circle(surface, eye_col, (ex, ey), 7)
        pygame.draw.ellipse(surface, (0, 0, 0), (ex - 2, ey - 6, 4, 12))
        pygame.draw.circle(surface, (255, 255, 255), (ex - 3, ey - 3), 2)
        # 眼眶金边
        pygame.draw.circle(surface, gold_bright, (ex, ey), 10, 2)
    
    # === 黄金龙角 ===
    for side in [-1, 1]:
        horn_x = cx + side * w * 0.18
        horn_y = head_y - head_r * 0.4
        # 金角
        _draw_dragon_horn(surface, int(horn_x), int(horn_y), w * 0.32, 90 + side * 25, t, gold_main, gold_bright)
        # 角上宝石
        for gem_i in range(2):
            gem_dist = 12 + gem_i * 12
            gem_angle = math.radians(90 + side * 25)
            gx = horn_x + math.cos(gem_angle) * gem_dist * side * 0.3
            gy = horn_y - math.sin(gem_angle) * gem_dist
            pygame.draw.circle(surface, ruby_col if gem_i == 0 else emerald_col, (int(gx), int(gy)), 3)
    
    # === 黄金獠牙 ===
    maw_y = head_y + head_r * 0.55
    for i in range(8):
        tx = cx - 21 + i * 6
        fang_h = 10 + abs(3.5 - i) * 2
        pygame.draw.polygon(surface, gold_white, [
            (tx - 2, int(maw_y)), (tx, int(maw_y + fang_h)), (tx + 2, int(maw_y))
        ])
    
    # === 金光闪烁 ===
    sparkle_phase = (frame % 25)
    if sparkle_phase < 8:
        for i in range(6):
            sx = cx + math.sin(t * 3 + i * 1.1) * w * 0.4
            sy = cy + math.cos(t * 2 + i * 1.3) * h * 0.35 + swim
            # 十字星芒
            star_size = int(5 * gold_shine)
            pygame.draw.line(surface, gold_white, (int(sx - star_size), int(sy)), (int(sx + star_size), int(sy)), 2)
            pygame.draw.line(surface, gold_white, (int(sx), int(sy - star_size)), (int(sx), int(sy + star_size)), 2)
            pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), 2)
