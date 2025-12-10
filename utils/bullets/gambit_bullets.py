# -*- coding: utf-8 -*-
"""
Gambit 战机子弹涂装效果渲染模块

包含以下子弹效果：
- card_spin/suit_change: 飞牌利刃弹
- random_roll/number_flash: 骰子乱数弹
- chip_scatter/value_glow: 筹码堆叠弹
- coin_toss/fate_decide: 金币翻转弹
- reel_spin/jackpot_chance: 老虎机转轮弹
- wheel_spin/color_bet: 轮盘赌球弹
- wild_card/chaos_laugh: 小丑王牌弹
"""
import pygame
import math


def render_gambit_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Gambit战机的子弹效果
    
    Args:
        surface: pygame绘图表面
        effects: 效果列表
        color: 主题颜色
        center_x, center_y: 中心坐标
        size: 子弹大小
        x, y: 左上角坐标
    
    Returns:
        bool: 如果渲染了效果返回True，否则False
    """
    
    if "card_spin" in effects or "suit_change" in effects:
        # 飞牌利刃弹：旋转扑克牌
        # 扑克牌轮廓
        card_w, card_h = size//2, size*2//3
        card_rect = (center_x - card_w//2, center_y - card_h//2, card_w, card_h)
        pygame.draw.rect(surface, (255, 255, 255), card_rect, border_radius=3)
        pygame.draw.rect(surface, color, card_rect, 2, border_radius=3)
        # 花色（动态切换）
        suit_phase = int(pygame.time.get_ticks() / 400) % 4
        suit_colors = [(0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0)]  # 黑桃红心梅花方片
        suit_color = suit_colors[suit_phase]
        # 简化花色符号
        if suit_phase == 0:  # 黑桃
            spade = [(center_x, center_y - size//8), (center_x - size//10, center_y + size//16), (center_x + size//10, center_y + size//16)]
            pygame.draw.polygon(surface, suit_color, spade)
            pygame.draw.circle(surface, suit_color, (center_x - size//16, center_y), size//20)
            pygame.draw.circle(surface, suit_color, (center_x + size//16, center_y), size//20)
        elif suit_phase == 1:  # 红心
            pygame.draw.circle(surface, suit_color, (center_x - size//16, center_y - size//16), size//16)
            pygame.draw.circle(surface, suit_color, (center_x + size//16, center_y - size//16), size//16)
            heart_tip = [(center_x, center_y + size//8), (center_x - size//8, center_y - size//16), (center_x + size//8, center_y - size//16)]
            pygame.draw.polygon(surface, suit_color, heart_tip)
        elif suit_phase == 2:  # 梅花
            pygame.draw.circle(surface, suit_color, (center_x, center_y - size//12), size//16)
            pygame.draw.circle(surface, suit_color, (center_x - size//12, center_y + size//24), size//16)
            pygame.draw.circle(surface, suit_color, (center_x + size//12, center_y + size//24), size//16)
        else:  # 方片
            diamond = [(center_x, center_y - size//8), (center_x + size//10, center_y), (center_x, center_y + size//8), (center_x - size//10, center_y)]
            pygame.draw.polygon(surface, suit_color, diamond)
        return True
    
    elif "random_roll" in effects or "number_flash" in effects:
        # 骰子乱数弹：滚动骰子
        # 骰子外框（立方体）
        dice_size = size // 2
        dice_rect = (center_x - dice_size//2, center_y - dice_size//2, dice_size, dice_size)
        pygame.draw.rect(surface, (255, 255, 255), dice_rect, border_radius=5)
        pygame.draw.rect(surface, color, dice_rect, 2, border_radius=5)
        # 点数（动态）
        dots_phase = int(pygame.time.get_ticks() / 300) % 6 + 1
        dot_positions = {
            1: [(0, 0)],
            2: [(-1, -1), (1, 1)],
            3: [(-1, -1), (0, 0), (1, 1)],
            4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
            5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
            6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]
        }
        dot_r = size // 18
        for dx, dy in dot_positions[dots_phase]:
            px = center_x + dx * dice_size // 4
            py = center_y + dy * dice_size // 4
            pygame.draw.circle(surface, (0, 0, 0), (px, py), dot_r)
        return True
    
    elif "chip_scatter" in effects or "value_glow" in effects:
        # 筹码堆叠弹：赌场筹码
        # 筹码堆（3层）
        chip_colors = [(255, 50, 50), (50, 100, 255), (255, 215, 0)]
        for i, chip_color in enumerate(chip_colors):
            chip_y = center_y + size//6 - i * size//8
            pygame.draw.ellipse(surface, chip_color, 
                              (center_x - size//3, chip_y - size//12, size*2//3, size//6))
            pygame.draw.ellipse(surface, (255, 255, 255), 
                              (center_x - size//3, chip_y - size//12, size*2//3, size//6), 2)
            # 筹码纹路
            pygame.draw.line(surface, (255, 255, 255), 
                           (center_x - size//4, chip_y), (center_x + size//4, chip_y), 1)
        # 金色光辉
        pygame.draw.circle(surface, (255, 255, 200), (center_x, center_y - size//8), size//10)
        return True
    
    elif "coin_toss" in effects or "fate_decide" in effects:
        # 金币翻转弹：翻转金币
        # 金币（椭圆模拟翻转）
        flip_phase = math.sin(pygame.time.get_ticks() / 200)
        coin_width = int(size//2 * abs(flip_phase) + size//10)
        pygame.draw.ellipse(surface, (255, 215, 0), 
                          (center_x - coin_width//2, center_y - size//4, coin_width, size//2))
        pygame.draw.ellipse(surface, (200, 150, 0), 
                          (center_x - coin_width//2, center_y - size//4, coin_width, size//2), 2)
        # 正反面标记
        if flip_phase > 0:
            # 正面：王冠
            pygame.draw.polygon(surface, (200, 150, 0), 
                              [(center_x, center_y - size//10), 
                               (center_x - size//10, center_y + size//16),
                               (center_x + size//10, center_y + size//16)])
        else:
            # 反面：数字
            pygame.draw.circle(surface, (200, 150, 0), (center_x, center_y), size//10, 2)
        # 闪光效果
        pygame.draw.circle(surface, (255, 255, 255), (center_x - size//8, center_y - size//8), size//20)
        return True
    
    elif "reel_spin" in effects or "jackpot_chance" in effects:
        # 老虎机转轮弹：老虎机图案
        # 老虎机框架
        frame_w, frame_h = size*2//3, size//2
        frame_rect = (center_x - frame_w//2, center_y - frame_h//2, frame_w, frame_h)
        pygame.draw.rect(surface, (100, 50, 50), frame_rect, border_radius=3)
        pygame.draw.rect(surface, (255, 215, 0), frame_rect, 3, border_radius=3)
        # 三个格子
        slot_w = frame_w // 3
        for i in range(3):
            slot_x = center_x - frame_w//2 + i * slot_w + slot_w//2
            slot_rect = (slot_x - slot_w//2 + 2, center_y - frame_h//2 + 3, slot_w - 4, frame_h - 6)
            pygame.draw.rect(surface, (255, 255, 255), slot_rect)
            # 符号（动态）
            symbol_phase = int(pygame.time.get_ticks() / 100 + i * 50) % 3
            symbol_colors = [(255, 0, 0), (255, 215, 0), (0, 200, 0)]  # 樱桃、7、BAR
            pygame.draw.circle(surface, symbol_colors[symbol_phase], (slot_x, center_y), size//12)
        return True
    
    elif "wheel_spin" in effects or "color_bet" in effects:
        # 轮盘赌球弹：轮盘+小球
        # 轮盘
        pygame.draw.circle(surface, (50, 100, 50), (center_x, center_y), int(size//2.5))
        pygame.draw.circle(surface, (200, 150, 50), (center_x, center_y), int(size//2.5), 3)
        # 红黑格子
        for i in range(12):
            angle = i * 30 * 3.14159 / 180
            slot_color = (255, 0, 0) if i % 2 == 0 else (0, 0, 0)
            x1 = center_x + int(size//4 * math.cos(angle))
            y1 = center_y + int(size//4 * math.sin(angle))
            x2 = center_x + int(size//2.5 * math.cos(angle))
            y2 = center_y + int(size//2.5 * math.sin(angle))
            pygame.draw.line(surface, slot_color, (x1, y1), (x2, y2), 4)
        # 旋转小球
        ball_angle = (pygame.time.get_ticks() / 100) * 3.14159 / 180
        ball_x = center_x + int(size//3 * math.cos(ball_angle))
        ball_y = center_y + int(size//3 * math.sin(ball_angle))
        pygame.draw.circle(surface, (200, 200, 200), (ball_x, ball_y), size//15)
        pygame.draw.circle(surface, (255, 255, 255), (ball_x, ball_y), size//15, 1)
        return True
    
    elif "wild_card" in effects or "chaos_laugh" in effects:
        # 小丑王牌弹：小丑面具
        # 小丑脸轮廓
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//3)
        pygame.draw.circle(surface, color, (center_x, center_y), size//3, 2)
        # 眼睛（菱形）
        eye_y = center_y - size//10
        for dx in [-size//8, size//8]:
            eye_points = [(center_x + dx, eye_y - size//15), 
                         (center_x + dx + size//20, eye_y),
                         (center_x + dx, eye_y + size//15), 
                         (center_x + dx - size//20, eye_y)]
            pygame.draw.polygon(surface, (0, 0, 0), eye_points)
        # 疯狂笑容（弧形）
        smile_rect = (center_x - size//5, center_y, size*2//5, size//4)
        pygame.draw.arc(surface, (255, 0, 0), smile_rect, 3.14159, 6.28318, 3)
        # 小丑帽尖
        hat_points = [(center_x, int(center_y - size//2.5)), 
                     (center_x - size//6, center_y - size//4),
                     (center_x + size//6, center_y - size//4)]
        pygame.draw.polygon(surface, (255, 100, 150), hat_points)
        pygame.draw.polygon(surface, (255, 215, 0), hat_points, 2)
        # 铃铛
        pygame.draw.circle(surface, (255, 215, 0), (center_x, int(center_y - size//2.5)), size//18)
        return True
    
    return False
