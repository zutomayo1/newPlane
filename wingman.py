#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
僚机系统 (Wingman System)
- 僚机是玩家的辅助单位
- 每个僚机配备一把副武器
- 僚机自动跟随玩家并使用副武器攻击
- 最多4个僚机，围绕玩家旋转
"""

import pygame
import math
from config import WIDTH, HEIGHT, CYAN, MAGENTA, WHITE, GRAY, YELLOW
from utils import draw_text

class Wingman:
    """僚机类"""
    
    def __init__(self, player, slot_index=0, weapon_system=None, paint_theme_id="default"):
        """
        初始化僚机
        :param player: 归属的玩家对象
        :param slot_index: 在编队中的位置索引 (0=上, 1=右, 2=下, 3=左)
        :param weapon_system: 副武器系统
        :param paint_theme_id: 涂装主题ID
        """
        self.player = player
        self.slot_index = slot_index
        self.weapon = weapon_system
        self.paint_theme_id = paint_theme_id
        self.last_player_slot = player.current_slot if player else 0  # 追踪玩家的武器槽位变化
        
        # 位置
        self.x = player.rect.centerx
        self.y = player.rect.centery
        self.rect = pygame.Rect(self.x - 15, self.y - 15, 30, 30)
        
        # 编队配置 - 4个方向（上、右、下、左）
        # 初始角度 - 每个槽位相隔90度
        # slot_index: 0=上, 1=右, 2=下, 3=左
        self.initial_angle = slot_index * math.pi / 2.0  # 0, π/2, π, 3π/2
        
        # 轨道参数
        self.orbit_radius = 100  # 轨道半径
        self.rotation_speed = 0.04  # 旋转速度 (弧度/毫秒，转换为帧数时更加可控)
        self.last_update_time = pygame.time.get_ticks()
        self.accumulated_rotation = 0  # 累积旋转角度
        
        # 状态
        self.health = 100
        self.max_health = 100
        self.active = True
        
    def update(self, mobs, homing_level=0, global_time=0):
        """更新僚机状态
        
        :param mobs: 敌人列表
        :param homing_level: 玩家的追踪等级
        :param global_time: 全局时间（用于旋转计算，可选）
        """
        if not self.active or not self.player:
            return
        
        # 检查玩家是否切换了武器，如果切换则同步更新僚机的武器
        if hasattr(self.player, 'current_slot') and self.last_player_slot != self.player.current_slot:
            self.last_player_slot = self.player.current_slot
            self._sync_weapon_with_player()
        
        # 计算时间增量用于平滑旋转
        current_time = pygame.time.get_ticks()
        time_delta = (current_time - self.last_update_time) / 1000.0  # 转换为秒
        self.last_update_time = current_time
        
        # 累积旋转角度 - 每帧增加一定的旋转量
        # 旋转速度：约1.5弧度/秒 ≈ 86°/秒
        self.accumulated_rotation -= time_delta * 1.5  # 负值实现顺时针
        
        # 计算该僚机的当前角度 = 初始角度 + 累积旋转角度
        current_angle_rad = self.initial_angle + self.accumulated_rotation
        
        # 计算轨道上的目标位置（相对于玩家）
        offset_x = self.orbit_radius * math.cos(current_angle_rad)
        offset_y = self.orbit_radius * math.sin(current_angle_rad)
        
        # 目标位置 = 玩家位置 + 轨道偏移
        target_x = self.player.rect.centerx + offset_x
        target_y = self.player.rect.centery + offset_y
        
        # 平滑跟随
        self.x += (target_x - self.x) * 0.15
        self.y += (target_y - self.y) * 0.15
        
        self.rect.center = (self.x, self.y)
        
        # 更新武器系统（恢复能量、热量等）
        if self.weapon:
            self.weapon.update()
        
        # 使用副武器攻击
        if self.weapon:
            self._shoot_weapon(mobs, homing_level)
    
    def _sync_weapon_with_player(self):
        """当玩家切换武器时，同步更新僚机的武器"""
        if not self.player or not hasattr(self.player, 'weapon_slots'):
            return
        
        try:
            # 获取玩家当前选中的武器
            current_weapon = self.player.weapon_slots[self.player.current_slot]
            
            if current_weapon:
                # 深拷贝玩家的武器配置
                import copy
                self.weapon = copy.deepcopy(current_weapon)
                # 降低冷却时间为一半
                if hasattr(self.weapon, 'cooldown_max'):
                    self.weapon.cooldown_max = max(1, self.weapon.cooldown_max // 2)
        except (IndexError, AttributeError) as e:
            print(f"僚机同步武器失败: {e}")
    
    def _shoot_weapon(self, mobs, homing_level):
        """使用副武器攻击"""
        if not self.weapon:
            return
        
        if not self.weapon.can_shoot():
            return
        
        try:
            # 调用副武器的射击逻辑（更新冷却）
            self.weapon.shoot(self.rect, mobs, homing_level)
            
            # 生成子弹 - 从僚机位置向最近的敌人射击
            if mobs:
                # 找最近的敌人
                nearest_mob = None
                nearest_dist = float('inf')
                
                for mob in mobs:
                    dx = mob.rect.centerx - self.rect.centerx
                    dy = mob.rect.centery - self.rect.centery
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_mob = mob
                
                if nearest_mob and nearest_dist < 500:
                    # 射向敌人
                    self._create_wingman_bullet(nearest_mob)
                else:
                    # 默认向下射击
                    self._create_wingman_bullet(None)
            else:
                # 默认向下射击
                self._create_wingman_bullet(None)
                
        except Exception as e:
            print(f"Wingman weapon shoot error: {e}")
    
    def _create_wingman_bullet(self, target):
        """从僚机创建子弹
        
        :param target: 目标敌人（如果为None则默认向下）
        """
        # 迟延导入以避免循环引用
        from sprites import Bullet
        
        if target:
            # 计算射向敌人的方向
            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            angle_rad = math.atan2(dy, dx)
        else:
            # 默认向下射击
            angle_rad = math.pi / 2
        
        # 转换为度数（Bullet类期望的是度数）
        angle_deg = math.degrees(angle_rad)
        
        # 从武器系统获取子弹类型和颜色
        if self.weapon:
            weapon_type = self.weapon.type
            
            # 将武器类型映射到子弹建模类型和颜色
            weapon_to_bullet = {
                'cannon': ('beam', (255, 150, 0)),          # 炮→光束，橙色
                'beam': ('beam', (100, 200, 255)),          # 光束→光束，青色
                'missile': ('rocket', (255, 100, 0)),       # 导弹→火箭，红橙色
                'explosive': ('flame', (255, 140, 0)),      # 爆炸→烈焰，橙色
                'blade': ('blade', (255, 0, 100)),          # 刀刃→光刃，品红色
                'arc': ('lightning', (150, 150, 255)),      # 电弧→闪电，淡蓝色
                'scatter': ('quant', (200, 100, 200)),      # 散射→量子，紫色
                'void': ('shadow', (100, 50, 150)),         # 虚空→暗影，深紫色
                'frost': ('prism', (100, 200, 255)),        # 冰冻→棱镜，冰蓝色
                'rocket': ('rocket', (255, 100, 0)),        # 火箭→火箭，火红色
                'pulse': ('beam', (0, 200, 200)),           # 脉冲→光束，深青色
                'vortex': ('spectral', (200, 0, 255)),      # 漩涡→谱能，品红色
                'gravity': ('shadow', (150, 50, 200)),      # 重力→暗影，深紫色
                'wave': ('wave', (100, 255, 200)),          # 海啸→波纹，海蓝色
                'inferno': ('flame', (255, 100, 0)),        # 地狱→烈焰，火红色
                'split': ('star', (255, 200, 0)),           # 分裂→星镖，黄色
            }
            
            if weapon_type in weapon_to_bullet:
                b_type, color = weapon_to_bullet[weapon_type]
            else:
                b_type = 'beam'
                color = (200, 200, 200)
        else:
            b_type = 'beam'
            color = (100, 200, 255)
        
        # 创建子弹 - Bullet类会自动添加到all_sprites和bullets组
        Bullet(int(self.x), int(self.y), angle=angle_deg, is_enemy=False, piercing=0, color=color, b_type=b_type)
    
    def draw(self, screen):
        """绘制僚机"""
        if not self.active:
            return
        
        # 【新功能】支持僚机涂装系统
        if hasattr(self, 'paint_theme_id') and self.paint_theme_id != "default":
            try:
                from wingman_themes import WINGMAN_DRAW_FUNCTIONS
                if self.paint_theme_id in WINGMAN_DRAW_FUNCTIONS:
                    draw_func = WINGMAN_DRAW_FUNCTIONS[self.paint_theme_id]
                    draw_func(screen, int(self.x), int(self.y))
                    return
            except (ImportError, KeyError):
                pass
        
        self._draw_wingman_plane(screen)
    
    def _draw_wingman_plane(self, screen):
        """绘制赛博朋克风格的僚机飞机
        
        设计：小型战斗机，基于玩家机体但更精悍
        """
        x, y = int(self.x), int(self.y)
        
        # 获取脉动效果
        t = pygame.time.get_ticks() / 1000.0
        pulse = abs(math.sin(t * 4))  # 更快的脉动
        
        # 机体颜色：紫/蓝渐变
        main_color = (150, 100, 200)  # 紫蓝色
        edge_color = (200, 150, 255)  # 亮紫色
        glow_color = (100, 200, 255)  # 青蓝色
        
        # === 背景光晕（透明） ===
        glow_radius = int(18 + 4 * pulse)
        # 使用Surface实现透明光晕
        glow_surf = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*glow_color, 8), (glow_radius + 2, glow_radius + 2), glow_radius)  # alpha=8 很透明
        screen.blit(glow_surf, (x - glow_radius - 2, y - glow_radius - 2))
        
        # === 主机体：菱形战斗机设计 ===
        # 机头（上）- 锐利的尖端
        nose_points = [
            (x, y - 14),      # 机头顶点
            (x + 3, y - 10),  # 右机头边
            (x - 3, y - 10)   # 左机头边
        ]
        pygame.draw.polygon(screen, edge_color, nose_points)
        
        # 机身主体（中央菱形）
        fuselage_points = [
            (x, y - 14),      # 上（机头）
            (x + 10, y),      # 右
            (x, y + 14),      # 下
            (x - 10, y)       # 左
        ]
        pygame.draw.polygon(screen, main_color, fuselage_points)
        pygame.draw.polygon(screen, edge_color, fuselage_points, 1)  # 边框
        
        # === 机翼 ===
        # 左翼
        left_wing = [
            (x - 10, y - 2),
            (x - 16, y - 4),
            (x - 16, y + 4),
            (x - 10, y + 2)
        ]
        pygame.draw.polygon(screen, main_color, left_wing)
        pygame.draw.line(screen, edge_color, (x - 10, y - 2), (x - 16, y - 4), 1)
        
        # 右翼
        right_wing = [
            (x + 10, y - 2),
            (x + 16, y - 4),
            (x + 16, y + 4),
            (x + 10, y + 2)
        ]
        pygame.draw.polygon(screen, main_color, right_wing)
        pygame.draw.line(screen, edge_color, (x + 10, y - 2), (x + 16, y - 4), 1)
        
        # === 副翼细节 ===
        # 上副翼
        pygame.draw.line(screen, glow_color, (x - 3, y - 8), (x + 3, y - 8), 1)
        
        # 下副翼
        pygame.draw.line(screen, glow_color, (x - 3, y + 8), (x + 3, y + 8), 1)
        
        # === 能量核心（驾驶舱） ===
        core_radius = int(3 + 1.5 * pulse)
        pygame.draw.circle(screen, (255, 200, 100), (x, y - 4), core_radius)  # 能量核心
        pygame.draw.circle(screen, (255, 255, 200), (x, y - 4), core_radius - 1)  # 内核
        
        # === 引擎尾焰 ===
        if self.weapon and self.weapon.is_firing:  # 正在射击时显示加强尾焰
            flame_brightness = int(100 + 155 * pulse)
            flame_points = [
                (x - 2, y + 14),
                (x - 4, y + 20 + int(3 * pulse)),
                (x, y + 18),
                (x + 4, y + 20 + int(3 * pulse)),
                (x + 2, y + 14)
            ]
            pygame.draw.polygon(screen, (flame_brightness, flame_brightness // 2, 0), flame_points)
            pygame.draw.polygon(screen, (255, 150, 0), flame_points, 1)
        else:
            # 待机时的微弱尾焰
            tail_points = [
                (x - 1, y + 14),
                (x - 2, y + 17),
                (x, y + 16),
                (x + 2, y + 17),
                (x + 1, y + 14)
            ]
            pygame.draw.polygon(screen, (100, 80, 20), tail_points)
        
        # === 武器指示灯 ===
        if self.weapon:
            # 武器类型显示在机翼上
            weapon_color = {
                'cannon': (255, 150, 0),      # 橙色
                'beam': (100, 200, 255),      # 青色
                'missile': (255, 100, 100),   # 红色
                'explosive': (255, 150, 50),  # 黄橙色
                'blade': (255, 0, 100),       # 品红色
                'arc': (150, 150, 255),       # 淡蓝色
                'scatter': (200, 100, 200),   # 紫色
                'void': (100, 50, 150),       # 深紫色
                'frost': (100, 200, 255),     # 冰蓝色
                'rocket': (255, 100, 0),      # 火红色
            }.get(self.weapon.type, (200, 200, 200))
            
            # 左右翼的武器指示灯
            pygame.draw.circle(screen, weapon_color, (x - 10, y - 2), 2)
            pygame.draw.circle(screen, weapon_color, (x + 10, y - 2), 2)
            
            # 武器充能条（在机身两侧）
            charge_ratio = min(1.0, 1.0 - self.weapon.reload_timer / max(1, self.weapon.cooldown_max))
            bar_length = 6
            bar_height = 1
            
            # 左侧充能条
            pygame.draw.rect(screen, (50, 50, 50), (x - 12, y - 6, bar_length, bar_height))
            pygame.draw.rect(screen, weapon_color, (x - 12, y - 6, int(bar_length * charge_ratio), bar_height))
            
            # 右侧充能条
            pygame.draw.rect(screen, (50, 50, 50), (x + 6, y - 6, bar_length, bar_height))
            pygame.draw.rect(screen, weapon_color, (x + 6, y - 6, int(bar_length * charge_ratio), bar_height))
        
        # === 护盾指示 ===
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            shield_color = (100 + int(155 * health_ratio), 150, 255)
            pygame.draw.circle(screen, shield_color, (x, y), 20, 1)
        
        # === 编队编号显示 ===
        # 在机身后方显示编队位置
        slot_names = ["↑", "→", "↓", "←"]
        slot_color = (150, 200, 255)
        # 绘制小指示符（在机体下方）
        pygame.draw.polygon(screen, slot_color, [
            (x - 4, y + 18),
            (x - 2, y + 20),
            (x + 2, y + 20),
            (x + 4, y + 18)
        ])
    
    def take_damage(self, amount):
        """受到伤害"""
        self.health -= amount
        if self.health <= 0:
            self.active = False
    
    def heal(self, amount):
        """恢复生命"""
        self.health = min(self.max_health, self.health + amount)
    
    def get_status(self):
        """获取僚机状态信息"""
        return {
            "slot": self.slot_index,
            "health": self.health,
            "weapon": self.weapon.name if self.weapon else "无",
            "active": self.active
        }


class WingmanSquadron:
    """僚机编队管理系统"""
    
    def __init__(self, player, max_wingmen=2):
        """
        初始化僚机编队
        :param player: 玩家对象
        :param max_wingmen: 最多僚机数量
        """
        self.player = player
        self.max_wingmen = max_wingmen
        self.wingmen = []  # 活跃的僚机列表
        
    def add_wingman(self, weapon_system):
        """添加僚机"""
        if len(self.wingmen) >= self.max_wingmen:
            return False
        
        slot_index = len(self.wingmen)
        wingman = Wingman(self.player, slot_index, weapon_system)
        self.wingmen.append(wingman)
        
        # 重新调整所有僚机的slot_index和初始角度，确保均匀分布
        # 这样即使分次添加僚机，它们也会自动排列成正方形
        self._rearrange_wingmen()
        
        return True
    
    def _rearrange_wingmen(self):
        """重新排列所有僚机以确保均匀分布"""
        for i, wingman in enumerate(self.wingmen):
            wingman.slot_index = i
            # 重新计算初始角度确保4个方向均匀分布
            wingman.initial_angle = i * math.pi / 2.0
            # 重置累积旋转，使得角度计算一致
            wingman.accumulated_rotation = 0
    
    def remove_wingman(self, index):
        """移除僚机"""
        if 0 <= index < len(self.wingmen):
            self.wingmen.pop(index)
    
    def update(self, mobs, global_time=0):
        """更新所有僚机
        
        :param mobs: 敌人列表
        :param global_time: 全局时间（用于轨道旋转）
        """
        for wingman in self.wingmen[:]:
            if wingman.active:
                wingman.update(mobs, self.player.homing_level, global_time)
            else:
                self.wingmen.remove(wingman)
    
    def draw(self, screen):
        """绘制所有僚机"""
        for wingman in self.wingmen:
            wingman.draw(screen)
    
    def get_squad_status(self):
        """获取整个编队的状态"""
        return {
            "count": len(self.wingmen),
            "max": self.max_wingmen,
            "wingmen": [w.get_status() for w in self.wingmen]
        }
