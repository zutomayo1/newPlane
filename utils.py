import pygame
import random
import math
import sys
import os
import wave
import struct
import tempfile
import traceback
import logging
import json
from config import *

# ==============================================================================
#   日志工具
# ==============================================================================
logger = logging.getLogger("neon_space")
logger.setLevel(logging.DEBUG)
try:
    file_handler = logging.FileHandler("debug.log", encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except Exception:
    pass

def log_error(msg):
    try:
        logger.error(str(msg))
    except Exception:
        # Fallback: best effort write
        try:
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write("ERROR: " + str(msg) + "\n")
        except:
            pass

def log_info(msg):
    try:
        logger.info(str(msg))
    except Exception:
        try:
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write("INFO: " + str(msg) + "\n")
        except:
            pass

def log_debug(msg):
    try:
        logger.debug(str(msg))
    except Exception:
        try:
            with open("debug.log", "a", encoding="utf-8") as f:
                f.write("DEBUG: " + str(msg) + "\n")
        except:
            pass

# ==============================================================================
#   游戏设置保存/加载
# ==============================================================================
SETTINGS_FILE = "game_settings.json"

def save_settings(background_style=None, master_volume=None, music_volume=None, sfx_volume=None, show_fps=None, screen_shake=None, particle_quality=None, show_damage_numbers=None):
    """保存游戏设置"""
    # 加载现有设置
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
        else:
            settings = {}
    except:
        settings = {}
    
    # 更新提供的设置
    if background_style is not None:
        settings["background_style"] = background_style
    if master_volume is not None:
        settings["master_volume"] = master_volume
    if music_volume is not None:
        settings["music_volume"] = music_volume
    if sfx_volume is not None:
        settings["sfx_volume"] = sfx_volume
    if show_fps is not None:
        settings["show_fps"] = show_fps
    if screen_shake is not None:
        settings["screen_shake"] = screen_shake
    if particle_quality is not None:
        settings["particle_quality"] = particle_quality
    if show_damage_numbers is not None:
        settings["show_damage_numbers"] = show_damage_numbers
    
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        log_info(f"设置已保存: {settings}")
    except Exception as e:
        log_error(f"保存设置失败: {e}")

def load_settings():
    """加载游戏设置"""
    default_settings = {
        "background_style": "classic",
        "master_volume": 1.0,
        "music_volume": 0.5,
        "sfx_volume": 0.8,
        "show_fps": True,
        "screen_shake": True,
        "particle_quality": "high",
        "show_damage_numbers": True
    }
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                log_info(f"设置已加载: {settings}")
                # 合并默认设置，确保所有键都存在
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
    except Exception as e:
        log_error(f"加载设置失败: {e}")
    return default_settings

def safe_blit(target_surf, src_surf, dest):
    """Safely blit a surface if both source and target are non-None.
    If either is None, log a warning and skip to avoid TypeError crashes.
    """
    if target_surf is None:
        log_debug("safe_blit: target_surf is None, skipping blit")
        return
    if src_surf is None:
        log_debug("safe_blit: src_surf is None, skipping blit")
        return
    try:
        target_surf.blit(src_surf, dest)
    except Exception as e:
        log_error(f"safe_blit failed: {e}")

# ==============================================================================
#   音频合成系统
# ==============================================================================
class AudioSynthesizer:
    def __init__(self):
        self.sample_rate = 44100
        self.cache_dir = os.path.join(tempfile.gettempdir(), "neon_space_audio_v15")
        if not os.path.exists(self.cache_dir):
            try: os.makedirs(self.cache_dir)
            except: self.cache_dir = None

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
                # 柔化方波 - 使用多个正弦波合成
                v = (math.sin(2 * math.pi * freq * t) * 0.7 +
                     math.sin(6 * math.pi * freq * t) * 0.15 +
                     math.sin(10 * math.pi * freq * t) * 0.08)
            elif wave_type == "saw": 
                # 柔化锯齿波 - 限制高频
                v = 2 * (t * freq - math.floor(t * freq + 0.5))
                v = max(-0.8, min(0.8, v))  # 软削波
            elif wave_type == "triangle":
                phase = (t * freq) % 1.0
                v = 4 * abs(phase - 0.5) - 1
            elif wave_type == "noise": 
                # 柔化噪音 - 降低峰值
                v = random.uniform(-0.7, 0.7)
            elif wave_type == "organ":  # 风琴音色 - 多个正弦波叠加
                v = (math.sin(2 * math.pi * freq * t) * 0.5 +
                     math.sin(4 * math.pi * freq * t) * 0.25 +
                     math.sin(6 * math.pi * freq * t) * 0.125)
            elif wave_type == "pluck":  # 拨弦音色
                decay_factor = math.exp(-t * 5)
                v = math.sin(2 * math.pi * freq * t) * decay_factor
            elif wave_type == "bell":  # 钟声音色
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
        """生成鼓点音效(优化版,更柔和)"""
        if drum_type == "kick":
            data = []
            dur = 0.3
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate
                freq = 120 * math.exp(-t * 12)  # 降低频率和衰减速度
                v = math.sin(2 * math.pi * freq * t) * math.exp(-t * 7)
                data.append(v * vol * 0.7)  # 降低音量
            return data
        elif drum_type == "snare":
            data = []
            dur = 0.15
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate
                tone = math.sin(2 * math.pi * 180 * t) * 0.25
                noise = random.uniform(-0.6, 0.6) * 0.5  # 降低噪音
                v = (tone + noise) * math.exp(-t * 10)
                data.append(v * vol * 0.7)
            return data
        elif drum_type == "hihat":
            data = []
            dur = 0.08
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate
                v = random.uniform(-0.6, 0.6) * math.exp(-t * 25)  # 降低强度
                data.append(v * vol * 0.25)
            return data
        elif drum_type == "tom":
            data = []
            dur = 0.2
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate
                freq = 100 * math.exp(-t * 7)  # 降低频率
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
        """混合多个音轨,应用压缩和归一化"""
        if not tracks:
            return []
        max_len = max(len(t) for t in tracks)
        mixed = [0] * max_len
        for track in tracks:
            for i, sample in enumerate(track):
                mixed[i] += sample
        # 应用压缩器防止削波
        mixed = self.apply_compressor(mixed, threshold=0.6, ratio=0.4)
        # 归一化到安全音量
        mixed = self.normalize_audio(mixed, target_level=0.7)
        return mixed

    def generate_all(self):
        if not self.cache_dir: return {}
        paths = {}
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
            
            # 10. Zap (Electric)
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

            # 16. BGM Normal
            bgm_data = []
            bpm = 120; beat_dur = 60 / bpm; total_beats = 16
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur); freq = 82.41 if beat < 12 else 73.42
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate; val_bass = (1.0 if math.sin(2 * math.pi * freq * t_local) > 0 else -1.0) * 0.3 * math.exp(-t_local * 5)
                    val_drum = 0
                    if beat % 4 == 0: val_drum += math.sin(2 * math.pi * 60 * math.exp(-t_local*20) * t_local) * 0.6 * math.exp(-t_local*10)
                    if beat % 4 == 2: val_drum += random.uniform(-0.5, 0.5) * 0.4 * math.exp(-t_local*15)
                    if beat % 2 == 1: val_drum += random.uniform(-0.3, 0.3) * 0.2 * math.exp(-t_local*30)
                    val_arp = 0
                    if beat % 2 == 0: arp_note = freq * 4; val_arp = math.sin(2 * math.pi * arp_note * t_local) * 0.08 * math.exp(-t_local*8)
                    bgm_data.append((val_bass + val_drum + val_arp) * 0.4)
            # 应用低通滚波和归一化
            bgm_data = self.apply_lowpass_filter(bgm_data, 0.4)
            bgm_data = self.normalize_audio(bgm_data, 0.55)
            paths["bgm_normal"] = self.save_wave("bgm_normal.wav", bgm_data)

            # 17. BGM Boss
            boss_bgm_data = []
            bpm = 170; beat_dur = 60 / bpm; total_beats = 32
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur); freq = 55.0 if (beat // 4) % 2 == 0 else 65.41 
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate; val_bass = (2 * (t_local * freq - math.floor(t_local * freq + 0.5))) * 0.5; val_bass *= math.exp(-t_local * 4)
                    val_drum = 0
                    if beat % 2 == 0: val_drum += math.sin(2 * math.pi * 90 * math.exp(-t_local*25) * t_local) * 0.9 * math.exp(-t_local*10)
                    if beat % 4 == 2: val_drum += random.uniform(-0.9, 0.9) * 0.6 * math.exp(-t_local*20)
                    val_lead = 0
                    if beat % 8 == 0: val_lead = math.sin(2 * math.pi * (900 - t_local*300) * t_local) * 0.25 * math.exp(-t_local*2)
                    mix = (val_bass + val_drum + val_lead) * 0.5; mix = max(-0.7, min(0.7, mix))
                    boss_bgm_data.append(mix)
            # 应用压缩和归一化
            boss_bgm_data = self.apply_compressor(boss_bgm_data, threshold=0.6, ratio=0.4)
            boss_bgm_data = self.normalize_audio(boss_bgm_data, 0.58)
            paths["bgm_boss"] = self.save_wave("bgm_boss.wav", boss_bgm_data)

            # 18. BGM Calm (宁静氛围 - 适合秋日枫林、水晶洞穴、镜面盐湖)
            calm_bgm = []
            bpm = 90; beat_dur = 60 / bpm; total_beats = 16
            melody = [329.63, 349.23, 392.00, 440.00, 392.00, 349.23, 329.63, 293.66]  # E F G A G F E D
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                melody_freq = melody[beat % len(melody)]
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 柔和的旋律
                    val_melody = math.sin(2 * math.pi * melody_freq * t_local) * 0.25 * math.exp(-t_local * 2)
                    # 轻柔的和声
                    val_harmony = math.sin(2 * math.pi * (melody_freq * 0.75) * t_local) * 0.15 * math.exp(-t_local * 3)
                    # 轻微的节奏
                    val_perc = 0
                    if beat % 4 == 0 and i < 1000:
                        val_perc = random.uniform(-0.2, 0.2) * math.exp(-t_local * 10)
                    calm_bgm.append((val_melody + val_harmony + val_perc) * 0.45)
            # 应用低通滚波
            calm_bgm = self.apply_lowpass_filter(calm_bgm, 0.35)
            calm_bgm = self.normalize_audio(calm_bgm, 0.5)
            paths["bgm_calm"] = self.save_wave("bgm_calm.wav", calm_bgm)

            # 19. BGM Mystery (神秘氛围 - 适合深海、遗忘都市、量子泡沫)
            mystery_bgm = []
            bpm = 100; beat_dur = 60 / bpm; total_beats = 20
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 缓慢变化的低音
                    bass_freq = 65 + 10 * math.sin(beat * 0.5)
                    val_bass = math.sin(2 * math.pi * bass_freq * t_local) * 0.3 * math.exp(-t_local * 3)
                    # 神秘的高频音效
                    val_high = math.sin(2 * math.pi * (1200 + 200 * math.sin(t_local * 3)) * t_local) * 0.1 * (1 - t_local)
                    # 回响效果
                    val_echo = 0
                    if beat % 5 == 0:
                        val_echo = math.sin(2 * math.pi * 880 * t_local) * 0.15 * math.exp(-t_local * 5)
                    mystery_bgm.append((val_bass + val_high + val_echo) * 0.4)
            # 应用低通滚波
            mystery_bgm = self.apply_lowpass_filter(mystery_bgm, 0.35)
            mystery_bgm = self.normalize_audio(mystery_bgm, 0.52)
            paths["bgm_mystery"] = self.save_wave("bgm_mystery.wav", mystery_bgm)

            # 20. BGM Epic (史诗战斗 - 适合太空战场、时空裂隙、破碎天空)
            epic_bgm = []
            bpm = 150; beat_dur = 60 / bpm; total_beats = 32
            power_chords = [82.41, 87.31, 98.00, 110.00]  # E F G A
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                chord_freq = power_chords[(beat // 4) % len(power_chords)]
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 强劲的低音
                    val_bass = (2 * (t_local * chord_freq - math.floor(t_local * chord_freq + 0.5))) * 0.5 * math.exp(-t_local * 3)
                    # 重鼓点
                    val_drum = 0
                    if beat % 2 == 0:
                        val_drum = math.sin(2 * math.pi * 80 * math.exp(-t_local*30) * t_local) * 0.8 * math.exp(-t_local*12)
                    # 高频旋律
                    val_lead = math.sin(2 * math.pi * (chord_freq * 6 + 100 * math.sin(beat * 0.7)) * t_local) * 0.2 * math.exp(-t_local * 4)
                    epic_bgm.append((val_bass + val_drum + val_lead) * 0.55)
            # 应用压缩和归一化
            epic_bgm = self.apply_compressor(epic_bgm, threshold=0.6, ratio=0.4)
            epic_bgm = self.normalize_audio(epic_bgm, 0.58)
            paths["bgm_epic"] = self.save_wave("bgm_epic.wav", epic_bgm)

            # 21. BGM Intense (紧张激烈 - 适合雷暴、火山、战争废墟)
            intense_bgm = []
            bpm = 140; beat_dur = 60 / bpm; total_beats = 24
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 快速变化的锯齿波
                    freq = 110 + 20 * (beat % 4)
                    val_saw = (2 * (t_local * freq - math.floor(t_local * freq + 0.5))) * 0.4
                    # 密集的打击乐
                    val_perc = 0
                    if beat % 1 == 0:
                        val_perc = random.uniform(-0.7, 0.7) * math.exp(-t_local * 15)
                    # 急促的高音
                    val_stab = 0
                    if beat % 2 == 0:
                        val_stab = math.sin(2 * math.pi * 1760 * t_local) * 0.3 * math.exp(-t_local * 8)
                    intense_bgm.append((val_saw + val_perc + val_stab) * 0.5)
            # 应用压缩防止过载
            intense_bgm = self.apply_compressor(intense_bgm, threshold=0.6, ratio=0.4)
            intense_bgm = self.normalize_audio(intense_bgm, 0.56)
            paths["bgm_intense"] = self.save_wave("bgm_intense.wav", intense_bgm)

            # 22. BGM Cyber (电子科技 - 适合数字矩阵、城市上空)
            cyber_bgm = []
            bpm = 128; beat_dur = 60 / bpm; total_beats = 16
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 电子贝斯
                    bass_freq = 65 if beat % 8 < 4 else 73
                    val_bass = (1.0 if math.sin(2 * math.pi * bass_freq * t_local) > 0 else -1.0) * 0.35 * math.exp(-t_local * 4)
                    # 4/4拍的鼓点
                    val_kick = 0
                    if beat % 4 == 0:
                        val_kick = math.sin(2 * math.pi * 50 * math.exp(-t_local*25) * t_local) * 0.7 * math.exp(-t_local*10)
                    # 电子琶音
                    arp_notes = [523, 659, 784, 1047]  # C E G C'
                    arp_freq = arp_notes[(beat * 4 + int(t_local * 8)) % len(arp_notes)]
                    val_arp = math.sin(2 * math.pi * arp_freq * t_local) * 0.15 * math.exp(-t_local * 6)
                    cyber_bgm.append((val_bass + val_kick + val_arp) * 0.48)
            # 应用低通滚波和归一化
            cyber_bgm = self.apply_lowpass_filter(cyber_bgm, 0.4)
            cyber_bgm = self.normalize_audio(cyber_bgm, 0.55)
            paths["bgm_cyber"] = self.save_wave("bgm_cyber.wav", cyber_bgm)

            # 23. BGM Ethereal (空灵飘渺 - 适合晨曦云海、极光彩幕)
            ethereal_bgm = []
            bpm = 80; beat_dur = 60 / bpm; total_beats = 12
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 缓慢的音垫
                    pad_freq = 220 + 55 * math.sin(beat * 0.3)
                    val_pad = math.sin(2 * math.pi * pad_freq * t_local) * 0.2
                    val_pad += math.sin(2 * math.pi * pad_freq * 1.5 * t_local) * 0.15
                    # 飘渺的高音
                    shimmer_freq = 1760 + 440 * math.sin(t_local * 2 + beat * 0.5)
                    val_shimmer = math.sin(2 * math.pi * shimmer_freq * t_local) * 0.1 * math.exp(-t_local * 1)
                    ethereal_bgm.append((val_pad + val_shimmer) * 0.4)
            # 应用低通滚波
            ethereal_bgm = self.apply_lowpass_filter(ethereal_bgm, 0.3)
            ethereal_bgm = self.normalize_audio(ethereal_bgm, 0.5)
            paths["bgm_ethereal"] = self.save_wave("bgm_ethereal.wav", ethereal_bgm)
            
            # 24. Achievement (成就解锁)
            data = []; notes = [523, 659, 784, 1047]
            for freq in notes: data.extend(self.generate_tone(freq, 0.15, 0.5, "square"))
            paths["achievement"] = self.save_wave("achievement.wav", data)
            
            # 19. Item Pickup (捡物品)
            data = []; dur = 0.25
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; freq = 600 + 400 * t; v = math.sin(2 * math.pi * freq * t) * 0.4 * (1 - t/dur); data.append(v)
            paths["item_pickup"] = self.save_wave("item_pickup.wav", data)
            
            # 20. Critical Hit (暴击)
            data = []; dur = 0.2
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; v = (2 * (t * 800 - math.floor(t * 800 + 0.5))) * 0.6 * (1 - t/dur); data.append(v)
            paths["critical"] = self.save_wave("critical.wav", data)
            
            # 21. Heal (治疗)
            data = []; notes = [440, 550, 660]
            for freq in notes: data.extend(self.generate_tone(freq, 0.1, 0.35, "sine"))
            paths["heal"] = self.save_wave("heal.wav", data)
            
            # 22. Shield (护盾激活)
            data = []; dur = 0.4
            for i in range(int(self.sample_rate * dur)):
                t = i / self.sample_rate; freq = 800 + 200 * math.sin(2 * math.pi * 5 * t); v = math.sin(2 * math.pi * freq * t) * 0.35 * (1 - t/dur); data.append(v)
            paths["shield"] = self.save_wave("shield.wav", data)

            # ===== 新增丰富的BGM音乐 =====
            
            # 23. BGM Orchestra (管弦乐 - 史诗战斗)
            orchestra_bgm = []
            bpm = 140; beat_dur = 60 / bpm; total_beats = 32
            melody_notes = [523, 587, 659, 698, 784, 880]  # C D E F G A
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                note_idx = (beat // 2) % len(melody_notes)
                melody_freq = melody_notes[note_idx]
                
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 弦乐组 - organ音色模拟弦乐
                    val_strings = (math.sin(2 * math.pi * melody_freq * t_local) * 0.3 +
                                  math.sin(4 * math.pi * melody_freq * t_local) * 0.15 +
                                  math.sin(6 * math.pi * melody_freq * t_local) * 0.08) * 0.25
                    # 铜管组 - 低八度的强音
                    val_brass = math.sin(2 * math.pi * (melody_freq * 0.5) * t_local) * 0.18 * (1 if beat % 4 == 0 else 0.4)
                    # 定音鼓
                    val_timpani = 0
                    if beat % 4 == 0 and i < 2000:
                        val_timpani = math.sin(2 * math.pi * 65 * t_local) * 0.25 * math.exp(-t_local * 8)
                    orchestra_bgm.append((val_strings + val_brass + val_timpani) * 0.5)
            # 应用低通滤波和归一化
            orchestra_bgm = self.apply_lowpass_filter(orchestra_bgm, 0.4)
            orchestra_bgm = self.normalize_audio(orchestra_bgm, 0.6)
            paths["bgm_orchestra"] = self.save_wave("bgm_orchestra.wav", orchestra_bgm)
            
            # 24. BGM Jazz (爵士 - 休闲探索)
            jazz_bgm = []
            bpm = 110; beat_dur = 60 / bpm; total_beats = 24
            jazz_progression = [262, 330, 392, 349]  # C E G F (爵士和弦根音)
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                bass_note = jazz_progression[(beat // 4) % len(jazz_progression)]
                
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 爵士低音 - walking bass
                    val_bass = math.sin(2 * math.pi * bass_note * t_local) * 0.3 * math.exp(-t_local * 2)
                    # 钢琴和弦 - bell音色
                    val_piano = 0
                    if beat % 2 == 0 and i < 5000:
                        chord_notes = [bass_note * 2, bass_note * 2.5, bass_note * 3]
                        for note in chord_notes:
                            val_piano += (math.sin(2 * math.pi * note * t_local) * 0.15 +
                                        math.sin(4 * math.pi * note * t_local) * 0.08 * math.exp(-t_local * 3))
                    # 爵士刷子鼓
                    val_brush = 0
                    if beat % 1 == 0 and i < 500:
                        val_brush = random.uniform(-0.15, 0.15) * math.exp(-t_local * 15)
                    jazz_bgm.append((val_bass + val_piano + val_brush) * 0.45)
            # 应用低通滚波和归一化
            jazz_bgm = self.apply_lowpass_filter(jazz_bgm, 0.4)
            jazz_bgm = self.normalize_audio(jazz_bgm, 0.55)
            paths["bgm_jazz"] = self.save_wave("bgm_jazz.wav", jazz_bgm)
            
            # 25. BGM Piano (钢琴独奏 - 情感场景)
            piano_bgm = []
            bpm = 90; beat_dur = 60 / bpm; total_beats = 20
            piano_melody = [392, 440, 523, 587, 523, 440, 392, 349]  # G A C D C A G F
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                note = piano_melody[beat % len(piano_melody)]
                
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 钢琴主旋律 - bell音色
                    val_melody = (math.sin(2 * math.pi * note * t_local) * 0.5 +
                                 math.sin(4 * math.pi * note * t_local) * 0.25 * math.exp(-t_local * 2) +
                                 math.sin(6 * math.pi * note * t_local) * 0.15 * math.exp(-t_local * 4))
                    val_melody *= math.exp(-t_local * 1.5)
                    # 和弦伴奏
                    val_chord = 0
                    if beat % 4 == 0:
                        chord_root = note * 0.5
                        val_chord = math.sin(2 * math.pi * chord_root * t_local) * 0.15 * math.exp(-t_local * 2)
                    piano_bgm.append((val_melody + val_chord) * 0.5)
            # 应用低通滚波和归一化
            piano_bgm = self.apply_lowpass_filter(piano_bgm, 0.35)
            piano_bgm = self.normalize_audio(piano_bgm, 0.55)
            paths["bgm_piano"] = self.save_wave("bgm_piano.wav", piano_bgm)
            
            # 26. BGM Rock (摇滚 - 高能战斗)
            rock_bgm = []
            bpm = 160; beat_dur = 60 / bpm; total_beats = 32
            power_riff = [82, 98, 110, 98]  # E G A G (强力Riff)
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                riff_note = power_riff[(beat // 2) % len(power_riff)]
                
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 失真吉他 - saw波 + 过载
                    val_guitar = (2 * (t_local * riff_note - math.floor(t_local * riff_note + 0.5)))
                    val_guitar = max(-0.8, min(0.8, val_guitar * 1.5)) * 0.4  # 过载效果
                    # 贝斯 - 低八度
                    val_bass = (2 * (t_local * (riff_note * 0.5) - math.floor(t_local * (riff_note * 0.5) + 0.5))) * 0.35
                    # 摇滚鼓组
                    val_drums = 0
                    if beat % 2 == 0 and i < 1500:  # Kick
                        val_drums += math.sin(2 * math.pi * 60 * math.exp(-t_local * 25) * t_local) * 0.6 * math.exp(-t_local * 10)
                    if beat % 4 == 2 and i < 800:  # Snare
                        val_drums += (math.sin(2 * math.pi * 200 * t_local) * 0.3 + random.uniform(-0.5, 0.5)) * math.exp(-t_local * 15)
                    if beat % 1 == 0 and i < 300:  # Hi-hat
                        val_drums += random.uniform(-0.2, 0.2) * math.exp(-t_local * 35)
                    rock_bgm.append((val_guitar + val_bass + val_drums) * 0.55)
            # 应用压缩和归一化
            rock_bgm = self.apply_compressor(rock_bgm, threshold=0.6, ratio=0.4)
            rock_bgm = self.normalize_audio(rock_bgm, 0.6)
            paths["bgm_rock"] = self.save_wave("bgm_rock.wav", rock_bgm)
            
            # 27. BGM Ambient (环境音乐 - 探索场景)
            ambient_bgm = []
            bpm = 60; beat_dur = 60 / bpm; total_beats = 16
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                for i in range(samples_per_beat):
                    t = beat * beat_dur + i / self.sample_rate
                    # 深沉的音垫层
                    val_pad1 = math.sin(2 * math.pi * 110 * t + math.sin(t * 0.3)) * 0.15
                    val_pad2 = math.sin(2 * math.pi * 165 * t + math.sin(t * 0.5)) * 0.12
                    val_pad3 = math.sin(2 * math.pi * 220 * t + math.sin(t * 0.7)) * 0.10
                    # 飘渺的高音
                    val_high = math.sin(2 * math.pi * (1760 + 220 * math.sin(t * 0.2)) * (i / self.sample_rate)) * 0.08
                    ambient_bgm.append((val_pad1 + val_pad2 + val_pad3 + val_high) * 0.4)
            # 应用低通滚波
            ambient_bgm = self.apply_lowpass_filter(ambient_bgm, 0.3)
            ambient_bgm = self.normalize_audio(ambient_bgm, 0.5)
            paths["bgm_ambient"] = self.save_wave("bgm_ambient.wav", ambient_bgm)
            
            # 28. BGM Electronic (电子舞曲 - 快节奏)
            electronic_bgm = []
            bpm = 130; beat_dur = 60 / bpm; total_beats = 32
            edm_bass = [65, 73, 82, 73]  # E F# G F#
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                bass_freq = edm_bass[(beat // 4) % len(edm_bass)]
                
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 重低音 - square波
                    val_sub = (1.0 if math.sin(2 * math.pi * bass_freq * t_local) > 0 else -1.0) * 0.4
                    # 合成器主音
                    val_synth = math.sin(2 * math.pi * (bass_freq * 4) * t_local + math.sin(2 * math.pi * 5 * t_local)) * 0.25
                    # 电子鼓
                    val_edrum = 0
                    if beat % 4 == 0 and i < 1200:
                        val_edrum += math.sin(2 * math.pi * 50 * math.exp(-t_local * 30) * t_local) * 0.7 * math.exp(-t_local * 12)
                    if beat % 2 == 1 and i < 600:
                        val_edrum += random.uniform(-0.4, 0.4) * math.exp(-t_local * 20)
                    # 合成器音效
                    val_fx = 0
                    if beat % 8 == 0:
                        val_fx = math.sin(2 * math.pi * (4000 * (1 - t_local * 2)) * t_local) * 0.15 * math.exp(-t_local * 3)
                    electronic_bgm.append((val_sub + val_synth + val_edrum + val_fx) * 0.5)
            # 应用压缩和归一化
            electronic_bgm = self.apply_compressor(electronic_bgm, threshold=0.65, ratio=0.4)
            electronic_bgm = self.normalize_audio(electronic_bgm, 0.58)
            paths["bgm_electronic"] = self.save_wave("bgm_electronic.wav", electronic_bgm)
            
            # 29. BGM Chiptune (8位芯片音乐 - 复古风格)
            chiptune_bgm = []
            bpm = 150; beat_dur = 60 / bpm; total_beats = 24
            chip_melody = [659, 784, 880, 784, 659, 523, 587, 659]  # E G A G E C D E
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                note = chip_melody[beat % len(chip_melody)]
                
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 主旋律 - square波 (8位风格)
                    val_melody = (1.0 if math.sin(2 * math.pi * note * t_local) > 0 else -1.0) * 0.25 * math.exp(-t_local * 3)
                    # 贝斯 - square波
                    val_bass = (1.0 if math.sin(2 * math.pi * (note * 0.25) * t_local) > 0 else -1.0) * 0.3 * (1 if beat % 2 == 0 else 0.5)
                    # 噪音通道 - 节奏
                    val_noise = 0
                    if beat % 4 == 0 and i < 500:
                        val_noise = random.uniform(-0.3, 0.3) * math.exp(-t_local * 20)
                    # 琶音
                    arp_notes = [note, note * 1.5, note * 2]
                    arp_idx = int((t_local * 8) % 3)
                    val_arp = (1.0 if math.sin(2 * math.pi * arp_notes[arp_idx] * t_local) > 0 else -1.0) * 0.15
                    chiptune_bgm.append((val_melody + val_bass + val_noise + val_arp) * 0.45)
            # 应用低通滚波减少方波刺耳
            chiptune_bgm = self.apply_lowpass_filter(chiptune_bgm, 0.45)
            chiptune_bgm = self.normalize_audio(chiptune_bgm, 0.55)
            paths["bgm_chiptune"] = self.save_wave("bgm_chiptune.wav", chiptune_bgm)
            
            # 30. BGM Tribal (部落节奏 - 原始战斗)
            tribal_bgm = []
            bpm = 120; beat_dur = 60 / bpm; total_beats = 32
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 深沉的鼓点
                    val_drum = 0
                    if beat % 2 == 0 and i < 2000:
                        val_drum = math.sin(2 * math.pi * 45 * math.exp(-t_local * 20) * t_local) * 0.7 * math.exp(-t_local * 8)
                    if beat % 4 == 1 and i < 1500:
                        val_drum += math.sin(2 * math.pi * 90 * t_local) * 0.5 * math.exp(-t_local * 10)
                    if beat % 4 == 3 and i < 1500:
                        val_drum += math.sin(2 * math.pi * 70 * t_local) * 0.5 * math.exp(-t_local * 10)
                    # 部落人声 (低沉的吟唱)
                    val_chant = 0
                    if beat % 8 == 0:
                        chant_freq = 110 + 20 * math.sin(t_local * 3)
                        val_chant = math.sin(2 * math.pi * chant_freq * t_local) * 0.2 * (1 - t_local * 0.5)
                    # 打击乐器
                    val_perc = 0
                    if beat % 1 == 0 and i < 300:
                        val_perc = random.uniform(-0.25, 0.25) * math.exp(-t_local * 25)
                    tribal_bgm.append((val_drum + val_chant + val_perc) * 0.55)
            # 应用压缩和归一化
            tribal_bgm = self.apply_compressor(tribal_bgm, threshold=0.6, ratio=0.4)
            tribal_bgm = self.normalize_audio(tribal_bgm, 0.58)
            paths["bgm_tribal"] = self.save_wave("bgm_tribal.wav", tribal_bgm)
            
            # 31. BGM Dubstep (重低音电子 - 疯狂战斗)
            dubstep_bgm = []
            bpm = 140; beat_dur = 60 / bpm; total_beats = 24
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # Wobble贝斯 - LFO调制的低音
                    wobble_freq = 65 + 30 * abs(math.sin(2 * math.pi * 4 * (beat * beat_dur + t_local)))
                    val_wobble = (2 * (t_local * wobble_freq - math.floor(t_local * wobble_freq + 0.5)))
                    val_wobble = max(-0.8, min(0.8, val_wobble * 2)) * 0.45  # 过载
                    # 陷阱鼓
                    val_trap = 0
                    if beat % 4 == 0 and i < 1000:
                        val_trap = math.sin(2 * math.pi * 55 * math.exp(-t_local * 30) * t_local) * 0.8 * math.exp(-t_local * 10)
                    if beat % 4 == 2 and i < 500:
                        val_trap += (random.uniform(-0.7, 0.7) + math.sin(2 * math.pi * 180 * t_local) * 0.3) * math.exp(-t_local * 12)
                    # Hi-hat快速律动
                    if i % 200 < 100 and i < 3000:
                        val_trap += random.uniform(-0.15, 0.15) * math.exp(-t_local * 40)
                    dubstep_bgm.append((val_wobble + val_trap) * 0.5)
            # 应用压缩器防止过载
            dubstep_bgm = self.apply_compressor(dubstep_bgm, threshold=0.5, ratio=0.35)
            dubstep_bgm = self.normalize_audio(dubstep_bgm, 0.55)
            paths["bgm_dubstep"] = self.save_wave("bgm_dubstep.wav", dubstep_bgm)
            
            # 32. BGM Synthwave (合成器波 - 赛博朋克)
            synthwave_bgm = []
            bpm = 120; beat_dur = 60 / bpm; total_beats = 32
            synthwave_chords = [220, 247, 277, 293]  # A B C# D
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                chord = synthwave_chords[(beat // 4) % len(synthwave_chords)]
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 合成贝斯线
                    val_bass = (2 * (t_local * chord * 0.5 - math.floor(t_local * chord * 0.5 + 0.5))) * 0.4
                    # 复古合成器和弦
                    val_synth = (math.sin(2 * math.pi * chord * t_local) * 0.25 +
                                math.sin(2 * math.pi * chord * 1.5 * t_local) * 0.15 +
                                math.sin(2 * math.pi * chord * 2 * t_local) * 0.1)
                    # 琶音器
                    arp_speed = 8
                    arp_notes = [chord * 2, chord * 2.5, chord * 3, chord * 4]
                    arp_idx = int((t_local * arp_speed) % len(arp_notes))
                    val_arp = math.sin(2 * math.pi * arp_notes[arp_idx] * t_local) * 0.15 * math.exp(-t_local * 4)
                    # 80年代电子鼓
                    val_drum = 0
                    if beat % 4 == 0 and i < 1500:
                        val_drum = (1.0 if math.sin(2 * math.pi * 60 * math.exp(-t_local * 20) * t_local) > 0 else -1.0) * 0.6 * math.exp(-t_local * 8)
                    if beat % 4 == 2 and i < 800:
                        val_drum += random.uniform(-0.4, 0.4) * 0.5 * math.exp(-t_local * 15)
                    synthwave_bgm.append((val_bass + val_synth + val_arp + val_drum) * 0.5)
            # 应用低通滚波和归一化
            synthwave_bgm = self.apply_lowpass_filter(synthwave_bgm, 0.4)
            synthwave_bgm = self.normalize_audio(synthwave_bgm, 0.58)
            paths["bgm_synthwave"] = self.save_wave("bgm_synthwave.wav", synthwave_bgm)
            
            # 33. BGM Metal (金属摇滚 - 极限战斗)
            metal_bgm = []
            bpm = 180; beat_dur = 60 / bpm; total_beats = 32
            metal_riff = [82, 73, 82, 92, 82, 73, 65, 73]  # E D E F# E D C# D
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                note = metal_riff[beat % len(metal_riff)]
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 重失真吉他 - 双音轨
                    val_guitar1 = (2 * (t_local * note - math.floor(t_local * note + 0.5)))
                    val_guitar1 = max(-0.9, min(0.9, val_guitar1 * 2.5)) * 0.35
                    val_guitar2 = (2 * (t_local * note * 2 - math.floor(t_local * note * 2 + 0.5)))
                    val_guitar2 = max(-0.9, min(0.9, val_guitar2 * 2.5)) * 0.25
                    # 金属贝斯
                    val_bass = (2 * (t_local * note * 0.5 - math.floor(t_local * note * 0.5 + 0.5))) * 0.4
                    # 双踩底鼓
                    val_drums = 0
                    if beat % 1 == 0 and i < 800:
                        val_drums = math.sin(2 * math.pi * 50 * math.exp(-t_local * 35) * t_local) * 0.8 * math.exp(-t_local * 12)
                    if beat % 4 == 2 and i < 600:
                        val_drums += (math.sin(2 * math.pi * 220 * t_local) * 0.3 + random.uniform(-0.6, 0.6)) * math.exp(-t_local * 18)
                    # 镲片疯狂打击
                    if i < 400:
                        val_drums += random.uniform(-0.2, 0.2) * math.exp(-t_local * 50)
                    metal_bgm.append((val_guitar1 + val_guitar2 + val_bass + val_drums) * 0.55)
            # 应用压缩防止失真过度
            metal_bgm = self.apply_compressor(metal_bgm, threshold=0.55, ratio=0.35)
            metal_bgm = self.normalize_audio(metal_bgm, 0.58)
            paths["bgm_metal"] = self.save_wave("bgm_metal.wav", metal_bgm)
            
            # 34. BGM Trance (迷幻电子 - 催眠节奏)
            trance_bgm = []
            bpm = 138; beat_dur = 60 / bpm; total_beats = 32
            trance_progression = [165, 185, 196, 220]  # E F# G A
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                base_note = trance_progression[(beat // 8) % len(trance_progression)]
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 迷幻主音 - FM合成
                    mod_freq = 5
                    carrier = base_note * 2
                    val_lead = math.sin(2 * math.pi * carrier * t_local + 2 * math.sin(2 * math.pi * mod_freq * t_local)) * 0.3
                    # Trance门控贝斯
                    gate = 1.0 if (beat % 2 == 0 and i < samples_per_beat // 2) else 0.3
                    val_bass = math.sin(2 * math.pi * base_note * t_local) * 0.35 * gate
                    # 4/4节拍
                    val_kick = 0
                    if beat % 4 == 0 and i < 1200:
                        val_kick = math.sin(2 * math.pi * 55 * math.exp(-t_local * 25) * t_local) * 0.7 * math.exp(-t_local * 10)
                    # 升降音效
                    val_riser = 0
                    if beat % 16 >= 12:
                        riser_freq = 200 * (1 + (beat % 16 - 12) * 0.5)
                        val_riser = random.uniform(-0.15, 0.15) * (1 - math.exp(-t_local * 10))
                    trance_bgm.append((val_lead + val_bass + val_kick + val_riser) * 0.5)
            # 应用低通滚波和压缩
            trance_bgm = self.apply_lowpass_filter(trance_bgm, 0.4)
            trance_bgm = self.apply_compressor(trance_bgm, threshold=0.6, ratio=0.4)
            trance_bgm = self.normalize_audio(trance_bgm, 0.57)
            paths["bgm_trance"] = self.save_wave("bgm_trance.wav", trance_bgm)
            
            # 35. BGM Orchestral_Dark (黑暗管弦 - 恐怖氛围)
            dark_orch_bgm = []
            bpm = 100; beat_dur = 60 / bpm; total_beats = 20
            dark_notes = [110, 117, 123, 131]  # A A# B C (不协和音程)
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                note = dark_notes[(beat // 4) % len(dark_notes)]
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 低沉弦乐组 - 不协和和弦
                    val_strings = (math.sin(2 * math.pi * note * t_local) * 0.3 +
                                  math.sin(2 * math.pi * note * 1.06 * t_local) * 0.25 +  # 微分音
                                  math.sin(2 * math.pi * note * 0.5 * t_local) * 0.2)
                    # 定音鼓轰鸣
                    val_timpani = 0
                    if beat % 8 == 0 and i < 3000:
                        val_timpani = math.sin(2 * math.pi * 50 * t_local) * 0.5 * math.exp(-t_local * 3)
                    # 不祥的铜管
                    val_brass = 0
                    if beat % 4 == 2:
                        val_brass = (2 * (t_local * (note * 0.75) - math.floor(t_local * (note * 0.75) + 0.5))) * 0.3 * (1 - t_local * 0.5)
                    dark_orch_bgm.append((val_strings + val_timpani + val_brass) * 0.48)
            # 应用低通滚波和归一化
            dark_orch_bgm = self.apply_lowpass_filter(dark_orch_bgm, 0.35)
            dark_orch_bgm = self.normalize_audio(dark_orch_bgm, 0.55)
            paths["bgm_orchestral_dark"] = self.save_wave("bgm_orchestral_dark.wav", dark_orch_bgm)
            
            # 36. BGM Funk (放克 - 律动感)
            funk_bgm = []
            bpm = 115; beat_dur = 60 / bpm; total_beats = 24
            funk_bassline = [82, 82, 98, 82, 110, 98, 82, 73]  # E E G E A G E D
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                bass_note = funk_bassline[beat % len(funk_bassline)]
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # Slap贝斯
                    val_bass = (2 * (t_local * bass_note - math.floor(t_local * bass_note + 0.5))) * 0.4 * math.exp(-t_local * 3)
                    # 放克吉他 - 切分节奏
                    val_guitar = 0
                    if (beat % 4 == 1 or beat % 4 == 3) and i < 800:
                        guitar_freq = bass_note * 2
                        val_guitar = (1.0 if math.sin(2 * math.pi * guitar_freq * t_local) > 0 else -1.0) * 0.2 * math.exp(-t_local * 8)
                    # 铜管刺 (horn stabs)
                    val_horns = 0
                    if beat % 8 == 4 and i < 1500:
                        val_horns = math.sin(2 * math.pi * (bass_note * 3) * t_local) * 0.25 * math.exp(-t_local * 4)
                    # 放克鼓
                    val_drums = 0
                    if beat % 4 == 0 and i < 1000:
                        val_drums = math.sin(2 * math.pi * 60 * math.exp(-t_local * 20) * t_local) * 0.6 * math.exp(-t_local * 10)
                    if beat % 4 == 2 and i < 700:
                        val_drums += (math.sin(2 * math.pi * 200 * t_local) * 0.25 + random.uniform(-0.3, 0.3)) * math.exp(-t_local * 14)
                    if beat % 2 == 1 and i < 400:
                        val_drums += random.uniform(-0.15, 0.15) * math.exp(-t_local * 25)
                    funk_bgm.append((val_bass + val_guitar + val_horns + val_drums) * 0.52)
            # 应用低通滚波和归一化
            funk_bgm = self.apply_lowpass_filter(funk_bgm, 0.4)
            funk_bgm = self.normalize_audio(funk_bgm, 0.57)
            paths["bgm_funk"] = self.save_wave("bgm_funk.wav", funk_bgm)
            
            # 37. BGM Breakbeat (碎拍 - 快速节奏)
            breakbeat_bgm = []
            bpm = 150; beat_dur = 60 / bpm; total_beats = 24
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 切碎的鼓循环
                    val_drums = 0
                    # Kick模式
                    kick_pattern = [0, 6, 8, 14]
                    sixteenth = int((t_local * 16) // 1)
                    if sixteenth in kick_pattern and (t_local * 16) % 1 < 0.3:
                        kick_t = (t_local * 16) % 1
                        val_drums = math.sin(2 * math.pi * 55 * math.exp(-kick_t * 25) * kick_t) * 0.7 * math.exp(-kick_t * 10)
                    # Snare模式
                    snare_pattern = [4, 12]
                    if sixteenth in snare_pattern and (t_local * 16) % 1 < 0.2:
                        snare_t = (t_local * 16) % 1
                        val_drums += (math.sin(2 * math.pi * 200 * snare_t) * 0.3 + random.uniform(-0.5, 0.5)) * math.exp(-snare_t * 15)
                    # Hi-hat碎拍
                    if (t_local * 32) % 1 < 0.1:
                        val_drums += random.uniform(-0.2, 0.2) * math.exp(-(t_local * 32 % 1) * 40)
                    # Reese贝斯
                    bass_freq = 65 if beat % 8 < 4 else 73
                    val_bass = (2 * (t_local * bass_freq - math.floor(t_local * bass_freq + 0.5))) * 0.35
                    val_bass += (2 * (t_local * bass_freq * 1.01 - math.floor(t_local * bass_freq * 1.01 + 0.5))) * 0.35  # 微分音产生厚度
                    breakbeat_bgm.append((val_drums + val_bass) * 0.5)
            # 应用压缩和归一化
            breakbeat_bgm = self.apply_compressor(breakbeat_bgm, threshold=0.6, ratio=0.4)
            breakbeat_bgm = self.normalize_audio(breakbeat_bgm, 0.57)
            paths["bgm_breakbeat"] = self.save_wave("bgm_breakbeat.wav", breakbeat_bgm)
            
            # 38. BGM Lofi (Lo-fi Hip Hop - 放松氛围)
            lofi_bgm = []
            bpm = 85; beat_dur = 60 / bpm; total_beats = 16
            lofi_chords = [220, 247, 196, 220]  # A B G A
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                chord = lofi_chords[(beat // 4) % len(lofi_chords)]
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 温暖的和弦 - 模拟黑胶质感
                    val_chord = (math.sin(2 * math.pi * chord * t_local) * 0.2 +
                                math.sin(2 * math.pi * chord * 1.5 * t_local) * 0.15 +
                                math.sin(2 * math.pi * chord * 2 * t_local) * 0.1)
                    # 加入轻微噪音模拟黑胶
                    val_chord += random.uniform(-0.02, 0.02)
                    # Lo-fi节拍
                    val_beat = 0
                    if beat % 4 == 0 and i < 2000:
                        val_beat = math.sin(2 * math.pi * 50 * math.exp(-t_local * 15) * t_local) * 0.5 * math.exp(-t_local * 8)
                    if beat % 4 == 2 and i < 1500:
                        val_beat += (math.sin(2 * math.pi * 180 * t_local) * 0.25 + random.uniform(-0.3, 0.3)) * math.exp(-t_local * 10)
                    # Hi-hat轻柔
                    if beat % 2 == 1 and i < 600:
                        val_beat += random.uniform(-0.1, 0.1) * math.exp(-t_local * 20)
                    lofi_bgm.append((val_chord + val_beat) * 0.45)
            # 应用低通滚波模拟黑胶质感
            lofi_bgm = self.apply_lowpass_filter(lofi_bgm, 0.3)
            lofi_bgm = self.normalize_audio(lofi_bgm, 0.52)
            paths["bgm_lofi"] = self.save_wave("bgm_lofi.wav", lofi_bgm)
            
            # 39. BGM Industrial (工业 - 机械感)
            industrial_bgm = []
            bpm = 130; beat_dur = 60 / bpm; total_beats = 24
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 金属敲击声
                    val_metal = 0
                    if beat % 2 == 0 and i < 500:
                        metal_freqs = [800, 1200, 1800]
                        for freq in metal_freqs:
                            val_metal += math.sin(2 * math.pi * freq * t_local) * 0.1 * math.exp(-t_local * 20)
                    # 机械噪音
                    val_noise = random.uniform(-0.3, 0.3) * 0.2 if i % 100 < 10 else 0
                    # 重工业鼓
                    val_drums = 0
                    if beat % 4 == 0 and i < 1500:
                        val_drums = (1.0 if math.sin(2 * math.pi * 45 * math.exp(-t_local * 30) * t_local) > 0 else -1.0) * 0.7 * math.exp(-t_local * 10)
                    if beat % 4 == 2 and i < 800:
                        val_drums += random.uniform(-0.6, 0.6) * 0.6 * math.exp(-t_local * 18)
                    # 失真贝斯
                    bass_freq = 55
                    val_bass = (2 * (t_local * bass_freq - math.floor(t_local * bass_freq + 0.5)))
                    val_bass = max(-0.85, min(0.85, val_bass * 2)) * 0.35
                    industrial_bgm.append((val_metal + val_noise + val_drums + val_bass) * 0.52)
            # 应用压缩和归一化
            industrial_bgm = self.apply_compressor(industrial_bgm, threshold=0.55, ratio=0.35)
            industrial_bgm = self.normalize_audio(industrial_bgm, 0.56)
            paths["bgm_industrial"] = self.save_wave("bgm_industrial.wav", industrial_bgm)
            
            # 40. BGM Cinematic (电影配乐 - 史诗叙事)
            cinematic_bgm = []
            bpm = 80; beat_dur = 60 / bpm; total_beats = 20
            cinematic_progression = [220, 247, 277, 294, 330]  # A B C# D E
            for beat in range(total_beats):
                samples_per_beat = int(self.sample_rate * beat_dur)
                note = cinematic_progression[(beat // 4) % len(cinematic_progression)]
                for i in range(samples_per_beat):
                    t_local = i / self.sample_rate
                    # 宏大的弦乐垫
                    val_strings = (math.sin(2 * math.pi * note * t_local) * 0.25 +
                                  math.sin(2 * math.pi * note * 1.5 * t_local) * 0.2 +
                                  math.sin(2 * math.pi * note * 2 * t_local) * 0.15 +
                                  math.sin(2 * math.pi * note * 0.5 * t_local) * 0.2)
                    # 法国号
                    val_horn = 0
                    if beat % 8 == 0:
                        val_horn = math.sin(2 * math.pi * (note * 0.75) * t_local) * 0.3 * (1 - t_local * 0.3)
                    # 定音鼓震撼
                    val_timp = 0
                    if beat % 4 == 0 and i < 3500:
                        val_timp = math.sin(2 * math.pi * 55 * t_local) * 0.6 * math.exp(-t_local * 2.5)
                    # 钟琴点缀
                    val_bells = 0
                    if beat % 2 == 0 and i < 2000:
                        bell_note = note * 4
                        val_bells = (math.sin(2 * math.pi * bell_note * t_local) * 0.15 +
                                    math.sin(4 * math.pi * bell_note * t_local) * 0.08 * math.exp(-t_local * 3))
                        val_bells *= math.exp(-t_local * 2)
                    cinematic_bgm.append((val_strings + val_horn + val_timp + val_bells) * 0.52)
            # 应用低通滚波和归一化
            cinematic_bgm = self.apply_lowpass_filter(cinematic_bgm, 0.35)
            cinematic_bgm = self.normalize_audio(cinematic_bgm, 0.58)
            paths["bgm_cinematic"] = self.save_wave("bgm_cinematic.wav", cinematic_bgm)

        except Exception as e:
            log_error(f"音频生成错误: {e}")
        return paths

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.current_bgm = None
        self.master_volume = 1.0  # 主音量
        self.sfx_volume = 0.8     # 音效音量
        self.music_volume = 0.5   # 音乐音量
        self.sound_channels = {}  # 跟踪正在播放的声道
        
        # 内部检查初始化状态，确保安全
        self.enabled = False
        try:
            if pygame.mixer.get_init():
                self.enabled = True
            else:
                # 尝试再次初始化，以防万一
                pygame.mixer.init()
                self.enabled = True
        except:
            self.enabled = False

        if self.enabled:
            try:
                self.synth = AudioSynthesizer()
                self.file_paths = self.synth.generate_all()
                self.load_sounds()
            except Exception as e:
                log_error(f"SoundManager init error: {e}")
                self.enabled = False

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
        }
        for name, path in self.file_paths.items():
            if path and not name.startswith("bgm"):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    vol = volume_map.get(name, 0.5)
                    self.sounds[name].set_volume(vol * self.sfx_volume)
                except: pass

    def play(self, name, volume=None):
        """播放音效，支持自定义音量"""
        if not self.enabled or name not in self.sounds:
            return
        try:
            sound = self.sounds[name]
            if volume is not None:
                sound.set_volume(volume * self.master_volume)
            channel = sound.play()
            self.sound_channels[name] = channel
        except: pass

    def play_music(self, track="normal"):
        if not self.enabled: return
        key = f"bgm_{track}"
        if key in self.file_paths and self.file_paths[key] and self.current_bgm != track:
            try:
                pygame.mixer.music.load(self.file_paths[key])
                pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
                pygame.mixer.music.play(-1)
                self.current_bgm = track
            except: pass

    def stop_music(self):
        if self.enabled:
            try: pygame.mixer.music.stop()
            except: pass
        self.current_bgm = None
    
    def set_master_volume(self, volume):
        """设置主音量（0.0 - 1.0）"""
        self.master_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
            for sound in self.sounds.values():
                try:
                    sound.set_volume(sound.get_volume() * (self.master_volume / (self.master_volume or 1)))
                except: pass
    
    def set_sfx_volume(self, volume):
        """设置音效音量（0.0 - 1.0）"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume):
        """设置音乐音量（0.0 - 1.0）"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

# ==============================================================================
#   绘图与UI工具
# ==============================================================================
def get_font(size, bold=False):
    font_names = ["roboto", "noto sans", "microsoftyahei", "simhei", "arial"]
    return pygame.font.SysFont(font_names, int(size), bold=bold)

# ==============================================================================
#   文本渲染缓存系统
# ==============================================================================
_text_cache = {}  # 缓存渲染好的文本surface
_cache_frame_counter = 0  # 帧计数器
_MAX_CACHE_SIZE = 500  # 最大缓存项数
_CACHE_CLEAN_INTERVAL = 60  # 每60帧清理一次

def _get_cache_key(text, size, color, effect):
    """生成缓存键"""
    return (str(text), int(size), tuple(color), effect)

def _clean_text_cache():
    """智能清理缓存"""
    global _text_cache, _cache_frame_counter
    _cache_frame_counter += 1
    
    # 每60帧或缓存超过500项时清理
    if _cache_frame_counter >= _CACHE_CLEAN_INTERVAL or len(_text_cache) > _MAX_CACHE_SIZE:
        # 只保留最近使用的一半
        if len(_text_cache) > _MAX_CACHE_SIZE // 2:
            # 简单策略：清空全部缓存
            _text_cache.clear()
        _cache_frame_counter = 0

def draw_text(surf, text, size, x, y, color=WHITE, align="center", shadow=True, glow=False):
    """优化的文本渲染函数 - 带缓存"""
    if surf is None:
        log_debug("draw_text: surf is None, skipping draw")
        return pygame.Rect(x, y, 0, 0)
    
    # 清理缓存（轻量级，每帧只检查一次）
    _clean_text_cache()
    
    # 确定效果类型
    if glow:
        effect = "glow"
    elif shadow:
        effect = "shadow"
    else:
        effect = "plain"
    
    # 生成缓存键
    cache_key = _get_cache_key(text, size, color, effect)
    
    # 尝试从缓存获取
    if cache_key in _text_cache:
        text_surface, shadow_surf, glow_surfaces = _text_cache[cache_key]
    else:
        # 渲染新的文本surface
        font = get_font(size, bold=True)
        text_surface = font.render(str(text), True, color)
        
        # 预渲染阴影和光晕
        shadow_surf = None
        glow_surfaces = None
        
        if glow:
            glow_color = (color[0]//2, color[1]//2, color[2]//2)
            glow_surf = font.render(str(text), True, glow_color)
            glow_surfaces = [glow_surf]  # 只需要一个glow surface，通过偏移多次绘制
        elif shadow:
            shadow_surf = font.render(str(text), True, (0,0,0))
        
        # 存入缓存
        _text_cache[cache_key] = (text_surface, shadow_surf, glow_surfaces)
    
    # 计算位置
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.midtop = (x, y)
    elif align == "left":
        text_rect.topleft = (x, y)
    elif align == "right":
        text_rect.topright = (x, y)
    
    # 绘制效果和文本
    if glow and glow_surfaces:
        glow_surf = glow_surfaces[0]
        surf.blit(glow_surf, (text_rect.x-1, text_rect.y))
        surf.blit(glow_surf, (text_rect.x+1, text_rect.y))
        surf.blit(glow_surf, (text_rect.x, text_rect.y-1))
        surf.blit(glow_surf, (text_rect.x, text_rect.y+1))
    elif shadow and shadow_surf:
        shadow_rect = text_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        surf.blit(shadow_surf, shadow_rect)
    
    surf.blit(text_surface, text_rect)
    return text_rect


def draw_mono_text(surf, text, size, x, y, color=WHITE, align="center", shadow=True):
    """Draw fixed-width (monospace) text, useful for counters / padded numbers."""
    monos = ["consolas", "courier new", "monaco"]
    font = pygame.font.SysFont(monos, int(size), bold=True)
    text_surface = font.render(str(text), True, color)
    rect = text_surface.get_rect()
    if align == "center": rect.midtop = (x, y)
    elif align == "left": rect.topleft = (x, y)
    elif align == "right": rect.topright = (x, y)
    if shadow:
        shadow_surf = font.render(str(text), True, (0,0,0))
        shadow_rect = rect.copy(); shadow_rect.x += 2; shadow_rect.y += 2
        surf.blit(shadow_surf, shadow_rect)
    surf.blit(text_surface, rect)
    return rect


def draw_spaced_text(surf, text, size, x, y, color=WHITE, align="center", spacing=2, shadow=True):
    """Draw text with increased letter-spacing (useful for headings)."""
    font = get_font(size, bold=True)
    # Compute width by summing characters
    total_w = sum(font.size(c)[0] for c in text) + spacing * (len(text) - 1)
    # Starting x depends on alignment
    if align == "center": start_x = x - total_w//2
    elif align == "left": start_x = x
    else: start_x = x - total_w
    cur_x = start_x
    for ch in text:
        ch_surf = font.render(ch, True, color)
        ch_rect = ch_surf.get_rect()
        ch_rect.topleft = (cur_x, y)
        if shadow:
            shadow_s = font.render(ch, True, (0,0,0))
            surf.blit(shadow_s, (cur_x+2, y+2))
        surf.blit(ch_surf, ch_rect)
        cur_x += ch_rect.width + spacing
    return pygame.Rect(start_x, y, total_w, font.get_linesize())

def draw_cyber_rect(surf, rect, color, alpha=255, cut_size=10, border_width=0, fill=True):
    # 如果rect是tuple，转为Rect对象
    if isinstance(rect, tuple):
        x, y, w, h = rect
    else:
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
    
    # 确保尺寸为整数且大于0
    w = int(max(1, w))
    h = int(max(1, h))
    x = int(x)
    y = int(y)
        
    points = [(x + cut_size, y), (x + w, y), (x + w, y + h - cut_size), (x + w - cut_size, y + h), (x, y + h), (x, y + cut_size)]
    if surf is None:
        log_debug("draw_cyber_rect: surf is None, skipping draw")
        return
    if fill:
        try:
            # 优化：只创建必要大小的Surface
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            if len(color) == 4: draw_color = color
            else: draw_color = (*color, alpha)
            # 坐标转换为相对坐标
            local_points = [(p[0]-x, p[1]-y) for p in points]
            pygame.draw.polygon(s, draw_color, local_points)
            surf.blit(s, (x, y))
        except Exception as e:
            log_error(f"draw_cyber_rect fill error: {e}, w={w}, h={h}")
            
    if border_width > 0:
        try:
            pygame.draw.polygon(surf, color, points, border_width)
        except Exception as e:
            log_error(f"draw_cyber_rect border error: {e}")

def draw_modern_bar(surf, x, y, pct, color, w=200, h=15, label=None, show_bg=True):
    pct = max(0, min(pct, 100))
    if show_bg:
        bg_points = [(x, y+h), (x+w, y+h), (x+w+h/2, y), (x+h/2, y)]
        # 优化：只创建必要大小的Surface
        min_x = x
        min_y = y
        max_x = x + w + h/2
        max_y = y + h
        surf_w = int(max_x - min_x + 1)
        surf_h = int(max_y - min_y + 1)
        
        s = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        local_points = [(p[0]-min_x, p[1]-min_y) for p in bg_points]
        
        pygame.draw.polygon(s, (20, 20, 30, 150), local_points)
        surf.blit(s, (min_x, min_y))
        pygame.draw.polygon(surf, (100, 100, 100), bg_points, 1)
    fill_w = int((pct / 100) * w)
    if fill_w > 0:
        fill_points = [(x, y+h), (x+fill_w, y+h), (x+fill_w+h/2, y), (x+h/2, y)]
        pygame.draw.polygon(surf, color, fill_points)
        highlight_points = [(x+h/2, y), (x+fill_w+h/2, y), (x+fill_w+h/2, y+2), (x+h/2+2, y+2)]
        pygame.draw.polygon(surf, (255, 255, 255, 100), highlight_points)
    if label:
        draw_text(surf, label, 14, x + w + h + 5, y, WHITE, align="left", shadow=True)


def draw_slanted_bar(surf, x, y, w, h, pct, color, bg_color=(30,30,40), tilt=10, border_color=None, border_width=1):
    """Draw a slanted/parallelogram progress bar slanted to the right by 'tilt' pixels."""
    # Clamp pct
    pct = max(0, min(pct, 100))
    # Background polygon (top shifted right by tilt)
    points_bg = [(x + tilt, y), (x + w + tilt, y), (x + w, y + h), (x, y + h)]
    s = pygame.Surface((w + tilt + 4, h + 4), pygame.SRCALPHA)
    # Draw background (solid rect as polygon)
    pygame.draw.polygon(s, (*bg_color, 220), [(p[0]-x, p[1]-y) for p in points_bg])
    # Fill amount
    fill_w = int((pct / 100.0) * w)
    if fill_w > 0:
        points_fill = [(x + tilt, y), (x + tilt + fill_w, y), (x + fill_w, y + h), (x, y + h)]
        pygame.draw.polygon(s, (*color, 255), [(p[0]-x, p[1]-y) for p in points_fill])
    # Blit back
    surf.blit(s, (x, y), special_flags=pygame.BLEND_RGBA_ADD)
    if border_color and border_width > 0:
        pygame.draw.polygon(surf, border_color, points_bg, border_width)
    return points_bg


def draw_rounded_rect_with_gradient(surf, rect, start_color, end_color, radius=4, border_color=None, border_width=1, alpha=200):
    """Draw a rounded rectangle with a vertical gradient and optional border.
    rect can be tuple or pygame.Rect. start_color and end_color are RGB tuples or RGBA.
    """
    if isinstance(rect, tuple):
        x, y, w, h = rect
    else:
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
    # Create a surface for gradient fill
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    # Ensure colors are 4-tuples
    def to_rgba(c):
        if len(c) == 3: return (c[0], c[1], c[2], alpha)
        return c
    s_col = to_rgba(start_color)
    e_col = to_rgba(end_color)
    for i in range(h):
        t = i / float(max(1, h-1))
        r = int(s_col[0] + (e_col[0] - s_col[0]) * t)
        gcol = int(s_col[1] + (e_col[1] - s_col[1]) * t)
        b = int(s_col[2] + (e_col[2] - s_col[2]) * t)
        a = int(s_col[3] + (e_col[3] - s_col[3]) * t)
        pygame.draw.line(g, (r, gcol, b, a), (0, i), (w, i))
    # draw rounded rect mask by drawing rect on mask and blitting
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255,255,255,255), (0,0,w,h), border_radius=radius)
    g.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(g, (x, y))
    if border_color and border_width > 0:
        pygame.draw.rect(surf, border_color, (x, y, w, h), border_width, border_radius=radius)


def draw_scanline_overlay(surf, rect, spacing=6, color=(255,255,255,8)):
    """Draw subtle horizontal scanlines inside rect to simulate HUD scanning."""
    if isinstance(rect, tuple):
        x, y, w, h = rect
    else:
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(0, h, spacing):
        pygame.draw.line(s, color, (0, i), (w, i))
    surf.blit(s, (x, y), special_flags=pygame.BLEND_RGBA_ADD)


def draw_badge(surf, center_x, center_y, diameter, color, text=None, text_color=WHITE, font_size=9):
    """Draw a circular badge with a short label inside."""
    s = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.circle(s, color, (diameter//2, diameter//2), diameter//2)
    surf.blit(s, (center_x - diameter//2, center_y - diameter//2))
    if text:
        draw_text(surf, text, font_size, center_x, center_y - font_size//2, text_color, align="center", shadow=False)

# ==============================================================================
#   素材生成工具
# ==============================================================================
_plane_cache = {}

def get_plane_surf(pid, visual=None, static=False):
    cache_key = None
    if static:
        vis_key = None
        if visual:
            # 将visual字典转换为可哈希的元组，处理列表/字典嵌套
            try:
                items = []
                for k, v in sorted(visual.items()):
                    if isinstance(v, list):
                        items.append((k, tuple(v)))
                    elif isinstance(v, dict):
                        # 简单处理一层嵌套字典
                        sub_items = tuple(sorted(v.items()))
                        items.append((k, sub_items))
                    else:
                        items.append((k, v))
                vis_key = tuple(items)
            except Exception:
                vis_key = str(visual) # Fallback
        
        cache_key = (pid, vis_key)
        if cache_key in _plane_cache:
            return _plane_cache[cache_key]

    try:
        s = _generate_plane_surf(pid, visual, static)
    except Exception as e:
        log_error(f"Error generating plane surf for {pid}: {e}")
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 0, 0), (60, 60), 30) # Error placeholder
    
    if static and cache_key:
        _plane_cache[cache_key] = s
    return s

def _generate_plane_surf(pid, visual=None, static=False):
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = CYBER_CYAN  # 默认颜色
    edge_color = CYBER_CYAN_BRIGHT  # 默认边框颜色
    # 应用视觉覆盖
    if visual:
        c = visual.get('neon_color', c)
        edge_color = visual.get('accent_color', edge_color)
        # 背景发光
        glow_color = visual.get('neon_color', c)
        glow_surf = pygame.Surface((140, 140), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*glow_color, 30), (70, 70), 60)
        s.blit(glow_surf, (-10, -10))
    
    # 获取时间脉冲值用于动画
    if static:
        t = 0
        pulse = 0
    else:
        t = pygame.time.get_ticks() / 1000.0
        pulse = abs(math.sin(t * 3))
    
    # 检查是否有模型样式覆盖 (专属改装)
    model_style = visual.get('model_style') if visual else None
    
    if model_style == "striker_mk2":
        # 绯红之刃·改：更尖锐的造型，双翼展开
        pygame.draw.polygon(s, (80, 0, 0), [(60, 0), (120, 100), (60, 80), (0, 100)])
        pygame.draw.polygon(s, c, [(60, 5), (115, 95), (60, 75), (5, 95)])
        pygame.draw.polygon(s, edge_color, [(60, 5), (115, 95), (60, 75), (5, 95)], 2)
        # 额外的能量翼
        wing_pulse = int(10 * pulse)
        pygame.draw.line(s, (255, 100, 100), (60, 40), (10 - wing_pulse, 80), 3)
        pygame.draw.line(s, (255, 100, 100), (60, 40), (110 + wing_pulse, 80), 3)
        return s
        
    elif model_style == "phantom_mk2":
        # 虚空行者：破碎的几何体，半透明
        # 绘制多个浮动的碎片
        center_alpha = 150 + int(100 * pulse)
        pygame.draw.circle(s, (*c[:3], center_alpha), (60, 60), 20)
        pygame.draw.circle(s, edge_color, (60, 60), 20, 2)
        
        # 环绕的碎片
        for i in range(4):
            angle = t * 3 + (i * math.pi / 2)
            dist = 35 + 5 * math.sin(t * 5)
            px = 60 + math.cos(angle) * dist
            py = 60 + math.sin(angle) * dist
            pygame.draw.polygon(s, c, [(px, py-5), (px+5, py), (px, py+5), (px-5, py)])
        return s

    elif model_style == "titan_mk2":
        # 移动要塞：巨大的正方形结构，厚重
        pygame.draw.rect(s, (50, 30, 10), (10, 10, 100, 100))
        pygame.draw.rect(s, c, (15, 15, 90, 90))
        pygame.draw.rect(s, edge_color, (15, 15, 90, 90), 4)
        # 反应堆核心
        core_pulse = int(20 * pulse)
        pygame.draw.circle(s, (255, 100, 0), (60, 60), 15 + core_pulse // 4)
        pygame.draw.line(s, (255, 200, 0), (15, 15), (105, 105), 2)
        pygame.draw.line(s, (255, 200, 0), (105, 15), (15, 105), 2)
        return s

    elif model_style == "thunderbird_mk2":
        # 风暴领主：闪电形状的机翼
        points = [(60, 0), (90, 40), (120, 30), (100, 70), (120, 100), (60, 80), (0, 100), (20, 70), (0, 30), (30, 40)]
        pygame.draw.polygon(s, (100, 100, 0), points)
        # 简单的缩放点
        inner_points = []
        for p in points:
            dx = p[0] - 60
            dy = p[1] - 60
            inner_points.append((60 + dx * 0.8, 60 + dy * 0.8))
            
        pygame.draw.polygon(s, c, inner_points)
        pygame.draw.lines(s, edge_color, True, points, 2)
        # 电弧效果
        if random.random() < 0.3:
            start_p = random.choice(points)
            end_p = random.choice(points)
            pygame.draw.line(s, (255, 255, 255), start_p, end_p, 2)
        return s

    elif model_style == "viper_mk2":
        # 九头蛇·毒液：生物质感，多头结构
        # 主体
        pygame.draw.ellipse(s, (20, 80, 20), (40, 20, 40, 80))
        pygame.draw.ellipse(s, c, (45, 25, 30, 70))
        # 头部
        head_y = 20 + int(5 * math.sin(t * 4))
        pygame.draw.circle(s, edge_color, (60, head_y), 15)
        # 侧翼（像蛇头）
        for i in [-1, 1]:
            offset_x = i * 30
            offset_y = 40 + int(5 * math.sin(t * 4 + i))
            pygame.draw.circle(s, (50, 150, 50), (60 + offset_x, offset_y), 10)
            pygame.draw.line(s, (20, 80, 20), (60, 60), (60 + offset_x, offset_y), 5)
        return s

    elif model_style == "specter_mk2":
        # 死神之镰：巨大的镰刀形状
        # 刀柄
        pygame.draw.line(s, (50, 50, 50), (60, 100), (60, 20), 4)
        # 刀刃
        blade_points = [(60, 20), (100, 10), (110, 40), (80, 60), (60, 40)]
        pygame.draw.polygon(s, (150, 150, 150), blade_points)
        pygame.draw.polygon(s, c, blade_points, 2)
        # 幽灵光环
        glow_alpha = 100 + int(50 * pulse)
        pygame.draw.circle(s, (*c[:3], glow_alpha), (60, 40), 30, 2)
        return s

    elif model_style == "aurora_mk2":
        # 星辰女神：光环结构
        # 中心核心
        pygame.draw.circle(s, (255, 255, 255), (60, 60), 15)
        # 旋转光环
        for i in range(3):
            radius = 30 + i * 10
            angle_offset = t * (i + 1)
            arc_rect = (60 - radius, 60 - radius, radius * 2, radius * 2)
            pygame.draw.arc(s, c, arc_rect, angle_offset, angle_offset + math.pi, 2)
        # 粒子
        for i in range(4):
            px = 60 + math.cos(t * 2 + i * math.pi / 2) * 40
            py = 60 + math.sin(t * 2 + i * math.pi / 2) * 40
            pygame.draw.circle(s, edge_color, (int(px), int(py)), 4)
        return s

    elif model_style == "crimson_mk2":
        # 血魔领主：尖刺结构
        # 主体
        pygame.draw.polygon(s, (100, 0, 0), [(60, 10), (90, 40), (60, 100), (30, 40)])
        # 尖刺
        spike_len = 10 + 5 * pulse
        pygame.draw.line(s, edge_color, (30, 40), (30 - spike_len, 30), 3)
        pygame.draw.line(s, edge_color, (90, 40), (90 + spike_len, 30), 3)
        pygame.draw.line(s, edge_color, (60, 100), (60, 110 + spike_len), 3)
        # 血槽
        pygame.draw.line(s, (255, 0, 0), (60, 20), (60, 90), 2)
        return s

    elif model_style == "stalker_mk2":
        # 虚空猎手：昆虫/异形结构
        # 身体
        pygame.draw.ellipse(s, (50, 0, 100), (45, 30, 30, 60))
        # 腿/触须
        for i in range(3):
            y_off = i * 15
            leg_len = 20 + 5 * math.sin(t * 10 + i)
            pygame.draw.line(s, c, (45, 40 + y_off), (45 - leg_len, 50 + y_off), 2)
            pygame.draw.line(s, c, (75, 40 + y_off), (75 + leg_len, 50 + y_off), 2)
        # 复眼
        pygame.draw.circle(s, (0, 255, 0), (55, 35), 3)
        pygame.draw.circle(s, (0, 255, 0), (65, 35), 3)
        return s

    elif model_style == "gaia_mk2":
        # 大地堡垒：水晶簇
        # 绘制多个重叠的菱形水晶
        crystals = [
            ((60, 60), 30, (100, 255, 100)),
            ((40, 70), 20, (50, 200, 50)),
            ((80, 70), 20, (50, 200, 50)),
            ((60, 30), 25, (150, 255, 150))
        ]
        for pos, size, col in crystals:
            pts = [
                (pos[0], pos[1] - size),
                (pos[0] + size * 0.6, pos[1]),
                (pos[0], pos[1] + size),
                (pos[0] - size * 0.6, pos[1])
            ]
            pygame.draw.polygon(s, col, pts)
            pygame.draw.polygon(s, edge_color, pts, 1)
        return s

    elif model_style == "weaver_mk2":
        # 命运编织者：网状结构
        # 节点
        nodes = [(60, 20), (30, 50), (90, 50), (60, 80), (20, 90), (100, 90)]
        for p in nodes:
            pygame.draw.circle(s, c, p, 4)
        # 连线
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                dist = math.hypot(nodes[i][0] - nodes[j][0], nodes[i][1] - nodes[j][1])
                if dist < 60:
                    width = 1
                    if random.random() < 0.1: width = 2 # 闪烁连线
                    pygame.draw.line(s, (200, 200, 200), nodes[i], nodes[j], width)
        return s

    elif model_style == "solar_mk2":
        # 太阳神：旋转的太阳
        # 核心
        pygame.draw.circle(s, (255, 200, 0), (60, 60), 25)
        # 光芒
        num_rays = 12
        for i in range(num_rays):
            angle = t + i * (2 * math.pi / num_rays)
            ray_len = 40 + 10 * math.sin(t * 5)
            end_x = 60 + math.cos(angle) * ray_len
            end_y = 60 + math.sin(angle) * ray_len
            pygame.draw.line(s, (255, 100, 0), (60, 60), (end_x, end_y), 3)
        return s

    elif model_style == "arbiter_mk2":
        # 真理裁决：完美的几何体
        # 旋转的正方形
        angle = t * 2
        size = 40
        pts = []
        for i in range(4):
            a = angle + i * (math.pi / 2)
            pts.append((60 + math.cos(a) * size, 60 + math.sin(a) * size))
        pygame.draw.polygon(s, c, pts, 2)
        # 内部三角形
        angle2 = -t * 3
        size2 = 20
        pts2 = []
        for i in range(3):
            a = angle2 + i * (2 * math.pi / 3)
            pts2.append((60 + math.cos(a) * size2, 60 + math.sin(a) * size2))
        pygame.draw.polygon(s, edge_color, pts2)
        return s

    elif model_style == "eclipse_mk2":
        # 永夜之蚀：日食效果
        # 黑色圆
        pygame.draw.circle(s, (0, 0, 0), (60, 60), 30)
        # 光晕
        pygame.draw.circle(s, (100, 50, 150), (60, 60), 32, 2)
        # 阴影遮挡
        offset = 10 * math.sin(t)
        pygame.draw.circle(s, (20, 0, 40), (60 + offset, 60), 25)
        return s

    elif model_style == "prism_mk2":
        # 水晶棱镜：透明三角
        pts = [(60, 20), (100, 90), (20, 90)]
        # 填充半透明
        s2 = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(s2, (*c[:3], 100), pts)
        s.blit(s2, (0, 0))
        # 边框
        pygame.draw.polygon(s, (255, 255, 255), pts, 2)
        # 折射光
        pygame.draw.line(s, (255, 255, 255), (60, 20), (60, 90), 1)
        return s

    elif model_style == "necro_mk2":
        # 巫妖王：骷髅头形状
        # 头骨
        pygame.draw.ellipse(s, (200, 200, 200), (40, 30, 40, 50))
        # 眼睛
        eye_color = (0, 255, 0)
        pygame.draw.circle(s, eye_color, (50, 45), 4)
        pygame.draw.circle(s, eye_color, (70, 45), 4)
        # 牙齿
        for i in range(3):
            x = 50 + i * 10
            pygame.draw.line(s, (150, 150, 150), (x, 70), (x, 80), 2)
        return s

    # ==================== Striker 专属涂装形态 ====================
    elif model_style == "mech_wings":
        # 机械飞升：纳米机械装甲，悬浮零件
        # 主机身 - 机械装甲板
        pygame.draw.polygon(s, (60, 60, 80), [(60, 10), (90, 90), (60, 85), (30, 90)])
        pygame.draw.polygon(s, c, [(60, 15), (85, 85), (60, 80), (35, 85)])
        
        # 悬浮机械零件
        gear_radius = 5 + int(3 * pulse)
        for i in range(4):
            angle = t * 2 + i * math.pi / 2
            gx = 60 + math.cos(angle) * 35
            gy = 50 + math.sin(angle) * 35
            pygame.draw.circle(s, (0, 255, 255), (int(gx), int(gy)), gear_radius)
            pygame.draw.circle(s, (255, 200, 0), (int(gx), int(gy)), gear_radius - 2)
        
        # 双涡轮推进器
        turbo_pulse = int(5 * pulse)
        pygame.draw.circle(s, (0, 200, 255), (40, 80), 8 + turbo_pulse)
        pygame.draw.circle(s, (0, 200, 255), (80, 80), 8 + turbo_pulse)
        pygame.draw.circle(s, (255, 255, 255), (40, 80), 4)
        pygame.draw.circle(s, (255, 255, 255), (80, 80), 4)
        
        # 机械关节连线
        pygame.draw.line(s, (100, 255, 255), (60, 40), (40, 80), 2)
        pygame.draw.line(s, (100, 255, 255), (60, 40), (80, 80), 2)
        return s

    elif model_style == "phase_shift":
        # 暗影相位：半透明，相位扭曲，暗影分身
        # 主体半透明
        s2 = pygame.Surface((120, 120), pygame.SRCALPHA)
        main_alpha = 120 + int(50 * pulse)
        pygame.draw.polygon(s2, (*c[:3], main_alpha), [(60, 10), (90, 90), (60, 85), (30, 90)])
        s.blit(s2, (0, 0))
        
        # 相位扭曲效果 - 多层分身
        for i in range(3):
            offset_x = int(10 * math.sin(t * 3 + i))
            offset_y = int(5 * math.cos(t * 3 + i))
            alpha = 40 - i * 10
            s3 = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(s3, (80, 80, 150, alpha), 
                              [(60 + offset_x, 10 + offset_y), 
                               (90 + offset_x, 90 + offset_y), 
                               (60 + offset_x, 85 + offset_y), 
                               (30 + offset_x, 90 + offset_y)])
            s.blit(s3, (0, 0))
        
        # 空间裂缝纹理
        for i in range(5):
            y = 20 + i * 15
            x_offset = int(5 * math.sin(t * 4 + i))
            pygame.draw.line(s, (150, 150, 200), (40 + x_offset, y), (80 - x_offset, y), 1)
        return s

    elif model_style == "critical_mass":
        # 核心熔毁：反应堆过载，岩浆裂痕，爆炸火花
        # 主体机身
        pygame.draw.polygon(s, (100, 50, 0), [(60, 10), (90, 90), (60, 85), (30, 90)])
        
        # 核心反应堆（脉动）
        core_size = 15 + int(8 * pulse)
        pygame.draw.circle(s, (255, 200, 0), (60, 50), core_size)
        pygame.draw.circle(s, (255, 100, 0), (60, 50), core_size - 5)
        pygame.draw.circle(s, (255, 50, 0), (60, 50), core_size - 10)
        
        # 裂痕系统 - 岩浆流淌
        crack_lines = [
            [(60, 50), (40, 30), (30, 40)],
            [(60, 50), (80, 30), (90, 40)],
            [(60, 50), (50, 70), (40, 85)],
            [(60, 50), (70, 70), (80, 85)]
        ]
        for crack in crack_lines:
            pygame.draw.lines(s, (255, 255, 0), False, crack, 2)
            pygame.draw.lines(s, (255, 150, 0), False, crack, 1)
        
        # 爆炸火花粒子
        if random.random() < 0.5:
            for i in range(3):
                spark_x = 60 + random.randint(-20, 20)
                spark_y = 50 + random.randint(-20, 20)
                spark_size = random.randint(2, 4)
                pygame.draw.circle(s, (255, 255, 100), (spark_x, spark_y), spark_size)
        
        # 能量波纹扩散
        wave_radius = int(30 + 15 * pulse)
        pygame.draw.circle(s, (255, 100, 0), (60, 50), wave_radius, 2)
        return s

    elif model_style == "quantum_flux":
        # 量子纠缠：薛定谔之翼，量子叠加态
        # 基础形态
        base_points = [(60, 10), (90, 90), (60, 85), (30, 90)]
        
        # 量子叠加 - 同时存在多个位置
        for i in range(5):
            phase_offset = t * 5 + i * 0.4
            offset_x = int(15 * math.sin(phase_offset))
            offset_y = int(10 * math.cos(phase_offset * 1.3))
            alpha = 60 - i * 10
            
            s4 = pygame.Surface((120, 120), pygame.SRCALPHA)
            shifted_points = [(p[0] + offset_x, p[1] + offset_y) for p in base_points]
            pygame.draw.polygon(s4, (*c[:3], alpha), shifted_points)
            s.blit(s4, (0, 0))
        
        # 量子纠缠连线
        for i in range(4):
            angle = t * 4 + i * math.pi / 2
            qx = 60 + math.cos(angle) * 40
            qy = 50 + math.sin(angle) * 30
            pygame.draw.line(s, (150, 255, 255), (60, 50), (int(qx), int(qy)), 1)
            pygame.draw.circle(s, (255, 150, 255), (int(qx), int(qy)), 3)
        
        # 粒子风暴
        for i in range(8):
            storm_angle = t * 10 + i * math.pi / 4
            storm_dist = 25 + 10 * math.sin(t * 8 + i)
            sx = 60 + math.cos(storm_angle) * storm_dist
            sy = 50 + math.sin(storm_angle) * storm_dist
            pygame.draw.circle(s, (200, 220, 255), (int(sx), int(sy)), 2)
        return s

    elif model_style == "seraph_wings":
        # 天使降临：神圣羽翼，光之使者，圣光柱
        # 主体机身
        pygame.draw.polygon(s, (200, 200, 150), [(60, 15), (80, 85), (60, 80), (40, 85)])
        
        # 天使光环
        halo_pulse = 25 + int(5 * pulse)
        pygame.draw.circle(s, (255, 255, 220), (60, 20), halo_pulse, 3)
        pygame.draw.circle(s, (255, 255, 255), (60, 20), halo_pulse - 5, 2)
        
        # 神圣羽翼展开（六翼）
        wing_colors = [(255, 255, 230), (255, 250, 220), (255, 245, 210)]
        for layer in range(3):
            wing_offset = 30 + layer * 10
            wing_y = 40 + layer * 5
            # 左翼
            left_wing = [(40, wing_y), (10, wing_y - 10), (5, wing_y + 15), (30, wing_y + 10)]
            pygame.draw.polygon(s, wing_colors[layer], left_wing)
            pygame.draw.polygon(s, (255, 255, 255), left_wing, 1)
            # 右翼
            right_wing = [(80, wing_y), (110, wing_y - 10), (115, wing_y + 15), (90, wing_y + 10)]
            pygame.draw.polygon(s, wing_colors[layer], right_wing)
            pygame.draw.polygon(s, (255, 255, 255), right_wing, 1)
        
        # 圣光柱（垂直光束）
        beam_alpha = 100 + int(50 * pulse)
        s5 = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(s5, (255, 255, 255, beam_alpha), (55, 0, 10, 120))
        s.blit(s5, (0, 0))
        
        # 光之粒子环绕
        for i in range(6):
            particle_angle = t * 3 + i * math.pi / 3
            px = 60 + math.cos(particle_angle) * 35
            py = 50 + math.sin(particle_angle) * 35
            pygame.draw.circle(s, (255, 255, 200), (int(px), int(py)), 3)
        return s

    elif model_style == "eastern_dragon":
        # 赤龙之怒：东方神龙，龙鳞，龙首机头，龙爪机翼
        # 龙身主体（蛇形）
        dragon_body = []
        for i in range(8):
            segment_y = 15 + i * 10
            segment_x = 60 + int(8 * math.sin(t * 3 + i * 0.5))
            dragon_body.append((segment_x, segment_y))
        
        # 绘制龙身
        for i in range(len(dragon_body) - 1):
            width = 20 - i * 2
            pygame.draw.line(s, (220, 0, 0), dragon_body[i], dragon_body[i + 1], width)
            pygame.draw.line(s, (255, 215, 0), dragon_body[i], dragon_body[i + 1], width - 4)
        
        # 龙首机头
        head_x, head_y = dragon_body[0]
        # 龙头轮廓
        dragon_head = [(head_x, head_y - 10), (head_x - 12, head_y), (head_x - 8, head_y + 8), 
                      (head_x, head_y + 5), (head_x + 8, head_y + 8), (head_x + 12, head_y)]
        pygame.draw.polygon(s, (200, 0, 0), dragon_head)
        pygame.draw.polygon(s, (255, 215, 0), dragon_head, 2)
        
        # 龙角
        pygame.draw.line(s, (255, 215, 0), (head_x - 8, head_y - 5), (head_x - 15, head_y - 15), 3)
        pygame.draw.line(s, (255, 215, 0), (head_x + 8, head_y - 5), (head_x + 15, head_y - 15), 3)
        
        # 龙眼
        pygame.draw.circle(s, (255, 255, 0), (head_x - 5, head_y - 3), 3)
        pygame.draw.circle(s, (255, 255, 0), (head_x + 5, head_y - 3), 3)
        pygame.draw.circle(s, (255, 0, 0), (head_x - 5, head_y - 3), 1)
        pygame.draw.circle(s, (255, 0, 0), (head_x + 5, head_y - 3), 1)
        
        # 龙爪机翼
        mid_x, mid_y = dragon_body[3]
        # 左爪
        claw_left = [(mid_x - 10, mid_y), (mid_x - 25, mid_y - 10), (mid_x - 30, mid_y - 5)]
        pygame.draw.lines(s, (255, 215, 0), False, claw_left, 3)
        for i in range(3):
            pygame.draw.line(s, (255, 215, 0), (mid_x - 30, mid_y - 5 + i * 3), 
                           (mid_x - 35, mid_y - 5 + i * 3), 2)
        # 右爪
        claw_right = [(mid_x + 10, mid_y), (mid_x + 25, mid_y - 10), (mid_x + 30, mid_y - 5)]
        pygame.draw.lines(s, (255, 215, 0), False, claw_right, 3)
        for i in range(3):
            pygame.draw.line(s, (255, 215, 0), (mid_x + 30, mid_y - 5 + i * 3), 
                           (mid_x + 35, mid_y - 5 + i * 3), 2)
        
        # 金色龙鳞纹理
        for i in range(1, len(dragon_body) - 1):
            scale_x, scale_y = dragon_body[i]
            pygame.draw.circle(s, (255, 215, 0), (scale_x - 6, scale_y), 2)
            pygame.draw.circle(s, (255, 215, 0), (scale_x + 6, scale_y), 2)
        return s

    elif model_style == "energy_blade":
        # 无尽锋刃：能量光剑，刀刃机翼，等离子刃光
        # 剑柄核心
        pygame.draw.rect(s, (100, 100, 150), (55, 40, 10, 30))
        pygame.draw.circle(s, (0, 255, 255), (60, 55), 8)
        
        # 能量刀身（主体变成光剑）
        blade_glow = int(5 * pulse)
        blade_points = [(60, 10), (65 + blade_glow, 15), (68, 85), (60, 95), (52, 85), (55 - blade_glow, 15)]
        
        # 多层光剑效果
        s6 = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(s6, (0, 255, 255, 100), blade_points)
        s.blit(s6, (0, 0))
        
        pygame.draw.polygon(s, (100, 255, 255), blade_points, 3)
        pygame.draw.polygon(s, (255, 255, 255), [(60, 15), (63, 20), (63, 90), (60, 90), (57, 90), (57, 20)])
        
        # 刀刃机翼（能量刀刃）
        # 左刃翼
        left_blade = [(60, 45), (20, 35), (15, 50), (40, 60)]
        s7 = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(s7, (0, 255, 255, 150), left_blade)
        s.blit(s7, (0, 0))
        pygame.draw.polygon(s, (150, 200, 255), left_blade, 2)
        
        # 右刃翼
        right_blade = [(60, 45), (100, 35), (105, 50), (80, 60)]
        s8 = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(s8, (255, 0, 255, 150), right_blade)
        s.blit(s8, (0, 0))
        pygame.draw.polygon(s, (255, 150, 255), right_blade, 2)
        
        # 闪电链连接
        if random.random() < 0.4:
            for i in range(2):
                lx = random.randint(40, 80)
                ly = random.randint(20, 80)
                pygame.draw.line(s, (255, 255, 255), (60, 55), (lx, ly), 1)
        
        # 等离子刃光粒子
        for i in range(6):
            blade_angle = t * 8 + i * math.pi / 3
            blade_dist = 30 + 5 * math.sin(t * 10 + i)
            bx = 60 + math.cos(blade_angle) * blade_dist
            by = 50 + math.sin(blade_angle) * blade_dist
            pygame.draw.circle(s, (150, 200, 255), (int(bx), int(by)), 2)
        return s

    # --- Striker MK3/MK4 ---
    elif model_style == "striker_heavy":
        # 重装突击：厚重的装甲板
        pygame.draw.rect(s, (100, 50, 50), (40, 20, 40, 80))
        pygame.draw.rect(s, (150, 80, 80), (30, 40, 60, 40))
        pygame.draw.rect(s, c, (45, 25, 30, 70))
        # 铆钉
        for y in range(30, 100, 20):
            pygame.draw.circle(s, (200, 200, 200), (42, y), 2)
            pygame.draw.circle(s, (200, 200, 200), (78, y), 2)
        return s

    elif model_style == "striker_speed":
        # 极速锋刃：细长的针状机体
        pygame.draw.polygon(s, c, [(60, 0), (70, 100), (60, 90), (50, 100)])
        pygame.draw.line(s, (255, 255, 255), (60, 0), (60, 100), 2)
        # 侧翼
        pygame.draw.polygon(s, edge_color, [(60, 40), (90, 80), (60, 70)])
        pygame.draw.polygon(s, edge_color, [(60, 40), (30, 80), (60, 70)])
        return s

    # ==================== Phantom 专属涂装形态 ====================
    elif model_style == "void_walker":
        # 虚空行者：星云纹理，虚空裂痕，黑洞效果
        # 黑洞核心
        void_center = (60, 50)
        for i in range(5):
            radius = 35 - i * 6
            alpha = 50 + i * 20
            void_color = (120 - i * 20, 0, 220 - i * 30, alpha)
            s_void = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(s_void, void_color, void_center, radius)
            s.blit(s_void, (0, 0))
        
        # 星云流动纹理
        for i in range(8):
            angle = t * 2 + i * math.pi / 4
            dist = 40 + 10 * math.sin(t * 3 + i)
            nx = 60 + math.cos(angle) * dist
            ny = 50 + math.sin(angle) * dist
            nebula_size = 8 + int(4 * math.sin(t * 5 + i))
            s_nebula = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(s_nebula, (200, 100, 255, 80), (int(nx), int(ny)), nebula_size)
            s.blit(s_nebula, (0, 0))
        
        # 虚空裂痕
        crack_points = [
            [(40, 30), (35, 40), (30, 50)],
            [(80, 30), (85, 40), (90, 50)],
            [(50, 70), (45, 80), (40, 90)],
            [(70, 70), (75, 80), (80, 90)]
        ]
        for crack in crack_points:
            for i in range(len(crack) - 1):
                pygame.draw.line(s, (140, 50, 200), crack[i], crack[i + 1], 2)
                # 裂痕发光
                s_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(s_glow, (200, 100, 255, 100), crack[i], crack[i + 1], 4)
                s.blit(s_glow, (0, 0))
        
        # 虚空粒子旋涡
        for i in range(12):
            spiral_angle = t * 4 + i * math.pi / 6
            spiral_dist = 25 + i * 2
            vx = 60 + math.cos(spiral_angle) * spiral_dist
            vy = 50 + math.sin(spiral_angle) * spiral_dist
            pygame.draw.circle(s, (140, 50, 200), (int(vx), int(vy)), 2)
        return s

    elif model_style == "multi_ghost":
        # 千幻魔影：多层幽灵分身，魂火粒子，灵魂锁链
        base_shape = [(60, 15), (85, 85), (60, 75), (35, 85)]
        
        # 6层幽灵分身（渐变透明）
        for i in range(6):
            offset_angle = t * 2 + i * math.pi / 3
            offset_x = int(15 * math.cos(offset_angle))
            offset_y = int(10 * math.sin(offset_angle))
            alpha = 120 - i * 15
            
            ghost_shape = [(p[0] + offset_x, p[1] + offset_y) for p in base_shape]
            s_ghost = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(s_ghost, (200, 200, 255, alpha), ghost_shape)
            s.blit(s_ghost, (0, 0))
            
            # 幽灵轮廓
            pygame.draw.polygon(s, (240, 240, 255), ghost_shape, 1)
        
        # 魂火粒子浮游
        for i in range(8):
            soul_angle = t * 3 + i * math.pi / 4
            soul_dist = 35 + 5 * math.sin(t * 6 + i)
            soul_x = 60 + math.cos(soul_angle) * soul_dist
            soul_y = 50 + math.sin(soul_angle) * soul_dist
            # 魂火效果
            fire_size = 4 + int(2 * pulse)
            pygame.draw.circle(s, (180, 180, 255), (int(soul_x), int(soul_y)), fire_size)
            pygame.draw.circle(s, (220, 220, 255), (int(soul_x), int(soul_y)), fire_size - 2)
        
        # 灵魂锁链缠绕
        chain_points = []
        for i in range(8):
            chain_angle = t * 4 + i * math.pi / 4
            cx = 60 + math.cos(chain_angle) * 30
            cy = 50 + math.sin(chain_angle) * 30
            chain_points.append((int(cx), int(cy)))
        
        for i in range(len(chain_points)):
            next_i = (i + 1) % len(chain_points)
            pygame.draw.line(s, (180, 180, 240), chain_points[i], chain_points[next_i], 1)
        return s

    elif model_style == "kaleidoscope":
        # 万花筒分形：镜像对称，钻石粒子，无限反射
        # 中心水晶
        pygame.draw.circle(s, (240, 240, 240), (60, 50), 15)
        pygame.draw.circle(s, (255, 255, 255), (60, 50), 12)
        
        # 万花筒对称图案（6重对称）
        for sym in range(6):
            base_angle = t + sym * math.pi / 3
            
            # 镜面碎片
            for i in range(3):
                angle = base_angle + i * 0.3
                dist = 25 + i * 8
                mx = 60 + math.cos(angle) * dist
                my = 50 + math.sin(angle) * dist
                
                # 绘制镜面碎片（菱形）
                mirror_size = 8 - i * 2
                mirror_points = [
                    (mx, my - mirror_size),
                    (mx + mirror_size * 0.6, my),
                    (mx, my + mirror_size),
                    (mx - mirror_size * 0.6, my)
                ]
                
                # 彩虹色渐变
                hue = (sym * 60 + i * 30) % 360
                mirror_color = pygame.Color(0)
                mirror_color.hsva = (hue, 80, 100, 100)
                
                s_mirror = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.polygon(s_mirror, (*mirror_color[:3], 150), mirror_points)
                s.blit(s_mirror, (0, 0))
                pygame.draw.polygon(s, (255, 255, 255), mirror_points, 1)
        
        # 钻石粒子漩涡
        for i in range(16):
            diamond_angle = -t * 5 + i * math.pi / 8
            diamond_dist = 35 + 5 * math.sin(t * 8 + i)
            dx = 60 + math.cos(diamond_angle) * diamond_dist
            dy = 50 + math.sin(diamond_angle) * diamond_dist
            
            # 钻石形粒子
            d_size = 3
            d_points = [(dx, dy - d_size), (dx + d_size, dy), (dx, dy + d_size), (dx - d_size, dy)]
            pygame.draw.polygon(s, (220, 220, 250), d_points)
        return s

    elif model_style == "eldritch_horror":
        # 深渊恐惧：扭曲触手，黑雾，恐惧之眼
        # 主体（有机生命体）
        body_pulse = int(5 * pulse)
        pygame.draw.ellipse(s, (100, 0, 140), (40 - body_pulse, 30, 40 + body_pulse * 2, 50))
        pygame.draw.ellipse(s, (120, 0, 160), (45, 35, 30, 40))
        
        # 扭曲触手（8条）
        for i in range(8):
            tentacle_angle = t * 2 + i * math.pi / 4
            tentacle_length = 35 + 10 * math.sin(t * 5 + i)
            
            # 触手由多段组成
            tentacle_segments = []
            for seg in range(5):
                seg_angle = tentacle_angle + seg * 0.2 * math.sin(t * 3)
                seg_dist = (seg + 1) * tentacle_length / 5
                tx = 60 + math.cos(seg_angle) * seg_dist
                ty = 50 + math.sin(seg_angle) * seg_dist
                tentacle_segments.append((int(tx), int(ty)))
            
            # 绘制触手
            if len(tentacle_segments) > 1:
                pygame.draw.lines(s, (170, 0, 170), False, tentacle_segments, 3)
                pygame.draw.lines(s, (120, 0, 160), False, tentacle_segments, 1)
                
                # 触手末端吸盘
                end_x, end_y = tentacle_segments[-1]
                pygame.draw.circle(s, (100, 0, 140), (end_x, end_y), 4)
        
        # 黑雾弥漫效果
        for i in range(6):
            fog_x = 40 + random.randint(0, 40)
            fog_y = 30 + random.randint(0, 50)
            fog_size = random.randint(8, 15)
            s_fog = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(s_fog, (50, 0, 70, 40), (fog_x, fog_y), fog_size)
            s.blit(s_fog, (0, 0))
        
        # 恐惧之眼（多个眼睛）
        eye_positions = [(50, 40), (70, 40), (60, 55)]
        for ex, ey in eye_positions:
            # 眼白
            pygame.draw.ellipse(s, (200, 180, 180), (ex - 5, ey - 3, 10, 6))
            # 瞳孔（跟随时间晃动）
            pupil_offset = int(2 * math.sin(t * 4))
            pygame.draw.circle(s, (255, 0, 0), (ex + pupil_offset, ey), 2)
        return s

    elif model_style == "aurora_borealis":
        # 北极天幕：极光流光，彩色光带，梦幻粒子
        # 主体轮廓
        outline = [(60, 15), (80, 80), (60, 70), (40, 80)]
        
        # 极光布幕（多层彩色波浪）
        aurora_colors = [
            (100, 255, 200),
            (150, 200, 255),
            (255, 100, 255),
            (100, 255, 255)
        ]
        
        for layer in range(4):
            aurora_points = []
            for i in range(10):
                x = 20 + i * 8
                y_offset = 10 * math.sin(t * 2 + i * 0.5 + layer)
                y = 40 + layer * 10 + y_offset
                aurora_points.append((x, y))
            
            # 绘制极光带
            if len(aurora_points) > 1:
                s_aurora = pygame.Surface((120, 120), pygame.SRCALPHA)
                for i in range(len(aurora_points) - 1):
                    pygame.draw.line(s_aurora, (*aurora_colors[layer], 100), 
                                   aurora_points[i], aurora_points[i + 1], 8)
                s.blit(s_aurora, (0, 0))
        
        # 机身融入极光
        s_body = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(s_body, (*c[:3], 150), outline)
        s.blit(s_body, (0, 0))
        
        # 光粒子舞蹈
        for i in range(20):
            particle_angle = t * 3 + i * math.pi / 10
            particle_dist = 30 + 15 * math.sin(t * 4 + i)
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            
            # 彩色粒子
            p_color = aurora_colors[i % 4]
            pygame.draw.circle(s, p_color, (int(px), int(py)), 2)
        
        # 梦幻光晕
        halo_alpha = 80 + int(40 * pulse)
        s_halo = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(s_halo, (150, 220, 255, halo_alpha), (60, 50), 40)
        s.blit(s_halo, (0, 0))
        return s

    elif model_style == "chronos":
        # 时间逆流者：沙漏纹理，时空波纹，过去分身
        # 沙漏机身形状
        hourglass_top = [(40, 20), (80, 20), (60, 50)]
        hourglass_bottom = [(60, 50), (40, 80), (80, 80)]
        
        pygame.draw.polygon(s, (200, 180, 255), hourglass_top)
        pygame.draw.polygon(s, (220, 200, 240), hourglass_bottom)
        pygame.draw.polygon(s, edge_color, hourglass_top, 2)
        pygame.draw.polygon(s, edge_color, hourglass_bottom, 2)
        
        # 沙漏中心瓶颈
        pygame.draw.circle(s, (255, 220, 200), (60, 50), 5)
        
        # 沙粒流动效果
        sand_y = 20 + int(30 * ((t * 2) % 1))
        for i in range(8):
            sand_x = 55 + random.randint(0, 10)
            pygame.draw.circle(s, (255, 220, 200), (sand_x, sand_y + i * 3), 1)
        
        # 时空波纹扩散（同心圆）
        for i in range(4):
            wave_phase = (t * 3 + i * 0.5) % 2
            wave_radius = int(20 + wave_phase * 25)
            wave_alpha = int(150 * (1 - wave_phase / 2))
            s_wave = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(s_wave, (220, 200, 240, wave_alpha), (60, 50), wave_radius, 2)
            s.blit(s_wave, (0, 0))
        
        # 过去的时间分身（时间轴上的残影）
        for i in range(3):
            time_offset = i + 1
            past_alpha = 60 - i * 15
            past_y_offset = int(-15 * math.sin(t * 2 - time_offset))
            
            s_past = pygame.Surface((120, 120), pygame.SRCALPHA)
            past_top = [(p[0], p[1] + past_y_offset) for p in hourglass_top]
            past_bottom = [(p[0], p[1] + past_y_offset) for p in hourglass_bottom]
            pygame.draw.polygon(s_past, (200, 180, 255, past_alpha), past_top)
            pygame.draw.polygon(s_past, (220, 200, 240, past_alpha), past_bottom)
            s.blit(s_past, (0, 0))
        
        # 时钟刻度
        for i in range(12):
            clock_angle = i * math.pi / 6
            tick_x1 = 60 + math.cos(clock_angle) * 35
            tick_y1 = 50 + math.sin(clock_angle) * 35
            tick_x2 = 60 + math.cos(clock_angle) * 40
            tick_y2 = 50 + math.sin(clock_angle) * 40
            pygame.draw.line(s, (200, 180, 255), (tick_x1, tick_y1), (tick_x2, tick_y2), 1)
        return s

    elif model_style == "data_god":
        # 数据之神：代码矩阵构成，数据流瀑布，矩阵雨
        # 机身由字符矩阵构成
        matrix_chars = "01"
        font_size = 8
        
        # 数据流瀑布背景
        for col in range(0, 120, 10):
            stream_height = random.randint(30, 80)
            stream_y = int((t * 50) % 120)
            for row in range(stream_height // font_size):
                char_y = (stream_y + row * font_size) % 120
                char = random.choice(matrix_chars)
                # 简化的字符渲染（用小方块代替）
                brightness = 255 - (row * 3)
                if brightness > 0:
                    pygame.draw.rect(s, (0, brightness, brightness // 2), 
                                   (col, char_y, font_size - 2, font_size - 2))
        
        # 机身主体（代码构成）
        code_shape = [(60, 15), (85, 80), (60, 70), (35, 80)]
        
        # 填充代码纹理
        for i in range(20):
            code_x = 40 + random.randint(0, 40)
            code_y = 20 + random.randint(0, 60)
            code_char = random.choice(matrix_chars)
            # 用绿色小方块表示代码
            pygame.draw.rect(s, (100, 255, 150), (code_x, code_y, 4, 6))
        
        # 机身轮廓
        pygame.draw.polygon(s, (0, 255, 50), code_shape, 2)
        
        # 矩阵雨暂留（悬浮的字符）
        for i in range(15):
            rain_angle = t * 4 + i * math.pi / 7.5
            rain_dist = 35 + 10 * math.sin(t * 5 + i)
            rain_x = 60 + math.cos(rain_angle) * rain_dist
            rain_y = 50 + math.sin(rain_angle) * rain_dist
            
            # 发光的代码字符
            pygame.draw.rect(s, (0, 255, 50), (int(rain_x) - 2, int(rain_y) - 3, 4, 6))
            # 字符发光效果
            s_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(s_glow, (100, 255, 150, 100), (int(rain_x), int(rain_y)), 6)
            s.blit(s_glow, (0, 0))
        
        # 数据流连线
        for i in range(6):
            line_angle = t * 3 + i * math.pi / 3
            lx = 60 + math.cos(line_angle) * 30
            ly = 50 + math.sin(line_angle) * 30
            pygame.draw.line(s, (30, 240, 70), (60, 50), (int(lx), int(ly)), 1)
        return s
    
    # ========== Titan专属涂装 ==========
    elif model_style == "mega_fortress":
        # 移动要塞·钢铁堡垒 - 层叠装甲板、多炮塔、防御塔形态
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：层叠装甲板（方形堡垒）
        armor_layers = [
            (70, 60, (120, 120, 120)),  # 最外层
            (60, 50, (140, 140, 140)),  # 中层
            (50, 40, (160, 160, 160)),  # 内层
        ]
        for layer_w, layer_h, color in armor_layers:
            pygame.draw.rect(s, color, (60 - layer_w//2, 50 - layer_h//2, layer_w, layer_h))
            pygame.draw.rect(s, (200, 200, 200), (60 - layer_w//2, 50 - layer_h//2, layer_w, layer_h), 2)
        
        # 主炮塔（顶部中心）
        main_turret_w, main_turret_h = 20, 12
        pygame.draw.rect(s, (100, 100, 100), (60 - main_turret_w//2, 30, main_turret_w, main_turret_h))
        pygame.draw.rect(s, (180, 180, 180), (60 - 4, 24, 8, 8))  # 炮管
        
        # 副炮塔（左右两侧）
        for side_x in [35, 85]:
            pygame.draw.rect(s, (110, 110, 110), (side_x - 8, 45, 16, 10))
            pygame.draw.circle(s, (150, 150, 150), (side_x, 50), 3)
        
        # 防御塔（四角）
        for corner_x, corner_y in [(40, 35), (80, 35), (40, 65), (80, 65)]:
            pygame.draw.polygon(s, (130, 130, 130), [
                (corner_x, corner_y - 6),
                (corner_x - 5, corner_y + 2),
                (corner_x + 5, corner_y + 2),
            ])
        
        # 工业烟雾（浓郁灰烟）
        smoke_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            smoke_offset = math.sin(t * 2 + i * math.pi / 4) * 5
            smoke_x = 60 + smoke_offset
            smoke_y = 70 + i * 8
            pygame.draw.circle(smoke_surface, (80, 80, 80, 120), (int(smoke_x), int(smoke_y)), int(8 + i * pulse))
        s.blit(smoke_surface, (0, 0))
        
        return s
    
    elif model_style == "nuclear_core":
        # 核动力泰坦·裂变反应堆 - 核心辉光、辐射波纹、核绿粒子
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：反应堆外壳
        pygame.draw.circle(s, (50, 50, 50), (60, 50), 28)
        pygame.draw.circle(s, (0, 200, 100), (60, 50), 24, 3)
        
        # 反应堆核心（辉光脉冲）
        core_size = int(18 * pulse)
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_glow, (0, 255, 120, 200), (60, 50), core_size)
        pygame.draw.circle(core_glow, (120, 255, 60, 150), (60, 50), core_size + 5)
        pygame.draw.circle(core_glow, (220, 255, 100, 80), (60, 50), core_size + 10)
        s.blit(core_glow, (0, 0))
        
        # 辐射波纹（3圈扩散）
        for i in range(3):
            wave_radius = (t * 40 + i * 20) % 60
            wave_alpha = int(200 * (1 - wave_radius / 60))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (0, 255, 120, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surface, (0, 0))
        
        # 核绿色辐射粒子（12个环绕）
        for i in range(12):
            particle_angle = t * 4 + i * math.pi / 6
            particle_dist = 35 + 5 * math.sin(t * 3 + i)
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(s, (120, 255, 60), (int(px), int(py)), 3)
            # 粒子发光
            p_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(p_glow, (120, 255, 60, 100), (int(px), int(py)), 5)
            s.blit(p_glow, (0, 0))
        
        # 辐射警告符号（旋转三叶）
        symbol_angle = t * 2
        for i in range(3):
            angle = symbol_angle + i * 2 * math.pi / 3
            sx = 60 + math.cos(angle) * 20
            sy = 50 + math.sin(angle) * 20
            pygame.draw.circle(s, (255, 255, 0), (int(sx), int(sy)), 4)
            pygame.draw.line(s, (255, 255, 0), (60, 50), (int(sx), int(sy)), 2)
        
        return s
    
    elif model_style == "volcanic_rage":
        # 熔岩巨兽·火山之怒 - 岩浆裂痕、火山爆发、燃烧石块
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        # 主体：深色岩石装甲
        body_points = [
            (60, 30), (80, 45), (75, 65), (60, 70),
            (45, 65), (40, 45)
        ]
        pygame.draw.polygon(s, (60, 30, 0), body_points)
        pygame.draw.polygon(s, (100, 50, 0), body_points, 2)
        
        # 岩浆裂痕（发光）
        magma_cracks = [
            [(50, 35), (55, 45), (52, 55)],
            [(65, 40), (68, 50), (70, 60)],
            [(55, 58), (60, 65), (65, 62)],
        ]
        for crack in magma_cracks:
            for i in range(len(crack) - 1):
                pygame.draw.line(s, (255, 120, 0), crack[i], crack[i+1], 3)
                # 裂痕发光
                crack_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(crack_glow, (255, 220, 50, 150), crack[i], crack[i+1], 6)
                s.blit(crack_glow, (0, 0))
        
        # 火山喷发（顶部）
        eruption_y = 20 - int(10 * pulse)
        for i in range(5):
            spark_x = 60 + (i - 2) * 8
            spark_y = eruption_y + i * 3
            pygame.draw.circle(s, (255, 100, 0), (spark_x, spark_y), 3)
            # 火花轨迹
            pygame.draw.line(s, (255, 150, 0), (spark_x, spark_y), (spark_x, spark_y + 10), 1)
        
        # 燃烧石块飞散（8个随机）
        for i in range(8):
            rock_angle = t * 2 + i * math.pi / 4
            rock_dist = 30 + 15 * math.sin(t * 3 + i)
            rock_x = 60 + math.cos(rock_angle) * rock_dist
            rock_y = 50 + math.sin(rock_angle) * rock_dist
            # 石块
            pygame.draw.rect(s, (80, 40, 0), (int(rock_x) - 3, int(rock_y) - 3, 6, 6))
            # 火焰
            fire_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(fire_glow, (255, 100, 0, 150), (int(rock_x), int(rock_y)), 5)
            s.blit(fire_glow, (0, 0))
        
        # 地狱火焰氛围（底部）
        hell_fire = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            fire_x = 40 + i * 8
            fire_height = 10 + 5 * math.sin(t * 5 + i)
            pygame.draw.polygon(hell_fire, (255, 100, 0, 180), [
                (fire_x, 80),
                (fire_x - 3, 80 - fire_height),
                (fire_x + 3, 80 - fire_height),
            ])
        s.blit(hell_fire, (0, 0))
        
        return s
    
    elif model_style == "steel_giant":
        # 机甲战神·钢铁巨人 - 机械关节、液压缸、重型武器、推进器群
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：机甲躯干
        pygame.draw.rect(s, (0, 150, 200), (50, 40, 20, 25))
        pygame.draw.rect(s, (255, 180, 0), (50, 40, 20, 25), 2)
        
        # 机械关节（肩部）
        for shoulder_x in [48, 72]:
            pygame.draw.circle(s, (100, 100, 100), (shoulder_x, 45), 6)
            pygame.draw.circle(s, (255, 180, 0), (shoulder_x, 45), 6, 2)
            # 活塞运动
            piston_offset = int(5 * math.sin(t * 3))
            pygame.draw.line(s, (150, 150, 150), (shoulder_x, 45), (shoulder_x, 55 + piston_offset), 3)
        
        # 液压缸（左右两侧，伸缩动画）
        for side_x, phase in [(35, 0), (85, math.pi)]:
            cylinder_length = 15 + int(5 * math.sin(t * 2.5 + phase))
            pygame.draw.rect(s, (120, 120, 120), (side_x - 3, 45, 6, cylinder_length))
            pygame.draw.circle(s, (200, 200, 0), (side_x, 45 + cylinder_length), 4)
        
        # 重型武器挂载（导弹发射器）
        for weapon_x in [40, 80]:
            # 发射器基座
            pygame.draw.rect(s, (80, 80, 80), (weapon_x - 5, 50, 10, 8))
            # 导弹
            pygame.draw.rect(s, (200, 50, 0), (weapon_x - 2, 45, 4, 6))
            pygame.draw.polygon(s, (255, 100, 0), [
                (weapon_x, 45),
                (weapon_x - 2, 48),
                (weapon_x + 2, 48),
            ])
        
        # 推进器群组（背部4个）
        thruster_positions = [(52, 68), (58, 68), (62, 68), (68, 68)]
        for tx, ty in thruster_positions:
            # 推进器喷口
            pygame.draw.rect(s, (60, 60, 60), (tx - 2, ty, 4, 6))
            # 火焰喷射
            flame_length = int(12 * pulse)
            flame_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(flame_surface, (100, 200, 255, 200), [
                (tx, ty + 6),
                (tx - 3, ty + 6 + flame_length),
                (tx + 3, ty + 6 + flame_length),
            ])
            s.blit(flame_surface, (0, 0))
        
        # 机械细节（螺栓）
        for bolt_x, bolt_y in [(54, 42), (66, 42), (54, 60), (66, 60)]:
            pygame.draw.circle(s, (180, 180, 180), (bolt_x, bolt_y), 2)
        
        return s
    
    elif model_style == "crystal":
        # 晶簇装甲·永恒之冰 - 水晶结构、光芒折射、冰晶粒子
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：中心冰晶核心
        pygame.draw.polygon(s, (150, 220, 255), [
            (60, 35), (70, 50), (60, 65), (50, 50)
        ])
        pygame.draw.polygon(s, (200, 255, 255), [
            (60, 35), (70, 50), (60, 65), (50, 50)
        ], 2)
        
        # 层叠水晶装甲（6个晶体突起）
        for i in range(6):
            crystal_angle = i * math.pi / 3 + t * 0.5
            cx = 60 + math.cos(crystal_angle) * 25
            cy = 50 + math.sin(crystal_angle) * 25
            # 晶体
            crystal_points = [
                (cx, cy - 8),
                (cx + 5, cy),
                (cx, cy + 8),
                (cx - 5, cy),
            ]
            pygame.draw.polygon(s, (180, 240, 255), crystal_points)
            pygame.draw.polygon(s, (200, 255, 255), crystal_points, 1)
        
        # 光芒多重折射（射线）
        refraction_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            ray_angle = t * 3 + i * math.pi / 4
            ray_length = 40 + 10 * math.sin(t * 2 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 50 + math.sin(ray_angle) * ray_length
            pygame.draw.line(refraction_surface, (200, 255, 255, 100), (60, 50), (int(ray_x), int(ray_y)), 2)
        s.blit(refraction_surface, (0, 0))
        
        # 冰晶粒子漩涡（16个螺旋）
        for i in range(16):
            spiral_angle = t * 4 + i * math.pi / 8
            spiral_dist = 20 + 15 * (i / 16)
            px = 60 + math.cos(spiral_angle) * spiral_dist
            py = 50 + math.sin(spiral_angle) * spiral_dist
            pygame.draw.circle(s, (180, 240, 255), (int(px), int(py)), 2)
            # 粒子闪耀
            sparkle = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(sparkle, (200, 255, 255, 150), (int(px), int(py)), 4)
            s.blit(sparkle, (0, 0))
        
        # 钻石般闪耀光环
        for i in range(3):
            halo_radius = 30 + i * 8
            halo_alpha = int(100 * (1 - i / 3) * pulse)
            halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(halo_surface, (200, 255, 255, halo_alpha), (60, 50), halo_radius, 1)
            s.blit(halo_surface, (0, 0))
        
        return s
    
    elif model_style == "hell_lord":
        # 恶魔战车·地狱领主 - 地狱之门、魔翼、血浆、火焰、魔魂
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        # 主体：黑暗战车
        pygame.draw.ellipse(s, (60, 0, 0), (45, 40, 30, 20))
        pygame.draw.ellipse(s, (120, 0, 0), (45, 40, 30, 20), 2)
        
        # 地狱之门（机身中心）
        gate_width = int(20 * pulse)
        gate_height = 25
        pygame.draw.rect(s, (30, 0, 0), (60 - gate_width//2, 38, gate_width, gate_height))
        # 门框火焰
        gate_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(gate_glow, (200, 30, 0, 150), (60 - gate_width//2 - 3, 35, gate_width + 6, gate_height + 6), 3)
        s.blit(gate_glow, (0, 0))
        
        # 魔翼展开（左右巨大翼）
        wing_offset = int(10 * math.sin(t * 2))
        # 左翼
        left_wing_points = [
            (50, 50),
            (30 - wing_offset, 40),
            (25 - wing_offset, 50),
            (30 - wing_offset, 60),
        ]
        pygame.draw.polygon(s, (100, 0, 0), left_wing_points)
        pygame.draw.polygon(s, (180, 0, 0), left_wing_points, 2)
        # 右翼
        right_wing_points = [
            (70, 50),
            (90 + wing_offset, 40),
            (95 + wing_offset, 50),
            (90 + wing_offset, 60),
        ]
        pygame.draw.polygon(s, (100, 0, 0), right_wing_points)
        pygame.draw.polygon(s, (180, 0, 0), right_wing_points, 2)
        
        # 血浆飞溅（10个液滴）
        for i in range(10):
            blood_angle = t * 4 + i * math.pi / 5
            blood_dist = 30 + 10 * math.sin(t * 3 + i)
            bx = 60 + math.cos(blood_angle) * blood_dist
            by = 50 + math.sin(blood_angle) * blood_dist
            pygame.draw.circle(s, (200, 30, 0), (int(bx), int(by)), 3)
            # 血迹轨迹
            pygame.draw.line(s, (150, 20, 0), (int(bx), int(by)), 
                           (int(bx - math.cos(blood_angle) * 5), int(by - math.sin(blood_angle) * 5)), 2)
        
        # 地狱火焰（底部环绕）
        hell_fire = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            fire_angle = i * math.pi / 4
            fx = 60 + math.cos(fire_angle) * 28
            fy = 50 + math.sin(fire_angle) * 28
            fire_height = 8 + 5 * math.sin(t * 5 + i)
            pygame.draw.polygon(hell_fire, (200, 30, 0, 200), [
                (fx, fy),
                (fx - 3, fy - fire_height),
                (fx + 3, fy - fire_height),
            ])
        s.blit(hell_fire, (0, 0))
        
        # 魔魂咆哭（幽灵脸）
        for i in range(3):
            soul_angle = t * 2 + i * 2 * math.pi / 3
            soul_dist = 35 + 5 * math.sin(t * 4 + i)
            sx = 60 + math.cos(soul_angle) * soul_dist
            sy = 50 + math.sin(soul_angle) * soul_dist
            # 鬼脸轮廓
            pygame.draw.circle(s, (100, 50, 50), (int(sx), int(sy)), 6)
            # 眼睛
            pygame.draw.circle(s, (255, 0, 0), (int(sx) - 2, int(sy) - 1), 2)
            pygame.draw.circle(s, (255, 0, 0), (int(sx) + 2, int(sy) - 1), 2)
        
        return s
    
    elif model_style == "space_station":
        # 轨道轰炸机·天基武库 - 卫星平台、等离子炮阵列、光束网络
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：卫星平台（六边形）
        platform_points = []
        for i in range(6):
            angle = i * math.pi / 3
            px = 60 + math.cos(angle) * 25
            py = 50 + math.sin(angle) * 25
            platform_points.append((px, py))
        pygame.draw.polygon(s, (200, 200, 220), platform_points)
        pygame.draw.polygon(s, (240, 240, 255), platform_points, 3)
        
        # 中心核心
        pygame.draw.circle(s, (255, 255, 255), (60, 50), 10)
        pygame.draw.circle(s, (240, 240, 255), (60, 50), 10, 2)
        
        # 等离子炮阵列（6门炮，每个顶点）
        for i in range(6):
            cannon_angle = i * math.pi / 3 + t * 0.5
            cannon_dist = 25
            cannon_x = 60 + math.cos(cannon_angle) * cannon_dist
            cannon_y = 50 + math.sin(cannon_angle) * cannon_dist
            # 炮台
            pygame.draw.circle(s, (180, 180, 200), (int(cannon_x), int(cannon_y)), 5)
            # 炮管
            barrel_x = cannon_x + math.cos(cannon_angle) * 8
            barrel_y = cannon_y + math.sin(cannon_angle) * 8
            pygame.draw.line(s, (220, 220, 255), (int(cannon_x), int(cannon_y)), 
                           (int(barrel_x), int(barrel_y)), 3)
            # 等离子光弹
            if i % 2 == 0:
                plasma_x = barrel_x + math.cos(cannon_angle) * 10
                plasma_y = barrel_y + math.sin(cannon_angle) * 10
                plasma_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(plasma_glow, (220, 220, 255, 200), (int(plasma_x), int(plasma_y)), 4)
                pygame.draw.circle(plasma_glow, (255, 255, 255, 100), (int(plasma_x), int(plasma_y)), 7)
                s.blit(plasma_glow, (0, 0))
        
        # 光束网络交织（连接所有炮台）
        beam_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            angle1 = i * math.pi / 3 + t * 0.5
            angle2 = (i + 2) % 6 * math.pi / 3 + t * 0.5
            x1 = 60 + math.cos(angle1) * 25
            y1 = 50 + math.sin(angle1) * 25
            x2 = 60 + math.cos(angle2) * 25
            y2 = 50 + math.sin(angle2) * 25
            pygame.draw.line(beam_surface, (220, 220, 255, 100), (int(x1), int(y1)), (int(x2), int(y2)), 2)
        s.blit(beam_surface, (0, 0))
        
        # 天基打击特效（向下激光）
        for i in range(3):
            laser_x = 50 + i * 10
            laser_length = 30 + int(10 * pulse)
            laser_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(laser_surface, (255, 255, 255, 200), (laser_x, 60), (laser_x, 60 + laser_length), 2)
            pygame.draw.circle(laser_surface, (255, 255, 255, 150), (laser_x, 60 + laser_length), 5)
            s.blit(laser_surface, (0, 0))
        
        # 能量护盾（外圈脉冲）
        for i in range(2):
            shield_radius = 35 + i * 8 + int(5 * pulse)
            shield_alpha = int(80 * (1 - i / 2))
            shield_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (220, 220, 255, shield_alpha), (60, 50), shield_radius, 2)
            s.blit(shield_surface, (0, 0))
        
        return s
    
    # ========== Thunderbird专属涂装 ==========
    elif model_style == "storm":
        # 风暴之眼·雷霆主宰 - 乌云漩涡、密集闪电链、雷电风暴核心
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        # 主体：鸟形轮廓（三角形）
        bird_points = [(60, 35), (75, 55), (60, 60), (45, 55)]
        pygame.draw.polygon(s, (100, 100, 150), bird_points)
        pygame.draw.polygon(s, (200, 200, 255), bird_points, 2)
        
        # 乌云漩涡环绕（3层螺旋云）
        cloud_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for layer in range(3):
            for i in range(8):
                cloud_angle = t * 2 + i * math.pi / 4 + layer * math.pi / 6
                cloud_dist = 25 + layer * 8
                cx = 60 + math.cos(cloud_angle) * cloud_dist
                cy = 50 + math.sin(cloud_angle) * cloud_dist
                cloud_size = 6 - layer * 2
                pygame.draw.circle(cloud_surface, (80, 80, 120, 150 - layer * 50), (int(cx), int(cy)), cloud_size)
        s.blit(cloud_surface, (0, 0))
        
        # 密集闪电链（12条闪电贯穿机身）
        lightning_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            if (int(t * 10) + i) % 3 == 0:  # 闪烁效果
                lightning_angle = i * math.pi / 6
                start_x = 60 + math.cos(lightning_angle) * 15
                start_y = 50 + math.sin(lightning_angle) * 15
                end_x = 60 + math.cos(lightning_angle) * 40
                end_y = 50 + math.sin(lightning_angle) * 40
                # 主闪电
                pygame.draw.line(lightning_surface, (200, 200, 255, 250), (int(start_x), int(start_y)), (int(end_x), int(end_y)), 2)
                # 闪电分叉
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                branch_angle = lightning_angle + math.pi / 6
                branch_x = mid_x + math.cos(branch_angle) * 10
                branch_y = mid_y + math.sin(branch_angle) * 10
                pygame.draw.line(lightning_surface, (150, 150, 255, 200), (int(mid_x), int(mid_y)), (int(branch_x), int(branch_y)), 1)
        s.blit(lightning_surface, (0, 0))
        
        # 雷电风暴核心（中心发光球）
        core_size = int(12 * pulse)
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_glow, (200, 200, 255, 220), (60, 50), core_size)
        pygame.draw.circle(core_glow, (150, 150, 255, 150), (60, 50), core_size + 5)
        pygame.draw.circle(core_glow, (100, 100, 200, 80), (60, 50), core_size + 10)
        s.blit(core_glow, (0, 0))
        
        return s
    
    elif model_style == "tesla":
        # 特斯拉线圈·电磁风暴 - 高压线圈、电弧网络、电磁脉冲、等离子球
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        # 主体：中心发电核心
        pygame.draw.circle(s, (0, 80, 200), (60, 50), 15)
        pygame.draw.circle(s, (0, 100, 255), (60, 50), 15, 2)
        
        # 高压线圈分布（6个环绕核心）
        for i in range(6):
            coil_angle = i * math.pi / 3 + t * 0.5
            coil_x = 60 + math.cos(coil_angle) * 25
            coil_y = 50 + math.sin(coil_angle) * 25
            # 线圈环
            pygame.draw.circle(s, (50, 150, 255), (int(coil_x), int(coil_y)), 6)
            pygame.draw.circle(s, (100, 200, 255), (int(coil_x), int(coil_y)), 6, 2)
            # 线圈内部螺旋
            for j in range(3):
                spiral_r = 3 + j
                spiral_angle = t * 5 + j * math.pi / 1.5
                sx = coil_x + math.cos(spiral_angle) * spiral_r
                sy = coil_y + math.sin(spiral_angle) * spiral_r
                pygame.draw.circle(s, (100, 200, 255), (int(sx), int(sy)), 1)
        
        # 电弧网络交织（连接所有线圈）
        arc_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            if (int(t * 8) + i) % 2 == 0:  # 闪烁
                angle1 = i * math.pi / 3 + t * 0.5
                angle2 = ((i + 1) % 6) * math.pi / 3 + t * 0.5
                x1 = 60 + math.cos(angle1) * 25
                y1 = 50 + math.sin(angle1) * 25
                x2 = 60 + math.cos(angle2) * 25
                y2 = 50 + math.sin(angle2) * 25
                # 电弧主线
                pygame.draw.line(arc_surface, (100, 200, 255, 200), (int(x1), int(y1)), (int(x2), int(y2)), 2)
                # 电弧辉光
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                pygame.draw.circle(arc_surface, (150, 220, 255, 150), (int(mid_x), int(mid_y)), 5)
        s.blit(arc_surface, (0, 0))
        
        # 电磁脉冲爆发（扩散波）
        for i in range(3):
            pulse_radius = (t * 50 + i * 25) % 80
            pulse_alpha = int(200 * (1 - pulse_radius / 80))
            pulse_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(pulse_surface, (50, 150, 255, pulse_alpha), (60, 50), int(pulse_radius), 2)
            s.blit(pulse_surface, (0, 0))
        
        # 等离子球环绕（8个小球）
        for i in range(8):
            plasma_angle = t * 4 + i * math.pi / 4
            plasma_dist = 35 + 5 * math.sin(t * 3 + i)
            px = 60 + math.cos(plasma_angle) * plasma_dist
            py = 50 + math.sin(plasma_angle) * plasma_dist
            plasma_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(plasma_glow, (100, 200, 255, 220), (int(px), int(py)), 4)
            pygame.draw.circle(plasma_glow, (150, 220, 255, 120), (int(px), int(py)), 7)
            s.blit(plasma_glow, (0, 0))
        
        return s
    
    elif model_style == "plasma":
        # 等离子羽翼·能量天使 - 等离子化羽翼、能量羽毛、等离子漩涡
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：天使形态核心
        pygame.draw.ellipse(s, (255, 150, 255), (50, 40, 20, 25))
        pygame.draw.ellipse(s, (255, 200, 255), (50, 40, 20, 25), 2)
        
        # 等离子化羽翼（左右大翅膀，每侧5根羽毛）
        wing_base_y = 50
        for side in [-1, 1]:  # 左右对称
            for i in range(5):
                feather_angle = side * (math.pi / 6 + i * math.pi / 12) + math.sin(t * 2 + i) * 0.2
                feather_length = 25 + i * 3
                feather_x = 60 + math.cos(feather_angle) * feather_length
                feather_y = wing_base_y + math.sin(feather_angle) * feather_length
                # 羽毛主干
                feather_color = (255, 150 + i * 10, 255)
                pygame.draw.line(s, feather_color, (60, wing_base_y), (int(feather_x), int(feather_y)), 3)
                # 羽毛发光
                feather_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(feather_glow, (255, 200, 255, 150), (60, wing_base_y), (int(feather_x), int(feather_y)), 6)
                s.blit(feather_glow, (0, 0))
        
        # 能量羽毛飘散（15个小羽毛粒子）
        for i in range(15):
            feather_angle = t * 3 + i * math.pi / 7.5
            feather_dist = 30 + 15 * math.sin(t * 2 + i)
            fx = 60 + math.cos(feather_angle) * feather_dist
            fy = 50 + math.sin(feather_angle) * feather_dist
            # 小羽毛
            pygame.draw.line(s, (230, 170, 255), (int(fx), int(fy)), (int(fx + 3), int(fy + 5)), 2)
            # 粒子辉光
            particle_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(particle_glow, (255, 200, 255, 120), (int(fx), int(fy)), 4)
            s.blit(particle_glow, (0, 0))
        
        # 等离子风暴漩涡（螺旋）
        spiral_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            spiral_angle = t * 4 + i * math.pi / 10
            spiral_dist = 10 + i * 2
            sx = 60 + math.cos(spiral_angle) * spiral_dist
            sy = 50 + math.sin(spiral_angle) * spiral_dist
            pygame.draw.circle(spiral_surface, (255, 150, 255, 180 - i * 8), (int(sx), int(sy)), 2)
        s.blit(spiral_surface, (0, 0))
        
        # 天使降临光环（外圈）
        for i in range(3):
            halo_radius = 35 + i * 8 + int(5 * pulse)
            halo_alpha = int(100 * (1 - i / 3))
            halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(halo_surface, (255, 200, 255, halo_alpha), (60, 50), halo_radius, 2)
            s.blit(halo_surface, (0, 0))
        
        return s
    
    elif model_style == "aurora_bird":
        # 极光战鹰·北境之翼 - 极光羽翼流动、七彩光带、光之羽毛
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：鸟形身躯
        pygame.draw.ellipse(s, (0, 200, 150), (52, 42, 16, 20))
        pygame.draw.ellipse(s, (100, 255, 200), (52, 42, 16, 20), 2)
        
        # 极光羽翼流动（波浪形光带，左右各4层）
        aurora_colors = [
            (255, 100, 100),  # 红
            (255, 200, 100),  # 橙
            (255, 255, 100),  # 黄
            (100, 255, 100),  # 绿
            (100, 200, 255),  # 蓝
            (200, 100, 255),  # 紫
        ]
        for side in [-1, 1]:
            for i in range(6):
                wave_angle = side * math.pi / 3 + math.sin(t * 3 + i * 0.5) * 0.3
                wave_length = 20 + i * 4
                wave_x = 60 + math.cos(wave_angle) * wave_length
                wave_y = 50 + math.sin(wave_angle) * wave_length
                # 极光光带（波浪线）
                aurora_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                color = aurora_colors[i]
                for j in range(5):
                    segment_ratio = j / 4
                    seg_x = 60 + (wave_x - 60) * segment_ratio
                    seg_y = 50 + (wave_y - 50) * segment_ratio + math.sin(t * 4 + j) * 3
                    next_ratio = (j + 1) / 4
                    next_x = 60 + (wave_x - 60) * next_ratio
                    next_y = 50 + (wave_y - 50) * next_ratio + math.sin(t * 4 + j + 1) * 3
                    pygame.draw.line(aurora_surface, (*color, 180), (int(seg_x), int(seg_y)), (int(next_x), int(next_y)), 3)
                s.blit(aurora_surface, (0, 0))
        
        # 七彩光带飘扬（尾部流动）
        for i in range(6):
            ribbon_x = 60
            ribbon_y = 70 + i * 5 + int(5 * math.sin(t * 3 + i))
            ribbon_length = 20 - i * 2
            color = aurora_colors[i]
            pygame.draw.line(s, color, (ribbon_x, ribbon_y), (ribbon_x + ribbon_length, ribbon_y + 5), 2)
        
        # 光之羽毛洒落（20个粒子）
        for i in range(20):
            feather_x = 40 + (t * 30 + i * 6) % 40
            feather_y = 30 + i * 3
            color = aurora_colors[i % 6]
            pygame.draw.line(s, color, (int(feather_x), int(feather_y)), (int(feather_x + 2), int(feather_y + 4)), 1)
            # 发光效果
            glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*color, 100), (int(feather_x), int(feather_y)), 3)
            s.blit(glow, (0, 0))
        
        return s
    
    elif model_style == "valkyrie":
        # 女武神·战争使者 - 神圣光翼、战争女神形态、圣光羽毛
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.12 + 1
        
        # 主体：女神人形轮廓
        pygame.draw.ellipse(s, (255, 240, 200), (54, 38, 12, 28))  # 身体
        pygame.draw.circle(s, (255, 250, 230), (60, 35), 5)  # 头部
        pygame.draw.ellipse(s, (255, 245, 220), (54, 38, 12, 28), 2)
        
        # 神圣光翼展开（巨大翅膀，左右各6根羽毛）
        wing_colors = [(255, 255, 255), (255, 250, 230), (255, 245, 220)]
        for side in [-1, 1]:
            for i in range(6):
                wing_angle = side * (math.pi / 4 + i * math.pi / 18)
                wing_length = 30 + i * 2
                wing_x = 60 + math.cos(wing_angle) * wing_length
                wing_y = 50 + math.sin(wing_angle) * wing_length
                # 羽毛层次（3层）
                for layer in range(3):
                    feather_offset = layer * 2
                    fx = 60 + math.cos(wing_angle) * (wing_length - feather_offset)
                    fy = 50 + math.sin(wing_angle) * (wing_length - feather_offset)
                    color = wing_colors[layer]
                    pygame.draw.line(s, color, (60, 50), (int(fx), int(fy)), 4 - layer)
        
        # 圣光羽毛暴雨（大量飘落羽毛）
        for i in range(25):
            feather_angle = t * 2 + i * math.pi / 12.5
            feather_dist = 25 + 20 * math.sin(t * 1.5 + i * 0.2)
            fx = 60 + math.cos(feather_angle) * feather_dist
            fy = 50 + math.sin(feather_angle) * feather_dist
            # 羽毛形状
            pygame.draw.line(s, (255, 250, 230), (int(fx), int(fy)), (int(fx + 3), int(fy + 5)), 2)
            # 圣光
            holy_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(holy_glow, (255, 255, 255, 120), (int(fx), int(fy)), 4)
            s.blit(holy_glow, (0, 0))
        
        # 天界裁决之力（十字圣光）
        cross_length = int(25 * pulse)
        cross_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 垂直光束
        pygame.draw.line(cross_glow, (255, 255, 255, 200), (60, 50 - cross_length), (60, 50 + cross_length), 4)
        # 水平光束
        pygame.draw.line(cross_glow, (255, 255, 255, 200), (60 - cross_length, 50), (60 + cross_length, 50), 4)
        s.blit(cross_glow, (0, 0))
        
        # 神圣光环
        halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(halo_surface, (255, 255, 255, 150), (60, 30), int(8 * pulse))
        s.blit(halo_surface, (0, 0))
        
        return s
    
    elif model_style == "phoenix":
        # 雷电凤凰·涅槃重生 - 凤凰真身、雷火交融、浴火重生、烈焰羽毛
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：凤凰身躯
        phoenix_body = [(60, 35), (70, 50), (65, 62), (60, 65), (55, 62), (50, 50)]
        pygame.draw.polygon(s, (255, 180, 0), phoenix_body)
        pygame.draw.polygon(s, (255, 255, 100), phoenix_body, 2)
        
        # 凤凰头部（高昂）
        pygame.draw.circle(s, (255, 200, 0), (60, 30), 6)
        # 凤冠（3根羽冠）
        for i in range(3):
            crown_x = 60 + (i - 1) * 4
            crown_y = 25 - i * 2
            pygame.draw.line(s, (255, 220, 50), (60, 30), (crown_x, crown_y), 2)
            pygame.draw.circle(s, (255, 100, 0), (crown_x, crown_y), 2)
        
        # 雷火交融羽翼（左右巨翼，火焰+闪电）
        for side in [-1, 1]:
            for i in range(7):
                wing_angle = side * (math.pi / 3 + i * math.pi / 14) + math.sin(t * 2 + i) * 0.15
                wing_length = 28 + i * 2
                wing_x = 60 + math.cos(wing_angle) * wing_length
                wing_y = 50 + math.sin(wing_angle) * wing_length
                # 火焰羽毛
                fire_gradient = (255, 220 - i * 15, 50 - i * 5)
                pygame.draw.line(s, fire_gradient, (60, 50), (int(wing_x), int(wing_y)), 3)
                # 雷电效果
                if i % 2 == 0 and (int(t * 10) % 3 == 0):
                    lightning = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(lightning, (100, 200, 255, 200), (60, 50), (int(wing_x), int(wing_y)), 1)
                    s.blit(lightning, (0, 0))
        
        # 浴火重生特效（环绕火焰螺旋）
        rebirth_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            fire_angle = t * 5 + i * math.pi / 6
            fire_dist = 20 + 15 * math.sin(t * 3 + i * 0.5)
            fire_x = 60 + math.cos(fire_angle) * fire_dist
            fire_y = 50 + math.sin(fire_angle) * fire_dist
            fire_size = 6 + 3 * math.sin(t * 4 + i)
            pygame.draw.circle(rebirth_surface, (255, 100, 0, 200), (int(fire_x), int(fire_y)), int(fire_size))
        s.blit(rebirth_surface, (0, 0))
        
        # 烈焰羽毛漫天（大量火焰粒子）
        for i in range(30):
            flame_angle = t * 3 + i * math.pi / 15
            flame_dist = 25 + 20 * (i / 30)
            fx = 60 + math.cos(flame_angle) * flame_dist
            fy = 50 + math.sin(flame_angle) * flame_dist
            # 火焰羽毛
            pygame.draw.line(s, (255, 200, 0), (int(fx), int(fy)), (int(fx + 2), int(fy + 4)), 1)
            # 火焰发光
            flame_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(flame_glow, (255, 150, 0, 150), (int(fx), int(fy)), 4)
            s.blit(flame_glow, (0, 0))
        
        # 凤鸣九天（声波扩散圈）
        for i in range(3):
            wave_radius = (t * 40 + i * 20) % 60
            wave_alpha = int(180 * (1 - wave_radius / 60))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (255, 200, 0, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surface, (0, 0))
        
        return s
    
    elif model_style == "cosmic":
        # 宇宙雷神·星云之翼 - 星云羽翼、宇宙风暴、星辰粒子、银河光带
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.12 + 1
        
        # 主体：星云核心
        pygame.draw.circle(s, (100, 50, 150), (60, 50), 12)
        pygame.draw.circle(s, (150, 100, 255), (60, 50), 12, 2)
        
        # 星云羽翼璀璨（渐变星云效果）
        nebula_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for side in [-1, 1]:
            for i in range(8):
                nebula_angle = side * (math.pi / 4 + i * math.pi / 16)
                nebula_dist = 20 + i * 3
                nx = 60 + math.cos(nebula_angle) * nebula_dist
                ny = 50 + math.sin(nebula_angle) * nebula_dist
                # 星云颜色渐变（紫-蓝-粉）
                color_r = 150 + int(50 * math.sin(t + i))
                color_g = 100 + int(50 * math.sin(t + i + 1))
                color_b = 255
                nebula_size = 8 - i
                pygame.draw.circle(nebula_surface, (color_r, color_g, color_b, 180), (int(nx), int(ny)), nebula_size)
        s.blit(nebula_surface, (0, 0))
        
        # 宇宙风暴漩涡（螺旋星云）
        for i in range(25):
            spiral_angle = t * 3 + i * math.pi / 12.5
            spiral_dist = 10 + i * 1.5
            sx = 60 + math.cos(spiral_angle) * spiral_dist
            sy = 50 + math.sin(spiral_angle) * spiral_dist
            star_color = (180 + int(30 * math.sin(i)), 120, 255)
            pygame.draw.circle(s, star_color, (int(sx), int(sy)), 2)
        
        # 星辰粒子暴雨（大量闪烁星星）
        for i in range(40):
            star_angle = t * 2 + i * math.pi / 20
            star_dist = 20 + 25 * (i / 40) + 5 * math.sin(t * 3 + i)
            star_x = 60 + math.cos(star_angle) * star_dist
            star_y = 50 + math.sin(star_angle) * star_dist
            # 星星闪烁
            if (int(t * 10) + i) % 4 < 2:
                pygame.draw.circle(s, (200, 150, 255), (int(star_x), int(star_y)), 2)
                # 星光
                star_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(star_glow, (200, 150, 255, 120), (int(star_x), int(star_y)), 4)
                s.blit(star_glow, (0, 0))
        
        # 银河光带尾迹（流动光带）
        galaxy_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            band_y = 40 + i * 4 + int(5 * math.sin(t * 2 + i * 0.5))
            band_x_start = 50 - i * 2
            band_x_end = 70 + i * 2
            # 渐变光带
            for j in range(20):
                segment_x = band_x_start + (band_x_end - band_x_start) * j / 20
                color_intensity = int(200 * (1 - abs(j - 10) / 10))
                pygame.draw.circle(galaxy_surface, (150, 100, 255, color_intensity), (int(segment_x), band_y), 2)
        s.blit(galaxy_surface, (0, 0))
        
        # 诸神黄昏（外圈能量爆发）
        for i in range(3):
            explosion_radius = 30 + i * 10 + int(8 * pulse)
            explosion_alpha = int(120 * (1 - i / 3))
            explosion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, (180, 120, 255, explosion_alpha), (60, 50), explosion_radius, 3)
            s.blit(explosion_surface, (0, 0))
        
        return s
    
    # ========== Viper专属涂装 ==========
    elif model_style == "cobra":
        # 眼镜蛇·毒牙致命 - 眼镜蛇形态、毒牙、蛇信、剧毒喷射
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        # 蛇头（三角形头部）
        head_points = [(60, 30), (70, 45), (50, 45)]
        pygame.draw.polygon(s, (100, 200, 0), head_points)
        pygame.draw.polygon(s, (150, 255, 50), head_points, 2)
        
        # 眼镜蛇颈部扩展（标志性扁平）
        hood_points = [
            (50, 45), (40, 50), (42, 60), 
            (60, 58), 
            (78, 60), (80, 50), (70, 45)
        ]
        pygame.draw.polygon(s, (120, 220, 20), hood_points)
        pygame.draw.polygon(s, (150, 255, 50), hood_points, 2)
        # 眼镜纹（两个圆环）
        for side_x in [48, 72]:
            pygame.draw.circle(s, (80, 180, 0), (side_x, 53), 5)
            pygame.draw.circle(s, (150, 255, 50), (side_x, 53), 5, 1)
        
        # 蛇身（S形波浪）
        body_points = []
        for i in range(10):
            segment_y = 58 + i * 4
            segment_x = 60 + int(12 * math.sin(t * 3 + i * 0.5))
            body_points.append((segment_x, segment_y))
        for i in range(len(body_points) - 1):
            pygame.draw.line(s, (100, 200, 0), body_points[i], body_points[i+1], 8)
        
        # 毒牙（两根尖锐牙齿）
        fang_length = int(8 * pulse)
        pygame.draw.line(s, (255, 255, 255), (55, 38), (53, 38 + fang_length), 3)
        pygame.draw.line(s, (255, 255, 255), (65, 38), (67, 38 + fang_length), 3)
        # 毒液滴
        for fang_x in [53, 67]:
            poison_y = 38 + fang_length + int(3 * math.sin(t * 5))
            pygame.draw.circle(s, (100, 255, 0), (fang_x, poison_y), 2)
        
        # 蛇信吐露（分叉舌头）
        tongue_length = 10 + int(5 * math.sin(t * 4))
        tongue_base_x, tongue_base_y = 60, 40
        tongue_tip_y = tongue_base_y + tongue_length
        # 舌头主干
        pygame.draw.line(s, (255, 100, 100), (tongue_base_x, tongue_base_y), (tongue_base_x, tongue_tip_y), 2)
        # 分叉
        pygame.draw.line(s, (255, 100, 100), (tongue_base_x, tongue_tip_y), (tongue_base_x - 3, tongue_tip_y + 3), 1)
        pygame.draw.line(s, (255, 100, 100), (tongue_base_x, tongue_tip_y), (tongue_base_x + 3, tongue_tip_y + 3), 1)
        
        # 剧毒喷射（毒液粒子）
        for i in range(8):
            spray_angle = math.pi / 2 + (i - 4) * math.pi / 16
            spray_dist = 15 + (t * 20 + i * 5) % 25
            spray_x = 60 + math.cos(spray_angle) * spray_dist
            spray_y = 40 + math.sin(spray_angle) * spray_dist
            pygame.draw.circle(s, (120, 240, 20), (int(spray_x), int(spray_y)), 2)
        
        return s
    
    elif model_style == "acid":
        # 强酸腐蚀·溶解一切 - 强酸流淌、腐蚀烟雾、酸液飞溅、金属溶解
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：酸液容器
        pygame.draw.rect(s, (180, 180, 0), (48, 35, 24, 30))
        pygame.draw.rect(s, (220, 220, 50), (48, 35, 24, 30), 2)
        
        # 强酸液体流淌（内部波动）
        acid_level = 50 + int(5 * math.sin(t * 3))
        pygame.draw.rect(s, (200, 255, 0), (50, acid_level, 20, 65 - acid_level))
        # 液面波动
        for i in range(5):
            wave_x = 50 + i * 5
            wave_y = acid_level + int(2 * math.sin(t * 4 + i))
            pygame.draw.circle(s, (255, 255, 100), (wave_x, wave_y), 2)
        
        # 腐蚀烟雾升腾（向上飘散）
        smoke_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            smoke_x = 55 + (i % 3) * 5 + int(3 * math.sin(t * 2 + i))
            smoke_y = 35 - (t * 15 + i * 5) % 30
            smoke_size = 4 + int(2 * (30 - (t * 15 + i * 5) % 30) / 30)
            pygame.draw.circle(smoke_surface, (220, 255, 50, 180 - i * 15), (int(smoke_x), int(smoke_y)), smoke_size)
        s.blit(smoke_surface, (0, 0))
        
        # 酸液飞溅（四周喷射）
        for i in range(12):
            splash_angle = i * math.pi / 6 + t * 2
            splash_dist = 25 + 10 * math.sin(t * 3 + i)
            splash_x = 60 + math.cos(splash_angle) * splash_dist
            splash_y = 50 + math.sin(splash_angle) * splash_dist
            # 酸滴
            pygame.draw.circle(s, (220, 255, 50), (int(splash_x), int(splash_y)), 3)
            # 腐蚀轨迹
            trail_x = splash_x - math.cos(splash_angle) * 5
            trail_y = splash_y - math.sin(splash_angle) * 5
            pygame.draw.line(s, (200, 240, 20), (int(splash_x), int(splash_y)), (int(trail_x), int(trail_y)), 1)
        
        # 金属溶解效果（底部腐蚀坑）
        corrosion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            pit_x = 50 + i * 5
            pit_size = 4 + int(2 * pulse)
            pygame.draw.circle(corrosion_surface, (150, 180, 0, 200), (pit_x, 70), pit_size)
            # 冒泡
            if int(t * 5 + i) % 3 == 0:
                bubble_y = 65 - int(5 * math.sin(t * 4 + i))
                pygame.draw.circle(corrosion_surface, (220, 255, 50, 150), (pit_x, bubble_y), 3)
        s.blit(corrosion_surface, (0, 0))
        
        return s
    
    elif model_style == "bio":
        # 生化武器·病毒扩散 - 病毒容器、病毒云团、感染粒子、生物危害符号
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：生化容器（圆柱形）
        pygame.draw.rect(s, (0, 150, 80), (52, 38, 16, 28))
        pygame.draw.ellipse(s, (0, 180, 100), (52, 35, 16, 6))
        pygame.draw.ellipse(s, (0, 180, 100), (52, 60, 16, 6))
        pygame.draw.rect(s, (100, 255, 150), (52, 38, 16, 28), 2)
        
        # 病毒容器内部（绿色病毒液）
        virus_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(virus_glow, (50, 220, 120, 200), (54, 40, 12, 24))
        s.blit(virus_glow, (0, 0))
        
        # 病毒云团扩散（3层雾气）
        for layer in range(3):
            for i in range(8):
                cloud_angle = t * 1.5 + i * math.pi / 4 + layer * math.pi / 6
                cloud_dist = 25 + layer * 10
                cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
                cloud_y = 50 + math.sin(cloud_angle) * cloud_dist
                cloud_size = 8 - layer * 2
                cloud_alpha = 180 - layer * 60
                cloud_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(cloud_surface, (50, 220, 120, cloud_alpha), (int(cloud_x), int(cloud_y)), cloud_size)
                s.blit(cloud_surface, (0, 0))
        
        # 感染粒子漂浮（20个病毒粒子）
        for i in range(20):
            particle_angle = t * 2 + i * math.pi / 10
            particle_dist = 20 + 20 * (i / 20) + 5 * math.sin(t * 3 + i)
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            # 病毒粒子（带刺的圆）
            pygame.draw.circle(s, (50, 220, 120), (int(px), int(py)), 3)
            # 病毒刺突（4个方向）
            for spike_dir in range(4):
                spike_angle = spike_dir * math.pi / 2 + t * 3
                spike_x = px + math.cos(spike_angle) * 4
                spike_y = py + math.sin(spike_angle) * 4
                pygame.draw.line(s, (100, 255, 150), (int(px), int(py)), (int(spike_x), int(spike_y)), 1)
        
        # 生物危害符号闪烁（中心三叶）
        if int(t * 3) % 2 == 0:
            symbol_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            for i in range(3):
                symbol_angle = i * 2 * math.pi / 3 + t
                symbol_x = 60 + math.cos(symbol_angle) * 12
                symbol_y = 50 + math.sin(symbol_angle) * 12
                # 扇形叶片
                pygame.draw.circle(symbol_surface, (255, 255, 0, 200), (int(symbol_x), int(symbol_y)), 5)
                pygame.draw.line(symbol_surface, (255, 255, 0, 200), (60, 50), (int(symbol_x), int(symbol_y)), 3)
            # 中心圆
            pygame.draw.circle(symbol_surface, (255, 255, 0, 200), (60, 50), 6)
            pygame.draw.circle(symbol_surface, (200, 200, 0, 200), (60, 50), 6, 2)
            s.blit(symbol_surface, (0, 0))
        
        return s
    
    elif model_style == "plasma_viper":
        # 等离子毒液·能量腐蚀 - 等离子态毒液、能量腐蚀、高能毒素、物质解离
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：能量核心
        pygame.draw.circle(s, (150, 0, 200), (60, 50), 15)
        pygame.draw.circle(s, (200, 0, 255), (60, 50), 15, 2)
        
        # 等离子态毒液（流动环状）
        plasma_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            plasma_angle = t * 4 + i * math.pi / 6
            plasma_dist = 18 + 5 * math.sin(t * 3 + i)
            px = 60 + math.cos(plasma_angle) * plasma_dist
            py = 50 + math.sin(plasma_angle) * plasma_dist
            # 等离子液滴
            drop_size = int(4 * pulse)
            pygame.draw.circle(plasma_surface, (200, 0, 255, 220), (int(px), int(py)), drop_size)
            pygame.draw.circle(plasma_surface, (255, 100, 255, 150), (int(px), int(py)), drop_size + 2)
        s.blit(plasma_surface, (0, 0))
        
        # 能量腐蚀波（扩散圈）
        for i in range(3):
            corrosion_radius = 20 + i * 10 + (t * 30) % 20
            corrosion_alpha = int(200 * (1 - ((t * 30) % 20) / 20))
            corrosion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(corrosion_surface, (220, 50, 255, corrosion_alpha), (60, 50), int(corrosion_radius), 2)
            s.blit(corrosion_surface, (0, 0))
        
        # 高能毒素射线（8条）
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            if (int(t * 8) + i) % 3 == 0:  # 闪烁
                ray_angle = i * math.pi / 4 + t * 0.5
                ray_length = 30 + 10 * math.sin(t * 3 + i)
                ray_x = 60 + math.cos(ray_angle) * ray_length
                ray_y = 50 + math.sin(ray_angle) * ray_length
                pygame.draw.line(ray_surface, (200, 0, 255, 200), (60, 50), (int(ray_x), int(ray_y)), 2)
                # 射线末端辉光
                pygame.draw.circle(ray_surface, (255, 100, 255, 150), (int(ray_x), int(ray_y)), 5)
        s.blit(ray_surface, (0, 0))
        
        # 物质解离效果（粒子分解）
        for i in range(15):
            disintegrate_angle = t * 3 + i * math.pi / 7.5
            disintegrate_dist = 25 + 15 * (i / 15)
            dx = 60 + math.cos(disintegrate_angle) * disintegrate_dist
            dy = 50 + math.sin(disintegrate_angle) * disintegrate_dist
            # 解离粒子（小方块）
            particle_size = 2 + int(2 * math.sin(t * 4 + i))
            pygame.draw.rect(s, (220, 50, 255), (int(dx) - particle_size//2, int(dy) - particle_size//2, particle_size, particle_size))
            # 粒子发光
            particle_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(particle_glow, (255, 100, 255, 120), (int(dx), int(dy)), 4)
            s.blit(particle_glow, (0, 0))
        
        return s
    
    elif model_style == "hydra":
        # 九头蛇·致命群蛇 - 多头蛇、九条蛇影、毒牙密布、毒液暴雨
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：蛇身中心
        pygame.draw.circle(s, (0, 120, 40), (60, 50), 12)
        pygame.draw.circle(s, (100, 200, 100), (60, 50), 12, 2)
        
        # 九条蛇头环绕（每条独立动画）
        for i in range(9):
            snake_angle = i * 2 * math.pi / 9 + t * 1.5
            snake_dist = 25 + 8 * math.sin(t * 2 + i * 0.5)
            head_x = 60 + math.cos(snake_angle) * snake_dist
            head_y = 50 + math.sin(snake_angle) * snake_dist
            
            # 蛇颈（连接到中心）
            neck_segments = 5
            for seg in range(neck_segments):
                seg_ratio = (seg + 1) / neck_segments
                seg_x = 60 + (head_x - 60) * seg_ratio + math.sin(t * 4 + i + seg) * 2
                seg_y = 50 + (head_y - 50) * seg_ratio + math.cos(t * 4 + i + seg) * 2
                prev_ratio = seg / neck_segments
                prev_x = 60 + (head_x - 60) * prev_ratio + math.sin(t * 4 + i + seg - 1) * 2
                prev_y = 50 + (head_y - 50) * prev_ratio + math.cos(t * 4 + i + seg - 1) * 2
                pygame.draw.line(s, (50, 180, 80), (int(prev_x), int(prev_y)), (int(seg_x), int(seg_y)), 4)
            
            # 蛇头（三角形）
            head_size = 6
            head_angle_offset = snake_angle
            head_points = [
                (head_x + math.cos(head_angle_offset) * head_size, head_y + math.sin(head_angle_offset) * head_size),
                (head_x + math.cos(head_angle_offset + 2.5) * 4, head_y + math.sin(head_angle_offset + 2.5) * 4),
                (head_x + math.cos(head_angle_offset - 2.5) * 4, head_y + math.sin(head_angle_offset - 2.5) * 4),
            ]
            pygame.draw.polygon(s, (0, 150, 50), [(int(p[0]), int(p[1])) for p in head_points])
            
            # 毒牙
            fang_x = head_x + math.cos(head_angle_offset) * (head_size + 3)
            fang_y = head_y + math.sin(head_angle_offset) * (head_size + 3)
            pygame.draw.line(s, (255, 255, 255), (int(head_x), int(head_y)), (int(fang_x), int(fang_y)), 2)
        
        # 毒液暴雨（大量毒滴）
        rain_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(25):
            rain_x = 30 + (i * 3.6) % 60
            rain_y = 20 + ((t * 50 + i * 4) % 70)
            pygame.draw.line(rain_surface, (50, 255, 0, 200), (int(rain_x), int(rain_y)), (int(rain_x), int(rain_y + 5)), 2)
            pygame.draw.circle(rain_surface, (100, 255, 50, 180), (int(rain_x), int(rain_y + 5)), 2)
        s.blit(rain_surface, (0, 0))
        
        return s
    
    elif model_style == "neon":
        # 霓虹毒蛇·致命诱惑 - 霓虹毒液纹理、彩色毒雾、荧光粒子
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        # 主体：蛇形轮廓（波浪身躯）
        body_points = []
        for i in range(15):
            segment_y = 30 + i * 4
            segment_x = 60 + int(15 * math.sin(t * 2 + i * 0.4))
            body_points.append((segment_x, segment_y))
        
        # 霓虹毒液纹理（渐变彩色）
        for i in range(len(body_points) - 1):
            # 彩虹渐变
            hue = (t * 50 + i * 20) % 360
            color_r = int(127 + 127 * math.sin(math.radians(hue)))
            color_g = int(127 + 127 * math.sin(math.radians(hue + 120)))
            color_b = int(127 + 127 * math.sin(math.radians(hue + 240)))
            pygame.draw.line(s, (color_r, color_g, color_b), body_points[i], body_points[i+1], 10)
            # 发光效果
            glow_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(glow_surface, (color_r, color_g, color_b, 150), body_points[i], body_points[i+1], 14)
            s.blit(glow_surface, (0, 0))
        
        # 彩色毒雾飘散（环绕雾气）
        fog_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            fog_angle = t * 2 + i * math.pi / 6
            fog_dist = 25 + 10 * math.sin(t * 1.5 + i)
            fog_x = 60 + math.cos(fog_angle) * fog_dist
            fog_y = 50 + math.sin(fog_angle) * fog_dist
            # 彩色雾团
            hue = (t * 80 + i * 30) % 360
            fog_r = int(127 + 127 * math.sin(math.radians(hue)))
            fog_g = int(127 + 127 * math.sin(math.radians(hue + 120)))
            fog_b = int(127 + 127 * math.sin(math.radians(hue + 240)))
            pygame.draw.circle(fog_surface, (fog_r, fog_g, fog_b, 120), (int(fog_x), int(fog_y)), 8)
        s.blit(fog_surface, (0, 0))
        
        # 荧光毒液粒子（闪烁）
        for i in range(20):
            if (int(t * 10) + i) % 4 < 2:  # 闪烁效果
                particle_angle = t * 3 + i * math.pi / 10
                particle_dist = 20 + 20 * (i / 20)
                px = 60 + math.cos(particle_angle) * particle_dist
                py = 50 + math.sin(particle_angle) * particle_dist
                # 荧光色
                hue = (t * 100 + i * 18) % 360
                p_r = int(127 + 127 * math.sin(math.radians(hue)))
                p_g = int(127 + 127 * math.sin(math.radians(hue + 120)))
                p_b = int(127 + 127 * math.sin(math.radians(hue + 240)))
                pygame.draw.circle(s, (p_r, p_g, p_b), (int(px), int(py)), 3)
                # 粒子辉光
                particle_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(particle_glow, (p_r, p_g, p_b, 180), (int(px), int(py)), 6)
                s.blit(particle_glow, (0, 0))
        
        return s
    
    elif model_style == "serpent_god":
        # 蛇神降世·巴蛇吞象 - 上古蛇神、蛇鳞闪耀、神话再现
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：巨大蛇头
        head_points = [(60, 25), (75, 45), (70, 55), (60, 58), (50, 55), (45, 45)]
        pygame.draw.polygon(s, (200, 160, 0), head_points)
        pygame.draw.polygon(s, (255, 215, 0), head_points, 3)
        
        # 蛇神眼睛（发光金色）
        for eye_x in [52, 68]:
            pygame.draw.circle(s, (255, 255, 100), (eye_x, 40), 5)
            pygame.draw.circle(s, (255, 215, 0), (eye_x, 40), 5, 2)
            # 瞳孔
            pygame.draw.circle(s, (200, 0, 0), (eye_x, 40), 2)
            # 神光
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (255, 255, 100, 150), (eye_x, 40), int(8 * pulse))
            s.blit(eye_glow, (0, 0))
        
        # 蛇身（粗壮盘旋）
        body_segments = []
        for i in range(12):
            segment_angle = t * 1.5 + i * math.pi / 6
            segment_dist = 20 + i * 2
            seg_x = 60 + math.cos(segment_angle) * segment_dist
            seg_y = 58 + i * 3
            body_segments.append((seg_x, seg_y))
        for i in range(len(body_segments) - 1):
            pygame.draw.line(s, (220, 180, 0), (int(body_segments[i][0]), int(body_segments[i][1])), 
                           (int(body_segments[i+1][0]), int(body_segments[i+1][1])), 12)
        
        # 蛇鳞闪耀（鳞片反光）
        scale_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            scale_angle = t * 2 + i * math.pi / 10
            scale_dist = 15 + 20 * (i / 20)
            scale_x = 60 + math.cos(scale_angle) * scale_dist
            scale_y = 50 + math.sin(scale_angle) * scale_dist
            # 鳞片（菱形）
            if (int(t * 8) + i) % 5 < 2:  # 闪烁
                scale_points = [
                    (scale_x, scale_y - 3),
                    (scale_x + 2, scale_y),
                    (scale_x, scale_y + 3),
                    (scale_x - 2, scale_y),
                ]
                pygame.draw.polygon(scale_surface, (255, 255, 100, 220), [(int(p[0]), int(p[1])) for p in scale_points])
        s.blit(scale_surface, (0, 0))
        
        # 神话气息（金色光环）
        for i in range(3):
            halo_radius = 30 + i * 10 + int(5 * pulse)
            halo_alpha = int(150 * (1 - i / 3))
            halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(halo_surface, (255, 215, 0, halo_alpha), (60, 45), halo_radius, 2)
            s.blit(halo_surface, (0, 0))
        
        # 巴蛇吞象之力（能量波动）
        power_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            power_angle = t * 3 + i * math.pi / 4
            power_dist = 35 + 10 * math.sin(t * 2 + i)
            power_x = 60 + math.cos(power_angle) * power_dist
            power_y = 50 + math.sin(power_angle) * power_dist
            pygame.draw.circle(power_surface, (255, 230, 50, 200), (int(power_x), int(power_y)), 4)
            # 连接到中心的能量线
            pygame.draw.line(power_surface, (255, 215, 0, 150), (60, 50), (int(power_x), int(power_y)), 2)
        s.blit(power_surface, (0, 0))
        
        return s
    
    # ========== Specter专属涂装 ==========
    elif model_style == "reaper":
        # 死神收割·灵魂收集者 - 死神镰刀、灵魂火焰、收割特效、亡魂哀嚎
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：死神斗篷轮廓
        cloak_points = [
            (60, 30), (70, 45), (68, 65), (60, 70),
            (52, 65), (50, 45)
        ]
        pygame.draw.polygon(s, (30, 0, 50), cloak_points)
        pygame.draw.polygon(s, (100, 0, 150), cloak_points, 2)
        
        # 死神头部（骷髅）
        pygame.draw.circle(s, (200, 200, 200), (60, 35), 6)
        # 空洞眼眶（发红光）
        for eye_x in [57, 63]:
            pygame.draw.circle(s, (255, 0, 0), (eye_x, 34), 2)
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (255, 0, 0, 150), (eye_x, 34), 4)
            s.blit(eye_glow, (0, 0))
        
        # 死神镰刀（大镰刀）
        scythe_angle = math.sin(t * 2) * 0.3
        # 镰刀柄
        handle_x = 75 + math.cos(scythe_angle) * 5
        handle_y = 50 + math.sin(scythe_angle) * 5
        pygame.draw.line(s, (100, 100, 100), (60, 45), (int(handle_x), int(handle_y)), 3)
        # 镰刀刃（弧形）
        blade_points = [
            (handle_x, handle_y),
            (handle_x + 15 * math.cos(scythe_angle + 0.5), handle_y + 15 * math.sin(scythe_angle + 0.5)),
            (handle_x + 12 * math.cos(scythe_angle + 1.5), handle_y + 12 * math.sin(scythe_angle + 1.5)),
            (handle_x + 5 * math.cos(scythe_angle + 2), handle_y + 5 * math.sin(scythe_angle + 2))
        ]
        pygame.draw.polygon(s, (200, 200, 200), [(int(p[0]), int(p[1])) for p in blade_points])
        pygame.draw.polygon(s, (255, 255, 255), [(int(p[0]), int(p[1])) for p in blade_points], 2)
        
        # 灵魂火焰飘荡（绿色鬼火）
        for i in range(10):
            flame_angle = t * 2 + i * math.pi / 5
            flame_dist = 25 + 10 * math.sin(t * 1.5 + i)
            flame_x = 60 + math.cos(flame_angle) * flame_dist
            flame_y = 50 + math.sin(flame_angle) * flame_dist
            flame_height = 8 + 4 * math.sin(t * 4 + i)
            # 鬼火形状
            fire_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(fire_surface, (100, 255, 100, 200), [
                (int(flame_x), int(flame_y)),
                (int(flame_x - 3), int(flame_y + flame_height)),
                (int(flame_x + 3), int(flame_y + flame_height))
            ])
            s.blit(fire_surface, (0, 0))
        
        # 收割特效（灵魂轨迹）
        soul_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            soul_offset = (t * 30 + i * 15) % 50
            soul_x = 60 + soul_offset - 25
            soul_y = 45 + int(5 * math.sin(t * 3 + i))
            # 小灵魂
            pygame.draw.circle(soul_surface, (180, 255, 180, 200 - int(soul_offset * 4)), (int(soul_x), int(soul_y)), 4)
        s.blit(soul_surface, (0, 0))
        
        # 亡魂哀嚎（声波圈）
        for i in range(3):
            wail_radius = (t * 40 + i * 20) % 60
            wail_alpha = int(150 * (1 - wail_radius / 60))
            wail_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wail_surface, (100, 0, 150, wail_alpha), (60, 50), int(wail_radius), 2)
            s.blit(wail_surface, (0, 0))
        
        return s
    
    elif model_style == "assassin":
        # 幽灵刺客·无声夺命 - 刺客形态、无声接近、致命一击
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        # 主体：刺客身影（半透明）
        body_alpha = int(150 + 50 * math.sin(t * 2))  # 闪烁隐身
        body_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 身体轮廓
        body_points = [(60, 35), (68, 50), (64, 65), (60, 68), (56, 65), (52, 50)]
        pygame.draw.polygon(body_surface, (50, 50, 80, body_alpha), body_points)
        pygame.draw.polygon(body_surface, (100, 100, 150, body_alpha), body_points, 2)
        s.blit(body_surface, (0, 0))
        
        # 刺客兜帽
        hood_points = [(60, 30), (65, 38), (55, 38)]
        pygame.draw.polygon(s, (30, 30, 50), hood_points)
        
        # 隐身残影（多个半透明分身）
        for i in range(3):
            shadow_offset = 8 * (i + 1)
            shadow_alpha = int(100 - i * 30)
            shadow_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            shadow_points = [(p[0] - shadow_offset, p[1]) for p in body_points]
            pygame.draw.polygon(shadow_surface, (50, 50, 80, shadow_alpha), shadow_points)
            s.blit(shadow_surface, (0, 0))
        
        # 双刀（刺客武器）
        knife_angle = math.sin(t * 3) * 0.3
        # 左手刀
        left_knife_x = 52 + math.cos(knife_angle) * 8
        left_knife_y = 55 + math.sin(knife_angle) * 8
        pygame.draw.line(s, (150, 150, 200), (52, 55), (int(left_knife_x), int(left_knife_y)), 3)
        pygame.draw.polygon(s, (200, 200, 255), [
            (int(left_knife_x), int(left_knife_y)),
            (int(left_knife_x + 5 * math.cos(knife_angle)), int(left_knife_y + 5 * math.sin(knife_angle))),
            (int(left_knife_x + 3 * math.cos(knife_angle + 0.5)), int(left_knife_y + 3 * math.sin(knife_angle + 0.5)))
        ])
        # 右手刀
        right_knife_x = 68 + math.cos(-knife_angle) * 8
        right_knife_y = 55 + math.sin(-knife_angle) * 8
        pygame.draw.line(s, (150, 150, 200), (68, 55), (int(right_knife_x), int(right_knife_y)), 3)
        pygame.draw.polygon(s, (200, 200, 255), [
            (int(right_knife_x), int(right_knife_y)),
            (int(right_knife_x + 5 * math.cos(-knife_angle)), int(right_knife_y + 5 * math.sin(-knife_angle))),
            (int(right_knife_x + 3 * math.cos(-knife_angle - 0.5)), int(right_knife_y + 3 * math.sin(-knife_angle - 0.5)))
        ])
        
        # 致命一击标记（红色叉）
        if int(t * 4) % 3 == 0:
            mark_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(mark_surface, (255, 0, 0, 200), (52, 42), (68, 58), 3)
            pygame.draw.line(mark_surface, (255, 0, 0, 200), (68, 42), (52, 58), 3)
            s.blit(mark_surface, (0, 0))
        
        # 无声移动粒子（黑雾）
        fog_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            fog_x = 60 + int(15 * math.cos(t * 2 + i * math.pi / 4))
            fog_y = 50 + int(15 * math.sin(t * 2 + i * math.pi / 4))
            pygame.draw.circle(fog_surface, (30, 30, 50, 100), (fog_x, fog_y), 6)
        s.blit(fog_surface, (0, 0))
        
        return s
    
    elif model_style == "wraith":
        # 幽灵怨灵·冤魂缠绕 - 半透明幽灵、怨灵面孔、灵魂锁链、冤魂飘荡
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：幽灵飘荡形态（半透明波动布料）
        ghost_points = []
        for i in range(10):
            angle = i * math.pi / 5 + math.pi / 2
            dist = 20 + 5 * math.sin(t * 3 + i * 0.5)
            gx = 60 + math.cos(angle) * dist
            gy = 40 + math.sin(angle) * dist + i * 3
            ghost_points.append((gx, gy))
        ghost_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(len(ghost_points) - 1):
            pygame.draw.line(ghost_surface, (150, 255, 255, 180), (int(ghost_points[i][0]), int(ghost_points[i][1])), 
                           (int(ghost_points[i+1][0]), int(ghost_points[i+1][1])), 12)
        s.blit(ghost_surface, (0, 0))
        
        # 怨灵面孔浮现（扭曲的脸）
        face_alpha = int(200 + 55 * math.sin(t * 2.5))
        face_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 脸部轮廓
        pygame.draw.circle(face_surface, (200, 255, 255, face_alpha), (60, 45), 12)
        # 空洞眼睛
        pygame.draw.circle(face_surface, (0, 0, 0, face_alpha), (55, 43), 3)
        pygame.draw.circle(face_surface, (0, 0, 0, face_alpha), (65, 43), 3)
        # 痛苦的嘴（O形）
        pygame.draw.circle(face_surface, (0, 0, 0, face_alpha), (60, 50), 4)
        s.blit(face_surface, (0, 0))
        
        # 灵魂锁链束缚（环绕锁链）
        chain_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            chain_angle = t * 2 + i * math.pi / 10
            chain_dist = 25 + 5 * math.sin(i * 0.5)
            chain_x = 60 + math.cos(chain_angle) * chain_dist
            chain_y = 50 + math.sin(chain_angle) * chain_dist
            # 锁链环节
            pygame.draw.circle(chain_surface, (180, 220, 220, 200), (int(chain_x), int(chain_y)), 2)
            if i > 0:
                prev_angle = t * 2 + (i - 1) * math.pi / 10
                prev_x = 60 + math.cos(prev_angle) * (25 + 5 * math.sin((i - 1) * 0.5))
                prev_y = 50 + math.sin(prev_angle) * (25 + 5 * math.sin((i - 1) * 0.5))
                pygame.draw.line(chain_surface, (180, 220, 220, 150), (int(prev_x), int(prev_y)), (int(chain_x), int(chain_y)), 1)
        s.blit(chain_surface, (0, 0))
        
        # 冤魂飘荡（小幽灵）
        for i in range(5):
            soul_angle = t * 1.5 + i * 2 * math.pi / 5
            soul_dist = 30 + 10 * math.sin(t * 2 + i)
            soul_x = 60 + math.cos(soul_angle) * soul_dist
            soul_y = 50 + math.sin(soul_angle) * soul_dist
            # 小幽灵轮廓
            soul_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(soul_surface, (180, 255, 255, 180), (int(soul_x), int(soul_y)), 5)
            # 哀伤表情
            pygame.draw.circle(soul_surface, (100, 200, 200, 180), (int(soul_x) - 2, int(soul_y) - 1), 1)
            pygame.draw.circle(soul_surface, (100, 200, 200, 180), (int(soul_x) + 2, int(soul_y) - 1), 1)
            s.blit(soul_surface, (0, 0))
        
        return s
    
    elif model_style == "sniper":
        # 幽灵狙击·远程收割 - 狙击手形态、精准射击、灵魂狙击、激光瞄准
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        # 主体：狙击手轮廓
        pygame.draw.rect(s, (0, 100, 200), (52, 42, 16, 22))
        pygame.draw.rect(s, (100, 200, 255), (52, 42, 16, 22), 2)
        
        # 狙击枪（长枪管）
        rifle_angle = math.sin(t * 2) * 0.2
        rifle_length = 30
        rifle_end_x = 60 + math.cos(rifle_angle) * rifle_length
        rifle_end_y = 50 + math.sin(rifle_angle) * rifle_length
        # 枪身
        pygame.draw.line(s, (80, 80, 100), (60, 50), (int(rifle_end_x), int(rifle_end_y)), 4)
        # 瞄准镜
        scope_x = 60 + math.cos(rifle_angle) * 10
        scope_y = 50 + math.sin(rifle_angle) * 10
        pygame.draw.circle(s, (50, 150, 255), (int(scope_x), int(scope_y)), 5)
        pygame.draw.circle(s, (100, 200, 255), (int(scope_x), int(scope_y)), 5, 2)
        
        # 激光瞄准线（红色激光）
        laser_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        laser_extended_x = rifle_end_x + math.cos(rifle_angle) * 50
        laser_extended_y = rifle_end_y + math.sin(rifle_angle) * 50
        pygame.draw.line(laser_surface, (255, 0, 0, 200), (int(rifle_end_x), int(rifle_end_y)), 
                        (int(laser_extended_x), int(laser_extended_y)), 1)
        # 激光点（闪烁）
        if int(t * 8) % 2 == 0:
            pygame.draw.circle(laser_surface, (255, 0, 0, 250), (int(laser_extended_x), int(laser_extended_y)), 3)
        s.blit(laser_surface, (0, 0))
        
        # 瞄准准星（十字线）
        target_x, target_y = int(laser_extended_x), int(laser_extended_y)
        crosshair_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(crosshair_surface, (255, 100, 100, 200), (target_x - 8, target_y), (target_x + 8, target_y), 1)
        pygame.draw.line(crosshair_surface, (255, 100, 100, 200), (target_x, target_y - 8), (target_x, target_y + 8), 1)
        pygame.draw.circle(crosshair_surface, (255, 100, 100, 200), (target_x, target_y), 6, 1)
        s.blit(crosshair_surface, (0, 0))
        
        # 灵魂狙击特效（能量波动）
        for i in range(3):
            energy_dist = 15 + i * 8 + (t * 20) % 15
            energy_x = 60 + math.cos(rifle_angle) * energy_dist
            energy_y = 50 + math.sin(rifle_angle) * energy_dist
            energy_alpha = int(200 * (1 - ((t * 20) % 15) / 15))
            energy_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(energy_surface, (50, 150, 255, energy_alpha), (int(energy_x), int(energy_y)), 4)
            s.blit(energy_surface, (0, 0))
        
        # 幽灵迷彩（半透明粒子）
        camo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            camo_x = 60 + int(10 * math.cos(t * 2 + i))
            camo_y = 50 + int(10 * math.sin(t * 2 + i))
            pygame.draw.circle(camo_surface, (50, 180, 255, 100), (camo_x, camo_y), 4)
        s.blit(camo_surface, (0, 0))
        
        return s
    
    elif model_style == "poltergeist":
        # 骚灵现象·灵异事件 - 物体悬浮飞舞、灵异力量、超自然现象
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：骚灵能量核心（不可见实体）
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_glow, (200, 100, 255, 180), (60, 50), int(15 * pulse))
        pygame.draw.circle(core_glow, (255, 150, 255, 120), (60, 50), int(20 * pulse))
        s.blit(core_glow, (0, 0))
        
        # 悬浮飞舞物体（多个物品旋转）
        objects = [
            # 书本
            lambda x, y: pygame.draw.rect(s, (150, 100, 50), (int(x) - 5, int(y) - 3, 10, 6)),
            # 椅子
            lambda x, y: pygame.draw.polygon(s, (100, 50, 0), [(int(x), int(y) - 5), (int(x) - 4, int(y) + 3), (int(x) + 4, int(y) + 3)]),
            # 灯具
            lambda x, y: pygame.draw.circle(s, (255, 255, 100), (int(x), int(y)), 4),
            # 花瓶
            lambda x, y: pygame.draw.polygon(s, (100, 200, 150), [(int(x), int(y) - 4), (int(x) - 3, int(y) + 4), (int(x) + 3, int(y) + 4)]),
        ]
        
        for i in range(8):
            obj_angle = t * 3 + i * math.pi / 4
            obj_dist = 25 + 10 * math.sin(t * 2 + i)
            obj_x = 60 + math.cos(obj_angle) * obj_dist
            obj_y = 50 + math.sin(obj_angle) * obj_dist + 5 * math.sin(t * 4 + i)  # 上下浮动
            # 绘制物体
            obj_func = objects[i % len(objects)]
            obj_func(obj_x, obj_y)
            # 物体旋转轨迹
            trail_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(trail_surface, (200, 100, 255, 100), (60, 50), (int(obj_x), int(obj_y)), 1)
            s.blit(trail_surface, (0, 0))
        
        # 灵异力量波动（能量圈）
        for i in range(3):
            wave_radius = 20 + i * 10 + (t * 30) % 20
            wave_alpha = int(180 * (1 - ((t * 30) % 20) / 20))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (220, 120, 255, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surface, (0, 0))
        
        # 超自然现象（扭曲空间）
        distortion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            dist_angle = i * math.pi / 6
            dist_inner = 10
            dist_outer = 18 + 5 * math.sin(t * 3 + i)
            inner_x = 60 + math.cos(dist_angle) * dist_inner
            inner_y = 50 + math.sin(dist_angle) * dist_inner
            outer_x = 60 + math.cos(dist_angle) * dist_outer
            outer_y = 50 + math.sin(dist_angle) * dist_outer
            pygame.draw.line(distortion_surface, (200, 100, 255, 150), (int(inner_x), int(inner_y)), (int(outer_x), int(outer_y)), 2)
        s.blit(distortion_surface, (0, 0))
        
        return s
    
    elif model_style == "fallen_angel":
        # 死亡天使·黑色羽翼 - 天使降临、黑色羽翼、天使审判、灵魂引渡
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.12 + 1
        
        # 主体：天使人形
        pygame.draw.ellipse(s, (30, 30, 50), (54, 38, 12, 28))
        pygame.draw.circle(s, (50, 50, 80), (60, 35), 5)  # 头部
        
        # 黑色羽翼展开（暗黑天使）
        wing_colors = [(20, 20, 40), (30, 30, 50), (50, 50, 80)]
        for side in [-1, 1]:
            for i in range(7):
                wing_angle = side * (math.pi / 4 + i * math.pi / 18) + math.sin(t * 1.5 + i) * 0.15
                wing_length = 28 + i * 2
                wing_x = 60 + math.cos(wing_angle) * wing_length
                wing_y = 50 + math.sin(wing_angle) * wing_length
                # 羽毛层次
                for layer in range(3):
                    feather_offset = layer * 2
                    fx = 60 + math.cos(wing_angle) * (wing_length - feather_offset)
                    fy = 50 + math.sin(wing_angle) * (wing_length - feather_offset)
                    color = wing_colors[layer]
                    pygame.draw.line(s, color, (60, 50), (int(fx), int(fy)), 4 - layer)
                    # 暗光效果
                    if layer == 0:
                        glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                        pygame.draw.line(glow, (100, 100, 180, 100), (60, 50), (int(fx), int(fy)), 6)
                        s.blit(glow, (0, 0))
        
        # 天使审判光环（暗紫色）
        halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(halo_surface, (100, 50, 150, 200), (60, 30), int(8 * pulse))
        pygame.draw.circle(halo_surface, (150, 100, 200, 150), (60, 30), int(10 * pulse), 2)
        s.blit(halo_surface, (0, 0))
        
        # 灵魂引渡（上升的灵魂）
        for i in range(6):
            soul_y = 70 - (t * 25 + i * 12) % 50
            soul_x = 60 + int(5 * math.sin(t * 3 + i))
            soul_alpha = int(200 * ((t * 25 + i * 12) % 50) / 50)
            soul_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 灵魂形状（小人形）
            pygame.draw.circle(soul_surface, (200, 200, 255, soul_alpha), (int(soul_x), int(soul_y)), 3)
            pygame.draw.line(soul_surface, (200, 200, 255, soul_alpha), (int(soul_x), int(soul_y) + 3), (int(soul_x), int(soul_y) + 8), 2)
            s.blit(soul_surface, (0, 0))
        
        # 审判之剑（光剑）
        sword_angle = math.sin(t * 2) * 0.3
        sword_x = 70 + math.cos(sword_angle) * 20
        sword_y = 55 + math.sin(sword_angle) * 20
        pygame.draw.line(s, (200, 200, 255), (60, 50), (int(sword_x), int(sword_y)), 3)
        # 剑刃发光
        sword_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(sword_glow, (200, 200, 255, 150), (60, 50), (int(sword_x), int(sword_y)), 6)
        s.blit(sword_glow, (0, 0))
        
        # 黑色羽毛飘落
        for i in range(10):
            feather_x = 40 + (t * 20 + i * 8) % 40
            feather_y = 30 + ((t * 30 + i * 6) % 50)
            pygame.draw.line(s, (30, 30, 50), (int(feather_x), int(feather_y)), (int(feather_x + 2), int(feather_y + 4)), 2)
        
        return s
    
    elif model_style == "void_hunter":
        # 虚空猎手·维度收割 - 跨维度狩猎、虚空镰刀、维度裂缝、收割一切
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：虚空猎手形态（扭曲的黑影）
        hunter_points = [
            (60, 30), (70, 45), (68, 60), (60, 68),
            (52, 60), (50, 45)
        ]
        # 虚空扭曲效果
        distorted_points = []
        for i, (x, y) in enumerate(hunter_points):
            distort_x = x + int(3 * math.sin(t * 4 + i))
            distort_y = y + int(3 * math.cos(t * 4 + i))
            distorted_points.append((distort_x, distort_y))
        pygame.draw.polygon(s, (50, 0, 80), distorted_points)
        pygame.draw.polygon(s, (100, 20, 150), distorted_points, 2)
        
        # 虚空镰刀（巨大紫色镰刀）
        scythe_angle = t * 1.5
        scythe_length = 35
        scythe_x = 60 + math.cos(scythe_angle) * scythe_length
        scythe_y = 50 + math.sin(scythe_angle) * scythe_length
        # 镰刀柄（虚空能量）
        for i in range(5):
            segment_ratio = i / 4
            seg_x = 60 + (scythe_x - 60) * segment_ratio
            seg_y = 50 + (scythe_y - 50) * segment_ratio
            pygame.draw.circle(s, (100, 20, 150), (int(seg_x), int(seg_y)), 2)
        pygame.draw.line(s, (80, 0, 120), (60, 50), (int(scythe_x), int(scythe_y)), 4)
        # 镰刀刃（弧形虚空刃）
        blade_points = [
            (scythe_x, scythe_y),
            (scythe_x + 18 * math.cos(scythe_angle + 1), scythe_y + 18 * math.sin(scythe_angle + 1)),
            (scythe_x + 15 * math.cos(scythe_angle + 2), scythe_y + 15 * math.sin(scythe_angle + 2)),
        ]
        pygame.draw.polygon(s, (150, 50, 180), [(int(p[0]), int(p[1])) for p in blade_points])
        blade_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(blade_glow, (180, 100, 220, 180), [(int(p[0]), int(p[1])) for p in blade_points])
        s.blit(blade_glow, (0, 0))
        
        # 维度裂缝（空间撕裂）
        for i in range(4):
            crack_angle = i * math.pi / 2 + t * 0.5
            crack_length = 20 + 10 * math.sin(t * 2 + i)
            crack_x = 60 + math.cos(crack_angle) * crack_length
            crack_y = 50 + math.sin(crack_angle) * crack_length
            # 裂缝线
            crack_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(crack_surface, (100, 0, 150, 220), (60, 50), (int(crack_x), int(crack_y)), 3)
            # 裂缝边缘发光
            pygame.draw.line(crack_surface, (180, 80, 220, 150), (60, 50), (int(crack_x), int(crack_y)), 5)
            s.blit(crack_surface, (0, 0))
            # 裂缝末端虚空能量
            pygame.draw.circle(s, (150, 50, 180), (int(crack_x), int(crack_y)), 5)
        
        # 跨维度粒子（虚空粒子飞散）
        for i in range(20):
            particle_angle = t * 3 + i * math.pi / 10
            particle_dist = 20 + 20 * (i / 20) + 8 * math.sin(t * 2 + i)
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            # 虚空粒子（方块）
            particle_size = 2 + int(2 * math.sin(t * 4 + i))
            pygame.draw.rect(s, (100, 20, 150), (int(px) - particle_size//2, int(py) - particle_size//2, particle_size, particle_size))
            # 粒子能量尾迹
            tail_x = px - math.cos(particle_angle) * 5
            tail_y = py - math.sin(particle_angle) * 5
            particle_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(particle_glow, (150, 50, 180, 150), (int(px), int(py)), (int(tail_x), int(tail_y)), 1)
            s.blit(particle_glow, (0, 0))
        
        # 虚空能量场（外圈脉冲）
        for i in range(3):
            void_radius = 25 + i * 10 + int(8 * pulse)
            void_alpha = int(150 * (1 - i / 3))
            void_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(void_surface, (100, 20, 150, void_alpha), (60, 50), void_radius, 2)
            s.blit(void_surface, (0, 0))
        
        return s
    
    # ========== Aurora专属涂装 ==========
    elif model_style == "goddess":
        # 极光至尊·女神真身 - 冰晶王座、极光天幕、冰雪风暴、世界冻结
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：女神形态
        pygame.draw.ellipse(s, (255, 240, 220), (54, 38, 12, 26))
        pygame.draw.circle(s, (255, 250, 240), (60, 35), 6)  # 头部
        # 女神皇冠
        crown_points = [
            (55, 30), (58, 25), (60, 23), (62, 25), (65, 30)
        ]
        pygame.draw.polygon(s, (255, 255, 220), crown_points)
        pygame.draw.polygon(s, (255, 255, 255), crown_points, 2)
        
        # 冰晶王座（巨大结构）
        throne_points = [
            (40, 65), (45, 45), (55, 48), (60, 50),
            (65, 48), (75, 45), (80, 65)
        ]
        pygame.draw.polygon(s, (200, 240, 255), throne_points)
        pygame.draw.polygon(s, (255, 255, 255), throne_points, 2)
        # 王座细节（冰晶）
        for tx, ty in [(45, 50), (75, 50), (48, 58), (72, 58)]:
            pygame.draw.polygon(s, (220, 255, 255), [
                (tx, ty - 4), (tx + 3, ty), (tx, ty + 4), (tx - 3, ty)
            ])
        
        # 极光天幕覆盖（波浪光带）
        aurora_colors = [
            (100, 255, 200), (150, 255, 220), (200, 255, 240)
        ]
        for layer in range(3):
            aurora_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            for i in range(10):
                wave_x = 30 + i * 6
                wave_y = 20 + layer * 8 + int(5 * math.sin(t * 2 + i * 0.5 + layer))
                next_x = 30 + (i + 1) * 6
                next_y = 20 + layer * 8 + int(5 * math.sin(t * 2 + (i + 1) * 0.5 + layer))
                pygame.draw.line(aurora_surface, (*aurora_colors[layer], 180), (wave_x, wave_y), (next_x, next_y), 4)
            s.blit(aurora_surface, (0, 0))
        
        # 冰雪风暴（环绕冰晶）
        for i in range(20):
            snow_angle = t * 3 + i * math.pi / 10
            snow_dist = 25 + 20 * (i / 20) + 5 * math.sin(t * 2 + i)
            snow_x = 60 + math.cos(snow_angle) * snow_dist
            snow_y = 50 + math.sin(snow_angle) * snow_dist
            # 雪花
            pygame.draw.circle(s, (255, 255, 255), (int(snow_x), int(snow_y)), 2)
            # 六角雪花细节
            for spike in range(6):
                spike_angle = snow_angle + spike * math.pi / 3
                spike_x = snow_x + math.cos(spike_angle) * 3
                spike_y = snow_y + math.sin(spike_angle) * 3
                pygame.draw.line(s, (220, 240, 255), (int(snow_x), int(snow_y)), (int(spike_x), int(spike_y)), 1)
        
        # 世界冻结效果（扩散冰冻圈）
        for i in range(3):
            freeze_radius = 30 + i * 12 + int(8 * pulse)
            freeze_alpha = int(120 * (1 - i / 3))
            freeze_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(freeze_surface, (200, 240, 255, freeze_alpha), (60, 50), freeze_radius, 3)
            s.blit(freeze_surface, (0, 0))
        
        # 神圣光环
        halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(halo_surface, (255, 255, 255, 200), (60, 30), int(10 * pulse))
        s.blit(halo_surface, (0, 0))
        
        return s
    
    elif model_style == "nebula":
        # 星云之心·宇宙梦境 - 星云纹理、星尘粒子、宇宙梦境
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：星云核心
        pygame.draw.circle(s, (100, 50, 180), (60, 50), 12)
        pygame.draw.circle(s, (150, 100, 255), (60, 50), 12, 2)
        
        # 星云纹理流动（多层渐变云）
        nebula_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for layer in range(4):
            for i in range(12):
                nebula_angle = t * 1.5 + i * math.pi / 6 + layer * math.pi / 8
                nebula_dist = 15 + layer * 8 + 5 * math.sin(t * 2 + i)
                nx = 60 + math.cos(nebula_angle) * nebula_dist
                ny = 50 + math.sin(nebula_angle) * nebula_dist
                # 星云颜色（紫-蓝-粉渐变）
                color_r = 150 + int(50 * math.sin(t + i))
                color_g = 100 + int(50 * math.sin(t + i + 2))
                color_b = 255
                nebula_size = 10 - layer * 2
                nebula_alpha = 200 - layer * 40
                pygame.draw.circle(nebula_surface, (color_r, color_g, color_b, nebula_alpha), (int(nx), int(ny)), nebula_size)
        s.blit(nebula_surface, (0, 0))
        
        # 星尘粒子暴雨（大量小星星）
        for i in range(40):
            star_angle = t * 2 + i * math.pi / 20
            star_dist = 20 + 25 * (i / 40) + 5 * math.sin(t * 3 + i)
            star_x = 60 + math.cos(star_angle) * star_dist
            star_y = 50 + math.sin(star_angle) * star_dist
            # 闪烁星尘
            if (int(t * 12) + i) % 5 < 3:
                star_brightness = int(200 + 55 * math.sin(t * 4 + i))
                pygame.draw.circle(s, (180, 120, 255, star_brightness), (int(star_x), int(star_y)), 2)
                # 星光
                star_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(star_glow, (200, 150, 255, 120), (int(star_x), int(star_y)), 4)
                s.blit(star_glow, (0, 0))
        
        # 宇宙梦境显现（流动光带）
        dream_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            dream_angle = t * 3 + i * math.pi / 4
            dream_inner = 18
            dream_outer = 35
            inner_x = 60 + math.cos(dream_angle) * dream_inner
            inner_y = 50 + math.sin(dream_angle) * dream_inner
            outer_x = 60 + math.cos(dream_angle) * dream_outer
            outer_y = 50 + math.sin(dream_angle) * dream_outer
            # 梦境光束
            pygame.draw.line(dream_surface, (180, 120, 255, 150), (int(inner_x), int(inner_y)), (int(outer_x), int(outer_y)), 3)
        s.blit(dream_surface, (0, 0))
        
        return s
    
    elif model_style == "ice_queen":
        # 冰雪女王·永冻领域 - 冰晶王冠、冰霜领域、永冻统治
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：女王轮廓
        pygame.draw.ellipse(s, (200, 230, 255), (54, 40, 12, 24))
        pygame.draw.circle(s, (220, 240, 255), (60, 36), 5)
        
        # 冰晶王冠高耸（多层尖塔）
        crown_layers = [
            # 中央最高塔
            [(60, 18), (58, 28), (62, 28)],
            # 左右副塔
            [(54, 22), (52, 30), (56, 30)],
            [(66, 22), (64, 30), (68, 30)],
            # 外侧小塔
            [(50, 26), (48, 32), (52, 32)],
            [(70, 26), (68, 32), (72, 32)],
        ]
        for tower in crown_layers:
            pygame.draw.polygon(s, (200, 240, 255), tower)
            pygame.draw.polygon(s, (255, 255, 255), tower, 2)
            # 塔尖宝石
            tip_x = tower[0][0]
            tip_y = tower[0][1]
            pygame.draw.circle(s, (150, 220, 255), (tip_x, tip_y), 2)
        
        # 冰霜领域扩张（六边形冰域）
        hexagon_points = []
        for i in range(6):
            hex_angle = i * math.pi / 3 + t * 0.5
            hex_dist = 28 + int(8 * pulse)
            hx = 60 + math.cos(hex_angle) * hex_dist
            hy = 50 + math.sin(hex_angle) * hex_dist
            hexagon_points.append((int(hx), int(hy)))
        frost_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(frost_surface, (200, 240, 255, 150), hexagon_points)
        pygame.draw.polygon(frost_surface, (220, 255, 255, 200), hexagon_points, 3)
        s.blit(frost_surface, (0, 0))
        
        # 冰晶飘落（细碎冰晶）
        for i in range(30):
            ice_x = 30 + (t * 20 + i * 3) % 60
            ice_y = 20 + ((t * 25 + i * 4) % 60)
            # 小冰晶（菱形）
            ice_points = [
                (ice_x, ice_y - 2),
                (ice_x + 2, ice_y),
                (ice_x, ice_y + 2),
                (ice_x - 2, ice_y),
            ]
            pygame.draw.polygon(s, (210, 250, 255), [(int(p[0]), int(p[1])) for p in ice_points])
        
        # 永冻统治气息（冰冻波纹）
        for i in range(3):
            freeze_radius = 25 + i * 10 + (t * 25) % 15
            freeze_alpha = int(180 * (1 - ((t * 25) % 15) / 15))
            freeze_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(freeze_surface, (200, 240, 255, freeze_alpha), (60, 50), int(freeze_radius), 2)
            s.blit(freeze_surface, (0, 0))
        
        # 冰权杖（女王权杖）
        staff_x = 48 + int(3 * math.sin(t * 2))
        staff_y = 55
        pygame.draw.line(s, (180, 220, 255), (staff_x, staff_y), (staff_x, staff_y + 20), 3)
        # 权杖顶部宝石
        pygame.draw.circle(s, (150, 220, 255), (staff_x, staff_y), 5)
        staff_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(staff_glow, (200, 240, 255, 200), (staff_x, staff_y), int(8 * pulse))
        s.blit(staff_glow, (0, 0))
        
        return s
    
    # Duplicate earlier "rainbow" implementation removed; Prism's `rainbow` implemented later.
    
    elif model_style == "prism":
        # 棱镜光辉·折射万象 - 水晶棱镜、光芒折射、璀璨夺目
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：水晶棱镜结构（六面体）
        prism_points = [
            (60, 35),  # 顶点
            (70, 45), (68, 60), (60, 65),
            (52, 60), (50, 45)
        ]
        pygame.draw.polygon(s, (180, 220, 255), prism_points)
        pygame.draw.polygon(s, (220, 255, 255), prism_points, 3)
        
        # 棱镜内部折射面
        for i in range(6):
            facet_angle = i * math.pi / 3
            fx = 60 + math.cos(facet_angle) * 8
            fy = 50 + math.sin(facet_angle) * 8
            pygame.draw.line(s, (200, 240, 255), (60, 50), (int(fx), int(fy)), 2)
        
        # 光芒无限折射（多重反射光线）
        refraction_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (139, 0, 255)]
        
        for i in range(21):
            ray_angle = t * 3 + i * math.pi / 10.5
            ray_start_dist = 12
            ray_end_dist = 40 + 5 * math.sin(t * 2 + i)
            start_x = 60 + math.cos(ray_angle) * ray_start_dist
            start_y = 50 + math.sin(ray_angle) * ray_start_dist
            end_x = 60 + math.cos(ray_angle) * ray_end_dist
            end_y = 50 + math.sin(ray_angle) * ray_end_dist
            # 彩色折射光
            color = rainbow_colors[i % 7]
            pygame.draw.line(refraction_surface, (*color, 180), (int(start_x), int(start_y)), (int(end_x), int(end_y)), 2)
            # 次级折射（分支）
            if i % 3 == 0:
                branch_angle = ray_angle + math.pi / 6
                branch_x = end_x + math.cos(branch_angle) * 10
                branch_y = end_y + math.sin(branch_angle) * 10
                pygame.draw.line(refraction_surface, (*color, 120), (int(end_x), int(end_y)), (int(branch_x), int(branch_y)), 1)
        s.blit(refraction_surface, (0, 0))
        
        # 万象光辉（旋转彩色光点）
        for i in range(24):
            light_angle = t * 4 + i * math.pi / 12
            light_dist = 25 + 10 * math.sin(t * 3 + i * 0.5)
            lx = 60 + math.cos(light_angle) * light_dist
            ly = 50 + math.sin(light_angle) * light_dist
            color = rainbow_colors[i % 7]
            pygame.draw.circle(s, color, (int(lx), int(ly)), 3)
            # 光辉闪耀
            light_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(light_glow, (*color, 150), (int(lx), int(ly)), 5)
            s.blit(light_glow, (0, 0))
        
        # 璀璨核心（中心脉冲）
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_glow, (255, 255, 255, 220), (60, 50), int(12 * pulse))
        pygame.draw.circle(core_glow, (220, 255, 255, 150), (60, 50), int(18 * pulse))
        s.blit(core_glow, (0, 0))
        
        return s
    
    elif model_style == "sakura":
        # 樱花女神·春之降临 - 樱花暴雨、粉色花瓣海洋、生命绽放
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：女神形态
        pygame.draw.ellipse(s, (255, 200, 220), (54, 40, 12, 24))
        pygame.draw.circle(s, (255, 220, 230), (60, 36), 5)
        
        # 樱花王冠
        for i in range(5):
            petal_angle = i * 2 * math.pi / 5 + t * 2
            petal_x = 60 + math.cos(petal_angle) * 8
            petal_y = 30 + math.sin(petal_angle) * 8
            # 五瓣樱花
            for j in range(5):
                sub_angle = petal_angle + j * 2 * math.pi / 5
                sub_x = petal_x + math.cos(sub_angle) * 3
                sub_y = petal_y + math.sin(sub_angle) * 3
                pygame.draw.circle(s, (255, 180, 200), (int(sub_x), int(sub_y)), 2)
        
        # 樱花暴雨飞舞（大量花瓣）
        for i in range(60):
            petal_x = 20 + (t * 15 + i * 2) % 80
            petal_y = 10 + ((t * 20 + i * 3) % 90)
            petal_rotation = (t * 5 + i) % (2 * math.pi)
            # 五瓣花瓣
            for j in range(5):
                petal_angle = petal_rotation + j * 2 * math.pi / 5
                px = petal_x + math.cos(petal_angle) * 3
                py = petal_y + math.sin(petal_angle) * 3
                pygame.draw.circle(s, (255, 180, 200), (int(px), int(py)), 2)
            # 花瓣中心
            pygame.draw.circle(s, (255, 200, 220), (int(petal_x), int(petal_y)), 1)
        
        # 粉色花瓣海洋（环绕飘散）
        ocean_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(30):
            ocean_angle = t * 2 + i * math.pi / 15
            ocean_dist = 25 + 15 * (i / 30) + 5 * math.sin(t * 3 + i)
            ocean_x = 60 + math.cos(ocean_angle) * ocean_dist
            ocean_y = 50 + math.sin(ocean_angle) * ocean_dist
            # 飘散花瓣（椭圆形）
            pygame.draw.ellipse(ocean_surface, (255, 180, 200, 200), (int(ocean_x) - 3, int(ocean_y) - 2, 6, 4))
        s.blit(ocean_surface, (0, 0))
        
        # 春天生命气息（绿色生机）
        life_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            life_angle = t * 1.5 + i * math.pi / 6
            life_dist = 20 + 10 * math.sin(t * 2 + i)
            life_x = 60 + math.cos(life_angle) * life_dist
            life_y = 50 + math.sin(life_angle) * life_dist
            # 嫩芽（小绿点）
            pygame.draw.circle(life_surface, (150, 255, 150, 180), (int(life_x), int(life_y)), 2)
        s.blit(life_surface, (0, 0))
        
        # 樱花树枝（女神背后）
        branch_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for side in [-1, 1]:
            branch_x = 60 + side * 15
            pygame.draw.line(branch_surface, (139, 90, 60, 200), (60, 50), (branch_x, 30), 3)
            pygame.draw.line(branch_surface, (139, 90, 60, 200), (60, 50), (branch_x, 70), 3)
            # 枝上樱花
            for i in range(3):
                flower_x = 60 + side * (5 + i * 5)
                flower_y = 40 + i * 10
                for j in range(5):
                    f_angle = j * 2 * math.pi / 5 + t
                    fx = flower_x + math.cos(f_angle) * 2
                    fy = flower_y + math.sin(f_angle) * 2
                    pygame.draw.circle(branch_surface, (255, 180, 200, 220), (int(fx), int(fy)), 2)
        s.blit(branch_surface, (0, 0))
        
        return s
    
    elif model_style == "celestial":
        # 天界使者·神圣降临 - 天使光环、圣洁羽翼、天界之门、神圣力量
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：天使形态
        pygame.draw.ellipse(s, (255, 250, 240), (54, 38, 12, 26))
        pygame.draw.circle(s, (255, 255, 255), (60, 35), 5)
        
        # 天使光环闪耀（头顶）
        halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(halo_surface, (255, 255, 255, 220), (60, 25), int(10 * pulse))
        pygame.draw.circle(halo_surface, (255, 250, 240, 180), (60, 25), int(12 * pulse), 2)
        # 光环射线
        for i in range(12):
            ray_angle = t * 2 + i * math.pi / 6
            ray_x = 60 + math.cos(ray_angle) * 12
            ray_y = 25 + math.sin(ray_angle) * 12
            pygame.draw.line(halo_surface, (255, 255, 255, 200), (60, 25), (int(ray_x), int(ray_y)), 2)
        s.blit(halo_surface, (0, 0))
        
        # 圣洁羽翼展开（巨大白色翅膀）
        wing_colors = [(255, 255, 255), (255, 252, 245), (255, 250, 240)]
        for side in [-1, 1]:
            for i in range(8):
                wing_angle = side * (math.pi / 4 + i * math.pi / 20) + math.sin(t * 1.5 + i) * 0.1
                wing_length = 32 + i * 2
                wing_x = 60 + math.cos(wing_angle) * wing_length
                wing_y = 50 + math.sin(wing_angle) * wing_length
                # 多层羽毛
                for layer in range(3):
                    feather_offset = layer * 2
                    fx = 60 + math.cos(wing_angle) * (wing_length - feather_offset)
                    fy = 50 + math.sin(wing_angle) * (wing_length - feather_offset)
                    color = wing_colors[layer]
                    pygame.draw.line(s, color, (60, 50), (int(fx), int(fy)), 5 - layer)
                    # 羽毛发光
                    if layer == 0:
                        feather_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
                        pygame.draw.line(feather_glow, (255, 255, 255, 150), (60, 50), (int(fx), int(fy)), 7)
                        s.blit(feather_glow, (0, 0))
        
        # 天界之门打开（背后光门）
        gate_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        gate_width = int(20 * pulse)
        gate_height = 35
        pygame.draw.rect(gate_surface, (255, 255, 255, 180), (60 - gate_width//2, 30, gate_width, gate_height))
        # 门框光芒
        pygame.draw.rect(gate_surface, (255, 250, 240, 220), (60 - gate_width//2 - 2, 28, gate_width + 4, gate_height + 4), 3)
        s.blit(gate_surface, (0, 0))
        
        # 神圣力量（圣光粒子）
        for i in range(30):
            holy_angle = t * 3 + i * math.pi / 15
            holy_dist = 20 + 20 * (i / 30) + 5 * math.sin(t * 2 + i)
            holy_x = 60 + math.cos(holy_angle) * holy_dist
            holy_y = 50 + math.sin(holy_angle) * holy_dist
            pygame.draw.circle(s, (255, 255, 255), (int(holy_x), int(holy_y)), 2)
            # 圣光
            holy_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(holy_glow, (255, 255, 255, 180), (int(holy_x), int(holy_y)), 4)
            s.blit(holy_glow, (0, 0))
        
        # 神圣十字（祝福标记）
        cross_size = int(15 * pulse)
        cross_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(cross_surface, (255, 255, 255, 200), (60, 50 - cross_size), (60, 50 + cross_size), 3)
        pygame.draw.line(cross_surface, (255, 255, 255, 200), (60 - cross_size, 50), (60 + cross_size, 50), 3)
        s.blit(cross_surface, (0, 0))
        
        # 圣洁光环（外圈）
        for i in range(3):
            aura_radius = 30 + i * 10 + int(8 * pulse)
            aura_alpha = int(120 * (1 - i / 3))
            aura_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(aura_surface, (255, 255, 255, aura_alpha), (60, 50), aura_radius, 2)
            s.blit(aura_surface, (0, 0))
        
        return s
    
    # ========== Crimson专属涂装 ==========
    elif model_style == "blood":
        # 绯红之刃·血月降临 - 血色光芒、血雾弥漫、血液飞溅、嗜血气息
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：刀刃形态
        blade_points = [(60, 30), (68, 48), (64, 65), (60, 68), (56, 65), (52, 48)]
        pygame.draw.polygon(s, (150, 0, 0), blade_points)
        pygame.draw.polygon(s, (200, 20, 20), blade_points, 2)
        
        # 血色光芒笼罩（红色辉光）
        blood_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(blood_glow, (180, 0, 0, 180), (60, 50), int(25 * pulse))
        pygame.draw.circle(blood_glow, (200, 30, 30, 120), (60, 50), int(32 * pulse))
        s.blit(blood_glow, (0, 0))
        
        # 血雾弥漫升腾（环绕雾气）
        fog_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            fog_angle = t * 1.5 + i * math.pi / 7.5
            fog_dist = 20 + 10 * math.sin(t * 2 + i)
            fog_x = 60 + math.cos(fog_angle) * fog_dist
            fog_y = 50 + math.sin(fog_angle) * fog_dist
            fog_size = 8 + int(4 * math.sin(t * 3 + i))
            pygame.draw.circle(fog_surface, (150, 0, 0, 150), (int(fog_x), int(fog_y)), fog_size)
        s.blit(fog_surface, (0, 0))
        
        # 血液飞溅特效（四周飞溅）
        for i in range(20):
            splash_angle = t * 3 + i * math.pi / 10
            splash_dist = 25 + 15 * (i / 20)
            splash_x = 60 + math.cos(splash_angle) * splash_dist
            splash_y = 50 + math.sin(splash_angle) * splash_dist
            # 血滴
            pygame.draw.circle(s, (200, 20, 20), (int(splash_x), int(splash_y)), 3)
            # 血迹轨迹
            trail_x = splash_x - math.cos(splash_angle) * 5
            trail_y = splash_y - math.sin(splash_angle) * 5
            pygame.draw.line(s, (180, 10, 10), (int(splash_x), int(splash_y)), (int(trail_x), int(trail_y)), 2)
        
        # 嗜血气息（红色波纹）
        for i in range(3):
            wave_radius = (t * 40 + i * 20) % 60
            wave_alpha = int(180 * (1 - wave_radius / 60))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (200, 0, 0, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surface, (0, 0))
        
        return s
    
    elif model_style == "samurai":
        # 绯红武士·血刃斩魂 - 武士刀、武士道、快速斩击、一击毙命
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.15 + 1
        
        # 主体：武士轮廓
        pygame.draw.rect(s, (150, 0, 0), (52, 40, 16, 26))
        pygame.draw.rect(s, (200, 0, 0), (52, 40, 16, 26), 2)
        # 武士头盔
        helmet_points = [(60, 35), (65, 40), (55, 40)]
        pygame.draw.polygon(s, (100, 0, 0), helmet_points)
        
        # 武士刀闪耀（长刀）
        katana_angle = math.sin(t * 4) * 0.5 + math.pi / 4
        katana_length = 35
        katana_x = 60 + math.cos(katana_angle) * katana_length
        katana_y = 50 + math.sin(katana_angle) * katana_length
        # 刀身
        pygame.draw.line(s, (200, 200, 220), (60, 50), (int(katana_x), int(katana_y)), 4)
        # 刀刃发光
        blade_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(blade_glow, (255, 255, 255, 200), (60, 50), (int(katana_x), int(katana_y)), 6)
        s.blit(blade_glow, (0, 0))
        # 刀柄（金色护手）
        pygame.draw.circle(s, (255, 215, 0), (60, 50), 5)
        pygame.draw.circle(s, (220, 180, 0), (60, 50), 5, 2)
        
        # 快速斩击轨迹（残影）
        for i in range(5):
            trail_angle = katana_angle + (i - 2) * 0.2
            trail_alpha = int(200 - i * 40)
            trail_x = 60 + math.cos(trail_angle) * katana_length
            trail_y = 50 + math.sin(trail_angle) * katana_length
            trail_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(trail_surface, (255, 100, 100, trail_alpha), (60, 50), (int(trail_x), int(trail_y)), 3)
            s.blit(trail_surface, (0, 0))
        
        # 血刃特效（刀刃滴血）
        for i in range(3):
            blood_dist = 20 + i * 8
            blood_x = 60 + math.cos(katana_angle) * blood_dist
            blood_y = 50 + math.sin(katana_angle) * blood_dist
            drop_offset = int(5 * math.sin(t * 5 + i))
            pygame.draw.circle(s, (200, 0, 0), (int(blood_x), int(blood_y + drop_offset)), 2)
        
        # 武士道精神（红色气息）
        spirit_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            spirit_angle = t * 2 + i * math.pi / 4
            spirit_dist = 25 + 8 * math.sin(t * 2 + i)
            spirit_x = 60 + math.cos(spirit_angle) * spirit_dist
            spirit_y = 50 + math.sin(spirit_angle) * spirit_dist
            pygame.draw.circle(spirit_surface, (200, 0, 0, 150), (int(spirit_x), int(spirit_y)), 4)
        s.blit(spirit_surface, (0, 0))
        
        return s
    
    elif model_style == "demon":
        # 血魔降世·魔王降临 - 血魔之翼、血色魔纹、魔王形态、血之君主
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：魔王身躯
        demon_points = [(60, 32), (70, 48), (66, 62), (60, 68), (54, 62), (50, 48)]
        pygame.draw.polygon(s, (80, 0, 0), demon_points)
        pygame.draw.polygon(s, (120, 0, 0), demon_points, 3)
        
        # 魔王头部（角）
        # 左角
        pygame.draw.line(s, (100, 0, 0), (55, 32), (50, 22), 4)
        pygame.draw.circle(s, (120, 0, 0), (50, 22), 3)
        # 右角
        pygame.draw.line(s, (100, 0, 0), (65, 32), (70, 22), 4)
        pygame.draw.circle(s, (120, 0, 0), (70, 22), 3)
        
        # 血魔之翼展开（蝙蝠翼）
        wing_offset = int(10 * math.sin(t * 2))
        for side in [-1, 1]:
            # 翼膜
            wing_points = [
                (60, 48),
                (60 + side * (20 + wing_offset), 40),
                (60 + side * (25 + wing_offset), 50),
                (60 + side * (22 + wing_offset), 60),
                (60, 58)
            ]
            wing_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(wing_surface, (100, 0, 0, 200), wing_points)
            pygame.draw.polygon(wing_surface, (150, 10, 10, 220), wing_points, 2)
            s.blit(wing_surface, (0, 0))
            # 翼骨
            for i in range(3):
                bone_x = 60 + side * (18 + wing_offset + i * 3)
                bone_y = 42 + i * 8
                pygame.draw.line(s, (120, 0, 0), (60, 48), (bone_x, bone_y), 2)
        
        # 血色魔纹遍布（发光符文）
        rune_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            rune_angle = t * 2 + i * math.pi / 6
            rune_dist = 18 + 8 * math.sin(t * 3 + i)
            rune_x = 60 + math.cos(rune_angle) * rune_dist
            rune_y = 50 + math.sin(rune_angle) * rune_dist
            # 魔纹符号（十字）
            if (int(t * 6) + i) % 3 == 0:
                pygame.draw.line(rune_surface, (200, 0, 0, 220), (int(rune_x) - 3, int(rune_y)), (int(rune_x) + 3, int(rune_y)), 2)
                pygame.draw.line(rune_surface, (200, 0, 0, 220), (int(rune_x), int(rune_y) - 3), (int(rune_x), int(rune_y) + 3), 2)
        s.blit(rune_surface, (0, 0))
        
        # 血之君主气息（深红光环）
        for i in range(3):
            aura_radius = 28 + i * 10 + int(8 * pulse)
            aura_alpha = int(150 * (1 - i / 3))
            aura_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(aura_surface, (120, 0, 0, aura_alpha), (60, 50), aura_radius, 3)
            s.blit(aura_surface, (0, 0))
        
        return s
    
    elif model_style == "inferno":
        # 地狱烈焰·炼狱之火 - 地狱火海、烈焰席卷、炼狱高温、焚毁世界
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：火焰核心
        pygame.draw.circle(s, (200, 50, 0), (60, 50), 15)
        pygame.draw.circle(s, (255, 100, 0), (60, 50), 15, 2)
        
        # 地狱火海燃烧（底部火焰）
        inferno_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            fire_x = 30 + i * 3
            fire_y = 70 + int(10 * math.sin(t * 4 + i * 0.5))
            fire_height = 20 + 10 * math.sin(t * 5 + i)
            # 火焰柱
            pygame.draw.polygon(inferno_surface, (255, 80, 0, 220), [
                (fire_x, fire_y),
                (fire_x - 3, fire_y - fire_height),
                (fire_x + 3, fire_y - fire_height)
            ])
            # 火焰内核
            pygame.draw.polygon(inferno_surface, (255, 150, 0, 180), [
                (fire_x, fire_y),
                (fire_x - 2, fire_y - fire_height * 0.7),
                (fire_x + 2, fire_y - fire_height * 0.7)
            ])
        s.blit(inferno_surface, (0, 0))
        
        # 烈焰席卷一切（环绕火焰）
        for i in range(16):
            flame_angle = t * 4 + i * math.pi / 8
            flame_dist = 25 + 10 * math.sin(t * 3 + i)
            flame_x = 60 + math.cos(flame_angle) * flame_dist
            flame_y = 50 + math.sin(flame_angle) * flame_dist
            flame_size = 8 + int(4 * pulse)
            # 火球
            flame_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(flame_surface, (255, 100, 0, 220), (int(flame_x), int(flame_y)), flame_size)
            pygame.draw.circle(flame_surface, (255, 150, 0, 180), (int(flame_x), int(flame_y)), flame_size - 2)
            s.blit(flame_surface, (0, 0))
        
        # 炼狱高温（热浪扭曲）
        heat_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            heat_radius = 20 + i * 8 + (t * 30) % 20
            heat_alpha = int(150 * (1 - ((t * 30) % 20) / 20))
            pygame.draw.circle(heat_surface, (255, 120, 0, heat_alpha), (60, 50), int(heat_radius), 2)
        s.blit(heat_surface, (0, 0))
        
        # 焚毁世界（火焰爆发）
        explosion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            exp_angle = i * math.pi / 6 + t * 2
            exp_dist = 30 + 15 * math.sin(t * 2.5 + i)
            exp_x = 60 + math.cos(exp_angle) * exp_dist
            exp_y = 50 + math.sin(exp_angle) * exp_dist
            # 爆炸火花
            pygame.draw.circle(explosion_surface, (255, 150, 0, 200), (int(exp_x), int(exp_y)), 5)
            pygame.draw.circle(explosion_surface, (255, 200, 100, 150), (int(exp_x), int(exp_y)), 8)
        s.blit(explosion_surface, (0, 0))
        
        return s
    
    elif model_style == "rose":
        # 血玫瑰·致命之美 - 血红玫瑰、带刺玫瑰丛、美丽致命、芬芳杀机
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：中心大玫瑰
        center_x, center_y = 60, 45
        # 玫瑰花瓣（多层）
        for layer in range(4):
            petal_count = 6 + layer * 2
            petal_dist = 6 + layer * 4
            for i in range(petal_count):
                petal_angle = t * 0.5 + i * 2 * math.pi / petal_count + layer * 0.3
                petal_x = center_x + math.cos(petal_angle) * petal_dist
                petal_y = center_y + math.sin(petal_angle) * petal_dist
                # 花瓣（椭圆）
                petal_color = (200 - layer * 20, 50, 80)
                pygame.draw.ellipse(s, petal_color, (int(petal_x) - 4, int(petal_y) - 3, 8, 6))
        # 花心
        pygame.draw.circle(s, (150, 30, 60), (center_x, center_y), 4)
        
        # 带刺玫瑰丛（藤蔓+刺）
        vine_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            vine_angle = i * 2 * math.pi / 5 + t * 0.3
            vine_length = 30
            # 藤蔓主干（波浪线）
            for j in range(8):
                segment_dist = j * 4
                segment_x = center_x + math.cos(vine_angle) * segment_dist + math.sin(t * 3 + j) * 3
                segment_y = center_y + math.sin(vine_angle) * segment_dist + math.cos(t * 3 + j) * 3
                next_dist = (j + 1) * 4
                next_x = center_x + math.cos(vine_angle) * next_dist + math.sin(t * 3 + j + 1) * 3
                next_y = center_y + math.sin(vine_angle) * next_dist + math.cos(t * 3 + j + 1) * 3
                pygame.draw.line(vine_surface, (100, 50, 0, 200), (int(segment_x), int(segment_y)), (int(next_x), int(next_y)), 3)
                # 刺（每隔一段）
                if j % 2 == 0:
                    thorn_angle = vine_angle + math.pi / 2
                    thorn_x = segment_x + math.cos(thorn_angle) * 5
                    thorn_y = segment_y + math.sin(thorn_angle) * 5
                    pygame.draw.line(vine_surface, (80, 0, 0, 220), (int(segment_x), int(segment_y)), (int(thorn_x), int(thorn_y)), 2)
        s.blit(vine_surface, (0, 0))
        
        # 血红玫瑰绽放（环绕小玫瑰）
        for i in range(8):
            rose_angle = t * 1.5 + i * math.pi / 4
            rose_dist = 28 + 8 * math.sin(t * 2 + i)
            rose_x = center_x + math.cos(rose_angle) * rose_dist
            rose_y = center_y + math.sin(rose_angle) * rose_dist
            # 小玫瑰
            for j in range(5):
                small_petal_angle = rose_angle + j * 2 * math.pi / 5
                small_petal_x = rose_x + math.cos(small_petal_angle) * 3
                small_petal_y = rose_y + math.sin(small_petal_angle) * 3
                pygame.draw.circle(s, (200, 50, 80), (int(small_petal_x), int(small_petal_y)), 2)
        
        # 芬芳杀机（粉红迷雾）
        mist_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            mist_x = center_x + int(25 * math.cos(t * 2 + i * 0.5))
            mist_y = center_y + int(25 * math.sin(t * 2 + i * 0.5))
            pygame.draw.circle(mist_surface, (220, 70, 100, 100), (mist_x, mist_y), 8)
        s.blit(mist_surface, (0, 0))
        
        return s
    
    elif model_style == "dragon":
        # 血龙咆哮·龙息焚天 - 血龙形态、龙息喷涌、血色龙鳞、龙威镇世
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：血龙头部
        dragon_head = [(60, 35), (70, 45), (68, 52), (60, 55), (52, 52), (50, 45)]
        pygame.draw.polygon(s, (180, 0, 0), dragon_head)
        pygame.draw.polygon(s, (220, 0, 0), dragon_head, 3)
        
        # 龙角
        pygame.draw.line(s, (200, 0, 0), (55, 35), (50, 25), 4)
        pygame.draw.circle(s, (255, 215, 0), (50, 25), 3)
        pygame.draw.line(s, (200, 0, 0), (65, 35), (70, 25), 4)
        pygame.draw.circle(s, (255, 215, 0), (70, 25), 3)
        
        # 龙眼（金色发光）
        for eye_x in [54, 66]:
            pygame.draw.circle(s, (255, 215, 0), (eye_x, 43), 4)
            pygame.draw.circle(s, (200, 0, 0), (eye_x, 43), 2)
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (255, 215, 0, 180), (eye_x, 43), int(6 * pulse))
            s.blit(eye_glow, (0, 0))
        
        # 龙身（蛇形）
        body_segments = []
        for i in range(10):
            segment_angle = t * 2 + i * math.pi / 5
            segment_dist = 15 + i * 2
            seg_x = 60 + math.cos(segment_angle) * segment_dist
            seg_y = 55 + i * 3
            body_segments.append((seg_x, seg_y))
        for i in range(len(body_segments) - 1):
            pygame.draw.line(s, (180, 0, 0), (int(body_segments[i][0]), int(body_segments[i][1])), 
                           (int(body_segments[i+1][0]), int(body_segments[i+1][1])), 10)
        
        # 血色龙鳞闪耀
        scale_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(25):
            scale_angle = t * 2 + i * math.pi / 12.5
            scale_dist = 15 + 20 * (i / 25)
            scale_x = 60 + math.cos(scale_angle) * scale_dist
            scale_y = 50 + math.sin(scale_angle) * scale_dist
            # 龙鳞（菱形）
            if (int(t * 8) + i) % 4 < 2:
                scale_points = [
                    (scale_x, scale_y - 2),
                    (scale_x + 2, scale_y),
                    (scale_x, scale_y + 2),
                    (scale_x - 2, scale_y)
                ]
                pygame.draw.polygon(scale_surface, (220, 0, 0, 220), [(int(p[0]), int(p[1])) for p in scale_points])
                pygame.draw.polygon(scale_surface, (255, 215, 0, 200), [(int(p[0]), int(p[1])) for p in scale_points], 1)
        s.blit(scale_surface, (0, 0))
        
        # 龙息喷涌（火焰吐息）
        breath_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        breath_angle = math.pi / 2
        for i in range(15):
            breath_dist = 15 + i * 4
            breath_x = 60 + math.cos(breath_angle) * breath_dist
            breath_y = 55 + math.sin(breath_angle) * breath_dist
            breath_width = 8 + i
            breath_alpha = int(220 - i * 10)
            # 火焰扩散
            pygame.draw.circle(breath_surface, (255, 100, 0, breath_alpha), (int(breath_x), int(breath_y)), breath_width)
        s.blit(breath_surface, (0, 0))
        
        # 龙威镇世（威压波动）
        for i in range(3):
            威 = 30 + i * 12 + int(10 * pulse)
            威_alpha = int(150 * (1 - i / 3))
            威_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(威_surface, (220, 0, 0, 威_alpha), (60, 50), 威, 3)
            s.blit(威_surface, (0, 0))
        
        return s
    
    elif model_style == "vampire":
        # 吸血鬼·血族领主 - 吸血蝙蝠、血族纹章、血液吸收光束、暗夜猎食者
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：吸血鬼轮廓
        vampire_cloak = [
            (60, 35), (68, 48), (66, 65), (60, 70),
            (54, 65), (52, 48)
        ]
        pygame.draw.polygon(s, (50, 0, 30), vampire_cloak)
        pygame.draw.polygon(s, (100, 0, 50), vampire_cloak, 2)
        
        # 吸血鬼面部
        pygame.draw.circle(s, (150, 130, 130), (60, 40), 6)
        # 红眼
        for eye_x in [57, 63]:
            pygame.draw.circle(s, (200, 0, 0), (eye_x, 39), 2)
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (200, 0, 0, 180), (eye_x, 39), 4)
            s.blit(eye_glow, (0, 0))
        # 尖牙
        pygame.draw.line(s, (255, 255, 255), (58, 42), (58, 45), 2)
        pygame.draw.line(s, (255, 255, 255), (62, 42), (62, 45), 2)
        
        # 吸血蝙蝠环绕（8只蝙蝠）
        for i in range(8):
            bat_angle = t * 3 + i * math.pi / 4
            bat_dist = 28 + 10 * math.sin(t * 2 + i)
            bat_x = 60 + math.cos(bat_angle) * bat_dist
            bat_y = 50 + math.sin(bat_angle) * bat_dist
            # 蝙蝠身体
            pygame.draw.circle(s, (80, 0, 40), (int(bat_x), int(bat_y)), 3)
            # 蝙蝠翅膀（左右）
            wing_offset = int(4 * math.sin(t * 6 + i))
            pygame.draw.line(s, (100, 0, 50), (int(bat_x), int(bat_y)), (int(bat_x - 5 - wing_offset), int(bat_y)), 2)
            pygame.draw.line(s, (100, 0, 50), (int(bat_x), int(bat_y)), (int(bat_x + 5 + wing_offset), int(bat_y)), 2)
        
        # 血族纹章（胸前）
        crest_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 纹章盾形
        crest_points = [(60, 48), (65, 52), (63, 58), (60, 60), (57, 58), (55, 52)]
        pygame.draw.polygon(crest_surface, (150, 0, 70, 220), crest_points)
        pygame.draw.polygon(crest_surface, (200, 0, 100, 220), crest_points, 2)
        # 纹章符号（蝙蝠）
        pygame.draw.circle(crest_surface, (200, 0, 100, 220), (60, 54), 2)
        pygame.draw.line(crest_surface, (200, 0, 100, 220), (60, 54), (57, 56), 1)
        pygame.draw.line(crest_surface, (200, 0, 100, 220), (60, 54), (63, 56), 1)
        s.blit(crest_surface, (0, 0))
        
        # 血液吸收光束（吸血射线）
        for i in range(4):
            beam_angle = t * 2 + i * math.pi / 2
            beam_length = 35 + 8 * math.sin(t * 3 + i)
            beam_x = 60 + math.cos(beam_angle) * beam_length
            beam_y = 50 + math.sin(beam_angle) * beam_length
            beam_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 吸血光束（从外向内）
            pygame.draw.line(beam_surface, (150, 0, 70, 200), (int(beam_x), int(beam_y)), (60, 50), 3)
            pygame.draw.circle(beam_surface, (200, 0, 100, 220), (int(beam_x), int(beam_y)), 4)
            s.blit(beam_surface, (0, 0))
        
        # 暗夜猎食者气息（暗红雾气）
        mist_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            mist_angle = t * 1.5 + i * math.pi / 5
            mist_dist = 20 + 8 * math.sin(t * 2 + i)
            mist_x = 60 + math.cos(mist_angle) * mist_dist
            mist_y = 50 + math.sin(mist_angle) * mist_dist
            pygame.draw.circle(mist_surface, (100, 0, 50, 120), (int(mist_x), int(mist_y)), 6)
        s.blit(mist_surface, (0, 0))
        
        return s
    
    # ========== Stalker专属涂装 ==========
    elif model_style == "predator":
        # 铁血战士·热能追踪 - 铁血战士形态、热能视觉、等离子炮、狩猎荣耀
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：铁血战士装甲
        armor_points = [(60, 32), (70, 46), (68, 60), (60, 66), (52, 60), (50, 46)]
        pygame.draw.polygon(s, (80, 0, 120), armor_points)
        pygame.draw.polygon(s, (150, 80, 180), armor_points, 3)
        
        # 铁血战士面罩（标志性）
        mask_points = [(60, 35), (65, 42), (60, 45), (55, 42)]
        pygame.draw.polygon(s, (120, 60, 140), mask_points)
        pygame.draw.polygon(s, (180, 100, 200), mask_points, 2)
        # 面罩发光眼睛（红色）
        for eye_x in [57, 63]:
            pygame.draw.circle(s, (255, 0, 0), (eye_x, 40), 2)
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (255, 0, 0, 200), (eye_x, 40), 4)
            s.blit(eye_glow, (0, 0))
        
        # 热能视觉追踪（热成像扫描线）
        thermal_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        scan_y = int(30 + (t * 40) % 50)
        # 扫描线
        pygame.draw.line(thermal_surface, (255, 100, 0, 220), (30, scan_y), (90, scan_y), 2)
        # 热能区域
        for i in range(8):
            heat_x = 40 + i * 8
            heat_y = scan_y + int(5 * math.sin(t * 5 + i))
            pygame.draw.circle(thermal_surface, (255, 150, 0, 150), (heat_x, heat_y), 4)
        s.blit(thermal_surface, (0, 0))
        
        # 等离子炮（肩部武器）
        cannon_angle = math.sin(t * 2) * 0.3
        cannon_x = 72 + math.cos(cannon_angle) * 8
        cannon_y = 45 + math.sin(cannon_angle) * 8
        # 炮管
        pygame.draw.line(s, (100, 100, 150), (72, 45), (int(cannon_x), int(cannon_y)), 4)
        # 炮口
        pygame.draw.circle(s, (150, 150, 255), (int(cannon_x), int(cannon_y)), 4)
        # 等离子充能
        if int(t * 4) % 3 == 0:
            plasma_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(plasma_glow, (150, 150, 255, 220), (int(cannon_x), int(cannon_y)), int(8 * pulse))
            s.blit(plasma_glow, (0, 0))
        
        # 狩猎荣耀标记（战利品符文）
        rune_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            rune_angle = t + i * math.pi / 3
            rune_x = 60 + math.cos(rune_angle) * 22
            rune_y = 50 + math.sin(rune_angle) * 22
            # 铁血符文（三角）
            if (int(t * 5) + i) % 3 == 0:
                rune_points = [
                    (rune_x, rune_y - 3),
                    (rune_x + 3, rune_y + 2),
                    (rune_x - 3, rune_y + 2)
                ]
                pygame.draw.polygon(rune_surface, (180, 100, 200, 200), [(int(p[0]), int(p[1])) for p in rune_points])
        s.blit(rune_surface, (0, 0))
        
        # 隐形装置（半透明效果）
        cloak_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            cloak_x = 60 + int(8 * math.cos(t * 2 + i))
            cloak_y = 50 + int(8 * math.sin(t * 2 + i))
            pygame.draw.circle(cloak_surface, (100, 150, 200, 80), (cloak_x, cloak_y), 6)
        s.blit(cloak_surface, (0, 0))
        
        return s
    
    elif model_style == "alien":
        # 异形猎手·完美生物 - 异形形态、酸性血液、致命猎杀
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：异形躯体（有机曲线）
        alien_points = [(60, 30), (72, 45), (68, 62), (60, 68), (52, 62), (48, 45)]
        pygame.draw.polygon(s, (40, 80, 20), alien_points)
        pygame.draw.polygon(s, (80, 150, 50), alien_points, 2)
        
        # 异形头部（长型）
        head_points = [(60, 25), (65, 30), (63, 38), (57, 38), (55, 30)]
        pygame.draw.polygon(s, (30, 70, 10), head_points)
        pygame.draw.polygon(s, (70, 140, 30), head_points, 2)
        
        # 异形内颚（经典双颚）
        if int(t * 4) % 3 == 0:
            inner_jaw_y = 38 + int(5 * math.sin(t * 6))
            pygame.draw.circle(s, (200, 200, 200), (60, inner_jaw_y), 3)
            pygame.draw.line(s, (200, 200, 200), (60, 38), (60, inner_jaw_y), 2)
        
        # 异形尾部（带刺）
        tail_segments = []
        for i in range(8):
            tail_angle = math.pi / 2 + math.sin(t * 3 + i * 0.5) * 0.3
            tail_dist = 10 + i * 4
            tail_x = 60 + math.cos(tail_angle) * tail_dist
            tail_y = 68 + math.sin(tail_angle) * tail_dist
            tail_segments.append((tail_x, tail_y))
        for i in range(len(tail_segments) - 1):
            pygame.draw.line(s, (50, 100, 30), (int(tail_segments[i][0]), int(tail_segments[i][1])), 
                           (int(tail_segments[i+1][0]), int(tail_segments[i+1][1])), 5)
        # 尾部尖刺
        if tail_segments:
            tip_x, tip_y = tail_segments[-1]
            pygame.draw.polygon(s, (80, 150, 50), [
                (int(tip_x), int(tip_y)),
                (int(tip_x - 4), int(tip_y + 6)),
                (int(tip_x + 4), int(tip_y + 6))
            ])
        
        # 酸性血液（绿色液滴）
        acid_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            acid_angle = t * 2 + i * math.pi / 4
            acid_dist = 25 + 8 * math.sin(t * 3 + i)
            acid_x = 60 + math.cos(acid_angle) * acid_dist
            acid_y = 50 + math.sin(acid_angle) * acid_dist
            # 酸液滴
            pygame.draw.circle(acid_surface, (100, 255, 50, 220), (int(acid_x), int(acid_y)), 3)
            # 酸液腐蚀效果
            pygame.draw.circle(acid_surface, (150, 255, 100, 150), (int(acid_x), int(acid_y)), 5)
        s.blit(acid_surface, (0, 0))
        
        # 完美生物进化纹理（有机纹路）
        texture_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            texture_y = 35 + i * 4
            texture_offset = int(3 * math.sin(t * 3 + i))
            pygame.draw.line(texture_surface, (70, 140, 30, 180), (50 + texture_offset, texture_y), (70 + texture_offset, texture_y), 2)
        s.blit(texture_surface, (0, 0))
        
        # 致命猎杀姿态（攻击爪）
        for side in [-1, 1]:
            claw_x = 60 + side * 15
            claw_y = 55 + int(5 * math.sin(t * 3))
            # 爪子
            for i in range(3):
                claw_tip_x = claw_x + side * (3 + i * 2)
                claw_tip_y = claw_y + 8 + i * 2
                pygame.draw.line(s, (80, 150, 50), (claw_x, claw_y), (claw_tip_x, claw_tip_y), 2)
        
        return s
    
    elif model_style == "chameleon":
        # 变色龙·完美伪装 - 色彩变幻、环境融入、伪装隐身
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：变色龙身体（颜色变化）
        hue_shift = int(t * 100) % 360
        color_r = int(127 + 127 * math.sin(math.radians(hue_shift)))
        color_g = int(127 + 127 * math.sin(math.radians(hue_shift + 120)))
        color_b = int(127 + 127 * math.sin(math.radians(hue_shift + 240)))
        
        body_points = [(60, 35), (68, 48), (65, 62), (60, 66), (55, 62), (52, 48)]
        chameleon_alpha = int(180 + 75 * math.sin(t * 2.5))  # 透明度变化
        body_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(body_surface, (color_r, color_g, color_b, chameleon_alpha), body_points)
        pygame.draw.polygon(body_surface, (color_r + 50, color_g + 50, color_b + 50, chameleon_alpha), body_points, 2)
        s.blit(body_surface, (0, 0))
        
        # 变色龙眼睛（独立转动）
        for side, eye_rotation in [(-1, t * 2), (1, -t * 2)]:
            eye_x = 60 + side * 6
            eye_y = 42
            # 眼球底座
            pygame.draw.circle(s, (color_r, color_g, color_b), (eye_x, eye_y), 5)
            # 瞳孔（独立转动）
            pupil_x = eye_x + int(2 * math.cos(eye_rotation))
            pupil_y = eye_y + int(2 * math.sin(eye_rotation))
            pygame.draw.circle(s, (0, 0, 0), (pupil_x, pupil_y), 2)
        
        # 色彩变幻波纹（皮肤纹理）
        pattern_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            pattern_angle = t * 3 + i * math.pi / 7.5
            pattern_dist = 18 + 8 * math.sin(t * 2 + i)
            pattern_x = 60 + math.cos(pattern_angle) * pattern_dist
            pattern_y = 50 + math.sin(pattern_angle) * pattern_dist
            # 色斑
            spot_hue = (hue_shift + i * 24) % 360
            spot_r = int(127 + 127 * math.sin(math.radians(spot_hue)))
            spot_g = int(127 + 127 * math.sin(math.radians(spot_hue + 120)))
            spot_b = int(127 + 127 * math.sin(math.radians(spot_hue + 240)))
            pygame.draw.circle(pattern_surface, (spot_r, spot_g, spot_b, 180), (int(pattern_x), int(pattern_y)), 4)
        s.blit(pattern_surface, (0, 0))
        
        # 环境融入效果（背景纹理模拟）
        blend_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            blend_x = 45 + (i % 4) * 10
            blend_y = 40 + (i // 4) * 15
            blend_alpha = int(100 + 100 * math.sin(t * 3 + i))
            pygame.draw.rect(blend_surface, (color_r, color_g, color_b, blend_alpha), (blend_x, blend_y, 8, 8))
        s.blit(blend_surface, (0, 0))
        
        # 伪装隐身（轮廓扭曲）
        distortion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            dist_angle = i * math.pi / 3
            dist_x = 60 + math.cos(dist_angle) * 25
            dist_y = 50 + math.sin(dist_angle) * 25
            pygame.draw.circle(distortion_surface, (color_r, color_g, color_b, 100), (int(dist_x), int(dist_y)), 6)
        s.blit(distortion_surface, (0, 0))
        
        return s
    
    elif model_style == "insect":
        # 虫群潜行·复眼侦测 - 虫群形态、复眼、潜行猎杀、群体智慧
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：昆虫身躯（分节）
        segments = [
            (60, 40, 12, 8),   # 头部
            (60, 50, 14, 10),  # 胸部
            (60, 62, 12, 8),   # 腹部
        ]
        for seg_x, seg_y, seg_w, seg_h in segments:
            pygame.draw.ellipse(s, (0, 80, 40), (seg_x - seg_w//2, seg_y - seg_h//2, seg_w, seg_h))
            pygame.draw.ellipse(s, (50, 130, 80), (seg_x - seg_w//2, seg_y - seg_h//2, seg_w, seg_h), 2)
        
        # 复眼全方位侦测（多个小眼）
        compound_eye_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for side in [-1, 1]:
            eye_base_x = 60 + side * 5
            eye_base_y = 38
            # 复眼构造（蜂窝状）
            for row in range(3):
                for col in range(3):
                    eye_x = eye_base_x + side * col * 2
                    eye_y = eye_base_y + row * 2
                    # 小眼单元
                    pygame.draw.circle(compound_eye_surface, (100, 255, 100, 220), (eye_x, eye_y), 1)
        s.blit(compound_eye_surface, (0, 0))
        
        # 昆虫触角（感知器官）
        for side in [-1, 1]:
            antenna_segments = []
            for i in range(6):
                antenna_angle = side * (math.pi / 3) + i * 0.2 + math.sin(t * 3 + i) * 0.2
                antenna_dist = 8 + i * 3
                antenna_x = 60 + math.cos(antenna_angle) * antenna_dist
                antenna_y = 35 + math.sin(antenna_angle) * antenna_dist
                antenna_segments.append((antenna_x, antenna_y))
            for i in range(len(antenna_segments) - 1):
                pygame.draw.line(s, (50, 130, 80), (int(antenna_segments[i][0]), int(antenna_segments[i][1])), 
                               (int(antenna_segments[i+1][0]), int(antenna_segments[i+1][1])), 2)
        
        # 昆虫腿部（6条腿）
        for i in range(6):
            leg_side = -1 if i < 3 else 1
            leg_segment = i % 3
            leg_base_x = 60 + leg_side * 7
            leg_base_y = 45 + leg_segment * 8
            leg_angle = leg_side * (math.pi / 3) + math.sin(t * 4 + i) * 0.4
            leg_length = 15
            leg_x = leg_base_x + math.cos(leg_angle) * leg_length
            leg_y = leg_base_y + math.sin(leg_angle) * leg_length
            pygame.draw.line(s, (50, 130, 80), (leg_base_x, leg_base_y), (int(leg_x), int(leg_y)), 2)
            # 腿部关节
            joint_x = leg_base_x + math.cos(leg_angle) * leg_length * 0.6
            joint_y = leg_base_y + math.sin(leg_angle) * leg_length * 0.6
            pygame.draw.circle(s, (20, 100, 50), (int(joint_x), int(joint_y)), 2)
        
        # 虫群粒子（小虫环绕）
        swarm_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            swarm_angle = t * 4 + i * math.pi / 10
            swarm_dist = 28 + 12 * (i / 20) + 5 * math.sin(t * 3 + i)
            swarm_x = 60 + math.cos(swarm_angle) * swarm_dist
            swarm_y = 50 + math.sin(swarm_angle) * swarm_dist
            # 小虫（点）
            pygame.draw.circle(swarm_surface, (20, 120, 70, 200), (int(swarm_x), int(swarm_y)), 2)
        s.blit(swarm_surface, (0, 0))
        
        # 群体智慧连接线（信息网络）
        network_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            if i < 4:
                continue
            angle1 = t * 2 + i * math.pi / 4
            angle2 = t * 2 + (i - 4) * math.pi / 4
            x1 = 60 + math.cos(angle1) * 20
            y1 = 50 + math.sin(angle1) * 20
            x2 = 60 + math.cos(angle2) * 20
            y2 = 50 + math.sin(angle2) * 20
            pygame.draw.line(network_surface, (50, 150, 100, 100), (int(x1), int(y1)), (int(x2), int(y2)), 1)
        s.blit(network_surface, (0, 0))
        
        return s
    
    elif model_style == "drone":
        # 无人机群·天罗地网 - 无人机部署、监控网络、智能追踪
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：中心控制无人机
        pygame.draw.circle(s, (180, 130, 0), (60, 50), 10)
        pygame.draw.circle(s, (220, 180, 20), (60, 50), 10, 2)
        # 中心摄像头
        pygame.draw.circle(s, (255, 200, 50), (60, 50), 5)
        pygame.draw.circle(s, (0, 0, 0), (60, 50), 3)
        
        # 螺旋桨（4个）
        prop_angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
        for prop_angle in prop_angles:
            prop_x = 60 + math.cos(prop_angle) * 15
            prop_y = 50 + math.sin(prop_angle) * 15
            # 螺旋桨臂
            pygame.draw.line(s, (150, 120, 0), (60, 50), (int(prop_x), int(prop_y)), 3)
            # 螺旋桨旋转
            blade_angle = t * 10 + prop_angle
            for blade in range(2):
                blade_offset = blade * math.pi
                blade_x1 = prop_x + math.cos(blade_angle + blade_offset) * 6
                blade_y1 = prop_y + math.sin(blade_angle + blade_offset) * 6
                blade_x2 = prop_x + math.cos(blade_angle + blade_offset + math.pi) * 6
                blade_y2 = prop_y + math.sin(blade_angle + blade_offset + math.pi) * 6
                pygame.draw.line(s, (200, 150, 0), (int(blade_x1), int(blade_y1)), (int(blade_x2), int(blade_y2)), 2)
        
        # 子无人机群（8个小无人机）
        for i in range(8):
            drone_angle = t * 2 + i * math.pi / 4
            drone_dist = 30 + 8 * math.sin(t * 1.5 + i)
            drone_x = 60 + math.cos(drone_angle) * drone_dist
            drone_y = 50 + math.sin(drone_angle) * drone_dist
            # 小无人机
            pygame.draw.circle(s, (200, 150, 0), (int(drone_x), int(drone_y)), 4)
            pygame.draw.circle(s, (255, 200, 50), (int(drone_x), int(drone_y)), 2)
        
        # 天罗地网监控连接线
        network_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            drone_angle = t * 2 + i * math.pi / 4
            drone_dist = 30 + 8 * math.sin(t * 1.5 + i)
            drone_x = 60 + math.cos(drone_angle) * drone_dist
            drone_y = 50 + math.sin(drone_angle) * drone_dist
            # 连接到中心
            pygame.draw.line(network_surface, (255, 200, 50, 150), (60, 50), (int(drone_x), int(drone_y)), 1)
            # 相邻连接
            next_i = (i + 1) % 8
            next_angle = t * 2 + next_i * math.pi / 4
            next_dist = 30 + 8 * math.sin(t * 1.5 + next_i)
            next_x = 60 + math.cos(next_angle) * next_dist
            next_y = 50 + math.sin(next_angle) * next_dist
            pygame.draw.line(network_surface, (255, 200, 50, 100), (int(drone_x), int(drone_y)), (int(next_x), int(next_y)), 1)
        s.blit(network_surface, (0, 0))
        
        # 智能追踪扫描（雷达波）
        for i in range(3):
            scan_radius = (t * 50 + i * 25) % 75
            scan_alpha = int(200 * (1 - scan_radius / 75))
            scan_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(scan_surface, (220, 180, 20, scan_alpha), (60, 50), int(scan_radius), 2)
            s.blit(scan_surface, (0, 0))
        
        # 数据传输粒子
        data_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            data_angle = t * 3 + i * math.pi / 6
            data_dist = 15 + ((t * 30 + i * 6) % 25)
            data_x = 60 + math.cos(data_angle) * data_dist
            data_y = 50 + math.sin(data_angle) * data_dist
            pygame.draw.circle(data_surface, (255, 200, 50, 220), (int(data_x), int(data_y)), 2)
        s.blit(data_surface, (0, 0))
        
        return s
    
    elif model_style == "void":
        # 虚空潜伏·无形存在 - 虚空隐匿、存在感抹除、维度穿梭、虚无形态
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.2 + 1
        
        # 主体：虚无形态（几乎透明）
        void_alpha = int(120 + 80 * math.sin(t * 2.5))
        void_points = [(60, 35), (68, 48), (64, 62), (60, 68), (56, 62), (52, 48)]
        void_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(void_surface, (80, 0, 120, void_alpha), void_points)
        pygame.draw.polygon(void_surface, (150, 50, 180, void_alpha + 50), void_points, 2)
        s.blit(void_surface, (0, 0))
        
        # 维度缝隙穿梭（空间裂缝）
        for i in range(5):
            crack_angle = t * 1.5 + i * 2 * math.pi / 5
            crack_length = 20 + 10 * math.sin(t * 2 + i)
            crack_x = 60 + math.cos(crack_angle) * crack_length
            crack_y = 50 + math.sin(crack_angle) * crack_length
            crack_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 裂缝线
            pygame.draw.line(crack_surface, (100, 20, 150, 220), (60, 50), (int(crack_x), int(crack_y)), 3)
            # 裂缝边缘光
            pygame.draw.line(crack_surface, (180, 80, 220, 150), (60, 50), (int(crack_x), int(crack_y)), 5)
            s.blit(crack_surface, (0, 0))
        
        # 存在感抹除（扭曲波纹）
        distortion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            distort_radius = 20 + i * 8 + (t * 25) % 20
            distort_alpha = int(150 * (1 - ((t * 25) % 20) / 20))
            pygame.draw.circle(distortion_surface, (100, 20, 150, distort_alpha), (60, 50), int(distort_radius), 2)
        s.blit(distortion_surface, (0, 0))
        
        # 虚空粒子（消失粒子）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 3 + i * math.pi / 10
            particle_dist = 20 + 20 * (i / 20)
            particle_alpha = int(220 - (i / 20) * 150)
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (100, 20, 150, particle_alpha), (int(px), int(py)), 2)
        s.blit(particle_surface, (0, 0))
        
        # 虚空眼睛（唯一可见）
        if (int(t * 3) % 5) < 2:
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (150, 50, 180, 250), (60, 45), int(6 * pulse))
            pygame.draw.circle(eye_glow, (100, 20, 150, 200), (60, 45), 4)
            s.blit(eye_glow, (0, 0))
        
        # 虚无能量场
        for i in range(3):
            void_radius = 25 + i * 10 + int(8 * pulse)
            void_alpha_ring = int(100 * (1 - i / 3))
            void_ring = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(void_ring, (100, 20, 150, void_alpha_ring), (60, 50), void_radius, 2)
            s.blit(void_ring, (0, 0))
        
        return s
    
    elif model_style == "xenomorph":
        # 异形皇后·终极猎食 - 异形皇后、完美进化、生物链顶端
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：异形皇后巨大躯体
        queen_body = [(60, 28), (75, 48), (70, 65), (60, 72), (50, 65), (45, 48)]
        pygame.draw.polygon(s, (20, 60, 20), queen_body)
        pygame.draw.polygon(s, (80, 120, 80), queen_body, 3)
        
        # 皇后冠状头部
        crown_points = [
            (60, 20),  # 顶峰
            (65, 25), (70, 22),  # 右侧尖刺
            (55, 25), (50, 22),  # 左侧尖刺
        ]
        for i in range(0, len(crown_points) - 1, 2):
            if i + 1 < len(crown_points):
                pygame.draw.line(s, (100, 150, 100), (60, 28), crown_points[i], 3)
                pygame.draw.circle(s, (80, 120, 80), crown_points[i], 3)
        
        # 皇后巨大内颚
        jaw_extension = int(8 * math.sin(t * 3))
        jaw_y = 42 + jaw_extension
        pygame.draw.circle(s, (180, 180, 180), (60, jaw_y), 4)
        pygame.draw.line(s, (180, 180, 180), (60, 38), (60, jaw_y), 3)
        # 内颚尖端
        pygame.draw.circle(s, (200, 200, 200), (60, jaw_y), 2)
        
        # 多节装甲尾部（更长更强）
        tail_segments_queen = []
        for i in range(12):
            tail_angle = math.pi / 2 + math.sin(t * 2 + i * 0.3) * 0.4
            tail_dist = 12 + i * 4
            tail_x = 60 + math.cos(tail_angle) * tail_dist
            tail_y = 72 + math.sin(tail_angle) * tail_dist
            tail_segments_queen.append((tail_x, tail_y))
        for i in range(len(tail_segments_queen) - 1):
            tail_width = 8 - int(i * 0.5)
            pygame.draw.line(s, (40, 90, 40), (int(tail_segments_queen[i][0]), int(tail_segments_queen[i][1])), 
                           (int(tail_segments_queen[i+1][0]), int(tail_segments_queen[i+1][1])), tail_width)
        # 尾部巨刺
        if tail_segments_queen:
            tip_x, tip_y = tail_segments_queen[-1]
            pygame.draw.polygon(s, (100, 150, 100), [
                (int(tip_x), int(tip_y)),
                (int(tip_x - 6), int(tip_y + 10)),
                (int(tip_x + 6), int(tip_y + 10))
            ])
        
        # 皇后背部尖刺（4对）
        for i in range(4):
            spike_x = 60
            spike_y = 35 + i * 8
            for side in [-1, 1]:
                spike_end_x = spike_x + side * (8 + i * 2)
                spike_end_y = spike_y - 5
                pygame.draw.line(s, (80, 120, 80), (spike_x, spike_y), (spike_end_x, spike_end_y), 3)
                pygame.draw.circle(s, (100, 150, 100), (spike_end_x, spike_end_y), 2)
        
        # 完美进化生物质（有机纹理）
        bio_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            bio_angle = t * 2 + i * math.pi / 10
            bio_dist = 20 + 15 * (i / 20)
            bio_x = 60 + math.cos(bio_angle) * bio_dist
            bio_y = 50 + math.sin(bio_angle) * bio_dist
            # 生物质节点
            pygame.draw.circle(bio_surface, (50, 120, 50, 200), (int(bio_x), int(bio_y)), 3)
        s.blit(bio_surface, (0, 0))
        
        # 酸液喷射（皇后能力）
        acid_spray = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            if (int(t * 6) + i) % 4 < 2:
                spray_angle = math.pi / 2 + (i - 6) * math.pi / 24
                spray_dist = 25 + (t * 30 + i * 5) % 30
                spray_x = 60 + math.cos(spray_angle) * spray_dist
                spray_y = 42 + math.sin(spray_angle) * spray_dist
                pygame.draw.circle(acid_spray, (150, 255, 100, 220), (int(spray_x), int(spray_y)), 3)
        s.blit(acid_spray, (0, 0))
        
        # 生物链顶端威压（能量场）
        for i in range(3):
            dominance_radius = 30 + i * 12 + int(10 * pulse)
            dominance_alpha = int(150 * (1 - i / 3))
            dominance_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(dominance_surface, (50, 120, 50, dominance_alpha), (60, 50), dominance_radius, 3)
            s.blit(dominance_surface, (0, 0))
        
        return s

    # --- Phantom MK3/MK4 ---
    elif model_style == "phantom_assassin":
        # 暗影刺客：前掠翼
        pygame.draw.polygon(s, (50, 0, 100), [(60, 10), (80, 40), (60, 100), (40, 40)])
        # 刀锋翅膀
        pygame.draw.polygon(s, c, [(60, 40), (110, 20), (80, 60)])
        pygame.draw.polygon(s, c, [(60, 40), (10, 20), (40, 60)])
        return s

    elif model_style == "phantom_mirage":
        # 海市蜃楼：多重虚影
        for i in range(3):
            offset = i * 5
            alpha = 100 - i * 30
            s2 = pygame.Surface((120, 120), pygame.SRCALPHA)
            pts = [(60 + offset, 20), (100 + offset, 100), (20 + offset, 100)]
            pygame.draw.polygon(s2, (*c[:3], alpha), pts)
            s.blit(s2, (0, 0))
        return s

    # --- Titan MK3/MK4 ---
    elif model_style == "titan_behemoth":
        # 战争巨兽：巨大的工业结构
        pygame.draw.rect(s, (50, 50, 50), (30, 30, 60, 60))
        pygame.draw.circle(s, (100, 100, 100), (30, 30), 15)
        pygame.draw.circle(s, (100, 100, 100), (90, 30), 15)
        pygame.draw.circle(s, (100, 100, 100), (30, 90), 15)
        pygame.draw.circle(s, (100, 100, 100), (90, 90), 15)
        pygame.draw.rect(s, c, (40, 40, 40, 40))
        return s

    elif model_style == "titan_fortress":
        # 浮空城：圆形堡垒
        pygame.draw.circle(s, (80, 80, 100), (60, 60), 40)
        pygame.draw.circle(s, c, (60, 60), 30)
        # 炮塔
        for i in range(4):
            angle = i * math.pi / 2
            ex = 60 + math.cos(angle) * 40
            ey = 60 + math.sin(angle) * 40
            pygame.draw.circle(s, (200, 50, 50), (int(ex), int(ey)), 8)
        return s

    # --- Thunderbird MK3/MK4 ---
    elif model_style == "thunderbird_storm":
        # 雷暴之眼：云团结构
        for i in range(5):
            ox = random.randint(30, 90)
            oy = random.randint(30, 90)
            r = random.randint(10, 20)
            pygame.draw.circle(s, (100, 100, 120), (ox, oy), r)
        # 闪电
        pygame.draw.lines(s, (255, 255, 0), False, [(40, 20), (60, 60), (50, 70), (80, 100)], 2)
        return s

    elif model_style == "thunderbird_volt":
        # 高压电擎：线圈
        pygame.draw.rect(s, (50, 50, 100), (50, 20, 20, 80))
        # 绕线
        for y in range(25, 95, 10):
            pygame.draw.ellipse(s, (0, 200, 255), (40, y, 40, 10), 2)
        # 顶部放电
        pygame.draw.circle(s, (200, 200, 255), (60, 20), 10 + int(5 * pulse))
        return s

    # --- Viper MK3/MK4 ---
    elif model_style == "viper_cobra":
        # 眼镜蛇王：宽大的颈部
        pygame.draw.ellipse(s, (50, 100, 50), (30, 30, 60, 50))
        pygame.draw.rect(s, (40, 80, 40), (50, 30, 20, 80))
        # 花纹
        pygame.draw.circle(s, (0, 0, 0), (45, 50), 5)
        pygame.draw.circle(s, (0, 0, 0), (75, 50), 5)
        return s

    elif model_style == "viper_venom":
        # 剧毒注射：针筒形状
        pygame.draw.rect(s, (200, 200, 200), (50, 30, 20, 60))
        pygame.draw.line(s, (100, 100, 100), (60, 30), (60, 10), 2) # 针头
        pygame.draw.rect(s, (0, 255, 0), (52, 32, 16, 56)) # 毒液
        return s

    # --- Specter MK3/MK4 ---
    elif model_style == "specter_ghost":
        # 恶灵附身：飘动的布料
        points = [(60, 20), (90, 40), (80, 100), (60, 90), (40, 100), (30, 40)]
        # 底部波浪
        points[2] = (80 + int(5 * math.sin(t * 5)), 100)
        points[4] = (40 + int(5 * math.cos(t * 5)), 100)
        pygame.draw.polygon(s, (200, 200, 200), points)
        # 眼睛
        pygame.draw.circle(s, (0, 0, 0), (50, 50), 5)
        pygame.draw.circle(s, (0, 0, 0), (70, 50), 5)
        return s

    elif model_style == "specter_sniper":
        # 鹰眼猎手：狙击枪造型
        pygame.draw.line(s, (50, 50, 50), (60, 100), (60, 10), 4) # 枪管
        pygame.draw.rect(s, (30, 30, 30), (55, 60, 10, 30)) # 机身
        pygame.draw.circle(s, (0, 255, 255), (70, 40), 8, 2) # 瞄准镜
        pygame.draw.line(s, (0, 255, 255), (70, 40), (60, 40), 1)
        return s

    # --- Aurora MK3/MK4 ---
    elif model_style == "aurora_nebula":
        # 星云漫步：粒子云
        # 静态模式下使用固定随机种子或固定位置
        if static:
            random.seed(pid) # 使用pid作为种子保证一致性
        
        for i in range(20):
            px = 60 + random.randint(-30, 30)
            py = 60 + random.randint(-30, 30)
            col = (random.randint(100, 255), 0, random.randint(100, 255))
            pygame.draw.circle(s, col, (px, py), random.randint(2, 6))
            
        if static:
            random.seed() # 恢复随机种子
        return s

    elif model_style == "aurora_borealis":
        # 极光之舞：波浪线
        for i in range(5):
            pts = []
            for x in range(20, 100, 10):
                y = 60 + i * 10 + 10 * math.sin(x * 0.1 + t * 2)
                pts.append((x, y))
            if len(pts) > 1:
                pygame.draw.lines(s, (0, 255, 100), False, pts, 2)
        return s
    
    # ========== Gaia专属涂装 ==========
    elif model_style == "forest":
        # 森林守护者·生命之林 - 参天古树、藤蔓缠绕、森林灵体、生命气息
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：古树形态
        trunk_points = [(60, 28), (66, 50), (64, 68), (56, 68), (54, 50)]
        pygame.draw.polygon(s, (60, 40, 20), trunk_points)
        pygame.draw.polygon(s, (100, 80, 50), trunk_points, 2)
        
        # 树冠（多层绿叶）
        for i in range(3):
            crown_y = 35 - i * 8
            crown_radius = 15 - i * 3
            crown_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(crown_surface, (50, 150, 50, 200), (60, crown_y), crown_radius)
            pygame.draw.circle(crown_surface, (80, 180, 80, 220), (60, crown_y), crown_radius, 2)
            s.blit(crown_surface, (0, 0))
        
        # 藤蔓缠绕（动态藤蔓）
        for side in [-1, 1]:
            vine_segments = []
            for i in range(10):
                vine_angle = side * (math.pi / 4) + i * 0.3 + math.sin(t * 2 + i) * 0.2
                vine_dist = 10 + i * 3
                vine_x = 60 + math.cos(vine_angle) * vine_dist
                vine_y = 50 + math.sin(vine_angle) * vine_dist
                vine_segments.append((vine_x, vine_y))
            for i in range(len(vine_segments) - 1):
                pygame.draw.line(s, (40, 120, 40), (int(vine_segments[i][0]), int(vine_segments[i][1])), 
                               (int(vine_segments[i+1][0]), int(vine_segments[i+1][1])), 3)
            # 藤蔓叶子
            for i in range(0, len(vine_segments), 3):
                leaf_x, leaf_y = vine_segments[i]
                pygame.draw.circle(s, (80, 180, 80), (int(leaf_x), int(leaf_y)), 3)
        
        # 森林灵体（绿色精灵）
        spirit_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            spirit_angle = t * 2 + i * math.pi / 4
            spirit_dist = 25 + 8 * math.sin(t * 3 + i)
            spirit_x = 60 + math.cos(spirit_angle) * spirit_dist
            spirit_y = 50 + math.sin(spirit_angle) * spirit_dist
            # 精灵光球
            pygame.draw.circle(spirit_surface, (100, 255, 100, 220), (int(spirit_x), int(spirit_y)), 4)
            pygame.draw.circle(spirit_surface, (150, 255, 150, 180), (int(spirit_x), int(spirit_y)), 6)
        s.blit(spirit_surface, (0, 0))
        
        # 生命气息（绿色粒子上升）
        life_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            life_x = 50 + (i % 3) * 10 + int(3 * math.sin(t * 2 + i))
            life_y = 70 - ((t * 30 + i * 6) % 50)
            life_alpha = int(200 * (1 - ((t * 30 + i * 6) % 50) / 50))
            pygame.draw.circle(life_surface, (80, 220, 80, life_alpha), (life_x, int(life_y)), 3)
        s.blit(life_surface, (0, 0))
        
        # 根系网络（地下根须）
        root_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            root_angle = math.pi / 2 + (i - 3) * math.pi / 12
            root_length = 20 + 5 * math.sin(t + i)
            root_x = 60 + math.cos(root_angle) * root_length
            root_y = 68 + math.sin(root_angle) * root_length
            pygame.draw.line(root_surface, (80, 60, 40, 180), (60, 68), (int(root_x), int(root_y)), 2)
        s.blit(root_surface, (0, 0))
        
        return s
    
    elif model_style == "crystal":
        # 水晶巨人·棱镜折射 - 水晶形态、光线折射、能量晶核、棱镜效果
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：水晶六边形结构
        crystal_points = [
            (60, 25),
            (70, 35),
            (70, 55),
            (60, 65),
            (50, 55),
            (50, 35)
        ]
        crystal_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(crystal_surface, (150, 200, 255, 230), crystal_points)
        pygame.draw.polygon(crystal_surface, (200, 230, 255, 250), crystal_points, 3)
        s.blit(crystal_surface, (0, 0))
        
        # 水晶内部裂纹（折射线）
        for i in range(8):
            crack_start = crystal_points[i % 6]
            crack_end = crystal_points[(i + 3) % 6]
            pygame.draw.line(s, (180, 220, 255, 200), crack_start, crack_end, 1)
        
        # 能量晶核（中心发光核心）
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        core_radius = int(8 * pulse)
        pygame.draw.circle(core_glow, (100, 200, 255, 250), (60, 45), core_radius)
        pygame.draw.circle(core_glow, (150, 230, 255, 200), (60, 45), core_radius + 4)
        s.blit(core_glow, (0, 0))
        
        # 光线折射（从核心射出）
        refraction_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            ray_angle = t * 3 + i * math.pi / 6
            ray_length = 25 + 10 * math.sin(t * 2 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 45 + math.sin(ray_angle) * ray_length
            # 彩虹色光线
            hue = (i * 30) % 360
            r = int(127 + 127 * math.sin(math.radians(hue)))
            g = int(127 + 127 * math.sin(math.radians(hue + 120)))
            b = int(127 + 127 * math.sin(math.radians(hue + 240)))
            pygame.draw.line(refraction_surface, (r, g, b, 220), (60, 45), (int(ray_x), int(ray_y)), 2)
        s.blit(refraction_surface, (0, 0))
        
        # 水晶碎片环绕
        shard_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            shard_angle = t * 2 + i * math.pi / 5
            shard_dist = 30 + 5 * math.sin(t * 3 + i)
            shard_x = 60 + math.cos(shard_angle) * shard_dist
            shard_y = 45 + math.sin(shard_angle) * shard_dist
            # 小水晶碎片（三角形）
            shard_points = [
                (shard_x, shard_y - 4),
                (shard_x + 3, shard_y + 3),
                (shard_x - 3, shard_y + 3)
            ]
            pygame.draw.polygon(shard_surface, (180, 220, 255, 220), [(int(p[0]), int(p[1])) for p in shard_points])
        s.blit(shard_surface, (0, 0))
        
        # 棱镜光谱效果
        spectrum_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            spectrum_radius = 20 + i * 5 + int(5 * pulse)
            spectrum_alpha = int(150 * (1 - i / 6))
            hue_shift = (t * 100 + i * 60) % 360
            r = int(127 + 127 * math.sin(math.radians(hue_shift)))
            g = int(127 + 127 * math.sin(math.radians(hue_shift + 120)))
            b = int(127 + 127 * math.sin(math.radians(hue_shift + 240)))
            pygame.draw.circle(spectrum_surface, (r, g, b, spectrum_alpha), (60, 45), spectrum_radius, 2)
        s.blit(spectrum_surface, (0, 0))
        
        return s
    
    elif model_style == "rock":
        # 岩石巨人·大地之力 - 岩石形态、大地能量、岩石粒子、坚不可摧
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.1 + 1
        
        # 主体：岩石巨人身躯
        rock_body = [(60, 30), (75, 48), (72, 68), (48, 68), (45, 48)]
        pygame.draw.polygon(s, (100, 80, 60), rock_body)
        pygame.draw.polygon(s, (150, 120, 100), rock_body, 3)
        
        # 岩石纹理（裂缝）
        for i in range(8):
            crack_x1 = 50 + (i % 3) * 10
            crack_y1 = 35 + (i // 3) * 10
            crack_x2 = crack_x1 + 5 + int(3 * math.sin(t + i))
            crack_y2 = crack_y1 + 8
            pygame.draw.line(s, (80, 60, 40), (crack_x1, crack_y1), (crack_x2, crack_y2), 2)
        
        # 大地之力（地脉能量）
        earth_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            earth_angle = i * math.pi / 3
            earth_x = 60 + math.cos(earth_angle) * 20
            earth_y = 50 + math.sin(earth_angle) * 20
            # 地脉节点
            pygame.draw.circle(earth_surface, (200, 150, 100, 220), (int(earth_x), int(earth_y)), 5)
            # 连线到中心
            pygame.draw.line(earth_surface, (180, 130, 80, 180), (60, 50), (int(earth_x), int(earth_y)), 2)
        s.blit(earth_surface, (0, 0))
        
        # 岩石粒子飞舞
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 2 + i * math.pi / 10
            particle_dist = 25 + 15 * (i / 20)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            # 岩石碎片
            pygame.draw.rect(particle_surface, (120, 100, 80, 220), (int(particle_x - 2), int(particle_y - 2), 4, 4))
        s.blit(particle_surface, (0, 0))
        
        # 大地护盾（岩石层）
        for i in range(4):
            shield_radius = 22 + i * 8 + int(6 * pulse)
            shield_alpha = int(150 * (1 - i / 4))
            shield_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 六边形护盾
            shield_points = []
            for j in range(6):
                angle = j * math.pi / 3 + t
                shield_points.append((
                    int(60 + math.cos(angle) * shield_radius),
                    int(50 + math.sin(angle) * shield_radius)
                ))
            pygame.draw.polygon(shield_surface, (150, 120, 100, shield_alpha), shield_points, 2)
            s.blit(shield_surface, (0, 0))
        
        # 地震波动（冲击波）
        for i in range(3):
            wave_radius = (t * 50 + i * 30) % 90
            wave_alpha = int(200 * (1 - wave_radius / 90))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (180, 130, 80, wave_alpha), (60, 50), int(wave_radius), 3)
            s.blit(wave_surface, (0, 0))
        
        return s
    
    elif model_style == "elemental":
        # 元素领主·自然四元 - 四元素环绕、地水火风交织、元素形态
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：元素核心
        pygame.draw.circle(s, (100, 200, 150), (60, 50), 12)
        pygame.draw.circle(s, (150, 255, 200), (60, 50), 12, 2)
        
        # 四元素环绕（地、水、火、风）
        elements = [
            {"angle": 0, "color": (150, 100, 50), "name": "地"},           # 地（棕色）
            {"angle": math.pi / 2, "color": (50, 150, 255), "name": "水"},  # 水（蓝色）
            {"angle": math.pi, "color": (255, 100, 50), "name": "火"},      # 火（红色）
            {"angle": 3 * math.pi / 2, "color": (200, 255, 200), "name": "风"}  # 风（浅绿）
        ]
        
        for i, elem in enumerate(elements):
            elem_angle = elem["angle"] + t * 1.5
            elem_dist = 28 + 5 * math.sin(t * 3 + i)
            elem_x = 60 + math.cos(elem_angle) * elem_dist
            elem_y = 50 + math.sin(elem_angle) * elem_dist
            
            # 元素球
            elem_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(elem_surface, (*elem["color"], 230), (int(elem_x), int(elem_y)), 8)
            pygame.draw.circle(elem_surface, (*elem["color"], 180), (int(elem_x), int(elem_y)), 12, 2)
            s.blit(elem_surface, (0, 0))
            
            # 元素特效
            if elem["name"] == "地":
                # 地：岩石碎片
                for j in range(3):
                    rock_x = elem_x + (j - 1) * 4
                    rock_y = elem_y + 10
                    pygame.draw.rect(s, elem["color"], (int(rock_x), int(rock_y), 3, 3))
            elif elem["name"] == "水":
                # 水：水滴
                for j in range(3):
                    drop_y = elem_y + 10 + j * 4
                    pygame.draw.circle(s, elem["color"], (int(elem_x), int(drop_y)), 2)
            elif elem["name"] == "火":
                # 火：火焰
                flame_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                for j in range(3):
                    flame_y = elem_y - 10 - j * 4 - int(3 * math.sin(t * 5 + j))
                    pygame.draw.circle(flame_surface, (*elem["color"], 220 - j * 50), (int(elem_x), int(flame_y)), 3 - j)
                s.blit(flame_surface, (0, 0))
            elif elem["name"] == "风":
                # 风：螺旋气流
                for j in range(3):
                    wind_angle = t * 6 + j * 2 * math.pi / 3
                    wind_x = elem_x + math.cos(wind_angle) * 8
                    wind_y = elem_y + math.sin(wind_angle) * 8
                    pygame.draw.circle(s, elem["color"], (int(wind_x), int(wind_y)), 2)
        
        # 元素连接线（能量流动）
        connection_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            elem1_angle = elements[i]["angle"] + t * 1.5
            elem2_angle = elements[(i + 1) % 4]["angle"] + t * 1.5
            elem1_dist = 28 + 5 * math.sin(t * 3 + i)
            elem2_dist = 28 + 5 * math.sin(t * 3 + (i + 1))
            x1 = 60 + math.cos(elem1_angle) * elem1_dist
            y1 = 50 + math.sin(elem1_angle) * elem1_dist
            x2 = 60 + math.cos(elem2_angle) * elem2_dist
            y2 = 50 + math.sin(elem2_angle) * elem2_dist
            pygame.draw.line(connection_surface, (150, 255, 200, 150), (int(x1), int(y1)), (int(x2), int(y2)), 2)
        s.blit(connection_surface, (0, 0))
        
        # 元素交织效果
        blend_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            blend_angle = t * 3 + i * math.pi / 6
            blend_dist = 20 + 8 * math.sin(t * 2 + i)
            blend_x = 60 + math.cos(blend_angle) * blend_dist
            blend_y = 50 + math.sin(blend_angle) * blend_dist
            # 混合色
            hue = (i * 30) % 360
            r = int(127 + 127 * math.sin(math.radians(hue)))
            g = int(127 + 127 * math.sin(math.radians(hue + 120)))
            b = int(127 + 127 * math.sin(math.radians(hue + 240)))
            pygame.draw.circle(blend_surface, (r, g, b, 200), (int(blend_x), int(blend_y)), 3)
        s.blit(blend_surface, (0, 0))
        
        return s
    
    elif model_style == "overgrowth":
        # 过度生长·野性爆发 - 植被疯长、藤蔓肆意、野性力量、自然失控
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：被植被覆盖的形态
        overgrown_body = [(60, 32), (70, 48), (68, 64), (52, 64), (50, 48)]
        pygame.draw.polygon(s, (20, 80, 20), overgrown_body)
        pygame.draw.polygon(s, (50, 120, 50), overgrown_body, 2)
        
        # 疯狂生长的藤蔓（多条）
        for vine_idx in range(8):
            vine_angle_base = vine_idx * math.pi / 4
            vine_segments = []
            for i in range(12):
                vine_angle = vine_angle_base + i * 0.2 + math.sin(t * 3 + vine_idx + i * 0.5) * 0.4
                vine_dist = 15 + i * 3
                vine_x = 60 + math.cos(vine_angle) * vine_dist
                vine_y = 50 + math.sin(vine_angle) * vine_dist
                vine_segments.append((vine_x, vine_y))
            # 绘制藤蔓
            for i in range(len(vine_segments) - 1):
                vine_width = max(1, 5 - i // 3)
                pygame.draw.line(s, (40, 140, 40), (int(vine_segments[i][0]), int(vine_segments[i][1])), 
                               (int(vine_segments[i+1][0]), int(vine_segments[i+1][1])), vine_width)
        
        # 野性植物爆发（尖刺）
        thorn_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            thorn_angle = t * 2 + i * math.pi / 8
            thorn_dist = 22 + 10 * math.sin(t * 4 + i)
            thorn_x = 60 + math.cos(thorn_angle) * thorn_dist
            thorn_y = 50 + math.sin(thorn_angle) * thorn_dist
            # 尖刺
            thorn_tip_x = thorn_x + math.cos(thorn_angle) * 8
            thorn_tip_y = thorn_y + math.sin(thorn_angle) * 8
            pygame.draw.line(thorn_surface, (80, 200, 80, 220), (int(thorn_x), int(thorn_y)), 
                           (int(thorn_tip_x), int(thorn_tip_y)), 3)
            pygame.draw.circle(thorn_surface, (100, 220, 100, 220), (int(thorn_tip_x), int(thorn_tip_y)), 2)
        s.blit(thorn_surface, (0, 0))
        
        # 植被粒子（花粉、孢子）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(30):
            particle_angle = t * 2 + i * math.pi / 15
            particle_dist = 20 + 20 * (i / 30) + 5 * math.sin(t * 4 + i)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (120, 255, 120, 220), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        # 失控的生命能量（绿色爆发）
        energy_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            energy_radius = 20 + i * 10 + int(8 * pulse)
            energy_alpha = int(180 * (1 - i / 4))
            pygame.draw.circle(energy_surface, (50, 200, 50, energy_alpha), (60, 50), energy_radius, 3)
        s.blit(energy_surface, (0, 0))
        
        return s
    
    elif model_style == "treant":
        # 树人长老·世界古树 - 树人形态、古树智慧、森林守护
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.1 + 1
        
        # 主体：树人身躯
        treant_body = [(60, 25), (72, 45), (70, 68), (50, 68), (48, 45)]
        pygame.draw.polygon(s, (80, 60, 40), treant_body)
        pygame.draw.polygon(s, (120, 100, 70), treant_body, 3)
        
        # 树人面孔（树皮纹理）
        # 眼睛（发光）
        for eye_x in [55, 65]:
            pygame.draw.circle(s, (100, 255, 100), (eye_x, 40), 3)
            eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (100, 255, 100, 200), (eye_x, 40), 5)
            s.blit(eye_glow, (0, 0))
        # 嘴（树皮裂缝）
        pygame.draw.arc(s, (60, 40, 20), (53, 45, 14, 8), 0, math.pi, 2)
        
        # 树枝手臂
        for side in [-1, 1]:
            arm_base_x = 60 + side * 10
            arm_base_y = 50
            # 主干
            arm_end_x = arm_base_x + side * 15
            arm_end_y = arm_base_y + 5
            pygame.draw.line(s, (100, 80, 60), (arm_base_x, arm_base_y), (arm_end_x, arm_end_y), 4)
            # 分支
            for i in range(3):
                branch_angle = (side * math.pi / 4) + i * 0.3
                branch_x = arm_end_x + math.cos(branch_angle) * 8
                branch_y = arm_end_y + math.sin(branch_angle) * 8
                pygame.draw.line(s, (100, 80, 60), (arm_end_x, arm_end_y), (int(branch_x), int(branch_y)), 2)
        
        # 头顶树冠
        crown_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            crown_x = 50 + i * 5
            crown_y = 20 - int(5 * math.sin(t * 2 + i))
            pygame.draw.circle(crown_surface, (60, 180, 60, 220), (crown_x, crown_y), 4)
        s.blit(crown_surface, (0, 0))
        
        # 古树智慧（符文）
        rune_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            rune_y = 35 + i * 6
            rune_x = 60 + int(3 * math.sin(t * 2 + i))
            # 古老符文（圆形）
            pygame.draw.circle(rune_surface, (150, 200, 100, 200), (rune_x, rune_y), 2)
        s.blit(rune_surface, (0, 0))
        
        # 森林守护光环
        for i in range(3):
            guardian_radius = 25 + i * 10 + int(5 * pulse)
            guardian_alpha = int(150 * (1 - i / 3))
            guardian_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(guardian_surface, (80, 180, 80, guardian_alpha), (60, 50), guardian_radius, 2)
            s.blit(guardian_surface, (0, 0))
        
        # 千年智慧粒子
        wisdom_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            wisdom_angle = t + i * math.pi / 6
            wisdom_dist = 30 + 8 * math.sin(t * 2 + i)
            wisdom_x = 60 + math.cos(wisdom_angle) * wisdom_dist
            wisdom_y = 50 + math.sin(wisdom_angle) * wisdom_dist
            pygame.draw.circle(wisdom_surface, (150, 200, 100, 220), (int(wisdom_x), int(wisdom_y)), 3)
        s.blit(wisdom_surface, (0, 0))
        
        return s
    
    elif model_style == "titan":
        # 盖亚泰坦·星球化身 - 星球泰坦、盖亚意志、地壳浮动、星球之力
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：星球形态（地球）
        planet_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(planet_surface, (50, 150, 250, 230), (60, 50), 20)
        pygame.draw.circle(planet_surface, (80, 180, 255, 250), (60, 50), 20, 2)
        s.blit(planet_surface, (0, 0))
        
        # 大陆板块（绿色陆地）
        continents = [
            [(55, 40), (65, 42), (63, 48), (57, 47)],
            [(48, 52), (54, 54), (52, 58), (47, 56)],
            [(66, 55), (72, 56), (70, 60), (65, 59)]
        ]
        for continent in continents:
            pygame.draw.polygon(s, (100, 200, 100), continent)
        
        # 地壳板块浮动（板块运动）
        plate_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            plate_angle = t * 0.5 + i * math.pi / 4
            plate_dist = 22 + 3 * math.sin(t * 2 + i)
            plate_x = 60 + math.cos(plate_angle) * plate_dist
            plate_y = 50 + math.sin(plate_angle) * plate_dist
            # 板块碎片
            pygame.draw.rect(plate_surface, (150, 130, 100, 200), (int(plate_x - 3), int(plate_y - 3), 6, 6))
        s.blit(plate_surface, (0, 0))
        
        # 盖亚意志（生命能量脉冲）
        will_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            will_radius = 25 + i * 10 + int(10 * pulse)
            will_alpha = int(200 * (1 - i / 4))
            pygame.draw.circle(will_surface, (100, 200, 150, will_alpha), (60, 50), will_radius, 3)
        s.blit(will_surface, (0, 0))
        
        # 星球之力（能量射线）
        power_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            power_angle = t * 2 + i * math.pi / 6
            power_length = 30 + 15 * (i / 12)
            power_x = 60 + math.cos(power_angle) * power_length
            power_y = 50 + math.sin(power_angle) * power_length
            pygame.draw.line(power_surface, (150, 200, 180, 220), (60, 50), (int(power_x), int(power_y)), 2)
        s.blit(power_surface, (0, 0))
        
        # 大气层（蓝色光晕）
        atmosphere_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            atm_radius = 22 + i * 4
            atm_alpha = int(150 * (1 - i / 3))
            pygame.draw.circle(atmosphere_surface, (100, 180, 255, atm_alpha), (60, 50), atm_radius, 2)
        s.blit(atmosphere_surface, (0, 0))
        
        # 生命之环（绿色生命圈）
        life_ring_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            ring_angle = t * 3 + i * math.pi / 10
            ring_x = 60 + math.cos(ring_angle) * 28
            ring_y = 50 + math.sin(ring_angle) * 28
            pygame.draw.circle(life_ring_surface, (100, 255, 100, 220), (int(ring_x), int(ring_y)), 2)
        s.blit(life_ring_surface, (0, 0))
        
        return s

    # --- Crimson MK3/MK4 ---
    elif model_style == "crimson_samurai":
        # 赤备武士：甲胄
        pygame.draw.polygon(s, (150, 0, 0), [(60, 20), (90, 40), (80, 90), (40, 90), (30, 40)])
        # 金色装饰
        pygame.draw.line(s, (255, 215, 0), (60, 20), (40, 90), 2)
        pygame.draw.line(s, (255, 215, 0), (60, 20), (80, 90), 2)
        # 兜鍪前立
        pygame.draw.polygon(s, (255, 215, 0), [(60, 10), (70, 30), (50, 30)])
        return s

    elif model_style == "crimson_demon":
        # 修罗恶鬼：双角
        pygame.draw.circle(s, (100, 0, 0), (60, 60), 30)
        # 角
        pygame.draw.polygon(s, (200, 200, 200), [(40, 40), (30, 10), (50, 30)])
        pygame.draw.polygon(s, (200, 200, 200), [(80, 40), (90, 10), (70, 30)])
        # 獠牙
        pygame.draw.polygon(s, (255, 255, 255), [(50, 80), (50, 90), (55, 80)])
        pygame.draw.polygon(s, (255, 255, 255), [(70, 80), (70, 90), (65, 80)])
        return s

    # --- Stalker MK3/MK4 ---
    elif model_style == "stalker_predator":
        # 星际掠食：大颚
        pygame.draw.ellipse(s, (50, 100, 0), (40, 40, 40, 60))
        # 颚
        pygame.draw.polygon(s, (100, 150, 50), [(40, 50), (20, 20), (50, 40)])
        pygame.draw.polygon(s, (100, 150, 50), [(80, 50), (100, 20), (70, 40)])
        return s

    elif model_style == "stalker_drone":
        # 蜂群思维：子机群
        positions = [(60, 60), (40, 40), (80, 40), (40, 80), (80, 80)]
        for px, py in positions:
            off_x = math.sin(t * 2 + px) * 5
            off_y = math.cos(t * 2 + py) * 5
            pygame.draw.circle(s, (255, 150, 0), (px + off_x, py + off_y), 8)
            pygame.draw.circle(s, (0, 0, 0), (px + off_x, py + off_y), 3)
        return s

    # --- Gaia MK3/MK4 ---
    elif model_style == "gaia_forest":
        # 森之灵：树叶
        pygame.draw.line(s, (100, 50, 0), (60, 100), (60, 20), 4) # 树干
        # 叶子
        for i in range(6):
            angle = i * math.pi / 3 + t
            lx = 60 + math.cos(angle) * 30
            ly = 50 + math.sin(angle) * 30
            pygame.draw.circle(s, (0, 200, 0), (lx, ly), 10)
        return s

    elif model_style == "gaia_crystal":
        # 晶簇护盾：环绕水晶
        pygame.draw.circle(s, c, (60, 60), 20)
        for i in range(4):
            angle = t + i * math.pi / 2
            cx = 60 + math.cos(angle) * 40
            cy = 60 + math.sin(angle) * 40
            pts = [(cx, cy-10), (cx+10, cy), (cx, cy+10), (cx-10, cy)]
            pygame.draw.polygon(s, (0, 255, 255), pts)
        return s

    # ========== Weaver专属涂装 ==========
    elif model_style == "spider":
        # 蜘蛛之网·命运丝线 - 蜘蛛形态、蛛网编织、命运丝线、猎物困缚
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：蜘蛛身体（头胸部+腹部）
        spider_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 腹部（椭圆）
        pygame.draw.ellipse(spider_surface, (50, 0, 0, 240), (48, 55, 24, 18))
        pygame.draw.ellipse(spider_surface, (150, 50, 50, 220), (48, 55, 24, 18), 2)
        # 头胸部
        pygame.draw.circle(spider_surface, (50, 0, 0, 240), (60, 48), 10)
        pygame.draw.circle(spider_surface, (150, 50, 50, 220), (60, 48), 10, 2)
        s.blit(spider_surface, (0, 0))
        
        # 蜘蛛八脚（动态摆动）
        leg_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            leg_angle = i * math.pi / 4
            leg_swing = math.sin(t * 4 + i) * 0.3
            # 第一段腿
            leg1_angle = leg_angle + leg_swing
            leg1_x = 60 + math.cos(leg1_angle) * 18
            leg1_y = 50 + math.sin(leg1_angle) * 18
            pygame.draw.line(leg_surface, (100, 20, 20, 220), (60, 50), (int(leg1_x), int(leg1_y)), 3)
            # 第二段腿
            leg2_angle = leg1_angle + 0.5
            leg2_x = leg1_x + math.cos(leg2_angle) * 15
            leg2_y = leg1_y + math.sin(leg2_angle) * 15
            pygame.draw.line(leg_surface, (100, 20, 20, 220), (int(leg1_x), int(leg1_y)), 
                           (int(leg2_x), int(leg2_y)), 2)
        s.blit(leg_surface, (0, 0))
        
        # 命运丝线（从腹部喷出）
        silk_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            silk_angle = t * 2 + i * math.pi / 6
            silk_length = 20 + 15 * math.sin(t * 3 + i)
            silk_x = 60 + math.cos(silk_angle) * silk_length
            silk_y = 65 + math.sin(silk_angle) * silk_length
            pygame.draw.line(silk_surface, (220, 220, 220, 180), (60, 65), 
                           (int(silk_x), int(silk_y)), 1)
        s.blit(silk_surface, (0, 0))
        
        # 蛛网节点
        web_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            web_angle = i * math.pi / 4
            web_dist = 35 + 8 * math.sin(t * 2 + i)
            web_x = 60 + math.cos(web_angle) * web_dist
            web_y = 50 + math.sin(web_angle) * web_dist
            pygame.draw.circle(web_surface, (255, 255, 255, 200), (int(web_x), int(web_y)), 3)
        s.blit(web_surface, (0, 0))
        
        return s
    
    elif model_style == "web":
        # 虚空编织·命运之网 - 虚空蛛网、粘连粒子、困阵效果、命运编织
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心编织点
        center_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(center_surface, (200, 200, 200, 240), (60, 50), 12)
        pygame.draw.circle(center_surface, (255, 255, 255, 220), (60, 50), int(12 * pulse))
        s.blit(center_surface, (0, 0))
        
        # 主要蛛网丝线（放射状）
        web_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            web_angle = i * math.pi / 6 + t * 0.2
            web_length = 35 + 10 * math.sin(t * 2 + i)
            web_x = 60 + math.cos(web_angle) * web_length
            web_y = 50 + math.sin(web_angle) * web_length
            pygame.draw.line(web_surface, (220, 220, 220, 200), (60, 50), 
                           (int(web_x), int(web_y)), 2)
            # 末端节点
            pygame.draw.circle(web_surface, (255, 255, 255, 220), (int(web_x), int(web_y)), 4)
        s.blit(web_surface, (0, 0))
        
        # 环状蛛网（同心圆）
        ring_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            ring_radius = 15 + i * 10
            ring_alpha = int(180 - i * 40)
            pygame.draw.circle(ring_surface, (220, 220, 220, ring_alpha), (60, 50), ring_radius, 1)
        s.blit(ring_surface, (0, 0))
        
        # 粘连粒子（困住目标）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 3 + i * math.pi / 10
            particle_dist = 20 + 25 * (i / 20)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (255, 255, 255, 200), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        # 命运丝线连接（随机连接）
        connection_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            if (int(t * 5) + i) % 3 < 2:
                angle1 = i * math.pi / 4
                angle2 = (i + 2) * math.pi / 4
                x1 = 60 + math.cos(angle1) * 35
                y1 = 50 + math.sin(angle1) * 35
                x2 = 60 + math.cos(angle2) * 35
                y2 = 50 + math.sin(angle2) * 35
                pygame.draw.line(connection_surface, (240, 240, 240, 150), 
                               (int(x1), int(y1)), (int(x2), int(y2)), 1)
        s.blit(connection_surface, (0, 0))
        
        return s
    
    elif model_style == "silk":
        # 丝绸之路·空间织布 - 丝绸纹理、空间编织、柔韧丝线、万物连接
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：丝绸卷轴形态
        silk_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 卷轴中心
        pygame.draw.ellipse(silk_surface, (220, 220, 220, 240), (45, 40, 30, 20))
        pygame.draw.ellipse(silk_surface, (255, 255, 255, 220), (45, 40, 30, 20), 2)
        s.blit(silk_surface, (0, 0))
        
        # 丝线缠绕（螺旋）
        thread_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(30):
            thread_angle = t * 2 + i * 0.2
            thread_dist = 15 + (i / 30) * 25
            thread_x = 60 + math.cos(thread_angle) * thread_dist
            thread_y = 50 + math.sin(thread_angle) * thread_dist
            if i < 29:
                next_angle = t * 2 + (i + 1) * 0.2
                next_dist = 15 + ((i + 1) / 30) * 25
                next_x = 60 + math.cos(next_angle) * next_dist
                next_y = 50 + math.sin(next_angle) * next_dist
                pygame.draw.line(thread_surface, (240, 240, 240, 200), 
                               (int(thread_x), int(thread_y)), 
                               (int(next_x), int(next_y)), 2)
        s.blit(thread_surface, (0, 0))
        
        # 丝绸光泽（流动高光）
        sheen_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            sheen_angle = t * 3 + i * math.pi / 5
            sheen_dist = 20 + 15 * math.sin(t * 2 + i)
            sheen_x = 60 + math.cos(sheen_angle) * sheen_dist
            sheen_y = 50 + math.sin(sheen_angle) * sheen_dist
            sheen_size = 3 + 2 * math.sin(t * 4 + i)
            pygame.draw.circle(sheen_surface, (255, 255, 255, 220), 
                             (int(sheen_x), int(sheen_y)), int(sheen_size))
        s.blit(sheen_surface, (0, 0))
        
        # 柔韧波动（波浪纹）
        wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            wave_y = 30 + i * 8
            wave_points = []
            for j in range(15):
                wave_x = 20 + j * 7
                wave_offset_y = wave_y + 5 * math.sin(t * 3 + j * 0.5 + i)
                wave_points.append((wave_x, wave_offset_y))
            for j in range(len(wave_points) - 1):
                pygame.draw.line(wave_surface, (240, 240, 240, 180), 
                               (int(wave_points[j][0]), int(wave_points[j][1])),
                               (int(wave_points[j+1][0]), int(wave_points[j+1][1])), 2)
        s.blit(wave_surface, (0, 0))
        
        return s
    
    elif model_style == "network":
        # 网络编织·数据之网 - 数据网络、信息流动、网络节点、万物互联
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：中心服务器/路由器
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(core_surface, (0, 150, 255, 240), (50, 40, 20, 20))
        pygame.draw.rect(core_surface, (100, 200, 255, 220), (50, 40, 20, 20), 2)
        # 脉冲效果
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.rect(core_glow, (0, 200, 255, int(150 * pulse)), 
                        (50 - int(5 * pulse), 40 - int(5 * pulse), 
                         20 + int(10 * pulse), 20 + int(10 * pulse)))
        s.blit(core_glow, (0, 0))
        s.blit(core_surface, (0, 0))
        
        # 网络节点（8个）
        node_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        nodes = []
        for i in range(8):
            node_angle = i * math.pi / 4 + t * 0.5
            node_dist = 35
            node_x = 60 + math.cos(node_angle) * node_dist
            node_y = 50 + math.sin(node_angle) * node_dist
            nodes.append((node_x, node_y))
            pygame.draw.circle(node_surface, (100, 200, 255, 240), (int(node_x), int(node_y)), 5)
            pygame.draw.circle(node_surface, (0, 150, 255, 220), (int(node_x), int(node_y)), 5, 1)
        s.blit(node_surface, (0, 0))
        
        # 数据连接线（从中心到节点）
        connection_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for node in nodes:
            pygame.draw.line(connection_surface, (50, 180, 255, 200), (60, 50), 
                           (int(node[0]), int(node[1])), 2)
        s.blit(connection_surface, (0, 0))
        
        # 数据包流动（沿连接线移动）
        packet_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            packet_progress = ((t * 2 + i * 0.5) % 2) / 2
            packet_x = 60 + (nodes[i][0] - 60) * packet_progress
            packet_y = 50 + (nodes[i][1] - 50) * packet_progress
            pygame.draw.circle(packet_surface, (0, 255, 255, 240), (int(packet_x), int(packet_y)), 3)
        s.blit(packet_surface, (0, 0))
        
        # 信息脉冲（扩散波）
        for i in range(3):
            pulse_radius = (t * 60 + i * 30) % 90
            pulse_alpha = int(200 * (1 - pulse_radius / 90))
            pulse_wave = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(pulse_wave, (0, 200, 255, pulse_alpha), (60, 50), int(pulse_radius), 2)
            s.blit(pulse_wave, (0, 0))
        
        return s
    
    elif model_style == "matrix":
        # 矩阵编织·代码之丝 - 矩阵代码、程序丝线、源代码、世界重写
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：矩阵核心
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_surface, (0, 255, 0, 250), (60, 50), 14)
        pygame.draw.circle(core_surface, (100, 255, 100, 230), (60, 50), int(14 * pulse))
        s.blit(core_surface, (0, 0))
        
        # 代码流（垂直下落的字符）
        code_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            code_x = 20 + i * 9
            # 每列代码的长度和位置不同
            code_length = 25 + int(15 * math.sin(t * 2 + i))
            code_y_start = ((t * 50 + i * 10) % 140) - 20
            # 绘制代码串（渐变）
            for j in range(int(code_length / 3)):
                char_y = code_y_start + j * 3
                if 0 <= char_y <= 120:
                    char_alpha = int(220 * (1 - j * 3 / code_length))
                    pygame.draw.rect(code_surface, (0, 255, 0, char_alpha), (code_x, int(char_y), 2, 2))
        s.blit(code_surface, (0, 0))
        
        # 矩阵网格（背景）
        grid_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(0, 120, 12):
            grid_alpha = int(80 + 60 * math.sin(t * 2 + i * 0.1))
            pygame.draw.line(grid_surface, (0, 200, 0, grid_alpha), (0, i), (120, i), 1)
            pygame.draw.line(grid_surface, (0, 200, 0, grid_alpha), (i, 0), (i, 120), 1)
        s.blit(grid_surface, (0, 0))
        
        # 程序节点（编织点）
        node_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            node_angle = t * 2 + i * math.pi / 4
            node_dist = 30 + 8 * math.sin(t * 2.5 + i)
            node_x = 60 + math.cos(node_angle) * node_dist
            node_y = 50 + math.sin(node_angle) * node_dist
            pygame.draw.circle(node_surface, (0, 255, 100, 240), (int(node_x), int(node_y)), 4)
            # 连接到中心
            pygame.draw.line(node_surface, (0, 255, 0, 180), (60, 50), 
                           (int(node_x), int(node_y)), 1)
        s.blit(node_surface, (0, 0))
        
        # 源代码脉冲
        pulse_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            pulse_radius = (t * 55 + i * 25) % 100
            pulse_alpha = int(200 * (1 - pulse_radius / 100))
            pygame.draw.circle(pulse_surface, (0, 255, 0, pulse_alpha), (60, 50), int(pulse_radius), 2)
        s.blit(pulse_surface, (0, 0))
        
        return s

    # --- Weaver MK3/MK4 ---
    elif model_style == "weaver_spider":
        # 黑寡妇：八脚
        pygame.draw.circle(s, (20, 20, 20), (60, 60), 20)
        pygame.draw.circle(s, (255, 0, 0), (60, 60), 5) # 沙漏标记
        for i in range(8):
            angle = i * math.pi / 4
            ex = 60 + math.cos(angle) * 45
            ey = 60 + math.sin(angle) * 45
            pygame.draw.line(s, (50, 50, 50), (60, 60), (ex, ey), 2)
            pygame.draw.circle(s, (50, 50, 50), (ex, ey), 3)
        return s

    elif model_style == "weaver_matrix":
        # 矩阵黑客：代码流
        for i in range(5):
            x = 30 + i * 15
            h = 40 + 20 * math.sin(t * 5 + i)
            pygame.draw.line(s, (0, 255, 0), (x, 20), (x, 20 + h), 2)
            pygame.draw.circle(s, (200, 255, 200), (x, 20 + h), 2)
        return s

    # --- Solar MK3/MK4 ---
    elif model_style == "solar_phoenix":
        # 浴火凤凰：鸟形
        pygame.draw.polygon(s, (255, 100, 0), [(60, 20), (80, 50), (60, 90), (40, 50)])
        # 翅膀
        wing_y = 50 + 10 * math.sin(t * 10)
        pygame.draw.polygon(s, (255, 50, 0), [(60, 40), (110, wing_y), (80, 70)])
        pygame.draw.polygon(s, (255, 50, 0), [(60, 40), (10, wing_y), (40, 70)])
        return s

    elif model_style == "solar_fusion":
        # 核聚变：环形
        pygame.draw.circle(s, (255, 255, 255), (60, 60), 15) # 核心
        # 环
        pygame.draw.ellipse(s, (100, 100, 255), (20, 40, 80, 40), 3)
        pygame.draw.ellipse(s, (100, 100, 255), (40, 20, 40, 80), 3)
        return s

    # --- Arbiter MK3/MK4 ---
    elif model_style == "arbiter_judge":
        # 末日审判：天平
        pygame.draw.line(s, (255, 215, 0), (60, 20), (60, 100), 4) # 中轴
        pygame.draw.line(s, (255, 215, 0), (20, 40), (100, 40), 4) # 横梁
        # 托盘
        y_off = 10 * math.sin(t)
        pygame.draw.line(s, c, (20, 40), (20, 70 + y_off), 1)
        pygame.draw.circle(s, c, (20, 75 + y_off), 10)
        pygame.draw.line(s, c, (100, 40), (100, 70 - y_off), 1)
        pygame.draw.circle(s, c, (100, 75 - y_off), 10)
        return s

    elif model_style == "arbiter_fractal":
        # 分形几何：三角形递归
        def draw_tri(surf, p1, p2, p3, depth):
            if depth == 0:
                pygame.draw.polygon(surf, (255, 0, 255), [p1, p2, p3], 1)
                return
            mid1 = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
            mid2 = ((p2[0]+p3[0])/2, (p2[1]+p3[1])/2)
            mid3 = ((p3[0]+p1[0])/2, (p3[1]+p1[1])/2)
            draw_tri(surf, p1, mid1, mid3, depth-1)
            draw_tri(surf, mid1, p2, mid2, depth-1)
            draw_tri(surf, mid3, mid2, p3, depth-1)
        
        draw_tri(s, (60, 20), (100, 90), (20, 90), 3)
        return s

    # --- Eclipse MK3/MK4 ---
    elif model_style == "eclipse_moon":
        # 血月降临：新月
        pygame.draw.circle(s, (200, 0, 0), (60, 60), 40)
        pygame.draw.circle(s, (0, 0, 0), (75, 50), 35) # 遮挡
        return s

    elif model_style == "eclipse_void":
        # 虚空吞噬：黑洞
        pygame.draw.circle(s, (0, 0, 0), (60, 60), 20)
        pygame.draw.circle(s, (100, 0, 200), (60, 60), 22, 2)
        # 吸积盘
        pygame.draw.ellipse(s, (50, 0, 100), (20, 50, 80, 20), 2)
        return s

    # --- Prism MK3/MK4 ---
    elif model_style == "prism_diamond":
        # 璀璨钻石：菱形
        pygame.draw.polygon(s, (200, 200, 255), [(60, 20), (90, 60), (60, 100), (30, 60)])
        pygame.draw.line(s, (255, 255, 255), (30, 60), (90, 60), 1)
        pygame.draw.line(s, (255, 255, 255), (60, 20), (60, 100), 1)
        return s

    elif model_style == "prism_refraction":
        # 光之折射：重叠三角
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        for i in range(3):
            off = i * 5
            pts = [(60, 20+off), (100-off, 90), (20+off, 90)]
            pygame.draw.polygon(s, colors[i], pts, 2)
        return s

    # --- Necro MK3/MK4 ---
    elif model_style == "necro_reaper":
        # 灵魂收割：大镰刀
        pygame.draw.arc(s, (150, 150, 150), (20, 20, 80, 80), 0, 3.14, 5)
        pygame.draw.line(s, (100, 50, 50), (60, 60), (60, 110), 4)
        return s

    elif model_style == "necro_bone":
        # 白骨战机：脊椎
        for i in range(6):
            y = 20 + i * 12
            w = 40 - abs(i - 3) * 10
            pygame.draw.rect(s, (220, 220, 220), (60 - w/2, y, w, 8))
        pygame.draw.line(s, (200, 200, 200), (60, 20), (60, 100), 4)
        return s

    # --- Striker MK5/MK6 ---
    elif model_style == "striker_overload":
        # 核心过载：原型基础上增加熔岩裂纹和高温光晕
        # 基础形状
        pygame.draw.polygon(s, (100, 50, 0), [(60, 10), (110, 90), (60, 110), (10, 90)])
        pygame.draw.polygon(s, (255, 100, 0), [(60, 15), (105, 90), (60, 105), (15, 90)])
        # 熔岩裂纹
        for i in range(5):
            p1 = (random.randint(30, 90), random.randint(30, 90))
            p2 = (p1[0] + random.randint(-10, 10), p1[1] + random.randint(-10, 10))
            pygame.draw.line(s, (255, 255, 0), p1, p2, 2)
        # 核心脉动
        core_size = int(10 + 5 * pulse)
        pygame.draw.circle(s, (255, 255, 200), (60, 50), core_size)
        return s

    elif model_style == "striker_hologram":
        # 全息投影：线框模式
        pts = [(60, 10), (110, 90), (60, 110), (10, 90)]
        pygame.draw.polygon(s, (0, 255, 255), pts, 1)
        # 扫描线
        scan_y = int(t * 50) % 120
        pygame.draw.line(s, (0, 255, 255), (0, scan_y), (120, scan_y), 1)
        return s

    # --- Phantom MK5/MK6 ---
    elif model_style == "phantom_void":
        # 虚空行者：深色背景+星光
        pts = [(60, 10), (90, 50), (120, 110), (60, 90), (0, 110), (30, 50)]
        pygame.draw.polygon(s, (20, 0, 40), pts)
        # 星光
        for i in range(10):
            px = random.randint(20, 100)
            py = random.randint(20, 100)
            pygame.draw.circle(s, (255, 255, 255), (px, py), 1)
        pygame.draw.polygon(s, (100, 50, 150), pts, 2)
        return s

    elif model_style == "phantom_phase":
        # 相位偏移：RGB分离效果
        pts = [(60, 10), (90, 50), (120, 110), (60, 90), (0, 110), (30, 50)]
        # 红层
        pygame.draw.polygon(s, (255, 0, 0), [(p[0]-2, p[1]) for p in pts], 1)
        # 蓝层
        pygame.draw.polygon(s, (0, 0, 255), [(p[0]+2, p[1]) for p in pts], 1)
        # 主体
        pygame.draw.polygon(s, (255, 255, 255), pts, 1)
        return s

    # --- Titan MK5/MK6 ---
    elif model_style == "titan_reactor":
        # 聚变反应堆：核心暴露
        pygame.draw.rect(s, (50, 50, 50), (20, 20, 80, 80))
        # 反应堆核心
        pygame.draw.circle(s, (0, 255, 0), (60, 60), 25)
        pygame.draw.circle(s, (200, 255, 200), (60, 60), 20 + int(5 * pulse))
        # 辐射标志
        pygame.draw.line(s, (0, 100, 0), (60, 60), (60, 30), 3)
        pygame.draw.line(s, (0, 100, 0), (60, 60), (85, 75), 3)
        pygame.draw.line(s, (0, 100, 0), (60, 60), (35, 75), 3)
        return s

    elif model_style == "titan_bastion":
        # 钢铁壁垒：额外装甲
        pygame.draw.rect(s, (100, 100, 100), (15, 15, 90, 90))
        pygame.draw.rect(s, (150, 150, 150), (25, 25, 70, 70))
        # 铆钉细节
        for x in [20, 100]:
            for y in [20, 100]:
                pygame.draw.circle(s, (50, 50, 50), (x, y), 3)
        return s

    # --- Thunderbird MK5/MK6 ---
    elif model_style == "thunderbird_plasma":
        # 等离子风暴：紫色光晕
        pts = [(60, 0), (20, 60), (0, 40), (20, 100), (60, 80), (100, 100), (120, 40), (100, 60)]
        pygame.draw.polygon(s, (100, 0, 100), pts)
        # 等离子流
        for i in range(3):
            y = 20 + i * 20 + int(t * 20) % 60
            pygame.draw.line(s, (255, 0, 255), (0, y), (120, y), 2)
        return s

    elif model_style == "thunderbird_sonic":
        # 超音速爆轰：音爆云
        pts = [(60, 0), (20, 60), (0, 40), (20, 100), (60, 80), (100, 100), (120, 40), (100, 60)]
        pygame.draw.polygon(s, (200, 200, 255), pts)
        # 音爆环
        pygame.draw.ellipse(s, (255, 255, 255), (10, 40 + int(5 * math.sin(t*10)), 100, 20), 2)
        return s

    # --- Viper MK5/MK6 ---
    elif model_style == "viper_acid":
        # 酸蚀之牙：滴落效果
        pts = [(60, 0), (100, 40), (80, 100), (40, 100), (20, 40)]
        pygame.draw.polygon(s, (50, 150, 0), pts)
        # 酸液滴落
        drop_y = int(t * 100) % 120
        pygame.draw.circle(s, (100, 255, 0), (60, drop_y), 4)
        pygame.draw.circle(s, (100, 255, 0), (30, (drop_y + 40) % 120), 3)
        pygame.draw.circle(s, (100, 255, 0), (90, (drop_y + 80) % 120), 3)
        return s

    elif model_style == "viper_shadow":
        # 暗影潜行：全黑+红眼
        pts = [(60, 0), (100, 40), (80, 100), (40, 100), (20, 40)]
        pygame.draw.polygon(s, (10, 10, 10), pts)
        pygame.draw.polygon(s, (50, 50, 50), pts, 2)
        # 红眼
        pygame.draw.circle(s, (255, 0, 0), (40, 40), 3)
        pygame.draw.circle(s, (255, 0, 0), (80, 40), 3)
        return s

    # --- Specter MK5/MK6 ---
    elif model_style == "specter_poltergeist":
        # 骚灵现象：漂浮物
        pts = [(60, 0), (80, 80), (60, 100), (40, 80)]
        pygame.draw.polygon(s, (100, 50, 150), pts)
        # 漂浮碎块
        for i in range(5):
            ox = math.sin(t * 2 + i) * 20
            oy = math.cos(t * 3 + i) * 20
            pygame.draw.rect(s, (200, 100, 255), (60 + ox, 50 + oy, 5, 5))
        return s

    elif model_style == "specter_wraith":
        # 幽冥鬼影：透明骨架
        pts = [(60, 0), (80, 80), (60, 100), (40, 80)]
        pygame.draw.polygon(s, (100, 255, 255), pts, 1)
        # 内部骨架
        pygame.draw.line(s, (200, 255, 255), (60, 10), (60, 90), 2)
        pygame.draw.line(s, (200, 255, 255), (40, 80), (80, 80), 2)
        return s

    # --- Aurora MK5/MK6 ---
    elif model_style == "aurora_starlight":
        # 星光熠熠：闪烁点
        pygame.draw.circle(s, (255, 255, 200), (60, 60), 50)
        # 闪烁
        for i in range(10):
            if random.random() < 0.5:
                px = random.randint(20, 100)
                py = random.randint(20, 100)
                if math.hypot(px-60, py-60) < 50:
                    pygame.draw.circle(s, (255, 255, 255), (px, py), 2)
        return s

    elif model_style == "aurora_prism":
        # 棱镜光辉：分色
        pygame.draw.circle(s, (255, 255, 255), (60, 60), 50, 2)
        # 内部三角
        pygame.draw.polygon(s, (255, 0, 0), [(60, 20), (95, 80), (25, 80)], 1)
        pygame.draw.polygon(s, (0, 255, 0), [(60, 25), (90, 75), (30, 75)], 1)
        pygame.draw.polygon(s, (0, 0, 255), [(60, 30), (85, 70), (35, 70)], 1)
        return s

    # --- Crimson MK5/MK6 ---
    elif model_style == "crimson_inferno":
        # 炼狱之火：流动岩浆
        pts = [(50, 80), (20, 20), (50, 40), (80, 20)]
        pygame.draw.polygon(s, (255, 50, 0), pts)
        # 岩浆纹路
        for i in range(5):
            y = 20 + i * 10 + int(t * 10) % 60
            pygame.draw.line(s, (255, 255, 0), (30, y), (70, y), 2)
        return s

    elif model_style == "crimson_bloodmoon":
        # 猩红血月：暗红+月亮
        pts = [(50, 80), (20, 20), (50, 40), (80, 20)]
        pygame.draw.polygon(s, (100, 0, 0), pts)
        # 血月标记
        pygame.draw.circle(s, (200, 0, 0), (50, 30), 10)
        return s

    # --- Stalker MK5/MK6 ---
    elif model_style == "stalker_chameleon":
        # 变色龙：颜色变化
        pts = [(50, 10), (30, 50), (10, 40), (30, 70), (50, 90), (70, 70), (90, 40), (70, 50)]
        # 颜色循环
        r = int(127 + 127 * math.sin(t))
        g = int(127 + 127 * math.sin(t + 2))
        b = int(127 + 127 * math.sin(t + 4))
        pygame.draw.polygon(s, (r, g, b), pts)
        pygame.draw.polygon(s, (255, 255, 255), pts, 2)
        return s

    elif model_style == "stalker_hunter":
        # 赏金猎人：瞄准线
        pts = [(50, 10), (30, 50), (10, 40), (30, 70), (50, 90), (70, 70), (90, 40), (70, 50)]
        pygame.draw.polygon(s, (200, 100, 0), pts)
        # 激光瞄准
        pygame.draw.line(s, (255, 0, 0), (50, 50), (50, 0), 1)
        pygame.draw.circle(s, (255, 0, 0), (50, 50), 3)
        return s

    # --- Gaia MK5/MK6 ---
    elif model_style == "gaia_overgrowth":
        # 野蛮生长：满是藤蔓
        pts = [(30, 20), (70, 20), (90, 60), (70, 90), (30, 90), (10, 60)]
        pygame.draw.polygon(s, (0, 100, 0), pts)
        # 藤蔓乱画
        for i in range(10):
            start = (random.randint(20, 80), random.randint(20, 80))
            end = (start[0] + random.randint(-10, 10), start[1] + random.randint(-10, 10))
            pygame.draw.line(s, (0, 200, 50), start, end, 2)
        return s

    elif model_style == "gaia_elemental":
        # 元素之灵：四色
        pts = [(30, 20), (70, 20), (90, 60), (70, 90), (30, 90), (10, 60)]
        center = (50, 50)
        # 分割四块
        pygame.draw.polygon(s, (255, 0, 0), [center, (30, 20), (70, 20)]) # 火
        pygame.draw.polygon(s, (0, 0, 255), [center, (70, 20), (90, 60)]) # 水
        pygame.draw.polygon(s, (0, 255, 0), [center, (90, 60), (70, 90)]) # 风
        pygame.draw.polygon(s, (150, 100, 0), [center, (70, 90), (30, 90)]) # 地
        return s

    # --- Weaver MK5/MK6 ---
    elif model_style == "weaver_network":
        # 神经网络：节点连接
        pygame.draw.circle(s, (0, 0, 100), (60, 60), 25)
        # 节点
        nodes = [(60, 35), (35, 60), (85, 60), (60, 85)]
        for p in nodes:
            pygame.draw.circle(s, (0, 200, 255), p, 4)
            pygame.draw.line(s, (0, 100, 255), (60, 60), p, 2)
        return s

    elif model_style == "weaver_silk":
        # 天蚕丝：白色柔光
        pygame.draw.circle(s, (200, 200, 200), (60, 60), 25)
        # 丝线缠绕
        for i in range(0, 360, 20):
            rad = math.radians(i + t * 20)
            x = 60 + math.cos(rad) * 25
            y = 60 + math.sin(rad) * 25
            pygame.draw.line(s, (255, 255, 255), (60, 60), (x, y), 1)
        return s

    elif model_style == "weaver_web":
        # 命运之网 - 虚空蛛网、粘连粒子、困阵效果
        web_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 中心点与多条丝线
        center = (60, 60)
        pygame.draw.circle(web_surface, (30, 30, 30, 220), center, 18)
        for i in range(10):
            angle = i * math.pi * 2 / 10 + t * 0.2
            ex = 60 + math.cos(angle) * (28 + 6 * math.sin(t * 2 + i))
            ey = 60 + math.sin(angle) * (28 + 6 * math.sin(t * 2 + i))
            pygame.draw.line(web_surface, (200, 200, 220, 200), center, (int(ex), int(ey)), 1)
            # 节点
            pygame.draw.circle(web_surface, (180, 220, 255, 200), (int(ex), int(ey)), 3)

        # 细网交织
        for i in range(20):
            a1 = i * math.pi * 2 / 20 + t * 0.1
            a2 = a1 + 0.5 + 0.2 * math.sin(t + i)
            x1 = 60 + math.cos(a1) * 15
            y1 = 60 + math.sin(a1) * 15
            x2 = 60 + math.cos(a2) * 35
            y2 = 60 + math.sin(a2) * 35
            pygame.draw.aaline(web_surface, (220, 220, 255, 120), (int(x1), int(y1)), (int(x2), int(y2)))

        # 粘性粒子（困住目标的微粒）
        for i in range(18):
            pa = t * 4 + i * math.pi / 9
            pd = 20 + (i % 6) * 6 + 4 * math.sin(t * 3 + i)
            px = 60 + math.cos(pa) * pd
            py = 60 + math.sin(pa) * pd
            pygame.draw.circle(web_surface, (180, 240, 255, 200), (int(px), int(py)), 2)

        s.blit(web_surface, (0, 0))
        return s

    elif model_style == "weaver_destiny":
        # 命运编织者 - 因果线、节点与闪烁符文
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1

        # 命运节点
        nodes = []
        for i in range(6):
            ang = i * math.pi * 2 / 6 + math.sin(t + i) * 0.2
            nx = 60 + math.cos(ang) * (22 + 6 * math.sin(t * 1.5 + i))
            ny = 50 + math.sin(ang) * (22 + 6 * math.sin(t * 1.5 + i))
            nodes.append((int(nx), int(ny)))
            pygame.draw.circle(s, (255, 230, 150, 220), (int(nx), int(ny)), 4)

        # 因果线连接并闪烁
        for i in range(len(nodes)):
            a = nodes[i]
            b = nodes[(i + 2) % len(nodes)]
            alpha = int(160 + 80 * math.sin(t * 3 + i))
            pygame.draw.line(s, (200, 200, 255, alpha), a, b, 2)

        # 中心符文
        center_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        cg = int(6 * pulse)
        pygame.draw.circle(center_glow, (255, 200, 100, 220), (60, 50), cg)
        pygame.draw.circle(center_glow, (255, 240, 200, 150), (60, 50), cg + 4)
        s.blit(center_glow, (0, 0))

        # 流动的命运粒子
        part = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(14):
            pa = t * 3 + i * math.pi / 7
            pd = 12 + (i % 5) * 6 + 4 * math.sin(t * 2 + i)
            px = 60 + math.cos(pa) * pd
            py = 50 + math.sin(pa) * pd
            pygame.draw.circle(part, (255, 220, 150, 200), (int(px), int(py)), 2)
        s.blit(part, (0, 0))

        return s

    elif model_style == "weaver_cosmic":
        # 宇宙编织 - 星河与丝线，星尘汇聚
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 背景星云
        neb = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(30):
            nx = random.randint(10, 110)
            ny = random.randint(10, 100)
            nr = random.randint(1, 3)
            col = (150 + random.randint(0,100), 100 + random.randint(0,120), 200 + random.randint(0,55), 30)
            pygame.draw.circle(neb, col, (nx, ny), nr)
        s.blit(neb, (0, 0))

        # 星河丝线（亮线）
        for i in range(8):
            angle = i * math.pi * 2 / 8 + t * 0.1
            sx = 60 + math.cos(angle) * (25 + 8 * math.sin(t * 1.5 + i))
            sy = 50 + math.sin(angle) * (25 + 8 * math.sin(t * 1.5 + i))
            pygame.draw.aaline(s, (200, 200, 255), (60, 50), (int(sx), int(sy)))

        # 旋转星群
        star_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(18):
            sa = t * 2 + i * math.pi / 9
            sd = 18 + (i % 6) * 4
            sx = 60 + math.cos(sa) * sd
            sy = 50 + math.sin(sa) * sd
            pygame.draw.circle(star_surface, (255, 255, 220, 220), (int(sx), int(sy)), 2)
        s.blit(star_surface, (0, 0))

        # 中心星核
        pygame.draw.circle(s, (240, 200, 255), (60, 50), 6)
        pygame.draw.circle(s, (200, 160, 255, 150), (60, 50), 12, 2)

        return s
    
    # ========== Solar专属涂装 ==========
    elif model_style == "sun_god":
        # 太阳神拉·审判 - 太阳神形态、神圣光芒、审判之光
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：太阳神核心
        sun_core = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(sun_core, (255, 200, 0, 250), (60, 50), 18)
        pygame.draw.circle(sun_core, (255, 255, 100, 220), (60, 50), int(18 * pulse))
        s.blit(sun_core, (0, 0))
        
        # 太阳神光环（多层）
        for i in range(4):
            ring_radius = 22 + i * 8 + int(6 * pulse)
            ring_alpha = int(200 * (1 - i / 4))
            ring_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ring_surface, (255, 220, 50, ring_alpha), (60, 50), ring_radius, 3)
            s.blit(ring_surface, (0, 0))
        
        # 神圣光芒（放射状）
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            ray_angle = t * 1.5 + i * math.pi / 8
            ray_length = 30 + 15 * math.sin(t * 3 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 50 + math.sin(ray_angle) * ray_length
            pygame.draw.line(ray_surface, (255, 255, 100, 220), (60, 50), (int(ray_x), int(ray_y)), 3)
        s.blit(ray_surface, (0, 0))
        
        # 审判之眼（神之凝视）
        eye_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(eye_glow, (255, 255, 200, 250), (60, 50), int(8 * pulse))
        pygame.draw.circle(eye_glow, (255, 200, 0, 200), (60, 50), 6)
        s.blit(eye_glow, (0, 0))
        
        # 神圣粒子
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 2 + i * math.pi / 10
            particle_dist = 25 + 15 * (i / 20)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (255, 255, 200, 220), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        return s
    
    elif model_style == "phoenix":
        # 太阳凤凰·永恒烈焰 - 凤凰形态、涅槃之火、不灭烈焰
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：凤凰身躯
        phoenix_body = [(60, 30), (70, 45), (68, 60), (52, 60), (50, 45)]
        pygame.draw.polygon(s, (255, 100, 0), phoenix_body)
        pygame.draw.polygon(s, (255, 200, 0), phoenix_body, 2)
        
        # 凤凰头冠
        crown_points = [(60, 25), (65, 30), (63, 20), (57, 20), (55, 30)]
        for i, point in enumerate(crown_points):
            flame_y = point[1] - int(5 * math.sin(t * 5 + i))
            pygame.draw.line(s, (255, 150, 0), point, (point[0], flame_y), 2)
            pygame.draw.circle(s, (255, 200, 0), (point[0], flame_y), 2)
        
        # 凤凰翅膀（火焰翅膀）
        for side in [-1, 1]:
            wing_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            for i in range(8):
                wing_angle = side * (math.pi / 3) + i * 0.2 + math.sin(t * 4 + i) * 0.3
                wing_dist = 15 + i * 3
                wing_x = 60 + math.cos(wing_angle) * wing_dist
                wing_y = 48 + math.sin(wing_angle) * wing_dist
                # 火焰羽毛
                flame_length = 8 + int(4 * math.sin(t * 5 + i))
                flame_tip_x = wing_x + math.cos(wing_angle) * flame_length
                flame_tip_y = wing_y + math.sin(wing_angle) * flame_length
                pygame.draw.line(wing_surface, (255, 100, 0, 220), (int(wing_x), int(wing_y)), 
                               (int(flame_tip_x), int(flame_tip_y)), 3)
                pygame.draw.circle(wing_surface, (255, 200, 0, 220), (int(flame_tip_x), int(flame_tip_y)), 2)
            s.blit(wing_surface, (0, 0))
        
        # 凤凰尾羽（火焰尾迹）
        tail_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            tail_angle = math.pi / 2 + (i - 5) * 0.1 + math.sin(t * 3 + i) * 0.2
            tail_dist = 15 + i * 4
            tail_x = 60 + math.cos(tail_angle) * tail_dist
            tail_y = 60 + math.sin(tail_angle) * tail_dist
            tail_alpha = int(220 - i * 15)
            pygame.draw.circle(tail_surface, (255, 150, 0, tail_alpha), (int(tail_x), int(tail_y)), 4 - i // 3)
        s.blit(tail_surface, (0, 0))
        
        # 涅槃之火（环绕火焰）
        fire_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            fire_angle = t * 4 + i * math.pi / 8
            fire_dist = 22 + 8 * math.sin(t * 3 + i)
            fire_x = 60 + math.cos(fire_angle) * fire_dist
            fire_y = 48 + math.sin(fire_angle) * fire_dist
            pygame.draw.circle(fire_surface, (255, 100, 0, 220), (int(fire_x), int(fire_y)), 3)
        s.blit(fire_surface, (0, 0))
        
        # 不灭烈焰（核心脉冲）
        for i in range(3):
            flame_radius = 15 + i * 8 + int(8 * pulse)
            flame_alpha = int(180 * (1 - i / 3))
            flame_ring = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(flame_ring, (255, 150, 0, flame_alpha), (60, 48), flame_radius, 2)
            s.blit(flame_ring, (0, 0))
        
        return s
    
    elif model_style == "fusion":
        # 核聚变·恒星之心 - 核聚变反应、氢氦燃烧、聚变能量
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：聚变核心
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_surface, (100, 150, 255, 250), (60, 50), 15)
        pygame.draw.circle(core_surface, (200, 220, 255, 230), (60, 50), int(15 * pulse))
        s.blit(core_surface, (0, 0))
        
        # 核聚变反应环（多层等离子环）
        for i in range(4):
            ring_angle = t * 2 + i * math.pi / 2
            ring_tilt = 0.3
            # 椭圆环（模拟3D效果）
            ring_radius = 20 + i * 6
            ring_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            ring_alpha = int(200 * (1 - i / 4))
            # 绘制椭圆轨道
            pygame.draw.ellipse(ring_surface, (150, 180, 255, ring_alpha), 
                              (60 - ring_radius, 50 - int(ring_radius * ring_tilt), 
                               ring_radius * 2, int(ring_radius * ring_tilt * 2)), 2)
            s.blit(ring_surface, (0, 0))
        
        # 氢氦原子粒子（环绕运动）
        atom_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            atom_angle = t * 3 + i * math.pi / 6
            atom_dist = 22 + 8 * math.sin(t * 2 + i)
            atom_x = 60 + math.cos(atom_angle) * atom_dist
            atom_y = 50 + math.sin(atom_angle) * atom_dist
            # 氢（蓝色）和氦（白色）交替
            if i % 2 == 0:
                pygame.draw.circle(atom_surface, (150, 200, 255, 220), (int(atom_x), int(atom_y)), 3)
            else:
                pygame.draw.circle(atom_surface, (255, 255, 255, 220), (int(atom_x), int(atom_y)), 3)
        s.blit(atom_surface, (0, 0))
        
        # 聚变能量释放（能量波）
        for i in range(3):
            wave_radius = (t * 60 + i * 30) % 90
            wave_alpha = int(220 * (1 - wave_radius / 90))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (200, 220, 255, wave_alpha), (60, 50), int(wave_radius), 3)
            s.blit(wave_surface, (0, 0))
        
        # 高能光子
        photon_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            photon_angle = t * 4 + i * math.pi / 10
            photon_dist = 15 + ((t * 40 + i * 4) % 30)
            photon_x = 60 + math.cos(photon_angle) * photon_dist
            photon_y = 50 + math.sin(photon_angle) * photon_dist
            photon_alpha = int(220 * (1 - ((t * 40 + i * 4) % 30) / 30))
            pygame.draw.circle(photon_surface, (255, 255, 255, photon_alpha), (int(photon_x), int(photon_y)), 2)
        s.blit(photon_surface, (0, 0))
        
        return s
    
    elif model_style == "flare":
        # 日冕耀斑·太阳风暴 - 耀斑爆发、日冕物质抛射、太阳风
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：太阳表面
        sun_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(sun_surface, (255, 255, 200, 240), (60, 50), 16)
        pygame.draw.circle(sun_surface, (255, 255, 255, 220), (60, 50), int(16 * pulse))
        s.blit(sun_surface, (0, 0))
        
        # 日冕耀斑（巨大火焰喷射）
        for i in range(8):
            flare_angle = t + i * math.pi / 4
            flare_intensity = math.sin(t * 2 + i) * 0.5 + 0.5
            flare_length = 20 + 25 * flare_intensity
            flare_x = 60 + math.cos(flare_angle) * flare_length
            flare_y = 50 + math.sin(flare_angle) * flare_length
            
            # 耀斑主体
            flare_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            flare_width = int(8 * flare_intensity)
            pygame.draw.line(flare_surface, (255, 255, 200, 220), (60, 50), (int(flare_x), int(flare_y)), flare_width)
            # 耀斑尖端
            pygame.draw.circle(flare_surface, (255, 255, 255, 220), (int(flare_x), int(flare_y)), flare_width // 2)
            s.blit(flare_surface, (0, 0))
        
        # 日冕物质抛射（CME粒子流）
        cme_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(30):
            cme_angle = t * 1.5 + i * math.pi / 15
            cme_speed = 2 + (i % 3)
            cme_dist = 18 + ((t * 40 * cme_speed + i * 6) % 40)
            cme_x = 60 + math.cos(cme_angle) * cme_dist
            cme_y = 50 + math.sin(cme_angle) * cme_dist
            cme_alpha = int(220 * (1 - ((t * 40 * cme_speed + i * 6) % 40) / 40))
            pygame.draw.circle(cme_surface, (255, 255, 220, cme_alpha), (int(cme_x), int(cme_y)), 2)
        s.blit(cme_surface, (0, 0))
        
        # 太阳风粒子暴雨
        wind_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(25):
            wind_angle = t * 2.5 + i * math.pi / 12.5
            wind_dist = 15 + ((t * 50 + i * 5) % 35)
            wind_x = 60 + math.cos(wind_angle) * wind_dist
            wind_y = 50 + math.sin(wind_angle) * wind_dist
            pygame.draw.circle(wind_surface, (255, 255, 200, 200), (int(wind_x), int(wind_y)), 1)
        s.blit(wind_surface, (0, 0))
        
        return s
    
    elif model_style == "corona":
        # 日冕王冠·太阳之子 - 日冕光环、黄金光辉、太阳神形态
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：太阳核心
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_glow, (255, 180, 100, 250), (60, 50), 14)
        pygame.draw.circle(core_glow, (255, 220, 150, 230), (60, 50), int(14 * pulse))
        s.blit(core_glow, (0, 0))
        
        # 日冕王冠（多层光环）
        for i in range(5):
            crown_radius = 18 + i * 6 + int(5 * pulse)
            crown_alpha = int(200 * (1 - i / 5))
            crown_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(crown_surface, (255, 200, 120, crown_alpha), (60, 50), crown_radius, 2)
            s.blit(crown_surface, (0, 0))
        
        # 王冠尖刺（辐射状）
        spike_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            spike_angle = i * math.pi / 6
            spike_base_dist = 20
            spike_length = 18 + 8 * math.sin(t * 3 + i)
            spike_base_x = 60 + math.cos(spike_angle) * spike_base_dist
            spike_base_y = 50 + math.sin(spike_angle) * spike_base_dist
            spike_tip_x = 60 + math.cos(spike_angle) * (spike_base_dist + spike_length)
            spike_tip_y = 50 + math.sin(spike_angle) * (spike_base_dist + spike_length)
            # 尖刺
            pygame.draw.line(spike_surface, (255, 220, 150, 220), (int(spike_base_x), int(spike_base_y)), 
                           (int(spike_tip_x), int(spike_tip_y)), 3)
            pygame.draw.circle(spike_surface, (255, 255, 200, 220), (int(spike_tip_x), int(spike_tip_y)), 2)
        s.blit(spike_surface, (0, 0))
        
        # 黄金光辉（环绕粒子）
        golden_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            golden_angle = t * 2 + i * math.pi / 10
            golden_dist = 25 + 10 * math.sin(t * 2.5 + i)
            golden_x = 60 + math.cos(golden_angle) * golden_dist
            golden_y = 50 + math.sin(golden_angle) * golden_dist
            pygame.draw.circle(golden_surface, (255, 220, 150, 220), (int(golden_x), int(golden_y)), 3)
        s.blit(golden_surface, (0, 0))
        
        # 太阳神光芒
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            ray_angle = t * 1.5 + i * math.pi / 4
            ray_length = 35 + 10 * math.sin(t * 3 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 50 + math.sin(ray_angle) * ray_length
            pygame.draw.line(ray_surface, (255, 200, 120, 200), (60, 50), (int(ray_x), int(ray_y)), 2)
        s.blit(ray_surface, (0, 0))
        
        return s
    
    elif model_style == "supernova":
        # 超新星·恒星爆炸 - 超新星爆发、恒星崩解、能量波扩散、星云形成
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.3 + 1
        
        # 主体：爆炸核心（极亮）
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        core_size = int(12 * pulse)
        pygame.draw.circle(core_surface, (255, 255, 255, 250), (60, 50), core_size)
        pygame.draw.circle(core_surface, (255, 200, 255, 230), (60, 50), core_size + 4)
        pygame.draw.circle(core_surface, (255, 230, 255, 200), (60, 50), core_size + 8)
        s.blit(core_surface, (0, 0))
        
        # 超新星爆炸波（多层冲击波）
        for i in range(5):
            wave_phase = (t * 2 + i * 0.4) % 2
            wave_radius = 15 + wave_phase * 35
            wave_alpha = int(220 * (1 - wave_phase / 2))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (255, 230, 255, wave_alpha), (60, 50), int(wave_radius), 4)
            s.blit(wave_surface, (0, 0))
        
        # 恒星碎片（高速喷射）
        debris_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(30):
            debris_angle = i * math.pi / 15
            debris_speed = 1.5 + (i % 3) * 0.5
            debris_dist = 15 + ((t * 50 * debris_speed + i * 3) % 45)
            debris_x = 60 + math.cos(debris_angle) * debris_dist
            debris_y = 50 + math.sin(debris_angle) * debris_dist
            debris_alpha = int(240 * (1 - ((t * 50 * debris_speed + i * 3) % 45) / 45))
            # 碎片（彩色）
            hue = (i * 12) % 360
            r = int(200 + 55 * math.sin(math.radians(hue)))
            g = int(150 + 105 * math.sin(math.radians(hue + 120)))
            b = int(200 + 55 * math.sin(math.radians(hue + 240)))
            pygame.draw.circle(debris_surface, (r, g, b, debris_alpha), (int(debris_x), int(debris_y)), 3)
        s.blit(debris_surface, (0, 0))
        
        # 星云形成（扩散气体）
        nebula_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            nebula_angle = t + i * math.pi / 10
            nebula_dist = 20 + 20 * (i / 20) + 8 * math.sin(t * 2 + i)
            nebula_x = 60 + math.cos(nebula_angle) * nebula_dist
            nebula_y = 50 + math.sin(nebula_angle) * nebula_dist
            nebula_alpha = int(150 * (1 - (i / 20)))
            pygame.draw.circle(nebula_surface, (255, 200, 255, nebula_alpha), (int(nebula_x), int(nebula_y)), 5)
        s.blit(nebula_surface, (0, 0))
        
        # 辐射光线
        radiation_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            rad_angle = t * 2 + i * math.pi / 8
            rad_length = 30 + 15 * math.sin(t * 4 + i)
            rad_x = 60 + math.cos(rad_angle) * rad_length
            rad_y = 50 + math.sin(rad_angle) * rad_length
            pygame.draw.line(radiation_surface, (255, 255, 255, 200), (60, 50), (int(rad_x), int(rad_y)), 2)
        s.blit(radiation_surface, (0, 0))
        
        return s
    
    elif model_style == "eclipse":
        # 日全食·光暗交替 - 日食现象、光暗转换、日冕边缘、贝利珠
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：被遮挡的太阳
        sun_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(sun_surface, (255, 200, 0, 240), (60, 50), 18)
        s.blit(sun_surface, (0, 0))
        
        # 月球遮挡（黑色圆盘）
        moon_offset_x = int(8 * math.sin(t))
        moon_offset_y = int(4 * math.cos(t))
        moon_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(moon_surface, (50, 50, 100, 250), (60 + moon_offset_x, 50 + moon_offset_y), 16)
        s.blit(moon_surface, (0, 0))
        
        # 日冕边缘发光（环形光晕）
        corona_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            corona_radius = 20 + i * 4 + int(3 * pulse)
            corona_alpha = int(200 * (1 - i / 4))
            pygame.draw.circle(corona_surface, (255, 200, 0, corona_alpha), (60, 50), corona_radius, 2)
        s.blit(corona_surface, (0, 0))
        
        # 贝利珠效应（钻石环）
        bailey_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            if (int(t * 3) + i) % 4 < 2:  # 闪烁效果
                bailey_angle = i * math.pi / 4
                bailey_x = 60 + math.cos(bailey_angle) * 18
                bailey_y = 50 + math.sin(bailey_angle) * 18
                pygame.draw.circle(bailey_surface, (255, 255, 255, 250), (int(bailey_x), int(bailey_y)), 3)
                # 光晕
                pygame.draw.circle(bailey_surface, (255, 255, 200, 180), (int(bailey_x), int(bailey_y)), 5)
        s.blit(bailey_surface, (0, 0))
        
        # 日冕流（极光般的流动）
        streamer_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            streamer_angle = i * math.pi / 6 + t * 0.5
            streamer_length = 22 + 10 * math.sin(t * 2 + i)
            streamer_x = 60 + math.cos(streamer_angle) * streamer_length
            streamer_y = 50 + math.sin(streamer_angle) * streamer_length
            pygame.draw.line(streamer_surface, (255, 200, 0, 180), (60, 50), (int(streamer_x), int(streamer_y)), 2)
        s.blit(streamer_surface, (0, 0))
        
        # 光暗交替粒子
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            particle_angle = t * 2.5 + i * math.pi / 7.5
            particle_dist = 25 + 8 * math.sin(t * 3 + i)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            # 交替明暗
            if i % 2 == 0:
                pygame.draw.circle(particle_surface, (255, 200, 0, 220), (int(particle_x), int(particle_y)), 2)
            else:
                pygame.draw.circle(particle_surface, (100, 100, 150, 220), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        return s
    
    # ========== Arbiter专属涂装 ==========
    elif model_style == "quantum":
        # 量子裁决·概率坍缩 - 量子叠加态、概率云、波函数坍缩、量子纠缠
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：量子核心（叠加态）
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 叠加态效果（多个半透明核心）
        for i in range(3):
            offset_x = int(6 * math.sin(t * 3 + i * 2))
            offset_y = int(6 * math.cos(t * 3 + i * 2))
            core_alpha = int(180 - i * 40)
            pygame.draw.circle(core_surface, (180, 100, 255, core_alpha), (60 + offset_x, 50 + offset_y), 12)
        s.blit(core_surface, (0, 0))
        
        # 概率云（漂浮云团）
        cloud_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(25):
            cloud_angle = t * 2 + i * math.pi / 12.5
            cloud_dist = 20 + 15 * (i / 25) + 5 * math.sin(t * 3 + i)
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 50 + math.sin(cloud_angle) * cloud_dist
            cloud_alpha = int(150 * (1 - (i / 25)))
            pygame.draw.circle(cloud_surface, (220, 150, 255, cloud_alpha), (int(cloud_x), int(cloud_y)), 4)
        s.blit(cloud_surface, (0, 0))
        
        # 波函数坍缩（收缩波）
        for i in range(4):
            collapse_phase = (t * 3 + i * 0.5) % 2
            if collapse_phase < 1:  # 收缩阶段
                collapse_radius = 35 - collapse_phase * 20
                collapse_alpha = int(200 * collapse_phase)
            else:  # 扩散阶段
                collapse_radius = 15 + (collapse_phase - 1) * 20
                collapse_alpha = int(200 * (2 - collapse_phase))
            collapse_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(collapse_surface, (180, 100, 255, collapse_alpha), (60, 50), int(collapse_radius), 2)
            s.blit(collapse_surface, (0, 0))
        
        # 量子纠缠（粒子对连接）
        entangle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            angle1 = t * 2 + i * math.pi / 3
            angle2 = angle1 + math.pi
            dist = 25 + 5 * math.sin(t * 3 + i)
            x1 = 60 + math.cos(angle1) * dist
            y1 = 50 + math.sin(angle1) * dist
            x2 = 60 + math.cos(angle2) * dist
            y2 = 50 + math.sin(angle2) * dist
            # 纠缠连线
            pygame.draw.line(entangle_surface, (220, 150, 255, 180), (int(x1), int(y1)), (int(x2), int(y2)), 2)
            # 纠缠粒子对
            pygame.draw.circle(entangle_surface, (180, 100, 255, 220), (int(x1), int(y1)), 4)
            pygame.draw.circle(entangle_surface, (180, 100, 255, 220), (int(x2), int(y2)), 4)
        s.blit(entangle_surface, (0, 0))
        
        return s
    
    elif model_style == "fractal":
        # 分形几何·无限循环 - 分形结构、几何递归、数学美学、完美对称
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：Sierpinski三角形（分形）
        def draw_sierpinski(surface, p1, p2, p3, depth, color_offset):
            if depth == 0:
                alpha = int(180 + 75 * math.sin(t * 2 + color_offset))
                pygame.draw.polygon(surface, (255, 0, 255, alpha), [p1, p2, p3], 2)
                return
            # 中点
            mid1 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
            mid2 = ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2)
            mid3 = ((p3[0] + p1[0]) / 2, (p3[1] + p1[1]) / 2)
            # 递归绘制
            draw_sierpinski(surface, p1, mid1, mid3, depth - 1, color_offset + 0.5)
            draw_sierpinski(surface, mid1, p2, mid2, depth - 1, color_offset + 1)
            draw_sierpinski(surface, mid3, mid2, p3, depth - 1, color_offset + 1.5)
        
        # 绘制分形
        fractal_depth = 3 + int(math.sin(t) * 0.5 + 0.5)
        draw_sierpinski(s, (60, 20), (90, 70), (30, 70), fractal_depth, t)
        
        # 旋转的分形粒子
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            particle_angle = t * 3 + i * math.pi / 6
            particle_dist = 35 + 8 * math.sin(t * 2 + i)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            # 小三角粒子
            size = 4
            tri_points = [
                (particle_x, particle_y - size),
                (particle_x + size, particle_y + size),
                (particle_x - size, particle_y + size)
            ]
            pygame.draw.polygon(particle_surface, (0, 255, 255, 220), [(int(p[0]), int(p[1])) for p in tri_points])
        s.blit(particle_surface, (0, 0))
        
        # 完美对称线
        symmetry_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            sym_angle = i * math.pi / 4
            sym_x = 60 + math.cos(sym_angle) * 40
            sym_y = 50 + math.sin(sym_angle) * 40
            pygame.draw.line(symmetry_surface, (200, 100, 255, 150), (60, 50), (int(sym_x), int(sym_y)), 1)
        s.blit(symmetry_surface, (0, 0))
        
        return s
    
    elif model_style == "law":
        # 法则之书·规则编写 - 法则之书、规则条文、法则粒子、规则执行
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：法则之书（展开的书页）
        book_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 左页
        pygame.draw.rect(book_surface, (255, 215, 0, 230), (30, 30, 25, 40))
        pygame.draw.rect(book_surface, (255, 255, 255, 230), (30, 30, 25, 40), 2)
        # 右页
        pygame.draw.rect(book_surface, (255, 215, 0, 230), (65, 30, 25, 40))
        pygame.draw.rect(book_surface, (255, 255, 255, 230), (65, 30, 25, 40), 2)
        # 书脊
        pygame.draw.line(book_surface, (200, 180, 0, 250), (60, 30), (60, 70), 3)
        s.blit(book_surface, (0, 0))
        
        # 规则条文（文字模拟）
        text_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for page_offset in [0, 35]:
            for i in range(6):
                line_y = 35 + i * 5
                line_length = 18 + int(3 * math.sin(t * 2 + i))
                pygame.draw.line(text_surface, (100, 80, 0, 220), (32 + page_offset, line_y), 
                               (32 + page_offset + line_length, line_y), 1)
        s.blit(text_surface, (0, 0))
        
        # 法则粒子（符文环绕）
        rune_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            rune_angle = t * 1.5 + i * math.pi / 6
            rune_dist = 40 + 8 * math.sin(t * 2.5 + i)
            rune_x = 60 + math.cos(rune_angle) * rune_dist
            rune_y = 50 + math.sin(rune_angle) * rune_dist
            # 符文（方形）
            pygame.draw.rect(rune_surface, (255, 215, 0, 220), (int(rune_x - 2), int(rune_y - 2), 4, 4))
            pygame.draw.rect(rune_surface, (255, 255, 255, 220), (int(rune_x - 2), int(rune_y - 2), 4, 4), 1)
        s.blit(rune_surface, (0, 0))
        
        # 规则执行（律令光束）
        execute_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            if (int(t * 4) + i) % 3 == 0:
                exec_angle = i * math.pi / 3
                exec_x = 60 + math.cos(exec_angle) * 50
                exec_y = 50 + math.sin(exec_angle) * 50
                pygame.draw.line(execute_surface, (255, 255, 255, 220), (60, 50), (int(exec_x), int(exec_y)), 2)
        s.blit(execute_surface, (0, 0))
        
        # 法则光环
        for i in range(3):
            law_radius = 35 + i * 10 + int(6 * pulse)
            law_alpha = int(150 * (1 - i / 3))
            law_ring = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(law_ring, (255, 215, 0, law_alpha), (60, 50), law_radius, 2)
            s.blit(law_ring, (0, 0))
        
        return s
    
    elif model_style == "balance":
        # 平衡裁决·天平永恒 - 天平、公正秤杆、平衡粒子、秩序维持
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：天平结构
        # 支柱
        pygame.draw.line(s, (128, 128, 128), (60, 25), (60, 65), 4)
        pygame.draw.line(s, (200, 200, 200), (60, 25), (60, 65), 2)
        # 底座
        pygame.draw.rect(s, (128, 128, 128), (50, 65, 20, 5))
        pygame.draw.rect(s, (200, 200, 200), (50, 65, 20, 5), 1)
        
        # 秤杆（平衡摆动）
        tilt = math.sin(t * 1.5) * 0.2
        beam_left_x = 60 - 25 * math.cos(tilt)
        beam_left_y = 35 + 25 * math.sin(tilt)
        beam_right_x = 60 + 25 * math.cos(tilt)
        beam_right_y = 35 - 25 * math.sin(tilt)
        pygame.draw.line(s, (128, 128, 128), (int(beam_left_x), int(beam_left_y)), 
                        (int(beam_right_x), int(beam_right_y)), 4)
        pygame.draw.line(s, (200, 200, 200), (int(beam_left_x), int(beam_left_y)), 
                        (int(beam_right_x), int(beam_right_y)), 2)
        
        # 秤盘（左右）
        for side, (bx, by) in [(0, (beam_left_x, beam_left_y)), (1, (beam_right_x, beam_right_y))]:
            # 悬挂链
            chain_y = by + 10
            pygame.draw.line(s, (150, 150, 150), (int(bx), int(by)), (int(bx), int(chain_y)), 2)
            # 秤盘
            pygame.draw.circle(s, (128, 128, 128), (int(bx), int(chain_y + 5)), 8)
            pygame.draw.circle(s, (200, 200, 200), (int(bx), int(chain_y + 5)), 8, 1)
        
        # 平衡粒子（飘散）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            particle_angle = t * 2 + i * math.pi / 8
            particle_dist = 35 + 10 * math.sin(t * 2.5 + i)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (150, 150, 150, 220), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        # 秩序光环
        for i in range(4):
            order_radius = 30 + i * 10 + int(5 * pulse)
            order_alpha = int(150 * (1 - i / 4))
            order_ring = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(order_ring, (200, 200, 200, order_alpha), (60, 45), order_radius, 2)
            s.blit(order_ring, (0, 0))
        
        return s
    
    elif model_style == "judge":
        # 终极审判·公正天平 - 审判天平、公正符文、裁决之光、法则之力
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：黄金天平
        # 支柱（发光）
        pillar_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.line(pillar_surface, (255, 255, 200, 250), (60, 20), (60, 70), 5)
        pygame.draw.line(pillar_surface, (255, 255, 255, 220), (60, 20), (60, 70), 3)
        s.blit(pillar_surface, (0, 0))
        
        # 黄金底座
        pygame.draw.rect(s, (255, 215, 0), (48, 70, 24, 6))
        pygame.draw.rect(s, (255, 255, 200), (48, 70, 24, 6), 2)
        
        # 秤杆（绝对平衡）
        beam_y = 35
        pygame.draw.line(s, (255, 215, 0), (30, beam_y), (90, beam_y), 5)
        pygame.draw.line(s, (255, 255, 200), (30, beam_y), (90, beam_y), 3)
        
        # 秤盘（左右平衡）
        for pan_x in [30, 90]:
            # 悬挂链
            pygame.draw.line(s, (200, 180, 0), (pan_x, beam_y), (pan_x, beam_y + 15), 2)
            # 秤盘（发光）
            pan_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(pan_surface, (255, 215, 0, 250), (pan_x, beam_y + 20), 10)
            pygame.draw.circle(pan_surface, (255, 255, 200, 220), (pan_x, beam_y + 20), int(10 * pulse))
            s.blit(pan_surface, (0, 0))
        
        # 公正符文（闪耀）
        rune_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            if (int(t * 5) + i) % 4 < 2:
                rune_angle = i * math.pi / 4
                rune_x = 60 + math.cos(rune_angle) * 45
                rune_y = 45 + math.sin(rune_angle) * 45
                # 符文（十字）
                pygame.draw.line(rune_surface, (255, 255, 200, 250), (int(rune_x - 3), int(rune_y)), 
                               (int(rune_x + 3), int(rune_y)), 2)
                pygame.draw.line(rune_surface, (255, 255, 200, 250), (int(rune_x), int(rune_y - 3)), 
                               (int(rune_x), int(rune_y + 3)), 2)
        s.blit(rune_surface, (0, 0))
        
        # 裁决之光（从天而降）
        judgment_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            light_y = 10 + ((t * 80 + i * 15) % 70)
            light_alpha = int(220 * (1 - ((t * 80 + i * 15) % 70) / 70))
            pygame.draw.line(judgment_surface, (255, 255, 255, light_alpha), (60, int(light_y)), (60, int(light_y + 10)), 4)
        s.blit(judgment_surface, (0, 0))
        
        # 法则光环
        for i in range(4):
            law_radius = 40 + i * 12 + int(8 * pulse)
            law_alpha = int(180 * (1 - i / 4))
            law_ring = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(law_ring, (255, 255, 200, law_alpha), (60, 45), law_radius, 3)
            s.blit(law_ring, (0, 0))
        
        return s
    
    elif model_style == "matrix":
        # 矩阵主宰·代码执行 - 矩阵世界、代码洪流、程序执行、数字主宰
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：矩阵核心
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_surface, (0, 255, 100, 250), (60, 50), 12)
        pygame.draw.circle(core_surface, (100, 255, 150, 230), (60, 50), int(12 * pulse))
        s.blit(core_surface, (0, 0))
        
        # 代码流（垂直下落）
        code_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            code_x = 20 + i * 10
            code_length = 30 + int(20 * math.sin(t * 2 + i))
            code_y = ((t * 60 + i * 12) % 130) - 10
            # 代码串（渐变）
            for j in range(int(code_length / 3)):
                char_y = code_y + j * 3
                char_alpha = int(220 * (1 - j * 3 / code_length))
                if 0 <= char_y <= 120:
                    pygame.draw.rect(code_surface, (0, 255, 100, char_alpha), (code_x, int(char_y), 2, 2))
        s.blit(code_surface, (0, 0))
        
        # 矩阵网格
        grid_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(0, 120, 15):
            grid_alpha = int(100 + 80 * math.sin(t * 2 + i * 0.1))
            pygame.draw.line(grid_surface, (0, 255, 100, grid_alpha), (0, i), (120, i), 1)
            pygame.draw.line(grid_surface, (0, 255, 100, grid_alpha), (i, 0), (i, 120), 1)
        s.blit(grid_surface, (0, 0))
        
        # 程序执行节点
        node_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            node_angle = t * 2 + i * math.pi / 4
            node_dist = 28 + 8 * math.sin(t * 3 + i)
            node_x = 60 + math.cos(node_angle) * node_dist
            node_y = 50 + math.sin(node_angle) * node_dist
            pygame.draw.circle(node_surface, (100, 255, 150, 220), (int(node_x), int(node_y)), 4)
            # 连接到核心
            pygame.draw.line(node_surface, (50, 255, 120, 180), (60, 50), (int(node_x), int(node_y)), 2)
        s.blit(node_surface, (0, 0))
        
        # 数据流粒子
        data_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            data_angle = t * 3 + i * math.pi / 10
            data_dist = 20 + ((t * 40 + i * 5) % 30)
            data_x = 60 + math.cos(data_angle) * data_dist
            data_y = 50 + math.sin(data_angle) * data_dist
            pygame.draw.circle(data_surface, (100, 255, 150, 220), (int(data_x), int(data_y)), 2)
        s.blit(data_surface, (0, 0))
        
        return s
    
    elif model_style == "truth":
        # 真理之眼·洞察一切 - 真理之眼、洞察本质、真理光芒、一切明晰
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.2 + 1
        
        # 主体：全视之眼
        # 眼睛轮廓（杏仁形）
        eye_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        eye_points = [
            (40, 50),
            (50, 40),
            (70, 40),
            (80, 50),
            (70, 60),
            (50, 60)
        ]
        pygame.draw.polygon(eye_surface, (255, 255, 255, 240), eye_points)
        pygame.draw.polygon(eye_surface, (255, 255, 220, 250), eye_points, 2)
        s.blit(eye_surface, (0, 0))
        
        # 眼球（发光）
        eyeball_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(eyeball_surface, (255, 255, 255, 250), (60, 50), 12)
        pygame.draw.circle(eyeball_surface, (255, 255, 220, 230), (60, 50), int(12 * pulse))
        s.blit(eyeball_surface, (0, 0))
        
        # 瞳孔（洞察）
        pupil_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(pupil_surface, (100, 100, 150, 250), (60, 50), 6)
        pygame.draw.circle(pupil_surface, (255, 255, 255, 250), (62, 48), 2)  # 高光
        s.blit(pupil_surface, (0, 0))
        
        # 真理光芒（放射状）
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            ray_angle = t * 1.5 + i * math.pi / 8
            ray_length = 35 + 15 * math.sin(t * 3 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 50 + math.sin(ray_angle) * ray_length
            ray_alpha = int(200 + 55 * math.sin(t * 4 + i))
            pygame.draw.line(ray_surface, (255, 255, 240, ray_alpha), (60, 50), (int(ray_x), int(ray_y)), 3)
        s.blit(ray_surface, (0, 0))
        
        # 洞察波纹（扫描）
        scan_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(4):
            scan_radius = (t * 60 + i * 20) % 80
            scan_alpha = int(200 * (1 - scan_radius / 80))
            pygame.draw.circle(scan_surface, (255, 255, 220, scan_alpha), (60, 50), int(scan_radius), 2)
        s.blit(scan_surface, (0, 0))
        
        # 真理符文（环绕）
        rune_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            rune_angle = t + i * math.pi / 6
            rune_dist = 40 + 8 * math.sin(t * 2.5 + i)
            rune_x = 60 + math.cos(rune_angle) * rune_dist
            rune_y = 50 + math.sin(rune_angle) * rune_dist
            # 符文（圆形）
            pygame.draw.circle(rune_surface, (255, 255, 220, 220), (int(rune_x), int(rune_y)), 3)
            pygame.draw.circle(rune_surface, (255, 255, 255, 220), (int(rune_x), int(rune_y)), 2)
        s.blit(rune_surface, (0, 0))
        
        # 一切明晰光环
        for i in range(3):
            clarity_radius = 45 + i * 12 + int(10 * pulse)
            clarity_alpha = int(180 * (1 - i / 3))
            clarity_ring = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(clarity_ring, (255, 255, 255, clarity_alpha), (60, 50), clarity_radius, 2)
            s.blit(clarity_ring, (0, 0))
        
        return s

    # --- Solar MK5/MK6 ---
    elif model_style == "solar_eclipse":
        # 日冕物质：喷射 + 暗核
        pygame.draw.circle(s, (255, 100, 0), (60, 60), 30)
        pygame.draw.circle(s, (50, 0, 0), (60, 60), 20) # 暗核
        # 喷射物
        for i in range(8):
            angle = i * math.pi / 4 + t
            ex = 60 + math.cos(angle) * (40 + 10 * math.sin(t * 5))
            ey = 60 + math.sin(angle) * (40 + 10 * math.sin(t * 5))
            pygame.draw.circle(s, (255, 200, 0), (int(ex), int(ey)), 5)
        return s

    elif model_style == "solar_flare_max":
        # 耀斑爆发：极亮 + 辐射刺
        # 辐射刺
        for i in range(12):
            angle = i * math.pi / 6 + t * 2
            ex = 60 + math.cos(angle) * 50
            ey = 60 + math.sin(angle) * 50
            pygame.draw.line(s, (255, 255, 100), (60, 60), (ex, ey), 2)
        pygame.draw.circle(s, (255, 255, 200), (60, 60), 30)
        pygame.draw.circle(s, (255, 255, 255), (60, 60), 20 + int(5 * pulse))
        return s
    
    # ========== Eclipse专属涂装 ==========
    elif model_style == "moon":
        # 血月当空·月蚀之力 - 血月高悬、月蚀能量、血色月光、月神之力
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：血月（红色月亮）
        moon_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(moon_surface, (150, 0, 0, 240), (60, 50), 18)
        pygame.draw.circle(moon_surface, (255, 50, 50, 220), (60, 50), int(18 * pulse))
        s.blit(moon_surface, (0, 0))
        
        # 月蚀阴影（月面暗纹）
        shadow_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            shadow_x = 55 + i * 3
            shadow_y = 45 + int(8 * math.sin(t + i))
            pygame.draw.circle(shadow_surface, (100, 0, 0, 180), (shadow_x, shadow_y), 4)
        s.blit(shadow_surface, (0, 0))
        
        # 血色月光（放射状光芒）
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            ray_angle = t * 1.5 + i * math.pi / 6
            ray_length = 25 + 12 * math.sin(t * 3 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 50 + math.sin(ray_angle) * ray_length
            pygame.draw.line(ray_surface, (255, 50, 50, 200), (60, 50), (int(ray_x), int(ray_y)), 2)
        s.blit(ray_surface, (0, 0))
        
        # 月神之力（环绕粒子）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 2 + i * math.pi / 10
            particle_dist = 25 + 10 * math.sin(t * 2.5 + i)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (180, 20, 20, 220), (int(particle_x), int(particle_y)), 3)
        s.blit(particle_surface, (0, 0))
        
        # 月蚀能量波
        for i in range(3):
            wave_radius = (t * 50 + i * 25) % 75
            wave_alpha = int(200 * (1 - wave_radius / 75))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (255, 50, 50, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surface, (0, 0))
        
        return s
    
    elif model_style == "void":
        # 虚空日食·黑洞边缘 - 虚空黑洞、引力透镜、事件视界、光线扭曲
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：黑洞核心（纯黑）
        blackhole_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(blackhole_surface, (0, 0, 0, 255), (60, 50), 14)
        s.blit(blackhole_surface, (0, 0))
        
        # 事件视界（紫色边缘）
        horizon_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            horizon_radius = 15 + i * 3 + int(2 * pulse)
            horizon_alpha = int(220 * (1 - i / 3))
            pygame.draw.circle(horizon_surface, (100, 0, 150, horizon_alpha), (60, 50), horizon_radius, 2)
        s.blit(horizon_surface, (0, 0))
        
        # 吸积盘（环状物质）
        disk_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            disk_angle = t * 3 + i * math.pi / 4
            # 椭圆轨道
            orbit_dist = 22 + 8 * math.sin(t * 2 + i)
            disk_x = 60 + math.cos(disk_angle) * orbit_dist
            disk_y = 50 + math.sin(disk_angle) * orbit_dist * 0.4  # 压扁效果
            pygame.draw.circle(disk_surface, (50, 0, 100, 220), (int(disk_x), int(disk_y)), 3)
        s.blit(disk_surface, (0, 0))
        
        # 引力透镜效应（扭曲光线）
        lens_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            lens_angle = i * math.pi / 6
            lens_dist = 28
            lens_x = 60 + math.cos(lens_angle) * lens_dist
            lens_y = 50 + math.sin(lens_angle) * lens_dist
            # 弯曲光线
            bend_offset = 8 * math.sin(t * 2 + i)
            bend_x = lens_x + math.cos(lens_angle + math.pi / 2) * bend_offset
            bend_y = lens_y + math.sin(lens_angle + math.pi / 2) * bend_offset
            pygame.draw.line(lens_surface, (100, 50, 150, 180), (int(lens_x), int(lens_y)), 
                           (int(bend_x), int(bend_y)), 2)
        s.blit(lens_surface, (0, 0))
        
        # 虚空粒子吸入
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 4 + i * math.pi / 10
            particle_progress = ((t * 50 + i * 5) % 100) / 100
            particle_dist = 45 - particle_progress * 30
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            particle_alpha = int(220 * (1 - particle_progress))
            pygame.draw.circle(particle_surface, (100, 0, 150, particle_alpha), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        return s
    
    elif model_style == "shadow":
        # 日食幽灵·暗影吞噬 - 日食阴影、黑暗吞食、暗影扩散、光暗界限
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：幽灵形态
        ghost_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        ghost_points = [(60, 25), (70, 40), (75, 60), (70, 75), (50, 75), (45, 60), (50, 40)]
        pygame.draw.polygon(ghost_surface, (30, 30, 50, 230), ghost_points)
        pygame.draw.polygon(ghost_surface, (80, 80, 120, 250), ghost_points, 2)
        s.blit(ghost_surface, (0, 0))
        
        # 暗影扩散（波动阴影）
        shadow_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            shadow_radius = 20 + i * 8 + int(6 * pulse)
            shadow_alpha = int(150 * (1 - i / 5))
            pygame.draw.circle(shadow_surface, (50, 50, 80, shadow_alpha), (60, 50), shadow_radius, 3)
        s.blit(shadow_surface, (0, 0))
        
        # 黑暗吞食（触手）
        tentacle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            tentacle_angle = t + i * math.pi / 4
            tentacle_segments = []
            for j in range(6):
                seg_dist = 15 + j * 4
                seg_angle = tentacle_angle + math.sin(t * 3 + i + j * 0.5) * 0.3
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist
                tentacle_segments.append((seg_x, seg_y))
            # 绘制触手
            for j in range(len(tentacle_segments) - 1):
                pygame.draw.line(tentacle_surface, (30, 30, 50, 200), 
                               (int(tentacle_segments[j][0]), int(tentacle_segments[j][1])),
                               (int(tentacle_segments[j+1][0]), int(tentacle_segments[j+1][1])), 3)
        s.blit(tentacle_surface, (0, 0))
        
        # 光暗界限（边缘闪烁）
        border_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            if (int(t * 5) + i) % 3 < 2:
                border_angle = i * math.pi / 6
                border_x = 60 + math.cos(border_angle) * 35
                border_y = 50 + math.sin(border_angle) * 35
                pygame.draw.circle(border_surface, (80, 80, 120, 220), (int(border_x), int(border_y)), 3)
        s.blit(border_surface, (0, 0))
        
        return s
    
    elif model_style == "abyss":
        # 深渊凝视·虚无吞噬 - 深渊裂缝、虚无力量、凝视毁灭、深渊吞噬
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：深渊之眼
        abyss_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(abyss_surface, (100, 0, 150, 250), (60, 50), 16)
        pygame.draw.circle(abyss_surface, (180, 50, 200, 230), (60, 50), int(16 * pulse))
        s.blit(abyss_surface, (0, 0))
        
        # 深渊瞳孔（凝视）
        pupil_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(pupil_surface, (50, 0, 100, 255), (60, 50), 8)
        # 恐怖高光
        pygame.draw.circle(pupil_surface, (150, 0, 200, 255), (62, 48), 2)
        s.blit(pupil_surface, (0, 0))
        
        # 深渊裂缝（放射状）
        crack_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            crack_angle = t + i * math.pi / 6
            crack_length = 20 + 15 * math.sin(t * 2 + i)
            crack_x = 60 + math.cos(crack_angle) * crack_length
            crack_y = 50 + math.sin(crack_angle) * crack_length
            # 裂缝（锯齿状）
            pygame.draw.line(crack_surface, (120, 20, 180, 220), (60, 50), (int(crack_x), int(crack_y)), 3)
            pygame.draw.line(crack_surface, (180, 50, 200, 220), (60, 50), (int(crack_x), int(crack_y)), 1)
        s.blit(crack_surface, (0, 0))
        
        # 虚无触手（从深渊伸出）
        tentacle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            tentacle_base_angle = i * math.pi / 4
            tentacle_segments = []
            for j in range(8):
                seg_angle = tentacle_base_angle + math.sin(t * 3 + i + j * 0.3) * 0.4
                seg_dist = 18 + j * 4
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist
                tentacle_segments.append((seg_x, seg_y))
            # 绘制触手
            for j in range(len(tentacle_segments) - 1):
                width = 5 - j // 2
                pygame.draw.line(tentacle_surface, (100, 0, 150, 220), 
                               (int(tentacle_segments[j][0]), int(tentacle_segments[j][1])),
                               (int(tentacle_segments[j+1][0]), int(tentacle_segments[j+1][1])), width)
        s.blit(tentacle_surface, (0, 0))
        
        # 毁灭粒子
        destroy_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(25):
            destroy_angle = t * 3 + i * math.pi / 12.5
            destroy_dist = 25 + 20 * (i / 25)
            destroy_x = 60 + math.cos(destroy_angle) * destroy_dist
            destroy_y = 50 + math.sin(destroy_angle) * destroy_dist
            destroy_alpha = int(220 * (1 - (i / 25)))
            pygame.draw.circle(destroy_surface, (120, 20, 180, destroy_alpha), (int(destroy_x), int(destroy_y)), 2)
        s.blit(destroy_surface, (0, 0))
        
        return s
    
    elif model_style == "night":
        # 永夜降临·黑暗时代 - 永恒黑夜、黑暗领域、星光消逝、永恒夜幕
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.1 + 1
        
        # 主体：夜幕形态
        night_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(night_surface, (20, 20, 40, 240), (60, 50), 18)
        pygame.draw.circle(night_surface, (80, 80, 120, 220), (60, 50), int(18 * pulse))
        s.blit(night_surface, (0, 0))
        
        # 黑暗领域扩张（多层黑暗）
        for i in range(5):
            darkness_radius = 22 + i * 8 + int(5 * pulse)
            darkness_alpha = int(180 * (1 - i / 5))
            darkness_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(darkness_surface, (40, 40, 70, darkness_alpha), (60, 50), darkness_radius, 3)
            s.blit(darkness_surface, (0, 0))
        
        # 消逝的星光（渐暗的星星）
        star_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            star_angle = t * 0.5 + i * math.pi / 7.5
            star_dist = 30 + 10 * (i / 15)
            star_x = 60 + math.cos(star_angle) * star_dist
            star_y = 50 + math.sin(star_angle) * star_dist
            # 渐暗效果
            star_brightness = int(200 * (1 - (i / 15)))
            if star_brightness > 50:
                pygame.draw.circle(star_surface, (star_brightness, star_brightness, star_brightness + 50, 220), 
                                 (int(star_x), int(star_y)), 2)
        s.blit(star_surface, (0, 0))
        
        # 永恒夜幕（波动阴影）
        veil_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            veil_angle = t * 2 + i * math.pi / 10
            veil_dist = 25 + 15 * math.sin(t * 2 + i)
            veil_x = 60 + math.cos(veil_angle) * veil_dist
            veil_y = 50 + math.sin(veil_angle) * veil_dist
            pygame.draw.circle(veil_surface, (40, 40, 70, 180), (int(veil_x), int(veil_y)), 4)
        s.blit(veil_surface, (0, 0))
        
        # 夜之精华（暗粒子）
        essence_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            essence_angle = t * 1.5 + i * math.pi / 6
            essence_dist = 35 + 8 * math.sin(t * 2.5 + i)
            essence_x = 60 + math.cos(essence_angle) * essence_dist
            essence_y = 50 + math.sin(essence_angle) * essence_dist
            pygame.draw.circle(essence_surface, (80, 80, 120, 220), (int(essence_x), int(essence_y)), 3)
        s.blit(essence_surface, (0, 0))
        
        return s
    
    elif model_style == "dual":
        # 日月双食·阴阳交替 - 日月同食、阴阳力量、双重天象、天地失色
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：日月双核
        # 太阳（左）
        sun_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        sun_x = 45
        pygame.draw.circle(sun_surface, (220, 100, 255, 230), (sun_x, 50), 12)
        pygame.draw.circle(sun_surface, (255, 150, 255, 210), (sun_x, 50), int(12 * pulse))
        s.blit(sun_surface, (0, 0))
        
        # 月亮（右）
        moon_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        moon_x = 75
        pygame.draw.circle(moon_surface, (150, 50, 180, 230), (moon_x, 50), 12)
        pygame.draw.circle(moon_surface, (200, 100, 255, 210), (moon_x, 50), int(12 * pulse))
        s.blit(moon_surface, (0, 0))
        
        # 阴阳交替线（中心连接）
        pygame.draw.line(s, (180, 70, 220), (sun_x, 50), (moon_x, 50), 3)
        
        # 阴阳符号（太极）
        taiji_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 白半
        pygame.draw.arc(taiji_surface, (255, 200, 255, 220), (52, 42, 16, 16), 0, math.pi, 4)
        # 黑半
        pygame.draw.arc(taiji_surface, (100, 0, 150, 220), (52, 42, 16, 16), math.pi, 2 * math.pi, 4)
        s.blit(taiji_surface, (0, 0))
        
        # 日月光环（交错）
        for i in range(6):
            ring_angle = t * 2 + i * math.pi / 3
            ring_dist = 30 + 8 * math.sin(t * 2.5 + i)
            # 日光粒子
            sun_ring_x = sun_x + math.cos(ring_angle) * ring_dist
            sun_ring_y = 50 + math.sin(ring_angle) * ring_dist
            pygame.draw.circle(s, (220, 100, 255, 220), (int(sun_ring_x), int(sun_ring_y)), 3)
            # 月光粒子
            moon_ring_x = moon_x + math.cos(ring_angle + math.pi) * ring_dist
            moon_ring_y = 50 + math.sin(ring_angle + math.pi) * ring_dist
            pygame.draw.circle(s, (150, 50, 180, 220), (int(moon_ring_x), int(moon_ring_y)), 3)
        
        # 双重天象能量波
        for i in range(3):
            wave_radius = (t * 50 + i * 30) % 90
            wave_alpha = int(200 * (1 - wave_radius / 90))
            wave_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 从两个核心扩散
            pygame.draw.circle(wave_surface, (180, 70, 220, wave_alpha), (sun_x, 50), int(wave_radius), 2)
            pygame.draw.circle(wave_surface, (180, 70, 220, wave_alpha), (moon_x, 50), int(wave_radius), 2)
            s.blit(wave_surface, (0, 0))
        
        return s
    
    elif model_style == "cosmos":
        # 宇宙日食·星际黑暗 - 宇宙尺度日食、星际黑暗降临、星光遮蔽、宇宙寂灭
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.8) * 0.25 + 1
        
        # 主体：超大质量黑洞核心
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 事件视界（最黑的部分）
        pygame.draw.circle(core_surface, (10, 0, 20, 255), (60, 50), 18)
        # 吸积盘内环（强引力扭曲）
        for i in range(5):
            ring_r = 18 + i * 3
            ring_alpha = int(250 - i * 40)
            pygame.draw.circle(core_surface, (80, 0, 120, ring_alpha), (60, 50), ring_r, 2)
        s.blit(core_surface, (0, 0))
        
        # 吸积盘（螺旋结构）
        accretion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for arm in range(3):
            arm_offset = arm * math.pi * 2 / 3
            for i in range(40):
                spiral_progress = i / 40
                spiral_angle = t * 1.5 + spiral_progress * math.pi * 4 + arm_offset
                spiral_dist = 25 + spiral_progress * 30
                spiral_x = 60 + math.cos(spiral_angle) * spiral_dist
                spiral_y = 50 + math.sin(spiral_angle) * spiral_dist
                # 颜色从紫色到深红（高温到低温）
                color_r = int(150 + 105 * spiral_progress)
                color_g = int(100 * (1 - spiral_progress))
                color_b = int(200 * (1 - spiral_progress))
                spiral_alpha = int(240 * (1 - spiral_progress * 0.7))
                if 0 <= spiral_x <= 120 and 0 <= spiral_y <= 120:
                    pygame.draw.circle(accretion_surface, (color_r, color_g, color_b, spiral_alpha), 
                                     (int(spiral_x), int(spiral_y)), 3)
        s.blit(accretion_surface, (0, 0))
        
        # 被遮蔽的星光（星际黑暗）
        stars_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(35):
            star_angle = (t * 0.3 + i * 0.618) * math.pi * 2  # 黄金角
            star_dist = 40 + (i % 3) * 8
            star_x = 60 + math.cos(star_angle) * star_dist
            star_y = 50 + math.sin(star_angle) * star_dist
            # 星光逐渐被遮蔽（渐暗效果）
            fade_factor = (math.sin(t * 2 + i) + 1) / 2
            star_brightness = int(180 * fade_factor)
            if star_brightness > 30:
                star_color = (star_brightness, star_brightness - 30, star_brightness + 50)
                if 0 <= star_x <= 120 and 0 <= star_y <= 120:
                    pygame.draw.circle(stars_surface, (*star_color, 220), 
                                     (int(star_x), int(star_y)), 2)
                    # 十字星芒
                    if star_brightness > 120:
                        for angle in [0, math.pi/2]:
                            ray_len = 4
                            rx1 = star_x + math.cos(angle) * ray_len
                            ry1 = star_y + math.sin(angle) * ray_len
                            rx2 = star_x - math.cos(angle) * ray_len
                            ry2 = star_y - math.sin(angle) * ray_len
                            pygame.draw.line(stars_surface, (*star_color, 180), 
                                           (int(rx1), int(ry1)), (int(rx2), int(ry2)), 1)
        s.blit(stars_surface, (0, 0))
        
        # 引力透镜效果（空间扭曲）
        lensing_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            lens_radius = 25 + i * 6 + int(5 * pulse)
            lens_alpha = int(120 * (1 - i / 6))
            # 绘制扭曲的光环
            for angle_deg in range(0, 360, 30):
                angle = math.radians(angle_deg)
                distortion = 2 * math.sin(t * 2 + angle * 3)
                lens_r = lens_radius + distortion
                lx = 60 + math.cos(angle) * lens_r
                ly = 50 + math.sin(angle) * lens_r
                if 0 <= lx <= 120 and 0 <= ly <= 120:
                    pygame.draw.circle(lensing_surface, (150, 100, 200, lens_alpha), 
                                     (int(lx), int(ly)), 2)
        s.blit(lensing_surface, (0, 0))
        
        # 霍金辐射（黑洞边缘微弱辐射）
        radiation_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            rad_angle = t * 4 + i * math.pi / 10
            rad_dist = 20 + 3 * math.sin(t * 3 + i)
            rad_x = 60 + math.cos(rad_angle) * rad_dist
            rad_y = 50 + math.sin(rad_angle) * rad_dist
            pygame.draw.circle(radiation_surface, (200, 150, 255, 200), (int(rad_x), int(rad_y)), 1)
        s.blit(radiation_surface, (0, 0))
        
        # 宇宙寂灭波（暗能量扩散）
        extinction_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            ext_radius = (t * 35 + i * 20) % 85
            ext_alpha = int(180 * (1 - ext_radius / 85))
            pygame.draw.circle(extinction_surface, (100, 50, 150, ext_alpha), (60, 50), int(ext_radius), 2)
        s.blit(extinction_surface, (0, 0))
        
        # 暗物质云（背景）
        dark_matter_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(30):
            dm_angle = t * 0.8 + i * 0.7
            dm_dist = 15 + 35 * (i / 30)
            dm_x = 60 + math.cos(dm_angle) * dm_dist
            dm_y = 50 + math.sin(dm_angle) * dm_dist
            dm_size = 1 + int(2 * math.sin(t * 2 + i))
            if 0 <= dm_x <= 120 and 0 <= dm_y <= 120:
                pygame.draw.circle(dark_matter_surface, (60, 0, 100, 150), 
                                 (int(dm_x), int(dm_y)), dm_size)
        s.blit(dark_matter_surface, (0, 0))
        
        return s

    # --- Arbiter MK5/MK6 ---
    elif model_style == "arbiter_law":
        # 绝对律法：符文
        pts = [(60, 10), (110, 60), (60, 110), (10, 60)]
        pygame.draw.polygon(s, (200, 150, 0), pts)
        # 符文模拟
        pygame.draw.line(s, (255, 255, 200), (60, 20), (60, 100), 2)
        pygame.draw.line(s, (255, 255, 200), (20, 60), (100, 60), 2)
        pygame.draw.circle(s, (255, 255, 200), (60, 60), 10, 2)
        return s

    elif model_style == "arbiter_balance":
        # 均衡之道：黑白
        pts = [(60, 10), (110, 60), (60, 110), (10, 60)]
        # 左黑
        pygame.draw.polygon(s, (20, 20, 20), [(60, 10), (10, 60), (60, 110)])
        # 右白
        pygame.draw.polygon(s, (220, 220, 220), [(60, 10), (110, 60), (60, 110)])
        return s
    
    # ========== Prism专属涂装 ==========
    elif model_style == "diamond":
        # 钻石星辰·完美折射 - 钻石切割面、完美折射、星辰闪耀、光之宝石
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：钻石形状（多面体）
        diamond_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 上半部（锥形）
        diamond_top = [(60, 35), (70, 50), (60, 55), (50, 50)]
        pygame.draw.polygon(diamond_surface, (220, 220, 255, 250), diamond_top)
        pygame.draw.polygon(diamond_surface, (255, 255, 255, 230), diamond_top, 2)
        # 下半部（锥形）
        diamond_bottom = [(60, 55), (70, 50), (75, 65), (60, 70), (45, 65), (50, 50)]
        pygame.draw.polygon(diamond_surface, (240, 240, 255, 250), diamond_bottom)
        pygame.draw.polygon(diamond_surface, (255, 255, 255, 230), diamond_bottom, 2)
        s.blit(diamond_surface, (0, 0))
        
        # 切割面反射（多条光线）
        facet_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            facet_angle = t * 2 + i * math.pi / 6
            facet_length = 15 + 10 * math.sin(t * 3 + i)
            facet_x = 60 + math.cos(facet_angle) * facet_length
            facet_y = 52 + math.sin(facet_angle) * facet_length
            pygame.draw.line(facet_surface, (255, 255, 255, 220), (60, 52), (int(facet_x), int(facet_y)), 2)
        s.blit(facet_surface, (0, 0))
        
        # 星辰闪耀（闪光点）
        sparkle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            if (int(t * 10) + i) % 5 < 3:
                sparkle_angle = i * math.pi / 7.5
                sparkle_dist = 25 + 15 * (i % 3) / 2
                sparkle_x = 60 + math.cos(sparkle_angle) * sparkle_dist
                sparkle_y = 52 + math.sin(sparkle_angle) * sparkle_dist
                pygame.draw.circle(sparkle_surface, (255, 255, 255, 240), (int(sparkle_x), int(sparkle_y)), 3)
                # 十字闪光
                pygame.draw.line(sparkle_surface, (240, 240, 255, 200), 
                               (int(sparkle_x) - 4, int(sparkle_y)), 
                               (int(sparkle_x) + 4, int(sparkle_y)), 1)
                pygame.draw.line(sparkle_surface, (240, 240, 255, 200), 
                               (int(sparkle_x), int(sparkle_y) - 4), 
                               (int(sparkle_x), int(sparkle_y) + 4), 1)
        s.blit(sparkle_surface, (0, 0))
        
        # 完美折射光环
        refract_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            refract_radius = 20 + i * 10 + int(5 * pulse)
            refract_alpha = int(200 * (1 - i / 3))
            pygame.draw.circle(refract_surface, (220, 220, 255, refract_alpha), (60, 52), refract_radius, 2)
        s.blit(refract_surface, (0, 0))
        
        return s
    
    elif model_style == "refraction":
        # 多重折射·光线迷宫 - 光线折射、光路复杂、眩目迷离、光学迷宫
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.15 + 1
        
        # 主体：多棱镜结构
        prism_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 中心三角形
        pygame.draw.polygon(prism_surface, (200, 255, 255, 240), [(60, 40), (70, 60), (50, 60)])
        pygame.draw.polygon(prism_surface, (255, 200, 255, 240), [(60, 40), (75, 55), (70, 60)])
        pygame.draw.polygon(prism_surface, (220, 230, 255, 240), [(60, 40), (45, 55), (50, 60)])
        s.blit(prism_surface, (0, 0))
        
        # 折射光路（复杂路径）
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            # 入射光
            start_angle = t + i * math.pi / 4
            start_x = 60 + math.cos(start_angle) * 40
            start_y = 50 + math.sin(start_angle) * 40
            
            # 折射点
            refract_x = 60 + math.cos(start_angle) * 20
            refract_y = 50 + math.sin(start_angle) * 20
            
            # 出射光（改变角度）
            exit_angle = start_angle + math.pi / 3 + math.sin(t * 2 + i) * 0.5
            exit_x = 60 + math.cos(exit_angle) * 35
            exit_y = 50 + math.sin(exit_angle) * 35
            
            # 绘制光路
            color_shift = int(50 * math.sin(t + i))
            pygame.draw.line(ray_surface, (200 + color_shift, 255, 255, 200), 
                           (int(start_x), int(start_y)), (int(refract_x), int(refract_y)), 2)
            pygame.draw.line(ray_surface, (255, 200 + color_shift, 255, 200), 
                           (int(refract_x), int(refract_y)), (int(exit_x), int(exit_y)), 2)
        s.blit(ray_surface, (0, 0))
        
        # 光学粒子（在光路上）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            particle_angle = t * 3 + i * math.pi / 10
            particle_dist = 15 + 25 * (i / 20)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            pygame.draw.circle(particle_surface, (220, 230, 255, 220), (int(particle_x), int(particle_y)), 2)
        s.blit(particle_surface, (0, 0))
        
        return s
    
    elif model_style == "laser":
        # 激光矩阵·光束网络 - 激光矩阵、光束网络、高能光束、光之武器
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主体：激光发射器核心
        core_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(core_surface, (255, 0, 100, 250), (60, 50), 12)
        pygame.draw.circle(core_surface, (255, 100, 150, 230), (60, 50), int(12 * pulse))
        s.blit(core_surface, (0, 0))
        
        # 激光矩阵节点
        node_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        nodes = []
        for i in range(8):
            node_angle = t + i * math.pi / 4
            node_dist = 30
            node_x = 60 + math.cos(node_angle) * node_dist
            node_y = 50 + math.sin(node_angle) * node_dist
            nodes.append((node_x, node_y))
            pygame.draw.circle(node_surface, (255, 50, 120, 240), (int(node_x), int(node_y)), 6)
        s.blit(node_surface, (0, 0))
        
        # 光束网络（连接所有节点）
        beam_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(len(nodes)):
            # 连接到中心
            pygame.draw.line(beam_surface, (255, 100, 150, 200), (60, 50), 
                           (int(nodes[i][0]), int(nodes[i][1])), 2)
            # 连接相邻节点
            next_i = (i + 1) % len(nodes)
            pygame.draw.line(beam_surface, (255, 50, 120, 180), 
                           (int(nodes[i][0]), int(nodes[i][1])), 
                           (int(nodes[next_i][0]), int(nodes[next_i][1])), 2)
        s.blit(beam_surface, (0, 0))
        
        # 高能脉冲（沿光束移动）
        pulse_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            pulse_progress = ((t * 2 + i * 0.5) % 2) / 2
            pulse_x = 60 + (nodes[i][0] - 60) * pulse_progress
            pulse_y = 50 + (nodes[i][1] - 50) * pulse_progress
            pygame.draw.circle(pulse_surface, (255, 150, 200, 240), (int(pulse_x), int(pulse_y)), 4)
        s.blit(pulse_surface, (0, 0))
        
        return s
    
    elif model_style == "glass":
        # 玻璃艺术·透明美学 - 玻璃材质、透明效果、光影交错、艺术结晶
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：玻璃立方体（透明感）
        glass_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 前面
        glass_front = [(50, 45), (70, 45), (70, 65), (50, 65)]
        pygame.draw.polygon(glass_surface, (100, 255, 220, 120), glass_front)
        pygame.draw.polygon(glass_surface, (150, 255, 255, 200), glass_front, 2)
        # 顶面
        glass_top = [(50, 45), (70, 45), (75, 40), (55, 40)]
        pygame.draw.polygon(glass_surface, (120, 255, 240, 140), glass_top)
        pygame.draw.polygon(glass_surface, (150, 255, 255, 200), glass_top, 2)
        # 侧面
        glass_side = [(70, 45), (75, 40), (75, 60), (70, 65)]
        pygame.draw.polygon(glass_surface, (80, 255, 200, 100), glass_side)
        pygame.draw.polygon(glass_surface, (150, 255, 255, 200), glass_side, 2)
        s.blit(glass_surface, (0, 0))
        
        # 光影效果（穿透玻璃）
        light_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            light_x = 52 + i * 3
            light_alpha = int(150 * math.sin(t * 2 + i))
            if light_alpha > 0:
                pygame.draw.line(light_surface, (150, 255, 255, light_alpha), 
                               (light_x, 40), (light_x, 70), 2)
        s.blit(light_surface, (0, 0))
        
        # 透明折射粒子
        refract_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            refract_angle = t + i * math.pi / 7.5
            refract_dist = 20 + 15 * math.sin(t * 2 + i)
            refract_x = 60 + math.cos(refract_angle) * refract_dist
            refract_y = 55 + math.sin(refract_angle) * refract_dist
            pygame.draw.circle(refract_surface, (120, 255, 240, 200), (int(refract_x), int(refract_y)), 3)
        s.blit(refract_surface, (0, 0))
        
        # 玻璃光泽（高光）
        highlight_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(highlight_surface, (200, 255, 255, 180), (65, 50), 8)
        pygame.draw.circle(highlight_surface, (255, 255, 255, 220), (66, 49), 3)
        s.blit(highlight_surface, (0, 0))
        
        return s
    
    elif model_style == "crystal":
        # 晶体共振·光芒四射 - 晶体结构、光芒发射、光的放大、晶莹璀璨
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：晶体核心（六边形）
        crystal_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        crystal_points = []
        for i in range(6):
            crystal_angle = i * math.pi / 3
            crystal_x = 60 + math.cos(crystal_angle) * 15
            crystal_y = 50 + math.sin(crystal_angle) * 15
            crystal_points.append((crystal_x, crystal_y))
        pygame.draw.polygon(crystal_surface, (180, 220, 255, 250), crystal_points)
        pygame.draw.polygon(crystal_surface, (220, 255, 255, 230), crystal_points, 2)
        s.blit(crystal_surface, (0, 0))
        
        # 晶体格子（内部结构）
        lattice_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            lattice_angle = i * math.pi / 3
            lattice_x = 60 + math.cos(lattice_angle) * 10
            lattice_y = 50 + math.sin(lattice_angle) * 10
            pygame.draw.line(lattice_surface, (200, 240, 255, 220), (60, 50), 
                           (int(lattice_x), int(lattice_y)), 2)
        s.blit(lattice_surface, (0, 0))
        
        # 光芒四射（强烈放射）
        ray_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            ray_angle = t + i * math.pi / 6
            ray_length = 20 + 20 * math.sin(t * 3 + i)
            ray_x = 60 + math.cos(ray_angle) * ray_length
            ray_y = 50 + math.sin(ray_angle) * ray_length
            # 渐变光束
            for j in range(5):
                ray_alpha = int(220 * (1 - j / 5))
                ray_width = 4 - j
                pygame.draw.line(ray_surface, (200, 240, 255, ray_alpha), (60, 50), 
                               (int(ray_x), int(ray_y)), ray_width)
        s.blit(ray_surface, (0, 0))
        
        # 共振波动
        resonance_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            res_radius = (t * 60 + i * 30) % 90
            res_alpha = int(200 * (1 - res_radius / 90))
            pygame.draw.circle(resonance_surface, (180, 220, 255, res_alpha), (60, 50), int(res_radius), 2)
        s.blit(resonance_surface, (0, 0))
        
        return s
    
    elif model_style == "rainbow":
        # 棱镜分光·七彩虹光 - 光谱分离、七彩虹光、色彩粒子、光的盛宴
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：棱镜（三角形）
        prism_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        prism_points = [(60, 35), (75, 60), (45, 60)]
        pygame.draw.polygon(prism_surface, (255, 255, 255, 240), prism_points)
        pygame.draw.polygon(prism_surface, (255, 230, 255, 220), prism_points, 2)
        s.blit(prism_surface, (0, 0))
        
        # 七彩光谱（红橙黄绿青蓝紫）
        rainbow_colors = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0),
            (0, 255, 255), (0, 0, 255), (127, 0, 255)
        ]
        
        # 分光效果（从棱镜右侧射出）
        spectrum_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i, color in enumerate(rainbow_colors):
            spectrum_angle = -math.pi / 4 + i * 0.15
            spectrum_start_x = 75
            spectrum_start_y = 60
            spectrum_length = 25 + 10 * math.sin(t * 2 + i)
            spectrum_end_x = spectrum_start_x + math.cos(spectrum_angle) * spectrum_length
            spectrum_end_y = spectrum_start_y + math.sin(spectrum_angle) * spectrum_length
            pygame.draw.line(spectrum_surface, (*color, 220), 
                           (spectrum_start_x, spectrum_start_y), 
                           (int(spectrum_end_x), int(spectrum_end_y)), 3)
        s.blit(spectrum_surface, (0, 0))
        
        # 色彩粒子（彩虹粒子飞舞）
        particle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(21):
            particle_angle = t * 2 + i * math.pi / 10.5
            particle_dist = 20 + 20 * (i / 21)
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            color_index = i % len(rainbow_colors)
            pygame.draw.circle(particle_surface, (*rainbow_colors[color_index], 220), 
                             (int(particle_x), int(particle_y)), 3)
        s.blit(particle_surface, (0, 0))
        
        # 光的盛宴（环绕光环）
        halo_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(7):
            halo_radius = 18 + i * 4
            color_index = (int(t * 3) + i) % len(rainbow_colors)
            pygame.draw.circle(halo_surface, (*rainbow_colors[color_index], 180), (60, 50), halo_radius, 2)
        s.blit(halo_surface, (0, 0))
        
        return s
    
    elif model_style == "aurora":
        # 极光棱镜·光谱盛宴 - 极光通过棱镜、光谱完全展开、色彩盛宴、绚烂夺目
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心：极光核心球体
        core_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8, 0, -1):
            glow_alpha = int(60 * (i / 8))
            pygame.draw.circle(core_glow, (100, 255, 200, glow_alpha), (60, 50), i * 3)
        s.blit(core_glow, (0, 0))
        pygame.draw.circle(s, (150, 255, 220), (60, 50), 12)
        pygame.draw.circle(s, (200, 255, 255), (60, 50), 12, 2)
        
        # 极光波浪（上下流动）
        for wave_idx in range(3):
            wave_y_base = 30 + wave_idx * 20
            wave_points = []
            for x in range(0, 120, 6):
                wave_y = wave_y_base + 8 * math.sin(t * 3 + x * 0.1 + wave_idx)
                wave_points.append((x, wave_y))
            
            # 绘制波浪带
            for i in range(len(wave_points) - 1):
                # 极光颜色渐变
                progress = i / len(wave_points)
                r = int(100 + 100 * math.sin(progress * math.pi + t))
                g = 255
                b = int(200 + 55 * math.cos(progress * math.pi + t))
                pygame.draw.line(s, (r, g, b, 180), 
                               wave_points[i], wave_points[i + 1], 5)
        
        # 光谱色带（从中心向外扩散）
        spectrum_colors = [
            (255, 50, 50),    # 红
            (255, 150, 50),   # 橙
            (255, 255, 50),   # 黄
            (50, 255, 50),    # 绿
            (50, 255, 255),   # 青
            (50, 50, 255),    # 蓝
            (200, 50, 255)    # 紫
        ]
        
        for i, color in enumerate(spectrum_colors):
            angle = (t + i * 0.5) * 2
            radius_base = 20 + i * 3
            # 绘制彩色圆环段
            for seg in range(12):
                seg_angle = angle + seg * math.pi / 6
                radius = radius_base + 3 * math.sin(t * 3 + seg)
                x = 60 + math.cos(seg_angle) * radius
                y = 50 + math.sin(seg_angle) * radius
                size = 4 + int(2 * math.sin(t * 4 + i + seg))
                pygame.draw.circle(s, color, (int(x), int(y)), size)
        
        # 光谱粒子暴雨
        for i in range(50):
            particle_angle = t * 2 + i * 0.4
            particle_dist = 10 + (i % 5) * 8
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            # 循环彩虹色
            color_idx = (int(t * 5) + i) % len(spectrum_colors)
            if 0 <= px <= 120 and 0 <= py <= 120:
                pygame.draw.circle(s, spectrum_colors[color_idx], (int(px), int(py)), 2)
        
        # 螺旋光束（棱镜效果）
        for beam_idx in range(7):
            beam_angle = beam_idx * math.pi * 2 / 7 + t
            beam_color = spectrum_colors[beam_idx]
            # 从中心发出的光束
            for step in range(15):
                dist = 15 + step * 3
                bx = 60 + math.cos(beam_angle) * dist
                by = 50 + math.sin(beam_angle) * dist
                beam_alpha = int(220 * (1 - step / 15))
                if 0 <= bx <= 120 and 0 <= by <= 120:
                    beam_color_alpha = (beam_color[0], beam_color[1], beam_color[2], beam_alpha)
                    pygame.draw.circle(s, beam_color_alpha, (int(bx), int(by)), 3)
        
        # 彩虹光环（脉动）
        for ring_idx in range(5):
            ring_radius = 25 + ring_idx * 8 + int(5 * pulse)
            ring_alpha = int(150 * (1 - ring_idx / 5))
            # 彩虹色环
            hue_phase = (t + ring_idx * 0.3) % 1.0
            ring_r = int(128 + 127 * math.sin(hue_phase * math.pi * 2))
            ring_g = int(128 + 127 * math.sin((hue_phase + 0.33) * math.pi * 2))
            ring_b = int(128 + 127 * math.sin((hue_phase + 0.67) * math.pi * 2))
            pygame.draw.circle(s, (ring_r, ring_g, ring_b, ring_alpha), (60, 50), ring_radius, 2)
        
        # 星光闪烁（光谱盛宴）
        for i in range(30):
            if (int(t * 8) + i) % 4 < 2:
                star_angle = i * 0.7
                star_dist = 35 + 10 * (i % 3)
                sx = 60 + math.cos(star_angle) * star_dist
                sy = 50 + math.sin(star_angle) * star_dist
                if 0 <= sx <= 120 and 0 <= sy <= 120:
                    star_color_idx = i % len(spectrum_colors)
                    pygame.draw.circle(s, spectrum_colors[star_color_idx], (int(sx), int(sy)), 3)
                    # 十字星芒
                    for offset in [-3, 3]:
                        pygame.draw.circle(s, spectrum_colors[star_color_idx], (int(sx) + offset, int(sy)), 1)
                        pygame.draw.circle(s, spectrum_colors[star_color_idx], (int(sx), int(sy) + offset), 1)
        
        return s

    # --- Eclipse MK5/MK6 ---
    elif model_style == "eclipse_abyss":
        # 深渊凝视：大眼 + 连接
        # 连接体
        pygame.draw.line(s, (50, 0, 100), (40, 60), (80, 60), 8)
        pygame.draw.circle(s, (50, 0, 100), (40, 60), 28)
        pygame.draw.circle(s, (50, 0, 100), (80, 60), 28)
        # 眼睛
        pygame.draw.circle(s, (255, 255, 255), (40, 60), 10)
        pygame.draw.circle(s, (0, 0, 0), (40, 60), 5)
        pygame.draw.circle(s, (255, 255, 255), (80, 60), 10)
        pygame.draw.circle(s, (0, 0, 0), (80, 60), 5)
        return s

    elif model_style == "eclipse_shadow":
        # 蚀刻阴影：模糊 + 连接
        # 连接体
        pygame.draw.line(s, (20, 20, 20), (40, 60), (80, 60), 8)
        for i in range(5):
            alpha = 50
            off = i * 2
            pygame.draw.circle(s, (0, 0, 0, alpha), (40+off, 60), 28)
            pygame.draw.circle(s, (0, 0, 0, alpha), (80-off, 60), 28)
        return s
    
    # ========== Necro专属涂装 ==========
    elif model_style == "lich":
        # 巫妖王·不死法师 - 巫妖形态、死亡魔法、灵魂囚笼、不死之力
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：巫妖头颅（骷髅头）
        skull_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(skull_surface, (100, 255, 100, 240), (60, 45), 16)
        pygame.draw.circle(skull_surface, (150, 255, 150, 220), (60, 45), int(16 * pulse))
        # 眼眶（绿色火焰）
        pygame.draw.circle(skull_surface, (50, 200, 50, 255), (54, 42), 5)
        pygame.draw.circle(skull_surface, (50, 200, 50, 255), (66, 42), 5)
        pygame.draw.circle(skull_surface, (150, 255, 150, 255), (54, 42), 3)
        pygame.draw.circle(skull_surface, (150, 255, 150, 255), (66, 42), 3)
        s.blit(skull_surface, (0, 0))
        
        # 灵魂囚笼（环绕的灵魂）
        soul_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            soul_angle = t * 2 + i * math.pi / 4
            soul_dist = 25 + 10 * math.sin(t * 2.5 + i)
            soul_x = 60 + math.cos(soul_angle) * soul_dist
            soul_y = 45 + math.sin(soul_angle) * soul_dist
            # 灵魂形态（小鬼魂）
            pygame.draw.circle(soul_surface, (100, 255, 100, 200), (int(soul_x), int(soul_y)), 5)
            pygame.draw.circle(soul_surface, (150, 255, 150, 180), (int(soul_x), int(soul_y) + 5), 4)
        s.blit(soul_surface, (0, 0))
        
        # 死亡魔法（法术符文）
        magic_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            rune_angle = t + i * math.pi / 3
            rune_dist = 35
            rune_x = 60 + math.cos(rune_angle) * rune_dist
            rune_y = 45 + math.sin(rune_angle) * rune_dist
            # 符文（五角星）
            rune_points = []
            for j in range(5):
                star_angle = rune_angle + j * 2 * math.pi / 5
                star_x = rune_x + math.cos(star_angle) * 4
                star_y = rune_y + math.sin(star_angle) * 4
                rune_points.append((star_x, star_y))
            if len(rune_points) >= 3:
                pygame.draw.polygon(magic_surface, (100, 255, 100, 220), 
                                  [(int(p[0]), int(p[1])) for p in rune_points], 2)
        s.blit(magic_surface, (0, 0))
        
        # 不死之力（能量波动）
        power_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            power_radius = (t * 50 + i * 30) % 90
            power_alpha = int(200 * (1 - power_radius / 90))
            pygame.draw.circle(power_surface, (100, 255, 100, power_alpha), (60, 45), int(power_radius), 2)
        s.blit(power_surface, (0, 0))
        
        return s
    
    elif model_style == "bone":
        # 白骨王座·骸骨帝王 - 白骨王座、骸骨帝王、骨骼军团、死亡统治
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.1 + 1
        
        # 主体：王座（骨架结构）
        throne_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 王座底座
        pygame.draw.rect(throne_surface, (200, 200, 200, 240), (45, 55, 30, 15))
        # 王座靠背
        pygame.draw.rect(throne_surface, (220, 220, 220, 240), (48, 30, 24, 25))
        # 骨刺装饰
        for i in range(5):
            spike_x = 50 + i * 5
            pygame.draw.polygon(throne_surface, (255, 255, 255, 240), 
                              [(spike_x, 30), (spike_x + 2, 25), (spike_x + 4, 30)])
        s.blit(throne_surface, (0, 0))
        
        # 骸骨帝王头颅
        skull_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(skull_surface, (220, 220, 220, 250), (60, 40), 12)
        # 王冠（骨制）
        crown_points = [(54, 32), (60, 28), (66, 32)]
        pygame.draw.polygon(skull_surface, (255, 255, 255, 250), crown_points)
        # 眼眶
        pygame.draw.circle(skull_surface, (100, 100, 100, 255), (56, 40), 3)
        pygame.draw.circle(skull_surface, (100, 100, 100, 255), (64, 40), 3)
        s.blit(skull_surface, (0, 0))
        
        # 骨骼军团（环绕骷髅）
        army_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            army_angle = t * 1.5 + i * math.pi / 4
            army_dist = 35 + 10 * math.sin(t + i)
            army_x = 60 + math.cos(army_angle) * army_dist
            army_y = 50 + math.sin(army_angle) * army_dist
            # 小骷髅头
            pygame.draw.circle(army_surface, (200, 200, 200, 220), (int(army_x), int(army_y)), 5)
            pygame.draw.circle(army_surface, (100, 100, 100, 220), (int(army_x) - 2, int(army_y)), 2)
            pygame.draw.circle(army_surface, (100, 100, 100, 220), (int(army_x) + 2, int(army_y)), 2)
        s.blit(army_surface, (0, 0))
        
        # 死亡统治光环
        aura_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            aura_radius = 20 + i * 10 + int(5 * pulse)
            aura_alpha = int(180 * (1 - i / 3))
            pygame.draw.circle(aura_surface, (220, 220, 220, aura_alpha), (60, 45), aura_radius, 2)
        s.blit(aura_surface, (0, 0))
        
        return s
    
    elif model_style == "plague":
        # 瘟疫传播·死亡疫病 - 瘟疫云团、疾病粒子、感染特效、死亡瘟疫
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：瘟疫核心
        plague_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(plague_surface, (100, 255, 0, 240), (60, 50), 14)
        pygame.draw.circle(plague_surface, (150, 255, 50, 220), (60, 50), int(14 * pulse))
        s.blit(plague_surface, (0, 0))
        
        # 瘟疫云团（扩散烟雾）
        cloud_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            cloud_angle = t + i * math.pi / 6
            cloud_dist = 18 + 12 * math.sin(t * 2 + i)
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 50 + math.sin(cloud_angle) * cloud_dist
            cloud_size = 6 + 4 * math.sin(t * 2.5 + i)
            pygame.draw.circle(cloud_surface, (120, 255, 20, 180), (int(cloud_x), int(cloud_y)), int(cloud_size))
        s.blit(cloud_surface, (0, 0))
        
        # 疾病粒子（漂浮孢子）
        spore_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            spore_angle = t * 1.5 + i * math.pi / 10
            spore_dist = 25 + 20 * (i / 20)
            spore_x = 60 + math.cos(spore_angle) * spore_dist
            spore_y = 50 + math.sin(spore_angle) * spore_dist + 5 * math.sin(t * 3 + i)
            pygame.draw.circle(spore_surface, (150, 255, 50, 220), (int(spore_x), int(spore_y)), 3)
        s.blit(spore_surface, (0, 0))
        
        # 感染特效（蔓延纹路）
        infect_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            infect_angle = i * math.pi / 4
            infect_segments = []
            for j in range(6):
                seg_dist = 15 + j * 4
                seg_angle = infect_angle + math.sin(t * 2 + i + j * 0.5) * 0.3
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist
                infect_segments.append((seg_x, seg_y))
            # 绘制感染线
            for j in range(len(infect_segments) - 1):
                pygame.draw.line(infect_surface, (100, 255, 0, 200), 
                               (int(infect_segments[j][0]), int(infect_segments[j][1])),
                               (int(infect_segments[j+1][0]), int(infect_segments[j+1][1])), 2)
        s.blit(infect_surface, (0, 0))
        
        return s
    
    elif model_style == "soul":
        # 灵魂收集·魂瓶封印 - 魂瓶、封印魂魄、灵魂能量、亡魂哀嚎
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：魂瓶（瓶状）
        bottle_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 瓶身
        pygame.draw.rect(bottle_surface, (0, 220, 255, 200), (50, 45, 20, 25))
        # 瓶颈
        pygame.draw.rect(bottle_surface, (0, 220, 255, 220), (55, 40, 10, 5))
        # 瓶盖
        pygame.draw.rect(bottle_surface, (100, 255, 255, 240), (54, 37, 12, 3))
        # 瓶口光芒
        pygame.draw.circle(bottle_surface, (100, 255, 255, 200), (60, 42), int(6 * pulse))
        s.blit(bottle_surface, (0, 0))
        
        # 封印的魂魄（瓶内灵魂）
        trapped_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(6):
            soul_y = 48 + i * 3 + int(5 * math.sin(t * 3 + i))
            if 48 <= soul_y <= 68:
                pygame.draw.circle(trapped_surface, (50, 240, 255, 220), (60, int(soul_y)), 3)
        s.blit(trapped_surface, (0, 0))
        
        # 灵魂能量涌动（从瓶口溢出）
        energy_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            energy_angle = t * 2 + i * math.pi / 5
            energy_dist = 10 + 15 * (i / 10)
            energy_x = 60 + math.cos(energy_angle) * energy_dist
            energy_y = 40 - (i / 10) * 15
            pygame.draw.circle(energy_surface, (100, 255, 255, int(220 * (1 - i / 10))), 
                             (int(energy_x), int(energy_y)), 3)
        s.blit(energy_surface, (0, 0))
        
        # 亡魂哀嚎（环绕鬼魂）
        ghost_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            ghost_angle = t * 1.5 + i * math.pi / 4
            ghost_dist = 30 + 10 * math.sin(t * 2 + i)
            ghost_x = 60 + math.cos(ghost_angle) * ghost_dist
            ghost_y = 55 + math.sin(ghost_angle) * ghost_dist
            # 鬼魂形态
            pygame.draw.circle(ghost_surface, (0, 220, 255, 180), (int(ghost_x), int(ghost_y)), 5)
            pygame.draw.circle(ghost_surface, (100, 255, 255, 160), (int(ghost_x), int(ghost_y) + 5), 4)
        s.blit(ghost_surface, (0, 0))
        
        return s
    
    elif model_style == "reaper":
        # 死神化身·灵魂收割 - 死神形态、收割镰刀、死亡宣判、生命终结
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体：死神头颅（骷髅）
        reaper_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(reaper_surface, (150, 0, 150, 240), (60, 45), 14)
        # 眼窝（紫色火焰）
        pygame.draw.circle(reaper_surface, (200, 100, 200, 255), (55, 43), 4)
        pygame.draw.circle(reaper_surface, (200, 100, 200, 255), (65, 43), 4)
        # 兜帽
        hood_points = [(45, 35), (60, 30), (75, 35), (70, 50), (50, 50)]
        pygame.draw.polygon(reaper_surface, (80, 0, 80, 220), hood_points)
        s.blit(reaper_surface, (0, 0))
        
        # 收割镰刀
        scythe_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 镰刀柄
        pygame.draw.line(scythe_surface, (100, 50, 100, 240), (60, 55), (60, 75), 4)
        # 镰刀刃（弧形）
        blade_points = [(60, 50), (75, 45), (78, 48), (62, 55)]
        pygame.draw.polygon(scythe_surface, (180, 50, 180, 240), blade_points)
        pygame.draw.polygon(scythe_surface, (200, 100, 200, 240), blade_points, 2)
        s.blit(scythe_surface, (0, 0))
        
        # 死亡宣判（降临光柱）
        judgment_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(5):
            beam_x = 58 + i
            beam_alpha = int(200 * math.sin(t * 3 + i))
            if beam_alpha > 0:
                pygame.draw.line(judgment_surface, (150, 0, 150, beam_alpha), 
                               (beam_x, 20), (beam_x, 80), 3)
        s.blit(judgment_surface, (0, 0))
        
        # 灵魂收割粒子
        harvest_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            harvest_angle = t * 2 + i * math.pi / 7.5
            harvest_dist = 25 + 15 * math.sin(t * 2.5 + i)
            harvest_x = 60 + math.cos(harvest_angle) * harvest_dist
            harvest_y = 50 + math.sin(harvest_angle) * harvest_dist
            pygame.draw.circle(harvest_surface, (180, 50, 180, 220), (int(harvest_x), int(harvest_y)), 3)
        s.blit(harvest_surface, (0, 0))
        
        # 生命终结光环
        end_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            end_radius = (t * 55 + i * 30) % 85
            end_alpha = int(200 * (1 - end_radius / 85))
            pygame.draw.circle(end_surface, (150, 0, 150, end_alpha), (60, 50), int(end_radius), 2)
        s.blit(end_surface, (0, 0))
        
        return s
    
    elif model_style == "vampire":
        # 吸血鬼伯爵·永夜不朽 - 吸血鬼形态、蝙蝠群、鲜血吸收、永夜不朽
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体：吸血鬼头像（苍白面容）
        vampire_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(vampire_surface, (150, 0, 50, 240), (60, 45), 14)
        # 眼睛（红色）
        pygame.draw.circle(vampire_surface, (200, 50, 100, 255), (55, 43), 3)
        pygame.draw.circle(vampire_surface, (200, 50, 100, 255), (65, 43), 3)
        # 獠牙
        pygame.draw.polygon(vampire_surface, (255, 255, 255, 255), [(57, 50), (57, 55), (59, 52)])
        pygame.draw.polygon(vampire_surface, (255, 255, 255, 255), [(63, 50), (63, 55), (61, 52)])
        s.blit(vampire_surface, (0, 0))
        
        # 蝙蝠群（飞舞）
        bat_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            bat_angle = t * 2.5 + i * math.pi / 4
            bat_dist = 25 + 15 * math.sin(t * 2 + i)
            bat_x = 60 + math.cos(bat_angle) * bat_dist
            bat_y = 45 + math.sin(bat_angle) * bat_dist
            # 蝙蝠形态（简化翅膀）
            wing_span = 6 + 2 * math.sin(t * 5 + i)
            pygame.draw.line(bat_surface, (80, 0, 40, 220), 
                           (int(bat_x - wing_span), int(bat_y)), 
                           (int(bat_x + wing_span), int(bat_y)), 2)
            pygame.draw.circle(bat_surface, (100, 0, 50, 220), (int(bat_x), int(bat_y)), 2)
        s.blit(bat_surface, (0, 0))
        
        # 鲜血吸收（血液粒子流向中心）
        blood_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(15):
            blood_progress = ((t * 2 + i * 0.2) % 1)
            blood_angle = i * math.pi / 7.5
            blood_dist = 40 - blood_progress * 25
            blood_x = 60 + math.cos(blood_angle) * blood_dist
            blood_y = 45 + math.sin(blood_angle) * blood_dist
            blood_alpha = int(220 * (1 - blood_progress))
            pygame.draw.circle(blood_surface, (180, 20, 70, blood_alpha), (int(blood_x), int(blood_y)), 3)
        s.blit(blood_surface, (0, 0))
        
        # 永夜光环（暗红色）
        aura_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(3):
            aura_radius = 18 + i * 10 + int(6 * pulse)
            aura_alpha = int(180 * (1 - i / 3))
            pygame.draw.circle(aura_surface, (150, 0, 50, aura_alpha), (60, 45), aura_radius, 2)
        s.blit(aura_surface, (0, 0))
        
        return s
    
    elif model_style == "undead":
        # 不死军团·永恒行军 - 军团行军、永恒战争、亡者复苏、死而复生
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.1 + 1
        
        # 主体：军团旗帜（骷髅标志）
        banner_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 旗杆
        pygame.draw.line(banner_surface, (100, 160, 100, 240), (60, 30), (60, 70), 4)
        # 旗帜
        flag_points = [(60, 30), (75, 35), (75, 50), (60, 45)]
        pygame.draw.polygon(banner_surface, (80, 120, 80, 220), flag_points)
        # 骷髅标志
        pygame.draw.circle(banner_surface, (150, 200, 150, 240), (67, 40), 4)
        pygame.draw.circle(banner_surface, (50, 100, 50, 255), (66, 39), 1)
        pygame.draw.circle(banner_surface, (50, 100, 50, 255), (68, 39), 1)
        s.blit(banner_surface, (0, 0))
        
        # 行军的军团（前进的骷髅）
        legion_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(10):
            legion_x = 30 + (t * 20 + i * 8) % 60
            legion_y = 60 + i % 3 * 8
            # 骷髅头
            pygame.draw.circle(legion_surface, (150, 200, 150, 220), (int(legion_x), legion_y), 4)
            # 眼眶
            pygame.draw.circle(legion_surface, (80, 120, 80, 220), (int(legion_x) - 1, legion_y), 1)
            pygame.draw.circle(legion_surface, (80, 120, 80, 220), (int(legion_x) + 1, legion_y), 1)
        s.blit(legion_surface, (0, 0))
        
        # 亡者复苏特效（从地面升起）
        rise_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            rise_x = 40 + i * 10
            rise_progress = ((t * 2 + i * 0.3) % 1)
            rise_y = 80 - rise_progress * 20
            rise_alpha = int(220 * rise_progress)
            if rise_alpha > 50:
                pygame.draw.circle(rise_surface, (100, 160, 100, rise_alpha), (rise_x, int(rise_y)), 3)
        s.blit(rise_surface, (0, 0))
        
        # 永恒战争能量（环绕旋转）
        war_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(12):
            war_angle = t * 2 + i * math.pi / 6
            war_dist = 30 + 8 * math.sin(t * 2.5 + i)
            war_x = 60 + math.cos(war_angle) * war_dist
            war_y = 50 + math.sin(war_angle) * war_dist
            pygame.draw.circle(war_surface, (150, 200, 150, 220), (int(war_x), int(war_y)), 3)
        s.blit(war_surface, (0, 0))
        
        return s

    # --- Prism MK5/MK6 ---
    elif model_style == "prism_laser":
        # 激光矩阵：红线
        pts = [(60, 5), (40, 90), (80, 90)]
        pygame.draw.polygon(s, (100, 0, 0), pts)
        # 激光束
        pygame.draw.line(s, (255, 0, 0), (60, 5), (60, 120), 2)
        pygame.draw.line(s, (255, 0, 0), (40, 90), (40, 120), 2)
        pygame.draw.line(s, (255, 0, 0), (80, 90), (80, 120), 2)
        return s

    elif model_style == "prism_glass":
        # 琉璃幻境：多彩
        pts = [(60, 5), (40, 90), (80, 90)]
        # 渐变填充模拟
        for i in range(10):
            col = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            y = 10 + i * 8
            if y < 90:
                pygame.draw.line(s, col, (50, y), (70, y), 4)
        pygame.draw.polygon(s, (255, 255, 255), pts, 2)
        return s

    # --- Necro MK5/MK6 ---
    elif model_style == "necro_plague":
        # 瘟疫之源：绿色气体 + 腐化骨架
        # 头骨主体
        pygame.draw.circle(s, (50, 100, 50), (60, 45), 22)
        pygame.draw.rect(s, (50, 100, 50), (45, 55, 30, 30))
        # 腐化眼窝
        pygame.draw.circle(s, (0, 50, 0), (52, 40), 5)
        pygame.draw.circle(s, (0, 50, 0), (68, 40), 5)
        pygame.draw.circle(s, (100, 255, 0), (52, 40), 2)
        pygame.draw.circle(s, (100, 255, 0), (68, 40), 2)
        # 骨架肋部
        for i, x in enumerate([45, 60, 75]):
            pygame.draw.line(s, (40, 90, 40), (x, 80), (x - 5, 105), 3)
        # 气泡
        for i in range(5):
            bx = random.randint(40, 80)
            by = random.randint(40, 80)
            pygame.draw.circle(s, (0, 255, 0), (bx, by), 3)
        return s

    elif model_style == "necro_soul":
        # 灵魂容器：蓝火 + 幽灵骨架
        # 头骨主体
        pygame.draw.circle(s, (0, 0, 100), (60, 45), 22)
        pygame.draw.rect(s, (0, 0, 100), (45, 55, 30, 30))
        # 灵魂面孔
        pygame.draw.circle(s, (0, 200, 255), (55, 40), 2)
        pygame.draw.circle(s, (0, 200, 255), (65, 40), 2)
        pygame.draw.arc(s, (0, 200, 255), (55, 50, 10, 5), 0, 3.14, 1)
        # 骨架肋部 (半透明)
        for i, x in enumerate([45, 60, 75]):
            pygame.draw.line(s, (0, 100, 200), (x, 80), (x - 5, 105), 3)
        # 灵魂火焰
        pygame.draw.circle(s, (0, 100, 255), (60, 45), 24, 1)
        return s

    # --- Gaia MK7/MK8/MK9 ---
    elif model_style == "gaia_world_tree":
        # 世界树：巨树形态
        pygame.draw.rect(s, (100, 50, 0), (50, 40, 20, 80)) # 树干
        # 树冠
        for i in range(5):
            angle = i * math.pi / 2.5 + t
            lx = 60 + math.cos(angle) * 40
            ly = 40 + math.sin(angle) * 20
            pygame.draw.circle(s, (0, 200, 50), (int(lx), int(ly)), 20)
        # 飘落的叶子
        for i in range(5):
            ly = (t * 50 + i * 20) % 120
            lx = 60 + math.sin(ly * 0.1) * 30
            pygame.draw.circle(s, (100, 255, 0), (int(lx), int(ly)), 3)
        return s

    # --- Eclipse MK7/MK8/MK9 ---
    elif model_style == "eclipse_black_hole":
        # 黑洞：吸积盘
        pygame.draw.circle(s, (0, 0, 0), (60, 60), 20)
        pygame.draw.circle(s, (255, 255, 255), (60, 60), 22, 1)
        # 旋转吸积盘
        for i in range(20):
            angle = t * 5 + i * 0.3
            dist = 30 + i * 2
            px = 60 + math.cos(angle) * dist
            py = 60 + math.sin(angle) * dist * 0.3
            pygame.draw.circle(s, (100, 0, 200), (int(px), int(py)), 2)
        return s

    elif model_style == "eclipse_event_horizon":
        # 视界：扭曲光线
        pygame.draw.circle(s, (0, 0, 0), (60, 60), 25)
        # 光线扭曲
        for i in range(10):
            angle = t * 2 + i * 0.6
            px = 60 + math.cos(angle) * 35
            py = 60 + math.sin(angle) * 35
            pygame.draw.line(s, (255, 255, 255), (60, 60), (px, py), 1)
        return s

    # --- Prism MK7/MK8/MK9 ---
    elif model_style == "prism_spectrum":
        # 全光谱：RGB循环
        pts = [(60, 10), (20, 90), (100, 90)]
        # 动态颜色
        r = int(127 + 127 * math.sin(t))
        g = int(127 + 127 * math.sin(t + 2))
        b = int(127 + 127 * math.sin(t + 4))
        pygame.draw.polygon(s, (r, g, b), pts, 2)
        # 内部光束
        pygame.draw.line(s, (r, g, b), (60, 10), (60, 90), 4)
        return s

    # --- Necro MK7/MK8/MK9 ---
    elif model_style == "necro_death_knight":
        # 死亡骑士：黑甲红眼
        pygame.draw.polygon(s, (20, 20, 20), [(60, 10), (100, 40), (80, 100), (40, 100), (20, 40)])
        pygame.draw.polygon(s, (100, 0, 0), [(60, 10), (100, 40), (80, 100), (40, 100), (20, 40)], 2)
        # 红眼
        pygame.draw.circle(s, (255, 0, 0), (45, 40), 4)
        pygame.draw.circle(s, (255, 0, 0), (75, 40), 4)
        # 符文剑
        pygame.draw.line(s, (0, 200, 255), (60, 20), (60, 90), 2)
        return s

    # --- Striker MK7/MK8/MK9 ---
    elif model_style == "striker_mecha_god":
        # 机甲之神：高达风
        pygame.draw.polygon(s, (255, 255, 255), [(60, 10), (100, 30), (80, 100), (40, 100), (20, 30)])
        pygame.draw.polygon(s, (0, 0, 255), [(60, 10), (100, 30), (80, 50), (40, 50), (20, 30)])
        pygame.draw.circle(s, (0, 255, 0), (60, 40), 5) # 监视器
        # 浮游炮
        for i in range(2):
            py = 30 + math.sin(t * 5 + i) * 10
            px = 20 if i == 0 else 100
            pygame.draw.rect(s, (255, 255, 255), (px-5, py, 10, 20))
        return s

    elif model_style == "striker_cyber_dragon":
        # 赛博龙：龙头
        pygame.draw.polygon(s, (200, 0, 0), [(60, 10), (90, 40), (80, 90), (40, 90), (30, 40)])
        # 龙须
        pygame.draw.arc(s, (255, 200, 0), (10, 30, 40, 40), 0, 3.14, 2)
        pygame.draw.arc(s, (255, 200, 0), (70, 30, 40, 40), 0, 3.14, 2)
        # 龙眼
        pygame.draw.circle(s, (0, 255, 255), (45, 45), 3)
        pygame.draw.circle(s, (0, 255, 255), (75, 45), 3)
        return s

    elif model_style == "striker_dimension_breaker":
        # 维度粉碎：故障风
        pts = [(60, 10), (110, 90), (60, 110), (10, 90)]
        # 随机偏移
        off_x = random.randint(-2, 2)
        pygame.draw.polygon(s, (255, 0, 255), [(p[0]+off_x, p[1]) for p in pts], 1)
        pygame.draw.polygon(s, (0, 255, 255), [(p[0]-off_x, p[1]) for p in pts], 1)
        return s

    # --- Phantom MK7/MK8/MK9 ---
    elif model_style == "phantom_assassin":
        # 虚空刺客：双刃
        pygame.draw.polygon(s, (20, 0, 40), [(60, 20), (80, 50), (60, 100), (40, 50)])
        # 能量刃
        pygame.draw.line(s, (150, 0, 255), (20, 40), (20, 80), 2)
        pygame.draw.line(s, (150, 0, 255), (100, 40), (100, 80), 2)
        return s

    elif model_style == "phantom_mirage":
        # 海市蜃楼：半透明分身
        pts = [(60, 10), (90, 50), (120, 110), (60, 90), (0, 110), (30, 50)]
        for i in range(3):
            alpha = 100 - i * 30
            off = i * 5
            s_temp = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(s_temp, (100, 255, 255, alpha), [(p[0], p[1]-off) for p in pts], 1)
            s.blit(s_temp, (0, 0))
        return s

    elif model_style == "phantom_time_walker":
        # 时间行者：钟表
        pygame.draw.circle(s, (200, 200, 200), (60, 60), 30, 1)
        # 指针
        angle_h = t
        angle_m = t * 12
        pygame.draw.line(s, (255, 215, 0), (60, 60), (60 + math.cos(angle_h)*15, 60 + math.sin(angle_h)*15), 2)
        pygame.draw.line(s, (255, 215, 0), (60, 60), (60 + math.cos(angle_m)*25, 60 + math.sin(angle_m)*25), 1)
        return s

    # --- Titan MK7/MK8/MK9 ---
    elif model_style == "titan_fortress":
        # 移动要塞：多炮塔
        pygame.draw.rect(s, (50, 50, 50), (20, 20, 80, 80))
        # 四角炮塔
        for x in [20, 100]:
            for y in [20, 100]:
                pygame.draw.circle(s, (100, 100, 100), (x, y), 10)
                pygame.draw.line(s, (255, 100, 0), (x, y), (x, y-15), 3)
        return s

    elif model_style == "titan_behemoth":
        # 比蒙巨兽：生物装甲
        pygame.draw.rect(s, (100, 50, 0), (20, 20, 80, 80), border_radius=10)
        # 呼吸灯
        pulse_val = int(127 + 127 * math.sin(t * 2))
        pygame.draw.circle(s, (255, 50, 0, pulse_val), (60, 60), 20)
        return s

    elif model_style == "titan_earth_shaker":
        # 撼地者：震波
        pygame.draw.rect(s, (150, 100, 50), (30, 30, 60, 60))
        # 震波环
        r = (t * 50) % 60
        pygame.draw.circle(s, (200, 150, 50), (60, 60), int(r), 2)
        return s

    # --- Thunderbird MK7/MK8/MK9 ---
    elif model_style == "thunderbird_thor":
        # 雷神之锤：锤子形状
        pygame.draw.rect(s, (100, 100, 100), (40, 20, 40, 60))
        pygame.draw.line(s, (150, 100, 50), (60, 80), (60, 120), 5)
        # 闪电
        if random.random() < 0.2:
            pygame.draw.line(s, (0, 255, 255), (40, 20), (80, 80), 2)
        return s

    elif model_style == "thunderbird_raijin":
        # 雷神降世：雷鼓
        pygame.draw.circle(s, (200, 0, 0), (60, 60), 30)
        # 环绕鼓
        for i in range(5):
            angle = t + i * math.pi * 2 / 5
            cx = 60 + math.cos(angle) * 45
            cy = 60 + math.sin(angle) * 45
            pygame.draw.circle(s, (100, 100, 0), (int(cx), int(cy)), 8)
        return s

    elif model_style == "thunderbird_storm":
        # 风暴降生：旋风
        pygame.draw.polygon(s, (100, 100, 255), [(60, 20), (20, 100), (100, 100)])
        # 旋风线条
        for i in range(5):
            angle = t * 10 + i
            r = 30 + i * 5
            px = 60 + math.cos(angle) * r
            py = 60 + math.sin(angle) * r * 0.5
            pygame.draw.circle(s, (200, 200, 255), (int(px), int(py)), 2)
        return s

    # --- Viper MK7/MK8/MK9 ---
    elif model_style == "viper_hydra":
        # 九头蛇：多头
        pygame.draw.circle(s, (0, 100, 0), (60, 80), 20)
        for i in range(3):
            angle = -0.5 + i * 0.5
            ex = 60 + math.sin(angle) * 40
            ey = 80 - math.cos(angle) * 40
            pygame.draw.line(s, (0, 150, 0), (60, 80), (ex, ey), 5)
            pygame.draw.circle(s, (0, 200, 0), (int(ex), int(ey)), 8)
        return s

    elif model_style == "viper_basilisk":
        # 蛇怪：石化眼
        pygame.draw.polygon(s, (100, 100, 100), [(60, 20), (40, 100), (80, 100)])
        pygame.draw.circle(s, (255, 255, 0), (60, 50), 10)
        pygame.draw.circle(s, (0, 0, 0), (60, 50), 2) # 瞳孔
        return s

    elif model_style == "viper_venom_lord":
        # 剧毒领主：毒液池
        pygame.draw.circle(s, (100, 0, 200), (60, 60), 30)
        # 冒泡
        if random.random() < 0.3:
            bx = random.randint(40, 80)
            by = random.randint(40, 80)
            pygame.draw.circle(s, (0, 255, 0), (bx, by), 4)
        return s

    # --- Specter MK7/MK8/MK9 ---
    elif model_style == "specter_reaper":
        # 死神：兜帽
        pygame.draw.polygon(s, (20, 20, 20), [(60, 10), (20, 100), (100, 100)])
        pygame.draw.circle(s, (0, 0, 0), (60, 40), 15) # 脸部阴影
        # 镰刀
        pygame.draw.arc(s, (200, 200, 200), (40, 20, 60, 60), 0, 3.14, 2)
        return s

    elif model_style == "specter_banshee":
        # 报丧女妖：声波
        pygame.draw.circle(s, (200, 200, 255), (60, 50), 20)
        # 声波扩散
        r = (t * 50) % 60
        pygame.draw.circle(s, (150, 150, 255), (60, 50), int(r), 1)
        return s

    elif model_style == "specter_soul_eater":
        # 噬魂者：大嘴
        pygame.draw.circle(s, (100, 0, 0), (60, 60), 30)
        pygame.draw.rect(s, (0, 0, 0), (40, 50, 40, 20)) # 嘴
        # 牙齿
        for i in range(5):
            x = 40 + i * 8
            pygame.draw.polygon(s, (255, 255, 255), [(x, 50), (x+4, 60), (x+8, 50)])
        return s

    # --- Aurora MK7/MK8/MK9 ---
    elif model_style == "aurora_borealis":
        # 北极光：流光
        for i in range(10):
            y = 10 + i * 10
            off = math.sin(t * 2 + i * 0.5) * 20
            pygame.draw.line(s, (0, 255, 100), (40+off, y), (80+off, y), 2)
        return s

    elif model_style == "aurora_mystic":
        # 秘法光辉：符文环
        pygame.draw.circle(s, (100, 0, 255), (60, 60), 20)
        pygame.draw.circle(s, (200, 0, 255), (60, 60), 35, 1)
        # 旋转符文
        for i in range(3):
            angle = t + i * 2
            px = 60 + math.cos(angle) * 35
            py = 60 + math.sin(angle) * 35
            pygame.draw.circle(s, (255, 255, 255), (int(px), int(py)), 3)
        return s

    elif model_style == "aurora_celestial":
        # 天界之光：六翼
        pygame.draw.circle(s, (255, 255, 200), (60, 60), 20)
        for i in range(6):
            angle = i * math.pi / 3
            ex = 60 + math.cos(angle) * 50
            ey = 60 + math.sin(angle) * 50
            pygame.draw.line(s, (255, 255, 255, 100), (60, 60), (ex, ey), 10)
        return s

    # --- Crimson MK7/MK8/MK9 ---
    elif model_style == "crimson_vampire":
        # 鲜血伯爵：蝙蝠翼
        pygame.draw.circle(s, (150, 0, 0), (60, 50), 15)
        # 翅膀
        pygame.draw.polygon(s, (100, 0, 0), [(60, 50), (10, 20), (30, 80)])
        pygame.draw.polygon(s, (100, 0, 0), [(60, 50), (110, 20), (90, 80)])
        return s

    elif model_style == "crimson_blood_king":
        # 血色君王：王冠
        pygame.draw.rect(s, (200, 0, 0), (40, 40, 40, 60))
        pygame.draw.polygon(s, (255, 215, 0), [(40, 40), (40, 20), (50, 30), (60, 10), (70, 30), (80, 20), (80, 40)])
        return s

    elif model_style == "crimson_hell_fire":
        # 地狱火：全身火焰
        pygame.draw.circle(s, (255, 100, 0), (60, 60), 30)
        for i in range(10):
            angle = random.uniform(0, 6.28)
            dist = random.randint(30, 50)
            px = 60 + math.cos(angle) * dist
            py = 60 + math.sin(angle) * dist
            pygame.draw.circle(s, (255, 50, 0), (int(px), int(py)), 5)
        return s

    # --- Stalker MK7/MK8/MK9 ---
    elif model_style == "stalker_predator":
        # 铁血战士：面具
        pygame.draw.polygon(s, (150, 150, 150), [(40, 20), (80, 20), (70, 80), (50, 80)])
        # 激光点
        pygame.draw.circle(s, (255, 0, 0), (75, 30), 2)
        pygame.draw.circle(s, (255, 0, 0), (72, 35), 2)
        pygame.draw.circle(s, (255, 0, 0), (78, 35), 2)
        return s

    elif model_style == "stalker_night_stalker":
        # 夜魔：红眼黑影
        pygame.draw.circle(s, (0, 0, 0), (60, 60), 30)
        pygame.draw.circle(s, (255, 0, 0), (50, 50), 3)
        pygame.draw.circle(s, (255, 0, 0), (70, 50), 3)
        return s

    elif model_style == "stalker_void_hunter":
        # 虚空猎手：紫色护目镜
        pygame.draw.rect(s, (50, 0, 100), (40, 20, 40, 80))
        pygame.draw.rect(s, (200, 0, 255), (40, 30, 40, 10))
        return s

    # --- Arbiter MK7/MK8/MK9 ---
    elif model_style == "arbiter_truth":
        # 真理之眼：金字塔眼
        pygame.draw.polygon(s, (255, 255, 255), [(60, 20), (100, 90), (20, 90)])
        pygame.draw.circle(s, (0, 200, 255), (60, 65), 10)
        return s

    elif model_style == "arbiter_order":
        # 秩序守护者：完美几何
        pygame.draw.rect(s, (255, 215, 0), (40, 40, 40, 40), 2)
        pygame.draw.circle(s, (255, 215, 0), (60, 60), 20, 2)
        pygame.draw.line(s, (255, 215, 0), (60, 20), (60, 100), 2)
        pygame.draw.line(s, (255, 215, 0), (20, 60), (100, 60), 2)
        return s

    elif model_style == "arbiter_divinity":
        # 神性：光环
        pygame.draw.circle(s, (255, 255, 200), (60, 60), 20)
        # 多重光环
        pygame.draw.circle(s, (255, 215, 0), (60, 60), 35, 2)
        pygame.draw.circle(s, (255, 215, 0), (60, 60), 45, 1)
        return s

    # ========== 16种新专属涂装外形 ==========
    elif model_style == "striker_ex":
        # 裂空雷刃 - 分叉闪电刀刃，动态电弧
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 主刃身（闪电形状）
        blade_points = [(60, 10), (70, 35), (65, 35), (75, 60), (70, 60), (80, 90), (60, 75), (40, 90), (50, 60), (45, 60), (55, 35), (50, 35)]
        pygame.draw.polygon(s, (255, 255, 100), blade_points)
        pygame.draw.polygon(s, (255, 255, 255), blade_points, 3)
        
        # 电弧效果
        for i in range(6):
            if random.random() < 0.3:
                start_idx = random.randint(0, len(blade_points)-1)
                end_idx = random.randint(0, len(blade_points)-1)
                pygame.draw.line(s, (200, 255, 255), blade_points[start_idx], blade_points[end_idx], 2)
        
        # 能量核心
        pygame.draw.circle(s, (255, 255, 255), (60, 50), int(8 * pulse))
        
        return s
    
    elif model_style == "phantom_ex":
        # 虚影裂隙 - 多层空间扭曲，相位偏移
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 多层相位飞机（3层错位）
        for layer in range(3):
            offset_x = int(10 * math.sin(t * 2 + layer * 2))
            offset_y = layer * 5
            alpha = 180 - layer * 50
            
            layer_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            phantom_points = [(60 + offset_x, 15 + offset_y), (85 + offset_x, 50 + offset_y), (75 + offset_x, 85 + offset_y), (45 + offset_x, 85 + offset_y), (35 + offset_x, 50 + offset_y)]
            pygame.draw.polygon(layer_surf, (150, 0, 255, alpha), phantom_points)
            pygame.draw.polygon(layer_surf, (200, 100, 255, alpha), phantom_points, 2)
            s.blit(layer_surf, (0, 0))
        
        # 空间裂隙
        for i in range(8):
            angle = t * 3 + i * math.pi / 4
            dist = 35 + 5 * math.sin(t * 4 + i)
            px = 60 + math.cos(angle) * dist
            py = 50 + math.sin(angle) * dist
            pygame.draw.circle(s, (255, 0, 255), (int(px), int(py)), 3)
        
        return s
    
    elif model_style == "titan_ex":
        # 重装巨锤 - 锤形机体，冲击波扩散
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 锤头（巨大矩形）
        hammer_rect = pygame.Rect(30, 20, 60, 40)
        pygame.draw.rect(s, (100, 100, 100), hammer_rect)
        pygame.draw.rect(s, (150, 150, 150), hammer_rect, 4)
        
        # 锤柄
        pygame.draw.rect(s, (80, 80, 80), (52, 60, 16, 35))
        
        # 冲击波（扩散圆环）
        for i in range(3):
            wave_radius = (t * 60 + i * 25) % 75
            wave_alpha = int(200 * (1 - wave_radius / 75))
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (255, 200, 0, wave_alpha), (60, 40), int(wave_radius), 3)
            s.blit(wave_surf, (0, 0))
        
        # 能量脉冲
        pygame.draw.circle(s, (255, 150, 0), (60, 40), int(12 * pulse))
        
        return s
    
    elif model_style == "thunderbird_ex":
        # 极光风暴 - 多层展翼，极光流动
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 三层翅膀（由内到外）
        for layer in range(3):
            wing_span = 40 + layer * 15
            wing_height = 30 + layer * 10
            alpha = 220 - layer * 40
            
            wing_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 左翼
            left_wing = [(60, 50), (60 - wing_span, 50 - wing_height), (60 - wing_span, 50 + wing_height)]
            pygame.draw.polygon(wing_surf, (0, 255, 200, alpha), left_wing)
            # 右翼
            right_wing = [(60, 50), (60 + wing_span, 50 - wing_height), (60 + wing_span, 50 + wing_height)]
            pygame.draw.polygon(wing_surf, (0, 255, 200, alpha), right_wing)
            s.blit(wing_surf, (0, 0))
        
        # 极光粒子流
        for i in range(20):
            particle_angle = t * 3 + i * math.pi / 10
            particle_dist = 30 + 20 * (i / 20)
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            # 彩虹色
            hue = (t * 50 + i * 18) % 360
            color_r = int(127 + 127 * math.sin(math.radians(hue)))
            color_g = int(127 + 127 * math.sin(math.radians(hue + 120)))
            color_b = int(127 + 127 * math.sin(math.radians(hue + 240)))
            pygame.draw.circle(s, (color_r, color_g, color_b), (int(px), int(py)), 3)
        
        return s
    
    elif model_style == "viper_ex":
        # 异形孢子 - 生物触手，孢子飘散
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中央孢囊
        pygame.draw.circle(s, (100, 255, 0), (60, 50), int(18 * pulse))
        pygame.draw.circle(s, (150, 255, 100), (60, 50), int(18 * pulse), 3)
        
        # 8根触手（动态摆动）
        for i in range(8):
            angle = i * math.pi / 4
            # 触手分段
            segments = []
            for j in range(6):
                seg_dist = 20 + j * 6
                seg_angle = angle + math.sin(t * 3 + i + j * 0.5) * 0.4
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist
                segments.append((int(seg_x), int(seg_y)))
            
            # 绘制触手
            for j in range(len(segments) - 1):
                width = 6 - j
                pygame.draw.line(s, (80, 200, 0), segments[j], segments[j+1], width)
        
        # 孢子飘散
        for i in range(15):
            spore_angle = t * 2 + i * 0.4
            spore_dist = 25 + (t * 20 + i * 5) % 40
            spx = 60 + math.cos(spore_angle) * spore_dist
            spy = 50 + math.sin(spore_angle) * spore_dist
            pygame.draw.circle(s, (150, 255, 50), (int(spx), int(spy)), 4)
        
        return s
    
    elif model_style == "specter_ex":
        # 幽冥镰刀 - 巨型镰刀，挥砍动画
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 镰刀摆动角度
        swing_angle = math.sin(t * 2) * 0.6
        
        # 镰刀柄
        handle_start = (60, 70)
        handle_end = (60 + int(30 * math.sin(swing_angle)), 30 + int(10 * math.cos(swing_angle)))
        pygame.draw.line(s, (100, 100, 100), handle_start, handle_end, 6)
        
        # 镰刀刃（弧形）
        blade_center = handle_end
        blade_curve = []
        for i in range(10):
            curve_angle = swing_angle - math.pi / 2 + i * 0.2
            curve_dist = 25 + i * 2
            bx = blade_center[0] + int(math.cos(curve_angle) * curve_dist)
            by = blade_center[1] + int(math.sin(curve_angle) * curve_dist)
            blade_curve.append((bx, by))
        
        pygame.draw.lines(s, (200, 200, 255), False, blade_curve, 8)
        
        # 幽冥气息
        for i in range(12):
            ghost_angle = t * 2 + i * math.pi / 6
            ghost_dist = 30 + 10 * math.sin(t * 3 + i)
            gx = 60 + math.cos(ghost_angle) * ghost_dist
            gy = 50 + math.sin(ghost_angle) * ghost_dist
            pygame.draw.circle(s, (150, 150, 255, 180), (int(gx), int(gy)), 4)
        
        return s
    
    elif model_style == "aurora_ex":
        # 星环女神 - 多重旋转光环，星光闪耀
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心女神形态（人形轮廓）
        pygame.draw.circle(s, (255, 220, 255), (60, 45), 12)
        pygame.draw.polygon(s, (200, 180, 255), [(60, 57), (50, 75), (70, 75)])
        
        # 5个旋转光环
        for ring in range(5):
            ring_radius = 20 + ring * 8
            ring_angle_offset = t * (1 + ring * 0.3)
            ring_alpha = int(200 - ring * 30)
            
            ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 绘制环上的光点
            for i in range(12):
                point_angle = ring_angle_offset + i * math.pi / 6
                px = 60 + math.cos(point_angle) * ring_radius
                py = 50 + math.sin(point_angle) * ring_radius
                pygame.draw.circle(ring_surf, (255, 200, 255, ring_alpha), (int(px), int(py)), 3)
            
            # 绘制环线
            pygame.draw.circle(ring_surf, (255, 180, 255, ring_alpha // 2), (60, 50), ring_radius, 1)
            s.blit(ring_surf, (0, 0))
        
        # 星光闪烁
        for i in range(20):
            if (int(t * 10) + i) % 4 < 2:
                star_x = 20 + (i * 5) % 80
                star_y = 20 + (i * 7) % 60
                pygame.draw.circle(s, (255, 255, 255), (star_x, star_y), 2)
        
        return s
    
    elif model_style == "crimson_ex":
        # 血色尖刺 - 尖刺向外延伸，血液飞溅
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 中心血核
        pygame.draw.circle(s, (200, 0, 0), (60, 50), int(15 * pulse))
        pygame.draw.circle(s, (255, 50, 50), (60, 50), int(15 * pulse), 2)
        
        # 8根尖刺（动态伸缩）
        for i in range(8):
            spike_angle = i * math.pi / 4
            spike_length = 25 + 15 * math.sin(t * 3 + i)
            
            # 尖刺顶点
            spike_tip_x = 60 + math.cos(spike_angle) * spike_length
            spike_tip_y = 50 + math.sin(spike_angle) * spike_length
            
            # 尖刺基座（三角形）
            base_angle1 = spike_angle + 0.3
            base_angle2 = spike_angle - 0.3
            base_dist = 12
            base1_x = 60 + math.cos(base_angle1) * base_dist
            base1_y = 50 + math.sin(base_angle1) * base_dist
            base2_x = 60 + math.cos(base_angle2) * base_dist
            base2_y = 50 + math.sin(base_angle2) * base_dist
            
            spike_points = [(int(spike_tip_x), int(spike_tip_y)), (int(base1_x), int(base1_y)), (int(base2_x), int(base2_y))]
            pygame.draw.polygon(s, (180, 0, 0), spike_points)
            pygame.draw.polygon(s, (255, 0, 0), spike_points, 2)
        
        # 血液飞溅粒子
        for i in range(15):
            blood_angle = t * 4 + i * 0.4
            blood_dist = 20 + (t * 30 + i * 5) % 35
            bx = 60 + math.cos(blood_angle) * blood_dist
            by = 50 + math.sin(blood_angle) * blood_dist
            pygame.draw.circle(s, (200, 0, 50), (int(bx), int(by)), 3)
        
        return s
    
    elif model_style == "stalker_ex":
        # 异界猎手 - 昆虫节肢结构，复眼闪光
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 主体（昆虫头胸）
        pygame.draw.ellipse(s, (80, 0, 120), (40, 35, 40, 30))
        pygame.draw.ellipse(s, (120, 0, 180), (40, 35, 40, 30), 3)
        
        # 复眼（闪烁）
        for eye_x in [50, 70]:
            eye_brightness = int(155 + 100 * math.sin(t * 5))
            pygame.draw.circle(s, (eye_brightness, 0, eye_brightness), (eye_x, 45), 6)
        
        # 6条节肢（3对）
        for pair in range(3):
            for side in [-1, 1]:
                leg_base_y = 40 + pair * 8
                leg_angle = side * (math.pi / 3 + pair * 0.2) + math.sin(t * 3 + pair) * 0.2
                
                # 节肢分段
                segments = []
                for seg in range(4):
                    seg_dist = 15 + seg * 8
                    seg_x = 60 + side * math.cos(leg_angle) * seg_dist
                    seg_y = leg_base_y + math.sin(leg_angle) * seg_dist * 0.5
                    segments.append((int(seg_x), int(seg_y)))
                
                # 绘制节肢
                for seg in range(len(segments) - 1):
                    pygame.draw.line(s, (100, 0, 150), segments[seg], segments[seg+1], 4)
        
        # 触须
        for side in [-1, 1]:
            antenna = []
            for i in range(5):
                ant_x = 60 + side * (5 + i * 3)
                ant_y = 35 - i * 4 + math.sin(t * 4 + side) * 3
                antenna.append((int(ant_x), int(ant_y)))
            pygame.draw.lines(s, (150, 0, 200), False, antenna, 2)
        
        return s
    
    elif model_style == "gaia_ex":
        # 晶体丛林 - 生长的水晶，脉动光芒
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心地核
        pygame.draw.circle(s, (0, 150, 100), (60, 50), 15)
        pygame.draw.circle(s, (0, 200, 150), (60, 50), 15, 2)
        
        # 12根水晶柱（向外生长）
        for i in range(12):
            crystal_angle = i * math.pi / 6
            crystal_height = 20 + 15 * math.sin(t * 2 + i * 0.5)
            
            # 水晶基座
            base_x = 60 + math.cos(crystal_angle) * 15
            base_y = 50 + math.sin(crystal_angle) * 15
            
            # 水晶顶部
            tip_x = 60 + math.cos(crystal_angle) * (15 + crystal_height)
            tip_y = 50 + math.sin(crystal_angle) * (15 + crystal_height)
            
            # 水晶侧边
            side_angle1 = crystal_angle + 0.2
            side_angle2 = crystal_angle - 0.2
            side1_x = 60 + math.cos(side_angle1) * 15
            side1_y = 50 + math.sin(side_angle1) * 15
            side2_x = 60 + math.cos(side_angle2) * 15
            side2_y = 50 + math.sin(side_angle2) * 15
            
            crystal_points = [(int(tip_x), int(tip_y)), (int(side1_x), int(side1_y)), (int(side2_x), int(side2_y))]
            
            # 渐变色（由内到外）
            color_intensity = int(155 + 100 * (crystal_height / 35))
            pygame.draw.polygon(s, (0, color_intensity, 100), crystal_points)
            pygame.draw.polygon(s, (0, 255, 150), crystal_points, 2)
            
            # 水晶光芒
            if (int(t * 10) + i) % 3 == 0:
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (0, 255, 150, 150), (int(tip_x), int(tip_y)), 6)
                s.blit(glow_surf, (0, 0))
        
        return s
    
    elif model_style == "weaver_ex":
        # 命运蛛网 - 辐射蛛网，节点闪烁
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心蜘蛛
        pygame.draw.circle(s, (255, 0, 255), (60, 50), int(12 * pulse))
        pygame.draw.circle(s, (255, 100, 255), (60, 50), int(12 * pulse), 2)
        
        # 8根主丝（辐射）
        web_nodes = []
        for i in range(8):
            main_angle = i * math.pi / 4
            
            # 每根主丝3个节点
            for node in range(1, 4):
                node_dist = 20 + node * 15
                node_x = 60 + math.cos(main_angle) * node_dist
                node_y = 50 + math.sin(main_angle) * node_dist
                web_nodes.append((int(node_x), int(node_y)))
                
                # 绘制到中心的丝线
                pygame.draw.line(s, (200, 0, 200), (60, 50), (int(node_x), int(node_y)), 2)
                
                # 节点
                node_size = 5 if (int(t * 8) + i + node) % 3 == 0 else 3
                pygame.draw.circle(s, (255, 150, 255), (int(node_x), int(node_y)), node_size)
        
        # 环形连接丝
        for ring in range(1, 4):
            ring_radius = 20 + ring * 15
            prev_point = None
            for i in range(9):  # 9个点形成闭环
                angle = i * math.pi / 4
                px = 60 + math.cos(angle) * ring_radius
                py = 50 + math.sin(angle) * ring_radius
                current_point = (int(px), int(py))
                
                if prev_point:
                    pygame.draw.line(s, (180, 0, 180), prev_point, current_point, 1)
                prev_point = current_point
        
        return s
    
    elif model_style == "solar_ex":
        # 耀斑之心 - 太阳核心，动态耀斑射线
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 太阳核心（多层辉光）
        for layer in range(5, 0, -1):
            layer_radius = int(18 * pulse * (layer / 5))
            layer_alpha = int(255 * (layer / 5))
            glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 200, 0, layer_alpha), (60, 50), layer_radius)
            s.blit(glow_surf, (0, 0))
        
        pygame.draw.circle(s, (255, 255, 100), (60, 50), 15)
        
        # 12道耀斑射线（动态长度）
        for i in range(12):
            flare_angle = i * math.pi / 6 + t * 0.5
            flare_length = 30 + 20 * math.sin(t * 3 + i)
            
            # 射线起点
            ray_start_x = 60 + math.cos(flare_angle) * 18
            ray_start_y = 50 + math.sin(flare_angle) * 18
            
            # 射线终点
            ray_end_x = 60 + math.cos(flare_angle) * (18 + flare_length)
            ray_end_y = 50 + math.sin(flare_angle) * (18 + flare_length)
            
            # 绘制渐变射线（多层）
            for layer in range(3):
                layer_width = 6 - layer * 2
                layer_alpha = int(220 - layer * 60)
                ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(ray_surf, (255, 150, 0, layer_alpha), 
                               (int(ray_start_x), int(ray_start_y)), 
                               (int(ray_end_x), int(ray_end_y)), layer_width)
                s.blit(ray_surf, (0, 0))
        
        # 日冕粒子
        for i in range(15):
            corona_angle = t * 2 + i * 0.4
            corona_dist = 25 + 15 * math.sin(t * 2.5 + i)
            cx = 60 + math.cos(corona_angle) * corona_dist
            cy = 50 + math.sin(corona_angle) * corona_dist
            pygame.draw.circle(s, (255, 200, 100), (int(cx), int(cy)), 3)
        
        return s
    
    elif model_style == "arbiter_ex":
        # 量子审判 - 概率云，量子纠缠
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心量子核心
        pygame.draw.circle(s, (0, 255, 255), (60, 50), int(12 * pulse))
        pygame.draw.circle(s, (100, 255, 255), (60, 50), int(12 * pulse), 3)
        
        # 概率云（随机位置粒子）
        for i in range(30):
            # 使用确定性随机（基于时间和索引）
            cloud_angle = (t * 3 + i * 0.7) % (2 * math.pi)
            cloud_dist = 20 + 25 * ((math.sin(t * 2 + i) + 1) / 2)
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 50 + math.sin(cloud_angle) * cloud_dist
            
            # 量子闪烁
            if (int(t * 15) + i) % 5 < 3:
                particle_alpha = int(200 * ((math.sin(t * 5 + i) + 1) / 2))
                pygame.draw.circle(s, (0, 200, 255, particle_alpha), (int(cloud_x), int(cloud_y)), 2)
        
        # 量子纠缠连线（随机连接粒子）
        entangle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            angle1 = (t * 3 + i) % (2 * math.pi)
            angle2 = (t * 3 + i + 3) % (2 * math.pi)
            dist1 = 30 + 15 * math.sin(t * 2 + i)
            dist2 = 30 + 15 * math.sin(t * 2 + i + 3)
            
            x1 = 60 + math.cos(angle1) * dist1
            y1 = 50 + math.sin(angle1) * dist1
            x2 = 60 + math.cos(angle2) * dist2
            y2 = 50 + math.sin(angle2) * dist2
            
            pygame.draw.line(entangle_surf, (0, 255, 255, 150), (int(x1), int(y1)), (int(x2), int(y2)), 1)
        s.blit(entangle_surf, (0, 0))
        
        # 审判光环
        for ring in range(3):
            ring_radius = 20 + ring * 12
            ring_alpha = int(180 - ring * 50)
            ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (0, 255, 255, ring_alpha), (60, 50), ring_radius, 2)
            s.blit(ring_surf, (0, 0))
        
        return s
    
    elif model_style == "eclipse_ex":
        # 日食幽灵 - 日月重叠，暗影吞噬
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 背后的太阳（金色）
        sun_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for layer in range(4, 0, -1):
            sun_radius = int(20 * pulse * (layer / 4))
            sun_alpha = int(200 * (layer / 4))
            pygame.draw.circle(sun_surf, (255, 200, 0, sun_alpha), (55, 50), sun_radius)
        s.blit(sun_surf, (0, 0))
        
        # 前方的月亮（黑暗）- 逐渐移动遮挡太阳
        moon_x = 55 + int(10 * math.sin(t * 0.8))
        pygame.draw.circle(s, (0, 0, 0), (moon_x, 50), 18)
        pygame.draw.circle(s, (100, 0, 150), (moon_x, 50), 18, 2)
        
        # 日冕（从边缘露出）
        corona_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(16):
            corona_angle = i * math.pi / 8
            corona_length = 15 + 8 * math.sin(t * 2.5 + i)
            
            # 从太阳中心向外
            corona_start_x = 55 + math.cos(corona_angle) * 20
            corona_start_y = 50 + math.sin(corona_angle) * 20
            corona_end_x = 55 + math.cos(corona_angle) * (20 + corona_length)
            corona_end_y = 50 + math.sin(corona_angle) * (20 + corona_length)
            
            pygame.draw.line(corona_surf, (255, 150, 0, 200), 
                           (int(corona_start_x), int(corona_start_y)),
                           (int(corona_end_x), int(corona_end_y)), 2)
        s.blit(corona_surf, (0, 0))
        
        # 暗影粒子（被吞噬）
        shadow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(20):
            shadow_progress = ((t * 2 + i * 0.3) % 1)
            shadow_angle = i * 0.3
            shadow_dist = 50 - shadow_progress * 30
            shadow_x = moon_x + math.cos(shadow_angle) * shadow_dist
            shadow_y = 50 + math.sin(shadow_angle) * shadow_dist
            shadow_alpha = int(200 * (1 - shadow_progress))
            pygame.draw.circle(shadow_surf, (50, 0, 100, shadow_alpha), (int(shadow_x), int(shadow_y)), 3)
        s.blit(shadow_surf, (0, 0))
        
        return s
    
    elif model_style == "prism_ex":
        # 棱镜折射 - 三棱镜，彩虹光束分离
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心三棱镜（正三角形）
        prism_size = int(25 * pulse)
        prism_points = [
            (60, 50 - prism_size),
            (60 - int(prism_size * 0.866), 50 + int(prism_size * 0.5)),
            (60 + int(prism_size * 0.866), 50 + int(prism_size * 0.5))
        ]
        pygame.draw.polygon(s, (255, 255, 255), prism_points)
        pygame.draw.polygon(s, (200, 200, 255), prism_points, 3)
        
        # 彩虹色谱
        rainbow_colors = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0),
            (0, 255, 255), (0, 0, 255), (127, 0, 255)
        ]
        
        # 三个方向射出彩虹光束
        for direction in range(3):
            base_angle = direction * 2 * math.pi / 3 + math.pi / 6
            
            # 每个方向7种颜色
            for color_idx, color in enumerate(rainbow_colors):
                beam_angle = base_angle + (color_idx - 3) * 0.15
                beam_start_x = prism_points[direction][0]
                beam_start_y = prism_points[direction][1]
                beam_length = 30 + 10 * math.sin(t * 2 + color_idx)
                beam_end_x = beam_start_x + math.cos(beam_angle) * beam_length
                beam_end_y = beam_start_y + math.sin(beam_angle) * beam_length
                
                beam_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(beam_surf, (*color, 200), 
                               (int(beam_start_x), int(beam_start_y)),
                               (int(beam_end_x), int(beam_end_y)), 3)
                s.blit(beam_surf, (0, 0))
        
        # 白光粒子汇聚到棱镜
        for i in range(10):
            particle_progress = ((t * 2 + i * 0.2) % 1)
            particle_angle = t + i * 0.6
            particle_dist = 50 - particle_progress * 30
            particle_x = 60 + math.cos(particle_angle) * particle_dist
            particle_y = 50 + math.sin(particle_angle) * particle_dist
            particle_alpha = int(220 * (1 - particle_progress))
            pygame.draw.circle(s, (255, 255, 255, particle_alpha), (int(particle_x), int(particle_y)), 3)
        
        return s
    
    elif model_style == "necro_ex":
        # 死灵骑士 - 骷髅马，亡魂召唤
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 骑士头盔
        helmet_rect = pygame.Rect(45, 25, 30, 25)
        pygame.draw.rect(s, (100, 100, 100), helmet_rect)
        pygame.draw.rect(s, (150, 150, 150), helmet_rect, 2)
        
        # 幽绿眼睛
        pygame.draw.circle(s, (0, 255, 100), (52, 35), 4)
        pygame.draw.circle(s, (0, 255, 100), (68, 35), 4)
        
        # 骷髅马头（下方）
        horse_points = [(60, 55), (50, 65), (45, 75), (55, 80), (65, 80), (75, 75), (70, 65)]
        pygame.draw.polygon(s, (200, 200, 200), horse_points)
        pygame.draw.polygon(s, (255, 255, 255), horse_points, 2)
        
        # 马眼（幽火）
        pygame.draw.circle(s, (100, 255, 100), (54, 68), 3)
        
        # 召唤的亡魂（环绕）
        for i in range(12):
            soul_angle = t * 2 + i * math.pi / 6
            soul_dist = 35 + 10 * math.sin(t * 2.5 + i)
            soul_x = 60 + math.cos(soul_angle) * soul_dist
            soul_y = 55 + math.sin(soul_angle) * soul_dist
            
            # 骷髅头轮廓
            skull_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(skull_surf, (100, 255, 100, 200), (int(soul_x), int(soul_y)), 5)
            pygame.draw.circle(skull_surf, (100, 255, 100, 180), (int(soul_x - 2), int(soul_y - 1)), 1)
            pygame.draw.circle(skull_surf, (100, 255, 100, 180), (int(soul_x + 2), int(soul_y - 1)), 1)
            s.blit(skull_surf, (0, 0))
        
        # 死灵能量波
        for ring in range(3):
            wave_radius = (t * 55 + ring * 25) % 75
            wave_alpha = int(200 * (1 - wave_radius / 75))
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (100, 255, 100, wave_alpha), (60, 55), int(wave_radius), 2)
            s.blit(wave_surf, (0, 0))
        
        return s

    # ========== 第二批16个新专属涂装外形 ==========
    elif model_style == "striker_ex2":
        # 龙卷风暴 - 螺旋气流，风刃切割
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.2 + 1
        
        # 中心风眼
        pygame.draw.circle(s, (100, 255, 100), (60, 50), int(10 * pulse))
        
        # 螺旋气流（3层）
        for layer in range(3):
            spiral_radius = 20 + layer * 15
            for i in range(12):
                angle = (t * 4 + i * math.pi / 6 + layer) % (2 * math.pi)
                x = 60 + math.cos(angle) * spiral_radius
                y = 50 + math.sin(angle) * spiral_radius
                # 风刃形状
                blade_points = [
                    (x, y),
                    (x + math.cos(angle + 0.5) * 8, y + math.sin(angle + 0.5) * 8),
                    (x + math.cos(angle - 0.5) * 8, y + math.sin(angle - 0.5) * 8)
                ]
                pygame.draw.polygon(s, (150, 255, 150, 200 - layer * 50), [(int(p[0]), int(p[1])) for p in blade_points])
        
        return s
    
    elif model_style == "phantom_ex2":
        # 时间裂缝 - 时钟齿轮，时光倒流
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心时钟表盘
        pygame.draw.circle(s, (255, 215, 0), (60, 50), 20)
        pygame.draw.circle(s, (255, 240, 150), (60, 50), 20, 3)
        
        # 12个刻度
        for i in range(12):
            angle = i * math.pi / 6 - math.pi / 2
            x1 = 60 + math.cos(angle) * 16
            y1 = 50 + math.sin(angle) * 16
            x2 = 60 + math.cos(angle) * 20
            y2 = 50 + math.sin(angle) * 20
            pygame.draw.line(s, (200, 150, 0), (int(x1), int(y1)), (int(x2), int(y2)), 2)
        
        # 时针（逆时针旋转）
        hour_angle = -t * 0.5
        minute_angle = -t * 6
        pygame.draw.line(s, (150, 100, 0), (60, 50), 
                        (int(60 + math.cos(hour_angle) * 12), int(50 + math.sin(hour_angle) * 12)), 3)
        pygame.draw.line(s, (180, 130, 0), (60, 50),
                        (int(60 + math.cos(minute_angle) * 18), int(50 + math.sin(minute_angle) * 18)), 2)
        
        # 沙漏沙粒
        for i in range(15):
            sand_y = 30 + (t * 50 + i * 5) % 40
            sand_x = 55 + (i % 3) * 5
            pygame.draw.circle(s, (255, 230, 100), (sand_x, int(sand_y)), 2)
        
        return s
    
    elif model_style == "titan_ex2":
        # 熔岩巨兽 - 岩浆裂纹，火山喷发
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.2 + 1
        
        # 巨兽身躯（岩石质感）
        body_rect = pygame.Rect(30, 20, 60, 60)
        pygame.draw.rect(s, (100, 50, 0), body_rect)
        pygame.draw.rect(s, (150, 80, 0), body_rect, 4)
        
        # 岩浆裂纹（发光）
        crack_lines = [
            [(40, 30), (50, 50), (45, 70)],
            [(70, 35), (60, 55), (65, 75)],
            [(50, 25), (55, 45), (60, 65)]
        ]
        for crack in crack_lines:
            for i in range(len(crack) - 1):
                pygame.draw.line(s, (255, 100, 0), crack[i], crack[i+1], 3)
                # 发光效果
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(glow_surf, (255, 150, 0, 180), crack[i], crack[i+1], 6)
                s.blit(glow_surf, (0, 0))
        
        # 火山喷发粒子
        for i in range(10):
            particle_angle = t * 3 + i * 0.6
            particle_dist = 15 + (t * 30 + i * 5) % 30
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 - particle_dist * 0.5
            pygame.draw.circle(s, (255, 120, 20), (int(px), int(py)), 4)
        
        return s
    
    elif model_style == "thunderbird_ex2":
        # 凤凰涅槃 - 火焰羽毛，浴火重生
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 凤凰头部
        pygame.draw.circle(s, (255, 50, 50), (60, 40), 12)
        pygame.draw.polygon(s, (255, 100, 0), [(60, 30), (55, 20), (65, 20)])  # 凤冠
        
        # 凤凰身体
        body_points = [(60, 52), (50, 65), (45, 75), (55, 80), (60, 85), (65, 80), (75, 75), (70, 65)]
        pygame.draw.polygon(s, (255, 80, 80), body_points)
        
        # 火焰翅膀（左右对称）
        for side in [-1, 1]:
            wing_base_x = 60 + side * 10
            for feather in range(5):
                feather_angle = side * (math.pi / 3 + feather * 0.3) + math.sin(t * 3 + feather) * 0.2
                feather_length = 25 + feather * 3
                fx = wing_base_x + math.cos(feather_angle) * feather_length
                fy = 55 + math.sin(feather_angle) * feather_length * 0.6
                # 羽毛（渐变火焰色）
                for seg in range(3):
                    seg_prog = seg / 3
                    color_r = 255
                    color_g = int(150 - seg_prog * 100)
                    sx = wing_base_x + math.cos(feather_angle) * feather_length * seg_prog
                    sy = 55 + math.sin(feather_angle) * feather_length * 0.6 * seg_prog
                    ex = wing_base_x + math.cos(feather_angle) * feather_length * (seg_prog + 0.33)
                    ey = 55 + math.sin(feather_angle) * feather_length * 0.6 * (seg_prog + 0.33)
                    pygame.draw.line(s, (color_r, color_g, 0), (int(sx), int(sy)), (int(ex), int(ey)), 4)
        
        # 涅槃光环
        for ring in range(3):
            ring_radius = 25 + ring * 12 + int(8 * pulse)
            ring_alpha = int(200 - ring * 60)
            ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (255, 100, 0, ring_alpha), (60, 50), ring_radius, 2)
            s.blit(ring_surf, (0, 0))
        
        return s
    
    elif model_style == "viper_ex2":
        # 深海巨鲸 - 鲸鱼形态，水波扩散
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 鲸鱼身体（流线型）
        whale_body = [(30, 50), (40, 40), (60, 35), (80, 40), (90, 50), (85, 60), (60, 65), (35, 60)]
        pygame.draw.polygon(s, (0, 100, 200), whale_body)
        pygame.draw.polygon(s, (0, 150, 255), whale_body, 3)
        
        # 鲸鱼眼睛
        pygame.draw.circle(s, (255, 255, 255), (70, 45), 4)
        pygame.draw.circle(s, (0, 0, 0), (71, 45), 2)
        
        # 锯齿背鳍
        for i in range(5):
            fin_x = 45 + i * 10
            fin_points = [(fin_x, 35), (fin_x - 3, 25), (fin_x + 3, 25)]
            pygame.draw.polygon(s, (0, 120, 220), fin_points)
        
        # 尾鳍（摆动）
        tail_swing = math.sin(t * 4) * 10
        tail_points = [(90, 50), (100 + tail_swing, 40), (105 + tail_swing, 50), (100 + tail_swing, 60)]
        pygame.draw.polygon(s, (0, 130, 230), tail_points)
        
        # 水波纹
        for ring in range(4):
            wave_radius = (t * 40 + ring * 20) % 80
            wave_alpha = int(180 * (1 - wave_radius / 80))
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (100, 200, 255, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surf, (0, 0))
        
        # 气泡上浮
        for i in range(10):
            bubble_y = 80 - (t * 40 + i * 8) % 60
            bubble_x = 50 + i * 3
            pygame.draw.circle(s, (150, 220, 255), (bubble_x, int(bubble_y)), 3)
        
        return s
    
    elif model_style == "specter_ex2":
        # 暗影刺客 - 双刀交叉，分身闪烁
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 刺客身影（模糊轮廓）
        for layer in range(3):
            offset = layer * 5
            alpha = 150 - layer * 40
            shadow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 头部
            pygame.draw.circle(shadow_surf, (50, 50, 100, alpha), (60 + offset, 35), 8)
            # 身体
            body_points = [(60 + offset, 43), (55 + offset, 60), (50 + offset, 75), (60 + offset, 70), (70 + offset, 75), (65 + offset, 60)]
            pygame.draw.polygon(shadow_surf, (50, 50, 100, alpha), body_points)
            s.blit(shadow_surf, (0, 0))
        
        # 双刀交叉
        blade_angle1 = math.pi / 4 + math.sin(t * 3) * 0.3
        blade_angle2 = -math.pi / 4 - math.sin(t * 3) * 0.3
        for blade_angle in [blade_angle1, blade_angle2]:
            blade_start_x = 60
            blade_start_y = 50
            blade_end_x = 60 + math.cos(blade_angle) * 35
            blade_end_y = 50 + math.sin(blade_angle) * 35
            pygame.draw.line(s, (100, 100, 150), (blade_start_x, blade_start_y), 
                           (int(blade_end_x), int(blade_end_y)), 4)
            pygame.draw.line(s, (150, 150, 200), (blade_start_x, blade_start_y),
                           (int(blade_end_x), int(blade_end_y)), 2)
        
        # 手里剑飞旋
        for i in range(4):
            shuriken_angle = t * 5 + i * math.pi / 2
            shuriken_dist = 30 + 10 * math.sin(t * 2 + i)
            sx = 60 + math.cos(shuriken_angle) * shuriken_dist
            sy = 50 + math.sin(shuriken_angle) * shuriken_dist
            # 四角星形
            star_points = []
            for j in range(8):
                star_angle = shuriken_angle + j * math.pi / 4
                star_radius = 5 if j % 2 == 0 else 3
                star_points.append((int(sx + math.cos(star_angle) * star_radius),
                                  int(sy + math.sin(star_angle) * star_radius)))
            pygame.draw.polygon(s, (80, 80, 130), star_points)
        
        return s
    
    elif model_style == "aurora_ex2":
        # 冰霜精灵 - 冰晶翅膀，雪花飘落
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 精灵身体（冰晶人形）
        pygame.draw.circle(s, (180, 230, 255), (60, 40), 10)  # 头
        body_points = [(60, 50), (55, 65), (53, 75), (60, 80), (67, 75), (65, 65)]
        pygame.draw.polygon(s, (150, 220, 255), body_points)
        
        # 冰晶翅膀（6片）
        for wing_idx in range(6):
            wing_angle = wing_idx * math.pi / 3 + t * 0.5
            wing_length = 25 + 8 * math.sin(t * 2 + wing_idx)
            # 翅膀主干
            wx = 60 + math.cos(wing_angle) * wing_length
            wy = 50 + math.sin(wing_angle) * wing_length
            pygame.draw.line(s, (200, 240, 255), (60, 50), (int(wx), int(wy)), 3)
            # 冰晶分支
            for branch in range(3):
                branch_angle = wing_angle + (branch - 1) * 0.4
                branch_dist = wing_length * 0.6
                bx = 60 + math.cos(branch_angle) * branch_dist
                by = 50 + math.sin(branch_angle) * branch_dist
                pygame.draw.line(s, (180, 230, 255), (int(wx), int(wy)), (int(bx), int(by)), 2)
        
        # 雪花飘落
        for i in range(20):
            snow_y = (t * 40 + i * 10) % 120
            snow_x = 30 + (i * 4) % 60 + math.sin(t * 2 + i) * 10
            # 六角雪花
            for j in range(6):
                sf_angle = j * math.pi / 3
                sf_x1 = snow_x + math.cos(sf_angle) * 3
                sf_y1 = snow_y + math.sin(sf_angle) * 3
                pygame.draw.line(s, (255, 255, 255), (int(snow_x), int(snow_y)), 
                               (int(sf_x1), int(sf_y1)), 1)
        
        # 冰封光环
        for ring in range(3):
            ice_radius = 20 + ring * 12
            ice_alpha = int(180 - ring * 50)
            ice_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ice_surf, (180, 230, 255, ice_alpha), (60, 50), ice_radius, 2)
            s.blit(ice_surf, (0, 0))
        
        return s
    
    elif model_style == "crimson_ex2":
        # 爆炸之星（超新星） - 星体爆发，能量释放
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 3) * 0.25 + 1
        
        # 超新星核心（极亮）
        for layer in range(6, 0, -1):
            core_radius = int(18 * pulse * (layer / 6))
            core_alpha = int(255 * (layer / 6))
            core_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(core_surf, (255, 255, 200, core_alpha), (60, 50), core_radius)
            s.blit(core_surf, (0, 0))
        
        # 爆炸冲击波（多层扩散）
        for wave in range(5):
            wave_radius = (t * 80 + wave * 20) % 100
            wave_alpha = int(200 * (1 - wave_radius / 100))
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (255, 255, 150, wave_alpha), (60, 50), int(wave_radius), 4)
            s.blit(wave_surf, (0, 0))
        
        # 星云碎片飞溅（24个方向）
        for i in range(24):
            fragment_angle = i * math.pi / 12
            fragment_dist = 20 + (t * 60 + i * 5) % 50
            fx = 60 + math.cos(fragment_angle) * fragment_dist
            fy = 50 + math.sin(fragment_angle) * fragment_dist
            fragment_size = 6 - int(fragment_dist / 15)
            if fragment_size > 1:
                pygame.draw.circle(s, (255, 255, 100), (int(fx), int(fy)), fragment_size)
        
        # 能量射线
        for ray in range(12):
            ray_angle = ray * math.pi / 6 + t
            ray_length = 30 + 15 * math.sin(t * 2 + ray)
            rx = 60 + math.cos(ray_angle) * ray_length
            ry = 50 + math.sin(ray_angle) * ray_length
            ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(ray_surf, (255, 255, 200, 200), (60, 50), (int(rx), int(ry)), 3)
            s.blit(ray_surf, (0, 0))
        
        return s
    
    elif model_style == "stalker_ex2":
        # 机械蜘蛛 - 8条机械腿，纳米虫群
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 蜘蛛主体（机械球体）
        pygame.draw.circle(s, (150, 150, 150), (60, 50), int(15 * pulse))
        pygame.draw.circle(s, (200, 200, 200), (60, 50), int(15 * pulse), 2)
        
        # 电子复眼（多个镜头）
        for eye_idx in range(6):
            eye_angle = eye_idx * math.pi / 3
            eye_x = 60 + math.cos(eye_angle) * 8
            eye_y = 50 + math.sin(eye_angle) * 8
            eye_brightness = int(155 + 100 * math.sin(t * 8 + eye_idx))
            pygame.draw.circle(s, (eye_brightness, 0, 0), (int(eye_x), int(eye_y)), 3)
        
        # 8条机械腿
        for leg_idx in range(8):
            leg_angle = leg_idx * math.pi / 4
            # 腿部关节动画
            leg_bend = math.sin(t * 4 + leg_idx) * 0.3
            
            # 第一节
            joint1_x = 60 + math.cos(leg_angle) * 18
            joint1_y = 50 + math.sin(leg_angle) * 18
            pygame.draw.line(s, (180, 180, 180), (60, 50), (int(joint1_x), int(joint1_y)), 4)
            
            # 第二节
            joint2_angle = leg_angle + leg_bend
            joint2_x = joint1_x + math.cos(joint2_angle) * 15
            joint2_y = joint1_y + math.sin(joint2_angle) * 15
            pygame.draw.line(s, (160, 160, 160), (int(joint1_x), int(joint1_y)), 
                           (int(joint2_x), int(joint2_y)), 3)
            
            # 第三节（末端）
            joint3_angle = joint2_angle - leg_bend * 0.5
            joint3_x = joint2_x + math.cos(joint3_angle) * 10
            joint3_y = joint2_y + math.sin(joint3_angle) * 10
            pygame.draw.line(s, (140, 140, 140), (int(joint2_x), int(joint2_y)),
                           (int(joint3_x), int(joint3_y)), 2)
        
        # 纳米虫群（小型飞行机器人）
        for nano_idx in range(20):
            nano_angle = t * 3 + nano_idx * 0.3
            nano_dist = 30 + 15 * math.sin(t * 2 + nano_idx)
            nx = 60 + math.cos(nano_angle) * nano_dist
            ny = 50 + math.sin(nano_angle) * nano_dist
            pygame.draw.rect(s, (220, 220, 220), (int(nx)-2, int(ny)-2, 4, 4))
        
        return s
    
    elif model_style == "gaia_ex2":
        # 樱花树灵 - 樱花树形态，花瓣飘落
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 树干
        trunk_rect = pygame.Rect(52, 40, 16, 45)
        pygame.draw.rect(s, (120, 80, 60), trunk_rect)
        pygame.draw.rect(s, (150, 100, 80), trunk_rect, 2)
        
        # 树枝（摇曳）
        for branch_idx in range(5):
            branch_angle = (branch_idx - 2) * 0.4 + math.sin(t * 2 + branch_idx) * 0.2
            branch_length = 20 + branch_idx * 3
            bx = 60 + math.cos(branch_angle) * branch_length
            by = 45 + branch_idx * 5
            pygame.draw.line(s, (140, 90, 70), (60, int(by)), (int(bx), int(by)), 3)
            
            # 樱花簇
            for flower in range(3):
                flower_angle = branch_angle + (flower - 1) * 0.3
                flower_dist = branch_length * 0.7
                fx = 60 + math.cos(flower_angle) * flower_dist
                fy = by
                pygame.draw.circle(s, (255, 180, 200), (int(fx), int(fy)), 5)
        
        # 樱花花瓣飘落（大量）
        for petal_idx in range(30):
            petal_y = (t * 30 + petal_idx * 8) % 120
            petal_x = 40 + (petal_idx * 3) % 40 + math.sin(t * 3 + petal_idx) * 15
            petal_rotation = t * 2 + petal_idx
            # 花瓣形状（椭圆）
            petal_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            petal_points = []
            for i in range(8):
                pa = i * math.pi / 4 + petal_rotation
                px = petal_x + math.cos(pa) * (4 if i % 2 == 0 else 2)
                py = petal_y + math.sin(pa) * (6 if i % 2 == 0 else 3)
                petal_points.append((int(px), int(py)))
            pygame.draw.polygon(petal_surf, (255, 150, 180, 220), petal_points)
            s.blit(petal_surf, (0, 0))
        
        # 春意光环
        for ring in range(3):
            spring_radius = 25 + ring * 12
            spring_alpha = int(180 - ring * 50)
            spring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(spring_surf, (255, 200, 220, spring_alpha), (60, 60), spring_radius, 2)
            s.blit(spring_surf, (0, 0))
        
        return s
    
    elif model_style == "weaver_ex2":
        # DNA螺旋 - 双螺旋结构，碱基对连接
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 双螺旋主链
        helix_points_1 = []
        helix_points_2 = []
        for i in range(20):
            y = 20 + i * 4
            angle1 = t * 2 + i * 0.4
            angle2 = angle1 + math.pi
            x1 = 60 + math.cos(angle1) * 20
            x2 = 60 + math.cos(angle2) * 20
            helix_points_1.append((int(x1), y))
            helix_points_2.append((int(x2), y))
        
        # 绘制螺旋线
        pygame.draw.lines(s, (0, 255, 150), False, helix_points_1, 3)
        pygame.draw.lines(s, (100, 255, 200), False, helix_points_2, 3)
        
        # 碱基对连接（横杠）
        for i in range(0, len(helix_points_1), 2):
            # 闪烁效果
            if (int(t * 10) + i) % 4 < 3:
                pygame.draw.line(s, (50, 255, 180), helix_points_1[i], helix_points_2[i], 2)
                # 碱基节点
                pygame.draw.circle(s, (0, 255, 150), helix_points_1[i], 4)
                pygame.draw.circle(s, (100, 255, 200), helix_points_2[i], 4)
        
        # 基因序列流动（发光粒子）
        for particle_idx in range(15):
            particle_progress = (t * 2 + particle_idx * 0.3) % 1
            particle_i = int(particle_progress * (len(helix_points_1) - 1))
            if particle_i < len(helix_points_1):
                px, py = helix_points_1[particle_i]
                particle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, (200, 255, 200, 220), (px, py), 6)
                s.blit(particle_surf, (0, 0))
        
        return s
    
    elif model_style == "solar_ex2":
        # 雷电之神（宙斯） - 雷神锤，闪电链条
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 雷神锤头（巨大方锤）
        hammer_head = pygame.Rect(35, 30, 50, 30)
        pygame.draw.rect(s, (150, 150, 150), hammer_head)
        pygame.draw.rect(s, (200, 200, 200), hammer_head, 3)
        # 锤面雕刻（闪电纹）
        pygame.draw.line(s, (100, 100, 255), (40, 35), (50, 55), 2)
        pygame.draw.line(s, (100, 100, 255), (50, 55), (45, 55), 2)
        pygame.draw.line(s, (100, 100, 255), (70, 35), (75, 55), 2)
        pygame.draw.line(s, (100, 100, 255), (75, 55), (80, 55), 2)
        
        # 锤柄
        pygame.draw.rect(s, (100, 80, 60), (55, 60, 10, 30))
        
        # 闪电链条缠绕（4条）
        for chain_idx in range(4):
            chain_angle = chain_idx * math.pi / 2 + t * 2
            chain_dist = 30 + 10 * math.sin(t * 3 + chain_idx)
            cx = 60 + math.cos(chain_angle) * chain_dist
            cy = 45 + math.sin(chain_angle) * chain_dist
            # 闪电链条
            pygame.draw.line(s, (200, 200, 255), (60, 45), (int(cx), int(cy)), 3)
            # 链条末端电球
            ball_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ball_surf, (220, 220, 255, 220), (int(cx), int(cy)), 6)
            s.blit(ball_surf, (0, 0))
        
        # 雷云环绕
        for cloud_idx in range(8):
            cloud_angle = t + cloud_idx * math.pi / 4
            cloud_dist = 35 + 8 * math.sin(t * 2 + cloud_idx)
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 45 + math.sin(cloud_angle) * cloud_dist
            pygame.draw.circle(s, (100, 100, 150), (int(cloud_x), int(cloud_y)), 5)
        
        # 天降神雷（随机闪电）
        if int(t * 10) % 3 == 0:
            for bolt in range(3):
                bolt_x = 40 + bolt * 20
                bolt_points = [(bolt_x, 10)]
                for seg in range(5):
                    bolt_y = 10 + seg * 15
                    bolt_x += random.choice([-5, 0, 5])
                    bolt_points.append((bolt_x, bolt_y))
                pygame.draw.lines(s, (255, 255, 255), False, bolt_points, 2)
        
        return s
    
    elif model_style == "arbiter_ex2":
        # 正义天秤 - 天秤平衡，律法之眼
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 天秤横杆
        pygame.draw.line(s, (255, 215, 0), (30, 40), (90, 40), 4)
        pygame.draw.circle(s, (255, 240, 100), (60, 40), 8)
        
        # 天秤支撑柱
        pygame.draw.line(s, (255, 215, 0), (60, 40), (60, 60), 4)
        
        # 左右秤盘（轻微倾斜表示审判）
        tilt = math.sin(t * 1.5) * 5
        # 左秤盘
        left_pan_y = 55 + tilt
        pygame.draw.line(s, (255, 230, 50), (30, 40), (35, int(left_pan_y)), 2)
        pygame.draw.ellipse(s, (255, 240, 100), (25, int(left_pan_y), 20, 8))
        # 右秤盘
        right_pan_y = 55 - tilt
        pygame.draw.line(s, (255, 230, 50), (90, 40), (85, int(right_pan_y)), 2)
        pygame.draw.ellipse(s, (255, 240, 100), (75, int(right_pan_y), 20, 8))
        
        # 律法之眼（悬浮在上方）
        eye_y = 25 + math.sin(t * 2) * 3
        pygame.draw.ellipse(s, (255, 215, 0), (50, int(eye_y), 20, 12))
        pygame.draw.circle(s, (255, 240, 100), (60, int(eye_y + 6)), 6)
        pygame.draw.circle(s, (100, 80, 0), (60, int(eye_y + 6)), 3)
        # 眼睛光芒
        eye_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(eye_surf, (255, 240, 100, 180), (60, int(eye_y + 6)), int(10 * pulse))
        s.blit(eye_surf, (0, 0))
        
        # 正义光柱（从眼睛向下）
        for beam in range(3):
            beam_x = 58 + beam
            pygame.draw.line(s, (255, 240, 100, 150), (beam_x, int(eye_y + 12)), (beam_x, 120), 2)
        
        # 审判之剑（悬浮在天秤上方）
        sword_x = 60 + math.sin(t * 2) * 10
        sword_points = [(sword_x, 15), (sword_x - 3, 25), (sword_x + 3, 25)]
        pygame.draw.polygon(s, (255, 215, 0), [(int(p[0]), p[1]) for p in sword_points])
        pygame.draw.line(s, (255, 230, 50), (int(sword_x), 25), (int(sword_x), 35), 3)
        
        return s
    
    elif model_style == "eclipse_ex2":
        # 星系吞噬者 - 黑洞巨口，引力波扭曲
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.25 + 1
        
        # 黑洞核心（绝对黑暗）
        pygame.draw.circle(s, (0, 0, 0), (60, 50), 22)
        
        # 事件视界（紫色边缘）
        for layer in range(4):
            horizon_radius = 22 + layer * 4
            horizon_alpha = int(220 - layer * 50)
            horizon_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(horizon_surf, (100, 0, 150, horizon_alpha), (60, 50), horizon_radius, 3)
            s.blit(horizon_surf, (0, 0))
        
        # 吞噬的星系（螺旋吸入）
        for arm in range(4):
            arm_offset = arm * math.pi / 2
            for star_idx in range(30):
                spiral_progress = star_idx / 30
                spiral_angle = t * 2 + spiral_progress * math.pi * 6 + arm_offset
                spiral_dist = 60 - spiral_progress * 40
                if spiral_dist > 22:  # 不进入事件视界
                    sx = 60 + math.cos(spiral_angle) * spiral_dist
                    sy = 50 + math.sin(spiral_angle) * spiral_dist
                    star_size = int(4 * (1 - spiral_progress))
                    if star_size > 0:
                        star_brightness = int(255 * (1 - spiral_progress * 0.7))
                        pygame.draw.circle(s, (star_brightness, star_brightness // 2, star_brightness), 
                                         (int(sx), int(sy)), star_size)
        
        # 引力波扭曲（同心圆波纹）
        for wave in range(6):
            wave_radius = (t * 60 + wave * 20) % 120
            if wave_radius > 25:  # 从事件视界外开始
                wave_alpha = int(150 * (1 - (wave_radius - 25) / 95))
                wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                # 扭曲效果（椭圆变形）
                distortion = 1 + 0.3 * math.sin(t * 3 + wave)
                pygame.draw.ellipse(wave_surf, (150, 50, 200, wave_alpha),
                                  (60 - wave_radius, int(50 - wave_radius * distortion),
                                   wave_radius * 2, int(wave_radius * 2 * distortion)), 2)
                s.blit(wave_surf, (0, 0))
        
        # 宇宙坍缩粒子
        for particle in range(25):
            particle_progress = ((t * 3 + particle * 0.2) % 1)
            particle_angle = particle * 0.8
            particle_dist = 60 - particle_progress * 38
            if particle_dist > 22:
                px = 60 + math.cos(particle_angle) * particle_dist
                py = 50 + math.sin(particle_angle) * particle_dist
                particle_alpha = int(220 * (1 - particle_progress))
                pygame.draw.circle(s, (120, 20, 180, particle_alpha), (int(px), int(py)), 3)
        
        return s
    
    elif model_style == "prism_ex2":
        # 万花筒 - 对称图案，镜像反射
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心万花筒核心
        pygame.draw.circle(s, (255, 100, 255), (60, 50), int(12 * pulse))
        
        # 6重对称图案
        for symmetry in range(6):
            base_angle = symmetry * math.pi / 3 + t * 0.5
            
            # 每个对称区域绘制复杂图案
            for pattern in range(5):
                pattern_dist = 15 + pattern * 8
                pattern_angle = base_angle + pattern * 0.3
                
                # 彩色图案块
                hue = (t * 50 + symmetry * 60 + pattern * 30) % 360
                color_r = int(127 + 127 * math.sin(math.radians(hue)))
                color_g = int(127 + 127 * math.sin(math.radians(hue + 120)))
                color_b = int(127 + 127 * math.sin(math.radians(hue + 240)))
                
                # 主图形
                px = 60 + math.cos(pattern_angle) * pattern_dist
                py = 50 + math.sin(pattern_angle) * pattern_dist
                
                # 绘制小多边形
                poly_points = []
                for i in range(6):
                    poly_angle = pattern_angle + i * math.pi / 3
                    poly_radius = 5 + 2 * math.sin(t * 3 + pattern)
                    poly_x = px + math.cos(poly_angle) * poly_radius
                    poly_y = py + math.sin(poly_angle) * poly_radius
                    poly_points.append((int(poly_x), int(poly_y)))
                pygame.draw.polygon(s, (color_r, color_g, color_b), poly_points)
                
                # 镜像反射（另一侧）
                mirror_angle = base_angle - pattern * 0.3
                mirror_px = 60 + math.cos(mirror_angle) * pattern_dist
                mirror_py = 50 + math.sin(mirror_angle) * pattern_dist
                mirror_poly_points = []
                for i in range(6):
                    mirror_poly_angle = mirror_angle + i * math.pi / 3
                    mirror_poly_radius = 5 + 2 * math.sin(t * 3 + pattern)
                    mirror_poly_x = mirror_px + math.cos(mirror_poly_angle) * mirror_poly_radius
                    mirror_poly_y = mirror_py + math.sin(mirror_poly_angle) * mirror_poly_radius
                    mirror_poly_points.append((int(mirror_poly_x), int(mirror_poly_y)))
                pygame.draw.polygon(s, (color_r, color_g, color_b), mirror_poly_points)
        
        # 迷幻光线
        for ray in range(12):
            ray_angle = ray * math.pi / 6 + t * 2
            ray_length = 25 + 15 * math.sin(t * 3 + ray)
            rx = 60 + math.cos(ray_angle) * ray_length
            ry = 50 + math.sin(ray_angle) * ray_length
            ray_hue = (t * 100 + ray * 30) % 360
            ray_r = int(127 + 127 * math.sin(math.radians(ray_hue)))
            ray_g = int(127 + 127 * math.sin(math.radians(ray_hue + 120)))
            ray_b = int(127 + 127 * math.sin(math.radians(ray_hue + 240)))
            ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(ray_surf, (ray_r, ray_g, ray_b, 180), (60, 50), (int(rx), int(ry)), 2)
            s.blit(ray_surf, (0, 0))
        
        return s
    
    elif model_style == "necro_ex2":
        # 虚无教主 - 万物归墟，存在湮灭
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.2 + 1
        
        # 虚无核心（纯黑但带紫色边缘）
        pygame.draw.circle(s, (0, 0, 0), (60, 50), int(20 * pulse))
        for layer in range(3):
            void_radius = int(20 * pulse) + layer * 5
            void_alpha = int(150 - layer * 40)
            void_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(void_surf, (50, 0, 50, void_alpha), (60, 50), void_radius, 2)
            s.blit(void_surf, (0, 0))
        
        # 存在消散（粒子被吸入虚无）
        for particle in range(30):
            particle_progress = ((t * 2 + particle * 0.15) % 1)
            particle_angle = particle * 0.7
            particle_dist = 60 - particle_progress * 40
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            # 粒子逐渐消失
            particle_alpha = int(220 * (1 - particle_progress))
            particle_size = int(5 * (1 - particle_progress * 0.7))
            if particle_size > 0 and particle_alpha > 0:
                particle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, (50, 50, 50, particle_alpha), 
                                 (int(px), int(py)), particle_size)
                s.blit(particle_surf, (0, 0))
        
        # 终焉之书（漂浮的黑色书页）
        for page in range(4):
            page_angle = t + page * math.pi / 2
            page_dist = 35 + 10 * math.sin(t * 2 + page)
            page_x = 60 + math.cos(page_angle) * page_dist
            page_y = 50 + math.sin(page_angle) * page_dist
            # 书页（矩形）
            page_rotation = math.sin(t * 3 + page) * 0.3
            page_points = []
            for corner in range(4):
                corner_angle = page_angle + corner * math.pi / 2 + page_rotation
                corner_dist = 8
                cx = page_x + math.cos(corner_angle) * corner_dist
                cy = page_y + math.sin(corner_angle) * corner_dist * 0.7
                page_points.append((int(cx), int(cy)))
            pygame.draw.polygon(s, (20, 20, 20), page_points)
            pygame.draw.polygon(s, (50, 50, 50), page_points, 1)
            # 书页上的符文
            pygame.draw.line(s, (80, 80, 80), (int(page_x - 5), int(page_y)), 
                           (int(page_x + 5), int(page_y)), 1)
        
        # 湮灭波动
        for wave in range(4):
            wave_radius = (t * 50 + wave * 25) % 100
            wave_alpha = int(180 * (1 - wave_radius / 100))
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(wave_surf, (20, 20, 20, wave_alpha), (60, 50), int(wave_radius), 2)
            s.blit(wave_surf, (0, 0))
        
        return s
    
    # ========== 第三批16个超级创意涂装（更丰富特效）==========
    elif model_style == "striker_ex3":
        # 次元裂缝 - 空间碎裂，现实崩坏
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.2 + 1
        
        # 主体裂缝（闪电形状但更扭曲）
        crack_center = (60, 50)
        crack_segments = []
        for i in range(20):
            angle = (i / 20) * math.pi * 2 + t * 0.5
            dist = 15 + 25 * (i / 20) + math.sin(t * 3 + i) * 8
            x = crack_center[0] + math.cos(angle) * dist
            y = crack_center[1] + math.sin(angle) * dist
            crack_segments.append((int(x), int(y)))
        
        # 绘制扭曲裂缝
        for i in range(len(crack_segments) - 1):
            # 多层裂缝效果
            for layer in range(3):
                offset = layer * 2
                color_intensity = 255 - layer * 80
                crack_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(crack_surf, (color_intensity, 0, color_intensity, 220 - layer * 50),
                               (crack_segments[i][0] + offset, crack_segments[i][1]),
                               (crack_segments[i+1][0] + offset, crack_segments[i+1][1]), 4 - layer)
                s.blit(crack_surf, (0, 0))
        
        # 空间碎片（漂浮的碎裂空间）
        for frag in range(25):
            frag_angle = t * 2 + frag * 0.4
            frag_dist = 20 + 30 * ((frag % 5) / 5)
            frag_x = 60 + math.cos(frag_angle) * frag_dist
            frag_y = 50 + math.sin(frag_angle) * frag_dist
            frag_rotation = t * 3 + frag
            
            # 碎片形状（不规则四边形）
            frag_points = []
            for i in range(4):
                fp_angle = frag_rotation + i * math.pi / 2
                fp_dist = 5 + random.randint(-2, 2)
                frag_points.append((int(frag_x + math.cos(fp_angle) * fp_dist),
                                  int(frag_y + math.sin(fp_angle) * fp_dist)))
            
            frag_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(frag_surf, (200, 0, 255, 180), frag_points)
            pygame.draw.polygon(frag_surf, (255, 100, 255, 220), frag_points, 2)
            s.blit(frag_surf, (0, 0))
        
        # 维度扭曲波纹
        for wave in range(5):
            wave_radius = (t * 70 + wave * 20) % 100
            wave_alpha = int(200 * (1 - wave_radius / 100))
            for angle_seg in range(8):
                seg_angle = angle_seg * math.pi / 4
                distortion = math.sin(t * 4 + angle_seg) * 10
                wx = 60 + math.cos(seg_angle) * (wave_radius + distortion)
                wy = 50 + math.sin(seg_angle) * (wave_radius + distortion)
                if angle_seg < 7:
                    next_angle = (angle_seg + 1) * math.pi / 4
                    next_distortion = math.sin(t * 4 + angle_seg + 1) * 10
                    next_wx = 60 + math.cos(next_angle) * (wave_radius + next_distortion)
                    next_wy = 50 + math.sin(next_angle) * (wave_radius + next_distortion)
                    wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(wave_surf, (255, 0, 255, wave_alpha),
                                   (int(wx), int(wy)), (int(next_wx), int(next_wy)), 3)
                    s.blit(wave_surf, (0, 0))
        
        return s
    
    elif model_style == "phantom_ex3":
        # 星云诞生 - 宇宙摇篮，恒星胚胎
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.2 + 1
        
        # 星云气体（大块半透明云团）
        for cloud in range(8):
            cloud_angle = t * 0.5 + cloud * math.pi / 4
            cloud_dist = 25 + 15 * math.sin(t * 2 + cloud)
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 50 + math.sin(cloud_angle) * cloud_dist
            cloud_size = 20 + 10 * math.sin(t * 1.5 + cloud)
            
            # 渐变云团
            for layer in range(5, 0, -1):
                layer_radius = int(cloud_size * (layer / 5))
                layer_alpha = int(100 * (layer / 5))
                cloud_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(cloud_surf, (100, 150, 255, layer_alpha),
                                 (int(cloud_x), int(cloud_y)), layer_radius)
                s.blit(cloud_surf, (0, 0))
        
        # 恒星胚胎（明亮的原恒星）
        proto_stars = []
        for star in range(12):
            star_angle = t * 1.2 + star * 0.5
            star_dist = 15 + 25 * ((star % 3) / 3)
            star_x = 60 + math.cos(star_angle) * star_dist
            star_y = 50 + math.sin(star_angle) * star_dist
            proto_stars.append((star_x, star_y))
            
            # 原恒星核心
            star_brightness = int(200 + 55 * math.sin(t * 5 + star))
            for glow in range(4, 0, -1):
                glow_radius = int(6 * pulse * (glow / 4))
                glow_alpha = int(255 * (glow / 4))
                star_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(star_surf, (star_brightness, star_brightness + 30, 255, glow_alpha),
                                 (int(star_x), int(star_y)), glow_radius)
                s.blit(star_surf, (0, 0))
        
        # 星际尘埃（连接恒星的尘埃流）
        for i in range(len(proto_stars)):
            for j in range(i + 1, len(proto_stars)):
                if random.random() < 0.3:  # 随机连接
                    dust_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    # 尘埃流动
                    for seg in range(5):
                        seg_prog = seg / 5
                        sx = proto_stars[i][0] + (proto_stars[j][0] - proto_stars[i][0]) * seg_prog
                        sy = proto_stars[i][1] + (proto_stars[j][1] - proto_stars[i][1]) * seg_prog
                        # 波动
                        offset_x = math.sin(t * 3 + seg) * 5
                        offset_y = math.cos(t * 3 + seg) * 5
                        if seg < 4:
                            next_prog = (seg + 1) / 5
                            ex = proto_stars[i][0] + (proto_stars[j][0] - proto_stars[i][0]) * next_prog
                            ey = proto_stars[i][1] + (proto_stars[j][1] - proto_stars[i][1]) * next_prog
                            next_offset_x = math.sin(t * 3 + seg + 1) * 5
                            next_offset_y = math.cos(t * 3 + seg + 1) * 5
                            pygame.draw.line(dust_surf, (150, 200, 255, 120),
                                           (int(sx + offset_x), int(sy + offset_y)),
                                           (int(ex + next_offset_x), int(ey + next_offset_y)), 2)
                    s.blit(dust_surf, (0, 0))
        
        # 宇宙射线
        for ray in range(20):
            if (int(t * 10) + ray) % 5 < 2:
                ray_angle = t * 4 + ray * 0.3
                ray_start_dist = 10
                ray_end_dist = 50
                ray_sx = 60 + math.cos(ray_angle) * ray_start_dist
                ray_sy = 50 + math.sin(ray_angle) * ray_start_dist
                ray_ex = 60 + math.cos(ray_angle) * ray_end_dist
                ray_ey = 50 + math.sin(ray_angle) * ray_end_dist
                ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(ray_surf, (255, 255, 255, 200),
                               (int(ray_sx), int(ray_sy)), (int(ray_ex), int(ray_ey)), 1)
                s.blit(ray_surf, (0, 0))
        
        return s
    elif model_style == "titan_ex3":
        # 符文巨像 - 古代守护者
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 巨像主体（巨大石块）
        golem_body = [(60, 20), (80, 35), (85, 60), (70, 80), (50, 80), (35, 60), (40, 35)]
        pygame.draw.polygon(s, (120, 90, 60), golem_body)
        pygame.draw.polygon(s, (150, 120, 80), golem_body, 4)
        
        # 古代符文（发光刻纹）
        runes = [
            # 符文位置和形状
            [(52, 30), (54, 28), (56, 30), (54, 32)],  # 额头符文
            [(48, 45), (50, 43), (52, 45), (50, 47)],  # 左眼符文
            [(68, 45), (70, 43), (72, 45), (70, 47)],  # 右眼符文
            [(55, 60), (60, 58), (65, 60), (60, 62)],  # 胸部符文
        ]
        
        for rune_idx, rune in enumerate(runes):
            rune_brightness = int(200 + 55 * math.sin(t * 4 + rune_idx))
            # 符文本体
            pygame.draw.polygon(s, (rune_brightness, 150, 50), rune)
            # 符文辉光
            for glow_layer in range(3):
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                glow_size = 8 + glow_layer * 4 + int(4 * pulse)
                center_x = sum(p[0] for p in rune) // len(rune)
                center_y = sum(p[1] for p in rune) // len(rune)
                glow_alpha = int(180 - glow_layer * 50)
                pygame.draw.circle(glow_surf, (rune_brightness, 150, 50, glow_alpha),
                                 (center_x, center_y), glow_size)
                s.blit(glow_surf, (0, 0))
        
        # 魔法阵环绕（3层旋转魔法阵）
        for circle in range(3):
            circle_radius = 30 + circle * 12
            circle_rotation = t * (1 + circle * 0.5)
            circle_alpha = int(200 - circle * 50)
            
            # 魔法阵圆环
            magic_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(magic_surf, (200, 150, 100, circle_alpha),
                             (60, 50), circle_radius, 2)
            
            # 魔法阵符号（6个）
            for symbol in range(6):
                symbol_angle = circle_rotation + symbol * math.pi / 3
                symbol_x = 60 + math.cos(symbol_angle) * circle_radius
                symbol_y = 50 + math.sin(symbol_angle) * circle_radius
                # 绘制符号（小三角形）
                symbol_points = []
                for i in range(3):
                    sp_angle = symbol_angle + i * 2 * math.pi / 3
                    sp_x = symbol_x + math.cos(sp_angle) * 4
                    sp_y = symbol_y + math.sin(sp_angle) * 4
                    symbol_points.append((int(sp_x), int(sp_y)))
                pygame.draw.polygon(magic_surf, (220, 180, 120, circle_alpha), symbol_points)
            
            s.blit(magic_surf, (0, 0))
        
        # 守护者能量护盾（六边形护盾）
        shield_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        shield_radius = 40 + int(5 * pulse)
        shield_points = []
        for i in range(6):
            shield_angle = t * 0.5 + i * math.pi / 3
            shield_x = 60 + math.cos(shield_angle) * shield_radius
            shield_y = 50 + math.sin(shield_angle) * shield_radius
            shield_points.append((int(shield_x), int(shield_y)))
        pygame.draw.polygon(shield_surf, (150, 200, 100, 100), shield_points)
        pygame.draw.polygon(shield_surf, (200, 250, 150, 200), shield_points, 3)
        s.blit(shield_surf, (0, 0))
        
        # 能量粒子流动
        for particle in range(20):
            particle_progress = (t * 2 + particle * 0.2) % 1
            particle_angle = particle * 0.3
            particle_dist = 20 + particle_progress * 30
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            particle_alpha = int(220 * (1 - particle_progress))
            pygame.draw.circle(s, (180, 150, 100, particle_alpha), (int(px), int(py)), 3)
        
        return s

    elif model_style == "thunderbird_ex3":
        # 雷霆瓦尔基里 - 战争天使
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 天使头部光环
        halo_radius = 25 + int(5 * pulse)
        halo_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(halo_surf, (255, 255, 200, 220), (60, 30), halo_radius, 3)
        # 光环光芒
        for ray in range(12):
            ray_angle = t * 2 + ray * math.pi / 6
            ray_inner_x = 60 + math.cos(ray_angle) * halo_radius
            ray_inner_y = 30 + math.sin(ray_angle) * halo_radius
            ray_outer_x = 60 + math.cos(ray_angle) * (halo_radius + 8)
            ray_outer_y = 30 + math.sin(ray_angle) * (halo_radius + 8)
            pygame.draw.line(halo_surf, (255, 255, 240, 200),
                           (int(ray_inner_x), int(ray_inner_y)),
                           (int(ray_outer_x), int(ray_outer_y)), 2)
        s.blit(halo_surf, (0, 0))
        
        # 天使身体（人形）
        pygame.draw.circle(s, (255, 255, 220), (60, 35), 8)  # 头
        body_points = [(60, 43), (55, 60), (53, 70), (60, 75), (67, 70), (65, 60)]
        pygame.draw.polygon(s, (255, 255, 240), body_points)
        
        # 雷电翅膀（6片羽翼）
        for wing_pair in range(3):
            wing_y_offset = 45 + wing_pair * 10
            wing_span = 35 - wing_pair * 5
            
            for side in [-1, 1]:
                # 羽翼主干
                wing_base_x = 60
                wing_tip_x = 60 + side * (wing_span + 10 * math.sin(t * 3 + wing_pair))
                wing_tip_y = wing_y_offset + 5 * math.sin(t * 2 + wing_pair)
                
                # 多层羽毛
                for feather in range(5):
                    feather_progress = feather / 5
                    fx = wing_base_x + (wing_tip_x - wing_base_x) * feather_progress
                    fy = wing_y_offset + (wing_tip_y - wing_y_offset) * feather_progress
                    feather_angle = side * (math.pi / 4 + feather * 0.2)
                    feather_length = 12 - feather * 1.5
                    
                    fex = fx + math.cos(feather_angle) * feather_length
                    fey = fy + math.sin(feather_angle) * feather_length
                    
                    # 羽毛带闪电效果
                    feather_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(feather_surf, (255, 255, 220, 230),
                                   (int(fx), int(fy)), (int(fex), int(fey)), 3)
                    # 闪电纹理
                    if (int(t * 10) + feather) % 3 == 0:
                        pygame.draw.line(feather_surf, (200, 200, 255, 255),
                                       (int(fx), int(fy)), (int(fex), int(fey)), 1)
                    s.blit(feather_surf, (0, 0))
        
        # 雷电战矛（斜握）
        spear_angle = math.pi / 4 + math.sin(t * 2) * 0.2
        spear_length = 40
        spear_x1 = 60
        spear_y1 = 55
        spear_x2 = spear_x1 + math.cos(spear_angle) * spear_length
        spear_y2 = spear_y1 + math.sin(spear_angle) * spear_length
        
        # 矛柄
        pygame.draw.line(s, (200, 200, 220), (spear_x1, spear_y1),
                       (int(spear_x2), int(spear_y2)), 4)
        # 矛尖
        spear_tip_points = [
            (spear_x2, spear_y2),
            (spear_x2 + math.cos(spear_angle + 0.3) * 10,
             spear_y2 + math.sin(spear_angle + 0.3) * 10),
            (spear_x2 + math.cos(spear_angle - 0.3) * 10,
             spear_y2 + math.sin(spear_angle - 0.3) * 10)
        ]
        pygame.draw.polygon(s, (255, 255, 255), [(int(p[0]), int(p[1])) for p in spear_tip_points])
        
        # 闪电环绕战矛
        for bolt in range(5):
            bolt_progress = (t * 3 + bolt * 0.4) % 1
            bolt_x = spear_x1 + (spear_x2 - spear_x1) * bolt_progress
            bolt_y = spear_y1 + (spear_y2 - spear_y1) * bolt_progress
            bolt_offset = math.sin(t * 6 + bolt) * 8
            bolt_ox = bolt_x + math.cos(spear_angle + math.pi / 2) * bolt_offset
            bolt_oy = bolt_y + math.sin(spear_angle + math.pi / 2) * bolt_offset
            bolt_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(bolt_surf, (220, 220, 255, 200),
                           (int(bolt_x), int(bolt_y)), (int(bolt_ox), int(bolt_oy)), 2)
            s.blit(bolt_surf, (0, 0))
        
        # 神圣光环效果
        for ring in range(3):
            ring_radius = 35 + ring * 15
            ring_alpha = int(150 - ring * 40)
            ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (255, 255, 240, ring_alpha), (60, 50), ring_radius, 2)
            s.blit(ring_surf, (0, 0))
        
        return s
    elif model_style == "viper_ex3":
        # 毒液交响曲 - 剧毒旋律
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 中心毒液唱片（旋转）
        disc_rotation = t * 2
        disc_radius = 18
        pygame.draw.circle(s, (0, 200, 80), (60, 50), disc_radius)
        pygame.draw.circle(s, (0, 255, 100), (60, 50), disc_radius, 2)
        # 唱片纹路
        for groove in range(5):
            groove_radius = disc_radius - groove * 3
            pygame.draw.circle(s, (0, 150, 60), (60, 50), groove_radius, 1)
        
        # 音符形状飞舞（各种音乐符号）
        notes = []
        for note in range(16):
            note_angle = disc_rotation + note * math.pi / 8
            note_dist = 25 + 20 * ((note % 4) / 4)
            note_x = 60 + math.cos(note_angle) * note_dist
            note_y = 50 + math.sin(note_angle) * note_dist
            notes.append((note_x, note_y, note))
            
            # 绘制不同类型的音符
            note_type = note % 4
            if note_type == 0:  # 四分音符
                pygame.draw.circle(s, (100, 255, 150), (int(note_x), int(note_y)), 4)
                pygame.draw.line(s, (100, 255, 150), (int(note_x + 4), int(note_y)),
                               (int(note_x + 4), int(note_y - 12)), 2)
            elif note_type == 1:  # 八分音符
                pygame.draw.circle(s, (100, 255, 150), (int(note_x), int(note_y)), 3)
                pygame.draw.line(s, (100, 255, 150), (int(note_x + 3), int(note_y)),
                               (int(note_x + 3), int(note_y - 10)), 2)
                pygame.draw.circle(s, (100, 255, 150), (int(note_x + 8), int(note_y - 10)), 2)
            elif note_type == 2:  # 升调符号
                pygame.draw.line(s, (100, 255, 150), (int(note_x - 3), int(note_y - 6)),
                               (int(note_x - 3), int(note_y + 6)), 2)
                pygame.draw.line(s, (100, 255, 150), (int(note_x + 3), int(note_y - 6)),
                               (int(note_x + 3), int(note_y + 6)), 2)
            else:  # 降调符号
                pygame.draw.circle(s, (100, 255, 150), (int(note_x), int(note_y - 3)), 3)
                pygame.draw.circle(s, (100, 255, 150), (int(note_x), int(note_y + 3)), 3)
        
        # 毒液音波（同心圆波纹带毒液效果）
        for wave in range(6):
            wave_radius = (t * 60 + wave * 15) % 90
            wave_alpha = int(200 * (1 - wave_radius / 90))
            # 波纹不是完美圆形，有毒液扭曲
            wave_points = []
            for i in range(16):
                wave_angle = i * math.pi / 8
                distortion = 3 * math.sin(t * 4 + wave + i)
                wx = 60 + math.cos(wave_angle) * (wave_radius + distortion)
                wy = 50 + math.sin(wave_angle) * (wave_radius + distortion)
                wave_points.append((int(wx), int(wy)))
            
            wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            if len(wave_points) > 2:
                pygame.draw.polygon(wave_surf, (0, 255, 100, wave_alpha), wave_points, 3)
            s.blit(wave_surf, (0, 0))
        
        # 五线谱线条
        for staff_line in range(5):
            staff_y = 20 + staff_line * 8
            staff_alpha = int(150 + 100 * math.sin(t * 3 + staff_line))
            staff_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(staff_surf, (50, 255, 120, staff_alpha),
                           (10, staff_y), (110, staff_y), 1)
            s.blit(staff_surf, (0, 0))
        
        # 毒液飞溅粒子（跟随旋律）
        for splash in range(12):
            splash_angle = t * 4 + splash * 0.5
            splash_dist = 30 + 15 * math.sin(t * 2 + splash)
            splash_x = 60 + math.cos(splash_angle) * splash_dist
            splash_y = 50 + math.sin(splash_angle) * splash_dist
            splash_size = 3 + int(2 * math.sin(t * 6 + splash))
            pygame.draw.circle(s, (150, 255, 50), (int(splash_x), int(splash_y)), splash_size)
        
        return s
    
    elif model_style == "specter_ex3":
        # 量子幽灵 - 叠加态，多位置存在
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 量子叠加（同时在多个位置）
        superposition_count = 8
        for pos in range(superposition_count):
            # 概率幅度（位置的可能性）
            amplitude = 0.3 + 0.7 * ((math.sin(t * 3 + pos) + 1) / 2)
            alpha = int(200 * amplitude)
            
            # 位置偏移
            offset_angle = pos * 2 * math.pi / superposition_count
            offset_dist = 15 * math.sin(t * 2 + pos)
            pos_x = 60 + math.cos(offset_angle) * offset_dist
            pos_y = 50 + math.sin(offset_angle) * offset_dist
            
            # 绘制幽灵形态
            ghost_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 头部
            pygame.draw.circle(ghost_surf, (100, 255, 255, alpha), (int(pos_x), int(pos_y - 10)), 8)
            # 身体（飘渺状）
            body_points = [
                (pos_x, pos_y - 2),
                (pos_x - 8, pos_y + 10),
                (pos_x - 6, pos_y + 18),
                (pos_x + 6, pos_y + 18),
                (pos_x + 8, pos_y + 10)
            ]
            pygame.draw.polygon(ghost_surf, (100, 255, 255, alpha),
                              [(int(p[0]), int(p[1])) for p in body_points])
            s.blit(ghost_surf, (0, 0))
        
        # 量子纠缠线（连接不同位置）
        entangle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(superposition_count):
            for j in range(i + 1, superposition_count):
                if random.random() < 0.4:
                    angle_i = i * 2 * math.pi / superposition_count
                    offset_i = 15 * math.sin(t * 2 + i)
                    pos_xi = 60 + math.cos(angle_i) * offset_i
                    pos_yi = 50 + math.sin(angle_i) * offset_i
                    
                    angle_j = j * 2 * math.pi / superposition_count
                    offset_j = 15 * math.sin(t * 2 + j)
                    pos_xj = 60 + math.cos(angle_j) * offset_j
                    pos_yj = 50 + math.sin(angle_j) * offset_j
                    
                    pygame.draw.line(entangle_surf, (150, 255, 255, 120),
                                   (int(pos_xi), int(pos_yi)), (int(pos_xj), int(pos_yj)), 1)
        s.blit(entangle_surf, (0, 0))
        
        # 波函数（概率密度云）
        for cloud_particle in range(40):
            cloud_angle = cloud_particle * 0.5
            cloud_dist = 10 + 35 * random.random()
            cloud_x = 60 + math.cos(cloud_angle) * cloud_dist
            cloud_y = 50 + math.sin(cloud_angle) * cloud_dist
            cloud_probability = 1 - (cloud_dist - 10) / 35
            cloud_alpha = int(180 * cloud_probability)
            cloud_size = 2 + int(3 * cloud_probability)
            if cloud_alpha > 30:
                pygame.draw.circle(s, (120, 255, 255, cloud_alpha),
                                 (int(cloud_x), int(cloud_y)), cloud_size)
        
        # 观测者效应（当观测时坍缩）
        collapse_progress = (math.sin(t * 1.5) + 1) / 2
        if collapse_progress > 0.7:  # 观测发生
            # 坍缩到中心位置
            collapse_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            collapse_intensity = int(255 * ((collapse_progress - 0.7) / 0.3))
            for ring in range(5):
                ring_radius = 45 - ring * 8 - int(collapse_progress * 10)
                ring_alpha = int(200 * (1 - ring / 5))
                pygame.draw.circle(collapse_surf, (100, 255, 255, ring_alpha),
                                 (60, 50), ring_radius, 2)
            s.blit(collapse_surf, (0, 0))
        
        # 量子涨落粒子
        for fluctuation in range(15):
            if (int(t * 20) + fluctuation) % 10 < 5:
                fluc_angle = fluctuation * 0.8
                fluc_dist = 20 + 25 * random.random()
                fluc_x = 60 + math.cos(fluc_angle) * fluc_dist
                fluc_y = 50 + math.sin(fluc_angle) * fluc_dist
                pygame.draw.circle(s, (200, 255, 255), (int(fluc_x), int(fluc_y)), 2)
        
        return s
    
    elif model_style == "aurora_ex3":
        # 北极光兽 - 极地守望
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.8) * 0.15 + 1
        
        # 狼形身体轮廓
        wolf_body = [
            (60, 35),  # 头部中心
            (50, 45), (45, 55),  # 前腿
            (48, 70), (52, 75),  # 前爪
            (60, 72), # 胸部
            (68, 75), (72, 70),  # 后腿
            (75, 55), (70, 45)  # 后躯
        ]
        pygame.draw.polygon(s, (180, 220, 255), wolf_body)
        pygame.draw.polygon(s, (200, 240, 255), wolf_body, 3)
        
        # 狼头（尖耳朵）
        # 左耳
        left_ear = [(53, 30), (50, 20), (57, 28)]
        pygame.draw.polygon(s, (180, 220, 255), left_ear)
        # 右耳
        right_ear = [(67, 30), (70, 20), (63, 28)]
        pygame.draw.polygon(s, (180, 220, 255), right_ear)
        # 狼嘴
        snout_points = [(60, 35), (55, 40), (60, 42), (65, 40)]
        pygame.draw.polygon(s, (200, 230, 255), snout_points)
        
        # 北极光毛发（流动的七彩光带）
        aurora_colors = [
            (0, 255, 150), (100, 255, 200), (150, 200, 255),
            (200, 150, 255), (255, 100, 200)
        ]
        
        for fur_layer in range(5):
            fur_y_offset = 40 + fur_layer * 8
            fur_wave = math.sin(t * 2 + fur_layer * 0.5) * 8
            color_idx = fur_layer % len(aurora_colors)
            aurora_color = aurora_colors[color_idx]
            
            # 流动的光带
            fur_points = []
            for seg in range(10):
                seg_x = 40 + seg * 4
                seg_y = fur_y_offset + math.sin(t * 3 + seg * 0.3 + fur_layer) * 5
                fur_points.append((int(seg_x), int(seg_y)))
            
            # 绘制光带
            if len(fur_points) > 1:
                fur_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                for i in range(len(fur_points) - 1):
                    alpha = int(180 - i * 15)
                    pygame.draw.line(fur_surf, (*aurora_color, alpha),
                                   fur_points[i], fur_points[i + 1], 3)
                s.blit(fur_surf, (0, 0))
        
        # 北极光尾巴（长长的光流尾巴）
        tail_segments = 12
        for tail_seg in range(tail_segments):
            tail_progress = tail_seg / tail_segments
            tail_x = 70 + tail_seg * 3
            tail_y = 50 + math.sin(t * 2.5 + tail_seg * 0.4) * 15
            tail_size = int(8 * (1 - tail_progress))
            tail_alpha = int(220 * (1 - tail_progress))
            color_idx = tail_seg % len(aurora_colors)
            tail_color = aurora_colors[color_idx]
            
            if tail_size > 0:
                tail_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(tail_surf, (*tail_color, tail_alpha),
                                 (int(tail_x), int(tail_y)), tail_size)
                s.blit(tail_surf, (0, 0))
        
        # 极光粒子环绕
        for aurora_particle in range(20):
            ap_angle = t * 2 + aurora_particle * 0.3
            ap_dist = 25 + 15 * math.sin(t * 3 + aurora_particle)
            ap_x = 60 + math.cos(ap_angle) * ap_dist
            ap_y = 50 + math.sin(ap_angle) * ap_dist
            color_idx = aurora_particle % len(aurora_colors)
            ap_color = aurora_colors[color_idx]
            pygame.draw.circle(s, ap_color, (int(ap_x), int(ap_y)), 3)
        
        # 冰晶效果
        for crystal in range(8):
            cx_angle = t * 1.5 + crystal * math.pi / 4
            cx_dist = 35
            cx_x = 60 + math.cos(cx_angle) * cx_dist
            cx_y = 50 + math.sin(cx_angle) * cx_dist
            # 六角冰晶
            crystal_points = []
            for i in range(6):
                cp_angle = cx_angle + i * math.pi / 3
                cp_x = cx_x + math.cos(cp_angle) * 4
                cp_y = cx_y + math.sin(cp_angle) * 4
                crystal_points.append((int(cp_x), int(cp_y)))
            pygame.draw.polygon(s, (200, 240, 255, 200), crystal_points)
        
        return s
    
    elif model_style == "crimson_ex3":
        # 恒星熔炉 - 核聚变
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.25 + 1
        
        # 核心反应堆（超亮中心）
        core_radius = int(12 * pulse)
        for core_layer in range(6, 0, -1):
            layer_radius = int(core_radius * (core_layer / 6))
            layer_brightness = int(255 * (core_layer / 6))
            layer_alpha = 255
            core_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 颜色从白到黄到红渐变
            if core_layer > 4:
                core_color = (255, 255, layer_brightness)
            elif core_layer > 2:
                core_color = (255, layer_brightness, 100)
            else:
                core_color = (255, 100, 50)
            pygame.draw.circle(core_surf, (*core_color, layer_alpha),
                             (60, 50), layer_radius)
            s.blit(core_surf, (0, 0))
        
        # 等离子体环流（旋转）
        plasma_rings = 4
        for ring in range(plasma_rings):
            ring_radius = 18 + ring * 8
            ring_rotation = t * (2 + ring * 0.3)
            ring_alpha = int(220 - ring * 40)
            
            # 不完整的圆环（模拟磁场线）
            for arc_seg in range(6):
                arc_start = ring_rotation + arc_seg * math.pi / 3
                arc_end = arc_start + math.pi / 4
                # 绘制弧段
                arc_points = []
                for arc_step in range(8):
                    arc_angle = arc_start + (arc_end - arc_start) * (arc_step / 8)
                    arc_x = 60 + math.cos(arc_angle) * ring_radius
                    arc_y = 50 + math.sin(arc_angle) * ring_radius
                    arc_points.append((int(arc_x), int(arc_y)))
                
                if len(arc_points) > 1:
                    plasma_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    for i in range(len(arc_points) - 1):
                        plasma_color = (255, 150 - ring * 30, 50)
                        pygame.draw.line(plasma_surf, (*plasma_color, ring_alpha),
                                       arc_points[i], arc_points[i + 1], 3)
                    s.blit(plasma_surf, (0, 0))
        
        # 太阳耀斑（喷射）
        flare_count = 8
        for flare in range(flare_count):
            flare_angle = t * 1.5 + flare * 2 * math.pi / flare_count
            flare_intensity = (math.sin(t * 4 + flare) + 1) / 2
            
            if flare_intensity > 0.5:  # 只在高强度时显示
                flare_length = 30 + 20 * flare_intensity
                flare_start_dist = 15
                flare_sx = 60 + math.cos(flare_angle) * flare_start_dist
                flare_sy = 50 + math.sin(flare_angle) * flare_start_dist
                flare_ex = 60 + math.cos(flare_angle) * flare_length
                flare_ey = 50 + math.sin(flare_angle) * flare_length
                
                # 多层耀斑
                for flare_layer in range(3):
                    flare_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    layer_offset = flare_layer * 2
                    layer_alpha = int(200 * flare_intensity - flare_layer * 50)
                    flare_color = (255, 200 - flare_layer * 50, 100)
                    
                    offset_angle = flare_angle + math.pi / 2
                    offset_x = math.cos(offset_angle) * layer_offset
                    offset_y = math.sin(offset_angle) * layer_offset
                    
                    pygame.draw.line(flare_surf, (*flare_color, layer_alpha),
                                   (int(flare_sx + offset_x), int(flare_sy + offset_y)),
                                   (int(flare_ex + offset_x), int(flare_ey + offset_y)), 4 - flare_layer)
                    s.blit(flare_surf, (0, 0))
        
        # 核反应粒子（高速喷射）
        for particle in range(30):
            particle_angle = particle * 0.4 + t * 5
            particle_progress = (t * 4 + particle * 0.1) % 1
            particle_dist = 10 + particle_progress * 45
            px = 60 + math.cos(particle_angle) * particle_dist
            py = 50 + math.sin(particle_angle) * particle_dist
            particle_alpha = int(255 * (1 - particle_progress))
            particle_size = int(4 * (1 - particle_progress)) + 1
            
            if particle_alpha > 30:
                pygame.draw.circle(s, (255, 255, 200, particle_alpha),
                                 (int(px), int(py)), particle_size)
        
        # 热浪扭曲（环形热波）
        for heat_wave in range(3):
            wave_radius = (t * 50 + heat_wave * 25) % 75
            wave_alpha = int(150 * (1 - wave_radius / 75))
            wave_distortion = 5 * math.sin(t * 4 + heat_wave)
            
            wave_points = []
            for i in range(16):
                wave_angle = i * math.pi / 8
                distort = wave_distortion * math.sin(i)
                wx = 60 + math.cos(wave_angle) * (wave_radius + distort)
                wy = 50 + math.sin(wave_angle) * (wave_radius + distort)
                wave_points.append((int(wx), int(wy)))
            
            if len(wave_points) > 2:
                heat_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.polygon(heat_surf, (255, 150, 50, wave_alpha), wave_points, 2)
                s.blit(heat_surf, (0, 0))
        
        return s
    
    elif model_style == "stalker_ex3":
        # 纳米风暴 - 灰雾吞噬
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 纳米机器人云（密集小粒子）
        nano_particle_count = 80
        for nano in range(nano_particle_count):
            # 螺旋运动
            nano_angle = t * 3 + nano * 0.2
            nano_spiral_radius = 10 + (nano % 30)
            nano_height = math.sin(t * 2 + nano * 0.1) * 15
            nano_x = 60 + math.cos(nano_angle) * nano_spiral_radius
            nano_y = 50 + nano_height + (nano % 5) * 3 - 10
            
            # 纳米粒子大小和颜色变化
            nano_size = 1 + int((nano % 3))
            nano_brightness = 100 + int(155 * ((math.sin(t * 4 + nano) + 1) / 2))
            nano_alpha = 150 + int(100 * ((nano_spiral_radius - 10) / 30))
            
            pygame.draw.circle(s, (nano_brightness, nano_brightness, nano_brightness, nano_alpha),
                             (int(nano_x), int(nano_y)), nano_size)
        
        # 吞噬波纹（向内收缩）
        for devour_wave in range(5):
            wave_progress = (t * 2 + devour_wave * 0.4) % 1
            # 从外向内
            wave_radius = int(50 * (1 - wave_progress))
            wave_alpha = int(200 * wave_progress)
            
            if wave_radius > 5:
                devour_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(devour_surf, (80, 80, 80, wave_alpha),
                                 (60, 50), wave_radius, 2)
                s.blit(devour_surf, (0, 0))
        
        # 灰雾触手（从中心延伸）
        tentacle_count = 8
        for tentacle in range(tentacle_count):
            tentacle_angle = tentacle * 2 * math.pi / tentacle_count + t * 0.5
            tentacle_length = 35 + 10 * math.sin(t * 2 + tentacle)
            
            # 触手由多段组成
            tentacle_segments = 8
            tentacle_points = [(60, 50)]
            
            for seg in range(1, tentacle_segments + 1):
                seg_progress = seg / tentacle_segments
                seg_dist = tentacle_length * seg_progress
                # 触手摆动
                seg_offset = math.sin(t * 3 + seg * 0.5) * 8 * seg_progress
                seg_angle = tentacle_angle + seg_offset * 0.1
                
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist
                tentacle_points.append((int(seg_x), int(seg_y)))
            
            # 绘制触手
            if len(tentacle_points) > 1:
                tentacle_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                for i in range(len(tentacle_points) - 1):
                    segment_alpha = int(180 * (1 - i / len(tentacle_points)))
                    segment_width = int(5 * (1 - i / len(tentacle_points))) + 1
                    pygame.draw.line(tentacle_surf, (100, 100, 100, segment_alpha),
                                   tentacle_points[i], tentacle_points[i + 1], segment_width)
                s.blit(tentacle_surf, (0, 0))
        
        # 被吞噬的碎片（向中心飞）
        for debris in range(15):
            debris_progress = (t * 2.5 + debris * 0.3) % 1
            debris_angle = debris * 0.8
            # 从外向内
            debris_dist = 50 * (1 - debris_progress)
            debris_x = 60 + math.cos(debris_angle) * debris_dist
            debris_y = 50 + math.sin(debris_angle) * debris_dist
            debris_alpha = int(255 * (1 - debris_progress))
            debris_size = 3 + int(3 * (1 - debris_progress))
            
            if debris_alpha > 30 and debris_dist > 5:
                debris_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                # 碎片形状（小方块）
                debris_rect = pygame.Rect(int(debris_x - debris_size / 2),
                                        int(debris_y - debris_size / 2),
                                        debris_size, debris_size)
                pygame.draw.rect(debris_surf, (150, 150, 150, debris_alpha), debris_rect)
                s.blit(debris_surf, (0, 0))
        
        # 中心吞噬核心
        core_pulse_radius = int(8 + 4 * pulse)
        for core_layer in range(4, 0, -1):
            layer_radius = int(core_pulse_radius * (core_layer / 4))
            layer_alpha = int(200 * (core_layer / 4))
            core_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(core_surf, (50, 50, 50, layer_alpha),
                             (60, 50), layer_radius)
            s.blit(core_surf, (0, 0))
        
        return s
    elif model_style == "gaia_ex3":
        # 四季更迭 - 轮回之树
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.15 + 1
        
        # 中心树干
        trunk_points = [(55, 80), (58, 40), (62, 40), (65, 80)]
        pygame.draw.polygon(s, (100, 70, 50), trunk_points)
        
        # 四季分区（树冠分成4个象限）
        seasons = [
            ("spring", 0, (100, 255, 150)),      # 春 - 绿色
            ("summer", math.pi / 2, (255, 200, 50)),   # 夏 - 金黄
            ("autumn", math.pi, (255, 100, 50)),      # 秋 - 橙红
            ("winter", 3 * math.pi / 2, (200, 230, 255))  # 冬 - 冰蓝
        ]
        
        for season_name, base_angle, color in seasons:
            # 每个季节占90度
            season_rotation = t * 2  # 整体旋转展示四季轮回
            
            for branch in range(8):
                branch_angle = base_angle + season_rotation + (branch / 8) * (math.pi / 2)
                branch_length = 20 + 15 * ((branch % 3) / 3)
                branch_x = 60 + math.cos(branch_angle) * branch_length
                branch_y = 50 + math.sin(branch_angle) * branch_length
                
                # 季节特色
                if season_name == "spring":  # 春 - 花朵
                    for petal in range(4):
                        petal_angle = t * 3 + petal * math.pi / 2
                        petal_x = branch_x + math.cos(petal_angle) * 4
                        petal_y = branch_y + math.sin(petal_angle) * 4
                        pygame.draw.circle(s, (255, 150, 200), (int(petal_x), int(petal_y)), 3)
                    pygame.draw.circle(s, color, (int(branch_x), int(branch_y)), 2)
                
                elif season_name == "summer":  # 夏 - 太阳光芒
                    pygame.draw.circle(s, color, (int(branch_x), int(branch_y)), 5)
                    for ray in range(6):
                        ray_angle = t * 4 + ray * math.pi / 3
                        ray_x = branch_x + math.cos(ray_angle) * 7
                        ray_y = branch_y + math.sin(ray_angle) * 7
                        pygame.draw.line(s, (255, 255, 100),
                                       (int(branch_x), int(branch_y)),
                                       (int(ray_x), int(ray_y)), 2)
                
                elif season_name == "autumn":  # 秋 - 落叶
                    leaf_fall = (t * 2 + branch) % 1
                    leaf_y = branch_y + leaf_fall * 30
                    leaf_alpha = int(255 * (1 - leaf_fall))
                    if leaf_alpha > 30:
                        leaf_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                        # 椭圆形叶子
                        leaf_rect = pygame.Rect(int(branch_x - 3), int(leaf_y - 2), 6, 4)
                        pygame.draw.ellipse(leaf_surf, (*color, leaf_alpha), leaf_rect)
                        s.blit(leaf_surf, (0, 0))
                
                else:  # 冬 - 雪花
                    # 六角雪花
                    for flake_arm in range(6):
                        flake_angle = branch_angle + flake_arm * math.pi / 3
                        flake_x = branch_x + math.cos(flake_angle) * 4
                        flake_y = branch_y + math.sin(flake_angle) * 4
                        pygame.draw.line(s, color,
                                       (int(branch_x), int(branch_y)),
                                       (int(flake_x), int(flake_y)), 1)
                    pygame.draw.circle(s, color, (int(branch_x), int(branch_y)), 2)
        
        # 轮回之环（四色环绕）
        for ring_seg in range(4):
            ring_color = seasons[ring_seg][2]
            ring_start_angle = seasons[ring_seg][1] + t * 2
            ring_end_angle = ring_start_angle + math.pi / 2
            
            # 绘制弧段
            arc_points = [(60, 50)]
            for arc_step in range(10):
                arc_progress = arc_step / 10
                arc_angle = ring_start_angle + (ring_end_angle - ring_start_angle) * arc_progress
                arc_x = 60 + math.cos(arc_angle) * 35
                arc_y = 50 + math.sin(arc_angle) * 35
                arc_points.append((int(arc_x), int(arc_y)))
            
            if len(arc_points) > 2:
                ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(ring_surf, ring_color, False, arc_points, 3)
                s.blit(ring_surf, (0, 0))
        
        return s
    
    elif model_style == "weaver_ex3":
        # 神经网络 - 思维脉冲
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.15 + 1
        
        # 神经元节点（多层网络）
        neurons = []
        layers = 4
        for layer in range(layers):
            neurons_in_layer = 5 + layer
            for neuron in range(neurons_in_layer):
                neuron_x = 20 + layer * 25
                neuron_y = 20 + (100 / (neurons_in_layer + 1)) * (neuron + 1)
                # 激活强度
                activation = (math.sin(t * 3 + layer * 0.5 + neuron * 0.3) + 1) / 2
                neurons.append((neuron_x, neuron_y, activation, layer))
        
        # 绘制神经连接（突触）
        synapse_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i, (x1, y1, act1, layer1) in enumerate(neurons):
            for j, (x2, y2, act2, layer2) in enumerate(neurons):
                # 只连接相邻层
                if layer2 == layer1 + 1:
                    # 连接强度
                    connection_strength = (act1 + act2) / 2
                    synapse_alpha = int(200 * connection_strength)
                    synapse_width = 1 + int(2 * connection_strength)
                    
                    # 脉冲传递动画
                    pulse_progress = (t * 2 + i * 0.1 + j * 0.1) % 1
                    pulse_x = x1 + (x2 - x1) * pulse_progress
                    pulse_y = y1 + (y2 - y1) * pulse_progress
                    
                    # 绘制连接线
                    pygame.draw.line(synapse_surf, (100, 200, 255, synapse_alpha),
                                   (int(x1), int(y1)), (int(x2), int(y2)), synapse_width)
                    
                    # 绘制脉冲点
                    pulse_size = int(3 * connection_strength)
                    if pulse_size > 0:
                        pygame.draw.circle(synapse_surf, (255, 255, 100),
                                         (int(pulse_x), int(pulse_y)), pulse_size)
        s.blit(synapse_surf, (0, 0))
        
        # 绘制神经元
        for neuron_x, neuron_y, activation, layer in neurons:
            neuron_size = int(5 + 5 * activation)
            neuron_brightness = int(150 + 105 * activation)
            
            # 神经元核心
            pygame.draw.circle(s, (neuron_brightness, neuron_brightness, 255), 
                             (int(neuron_x), int(neuron_y)), neuron_size)
            # 神经元外环
            pygame.draw.circle(s, (200, 200, 255), 
                             (int(neuron_x), int(neuron_y)), neuron_size + 2, 1)
            
            # 激活时发光
            if activation > 0.7:
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                glow_alpha = int(150 * (activation - 0.7) / 0.3)
                pygame.draw.circle(glow_surf, (255, 255, 200, glow_alpha),
                                 (int(neuron_x), int(neuron_y)), neuron_size + 5)
                s.blit(glow_surf, (0, 0))
        
        # 电信号波纹（全局思维活动）
        for signal_wave in range(3):
            wave_progress = (t * 1.5 + signal_wave * 0.5) % 1
            wave_x = 20 + wave_progress * 100
            wave_alpha = int(180 * (1 - abs(wave_progress - 0.5) * 2))
            
            if wave_alpha > 30:
                signal_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(signal_surf, (150, 200, 255, wave_alpha),
                               (int(wave_x), 10), (int(wave_x), 110), 2)
                s.blit(signal_surf, (0, 0))
        
        return s
    
    elif model_style == "solar_ex3":
        # 暗物质潮汐 - 引力奇点
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2) * 0.2 + 1
        
        # 奇点核心（超密黑洞）
        singularity_radius = int(8 * pulse)
        # 事件视界
        for horizon_layer in range(5, 0, -1):
            horizon_radius = int(singularity_radius * (horizon_layer / 5))
            horizon_alpha = int(255 * (horizon_layer / 5))
            # 黑到紫的渐变
            horizon_color = (50 * (horizon_layer / 5), 0, 100 * (horizon_layer / 5))
            pygame.draw.circle(s, (*horizon_color, horizon_alpha), (60, 50), horizon_radius)
        
        # 吸积盘（螺旋旋转）
        accretion_spirals = 3
        for spiral in range(accretion_spirals):
            spiral_offset = spiral * 2 * math.pi / accretion_spirals
            
            for segment in range(30):
                seg_angle = t * 3 + spiral_offset + segment * 0.3
                seg_dist = 12 + segment * 1.5
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist * 0.3  # 扁平
                
                # 颜色从外到内：蓝->紫->红（温度上升）
                temp_factor = 1 - (segment / 30)
                if temp_factor > 0.7:
                    seg_color = (100, 100, 255)
                elif temp_factor > 0.4:
                    seg_color = (200, 100, 255)
                else:
                    seg_color = (255, 150, 100)
                
                seg_alpha = int(220 * (1 - temp_factor * 0.5))
                seg_size = int(3 + 3 * temp_factor)
                
                pygame.draw.circle(s, (*seg_color, seg_alpha),
                                 (int(seg_x), int(seg_y)), seg_size)
        
        # 引力透镜效应（光线弯曲）
        for lens_ring in range(4):
            ring_radius = 15 + lens_ring * 10
            ring_rotation = t * (1 + lens_ring * 0.2)
            ring_alpha = int(180 - lens_ring * 40)
            
            # 扭曲的环
            lens_points = []
            for i in range(20):
                lens_angle = i * math.pi / 10 + ring_rotation
                # 引力扭曲
                distortion = 5 * math.sin(lens_angle * 3)
                lensed_radius = ring_radius + distortion
                lens_x = 60 + math.cos(lens_angle) * lensed_radius
                lens_y = 50 + math.sin(lens_angle) * lensed_radius * 0.6
                lens_points.append((int(lens_x), int(lens_y)))
            
            if len(lens_points) > 2:
                lens_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(lens_surf, (150, 150, 255, ring_alpha), True, lens_points, 2)
                s.blit(lens_surf, (0, 0))
        
        # 霍金辐射（从事件视界逃逸的粒子）
        for radiation in range(15):
            rad_angle = t * 4 + radiation * 0.4
            rad_progress = (t * 2 + radiation * 0.2) % 1
            rad_start_dist = singularity_radius + 2
            rad_dist = rad_start_dist + rad_progress * 30
            rad_x = 60 + math.cos(rad_angle) * rad_dist
            rad_y = 50 + math.sin(rad_angle) * rad_dist
            rad_alpha = int(255 * (1 - rad_progress))
            
            if rad_alpha > 30:
                pygame.draw.circle(s, (200, 200, 255, rad_alpha),
                                 (int(rad_x), int(rad_y)), 2)
        
        # 时空扭曲网格
        grid_lines = 8
        for grid_x in range(grid_lines):
            grid_points = []
            for grid_y in range(grid_lines):
                gx = 20 + grid_x * 10
                gy = 20 + grid_y * 10
                # 靠近奇点时扭曲
                dx = gx - 60
                dy = gy - 50
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    warp_factor = max(0, 1 - dist / 50)
                    warp_strength = warp_factor * 15
                    warp_angle = math.atan2(dy, dx) + math.pi
                    gx += math.cos(warp_angle) * warp_strength
                    gy += math.sin(warp_angle) * warp_strength
                grid_points.append((int(gx), int(gy)))
            
            if len(grid_points) > 1:
                grid_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(grid_surf, (80, 80, 120, 100), False, grid_points, 1)
                s.blit(grid_surf, (0, 0))
        
        return s
    
    elif model_style == "arbiter_ex3":
        # 真理之门 - 全知之眼
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.8) * 0.2 + 1
        
        # 中心全知之眼
        eye_radius = int(15 * pulse)
        # 眼白
        pygame.draw.circle(s, (255, 255, 255), (60, 50), eye_radius)
        # 虹膜（多层）
        iris_colors = [(100, 150, 255), (150, 200, 255), (200, 230, 255)]
        for iris_layer, iris_color in enumerate(iris_colors):
            iris_radius = int(eye_radius * 0.7 * ((3 - iris_layer) / 3))
            pygame.draw.circle(s, iris_color, (60, 50), iris_radius)
        # 瞳孔
        pupil_radius = int(eye_radius * 0.3)
        pygame.draw.circle(s, (0, 0, 0), (60, 50), pupil_radius)
        # 瞳孔反光
        pygame.draw.circle(s, (255, 255, 255), (62, 48), max(2, pupil_radius // 3))
        
        # 眼睑/边框
        pygame.draw.circle(s, (200, 180, 255), (60, 50), eye_radius, 2)
        
        # 真理之门框架（巨大门框）
        gate_width = 80
        gate_height = 100
        gate_left = 60 - gate_width // 2
        gate_top = 50 - gate_height // 2
        
        # 门框立柱
        left_pillar = pygame.Rect(gate_left - 5, gate_top, 5, gate_height)
        right_pillar = pygame.Rect(gate_left + gate_width, gate_top, 5, gate_height)
        pygame.draw.rect(s, (180, 160, 220), left_pillar)
        pygame.draw.rect(s, (180, 160, 220), right_pillar)
        pygame.draw.rect(s, (220, 200, 255), left_pillar, 1)
        pygame.draw.rect(s, (220, 200, 255), right_pillar, 1)
        
        # 门楣
        lintel = pygame.Rect(gate_left - 5, gate_top - 5, gate_width + 10, 5)
        pygame.draw.rect(s, (180, 160, 220), lintel)
        pygame.draw.rect(s, (220, 200, 255), lintel, 1)
        
        # 古代符文（在门框上）
        runes_on_gate = 12
        for rune_idx in range(runes_on_gate):
            rune_progress = rune_idx / runes_on_gate
            rune_brightness = int(150 + 105 * ((math.sin(t * 4 + rune_idx) + 1) / 2))
            
            if rune_idx < 6:  # 左柱
                rune_x = gate_left - 2
                rune_y = gate_top + int(gate_height * rune_progress)
            else:  # 右柱
                rune_x = gate_left + gate_width + 2
                rune_y = gate_top + int(gate_height * ((rune_idx - 6) / 6))
            
            # 简单符文形状（十字）
            rune_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(rune_surf, (rune_brightness, rune_brightness, 255),
                           (rune_x - 2, rune_y), (rune_x + 2, rune_y), 1)
            pygame.draw.line(rune_surf, (rune_brightness, rune_brightness, 255),
                           (rune_x, rune_y - 2), (rune_x, rune_y + 2), 1)
            s.blit(rune_surf, (0, 0))
        
        # 凝视射线（从眼睛射出）
        gaze_count = 16
        for gaze in range(gaze_count):
            gaze_angle = t * 2 + gaze * 2 * math.pi / gaze_count
            gaze_length = 35 + 10 * math.sin(t * 3 + gaze)
            gaze_ex = 60 + math.cos(gaze_angle) * gaze_length
            gaze_ey = 50 + math.sin(gaze_angle) * gaze_length
            
            gaze_alpha = int(150 * ((math.sin(t * 4 + gaze) + 1) / 2))
            if gaze_alpha > 50:
                gaze_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(gaze_surf, (200, 200, 255, gaze_alpha),
                               (60, 50), (int(gaze_ex), int(gaze_ey)), 1)
                s.blit(gaze_surf, (0, 0))
        
        # 知识粒子（环绕）
        for knowledge in range(20):
            know_angle = t * 1.5 + knowledge * 0.3
            know_dist = 25 + 15 * ((knowledge % 4) / 4)
            know_x = 60 + math.cos(know_angle) * know_dist
            know_y = 50 + math.sin(know_angle) * know_dist
            know_brightness = int(200 + 55 * math.sin(t * 5 + knowledge))
            
            # 书本/卷轴形状
            book_rect = pygame.Rect(int(know_x - 2), int(know_y - 3), 4, 6)
            pygame.draw.rect(s, (know_brightness, know_brightness, 255), book_rect)
            pygame.draw.line(s, (255, 255, 255), (int(know_x - 2), int(know_y)),
                           (int(know_x + 2), int(know_y)), 1)
        
        return s
    
    elif model_style == "eclipse_ex3":
        # 反物质引擎 - 湮灭核心
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 2.5) * 0.25 + 1
        
        # 湮灭核心（正反物质碰撞）
        core_radius = int(10 * pulse)
        # 能量爆发
        for explosion_layer in range(6, 0, -1):
            layer_radius = int(core_radius * (explosion_layer / 6))
            layer_alpha = 255
            # 白->黄->橙->红渐变
            if explosion_layer > 4:
                layer_color = (255, 255, 255)
            elif explosion_layer > 2:
                layer_color = (255, 255, 100)
            else:
                layer_color = (255, 150, 50)
            pygame.draw.circle(s, (*layer_color, layer_alpha), (60, 50), layer_radius)
        
        # 正物质流（蓝色，从左侧流入）
        matter_particles = 15
        for mp in range(matter_particles):
            mp_progress = (t * 3 + mp * 0.2) % 1
            mp_x = 10 + mp_progress * 45
            mp_y = 50 + math.sin(t * 4 + mp) * 10
            mp_alpha = int(255 * (1 - mp_progress))
            mp_size = 3 + int(3 * (1 - mp_progress))
            
            if mp_alpha > 30:
                pygame.draw.circle(s, (100, 150, 255, mp_alpha),
                                 (int(mp_x), int(mp_y)), mp_size)
        
        # 反物质流（红色，从右侧流入）
        for amp in range(matter_particles):
            amp_progress = (t * 3 + amp * 0.2) % 1
            amp_x = 110 - amp_progress * 45
            amp_y = 50 + math.sin(t * 4 + amp + math.pi) * 10
            amp_alpha = int(255 * (1 - amp_progress))
            amp_size = 3 + int(3 * (1 - amp_progress))
            
            if amp_alpha > 30:
                pygame.draw.circle(s, (255, 100, 100, amp_alpha),
                                 (int(amp_x), int(amp_y)), amp_size)
        
        # 湮灭光子射出（伽马射线）
        gamma_rays = 12
        for gamma in range(gamma_rays):
            gamma_angle = gamma * 2 * math.pi / gamma_rays + t * 4
            gamma_progress = (t * 5 + gamma * 0.3) % 1
            gamma_start_dist = core_radius + 2
            gamma_dist = gamma_start_dist + gamma_progress * 40
            gamma_x = 60 + math.cos(gamma_angle) * gamma_dist
            gamma_y = 50 + math.sin(gamma_angle) * gamma_dist
            gamma_alpha = int(255 * (1 - gamma_progress))
            
            if gamma_alpha > 30:
                # 绘制射线
                gamma_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                gamma_sx = 60 + math.cos(gamma_angle) * gamma_start_dist
                gamma_sy = 50 + math.sin(gamma_angle) * gamma_start_dist
                pygame.draw.line(gamma_surf, (255, 255, 255, gamma_alpha),
                               (int(gamma_sx), int(gamma_sy)),
                               (int(gamma_x), int(gamma_y)), 2)
                s.blit(gamma_surf, (0, 0))
        
        # 能量环（湮灭产生的冲击波）
        for shockwave in range(4):
            wave_progress = (t * 2 + shockwave * 0.3) % 1
            wave_radius = int(15 + wave_progress * 45)
            wave_alpha = int(220 * (1 - wave_progress))
            
            if wave_alpha > 30:
                wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(wave_surf, (255, 200, 150, wave_alpha),
                                 (60, 50), wave_radius, 3)
                s.blit(wave_surf, (0, 0))
        
        # 磁约束场（防止提前湮灭）
        magnetic_field_lines = 8
        for field_line in range(magnetic_field_lines):
            field_angle = field_line * math.pi / 4
            field_rotation = t * 2
            
            # 磁力线弧形
            field_points = []
            for arc_seg in range(15):
                arc_progress = arc_seg / 15
                arc_dist = 20 + arc_progress * 25
                arc_angle = field_angle + field_rotation + math.sin(arc_progress * math.pi) * 0.5
                field_x = 60 + math.cos(arc_angle) * arc_dist
                field_y = 50 + math.sin(arc_angle) * arc_dist
                field_points.append((int(field_x), int(field_y)))
            
            if len(field_points) > 1:
                field_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(field_surf, (100, 255, 255, 150), False, field_points, 1)
                s.blit(field_surf, (0, 0))
        
        return s
    
    elif model_style == "prism_ex3":
        # 五维投影 - 超立方体
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.5) * 0.15 + 1
        
        # 4D超立方体的3D投影顶点（Tesseract）
        # 内立方体顶点
        inner_size = 15
        inner_vertices = [
            (60 - inner_size, 50 - inner_size, -inner_size),
            (60 + inner_size, 50 - inner_size, -inner_size),
            (60 + inner_size, 50 + inner_size, -inner_size),
            (60 - inner_size, 50 + inner_size, -inner_size),
            (60 - inner_size, 50 - inner_size, inner_size),
            (60 + inner_size, 50 - inner_size, inner_size),
            (60 + inner_size, 50 + inner_size, inner_size),
            (60 - inner_size, 50 + inner_size, inner_size),
        ]
        
        # 外立方体顶点
        outer_size = 25
        outer_vertices = [
            (60 - outer_size, 50 - outer_size, -outer_size),
            (60 + outer_size, 50 - outer_size, -outer_size),
            (60 + outer_size, 50 + outer_size, -outer_size),
            (60 - outer_size, 50 + outer_size, -outer_size),
            (60 - outer_size, 50 - outer_size, outer_size),
            (60 + outer_size, 50 - outer_size, outer_size),
            (60 + outer_size, 50 + outer_size, outer_size),
            (60 - outer_size, 50 + outer_size, outer_size),
        ]
        
        # 4D旋转矩阵（简化投影）
        rotation_4d = t * 1.5
        
        # 投影顶点（应用4D旋转）
        def project_4d_vertex(v, w_coord):
            x, y, z = v
            # 简化的4D->3D投影
            w = w_coord * math.cos(rotation_4d)
            proj_scale = 1 / (4 - w * 0.1)
            return (int(x * proj_scale), int(y * proj_scale))
        
        inner_projected = [project_4d_vertex(v, -1) for v in inner_vertices]
        outer_projected = [project_4d_vertex(v, 1) for v in outer_vertices]
        
        # 绘制内立方体边
        inner_edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # 前面
            (4, 5), (5, 6), (6, 7), (7, 4),  # 后面
            (0, 4), (1, 5), (2, 6), (3, 7),  # 连接
        ]
        
        for edge in inner_edges:
            p1 = inner_projected[edge[0]]
            p2 = inner_projected[edge[1]]
            pygame.draw.line(s, (150, 200, 255), p1, p2, 2)
        
        # 绘制外立方体边
        for edge in inner_edges:
            p1 = outer_projected[edge[0]]
            p2 = outer_projected[edge[1]]
            pygame.draw.line(s, (200, 150, 255), p1, p2, 2)
        
        # 连接内外立方体（超立方体的4D边）
        for i in range(8):
            p1 = inner_projected[i]
            p2 = outer_projected[i]
            hyper_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(hyper_surf, (255, 200, 255, 180), p1, p2, 1)
            s.blit(hyper_surf, (0, 0))
        
        # 绘制顶点
        for vertex in inner_projected:
            pygame.draw.circle(s, (100, 255, 255), vertex, 4)
        for vertex in outer_projected:
            pygame.draw.circle(s, (255, 100, 255), vertex, 4)
        
        # 维度波动效果
        for dimension_wave in range(5):
            wave_angle = t * 2 + dimension_wave * 2 * math.pi / 5
            wave_dist = 35 + 10 * math.sin(t * 3 + dimension_wave)
            wave_x = 60 + math.cos(wave_angle) * wave_dist
            wave_y = 50 + math.sin(wave_angle) * wave_dist
            wave_alpha = int(200 * ((math.sin(t * 4 + dimension_wave) + 1) / 2))
            
            # 高维粒子
            for glow in range(3, 0, -1):
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                glow_radius = glow * 3
                glow_alpha = int(wave_alpha * (glow / 3))
                pygame.draw.circle(glow_surf, (255, 255, 255, glow_alpha),
                                 (int(wave_x), int(wave_y)), glow_radius)
                s.blit(glow_surf, (0, 0))
        
        # 维度裂缝（5D空间的切面）
        rift_count = 6
        for rift in range(rift_count):
            rift_angle = rift * math.pi / 3 + t
            rift_length = 40
            rift_x1 = 60 + math.cos(rift_angle) * 10
            rift_y1 = 50 + math.sin(rift_angle) * 10
            rift_x2 = 60 + math.cos(rift_angle) * rift_length
            rift_y2 = 50 + math.sin(rift_angle) * rift_length
            
            rift_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            rift_alpha = int(150 * ((math.sin(t * 3 + rift) + 1) / 2))
            pygame.draw.line(rift_surf, (200, 200, 255, rift_alpha),
                           (int(rift_x1), int(rift_y1)),
                           (int(rift_x2), int(rift_y2)), 2)
            s.blit(rift_surf, (0, 0))
        
        return s
    
    elif model_style == "necro_ex3":
        # 熵增极限 - 热寂降临
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pulse = math.sin(t * 1.2) * 0.1 + 1  # 缓慢脉动
        
        # 中心热寂核心（温度接近绝对零度）
        core_radius = int(12 * pulse)
        # 深蓝到黑的渐变（低温）
        for core_layer in range(6, 0, -1):
            layer_radius = int(core_radius * (core_layer / 6))
            layer_alpha = 255
            layer_blue = int(50 * (core_layer / 6))
            core_color = (layer_blue // 3, layer_blue // 3, layer_blue)
            pygame.draw.circle(s, (*core_color, layer_alpha), (60, 50), layer_radius)
        
        # 能量耗散（粒子运动逐渐停止）
        entropy_particles = 40
        for ep in range(entropy_particles):
            # 粒子速度递减
            ep_speed = 1 - (t % 3) / 3  # 随时间减速
            ep_angle = ep * 0.5 + t * ep_speed
            ep_dist = 15 + (ep % 8) * 4
            ep_x = 60 + math.cos(ep_angle) * ep_dist
            ep_y = 50 + math.sin(ep_angle) * ep_dist
            
            # 颜色渐暗（能量降低）
            ep_brightness = int(150 * ep_speed)
            ep_alpha = int(200 * ep_speed)
            ep_size = max(1, int(3 * ep_speed))
            
            if ep_alpha > 30:
                pygame.draw.circle(s, (ep_brightness // 2, ep_brightness // 2, ep_brightness, ep_alpha),
                                 (int(ep_x), int(ep_y)), ep_size)
        
        # 热死环（能量均匀分布）
        thermal_rings = 6
        for ring in range(thermal_rings):
            ring_radius = 15 + ring * 8
            ring_alpha = int(100 - ring * 15)
            
            # 环不完整（象征结构崩解）
            ring_completeness = 1 - (ring / thermal_rings) * 0.5
            ring_segments = int(20 * ring_completeness)
            
            for seg in range(ring_segments):
                seg_angle = seg * 2 * math.pi / 20 + t * 0.3
                seg_x1 = 60 + math.cos(seg_angle) * ring_radius
                seg_y1 = 50 + math.sin(seg_angle) * ring_radius
                seg_angle2 = (seg + 1) * 2 * math.pi / 20 + t * 0.3
                seg_x2 = 60 + math.cos(seg_angle2) * ring_radius
                seg_y2 = 50 + math.sin(seg_angle2) * ring_radius
                
                if ring_alpha > 10:
                    ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(ring_surf, (50, 50, 80, ring_alpha),
                                   (int(seg_x1), int(seg_y1)),
                                   (int(seg_x2), int(seg_y2)), 2)
                    s.blit(ring_surf, (0, 0))
        
        # 结构崩解（网格瓦解）
        grid_decay = (t % 5) / 5  # 5秒循环
        grid_size = 8
        for gx in range(grid_size):
            for gy in range(grid_size):
                grid_x = 20 + gx * 10
                grid_y = 20 + gy * 10
                
                # 网格点逐渐消失
                decay_progress = (gx + gy) / (grid_size * 2)
                if decay_progress < grid_decay:
                    continue  # 已消失
                
                point_alpha = int(120 * (1 - grid_decay))
                if point_alpha > 20:
                    pygame.draw.circle(s, (60, 60, 90, point_alpha),
                                     (grid_x, grid_y), 1)
                    
                    # 连接线
                    if gx < grid_size - 1:
                        next_x = 20 + (gx + 1) * 10
                        next_decay = (gx + 1 + gy) / (grid_size * 2)
                        if next_decay >= grid_decay:
                            line_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                            pygame.draw.line(line_surf, (60, 60, 90, point_alpha // 2),
                                           (grid_x, grid_y), (next_x, grid_y), 1)
                            s.blit(line_surf, (0, 0))
        
        # 信息丢失（随机闪烁的信息碎片）
        info_fragments = 12
        for frag in range(info_fragments):
            if (int(t * 5) + frag) % 7 < 2:  # 随机出现
                frag_angle = frag * 0.5
                frag_dist = 25 + 20 * random.random()
                frag_x = 60 + math.cos(frag_angle) * frag_dist
                frag_y = 50 + math.sin(frag_angle) * frag_dist
                frag_alpha = int(180 * random.random())
                
                # 二进制位形状
                frag_char = random.choice(['0', '1'])
                # 简化为点（无法渲染文字）
                pygame.draw.circle(s, (100, 100, 120, frag_alpha),
                                 (int(frag_x), int(frag_y)), 2)
        
        # 宇宙微波背景辐射（均匀但冰冷）
        cmb_noise = 30
        for noise in range(cmb_noise):
            noise_x = random.randint(10, 110)
            noise_y = random.randint(10, 110)
            noise_brightness = random.randint(40, 70)
            noise_alpha = random.randint(50, 100)
            pygame.draw.circle(s, (noise_brightness, noise_brightness, noise_brightness + 20, noise_alpha),
                             (noise_x, noise_y), 1)
        
        # 时间箭头停滞（熵达到最大）
        # 绘制停滞的钟表指针
        clock_center = (60, 50)
        clock_radius = 35
        # 时钟边框（破碎）
        for clock_seg in range(8):
            if (clock_seg + int(t * 2)) % 3 != 0:  # 部分缺失
                seg_start_angle = clock_seg * math.pi / 4
                seg_end_angle = seg_start_angle + math.pi / 4
                clock_points = [clock_center]
                for angle_step in range(5):
                    angle = seg_start_angle + (seg_end_angle - seg_start_angle) * (angle_step / 4)
                    cx = clock_center[0] + math.cos(angle) * clock_radius
                    cy = clock_center[1] + math.sin(angle) * clock_radius
                    clock_points.append((int(cx), int(cy)))
                
                if len(clock_points) > 2:
                    clock_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.lines(clock_surf, (80, 80, 100, 150), False, clock_points, 1)
                    s.blit(clock_surf, (0, 0))
        
        # 停滞的指针（几乎不动）
        hand_angle = t * 0.1  # 极慢
        hand_length = 25
        hand_x = 60 + math.cos(hand_angle - math.pi / 2) * hand_length
        hand_y = 50 + math.sin(hand_angle - math.pi / 2) * hand_length
        pygame.draw.line(s, (100, 100, 130), (60, 50), (int(hand_x), int(hand_y)), 2)
        
        return s
    
    # ========== 第四批16个超级动态涂装（无锚点+丰富配色）==========
    elif model_style == "striker_ex4":
        # 液态金属 - 活体机械
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 流动的液态金属效果（像水银一样）
        blob_count = 12
        for blob in range(blob_count):
            # 每个液滴的运动轨迹
            blob_angle = (blob / blob_count) * math.pi * 2 + t * 1.5
            blob_orbit = 20 + 10 * math.sin(t * 2 + blob * 0.5)
            blob_x = 60 + math.cos(blob_angle) * blob_orbit
            blob_y = 50 + math.sin(blob_angle) * blob_orbit
            
            # 液滴大小变化（呼吸效果）
            blob_size = 8 + 4 * math.sin(t * 3 + blob)
            
            # 金属反光效果（多层渐变）
            for layer in range(4, 0, -1):
                layer_size = blob_size * (layer / 4)
                layer_brightness = 140 + int(80 * (layer / 4))
                pygame.draw.circle(s, (layer_brightness, layer_brightness, layer_brightness + 20),
                                 (int(blob_x), int(blob_y)), int(layer_size))
        
        # 液态连接线（液滴之间的金属丝）
        for i in range(blob_count):
            angle_i = (i / blob_count) * math.pi * 2 + t * 1.5
            orbit_i = 20 + 10 * math.sin(t * 2 + i * 0.5)
            x1 = 60 + math.cos(angle_i) * orbit_i
            y1 = 50 + math.sin(angle_i) * orbit_i
            
            # 连接到相邻液滴
            next_i = (i + 1) % blob_count
            angle_next = (next_i / blob_count) * math.pi * 2 + t * 1.5
            orbit_next = 20 + 10 * math.sin(t * 2 + next_i * 0.5)
            x2 = 60 + math.cos(angle_next) * orbit_next
            y2 = 50 + math.sin(angle_next) * orbit_next
            
            # 波动的连接线
            segments = 5
            for seg in range(segments):
                seg_prog = seg / segments
                sx = x1 + (x2 - x1) * seg_prog
                sy = y1 + (y2 - y1) * seg_prog
                wave_offset = 3 * math.sin(t * 4 + seg + i)
                perp_angle = angle_i + math.pi / 2
                sx += math.cos(perp_angle) * wave_offset
                sy += math.sin(perp_angle) * wave_offset
                
                if seg < segments - 1:
                    next_prog = (seg + 1) / segments
                    ex = x1 + (x2 - x1) * next_prog
                    ey = y1 + (y2 - y1) * next_prog
                    next_wave = 3 * math.sin(t * 4 + seg + 1 + i)
                    ex += math.cos(perp_angle) * next_wave
                    ey += math.sin(perp_angle) * next_wave
                    
                    pygame.draw.line(s, (180, 180, 200), 
                                   (int(sx), int(sy)), (int(ex), int(ey)), 2)
        
        # 机械呼吸效果（中心脉动）
        breath_radius = int(15 + 8 * math.sin(t * 1.5))
        for ring in range(3):
            ring_radius = breath_radius + ring * 5
            ring_alpha = int(150 - ring * 40)
            ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (200, 200, 220, ring_alpha), (60, 50), ring_radius, 2)
            s.blit(ring_surf, (0, 0))
        
        # 流动粒子（展现液态特性）
        for particle in range(20):
            p_progress = (t * 2 + particle * 0.15) % 1
            p_angle = particle * 0.7 + t * 0.5
            p_dist = 15 + p_progress * 35
            px = 60 + math.cos(p_angle) * p_dist
            py = 50 + math.sin(p_angle) * p_dist
            p_alpha = int(200 * (1 - p_progress))
            
            if p_alpha > 30:
                pygame.draw.circle(s, (220, 220, 240, p_alpha), (int(px), int(py)), 2)
        
        return s
    
    elif model_style == "phantom_ex4":
        # 彩虹漩涡 - 光谱风暴
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 旋转的七彩光束
        color_segments = 7
        for segment in range(color_segments):
            # HSV色彩空间循环
            hue = (segment / color_segments + t * 0.5) % 1
            # HSV转RGB
            h = hue * 6
            c = 1
            x = 1 - abs(h % 2 - 1)
            if h < 1:
                r, g, b = c, x, 0
            elif h < 2:
                r, g, b = x, c, 0
            elif h < 3:
                r, g, b = 0, c, x
            elif h < 4:
                r, g, b = 0, x, c
            elif h < 5:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x
            
            color = (int(r * 255), int(g * 255), int(b * 255))
            
            # 螺旋光束
            spiral_turns = 3
            points = []
            for step in range(20):
                step_prog = step / 20
                spiral_angle = (segment / color_segments) * math.pi * 2 + step_prog * spiral_turns * math.pi * 2 + t * 2
                spiral_radius = 10 + step_prog * 40
                sx = 60 + math.cos(spiral_angle) * spiral_radius
                sy = 50 + math.sin(spiral_angle) * spiral_radius
                points.append((int(sx), int(sy)))
            
            # 绘制彩色螺旋
            if len(points) > 1:
                for i in range(len(points) - 1):
                    alpha = int(220 * (1 - i / len(points)))
                    spiral_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(spiral_surf, (*color, alpha), points[i], points[i + 1], 3)
                    s.blit(spiral_surf, (0, 0))
        
        # 色彩粒子漩涡
        for particle in range(30):
            p_angle = (particle / 30) * math.pi * 2 + t * 3
            p_dist = 15 + (particle % 10) * 3
            px = 60 + math.cos(p_angle) * p_dist
            py = 50 + math.sin(p_angle) * p_dist
            
            # 粒子颜色随位置变化
            particle_hue = ((particle / 30) + t * 0.5) % 1
            h = particle_hue * 6
            if h < 1:
                pr, pg, pb = 255, int(255 * (h % 1)), 0
            elif h < 2:
                pr, pg, pb = int(255 * (1 - h % 1)), 255, 0
            elif h < 3:
                pr, pg, pb = 0, 255, int(255 * (h % 1))
            elif h < 4:
                pr, pg, pb = 0, int(255 * (1 - h % 1)), 255
            elif h < 5:
                pr, pg, pb = int(255 * (h % 1)), 0, 255
            else:
                pr, pg, pb = 255, 0, int(255 * (1 - h % 1))
            
            pygame.draw.circle(s, (pr, pg, pb), (int(px), int(py)), 3)
        
        # 彩虹环（扩散波）
        for wave in range(4):
            wave_progress = (t * 2 + wave * 0.3) % 1
            wave_radius = int(20 + wave_progress * 40)
            wave_alpha = int(180 * (1 - wave_progress))
            
            if wave_alpha > 30:
                # 彩虹分段
                for arc_seg in range(12):
                    arc_hue = ((arc_seg / 12) + t * 0.3) % 1
                    h = arc_hue * 6
                    if h < 3:
                        ar = int(255 * max(0, 1 - abs(h - 1)))
                        ag = int(255 * max(0, 1 - abs(h - 2)))
                        ab = int(255 * max(0, 1 - abs(h)))
                    else:
                        ar = int(255 * max(0, 1 - abs(h - 5)))
                        ag = int(255 * max(0, 1 - abs(h - 6)))
                        ab = int(255 * max(0, 1 - abs(h - 4)))
                    
                    arc_start = arc_seg * math.pi / 6
                    arc_end = (arc_seg + 1) * math.pi / 6
                    arc_points = []
                    for arc_step in range(5):
                        arc_angle = arc_start + (arc_end - arc_start) * (arc_step / 4)
                        ax = 60 + math.cos(arc_angle) * wave_radius
                        ay = 50 + math.sin(arc_angle) * wave_radius
                        arc_points.append((int(ax), int(ay)))
                    
                    if len(arc_points) > 1:
                        wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                        pygame.draw.lines(wave_surf, (ar, ag, ab, wave_alpha), False, arc_points, 3)
                        s.blit(wave_surf, (0, 0))
        
        return s
    
    elif model_style == "titan_ex4":
        # 熔岩巨兽 - 地核之怒
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 熔岩裂缝网络（像地壳裂开）
        crack_lines = 8
        for crack in range(crack_lines):
            crack_angle = crack * math.pi / 4 + math.sin(t * 0.5) * 0.2
            
            # 裂缝主干
            crack_points = [(60, 50)]
            segments = 8
            for seg in range(1, segments + 1):
                seg_dist = seg * 6
                seg_angle = crack_angle + (random.random() - 0.5) * 0.3
                seg_x = 60 + math.cos(seg_angle) * seg_dist
                seg_y = 50 + math.sin(seg_angle) * seg_dist
                crack_points.append((int(seg_x), int(seg_y)))
            
            # 裂缝发光（从内部发出红光）
            for i in range(len(crack_points) - 1):
                glow_intensity = 1 - (i / len(crack_points))
                glow_brightness = int(200 * glow_intensity)
                
                # 多层发光
                for glow_layer in range(3):
                    glow_width = 6 - glow_layer * 2
                    glow_alpha = int(220 * glow_intensity - glow_layer * 40)
                    if glow_alpha > 30:
                        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                        # 颜色从白到黄到橙到红
                        if glow_layer == 0:
                            glow_color = (255, 255, 200)
                        elif glow_layer == 1:
                            glow_color = (255, glow_brightness, 50)
                        else:
                            glow_color = (glow_brightness, 50, 0)
                        
                        pygame.draw.line(glow_surf, (*glow_color, glow_alpha),
                                       crack_points[i], crack_points[i + 1], glow_width)
                        s.blit(glow_surf, (0, 0))
        
        # 熔岩气泡（上升）
        for bubble in range(15):
            bubble_progress = (t * 1.5 + bubble * 0.2) % 1
            bubble_angle = bubble * 0.6 + math.sin(t + bubble) * 0.3
            bubble_start_dist = 10
            bubble_dist = bubble_start_dist + bubble_progress * 40
            bx = 60 + math.cos(bubble_angle) * bubble_dist
            by = 50 + math.sin(bubble_angle) * bubble_dist
            
            # 气泡大小随上升而增大
            bubble_size = int(3 + bubble_progress * 5)
            bubble_alpha = int(220 * (1 - bubble_progress))
            
            if bubble_alpha > 30:
                # 橙红色气泡
                pygame.draw.circle(s, (255, 100 + int(100 * (1 - bubble_progress)), 0, bubble_alpha),
                                 (int(bx), int(by)), bubble_size)
                # 气泡边缘更亮
                pygame.draw.circle(s, (255, 200, 100, bubble_alpha), (int(bx), int(by)), bubble_size, 1)
        
        # 岩浆脉动（中心）
        pulse_intensity = (math.sin(t * 2.5) + 1) / 2
        for pulse_ring in range(5, 0, -1):
            pulse_radius = int(15 * pulse_intensity * (pulse_ring / 5))
            pulse_brightness = int(200 + 55 * pulse_intensity)
            pulse_color = (255, pulse_brightness // 2, 0)
            pygame.draw.circle(s, pulse_color, (60, 50), pulse_radius)
        
        # 火星飞溅
        for spark in range(20):
            if (int(t * 10) + spark) % 7 < 3:
                spark_angle = spark * 0.5 + t * 3
                spark_dist = 20 + 30 * random.random()
                spark_x = 60 + math.cos(spark_angle) * spark_dist
                spark_y = 50 + math.sin(spark_angle) * spark_dist
                spark_brightness = int(200 + 55 * random.random())
                
                # 小火星
                pygame.draw.circle(s, (255, spark_brightness, 0), (int(spark_x), int(spark_y)), 2)
        
        # 热浪扭曲（环形波）
        for heat_ring in range(3):
            heat_progress = (t * 1.5 + heat_ring * 0.4) % 1
            heat_radius = int(20 + heat_progress * 35)
            heat_alpha = int(150 * (1 - heat_progress))
            
            if heat_alpha > 30:
                # 扭曲的圆环
                heat_points = []
                for i in range(16):
                    heat_angle = i * math.pi / 8
                    distortion = 5 * math.sin(t * 3 + i + heat_ring)
                    hx = 60 + math.cos(heat_angle) * (heat_radius + distortion)
                    hy = 50 + math.sin(heat_angle) * (heat_radius + distortion)
                    heat_points.append((int(hx), int(hy)))
                
                if len(heat_points) > 2:
                    heat_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.polygon(heat_surf, (255, 150, 50, heat_alpha), heat_points, 2)
                    s.blit(heat_surf, (0, 0))
        
        return s
    
    elif model_style == "thunderbird_ex4":
        # 等离子生命 - 电弧之魂
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 等离子球（核心）
        plasma_core_radius = int(10 + 5 * math.sin(t * 3))
        for core_layer in range(5, 0, -1):
            layer_radius = int(plasma_core_radius * (core_layer / 5))
            layer_alpha = 255
            # 从青蓝到白的渐变
            layer_brightness = int(100 + 155 * (core_layer / 5))
            core_color = (layer_brightness, 255, 255)
            pygame.draw.circle(s, core_color, (60, 50), layer_radius)
        
        # 闪电分叉（随机生成）
        lightning_branches = 6
        for branch in range(lightning_branches):
            # 主闪电路径
            branch_angle = branch * math.pi / 3 + t * 2
            
            # 闪电节点
            lightning_points = [(60, 50)]
            current_x, current_y = 60, 50
            
            for seg in range(6):
                # 随机偏移
                seg_angle = branch_angle + (random.random() - 0.5) * 0.8
                seg_dist = 8 + random.random() * 5
                current_x += math.cos(seg_angle) * seg_dist
                current_y += math.sin(seg_angle) * seg_dist
                lightning_points.append((int(current_x), int(current_y)))
            
            # 绘制闪电
            for i in range(len(lightning_points) - 1):
                # 闪烁效果
                if (int(t * 20) + branch) % 5 < 4:
                    lightning_brightness = int(200 + 55 * random.random())
                    
                    # 多层闪电
                    for layer in range(3):
                        layer_width = 4 - layer
                        layer_alpha = 255 - layer * 70
                        lightning_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                        
                        if layer == 0:
                            lightning_color = (255, 255, 255)
                        elif layer == 1:
                            lightning_color = (lightning_brightness, 255, 255)
                        else:
                            lightning_color = (100, lightning_brightness, 255)
                        
                        pygame.draw.line(lightning_surf, (*lightning_color, layer_alpha),
                                       lightning_points[i], lightning_points[i + 1], layer_width)
                        s.blit(lightning_surf, (0, 0))
                
                # 小分支
                if random.random() < 0.3:
                    sub_angle = branch_angle + (random.random() - 0.5) * 1.5
                    sub_dist = 10
                    sub_x = lightning_points[i][0] + int(math.cos(sub_angle) * sub_dist)
                    sub_y = lightning_points[i][1] + int(math.sin(sub_angle) * sub_dist)
                    
                    if (int(t * 20) + i) % 6 < 4:
                        pygame.draw.line(s, (150, 255, 255),
                                       lightning_points[i], (sub_x, sub_y), 2)
        
        # 电弧粒子环绕
        for particle in range(25):
            p_angle = particle * 0.4 + t * 4
            p_dist = 20 + 15 * math.sin(t * 2 + particle * 0.3)
            px = 60 + math.cos(p_angle) * p_dist
            py = 50 + math.sin(p_angle) * p_dist
            
            # 粒子闪烁
            if (int(t * 15) + particle) % 4 < 3:
                particle_brightness = int(200 + 55 * math.sin(t * 6 + particle))
                pygame.draw.circle(s, (particle_brightness, 255, 255), (int(px), int(py)), 2)
        
        # 电磁场波动
        for field_wave in range(4):
            wave_progress = (t * 2.5 + field_wave * 0.3) % 1
            wave_radius = int(15 + wave_progress * 40)
            wave_alpha = int(200 * (1 - wave_progress))
            
            if wave_alpha > 30:
                # 波动不规则
                wave_points = []
                for i in range(12):
                    wave_angle = i * math.pi / 6
                    distortion = 5 * math.sin(t * 4 + i + field_wave)
                    wx = 60 + math.cos(wave_angle) * (wave_radius + distortion)
                    wy = 50 + math.sin(wave_angle) * (wave_radius + distortion)
                    wave_points.append((int(wx), int(wy)))
                
                if len(wave_points) > 2:
                    field_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.lines(field_surf, (100, 255, 255, wave_alpha), True, wave_points, 2)
                    s.blit(field_surf, (0, 0))
        
        # 电离气体云
        for gas_particle in range(30):
            gas_angle = gas_particle * 0.3
            gas_dist = 10 + 35 * random.random()
            gas_x = 60 + math.cos(gas_angle) * gas_dist
            gas_y = 50 + math.sin(gas_angle) * gas_dist
            gas_alpha = int(120 * (1 - (gas_dist - 10) / 35))
            
            if gas_alpha > 20:
                pygame.draw.circle(s, (150, 255, 255, gas_alpha), (int(gas_x), int(gas_y)), 2)
        
        return s
    elif model_style == "viper_ex4":
        # 生物荧光 - 深海幻影
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 荧光触手（像水母触手）
        tentacles = 8
        for tentacle in range(tentacles):
            tentacle_base_angle = tentacle * math.pi / 4
            
            # 触手节点
            tentacle_points = [(60, 50)]
            current_angle = tentacle_base_angle
            
            for segment in range(10):
                # 波动摆动
                wave = math.sin(t * 2 - segment * 0.3) * 0.3
                current_angle = tentacle_base_angle + wave
                segment_dist = (segment + 1) * 4
                tx = 60 + math.cos(current_angle) * segment_dist
                ty = 50 + math.sin(current_angle) * segment_dist
                tentacle_points.append((int(tx), int(ty)))
            
            # 绘制触手（渐变色）
            for i in range(len(tentacle_points) - 1):
                seg_progress = i / len(tentacle_points)
                # 青绿到蓝紫渐变
                seg_r = int(0 + 100 * seg_progress)
                seg_g = int(255 - 105 * seg_progress)
                seg_b = int(200 + 55 * seg_progress)
                seg_alpha = int(220 * (1 - seg_progress))
                seg_width = int(6 * (1 - seg_progress)) + 1
                
                if seg_alpha > 30:
                    tent_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(tent_surf, (seg_r, seg_g, seg_b, seg_alpha),
                                   tentacle_points[i], tentacle_points[i + 1], seg_width)
                    s.blit(tent_surf, (0, 0))
        
        # 荧光脉冲（从中心向外）
        pulse_waves = 5
        for wave in range(pulse_waves):
            wave_progress = (t * 1.5 + wave * 0.3) % 1
            wave_radius = int(10 + wave_progress * 45)
            wave_alpha = int(200 * (1 - wave_progress))
            
            if wave_alpha > 30:
                # 颜色随波动变化
                wave_hue_shift = wave_progress
                wave_r = int(0 + 100 * wave_hue_shift)
                wave_g = int(255 - 55 * wave_hue_shift)
                wave_b = int(200 + 55 * wave_hue_shift)
                
                wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(wave_surf, (wave_r, wave_g, wave_b, wave_alpha),
                                 (60, 50), wave_radius, 3)
                s.blit(wave_surf, (0, 0))
        
        # 荧光粒子漂浮
        for particle in range(40):
            # 粒子波动路径
            p_base_angle = particle * 0.4
            p_wave = math.sin(t * 2 + particle * 0.2) * 10
            p_dist = 15 + (particle % 8) * 4 + p_wave
            px = 60 + math.cos(p_base_angle) * p_dist
            py = 50 + math.sin(p_base_angle) * p_dist
            
            # 粒子闪烁
            p_brightness = (math.sin(t * 4 + particle * 0.5) + 1) / 2
            p_alpha = int(200 * p_brightness)
            p_size = 2 + int(2 * p_brightness)
            
            # 青绿荧光
            if p_alpha > 30:
                pygame.draw.circle(s, (0, 255, 200, p_alpha), (int(px), int(py)), p_size)
        
        # 中心荧光核（像水母伞部）
        core_radius = int(12 + 5 * math.sin(t * 2))
        for core_layer in range(4, 0, -1):
            layer_radius = int(core_radius * (core_layer / 4))
            layer_alpha = int(180 * (core_layer / 4))
            # 渐变：青色到蓝色
            layer_g = int(255 * (core_layer / 4))
            layer_b = int(200 + 55 * (1 - core_layer / 4))
            core_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(core_surf, (50, layer_g, layer_b, layer_alpha),
                             (60, 50), layer_radius)
            s.blit(core_surf, (0, 0))
        
        # 生物电流（螺旋）
        for spiral in range(3):
            spiral_offset = spiral * 2 * math.pi / 3
            spiral_points = []
            
            for step in range(15):
                step_prog = step / 15
                spiral_angle = spiral_offset + step_prog * math.pi * 4 + t * 2
                spiral_radius = 15 + step_prog * 30
                sx = 60 + math.cos(spiral_angle) * spiral_radius
                sy = 50 + math.sin(spiral_angle) * spiral_radius
                spiral_points.append((int(sx), int(sy)))
            
            # 绘制螺旋
            for i in range(len(spiral_points) - 1):
                alpha = int(150 * (1 - i / len(spiral_points)))
                if alpha > 30:
                    spiral_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(spiral_surf, (100, 255, 220, alpha),
                                   spiral_points[i], spiral_points[i + 1], 2)
                    s.blit(spiral_surf, (0, 0))
        
        return s
    
    elif model_style == "specter_ex4":
        # 全息投影 - 数据流动
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 扫描线效果
        scan_lines = 15
        for scan in range(scan_lines):
            scan_y = int((t * 80 + scan * 8) % 120)
            scan_alpha = int(150 * (math.sin(t * 3 + scan) + 1) / 2)
            
            if scan_alpha > 30:
                scan_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(scan_surf, (0, 255, 255, scan_alpha),
                               (10, scan_y), (110, scan_y), 1)
                s.blit(scan_surf, (0, 0))
        
        # 数据流粒子（二进制）
        data_particles = 50
        for dp in range(data_particles):
            dp_x = 20 + (dp % 10) * 10
            dp_progress = (t * 2 + dp * 0.1) % 1
            dp_y = 10 + dp_progress * 100
            dp_alpha = int(200 * (1 - abs(dp_progress - 0.5) * 2))
            
            if dp_alpha > 30:
                # 二进制位（0或1）
                dp_value = (int(t * 10) + dp) % 2
                dp_color = (0, 255, 255) if dp_value == 1 else (255, 0, 255)
                pygame.draw.circle(s, (*dp_color, dp_alpha), (dp_x, int(dp_y)), 2)
        
        # 全息网格（三维投影）
        grid_layers = 4
        for layer in range(grid_layers):
            layer_depth = layer / grid_layers
            layer_scale = 0.5 + layer_depth * 0.5
            layer_offset_y = int(layer * 5 * math.sin(t + layer))
            layer_alpha = int(120 + 80 * layer_depth)
            
            # 网格线
            grid_size = 4
            for gx in range(grid_size + 1):
                # 垂直线
                x_pos = int(30 + gx * 15 * layer_scale)
                y_start = int(30 + layer_offset_y)
                y_end = int(70 + layer_offset_y)
                
                grid_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(grid_surf, (100, 200, 255, layer_alpha),
                               (x_pos, y_start), (x_pos, y_end), 1)
                s.blit(grid_surf, (0, 0))
            
            for gy in range(grid_size + 1):
                # 水平线
                y_pos = int(30 + gy * 10 * layer_scale + layer_offset_y)
                x_start = int(30)
                x_end = int(30 + grid_size * 15 * layer_scale)
                
                grid_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(grid_surf, (100, 200, 255, layer_alpha),
                               (x_start, y_pos), (x_end, y_pos), 1)
                s.blit(grid_surf, (0, 0))
        
        # 像素化重构效果
        pixel_blocks = 12
        for block in range(pixel_blocks):
            # 随机出现的像素块
            if (int(t * 5) + block) % 8 < 5:
                block_angle = block * 0.5
                block_dist = 20 + (block % 4) * 8
                block_x = int(60 + math.cos(block_angle) * block_dist)
                block_y = int(50 + math.sin(block_angle) * block_dist)
                block_size = 6
                
                # 青色和品红交替
                block_color = (0, 255, 255) if block % 2 == 0 else (255, 0, 255)
                block_alpha = int(180 * ((math.sin(t * 4 + block) + 1) / 2))
                
                if block_alpha > 30:
                    block_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    block_rect = pygame.Rect(block_x - block_size // 2,
                                            block_y - block_size // 2,
                                            block_size, block_size)
                    pygame.draw.rect(block_surf, (*block_color, block_alpha), block_rect)
                    pygame.draw.rect(block_surf, (255, 255, 255, block_alpha), block_rect, 1)
                    s.blit(block_surf, (0, 0))
        
        # 中心全息核心
        holo_core_radius = int(15 + 5 * math.sin(t * 2.5))
        for holo_ring in range(3):
            ring_radius = holo_core_radius + holo_ring * 8
            ring_alpha = int(150 - holo_ring * 40)
            holo_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 青蓝色
            pygame.draw.circle(holo_surf, (0, 200, 255, ring_alpha), (60, 50), ring_radius, 2)
            s.blit(holo_surf, (0, 0))
        
        # 数据流螺旋
        data_stream_points = []
        for stream_step in range(20):
            stream_prog = stream_step / 20
            stream_angle = stream_prog * math.pi * 6 + t * 3
            stream_radius = 10 + stream_prog * 35
            stream_x = 60 + math.cos(stream_angle) * stream_radius
            stream_y = 50 + math.sin(stream_angle) * stream_radius
            data_stream_points.append((int(stream_x), int(stream_y)))
        
        # 绘制数据流
        for i in range(len(data_stream_points) - 1):
            stream_alpha = int(180 * (1 - i / len(data_stream_points)))
            if stream_alpha > 30:
                stream_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                stream_color = (0, 255, 255) if i % 2 == 0 else (255, 0, 255)
                pygame.draw.line(stream_surf, (*stream_color, stream_alpha),
                               data_stream_points[i], data_stream_points[i + 1], 2)
                s.blit(stream_surf, (0, 0))
        
        return s
    
    elif model_style == "aurora_ex4":
        # 蝴蝶效应 - 混沌之翼
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 蝴蝶翅膀形状（洛伦兹吸引子投影）
        wing_points_left = []
        wing_points_right = []
        
        # 使用混沌方程生成翅膀轨迹
        for step in range(30):
            step_prog = step / 30
            # 简化的混沌轨迹
            chaos_x = 20 * math.sin(step_prog * math.pi * 4 + t * 2) * step_prog
            chaos_y = 25 * math.sin(step_prog * math.pi * 2 + t) * (1 - step_prog)
            
            # 左翼
            left_x = int(60 - 10 - chaos_x)
            left_y = int(50 + chaos_y)
            wing_points_left.append((left_x, left_y))
            
            # 右翼（镜像）
            right_x = int(60 + 10 + chaos_x)
            right_y = int(50 + chaos_y)
            wing_points_right.append((right_x, right_y))
        
        # 绘制翅膀（渐变色彩）
        for i in range(len(wing_points_left) - 1):
            color_prog = i / len(wing_points_left)
            # 彩虹渐变
            if color_prog < 0.33:
                wing_r = int(255 * (1 - color_prog / 0.33))
                wing_g = int(255 * (color_prog / 0.33))
                wing_b = 150
            elif color_prog < 0.67:
                wing_r = 150
                wing_g = int(255 * (1 - (color_prog - 0.33) / 0.34))
                wing_b = int(255 * ((color_prog - 0.33) / 0.34))
            else:
                wing_r = int(255 * ((color_prog - 0.67) / 0.33))
                wing_g = 150
                wing_b = int(255 * (1 - (color_prog - 0.67) / 0.33))
            
            wing_alpha = int(200 * (1 - color_prog * 0.5))
            
            # 左翼
            wing_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(wing_surf, (wing_r, wing_g, wing_b, wing_alpha),
                           wing_points_left[i], wing_points_left[i + 1], 4)
            s.blit(wing_surf, (0, 0))
            
            # 右翼
            wing_surf2 = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(wing_surf2, (wing_r, wing_g, wing_b, wing_alpha),
                           wing_points_right[i], wing_points_right[i + 1], 4)
            s.blit(wing_surf2, (0, 0))
        
        # 翅膀上的斑点（随机生成）
        random.seed(int(t * 2))  # 半随机
        for spot in range(20):
            spot_side = spot % 2
            spot_prog = (spot // 2) / 10
            
            # 斑点位置
            base_x = 60 + (-25 if spot_side == 0 else 25)
            base_y = 50
            offset_x = int((random.random() - 0.5) * 30 * spot_prog)
            offset_y = int((random.random() - 0.5) * 40 * (1 - spot_prog))
            spot_x = base_x + offset_x
            spot_y = base_y + offset_y
            
            # 斑点颜色（随机）
            spot_colors = [
                (255, 100, 150),
                (150, 200, 255),
                (200, 255, 100),
                (255, 200, 100),
                (150, 100, 255)
            ]
            spot_color = spot_colors[spot % len(spot_colors)]
            spot_size = 3 + int(3 * random.random())
            spot_alpha = int(180 * (1 - spot_prog * 0.5))
            
            if spot_alpha > 30:
                pygame.draw.circle(s, (*spot_color, spot_alpha), (spot_x, spot_y), spot_size)
        
        random.seed()  # 重置随机种子
        
        # 混沌轨迹（粒子流）
        for particle in range(25):
            p_progress = (t * 2 + particle * 0.1) % 1
            # 混沌轨迹
            p_x = 60 + 35 * math.sin(p_progress * math.pi * 6 + particle * 0.3)
            p_y = 50 + 30 * math.cos(p_progress * math.pi * 4 + particle * 0.2)
            p_alpha = int(180 * (1 - p_progress))
            
            if p_alpha > 30:
                # 彩色粒子
                p_hue = (p_progress + particle / 25) % 1
                if p_hue < 0.5:
                    p_color = (255, int(255 * (p_hue * 2)), int(255 * (1 - p_hue * 2)))
                else:
                    p_color = (int(255 * (1 - (p_hue - 0.5) * 2)), int(255 * ((p_hue - 0.5) * 2)), 255)
                
                pygame.draw.circle(s, (*p_color, p_alpha), (int(p_x), int(p_y)), 2)
        
        # 蝴蝶身体
        body_segments = 5
        for seg in range(body_segments):
            seg_y = 35 + seg * 6
            seg_width = 4 - seg // 2
            pygame.draw.circle(s, (50, 50, 80), (60, seg_y), seg_width)
        
        # 触角
        for antenna in [-1, 1]:
            antenna_points = [(60, 35)]
            for ant_seg in range(5):
                ant_prog = ant_seg / 5
                ant_angle = -math.pi / 2 + antenna * (math.pi / 6 + ant_prog * math.pi / 6)
                ant_x = 60 + antenna * 5 + math.cos(ant_angle) * ant_prog * 12
                ant_y = 35 - math.sin(ant_angle) * ant_prog * 12
                antenna_points.append((int(ant_x), int(ant_y)))
            
            if len(antenna_points) > 1:
                pygame.draw.lines(s, (80, 80, 120), False, antenna_points, 2)
        
        return s
    elif model_style == "crimson_ex4":
        # 烟火绽放 - 庆典之舞
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 烟花爆炸点（多个）
        fireworks = 5
        for fw in range(fireworks):
            # 每个烟花的爆炸进度
            fw_progress = ((t * 1.5 + fw * 0.4) % 1)
            fw_angle_offset = fw * 1.3
            fw_x = 60 + int(25 * math.cos(fw_angle_offset))
            fw_y = 50 + int(25 * math.sin(fw_angle_offset))
            
            # 烟花粒子
            if fw_progress < 0.8:
                particle_count = 16
                for particle in range(particle_count):
                    particle_angle = (particle / particle_count) * math.pi * 2
                    particle_dist = fw_progress * 30
                    px = fw_x + int(math.cos(particle_angle) * particle_dist)
                    py = fw_y + int(math.sin(particle_angle) * particle_dist)
                    
                    # 粒子颜色（随烟花变化）
                    if fw % 3 == 0:
                        p_color = (255, int(100 + 155 * (1 - fw_progress)), 100)
                    elif fw % 3 == 1:
                        p_color = (int(100 + 155 * (1 - fw_progress)), 255, 100)
                    else:
                        p_color = (100, int(100 + 155 * (1 - fw_progress)), 255)
                    
                    p_alpha = int(250 * (1 - fw_progress))
                    p_size = int(4 * (1 - fw_progress)) + 1
                    
                    if p_alpha > 30:
                        pygame.draw.circle(s, (*p_color, p_alpha), (px, py), p_size)
                        # 拖尾
                        trail_len = int(5 * (1 - fw_progress))
                        trail_x = fw_x + int(math.cos(particle_angle) * (particle_dist - trail_len))
                        trail_y = fw_y + int(math.sin(particle_angle) * (particle_dist - trail_len))
                        trail_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                        pygame.draw.line(trail_surf, (*p_color, p_alpha // 2),
                                       (trail_x, trail_y), (px, py), 2)
                        s.blit(trail_surf, (0, 0))
        
        # 持续的火花雨
        for spark in range(30):
            spark_progress = (t * 2 + spark * 0.1) % 1
            spark_x = 30 + (spark % 10) * 9
            spark_y = -10 + spark_progress * 130
            spark_alpha = int(200 * (1 - spark_progress))
            
            if spark_alpha > 30 and spark_y < 110:
                spark_colors = [(255, 50, 100), (255, 200, 50), (100, 150, 255)]
                spark_color = spark_colors[spark % 3]
                pygame.draw.circle(s, (*spark_color, spark_alpha), (spark_x, int(spark_y)), 2)
        
        return s
    
    elif model_style == "stalker_ex4":
        # 迷幻漩涡 - 催眠螺旋
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 多层旋转螺旋
        spiral_layers = 6
        for layer in range(spiral_layers):
            layer_rotation = t * (1 + layer * 0.3)
            layer_radius_start = 5 + layer * 8
            
            # 螺旋线
            spiral_points = []
            segments = 30
            for seg in range(segments):
                seg_prog = seg / segments
                seg_angle = layer_rotation + seg_prog * math.pi * 6
                seg_radius = layer_radius_start + seg_prog * 30
                sx = 60 + int(math.cos(seg_angle) * seg_radius)
                sy = 50 + int(math.sin(seg_angle) * seg_radius)
                spiral_points.append((sx, sy))
            
            # 颜色渐变（紫色到青色）
            for i in range(len(spiral_points) - 1):
                color_prog = i / len(spiral_points)
                r = int(255 * (1 - color_prog))
                g = int(100 + 155 * color_prog)
                b = 255
                alpha = int(180 - layer * 25)
                
                if alpha > 30:
                    spiral_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(spiral_surf, (r, g, b, alpha),
                                   spiral_points[i], spiral_points[i + 1], 3)
                    s.blit(spiral_surf, (0, 0))
        
        # 催眠环
        ring_count = 8
        for ring in range(ring_count):
            ring_progress = (t + ring * 0.2) % 1
            ring_radius = int(10 + ring_progress * 45)
            ring_alpha = int(200 * (1 - ring_progress))
            
            if ring_alpha > 30:
                ring_hue = (ring / ring_count + t * 0.3) % 1
                if ring_hue < 0.5:
                    ring_color = (255, int(255 * ring_hue * 2), 255)
                else:
                    ring_color = (int(255 * (1 - (ring_hue - 0.5) * 2)), 255, 255)
                
                ring_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (*ring_color, ring_alpha), (60, 50), ring_radius, 2)
                s.blit(ring_surf, (0, 0))
        
        return s
    
    elif model_style == "gaia_ex4":
        # 万花筒梦境 - 镜像迷宫
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 万花筒对称（6重对称）
        symmetry = 6
        for sym in range(symmetry):
            base_angle = sym * math.pi * 2 / symmetry + t
            
            # 对称图案元素
            for element in range(5):
                elem_dist = 15 + element * 8
                elem_angle = base_angle + element * 0.5
                ex = 60 + int(math.cos(elem_angle) * elem_dist)
                ey = 50 + int(math.sin(elem_angle) * elem_dist)
                
                # 颜色循环
                color_index = (sym + element) % 3
                if color_index == 0:
                    elem_color = (255, 180, 100)
                elif color_index == 1:
                    elem_color = (100, 180, 255)
                else:
                    elem_color = (180, 255, 100)
                
                elem_size = 6 - element
                pygame.draw.circle(s, elem_color, (ex, ey), elem_size)
                
                # 连接到中心
                line_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(line_surf, (*elem_color, 150), (60, 50), (ex, ey), 1)
                s.blit(line_surf, (0, 0))
        
        # 旋转的几何形状
        shape_rotation = t * 2
        shape_sides = 6
        shape_radius = 20
        shape_points = []
        for i in range(shape_sides):
            angle = shape_rotation + i * math.pi * 2 / shape_sides
            px = 60 + int(math.cos(angle) * shape_radius)
            py = 50 + int(math.sin(angle) * shape_radius)
            shape_points.append((px, py))
        
        if len(shape_points) > 2:
            pygame.draw.polygon(s, (200, 200, 255, 180), shape_points, 3)
        
        return s
    
    elif model_style == "weaver_ex4":
        # 波动艺术 - 声波可视
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 波形（类似音频波形）
        waveforms = 4
        for wave in range(waveforms):
            wave_y_base = 30 + wave * 20
            wave_points = []
            
            for x in range(120):
                # 多重频率叠加
                y_offset = 0
                y_offset += 8 * math.sin((x / 10 + t * 3) * math.pi)
                y_offset += 4 * math.sin((x / 5 + t * 5) * math.pi * 2)
                y_offset += 2 * math.sin((x / 3 + t * 7) * math.pi * 3)
                
                y = int(wave_y_base + y_offset)
                wave_points.append((x, y))
            
            # 颜色渐变
            if wave == 0:
                wave_color = (100, 255, 150)
            elif wave == 1:
                wave_color = (255, 150, 100)
            elif wave == 2:
                wave_color = (150, 100, 255)
            else:
                wave_color = (255, 255, 100)
            
            if len(wave_points) > 1:
                wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(wave_surf, (*wave_color, 200), False, wave_points, 2)
                s.blit(wave_surf, (0, 0))
        
        # 频率指示器
        for freq_bar in range(10):
            bar_x = 20 + freq_bar * 10
            bar_height = int(20 + 20 * abs(math.sin(t * 4 + freq_bar * 0.5)))
            bar_rect = pygame.Rect(bar_x, 90 - bar_height, 6, bar_height)
            
            bar_color_val = int(100 + 155 * abs(math.sin(t * 3 + freq_bar)))
            pygame.draw.rect(s, (100, bar_color_val, 255), bar_rect)
        
        return s
    
    elif model_style == "solar_ex4":
        # 极光风暴 - 磁暴舞曲
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 极光带（波动的彩色丝带）
        aurora_bands = 5
        for band in range(aurora_bands):
            band_y_base = 30 + band * 15
            band_points = []
            
            for x in range(0, 121, 3):
                wave_y = band_y_base + int(15 * math.sin((x / 15 + t * 2 + band) * math.pi))
                band_points.append((x, wave_y))
            
            # 极光颜色（绿到紫渐变）
            band_prog = band / aurora_bands
            if band_prog < 0.33:
                band_r = int(255 * band_prog / 0.33)
                band_g = 255
                band_b = 150
            elif band_prog < 0.67:
                band_r = 255
                band_g = int(255 * (1 - (band_prog - 0.33) / 0.34))
                band_b = int(150 + 105 * (band_prog - 0.33) / 0.34)
            else:
                band_r = int(255 * (1 - (band_prog - 0.67) / 0.33))
                band_g = 150
                band_b = 255
            
            # 绘制极光带（带透明度）
            for i in range(len(band_points) - 1):
                aurora_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                alpha = int(180 + 75 * math.sin(t * 3 + i * 0.1 + band))
                pygame.draw.line(aurora_surf, (band_r, band_g, band_b, alpha),
                               band_points[i], band_points[i + 1], 4)
                s.blit(aurora_surf, (0, 0))
        
        # 磁场粒子
        for particle in range(40):
            p_angle = particle * 0.3 + t * 2
            p_dist = 20 + int(15 * math.sin(t * 3 + particle * 0.2))
            px = 60 + int(math.cos(p_angle) * p_dist)
            py = 50 + int(math.sin(p_angle) * p_dist)
            
            p_colors = [(0, 255, 150), (150, 0, 255), (255, 150, 0)]
            p_color = p_colors[particle % 3]
            pygame.draw.circle(s, p_color, (px, py), 2)
        
        return s
    
    elif model_style == "arbiter_ex4":
        # 水墨丹青 - 墨滴扩散
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 墨滴扩散（从中心）
        ink_drops = 6
        for drop in range(ink_drops):
            drop_progress = ((t + drop * 0.3) % 1.5) / 1.5
            
            if drop_progress < 1:
                # 墨迹边缘（不规则）
                ink_points = []
                segments = 20
                for seg in range(segments):
                    seg_angle = seg * math.pi * 2 / segments
                    # 不规则边缘
                    radius_var = 1 + 0.3 * math.sin(seg * 2 + drop * 3)
                    ink_radius = drop_progress * 40 * radius_var
                    ix = 60 + int(math.cos(seg_angle) * ink_radius)
                    iy = 50 + int(math.sin(seg_angle) * ink_radius)
                    ink_points.append((ix, iy))
                
                # 墨色渐变（深到浅）
                ink_darkness = int(80 * (1 - drop_progress * 0.7))
                ink_alpha = int(200 * (1 - drop_progress))
                
                if ink_alpha > 20 and len(ink_points) > 2:
                    ink_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.polygon(ink_surf, (ink_darkness, ink_darkness, ink_darkness + 30, ink_alpha),
                                      ink_points)
                    s.blit(ink_surf, (0, 0))
        
        # 笔触（飘逸的线条）
        for stroke in range(4):
            stroke_angle = stroke * math.pi / 2 + t * 0.5
            stroke_points = []
            
            for seg in range(8):
                seg_prog = seg / 8
                seg_dist = 15 + seg_prog * 25
                seg_angle = stroke_angle + math.sin(t * 2 + seg) * 0.3
                sx = 60 + int(math.cos(seg_angle) * seg_dist)
                sy = 50 + int(math.sin(seg_angle) * seg_dist)
                stroke_points.append((sx, sy))
            
            # 绘制笔触
            for i in range(len(stroke_points) - 1):
                width = int(5 * (1 - i / len(stroke_points)))
                alpha = int(180 * (1 - i / len(stroke_points)))
                if alpha > 30:
                    stroke_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.line(stroke_surf, (50, 50, 80, alpha),
                                   stroke_points[i], stroke_points[i + 1], width)
                    s.blit(stroke_surf, (0, 0))
        
        return s
    
    elif model_style == "eclipse_ex4":
        # 霓虹都市 - 赛博脉动
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 霓虹灯管（垂直线条）
        neon_tubes = 12
        for tube in range(neon_tubes):
            tube_x = 15 + tube * 9
            tube_height = int(40 + 30 * abs(math.sin(t * 3 + tube * 0.5)))
            tube_y_start = 55 - tube_height // 2
            
            # 霓虹颜色交替
            if tube % 3 == 0:
                neon_color = (255, 0, 150)
            elif tube % 3 == 1:
                neon_color = (0, 255, 200)
            else:
                neon_color = (255, 200, 0)
            
            # 闪烁效果
            if (int(t * 10) + tube) % 6 < 5:
                # 外发光
                for glow in range(3, 0, -1):
                    glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    glow_alpha = int(180 - glow * 50)
                    pygame.draw.line(glow_surf, (*neon_color, glow_alpha),
                                   (tube_x, tube_y_start),
                                   (tube_x, tube_y_start + tube_height),
                                   glow * 2)
                    s.blit(glow_surf, (0, 0))
                
                # 核心
                pygame.draw.line(s, (255, 255, 255),
                               (tube_x, tube_y_start),
                               (tube_x, tube_y_start + tube_height), 2)
        
        # 赛博网格
        grid_lines = 8
        for grid in range(grid_lines):
            grid_y = 20 + grid * 12
            grid_alpha = int(100 + 100 * abs(math.sin(t * 2 + grid)))
            grid_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(grid_surf, (0, 255, 200, grid_alpha),
                           (10, grid_y), (110, grid_y), 1)
            s.blit(grid_surf, (0, 0))
        
        # 数据流粒子
        for data in range(20):
            data_progress = (t * 2 + data * 0.15) % 1
            data_x = 20 + int(data_progress * 80)
            data_y = 30 + (data % 5) * 15
            data_alpha = int(220 * (1 - abs(data_progress - 0.5) * 2))
            
            if data_alpha > 30:
                data_color = (255, 0, 150) if data % 2 == 0 else (0, 255, 200)
                pygame.draw.circle(s, (*data_color, data_alpha), (data_x, data_y), 2)
        
        return s
    
    elif model_style == "prism_ex4":
        # 油画笔触 - 印象流动
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 厚重笔触（梵高风格旋转）
        brush_strokes = 20
        for stroke in range(brush_strokes):
            stroke_angle = (stroke / brush_strokes) * math.pi * 2 + t * 0.5
            stroke_dist = 10 + (stroke % 4) * 10
            
            # 笔触中心
            stroke_cx = 60 + int(math.cos(stroke_angle) * stroke_dist)
            stroke_cy = 50 + int(math.sin(stroke_angle) * stroke_dist)
            
            # 笔触形状（短线段）
            stroke_length = 12
            stroke_dir = stroke_angle + math.pi / 2 + math.sin(t * 2 + stroke) * 0.5
            stroke_x1 = stroke_cx - int(math.cos(stroke_dir) * stroke_length / 2)
            stroke_y1 = stroke_cy - int(math.sin(stroke_dir) * stroke_length / 2)
            stroke_x2 = stroke_cx + int(math.cos(stroke_dir) * stroke_length / 2)
            stroke_y2 = stroke_cy + int(math.sin(stroke_dir) * stroke_length / 2)
            
            # 油画色彩（暖色调）
            color_var = (stroke / brush_strokes + t * 0.2) % 1
            if color_var < 0.33:
                stroke_color = (200, int(150 + 105 * color_var / 0.33), 100)
            elif color_var < 0.67:
                stroke_color = (int(200 - 100 * (color_var - 0.33) / 0.34), 255, 100)
            else:
                stroke_color = (100, int(255 - 105 * (color_var - 0.67) / 0.33), 200)
            
            # 绘制厚重笔触
            for layer in range(3):
                stroke_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                layer_alpha = 200 - layer * 50
                pygame.draw.line(stroke_surf, (*stroke_color, layer_alpha),
                               (stroke_x1, stroke_y1), (stroke_x2, stroke_y2), 5 - layer)
                s.blit(stroke_surf, (0, 0))
        
        # 旋转星空效果（中心）
        for star in range(15):
            star_angle = star * 0.8 + t * 2
            star_dist = 10 + int(15 * math.sin(t + star))
            star_x = 60 + int(math.cos(star_angle) * star_dist)
            star_y = 50 + int(math.sin(star_angle) * star_dist)
            
            star_brightness = int(150 + 105 * abs(math.sin(t * 3 + star)))
            pygame.draw.circle(s, (star_brightness, star_brightness, 200), (star_x, star_y), 3)
        
        return s
    
    elif model_style == "necro_ex4":
        # 黑洞漩涡 - 引力舞蹈
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        
        # 黑洞中心（纯黑）
        event_horizon = 12
        for layer in range(5, 0, -1):
            layer_radius = int(event_horizon * (layer / 5))
            layer_darkness = int(100 * (1 - layer / 5))
            pygame.draw.circle(s, (layer_darkness // 3, 0, layer_darkness),
                             (60, 50), layer_radius)
        
        # 吸积盘（螺旋向内）
        accretion_particles = 40
        for particle in range(accretion_particles):
            p_angle = particle * 0.5 + t * 3
            p_progress = (t + particle * 0.05) % 1
            # 螺旋向内
            p_dist = 50 * (1 - p_progress) + event_horizon
            px = 60 + int(math.cos(p_angle) * p_dist)
            py = 50 + int(math.sin(p_angle) * p_dist * 0.3)  # 扁平化
            
            # 颜色：外围蓝->内部红（温度）
            if p_progress < 0.3:
                p_color = (100, 100, 255)
            elif p_progress < 0.6:
                p_color = (200, 150, 255)
            else:
                p_color = (255, int(150 * (1 - p_progress)), 100)
            
            p_alpha = int(220 * (1 - p_progress * 0.5))
            p_size = int(4 * (1 - p_progress)) + 1
            
            if p_alpha > 30:
                pygame.draw.circle(s, (*p_color, p_alpha), (px, py), p_size)
        
        # 引力透镜（光线弯曲）
        lens_rings = 5
        for ring in range(lens_rings):
            ring_radius = event_horizon + 10 + ring * 8
            ring_alpha = int(150 - ring * 25)
            
            # 扭曲的环
            ring_points = []
            for i in range(16):
                ring_angle = i * math.pi / 8 + t
                distortion = 5 * math.sin(t * 2 + i + ring)
                rx = 60 + int(math.cos(ring_angle) * (ring_radius + distortion))
                ry = 50 + int(math.sin(ring_angle) * (ring_radius + distortion))
                ring_points.append((rx, ry))
            
            if ring_alpha > 20 and len(ring_points) > 2:
                lens_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.lines(lens_surf, (100, 0, 150, ring_alpha), True, ring_points, 2)
                s.blit(lens_surf, (0, 0))
        
        # 霍金辐射
        for radiation in range(12):
            rad_angle = radiation * 0.5 + t * 4
            rad_progress = (t * 2 + radiation * 0.2) % 1
            rad_dist = event_horizon + 3 + rad_progress * 35
            rad_x = 60 + int(math.cos(rad_angle) * rad_dist)
            rad_y = 50 + int(math.sin(rad_angle) * rad_dist)
            rad_alpha = int(200 * (1 - rad_progress))
            
            if rad_alpha > 30:
                pygame.draw.circle(s, (150, 100, 200, rad_alpha), (rad_x, rad_y), 2)
        
        return s

    elif model_style == "striker_ex5":  # 像素进化·8bit回忆
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        plane_size = (120, 120)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        pixel_size = int(abs(math.sin(t * 0.5)) * 15) + 3
        
        # 像素化效果
        for py in range(0, plane_size[1], pixel_size):
            for px in range(0, plane_size[0], pixel_size):
                color_phase = (px + py + t * 50) / 50.0
                r = int(128 + 127 * math.sin(color_phase))
                g = int(128 + 127 * math.sin(color_phase + 2.094))
                b = int(128 + 127 * math.sin(color_phase + 4.189))
                pygame.draw.rect(plane_surf, (r, g, b), (px, py, pixel_size, pixel_size))
        
        # 像素方块重组动画
        for i in range(25):
            angle = t * 2 + i * 0.25
            radius = 20 + math.sin(t + i * 0.5) * 10
            block_x = center[0] + math.cos(angle) * radius
            block_y = center[1] + math.sin(angle) * radius
            block_size = int(abs(math.sin(t * 2 + i)) * 8) + 4
            block_color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)][i % 4]
            pygame.draw.rect(plane_surf, block_color, (block_x - block_size//2, block_y - block_size//2, block_size, block_size), 2)
        return plane_surf

    elif model_style == "phantom_ex5":  # 表情包战士·颜文字
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 基础形状
        pygame.draw.circle(plane_surf, c, center, 45)
        pygame.draw.circle(plane_surf, edge_color, center, 45, 3)
        
        # 绘制表情（用简单图形模拟）
        for i in range(6):
            angle = t + i * 1.047
            radius = 25 + math.sin(t * 2 + i) * 8
            ex = center[0] + math.cos(angle) * radius
            ey = center[1] + math.sin(angle) * radius
            
            # 表情圆脸
            face_size = int(8 + abs(math.sin(t * 3 + i)) * 4)
            emoji_color = (255, int(200 + 55 * math.sin(t + i)), int(100 + 100 * math.cos(t + i)))
            pygame.draw.circle(plane_surf, emoji_color, (int(ex), int(ey)), face_size, 2)
            
            # 眼睛
            pygame.draw.circle(plane_surf, emoji_color, (int(ex - face_size//3), int(ey - face_size//4)), 2)
            pygame.draw.circle(plane_surf, emoji_color, (int(ex + face_size//3), int(ey - face_size//4)), 2)
            
            # 嘴巴（根据索引改变表情）
            if i % 3 == 0:  # 笑脸
                pygame.draw.arc(plane_surf, emoji_color, (ex - face_size//2, ey, face_size, face_size//2), 0, 3.14, 2)
            elif i % 3 == 1:  # 生气
                pygame.draw.line(plane_surf, emoji_color, (ex - face_size//2, ey + face_size//3), (ex + face_size//2, ey + face_size//3), 2)
            else:  # 惊讶
                pygame.draw.circle(plane_surf, emoji_color, (int(ex), int(ey + face_size//3)), face_size//4, 2)
        return plane_surf

    elif model_style == "titan_ex5":  # 几何变形·欧几里得
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        morph_phase = t % 4.0
        
        # 计算当前形状
        shape_idx = int(morph_phase)
        
        for layer in range(4):
            radius = 40 - layer * 8
            rotation = t + layer * 0.5
            
            if shape_idx == 0:
                sides = 3
            elif shape_idx == 1:
                sides = 4
            elif shape_idx == 2:
                sides = 5
            else:
                sides = 20
            
            # 绘制多边形
            points = []
            for i in range(sides):
                angle = rotation + (i / sides) * 2 * math.pi
                px = center[0] + math.cos(angle) * radius
                py = center[1] + math.sin(angle) * radius
                points.append((px, py))
            
            if len(points) >= 3:
                color_phase = t + layer * 0.5
                r = int(128 + 127 * math.sin(color_phase))
                g = int(128 + 127 * math.sin(color_phase + 2.094))
                b = int(128 + 127 * math.sin(color_phase + 4.189))
                pygame.draw.polygon(plane_surf, (r, g, b), points, 3)
        return plane_surf

    elif model_style == "thunderbird_ex5":  # 音游节奏·下落天堂
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 基础圆形
        pygame.draw.circle(plane_surf, c, center, 45)
        pygame.draw.circle(plane_surf, edge_color, center, 45, 3)
        
        # 轨道线
        track_count = 4
        track_width = 20
        for i in range(track_count):
            track_x = center[0] - track_width * 1.5 + i * track_width
            pygame.draw.line(plane_surf, (100, 100, 150), (track_x, center[1] - 30), (track_x, center[1] + 30), 1)
        
        # 下落音符
        for i in range(12):
            note_phase = (t * 3 + i * 0.3) % 1.0
            track_idx = i % track_count
            note_x = center[0] - track_width * 1.5 + track_idx * track_width
            note_y = center[1] - 30 + note_phase * 60
            
            note_type = i % 3
            if note_type == 0:
                note_color = (255, 100, 150)
                pygame.draw.circle(plane_surf, note_color, (int(note_x), int(note_y)), 4)
            elif note_type == 1:
                note_color = (100, 255, 150)
                pygame.draw.rect(plane_surf, note_color, (note_x - 3, note_y, 6, 15))
            else:
                note_color = (150, 100, 255)
                pygame.draw.polygon(plane_surf, note_color, [(note_x, note_y), (note_x - 5, note_y + 8), (note_x + 5, note_y + 8)])
            
            # Perfect判定特效
            if 0.85 < note_phase < 0.95:
                perfect_size = int((0.95 - note_phase) * 100)
                pygame.draw.circle(plane_surf, (255, 255, 100), (int(note_x), int(center[1] + 25)), perfect_size, 2)
        return plane_surf

    elif model_style == "viper_ex5":  # 魔法阵召唤·炼金术
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 外圈魔法阵
        for ring in range(3):
            ring_radius = 40 - ring * 10
            ring_rotation = t * (1 + ring * 0.5) * (-1 if ring % 2 else 1)
            
            pygame.draw.circle(plane_surf, (200, 150, 255), center, ring_radius, 2)
            
            # 符文符号
            rune_count = 6 + ring * 2
            for i in range(rune_count):
                angle = ring_rotation + (i / rune_count) * 2 * math.pi
                rx = center[0] + math.cos(angle) * ring_radius
                ry = center[1] + math.sin(angle) * ring_radius
                
                if i % 2 == 0:
                    points = [(rx, ry - 4), (rx - 3, ry + 2), (rx + 3, ry + 2)]
                    pygame.draw.polygon(plane_surf, (255, 200, 100), points)
                else:
                    points = [(rx, ry - 3), (rx + 3, ry), (rx, ry + 3), (rx - 3, ry)]
                    pygame.draw.polygon(plane_surf, (100, 255, 150), points)
        
        # 中心炼金符号
        center_size = int(8 + abs(math.sin(t * 2)) * 5)
        pygame.draw.circle(plane_surf, (255, 200, 100), center, center_size)
        pygame.draw.circle(plane_surf, (200, 150, 255), center, center_size, 2)
        
        # 召唤粒子从天而降
        for i in range(15):
            fall_phase = (t * 2 + i * 0.2) % 1.0
            px = center[0] + math.sin(t + i) * 25
            py = center[1] - 35 + fall_phase * 70
            particle_color = (200 + int(55 * math.sin(t + i)), 150, 255)
            pygame.draw.circle(plane_surf, particle_color, (int(px), int(py)), 3)
        return plane_surf

    elif model_style == "specter_ex5":  # 故障艺术·系统崩溃
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        glitch_intensity = abs(math.sin(t * 3))
        
        # RGB通道分离
        offset = int(glitch_intensity * 8)
        for i in range(3):
            shift_x = offset * (i - 1)
            shift_y = offset * (2 - i) if i % 2 else -offset
            
            for j in range(8):
                block_angle = t + j * 0.785
                block_radius = 20 + j * 3
                bx = center[0] + math.cos(block_angle) * block_radius + shift_x
                by = center[1] + math.sin(block_angle) * block_radius + shift_y
                
                if i == 0:
                    color = (255, 0, 0)
                elif i == 1:
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 255)
                
                pygame.draw.rect(plane_surf, color, (bx - 4, by - 4, 8, 8))
        
        # 画面撕裂线
        if glitch_intensity > 0.7:
            for i in range(5):
                tear_y = center[1] - 20 + i * 10
                tear_offset = int(glitch_intensity * 15 * math.sin(t * 10 + i))
                pygame.draw.line(plane_surf, (255, 255, 255), 
                               (center[0] - 30 + tear_offset, tear_y), 
                               (center[0] + 30 + tear_offset, tear_y), 2)
        
        # 数字乱码粒子
        for i in range(20):
            noise_x = center[0] + (hash((i, int(t * 10))) % 60) - 30
            noise_y = center[1] + (hash((i + 100, int(t * 10))) % 60) - 30
            noise_color = (255, 255, 255) if hash((i, int(t * 5))) % 2 else (0, 0, 0)
            pygame.draw.rect(plane_surf, noise_color, (noise_x, noise_y, 2, 2))
        return plane_surf

    elif model_style == "aurora_ex5":  # 折纸艺术·千纸鹤
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 基础圆形
        pygame.draw.circle(plane_surf, (255, 200, 200), center, 45, 3)
        
        # 纸鹤轮廓
        for crane_idx in range(6):
            angle = t + crane_idx * 1.047
            distance = 20 + abs(math.sin(t + crane_idx)) * 10
            crane_x = center[0] + math.cos(angle) * distance
            crane_y = center[1] + math.sin(angle) * distance
            
            crane_size = 8
            crane_color = (255, 180 + crane_idx * 10, 180 + crane_idx * 10)
            
            # 纸鹤身体
            body_points = [
                (crane_x, crane_y - crane_size),
                (crane_x - crane_size, crane_y + crane_size//2),
                (crane_x + crane_size, crane_y + crane_size//2)
            ]
            pygame.draw.polygon(plane_surf, crane_color, body_points, 2)
            
            # 翅膀
            wing1_points = [
                (crane_x - crane_size//2, crane_y),
                (crane_x - crane_size * 1.5, crane_y - crane_size//2),
                (crane_x - crane_size, crane_y + crane_size//2)
            ]
            pygame.draw.polygon(plane_surf, crane_color, wing1_points, 1)
            
            wing2_points = [
                (crane_x + crane_size//2, crane_y),
                (crane_x + crane_size * 1.5, crane_y - crane_size//2),
                (crane_x + crane_size, crane_y + crane_size//2)
            ]
            pygame.draw.polygon(plane_surf, crane_color, wing2_points, 1)
        
        # 折痕线动画
        for i in range(8):
            fold_angle = t * 2 + i * 0.393
            fold_radius = 35
            fx1 = center[0] + math.cos(fold_angle) * fold_radius
            fy1 = center[1] + math.sin(fold_angle) * fold_radius
            fx2 = center[0] - math.cos(fold_angle) * fold_radius
            fy2 = center[1] - math.sin(fold_angle) * fold_radius
            pygame.draw.line(plane_surf, (200, 200, 200), (fx1, fy1), (fx2, fy2), 1)
        return plane_surf

    elif model_style == "crimson_ex5":  # 弹幕地狱·东方幻想
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 基础形状
        pygame.draw.circle(plane_surf, c, center, 45)
        pygame.draw.circle(plane_surf, edge_color, center, 45, 3)
        
        # 弹幕图案1：圆形扩散
        pattern1_count = 16
        for i in range(pattern1_count):
            angle = (t * 2) + (i / pattern1_count) * 2 * math.pi
            bullet_phase = (t * 1.5) % 1.0
            radius = 10 + bullet_phase * 25
            bx = center[0] + math.cos(angle) * radius
            by = center[1] + math.sin(angle) * radius
            bullet_color = (255, 100 + int(100 * bullet_phase), 150)
            pygame.draw.circle(plane_surf, bullet_color, (int(bx), int(by)), 2)
        
        # 弹幕图案2：螺旋弹幕
        for i in range(30):
            spiral_angle = t * 3 + i * 0.3
            spiral_radius = 5 + i * 0.8
            sx = center[0] + math.cos(spiral_angle) * spiral_radius
            sy = center[1] + math.sin(spiral_angle) * spiral_radius
            spiral_color = (150, 100, 255)
            pygame.draw.circle(plane_surf, spiral_color, (int(sx), int(sy)), 2)
        
        # 弹幕图案3：十字弹幕
        cross_phase = (t * 2) % 1.0
        for direction in range(4):
            angle = direction * 1.571
            for j in range(5):
                bullet_dist = 10 + (cross_phase + j * 0.2) * 20
                cx = center[0] + math.cos(angle) * bullet_dist
                cy = center[1] + math.sin(angle) * bullet_dist
                pygame.draw.circle(plane_surf, (100, 255, 150), (int(cx), int(cy)), 3)
        return plane_surf

    elif model_style == "stalker_ex5":  # 时钟齿轮·蒸汽朋克
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 大齿轮
        for gear_idx in range(3):
            gear_radius = 35 - gear_idx * 10
            gear_rotation = t * (1 + gear_idx * 0.5) * (-1 if gear_idx % 2 else 1)
            teeth_count = 12 - gear_idx * 2
            
            gear_color = (180 + gear_idx * 20, 140 + gear_idx * 20, 100 + gear_idx * 10)
            pygame.draw.circle(plane_surf, gear_color, center, gear_radius, 2)
            
            # 齿轮齿
            for i in range(teeth_count):
                tooth_angle = gear_rotation + (i / teeth_count) * 2 * math.pi
                inner_x = center[0] + math.cos(tooth_angle) * (gear_radius - 3)
                inner_y = center[1] + math.sin(tooth_angle) * (gear_radius - 3)
                outer_x = center[0] + math.cos(tooth_angle) * (gear_radius + 3)
                outer_y = center[1] + math.sin(tooth_angle) * (gear_radius + 3)
                pygame.draw.line(plane_surf, gear_color, (inner_x, inner_y), (outer_x, outer_y), 2)
        
        # 钟表指针
        for hand_idx in range(3):
            hand_length = 25 - hand_idx * 7
            hand_speed = 1 + hand_idx * 2
            hand_angle = t * hand_speed - 1.571
            hand_x = center[0] + math.cos(hand_angle) * hand_length
            hand_y = center[1] + math.sin(hand_angle) * hand_length
            hand_color = (220, 180, 120)
            pygame.draw.line(plane_surf, hand_color, center, (hand_x, hand_y), 3 - hand_idx)
        
        # 蒸汽粒子
        for i in range(15):
            steam_phase = (t + i * 0.2) % 1.5
            steam_x = center[0] + math.sin(t + i) * 20
            steam_y = center[1] + 30 - steam_phase * 40
            steam_size = int(3 + steam_phase * 4)
            steam_color = (200, 200, 200)
            pygame.draw.circle(plane_surf, steam_color, (int(steam_x), int(steam_y)), steam_size, 1)
        return plane_surf

    elif model_style == "gaia_ex5":  # DNA螺旋·生命密码
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 双螺旋结构
        helix_length = 50
        helix_radius = 15
        for i in range(30):
            z = (i / 30.0) * helix_length - helix_length / 2
            angle1 = t + i * 0.3
            angle2 = angle1 + math.pi
            
            # 第一条螺旋
            x1 = center[0] + z * 0.4 + math.cos(angle1) * helix_radius
            y1 = center[1] + math.sin(angle1) * helix_radius
            helix1_color = (100, 255, 150)
            pygame.draw.circle(plane_surf, helix1_color, (int(x1), int(y1)), 3)
            
            # 第二条螺旋
            x2 = center[0] + z * 0.4 + math.cos(angle2) * helix_radius
            y2 = center[1] + math.sin(angle2) * helix_radius
            helix2_color = (255, 150, 100)
            pygame.draw.circle(plane_surf, helix2_color, (int(x2), int(y2)), 3)
            
            # 碱基对连接线
            if i % 3 == 0:
                pygame.draw.line(plane_surf, (150, 100, 255), (x1, y1), (x2, y2), 1)
        
        # 细胞分裂动画
        division_phase = (t % 2.0) / 2.0
        if division_phase < 0.5:
            cell_size = int(10 + division_phase * 30)
            pygame.draw.circle(plane_surf, (100, 255, 200), center, cell_size, 2)
        else:
            split_distance = int((division_phase - 0.5) * 40)
            pygame.draw.circle(plane_surf, (100, 255, 200), (center[0] - split_distance, center[1]), 10, 2)
            pygame.draw.circle(plane_surf, (100, 255, 200), (center[0] + split_distance, center[1]), 10, 2)
        return plane_surf

    elif model_style == "weaver_ex5":  # 棋盘游戏·策略大师
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 棋盘格子
        board_size = 6
        cell_size = 10
        for row in range(board_size):
            for col in range(board_size):
                cell_x = center[0] - (board_size * cell_size) // 2 + col * cell_size
                cell_y = center[1] - (board_size * cell_size) // 2 + row * cell_size
                
                if (row + col) % 2 == 0:
                    cell_color = (220, 220, 220)
                else:
                    cell_color = (50, 50, 50)
                
                pygame.draw.rect(plane_surf, cell_color, (cell_x, cell_y, cell_size, cell_size))
        
        # 国际象棋棋子
        for i in range(8):
            piece_angle = t + i * 0.785
            piece_radius = 35
            piece_x = center[0] + math.cos(piece_angle) * piece_radius
            piece_y = center[1] + math.sin(piece_angle) * piece_radius
            
            piece_type = i % 4
            if piece_type == 0:
                pygame.draw.circle(plane_surf, (255, 215, 0), (int(piece_x), int(piece_y)), 4)
                pygame.draw.line(plane_surf, (255, 215, 0), (piece_x, piece_y - 6), (piece_x, piece_y - 2), 2)
            elif piece_type == 1:
                pygame.draw.circle(plane_surf, (192, 192, 192), (int(piece_x), int(piece_y)), 5)
            elif piece_type == 2:
                pygame.draw.rect(plane_surf, (139, 69, 19), (piece_x - 4, piece_y - 4, 8, 8))
            else:
                pygame.draw.circle(plane_surf, (150, 150, 150), (int(piece_x), int(piece_y)), 3)
        
        # 围棋棋子
        go_positions = [(0, -18), (18, 0), (0, 18), (-18, 0)]
        for idx, (dx, dy) in enumerate(go_positions):
            go_x = center[0] + dx
            go_y = center[1] + dy
            go_color = (0, 0, 0) if idx % 2 == 0 else (255, 255, 255)
            pygame.draw.circle(plane_surf, go_color, (int(go_x), int(go_y)), 5)
        return plane_surf

    elif model_style == "solar_ex5":  # 天气预报·气象万千
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        weather_cycle = int(t / 2) % 4
        
        if weather_cycle == 0:  # 晴天
            sun_size = int(15 + abs(math.sin(t * 2)) * 5)
            pygame.draw.circle(plane_surf, (255, 220, 100), center, sun_size)
            
            for i in range(8):
                ray_angle = t + i * 0.785
                ray_length = 25 + abs(math.sin(t * 3 + i)) * 10
                ray_x = center[0] + math.cos(ray_angle) * ray_length
                ray_y = center[1] + math.sin(ray_angle) * ray_length
                pygame.draw.line(plane_surf, (255, 220, 100), center, (ray_x, ray_y), 3)
        
        elif weather_cycle == 1:  # 雨天
            pygame.draw.circle(plane_surf, (150, 150, 150), center, 20)
            for i in range(25):
                rain_phase = (t * 5 + i * 0.1) % 1.0
                rain_x = center[0] + (i % 5 - 2) * 12
                rain_y = center[1] - 30 + rain_phase * 60
                pygame.draw.line(plane_surf, (100, 180, 255), 
                               (rain_x, rain_y), (rain_x - 2, rain_y + 8), 2)
        
        elif weather_cycle == 2:  # 雪天
            pygame.draw.circle(plane_surf, (200, 200, 200), center, 20)
            for i in range(20):
                snow_phase = (t * 2 + i * 0.15) % 1.0
                snow_x = center[0] + math.sin(t + i) * 30
                snow_y = center[1] - 30 + snow_phase * 60
                
                for branch in range(6):
                    branch_angle = (branch / 6.0) * 2 * math.pi
                    bx = snow_x + math.cos(branch_angle) * 4
                    by = snow_y + math.sin(branch_angle) * 4
                    pygame.draw.line(plane_surf, (255, 255, 255), (snow_x, snow_y), (bx, by), 1)
        
        else:  # 雷暴
            pygame.draw.circle(plane_surf, (80, 80, 80), center, 20)
            if int(t * 10) % 3 == 0:
                for i in range(5):
                    lightning_x = center[0] + (i - 2) * 10
                    lightning_y1 = center[1] - 25 + i * 10
                    lightning_y2 = lightning_y1 + 10
                    pygame.draw.line(plane_surf, (255, 255, 100), 
                                   (lightning_x, lightning_y1), (lightning_x + 6, lightning_y2), 3)
        return plane_surf

    elif model_style == "arbiter_ex5":  # 星座连线·黄道十二宫
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        constellation_idx = int(t / 3) % 4
        
        # 星座星星位置
        constellations = [
            [(0, -20), (12, -15), (-12, -10), (0, 5)],
            [(0, -15), (18, -10), (18, 8), (0, 15), (-18, 8), (-18, -10)],
            [(-12, -15), (12, -15), (12, 5), (-12, 5)],
            [(0, -18), (12, -8), (12, 8), (0, 18), (-12, 8), (-12, -8)],
        ]
        
        current_constellation = constellations[constellation_idx]
        
        # 绘制星星和连线
        for idx, (dx, dy) in enumerate(current_constellation):
            star_x = center[0] + dx
            star_y = center[1] + dy
            star_brightness = int(200 + 55 * math.sin(t * 3 + idx))
            pygame.draw.circle(plane_surf, (star_brightness, star_brightness, 200), 
                             (int(star_x), int(star_y)), 4)
            
            if idx > 0:
                prev_dx, prev_dy = current_constellation[idx - 1]
                pygame.draw.line(plane_surf, (200, 200, 255), 
                               (center[0] + prev_dx, center[1] + prev_dy),
                               (star_x, star_y), 2)
        
        # 星座符号环绕
        for i in range(12):
            symbol_angle = t * 0.5 + i * 0.524
            symbol_radius = 40
            sx = center[0] + math.cos(symbol_angle) * symbol_radius
            sy = center[1] + math.sin(symbol_angle) * symbol_radius
            symbol_color = (255, 255, 200) if i == constellation_idx else (150, 150, 150)
            pygame.draw.circle(plane_surf, symbol_color, (int(sx), int(sy)), 3)
        return plane_surf

    elif model_style == "eclipse_ex5":  # 漫画分镜·速度线
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 速度线
        for i in range(24):
            angle = (i / 24.0) * 2 * math.pi
            speed_length = 30 + abs(math.sin(t * 2 + i)) * 15
            line_start_x = center[0] + math.cos(angle) * 10
            line_start_y = center[1] + math.sin(angle) * 10
            line_end_x = center[0] + math.cos(angle) * speed_length
            line_end_y = center[1] + math.sin(angle) * speed_length
            pygame.draw.line(plane_surf, (255, 100, 100), 
                           (line_start_x, line_start_y), (line_end_x, line_end_y), 2)
        
        # 漫画爆炸泡泡
        for i in range(5):
            bubble_angle = t * 2 + i * 1.257
            bubble_radius = 25 + i * 4
            bubble_x = center[0] + math.cos(bubble_angle) * bubble_radius
            bubble_y = center[1] + math.sin(bubble_angle) * bubble_radius
            bubble_size = int(8 + abs(math.sin(t * 3 + i)) * 5)
            
            # 爆炸形状
            points = []
            for j in range(8):
                spike_angle = (j / 8.0) * 2 * math.pi
                spike_radius = bubble_size if j % 2 == 0 else bubble_size * 1.5
                px = bubble_x + math.cos(spike_angle) * spike_radius
                py = bubble_y + math.sin(spike_angle) * spike_radius
                points.append((px, py))
            
            if len(points) >= 3:
                pygame.draw.polygon(plane_surf, (100, 100, 255), points, 2)
        
        # 音效字模拟
        if int(t * 2) % 2 == 0:
            for i in range(3):
                text_x = center[0] + (i - 1) * 18
                text_y = center[1] - 25
                pygame.draw.circle(plane_surf, (255, 255, 100), (text_x, text_y), 6, 2)
                pygame.draw.line(plane_surf, (255, 255, 100), 
                               (text_x - 4, text_y + 6), (text_x + 4, text_y + 6), 2)
        return plane_surf

    elif model_style == "prism_ex5":  # 乐高积木·创意拼搭
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        block_colors = [(255, 50, 50), (50, 255, 50), (50, 50, 255), 
                      (255, 255, 50), (255, 50, 255), (50, 255, 255)]
        
        for layer in range(4):
            for i in range(6):
                angle = t * 0.5 + layer * 0.785 + i * 1.047
                radius = 20 + layer * 10
                block_x = center[0] + math.cos(angle) * radius
                block_y = center[1] + math.sin(angle) * radius
                
                block_size = 10
                block_color = block_colors[(layer + i) % len(block_colors)]
                
                pygame.draw.rect(plane_surf, block_color, 
                               (block_x - block_size//2, block_y - block_size//2, 
                                block_size, block_size))
                
                # 积木凸起
                for dy in [-3, 3]:
                    for dx in [-3, 3]:
                        pygame.draw.circle(plane_surf, 
                                         tuple(max(0, c - 50) for c in block_color),
                                         (int(block_x + dx), int(block_y + dy)), 1)
        
        # 拼搭动画
        for i in range(8):
            fall_phase = (t * 2 + i * 0.3) % 1.0
            fall_x = center[0] + math.sin(t + i) * 25
            fall_y = center[1] - 35 + fall_phase * 70
            fall_color = block_colors[i % len(block_colors)]
            fall_size = 8
            pygame.draw.rect(plane_surf, fall_color, 
                           (fall_x - fall_size//2, fall_y - fall_size//2, 
                            fall_size, fall_size))
        return plane_surf

    elif model_style == "necro_ex5":  # 俄罗斯方块·消除爆炸
        plane_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        center = (60, 60)
        ticks = pygame.time.get_ticks()
        t = ticks * 0.001
        
        # 下落的方块
        tetromino_types = [
            [(0, 0), (1, 0), (2, 0), (3, 0)],
            [(0, 0), (1, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (2, 0), (1, 1)],
        ]
        
        for i in range(6):
            fall_phase = (t * 2 + i * 0.4) % 1.0
            tetromino = tetromino_types[i % len(tetromino_types)]
            
            base_x = center[0] - 18 + (i % 3) * 18
            base_y = center[1] - 35 + fall_phase * 70
            
            block_size = 6
            block_color = [(100, 255, 255), (255, 255, 100), (255, 100, 255)][i % 3]
            
            for block_dx, block_dy in tetromino:
                block_x = base_x + block_dx * block_size
                block_y = base_y + block_dy * block_size
                pygame.draw.rect(plane_surf, block_color, 
                               (block_x, block_y, block_size - 1, block_size - 1))
                pygame.draw.rect(plane_surf, 
                               tuple(min(255, c + 50) for c in block_color),
                               (block_x, block_y, block_size - 1, block_size - 1), 1)
        
        # 消除特效
        clear_phase = (t * 3) % 1.0
        if clear_phase < 0.3:
            clear_y = center[1] + 25
            clear_width = int(50 * (1 - clear_phase / 0.3))
            pygame.draw.rect(plane_surf, (255, 255, 255), 
                           (center[0] - 25, clear_y - 3, clear_width, 6))
            
            # 爆炸粒子
            for i in range(10):
                particle_angle = (i / 10.0) * 2 * math.pi
                particle_dist = (clear_phase / 0.3) * 35
                px = center[0] + math.cos(particle_angle) * particle_dist
                py = clear_y + math.sin(particle_angle) * particle_dist
                pygame.draw.circle(plane_surf, (255, 255, 100), (int(px), int(py)), 3)
        return plane_surf


    # 赛博朋克风格几何飞机 - 13种机体差异化设计 + 动态特性
    # ========== Mirage幻镜·万华专属涂装渲染 ==========
    elif model_style == "mirage_fractal":
        # 分形迷宫·无限递归 - 曼德博分形，无限递归图案
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 分形递归圆环（5层）
        for depth in range(5):
            layer_count = 2 ** depth
            layer_r = 10 + depth * 8
            for i in range(layer_count):
                angle = (i * 360 / layer_count + t * (5 - depth) * 3) * 0.01745
                fx = 60 + math.cos(angle) * layer_r
                fy = 60 + math.sin(angle) * layer_r
                frac_size = 8 - depth
                pygame.draw.circle(s, (180 + depth * 15, 120 + depth * 10, 255), 
                                  (int(fx), int(fy)), frac_size)
        # 中心分形核心
        pygame.draw.circle(s, (200, 150, 255), (60, 60), 12)
        pygame.draw.circle(s, (180, 120, 255), (60, 60), 8)
        # 递归连线
        for i in range(8):
            angle = (i * 45 + t * 10) * 0.01745
            end_x = 60 + math.cos(angle) * 45
            end_y = 60 + math.sin(angle) * 45
            pygame.draw.line(s, (160, 100, 230), (60, 60), (end_x, end_y), 1)
        
        return s

    elif model_style == "mirage_butterfly":
        # 蝴蝶效应·混沌之翼 - 蝴蝶翅膀对称图案
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        wing_flutter = abs(math.sin(t * 4)) * 0.3
        # 左翅膀
        left_wing = [(60, 60), (20, 40 - wing_flutter * 20), (15, 60), (25, 80 + wing_flutter * 15)]
        pygame.draw.polygon(s, (255, 180, 220), left_wing)
        pygame.draw.polygon(s, (255, 200, 240), left_wing, 2)
        # 右翅膀（镜像）
        right_wing = [(60, 60), (100, 40 - wing_flutter * 20), (105, 60), (95, 80 + wing_flutter * 15)]
        pygame.draw.polygon(s, (255, 180, 220), right_wing)
        pygame.draw.polygon(s, (255, 200, 240), right_wing, 2)
        # 翅膀花纹（64个鳞粉点）
        for scale_i in range(64):
            scale_side = 1 if scale_i < 32 else -1
            scale_angle = ((scale_i % 32) * 11.25 + t * 5) * 0.01745
            scale_r = 15 + (scale_i % 16) * 1.5
            scale_x = 60 + scale_side * (10 + math.cos(scale_angle) * scale_r)
            scale_y = 60 + math.sin(scale_angle) * scale_r * 0.8
            rainbow_hue = (scale_i * 5 + t * 30) % 360
            scale_color = (255, 150 + int(50 * math.sin(rainbow_hue * 0.01745)), 200)
            pygame.draw.circle(s, scale_color, (int(scale_x), int(scale_y)), 2)
        # 蝴蝶身体
        pygame.draw.ellipse(s, (230, 150, 200), (57, 45, 6, 30))
        pygame.draw.circle(s, (255, 200, 240), (60, 42), 4)
        
        return s

    elif model_style == "mirage_kaleidoscope":
        # 万花筒梦·色彩轮转 - 经典万花筒旋转图案
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        rotation = t * 30
        # 12个彩色扇区
        segment_colors = [
            (255, 100, 100), (255, 180, 100), (255, 255, 100),
            (180, 255, 100), (100, 255, 100), (100, 255, 180),
            (100, 255, 255), (100, 180, 255), (100, 100, 255),
            (180, 100, 255), (255, 100, 255), (255, 100, 180)
        ]
        for seg_i in range(12):
            seg_angle = (seg_i * 30 + rotation) * 0.01745
            next_angle = ((seg_i + 1) * 30 + rotation) * 0.01745
            # 扇形顶点
            pts = [(60, 60)]
            for a in range(int(seg_angle * 57.3), int(next_angle * 57.3) + 1, 5):
                rad = a * 0.01745
                pts.append((60 + math.cos(rad) * 45, 60 + math.sin(rad) * 45))
            if len(pts) > 2:
                pygame.draw.polygon(s, segment_colors[seg_i], pts)
        # 内圈花纹
        for inner_i in range(6):
            inner_angle = (inner_i * 60 + rotation * 2) * 0.01745
            ix = 60 + math.cos(inner_angle) * 20
            iy = 60 + math.sin(inner_angle) * 20
            pygame.draw.circle(s, (255, 220, 180), (int(ix), int(iy)), 6)
        # 中心宝石
        pygame.draw.circle(s, (255, 200, 150), (60, 60), 10)
        pygame.draw.circle(s, (255, 220, 180), (60, 60), 6)
        
        return s

    elif model_style == "mirage_crystal_palace":
        # 水晶宫殿·冰雕折射 - 冰雪水晶，七色折射
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 16根冰柱（环绕）
        for column_i in range(16):
            col_angle = (column_i * 22.5 + t * 3) * 0.01745
            col_r = 35
            col_x = 60 + math.cos(col_angle) * col_r
            col_y = 60 + math.sin(col_angle) * col_r
            col_height = 15 + int(5 * math.sin(t * 2 + column_i))
            # 冰柱（梯形）
            col_pts = [
                (col_x - 3, col_y + 5),
                (col_x - 2, col_y - col_height),
                (col_x + 2, col_y - col_height),
                (col_x + 3, col_y + 5)
            ]
            pygame.draw.polygon(s, (200, 240, 255), col_pts)
            pygame.draw.polygon(s, (220, 250, 255), col_pts, 1)
        # 8道折射光线
        for beam_i in range(8):
            beam_angle = (beam_i * 45 + t * 20) * 0.01745
            beam_x = 60 + math.cos(beam_angle) * 50
            beam_y = 60 + math.sin(beam_angle) * 50
            rainbow_colors = [(255, 200, 200), (255, 255, 200), (200, 255, 200),
                             (200, 255, 255), (200, 200, 255), (255, 200, 255)]
            beam_color = rainbow_colors[beam_i % 6]
            pygame.draw.line(s, beam_color, (60, 60), (beam_x, beam_y), 2)
        # 中心水晶核心
        pygame.draw.polygon(s, (180, 220, 250), [(60, 45), (50, 60), (60, 75), (70, 60)])
        pygame.draw.polygon(s, (220, 250, 255), [(60, 45), (50, 60), (60, 75), (70, 60)], 2)
        
        return s

    elif model_style == "mirage_funhouse":
        # 哈哈镜屋·扭曲现实 - 扭曲变形镜像
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        warp_phase = t * 3
        # 6面哈哈镜（扭曲波浪边框）
        for mirror_i in range(6):
            m_angle = (mirror_i * 60) * 0.01745
            m_x = 60 + math.cos(m_angle) * 35
            m_y = 60 + math.sin(m_angle) * 35
            # 波浪形边框
            wave_pts = []
            for seg in range(12):
                seg_angle = (seg * 30) * 0.01745
                warp = 3 * math.sin(warp_phase + seg + mirror_i)
                wx = m_x + math.cos(seg_angle) * (12 + warp)
                wy = m_y + math.sin(seg_angle) * (12 + warp)
                wave_pts.append((int(wx), int(wy)))
            pygame.draw.polygon(s, (255, 180, 130), wave_pts, 2)
            pygame.draw.circle(s, (255, 150, 100, 100), (int(m_x), int(m_y)), 10)
        # 扭曲反射线
        for warp_line in range(12):
            wl_angle = (warp_line * 30 + t * 15) * 0.01745
            wl_x = 60 + math.cos(wl_angle) * 45
            wl_y = 60 + math.sin(wl_angle) * 45
            warp_offset = 5 * math.sin(t * 4 + warp_line)
            pygame.draw.line(s, (230, 130, 80), (60, 60), 
                           (wl_x + warp_offset, wl_y + warp_offset), 1)
        # 中心笑脸（变形）
        pygame.draw.circle(s, (255, 150, 100), (60, 60), 15)
        pygame.draw.circle(s, (255, 180, 130), (60, 60), 12)
        
        return s

    elif model_style == "mirage_doppelganger":
        # 二重身影·暗夜替身 - 神秘暗影分身
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        shadow_delay = t * 0.5
        # 主体轮廓（暗色）
        pygame.draw.circle(s, (80, 60, 100), (60, 55), 25)
        pygame.draw.ellipse(s, (80, 60, 100), (45, 60, 30, 40))
        # 延迟影子（偏移）
        shadow_offset = 5 + int(3 * math.sin(shadow_delay))
        pygame.draw.circle(s, (60, 40, 80, 150), (60 + shadow_offset, 55 + shadow_offset), 25)
        pygame.draw.ellipse(s, (60, 40, 80, 150), (45 + shadow_offset, 60 + shadow_offset, 30, 40))
        # 诡异眼睛
        pygame.draw.circle(s, (150, 100, 200), (52, 52), 4)
        pygame.draw.circle(s, (150, 100, 200), (68, 52), 4)
        pygame.draw.circle(s, (200, 150, 255), (52, 52), 2)
        pygame.draw.circle(s, (200, 150, 255), (68, 52), 2)
        # 暗雾粒子
        for fog_i in range(20):
            fog_angle = (fog_i * 18 + t * 8) * 0.01745
            fog_r = 35 + int(10 * math.sin(t + fog_i))
            fog_x = 60 + math.cos(fog_angle) * fog_r
            fog_y = 60 + math.sin(fog_angle) * fog_r
            pygame.draw.circle(s, (60, 40, 80, 80), (int(fog_x), int(fog_y)), 4)
        
        return s

    elif model_style == "mirage_infinity_room":
        # 无限镜室·永恒延伸 - 草间弥生风格，无限点阵
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 100个光点（模拟无限镜室）
        for dot_i in range(100):
            # 伪3D深度效果
            depth = (dot_i % 10) / 10
            dot_angle = (dot_i * 36 + t * 5) * 0.01745
            dot_r = 10 + depth * 35
            dot_x = 60 + math.cos(dot_angle) * dot_r
            dot_y = 60 + math.sin(dot_angle) * dot_r
            dot_size = int(4 * (1 - depth * 0.5))
            dot_alpha = int(255 * (1 - depth * 0.7))
            if dot_size > 0:
                # 彩色点
                hue_shift = (dot_i * 3.6 + t * 20) % 360
                r = int(255 * (1 if hue_shift < 120 or hue_shift > 240 else 0))
                g = int(255 * (1 if 60 < hue_shift < 180 else 0))
                b = int(255 * (1 if hue_shift > 180 else 0))
                pygame.draw.circle(s, (max(r, 100), max(g, 100), max(b, 150), dot_alpha), 
                                  (int(dot_x), int(dot_y)), dot_size)
        # 中心红色大点
        pygame.draw.circle(s, (255, 100, 150), (60, 60), 10)
        pygame.draw.circle(s, (255, 130, 180), (60, 60), 6)
        
        return s

    elif model_style == "mirage_alice":
        # 镜中奇遇·爱丽丝门 - 爱丽丝梦游仙境风格
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 魔镜门框（椭圆）
        pygame.draw.ellipse(s, (200, 150, 100), (25, 20, 70, 80), 4)
        pygame.draw.ellipse(s, (255, 200, 150), (30, 25, 60, 70), 2)
        # 镜中漩涡
        for swirl in range(8):
            swirl_angle = (swirl * 45 + t * 30) * 0.01745
            swirl_r = 5 + swirl * 3
            sx = 60 + math.cos(swirl_angle) * swirl_r
            sy = 60 + math.sin(swirl_angle) * swirl_r
            pygame.draw.circle(s, (255, 100, 100), (int(sx), int(sy)), 3)
        # 8个扑克牌士兵
        for card_i in range(8):
            card_angle = (card_i * 45 + t * 10) * 0.01745
            card_r = 42
            card_x = 60 + math.cos(card_angle) * card_r
            card_y = 60 + math.sin(card_angle) * card_r
            # 红心或黑桃
            card_color = (255, 100, 100) if card_i % 2 == 0 else (50, 50, 50)
            pygame.draw.rect(s, (255, 255, 255), (int(card_x) - 4, int(card_y) - 6, 8, 12))
            pygame.draw.circle(s, card_color, (int(card_x), int(card_y)), 3)
        # 茶杯
        pygame.draw.ellipse(s, (200, 180, 150), (52, 70, 16, 10))
        pygame.draw.rect(s, (200, 180, 150), (54, 65, 12, 10))
        
        return s

    elif model_style == "mirage_narcissus":
        # 水仙倒影·自恋之池 - 水面倒影，涟漪效果
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 8圈涟漪
        for ripple_i in range(8):
            ripple_phase = (t * 2 + ripple_i * 0.3) % 1.0
            ripple_r = int(10 + ripple_phase * 40)
            ripple_alpha = int(150 * (1 - ripple_phase))
            if ripple_alpha > 0:
                pygame.draw.circle(s, (160, 200, 240, ripple_alpha), (60, 60), ripple_r, 2)
        # 水仙花倒影（上下对称）
        # 上半（正像）
        pygame.draw.circle(s, (255, 255, 200), (60, 40), 8)  # 花心
        for petal in range(6):
            petal_angle = (petal * 60) * 0.01745
            px = 60 + math.cos(petal_angle) * 12
            py = 40 + math.sin(petal_angle) * 12
            pygame.draw.circle(s, (255, 255, 220), (int(px), int(py)), 5)
        # 下半（倒影，稍微模糊）
        pygame.draw.circle(s, (200, 220, 255, 150), (60, 80), 8)
        for petal in range(6):
            petal_angle = (petal * 60) * 0.01745
            px = 60 + math.cos(petal_angle) * 12
            py = 80 - math.sin(petal_angle) * 12
            pygame.draw.circle(s, (200, 220, 255, 150), (int(px), int(py)), 5)
        # 花茎
        pygame.draw.line(s, (100, 180, 100), (60, 48), (60, 72), 2)
        
        return s

    elif model_style == "mirage_hologram":
        # 全息投影·未来幻象 - 科幻全息效果
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 48条扫描线
        for scan_i in range(48):
            scan_y = 10 + scan_i * 2
            scan_alpha = 100 + int(50 * math.sin(t * 5 + scan_i * 0.2))
            pygame.draw.line(s, (100, 200, 255, scan_alpha), (20, scan_y), (100, scan_y), 1)
        # 全息轮廓（三角形机体）
        glitch_offset = int(3 * math.sin(t * 10))
        holo_pts = [(60 + glitch_offset, 30), (35, 80), (85, 80)]
        pygame.draw.polygon(s, (100, 200, 255, 150), holo_pts)
        pygame.draw.polygon(s, (130, 220, 255), holo_pts, 2)
        # 故障效果（闪烁条纹）
        if int(t * 10) % 5 == 0:
            glitch_y = random.randint(30, 80)
            pygame.draw.rect(s, (100, 200, 255), (20, glitch_y, 80, 3))
        # 数据流粒子
        for data_i in range(20):
            data_angle = (data_i * 18 + t * 30) * 0.01745
            data_r = 40
            data_x = 60 + math.cos(data_angle) * data_r
            data_y = 60 + math.sin(data_angle) * data_r
            pygame.draw.rect(s, (80, 180, 240), (int(data_x), int(data_y), 3, 3))
        
        return s

    elif model_style == "mirage_phantom_opera":
        # 魅影歌剧·面具之下 - 歌剧魅影风格
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 半脸面具
        # 白色半边
        pygame.draw.circle(s, (255, 255, 255), (60, 50), 25)
        pygame.draw.rect(s, (0, 0, 0, 0), (60, 25, 30, 50))  # 遮住右半
        # 黑暗半边
        pygame.draw.circle(s, (30, 30, 30), (60, 50), 25)
        pygame.draw.rect(s, (0, 0, 0, 0), (30, 25, 30, 50))  # 遮住左半
        # 眼睛
        pygame.draw.circle(s, (200, 200, 200), (50, 48), 5)
        pygame.draw.circle(s, (50, 50, 50), (70, 48), 5)
        # 16片玫瑰花瓣
        for rose_i in range(16):
            rose_angle = (rose_i * 22.5 + t * 8) * 0.01745
            rose_r = 35 + int(5 * math.sin(t * 2 + rose_i))
            rose_x = 60 + math.cos(rose_angle) * rose_r
            rose_y = 60 + math.sin(rose_angle) * rose_r
            pygame.draw.circle(s, (200, 50, 80), (int(rose_x), int(rose_y)), 4)
        # 烛光效果
        candle_flicker = abs(math.sin(t * 8))
        pygame.draw.circle(s, (255, 200, 100, int(150 * candle_flicker)), (60, 90), 8)
        pygame.draw.circle(s, (255, 255, 200), (60, 90), 4)
        
        return s

    elif model_style == "mirage_ouroboros":
        # 衔尾之蛇·镜像轮回 - 衔尾蛇无限循环
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 24节蛇身
        for seg_i in range(24):
            seg_progress = seg_i / 24
            seg_angle = (seg_progress * 360 + t * 20) * 0.01745
            seg_r = 35
            seg_x = 60 + math.cos(seg_angle) * seg_r
            seg_y = 60 + math.sin(seg_angle) * seg_r
            # 蛇身颜色渐变（金色到绿色）
            seg_color = (200 - seg_i * 3, 180 - seg_i * 2, 100 + seg_i * 2)
            seg_size = 6 if seg_i < 12 else 5  # 头部较大
            pygame.draw.circle(s, seg_color, (int(seg_x), int(seg_y)), seg_size)
            # 鳞片纹理
            if seg_i % 3 == 0:
                pygame.draw.circle(s, (220, 200, 120), (int(seg_x), int(seg_y)), seg_size - 2, 1)
        # 蛇头（咬住尾巴）
        head_angle = t * 20 * 0.01745
        head_x = 60 + math.cos(head_angle) * 35
        head_y = 60 + math.sin(head_angle) * 35
        pygame.draw.circle(s, (200, 180, 100), (int(head_x), int(head_y)), 8)
        # 眼睛
        eye_x = head_x + math.cos(head_angle) * 4
        eye_y = head_y + math.sin(head_angle) * 4
        pygame.draw.circle(s, (255, 50, 50), (int(eye_x), int(eye_y)), 2)
        # 中心无限符号
        pygame.draw.circle(s, (200, 180, 100), (50, 60), 10, 2)
        pygame.draw.circle(s, (200, 180, 100), (70, 60), 10, 2)
        
        return s

        # ========== Gambit命运赌徒·艾斯专属涂装渲染 ==========
    if model_style == "gambit_vegas":
        # 拉斯维加斯·霓虹罪城 - 霓虹灯老虎机
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 霓虹边框闪烁
        neon_phase = int(t * 10) % 3
        neon_colors = [(255, 50, 50), (50, 255, 50), (255, 215, 0)]
        pygame.draw.rect(s, neon_colors[neon_phase], (15, 15, 90, 90), 4, border_radius=10)
        # 3个老虎机转轮
        reel_symbols = ['7', '🍒', '💎']
        for reel_i in range(3):
            reel_x = 30 + reel_i * 25
            reel_y = 50 + int(5 * math.sin(t * 8 + reel_i * 2))
            pygame.draw.rect(s, (50, 50, 50), (reel_x - 8, reel_y - 12, 20, 24), border_radius=3)
            pygame.draw.rect(s, (255, 215, 0), (reel_x - 8, reel_y - 12, 20, 24), 2, border_radius=3)
            # 符号（用圆圈代替）
            symbol_color = [(255, 215, 0), (255, 50, 50), (100, 200, 255)][reel_i]
            pygame.draw.circle(s, symbol_color, (reel_x + 2, reel_y), 6)
        # 金币雨
        for coin_i in range(15):
            coin_y = (t * 100 + coin_i * 20) % 120
            coin_x = 20 + (coin_i * 7) % 80
            pygame.draw.circle(s, (255, 215, 0), (int(coin_x), int(coin_y)), 4)
            pygame.draw.circle(s, (230, 190, 0), (int(coin_x), int(coin_y)), 4, 1)
        # JACKPOT文字位置（用金色条代替）
        pygame.draw.rect(s, (255, 215, 0), (25, 85, 70, 10), border_radius=2)
        
    elif model_style == "gambit_tarot":
        # 塔罗牌阵·命运占卜 - 神秘塔罗牌
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 22张大阿尔卡纳牌阵（环绕）
        for card_i in range(22):
            card_angle = (card_i * 16.36 + t * 5) * 0.01745
            card_r = 38
            card_x = 60 + math.cos(card_angle) * card_r
            card_y = 60 + math.sin(card_angle) * card_r
            # 牌面
            pygame.draw.rect(s, (180, 100, 200), (int(card_x) - 5, int(card_y) - 7, 10, 14))
            pygame.draw.rect(s, (200, 120, 220), (int(card_x) - 5, int(card_y) - 7, 10, 14), 1)
            # 神秘符号
            pygame.draw.circle(s, (255, 200, 255), (int(card_x), int(card_y)), 3)
        # 中心命运之轮
        pygame.draw.circle(s, (180, 100, 200), (60, 60), 20, 3)
        for spoke in range(8):
            spoke_angle = (spoke * 45 + t * 15) * 0.01745
            sx = 60 + math.cos(spoke_angle) * 18
            sy = 60 + math.sin(spoke_angle) * 18
            pygame.draw.line(s, (200, 120, 220), (60, 60), (sx, sy), 2)
        pygame.draw.circle(s, (255, 200, 255), (60, 60), 8)
        
        return s

    elif model_style == "gambit_mahjong":
        # 麻将国士·东风起势 - 麻将牌
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 13张国士无双牌阵
        tiles = ['东', '南', '西', '北', '中', '發', '白', '一', '九', '①', '⑨', '1', '9']
        for tile_i in range(13):
            tile_angle = (tile_i * 27.7 + t * 8) * 0.01745
            tile_r = 38
            tile_x = 60 + math.cos(tile_angle) * tile_r
            tile_y = 60 + math.sin(tile_angle) * tile_r
            # 麻将牌（白色底）
            pygame.draw.rect(s, (255, 255, 240), (int(tile_x) - 6, int(tile_y) - 8, 12, 16), border_radius=2)
            pygame.draw.rect(s, (0, 150, 100), (int(tile_x) - 6, int(tile_y) - 8, 12, 16), 1, border_radius=2)
            # 牌面花纹
            tile_color = (255, 0, 0) if tile_i < 7 else (0, 100, 0)
            pygame.draw.circle(s, tile_color, (int(tile_x), int(tile_y)), 3)
        # 中心（胡牌！）
        pygame.draw.circle(s, (0, 150, 100), (60, 60), 18)
        pygame.draw.circle(s, (50, 180, 130), (60, 60), 14)
        pygame.draw.circle(s, (255, 255, 240), (60, 60), 8)
        
        return s

    elif model_style == "gambit_lottery":
        # 彩票头奖·亿万梦想 - 彩票号码球
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 49个号码球（环绕）
        for ball_i in range(20):
            ball_angle = (ball_i * 18 + t * 15) * 0.01745
            ball_r = 30 + int(8 * math.sin(t * 3 + ball_i))
            ball_x = 60 + math.cos(ball_angle) * ball_r
            ball_y = 60 + math.sin(ball_angle) * ball_r
            # 彩球颜色
            ball_colors = [(255, 100, 100), (255, 200, 100), (100, 255, 100),
                          (100, 200, 255), (200, 100, 255)]
            ball_color = ball_colors[ball_i % 5]
            pygame.draw.circle(s, ball_color, (int(ball_x), int(ball_y)), 6)
            pygame.draw.circle(s, (255, 255, 255), (int(ball_x) - 2, int(ball_y) - 2), 2)
        # 头奖光环
        jackpot_pulse = abs(math.sin(t * 5))
        pygame.draw.circle(s, (255, 215, 0, int(150 * jackpot_pulse)), (60, 60), 25, 4)
        # 中心大奖球
        pygame.draw.circle(s, (255, 50, 50), (60, 60), 15)
        pygame.draw.circle(s, (255, 150, 150), (60, 60), 10)
        pygame.draw.circle(s, (255, 255, 255), (55, 55), 4)
        
        return s

    elif model_style == "gambit_blackjack":
        # 二十一点·黑杰克王 - 绿色赌桌
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 绿色赌桌
        pygame.draw.ellipse(s, (0, 100, 50), (15, 25, 90, 70))
        pygame.draw.ellipse(s, (50, 150, 100), (15, 25, 90, 70), 3)
        # 筹码堆（3堆）
        chip_colors = [(255, 50, 50), (50, 50, 255), (50, 50, 50)]
        for stack_i in range(3):
            stack_x = 35 + stack_i * 25
            for chip in range(4):
                chip_y = 75 - chip * 3
                pygame.draw.ellipse(s, chip_colors[stack_i], (stack_x - 6, chip_y - 2, 12, 4))
        # A和K牌
        # A牌
        pygame.draw.rect(s, (255, 255, 255), (40, 35, 16, 22), border_radius=2)
        pygame.draw.circle(s, (50, 50, 50), (48, 46), 5)  # 黑桃
        # K牌
        pygame.draw.rect(s, (255, 255, 255), (64, 35, 16, 22), border_radius=2)
        pygame.draw.circle(s, (255, 50, 50), (72, 46), 5)  # 红心
        # 21点标记
        pygame.draw.circle(s, (255, 215, 0), (60, 20), 10)
        
        return s

    elif model_style == "gambit_russian_roulette":
        # 俄罗斯轮盘·致命赌注 - 左轮手枪
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 弹巢（6个孔）
        cylinder_rotation = t * 30
        pygame.draw.circle(s, (150, 150, 150), (60, 60), 30)
        pygame.draw.circle(s, (120, 120, 120), (60, 60), 25)
        for chamber_i in range(6):
            chamber_angle = (chamber_i * 60 + cylinder_rotation) * 0.01745
            chamber_x = 60 + math.cos(chamber_angle) * 18
            chamber_y = 60 + math.sin(chamber_angle) * 18
            # 空弹巢
            pygame.draw.circle(s, (80, 80, 80), (int(chamber_x), int(chamber_y)), 6)
            # 子弹（只有1个）
            if chamber_i == 0:
                pygame.draw.circle(s, (255, 215, 0), (int(chamber_x), int(chamber_y)), 4)
        # 枪管
        pygame.draw.rect(s, (100, 100, 100), (60, 30, 8, 20))
        # 扳机
        pygame.draw.rect(s, (80, 80, 80), (55, 85, 10, 15), border_radius=2)
        # 危险警告
        warning_flash = int(t * 5) % 2
        if warning_flash:
            pygame.draw.circle(s, (255, 0, 0, 100), (60, 60), 35, 3)
        
        return s

    elif model_style == "gambit_horseshoe":
        # 四叶幸运草·幸运护符 - 幸运符号组合
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 24片四叶草叶子
        for clover_i in range(24):
            clover_angle = (clover_i * 15 + t * 10) * 0.01745
            clover_r = 35
            clover_x = 60 + math.cos(clover_angle) * clover_r
            clover_y = 60 + math.sin(clover_angle) * clover_r
            # 心形叶子
            pygame.draw.circle(s, (100, 200, 100), (int(clover_x), int(clover_y)), 5)
        # 马蹄铁
        horseshoe_pts = []
        for hs_i in range(12):
            hs_angle = (hs_i * 15 - 75) * 0.01745
            hs_x = 60 + math.cos(hs_angle) * 22
            hs_y = 55 + math.sin(hs_angle) * 22
            horseshoe_pts.append((int(hs_x), int(hs_y)))
        if len(horseshoe_pts) > 1:
            pygame.draw.lines(s, (255, 215, 0), False, horseshoe_pts, 5)
        # 幸运闪光
        sparkle_phase = t * 8
        for sparkle_i in range(8):
            if int(sparkle_phase + sparkle_i) % 4 == 0:
                sp_angle = (sparkle_i * 45) * 0.01745
                sp_x = 60 + math.cos(sp_angle) * 45
                sp_y = 60 + math.sin(sp_angle) * 45
                pygame.draw.circle(s, (255, 255, 200), (int(sp_x), int(sp_y)), 3)
        # 中心四叶草
        for leaf in range(4):
            leaf_angle = (leaf * 90 + 45) * 0.01745
            leaf_x = 60 + math.cos(leaf_angle) * 8
            leaf_y = 60 + math.sin(leaf_angle) * 8
            pygame.draw.circle(s, (130, 220, 130), (int(leaf_x), int(leaf_y)), 6)
        pygame.draw.circle(s, (100, 180, 100), (60, 60), 4)
        
        return s

    elif model_style == "gambit_casino_royale":
        # 皇家赌场·007特工 - 优雅黑金风格
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 黑色背景
        pygame.draw.circle(s, (20, 20, 20), (60, 60), 45)
        pygame.draw.circle(s, (50, 50, 50), (60, 60), 45, 2)
        # 金色装饰边
        pygame.draw.circle(s, (255, 215, 0), (60, 60), 42, 1)
        # 007风格枪管视角
        for ring in range(5):
            ring_r = 10 + ring * 7
            pygame.draw.circle(s, (50, 50, 50), (60, 60), ring_r, 1)
        # 马提尼杯
        pygame.draw.polygon(s, (200, 200, 200), [(50, 75), (60, 55), (70, 75)])
        pygame.draw.line(s, (200, 200, 200), (60, 75), (60, 90), 2)
        pygame.draw.line(s, (200, 200, 200), (52, 90), (68, 90), 2)
        # 橄榄
        pygame.draw.circle(s, (100, 150, 50), (60, 65), 3)
        # 扑克牌角落
        pygame.draw.rect(s, (255, 255, 255), (80, 20, 20, 28), border_radius=2)
        pygame.draw.circle(s, (255, 50, 50), (90, 34), 4)  # 红心A
        
        return s

    elif model_style == "gambit_pachinko":
        # 弹珠柏青哥·银色瀑布 - 柏青哥机台
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 钉板网格
        for pin_row in range(8):
            for pin_col in range(6):
                offset = 5 if pin_row % 2 == 0 else 0
                pin_x = 20 + pin_col * 15 + offset
                pin_y = 15 + pin_row * 12
                pygame.draw.circle(s, (200, 200, 200), (pin_x, pin_y), 2)
        # 100个银色弹珠（瀑布效果）
        for ball_i in range(30):
            ball_progress = (t * 3 + ball_i * 0.1) % 1.0
            ball_x = 30 + (ball_i * 3) % 60 + int(5 * math.sin(ball_progress * 10 + ball_i))
            ball_y = int(ball_progress * 100) + 10
            if ball_y < 110:
                pygame.draw.circle(s, (220, 220, 255), (ball_x, ball_y), 3)
                pygame.draw.circle(s, (255, 255, 255), (ball_x - 1, ball_y - 1), 1)
        # 入球口
        pygame.draw.rect(s, (255, 50, 50), (45, 95, 30, 15), border_radius=3)
        pygame.draw.rect(s, (255, 215, 0), (45, 95, 30, 15), 2, border_radius=3)
        
        return s

    elif model_style == "gambit_fortune_cookie":
        # 幸运饼签·命运甜点 - 幸运饼干
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 12个饼干碎片
        for cookie_i in range(12):
            cookie_angle = (cookie_i * 30 + t * 8) * 0.01745
            cookie_r = 35
            cookie_x = 60 + math.cos(cookie_angle) * cookie_r
            cookie_y = 60 + math.sin(cookie_angle) * cookie_r
            # 饼干弧形碎片
            pygame.draw.arc(s, (255, 200, 100), 
                          (int(cookie_x) - 8, int(cookie_y) - 8, 16, 16),
                          cookie_angle, cookie_angle + 1, 4)
        # 中心完整饼干
        pygame.draw.circle(s, (255, 200, 100), (60, 60), 18)
        pygame.draw.arc(s, (230, 180, 80), (42, 42, 36, 36), 0.5, 2.5, 3)
        # 签纸飘出
        paper_wave = math.sin(t * 3) * 5
        pygame.draw.rect(s, (255, 255, 240), (50 + paper_wave, 55, 20, 8))
        pygame.draw.line(s, (200, 50, 50), (52 + paper_wave, 59), (68 + paper_wave, 59), 1)
        # 幸运光芒
        for ray_i in range(8):
            ray_angle = (ray_i * 45 + t * 20) * 0.01745
            ray_x = 60 + math.cos(ray_angle) * 48
            ray_y = 60 + math.sin(ray_angle) * 48
            pygame.draw.line(s, (255, 220, 130), (60, 60), (ray_x, ray_y), 1)
        
        return s

    elif model_style == "gambit_probability":
        # 概率云图·量子赌博 - 概率波函数
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 波函数可视化
        for x in range(20, 100, 3):
            # 高斯分布曲线
            gaussian = math.exp(-((x - 60) ** 2) / 400)
            wave_y = 60 - int(gaussian * 30 * abs(math.sin(t * 3 + x * 0.1)))
            pygame.draw.circle(s, (100, 200, 255), (x, wave_y), 2)
            # 概率分布点
            pygame.draw.line(s, (100, 200, 255, 100), (x, 60), (x, wave_y), 1)
        # 3个叠加态（薛定谔）
        for state_i in range(3):
            state_angle = (state_i * 120 + t * 15) * 0.01745
            state_r = 25
            state_x = 60 + math.cos(state_angle) * state_r
            state_y = 60 + math.sin(state_angle) * state_r
            # 模糊态（半透明）
            pygame.draw.circle(s, (130, 220, 255, 150), (int(state_x), int(state_y)), 10)
            pygame.draw.circle(s, (100, 200, 255), (int(state_x), int(state_y)), 10, 2)
        # 中心观测点
        pygame.draw.circle(s, (255, 255, 255), (60, 60), 8)
        pygame.draw.circle(s, (100, 200, 255), (60, 60), 8, 2)
        # 不确定性符号
        pygame.draw.circle(s, (80, 180, 240), (60, 60), 35, 1)
        
        return s

    elif model_style == "gambit_joker":
        # 小丑王牌·混沌之笑 - 疯狂小丑
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        # 小丑帽（三尖）
        hat_colors = [(255, 50, 100), (100, 255, 150), (255, 255, 100)]
        for tip_i in range(3):
            tip_angle = (tip_i * 120 - 90 + math.sin(t * 5) * 10) * 0.01745
            tip_x = 60 + math.cos(tip_angle) * 30
            tip_y = 45 + math.sin(tip_angle) * 20
            pygame.draw.polygon(s, hat_colors[tip_i], 
                              [(60, 50), (tip_x - 5, tip_y), (tip_x + 5, tip_y)])
            # 铃铛
            pygame.draw.circle(s, (255, 215, 0), (int(tip_x), int(tip_y) - 5), 4)
        # 脸
        pygame.draw.circle(s, (255, 255, 255), (60, 60), 20)
        # 疯狂笑容
        smile_width = 12 + int(3 * math.sin(t * 8))
        pygame.draw.arc(s, (255, 50, 100), (48, 55, smile_width * 2, 15), 3.14, 0, 3)
        # 眼睛（不对称）
        pygame.draw.circle(s, (50, 50, 50), (52, 55), 4)
        pygame.draw.circle(s, (50, 50, 50), (68, 58), 5)  # 一大一小
        # 红鼻子
        pygame.draw.circle(s, (255, 50, 50), (60, 62), 5)
        # 混沌粒子
        for chaos_i in range(16):
            chaos_angle = (chaos_i * 22.5 + t * 30) * 0.01745
            chaos_r = 40 + int(5 * math.sin(t * 5 + chaos_i))
            chaos_x = 60 + math.cos(chaos_angle) * chaos_r
            chaos_y = 60 + math.sin(chaos_angle) * chaos_r
            chaos_color = hat_colors[chaos_i % 3]
            pygame.draw.circle(s, chaos_color, (int(chaos_x), int(chaos_y)), 3)
    
    if pid == "striker": 
        # 攻击型：脉动菱形 + 闪烁能量核心
        pygame.draw.polygon(s, (50, 100, 150), [(60, 10), (110, 90), (60, 110), (10, 90)])
        pygame.draw.polygon(s, c, [(60, 15), (105, 90), (60, 105), (15, 90)])
        pygame.draw.polygon(s, edge_color, [(60, 15), (105, 90), (60, 105), (15, 90)], 3)
        pygame.draw.polygon(s, (255, 200, 0), [(60, 35), (90, 90), (60, 100), (30, 90)], 1)
        # 动态：能量核心脉动大小
        core_size = int(5 + 3 * pulse)
        pygame.draw.circle(s, (255, 100 + int(155 * pulse), 100), (60, 50), core_size)
        
    elif pid == "phantom": 
        # 幽灵型：六边形 + 旋转能量点
        main_color = (200, 100, 255)
        pygame.draw.polygon(s, (100, 50, 150), [(60, 10), (90, 50), (120, 110), (60, 90), (0, 110), (30, 50)])
        pygame.draw.polygon(s, main_color, [(60, 15), (88, 52), (115, 105), (60, 88), (5, 105), (32, 52)])
        pygame.draw.polygon(s, edge_color, [(60, 15), (88, 52), (115, 105), (60, 88), (5, 105), (32, 52)], 2)
        # 动态：能量点旋转
        for i in range(3):
            angle = t * 2 + (i * 2 * math.pi / 3)
            x = 60 + math.cos(angle) * 15
            y = 70 + math.sin(angle) * 10
            pygame.draw.circle(s, (150 + int(100 * pulse), 200, 255), (int(x), int(y)), 4)
            
    elif pid == "titan": 
        # 巨人型：厚重感 + 闪烁炮塔
        pygame.draw.rect(s, (80, 50, 20), (18, 18, 84, 84))
        pygame.draw.rect(s, CYBER_AMBER, (20, 20, 80, 80))
        pygame.draw.rect(s, (255, 200, 0), (20, 20, 80, 80), 3)
        tower_brightness = int(100 + 155 * pulse)
        pygame.draw.rect(s, (tower_brightness, tower_brightness // 2, 0), (40, 5, 40, 35))
        pygame.draw.rect(s, (200, 150, 50), (35, 35, 50, 50), 2)
        pygame.draw.circle(s, (255, 255, int(100 * pulse)), (60, 60), 12)
        
    elif pid == "thunderbird": 
        # 雷鸟型：眼睛闪烁 + 翅膀脉动
        main_color = (255, 200, 0)
        pygame.draw.polygon(s, (100, 80, 0), [(60, 0), (20, 60), (0, 40), (20, 100), (60, 80), (100, 100), (120, 40), (100, 60)])
        pygame.draw.polygon(s, main_color, [(60, 5), (25, 60), (5, 40), (25, 95), (60, 75), (95, 95), (115, 40), (95, 60)])
        pygame.draw.polygon(s, edge_color, [(60, 5), (25, 60), (5, 40), (25, 95), (60, 75), (95, 95), (115, 40), (95, 60)], 2)
        # 动态：眼睛闪烁
        eye_bright = int(100 + 155 * pulse)
        pygame.draw.circle(s, (eye_bright, 200, 255), (60, 40), 8)
        
    elif pid == "viper": 
        # 毒蛇型：毒囊呼吸 + 眼睛跟踪
        main_color = (100, 200, 50)
        pygame.draw.polygon(s, (50, 100, 30), [(60, 0), (100, 40), (80, 100), (40, 100), (20, 40)])
        pygame.draw.polygon(s, main_color, [(60, 5), (95, 42), (78, 95), (42, 95), (25, 42)])
        pygame.draw.polygon(s, edge_color, [(60, 5), (95, 42), (78, 95), (42, 95), (25, 42)], 2)
        # 动态：毒囊呼吸
        toxin_scale = 1 + 0.4 * pulse
        toxin_points = [(60, int(20 + 5 * pulse)), (int(70 + 5 * pulse), 60), (60, int(50 - 5 * pulse)), (int(50 - 5 * pulse), 60)]
        pygame.draw.polygon(s, (255, int(100 * pulse), 0), toxin_points, 1)
        pygame.draw.circle(s, (255, 100 + int(155 * pulse), 0), (60, 30), 4)
        
    elif pid == "specter": 
        # 幽灵型：透明度脉动 + 能量波纹
        pygame.draw.polygon(s, (30, 40, 80), [(60, 0), (80, 80), (60, 100), (40, 80)])
        pygame.draw.polygon(s, (150, 180, 255), [(60, 5), (78, 78), (60, 95), (42, 78)])
        pygame.draw.polygon(s, edge_color, [(60, 5), (78, 78), (60, 95), (42, 78)], 3)
        pygame.draw.circle(s, WHITE, (60, 50), 8)
        pygame.draw.circle(s, (100, 150, 255), (60, 50), 5)
        # 动态：能量波纹
        ripple_r = int(15 + 5 * pulse)
        pygame.draw.circle(s, (100 + int(155 * pulse), 200, 255), (60, 50), ripple_r, 1)
        
    elif pid == "aurora": 
        # 极光型：彩虹色旋转 + 多环脉动
        pygame.draw.circle(s, (80, 50, 100), (60, 60), 52)
        pygame.draw.circle(s, (150, 100, 200), (60, 60), 50)
        pygame.draw.circle(s, edge_color, (60, 60), 50, 2)
        # 动态：彩虹色环旋转
        angle = t * 2
        r = int(35 + 5 * pulse)
        color_val = int(200 + 55 * pulse)
        pygame.draw.circle(s, (color_val, 100, 200), (60, 60), r, 1)
        pygame.draw.circle(s, WHITE, (60, 60), 20)
        pygame.draw.circle(s, (255 - int(100 * pulse), 100, 200), (60, 60), 10)
        
    elif pid == "crimson": 
        # 猩红型：能量条闪烁 + 边框脉动
        pygame.draw.polygon(s, (100, 20, 20), [(50, 80), (20, 20), (50, 40), (80, 20)])
        pygame.draw.polygon(s, CYBER_RED_ALERT, [(50, 78), (22, 22), (50, 42), (78, 22)])
        pygame.draw.polygon(s, (255, 100, 100), [(50, 78), (22, 22), (50, 42), (78, 22)], 3)
        # 动态：能量条颜色脉动
        energy_color_r = int(255 * pulse)
        pygame.draw.line(s, (energy_color_r, int(200 * pulse), 0), (50, 80), (50, 10), 4)
        pygame.draw.line(s, WHITE, (50, 80), (50, 10), 2)
        
    elif pid == "stalker": 
        # 潜行者型：眼睛扫描 + 隐身脉动
        main_color = (100, 120, 150)
        pygame.draw.polygon(s, (50, 60, 80), [(50, 10), (30, 50), (10, 40), (30, 70), (50, 90), (70, 70), (90, 40), (70, 50)])
        pygame.draw.polygon(s, main_color, [(50, 12), (32, 50), (12, 40), (32, 68), (50, 88), (68, 68), (88, 40), (68, 50)])
        pygame.draw.polygon(s, edge_color, [(50, 12), (32, 50), (12, 40), (32, 68), (50, 88), (68, 68), (88, 40), (68, 50)], 2)
        # 动态：三个眼睛扫描
        for idx, x in enumerate([30, 50, 70]):
            eye_bright = int(255 * abs(math.sin(t * 3 + idx)))
            pygame.draw.circle(s, (eye_bright, 100, 0), (x, 30), 5)
            pygame.draw.circle(s, BLACK, (x, 30), 3)
            
    elif pid == "gaia": 
        # 盖亚型：中心生长脉动 + 能量流动
        main_color = (100, 200, 100)
        pygame.draw.polygon(s, (50, 100, 50), [(30, 20), (70, 20), (90, 60), (70, 90), (30, 90), (10, 60)])
        pygame.draw.polygon(s, main_color, [(32, 22), (68, 22), (88, 60), (68, 88), (32, 88), (12, 60)])
        pygame.draw.polygon(s, edge_color, [(32, 22), (68, 22), (88, 60), (68, 88), (32, 88), (12, 60)], 2)
        # 动态：中心圆脉动生长
        core_r = int(22 + 5 * pulse)
        pygame.draw.circle(s, CYBER_LIME, (50, 50), core_r)
        pygame.draw.circle(s, (200, 255, 100), (50, 50), int(18 + 3 * pulse))
        pygame.draw.circle(s, (100, 150, 100), (50, 50), 8)
        
    elif pid == "weaver": 
        # 织网者型：蜘蛛网旋转 + 中心脉动
        pygame.draw.circle(s, (80, 80, 100), (60, 60), 26)
        pygame.draw.circle(s, (200, 200, 220), (60, 60), 25)
        pygame.draw.circle(s, edge_color, (60, 60), 25, 2)
        pygame.draw.circle(s, WHITE, (60, 60), 15)
        pygame.draw.circle(s, (100, 150, 200), (60, 60), 10)
        # 动态：蜘蛛网旋转
        for angle in range(0, 360, 45):
            rad = math.radians(angle + t * 50)
            x = 60 + math.cos(rad) * 30
            y = 60 + math.sin(rad) * 30
            web_color = (int(150 + 100 * pulse), 180, 200)
            pygame.draw.line(s, web_color, (60, 60), (x, y), 1)
            
    elif pid == "solar": 
        # 太阳型：放射线旋转 + 脉冲能量
        pygame.draw.circle(s, (100, 50, 0), (60, 60), 32)
        pygame.draw.circle(s, CYBER_AMBER, (60, 60), 30)
        pygame.draw.circle(s, (255, 200, 0), (60, 60), 30, 2)
        # 动态：8条放射线旋转
        for i in range(8):
            angle = (t * 2 + i * 45) * math.pi / 180
            x1 = 60 + math.cos(angle) * (25 + int(10 * pulse))
            y1 = 60 + math.sin(angle) * (25 + int(10 * pulse))
            x2 = 60 + math.cos(angle) * (45 + int(10 * pulse))
            y2 = 60 + math.sin(angle) * (45 + int(10 * pulse))
            pygame.draw.line(s, (255, 255, int(100 * pulse)), (int(x1), int(y1)), (int(x2), int(y2)), 2)
        pygame.draw.circle(s, (255, 255, int(100 + 155 * pulse)), (60, 60), 12)
        
    elif pid == "arbiter": 
        # 仲裁者型：内部正方形旋转 + 能量脉冲
        main_color = (100, 150, 200)
        pygame.draw.polygon(s, (50, 75, 100), [(60, 10), (110, 60), (60, 110), (10, 60)])
        pygame.draw.polygon(s, main_color, [(60, 12), (108, 60), (60, 108), (12, 60)])
        pygame.draw.polygon(s, edge_color, [(60, 12), (108, 60), (60, 108), (12, 60)], 2)
        # 动态：内部正方形旋转
        angle = t * 2
        size = 15 + int(8 * pulse)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        corners = [
            (60 + cos_a * size - sin_a * size, 60 + sin_a * size + cos_a * size),
            (60 + cos_a * size + sin_a * size, 60 + sin_a * size - cos_a * size),
            (60 - cos_a * size + sin_a * size, 60 - sin_a * size - cos_a * size),
            (60 - cos_a * size - sin_a * size, 60 - sin_a * size + cos_a * size),
        ]
        pygame.draw.polygon(s, (100 + int(155 * pulse), 200, 255), corners)
        pygame.draw.circle(s, (200, 255, 255), (60, 60), 6)
        
    elif pid == "eclipse":
        # 日食幽灵型：双核心 + 吸收光芒
        pygame.draw.circle(s, (30, 20, 50), (40, 60), 28)
        pygame.draw.circle(s, (150, 50, 200), (40, 60), 26)
        pygame.draw.circle(s, (30, 20, 50), (80, 60), 28)
        pygame.draw.circle(s, (150, 50, 200), (80, 60), 26)
        pygame.draw.line(s, (100, 50, 180), (40, 60), (80, 60), 3)
        # 中间连接体
        pygame.draw.rect(s, (100, 50, 180), (52, 54, 16, 12))
        # 动态：吸收光晕脉动
        aura_r = int(32 + 8 * pulse)
        pygame.draw.circle(s, (200, 100, 255), (40, 60), aura_r, 1)
        pygame.draw.circle(s, (200, 100, 255), (80, 60), aura_r, 1)
        # 能量流
        for i in range(3):
            offset = i * 8 - 8
            pygame.draw.line(s, (150 + int(100 * pulse), 50 + int(150 * pulse), 200), (40, 60 + offset), (80, 60 + offset), 1)
        
    elif pid == "prism":
        # 棱镜分光型：三棱柱 + 光谱分解
        # 三个主色：红绿蓝
        pygame.draw.polygon(s, (50, 100, 150), [(60, 5), (40, 90), (80, 90)])
        pygame.draw.polygon(s, (0, 255, 200), [(60, 8), (42, 88), (78, 88)])
        pygame.draw.polygon(s, edge_color, [(60, 8), (42, 88), (78, 88)], 2)
        # 三条能量射线
        for angle, color in [(0, (255, 100, 100)), (120, (100, 255, 100)), (240, (100, 100, 255))]:
            rad = math.radians(angle)
            start_x, start_y = 60, 45
            end_x = start_x + math.cos(rad) * 35
            end_y = start_y + math.sin(rad) * 35
            pygame.draw.line(s, color, (int(start_x), int(start_y)), (int(end_x), int(end_y)), 2)
            # 脉动的光点
            pulsing_r = int(3 + 2 * abs(math.sin(t * 4 + angle)))
            pygame.draw.circle(s, color, (int(end_x), int(end_y)), pulsing_r)
        # 中心棱镜
        pygame.draw.circle(s, (150, 200, 255), (60, 45), 8)
        
    elif pid == "necro":
        # 死灵骑士型：骷髅头 + 吸血能量
        # 头骨主体
        pygame.draw.circle(s, (80, 80, 100), (60, 45), 22)
        pygame.draw.circle(s, (150, 50, 150), (60, 45), 20)
        pygame.draw.rect(s, (80, 80, 100), (45, 55, 30, 30))
        pygame.draw.rect(s, (150, 50, 150), (47, 57, 26, 26))
        # 眼窝
        pygame.draw.circle(s, BLACK, (52, 40), 5)
        pygame.draw.circle(s, BLACK, (68, 40), 5)
        pygame.draw.circle(s, (255, 100, 150), (52, 40), 2)
        pygame.draw.circle(s, (255, 100, 150), (68, 40), 2)
        # 骨架肋部（下半身）
        for i, x in enumerate([45, 60, 75]):
            pygame.draw.line(s, (150, 50, 150), (x, 80), (x - 5, 105), 3)
        # 动态：吸血能量脉冲
        vampire_pulse = int(100 + 155 * pulse)
        pygame.draw.circle(s, (vampire_pulse, 50, 150), (60, 45), 24, 2)
        # 能量流向
        for offset in range(-10, 15, 5):
            pygame.draw.line(s, (200, 50, 150), (40, 60 + offset), (50, 70 + offset), 1)
    
    elif pid == "wormhole":
        # ========== Wormhole 专属涂装 ==========
        if model_style == "wormhole_monsoon":
            # 季风洪流·水龙卷暴 - 三重水龙卷螺旋，雷电闪烁
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 三重水龙卷螺旋
            for layer in range(3):
                for i in range(12):
                    spiral_angle = (t * 5 + i * 30 + layer * 40) * 0.01745
                    spiral_r = 15 + layer * 8 + i * 1.5
                    sx = 60 + math.cos(spiral_angle) * spiral_r
                    sy = 60 + math.sin(spiral_angle) * spiral_r
                    color_intensity = 100 + layer * 40
                    pygame.draw.circle(s, (60 + layer * 20, color_intensity, 220), (int(sx), int(sy)), 3 - layer)
            # 雷电闪烁效果
            if int(t * 8) % 4 < 2:
                lightning_points = [(60, 20), (55, 40), (65, 50), (60, 70)]
                pygame.draw.lines(s, (255, 255, 255), False, lightning_points, 4)
                pygame.draw.lines(s, (100, 200, 255), False, lightning_points, 2)
            # 水滴爆炸粒子
            for i in range(20):
                drop_angle = (t * 3 + i * 18) * 0.01745
                drop_r = 25 + math.sin(t * 4 + i) * 8
                dx = 60 + math.cos(drop_angle) * drop_r
                dy = 60 + math.sin(drop_angle) * drop_r
                pygame.draw.circle(s, (100, 200, 255), (int(dx), int(dy)), 2)
            # 蓝色涡旋核心
            pygame.draw.circle(s, (60, 140, 220), (60, 60), 12)
            pygame.draw.circle(s, (100, 200, 255), (60, 60), 8)
        
        elif model_style == "wormhole_mirage":
            # 蜃景幻界·折光异象 - 热浪波纹扭曲，半透明虚影分身
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 热浪波纹扭曲效果（8层）
            for i in range(8):
                wave_y = 20 + i * 12
                wave_points = []
                for x in range(0, 130, 8):
                    distort_y = wave_y + math.sin(x * 0.08 + t * 4 + i * 0.5) * 6
                    wave_points.append((x, int(distort_y)))
                if len(wave_points) > 1:
                    alpha = 120 - i * 12
                    pygame.draw.lines(s, (255, 200, 100, alpha), False, wave_points, 2)
            # 半透明虚影重叠（3个分身）
            for offset in [-10, 0, 10]:
                alpha = 180 if offset == 0 else 100
                phantom_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(phantom_surf, (255, 200, 100, alpha), (60 + offset, 60), 18)
                pygame.draw.circle(phantom_surf, (80, 180, 255, alpha), (60 + offset, 60), 14, 2)
                s.blit(phantom_surf, (0, 0))
            # 七彩折射光束
            for i in range(6):
                ray_angle = (t * 2 + i * 60) * 0.01745
                ray_end_x = 60 + math.cos(ray_angle) * 35
                ray_end_y = 60 + math.sin(ray_angle) * 35
                rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 127, 255), (148, 0, 211)]
                pygame.draw.line(s, rainbow_colors[i % 6], (60, 60), (int(ray_end_x), int(ray_end_y)), 2)
        
        elif model_style == "wormhole_bonsai":
            # 禅庭之心·生灵盆栽 - 树枝蜿蜒生长，绿叶螺旋环绕
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 盆景底座（更细致）
            pygame.draw.rect(s, (100, 80, 60), (35, 85, 50, 12))
            pygame.draw.rect(s, (140, 120, 100), (35, 85, 50, 12), 2)
            # 蜿蜒树干（分段绘制生长感）
            trunk_points = []
            for i in range(8):
                trunk_x = 60 + math.sin(i * 0.3 + t * 0.5) * 5
                trunk_y = 85 - i * 7
                trunk_points.append((int(trunk_x), int(trunk_y)))
            if len(trunk_points) > 1:
                pygame.draw.lines(s, (80, 60, 40), False, trunk_points, 6)
            # 蜿蜒枝干（4条）
            for branch_i in range(4):
                branch_angle = branch_i * 90 + 45
                branch_points = [(60, 50)]
                for seg in range(4):
                    seg_angle = (branch_angle + math.sin(t + seg) * 15) * 0.01745
                    seg_r = 8 + seg * 6
                    bx = 60 + math.cos(seg_angle) * seg_r
                    by = 50 + math.sin(seg_angle) * seg_r
                    branch_points.append((int(bx), int(by)))
                if len(branch_points) > 1:
                    pygame.draw.lines(s, (100, 80, 60), False, branch_points, 3)
            # 绿叶螺旋环绕（12片）
            for i in range(12):
                leaf_angle = (t * 3 + i * 30) * 0.01745
                leaf_r = 20 + math.sin(t * 2 + i) * 5
                lx = 60 + math.cos(leaf_angle) * leaf_r
                ly = 50 + math.sin(leaf_angle) * leaf_r
                leaf_color = (50 + i * 8, 140, 90)
                pygame.draw.ellipse(s, leaf_color, (int(lx) - 4, int(ly) - 3, 8, 6))
            # 根须发光脉动
            root_glow = int(abs(math.sin(t * 3)) * 50) + 50
            pygame.draw.circle(s, (50, root_glow, 90, 80), (60, 85), 25)
        
        elif model_style == "wormhole_lantern":
            # 千灯夜宴·炫光祈愿 - 六边形灯笼旋转，烛火摇曳光晕
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 中心主灯笼（六边形）
            hex_points = []
            for i in range(6):
                hex_angle = (i * 60 + t * 20) * 0.01745
                hex_x = 60 + math.cos(hex_angle) * 18
                hex_y = 60 + math.sin(hex_angle) * 18
                hex_points.append((int(hex_x), int(hex_y)))
            pygame.draw.polygon(s, (255, 220, 150, 200), hex_points)
            pygame.draw.polygon(s, (255, 180, 60), hex_points, 3)
            # 连接中心线（纸质纹理）
            for point in hex_points:
                pygame.draw.line(s, (240, 200, 130), (60, 60), point, 1)
            # 烛火核心（摇曳效果）
            flicker = int(abs(math.sin(t * 6)) * 8)
            pygame.draw.ellipse(s, (255, 200, 80), (52, 52 - flicker, 16, 20 + flicker))
            pygame.draw.circle(s, (255, 255, 200), (60, 56 - flicker), 6)
            # 温暖光晕脉冲（3层）
            for ring in range(3):
                glow_r = 25 + ring * 12 + int(pulse * 10)
                glow_alpha = 120 - ring * 35
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 220, 100, glow_alpha), (60, 60), glow_r)
                s.blit(glow_surf, (0, 0))
            # 周围小灯笼升空
            for i in range(4):
                small_ly = 100 - int((t * 15 + i * 30) % 120)
                small_lx = 20 + i * 25
                pygame.draw.rect(s, (255, 200, 100), (small_lx, small_ly, 12, 16), 2)
                pygame.draw.circle(s, (255, 220, 120, 150), (small_lx + 6, small_ly + 8), 10)
        
        elif model_style == "wormhole_geode":
            # 晶洞星爆·紫晶能核 - 多面紫晶旋转，能量脉冲爆发，裂纹闪电
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 多面紫晶外壳（12面体旋转）
            crystal_points = []
            for i in range(12):
                crystal_angle = (i * 30 + t * 40) * 0.01745
                crystal_r = 28 if i % 2 == 0 else 22
                cx = 60 + math.cos(crystal_angle) * crystal_r
                cy = 60 + math.sin(crystal_angle) * crystal_r
                crystal_points.append((int(cx), int(cy)))
            pygame.draw.polygon(s, (180, 100, 240, 200), crystal_points)
            pygame.draw.polygon(s, (140, 60, 240), crystal_points, 3)
            # 内部晶面三角形
            for i in range(0, 12, 2):
                triangle = [(60, 60), crystal_points[i], crystal_points[(i+2) % 12]]
                inner_color = (140 + i * 8, 60 + i * 5, 200 + i * 4)
                pygame.draw.polygon(s, inner_color, triangle)
            # 能量脉冲（3层渐变）
            pulse_intensity = int(abs(math.sin(t * 4)) * 50) + 150
            for ring in range(3):
                pulse_r = 8 + ring * 6 + int(pulse * 8)
                pulse_alpha = 200 - ring * 50
                pygame.draw.circle(s, (180, 100, 240, pulse_alpha), (60, 60), pulse_r)
            # 裂纹闪电四射（8道）
            for i in range(8):
                lightning_angle = (i * 45 + t * 30) * 0.01745
                lightning_segments = []
                for seg in range(4):
                    seg_r = 18 + seg * 8
                    seg_x = 60 + math.cos(lightning_angle) * seg_r + random.randint(-2, 2)
                    seg_y = 60 + math.sin(lightning_angle) * seg_r + random.randint(-2, 2)
                    lightning_segments.append((int(seg_x), int(seg_y)))
                if len(lightning_segments) > 1:
                    pygame.draw.lines(s, (200, 120, 255), False, lightning_segments, 2)
            # 水晶碎片螺旋
            for i in range(6):
                shard_angle = (t * 6 + i * 60) * 0.01745
                shard_r = 35 + math.sin(t * 3 + i) * 5
                sx = 60 + math.cos(shard_angle) * shard_r
                sy = 60 + math.sin(shard_angle) * shard_r
                pygame.draw.circle(s, (200, 140, 255), (int(sx), int(sy)), 3)
        
        elif model_style == "wormhole_totem":
            # 祖灵图腾·古神降临 - 三层图腾旋转，符文闪烁，灵魂能量环
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 三层图腾柱（带旋转效果）
            for layer in range(3):
                layer_y = 25 + layer * 25
                layer_rotation = math.sin(t * 2 + layer) * 5
                # 图腾段
                totem_rect = (48 + layer_rotation, layer_y, 24, 22)
                pygame.draw.rect(s, (200 - layer * 20, 100 - layer * 15, 40), totem_rect)
                pygame.draw.rect(s, (220 - layer * 15, 130 - layer * 10, 60), totem_rect, 3)
                # 雕刻纹路
                for line_i in range(3):
                    carve_y = layer_y + 4 + line_i * 6
                    pygame.draw.line(s, (120, 80, 40), (52, carve_y), (68, carve_y), 2)
                # 图腾面孔眼睛
                eye_y = layer_y + 12
                pygame.draw.circle(s, (255, 220, 150), (55, eye_y), 3)
                pygame.draw.circle(s, (255, 220, 150), (65, eye_y), 3)
                pygame.draw.circle(s, (100, 60, 20), (55, eye_y), 2)
                pygame.draw.circle(s, (100, 60, 20), (65, eye_y), 2)
                # 眼睛发光
                if int(t * 3 + layer) % 2 == 0:
                    glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (255, 220, 100, 150), (55, eye_y), 6)
                    pygame.draw.circle(glow_surf, (255, 220, 100, 150), (65, eye_y), 6)
                    s.blit(glow_surf, (0, 0))
            # 符文连续闪烁（8个环绕）
            for i in range(8):
                rune_angle = (i * 45 + t * 50) * 0.01745
                rune_r = 35
                rune_x = 60 + math.cos(rune_angle) * rune_r
                rune_y = 60 + math.sin(rune_angle) * rune_r
                rune_brightness = int(abs(math.sin(t * 5 + i)) * 155) + 100
                pygame.draw.circle(s, (255, rune_brightness, 50), (int(rune_x), int(rune_y)), 4)
                pygame.draw.circle(s, (255, 255, 150), (int(rune_x), int(rune_y)), 2)
            # 灵魂能量环螺旋上升（4层）
            for ring_i in range(4):
                ring_y = 90 - ring_i * 15 - int(t * 20) % 60
                ring_r = 20 + ring_i * 5
                ring_alpha = 120 - ring_i * 25
                pygame.draw.circle(s, (200, 150, 100, ring_alpha), (60, ring_y), ring_r, 2)
        
        elif model_style == "wormhole_ruins":
            # 失落帝国·时光回溯 - 石碑浮现消失，文字点亮，时空波纹
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 石碑浮现消失循环
            tablet_phase = (t * 0.8) % 2.0
            tablet_alpha = int(abs(math.sin(tablet_phase * 1.57)) * 200)
            tablet_points = [
                (40, 30), (80, 32), (85, 60), (78, 88), (42, 86), (35, 58)
            ]
            tablet_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(tablet_surf, (100, 110, 140, tablet_alpha), tablet_points)
            pygame.draw.polygon(tablet_surf, (130, 140, 170, tablet_alpha), tablet_points, 3)
            s.blit(tablet_surf, (0, 0))
            # 古文字符号逐个点亮（8个）
            for i in range(8):
                text_x = 45 + (i % 3) * 12
                text_y = 40 + (i // 3) * 15
                text_phase = (t * 2 + i * 0.3) % 1.0
                if text_phase > 0.2:
                    text_brightness = int(min(text_phase * 255, 200))
                    # 竖线
                    pygame.draw.line(s, (text_brightness, text_brightness - 30, 150), 
                                   (text_x, text_y - 4), (text_x, text_y + 4), 2)
                    # 横线或点
                    if i % 2 == 0:
                        pygame.draw.line(s, (text_brightness, text_brightness - 30, 150),
                                       (text_x - 3, text_y), (text_x + 3, text_y), 2)
                    else:
                        pygame.draw.circle(s, (text_brightness, text_brightness - 30, 150), (text_x, text_y), 2)
            # 历史波纹时空扩散
            echo_phase = (t * 1.5) % 1.0
            for echo_i in range(3):
                echo_r = int((20 + echo_i * 15) * (1 + echo_phase * 1.5))
                echo_alpha = int((140 - echo_i * 40) * (1 - echo_phase))
                if echo_alpha > 0:
                    pygame.draw.circle(s, (150, 160, 190, echo_alpha), (60, 60), echo_r, 2)
            # 裂痕发光重组（5条）
            for crack_i in range(5):
                crack_angle = crack_i * 72
                crack_progress = (t + crack_i * 0.2) % 1.0
                if crack_progress < 0.7:  # 显示70%时间
                    crack_len = int(25 * crack_progress)
                    crack_x = 60 + int(math.cos(crack_angle * 0.01745) * crack_len)
                    crack_y = 60 + int(math.sin(crack_angle * 0.01745) * crack_len)
                    pygame.draw.line(s, (180, 200, 230), (60, 60), (crack_x, crack_y), 2)
                    # 裂痕端点发光
                    pygame.draw.circle(s, (200, 220, 255), (crack_x, crack_y), 3)
        
        elif model_style == "wormhole_teaceremony":
            # 茶香灵境·悟道之境 - 茶叶螺旋舞动，蒸汽形成禅意文字
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 茶碗（更精致）
            pygame.draw.ellipse(s, (150, 180, 120), (38, 55, 44, 35))
            pygame.draw.ellipse(s, (180, 210, 150), (38, 55, 44, 35), 2)
            pygame.draw.ellipse(s, (120, 150, 100), (42, 75, 36, 12))
            # 茶叶螺旋漂浮舞动（10片）
            for i in range(10):
                leaf_spiral_angle = (t * 3 + i * 36) * 0.01745
                leaf_r = 15 + math.sin(t * 2 + i) * 8
                leaf_x = 60 + math.cos(leaf_spiral_angle) * leaf_r
                leaf_y = 65 + math.sin(leaf_spiral_angle) * leaf_r * 0.7
                # 茶叶椭圆形
                leaf_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.ellipse(leaf_surf, (80, 140, 80), (int(leaf_x) - 4, int(leaf_y) - 2, 8, 5))
                pygame.draw.ellipse(leaf_surf, (100, 160, 100), (int(leaf_x) - 4, int(leaf_y) - 2, 8, 5), 1)
                s.blit(leaf_surf, (0, 0))
            # 蒸汽形成禅意符号（升腾）
            steam_chars = ['茶', '禅', '静']
            for i in range(6):
                steam_y = 55 - i * 12 - int(t * 20) % 70
                steam_x = 60 + math.sin(t * 1.5 + i * 0.8) * 8
                steam_alpha = max(0, 180 - i * 25 - int(t * 20) % 70)
                if steam_alpha > 0:
                    # 简化为圆形粒子
                    steam_size = 4 + i // 2
                    pygame.draw.circle(s, (200, 230, 200, steam_alpha), (int(steam_x), int(steam_y)), steam_size)
            # 茶水涟漪波纹扩散
            ripple_phase = (t * 2) % 1.5
            for ripple_i in range(3):
                ripple_r = int((10 + ripple_i * 8) * (1 + ripple_phase))
                ripple_alpha = int((120 - ripple_i * 30) * (1 - ripple_phase / 1.5))
                if ripple_alpha > 0:
                    pygame.draw.ellipse(s, (150, 200, 120, ripple_alpha), 
                                      (60 - ripple_r, 65 - ripple_r // 2, ripple_r * 2, ripple_r), 2)
            # 翠绿光晕柔和脉动
            zen_glow = int(abs(math.sin(t * 1.5)) * 40) + 40
            zen_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(zen_surf, (120, 180, 100, zen_glow), (60, 60), 45)
            s.blit(zen_surf, (0, 0))
        
        elif model_style == "wormhole_windchime":
            # 音波共振·水晶风铃 - 可见音波环，彩虹扩散，曼德拉图案
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 中心吊环
            pygame.draw.circle(s, (200, 220, 255), (60, 25), 10, 3)
            pygame.draw.circle(s, (180, 220, 255), (60, 25), 6)
            # 风铃铃铛旋转（8个）
            for i in range(8):
                chime_angle = (i * 45 + t * 30) * 0.01745
                chime_swing = math.sin(t * 3 + i) * 4
                chime_r = 20 + chime_swing
                chime_x = 60 + math.cos(chime_angle) * chime_r
                chime_y = 35 + math.sin(chime_angle) * chime_r * 0.5
                # 吊线
                pygame.draw.line(s, (180, 200, 240), (60, 25), (int(chime_x), int(chime_y)), 1)
                # 铃铛（水晶质感）
                pygame.draw.circle(s, (150, 180, 220), (int(chime_x), int(chime_y)), 5)
                pygame.draw.circle(s, (200, 230, 255), (int(chime_x), int(chime_y)), 3)
            # 可见音波涟漪（彩虹扩散）
            wave_phase = (t * 2.5) % 1.0
            rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 127, 255), (148, 0, 211)]
            for wave_ring in range(6):
                wave_r = int((15 + wave_ring * 10) * (1 + wave_phase * 2))
                wave_alpha = int((150 - wave_ring * 20) * (1 - wave_phase))
                if wave_alpha > 0:
                    wave_color = rainbow_colors[wave_ring % len(rainbow_colors)]
                    pygame.draw.circle(s, (*wave_color, wave_alpha), (60, 60), wave_r, 2)
            # 曼德拉共振图案（8角星）
            mandala_points = []
            for star_i in range(8):
                star_angle = (star_i * 45 + t * 20) * 0.01745
                star_r = 28 + math.sin(t * 4 + star_i) * 5
                star_x = 60 + math.cos(star_angle) * star_r
                star_y = 60 + math.sin(star_angle) * star_r
                mandala_points.append((int(star_x), int(star_y)))
            if len(mandala_points) > 1:
                pygame.draw.lines(s, (150, 200, 250), True, mandala_points, 2)
        
        elif model_style == "wormhole_silk_road":
            # 丝路传说·驼影商道 - 丝绸龙舞，驼队光轨，文化交融
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 丝绸龙舞飘带（3条大型）
            for ribbon_i in range(3):
                ribbon_points = []
                for seg in range(15):
                    seg_x = seg * 9
                    seg_y = 30 + ribbon_i * 20 + math.sin(t * 2 + seg * 0.4 + ribbon_i) * 12
                    ribbon_points.append((seg_x, int(seg_y)))
                if len(ribbon_points) > 1:
                    # 丝绸渐变色
                    ribbon_colors = [(255, 190, 130), (240, 180, 120), (220, 160, 100)]
                    pygame.draw.lines(s, ribbon_colors[ribbon_i], False, ribbon_points, 4)
                    pygame.draw.lines(s, (255, 220, 160), False, ribbon_points, 2)
            # 驼队剪影留光轨
            for camel_i in range(4):
                camel_x = 15 + int((t * 25 + camel_i * 30) % 120)
                camel_y = 75
                # 驼峰
                pygame.draw.circle(s, (200, 150, 100), (camel_x, camel_y - 8), 10)
                # 驼身
                pygame.draw.ellipse(s, (200, 150, 100), (camel_x - 8, camel_y, 16, 12))
                # 光轨尾迹
                trail_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                for trail_seg in range(5):
                    trail_x = camel_x - trail_seg * 8
                    if 0 <= trail_x <= 120:
                        trail_alpha = 100 - trail_seg * 18
                        pygame.draw.circle(trail_surf, (255, 200, 130, trail_alpha), (trail_x, camel_y + 6), 6 - trail_seg)
                s.blit(trail_surf, (0, 0))
            # 东西文化符号交织（6种）
            symbols = ['星', '月', '太阳', '花', '符', '文']
            for sym_i in range(6):
                sym_angle = (sym_i * 60 + t * 40) * 0.01745
                sym_r = 35
                sym_x = 60 + math.cos(sym_angle) * sym_r
                sym_y = 60 + math.sin(sym_angle) * sym_r
                # 用圆形代表符号
                sym_size = 4 + int(abs(math.sin(t * 3 + sym_i)) * 3)
                pygame.draw.circle(s, (255, 200, 150), (int(sym_x), int(sym_y)), sym_size)
                pygame.draw.circle(s, (220, 160, 100), (int(sym_x), int(sym_y)), sym_size, 1)
            # 金币粒子飞散
            for coin_i in range(10):
                coin_angle = (t * 5 + coin_i * 36) * 0.01745
                coin_r = 25 + math.sin(t * 3 + coin_i) * 8
                coin_x = 60 + math.cos(coin_angle) * coin_r
                coin_y = 60 + math.sin(coin_angle) * coin_r
                pygame.draw.circle(s, (255, 215, 0), (int(coin_x), int(coin_y)), 3)
                pygame.draw.circle(s, (255, 255, 100), (int(coin_x), int(coin_y)), 2)
        
        elif model_style == "wormhole_supercell":
            # 龙卷母胎·风暴之眼 - 三层嵌套涡旋，墙云下降，雷暴电弧
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 超级雷暴云团（上层）
            for cloud_i in range(12):
                cloud_x = 20 + cloud_i * 9 + math.sin(t * 1.5 + cloud_i) * 6
                cloud_y = 15 + math.cos(t * 2 + cloud_i) * 4
                cloud_size = 6 + int(abs(math.sin(t + cloud_i)) * 3)
                pygame.draw.circle(s, (60, 90, 130), (int(cloud_x), int(cloud_y)), cloud_size)
            # 三层嵌套涡旋（疯狂旋转）
            for vortex_layer in range(3):
                vortex_speed = 5 - vortex_layer * 1.5
                for ring in range(8):
                    ring_angle = (t * vortex_speed - ring * 0.4 - vortex_layer * 0.8) % 6.28
                    ring_radius = 12 + ring * 4 + vortex_layer * 8
                    # 涡旋粒子位置
                    for seg in range(12):
                        seg_angle = ring_angle + seg * 0.524
                        vortex_x = 60 + math.cos(seg_angle) * ring_radius
                        vortex_y = 70 + math.sin(seg_angle) * ring_radius * 0.7
                        particle_size = 3 - vortex_layer
                        vortex_color = (80 + vortex_layer * 20, 110 + vortex_layer * 20, 150 + vortex_layer * 20)
                        pygame.draw.circle(s, vortex_color, (int(vortex_x), int(vortex_y)), particle_size)
            # 墙云漏斗下降
            funnel_points = []
            for funnel_seg in range(10):
                funnel_y = 40 + funnel_seg * 5
                funnel_width = 8 + funnel_seg * 2
                funnel_x_offset = math.sin(t * 2 + funnel_seg * 0.5) * 3
                funnel_points.append((60 - funnel_width + funnel_x_offset, funnel_y))
            funnel_points_right = [(60 + (60 - x), y) for x, y in funnel_points]
            all_funnel = funnel_points + funnel_points_right[::-1]
            if len(all_funnel) > 2:
                pygame.draw.polygon(s, (70, 100, 140, 150), all_funnel)
            # 雷暴电弧连锁
            if int(t * 5) % 3 < 2:
                for lightning_i in range(4):
                    lightning_start_angle = lightning_i * 90
                    lightning_points = [(60, 30)]
                    for seg in range(5):
                        seg_angle = (lightning_start_angle + random.randint(-20, 20)) * 0.01745
                        seg_r = 15 + seg * 10
                        lx = 60 + math.cos(seg_angle) * seg_r + random.randint(-4, 4)
                        ly = 30 + seg * 8 + random.randint(-3, 3)
                        lightning_points.append((int(lx), int(ly)))
                    if len(lightning_points) > 1:
                        pygame.draw.lines(s, (255, 255, 255), False, lightning_points, 3)
                        pygame.draw.lines(s, (100, 200, 255), False, lightning_points, 1)
            # 风柱中心涡旋眼
            pygame.draw.circle(s, (40, 70, 110), (60, 70), 10)
            pygame.draw.circle(s, (80, 120, 160), (60, 70), 6)
        
        elif model_style == "wormhole_paperlamp":
            # 和风灯影·纸艺祭典 - 纸灯阵列，樱花飘落，柔光灯海
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 纸灯笼阵列（3x3网格）
            for row in range(3):
                for col in range(3):
                    lamp_x = 20 + col * 30
                    lamp_y = 20 + row * 30
                    # 灯笼框架（细致线条）
                    lamp_rect = (lamp_x, lamp_y, 24, 28)
                    pygame.draw.rect(s, (255, 230, 190), lamp_rect, 2)
                    # 竖向分割线
                    pygame.draw.line(s, (240, 220, 180), (lamp_x + 12, lamp_y), (lamp_x + 12, lamp_y + 28), 1)
                    # 横向纸质纹理
                    for texture_i in range(4):
                        tex_y = lamp_y + 4 + texture_i * 7
                        pygame.draw.line(s, (245, 225, 185), (lamp_x + 2, tex_y), (lamp_x + 22, tex_y), 1)
                    # 柔和光晕（脉动效果）
                    glow_intensity = int(abs(math.sin(t * 1.5 + row + col)) * 50) + 60
                    glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (255, 200, 150, glow_intensity), 
                                     (lamp_x + 12, lamp_y + 14), 16)
                    s.blit(glow_surf, (0, 0))
            # 樱花花瓣飘落
            for petal_i in range(15):
                petal_x = 20 + (petal_i * 37 + int(t * 10)) % 100
                petal_y = int((t * 30 + petal_i * 20) % 120)
                petal_rotation = (t + petal_i) * 2
                # 简化樱花（椭圆）
                petal_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.ellipse(petal_surf, (255, 200, 220), (petal_x - 3, petal_y - 2, 6, 4))
                pygame.draw.ellipse(petal_surf, (255, 180, 200), (petal_x - 3, petal_y - 2, 6, 4), 1)
                s.blit(petal_surf, (0, 0))
            # 整体柔光氛围（灯海效果）
            ambient_glow = pygame.Surface((120, 120), pygame.SRCALPHA)
            for glow_ring in range(3):
                glow_r = 40 + glow_ring * 20
                glow_alpha = 40 - glow_ring * 10
                pygame.draw.circle(ambient_glow, (255, 230, 190, glow_alpha), (60, 60), glow_r)
            s.blit(ambient_glow, (0, 0))
        
        else:
            # 默认虫洞：生物机械混合体，虫洞传送效果
            main_color = (180, 0, 255)
            portal_color = (0, 255, 180)
            
            # 主体：有机生物外壳
            # 外层触手状结构
            for i in range(6):
                angle = t * 2 + i * 1.047  # 60度间隔
                tentacle_length = 35 + math.sin(t * 3 + i) * 8
                # 触手起点和终点
                start_x = 60 + math.cos(angle) * 15
                start_y = 60 + math.sin(angle) * 15
                end_x = 60 + math.cos(angle) * tentacle_length
                end_y = 60 + math.sin(angle) * tentacle_length
                
                # 触手分段绘制，带波动效果
                segments = 5
                for seg in range(segments):
                    seg_progress = seg / segments
                    wave_offset = math.sin(t * 4 + i + seg * 0.5) * 3
                    
                    seg_x1 = start_x + (end_x - start_x) * seg_progress
                    seg_y1 = start_y + (end_y - start_y) * seg_progress
                    seg_x2 = start_x + (end_x - start_x) * (seg_progress + 0.2)
                    seg_y2 = start_y + (end_y - start_y) * (seg_progress + 0.2)
                    
                    # 添加波动
                    perp_angle = angle + 1.571  # 垂直方向
                    seg_x1 += math.cos(perp_angle) * wave_offset
                    seg_y1 += math.sin(perp_angle) * wave_offset
                    seg_x2 += math.cos(perp_angle) * wave_offset
                    seg_y2 += math.sin(perp_angle) * wave_offset
                    
                    # 触手颜色渐变
                    seg_color_r = int(180 - seg_progress * 100)
                    seg_color_g = int(seg_progress * 255)
                    seg_color_b = 255
                    pygame.draw.line(s, (seg_color_r, seg_color_g, seg_color_b), 
                                   (seg_x1, seg_y1), (seg_x2, seg_y2), 3)
            
            # 中心虫洞入口（旋转的虫洞）
            wormhole_layers = 5
            for layer in range(wormhole_layers, 0, -1):
                layer_radius = layer * 6 + int(pulse * 3)
                layer_rotation = t * (3 - layer * 0.3) * (-1 if layer % 2 else 1)
                
                # 虫洞环
                points = []
                spiral_points = 12
                for i in range(spiral_points):
                    point_angle = layer_rotation + (i / spiral_points) * 2 * math.pi
                    distortion = math.sin(t * 5 + i + layer) * 2
                    px = 60 + math.cos(point_angle) * (layer_radius + distortion)
                    py = 60 + math.sin(point_angle) * (layer_radius + distortion)
                    points.append((px, py))
                
                if len(points) >= 3:
                    # 颜色从外到内：紫色到青色
                    layer_r = int(180 * (layer / wormhole_layers))
                    layer_g = int(255 * (1 - layer / wormhole_layers))
                    layer_b = 255
                    pygame.draw.polygon(s, (layer_r, layer_g, layer_b), points, 2)
            
            # 虫洞核心（黑洞效果）
            core_size = int(8 + 3 * pulse)
            for core_ring in range(3, 0, -1):
                core_alpha = int(255 * (core_ring / 3))
                core_color = (50 * core_ring, 0, 100 * core_ring)
                pygame.draw.circle(s, core_color, (60, 60), core_size - core_ring * 2)
            
            # 维度裂缝粒子（从虫洞飞出）
            for particle_idx in range(8):
                particle_angle = t * 4 + particle_idx * 0.785
                particle_progress = (t * 3 + particle_idx * 0.3) % 1.0
                particle_distance = 5 + particle_progress * 30
                
                px = 60 + math.cos(particle_angle) * particle_distance
                py = 60 + math.sin(particle_angle) * particle_distance
                
                particle_size = int(4 * (1 - particle_progress))
                if particle_size > 0:
                    particle_color = (int(180 * (1 - particle_progress)), 
                                    int(255 * particle_progress), 255)
                    pygame.draw.circle(s, particle_color, (int(px), int(py)), particle_size)
            
            # 能量脉冲环
            pulse_ring_radius = int(40 + 10 * abs(math.sin(t * 2)))
            pygame.draw.circle(s, portal_color, (60, 60), pulse_ring_radius, 1)
    
    elif pid == "chronos":
        # ========== Chronos - 时之回响·克洛诺斯 ==========
        # 时间旅行者，时钟机械美学，时间轨迹记录
        main_color = (100, 220, 255)
        accent_color = (255, 200, 100)
        
        # 时钟外壳（双环结构）
        pygame.draw.circle(s, (80, 180, 230), (60, 60), 42, 3)
        pygame.draw.circle(s, main_color, (60, 60), 38, 2)
        pygame.draw.circle(s, (50, 150, 200), (60, 60), 34)
        
        # 12个时刻刻度
        for hour in range(12):
            angle = (hour * 30 - 90) * 0.01745  # 从12点开始
            tick_len = 6 if hour % 3 == 0 else 3
            outer_x = 60 + math.cos(angle) * 34
            outer_y = 60 + math.sin(angle) * 34
            inner_x = 60 + math.cos(angle) * (34 - tick_len)
            inner_y = 60 + math.sin(angle) * (34 - tick_len)
            pygame.draw.line(s, accent_color, (outer_x, outer_y), (inner_x, inner_y), 2)
        
        # 旋转的时针和分针
        hour_angle = (t * 0.5 - 90) * 0.01745  # 慢速旋转
        minute_angle = (t * 6 - 90) * 0.01745  # 快速旋转
        
        # 时针（短粗）
        hour_x = 60 + math.cos(hour_angle) * 18
        hour_y = 60 + math.sin(hour_angle) * 18
        pygame.draw.line(s, accent_color, (60, 60), (hour_x, hour_y), 4)
        pygame.draw.circle(s, (255, 220, 150), (int(hour_x), int(hour_y)), 3)
        
        # 分针（长细）
        minute_x = 60 + math.cos(minute_angle) * 28
        minute_y = 60 + math.sin(minute_angle) * 28
        pygame.draw.line(s, WHITE, (60, 60), (minute_x, minute_y), 3)
        pygame.draw.circle(s, (255, 255, 255), (int(minute_x), int(minute_y)), 2)
        
        # 秒针（超快速，细线）
        second_angle = (t * 30 - 90) * 0.01745
        second_x = 60 + math.cos(second_angle) * 32
        second_y = 60 + math.sin(second_angle) * 32
        pygame.draw.line(s, (0, 255, 255), (60, 60), (second_x, second_y), 1)
        
        # 中心齿轮（时间核心）
        pygame.draw.circle(s, (255, 200, 100), (60, 60), 8)
        pygame.draw.circle(s, (255, 220, 150), (60, 60), 5)
        # 齿轮齿
        for i in range(8):
            gear_angle = (t * 10 + i * 45) * 0.01745
            gear_x1 = 60 + math.cos(gear_angle) * 8
            gear_y1 = 60 + math.sin(gear_angle) * 8
            gear_x2 = 60 + math.cos(gear_angle) * 12
            gear_y2 = 60 + math.sin(gear_angle) * 12
            pygame.draw.line(s, (200, 160, 80), (gear_x1, gear_y1), (gear_x2, gear_y2), 2)
        
        # 时间回响轨迹（历史残影）
        echo_count = 6
        for echo_i in range(echo_count):
            echo_progress = (t * 2 + echo_i * 0.5) % 1.0
            echo_angle = (echo_progress * 360 - 90) * 0.01745
            echo_r = 25 + echo_progress * 15
            echo_x = 60 + math.cos(echo_angle) * echo_r
            echo_y = 60 + math.sin(echo_angle) * echo_r
            echo_alpha = int(200 * (1 - echo_progress))
            if echo_alpha > 0:
                echo_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(echo_surf, (*main_color, echo_alpha), (int(echo_x), int(echo_y)), 4 - echo_i)
                s.blit(echo_surf, (0, 0))
        
        # 外围时间粒子环（逆时针旋转）
        for particle_i in range(12):
            particle_angle = (-t * 3 + particle_i * 30) * 0.01745
            particle_r = 48 + math.sin(t * 5 + particle_i) * 3
            px = 60 + math.cos(particle_angle) * particle_r
            py = 60 + math.sin(particle_angle) * particle_r
            particle_size = 3 + int(abs(math.sin(t * 4 + particle_i)) * 2)
            pygame.draw.circle(s, (100, 220, 255), (int(px), int(py)), particle_size)
            pygame.draw.circle(s, (200, 240, 255), (int(px), int(py)), particle_size - 1)
        
        # 时空扭曲波纹（脉冲效果）
        for ripple_i in range(3):
            ripple_phase = (t * 2 + ripple_i * 0.33) % 1.0
            ripple_r = int(20 + ripple_phase * 35)
            ripple_alpha = int(150 * (1 - ripple_phase))
            if ripple_alpha > 0:
                pygame.draw.circle(s, (*main_color, ripple_alpha), (60, 60), ripple_r, 2)
    
    elif pid == "mirage":
        # ========== Mirage - 幻镜·万华 ==========
        # 镜像分身召唤师，万花筒美学，三角棱镜结构
        main_color = (200, 150, 255)
        accent_color = (255, 200, 255)
        
        # 三角棱镜主体（核心镜面）
        prism_points = [
            (60, 25),      # 顶点
            (30, 85),      # 左下
            (90, 85)       # 右下
        ]
        # 渐变填充效果
        prism_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.polygon(prism_surf, (*main_color, 180), prism_points)
        s.blit(prism_surf, (0, 0))
        pygame.draw.polygon(s, accent_color, prism_points, 2)
        
        # 内部折射分割线
        pygame.draw.line(s, (255, 220, 255, 150), (60, 25), (60, 75), 1)
        pygame.draw.line(s, (255, 220, 255, 150), (60, 55), (40, 75), 1)
        pygame.draw.line(s, (255, 220, 255, 150), (60, 55), (80, 75), 1)
        
        # 旋转的分身影像（3个镜像）
        mirror_count = 3
        for mirror_i in range(mirror_count):
            mirror_angle = (t * 2 + mirror_i * 120) * 0.01745
            mirror_r = 38 + math.sin(t * 3 + mirror_i) * 5
            mx = 60 + math.cos(mirror_angle) * mirror_r
            my = 60 + math.sin(mirror_angle) * mirror_r
            
            # 分身光点（小三角形）
            mini_size = 8
            mini_angle_rad = (t * 5 + mirror_i * 120) * 0.01745
            mini_points = []
            for vertex_i in range(3):
                vertex_angle = mini_angle_rad + vertex_i * (2 * math.pi / 3)
                px = mx + math.cos(vertex_angle) * mini_size
                py = my + math.sin(vertex_angle) * mini_size
                mini_points.append((px, py))
            
            # 半透明分身
            mirror_alpha = 180 - mirror_i * 30
            mirror_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.polygon(mirror_surf, (*accent_color, mirror_alpha), mini_points)
            s.blit(mirror_surf, (0, 0))
            pygame.draw.polygon(s, (255, 255, 255), mini_points, 1)
        
        # 万花筒光线（6条对称光束）
        for ray_i in range(6):
            ray_angle = (ray_i * 60 + t * 8) * 0.01745
            ray_len = 50 + math.sin(t * 4 + ray_i) * 8
            ray_end_x = 60 + math.cos(ray_angle) * ray_len
            ray_end_y = 60 + math.sin(ray_angle) * ray_len
            # 渐变光线
            for seg in range(5):
                seg_start_r = 15 + seg * 7
                seg_end_r = seg_start_r + 8
                seg_alpha = 200 - seg * 35
                seg_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                sx1 = 60 + math.cos(ray_angle) * seg_start_r
                sy1 = 60 + math.sin(ray_angle) * seg_start_r
                sx2 = 60 + math.cos(ray_angle) * seg_end_r
                sy2 = 60 + math.sin(ray_angle) * seg_end_r
                pygame.draw.line(seg_surf, (*main_color, seg_alpha), (sx1, sy1), (sx2, sy2), 2)
                s.blit(seg_surf, (0, 0))
        
        # 核心水晶（中心发光点）
        pygame.draw.circle(s, (255, 255, 255), (60, 55), 8)
        pygame.draw.circle(s, accent_color, (60, 55), 6)
        pygame.draw.circle(s, (255, 200, 255), (60, 55), 4)
        
        # 镜像粒子环
        for particle_i in range(16):
            particle_angle = (particle_i * 22.5 + t * 5) * 0.01745
            particle_r = 48 + math.sin(t * 6 + particle_i) * 4
            px = 60 + math.cos(particle_angle) * particle_r
            py = 60 + math.sin(particle_angle) * particle_r
            particle_size = 2 + int(abs(math.sin(t * 3 + particle_i)))
            pygame.draw.circle(s, (220, 180, 255), (int(px), int(py)), particle_size)
        
        # 反射波纹
        for ripple_i in range(2):
            ripple_phase = (t * 2.5 + ripple_i * 0.5) % 1.0
            ripple_r = int(20 + ripple_phase * 30)
            ripple_alpha = int(120 * (1 - ripple_phase))
            if ripple_alpha > 0:
                pygame.draw.circle(s, (*accent_color, ripple_alpha), (60, 55), ripple_r, 2)
    
    elif pid == "gambit":
        # ========== Gambit - 命运赌徒·艾斯 ==========
        # 赌场美学，扑克牌+骰子+轮盘，金色与红黑配色
        gold_color = (255, 215, 0)
        red_color = (255, 50, 50)
        black_color = (30, 30, 30)
        
        # 主体轮盘（圆形底盘）
        pygame.draw.circle(s, black_color, (60, 60), 42)
        pygame.draw.circle(s, gold_color, (60, 60), 42, 3)
        pygame.draw.circle(s, (40, 40, 40), (60, 60), 38)
        
        # 轮盘分区（红黑交替，12格）
        for sector_i in range(12):
            sector_angle_start = (sector_i * 30 + t * 3) * 0.01745
            sector_angle_end = ((sector_i + 1) * 30 + t * 3) * 0.01745
            sector_color = red_color if sector_i % 2 == 0 else black_color
            # 扇形
            sector_points = [(60, 60)]
            for ang in range(int(sector_angle_start * 57.3), int(sector_angle_end * 57.3) + 1, 3):
                ang_rad = ang * 0.01745
                sector_points.append((60 + math.cos(ang_rad) * 35, 60 + math.sin(ang_rad) * 35))
            if len(sector_points) > 2:
                pygame.draw.polygon(s, sector_color, sector_points)
        
        # 轮盘边框金边
        pygame.draw.circle(s, gold_color, (60, 60), 36, 2)
        
        # 中心旋转的骰子
        dice_size = 14
        dice_angle = t * 8
        dice_points = []
        for corner_i in range(4):
            corner_angle = (dice_angle + corner_i * 90) * 0.01745
            dx = 60 + math.cos(corner_angle) * dice_size
            dy = 60 + math.sin(corner_angle) * dice_size
            dice_points.append((dx, dy))
        pygame.draw.polygon(s, (255, 255, 255), dice_points)
        pygame.draw.polygon(s, gold_color, dice_points, 2)
        
        # 骰子点数（随机显示1-6）
        dice_dots = int(t * 2) % 6 + 1
        if dice_dots == 1:
            pygame.draw.circle(s, black_color, (60, 60), 3)
        elif dice_dots == 2:
            pygame.draw.circle(s, black_color, (56, 56), 2)
            pygame.draw.circle(s, black_color, (64, 64), 2)
        elif dice_dots == 3:
            pygame.draw.circle(s, black_color, (56, 56), 2)
            pygame.draw.circle(s, black_color, (60, 60), 2)
            pygame.draw.circle(s, black_color, (64, 64), 2)
        elif dice_dots == 4:
            pygame.draw.circle(s, black_color, (56, 56), 2)
            pygame.draw.circle(s, black_color, (64, 56), 2)
            pygame.draw.circle(s, black_color, (56, 64), 2)
            pygame.draw.circle(s, black_color, (64, 64), 2)
        elif dice_dots == 5:
            pygame.draw.circle(s, black_color, (56, 56), 2)
            pygame.draw.circle(s, black_color, (64, 56), 2)
            pygame.draw.circle(s, black_color, (60, 60), 2)
            pygame.draw.circle(s, black_color, (56, 64), 2)
            pygame.draw.circle(s, black_color, (64, 64), 2)
        else:  # 6
            pygame.draw.circle(s, black_color, (56, 56), 2)
            pygame.draw.circle(s, black_color, (64, 56), 2)
            pygame.draw.circle(s, black_color, (56, 60), 2)
            pygame.draw.circle(s, black_color, (64, 60), 2)
            pygame.draw.circle(s, black_color, (56, 64), 2)
            pygame.draw.circle(s, black_color, (64, 64), 2)
        
        # 四张旋转的扑克牌（A、K、Q、J）
        card_symbols = ['♠', '♥', '♦', '♣']
        for card_i in range(4):
            card_angle = (card_i * 90 + t * 4) * 0.01745
            card_r = 46
            cx = 60 + math.cos(card_angle) * card_r
            cy = 60 + math.sin(card_angle) * card_r
            # 卡片形状（小矩形）
            card_w, card_h = 10, 14
            card_rot = card_angle + math.pi / 2
            card_pts = []
            corners = [(-card_w/2, -card_h/2), (card_w/2, -card_h/2), 
                       (card_w/2, card_h/2), (-card_w/2, card_h/2)]
            for corner in corners:
                rx = corner[0] * math.cos(card_rot) - corner[1] * math.sin(card_rot)
                ry = corner[0] * math.sin(card_rot) + corner[1] * math.cos(card_rot)
                card_pts.append((cx + rx, cy + ry))
            # 红黑交替
            card_color = red_color if card_i % 2 == 0 else black_color
            pygame.draw.polygon(s, (255, 255, 255), card_pts)
            pygame.draw.polygon(s, card_color, card_pts, 1)
        
        # 金色运气粒子
        for luck_i in range(10):
            luck_phase = (t * 3 + luck_i * 0.3) % 1.0
            luck_angle = (luck_i * 36 + t * 6) * 0.01745
            luck_r = 30 + luck_phase * 25
            lx = 60 + math.cos(luck_angle) * luck_r
            ly = 60 + math.sin(luck_angle) * luck_r
            luck_alpha = int(255 * (1 - luck_phase))
            luck_size = int(4 * (1 - luck_phase)) + 1
            luck_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(luck_surf, (*gold_color, luck_alpha), (int(lx), int(ly)), luck_size)
            s.blit(luck_surf, (0, 0))
        
        # 幸运星闪烁
        for star_i in range(5):
            star_angle = (star_i * 72 + t * 2) * 0.01745
            star_r = 52
            star_x = 60 + math.cos(star_angle) * star_r
            star_y = 60 + math.sin(star_angle) * star_r
            star_brightness = abs(math.sin(t * 8 + star_i * 1.5))
            if star_brightness > 0.7:
                # 四角星
                star_size = 4
                pygame.draw.line(s, gold_color, (star_x - star_size, star_y), (star_x + star_size, star_y), 2)
                pygame.draw.line(s, gold_color, (star_x, star_y - star_size), (star_x, star_y + star_size), 2)
        
        # ========== Chronos专属涂装渲染 ==========
        if model_style == "chronos_memoir":
            # 时光相册·记忆胶片 - 老式胶片相机时钟，照片碎片，怀旧棕褐滤镜
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 怀旧棕褐色背景（胶片纹理）
            for grain_i in range(100):
                gx = random.randint(0, 120)
                gy = random.randint(0, 120)
                grain_alpha = random.randint(20, 60)
                pygame.draw.circle(s, (180, 150, 110, grain_alpha), (gx, gy), 1)
            # 相机快门时钟框
            pygame.draw.circle(s, (200, 160, 120), (60, 60), 40, 3)
            pygame.draw.circle(s, (220, 180, 140), (60, 60), 37, 1)
            # 24张照片碎片（环绕旋转）
            for photo_i in range(24):
                photo_angle = (photo_i * 15 + t * 8) * 0.01745
                photo_r = 32 + int(3 * math.sin(t * 2 + photo_i))
                photo_x = 60 + math.cos(photo_angle) * photo_r
                photo_y = 60 + math.sin(photo_angle) * photo_r
                # 照片矩形（不同泛黄程度）
                sepia = (200 - photo_i * 3, 160 - photo_i * 2, 120 - photo_i)
                photo_rect = pygame.Rect(int(photo_x) - 4, int(photo_y) - 3, 8, 6)
                pygame.draw.rect(s, sepia, photo_rect)
                pygame.draw.rect(s, (180, 150, 110), photo_rect, 1)
            # 时钟指针（胶卷条纹）
            for hand_i in range(2):
                hand_angle = (t * (20 if hand_i == 0 else 3) - 90) * 0.01745
                hand_len = 28 if hand_i == 0 else 35
                hx = 60 + math.cos(hand_angle) * hand_len
                hy = 60 + math.sin(hand_angle) * hand_len
                hand_color = (200, 160, 120) if hand_i == 0 else (220, 180, 140)
                pygame.draw.line(s, hand_color, (60, 60), (hx, hy), 3)
            # 中心快门按钮
            pygame.draw.circle(s, (220, 180, 140), (60, 60), 8)
            pygame.draw.circle(s, (200, 160, 120), (60, 60), 5)
        
        elif model_style == "chronos_biological":
            # 生物钟律·心跳脉搏 - 活体时钟，心脏跳动韵律，血管脉冲，DNA螺旋
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 心脏跳动核心（周期性脉动）
            heartbeat_cycle = int(t * 72 / 60) % 2  # 72 BPM
            beat_phase = (t * 72 / 60) % 1.0
            beat_size = 25 + int(8 * math.sin(beat_phase * math.pi * 2))
            pygame.draw.circle(s, (255, 120, 140), (60, 60), beat_size)
            pygame.draw.circle(s, (255, 100, 120), (60, 60), beat_size - 5)
            # 血管脉冲波纹（8个方向扩散）
            for pulse_i in range(8):
                pulse_angle = (pulse_i * 45) * 0.01745
                pulse_r = 30 + int(15 * beat_phase)
                pulse_alpha = int(200 * (1 - beat_phase))
                if pulse_alpha > 0:
                    pulse_x = 60 + math.cos(pulse_angle) * pulse_r
                    pulse_y = 60 + math.sin(pulse_angle) * pulse_r
                    pygame.draw.circle(s, (255, 150, 170, pulse_alpha), (int(pulse_x), int(pulse_y)), 6)
            # DNA双螺旋缠绕（环绕时钟）
            for helix_i in range(36):
                helix_progress = helix_i / 36
                helix_angle = (helix_progress * 360 + t * 30) * 0.01745
                helix_r = 38
                helix_offset = 5 * math.sin(helix_progress * math.pi * 6)
                # 第一条链
                hx1 = 60 + math.cos(helix_angle) * (helix_r + helix_offset)
                hy1 = 60 + math.sin(helix_angle) * (helix_r + helix_offset)
                pygame.draw.circle(s, (255, 150, 170), (int(hx1), int(hy1)), 2)
                # 第二条链（相位差180度）
                hx2 = 60 + math.cos(helix_angle) * (helix_r - helix_offset)
                hy2 = 60 + math.sin(helix_angle) * (helix_r - helix_offset)
                pygame.draw.circle(s, (230, 80, 100), (int(hx2), int(hy2)), 2)
                # 碱基对连接（每隔3个）
                if helix_i % 3 == 0:
                    pygame.draw.line(s, (255, 200, 210), (hx1, hy1), (hx2, hy2), 1)
            # 细胞分裂动画（时钟指针）
            cell_hand_angle = (t * 15 - 90) * 0.01745
            cell_hx = 60 + math.cos(cell_hand_angle) * 30
            cell_hy = 60 + math.sin(cell_hand_angle) * 30
            pygame.draw.line(s, (255, 100, 120), (60, 60), (cell_hx, cell_hy), 3)
            # 生命能量粒子
            for life_i in range(12):
                life_angle = (life_i * 30 + t * 50) * 0.01745
                life_x = 60 + math.cos(life_angle) * 48
                life_y = 60 + math.sin(life_angle) * 48
                pygame.draw.circle(s, (255, 150, 170), (int(life_x), int(life_y)), 3)
        
        elif model_style == "chronos_tidal":
            # 潮汐涨落·月相周期 - 海洋潮汐时钟，月相盈亏，潮水波纹，贝壳装饰
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 月相周期（8相）
            moon_phase = int((t * 0.5) % 8)
            moon_x, moon_y = 60, 25
            # 绘制月相
            pygame.draw.circle(s, (240, 240, 240), (moon_x, moon_y), 12)
            if moon_phase < 4:  # 上弦
                shadow_offset = int(12 * (moon_phase / 4))
                pygame.draw.circle(s, (100, 120, 140), (moon_x - shadow_offset, moon_y), 12)
            else:  # 下弦
                shadow_offset = int(12 * ((8 - moon_phase) / 4))
                pygame.draw.circle(s, (100, 120, 140), (moon_x + shadow_offset, moon_y), 12)
            # 12层潮汐波纹（从中心扩散）
            for tide_i in range(12):
                tide_phase = ((t * 2 + tide_i * 0.2) % 1.0)
                tide_r = int(20 + tide_phase * 35)
                tide_alpha = int(150 * (1 - tide_phase))
                if tide_alpha > 0:
                    # 波浪形状（不规则）
                    wave_points = []
                    for seg in range(24):
                        wave_angle = (seg * 15) * 0.01745
                        wave_r_offset = tide_r + int(3 * math.sin(seg * 0.8 + t * 4))
                        wx = 60 + math.cos(wave_angle) * wave_r_offset
                        wy = 60 + math.sin(wave_angle) * wave_r_offset
                        wave_points.append((int(wx), int(wy)))
                    if len(wave_points) > 2:
                        pygame.draw.polygon(s, (100, 180, 220, tide_alpha), wave_points, 2)
            # 贝壳珍珠点缀（8个）
            for shell_i in range(8):
                shell_angle = (shell_i * 45 + t * 5) * 0.01745
                shell_r = 42
                shell_x = 60 + math.cos(shell_angle) * shell_r
                shell_y = 60 + math.sin(shell_angle) * shell_r
                # 贝壳形状（螺旋渐大）
                for spiral in range(3):
                    spiral_r = 4 + spiral * 2
                    spiral_offset = spiral * 0.3
                    sx = shell_x + math.cos(shell_angle + spiral_offset) * spiral_r
                    sy = shell_y + math.sin(shell_angle + spiral_offset) * spiral_r
                    pygame.draw.circle(s, (220, 240, 255), (int(sx), int(sy)), 4 - spiral)
            # 中心漩涡（潮汐力）
            pygame.draw.circle(s, (120, 200, 240), (60, 60), 18, 2)
            pygame.draw.circle(s, (100, 180, 220), (60, 60), 12)
            # 时钟指针（海浪形）
            hand_angle = (t * 12 - 90) * 0.01745
            hx = 60 + math.cos(hand_angle) * 32
            hy = 60 + math.sin(hand_angle) * 32
            pygame.draw.line(s, (80, 160, 200), (60, 60), (hx, hy), 3)
        
        elif model_style == "chronos_musical":
            # 音律节拍·八音盒舞 - 旋转八音盒时钟，音符飘舞，五线谱螺旋，舞者旋转
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 八音盒底座（旋转）
            box_angle = t * 10
            for box_seg in range(8):
                seg_angle = (box_seg * 45 + box_angle) * 0.01745
                box_x = 60 + math.cos(seg_angle) * 45
                box_y = 60 + math.sin(seg_angle) * 45
                pygame.draw.circle(s, (230, 180, 230), (int(box_x), int(box_y)), 4)
            # 五线谱螺旋（3圈）
            for staff_i in range(3):
                staff_r = 25 + staff_i * 8
                for seg in range(24):
                    staff_angle = (seg * 15 + t * 20) * 0.01745
                    staff_x = 60 + math.cos(staff_angle) * staff_r
                    staff_y = 60 + math.sin(staff_angle) * staff_r
                    pygame.draw.line(s, (200, 150, 200), (staff_x, staff_y), 
                                   (staff_x + 3, staff_y), 1)
            # 32个音符粒子飘舞
            note_shapes = [(2, 4), (3, 3), (2, 5)]  # 不同音符大小
            for note_i in range(32):
                note_angle = (note_i * 11.25 + t * 40) * 0.01745
                note_r = 20 + int(15 * math.sin(t * 3 + note_i * 0.2))
                note_x = 60 + math.cos(note_angle) * note_r
                note_y = 60 + math.sin(note_angle) * note_r
                note_shape = note_shapes[note_i % 3]
                # 音符椭圆
                pygame.draw.ellipse(s, (255, 200, 255), 
                                  (int(note_x) - note_shape[0], int(note_y) - note_shape[1],
                                   note_shape[0] * 2, note_shape[1] * 2))
                # 音符符杆
                pygame.draw.line(s, (230, 180, 230), (note_x, note_y), 
                               (note_x, note_y - 8), 1)
            # 中心旋转舞者（简化轮廓）
            dancer_angle = t * 60
            dancer_arms = [(15, 0), (15, 90), (15, 180), (15, 270)]
            for arm_r, arm_offset in dancer_arms:
                arm_angle = (dancer_angle + arm_offset) * 0.01745
                arm_x = 60 + math.cos(arm_angle) * arm_r
                arm_y = 60 + math.sin(arm_angle) * arm_r
                pygame.draw.line(s, (255, 200, 255), (60, 60), (arm_x, arm_y), 2)
            pygame.draw.circle(s, (255, 200, 255), (60, 60), 6)
        
        elif model_style == "chronos_geological":
            # 地质纪元·岩层年轮 - 地层沉积时钟，亿万年岩石叠加，化石镶嵌
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 15层地质沉积圈（从内到外，颜色渐变）
            strata_colors = [
                (160, 140, 120), (155, 135, 115), (150, 130, 110),
                (145, 125, 105), (140, 120, 100), (135, 115, 95),
                (130, 110, 90), (125, 105, 85), (120, 100, 80),
                (115, 95, 75), (110, 90, 70), (105, 85, 65),
                (100, 80, 60), (95, 75, 55), (90, 70, 50)
            ]
            for layer_i in range(15):
                layer_r = 8 + layer_i * 3
                layer_color = strata_colors[layer_i]
                pygame.draw.circle(s, layer_color, (60, 60), layer_r, 2)
                # 地层不规则边缘（裂缝）
                if layer_i % 3 == 0:
                    for crack in range(8):
                        crack_angle = (crack * 45 + layer_i * 5) * 0.01745
                        crack_x = 60 + math.cos(crack_angle) * layer_r
                        crack_y = 60 + math.sin(crack_angle) * layer_r
                        crack_len = 3
                        crack_end_x = crack_x + math.cos(crack_angle) * crack_len
                        crack_end_y = crack_y + math.sin(crack_angle) * crack_len
                        pygame.draw.line(s, (80, 60, 40), (crack_x, crack_y), 
                                       (crack_end_x, crack_end_y), 1)
            # 8个化石标记（三叶虫、菊石等）
            for fossil_i in range(8):
                fossil_angle = (fossil_i * 45 + t * 3) * 0.01745
                fossil_r = 38
                fossil_x = 60 + math.cos(fossil_angle) * fossil_r
                fossil_y = 60 + math.sin(fossil_angle) * fossil_r
                # 螺旋化石形状
                for spiral in range(4):
                    spiral_offset = spiral * 0.4
                    spiral_r = 3 + spiral
                    sx = fossil_x + math.cos(fossil_angle + spiral_offset) * spiral_r * 0.5
                    sy = fossil_y + math.sin(fossil_angle + spiral_offset) * spiral_r * 0.5
                    pygame.draw.circle(s, (100, 80, 60), (int(sx), int(sy)), 2)
            # 地质时钟指针（岩石纹理）
            hand_angle = (t * 5 - 90) * 0.01745
            hx = 60 + math.cos(hand_angle) * 35
            hy = 60 + math.sin(hand_angle) * 35
            pygame.draw.line(s, (140, 120, 100), (60, 60), (hx, hy), 4)
            pygame.draw.circle(s, (160, 140, 120), (60, 60), 6)
        
        elif model_style == "chronos_culinary":
            # 烹饪计时·美食盛宴 - 厨房定时器时钟，食材翻炒，沸腾泡泡，香料飘散
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 厨房定时器外框（橙色温暖）
            pygame.draw.circle(s, (255, 150, 80), (60, 60), 42, 3)
            pygame.draw.circle(s, (255, 180, 100), (60, 60), 38, 1)
            # 60个刻度（分钟）
            for minute in range(60):
                mark_angle = (minute * 6 - 90) * 0.01745
                mark_r = 35 if minute % 5 == 0 else 37
                mark_len = 5 if minute % 5 == 0 else 3
                mx1 = 60 + math.cos(mark_angle) * mark_r
                my1 = 60 + math.sin(mark_angle) * mark_r
                mx2 = 60 + math.cos(mark_angle) * (mark_r - mark_len)
                my2 = 60 + math.sin(mark_angle) * (mark_r - mark_len)
                pygame.draw.line(s, (230, 130, 60), (mx1, my1), (mx2, my2), 2)
            # 40个食材粒子（环绕旋转）
            ingredients = [
                (255, 100, 100),  # 番茄红
                (100, 255, 100),  # 蔬菜绿
                (255, 200, 100),  # 面包黄
                (200, 150, 100)   # 肉类棕
            ]
            for ing_i in range(40):
                ing_angle = (ing_i * 9 + t * 30) * 0.01745
                ing_r = 28 + int(5 * math.sin(t * 4 + ing_i))
                ing_x = 60 + math.cos(ing_angle) * ing_r
                ing_y = 60 + math.sin(ing_angle) * ing_r
                ing_color = ingredients[ing_i % 4]
                pygame.draw.circle(s, ing_color, (int(ing_x), int(ing_y)), 3)
            # 沸腾泡泡效果（从中心向上）
            for bubble_i in range(20):
                bubble_progress = ((t * 3 + bubble_i * 0.1) % 1.0)
                bubble_x = 60 + int(10 * math.sin(bubble_i + t * 5))
                bubble_y = 60 - int(bubble_progress * 40)
                bubble_size = int(4 * (1 - bubble_progress))
                if bubble_size > 0:
                    bubble_alpha = int(180 * (1 - bubble_progress))
                    pygame.draw.circle(s, (255, 255, 255, bubble_alpha), 
                                     (bubble_x, bubble_y), bubble_size)
            # 定时器指针（旋转倒数）
            timer_hand_angle = (t * 20 - 90) * 0.01745
            thx = 60 + math.cos(timer_hand_angle) * 30
            thy = 60 + math.sin(timer_hand_angle) * 30
            pygame.draw.line(s, (255, 100, 50), (60, 60), (thx, thy), 4)
            # 中心旋钮
            pygame.draw.circle(s, (255, 150, 80), (60, 60), 8)
            pygame.draw.circle(s, (255, 180, 100), (60, 60), 5)
        
        elif model_style == "chronos_athletic":
            # 竞技秒表·极速冲刺 - 运动秒表时钟，赛道跑道，冲刺残影，汗水飞溅
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 8条赛道跑道（环形）
            for lane_i in range(8):
                lane_r = 15 + lane_i * 5
                lane_color = (255, 80 + lane_i * 5, 80 + lane_i * 5)
                pygame.draw.circle(s, lane_color, (60, 60), lane_r, 1)
            # 起跑线标记（4个方向）
            for start_i in range(4):
                start_angle = (start_i * 90) * 0.01745
                start_x = 60 + math.cos(start_angle) * 48
                start_y = 60 + math.sin(start_angle) * 48
                pygame.draw.rect(s, (255, 255, 255), (int(start_x) - 2, int(start_y) - 5, 4, 10))
            # 5层冲刺残影（运动员）
            for afterimage_i in range(5):
                afterimage_alpha = 200 - afterimage_i * 40
                afterimage_offset = afterimage_i * 5
                runner_angle = (t * 80 - afterimage_offset * 10) * 0.01745
                runner_r = 35
                runner_x = 60 + math.cos(runner_angle) * runner_r
                runner_y = 60 + math.sin(runner_angle) * runner_r
                # 简化运动员形状（椭圆）
                runner_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.ellipse(runner_surf, (255, 120, 120, afterimage_alpha),
                                  (int(runner_x) - 4, int(runner_y) - 6, 8, 12))
                s.blit(runner_surf, (0, 0))
            # 汗水飞溅粒子（20个）
            for sweat_i in range(20):
                sweat_progress = ((t * 5 + sweat_i * 0.1) % 1.0)
                sweat_angle = (t * 80 + sweat_i * 18) * 0.01745
                sweat_r = 35 + int(sweat_progress * 15)
                sweat_x = 60 + math.cos(sweat_angle) * sweat_r
                sweat_y = 60 + math.sin(sweat_angle) * sweat_r
                sweat_alpha = int(200 * (1 - sweat_progress))
                if sweat_alpha > 0:
                    pygame.draw.circle(s, (150, 200, 255, sweat_alpha), (int(sweat_x), int(sweat_y)), 2)
            # 秒表指针（极速旋转）
            stopwatch_hand = (t * 100 - 90) * 0.01745
            shx = 60 + math.cos(stopwatch_hand) * 30
            shy = 60 + math.sin(stopwatch_hand) * 30
            pygame.draw.line(s, (255, 80, 80), (60, 60), (shx, shy), 3)
            # 中心秒表按钮
            pygame.draw.circle(s, (255, 120, 120), (60, 60), 10)
            pygame.draw.circle(s, (255, 80, 80), (60, 60), 6)
        
        elif model_style == "chronos_gardening":
            # 园艺四季·花开花落 - 植物生长时钟，种子发芽，藤蔓攀爬，四季轮转
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 四季背景色环（春夏秋冬）
            season_colors = [
                (150, 255, 150),  # 春-嫩绿
                (100, 200, 100),  # 夏-深绿
                (255, 180, 100),  # 秋-橙黄
                (200, 220, 255)   # 冬-冰蓝
            ]
            current_season = int((t * 0.5) % 4)
            season_color = season_colors[current_season]
            pygame.draw.circle(s, season_color, (60, 60), 45, 8)
            # 12条藤蔓螺旋攀爬
            for vine_i in range(12):
                vine_angle_start = (vine_i * 30) * 0.01745
                vine_points = []
                for seg in range(8):
                    vine_progress = seg / 8
                    vine_r = 10 + vine_progress * 35
                    vine_angle = vine_angle_start + vine_progress * (t * 2)
                    vine_offset = 3 * math.sin(t * 3 + vine_i + seg)
                    vx = 60 + math.cos(vine_angle) * (vine_r + vine_offset)
                    vy = 60 + math.sin(vine_angle) * (vine_r + vine_offset)
                    vine_points.append((int(vx), int(vy)))
                if len(vine_points) > 1:
                    pygame.draw.lines(s, (100, 180, 80), False, vine_points, 2)
            # 16朵季节性花朵绽放
            bloom_phase = (t * 2) % 1.0
            for bloom_i in range(16):
                bloom_angle = (bloom_i * 22.5 + t * 10) * 0.01745
                bloom_r = 38
                bloom_x = 60 + math.cos(bloom_angle) * bloom_r
                bloom_y = 60 + math.sin(bloom_angle) * bloom_r
                # 花瓣大小随时间变化（绽放-凋零）
                petal_size = int(5 * abs(math.sin(bloom_phase * math.pi + bloom_i * 0.2)))
                if petal_size > 0:
                    # 5片花瓣
                    for petal in range(5):
                        petal_angle = (petal * 72 + t * 5) * 0.01745
                        petal_x = bloom_x + math.cos(petal_angle) * petal_size
                        petal_y = bloom_y + math.sin(petal_angle) * petal_size
                        pygame.draw.circle(s, season_color, (int(petal_x), int(petal_y)), 3)
                    # 花心
                    pygame.draw.circle(s, (255, 200, 100), (int(bloom_x), int(bloom_y)), 2)
            # 中心种子（生长核心）
            pygame.draw.circle(s, (140, 220, 120), (60, 60), 12)
            pygame.draw.circle(s, (120, 200, 100), (60, 60), 8)
            # 生长时针
            growth_hand = (t * 8 - 90) * 0.01745
            ghx = 60 + math.cos(growth_hand) * 28
            ghy = 60 + math.sin(growth_hand) * 28
            pygame.draw.line(s, (100, 180, 80), (60, 60), (ghx, ghy), 3)
            # 蒸汽气泡（40个）
            for steam_i in range(40):
                steam_progress = ((t * 2 + steam_i * 0.05) % 1.0)
                steam_x = 60 + random.randint(-20, 20)
                steam_y = 60 + int(steam_progress * 50)
                steam_size = int(3 * (1 - steam_progress))
                if steam_size > 0:
                    alpha = int(150 * (1 - steam_progress))
                    pygame.draw.circle(s, (220, 220, 220, alpha), (steam_x, steam_y), steam_size)
            # 罗马数字刻度位置（用小圆圈代替）
            for roman in range(12):
                roman_angle = (roman * 30 - 90) * 0.01745
                rx = 60 + math.cos(roman_angle) * 28
                ry = 60 + math.sin(roman_angle) * 28
                pygame.draw.circle(s, (200, 150, 80), (int(rx), int(ry)), 3)
        
        elif model_style == "chronos_theatrical":
            # 戏剧幕布·三幕悲喜 - 舞台大幕时钟，红色天鹅绒帷幕，面具悲喜，聚光灯
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 8条帷幕波浪（红色天鹅绒）
            for curtain_i in range(8):
                curtain_x = 15 + curtain_i * 13
                curtain_points = []
                for wave_seg in range(10):
                    wave_y = 20 + wave_seg * 8 + int(8 * math.sin(t * 3 + curtain_i * 0.5 + wave_seg * 0.3))
                    curtain_points.append((curtain_x, wave_y))
                if len(curtain_points) > 1:
                    pygame.draw.lines(s, (180, 50, 80), False, curtain_points, 3)
            # 三幕分界线（起承转合）
            for act in range(3):
                act_angle = (act * 120 + t * 5) * 0.01745
                act_r = 38
                act_x = 60 + math.cos(act_angle) * act_r
                act_y = 60 + math.sin(act_angle) * act_r
                pygame.draw.line(s, (200, 80, 100), (60, 60), (act_x, act_y), 2)
            # 3个面具转换（悲伤-中立-欢乐）
            mask_phase = int((t * 0.8) % 3)
            mask_expressions = [
                [(50, 55), (50, 65)],  # 悲伤（下弯嘴）
                [(50, 60), (70, 60)],  # 中立（直线）
                [(50, 65), (50, 55)]   # 欢乐（上弯嘴）
            ]
            # 左侧面具
            pygame.draw.circle(s, (220, 220, 220), (35, 60), 12)
            pygame.draw.circle(s, (50, 50, 50), (32, 57), 3)  # 左眼
            pygame.draw.circle(s, (50, 50, 50), (38, 57), 3)  # 右眼
            mouth_expr = mask_expressions[mask_phase]
            pygame.draw.line(s, (50, 50, 50), (30, mouth_expr[0][1]), (40, mouth_expr[1][1]), 2)
            # 右侧面具（相反表情）
            opposite_phase = (mask_phase + 2) % 3
            pygame.draw.circle(s, (220, 220, 220), (85, 60), 12)
            pygame.draw.circle(s, (50, 50, 50), (82, 57), 3)
            pygame.draw.circle(s, (50, 50, 50), (88, 57), 3)
            opp_expr = mask_expressions[opposite_phase]
            pygame.draw.line(s, (50, 50, 50), (80, opp_expr[0][1]), (90, opp_expr[1][1]), 2)
            # 聚光灯扫射（3束）
            for spot_i in range(3):
                spot_angle = (spot_i * 120 + t * 40) * 0.01745
                spot_len = 45
                spot_x = 60 + math.cos(spot_angle) * spot_len
                spot_y = 60 + math.sin(spot_angle) * spot_len
                spot_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(spot_surf, (255, 255, 200, 80), (60, 60), (spot_x, spot_y), 8)
                s.blit(spot_surf, (0, 0))
            # 中心舞台
            pygame.draw.circle(s, (200, 80, 100), (60, 60), 10)
            pygame.draw.circle(s, (180, 50, 80), (60, 60), 6)
        
        elif model_style == "chronos_chemical":
            # 化学反应·试管计时 - 实验室烧杯时钟，试剂变色，分子结构，反应泡泡
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 烧杯容器轮廓
            pygame.draw.ellipse(s, (100, 255, 180), (30, 50, 60, 40), 2)
            pygame.draw.line(s, (100, 255, 180), (35, 50), (35, 30), 2)
            pygame.draw.line(s, (100, 255, 180), (85, 50), (85, 30), 2)
            pygame.draw.line(s, (100, 255, 180), (35, 30), (85, 30), 2)
            # 液体颜色变化（化学反应）
            reaction_phase = (t * 1.5) % 1.0
            liquid_colors = [
                (100, 255, 180),
                (120, 255, 200),
                (80, 230, 160)
            ]
            liquid_color_index = int(reaction_phase * 3) % 3
            liquid_color = liquid_colors[liquid_color_index]
            liquid_level = 65 + int(5 * math.sin(t * 3))
            pygame.draw.ellipse(s, liquid_color, (32, liquid_level, 56, 25))
            # 24个分子键结构（环绕）
            for bond_i in range(24):
                bond_angle = (bond_i * 15 + t * 20) * 0.01745
                bond_r = 35
                bond_x = 60 + math.cos(bond_angle) * bond_r
                bond_y = 60 + math.sin(bond_angle) * bond_r
                # 原子节点
                pygame.draw.circle(s, (120, 255, 200), (int(bond_x), int(bond_y)), 3)
                # 化学键连接（每隔3个）
                if bond_i % 3 == 0:
                    next_bond_angle = ((bond_i + 3) * 15 + t * 20) * 0.01745
                    next_bond_x = 60 + math.cos(next_bond_angle) * bond_r
                    next_bond_y = 60 + math.sin(next_bond_angle) * bond_r
                    pygame.draw.line(s, (80, 230, 160), (bond_x, bond_y), 
                                   (next_bond_x, next_bond_y), 1)
            # 40个反应泡泡（从中心冒出）
            for bubble_i in range(40):
                bubble_progress = ((t * 4 + bubble_i * 0.05) % 1.0)
                bubble_angle = (bubble_i * 9) * 0.01745
                bubble_r = 5 + int(bubble_progress * 40)
                bubble_x = 60 + math.cos(bubble_angle) * bubble_r
                bubble_y = 60 + math.sin(bubble_angle) * bubble_r
                bubble_size = int(3 * (1 - bubble_progress))
                if bubble_size > 0:
                    bubble_alpha = int(180 * (1 - bubble_progress))
                    pygame.draw.circle(s, (100, 255, 180, bubble_alpha), 
                                     (int(bubble_x), int(bubble_y)), bubble_size)
            # 中心反应核心
            pygame.draw.circle(s, (120, 255, 200), (60, 60), 10)
            pygame.draw.circle(s, (100, 255, 180), (60, 60), 6)
        
        elif model_style == "chronos_meteorological":
            # 气象预报·风云变幻 - 气象站时钟，天气图标，云图旋转，雨滴雪花
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 12个天气图标位置（环绕）
            weather_icons = [
                (255, 200, 100),  # 阳光
                (200, 200, 200),  # 阴天
                (100, 150, 255),  # 雨
                (255, 255, 255)   # 雪
            ]
            for icon_i in range(12):
                icon_angle = (icon_i * 30 + t * 8) * 0.01745
                icon_r = 40
                icon_x = 60 + math.cos(icon_angle) * icon_r
                icon_y = 60 + math.sin(icon_angle) * icon_r
                icon_color = weather_icons[icon_i % 4]
                # 简化图标（圆圈）
                pygame.draw.circle(s, icon_color, (int(icon_x), int(icon_y)), 5)
                if icon_i % 4 == 0:  # 阳光（射线）
                    for ray in range(6):
                        ray_angle = (ray * 60) * 0.01745
                        ray_end_x = icon_x + math.cos(ray_angle) * 8
                        ray_end_y = icon_y + math.sin(ray_angle) * 8
                        pygame.draw.line(s, icon_color, (icon_x, icon_y), 
                                       (ray_end_x, ray_end_y), 1)
                elif icon_i % 4 == 2:  # 雨（下落线）
                    for drop in range(3):
                        drop_y = icon_y + 5 + drop * 3
                        pygame.draw.line(s, icon_color, (icon_x, icon_y + 5), 
                                       (icon_x, drop_y), 1)
            # 8个云形成（卫星云图旋转）
            for cloud_i in range(8):
                cloud_angle = (cloud_i * 45 + t * 15) * 0.01745
                cloud_r = 28 + int(5 * math.sin(t * 2 + cloud_i))
                cloud_x = 60 + math.cos(cloud_angle) * cloud_r
                cloud_y = 60 + math.sin(cloud_angle) * cloud_r
                # 云朵形状（3个重叠圆）
                pygame.draw.circle(s, (180, 220, 255), (int(cloud_x) - 3, int(cloud_y)), 4)
                pygame.draw.circle(s, (180, 220, 255), (int(cloud_x) + 3, int(cloud_y)), 4)
                pygame.draw.circle(s, (180, 220, 255), (int(cloud_x), int(cloud_y) - 3), 5)
            # 气压计指针
            pressure_hand = (t * 12 - 90) * 0.01745
            phx = 60 + math.cos(pressure_hand) * 32
            phy = 60 + math.sin(pressure_hand) * 32
            pygame.draw.line(s, (150, 200, 255), (60, 60), (phx, phy), 3)
            # 中心温度计
            pygame.draw.circle(s, (180, 220, 255), (60, 60), 12)
            pygame.draw.circle(s, (150, 200, 255), (60, 60), 8)
            # 下落雨滴（20个）
            for rain_i in range(20):
                rain_progress = ((t * 3 + rain_i * 0.1) % 1.0)
                rain_x = 20 + (rain_i * 5) % 100
                rain_y = int(rain_progress * 120)
                pygame.draw.line(s, (100, 150, 255), (rain_x, rain_y), 
                               (rain_x, rain_y + 4), 1)
        
        elif model_style == "chronos_archaeological":
            # 考古发掘·文明密码 - 古文明遗迹时钟，象形文字，陶器碎片，分层挖掘
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 考古分层（5层土壤）
            strata_colors = [
                (200, 160, 100), (190, 150, 90),
                (180, 140, 80), (170, 130, 70),
                (160, 120, 60)
            ]
            for layer in range(5):
                layer_y = 25 + layer * 15
                layer_height = 15
                pygame.draw.rect(s, strata_colors[layer], 
                               (10, layer_y, 100, layer_height))
                # 土层纹理线
                for texture_line in range(3):
                    line_y = layer_y + texture_line * 5
                    pygame.draw.line(s, (180 - layer * 10, 140 - layer * 10, 80 - layer * 10),
                                   (10, line_y), (110, line_y), 1)
            # 20个象形文字符号（环绕）
            hieroglyph_shapes = [
                [(0, -3), (0, 3)],        # 竖线
                [(-3, 0), (3, 0)],        # 横线
                [(-2, -2), (2, 2)],       # 斜线
                [(-2, 2), (2, -2)]        # 反斜
            ]
            for glyph_i in range(20):
                glyph_angle = (glyph_i * 18 + t * 5) * 0.01745
                glyph_r = 42
                glyph_x = 60 + math.cos(glyph_angle) * glyph_r
                glyph_y = 60 + math.sin(glyph_angle) * glyph_r
                shape = hieroglyph_shapes[glyph_i % 4]
                glyph_start = (glyph_x + shape[0][0], glyph_y + shape[0][1])
                glyph_end = (glyph_x + shape[1][0], glyph_y + shape[1][1])
                pygame.draw.line(s, (220, 180, 120), glyph_start, glyph_end, 2)
            # 16个陶器碎片（拼接）
            for shard_i in range(16):
                shard_angle = (shard_i * 22.5 + t * 8) * 0.01745
                shard_r = 30 + int(5 * math.sin(t + shard_i))
                shard_x = 60 + math.cos(shard_angle) * shard_r
                shard_y = 60 + math.sin(shard_angle) * shard_r
                # 碎片不规则四边形
                shard_points = [
                    (shard_x - 3, shard_y - 2),
                    (shard_x + 2, shard_y - 3),
                    (shard_x + 3, shard_y + 2),
                    (shard_x - 2, shard_y + 3)
                ]
                pygame.draw.polygon(s, (200, 160, 100), shard_points)
                pygame.draw.polygon(s, (180, 140, 80), shard_points, 1)
            # 中心文明核心（罗盘）
            pygame.draw.circle(s, (220, 180, 120), (60, 60), 15, 2)
            pygame.draw.circle(s, (200, 160, 100), (60, 60), 10)
            # 指针（挖掘进度）
            excavation_hand = (t * 6 - 90) * 0.01745
            ehx = 60 + math.cos(excavation_hand) * 28
            ehy = 60 + math.sin(excavation_hand) * 28
            pygame.draw.line(s, (180, 140, 80), (60, 60), (ehx, ehy), 3)
    
    elif pid == "puppeteer":
        # ========== Puppeteer - 牵线木偶师·玛丽奥 ==========
        # 哥特傀儡美学，提线木偶+十字架+丝线，深紫与暗金配色
        purple_dark = (80, 40, 120)
        purple_light = (150, 100, 200)
        gold_dark = (180, 150, 80)
        thread_color = (200, 180, 220)
        
        # 主体十字架控制架
        pygame.draw.rect(s, purple_dark, (55, 15, 10, 50))  # 竖杆
        pygame.draw.rect(s, purple_dark, (35, 25, 50, 8))   # 横杆
        pygame.draw.rect(s, gold_dark, (55, 15, 10, 50), 2)
        pygame.draw.rect(s, gold_dark, (35, 25, 50, 8), 2)
        
        # 中心傀儡人偶
        puppet_sway = math.sin(t * 3) * 5
        puppet_cx = 60 + puppet_sway
        # 傀儡头
        pygame.draw.circle(s, (240, 220, 200), (int(puppet_cx), 50), 12)
        pygame.draw.circle(s, purple_dark, (int(puppet_cx) - 4, 48), 3)  # 左眼
        pygame.draw.circle(s, purple_dark, (int(puppet_cx) + 4, 48), 3)  # 右眼
        pygame.draw.line(s, purple_dark, (int(puppet_cx) - 3, 55), (int(puppet_cx) + 3, 55), 2)  # 嘴
        # 傀儡身体
        pygame.draw.rect(s, purple_light, (int(puppet_cx) - 8, 62, 16, 25))
        pygame.draw.rect(s, gold_dark, (int(puppet_cx) - 8, 62, 16, 25), 1)
        # 傀儡手臂
        arm_angle_l = math.sin(t * 4) * 0.3
        arm_angle_r = math.sin(t * 4 + 1) * 0.3
        arm_l_x = puppet_cx - 8 + math.cos(arm_angle_l - 2.5) * 18
        arm_l_y = 68 + math.sin(arm_angle_l - 2.5) * 18
        arm_r_x = puppet_cx + 8 + math.cos(arm_angle_r - 0.5) * 18
        arm_r_y = 68 + math.sin(arm_angle_r - 0.5) * 18
        pygame.draw.line(s, (240, 220, 200), (int(puppet_cx) - 8, 68), (int(arm_l_x), int(arm_l_y)), 3)
        pygame.draw.line(s, (240, 220, 200), (int(puppet_cx) + 8, 68), (int(arm_r_x), int(arm_r_y)), 3)
        # 傀儡腿
        leg_angle_l = math.sin(t * 4 + 0.5) * 0.2
        leg_angle_r = math.sin(t * 4 + 1.5) * 0.2
        leg_l_x = puppet_cx - 4 + math.cos(leg_angle_l + 1.57) * 20
        leg_l_y = 87 + math.sin(leg_angle_l + 1.57) * 20
        leg_r_x = puppet_cx + 4 + math.cos(leg_angle_r + 1.57) * 20
        leg_r_y = 87 + math.sin(leg_angle_r + 1.57) * 20
        pygame.draw.line(s, (240, 220, 200), (int(puppet_cx) - 4, 87), (int(leg_l_x), int(leg_l_y)), 3)
        pygame.draw.line(s, (240, 220, 200), (int(puppet_cx) + 4, 87), (int(leg_r_x), int(leg_r_y)), 3)
        
        # 提线（从控制架到傀儡各部位）
        thread_points = [
            (60, 33, puppet_cx, 38),        # 头
            (45, 29, arm_l_x, arm_l_y),     # 左手
            (75, 29, arm_r_x, arm_r_y),     # 右手
            (50, 29, leg_l_x, leg_l_y),     # 左脚
            (70, 29, leg_r_x, leg_r_y),     # 右脚
        ]
        for tx1, ty1, tx2, ty2 in thread_points:
            # 丝线闪烁效果
            thread_alpha = int(150 + 50 * math.sin(t * 6 + tx1 * 0.1))
            thread_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(thread_surf, (*thread_color, thread_alpha), 
                           (int(tx1), int(ty1)), (int(tx2), int(ty2)), 1)
            s.blit(thread_surf, (0, 0))
        
        # 环绕的小傀儡灵魂（6个）
        for soul_i in range(6):
            soul_angle = (soul_i * 60 + t * 30) * 0.01745
            soul_r = 48
            soul_x = 60 + math.cos(soul_angle) * soul_r
            soul_y = 60 + math.sin(soul_angle) * soul_r
            # 迷你傀儡头
            soul_alpha = int(180 + 50 * math.sin(t * 4 + soul_i))
            soul_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(soul_surf, (*purple_light, soul_alpha), (int(soul_x), int(soul_y)), 6)
            pygame.draw.circle(soul_surf, (*gold_dark, soul_alpha), (int(soul_x), int(soul_y)), 6, 1)
            # 迷你X眼
            pygame.draw.line(soul_surf, (*purple_dark, soul_alpha), 
                           (int(soul_x) - 2, int(soul_y) - 2), (int(soul_x) + 2, int(soul_y) + 2), 1)
            pygame.draw.line(soul_surf, (*purple_dark, soul_alpha), 
                           (int(soul_x) - 2, int(soul_y) + 2), (int(soul_x) + 2, int(soul_y) - 2), 1)
            s.blit(soul_surf, (0, 0))
        
        # 命运丝线网络（连接各小傀儡）
        for net_i in range(6):
            net_angle1 = (net_i * 60 + t * 30) * 0.01745
            net_angle2 = ((net_i + 1) * 60 + t * 30) * 0.01745
            nx1 = 60 + math.cos(net_angle1) * 48
            ny1 = 60 + math.sin(net_angle1) * 48
            nx2 = 60 + math.cos(net_angle2) * 48
            ny2 = 60 + math.sin(net_angle2) * 48
            net_alpha = int(80 + 40 * math.sin(t * 3 + net_i))
            net_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.line(net_surf, (*thread_color, net_alpha), 
                           (int(nx1), int(ny1)), (int(nx2), int(ny2)), 1)
            s.blit(net_surf, (0, 0))
        
        # ========== Puppeteer 专属涂装 ==========
        if model_style == "puppeteer_gothic":
            # 哥特剧院·暗夜傀儡 - 维多利亚哥特风格，蜘蛛网+铁艺+红色天鹅绒
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 哥特铁艺蜘蛛网框架
            for web_ring in range(5):
                web_r = 15 + web_ring * 10
                pygame.draw.circle(s, (40, 20, 30), (60, 60), web_r, 1)
            for web_spoke in range(12):
                spoke_angle = (web_spoke * 30) * 0.01745
                sx = 60 + math.cos(spoke_angle) * 55
                sy = 60 + math.sin(spoke_angle) * 55
                pygame.draw.line(s, (50, 25, 35), (60, 60), (int(sx), int(sy)), 1)
            # 中央暗夜傀儡（吊在蛛网上）
            puppet_swing = math.sin(t * 2) * 8
            pcx = 60 + puppet_swing
            # 破碎瓷娃娃脸
            pygame.draw.circle(s, (220, 200, 190), (int(pcx), 45), 14)
            # 裂纹
            for crack in range(3):
                crack_angle = (crack * 60 + 30) * 0.01745
                cx1 = pcx + math.cos(crack_angle) * 5
                cy1 = 45 + math.sin(crack_angle) * 5
                cx2 = pcx + math.cos(crack_angle) * 14
                cy2 = 45 + math.sin(crack_angle) * 14
                pygame.draw.line(s, (80, 40, 50), (int(cx1), int(cy1)), (int(cx2), int(cy2)), 1)
            # 空洞眼睛（红色光点）
            eye_glow = int(200 + 55 * math.sin(t * 5))
            pygame.draw.circle(s, (eye_glow, 30, 30), (int(pcx) - 5, 43), 4)
            pygame.draw.circle(s, (eye_glow, 30, 30), (int(pcx) + 5, 43), 4)
            pygame.draw.circle(s, (255, 100, 100), (int(pcx) - 5, 43), 2)
            pygame.draw.circle(s, (255, 100, 100), (int(pcx) + 5, 43), 2)
            # 红色天鹅绒裙摆（波浪形）
            dress_points = [(int(pcx) - 12, 60)]
            for wave in range(8):
                wave_x = pcx - 12 + wave * 3
                wave_y = 85 + math.sin(t * 4 + wave) * 3
                dress_points.append((int(wave_x), int(wave_y)))
            dress_points.append((int(pcx) + 12, 60))
            pygame.draw.polygon(s, (120, 30, 50), dress_points)
            # 悬挂丝线（蜘蛛丝质感）
            for thread_i in range(5):
                thread_x = pcx - 8 + thread_i * 4
                thread_sway = math.sin(t * 3 + thread_i) * 2
                pygame.draw.line(s, (80, 80, 90), (int(thread_x + thread_sway), 10), (int(thread_x), 45 - 14), 1)
            # 飘落的蜘蛛（3只）
            for spider_i in range(3):
                spider_y = ((t * 20 + spider_i * 40) % 80) + 20
                spider_x = 20 + spider_i * 40 + math.sin(t * 2 + spider_i) * 5
                pygame.draw.circle(s, (30, 20, 25), (int(spider_x), int(spider_y)), 3)
                # 蜘蛛腿
                for leg in range(4):
                    leg_angle = (leg * 45 + 22.5) * 0.01745
                    lx = spider_x + math.cos(leg_angle) * 5
                    ly = spider_y + math.sin(leg_angle) * 5
                    pygame.draw.line(s, (30, 20, 25), (int(spider_x), int(spider_y)), (int(lx), int(ly)), 1)
        
        elif model_style == "puppeteer_music_box":
            # 八音盒·永恒旋律 - 精美八音盒，瓷娃娃芭蕾舞者
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 八音盒底座（金色装饰边框）
            pygame.draw.rect(s, (60, 40, 30), (20, 70, 80, 35), border_radius=5)
            pygame.draw.rect(s, (200, 160, 80), (20, 70, 80, 35), 2, border_radius=5)
            # 金色花纹装饰
            for deco_i in range(6):
                deco_x = 28 + deco_i * 12
                pygame.draw.circle(s, (220, 180, 100), (deco_x, 85), 3)
            # 旋转齿轮（内部机械）
            gear_angle = t * 60
            for gear_i in range(8):
                g_angle = (gear_i * 45 + gear_angle) * 0.01745
                gx = 60 + math.cos(g_angle) * 25
                gy = 87 + math.sin(g_angle) * 8
                pygame.draw.circle(s, (180, 140, 60), (int(gx), int(gy)), 2)
            # 芭蕾舞者瓷娃娃（旋转）
            dancer_angle = t * 90
            dancer_cx = 60
            dancer_cy = 50
            # 旋转的裙摆（圆锥形）
            for skirt_layer in range(3):
                skirt_r = 12 + skirt_layer * 4
                skirt_y = 55 + skirt_layer * 3
                skirt_points = []
                for skirt_seg in range(16):
                    seg_angle = (skirt_seg * 22.5 + dancer_angle) * 0.01745
                    wave = math.sin(seg_angle * 4) * 2
                    sx = dancer_cx + math.cos(seg_angle) * (skirt_r + wave)
                    sy = skirt_y + math.sin(seg_angle) * 3
                    skirt_points.append((int(sx), int(sy)))
                pygame.draw.polygon(s, (255, 200, 220), skirt_points)
                pygame.draw.polygon(s, (220, 170, 190), skirt_points, 1)
            # 瓷娃娃上身
            pygame.draw.ellipse(s, (255, 240, 235), (dancer_cx - 6, 40, 12, 18))
            # 瓷娃娃头（精致）
            pygame.draw.circle(s, (255, 245, 240), (dancer_cx, 32), 10)
            # 腮红
            pygame.draw.circle(s, (255, 180, 180), (dancer_cx - 5, 34), 3)
            pygame.draw.circle(s, (255, 180, 180), (dancer_cx + 5, 34), 3)
            # 闭眼（弧线）
            pygame.draw.arc(s, (60, 40, 40), (dancer_cx - 7, 28, 6, 6), 0, 3.14159, 2)
            pygame.draw.arc(s, (60, 40, 40), (dancer_cx + 1, 28, 6, 6), 0, 3.14159, 2)
            # 举起的手臂
            arm_l_angle = math.sin(t * 2) * 0.3 - 1.2
            arm_r_angle = math.sin(t * 2 + 1) * 0.3 + 1.2 - 3.14159
            arm_l_x = dancer_cx + math.cos(arm_l_angle) * 15
            arm_l_y = 45 + math.sin(arm_l_angle) * 15
            arm_r_x = dancer_cx + math.cos(arm_r_angle) * 15
            arm_r_y = 45 + math.sin(arm_r_angle) * 15
            pygame.draw.line(s, (255, 240, 235), (dancer_cx - 5, 45), (int(arm_l_x), int(arm_l_y)), 3)
            pygame.draw.line(s, (255, 240, 235), (dancer_cx + 5, 45), (int(arm_r_x), int(arm_r_y)), 3)
            # 音符粒子飘出
            for note_i in range(8):
                note_phase = ((t * 1.5 + note_i * 0.3) % 1.0)
                note_angle = (note_i * 45 + t * 20) * 0.01745
                note_r = 30 + note_phase * 25
                note_x = 60 + math.cos(note_angle) * note_r
                note_y = 50 + math.sin(note_angle) * note_r - note_phase * 20
                note_alpha = int(200 * (1 - note_phase))
                if note_alpha > 0:
                    note_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    # 音符形状
                    pygame.draw.circle(note_surf, (220, 180, 100, note_alpha), (int(note_x), int(note_y)), 3)
                    pygame.draw.line(note_surf, (220, 180, 100, note_alpha), (int(note_x) + 3, int(note_y)), (int(note_x) + 3, int(note_y) - 8), 1)
                    s.blit(note_surf, (0, 0))
        
        elif model_style == "puppeteer_voodoo":
            # 巫毒咒术·灵魂缝针 - 麻布巫毒娃娃，针和符文
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 麻布背景纹理
            for fiber_i in range(20):
                fiber_x = random.randint(20, 100)
                fiber_y = random.randint(20, 100)
                pygame.draw.line(s, (120, 100, 70), (fiber_x, fiber_y), (fiber_x + random.randint(-10, 10), fiber_y + random.randint(-10, 10)), 1)
            # 巫毒娃娃主体（粗糙麻布质感）
            body_points = [(60, 25), (75, 35), (80, 55), (70, 90), (50, 90), (40, 55), (45, 35)]
            pygame.draw.polygon(s, (160, 140, 100), body_points)
            pygame.draw.polygon(s, (100, 80, 50), body_points, 2)
            # 缝合线（X形针脚）
            stitch_positions = [(55, 40), (65, 40), (50, 60), (70, 60), (55, 75), (65, 75)]
            for sx, sy in stitch_positions:
                pygame.draw.line(s, (80, 60, 40), (sx - 3, sy - 3), (sx + 3, sy + 3), 2)
                pygame.draw.line(s, (80, 60, 40), (sx - 3, sy + 3), (sx + 3, sy - 3), 2)
            # 纽扣眼睛
            pygame.draw.circle(s, (40, 30, 20), (52, 35), 5)
            pygame.draw.circle(s, (40, 30, 20), (68, 35), 5)
            pygame.draw.line(s, (80, 60, 40), (49, 32), (55, 38), 1)
            pygame.draw.line(s, (80, 60, 40), (49, 38), (55, 32), 1)
            pygame.draw.line(s, (80, 60, 40), (65, 32), (71, 38), 1)
            pygame.draw.line(s, (80, 60, 40), (65, 38), (71, 32), 1)
            # 扎入的针（动态抖动）
            for pin_i in range(5):
                pin_x = 45 + pin_i * 8
                pin_y = 50 + math.sin(t * 8 + pin_i) * 2
                pin_angle = (pin_i * 15 - 30) * 0.01745
                pin_end_x = pin_x + math.cos(pin_angle) * 20
                pin_end_y = pin_y + math.sin(pin_angle) * 20 - 15
                pygame.draw.line(s, (180, 180, 190), (pin_x, int(pin_y)), (int(pin_end_x), int(pin_end_y)), 2)
                pygame.draw.circle(s, (255, 50, 50), (int(pin_end_x), int(pin_end_y) - 3), 3)
            # 诅咒符文环绕
            for rune_i in range(6):
                rune_angle = (rune_i * 60 + t * 25) * 0.01745
                rune_r = 50
                rune_x = 60 + math.cos(rune_angle) * rune_r
                rune_y = 60 + math.sin(rune_angle) * rune_r
                rune_alpha = int(150 + 80 * math.sin(t * 4 + rune_i))
                rune_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                # 简单符文形状
                pygame.draw.circle(rune_surf, (200, 100, 50, rune_alpha), (int(rune_x), int(rune_y)), 6, 2)
                pygame.draw.line(rune_surf, (200, 100, 50, rune_alpha), (int(rune_x) - 4, int(rune_y)), (int(rune_x) + 4, int(rune_y)), 1)
                pygame.draw.line(rune_surf, (200, 100, 50, rune_alpha), (int(rune_x), int(rune_y) - 4), (int(rune_x), int(rune_y) + 4), 1)
                s.blit(rune_surf, (0, 0))
        
        elif model_style == "puppeteer_circus":
            # 暗黑马戏·疯狂大帐 - 恐怖马戏团，小丑傀儡
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 马戏团帐篷条纹（红白染血）
            for stripe_i in range(12):
                stripe_angle = (stripe_i * 30) * 0.01745
                stripe_color = (200, 50, 50) if stripe_i % 2 == 0 else (240, 230, 220)
                # 血渍效果
                if stripe_i % 3 == 0:
                    stripe_color = (150, 30, 30)
                stripe_points = [(60, 15)]
                sx1 = 60 + math.cos(stripe_angle - 0.13) * 50
                sy1 = 60 + math.sin(stripe_angle - 0.13) * 50
                sx2 = 60 + math.cos(stripe_angle + 0.13) * 50
                sy2 = 60 + math.sin(stripe_angle + 0.13) * 50
                stripe_points.extend([(int(sx1), int(sy1)), (int(sx2), int(sy2))])
                pygame.draw.polygon(s, stripe_color, stripe_points)
            # 中央疯狂小丑傀儡
            clown_bounce = abs(math.sin(t * 6)) * 5
            clown_y = 50 - clown_bounce
            # 小丑脸（白色+红鼻子）
            pygame.draw.circle(s, (255, 255, 255), (60, int(clown_y)), 12)
            pygame.draw.circle(s, (255, 0, 0), (60, int(clown_y) + 2), 4)  # 红鼻子
            # 疯狂眼睛（不对称，抖动）
            left_eye_x = 55 + math.sin(t * 10) * 2
            right_eye_x = 65 + math.cos(t * 10) * 2
            pygame.draw.circle(s, (0, 0, 0), (int(left_eye_x), int(clown_y) - 3), 4)
            pygame.draw.circle(s, (0, 0, 0), (int(right_eye_x), int(clown_y) - 3), 3)
            pygame.draw.circle(s, (255, 255, 0), (int(left_eye_x), int(clown_y) - 3), 2)
            pygame.draw.circle(s, (255, 0, 0), (int(right_eye_x), int(clown_y) - 3), 1)
            # 扭曲笑容
            smile_points = [(52, int(clown_y) + 5)]
            for sm in range(5):
                sm_x = 52 + sm * 4
                sm_y = clown_y + 8 + math.sin(t * 8 + sm) * 2
                smile_points.append((sm_x, int(sm_y)))
            smile_points.append((68, int(clown_y) + 5))
            pygame.draw.lines(s, (200, 0, 0), False, smile_points, 2)
            # 小丑帽（尖顶+铃铛）
            hat_points = [(50, int(clown_y) - 10), (60, int(clown_y) - 30), (70, int(clown_y) - 10)]
            pygame.draw.polygon(s, (200, 50, 50), hat_points)
            pygame.draw.polygon(s, (255, 215, 0), hat_points, 2)
            bell_swing = math.sin(t * 8) * 5
            pygame.draw.circle(s, (255, 215, 0), (60 + int(bell_swing), int(clown_y) - 32), 4)
            # 悬吊的其他小丑傀儡（模糊背景）
            for bg_clown in range(3):
                bg_x = 25 + bg_clown * 35
                bg_y = 80 + math.sin(t * 2 + bg_clown) * 5
                bg_alpha = 100
                bg_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(bg_surf, (255, 255, 255, bg_alpha), (bg_x, int(bg_y)), 6)
                pygame.draw.circle(bg_surf, (255, 0, 0, bg_alpha), (bg_x, int(bg_y) + 1), 2)
                s.blit(bg_surf, (0, 0))
        
        elif model_style == "puppeteer_kabuki":
            # 歌舞伎·能面之舞 - 日本歌舞伎，能面具，和服丝线
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 和纸背景纹理
            pygame.draw.rect(s, (250, 245, 235), (15, 15, 90, 90))
            for paper_line in range(10):
                pygame.draw.line(s, (240, 230, 220), (15, 15 + paper_line * 10), (105, 15 + paper_line * 10), 1)
            # 能面具（白面红纹）
            mask_sway = math.sin(t * 1.5) * 3
            mask_cx = 60 + mask_sway
            # 面具轮廓
            mask_points = [(int(mask_cx), 25), (int(mask_cx) + 20, 40), (int(mask_cx) + 18, 65), 
                          (int(mask_cx), 75), (int(mask_cx) - 18, 65), (int(mask_cx) - 20, 40)]
            pygame.draw.polygon(s, (255, 250, 245), mask_points)
            pygame.draw.polygon(s, (200, 50, 50), mask_points, 2)
            # 能面眼睛（细长弯曲）
            pygame.draw.arc(s, (20, 20, 20), (int(mask_cx) - 15, 38, 12, 8), 0.5, 2.6, 2)
            pygame.draw.arc(s, (20, 20, 20), (int(mask_cx) + 3, 38, 12, 8), 0.5, 2.6, 2)
            # 红色唇纹
            pygame.draw.ellipse(s, (200, 50, 50), (int(mask_cx) - 6, 58, 12, 6))
            # 额头红色图案
            pygame.draw.circle(s, (200, 50, 50), (int(mask_cx), 32), 4)
            # 和服丝线（优雅垂落）
            for silk_i in range(7):
                silk_x = 35 + silk_i * 8
                silk_wave = math.sin(t * 2 + silk_i * 0.5) * 3
                silk_points = []
                for silk_seg in range(8):
                    seg_y = 75 + silk_seg * 5
                    seg_x = silk_x + math.sin(t * 3 + silk_seg * 0.3) * silk_wave
                    silk_points.append((int(seg_x), seg_y))
                if len(silk_points) > 1:
                    silk_color = (200, 50, 50) if silk_i % 2 == 0 else (255, 215, 100)
                    pygame.draw.lines(s, silk_color, False, silk_points, 2)
            # 樱花瓣飘落
            for sakura_i in range(8):
                sakura_phase = ((t * 0.8 + sakura_i * 0.2) % 1.0)
                sakura_x = 20 + sakura_i * 12 + math.sin(t * 2 + sakura_i) * 10
                sakura_y = sakura_phase * 120
                sakura_rot = t * 100 + sakura_i * 45
                sakura_alpha = int(200 * (1 - abs(sakura_phase - 0.5) * 2))
                if sakura_alpha > 0:
                    sakura_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    # 花瓣形状
                    petal_points = []
                    for p in range(5):
                        p_angle = (p * 72 + sakura_rot) * 0.01745
                        p_r = 4 if p % 2 == 0 else 2
                        px = sakura_x + math.cos(p_angle) * p_r
                        py = sakura_y + math.sin(p_angle) * p_r
                        petal_points.append((int(px), int(py)))
                    pygame.draw.polygon(sakura_surf, (255, 180, 200, sakura_alpha), petal_points)
                    s.blit(sakura_surf, (0, 0))
        
        elif model_style == "puppeteer_clockwork":
            # 发条心脏·机械少女 - 蒸汽朋克发条人偶
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 黄铜底板
            pygame.draw.circle(s, (180, 140, 80), (60, 60), 50)
            pygame.draw.circle(s, (200, 160, 100), (60, 60), 50, 3)
            # 多层齿轮（不同速度旋转）
            gear_configs = [(60, 60, 35, 12, 1), (35, 45, 15, 8, -1.5), (85, 45, 15, 8, 1.5),
                           (45, 80, 12, 6, -2), (75, 80, 12, 6, 2)]
            for gx, gy, gr, teeth, speed in gear_configs:
                gear_rot = t * 30 * speed
                # 齿轮主体
                pygame.draw.circle(s, (160, 120, 60), (gx, gy), gr)
                pygame.draw.circle(s, (200, 160, 100), (gx, gy), gr, 2)
                # 齿轮齿
                for tooth in range(teeth):
                    tooth_angle = (tooth * 360 / teeth + gear_rot) * 0.01745
                    tx1 = gx + math.cos(tooth_angle) * gr
                    ty1 = gy + math.sin(tooth_angle) * gr
                    tx2 = gx + math.cos(tooth_angle) * (gr + 5)
                    ty2 = gy + math.sin(tooth_angle) * (gr + 5)
                    pygame.draw.line(s, (200, 160, 100), (int(tx1), int(ty1)), (int(tx2), int(ty2)), 3)
                # 中心孔
                pygame.draw.circle(s, (100, 80, 40), (gx, gy), gr // 3)
            # 机械少女轮廓（简化）
            girl_phase = math.sin(t * 2) * 0.1
            # 头部
            pygame.draw.circle(s, (220, 200, 180), (60, 40), 12)
            # 发条钥匙（从背后伸出，旋转）
            key_angle = t * 60
            key_x = 60 + math.cos(key_angle * 0.01745) * 8
            key_y = 40 + math.sin(key_angle * 0.01745) * 8
            pygame.draw.rect(s, (200, 160, 100), (int(key_x) - 2, 15, 4, 20))
            pygame.draw.circle(s, (200, 160, 100), (int(key_x), 12), 6, 2)
            # 蒸汽粒子喷出
            for steam_i in range(10):
                steam_phase = ((t * 3 + steam_i * 0.2) % 1.0)
                steam_x = 60 + (random.random() - 0.5) * 20
                steam_y = 20 - steam_phase * 30
                steam_alpha = int(150 * (1 - steam_phase))
                steam_size = int(5 * steam_phase + 2)
                if steam_alpha > 0 and steam_y > 0:
                    steam_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.circle(steam_surf, (200, 200, 200, steam_alpha), (int(steam_x), int(steam_y)), steam_size)
                    s.blit(steam_surf, (0, 0))
        
        elif model_style == "puppeteer_shadow":
            # 影子戏·剪影物语 - 中国皮影戏，半透明剪影
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 灯光背景（暖黄色渐变）
            for light_ring in range(10):
                light_r = 55 - light_ring * 5
                light_alpha = 50 + light_ring * 10
                pygame.draw.circle(s, (255, 220, 150, light_alpha), (60, 60), light_r)
            # 皮影人物（彩色半透明）
            shadow_sway = math.sin(t * 2) * 5
            shadow_cx = 60 + shadow_sway
            # 皮影轮廓（战士形态）
            shadow_color = (80, 40, 20, 200)
            shadow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 头部（带头盔/头饰）
            head_points = [(int(shadow_cx), 25), (int(shadow_cx) + 10, 30), (int(shadow_cx) + 8, 45),
                          (int(shadow_cx) - 8, 45), (int(shadow_cx) - 10, 30)]
            pygame.draw.polygon(shadow_surf, shadow_color, head_points)
            # 头饰羽毛
            for feather in range(3):
                f_angle = (-30 + feather * 30 + math.sin(t * 3) * 10) * 0.01745
                fx = shadow_cx + math.cos(f_angle) * 15
                fy = 25 + math.sin(f_angle) * 15 - 10
                pygame.draw.line(shadow_surf, (200, 100, 50, 180), (int(shadow_cx), 25), (int(fx), int(fy)), 2)
            # 身体
            body_points = [(int(shadow_cx) - 8, 45), (int(shadow_cx) + 8, 45),
                          (int(shadow_cx) + 12, 80), (int(shadow_cx) - 12, 80)]
            pygame.draw.polygon(shadow_surf, shadow_color, body_points)
            # 手臂（摆动）
            arm_angle = math.sin(t * 3) * 0.5
            left_arm_end = (shadow_cx - 20 + math.cos(arm_angle - 2) * 15, 55 + math.sin(arm_angle - 2) * 15)
            right_arm_end = (shadow_cx + 20 + math.cos(arm_angle + 1) * 15, 55 + math.sin(arm_angle + 1) * 15)
            pygame.draw.line(shadow_surf, shadow_color, (int(shadow_cx) - 8, 50), (int(left_arm_end[0]), int(left_arm_end[1])), 4)
            pygame.draw.line(shadow_surf, shadow_color, (int(shadow_cx) + 8, 50), (int(right_arm_end[0]), int(right_arm_end[1])), 4)
            # 武器（长枪）
            spear_end = (right_arm_end[0] + 25, right_arm_end[1] - 30)
            pygame.draw.line(shadow_surf, (100, 60, 30, 200), (int(right_arm_end[0]), int(right_arm_end[1])), (int(spear_end[0]), int(spear_end[1])), 3)
            s.blit(shadow_surf, (0, 0))
            # 控制杆（竹竿）
            for rod in range(3):
                rod_x = 30 + rod * 30
                rod_alpha = 100 + int(50 * math.sin(t * 2 + rod))
                pygame.draw.line(s, (150, 120, 80, rod_alpha), (rod_x, 100), (rod_x, 120), 2)
        
        elif model_style == "puppeteer_marionette":
            # 提线精灵·星辰丝网 - 银色星光丝线，水晶傀儡
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 星空背景
            for star_i in range(30):
                star_x = random.randint(10, 110)
                star_y = random.randint(10, 110)
                star_twinkle = int(150 + 100 * math.sin(t * 5 + star_i))
                pygame.draw.circle(s, (200, 220, 255, star_twinkle), (star_x, star_y), 1)
            # 水晶傀儡（半透明晶体质感）
            crystal_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            crystal_sway = math.sin(t * 2) * 3
            crystal_cx = 60 + crystal_sway
            # 水晶头（多面体）
            head_facets = []
            for facet in range(6):
                f_angle = (facet * 60 + t * 20) * 0.01745
                fx = crystal_cx + math.cos(f_angle) * 10
                fy = 40 + math.sin(f_angle) * 10
                head_facets.append((int(fx), int(fy)))
            pygame.draw.polygon(crystal_surf, (200, 220, 255, 180), head_facets)
            pygame.draw.polygon(crystal_surf, (255, 255, 255, 200), head_facets, 2)
            # 水晶身体
            body_facets = [(int(crystal_cx) - 10, 50), (int(crystal_cx) + 10, 50),
                          (int(crystal_cx) + 8, 80), (int(crystal_cx), 90), (int(crystal_cx) - 8, 80)]
            pygame.draw.polygon(crystal_surf, (180, 200, 255, 150), body_facets)
            pygame.draw.polygon(crystal_surf, (220, 240, 255, 200), body_facets, 2)
            s.blit(crystal_surf, (0, 0))
            # 星辰丝线（银色闪烁）
            thread_points = [(60, 10), (crystal_cx, 30),  # 头
                            (40, 15), (crystal_cx - 15, 55),  # 左手
                            (80, 15), (crystal_cx + 15, 55),  # 右手
                            (50, 12), (crystal_cx - 5, 85),   # 左脚
                            (70, 12), (crystal_cx + 5, 85)]   # 右脚
            for i in range(0, len(thread_points), 2):
                thread_alpha = int(200 + 55 * math.sin(t * 8 + i))
                thread_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(thread_surf, (220, 230, 255, thread_alpha), 
                               (int(thread_points[i][0]), int(thread_points[i][1])),
                               (int(thread_points[i+1][0]), int(thread_points[i+1][1])), 1)
                # 丝线上的星星
                for star_pos in range(3):
                    star_t = star_pos / 3
                    sx = thread_points[i][0] + (thread_points[i+1][0] - thread_points[i][0]) * star_t
                    sy = thread_points[i][1] + (thread_points[i+1][1] - thread_points[i][1]) * star_t
                    star_pulse = int(200 + 55 * math.sin(t * 10 + i + star_pos))
                    pygame.draw.circle(thread_surf, (255, 255, 255, star_pulse), (int(sx), int(sy)), 2)
                s.blit(thread_surf, (0, 0))
        
        elif model_style == "puppeteer_porcelain":
            # 瓷器人偶·碎裂之美 - 青花瓷娃娃，金缮修复
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 瓷器底座
            pygame.draw.ellipse(s, (240, 245, 250), (30, 85, 60, 20))
            pygame.draw.ellipse(s, (50, 80, 150), (30, 85, 60, 20), 2)
            # 瓷娃娃主体
            # 身体（瓷白色）
            pygame.draw.ellipse(s, (250, 252, 255), (45, 45, 30, 45))
            # 青花纹理
            for pattern in range(5):
                p_angle = (pattern * 72 + 20) * 0.01745
                px = 60 + math.cos(p_angle) * 10
                py = 65 + math.sin(p_angle) * 15
                pygame.draw.circle(s, (50, 80, 150), (int(px), int(py)), 3, 1)
            # 头部
            pygame.draw.circle(s, (250, 252, 255), (60, 35), 15)
            # 青花眼睛
            pygame.draw.circle(s, (50, 80, 150), (54, 33), 3)
            pygame.draw.circle(s, (50, 80, 150), (66, 33), 3)
            # 裂纹+金缮
            crack_paths = [
                [(45, 30), (50, 40), (48, 55)],
                [(70, 25), (75, 35), (72, 50)],
                [(55, 60), (60, 75), (58, 88)]
            ]
            for crack_path in crack_paths:
                # 裂纹
                pygame.draw.lines(s, (80, 80, 80), False, crack_path, 1)
                # 金缮（金色修复线）
                gold_glow = int(200 + 55 * math.sin(t * 3))
                for i in range(len(crack_path) - 1):
                    pygame.draw.line(s, (gold_glow, int(gold_glow * 0.7), 50), 
                                   crack_path[i], crack_path[i+1], 2)
            # 飘落的碎片（金边）
            for shard_i in range(4):
                shard_phase = ((t * 0.5 + shard_i * 0.3) % 1.0)
                shard_x = 30 + shard_i * 20 + math.sin(t + shard_i) * 10
                shard_y = shard_phase * 100 + 10
                shard_rot = t * 100 + shard_i * 90
                shard_alpha = int(200 * (1 - shard_phase))
                if shard_alpha > 0:
                    shard_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    # 碎片形状
                    shard_points = []
                    for sp in range(3):
                        sp_angle = (sp * 120 + shard_rot) * 0.01745
                        spx = shard_x + math.cos(sp_angle) * 5
                        spy = shard_y + math.sin(sp_angle) * 5
                        shard_points.append((int(spx), int(spy)))
                    pygame.draw.polygon(shard_surf, (250, 252, 255, shard_alpha), shard_points)
                    pygame.draw.polygon(shard_surf, (220, 180, 50, shard_alpha), shard_points, 1)
                    s.blit(shard_surf, (0, 0))
        
        elif model_style == "puppeteer_nightmare":
            # 噩梦编织·深渊之弦 - 恐惧深渊，扭曲丝线连接眼睛
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 深渊黑暗背景
            for void_ring in range(8):
                void_r = 55 - void_ring * 6
                void_alpha = 30 + void_ring * 15
                pygame.draw.circle(s, (20, 0, 40, void_alpha), (60, 60), void_r)
            # 中央巨眼
            eye_pulse = abs(math.sin(t * 2))
            eye_size = int(20 + eye_pulse * 5)
            pygame.draw.circle(s, (100, 0, 60), (60, 60), eye_size)
            pygame.draw.circle(s, (200, 50, 100), (60, 60), eye_size - 5)
            pygame.draw.circle(s, (0, 0, 0), (60, 60), eye_size - 12)
            # 瞳孔（追踪效果）
            pupil_x = 60 + math.sin(t * 1.5) * 3
            pupil_y = 60 + math.cos(t * 1.5) * 3
            pygame.draw.circle(s, (255, 0, 100), (int(pupil_x), int(pupil_y)), 3)
            # 扭曲丝线（从眼睛延伸）
            for string_i in range(12):
                string_angle = (string_i * 30 + t * 15) * 0.01745
                # 扭曲路径
                string_points = [(60, 60)]
                for seg in range(6):
                    seg_r = 20 + seg * 8
                    seg_angle = string_angle + math.sin(t * 4 + seg) * 0.3
                    sx = 60 + math.cos(seg_angle) * seg_r
                    sy = 60 + math.sin(seg_angle) * seg_r
                    string_points.append((int(sx), int(sy)))
                # 绘制扭曲线
                string_alpha = int(150 + 80 * math.sin(t * 5 + string_i))
                string_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                if len(string_points) > 1:
                    pygame.draw.lines(string_surf, (150, 50, 100, string_alpha), False, string_points, 2)
                s.blit(string_surf, (0, 0))
                # 末端小眼睛
                end_x, end_y = string_points[-1]
                pygame.draw.circle(s, (200, 50, 100), (end_x, end_y), 4)
                pygame.draw.circle(s, (0, 0, 0), (end_x, end_y), 2)
        
        elif model_style == "puppeteer_eden":
            # 伊甸傀儡·禁果之弦 - 伊甸园蛇与苹果，神圣与堕落
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 光环背景
            halo_pulse = abs(math.sin(t * 2))
            for halo in range(3):
                halo_r = 50 - halo * 10
                halo_alpha = int(50 + 30 * halo_pulse)
                pygame.draw.circle(s, (255, 230, 150, halo_alpha), (60, 60), halo_r)
            # 生命之树（中央）
            pygame.draw.line(s, (100, 70, 40), (60, 90), (60, 40), 4)
            # 树枝
            for branch in range(4):
                b_angle = (-60 + branch * 40) * 0.01745
                bx = 60 + math.cos(b_angle) * 20
                by = 50 + math.sin(b_angle) * 15
                pygame.draw.line(s, (100, 70, 40), (60, 55 - branch * 5), (int(bx), int(by)), 2)
            # 禁果（红苹果，发光）
            apple_glow = int(200 + 55 * math.sin(t * 4))
            pygame.draw.circle(s, (apple_glow, 30, 30), (75, 45), 8)
            pygame.draw.circle(s, (255, 50, 50), (75, 45), 6)
            # 苹果光芒
            for ray in range(6):
                ray_angle = (ray * 60 + t * 30) * 0.01745
                ray_end_x = 75 + math.cos(ray_angle) * 15
                ray_end_y = 45 + math.sin(ray_angle) * 15
                ray_alpha = int(100 + 50 * math.sin(t * 6 + ray))
                ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(ray_surf, (255, 200, 100, ray_alpha), (75, 45), (int(ray_end_x), int(ray_end_y)), 1)
                s.blit(ray_surf, (0, 0))
            # 缠绕的蛇（围绕树干）
            snake_points = []
            for snake_seg in range(20):
                snake_t = snake_seg / 20
                snake_y = 85 - snake_t * 50
                snake_x = 60 + math.sin(snake_t * 6 + t * 3) * 10
                snake_points.append((int(snake_x), int(snake_y)))
            if len(snake_points) > 1:
                pygame.draw.lines(s, (50, 100, 50), False, snake_points, 3)
            # 蛇头
            snake_head_x, snake_head_y = snake_points[-1]
            pygame.draw.circle(s, (60, 120, 60), (snake_head_x, snake_head_y), 5)
            # 蛇眼（红色）
            pygame.draw.circle(s, (255, 50, 50), (snake_head_x - 2, snake_head_y - 1), 2)
            pygame.draw.circle(s, (255, 50, 50), (snake_head_x + 2, snake_head_y - 1), 2)
            # 天使羽毛（堕落中）
            for feather_i in range(5):
                feather_phase = ((t * 0.3 + feather_i * 0.25) % 1.0)
                feather_x = 20 + feather_i * 20 + math.sin(t + feather_i) * 8
                feather_y = feather_phase * 110 + 5
                feather_rot = t * 50 + feather_i * 72
                feather_alpha = int(180 * (1 - feather_phase))
                if feather_alpha > 0:
                    feather_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    # 羽毛形状
                    f_points = [(int(feather_x), int(feather_y) - 6), 
                               (int(feather_x) - 3, int(feather_y) + 6),
                               (int(feather_x) + 3, int(feather_y) + 6)]
                    pygame.draw.polygon(feather_surf, (255, 255, 255, feather_alpha), f_points)
                    s.blit(feather_surf, (0, 0))
        
        elif model_style == "puppeteer_fate":
            # 命运纺车·三女神 - 希腊命运三女神，纺锤、量尺、剪刀
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 命运之轮背景
            wheel_rot = t * 10
            pygame.draw.circle(s, (60, 50, 80), (60, 60), 50, 2)
            for spoke in range(12):
                spoke_angle = (spoke * 30 + wheel_rot) * 0.01745
                sx = 60 + math.cos(spoke_angle) * 50
                sy = 60 + math.sin(spoke_angle) * 50
                pygame.draw.line(s, (80, 70, 100), (60, 60), (int(sx), int(sy)), 1)
            # 三女神象征物（环绕）
            symbols_angle = t * 20
            # 1. 纺锤（克洛托 - 纺织生命）
            spindle_angle = (symbols_angle) * 0.01745
            spindle_x = 60 + math.cos(spindle_angle) * 35
            spindle_y = 60 + math.sin(spindle_angle) * 35
            pygame.draw.ellipse(s, (200, 180, 220), (int(spindle_x) - 4, int(spindle_y) - 10, 8, 20))
            # 纺出的丝线
            for thread in range(8):
                thread_angle = (thread * 45 + t * 50) * 0.01745
                tx = spindle_x + math.cos(thread_angle) * (8 + thread * 2)
                ty = spindle_y + math.sin(thread_angle) * (8 + thread * 2)
                thread_alpha = 200 - thread * 20
                thread_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.line(thread_surf, (180, 150, 200, thread_alpha), (int(spindle_x), int(spindle_y)), (int(tx), int(ty)), 1)
                s.blit(thread_surf, (0, 0))
            # 2. 量尺（拉刻西斯 - 量度生命）
            ruler_angle = (symbols_angle + 120) * 0.01745
            ruler_x = 60 + math.cos(ruler_angle) * 35
            ruler_y = 60 + math.sin(ruler_angle) * 35
            pygame.draw.rect(s, (220, 200, 180), (int(ruler_x) - 12, int(ruler_y) - 3, 24, 6))
            # 刻度
            for mark in range(5):
                mark_x = ruler_x - 10 + mark * 5
                pygame.draw.line(s, (100, 80, 60), (int(mark_x), int(ruler_y) - 3), (int(mark_x), int(ruler_y) + 3), 1)
            # 3. 剪刀（阿特罗波斯 - 剪断生命）
            scissors_angle = (symbols_angle + 240) * 0.01745
            scissors_x = 60 + math.cos(scissors_angle) * 35
            scissors_y = 60 + math.sin(scissors_angle) * 35
            # 剪刀开合动画
            scissors_open = abs(math.sin(t * 4)) * 0.3
            pygame.draw.line(s, (180, 180, 200), (int(scissors_x), int(scissors_y)), 
                           (int(scissors_x) - 8, int(scissors_y) - 12 + scissors_open * 20), 3)
            pygame.draw.line(s, (180, 180, 200), (int(scissors_x), int(scissors_y)), 
                           (int(scissors_x) + 8, int(scissors_y) - 12 - scissors_open * 20), 3)
            pygame.draw.circle(s, (150, 150, 170), (int(scissors_x), int(scissors_y)), 4)
            # 中央命运之眼
            pygame.draw.circle(s, (150, 130, 180), (60, 60), 12)
            pygame.draw.circle(s, (200, 180, 220), (60, 60), 8)
            pygame.draw.circle(s, (80, 60, 100), (60, 60), 4)
    
    elif pid == "pandemic":
        # ========== Pandemic - 末日瘟神·零号 ==========
        # 生化瘟疫美学，病毒+细菌+毒雾，毒绿与腐紫配色
        toxic_green = (80, 255, 80)
        decay_purple = (150, 80, 180)
        bio_yellow = (200, 200, 80)
        fog_color = (100, 180, 100)
        
        # 主体病毒球体
        pygame.draw.circle(s, decay_purple, (60, 60), 35)
        pygame.draw.circle(s, (100, 50, 130), (60, 60), 30)
        pygame.draw.circle(s, toxic_green, (60, 60), 35, 2)
        
        # 病毒刺突蛋白（16个）
        for spike_i in range(16):
            spike_angle = (spike_i * 22.5 + t * 20) * 0.01745
            spike_base_r = 32
            spike_tip_r = 42 + int(3 * math.sin(t * 5 + spike_i))
            spike_bx = 60 + math.cos(spike_angle) * spike_base_r
            spike_by = 60 + math.sin(spike_angle) * spike_base_r
            spike_tx = 60 + math.cos(spike_angle) * spike_tip_r
            spike_ty = 60 + math.sin(spike_angle) * spike_tip_r
            # 刺突杆
            pygame.draw.line(s, toxic_green, (int(spike_bx), int(spike_by)), 
                           (int(spike_tx), int(spike_ty)), 2)
            # 刺突头（球形）
            pygame.draw.circle(s, bio_yellow, (int(spike_tx), int(spike_ty)), 4)
            pygame.draw.circle(s, toxic_green, (int(spike_tx), int(spike_ty)), 4, 1)
        
        # 内部DNA/RNA螺旋
        for helix_i in range(24):
            helix_progress = helix_i / 24
            helix_angle = (helix_progress * 720 + t * 60) * 0.01745
            helix_r = 18
            helix_offset = 8 * math.sin(helix_progress * math.pi * 4)
            # 双螺旋
            hx1 = 60 + math.cos(helix_angle) * (helix_r + helix_offset) * 0.5
            hy1 = 60 + helix_progress * 40 - 20
            hx2 = 60 + math.cos(helix_angle + math.pi) * (helix_r + helix_offset) * 0.5
            hy2 = hy1
            if 35 < hy1 < 85:  # 只在球体内部绘制
                pygame.draw.circle(s, toxic_green, (int(hx1), int(hy1)), 2)
                pygame.draw.circle(s, bio_yellow, (int(hx2), int(hy2)), 2)
                # 碱基对连接
                if helix_i % 3 == 0:
                    pygame.draw.line(s, (150, 200, 150), (int(hx1), int(hy1)), 
                                   (int(hx2), int(hy2)), 1)
        
        # 毒雾粒子扩散（20个）
        for fog_i in range(20):
            fog_phase = ((t * 2 + fog_i * 0.15) % 1.0)
            fog_angle = (fog_i * 18 + t * 8) * 0.01745
            fog_r = 35 + fog_phase * 25
            fog_x = 60 + math.cos(fog_angle) * fog_r
            fog_y = 60 + math.sin(fog_angle) * fog_r
            fog_alpha = int(150 * (1 - fog_phase))
            fog_size = int(6 * (1 - fog_phase * 0.5))
            if fog_alpha > 0:
                fog_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(fog_surf, (*fog_color, fog_alpha), 
                                 (int(fog_x), int(fog_y)), fog_size)
                s.blit(fog_surf, (0, 0))
        
        # 感染标记（生物危害符号）
        bio_r = 12
        for bio_i in range(3):
            bio_angle = (bio_i * 120 + 30) * 0.01745
            bx = 60 + math.cos(bio_angle) * bio_r
            by = 60 + math.sin(bio_angle) * bio_r
            # 扇形
            arc_start = bio_angle - 0.4
            arc_end = bio_angle + 0.4
            arc_points = [(60, 60)]
            for arc_seg in range(8):
                arc_a = arc_start + (arc_end - arc_start) * arc_seg / 7
                ax = 60 + math.cos(arc_a) * 20
                ay = 60 + math.sin(arc_a) * 20
                arc_points.append((int(ax), int(ay)))
            if len(arc_points) > 2:
                pygame.draw.polygon(s, toxic_green, arc_points)
        pygame.draw.circle(s, (100, 50, 130), (60, 60), 8)
        
        # 变异闪烁效果
        mutation_pulse = abs(math.sin(t * 4))
        if mutation_pulse > 0.8:
            pulse_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pulse_alpha = int((mutation_pulse - 0.8) * 5 * 200)
            pygame.draw.circle(pulse_surf, (*toxic_green, pulse_alpha), (60, 60), 40)
            s.blit(pulse_surf, (0, 0))
        
        # ========== Pandemic 专属涂装 ==========
        if model_style == "pandemic_plague":
            # 黑死病·乌鸦医生 - 中世纪瘟疫医生，鸟嘴面具
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 黑暗雾气背景
            for fog in range(15):
                fog_x = random.randint(10, 110)
                fog_y = random.randint(10, 110)
                fog_alpha = random.randint(30, 80)
                fog_size = random.randint(10, 25)
                pygame.draw.circle(s, (30, 30, 35, fog_alpha), (fog_x, fog_y), fog_size)
            # 瘟疫医生剪影
            # 宽檐帽
            hat_points = [(30, 35), (60, 20), (90, 35), (85, 40), (35, 40)]
            pygame.draw.polygon(s, (20, 20, 25), hat_points)
            # 鸟嘴面具
            beak_sway = math.sin(t * 2) * 2
            pygame.draw.ellipse(s, (40, 35, 30), (45, 38, 30, 25))  # 头部
            # 长鸟嘴
            beak_points = [(75, 48), (105 + int(beak_sway), 55), (75, 58)]
            pygame.draw.polygon(s, (50, 45, 40), beak_points)
            # 圆形眼镜（红色反光）
            eye_glow = int(150 + 80 * math.sin(t * 4))
            pygame.draw.circle(s, (30, 25, 25), (52, 45), 7)
            pygame.draw.circle(s, (eye_glow, 30, 30), (52, 45), 5)
            pygame.draw.circle(s, (30, 25, 25), (66, 45), 7)
            pygame.draw.circle(s, (eye_glow, 30, 30), (66, 45), 5)
            # 长袍身体
            robe_points = [(40, 60), (80, 60), (90, 110), (30, 110)]
            pygame.draw.polygon(s, (25, 25, 30), robe_points)
            # 手持香炉（摇摆）
            censer_x = 85 + math.sin(t * 3) * 5
            censer_y = 75
            pygame.draw.circle(s, (80, 60, 40), (int(censer_x), censer_y), 6)
            pygame.draw.line(s, (60, 50, 35), (int(censer_x), censer_y - 6), (int(censer_x), censer_y - 20), 2)
            # 香炉烟雾
            for smoke in range(8):
                smoke_phase = ((t * 2 + smoke * 0.2) % 1.0)
                smoke_x = censer_x + math.sin(t * 4 + smoke) * 5
                smoke_y = censer_y - 20 - smoke_phase * 30
                smoke_alpha = int(150 * (1 - smoke_phase))
                if smoke_alpha > 0:
                    smoke_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.circle(smoke_surf, (60, 60, 65, smoke_alpha), (int(smoke_x), int(smoke_y)), int(4 + smoke_phase * 5))
                    s.blit(smoke_surf, (0, 0))
            # 飘落的乌鸦羽毛
            for feather in range(4):
                feather_phase = ((t * 0.5 + feather * 0.3) % 1.0)
                feather_x = 20 + feather * 25 + math.sin(t + feather) * 10
                feather_y = feather_phase * 100 + 10
                feather_alpha = int(180 * (1 - feather_phase))
                if feather_alpha > 0:
                    pygame.draw.ellipse(s, (20, 20, 25, feather_alpha), (int(feather_x) - 2, int(feather_y) - 5, 4, 10))
        
        elif model_style == "pandemic_biohazard":
            # 生化危机·橙色警报 - 生化危害标志，隔离区
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 警示条纹背景
            for stripe in range(12):
                stripe_y = stripe * 10
                stripe_color = (255, 150, 0) if stripe % 2 == 0 else (40, 40, 40)
                pygame.draw.rect(s, stripe_color, (10, stripe_y, 100, 10))
            # 生化危害符号（大型旋转）
            bio_rot = t * 30
            bio_cx, bio_cy = 60, 60
            # 中心圆
            pygame.draw.circle(s, (40, 40, 40), (bio_cx, bio_cy), 12)
            pygame.draw.circle(s, (255, 150, 0), (bio_cx, bio_cy), 12, 3)
            # 三片扇叶
            for blade in range(3):
                blade_angle = (blade * 120 + bio_rot) * 0.01745
                # 扇形主体
                arc_points = [(bio_cx, bio_cy)]
                for arc_seg in range(10):
                    arc_a = blade_angle - 0.4 + arc_seg * 0.08
                    arc_r = 40
                    ax = bio_cx + math.cos(arc_a) * arc_r
                    ay = bio_cy + math.sin(arc_a) * arc_r
                    arc_points.append((int(ax), int(ay)))
                pygame.draw.polygon(s, (255, 150, 0), arc_points)
                # 内切口
                cut_angle = blade_angle
                cut_points = [(bio_cx, bio_cy)]
                for cut_seg in range(6):
                    cut_a = cut_angle - 0.2 + cut_seg * 0.07
                    cut_r = 25
                    cx = bio_cx + math.cos(cut_a) * cut_r
                    cy = bio_cy + math.sin(cut_a) * cut_r
                    cut_points.append((int(cx), int(cy)))
                pygame.draw.polygon(s, (40, 40, 40), cut_points)
            # 警告闪烁效果
            if int(t * 4) % 2 == 0:
                flash_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(flash_surf, (255, 200, 100, 80), (60, 60), 55)
                s.blit(flash_surf, (0, 0))
            # 隔离带粒子
            for tape in range(6):
                tape_angle = (tape * 60 + t * 40) * 0.01745
                tape_r = 52
                tape_x = 60 + math.cos(tape_angle) * tape_r
                tape_y = 60 + math.sin(tape_angle) * tape_r
                pygame.draw.rect(s, (255, 200, 0), (int(tape_x) - 8, int(tape_y) - 2, 16, 4))
                pygame.draw.rect(s, (40, 40, 40), (int(tape_x) - 8, int(tape_y) - 2, 16, 4), 1)
        
        elif model_style == "pandemic_fungal":
            # 真菌帝国·孢子君主 - 恐怖真菌感染，蘑菇群落
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 腐败有机物背景
            for decay in range(20):
                decay_x = random.randint(15, 105)
                decay_y = random.randint(15, 105)
                decay_color = (80 + random.randint(0, 40), 60 + random.randint(0, 30), 50 + random.randint(0, 20))
                pygame.draw.circle(s, decay_color, (decay_x, decay_y), random.randint(3, 8))
            # 中央巨型蘑菇
            # 菌柄
            pygame.draw.rect(s, (180, 150, 120), (52, 60, 16, 40))
            pygame.draw.rect(s, (150, 120, 90), (52, 60, 16, 40), 2)
            # 菌盖（脉动）
            cap_pulse = abs(math.sin(t * 3))
            cap_width = int(40 + cap_pulse * 8)
            cap_height = int(25 + cap_pulse * 5)
            pygame.draw.ellipse(s, (150, 80, 60), (60 - cap_width//2, 35, cap_width, cap_height))
            # 菌盖斑点
            for spot in range(8):
                spot_angle = (spot * 45 + t * 10) * 0.01745
                spot_r = 12 + spot % 3 * 3
                spot_x = 60 + math.cos(spot_angle) * spot_r
                spot_y = 47 + math.sin(spot_angle) * (spot_r * 0.4)
                pygame.draw.circle(s, (200, 150, 100), (int(spot_x), int(spot_y)), 3)
            # 周围小蘑菇群落
            small_mushrooms = [(25, 80, 8), (40, 90, 6), (80, 85, 7), (95, 75, 5), (30, 70, 5), (90, 95, 6)]
            for mx, my, msize in small_mushrooms:
                grow_phase = abs(math.sin(t * 2 + mx * 0.1))
                # 小菌柄
                pygame.draw.rect(s, (160, 130, 100), (mx - 2, my, 4, msize + 5))
                # 小菌盖
                pygame.draw.ellipse(s, (130, 70, 50), (mx - msize, my - msize//2, msize * 2, msize))
            # 孢子云扩散
            for spore in range(25):
                spore_phase = ((t * 1.5 + spore * 0.1) % 1.0)
                spore_angle = (spore * 14.4 + t * 20) * 0.01745
                spore_r = 20 + spore_phase * 40
                spore_x = 60 + math.cos(spore_angle) * spore_r
                spore_y = 50 + math.sin(spore_angle) * spore_r * 0.7
                spore_alpha = int(200 * (1 - spore_phase))
                spore_size = int(3 * (1 - spore_phase * 0.5))
                if spore_alpha > 0:
                    spore_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.circle(spore_surf, (180, 150, 100, spore_alpha), (int(spore_x), int(spore_y)), spore_size)
                    s.blit(spore_surf, (0, 0))
        
        elif model_style == "pandemic_neon_virus":
            # 赛博瘟疫·数据病毒 - 数字病毒，荧光绿代码
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 黑色数字背景
            pygame.draw.rect(s, (10, 15, 10), (10, 10, 100, 100))
            # 矩阵代码雨
            for col in range(10):
                col_x = 15 + col * 10
                col_speed = 1 + (col % 3) * 0.5
                for row in range(12):
                    char_y = ((t * 30 * col_speed + row * 10 + col * 7) % 100) + 10
                    char_alpha = int(255 * (1 - (char_y - 10) / 100))
                    if char_alpha > 0:
                        # 绿色方块代表代码字符
                        pygame.draw.rect(s, (0, char_alpha, 0, char_alpha), (col_x, int(char_y), 6, 8))
            # 中央病毒实体（多边形赛博风格）
            virus_rot = t * 40
            virus_cx, virus_cy = 60, 60
            # 外层六边形
            outer_points = []
            for i in range(6):
                angle = (i * 60 + virus_rot) * 0.01745
                ox = virus_cx + math.cos(angle) * 30
                oy = virus_cy + math.sin(angle) * 30
                outer_points.append((int(ox), int(oy)))
            pygame.draw.polygon(s, (0, 80, 0), outer_points)
            pygame.draw.polygon(s, (0, 255, 100), outer_points, 2)
            # 内层三角形（反向旋转）
            inner_points = []
            for i in range(3):
                angle = (i * 120 - virus_rot * 2) * 0.01745
                ix = virus_cx + math.cos(angle) * 15
                iy = virus_cy + math.sin(angle) * 15
                inner_points.append((int(ix), int(iy)))
            pygame.draw.polygon(s, (0, 150, 50), inner_points)
            pygame.draw.polygon(s, (0, 255, 100), inner_points, 2)
            # 连接线（数据流）
            for i in range(6):
                pygame.draw.line(s, (0, 200, 80), outer_points[i], inner_points[i % 3], 1)
            # 核心发光
            glow_pulse = abs(math.sin(t * 5))
            glow_size = int(8 + glow_pulse * 4)
            pygame.draw.circle(s, (0, 255, 100), (virus_cx, virus_cy), glow_size)
            pygame.draw.circle(s, (200, 255, 200), (virus_cx, virus_cy), glow_size - 3)
            # 扫描线效果
            scan_y = int((t * 50) % 100) + 10
            pygame.draw.line(s, (0, 255, 100, 150), (10, scan_y), (110, scan_y), 1)
        
        elif model_style == "pandemic_zombie":
            # 丧尸末日·腐烂觉醒 - 腐烂丧尸，活死人
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 血渍背景
            for blood in range(15):
                blood_x = random.randint(15, 105)
                blood_y = random.randint(15, 105)
                blood_size = random.randint(5, 15)
                pygame.draw.circle(s, (80, 20, 20), (blood_x, blood_y), blood_size)
            # 丧尸头部
            head_sway = math.sin(t * 1.5) * 3
            head_cx = 60 + head_sway
            # 腐烂皮肤
            pygame.draw.ellipse(s, (90, 120, 70), (int(head_cx) - 18, 25, 36, 40))
            # 腐烂斑块
            rot_spots = [(head_cx - 8, 35), (head_cx + 10, 40), (head_cx - 5, 50), (head_cx + 8, 55)]
            for rx, ry in rot_spots:
                pygame.draw.circle(s, (60, 80, 50), (int(rx), int(ry)), random.randint(3, 6))
            # 空洞眼睛（一只正常一只缺失）
            pygame.draw.circle(s, (20, 20, 20), (int(head_cx) - 7, 38), 6)
            pygame.draw.circle(s, (200, 200, 50), (int(head_cx) - 7, 38), 3)  # 发光眼
            pygame.draw.ellipse(s, (40, 30, 30), (int(head_cx) + 2, 35, 10, 8))  # 缺失眼窝
            # 露出的牙齿
            for tooth in range(5):
                tooth_x = head_cx - 8 + tooth * 4
                tooth_h = 3 + random.randint(0, 3)
                pygame.draw.rect(s, (200, 200, 180), (int(tooth_x), 55, 3, tooth_h))
            # 撕裂的身体
            body_points = [(int(head_cx) - 15, 65), (int(head_cx) + 15, 65), 
                          (int(head_cx) + 20, 100), (int(head_cx) - 20, 100)]
            pygame.draw.polygon(s, (70, 100, 60), body_points)
            # 露出的肋骨
            for rib in range(4):
                rib_y = 72 + rib * 7
                pygame.draw.arc(s, (200, 190, 170), (int(head_cx) - 12, rib_y, 24, 8), 0, 3.14159, 2)
            # 伸出的手臂（抖动）
            arm_shake = math.sin(t * 8) * 3
            pygame.draw.line(s, (80, 110, 65), (int(head_cx) + 15, 75), (int(head_cx) + 40 + arm_shake, 60), 5)
            # 手指（弯曲）
            for finger in range(4):
                f_angle = (-0.5 + finger * 0.3 + math.sin(t * 4 + finger) * 0.2)
                fx = head_cx + 40 + arm_shake + math.cos(f_angle) * 8
                fy = 60 + math.sin(f_angle) * 8
                pygame.draw.line(s, (70, 100, 55), (int(head_cx) + 40 + arm_shake, 60), (int(fx), int(fy)), 2)
        
        elif model_style == "pandemic_parasite":
            # 寄生虫潮·蠕虫之母 - 恐怖寄生虫群，蠕动触须
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 有机物背景
            pygame.draw.circle(s, (120, 80, 90), (60, 60), 50)
            pygame.draw.circle(s, (100, 60, 70), (60, 60), 45)
            # 中央宿主（肿胀）
            host_pulse = abs(math.sin(t * 2))
            host_size = int(25 + host_pulse * 8)
            pygame.draw.circle(s, (150, 100, 110), (60, 60), host_size)
            pygame.draw.circle(s, (180, 120, 130), (60, 60), host_size - 5)
            # 内部可见的寄生虫轮廓
            for parasite in range(5):
                p_angle = (parasite * 72 + t * 20) * 0.01745
                p_r = 10 + math.sin(t * 3 + parasite) * 3
                px = 60 + math.cos(p_angle) * p_r
                py = 60 + math.sin(p_angle) * p_r
                pygame.draw.ellipse(s, (100, 60, 70), (int(px) - 4, int(py) - 2, 8, 4))
            # 蠕动的触须/蠕虫（从宿主伸出）
            for worm in range(8):
                worm_angle = (worm * 45) * 0.01745
                worm_points = [(60, 60)]
                for seg in range(8):
                    seg_r = host_size + seg * 5
                    seg_angle = worm_angle + math.sin(t * 4 + seg * 0.5 + worm) * 0.3
                    wx = 60 + math.cos(seg_angle) * seg_r
                    wy = 60 + math.sin(seg_angle) * seg_r
                    worm_points.append((int(wx), int(wy)))
                # 渐变粗细的蠕虫
                for i in range(len(worm_points) - 1):
                    width = max(1, 5 - i // 2)
                    pygame.draw.line(s, (180, 100, 120), worm_points[i], worm_points[i + 1], width)
                # 蠕虫头部
                if len(worm_points) > 1:
                    head_x, head_y = worm_points[-1]
                    pygame.draw.circle(s, (200, 120, 140), (head_x, head_y), 3)
            # 脱落的虫卵
            for egg in range(10):
                egg_phase = ((t * 0.8 + egg * 0.15) % 1.0)
                egg_angle = (egg * 36 + t * 15) * 0.01745
                egg_r = 50 + egg_phase * 15
                egg_x = 60 + math.cos(egg_angle) * egg_r
                egg_y = 60 + math.sin(egg_angle) * egg_r
                egg_alpha = int(200 * (1 - egg_phase))
                if egg_alpha > 0:
                    egg_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.ellipse(egg_surf, (200, 150, 160, egg_alpha), (int(egg_x) - 3, int(egg_y) - 2, 6, 4))
                    s.blit(egg_surf, (0, 0))
        
        elif model_style == "pandemic_radiation":
            # 核辐射·切尔诺贝利 - 核辐射符号，变异生物
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 辐射光芒背景
            for ray in range(12):
                ray_angle = (ray * 30 + t * 10) * 0.01745
                ray_color = (255, 255, 0, 100) if ray % 2 == 0 else (40, 40, 40, 100)
                ray_points = [(60, 60)]
                r1_x = 60 + math.cos(ray_angle - 0.13) * 60
                r1_y = 60 + math.sin(ray_angle - 0.13) * 60
                r2_x = 60 + math.cos(ray_angle + 0.13) * 60
                r2_y = 60 + math.sin(ray_angle + 0.13) * 60
                ray_points.extend([(int(r1_x), int(r1_y)), (int(r2_x), int(r2_y))])
                ray_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.polygon(ray_surf, ray_color, ray_points)
                s.blit(ray_surf, (0, 0))
            # 核辐射三叶符号
            rad_rot = t * 20
            # 中心圆
            pygame.draw.circle(s, (40, 40, 40), (60, 60), 10)
            pygame.draw.circle(s, (255, 255, 0), (60, 60), 10, 2)
            # 三片扇叶
            for leaf in range(3):
                leaf_angle = (leaf * 120 + rad_rot) * 0.01745
                # 扇叶
                leaf_points = []
                for seg in range(-3, 4):
                    seg_angle = leaf_angle + seg * 0.12
                    seg_r = 35
                    lx = 60 + math.cos(seg_angle) * seg_r
                    ly = 60 + math.sin(seg_angle) * seg_r
                    leaf_points.append((int(lx), int(ly)))
                leaf_points.append((60, 60))
                pygame.draw.polygon(s, (255, 255, 0), leaf_points)
            # 变异生物剪影（扭曲的动物）
            mutant_x = 60 + math.sin(t * 2) * 5
            mutant_y = 85
            # 变异体主体
            pygame.draw.ellipse(s, (80, 100, 60), (int(mutant_x) - 10, mutant_y - 5, 20, 12))
            # 多余的肢体
            for limb in range(5):
                limb_angle = (limb * 50 + t * 30) * 0.01745
                limb_x = mutant_x + math.cos(limb_angle) * 12
                limb_y = mutant_y + math.sin(limb_angle) * 8
                pygame.draw.line(s, (70, 90, 50), (int(mutant_x), mutant_y), (int(limb_x), int(limb_y)), 2)
            # 盖革计数器粒子
            for particle in range(15):
                particle_phase = ((t * 3 + particle * 0.1) % 1.0)
                particle_angle = random.random() * 6.28
                particle_r = particle_phase * 60
                particle_x = 60 + math.cos(particle_angle) * particle_r
                particle_y = 60 + math.sin(particle_angle) * particle_r
                particle_alpha = int(255 * (1 - particle_phase))
                if particle_alpha > 0:
                    pygame.draw.circle(s, (255, 255, 0, particle_alpha), (int(particle_x), int(particle_y)), 2)
        
        elif model_style == "pandemic_coral":
            # 珊瑚瘟疫·深海异变 - 荧光珊瑚病变
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 深海背景
            pygame.draw.rect(s, (10, 30, 50), (10, 10, 100, 100))
            # 水中光线
            for beam in range(5):
                beam_x = 20 + beam * 20
                beam_alpha = int(30 + 20 * math.sin(t * 2 + beam))
                beam_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                beam_points = [(beam_x, 10), (beam_x + 10, 10), (beam_x + 15, 110), (beam_x - 5, 110)]
                pygame.draw.polygon(beam_surf, (100, 150, 200, beam_alpha), beam_points)
                s.blit(beam_surf, (0, 0))
            # 中央病变珊瑚（荧光色）
            coral_colors = [(255, 100, 150), (100, 255, 200), (255, 200, 100), (200, 100, 255)]
            # 主珊瑚分支
            for branch in range(6):
                branch_angle = (branch * 60 + 15) * 0.01745
                branch_sway = math.sin(t * 1.5 + branch) * 3
                branch_color = coral_colors[branch % 4]
                # 分支路径
                branch_points = [(60, 70)]
                for seg in range(5):
                    seg_angle = branch_angle + math.sin(t * 2 + seg) * 0.2
                    seg_r = 10 + seg * 8
                    bx = 60 + math.cos(seg_angle) * seg_r + branch_sway
                    by = 70 - seg * 8
                    branch_points.append((int(bx), int(by)))
                # 绘制分支
                for i in range(len(branch_points) - 1):
                    width = 5 - i
                    pygame.draw.line(s, branch_color, branch_points[i], branch_points[i + 1], max(1, width))
                # 分支末端球体（息肉）
                end_x, end_y = branch_points[-1]
                polyp_pulse = abs(math.sin(t * 4 + branch))
                polyp_size = int(4 + polyp_pulse * 3)
                pygame.draw.circle(s, branch_color, (end_x, end_y), polyp_size)
                # 发光效果
                glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*branch_color, 100), (end_x, end_y), polyp_size + 5)
                s.blit(glow_surf, (0, 0))
            # 飘浮的病变碎片
            for debris in range(8):
                debris_phase = ((t * 0.5 + debris * 0.2) % 1.0)
                debris_x = 20 + debris * 12 + math.sin(t + debris) * 5
                debris_y = 100 - debris_phase * 80
                debris_color = coral_colors[debris % 4]
                debris_alpha = int(200 * (1 - abs(debris_phase - 0.5) * 2))
                if debris_alpha > 0:
                    pygame.draw.circle(s, (*debris_color, debris_alpha), (int(debris_x), int(debris_y)), 3)
        
        elif model_style == "pandemic_prion":
            # 朊病毒·疯牛噩梦 - 大脑海绵状病变
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 大脑背景（粉色）
            pygame.draw.ellipse(s, (220, 180, 190), (20, 25, 80, 70))
            # 大脑沟回
            brain_folds = [
                [(30, 40), (40, 35), (50, 40), (45, 50)],
                [(55, 35), (70, 30), (80, 40), (70, 50)],
                [(35, 55), (50, 50), (60, 60), (45, 70)],
                [(65, 55), (80, 50), (85, 65), (70, 70)]
            ]
            for fold in brain_folds:
                pygame.draw.lines(s, (200, 150, 160), False, fold, 2)
            # 海绵状空洞（prion 造成）
            holes = [(35, 45, 5), (55, 40, 6), (75, 45, 4), (45, 60, 7), (65, 55, 5), (50, 75, 4)]
            for hx, hy, hr in holes:
                hole_pulse = abs(math.sin(t * 3 + hx * 0.1))
                hole_r = hr + int(hole_pulse * 2)
                pygame.draw.circle(s, (40, 30, 35), (hx, hy), hole_r)
                pygame.draw.circle(s, (80, 60, 70), (hx, hy), hole_r, 1)
            # 扭曲的蛋白质链（动态蠕动）
            for chain in range(6):
                chain_start_angle = (chain * 60 + t * 30) * 0.01745
                chain_points = []
                for seg in range(10):
                    seg_angle = chain_start_angle + seg * 0.5 + math.sin(t * 5 + seg) * 0.3
                    seg_r = 5 + seg * 4
                    cx = 60 + math.cos(seg_angle) * seg_r
                    cy = 55 + math.sin(seg_angle) * seg_r * 0.6
                    chain_points.append((int(cx), int(cy)))
                if len(chain_points) > 1:
                    pygame.draw.lines(s, (255, 200, 100), False, chain_points, 2)
                    # 蛋白质折叠节点
                    for point in chain_points[::2]:
                        pygame.draw.circle(s, (255, 220, 150), point, 2)
            # 神经信号干扰（闪烁）
            if random.random() > 0.7:
                glitch_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                glitch_x = random.randint(25, 95)
                glitch_y = random.randint(30, 85)
                pygame.draw.circle(glitch_surf, (255, 255, 255, 150), (glitch_x, glitch_y), 8)
                s.blit(glitch_surf, (0, 0))
        
        elif model_style == "pandemic_alien":
            # 外星瘟疫·仙女座病毒 - 来自星际的未知病原体
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 外星星空背景
            for star in range(40):
                star_x = random.randint(5, 115)
                star_y = random.randint(5, 115)
                star_bright = int(100 + 155 * random.random())
                pygame.draw.circle(s, (star_bright, star_bright, star_bright), (star_x, star_y), 1)
            # 外星病毒（奇异几何形态）
            alien_rot = t * 25
            alien_cx, alien_cy = 60, 60
            # 四面体核心
            tetra_points = []
            for i in range(4):
                if i < 3:
                    angle = (i * 120 + alien_rot) * 0.01745
                    tx = alien_cx + math.cos(angle) * 25
                    ty = alien_cy + math.sin(angle) * 25
                else:
                    tx, ty = alien_cx, alien_cy - 30
                tetra_points.append((int(tx), int(ty)))
            # 绘制四面体边
            pygame.draw.line(s, (100, 255, 200), tetra_points[0], tetra_points[1], 2)
            pygame.draw.line(s, (100, 255, 200), tetra_points[1], tetra_points[2], 2)
            pygame.draw.line(s, (100, 255, 200), tetra_points[2], tetra_points[0], 2)
            pygame.draw.line(s, (80, 200, 160), tetra_points[0], tetra_points[3], 2)
            pygame.draw.line(s, (80, 200, 160), tetra_points[1], tetra_points[3], 2)
            pygame.draw.line(s, (80, 200, 160), tetra_points[2], tetra_points[3], 2)
            # 外星触须（非欧几里得弯曲）
            for tendril in range(8):
                tendril_angle = (tendril * 45 + t * 20) * 0.01745
                tendril_points = [(alien_cx, alien_cy)]
                for seg in range(8):
                    seg_r = 25 + seg * 5
                    # 非欧几里得弯曲
                    seg_curve = math.sin(t * 3 + seg * 0.8 + tendril) * 0.5
                    seg_angle = tendril_angle + seg_curve
                    tx = alien_cx + math.cos(seg_angle) * seg_r
                    ty = alien_cy + math.sin(seg_angle) * seg_r
                    tendril_points.append((int(tx), int(ty)))
                tendril_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                tendril_alpha = int(200 - tendril * 10)
                pygame.draw.lines(tendril_surf, (100, 255, 200, tendril_alpha), False, tendril_points, 2)
                s.blit(tendril_surf, (0, 0))
            # 核心脉动
            core_pulse = abs(math.sin(t * 4))
            core_size = int(10 + core_pulse * 5)
            pygame.draw.circle(s, (150, 255, 220), (alien_cx, alien_cy), core_size)
            pygame.draw.circle(s, (200, 255, 240), (alien_cx, alien_cy), core_size - 3)
        
        elif model_style == "pandemic_chimera":
            # 嵌合瘟疫·基因拼接 - 人造超级病原体，DNA拼接
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 实验室蓝色背景
            pygame.draw.rect(s, (20, 30, 50), (10, 10, 100, 100))
            # DNA双螺旋（多色拼接）
            helix_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
            for strand in range(2):
                strand_offset = strand * 3.14159
                strand_points = []
                for seg in range(20):
                    seg_t = seg / 20
                    seg_y = 15 + seg * 5
                    seg_x = 60 + math.sin(seg_t * 6.28 + t * 3 + strand_offset) * 20
                    strand_points.append((int(seg_x), seg_y))
                    # 拼接色块
                    color_idx = seg // 5
                    pygame.draw.circle(s, helix_colors[color_idx % 4], (int(seg_x), seg_y), 4)
                # 连接线
                if strand == 0:
                    for seg in range(0, 20, 2):
                        seg_t = seg / 20
                        seg_y = 15 + seg * 5
                        seg_x1 = 60 + math.sin(seg_t * 6.28 + t * 3) * 20
                        seg_x2 = 60 + math.sin(seg_t * 6.28 + t * 3 + 3.14159) * 20
                        pygame.draw.line(s, (150, 150, 150), (int(seg_x1), seg_y), (int(seg_x2), seg_y), 1)
            # 基因编辑标记（CRISPR切口）
            for cut in range(3):
                cut_y = 30 + cut * 30
                cut_x = 60 + math.sin(t * 2 + cut) * 15
                # 剪刀符号
                pygame.draw.line(s, (255, 200, 100), (int(cut_x) - 8, cut_y - 5), (int(cut_x) + 8, cut_y + 5), 2)
                pygame.draw.line(s, (255, 200, 100), (int(cut_x) - 8, cut_y + 5), (int(cut_x) + 8, cut_y - 5), 2)
            # 嵌合病毒实体（多种病毒特征融合）
            chimera_x, chimera_y = 85, 90
            # 球形基底
            pygame.draw.circle(s, (200, 100, 255), (chimera_x, chimera_y), 15)
            # 不同病毒的刺突
            for spike in range(8):
                spike_angle = (spike * 45 + t * 30) * 0.01745
                spike_color = helix_colors[spike % 4]
                spike_len = 8 + (spike % 3) * 3
                sx = chimera_x + math.cos(spike_angle) * (15 + spike_len)
                sy = chimera_y + math.sin(spike_angle) * (15 + spike_len)
                pygame.draw.line(s, spike_color, (chimera_x + int(math.cos(spike_angle) * 15), 
                                                  chimera_y + int(math.sin(spike_angle) * 15)),
                               (int(sx), int(sy)), 2)
                pygame.draw.circle(s, spike_color, (int(sx), int(sy)), 3)
        
        elif model_style == "pandemic_omega":
            # 终末瘟疫·Ω灭绝株 - 人类终结病毒，黑色死亡
            s = pygame.Surface((120, 120), pygame.SRCALPHA)
            # 虚空黑暗背景
            for void in range(8):
                void_r = 60 - void * 6
                void_alpha = 50 + void * 20
                pygame.draw.circle(s, (void_alpha // 5, 0, 0, void_alpha), (60, 60), void_r)
            # Ω符号（巨大，旋转）
            omega_rot = t * 5
            omega_cx, omega_cy = 60, 55
            # Ω 主体（手绘近似）
            omega_points = []
            for i in range(20):
                i_t = i / 20
                omega_angle = (-0.5 + i_t * 4.14) + omega_rot * 0.01745
                omega_r = 30
                if i < 18:
                    ox = omega_cx + math.cos(omega_angle) * omega_r
                    oy = omega_cy + math.sin(omega_angle) * omega_r * 0.8
                    omega_points.append((int(ox), int(oy)))
            if len(omega_points) > 2:
                pygame.draw.lines(s, (150, 0, 0), False, omega_points, 5)
            # Ω 底部两脚
            pygame.draw.line(s, (150, 0, 0), (omega_cx - 25, omega_cy + 20), (omega_cx - 25, omega_cy + 35), 5)
            pygame.draw.line(s, (150, 0, 0), (omega_cx + 25, omega_cy + 20), (omega_cx + 25, omega_cy + 35), 5)
            # 死亡能量波（向外扩散）
            for wave in range(5):
                wave_phase = ((t * 1.5 + wave * 0.3) % 1.0)
                wave_r = int(20 + wave_phase * 45)
                wave_alpha = int(200 * (1 - wave_phase))
                if wave_alpha > 0:
                    wave_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
                    pygame.draw.circle(wave_surf, (100, 0, 0, wave_alpha), (60, 60), wave_r, 3)
                    s.blit(wave_surf, (0, 0))
            # 熄灭的生命火花（下坠）
            for spark in range(10):
                spark_phase = ((t * 0.8 + spark * 0.15) % 1.0)
                spark_x = 20 + spark * 10 + math.sin(t * 2 + spark) * 5
                spark_y = 10 + spark_phase * 100
                spark_alpha = int(255 * (1 - spark_phase))
                if spark_alpha > 0:
                    # 火花从亮变暗
                    spark_brightness = int(255 * (1 - spark_phase))
                    pygame.draw.circle(s, (spark_brightness, spark_brightness // 3, 0, spark_alpha), 
                                      (int(spark_x), int(spark_y)), 2)
            # 中心黑洞
            pygame.draw.circle(s, (0, 0, 0), (omega_cx, omega_cy), 12)
            pygame.draw.circle(s, (50, 0, 0), (omega_cx, omega_cy), 12, 2)
    
    return s


def get_boss_surf(type_name, color, visual=None):
    s = pygame.Surface((240, 240), pygame.SRCALPHA)
    
    # 辅助绘制函数 (闭包)
    def draw_carrier(): pygame.draw.polygon(s, (80, 0, 0), [(0, 60), (120, 180), (240, 60), (120, 0)]); pygame.draw.polygon(s, color, [(20, 60), (120, 160), (220, 60), (120, 20)], 3); pygame.draw.rect(s, color, (100, 60, 40, 40)); pygame.draw.rect(s, (50, 0, 0), (20, 20, 40, 80)); pygame.draw.rect(s, (50, 0, 0), (180, 20, 40, 80))
    def draw_fortress(): pygame.draw.rect(s, (50, 30, 0), (0, 0, 200, 200), border_radius=20); pygame.draw.rect(s, color, (20, 20, 160, 160), 5, border_radius=15); pygame.draw.circle(s, DARK_RED, (100, 100), 60); pygame.draw.circle(s, color, (100, 100), 40)
    def draw_assassin(): pygame.draw.polygon(s, (30, 0, 50), [(0, 0), (90, 120), (180, 0), (90, 40)]); pygame.draw.polygon(s, color, [(20, 10), (90, 100), (160, 10), (90, 50)], 3)
    def draw_seraphim():
        cx, cy = 110, 110; pygame.draw.circle(s, color, (cx, cy), 100, 4); pygame.draw.circle(s, WHITE, (cx, cy), 90, 2); pygame.draw.circle(s, WHITE, (cx, cy), 40); pygame.draw.circle(s, color, (cx, cy), 30)
        for i in range(0, 360, 60): rad = math.radians(i); end_x = cx + math.cos(rad) * 100; end_y = cy + math.sin(rad) * 100; pygame.draw.line(s, color, (cx, cy), (end_x, end_y), 5)
    def draw_leviathan():
        for i in range(5): y = 50 + i * 50; size = 60 - i * 8; pygame.draw.circle(s, color, (100, y), size); pygame.draw.circle(s, (50, 0, 80), (100, y), size-5)
        pygame.draw.polygon(s, color, [(50, 50), (150, 50), (100, 0)])
    def draw_overlord():
        pygame.draw.circle(s, (20, 20, 30), (100, 100), 90); pygame.draw.circle(s, color, (100, 100), 90, 4); pygame.draw.circle(s, RED, (100, 100), 30)
        for i in range(0, 360, 45): rad = math.radians(i); end_x = 100 + math.cos(rad) * 100; end_y = 100 + math.sin(rad) * 100; pygame.draw.line(s, GRAY, (100, 100), (end_x, end_y), 2)
    def draw_ragnarok(): pygame.draw.rect(s, color, (60, 40, 120, 100), border_radius=10); pygame.draw.rect(s, DARK_RED, (90, 70, 60, 40)); pygame.draw.line(s, RED, (90, 90), (150, 90), 2); pygame.draw.polygon(s, GRAY, [(40, 40), (60, 60), (60, 120), (40, 140)]); pygame.draw.polygon(s, GRAY, [(200, 40), (180, 60), (180, 120), (200, 140)])
    def draw_hydra():
        for i, offset in enumerate([-50, 0, 50]): mx, my = 120 + offset, 100 - abs(offset)//2; pygame.draw.circle(s, color, (mx, my), 30); pygame.draw.circle(s, LIME, (mx, my), 20); pygame.draw.line(s, (0, 100, 0), (120, 200), (mx, my+20), 10)
    def draw_chronos():
        pygame.draw.circle(s, color, (120, 120), 100, 2); pygame.draw.circle(s, color, (120, 120), 80, 1); pygame.draw.circle(s, WHITE, (120, 120), 10); pygame.draw.line(s, WHITE, (120, 120), (120, 50), 4); pygame.draw.line(s, WHITE, (120, 120), (180, 120), 3)
        for i in range(12): rad = math.radians(i * 30); sx = 120 + math.cos(rad) * 90; sy = 120 + math.sin(rad) * 90; pygame.draw.circle(s, color, (int(sx), int(sy)), 5)
    def draw_gazer():
        pygame.draw.circle(s, (50, 0, 0), (120, 120), 100); pygame.draw.circle(s, RED, (120, 120), 80, 2); pygame.draw.circle(s, BLACK, (120, 120), 40); pygame.draw.circle(s, RED, (120, 120), 15)
        for i in range(0, 360, 45): rad = math.radians(i); ex = 120 + math.cos(rad) * 110; ey = 120 + math.sin(rad) * 110; pygame.draw.line(s, (100, 0, 0), (120, 120), (ex, ey), 2)
    def draw_lich(): pygame.draw.polygon(s, (20, 0, 30), [(60, 180), (180, 180), (120, 40)]); pygame.draw.circle(s, GHOST_CYAN, (120, 80), 25); pygame.draw.circle(s, BLACK, (110, 75), 5); pygame.draw.circle(s, BLACK, (130, 75), 5); pygame.draw.rect(s, GHOST_CYAN, (40, 100, 20, 40), 1); pygame.draw.rect(s, GHOST_CYAN, (180, 100, 20, 40), 1)
    def draw_tempest():
        pygame.draw.circle(s, GRAY, (120, 120), 90, 5); pygame.draw.circle(s, WIND_BLUE, (120, 120), 20)
        for i in range(0, 360, 60): rad = math.radians(i); ex = 120 + math.cos(rad) * 90; ey = 120 + math.sin(rad) * 90; pygame.draw.line(s, WIND_BLUE, (120, 120), (ex, ey), 8)
    
    def draw_void_golem():
        # 虚空魔像：机械齿轮风格，紫色能量核心
        cx, cy = 120, 120
        # 外层齿轮轮廓
        pygame.draw.circle(s, color, (cx, cy), 90, 4)
        # 内层齿轮
        pygame.draw.circle(s, (60, 0, 100), (cx, cy), 70, 2)
        # 中央能量核心（脉动）
        core_size = 30 + int(10 * math.sin(pygame.time.get_ticks() / 300))
        pygame.draw.circle(s, (200, 100, 255), (cx, cy), core_size)
        pygame.draw.circle(s, (255, 150, 255), (cx, cy), core_size - 5)
        # 齿轮齿片（8个方向）
        for i in range(8):
            rad = math.radians(i * 45)
            # 外齿
            gx1 = cx + math.cos(rad) * 100
            gy1 = cy + math.sin(rad) * 100
            gx2 = cx + math.cos(rad + 0.3) * 90
            gy2 = cy + math.sin(rad + 0.3) * 90
            gx3 = cx + math.cos(rad - 0.3) * 90
            gy3 = cy + math.sin(rad - 0.3) * 90
            pygame.draw.polygon(s, color, [(int(gx1), int(gy1)), (int(gx2), int(gy2)), (int(gx3), int(gy3))])
        # 能量辐射线（4条）
        for i in range(0, 360, 90):
            rad = math.radians(i)
            ex = cx + math.cos(rad) * 110
            ey = cy + math.sin(rad) * 110
            pygame.draw.line(s, (150, 50, 200), (cx, cy), (int(ex), int(ey)), 3)
    
    def draw_abyss_queen():
        # 星渊女王：星体和王冠形状，紫蓝色
        cx, cy = 120, 120
        # 王冠顶部（三个尖角）
        crown_y = 50
        pygame.draw.polygon(s, color, [
            (cx - 40, crown_y + 20),
            (cx - 60, crown_y),
            (cx, crown_y - 30),
            (cx + 60, crown_y),
            (cx + 40, crown_y + 20)
        ])
        # 皇冠下的珍珠（3个）
        for offset in [-30, 0, 30]:
            pygame.draw.circle(s, (255, 200, 255), (cx + offset, crown_y + 35), 8)
        # 主体球形（星渊能量）
        pygame.draw.circle(s, (80, 40, 150), (cx, cy), 70, 2)
        pygame.draw.circle(s, color, (cx, cy), 65, 3)
        # 中央星体（脉动）
        star_size = 25 + int(8 * math.sin(pygame.time.get_ticks() / 250))
        pygame.draw.circle(s, (255, 200, 255), (cx, cy), star_size)
        # 环绕的小星体（5个）
        for i in range(5):
            rad = math.radians(i * 72 + pygame.time.get_ticks() / 50)
            sx = cx + math.cos(rad) * 85
            sy = cy + math.sin(rad) * 85
            pygame.draw.circle(s, (200, 100, 255), (int(sx), int(sy)), 6)
            # 星体光晕
            pygame.draw.circle(s, (150, 80, 200), (int(sx), int(sy)), 10, 1)
        # 底部触手轮廓（3根）
        for offset in [-30, 0, 30]:
            pygame.draw.line(s, (100, 50, 180), (cx + offset, cy + 70), (cx + offset, cy + 110), 4)
            # 触手节点
            for j in range(3):
                node_y = cy + 70 + j * 13
                pygame.draw.circle(s, color, (cx + offset, node_y), 4)

    if visual:
        # Add subtle aura if provided
        aura = visual.get('aura')
        if aura:
            aura_surf = pygame.Surface((260, 260), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (*aura, 40), (130, 130), 120)
            s.blit(aura_surf, (-10, -10), special_flags=pygame.BLEND_ADD)
    if type_name == "carrier": draw_carrier()
    elif type_name == "fortress": draw_fortress()
    elif type_name == "assassin": draw_assassin()
    elif type_name == "seraphim": draw_seraphim()
    elif type_name == "leviathan": draw_leviathan()
    elif type_name == "overlord": draw_overlord()
    elif type_name == "ragnarok":
        # Use procedural dreadnought renderer for higher fidelity boss appearance
        try:
            t = pygame.time.get_ticks() / 1000.0
            proc = procedural_dreadnought_surface(240, color, visual.get('core_color', color) if visual else color, t)
            s.blit(proc, (0, 0), special_flags=pygame.BLEND_ADD)
        except Exception:
            draw_ragnarok()
    elif type_name == "hydra": draw_hydra()
    elif type_name == "chronos": draw_chronos()
    elif type_name == "gazer": draw_gazer()
    elif type_name == "lich": draw_lich()
    elif type_name == "tempest": draw_tempest()
    elif type_name == "void_golem": draw_void_golem()
    elif type_name == "abyss_queen": draw_abyss_queen()
    return s


# ------------------------------------------------------------------------------
# Procedural rendering helpers (neon cyberpunk, vector-style)
# ------------------------------------------------------------------------------
def _bloom(surface, center, color, max_radius=60, layers=4):
    """Draw bloom by blitting expanding translucent circles."""
    cx, cy = center
    for i in range(layers, 0, -1):
        r = int(max_radius * (i / float(layers)))
        alpha = int(80 * (i / float(layers)))
        tmp = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(tmp, (*color[:3], alpha), (r, r), r)
        surface.blit(tmp, (cx - r, cy - r), special_flags=pygame.BLEND_ADD)


def procedural_interceptor_surface(size=80, neon=(0, 255, 200), accent=(255,255,255), t=None):
    """Generate an Interceptor (sharp/triangular) surface. """
    if t is None: t = pygame.time.get_ticks() / 1000.0
    s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    cx, cy = size, size
    # outline and base
    pts = [
        (cx, cy - int(size*0.9)),
        (cx + int(size*0.6), cy + int(size*0.4)),
        (cx, cy + int(size*0.2)),
        (cx - int(size*0.6), cy + int(size*0.4))
    ]
    # vertex breathing effect
    jitter = math.sin(t * 15) * 2
    pts = [(x + (jitter if i % 2 == 0 else -jitter), y) for i, (x, y) in enumerate(pts)]
    pygame.draw.polygon(s, (*neon[:3], 160), pts)
    pygame.draw.polygon(s, (*accent[:3], 255), pts, 2)
    # interior greebles (lines, vents, circuitry traces)
    for i in range(4):
        a = i / 4.0
        sx = cx + (pts[0][0] - cx) * (0.2 + a*0.6)
        sy = cy + (pts[0][1] - cy) * (0.2 + a*0.6)
        ex = sx + (random.random()-0.5) * 12
        ey = sy + (random.random()-0.5) * 12
        pygame.draw.line(s, (*accent[:3], 80), (sx, sy), (ex, ey), 1)
        # small vents (rectangles)
        vx = int(sx + (ex - sx) * 0.6)
        vy = int(sy + (ey - sy) * 0.6)
        pygame.draw.rect(s, (*neon[:3], 140), (vx-2, vy-1, 4, 2))
    # more circuitry/trace dots
    for g in range(6):
        rr = random.random()
        gx = cx + (random.random() - 0.5) * size * 0.5
        gy = cy + (random.random() - 0.5) * size * 0.25
        pygame.draw.circle(s, (*accent[:3], 120), (int(gx), int(gy)), 1)
    # engine vibrate thrusters
    thr_y = cy + int(size*0.4) + math.sin(t*30) * 3
    pygame.draw.circle(s, (*neon[:3], 230), (cx - int(size*0.22), thr_y), int(size*0.08))
    pygame.draw.circle(s, (*neon[:3], 200), (cx + int(size*0.22), thr_y), int(size*0.08))
    # internal greebles
    for g in range(6):
        angle = g * 60 + (t*30 % 360)
        ga = math.radians(angle)
        gx = cx + math.cos(ga) * (size*0.22)
        gy = cy + math.sin(ga) * (size*0.22)
        pygame.draw.circle(s, (*accent[:3], 120), (int(gx), int(gy)), 2)
    # glow
    _bloom(s, (cx, cy), neon, max_radius=int(size*0.8), layers=3)
    return s


def procedural_juggernaut_surface(size=80, color=(255,140,0), accent=(200,100,0), t=None):
    """Generate a Juggernaut (blocky, layered) surface."""
    if t is None: t = pygame.time.get_ticks() / 1000.0
    s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    cx, cy = size, size
    # core rectangle
    rect = pygame.Rect(cx - size*0.7//2, cy - size*0.5//2, int(size*1.4), int(size*1.0))
    pygame.draw.rect(s, (*color[:3], 220), rect, border_radius=8)
    # nested armor plates
    for i in range(3):
        inset = i * 8
        r = rect.inflate(-inset, -inset)
        pygame.draw.rect(s, (*accent[:3], 120), r, 2, border_radius=max(2, 8-i*2))
        # panel gaps: horizontal lines
        gap_y = r.top + 10 + i * 12
        pygame.draw.line(s, (50, 20, 0), (r.left + 6, gap_y), (r.right - 6, gap_y), 2)
    # rotating vents
    for i in range(3):
        ang = math.radians(i * 120 + t * 60)
        vx = cx + math.cos(ang) * int(size*0.8)
        vy = cy + math.sin(ang) * int(size*0.4)
        pygame.draw.circle(s, (*accent[:3], 230), (int(vx), int(vy)), int(size*0.12))
        pygame.draw.circle(s, (255, 200, 120), (int(vx), int(vy)), int(size*0.06))
    # greebles: bolts and rivets, panel gaps, diagonal seams
    for bx in range(rect.left+6, rect.right-6, 12):
        pygame.draw.circle(s, (50, 20, 0), (bx, rect.bottom-6), 2)
    # vertical panel gaps
    for x in range(rect.left + 12, rect.right - 12, 24):
        pygame.draw.line(s, (40, 15, 0), (x, rect.top + 6), (x, rect.bottom - 6), 1)
    # diagonal seam
    pygame.draw.line(s, (40, 20, 10), (rect.left+6, rect.top+6), (rect.right-6, rect.bottom-6), 1)
    pygame.draw.line(s, (40, 20, 10), (rect.left+6, rect.bottom-6), (rect.right-6, rect.top+6), 1)
    _bloom(s, (cx, cy), color, max_radius=int(size*0.6), layers=3)
    return s


def procedural_swarmer_surface(size=64, color=(150, 0, 255), accent=(255, 0, 200), t=None):
    """Generate a Swarmer (organic) surface with moving mandibles."""
    if t is None: t = pygame.time.get_ticks() / 1000.0
    s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    cx, cy = size, size
    # central orb
    pygame.draw.circle(s, (*color[:3], 230), (cx, cy), int(size*0.5))
    pygame.draw.circle(s, (*accent[:3], 200), (cx, cy), int(size*0.35))
    # mandibles - animated
    for i in range(3):
        a = i * 120
        ang = math.radians(a + math.sin(t * 6 + i) * 20)
        ox = cx + math.cos(ang) * int(size*0.7)
        oy = cy + math.sin(ang) * int(size*0.7)
        mx1 = cx + math.cos(ang) * int(size*0.35)
        my1 = cy + math.sin(ang) * int(size*0.35)
        pts = [(cx, cy), (mx1, my1), (ox, oy)]
        pygame.draw.polygon(s, (*accent[:3], 200), pts)
        # vein detail
        pygame.draw.line(s, (120, 0, 180), (cx + 2, cy), (int(mx1), int(my1)), 1)
    # internal small circles / greebles (veins and organic dots)
    for i in range(10):
        ang = math.radians(i * 36 + t * 40)
        r = 8 + (i % 2) * 5
        px = cx + math.cos(ang) * (int(size*0.25) + (i % 2) * 6)
        py = cy + math.sin(ang) * (int(size*0.25) + (i % 2) * 6)
        pygame.draw.circle(s, (*accent[:3], 120), (int(px), int(py)), int(r/8))
    # veins: sinuous curves around center
    for v in range(3):
        pts = []
        for k in range(-10, 11):
            x = cx + (k/11) * (size * 0.6)
            y = cy + math.sin((k + v*3) * 0.6 + t * 4) * 6 + (v-1) * 6
            pts.append((int(x), int(y)))
        pygame.draw.lines(s, (120, 0, 180, 120), False, pts, 1)
        # dots along the vein
        for p in pts[::4]:
            pygame.draw.circle(s, (*color[:3], 120), p, 1)
    _bloom(s, (cx, cy), color, max_radius=int(size*0.8), layers=3)
    return s


def procedural_dreadnought_surface(size=240, color=(200,0,50), accent=(255,120,120), t=None):
    """Large multi-part dreadnought boss with rotating core and turrets"""
    if t is None: t = pygame.time.get_ticks() / 1000.0
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size//2, size//2
    # Core mandala: concentric rings + rotated spokes
    for i in range(6):
        r = 20 + i * 18
        pygame.draw.circle(s, (*accent[:3], 40), (cx, cy), r, 2)
    # spokes (slowly rotate)
    angle_offset = (t * 10) % 360
    for i in range(0, 360, 30):
        ang = math.radians(i + angle_offset)
        ex = cx + math.cos(ang) * int(size*0.4)
        ey = cy + math.sin(ang) * int(size*0.4)
        pygame.draw.line(s, (*color[:3], 120), (cx, cy), (ex, ey), 3)
    # Turrets rotating around core
    turret_count = 8
    for i in range(turret_count):
        ang = math.radians(i * (360 / turret_count) + t * 45)
        tx = cx + math.cos(ang) * int(size*0.42)
        ty = cy + math.sin(ang) * int(size*0.42)
        pygame.draw.circle(s, (*color[:3], 200), (int(tx), int(ty)), 18)
        pygame.draw.circle(s, (*accent[:3], 255), (int(tx), int(ty)), 6)
    # Weak points pulsing
    for i in range(4):
        ang = math.radians(i * 90 + angle_offset)
        wx = cx + math.cos(ang) * int(size*0.25)
        wy = cy + math.sin(ang) * int(size*0.25)
        p = int(6 + 4 * (0.5 + 0.5 * math.sin(t * 6 + i)))
        pygame.draw.circle(s, (255, 50, 50, 220), (int(wx), int(wy)), p)
    _bloom(s, (cx, cy), color, max_radius=int(size*0.6), layers=4)
    return s

# ==============================================================================
#   实例化全局对象 (这是必须的！)
# ==============================================================================
# 防止导入时音频初始化失败
try:
    pygame.mixer.pre_init(44100, -16, 2, 1024)
    pygame.init()
    pygame.mixer.init()
except:
    pass

# 实例化 sound_mgr，供其他模块调用
sound_mgr = SoundManager()