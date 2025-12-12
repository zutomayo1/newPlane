"""
苍穹轨断·诺娃 - 外形定义
电磁轨道炮的星际猎手 - 12种完全不同形态的涂装
"""
import pygame
import math
import random

NOVA_STYLES = [
    "nova_default", "nova_electromagnetic", "nova_quantum", "nova_railgun_mk2",
    "nova_stealth_ops", "nova_hyperion", "nova_void_hunter", "nova_thunder_god",
    "nova_ion_storm", "nova_mecha_prime", "nova_orbital_station", "nova_magnetic_north"
]

def is_nova_style(model_style):
    return model_style in NOVA_STYLES

def render_nova_skin(surface, c, model_style, t, pid, static):
    if model_style not in NOVA_STYLES:
        return None
    skin_id = model_style.replace("nova_", "")
    frame = 0 if static else int(t * 60) % 360
    draw_nova(surface, c, 60, 60, scale=1.8, skin_id=skin_id, frame=frame)
    return surface

def draw_nova(surface, color, x, y, scale=1.0, skin_id="default", frame=0):
    """绘制诺娃 - 12种独特形态"""
    cx, cy = x, y
    s = scale
    pulse = math.sin(frame * 0.1) * 3
    
    # 根据皮肤选择完全不同的绘制方式
    if skin_id == "default":
        _draw_default(surface, cx, cy, s, frame, pulse)
    elif skin_id == "electromagnetic":
        _draw_electromagnetic(surface, cx, cy, s, frame, pulse)
    elif skin_id == "quantum":
        _draw_quantum(surface, cx, cy, s, frame, pulse)
    elif skin_id == "railgun_mk2":
        _draw_railgun_mk2(surface, cx, cy, s, frame, pulse)
    elif skin_id == "stealth_ops":
        _draw_stealth_ops(surface, cx, cy, s, frame, pulse)
    elif skin_id == "hyperion":
        _draw_hyperion(surface, cx, cy, s, frame, pulse)
    elif skin_id == "void_hunter":
        _draw_void_hunter(surface, cx, cy, s, frame, pulse)
    elif skin_id == "thunder_god":
        _draw_thunder_god(surface, cx, cy, s, frame, pulse)
    elif skin_id == "ion_storm":
        _draw_ion_storm(surface, cx, cy, s, frame, pulse)
    elif skin_id == "mecha_prime":
        _draw_mecha_prime(surface, cx, cy, s, frame, pulse)
    elif skin_id == "orbital_station":
        _draw_orbital_station(surface, cx, cy, s, frame, pulse)
    elif skin_id == "magnetic_north":
        _draw_magnetic_north(surface, cx, cy, s, frame, pulse)
    else:
        _draw_default(surface, cx, cy, s, frame, pulse)

def _draw_default(surface, cx, cy, s, frame, pulse):
    """默认 - 标准轨道炮战机"""
    # 能量光环
    for i in range(3):
        r = int(30*s + i*8 + pulse)
        surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (100, 180, 255, 40-i*12), (r, r), r)
        surface.blit(surf, (cx-r, cy-r))
    
    # 机翼 - 标准三角翼
    pygame.draw.polygon(surface, (60, 100, 160), [
        (cx-35*s, cy+5*s), (cx-10*s, cy-10*s), (cx-8*s, cy+15*s)])
    pygame.draw.polygon(surface, (60, 100, 160), [
        (cx+35*s, cy+5*s), (cx+10*s, cy-10*s), (cx+8*s, cy+15*s)])
    
    # 主体 - 流线型
    pygame.draw.polygon(surface, (80, 130, 200), [
        (cx, cy-30*s), (cx-12*s, cy), (cx-8*s, cy+20*s),
        (cx+8*s, cy+20*s), (cx+12*s, cy)])
    
    # 轨道炮管
    pygame.draw.rect(surface, (120, 150, 180), (cx-3*s, cy-35*s, 6*s, 20*s))
    pygame.draw.circle(surface, (150, 200, 255), (int(cx), int(cy-35*s)), int(4*s))
    
    # 能量核心
    pygame.draw.circle(surface, (100, 180, 255), (int(cx), int(cy)), int(8*s+pulse/2))
    pygame.draw.circle(surface, (200, 230, 255), (int(cx), int(cy)), int(4*s))

def _draw_electromagnetic(surface, cx, cy, s, frame, pulse):
    """电磁脉冲 - 环形电磁场结构"""
    # 多层电磁环
    for i in range(5):
        angle = frame * 3 + i * 72
        r = 25*s + i*5
        ring_surf = pygame.Surface((int(r*2+20), int(r*2+20)), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (100, 200, 255, 60), (int(r+10), int(r+10)), int(r), 2)
        rotated = pygame.transform.rotate(ring_surf, angle)
        surface.blit(rotated, (cx - rotated.get_width()//2, cy - rotated.get_height()//2))
    
    # 闪电效果
    for i in range(6):
        angle = frame * 2 + i * 60
        x1 = cx + math.cos(math.radians(angle)) * 15*s
        y1 = cy + math.sin(math.radians(angle)) * 15*s
        x2 = cx + math.cos(math.radians(angle)) * 35*s
        y2 = cy + math.sin(math.radians(angle)) * 35*s
        # 锯齿闪电
        points = [(x1, y1)]
        for j in range(3):
            mx = x1 + (x2-x1)*(j+1)/4 + random.randint(-5, 5)*s
            my = y1 + (y2-y1)*(j+1)/4 + random.randint(-5, 5)*s
            points.append((mx, my))
        points.append((x2, y2))
        pygame.draw.lines(surface, (180, 230, 255), False, points, 2)
    
    # 圆形主体
    pygame.draw.circle(surface, (40, 80, 180), (int(cx), int(cy)), int(18*s))
    pygame.draw.circle(surface, (100, 200, 255), (int(cx), int(cy)), int(12*s))
    pygame.draw.circle(surface, (220, 240, 255), (int(cx), int(cy)), int(6*s))

def _draw_quantum(surface, cx, cy, s, frame, pulse):
    """量子态 - 不确定性形态，边缘模糊"""
    # 量子云
    random.seed(int(frame/10))
    for i in range(20):
        qx = cx + random.gauss(0, 20*s)
        qy = cy + random.gauss(0, 15*s)
        qr = random.randint(3, 8)*s
        alpha = random.randint(30, 100)
        color = (
            int(80 + 100*math.sin(frame*0.1 + i)),
            int(60 + 80*math.sin(frame*0.1 + i + 1)),
            int(160 + 80*math.sin(frame*0.1 + i + 2))
        )
        surf = pygame.Surface((int(qr*2), int(qr*2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, alpha), (int(qr), int(qr)), int(qr))
        surface.blit(surf, (qx-qr, qy-qr))
    
    # 概率波纹
    for i in range(3):
        wave_r = (frame*2 + i*40) % 60 * s
        alpha = max(0, 100 - int(wave_r))
        if alpha > 0:
            surf = pygame.Surface((int(wave_r*2+10), int(wave_r*2+10)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (180, 150, 255, alpha), (int(wave_r+5), int(wave_r+5)), int(wave_r), 2)
            surface.blit(surf, (cx-wave_r-5, cy-wave_r-5))
    
    # 测不准核心 - 位置抖动
    core_x = cx + math.sin(frame*0.5)*5*s
    core_y = cy + math.cos(frame*0.7)*5*s
    pygame.draw.circle(surface, (180, 150, 255), (int(core_x), int(core_y)), int(10*s))
    pygame.draw.circle(surface, (255, 255, 255), (int(core_x), int(core_y)), int(5*s))

def _draw_railgun_mk2(surface, cx, cy, s, frame, pulse):
    """轨道炮II型 - 重装军用形态"""
    # 厚重装甲
    armor_color = (80, 85, 90)
    warning_color = (255, 150, 50)
    
    # 巨大肩甲
    pygame.draw.polygon(surface, armor_color, [
        (cx-40*s, cy-5*s), (cx-25*s, cy-20*s), (cx-15*s, cy-10*s), (cx-20*s, cy+10*s)])
    pygame.draw.polygon(surface, armor_color, [
        (cx+40*s, cy-5*s), (cx+25*s, cy-20*s), (cx+15*s, cy-10*s), (cx+20*s, cy+10*s)])
    
    # 警示条纹
    for i in range(3):
        y = cy - 10*s + i*8*s
        pygame.draw.line(surface, warning_color, (cx-35*s, y), (cx-20*s, y), 3)
        pygame.draw.line(surface, warning_color, (cx+20*s, y), (cx+35*s, y), 3)
    
    # 重型主体
    pygame.draw.polygon(surface, (100, 105, 110), [
        (cx, cy-25*s), (cx-18*s, cy-5*s), (cx-15*s, cy+22*s),
        (cx+15*s, cy+22*s), (cx+18*s, cy-5*s)])
    
    # 双轨道炮
    pygame.draw.rect(surface, (60, 65, 70), (cx-8*s, cy-40*s, 5*s, 30*s))
    pygame.draw.rect(surface, (60, 65, 70), (cx+3*s, cy-40*s, 5*s, 30*s))
    pygame.draw.circle(surface, warning_color, (int(cx-5.5*s), int(cy-40*s)), int(3*s))
    pygame.draw.circle(surface, warning_color, (int(cx+5.5*s), int(cy-40*s)), int(3*s))
    
    # 动力指示灯
    blink = (frame // 15) % 2
    pygame.draw.circle(surface, (255, 50, 50) if blink else (100, 30, 30), (int(cx), int(cy+15*s)), int(4*s))

def _draw_stealth_ops(surface, cx, cy, s, frame, pulse):
    """隐形行动 - 棱角分明的隐身形态"""
    stealth_color = (30, 32, 35)
    edge_color = (50, 55, 60)
    
    # 极简棱角外形 - F-117风格
    body = [
        (cx, cy-28*s), (cx-20*s, cy-5*s), (cx-25*s, cy+5*s),
        (cx-15*s, cy+20*s), (cx+15*s, cy+20*s), (cx+25*s, cy+5*s), (cx+20*s, cy-5*s)]
    pygame.draw.polygon(surface, stealth_color, body)
    pygame.draw.polygon(surface, edge_color, body, 1)
    
    # 锐角翼
    pygame.draw.polygon(surface, stealth_color, [
        (cx-25*s, cy+5*s), (cx-45*s, cy+15*s), (cx-15*s, cy+20*s)])
    pygame.draw.polygon(surface, stealth_color, [
        (cx+25*s, cy+5*s), (cx+45*s, cy+15*s), (cx+15*s, cy+20*s)])
    
    # 微弱的指示光 - 只在特定帧闪烁
    if frame % 60 < 5:
        pygame.draw.circle(surface, (20, 80, 20), (int(cx), int(cy)), int(3*s))
    
    # 隐身波纹效果
    if frame % 30 < 15:
        alpha = 30 - (frame % 30) * 2
        r = 30*s + (frame % 30)*s
        surf = pygame.Surface((int(r*2), int(r*2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (60, 65, 70, alpha), (int(r), int(r)), int(r), 1)
        surface.blit(surf, (cx-r, cy-r))

def _draw_hyperion(surface, cx, cy, s, frame, pulse):
    """海伯利安 - 希腊神话风格"""
    gold = (255, 200, 100)
    bronze = (180, 130, 80)
    
    # 光芒背景
    for i in range(12):
        angle = i * 30 + frame
        x1 = cx + math.cos(math.radians(angle)) * 20*s
        y1 = cy + math.sin(math.radians(angle)) * 20*s
        x2 = cx + math.cos(math.radians(angle)) * 40*s
        y2 = cy + math.sin(math.radians(angle)) * 40*s
        pygame.draw.line(surface, (255, 220, 150), (x1, y1), (x2, y2), 2)
    
    # 圆盾形主体
    pygame.draw.circle(surface, bronze, (int(cx), int(cy)), int(22*s))
    pygame.draw.circle(surface, gold, (int(cx), int(cy)), int(18*s))
    
    # 希腊回纹
    for i in range(4):
        r = 15*s - i*3*s
        rect = (cx-r, cy-r, r*2, r*2)
        pygame.draw.arc(surface, bronze, rect, i*math.pi/2, (i+1)*math.pi/2, 2)
    
    # 侧翼 - 羽翼造型
    for side in [-1, 1]:
        for i in range(5):
            feather_x = cx + side * (20 + i*6)*s
            feather_y = cy + (i-2)*5*s
            pygame.draw.ellipse(surface, gold, (feather_x-8*s, feather_y-3*s, 16*s, 6*s))
    
    # 中央宝石
    pygame.draw.circle(surface, (255, 100, 100), (int(cx), int(cy)), int(6*s))
    pygame.draw.circle(surface, (255, 200, 200), (int(cx-2*s), int(cy-2*s)), int(2*s))

def _draw_void_hunter(surface, cx, cy, s, frame, pulse):
    """虚空猎手 - 暗物质形态"""
    void_color = (20, 10, 40)
    dark_matter = (80, 50, 120)
    
    # 引力透镜扭曲效果
    for i in range(8):
        angle = frame * 0.5 + i * 45
        dist = 30*s + math.sin(frame*0.1 + i)*5*s
        px = cx + math.cos(math.radians(angle)) * dist
        py = cy + math.sin(math.radians(angle)) * dist
        # 扭曲的光点
        pygame.draw.circle(surface, (150, 100, 200), (int(px), int(py)), int(3*s))
    
    # 黑洞核心
    for i in range(5):
        r = 20*s - i*4*s
        alpha = 50 + i*30
        surf = pygame.Surface((int(r*2+4), int(r*2+4)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*dark_matter, alpha), (int(r+2), int(r+2)), int(r))
        surface.blit(surf, (cx-r-2, cy-r-2))
    pygame.draw.circle(surface, void_color, (int(cx), int(cy)), int(8*s))
    
    # 锐利三角翼
    pygame.draw.polygon(surface, dark_matter, [
        (cx-10*s, cy), (cx-40*s, cy+10*s), (cx-15*s, cy+15*s)])
    pygame.draw.polygon(surface, dark_matter, [
        (cx+10*s, cy), (cx+40*s, cy+10*s), (cx+15*s, cy+15*s)])
    
    # 吸收粒子
    random.seed(frame//5)
    for i in range(10):
        dist = 50*s - (frame % 30)*s
        angle = random.randint(0, 360)
        px = cx + math.cos(math.radians(angle)) * dist
        py = cy + math.sin(math.radians(angle)) * dist
        pygame.draw.circle(surface, (120, 80, 180), (int(px), int(py)), 2)

def _draw_thunder_god(surface, cx, cy, s, frame, pulse):
    """雷神之锤 - 北欧神话风格"""
    gold = (255, 215, 0)
    blue = (50, 100, 200)
    
    # 雷电背景
    if frame % 20 < 3:
        for i in range(4):
            angle = random.randint(0, 360)
            length = random.randint(30, 50)*s
            x2 = cx + math.cos(math.radians(angle)) * length
            y2 = cy + math.sin(math.radians(angle)) * length
            pygame.draw.line(surface, (255, 255, 200), (cx, cy), (x2, y2), 3)
    
    # 锤形主体
    pygame.draw.rect(surface, (100, 100, 120), (cx-15*s, cy-10*s, 30*s, 25*s))  # 锤头
    pygame.draw.rect(surface, (80, 60, 40), (cx-4*s, cy+15*s, 8*s, 15*s))  # 锤柄
    
    # 北欧符文
    pygame.draw.line(surface, gold, (cx-8*s, cy-5*s), (cx-8*s, cy+10*s), 2)
    pygame.draw.line(surface, gold, (cx-8*s, cy), (cx-3*s, cy-5*s), 2)
    pygame.draw.line(surface, gold, (cx+8*s, cy-5*s), (cx+8*s, cy+10*s), 2)
    pygame.draw.line(surface, gold, (cx+8*s, cy), (cx+3*s, cy+5*s), 2)
    
    # 电弧翼
    for side in [-1, 1]:
        wing_x = cx + side * 25*s
        points = [(cx + side*15*s, cy)]
        for i in range(5):
            px = cx + side*(15 + i*8)*s
            py = cy + math.sin(frame*0.3 + i)*8*s
            points.append((px, py))
        pygame.draw.lines(surface, (150, 200, 255), False, points, 3)
    
    # 雷电核心
    pygame.draw.circle(surface, blue, (int(cx), int(cy)), int(10*s))
    pygame.draw.circle(surface, (200, 220, 255), (int(cx), int(cy)), int(5*s))

def _draw_ion_storm(surface, cx, cy, s, frame, pulse):
    """离子风暴 - 旋转风暴形态"""
    storm_color = (100, 220, 180)
    
    # 旋转风暴粒子
    for i in range(30):
        angle = frame * 3 + i * 12
        dist = 10*s + i*s
        px = cx + math.cos(math.radians(angle)) * dist
        py = cy + math.sin(math.radians(angle)) * dist
        size = 2 + (30-i)/10
        alpha = 200 - i*5
        surf = pygame.Surface((int(size*2+2), int(size*2+2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*storm_color, alpha), (int(size+1), int(size+1)), int(size))
        surface.blit(surf, (px-size-1, py-size-1))
    
    # 风暴眼 - 平静核心
    pygame.draw.circle(surface, (30, 60, 50), (int(cx), int(cy)), int(15*s))
    pygame.draw.circle(surface, (50, 100, 80), (int(cx), int(cy)), int(10*s))
    pygame.draw.circle(surface, storm_color, (int(cx), int(cy)), int(5*s))
    
    # 弧形翼 - 风暴臂
    for side in [-1, 1]:
        arc_rect = (cx + side*5*s - 30*s, cy - 30*s, 60*s, 60*s)
        pygame.draw.arc(surface, storm_color, arc_rect, 
                       math.pi/2 if side > 0 else -math.pi/2,
                       math.pi if side > 0 else 0, 4)

def _draw_mecha_prime(surface, cx, cy, s, frame, pulse):
    """机甲领袖 - 变形金刚风格"""
    red = (200, 50, 50)
    blue = (50, 80, 180)
    silver = (180, 185, 190)
    
    # 胸甲
    pygame.draw.polygon(surface, blue, [
        (cx, cy-20*s), (cx-18*s, cy), (cx-15*s, cy+15*s),
        (cx+15*s, cy+15*s), (cx+18*s, cy)])
    
    # 肩甲 - 大型方块
    pygame.draw.rect(surface, red, (cx-35*s, cy-15*s, 18*s, 20*s))
    pygame.draw.rect(surface, red, (cx+17*s, cy-15*s, 18*s, 20*s))
    
    # 头部
    pygame.draw.polygon(surface, silver, [
        (cx, cy-30*s), (cx-8*s, cy-20*s), (cx+8*s, cy-20*s)])
    pygame.draw.rect(surface, blue, (cx-5*s, cy-28*s, 10*s, 6*s))  # 头盔
    
    # 领导者徽章 - 汽车人标志简化
    pygame.draw.polygon(surface, red, [
        (cx, cy-5*s), (cx-6*s, cy+5*s), (cx, cy+2*s), (cx+6*s, cy+5*s)])
    
    # 手臂轮廓
    pygame.draw.rect(surface, silver, (cx-38*s, cy+5*s, 8*s, 18*s))
    pygame.draw.rect(surface, silver, (cx+30*s, cy+5*s, 8*s, 18*s))
    
    # 眼睛发光
    pygame.draw.circle(surface, (100, 200, 255), (int(cx-3*s), int(cy-25*s)), int(2*s))
    pygame.draw.circle(surface, (100, 200, 255), (int(cx+3*s), int(cy-25*s)), int(2*s))

def _draw_orbital_station(surface, cx, cy, s, frame, pulse):
    """轨道站 - 空间站模块化形态"""
    white = (230, 235, 240)
    silver = (180, 185, 195)
    
    # 太阳能板
    for side in [-1, 1]:
        panel_x = cx + side * 30*s
        pygame.draw.rect(surface, (50, 80, 150), (panel_x-12*s, cy-20*s, 24*s, 40*s))
        # 电池格
        for i in range(4):
            for j in range(8):
                pygame.draw.rect(surface, (70, 100, 170), 
                               (panel_x-10*s + j*3*s, cy-18*s + i*10*s, 2.5*s, 9*s), 1)
        # 连接臂
        pygame.draw.rect(surface, silver, (cx + side*15*s, cy-3*s, 15*s * abs(side), 6*s))
    
    # 主模块 - 圆柱体
    pygame.draw.ellipse(surface, white, (cx-15*s, cy-25*s, 30*s, 50*s))
    pygame.draw.ellipse(surface, silver, (cx-15*s, cy-25*s, 30*s, 50*s), 2)
    
    # 对接口
    pygame.draw.circle(surface, silver, (int(cx), int(cy-25*s)), int(8*s))
    pygame.draw.circle(surface, (50, 50, 60), (int(cx), int(cy-25*s)), int(5*s))
    
    # 观察窗
    for i in range(3):
        wy = cy - 10*s + i * 12*s
        pygame.draw.ellipse(surface, (100, 150, 200), (cx-4*s, wy-3*s, 8*s, 6*s))
    
    # 旋转环
    ring_angle = frame * 2
    for i in range(8):
        a = ring_angle + i * 45
        rx = cx + math.cos(math.radians(a)) * 18*s
        ry = cy + math.sin(math.radians(a)) * 5*s  # 椭圆轨道
        pygame.draw.circle(surface, (255, 200, 100), (int(rx), int(ry)), int(2*s))

def _draw_magnetic_north(surface, cx, cy, s, frame, pulse):
    """磁极之北 - 指南针形态"""
    north_color = (100, 150, 220)
    south_color = (220, 100, 100)
    
    # 磁力线
    for i in range(8):
        angle_offset = i * 45
        for j in range(10):
            t = j / 10
            # 磁力线弧度
            angle = math.radians(angle_offset + frame)
            dist = 15*s + j*3*s
            curve = math.sin(t * math.pi) * 20*s
            px = cx + math.cos(angle) * dist
            py = cy + math.sin(angle) * dist - curve
            color = north_color if py < cy else south_color
            pygame.draw.circle(surface, color, (int(px), int(py)), 2)
    
    # 指南针主体
    pygame.draw.circle(surface, (200, 190, 170), (int(cx), int(cy)), int(20*s))
    pygame.draw.circle(surface, (230, 225, 210), (int(cx), int(cy)), int(16*s))
    
    # 指针 - 旋转
    needle_angle = math.radians(frame * 0.5)
    n_len = 15*s
    # 北针（蓝）
    nx = cx + math.sin(needle_angle) * n_len
    ny = cy - math.cos(needle_angle) * n_len
    pygame.draw.polygon(surface, north_color, [
        (cx, cy), (nx, ny), 
        (cx + math.cos(needle_angle)*3*s, cy + math.sin(needle_angle)*3*s)])
    # 南针（红）
    sx = cx - math.sin(needle_angle) * n_len
    sy = cy + math.cos(needle_angle) * n_len
    pygame.draw.polygon(surface, south_color, [
        (cx, cy), (sx, sy),
        (cx - math.cos(needle_angle)*3*s, cy - math.sin(needle_angle)*3*s)])
    
    # 中心轴
    pygame.draw.circle(surface, (80, 70, 60), (int(cx), int(cy)), int(4*s))
    
    # N/S标记
    pygame.draw.circle(surface, north_color, (int(cx), int(cy-28*s)), int(5*s))
    pygame.draw.circle(surface, south_color, (int(cx), int(cy+28*s)), int(5*s))

def _render_nova_base(surface, t, pulse):
    frame = int(t * 60) % 360
    draw_nova(surface, (100, 150, 220), 60, 60, scale=1.8, skin_id="default", frame=frame)
