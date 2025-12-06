"""测试追踪卡牌效果"""
import pygame
import sys

# 初始化
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("追踪卡牌测试")

# 导入必要模块
from sprites import Player, Enemy, all_sprites, mobs, bullets
from roguelite import Card, CARD_MODIFIERS, apply_card_effect

def main():
    clock = pygame.time.Clock()
    
    # 创建玩家
    player = Player("striker")
    print(f"初始状态:")
    print(f"  homing_level: {player.homing_level}")
    print(f"  has_homing: {getattr(player, 'has_homing', False)}")
    print(f"  homing_strength: {getattr(player, 'homing_strength', 0)}")
    
    # 创建测试卡牌并添加追踪模块
    print("\n添加追踪卡牌...")
    test_card = Card("speed_1")  # 随便一个基础卡
    test_card.add_modifier("homing_addon")
    
    # 应用卡牌效果
    apply_card_effect(player, test_card)
    
    print(f"\n应用卡牌后:")
    print(f"  homing_level: {player.homing_level}")
    print(f"  has_homing: {getattr(player, 'has_homing', False)}")
    print(f"  homing_strength: {getattr(player, 'homing_strength', 0)}")
    
    # 检查射击时的追踪值计算
    print(f"\n射击时计算:")
    homing_value = getattr(player, 'homing_strength', 0) if getattr(player, 'has_homing', False) else 0
    print(f"  homing_value (传给子弹): {homing_value}")
    print(f"  预期：应该传递homing_strength的值到子弹")
    
    # 创建敌人用于测试
    test_mob = Enemy("drone", 0)
    test_mob.rect.center = (400, 200)
    
    # 测试射击
    print("\n测试射击...")
    player.last_shot = 0  # 重置射击冷却
    player._fire_main_gun()
    
    # 检查生成的子弹
    if bullets:
        test_bullet = list(bullets)[0]
        print(f"  子弹的homing值: {test_bullet.homing}")
        print(f"  子弹追踪 {'有效' if test_bullet.homing > 0 else '无效'}")
    else:
        print("  没有生成子弹!")
    
    # 游戏循环
    running = True
    frame = 0
    while running and frame < 300:  # 运行5秒
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # 更新
        all_sprites.update()
        
        # 绘制
        screen.fill((20, 20, 30))
        all_sprites.draw(screen)
        
        # 显示信息
        font = pygame.font.Font(None, 24)
        info = [
            f"Frame: {frame}",
            f"has_homing: {getattr(player, 'has_homing', False)}",
            f"homing_strength: {getattr(player, 'homing_strength', 0):.2f}",
            f"Bullets: {len(bullets)}",
        ]
        for i, line in enumerate(info):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
        frame += 1
    
    pygame.quit()
    print("\n测试完成!")

if __name__ == "__main__":
    main()
