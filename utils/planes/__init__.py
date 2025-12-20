"""
机体渲染包 - 所有机体外观渲染的统一入口

已完成拆分：
- base.py: 缓存和入口函数
- tier1.py: T1基础机体 (9种)
- tier2.py: T2进阶机体 (4种)  
- tier3.py: T3高级机体 (4种)
- special.py: 特殊机体 (3种: chronos, mirage, gambit)
- hidden.py: 隐藏机体 (2种: puppeteer, pandemic)
- skins_mk2.py: MK2涂装 (16种)
- skins_striker.py: Striker专属涂装 (14种)
- skins_phantom.py: Phantom专属涂装 (11种)
- skins_titan.py: Titan专属涂装 (7种)
- skins_thunderbird.py: Thunderbird专属涂装 (7种)
- skins_viper.py: Viper专属涂装 (7种)
- skins_specter.py: Specter专属涂装 (7种)
- skins_aurora.py: Aurora专属涂装 (6种)
- skins_crimson.py: Crimson专属涂装 (7种)
- skins_stalker.py: Stalker专属涂装 (7种)
- skins_gaia.py: Gaia专属涂装 (7种)
- skins_weaver.py: Weaver专属涂装 (5种)
- skins_solar.py: Solar专属涂装 (7种)
- skins_arbiter.py: Arbiter专属涂装 (7种)
- skins_eclipse.py: Eclipse专属涂装 (7种)
- skins_prism.py: Prism专属涂装 (7种)
- skins_necro.py: Necro专属涂装 (7种)
- skins_wormhole.py: Wormhole专属涂装 (12种)
- skins_chronos.py: Chronos专属涂装 (12种)
- skins_mirage.py: Mirage专属涂装 (12种)
- skins_gambit.py: Gambit专属涂装 (12种)
- skins_puppeteer.py: Puppeteer专属涂装 (12种)
- skins_pandemic.py: Pandemic专属涂装 (12种)
- skins_omega.py: Omega专属涂装 (12种) [终极机体]
- skins_genesis.py: Genesis专属涂装 (12种) [终极机体]
- skins_truth.py: Truth专属涂装 (10种) [终极机体]
- skins_asura.py: Asura专属涂装 (10种) [近战机体]
- skins_dragoon.py: Dragoon专属涂装 (10种) [近战机体]
- skins_origami.py: Origami专属涂装 (12种) [折纸鹤机体]
- skins_helios.py: Helios专属涂装 (12种) [远程狙击机体]
- skins_frostflare.py: Frostflare专属涂装 (12种) [远程狙击机体]
- skins_nova.py: Nova专属涂装 (12种) [远程狙击机体]
- skins_spectrum.py: Spectrum专属涂装 (12种) [远程狙击机体]
- skins_darkstring.py: Darkstring专属涂装 (12种) [远程狙击机体]
- skins_cthulhu.py: Cthulhu专属涂装 (12种) [月蚀星骸·克苏鲁]
- skins_turu.py: Turu专属涂装 (12种) [巨石核拳·图鲁]
- skins_staradia.py: Staradia专属涂装 (12种) [辉耀天女·斯塔德]
- skins_dukefishron.py: DukeFishron专属涂装 (6种) [深渊龙鱼·猪公爵]
- skins_slime.py: Slime专属涂装 (12种) [末世星凝·史莱姆]
- skins_oro.py: Oro专属涂装 (12种) [终噬星链·奥罗]
- skins_yharon.py: Yharon专属涂装 (12种) [狱炎神龙·犽戎]
- skins_providence.py: Providence专属涂装 (12种) [亵渎天神·普罗维登斯]
- skins_heavymetal.py: HeavyMetal专属涂装 (12种) [维那斯万岁·HEAVY METAL]

所有机体涂装拆分完成！共计 417 种涂装。
"""

from .base import get_plane_surf, clear_plane_cache
from .tier1 import render_tier1
from .tier2 import render_tier2
from .tier3 import render_tier3
from .special import render_special
from .hidden import render_hidden
from .skins_mk2 import render_mk2_skin, is_mk2_style, MK2_STYLES
from .skins_striker import render_striker_skin, is_striker_style, STRIKER_STYLES
from .skins_phantom import render_phantom_skin, is_phantom_style, PHANTOM_STYLES
from .skins_titan import render_titan_skin, is_titan_style, TITAN_STYLES
from .skins_thunderbird import render_thunderbird_skin, is_thunderbird_style, THUNDERBIRD_STYLES
from .skins_viper import render_viper_skin, is_viper_style, VIPER_STYLES
from .skins_specter import render_specter_skin, is_specter_style, SPECTER_STYLES
from .skins_aurora import render_aurora_skin, is_aurora_style, AURORA_STYLES
from .skins_crimson import render_crimson_skin, is_crimson_style, CRIMSON_STYLES
from .skins_stalker import render_stalker_skin, is_stalker_style, STALKER_STYLES
from .skins_gaia import render_gaia_skin, is_gaia_style, GAIA_STYLES
from .skins_weaver import render_weaver_skin, is_weaver_style, WEAVER_STYLES
from .skins_solar import render_solar_skin, is_solar_style, SOLAR_STYLES
from .skins_arbiter import render_arbiter_skin, is_arbiter_style, ARBITER_STYLES
from .skins_eclipse import render_eclipse_skin, is_eclipse_style, ECLIPSE_STYLES
from .skins_prism import render_prism_skin, is_prism_style, PRISM_STYLES
from .skins_necro import render_necro_skin, is_necro_style, NECRO_STYLES
from .skins_wormhole import render_wormhole_skin, is_wormhole_style, WORMHOLE_STYLES
from .skins_chronos import render_chronos_skin, is_chronos_style, CHRONOS_STYLES
from .skins_mirage import render_mirage_skin, is_mirage_style, MIRAGE_STYLES
from .skins_gambit import render_gambit_skin, is_gambit_style, GAMBIT_STYLES
from .skins_puppeteer import render_puppeteer_skin, is_puppeteer_style, PUPPETEER_STYLES
from .skins_pandemic import render_pandemic_skin, is_pandemic_style, PANDEMIC_STYLES
from .skins_omega import render_omega_skin, is_omega_style, OMEGA_STYLES
from .skins_genesis import render_genesis_skin, is_genesis_style, GENESIS_STYLES
from .skins_truth import render_truth_skin, is_truth_style, TRUTH_STYLES
from .skins_asura import render_asura_skin, is_asura_style, ASURA_STYLES
from .skins_dragoon import render_dragoon_skin, is_dragoon_style, DRAGOON_STYLES
from .skins_origami import render_origami_skin, is_origami_style, ORIGAMI_STYLES
from .skins_helios import render_helios_skin, is_helios_style, HELIOS_STYLES
from .skins_frostflare import render_frostflare_skin, is_frostflare_style, FROSTFLARE_STYLES
from .skins_nova import render_nova_skin, is_nova_style, NOVA_STYLES
from .skins_spectrum import render_spectrum_skin, is_spectrum_style, SPECTRUM_STYLES
from .skins_darkstring import render_darkstring_skin, is_darkstring_style, DARKSTRING_STYLES
from .skins_cthulhu import render_cthulhu_skin, is_cthulhu_style, CTHULHU_STYLES
from .skins_turu import render_turu_skin, is_turu_style, TURU_STYLES
from .skins_staradia import render_staradia_skin, is_staradia_style, STARADIA_STYLES
from .skins_dukefishron import draw_duke
from .skins_slime import draw_slime, is_slime_style, render_slime_skin, SLIME_STYLES
from .skins_oro import draw_oro, is_oro_style, render_oro_skin, ORO_STYLES
from .skins_yharon import draw_yharon, is_yharon_style, render_yharon_skin, YHARON_STYLES
from .skins_providence import draw_providence, is_providence_style, render_providence_skin, PROVIDENCE_STYLES
from .skins_galaxia import render_galaxia_plane, is_galaxia_style, get_galaxia_theme, get_all_galaxia_styles, GALAXIA_THEMES
from .skins_magnus import render_magnus_plane, is_magnus_style, get_magnus_theme, get_all_magnus_styles, MAGNUS_THEMES
from .skins_heavymetal import render_heavymetal_plane, render_heavymetal_skin, is_heavymetal_style, get_heavymetal_theme, get_all_heavymetal_styles, HEAVYMETAL_THEMES, HEAVYMETAL_STYLES, draw_heavymetal, _render_heavymetal_base
from .skins_scarlet import render_scarlet_skin, is_scarlet_style, SCARLET_STYLES, _render_scarlet_base, get_scarlet_theme
from .skins_zenith import draw_zenith, is_zenith_style, render_zenith_skin, ZENITH_STYLES, get_zenith_theme

# DukeFishron样式定义 - 12个高质量涂装（带duke_前缀避免冲突）
DUKEFISHRON_STYLES = [
    "duke_default", "duke_abyss", "duke_rage", "duke_storm", "duke_coral", "duke_void_sea",
    "duke_tsunami", "duke_phantom", "duke_blood_moon", "duke_tropical", "duke_frost", "duke_golden"
]

def is_dukefishron_style(style):
    return style in DUKEFISHRON_STYLES

def render_dukefishron_skin(surface, color, x, y, w, h, frame, style):
    draw_duke(surface, color, x, y, w, h, frame, style)

__all__ = [
    'get_plane_surf', 'clear_plane_cache',
    'render_tier1', 'render_tier2', 'render_tier3', 'render_special', 'render_hidden',
    'render_mk2_skin', 'is_mk2_style', 'MK2_STYLES',
    'render_striker_skin', 'is_striker_style', 'STRIKER_STYLES',
    'render_phantom_skin', 'is_phantom_style', 'PHANTOM_STYLES',
    'render_titan_skin', 'is_titan_style', 'TITAN_STYLES',
    'render_thunderbird_skin', 'is_thunderbird_style', 'THUNDERBIRD_STYLES',
    'render_viper_skin', 'is_viper_style', 'VIPER_STYLES',
    'render_specter_skin', 'is_specter_style', 'SPECTER_STYLES',
    'render_aurora_skin', 'is_aurora_style', 'AURORA_STYLES',
    'render_crimson_skin', 'is_crimson_style', 'CRIMSON_STYLES',
    'render_stalker_skin', 'is_stalker_style', 'STALKER_STYLES',
    'render_gaia_skin', 'is_gaia_style', 'GAIA_STYLES',
    'render_weaver_skin', 'is_weaver_style', 'WEAVER_STYLES',
    'render_solar_skin', 'is_solar_style', 'SOLAR_STYLES',
    'render_arbiter_skin', 'is_arbiter_style', 'ARBITER_STYLES',
    'render_eclipse_skin', 'is_eclipse_style', 'ECLIPSE_STYLES',
    'render_prism_skin', 'is_prism_style', 'PRISM_STYLES',
    'render_necro_skin', 'is_necro_style', 'NECRO_STYLES',
    'render_wormhole_skin', 'is_wormhole_style', 'WORMHOLE_STYLES',
    'render_chronos_skin', 'is_chronos_style', 'CHRONOS_STYLES',
    'render_mirage_skin', 'is_mirage_style', 'MIRAGE_STYLES',
    'render_gambit_skin', 'is_gambit_style', 'GAMBIT_STYLES',
    'render_puppeteer_skin', 'is_puppeteer_style', 'PUPPETEER_STYLES',
    'render_pandemic_skin', 'is_pandemic_style', 'PANDEMIC_STYLES',
    'render_omega_skin', 'is_omega_style', 'OMEGA_STYLES',
    'render_genesis_skin', 'is_genesis_style', 'GENESIS_STYLES',
    'render_truth_skin', 'is_truth_style', 'TRUTH_STYLES',
    'render_asura_skin', 'is_asura_style', 'ASURA_STYLES',
    'render_dragoon_skin', 'is_dragoon_style', 'DRAGOON_STYLES',
    'render_origami_skin', 'is_origami_style', 'ORIGAMI_STYLES',
    'render_helios_skin', 'is_helios_style', 'HELIOS_STYLES',
    'render_frostflare_skin', 'is_frostflare_style', 'FROSTFLARE_STYLES',
    'render_nova_skin', 'is_nova_style', 'NOVA_STYLES',
    'render_spectrum_skin', 'is_spectrum_style', 'SPECTRUM_STYLES',
    'render_darkstring_skin', 'is_darkstring_style', 'DARKSTRING_STYLES',
    'render_cthulhu_skin', 'is_cthulhu_style', 'CTHULHU_STYLES',
    'render_turu_skin', 'is_turu_style', 'TURU_STYLES',
    'render_staradia_skin', 'is_staradia_style', 'STARADIA_STYLES',
    'render_dukefishron_skin', 'is_dukefishron_style', 'DUKEFISHRON_STYLES', 'draw_duke',
    'render_slime_skin', 'is_slime_style', 'SLIME_STYLES', 'draw_slime',
    'render_oro_skin', 'is_oro_style', 'ORO_STYLES', 'draw_oro',
    'render_yharon_skin', 'is_yharon_style', 'YHARON_STYLES', 'draw_yharon',
    'render_providence_skin', 'is_providence_style', 'PROVIDENCE_STYLES', 'draw_providence',
    'render_galaxia_plane', 'is_galaxia_style', 'get_galaxia_theme', 'get_all_galaxia_styles', 'GALAXIA_THEMES',
    'render_magnus_plane', 'is_magnus_style', 'get_magnus_theme', 'get_all_magnus_styles', 'MAGNUS_THEMES',
    'render_heavymetal_plane', 'render_heavymetal_skin', 'is_heavymetal_style', 'get_heavymetal_theme', 'get_all_heavymetal_styles', 'HEAVYMETAL_THEMES', 'HEAVYMETAL_STYLES', 'draw_heavymetal', '_render_heavymetal_base',
    'render_scarlet_skin', 'is_scarlet_style', 'SCARLET_STYLES', '_render_scarlet_base', 'get_scarlet_theme',
    'render_zenith_skin', 'is_zenith_style', 'ZENITH_STYLES', 'draw_zenith', 'get_zenith_theme'
]
