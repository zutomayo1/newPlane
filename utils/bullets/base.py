# -*- coding: utf-8 -*-
"""
子弹涂装效果主调度模块

集中管理所有战机的子弹效果渲染，提供统一的 draw_bullet_preview 接口
"""
import pygame
import math

# 导入所有战机的子弹效果模块
from .striker_bullets import render_striker_bullet
from .phantom_bullets import render_phantom_bullet
from .titan_bullets import render_titan_bullet
from .thunderbird_bullets import render_thunderbird_bullet
from .viper_bullets import render_viper_bullet
from .specter_bullets import render_specter_bullet
from .aurora_bullets import render_aurora_bullet
from .crimson_bullets import render_crimson_bullet
from .stalker_bullets import render_stalker_bullet
from .gaia_bullets import render_gaia_bullet
from .weaver_bullets import render_weaver_bullet
from .solar_bullets import render_solar_bullet
from .arbiter_bullets import render_arbiter_bullet
from .eclipse_bullets import render_eclipse_bullet
from .prism_bullets import render_prism_bullet
from .necro_bullets import render_necro_bullet
from .wormhole_bullets import render_wormhole_bullet
from .chronos_bullets import render_chronos_bullet
from .mirage_bullets import render_mirage_bullet
from .gambit_bullets import render_gambit_bullet
from .puppeteer_bullets import render_puppeteer_bullet
from .pandemic_bullets import render_pandemic_bullet
from .omega_bullets import render_omega_bullet
from .genesis_bullets import render_genesis_bullet
from .asura_bullets import render_asura_bullet
from .dragoon_bullets import render_dragoon_bullet
from .origami_bullets import render_origami_bullet
# 导入新机体子弹效果模块
from .thornvine_bullets import render_thornvine_bullet
from .starblade_bullets import render_starblade_bullet
from .acidswamp_bullets import render_acidswamp_bullet
from .crystalfall_bullets import render_crystalfall_bullet
from .sporeveil_bullets import render_sporeveil_bullet
from .cthulhu_bullets import render_cthulhu_bullet  # 月蚀星骸·克苏鲁
from .turu_bullets import render_turu_bullet  # 巨石核拳·图鲁
from .staradia_bullets import render_staradia_bullet_preview  # 辉耀天女·斯塔德
from .dukefishron_bullets import render_dukefishron_bullet_preview  # 深渊龙鱼·猪公爵
from .slime_bullets import render_slime_bullet_preview  # 末世星凝·史莱姆
from .providence_bullets import render_providence_bullet_preview  # 亵渎天神·普罗维登斯
from .scarlet_bullets import render_scarlet_bullet  # 绯红恶魔·SCARLET


# 渲染函数列表，按优先级顺序排列（终极机体优先）
BULLET_RENDERERS = [
    render_omega_bullet,      # [终极机体] Omega
    render_genesis_bullet,    # [终极机体] Genesis
    render_striker_bullet,
    render_phantom_bullet,
    render_titan_bullet,
    render_thunderbird_bullet,
    render_viper_bullet,
    render_specter_bullet,
    render_aurora_bullet,
    render_crimson_bullet,
    render_stalker_bullet,
    render_gaia_bullet,
    render_weaver_bullet,
    render_solar_bullet,
    render_arbiter_bullet,
    render_eclipse_bullet,
    render_prism_bullet,
    render_necro_bullet,
    render_wormhole_bullet,
    render_chronos_bullet,
    render_mirage_bullet,
    render_gambit_bullet,
    render_puppeteer_bullet,
    render_pandemic_bullet,
    render_asura_bullet,
    render_dragoon_bullet,
    render_origami_bullet,    # [特殊机体] Origami 折纸鹤·零式
    # 新增5个机体的子弹渲染
    render_thornvine_bullet,   # 棘刺藤骨·荆穹
    render_starblade_bullet,   # 浮游刃环·星镰
    render_acidswamp_bullet,   # 酸蚀喷溅·腐沼
    render_crystalfall_bullet, # 晶簇射流·晶瀑
    render_sporeveil_bullet,   # 孢子幕炮·菌幕
    render_cthulhu_bullet,     # [终极机体] 月蚀星骸·克苏鲁
    render_turu_bullet,        # [终极机体] 巨石核拳·图鲁
    render_staradia_bullet_preview,  # [至尊机体] 辉耀天女·斯塔德
    render_dukefishron_bullet_preview,  # [至尊机体] 深渊龙鱼·猪公爵
    render_slime_bullet_preview,  # [至尊机体] 末世星凝·史莱姆
    render_providence_bullet_preview,  # [至尊机体] 亵渎天神·普罗维登斯
    render_scarlet_bullet,  # [吸血鬼机体] 绯红恶魔·SCARLET
]


def draw_bullet_preview(surface, theme, x, y, size=60, plane_id=None):
    """
    绘制子弹预览效果
    
    Args:
        surface: pygame绘图表面
        theme: 主题字典，包含 'effects' 和 'color' 键
        x, y: 绘制位置（左上角）
        size: 预览尺寸
        plane_id: 机体ID，用于判断是否渲染该机体的默认子弹样式
    """
    try:
        effects = theme.get("effects", [])
        color = theme.get("color", (100, 150, 255))
        
        # 计算中心坐标
        center_x = x + size // 2
        center_y = y + size // 2
        
        # 遍历所有渲染器，找到匹配的效果
        rendered = False
        for renderer in BULLET_RENDERERS:
            # 尝试传入plane_id参数（新版渲染器支持）
            try:
                if renderer(surface, effects, color, center_x, center_y, size, x, y, plane_id=plane_id):
                    rendered = True
                    break
            except TypeError:
                # 旧版渲染器不支持plane_id参数
                if renderer(surface, effects, color, center_x, center_y, size, x, y):
                    rendered = True
                    break
        
        # 如果没有匹配的效果，绘制默认圆形
        if not rendered:
            pygame.draw.circle(surface, color, (center_x, center_y), size//3)
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), size//3, 2)
        
        # 在周围绘制小光点作为装饰
        for i in range(3):
            angle = (i * 120) * 3.14159 / 180
            px = center_x + int(size//2.2 * math.cos(angle))
            py = center_y + int(size//2.2 * math.sin(angle))
            pygame.draw.circle(surface, color, (px, py), 3)
            pygame.draw.circle(surface, (255, 255, 255), (px, py), 3, 1)
                
    except Exception as e:
        # 渲染失败时显示灰色圆形
        pygame.draw.circle(surface, (100, 100, 100), (x + size//2, y + size//2), size//4)
