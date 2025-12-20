# 分形天顶·ZENITH 开发记录

## 基本信息
| 属性 | 值 |
|------|-----|
| 机体ID | zenith |
| 机体名称 | 分形天顶·ZENITH |
| 原型 | Terraria - Zenith (天顶剑) |
| 定位 | 终极收藏机体 / 剑阵母舰 |
| 稀有度 | ★★★★★ 传说 |
| 解锁条件 | 通关所有Boss / 收集12把名剑碎片 |

---

## 设计理念

### 灵感来源
天顶剑是泰拉瑞亚中的终极近战武器，由12把传奇剑刃合成。攻击时会召唤所有组成它的剑影向敌人飞去，形成华丽的剑幕。

### 核心概念
- **不发射子弹，而是投掷环绕的剑**
- **剑像回旋镖一样飞出后返回**
- **剑阵可格挡敌弹（分形护盾）**
- **终极技能：所有剑合体成巨剑劈砍**

---

## 机体外观

### 主体设计
```
     ◇ ← 彩虹像素尖端
    ╱█╲ ← 核心（靛青色）
   ╱███╲ ← 分形机翼（渐变）
  ╱█████╲ ← 能量层
 ╱▓▓▓▓▓▓▓╲ ← 剑阵基座
╱ ★ ★ ★ ★ ╲ ← 环绕的12把名剑
```

### 视觉特效
1. **彩虹循环光效** - 机体边缘持续RGB渐变
2. **像素碎片粒子** - 周围飘散发光碎片
3. **剑阵环绕** - 12把不同颜色的剑围绕旋转
4. **分形核心脉动** - 中心能量核心规律脉动

---

## 涂装系统

### 6种涂装主题

| 涂装ID | 名称 | 主色调 | 设计理念 |
|--------|------|--------|----------|
| zenith_default | 分形天顶 | 靛青+品红 | 原版天顶剑配色 |
| zenith_terra | 泰拉圣剑 | 翠绿 | 致敬泰拉刃 |
| zenith_meowmere | 喵喵彩虹 | 粉色 | 致敬喵喵刃 |
| zenith_stardust | 星尘龙骸 | 星蓝 | 致敬星尘龙剑 |
| zenith_solar | 日耀烈焰 | 烈焰橙 | 致敬日耀喷发 |
| zenith_void | 虚空终末 | 深紫黑 | 虚空版本 |

### 颜色参数
```python
ZENITH_THEMES = {
    "zenith_default": {
        "core": (75, 0, 130),        # 靛青核心
        "blade": (255, 255, 255),    # 纯白剑刃
        "glow": (255, 0, 255),       # 品红光效
        "pixel": (255, 255, 255),    # 像素碎片
        "trail": (147, 112, 219),    # 紫罗兰拖尾
        "accent": (200, 100, 255),   # 强调色
        "energy": (180, 80, 255),    # 能量色
    },
    # ...其他涂装
}
```

---

## 弹幕系统

### 文件结构
- `utils/bullets/zenith_bullets.py` - 弹幕模块（2141行）
- `utils/planes/skins_zenith.py` - 涂装系统（1195行）

### 核心类

#### 1. SwordArray（剑阵管理器）
```python
class SwordArray:
    """管理环绕机体的所有剑"""
    - swords: 当前在机体周围的剑（12把）
    - flying_swords: 飞出去的剑引用
    - get_next_available_sword(): 获取下一把可投掷的剑
    - mark_sword_flying(idx): 标记剑已飞出
    - mark_sword_returned(idx): 标记剑已返回
```

#### 2. ThrowingSwordBullet（天顶剑影）
主武器 - 还原泰拉瑞亚天顶剑攻击动画

**飞行轨迹：扁平椭圆**
```
                    ★ ← 最远点
                 ↗     ↘
              ↗           ↘
           ↗                 ↘
        ↗                       ↘  ← 横向偏移（15-25%）
    [玩家] ──────────────────────→ 飞行距离（60-80%屏高）
        ↖                       ↙
           ↖                 ↙
              ↖           ↙
                 ↖     ↙
                    ★
```

**核心参数：**
| 参数 | 值 | 说明 |
|------|-----|------|
| max_distance | 屏高 × 60-80% | 椭圆长轴 |
| lateral_amplitude | 长轴 × 15-25% | 椭圆短轴 |
| base_angle | -90 ± 15° | 飞行方向（向上） |
| outward_speed | 0.025 | 飞出速度 |
| return_speed | 0.045 | 返回速度（更快） |
| sword_rotation_speed | 18-30°/帧 | 剑身自旋 |
| max_afterimages | 10 | 残影数量 |

#### 3. 12把名剑数据
```python
LEGENDARY_SWORDS = [
    {"id": 0, "name": "泰拉刃", "color": (0, 255, 100), "length": 22, "damage_mult": 1.2},
    {"id": 1, "name": "喵喵刃", "color": (255, 150, 200), "length": 20, "damage_mult": 1.0},
    {"id": 2, "name": "星怒", "color": (255, 255, 100), "length": 18, "damage_mult": 0.9},
    {"id": 3, "name": "星尘龙剑", "color": (0, 180, 255), "length": 24, "damage_mult": 1.3},
    {"id": 4, "name": "日耀喷发", "color": (255, 150, 0), "length": 21, "damage_mult": 1.1},
    {"id": 5, "name": "星旋剑", "color": (0, 220, 200), "length": 19, "damage_mult": 1.0},
    {"id": 6, "name": "星云剑", "color": (200, 80, 255), "length": 20, "damage_mult": 1.0},
    {"id": 7, "name": "流星剑", "color": (150, 200, 230), "length": 17, "damage_mult": 0.85},
    {"id": 8, "name": "种子弯刀", "color": (100, 200, 80), "length": 16, "damage_mult": 0.8},
    {"id": 9, "name": "无头骑士剑", "color": (255, 120, 0), "length": 23, "damage_mult": 1.15},
    {"id": 10, "name": "彩虹猫之刃", "color": (255, 100, 180), "length": 19, "damage_mult": 1.0},
    {"id": 11, "name": "铜短剑", "color": (200, 150, 100), "length": 10, "damage_mult": 0.5},  # 彩蛋
]
```

---

## 技能系统

### 主武器：天顶剑影
- 投掷环绕的剑向前飞行
- 剑沿扁平椭圆轨迹飞出并返回
- 每把剑独立伤害判定，可穿透
- 残影拖尾效果

### 副武器：剑阵防御
- 环绕的剑形成防护圈
- 可自动格挡接近的敌弹
- 格挡时剑短暂发光

### 终极技能：天顶合剑
- 所有12把剑飞向机体前方
- 合体形成巨型天顶剑
- 向前劈砍造成超高范围伤害
- 彩虹剑气横扫全屏

---

## 渲染技术

### 剑刃绘制（_draw_detailed_sword）
```python
# 多层结构
1. 外发光（半透明大范围）
2. 剑身主体（多边形）
3. 剑刃边缘高光
4. 剑尖发光点
5. 彩虹循环调色
```

### 残影系统
```python
self.afterimages = []  # 历史位置列表
# 每2帧记录一次位置
afterimages.append({
    'x': float_x,
    'y': float_y,
    'rotation': sword_rotation,
    'alpha': 200  # 逐帧衰减
})
```

### 彩虹颜色循环
```python
def _get_rainbow_color(frame, offset=0):
    hue = ((frame * 3 + offset) % 360) / 360.0
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    return (int(r * 255), int(g * 255), int(b * 255))
```

---

## 性能优化

### 1. 剑阵全局实例缓存
```python
_sword_arrays = {}  # owner_id -> SwordArray
def get_sword_array(owner, style):
    # 避免重复创建
```

### 2. 残影数量限制
```python
self.max_afterimages = 10
if len(self.afterimages) > self.max_afterimages:
    self.afterimages.pop(0)
```

### 3. 穿透冷却机制
```python
self.hit_enemies = {}  # enemy_id -> cooldown
self.hit_cooldown = 8  # 每8帧可再次命中同一敌人
```

---

## 文件清单

| 文件 | 行数 | 功能 |
|------|------|------|
| utils/bullets/zenith_bullets.py | 2141 | 弹幕系统核心 |
| utils/planes/skins_zenith.py | 1195 | 涂装与渲染 |

---

## 开发日志

### 2025年12月20日
- ✅ 创建天顶战机基础框架
- ✅ 实现12把名剑数据库
- ✅ 实现剑阵管理器（SwordArray）
- ✅ 实现天顶剑影弹幕（ThrowingSwordBullet）
- ✅ 扁平椭圆飞行轨迹算法
- ✅ 剑身高速自旋 + 残影系统
- ✅ 6种涂装主题设计
- ✅ 彩虹循环光效
- ✅ 机体sprite渲染（像素碎片风格）

---

## 待实现功能

- [ ] 副武器：剑阵防御自动格挡
- [ ] 终极技能：天顶合剑巨剑劈砍
- [ ] 音效系统集成
- [ ] 铜短剑彩蛋特殊效果
- [ ] 收集系统（解锁全部名剑）
