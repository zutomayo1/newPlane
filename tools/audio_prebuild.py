"""
音频预构建工具

将程序化合成的音效和BGM预先生成并保存到assets目录
避免每次启动游戏都需要重新合成

使用方式:
    python tools/audio_prebuild.py

选项:
    1. 生成所有音效 (SFX)
    2. 生成所有背景音乐 (BGM)
    3. 生成全部
    4. 生成指定BGM
"""
import os
import sys
import shutil
import json
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pygame
pygame.init()
pygame.mixer.init()


class AudioPrebuilder:
    """音频预构建器"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or PROJECT_ROOT / "assets" / "audio")
        self.sfx_dir = self.output_dir / "sfx"
        self.bgm_dir = self.output_dir / "bgm"
        
        # 确保目录存在
        self.sfx_dir.mkdir(parents=True, exist_ok=True)
        self.bgm_dir.mkdir(parents=True, exist_ok=True)
        
        self.generated_sfx = []
        self.generated_bgm = []
    
    def generate_all_sfx(self):
        """生成所有音效"""
        print("\n=== 生成音效 ===\n")
        
        from utils.audio import AudioSynthesizer
        synth = AudioSynthesizer()
        paths = synth.generate_all()
        
        sfx_count = 0
        for name, path in paths.items():
            if not path or not os.path.exists(path):
                continue
            
            # 跳过BGM和图层
            if name.startswith("bgm") or name.startswith("layer_"):
                continue
            
            dest = self.sfx_dir / os.path.basename(path)
            shutil.copy2(path, dest)
            self.generated_sfx.append(name)
            sfx_count += 1
            print(f"  [OK] {name} -> {dest.name}")
        
        print(f"\n音效生成完成: {sfx_count} 个文件")
        return sfx_count
    
    def generate_all_bgm(self):
        """生成所有BGM"""
        print("\n=== 生成背景音乐 ===\n")
        print("注意: BGM生成较慢，请耐心等待...\n")
        
        from utils.audio import AudioSynthesizer
        synth = AudioSynthesizer()
        
        # 获取所有BGM ID
        bgm_ids = synth.get_bgm_track_ids()
        
        bgm_count = 0
        for track_id in bgm_ids:
            print(f"  正在生成: {track_id}...", end=" ", flush=True)
            try:
                path = synth.ensure_bgm_generated(track_id)
                if path and os.path.exists(path):
                    dest = self.bgm_dir / f"bgm_{track_id}.wav"
                    shutil.copy2(path, dest)
                    self.generated_bgm.append(track_id)
                    bgm_count += 1
                    print("[OK]")
                else:
                    print("[SKIP]")
            except Exception as e:
                print(f"[FAIL] {e}")
        
        print(f"\nBGM生成完成: {bgm_count} 个文件")
        return bgm_count
    
    def generate_specific_bgm(self, track_id: str):
        """生成指定BGM"""
        print(f"\n=== 生成BGM: {track_id} ===\n")
        
        from utils.audio import AudioSynthesizer
        synth = AudioSynthesizer()
        
        try:
            path = synth.ensure_bgm_generated(track_id)
            if path and os.path.exists(path):
                dest = self.bgm_dir / f"bgm_{track_id}.wav"
                shutil.copy2(path, dest)
                print(f"  [OK] {track_id} -> {dest}")
                return True
            else:
                print(f"  [FAIL] 无法生成 {track_id}")
                return False
        except Exception as e:
            print(f"  [FAIL] {e}")
            return False
    
    def generate_sfx_manifest(self):
        """生成音效清单文件"""
        manifest = {
            "version": "1.0",
            "base_path": "assets/audio/sfx",
            "sounds": {}
        }
        
        # 默认音量配置
        volume_map = {
            "shoot": 0.15,
            "warning": 0.8,
            "explosion": 0.6,
            "levelup": 0.5,
            "achievement": 0.6,
            "item_pickup": 0.4,
            "critical": 0.5,
            "heal": 0.4,
            "shield": 0.45,
            "hit": 0.5,
            "select": 0.3,
            "confirm": 0.4,
            "cancel": 0.3,
            "gameover": 0.7,
            "stinger_victory": 0.85,
            "stinger_defeat": 0.8,
            "stinger_boss_phase": 0.85,
        }
        
        for sfx_file in self.sfx_dir.glob("*.wav"):
            name = sfx_file.stem
            manifest["sounds"][name] = {
                "file": sfx_file.name,
                "volume": volume_map.get(name, 0.5)
            }
        
        manifest_path = PROJECT_ROOT / "data" / "audio" / "sfx_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"\n音效清单已保存: {manifest_path}")
    
    def generate_bgm_manifest(self):
        """生成BGM清单文件"""
        from utils.audio import AudioSynthesizer
        synth = AudioSynthesizer()
        
        manifest = {
            "version": "1.0",
            "base_path": "assets/audio/bgm",
            "tracks": {}
        }
        
        for bgm_file in self.bgm_dir.glob("*.wav"):
            # 从文件名提取track_id
            name = bgm_file.stem
            if name.startswith("bgm_"):
                track_id = name[4:]
            else:
                track_id = name
            
            # 获取BPM信息
            presets = synth._EXTENDED_BGM_PRESETS
            bpm = 120
            if track_id in presets:
                bpm = presets[track_id].get("bpm", 120)
            
            manifest["tracks"][track_id] = {
                "file": bgm_file.name,
                "bpm": bpm
            }
        
        manifest_path = PROJECT_ROOT / "data" / "audio" / "bgm_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"BGM清单已保存: {manifest_path}")


def main():
    """主函数"""
    builder = AudioPrebuilder()
    
    # 支持命令行参数
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("=" * 50)
        print("        音频预构建工具 v1.0")
        print("=" * 50)
        print("\n请选择操作:\n")
        print("  1. 生成所有音效 (SFX)")
        print("  2. 生成所有背景音乐 (BGM) [较慢]")
        print("  3. 生成全部")
        print("  4. 生成指定BGM")
        print("  5. 仅生成清单文件")
        print("  0. 退出")
        print()
        
        choice = input("请输入选项 (0-5): ").strip()
    
    if choice == "1" or choice == "sfx":
        builder.generate_all_sfx()
        builder.generate_sfx_manifest()
    
    elif choice == "2" or choice == "bgm":
        builder.generate_all_bgm()
        builder.generate_bgm_manifest()
    
    elif choice == "3" or choice == "all":
        builder.generate_all_sfx()
        builder.generate_sfx_manifest()
        print()
        builder.generate_all_bgm()
        builder.generate_bgm_manifest()
    
    elif choice == "4":
        from utils.audio import AudioSynthesizer
        synth = AudioSynthesizer()
        bgm_ids = synth.get_bgm_track_ids()
        print(f"\n可用BGM: {', '.join(bgm_ids[:10])}...")
        print(f"(共 {len(bgm_ids)} 个)\n")
        track_id = input("请输入BGM ID: ").strip()
        builder.generate_specific_bgm(track_id)
    
    elif choice == "5" or choice == "manifest":
        builder.generate_sfx_manifest()
        builder.generate_bgm_manifest()
    
    elif choice == "0":
        print("再见!")
        return
    
    else:
        print("无效选项")
        return
    
    print("\n操作完成!")


if __name__ == "__main__":
    main()
