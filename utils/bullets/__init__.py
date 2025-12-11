"""
子弹涂装渲染包 - 所有子弹外观渲染的统一入口

模块列表:
- base.py: 入口函数和默认渲染
- striker_bullets.py: Striker子弹涂装
- phantom_bullets.py: Phantom子弹涂装
- titan_bullets.py: Titan子弹涂装
- thunderbird_bullets.py: Thunderbird子弹涂装
- viper_bullets.py: Viper子弹涂装
- specter_bullets.py: Specter子弹涂装
- aurora_bullets.py: Aurora子弹涂装
- crimson_bullets.py: Crimson子弹涂装
- stalker_bullets.py: Stalker子弹涂装
- gaia_bullets.py: Gaia子弹涂装
- weaver_bullets.py: Weaver子弹涂装
- solar_bullets.py: Solar子弹涂装
- arbiter_bullets.py: Arbiter子弹涂装
- eclipse_bullets.py: Eclipse子弹涂装
- prism_bullets.py: Prism子弹涂装
- necro_bullets.py: Necro子弹涂装
- wormhole_bullets.py: Wormhole子弹涂装
- chronos_bullets.py: Chronos子弹涂装
- mirage_bullets.py: Mirage子弹涂装
- gambit_bullets.py: Gambit子弹涂装
- puppeteer_bullets.py: Puppeteer子弹涂装
- pandemic_bullets.py: Pandemic子弹涂装
- omega_bullets.py: Omega子弹涂装 [终极机体]
- genesis_bullets.py: Genesis子弹涂装 [终极机体]
- truth_bullets.py: Truth子弹涂装 [终极机体]
- asura_bullets.py: Asura子弹涂装 [近战机体]
- dragoon_bullets.py: Dragoon子弹涂装 [近战机体]
"""

from .base import draw_bullet_preview
from .asura_bullets import render_asura_bullet, ASURA_BULLET_THEMES
from .dragoon_bullets import render_dragoon_bullet, DRAGOON_BULLET_THEMES

__all__ = ['draw_bullet_preview', 'render_asura_bullet', 'ASURA_BULLET_THEMES', 
           'render_dragoon_bullet', 'DRAGOON_BULLET_THEMES']
