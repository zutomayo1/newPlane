# -*- coding: utf-8 -*-
"""
游戏状态管理器 - 统一管理所有游戏状态切换
"""

from typing import Callable, Dict, Optional, Any
from enum import Enum, auto


class GameState(Enum):
    """游戏状态枚举"""
    # 菜单相关
    MENU = auto()
    MODE_SELECT = auto()
    PLANE_SELECT = auto()
    SETTINGS = auto()
    KEYBIND_SETTINGS = auto()
    AUDIO_EXTENSION = auto()
    
    # 游戏相关
    GAME = auto()
    PAUSED = auto()
    UPGRADE = auto()
    GAME_OVER = auto()
    
    # 挑战模式
    BOSS_CHALLENGE = auto()
    BOSS_CHALLENGE_PLAY = auto()
    BOSS_CHALLENGE_COMPLETE = auto()
    TRAINING_GROUND = auto()
    TRAINING_SELECT_PLANE = auto()
    TRAINING_PLAY = auto()
    
    # 其他界面
    CODEX = auto()
    TALENT_TREE = auto()
    MUSIC_LIBRARY = auto()
    AUDIO_HUB = auto()
    SOUND_LAB = auto()
    CUSTOMIZATION = auto()
    ACHIEVEMENTS = auto()
    DAILY_QUESTS = auto()
    GALLERY = auto()
    DATABASE = auto()
    PERSONALIZATION = auto()
    APPEARANCE_SETTINGS = auto()
    BACKGROUND_SETTINGS = auto()


class GameStateManager:
    """
    游戏状态管理器
    
    功能：
    - 统一管理状态切换
    - 支持状态进入/离开回调
    - 维护状态历史（用于返回）
    - 提供状态查询接口
    """
    
    def __init__(self):
        self._current_state: str = "menu"
        self._previous_state: str = "menu"
        self._state_history: list = []
        self._max_history = 10
        
        # 状态回调
        self._enter_callbacks: Dict[str, Callable] = {}
        self._exit_callbacks: Dict[str, Callable] = {}
        
        # 状态数据（每个状态可以存储临时数据）
        self._state_data: Dict[str, Any] = {}
    
    @property
    def current(self) -> str:
        """获取当前状态"""
        return self._current_state
    
    @property
    def previous(self) -> str:
        """获取上一个状态"""
        return self._previous_state
    
    def is_state(self, *states: str) -> bool:
        """检查当前是否为指定状态之一"""
        return self._current_state in states
    
    def is_in_game(self) -> bool:
        """检查是否在游戏中"""
        return self._current_state in ("game", "boss_challenge_play", "training_play")
    
    def is_in_menu(self) -> bool:
        """检查是否在菜单相关界面"""
        return self._current_state in (
            "menu", "mode_select", "plane_select", "settings", 
            "keybind_settings", "audio_extension"
        )
    
    def change_state(self, new_state: str, save_history: bool = True, **kwargs):
        """
        切换游戏状态
        
        Args:
            new_state: 新状态名称
            save_history: 是否保存到历史（用于返回）
            **kwargs: 传递给新状态的数据
        """
        if new_state == self._current_state:
            return
        
        old_state = self._current_state
        
        # 调用离开回调
        if old_state in self._exit_callbacks:
            self._exit_callbacks[old_state]()
        
        # 保存历史
        if save_history:
            self._state_history.append(old_state)
            if len(self._state_history) > self._max_history:
                self._state_history.pop(0)
        
        # 更新状态
        self._previous_state = old_state
        self._current_state = new_state
        
        # 存储状态数据
        if kwargs:
            self._state_data[new_state] = kwargs
        
        # 调用进入回调
        if new_state in self._enter_callbacks:
            self._enter_callbacks[new_state](**kwargs)
    
    def go_back(self) -> bool:
        """
        返回上一个状态
        
        Returns:
            是否成功返回
        """
        if not self._state_history:
            return False
        
        previous = self._state_history.pop()
        self.change_state(previous, save_history=False)
        return True
    
    def register_enter_callback(self, state: str, callback: Callable):
        """注册状态进入回调"""
        self._enter_callbacks[state] = callback
    
    def register_exit_callback(self, state: str, callback: Callable):
        """注册状态离开回调"""
        self._exit_callbacks[state] = callback
    
    def get_state_data(self, state: str = None) -> Any:
        """获取状态数据"""
        if state is None:
            state = self._current_state
        return self._state_data.get(state, {})
    
    def set_state_data(self, key: str, value: Any, state: str = None):
        """设置状态数据"""
        if state is None:
            state = self._current_state
        if state not in self._state_data:
            self._state_data[state] = {}
        self._state_data[state][key] = value
    
    def clear_history(self):
        """清除状态历史"""
        self._state_history.clear()


# 全局状态管理器实例
state_manager = GameStateManager()


# ==================== 便捷函数 ====================

def get_state() -> str:
    """获取当前游戏状态"""
    return state_manager.current

def set_state(new_state: str, **kwargs):
    """设置游戏状态"""
    state_manager.change_state(new_state, **kwargs)

def is_state(*states: str) -> bool:
    """检查当前状态"""
    return state_manager.is_state(*states)

def go_back() -> bool:
    """返回上一状态"""
    return state_manager.go_back()
