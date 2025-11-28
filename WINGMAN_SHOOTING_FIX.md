# 僚机射击系统修复 (Wingman Shooting System Fix)

## 问题描述
用户报告看不到僚机发射的子弹。

## 根本原因分析

### 问题1：武器系统未更新
**位置**: `wingman.py` - `Wingman.update()` 方法

**原因**: 僚机的武器系统没有调用 `update()` 方法，导致：
- Beam 类型武器的能量无法恢复
- Cannon 类型武器的热量无法散发
- 其他武器的冷却计时器无法更新

**症状**: `weapon.can_shoot()` 总是返回 False（因为能量 = 0 或热量已满）

**修复方法**:
```python
# 在 wingman.update() 中添加
if self.weapon:
    self.weapon.update()  # 更新武器系统状态
```

### 问题2：冷却时间过长（用户需求）
**位置**: `roguelite.py` - `create_wingman_weapon()` 函数

**原因**: 僚机继承了玩家武器的完整冷却配置，导致射击频率太低

**修复方法**:
```python
# 降低冷却时间为原来的一半
if hasattr(wingman_weapon, 'cooldown_max'):
    wingman_weapon.cooldown_max = max(1, wingman_weapon.cooldown_max // 2)
```

## 修复后的效果

✅ 僚机现在能正常射击
✅ 射击频率提升（冷却时间减半）
✅ 子弹在游戏中可见

## 修改文件

1. **wingman.py** (第 76-79 行)
   - 添加 `self.weapon.update()` 调用

2. **roguelite.py** (第 64-65 行, 82-83 行)
   - 在两处 `create_wingman_weapon` 中添加冷却时间减半逻辑

## 验证方式

1. 启动游戏
2. 获得僚机卡牌（保证获得机制）
3. 在游戏中与敌人交战
4. 观察僚机周围是否有射击的青色光束

**预期结果**: 应该看到4个僚机不断向敌人发射青色光束
