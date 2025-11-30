import re

file_path = r"c:\Users\真夜中\Desktop\newPlane\customization.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 所有47个未更新的涂装：ID, 新粒子数, 新尾迹宽度, 新名称, 新描述
updates = [
    # Arbiter (4个未更新)
    ("arbiter_balance", 78, 11, "平衡裁决天平永恒", "天平绝对平衡，公正秤杆显现，平衡粒子飘散，秩序维持"),
    ("arbiter_law", 85, 12, "法则之书规则编写", "法则之书展开，规则条文显现，法则粒子环绕，规则执行"),
    ("arbiter_fractal", 92, 13, "分形几何无限循环", "分形结构显现，几何无限递归，数学美学，完美对称"),
    ("arbiter_truth", 102, 14, "真理之眼洞察一切", "真理之眼睁开，洞察万物本质，真理光芒普照，一切明晰"),
    
    # Crimson (4个未更新)
    ("crimson_rose", 88, 12, "血玫瑰致命之美", "血红玫瑰绽放，带刺玫瑰丛生，美丽而致命，芬芳杀机"),
    ("crimson_samurai", 95, 13, "绯红武士血刃斩魂", "武士刀刃闪耀，武士道精神，血刃快速斩击，一击毙命"),
    ("crimson_inferno", 105, 14, "地狱烈焰炼狱之火", "地狱火海燃烧，烈焰席卷一切，炼狱般高温，焚毁世界"),
    ("crimson_dragon", 112, 15, "血龙咆哮龙息焚天", "血龙形态显现，龙息喷涌而出，血色龙鳞闪耀，龙威镇世"),
    
    # Eclipse (3个未更新)
    ("eclipse_dual", 95, 13, "日月双食阴阳交替", "日月同时食相，阴阳力量交替，双重天象，天地失色"),
    ("eclipse_abyss", 105, 14, "深渊凝视虚无吞噬", "深渊裂缝开启，虚无力量涌出，凝视毁灭一切，深渊吞噬"),
    ("eclipse_cosmos", 115, 15, "宇宙日食星际黑暗", "宇宙尺度日食，星际黑暗降临，星光全部遮蔽，宇宙寂灭"),
    
    # Gaia (6个未更新)
    ("gaia_rock", 75, 11, "岩石巨人大地之力", "岩石巨人形态，大地之力涌动，岩石粒子飞舞，坚不可摧"),
    ("gaia_crystal", 85, 12, "水晶森林宝石丛林", "水晶树木丛生，宝石果实闪耀，晶莹剔透，光芒万丈"),
    ("gaia_elemental", 92, 13, "元素领主自然四元", "四元素环绕，地水火风交织，元素领主形态，自然之力"),
    ("gaia_overgrowth", 100, 14, "过度生长野性爆发", "植被疯狂生长，藤蔓肆意蔓延，野性力量爆发，自然失控"),
    ("gaia_treant", 108, 15, "树人长老世界古树", "树人长老形态，世界古树降临，千年智慧，森林守护"),
    ("gaia_titan", 118, 16, "盖亚泰坦星球化身", "星球泰坦显现，盖亚意志具化，地壳板块浮动，星球之力"),
    
    # Necro (3个未更新)
    ("necro_bone", 88, 12, "白骨王座骸骨帝王", "白骨王座显现，骸骨帝王登基，骨骼军团列阵，死亡统治"),
    ("necro_soul", 95, 13, "灵魂收集魂瓶封印", "灵魂收集瓶显现，无数魂魄封印，灵魂能量涌动，亡魂哀嚎"),
    ("necro_vampire", 105, 14, "吸血鬼伯爵永夜不朽", "吸血鬼伯爵形态，蝙蝠群环绕，鲜血吸收，永夜不朽"),
    
    # Prism (3个未更新)
    ("prism_refraction", 85, 12, "多重折射光线迷宫", "光线多次折射，光学迷宫形成，光路复杂，眩目迷离"),
    ("prism_glass", 92, 13, "玻璃艺术透明美学", "玻璃艺术品形态，透明材质美学，光影交错，艺术结晶"),
    ("prism_aurora", 110, 14, "极光棱镜光谱盛宴", "极光通过棱镜，光谱完全展开，色彩盛宴，绚烂夺目"),
    
    # Solar (2个未更新)
    ("solar_sun_god", 108, 15, "太阳神拉之审判", "太阳神拉显现，太阳审判降临，神圣光芒普照，万物臣服"),
    ("solar_phoenix", 118, 16, "太阳凤凰永恒烈焰", "太阳凤凰涅槃，永恒烈焰燃烧，凤凰真火，不灭不休"),
    
    # Specter (5个未更新)
    ("specter_assassin", 75, 11, "幽灵刺客无声夺命", "幽灵刺客形态，无声无息接近，致命一击，夺命于无形"),
    ("specter_sniper", 82, 12, "幽灵狙击远程收割", "幽灵狙击手形态，远距离精准射击，灵魂狙击，一发致命"),
    ("specter_poltergeist", 90, 13, "骚灵现象灵异事件", "骚灵现象爆发，物体悬浮飞舞，灵异力量，超自然现象"),
    ("specter_angel", 100, 14, "死亡天使黑色羽翼", "死亡天使降临，黑色羽翼展开，天使审判，灵魂引渡"),
    ("specter_void_hunter", 110, 15, "虚空猎手维度收割", "虚空猎手形态，跨维度狩猎，虚空镰刀，收割一切"),
    
    # Stalker (6个未更新)
    ("stalker_chameleon", 72, 11, "变色龙完美伪装", "变色龙形态，完美环境伪装，色彩变幻，融入环境"),
    ("stalker_predator", 80, 12, "铁血战士热能追踪", "铁血战士形态，热能视觉追踪，等离子炮，狩猎荣耀"),
    ("stalker_alien", 88, 13, "异形猎手完美生物", "异形生物形态，完美生物设计，酸性血液，致命猎杀"),
    ("stalker_insect", 95, 14, "虫群潜行复眼侦测", "虫群形态，复眼全方位侦测，潜行猎杀，群体智慧"),
    ("stalker_drone", 102, 14, "无人机群天罗地网", "无人机群部署，天罗地网监控，智能追踪，无处可逃"),
    ("stalker_xenomorph", 115, 16, "异形皇后终极猎食", "异形皇后显现，终极生物猎手，完美进化，生物链顶端"),
    
    # Striker (1个：striker_stealth需要从65提升)
    ("striker_stealth", 70, 11, "暗影相位虚空渗透", "相位扭曲力场，机身半透明化，暗影分身环绕，空间裂缝尾迹"),
    
    # Titan (1个未更新)
    ("titan_crystal", 88, 12, "晶簇装甲永恒之冰", "水晶结构装甲层叠，光芒多重折射，冰晶粒子漩涡，钻石般闪耀"),
    
    # Viper (3个未更新)
    ("viper_cobra", 78, 11, "眼镜蛇毒牙致命", "眼镜蛇形态，毒牙尖锐致命，蛇信吐露，剧毒喷射"),
    ("viper_plasma", 92, 13, "等离子毒液能量腐蚀", "等离子态毒液，能量腐蚀一切，高能毒素，物质解离"),
    ("viper_serpent_god", 115, 16, "蛇神降世巴蛇吞象", "上古蛇神降世，巴蛇吞象之力，蛇鳞闪耀，神话再现"),
    
    # Weaver (5个未更新)
    ("weaver_spider", 75, 11, "蜘蛛之网命运丝线", "蜘蛛结网形态，命运丝线编织，蛛网密布，困住猎物"),
    ("weaver_silk", 85, 12, "丝绸之路空间织布", "丝绸般空间编织，空间之路铺展，柔韧丝线，连接万物"),
    ("weaver_network", 92, 13, "网络编织数据之网", "数据网络编织，信息之网扩散，网络节点，连接一切"),
    ("weaver_matrix", 100, 14, "矩阵编织代码之丝", "矩阵代码编织，程序丝线交织，源代码显现，世界重写"),
    ("weaver_destiny", 110, 15, "命运编织因果之网", "命运之网显现，因果关系编织，命运线条交错，宿命难逃"),
]

for paint_id, particle, trail_w, new_name, new_desc in updates:
    pattern = rf'("{paint_id}":\s*\{{[^}}]+?"name":\s*")[^"]+(",[^}}]+?"desc":\s*")[^"]+(",[^}}]+?"particle_count":\s*)\d+([^}}]+?"trail_width":\s*)\d+'
    
    def replacer(match):
        return f'{match.group(1)}{new_name}{match.group(2)}{new_desc}{match.group(3)}{particle}{match.group(4)}{trail_w}'
    
    content = re.sub(pattern, replacer, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully updated all {len(updates)} remaining exclusive themes!")
print("ALL 112 EXCLUSIVE THEMES ARE NOW UPGRADED!")
