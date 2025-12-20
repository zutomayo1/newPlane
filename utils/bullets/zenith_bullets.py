# -*- coding: utf-8 -*-
"""
分形天顶·ZENITH 弹幕系统
原型：Terraria - Zenith (The Ultimate Sword)

核心机制：
- 机体不发射子弹，而是把环绕的剑扔出去
- 剑像回旋镖一样飞出后返回
- 剑阵可格挡敌弹（分形护盾）
- 蓄力技能：所有剑合体成巨剑劈砍
"""

import pygame
import math
import random
import colorsys
from config import WIDTH, HEIGHT, all_sprites, bullets, mobs, enemy_bullets

# ==================== 名剑数据库 ====================
LEGENDARY_SWORDS = [
    {"id": 0, "name": "泰拉刃", "color": (0, 255, 100), "length": 22, "damage_mult": 1.2},
    {"id": 1, "name": "喵喵刃", "color": (255, 150, 200), "length": 20, "damage_mult": 1.0},
    {"id": 2, "name": "星怒", "color": (255, 255, 100), "length": 18, "damage_mult": 0.9},
    {"id": 3, "name": "星尘龙剑", "color": (0, 180, 255), "length": 24, "damage_mult": 1.3},
    {"id": 4, "name": "日耀喷发", "color": (255, 150, 0), "length": 21, "damage_mult": 1.1},
    {"id": 5, "name": "星旋剑", "color": (0, 220, 200), "length": 19, "damage_mult": 1.0},
    {"id": 6, "name": "星云剑", "color": (200, 80, 255), "length": 20, "damage_mult": 1.0},
    {"id": 7, "name": "流星剑", "color": (150, 200, 230), "length": 17, "damage_mult": 0.85},
    {"id": 8, "name": "种子弯刀", "color": (100, 200, 80), "length": 16, "damage_mult": 0.8},
    {"id": 9, "name": "无头骑士剑", "color": (255, 120, 0), "length": 23, "damage_mult": 1.15},
    {"id": 10, "name": "彩虹猫之刃", "color": (255, 100, 180), "length": 19, "damage_mult": 1.0},
    {"id": 11, "name": "铜短剑", "color": (200, 150, 100), "length": 10, "damage_mult": 0.5},  # 彩蛋
]

# ==================== 涂装主题 ====================
ZENITH_THEMES = {
    "zenith_default": {"core": (75, 0, 130), "blade": (255, 255, 255), "glow": (255, 0, 255), "pixel": (255, 255, 255), "trail": (147, 112, 219)},
}

def get_zenith_theme(style):
    return ZENITH_THEMES.get(style, ZENITH_THEMES["zenith_default"])


def _get_rainbow_color(frame, offset=0):
    """获取彩虹循环颜色"""
    hue = ((frame * 3 + offset) % 360) / 360.0
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    return (int(r * 255), int(g * 255), int(b * 255))


# ==================== 剑阵管理器 ====================
class SwordArray:
    """
    剑阵管理器 - 管理环绕机体的所有剑
    跟踪哪些剑在机体周围，哪些已经飞出去
    """
    
    def __init__(self, owner, style="zenith_default"):
        self.owner = owner
        self.style = style
        self.swords = []  # 当前在机体周围的剑
        self.flying_swords = []  # 飞出去的剑（引用）
        self.next_sword_index = 0  # 下一把要发射的剑
        
        # 初始化12把剑
        for i, sword_data in enumerate(LEGENDARY_SWORDS):
            self.swords.append({
                'data': sword_data,
                'angle': i * 30,  # 初始角度
                'orbit_radius': 45,
                'available': True,  # 是否可用（未飞出）
                'return_timer': 0,
            })
    
    def get_next_available_sword(self):
        """获取下一把可用的剑"""
        for i in range(len(self.swords)):
            idx = (self.next_sword_index + i) % len(self.swords)
            if self.swords[idx]['available']:
                self.next_sword_index = (idx + 1) % len(self.swords)
                return idx, self.swords[idx]
        return None, None
    
    def mark_sword_flying(self, idx):
        """标记剑已飞出"""
        if idx is not None and idx < len(self.swords):
            self.swords[idx]['available'] = False
    
    def mark_sword_returned(self, idx):
        """标记剑已返回"""
        if idx is not None and idx < len(self.swords):
            self.swords[idx]['available'] = True
    
    def get_available_count(self):
        """获取可用剑数量"""
        return sum(1 for s in self.swords if s['available'])
    
    def get_all_sword_positions(self, cx, cy, frame):
        """获取所有剑的位置（用于渲染和碰撞）"""
        positions = []
        for i, sword in enumerate(self.swords):
            if sword['available']:
                angle = frame * 4 + sword['angle']
                rad = math.radians(angle)
                sx = cx + math.cos(rad) * sword['orbit_radius']
                sy = cy + math.sin(rad) * sword['orbit_radius']
                positions.append({
                    'x': sx, 'y': sy,
                    'angle': angle + 90,
                    'data': sword['data'],
                    'index': i
                })
        return positions


# ==================== 全局剑阵实例 ====================
_sword_arrays = {}  # owner_id -> SwordArray

def get_sword_array(owner, style="zenith_default"):
    """获取或创建剑阵"""
    owner_id = id(owner)
    if owner_id not in _sword_arrays:
        _sword_arrays[owner_id] = SwordArray(owner, style)
    return _sword_arrays[owner_id]

def clear_sword_array(owner):
    """清除剑阵"""
    owner_id = id(owner)
    if owner_id in _sword_arrays:
        del _sword_arrays[owner_id]


# ==================== 主武器：天顶剑影 ====================
class ThrowingSwordBullet(pygame.sprite.Sprite):
    """
    天顶剑影 - 还原泰拉瑞亚天顶剑攻击
    
    核心机制：
    1. 剑从玩家位置向前飞出（扁平椭圆轨迹的上半弧）
    2. 到达最远点后，以更快速度从下半弧飞回玩家
    3. 每把剑的角度有微小随机偏移，形成扇形剑幕
    4. 剑身高速自旋，拖着长残影
    5. 每把剑颜色/外观不同
    """
    
    def __init__(self, x, y, damage, owner=None, style="zenith_default", sword_array=None, is_first=False):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.is_enemy = False
        self.style = style
        self.is_first = is_first
        
        # 随机选择一把名剑的外观
        self.sword_data = random.choice(LEGENDARY_SWORDS)
        self.damage = int(damage * self.sword_data.get('damage_mult', 1.0))
        
        # 起点（玩家位置）
        self.start_x = float(x)
        self.start_y = float(y)
        self.float_x = float(x)
        self.float_y = float(y)
        
        # 扁平椭圆参数
        # 椭圆长轴（飞行距离）= 屏幕高度的60-80%
        self.max_distance = HEIGHT * (0.6 + random.uniform(0, 0.2))
        # 椭圆短轴（横向偏移）= 长轴的15-25%，形成扁平椭圆
        self.lateral_amplitude = self.max_distance * (0.15 + random.uniform(0, 0.1))
        
        # 飞行方向（向上为主，带随机扇形偏移 ±15度）
        self.base_angle = -90 + random.uniform(-15, 15)  # -90是正上方
        
        # 横向弯曲方向（左弯或右弯）
        self.curve_direction = random.choice([-1, 1])
        
        # 飞行阶段：0~1 飞出，1~2 返回
        self.progress = 0
        self.outward_speed = 0.025 + random.uniform(-0.005, 0.005)  # 飞出速度
        self.return_speed = 0.045 + random.uniform(-0.005, 0.005)   # 返回速度（更快）
        
        # 剑身高速自旋（每秒3-5圈 = 每帧 18-30度）
        self.sword_rotation = random.uniform(0, 360)
        self.sword_rotation_speed = random.uniform(18, 30) * random.choice([-1, 1])
        
        self.frame = 0
        self.lifetime = 180
        
        # 穿透命中记录（每8帧可再次命中同一敌人）
        self.hit_enemies = {}
        self.hit_cooldown = 8
        
        # 残影系统 - 存储剑身的历史位置和旋转
        self.afterimages = []
        self.max_afterimages = 10
        
        self.size = 80
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        self.sword_rotation += self.sword_rotation_speed
        
        # 更新穿透冷却
        to_remove = []
        for enemy_id, cooldown in self.hit_enemies.items():
            self.hit_enemies[enemy_id] = cooldown - 1
            if self.hit_enemies[enemy_id] <= 0:
                to_remove.append(enemy_id)
        for eid in to_remove:
            del self.hit_enemies[eid]
        
        # 更新起点（跟随玩家）
        if self.owner and self.owner.alive():
            # 只在返回阶段更新目标点
            if self.progress >= 1:
                self.start_x = float(self.owner.rect.centerx)
                self.start_y = float(self.owner.rect.centery)
        
        # 保存当前位置作为残影
        if self.frame % 2 == 0:
            self.afterimages.append({
                'x': self.float_x,
                'y': self.float_y,
                'rotation': self.sword_rotation,
                'alpha': 200
            })
            if len(self.afterimages) > self.max_afterimages:
                self.afterimages.pop(0)
        
        # 更新残影透明度
        for img in self.afterimages:
            img['alpha'] = max(0, img['alpha'] - 20)
        
        # 飞行进度更新
        if self.progress < 1:
            # 飞出阶段
            self.progress += self.outward_speed
        else:
            # 返回阶段（更快）
            self.progress += self.return_speed
        
        # 计算当前位置（扁平椭圆轨迹）
        self._update_position()
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 完成往返后消失
        if self.progress >= 2:
            self.kill()
            return
        
        if self.frame > self.lifetime:
            self.kill()
            return
        
        self._check_collision()
        self._render()
    
    def _update_position(self):
        """计算扁平椭圆轨迹上的位置"""
        # 将progress映射到椭圆参数
        # 0~1: 椭圆上半弧（飞出）
        # 1~2: 椭圆下半弧（返回）
        
        if self.progress < 1:
            # 飞出阶段：沿椭圆上半弧
            t = self.progress  # 0 -> 1
            # 前进距离（沿主方向）
            forward_dist = self.max_distance * t
            # 横向偏移（正弦曲线，形成弧线）
            lateral_offset = self.lateral_amplitude * math.sin(t * math.pi) * self.curve_direction
        else:
            # 返回阶段：沿椭圆下半弧
            t = self.progress - 1  # 0 -> 1
            # 前进距离（从最远点返回）
            forward_dist = self.max_distance * (1 - t)
            # 横向偏移（反向弧线）
            lateral_offset = -self.lateral_amplitude * math.sin(t * math.pi) * self.curve_direction
        
        # 将局部坐标转换为世界坐标
        angle_rad = math.radians(self.base_angle)
        
        # 主方向向量（飞行方向）
        forward_x = math.cos(angle_rad) * forward_dist
        forward_y = math.sin(angle_rad) * forward_dist
        
        # 垂直方向向量（横向偏移）
        perp_angle = angle_rad + math.pi / 2
        lateral_x = math.cos(perp_angle) * lateral_offset
        lateral_y = math.sin(perp_angle) * lateral_offset
        
        # 最终位置 = 起点 + 前进 + 横向
        self.float_x = self.start_x + forward_x + lateral_x
        self.float_y = self.start_y + forward_y + lateral_y
    
    def _check_collision(self):
        """碰撞检测 - 穿透但有冷却"""
        for mob in mobs:
            mob_id = id(mob)
            if mob_id in self.hit_enemies:
                continue
            
            if self.rect.colliderect(mob.rect):
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
                    self.hit_enemies[mob_id] = self.hit_cooldown
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        sword_color = self.sword_data['color']
        sword_length = self.sword_data['length']
        
        # 绘制残影（剑身的半透明副本）
        for i, img in enumerate(self.afterimages):
            if img['alpha'] > 0:
                rel_x = int(img['x'] - self.float_x + cx)
                rel_y = int(img['y'] - self.float_y + cy)
                
                if 0 < rel_x < self.size and 0 < rel_y < self.size:
                    rad = math.radians(img['rotation'])
                    alpha = img['alpha']
                    trail_color = _get_rainbow_color(self.frame + i * 5, self.sword_data['id'] * 30)
                    self._draw_sword_afterimage(rel_x, rel_y, rad, sword_length * 0.85, trail_color, alpha)
        
        # 绘制主剑身（详细造型）
        rad = math.radians(self.sword_rotation)
        self._draw_detailed_sword(cx, cy, rad, sword_length, sword_color)
    
    def _draw_sword_afterimage(self, cx, cy, rad, length, color, alpha):
        """绘制残影剑（简化但带光晕）- 性能优化版"""
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)
        
        tip_x = cx + cos_r * length
        tip_y = cy + sin_r * length
        hilt_x = cx - cos_r * 6
        hilt_y = cy - sin_r * 6
        
        # 直接在 self.image 上绘制，避免创建临时 Surface
        hilt_pos = (int(hilt_x), int(hilt_y))
        tip_pos = (int(tip_x), int(tip_y))
        
        # 残影光晕（合并绘制）
        pygame.draw.line(self.image, (*color, alpha // 3), hilt_pos, tip_pos, 8)
        pygame.draw.line(self.image, (*color, alpha // 2), hilt_pos, tip_pos, 4)
        pygame.draw.line(self.image, (255, 255, 255, alpha // 3), hilt_pos, tip_pos, 2)
    
    def _draw_detailed_sword(self, cx, cy, rad, length, base_color):
        """
        绘制有质感的剑 - 性能优化版
        直接在 self.image 上绘制，避免创建多个临时 Surface
        """
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)
        perp_cos = math.cos(rad + math.pi / 2)
        perp_sin = math.sin(rad + math.pi / 2)
        
        # 关键点（缓存计算结果）
        tip_x = cx + cos_r * length
        tip_y = cy + sin_r * length
        guard_x = cx - cos_r * 3
        guard_y = cy - sin_r * 3
        hilt_x = cx - cos_r * 10
        hilt_y = cy - sin_r * 10
        
        tip_pos = (int(tip_x), int(tip_y))
        guard_pos = (int(guard_x), int(guard_y))
        hilt_pos = (int(hilt_x), int(hilt_y))
        center_pos = (int(cx), int(cy))
        
        # ========== 1. 外层光晕（直接绘制）==========
        for g in range(5):
            glow_alpha = 50 - g * 10
            glow_width = 20 - g * 4
            if glow_width > 0 and glow_alpha > 0:
                pygame.draw.line(self.image, (*base_color, glow_alpha),
                               center_pos, tip_pos, glow_width)
        
        # ========== 2. 动态能量流 ==========
        energy_phase = (self.frame * 0.15) % 1.0
        sword_id_offset = self.sword_data['id'] * 30
        for i in range(4):
            e_t = (energy_phase + i * 0.25) % 1.0
            e_x = int(cx + cos_r * (length * e_t))
            e_y = int(cy + sin_r * (length * e_t))
            e_alpha = int(100 * (1 - abs(e_t - 0.5) * 2))
            if e_alpha > 0:
                e_color = _get_rainbow_color(self.frame + i * 20, sword_id_offset)
                pygame.draw.circle(self.image, (*e_color, e_alpha), (e_x, e_y), 4)
        
        # ========== 3. 剑身（多层渐变金属质感）==========
        blade_width = 5
        
        # 剑身轮廓点
        blade_pts = [
            (int(guard_x + perp_cos * blade_width), int(guard_y + perp_sin * blade_width)),
            (int(tip_x + perp_cos * 1.5), int(tip_y + perp_sin * 1.5)),
            (int(tip_x + cos_r * 4), int(tip_y + sin_r * 4)),
            (int(tip_x - perp_cos * 1.5), int(tip_y - perp_sin * 1.5)),
            (int(guard_x - perp_cos * blade_width), int(guard_y - perp_sin * blade_width)),
        ]
        
        # 底层：深色轮廓
        dark_color = (max(0, base_color[0] - 60), max(0, base_color[1] - 60), max(0, base_color[2] - 60), 255)
        pygame.draw.polygon(self.image, dark_color, blade_pts)
        
        # 中层：主色
        bw1 = blade_width - 1
        inner_pts = [
            (int(guard_x + perp_cos * bw1), int(guard_y + perp_sin * bw1)),
            (int(tip_x + perp_cos), int(tip_y + perp_sin)),
            (int(tip_x + cos_r * 3), int(tip_y + sin_r * 3)),
            (int(tip_x - perp_cos), int(tip_y - perp_sin)),
            (int(guard_x - perp_cos * bw1), int(guard_y - perp_sin * bw1)),
        ]
        pygame.draw.polygon(self.image, (*base_color, 255), inner_pts)
        
        # 顶层：高光带
        highlight_color = (min(255, base_color[0] + 80), min(255, base_color[1] + 80), min(255, base_color[2] + 80), 200)
        hl_start = (int(guard_x + perp_cos * blade_width * 0.3), int(guard_y + perp_sin * blade_width * 0.3))
        hl_end = (int(tip_x + perp_cos * 0.5), int(tip_y + perp_sin * 0.5))
        pygame.draw.line(self.image, highlight_color, hl_start, hl_end, 2)
        
        # 白色高光点（每3帧一次）
        if self.frame % 3 == 0:
            flash_phase = (self.frame * 0.1) % 1.0
            flash_x = int(guard_x + cos_r * length * 0.3 * flash_phase + perp_cos * 2)
            flash_y = int(guard_y + sin_r * length * 0.3 * flash_phase + perp_sin * 2)
            pygame.draw.circle(self.image, (255, 255, 255, 200), (flash_x, flash_y), 2)
        
        # ========== 4. 剑刃边缘光 ==========
        edge_start = (int(guard_x + perp_cos * blade_width), int(guard_y + perp_sin * blade_width))
        edge_end = (int(tip_x + cos_r * 4), int(tip_y + sin_r * 4))
        pygame.draw.line(self.image, (255, 255, 255, 150), edge_start, edge_end, 1)
        
        # ========== 5. 护手 ==========
        guard_len = 8
        guard_start = (int(guard_x + perp_cos * guard_len), int(guard_y + perp_sin * guard_len))
        guard_end = (int(guard_x - perp_cos * guard_len), int(guard_y - perp_sin * guard_len))
        
        for i in range(3):
            g_width = 4 - i
            g_color = (200 - i * 30, 170 - i * 25, 80 - i * 15, 255)
            pygame.draw.line(self.image, g_color, guard_start, guard_end, g_width)
        
        # 护手高光
        pygame.draw.line(self.image, (255, 240, 200, 180),
                        (int(guard_x + perp_cos * (guard_len - 1)), int(guard_y + perp_sin * (guard_len - 1))),
                        (int(guard_x + perp_cos * 2), int(guard_y + perp_sin * 2)), 1)
        
        # ========== 6. 剑柄 ==========
        hilt_segments = 4
        hilt_dx = hilt_x - guard_x
        hilt_dy = hilt_y - guard_y
        for i in range(hilt_segments):
            t = i / hilt_segments
            t_next = (i + 1) / hilt_segments
            seg_start = (int(guard_x + hilt_dx * t), int(guard_y + hilt_dy * t))
            seg_end = (int(guard_x + hilt_dx * t_next), int(guard_y + hilt_dy * t_next))
            seg_color = (90, 60, 40, 255) if i % 2 == 0 else (70, 45, 30, 255)
            pygame.draw.line(self.image, seg_color, seg_start, seg_end, 4)
        
        # ========== 7. 柄端宝石 ==========
        gem_color = _get_rainbow_color(self.frame * 2, self.sword_data['id'] * 50)
        
        # 宝石光晕
        for g in range(3):
            g_r = 6 - g * 2
            g_alpha = 80 - g * 25
            if g_alpha > 0:
                pygame.draw.circle(self.image, (*gem_color, g_alpha), hilt_pos, g_r)
        
        # 宝石主体
        pygame.draw.circle(self.image, gem_color, hilt_pos, 3)
        pygame.draw.circle(self.image, (255, 255, 255), hilt_pos, 2)
        pygame.draw.circle(self.image, (255, 255, 255, 255), (int(hilt_x - 1), int(hilt_y - 1)), 1)
        
        # ========== 8. 剑尖闪光 ==========
        if self.frame % 4 < 2:
            tip_flash_pos = (int(tip_x + cos_r * 2), int(tip_y + sin_r * 2))
            pygame.draw.circle(self.image, (255, 255, 255, 200), tip_flash_pos, 3)
            pygame.draw.circle(self.image, (*base_color, 150), tip_flash_pos, 5)


# ==================== 分形护盾 (被动) ====================
class FractalShield(pygame.sprite.Sprite):
    """
    分形护盾 - 被动系统
    
    机制：
    - 环绕机体的剑阵可以格挡敌人子弹
    - 每把在位的剑都有格挡范围
    - 格挡时消耗护盾耐久度
    - 耐久度自动回复
    """
    
    def __init__(self, owner, style="zenith_default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.sword_array = get_sword_array(owner, style)
        
        self.frame = 0
        self.durability = 100
        self.max_durability = 100
        self.regen_rate = 0.08  # 每帧回复
        self.block_cost = 8  # 每次格挡消耗
        
        self.shield_radius = 55  # 剑阵格挡半径
        self.block_flash = 0  # 格挡闪光效果
        
        self.size = 140
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        all_sprites.add(self)
    
    def update(self):
        if not self.owner or not self.owner.alive():
            clear_sword_array(self.owner)
            self.kill()
            return
        
        self.frame += 1
        self.rect.center = self.owner.rect.center
        
        # 耐久回复
        if self.durability < self.max_durability:
            self.durability = min(self.max_durability, self.durability + self.regen_rate)
        
        # 格挡闪光衰减
        if self.block_flash > 0:
            self.block_flash -= 5
        
        # 检测并格挡敌弹
        self._block_bullets()
        self._render()
    
    def _block_bullets(self):
        """格挡敌人子弹"""
        if self.durability <= 0:
            return
        
        # 获取当前剑的位置
        sword_positions = self.sword_array.get_all_sword_positions(
            self.owner.rect.centerx, self.owner.rect.centery, self.frame
        )
        
        if not sword_positions:
            return  # 没有剑在位
        
        for bullet in list(enemy_bullets):
            bx, by = bullet.rect.centerx, bullet.rect.centery
            
            # 检查是否在剑阵范围内
            for sword_pos in sword_positions:
                dx = bx - sword_pos['x']
                dy = by - sword_pos['y']
                dist = math.hypot(dx, dy)
                
                if dist < 25:  # 每把剑的格挡范围
                    bullet.kill()
                    self.durability -= self.block_cost
                    self.block_flash = 100
                    # 可以添加格挡粒子效果
                    break
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        if self.durability <= 0:
            return
        
        alpha_mult = self.durability / self.max_durability
        
        # 绘制剑阵（视觉层 - 实际剑由机体渲染）
        sword_positions = self.sword_array.get_all_sword_positions(cx, cy, self.frame)
        
        for sword_pos in sword_positions:
            sx, sy = sword_pos['x'], sword_pos['y']
            sword_angle = sword_pos['angle']
            sword_data = sword_pos['data']
            rad = math.radians(sword_angle)
            length = sword_data['length'] * 0.7
            color = sword_data['color']
            
            # 剑的发光效果
            glow_alpha = int(80 * alpha_mult)
            if self.block_flash > 0:
                glow_alpha = min(255, glow_alpha + self.block_flash)
            
            tip_x = sx + math.cos(rad) * length
            tip_y = sy + math.sin(rad) * length
            
            # 发光
            glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.line(glow_surf, (*color, glow_alpha), (15, 15),
                             (15 + math.cos(rad) * length, 15 + math.sin(rad) * length), 8)
            self.image.blit(glow_surf, (int(sx - 15), int(sy - 15)))
            
            # 剑身
            pygame.draw.line(self.image, color, (sx, sy), (tip_x, tip_y), 3)
            pygame.draw.circle(self.image, (255, 255, 255), (int(tip_x), int(tip_y)), 2)
        
        # 格挡时的闪光环
        if self.block_flash > 0:
            flash_alpha = min(100, self.block_flash)
            flash_surf = pygame.Surface((self.shield_radius * 2 + 4, self.shield_radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 255, 255, flash_alpha), 
                              (self.shield_radius + 2, self.shield_radius + 2), self.shield_radius, 2)
            self.image.blit(flash_surf, (cx - self.shield_radius - 2, cy - self.shield_radius - 2))


# ==================== 棱镜折射 (蓄力技能) ====================
class PrismBreakSkill(pygame.sprite.Sprite):
    """
    棱镜折射 - 蓄力技能
    
    机制：
    - 所有环绕的剑瞬间向中心聚合
    - 合体成一把巨型彩虹剑
    - 向前方劈砍，造成巨额近战伤害
    - 劈砍范围内的所有敌人都受到伤害
    
    学习克苏鲁风格：华丽的聚合特效、巨剑光晕、劈砍残影、粒子爆发
    """
    
    def __init__(self, owner, damage, style="zenith_default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        self.sword_array = get_sword_array(owner, style)
        
        self.frame = 0
        self.duration = 100  # 延长持续时间
        
        # 阶段：merge(合体) -> slash(劈砍) -> disperse(散开)
        self.phase = "merge"
        self.merge_duration = 25
        self.slash_duration = 40
        self.disperse_duration = 35
        
        self.slash_angle = 0
        self.slash_start_angle = -150
        self.slash_end_angle = 150
        self.hit_enemies = set()
        
        # 粒子系统
        self.particles = []
        self.energy_lines = []
        self.slash_waves = []
        self.explosions = []
        self.sword_ghosts = []  # 剑的幻影
        
        # 聚合剑的状态
        self.merging_swords = []
        for i, sword_data in enumerate(LEGENDARY_SWORDS):
            base_angle = i * 30
            self.merging_swords.append({
                'data': sword_data,
                'angle': base_angle,
                'radius': 80,
                'rotation': random.uniform(0, 360),
                'spin_speed': random.uniform(8, 15),
            })
        
        self.size = (WIDTH, HEIGHT)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _add_particle(self, x, y, vx, vy, color, life, size=4):
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size
        })
    
    def _add_explosion(self, x, y, color, scale=1.0):
        self.explosions.append({
            'x': x, 'y': y, 'color': color, 'frame': 0, 'max_frame': 20, 'scale': scale
        })
    
    def _add_slash_wave(self, cx, cy, angle, color):
        self.slash_waves.append({
            'cx': cx, 'cy': cy, 'angle': angle, 'color': color,
            'life': 12, 'max_life': 12
        })
    
    def update(self):
        self.frame += 1
        cx = self.owner.rect.centerx if self.owner else WIDTH // 2
        cy = self.owner.rect.centery if self.owner else HEIGHT // 2
        
        if self.frame <= self.merge_duration:
            self.phase = "merge"
            progress = self.frame / self.merge_duration
            
            # 更新聚合剑
            for sword in self.merging_swords:
                sword['radius'] = 80 * (1 - progress * 0.95)
                sword['angle'] += 8
                sword['rotation'] += sword['spin_speed']
                
                # 向心能量线
                if self.frame % 3 == 0:
                    rad = math.radians(sword['angle'])
                    sx = cx + math.cos(rad) * sword['radius']
                    sy = cy + math.sin(rad) * sword['radius']
                    self.energy_lines.append({
                        'x': sx, 'y': sy, 'tx': cx, 'ty': cy,
                        'color': sword['data']['color'], 'life': 10
                    })
                    
                    # 聚合粒子
                    self._add_particle(sx, sy,
                                     (cx - sx) * 0.05, (cy - sy) * 0.05,
                                     sword['data']['color'], 15, 4)
        
        elif self.frame <= self.merge_duration + self.slash_duration:
            self.phase = "slash"
            slash_progress = (self.frame - self.merge_duration) / self.slash_duration
            self.slash_angle = self.slash_start_angle + (self.slash_end_angle - self.slash_start_angle) * slash_progress
            
            # 劈砍波纹
            if self.frame % 2 == 0:
                color = _get_rainbow_color(self.frame * 5, 0)
                self._add_slash_wave(cx, cy, self.slash_angle - 90, color)
            
            # 劈砍粒子
            rad = math.radians(self.slash_angle - 90)
            for i in range(3):
                dist = random.uniform(50, 250)
                px = cx + math.cos(rad) * dist
                py = cy + math.sin(rad) * dist
                color = _get_rainbow_color(self.frame * 3, i * 40)
                self._add_particle(px, py,
                                 random.uniform(-3, 3), random.uniform(-3, 3),
                                 color, 20, 5)
            
            # 检测伤害
            self._check_slash_damage(cx, cy)
            
        else:
            self.phase = "disperse"
            disperse_progress = (self.frame - self.merge_duration - self.slash_duration) / self.disperse_duration
            
            # 更新散开的剑
            for i, sword in enumerate(self.merging_swords):
                sword['radius'] = 5 + disperse_progress * 100
                sword['angle'] += 5 * (1 - disperse_progress)
                
                # 添加剑幻影
                if self.frame % 4 == 0:
                    rad = math.radians(sword['angle'])
                    sx = cx + math.cos(rad) * sword['radius']
                    sy = cy + math.sin(rad) * sword['radius']
                    self.sword_ghosts.append({
                        'x': sx, 'y': sy, 'angle': sword['rotation'],
                        'color': sword['data']['color'], 'life': 15, 'size': 1 - disperse_progress * 0.5
                    })
        
        # 更新能量线（性能优化）
        new_lines = []
        for line in self.energy_lines:
            line['life'] -= 1
            if line['life'] > 0:
                new_lines.append(line)
        self.energy_lines = new_lines
        
        # 更新斩击波（性能优化）
        new_waves = []
        for wave in self.slash_waves:
            wave['life'] -= 1
            if wave['life'] > 0:
                new_waves.append(wave)
        self.slash_waves = new_waves
        
        # 更新剑幻影（性能优化）
        new_ghosts = []
        for ghost in self.sword_ghosts:
            ghost['life'] -= 1
            if ghost['life'] > 0:
                new_ghosts.append(ghost)
        self.sword_ghosts = new_ghosts
        
        # 更新爆炸（性能优化）
        new_explosions = []
        for exp in self.explosions:
            exp['frame'] += 1
            if exp['frame'] < exp['max_frame']:
                new_explosions.append(exp)
        self.explosions = new_explosions
        
        if self.frame > self.duration:
            self.kill()
            return
        
        self._render()
    
    def _check_slash_damage(self, cx, cy):
        """检测劈砍伤害"""
        slash_range = 280
        
        rad = math.radians(self.slash_angle - 90)
        
        for mob in mobs:
            if id(mob) in self.hit_enemies:
                continue
            
            dx = mob.rect.centerx - cx
            dy = mob.rect.centery - cy
            dist = math.hypot(dx, dy)
            
            if dist > slash_range:
                continue
            
            mob_angle = math.degrees(math.atan2(dy, dx))
            angle_diff = abs((mob_angle - self.slash_angle + 180) % 360 - 180)
            
            if angle_diff < 50:
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage * 5)
                    self.hit_enemies.add(id(mob))
                    
                    # 命中爆炸
                    color = _get_rainbow_color(self.frame * 3, 0)
                    self._add_explosion(mob.rect.centerx, mob.rect.centery, color, 1.5)
                    
                    # 命中粒子
                    for _ in range(15):
                        angle = random.uniform(0, 360)
                        speed = random.uniform(5, 12)
                        self._add_particle(mob.rect.centerx, mob.rect.centery,
                                         math.cos(math.radians(angle)) * speed,
                                         math.sin(math.radians(angle)) * speed,
                                         color, 25, 6)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx = self.owner.rect.centerx if self.owner else WIDTH // 2
        cy = self.owner.rect.centery if self.owner else HEIGHT // 2
        
        if self.phase == "merge":
            progress = self.frame / self.merge_duration
            
            # 背景能量漩涡
            for i in range(5):
                vortex_r = 100 - i * 15 - progress * 50
                if vortex_r > 0:
                    color = _get_rainbow_color(self.frame * 2, i * 30)
                    alpha = int((80 - i * 12) * (1 - progress * 0.5))
                    for j in range(8):
                        angle = j * 45 + self.frame * (4 - i)
                        rad = math.radians(angle)
                        ax = cx + math.cos(rad) * vortex_r
                        ay = cy + math.sin(rad) * vortex_r
                        pygame.draw.circle(self.image, (*color, alpha), (int(ax), int(ay)), 4 - i // 2)
            
            # 能量线
            for line in self.energy_lines:
                alpha = int(200 * line['life'] / 10)
                for i in range(3):
                    a = max(0, alpha - i * 50)
                    w = 3 - i
                    pygame.draw.line(self.image, (*line['color'], a),
                                   (int(line['x']), int(line['y'])),
                                   (int(line['tx']), int(line['ty'])), w)
            
            # 聚合中的剑
            for sword in self.merging_swords:
                rad = math.radians(sword['angle'])
                sx = cx + math.cos(rad) * sword['radius']
                sy = cy + math.sin(rad) * sword['radius']
                
                color = sword['data']['color']
                length = sword['data']['length'] * (1 - progress * 0.3)
                
                # 剑指向中心
                sword_rad = math.radians(sword['rotation'])
                tip_x = sx + math.cos(sword_rad) * length
                tip_y = sy + math.sin(sword_rad) * length
                
                # 多层光晕
                for i in range(4):
                    glow_alpha = 150 - i * 30
                    glow_width = 8 - i * 2
                    pygame.draw.line(self.image, (*color, glow_alpha),
                                   (int(sx), int(sy)), (int(tip_x), int(tip_y)), glow_width)
                
                # 剑尖光芒
                pygame.draw.circle(self.image, (255, 255, 255, 200), (int(tip_x), int(tip_y)), 4)
            
            # 中心聚合光芒
            glow_r = int(30 * progress)
            if glow_r > 0:
                for i in range(5):
                    r = glow_r - i * 4
                    if r > 0:
                        color = _get_rainbow_color(self.frame * 3, i * 40)
                        alpha = 200 - i * 30
                        pygame.draw.circle(self.image, (*color, alpha), (cx, cy), r)
        
        elif self.phase == "slash":
            rad = math.radians(self.slash_angle - 90)
            giant_sword_length = 300
            
            tip_x = cx + math.cos(rad) * giant_sword_length
            tip_y = cy + math.sin(rad) * giant_sword_length
            
            # 劈砍波纹
            for wave in self.slash_waves:
                wave_progress = 1 - wave['life'] / wave['max_life']
                wave_length = 280 * (0.3 + wave_progress * 0.7)
                wave_alpha = int(150 * wave['life'] / wave['max_life'])
                wave_rad = math.radians(wave['angle'])
                
                wave_tip_x = wave['cx'] + math.cos(wave_rad) * wave_length
                wave_tip_y = wave['cy'] + math.sin(wave_rad) * wave_length
                
                for i in range(3):
                    a = max(0, wave_alpha - i * 40)
                    w = 6 - i * 2
                    offset = (i - 1) * 8
                    ox = math.cos(wave_rad + math.pi / 2) * offset
                    oy = math.sin(wave_rad + math.pi / 2) * offset
                    pygame.draw.line(self.image, (*wave['color'], a),
                                   (int(wave['cx'] + ox), int(wave['cy'] + oy)),
                                   (int(wave_tip_x + ox), int(wave_tip_y + oy)), w)
            
            # 巨剑外层光晕
            for i in range(6):
                glow_alpha = 80 - i * 12
                glow_width = 20 - i * 3
                color = _get_rainbow_color(self.frame * 4, i * 30)
                pygame.draw.line(self.image, (*color, glow_alpha),
                               (cx, cy), (int(tip_x), int(tip_y)), glow_width)
            
            # 彩虹巨剑核心（多层）
            for i in range(10):
                color = _get_rainbow_color(self.frame * 4, i * 36)
                offset = (i - 5) * 5
                
                offset_x = math.cos(rad + math.pi / 2) * offset
                offset_y = math.sin(rad + math.pi / 2) * offset
                
                pygame.draw.line(self.image, (*color, 220), 
                                (cx + offset_x, cy + offset_y),
                                (tip_x + offset_x, tip_y + offset_y), 
                                14 - abs(i - 5))
            
            # 剑身中央高光
            pygame.draw.line(self.image, (255, 255, 255, 200),
                           (cx, cy), (int(tip_x), int(tip_y)), 4)
            
            # 剑尖爆发光芒
            for i in range(8):
                flare_angle = i * 45 + self.frame * 10
                flare_length = 25 + 10 * math.sin(self.frame * 0.3)
                flare_rad = math.radians(flare_angle)
                fx = tip_x + math.cos(flare_rad) * flare_length
                fy = tip_y + math.sin(flare_rad) * flare_length
                color = _get_rainbow_color(self.frame * 3, i * 45)
                pygame.draw.line(self.image, (*color, 180),
                               (int(tip_x), int(tip_y)), (int(fx), int(fy)), 3)
            
            pygame.draw.circle(self.image, (255, 255, 255), (int(tip_x), int(tip_y)), 18)
            pygame.draw.circle(self.image, (255, 255, 200), (int(tip_x), int(tip_y)), 12)
            
            # 劈砍残影
            for j in range(6):
                trail_angle = self.slash_angle - 90 - j * 12
                trail_rad = math.radians(trail_angle)
                trail_length = giant_sword_length * (1 - j * 0.08)
                trail_tip_x = cx + math.cos(trail_rad) * trail_length
                trail_tip_y = cy + math.sin(trail_rad) * trail_length
                
                trail_alpha = 120 - j * 18
                color = _get_rainbow_color(self.frame * 3, j * 50)
                pygame.draw.line(self.image, (*color, trail_alpha),
                                (cx, cy), (int(trail_tip_x), int(trail_tip_y)), 10 - j)
            
            # 剑柄能量环
            for i in range(3):
                ring_r = 15 + i * 8
                color = _get_rainbow_color(self.frame * 2, i * 60)
                pygame.draw.circle(self.image, (*color, 100 - i * 25), (cx, cy), ring_r, 2)
        
        elif self.phase == "disperse":
            disperse_progress = (self.frame - self.merge_duration - self.slash_duration) / self.disperse_duration
            
            # 剑幻影
            for ghost in self.sword_ghosts:
                alpha = int(180 * ghost['life'] / 15)
                length = 20 * ghost['size']
                rad = math.radians(ghost['angle'])
                tip_x = ghost['x'] + math.cos(rad) * length
                tip_y = ghost['y'] + math.sin(rad) * length
                
                pygame.draw.line(self.image, (*ghost['color'], alpha),
                               (int(ghost['x']), int(ghost['y'])),
                               (int(tip_x), int(tip_y)), 3)
            
            # 散开的剑
            for sword in self.merging_swords:
                rad = math.radians(sword['angle'])
                sx = cx + math.cos(rad) * sword['radius']
                sy = cy + math.sin(rad) * sword['radius']
                
                color = sword['data']['color']
                alpha = int(255 * (1 - disperse_progress))
                length = sword['data']['length'] * (1 - disperse_progress * 0.5)
                
                sword_rad = math.radians(sword['rotation'] + self.frame * 3)
                tip_x = sx + math.cos(sword_rad) * length
                tip_y = sy + math.sin(sword_rad) * length
                
                # 光晕
                for i in range(3):
                    a = max(0, alpha - i * 60)
                    w = 6 - i * 2
                    pygame.draw.line(self.image, (*color, a),
                                   (int(sx), int(sy)), (int(tip_x), int(tip_y)), w)
                
                # 剑尾粒子
                pygame.draw.circle(self.image, (*color, alpha // 2), (int(sx), int(sy)), 4)
            
            # 中心余晖
            glow_r = int(40 * (1 - disperse_progress))
            if glow_r > 0:
                for i in range(3):
                    r = glow_r - i * 8
                    if r > 0:
                        color = _get_rainbow_color(self.frame * 2, i * 50)
                        alpha = int(150 * (1 - disperse_progress) - i * 30)
                        if alpha > 0:
                            pygame.draw.circle(self.image, (*color, alpha), (cx, cy), r)
        
        # 绘制爆炸
        for exp in self.explosions:
            progress = exp['frame'] / exp['max_frame']
            scale = exp['scale']
            
            for i in range(4):
                r = int((30 + progress * 50 - i * 10) * scale)
                if r > 0:
                    alpha = int(200 * (1 - progress) - i * 35)
                    if alpha > 0:
                        pygame.draw.circle(self.image, (*exp['color'], alpha),
                                         (int(exp['x']), int(exp['y'])), r, 4 - i)
            
            # 爆炸星芒
            if progress < 0.5:
                for i in range(6):
                    angle = i * 60 + progress * 120
                    length = 50 * scale * (1 - progress * 2)
                    rad = math.radians(angle)
                    ex = exp['x'] + math.cos(rad) * length
                    ey = exp['y'] + math.sin(rad) * length
                    alpha = int(255 * (1 - progress * 2))
                    pygame.draw.line(self.image, (255, 255, 255, alpha),
                                   (int(exp['x']), int(exp['y'])), (int(ex), int(ey)), 3)
        
        # 绘制粒子（性能优化：使用列表推导）
        new_particles = []
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= 0.94
            p['vy'] *= 0.94
            p['life'] -= 1
            if p['life'] > 0:
                progress = p['life'] / p['max_life']
                alpha = int(255 * progress)
                size = max(1, int(p['size'] * progress))
                
                # 粒子光晕
                if size > 2:
                    pygame.draw.circle(self.image, (*p['color'][:3], alpha // 3),
                                     (int(p['x']), int(p['y'])), size + 3)
                pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                 (int(p['x']), int(p['y'])), size)
                new_particles.append(p)
        self.particles = new_particles


# ==================== 技能1：泰拉光束 ====================
class TerraBeamSkill(pygame.sprite.Sprite):
    """
    泰拉光束 - F技能
    召唤绿色泰拉刃幻影，发射全屏绿色剑气波
    学习克苏鲁风格：多层光晕、粒子系统、动态变形
    """
    
    def __init__(self, owner, damage, style="zenith_default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        self.theme = get_zenith_theme(style)
        
        self.frame = 0
        self.duration = 120
        self.phase = 0  # 0=蓄力, 1=发射, 2=爆发, 3=结束
        
        # 泰拉刃幻影
        self.blades = []
        for i in range(8):
            self.blades.append({
                'angle': i * 45,
                'dist': 150,
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(8, 15),
                'scale': 1.0,
            })
        
        # 粒子系统
        self.particles = []
        
        # 剑气波参数
        self.wave_lines = []
        
        self.size = (WIDTH, HEIGHT)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size
        })
    
    def update(self):
        self.frame += 1
        
        if self.frame < 40:
            self.phase = 0
        elif self.frame < 50:
            self.phase = 1
            if self.frame == 40:
                self._fire_beam()
        elif self.frame < 90:
            self.phase = 2
        else:
            self.phase = 3
        
        if self.frame > self.duration:
            self.kill()
            return
        
        self._render()
    
    def _fire_beam(self):
        """发射剑气波 - 生成多条剑气"""
        cx = self.owner.rect.centerx if self.owner else WIDTH // 2
        cy = self.owner.rect.centery if self.owner else HEIGHT // 2
        
        # 生成多条剑气波
        for i in range(5):
            self.wave_lines.append({
                'y': cy - 100,
                'speed': 15 + i * 2,
                'delay': i * 3,
                'width': 30 - i * 4,
                'alpha': 255,
            })
        
        # 对所有敌人造成伤害
        for mob in mobs:
            if hasattr(mob, 'take_damage'):
                mob.take_damage(self.damage * 2)
            # 命中粒子
            for _ in range(15):
                self._add_particle(mob.rect.centerx, mob.rect.centery,
                                 random.uniform(-8, 8), random.uniform(-12, 4),
                                 (0, 255, 100), random.randint(20, 40), random.randint(3, 8))
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx = self.owner.rect.centerx if self.owner else WIDTH // 2
        cy = self.owner.rect.centery if self.owner else HEIGHT // 2
        
        # 泰拉绿配色
        terra_green = (0, 255, 100)
        terra_dark = (0, 180, 70)
        terra_light = (150, 255, 200)
        terra_glow = (100, 255, 180)
        
        # ========== 阶段0：蓄力 - 泰拉刃聚集 ==========
        if self.phase == 0:
            progress = self.frame / 40
            
            # 背景暗化
            dark_alpha = int(40 * progress)
            pygame.draw.rect(self.image, (0, 20, 10, dark_alpha), (0, 0, WIDTH, HEIGHT))
            
            # 中心能量漩涡
            for i in range(5):
                vortex_r = 80 - progress * 50 + i * 15
                vortex_alpha = int(100 - i * 15)
                pulse = abs(math.sin(self.frame * 0.2 + i * 0.5))
                pygame.draw.circle(self.image, (*terra_green, int(vortex_alpha * pulse)), 
                                 (cx, cy), int(vortex_r), 3)
            
            # 能量聚集线
            for i in range(16):
                angle = self.frame * 3 + i * 22.5
                start_r = 200 * (1 - progress * 0.8)
                end_r = 30
                sx = cx + math.cos(math.radians(angle)) * start_r
                sy = cy + math.sin(math.radians(angle)) * start_r
                ex = cx + math.cos(math.radians(angle)) * end_r
                ey = cy + math.sin(math.radians(angle)) * end_r
                alpha = int(150 * progress)
                pygame.draw.line(self.image, (*terra_glow, alpha), 
                               (int(sx), int(sy)), (int(ex), int(ey)), 2)
            
            # 泰拉刃幻影旋转聚集
            for blade in self.blades:
                blade['dist'] = 150 * (1 - progress * 0.8)
                blade['rotation'] += blade['rot_speed']
                blade['angle'] += 3
                
                bx = cx + math.cos(math.radians(blade['angle'])) * blade['dist']
                by = cy + math.sin(math.radians(blade['angle'])) * blade['dist']
                
                # 绘制泰拉刃
                self._draw_terra_blade(bx, by, blade['rotation'], 1.0 + progress * 0.3)
                
                # 刃周围粒子
                if self.frame % 3 == 0:
                    self._add_particle(bx, by, random.uniform(-3, 3), random.uniform(-3, 3),
                                     terra_green, 20, 4)
        
        # ========== 阶段1&2：发射 - 剑气波 ==========
        elif self.phase in [1, 2]:
            # 背景绿色闪光
            flash_alpha = int(60 * abs(math.sin(self.frame * 0.3)))
            pygame.draw.rect(self.image, (*terra_green, flash_alpha), (0, 0, WIDTH, HEIGHT))
            
            # 更新并绘制剑气波（性能优化）
            new_wave_lines = []
            for wave in self.wave_lines:
                if wave['delay'] > 0:
                    wave['delay'] -= 1
                    new_wave_lines.append(wave)
                    continue
                
                wave['y'] -= wave['speed']
                wave['alpha'] = max(0, wave['alpha'] - 3)
                
                if wave['y'] < -100 or wave['alpha'] <= 0:
                    continue  # 不添加到新列表，相当于移除
                
                # 绘制剑气波（多层）
                w = wave['width']
                for layer in range(5):
                    layer_y = wave['y'] + layer * 4
                    layer_w = w - layer * 4
                    layer_alpha = int(wave['alpha'] * (1 - layer * 0.15))
                    
                    if layer_w > 0 and layer_alpha > 0:
                        # 主体
                        pygame.draw.rect(self.image, (*terra_green, layer_alpha),
                                        (0, int(layer_y - layer_w // 2), WIDTH, layer_w))
                        
                        # 边缘光
                        if layer == 0:
                            pygame.draw.line(self.image, (*terra_light, layer_alpha),
                                           (0, int(layer_y - layer_w // 2)),
                                           (WIDTH, int(layer_y - layer_w // 2)), 3)
                
                # 剑气中的小剑影
                for i in range(5):
                    sx = random.randint(50, WIDTH - 50)
                    sy = wave['y'] + random.randint(-15, 15)
                    self._draw_mini_sword(sx, sy, random.uniform(0, 360), wave['alpha'])
                
                new_wave_lines.append(wave)
            self.wave_lines = new_wave_lines
            
            # 中心爆发光环
            if self.phase == 1:
                burst_r = (self.frame - 40) * 20
                burst_alpha = int(200 - (self.frame - 40) * 15)
                if burst_alpha > 0:
                    pygame.draw.circle(self.image, (*terra_glow, burst_alpha), 
                                     (cx, cy), burst_r, 4)
        
        # ========== 粒子更新（性能优化：使用列表推导过滤）==========
        new_particles = []
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.2  # 重力
            p['life'] -= 1
            if p['life'] > 0:
                alpha = int(255 * p['life'] / p['max_life'])
                size = int(p['size'] * p['life'] / p['max_life'])
                if size > 0:
                    pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                     (int(p['x']), int(p['y'])), size)
                new_particles.append(p)
        self.particles = new_particles
    
    def _draw_terra_blade(self, x, y, rotation, scale):
        """绘制泰拉刃"""
        rad = math.radians(rotation)
        length = 35 * scale
        width = 8 * scale
        
        cos_r = math.cos(rad)
        sin_r = math.sin(rad)
        perp_cos = math.cos(rad + math.pi / 2)
        perp_sin = math.sin(rad + math.pi / 2)
        
        # 剑身顶点
        tip = (x + cos_r * length, y + sin_r * length)
        base_l = (x + perp_cos * width, y + perp_sin * width)
        base_r = (x - perp_cos * width, y - perp_sin * width)
        hilt = (x - cos_r * 10, y - sin_r * 10)
        
        points = [tip, base_l, hilt, base_r]
        points = [(int(p[0]), int(p[1])) for p in points]
        
        # 外发光
        for g in range(3):
            glow_points = [(int(tip[0] + cos_r * g * 2), int(tip[1] + sin_r * g * 2)),
                          (int(base_l[0] + perp_cos * g), int(base_l[1] + perp_sin * g)),
                          (int(hilt[0] - cos_r * g), int(hilt[1] - sin_r * g)),
                          (int(base_r[0] - perp_cos * g), int(base_r[1] - perp_sin * g))]
            pygame.draw.polygon(self.image, (0, 255, 100, 60 - g * 15), glow_points)
        
        # 主体
        pygame.draw.polygon(self.image, (0, 255, 100), points)
        pygame.draw.polygon(self.image, (150, 255, 200), points, 2)
        
        # 高光
        pygame.draw.line(self.image, (200, 255, 230),
                        (int(x + perp_cos * 2), int(y + perp_sin * 2)),
                        (int(tip[0]), int(tip[1])), 2)
    
    def _draw_mini_sword(self, x, y, rotation, alpha):
        """绘制小剑影"""
        rad = math.radians(rotation)
        length = 15
        
        tip_x = x + math.cos(rad) * length
        tip_y = y + math.sin(rad) * length
        
        pygame.draw.line(self.image, (0, 255, 100, int(alpha * 0.8)),
                        (int(x), int(y)), (int(tip_x), int(tip_y)), 3)
        pygame.draw.circle(self.image, (200, 255, 230, int(alpha)),
                          (int(tip_x), int(tip_y)), 3)


# ==================== 技能2：喵星人轰炸 ====================
class MeowmereBombSkill(pygame.sprite.Sprite):
    """
    喵星人轰炸 - G技能
    召唤大量彩虹猫头疯狂反弹
    学习克苏鲁风格：华丽的彩虹拖尾、爆炸效果、粒子系统
    """
    
    def __init__(self, owner, damage, style="zenith_default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        
        self.frame = 0
        self.duration = 240
        self.cats = []
        self.particles = []
        self.explosions = []
        
        self.size = (WIDTH, HEIGHT)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        # 生成猫头 - 分批生成
        cx = owner.rect.centerx if owner else WIDTH // 2
        cy = owner.rect.centery if owner else HEIGHT // 2
        for i in range(16):
            angle = i * 22.5 + random.uniform(-10, 10)
            speed = random.uniform(10, 18)
            self.cats.append({
                'x': cx, 'y': cy,
                'vx': math.cos(math.radians(angle)) * speed,
                'vy': math.sin(math.radians(angle)) * speed,
                'color_offset': i * 22,
                'trail': [],
                'size': random.uniform(0.8, 1.2),
                'spawn_delay': i * 2,
                'spawned': False,
                'rotation': 0,
                'hit_count': 0,
            })
        
        all_sprites.add(self)
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size
        })
    
    def _add_explosion(self, x, y, color):
        self.explosions.append({
            'x': x, 'y': y, 'color': color, 'frame': 0, 'max_frame': 20
        })
    
    def update(self):
        self.frame += 1
        
        # 更新猫头
        for cat in self.cats:
            if cat['spawn_delay'] > 0:
                cat['spawn_delay'] -= 1
                continue
            
            if not cat['spawned']:
                cat['spawned'] = True
                # 生成特效
                color = _get_rainbow_color(self.frame, cat['color_offset'])
                for _ in range(8):
                    self._add_particle(cat['x'], cat['y'],
                                     random.uniform(-5, 5), random.uniform(-5, 5),
                                     color, 20, 5)
            
            cat['x'] += cat['vx']
            cat['y'] += cat['vy']
            cat['rotation'] += 5 if cat['vx'] > 0 else -5
            
            # 反弹 - 带特效
            bounced = False
            if cat['x'] < 30:
                cat['vx'] = abs(cat['vx']) * 1.02
                cat['x'] = 30
                bounced = True
            elif cat['x'] > WIDTH - 30:
                cat['vx'] = -abs(cat['vx']) * 1.02
                cat['x'] = WIDTH - 30
                bounced = True
            if cat['y'] < 30:
                cat['vy'] = abs(cat['vy']) * 1.02
                cat['y'] = 30
                bounced = True
            elif cat['y'] > HEIGHT - 30:
                cat['vy'] = -abs(cat['vy']) * 1.02
                cat['y'] = HEIGHT - 30
                bounced = True
            
            if bounced:
                color = _get_rainbow_color(self.frame, cat['color_offset'])
                self._add_explosion(cat['x'], cat['y'], color)
                for _ in range(6):
                    self._add_particle(cat['x'], cat['y'],
                                     random.uniform(-4, 4), random.uniform(-4, 4),
                                     color, 15, 4)
            
            # 限速
            speed = math.hypot(cat['vx'], cat['vy'])
            if speed > 25:
                cat['vx'] = cat['vx'] / speed * 25
                cat['vy'] = cat['vy'] / speed * 25
            
            # 彩虹拖尾
            cat['trail'].append({
                'x': cat['x'], 'y': cat['y'], 
                'alpha': 255, 
                'color': _get_rainbow_color(self.frame, cat['color_offset'])
            })
            if len(cat['trail']) > 30:
                cat['trail'].pop(0)
            for t in cat['trail']:
                t['alpha'] = max(0, t['alpha'] - 8)
            
            # 检测敌人
            for mob in mobs:
                dx = mob.rect.centerx - cat['x']
                dy = mob.rect.centery - cat['y']
                if math.hypot(dx, dy) < 35:
                    if hasattr(mob, 'take_damage'):
                        mob.take_damage(self.damage * 0.6)
                        cat['hit_count'] += 1
                        
                        # 命中爆炸
                        color = _get_rainbow_color(self.frame, cat['color_offset'])
                        self._add_explosion(mob.rect.centerx, mob.rect.centery, color)
                        for _ in range(10):
                            self._add_particle(mob.rect.centerx, mob.rect.centery,
                                             random.uniform(-6, 6), random.uniform(-6, 6),
                                             color, 25, 5)
        
        # 更新爆炸（性能优化）
        new_explosions = []
        for exp in self.explosions:
            exp['frame'] += 1
            if exp['frame'] < exp['max_frame']:
                new_explosions.append(exp)
        self.explosions = new_explosions
        
        if self.frame > self.duration:
            self.kill()
            return
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        
        # 背景彩虹波纹
        if self.frame < 30:
            wave_r = self.frame * 20
            wave_alpha = int(100 - self.frame * 3)
            if wave_alpha > 0:
                cx = self.owner.rect.centerx if self.owner else WIDTH // 2
                cy = self.owner.rect.centery if self.owner else HEIGHT // 2
                for i in range(7):
                    color = _get_rainbow_color(self.frame, i * 50)
                    r = wave_r + i * 10
                    pygame.draw.circle(self.image, (*color, wave_alpha - i * 10),
                                      (cx, cy), r, 3)
        
        # 绘制拖尾
        for cat in self.cats:
            if not cat['spawned']:
                continue
            
            # 彩虹渐变拖尾
            trail_len = len(cat['trail'])
            for i, t in enumerate(cat['trail']):
                if t['alpha'] > 0:
                    # 多层拖尾
                    progress = i / max(1, trail_len)
                    size = int((6 - progress * 4) * cat['size'])
                    
                    # 外层光晕
                    if size > 2:
                        pygame.draw.circle(self.image, (*t['color'], t['alpha'] // 3),
                                         (int(t['x']), int(t['y'])), size + 3)
                    
                    # 核心
                    pygame.draw.circle(self.image, (*t['color'], t['alpha']),
                                     (int(t['x']), int(t['y'])), max(1, size))
        
        # 绘制爆炸
        for exp in self.explosions:
            progress = exp['frame'] / exp['max_frame']
            r = int(20 + progress * 30)
            alpha = int(200 * (1 - progress))
            
            # 多层爆炸环
            for i in range(3):
                ring_r = r - i * 8
                ring_alpha = alpha - i * 40
                if ring_r > 0 and ring_alpha > 0:
                    pygame.draw.circle(self.image, (*exp['color'], ring_alpha),
                                     (int(exp['x']), int(exp['y'])), ring_r, 3)
            
            # 星形闪光
            if progress < 0.5:
                for i in range(6):
                    angle = i * 60 + progress * 180
                    length = r * 1.5 * (1 - progress * 2)
                    ex = exp['x'] + math.cos(math.radians(angle)) * length
                    ey = exp['y'] + math.sin(math.radians(angle)) * length
                    pygame.draw.line(self.image, (255, 255, 255, alpha),
                                   (int(exp['x']), int(exp['y'])), (int(ex), int(ey)), 2)
        
        # 绘制粒子（性能优化：使用列表推导）
        new_particles = []
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= 0.95
            p['vy'] *= 0.95
            p['life'] -= 1
            if p['life'] > 0:
                alpha = int(255 * p['life'] / p['max_life'])
                size = max(1, int(p['size'] * p['life'] / p['max_life']))
                pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                 (int(p['x']), int(p['y'])), size)
                new_particles.append(p)
        self.particles = new_particles
        
        # 绘制猫头
        for cat in self.cats:
            if not cat['spawned']:
                continue
            
            cx, cy = int(cat['x']), int(cat['y'])
            color = _get_rainbow_color(self.frame, cat['color_offset'])
            scale = cat['size']
            
            # 猫头光晕
            for i in range(3):
                glow_r = int((14 + i * 4) * scale)
                glow_alpha = 80 - i * 20
                pygame.draw.circle(self.image, (*color, glow_alpha), (cx, cy), glow_r)
            
            # 头部
            head_r = int(12 * scale)
            pygame.draw.circle(self.image, color, (cx, cy), head_r)
            pygame.draw.circle(self.image, (255, 255, 255, 150), (cx, cy), head_r, 2)
            
            # 耳朵
            ear_points_l = [(cx - int(9 * scale), cy - int(5 * scale)),
                           (cx - int(5 * scale), cy - int(16 * scale)),
                           (cx - int(2 * scale), cy - int(5 * scale))]
            ear_points_r = [(cx + int(9 * scale), cy - int(5 * scale)),
                           (cx + int(5 * scale), cy - int(16 * scale)),
                           (cx + int(2 * scale), cy - int(5 * scale))]
            pygame.draw.polygon(self.image, color, ear_points_l)
            pygame.draw.polygon(self.image, color, ear_points_r)
            pygame.draw.polygon(self.image, (255, 200, 220), ear_points_l, 1)
            pygame.draw.polygon(self.image, (255, 200, 220), ear_points_r, 1)
            
            # 眼睛 - 动态
            eye_offset = int(2 * math.sin(self.frame * 0.2 + cat['color_offset']))
            pygame.draw.circle(self.image, (255, 255, 255), 
                             (cx - int(4 * scale) + eye_offset, cy - int(2 * scale)), int(4 * scale))
            pygame.draw.circle(self.image, (255, 255, 255),
                             (cx + int(4 * scale) + eye_offset, cy - int(2 * scale)), int(4 * scale))
            pygame.draw.circle(self.image, (0, 0, 0),
                             (cx - int(4 * scale) + eye_offset, cy - int(2 * scale)), int(2 * scale))
            pygame.draw.circle(self.image, (0, 0, 0),
                             (cx + int(4 * scale) + eye_offset, cy - int(2 * scale)), int(2 * scale))
            # 高光
            pygame.draw.circle(self.image, (255, 255, 255),
                             (cx - int(5 * scale) + eye_offset, cy - int(3 * scale)), 1)
            pygame.draw.circle(self.image, (255, 255, 255),
                             (cx + int(3 * scale) + eye_offset, cy - int(3 * scale)), 1)
            
            # 嘴
            pygame.draw.arc(self.image, (255, 200, 200),
                          (cx - int(3 * scale), cy + int(1 * scale), int(6 * scale), int(4 * scale)),
                          0, math.pi, 1)
            
            # 胡须
            for side in [-1, 1]:
                for i in range(3):
                    wx = cx + side * int(8 * scale)
                    wy = cy + int((i - 1) * 3 * scale)
                    wex = cx + side * int(18 * scale)
                    wey = wy + int((i - 1) * 2 * scale)
                    pygame.draw.line(self.image, (255, 255, 255, 150),
                                   (wx, wy), (wex, wey), 1)


# ==================== 技能3：天顶霸主 ====================
class ZenithOverdriveSkill(pygame.sprite.Sprite):
    """
    天顶霸主 - 终极奥义
    化作分形圆环，所有剑鬼畜速度全屏乱舞，背景像素崩坏
    学习克苏鲁风格：多层视觉、粒子爆发、拖尾幻影、能量漩涡
    """
    
    def __init__(self, owner, damage, style="zenith_default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        self.theme = get_zenith_theme(style)
        
        self.frame = 0
        self.duration = 300  # 5秒
        self.swords = []
        self.particles = []
        self.explosions = []
        self.slash_trails = []
        self.energy_waves = []
        
        self.size = (WIDTH, HEIGHT)
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        # 生成所有剑 - 增强版
        for i, sword in enumerate(LEGENDARY_SWORDS):
            self.swords.append({
                'data': sword,
                'x': random.uniform(100, WIDTH - 100),
                'y': random.uniform(100, HEIGHT - 100),
                'angle': random.uniform(0, 360),
                'speed': random.uniform(15, 30),
                'target': None,
                'phase': 0,
                'trail': [],
                'spin': random.uniform(15, 25),
                'glow_pulse': random.uniform(0, math.pi * 2),
                'hit_flash': 0,
            })
        
        # 像素碎片 - 更多层次
        self.pixels = []
        for i in range(80):
            self.pixels.append({
                'x': random.uniform(0, WIDTH),
                'y': random.uniform(0, HEIGHT),
                'size': random.randint(4, 16),
                'color_offset': random.randint(0, 360),
                'drift': random.uniform(-3, 3),
                'drift_x': random.uniform(-2, 2),
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-5, 5),
                'pulse': random.uniform(0, math.pi * 2),
            })
        
        # 分形能量线
        self.fractal_lines = []
        for i in range(24):
            self.fractal_lines.append({
                'angle': i * 15,
                'length': random.uniform(60, 120),
                'pulse': random.uniform(0, math.pi * 2),
                'color_offset': i * 15,
            })
        
        all_sprites.add(self)
    
    def _add_particle(self, x, y, vx, vy, color, life, size=4):
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size
        })
    
    def _add_explosion(self, x, y, color, scale=1.0):
        self.explosions.append({
            'x': x, 'y': y, 'color': color, 'frame': 0, 'max_frame': 25, 'scale': scale
        })
    
    def _add_slash_trail(self, x, y, angle, color, length):
        self.slash_trails.append({
            'x': x, 'y': y, 'angle': angle, 'color': color, 
            'length': length, 'life': 15, 'max_life': 15
        })
    
    def update(self):
        self.frame += 1
        
        # 阶段性能量波
        if self.frame % 60 == 0:
            cx = self.owner.rect.centerx if self.owner and self.owner.alive() else WIDTH // 2
            cy = self.owner.rect.centery if self.owner and self.owner.alive() else HEIGHT // 2
            self.energy_waves.append({
                'x': cx, 'y': cy, 'radius': 0, 'max_radius': 300,
                'color_offset': self.frame, 'alpha': 200
            })
        
        # 更新能量波（性能优化）
        new_waves = []
        for wave in self.energy_waves:
            wave['radius'] += 8
            wave['alpha'] = int(200 * (1 - wave['radius'] / wave['max_radius']))
            if wave['radius'] < wave['max_radius']:
                new_waves.append(wave)
        self.energy_waves = new_waves
        
        # 更新剑
        for sword in self.swords:
            # 寻找新目标
            if sword['target'] is None or not sword['target'].alive():
                alive_mobs = [m for m in mobs if m.alive()]
                if alive_mobs:
                    sword['target'] = random.choice(alive_mobs)
                else:
                    sword['target'] = None
            
            old_x, old_y = sword['x'], sword['y']
            
            # 移动
            if sword['target']:
                dx = sword['target'].rect.centerx - sword['x']
                dy = sword['target'].rect.centery - sword['y']
                dist = math.hypot(dx, dy)
                if dist > 0:
                    sword['x'] += (dx / dist) * sword['speed']
                    sword['y'] += (dy / dist) * sword['speed']
                    sword['angle'] = math.degrees(math.atan2(dy, dx))
                
                # 命中
                if dist < 40:
                    if hasattr(sword['target'], 'take_damage'):
                        sword['target'].take_damage(self.damage * 0.3)
                        sword['hit_flash'] = 10
                        
                        # 命中爆炸特效
                        color = sword['data']['color']
                        self._add_explosion(sword['target'].rect.centerx, 
                                          sword['target'].rect.centery, color, 1.5)
                        
                        # 爆炸粒子
                        for _ in range(12):
                            angle = random.uniform(0, 360)
                            speed = random.uniform(4, 10)
                            self._add_particle(sword['target'].rect.centerx,
                                             sword['target'].rect.centery,
                                             math.cos(math.radians(angle)) * speed,
                                             math.sin(math.radians(angle)) * speed,
                                             color, 25, 6)
                        
                        # 斩击拖尾
                        self._add_slash_trail(sword['target'].rect.centerx,
                                            sword['target'].rect.centery,
                                            sword['angle'], color, 60)
                    
                    sword['target'] = None
            else:
                # 随机漫游
                sword['angle'] += random.uniform(-30, 30)
                sword['x'] += math.cos(math.radians(sword['angle'])) * sword['speed'] * 0.5
                sword['y'] += math.sin(math.radians(sword['angle'])) * sword['speed'] * 0.5
            
            # 边界反弹
            if sword['x'] < 50 or sword['x'] > WIDTH - 50:
                sword['angle'] = 180 - sword['angle']
            if sword['y'] < 50 or sword['y'] > HEIGHT - 50:
                sword['angle'] = -sword['angle']
            
            sword['x'] = max(50, min(WIDTH - 50, sword['x']))
            sword['y'] = max(50, min(HEIGHT - 50, sword['y']))
            
            # 更新拖尾
            sword['trail'].append({
                'x': sword['x'], 'y': sword['y'],
                'angle': sword['angle'] + self.frame * sword['spin'],
                'alpha': 255
            })
            if len(sword['trail']) > 12:
                sword['trail'].pop(0)
            for t in sword['trail']:
                t['alpha'] = max(0, t['alpha'] - 20)
            
            # 更新命中闪烁
            if sword['hit_flash'] > 0:
                sword['hit_flash'] -= 1
            
            # 移动时产生粒子
            if self.frame % 3 == 0:
                color = sword['data']['color']
                self._add_particle(sword['x'], sword['y'],
                                 random.uniform(-2, 2), random.uniform(-2, 2),
                                 color, 15, 3)
        
        # 更新像素碎片
        for pixel in self.pixels:
            pixel['y'] += pixel['drift']
            pixel['x'] += pixel['drift_x'] + math.sin(self.frame * 0.05 + pixel['pulse']) * 2
            pixel['rotation'] += pixel['rot_speed']
            pixel['pulse'] += 0.1
            if pixel['y'] < -20:
                pixel['y'] = HEIGHT + 20
            elif pixel['y'] > HEIGHT + 20:
                pixel['y'] = -20
            if pixel['x'] < -20:
                pixel['x'] = WIDTH + 20
            elif pixel['x'] > WIDTH + 20:
                pixel['x'] = -20
        
        # 更新斩击拖尾（性能优化）
        new_trails = []
        for trail in self.slash_trails:
            trail['life'] -= 1
            if trail['life'] > 0:
                new_trails.append(trail)
        self.slash_trails = new_trails
        
        # 更新爆炸（性能优化）
        new_explosions = []
        for exp in self.explosions:
            exp['frame'] += 1
            if exp['frame'] < exp['max_frame']:
                new_explosions.append(exp)
        self.explosions = new_explosions
        
        if self.frame > self.duration:
            self.kill()
            return
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        
        # 背景像素崩坏效果（性能优化：直接绘制旋转多边形，避免临时Surface）
        for pixel in self.pixels:
            color = _get_rainbow_color(self.frame, pixel['color_offset'])
            pulse = math.sin(pixel['pulse']) * 0.3 + 0.7
            alpha = int((80 + 60 * math.sin(self.frame * 0.1 + pixel['color_offset'])) * pulse)
            
            size = int(pixel['size'] * pulse)
            if size > 0:
                # 直接计算旋转矩形的四个顶点
                cx, cy = pixel['x'], pixel['y']
                rad = math.radians(pixel['rotation'])
                cos_r, sin_r = math.cos(rad), math.sin(rad)
                half = size / 2
                
                # 四个角点的偏移
                corners = [(-half, -half), (half, -half), (half, half), (-half, half)]
                points = []
                for dx, dy in corners:
                    rx = dx * cos_r - dy * sin_r
                    ry = dx * sin_r + dy * cos_r
                    points.append((int(cx + rx), int(cy + ry)))
                
                # 绘制像素核心
                pygame.draw.polygon(self.image, (*color, alpha), points)
                
                # 绘制光晕边框
                pygame.draw.polygon(self.image, (*color, alpha // 3), points, 1)
        
        # 能量波
        for wave in self.energy_waves:
            if wave['alpha'] > 0:
                for i in range(3):
                    r = wave['radius'] - i * 10
                    if r > 0:
                        color = _get_rainbow_color(self.frame, wave['color_offset'] + i * 30)
                        alpha = max(0, wave['alpha'] - i * 40)
                        pygame.draw.circle(self.image, (*color, alpha),
                                         (int(wave['x']), int(wave['y'])), int(r), 4 - i)
        
        # 分形圆环 - 超级增强版
        if self.owner and self.owner.alive():
            cx, cy = self.owner.rect.centerx, self.owner.rect.centery
            
            # 多层脉动圆环
            for ring_i in range(5):
                ring_r = 60 + ring_i * 25 + 15 * math.sin(self.frame * 0.1 + ring_i * 0.5)
                color = _get_rainbow_color(self.frame, ring_i * 50)
                alpha = 80 - ring_i * 12
                
                # 圆环本体
                pygame.draw.circle(self.image, (*color, alpha), (cx, cy), int(ring_r), 3)
                
                # 圆环上的能量点
                for j in range(12):
                    dot_angle = j * 30 + self.frame * (3 - ring_i * 0.5)
                    dot_rad = math.radians(dot_angle)
                    dot_x = cx + math.cos(dot_rad) * ring_r
                    dot_y = cy + math.sin(dot_rad) * ring_r
                    dot_size = 3 + int(2 * math.sin(self.frame * 0.2 + j))
                    pygame.draw.circle(self.image, (*color, alpha + 50),
                                     (int(dot_x), int(dot_y)), dot_size)
            
            # 分形能量线
            for line in self.fractal_lines:
                line_angle = line['angle'] + self.frame * 2
                line_length = line['length'] + 20 * math.sin(self.frame * 0.15 + line['pulse'])
                line_rad = math.radians(line_angle)
                
                end_x = cx + math.cos(line_rad) * line_length
                end_y = cy + math.sin(line_rad) * line_length
                
                color = _get_rainbow_color(self.frame, line['color_offset'])
                
                # 多层线条
                for i in range(3):
                    alpha = 150 - i * 40
                    width = 4 - i
                    pygame.draw.line(self.image, (*color, alpha),
                                   (cx, cy), (int(end_x), int(end_y)), width)
                
                # 线条末端光球
                pygame.draw.circle(self.image, (*color, 200), (int(end_x), int(end_y)), 5)
                pygame.draw.circle(self.image, (255, 255, 255, 150), (int(end_x), int(end_y)), 3)
        
        # 斩击拖尾
        for trail in self.slash_trails:
            progress = trail['life'] / trail['max_life']
            alpha = int(200 * progress)
            length = trail['length'] * progress
            rad = math.radians(trail['angle'])
            
            end_x = trail['x'] + math.cos(rad) * length
            end_y = trail['y'] + math.sin(rad) * length
            start_x = trail['x'] - math.cos(rad) * length * 0.5
            start_y = trail['y'] - math.sin(rad) * length * 0.5
            
            # 多层斩击线
            for i in range(4):
                c = trail['color']
                a = max(0, alpha - i * 40)
                w = 8 - i * 2
                pygame.draw.line(self.image, (*c, a),
                               (int(start_x), int(start_y)), (int(end_x), int(end_y)), w)
        
        # 绘制爆炸
        for exp in self.explosions:
            progress = exp['frame'] / exp['max_frame']
            scale = exp['scale']
            
            # 多层爆炸环
            for i in range(4):
                r = int((25 + progress * 40 - i * 8) * scale)
                if r > 0:
                    alpha = int(200 * (1 - progress) - i * 30)
                    if alpha > 0:
                        pygame.draw.circle(self.image, (*exp['color'], alpha),
                                         (int(exp['x']), int(exp['y'])), r, 4 - i)
            
            # 星形爆发
            if progress < 0.6:
                for i in range(8):
                    angle = i * 45 + progress * 90
                    length = 40 * scale * (1 - progress * 1.5)
                    if length > 0:
                        rad = math.radians(angle)
                        ex = exp['x'] + math.cos(rad) * length
                        ey = exp['y'] + math.sin(rad) * length
                        alpha = int(255 * (1 - progress * 1.5))
                        pygame.draw.line(self.image, (255, 255, 255, alpha),
                                       (int(exp['x']), int(exp['y'])), (int(ex), int(ey)), 3)
        
        # 绘制粒子（性能优化：使用列表推导）
        new_particles = []
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= 0.92
            p['vy'] *= 0.92
            p['life'] -= 1
            if p['life'] > 0:
                progress = p['life'] / p['max_life']
                alpha = int(255 * progress)
                size = max(1, int(p['size'] * progress))
                
                # 粒子光晕
                if size > 2:
                    pygame.draw.circle(self.image, (*p['color'][:3], alpha // 3),
                                     (int(p['x']), int(p['y'])), size + 2)
                pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                 (int(p['x']), int(p['y'])), size)
                new_particles.append(p)
        self.particles = new_particles
        
        # 绘制所有剑 - 超级增强版
        for sword in self.swords:
            sx, sy = int(sword['x']), int(sword['y'])
            angle = sword['angle'] + self.frame * sword['spin']
            
            # 绘制拖尾
            for i, t in enumerate(sword['trail']):
                if t['alpha'] > 0:
                    trail_progress = i / max(1, len(sword['trail']))
                    self._draw_sword_ghost(t['x'], t['y'], t['angle'],
                                          sword['data'], t['alpha'] * 0.6, 
                                          0.5 + trail_progress * 0.3)
            
            # 命中时的闪烁效果
            glow_intensity = 1.0
            if sword['hit_flash'] > 0:
                glow_intensity = 1.5 + math.sin(sword['hit_flash'] * 0.5) * 0.5
            
            # 绘制主剑
            self._draw_legendary_sword(sx, sy, angle, sword['data'], glow_intensity)
    
    def _draw_sword_ghost(self, x, y, angle, sword_data, alpha, scale):
        """绘制剑的幻影"""
        rad = math.radians(angle)
        length = sword_data['length'] * scale
        color = sword_data['color']
        
        tip_x = x + math.cos(rad) * length
        tip_y = y + math.sin(rad) * length
        
        a = int(alpha)
        pygame.draw.line(self.image, (*color, a), (int(x), int(y)), (int(tip_x), int(tip_y)), 3)
    
    def _draw_legendary_sword(self, x, y, angle, sword_data, glow_intensity=1.0):
        """绘制华丽的传奇之剑"""
        rad = math.radians(angle)
        length = sword_data['length']
        color = sword_data['color']
        
        tip_x = x + math.cos(rad) * length
        tip_y = y + math.sin(rad) * length
        
        # 多层光晕
        for i in range(5):
            glow_alpha = int((120 - i * 20) * glow_intensity)
            glow_width = 12 - i * 2
            if glow_alpha > 0 and glow_width > 0:
                pygame.draw.line(self.image, (*color, glow_alpha),
                               (x, y), (int(tip_x), int(tip_y)), glow_width)
        
        # 剑身核心
        pygame.draw.line(self.image, color, (x, y), (int(tip_x), int(tip_y)), 4)
        
        # 剑身高光
        mid_x = x + math.cos(rad) * length * 0.5
        mid_y = y + math.sin(rad) * length * 0.5
        pygame.draw.line(self.image, (255, 255, 255, 180),
                       (int(mid_x - math.cos(rad) * length * 0.3), int(mid_y - math.sin(rad) * length * 0.3)),
                       (int(mid_x + math.cos(rad) * length * 0.2), int(mid_y + math.sin(rad) * length * 0.2)), 2)
        
        # 剑尖光芒
        pygame.draw.circle(self.image, (255, 255, 255), (int(tip_x), int(tip_y)), 5)
        pygame.draw.circle(self.image, color, (int(tip_x), int(tip_y)), 3)
        
        # 剑柄宝石
        gem_x = x - math.cos(rad) * 5
        gem_y = y - math.sin(rad) * 5
        pygame.draw.circle(self.image, (255, 255, 255, 200), (int(gem_x), int(gem_y)), 4)
        pygame.draw.circle(self.image, color, (int(gem_x), int(gem_y)), 3)





# ==================== 子弹预览渲染 ====================
def render_zenith_bullet_preview(surface, x, y, style="zenith_default"):
    """渲染天顶子弹预览"""
    theme = get_zenith_theme(style)
    cx, cy = x + 20, y + 20
    frame = pygame.time.get_ticks() // 16
    
    # 绘制回旋剑
    angle = frame * 10
    rad = math.radians(angle)
    length = 15
    
    color = _get_rainbow_color(frame, 0)
    tip_x = cx + math.cos(rad) * length
    tip_y = cy + math.sin(rad) * length
    
    pygame.draw.line(surface, color, (cx, cy), (int(tip_x), int(tip_y)), 3)
    pygame.draw.circle(surface, (255, 255, 255), (int(tip_x), int(tip_y)), 2)
