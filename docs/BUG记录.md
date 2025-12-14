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
