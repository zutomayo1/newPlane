# 升级卡牌选择 Bug 修复报告

## 问题描述

**症状**：每次升级待选择的卡片总是和第一次升级的一样

**根本原因**：在 `roguelite.py` 的 `trigger_levelup()` 方法中，存在一个早期返回检查：

```python
def trigger_levelup(self):
    # 如果已经处于等待升级状态，则不重复触发
    if self.level_up_ready:
        return  # ← 这行导致问题！
```

当玩家进行第一次升级时：
1. `level_up()` 调用 `trigger_levelup()`
2. `trigger_levelup()` 生成3个随机卡牌，设置 `level_up_ready = True`
3. 玩家选择卡牌，设置 `level_up_ready = False`

但当进行第二次升级时：
1. `level_up()` 再次调用 `trigger_levelup()`
2. 由于某个时序问题，`level_up_ready` 可能仍为 `True`
3. 函数在第一行就返回，不生成新卡牌
4. 系统使用旧的卡牌组合

## 修复方案

### 修改1：删除 trigger_levelup 中的早期返回

**文件**：`roguelite.py` 第291-294行

```python
# 旧代码：
def trigger_levelup(self):
    """触发升级，随机选择 3 个不重复的增益"""
    # 如果已经处于等待升级状态，则不重复触发
    if self.level_up_ready:
        return

# 新代码：
def trigger_levelup(self):
    """触发升级，随机选择 3 个不重复的增益"""
    # 如果已经处于等待升级状态，也应该生成新选项（用于连续升级的情况）
    # 只有当玩家还没选择时才会显示旧选项，但内部upgrade_choice应该每次都更新
```

**效果**：每次调用 `trigger_levelup()` 都会生成新的卡牌组合

### 修改2：加强 main.py 中的升级选项同步

**文件**：`main.py` 第1928-1940行

```python
# 旧代码：
if new_level > prev_level and player.upgrade_manager and player.upgrade_manager.level_up_ready:
    levelup_ready = True
    upgrade_options = player.upgrade_manager.upgrade_choice

# 新代码：
if new_level > prev_level and player.upgrade_manager:
    # 确保upgrade_choice已生成
    if not player.upgrade_manager.upgrade_choice:
        player.upgrade_manager.trigger_levelup()
    
    if player.upgrade_manager.level_up_ready and player.upgrade_manager.upgrade_choice:
        levelup_ready = True
        upgrade_options = player.upgrade_manager.upgrade_choice.copy() if player.upgrade_manager.upgrade_choice else []
        upgrade_selected = 0
        sound_mgr.play("levelup")
        # ... 其他代码
```

**效果**：
- 显式确保 `upgrade_choice` 已生成
- 使用 `.copy()` 创建独立副本，避免引用问题
- 更安全的检查逻辑

## 测试结果

运行 `test_upgrade_diversity.py` 后的结果：

```
第 1 次升级：钛金装甲、斩杀协议、强力磁场
第 2 次升级：钛金装甲、偏导护盾、强力磁场 ✓ 不同
第 3 次升级：鹰眼瞄准、火力强化、极速装填 ✓ 不同
第 4 次升级：斩杀协议、极速装填、火力强化 ✓ 不同
第 5 次升级：鹰眼瞄准、活性装甲、强力磁场 ✓ 不同

✅ 通过：所有 5 次升级都生成了不同的卡牌组合
```

## 数据流验证

修复前后的数据流对比：

### 修复前（有问题）
```
升级1: generate_choice() → ['buff1', 'buff2', 'buff3']
升级2: early_return() → 复用 ['buff1', 'buff2', 'buff3'] ❌
升级3: early_return() → 复用 ['buff1', 'buff2', 'buff3'] ❌
```

### 修复后（正常）
```
升级1: generate_choice() → ['buff1', 'buff2', 'buff3']
升级2: generate_choice() → ['buff4', 'buff5', 'buff6'] ✓
升级3: generate_choice() → ['buff7', 'buff8', 'buff9'] ✓
```

## 后续验证

✅ 代码编译无误
✅ 模块导入成功
✅ 升级卡牌多样性测试通过
✅ 游戏运行正常

## 相关文件

- `roguelite.py` - UpgradeManager 类
- `main.py` - 升级UI显示逻辑
- `test_upgrade_diversity.py` - 多样性验证脚本（新增）
