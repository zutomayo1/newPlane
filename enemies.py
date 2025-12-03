"""
敌人系统 - 模块化敌人管理
提供配置驱动的敌人创建和AI系统
"""
import pygame
import math
import random
from config import *

# 直接使用config中的全局sprite组（避免循环导入）
# 这些已在config.py中定义：all_sprites, mobs, bullets, enemy_bullets

# Bullet类延迟导入（避免循环导入）
_Bullet = None

def _get_bullet_class():
    """延迟导入Bullet类"""
    global _Bullet
    if _Bullet is None:
        from sprites import Bullet
        _Bullet = Bullet
    return _Bullet

def init_enemy_system():
    """
    初始化敌人系统
    注意：sprite组直接使用config.py中的全局变量，无需传入
    """
    pass  # 保留此函数以保持API一致性


class Enemy(pygame.sprite.Sprite):
    """
    敌人基类
    支持配置驱动和自定义AI行为
    """
    
    def __init__(self, enemy_type, config=None, spawn_pos=None):
        """
        初始化敌人
        
        Args:
            enemy_type: 敌人类型ID
            config: 配置字典，可选
            spawn_pos: 生成位置 (x, y)，可选
        """
        super().__init__()
        
        # 添加到sprite组（使用config中的全局组）
        all_sprites.add(self)
        mobs.add(self)
        
        # 基础属性
        self.type = enemy_type
        self.config = config or {}
        self.frozen_timer = 0
        self.timer = 0
        self.state = "move"
        
        # 从配置加载属性
        self.hp = self.config.get('hp', 50)
        self.max_hp = self.hp
        self.base_speed = self.config.get('speed', 2.0)
        self.speed = self.base_speed
        self.radius = self.config.get('radius', 20)
        self.score = self.config.get('score', 100)
        
        # 精英系统
        self.is_elite = False
        self.affix = None
        elite_chance = self.config.get('elite_chance', 0.1)
        if random.random() < elite_chance:
            self._make_elite()
        
        # 创建图像
        self._create_image()
        
        # 设置位置
        self.rect = self.image.get_rect()
        if spawn_pos:
            self.rect.x, self.rect.y = spawn_pos
        else:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
        
        # AI行为
        self.ai_behavior = self.config.get('ai_behavior', 'straight')
        self.attack_pattern = self.config.get('attack_pattern', None)
        self.movement_data = {}  # 存储AI需要的额外数据
        
        # 向后兼容属性（原系统可能用到）
        self.neon_color = self.config.get('color', (255, 100, 100))
    
    def _make_elite(self):
        """将敌人变为精英"""
        self.is_elite = True
        self.hp = int(self.hp * 3)
        self.max_hp = self.hp
        self.affix = random.choice(['fast', 'tank', 'split'])
        
        if self.affix == 'fast':
            self.base_speed *= 1.5
            self.speed *= 1.5
        elif self.affix == 'tank':
            self.hp = int(self.hp * 2)
            self.max_hp = self.hp
            self.radius = int(self.radius * 1.3)
    
    def _create_image(self):
        """根据敌人类型创建精细的建模图像"""
        size = 70 if self.is_elite else 50
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        enemy_type = self.type
        color = self.config.get('color', (255, 100, 100))
        
        if self.is_elite:
            self._draw_elite_enemy(size, center, color)
        else:
            # 根据敌人类型调用专门的绘制方法
            if enemy_type == 'scout_moth':
                self._draw_scout_moth(size, center, color)
            elif enemy_type == 'trooper_spear':
                self._draw_trooper_spear(size, center, color)
            elif enemy_type == 'lurker_halo':
                self._draw_lurker_halo(size, center, color)
            elif enemy_type == 'bomber_deepjelly':
                self._draw_bomber_deepjelly(size, center, color)
            elif enemy_type == 'jammer_amethyst':
                self._draw_jammer_amethyst(size, center, color)
            elif enemy_type == 'shield_beeguard':
                self._draw_shield_beeguard(size, center, color)
            elif enemy_type in ['splitter_azurecore', 'sniper_blackneedle', 'weaver_dualwasp',
                               'summoner_nethalo', 'prism_voidprism', 'guard_heavyanvil',
                               'nestlord_livestarport', 'weaver_dimensionspindle', 'judge_dualpolar',
                               'annihilator_soleye', 'chaos_discordantprism', 'phantom_voidstrider']:
                self._draw_advanced_enemy(size, center, color, enemy_type)
            else:
                self._draw_default_enemy(size, center, color)
        
        # 储存用于动画的初始数据
        self.animation_time = 0
    
    def _draw_elite_enemy(self, size, center, color):
        """绘制精英敌人：金色多层星形"""
        # 多层圆形
        pygame.draw.circle(self.image, (255, 200, 0), (center, center), center-3, 0)
        pygame.draw.circle(self.image, (255, 150, 0), (center, center), center-6, 3)
        pygame.draw.circle(self.image, (200, 100, 50), (center, center), center-10, 2)
        pygame.draw.circle(self.image, (255, 200, 0), (center, center), center-12, 1)
        
        # 星形光芒
        for i in range(12):
            angle = i * 30
            rad = math.radians(angle)
            x = center + int((center-8) * math.cos(rad))
            y = center + int((center-8) * math.sin(rad))
            pygame.draw.circle(self.image, (255, 255, 150), (x, y), 3)
    
    def _draw_scout_moth(self, size, center, color):
        """侦察机·灰蛾：精细三角形机体+结构细节"""
        # 主体：不等边三角形（更精细）
        triangle = [
            (center, 5),           # 尖锐前缘
            (size-5, size-5),      # 右下
            (5, size-5)            # 左下
        ]
        
        # 分层结构：主装甲
        pygame.draw.polygon(self.image, color, triangle)
        
        # 装甲分割线（中线）
        pygame.draw.line(self.image, (80, 80, 80), (center, 5), (center, size-5), 1)
        
        # 左右侧装甲分色
        left_tri = [(center, 5), (center, size-5), (5, size-5)]
        right_tri = [(center, 5), (size-5, size-5), (center, size-5)]
        pygame.draw.polygon(self.image, tuple(c-10 if c > 10 else 0 for c in color), left_tri, 0)
        
        # 焊接纹路（多层）
        for i in range(5):
            offset_y = 8 + i * 6
            offset_x_left = (offset_y - 5) * 0.3
            offset_x_right = -(offset_y - 5) * 0.3
            pygame.draw.line(self.image, (100, 100, 100), 
                           (center-offset_x_left-2, offset_y), (center+offset_x_right+2, offset_y), 1)
        
        # 铆钉纹理（小圆点）
        for i in range(2):
            for j in range(3):
                rivet_x = center - 6 + i * 12 + (j % 2) * 6
                rivet_y = 10 + j * 8
                if 5 < rivet_x < size-5 and 5 < rivet_y < size-5:
                    pygame.draw.circle(self.image, (80, 80, 80), (rivet_x, rivet_y), 1)
        
        # 喷口纹理（尾部）
        pygame.draw.rect(self.image, (30, 30, 30), (center-2, size-8, 4, 3))
        pygame.draw.circle(self.image, (50, 50, 50), (center, size-5), 1)
        
        # 边框
        pygame.draw.polygon(self.image, (100, 150, 200), triangle, 2)
        
        # 红色扫描灯（中心）
        pygame.draw.circle(self.image, (255, 100, 100), (center, center), 3)
        pygame.draw.circle(self.image, (255, 50, 50), (center, center), 1)
    
    def _draw_trooper_spear(self, size, center, color):
        """突击兵·赤矛：复杂X型战斗机+多部件"""
        # 主机身（圆柱形）
        pygame.draw.ellipse(self.image, color, (center-4, center-10, 8, 18))
        pygame.draw.ellipse(self.image, tuple(c-20 if c > 20 else 0 for c in color), 
                          (center-4, center-10, 8, 18), 2)
        
        # 机身中线（金属反光）
        pygame.draw.line(self.image, (150, 150, 150), (center, center-10), (center, center+8), 1)
        
        # X型双翼（双层结构）
        wing_offset = 9
        wing_base_y = center - 2
        
        # 上翼
        pygame.draw.line(self.image, color, (center-wing_offset, wing_base_y-3), 
                        (center+wing_offset, wing_base_y-3), 4)
        pygame.draw.line(self.image, (100, 150, 200), (center-wing_offset, wing_base_y-3), 
                        (center+wing_offset, wing_base_y-3), 1)
        
        # 下翼
        pygame.draw.line(self.image, color, (center-wing_offset, wing_base_y+3), 
                        (center+wing_offset, wing_base_y+3), 4)
        pygame.draw.line(self.image, (100, 150, 200), (center-wing_offset, wing_base_y+3), 
                        (center+wing_offset, wing_base_y+3), 1)
        
        # 翼端燃料罐（方形）
        tank_size = 3
        for x_pos in [center-wing_offset, center+wing_offset]:
            for y_pos in [wing_base_y-3, wing_base_y+3]:
                pygame.draw.rect(self.image, (50, 50, 50), (x_pos-tank_size, y_pos-tank_size, tank_size*2, tank_size*2))
        
        # 双管机炮（机头）
        pygame.draw.circle(self.image, (40, 40, 40), (center, 4), 2)
        pygame.draw.circle(self.image, (20, 20, 20), (center-1.5, 4), 0.8)
        pygame.draw.circle(self.image, (20, 20, 20), (center+1.5, 4), 0.8)
        pygame.draw.circle(self.image, (80, 80, 80), (center, 4), 2, 1)
        
        # 尾部推进器（环形）
        pygame.draw.circle(self.image, (100, 80, 0), (center, size-5), 3, 1)
        pygame.draw.circle(self.image, (200, 150, 50), (center, size-5), 2, 1)
        
        # 机体分割线
        pygame.draw.line(self.image, (80, 80, 80), (center, center-10), (center, center+8), 1)
    
    def _draw_lurker_halo(self, size, center, color):
        """徘徊者·光环盘：精细八边形核心+多层光环+扫描阵列"""
        # 核心舱（正八边形，分层）
        angles = [i * 45 for i in range(8)]
        core_points = [(center + 8 * math.cos(math.radians(a)), 
                       center + 8 * math.sin(math.radians(a))) for a in angles]
        
        # 外层装甲
        pygame.draw.polygon(self.image, color, core_points)
        pygame.draw.polygon(self.image, (100, 200, 150), core_points, 2)
        
        # 内层核心（略小）
        inner_core = [(center + 5 * math.cos(math.radians(a)), 
                       center + 5 * math.sin(math.radians(a))) for a in angles]
        pygame.draw.polygon(self.image, tuple(c+30 if c < 225 else 255 for c in color), inner_core, 1)
        
        # 内部光路纹理
        for i in range(4):
            angle = i * 90
            rad = math.radians(angle)
            x = center + 4 * math.cos(rad)
            y = center + 4 * math.sin(rad)
            pygame.draw.line(self.image, (100, 150, 100), (center, center), (int(x), int(y)), 1)
        
        # 多层光环（金属材质）
        pygame.draw.circle(self.image, (100, 200, 255), (center, center), 15, 2)
        pygame.draw.circle(self.image, (80, 180, 200), (center, center), 14, 1)
        pygame.draw.circle(self.image, (100, 200, 255), (center, center), 13, 1)
        
        # 金属反光线条
        for i in range(8):
            angle = i * 45 + 22.5
            rad = math.radians(angle)
            x1 = center + 13 * math.cos(rad)
            y1 = center + 13 * math.sin(rad)
            x2 = center + 14.5 * math.cos(rad)
            y2 = center + 14.5 * math.sin(rad)
            pygame.draw.line(self.image, (150, 220, 255), (int(x1), int(y1)), (int(x2), int(y2)), 1)
        
        # 黄色扫描箭头标记（3个）
        for i in range(3):
            angle = i * 120
            rad = math.radians(angle)
            arrow_x = center + 12 * math.cos(rad)
            arrow_y = center + 12 * math.sin(rad)
            pygame.draw.polygon(self.image, (255, 255, 100), [
                (arrow_x, arrow_y-1),
                (arrow_x+1.5, arrow_y+1.5),
                (arrow_x-1.5, arrow_y+1.5)
            ])
            pygame.draw.polygon(self.image, (200, 200, 50), [
                (arrow_x, arrow_y-1),
                (arrow_x+1.5, arrow_y+1.5),
                (arrow_x-1.5, arrow_y+1.5)
            ], 1)
    
    def _draw_bomber_deepjelly(self, size, center, color):
        """轰炸艇·深水母：复杂水滴形+纹理+舱门系统"""
        # 上部：分段圆弧装甲
        pygame.draw.circle(self.image, color, (center, center-4), 10)
        pygame.draw.circle(self.image, tuple(c-15 if c > 15 else 0 for c in color), 
                         (center, center-4), 10, 1)
        
        # 上部装甲分割
        pygame.draw.line(self.image, (80, 80, 80), (center-8, center-4), (center+8, center-4), 1)
        
        # 下部：水滴形
        pygame.draw.circle(self.image, color, (center, center+5), 7)
        pygame.draw.circle(self.image, tuple(c-15 if c > 15 else 0 for c in color), 
                         (center, center+5), 7, 1)
        
        # 六边形防爆纹理（多层）
        for layer in range(2):
            for i in range(4):
                for j in range(3):
                    hex_x = center - 8 + i * 5 + (j % 2) * 2.5
                    hex_y = center - 6 + j * 4 + layer * 2
                    # 六边形网格
                    hex_size = 2
                    hex_angles = [i * 60 for i in range(6)]
                    hex_points = [(hex_x + hex_size * math.cos(math.radians(a)), 
                                 hex_y + hex_size * math.sin(math.radians(a))) 
                                for a in hex_angles]
                    pygame.draw.polygon(self.image, (100, 120, 150), hex_points, 1)
        
        # 投弹舱门系统（3个）
        door_y_positions = [center-2, center+2, center+6]
        for door_y in door_y_positions:
            pygame.draw.rect(self.image, (30, 30, 30), (center-4, door_y, 8, 3))
            pygame.draw.rect(self.image, (80, 80, 80), (center-4, door_y, 8, 3), 1)
        
        # 推进器喷口（下方）
        for offset in [-4, 0, 4]:
            pygame.draw.circle(self.image, (50, 50, 50), (center+offset, size-5), 1)
        
        # 中心能量脉络
        pygame.draw.line(self.image, (100, 200, 100), (center, center-4), (center, center+5), 1)
    
    def _draw_jammer_amethyst(self, size, center, color):
        """干扰者·紫菱：复杂晶体+电磁节点+力场网"""
        # 外层菱形晶体（主体）
        diamond = [
            (center, 3),
            (size-3, center),
            (center, size-3),
            (3, center)
        ]
        pygame.draw.polygon(self.image, color, diamond)
        pygame.draw.polygon(self.image, (200, 100, 200), diamond, 2)
        
        # 内层晶体（略小，颜色略深）
        inner_diamond = [
            (center, 6),
            (size-6, center),
            (center, size-6),
            (6, center)
        ]
        pygame.draw.polygon(self.image, tuple(c-30 if c > 30 else 0 for c in color), inner_diamond, 1)
        
        # 晶体纹理线条（从中心辐射）
        for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
            rad = math.radians(angle)
            x = center + 8 * math.cos(rad)
            y = center + 8 * math.sin(rad)
            pygame.draw.line(self.image, (150, 100, 150), (center, center), (int(x), int(y)), 1)
        
        # 金属骨架节点（四个球形，多层）
        for angle in [45, 135, 225, 315]:
            rad = math.radians(angle)
            x = center + 11 * math.cos(rad)
            y = center + 11 * math.sin(rad)
            # 外层金属
            pygame.draw.circle(self.image, (180, 180, 180), (int(x), int(y)), 2)
            # 内层发光
            pygame.draw.circle(self.image, (200, 150, 200), (int(x), int(y)), 1)
        
        # 电弧连接线（节点之间）
        for i in range(4):
            angle1 = [45, 135, 225, 315][i]
            angle2 = [45, 135, 225, 315][(i+1)%4]
            rad1 = math.radians(angle1)
            rad2 = math.radians(angle2)
            x1 = center + 11 * math.cos(rad1)
            y1 = center + 11 * math.sin(rad1)
            x2 = center + 11 * math.cos(rad2)
            y2 = center + 11 * math.sin(rad2)
            pygame.draw.line(self.image, (200, 100, 200), (int(x1), int(y1)), (int(x2), int(y2)), 1)
        
        # 电磁力场网（半透明大圆）
        pygame.draw.circle(self.image, (180, 100, 200), (center, center), 13, 1)
        pygame.draw.circle(self.image, (160, 80, 180), (center, center), 12, 1)
    
    def _draw_shield_beeguard(self, size, center, color):
        """盾卫机·蜂巢护卫：复杂六边形+多层蜂窝+能量盾系统"""
        # 机体（六边形，分层）
        angles = [i * 60 for i in range(6)]
        hexagon = [(center + 9 * math.cos(math.radians(a)), 
                   center + 9 * math.sin(math.radians(a))) for a in angles]
        pygame.draw.polygon(self.image, color, hexagon)
        pygame.draw.polygon(self.image, (80, 120, 60), hexagon, 2)
        
        # 内层六边形（颜色略深）
        inner_hex = [(center + 6 * math.cos(math.radians(a)), 
                     center + 6 * math.sin(math.radians(a))) for a in angles]
        pygame.draw.polygon(self.image, tuple(c-20 if c > 20 else 0 for c in color), inner_hex, 1)
        
        # 多层蜂窝结构（密集）
        hex_size = 1.5
        for layer in range(3):
            for i in range(3):
                for j in range(3):
                    hx = center - 7 + i * 4 + (j % 2) * 2
                    hy = center - 6 + j * 3
                    hc_angles = [k * 60 for k in range(6)]
                    hc_points = [(hx + (hex_size + layer * 0.5) * math.cos(math.radians(a)), 
                                hy + (hex_size + layer * 0.5) * math.sin(math.radians(a))) 
                               for a in hc_angles]
                    pygame.draw.polygon(self.image, (100, 150, 100), hc_points, 1)
        
        # 多层能量盾牌系统
        pygame.draw.circle(self.image, (100, 200, 100), (center, center), 13, 2)
        pygame.draw.circle(self.image, (120, 220, 120), (center, center), 12, 1)
        pygame.draw.circle(self.image, (150, 255, 150), (center, center), 11, 1)
        
        # 能量纹路（辐射线）
        for angle in angles:
            rad = math.radians(angle)
            x = center + 13 * math.cos(rad)
            y = center + 13 * math.sin(rad)
            pygame.draw.line(self.image, (150, 255, 150), (center, center), (int(x), int(y)), 1)
        
        # 红色光学传感器（中心）
        pygame.draw.circle(self.image, (255, 80, 80), (center, center), 2)
        pygame.draw.circle(self.image, (255, 50, 50), (center, center), 1)
    
    def _draw_crystal_cluster(self, size, center, color):
        """蔚蓝核心：精细多面体晶簇系统"""
        # 中心主晶体（多层）
        for r in [10, 7, 4, 1]:
            pygame.draw.circle(self.image, color, (center, center), r, 1 if r > 1 else 0)
        
        # 中心能量核心
        pygame.draw.circle(self.image, (200, 220, 255), (center, center), 2)
        
        # 周围4个卫星晶体（分层）
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle)
            x = center + 12 * math.cos(rad)
            y = center + 12 * math.sin(rad)
            # 外层
            pygame.draw.circle(self.image, color, (int(x), int(y)), 4)
            # 内层
            pygame.draw.circle(self.image, tuple(c+30 if c < 225 else 255 for c in color), 
                             (int(x), int(y)), 2, 1)
        
        # 连接晶体的蓝色光纤
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle)
            x = center + 12 * math.cos(rad)
            y = center + 12 * math.sin(rad)
            pygame.draw.line(self.image, (100, 150, 200), (center, center), (int(x), int(y)), 1)
    
    def _draw_needle_sniper(self, size, center, color):
        """黑针：精细修长狙击舰系统"""
        # 主机身（椭圆形）
        pygame.draw.ellipse(self.image, color, (center-2, 4, 4, size-8))
        pygame.draw.ellipse(self.image, (100, 100, 120), (center-2, 4, 4, size-8), 1)
        
        # 机身中线反光
        pygame.draw.line(self.image, (150, 150, 150), (center, 4), (center, size-4), 1)
        
        # 尖锐头部（多层）
        pygame.draw.polygon(self.image, color, [
            (center-2.5, 8), (center+2.5, 8), (center, 3)
        ])
        pygame.draw.polygon(self.image, (80, 80, 80), [
            (center-2.5, 8), (center+2.5, 8), (center, 3)
        ], 1)
        
        # 炮口散热片（两侧）
        for offset in [-2, 2]:
            pygame.draw.rect(self.image, (80, 80, 80), (center+offset-1, center-3, 1, 6))
        
        # 长炮管（下方，双层）
        pygame.draw.rect(self.image, (50, 50, 50), (center-1.5, center-1, 3, 10))
        pygame.draw.rect(self.image, (80, 80, 80), (center-1.5, center-1, 3, 10), 1)
        
        # 尾部推进器（环形）
        pygame.draw.circle(self.image, (100, 80, 0), (center, size-4), 2.5, 1)
        pygame.draw.circle(self.image, (200, 150, 50), (center, size-4), 1.5, 1)
    
    def _draw_dual_wasp(self, size, center, color):
        """双生黄蜂：精细双梭形联合舰系统"""
        # 左梭形（完整结构）
        left_wasp = [
            (center-7, 8), (center-2, center-5), 
            (center-7, size-8), (center-11, center-5)
        ]
        pygame.draw.polygon(self.image, color, left_wasp)
        pygame.draw.polygon(self.image, (100, 150, 50), left_wasp, 2)
        
        # 左梭形内部纹理
        pygame.draw.line(self.image, (80, 80, 80), (center-7, center), (center-7, size-8), 1)
        
        # 右梭形（完整结构）
        right_wasp = [
            (center+7, 8), (center+11, center-5), 
            (center+7, size-8), (center+2, center-5)
        ]
        pygame.draw.polygon(self.image, color, right_wasp)
        pygame.draw.polygon(self.image, (100, 150, 50), right_wasp, 2)
        
        # 右梭形内部纹理
        pygame.draw.line(self.image, (80, 80, 80), (center+7, center), (center+7, size-8), 1)
        
        # 中央连接杆（银色，多层）
        pygame.draw.line(self.image, (150, 150, 150), (center-7, center), (center+7, center), 3)
        pygame.draw.line(self.image, (200, 200, 200), (center-7, center), (center+7, center), 1)
        
        # 连接处能量球
        pygame.draw.circle(self.image, (255, 200, 100), (center, center), 2)
        pygame.draw.circle(self.image, (200, 150, 50), (center, center), 1)
        
        # 三连装枪口（每个梭形）
        gun_offset_y = center - 4
        for x_base in [center-7, center+7]:
            for i, offset in enumerate([-1.5, 0, 1.5]):
                pygame.draw.circle(self.image, (50, 50, 50), (int(x_base+offset), int(gun_offset_y)), 0.8)
    
    def _draw_summoner_ufo(self, size, center, color):
        """母巢光环：精细UFO圆盘系统+能量阵"""
        # 底部圆盘（分层）
        pygame.draw.circle(self.image, (180, 140, 0), (center, center+3), 11)
        pygame.draw.circle(self.image, (200, 160, 20), (center, center+3), 11, 2)
        pygame.draw.circle(self.image, (160, 120, 0), (center, center+3), 9, 1)
        
        # 圆盘舱门阵列（6个）
        for i in range(6):
            angle = i * 60
            rad = math.radians(angle)
            x = center + 8 * math.cos(rad)
            y = center + 3 + 8 * math.sin(rad)
            pygame.draw.rect(self.image, (50, 50, 50), (int(x)-1.5, int(y)-1, 3, 2))
        
        # 中央指挥塔（多层）
        pygame.draw.circle(self.image, (100, 50, 150), (center, center-3), 5, 2)
        pygame.draw.circle(self.image, (150, 100, 200), (center, center-3), 4, 1)
        pygame.draw.circle(self.image, (180, 130, 220), (center, center-3), 2, 1)
        
        # 塔顶控制灯
        pygame.draw.circle(self.image, (255, 100, 100), (center, center-6), 1)
        
        # 下方魔法阵系统（多层旋转）
        for r in [10, 7, 4]:
            pygame.draw.circle(self.image, (100, 150, 255), (center, center+9), r, 1)
        
        # 阵法连接线（十字）
        pygame.draw.line(self.image, (100, 150, 255), (center, center+4), (center, center+14), 1)
        pygame.draw.line(self.image, (100, 150, 255), (center-6, center+9), (center+6, center+9), 1)
    
    def _draw_prism(self, size, center, color):
        """虚空棱镜：精细正二十面体光学系统"""
        # 外层棱晶（多层透明效果）
        pygame.draw.circle(self.image, (200, 220, 240), (center, center), 11, 2)
        pygame.draw.circle(self.image, (180, 200, 220), (center, center), 9, 2)
        pygame.draw.circle(self.image, (200, 220, 240), (center, center), 7, 1)
        
        # 棱晶边缘反光
        for i in range(8):
            angle = i * 45
            rad = math.radians(angle)
            x = center + 11 * math.cos(rad)
            y = center + 11 * math.sin(rad)
            pygame.draw.circle(self.image, (220, 240, 255), (int(x), int(y)), 1)
        
        # 内部能量核心（多层）
        pygame.draw.circle(self.image, (200, 200, 255), (center, center), 3, 1)
        pygame.draw.circle(self.image, (255, 255, 255), (center, center), 2)
        pygame.draw.circle(self.image, (150, 200, 255), (center, center), 1)
    
    def _draw_heavy_anvil(self, size, center, color):
        """重装铁砧：精细球形堡垒系统"""
        # 主体球（分层装甲）
        pygame.draw.circle(self.image, color, (center, center), 11)
        pygame.draw.circle(self.image, (100, 100, 120), (center, center), 11, 2)
        pygame.draw.circle(self.image, tuple(c-20 if c > 20 else 0 for c in color), 
                         (center, center), 9, 1)
        
        # 装甲板缝隙系统（四向）
        for i in range(4):
            angle = i * 90
            rad = math.radians(angle)
            x = center + 9 * math.cos(rad)
            y = center + 9 * math.sin(rad)
            # 缝隙
            pygame.draw.line(self.image, (255, 120, 50), (int(x)-2, int(y)), (int(x)+2, int(y)), 2)
            # 发光效果
            pygame.draw.line(self.image, (255, 180, 100), (int(x)-1, int(y)), (int(x)+1, int(y)), 1)
        
        # 炮塔结构（顶部）
        pygame.draw.circle(self.image, (80, 80, 80), (center, center-6), 3, 1)
        pygame.draw.rect(self.image, (100, 100, 100), (center-2, center-8, 4, 3))
        
        # 反重力引擎（底部，向下光柱）
        pygame.draw.circle(self.image, (50, 150, 255), (center, center+10), 3, 1)
        pygame.draw.line(self.image, (100, 200, 255), (center-1, center+10), (center-2, center+14), 1)
        pygame.draw.line(self.image, (100, 200, 255), (center+1, center+10), (center+2, center+14), 1)
    
    def _draw_default_enemy(self, size, center, color):
        """默认敌人：渐变圆形"""
        pygame.draw.circle(self.image, color, (center, center), center-5)
        pygame.draw.circle(self.image, tuple(min(c+50, 255) for c in color), (center, center), center-5, 2)
        pygame.draw.circle(self.image, tuple(min(c+100, 255) for c in color), (center, center), center-10, 1)
    
    def _draw_advanced_enemy(self, size, center, color, enemy_type):
        """绘制高级敌人（第二和第三批）"""
        if enemy_type == 'splitter_azurecore':
            self._draw_crystal_cluster(size, center, color)
        elif enemy_type == 'sniper_blackneedle':
            self._draw_needle_sniper(size, center, color)
        elif enemy_type == 'weaver_dualwasp':
            self._draw_dual_wasp(size, center, color)
        elif enemy_type == 'summoner_nethalo':
            self._draw_summoner_ufo(size, center, color)
        elif enemy_type == 'prism_voidprism':
            self._draw_prism(size, center, color)
        elif enemy_type == 'guard_heavyanvil':
            self._draw_heavy_anvil(size, center, color)
        elif enemy_type == 'nestlord_livestarport':
            self._draw_nest_lord(size, center, color)
        elif enemy_type == 'weaver_dimensionspindle':
            self._draw_dimension_spindle(size, center, color)
        elif enemy_type == 'judge_dualpolar':
            self._draw_dual_judge(size, center, color)
        elif enemy_type == 'annihilator_soleye':
            self._draw_sole_eye(size, center, color)
        elif enemy_type == 'chaos_discordantprism':
            self._draw_chaos_prism(size, center, color)
        elif enemy_type == 'phantom_voidstrider':
            self._draw_phantom_strider(size, center, color)
    
    def _draw_nest_lord(self, size, center, color):
        """巢穴领主·活体星港：精细生物机械混合体系统"""
        # 主体：生物核心（心脏形，分层）
        pygame.draw.circle(self.image, (100, 20, 50), (center, center), 9)
        pygame.draw.circle(self.image, (150, 50, 80), (center, center), 9, 2)
        pygame.draw.circle(self.image, (50, 10, 30), (center, center), 6, 1)
        
        # 核心中央血红灯
        pygame.draw.circle(self.image, (255, 100, 100), (center, center), 2)
        pygame.draw.circle(self.image, (200, 50, 50), (center, center), 1)
        
        # 血管触须系统（上下六条）
        for i in range(6):
            if i < 3:
                # 上方触须
                angle = i * 60 - 60
                rad = math.radians(angle)
                dx = int(4 * math.cos(rad))
                dy = -3
                pygame.draw.line(self.image, (100, 20, 50), 
                               (center + dx, center + dy), (center + dx - 1, center - 10), 2)
            else:
                # 下方触须
                angle = (i - 3) * 60 + 60
                rad = math.radians(angle)
                dx = int(4 * math.cos(rad))
                dy = 3
                pygame.draw.line(self.image, (100, 20, 50), 
                               (center + dx, center + dy), (center + dx - 1, center + 10), 2)
        
        # 卵囊系统（4个，发光）
        for angle in [45, 135, 225, 315]:
            rad = math.radians(angle)
            x = center + 11 * math.cos(rad)
            y = center + 11 * math.sin(rad)
            # 卵囊
            pygame.draw.circle(self.image, (150, 255, 100), (int(x), int(y)), 2)
            pygame.draw.circle(self.image, (200, 255, 150), (int(x), int(y)), 2, 1)
        
        # 血管纹路网络
        pygame.draw.circle(self.image, (100, 50, 80), (center, center), 13, 1)
        for angle in [0, 60, 120, 180, 240, 300]:
            rad = math.radians(angle)
            x = center + 13 * math.cos(rad)
            y = center + 13 * math.sin(rad)
            pygame.draw.line(self.image, (80, 30, 60), (center, center), (int(x), int(y)), 1)
    
    def _draw_dimension_spindle(self, size, center, color):
        """时空编织者·次元纺锤：精细银色纺锤+扭曲场系统"""
        # 外层纺锤体（银色三层）
        pygame.draw.polygon(self.image, (180, 180, 200), [
            (center, 5), (size - 5, center), (center, size - 5), (5, center)
        ])
        pygame.draw.polygon(self.image, (220, 220, 240), [
            (center, 5), (size - 5, center), (center, size - 5), (5, center)
        ], 1)
        pygame.draw.polygon(self.image, (100, 100, 150), [
            (center, 5), (size - 5, center), (center, size - 5), (5, center)
        ], 1)
        
        # 中层纺锤体（内层颜色）
        inner_points = [
            (center, center - 6), (center + 8, center), 
            (center, center + 6), (center - 8, center)
        ]
        pygame.draw.polygon(self.image, (140, 140, 180), inner_points)
        pygame.draw.polygon(self.image, (180, 180, 220), inner_points, 1)
        
        # 扭曲场纹路系统（多层）
        for r in [14, 10, 6]:
            pygame.draw.circle(self.image, (100, 140, 200), (center, center), r, 1)
        for r in [12, 8]:
            pygame.draw.circle(self.image, (80, 120, 180), (center, center), r, 1)
        
        # 时空粒子纹理（8条辐射线）
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = center + 12 * math.cos(rad)
            y1 = center + 12 * math.sin(rad)
            x2 = center + 5 * math.cos(rad)
            y2 = center + 5 * math.sin(rad)
            pygame.draw.line(self.image, (120, 160, 220), (int(x1), int(y1)), (int(x2), int(y2)), 1)
        
        # 中心能量汇聚点
        pygame.draw.circle(self.image, (255, 255, 200), (center, center), 3)
        pygame.draw.circle(self.image, (200, 200, 150), (center, center), 3, 1)
        pygame.draw.circle(self.image, (150, 150, 100), (center, center), 1)
    
    def _draw_dual_judge(self, size, center, color):
        """镜像仲裁者·双极幻象：精细双仁形+对称能量屏障"""
        # 左仁主体（分层）
        pygame.draw.circle(self.image, (220, 230, 255), (center - 6, center), 7)
        pygame.draw.circle(self.image, (180, 200, 240), (center - 6, center), 7, 1)
        pygame.draw.circle(self.image, (150, 170, 220), (center - 6, center), 5, 1)
        
        # 左仁中央灯
        pygame.draw.circle(self.image, (100, 150, 255), (center - 6, center), 2)
        pygame.draw.circle(self.image, (200, 220, 255), (center - 6, center), 2, 1)
        
        # 右仁主体（分层）
        pygame.draw.circle(self.image, (220, 230, 255), (center + 6, center), 7)
        pygame.draw.circle(self.image, (180, 200, 240), (center + 6, center), 7, 1)
        pygame.draw.circle(self.image, (150, 170, 220), (center + 6, center), 5, 1)
        
        # 右仁中央灯
        pygame.draw.circle(self.image, (100, 150, 255), (center + 6, center), 2)
        pygame.draw.circle(self.image, (200, 220, 255), (center + 6, center), 2, 1)
        
        # 双仁连接能量线系统（3层）
        pygame.draw.line(self.image, (100, 180, 255), (center - 6, center), (center + 6, center), 2)
        pygame.draw.line(self.image, (120, 200, 255), (center - 6, center - 1), (center + 6, center - 1), 1)
        pygame.draw.line(self.image, (120, 200, 255), (center - 6, center + 1), (center + 6, center + 1), 1)
        
        # 对称能量屏障（4层圆形）
        pygame.draw.circle(self.image, (150, 180, 220), (center, center), 14, 1)
        pygame.draw.circle(self.image, (120, 160, 200), (center, center), 11, 1)
        pygame.draw.circle(self.image, (100, 140, 180), (center, center), 8, 1)
        
        # 对称发光点（上下）
        pygame.draw.circle(self.image, (200, 200, 255), (center, center - 10), 1)
        pygame.draw.circle(self.image, (200, 200, 255), (center, center + 10), 1)
        
        # 中央能量核心
        pygame.draw.circle(self.image, (255, 200, 255), (center, center), 2)
    
    def _draw_sole_eye(self, size, center, color):
        """湮灭光束舰·肃正之眼：精细深空黑舰+环形眼睛系统"""
        # 舰体主轮廓（分层）
        pygame.draw.rect(self.image, (15, 15, 25), (center - 9, center - 7, 18, 14))
        pygame.draw.rect(self.image, (40, 40, 60), (center - 9, center - 7, 18, 14), 1)
        
        # 舰体中线（金属反光）
        pygame.draw.line(self.image, (80, 80, 100), (center, center - 7), (center, center + 7), 1)
        
        # 舰体装甲分割（左右两侧）
        pygame.draw.line(self.image, (30, 30, 50), (center - 9, center - 3), (center - 1, center - 3), 1)
        pygame.draw.line(self.image, (30, 30, 50), (center - 9, center + 3), (center - 1, center + 3), 1)
        pygame.draw.line(self.image, (30, 30, 50), (center + 1, center - 3), (center + 9, center - 3), 1)
        pygame.draw.line(self.image, (30, 30, 50), (center + 1, center + 3), (center + 9, center + 3), 1)
        
        # 环形眼睛系统（中央多层）
        pygame.draw.circle(self.image, (150, 150, 200), (center, center), 5, 2)  # 外层
        pygame.draw.circle(self.image, (100, 100, 150), (center, center), 4, 1)  # 中层
        pygame.draw.circle(self.image, (80, 80, 120), (center, center), 3, 1)   # 内层
        
        # 眼睛中心（亮白色）
        pygame.draw.circle(self.image, (255, 255, 255), (center, center), 2)
        pygame.draw.circle(self.image, (200, 200, 200), (center, center), 1)
        
        # 能量翼板系统（左右两侧多层）
        # 左翼板
        pygame.draw.polygon(self.image, (100, 150, 200), [
            (center - 9, center - 3), (center - 14, center - 3), (center - 14, center + 3)
        ])
        pygame.draw.polygon(self.image, (150, 180, 220), [
            (center - 9, center - 3), (center - 14, center - 3), (center - 14, center + 3)
        ], 1)
        
        # 右翼板
        pygame.draw.polygon(self.image, (100, 150, 200), [
            (center + 9, center - 3), (center + 14, center - 3), (center + 14, center + 3)
        ])
        pygame.draw.polygon(self.image, (150, 180, 220), [
            (center + 9, center - 3), (center + 14, center - 3), (center + 14, center + 3)
        ], 1)
        
        # 扫描光线（从眼睛向外）
        pygame.draw.line(self.image, (100, 200, 255), (center, center), (center + 12, center), 1)
        pygame.draw.line(self.image, (100, 200, 255), (center, center), (center - 12, center), 1)
    
    def _draw_chaos_prism(self, size, center, color):
        """混沌信标·不谐棱柱：精细多色混沌棱镜系统"""
        # 外层多色菱形棱镜（3层）
        colors_outer = [(200, 100, 200), (100, 200, 200), (255, 200, 100)]
        for idx, c in enumerate(colors_outer):
            offset = idx * 1
            pygame.draw.polygon(self.image, c, [
                (center, 3 + offset),
                (size - 3 - offset, center),
                (center, size - 3 - offset),
                (3 + offset, center)
            ])
        
        # 中层菱形（半透明效果）
        pygame.draw.polygon(self.image, (200, 200, 100), [
            (center, 6), (size - 6, center), (center, size - 6), (6, center)
        ], 1)
        
        # 内层菱形（颜色对比）
        inner_offset = 3
        pygame.draw.polygon(self.image, (150, 150, 200), [
            (center, center - inner_offset),
            (center + inner_offset, center),
            (center, center + inner_offset),
            (center - inner_offset, center)
        ])
        
        # 混沌中心能量体（多色交错）
        pygame.draw.circle(self.image, (255, 150, 200), (center, center), 4)
        pygame.draw.circle(self.image, (150, 255, 150), (center, center), 3, 1)
        pygame.draw.circle(self.image, (255, 255, 100), (center, center), 2, 1)
        
        # 混沌光线（8条辐射）
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x = center + 10 * math.cos(rad)
            y = center + 10 * math.sin(rad)
            colors_line = [(200, 100, 200), (100, 200, 200), (255, 200, 100), (200, 200, 100)]
            color_idx = (angle // 45) % len(colors_line)  # 确保索引不超出范围
            pygame.draw.line(self.image, colors_line[color_idx], (center, center), (int(x), int(y)), 1)
    
    def _draw_phantom_strider(self, size, center, color):
        """相位幽影·幽域潜行者：精细紫色幽影+相位刃系统"""
        # 主体轮廓（紫色分层）
        pygame.draw.circle(self.image, (100, 40, 150), (center, center), 9, 2)
        pygame.draw.circle(self.image, (80, 20, 120), (center, center), 9, 1)
        pygame.draw.circle(self.image, (60, 10, 90), (center, center), 6, 1)
        
        # 类人形身体（分段）
        # 头部
        pygame.draw.circle(self.image, (120, 60, 160), (center, center - 5), 3, 1)
        
        # 躯干（中央线条）
        pygame.draw.line(self.image, (80, 30, 130), (center, center - 2), (center, center + 4), 1)
        
        # 左臂（向左上）
        pygame.draw.line(self.image, (80, 20, 120), (center - 2, center), (center - 6, center - 4), 2)
        pygame.draw.line(self.image, (120, 60, 160), (center - 2, center), (center - 6, center - 4), 1)
        
        # 右臂（向右上）
        pygame.draw.line(self.image, (80, 20, 120), (center + 2, center), (center + 6, center - 4), 2)
        pygame.draw.line(self.image, (120, 60, 160), (center + 2, center), (center + 6, center - 4), 1)
        
        # 幽蓝眼睛系统（双眼）
        pygame.draw.circle(self.image, (150, 100, 200), (center - 2, center - 4), 1)
        pygame.draw.circle(self.image, (150, 100, 200), (center + 2, center - 4), 1)
        pygame.draw.circle(self.image, (200, 150, 220), (center - 2, center - 4), 1, 1)
        pygame.draw.circle(self.image, (200, 150, 220), (center + 2, center - 4), 1, 1)
        
        # 相位刃系统（两把武器刃）
        # 左相位刃
        pygame.draw.polygon(self.image, (150, 100, 200), [
            (center - 5, center + 3), (center - 7, center + 3), (center - 6, center + 10)
        ])
        pygame.draw.polygon(self.image, (200, 150, 220), [
            (center - 5, center + 3), (center - 7, center + 3), (center - 6, center + 10)
        ], 1)
        
        # 右相位刃
        pygame.draw.polygon(self.image, (150, 100, 200), [
            (center + 5, center + 3), (center + 7, center + 3), (center + 6, center + 10)
        ])
        pygame.draw.polygon(self.image, (200, 150, 220), [
            (center + 5, center + 3), (center + 7, center + 3), (center + 6, center + 10)
        ], 1)
        
        # 幽影烟雾效果（外层）
        pygame.draw.circle(self.image, (60, 10, 90), (center, center), 11, 1)
    
    def _update_animation(self):
        """更新动画帧（动态效果）"""
        size = 70 if self.is_elite else 50
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        color = self.config.get('color', (255, 100, 100))
        
        enemy_type = self.type
        anim = (self.animation_time // 5) % 20  # 动画循环周期
        
        if self.is_elite:
            self._draw_elite_enemy_animated(size, center, color, anim)
        else:
            # 根据敌人类型绘制动画版本
            if enemy_type == 'scout_moth':
                self._draw_scout_moth_animated(size, center, color, anim)
            elif enemy_type == 'lurker_halo':
                self._draw_lurker_halo_animated(size, center, color, anim)
            elif enemy_type == 'summoner_nethalo':
                self._draw_summoner_ufo_animated(size, center, color, anim)
            elif enemy_type == 'prism_voidprism':
                self._draw_prism_animated(size, center, color, anim)
            elif enemy_type == 'nestlord_livestarport':
                self._draw_nest_lord_animated(size, center, color, anim)
            elif enemy_type == 'weaver_dimensionspindle':
                self._draw_dimension_spindle_animated(size, center, color, anim)
            elif enemy_type == 'annihilator_soleye':
                self._draw_sole_eye_animated(size, center, color, anim)
            elif enemy_type == 'chaos_discordantprism':
                self._draw_chaos_prism_animated(size, center, color, anim)
            else:
                # 静态敌人保持原样
                if enemy_type == 'trooper_spear':
                    self._draw_trooper_spear(size, center, color)
                elif enemy_type == 'bomber_deepjelly':
                    self._draw_bomber_deepjelly(size, center, color)
                elif enemy_type == 'jammer_amethyst':
                    self._draw_jammer_amethyst(size, center, color)
                elif enemy_type == 'shield_beeguard':
                    self._draw_shield_beeguard(size, center, color)
                elif enemy_type == 'sniper_blackneedle':
                    self._draw_needle_sniper(size, center, color)
                elif enemy_type == 'weaver_dualwasp':
                    self._draw_dual_wasp(size, center, color)
                elif enemy_type == 'splitter_azurecore':
                    self._draw_crystal_cluster(size, center, color)
                elif enemy_type == 'guard_heavyanvil':
                    self._draw_heavy_anvil(size, center, color)
                elif enemy_type == 'judge_dualpolar':
                    self._draw_dual_judge(size, center, color)
                elif enemy_type == 'phantom_voidstrider':
                    self._draw_phantom_strider(size, center, color)
                else:
                    self._draw_default_enemy(size, center, color)
    
    def _draw_elite_enemy_animated(self, size, center, color, anim):
        """精英敌人动画：脉动效果"""
        pulse = math.sin(anim * 0.314) * 3
        
        # 多层圆形
        pygame.draw.circle(self.image, (255, 200, 0), (center, center), int(center - 3 + pulse), 0)
        pygame.draw.circle(self.image, (255, 150, 0), (center, center), center - 6, 3)
        pygame.draw.circle(self.image, (200, 100, 50), (center, center), center - 10, 2)
        
        # 旋转星形光芒
        for i in range(12):
            angle = i * 30 + anim * 6
            rad = math.radians(angle)
            x = center + int((center - 8 + pulse) * math.cos(rad))
            y = center + int((center - 8 + pulse) * math.sin(rad))
            pygame.draw.circle(self.image, (255, 255, 150), (x, y), 3)
    
    def _draw_scout_moth_animated(self, size, center, color, anim):
        """侦察机动画：旋转扫描灯"""
        # 主体
        triangle = [
            (center, 5),
            (size - 5, size - 5),
            (5, size - 5)
        ]
        pygame.draw.polygon(self.image, color, triangle)
        pygame.draw.polygon(self.image, (100, 150, 200), triangle, 2)
        
        # 焊接纹路
        for i in range(3):
            offset = (i - 1) * 3
            pygame.draw.line(self.image, (100, 100, 100), 
                           (center - 5 + offset, center), (center + 5 + offset, size - 5), 1)
        
        # 旋转扫描灯
        angle = anim * 18  # 每帧旋转18度
        rad = math.radians(angle)
        scan_r = 3
        scan_x = center + int(scan_r * math.cos(rad))
        scan_y = center + int(scan_r * math.sin(rad))
        pygame.draw.circle(self.image, (255, 50, 50), (int(scan_x), int(scan_y)), 2)
        pygame.draw.circle(self.image, (255, 100, 100), (center, center), 4, 1)
    
    def _draw_lurker_halo_animated(self, size, center, color, anim):
        """光环盘动画：旋转光环和箭头"""
        # 核心舱（正八边形）
        angles = [i * 45 for i in range(8)]
        core_points = [(center + 8 * math.cos(math.radians(a)), 
                       center + 8 * math.sin(math.radians(a))) for a in angles]
        pygame.draw.polygon(self.image, color, core_points)
        pygame.draw.polygon(self.image, (100, 200, 150), core_points, 2)
        
        # 旋转光环
        pygame.draw.circle(self.image, (100, 200, 255), (center, center), 14 + int(math.sin(anim * 0.314) * 2), 2)
        pygame.draw.circle(self.image, (100, 200, 255), (center, center), 13, 1)
        
        # 旋转的黄色箭头
        for i in range(3):
            angle = i * 120 + anim * 12
            rad = math.radians(angle)
            arrow_x = center + 12 * math.cos(rad)
            arrow_y = center + 12 * math.sin(rad)
            pygame.draw.polygon(self.image, (255, 255, 100), [
                (arrow_x, arrow_y - 1),
                (arrow_x + 1, arrow_y + 1),
                (arrow_x - 1, arrow_y + 1)
            ])
    
    def _draw_summoner_ufo_animated(self, size, center, color, anim):
        """母巢光环动画：脉动魔法阵"""
        # 底部圆盘
        pygame.draw.circle(self.image, (180, 140, 0), (center, center + 3), 10)
        pygame.draw.circle(self.image, (200, 160, 20), (center, center + 3), 10, 2)
        
        # 中央指挥塔（脉动）
        pulse = int(math.sin(anim * 0.314) * 1)
        pygame.draw.circle(self.image, (100, 50, 150), (center, center - 3), 5 + pulse, 2)
        pygame.draw.circle(self.image, (150, 100, 200), (center, center - 3), 3 + pulse, 1)
        
        # 下方魔法阵（旋转）
        for i in range(2):
            r = 8 if i == 0 else 5
            rotation = anim * (12 if i == 0 else -12)
            pygame.draw.circle(self.image, (100, 150, 255), (center, center + 8), r, 1)
    
    def _draw_prism_animated(self, size, center, color, anim):
        """虚空棱镜动画：旋转彩虹折射"""
        # 外层棱晶（旋转）
        for i in range(3):
            rotation = i * 120 + anim * 6
            offset = int(math.sin(math.radians(rotation)) * 2)
            pygame.draw.circle(self.image, (200 + offset, 220, 240), (center, center), 10 + offset, 2)
        
        pygame.draw.circle(self.image, (180, 200, 220), (center, center), 8, 1)
        
        # 脉动的内部光核
        pulse = 2 + int(math.sin(anim * 0.314) * 1)
        pygame.draw.circle(self.image, (255, 255, 255), (center, center), pulse)
    
    def _draw_nest_lord_animated(self, size, center, color, anim):
        """巢穴领主动画：卵囊脉动孵化"""
        # 主体：心脏跳动
        pulse = int(math.sin(anim * 0.314) * 2)
        pygame.draw.circle(self.image, (100, 20, 50), (center, center), 8 + pulse)
        pygame.draw.circle(self.image, (150, 50, 80), (center, center), 8 + pulse, 2)
        
        # 触须（波动）
        for dx in [-3, 0, 3]:
            wave = int(math.sin(anim * 0.157 + dx) * 1)
            pygame.draw.line(self.image, (100, 20, 50), 
                           (center + dx, center - 8), (center + dx - 2 + wave, center - 14), 2)
            pygame.draw.line(self.image, (100, 20, 50), 
                           (center + dx, center + 8), (center + dx - 2 + wave, center + 14), 2)
        
        # 卵囊（脉动发光）
        brightness = int(150 + 100 * abs(math.sin(anim * 0.157)))
        for angle in [45, 135, 225, 315]:
            rad = math.radians(angle)
            x = center + 10 * math.cos(rad)
            y = center + 10 * math.sin(rad)
            pygame.draw.circle(self.image, (brightness, 255, 100), (int(x), int(y)), 2, 1)
        
        # 血管纹路
        pygame.draw.circle(self.image, (100, 50, 80), (center, center), 12, 1)
    
    def _draw_dimension_spindle_animated(self, size, center, color, anim):
        """次元纺锤动画：扭曲空间效果"""
        twist = anim * 18  # 旋转度数
        
        # 中心纺锤体（旋转）
        rad = math.radians(twist)
        pygame.draw.polygon(self.image, (200, 200, 220), [
            (center, 5), (size - 5, center), (center, size - 5), (5, center)
        ])
        pygame.draw.polygon(self.image, (150, 180, 200), [
            (center, 5), (size - 5, center), (center, size - 5), (5, center)
        ], 2)
        
        # 脉动能量点
        pulse = 2 + int(math.sin(anim * 0.314))
        pygame.draw.circle(self.image, (255, 255, 200), (center, center), pulse)
        
        # 扭曲场纹路（脉动半径）
        for r_factor in [1.5, 1.0, 0.5]:
            r = int(15 * r_factor + math.sin(anim * 0.157) * 2)
            pygame.draw.circle(self.image, (100, 150, 220), (center, center), r, 1)
    
    def _draw_sole_eye_animated(self, size, center, color, anim):
        """肃正之眼动画：充能扫描效果"""
        # 舰体
        pygame.draw.rect(self.image, (20, 20, 30), (center - 8, center - 6, 16, 12))
        pygame.draw.circle(self.image, (40, 40, 60), (center, center), 8, 2)
        
        # 环形眼睛（充能脉冲）
        pulse = int(math.sin(anim * 0.314) * 2)
        pygame.draw.circle(self.image, (100 + pulse * 20, 100 + pulse * 20, 150 + pulse * 50), 
                          (center, center - 2), 4 + pulse, 2)
        pygame.draw.circle(self.image, (80, 80, 120), (center, center - 2), 3, 1)
        
        # 眼睛中心扫描
        brightness = 150 + int(100 * abs(math.sin(anim * 0.157)))
        pygame.draw.circle(self.image, (brightness, brightness, 255), (center, center - 2), 1)
        
        # 扫描光线（旋转）
        for i in range(3):
            angle = anim * 6 + i * 120
            rad = math.radians(angle)
            x2 = center + 5 * math.cos(rad)
            y2 = center - 2 + 5 * math.sin(rad)
            pygame.draw.line(self.image, (150, 150, 255), 
                           (center, center - 2), (x2, y2), 1)
        
        # 能量翼板
        pygame.draw.polygon(self.image, (100, 150, 200), [
            (center - 8, center - 3), (center - 12, center - 2), (center - 12, center + 2)
        ])
        pygame.draw.polygon(self.image, (100, 150, 200), [
            (center + 8, center - 3), (center + 12, center - 2), (center + 12, center + 2)
        ])
    
    def _draw_chaos_prism_animated(self, size, center, color, anim):
        """混沌棱柱动画：不规则形态变化"""
        # 多色旋转棱柱（不规则变形）
        colors = [(200, 100, 200), (100, 200, 200), (255, 200, 100), (200, 200, 100)]
        for i, c in enumerate(colors):
            offset = i * 2 + int(math.sin(anim * 0.314 + i) * 1)
            pygame.draw.polygon(self.image, c, [
                (center, 3 + offset),
                (size - 3 - offset, center),
                (center, size - 3 - offset),
                (3 + offset, center)
            ], 1)
        
        # 混沌中心（颜色闪烁）
        color_idx = (anim // 5) % len(colors)
        pygame.draw.circle(self.image, colors[color_idx], (center, center), 3)
    
    def update(self):
        """更新敌人状态"""
        # 冻结检查
        if self.frozen_timer > 0:
            self.frozen_timer -= 1
            return
        
        self.timer += 1
        self.animation_time += 1
        
        # 执行AI行为
        self._execute_ai()
        
        # 执行攻击模式
        self._execute_attack()
        
        # 更新动态效果（每5帧重绘一次）
        if self.animation_time % 5 == 0:
            self._update_animation()
        
        # 边界检查
        if self.rect.top > HEIGHT:
            self.kill()
    
    def _execute_ai(self):
        """执行AI移动逻辑"""
        behavior = self.ai_behavior
        ai_params = self.config.get('ai_params', {})
        
        if behavior == 'straight':
            # 直线下降
            self.rect.y += self.speed
        
        elif behavior == 'sine':
            # 正弦波移动
            self.rect.y += self.speed
            if 'start_x' not in self.movement_data:
                self.movement_data['start_x'] = self.rect.x
            amplitude = ai_params.get('amplitude', 70)
            frequency = ai_params.get('frequency', 0.03)
            self.rect.x = self.movement_data['start_x'] + math.sin(self.timer * frequency) * amplitude
        
        elif behavior == 'zigzag':
            # 之字形移动
            self.rect.y += self.speed
            if 'direction' not in self.movement_data:
                self.movement_data['direction'] = random.choice([-1, 1])
            zigzag_speed = ai_params.get('zigzag_speed', 5)
            self.rect.x += self.movement_data['direction'] * zigzag_speed
            if self.rect.x <= 0 or self.rect.x >= WIDTH - self.rect.width:
                self.movement_data['direction'] *= -1
        
        elif behavior == 'circle':
            # 圆形轨迹
            if 'center_x' not in self.movement_data:
                self.movement_data['center_x'] = WIDTH // 2
                self.movement_data['center_y'] = self.rect.y
            radius = ai_params.get('radius', 90)
            angular_speed = ai_params.get('angular_speed', 2.0)
            angle = self.timer * angular_speed
            self.rect.x = self.movement_data['center_x'] + math.cos(angle) * radius
            self.rect.y = self.movement_data['center_y'] + math.sin(angle) * radius
            self.movement_data['center_y'] += self.speed * 0.5
        
        elif behavior == 'custom':
            # 自定义行为（通过回调函数）
            custom_func = self.config.get('custom_movement')
            if custom_func:
                custom_func(self)
    
    def _execute_attack(self):
        """执行攻击模式"""
        if not self.attack_pattern:
            return
        
        pattern = self.attack_pattern
        attack_params = self.config.get('attack_params', {})
        interval = self.config.get('attack_interval', 60)
        
        if self.timer % interval != 0:
            return
        
        # 攻击逻辑在这里实现
        # 需要访问Bullet类时通过_sprite_groups获取
        if pattern == 'single':
            self._shoot_single()
        elif pattern == 'spread':
            self._shoot_spread(attack_params)
        elif pattern == 'burst':
            self._shoot_burst(attack_params)
        elif pattern == 'custom':
            custom_func = self.config.get('custom_attack')
            if custom_func:
                custom_func(self)
    
    def _shoot_single(self):
        """单发射击"""
        Bullet = _get_bullet_class()
        if Bullet:
            Bullet(self.rect.centerx, self.rect.bottom, 
                   is_enemy=True, color=self.config.get('bullet_color', (255, 100, 100)),
                   b_type="needle")
    
    def _shoot_spread(self, params):
        """散射"""
        Bullet = _get_bullet_class()
        if Bullet:
            spread_count = params.get('spread_count', 3)
            spread_angle = params.get('spread_angle', 45)
            for i in range(spread_count):
                angle = -spread_angle + (i * 2 * spread_angle / (spread_count - 1)) if spread_count > 1 else 0
                rad = math.radians(angle)
                vx = math.sin(rad) * 3
                vy = math.cos(rad) * 3
                Bullet(self.rect.centerx, self.rect.bottom, vx=vx, vy=vy,
                       is_enemy=True, color=self.config.get('bullet_color', (255, 100, 100)),
                       b_type="needle")
    
    def _shoot_burst(self, params):
        """连发"""
        Bullet = _get_bullet_class()
        if Bullet:
            burst_count = params.get('burst_count', 2)
            for i in range(burst_count):
                offset = (i - burst_count//2) * 10
                Bullet(self.rect.centerx + offset, self.rect.bottom,
                       is_enemy=True, color=self.config.get('bullet_color', (255, 100, 100)),
                       b_type="needle")
    
    def take_damage(self, damage):
        """
        受到伤害
        
        Args:
            damage: 伤害值
        
        Returns:
            bool: 是否存活
        """
        self.hp -= damage
        if self.hp <= 0:
            self.on_death()
            return False
        return True
    
    def on_death(self):
        """死亡时调用，处理特殊能力"""
        special_ability = self.config.get('special_ability', None)
        
        if special_ability == 'split_on_death':
            # 分裂：创建4个子体侦察机
            self._spawn_splits()
        elif special_ability == 'summon_minions':
            # 召唤：生成3个小型敌机
            self._spawn_minions()
        elif special_ability == 'bullet_refraction':
            # 折射机制由子弹系统处理，死亡时无特殊效果
            pass
        elif special_ability == 'spawn_biounits':
            # 生物单位：生成生物无人机
            self._spawn_biounits()
        elif special_ability == 'phase_shift':
            # 相位移位：只是视觉效果，死亡时无特殊能力
            pass
        elif special_ability == 'dual_shield':
            # 双盾系统由攻击逻辑处理
            pass
        elif special_ability == 'beam_attack':
            # 光束攻击：只是大型子弹，死亡时无特殊能力
            pass
        elif special_ability == 'chaotic_attack':
            # 混沌攻击：已在attack_pattern中实现
            pass
        elif special_ability == 'phase_dodge':
            # 相位闪躲：只影响伤害判定，死亡时无特殊能力
            pass
        
        # 最后销毁
        self.kill()
    
    def _spawn_splits(self):
        """裂解者分裂：生成4个子体"""
        Bullet = _get_bullet_class()
        if not Bullet:
            return
        
        # 生成4个子敌机（简化为特殊子弹）
        for i in range(4):
            angle = i * 90
            rad = math.radians(angle)
            vx = math.cos(rad) * 3
            vy = math.sin(rad) * 3
            
            # 使用特殊子弹表示分裂体
            Bullet(self.rect.centerx, self.rect.centery,
                  is_enemy=False, color=(100, 150, 220),
                  b_type="split_fragment")
    
    def _spawn_minions(self):
        """召唤师召唤：生成小型敌机"""
        # 调用工厂创建小型敌机
        for i in range(3):
            angle = i * 120
            rad = math.radians(angle)
            x = self.rect.centerx + math.cos(rad) * 50
            y = self.rect.centery + math.sin(rad) * 50
            
            # 生成规模较小的侦察机
            enemy_factory.create_enemy('scout_moth', spawn_pos=(x, y))
    
    def _spawn_biounits(self):
        """巢穴领主生成：生成生物无人机"""
        for i in range(3):
            angle = i * 120
            rad = math.radians(angle)
            x = self.rect.centerx + math.cos(rad) * 60
            y = self.rect.centery + math.sin(rad) * 60
            
            # 生成特殊的生物敌机（可使用现有的高速小敌机）
            enemy_factory.create_enemy('splitter_azurecore', spawn_pos=(x, y))


class EnemyFactory:
    """
    敌人工厂
    负责根据配置创建敌人实例
    """
    
    def __init__(self):
        self.enemy_configs = {}
    
    def register_type(self, type_id, config):
        """
        注册敌人类型
        
        Args:
            type_id: 类型ID
            config: 配置字典
        """
        self.enemy_configs[type_id] = config
    
    def create_enemy(self, type_id, spawn_pos=None, override_config=None):
        """
        创建敌人实例
        
        Args:
            type_id: 类型ID
            spawn_pos: 生成位置
            override_config: 覆盖配置
        
        Returns:
            Enemy: 敌人实例，如果类型不存在返回None
        """
        if type_id not in self.enemy_configs:
            return None
        
        config = self.enemy_configs[type_id].copy()
        if override_config:
            config.update(override_config)
        
        return Enemy(type_id, config, spawn_pos)
    
    def get_all_types(self):
        """获取所有已注册的类型"""
        return list(self.enemy_configs.keys())
    
    def load_from_dict(self, configs_dict):
        """
        从字典批量加载配置
        
        Args:
            configs_dict: {type_id: config} 格式的字典
        """
        for type_id, config in configs_dict.items():
            self.register_type(type_id, config)
    
    def load_from_json(self, json_path):
        """
        从JSON文件加载敌人配置
        
        Args:
            json_path: JSON文件路径
        """
        import json
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'enemies' in data:
                self.load_from_dict(data['enemies'])
                return True
        except Exception as e:
            print(f"Error loading enemy config from {json_path}: {e}")
        return False
    
    @property
    def types(self):
        """获取所有已注册的类型（为了兼容性）"""
        return self.enemy_configs


# 创建全局工厂实例
enemy_factory = EnemyFactory()


# ==================== 使用示例（注释掉的） ====================
"""
# 在main.py中初始化（在from sprites import *之后）：
from enemies import init_enemy_system, enemy_factory, Enemy

# 初始化（sprite组会自动使用config中的全局变量）
init_enemy_system()

# 注册敌人类型
enemy_factory.register_type('basic', {
    'hp': 50,
    'speed': 2.0,
    'radius': 20,
    'score': 100,
    'color': (255, 100, 100),
    'ai_behavior': 'straight',
    'attack_pattern': 'single',
    'attack_interval': 60,
    'elite_chance': 0.1
})

enemy_factory.register_type('zigzag', {
    'hp': 60,
    'speed': 2.5,
    'radius': 18,
    'score': 150,
    'color': (100, 200, 255),
    'ai_behavior': 'zigzag',
    'zigzag_speed': 3,
    'attack_pattern': 'spread',
    'attack_interval': 45,
    'elite_chance': 0.15
})

# 创建敌人
enemy = enemy_factory.create_enemy('basic')
enemy = enemy_factory.create_enemy('zigzag', spawn_pos=(300, -50))
"""
