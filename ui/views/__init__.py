# -*- coding: utf-8 -*-
"""
UI视图模块 - 所有界面绘制函数
"""

# 导出所有视图函数
# from .settings import draw_settings_ui
# from .audio_extension import draw_audio_extension_ui
# from .keybind import draw_keybind_settings_ui

from .mode_select import (
    draw_mode_select_ui,
    get_mode_select_selected,
    set_mode_select_selected
)

__all__ = [
    # 模式选择
    'draw_mode_select_ui',
    'get_mode_select_selected',
    'set_mode_select_selected',
]
