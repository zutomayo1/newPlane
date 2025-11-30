import re

file_path = r"c:\Users\真夜中\Desktop\newPlane\customization.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

updates = [
    # Solar (7个)
    ("solar_flare", 82, 13, "日冕耀斑太阳风暴", "太阳耀斑爆发，日冕物质抛射，太阳风粒子暴雨，恒星能量"),
    ("solar_corona", 88, 12, "日冕王冠太阳之子", "日冕王冠显现，太阳光芒万丈，黄金光辉笼罩，太阳神形态"),
    ("solar_fusion", 95, 14, "核聚变恒星之心", "核聚变反应爆发，氢氦燃烧特效，恒星内核能量，聚变光芒"),
    ("solar_prominence", 90, 13, "日珥风暴等离子喷发", "巨型日珥喷发，等离子体风暴，磁场扭曲特效，太阳风暴"),
    ("solar_eclipse", 102, 14, "日全食光暗交替", "日全食现象，光暗瞬间转换，日冕边缘发光，贝利珠特效"),
    ("solar_supernova", 112, 15, "超新星恒星爆炸", "超新星爆炸序列，恒星崩解特效，能量波扩散，星云形成"),
    ("solar_helios", 125, 16, "赫利俄斯太阳神降临", "太阳神真身显现，驾驭火焰战车，太阳神力爆发，万物焚毁，光明主宰"),
    
    # Arbiter (7个)
    ("arbiter_quantum", 80, 12, "量子裁决概率坍缩", "量子态叠加显现，概率云团漂浮，波函数坍缩，量子纠缠"),
    ("arbiter_judge", 85, 11, "终极审判公正天平", "审判天平显现，公正符文闪耀，裁决之光降临，法则之力"),
    ("arbiter_matrix", 92, 13, "矩阵主宰代码执行", "矩阵世界显现，代码洪流奔涌，程序执行特效，数字主宰"),
    ("arbiter_space", 88, 12, "空间裁决维度切割", "空间被切割分离，维度刀刃显现，空间碎片漂浮，几何分割"),
    ("arbiter_time", 98, 14, "时间裁决因果锁链", "时间线可视化，因果锁链连接，时间审判降临，命运裁决"),
    ("arbiter_cosmic", 108, 15, "宇宙法庭真理裁决", "宇宙法庭开庭，真理符文闪耀，法则之书展开，终极裁决"),
    ("arbiter_omega", 120, 16, "终极裁决秩序主宰", "秩序化身显现，法则重新编写，混沌归于秩序，绝对裁决，万法归一"),
    
    # Eclipse (7个)
    ("eclipse_shadow", 78, 11, "日食幽灵暗影吞噬", "日食阴影吞噬，黑暗吞食光明，暗影扩散特效，光暗界限"),
    ("eclipse_void", 85, 12, "虚空日食黑洞边缘", "虚空黑洞显现，引力透镜效应，事件视界线，光线扭曲"),
    ("eclipse_night", 92, 13, "永夜降临黑暗时代", "永恒黑夜降临，黑暗领域扩张，星光逐渐消逝，永恒夜幕"),
    ("eclipse_moon", 88, 12, "血月当空月蚀之力", "血月高悬天空，月蚀能量降临，血色月光洒落，月神之力"),
    ("eclipse_dark", 100, 14, "暗面觉醒黑暗本源", "黑暗本源觉醒，暗物质显现，反物质湮灭，黑暗吞噬"),
    ("eclipse_eternal", 110, 15, "永恒日食终结之日", "永恒日食天象，末日征兆显现，世界走向黑暗，终结预言"),
    ("eclipse_singularity", 122, 16, "奇点日食黑洞降临", "黑洞奇点显现，引力扭曲空间，时空被撕裂，吞噬一切，宇宙终结"),
    
    # Prism (7个)
    ("prism_rainbow", 75, 11, "棱镜分光七彩虹光", "光谱完全分离，七彩虹光闪耀，色彩粒子飞舞，光的盛宴"),
    ("prism_refract", 82, 12, "折射万象光之迷宫", "光线多重折射，光路交织复杂，光学迷宫形成，折射美学"),
    ("prism_laser", 90, 13, "激光矩阵光束网络", "激光矩阵布阵，光束网络交织，高能光束发射，光之武器"),
    ("prism_crystal", 88, 12, "晶体共振光芒四射", "晶体结构共振，光芒四面发射，光的放大效应，晶莹璀璨"),
    ("prism_spectrum", 98, 14, "光谱爆发全频共振", "全光谱爆发，所有频率共振，可见不可见光，光之全貌"),
    ("prism_diamond", 108, 15, "钻石星辰完美折射", "钻石切割面显现，完美折射光芒，星辰般闪耀，光之宝石"),
    ("prism_infinity", 120, 16, "无限光谱光之本源", "无限光谱展开，光之本源显露，光速粒子暴雨，光子海洋，万物皆光"),
    
    # Necro (7个)
    ("necro_death", 80, 12, "死灵骑士亡者军团", "亡者军团召唤，骸骨士兵列阵，死灵法术闪耀，亡灵大军"),
    ("necro_lich", 85, 11, "巫妖王不死法师", "巫妖王形态显现，死亡魔法爆发，灵魂囚笼显现，不死之力"),
    ("necro_plague", 92, 13, "瘟疫传播死亡疫病", "瘟疫云团扩散，疾病粒子漂浮，感染特效显现，死亡瘟疫"),
    ("necro_curse", 88, 12, "诅咒之力亡魂缠身", "诅咒符文闪烁，亡魂缠绕机身，诅咒能量爆发，不详预兆"),
    ("necro_undead", 100, 14, "不死军团永恒行军", "不死军团行军，永恒战争继续，亡者复苏特效，死而复生"),
    ("necro_reaper", 110, 15, "死神化身灵魂收割", "死神真身显化，灵魂收割镰刀，死亡宣判降临，生命终结"),
    ("necro_apocalypse", 125, 16, "死亡天启末日降临", "天启四骑士降临，死亡瘟疫战争饥荒，世界末日场景，万物归寂，亡者之王"),
]

for paint_id, particle, trail_w, new_name, new_desc in updates:
    pattern = rf'("{paint_id}":\s*\{{[^}}]+?"name":\s*")[^"]+(",[^}}]+?"desc":\s*")[^"]+(",[^}}]+?"particle_count":\s*)\d+([^}}]+?"trail_width":\s*)\d+'
    
    def replacer(match):
        return f'{match.group(1)}{new_name}{match.group(2)}{new_desc}{match.group(3)}{particle}{match.group(4)}{trail_w}'
    
    content = re.sub(pattern, replacer, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated final 35 exclusive themes (Solar, Arbiter, Eclipse, Prism, Necro)!")
print("ALL 112 EXCLUSIVE THEMES NOW UPDATED!")
