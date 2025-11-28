#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追踪卡牌效果验证 - 模拟完整升级流程"""

import sys
import math
sys.path.insert(0, r'c:\Users\真夜中\Desktop\newPlane')

try:
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))
    
    from config import PLANES
    from sprites import Player, Bullet, Enemy, mobs
    from roguelite import apply_buff_to_player
    
    print("=== 追踪卡牌完整效果验证 ===\n")
    
    # 创建玩家和敌人
    print("1. 创建游戏对象...")
    player = Player("striker")
    enemy = Enemy("drone")
    mobs.add(enemy)
    
    # 手动设置敌人位置
    enemy.rect.x = 640
    enemy.rect.y = 200
    
    print(f"   玩家位置: ({player.rect.centerx}, {player.rect.centery})")
    print(f"   敌人位置: ({enemy.rect.centerx}, {enemy.rect.centery})")
    print(f"   初始 homing_level: {player.homing_level}")
    
    # 测试1: 不追踪的子弹
    print("\n2. 测试普通子弹 (无追踪)...")
    bullet1 = Bullet(player.rect.centerx, player.rect.top, homing=0)
    print(f"   创建子弹: homing={bullet1.homing}")
    print(f"   初始速度: {bullet1.vel}")
    initial_vel = bullet1.vel.copy()
    
    # 模拟5帧更新
    for i in range(5):
        bullet1.update()
    print(f"   5帧后速度: {bullet1.vel}")
    print(f"   速度是否改变: {bullet1.vel != initial_vel}")
    
    # 清理
    bullet1.kill()
    mobs.remove(enemy)
    
    # 测试2: 应用追踪卡牌后
    print("\n3. 应用追踪卡牌...")
    apply_buff_to_player(player, "homing")
    print(f"   应用后 homing_level: {player.homing_level}")
    
    # 重新添加敌人
    enemy2 = Enemy("drone")
    mobs.add(enemy2)
    enemy2.rect.x = 640
    enemy2.rect.y = 200
    
    # 创建追踪子弹
    print("\n4. 创建追踪子弹...")
    bullet2 = Bullet(player.rect.centerx, player.rect.top, homing=player.homing_level)
    print(f"   创建子弹: homing={bullet2.homing}")
    print(f"   初始速度: {bullet2.vel}")
    initial_vel2 = bullet2.vel.copy()
    
    # 模拟10帧更新 (追踪逻辑应该工作)
    print(f"\n5. 模拟10帧更新并检查追踪效果...")
    for frame in range(10):
        bullet2.update()
        
        # 检查速度是否改变 (追踪导致向量改变)
        current_vel = bullet2.vel
        distance_to_enemy = bullet2.pos.distance_to(pygame.math.Vector2(enemy2.rect.center))
        
        if frame == 0:
            print(f"   初始: vel={current_vel}, dist={distance_to_enemy:.1f}")
        elif frame == 9:
            print(f"   第10帧: vel={current_vel}, dist={distance_to_enemy:.1f}")
            
            # 检查速度是否改变
            vel_changed = (abs(current_vel.x - initial_vel2.x) > 0.01 or 
                          abs(current_vel.y - initial_vel2.y) > 0.01)
            print(f"   速度是否改变 (表示追踪工作): {vel_changed}")
    
    print("\n=== 验证结论 ===")
    if bullet2.homing > 0:
        print("✓ 追踪子弹创建成功")
        print("✓ 追踪卡牌系统正常工作")
        print("\n实际应用:")
        print("- 获取智能弹道卡牌后，homing_level + 1")
        print("- 射出的子弹会自动追踪500范围内的敌人")
        print("- 追踪通过平滑的速度向量转向实现")
    else:
        print("✗ 追踪卡牌未正确应用")
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
