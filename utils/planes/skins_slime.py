# -*- coding: utf-8 -*-
"""
末世星凝·史莱姆 - 涂装模块

至尊特殊型机体：零瞬移的远程链式吸附弹幕
将「星凝核心」「史莱姆凝胶」「重力漩涡」改写成远程链式+吸附弹幕
全程悬浮漂移，不闪现、不穿墙，保留「星球碾压」压迫感

主题配色：星凝紫+凝胶蓝
"""
import pygame
import math
import random

# 末世星凝涂装样式列表
SLIME_STYLES = [
    "slime_default",      # 星凝原型 - 紫蓝渐变+核心脉动
    "slime_cosmic",       # 宇宙凝胶 - 星云紫+银河蓝流动
    "slime_void",         # 虚空凝核 - 暗黑紫+空间裂隙
    "slime_crystal",      # 晶化形态 - 水晶透明+折射光芒
    "slime_toxic",        # 剧毒凝核 - 荧光绿+毒液滴落
    "slime_royal",        # 皇家凝胶 - 金紫华贵+王冠标记
    "slime_blood",        # 血染凝核 - 深红黑+血浆脉动
    "slime_ice",          # 极寒凝胶 - 冰蓝透明+冰晶飘浮
    "slime_flame",        # 炽焰凝核 - 熔岩橙红+火焰舞动
    "slime_phantom",      # 幽魂凝胶 - 幽蓝透明+灵魂飘散
    "slime_rainbow",      # 彩虹凝核 - 七彩渐变+棱镜光芒
    "slime_abyss",        # 深渊星陨 - 末世紫黑+星陨坠落
]


def is_slime_style(model_style):
    """检查是否为史莱姆涂装"""
    return model_style in SLIME_STYLES


def draw_slime(surface, color, x, y, w, h, frame=0, style="slime_default"):
    """绘制末世星凝·史莱姆"""
    renderers = {
        "slime_default": _draw_slime_default,
        "slime_cosmic": _draw_slime_cosmic,
        "slime_void": _draw_slime_void,
        "slime_crystal": _draw_slime_crystal,
        "slime_toxic": _draw_slime_toxic,
        "slime_royal": _draw_slime_royal,
        "slime_blood": _draw_slime_blood,
        "slime_ice": _draw_slime_ice,
        "slime_flame": _draw_slime_flame,
        "slime_phantom": _draw_slime_phantom,
        "slime_rainbow": _draw_slime_rainbow,
        "slime_abyss": _draw_slime_abyss,
    }
    draw_func = renderers.get(style, _draw_slime_default)
    draw_func(surface, color, x, y, w, h, frame)


def render_slime_skin(surface, color, model_style, t, pid, static):
    """渲染史莱姆涂装入口"""
    if not is_slime_style(model_style):
        return None
    frame = int(t * 60) if not static else 0
    draw_slime(surface, color, 10, 10, 100, 100, frame, model_style)
    return surface


# =============================================================================
#   核心辅助函数 - 史莱姆的凝胶元素（高品质版）
# =============================================================================

def _draw_slime_core(s, cx, cy, radius, t, core_col, pulse_col, pulse_rate=0.15):
    """星凝核心 - 多层脉动核心+能量脉冲+内部结构"""
    pulse = abs(math.sin(t * pulse_rate)) * 0.3 + 0.7
    core_r = int(radius * pulse)
    
    # 外层巨大光晕（7层渐变）
    for i in range(7):
        glow_r = core_r + (7 - i) * 6
        alpha = 25 + i * 12
        glow_col = (
            min(255, core_col[0] + (7 - i) * 8),
            min(255, core_col[1] + (7 - i) * 8),
            min(255, core_col[2] + (7 - i) * 8)
        )
        pygame.draw.circle(s, (*glow_col, alpha), (cx, cy), glow_r)
    
    # 核心主体（多层渐变）
    for layer in range(4):
        layer_r = core_r - layer * 3
        if layer_r > 0:
            layer_col = (
                min(255, core_col[0] + layer * 15),
                min(255, core_col[1] + layer * 15),
                min(255, core_col[2] + layer * 15)
            )
            pygame.draw.circle(s, layer_col, (cx, cy), layer_r)
    
    # 脉冲波纹（5层扩散）
    for i in range(5):
        wave_prog = ((t * 0.1 + i * 0.2) % 1.0)
        wave_r = int(core_r * (1 + wave_prog * 1.2))
        wave_alpha = int(180 * (1 - wave_prog))
        if wave_alpha > 0 and wave_r > 0:
            pygame.draw.circle(s, (*pulse_col[:3], wave_alpha), (cx, cy), wave_r, 2)
    
    # 内部能量流动
    for i in range(6):
        flow_angle = t * 0.3 + i * math.pi / 3
        flow_r = core_r * 0.5
        fx = cx + math.cos(flow_angle) * flow_r
        fy = cy + math.sin(flow_angle) * flow_r
        flow_size = 3 + int(math.sin(t * 0.4 + i) * 2)
        pygame.draw.circle(s, (*pulse_col[:3], 150), (int(fx), int(fy)), flow_size)
    
    # 核心高光（双层）
    highlight_r = max(3, core_r // 3)
    pygame.draw.circle(s, (255, 255, 255, 220), (cx - core_r // 4, cy - core_r // 4), highlight_r)
    pygame.draw.circle(s, (255, 255, 255, 180), (cx - core_r // 3, cy - core_r // 3), highlight_r // 2)
    
    # 核心中央亮点
    pygame.draw.circle(s, (255, 255, 255), (cx, cy), max(2, core_r // 5))


def _draw_slime_body(s, cx, cy, w, h, t, body_col, jiggle=True):
    """凝胶身体 - 超精细弹性变形+内部结构+层次感"""
    if jiggle:
        jiggle_x = math.sin(t * 0.2) * 4
        jiggle_y = math.cos(t * 0.15) * 3
    else:
        jiggle_x, jiggle_y = 0, 0
    
    # 身体主椭圆（带呼吸效果）
    breath = abs(math.sin(t * 0.12))
    body_w = int(w * (0.92 + breath * 0.08 + math.sin(t * 0.18) * 0.03))
    body_h = int(h * (0.88 - breath * 0.05 + math.cos(t * 0.18) * 0.03))
    
    # 外层阴影光晕（5层）
    for i in range(5):
        shadow_r_w = body_w + (5 - i) * 4
        shadow_r_h = body_h + (5 - i) * 3
        shadow_alpha = 20 + i * 8
        shadow_col = (max(0, body_col[0] - 30), max(0, body_col[1] - 30), max(0, body_col[2] - 30))
        pygame.draw.ellipse(s, (*shadow_col, shadow_alpha),
                           (cx - shadow_r_w // 2 + int(jiggle_x), 
                            cy - shadow_r_h // 2 + int(jiggle_y),
                            shadow_r_w, shadow_r_h))
    
    # 主体身体
    body_rect = (
        cx - body_w // 2 + int(jiggle_x),
        cy - body_h // 2 + int(jiggle_y),
        body_w, body_h
    )
    pygame.draw.ellipse(s, body_col, body_rect)
    
    # 边缘高光描边
    edge_col = tuple(min(255, c + 40) for c in body_col[:3])
    pygame.draw.ellipse(s, edge_col, body_rect, 2)
    
    # 多层凝胶高光（模拟透明质感）
    # 顶部大高光
    highlight_w = body_w * 2 // 3
    highlight_h = body_h // 3
    highlight_rect = (
        cx - highlight_w // 2 + int(jiggle_x),
        cy - body_h // 3 + int(jiggle_y),
        highlight_w, highlight_h
    )
    highlight_col = tuple(min(255, c + 60) for c in body_col[:3])
    pygame.draw.ellipse(s, (*highlight_col, 140), highlight_rect)
    
    # 小高光点
    small_hl_col = tuple(min(255, c + 80) for c in body_col[:3])
    pygame.draw.ellipse(s, (*small_hl_col, 180),
                       (cx - body_w // 4 + int(jiggle_x), cy - body_h // 4 + int(jiggle_y),
                        body_w // 5, body_h // 6))
    
    # 底部深色阴影
    shadow_rect = (
        cx - body_w // 3 + int(jiggle_x),
        cy + body_h // 6 + int(jiggle_y),
        body_w * 2 // 3, body_h // 4
    )
    shadow_col = tuple(max(0, c - 40) for c in body_col[:3])
    pygame.draw.ellipse(s, (*shadow_col, 100), shadow_rect)
    
    # 内部流动纹理（模拟凝胶内部）
    for i in range(6):
        flow_angle = t * 0.1 + i * math.pi / 3
        flow_r = body_w * 0.25 * (0.6 + 0.4 * math.sin(t * 0.15 + i))
        flow_x = cx + math.cos(flow_angle) * flow_r + jiggle_x
        flow_y = cy + math.sin(flow_angle) * flow_r * 0.7 + jiggle_y
        flow_size = 6 + int(math.sin(t * 0.2 + i) * 3)
        flow_col = tuple(min(255, c + 30) for c in body_col[:3])
        pygame.draw.circle(s, (*flow_col, 80), (int(flow_x), int(flow_y)), flow_size)
    
    return body_w, body_h


def _draw_gravity_tendrils(s, cx, cy, count, length, t, tendril_col, core_col):
    """重力触须 - 高品质吸附能量触手+末端光球+脉动效果"""
    for i in range(count):
        base_angle = (i * 2 * math.pi / count) + t * 0.08
        wave = math.sin(t * 0.15 + i * 0.5) * 0.4
        angle = base_angle + wave
        
        # 触须多段弯曲（更多段，更流畅）
        points = []
        segments = 8
        for seg in range(segments + 1):
            prog = seg / segments
            # 多层波动
            seg_wave = math.sin(t * 0.2 + i + seg * 0.6) * 10 * prog
            seg_wave += math.cos(t * 0.15 + i * 0.7 + seg * 0.4) * 5 * prog
            # S形弯曲
            curve = math.sin(prog * math.pi) * 8
            px = cx + math.cos(angle) * length * prog + seg_wave + curve * math.cos(angle + math.pi/2)
            py = cy + math.sin(angle) * length * prog + curve * math.sin(angle + math.pi/2)
            points.append((int(px), int(py)))
        
        # 触须渐变粗细（多层绘制，更立体）
        if len(points) >= 2:
            # 外层光晕
            for j in range(len(points) - 1):
                thickness = max(2, int(8 * (1 - j / len(points))))
                alpha = int(60 * (1 - j / len(points)))
                glow_col = (min(255, tendril_col[0] + 40), min(255, tendril_col[1] + 40), min(255, tendril_col[2] + 40))
                pygame.draw.line(s, (*glow_col, alpha), points[j], points[j+1], thickness + 4)
            
            # 主触须
            for j in range(len(points) - 1):
                thickness = max(1, int(5 * (1 - j / len(points))))
                alpha = int(220 * (1 - j / len(points) * 0.6))
                pygame.draw.line(s, (*tendril_col[:3], alpha), points[j], points[j+1], thickness)
            
            # 内部高光线
            for j in range(len(points) - 1):
                thickness = max(1, int(2 * (1 - j / len(points))))
                alpha = int(150 * (1 - j / len(points)))
                hl_col = (min(255, tendril_col[0] + 60), min(255, tendril_col[1] + 60), min(255, tendril_col[2] + 60))
                pygame.draw.line(s, (*hl_col, alpha), points[j], points[j+1], thickness)
        
        # 触须末端星凝球（多层发光）
        if points:
            end_x, end_y = points[-1]
            pulse = abs(math.sin(t * 0.3 + i * 0.8))
            ball_r = 4 + int(pulse * 3)
            
            # 光晕
            for layer in range(4):
                glow_r = ball_r + (4 - layer) * 3
                glow_alpha = 30 + layer * 20
                pygame.draw.circle(s, (*core_col[:3], glow_alpha), (end_x, end_y), glow_r)
            
            # 核心球
            pygame.draw.circle(s, core_col, (end_x, end_y), ball_r)
            pygame.draw.circle(s, (255, 255, 255), (end_x - 2, end_y - 2), max(1, ball_r // 2))
            
            # 能量射线（从末端向外）
            for ray in range(3):
                ray_angle = t * 0.5 + i + ray * math.pi * 2 / 3
                ray_len = 8 + pulse * 5
                rx = end_x + math.cos(ray_angle) * ray_len
                ry = end_y + math.sin(ray_angle) * ray_len
                pygame.draw.line(s, (*core_col[:3], 120), (end_x, end_y), (int(rx), int(ry)), 1)


def _draw_star_particles(s, cx, cy, radius, count, t, particle_col):
    """星凝粒子 - 高品质飘浮星尘+多层轨道+闪烁效果"""
    # 多层轨道粒子
    for orbit in range(3):
        orbit_r = radius * (0.5 + orbit * 0.25)
        orbit_count = count + orbit * 2
        orbit_speed = 0.1 - orbit * 0.02
        
        for i in range(orbit_count):
            angle = t * orbit_speed + i * (2 * math.pi / orbit_count) + orbit * 0.5
            # 轨道扁率
            dist_x = orbit_r * (1 + 0.15 * math.sin(t * 0.2 + i * 0.5))
            dist_y = orbit_r * 0.65 * (1 + 0.1 * math.cos(t * 0.15 + i * 0.3))
            # 上下浮动
            float_z = math.sin(t * 0.25 + i * 0.7) * 5
            
            px = cx + math.cos(angle) * dist_x
            py = cy + math.sin(angle) * dist_y + float_z
            
            # 闪烁效果
            twinkle = abs(math.sin(t * 0.4 + i * 1.3 + orbit))
            alpha = int(120 + 130 * twinkle)
            particle_size = 2 + int(twinkle * 2) - orbit
            
            if particle_size > 0:
                # 粒子光晕
                glow_col = (min(255, particle_col[0] + 30), min(255, particle_col[1] + 30), min(255, particle_col[2] + 30))
                pygame.draw.circle(s, (*glow_col, alpha // 3), (int(px), int(py)), particle_size + 3)
                # 粒子主体
                pygame.draw.circle(s, (*particle_col[:3], alpha), (int(px), int(py)), particle_size)
                
                # 十字星芒（主轨道粒子）
                if orbit == 0 and i % 2 == 0:
                    star_len = particle_size + 4 + int(twinkle * 3)
                    for angle_off in [0, math.pi/2, math.pi, math.pi*1.5]:
                        sx = px + math.cos(angle_off) * star_len
                        sy = py + math.sin(angle_off) * star_len
                        pygame.draw.line(s, (*particle_col[:3], alpha // 2), 
                                       (int(px), int(py)), (int(sx), int(sy)), 1)
                    # 对角星芒
                    for angle_off in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
                        sx = px + math.cos(angle_off) * (star_len * 0.6)
                        sy = py + math.sin(angle_off) * (star_len * 0.6)
                        pygame.draw.line(s, (*particle_col[:3], alpha // 3), 
                                       (int(px), int(py)), (int(sx), int(sy)), 1)


def _draw_gel_drips(s, cx, bottom_y, count, t, drip_col):
    """凝胶滴落 - 高品质黏稠滴落效果+拉丝+飞溅"""
    for i in range(count):
        drip_x = cx + (i - count // 2) * 14
        drip_phase = (t * 0.08 + i * 0.25) % 1.0
        drip_y = bottom_y + drip_phase * 25
        drip_size = int(5 * (1 - drip_phase * 0.7))
        
        if drip_size > 0:
            # 拉丝效果（多层渐变）
            stretch = drip_phase * 15
            for layer in range(3):
                layer_alpha = 80 - layer * 20 + int(40 * (1 - drip_phase))
                layer_width = 3 - layer
                if layer_width > 0:
                    # 拉丝主体
                    pygame.draw.line(s, (*drip_col[:3], layer_alpha), 
                                   (drip_x, bottom_y), (drip_x, int(drip_y - stretch * 0.3)), layer_width)
                    # 拉丝细化
                    if stretch > 5:
                        pygame.draw.line(s, (*drip_col[:3], layer_alpha // 2),
                                       (drip_x, int(drip_y - stretch * 0.3)), (drip_x, int(drip_y)), max(1, layer_width - 1))
            
            # 液滴主体（椭圆形+高光）
            drop_w = drip_size * 2
            drop_h = int(drip_size * 1.8)
            pygame.draw.ellipse(s, drip_col, 
                              (drip_x - drop_w // 2, int(drip_y), drop_w, drop_h))
            # 液滴高光
            hl_col = tuple(min(255, c + 50) for c in drip_col[:3])
            pygame.draw.ellipse(s, (*hl_col, 150),
                              (drip_x - drop_w // 4, int(drip_y) + 1, drop_w // 3, drop_h // 3))
            
            # 即将滴落时的颤动
            if drip_phase > 0.7:
                wobble = math.sin(t * 2 + i * 3) * 2
                pygame.draw.ellipse(s, drip_col,
                                  (drip_x - drop_w // 2 + int(wobble), int(drip_y) + 1, drop_w, drop_h - 2))
    
    # 地面水坑效果
    puddle_alpha = int(60 + 30 * math.sin(t * 0.3))
    puddle_w = count * 16
    pygame.draw.ellipse(s, (*drip_col[:3], puddle_alpha),
                       (cx - puddle_w // 2, int(bottom_y + 28), puddle_w, 8))


def _draw_gravity_vortex(s, cx, cy, radius, t, vortex_col, spiral_col):
    """重力漩涡 - 高品质吸引场视觉效果+多层螺旋+粒子吸入"""
    # 外层扭曲光环
    for ring in range(5):
        ring_r = radius - ring * 8
        if ring_r > 0:
            ring_alpha = 30 + ring * 15
            ring_wobble = math.sin(t * 0.2 + ring * 0.5) * 3
            pygame.draw.circle(s, (*vortex_col[:3], ring_alpha), 
                             (int(cx + ring_wobble), cy), int(ring_r), 2)
    
    # 多臂漩涡螺旋线（6臂）
    for arm in range(6):
        arm_offset = arm * math.pi / 3
        points = []
        for i in range(30):
            prog = i / 30
            # 对数螺旋
            spiral_angle = t * 0.2 + arm_offset + prog * math.pi * 3
            spiral_r = radius * prog
            # 添加波动
            wave = math.sin(t * 0.3 + prog * 5) * 3
            sx = cx + math.cos(spiral_angle) * (spiral_r + wave)
            sy = cy + math.sin(spiral_angle) * (spiral_r + wave) * 0.7
            points.append((int(sx), int(sy)))
        
        if len(points) >= 2:
            # 螺旋光晕
            for j in range(len(points) - 1):
                alpha = int(80 * (j / len(points)))
                thickness = max(1, int(4 * (j / len(points))))
                glow_col = (min(255, spiral_col[0] + 30), min(255, spiral_col[1] + 30), min(255, spiral_col[2] + 30))
                pygame.draw.line(s, (*glow_col, alpha // 2), points[j], points[j+1], thickness + 2)
            
            # 主螺旋线
            for j in range(len(points) - 1):
                alpha = int(180 * (j / len(points)))
                thickness = max(1, int(3 * (j / len(points))))
                pygame.draw.line(s, (*spiral_col[:3], alpha), points[j], points[j+1], thickness)
    
    # 被吸入的粒子
    for i in range(12):
        particle_angle = t * 0.15 + i * math.pi / 6
        particle_dist = radius * (1.2 - (t * 0.05 + i * 0.08) % 1.0)
        if particle_dist > 5:
            px = cx + math.cos(particle_angle) * particle_dist
            py = cy + math.sin(particle_angle) * particle_dist * 0.7
            p_size = 2 + int((1 - particle_dist / radius) * 3)
            p_alpha = int(200 * (particle_dist / radius))
            pygame.draw.circle(s, (*spiral_col[:3], p_alpha), (int(px), int(py)), max(1, p_size))
    
    # 中心黑洞效果
    for i in range(4):
        hole_r = 8 - i * 2
        if hole_r > 0:
            hole_alpha = 60 + i * 30
            pygame.draw.circle(s, (*vortex_col[:3], hole_alpha), (cx, cy), hole_r)
    
    # 漩涡边缘能量环
    pulse = abs(math.sin(t * 0.25))
    edge_r = int(radius + pulse * 5)
    pygame.draw.circle(s, (*vortex_col[:3], 80), (cx, cy), edge_r, 3)


# =============================================================================
#   12款专属涂装渲染（高品质版）
# =============================================================================

def _draw_slime_default(surface, color, x, y, w, h, frame):
    """默认涂装 - 星凝原型：史诗级紫蓝渐变+核心脉动+重力场"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    pulse = abs(math.sin(t * 0.2))
    
    # 颜色方案 - 星凝紫+凝胶蓝（高饱和度）
    body_main = (120, 80, 200)      # 星凝紫
    body_accent = (60, 140, 220)    # 凝胶蓝
    core_col = (180, 120, 255)      # 核心亮紫
    tendril_col = (100, 160, 255)   # 触须蓝
    particle_col = (200, 180, 255)  # 星尘紫
    glow_col = (140, 100, 230)      # 光晕紫
    
    # === 超大背景光晕（7层渐变） ===
    for i in range(7):
        glow_r = int(w * 0.55 - i * 6 + pulse * 8)
        glow_alpha = 25 + i * 8
        pygame.draw.circle(surface, (*glow_col, glow_alpha), (cx, cy), glow_r)
    
    # === 重力场漩涡（背景层） ===
    _draw_gravity_vortex(surface, cx, cy, int(w * 0.48), t, body_accent, particle_col)
    
    # === 重力触须（12条） ===
    _draw_gravity_tendrils(surface, cx, cy, 12, int(w * 0.48), t, tendril_col, core_col)
    
    # === 凝胶主体 ===
    body_w, body_h = _draw_slime_body(surface, cx, cy, w * 0.68, h * 0.58, t, body_main)
    
    # === 内部纹理 - 多层流动效果 ===
    for layer in range(2):
        for i in range(6):
            flow_angle = t * (0.12 - layer * 0.03) + i * math.pi / 3 + layer * 0.5
            flow_r = body_w * (0.28 - layer * 0.08)
            flow_x = cx + math.cos(flow_angle) * flow_r
            flow_y = cy + math.sin(flow_angle) * flow_r * 0.65
            flow_size = 10 - layer * 3 + int(math.sin(t * 0.2 + i + layer) * 2)
            flow_alpha = 100 - layer * 30
            pygame.draw.circle(surface, (*body_accent, flow_alpha), (int(flow_x), int(flow_y)), flow_size)
    
    # === 星凝核心（超大多层） ===
    _draw_slime_core(surface, cx, cy - 5, 22, t, core_col, particle_col)
    
    # === 多轨道星凝粒子 ===
    _draw_star_particles(surface, cx, cy, w * 0.52, 8, t, particle_col)
    
    # === 凝胶滴落 ===
    _draw_gel_drips(surface, cx, cy + int(body_h * 0.42), 5, t, body_main)
    
    # === 悬浮光环（多层） ===
    hover_y = cy + h * 0.38 + math.sin(t * 0.2) * 4
    for i in range(3):
        ring_alpha = 80 - i * 20
        ring_h = 10 - i * 2
        pygame.draw.ellipse(surface, (*body_accent, ring_alpha), 
                           (cx - w * 0.35 + i * 8, int(hover_y) + i * 2, w * 0.7 - i * 16, ring_h))
    
    # === 顶部装饰星芒 ===
    star_y = cy - body_h * 0.45
    for i in range(5):
        star_angle = -math.pi/2 + (i - 2) * 0.4 + math.sin(t * 0.3) * 0.1
        star_len = 15 + int(pulse * 8)
        sx = cx + math.cos(star_angle) * star_len
        sy = star_y + math.sin(star_angle) * star_len
        pygame.draw.line(surface, (*particle_col, 180), (cx, int(star_y)), (int(sx), int(sy)), 2)
        pygame.draw.circle(surface, particle_col, (int(sx), int(sy)), 3)


def _draw_slime_cosmic(surface, color, x, y, w, h, frame):
    """宇宙凝胶 - 史诗级星云紫+银河蓝流动+宇宙尘埃"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    pulse = abs(math.sin(t * 0.18))
    
    # 宇宙配色
    body_main = (60, 30, 140)       # 深空紫
    body_accent = (30, 80, 160)     # 银河蓝
    core_col = (140, 90, 240)       # 星云核心
    nebula_col = (180, 130, 255)    # 星云粉
    star_col = (255, 255, 220)      # 星光
    galaxy_col = (100, 60, 200)     # 银河紫
    
    # === 深空背景（多层星云） ===
    for layer in range(4):
        nebula_r = int(w * 0.55 - layer * 10 + pulse * 6)
        nebula_alpha = 35 - layer * 6
        pygame.draw.circle(surface, (*galaxy_col, nebula_alpha), (cx, cy), nebula_r)
    
    # === 银河漩涡（超大规模） ===
    _draw_gravity_vortex(surface, cx, cy, int(w * 0.52), t * 0.8, body_accent, nebula_col)
    
    # === 远处星系点（背景层） ===
    for i in range(20):
        star_angle = t * 0.02 + i * math.pi / 10
        star_dist = w * 0.48 + math.sin(i * 1.3) * 15
        sx = cx + math.cos(star_angle) * star_dist
        sy = cy + math.sin(star_angle) * star_dist * 0.6
        star_size = 1 + (i % 3)
        twinkle = abs(math.sin(t * 0.5 + i * 0.7))
        pygame.draw.circle(surface, (*star_col, int(100 + 155 * twinkle)), (int(sx), int(sy)), star_size)
    
    # === 重力触须 - 星云流（10条） ===
    _draw_gravity_tendrils(surface, cx, cy, 10, int(w * 0.5), t, nebula_col, star_col)
    
    # === 凝胶主体（深空质感） ===
    body_w, body_h = _draw_slime_body(surface, cx, cy, w * 0.62, h * 0.52, t, body_main)
    
    # === 内部星云旋转（双层） ===
    for layer in range(2):
        for i in range(6):
            nebula_angle = t * (0.1 - layer * 0.03) + i * math.pi / 3
            nebula_r = body_w * (0.32 - layer * 0.1)
            nx = cx + math.cos(nebula_angle) * nebula_r
            ny = cy + math.sin(nebula_angle) * nebula_r * 0.55
            size = 12 - layer * 4 + int(math.sin(t * 0.2 + i) * 3)
            col = nebula_col if layer == 0 else body_accent
            pygame.draw.circle(surface, (*col, 90 - layer * 25), (int(nx), int(ny)), size)
    
    # === 星凝核心 - 脉冲星效果 ===
    _draw_slime_core(surface, cx, cy - 3, 20, t * 1.5, core_col, star_col, 0.22)
    
    # === 脉冲星射线 ===
    for i in range(4):
        ray_angle = t * 0.4 + i * math.pi / 2
        ray_len = 35 + int(pulse * 15)
        rx = cx + math.cos(ray_angle) * ray_len
        ry = cy + math.sin(ray_angle) * ray_len * 0.5
        for thickness in range(3):
            pygame.draw.line(surface, (*star_col, 150 - thickness * 40),
                           (cx, cy - 3), (int(rx), int(ry)), 3 - thickness)
    
    # === 多轨道星尘粒子 ===
    _draw_star_particles(surface, cx, cy, w * 0.48, 10, t, star_col)
    
    # === 银河环（三层旋转） ===
    for ring in range(3):
        ring_y = cy + h * 0.4 + ring * 3 + math.sin(t * 0.2 + ring) * 3
        ring_angle = t * 0.1 + ring * 0.3
        ring_w = w * 0.65 - ring * 10
        ring_alpha = 70 - ring * 15
        pygame.draw.ellipse(surface, (*body_accent, ring_alpha),
                           (cx - ring_w // 2, int(ring_y), int(ring_w), 10 - ring * 2))


def _draw_slime_void(surface, color, x, y, w, h, frame):
    """虚空凝核 - 史诗级暗黑紫+空间裂隙+事件视界"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    pulse = abs(math.sin(t * 0.15))
    
    # 虚空配色
    body_main = (25, 12, 50)        # 深渊紫
    body_accent = (50, 25, 90)      # 暗紫
    core_col = (90, 45, 160)        # 虚空核心
    rift_col = (160, 70, 255)       # 裂隙光
    void_col = (8, 4, 20)           # 虚空黑
    event_col = (120, 60, 200)      # 事件视界
    
    # === 虚空吞噬背景（全黑渐变） ===
    for i in range(8):
        void_r = int(w * 0.58 - i * 5)
        void_alpha = 40 - i * 4
        pygame.draw.circle(surface, (*void_col, void_alpha), (cx, cy), void_r)
    
    # === 空间裂隙背景（多条闪烁裂缝） ===
    for i in range(8):
        rift_angle = t * 0.08 + i * math.pi / 4
        rift_len = w * 0.5 + math.sin(t * 0.3 + i) * 12
        # 裂隙起点（从核心区域开始）
        start_r = 15
        rx1 = cx + math.cos(rift_angle) * start_r
        ry1 = cy + math.sin(rift_angle) * start_r
        # 裂隙终点（锯齿状）
        points = [(int(rx1), int(ry1))]
        for seg in range(5):
            prog = (seg + 1) / 5
            jitter = math.sin(t * 0.5 + i + seg * 2) * 8
            px = cx + math.cos(rift_angle + jitter * 0.02) * rift_len * prog
            py = cy + math.sin(rift_angle + jitter * 0.02) * rift_len * prog * 0.65 + jitter
            points.append((int(px), int(py)))
        
        # 裂隙光晕
        if len(points) >= 2:
            for j in range(len(points) - 1):
                glow_alpha = int(80 * (1 - j / len(points)))
                pygame.draw.line(surface, (*rift_col, glow_alpha), points[j], points[j+1], 5)
            # 主裂隙线
            for j in range(len(points) - 1):
                line_alpha = int(200 * (1 - j / len(points) * 0.5))
                pygame.draw.line(surface, (*rift_col, line_alpha), points[j], points[j+1], 2)
    
    # === 重力触须 - 虚空丝（吸入效果） ===
    _draw_gravity_tendrils(surface, cx, cy, 12, int(w * 0.45), t, body_accent, rift_col)
    
    # === 凝胶主体 - 暗黑质感 ===
    body_w, body_h = _draw_slime_body(surface, cx, cy, w * 0.6, h * 0.5, t, body_main)
    
    # === 内部虚空涌动 ===
    for i in range(5):
        void_angle = t * 0.15 + i * math.pi * 2 / 5
        void_r = body_w * 0.25
        vx = cx + math.cos(void_angle) * void_r
        vy = cy + math.sin(void_angle) * void_r * 0.6
        pygame.draw.circle(surface, (*void_col, 150), (int(vx), int(vy)), 8)
        pygame.draw.circle(surface, (*body_accent, 100), (int(vx), int(vy)), 5)
    
    # === 虚空核心 - 黑洞效果（事件视界） ===
    # 多层事件视界
    for i in range(6):
        horizon_r = 22 - i * 3
        if horizon_r > 0:
            horizon_alpha = 50 + i * 25
            pygame.draw.circle(surface, (*event_col, horizon_alpha), (cx, cy - 2), horizon_r, 2)
    
    # 绝对黑暗核心
    pygame.draw.circle(surface, void_col, (cx, cy - 2), 12)
    pygame.draw.circle(surface, (0, 0, 0), (cx, cy - 2), 8)
    
    # 奇点闪光
    singularity_flash = abs(math.sin(t * 0.6))
    pygame.draw.circle(surface, (*rift_col, int(200 * singularity_flash)), (cx, cy - 2), 3)
    
    # === 裂隙粒子（被吸入） ===
    for i in range(15):
        angle = t * 0.12 + i * math.pi / 7.5
        dist = w * 0.4 * (1 - (t * 0.03 + i * 0.06) % 1.0)
        if dist > 8:
            px = cx + math.cos(angle) * dist
            py = cy + math.sin(angle) * dist * 0.6
            p_alpha = int(180 * (dist / (w * 0.4)))
            pygame.draw.circle(surface, (*rift_col, p_alpha), (int(px), int(py)), 2)
    
    # === 虚空滴落（暗物质） ===
    _draw_gel_drips(surface, cx, cy + int(body_h * 0.4), 4, t, void_col)


def _draw_slime_crystal(surface, color, x, y, w, h, frame):
    """晶化形态 - 史诗级水晶透明+棱镜折射+几何美学"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    pulse = abs(math.sin(t * 0.2))
    
    # 水晶配色
    body_main = (170, 195, 255)     # 透明蓝白
    body_accent = (210, 225, 255)   # 冰晶白
    core_col = (140, 175, 255)      # 水晶核心
    prism_colors = [
        (255, 180, 180), (255, 220, 160), (255, 255, 180),
        (180, 255, 200), (180, 220, 255), (200, 180, 255)
    ]
    
    # === 棱镜光芒背景（6方向彩虹射线） ===
    for i in range(6):
        ray_angle = t * 0.06 + i * math.pi / 3
        ray_len = w * 0.55 + pulse * 10
        col = prism_colors[i]
        # 多层光芒
        for layer in range(3):
            layer_len = ray_len - layer * 8
            layer_alpha = 100 - layer * 25
            rx = cx + math.cos(ray_angle) * layer_len
            ry = cy + math.sin(ray_angle) * layer_len * 0.6
            pygame.draw.line(surface, (*col, layer_alpha), (cx, cy), (int(rx), int(ry)), 4 - layer)
        # 光芒末端闪光
        flash = abs(math.sin(t * 0.4 + i))
        pygame.draw.circle(surface, (*col, int(200 * flash)), (int(rx), int(ry)), 5)
    
    # === 晶化触须（六边形结构） ===
    for i in range(6):
        angle = t * 0.04 + i * math.pi / 3
        length = w * 0.42
        col = prism_colors[i]
        
        # 棱柱形触须（多段）
        points = []
        for seg in range(6):
            prog = seg / 5
            # 锯齿形路径
            jitter = math.sin(prog * math.pi * 2) * 5
            px = cx + math.cos(angle) * length * prog + jitter * math.cos(angle + math.pi/2)
            py = cy + math.sin(angle) * length * prog + jitter * math.sin(angle + math.pi/2)
            points.append((int(px), int(py)))
        
        if len(points) >= 2:
            # 光晕
            pygame.draw.lines(surface, (*col, 60), False, points, 5)
            # 主线
            pygame.draw.lines(surface, (*col, 180), False, points, 2)
        
        # 末端水晶（多边形）
        if points:
            end_x, end_y = points[-1]
            crystal_size = 8 + int(pulse * 3)
            crystal_pts = []
            for j in range(6):
                ca = j * math.pi / 3 + t * 0.2
                cpx = end_x + math.cos(ca) * crystal_size
                cpy = end_y + math.sin(ca) * crystal_size * 0.8
                crystal_pts.append((int(cpx), int(cpy)))
            pygame.draw.polygon(surface, (*col, 180), crystal_pts)
            pygame.draw.polygon(surface, (255, 255, 255), crystal_pts, 1)
    
    # === 水晶主体（八边形+内部结构） ===
    crystal_pts = []
    for i in range(8):
        angle = i * math.pi / 4 + t * 0.02
        r = w * 0.3 + (i % 2) * w * 0.06 + pulse * 4
        px = cx + math.cos(angle) * r
        py = cy + math.sin(angle) * r * 0.75
        crystal_pts.append((int(px), int(py)))
    
    # 水晶主体
    pygame.draw.polygon(surface, (*body_main, 200), crystal_pts)
    pygame.draw.polygon(surface, body_accent, crystal_pts, 2)
    
    # 内部晶格
    for i in range(0, 8, 2):
        pygame.draw.line(surface, (*body_accent, 80), crystal_pts[i], (cx, cy), 1)
    
    # 高光面
    hl_pts = [crystal_pts[0], crystal_pts[1], (cx, cy)]
    pygame.draw.polygon(surface, (*body_accent, 100), hl_pts)
    
    # === 晶核（旋转内核） ===
    _draw_slime_core(surface, cx, cy, 16, t, core_col, body_accent, 0.25)
    
    # 内核棱镜
    for i in range(3):
        inner_angle = t * 0.5 + i * math.pi * 2 / 3
        inner_r = 8
        ix = cx + math.cos(inner_angle) * inner_r
        iy = cy + math.sin(inner_angle) * inner_r
        pygame.draw.circle(surface, prism_colors[i * 2], (int(ix), int(iy)), 4)
    
    # === 棱镜闪光波纹 ===
    for i in range(4):
        flash_prog = ((t * 0.15 + i * 0.25) % 1.0)
        flash_r = int(w * 0.45 * flash_prog)
        flash_alpha = int(150 * (1 - flash_prog))
        if flash_alpha > 0 and flash_r > 0:
            pygame.draw.circle(surface, (*prism_colors[i % 6], flash_alpha), (cx, cy), flash_r, 2)


def _draw_slime_toxic(surface, color, x, y, w, h, frame):
    """剧毒凝核 - 史诗级荧光绿+毒液滴落+危险标记+生化气息"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    pulse = abs(math.sin(t * 0.25))
    
    # 剧毒配色
    body_main = (60, 180, 40)       # 毒绿
    body_accent = (100, 255, 60)    # 荧光绿
    core_col = (140, 255, 80)       # 毒核
    bubble_col = (80, 220, 60)      # 毒泡
    drip_col = (50, 160, 30)        # 毒液
    warning_col = (255, 200, 0)     # 警告黄
    skull_col = (200, 200, 180)     # 骷髅白
    
    # === 毒气弥漫背景（多层扩散） ===
    for layer in range(4):
        for i in range(6):
            gas_angle = t * (0.1 - layer * 0.02) + i * math.pi / 3 + layer * 0.5
            gas_r = w * (0.5 - layer * 0.08) + math.sin(t * 0.2 + i + layer) * 12
            gx = cx + math.cos(gas_angle) * gas_r
            gy = cy + math.sin(gas_angle) * gas_r * 0.55 - layer * 8
            size = 18 - layer * 3 + int(math.sin(t * 0.15 + i) * 5)
            gas_alpha = 50 - layer * 10
            pygame.draw.circle(surface, (*body_main, gas_alpha), (int(gx), int(gy)), size)
    
    # === 毒触须（滴液效果） ===
    _draw_gravity_tendrils(surface, cx, cy, 10, int(w * 0.45), t, drip_col, bubble_col)
    
    # === 凝胶主体 ===
    body_w, body_h = _draw_slime_body(surface, cx, cy, w * 0.62, h * 0.52, t, body_main)
    
    # === 大量冒泡效果（多层） ===
    for layer in range(2):
        for i in range(8):
            bubble_phase = (t * (0.1 + layer * 0.03) + i * 0.12) % 1.0
            bx = cx + (i - 3.5) * 10 + math.sin(t * 0.2 + i) * 4 + layer * 3
            by = cy + body_h * 0.25 - bubble_phase * body_h * 0.6
            bubble_size = int((5 - layer * 2) * (1 - bubble_phase * 0.5))
            if bubble_size > 0:
                # 气泡光晕
                pygame.draw.circle(surface, (*bubble_col, 60), (int(bx), int(by)), bubble_size + 3)
                # 气泡主体
                pygame.draw.circle(surface, (*bubble_col, 180), (int(bx), int(by)), bubble_size)
                # 气泡高光
                pygame.draw.circle(surface, (255, 255, 255, 150), (int(bx) - 1, int(by) - 1), max(1, bubble_size // 2))
    
    # === 毒核（脉动+辐射） ===
    _draw_slime_core(surface, cx, cy - 3, 18, t * 1.3, core_col, body_accent, 0.2)
    
    # === 危险辐射标记 ===
    warning_pulse = abs(math.sin(t * 0.4))
    
    # 辐射符号
    symbol_y = cy - body_h * 0.35
    symbol_r = 10 + int(warning_pulse * 4)
    # 中心圆
    pygame.draw.circle(surface, (*warning_col, int(180 * warning_pulse)), (cx, int(symbol_y)), symbol_r // 2)
    # 三扇叶
    for i in range(3):
        fan_angle = i * math.pi * 2 / 3 - math.pi / 2
        fan_pts = [
            (cx, symbol_y),
            (cx + math.cos(fan_angle - 0.4) * symbol_r, symbol_y + math.sin(fan_angle - 0.4) * symbol_r),
            (cx + math.cos(fan_angle) * symbol_r * 1.5, symbol_y + math.sin(fan_angle) * symbol_r * 1.5),
            (cx + math.cos(fan_angle + 0.4) * symbol_r, symbol_y + math.sin(fan_angle + 0.4) * symbol_r),
        ]
        pygame.draw.polygon(surface, (*warning_col, int(150 * warning_pulse)), 
                          [(int(p[0]), int(p[1])) for p in fan_pts])
    
    # === 骷髅标记（隐约可见） ===
    skull_alpha = int(60 + 40 * math.sin(t * 0.2))
    pygame.draw.circle(surface, (*skull_col, skull_alpha), (cx, cy + 5), 8)  # 头
    pygame.draw.ellipse(surface, (*skull_col, skull_alpha), (cx - 3, cy + 2, 2, 3))  # 左眼
    pygame.draw.ellipse(surface, (*skull_col, skull_alpha), (cx + 1, cy + 2, 2, 3))  # 右眼
    
    # === 大量毒液滴落 ===
    _draw_gel_drips(surface, cx, cy + int(body_h * 0.38), 6, t, drip_col)


def _draw_slime_royal(surface, color, x, y, w, h, frame):
    """皇家凝胶 - 史诗级金紫华贵+王冠+宝石镶嵌+皇家纹章"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    pulse = abs(math.sin(t * 0.18))
    
    # 皇家配色
    body_main = (130, 70, 170)      # 皇家紫
    body_accent = (255, 200, 80)    # 皇金
    core_col = (190, 140, 255)      # 宝石紫
    crown_col = (255, 215, 0)       # 金色
    gem_red = (255, 80, 120)        # 红宝石
    gem_blue = (80, 180, 255)       # 蓝宝石
    gem_green = (100, 255, 150)     # 绿宝石
    velvet = (100, 40, 80)          # 天鹅绒
    
    # === 皇家光环背景（金色波纹） ===
    for i in range(5):
        ring_r = int(w * 0.52 - i * 8 + pulse * 6)
        ring_alpha = 50 + i * 12
        pygame.draw.circle(surface, (*body_accent, ring_alpha), (cx, cy), ring_r, 2)
    
    # === 皇家触须（金边） ===
    _draw_gravity_tendrils(surface, cx, cy + 5, 8, int(w * 0.42), t, body_main, crown_col)
    
    # === 凝胶主体 ===
    body_w, body_h = _draw_slime_body(surface, cx, cy + 5, w * 0.6, h * 0.5, t, body_main)
    
    # === 皇家纹章（内部花纹） ===
    for i in range(4):
        emblem_angle = t * 0.05 + i * math.pi / 2
        emblem_r = body_w * 0.25
        ex = cx + math.cos(emblem_angle) * emblem_r
        ey = cy + 5 + math.sin(emblem_angle) * emblem_r * 0.6
        # 鸢尾花纹（皇家符号）
        pygame.draw.ellipse(surface, (*body_accent, 100), (int(ex) - 6, int(ey) - 8, 12, 16))
        pygame.draw.circle(surface, (*body_accent, 150), (int(ex), int(ey) - 5), 3)
    
    # === 华丽王冠 ===
    crown_y = cy - body_h * 0.38
    # 王冠底座
    pygame.draw.rect(surface, crown_col, (cx - 22, int(crown_y) + 8, 44, 8))
    pygame.draw.rect(surface, (255, 240, 150), (cx - 22, int(crown_y) + 8, 44, 3))
    
    # 王冠尖塔（5个）
    spire_heights = [18, 25, 32, 25, 18]
    for i, h_spire in enumerate(spire_heights):
        spire_x = cx - 18 + i * 9
        spire_pts = [
            (spire_x - 4, crown_y + 8),
            (spire_x, crown_y + 8 - h_spire - pulse * 3),
            (spire_x + 4, crown_y + 8),
        ]
        pygame.draw.polygon(surface, crown_col, [(int(p[0]), int(p[1])) for p in spire_pts])
        # 尖端高光
        pygame.draw.polygon(surface, (255, 250, 200), [(int(p[0]), int(p[1])) for p in spire_pts], 1)
    
    # 王冠宝石（顶部大宝石+侧面小宝石）
    # 中央红宝石
    gem_y = crown_y + 8 - spire_heights[2]
    pygame.draw.circle(surface, gem_red, (cx, int(gem_y) + 5), 6)
    pygame.draw.circle(surface, (255, 200, 220), (cx - 2, int(gem_y) + 3), 2)
    
    # 侧面宝石
    gems = [(gem_blue, -9, spire_heights[1]), (gem_green, 9, spire_heights[3])]
    for col, dx, sh in gems:
        gx = cx + dx
        gy = crown_y + 8 - sh + 3
        pygame.draw.circle(surface, col, (int(gx), int(gy)), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(gx) - 1, int(gy) - 1), 1)
    
    # 天鹅绒内衬
    pygame.draw.ellipse(surface, velvet, (cx - 18, int(crown_y) + 10, 36, 6))
    
    # === 皇家核心（带宝石光芒） ===
    _draw_slime_core(surface, cx, cy + 5, 18, t, core_col, body_accent, 0.15)
    
    # === 环绕金粒子（带闪烁） ===
    for i in range(12):
        angle = t * 0.08 + i * math.pi / 6
        dist = w * 0.4
        px = cx + math.cos(angle) * dist
        py = cy + math.sin(angle) * dist * 0.65
        twinkle = abs(math.sin(t * 0.5 + i * 0.8))
        # 金粒子
        pygame.draw.circle(surface, (*crown_col, int(180 + 75 * twinkle)), (int(px), int(py)), 4)
        pygame.draw.circle(surface, (255, 255, 220), (int(px), int(py)), 2)
        # 十字闪光
        if twinkle > 0.7:
            for da in [0, math.pi/2]:
                lx = px + math.cos(da) * 6
                ly = py + math.sin(da) * 6
                pygame.draw.line(surface, (255, 255, 200, 200), (int(px), int(py)), (int(lx), int(ly)), 1)


def _draw_slime_blood(surface, color, x, y, w, h, frame):
    """血染凝核 - 史诗级深红黑+血浆脉动+心跳效果+血脉扩散"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 心跳效果（双脉冲）
    heartbeat1 = abs(math.sin(t * 0.5))
    heartbeat2 = abs(math.sin(t * 0.5 + 0.3)) * 0.6
    heartbeat = max(heartbeat1, heartbeat2)
    
    # 血染配色
    body_main = (100, 15, 35)       # 深血红
    body_accent = (160, 35, 55)     # 鲜血红
    core_col = (180, 45, 70)        # 血核
    vein_col = (70, 8, 25)          # 血管暗
    pulse_col = (255, 90, 110)      # 脉动亮
    artery_col = (200, 60, 80)      # 动脉红
    
    # === 血脉扩散网络（复杂静脉网） ===
    for layer in range(2):
        for i in range(8):
            vein_angle = t * 0.04 + i * math.pi / 4 + layer * 0.2
            # 主静脉
            points = []
            for seg in range(7):
                prog = seg / 6
                # 有机弯曲
                curve = math.sin(prog * math.pi * 1.5 + i) * 10
                branch = math.cos(prog * math.pi * 2 + t * 0.2) * 5 * prog
                vx = cx + math.cos(vein_angle) * w * 0.48 * prog + curve * math.cos(vein_angle + math.pi/2)
                vy = cy + math.sin(vein_angle) * h * 0.4 * prog + branch
                points.append((int(vx), int(vy)))
            
            if len(points) >= 2:
                # 血管脉动光晕
                for j in range(len(points) - 1):
                    glow_alpha = int(40 * heartbeat * (1 - j / len(points)))
                    pygame.draw.line(surface, (*pulse_col, glow_alpha), points[j], points[j+1], 6)
                # 主血管
                for j in range(len(points) - 1):
                    thickness = max(1, int(4 * (1 - j / len(points))))
                    vein_c = vein_col if layer == 0 else artery_col
                    pygame.draw.line(surface, vein_c, points[j], points[j+1], thickness)
            
            # 分支血管
            if layer == 0 and len(points) > 3:
                branch_start = points[3]
                for b in range(2):
                    branch_angle = vein_angle + (b - 0.5) * 0.8
                    bx = branch_start[0] + math.cos(branch_angle) * 15
                    by = branch_start[1] + math.sin(branch_angle) * 12
                    pygame.draw.line(surface, vein_col, branch_start, (int(bx), int(by)), 2)
    
    # === 血触须 ===
    _draw_gravity_tendrils(surface, cx, cy, 10, int(w * 0.44), t, vein_col, pulse_col)
    
    # === 凝胶主体 ===
    body_w, body_h = _draw_slime_body(surface, cx, cy, w * 0.62, h * 0.52, t, body_main)
    
    # === 血浆脉动（从核心扩散，心跳节奏） ===
    for i in range(4):
        pulse_phase = ((t * 0.2 + i * 0.25) % 1.0)
        pulse_r = int(body_w * 0.35 * (1 + pulse_phase * 0.8))
        pulse_alpha = int(180 * (1 - pulse_phase) * heartbeat)
        if pulse_alpha > 0 and pulse_r > 0:
            pygame.draw.circle(surface, (*pulse_col, pulse_alpha), (cx, cy), pulse_r, 3)
    
    # === 血核心（跳动的心脏） ===
    core_r = int(18 * (0.85 + heartbeat * 0.15))
    # 多层光晕
    for i in range(5):
        glow_r = core_r + (5 - i) * 4
        glow_alpha = int((30 + i * 15) * heartbeat)
        pygame.draw.circle(surface, (*pulse_col, glow_alpha), (cx, cy), glow_r)
    # 核心
    pygame.draw.circle(surface, core_col, (cx, cy), core_r)
    # 血管纹理
    for i in range(4):
        v_angle = i * math.pi / 2 + t * 0.1
        vx = cx + math.cos(v_angle) * core_r * 0.6
        vy = cy + math.sin(v_angle) * core_r * 0.6
        pygame.draw.line(surface, vein_col, (cx, cy), (int(vx), int(vy)), 2)
    # 高光
    pygame.draw.circle(surface, (255, 150, 170), (cx - core_r // 3, cy - core_r // 3), core_r // 3)
    
    # === 血滴飞溅 ===
    _draw_gel_drips(surface, cx, cy + int(body_h * 0.4), 5, t * 1.5, body_accent)


def _draw_slime_ice(surface, color, x, y, w, h, frame):
    """极寒凝胶 - 史诗级冰蓝透明+冰晶飘浮+霜冻效果+寒气"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    pulse = abs(math.sin(t * 0.15))
    
    # 冰霜配色
    body_main = (140, 195, 255)     # 冰蓝
    body_accent = (195, 225, 255)   # 霜白
    core_col = (170, 215, 255)      # 冰核
    crystal_col = (215, 235, 255)   # 冰晶
    snow_col = (255, 255, 255)      # 雪白
    frost_col = (100, 180, 255)     # 霜蓝
    
    # === 寒气弥漫背景 ===
    for layer in range(3):
        for i in range(5):
            frost_angle = t * 0.05 + i * math.pi / 2.5 + layer * 0.4
            frost_r = w * (0.52 - layer * 0.1) + math.sin(t * 0.1 + i) * 8
            fx = cx + math.cos(frost_angle) * frost_r
            fy = cy + math.sin(frost_angle) * frost_r * 0.6 + layer * 5
            size = 20 - layer * 5 + int(math.sin(t * 0.12 + i) * 4)
            pygame.draw.circle(surface, (*body_accent, 40 - layer * 10), (int(fx), int(fy)), size)
    
    # === 飘浮六边形冰晶（多层轨道） ===
    for orbit in range(2):
        for i in range(6 + orbit * 2):
            crystal_angle = t * (0.06 - orbit * 0.015) + i * math.pi / (3 + orbit)
            crystal_r = w * (0.45 - orbit * 0.08) + math.sin(t * 0.15 + i) * 8
            cx_pos = cx + math.cos(crystal_angle) * crystal_r
            cy_pos = cy + math.sin(crystal_angle) * crystal_r * 0.6
            
            # 六边形冰晶
            crystal_size = 7 - orbit * 2 + int(pulse * 2)
            hex_pts = []
            for j in range(6):
                ha = j * math.pi / 3 + t * 0.1
                hx = cx_pos + math.cos(ha) * crystal_size
                hy = cy_pos + math.sin(ha) * crystal_size
                hex_pts.append((int(hx), int(hy)))
            
            # 冰晶光晕
            pygame.draw.polygon(surface, (*crystal_col, 60), hex_pts)
            # 冰晶主体
            pygame.draw.polygon(surface, (*crystal_col, 200), hex_pts)
            # 冰晶边缘
            pygame.draw.polygon(surface, snow_col, hex_pts, 1)
            # 内部结构
            pygame.draw.line(surface, (*snow_col, 150), hex_pts[0], hex_pts[3], 1)
            pygame.draw.line(surface, (*snow_col, 150), hex_pts[1], hex_pts[4], 1)
            pygame.draw.line(surface, (*snow_col, 150), hex_pts[2], hex_pts[5], 1)
    
    # === 冰触须（霜化） ===
    _draw_gravity_tendrils(surface, cx, cy, 8, int(w * 0.4), t * 0.8, body_accent, crystal_col)
    
    # === 透明凝胶主体（冰质感） ===
    body_w, body_h = _draw_slime_body(surface, cx, cy, w * 0.6, h * 0.5, t, (*body_main, 200))
    
    # === 内部冰裂纹（有机纹路） ===
    for i in range(6):
        crack_cx = cx + (random.Random(i * 7).random() - 0.5) * body_w * 0.5
        crack_cy = cy + (random.Random(i * 13).random() - 0.5) * body_h * 0.4
        # 裂纹分支
        for branch in range(3):
            branch_angle = random.Random(i * 17 + branch).random() * math.pi * 2
            branch_len = 10 + random.Random(i * 23 + branch).random() * 10
            bx = crack_cx + math.cos(branch_angle) * branch_len
            by = crack_cy + math.sin(branch_angle) * branch_len * 0.7
            pygame.draw.line(surface, (*body_accent, 120), (int(crack_cx), int(crack_cy)), (int(bx), int(by)), 1)
    
    # === 冰核（冻结效果） ===
    _draw_slime_core(surface, cx, cy, 16, t * 0.7, core_col, snow_col, 0.12)
    
    # 核心冰晶结构
    for i in range(6):
        ice_angle = i * math.pi / 3
        ice_len = 10
        ix = cx + math.cos(ice_angle) * ice_len
        iy = cy + math.sin(ice_angle) * ice_len
        pygame.draw.line(surface, (*snow_col, 180), (cx, cy), (int(ix), int(iy)), 2)
    
    # === 雪花粒子飘落 ===
    for i in range(10):
        snow_y = (cy - h * 0.45 + (t * 15 + i * 25) % (h * 0.9))
        snow_x = cx + math.sin(t * 0.3 + i * 2) * w * 0.4
        snow_size = 2 + (i % 3)
        # 雪花六角
        for j in range(6):
            sa = j * math.pi / 3
            sx = snow_x + math.cos(sa) * snow_size
            sy = snow_y + math.sin(sa) * snow_size
            pygame.draw.line(surface, snow_col, (int(snow_x), int(snow_y)), (int(sx), int(sy)), 1)
        pygame.draw.circle(surface, snow_col, (int(snow_x), int(snow_y)), 1)
    
    # === 底部冷气蔓延 ===
    for i in range(3):
        cold_y = cy + h * 0.35 + i * 4
        cold_alpha = 60 - i * 15
        cold_w = w * 0.75 - i * 10
        pygame.draw.ellipse(surface, (*frost_col, cold_alpha),
                           (cx - cold_w // 2, int(cold_y), int(cold_w), 10 - i * 2))


def _draw_slime_flame(surface, color, x, y, w, h, frame):
    """炽焰凝核 - 史诗级熔岩橙红+火焰舞动+岩浆纹理+余烬升腾"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    pulse = abs(math.sin(t * 0.2))
    
    # 炽焰配色
    body_main = (180, 60, 20)       # 熔岩橙
    body_accent = (255, 140, 40)    # 火焰黄
    core_col = (255, 200, 80)       # 炎核
    flame_col = (255, 80, 20)       # 烈焰
    ember_col = (255, 60, 10)       # 余烬
    magma_col = (200, 40, 10)       # 岩浆暗
    heat_col = (255, 255, 150)      # 高温白
    
    # === 热浪背景（扭曲效果） ===
    for layer in range(3):
        for i in range(6):
            heat_angle = t * 0.08 + i * math.pi / 3 + layer * 0.3
            heat_r = w * (0.55 - layer * 0.1) + math.sin(t * 0.15 + i) * 10
            hx = cx + math.cos(heat_angle) * heat_r + math.sin(t * 0.3 + i) * 5
            hy = cy + math.sin(heat_angle) * heat_r * 0.5 - layer * 10
            size = 18 - layer * 4
            pygame.draw.circle(surface, (*body_accent, 35 - layer * 8), (int(hx), int(hy)), size)
    
    # === 火焰舞动（多层火焰柱） ===
    for layer in range(2):
        for i in range(12 - layer * 4):
            flame_base_x = cx + (i - (5.5 - layer * 2)) * (8 + layer * 2)
            base_height = 28 - layer * 8 + math.sin(t * 0.5 + i * 0.7) * 14
            flame_wave = math.sin(t * 0.4 + i * 0.5 + layer) * 6
            
            # 火焰形状（多边形）
            flame_pts = [
                (flame_base_x - 5 + layer, cy - 12 - layer * 5),
                (flame_base_x + flame_wave * 0.5, cy - 12 - layer * 5 - base_height),
                (flame_base_x + 5 - layer, cy - 12 - layer * 5),
            ]
            
            # 火焰光晕
            glow_pts = [
                (flame_base_x - 8 + layer, cy - 10 - layer * 5),
                (flame_base_x + flame_wave * 0.3, cy - 8 - layer * 5 - base_height * 1.1),
                (flame_base_x + 8 - layer, cy - 10 - layer * 5),
            ]
            glow_col = flame_col if layer == 0 else body_accent
            pygame.draw.polygon(surface, (*glow_col, 60), 
                              [(int(p[0]), int(p[1])) for p in glow_pts])
            
            # 主火焰
            flame_c = flame_col if layer == 0 else body_accent
            alpha = 200 - layer * 50 + int(pulse * 30)
            pygame.draw.polygon(surface, (*flame_c, alpha), 
                              [(int(p[0]), int(p[1])) for p in flame_pts])
            
            # 火焰内芯（高温白）
            if layer == 0:
                inner_pts = [
                    (flame_base_x - 2, cy - 15),
                    (flame_base_x + flame_wave * 0.2, cy - 15 - base_height * 0.6),
                    (flame_base_x + 2, cy - 15),
                ]
                pygame.draw.polygon(surface, (*heat_col, 150), 
                                  [(int(p[0]), int(p[1])) for p in inner_pts])
    
    # === 熔岩触须 ===
    _draw_gravity_tendrils(surface, cx, cy + 8, 8, int(w * 0.38), t * 1.3, ember_col, body_accent)
    
    # === 凝胶主体（熔岩质感） ===
    body_w, body_h = _draw_slime_body(surface, cx, cy + 8, w * 0.58, h * 0.48, t, body_main)
    
    # === 熔岩纹理（流动裂隙） ===
    for i in range(8):
        lava_angle = t * 0.12 + i * math.pi / 4
        lava_r = body_w * 0.32
        lx = cx + math.cos(lava_angle) * lava_r
        ly = cy + 8 + math.sin(lava_angle) * lava_r * 0.6
        # 熔岩光晕
        pygame.draw.circle(surface, (*body_accent, 100), (int(lx), int(ly)), 10)
        # 熔岩核心
        pygame.draw.circle(surface, (*core_col, 180), (int(lx), int(ly)), 6)
        # 高温点
        pygame.draw.circle(surface, (*heat_col, 150), (int(lx), int(ly)), 3)
    
    # === 炎核（超热中心） ===
    _draw_slime_core(surface, cx, cy + 8, 20, t * 1.6, core_col, heat_col, 0.22)
    
    # === 余烬粒子升腾 ===
    for i in range(12):
        ember_phase = (t * 0.15 + i * 0.08) % 1.0
        ex = cx + (i - 5.5) * 10 + math.sin(t * 0.3 + i) * 8
        ey = cy + 5 - ember_phase * h * 0.7
        ember_size = int(4 * (1 - ember_phase * 0.7))
        if ember_size > 0:
            # 余烬光晕
            pygame.draw.circle(surface, (*body_accent, int(80 * (1 - ember_phase))), 
                             (int(ex), int(ey)), ember_size + 3)
            # 余烬主体
            pygame.draw.circle(surface, (*ember_col, int(220 * (1 - ember_phase))), 
                             (int(ex), int(ey)), ember_size)
            # 高温核
            if ember_phase < 0.3:
                pygame.draw.circle(surface, (*heat_col, int(200 * (1 - ember_phase * 3))),
                                 (int(ex), int(ey)), max(1, ember_size - 1))


def _draw_slime_phantom(surface, color, x, y, w, h, frame):
    """幽魂凝胶 - 史诗级幽蓝透明+灵魂飘散+以太层+鬼火缭绕"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 幽魂配色
    body_main = (80, 120, 180)      # 幽蓝
    body_accent = (130, 180, 240)   # 灵光
    core_col = (180, 220, 255)      # 魂核
    ghost_col = (200, 235, 255)     # 幽白
    wisp_col = (100, 140, 200)      # 魂丝
    ether_col = (160, 200, 255)     # 以太
    void_col = (60, 80, 120)        # 虚空
    
    # 透明度波动（呼吸+闪烁）
    ghost_alpha = int(100 + 50 * math.sin(t * 0.2) + 25 * math.sin(t * 0.55))
    flicker = int(30 * math.sin(t * 0.8))
    
    # === 以太场背景（多层涟漪） ===
    for layer in range(4):
        ether_r = w * (0.55 - layer * 0.08) + math.sin(t * 0.15 + layer) * 10
        ether_alpha = 30 - layer * 6 + int(math.sin(t * 0.25 + layer * 0.5) * 8)
        pygame.draw.ellipse(surface, (*ether_col, ether_alpha),
                          (int(cx - ether_r), int(cy - ether_r * 0.7), 
                           int(ether_r * 2), int(ether_r * 1.4)))
    
    # === 鬼火缭绕（环绕幽光） ===
    for i in range(8):
        ghost_angle = t * 0.12 + i * math.pi / 4
        ghost_r = w * 0.42 + math.sin(t * 0.2 + i * 0.5) * 8
        gx = cx + math.cos(ghost_angle) * ghost_r
        gy = cy + math.sin(ghost_angle) * ghost_r * 0.5
        bob = math.sin(t * 0.4 + i * 1.2) * 6
        
        # 鬼火外晕
        pygame.draw.circle(surface, (*ether_col, 40), (int(gx), int(gy + bob)), 12)
        pygame.draw.circle(surface, (*body_accent, 80), (int(gx), int(gy + bob)), 8)
        # 鬼火内芯
        pygame.draw.circle(surface, (*ghost_col, 160 + flicker), (int(gx), int(gy + bob)), 5)
        pygame.draw.circle(surface, (255, 255, 255, 120), (int(gx), int(gy + bob)), 3)
    
    # === 灵魂拖尾（多层渐隐） ===
    for i in range(7):
        tail_y = cy + h * 0.28 + i * 10
        tail_alpha = ghost_alpha - i * 14
        tail_w = w * 0.52 - i * w * 0.06
        wave = math.sin(t * 0.25 + i * 0.4) * 4
        if tail_alpha > 0:
            # 外层晕
            pygame.draw.ellipse(surface, (*void_col, max(0, tail_alpha - 30)),
                              (int(cx - tail_w // 2 - 4 + wave), int(tail_y - 2), 
                               int(tail_w + 8), 14))
            # 主体
            pygame.draw.ellipse(surface, (*wisp_col, tail_alpha),
                              (int(cx - tail_w // 2 + wave), int(tail_y), int(tail_w), 10))
            # 内芯
            pygame.draw.ellipse(surface, (*body_accent, min(255, tail_alpha + 20)),
                              (int(cx - tail_w // 3 + wave), int(tail_y + 2), 
                               int(tail_w * 0.6), 6))
    
    # === 幽魂触须（多段飘动） ===
    for i in range(8):
        angle = t * 0.08 + i * math.pi / 4
        drift_base = math.sin(t * 0.15 + i) * 10
        
        for seg in range(6):
            prog = seg / 5
            drift = drift_base * (1 + prog * 0.5) + math.sin(t * 0.25 + i + seg * 0.6) * 6 * prog
            px = cx + math.cos(angle) * w * 0.38 * prog + drift
            py = cy + math.sin(angle) * h * 0.32 * prog
            seg_alpha = int(ghost_alpha * (1 - prog * 0.6))
            seg_size = max(1, 6 - seg)
            
            # 触须节光晕
            if seg_size > 2:
                pygame.draw.circle(surface, (*ether_col, seg_alpha // 2), 
                                 (int(px), int(py)), seg_size + 2)
            pygame.draw.circle(surface, (*ghost_col, seg_alpha), (int(px), int(py)), seg_size)
    
    # === 透明凝胶主体（多层透明度） ===
    body_w = int(w * 0.56)
    body_h = int(h * 0.46)
    
    # 外层虚影
    pygame.draw.ellipse(surface, (*void_col, ghost_alpha // 3), 
                       (cx - body_w // 2 - 5, cy - body_h // 2 - 3, body_w + 10, body_h + 6))
    # 主体
    pygame.draw.ellipse(surface, (*body_main, ghost_alpha), 
                       (cx - body_w // 2, cy - body_h // 2, body_w, body_h))
    # 内层光泽
    pygame.draw.ellipse(surface, (*body_accent, ghost_alpha // 2),
                       (cx - body_w // 2 + 4, cy - body_h // 2 + 4, body_w - 8, body_h - 8))
    
    # === 幽光高光（双层） ===
    pygame.draw.ellipse(surface, (*ghost_col, ghost_alpha // 2 + 20),
                       (cx - body_w // 3, cy - body_h // 3, body_w // 2, body_h // 3))
    pygame.draw.ellipse(surface, (255, 255, 255, ghost_alpha // 3),
                       (cx - body_w // 4, cy - body_h // 2.5, body_w // 3, body_h // 5))
    
    # === 以太纹理（内部流动） ===
    for i in range(5):
        ether_angle = t * 0.1 + i * math.pi * 2 / 5
        er = body_w * 0.28
        ex = cx + math.cos(ether_angle) * er
        ey = cy + math.sin(ether_angle) * er * 0.7
        pygame.draw.circle(surface, (*ether_col, 80 + flicker), (int(ex), int(ey)), 6)
    
    # === 魂核（多层+脉动） ===
    core_pulse = math.sin(t * 0.3)
    core_alpha = int(180 + 50 * core_pulse)
    core_size = 16 + int(core_pulse * 3)
    
    # 核外晕
    pygame.draw.circle(surface, (*void_col, 60), (cx, cy), core_size + 8)
    pygame.draw.circle(surface, (*body_main, 100), (cx, cy), core_size + 4)
    # 主核
    pygame.draw.circle(surface, (*core_col, core_alpha), (cx, cy), core_size)
    # 高光双点
    pygame.draw.circle(surface, (*ghost_col, core_alpha + 30), (cx - 5, cy - 5), 6)
    pygame.draw.circle(surface, (255, 255, 255, 180), (cx - 6, cy - 6), 3)
    pygame.draw.circle(surface, (255, 255, 255, 120), (cx + 3, cy - 3), 2)
    
    # === 飘散灵魂粒子（多层轨道） ===
    for layer in range(2):
        for i in range(6):
            soul_phase = (t * (0.08 + layer * 0.03) + i * 0.15 + layer * 0.5) % 1.0
            orbit_r = w * (0.3 + layer * 0.1)
            sx = cx + math.sin(t * 0.15 + i * 2 + layer) * orbit_r * (1 - soul_phase * 0.3)
            sy = cy - soul_phase * h * (0.5 + layer * 0.15)
            soul_alpha = int((ghost_alpha + 40) * (1 - soul_phase))
            soul_size = 4 - layer
            
            if soul_alpha > 0:
                # 灵魂光晕
                pygame.draw.circle(surface, (*ether_col, soul_alpha // 2), 
                                 (int(sx), int(sy)), soul_size + 3)
                # 灵魂主体
                pygame.draw.circle(surface, (*ghost_col, soul_alpha), (int(sx), int(sy)), soul_size)
                # 灵魂亮点
                if soul_phase < 0.4:
                    pygame.draw.circle(surface, (255, 255, 255, int(soul_alpha * 0.6)),
                                     (int(sx), int(sy)), max(1, soul_size - 1))


def _draw_slime_rainbow(surface, color, x, y, w, h, frame):
    """彩虹凝核 - 史诗级七彩渐变+棱镜光芒+彩虹旋涡+光谱粒子"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 彩虹七色（高饱和）
    rainbow = [
        (255, 80, 80),    # 红
        (255, 160, 60),   # 橙
        (255, 240, 80),   # 黄
        (80, 255, 130),   # 绿
        (80, 180, 255),   # 蓝
        (130, 100, 255),  # 靛
        (200, 100, 255),  # 紫
    ]
    white = (255, 255, 255)
    
    # 色相循环偏移
    color_shift = int(t * 1.5) % 7
    
    # === 彩虹旋涡背景 ===
    for layer in range(3):
        for i in range(14):
            spiral_angle = t * (0.08 - layer * 0.02) + i * math.pi / 7 + layer * 0.5
            spiral_r = w * (0.52 - layer * 0.08) + math.sin(t * 0.15 + i + layer) * 8
            sx = cx + math.cos(spiral_angle) * spiral_r
            sy = cy + math.sin(spiral_angle) * spiral_r * 0.6
            col = rainbow[(i + color_shift + layer) % 7]
            size = 10 - layer * 2
            pygame.draw.circle(surface, (*col, 60 - layer * 15), (int(sx), int(sy)), size)
    
    # === 彩虹光环（多层发光） ===
    for ring in range(2):
        for i, col in enumerate(rainbow):
            ring_r = w * (0.48 - ring * 0.08) - i * 4
            offset_x = math.sin(t * 0.2 + i * 0.3 + ring) * 4
            offset_y = math.cos(t * 0.25 + i * 0.4 + ring) * 2
            alpha = 100 - ring * 30
            pygame.draw.circle(surface, (*col, alpha), 
                             (int(cx + offset_x), int(cy + offset_y)), int(ring_r), 3 - ring)
    
    # === 棱镜光芒（交叉彩虹射线） ===
    for i in range(14):
        ray_angle = t * 0.06 + i * math.pi / 7
        ray_len = w * 0.55 + math.sin(t * 0.25 + i * 0.5) * 15
        col = rainbow[i % 7]
        
        rx = cx + math.cos(ray_angle) * ray_len
        ry = cy + math.sin(ray_angle) * ray_len * 0.55
        
        # 光芒外晕
        pygame.draw.line(surface, (*col, 50), (cx, cy), (int(rx), int(ry)), 6)
        # 光芒主体
        pygame.draw.line(surface, (*col, 120), (cx, cy), (int(rx), int(ry)), 3)
        # 光芒内芯
        pygame.draw.line(surface, (*white, 80), (cx, cy), 
                        (int(cx + (rx - cx) * 0.5), int(cy + (ry - cy) * 0.5)), 1)
    
    # === 彩虹触须（七彩分段） ===
    for i in range(7):
        angle = t * 0.1 + i * math.pi * 2 / 7
        col = rainbow[(i + color_shift) % 7]
        
        for seg in range(6):
            prog = seg / 5
            wave = math.sin(t * 0.3 + i + seg * 0.6) * 8 * prog
            px = cx + math.cos(angle) * w * 0.42 * prog + wave
            py = cy + math.sin(angle) * h * 0.36 * prog
            seg_size = max(1, 6 - seg)
            
            # 触须节光晕
            pygame.draw.circle(surface, (*col, 100), (int(px), int(py)), seg_size + 3)
            pygame.draw.circle(surface, (*col, 200), (int(px), int(py)), seg_size)
            if seg == 5:
                pygame.draw.circle(surface, (*white, 150), (int(px), int(py)), 2)
    
    # === 渐变凝胶主体（七色分层） ===
    body_w, body_h = int(w * 0.56), int(h * 0.46)
    
    # 外层光晕
    pygame.draw.ellipse(surface, (*rainbow[color_shift], 40),
                       (cx - body_w // 2 - 6, cy - body_h // 2 - 4, body_w + 12, body_h + 8))
    
    # 分层渐变
    for i, col in enumerate(rainbow):
        layer_h = body_h // 7 + 2
        layer_y = cy - body_h // 2 + i * (body_h // 7)
        shift_idx = (i + color_shift) % 7
        shifted_col = rainbow[shift_idx]
        pygame.draw.ellipse(surface, (*shifted_col, 170),
                           (cx - body_w // 2, int(layer_y), body_w, layer_h + 4))
    
    # 主体光泽
    pygame.draw.ellipse(surface, (*white, 50),
                       (cx - body_w // 3, cy - body_h // 3, body_w // 2, body_h // 3))
    pygame.draw.ellipse(surface, (*white, 80),
                       (cx - body_w // 4, cy - body_h // 2.5, body_w // 3, body_h // 5))
    
    # === 棱镜核心（颜色循环） ===
    core_col_idx = int(t * 2) % 7
    next_col_idx = (core_col_idx + 1) % 7
    core_col = rainbow[core_col_idx]
    next_col = rainbow[next_col_idx]
    
    # 核心外晕
    pygame.draw.circle(surface, (*next_col, 80), (cx, cy), 22)
    pygame.draw.circle(surface, (*core_col, 120), (cx, cy), 18)
    # 主核
    pygame.draw.circle(surface, core_col, (cx, cy), 14)
    # 高光
    pygame.draw.circle(surface, white, (cx - 5, cy - 5), 5)
    pygame.draw.circle(surface, (*white, 180), (cx + 3, cy - 3), 2)
    
    # === 彩虹粒子（双层轨道） ===
    for layer in range(2):
        for i in range(14):
            angle = t * (0.12 - layer * 0.04) + i * math.pi / 7 + layer * 0.5
            dist = w * (0.4 - layer * 0.08)
            col = rainbow[i % 7]
            px = cx + math.cos(angle) * dist
            py = cy + math.sin(angle) * dist * 0.65
            size = 4 - layer
            
            # 粒子光晕
            pygame.draw.circle(surface, (*col, 100), (int(px), int(py)), size + 2)
            pygame.draw.circle(surface, col, (int(px), int(py)), size)
    
    # === 光谱爆发效果 ===
    burst_phase = (t * 0.1) % 1.0
    if burst_phase < 0.3:
        burst_r = w * 0.3 + burst_phase * w * 0.4
        burst_alpha = int(100 * (1 - burst_phase / 0.3))
        for i in range(7):
            burst_col = rainbow[i]
            pygame.draw.circle(surface, (*burst_col, burst_alpha // 7), 
                             (cx, cy), int(burst_r + i * 3), 2)


def _draw_slime_abyss(surface, color, x, y, w, h, frame):
    """深渊星陨 - 史诗级末世紫黑+星陨坠落+次元裂隙+毁灭脉冲"""
    cx, cy = x + w // 2, y + h // 2
    t = frame * 0.05
    
    # 末世配色
    body_main = (40, 20, 70)        # 末世紫黑
    body_accent = (90, 50, 130)     # 深渊紫
    core_col = (160, 100, 220)      # 星陨核心
    meteor_col = (220, 160, 255)    # 流星紫
    star_col = (255, 220, 255)      # 星光
    crack_col = (200, 80, 255)      # 裂隙
    void_col = (20, 10, 40)         # 虚空
    doom_col = (255, 100, 180)      # 毁灭粉
    
    pulse = abs(math.sin(t * 0.2))
    doom_pulse = abs(math.sin(t * 0.15))
    
    # === 末世压迫感背景（层层黑暗） ===
    for layer in range(4):
        doom_r = w * (0.6 - layer * 0.08) + math.sin(t * 0.1 + layer) * 8
        pygame.draw.circle(surface, (*void_col, 50 - layer * 10), (cx, cy), int(doom_r))
    
    # === 次元裂隙（闪电状） ===
    for i in range(8):
        crack_angle = t * 0.05 + i * math.pi / 4
        crack_len = w * 0.55
        
        points = [(cx, cy)]
        for seg in range(7):
            prog = (seg + 1) / 7
            jitter_x = math.sin(t * 0.35 + i + seg * 0.8) * 12 * prog
            jitter_y = math.cos(t * 0.4 + i * 2 + seg) * 8 * prog
            px = cx + math.cos(crack_angle) * crack_len * prog + jitter_x
            py = cy + math.sin(crack_angle) * crack_len * prog * 0.65 + jitter_y
            points.append((int(px), int(py)))
        
        if len(points) >= 2:
            # 裂隙外晕
            pygame.draw.lines(surface, (*body_accent, 80), False, points, 5)
            # 裂隙主体
            pygame.draw.lines(surface, (*crack_col, 160), False, points, 2)
            # 裂隙高光
            pygame.draw.lines(surface, (*star_col, 100), False, points[:4], 1)
    
    # === 毁灭脉冲环（扩散） ===
    for ring in range(3):
        ring_phase = (t * 0.12 + ring * 0.33) % 1.0
        ring_r = w * 0.2 + ring_phase * w * 0.45
        ring_alpha = int(120 * (1 - ring_phase))
        pygame.draw.circle(surface, (*doom_col, ring_alpha), (cx, cy), int(ring_r), 3 - ring)
    
    # === 星陨触须（深渊版） ===
    _draw_gravity_tendrils(surface, cx, cy + 5, 10, int(w * 0.48), t * 0.9, body_accent, meteor_col)
    
    # === 凝胶主体（虚空质感） ===
    body_w, body_h = _draw_slime_body(surface, cx, cy + 5, w * 0.6, h * 0.5, t, body_main)
    
    # === 虚空纹理（吞噬涡流） ===
    for layer in range(2):
        for i in range(6):
            void_angle = t * (0.08 - layer * 0.02) + i * math.pi / 3 + layer * 0.5
            void_r = body_w * (0.3 - layer * 0.08)
            vx = cx + math.cos(void_angle) * void_r
            vy = cy + 5 + math.sin(void_angle) * void_r * 0.65
            size = 8 - layer * 3
            pygame.draw.circle(surface, (*void_col, 180), (int(vx), int(vy)), size)
            pygame.draw.circle(surface, (*body_accent, 120), (int(vx), int(vy)), size - 2)
    
    # === 内部星陨（轨道流星） ===
    for layer in range(2):
        for i in range(5 - layer * 2):
            meteor_angle = t * (0.14 - layer * 0.04) + i * math.pi * 2 / (5 - layer * 2) + layer
            meteor_r = body_w * (0.28 - layer * 0.08)
            mx = cx + math.cos(meteor_angle) * meteor_r
            my = cy + 5 + math.sin(meteor_angle) * meteor_r * 0.6
            
            # 流星尾迹（多层）
            tail_len = 18 - layer * 5
            for tl in range(3):
                t_prog = tl / 2
                tx = mx - math.cos(meteor_angle) * tail_len * (1 - t_prog * 0.3)
                ty = my - math.sin(meteor_angle) * tail_len * 0.6 * (1 - t_prog * 0.3)
                t_alpha = 180 - tl * 50
                t_width = 4 - tl
                pygame.draw.line(surface, (*meteor_col, t_alpha), 
                               (int(mx), int(my)), (int(tx), int(ty)), t_width)
            
            # 流星头
            pygame.draw.circle(surface, (*meteor_col, 220), (int(mx), int(my)), 6 - layer * 2)
            pygame.draw.circle(surface, (*star_col, 180), (int(mx), int(my)), 3 - layer)
    
    # === 末世核心（脉动+裂纹） ===
    core_size = 20 + int(pulse * 4)
    
    # 核外虚空
    pygame.draw.circle(surface, (*void_col, 100), (cx, cy + 3), core_size + 10)
    pygame.draw.circle(surface, (*body_accent, 80), (cx, cy + 3), core_size + 5)
    
    # 主核
    _draw_slime_core(surface, cx, cy + 3, core_size, t * 1.2, core_col, star_col, 0.2)
    
    # 核心裂纹
    for i in range(6):
        crack_a = i * math.pi / 3 + t * 0.08
        crack_len = core_size * 0.8
        c_end_x = cx + math.cos(crack_a) * crack_len
        c_end_y = cy + 3 + math.sin(crack_a) * crack_len
        pygame.draw.line(surface, (*crack_col, 150), (cx, cy + 3), 
                        (int(c_end_x), int(c_end_y)), 1)
    
    # === 星陨坠落粒子（多层轨迹） ===
    for layer in range(2):
        for i in range(8 - layer * 3):
            fall_phase = (t * (0.15 - layer * 0.04) + i * (0.12 + layer * 0.05)) % 1.0
            spread = (i - (3.5 - layer * 1.5)) * (14 - layer * 4)
            fx = cx + spread + math.sin(t * 0.2 + i + layer) * 6
            fy = cy - h * 0.55 + fall_phase * h * 1.1
            
            # 流星拖尾
            trail_len = 20 - layer * 6
            for tl in range(3):
                t_alpha = int(200 * (1 - fall_phase) * (1 - tl * 0.3))
                if t_alpha > 0:
                    pygame.draw.line(surface, (*meteor_col, t_alpha),
                                   (int(fx), int(fy)), (int(fx), int(fy - trail_len * (1 - tl * 0.3))), 
                                   3 - tl)
            
            # 流星头
            head_alpha = int(220 * (1 - fall_phase))
            if head_alpha > 0:
                pygame.draw.circle(surface, (*star_col, head_alpha), (int(fx), int(fy)), 4 - layer)
                pygame.draw.circle(surface, (255, 255, 255, head_alpha // 2), 
                                 (int(fx), int(fy)), 2)
    
    # === 末世压迫光环（多层呼吸） ===
    for i in range(4):
        doom_r = w * (0.54 - i * 0.06) + doom_pulse * 6
        doom_alpha = 30 + i * 15 + int(doom_pulse * 20)
        pygame.draw.circle(surface, (*body_accent, doom_alpha), (cx, cy + 3), int(doom_r), 2)
    
    # === 凝胶滴落（末世版） ===
    _draw_gel_drips(surface, cx, cy + int(body_h * 0.42), 5, t * 1.1, body_main)
    
    # === 毁灭星辰装饰 ===
    for i in range(6):
        star_angle = t * 0.07 + i * math.pi / 3
        star_r = w * 0.5 + math.sin(t * 0.2 + i) * 10
        sx = cx + math.cos(star_angle) * star_r
        sy = cy + math.sin(star_angle) * star_r * 0.6
        twinkle = abs(math.sin(t * 0.4 + i * 1.5))
        star_size = int(3 + twinkle * 2)
        
        # 星辰光晕
        pygame.draw.circle(surface, (*doom_col, int(60 * twinkle)), (int(sx), int(sy)), star_size + 4)
        pygame.draw.circle(surface, (*star_col, int(180 * twinkle)), (int(sx), int(sy)), star_size)
        pygame.draw.circle(surface, (255, 255, 255, int(200 * twinkle)), (int(sx), int(sy)), max(1, star_size - 1))
