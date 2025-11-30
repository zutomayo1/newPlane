import re

with open(r"c:\Users\真夜中\Desktop\newPlane\customization.py", "r", encoding="utf-8") as f:
    content = f.read()

# 提取所有专属涂装块
pattern = r'"([a-z_]+)":\s*\{[^}]+?"particle_count":\s*(\d+),[^}]+?"exclusive_plane":\s*"([a-z]+)"'
matches = re.findall(pattern, content, re.DOTALL)

low_particle = [(paint_id, int(count), plane) for paint_id, count, plane in matches if int(count) < 70]

print(f"找到 {len(low_particle)} 个低粒子数专属涂装:\n")
for pid, count, plane in sorted(low_particle, key=lambda x: x[2]):
    print(f"{plane:15} | {pid:30} | particle_count: {count}")
