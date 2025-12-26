"""
配置迁移工具

将 config.py 中的硬编码数据迁移到 JSON 配置文件

使用方式:
    python tools/config_migrator.py

功能:
    1. 导出机体配置到 data/planes/*.json
    2. 导出颜色配置到 data/ui/colors.json
    3. 生成涂装配置骨架
"""
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ConfigMigrator:
    """配置迁移器"""
    
    def __init__(self):
        self.data_dir = PROJECT_ROOT / "data"
        self.planes_dir = self.data_dir / "planes"
        self.skins_dir = self.data_dir / "skins"
        self.ui_dir = self.data_dir / "ui"
        
        # 确保目录存在
        self.planes_dir.mkdir(parents=True, exist_ok=True)
        self.skins_dir.mkdir(parents=True, exist_ok=True)
        self.ui_dir.mkdir(parents=True, exist_ok=True)
    
    def export_planes(self):
        """导出所有机体配置"""
        print("\n=== 导出机体配置 ===\n")
        
        from config import PLANES
        
        count = 0
        for plane_id, plane_data in PLANES.items():
            config = self._convert_plane_config(plane_id, plane_data)
            
            output_path = self.planes_dir / f"{plane_id}.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"  [OK] {plane_id}.json")
            count += 1
        
        print(f"\n完成: 导出 {count} 个机体配置")
    
    def _convert_plane_config(self, plane_id: str, data: dict) -> dict:
        """转换机体配置格式"""
        color = data.get("color", (0, 255, 255))
        visual = data.get("visual", {})
        
        return {
            "$schema": "./_schema.json",
            "id": plane_id,
            "name": data.get("name", plane_id),
            "name_en": plane_id.replace("_", " ").title(),
            "description": data.get("desc", ""),
            "tier": self._guess_tier(plane_id),
            "rarity": self._guess_rarity(plane_id),
            
            "stats": {
                "hp": data.get("hp", 100),
                "speed": data.get("speed", 4.0),
                "damage": data.get("damage", 10),
                "fire_rate": data.get("delay", 180),
                "shield": 0,
                "crit_rate": 0.05,
                "crit_damage": 1.5
            },
            
            "visuals": {
                "sprite_path": f"sprites/planes/{plane_id}/default.png",
                "sprite_size": [120, 120],
                "fallback_renderer": plane_id,
                "colors": {
                    "primary": self._rgb_to_hex(visual.get("neon_color", color)),
                    "secondary": self._rgb_to_hex(visual.get("accent_color", (255, 215, 0))),
                    "glow": self._rgb_to_hex(visual.get("neon_color", color)),
                    "trail": self._rgb_to_hex(visual.get("trail_color", color))
                }
            },
            
            "abilities": {
                "passive": {
                    "id": visual.get("ability", "none"),
                    "name": "",
                    "description": ""
                },
                "ultimate": {
                    "id": data.get("ult_name", "").lower().replace(" ", "_"),
                    "name": data.get("ult_name", ""),
                    "color": self._rgb_to_hex(data.get("ult_color", color)),
                    "damage_multiplier": 5.0,
                    "cooldown": 15.0
                }
            },
            
            "bullet": {
                "type": data.get("bullet_type", "default"),
                "sprite_path": f"sprites/bullets/{data.get('bullet_type', 'default')}.png",
                "sound": "shoot"
            },
            
            "unlock": {
                "type": "default",
                "condition": None
            }
        }
    
    def _guess_tier(self, plane_id: str) -> int:
        """根据机体ID猜测等级"""
        tier1 = ["striker", "phantom", "titan", "thunderbird", "viper", 
                 "specter", "aurora", "crimson", "stalker"]
        tier2 = ["gaia", "weaver", "solar", "arbiter"]
        tier3 = ["eclipse", "prism", "necro", "wormhole"]
        tier4 = ["chronos", "mirage", "gambit"]
        tier5 = ["puppeteer", "pandemic", "omega", "genesis", "truth"]
        
        if plane_id in tier1:
            return 1
        elif plane_id in tier2:
            return 2
        elif plane_id in tier3:
            return 3
        elif plane_id in tier4:
            return 4
        elif plane_id in tier5:
            return 5
        return 1
    
    def _guess_rarity(self, plane_id: str) -> int:
        """根据机体ID猜测稀有度"""
        tier = self._guess_tier(plane_id)
        return min(tier + 1, 6)
    
    def _rgb_to_hex(self, rgb) -> str:
        """RGB转十六进制"""
        if isinstance(rgb, str):
            return rgb
        if rgb is None:
            return "#FFFFFF"
        r, g, b = rgb[:3]
        return f"#{r:02X}{g:02X}{b:02X}"
    
    def export_colors(self):
        """导出颜色配置"""
        print("\n=== 导出颜色配置 ===\n")
        
        # 读取config.py中的颜色定义
        import config
        
        colors = {}
        for name in dir(config):
            value = getattr(config, name)
            # 检查是否是颜色元组
            if isinstance(value, tuple) and len(value) >= 3:
                if all(isinstance(v, int) and 0 <= v <= 255 for v in value[:3]):
                    # 跳过一些不是颜色的元组
                    if name.startswith("_") or name in ["WIDTH", "HEIGHT", "FPS"]:
                        continue
                    colors[name.lower()] = self._rgb_to_hex(value)
        
        # 组织成层次结构
        palette = {
            "background": {},
            "primary": {},
            "accent": {},
            "alert": {},
            "rarity": {},
            "ui": {},
            "gameplay": {},
            "legacy": {}
        }
        
        for name, hex_color in colors.items():
            if "bg" in name or "black" in name or "dark" in name or "midnight" in name:
                palette["background"][name] = hex_color
            elif "cyan" in name:
                palette["primary"][name] = hex_color
            elif "red" in name or "alert" in name or "danger" in name:
                palette["alert"][name] = hex_color
            elif "rarity" in name:
                palette["rarity"][name] = hex_color
            elif any(x in name for x in ["lime", "amber", "magenta", "orange", "purple", "gold"]):
                palette["accent"][name] = hex_color
            else:
                palette["legacy"][name] = hex_color
        
        output = {
            "theme": "cyberpunk",
            "version": "1.0",
            "palette": palette
        }
        
        output_path = self.ui_dir / "colors.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"  [OK] colors.json ({len(colors)} 个颜色)")
    
    def generate_skin_skeleton(self):
        """生成涂装配置骨架"""
        print("\n=== 生成涂装配置骨架 ===\n")
        
        from config import PLANES
        
        count = 0
        for plane_id in PLANES.keys():
            output_path = self.skins_dir / f"{plane_id}_skins.json"
            
            # 如果已存在则跳过
            if output_path.exists():
                print(f"  [SKIP] {plane_id}_skins.json (已存在)")
                continue
            
            skeleton = {
                "$schema": "./_schema.json",
                "plane_id": plane_id,
                "skins": [
                    {
                        "id": f"{plane_id}_default",
                        "name": "标准涂装",
                        "name_en": "Default",
                        "rarity": 1,
                        "unlock_type": "default",
                        "sprite_override": None,
                        "color_override": None,
                        "particle_effects": [],
                        "stat_bonus": None
                    }
                ]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(skeleton, f, indent=2, ensure_ascii=False)
            
            print(f"  [OK] {plane_id}_skins.json")
            count += 1
        
        print(f"\n完成: 生成 {count} 个涂装配置骨架")


def main():
    """主函数"""
    migrator = ConfigMigrator()
    
    # 支持命令行参数
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("=" * 50)
        print("        配置迁移工具 v1.0")
        print("=" * 50)
        print("\n请选择操作:\n")
        print("  1. 导出机体配置")
        print("  2. 导出颜色配置")
        print("  3. 生成涂装配置骨架")
        print("  4. 执行全部")
        print("  0. 退出")
        print()
        
        choice = input("请输入选项 (0-4): ").strip()
    
    if choice == "1":
        migrator.export_planes()
    
    elif choice == "2":
        migrator.export_colors()
    
    elif choice == "3":
        migrator.generate_skin_skeleton()
    
    elif choice == "4" or choice == "all":
        migrator.export_planes()
        migrator.export_colors()
        migrator.generate_skin_skeleton()
    
    elif choice == "0":
        print("再见!")
        return
    
    else:
        print("无效选项")
        return
    
    print("\n操作完成!")


if __name__ == "__main__":
    main()
