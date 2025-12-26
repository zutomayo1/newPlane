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

---

## Bug #007: 技能效果渲染在屏幕左侧而非玩家位置

### 问题描述
HEAVY METAL 机体的所有技能效果（Q/E/R/F/G/C）都渲染在屏幕左侧，而不是跟随玩家位置。

### 具体表现
- 用户操作 HEAVY METAL 机体，玩家在屏幕中央偏右位置
- 按下技能键后，视觉效果全部出现在屏幕左边 1/3 区域
- 效果看起来与玩家完全脱节

### 根本原因
**屏幕尺寸硬编码不匹配**：

游戏实际屏幕尺寸为 `1280 x 720`（在 config.py 中定义），但 `heavymetal_bullets.py` 中所有技能效果的 Surface 都硬编码为 `480 x 640`：

```python
# 问题代码 - 使用错误的硬编码尺寸
self.image = pygame.Surface((480, 640), pygame.SRCALPHA)
self.rect = self.image.get_rect(topleft=(0, 0))
```

这导致：
1. 全屏 Surface 只覆盖屏幕左边 480 像素（实际需要 1280）
2. 玩家在 `WIDTH/2 = 640` 位置时，已超出 480 的范围
3. 效果在 Surface 上按 `self.x, self.y` 绘制，但 Surface 本身位置错误

### 影响范围
- `DeathMetalSolo` - R键技能
- `DeathMetalSoloUlt` - F键大招
- `EchoWallSkill` - G键技能
- `HellishOpenerSkill` - C键技能
- `PowerChordWave` - Q键技能（中心偏移问题）
- 所有相关渲染代码中的硬编码坐标（240, 320, 430, 440, 600 等）

### 解决方案

1. **导入实际屏幕尺寸**：
```python
from config import all_sprites, bullets, mobs, enemy_bullets, WIDTH, HEIGHT
```

2. **修改所有全屏 Surface 创建**：
```python
# 修复后 - 使用实际屏幕尺寸
self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
self.rect = self.image.get_rect(topleft=(0, 0))
```

3. **修改所有硬编码坐标**：
```python
# 聚光灯位置
spotlight_x = WIDTH // 2 + int(WIDTH * 0.15 * math.sin(spot_phase))
spotlight_y = HEIGHT // 2 + int(HEIGHT * 0.15 * math.cos(spot_phase * 0.7))

# EQ条形图
bar_x = int(i * (WIDTH / eq_count))
bar_y = HEIGHT - bar_height  # 底部

# 边缘效果
pygame.draw.rect(self.image, color, (0, 0, WIDTH, HEIGHT), 12)

# 边界检查
if self.y > HEIGHT + 50 or self.x > WIDTH + 50:
    self.kill()

# 敌人位置限制
enemy.rect.x = max(0, min(WIDTH - 40, enemy.rect.x))
enemy.rect.y = max(0, min(HEIGHT - 40, enemy.rect.y))
```

4. **修复 PowerChordWave 尺寸计算**：
```python
# 基于实际半径动态计算 Surface 尺寸
surf_size = self.max_radius * 2 + 100
self.image = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
self.rect = self.image.get_rect(center=(int(x), int(y)))

# 渲染时使用动态中心
cx, cy = surf_size // 2, surf_size // 2
```

### 预防措施

1. **永远不要硬编码屏幕尺寸**：
   ```python
   # ❌ 错误
   self.image = pygame.Surface((480, 640), pygame.SRCALPHA)
   
   # ✅ 正确
   from config import WIDTH, HEIGHT
   self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
   ```

2. **全屏效果检查清单**：
   - [ ] Surface 尺寸是否使用 WIDTH, HEIGHT？
   - [ ] 渲染坐标是否使用 WIDTH/2, HEIGHT/2 作为中心？
   - [ ] 边界检查是否使用 WIDTH, HEIGHT？
   - [ ] 循环范围是否使用 WIDTH, HEIGHT？

3. **新建技能效果类模板**：
   ```python
   class NewFullScreenSkill(pygame.sprite.Sprite):
       def __init__(self, x, y, ...):
           super().__init__()
           self.x = x
           self.y = y
           # 全屏效果必须使用 WIDTH, HEIGHT
           self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
           self.rect = self.image.get_rect(topleft=(0, 0))
   ```

### 相关文件
- `utils/bullets/heavymetal_bullets.py` - 所有技能类
- `config.py` - WIDTH=1280, HEIGHT=720 定义

### 修复日期
2025年12月19日

---

## Bug #008: 技能击杀敌人不增加击杀数、得分和经验

### 问题描述
使用技能（如天顶的棱镜折射、喵星人轰炸等）击杀敌人后，击杀数不增加、得分不增加、也不掉落经验球和物品。

### 具体表现
- 用户使用技能击杀敌人
- 敌人正常死亡消失
- 但击杀计数器不变
- 得分不增加
- 没有经验球掉落
- 没有物品掉落
- 成就系统不记录击杀

### 根本原因
**技能伤害和子弹伤害走不同的死亡处理路径**

游戏中有两种击杀敌人的方式：
1. **子弹碰撞**：在 `main.py` 的子弹碰撞检测中，直接检查 `m.hp <= 0`，然后处理所有奖励逻辑
2. **技能伤害**：调用敌人的 `take_damage()` 方法

问题在于 `enemies.py` 中的 `take_damage()` 方法：

```python
def take_damage(self, damage):
    self.hp -= damage
    if self.hp <= 0:
        self.on_death()  # 直接调用 on_death
        return False
    return True

def on_death(self):
    # 处理分裂等特殊能力...
    self.kill()  # 直接销毁，没有任何奖励逻辑！
```

当技能通过 `take_damage()` 杀死敌人时：
- 敌人直接在 `on_death()` 中被 `kill()` 移除
- **完全绕过了 main.py 中的奖励逻辑**
- 导致击杀数、得分、经验、物品等全部丢失

### 解决方案

在 `main.py` 的 `all_sprites.update()` 之后，添加统一的死亡敌人检测循环：

```python
all_sprites.update()

# 【修复】检测被技能杀死的敌人
for m in list(mobs):
    if m.hp <= 0 and not getattr(m, '_death_rewarded', False):
        m._death_rewarded = True  # 标记已处理，防止重复
        
        # 加分
        score += 100 if m.is_elite else 20
        
        # 记录击杀
        player.stats['kills'] += 1
        player.stats['current_combo'] += 1
        # ... 其他奖励逻辑
        
        # 经验掉落
        ExperienceOrb(m.rect.centerx, m.rect.centery, xp_amount)
        
        # 物品掉落
        if item_manager:
            item_manager.try_spawn_drop(m.rect.centerx, m.rect.centery)
        
        m.kill()
```

同时，在原有的子弹碰撞死亡处理和毒杀死亡处理中添加 `_death_rewarded` 标记，防止重复奖励。

### 预防措施

1. **统一死亡处理入口**：
   - 所有导致敌人死亡的方式都应该经过同一个奖励处理逻辑
   - 不要在多个地方重复实现奖励逻辑

2. **敌人死亡设计原则**：
   ```python
   # ❌ 错误：敌人自己处理死亡
   def take_damage(self, damage):
       self.hp -= damage
       if self.hp <= 0:
           self.kill()  # 直接销毁，奖励丢失
   
   # ✅ 正确：只标记死亡，让主循环统一处理
   def take_damage(self, damage):
       self.hp -= damage
       # 不要在这里 kill()，让主循环检测 hp <= 0 并处理奖励
   ```

3. **使用标记防止重复处理**：
   ```python
   if m.hp <= 0 and not getattr(m, '_death_rewarded', False):
       m._death_rewarded = True
       # 处理奖励...
   ```

4. **检查清单**：
   - [ ] 新增的伤害方式是否会绕过主循环的死亡检测？
   - [ ] 是否有在敌人类内部直接调用 `kill()` 的情况？
   - [ ] 奖励逻辑是否只在一个地方实现？

### 相关文件
- `main.py` - 第8135行后添加死亡检测循环
- `main.py` - 第8936行子弹碰撞死亡处理添加标记
- `main.py` - 第8338行毒杀死亡处理添加标记
- `enemies.py` - `take_damage()` 和 `on_death()` 方法

### 修复日期
2025年12月20日

---

## Bug #009: 普通模式敌人只刷新一批后停止

### 问题描述
普通模式开局后，敌人刷新一批到12个后就再也不刷新了，即使玩家击杀敌人场上也不再有新敌人出现。

### 具体表现
- 游戏开始后敌人正常刷新到上限（12个）
- 击杀敌人后，场上敌人数量不变或只减少不增加
- 调试日志显示 `mobs=12, allowed=0` 持续数分钟不变

### 根本原因
**Enemy类缺少边界检测**：敌人飞出屏幕后不会被移除，导致 `mobs` 精灵组一直保持满员状态。

`Enemy.update()` 方法中没有边界检测代码：
```python
def update(self) -> None:
    # ... 移动和攻击逻辑 ...
    self._apply_behavior(effective_dt)
    self._apply_dynamic_effects()
    self._apply_support_auras()
    self._maybe_attack()
    # ❌ 没有边界检测，敌人飞出屏幕后仍然存在于 mobs 组中
```

而 `EnemyBullet` 类有正确的边界检测：
```python
def update(self) -> None:
    # ...
    if (self.rect.right < -40 or self.rect.left > WIDTH + 40 ...):
        self.kill()  # ✅ 飞出屏幕后移除
```

刷怪逻辑检查 `allowed = max_cap - len(mobs)`，由于敌人不会被移除，`len(mobs)` 永远是12，`allowed` 永远是0，导致不再刷新。

### 解决方案
在 `Enemy.update()` 方法末尾添加边界检测：

```python
def update(self) -> None:
    # ... 原有逻辑 ...
    self._apply_behavior(effective_dt)
    self._apply_dynamic_effects()
    self._apply_support_auras()
    self._maybe_attack()

    # 边界检测：飞出屏幕的敌人自动移除
    if (
        self.rect.top > HEIGHT + 100
        or self.rect.bottom < -100
        or self.rect.left > WIDTH + 100
        or self.rect.right < -100
    ):
        self.kill()
```

### 附加问题
调试过程中还发现敌人生成代码的缩进错误，导致刷怪逻辑位于错误的代码块外：
- 敌人生成代码（第9310行）缩进为20空格
- 应该位于 `else:` (非 `levelup_paused`) 分支内（24空格）

这导致刷怪逻辑虽然每帧执行，但处于错误的上下文中。修复后将其缩进增加4空格。

### 预防措施
1. **所有移动实体都应有边界检测**：敌人、子弹、道具等飞出屏幕后必须移除
2. **检查清单**：
   - [ ] 新增的敌人类型是否继承了正确的边界检测？
   - [ ] 移动逻辑是否会导致实体永远留在屏幕外？
   - [ ] 精灵组的数量是否会正常增减？

3. **调试建议**：遇到"不刷新"问题时，优先检查：
   - 刷怪条件是否满足（`allowed > 0`）
   - 计时器是否正常递增/重置
   - 已有实体是否正常移除

### 相关文件
- `enemies.py` - `Enemy.update()` 方法（第2757-2764行）
- `main.py` - 敌人生成逻辑（第9310-9365行）

### 修复日期
2025年12月22日
---

## Bug #010: 字体渲染异常导致变量未定义错误

### 问题描述
成就界面点击某个成就查看详情时，控制台报错 `NameError: name 'quote_right' is not defined`，但代码中 `quote_right` 明明在使用前一行就定义了。

### 游戏表现
- 用户进入成就界面，点击左侧的某个成就徽章
- **界面卡死**，无法操作，无法返回主菜单
- 成就详情面板没有显示任何内容
- 必须强制关闭游戏才能退出

### 具体表现
- 用户进入成就界面，点击某个成就徽章
- 控制台报错：
  ```
  NameError: name 'quote_right' is not defined
  Traceback (most recent call last):
    File "main.py", line 4906, in _draw_achievements_ui_inner
      screen.blit(quote_right, (px + 25 + desc_surf.get_width(), py - 8))
  ```
- 但查看代码，`quote_right` 在第4905行定义，第4906行使用，逻辑上不应该未定义

### 根本原因
**字体渲染异常导致赋值语句未完成**

问题代码：
```python
quote_right = quote_font.render(""", True, quote_color)  # 第4905行
screen.blit(quote_right, ...)  # 第4906行 - 报 NameError
```

真正的问题在第4905行：`quote_font.render(""", ...)` 渲染中文右引号 `"` 时抛出了异常。

由于异常发生在赋值表达式的**右侧**（`render()` 调用），赋值操作没有完成，`quote_right` 变量从未被创建。当执行到第4906行时，Python 报告 `NameError`。

这是一个**误导性错误**：
- Python 报告的错误位置是第4906行（使用变量的地方）
- 但实际出错的是第4905行（`render()` 调用失败）

可能的渲染失败原因：
1. SimHei 字体可能无法正确渲染特殊的中文引号字符 `"`
2. 字体对象在某些情况下状态异常

### 解决方案
移除引号装饰代码，简化描述区域渲染：

```python
# 修复前（问题代码）
quote_font = get_ach_font("SimHei", 28)
quote_color = (80, 85, 100)
quote_left = quote_font.render(""", True, quote_color)
screen.blit(quote_left, (px - 5, py - 8))
desc_surf = desc_font.render(desc_text, True, (190, 195, 210))
screen.blit(desc_surf, (px + 20, py + 5))
quote_right = quote_font.render(""", True, quote_color)  # ← 这里失败
screen.blit(quote_right, (px + 25 + desc_surf.get_width(), py - 8))

# 修复后（简化版）
desc_surf = desc_font.render(desc_text, True, (190, 195, 210))
screen.blit(desc_surf, (px + 5, py + 5))
```

### 预防措施
1. **避免使用特殊Unicode字符进行渲染**：中文引号 `"` `"` 等特殊字符可能在某些字体中不支持
2. **字体渲染应使用 try-except 包裹**：
   ```python
   try:
       surf = font.render(text, True, color)
   except Exception:
       surf = fallback_font.render("?", True, color)  # 降级处理
   ```
3. **注意"误导性错误"**：当看到 `NameError: name 'xxx' is not defined`，但 `xxx` 明明在上一行定义时，检查上一行的表达式是否可能抛出异常
4. **赋值语句右侧的函数调用失败会导致变量未创建**：
   ```python
   x = some_function()  # 如果 some_function() 抛异常，x 不会被创建
   print(x)  # NameError: name 'x' is not defined
   ```

### 相关文件
- `main.py` - `_draw_achievements_ui_inner()` 函数，成就详情描述区域渲染

### 修复日期
2025年12月23日

---

## Bug #011: 排行榜缓存渐变函数索引越界导致界面卡死

### 问题描述
点击排行榜界面后，游戏立即卡死无响应。

### 具体表现
- 用户从主菜单点击"排行榜"按钮
- 游戏窗口立即卡死，无法操作
- 需要强制关闭程序

### 根本原因
**渐变缓存函数参数处理错误**：`_get_lb_gradient()` 函数假设 `colors` 参数始终有两个颜色，但实际调用时只传入了单个颜色。

```python
# 问题代码
def _get_lb_gradient(key, width, height, colors, alpha_range=(255, 0)):
    # ...
    r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)  # colors[1] 越界！
    g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
    b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
```

调用处传入单色：
```python
# 只传了一个颜色
panel_bg = _get_lb_gradient("panel_bg", width, height, [(15, 18, 28)], (220, 100))
```

当 `colors = [(15, 18, 28)]` 时，访问 `colors[1]` 会抛出 `IndexError`，但由于异常未被捕获，导致整个渲染循环阻塞。

### 修复方案
添加对单色情况的兼容处理：

```python
# 修复后
def _get_lb_gradient(key, width, height, colors, alpha_range=(255, 0)):
    cache_key = (key, width, height)
    if cache_key not in _leaderboard_cache["gradient_surfaces"]:
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        # 处理单色或双色情况
        color1 = colors[0]
        color2 = colors[1] if len(colors) > 1 else colors[0]  # 兼容单色
        for y in range(height):
            ratio = y / height if height > 0 else 0
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            alpha = int(alpha_range[0] * (1 - ratio) + alpha_range[1] * ratio)
            pygame.draw.line(surf, (r, g, b, alpha), (0, y), (width, y))
        _leaderboard_cache["gradient_surfaces"][cache_key] = surf
    return _leaderboard_cache["gradient_surfaces"][cache_key]
```

### 预防措施
1. **函数参数应有默认值或边界检查**：当参数是列表时，访问索引前应检查长度
2. **缓存函数的首次调用尤其危险**：因为缓存未命中时才会执行可能出错的代码
3. **性能优化时要充分测试**：缓存系统引入后，原本正常的代码路径可能因参数传递问题出错
4. **使用防御性编程**：
   ```python
   # 好的做法
   color2 = colors[1] if len(colors) > 1 else colors[0]
   # 或者
   color2 = colors[-1]  # 取最后一个元素
   ```

### 相关文件
- `main.py` - `_get_lb_gradient()` 函数，排行榜渐变缓存
- `main.py` - `draw_leaderboard_ui()` 函数，调用渐变缓存

### 修复日期
2025年12月23日

---

## Bug #012: 涂装界面性能优化导致函数命名冲突

### 问题描述
为涂装界面添加字体缓存优化后，游戏启动后直接黑屏，无法显示任何内容。

### 具体表现
- 游戏窗口打开后完全黑屏
- 没有报错信息
- 无法进入主菜单

### 根本原因
**函数命名冲突**：在 `main.py` 中创建了一个新的字体缓存函数 `get_font(name, size)`，但这个名称与 `utils/ui.py` 中已导入的 `get_font(size, bold=False)` 函数冲突。

`utils/ui.py` 中的原始函数：
```python
def get_font(size, bold=False):
    font_names = ["roboto", "noto sans", "microsoftyahei", "simhei", "arial"]
    return pygame.font.SysFont(font_names, int(size), bold=bold)
```

新添加的缓存函数覆盖了导入的函数：
```python
def get_font(name, size):  # 错误：与导入的函数同名
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(name, size)
    return _font_cache[key]
```

在主菜单 `draw_menu_ui()` 中调用：
```python
title_font = get_font(int(60 * scale), bold=True)
```

由于函数签名不匹配：
- 原函数期望 `(size, bold=False)`
- 新函数期望 `(name, size)`
- 结果：`name` 参数接收到数字 `60`，导致字体创建失败

### 解决方案
将新的缓存函数改名为 `get_cached_font()`，避免与原有函数冲突：
```python
def get_cached_font(name, size):
    """获取缓存的字体对象（全局通用）"""
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(name, size)
    return _font_cache[key]
```

同时更新所有调用处使用新名称。

### 预防措施
1. **创建新函数前检查命名冲突**：搜索代码库确认函数名未被使用
2. **注意导入的函数**：模块级别定义的函数会覆盖 `from xxx import *` 导入的同名函数
3. **使用更具体的函数名**：如 `get_cached_font` 比 `get_font` 更不容易冲突
4. **测试性能优化代码**：即使语法正确，运行时也可能因函数覆盖产生意外行为

### 相关文件
- `main.py` - `get_cached_font()` 函数定义（第238行）
- `utils/ui.py` - 原始 `get_font()` 函数（第12行）
- `main.py` - `draw_menu_ui()` 中的调用（第1420行）

### 修复日期
2025年12月23日

---

## Bug #013: 涂装界面Emoji显示错误

### 问题描述
涂装界面解锁按钮中的💎（钻石）emoji 显示为方块或乱码。

### 具体表现
- 解锁按钮显示 "□ 100" 而不是 "💎 100"
- 战机涂装和僚机涂装界面都有此问题

### 根本原因
使用 `SimHei` 字体渲染包含 emoji 的文本，但 `SimHei` 字体不支持 emoji 字符。

问题代码：
```python
btn_font = pygame.font.SysFont("SimHei", 13)
btn_text = btn_font.render(f"💎 {cost}", True, GOLD)  # SimHei 无法渲染 💎
```

### 解决方案
将 emoji 和文本分开渲染，emoji 使用 `Segoe UI Emoji` 字体：
```python
emoji_f = get_cached_font("Segoe UI Emoji", 12)
text_color = GOLD if can_afford else (120, 100, 100)
gem_surf = emoji_f.render("💎", True, text_color)
cost_surf = font_13.render(f" {cost}", True, text_color)
# 计算总宽度后居中显示
total_w = gem_surf.get_width() + cost_surf.get_width()
start_x = btn_rect.centerx - total_w//2
screen.blit(gem_surf, (start_x, btn_rect.centery - gem_surf.get_height()//2))
screen.blit(cost_surf, (start_x + gem_surf.get_width(), btn_rect.centery - cost_surf.get_height()//2))
```

### 预防措施
1. **Emoji 必须使用专用字体**：Windows 上使用 `Segoe UI Emoji`
2. **混合内容分开渲染**：emoji 用 emoji 字体，文本用中文字体
3. **创建 UI 时考虑字体兼容性**：设计阶段就规划好哪些地方需要 emoji

### 相关文件
- `main.py` - `draw_plane_customization_ui()` 函数（第6780行附近）
- `main.py` - `draw_wingman_customization_ui()` 函数（第7260行附近）

### 修复日期
2025年12月23日

---

## Bug #014: 天赋树界面卡死

### 问题描述
点击天赋树（星轨天赋阵）按钮后，画面直接卡死，无法操作。

### 具体表现
- 从主菜单点击天赋树按钮
- 画面冻结，无法响应任何输入
- 必须强制关闭程序

### 根本原因
**每帧渐变循环未缓存**：`draw_talent_tree_ui()` 函数中存在多处 `for y in range(height)` 循环用于绘制渐变效果，每帧执行导致严重性能问题。

问题代码示例：
```python
# 主背景 - 每帧700次循环
for y in range(HEIGHT):
    pygame.draw.line(bg, color, (0, y), (WIDTH, y))

# 面板背景 - 每帧400+次循环
for ty in range(tree_rect.height):
    pygame.draw.line(tree_bg, color, (0, ty), (tree_rect.width, ty))

# 信息面板、核心区域、弹出窗口等也有类似循环
```

此问题与 Bug #011（排行榜界面卡死）完全相同。

### 解决方案
参照排行榜的缓存模式，创建静态Surface缓存：

```python
# 缓存字典
_talent_tree_cache = {
    "bg_surface": None,
    "bg_size": (0, 0),
    "gradient_surfaces": {},
}

# 主背景缓存
def _get_talent_tree_background():
    if _talent_tree_cache["bg_surface"] is None:
        bg = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            # ... 渐变绘制（只执行一次）
        _talent_tree_cache["bg_surface"] = bg
    return _talent_tree_cache["bg_surface"]

# 通用渐变缓存
def _get_tt_gradient(key, width, height, colors, alpha=235):
    cache_key = (key, width, height)
    if cache_key not in _talent_tree_cache["gradient_surfaces"]:
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        # ... 渐变绘制（只执行一次）
        _talent_tree_cache["gradient_surfaces"][cache_key] = surf
    return _talent_tree_cache["gradient_surfaces"][cache_key]
```

替换所有渐变循环为缓存调用：
```python
# 主背景
screen.blit(_get_talent_tree_background(), (0, 0))

# 各面板背景
tree_bg = _get_tt_gradient("tree_panel", tree_rect.width, tree_rect.height, [(13, 15, 20), (18, 20, 25)])
info_bg = _get_tt_gradient("info_panel", info_rect.width, info_rect.height, [(10, 12, 15), (18, 20, 23)])
core_bg = _get_tt_gradient("core_area", core_area_w, core_area_h, [(12, 11, 9), (18, 17, 15)])
```

### 缓存的区域
1. ✅ 主背景 (`_get_talent_tree_background`)
2. ✅ 标题面板渐变
3. ✅ 天赋树主面板渐变
4. ✅ 信息面板渐变
5. ✅ 核心区域渐变
6. ✅ 返回/重置按钮渐变
7. ✅ 弹出窗口背景渐变
8. ✅ 核心选项卡片渐变

### 预防措施
1. **禁止在每帧函数中使用大循环**：任何 `for y in range(height)` 都应该缓存
2. **新UI参考已有缓存模式**：排行榜(`_get_lb_background`)、个性化菜单(`_personalization_cache`)
3. **渐变效果必须预渲染**：使用 `pygame.Surface` 预渲染后 `blit`

### 相关文件
- `main.py` - `_talent_tree_cache` 缓存字典（第172行）
- `main.py` - `_get_talent_tree_background()` 函数（第178行）
- `main.py` - `_get_tt_gradient()` 函数（第191行）
- `main.py` - `draw_talent_tree_ui()` 函数（第2991行）

### 相关Bug
- Bug #011: 排行榜界面卡死（相同原因，相同解决方案）

### 修复日期
2025年12月23日