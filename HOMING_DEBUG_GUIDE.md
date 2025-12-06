# 追踪卡牌调试指南

## 问题描述
用户反馈追踪卡牌没有效果

## 已添加的调试代码

### 1. 射击时追踪值诊断 (sprites.py:8917-8921)
```python
# 【调试】追踪卡牌诊断
if hasattr(self, 'has_homing') or hasattr(self, 'homing_strength'):
    print(f"[追踪诊断] has_homing={getattr(self, 'has_homing', False)}, homing_strength={getattr(self, 'homing_strength', 0)}, homing_value={homing_value}")
```

### 2. 卡牌效果应用诊断 (roguelite.py:1377-1385)
```python
print(f"[卡牌效果] 应用追踪卡牌: has_homing=True, homing_strength={player.homing_strength}")
```

## 测试步骤

1. 运行游戏:
   ```powershell
   python main.py
   ```

2. 开始游戏,选择任意飞机

3. 击杀敌人升级,在卡牌选择界面查找以下卡牌:
   - 带有"追踪模块"修饰器的卡牌
   - 或者任何基础卡牌+追踪模块

4. 选择追踪卡牌后,观察控制台输出:
   - 应该看到`[卡牌效果] 应用追踪卡牌...`
   - 记录`homing_strength`的值

5. 射击时观察控制台:
   - 应该看到`[追踪诊断]`输出
   - 检查`homing_value`是否>0

6. 观察子弹行为:
   - 子弹应该是绿色(HOMING_COLOR)
   - 子弹应该会追踪最近的敌人

## 预期结果

### 正常情况
```
[卡牌效果] 应用追踪卡牌: has_homing=True, homing_strength=0.5
[追踪诊断] has_homing=True, homing_strength=0.5, homing_value=0.5
```
子弹应该追踪敌人

### 异常情况

#### 情况1: 卡牌效果未应用
```
(没有[卡牌效果]输出)
```
**原因**: 卡牌系统没有调用`_apply_card_to_player`
**解决**: 检查`add_card`或升级流程

#### 情况2: homing_value为0
```
[卡牌效果] 应用追踪卡牌: has_homing=True, homing_strength=0.5
[追踪诊断] has_homing=True, homing_strength=0.5, homing_value=0.0
```
**原因**: `_fire_main_gun`中的条件判断有问题
**解决**: 检查`getattr(self, 'has_homing', False)`

#### 情况3: 子弹homing属性为0
```
[追踪诊断] has_homing=True, homing_strength=0.5, homing_value=0.5
```
但子弹不追踪
**原因**: Bullet构造函数或update方法问题
**解决**: 检查Bullet(homing=homing_value)传递和self.homing>0判断

## 追踪系统架构

```
卡牌系统 (roguelite.py)
  └─> _apply_card_to_player()
       └─> player.has_homing = True
       └─> player.homing_strength = 0.5

玩家射击 (sprites.py:Player._fire_main_gun)
  └─> homing_value = homing_strength if has_homing else 0
       └─> Bullet(..., homing=homing_value)

子弹追踪 (sprites.py:Bullet.update)
  └─> if self.homing > 0:
       └─> 寻找最近敌人
       └─> lerp_strength = min(self.homing * 3, 0.95)
       └─> self.vel = self.vel.lerp(target_vec, lerp_strength)
```

## 可能的问题点

1. **卡牌类型错误**: "homing_addon"应该是modifier type
2. **effect计算错误**: `_calculate_effect`可能没有正确合并modifier效果
3. **条件判断错误**: `effect["homing"]`可能不是truthy值
4. **属性名错误**: 使用了`has_homing`但检查的是其他属性
5. **Bullet构造参数**: homing参数没有正确传递

## 下一步

根据控制台输出确定具体是哪个环节出问题,然后针对性修复。
