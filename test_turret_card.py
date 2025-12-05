"""测试炮塔卡牌是否生效"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("炮塔卡牌系统测试")
print("=" * 60)

# 1. 检查卡牌数据
print("\n【1. 检查卡牌数据】")
try:
    from roguelite import BASE_CARDS
    turret_card = BASE_CARDS.get("auto_turret")
    if turret_card:
        print(f"✅ 找到炮塔卡牌: {turret_card['name']}")
        print(f"   描述: {turret_card['desc']}")
        print(f"   品质: {turret_card['rarity']}星")
        print(f"   基础效果: {turret_card['base_effect']}")
        print(f"   升级路径: {len(turret_card['upgrades'])}级")
        for i, upgrade in enumerate(turret_card['upgrades'], 1):
            print(f"     Lv{upgrade['level']}: {upgrade['desc']} -> {upgrade['effect']}")
    else:
        print("❌ 未找到炮塔卡牌")
except Exception as e:
    print(f"❌ 加载卡牌数据失败: {e}")

# 2. 检查效果应用代码
print("\n【2. 检查效果应用代码】")
try:
    from roguelite import apply_card_effect
    print("✅ 效果应用函数存在")
    
    # 检查是否包含turret_count处理
    import inspect
    source = inspect.getsource(apply_card_effect)
    if 'turret_count' in source:
        print("✅ 发现 turret_count 处理代码")
        # 提取相关代码行
        lines = source.split('\n')
        for i, line in enumerate(lines):
            if 'turret_count' in line or (i > 0 and 'turret' in lines[i-1]):
                print(f"   {line.strip()}")
    else:
        print("❌ 未发现 turret_count 处理代码")
except Exception as e:
    print(f"❌ 检查失败: {e}")

# 3. 检查玩家类的炮塔属性
print("\n【3. 检查玩家类的炮塔属性】")
try:
    from sprites import Player
    
    # 创建测试玩家
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    player = Player("striker")
    
    # 检查炮塔相关属性
    turret_attrs = ['has_turrets', 'turret_count', 'turret_damage', 'turret_cooldown']
    print("炮塔相关属性:")
    for attr in turret_attrs:
        if hasattr(player, attr):
            value = getattr(player, attr)
            print(f"   ✅ {attr}: {value}")
        else:
            print(f"   ❌ {attr}: 不存在")
    
    pygame.quit()
except Exception as e:
    print(f"❌ 检查失败: {e}")

# 4. 检查炮塔射击方法
print("\n【4. 检查炮塔射击方法】")
try:
    from sprites import Player
    import inspect
    
    if hasattr(Player, '_fire_turrets'):
        print("✅ 找到 _fire_turrets 方法")
        source = inspect.getsource(Player._fire_turrets)
        lines = source.split('\n')
        print(f"   方法共 {len(lines)} 行")
        print("   关键逻辑:")
        for line in lines[:10]:  # 显示前10行
            if line.strip():
                print(f"     {line}")
    else:
        print("❌ 未找到 _fire_turrets 方法")
except Exception as e:
    print(f"❌ 检查失败: {e}")

# 5. 检查update方法中的炮塔更新
print("\n【5. 检查update方法中的炮塔更新】")
try:
    from sprites import Player
    import inspect
    
    source = inspect.getsource(Player.update)
    if 'has_turrets' in source and '_fire_turrets' in source:
        print("✅ update方法包含炮塔更新逻辑")
        lines = source.split('\n')
        for i, line in enumerate(lines):
            if 'turret' in line.lower():
                print(f"   {line.strip()}")
    else:
        print("❌ update方法未包含炮塔更新逻辑")
except Exception as e:
    print(f"❌ 检查失败: {e}")

# 6. 检查渲染代码
print("\n【6. 检查main.py中的炮塔渲染】")
try:
    with open('main.py', 'r', encoding='utf-8') as f:
        main_code = f.read()
    
    if 'has_turrets' in main_code and '绘制炮塔' in main_code:
        print("✅ main.py包含炮塔渲染代码")
        lines = main_code.split('\n')
        found_section = False
        for line in lines:
            if '绘制炮塔' in line:
                found_section = True
            if found_section:
                if line.strip():
                    print(f"   {line[:80]}")
                if 'else:' in line and found_section:
                    break
    else:
        print("❌ main.py未包含炮塔渲染代码")
except Exception as e:
    print(f"❌ 检查失败: {e}")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)
print("\n建议:")
print("1. 进入游戏，获取'自动炮塔'卡牌")
print("2. 观察玩家周围是否出现环绕的橙色炮塔")
print("3. 炮塔应该自动向附近敌人射击（橙色小子弹）")
print("4. 升级后炮塔数量和伤害应该增加")
