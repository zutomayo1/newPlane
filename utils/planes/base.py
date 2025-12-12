"""
机体渲染基础模块

包含缓存、通用辅助函数和渲染入口
"""
import pygame
import math

from config import CYBER_CYAN, CYBER_CYAN_BRIGHT
from ..core import log_error

# ==============================================================================
#   机体缓存
# ==============================================================================
_plane_cache = {}


def get_plane_surf(pid, visual=None, static=False):
    """获取机体渲染图像（带缓存）"""
    cache_key = None
    if static:
        vis_key = None
        if visual:
            try:
                items = []
                for k, v in sorted(visual.items()):
                    if isinstance(v, list):
                        items.append((k, tuple(v)))
                    elif isinstance(v, dict):
                        sub_items = tuple(sorted(v.items()))
                        items.append((k, sub_items))
                    else:
                        items.append((k, v))
                vis_key = tuple(items)
            except Exception:
                vis_key = str(visual)
        
        cache_key = (pid, vis_key)
        if cache_key in _plane_cache:
            return _plane_cache[cache_key]

    try:
        s = _generate_plane_surf(pid, visual, static)
    except Exception as e:
        log_error(f"Error generating plane surf for {pid}: {e}")
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 0, 0), (60, 60), 30)
    
    if static and cache_key:
        _plane_cache[cache_key] = s
    return s


def _generate_plane_surf(pid, visual=None, static=False):
    """生成机体渲染 - 主入口函数"""
    s = pygame.Surface((120, 120), pygame.SRCALPHA)
    c = CYBER_CYAN
    edge_color = CYBER_CYAN_BRIGHT
    
    if visual:
        c = visual.get('neon_color', c)
        edge_color = visual.get('accent_color', edge_color)
        glow_color = visual.get('neon_color', c)
        glow_surf = pygame.Surface((140, 140), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*glow_color, 30), (70, 70), 60)
        s.blit(glow_surf, (-10, -10))
    
    if static:
        t = 0
        pulse = 0
    else:
        t = pygame.time.get_ticks() / 1000.0
        pulse = abs(math.sin(t * 3))
    
    # 检查是否有模型样式覆盖 (专属改装)
    model_style = visual.get('model_style') if visual else None
    
    if model_style:
        # 尝试 MK2 涂装（已拆分）
        from .skins_mk2 import render_mk2_skin, is_mk2_style
        if is_mk2_style(model_style):
            result = render_mk2_skin(s, pid, model_style, c, edge_color, t, pulse)
            if result:
                return result
        
        # 尝试 Striker 专属涂装（已拆分）
        from .skins_striker import render_striker_skin, is_striker_style
        if is_striker_style(model_style):
            result = render_striker_skin(s, model_style, c, edge_color, t, pulse)
            if result:
                return result
        
        # 尝试 Phantom 专属涂装（已拆分）
        from .skins_phantom import render_phantom_skin, is_phantom_style
        if is_phantom_style(model_style):
            result = render_phantom_skin(s, model_style, c, edge_color, t, pulse)
            if result:
                return result
        
        # 尝试 Titan 专属涂装（已拆分）
        from .skins_titan import render_titan_skin, is_titan_style
        if is_titan_style(model_style):
            result = render_titan_skin(s, model_style, c, edge_color, t, pulse)
            if result:
                return result
        
        # 尝试 Thunderbird 专属涂装（已拆分）
        from .skins_thunderbird import render_thunderbird_skin, is_thunderbird_style
        if is_thunderbird_style(model_style):
            result = render_thunderbird_skin(s, model_style, c, edge_color, t, pulse)
            if result:
                return result
        
        # 尝试 Viper 专属涂装（已拆分）
        from .skins_viper import render_viper_skin, is_viper_style
        if is_viper_style(model_style):
            result = render_viper_skin(s, model_style, c, edge_color, t, pulse)
            if result:
                return result
        
        # 尝试 Specter 专属涂装（已拆分）
        from .skins_specter import render_specter_skin, is_specter_style
        if is_specter_style(model_style):
            result = render_specter_skin(s, model_style, c, edge_color, t, pulse)
            if result:
                return result
        
        # 尝试 Aurora 专属涂装（已拆分）
        from .skins_aurora import render_aurora_skin, is_aurora_style
        if is_aurora_style(model_style):
            result = render_aurora_skin(s, model_style, c, edge_color, t, pulse)
            if result:
                return result
        
        # 尝试 Crimson 专属涂装（已拆分）
        from .skins_crimson import render_crimson_skin, is_crimson_style
        if is_crimson_style(model_style):
            result = render_crimson_skin(s, model_style, c, edge_color, t, pulse)
            if result:
                return result
        
        # 尝试 Stalker 专属涂装（已拆分）
        from .skins_stalker import render_stalker_skin, is_stalker_style
        if is_stalker_style(model_style):
            result = render_stalker_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Gaia 专属涂装（已拆分）
        from .skins_gaia import render_gaia_skin, is_gaia_style
        if is_gaia_style(model_style):
            result = render_gaia_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Weaver 专属涂装（已拆分）
        from .skins_weaver import render_weaver_skin, is_weaver_style
        if is_weaver_style(model_style):
            result = render_weaver_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Solar 专属涂装（已拆分）
        from .skins_solar import render_solar_skin, is_solar_style
        if is_solar_style(model_style):
            result = render_solar_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Arbiter 专属涂装（已拆分）
        from .skins_arbiter import render_arbiter_skin, is_arbiter_style
        if is_arbiter_style(model_style):
            result = render_arbiter_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Eclipse 专属涂装（已拆分）
        from .skins_eclipse import render_eclipse_skin, is_eclipse_style
        if is_eclipse_style(model_style):
            result = render_eclipse_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Prism 专属涂装（已拆分）
        from .skins_prism import render_prism_skin, is_prism_style
        if is_prism_style(model_style):
            result = render_prism_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Necro 专属涂装（已拆分）
        from .skins_necro import render_necro_skin, is_necro_style
        if is_necro_style(model_style):
            result = render_necro_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Wormhole 专属涂装（已拆分）
        from .skins_wormhole import render_wormhole_skin, is_wormhole_style
        if is_wormhole_style(model_style):
            result = render_wormhole_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Chronos 专属涂装（已拆分）
        from .skins_chronos import render_chronos_skin, is_chronos_style
        if is_chronos_style(model_style):
            result = render_chronos_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Mirage 专属涂装（已拆分）
        from .skins_mirage import render_mirage_skin, is_mirage_style
        if is_mirage_style(model_style):
            result = render_mirage_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Gambit 专属涂装（已拆分）
        from .skins_gambit import render_gambit_skin, is_gambit_style
        if is_gambit_style(model_style):
            result = render_gambit_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Puppeteer 专属涂装（已拆分）
        from .skins_puppeteer import render_puppeteer_skin, is_puppeteer_style
        if is_puppeteer_style(model_style):
            result = render_puppeteer_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Pandemic 专属涂装（已拆分）
        from .skins_pandemic import render_pandemic_skin, is_pandemic_style
        if is_pandemic_style(model_style):
            result = render_pandemic_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Omega 专属涂装（终极机体）
        from .skins_omega import render_omega_skin, is_omega_style
        if is_omega_style(model_style):
            result = render_omega_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Genesis 专属涂装（终极机体）
        from .skins_genesis import render_genesis_skin, is_genesis_style
        if is_genesis_style(model_style):
            result = render_genesis_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Truth 专属涂装（终极机体）
        from .skins_truth import render_truth_skin, is_truth_style
        if is_truth_style(model_style):
            result = render_truth_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Asura 专属涂装（近战机体）
        from .skins_asura import render_asura_skin, is_asura_style
        if is_asura_style(model_style):
            result = render_asura_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Dragoon 专属涂装（近战机体）
        from .skins_dragoon import render_dragoon_skin, is_dragoon_style
        if is_dragoon_style(model_style):
            result = render_dragoon_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Origami 专属涂装（折纸鹤机体）
        from .skins_origami import render_origami_skin, is_origami_style
        if is_origami_style(model_style):
            result = render_origami_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Helios 专属涂装（远程狙击机体）
        from .skins_helios import render_helios_skin, is_helios_style
        if is_helios_style(model_style):
            result = render_helios_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Frostflare 专属涂装（远程狙击机体）
        from .skins_frostflare import render_frostflare_skin, is_frostflare_style
        if is_frostflare_style(model_style):
            result = render_frostflare_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Nova 专属涂装（远程狙击机体）
        from .skins_nova import render_nova_skin, is_nova_style
        if is_nova_style(model_style):
            result = render_nova_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Spectrum 专属涂装（远程狙击机体）
        from .skins_spectrum import render_spectrum_skin, is_spectrum_style
        if is_spectrum_style(model_style):
            result = render_spectrum_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Darkstring 专属涂装（远程狙击机体）
        from .skins_darkstring import render_darkstring_skin, is_darkstring_style
        if is_darkstring_style(model_style):
            result = render_darkstring_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 所有涂装都已拆分，如果没有匹配则继续渲染基础机体
        # （不再需要 utils_legacy 回退）
    
    # T1 机体（已拆分）
    if pid in ("striker", "phantom", "titan", "thunderbird", "viper", 
               "specter", "aurora", "crimson", "stalker"):
        from .tier1 import render_tier1
        render_tier1(s, pid, c, edge_color, t, pulse, visual)
    
    # T2 机体（已拆分）
    elif pid in ("gaia", "weaver", "solar", "arbiter"):
        from .tier2 import render_tier2
        render_tier2(s, pid, c, edge_color, t, pulse, visual)
    
    # T3 机体（已拆分）
    elif pid in ("eclipse", "prism", "necro", "wormhole"):
        from .tier3 import render_tier3
        render_tier3(s, pid, c, edge_color, t, pulse, visual)
    
    # 特殊机体（已拆分）
    elif pid in ("chronos", "mirage", "gambit"):
        from .special import render_special
        render_special(s, pid, c, edge_color, t, pulse, visual)
    
    # 隐藏机体（已拆分）
    elif pid in ("puppeteer", "pandemic"):
        from .hidden import render_hidden
        render_hidden(s, pid, c, edge_color, t, pulse)
    
    # 终极机体 - Omega
    elif pid == "omega":
        from .skins_omega import _render_omega_base
        _render_omega_base(s, t, pulse)
    
    # 终极机体 - Genesis
    elif pid == "genesis":
        from .skins_genesis import _render_genesis_base
        _render_genesis_base(s, t, pulse)
    
    # 终极机体 - Truth
    elif pid == "truth":
        from .skins_truth import _render_truth_base
        _render_truth_base(s, t, pulse)
    
    # 近战机体 - Asura
    elif pid == "asura":
        from .skins_asura import _render_asura_base
        _render_asura_base(s, t, pulse)
    
    # 近战机体 - Dragoon
    elif pid == "dragoon":
        from .skins_dragoon import _render_dragoon_base
        _render_dragoon_base(s, t, pulse)
    
    # 折纸鹤机体 - Origami
    elif pid == "origami":
        from .skins_origami import _render_origami_base
        _render_origami_base(s, t, pulse)
    
    # 远程狙击机体 - Helios
    elif pid == "helios":
        from .skins_helios import _render_helios_base
        _render_helios_base(s, t, pulse)
    
    # 远程狙击机体 - Frostflare
    elif pid == "frostflare":
        from .skins_frostflare import _render_frostflare_base
        _render_frostflare_base(s, t, pulse)
    
    # 远程狙击机体 - Nova
    elif pid == "nova":
        from .skins_nova import _render_nova_base
        _render_nova_base(s, t, pulse)
    
    # 远程狙击机体 - Spectrum
    elif pid == "spectrum":
        from .skins_spectrum import _render_spectrum_base
        _render_spectrum_base(s, t, pulse)
    
    # 远程狙击机体 - Darkstring
    elif pid == "darkstring":
        from .skins_darkstring import _render_darkstring_base
        _render_darkstring_base(s, t, pulse)
    
    else:
        # 默认占位图形
        pygame.draw.circle(s, c, (60, 60), 30)
        pygame.draw.circle(s, edge_color, (60, 60), 30, 2)
    
    return s


def clear_plane_cache():
    """清空机体缓存"""
    global _plane_cache
    _plane_cache.clear()


__all__ = ['get_plane_surf', 'clear_plane_cache']
