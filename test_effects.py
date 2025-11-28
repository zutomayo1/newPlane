#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试特效系统功能"""

import sys
sys.path.insert(0, r'c:\Users\真夜中\Desktop\newPlane')

from systems import EffectManager, ParticleEffect, ScreenShake

print("=" * 50)
print("特效系统测试")
print("=" * 50)

# 创建特效管理器
effect_mgr = EffectManager()

print("\n1. 粒子效果测试:")
effect_mgr.add_particle(100, 100, "explosion", 20)
print(f"   ✓ 添加爆炸效果 (20个粒子)")

effect_mgr.add_particle(200, 200, "ice", 15)
print(f"   ✓ 添加冰冻效果 (15个粒子)")

effect_mgr.add_particle(300, 300, "lightning", 25)
print(f"   ✓ 添加闪电效果 (25个粒子)")

effect_mgr.add_particle(400, 400, "heal", 18)
print(f"   ✓ 添加治疗效果 (18个粒子)")

print(f"\n2. 初始粒子数: {len(effect_mgr.particles)}")

print(f"\n3. 屏幕震动测试:")
effect_mgr.trigger_shake(duration=10, intensity=5)
print(f"   ✓ 触发屏幕震动 (强度 5, 持续 10 帧)")
print(f"   ✓ 当前震动活跃: {effect_mgr.screen_shake.is_active()}")

print(f"\n4. 模拟更新 (10帧):")
for i in range(10):
    effect_mgr.update()
print(f"   ✓ 更新完成")
print(f"   剩余粒子数: {len(effect_mgr.particles)}")
print(f"   屏幕震动活跃: {effect_mgr.screen_shake.is_active() if effect_mgr.screen_shake else False}")

print(f"\n5. 继续更新 (20帧，清空粒子):")
for i in range(20):
    effect_mgr.update()
print(f"   ✓ 更新完成")
print(f"   剩余粒子数: {len(effect_mgr.particles)}")

print(f"\n6. 屏幕偏移测试:")
effect_mgr.trigger_shake(duration=15, intensity=8)
offset1 = effect_mgr.get_shake_offset()
print(f"   第1次获取偏移: {offset1}")
effect_mgr.update()
offset2 = effect_mgr.get_shake_offset()
print(f"   第2次获取偏移: {offset2}")

print("\n" + "=" * 50)
print("特效系统测试完成 ✓")
print("=" * 50)
