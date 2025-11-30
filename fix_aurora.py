import re

file_path = r"c:\Users\真夜中\Desktop\newPlane\customization.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 真实存在的涂装ID和更新数据
updates = [
    # Aurora (已有goddess=122，需要更新其余6个)
    ("aurora_nebula", 82, 13, "星云之心宇宙梦境", "星云纹理流动，星尘粒子暴雨，宇宙梦境显现，星云美学"),
    ("aurora_ice_queen", 90, 14, "冰雪女王永冻领域", "冰晶王冠高耸，冰霜领域扩张，冰雪女王降临，永冻统治"),
    ("aurora_rainbow", 98, 14, "彩虹织者七色天桥", "七彩光芒交织，彩虹尾迹绚烂，彩虹桥架起，色彩风暴"),
    ("aurora_prism", 105, 15, "棱镜光辉折射万象", "水晶棱镜结构，光芒无限折射，万象光辉，璀璨夺目"),
    ("aurora_sakura", 112, 15, "樱花女神春之降临", "樱花暴雨飞舞，粉色花瓣海洋，春天女神显现，生命绽放"),
    ("aurora_celestial", 120, 16, "天界使者神圣降临", "天使光环闪耀，圣洁羽翼展开，天界之门打开，神圣力量"),
    
    # Crimson (已更新blood=80，需更新其余)
    # ... (已经在前面批处理完成了，跳过)
]

for paint_id, particle, trail_w, new_name, new_desc in updates:
    pattern = rf'("{paint_id}":\s*\{{[^}}]+?"name":\s*")[^"]+(",[^}}]+?"desc":\s*")[^"]+(",[^}}]+?"particle_count":\s*)\d+([^}}]+?"trail_width":\s*)\d+'
    
    def replacer(match):
        return f'{match.group(1)}{new_name}{match.group(2)}{new_desc}{match.group(3)}{particle}{match.group(4)}{trail_w}'
    
    content = re.sub(pattern, replacer, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed remaining Aurora themes!")
