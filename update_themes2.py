import re

file_path = r"c:\Users\真夜中\Desktop\newPlane\customization.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

updates = [
    # Aurora (7个)
    ("aurora_northern", 78, 12, "极光女神北境冰晶", "极光帷幕垂下，冰晶粒子漫天，女神光环闪耀，冰雪精灵飞舞"),
    ("aurora_ice", 85, 13, "冰封女神凛冬之怒", "冰霜女神形态，冰川覆盖机身，冰刺爆发生长，暴风雪肆虐"),
    ("aurora_crystal", 92, 13, "水晶幻境冰晶宫殿", "水晶宫殿结构，冰晶折射万象，钻石粒子暴雨，晶莹剔透"),
    ("aurora_dream", 88, 12, "梦境织者幻想之翼", "梦境色彩流动，幻想粒子飘散，七彩光芒交织，如梦似幻"),
    ("aurora_winter", 98, 14, "永冬领主冰封世界", "永恒冬季形态，冰封领域扩散，冰霜风暴中心，冰河世纪"),
    ("aurora_seraph", 108, 15, "冰雪天使圣洁化身", "冰雪天使降临，圣洁冰翼展开，冰晶羽毛纷飞，神圣冰封"),
    ("aurora_goddess", 122, 16, "极光至尊女神真身", "极光女神真身显现，冰晶王座降临，极光天幕覆盖，冰雪风暴，世界冻结"),
    
    # Crimson (7个)
    ("crimson_blood", 80, 12, "绯红之刃血月降临", "血色光芒笼罩，血雾弥漫升腾，血液飞溅特效，嗜血气息"),
    ("crimson_vampire", 85, 11, "吸血鬼血族领主", "吸血蝙蝠环绕，血族纹章显现，血液吸收光束，暗夜猎食者"),
    ("crimson_blade", 95, 14, "血刃狂舞千刀万剐", "血色刀刃密布，刀光剑影交织，血刃风暴旋转，切割一切"),
    ("crimson_hell", 90, 13, "地狱血焰炼狱烈火", "血色火焰燃烧，地狱之火咆哮，血焰漩涡吞噬，炼狱化身"),
    ("crimson_scarlet", 102, 14, "猩红风暴血之狂潮", "猩红风暴肆虐，血浪翻涌席卷，血雨倾盆而下，血之海洋"),
    ("crimson_demon", 110, 15, "血魔降世魔王降临", "血魔之翼展开，血色魔纹遍布，魔王形态显现，血之君主"),
    ("crimson_eternal", 120, 16, "永恒血契不死之身", "永恒血契符文，不死形态显化，血液永恒循环，血之不朽，复活重生"),
    
    # Stalker (7个)
    ("stalker_stealth", 75, 11, "星界潜行隐匿追踪者", "星光扭曲隐形，空间褶皱潜行，追踪标记显现，无声猎杀"),
    ("stalker_shadow", 82, 12, "暗影刺客影之舞者", "影子形态切换，暗影分身术，黑暗步法飘忽，致命一击"),
    ("stalker_cosmic", 90, 13, "宇宙猎人星际追踪", "星际追踪装置，宇宙能量印记，空间跃迁轨迹，星光伪装"),
    ("stalker_void", 88, 12, "虚空潜伏无形存在", "虚空隐匿状态，存在感抹除，维度缝隙穿梭，虚无形态"),
    ("stalker_eclipse", 98, 14, "日食暗杀光暗交错", "日食现象伴随，光影交错隐匿，暗杀时刻降临，致命月影"),
    ("stalker_ghost", 105, 15, "幽灵刺客不可见者", "完全幽灵化，透明度极高，幽魂轨迹飘忽，灵魂刺客"),
    ("stalker_omega", 118, 16, "终极捕食完美猎手", "完美捕食者形态，终极隐匿技术，致命精准打击，猎杀时刻，无人生还"),
    
    # Gaia (7个)
    ("gaia_nature", 78, 12, "大地守护自然之力", "藤蔓缠绕机身，树木生长蔓延，花朵绽放飞舞，自然生机"),
    ("gaia_forest", 85, 11, "森林之母绿色守护", "森林植被覆盖，树冠枝叶繁茂，绿叶粒子飞扬，生命气息"),
    ("gaia_terra", 92, 13, "大地母神泰拉化身", "大地纹理显现，岩石土壤结构，地脉能量流动，母神之力"),
    ("gaia_bloom", 88, 12, "生命绽放百花盛开", "百花齐放特效，花瓣雨漫天飞舞，生命能量绽放，春意盎然"),
    ("gaia_ancient", 98, 14, "远古巨树世界之树", "世界树形态显现，树根深入虚空，枝叶遮天蔽日，远古之力"),
    ("gaia_terra_prime", 108, 15, "盖亚本源星球意志", "星球意志显化，地壳板块浮动，自然法则具现，造物主力量"),
    ("gaia_genesis", 120, 16, "创世纪生命起源", "创世之力爆发，生命起源之光，万物生长狂潮，基因密码显现，生命之树绽放"),
    
    # Weaver (7个)
    ("weaver_web", 75, 11, "虚空编织命运之网", "命运丝线交织，虚空之网编织，丝线粒子飘舞，命运编织者"),
    ("weaver_portal", 82, 12, "传送门空间裂隙", "空间传送门开启，裂隙纹理显现，传送能量波动，次元穿梭"),
    ("weaver_dimension", 90, 13, "维度行者多元宇宙", "多维度空间叠加，维度墙壁破碎，空间碎片漂浮，多元形态"),
    ("weaver_time", 88, 12, "时空织者时间之网", "时间线显现，时空网格交织，时间碎片飘散，时空扭曲"),
    ("weaver_reality", 98, 14, "现实扭曲改写法则", "现实法则重写，物理规则崩溃，空间结构改变，真理编织"),
    ("weaver_cosmic", 108, 15, "宇宙编织星河织布", "星河丝线编织，宇宙结构显化，星辰作为编织点，造物之手"),
    ("weaver_infinity", 122, 16, "无限编织万物起源", "无限符号显现，万物编码可见，宇宙源代码运行，终极编织者，创造与毁灭"),
]

for paint_id, particle, trail_w, new_name, new_desc in updates:
    pattern = rf'("{paint_id}":\s*\{{[^}}]+?"name":\s*")[^"]+(",[^}}]+?"desc":\s*")[^"]+(",[^}}]+?"particle_count":\s*)\d+([^}}]+?"trail_width":\s*)\d+'
    
    def replacer(match):
        return f'{match.group(1)}{new_name}{match.group(2)}{new_desc}{match.group(3)}{particle}{match.group(4)}{trail_w}'
    
    content = re.sub(pattern, replacer, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated 35 more exclusive themes (Aurora, Crimson, Stalker, Gaia, Weaver)!")
