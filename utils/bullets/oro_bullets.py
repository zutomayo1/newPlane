# -*- coding: utf-8 -*-
"""
终噬星链·奥罗 - 专属子弹模块
千节链生长+黑狱激光栅+终噬黑洞三维轰炸

特性：
- 黑狱链段：1.6屏射程，命中后生成「星链节」
- 星链节：留场3s，每1s向外延伸1节，最多5节
- 激光栅：链节≥3时释放十字穿透激光
- 噬能debuff：远程易伤+10%，上限5层

大招：
- 千节连生：9道链段形成千节墙，同步爆炸
- 激光栅风暴：4s十字激光持续轰炸
- 终噬黑洞：超大范围黑洞持续5s
"""
import pygame
import math
import random
from config import all_sprites, mobs, WIDTH, HEIGHT, enemy_bullets, bullets

# ==================== 12款子弹皮肤配置 ====================
ORO_BULLET_THEMES = {
    # ================= [系列一：传说重现] =================
    "default": {
        # 宇宙吞噬者·原初 - 死亡激光
        "name": "死亡激光",
        "type": "beam",
        "color": (148, 0, 211),
        "glow": (0, 255, 255),
        "size": 4,
        # 兼容旧字段
        "core": (148, 0, 211),
        "chain": (100, 0, 180),
        "laser": (0, 255, 255),
        "pulse": (180, 100, 255),
        "void": (20, 0, 40),
        "star": (200, 80, 255),
    },
    "phantom": {
        # 星神游龙·幽灵 - 幽灵法球
        "name": "幽灵法球",
        "type": "orb",
        "color": (100, 149, 237),
        "glow": (255, 255, 255),
        "size": 6,
        "core": (100, 149, 237),
        "chain": (80, 120, 200),
        "laser": (200, 220, 255),
        "pulse": (255, 255, 255),
        "void": (30, 40, 70),
        "star": (180, 200, 255),
    },
    "golden": {
        # 弑神装甲·重装 - 弑神弹头
        "name": "弑神弹头",
        "type": "missile",
        "color": (255, 215, 0),
        "glow": (255, 69, 0),
        "size": 5,
        "core": (255, 215, 0),
        "chain": (200, 160, 0),
        "laser": (255, 120, 0),
        "pulse": (255, 200, 100),
        "void": (60, 50, 0),
        "star": (255, 230, 100),
    },

    # ================= [系列二：元素反转] =================
    "inferno": {
        # 狱炎长虫·熔岩 - 熔岩滴注
        "name": "熔岩滴注",
        "type": "blob",
        "color": (139, 0, 0),
        "glow": (255, 140, 0),
        "size": 7,
        "core": (139, 0, 0),
        "chain": (180, 50, 0),
        "laser": (255, 140, 0),
        "pulse": (255, 200, 50),
        "void": (60, 20, 0),
        "star": (255, 180, 80),
    },
    "frost": {
        # 极地灾厄·冰晶 - 冰晶碎片
        "name": "冰晶碎片",
        "type": "shard",
        "color": (200, 255, 255),
        "glow": (0, 191, 255),
        "size": 6,
        "core": (200, 255, 255),
        "chain": (150, 220, 255),
        "laser": (0, 191, 255),
        "pulse": (220, 255, 255),
        "void": (50, 80, 100),
        "star": (180, 240, 255),
    },
    "toxic": {
        # 生化危机·辐射 - 辐射毒云
        "name": "辐射毒云",
        "type": "cloud",
        "color": (50, 205, 50),
        "glow": (173, 255, 47),
        "size": 8,
        "core": (50, 205, 50),
        "chain": (40, 160, 40),
        "laser": (173, 255, 47),
        "pulse": (200, 255, 100),
        "void": (20, 60, 20),
        "star": (150, 255, 100),
    },

    # ================= [系列三：概念重构] =================
    "cosmic": {
        # 矩阵代码·黑客 - 二进制流
        "name": "二进制流",
        "type": "pixel",
        "color": (0, 255, 0),
        "glow": (20, 20, 20),
        "size": 4,
        "core": (0, 255, 0),
        "chain": (0, 200, 0),
        "laser": (50, 255, 50),
        "pulse": (100, 255, 100),
        "void": (0, 30, 0),
        "star": (80, 255, 80),
    },
    "royal": {
        # 水墨游龙·写意 - 泼墨
        "name": "泼墨",
        "type": "ink",
        "color": (0, 0, 0),
        "glow": (50, 50, 50),
        "size": 6,
        "core": (0, 0, 0),
        "chain": (30, 30, 30),
        "laser": (80, 80, 80),
        "pulse": (100, 100, 100),
        "void": (10, 10, 10),
        "star": (60, 60, 60),
    },
    "crimson": {
        # 折纸大蛇·维度 - 纸飞镖
        "name": "纸飞镖",
        "type": "triangle",
        "color": (255, 250, 205),
        "glow": (200, 0, 0),
        "size": 5,
        "core": (255, 250, 205),
        "chain": (240, 230, 180),
        "laser": (220, 20, 60),
        "pulse": (255, 100, 100),
        "void": (80, 70, 50),
        "star": (255, 200, 180),
    },

    # ================= [系列四：终极幻想] =================
    "void": {
        # 视界线·虚空 - 微型黑洞
        "name": "微型黑洞",
        "type": "void_hole",
        "color": (0, 0, 0),
        "glow": (138, 43, 226),
        "size": 6,
        "core": (0, 0, 0),
        "chain": (20, 10, 40),
        "laser": (138, 43, 226),
        "pulse": (180, 80, 255),
        "void": (5, 0, 15),
        "star": (160, 60, 240),
    },
    "abyss": {
        # 机械降神·齿轮 - 黄铜弩箭
        "name": "黄铜弩箭",
        "type": "bolt",
        "color": (184, 134, 11),
        "glow": (255, 255, 255),
        "size": 4,
        "core": (184, 134, 11),
        "chain": (150, 110, 10),
        "laser": (218, 165, 32),
        "pulse": (255, 220, 100),
        "void": (60, 40, 5),
        "star": (255, 200, 80),
    },
    "blood": {
        # 数据删除·终焉 - 删除指令
        "name": "删除指令",
        "type": "cross",
        "color": (255, 0, 0),
        "glow": (255, 255, 255),
        "size": 5,
        "core": (255, 0, 0),
        "chain": (200, 0, 0),
        "laser": (255, 100, 100),
        "pulse": (255, 200, 200),
        "void": (80, 0, 0),
        "star": (255, 150, 150),
    },
}


def get_theme(style):
    """获取主题配色"""
    return ORO_BULLET_THEMES.get(style, ORO_BULLET_THEMES["default"])


# ==================== 黑狱链段（主武器）====================
class VoidChainBullet(pygame.sprite.Sprite):
    """黑狱链段 - 主武器，1.6屏射程，命中生成星链节"""
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 1
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 20
        self.max_range = HEIGHT * 1.6  # 1.6屏射程
        self.traveled = 0
        
        self.frame = 0
        self.angle = -math.pi / 2
        
        # 链节粒子轨迹
        self.trail = []
        self.trail_max = 12
        
        # 创建图像
        self.size = 24
        self.image = pygame.Surface((self.size, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
    def update(self):
        self.frame += 1
        
        # 移动
        dx = math.cos(self.angle) * self.speed
        dy = math.sin(self.angle) * self.speed
        self.float_x += dx
        self.float_y += dy
        self.traveled += self.speed
        
        # 记录轨迹
        self.trail.append((self.float_x, self.float_y))
        if len(self.trail) > self.trail_max:
            self.trail.pop(0)
        
        # 超出范围销毁
        if self.traveled > self.max_range or self.float_y < -50:
            self.kill()
            return
        
        # 更新位置
        self.rect.centerx = int(self.float_x)
        self.rect.centery = int(self.float_y)
        
        # 绘制
        self._render()
        
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size
        t = self.frame * 0.1
        
        # 获取皮肤类型和颜色
        b_type = self.theme.get("type", "beam")
        col_main = self.theme.get("color", self.theme["core"])
        col_glow = self.theme.get("glow", self.theme["pulse"])
        size = self.theme.get("size", 5)
        
        # --- 根据类型绘制不同形状 ---
        
        # 1. 激光束 (Beam) - 长条形，带发光边缘
        if b_type == "beam":
            length = size * 5
            rect_glow = pygame.Rect(cx - 3, cy - length // 2, 6, length)
            rect_core = pygame.Rect(cx - 2, cy - length // 2, 4, length)
            pygame.draw.rect(self.image, col_glow, rect_glow)
            pygame.draw.rect(self.image, col_main, rect_core)
            # 头部发光
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy - length // 2), 3)
        
        # 2. 幽灵法球 (Orb) - 模糊圆形，带尾迹
        elif b_type == "orb":
            pygame.draw.circle(self.image, col_main, (cx, cy), size)
            pygame.draw.circle(self.image, (*col_glow, 100), (cx, cy), size + 3)
            pygame.draw.circle(self.image, (255, 255, 255), (cx - 2, cy - 2), 2)
            # 尾迹
            for i in range(3):
                pygame.draw.circle(self.image, (*col_main, 80 - i * 25), 
                                  (cx, cy + size + i * 4), size - i)
        
        # 3. 导弹 (Missile) - 尖头
        elif b_type == "missile":
            pts = [
                (cx, cy - size * 3),       # 弹头
                (cx + size, cy + size),    # 右翼
                (cx, cy),                  # 底部凹陷
                (cx - size, cy + size)     # 左翼
            ]
            pygame.draw.polygon(self.image, col_main, pts)
            pygame.draw.polygon(self.image, col_glow, pts, 2)
            # 尾焰
            pygame.draw.polygon(self.image, col_glow, 
                              [(cx - 3, cy + size), (cx, cy + size + 6), (cx + 3, cy + size)])
        
        # 4. 冰晶 (Shard) - 旋转的菱形
        elif b_type == "shard":
            rot_offset = math.sin(t * 0.8) * 3
            pts = [
                (cx, cy - size * 2 + rot_offset),
                (cx + size, cy),
                (cx, cy + size * 2 + rot_offset),
                (cx - size, cy)
            ]
            pygame.draw.polygon(self.image, col_main, pts)
            pygame.draw.polygon(self.image, col_glow, pts, 2)
            # 内核
            pygame.draw.circle(self.image, col_glow, (cx, cy), size // 2)
        
        # 5. 矩阵像素 (Pixel) - 方形，带拖尾
        elif b_type == "pixel":
            pygame.draw.rect(self.image, col_main, 
                           (cx - size, cy - size, size * 2, size * 2))
            # 拖尾像素
            for i in range(3):
                pygame.draw.rect(self.image, (*col_main, 100 - i * 30), 
                               (cx - size, cy + size + i * size, size * 2, size * 2))
        
        # 6. 水墨 (Ink) - 不规则圆 (使用帧数模拟随机)
        elif b_type == "ink":
            radius = size + int(math.sin(t * 2) * 1)
            pygame.draw.circle(self.image, col_main, (cx, cy), int(radius))
            # 溅墨 - 固定位置
            for i in range(2):
                angle = t * 0.5 + i * 2.5
                sx = cx + int(math.cos(angle) * 5)
                sy = cy + 8 + i * 4
                pygame.draw.circle(self.image, col_main, (sx, sy), 2 + i)
        
        # 7. 纸飞镖 (Triangle) - 纯色三角形
        elif b_type == "triangle":
            pts = [
                (cx, cy - size * 3),
                (cx + size, cy + size),
                (cx - size, cy + size)
            ]
            pygame.draw.polygon(self.image, col_main, pts)
            # 折痕
            pygame.draw.line(self.image, col_glow, (cx, cy - size * 3), (cx, cy + size), 2)
        
        # 8. 黑洞 (Void Hole) - 黑芯紫边
        elif b_type == "void_hole":
            # 外发光脉冲
            glow_size = size + int(abs(math.sin(t * 0.5)) * 3)
            pygame.draw.circle(self.image, col_glow, (cx, cy), glow_size + 2)
            pygame.draw.circle(self.image, col_main, (cx, cy), size)  # 纯黑核心
            # 扭曲线条
            for i in range(4):
                angle = t + i * math.pi / 2
                ex = cx + math.cos(angle) * (size + 4)
                ey = cy + math.sin(angle) * (size + 4)
                pygame.draw.line(self.image, col_glow, (cx, cy), (int(ex), int(ey)), 1)
        
        # 9. 交叉/删除 (Cross) - X 形状
        elif b_type == "cross":
            thick = 3
            l = size * 2
            # X 形状
            pygame.draw.line(self.image, col_main, (cx - l, cy - l), (cx + l, cy + l), thick)
            pygame.draw.line(self.image, col_main, (cx + l, cy - l), (cx - l, cy + l), thick)
            # 发光边缘
            pygame.draw.line(self.image, col_glow, (cx - l - 1, cy - l - 1), (cx + l + 1, cy + l + 1), 1)
            pygame.draw.line(self.image, col_glow, (cx + l + 1, cy - l - 1), (cx - l - 1, cy + l + 1), 1)
        
        # 10. 熔岩/毒云 (Blob/Cloud) - 使用帧数模拟脉动
        elif b_type in ["blob", "cloud"]:
            for i in range(4):
                # 用帧数+索引生成稳定的偏移
                ox = int(math.sin(t + i * 1.5) * 3)
                oy = int(math.cos(t + i * 1.2) * 3)
                r = size - (i % 3)
                pygame.draw.circle(self.image, col_main, (cx + ox, cy + oy), r)
            pygame.draw.circle(self.image, col_glow, (cx, cy), size // 2)
        
        # 11. 机械弩箭 (Bolt)
        elif b_type == "bolt":
            # 箭杆
            pygame.draw.line(self.image, col_main, (cx, cy - size * 3), (cx, cy + size * 2), 3)
            # 箭头
            pygame.draw.polygon(self.image, col_glow, 
                              [(cx, cy - size * 3.5), (cx - 4, cy - size * 2), (cx + 4, cy - size * 2)])
            # 箭羽
            pygame.draw.line(self.image, col_main, (cx - 4, cy + size), (cx, cy + size * 2), 2)
            pygame.draw.line(self.image, col_main, (cx + 4, cy + size), (cx, cy + size * 2), 2)
        
        # 默认：链节形状
        else:
            chain_col = self.theme["chain"]
            core_col = self.theme["core"]
            pulse_col = self.theme["pulse"]
            
            for i in range(3):
                glow_r = 12 - i * 2
                pygame.draw.ellipse(self.image, (*core_col, 40 + i * 20),
                                  (cx - glow_r, cy - glow_r - 4, glow_r * 2, glow_r * 2 + 8))
            
            for seg in range(3):
                seg_y = cy - 8 + seg * 8
                seg_pulse = math.sin(t * 2 + seg) * 2
                seg_w = 8 + int(seg_pulse)
                pygame.draw.ellipse(self.image, chain_col,
                                  (cx - seg_w // 2, seg_y - 5, seg_w, 10))
            
            pygame.draw.line(self.image, pulse_col, (cx, cy - 12), (cx, cy + 12), 2)
            core_r = 4 + int(abs(math.sin(t * 3)) * 2)
            pygame.draw.circle(self.image, pulse_col, (cx, cy), core_r)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), core_r // 2)
        
    def on_hit(self, target):
        """命中时生成星链节"""
        if hasattr(target, 'rect'):
            chain_node = ChainNode(target.rect.centerx, target.rect.centery, 
                                  self.damage * 0.3, self.owner, self.style)
            all_sprites.add(chain_node)
            bullets.add(chain_node)
        return True


# ==================== 星链节（留场单位）====================
class ChainNode(pygame.sprite.Sprite):
    """星链节 - 留场3s，每1s延伸1节，最多5节"""
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.frame = 0
        self.lifetime = 180  # 3秒 @ 60fps
        self.grow_interval = 60  # 1秒生长一次
        self.last_grow = 0
        self.chain_count = 1  # 当前链节数
        self.max_chains = 5
        
        # 子链节列表
        self.child_chains = []
        self.is_activated = False
        
        # 创建图像
        self.size = 40
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        # 生命结束
        if self.lifetime <= 0:
            self._expire()
            return
        
        # 链节生长
        if self.frame - self.last_grow >= self.grow_interval and self.chain_count < self.max_chains:
            self._grow_chain()
            self.last_grow = self.frame
        
        # 链节≥3时释放激光栅 - 降低频率
        if self.chain_count >= 3 and self.frame % 60 == 0:
            self._fire_laser_grid()
        
        # 持续DOT伤害
        self._apply_dot()
        
        # 绘制
        self._render()
        
    def _grow_chain(self):
        """生长新链节"""
        self.chain_count += 1
        # 随机方向延伸
        angle = random.uniform(0, math.pi * 2)
        dist = 60
        new_x = self.float_x + math.cos(angle) * dist
        new_y = self.float_y + math.sin(angle) * dist
        
        # 限制在屏幕内
        new_x = max(30, min(WIDTH - 30, new_x))
        new_y = max(30, min(HEIGHT - 30, new_y))
        
        self.child_chains.append({
            'x': new_x, 'y': new_y, 
            'angle': angle, 
            'frame': 0
        })
        
    def _fire_laser_grid(self):
        """释放十字激光栅 - 只从主节点发射"""
        laser = LaserGrid(self.float_x, self.float_y, self.damage * 0.5, 
                         self.owner, self.style)
        all_sprites.add(laser)
        bullets.add(laser)
            
    def _apply_dot(self):
        """对范围内敌人造成DOT"""
        if self.frame % 20 != 0:
            return
        for mob in mobs:
            dist = math.hypot(mob.rect.centerx - self.float_x,
                            mob.rect.centery - self.float_y)
            if dist < 80:
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage * 0.1)
                    
    def _expire(self):
        """链节消失"""
        self.kill()
        
    def activate(self):
        """被激活时爆炸"""
        if self.is_activated:
            return
        self.is_activated = True
        
        # 创建爆炸效果
        explosion = ChainExplosion(self.float_x, self.float_y, self.damage * 2,
                                  self.owner, self.style)
        all_sprites.add(explosion)
        bullets.add(explosion)
        
        # 掉落吞噬核
        pickup = VoidCorePickup(self.float_x, self.float_y, 20)
        all_sprites.add(pickup)
        
        self.kill()
        
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.08
        
        chain_col = self.theme["chain"]
        core_col = self.theme["core"]
        pulse_col = self.theme["pulse"]
        void_col = self.theme["void"]
        
        # 吸扯范围指示
        range_alpha = int(30 + 20 * math.sin(t))
        pygame.draw.circle(self.image, (*void_col, range_alpha), (cx, cy), 18)
        
        # 核心光晕
        for i in range(4):
            glow_r = 14 - i * 2 + int(math.sin(t * 2) * 2)
            glow_alpha = 60 + i * 30
            pygame.draw.circle(self.image, (*core_col, glow_alpha), (cx, cy), glow_r)
        
        # 核心
        core_r = 8 + int(math.sin(t * 3) * 2)
        pygame.draw.circle(self.image, chain_col, (cx, cy), core_r)
        pygame.draw.circle(self.image, pulse_col, (cx, cy), core_r - 3)
        
        # 链节数指示（小圆点）
        for i in range(self.chain_count):
            dot_angle = i * math.pi * 2 / max(1, self.chain_count) + t
            dot_r = 12
            dx = cx + math.cos(dot_angle) * dot_r
            dy = cy + math.sin(dot_angle) * dot_r
            pygame.draw.circle(self.image, pulse_col, (int(dx), int(dy)), 3)


# ==================== 激光栅 ====================
class LaserGrid(pygame.sprite.Sprite):
    """十字激光栅 - 穿透伤害"""
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 999
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.frame = 0
        self.lifetime = 12  # 0.2秒（缩短生命周期）
        
        # 十字激光大小 - 减小 Surface
        self.size = 120
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        self.hit_enemies = set()
        
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 检测碰撞
        self._check_hits()
        
        # 绘制
        self._render()
        
    def _check_hits(self):
        """检测十字范围内敌人"""
        for mob in mobs:
            if id(mob) in self.hit_enemies:
                continue
            mx, my = mob.rect.centerx, mob.rect.centery
            # 十字范围检测
            in_horizontal = abs(my - self.float_y) < 15 and abs(mx - self.float_x) < 80
            in_vertical = abs(mx - self.float_x) < 15 and abs(my - self.float_y) < 80
            if in_horizontal or in_vertical:
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
                    self.hit_enemies.add(id(mob))
                    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        laser_col = self.theme["laser"]
        pulse_col = self.theme["pulse"]
        
        # 激光强度随时间衰减
        intensity = self.lifetime / 12
        alpha = int(180 * intensity)
        
        # 简化绘制 - 只画一层
        pygame.draw.line(self.image, (*laser_col, alpha), (0, cy), (self.size, cy), 6)
        pygame.draw.line(self.image, (*laser_col, alpha), (cx, 0), (cx, self.size), 6)
        pygame.draw.circle(self.image, (*pulse_col, alpha), (cx, cy), 5)


# ==================== 链节爆炸 ====================
class ChainExplosion(pygame.sprite.Sprite):
    """链节爆炸效果"""
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.frame = 0
        self.lifetime = 20
        self.has_damaged = False
        
        self.size = 120
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 第一帧造成伤害
        if not self.has_damaged:
            self._deal_damage()
            self.has_damaged = True
        
        self._render()
        
    def _deal_damage(self):
        for mob in mobs:
            dist = math.hypot(mob.rect.centerx - self.float_x,
                            mob.rect.centery - self.float_y)
            if dist < 60:
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
                    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        pulse_col = self.theme["pulse"]
        laser_col = self.theme["laser"]
        
        progress = 1 - self.lifetime / 20
        radius = int(20 + progress * 40)
        alpha = int(255 * (1 - progress))
        
        # 爆炸波纹
        for i in range(3):
            r = radius - i * 8
            a = max(0, alpha - i * 60)
            if r > 0 and a > 0:
                pygame.draw.circle(self.image, (*laser_col, a), (cx, cy), r, 3)
        
        # 中心闪光
        if progress < 0.3:
            flash_alpha = int(255 * (1 - progress / 0.3))
            pygame.draw.circle(self.image, (*pulse_col, flash_alpha), (cx, cy), 15)


# ==================== 吞噬核拾取 ====================
class VoidCorePickup(pygame.sprite.Sprite):
    """吞噬核 - 拾取回复能量"""
    
    def __init__(self, x, y, energy=20):
        super().__init__()
        self.float_x = float(x)
        self.float_y = float(y)
        self.energy = energy
        
        self.frame = 0
        self.lifetime = 300  # 5秒
        
        self.size = 24
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 缓慢下落
        self.float_y += 0.5
        self.rect.centery = int(self.float_y)
        
        self._render()
        
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.1
        
        # 核心颜色
        core_col = (80, 20, 120)
        pulse_col = (200, 50, 80)
        
        # 光晕
        pulse = abs(math.sin(t))
        glow_r = 10 + int(pulse * 3)
        pygame.draw.circle(self.image, (*core_col, 100), (cx, cy), glow_r)
        
        # 核心
        pygame.draw.circle(self.image, core_col, (cx, cy), 8)
        pygame.draw.circle(self.image, pulse_col, (cx, cy), 5)
        pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 2)
        
    def collect(self, player):
        """被玩家拾取"""
        if hasattr(player, 'energy'):
            player.energy = min(100, player.energy + self.energy)
        self.kill()


# ==================== 预览函数 ====================
def render_oro_bullet_preview(surface, effects, color, center_x, center_y, size, x, y, plane_id=None):
    """渲染奥罗子弹预览 - 根据皮肤类型绘制不同形状"""
    t = pygame.time.get_ticks() * 0.003
    
    style = "default"
    if effects:
        for effect in effects:
            if effect.startswith("oro_bullet_"):
                style = effect.replace("oro_bullet_", "")
                break
    
    theme = get_theme(style)
    b_type = theme.get("type", "beam")
    col_main = theme.get("color", theme["core"])
    col_glow = theme.get("glow", theme["pulse"])
    b_size = theme.get("size", 8)
    
    cx, cy = int(center_x), int(center_y)
    
    # 背景光晕
    for i in range(3):
        glow_r = int(size * 0.25 - i * 4)
        if glow_r > 0:
            pygame.draw.circle(surface, (*col_glow, 30 + i * 15), (cx, cy), glow_r)
    
    # --- 根据类型绘制不同形状预览 ---
    
    # 1. 激光束 (Beam)
    if b_type == "beam":
        length = b_size * 4
        pygame.draw.rect(surface, col_glow, (cx - 4, cy - length // 2, 8, length))
        pygame.draw.rect(surface, col_main, (cx - 2, cy - length // 2, 4, length))
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy - length // 2), 4)
        pygame.draw.circle(surface, col_glow, (cx, cy + length // 2), 3)
    
    # 2. 幽灵法球 (Orb)
    elif b_type == "orb":
        pygame.draw.circle(surface, (*col_glow, 80), (cx, cy), b_size + 6)
        pygame.draw.circle(surface, col_main, (cx, cy), b_size + 2)
        pygame.draw.circle(surface, (255, 255, 255), (cx - 3, cy - 3), 3)
        for i in range(3):
            pygame.draw.circle(surface, (*col_main, 60 - i * 20), (cx, cy + b_size + 4 + i * 5), b_size - i)
    
    # 3. 导弹 (Missile)
    elif b_type == "missile":
        pts = [
            (cx, cy - b_size * 3),
            (cx + b_size + 2, cy + b_size),
            (cx, cy - 2),
            (cx - b_size - 2, cy + b_size)
        ]
        pygame.draw.polygon(surface, col_main, pts)
        pygame.draw.polygon(surface, col_glow, pts, 2)
        pygame.draw.polygon(surface, col_glow, 
                          [(cx - 4, cy + b_size - 2), (cx, cy + b_size + 8), (cx + 4, cy + b_size - 2)])
    
    # 4. 冰晶 (Shard)
    elif b_type == "shard":
        rot = math.sin(t * 0.8) * 3
        pts = [
            (cx, cy - b_size * 2 + rot),
            (cx + b_size + 2, cy),
            (cx, cy + b_size * 2 + rot),
            (cx - b_size - 2, cy)
        ]
        pygame.draw.polygon(surface, col_main, pts)
        pygame.draw.polygon(surface, col_glow, pts, 2)
        pygame.draw.circle(surface, col_glow, (cx, cy), b_size // 2)
    
    # 5. 矩阵像素 (Pixel)
    elif b_type == "pixel":
        pygame.draw.rect(surface, col_main, (cx - b_size, cy - b_size, b_size * 2, b_size * 2))
        for i in range(3):
            pygame.draw.rect(surface, (*col_main, 80 - i * 25),
                           (cx - b_size, cy + b_size + 2 + i * (b_size + 1), b_size * 2, b_size * 2))
    
    # 6. 水墨 (Ink)
    elif b_type == "ink":
        pygame.draw.circle(surface, col_main, (cx, cy), b_size + 2)
        for i in range(3):
            angle = t * 0.5 + i * 2.0
            sx = cx + int(math.cos(angle) * 6)
            sy = cy + 10 + i * 3
            pygame.draw.circle(surface, col_main, (sx, sy), 2 + i % 2)
    
    # 7. 纸飞镖 (Triangle)
    elif b_type == "triangle":
        pts = [
            (cx, cy - b_size * 3),
            (cx + b_size + 3, cy + b_size + 2),
            (cx - b_size - 3, cy + b_size + 2)
        ]
        pygame.draw.polygon(surface, col_main, pts)
        pygame.draw.line(surface, col_glow, (cx, cy - b_size * 3), (cx, cy + b_size + 2), 2)
    
    # 8. 黑洞 (Void Hole)
    elif b_type == "void_hole":
        glow_size = b_size + int(abs(math.sin(t * 0.5)) * 4)
        pygame.draw.circle(surface, col_glow, (cx, cy), glow_size + 4)
        pygame.draw.circle(surface, col_main, (cx, cy), b_size + 2)
        for i in range(4):
            angle = t + i * math.pi / 2
            ex = cx + math.cos(angle) * (b_size + 8)
            ey = cy + math.sin(angle) * (b_size + 8)
            pygame.draw.line(surface, col_glow, (cx, cy), (int(ex), int(ey)), 2)
    
    # 9. 交叉/删除 (Cross)
    elif b_type == "cross":
        l = b_size * 2
        pygame.draw.line(surface, col_main, (cx - l, cy - l), (cx + l, cy + l), 4)
        pygame.draw.line(surface, col_main, (cx + l, cy - l), (cx - l, cy + l), 4)
        pygame.draw.line(surface, col_glow, (cx - l - 1, cy - l - 1), (cx + l + 1, cy + l + 1), 2)
        pygame.draw.line(surface, col_glow, (cx + l + 1, cy - l - 1), (cx - l - 1, cy + l + 1), 2)
    
    # 10. 熔岩/毒云 (Blob/Cloud)
    elif b_type in ["blob", "cloud"]:
        for i in range(5):
            ox = int(math.sin(t + i * 1.3) * 4)
            oy = int(math.cos(t + i * 1.1) * 4)
            r = b_size - (i % 3)
            pygame.draw.circle(surface, col_main, (cx + ox, cy + oy), r + 2)
        pygame.draw.circle(surface, col_glow, (cx, cy), b_size // 2)
    
    # 11. 机械弩箭 (Bolt)
    elif b_type == "bolt":
        pygame.draw.line(surface, col_main, (cx, cy - b_size * 3), (cx, cy + b_size * 2), 4)
        pygame.draw.polygon(surface, col_glow,
                          [(cx, cy - b_size * 4), (cx - 5, cy - b_size * 2), (cx + 5, cy - b_size * 2)])
        pygame.draw.line(surface, col_main, (cx - 5, cy + b_size), (cx, cy + b_size * 2), 3)
        pygame.draw.line(surface, col_main, (cx + 5, cy + b_size), (cx, cy + b_size * 2), 3)
    
    # 默认：链节形状
    else:
        chain_col = theme["chain"]
        pulse_col = theme["pulse"]
        chain_y = cy - size * 0.15
        for seg in range(3):
            seg_y = int(chain_y + seg * 12)
            seg_w = 10 + int(math.sin(t * 2 + seg) * 2)
            pygame.draw.ellipse(surface, chain_col,
                              (cx - seg_w // 2, seg_y - 6, seg_w, 12))
            pygame.draw.ellipse(surface, (*pulse_col, 180),
                              (cx - seg_w // 2 + 2, seg_y - 4, seg_w - 4, 8))
        core_r = 6 + int(abs(math.sin(t * 2)) * 2)
        pygame.draw.circle(surface, pulse_col, (cx, int(chain_y + 12)), core_r)


# ==================== 终极技能 I: 宇宙坍缩·维度网格 [F] ====================
class DimensionGridSkill(pygame.sprite.Sprite):
    """
    宇宙坍缩·维度网格 - 全屏激光网格封锁
    机体节段解离飞向四边，构建激光网格向中心收缩
    """
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.frame = 0
        self.phase = "scatter"  # scatter -> build -> collapse -> end
        self.scatter_duration = 30   # 0.5s 节段飞散
        self.build_duration = 20     # 0.33s 构建网格
        self.collapse_duration = 180 # 3s 收缩
        self.end_duration = 30       # 0.5s 结束
        
        # 节段位置 - 飞向四边
        self.segments = []
        self._init_segments()
        
        # 激光网格
        self.grid_lines = []
        self.grid_spacing = 60  # 初始间距
        self.rotation = 0
        
        self.size = max(WIDTH, HEIGHT) + 100
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        # 锁定玩家 + 无敌状态
        if owner:
            owner.skill_locked = True
            owner.invincible = True  # 技能期间无敌
            
    def _init_segments(self):
        """初始化节段，准备飞向四边"""
        edges = ['top', 'bottom', 'left', 'right']
        for i in range(24):  # 24个节段
            edge = edges[i % 4]
            if edge == 'top':
                target = (random.randint(50, WIDTH - 50), -20)
            elif edge == 'bottom':
                target = (random.randint(50, WIDTH - 50), HEIGHT + 20)
            elif edge == 'left':
                target = (-20, random.randint(50, HEIGHT - 50))
            else:
                target = (WIDTH + 20, random.randint(50, HEIGHT - 50))
            
            self.segments.append({
                'x': self.float_x,
                'y': self.float_y,
                'tx': target[0],
                'ty': target[1],
                'edge': edge
            })
    
    def update(self):
        self.frame += 1
        
        if self.phase == "scatter":
            self._update_scatter()
            if self.frame >= self.scatter_duration:
                self.phase = "build"
                self.frame = 0
        elif self.phase == "build":
            self._build_grid()
            if self.frame >= self.build_duration:
                self.phase = "collapse"
                self.frame = 0
        elif self.phase == "collapse":
            self._update_collapse()
            self._deal_damage()
            self._clear_bullets()
            if self.frame >= self.collapse_duration:
                self.phase = "end"
                self.frame = 0
                self._final_explosion()
        elif self.phase == "end":
            if self.frame >= self.end_duration:
                if self.owner:
                    self.owner.skill_locked = False
                    self.owner.invincible = False  # 解除无敌
                self.kill()
                return
        
        self._render()
    
    def _update_scatter(self):
        """节段飞向边缘"""
        prog = self.frame / self.scatter_duration
        for seg in self.segments:
            seg['x'] = seg['x'] + (seg['tx'] - seg['x']) * 0.15
            seg['y'] = seg['y'] + (seg['ty'] - seg['y']) * 0.15
    
    def _build_grid(self):
        """构建激光网格"""
        if self.frame == 1:
            # 生成网格线
            for i in range(0, WIDTH + 100, self.grid_spacing):
                self.grid_lines.append({'type': 'v', 'pos': i, 'alpha': 0})
            for i in range(0, HEIGHT + 100, self.grid_spacing):
                self.grid_lines.append({'type': 'h', 'pos': i, 'alpha': 0})
        
        # 渐显
        for line in self.grid_lines:
            line['alpha'] = min(255, line['alpha'] + 15)
    
    def _update_collapse(self):
        """网格向中心收缩"""
        self.rotation += 0.5  # 缓慢旋转
        
        # 收缩网格间距
        prog = self.frame / self.collapse_duration
        self.grid_spacing = max(20, 60 - int(prog * 40))
    
    def _deal_damage(self):
        """对敌人造成伤害"""
        if self.frame % 12 == 0:  # 降低频率，增加单次伤害
            for mob in mobs:
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage * 0.15)
                    # 玻璃碎裂效果 - 降低生成频率
                    if (self.frame + id(mob)) % 40 == 0:
                        self._spawn_shatter(mob.rect.centerx, mob.rect.centery)
    
    def _clear_bullets(self):
        """消弹"""
        for bullet in enemy_bullets:
            if bullet.rect.colliderect(pygame.Rect(0, 0, WIDTH, HEIGHT)):
                bullet.kill()
    
    def _spawn_shatter(self, x, y):
        """生成碎裂粒子"""
        effect = ShatterEffect(x, y, self.theme)
        all_sprites.add(effect)
    
    def _final_explosion(self):
        """最终爆发"""
        flash = ScreenFlash((0, 255, 255), 25)
        all_sprites.add(flash)
        
        # 对所有敌人造成大伤害
        for mob in mobs:
            if hasattr(mob, 'take_damage'):
                mob.take_damage(self.damage * 2)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.1
        
        laser_col = self.theme.get("laser", (0, 255, 255))
        pulse_col = self.theme.get("pulse", (180, 100, 255))
        core_col = self.theme.get("core", (148, 0, 211))
        
        # 绘制飞散的节段
        if self.phase == "scatter":
            for seg in self.segments:
                sx = int(seg['x'] - (WIDTH // 2 - cx))
                sy = int(seg['y'] - (HEIGHT // 2 - cy))
                pygame.draw.circle(self.image, pulse_col, (sx, sy), 6)
                pygame.draw.circle(self.image, laser_col, (sx, sy), 3)
        
        # 绘制激光网格
        if self.phase in ["build", "collapse"]:
            offset_x = WIDTH // 2 - cx
            offset_y = HEIGHT // 2 - cy
            
            # 只绘制每隔一条的网格线，减少绘制次数
            for i, line in enumerate(self.grid_lines):
                if i % 2 == 0:  # 跳过一半的线
                    continue
                alpha = min(180, line['alpha'])
                col = (*laser_col, alpha)
                
                if line['type'] == 'v':
                    x = int(line['pos'] - offset_x)
                    pygame.draw.line(self.image, col, (x, 0), (x, self.size), 2)
                else:
                    y = int(line['pos'] - offset_y)
                    pygame.draw.line(self.image, col, (0, y), (self.size, y), 2)
            
            # 边缘节段发光 - 简化
            glow_r = 8 + int(math.sin(t * 3) * 3)
            for seg in self.segments:
                sx = int(seg['x'] - offset_x)
                sy = int(seg['y'] - offset_y)
                pygame.draw.circle(self.image, pulse_col, (sx, sy), glow_r)


# ==================== 玻璃碎裂效果 ====================
class ShatterEffect(pygame.sprite.Sprite):
    """玻璃碎裂粒子效果"""
    
    def __init__(self, x, y, theme):
        super().__init__()
        self.float_x = float(x)
        self.float_y = float(y)
        self.theme = theme
        
        self.frame = 0
        self.lifetime = 20
        
        self.shards = []
        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            self.shards.append({
                'x': 0, 'y': 0,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.randint(2, 5)
            })
        
        self.size = 60
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        
        for shard in self.shards:
            shard['x'] += shard['vx']
            shard['y'] += shard['vy']
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        alpha = int(255 * (1 - self.frame / self.lifetime))
        col = (*self.theme.get("laser", (0, 255, 255)), alpha)
        
        for shard in self.shards:
            sx = int(cx + shard['x'])
            sy = int(cy + shard['y'])
            pygame.draw.polygon(self.image, col, [
                (sx, sy - shard['size']),
                (sx + shard['size'], sy),
                (sx, sy + shard['size']),
                (sx - shard['size'], sy)
            ])


# ==================== 终极技能 II: 弑神冲袭·现实撕裂 [G] ====================
class GodSlayerSkill(pygame.sprite.Sprite):
    """
    弑神冲袭·现实撕裂 - 极速Z字冲撞，完全无敌
    机体化为闪电在屏幕内高频折返，留下时空裂痕
    """
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.frame = 0
        self.phase = "charge"  # charge -> dash -> explode
        self.charge_duration = 20    # 0.33s 蓄力
        self.dash_duration = 180     # 3s 冲刺
        self.explode_duration = 30   # 0.5s 爆炸
        
        # 冲刺路径
        self.dash_points = []
        self.current_target = 0
        self.dash_speed = 25
        self.trail = []  # 残影轨迹
        self.rifts = []  # 时空裂痕
        
        # 无敌状态
        if owner:
            owner.invincible = True
            owner.skill_locked = True
            self.original_pos = (owner.rect.centerx, owner.rect.centery)
        
        self.size = 100
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        self._generate_dash_path()
    
    def _generate_dash_path(self):
        """生成Z字形冲刺路径"""
        # 8-12次折返
        num_points = random.randint(8, 12)
        for i in range(num_points):
            px = random.randint(50, WIDTH - 50)
            py = random.randint(50, HEIGHT - 50)
            self.dash_points.append((px, py))
    
    def update(self):
        self.frame += 1
        
        if self.phase == "charge":
            if self.frame >= self.charge_duration:
                self.phase = "dash"
                self.frame = 0
        elif self.phase == "dash":
            self._update_dash()
            if self.frame >= self.dash_duration or self.current_target >= len(self.dash_points):
                self.phase = "explode"
                self.frame = 0
                self._trigger_explosion()
        elif self.phase == "explode":
            if self.frame >= self.explode_duration:
                self._end_skill()
                self.kill()
                return
        
        self._render()
    
    def _update_dash(self):
        """更新冲刺"""
        if self.current_target >= len(self.dash_points):
            return
        
        target = self.dash_points[self.current_target]
        dx = target[0] - self.float_x
        dy = target[1] - self.float_y
        dist = math.hypot(dx, dy)
        
        if dist < self.dash_speed:
            # 到达目标点，生成裂痕
            self._spawn_rift(self.float_x, self.float_y)
            self.current_target += 1
            # 对路径上敌人造成伤害
            self._deal_collision_damage()
        else:
            # 移动
            self.float_x += dx / dist * self.dash_speed
            self.float_y += dy / dist * self.dash_speed
            
            # 添加残影（减少存储量）
            if self.frame % 2 == 0:
                self.trail.append({'x': self.float_x, 'y': self.float_y, 'alpha': 255})
                if len(self.trail) > 15:
                    self.trail.pop(0)
        
        # 更新残影透明度
        for tr in self.trail:
            tr['alpha'] = max(0, tr['alpha'] - 20)
        
        # 更新机体位置
        if self.owner:
            self.owner.rect.center = (int(self.float_x), int(self.float_y))
        
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _spawn_rift(self, x, y):
        """生成时空裂痕"""
        rift = RealityRift(x, y, self.damage * 0.5, self.owner, self.style)
        all_sprites.add(rift)
        bullets.add(rift)
        self.rifts.append(rift)
    
    def _deal_collision_damage(self):
        """碰撞伤害"""
        for mob in mobs:
            dist = math.hypot(mob.rect.centerx - self.float_x, 
                            mob.rect.centery - self.float_y)
            if dist < 60:
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage * 1.5)
    
    def _trigger_explosion(self):
        """所有裂痕同时爆炸"""
        for rift in self.rifts:
            if rift.alive():
                rift.explode()
        
        flash = ScreenFlash((255, 0, 255), 20)
        all_sprites.add(flash)
    
    def _end_skill(self):
        """结束技能"""
        if self.owner:
            self.owner.invincible = False
            self.owner.skill_locked = False
            # 返回原位置或当前位置
            if hasattr(self, 'original_pos'):
                self.owner.rect.center = self.original_pos
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.15
        
        pulse_col = self.theme.get("pulse", (180, 100, 255))
        laser_col = self.theme.get("laser", (0, 255, 255))
        
        if self.phase == "charge":
            # 蓄力效果 - 反色闪烁
            glow = int(128 + 127 * math.sin(t * 5))
            pygame.draw.circle(self.image, (glow, glow, 255), (cx, cy), 30)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 15)
        
        elif self.phase == "dash":
            # 光带核心
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 12)
            pygame.draw.circle(self.image, laser_col, (cx, cy), 8)
            
            # Glitch噪点 - 使用帧数生成稳定位置
            for i in range(5):
                angle = self.frame * 0.3 + i * 1.2
                gx = cx + int(math.cos(angle) * 15)
                gy = cy + int(math.sin(angle * 0.7) * 15)
                line_len = 8 + (i % 3) * 3
                pygame.draw.line(self.image, pulse_col, 
                               (gx, gy), (gx + line_len, gy), 2)


# ==================== 时空裂痕 ====================
class RealityRift(pygame.sprite.Sprite):
    """弑神冲袭留下的时空裂痕"""
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        self.frame = 0
        self.lifetime = 180  # 3秒后自动爆炸
        self.exploded = False
        
        # 二进制粒子
        self.particles = []
        for _ in range(8):
            self.particles.append({
                'x': random.uniform(-15, 15),
                'y': random.uniform(-15, 15),
                'char': random.choice(['0', '1']),
                'alpha': random.randint(100, 255)
            })
        
        self.size = 80
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        
        if self.frame >= self.lifetime and not self.exploded:
            self.explode()
        
        if self.exploded and self.frame > 20:
            self.kill()
            return
        
        # 持续伤害（每30帧检测一次，减少开销）
        if not self.exploded and self.frame % 30 == 0:
            for mob in mobs:
                dist = math.hypot(mob.rect.centerx - self.float_x,
                                mob.rect.centery - self.float_y)
                if dist < 40 and hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage * 0.4)
        
        self._render()
    
    def explode(self):
        """爆炸"""
        self.exploded = True
        self.frame = 0
        
        # 对范围内敌人造成伤害
        for mob in mobs:
            dist = math.hypot(mob.rect.centerx - self.float_x,
                            mob.rect.centery - self.float_y)
            if dist < 80:
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.1
        
        void_col = self.theme.get("void", (20, 0, 40))
        pulse_col = self.theme.get("pulse", (180, 100, 255))
        
        if not self.exploded:
            # 锯齿裂痕 - 使用正弦波动模拟不规则
            points = []
            for i in range(6):
                angle = i * math.pi / 3 + t * 0.5
                r = 15 + int(math.sin(t * 2 + i) * 3)
                points.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
            pygame.draw.polygon(self.image, void_col, points)
            pygame.draw.polygon(self.image, pulse_col, points, 2)
            
            # 二进制粒子喷涌
            for p in self.particles:
                px = int(cx + p['x'] + math.sin(t + p['x']) * 3)
                py = int(cy + p['y'] - self.frame * 0.3)
                if 0 < px < self.size and 0 < py < self.size:
                    pygame.draw.circle(self.image, (*pulse_col, p['alpha']), (px, py), 2)
        else:
            # 爆炸效果
            exp_r = self.frame * 4
            alpha = max(0, 255 - self.frame * 12)
            pygame.draw.circle(self.image, (*pulse_col, alpha), (cx, cy), exp_r, 3)


# ==================== 终极技能 III: 视界线·衔尾蛇 [C] ====================
class OuroborosSkill(pygame.sprite.Sprite):
    """
    视界线·衔尾蛇 - 黑洞吞噬终极清屏
    机体螺旋运动形成光环，中心撕开微型黑洞吞噬一切
    """
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        # 固定在屏幕中心
        self.float_x = float(WIDTH // 2)
        self.float_y = float(HEIGHT // 2)
        
        self.frame = 0
        self.phase = "spiral"  # spiral -> singularity -> collapse
        self.spiral_duration = 60     # 1s 螺旋形成
        self.singularity_duration = 180  # 3s 黑洞吸引
        self.collapse_duration = 40   # 0.67s 坍缩
        
        # 螺旋参数
        self.spiral_angle = 0
        self.spiral_speed = 0.2
        self.ring_radius = 80
        
        # 黑洞参数
        self.blackhole_radius = 0
        self.max_blackhole_radius = 200
        self.pull_strength = 0
        
        # 锁定玩家 + 无敌状态
        if owner:
            owner.skill_locked = True
            owner.invincible = True  # 技能期间无敌
            self.original_pos = (owner.rect.centerx, owner.rect.centery)
        
        self.size = 500
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.float_x), int(self.float_y)))
    
    def update(self):
        self.frame += 1
        
        if self.phase == "spiral":
            self._update_spiral()
            if self.frame >= self.spiral_duration:
                self.phase = "singularity"
                self.frame = 0
                self._spawn_singularity()
        elif self.phase == "singularity":
            self._update_singularity()
            if self.frame >= self.singularity_duration:
                self.phase = "collapse"
                self.frame = 0
        elif self.phase == "collapse":
            self._update_collapse()
            if self.frame >= self.collapse_duration:
                self._final_annihilation()
                self._end_skill()
                self.kill()
                return
        
        # 更新机体位置（螺旋运动）
        if self.owner and self.phase == "spiral":
            angle = self.spiral_angle
            ox = self.float_x + math.cos(angle) * self.ring_radius
            oy = self.float_y + math.sin(angle) * self.ring_radius
            self.owner.rect.center = (int(ox), int(oy))
        elif self.owner:
            # 固定在中心
            self.owner.rect.center = (int(self.float_x), int(self.float_y))
        
        self._render()
    
    def _update_spiral(self):
        """螺旋阶段 - 机体加速旋转"""
        self.spiral_angle += self.spiral_speed
        self.spiral_speed = min(0.8, self.spiral_speed + 0.02)  # 加速
        self.ring_radius = max(20, 80 - self.frame)  # 收缩
    
    def _spawn_singularity(self):
        """生成奇点"""
        shockwave = BlackHoleShockwave(self.float_x, self.float_y, self.style)
        all_sprites.add(shockwave)
    
    def _update_singularity(self):
        """奇点阶段 - 持续吸引并伤害"""
        # 黑洞半径增长
        progress = self.frame / self.singularity_duration
        self.blackhole_radius = int(self.max_blackhole_radius * min(1, progress * 1.5))
        self.pull_strength = 3 + progress * 5
        
        # 每3帧更新一次吸引（降低频率）
        if self.frame % 3 == 0:
            cx, cy = self.float_x, self.float_y
            pull = self.pull_strength
            
            # 吸引所有敌人
            for mob in mobs:
                dx = mob.rect.centerx - cx
                dy = mob.rect.centery - cy
                dist = math.hypot(dx, dy)
                if dist > 30:
                    factor = pull * (1 - min(1, dist / 400)) / dist
                    mob.rect.centerx -= int(dx * factor)
                    mob.rect.centery -= int(dy * factor)
            
            # 吸引敌方子弹
            bh_r = self.blackhole_radius
            for bullet in enemy_bullets:
                dx = bullet.rect.centerx - cx
                dy = bullet.rect.centery - cy
                dist = math.hypot(dx, dy)
                if dist < bh_r:
                    bullet.kill()
                elif dist < 300:
                    factor = 3 / dist
                    if hasattr(bullet, 'float_x'):
                        bullet.float_x -= dx * factor
                        bullet.float_y -= dy * factor
        
        # 持续伤害 - 每15帧一次
        if self.frame % 15 == 0:
            bh_r = self.blackhole_radius
            for mob in mobs:
                dist = math.hypot(mob.rect.centerx - self.float_x,
                                mob.rect.centery - self.float_y)
                if dist < bh_r and hasattr(mob, 'take_damage'):
                    dmg_mult = 1.5 + (1 - dist / bh_r) * 0.5
                    mob.take_damage(self.damage * 0.2 * dmg_mult)
    
    def _update_collapse(self):
        """坍缩阶段 - 黑洞收缩"""
        progress = self.frame / self.collapse_duration
        self.blackhole_radius = int(self.max_blackhole_radius * (1 - progress))
        self.pull_strength = 10 * (1 - progress)
    
    def _final_annihilation(self):
        """终焉 - 全屏清屏"""
        # 闪白
        flash = ScreenFlash((255, 255, 255), 40)
        all_sprites.add(flash)
        
        # 秒杀所有非Boss敌人
        for mob in mobs:
            if hasattr(mob, 'is_boss') and mob.is_boss:
                # Boss受到大量伤害
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage * 5)
            else:
                # 非Boss直接秒杀
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(99999)
        
        # 掉落能量核
        for i in range(6):
            angle = i * math.pi / 3
            dist = 60
            px = self.float_x + math.cos(angle) * dist
            py = self.float_y + math.sin(angle) * dist
            pickup = VoidCorePickup(px, py, 50)
            all_sprites.add(pickup)
    
    def _end_skill(self):
        """结束技能"""
        if self.owner:
            self.owner.skill_locked = False
            self.owner.invincible = False  # 解除无敌
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.05
        
        void_col = self.theme.get("void", (20, 0, 40))
        core_col = self.theme.get("core", (148, 0, 211))
        pulse_col = self.theme.get("pulse", (180, 100, 255))
        laser_col = self.theme.get("laser", (0, 255, 255))
        
        if self.phase == "spiral":
            # 绘制机体轨迹圆环
            trail_alpha = min(200, self.frame * 5)
            pygame.draw.circle(self.image, (*laser_col, trail_alpha), (cx, cy), 
                             int(self.ring_radius), 3)
            
            # 旋转光点
            for i in range(8):
                angle = self.spiral_angle + i * math.pi / 4
                px = cx + math.cos(angle) * self.ring_radius
                py = cy + math.sin(angle) * self.ring_radius
                pygame.draw.circle(self.image, pulse_col, (int(px), int(py)), 4)
        
        elif self.phase == "singularity":
            # 引力透镜效果 - 扭曲环 (减少为3层)
            for i in range(3):
                ring_r = self.blackhole_radius - i * 40
                if ring_r > 0:
                    alpha = 120 - i * 25
                    pygame.draw.circle(self.image, (*core_col, alpha), (cx, cy), ring_r, 2)
            
            # 漩涡臂 (简化: 4条臂 × 6段 = 24次绘制)
            bh_r = self.blackhole_radius
            for arm in range(4):
                arm_offset = arm * math.pi / 2
                for seg in range(6):
                    prog = seg / 6
                    spiral_angle = t * 3 + arm_offset + prog * math.pi * 2
                    spiral_r = bh_r * prog * 0.85
                    sx = cx + math.cos(spiral_angle) * spiral_r
                    sy = cy + math.sin(spiral_angle) * spiral_r
                    dot_r = int(4 * (1 - prog) + 1)
                    pygame.draw.circle(self.image, pulse_col, (int(sx), int(sy)), dot_r)
            
            # 黑洞核心 (简化为2层)
            pygame.draw.circle(self.image, void_col, (cx, cy), 30)
            pygame.draw.circle(self.image, (0, 0, 0), (cx, cy), 20)
            
            # 事件视界
            horizon_pulse = int(5 + 3 * math.sin(t * 4))
            pygame.draw.circle(self.image, laser_col, (cx, cy), 35 + horizon_pulse, 2)
        
        elif self.phase == "collapse":
            # 坍缩效果
            progress = self.frame / self.collapse_duration
            collapse_r = int(self.blackhole_radius)
            
            # 收缩的光环
            if collapse_r > 5:
                pygame.draw.circle(self.image, (*laser_col, 200), (cx, cy), collapse_r, 4)
            
            # 中心闪光
            flash_r = int(10 + 30 * progress)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), flash_r)


# ==================== 黑洞冲击波 ====================
class BlackHoleShockwave(pygame.sprite.Sprite):
    """黑洞生成时的冲击波"""
    
    def __init__(self, x, y, style="default"):
        super().__init__()
        self.float_x = float(x)
        self.float_y = float(y)
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.lifetime = 30
        self.max_radius = 200
        
        self.size = 450
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        self._render()
        
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        progress = self.frame / self.lifetime
        radius = int(self.max_radius * progress)
        alpha = int(200 * (1 - progress))
        
        pulse_col = self.theme["pulse"]
        laser_col = self.theme["laser"]
        
        for i in range(3):
            r = radius - i * 10
            a = max(0, alpha - i * 40)
            if r > 0 and a > 0:
                pygame.draw.circle(self.image, (*laser_col, a), (cx, cy), r, 4 - i)


# ==================== 屏幕闪白效果 ====================
class ScreenFlash(pygame.sprite.Sprite):
    """全屏闪白效果"""
    
    def __init__(self, color=(255, 255, 255), duration=15):
        super().__init__()
        self.color = color
        self.frame = 0
        self.duration = duration
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
    def update(self):
        self.frame += 1
        if self.frame >= self.duration:
            self.kill()
            return
        
        progress = self.frame / self.duration
        alpha = int(200 * (1 - progress))
        self.image.fill((*self.color, alpha))
