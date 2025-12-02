"""
僚机涂装主题系统
包含8种独立的僚机涂装主题及其绘制函数
"""
import pygame
import math
import random

# ==============================================================================
#   僚机涂装主题配置
# ==============================================================================

WINGMAN_THEMES = {
    "default": {
        "name": "默认涂装",
        "desc": "僚机的标准配色",
        "cost": 0,
        "category": "default",
        "main_color": (150, 100, 200),
        "edge_color": (200, 150, 255),
        "glow_color": (100, 200, 255),
    },
    "quantum_ghost": {
        "name": "量子幽灵",
        "desc": "量子态僚机，半透明形态，带量子粒子效果",
        "cost": 1200,
        "category": "rare",
        "main_color": (150, 255, 255),
        "edge_color": (255, 150, 255),
        "glow_color": (200, 220, 255),
        "particle_effect": "quantum",
    },
    "lava_titan": {
        "name": "熔岩泰坦",
        "desc": "炽热的熔岩僚机，装甲裂痕流淌岩浆",
        "cost": 1200,
        "category": "rare",
        "main_color": (255, 80, 0),
        "edge_color": (255, 150, 0),
        "glow_color": (255, 200, 50),
        "particle_effect": "magma",
    },
    "aurora_valkyrie": {
        "name": "极光女武神",
        "desc": "极光能量环绕的战斗僚机",
        "cost": 1200,
        "category": "rare",
        "main_color": (100, 255, 200),
        "edge_color": (255, 100, 255),
        "glow_color": (150, 220, 255),
        "particle_effect": "aurora",
    },
    "shadow_reaper": {
        "name": "暗影收割者",
        "desc": "幽暗的暗影僚机，黑雾缭绕",
        "cost": 1500,
        "category": "epic",
        "main_color": (80, 80, 150),
        "edge_color": (150, 150, 200),
        "glow_color": (100, 100, 180),
        "particle_effect": "shadow",
    },
    "mech_swarm": {
        "name": "机械蜂群",
        "desc": "纳米机械装甲，机械零件环绕",
        "cost": 1500,
        "category": "epic",
        "main_color": (0, 255, 255),
        "edge_color": (255, 200, 0),
        "glow_color": (0, 220, 255),
        "particle_effect": "mech",
    },
    "nebula_dragoon": {
        "name": "星云龙骑",
        "desc": "星云能量构成的龙形僚机",
        "cost": 2000,
        "category": "legendary",
        "main_color": (150, 100, 255),
        "edge_color": (200, 150, 255),
        "glow_color": (180, 120, 255),
        "particle_effect": "nebula",
    },
    "time_rift": {
        "name": "时空裂痕",
        "desc": "扭曲时空的僚机，时空波纹扩散",
        "cost": 2000,
        "category": "legendary",
        "main_color": (200, 180, 255),
        "edge_color": (255, 220, 200),
        "glow_color": (220, 200, 240),
        "particle_effect": "time",
    },
}

# ==============================================================================
#   僚机绘制函数
# ==============================================================================

def draw_default_wingman(screen, x, y):
    """绘制默认涂装僚机"""
    t = pygame.time.get_ticks() / 1000.0
    pulse = abs(math.sin(t * 4))
    
    main_color = (150, 100, 200)
    edge_color = (200, 150, 255)
    glow_color = (100, 200, 255)
    
    # 机体主体
    body_points = [
        (x, y - 15),
        (x - 10, y + 10),
        (x + 10, y + 10),
    ]
    pygame.draw.polygon(screen, main_color, body_points)
    pygame.draw.polygon(screen, edge_color, body_points, 2)
    
    # 机翼
    pygame.draw.line(screen, edge_color, (x - 10, y), (x - 18, y + 5), 3)
    pygame.draw.line(screen, edge_color, (x + 10, y), (x + 18, y + 5), 3)
    
    # 脉动引擎光效
    glow_intensity = int(100 + 155 * pulse)
    glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*glow_color, glow_intensity), (15, 15), 10)
    screen.blit(glow_surf, (x - 15, y - 5))


def draw_quantum_ghost_wingman(screen, x, y):
    """绘制量子幽灵僚机"""
    t = pygame.time.get_ticks() / 1000.0
    pulse = abs(math.sin(t * 8))
    
    main_color = (150, 255, 255)
    edge_color = (255, 150, 255)
    glow_color = (200, 220, 255)
    
    # 量子态效果 - 半透明
    alpha = int(100 + 100 * pulse)
    
    # 创建半透明表面
    quantum_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    
    # 机体主体 - 三角形
    body_points = [
        (30, 15),
        (20, 45),
        (40, 45),
    ]
    pygame.draw.polygon(quantum_surf, (*main_color, alpha), body_points)
    pygame.draw.polygon(quantum_surf, (*edge_color, alpha + 50), body_points, 2)
    
    # 量子粒子效果
    for i in range(5):
        offset_x = random.randint(-15, 15)
        offset_y = random.randint(-15, 15)
        particle_alpha = int(50 + 50 * pulse)
        pygame.draw.circle(quantum_surf, (*glow_color, particle_alpha), 
                         (30 + offset_x, 30 + offset_y), 2)
    
    screen.blit(quantum_surf, (x - 30, y - 30))


def draw_lava_titan_wingman(screen, x, y):
    """绘制熔岩泰坦僚机"""
    t = pygame.time.get_ticks() / 1000.0
    pulse = abs(math.sin(t * 6))
    
    main_color = (255, 80, 0)
    edge_color = (255, 150, 0)
    glow_color = (255, 200, 50)
    
    # 机体主体 - 更宽厚
    body_points = [
        (x, y - 12),
        (x - 15, y + 12),
        (x + 15, y + 12),
    ]
    pygame.draw.polygon(screen, main_color, body_points)
    pygame.draw.polygon(screen, edge_color, body_points, 3)
    
    # 装甲板
    pygame.draw.rect(screen, edge_color, (x - 8, y - 5, 16, 8), 2)
    
    # 岩浆裂痕效果
    crack_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    lava_intensity = int(150 + 105 * pulse)
    
    # 绘制裂痕
    for i in range(3):
        start_x = 20 + random.randint(-5, 5)
        start_y = 10 + i * 5
        end_x = 20 + random.randint(-5, 5)
        end_y = start_y + random.randint(3, 8)
        pygame.draw.line(crack_surf, (*glow_color, lava_intensity), 
                        (start_x, start_y), (end_x, end_y), 2)
    
    screen.blit(crack_surf, (x - 20, y - 20))
    
    # 熔岩粒子
    for i in range(8):
        particle_x = x + random.randint(-10, 10)
        particle_y = y + random.randint(5, 15)
        particle_alpha = int(100 + 100 * pulse)
        particle_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*glow_color, particle_alpha), (2, 2), 2)
        screen.blit(particle_surf, (particle_x - 2, particle_y - 2))


def draw_aurora_valkyrie_wingman(screen, x, y):
    """绘制极光女武神僚机"""
    t = pygame.time.get_ticks() / 1000.0
    pulse = abs(math.sin(t * 5))
    
    # 极光色彩循环
    hue_shift = (t * 50) % 360
    main_color = (100, 255, 200)
    edge_color = (255, 100, 255)
    glow_color = (150, 220, 255)
    
    # 机体主体
    body_points = [
        (x, y - 15),
        (x - 12, y + 10),
        (x + 12, y + 10),
    ]
    pygame.draw.polygon(screen, main_color, body_points)
    pygame.draw.polygon(screen, edge_color, body_points, 2)
    
    # 极光能量环
    aurora_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
    for i in range(3):
        radius = 15 + i * 5
        alpha = int(50 + 50 * pulse - i * 15)
        color_offset = i * 40
        pygame.draw.circle(aurora_surf, (*glow_color, alpha), (25, 25), radius, 2)
    
    screen.blit(aurora_surf, (x - 25, y - 25))
    
    # 极光粒子舞蹈
    for i in range(6):
        angle = (t * 2 + i * math.pi / 3) % (2 * math.pi)
        particle_x = x + int(20 * math.cos(angle))
        particle_y = y + int(20 * math.sin(angle))
        particle_alpha = int(100 + 100 * pulse)
        particle_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*edge_color, particle_alpha), (3, 3), 3)
        screen.blit(particle_surf, (particle_x - 3, particle_y - 3))


def draw_shadow_reaper_wingman(screen, x, y):
    """绘制暗影收割者僚机"""
    t = pygame.time.get_ticks() / 1000.0
    pulse = abs(math.sin(t * 4))
    
    main_color = (80, 80, 150)
    edge_color = (150, 150, 200)
    glow_color = (100, 100, 180)
    
    # 暗影雾气
    shadow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
    shadow_alpha = int(80 + 80 * pulse)
    
    # 多层雾气
    for i in range(4):
        radius = 30 - i * 5
        alpha = shadow_alpha - i * 20
        pygame.draw.circle(shadow_surf, (*glow_color, max(0, alpha)), 
                         (40, 40), radius)
    
    screen.blit(shadow_surf, (x - 40, y - 40))
    
    # 机体主体 - 更锐利的形状
    body_points = [
        (x, y - 18),
        (x - 8, y),
        (x - 12, y + 12),
        (x + 12, y + 12),
        (x + 8, y),
    ]
    pygame.draw.polygon(screen, main_color, body_points)
    pygame.draw.polygon(screen, edge_color, body_points, 2)
    
    # 暗影分身效果
    for i in range(2):
        offset_x = random.randint(-8, 8)
        offset_y = random.randint(-8, 8)
        ghost_alpha = int(30 + 30 * pulse)
        ghost_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        ghost_points = [
            (20 + offset_x, 2),
            (12 + offset_x, 20),
            (28 + offset_x, 20),
        ]
        pygame.draw.polygon(ghost_surf, (*main_color, ghost_alpha), ghost_points)
        screen.blit(ghost_surf, (x - 20, y - 20))


def draw_mech_swarm_wingman(screen, x, y):
    """绘制机械蜂群僚机"""
    t = pygame.time.get_ticks() / 1000.0
    pulse = abs(math.sin(t * 6))
    
    main_color = (0, 255, 255)
    edge_color = (255, 200, 0)
    glow_color = (0, 220, 255)
    
    # 机体主体 - 机械感
    body_points = [
        (x, y - 12),
        (x - 10, y + 8),
        (x + 10, y + 8),
    ]
    pygame.draw.polygon(screen, main_color, body_points)
    pygame.draw.polygon(screen, edge_color, body_points, 3)
    
    # 纳米装甲板
    for i in range(3):
        armor_y = y - 8 + i * 6
        pygame.draw.line(screen, edge_color, (x - 8, armor_y), (x + 8, armor_y), 2)
    
    # 机械零件环绕
    for i in range(6):
        angle = (t * 3 + i * math.pi / 3) % (2 * math.pi)
        part_x = x + int(18 * math.cos(angle))
        part_y = y + int(18 * math.sin(angle))
        
        # 绘制小型机械部件
        pygame.draw.rect(screen, edge_color, (part_x - 2, part_y - 2, 4, 4))
        pygame.draw.circle(screen, glow_color, (part_x, part_y), 2, 1)
    
    # 能量脉冲
    pulse_intensity = int(100 + 155 * pulse)
    pulse_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(pulse_surf, (*glow_color, pulse_intensity), (15, 15), 8)
    screen.blit(pulse_surf, (x - 15, y - 5))


def draw_nebula_dragoon_wingman(screen, x, y):
    """绘制星云龙骑僚机"""
    t = pygame.time.get_ticks() / 1000.0
    pulse = abs(math.sin(t * 4))
    
    main_color = (150, 100, 255)
    edge_color = (200, 150, 255)
    glow_color = (180, 120, 255)
    
    # 星云效果
    nebula_surf = pygame.Surface((70, 70), pygame.SRCALPHA)
    nebula_alpha = int(60 + 60 * pulse)
    
    # 多层星云
    for i in range(5):
        radius = 25 - i * 4
        alpha = nebula_alpha - i * 10
        offset_x = int(5 * math.sin(t * 2 + i))
        offset_y = int(5 * math.cos(t * 2 + i))
        pygame.draw.circle(nebula_surf, (*glow_color, max(0, alpha)), 
                         (35 + offset_x, 35 + offset_y), radius)
    
    screen.blit(nebula_surf, (x - 35, y - 35))
    
    # 龙形机体
    body_points = [
        (x, y - 15),
        (x - 10, y),
        (x - 12, y + 12),
        (x, y + 8),
        (x + 12, y + 12),
        (x + 10, y),
    ]
    pygame.draw.polygon(screen, main_color, body_points)
    pygame.draw.polygon(screen, edge_color, body_points, 2)
    
    # 星云粒子
    for i in range(10):
        angle = (t + i * 0.6) % (2 * math.pi)
        dist = 20 + 10 * math.sin(t * 3 + i)
        particle_x = x + int(dist * math.cos(angle))
        particle_y = y + int(dist * math.sin(angle))
        particle_alpha = int(80 + 80 * pulse)
        particle_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*edge_color, particle_alpha), (2, 2), 2)
        screen.blit(particle_surf, (particle_x - 2, particle_y - 2))


def draw_time_rift_wingman(screen, x, y):
    """绘制时空裂痕僚机"""
    t = pygame.time.get_ticks() / 1000.0
    pulse = abs(math.sin(t * 5))
    
    main_color = (200, 180, 255)
    edge_color = (255, 220, 200)
    glow_color = (220, 200, 240)
    
    # 时空波纹扩散
    ripple_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
    for i in range(4):
        radius = int(15 + 20 * ((t * 2 + i * 0.5) % 1))
        alpha = int(150 - 150 * ((t * 2 + i * 0.5) % 1))
        pygame.draw.circle(ripple_surf, (*glow_color, max(0, alpha)), 
                         (50, 50), radius, 2)
    
    screen.blit(ripple_surf, (x - 50, y - 50))
    
    # 机体主体
    body_points = [
        (x, y - 15),
        (x - 12, y + 10),
        (x + 12, y + 10),
    ]
    pygame.draw.polygon(screen, main_color, body_points)
    pygame.draw.polygon(screen, edge_color, body_points, 2)
    
    # 时空扭曲效果 - 过去分身
    for i in range(3):
        ghost_offset = int(10 * (i + 1) * pulse)
        ghost_alpha = int(80 - i * 25)
        ghost_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        ghost_points = [
            (20, 5 - ghost_offset),
            (8, 25 - ghost_offset),
            (32, 25 - ghost_offset),
        ]
        pygame.draw.polygon(ghost_surf, (*main_color, ghost_alpha), ghost_points)
        screen.blit(ghost_surf, (x - 20, y - 20))
    
    # 时间粒子
    for i in range(8):
        angle = (t * 4 + i * math.pi / 4) % (2 * math.pi)
        particle_x = x + int(15 * math.cos(angle))
        particle_y = y + int(15 * math.sin(angle))
        particle_alpha = int(100 + 100 * pulse)
        particle_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*glow_color, particle_alpha), (1, 1), 1)
        screen.blit(particle_surf, (particle_x - 1, particle_y - 1))


# ==============================================================================
#   绘制函数映射表
# ==============================================================================

WINGMAN_DRAW_FUNCTIONS = {
    "default": draw_default_wingman,
    "quantum_ghost": draw_quantum_ghost_wingman,
    "lava_titan": draw_lava_titan_wingman,
    "aurora_valkyrie": draw_aurora_valkyrie_wingman,
    "shadow_reaper": draw_shadow_reaper_wingman,
    "mech_swarm": draw_mech_swarm_wingman,
    "nebula_dragoon": draw_nebula_dragoon_wingman,
    "time_rift": draw_time_rift_wingman,
}
