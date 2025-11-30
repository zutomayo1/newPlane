import re

file_path = r"c:\Users\真夜中\Desktop\newPlane\customization.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 定义需要更新的涂装数据：飞机名、涂装ID后缀、新粒子数、新尾迹宽度
updates = [
    # Thunderbird (7个)
    ("thunderbird_storm", 78, 12, "风暴之眼雷霆主宰", "乌云漩涡环绕，密集闪电链贯穿机身，雷电风暴核心，震耳雷鸣"),
    ("thunderbird_tesla", 85, 11, "特斯拉线圈电磁风暴", "高压线圈全机身分布，电弧网络交织，电磁脉冲爆发，等离子球环绕"),
    ("thunderbird_plasma", 95, 13, "等离子羽翼能量天使", "羽翼完全等离子化，能量羽毛飘散，等离子风暴漩涡，天使降临姿态"),
    ("thunderbird_aurora", 82, 12, "极光战鹰北境之翼", "极光羽翼流动变幻，七彩光带飘扬，光之羽毛洒落，梦幻鸟形"),
    ("thunderbird_valkyrie", 92, 13, "女武神战争使者", "神圣光翼展开，战争女神形态，圣光羽毛暴雨，天界裁决之力"),
    ("thunderbird_phoenix", 105, 14, "雷电凤凰涅槃重生", "凤凰真身显现，雷火交融羽翼，浴火重生特效，凤鸣九天，烈焰羽毛漫天"),
    ("thunderbird_cosmic", 118, 16, "宇宙雷神星云之翼", "星云羽翼璀璨，宇宙风暴漩涡，星辰粒子暴雨，银河光带尾迹，诸神黄昏"),
    
    # Viper (7个)
    ("viper_toxic", 75, 11, "剧毒之牙毒液喷涌", "毒液从机身渗出，毒雾弥漫扩散，剧毒液滴飞溅，生化警告标志"),
    ("viper_acid", 82, 12, "强酸腐蚀溶解一切", "强酸液体流淌，腐蚀烟雾升腾，酸液飞溅特效，金属溶解效果"),
    ("viper_bio", 90, 13, "生化武器病毒扩散", "生化病毒容器外露，病毒云团扩散，感染粒子漂浮，生物危害符号闪烁"),
    ("viper_neon", 88, 12, "霓虹毒蛇致命诱惑", "霓虹毒液流动纹理，彩色毒雾飘散，荧光毒液粒子，致命美丽"),
    ("viper_shadow", 95, 14, "暗影猎手无声潜行", "暗影形态变幻，黑雾吞噬光线，影子分身飘忽，致命暗杀者"),
    ("viper_cyber", 102, 14, "赛博蝰蛇数据毒素", "数据病毒可视化，代码毒素扩散，网络入侵特效，数字腐蚀"),
    ("viper_hydra", 115, 16, "九头蛇致命群蛇", "多头蛇形态，九条蛇影环绕，毒牙密布，群蛇撕咬特效，毒液暴雨"),
    
    # Specter (7个)
    ("specter_reaper", 80, 12, "死神收割灵魂收集者", "死神镰刀形态，灵魂火焰飘荡，收割特效，亡魂哀嚎"),
    ("specter_wraith", 85, 11, "幽灵怨灵冤魂缠绕", "幽灵形态半透明，怨灵面孔浮现，灵魂锁链束缚，冤魂飘荡"),
    ("specter_bone", 92, 13, "骸骨战机死亡使者", "骸骨结构外露，骷髅装饰遍布，死亡气息弥漫，骨刺突出"),
    ("specter_necro", 88, 12, "亡灵召唤死灵法术", "亡灵法阵显现，召唤符文闪烁，死灵仆从环绕，黑暗魔法能量"),
    ("specter_void", 98, 14, "虚空幽魂湮灭之影", "虚空能量侵蚀，幽魂形态变幻，湮灭粒子扩散，存在感消失"),
    ("specter_frost", 105, 14, "冰霜幽魂永冻亡灵", "冰霜覆盖机身，冰晶灵魂浮现，冻结气息扩散，冰封死域"),
    ("specter_judge", 120, 16, "终极审判死神降临", "审判之翼展开，死神真身显现，灵魂审判光柱，地狱之门开启，末日降临"),
]

for paint_id, particle, trail_w, new_name, new_desc in updates:
    # 查找并替换整个涂装块
    pattern = rf'("{paint_id}":\s*\{{[^}}]+?"name":\s*")[^"]+(",[^}}]+?"desc":\s*")[^"]+(",[^}}]+?"particle_count":\s*)\d+([^}}]+?"trail_width":\s*)\d+'
    
    def replacer(match):
        return f'{match.group(1)}{new_name}{match.group(2)}{new_desc}{match.group(3)}{particle}{match.group(4)}{trail_w}'
    
    content = re.sub(pattern, replacer, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated 21 exclusive themes successfully!")
