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
            
            # 18. Achievement (成就解锁)
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
        
    points = [(x + cut_size, y), (x + w, y), (x + w, y + h - cut_size), (x + w - cut_size, y + h), (x, y + h), (x, y + cut_size)]
    if surf is None:
        log_debug("draw_cyber_rect: surf is None, skipping draw")
        return
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
def get_plane_surf(pid, visual=None):
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
    t = pygame.time.get_ticks() / 1000.0
    pulse = abs(math.sin(t * 3))
    
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