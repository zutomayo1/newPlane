# 🎸 维那斯万岁·HEAVY METAL 开发记录

## 机体概述

| 属性 | 值 |
|------|-----|
| **机体ID** | heavymetal |
| **机体名称** | 维那斯万岁·HEAVY METAL |
| **机体类型** | 重型飞行吉他战舰 |
| **视觉风格** | 工业金属 + 黑暗哥特 + 舞台威压 |
| **HP** | 165 |
| **速度** | 4.4 |
| **伤害** | 32 |
| **主题色** | 紫色 (148, 0, 211) |

## 设计理念

HEAVY METAL是一架以电吉他为造型的重型战机，将摇滚乐的狂野与战斗的激情完美融合。整体设计强调：

1. **完整吉他造型** - Flying V琴身 + 琴颈 + 琴头全部可见
2. **倾斜动感** - 7度倾斜角增加视觉冲击力
3. **工业压迫感** - 厚重金属质感，拒绝花哨特效
4. **音乐元素** - 拾音器、琴弦、音箱等细节一应俱全

---

## 技能系统

### Q技能 - 强力和弦 (Power Chord Wave)
- **冷却时间**: 2秒 (120帧)
- **效果**: 90°扇形冲击波
- **功能**: 清除弹幕 + 击退敌人
- **视觉**: 紫色音波扩散

### E技能 - 舞台俯冲 (Stage Dive Meteor)
- **冷却时间**: 5秒 (300帧)
- **效果**: 火焰流星从天而降
- **伤害**: 200点
- **范围**: 150像素爆炸半径
- **视觉**: 燃烧的吉他坠落

### R技能 - 死亡金属独奏 (Death Metal Solo)
- **冷却时间**: 10秒 (600帧)
- **效果**: 全屏音波攻击
- **伤害**: 持续伤害
- **视觉**: 震撼的音波涟漪

---

## 12种涂装系统

### 涂装列表

| 编号 | 涂装ID | 名称 | 主色调 | 特色装饰 |
|------|--------|------|--------|----------|
| 1 | default | 死亡金属 | 纯黑 (5,5,8) | 骷髅图案 + 紫色闪电尾焰 |
| 2 | bloody | 血腥狂欢 | 鲜红 (120,15,15) | 血迹飞溅 + 滴血尾焰 |
| 3 | cyber | 电子蓝调 | 赛博蓝 (20,80,180) | 电路纹路 + 电弧尾焰 + LED灯带 |
| 4 | golden | 黄金圣歌 | 土豪金 (200,170,80) | 圣光光环 + 金色粒子 |
| 5 | psychedelic | 迷幻紫雾 | 荧光紫 (160,50,200) | 漩涡图案 + 波纹尾焰 |
| 6 | toxic | 核废料 | 荧光绿 (50,200,50) | 辐射符号 + 毒雾尾焰 |
| 7 | frost | 冰封圣咏 | 冰蓝白 (180,220,255) | 冰晶图案 + 冰霜粒子 |
| 8 | hellfire | 地狱烈焰 | 熔岩橙 (220,100,20) | 熔岩裂纹 + 炽焰尾焰 |
| 9 | midnight | 午夜蓝调 | 深邃蓝 (15,25,80) | 星星点缀 + 月光尾焰 |
| 10 | rainbow | 彩虹桥 | 渐变彩虹 | 棱镜分光 + 七彩尾焰 |
| 11 | steampunk | 蒸汽朋克 | 黄铜 (165,120,60) | 齿轮装饰 + 蒸汽尾焰 |
| 12 | starpunk | 星际朋克 | 星云紫 (100,50,150) | 星云云雾 + 星尘尾迹 |

### 差异化装饰元素

每种涂装都有独特的视觉元素：

1. **琴身图案** (decal_type)
   - skull: 骷髅
   - blood_splatter: 血迹
   - circuit: 电路
   - halo: 光环
   - spiral: 漩涡
   - radiation: 辐射符号
   - ice_crystal: 冰晶
   - lava_cracks: 熔岩裂纹
   - stars: 星星
   - prism: 棱镜
   - gears: 齿轮
   - nebula: 星云

2. **纹路图案** (body_pattern)
   - cracks: 裂纹
   - circuit_lines: 电路板
   - hazard_stripes: 警示条纹
   - frost_cracks: 冰裂纹
   - magma_veins: 岩浆脉络
   - rainbow_stripes: 彩虹条纹
   - rivets: 铆钉

3. **尾焰风格** (exhaust_style)
   - lightning: 闪电形
   - dripping: 滴血形
   - electric_arc: 电弧形
   - holy_flame: 圣焰
   - wavy: 波纹形
   - toxic_cloud: 毒雾形
   - frost_breath: 冰霜吐息
   - inferno: 地狱烈焰
   - moonbeam: 月光
   - rainbow_trail: 彩虹尾迹
   - steam_puff: 蒸汽喷射
   - stardust: 星尘尾迹

4. **音箱特效** (speaker_effect)
   - pulse_dark: 暗脉冲
   - heartbeat: 心跳脉动
   - scanning: 扫描线
   - radiant: 光芒四射
   - hypnotic: 催眠脉动
   - geiger: 盖革计数器
   - frozen: 冰冻效果
   - eruption: 喷发效果
   - starlight: 星光闪烁
   - disco: 迪斯科灯效
   - clockwork: 钟表机械
   - warp: 曲速效果

---

## 渲染架构

### 主渲染函数
```
render_heavymetal_plane(surface, x, y, theme_name, t, scale)
```

### 渲染层级（从底到顶）
1. 音箱引擎 (`_draw_speaker_cabinet`)
2. 尾部推进火焰 (`_draw_exhaust_rotated`)
3. 吉他琴身主体 (Flying V造型)
4. 拾音器 (`_draw_pickups_rotated`)
5. 琴桥与控制旋钮 (`_draw_bridge_and_controls_rotated`)
6. 琴颈 (`_draw_guitar_neck_rotated`)
7. 琴头 (`_draw_headstock_rotated`)
8. 差异化装饰元素 (`_draw_theme_decorations`)
9. 边缘轮廓微光

### 关键参数
- **显示比例**: `display_scale = scale * 0.5`
- **倾斜角度**: `tilt_angle = -0.1` (约6度)
- **琴身中心**: 与玩家中心对齐

---

## 文件结构

```
utils/
├── planes/
│   └── skins_heavymetal.py    # 涂装渲染系统 (~2300行)
├── bullets/
│   └── heavymetal_bullets.py  # 专属弹幕系统
```

### 主要导出
- `render_heavymetal_plane` - 主渲染函数
- `render_heavymetal_skin` - 皮肤渲染
- `HEAVYMETAL_THEMES` - 12种主题配色
- `HEAVYMETAL_STYLES` - 样式映射

---

## 开发历程

### 2025-12-19

#### 初始问题修复
- 修复技能在错误屏幕位置释放的BUG
- 添加12种涂装到`customization.py`的`PAINT_THEMES`

#### 视觉重构
- 重写整体建模，增强压迫感
- 添加完整吉他展示（琴身+琴颈+琴头）
- 添加倾斜角度增加动感
- 调整缩放比例确保完整显示

#### 涂装差异化
- 重写12种涂装配色，使用高对比度鲜艳色彩
- 添加差异化装饰系统：
  - 琴身图案（骷髅、电路、冰晶等）
  - 纹路图案（裂纹、条纹、脉络等）
  - 尾焰风格（闪电、电弧、冰霜等）
  - 音箱特效（脉动、扫描、迪斯科等）

---

## 技术细节

### 旋转系统
所有组件支持统一旋转，使用旋转矩阵：
```python
def rotate_point(px, py, origin_x, origin_y):
    dx, dy = px - origin_x, py - origin_y
    return (
        int(origin_x + dx * cos_a - dy * sin_a),
        int(origin_y + dx * sin_a + dy * cos_a)
    )
```

### 动态效果
- 呼吸效果: `pulse = 0.5 + 0.5 * math.sin(t * rate)`
- 闪烁效果: `alpha = int(base + range * math.sin(t * freq))`
- 旋转动画: `angle = t * speed`

---

## 总结

HEAVY METAL机体是一个完整的重型战机系统，融合了摇滚乐的狂野美学与射击游戏的战斗体验。12种高辨识度涂装为玩家提供了丰富的个性化选择，每种涂装都有独特的视觉元素和动态效果。

**维那斯万岁！🎸🤘**
