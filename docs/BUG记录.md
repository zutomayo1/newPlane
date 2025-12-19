# 霓虹深空 Bug 记录文档

记录开发过程中遇到的典型 Bug，便于后续参考和避免类似问题。

---

## 开发规范

### 变量命名规范

为避免类似 Bug #001 的命名冲突问题，制定以下命名规范：

#### 涂装ID命名
| 类型 | 前缀格式 | 示例 |
|------|---------|------|
| 机体涂装 | `{机体名}_{涂装名}` | `crystalfall_void` |
| 子弹涂装 | `{机体名}_bullet_{涂装名}` | `crystalfall_bullet_void` |
| 尾迹涂装 | `{机体名}_trail_{涂装名}` | `crystalfall_trail_void` |

> **注意**：此规范仅适用于**新增**的涂装ID，现有涂装ID保持不变。

#### 函数参数命名
- 布尔类型参数使用 `is_` 或 `has_` 前缀：`is_bullet`, `is_unlocked`, `has_effect`
- 类型标识参数明确指定：`theme_type="bullet"` 而非依赖自动判断

#### 字典键命名
- 不同类型的数据使用不同的字典，避免ID冲突
- 若必须共用字典，使用复合键：`("bullet", "crystalfall_void")`

---

## Bug #001: 涂装ID命名冲突导致装备失败

### 问题描述
点击机体涂装的"装备"按钮后，显示"涂装已装备"，但实际UI上涂装没有变化，预览也没有更新。

### 具体表现
- 用户选择 Crystalfall 机体，点击专属涂装 `crystalfall_void` 的装备按钮
- 控制台显示 `equip_theme 返回: success=True, msg=涂装已装备`
- 但 UI 仍然显示之前的涂装（如 `crystalfall_quartz`）
- `get_equipped_theme()` 返回的不是刚装备的涂装

### 根本原因
**涂装ID命名冲突**：同一个ID（如 `crystalfall_void`）同时存在于两个不同的字典中：
- `PAINT_THEMES`（机体涂装，第7355行）
- `BULLET_THEMES`（子弹涂装，第10430行）

`equip_theme()` 函数使用以下逻辑判断涂装类型：
```python
# 问题代码：仅通过字典包含关系判断，易产生冲突
is_bullet_theme = theme_id in BULLET_THEMES
```

由于 `crystalfall_void` 同时存在于两个字典，`theme_id in BULLET_THEMES` 返回 `True`，导致：
- 机体涂装被错误地保存到 `equipped_bullet_themes` 字典
- 而 `get_equipped_theme()` 查询的是 `equipped_themes` 字典
- 结果显示不一致

### 解决方案
1. **修改 `equip_theme()` 函数**，增加 `bullet` 参数明确指定涂装类型：
```python
def equip_theme(self, plane_id, theme_id, bullet=None):
    if bullet is None:
        # 优先检查是否为机体涂装，避免命名冲突时错误识别
        if theme_id in PAINT_THEMES:
            is_bullet = False
        elif theme_id in BULLET_THEMES:
            is_bullet = True
        else:
            return False, "涂装不存在"
    else:
        is_bullet = bullet
```

2. **修改调用处**，传递明确的 `bullet` 参数：
```python
success, msg = customization_manager.equip_theme(
    customization_selected_plane, 
    theme_id, 
    bullet=is_bullet  # 从UI点击处已知是机体还是子弹涂装
)
```

### 预防措施
1. **避免命名冲突**：不同类型的涂装使用不同的命名前缀
   - 机体涂装：`plane_crystalfall_void`
   - 子弹涂装：`bullet_crystalfall_void`

2. **或者在函数调用时始终明确类型**：不依赖自动判断，总是传递明确的类型参数

### 相关文件
- `customization.py` - `equip_theme()` 函数
- `main.py` - `handle_plane_customization_click()` 函数

### 修复日期
2025年12月13日

---

## Bug #002: 模块导出类名不匹配导致涂装界面卡死

### 问题描述
在涂装界面点击子弹选项时，整个界面卡死无响应。

### 具体表现
- 用户进入涂装界面，选择史莱姆机体
- 点击子弹涂装选项
- 界面完全卡死，无法操作
- 无错误提示，程序无响应

### 根本原因
**模块导出与实际类名不匹配**：在重写史莱姆机体的三个终极技能后，类名发生了变化，但 `utils/bullets/__init__.py` 中的导出语句没有同步更新。

旧类名（已删除）：
- `StarGelRainSkill`
- `GravityVortexSkill`
- `ApocalypseStarfallSkill`
- `ApocalypseDomain`

新类名（实际存在）：
- `StarStompSkill`
- `AstralCrystalSkill`
- `AureusSpawnSkill`

当涂装界面尝试加载 bullets 模块时，Python 抛出 `ImportError`：
```
ImportError: cannot import name 'StarGelRainSkill' from 'utils.bullets.slime_bullets'
```

由于导入失败发生在模块加载阶段，错误没有被正确捕获，导致界面卡死。

### 解决方案
更新 `utils/bullets/__init__.py` 中的导出语句，使用正确的类名：

```python
# 修复前（错误）
from .slime_bullets import (SLIME_BULLET_THEMES, StarGelBullet, GravityDomain, 
                            MiniStarGelBullet, GelCoreBullet, StarGelPickup,
                            StarGelRainSkill, GravityVortexSkill, 
                            ApocalypseStarfallSkill, ApocalypseDomain)

# 修复后（正确）
from .slime_bullets import (SLIME_BULLET_THEMES, StarGelBullet, GravityDomain, 
                            MiniStarGelBullet, GelCoreBullet, StarGelPickup,
                            StarStompSkill, AstralCrystalSkill, AureusSpawnSkill,
                            StarSlimeDownEffect)
```

### 预防措施
1. **重命名类时同步更新所有引用**：使用 IDE 的"重命名符号"功能，或在重命名后全局搜索旧类名
2. **在 `__init__.py` 修改后测试导入**：运行 `python -c "from utils.bullets import *"` 验证导入成功
3. **添加模块加载的异常处理**：在涂装界面加载模块时使用 try-except，避免静默卡死

### 相关文件
- `utils/bullets/__init__.py` - 模块导出定义
- `utils/bullets/slime_bullets.py` - 史莱姆子弹类定义

### 修复日期
2025年12月14日

---

## Bug #003: 子弹渲染方法中变量作用域错误导致游戏画面卡死

### 问题描述
选择 Oro（维度吞噬者·神杀）机体后点击出击，游戏画面停留在选择机体界面，但游戏实际已经开始（能听到子弹发射声音）。

### 具体表现
- 用户选择 Oro 机体，点击"出击"按钮
- 控制台显示 `reset_game完成，切换到游戏状态`
- 画面仍停留在选择机体界面
- 但能听到子弹发射的声音，说明游戏逻辑已在运行
- 无错误信息输出到控制台（异常被静默吞掉）

### 根本原因
**变量作用域错误**：在 `VoidChainBullet._render()` 方法中，有一行代码被错误地放在了 `else` 块外面：

```python
# 问题代码位置：oro_bullets.py 第425行
        # 默认：链节形状
        else:
            ...
            core_r = 4 + int(abs(math.sin(t * 3)) * 2)
            pygame.draw.circle(self.image, pulse_col, (cx, cy), core_r)
        pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), core_r // 2)  # ← 错误！在else外面
```

当子弹类型为 beam、orb、missile 等非默认类型时：
1. 代码进入对应的 `if/elif` 分支
2. 不会进入 `else` 分支，因此 `core_r` 变量不会被定义
3. 但最后一行 `pygame.draw.circle(..., core_r // 2)` 仍会执行
4. 导致 `UnboundLocalError: cannot access local variable 'core_r'`

由于渲染异常发生在 sprite 的 `draw()` 方法内部，pygame 没有正确处理，导致：
- 游戏逻辑继续运行（能听到声音）
- 但渲染循环失败，画面不更新

### 解决方案
将该行代码移入 `else` 块内部：

```python
# 修复后
        else:
            ...
            core_r = 4 + int(abs(math.sin(t * 3)) * 2)
            pygame.draw.circle(self.image, pulse_col, (cx, cy), core_r)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), core_r // 2)  # ← 现在正确在else内部
```

### 预防措施
1. **检查多分支代码的缩进**：确保共用变量在所有分支中都有定义，或只在定义它的分支内使用
2. **添加渲染异常捕获**：在 sprite 的 `_render()` 方法中使用 try-except 包裹，避免单个 sprite 渲染失败导致整个游戏卡死
3. **单元测试渲染方法**：对每种子弹类型单独调用 `_render()` 测试，确保不会抛出异常
4. **代码审查时重点关注 if/elif/else 块后的代码**：确认是否应该在块内还是块外

### 相关文件
- `utils/bullets/oro_bullets.py` - `VoidChainBullet._render()` 方法，第266-425行

### 修复日期
2025年12月14日

---

## Bug 模板

### 问题描述
[简述问题现象]

### 具体表现
[详细描述复现步骤和观察到的现象]

### 根本原因
[分析问题的根本原因]

### 解决方案
[描述如何修复]

### 预防措施
[如何避免类似问题再次发生]

### 相关文件
[列出涉及的文件]

### 修复日期
[记录修复日期]

---

## Bug #004: Pygame Alpha值越界导致涂装渲染失败

### 问题描述
部分涂装在预览时显示为"红色圆圈"并一闪一闪，实际机体图形没有正确渲染。

### 具体表现
- 火山领主（turu_volcanic）涂装预览显示红色圆圈闪烁
- 黄金图鲁（turu_golden）涂装预览显示红色圆圈
- 克苏鲁深渊凝视（cthulhu_abyss）涂装预览显示红色圆圈闪烁
- 控制台无明显错误（错误被 pygame 静默处理或在特定帧才触发）

### 根本原因
**Alpha 值计算溢出**：pygame 的 `draw.circle()` 等函数要求颜色参数的 alpha 值必须在 0-255 范围内。当动态计算的 alpha 值超出范围时，pygame 抛出 `ValueError: invalid color argument`。

#### 问题代码示例

**turu_volcanic (火山领主)**:
```python
# 问题1: ring_alpha 最大可达 270 (120 + 4*25 + 1*50)
ring_alpha = int(120 + ring * 25 + eruption * 50)  # 当 ring=4, eruption=1

# 问题2: p_alpha 可能为负数
p_alpha = int((1.2 - p_age) * 220)  # 当 p_age ≈ 1.2 时
```

**turu_golden (黄金图鲁)**:
```python
# ring_alpha 最大可达 260 (200 + 3*20)
ring_alpha = int(200 + ring * 20)  # 当 ring=3
```

**cthulhu_abyss (深渊凝视)**:
```python
# 当 flicker=0.25, g=2 时: 15 - 30 = -15 (负数)
pygame.draw.circle(glow_surf, (*col, int(60 * flicker) - g * 15), ...)
```

### 解决方案
使用 `max(0, min(255, value))` 确保所有 alpha 值在有效范围内：

```python
# 修复后的代码
ring_alpha = min(255, int(120 + ring * 20 + eruption * 40))
p_alpha = max(0, min(255, int((1.2 - p_age) * 220)))
glow_alpha = max(0, min(255, int(60 * flicker) - g * 15))
if glow_alpha > 0:
    pygame.draw.circle(...)
```

### 预防措施
1. **Alpha 值计算规范**：所有动态计算的 alpha 值必须使用边界检查
   ```python
   alpha = max(0, min(255, calculated_alpha))
   ```

2. **代码审查清单**：检查所有涉及以下模式的代码
   - `int(base + variable * multiplier)` 可能超过 255
   - `int((max_value - variable) * multiplier)` 可能为负
   - `base - variable * step` 减法可能为负

3. **单元测试**：对每个涂装渲染函数进行多时间点测试
   ```python
   for t in [0.0, 0.1, 0.5, 0.8, 1.0, 2.0]:
       try:
           render_function(surface, t, pulse)
       except ValueError as e:
           print(f"t={t}: {e}")
   ```

### 相关文件
- `utils/planes/skins_turu.py`: _render_turu_volcanic, _render_turu_golden
- `utils/planes/skins_cthulhu.py`: draw_cthulhu_abyss

### 修复日期
2025年12月16日

---

## Bug #005: Pygame实心圆覆盖精细渲染

### 问题描述
MAGNUS机体（真理之书）在游戏中只显示为纯色圆形，2500+行的精细魔法书渲染完全看不到。

### 具体表现
- 用户选择MAGNUS机体，进入涂装界面或游戏
- 预览/游戏中只显示一个纯色圆形
- 调试日志显示渲染函数确实被调用（`render_magnus_plane` 正常执行）
- 控制台无报错
- 测试脚本统计显示有90000+像素被渲染，但最终图像仍是纯色圆

### 根本原因
**Pygame `draw.circle()` 缺省参数导致实心圆覆盖**

在 `skins_magnus.py` 文件末尾，存在一段"氛围光晕"代码：

```python
# 问题代码位置：skins_magnus.py 第2497-2502行
# ---------- 11.10 整体氛围光晕（最底层但最后绘制以混合） ----------
atmosphere_pulse = 0.4 + 0.2 * math.sin(t * 1.5) + 0.2 * math.sin(t * 2.3)
atmosphere_alpha = max(0, min(255, int(20 * atmosphere_pulse)))
atmosphere_radius = int(85 * scale)

pygame.draw.circle(surface, (*theme["crystal"], atmosphere_alpha),
                  (cx, cy), atmosphere_radius)  # ← 问题：画了一个 85*scale 大小的实心圆！
```

关键问题：
1. `pygame.draw.circle(surface, color, center, radius)` 不指定 `width` 参数时，默认画**实心圆**
2. 这个圆的半径是 `85 * scale`，几乎覆盖整个机体渲染区域
3. 虽然 alpha 值较低（约20），但在透明surface上会完全替换掉之前的像素

代码意图是画一个"氛围光晕"混合效果，但实际效果是用半透明实心圆覆盖了所有精细渲染。

### 解决方案
移除这个覆盖性的实心圆绘制，或改为环形：

```python
# 修复方案1：直接移除
# ---------- 11.10 整体氛围光晕（最底层但最后绘制以混合） ----------
# 注意：这个光晕应该非常透明，只是增加氛围感，不能覆盖主体
# 已移除实心圆绘制，因为它会覆盖掉所有细节渲染

return surface

# 修复方案2：如果需要光晕效果，画环形而非实心圆
# pygame.draw.circle(surface, color, center, radius, width=2)  # 指定 width 参数
```

### 预防措施
1. **Pygame draw.circle 参数检查**：
   - `pygame.draw.circle(surface, color, center, radius)` → **实心圆**
   - `pygame.draw.circle(surface, color, center, radius, width)` → **空心环**
   
2. **渲染顺序原则**：
   - 大面积填充（背景、光晕）应该**最先绘制**
   - 精细细节应该**最后绘制**
   - 避免在渲染函数末尾画大面积图形

3. **视觉测试规范**：
   - 重写渲染代码后，生成测试图片并**目视检查**
   - 不能仅依赖像素统计，因为覆盖图形也会产生大量像素

4. **代码审查清单**：
   ```python
   # 检查所有 pygame.draw.circle 调用
   # 确认是否需要指定 width 参数
   pygame.draw.circle(...)  # ← 检查：是否应该是空心环？
   ```

### 相关文件
- `utils/planes/skins_magnus.py` - `render_magnus_plane()` 函数末尾

### 修复日期
2025年12月18日
