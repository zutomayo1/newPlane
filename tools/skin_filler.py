#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
皮肤配置填充工具
从 customization.py 的 PAINT_THEMES 提取机体专属皮肤，填充到 data/skins/*.json
"""

import sys
import os
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from customization import PAINT_THEMES
from config import PLANES


def rgb_to_hex(rgb):
    """RGB 转十六进制"""
    if isinstance(rgb, tuple) and len(rgb) >= 3:
        return "#{:02X}{:02X}{:02X}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    return rgb


def get_rarity_from_category(category):
    """从 category 获取稀有度"""
    mapping = {
        "default": 1,
        "common": 1,
        "rare": 2,
        "epic": 3,
        "legendary": 4,
        "exclusive": 4,
        "mythic": 5,
        "supreme": 6,
    }
    return mapping.get(category, 3)


def create_skin_entry(skin_id, theme_data, plane_id):
    """创建皮肤配置条目"""
    # 生成简短 ID（移除机体前缀）
    short_id = skin_id.replace(f"{plane_id}_", "")
    
    skin = {
        "id": skin_id,
        "name": theme_data.get("name", short_id),
        "name_en": short_id.replace("_", " ").title(),
        "rarity": get_rarity_from_category(theme_data.get("category", "rare")),
        "unlock_type": "shop" if theme_data.get("cost", 0) > 0 else "default",
        "unlock_condition": None,
        "cost": theme_data.get("cost", 0),
        "sprite_override": f"sprites/planes/{plane_id}/{short_id}.png",
        "fallback_renderer": theme_data.get("model_style", short_id),
        "color_override": {
            "primary": rgb_to_hex(theme_data.get("neon_color", (255, 255, 255))),
            "secondary": rgb_to_hex(theme_data.get("accent_color", (255, 255, 255))),
            "glow": rgb_to_hex(theme_data.get("neon_color", (255, 255, 255))),
            "trail": rgb_to_hex(theme_data.get("trail_color", (255, 255, 255))),
        },
        "trail_style": theme_data.get("trail_style", "normal"),
        "trail_width": theme_data.get("trail_width", 2),
        "particle_count": theme_data.get("particle_count", 10),
        "animated": theme_data.get("animated", False),
        "particle_effects": [],
        "stat_bonus": None
    }
    
    return skin


def main():
    print("=" * 60)
    print("皮肤配置填充工具")
    print("=" * 60)
    
    # 收集每个机体的专属皮肤
    plane_skins = {plane_id: [] for plane_id in PLANES.keys()}
    
    for skin_id, theme_data in PAINT_THEMES.items():
        # 检查是否是机体专属皮肤
        exclusive_plane = theme_data.get("exclusive_plane")
        
        if exclusive_plane and exclusive_plane in plane_skins:
            plane_skins[exclusive_plane].append((skin_id, theme_data))
        else:
            # 尝试从 ID 推断机体
            for plane_id in PLANES.keys():
                if skin_id.startswith(f"{plane_id}_"):
                    plane_skins[plane_id].append((skin_id, theme_data))
                    break
    
    # 更新每个机体的皮肤配置
    updated_count = 0
    total_skins = 0
    
    for plane_id, skins in plane_skins.items():
        if not skins:
            continue
        
        json_path = PROJECT_ROOT / "data" / "skins" / f"{plane_id}_skins.json"
        
        # 加载现有配置
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {
                "$schema": "./_schema.json",
                "plane_id": plane_id,
                "skins": []
            }
        
        # 获取已有皮肤 ID
        existing_ids = {s["id"] for s in config.get("skins", [])}
        
        # 确保有默认皮肤
        if f"{plane_id}_default" not in existing_ids:
            default_skin = {
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
            config["skins"].insert(0, default_skin)
            existing_ids.add(f"{plane_id}_default")
        
        # 添加新皮肤
        added = 0
        for skin_id, theme_data in skins:
            if skin_id not in existing_ids:
                skin_entry = create_skin_entry(skin_id, theme_data, plane_id)
                config["skins"].append(skin_entry)
                added += 1
                total_skins += 1
        
        if added > 0:
            # 保存更新后的配置
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ {plane_id}: +{added} 皮肤 (共 {len(config['skins'])})")
            updated_count += 1
    
    print(f"\n更新完成: {updated_count} 个机体, 新增 {total_skins} 个皮肤")


if __name__ == "__main__":
    main()
