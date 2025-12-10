# Mirage 专属涂装渲染模块
# 包含: mirage_kaleidoscope, mirage_fractal, mirage_butterfly, mirage_crystal_palace,
#       mirage_funhouse, mirage_doppelganger, mirage_infinity_room, mirage_alice,
#       mirage_narcissus, mirage_hologram, mirage_phantom_opera, mirage_ouroboros

import pygame
import math
import random

# Mirage涂装列表
MIRAGE_STYLES = [
    "mirage_kaleidoscope", "mirage_fractal", "mirage_butterfly", "mirage_crystal_palace",
    "mirage_funhouse", "mirage_doppelganger", "mirage_infinity_room", "mirage_alice",
    "mirage_narcissus", "mirage_hologram", "mirage_phantom_opera", "mirage_ouroboros"
]

def is_mirage_style(model_style):
    """检查是否为Mirage涂装"""
    return model_style in MIRAGE_STYLES

def render_mirage_skin(s, c, model_style, t, pid, static=False):
    """渲染Mirage涂装，返回Surface或None"""
    pulse = math.sin(t * 2) * 0.15 + 1
    
    if model_style == "mirage_kaleidoscope":
        # 万花筒梦·色彩轮转 - 经典万花筒旋转图案
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        rotation = t * 30
        # 12个彩色扇区
        segment_colors = [
            (255, 100, 100), (255, 180, 100), (255, 255, 100),
            (180, 255, 100), (100, 255, 100), (100, 255, 180),
            (100, 255, 255), (100, 180, 255), (100, 100, 255),
            (180, 100, 255), (255, 100, 255), (255, 100, 180)
        ]
        for seg_i in range(12):
            seg_angle = (seg_i * 30 + rotation) * 0.01745
            next_angle = ((seg_i + 1) * 30 + rotation) * 0.01745
            # 扇形顶点
            pts = [(60, 60)]
            for a in range(int(seg_angle * 57.3), int(next_angle * 57.3) + 1, 5):
                rad = a * 0.01745
                pts.append((60 + math.cos(rad) * 45, 60 + math.sin(rad) * 45))
            if len(pts) > 2:
                pygame.draw.polygon(s, segment_colors[seg_i], pts)
        # 内圈花纹
        for inner_i in range(6):
            inner_angle = (inner_i * 60 + rotation * 2) * 0.01745
            ix = 60 + math.cos(inner_angle) * 20
            iy = 60 + math.sin(inner_angle) * 20
            pygame.draw.circle(s, (255, 220, 180), (int(ix), int(iy)), 6)
        # 中心宝石
        pygame.draw.circle(s, (255, 200, 150), (60, 60), 10)
        pygame.draw.circle(s, (255, 220, 180), (60, 60), 6)
        return s

    elif model_style == "mirage_crystal_palace":
        # 水晶宫殿·冰雕折射 - 冰雪水晶，七色折射
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 16根冰柱（环绕）
        for column_i in range(16):
            col_angle = (column_i * 22.5 + t * 3) * 0.01745
            col_r = 35
            col_x = 60 + math.cos(col_angle) * col_r
            col_y = 60 + math.sin(col_angle) * col_r
            col_height = 15 + int(5 * math.sin(t * 2 + column_i))
            # 冰柱（梯形）
            col_pts = [
                (col_x - 3, col_y + 5),
                (col_x - 2, col_y - col_height),
                (col_x + 2, col_y - col_height),
                (col_x + 3, col_y + 5)
            ]
            pygame.draw.polygon(s, (200, 240, 255), col_pts)
            pygame.draw.polygon(s, (220, 250, 255), col_pts, 1)
        # 8道折射光线
        for beam_i in range(8):
            beam_angle = (beam_i * 45 + t * 20) * 0.01745
            beam_x = 60 + math.cos(beam_angle) * 50
            beam_y = 60 + math.sin(beam_angle) * 50
            rainbow_colors = [(255, 200, 200), (255, 255, 200), (200, 255, 200),
                             (200, 255, 255), (200, 200, 255), (255, 200, 255)]
            beam_color = rainbow_colors[beam_i % 6]
            pygame.draw.line(s, beam_color, (60, 60), (beam_x, beam_y), 2)
        # 中心水晶核心
        pygame.draw.polygon(s, (180, 220, 250), [(60, 45), (50, 60), (60, 75), (70, 60)])
        pygame.draw.polygon(s, (220, 250, 255), [(60, 45), (50, 60), (60, 75), (70, 60)], 2)
        return s

    elif model_style == "mirage_funhouse":
        # 哈哈镜屋·扭曲现实 - 扭曲变形镜像
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        warp_phase = t * 3
        # 6面哈哈镜（扭曲波浪边框）
        for mirror_i in range(6):
            m_angle = (mirror_i * 60) * 0.01745
            m_x = 60 + math.cos(m_angle) * 35
            m_y = 60 + math.sin(m_angle) * 35
            # 波浪形边框
            wave_pts = []
            for seg in range(12):
                seg_angle = (seg * 30) * 0.01745
                warp = 3 * math.sin(warp_phase + seg + mirror_i)
                wx = m_x + math.cos(seg_angle) * (12 + warp)
                wy = m_y + math.sin(seg_angle) * (12 + warp)
                wave_pts.append((int(wx), int(wy)))
            pygame.draw.polygon(s, (255, 180, 130), wave_pts, 2)
            pygame.draw.circle(s, (255, 150, 100, 100), (int(m_x), int(m_y)), 10)
        # 扭曲反射线
        for warp_line in range(12):
            wl_angle = (warp_line * 30 + t * 15) * 0.01745
            wl_x = 60 + math.cos(wl_angle) * 45
            wl_y = 60 + math.sin(wl_angle) * 45
            warp_offset = 5 * math.sin(t * 4 + warp_line)
            pygame.draw.line(s, (230, 130, 80), (60, 60), 
                           (wl_x + warp_offset, wl_y + warp_offset), 1)
        # 中心笑脸（变形）
        pygame.draw.circle(s, (255, 150, 100), (60, 60), 15)
        pygame.draw.circle(s, (255, 180, 130), (60, 60), 12)
        return s

    elif model_style == "mirage_doppelganger":
        # 二重身影·暗夜替身 - 神秘暗影分身
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        shadow_delay = t * 0.5
        # 主体轮廓（暗色）
        pygame.draw.circle(s, (80, 60, 100), (60, 55), 25)
        pygame.draw.ellipse(s, (80, 60, 100), (45, 60, 30, 40))
        # 延迟影子（偏移）
        shadow_offset = 5 + int(3 * math.sin(shadow_delay))
        pygame.draw.circle(s, (60, 40, 80, 150), (60 + shadow_offset, 55 + shadow_offset), 25)
        pygame.draw.ellipse(s, (60, 40, 80, 150), (45 + shadow_offset, 60 + shadow_offset, 30, 40))
        # 诡异眼睛
        pygame.draw.circle(s, (150, 100, 200), (52, 52), 4)
        pygame.draw.circle(s, (150, 100, 200), (68, 52), 4)
        pygame.draw.circle(s, (200, 150, 255), (52, 52), 2)
        pygame.draw.circle(s, (200, 150, 255), (68, 52), 2)
        # 暗雾粒子
        for fog_i in range(20):
            fog_angle = (fog_i * 18 + t * 8) * 0.01745
            fog_r = 35 + int(10 * math.sin(t + fog_i))
            fog_x = 60 + math.cos(fog_angle) * fog_r
            fog_y = 60 + math.sin(fog_angle) * fog_r
            pygame.draw.circle(s, (60, 40, 80, 80), (int(fog_x), int(fog_y)), 4)
        return s

    elif model_style == "mirage_infinity_room":
        # 无限镜室·永恒延伸 - 草间弥生风格，无限点阵
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 100个光点（模拟无限镜室）
        for dot_i in range(100):
            # 伪3D深度效果
            depth = (dot_i % 10) / 10
            dot_angle = (dot_i * 36 + t * 5) * 0.01745
            dot_r = 10 + depth * 35
            dot_x = 60 + math.cos(dot_angle) * dot_r
            dot_y = 60 + math.sin(dot_angle) * dot_r
            dot_size = int(4 * (1 - depth * 0.5))
            dot_alpha = int(255 * (1 - depth * 0.7))
            if dot_size > 0:
                # 彩色点
                hue_shift = (dot_i * 3.6 + t * 20) % 360
                r = int(255 * (1 if hue_shift < 120 or hue_shift > 240 else 0))
                g = int(255 * (1 if 60 < hue_shift < 180 else 0))
                b = int(255 * (1 if hue_shift > 180 else 0))
                pygame.draw.circle(s, (max(r, 100), max(g, 100), max(b, 150), dot_alpha), 
                                  (int(dot_x), int(dot_y)), dot_size)
        # 中心红色大点
        pygame.draw.circle(s, (255, 100, 150), (60, 60), 10)
        pygame.draw.circle(s, (255, 130, 180), (60, 60), 6)
        return s

    elif model_style == "mirage_alice":
        # 镜中奇遇·爱丽丝门 - 爱丽丝梦游仙境风格
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 魔镜门框（椭圆）
        pygame.draw.ellipse(s, (200, 150, 100), (25, 20, 70, 80), 4)
        pygame.draw.ellipse(s, (255, 200, 150), (30, 25, 60, 70), 2)
        # 镜中漩涡
        for swirl in range(8):
            swirl_angle = (swirl * 45 + t * 30) * 0.01745
            swirl_r = 5 + swirl * 3
            sx = 60 + math.cos(swirl_angle) * swirl_r
            sy = 60 + math.sin(swirl_angle) * swirl_r
            pygame.draw.circle(s, (255, 100, 100), (int(sx), int(sy)), 3)
        # 8个扑克牌士兵
        for card_i in range(8):
            card_angle = (card_i * 45 + t * 10) * 0.01745
            card_r = 42
            card_x = 60 + math.cos(card_angle) * card_r
            card_y = 60 + math.sin(card_angle) * card_r
            # 红心或黑桃
            card_color = (255, 100, 100) if card_i % 2 == 0 else (50, 50, 50)
            pygame.draw.rect(s, (255, 255, 255), (int(card_x) - 4, int(card_y) - 6, 8, 12))
            pygame.draw.circle(s, card_color, (int(card_x), int(card_y)), 3)
        # 茶杯
        pygame.draw.ellipse(s, (200, 180, 150), (52, 70, 16, 10))
        pygame.draw.rect(s, (200, 180, 150), (54, 65, 12, 10))
        return s

    elif model_style == "mirage_narcissus":
        # 水仙倒影·自恋之池 - 水面倒影，涟漪效果
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 8圈涟漪
        for ripple_i in range(8):
            ripple_phase = (t * 2 + ripple_i * 0.3) % 1.0
            ripple_r = int(10 + ripple_phase * 40)
            ripple_alpha = int(150 * (1 - ripple_phase))
            if ripple_alpha > 0:
                pygame.draw.circle(s, (160, 200, 240, ripple_alpha), (60, 60), ripple_r, 2)
        # 水仙花倒影（上下对称）
        # 上半（正像）
        pygame.draw.circle(s, (255, 255, 200), (60, 40), 8)  # 花心
        for petal in range(6):
            petal_angle = (petal * 60) * 0.01745
            px = 60 + math.cos(petal_angle) * 12
            py = 40 + math.sin(petal_angle) * 12
            pygame.draw.circle(s, (255, 255, 220), (int(px), int(py)), 5)
        # 下半（倒影，稍微模糊）
        pygame.draw.circle(s, (200, 220, 255, 150), (60, 80), 8)
        for petal in range(6):
            petal_angle = (petal * 60) * 0.01745
            px = 60 + math.cos(petal_angle) * 12
            py = 80 - math.sin(petal_angle) * 12
            pygame.draw.circle(s, (200, 220, 255, 150), (int(px), int(py)), 5)
        # 花茎
        pygame.draw.line(s, (100, 180, 100), (60, 48), (60, 72), 2)
        return s

    elif model_style == "mirage_hologram":
        # 全息投影·未来幻象 - 科幻全息效果
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 48条扫描线
        for scan_i in range(48):
            scan_y = 10 + scan_i * 2
            scan_alpha = 100 + int(50 * math.sin(t * 5 + scan_i * 0.2))
            pygame.draw.line(s, (100, 200, 255, scan_alpha), (20, scan_y), (100, scan_y), 1)
        # 全息轮廓（三角形机体）
        glitch_offset = int(3 * math.sin(t * 10))
        holo_pts = [(60 + glitch_offset, 30), (35, 80), (85, 80)]
        pygame.draw.polygon(s, (100, 200, 255, 150), holo_pts)
        pygame.draw.polygon(s, (130, 220, 255), holo_pts, 2)
        # 故障效果（闪烁条纹）
        if int(t * 10) % 5 == 0:
            glitch_y = random.randint(30, 80)
            pygame.draw.rect(s, (100, 200, 255), (20, glitch_y, 80, 3))
        # 数据流粒子
        for data_i in range(20):
            data_angle = (data_i * 18 + t * 30) * 0.01745
            data_r = 40
            data_x = 60 + math.cos(data_angle) * data_r
            data_y = 60 + math.sin(data_angle) * data_r
            pygame.draw.rect(s, (80, 180, 240), (int(data_x), int(data_y), 3, 3))
        return s

    elif model_style == "mirage_phantom_opera":
        # 魅影歌剧·面具之下 - 歌剧魅影风格
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 半脸面具
        # 白色半边
        pygame.draw.circle(s, (255, 255, 255), (60, 50), 25)
        pygame.draw.rect(s, (0, 0, 0, 0), (60, 25, 30, 50))  # 遮住右半
        # 黑暗半边
        pygame.draw.circle(s, (30, 30, 30), (60, 50), 25)
        pygame.draw.rect(s, (0, 0, 0, 0), (30, 25, 30, 50))  # 遮住左半
        # 眼睛
        pygame.draw.circle(s, (200, 200, 200), (50, 48), 5)
        pygame.draw.circle(s, (50, 50, 50), (70, 48), 5)
        # 16片玫瑰花瓣
        for rose_i in range(16):
            rose_angle = (rose_i * 22.5 + t * 8) * 0.01745
            rose_r = 35 + int(5 * math.sin(t * 2 + rose_i))
            rose_x = 60 + math.cos(rose_angle) * rose_r
            rose_y = 60 + math.sin(rose_angle) * rose_r
            pygame.draw.circle(s, (200, 50, 80), (int(rose_x), int(rose_y)), 4)
        # 烛光效果
        candle_flicker = abs(math.sin(t * 8))
        pygame.draw.circle(s, (255, 200, 100, int(150 * candle_flicker)), (60, 90), 8)
        pygame.draw.circle(s, (255, 255, 200), (60, 90), 4)
        return s

    elif model_style == "mirage_ouroboros":
        # 衔尾之蛇·镜像轮回 - 衔尾蛇无限循环
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 24节蛇身
        for seg_i in range(24):
            seg_progress = seg_i / 24
            seg_angle = (seg_progress * 360 + t * 20) * 0.01745
            seg_r = 35
            seg_x = 60 + math.cos(seg_angle) * seg_r
            seg_y = 60 + math.sin(seg_angle) * seg_r
            # 蛇身颜色渐变（金色到绿色）
            seg_color = (200 - seg_i * 3, 180 - seg_i * 2, 100 + seg_i * 2)
            seg_size = 6 if seg_i < 12 else 5  # 头部较大
            pygame.draw.circle(s, seg_color, (int(seg_x), int(seg_y)), seg_size)
            # 鳞片纹理
            if seg_i % 3 == 0:
                pygame.draw.circle(s, (220, 200, 120), (int(seg_x), int(seg_y)), seg_size - 2, 1)
        # 蛇头（咬住尾巴）
        head_angle = t * 20 * 0.01745
        head_x = 60 + math.cos(head_angle) * 35
        head_y = 60 + math.sin(head_angle) * 35
        pygame.draw.circle(s, (200, 180, 100), (int(head_x), int(head_y)), 8)
        # 眼睛
        eye_x = head_x + math.cos(head_angle) * 4
        eye_y = head_y + math.sin(head_angle) * 4
        pygame.draw.circle(s, (255, 50, 50), (int(eye_x), int(eye_y)), 2)
        # 中心无限符号
        pygame.draw.circle(s, (200, 180, 100), (50, 60), 10, 2)
        pygame.draw.circle(s, (200, 180, 100), (70, 60), 10, 2)
        return s
    
    # mirage_fractal 和 mirage_butterfly 需要从其他位置找
    elif model_style == "mirage_fractal":
        # 分形镜界·无尽递归
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 递归三角形图案
        for level in range(4):
            size = 40 - level * 8
            for tri in range(3 ** level):
                angle_offset = (tri * 360 / (3 ** level) + t * 10) * 0.01745
                tri_x = 60 + math.cos(angle_offset) * (level * 10)
                tri_y = 60 + math.sin(angle_offset) * (level * 10)
                pts = []
                for v in range(3):
                    v_angle = (v * 120 + t * 15) * 0.01745
                    vx = tri_x + math.cos(v_angle) * size
                    vy = tri_y + math.sin(v_angle) * size
                    pts.append((int(vx), int(vy)))
                if len(pts) == 3:
                    color_intensity = 255 - level * 40
                    pygame.draw.polygon(s, (color_intensity, 150, 255 - level * 30), pts, 2)
        pygame.draw.circle(s, (200, 150, 255), (60, 60), 8)
        return s
    
    elif model_style == "mirage_butterfly":
        # 蝴蝶效应·混沌之翼
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        wing_flap = math.sin(t * 5) * 0.3
        # 左翅膀
        left_pts = [(60, 60)]
        for i in range(8):
            angle = (120 + i * 10 + wing_flap * 20) * 0.01745
            r = 25 + i * 3
            left_pts.append((60 + math.cos(angle) * r, 60 + math.sin(angle) * r))
        pygame.draw.polygon(s, (255, 180, 220), left_pts)
        pygame.draw.polygon(s, (255, 100, 150), left_pts, 2)
        # 右翅膀
        right_pts = [(60, 60)]
        for i in range(8):
            angle = (60 - i * 10 - wing_flap * 20) * 0.01745
            r = 25 + i * 3
            right_pts.append((60 + math.cos(angle) * r, 60 + math.sin(angle) * r))
        pygame.draw.polygon(s, (255, 180, 220), right_pts)
        pygame.draw.polygon(s, (255, 100, 150), right_pts, 2)
        # 翅膀斑点
        for spot in range(6):
            spot_angle = (130 + spot * 8) * 0.01745
            spot_r = 20 + spot * 4
            sx = 60 + math.cos(spot_angle) * spot_r
            sy = 60 + math.sin(spot_angle) * spot_r
            pygame.draw.circle(s, (255, 220, 240), (int(sx), int(sy)), 3)
            # 镜像
            sx2 = 60 + math.cos(-spot_angle + 3.14) * spot_r
            pygame.draw.circle(s, (255, 220, 240), (int(sx2), int(sy)), 3)
        # 身体
        pygame.draw.ellipse(s, (230, 150, 200), (57, 45, 6, 30))
        pygame.draw.circle(s, (255, 200, 240), (60, 42), 4)
        return s
    
    return None
