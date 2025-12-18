# 宇宙之弧·GALAXIA 开发记录

## 机体概述

**GALAXIA（宇宙之弧）** 是泰拉瑞亚武器变形系列的第一台机体，基于泰拉瑞亚灾厄模组中的传奇武器「宇宙之弧（Ark of the Cosmos）」设计。这是一台剪刀变形机甲，拥有12种主题涂装，每种涂装对应泰拉瑞亚中的不同传奇武器。

## 设计理念

- **核心形态**：剪刀变形机甲，双刃交叉设计
- **视觉风格**：宇宙星云、星尘粒子、螺旋星云尾迹
- **变形机制**：剪刀开合动画，刀刃呼吸效果
- **规模定位**：2.0倍放大，强烈压迫感

## 涂装系统（12种）

| 涂装ID | 名称 | 设计来源 | 配色特点 |
|--------|------|----------|----------|
| default | 宇宙之弧 | Ark of the Cosmos | 紫蓝渐变，星云色调 |
| galaxia | 星系之刃 | Galaxia | 深紫宇宙色 |
| stellar | 恒星吞噬者 | Stellar Contempt | 金橙恒星色 |
| biome | 生态裂隙 | Biome Blade | 绿色生态色 |
| true_biome | 真·生态裂隙 | True Biome Blade | 深绿自然色 |
| ordeal | 厄难长刀 | Ordeal's End | 暗红血色 |
| crimson | 猩红噩梦 | Corrupted/Crimson | 血肉骨骸色 |
| zenith | 天顶之刃 | Zenith | 金黄光芒色 |
| rainbow | 彩虹水晶 | Prism | 彩虹色谱循环 |
| void | 虚空撕裂 | Void | 深紫虚空色 |
| solar | 日耀烈焰 | Solar | 橙红火焰色 |
| nebula | 星云幻影 | Nebula | 粉紫星云色 |

## 主武器系统

### CosmicScissorBullet（宇宙剪刀弹）
- **发射方式**：双刃交叉发射
- **视觉效果**：
  - 剪刀刀刃形态
  - 交叉斩击路径
  - 宇宙能量尾迹
  - 星尘粒子拖尾
- **伤害类型**：能量斩击

## 大招系统（3种）

### F键 - DimensionalSlashSkill（次元斩击）
- **效果**：释放5道次元斩击
- **视觉**：
  - 闪电链连接效果
  - 光柱冲击波
  - 屏幕闪烁
  - 次元裂隙特效
- **伤害**：高爆发AOE

### G键 - GalaxyTrapSkill（星系陷阱）
- **效果**：创建引力陷阱
- **视觉**：
  - 4条螺旋臂
  - 12颗轨道星星
  - 吸收拖尾效果
  - 引力扭曲场
- **伤害**：持续吸引+伤害

### C键 - BigRipSkill（大撕裂）
- **效果**：巨型剪刀撕裂屏幕
- **视觉**：
  - 巨型剪刀开合动画
  - 虚空触须
  - 宇宙碎片喷发
  - 星云云朵
  - 超新星爆炸
  - 裂隙伤疤
- **伤害**：全屏毁灭性打击

## Bug修复记录

### Bug #004 - Alpha值越界（zenith涂装）

**问题描述**：天顶之刃涂装显示为红色圆圈

**根本原因**：
```python
power_pulse = 0.4 + 0.6 * math.sin(t * 5)
# 当sin为-1时，power_pulse = 0.4 - 0.6 = -0.2
# 导致后续alpha计算为负数
```

**修复方案**：
1. 修改 `power_pulse` 公式为 `0.5 + 0.5 * math.sin(t * 5)`，确保范围0.0-1.0
2. 所有alpha值添加 `max(0, min(255, ...))` 保护

**修复位置**：
- `skins_galaxia.py` 第1558行：power_pulse计算
- 第1524行：mid_highlight_alpha
- 第1529行：glow_alpha
- 第1537行：剑柄握把alpha
- 第1542行：剑柄宝石alpha
- 第1580行：seg_alpha
- 第1584行：burst_line_alpha
- 第1600行：符文剑尖alpha
- 第1610行：符文光环alpha
- 第1625行：pillar_alpha和layer_alpha

### 机体缩放问题

**问题描述**：机体模型太小，没有压迫感

**修复方案**：
- 将scale从1.4倍增加到2.0倍
- 渲染surface从120x120增加到280x280
- 最终缩放回120x120显示

### crimson涂装缺失颜色

**问题描述**：猩红噩梦涂装显示为红色圆圈

**根本原因**：缺少flesh、bone、blood颜色键

**修复方案**：添加缺失的颜色定义

## 技术实现

### 文件结构
```
utils/planes/skins_galaxia.py  # 涂装渲染系统（~2574行）
utils/bullets/galaxia_bullets.py  # 子弹和技能系统（~1179行）
```

### 渲染层级（从后到前）
1. 远景星云背景 - 螺旋星云尾迹
2. 环绕星尘粒子云 - 双层轨道
3. 能量光环 - 多层扩散环
4. 机体主体 - 剪刀变形机甲
5. 刀刃高光 - 动态呼吸效果
6. 核心能量球 - 脉冲发光
7. 主题特效 - 各涂装独特效果

### 注册信息
```json
// customization.json
"galaxia": {
    "name": "宇宙之弧",
    "unlock_condition": "击败奥罗",
    "skins": ["default", "galaxia", "stellar", "biome", "true_biome", 
              "ordeal", "crimson", "zenith", "rainbow", "void", 
              "solar", "nebula"]
}
```

## 开发时间线

- 2025年12月18日：完成基础机体框架和12种涂装
- 2025年12月18日：添加主武器CosmicScissorBullet
- 2025年12月18日：实现三大技能系统
- 2025年12月18日：修复crimson涂装颜色缺失
- 2025年12月18日：修复zenith涂装Bug #004
- 2025年12月18日：优化机体规模至2.0倍

## 后续计划

- [ ] 添加更多泰拉瑞亚武器变形涂装
- [ ] 优化剪刀开合动画
- [ ] 添加变形音效
- [ ] 完善技能平衡性
