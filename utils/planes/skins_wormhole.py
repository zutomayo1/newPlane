# Wormhole 专属涂装渲染模块
# 包含: wormhole_monsoon, wormhole_mirage, wormhole_bonsai, wormhole_lantern, 
#       wormhole_geode, wormhole_totem, wormhole_ruins, wormhole_teaceremony,
#       wormhole_windchime, wormhole_silk_road, wormhole_supercell, wormhole_paperlamp

import pygame
import math
import random

# Wormhole涂装列表
WORMHOLE_STYLES = [
    "wormhole_monsoon", "wormhole_mirage", "wormhole_bonsai", "wormhole_lantern",
    "wormhole_geode", "wormhole_totem", "wormhole_ruins", "wormhole_teaceremony",
    "wormhole_windchime", "wormhole_silk_road", "wormhole_supercell", "wormhole_paperlamp"
]

def is_wormhole_style(model_style):
    """检查是否为Wormhole涂装"""
    return model_style in WORMHOLE_STYLES

def render_wormhole_skin(s, c, model_style, t, pid, static=False):
    """渲染Wormhole涂装，返回Surface或None"""
    pulse = math.sin(t * 2) * 0.15 + 1
    
    if model_style == "wormhole_monsoon":
        # 季风洪流·水龙卷暴 - 三重水龙卷螺旋，雷电闪烁
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 三重水龙卷螺旋
        for layer in range(3):
            for i in range(12):
                spiral_angle = (t * 5 + i * 30 + layer * 40) * 0.01745
                spiral_r = 15 + layer * 8 + i * 1.5
                sx = 60 + math.cos(spiral_angle) * spiral_r
                sy = 60 + math.sin(spiral_angle) * spiral_r
                color_intensity = 100 + layer * 40
                pygame.draw.circle(s, (60 + layer * 20, color_intensity, 220), (int(sx), int(sy)), 3 - layer)
        # 雷电闪烁效果
        if int(t * 8) % 4 < 2:
            lightning_points = [(60, 20), (55, 40), (65, 50), (60, 70)]
            pygame.draw.lines(s, (255, 255, 255), False, lightning_points, 4)
            pygame.draw.lines(s, (100, 200, 255), False, lightning_points, 2)
        # 水滴爆炸粒子
        for i in range(20):
            drop_angle = (t * 3 + i * 18) * 0.01745
            drop_r = 25 + math.sin(t * 4 + i) * 8
            dx = 60 + math.cos(drop_angle) * drop_r
            dy = 60 + math.sin(drop_angle) * drop_r
            pygame.draw.circle(s, (100, 200, 255), (int(dx), int(dy)), 2)
        # 蓝色涡旋核心
        pygame.draw.circle(s, (60, 140, 220), (60, 60), 12)
        pygame.draw.circle(s, (100, 200, 255), (60, 60), 8)
        return s
    
    elif model_style == "wormhole_mirage":
        # 蜃景幻界·折光异象 - 热浪波纹扭曲，半透明虚影分身
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 热浪波纹扭曲效果（8层）
        for i in range(8):
            wave_y = 20 + i * 12
            wave_points = []
            for x in range(0, 130, 8):
                distort_y = wave_y + math.sin(x * 0.08 + t * 4 + i * 0.5) * 6
                wave_points.append((x, int(distort_y)))
            if len(wave_points) > 1:
                alpha = 120 - i * 12
                pygame.draw.lines(s, (255, 200, 100, alpha), False, wave_points, 2)
        # 半透明虚影重叠（3个分身）
        for offset in [-10, 0, 10]:
            alpha = 180 if offset == 0 else 100
            phantom_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(phantom_surf, (255, 200, 100, alpha), (60 + offset, 60), 18)
            pygame.draw.circle(phantom_surf, (80, 180, 255, alpha), (60 + offset, 60), 14, 2)
            s.blit(phantom_surf, (0, 0))
        # 七彩折射光束
        for i in range(6):
            ray_angle = (t * 2 + i * 60) * 0.01745
            ray_end_x = 60 + math.cos(ray_angle) * 35
            ray_end_y = 60 + math.sin(ray_angle) * 35
            rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 127, 255), (148, 0, 211)]
            pygame.draw.line(s, rainbow_colors[i % 6], (60, 60), (int(ray_end_x), int(ray_end_y)), 2)
        return s
    
    elif model_style == "wormhole_bonsai":
        # 禅庭之心·生灵盆栽 - 树枝蜿蜒生长，绿叶螺旋环绕
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 盆景底座（更细致）
        pygame.draw.rect(s, (100, 80, 60), (35, 85, 50, 12))
        pygame.draw.rect(s, (140, 120, 100), (35, 85, 50, 12), 2)
        # 蜿蜒树干（分段绘制生长感）
        trunk_points = []
        for i in range(8):
            trunk_x = 60 + math.sin(i * 0.3 + t * 0.5) * 5
            trunk_y = 85 - i * 7
            trunk_points.append((int(trunk_x), int(trunk_y)))
        if len(trunk_points) > 1:
            pygame.draw.lines(s, (80, 60, 40), False, trunk_points, 6)
        # 蜿蜒枝干（4条）
        for branch_i in range(4):
            branch_angle = branch_i * 90 + 45
            branch_points = [(60, 50)]
            for seg in range(4):
                seg_angle = (branch_angle + math.sin(t + seg) * 15) * 0.01745
                seg_r = 8 + seg * 6
                bx = 60 + math.cos(seg_angle) * seg_r
                by = 50 + math.sin(seg_angle) * seg_r
                branch_points.append((int(bx), int(by)))
            if len(branch_points) > 1:
                pygame.draw.lines(s, (100, 80, 60), False, branch_points, 3)
        # 绿叶螺旋环绕（12片）
        for i in range(12):
            leaf_angle = (t * 3 + i * 30) * 0.01745
            leaf_r = 20 + math.sin(t * 2 + i) * 5
            lx = 60 + math.cos(leaf_angle) * leaf_r
            ly = 50 + math.sin(leaf_angle) * leaf_r
            leaf_color = (50 + i * 8, 140, 90)
            pygame.draw.ellipse(s, leaf_color, (int(lx) - 4, int(ly) - 3, 8, 6))
        # 根须发光脉动
        root_glow = int(abs(math.sin(t * 3)) * 50) + 50
        pygame.draw.circle(s, (50, root_glow, 90, 80), (60, 85), 25)
        return s
    
    elif model_style == "wormhole_lantern":
        # 千灯夜宴·炫光祈愿 - 六边形灯笼旋转，烛火摇曳光晕
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 中心主灯笼（六边形）
        hex_points = []
        for i in range(6):
            hex_angle = (i * 60 + t * 20) * 0.01745
            hex_x = 60 + math.cos(hex_angle) * 18
            hex_y = 60 + math.sin(hex_angle) * 18
            hex_points.append((int(hex_x), int(hex_y)))
        pygame.draw.polygon(s, (255, 220, 150, 200), hex_points)
        pygame.draw.polygon(s, (255, 180, 60), hex_points, 3)
        # 连接中心线（纸质纹理）
        for point in hex_points:
            pygame.draw.line(s, (240, 200, 130), (60, 60), point, 1)
        # 烛火核心（摇曳效果）
        flicker = int(abs(math.sin(t * 6)) * 8)
        pygame.draw.ellipse(s, (255, 200, 80), (52, 52 - flicker, 16, 20 + flicker))
        pygame.draw.circle(s, (255, 255, 200), (60, 56 - flicker), 6)
        # 温暖光晕脉冲（3层）
        for ring in range(3):
            glow_r = 25 + ring * 12 + int(pulse * 10)
            glow_alpha = 120 - ring * 35
            glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 220, 100, glow_alpha), (60, 60), glow_r)
            s.blit(glow_surf, (0, 0))
        # 周围小灯笼升空
        for i in range(4):
            small_ly = 100 - int((t * 15 + i * 30) % 120)
            small_lx = 20 + i * 25
            pygame.draw.rect(s, (255, 200, 100), (small_lx, small_ly, 12, 16), 2)
            pygame.draw.circle(s, (255, 220, 120, 150), (small_lx + 6, small_ly + 8), 10)
        return s
    
    elif model_style == "wormhole_geode":
        # 晶洞星爆·紫晶能核 - 多面紫晶旋转，能量脉冲爆发，裂纹闪电
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 多面紫晶外壳（12面体旋转）
        crystal_points = []
        for i in range(12):
            crystal_angle = (i * 30 + t * 40) * 0.01745
            crystal_r = 28 if i % 2 == 0 else 22
            cx = 60 + math.cos(crystal_angle) * crystal_r
            cy = 60 + math.sin(crystal_angle) * crystal_r
            crystal_points.append((int(cx), int(cy)))
        pygame.draw.polygon(s, (180, 100, 240, 200), crystal_points)
        pygame.draw.polygon(s, (140, 60, 240), crystal_points, 3)
        # 内部晶面三角形
        for i in range(0, 12, 2):
            triangle = [(60, 60), crystal_points[i], crystal_points[(i+2) % 12]]
            inner_color = (140 + i * 8, 60 + i * 5, 200 + i * 4)
            pygame.draw.polygon(s, inner_color, triangle)
        # 能量脉冲（3层渐变）
        for ring in range(3):
            pulse_r = 8 + ring * 6 + int(pulse * 8)
            pulse_alpha = 200 - ring * 50
            pygame.draw.circle(s, (180, 100, 240, pulse_alpha), (60, 60), pulse_r)
        # 裂纹闪电四射（8道）
        for i in range(8):
            lightning_angle = (i * 45 + t * 30) * 0.01745
            lightning_segments = []
            for seg in range(4):
                seg_r = 18 + seg * 8
                seg_x = 60 + math.cos(lightning_angle) * seg_r + random.randint(-2, 2)
                seg_y = 60 + math.sin(lightning_angle) * seg_r + random.randint(-2, 2)
                lightning_segments.append((int(seg_x), int(seg_y)))
            if len(lightning_segments) > 1:
                pygame.draw.lines(s, (200, 120, 255), False, lightning_segments, 2)
        # 水晶碎片螺旋
        for i in range(6):
            shard_angle = (t * 6 + i * 60) * 0.01745
            shard_r = 35 + math.sin(t * 3 + i) * 5
            sx = 60 + math.cos(shard_angle) * shard_r
            sy = 60 + math.sin(shard_angle) * shard_r
            pygame.draw.circle(s, (200, 140, 255), (int(sx), int(sy)), 3)
        return s
    
    elif model_style == "wormhole_totem":
        # 祖灵图腾·古神降临 - 三层图腾旋转，符文闪烁，灵魂能量环
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 三层图腾柱（带旋转效果）
        for layer in range(3):
            layer_y = 25 + layer * 25
            layer_rotation = math.sin(t * 2 + layer) * 5
            # 图腾段
            totem_rect = (48 + layer_rotation, layer_y, 24, 22)
            pygame.draw.rect(s, (200 - layer * 20, 100 - layer * 15, 40), totem_rect)
            pygame.draw.rect(s, (220 - layer * 15, 130 - layer * 10, 60), totem_rect, 3)
            # 雕刻纹路
            for line_i in range(3):
                carve_y = layer_y + 4 + line_i * 6
                pygame.draw.line(s, (120, 80, 40), (52, carve_y), (68, carve_y), 2)
            # 图腾面孔眼睛
            eye_y = layer_y + 12
            pygame.draw.circle(s, (255, 220, 150), (55, eye_y), 3)
            pygame.draw.circle(s, (255, 220, 150), (65, eye_y), 3)
            pygame.draw.circle(s, (100, 60, 20), (55, eye_y), 2)
            pygame.draw.circle(s, (100, 60, 20), (65, eye_y), 2)
            # 眼睛发光
            if int(t * 3 + layer) % 2 == 0:
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 220, 100, 150), (55, eye_y), 6)
                pygame.draw.circle(glow_surf, (255, 220, 100, 150), (65, eye_y), 6)
                s.blit(glow_surf, (0, 0))
        # 符文连续闪烁（8个环绕）
        for i in range(8):
            rune_angle = (i * 45 + t * 50) * 0.01745
            rune_r = 35
            rune_x = 60 + math.cos(rune_angle) * rune_r
            rune_y = 60 + math.sin(rune_angle) * rune_r
            rune_brightness = int(abs(math.sin(t * 5 + i)) * 155) + 100
            pygame.draw.circle(s, (255, rune_brightness, 50), (int(rune_x), int(rune_y)), 4)
            pygame.draw.circle(s, (255, 255, 150), (int(rune_x), int(rune_y)), 2)
        # 灵魂能量环螺旋上升（4层）
        for ring_i in range(4):
            ring_y = 90 - ring_i * 15 - int(t * 20) % 60
            ring_r = 20 + ring_i * 5
            ring_alpha = 120 - ring_i * 25
            pygame.draw.circle(s, (200, 150, 100, ring_alpha), (60, ring_y), ring_r, 2)
        return s
    
    elif model_style == "wormhole_ruins":
        # 失落帝国·时光回溯 - 石碑浮现消失，文字点亮，时空波纹
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 石碑浮现消失循环
        tablet_phase = (t * 0.8) % 2.0
        tablet_alpha = int(abs(math.sin(tablet_phase * 1.57)) * 200)
        tablet_points = [
            (40, 30), (80, 32), (85, 60), (78, 88), (42, 86), (35, 58)
        ]
        tablet_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(tablet_surf, (100, 110, 140, tablet_alpha), tablet_points)
        pygame.draw.polygon(tablet_surf, (130, 140, 170, tablet_alpha), tablet_points, 3)
        s.blit(tablet_surf, (0, 0))
        # 古文字符号逐个点亮（8个）
        for i in range(8):
            text_x = 45 + (i % 3) * 12
            text_y = 40 + (i // 3) * 15
            text_phase = (t * 2 + i * 0.3) % 1.0
            if text_phase > 0.2:
                text_brightness = int(min(text_phase * 255, 200))
                # 竖线
                pygame.draw.line(s, (text_brightness, text_brightness - 30, 150), 
                               (text_x, text_y - 4), (text_x, text_y + 4), 2)
                # 横线或点
                if i % 2 == 0:
                    pygame.draw.line(s, (text_brightness, text_brightness - 30, 150),
                                   (text_x - 3, text_y), (text_x + 3, text_y), 2)
                else:
                    pygame.draw.circle(s, (text_brightness, text_brightness - 30, 150), (text_x, text_y), 2)
        # 历史波纹时空扩散
        echo_phase = (t * 1.5) % 1.0
        for echo_i in range(3):
            echo_r = int((20 + echo_i * 15) * (1 + echo_phase * 1.5))
            echo_alpha = int((140 - echo_i * 40) * (1 - echo_phase))
            if echo_alpha > 0:
                pygame.draw.circle(s, (150, 160, 190, echo_alpha), (60, 60), echo_r, 2)
        # 裂痕发光重组（5条）
        for crack_i in range(5):
            crack_angle = crack_i * 72
            crack_progress = (t + crack_i * 0.2) % 1.0
            if crack_progress < 0.7:  # 显示70%时间
                crack_len = int(25 * crack_progress)
                crack_x = 60 + int(math.cos(crack_angle * 0.01745) * crack_len)
                crack_y = 60 + int(math.sin(crack_angle * 0.01745) * crack_len)
                pygame.draw.line(s, (180, 200, 230), (60, 60), (crack_x, crack_y), 2)
                # 裂痕端点发光
                pygame.draw.circle(s, (200, 220, 255), (crack_x, crack_y), 3)
        return s
    
    elif model_style == "wormhole_teaceremony":
        # 茶香灵境·悟道之境 - 茶叶螺旋舞动，蒸汽形成禅意文字
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 茶碗（更精致）
        pygame.draw.ellipse(s, (150, 180, 120), (38, 55, 44, 35))
        pygame.draw.ellipse(s, (180, 210, 150), (38, 55, 44, 35), 2)
        pygame.draw.ellipse(s, (120, 150, 100), (42, 75, 36, 12))
        # 茶叶螺旋漂浮舞动（10片）
        for i in range(10):
            leaf_spiral_angle = (t * 3 + i * 36) * 0.01745
            leaf_r = 15 + math.sin(t * 2 + i) * 8
            leaf_x = 60 + math.cos(leaf_spiral_angle) * leaf_r
            leaf_y = 65 + math.sin(leaf_spiral_angle) * leaf_r * 0.7
            # 茶叶椭圆形
            leaf_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.ellipse(leaf_surf, (80, 140, 80), (int(leaf_x) - 4, int(leaf_y) - 2, 8, 5))
            pygame.draw.ellipse(leaf_surf, (100, 160, 100), (int(leaf_x) - 4, int(leaf_y) - 2, 8, 5), 1)
            s.blit(leaf_surf, (0, 0))
        # 蒸汽形成禅意符号（升腾）
        for i in range(6):
            steam_y = 55 - i * 12 - int(t * 20) % 70
            steam_x = 60 + math.sin(t * 1.5 + i * 0.8) * 8
            steam_alpha = max(0, 180 - i * 25 - int(t * 20) % 70)
            if steam_alpha > 0:
                # 简化为圆形粒子
                steam_size = 4 + i // 2
                pygame.draw.circle(s, (200, 230, 200, steam_alpha), (int(steam_x), int(steam_y)), steam_size)
        # 茶水涟漪波纹扩散
        ripple_phase = (t * 2) % 1.5
        for ripple_i in range(3):
            ripple_r = int((10 + ripple_i * 8) * (1 + ripple_phase))
            ripple_alpha = int((120 - ripple_i * 30) * (1 - ripple_phase / 1.5))
            if ripple_alpha > 0:
                pygame.draw.ellipse(s, (150, 200, 120, ripple_alpha), 
                                  (60 - ripple_r, 65 - ripple_r // 2, ripple_r * 2, ripple_r), 2)
        # 翠绿光晕柔和脉动
        zen_glow = int(abs(math.sin(t * 1.5)) * 40) + 40
        zen_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(zen_surf, (120, 180, 100, zen_glow), (60, 60), 45)
        s.blit(zen_surf, (0, 0))
        return s
    
    elif model_style == "wormhole_windchime":
        # 音波共振·水晶风铃 - 可见音波环，彩虹扩散，曼德拉图案
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 中心吊环
        pygame.draw.circle(s, (200, 220, 255), (60, 25), 10, 3)
        pygame.draw.circle(s, (180, 220, 255), (60, 25), 6)
        # 风铃铃铛旋转（8个）
        for i in range(8):
            chime_angle = (i * 45 + t * 30) * 0.01745
            chime_swing = math.sin(t * 3 + i) * 4
            chime_r = 20 + chime_swing
            chime_x = 60 + math.cos(chime_angle) * chime_r
            chime_y = 35 + math.sin(chime_angle) * chime_r * 0.5
            # 吊线
            pygame.draw.line(s, (180, 200, 240), (60, 25), (int(chime_x), int(chime_y)), 1)
            # 铃铛（水晶质感）
            pygame.draw.circle(s, (150, 180, 220), (int(chime_x), int(chime_y)), 5)
            pygame.draw.circle(s, (200, 230, 255), (int(chime_x), int(chime_y)), 3)
        # 可见音波涟漪（彩虹扩散）
        wave_phase = (t * 2.5) % 1.0
        rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 127, 255), (148, 0, 211)]
        for wave_ring in range(6):
            wave_r = int((15 + wave_ring * 10) * (1 + wave_phase * 2))
            wave_alpha = int((150 - wave_ring * 20) * (1 - wave_phase))
            if wave_alpha > 0:
                wave_color = rainbow_colors[wave_ring % len(rainbow_colors)]
                pygame.draw.circle(s, (*wave_color, wave_alpha), (60, 60), wave_r, 2)
        # 曼德拉共振图案（8角星）
        mandala_points = []
        for star_i in range(8):
            star_angle = (star_i * 45 + t * 20) * 0.01745
            star_r = 28 + math.sin(t * 4 + star_i) * 5
            star_x = 60 + math.cos(star_angle) * star_r
            star_y = 60 + math.sin(star_angle) * star_r
            mandala_points.append((int(star_x), int(star_y)))
        if len(mandala_points) > 1:
            pygame.draw.lines(s, (150, 200, 250), True, mandala_points, 2)
        return s
    
    elif model_style == "wormhole_silk_road":
        # 丝路传说·驼影商道 - 丝绸龙舞，驼队光轨，文化交融
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 丝绸龙舞飘带（3条大型）
        for ribbon_i in range(3):
            ribbon_points = []
            for seg in range(15):
                seg_x = seg * 9
                seg_y = 30 + ribbon_i * 20 + math.sin(t * 2 + seg * 0.4 + ribbon_i) * 12
                ribbon_points.append((seg_x, int(seg_y)))
            if len(ribbon_points) > 1:
                # 丝绸渐变色
                ribbon_colors = [(255, 190, 130), (240, 180, 120), (220, 160, 100)]
                pygame.draw.lines(s, ribbon_colors[ribbon_i], False, ribbon_points, 4)
                pygame.draw.lines(s, (255, 220, 160), False, ribbon_points, 2)
        # 驼队剪影留光轨
        for camel_i in range(4):
            camel_x = 15 + int((t * 25 + camel_i * 30) % 120)
            camel_y = 75
            # 驼峰
            pygame.draw.circle(s, (200, 150, 100), (camel_x, camel_y - 8), 10)
            # 驼身
            pygame.draw.ellipse(s, (200, 150, 100), (camel_x - 8, camel_y, 16, 12))
            # 光轨尾迹
            trail_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            for trail_seg in range(5):
                trail_x = camel_x - trail_seg * 8
                if 0 <= trail_x <= 120:
                    trail_alpha = 100 - trail_seg * 18
                    pygame.draw.circle(trail_surf, (255, 200, 130, trail_alpha), (trail_x, camel_y + 6), 6 - trail_seg)
            s.blit(trail_surf, (0, 0))
        # 东西文化符号交织（6种）
        for sym_i in range(6):
            sym_angle = (sym_i * 60 + t * 40) * 0.01745
            sym_r = 35
            sym_x = 60 + math.cos(sym_angle) * sym_r
            sym_y = 60 + math.sin(sym_angle) * sym_r
            # 用圆形代表符号
            sym_size = 4 + int(abs(math.sin(t * 3 + sym_i)) * 3)
            pygame.draw.circle(s, (255, 200, 150), (int(sym_x), int(sym_y)), sym_size)
            pygame.draw.circle(s, (220, 160, 100), (int(sym_x), int(sym_y)), sym_size, 1)
        # 金币粒子飞散
        for coin_i in range(10):
            coin_angle = (t * 5 + coin_i * 36) * 0.01745
            coin_r = 25 + math.sin(t * 3 + coin_i) * 8
            coin_x = 60 + math.cos(coin_angle) * coin_r
            coin_y = 60 + math.sin(coin_angle) * coin_r
            pygame.draw.circle(s, (255, 215, 0), (int(coin_x), int(coin_y)), 3)
            pygame.draw.circle(s, (255, 255, 100), (int(coin_x), int(coin_y)), 2)
        return s
    
    elif model_style == "wormhole_supercell":
        # 龙卷母胎·风暴之眼 - 三层嵌套涡旋，墙云下降，雷暴电弧
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 超级雷暴云团（上层）
        for cloud_i in range(12):
            cloud_x = 20 + cloud_i * 9 + math.sin(t * 1.5 + cloud_i) * 6
            cloud_y = 15 + math.cos(t * 2 + cloud_i) * 4
            cloud_size = 6 + int(abs(math.sin(t + cloud_i)) * 3)
            pygame.draw.circle(s, (60, 90, 130), (int(cloud_x), int(cloud_y)), cloud_size)
        # 三层嵌套涡旋（疯狂旋转）
        for vortex_layer in range(3):
            vortex_speed = 5 - vortex_layer * 1.5
            for ring in range(8):
                ring_angle = (t * vortex_speed - ring * 0.4 - vortex_layer * 0.8) % 6.28
                ring_radius = 12 + ring * 4 + vortex_layer * 8
                # 涡旋粒子位置
                for seg in range(12):
                    seg_angle = ring_angle + seg * 0.524
                    vortex_x = 60 + math.cos(seg_angle) * ring_radius
                    vortex_y = 70 + math.sin(seg_angle) * ring_radius * 0.7
                    particle_size = 3 - vortex_layer
                    vortex_color = (80 + vortex_layer * 20, 110 + vortex_layer * 20, 150 + vortex_layer * 20)
                    pygame.draw.circle(s, vortex_color, (int(vortex_x), int(vortex_y)), particle_size)
        # 墙云漏斗下降
        funnel_points = []
        for funnel_seg in range(10):
            funnel_y = 40 + funnel_seg * 5
            funnel_width = 8 + funnel_seg * 2
            funnel_x_offset = math.sin(t * 2 + funnel_seg * 0.5) * 3
            funnel_points.append((60 - funnel_width + funnel_x_offset, funnel_y))
        funnel_points_right = [(60 + (60 - x), y) for x, y in funnel_points]
        all_funnel = funnel_points + funnel_points_right[::-1]
        if len(all_funnel) > 2:
            pygame.draw.polygon(s, (70, 100, 140, 150), all_funnel)
        # 雷暴电弧连锁
        if int(t * 5) % 3 < 2:
            for lightning_i in range(4):
                lightning_start_angle = lightning_i * 90
                lightning_points = [(60, 30)]
                for seg in range(5):
                    seg_angle = (lightning_start_angle + random.randint(-20, 20)) * 0.01745
                    seg_r = 15 + seg * 10
                    lx = 60 + math.cos(seg_angle) * seg_r + random.randint(-4, 4)
                    ly = 30 + seg * 8 + random.randint(-3, 3)
                    lightning_points.append((int(lx), int(ly)))
                if len(lightning_points) > 1:
                    pygame.draw.lines(s, (255, 255, 255), False, lightning_points, 3)
                    pygame.draw.lines(s, (100, 200, 255), False, lightning_points, 1)
        # 风柱中心涡旋眼
        pygame.draw.circle(s, (40, 70, 110), (60, 70), 10)
        pygame.draw.circle(s, (80, 120, 160), (60, 70), 6)
        return s
    
    elif model_style == "wormhole_paperlamp":
        # 和风灯影·纸艺祭典 - 纸灯阵列，樱花飘落，柔光灯海
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 纸灯笼阵列（3x3网格）
        for row in range(3):
            for col in range(3):
                lamp_x = 20 + col * 30
                lamp_y = 20 + row * 30
                # 灯笼框架（细致线条）
                lamp_rect = (lamp_x, lamp_y, 24, 28)
                pygame.draw.rect(s, (255, 230, 190), lamp_rect, 2)
                # 竖向分割线
                pygame.draw.line(s, (240, 220, 180), (lamp_x + 12, lamp_y), (lamp_x + 12, lamp_y + 28), 1)
                # 横向纸质纹理
                for texture_i in range(4):
                    tex_y = lamp_y + 4 + texture_i * 7
                    pygame.draw.line(s, (245, 225, 185), (lamp_x + 2, tex_y), (lamp_x + 22, tex_y), 1)
                # 柔和光晕（脉动效果）
                glow_intensity = int(abs(math.sin(t * 1.5 + row + col)) * 50) + 60
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 200, 150, glow_intensity), 
                                 (lamp_x + 12, lamp_y + 14), 16)
                s.blit(glow_surf, (0, 0))
        # 樱花花瓣飘落
        for petal_i in range(15):
            petal_x = 20 + (petal_i * 37 + int(t * 10)) % 100
            petal_y = int((t * 30 + petal_i * 20) % 120)
            # 简化樱花（椭圆）
            petal_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.ellipse(petal_surf, (255, 200, 220), (petal_x - 3, petal_y - 2, 6, 4))
            pygame.draw.ellipse(petal_surf, (255, 180, 200), (petal_x - 3, petal_y - 2, 6, 4), 1)
            s.blit(petal_surf, (0, 0))
        # 整体柔光氛围（灯海效果）
        ambient_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        for glow_ring in range(3):
            glow_r = 40 + glow_ring * 20
            glow_alpha = 40 - glow_ring * 10
            pygame.draw.circle(ambient_glow, (255, 230, 190, glow_alpha), (60, 60), glow_r)
        s.blit(ambient_glow, (0, 0))
        return s
    
    return None
