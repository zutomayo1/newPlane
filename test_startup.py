#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试游戏启动逻辑，检查 reset_game() 是否工作正常
"""

import sys
import traceback

log_info("[TEST] 导入模块...")
try:
    from config import *
    from utils import *
    from systems import *
    from sprites import *
    from roguelite import *
    log_info("[OK] 所有模块导入成功")
except Exception as e:
    log_error(f"模块导入失败: {e}")
    traceback.print_exc()
    sys.exit(1)

# 初始化全局变量
log_info("[TEST] 初始化全局变量...")
player = None
boss = None
score = 0
combo_count = 0
combo_timer = 0
boss_warning_timer = 0
next_boss_score = 5000
global_time_freeze = 0
wave = 0
upgrade_options = []
upgrade_selected = 0
levelup_ready = False
frozen_screen = None
is_paused = False
selected_plane = "striker"

def reset_game():
    global player, boss, score, combo_count, combo_timer
    global boss_warning_timer, next_boss_score, global_time_freeze, is_paused
    global upgrade_options, upgrade_selected, levelup_ready, frozen_screen, wave
    
    log_debug("reset_game() 开始")
    
    is_paused = False 
    frozen_screen = None
    upgrade_options = []
    upgrade_selected = 0
    levelup_ready = False
    
    all_sprites.empty()
    mobs.empty()
    bullets.empty()
    enemy_bullets.empty()
    powerups.empty()
    supplies.empty()
    
    score = 0
    combo_count = 0
    combo_timer = 0
    boss_warning_timer = 0
    next_boss_score = 5000
    global_time_freeze = 0
    wave = 0
    boss = None
    
    log_debug(f"准备创建 Player，selected_plane={selected_plane}")
    player = Player(selected_plane)
    log_debug("Player 创建完成")
    
    # 初始化肉鸽系统
    log_debug("初始化肉鸽系统...")
    player.init_roguelite_systems()
    log_debug("肉鸽系统初始化完成")
    
    all_sprites.add(player)
    log_debug("Player 已添加到 all_sprites")
    
    log_debug("reset_game() 完成")

# 测试 Player 创建
log_info("\n[TEST] 尝试创建 Player...")
try:
    reset_game()
    log_info("[OK] reset_game() 执行成功！")
    log_info(f"player = {player}")
    log_info(f"player.upgrade_manager = {player.upgrade_manager}")
except Exception as e:
    log_error(f"reset_game() 失败: {e}")
    traceback.print_exc()
    sys.exit(1)

log_info("\n[TEST] 所有测试完成！")
