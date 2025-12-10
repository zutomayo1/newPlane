# Arbiter 专属涂装渲染模块
# 包含: quantum, fractal, law, balance, judge, arbiter_matrix, truth

import pygame
import math

# Arbiter涂装列表
ARBITER_STYLES = ["quantum", "fractal", "law", "balance", "judge", "arbiter_matrix", "truth", "arbiter_ex", "arbiter_ex2", "arbiter_ex3", "arbiter_ex4", "arbiter_ex5"]

def is_arbiter_style(model_style):
    """检查是否为Arbiter涂装"""
    return model_style in ARBITER_STYLES

def render_arbiter_skin(s, c, model_style, t, pid, static=False):
    """渲染Arbiter涂装，返回Surface或None"""
    
    if model_style == "quantum":
        # 量子裁决·概率坍缩 - 量子叠加态、概率云、波函数坍缩、量子纠缠
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：量子核心（叠加态）
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 叠加态效果（多个半透明核心）
        for i in range(3):
            offset_x = int(6 * math.sin(t * 3 + i * 2))
            offset_y = int(6 * math.cos(t * 3 + i * 2))
            core_alpha = int(180 - i * 40)
            pygame.draw.circle(core_surface, (180, 100, 255, core_alpha), (60 + offset_x, 50 + offset_y), 12)
        s.blit(core_surface, (0, 0))
        
        # 概率云（漂浮云团）
        cloud_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(25):
            cloud_angle = t * 2 + i * math.pi / 12.5
            cloud_dist = 20 + 15 * (i / 25) + 5 * math.sin(t * 3 + i)
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 50 + math.sin(cloud_angle) * cloud_dist
            cloud_alpha = int(150 * (1 - (i / 25)))
            pygame.draw.circle(cloud_surface, (220, 150, 255, cloud_alpha), (int(cloud_x), int(cloud_y)), 4)
        s.blit(cloud_surface, (0, 0))
        
        # 波函数坍缩（收缩波）
        for i in range(4):
            collapse_phase = (t * 3 + i * 0.5) % 2
            if collapse_phase < 1:  # 收缩阶段
                collapse_radius = 35 - collapse_phase * 20
                collapse_alpha = int(200 * collapse_phase)
            else:  # 扩散阶段
                collapse_radius = 15 + (collapse_phase - 1) * 20
                collapse_alpha = int(200 * (2 - collapse_phase))
            collapse_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(collapse_surface, (180, 100, 255, collapse_alpha), (60, 50), int(collapse_radius), 2)
            s.blit(collapse_surface, (0, 0))
        
        # 量子纠缠（粒子对连接）
        entangle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            angle1 = t * 2 + i * math.pi / 3
            angle2 = angle1 + math.pi
            dist = 25 + 5 * math.sin(t * 3 + i)
            x1 = 60 + math.cos(angle1) * dist
            y1 = 50 + math.sin(angle1) * dist
            x2 = 60 + math.cos(angle2) * dist
            y2 = 50 + math.sin(angle2) * dist
            # 纠缠连线
            pygame.draw.line(entangle_surface, (220, 150, 255, 180), (int(x1), int(y1)), (int(x2), int(y2)), 2)
            # 纠缠粒子对
            pygame.draw.circle(entangle_surface, (180, 100, 255, 220), (int(x1), int(y1)), 4)
            pygame.draw.circle(entangle_surface, (180, 100, 255, 220), (int(x2), int(y2)), 4)
        s.blit(entangle_surface, (0, 0))
        
        return s
    
    elif model_style == "fractal":
        # 分形几何·无限循环 - 分形结构、几何递归、数学美学、完美对称
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：Sierpinski三角形（分形）
        def draw_sierpinski(surface, p1, p2, p3, depth, color_offset):
            if depth == 0:
                alpha = int(180 + 75 * math.sin(t * 2 + color_offset))
                pygame.draw.polygon(surface, (255, 0, 255, alpha), [p1, p2, p3], 2)
                return
            # 中点
            mid1 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
            mid2 = ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2)
            mid3 = ((p3[0] + p1[0]) / 2, (p3[1] + p1[1]) / 2)
            # 递归绘制
            draw_sierpinski(surface, p1, mid1, mid3, depth - 1, color_offset + 0.5)
            draw_sierpinski(surface, mid1, p2, mid2, depth - 1, color_offset + 1)
            draw_sierpinski(surface, mid3, mid2, p3, depth - 1, color_offset + 1.5)
        
        # 绘制分形
        fractal_depth = 3 + int(math.sin(t) * 0.5 + 0.5)
        draw_sierpinski(s, (60, 20), (90, 70), (30, 70), fractal_depth, t)
        
        # 旋转的分形粒子
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            particle_angle = t * 3 + i * math.pi / 6
            particle_dist = 35 + 8 * math.sin(t * 2 + i)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            # 小三角粒子
            size = 4
            tri_points = [
                (particle_x, particle_y - size),
                (particle_x + size, particle_y + size),
                (particle_x - size, particle_y + size)
            ]
            pygame.draw.polygon(particle_surface, (0, 255, 255, 220), [(int(p[0]), int(p[1])) for p in tri_points])
        s.blit(particle_surface, (0, 0))
        
        # 完美对称线
        symmetry_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            sym_angle = i * math.pi / 4
            sym_x = 60 + math.cos(sym_angle) * 40
            sym_y = 50 + math.sin(sym_angle) * 40
            pygame.draw.line(symmetry_surface, (200, 100, 255, 150), (60, 50), (int(sym_x), int(sym_y)), 1)
        s.blit(symmetry_surface, (0, 0))
        
        return s
    
    elif model_style == "law":
        # 法则之书·规则编写 - 法则之书、规则条文、法则粒子、规则执行
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：法则之书（展开的书页）
        book_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 左页
        pygame.draw.rect(book_surface, (255, 215, 0, 230), (30, 30, 25, 40))
        pygame.draw.rect(book_surface, (255, 255, 255, 230), (30, 30, 25, 40), 2)
        # 右页
        pygame.draw.rect(book_surface, (255, 215, 0, 230), (65, 30, 25, 40))
        pygame.draw.rect(book_surface, (255, 255, 255, 230), (65, 30, 25, 40), 2)
        # 书脊
        pygame.draw.line(book_surface, (200, 180, 0, 250), (60, 30), (60, 70), 3)
        s.blit(book_surface, (0, 0))
        
        # 规则条文（文字模拟）
        text_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for page_offset in [0, 35]:
            for i in range(6):
                line_y = 35 + i * 5
                line_length = 18 + int(3 * math.sin(t * 2 + i))
                pygame.draw.line(text_surface, (100, 80, 0, 220), (32 + page_offset, line_y), 
                               (32 + page_offset + line_length, line_y), 1)
        s.blit(text_surface, (0, 0))
        
        # 法则粒子（符文环绕）
        rune_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            rune_angle = t * 1.5 + i * math.pi / 6
            rune_dist = 40 + 8 * math.sin(t * 2.5 + i)
            rune_x = 60 + math.cos(rune_angle) * rune_dist
            rune_y = 50 + math.sin(rune_angle) * rune_dist
            # 符文（方形）
            pygame.draw.rect(rune_surface, (255, 215, 0, 220), (int(rune_x - 2), int(rune_y - 2), 4, 4))
            pygame.draw.rect(rune_surface, (255, 255, 255, 220), (int(rune_x - 2), int(rune_y - 2), 4, 4), 1)
        s.blit(rune_surface, (0, 0))
        
        # 规则执行（律令光束）
        execute_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            if (int(t * 4) + i) % 3 == 0:
                exec_angle = i * math.pi / 3
                exec_x = 60 + math.cos(exec_angle) * 50
                exec_y = 50 + math.sin(exec_angle) * 50
                pygame.draw.line(execute_surface, (255, 255, 255, 220), (60, 50), (int(exec_x), int(exec_y)), 2)
        s.blit(execute_surface, (0, 0))
        
        # 法则光环
        for i in range(3):
            law_radius = 35 + i * 10 + int(6 * pulse)
            law_alpha = int(150 * (1 - i / 3))
            law_ring = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(law_ring, (255, 215, 0, law_alpha), (60, 50), law_radius, 2)
            s.blit(law_ring, (0, 0))
        
        return s
    
    elif model_style == "balance":
        # 平衡裁决·天平永恒 - 天平、公正秤杆、平衡粒子、秩序维持
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：天平结构
        # 支柱
        pygame.draw.line(s, (128, 128, 128), (60, 25), (60, 65), 4)
        pygame.draw.line(s, (200, 200, 200), (60, 25), (60, 65), 2)
        # 底座
        pygame.draw.rect(s, (128, 128, 128), (50, 65, 20, 5))
        pygame.draw.rect(s, (200, 200, 200), (50, 65, 20, 5), 1)
        
        # 秤杆（平衡摆动）
        tilt = math.sin(t * 1.5) * 0.2
        beam_left_x = 60 - 25 * math.cos(tilt)
        beam_left_y = 35 + 25 * math.sin(tilt)
        beam_right_x = 60 + 25 * math.cos(tilt)
        beam_right_y = 35 - 25 * math.sin(tilt)
        pygame.draw.line(s, (128, 128, 128), (int(beam_left_x), int(beam_left_y)), 
                        (int(beam_right_x), int(beam_right_y)), 4)
        pygame.draw.line(s, (200, 200, 200), (int(beam_left_x), int(beam_left_y)), 
                        (int(beam_right_x), int(beam_right_y)), 2)
        
        # 秤盘（左右）
        for side, (bx, by) in [(0, (beam_left_x, beam_left_y)), (1, (beam_right_x, beam_right_y))]:
            # 悬挂链
            chain_y = by + 10
            pygame.draw.line(s, (150, 150, 150), (int(bx), int(by)), (int(bx), int(chain_y)), 2)
            # 秤盘
            pygame.draw.circle(s, (128, 128, 128), (int(bx), int(chain_y + 5)), 8)
            pygame.draw.circle(s, (200, 200, 200), (int(bx), int(chain_y + 5)), 8, 1)
        
        # 平衡粒子（飘散）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            particle_angle = t * 2 + i * math.pi / 8
            particle_dist = 35 + 10 * math.sin(t * 2.5 + i)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (150, 150, 150, 220), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        # 秩序光环
        for i in range(4):
            order_radius = 30 + i * 10 + int(5 * pulse)
            order_alpha = int(150 * (1 - i / 4))
            order_ring = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(order_ring, (200, 200, 200, order_alpha), (60, 45), order_radius, 2)
            s.blit(order_ring, (0, 0))
        
        return s
    
    elif model_style == "judge":
        # 终极审判·公正天平 - 审判天平、公正符文、裁决之光、法则之力
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：黄金天平
        # 支柱（发光）
        pillar_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(pillar_surface, (255, 255, 200, 250), (60, 20), (60, 70), 5)
        pygame.draw.line(pillar_surface, (255, 255, 255, 220), (60, 20), (60, 70), 3)
        s.blit(pillar_surface, (0, 0))
        
        # 黄金底座
        pygame.draw.rect(s, (255, 215, 0), (48, 70, 24, 6))
        pygame.draw.rect(s, (255, 255, 200), (48, 70, 24, 6), 2)
        
        # 秤杆（绝对平衡）
        beam_y = 35
        pygame.draw.line(s, (255, 215, 0), (30, beam_y), (90, beam_y), 5)
        pygame.draw.line(s, (255, 255, 200), (30, beam_y), (90, beam_y), 3)
        
        # 秤盘（左右平衡）
        for pan_x in [30, 90]:
            # 悬挂链
            pygame.draw.line(s, (200, 180, 0), (pan_x, beam_y), (pan_x, beam_y + 15), 2)
            # 秤盘（发光）
            pan_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(pan_surface, (255, 215, 0, 250), (pan_x, beam_y + 20), 10)
            pygame.draw.circle(pan_surface, (255, 255, 200, 220), (pan_x, beam_y + 20), int(10 * pulse))
            s.blit(pan_surface, (0, 0))
        
        # 公正符文（闪耀）
        rune_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            if (int(t * 5) + i) % 4 < 2:
                rune_angle = i * math.pi / 4
                rune_x = 60 + math.cos(rune_angle) * 45
                rune_y = 45 + math.sin(rune_angle) * 45
                # 符文（十字）
                pygame.draw.line(rune_surface, (255, 255, 200, 250), (int(rune_x - 3), int(rune_y)), 
                               (int(rune_x + 3), int(rune_y)), 2)
                pygame.draw.line(rune_surface, (255, 255, 200, 250), (int(rune_x), int(rune_y - 3)), 
                               (int(rune_x), int(rune_y + 3)), 2)
        s.blit(rune_surface, (0, 0))
        
        # 裁决之光（从天而降）
        judgment_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            light_y = 10 + ((t * 80 + i * 15) % 70)
            light_alpha = int(220 * (1 - ((t * 80 + i * 15) % 70) / 70))
            pygame.draw.line(judgment_surface, (255, 255, 255, light_alpha), (60, int(light_y)), (60, int(light_y + 10)), 4)
        s.blit(judgment_surface, (0, 0))
        
        # 法则光环
        for i in range(4):
            law_radius = 40 + i * 12 + int(8 * pulse)
            law_alpha = int(180 * (1 - i / 4))
            law_ring = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(law_ring, (255, 255, 200, law_alpha), (60, 45), law_radius, 3)
            s.blit(law_ring, (0, 0))
        
        return s
    
    elif model_style == "arbiter_matrix":
        # 矩阵主宰·代码执行 - 矩阵世界、代码洪流、程序执行、数字主宰
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：矩阵核心
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_surface, (0, 255, 100, 250), (60, 50), 12)
        pygame.draw.circle(core_surface, (100, 255, 150, 230), (60, 50), int(12 * pulse))
        s.blit(core_surface, (0, 0))
        
        # 代码流（垂直下落）
        code_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            code_x = 20 + i * 10
            code_length = 30 + int(20 * math.sin(t * 2 + i))
            code_y = ((t * 60 + i * 12) % 130) - 10
            # 代码串（渐变）
            for j in range(int(code_length / 3)):
                char_y = code_y + j * 3
                char_alpha = int(220 * (1 - j * 3 / code_length))
                if 0 <= char_y <= 120:
                    pygame.draw.rect(code_surface, (0, 255, 100, char_alpha), (code_x, int(char_y), 2, 2))
        s.blit(code_surface, (0, 0))
        
        # 矩阵网格
        grid_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(0, 120, 15):
            grid_alpha = int(100 + 80 * math.sin(t * 2 + i * 0.1))
            pygame.draw.line(grid_surface, (0, 255, 100, grid_alpha), (0, i), (120, i), 1)
            pygame.draw.line(grid_surface, (0, 255, 100, grid_alpha), (i, 0), (i, 120), 1)
        s.blit(grid_surface, (0, 0))
        
        # 程序执行节点
        node_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            node_angle = t * 2 + i * math.pi / 4
            node_dist = 28 + 8 * math.sin(t * 3 + i)
            node_x = 60 + math.cos(node_angle) * node_dist
            node_y = 50 + math.sin(node_angle) * node_dist
            pygame.draw.circle(node_surface, (100, 255, 150, 220), (int(node_x), int(node_y)), 4)
            # 连接到核心
            pygame.draw.line(node_surface, (50, 255, 120, 180), (60, 50), (int(node_x), int(node_y)), 2)
        s.blit(node_surface, (0, 0))
        
        # 数据流粒子
        data_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            data_angle = t * 3 + i * math.pi / 10
            data_dist = 20 + ((t * 40 + i * 5) % 30)
            data_x = 60 + math.cos(data_angle) * data_dist
            data_y = 50 + math.sin(data_angle) * data_dist
            pygame.draw.circle(data_surface, (100, 255, 150, 220), (int(data_x), int(data_y)), 2)
        s.blit(data_surface, (0, 0))
        
        return s
    
    elif model_style == "truth":
        # 真理之眼·洞察一切 - 真理之眼、洞察本质、真理光芒、一切明晰
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.2 + 1
        
        # 主体：全视之眼
        # 眼睛轮廓（杏仁形）
        eye_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        eye_points = [
            (40, 50),
            (50, 40),
            (70, 40),
            (80, 50),
            (70, 60),
            (50, 60)
        ]
        pygame.draw.polygon(eye_surface, (255, 255, 255, 240), eye_points)
        pygame.draw.polygon(eye_surface, (255, 255, 220, 250), eye_points, 2)
        s.blit(eye_surface, (0, 0))
        
        # 眼球（发光）
        eyeball_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(eyeball_surface, (255, 255, 255, 250), (60, 50), 12)
        pygame.draw.circle(eyeball_surface, (255, 255, 220, 230), (60, 50), int(12 * pulse))
        s.blit(eyeball_surface, (0, 0))
        
        # 瞳孔（洞察）
        pupil_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(pupil_surface, (100, 100, 150, 250), (60, 50), 6)
        pygame.draw.circle(pupil_surface, (255, 255, 255, 250), (62, 48), 2)  # 高光
        s.blit(pupil_surface, (0, 0))
        
        # 真理光芒（放射状）
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            ray_angle = t * 1.5 + i * math.pi / 8
            ray_length = 35 + 15 * math.sin(t * 3 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 50 + math.sin(ray_angle) * ray_length
            ray_alpha = int(200 + 55 * math.sin(t * 4 + i))
            pygame.draw.line(ray_surface, (255, 255, 240, ray_alpha), (60, 50), (int(ray_x), int(ray_y)), 3)
        s.blit(ray_surface, (0, 0))
        
        # 洞察波纹（扫描）
        scan_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            scan_radius = (t * 60 + i * 20) % 80
            scan_alpha = int(200 * (1 - scan_radius / 80))
            pygame.draw.circle(scan_surface, (255, 255, 220, scan_alpha), (60, 50), int(scan_radius), 2)
        s.blit(scan_surface, (0, 0))
        
        # 真理符文（环绕）
        rune_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            rune_angle = t + i * math.pi / 6
            rune_dist = 40 + 8 * math.sin(t * 2.5 + i)
            rune_x = 60 + math.cos(rune_angle) * rune_dist
            rune_y = 50 + math.sin(rune_angle) * rune_dist
            # 符文（圆形）
            pygame.draw.circle(rune_surface, (255, 255, 220, 220), (int(rune_x), int(rune_y)), 3)
            pygame.draw.circle(rune_surface, (255, 255, 255, 220), (int(rune_x), int(rune_y)), 2)
        s.blit(rune_surface, (0, 0))
        
        # 一切明晰光环
        for i in range(3):
            clarity_radius = 45 + i * 12 + int(10 * pulse)
            clarity_alpha = int(180 * (1 - i / 3))
            clarity_ring = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(clarity_ring, (255, 255, 255, clarity_alpha), (60, 50), clarity_radius, 2)
            s.blit(clarity_ring, (0, 0))
        
        return s
    
    elif model_style == "arbiter_ex":
        # 量子审判 - 概率云，量子纠缠
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心量子核心
        pygame.draw.circle(s, (0, 255, 255), (60, 50), int(12 * pulse))
        pygame.draw.circle(s, (100, 255, 255), (60, 50), int(12 * pulse), 3)
        
        # 概率云（随机位置粒子）
        for i in range(30):
            # 使用确定性随机（基于时间和索引）
            cloud_angle = (t * 3 + i * 0.7) % (2 * math.pi)
            cloud_dist = 20 + 25 * ((math.sin(t * 2 + i) + 1) / 2)
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 50 + math.sin(cloud_angle) * cloud_dist
            
            # 量子闪烁
            if (int(t * 15) + i) % 5 < 3:
                particle_alpha = int(200 * ((math.sin(t * 5 + i) + 1) / 2))
                pygame.draw.circle(s, (0, 200, 255, particle_alpha), (int(cloud_x), int(cloud_y)), 2)
        
        # 量子纠缠连线（随机连接粒子）
        entangle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            angle1 = (t * 3 + i) % (2 * math.pi)
            angle2 = (t * 3 + i + 3) % (2 * math.pi)
            dist1 = 30 + 15 * math.sin(t * 2 + i)
            dist2 = 30 + 15 * math.sin(t * 2 + i + 3)
            
            x1 = 60 + math.cos(angle1) * dist1
            y1 = 50 + math.sin(angle1) * dist1
            x2 = 60 + math.cos(angle2) * dist2
            y2 = 50 + math.sin(angle2) * dist2
            
            pygame.draw.line(entangle_surf, (0, 255, 255, 150), (int(x1), int(y1)), (int(x2), int(y2)), 1)
        s.blit(entangle_surf, (0, 0))
        
        # 审判光环
        for ring in range(3):
            ring_radius = 20 + ring * 12
            ring_alpha = int(180 - ring * 50)
            ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (0, 255, 255, ring_alpha), (60, 50), ring_radius, 2)
            s.blit(ring_surf, (0, 0))
        
        return s
    
    elif model_style == "arbiter_ex2":
        # 正义天秤 - 天秤平衡，律法之眼
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 天秤横杆
        pygame.draw.line(s, (255, 215, 0), (30, 40), (90, 40), 4)
        pygame.draw.circle(s, (255, 240, 100), (60, 40), 8)
        
        # 天秤支撑柱
        pygame.draw.line(s, (255, 215, 0), (60, 40), (60, 60), 4)
        
        # 左右秤盘（轻微倾斜表示审判）
        tilt = math.sin(t * 1.5) * 5
        # 左秤盘
        left_pan_y = 55 + tilt
        pygame.draw.line(s, (255, 230, 50), (30, 40), (35, int(left_pan_y)), 2)
        pygame.draw.ellipse(s, (255, 240, 100), (25, int(left_pan_y), 20, 8))
        # 右秤盘
        right_pan_y = 55 - tilt
        pygame.draw.line(s, (255, 230, 50), (90, 40), (85, int(right_pan_y)), 2)
        pygame.draw.ellipse(s, (255, 240, 100), (75, int(right_pan_y), 20, 8))
        
        # 律法之眼（悬浮在上方）
        eye_y = 25 + math.sin(t * 2) * 3
        pygame.draw.ellipse(s, (255, 215, 0), (50, int(eye_y), 20, 12))
        pygame.draw.circle(s, (255, 240, 100), (60, int(eye_y + 6)), 6)
        pygame.draw.circle(s, (100, 80, 0), (60, int(eye_y + 6)), 3)
        # 眼睛光芒
        eye_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(eye_surf, (255, 240, 100, 180), (60, int(eye_y + 6)), int(10 * pulse))
        s.blit(eye_surf, (0, 0))
        
        # 正义光柱（从眼睛向下）
        for beam in range(3):
            beam_x = 58 + beam
            pygame.draw.line(s, (255, 240, 100, 150), (beam_x, int(eye_y + 12)), (beam_x, 120), 2)
        
        # 审判之剑（悬浮在天秤上方）
        sword_x = 60 + math.sin(t * 2) * 10
        sword_points = [(sword_x, 15), (sword_x - 3, 25), (sword_x + 3, 25)]
        pygame.draw.polygon(s, (255, 215, 0), [(int(p[0]), p[1]) for p in sword_points])
        pygame.draw.line(s, (255, 230, 50), (int(sword_x), 25), (int(sword_x), 35), 3)
        
        return s
    
    elif model_style == "arbiter_ex3":
        # 真理之门 - 全知之眼
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.8) * 0.2 + 1
        
        # 中心全知之眼
        eye_radius = int(15 * pulse)
        # 眼白
        pygame.draw.circle(s, (255, 255, 255), (60, 50), eye_radius)
        # 虹膜（多层）
        iris_colors = [(100, 150, 255), (150, 200, 255), (200, 230, 255)]
        for iris_layer, iris_color in enumerate(iris_colors):
            iris_radius = int(eye_radius * 0.7 * ((3 - iris_layer) / 3))
            pygame.draw.circle(s, iris_color, (60, 50), iris_radius)
        # 瞳孔
        pupil_radius = int(eye_radius * 0.3)
        pygame.draw.circle(s, (0, 0, 0), (60, 50), pupil_radius)
        # 瞳孔反光
        pygame.draw.circle(s, (255, 255, 255), (62, 48), max(2, pupil_radius // 3))
        
        # 眼睹/边框
        pygame.draw.circle(s, (200, 180, 255), (60, 50), eye_radius, 2)
        
        # 真理之门框架（巨大门框）
        gate_width = 80
        gate_height = 100
        gate_left = 60 - gate_width // 2
        gate_top = 50 - gate_height // 2
        
        # 门框立柱
        left_pillar = pygame.Rect(gate_left - 5, gate_top, 5, gate_height)
        right_pillar = pygame.Rect(gate_left + gate_width, gate_top, 5, gate_height)
        pygame.draw.rect(s, (180, 160, 220), left_pillar)
        pygame.draw.rect(s, (180, 160, 220), right_pillar)
        pygame.draw.rect(s, (220, 200, 255), left_pillar, 1)
        pygame.draw.rect(s, (220, 200, 255), right_pillar, 1)
        
        # 门樽
        lintel = pygame.Rect(gate_left - 5, gate_top - 5, gate_width + 10, 5)
        pygame.draw.rect(s, (180, 160, 220), lintel)
        pygame.draw.rect(s, (220, 200, 255), lintel, 1)
        
        # 古代符文（在门框上）
        runes_on_gate = 12
        for rune_idx in range(runes_on_gate):
            rune_progress = rune_idx / runes_on_gate
            rune_brightness = int(150 + 105 * ((math.sin(t * 4 + rune_idx) + 1) / 2))
            
            if rune_idx < 6:  # 左柱
                rune_x = gate_left - 2
                rune_y = gate_top + int(gate_height * rune_progress)
            else:  # 右柱
                rune_x = gate_left + gate_width + 2
                rune_y = gate_top + int(gate_height * ((rune_idx - 6) / 6))
            
            # 简单符文形状（十字）
            rune_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(rune_surf, (rune_brightness, rune_brightness, 255),
                           (rune_x - 2, rune_y), (rune_x + 2, rune_y), 1)
            pygame.draw.line(rune_surf, (rune_brightness, rune_brightness, 255),
                           (rune_x, rune_y - 2), (rune_x, rune_y + 2), 1)
            s.blit(rune_surf, (0, 0))
        
        # 凝视射线（从眼睛射出）
        gaze_count = 16
        for gaze in range(gaze_count):
            gaze_angle = t * 2 + gaze * 2 * math.pi / gaze_count
            gaze_length = 35 + 10 * math.sin(t * 3 + gaze)
            gaze_ex = 60 + math.cos(gaze_angle) * gaze_length
            gaze_ey = 50 + math.sin(gaze_angle) * gaze_length
            
            gaze_alpha = int(150 * ((math.sin(t * 4 + gaze) + 1) / 2))
            if gaze_alpha > 50:
                gaze_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(gaze_surf, (200, 200, 255, gaze_alpha),
                               (60, 50), (int(gaze_ex), int(gaze_ey)), 1)
                s.blit(gaze_surf, (0, 0))
        
        # 知识粒子（环绕）
        for knowledge in range(20):
            know_angle = t * 1.5 + knowledge * 0.3
            know_dist = 25 + 15 * ((knowledge % 4) / 4)
            know_x = 60 + math.cos(know_angle) * know_dist
            know_y = 50 + math.sin(know_angle) * know_dist
            know_brightness = int(200 + 55 * math.sin(t * 5 + knowledge))
            
            # 书本/卷轴形状
            book_rect = pygame.Rect(int(know_x - 2), int(know_y - 3), 4, 6)
            pygame.draw.rect(s, (know_brightness, know_brightness, 255), book_rect)
            pygame.draw.line(s, (255, 255, 255), (int(know_x - 2), int(know_y)),
                           (int(know_x + 2), int(know_y)), 1)
        
        return s
    
    elif model_style == "arbiter_ex4":
        # 水墨丹青 - 墨滴扩散
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 墨滴扩散（从中心）
        ink_drops = 6
        for drop in range(ink_drops):
            drop_progress = ((t + drop * 0.3) % 1.5) / 1.5
            
            if drop_progress < 1:
                # 墨迹边缘（不规则）
                ink_points = []
                segments = 20
                for seg in range(segments):
                    seg_angle = seg * math.pi * 2 / segments
                    # 不规则边缘
                    radius_var = 1 + 0.3 * math.sin(seg * 2 + drop * 3)
                    ink_radius = drop_progress * 40 * radius_var
                    ix = 60 + int(math.cos(seg_angle) * ink_radius)
                    iy = 50 + int(math.sin(seg_angle) * ink_radius)
                    ink_points.append((ix, iy))
                
                # 墨色渐变（深到浅）
                ink_darkness = int(80 * (1 - drop_progress * 0.7))
                ink_alpha = int(200 * (1 - drop_progress))
                
                if ink_alpha > 20 and len(ink_points) > 2:
                    ink_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.polygon(ink_surf, (ink_darkness, ink_darkness, ink_darkness + 30, ink_alpha),
                                      ink_points)
                    s.blit(ink_surf, (0, 0))
        
        # 笔触（飘逸的线条）
        for stroke in range(4):
            stroke_angle = stroke * math.pi / 2 + t * 0.5
            stroke_points = []
            
            for seg in range(8):
                seg_prog = seg / 8
                seg_dist = 15 + seg_prog * 25
                seg_angle = stroke_angle + math.sin(t * 2 + seg) * 0.3
                sx = 60 + int(math.cos(seg_angle) * seg_dist)
                sy = 50 + int(math.sin(seg_angle) * seg_dist)
                stroke_points.append((sx, sy))
            
            # 绘制笔触
            for i in range(len(stroke_points) - 1):
                width = int(5 * (1 - i / len(stroke_points)))
                alpha = int(180 * (1 - i / len(stroke_points)))
                if alpha > 30:
                    stroke_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(stroke_surf, (50, 50, 80, alpha),
                                   stroke_points[i], stroke_points[i + 1], width)
                    s.blit(stroke_surf, (0, 0))
        
        return s
    
    elif model_style == "arbiter_ex5":  # 星座连线·黄道十二宫
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        constellation_idx = int(t / 3) % 4
        
        # 星座星星位置
        constellations = [
            [(0, -20), (12, -15), (-12, -10), (0, 5)],
            [(0, -15), (18, -10), (18, 8), (0, 15), (-18, 8), (-18, -10)],
            [(-12, -15), (12, -15), (12, 5), (-12, 5)],
            [(0, -18), (12, -8), (12, 8), (0, 18), (-12, 8), (-12, -8)],
        ]
        
        current_constellation = constellations[constellation_idx]
        
        # 绘制星星和连线
        for idx, (dx, dy) in enumerate(current_constellation):
            star_x = center[0] + dx
            star_y = center[1] + dy
            star_brightness = int(200 + 55 * math.sin(t * 3 + idx))
            pygame.draw.circle(plane_surf, (star_brightness, star_brightness, 200), 
                             (int(star_x), int(star_y)), 4)
            
            if idx > 0:
                prev_dx, prev_dy = current_constellation[idx - 1]
                pygame.draw.line(plane_surf, (200, 200, 255), 
                               (center[0] + prev_dx, center[1] + prev_dy),
                               (star_x, star_y), 2)
        
        # 星座符号环绕
        for i in range(12):
            symbol_angle = t * 0.5 + i * 0.524
            symbol_radius = 40
            sx = center[0] + math.cos(symbol_angle) * symbol_radius
            sy = center[1] + math.sin(symbol_angle) * symbol_radius
            symbol_color = (255, 255, 200) if i == constellation_idx else (150, 150, 150)
            pygame.draw.circle(plane_surf, symbol_color, (int(sx), int(sy)), 3)
        return plane_surf
    
    return None
