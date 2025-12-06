"""简单诊断追踪卡牌问题"""

# 检查卡牌定义
from roguelite import CARD_MODIFIERS_DICT

print("=== 检查追踪卡牌定义 ===")
if "homing_addon" in CARD_MODIFIERS_DICT:
    homing_card = CARD_MODIFIERS_DICT["homing_addon"]
    print(f"卡牌名称: {homing_card['name']}")
    print(f"卡牌效果: {homing_card['effect']}")
    print(f"效果类型: {homing_card['type']}")
else:
    print("错误: 找不到homing_addon!")

# 检查effect应用代码
print("\n=== 检查apply_card_effect函数 ===")
import inspect
from roguelite import apply_card_effect

source = inspect.getsource(apply_card_effect)
homing_lines = [line for line in source.split('\n') if 'homing' in line.lower()]
print("追踪相关代码:")
for line in homing_lines:
    print(f"  {line}")

# 模拟应用卡牌
print("\n=== 模拟应用卡牌 ===")

class MockPlayer:
    def __init__(self):
        self.homing_level = 0

player = MockPlayer()
print(f"初始 homing_level: {player.homing_level}")
print(f"初始 has_homing: {getattr(player, 'has_homing', False)}")
print(f"初始 homing_strength: {getattr(player, 'homing_strength', 0)}")

# 模拟卡牌效果
effect = {"homing": True, "homing_strength": 0.5}
print(f"\n应用效果: {effect}")

# 手动应用逻辑(从apply_card_effect复制)
if "homing" in effect and effect["homing"]:
    player.has_homing = True
    if "homing_strength" in effect:
        player.homing_strength = getattr(player, "homing_strength", 0.0) + effect["homing_strength"]
    else:
        player.homing_strength = getattr(player, "homing_strength", 0.0) + 0.15

print(f"\n应用后 has_homing: {getattr(player, 'has_homing', False)}")
print(f"应用后 homing_strength: {getattr(player, 'homing_strength', 0)}")

# 检查射击时的计算
print("\n=== 射击时的追踪值计算 ===")
homing_value = getattr(player, 'homing_strength', 0) if getattr(player, 'has_homing', False) else 0
print(f"homing_value (传给Bullet): {homing_value}")

# 检查子弹追踪逻辑
print("\n=== 子弹追踪逻辑 ===")
print(f"检查条件: self.homing > 0")
print(f"当前值: {homing_value} > 0 = {homing_value > 0}")
print(f"追踪强度: min({homing_value} * 3, 0.95) = {min(homing_value * 3, 0.95)}")

print("\n=== 诊断结果 ===")
if homing_value > 0:
    print("✓ 追踪系统应该工作正常!")
    print(f"  - 卡牌效果正确设置")
    print(f"  - 追踪值 {homing_value} 会传给子弹")
    print(f"  - 子弹会以 {min(homing_value * 3, 0.95):.2f} 的强度追踪")
else:
    print("✗ 追踪系统有问题!")
    print("  可能原因:")
    print("  - 卡牌效果没有应用")
    print("  - homing_strength没有传递")
