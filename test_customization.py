"""测试涂装系统"""
import sys
sys.path.insert(0, '.')

try:
    print("1. 导入config...")
    from config import PLANES
    print("   ✓ config导入成功")
    
    print("2. 导入customization...")
    from customization import customization_manager, PAINT_THEMES
    print("   ✓ customization导入成功")
    
    print("3. 测试get_theme_visual...")
    for plane_id in list(PLANES.keys())[:3]:  # 测试前3个飞机
        print(f"   测试飞机: {plane_id}")
        default_visual = PLANES[plane_id].get('visual', None)
        print(f"   default_visual: {default_visual}")
        
        result = customization_manager.get_theme_visual(plane_id, default_visual)
        print(f"   result: {result}")
    
    print("4. 测试Player初始化...")
    from sprites import Player
    print("   导入Player成功")
    
    # 测试创建玩家
    plane_id = "striker"
    default_visual = PLANES[plane_id].get('visual', None)
    custom_visual = customization_manager.get_theme_visual(plane_id, default_visual)
    print(f"   custom_visual for striker: {custom_visual}")
    
    print("   创建Player...")
    player = Player(plane_id, custom_visual=custom_visual)
    print("   ✓ Player创建成功")
    
    print("\n✅ 所有测试通过！")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
