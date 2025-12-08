import re

# 读取文件
with open('customization.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 定义剩余15个新涂装（已经添加了phantom_ex2）
new_paints = [
    ('titan', 'titan_ex2', '熔岩巨兽·火山之心', '岩浆裂纹机身，熔岩喷发效果，火山灰烟尘，地火核心脉动', (255, 100, 0), (255, 150, 50), (255, 120, 20), 4000, 'fire', 140, 20),
    ('thunderbird', 'thunderbird_ex2', '凤凰涅槃·浴火重生', '凤凰展翼形态，火焰羽毛飘落，涅槃重生光环，神鸟啼鸣特效', (255, 50, 50), (255, 150, 100), (255, 80, 80), 4000, 'fire', 145, 19),
    ('viper', 'viper_ex2', '深海巨鲸·深渊猎食者', '鲸鱼形态机身，锯齿背鳍凸起，水波纹扩散，深海气泡上浮', (0, 150, 255), (100, 200, 255), (50, 180, 255), 4000, 'water', 135, 18),
    ('specter', 'specter_ex2', '暗影刺客·隐匿之刃', '隐形刺客形态，双刀交叉姿态，暗影分身闪烁，忍者手里剑飞旋', (50, 50, 100), (100, 100, 150), (70, 70, 120), 4000, 'shadow', 125, 16),
    ('aurora', 'aurora_ex2', '冰霜精灵·寒冰女王', '冰晶翅膀展开，雪花飘落特效，冰锥环绕飞舞，冰封寒气扩散', (150, 220, 255), (200, 240, 255), (180, 230, 255), 4000, 'ice', 140, 18),
    ('crimson', 'crimson_ex2', '爆炸之星·超新星', '星体爆发形态，爆炸冲击波扩散，星云碎片飞溅，能量核聚变光芒', (255, 255, 100), (255, 255, 200), (255, 255, 150), 4000, 'energy', 150, 20),
    ('stalker', 'stalker_ex2', '机械蜘蛛·纳米虫群', '蜘蛛机械腿展开，纳米机器虫飞舞，电子复眼扫描，机械丝线连接', (200, 200, 200), (240, 240, 240), (220, 220, 220), 4000, 'tech', 135, 17),
    ('gaia', 'gaia_ex2', '樱花树灵·落英缤纷', '樱花树形态，粉色花瓣飘落，树枝摇曳生姿，春意盎然光环', (255, 150, 180), (255, 200, 220), (255, 180, 200), 4000, 'nature', 145, 18),
    ('weaver', 'weaver_ex2', 'DNA螺旋·基因编码', '双螺旋DNA结构，碱基对连接闪烁，基因序列流动，细胞分裂特效', (0, 255, 150), (100, 255, 200), (50, 255, 180), 4000, 'bio', 130, 17),
    ('solar', 'solar_ex2', '雷电之神·宙斯之怒', '雷神锤形态，闪电链条缠绕，雷云翻滚汇聚，天降神雷审判', (200, 200, 255), (230, 230, 255), (220, 220, 255), 4000, 'lightning', 140, 19),
    ('arbiter', 'arbiter_ex2', '正义天秤·律法之眼', '天秤悬浮平衡，律法之眼注视，正义光柱降临，审判之剑高悬', (255, 215, 0), (255, 240, 100), (255, 230, 50), 4000, 'holy', 135, 18),
    ('eclipse', 'eclipse_ex2', '星系吞噬者·宇宙终焉', '黑洞形态巨口，吞噬星系特效，引力波扭曲，宇宙坍缩漩涡', (100, 0, 150), (150, 50, 200), (120, 20, 180), 4000, 'void', 150, 20),
    ('prism', 'prism_ex2', '万花筒·幻彩迷宫', '万花筒对称图案，镜像反射无限，色彩万变交织，迷幻光学效果', (255, 100, 255), (255, 180, 255), (255, 140, 255), 4000, 'rainbow', 145, 19),
    ('necro', 'necro_ex2', '虚无教主·万物归墟', '虚无教主降临，万物归于寂灭，存在消散湮灭，终焉之书翻页', (0, 0, 0), (50, 50, 50), (20, 20, 20), 4000, 'void', 150, 20),
]

# 查找每个 _ex 涂装并在其后插入 _ex2
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
        if f'"{plane}_ex"' in line and '"name"' not in line:
            # 找到 _ex 的结束位置（下一个 "# ====="）
            j = i + 1
            while j < len(lines) and '# ==========' not in lines[j]:
                j += 1
            # 在分隔线之前插入
            lines.insert(j, paint_config)
            break

# 写回文件
with open('customization.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('成功添加15个新涂装配置!')
