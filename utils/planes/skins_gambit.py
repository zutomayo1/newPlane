# Gambit 专属涂装渲染模块
# 包含: gambit_vegas, gambit_tarot, gambit_mahjong, gambit_lottery,
#       gambit_blackjack, gambit_russian_roulette, gambit_horseshoe, gambit_casino_royale,
#       gambit_pachinko, gambit_fortune_cookie, gambit_probability, gambit_joker

import pygame
import math
import random

# Gambit涂装列表
GAMBIT_STYLES = [
    "gambit_vegas", "gambit_tarot", "gambit_mahjong", "gambit_lottery",
    "gambit_blackjack", "gambit_russian_roulette", "gambit_horseshoe", "gambit_casino_royale",
    "gambit_pachinko", "gambit_fortune_cookie", "gambit_probability", "gambit_joker"
]

def is_gambit_style(model_style):
    """检查是否为Gambit涂装"""
    return model_style in GAMBIT_STYLES

def render_gambit_skin(s, c, model_style, t, pid, static=False):
    """渲染Gambit涂装，返回Surface或None"""
    pulse = math.sin(t * 2) * 0.15 + 1
    
    if model_style == "gambit_vegas":
        # 拉斯维加斯·霓虹罪城 - 霓虹灯老虎机
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 霓虹边框闪烁
        neon_phase = int(t * 10) % 3
        neon_colors = [(255, 50, 50), (50, 255, 50), (255, 215, 0)]
        pygame.draw.rect(s, neon_colors[neon_phase], (15, 15, 90, 90), 4, border_radius=10)
        # 3个老虎机转轮
        for reel_i in range(3):
            reel_x = 30 + reel_i * 25
            reel_y = 50 + int(5 * math.sin(t * 8 + reel_i * 2))
            pygame.draw.rect(s, (50, 50, 50), (reel_x - 8, reel_y - 12, 20, 24), border_radius=3)
            pygame.draw.rect(s, (255, 215, 0), (reel_x - 8, reel_y - 12, 20, 24), 2, border_radius=3)
            # 符号（用圆圈代替）
            symbol_color = [(255, 215, 0), (255, 50, 50), (100, 200, 255)][reel_i]
            pygame.draw.circle(s, symbol_color, (reel_x + 2, reel_y), 6)
        # 金币雨
        for coin_i in range(15):
            coin_y = (t * 100 + coin_i * 20) % 120
            coin_x = 20 + (coin_i * 7) % 80
            pygame.draw.circle(s, (255, 215, 0), (int(coin_x), int(coin_y)), 4)
            pygame.draw.circle(s, (230, 190, 0), (int(coin_x), int(coin_y)), 4, 1)
        # JACKPOT文字位置（用金色条代替）
        pygame.draw.rect(s, (255, 215, 0), (25, 85, 70, 10), border_radius=2)
        return s
        
    elif model_style == "gambit_tarot":
        # 塔罗牌阵·命运占卜 - 神秘塔罗牌
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 22张大阿尔卡纳牌阵（环绕）
        for card_i in range(22):
            card_angle = (card_i * 16.36 + t * 5) * 0.01745
            card_r = 38
            card_x = 60 + math.cos(card_angle) * card_r
            card_y = 60 + math.sin(card_angle) * card_r
            # 牌面
            pygame.draw.rect(s, (180, 100, 200), (int(card_x) - 5, int(card_y) - 7, 10, 14))
            pygame.draw.rect(s, (200, 120, 220), (int(card_x) - 5, int(card_y) - 7, 10, 14), 1)
            # 神秘符号
            pygame.draw.circle(s, (255, 200, 255), (int(card_x), int(card_y)), 3)
        # 中心命运之轮
        pygame.draw.circle(s, (180, 100, 200), (60, 60), 20, 3)
        for spoke in range(8):
            spoke_angle = (spoke * 45 + t * 15) * 0.01745
            sx = 60 + math.cos(spoke_angle) * 18
            sy = 60 + math.sin(spoke_angle) * 18
            pygame.draw.line(s, (200, 120, 220), (60, 60), (sx, sy), 2)
        pygame.draw.circle(s, (255, 200, 255), (60, 60), 8)
        return s

    elif model_style == "gambit_mahjong":
        # 麻将国士·东风起势 - 麻将牌
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 13张国士无双牌阵
        for tile_i in range(13):
            tile_angle = (tile_i * 27.7 + t * 8) * 0.01745
            tile_r = 38
            tile_x = 60 + math.cos(tile_angle) * tile_r
            tile_y = 60 + math.sin(tile_angle) * tile_r
            # 麻将牌（白色底）
            pygame.draw.rect(s, (255, 255, 240), (int(tile_x) - 6, int(tile_y) - 8, 12, 16), border_radius=2)
            pygame.draw.rect(s, (0, 150, 100), (int(tile_x) - 6, int(tile_y) - 8, 12, 16), 1, border_radius=2)
            # 牌面花纹
            tile_color = (255, 0, 0) if tile_i < 7 else (0, 100, 0)
            pygame.draw.circle(s, tile_color, (int(tile_x), int(tile_y)), 3)
        # 中心（胡牌！）
        pygame.draw.circle(s, (0, 150, 100), (60, 60), 18)
        pygame.draw.circle(s, (50, 180, 130), (60, 60), 14)
        pygame.draw.circle(s, (255, 255, 240), (60, 60), 8)
        return s

    elif model_style == "gambit_lottery":
        # 彩票头奖·亿万梦想 - 彩票号码球
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 20个号码球（环绕）
        for ball_i in range(20):
            ball_angle = (ball_i * 18 + t * 15) * 0.01745
            ball_r = 30 + int(8 * math.sin(t * 3 + ball_i))
            ball_x = 60 + math.cos(ball_angle) * ball_r
            ball_y = 60 + math.sin(ball_angle) * ball_r
            # 彩球颜色
            ball_colors = [(255, 100, 100), (255, 200, 100), (100, 255, 100),
                          (100, 200, 255), (200, 100, 255)]
            ball_color = ball_colors[ball_i % 5]
            pygame.draw.circle(s, ball_color, (int(ball_x), int(ball_y)), 6)
            pygame.draw.circle(s, (255, 255, 255), (int(ball_x) - 2, int(ball_y) - 2), 2)
        # 头奖光环
        jackpot_pulse = abs(math.sin(t * 5))
        pygame.draw.circle(s, (255, 215, 0, int(150 * jackpot_pulse)), (60, 60), 25, 4)
        # 中心大奖球
        pygame.draw.circle(s, (255, 50, 50), (60, 60), 15)
        pygame.draw.circle(s, (255, 150, 150), (60, 60), 10)
        pygame.draw.circle(s, (255, 255, 255), (55, 55), 4)
        return s

    elif model_style == "gambit_blackjack":
        # 二十一点·黑杰克王 - 绿色赌桌
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 绿色赌桌
        pygame.draw.ellipse(s, (0, 100, 50), (15, 25, 90, 70))
        pygame.draw.ellipse(s, (50, 150, 100), (15, 25, 90, 70), 3)
        # 筹码堆（3堆）
        chip_colors = [(255, 50, 50), (50, 50, 255), (50, 50, 50)]
        for stack_i in range(3):
            stack_x = 35 + stack_i * 25
            for chip in range(4):
                chip_y = 75 - chip * 3
                pygame.draw.ellipse(s, chip_colors[stack_i], (stack_x - 6, chip_y - 2, 12, 4))
        # A和K牌
        pygame.draw.rect(s, (255, 255, 255), (40, 35, 16, 22), border_radius=2)
        pygame.draw.circle(s, (50, 50, 50), (48, 46), 5)  # 黑桃
        pygame.draw.rect(s, (255, 255, 255), (64, 35, 16, 22), border_radius=2)
        pygame.draw.circle(s, (255, 50, 50), (72, 46), 5)  # 红心
        # 21点标记
        pygame.draw.circle(s, (255, 215, 0), (60, 20), 10)
        return s

    elif model_style == "gambit_russian_roulette":
        # 俄罗斯轮盘·致命赌注 - 左轮手枪
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 弹巢（6个孔）
        cylinder_rotation = t * 30
        pygame.draw.circle(s, (150, 150, 150), (60, 60), 30)
        pygame.draw.circle(s, (120, 120, 120), (60, 60), 25)
        for chamber_i in range(6):
            chamber_angle = (chamber_i * 60 + cylinder_rotation) * 0.01745
            chamber_x = 60 + math.cos(chamber_angle) * 18
            chamber_y = 60 + math.sin(chamber_angle) * 18
            # 空弹巢
            pygame.draw.circle(s, (80, 80, 80), (int(chamber_x), int(chamber_y)), 6)
            # 子弹（只有1个）
            if chamber_i == 0:
                pygame.draw.circle(s, (255, 215, 0), (int(chamber_x), int(chamber_y)), 4)
        # 枪管
        pygame.draw.rect(s, (100, 100, 100), (60, 30, 8, 20))
        # 扳机
        pygame.draw.rect(s, (80, 80, 80), (55, 85, 10, 15), border_radius=2)
        # 危险警告
        warning_flash = int(t * 5) % 2
        if warning_flash:
            pygame.draw.circle(s, (255, 0, 0, 100), (60, 60), 35, 3)
        return s

    elif model_style == "gambit_horseshoe":
        # 四叶幸运草·幸运护符 - 幸运符号组合
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 24片四叶草叶子
        for clover_i in range(24):
            clover_angle = (clover_i * 15 + t * 10) * 0.01745
            clover_r = 35
            clover_x = 60 + math.cos(clover_angle) * clover_r
            clover_y = 60 + math.sin(clover_angle) * clover_r
            # 心形叶子
            pygame.draw.circle(s, (100, 200, 100), (int(clover_x), int(clover_y)), 5)
        # 马蹄铁
        horseshoe_pts = []
        for hs_i in range(12):
            hs_angle = (hs_i * 15 - 75) * 0.01745
            hs_x = 60 + math.cos(hs_angle) * 22
            hs_y = 55 + math.sin(hs_angle) * 22
            horseshoe_pts.append((int(hs_x), int(hs_y)))
        if len(horseshoe_pts) > 1:
            pygame.draw.lines(s, (255, 215, 0), False, horseshoe_pts, 5)
        # 幸运闪光
        sparkle_phase = t * 8
        for sparkle_i in range(8):
            if int(sparkle_phase + sparkle_i) % 4 == 0:
                sp_angle = (sparkle_i * 45) * 0.01745
                sp_x = 60 + math.cos(sp_angle) * 45
                sp_y = 60 + math.sin(sp_angle) * 45
                pygame.draw.circle(s, (255, 255, 200), (int(sp_x), int(sp_y)), 3)
        # 中心四叶草
        for leaf in range(4):
            leaf_angle = (leaf * 90 + 45) * 0.01745
            leaf_x = 60 + math.cos(leaf_angle) * 8
            leaf_y = 60 + math.sin(leaf_angle) * 8
            pygame.draw.circle(s, (130, 220, 130), (int(leaf_x), int(leaf_y)), 6)
        pygame.draw.circle(s, (100, 180, 100), (60, 60), 4)
        return s

    elif model_style == "gambit_casino_royale":
        # 皇家赌场·007特工 - 优雅黑金风格
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 黑色背景
        pygame.draw.circle(s, (20, 20, 20), (60, 60), 45)
        pygame.draw.circle(s, (50, 50, 50), (60, 60), 45, 2)
        # 金色装饰边
        pygame.draw.circle(s, (255, 215, 0), (60, 60), 42, 1)
        # 007风格枪管视角
        for ring in range(5):
            ring_r = 10 + ring * 7
            pygame.draw.circle(s, (50, 50, 50), (60, 60), ring_r, 1)
        # 马提尼杯
        pygame.draw.polygon(s, (200, 200, 200), [(50, 75), (60, 55), (70, 75)])
        pygame.draw.line(s, (200, 200, 200), (60, 75), (60, 90), 2)
        pygame.draw.line(s, (200, 200, 200), (52, 90), (68, 90), 2)
        # 橄榄
        pygame.draw.circle(s, (100, 150, 50), (60, 65), 3)
        # 扑克牌角落
        pygame.draw.rect(s, (255, 255, 255), (80, 20, 20, 28), border_radius=2)
        pygame.draw.circle(s, (255, 50, 50), (90, 34), 4)  # 红心A
        return s

    elif model_style == "gambit_pachinko":
        # 弹珠柏青哥·银色瀑布 - 柏青哥机台
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 钉板网格
        for pin_row in range(8):
            for pin_col in range(6):
                offset = 5 if pin_row % 2 == 0 else 0
                pin_x = 20 + pin_col * 15 + offset
                pin_y = 15 + pin_row * 12
                pygame.draw.circle(s, (200, 200, 200), (pin_x, pin_y), 2)
        # 30个银色弹珠（瀑布效果）
        for ball_i in range(30):
            ball_progress = (t * 3 + ball_i * 0.1) % 1.0
            ball_x = 30 + (ball_i * 3) % 60 + int(5 * math.sin(ball_progress * 10 + ball_i))
            ball_y = int(ball_progress * 100) + 10
            if ball_y < 110:
                pygame.draw.circle(s, (220, 220, 255), (ball_x, ball_y), 3)
                pygame.draw.circle(s, (255, 255, 255), (ball_x - 1, ball_y - 1), 1)
        # 入球口
        pygame.draw.rect(s, (255, 50, 50), (45, 95, 30, 15), border_radius=3)
        pygame.draw.rect(s, (255, 215, 0), (45, 95, 30, 15), 2, border_radius=3)
        return s

    elif model_style == "gambit_fortune_cookie":
        # 幸运饼签·命运甜点 - 幸运饼干
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 12个饼干碎片
        for cookie_i in range(12):
            cookie_angle = (cookie_i * 30 + t * 8) * 0.01745
            cookie_r = 35
            cookie_x = 60 + math.cos(cookie_angle) * cookie_r
            cookie_y = 60 + math.sin(cookie_angle) * cookie_r
            # 饼干弧形碎片
            pygame.draw.arc(s, (255, 200, 100), 
                          (int(cookie_x) - 8, int(cookie_y) - 8, 16, 16),
                          cookie_angle, cookie_angle + 1, 4)
        # 中心完整饼干
        pygame.draw.circle(s, (255, 200, 100), (60, 60), 18)
        pygame.draw.arc(s, (230, 180, 80), (42, 42, 36, 36), 0.5, 2.5, 3)
        # 签纸飘出
        paper_wave = math.sin(t * 3) * 5
        pygame.draw.rect(s, (255, 255, 240), (50 + paper_wave, 55, 20, 8))
        pygame.draw.line(s, (200, 50, 50), (52 + paper_wave, 59), (68 + paper_wave, 59), 1)
        # 幸运光芒
        for ray_i in range(8):
            ray_angle = (ray_i * 45 + t * 20) * 0.01745
            ray_x = 60 + math.cos(ray_angle) * 48
            ray_y = 60 + math.sin(ray_angle) * 48
            pygame.draw.line(s, (255, 220, 130), (60, 60), (ray_x, ray_y), 1)
        return s

    elif model_style == "gambit_probability":
        # 概率云图·量子赌博 - 概率波函数
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 波函数可视化
        for x in range(20, 100, 3):
            # 高斯分布曲线
            gaussian = math.exp(-((x - 60) ** 2) / 400)
            wave_y = 60 - int(gaussian * 30 * abs(math.sin(t * 3 + x * 0.1)))
            pygame.draw.circle(s, (100, 200, 255), (x, wave_y), 2)
            # 概率分布点
            pygame.draw.line(s, (100, 200, 255, 100), (x, 60), (x, wave_y), 1)
        # 3个叠加态（薛定谔）
        for state_i in range(3):
            state_angle = (state_i * 120 + t * 15) * 0.01745
            state_r = 25
            state_x = 60 + math.cos(state_angle) * state_r
            state_y = 60 + math.sin(state_angle) * state_r
            # 模糊态（半透明）
            pygame.draw.circle(s, (130, 220, 255, 150), (int(state_x), int(state_y)), 10)
            pygame.draw.circle(s, (100, 200, 255), (int(state_x), int(state_y)), 10, 2)
        # 中心观测点
        pygame.draw.circle(s, (255, 255, 255), (60, 60), 8)
        pygame.draw.circle(s, (100, 200, 255), (60, 60), 8, 2)
        # 不确定性符号
        pygame.draw.circle(s, (80, 180, 240), (60, 60), 35, 1)
        return s

    elif model_style == "gambit_joker":
        # 小丑王牌·混沌之笑 - 疯狂小丑
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 小丑帽（三尖）
        hat_colors = [(255, 50, 100), (100, 255, 150), (255, 255, 100)]
        for tip_i in range(3):
            tip_angle = (tip_i * 120 - 90 + math.sin(t * 5) * 10) * 0.01745
            tip_x = 60 + math.cos(tip_angle) * 30
            tip_y = 45 + math.sin(tip_angle) * 20
            pygame.draw.polygon(s, hat_colors[tip_i], 
                              [(60, 50), (tip_x - 5, tip_y), (tip_x + 5, tip_y)])
            # 铃铛
            pygame.draw.circle(s, (255, 215, 0), (int(tip_x), int(tip_y) - 5), 4)
        # 脸
        pygame.draw.circle(s, (255, 255, 255), (60, 60), 20)
        # 疯狂笑容
        smile_width = 12 + int(3 * math.sin(t * 8))
        pygame.draw.arc(s, (255, 50, 100), (48, 55, smile_width * 2, 15), 3.14, 0, 3)
        # 眼睛（不对称）
        pygame.draw.circle(s, (50, 50, 50), (52, 55), 4)
        pygame.draw.circle(s, (50, 50, 50), (68, 58), 5)  # 一大一小
        # 红鼻子
        pygame.draw.circle(s, (255, 50, 50), (60, 62), 5)
        # 混沌粒子
        for chaos_i in range(16):
            chaos_angle = (chaos_i * 22.5 + t * 30) * 0.01745
            chaos_r = 40 + int(5 * math.sin(t * 5 + chaos_i))
            chaos_x = 60 + math.cos(chaos_angle) * chaos_r
            chaos_y = 60 + math.sin(chaos_angle) * chaos_r
            chaos_color = hat_colors[chaos_i % 3]
            pygame.draw.circle(s, chaos_color, (int(chaos_x), int(chaos_y)), 3)
        return s
    
    return None
