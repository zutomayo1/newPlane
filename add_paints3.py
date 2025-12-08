import re

# 读取文件
with open('customization.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 定义第三批16个超级创意涂装（_ex3系列）
new_paints = [
    ('striker', 'striker_ex3', '次元裂缝·空间碎裂', '空间裂缝撕裂现实，碎片化空间漂浮，维度扭曲视觉，现实崩坏特效', (255, 0, 255), (255, 100, 255), (255, 50, 255), 4200, 'void', 160, 21),
    ('phantom', 'phantom_ex3', '星云诞生·宇宙摇篮', '星云气体翻滚，恒星胚胎闪烁，星际尘埃漩涡，宇宙孕育生机', (100, 150, 255), (150, 200, 255), (120, 180, 255), 4200, 'cosmic', 155, 20),
    ('titan', 'titan_ex3', '符文巨像·古代守护', '巨型石像形态，古代符文发光，魔法阵环绕，守护者能量护盾', (150, 100, 50), (200, 150, 100), (180, 120, 80), 4200, 'magic', 145, 22),
    ('thunderbird', 'thunderbird_ex3', '雷霆瓦尔基里·战争天使', '天使翅膀展开，雷电战矛横扫，神圣光环笼罩，战争号角回响', (255, 255, 200), (255, 255, 240), (255, 255, 220), 4200, 'holy', 165, 21),
    ('viper', 'viper_ex3', '毒液交响曲·剧毒旋律', '音符形状飞舞，毒液音波扩散，交响乐章流动，致命旋律飘荡', (0, 255, 100), (100, 255, 150), (50, 255, 120), 4200, 'toxic', 155, 20),
    ('specter', 'specter_ex3', '量子幽灵·叠加态', '多个位置同时存在，量子态闪烁切换，观测者效应，薛定谔之影', (100, 255, 255), (150, 255, 255), (120, 255, 255), 4200, 'quantum', 160, 19),
    ('aurora', 'aurora_ex3', '北极光兽·极地守望', '极光巨狼形态，极光毛发飘动，寒冰利爪闪烁，北极星光照耀', (0, 255, 180), (100, 255, 220), (50, 255, 200), 4200, 'aurora', 170, 20),
    ('crimson', 'crimson_ex3', '恒星熔炉·核聚变', '核聚变反应炉，等离子体喷射，磁场约束环，恒星级能量', (255, 150, 0), (255, 200, 100), (255, 180, 50), 4200, 'fusion', 175, 22),
    ('stalker', 'stalker_ex3', '纳米风暴·灰雾吞噬', '纳米机器人云，自我复制扩散，灰雾吞噬一切，微观机械潮', (120, 120, 120), (180, 180, 180), (150, 150, 150), 4200, 'nano', 180, 21),
    ('gaia', 'gaia_ex3', '四季更迭·轮回之树', '树木四季变化，春夏秋冬交替，生命轮回循环，自然更替律动', (100, 200, 100), (150, 220, 150), (120, 210, 120), 4200, 'nature', 165, 20),
    ('weaver', 'weaver_ex3', '神经网络·思维脉冲', '神经元连接网，思维电流传递，突触闪烁亮起，意识流动可见', (255, 100, 150), (255, 150, 200), (255, 120, 180), 4200, 'neural', 160, 19),
    ('solar', 'solar_ex3', '暗物质潮汐·引力奇点', '暗物质可视化，引力透镜弯曲，时空涟漪扩散，引力奇点旋转', (50, 0, 100), (100, 50, 150), (80, 20, 120), 4200, 'gravity', 170, 21),
    ('arbiter', 'arbiter_ex3', '真理之门·全知之眼', '真理之门开启，全知之眼注视，知识流光溢出，智慧之树显现', (255, 215, 0), (255, 240, 100), (255, 230, 50), 4200, 'wisdom', 155, 20),
    ('eclipse', 'eclipse_ex3', '反物质引擎·湮灭核心', '正反物质对撞，湮灭能量爆发，反物质容器，对撞机光环', (255, 0, 150), (255, 100, 200), (255, 50, 180), 4200, 'antimatter', 175, 22),
    ('prism', 'prism_ex3', '五维投影·超立方体', '超立方体旋转，四维投影可见，五维几何结构，多维空间折叠', (0, 255, 255), (100, 255, 255), (50, 255, 255), 4200, 'hyperdim', 165, 21),
    ('necro', 'necro_ex3', '熵增极限·热寂降临', '宇宙热寂状态，熵值最大化，能量耗散殆尽，万物归于平静', (20, 20, 50), (50, 50, 80), (30, 30, 60), 4200, 'entropy', 170, 22),
]

# 查找每个 _ex2 涂装并在其后插入 _ex3
for plane, style, name, desc, neon, accent, trail, cost, trail_style, particle, trail_width in new_paints:
    # 构建涂装配置文本
    paint_config = f'''    "{style}": {{
        "name": "{name}",
        "desc": "{desc}",
        "neon_color": {neon},
        "accent_color": {accent},
        "trail_color": {trail},
        "unlocked": False,
        "cost": {cost},
        "trail_style": "{trail_style}",
        "particle_count": {particle},
        "category": "exclusive",
        "trail_width": {trail_width},
        "exclusive_plane": "{plane}",
        "model_style": "{style}",
        "animated": True,
    }},
'''
    
    # 查找插入位置
    for i, line in enumerate(lines):
        if f'"{plane}_ex2"' in line and '"name"' not in line:
            # 找到 _ex2 的结束位置（下一个 "# ====="）
            j = i + 1
            while j < len(lines) and '# ==========' not in lines[j]:
                j += 1
            # 在分隔线之前插入
            lines.insert(j, paint_config)
            break

# 写回文件
with open('customization.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('成功添加16个第三批超级创意涂装配置!')
