"""
音频系统模块 - 音频合成器和音效管理器
"""
import pygame
import random
import math
import os
import json
import threading
import queue
import wave
import struct
import tempfile
import time

from utils.core import log_error, log_info

class AudioSynthesizer:
    _EXTENDED_BGM_PRESETS: dict[str, dict] = {
        "dnb": {"bpm": 174, "roots": [55.0, 49.0, 65.41, 73.42], "mix": 0.52},
        "downtempo": {"bpm": 92, "roots": [110.0, 98.0, 123.47, 92.50], "mix": 0.50},
        "deep_house": {"bpm": 124, "roots": [55.0, 65.41, 73.42, 61.74], "mix": 0.52},
        "acid": {"bpm": 132, "roots": [55.0, 55.0, 65.41, 49.0], "mix": 0.54},
        "glitch": {"bpm": 150, "roots": [65.41, 73.42, 82.41, 73.42], "mix": 0.50},
        "drone": {"bpm": 60, "roots": [110.0, 123.47, 98.0, 110.0], "mix": 0.45},
        "space": {"bpm": 72, "roots": [82.41, 92.50, 73.42, 98.0], "mix": 0.46},
        "menu_alt": {"bpm": 84, "roots": [110.0, 130.81, 98.0, 123.47], "mix": 0.50},
        "boss_phase2": {"bpm": 176, "roots": [55.0, 65.41, 49.0, 73.42], "mix": 0.56},
        "victory_fanfare": {"bpm": 136, "roots": [110.0, 123.47, 146.83, 130.81], "mix": 0.54},

        # breadth pack presets (scene-themed ids)
        "menu_chill": {"bpm": 86, "roots": [110.0, 98.0, 123.47, 92.50], "mix": 0.46},
        "menu_dark": {"bpm": 78, "roots": [98.0, 92.50, 82.41, 73.42], "mix": 0.48},
        "menu_arcade": {"bpm": 128, "roots": [55.0, 65.41, 73.42, 61.74], "mix": 0.52},
        "menu_lounge": {"bpm": 104, "roots": [130.81, 146.83, 164.81, 146.83], "mix": 0.48},

        "explore_ruins": {"bpm": 96, "roots": [82.41, 92.50, 73.42, 98.0], "mix": 0.46},
        "explore_desert": {"bpm": 102, "roots": [73.42, 82.41, 98.0, 92.50], "mix": 0.48},
        "explore_snow": {"bpm": 88, "roots": [110.0, 123.47, 98.0, 110.0], "mix": 0.44},
        "explore_void": {"bpm": 70, "roots": [82.41, 73.42, 65.41, 73.42], "mix": 0.44},
        "explore_lostlab": {"bpm": 112, "roots": [65.41, 73.42, 82.41, 73.42], "mix": 0.50},
        "explore_ocean": {"bpm": 76, "roots": [92.50, 98.0, 82.41, 110.0], "mix": 0.45},
        "explore_sky": {"bpm": 120, "roots": [110.0, 123.47, 146.83, 130.81], "mix": 0.48},

        "combat_assault": {"bpm": 140, "roots": [55.0, 65.41, 73.42, 61.74], "mix": 0.56},
        "combat_swarm": {"bpm": 156, "roots": [65.41, 73.42, 82.41, 73.42], "mix": 0.56},
        "combat_mecha": {"bpm": 150, "roots": [49.0, 55.0, 65.41, 55.0], "mix": 0.58},
        "combat_siege": {"bpm": 132, "roots": [55.0, 49.0, 65.41, 55.0], "mix": 0.58},
        "combat_pursuit": {"bpm": 172, "roots": [55.0, 65.41, 49.0, 73.42], "mix": 0.58},
        "combat_arena": {"bpm": 148, "roots": [82.41, 92.50, 98.0, 110.0], "mix": 0.56},
        "combat_gauntlet": {"bpm": 178, "roots": [82.41, 73.42, 82.41, 92.50], "mix": 0.60},
        "combat_hazard": {"bpm": 145, "roots": [65.41, 73.42, 82.41, 73.42], "mix": 0.56},

        "boss_phase1": {"bpm": 160, "roots": [98.0, 92.50, 82.41, 73.42], "mix": 0.58},
        "boss_final": {"bpm": 182, "roots": [55.0, 65.41, 49.0, 73.42], "mix": 0.62},
        "boss_void": {"bpm": 150, "roots": [73.42, 65.41, 82.41, 73.42], "mix": 0.58},
        "boss_slow": {"bpm": 120, "roots": [98.0, 92.50, 82.41, 73.42], "mix": 0.56},

        "victory_loop": {"bpm": 124, "roots": [110.0, 123.47, 146.83, 130.81], "mix": 0.52},

        # legacy styles migrated to extended generator
        "orchestra": {"bpm": 100, "roots": [110.0, 123.47, 146.83, 130.81], "mix": 0.50},
        "cinematic": {"bpm": 80, "roots": [110.0, 98.0, 123.47, 92.50], "mix": 0.48},
        "orchestral_dark": {"bpm": 96, "roots": [98.0, 92.50, 82.41, 73.42], "mix": 0.50},
        "jazz": {"bpm": 110, "roots": [130.81, 146.83, 164.81, 146.83], "mix": 0.48},
        "piano": {"bpm": 90, "roots": [110.0, 123.47, 98.0, 130.81], "mix": 0.46},
        "lofi": {"bpm": 85, "roots": [110.0, 98.0, 92.50, 123.47], "mix": 0.44},
        "funk": {"bpm": 115, "roots": [82.41, 98.0, 92.50, 110.0], "mix": 0.50},
        "rock": {"bpm": 160, "roots": [82.41, 73.42, 98.0, 92.50], "mix": 0.56},
        "metal": {"bpm": 180, "roots": [82.41, 73.42, 82.41, 92.50], "mix": 0.58},
        "ambient": {"bpm": 60, "roots": [110.0, 123.47, 146.83, 130.81], "mix": 0.42},
        "electronic": {"bpm": 130, "roots": [55.0, 65.41, 73.42, 61.74], "mix": 0.52},
        "synthwave": {"bpm": 120, "roots": [110.0, 123.47, 146.83, 130.81], "mix": 0.52},
        "trance": {"bpm": 138, "roots": [82.41, 92.50, 98.0, 110.0], "mix": 0.54},
        "breakbeat": {"bpm": 150, "roots": [65.41, 73.42, 82.41, 73.42], "mix": 0.54},
        "tribal": {"bpm": 120, "roots": [82.41, 82.41, 98.0, 82.41], "mix": 0.54},
        "dubstep": {"bpm": 140, "roots": [55.0, 55.0, 65.41, 49.0], "mix": 0.56},
        "industrial": {"bpm": 130, "roots": [55.0, 49.0, 65.41, 55.0], "mix": 0.56},
        "chiptune": {"bpm": 150, "roots": [220.0, 196.0, 246.94, 293.66], "mix": 0.50},
    }

    def __init__(self):
        self.sample_rate = 44100
        # bump cache version when synthesis logic changes to ensure new audio is regenerated
        self.cache_dir = os.path.join(tempfile.gettempdir(), "neon_space_audio_v16")
        if not os.path.exists(self.cache_dir):
            try: os.makedirs(self.cache_dir)
            except: self.cache_dir = None

        self._cache_index_path = os.path.join(self.cache_dir, "cache_index.json") if self.cache_dir else None

    def _cache_path(self, filename: str) -> str | None:
        if not self.cache_dir:
            return None
        return os.path.join(self.cache_dir, filename)

    def _read_cache_index(self) -> dict:
        if not self._cache_index_path:
            return {}
        try:
            if os.path.exists(self._cache_index_path):
                with open(self._cache_index_path, "r", encoding="utf-8") as f:
                    return json.load(f) or {}
        except Exception:
            return {}
        return {}

    def _write_cache_index(self, payload: dict) -> None:
        if not self._cache_index_path:
            return
        try:
            with open(self._cache_index_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception:
            return

    def _update_cache_index_track(self, track_key: str, filename: str) -> None:
        if not self._cache_index_path:
            return
        idx = self._read_cache_index()
        idx.setdefault("version", os.path.basename(self.cache_dir) if self.cache_dir else "")
        idx.setdefault("tracks", {})
        idx["tracks"][track_key] = {
            "file": filename,
            "generated_at": time.time(),
        }
        self._write_cache_index(idx)

    def get_bgm_track_ids(self) -> list[str]:
        """Return all supported bgm track ids (without 'bgm_' prefix)."""
        base = [
            "normal",
            "boss",
            "calm",
            "mystery",
            "epic",
            "intense",
            "cyber",
            "ethereal",
            "orchestra",
            "jazz",
            "piano",
            "rock",
            "ambient",
            "electronic",
            "chiptune",
            "tribal",
            "dubstep",
            "synthwave",
            "metal",
            "trance",
            "orchestral_dark",
            "funk",
            "breakbeat",
            "lofi",
            "industrial",
            "cinematic",
            "dnb",
            "downtempo",
            "deep_house",
            "acid",
            "glitch",
            "drone",
            "space",
            "menu_alt",
            "boss_phase2",
            "victory_fanfare",
        ]

        # breadth pack: ids are chosen to work with tag inference rules in music_catalog.py
        breadth = [
            "menu_chill",
            "menu_dark",
            "menu_arcade",
            "menu_lounge",
            "explore_ruins",
            "explore_desert",
            "explore_snow",
            "explore_void",
            "explore_lostlab",
            "explore_ocean",
            "explore_sky",
            "combat_assault",
            "combat_swarm",
            "combat_mecha",
            "combat_siege",
            "combat_pursuit",
            "combat_arena",
            "combat_gauntlet",
            "combat_hazard",
            "boss_phase1",
            "boss_final",
            "boss_void",
            "boss_slow",
            "victory_loop",
        ]

        return base + breadth

    def get_track_bpm(self, track_id: str) -> int:
        """Return the intended BPM for a bgm track id (with or without 'bgm_' prefix)."""
        clean_id = track_id[4:] if track_id.startswith("bgm_") else track_id
        base_map = {
            "normal": 120,
            "boss": 170,
            "calm": 90,
            "mystery": 100,
            "epic": 150,
            "intense": 140,
            "cyber": 128,
            "ethereal": 80,
        }
        if clean_id in base_map:
            return base_map[clean_id]
        preset = self._EXTENDED_BGM_PRESETS.get(clean_id)
        if preset and isinstance(preset, dict) and "bpm" in preset:
            try:
                return int(preset["bpm"])
            except Exception:
                return 120
        return 120

    def build_manifest(self) -> dict:
        """Return a full key->path map without generating heavy bgm audio upfront."""
        if not self.cache_dir:
            return {}
        paths: dict[str, str | None] = {}

        # BGM: always expose in manifest so music library can list them.
        for track_id in self.get_bgm_track_ids():
            key = f"bgm_{track_id}"
            filename = f"bgm_{track_id}.wav"
            paths[key] = self._cache_path(filename)

        # layers
        for layer_name in (
            "layer_pad",
            "layer_pulse",
            "layer_percussion",
            # state-specific stems (scheme C)
            "layer_menu_pad",
            "layer_menu_pulse",
            "layer_explore_pad",
            "layer_explore_pulse",
            "layer_combat_pulse",
            "layer_combat_percussion",
            "layer_boss_pulse",
            "layer_boss_percussion",
        ):
            paths[layer_name] = self._cache_path(f"{layer_name}.wav")

        # stingers (scheme E)
        for st in (
            "stinger_victory",
            "stinger_defeat",
            "stinger_boss_phase",
        ):
            paths[st] = self._cache_path(f"{st}.wav")

        return paths

    def ensure_bgm_generated(self, track_id: str) -> str | None:
        """Generate a bgm wav if missing and return its path."""
        if not self.cache_dir:
            return None
        clean_id = track_id[4:] if track_id.startswith("bgm_") else track_id
        key = f"bgm_{clean_id}"
        filename = f"bgm_{clean_id}.wav"
        path = self._cache_path(filename)
        if not path:
            return None
        if os.path.exists(path):
            return path

        try:
            if clean_id == "normal":
                data = self._generate_bgm_normal()
            elif clean_id == "boss":
                data = self._generate_bgm_boss()
            elif clean_id == "calm":
                data = self._generate_bgm_calm()
            elif clean_id == "mystery":
                data = self._generate_bgm_mystery()
            elif clean_id == "epic":
                data = self._generate_bgm_epic()
            elif clean_id == "intense":
                data = self._generate_bgm_intense()
            elif clean_id == "cyber":
                data = self._generate_bgm_cyber()
            elif clean_id == "ethereal":
                data = self._generate_bgm_ethereal()
            else:
                data = self._generate_extended_bgm(clean_id)

            saved = self.save_wave(filename, data)
            if saved:
                self._update_cache_index_track(key, filename)
            return saved
        except Exception:
            return None

    def save_wave(self, filename, data):
        if not self.cache_dir: return None
        path = os.path.join(self.cache_dir, filename)
        if os.path.exists(path): return path
        try:
            with wave.open(path, 'w') as f:
                f.setparams((1, 2, self.sample_rate, len(data), 'NONE', 'not compressed'))
                packed_data = struct.pack('h' * len(data), *[int(max(-1, min(1, s)) * 32767) for s in data])
                f.writeframes(packed_data)
            return path
        except: return None
    
    def apply_lowpass_filter(self, data, cutoff_ratio=0.3):
        """应用简单的低通滤波器,减少高频刺耳"""
        if not data:
            return data
        filtered = [data[0]]
        alpha = cutoff_ratio
        for i in range(1, len(data)):
            filtered.append(alpha * data[i] + (1 - alpha) * filtered[-1])
        return filtered
    
    def apply_compressor(self, data, threshold=0.7, ratio=0.5):
        """应用压缩器,防止音量过大"""
        compressed = []
        for sample in data:
            if abs(sample) > threshold:
                sign = 1 if sample > 0 else -1
                excess = abs(sample) - threshold
                sample = sign * (threshold + excess * ratio)
            compressed.append(sample)
        return compressed
    
    def normalize_audio(self, data, target_level=0.8):
        """归一化音频,确保音量适中"""
        if not data:
            return data
        max_val = max(abs(s) for s in data)
        if max_val > 0:
            scale = target_level / max_val
            return [s * scale for s in data]
        return data

    def generate_tone(self, freq, duration, vol=0.5, wave_type="sine", envelope="smooth"):
        """生成音调,支持多种波形和包络"""
        n_samples = int(self.sample_rate * duration)
        data = []
        for i in range(n_samples):
            t = i / self.sample_rate
            v = 0
            # 波形生成
            if wave_type == "sine": 
                v = math.sin(2 * math.pi * freq * t)
            elif wave_type == "square": 
                v = (math.sin(2 * math.pi * freq * t) * 0.7 +
                     math.sin(6 * math.pi * freq * t) * 0.15 +
                     math.sin(10 * math.pi * freq * t) * 0.08)
            elif wave_type == "saw": 
                v = 2 * (t * freq - math.floor(t * freq + 0.5))
                v = max(-0.8, min(0.8, v))
            elif wave_type == "triangle":
                phase = (t * freq) % 1.0
                v = 4 * abs(phase - 0.5) - 1
            elif wave_type == "noise": 
                v = random.uniform(-0.7, 0.7)
            elif wave_type == "organ":
                v = (math.sin(2 * math.pi * freq * t) * 0.5 +
                     math.sin(4 * math.pi * freq * t) * 0.25 +
                     math.sin(6 * math.pi * freq * t) * 0.125)
            elif wave_type == "pluck":
                decay_factor = math.exp(-t * 5)
                v = math.sin(2 * math.pi * freq * t) * decay_factor
            elif wave_type == "bell":
                v = (math.sin(2 * math.pi * freq * t) * 0.5 +
                     math.sin(4 * math.pi * freq * t) * 0.3 * math.exp(-t * 2) +
                     math.sin(6 * math.pi * freq * t) * 0.2 * math.exp(-t * 4))
            
            # 包络处理
            if envelope == "smooth":
                if i < 100: v *= (i/100)
                if i > n_samples - 500: v *= ((n_samples - i)/500)
            elif envelope == "sharp":
                if i < 10: v *= (i/10)
                if i > n_samples - 50: v *= ((n_samples - i)/50)
            elif envelope == "long":
                if i < 500: v *= (i/500)
                if i > n_samples - 2000: v *= ((n_samples - i)/2000)
            elif envelope == "pluck":
                v *= math.exp(-t * 4)
                
            data.append(v * vol)
        return data
    
    def generate_drum(self, drum_type, vol=0.5):
        """生成鼓点音效"""
        if drum_type == "kick":
            data = []
            dur = 0.3
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate
                freq = 120 * math.exp(-t * 12)
                v = math.sin(2 * math.pi * freq * t) * math.exp(-t * 7)
                data.append(v * vol * 0.7)
            return data
        elif drum_type == "snare":
            data = []
            dur = 0.15
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate
                tone = math.sin(2 * math.pi * 180 * t) * 0.25
                noise = random.uniform(-0.6, 0.6) * 0.5
                v = (tone + noise) * math.exp(-t * 10)
                data.append(v * vol * 0.7)
            return data
        elif drum_type == "hihat":
            data = []
            dur = 0.08
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate
                v = random.uniform(-0.6, 0.6) * math.exp(-t * 25)
                data.append(v * vol * 0.25)
            return data
        elif drum_type == "tom":
            data = []
            dur = 0.2
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate
                freq = 100 * math.exp(-t * 7)
                v = math.sin(2 * math.pi * freq * t) * math.exp(-t * 5)
                data.append(v * vol * 0.6)
            return data
        return []
    
    def add_reverb(self, data, decay=0.3, delay_samples=4410):
        """添加混响效果"""
        reverb_data = data[:]
        for i in range(delay_samples, len(data)):
            reverb_data[i] += data[i - delay_samples] * decay
        return reverb_data
    
    def mix_tracks(self, *tracks):
        """混合多个音轨"""
        if not tracks:
            return []
        max_len = max(len(t) for t in tracks)
        mixed = [0] * max_len
        for track in tracks:
            for i, sample in enumerate(track):
                mixed[i] += sample
        mixed = self.apply_compressor(mixed, threshold=0.6, ratio=0.4)
        mixed = self.normalize_audio(mixed, target_level=0.7)
        return mixed

    def generate_all(self):
        """生成音效/图层，并返回包含所有 BGM 的清单（BGM 按需生成）。"""
        if not self.cache_dir: return {}
        paths = self.build_manifest()
        try:
            # 1. Shoot
            data = []
            for i in range(int(self.sample_rate * 0.15)):
                t = i / self.sample_rate; freq = 800 * math.exp(-t * 15); v = math.sin(2 * math.pi * freq * t) * 0.3 * (1 - t/0.15); data.append(v)
            paths["shoot"] = self.save_wave("shoot.wav", data)
            
            # 2. Explosion
            data = []; dur = 0.4
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; v = random.uniform(-1, 1) * 0.6 * math.exp(-t * 8); data.append(v)
            paths["explosion"] = self.save_wave("explosion.wav", data)
            
            # 3. Hit
            data = []; dur = 0.2
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; v = random.uniform(-1, 1) * 0.5 * (1 - t/dur); data.append(v)
            paths["hit"] = self.save_wave("hit.wav", data)
            
            # 4. LevelUp
            data = []; notes = [440, 554, 659, 880]
            for freq in notes: data.extend(self.generate_tone(freq, 0.1, 0.4, "square"))
            paths["levelup"] = self.save_wave("levelup.wav", data)

            # 5. Warning
            data = []; dur = 1.0
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; freq = 400 + 200 * math.sin(2 * math.pi * 8 * t); v = (2 * (t * freq - math.floor(t * freq + 0.5))) * 0.5; data.append(v)
            paths["warning"] = self.save_wave("warning.wav", data)

            # 6. Laser
            data = []; dur = 1.5
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; freq = 1000 + 50 * math.sin(2 * math.pi * 50 * t); v = math.sin(2 * math.pi * freq * t) * 0.4 * (1 - t/dur); data.append(v)
            paths["laser"] = self.save_wave("laser.wav", data)

            # 7. Dash
            data = []; dur = 0.3
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; v = random.uniform(-1, 1) * math.sin(2*math.pi*50*t) * 0.5 * (1-t/dur); data.append(v)
            paths["dash"] = self.save_wave("dash.wav", data)

            # 8. Graze
            paths["graze"] = self.save_wave("graze.wav", self.generate_tone(1500, 0.1, 0.3, "sine"))
            # 9. Select
            paths["select"] = self.save_wave("select.wav", self.generate_tone(880, 0.05, 0.3, "square"))
            
            # 10. Zap
            data = []; dur = 0.3
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; freq = random.randint(200, 1000); v = math.sin(2 * math.pi * freq * t) * 0.3 * (1-t/dur); data.append(v)
            paths["zap"] = self.save_wave("zap.wav", data)

            # 11. Sniper Charge
            data = []; dur = 0.8
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; freq = 200 * math.exp(t * 3); v = math.sin(2 * math.pi * freq * t) * 0.3; data.append(v)
            paths["sniper_charge"] = self.save_wave("sniper_charge.wav", data)

            # 12. Freeze
            data = []; dur = 1.0
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; freq = 1000 * math.exp(-t * 3); v = math.sin(2 * math.pi * freq * t) * 0.4; data.append(v)
            paths["freeze"] = self.save_wave("freeze.wav", data)

            # 13. Nuke
            data = []; dur = 2.5
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; v1 = random.uniform(-1, 1) * 0.5; v2 = math.sin(2 * math.pi * 30 * t) * 0.5; v = (v1 + v2) * 0.8 * (1 - t/dur); data.append(v)
            paths["nuke"] = self.save_wave("nuke.wav", data)

            # 14. Gameover
            data = []; notes = [440, 349, 261]
            for freq in notes: data.extend(self.generate_tone(freq, 0.4, 0.5, "sine"))
            paths["gameover"] = self.save_wave("gameover.wav", data)

            # 15. Blackhole
            data = []; dur = 1.0
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; v = math.sin(2 * math.pi * 40 * t + 5 * math.sin(2*math.pi*5*t)) * 0.6; data.append(v)
            paths["blackhole"] = self.save_wave("blackhole.wav", data)

            # 16. Achievement
            data = []; notes = [523, 659, 784, 1047]
            for freq in notes: data.extend(self.generate_tone(freq, 0.15, 0.5, "square"))
            paths["achievement"] = self.save_wave("achievement.wav", data)
            
            # 17. Item Pickup
            data = []; dur = 0.25
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; freq = 600 + 400 * t; v = math.sin(2 * math.pi * freq * t) * 0.4 * (1 - t/dur); data.append(v)
            paths["item_pickup"] = self.save_wave("item_pickup.wav", data)
            
            # 18. Critical Hit
            data = []; dur = 0.2
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; v = (2 * (t * 800 - math.floor(t * 800 + 0.5))) * 0.6 * (1 - t/dur); data.append(v)
            paths["critical"] = self.save_wave("critical.wav", data)
            
            # 19. Heal
            data = []; notes = [440, 550, 660]
            for freq in notes: data.extend(self.generate_tone(freq, 0.1, 0.35, "sine"))
            paths["heal"] = self.save_wave("heal.wav", data)
            
            # 20. Shield
            data = []; dur = 0.4
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; freq = 800 + 200 * math.sin(2 * math.pi * 5 * t); v = math.sin(2 * math.pi * freq * t) * 0.35 * (1 - t/dur); data.append(v)
            paths["shield"] = self.save_wave("shield.wav", data)

            # ===== scheme E: stingers (short musical accents) =====
            paths["stinger_victory"] = self.save_wave("stinger_victory.wav", self._generate_stinger_victory())
            paths["stinger_defeat"] = self.save_wave("stinger_defeat.wav", self._generate_stinger_defeat())
            paths["stinger_boss_phase"] = self.save_wave(
                "stinger_boss_phase.wav", self._generate_stinger_boss_phase()
            )

            # 自适应音乐图层（为 MusicDirector 提供动态叠加素材）
            layer_pad = self._generate_layer_pad()
            paths["layer_pad"] = self.save_wave("layer_pad.wav", layer_pad)

            layer_pulse = self._generate_layer_pulse()
            paths["layer_pulse"] = self.save_wave("layer_pulse.wav", layer_pulse)

            layer_percussion = self._generate_layer_percussion()
            paths["layer_percussion"] = self.save_wave("layer_percussion.wav", layer_percussion)

            # scheme C: state-specific stems (small set, ok to eager-generate)
            paths["layer_menu_pad"] = self.save_wave("layer_menu_pad.wav", self._generate_layer_pad_variant("menu"))
            paths["layer_menu_pulse"] = self.save_wave("layer_menu_pulse.wav", self._generate_layer_pulse_variant("menu"))
            paths["layer_explore_pad"] = self.save_wave("layer_explore_pad.wav", self._generate_layer_pad_variant("explore"))
            paths["layer_explore_pulse"] = self.save_wave("layer_explore_pulse.wav", self._generate_layer_pulse_variant("explore"))
            paths["layer_combat_pulse"] = self.save_wave("layer_combat_pulse.wav", self._generate_layer_pulse_variant("combat"))
            paths["layer_combat_percussion"] = self.save_wave(
                "layer_combat_percussion.wav", self._generate_layer_percussion_variant("combat")
            )
            paths["layer_boss_pulse"] = self.save_wave("layer_boss_pulse.wav", self._generate_layer_pulse_variant("boss"))
            paths["layer_boss_percussion"] = self.save_wave(
                "layer_boss_percussion.wav", self._generate_layer_percussion_variant("boss")
            )

            # write a lightweight manifest index
            idx = {
                "version": os.path.basename(self.cache_dir) if self.cache_dir else "",
                "manifest_written_at": time.time(),
                "bgm_track_ids": self.get_bgm_track_ids(),
            }
            self._write_cache_index(idx)

        except Exception as e:
            log_error(f"音频生成错误: {e}")
        return paths

    def _generate_stinger_victory(self):
        data = []
        # bright arpeggio + tiny hit
        notes = [523.25, 659.25, 783.99, 1046.5]
        for f in notes:
            data.extend(self.generate_tone(f, 0.09, 0.55, "square"))
        data.extend(self.generate_tone(1567.98, 0.12, 0.35, "sine"))
        # add a short kick-like thump
        data.extend(self.generate_drum("kick", vol=0.55))
        data = self.add_reverb(data, decay=0.22, delay_samples=int(self.sample_rate * 0.06))
        data = self.apply_lowpass_filter(data, 0.42)
        data = self.normalize_audio(data, 0.7)
        return data

    def _generate_stinger_defeat(self):
        data = []
        # falling minor-like tone + low boom
        notes = [293.66, 246.94, 220.0, 196.0]
        for f in notes:
            data.extend(self.generate_tone(f, 0.12, 0.5, "sine"))
        boom = []
        dur = 0.45
        rng = random.Random(77)
        for i in range(int(self.sample_rate * dur)):
            t = i / self.sample_rate
            low = math.sin(2 * math.pi * (70 * math.exp(-t * 2.6)) * t) * math.exp(-t * 5.0)
            noise = rng.uniform(-0.6, 0.6) * math.exp(-t * 10.0)
            boom.append((low * 0.9 + noise * 0.25) * 0.55)
        data.extend(boom)
        data = self.add_reverb(data, decay=0.18, delay_samples=int(self.sample_rate * 0.08))
        data = self.apply_lowpass_filter(data, 0.35)
        data = self.normalize_audio(data, 0.65)
        return data

    def _generate_stinger_boss_phase(self):
        data = []
        # rising sweep + impact
        dur = 0.65
        rng = random.Random(131)
        for i in range(int(self.sample_rate * dur)):
            t = i / self.sample_rate
            sweep = 240 + 820 * (t / dur)
            tone = math.sin(2 * math.pi * sweep * t) * (0.45 + 0.25 * math.sin(t * 35))
            grit = (2 * (t * (sweep * 0.5) - math.floor(t * (sweep * 0.5) + 0.5))) * 0.18
            noise = rng.uniform(-0.5, 0.5) * math.exp(-t * 10.0) * 0.25
            env = 1.0 if t < 0.22 else math.exp(-(t - 0.22) * 5.5)
            data.append((tone * 0.55 + grit + noise) * env)
        hit = self.generate_drum("kick", vol=0.8)
        hit = self.apply_compressor(hit, threshold=0.55, ratio=0.35)
        data = self.mix_tracks(data, hit)
        data = self.add_reverb(data, decay=0.25, delay_samples=int(self.sample_rate * 0.05))
        data = self.apply_lowpass_filter(data, 0.48)
        data = self.normalize_audio(data, 0.75)
        return data
    
    def _generate_bgm_normal(self):
        """生成普通BGM"""
        bgm_data = []
        bpm = 120; beat_dur = 60 / bpm; total_beats = 16
        for beat in range(total_beats):
            samples_per_beat = int(self.sample_rate * beat_dur)
            freq = 82.41 if beat < 12 else 73.42
            for i in range(samples_per_beat):
                t_local = i / self.sample_rate
                val_bass = (1.0 if math.sin(2 * math.pi * freq * t_local) > 0 else -1.0) * 0.3 * math.exp(-t_local * 5)
                val_drum = 0
                if beat % 4 == 0: val_drum += math.sin(2 * math.pi * 60 * math.exp(-t_local*20) * t_local) * 0.6 * math.exp(-t_local*10)
                if beat % 4 == 2: val_drum += random.uniform(-0.5, 0.5) * 0.4 * math.exp(-t_local*15)
                if beat % 2 == 1: val_drum += random.uniform(-0.3, 0.3) * 0.2 * math.exp(-t_local*30)
                val_arp = 0
                if beat % 2 == 0:
                    arp_note = freq * 4
                    val_arp = math.sin(2 * math.pi * arp_note * t_local) * 0.08 * math.exp(-t_local*8)
                bgm_data.append((val_bass + val_drum + val_arp) * 0.4)
        bgm_data = self.apply_lowpass_filter(bgm_data, 0.4)
        bgm_data = self.normalize_audio(bgm_data, 0.55)
        return bgm_data
    
    def _generate_bgm_boss(self):
        """生成Boss战BGM"""
        boss_bgm_data = []
        bpm = 170; beat_dur = 60 / bpm; total_beats = 32
        for beat in range(total_beats):
            samples_per_beat = int(self.sample_rate * beat_dur)
            freq = 55.0 if (beat // 4) % 2 == 0 else 65.41
            for i in range(samples_per_beat):
                t_local = i / self.sample_rate
                val_bass = (2 * (t_local * freq - math.floor(t_local * freq + 0.5))) * 0.5 * math.exp(-t_local * 4)
                val_drum = 0
                if beat % 2 == 0: val_drum += math.sin(2 * math.pi * 90 * math.exp(-t_local*25) * t_local) * 0.9 * math.exp(-t_local*10)
                if beat % 4 == 2: val_drum += random.uniform(-0.9, 0.9) * 0.6 * math.exp(-t_local*20)
                val_lead = 0
                if beat % 8 == 0: val_lead = math.sin(2 * math.pi * (900 - t_local*300) * t_local) * 0.25 * math.exp(-t_local*2)
                mix = (val_bass + val_drum + val_lead) * 0.5
                mix = max(-0.7, min(0.7, mix))
                boss_bgm_data.append(mix)
        boss_bgm_data = self.apply_compressor(boss_bgm_data, threshold=0.6, ratio=0.4)
        boss_bgm_data = self.normalize_audio(boss_bgm_data, 0.58)
        return boss_bgm_data
    
    def _generate_bgm_calm(self):
        """生成宁静BGM"""
        calm_bgm = []
        bpm = 90; beat_dur = 60 / bpm; total_beats = 16
        melody = [329.63, 349.23, 392.00, 440.00, 392.00, 349.23, 329.63, 293.66]
        for beat in range(total_beats):
            samples_per_beat = int(self.sample_rate * beat_dur)
            melody_freq = melody[beat % len(melody)]
            for i in range(samples_per_beat):
                t_local = i / self.sample_rate
                val_melody = math.sin(2 * math.pi * melody_freq * t_local) * 0.25 * math.exp(-t_local * 2)
                val_harmony = math.sin(2 * math.pi * (melody_freq * 0.75) * t_local) * 0.15 * math.exp(-t_local * 3)
                val_perc = 0
                if beat % 4 == 0 and i < 1000:
                    val_perc = random.uniform(-0.2, 0.2) * math.exp(-t_local * 10)
                calm_bgm.append((val_melody + val_harmony + val_perc) * 0.45)
        calm_bgm = self.apply_lowpass_filter(calm_bgm, 0.35)
        calm_bgm = self.normalize_audio(calm_bgm, 0.5)
        return calm_bgm
    
    def _generate_bgm_mystery(self):
        """生成神秘BGM"""
        mystery_bgm = []
        bpm = 100; beat_dur = 60 / bpm; total_beats = 20
        for beat in range(total_beats):
            samples_per_beat = int(self.sample_rate * beat_dur)
            for i in range(samples_per_beat):
                t_local = i / self.sample_rate
                bass_freq = 65 + 10 * math.sin(beat * 0.5)
                val_bass = math.sin(2 * math.pi * bass_freq * t_local) * 0.3 * math.exp(-t_local * 3)
                val_high = math.sin(2 * math.pi * (1200 + 200 * math.sin(t_local * 3)) * t_local) * 0.1 * (1 - t_local)
                val_echo = 0
                if beat % 5 == 0:
                    val_echo = math.sin(2 * math.pi * 880 * t_local) * 0.15 * math.exp(-t_local * 5)
                mystery_bgm.append((val_bass + val_high + val_echo) * 0.4)
        mystery_bgm = self.apply_lowpass_filter(mystery_bgm, 0.35)
        mystery_bgm = self.normalize_audio(mystery_bgm, 0.52)
        return mystery_bgm
    
    def _generate_bgm_epic(self):
        """生成史诗BGM"""
        epic_bgm = []
        bpm = 150; beat_dur = 60 / bpm; total_beats = 32
        power_chords = [82.41, 87.31, 98.00, 110.00]
        for beat in range(total_beats):
            samples_per_beat = int(self.sample_rate * beat_dur)
            chord_freq = power_chords[(beat // 4) % len(power_chords)]
            for i in range(samples_per_beat):
                t_local = i / self.sample_rate
                val_bass = (2 * (t_local * chord_freq - math.floor(t_local * chord_freq + 0.5))) * 0.5 * math.exp(-t_local * 3)
                val_drum = 0
                if beat % 2 == 0:
                    val_drum = math.sin(2 * math.pi * 80 * math.exp(-t_local*30) * t_local) * 0.8 * math.exp(-t_local*12)
                val_lead = math.sin(2 * math.pi * (chord_freq * 6 + 100 * math.sin(beat * 0.7)) * t_local) * 0.2 * math.exp(-t_local * 4)
                epic_bgm.append((val_bass + val_drum + val_lead) * 0.55)
        epic_bgm = self.apply_compressor(epic_bgm, threshold=0.6, ratio=0.4)
        epic_bgm = self.normalize_audio(epic_bgm, 0.58)
        return epic_bgm
    
    def _generate_bgm_intense(self):
        """生成紧张BGM"""
        intense_bgm = []
        bpm = 140; beat_dur = 60 / bpm; total_beats = 24
        for beat in range(total_beats):
            samples_per_beat = int(self.sample_rate * beat_dur)
            for i in range(samples_per_beat):
                t_local = i / self.sample_rate
                freq = 110 + 20 * (beat % 4)
                val_saw = (2 * (t_local * freq - math.floor(t_local * freq + 0.5))) * 0.4
                val_perc = random.uniform(-0.7, 0.7) * math.exp(-t_local * 15) if beat % 1 == 0 else 0
                val_stab = 0
                if beat % 2 == 0:
                    val_stab = math.sin(2 * math.pi * 1760 * t_local) * 0.3 * math.exp(-t_local * 8)
                intense_bgm.append((val_saw + val_perc + val_stab) * 0.5)
        intense_bgm = self.apply_compressor(intense_bgm, threshold=0.6, ratio=0.4)
        intense_bgm = self.normalize_audio(intense_bgm, 0.56)
        return intense_bgm
    
    def _generate_bgm_cyber(self):
        """生成赛博BGM"""
        cyber_bgm = []
        bpm = 128; beat_dur = 60 / bpm; total_beats = 16
        for beat in range(total_beats):
            samples_per_beat = int(self.sample_rate * beat_dur)
            for i in range(samples_per_beat):
                t_local = i / self.sample_rate
                bass_freq = 65 if beat % 8 < 4 else 73
                val_bass = (1.0 if math.sin(2 * math.pi * bass_freq * t_local) > 0 else -1.0) * 0.35 * math.exp(-t_local * 4)
                val_kick = 0
                if beat % 4 == 0:
                    val_kick = math.sin(2 * math.pi * 50 * math.exp(-t_local*25) * t_local) * 0.7 * math.exp(-t_local*10)
                arp_notes = [523, 659, 784, 1047]
                arp_freq = arp_notes[(beat * 4 + int(t_local * 8)) % len(arp_notes)]
                val_arp = math.sin(2 * math.pi * arp_freq * t_local) * 0.15 * math.exp(-t_local * 6)
                cyber_bgm.append((val_bass + val_kick + val_arp) * 0.48)
        cyber_bgm = self.apply_lowpass_filter(cyber_bgm, 0.4)
        cyber_bgm = self.normalize_audio(cyber_bgm, 0.55)
        return cyber_bgm
    
    def _generate_bgm_ethereal(self):
        """生成空灵BGM"""
        ethereal_bgm = []
        bpm = 80; beat_dur = 60 / bpm; total_beats = 12
        for beat in range(total_beats):
            samples_per_beat = int(self.sample_rate * beat_dur)
            for i in range(samples_per_beat):
                t_local = i / self.sample_rate
                pad_freq = 220 + 55 * math.sin(beat * 0.3)
                val_pad = math.sin(2 * math.pi * pad_freq * t_local) * 0.2
                val_pad += math.sin(2 * math.pi * pad_freq * 1.5 * t_local) * 0.15
                shimmer_freq = 1760 + 440 * math.sin(t_local * 2 + beat * 0.5)
                val_shimmer = math.sin(2 * math.pi * shimmer_freq * t_local) * 0.1 * math.exp(-t_local * 1)
                ethereal_bgm.append((val_pad + val_shimmer) * 0.4)
        ethereal_bgm = self.apply_lowpass_filter(ethereal_bgm, 0.3)
        ethereal_bgm = self.normalize_audio(ethereal_bgm, 0.5)
        return ethereal_bgm
    
    def _seeded_rng(self, key):
        # 让同一风格每次启动生成结果一致，便于调参和音乐馆试听
        seed = 0
        for ch in str(key):
            seed = (seed * 131 + ord(ch)) & 0xFFFFFFFF
        return random.Random(seed)

    def _generate_extended_bgm(self, style):
        """生成更“有编曲感”的BGM（鼓/贝斯/铺底/主旋律），用于扩展曲库。"""
        rng = self._seeded_rng(style)

        preset = self._EXTENDED_BGM_PRESETS.get(style, {"bpm": 120, "roots": [110.0, 123.47, 98.0, 130.81], "mix": 0.5})
        bpm = preset["bpm"]
        roots = preset["roots"]
        mix_gain = preset["mix"]
        beat_dur = 60 / max(1, bpm)
        sr = self.sample_rate
        data = []

        ambient_like = {"drone", "space", "ambient", "menu_alt", "lofi", "piano", "cinematic", "orchestra", "orchestral_dark"}
        club_like = {"deep_house", "electronic", "trance", "synthwave"}
        break_like = {"dnb", "breakbeat"}
        rock_like = {"rock", "metal"}
        jazz_like = {"jazz", "funk"}
        industrial_like = {"industrial", "glitch"}
        tribal_like = {"tribal"}
        dubstep_like = {"dubstep"}
        chip_like = {"chiptune"}

        # keep generation time reasonable; derive beats from a target duration
        target_seconds = 14.0 if style in ambient_like else 12.0
        total_beats = int(max(1.0, target_seconds) / max(0.05, beat_dur))
        total_beats = max(16, min(32, total_beats))

        for beat in range(total_beats):
            samples_per_beat = int(sr * beat_dur)
            root = roots[(beat // 4) % len(roots)]

            # 小节结构：每 16 拍变一次“段落”，提高听感变化
            section = (beat // 16) % 3
            intensity = 0.65 if section == 0 else (0.85 if section == 1 else 0.75)

            for i in range(samples_per_beat):
                t = i / sr
                # Sub + Bass
                sub = math.sin(2 * math.pi * (root * 0.5) * t) * 0.22
                saw = 2 * ((t * root) - math.floor(t * root + 0.5))
                bass = saw * (0.24 if style in rock_like or style in industrial_like else 0.20)
                if style in dubstep_like:
                    wobble = 0.55 + 0.45 * math.sin(2 * math.pi * 3.0 * (t + beat * beat_dur))
                    bass *= wobble
                bass *= math.exp(-t * (2.2 if style in ("dnb", "boss_phase2") else 1.7))

                # Pad（慢起慢落，略带泛音）
                pad_base = math.sin(2 * math.pi * (root * 2) * t) * 0.08
                pad_fifth = math.sin(2 * math.pi * (root * 3) * t) * 0.05
                pad_weight = 0.9 if style in ("drone", "space") else (0.85 if style in ambient_like else 0.7)
                pad = (pad_base + pad_fifth) * pad_weight
                pad *= (0.6 + 0.4 * math.sin(2 * math.pi * 0.12 * (t + beat)))

                # orchestral chord support
                chord = 0.0
                if style in ("orchestra", "cinematic", "orchestral_dark"):
                    third_ratio = 1.25 if style != "orchestral_dark" else 1.2
                    fifth_ratio = 1.5
                    chord = (
                        math.sin(2 * math.pi * (root * 2.0) * t) * 0.06
                        + math.sin(2 * math.pi * (root * 2.0 * third_ratio) * t) * 0.05
                        + math.sin(2 * math.pi * (root * 2.0 * fifth_ratio) * t) * 0.04
                    )
                    chord *= (0.85 if style == "orchestral_dark" else 1.0)

                # Lead/Arp（节拍触发，快速衰减）
                lead = 0.0
                if style in ("dnb", "deep_house", "acid", "boss_phase2", "victory_fanfare", "trance", "synthwave", "electronic", "breakbeat"):
                    if beat % 2 == 0:
                        ratio = [1.0, 1.25, 1.5, 2.0][(beat // 2) % 4]
                        lead_freq = root * 4 * ratio
                        wave = math.sin(2 * math.pi * lead_freq * t)
                        lead = wave * 0.14 * math.exp(-t * 7.5)
                elif style in rock_like:
                    if beat % 2 == 0:
                        lead_freq = root * 4
                        grit = 2 * ((t * lead_freq) - math.floor(t * lead_freq + 0.5))
                        lead = grit * 0.11 * math.exp(-t * 6.5)
                elif style in jazz_like or style in ("piano", "lofi"):
                    if beat % 4 == 0:
                        lead_freq = root * 2
                        wave = math.sin(2 * math.pi * lead_freq * t)
                        lead = wave * 0.10 * math.exp(-t * 5.0)
                elif style in chip_like:
                    if beat % 2 == 0:
                        ratio = [1.0, 1.5, 2.0, 2.5][(beat // 2) % 4]
                        lead_freq = root * ratio
                        sq = (1.0 if math.sin(2 * math.pi * lead_freq * t) > 0 else -1.0)
                        lead = sq * 0.10 * math.exp(-t * 10.0)
                elif style in ("orchestra", "cinematic", "orchestral_dark"):
                    if beat % 4 == 0:
                        lead_freq = root * 4
                        vib = 1.0 + 0.004 * math.sin(2 * math.pi * 5.5 * t)
                        wave = math.sin(2 * math.pi * (lead_freq * vib) * t)
                        lead = wave * 0.09 * math.exp(-t * 3.5)
                elif style == "glitch":
                    if rng.random() < 0.015:
                        lead = rng.uniform(-0.35, 0.35) * math.exp(-t * 25)

                # Drums
                kick = 0.0
                snare = 0.0
                hat = 0.0
                if style in ("dnb", "boss_phase2"):
                    if beat % 4 == 0 and i < sr * 0.07:
                        kick = math.sin(2 * math.pi * (90 * math.exp(-t * 35)) * t) * 0.95
                    if beat % 4 == 2 and i < sr * 0.12:
                        snare = rng.uniform(-0.8, 0.8) * math.exp(-t * 28)
                    hat = rng.uniform(-0.25, 0.25) * math.exp(-t * 55)
                elif style in ("deep_house", "acid"):
                    if beat % 4 == 0 and i < sr * 0.08:
                        kick = math.sin(2 * math.pi * (75 * math.exp(-t * 28)) * t) * 0.85
                    if beat % 4 == 2 and i < sr * 0.10:
                        snare = rng.uniform(-0.55, 0.55) * math.exp(-t * 32)
                    hat = rng.uniform(-0.18, 0.18) * math.exp(-t * 70)
                elif style in ("downtempo", "menu_alt"):
                    if beat % 4 == 0 and i < sr * 0.09:
                        kick = math.sin(2 * math.pi * (60 * math.exp(-t * 22)) * t) * 0.65
                    if beat % 8 == 4 and i < sr * 0.11:
                        snare = rng.uniform(-0.35, 0.35) * math.exp(-t * 22)
                    hat = rng.uniform(-0.12, 0.12) * math.exp(-t * 80)
                elif style in ("drone", "space"):
                    # 这些风格鼓点更稀疏、更“空气感”
                    if beat % 8 == 0 and i < sr * 0.10:
                        kick = math.sin(2 * math.pi * (45 * math.exp(-t * 18)) * t) * 0.40
                    hat = rng.uniform(-0.08, 0.08) * math.exp(-t * 90)
                elif style == "victory_fanfare":
                    if beat % 4 == 0 and i < sr * 0.08:
                        kick = math.sin(2 * math.pi * (85 * math.exp(-t * 26)) * t) * 0.75
                    if beat % 8 in (2, 6) and i < sr * 0.10:
                        snare = rng.uniform(-0.5, 0.5) * math.exp(-t * 26)
                    hat = rng.uniform(-0.15, 0.15) * math.exp(-t * 65)
                elif style in club_like:
                    if beat % 4 == 0 and i < sr * 0.08:
                        kick = math.sin(2 * math.pi * (75 * math.exp(-t * 28)) * t) * 0.85
                    if beat % 4 == 2 and i < sr * 0.10:
                        snare = rng.uniform(-0.50, 0.50) * math.exp(-t * 30)
                    hat = rng.uniform(-0.18, 0.18) * math.exp(-t * 70)
                elif style in break_like:
                    if beat % 4 == 0 and i < sr * 0.07:
                        kick = math.sin(2 * math.pi * (92 * math.exp(-t * 35)) * t) * 0.90
                    if beat % 4 == 2 and i < sr * 0.12:
                        snare = rng.uniform(-0.75, 0.75) * math.exp(-t * 26)
                    hat = rng.uniform(-0.22, 0.22) * math.exp(-t * 55)
                elif style in rock_like:
                    if beat % 2 == 0 and i < sr * 0.08:
                        kick = math.sin(2 * math.pi * (95 * math.exp(-t * 30)) * t) * 0.85
                    if beat % 4 == 2 and i < sr * 0.12:
                        snare = rng.uniform(-0.65, 0.65) * math.exp(-t * 24)
                    hat = rng.uniform(-0.20, 0.20) * math.exp(-t * 55)
                elif style in jazz_like:
                    if beat % 4 == 0 and i < sr * 0.09:
                        kick = math.sin(2 * math.pi * (62 * math.exp(-t * 22)) * t) * 0.55
                    if beat % 8 == 4 and i < sr * 0.11:
                        snare = rng.uniform(-0.30, 0.30) * math.exp(-t * 22)
                    # light swing-ish hat
                    if beat % 2 == 1:
                        hat = rng.uniform(-0.10, 0.10) * math.exp(-t * 85)
                elif style in tribal_like:
                    if beat % 4 == 0 and i < sr * 0.10:
                        kick = math.sin(2 * math.pi * (55 * math.exp(-t * 20)) * t) * 0.55
                    if beat % 4 == 2 and i < sr * 0.10:
                        snare = rng.uniform(-0.40, 0.40) * math.exp(-t * 24)
                    if beat % 2 == 1:
                        hat = rng.uniform(-0.10, 0.10) * math.exp(-t * 75)
                elif style in dubstep_like:
                    # half-time
                    if beat % 4 == 0 and i < sr * 0.08:
                        kick = math.sin(2 * math.pi * (85 * math.exp(-t * 26)) * t) * 0.85
                    if beat % 4 == 2 and i < sr * 0.13:
                        snare = rng.uniform(-0.75, 0.75) * math.exp(-t * 22)
                    hat = rng.uniform(-0.16, 0.16) * math.exp(-t * 65)
                elif style in industrial_like:
                    if beat % 4 == 0 and i < sr * 0.09:
                        kick = math.sin(2 * math.pi * (70 * math.exp(-t * 24)) * t) * 0.80
                    if beat % 4 == 2 and i < sr * 0.12:
                        snare = rng.uniform(-0.70, 0.70) * math.exp(-t * 20)
                    hat = rng.uniform(-0.22, 0.22) * math.exp(-t * 55)

                drums = (kick + snare + hat) * 0.22

                # extra grit for industrial styles
                grit_noise = 0.0
                if style in industrial_like:
                    grit_noise = rng.uniform(-0.12, 0.12) * math.exp(-t * 18)

                # 轻微“酸线”效果：用 saw 做一个快速滤波式的包络
                acid_line = 0.0
                if style == "acid":
                    cutoff = 0.35 + 0.25 * math.sin(2 * math.pi * (0.5 + 0.05 * beat) * t)
                    acid_wave = 2 * ((t * (root * 2.0)) - math.floor(t * (root * 2.0) + 0.5))
                    acid_line = acid_wave * 0.10 * math.exp(-t * (6 + 6 * cutoff))

                sample = (sub + bass + pad + chord + lead + drums + acid_line + grit_noise) * (mix_gain * intensity)
                sample = max(-0.8, min(0.8, sample))
                data.append(sample)

        # 统一做一点点质感处理
        if style in ("drone", "space", "menu_alt", "ambient", "lofi", "piano", "orchestra", "cinematic", "orchestral_dark"):
            data = self.add_reverb(data, decay=0.22, delay_samples=int(sr * 0.09))
            data = self.apply_lowpass_filter(data, 0.28)
        else:
            data = self.apply_lowpass_filter(data, 0.42)

        data = self.apply_compressor(data, threshold=0.62, ratio=0.45)
        data = self.normalize_audio(data, target_level=0.56)
        return data

    def _generate_layer_pad(self):
        """柔和垫底氛围层"""
        data = []
        duration = 12
        for i in range(int(self.sample_rate * duration)):
            t = i / self.sample_rate
            base = math.sin(2 * math.pi * 110 * t) * 0.2
            fifth = math.sin(2 * math.pi * 165 * t) * 0.15
            shimmer = math.sin(2 * math.pi * (440 + 30 * math.sin(t * 0.2)) * t) * 0.08
            val = (base + fifth + shimmer) * math.exp(-t * 0.05)
            data.append(val * 0.6)
        data = self.apply_lowpass_filter(data, 0.25)
        data = self.normalize_audio(data, 0.4)
        return data

    def _generate_layer_pad_variant(self, family: str):
        """A slightly different pad layer per game state (menu/explore/combat/boss)."""
        rng = self._seeded_rng(f"layer_pad_{family}")
        data = []
        duration = 12
        if family == "menu":
            base_freq = 110
            shimmer_base = 440
            decay = 0.06
            lp = 0.23
            level = 0.38
        elif family == "explore":
            base_freq = 98
            shimmer_base = 520
            decay = 0.05
            lp = 0.26
            level = 0.40
        elif family == "boss":
            base_freq = 82
            shimmer_base = 360
            decay = 0.08
            lp = 0.22
            level = 0.36
        else:  # combat
            base_freq = 92
            shimmer_base = 480
            decay = 0.07
            lp = 0.24
            level = 0.36

        for i in range(int(self.sample_rate * duration)):
            t = i / self.sample_rate
            wobble = 1.0 + 0.01 * math.sin(t * 0.35) + 0.006 * math.sin(t * 0.11)
            base = math.sin(2 * math.pi * (base_freq * wobble) * t) * 0.18
            fifth = math.sin(2 * math.pi * (base_freq * 1.5 * wobble) * t) * 0.14
            shimmer = math.sin(2 * math.pi * ((shimmer_base + 22 * math.sin(t * 0.25)) * wobble) * t) * 0.06
            air = (rng.uniform(-0.10, 0.10) * 0.06) * (0.6 + 0.4 * math.sin(t * 0.8))
            val = (base + fifth + shimmer + air) * math.exp(-t * decay)
            data.append(val * 0.65)
        data = self.add_reverb(data, decay=0.18, delay_samples=int(self.sample_rate * 0.085))
        data = self.apply_lowpass_filter(data, lp)
        data = self.normalize_audio(data, level)
        return data

    def _generate_layer_pulse(self):
        """律动脉冲层"""
        data = []
        bpm = 120
        beat_dur = 60 / bpm
        total_beats = 32
        for beat in range(total_beats):
            samples = int(self.sample_rate * beat_dur)
            for i in range(samples):
                t_local = i / self.sample_rate
                freq = 55 if beat % 4 < 2 else 73
                wave = (2 * (t_local * freq - math.floor(t_local * freq + 0.5))) * 0.35
                atk = math.exp(-t_local * 8)
                data.append(wave * atk * 0.7)
        data = self.apply_lowpass_filter(data, 0.45)
        data = self.normalize_audio(data, 0.45)
        return data

    def _generate_layer_pulse_variant(self, family: str):
        """A slightly different pulse layer per game state."""
        rng = self._seeded_rng(f"layer_pulse_{family}")
        data = []
        if family == "menu":
            bpm = 92
            base_a, base_b = 55, 73
            lp = 0.42
            level = 0.42
        elif family == "explore":
            bpm = 110
            base_a, base_b = 55, 82
            lp = 0.44
            level = 0.44
        elif family == "boss":
            bpm = 150
            base_a, base_b = 65, 92
            lp = 0.48
            level = 0.48
        else:  # combat
            bpm = 132
            base_a, base_b = 65, 82
            lp = 0.46
            level = 0.46

        beat_dur = 60 / bpm
        total_beats = 32
        for beat in range(total_beats):
            samples = int(self.sample_rate * beat_dur)
            for i in range(samples):
                t_local = i / self.sample_rate
                freq = base_a if beat % 4 < 2 else base_b
                wave = (2 * (t_local * freq - math.floor(t_local * freq + 0.5))) * 0.32
                atk = math.exp(-t_local * (7.5 if family in ("menu", "explore") else 6.5))
                # tiny swing / jitter
                jitter = 1.0 + (rng.uniform(-0.02, 0.02) if beat % 2 == 1 else 0.0)
                data.append(wave * atk * 0.7 * jitter)
        data = self.apply_lowpass_filter(data, lp)
        data = self.normalize_audio(data, level)
        return data

    def _generate_layer_percussion(self):
        """高能鼓击层"""
        data = []
        bpm = 140
        beat_dur = 60 / bpm
        total_beats = 32
        for beat in range(total_beats):
            samples = int(self.sample_rate * beat_dur)
            for i in range(samples):
                t_local = i / self.sample_rate
                kick = 0
                if beat % 2 == 0 and i < self.sample_rate * 0.08:
                    kick = math.sin(2 * math.pi * (90 * math.exp(-t_local * 35)) * t_local) * 0.8
                snare = 0
                if beat % 4 == 2 and i < self.sample_rate * 0.12:
                    snare = random.uniform(-0.6, 0.6) * math.exp(-t_local * 35)
                hat = random.uniform(-0.3, 0.3) * math.exp(-t_local * 60)
                data.append((kick + snare + hat) * 0.6)
        data = self.apply_compressor(data, threshold=0.5, ratio=0.35)
        data = self.normalize_audio(data, 0.5)
        return data

    def _generate_layer_percussion_variant(self, family: str):
        """A slightly different percussion layer per game state."""
        rng = self._seeded_rng(f"layer_perc_{family}")
        data = []
        if family == "boss":
            bpm = 168
            kick_gain = 0.95
            snare_gain = 0.75
            hat_gain = 0.35
            level = 0.55
        elif family == "combat":
            bpm = 150
            kick_gain = 0.85
            snare_gain = 0.65
            hat_gain = 0.30
            level = 0.52
        else:
            bpm = 120
            kick_gain = 0.55
            snare_gain = 0.40
            hat_gain = 0.22
            level = 0.45

        beat_dur = 60 / bpm
        total_beats = 32
        for beat in range(total_beats):
            samples = int(self.sample_rate * beat_dur)
            for i in range(samples):
                t_local = i / self.sample_rate
                kick = 0.0
                if beat % 4 == 0 and i < self.sample_rate * 0.08:
                    kick = math.sin(2 * math.pi * (90 * math.exp(-t_local * 35)) * t_local) * kick_gain
                snare = 0.0
                if beat % 4 == 2 and i < self.sample_rate * 0.12:
                    snare = rng.uniform(-0.75, 0.75) * math.exp(-t_local * 28) * snare_gain
                hat = rng.uniform(-0.3, 0.3) * math.exp(-t_local * 60) * hat_gain
                data.append((kick + snare + hat) * 0.6)
        data = self.apply_compressor(data, threshold=0.5, ratio=0.35)
        data = self.normalize_audio(data, level)
        return data


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.current_bgm = None
        self.master_volume = 1.0
        self.sfx_volume = 0.8
        self.music_volume = 0.5
        self.sound_channels = {}
        self._bgm_sound_cache = {}
        self._volume_listeners = []
        self._bgm_prewarm_thread = None
        self._bgm_prewarm_stop = False
        self._bgm_prewarm_queue = queue.Queue()
        self._bgm_prewarm_inflight = set()
        
        self.enabled = False
        try:
            if pygame.mixer.get_init():
                self.enabled = True
            else:
                pygame.mixer.init()
                self.enabled = True
            try:
                if pygame.mixer.get_num_channels() < 32:
                    pygame.mixer.set_num_channels(32)
            except: pass
        except:
            self.enabled = False

        if self.enabled:
            try:
                self.synth = AudioSynthesizer()
                self.file_paths = self.synth.generate_all()
                self.load_sounds()
                self._start_bgm_prewarm()
            except Exception as e:
                log_error(f"SoundManager init error: {e}")
                self.enabled = False

    def _start_bgm_prewarm(self):
        """Start a background worker that pre-generates BGMs to avoid first-play stalls."""
        if not self.enabled:
            return
        if not hasattr(self, "synth") or not self.synth:
            return
        if self._bgm_prewarm_thread and self._bgm_prewarm_thread.is_alive():
            return

        # keep this list small: it should cover most first-play cases (menu + early explore)
        prewarm_ids = [
            "cinematic",
            "menu_alt",
            "calm",
            "piano",
            "lofi",
            "menu_chill",
            "menu_dark",
            "menu_arcade",
            "normal",
            "mystery",
            "ambient",
            "space",
        ]

        self._bgm_prewarm_stop = False

        def _worker():
            while not self._bgm_prewarm_stop:
                try:
                    track_id = self._bgm_prewarm_queue.get(timeout=0.2)
                except Exception:
                    continue
                try:
                    if track_id is None:
                        break
                    self.synth.ensure_bgm_generated(track_id)
                except Exception:
                    pass
                finally:
                    try:
                        self._bgm_prewarm_inflight.discard(track_id)
                    except Exception:
                        pass
                    try:
                        self._bgm_prewarm_queue.task_done()
                    except Exception:
                        pass
                # tiny delay to avoid hogging CPU during gameplay/menu rendering
                time.sleep(0.01)

        self._bgm_prewarm_thread = threading.Thread(target=_worker, name="bgm_prewarm", daemon=True)
        self._bgm_prewarm_thread.start()

        # enqueue initial warm list
        for tid in prewarm_ids:
            self.queue_bgm_prewarm(tid)

    def queue_bgm_prewarm(self, track_id: str) -> None:
        """Queue a BGM for background generation (non-blocking)."""
        if not self.enabled:
            return
        if not hasattr(self, "synth") or not self.synth:
            return
        clean_id = track_id[4:] if isinstance(track_id, str) and track_id.startswith("bgm_") else track_id
        if not clean_id:
            return
        key = f"bgm_{clean_id}"
        path = None
        try:
            path = self.file_paths.get(key) if hasattr(self, "file_paths") else None
        except Exception:
            path = None
        try:
            if path and os.path.exists(path):
                return
        except Exception:
            pass

        if clean_id in self._bgm_prewarm_inflight:
            return
        self._bgm_prewarm_inflight.add(clean_id)
        try:
            self._bgm_prewarm_queue.put_nowait(clean_id)
        except Exception:
            # best-effort; avoid blocking UI
            self._bgm_prewarm_inflight.discard(clean_id)

    def stop_bgm_prewarm(self):
        self._bgm_prewarm_stop = True
        try:
            self._bgm_prewarm_queue.put_nowait(None)
        except Exception:
            pass

    def load_sounds(self):
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
            # scheme E stingers
            "stinger_victory": 0.85,
            "stinger_defeat": 0.8,
            "stinger_boss_phase": 0.85,
        }
        for name, path in self.file_paths.items():
            if path and not name.startswith("bgm") and not name.startswith("layer_"):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    vol = volume_map.get(name, 0.5)
                    self.sounds[name].set_volume(vol * self.sfx_volume)
                except: pass

    def play(self, name, volume=None):
        """播放音效"""
        if not self.enabled or name not in self.sounds:
            return
        try:
            sound = self.sounds[name]
            if volume is not None:
                sound.set_volume(volume * self.master_volume)
            channel = sound.play()
            self.sound_channels[name] = channel
        except: pass

    def register_volume_listener(self, callback):
        if callback not in self._volume_listeners:
            self._volume_listeners.append(callback)

    def _notify_volume_change(self):
        mix = self.master_volume * self.music_volume
        for callback in list(self._volume_listeners):
            try:
                callback(mix)
            except Exception as exc:
                log_error(f"音量监听器错误: {exc}")

    def play_music(self, track="normal", fade_ms=0, force=False):
        if not self.enabled:
            return
        key = f"bgm_{track}"
        if key not in self.file_paths or not self.file_paths[key]:
            return
        if self.current_bgm == track and not force:
            return
        try:
            # ensure on-demand bgm exists before loading
            if hasattr(self, "synth") and self.synth:
                self.synth.ensure_bgm_generated(track)
            pygame.mixer.music.load(self.file_paths[key])
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
            pygame.mixer.music.play(-1, fade_ms=fade_ms)
            self.current_bgm = track
        except Exception as exc:
            log_error(f"播放音乐失败: {exc}")

    def get_music_pos_ms(self) -> int:
        """Return current music playback position in ms (pygame returns -1 if unknown)."""
        if not self.enabled:
            return -1
        try:
            return int(pygame.mixer.music.get_pos())
        except Exception:
            return -1

    def get_track_bpm(self, track: str) -> int:
        """Return BPM for a bgm track id (without 'bgm_' prefix)."""
        try:
            if hasattr(self, "synth") and self.synth:
                return int(self.synth.get_track_bpm(track))
        except Exception:
            return -1
        return -1

    def stop_music(self):
        if self.enabled:
            try: pygame.mixer.music.stop()
            except: pass
        self.current_bgm = None

    def fadeout_music(self, fade_ms=800):
        if self.enabled:
            try:
                pygame.mixer.music.fadeout(fade_ms)
            except: pass
        self.current_bgm = None

    def get_bgm_clip(self, track):
        if not self.enabled:
            return None
        if track in self._bgm_sound_cache:
            return self._bgm_sound_cache[track]
        key = f"bgm_{track}" if track.startswith("bgm_") else f"bgm_{track}"
        alt_key = track if track.startswith("layer_") else f"layer_{track}" if track in {"pad", "pulse", "percussion"} else None
        # ensure on-demand bgm exists before loading
        if hasattr(self, "synth") and self.synth:
            if key.startswith("bgm_"):
                self.synth.ensure_bgm_generated(key)

        path = self.file_paths.get(key)
        if not path and alt_key:
            path = self.file_paths.get(alt_key)
        if not path:
            path = self.file_paths.get(track)
        if not path:
            return None
        try:
            sound = pygame.mixer.Sound(path)
            self._bgm_sound_cache[track] = sound
            sound.set_volume(self.music_volume * self.master_volume * 0.4)
            return sound
        except Exception as exc:
            log_error(f"加载BGM音轨失败: {exc}")
            return None
    
    def set_master_volume(self, volume):
        """设置主音量"""
        self.master_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        self._notify_volume_change()
    
    def set_sfx_volume(self, volume):
        """设置音效音量"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume):
        """设置音乐音量"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        self._notify_volume_change()


class MusicDirector:
    """自适应音乐调度器，负责管理乐曲状态、图层与提示音"""

    def __init__(self, sound_manager):
        self.sound_mgr = sound_manager
        self.state_catalog = self._build_catalog()
        self.state_stack = []
        self.current_state = None
        self.current_track = None
        self.current_intensity = 0.3
        self.fade_ms = 1400
        self.layer_channels = {}
        self.active_layers = {}
        self.layer_settings = {}
        self._silenced_until = 0.0
        self._resume_request = None
        self._layers_dirty = False
        self._selection_nonce = 0
        # scheme D: beat-aligned, debounced switching
        self._pending_music: dict | None = None
        self._last_switch_at = 0.0
        self._min_track_hold_s = 10.0
        self._beats_per_bar = 4
        if self.sound_mgr and self.sound_mgr.enabled:
            self.sound_mgr.register_volume_listener(self._on_volume_change)

    def _state_bpm(self, state: str) -> int:
        # A simple, stable bpm per state (used for bar-quantized switching).
        return {
            "menu": 96,
            "explore": 110,
            "combat": 132,
            "boss": 160,
            "boss_challenge": 168,
            "victory": 120,
            "defeat": 90,
        }.get(state, 120)

    def _calc_next_bar_delay_ms(self, state: str) -> int:
        if not self.sound_mgr:
            return 0
        pos_ms = self.sound_mgr.get_music_pos_ms()
        if pos_ms < 0:
            return 0

        bpm = -1
        if self.current_track:
            try:
                bpm = int(self.sound_mgr.get_track_bpm(self.current_track))
            except Exception:
                bpm = -1
        if bpm <= 0:
            bpm = int(self._state_bpm(state))
        bpm = max(40, min(220, int(bpm)))
        beat_ms = 60000.0 / bpm
        bar_ms = max(200.0, beat_ms * max(1, int(self._beats_per_bar)))
        rem = pos_ms % int(bar_ms)
        delay = int(bar_ms) - rem
        # If we're extremely close to a boundary, push to next bar
        if delay < 90:
            delay += int(bar_ms)
        # Don't wait too long; keep responsiveness
        return max(0, min(2500, delay))

    def _clear_pending_music(self):
        self._pending_music = None

    def _request_track(self, track: str | None, immediate: bool, force: bool):
        if not track:
            return

        if track == self.current_track and not force:
            self._clear_pending_music()
            return

        if immediate or force or not self.current_track:
            self._clear_pending_music()
            self._play_track(track, immediate=immediate, force=True)
            self._last_switch_at = time.perf_counter()
            return

        now = time.perf_counter()
        # avoid rapid switching due to high-frequency intensity updates
        if (now - self._last_switch_at) < self._min_track_hold_s:
            return

        if self._pending_music and self._pending_music.get("target") == track:
            return

        delay_ms = self._calc_next_bar_delay_ms(self.current_state or "")
        self._pending_music = {
            "phase": "wait_bar",
            "target": track,
            "execute_at": now + delay_ms / 1000.0,
            "fadein_ms": self.fade_ms,
        }

    def _build_catalog(self):
        # Catalog defines layer behavior + fallback only. Track selection is
        # handled dynamically from the available bgm_* pool.
        return {
            "menu": {
                "fallback": "cinematic",
                "layers": {
                    "pad": {"track": "layer_menu_pad", "volume": 0.18},
                    "pulse": {"track": "layer_menu_pulse", "min_intensity": 0.6, "volume": 0.08}
                }
            },
            "explore": {
                "fallback": "normal",
                "layers": {
                    "pad": {"track": "layer_explore_pad", "volume": 0.2},
                    "pulse": {"track": "layer_explore_pulse", "min_intensity": 0.5, "volume": 0.1}
                }
            },
            "combat": {
                "fallback": "intense",
                "layers": {
                    "pulse": {"track": "layer_combat_pulse", "volume": 0.16},
                    "percussion": {"track": "layer_combat_percussion", "min_intensity": 0.6, "volume": 0.22}
                }
            },
            "boss": {
                "fallback": "boss",
                "layers": {
                    "pulse": {"track": "layer_boss_pulse", "volume": 0.14},
                    "percussion": {"track": "layer_boss_percussion", "volume": 0.25}
                }
            },
            "boss_challenge": {
                "fallback": "orchestral_dark",
                "layers": {
                    "pulse": {"track": "layer_boss_pulse", "volume": 0.12},
                    "percussion": {"track": "layer_boss_percussion", "min_intensity": 0.7, "volume": 0.18}
                }
            },
            "victory": {
                "fallback": "epic",
                "layers": {
                    "pad": {"track": "layer_pad", "volume": 0.22}
                }
            },
            "defeat": {
                "fallback": "ambient",
                "layers": {
                    "pad": {"track": "layer_pad", "volume": 0.15}
                }
            }
        }

    def set_state(self, state, intensity=0.5, immediate=False, force=False, override_track=None, layers_enabled=True):
        if not self.sound_mgr or not self.sound_mgr.enabled:
            return
        if state != self.current_state:
            self._selection_nonce += 1
        self.current_state = state
        self.current_intensity = intensity
        descriptor = self.state_catalog.get(state)
        if override_track:
            track = override_track
        else:
            track = self._select_track_from_pool(state, descriptor, intensity)
        layer_specs = descriptor.get("layers", {}) if descriptor and layers_enabled else {}
        if self._silenced_until and time.perf_counter() < self._silenced_until:
            self._resume_request = (state, intensity, immediate, force, override_track, layers_enabled)
            return
        self._request_track(track, immediate=immediate, force=force)
        if layers_enabled:
            self._apply_layers(layer_specs, intensity)
        else:
            self._disable_unused_layers({})

    def push_state(self, state, intensity=0.8, immediate=False, **kwargs):
        self.state_stack.append((self.current_state, self.current_intensity))
        self.set_state(state, intensity=intensity, immediate=immediate, force=True, **kwargs)

    def pop_state(self, **kwargs):
        if not self.state_stack:
            return False
        prev_state, prev_intensity = self.state_stack.pop()
        if prev_state is None:
            prev_state = "menu"
            prev_intensity = 0.3
        self.set_state(prev_state, intensity=prev_intensity, force=True, **kwargs)
        return True

    def pause_for_stinger(self, stinger=None, resume_state=None, resume_intensity=None, silence_ms=1800):
        if not self.sound_mgr or not self.sound_mgr.enabled:
            return
        self._clear_pending_music()
        self.sound_mgr.fadeout_music(min(1200, silence_ms))
        if stinger:
            self.sound_mgr.play(stinger)
        resume_state = resume_state or self.current_state or "menu"
        resume_intensity = resume_intensity if resume_intensity is not None else self.current_intensity
        self._silenced_until = time.perf_counter() + silence_ms / 1000.0
        self._resume_request = (resume_state, resume_intensity, True, True, None, True)

    def register_state(self, name, descriptor):
        self.state_catalog[name] = descriptor

    def update(self):
        # scheme D: execute scheduled, bar-quantized track transitions
        if self._pending_music:
            now = time.perf_counter()
            phase = self._pending_music.get("phase")
            if now >= float(self._pending_music.get("execute_at", 0.0)):
                if phase == "wait_bar":
                    out_ms = max(120, min(260, int(self.fade_ms * 0.15)))
                    try:
                        self.sound_mgr.fadeout_music(out_ms)
                    except Exception:
                        pass
                    self._pending_music["phase"] = "play"
                    self._pending_music["execute_at"] = now + out_ms / 1000.0
                elif phase == "play":
                    target = self._pending_music.get("target")
                    fadein = int(self._pending_music.get("fadein_ms") or self.fade_ms)
                    self._pending_music = None
                    if target:
                        self.sound_mgr.play_music(target, fade_ms=fadein, force=True)
                        self.current_track = target
                        self._last_switch_at = time.perf_counter()

        if self._layers_dirty:
            self._refresh_layer_volumes()
            self._layers_dirty = False
        if self._silenced_until and time.perf_counter() >= self._silenced_until:
            if self._resume_request:
                state, intensity, immediate, force, override_track, layers_enabled = self._resume_request
                self._resume_request = None
                self._silenced_until = 0.0
                self.set_state(state, intensity=intensity, immediate=immediate, force=force,
                               override_track=override_track, layers_enabled=layers_enabled)
            else:
                self._silenced_until = 0.0

    def refresh_layers(self):
        self._refresh_layer_volumes()

    def _play_track(self, track, immediate=False, force=False):
        if not track:
            return
        fade = 0 if immediate else self.fade_ms
        self.sound_mgr.play_music(track, fade_ms=fade, force=force)
        self.current_track = track

    def _stable_hash(self, text: str) -> int:
        h = 2166136261
        for ch in text:
            h ^= ord(ch)
            h = (h * 16777619) & 0xFFFFFFFF
        return h

    def _available_bgm_ids(self) -> set[str]:
        ids: set[str] = set()
        try:
            for k in getattr(self.sound_mgr, "file_paths", {}) or {}:
                if k.startswith("bgm_"):
                    ids.add(k[4:])
        except Exception:
            return set()
        return ids

    def _pick_candidate(self, state: str, bucket: str, candidates: list[str], fallback: str | None) -> str | None:
        if not candidates:
            return fallback
        # keep current track if it still fits the bucket to avoid unnecessary switching
        if state == self.current_state and self.current_track in candidates:
            return self.current_track
        salt = f"{state}|{bucket}|{self._selection_nonce}"
        idx = self._stable_hash(salt) % len(candidates)
        pick = candidates[idx]
        if pick == self.current_track and len(candidates) > 1:
            pick = candidates[(idx + 1) % len(candidates)]
        return pick

    def _select_track_from_pool(self, state: str, descriptor: dict | None, intensity: float) -> str | None:
        available = self._available_bgm_ids()
        fallback = (descriptor or {}).get("fallback") if descriptor else None
        if not available:
            return fallback or state

        i = max(0.0, min(1.0, float(intensity)))

        def _by_prefix(prefix: str) -> list[str]:
            return sorted([t for t in available if t.startswith(prefix)])

        def _by_ids(items: list[str]) -> list[str]:
            return [t for t in items if t in available]

        if state == "menu":
            low = _by_ids(["calm", "piano", "lofi", "menu_chill", "menu_lounge", "menu_alt"]) + _by_prefix("menu_")
            mid = _by_ids(["cinematic", "orchestra", "downtempo", "menu_arcade", "menu_dark"]) + _by_prefix("menu_")
            high = _by_ids(["ethereal", "space"]) + _by_prefix("menu_")
            bucket = "low" if i < 0.45 else ("mid" if i < 0.8 else "high")
            candidates = low if bucket == "low" else (mid if bucket == "mid" else high)
            return self._pick_candidate(state, bucket, [c for c in candidates if c in available], fallback or "cinematic")

        if state == "explore":
            low = _by_ids(["normal", "calm", "ambient", "space", "drone", "explore_snow", "explore_ocean"]) + _by_prefix("explore_")
            mid = _by_ids(["mystery", "ethereal", "explore_ruins", "explore_lostlab", "explore_desert"]) + _by_prefix("explore_")
            high = _by_ids(["epic", "deep_house", "explore_void", "cyber"]) + _by_prefix("explore_")
            bucket = "low" if i < 0.42 else ("mid" if i < 0.78 else "high")
            candidates = low if bucket == "low" else (mid if bucket == "mid" else high)
            return self._pick_candidate(state, bucket, [c for c in candidates if c in available], fallback or "normal")

        if state == "combat":
            low = _by_ids(["electronic", "trance", "breakbeat", "deep_house", "combat_assault", "combat_arena", "combat_hazard"]) + _by_prefix("combat_")
            mid = _by_ids(["intense", "dnb", "glitch", "metal", "combat_swarm", "combat_mecha", "combat_siege"]) + _by_prefix("combat_")
            high = _by_ids(["boss_phase1", "boss_slow", "combat_gauntlet", "combat_pursuit", "boss_phase2"]) + _by_prefix("combat_")
            bucket = "low" if i < 0.55 else ("mid" if i < 0.82 else "high")
            candidates = low if bucket == "low" else (mid if bucket == "mid" else high)
            return self._pick_candidate(state, bucket, [c for c in candidates if c in available], fallback or "intense")

        if state in ("boss", "boss_challenge"):
            p1 = _by_ids(["boss_phase1", "boss_slow", "orchestral_dark", "boss_void", "boss"]) + _by_prefix("boss_")
            p2 = _by_ids(["boss", "boss_phase2", "industrial", "metal"]) + _by_prefix("boss_")
            p3 = _by_ids(["boss_final", "boss_phase2", "metal", "dnb"]) + _by_prefix("boss_")
            bucket = "p1" if i < 0.55 else ("p2" if i < 0.82 else "p3")
            candidates = p1 if bucket == "p1" else (p2 if bucket == "p2" else p3)
            return self._pick_candidate(state, bucket, [c for c in candidates if c in available], fallback or "boss")

        if state == "victory":
            candidates = _by_ids(["victory_fanfare", "victory_loop", "epic", "orchestra"]) + _by_prefix("victory_")
            return self._pick_candidate(state, "v", [c for c in candidates if c in available], fallback or "victory_fanfare")

        if state == "defeat":
            candidates = _by_ids(["drone", "ambient", "menu_dark", "explore_void"]) + _by_prefix("explore_")
            return self._pick_candidate(state, "d", [c for c in candidates if c in available], fallback or "ambient")

        if state in available:
            return state
        return fallback or "normal"

    def _apply_layers(self, layer_specs, intensity):
        desired = {}
        for name, spec in layer_specs.items():
            min_i = spec.get("min_intensity", 0.0)
            max_i = spec.get("max_intensity", 1.0)
            if intensity < min_i or intensity > max_i:
                continue
            track = spec.get("track")
            if not track:
                continue
            clip = self.sound_mgr.get_bgm_clip(track)
            if not clip:
                continue
            current_track = self.active_layers.get(name)
            channel = self._get_layer_channel(name)
            if not channel:
                continue
            base_volume = spec.get("volume", 0.2)
            if current_track == track and channel.get_busy():
                channel.set_volume(base_volume * self._current_mix())
            else:
                channel.play(clip, loops=-1, fade_ms=spec.get("fade_ms", 400))
                channel.set_volume(base_volume * self._current_mix())
            desired[name] = track
            self.layer_settings[name] = {"volume": base_volume}
        self._disable_unused_layers(desired)
        self.active_layers = desired

    def _disable_unused_layers(self, desired):
        for name, track in list(self.active_layers.items()):
            if name in desired:
                continue
            channel = self.layer_channels.get(name)
            if channel:
                try:
                    channel.fadeout(400)
                except: pass
            self.layer_settings.pop(name, None)
        for name in list(self.active_layers.keys()):
            if name not in desired:
                self.active_layers.pop(name, None)

    def _get_layer_channel(self, name):
        channel = self.layer_channels.get(name)
        if channel:
            return channel
        channel = pygame.mixer.find_channel()
        if not channel:
            try:
                pygame.mixer.set_num_channels(pygame.mixer.get_num_channels() + 4)
                channel = pygame.mixer.find_channel()
            except: return None
        self.layer_channels[name] = channel
        return channel

    def _current_mix(self):
        if not self.sound_mgr:
            return 0.0
        return self.sound_mgr.master_volume * self.sound_mgr.music_volume

    def _refresh_layer_volumes(self):
        mix = self._current_mix()
        for name, spec in self.layer_settings.items():
            channel = self.layer_channels.get(name)
            if channel:
                channel.set_volume(spec.get("volume", 0.2) * mix)

    def _on_volume_change(self, _):
        self._layers_dirty = True
