"""
工具包 - 统一导出接口

此包重新导出所有子模块的公共接口，保持向后兼容
"""

# 机体渲染（从 planes 子包导入）
from .planes import get_plane_surf, clear_plane_cache

# 核心功能（已拆分到子模块）
from .core import (
    log_error, log_info, log_debug,
    save_settings, load_settings,
    safe_blit
)

# 音频系统（已拆分到子模块）
from .audio import (
    AudioSynthesizer,
    SoundManager
)

# 创建全局音频管理器实例
sound_mgr = SoundManager()

# UI绘制（已拆分到子模块）
from .ui import (
    get_font,
    draw_text, draw_mono_text, draw_spaced_text,
    draw_cyber_rect, draw_modern_bar, draw_slanted_bar,
    draw_rounded_rect_with_gradient, draw_scanline_overlay,
    draw_badge
)

# 敌人渲染（已拆分到子模块）
from .enemies import (
    get_boss_surf,
    procedural_interceptor_surface,
    procedural_juggernaut_surface,
    procedural_swarmer_surface,
    procedural_dreadnought_surface,
    _bloom
)

__all__ = [
    # Core
    'log_error', 'log_info', 'log_debug',
    'save_settings', 'load_settings',
    'safe_blit',
    # Audio
    'AudioSynthesizer', 'SoundManager',
    'sound_mgr',  # 全局实例
    # UI
    'get_font',
    'draw_text', 'draw_mono_text', 'draw_spaced_text',
    'draw_cyber_rect', 'draw_modern_bar', 'draw_slanted_bar',
    'draw_rounded_rect_with_gradient', 'draw_scanline_overlay',
    'draw_badge',
    # Planes
    'get_plane_surf', 'clear_plane_cache',
    # Enemies
    'get_boss_surf',
    'procedural_interceptor_surface',
    'procedural_juggernaut_surface',
    'procedural_swarmer_surface',
    'procedural_dreadnought_surface',
    '_bloom'
]
