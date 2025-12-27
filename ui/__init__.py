# -*- coding: utf-8 -*-
"""
UI模块 - 统一管理UI相关组件

包含:
- context: 共享游戏上下文
- components: 可复用UI组件
- state_manager: 游戏状态管理器
- draw_utils: 绘制工具函数
- views: UI视图函数（待迁移）
"""

from .context import (
    init_context,
    get_mouse_pos,
    # 颜色常量
    WHITE, BLACK, GRAY, 
    RED, LIME, CYAN, MAGENTA, YELLOW, ORANGE
)

from .components import (
    get_font,
    draw_cyber_rect,
    draw_gradient_rect,
    draw_text,
    Button,
    Slider,
    Checkbox,
    Panel
)

from .state_manager import (
    GameState,
    GameStateManager,
    state_manager,
    get_state,
    set_state,
    is_state,
    go_back
)

from .draw_utils import (
    draw_grid_background,
    draw_particles,
    draw_glow_border,
    draw_title_panel,
    draw_section_header,
    draw_progress_bar,
    draw_slider_handle,
    draw_action_button,
    draw_item_card,
    draw_popup_panel,
    draw_save_message
)

__all__ = [
    # Context
    'init_context',
    'get_mouse_pos',
    # Colors
    'WHITE', 'BLACK', 'GRAY', 'RED', 'LIME', 'CYAN', 'MAGENTA', 'YELLOW', 'ORANGE',
    # Components
    'get_font', 'draw_cyber_rect', 'draw_gradient_rect', 'draw_text',
    'Button', 'Slider', 'Checkbox', 'Panel',
    # State Manager
    'GameState', 'GameStateManager', 'state_manager',
    'get_state', 'set_state', 'is_state', 'go_back',
    # Draw Utils
    'draw_grid_background', 'draw_particles', 'draw_glow_border',
    'draw_title_panel', 'draw_section_header',
    'draw_progress_bar', 'draw_slider_handle',
    'draw_action_button', 'draw_item_card',
    'draw_popup_panel', 'draw_save_message'
]
