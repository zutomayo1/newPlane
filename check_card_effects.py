"""检查哪些卡牌效果可能没有实现"""
import sys

# 导入卡牌数据
from roguelite import BASE_CARDS, MODIFIER_CARDS

print("=" * 80)
print("卡牌效果实现检查")
print("=" * 80)

# 收集所有效果类型
all_effects = set()
card_effects = {}

print("\n【基础卡牌效果】")
for card_id, card_data in BASE_CARDS.items():
    base_effect = card_data.get("base_effect", {})
    effects_list = list(base_effect.keys())
    all_effects.update(effects_list)
    card_effects[card_id] = effects_list
    print(f"{card_data['name']:12s} | {', '.join(effects_list)}")

print("\n【修饰卡牌效果】")
for card_id, card_data in MODIFIER_CARDS.items():
    base_effect = card_data.get("base_effect", {})
    effects_list = list(base_effect.keys())
    all_effects.update(effects_list)
    card_effects[card_id] = effects_list
    print(f"{card_data['name']:12s} | {', '.join(effects_list)}")

print("\n" + "=" * 80)
print(f"【所有效果类型】共 {len(all_effects)} 种")
print("=" * 80)
for effect in sorted(all_effects):
    print(f"  - {effect}")

# 检查roguelite.py中是否实现了这些效果
print("\n" + "=" * 80)
print("【检查效果实现情况】")
print("=" * 80)

with open('roguelite.py', 'r', encoding='utf-8') as f:
    code = f.read()

not_implemented = []
implemented = []

for effect in sorted(all_effects):
    # 检查是否在apply_card_effect中处理了这个效果
    if f'if "{effect}" in effect:' in code or f'if "{effect}"' in code:
        implemented.append(effect)
        print(f"✅ {effect:25s} - 已实现")
    else:
        not_implemented.append(effect)
        print(f"❌ {effect:25s} - 未实现")

print("\n" + "=" * 80)
print("【统计】")
print("=" * 80)
print(f"已实现: {len(implemented)}/{len(all_effects)}")
print(f"未实现: {len(not_implemented)}/{len(all_effects)}")

if not_implemented:
    print("\n【未实现的效果】")
    for effect in not_implemented:
        # 找出使用这个效果的卡牌
        cards_using = [name for name, effects in card_effects.items() 
                      if effect in effects]
        print(f"  {effect:25s} <- {', '.join(cards_using)}")
