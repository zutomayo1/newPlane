"""
核心工具模块 - 日志、设置管理、基础工具函数
"""
import os
import json
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

def save_settings(background_style=None, master_volume=None, music_volume=None, sfx_volume=None, show_fps=None, screen_shake=None, particle_quality=None, show_damage_numbers=None, auto_fire=None):
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
    if auto_fire is not None:
        settings["auto_fire"] = auto_fire
    
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
    """Safely blit a surface if both source and target are non-None."""
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
