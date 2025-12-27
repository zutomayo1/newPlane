# -*- coding: utf-8 -*-
"""
游戏上下文 - 提供全局共享的游戏状态和资源引用

这个模块解决UI模块与main.py之间的循环依赖问题。
main.py在初始化时将关键对象注册到这里，其他模块通过这里访问。
"""

import pygame

# ==================== 核心引用 ====================
# 这些变量在main.py初始化时被设置
screen = None  # pygame屏幕对象
sound_mgr = None  # 音频管理器
music_director = None  # 音乐总监

# ==================== 游戏设置 ====================
game_settings = {}  # 当前游戏设置字典

# ==================== 游戏状态 ====================
game_state = "menu"  # 当前游戏状态

# ==================== UI状态 ====================
settings_saved_timer = 0
settings_saved_msg = ""

# ==================== 常量 ====================
WIDTH = 1280
HEIGHT = 720

# 颜色常量
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
LIME = (0, 255, 128)

# ==================== 工具函数 ====================

def get_mouse_pos():
    """获取鼠标位置"""
    return pygame.mouse.get_pos()

def init_context(main_screen, main_sound_mgr, main_music_director, main_settings):
    """
    初始化游戏上下文（由main.py调用）
    
    Args:
        main_screen: pygame屏幕对象
        main_sound_mgr: SoundManager实例
        main_music_director: MusicDirector实例
        main_settings: 游戏设置字典
    """
    global screen, sound_mgr, music_director, game_settings
    screen = main_screen
    sound_mgr = main_sound_mgr
    music_director = main_music_director
    game_settings = main_settings

def set_game_state(new_state):
    """设置游戏状态"""
    global game_state
    game_state = new_state

def get_game_state():
    """获取当前游戏状态"""
    return game_state

def set_settings_message(msg, timer=120):
    """设置设置保存消息"""
    global settings_saved_msg, settings_saved_timer
    settings_saved_msg = msg
    settings_saved_timer = timer
