"""
音频系统模块 - 音频合成器和音效管理器
"""
import pygame
import random
import math
import os
import wave
import struct
import tempfile

from utils.core import log_error, log_info

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
        """生成所有音效和BGM"""
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

            # ===== BGM 生成 (简化版,完整版在原文件中) =====
            # BGM Normal
            bgm_data = self._generate_bgm_normal()
            paths["bgm_normal"] = self.save_wave("bgm_normal.wav", bgm_data)
            
            # BGM Boss
            boss_bgm_data = self._generate_bgm_boss()
            paths["bgm_boss"] = self.save_wave("bgm_boss.wav", boss_bgm_data)
            
            # BGM Calm
            calm_bgm = self._generate_bgm_calm()
            paths["bgm_calm"] = self.save_wave("bgm_calm.wav", calm_bgm)
            
            # BGM Mystery
            mystery_bgm = self._generate_bgm_mystery()
            paths["bgm_mystery"] = self.save_wave("bgm_mystery.wav", mystery_bgm)
            
            # BGM Epic
            epic_bgm = self._generate_bgm_epic()
            paths["bgm_epic"] = self.save_wave("bgm_epic.wav", epic_bgm)
            
            # BGM Intense
            intense_bgm = self._generate_bgm_intense()
            paths["bgm_intense"] = self.save_wave("bgm_intense.wav", intense_bgm)
            
            # BGM Cyber
            cyber_bgm = self._generate_bgm_cyber()
            paths["bgm_cyber"] = self.save_wave("bgm_cyber.wav", cyber_bgm)
            
            # BGM Ethereal
            ethereal_bgm = self._generate_bgm_ethereal()
            paths["bgm_ethereal"] = self.save_wave("bgm_ethereal.wav", ethereal_bgm)
            
            # 其他BGM使用简化方法生成
            for bgm_name in ["orchestra", "jazz", "piano", "rock", "ambient", "electronic", 
                            "chiptune", "tribal", "dubstep", "synthwave", "metal", "trance",
                            "orchestral_dark", "funk", "breakbeat", "lofi", "industrial", "cinematic"]:
                bgm_data = self._generate_generic_bgm(bgm_name)
                paths[f"bgm_{bgm_name}"] = self.save_wave(f"bgm_{bgm_name}.wav", bgm_data)

        except Exception as e:
            log_error(f"音频生成错误: {e}")
        return paths
    
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
    
    def _generate_generic_bgm(self, style):
        """生成通用风格BGM"""
        bgm_data = []
        bpm = 120; beat_dur = 60 / bpm; total_beats = 16
        
        # 根据风格调整参数
        style_params = {
            "orchestra": (100, 0.4, [220, 247, 277, 294]),
            "jazz": (110, 0.45, [262, 330, 392, 349]),
            "piano": (90, 0.5, [392, 440, 523, 587]),
            "rock": (160, 0.55, [82, 98, 110, 98]),
            "ambient": (60, 0.4, [110, 165, 220, 165]),
            "electronic": (130, 0.5, [65, 73, 82, 73]),
            "chiptune": (150, 0.45, [659, 784, 880, 784]),
            "tribal": (120, 0.55, [82, 82, 98, 82]),
            "dubstep": (140, 0.5, [65, 65, 73, 65]),
            "synthwave": (120, 0.5, [220, 247, 277, 293]),
            "metal": (180, 0.55, [82, 73, 82, 92]),
            "trance": (138, 0.5, [165, 185, 196, 220]),
            "orchestral_dark": (100, 0.48, [110, 117, 123, 131]),
            "funk": (115, 0.52, [82, 82, 98, 82]),
            "breakbeat": (150, 0.5, [65, 73, 82, 73]),
            "lofi": (85, 0.45, [220, 247, 196, 220]),
            "industrial": (130, 0.52, [55, 55, 65, 55]),
            "cinematic": (80, 0.52, [220, 247, 277, 294]),
        }
        
        params = style_params.get(style, (120, 0.5, [220, 247, 277, 294]))
        bpm, vol_mult, notes = params
        beat_dur = 60 / bpm
        
        for beat in range(total_beats):
            samples_per_beat = int(self.sample_rate * beat_dur)
            note = notes[beat % len(notes)]
            for i in range(samples_per_beat):
                t_local = i / self.sample_rate
                val = math.sin(2 * math.pi * note * t_local) * 0.3 * math.exp(-t_local * 2)
                val += math.sin(2 * math.pi * note * 0.5 * t_local) * 0.2 * math.exp(-t_local * 3)
                if beat % 4 == 0 and i < 1500:
                    val += math.sin(2 * math.pi * 60 * math.exp(-t_local*20) * t_local) * 0.5 * math.exp(-t_local*10)
                bgm_data.append(val * vol_mult)
        
        bgm_data = self.apply_lowpass_filter(bgm_data, 0.4)
        bgm_data = self.normalize_audio(bgm_data, 0.55)
        return bgm_data


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.current_bgm = None
        self.master_volume = 1.0
        self.sfx_volume = 0.8
        self.music_volume = 0.5
        self.sound_channels = {}
        
        self.enabled = False
        try:
            if pygame.mixer.get_init():
                self.enabled = True
            else:
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
        """设置主音量"""
        self.master_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
    
    def set_sfx_volume(self, volume):
        """设置音效音量"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume):
        """设置音乐音量"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
