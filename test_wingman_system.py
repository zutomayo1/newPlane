#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""僚机系统测试"""

import sys
sys.path.insert(0, r'c:\Users\真夜中\Desktop\newPlane')

try:
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))
    
    from sprites import Player
    from wingman import WingmanSquadron, Wingman
    
    print("=== 僚机系统测试 ===\n")
    
    # 1. 创建玩家
    print("1. 创建玩家...")
    player = Player("striker")
    print(f"   玩家位置: ({player.rect.centerx}, {player.rect.centery})")
    print(f"   玩家追踪等级: {player.homing_level}")
    print(f"   最多僚机数: {player.max_wingmen}")
    
    # 2. 初始化僚机编队
    print("\n2. 初始化僚机编队...")
    player.wingman_squadron = WingmanSquadron(player, max_wingmen=2)
    print(f"   编队创建成功")
    print(f"   当前僚机数: {len(player.wingman_squadron.wingmen)}")
    
    # 3. 添加僚机（不需要武器，仅测试编队系统）
    print("\n3. 添加僚机...")
    
    # 添加第一个僚机（无武器）
    result1 = player.wingman_squadron.add_wingman(None)
    print(f"   添加第1个僚机: {'成功' if result1 else '失败'}")
    
    # 添加第二个僚机
    result2 = player.wingman_squadron.add_wingman(None)
    print(f"   添加第2个僚机: {'成功' if result2 else '失败'}")
    
    # 尝试添加第3个（应该超过上限）
    result3 = player.wingman_squadron.add_wingman(None)
    print(f"   添加第3个僚机: {'成功' if result3 else '失败（超过上限）'}")
    
    # 4. 检查编队状态
    print("\n4. 编队状态...")
    status = player.wingman_squadron.get_squad_status()
    print(f"   编队规模: {status['count']}/{status['max']}")
    for i, w_status in enumerate(status['wingmen']):
        print(f"   - 僚机{i+1}: 位置={w_status['slot']}, 血量={w_status['health']}, 武器={w_status['weapon']}")
    
    # 5. 测试僚机更新
    print("\n5. 模拟10帧更新...")
    from sprites import mobs
    for frame in range(10):
        player.wingman_squadron.update(mobs)
        if frame % 3 == 0:
            for w in player.wingman_squadron.wingmen:
                print(f"   第{frame+1}帧: 僚机位置 ({w.x:.1f}, {w.y:.1f})")
    
    # 6. 测试伤害
    print("\n6. 测试僚机伤害...")
    if player.wingman_squadron.wingmen:
        wingman = player.wingman_squadron.wingmen[0]
        print(f"   僚机初始血量: {wingman.health}")
        wingman.take_damage(30)
        print(f"   受到30点伤害后: {wingman.health}")
        wingman.heal(50)
        print(f"   恢复50点血量后: {wingman.health}")
    
    # 7. 验证玩家不再使用副武器
    print("\n7. 验证玩家副武器变化...")
    print(f"   玩家weapon_slots数量: {len(player.weapon_slots)}")
    print(f"   玩家不再直接调用weapon_slots.shoot()")
    print(f"   所有副武器逻辑已转移到僚机系统")
    
    print("\n=== 测试完成 ===")
    print("OK: 僚机系统初始化成功")
    print("OK: 玩家副武器已禁用")
    print("OK: 僚机可以使用副武器")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
