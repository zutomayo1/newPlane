# 子弹涂装完全重新设计方案

## 设计理念
每个子弹涂装必须：
1. **视觉契合**：与机体涂装的核心视觉元素完全一致
2. **独特特效**：不只是换色，而是有独特的粒子、图案、动画
3. **主题呼应**：名字、形状、特效都与涂装故事相关

## 重点案例

### Phantom Matrix (代码矩阵弹)
- **当前**: 简单的代码字符形状
- **应该**: 子弹由"1"和"0"字符组成，飞行时留下绿色数字雨尾迹
- **特效**: matrix_rain (数字雨), glitch_effect (故障闪烁)

### Striker MK2 (纳米机械弹)
- **当前**: 简单的钻头形状
- **应该**: 子弹显示为旋转的齿轮图案，飞行时掉落小金属碎片
- **特效**: rotating_parts (旋转零件), metal_sparks (金属火花)

### Phantom Ghost (幽魂弹)
- **当前**: 半透明圆形
- **应该**: 显示幽灵面孔表情，半透明飘动，带有魂火粒子
- **特效**: ghost_face (鬼脸), soul_flame (魂火粒子)

### Striker Overdrive (熔岩核心弹)
- **当前**: 橙红火球
- **应该**: 中心是裂开的反应堆，裂缝流淌岩浆，掉落燃烧的岩浆块
- **特效**: lava_crack (岩浆裂纹), molten_drops (熔岩滴落)

### Titan Fortress (要塞炮弹)
- **当前**: 灰色椭圆
- **应该**: 显示为装甲板拼接的炮弹，带有铆钉图案，尾部喷射黑烟
- **特效**: armor_plating (装甲纹理), smoke_trail (黑烟尾迹)

### Aurora Sakura (樱花花瓣弹)
- **当前**: 粉色椭圆
- **应该**: 5片樱花花瓣形状，飞行时旋转，掉落粉色花瓣
- **特效**: petal_rotate (花瓣旋转), petal_fall (花瓣飘落)

## 新的子弹属性结构

```python
{
    "shape": "custom_pattern",  # 自定义图案类型
    "pattern": "matrix_01",     # 具体图案内容
    "animation": "rotate",      # 动画类型
    "particle_type": "digit",   # 粒子类型
    "particle_color": (0,255,0),
    "trail_pattern": "code_rain",  # 尾迹图案
}
```

## 需要实现的新形状

1. **matrix_01**: 显示"1"和"0"字符
2. **gear_pattern**: 齿轮图案
3. **ghost_face**: 幽灵面孔
4. **reactor_core**: 裂开的反应堆
5. **armor_plate**: 装甲板纹理
6. **sakura_5petal**: 5瓣樱花
7. **dragon_scale**: 龙鳞纹理
8. **tentacle_eye**: 触手+眼睛
9. **hourglass_sand**: 沙漏+沙粒
10. **blood_drop**: 血滴形状

## 需要实现的新特效

1. **digit_rain**: 数字雨尾迹
2. **gear_spin**: 齿轮旋转
3. **soul_particle**: 魂火粒子
4. **lava_drip**: 岩浆滴落
5. **metal_fragment**: 金属碎片
6. **petal_fall**: 花瓣飘落
7. **scale_shimmer**: 龙鳞闪光
8. **tentacle_wriggle**: 触手蠕动
9. **sand_flow**: 沙粒流动
10. **blood_splatter**: 血液飞溅
