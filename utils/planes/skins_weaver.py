# Weaver 专属涂装渲染模块
# 包含: spider, web, silk, network, matrix

import pygame
import math

# Weaver涂装列表
WEAVER_STYLES = ["spider", "web", "silk", "network", "matrix", "weaver_ex", "weaver_ex2", "weaver_ex3", "weaver_ex4", "weaver_ex5"]

def is_weaver_style(model_style):
    """检查是否为Weaver涂装"""
    return model_style in WEAVER_STYLES

def render_weaver_skin(s, c, model_style, t, pid, static=False):
    """渲染Weaver涂装，返回Surface或None"""
    
    if model_style == "spider":
        # 蜘蛛之网·命运丝线 - 蜘蛛形态、蛛网编织、命运丝线、猎物困缚
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：蜘蛛身体（头胸部+腹部）
        spider_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 腹部（椭圆）
        pygame.draw.ellipse(spider_surface, (50, 0, 0, 240), (48, 55, 24, 18))
        pygame.draw.ellipse(spider_surface, (150, 50, 50, 220), (48, 55, 24, 18), 2)
        # 头胸部
        pygame.draw.circle(spider_surface, (50, 0, 0, 240), (60, 48), 10)
        pygame.draw.circle(spider_surface, (150, 50, 50, 220), (60, 48), 10, 2)
        s.blit(spider_surface, (0, 0))
        
        # 蜘蛛八脚（动态摆动）
        leg_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            leg_angle = i * math.pi / 4
            leg_swing = math.sin(t * 4 + i) * 0.3
            # 第一段腿
            leg1_angle = leg_angle + leg_swing
            leg1_x = 60 + math.cos(leg1_angle) * 18
            leg1_y = 50 + math.sin(leg1_angle) * 18
            pygame.draw.line(leg_surface, (100, 20, 20, 220), (60, 50), (int(leg1_x), int(leg1_y)), 3)
            # 第二段腿
            leg2_angle = leg1_angle + 0.5
            leg2_x = leg1_x + math.cos(leg2_angle) * 15
            leg2_y = leg1_y + math.sin(leg2_angle) * 15
            pygame.draw.line(leg_surface, (100, 20, 20, 220), (int(leg1_x), int(leg1_y)), 
                           (int(leg2_x), int(leg2_y)), 2)
        s.blit(leg_surface, (0, 0))
        
        # 命运丝线（从腹部喷出）
        silk_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            silk_angle = t * 2 + i * math.pi / 6
            silk_length = 20 + 15 * math.sin(t * 3 + i)
            silk_x = 60 + math.cos(silk_angle) * silk_length
            silk_y = 65 + math.sin(silk_angle) * silk_length
            pygame.draw.line(silk_surface, (220, 220, 220, 180), (60, 65), 
                           (int(silk_x), int(silk_y)), 1)
        s.blit(silk_surface, (0, 0))
        
        # 蛛网节点
        web_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            web_angle = i * math.pi / 4
            web_dist = 35 + 8 * math.sin(t * 2 + i)
            web_x = 60 + math.cos(web_angle) * web_dist
            web_y = 50 + math.sin(web_angle) * web_dist
            pygame.draw.circle(web_surface, (255, 255, 255, 200), (int(web_x), int(web_y)), 3)
        s.blit(web_surface, (0, 0))
        
        return s
    
    elif model_style == "web":
        # 虚空编织·命运之网 - 虚空蛛网、粘连粒子、困阵效果、命运编织
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心编织点
        center_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(center_surface, (200, 200, 200, 240), (60, 50), 12)
        pygame.draw.circle(center_surface, (255, 255, 255, 220), (60, 50), int(12 * pulse))
        s.blit(center_surface, (0, 0))
        
        # 主要蛛网丝线（放射状）
        web_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            web_angle = i * math.pi / 6 + t * 0.2
            web_length = 35 + 10 * math.sin(t * 2 + i)
            web_x = 60 + math.cos(web_angle) * web_length
            web_y = 50 + math.sin(web_angle) * web_length
            pygame.draw.line(web_surface, (220, 220, 220, 200), (60, 50), 
                           (int(web_x), int(web_y)), 2)
            # 末端节点
            pygame.draw.circle(web_surface, (255, 255, 255, 220), (int(web_x), int(web_y)), 4)
        s.blit(web_surface, (0, 0))
        
        # 环状蛛网（同心圆）
        ring_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            ring_radius = 15 + i * 10
            ring_alpha = int(180 - i * 40)
            pygame.draw.circle(ring_surface, (220, 220, 220, ring_alpha), (60, 50), ring_radius, 1)
        s.blit(ring_surface, (0, 0))
        
        # 粘连粒子（困住目标）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 3 + i * math.pi / 10
            particle_dist = 20 + 25 * (i / 20)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (255, 255, 255, 200), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        # 命运丝线连接（随机连接）
        connection_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            if (int(t * 5) + i) % 3 < 2:
                angle1 = i * math.pi / 4
                angle2 = (i + 2) * math.pi / 4
                x1 = 60 + math.cos(angle1) * 35
                y1 = 50 + math.sin(angle1) * 35
                x2 = 60 + math.cos(angle2) * 35
                y2 = 50 + math.sin(angle2) * 35
                pygame.draw.line(connection_surface, (240, 240, 240, 150), 
                               (int(x1), int(y1)), (int(x2), int(y2)), 1)
        s.blit(connection_surface, (0, 0))
        
        return s
    
    elif model_style == "silk":
        # 丝绸之路·空间织布 - 丝绸纹理、空间编织、柔韧丝线、万物连接
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：丝绸卷轴形态
        silk_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 卷轴中心
        pygame.draw.ellipse(silk_surface, (220, 220, 220, 240), (45, 40, 30, 20))
        pygame.draw.ellipse(silk_surface, (255, 255, 255, 220), (45, 40, 30, 20), 2)
        s.blit(silk_surface, (0, 0))
        
        # 丝线缠绕（螺旋）
        thread_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(30):
            thread_angle = t * 2 + i * 0.2
            thread_dist = 15 + (i / 30) * 25
            thread_x = 60 + math.cos(thread_angle) * thread_dist
            thread_y = 50 + math.sin(thread_angle) * thread_dist
            if i < 29:
                next_angle = t * 2 + (i + 1) * 0.2
                next_dist = 15 + ((i + 1) / 30) * 25
                next_x = 60 + math.cos(next_angle) * next_dist
                next_y = 50 + math.sin(next_angle) * next_dist
                pygame.draw.line(thread_surface, (240, 240, 240, 200), 
                               (int(thread_x), int(thread_y)), 
                               (int(next_x), int(next_y)), 2)
        s.blit(thread_surface, (0, 0))
        
        # 丝绸光泽（流动高光）
        sheen_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            sheen_angle = t * 3 + i * math.pi / 5
            sheen_dist = 20 + 15 * math.sin(t * 2 + i)
            sheen_x = 60 + math.cos(sheen_angle) * sheen_dist
            sheen_y = 50 + math.sin(sheen_angle) * sheen_dist
            sheen_size = 3 + 2 * math.sin(t * 4 + i)
            pygame.draw.circle(sheen_surface, (255, 255, 255, 220), 
                             (int(sheen_x), int(sheen_y)), int(sheen_size))
        s.blit(sheen_surface, (0, 0))
        
        # 柔韧波动（波浪纹）
        wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            wave_y = 30 + i * 8
            wave_points = []
            for j in range(15):
                wave_x = 20 + j * 7
                wave_offset_y = wave_y + 5 * math.sin(t * 3 + j * 0.5 + i)
                wave_points.append((wave_x, wave_offset_y))
            for j in range(len(wave_points) - 1):
                pygame.draw.line(wave_surface, (240, 240, 240, 180), 
                               (int(wave_points[j][0]), int(wave_points[j][1])),
                               (int(wave_points[j+1][0]), int(wave_points[j+1][1])), 2)
        s.blit(wave_surface, (0, 0))
        
        return s
    
    elif model_style == "network":
        # 网络编织·数据之网 - 数据网络、信息流动、网络节点、万物互联
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：中心服务器/路由器
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(core_surface, (0, 150, 255, 240), (50, 40, 20, 20))
        pygame.draw.rect(core_surface, (100, 200, 255, 220), (50, 40, 20, 20), 2)
        # 脉冲效果
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(core_glow, (0, 200, 255, int(150 * pulse)), 
                        (50 - int(5 * pulse), 40 - int(5 * pulse), 
                         20 + int(10 * pulse), 20 + int(10 * pulse)))
        s.blit(core_glow, (0, 0))
        s.blit(core_surface, (0, 0))
        
        # 网络节点（8个）
        node_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        nodes = []
        for i in range(8):
            node_angle = i * math.pi / 4 + t * 0.5
            node_dist = 35
            node_x = 60 + math.cos(node_angle) * node_dist
            node_y = 50 + math.sin(node_angle) * node_dist
            nodes.append((node_x, node_y))
            pygame.draw.circle(node_surface, (100, 200, 255, 240), (int(node_x), int(node_y)), 5)
            pygame.draw.circle(node_surface, (0, 150, 255, 220), (int(node_x), int(node_y)), 5, 1)
        s.blit(node_surface, (0, 0))
        
        # 数据连接线（从中心到节点）
        connection_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for node in nodes:
            pygame.draw.line(connection_surface, (50, 180, 255, 200), (60, 50), 
                           (int(node[0]), int(node[1])), 2)
        s.blit(connection_surface, (0, 0))
        
        # 数据包流动（沿连接线移动）
        packet_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            packet_progress = ((t * 2 + i * 0.5) % 2) / 2
            packet_x = 60 + (nodes[i][0] - 60) * packet_progress
            packet_y = 50 + (nodes[i][1] - 50) * packet_progress
            pygame.draw.circle(packet_surface, (0, 255, 255, 240), (int(packet_x), int(packet_y)), 3)
        s.blit(packet_surface, (0, 0))
        
        # 信息脉冲（扩散波）
        for i in range(3):
            pulse_radius = (t * 60 + i * 30) % 90
            pulse_alpha = int(200 * (1 - pulse_radius / 90))
            pulse_wave = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(pulse_wave, (0, 200, 255, pulse_alpha), (60, 50), int(pulse_radius), 2)
            s.blit(pulse_wave, (0, 0))
        
        return s
    
    elif model_style == "matrix":
        # 矩阵编织·代码之丝 - 矩阵代码、程序丝线、源代码、世界重写
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：矩阵核心
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_surface, (0, 255, 0, 250), (60, 50), 14)
        pygame.draw.circle(core_surface, (100, 255, 100, 230), (60, 50), int(14 * pulse))
        s.blit(core_surface, (0, 0))
        
        # 代码流（垂直下落的字符）
        code_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            code_x = 20 + i * 9
            # 每列代码的长度和位置不同
            code_length = 25 + int(15 * math.sin(t * 2 + i))
            code_y_start = ((t * 50 + i * 10) % 140) - 20
            # 绘制代码串（渐变）
            for j in range(int(code_length / 3)):
                char_y = code_y_start + j * 3
                if 0 <= char_y <= 120:
                    char_alpha = int(220 * (1 - j * 3 / code_length))
                    pygame.draw.rect(code_surface, (0, 255, 0, char_alpha), (code_x, int(char_y), 2, 2))
        s.blit(code_surface, (0, 0))
        
        # 矩阵网格（背景）
        grid_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(0, 120, 12):
            grid_alpha = int(80 + 60 * math.sin(t * 2 + i * 0.1))
            pygame.draw.line(grid_surface, (0, 200, 0, grid_alpha), (0, i), (120, i), 1)
            pygame.draw.line(grid_surface, (0, 200, 0, grid_alpha), (i, 0), (i, 120), 1)
        s.blit(grid_surface, (0, 0))
        
        # 程序节点（编织点）
        node_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            node_angle = t * 2 + i * math.pi / 4
            node_dist = 30 + 8 * math.sin(t * 2.5 + i)
            node_x = 60 + math.cos(node_angle) * node_dist
            node_y = 50 + math.sin(node_angle) * node_dist
            pygame.draw.circle(node_surface, (0, 255, 100, 240), (int(node_x), int(node_y)), 4)
            # 连接到中心
            pygame.draw.line(node_surface, (0, 255, 0, 180), (60, 50), 
                           (int(node_x), int(node_y)), 1)
        s.blit(node_surface, (0, 0))
        
        # 源代码脉冲
        pulse_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            pulse_radius = (t * 55 + i * 25) % 100
            pulse_alpha = int(200 * (1 - pulse_radius / 100))
            pygame.draw.circle(pulse_surface, (0, 255, 0, pulse_alpha), (60, 50), int(pulse_radius), 2)
        s.blit(pulse_surface, (0, 0))
        
        return s
    
    elif model_style == "weaver_ex":
        # 命运蛛网 - 辐射蛛网，节点闪烁
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心蜘蛛
        pygame.draw.circle(s, (255, 0, 255), (60, 50), int(12 * pulse))
        pygame.draw.circle(s, (255, 100, 255), (60, 50), int(12 * pulse), 2)
        
        # 8根主丝（辐射）
        web_nodes = []
        for i in range(8):
            main_angle = i * math.pi / 4
            
            # 每根主丝3个节点
            for node in range(1, 4):
                node_dist = 20 + node * 15
                node_x = 60 + math.cos(main_angle) * node_dist
                node_y = 50 + math.sin(main_angle) * node_dist
                web_nodes.append((int(node_x), int(node_y)))
                
                # 绘制到中心的丝线
                pygame.draw.line(s, (200, 0, 200), (60, 50), (int(node_x), int(node_y)), 2)
                
                # 节点
                node_size = 5 if (int(t * 8) + i + node) % 3 == 0 else 3
                pygame.draw.circle(s, (255, 150, 255), (int(node_x), int(node_y)), node_size)
        
        # 环形连接丝
        for ring in range(1, 4):
            ring_radius = 20 + ring * 15
            prev_point = None
            for i in range(9):  # 9个点形成闭环
                angle = i * math.pi / 4
                px = 60 + math.cos(angle) * ring_radius
                py = 50 + math.sin(angle) * ring_radius
                current_point = (int(px), int(py))
                
                if prev_point:
                    pygame.draw.line(s, (180, 0, 180), prev_point, current_point, 1)
                prev_point = current_point
        
        return s
    
    elif model_style == "weaver_ex2":
        # DNA螺旋 - 双螺旋结构，碱基对连接
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 双螺旋主链
        helix_points_1 = []
        helix_points_2 = []
        for i in range(20):
            y = 20 + i * 4
            angle1 = t * 2 + i * 0.4
            angle2 = angle1 + math.pi
            x1 = 60 + math.cos(angle1) * 20
            x2 = 60 + math.cos(angle2) * 20
            helix_points_1.append((int(x1), y))
            helix_points_2.append((int(x2), y))
        
        # 绘制螺旋线
        pygame.draw.lines(s, (0, 255, 150), False, helix_points_1, 3)
        pygame.draw.lines(s, (100, 255, 200), False, helix_points_2, 3)
        
        # 碱基对连接（横靠）
        for i in range(0, len(helix_points_1), 2):
            # 闪烁效果
            if (int(t * 10) + i) % 4 < 3:
                pygame.draw.line(s, (50, 255, 180), helix_points_1[i], helix_points_2[i], 2)
                # 碱基节点
                pygame.draw.circle(s, (0, 255, 150), helix_points_1[i], 4)
                pygame.draw.circle(s, (100, 255, 200), helix_points_2[i], 4)
        
        # 基因序列流动（发光粒子）
        for particle_idx in range(15):
            particle_progress = (t * 2 + particle_idx * 0.3) % 1
            particle_i = int(particle_progress * (len(helix_points_1) - 1))
            if particle_i < len(helix_points_1):
                px, py = helix_points_1[particle_i]
                particle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, (200, 255, 200, 220), (px, py), 6)
                s.blit(particle_surf, (0, 0))
        
        return s
    
    elif model_style == "weaver_ex3":
        # 神经网络 - 思维脉冲
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 神经元节点（多层网络）
        neurons = []
        layers = 4
        for layer in range(layers):
            neurons_in_layer = 5 + layer
            for neuron in range(neurons_in_layer):
                neuron_x = 20 + layer * 25
                neuron_y = 20 + (100 / (neurons_in_layer + 1)) * (neuron + 1)
                # 激活强度
                activation = (math.sin(t * 3 + layer * 0.5 + neuron * 0.3) + 1) / 2
                neurons.append((neuron_x, neuron_y, activation, layer))
        
        # 绘制神经连接（突触）
        synapse_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i, (x1, y1, act1, layer1) in enumerate(neurons):
            for j, (x2, y2, act2, layer2) in enumerate(neurons):
                # 只连接相邻层
                if layer2 == layer1 + 1:
                    # 连接强度
                    connection_strength = (act1 + act2) / 2
                    synapse_alpha = int(200 * connection_strength)
                    synapse_width = 1 + int(2 * connection_strength)
                    
                    # 脉冲传递动画
                    pulse_progress = (t * 2 + i * 0.1 + j * 0.1) % 1
                    pulse_x = x1 + (x2 - x1) * pulse_progress
                    pulse_y = y1 + (y2 - y1) * pulse_progress
                    
                    # 绘制连接线
                    pygame.draw.line(synapse_surf, (100, 200, 255, synapse_alpha),
                                   (int(x1), int(y1)), (int(x2), int(y2)), synapse_width)
                    
                    # 绘制脉冲点
                    pulse_size = int(3 * connection_strength)
                    if pulse_size > 0:
                        pygame.draw.circle(synapse_surf, (255, 255, 100),
                                         (int(pulse_x), int(pulse_y)), pulse_size)
        s.blit(synapse_surf, (0, 0))
        
        # 绘制神经元
        for neuron_x, neuron_y, activation, layer in neurons:
            neuron_size = int(5 + 5 * activation)
            neuron_brightness = int(150 + 105 * activation)
            
            # 神经元核心
            pygame.draw.circle(s, (neuron_brightness, neuron_brightness, 255), 
                             (int(neuron_x), int(neuron_y)), neuron_size)
            # 神经元外环
            pygame.draw.circle(s, (200, 200, 255), 
                             (int(neuron_x), int(neuron_y)), neuron_size + 2, 1)
            
            # 激活时发光
            if activation > 0.7:
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                glow_alpha = int(150 * (activation - 0.7) / 0.3)
                pygame.draw.circle(glow_surf, (255, 255, 200, glow_alpha),
                                 (int(neuron_x), int(neuron_y)), neuron_size + 5)
                s.blit(glow_surf, (0, 0))
        
        # 电信号波纹（全局思维活动）
        for signal_wave in range(3):
            wave_progress = (t * 1.5 + signal_wave * 0.5) % 1
            wave_x = 20 + wave_progress * 100
            wave_alpha = int(180 * (1 - abs(wave_progress - 0.5) * 2))
            
            if wave_alpha > 30:
                signal_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(signal_surf, (150, 200, 255, wave_alpha),
                               (int(wave_x), 10), (int(wave_x), 110), 2)
                s.blit(signal_surf, (0, 0))
        
        return s
    
    elif model_style == "weaver_ex4":
        # 波动艺术 - 声波可视化
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 波形（类似音频波形）
        waveforms = 4
        for wave in range(waveforms):
            wave_y_base = 30 + wave * 20
            wave_points = []
            
            for x in range(120):
                # 多重频率叠加
                y_offset = 0
                y_offset += 8 * math.sin((x / 10 + t * 3) * math.pi)
                y_offset += 4 * math.sin((x / 5 + t * 5) * math.pi * 2)
                y_offset += 2 * math.sin((x / 3 + t * 7) * math.pi * 3)
                
                y = int(wave_y_base + y_offset)
                wave_points.append((x, y))
            
            # 颜色渐变
            if wave == 0:
                wave_color = (100, 255, 150)
            elif wave == 1:
                wave_color = (255, 150, 100)
            elif wave == 2:
                wave_color = (150, 100, 255)
            else:
                wave_color = (255, 255, 100)
            
            if len(wave_points) > 1:
                wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(wave_surf, (*wave_color, 200), False, wave_points, 2)
                s.blit(wave_surf, (0, 0))
        
        # 频率指示器
        for freq_bar in range(10):
            bar_x = 20 + freq_bar * 10
            bar_height = int(20 + 20 * abs(math.sin(t * 4 + freq_bar * 0.5)))
            bar_rect = pygame.Rect(bar_x, 90 - bar_height, 6, bar_height)
            
            bar_color_val = int(100 + 155 * abs(math.sin(t * 3 + freq_bar)))
            pygame.draw.rect(s, (100, bar_color_val, 255), bar_rect)
        
        return s
    
    elif model_style == "weaver_ex5":  # 棋盘游戏·策略大师
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 棋盘格子
        board_size = 6
        cell_size = 10
        for row in range(board_size):
            for col in range(board_size):
                cell_x = center[0] - (board_size * cell_size) // 2 + col * cell_size
                cell_y = center[1] - (board_size * cell_size) // 2 + row * cell_size
                
                if (row + col) % 2 == 0:
                    cell_color = (220, 220, 220)
                else:
                    cell_color = (50, 50, 50)
                
                pygame.draw.rect(plane_surf, cell_color, (cell_x, cell_y, cell_size, cell_size))
        
        # 国际象棋棋子
        for i in range(8):
            piece_angle = t + i * 0.785
            piece_radius = 35
            piece_x = center[0] + math.cos(piece_angle) * piece_radius
            piece_y = center[1] + math.sin(piece_angle) * piece_radius
            
            piece_type = i % 4
            if piece_type == 0:
                pygame.draw.circle(plane_surf, (255, 215, 0), (int(piece_x), int(piece_y)), 4)
                pygame.draw.line(plane_surf, (255, 215, 0), (piece_x, piece_y - 6), (piece_x, piece_y - 2), 2)
            elif piece_type == 1:
                pygame.draw.circle(plane_surf, (192, 192, 192), (int(piece_x), int(piece_y)), 5)
            elif piece_type == 2:
                pygame.draw.rect(plane_surf, (139, 69, 19), (piece_x - 4, piece_y - 4, 8, 8))
            else:
                pygame.draw.circle(plane_surf, (150, 150, 150), (int(piece_x), int(piece_y)), 3)
        
        # 围棋棋子
        go_positions = [(0, -18), (18, 0), (0, 18), (-18, 0)]
        for idx, (dx, dy) in enumerate(go_positions):
            go_x = center[0] + dx
            go_y = center[1] + dy
            go_color = (0, 0, 0) if idx % 2 == 0 else (255, 255, 255)
            pygame.draw.circle(plane_surf, go_color, (int(go_x), int(go_y)), 5)
        return plane_surf
    
    return None
