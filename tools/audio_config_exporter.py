"""
音频配置导出工具

将音频合成器的硬编码配置导出到JSON文件
"""
import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def export_bgm_presets():
    """导出BGM预设配置到JSON"""
    from utils.audio import AudioSynthesizer
    synth = AudioSynthesizer()
    
    # 基础BGM预设（hardcoded in get_track_bpm）
    base_presets = {
        "normal": {"bpm": 120, "roots": [110.0, 123.47, 146.83, 130.81], "mix": 0.50, "category": "explore"},
        "boss": {"bpm": 170, "roots": [55.0, 65.41, 49.0, 73.42], "mix": 0.58, "category": "boss"},
        "calm": {"bpm": 90, "roots": [110.0, 123.47, 98.0, 130.81], "mix": 0.44, "category": "menu"},
        "mystery": {"bpm": 100, "roots": [82.41, 92.50, 73.42, 98.0], "mix": 0.46, "category": "explore"},
        "epic": {"bpm": 150, "roots": [82.41, 92.50, 98.0, 110.0], "mix": 0.54, "category": "combat"},
        "intense": {"bpm": 140, "roots": [55.0, 65.41, 73.42, 61.74], "mix": 0.56, "category": "combat"},
        "cyber": {"bpm": 128, "roots": [55.0, 65.41, 73.42, 61.74], "mix": 0.52, "category": "explore"},
        "ethereal": {"bpm": 80, "roots": [110.0, 123.47, 146.83, 130.81], "mix": 0.44, "category": "menu"},
    }
    
    # 获取扩展预设
    extended = synth._EXTENDED_BGM_PRESETS.copy()
    
    # 合并所有预设
    all_presets = {}
    
    # 添加基础预设
    for track_id, preset in base_presets.items():
        all_presets[track_id] = preset
    
    # 添加扩展预设（添加category）
    for track_id, preset in extended.items():
        if track_id not in all_presets:
            # 推断category
            if track_id.startswith("menu_"):
                category = "menu"
            elif track_id.startswith("explore_"):
                category = "explore"
            elif track_id.startswith("combat_"):
                category = "combat"
            elif track_id.startswith("boss"):
                category = "boss"
            elif track_id.startswith("victory"):
                category = "victory"
            else:
                # 根据bpm推断
                bpm = preset.get("bpm", 120)
                if bpm < 90:
                    category = "menu"
                elif bpm < 130:
                    category = "explore"
                elif bpm < 160:
                    category = "combat"
                else:
                    category = "boss"
            
            all_presets[track_id] = {
                **preset,
                "category": category
            }
    
    # 构建manifest
    manifest = {
        "version": "1.0",
        "base_path": "assets/audio/bgm",
        "tracks": {}
    }
    
    for track_id, preset in sorted(all_presets.items()):
        manifest["tracks"][track_id] = {
            "file": f"bgm_{track_id}.wav",
            "bpm": preset.get("bpm", 120),
            "roots": preset.get("roots", [110.0, 123.47, 146.83, 130.81]),
            "mix": preset.get("mix", 0.50),
            "category": preset.get("category", "explore")
        }
    
    # 保存
    output_path = PROJECT_ROOT / "data" / "audio" / "bgm_manifest.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"导出 {len(manifest['tracks'])} 个BGM预设到 {output_path}")
    return manifest


def export_sfx_presets():
    """导出SFX合成参数到JSON"""
    # 音效合成参数（从generate_all方法推断）
    sfx_presets = {
        "shoot": {
            "type": "tone",
            "description": "射击音效",
            "params": {"freq": 800, "duration": 0.08, "wave": "square", "envelope": "sharp"}
        },
        "explosion": {
            "type": "noise",
            "description": "爆炸音效",
            "params": {"duration": 0.4, "envelope": "decay"}
        },
        "hit": {
            "type": "tone",
            "description": "击中音效",
            "params": {"freq": 200, "duration": 0.1, "wave": "noise", "envelope": "sharp"}
        },
        "laser": {
            "type": "sweep",
            "description": "激光音效",
            "params": {"freq_start": 1200, "freq_end": 400, "duration": 0.15}
        },
        "levelup": {
            "type": "arpeggio",
            "description": "升级音效",
            "params": {"notes": [523, 659, 784, 1047], "duration": 0.5}
        },
        "item_pickup": {
            "type": "tone",
            "description": "拾取物品",
            "params": {"freq": 880, "duration": 0.1, "wave": "sine"}
        },
        "warning": {
            "type": "pulse",
            "description": "警告音效",
            "params": {"freq": 440, "duration": 0.3, "pulses": 3}
        },
        "shield": {
            "type": "tone",
            "description": "护盾音效",
            "params": {"freq": 300, "duration": 0.2, "wave": "sine", "modulation": True}
        },
        "heal": {
            "type": "sweep",
            "description": "治疗音效",
            "params": {"freq_start": 400, "freq_end": 800, "duration": 0.3}
        },
        "critical": {
            "type": "impact",
            "description": "暴击音效",
            "params": {"freq": 150, "duration": 0.15}
        },
        "dash": {
            "type": "whoosh",
            "description": "冲刺音效",
            "params": {"duration": 0.2}
        },
        "freeze": {
            "type": "crystal",
            "description": "冰冻音效",
            "params": {"freq": 2000, "duration": 0.25}
        },
        "zap": {
            "type": "electric",
            "description": "电击音效",
            "params": {"duration": 0.15}
        },
        "nuke": {
            "type": "explosion",
            "description": "核爆音效",
            "params": {"duration": 0.8, "intensity": 1.0}
        },
        "blackhole": {
            "type": "rumble",
            "description": "黑洞音效",
            "params": {"duration": 0.5, "freq": 50}
        },
        "graze": {
            "type": "whoosh",
            "description": "擦弹音效",
            "params": {"duration": 0.1, "intensity": 0.3}
        },
        "sniper_charge": {
            "type": "charge",
            "description": "狙击蓄力",
            "params": {"duration": 0.5, "freq_start": 200, "freq_end": 1000}
        },
        "select": {
            "type": "click",
            "description": "选择音效",
            "params": {"freq": 600, "duration": 0.05}
        },
        "gameover": {
            "type": "descend",
            "description": "游戏结束",
            "params": {"duration": 1.0}
        },
        "achievement": {
            "type": "fanfare",
            "description": "成就音效",
            "params": {"notes": [523, 659, 784], "duration": 0.6}
        },
        "stinger_victory": {
            "type": "stinger",
            "description": "胜利音效",
            "params": {"style": "victory", "duration": 2.0}
        },
        "stinger_defeat": {
            "type": "stinger",
            "description": "失败音效",
            "params": {"style": "defeat", "duration": 1.5}
        },
        "stinger_boss_phase": {
            "type": "stinger",
            "description": "Boss阶段转换",
            "params": {"style": "boss_phase", "duration": 1.0}
        }
    }
    
    manifest = {
        "version": "1.0",
        "description": "音效合成参数配置",
        "presets": sfx_presets
    }
    
    output_path = PROJECT_ROOT / "data" / "audio" / "sfx_presets.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"导出 {len(sfx_presets)} 个SFX预设到 {output_path}")
    return manifest


def main():
    print("=" * 50)
    print("       音频配置导出工具")
    print("=" * 50)
    
    print("\n[1/2] 导出BGM预设...")
    bgm = export_bgm_presets()
    
    print("\n[2/2] 导出SFX预设...")
    sfx = export_sfx_presets()
    
    print("\n" + "=" * 50)
    print("导出完成!")
    print(f"  BGM: {len(bgm['tracks'])} 个")
    print(f"  SFX: {len(sfx['presets'])} 个")
    print("=" * 50)


if __name__ == "__main__":
    main()
