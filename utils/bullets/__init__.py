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
- origami_bullets.py: Origami子弹涂装 [折纸鹤机体]
- thornvine_bullets.py: Thornvine子弹涂装 [棘刺藤骨]
- starblade_bullets.py: Starblade子弹涂装 [浮游刃环]
- acidswamp_bullets.py: Acidswamp子弹涂装 [酸蚀喷溅]
- crystalfall_bullets.py: Crystalfall子弹涂装 [晶簇射流]
- sporeveil_bullets.py: Sporeveil子弹涂装 [孢子幕炮]
- cthulhu_bullets.py: Cthulhu子弹涂装 [月蚀星骸·克苏鲁]
- turu_bullets.py: Turu子弹涂装 [巨石核拳·图鲁]
- staradia_bullets.py: Staradia子弹涂装 [辉耀天女·斯塔德]
- dukefishron_bullets.py: DukeFishron子弹涂装 [深渊龙鱼·猪公爵]
- slime_bullets.py: Slime子弹涂装 [末世星凝·史莱姆]
- oro_bullets.py: Oro子弹涂装 [终噬星链·奥罗]
- yharon_bullets.py: Yharon子弹涂装 [狱炎神龙·犽戎]
"""

from .base import draw_bullet_preview
from .asura_bullets import render_asura_bullet, ASURA_BULLET_THEMES
from .dragoon_bullets import render_dragoon_bullet, DRAGOON_BULLET_THEMES
from .origami_bullets import OrigamiBlade, OrigamiCrane, FeatherWall, CraneBullet
from .thornvine_bullets import render_thornvine_bullet
from .starblade_bullets import render_starblade_bullet
from .acidswamp_bullets import render_acidswamp_bullet
from .crystalfall_bullets import render_crystalfall_bullet
from .sporeveil_bullets import render_sporeveil_bullet
from .cthulhu_bullets import render_cthulhu_bullet, CTHULHU_BULLET_THEMES
from .turu_bullets import render_turu_bullet
from .staradia_bullets import render_staradia_bullet, STARADIA_BULLET_THEMES, MoonRainbowShuttle, RadiantRemnant, MoonlightBullet, RadiantBeam, RadiantStorm, MoonRainbowRail, RadiantDomain, RainbowCrash, spawn_rainbow_crash
from .dukefishron_bullets import DUKE_BULLET_THEMES, AbyssSpear, SharkTornado, MiniSharkBullet, AbyssBubblePickup, WaveTrail, SharkTornadoStorm, AbyssBubbleStorm, DragonFishTsunami, TsunamiWall, DukeKillEffect, spawn_duke_kill_effect
from .slime_bullets import (SLIME_BULLET_THEMES, StarGelBullet, GravityDomain, 
                            MiniStarGelBullet, GelCoreBullet, StarGelPickup,
                            StarStompSkill, AstralCrystalSkill, AureusSpawnSkill,
                            StarSlimeDownEffect)
from .oro_bullets import (ORO_BULLET_THEMES, VoidChainBullet, ChainNode, LaserGrid,
                          ChainExplosion, VoidCorePickup, DimensionGridSkill, ShatterEffect,
                          GodSlayerSkill, RealityRift, OuroborosSkill,
                          render_oro_bullet_preview)
from .yharon_bullets import (YHARON_THEMES, FlareStreamBullet, EmberSpark, BorderDrone,
                             BorderBullet, DragonDashSkill, DraconicTornado, JungleBreath,
                             PoisonCloud, GigaNukeSkill, DraconicSwarmSkill, Bumblebirb,
                             BumblebirbBullet, EnemyAscendedSkill, HellFirePillar,
                             render_yharon_bullet_preview)

__all__ = ['draw_bullet_preview', 'render_asura_bullet', 'ASURA_BULLET_THEMES', 
           'render_dragoon_bullet', 'DRAGOON_BULLET_THEMES',
           'OrigamiBlade', 'OrigamiCrane', 'FeatherWall', 'CraneBullet',
           'render_thornvine_bullet', 'render_starblade_bullet',
           'render_acidswamp_bullet', 'render_crystalfall_bullet',
           'render_sporeveil_bullet', 'render_cthulhu_bullet', 'CTHULHU_BULLET_THEMES',
           'render_turu_bullet', 'render_staradia_bullet', 'STARADIA_BULLET_THEMES',
           'MoonRainbowShuttle', 'RadiantRemnant', 'MoonlightBullet', 'RadiantBeam',
           'RadiantStorm', 'MoonRainbowRail', 'RadiantDomain', 'RainbowCrash', 'spawn_rainbow_crash',
           'DUKE_BULLET_THEMES', 'AbyssSpear', 'SharkTornado', 'MiniSharkBullet', 
           'AbyssBubblePickup', 'WaveTrail', 'SharkTornadoStorm', 'AbyssBubbleStorm',
           'DragonFishTsunami', 'TsunamiWall', 'DukeKillEffect', 'spawn_duke_kill_effect',
           'SLIME_BULLET_THEMES', 'StarGelBullet', 'GravityDomain', 'MiniStarGelBullet',
           'GelCoreBullet', 'StarGelPickup', 'StarStompSkill', 'AstralCrystalSkill',
           'AureusSpawnSkill', 'StarSlimeDownEffect',
           'ORO_BULLET_THEMES', 'VoidChainBullet', 'ChainNode', 'LaserGrid',
           'ChainExplosion', 'VoidCorePickup', 'DimensionGridSkill', 'ShatterEffect',
           'GodSlayerSkill', 'RealityRift', 'OuroborosSkill', 'render_oro_bullet_preview',
           'YHARON_THEMES', 'FlareStreamBullet', 'EmberSpark', 'BorderDrone',
           'BorderBullet', 'DragonDashSkill', 'DraconicTornado', 'JungleBreath',
           'PoisonCloud', 'GigaNukeSkill', 'DraconicSwarmSkill', 'Bumblebirb',
           'BumblebirbBullet', 'EnemyAscendedSkill', 'HellFirePillar',
           'render_yharon_bullet_preview']
