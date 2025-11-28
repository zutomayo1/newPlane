"""可视化测试：僚机子弹是否正常显示"""
import pygame
import sys
import os
import math

pygame.init()

sys.path.insert(0, os.path.dirname(__file__))

from sprites import Player, Enemy, bullets, all_sprites, mobs, Bullet
from config import WIDTH, HEIGHT, CYAN, BLACK
from systems import WeaponSystem
from roguelite import add_wingmen_to_player

# 初始化显示
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wingman Bullet Visual Test")
clock = pygame.time.Clock()

# 创建玩家
player = Player()
all_sprites.add(player)

# 初始化僚机编队
add_wingmen_to_player(player, count=4)

# 创建敌人目标
for i in range(3):
    enemy = Enemy("drone")
    enemy.rect.x = 200 + i * 150
    enemy.rect.y = 200

# 游戏循环
running = True
frame = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    frame += 1
    
    # 更新（只更新玩家和僚机，不更新敌人）
    # all_sprites.update()
    player.update()  # 只更新玩家
    player.wingman_squadron.update(mobs, global_time=frame*0.04)
    
    # 绘制
    screen.fill(BLACK)
    all_sprites.draw(screen)
    player.wingman_squadron.draw(screen)
    
    # 绘制子弹计数
    font = pygame.font.Font(None, 36)
    text = font.render(f"Bullets: {len(bullets)}", True, CYAN)
    screen.blit(text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
print(f"Test ended. Total frames: {frame}, Peak bullets: {len(bullets)}")
