#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BOSS 数据导出工具
将 config.py 中的 BOSS_DB 导出为 JSON 文件
"""

import sys
import os
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
sys.path.insert(0, '..')

from config import BOSS_DB

def rgb_to_hex(rgb):
    """RGB 转 十六进制"""
    if isinstance(rgb, tuple) and len(rgb) >= 3:
        return "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])
    return rgb

def export_boss(boss_id, boss_data):
    """导出单个 Boss 配置"""
    visual = boss_data.get("visual", {})
    
    config = {
        "$schema": "./_boss_schema.json",
        "id": boss_id,
        "name": boss_data.get("name", boss_id),
        "description": boss_data.get("desc", ""),
        "stats": {
            "armor": next((s[1] for s in boss_data.get("stats", []) if s[0] == "装甲"), 100),
            "damage": next((s[1] for s in boss_data.get("stats", []) if s[0] == "毁灭"), 100),
            "mobility": next((s[1] for s in boss_data.get("stats", []) if s[0] == "机动"), 50),
        },
        "visuals": {
            "colors": {
                "primary": rgb_to_hex(boss_data.get("color", (255, 255, 255))),
                "core": rgb_to_hex(visual.get("core_color", boss_data.get("color", (255, 255, 255)))),
                "aura": rgb_to_hex(visual.get("aura", (255, 255, 255))),
            },
            "phase_effect": visual.get("phase_effect", "")
        },
        "phases": boss_data.get("phases", [])
    }
    
    return config

def main():
    output_dir = "../data/bosses"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("BOSS 数据导出工具")
    print("=" * 60)
    
    exported = 0
    for boss_id, boss_data in BOSS_DB.items():
        config = export_boss(boss_id, boss_data)
        
        output_path = os.path.join(output_dir, f"{boss_id}.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ {boss_id}: {boss_data.get('name', boss_id)}")
        exported += 1
    
    # 创建 schema
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Boss 配置 Schema",
        "type": "object",
        "required": ["id", "name", "stats", "visuals", "phases"],
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "description": {"type": "string"},
            "stats": {
                "type": "object",
                "properties": {
                    "armor": {"type": "integer"},
                    "damage": {"type": "integer"},
                    "mobility": {"type": "integer"}
                }
            },
            "visuals": {
                "type": "object",
                "properties": {
                    "colors": {"type": "object"},
                    "phase_effect": {"type": "string"}
                }
            },
            "phases": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "threshold": {"type": "number"},
                        "effect": {"type": "object"},
                        "fire_rate_mult": {"type": "number"}
                    }
                }
            }
        }
    }
    
    schema_path = os.path.join(output_dir, "_boss_schema.json")
    with open(schema_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print(f"\n导出完成: {exported} 个 Boss")
    print(f"输出目录: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
