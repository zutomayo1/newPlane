#!/usr/bin/env python3
"""直接测试星渊女王的攻击循环"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pygame
import math
from config import BOSS_DB, WIDTH, HEIGHT
from sprites import Boss, Bullet, all_sprites, enemy_bullets
import random

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

print("创建星渊女王Boss...")
boss = Boss("abyss_queen")
boss.rect.y = 100  # 强制设置到战斗位置
boss.state = "fight"  # 直接进入战斗状态
boss.start_y = 100
all_sprites.add(boss)

print("运行模拟战斗（200帧）...")
try:
    for frame in range(200):
        clock.tick(60)
        
        # 更新所有精灵
        for sprite in all_sprites:
            if hasattr(sprite, 'update'):
                sprite.update()
        
        # 每10帧检查一下
        if frame % 10 == 0:
            enemy_bullet_count = len(enemy_bullets)
            print(f"  [第{frame+1}帧] Boss血量: {boss.hp}/{boss.max_hp}, 敌方子弹数: {enemy_bullet_count}, Boss阶段: {boss.phase_index}")
            
            # 检查最后一个敌方子弹
            if enemy_bullets:
                last_bullet = list(enemy_bullets)[-1]
                print(f"    最后的敌方子弹: type={last_bullet.b_type}, pos={last_bullet.pos}")
        
        # 清除屏幕（虽然不显示）
        screen.fill((0, 0, 0))
        pygame.display.flip()
        
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n测试完成！最终敌方子弹数: {len(enemy_bullets)}")
print(f"  Boss状态: 血量={boss.hp}, 阶段={boss.phase_index}, 状态={boss.state}")
pygame.quit()
