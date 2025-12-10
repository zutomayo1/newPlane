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

所有机体涂装拆分完成！共计 208 种涂装。
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
    'render_pandemic_skin', 'is_pandemic_style', 'PANDEMIC_STYLES'
]
