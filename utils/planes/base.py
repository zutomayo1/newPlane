"""
机体渲染基础模块

包含缓存、通用辅助函数和渲染入口
支持从资产文件加载（优先）或程序化渲染（回退）
"""
import pygame
import math

from config import CYBER_CYAN, CYBER_CYAN_BRIGHT
from ..core import log_error

# ==============================================================================
#   机体缓存
# ==============================================================================
_plane_cache = {}

# 资产管理器（延迟导入避免循环引用）
_asset_manager = None

def _get_asset_manager():
    """获取资产管理器实例"""
    global _asset_manager
    if _asset_manager is None:
        try:
            from ..asset_manager import asset_manager
            _asset_manager = asset_manager
        except ImportError:
            _asset_manager = False  # 标记为不可用
    return _asset_manager if _asset_manager else None


def get_plane_surf(pid, visual=None, static=False):
    """
    获取机体渲染图像（带缓存）
    
    优先从 assets/sprites/planes/{pid}/{skin}.png 加载
    如果不存在则回退到程序化渲染
    """
    cache_key = None
    skin_id = "default"
    
    # 确定涂装ID
    if visual:
        model_style = visual.get("model_style")
        if model_style:
            # 从 model_style 提取 skin_id
            if model_style.startswith(f"{pid}_"):
                skin_id = model_style[len(pid)+1:]
            else:
                skin_id = model_style
    
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
    
    # 尝试从资产文件加载
    asset_mgr = _get_asset_manager()
    if asset_mgr and static:
        sprite_path = f"sprites/planes/{pid}/{skin_id}.png"
        sprite = asset_mgr.get_sprite(sprite_path)
        if sprite is not None:
            if cache_key:
                _plane_cache[cache_key] = sprite
            return sprite

    # 回退到程序化渲染
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
        
        # 尝试 Thornvine 专属涂装（藤骨机体）
        from .skins_thornvine import render_thornvine_skin, is_thornvine_style
        if is_thornvine_style(model_style):
            result = render_thornvine_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Starblade 专属涂装（环刃机体）
        from .skins_starblade import render_starblade_skin, is_starblade_style
        if is_starblade_style(model_style):
            result = render_starblade_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Acidswamp 专属涂装（酸沼机体）
        from .skins_acidswamp import render_acidswamp_skin, is_acidswamp_style
        if is_acidswamp_style(model_style):
            result = render_acidswamp_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Crystalfall 专属涂装（晶瀑机体）
        from .skins_crystalfall import render_crystalfall_skin, is_crystalfall_style
        if is_crystalfall_style(model_style):
            result = render_crystalfall_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Sporeveil 专属涂装（菌幕机体）
        from .skins_sporeveil import render_sporeveil_skin, is_sporeveil_style
        if is_sporeveil_style(model_style):
            result = render_sporeveil_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Cthulhu 专属涂装（月蚀星骸·克苏鲁）
        from .skins_cthulhu import render_cthulhu_skin, is_cthulhu_style
        if is_cthulhu_style(model_style):
            result = render_cthulhu_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Turu 专属涂装（巨石核拳·图鲁）
        from .skins_turu import render_turu_skin, is_turu_style
        if is_turu_style(model_style):
            result = render_turu_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Staradia 专属涂装（辉耀天女·斯塔德）
        from .skins_staradia import render_staradia_skin, is_staradia_style
        if is_staradia_style(model_style):
            render_staradia_skin(s, 60, 60, model_style, 30, t)
            return s
        
        # 尝试 DukeFishron 专属涂装（深渊龙鱼·猪公爵）
        from .skins_dukefishron import draw_duke
        from . import is_dukefishron_style
        if is_dukefishron_style(model_style):
            frame = int(t * 60) if not static else 0
            draw_duke(s, c, 10, 10, 100, 100, frame, model_style)
            return s
        
        # 尝试 Slime 专属涂装（末世星凝·史莱姆）
        from .skins_slime import render_slime_skin, is_slime_style
        if is_slime_style(model_style):
            frame = int(t * 60) if not static else 0
            from .skins_slime import draw_slime
            draw_slime(s, c, 10, 10, 100, 100, frame, model_style)
            return s
        
        # 尝试 Oro 专属涂装（终噬星链·奥罗）
        from .skins_oro import render_oro_skin, is_oro_style
        if is_oro_style(model_style):
            frame = int(t * 60) if not static else 0
            from .skins_oro import draw_oro
            draw_oro(s, c, 10, 10, 100, 100, frame, model_style)
            return s
        
        # 尝试 Yharon 专属涂装（狱炎神龙·犽戎）
        from .skins_yharon import render_yharon_skin, is_yharon_style
        if is_yharon_style(model_style):
            frame = int(t * 60) if not static else 0
            from .skins_yharon import draw_yharon
            draw_yharon(s, c, 10, 10, 100, 100, frame, model_style)
            return s
        
        # 尝试 Providence 专属涂装（亵渎天神·普罗维登斯）
        from .skins_providence import render_providence_skin, is_providence_style
        if is_providence_style(model_style):
            frame = int(t * 60) if not static else 0
            from .skins_providence import draw_providence
            draw_providence(s, c, 10, 10, 100, 100, frame, model_style)
            return s
        
        # 尝试 Goliath 专属涂装（瘟疫使者·歌莉娅）
        from .skins_goliath import is_goliath_style
        if is_goliath_style(model_style):
            frame = int(t * 60) if not static else 0
            from .skins_goliath import draw_goliath
            draw_goliath(s, c, 10, 10, 100, 100, frame, model_style)
            return s
        
        # 尝试 Sepulcher 专属涂装（至尊灾厄·终末王座）
        if model_style and model_style.startswith("sepulcher_"):
            frame = int(t * 60) if not static else 0
            from .skins_sepulcher import get_sepulcher_theme
            theme = get_sepulcher_theme(model_style)
            _draw_sepulcher_preview(s, c, 10, 10, 100, 100, frame, theme)
            return s
        
        # 尝试 Galaxia 专属涂装（宇宙之弧·Galaxia）
        if model_style and model_style.startswith("galaxia_"):
            frame = int(t * 60) if not static else 0
            from .skins_galaxia import render_galaxia_plane
            # 280x280的surface，中心区域100x100，留出90像素边距容纳2.0倍放大
            big_s = pygame.Surface((280, 280), pygame.SRCALPHA)
            render_galaxia_plane(big_s, c, 90, 90, 100, 100, frame, model_style)
            scaled = pygame.transform.smoothscale(big_s, (120, 120))
            s.blit(scaled, (0, 0))
            return s
        
        # 尝试 Magnus 专属涂装（真理之书·MAGNUS）
        if model_style and model_style.startswith("magnus_"):
            frame = int(t * 60) if not static else 0
            from .skins_magnus import render_magnus_plane
            # 400x400的surface，中心区域100x100，留出150像素边距容纳2.3倍放大的所有视觉效果
            big_s = pygame.Surface((400, 400), pygame.SRCALPHA)
            render_magnus_plane(big_s, c, 150, 150, 100, 100, frame, model_style)
            scaled = pygame.transform.smoothscale(big_s, (120, 120))
            s.blit(scaled, (0, 0))
            return s
        
        # 尝试 Heavy Metal 专属涂装（维那斯万岁·HEAVY METAL）
        from .skins_heavymetal import is_heavymetal_style
        if is_heavymetal_style(model_style):
            frame = int(t * 60) if not static else 0
            from .skins_heavymetal import render_heavymetal_skin
            render_heavymetal_skin(s, c, 60, 60, 100, 100, frame, model_style)
            return s
        
        # 尝试 Scarlet 专属涂装（绯红恶魔·SCARLET）
        from .skins_scarlet import render_scarlet_skin, is_scarlet_style
        if is_scarlet_style(model_style):
            result = render_scarlet_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Zenith 专属涂装（分形天顶·ZENITH）
        from .skins_zenith import render_zenith_skin, is_zenith_style
        if is_zenith_style(model_style):
            result = render_zenith_skin(s, c, model_style, t, pid, static)
            if result:
                return result
        
        # 尝试 Viscerator 专属涂装（光之在解·VISCERATOR）
        from .skins_viscerator import is_viscerator_style, draw_viscerator_plane
        if is_viscerator_style(model_style):
            frame = int(t * 60) if t > 0 else 0
            draw_viscerator_plane(s, model_style, frame)
            return s
        
        # 尝试 Crusher 专属涂装（晶体粉碎者·CRUSHER）
        from .skins_crusher import is_crusher_style, draw_crusher_plane
        if is_crusher_style(model_style):
            frame = int(t * 60) if t > 0 else 0
            draw_crusher_plane(s, model_style, frame)
            return s
        
        # 尝试 SDMG 专属涂装（星际海豚·S.D.M.G.）
        from .skins_sdmg import is_sdmg_style, draw_sdmg
        if is_sdmg_style(model_style):
            frame = int(t * 60) if t > 0 else 0
            draw_sdmg(s, c, 10, 10, 100, 100, frame, model_style)
            return s
        
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
    
    # 藤骨机体 - Thornvine
    elif pid == "thornvine":
        from .skins_thornvine import _render_thornvine_base
        _render_thornvine_base(s, t, pulse)
    
    # 环刃机体 - Starblade
    elif pid == "starblade":
        from .skins_starblade import _render_starblade_base
        _render_starblade_base(s, t, pulse)
    
    # 酸沼机体 - Acidswamp
    elif pid == "acidswamp":
        from .skins_acidswamp import _render_acidswamp_base
        _render_acidswamp_base(s, t, pulse)
    
    # 晶瀑机体 - Crystalfall
    elif pid == "crystalfall":
        from .skins_crystalfall import _render_crystalfall_base
        _render_crystalfall_base(s, t, pulse)
    
    # 菌幕机体 - Sporeveil
    elif pid == "sporeveil":
        from .skins_sporeveil import _render_sporeveil_base
        _render_sporeveil_base(s, t, pulse)
    
    # 月蚀星骸 - Cthulhu
    elif pid == "cthulhu":
        from .skins_cthulhu import _render_cthulhu_base
        _render_cthulhu_base(s, t, pulse)
    
    # 巨石核拳 - Turu
    elif pid == "turu":
        from .skins_turu import _render_turu_base
        _render_turu_base(s, t, pulse)
    
    # 辉耀天女 - Staradia
    elif pid == "staradia":
        from .skins_staradia import _render_staradia_base
        _render_staradia_base(s, t, pulse)
    
    # 深渊龙鱼 - DukeFishron
    elif pid == "dukefishron":
        from .skins_dukefishron import draw_duke
        frame = int(t * 60) if t > 0 else 0
        draw_duke(s, c, 10, 10, 100, 100, frame, "duke_default")
    
    # 末世星凝 - Slime
    elif pid == "slime":
        from .skins_slime import draw_slime
        frame = int(t * 60) if t > 0 else 0
        draw_slime(s, c, 10, 10, 100, 100, frame, "default")
    
    # 终噬星链 - Oro
    elif pid == "oro":
        from .skins_oro import draw_oro
        frame = int(t * 60) if t > 0 else 0
        draw_oro(s, c, 10, 10, 100, 100, frame, "default")
    
    # 狱炎神龙 - Yharon
    elif pid == "yharon":
        from .skins_yharon import draw_yharon
        frame = int(t * 60) if t > 0 else 0
        draw_yharon(s, c, 10, 10, 100, 100, frame, "yharon_default")
    
    # 亵渎天神 - Providence
    elif pid == "providence":
        from .skins_providence import draw_providence
        frame = int(t * 60) if t > 0 else 0
        draw_providence(s, c, 10, 10, 100, 100, frame, "providence_default")
    
    # 瘟疫使者 - Goliath
    elif pid == "goliath":
        from .skins_goliath import draw_goliath
        frame = int(t * 60) if t > 0 else 0
        draw_goliath(s, c, 10, 10, 100, 100, frame, "goliath_default")
    
    # 至尊灾厄 - Sepulcher
    elif pid == "sepulcher":
        from .skins_sepulcher import get_sepulcher_theme
        frame = int(t * 60) if t > 0 else 0
        theme = get_sepulcher_theme("sepulcher_default")
        _draw_sepulcher_preview(s, c, 10, 10, 100, 100, frame, theme)
    
    # 宇宙之弧 - Galaxia
    elif pid == "galaxia":
        from .skins_galaxia import render_galaxia_plane
        frame = int(t * 60) if t > 0 else 0
        # 280x280的surface，中心区域100x100，留出90像素边距容纳2.0倍放大
        big_s = pygame.Surface((280, 280), pygame.SRCALPHA)
        render_galaxia_plane(big_s, c, 90, 90, 100, 100, frame, "galaxia_default")
        scaled = pygame.transform.smoothscale(big_s, (120, 120))
        s.blit(scaled, (0, 0))
    
    # 真理之书 - Magnus
    elif pid == "magnus":
        from .skins_magnus import render_magnus_plane
        frame = int(t * 60) if t > 0 else 0
        # 400x400的surface，中心区域100x100，留出150像素边距容纳2.3倍放大的所有视觉效果
        big_s = pygame.Surface((400, 400), pygame.SRCALPHA)
        render_magnus_plane(big_s, c, 150, 150, 100, 100, frame, "magnus_default")
        scaled = pygame.transform.smoothscale(big_s, (120, 120))
        s.blit(scaled, (0, 0))
    
    # 维那斯万岁 - Heavy Metal
    elif pid == "heavymetal":
        from .skins_heavymetal import _render_heavymetal_base
        _render_heavymetal_base(s, t, pulse)
    
    # 绯红恶魔 - Scarlet
    elif pid == "scarlet":
        from .skins_scarlet import _render_scarlet_base
        _render_scarlet_base(s, t, pulse)
    
    # 分形天顶 - Zenith
    elif pid == "zenith":
        from .skins_zenith import draw_zenith
        frame = int(t * 60) if t > 0 else 0
        draw_zenith(s, c, 10, 10, 100, 100, frame, "zenith_default")
    
    # 光之在解 - Viscerator
    elif pid == "viscerator":
        from .skins_viscerator import draw_viscerator_plane
        frame = int(t * 60) if t > 0 else 0
        draw_viscerator_plane(s, "viscerator_default", frame)
    
    # 晶体粉碎者 - Crusher
    elif pid == "crusher":
        from .skins_crusher import draw_crusher_plane
        frame = int(t * 60) if t > 0 else 0
        draw_crusher_plane(s, "crusher_default", frame)
    
    # 星际海豚 - SDMG
    elif pid == "sdmg":
        from .skins_sdmg import draw_sdmg
        frame = int(t * 60) if t > 0 else 0
        draw_sdmg(s, c, 10, 10, 100, 100, frame, "sdmg_default")
    
    else:
        # 默认占位图形
        pygame.draw.circle(s, c, (60, 60), 30)
        pygame.draw.circle(s, edge_color, (60, 60), 30, 2)
    
    return s


def _draw_sepulcher_preview(surface, color, x, y, w, h, frame, theme):
    """
    绘制至尊灾厄·终末王座的预览图
    调用skins_sepulcher的完整绘制函数
    """
    from utils.planes.skins_sepulcher import draw_sepulcher
    
    # 根据theme反查style
    style = "sepulcher_default"
    from utils.planes.skins_sepulcher import SEPULCHER_THEMES
    for key, val in SEPULCHER_THEMES.items():
        if val.get("armor") == theme.get("armor") and val.get("core") == theme.get("core"):
            style = key
            break
    
    draw_sepulcher(surface, color, x, y, w, h, frame, style)


def clear_plane_cache():
    """清空机体缓存"""
    global _plane_cache
    _plane_cache.clear()


__all__ = ['get_plane_surf', 'clear_plane_cache']
