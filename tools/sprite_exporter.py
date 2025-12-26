"""
精灵导出工具

将程序化绘制的机体、子弹、敌人导出为PNG精灵图
用于迁移到资产管理系统

使用方式:
    python tools/sprite_exporter.py

选项:
    1. 导出所有机体精灵
    2. 导出指定机体
    3. 导出所有涂装
    4. 生成精灵清单
"""
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pygame
pygame.init()
# 创建一个隐藏的显示窗口（某些Surface操作需要）
pygame.display.set_mode((1, 1), pygame.HIDDEN)

from config import PLANES
from utils.planes import get_plane_surf


class SpriteExporter:
    """精灵导出器"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or PROJECT_ROOT / "assets" / "sprites")
        self.exported_count = 0
        self.failed_count = 0
        self.manifest = {"version": "1.0", "sprites": {}}
    
    def export_plane(self, plane_id: str, visual: dict = None, 
                     skin_id: str = "default") -> bool:
        """
        导出单个机体精灵
        
        Args:
            plane_id: 机体ID
            visual: 视觉配置
            skin_id: 涂装ID
        
        Returns:
            是否成功
        """
        output_path = self.output_dir / "planes" / plane_id / f"{skin_id}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # 获取机体Surface
            surf = get_plane_surf(plane_id, visual, static=True)
            
            if surf is None:
                print(f"  [SKIP] {plane_id}/{skin_id}: 无法生成Surface")
                return False
            
            # 保存为PNG
            pygame.image.save(surf, str(output_path))
            
            # 记录到清单
            rel_path = f"planes/{plane_id}/{skin_id}.png"
            self.manifest["sprites"][rel_path] = {
                "width": surf.get_width(),
                "height": surf.get_height(),
                "plane_id": plane_id,
                "skin_id": skin_id
            }
            
            self.exported_count += 1
            print(f"  [OK] {rel_path}")
            return True
            
        except Exception as e:
            self.failed_count += 1
            print(f"  [FAIL] {plane_id}/{skin_id}: {e}")
            return False
    
    def export_all_planes(self):
        """导出所有机体的默认涂装"""
        print("\n=== 导出机体精灵 ===\n")
        
        for plane_id, plane_data in PLANES.items():
            visual = plane_data.get("visual", {})
            visual["neon_color"] = plane_data.get("color", (0, 255, 255))
            self.export_plane(plane_id, visual, "default")
        
        print(f"\n完成: 成功 {self.exported_count}, 失败 {self.failed_count}")
    
    def export_plane_with_skins(self, plane_id: str):
        """导出指定机体的所有涂装"""
        print(f"\n=== 导出 {plane_id} 所有涂装 ===\n")
        
        if plane_id not in PLANES:
            print(f"错误: 未找到机体 {plane_id}")
            return
        
        plane_data = PLANES[plane_id]
        
        # 导出默认涂装
        visual = plane_data.get("visual", {})
        visual["neon_color"] = plane_data.get("color", (0, 255, 255))
        self.export_plane(plane_id, visual, "default")
        
        # 尝试加载涂装配置
        skin_config_path = PROJECT_ROOT / "data" / "skins" / f"{plane_id}_skins.json"
        if skin_config_path.exists():
            with open(skin_config_path, 'r', encoding='utf-8') as f:
                skin_data = json.load(f)
            
            for skin in skin_data.get("skins", []):
                skin_id = skin.get("id", "").replace(f"{plane_id}_", "")
                if skin_id == "default":
                    continue
                
                # 构建视觉配置
                skin_visual = visual.copy()
                if skin.get("color_override"):
                    colors = skin["color_override"]
                    if colors.get("primary"):
                        skin_visual["neon_color"] = self._hex_to_rgb(colors["primary"])
                    if colors.get("secondary"):
                        skin_visual["accent_color"] = self._hex_to_rgb(colors["secondary"])
                
                # 设置model_style以触发涂装渲染
                skin_visual["model_style"] = skin.get("fallback_renderer", skin_id)
                
                self.export_plane(plane_id, skin_visual, skin_id)
        
        print(f"\n完成: 成功 {self.exported_count}, 失败 {self.failed_count}")
    
    def export_all_with_skins(self):
        """导出所有机体及其所有涂装"""
        print("\n=== 导出所有机体和涂装 ===\n")
        
        for plane_id in PLANES.keys():
            print(f"\n--- {plane_id} ---")
            self.export_plane_with_skins(plane_id)
        
        print(f"\n总计: 成功 {self.exported_count}, 失败 {self.failed_count}")
    
    def generate_manifest(self):
        """生成精灵清单文件"""
        manifest_path = self.output_dir / "manifest.json"
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
        
        print(f"\n清单已保存: {manifest_path}")
        print(f"共 {len(self.manifest['sprites'])} 个精灵")
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """十六进制转RGB"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def main():
    """主函数"""
    exporter = SpriteExporter()
    
    # 支持命令行参数
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("=" * 50)
        print("        精灵导出工具 v1.0")
        print("=" * 50)
        print("\n请选择操作:\n")
        print("  1. 导出所有机体 (默认涂装)")
        print("  2. 导出指定机体 (所有涂装)")
        print("  3. 导出全部 (所有机体+所有涂装)")
        print("  4. 仅生成清单文件")
        print("  0. 退出")
        print()
        
        choice = input("请输入选项 (0-4): ").strip()
    
    if choice == "1" or choice == "planes":
        exporter.export_all_planes()
        exporter.generate_manifest()
    
    elif choice == "2":
        print(f"\n可用机体: {', '.join(PLANES.keys())}\n")
        plane_id = input("请输入机体ID: ").strip()
        exporter.export_plane_with_skins(plane_id)
        exporter.generate_manifest()
    
    elif choice == "3" or choice == "all":
        exporter.export_all_with_skins()
        exporter.generate_manifest()
    
    elif choice == "4" or choice == "manifest":
        # 扫描已有文件生成清单
        sprites_dir = exporter.output_dir
        for png_file in sprites_dir.rglob("*.png"):
            rel_path = png_file.relative_to(sprites_dir).as_posix()
            try:
                img = pygame.image.load(str(png_file))
                exporter.manifest["sprites"][rel_path] = {
                    "width": img.get_width(),
                    "height": img.get_height()
                }
            except:
                pass
        exporter.generate_manifest()
    
    elif choice == "0":
        print("再见!")
        return
    
    else:
        print("无效选项")
        return
    
    print("\n操作完成!")


if __name__ == "__main__":
    main()
