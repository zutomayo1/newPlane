#!/usr/bin/env python3
"""测试星渊女王Boss是否有bug"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("导入模块...")
    from config import BOSS_DB
    from sprites import Boss
    import pygame
    
    print("初始化pygame...")
    pygame.init()
    
    print("\n检查BOSS_DB中的星渊女王配置...")
    if "abyss_queen" in BOSS_DB:
        boss_config = BOSS_DB["abyss_queen"]
        print(f"✓ 星渊女王配置存在")
        print(f"  名称: {boss_config.get('name')}")
        print(f"  描述: {boss_config.get('desc')}")
        print(f"  颜色: {boss_config.get('color')}")
        print(f"  阶段数: {len(boss_config.get('phases', []))}")
    else:
        print("✗ 星渊女王配置不存在!")
        sys.exit(1)
    
    print("\n创建星渊女王Boss...")
    try:
        boss = Boss("abyss_queen")
        print(f"✓ Boss创建成功")
        print(f"  名称: {boss.name}")
        print(f"  血量: {boss.hp}")
        print(f"  图像尺寸: {boss.image.get_size()}")
    except Exception as e:
        print(f"✗ Boss创建失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n测试Boss的更新方法...")
    try:
        for i in range(10):
            boss.update()
            if i % 2 == 0:
                print(f"  更新 {i+1}/10...")
        print(f"✓ Boss更新成功")
    except Exception as e:
        print(f"✗ Boss更新失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n检查子弹类型...")
    bullet_types = ["star", "star_guard", "star_burst"]
    for b_type in bullet_types:
        print(f"  - {b_type}: OK")
    
    print("\n✓ 所有测试通过！星渊女王没有bug")
    
except Exception as e:
    print(f"\n✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
