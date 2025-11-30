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
        self.cache_dir = os.path.join(tempfile.gettempdir(), "neon_space_audio_v13")
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

    def generate_tone(self, freq, duration, vol=0.5, wave_type="sine"):
        n_samples = int(self.sample_rate * duration)
        data = []
        for i in range(n_samples):
            t = i / self.sample_rate
            v = 0
            if wave_type == "sine": v = math.sin(2 * math.pi * freq * t)
            elif wave_type == "square": v = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            elif wave_type == "saw": v = 2 * (t * freq - math.floor(t * freq + 0.5))
            elif wave_type == "noise": v = random.uniform(-1, 1)
            # Envelope
            if i < 100: v *= (i/100)
            if i > n_samples - 500: v *= ((n_samples - i)/500)
            data.append(v * vol)
        return data

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
                    if beat % 2 == 0: arp_note = freq * 4; val_arp = math.sin(2 * math.pi * arp_note * t_local) * 0.1 * math.exp(-t_local*8)
                    bgm_data.append((val_bass + val_drum + val_arp) * 0.5)
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
                    mix = (val_bass + val_drum + val_lead) * 0.7; mix = max(-0.9, min(0.9, mix))
                    boss_bgm_data.append(mix)
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
                    calm_bgm.append((val_melody + val_harmony + val_perc) * 0.6)
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
                    mystery_bgm.append((val_bass + val_high + val_echo) * 0.5)
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
                    epic_bgm.append((val_bass + val_drum + val_lead) * 0.75)
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
                    intense_bgm.append((val_saw + val_perc + val_stab) * 0.7)
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
                    cyber_bgm.append((val_bass + val_kick + val_arp) * 0.6)
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
                    ethereal_bgm.append((val_pad + val_shimmer) * 0.5)
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

def draw_text(surf, text, size, x, y, color=WHITE, align="center", shadow=True, glow=False):
    font = get_font(size, bold=True)
    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect()
    if align == "center": text_rect.midtop = (x, y)
    elif align == "left": text_rect.topleft = (x, y)
    elif align == "right": text_rect.topright = (x, y)
    
    if surf is None:
        log_debug("draw_text: surf is None, skipping draw")
        return pygame.Rect(x, y, 0, 0)
    if glow:
        glow_surf = font.render(str(text), True, (color[0]//2, color[1]//2, color[2]//2))
        surf.blit(glow_surf, (text_rect.x-1, text_rect.y))
        surf.blit(glow_surf, (text_rect.x+1, text_rect.y))
        surf.blit(glow_surf, (text_rect.x, text_rect.y-1))
        surf.blit(glow_surf, (text_rect.x, text_rect.y+1))
    elif shadow:
        shadow_surf = font.render(str(text), True, (0,0,0))
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

    # 赛博朋克风格几何飞机 - 13种机体差异化设计 + 动态特性
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