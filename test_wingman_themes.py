"""
测试僚机涂装系统
验证8种涂装主题是否正常工作
"""
import pygame
import sys
import math

# 初始化 Pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("僚机涂装系统测试")

# 导入僚机涂装系统
try:
    from wingman_themes import WINGMAN_THEMES, WINGMAN_DRAW_FUNCTIONS
    print("✓ 成功导入僚机涂装系统")
    print(f"✓ 发现 {len(WINGMAN_THEMES)} 种僚机涂装主题")
    print(f"✓ 发现 {len(WINGMAN_DRAW_FUNCTIONS)} 个绘制函数")
    
    # 检查每个主题是否有对应的绘制函数
    for theme_id in WINGMAN_THEMES:
        if theme_id in WINGMAN_DRAW_FUNCTIONS:
            print(f"  ✓ {theme_id}: {WINGMAN_THEMES[theme_id]['name']}")
        else:
            print(f"  ✗ {theme_id}: 缺少绘制函数")
    
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 导入自定义管理器
try:
    from customization import CustomizationManager
    cm = CustomizationManager()
    print(f"\n✓ CustomizationManager 初始化成功")
    print(f"✓ 已解锁僚机涂装数: {cm.get_unlocked_wingman_count()}/{cm.get_total_wingman_count()}")
except Exception as e:
    print(f"✗ CustomizationManager 初始化失败: {e}")
    cm = None

# 测试数据
theme_ids = list(WINGMAN_THEMES.keys())
current_theme_index = 0
clock = pygame.time.Clock()

# 测试位置（屏幕中央）
test_x = SCREEN_WIDTH // 2
test_y = SCREEN_HEIGHT // 2

print(f"\n【测试开始】")
print(f"按 空格键 切换涂装主题")
print(f"按 ESC 退出测试")
print(f"\n当前主题: {theme_ids[current_theme_index]} - {WINGMAN_THEMES[theme_ids[current_theme_index]]['name']}")

# 主循环
running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                # 切换涂装
                current_theme_index = (current_theme_index + 1) % len(theme_ids)
                theme_id = theme_ids[current_theme_index]
                theme = WINGMAN_THEMES[theme_id]
                print(f"\n切换到: {theme_id} - {theme['name']}")
                print(f"  描述: {theme['desc']}")
                print(f"  价格: {theme['cost']} 核心")
                print(f"  品质: {theme['category']}")
    
    # 清屏
    screen.fill((20, 20, 30))
    
    # 绘制标题
    font = pygame.font.Font(None, 36)
    title = font.render("Wingman Paint System Test", True, (255, 255, 255))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
    
    # 绘制当前主题信息
    info_font = pygame.font.Font(None, 28)
    theme_id = theme_ids[current_theme_index]
    theme = WINGMAN_THEMES[theme_id]
    
    info_lines = [
        f"Theme: {theme['name']}",
        f"ID: {theme_id}",
        f"Cost: {theme['cost']} Cores",
        f"Quality: {theme['category']}",
        f"[SPACE] Next  [ESC] Exit"
    ]
    
    for i, line in enumerate(info_lines):
        text = info_font.render(line, True, (200, 200, 255))
        screen.blit(text, (30, 80 + i * 35))
    
    # 绘制僚机（使用当前涂装）
    try:
        draw_func = WINGMAN_DRAW_FUNCTIONS[theme_id]
        
        # 在屏幕中央绘制
        draw_func(screen, test_x, test_y)
        
        # 在四个角落也绘制，展示编队效果
        positions = [
            (test_x - 150, test_y - 100),  # 左上
            (test_x + 150, test_y - 100),  # 右上
            (test_x - 150, test_y + 100),  # 左下
            (test_x + 150, test_y + 100),  # 右下
        ]
        
        for pos_x, pos_y in positions:
            draw_func(screen, pos_x, pos_y)
        
    except Exception as e:
        # 如果绘制失败，显示错误信息
        error_text = info_font.render(f"Draw Error: {str(e)}", True, (255, 100, 100))
        screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, SCREEN_HEIGHT - 50))
    
    # 绘制中心十字准线
    pygame.draw.line(screen, (80, 80, 80), (test_x - 10, test_y), (test_x + 10, test_y), 1)
    pygame.draw.line(screen, (80, 80, 80), (test_x, test_y - 10), (test_x, test_y + 10), 1)
    
    pygame.display.flip()

pygame.quit()
print("\n【测试结束】")
