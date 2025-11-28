#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断追踪卡牌系统问题"""

import sys
sys.path.insert(0, '/c/Users/真夜中/Desktop/newPlane')

try:
    import pygame
    pygame.init()
    
    from config import PLANES
    from sprites import Player
    from roguelite import apply_buff_to_player, BUFF_LIBRARY
    
    print("=== 追踪卡牌诊断系统 ===\n")
    
    # 测试1: 检查卡牌定义
    print("1. 追踪卡牌定义检查:")
    if "homing" in BUFF_LIBRARY:
        buff = BUFF_LIBRARY["homing"]
        print(f"  OK: 卡牌存在: {buff['name']}")
        print(f"  描述: {buff['desc']}")
        print(f"  稀有度: {buff['rarity']}")
        print(f"  类型: {buff['type']}")
    else:
        print("  ERROR: 追踪卡牌未找到!")
        sys.exit(1)
    
    # 测试2: Player初始化
    print("\n2. Player初始化检查:")
    selected_plane = "striker"
    player = Player(selected_plane)
    print(f"  OK: Player创建成功")
    print(f"  初始 homing_level: {player.homing_level}")
    print(f"  类型: {type(player.homing_level)}")
    
    # 测试3: 应用卡牌
    print("\n3. 应用追踪卡牌:")
    print(f"  应用前: homing_level = {player.homing_level}")
    apply_buff_to_player(player, "homing")
    print(f"  应用后: homing_level = {player.homing_level}")
    
    if player.homing_level > 0:
        print(f"  OK: 卡牌应用成功")
    else:
        print(f"  ERROR: 卡牌应用失败!")
        sys.exit(1)
    
    # 测试4: 多次应用
    print("\n4. 多次应用卡牌:")
    for i in range(3):
        apply_buff_to_player(player, "homing")
        print(f"  应用 #{i+2}: homing_level = {player.homing_level}")
    
    # 测试5: 子弹追踪创建
    print("\n5. 创建追踪子弹:")
    from sprites import Bullet, mobs
    bullet = Bullet(640, 360, homing=player.homing_level)
    print(f"  OK: 子弹创建成功")
    print(f"  子弹 homing 值: {bullet.homing}")
    print(f"  子弹追踪状态: {'启用' if bullet.homing > 0 else '禁用'}")
    
    print("\n=== 诊断完成 ===")
    print("OK: 所有测试通过，追踪卡牌系统正常工作")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

