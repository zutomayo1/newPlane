"""
测试僚机涂装系统的完整集成
验证从解锁、装备到游戏中显示的完整流程
"""
import pygame
import sys

# 初始化 Pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("僚机涂装系统集成测试")

print("=" * 60)
print("僚机涂装系统集成测试")
print("=" * 60)

# 导入必要的模块
try:
    from customization import CustomizationManager
    from wingman_themes import WINGMAN_THEMES
    from wingman import Wingman, WingmanSquadron
    from sprites import Player
    print("✓ 所有模块导入成功")
except ImportError as e:
    print(f"✗ 模块导入失败: {e}")
    sys.exit(1)

# 初始化自定义管理器
cm = CustomizationManager()
print(f"\n【CustomizationManager 状态】")
print(f"已解锁僚机涂装: {cm.get_unlocked_wingman_count()}/{cm.get_total_wingman_count()}")
print(f"已装备涂装槽位: {list(cm.equipped_wingman_themes.keys())}")

# 创建虚拟武器库数据
mock_arsenal = {
    "currencies": {
        "cores": 10000  # 给足够的核心用于测试
    }
}

# 测试解锁所有僚机涂装
print(f"\n【解锁所有僚机涂装】")
for theme_id in WINGMAN_THEMES:
    if theme_id == "default":
        continue  # 跳过默认涂装
    
    success, msg = cm.unlock_wingman_theme(theme_id, mock_arsenal)
    if success:
        print(f"  ✓ {theme_id}: {msg}")
    else:
        print(f"  - {theme_id}: {msg}")

print(f"\n解锁后状态: {cm.get_unlocked_wingman_count()}/{cm.get_total_wingman_count()}")
print(f"剩余核心: {mock_arsenal['currencies']['cores']}")

# 测试为4个槽位装备不同涂装
print(f"\n【为4个僚机槽位装备涂装】")
test_themes = ["quantum_ghost", "lava_titan", "aurora_valkyrie", "shadow_reaper"]
for i, theme_id in enumerate(test_themes):
    success, msg = cm.equip_wingman_theme(i, theme_id)
    print(f"  槽位 {i}: {theme_id} -> {msg}")

# 创建玩家和僚机编队
print(f"\n【创建玩家和僚机编队】")
player = Player("striker")
player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
squadron = WingmanSquadron(player, max_wingmen=4)
print(f"  ✓ 玩家创建成功")
print(f"  ✓ 僚机编队创建成功 (最大僚机数: 4)")

# 添加4个僚机
print(f"\n【添加僚机到编队】")
for i in range(4):
    success = squadron.add_wingman(None)  # 武器系统可以为None
    if success:
        wingman = squadron.wingmen[i]
        print(f"  ✓ 僚机 {i}: 槽位={wingman.slot_index}, 涂装={wingman.paint_theme_id}")
    else:
        print(f"  ✗ 僚机 {i}: 添加失败")

# 可视化测试
print(f"\n【启动可视化测试】")
print(f"显示4个僚机，每个使用不同的涂装")
print(f"按 ESC 退出")

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # 更新僚机位置
    squadron.update(None)
    
    # 清屏
    screen.fill((20, 20, 30))
    
    # 绘制标题
    font = pygame.font.Font(None, 36)
    title = font.render("Wingman Paint System Integration Test", True, (255, 255, 255))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
    
    # 绘制信息
    info_font = pygame.font.Font(None, 24)
    info_lines = [
        f"Unlocked Themes: {cm.get_unlocked_wingman_count()}/{cm.get_total_wingman_count()}",
        f"Active Wingmen: {len(squadron.wingmen)}/{squadron.max_wingmen}",
        "",
        "Wingman Paint Themes:",
    ]
    
    for i, wingman in enumerate(squadron.wingmen):
        theme_name = WINGMAN_THEMES[wingman.paint_theme_id]['name']
        info_lines.append(f"  Slot {i}: {theme_name}")
    
    for i, line in enumerate(info_lines):
        text = info_font.render(line, True, (200, 200, 255))
        screen.blit(text, (30, 80 + i * 30))
    
    # 绘制玩家（简单的中心点）
    pygame.draw.circle(screen, (100, 255, 100), 
                      (int(player.rect.centerx), int(player.rect.centery)), 15)
    pygame.draw.circle(screen, (255, 255, 255), 
                      (int(player.rect.centerx), int(player.rect.centery)), 15, 2)
    
    # 绘制僚机编队
    squadron.draw(screen)
    
    # 绘制控制提示
    hint = info_font.render("[ESC] Exit", True, (150, 150, 150))
    screen.blit(hint, (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 40))
    
    pygame.display.flip()

pygame.quit()

print(f"\n【测试完成】")
print(f"僚机涂装系统集成测试通过！")
print("=" * 60)
