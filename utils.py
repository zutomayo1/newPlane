import pygame
import random
import math
import sys
import os
import wave
import struct
import tempfile
import traceback
from config import *

# ==============================================================================
#   日志工具
# ==============================================================================
def log_error(msg):
    try:
        with open("debug.log", "a", encoding="utf-8") as f:
            f.write(str(msg) + "\n")
    except:
        pass

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

        except Exception as e:
            log_error(f"音频生成错误: {e}")
        return paths

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.current_bgm = None
        
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
        for name, path in self.file_paths.items():
            if path and not name.startswith("bgm"):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    vol = 0.5
                    if name == "shoot": vol = 0.15
                    if name == "warning": vol = 0.8
                    self.sounds[name].set_volume(vol)
                except: pass

    def play(self, name):
        if self.enabled and name in self.sounds:
            try: self.sounds[name].play()
            except: pass

    def play_music(self, track="normal"):
        if not self.enabled: return
        key = f"bgm_{track}"
        if key in self.file_paths and self.file_paths[key] and self.current_bgm != track:
            try:
                pygame.mixer.music.load(self.file_paths[key])
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                self.current_bgm = track
            except: pass

    def stop_music(self):
        if self.enabled:
            try: pygame.mixer.music.stop()
            except: pass
        self.current_bgm = None

# ==============================================================================
#   绘图与UI工具
# ==============================================================================
def get_font(size, bold=False):
    font_names = ["microsoftyahei", "simhei", "arial"]
    return pygame.font.SysFont(font_names, int(size), bold=bold)

def draw_text(surf, text, size, x, y, color=WHITE, align="center", shadow=True, glow=False):
    font = get_font(size, bold=True)
    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect()
    if align == "center": text_rect.midtop = (x, y)
    elif align == "left": text_rect.topleft = (x, y)
    elif align == "right": text_rect.topright = (x, y)
    
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

def draw_cyber_rect(surf, rect, color, alpha=255, cut_size=10, border_width=0, fill=True):
    # 如果rect是tuple，转为Rect对象
    if isinstance(rect, tuple):
        x, y, w, h = rect
    else:
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        
    points = [(x + cut_size, y), (x + w, y), (x + w, y + h - cut_size), (x + w - cut_size, y + h), (x, y + h), (x, y + cut_size)]
    if fill:
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        if len(color) == 4: draw_color = color
        else: draw_color = (*color, alpha)
        pygame.draw.polygon(s, draw_color, points)
        surf.blit(s, (0,0))
    if border_width > 0:
        pygame.draw.polygon(surf, color, points, border_width)

def draw_modern_bar(surf, x, y, pct, color, w=200, h=15, label=None, show_bg=True):
    pct = max(0, min(pct, 100))
    if show_bg:
        bg_points = [(x, y+h), (x+w, y+h), (x+w+h/2, y), (x+h/2, y)]
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(s, (20, 20, 30, 150), bg_points)
        surf.blit(s, (0,0))
        pygame.draw.polygon(surf, (100, 100, 100), bg_points, 1)
    fill_w = int((pct / 100) * w)
    if fill_w > 0:
        fill_points = [(x, y+h), (x+fill_w, y+h), (x+fill_w+h/2, y), (x+h/2, y)]
        pygame.draw.polygon(surf, color, fill_points)
        highlight_points = [(x+h/2, y), (x+fill_w+h/2, y), (x+fill_w+h/2, y+2), (x+h/2+2, y+2)]
        pygame.draw.polygon(surf, (255, 255, 255, 100), highlight_points)
    if label:
        draw_text(surf, label, 14, x + w + h + 5, y, WHITE, align="left", shadow=True)

# ==============================================================================
#   素材生成工具
# ==============================================================================
def get_plane_surf(pid):
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = CYBER_CYAN  # 统一使用极光青色
    edge_color = CYBER_CYAN_BRIGHT  # 边框使用更亮的电光蓝
    
    # 赛博朋克风格几何飞机
    if pid == "striker": 
        pygame.draw.polygon(s, c, [(60, 10), (110, 90), (60, 110), (10, 90)])
        pygame.draw.polygon(s, edge_color, [(60, 10), (110, 90), (60, 110), (10, 90)], 2)
        pygame.draw.polygon(s, WHITE, [(60, 30), (90, 90), (60, 100), (30, 90)], 1)
    elif pid == "phantom": 
        pygame.draw.polygon(s, c, [(60, 10), (90, 50), (120, 110), (60, 90), (0, 110), (30, 50)])
        pygame.draw.polygon(s, edge_color, [(60, 10), (90, 50), (120, 110), (60, 90), (0, 110), (30, 50)], 2)
    elif pid == "titan": 
        pygame.draw.rect(s, c, (20, 20, 80, 80))
        pygame.draw.rect(s, edge_color, (20, 20, 80, 80), 2)
        pygame.draw.rect(s, CYBER_AMBER, (40, 0, 40, 40))
    elif pid == "thunderbird": 
        pygame.draw.polygon(s, c, [(60, 0), (20, 60), (0, 40), (20, 100), (60, 80), (100, 100), (120, 40), (100, 60)])
        pygame.draw.polygon(s, edge_color, [(60, 0), (20, 60), (0, 40), (20, 100), (60, 80), (100, 100), (120, 40), (100, 60)], 2)
    elif pid == "viper": 
        pygame.draw.polygon(s, c, [(60, 0), (100, 40), (80, 100), (40, 100), (20, 40)])
        pygame.draw.polygon(s, edge_color, [(60, 0), (100, 40), (80, 100), (40, 100), (20, 40)], 2)
    elif pid == "specter": 
        pygame.draw.polygon(s, c, [(60, 0), (80, 80), (60, 100), (40, 80)])
        pygame.draw.polygon(s, edge_color, [(60, 0), (80, 80), (60, 100), (40, 80)], 2)
    elif pid == "aurora": 
        pygame.draw.circle(s, c, (60, 60), 50)
        pygame.draw.circle(s, edge_color, (60, 60), 50, 2)
        pygame.draw.circle(s, WHITE, (60, 60), 20)
    elif pid == "crimson": 
        pygame.draw.polygon(s, CYBER_RED_ALERT, [(50, 80), (20, 20), (50, 40), (80, 20)])
        pygame.draw.polygon(s, CYBER_CYAN_BRIGHT, [(50, 80), (20, 20), (50, 40), (80, 20)], 2)
        pygame.draw.line(s, WHITE, (50, 80), (50, 10), 3)
    elif pid == "stalker": 
        pygame.draw.polygon(s, c, [(50, 10), (30, 50), (10, 40), (30, 70), (50, 90), (70, 70), (90, 40), (70, 50)])
        pygame.draw.polygon(s, edge_color, [(50, 10), (30, 50), (10, 40), (30, 70), (50, 90), (70, 70), (90, 40), (70, 50)], 2)
        pygame.draw.circle(s, CYBER_AMBER, (30, 30), 5)
    elif pid == "gaia": 
        pygame.draw.polygon(s, c, [(30, 20), (70, 20), (90, 60), (70, 90), (30, 90), (10, 60)])
        pygame.draw.polygon(s, edge_color, [(30, 20), (70, 20), (90, 60), (70, 90), (30, 90), (10, 60)], 2)
        pygame.draw.circle(s, CYBER_LIME, (50, 50), 20)
    elif pid == "weaver": 
        pygame.draw.circle(s, c, (60, 60), 25)
        pygame.draw.circle(s, edge_color, (60, 60), 25, 2)
        pygame.draw.circle(s, WHITE, (60, 60), 10)
    elif pid == "solar": 
        pygame.draw.circle(s, CYBER_AMBER, (60, 60), 30)
        pygame.draw.circle(s, edge_color, (60, 60), 30, 2)
    elif pid == "arbiter": 
        pygame.draw.polygon(s, c, [(60, 10), (110, 60), (60, 110), (10, 60)])
        pygame.draw.polygon(s, edge_color, [(60, 10), (110, 60), (60, 110), (10, 60)], 2)
        pygame.draw.rect(s, CYBER_CYAN_BRIGHT, (45, 45, 30, 30), 1)
    return s

def get_boss_surf(type_name, color):
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

    if type_name == "carrier": draw_carrier()
    elif type_name == "fortress": draw_fortress()
    elif type_name == "assassin": draw_assassin()
    elif type_name == "seraphim": draw_seraphim()
    elif type_name == "leviathan": draw_leviathan()
    elif type_name == "overlord": draw_overlord()
    elif type_name == "ragnarok": draw_ragnarok()
    elif type_name == "hydra": draw_hydra()
    elif type_name == "chronos": draw_chronos()
    elif type_name == "gazer": draw_gazer()
    elif type_name == "lich": draw_lich()
    elif type_name == "tempest": draw_tempest()
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