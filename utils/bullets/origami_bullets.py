"""
折纸鹤·零式 - 专属子弹模块
千羽散 - 折纸刃子弹系统

特性：
- 12枚扇形散射的折纸飞镖
- 命中后三段弹射
- 7种独特子弹涂装
- 千羽护盾 - 羽毛切割墙

子弹涂装列表 (7种):
1. default - 虹彩飞镖（镭射变色）
2. golden - 金箔飞镖（金色+祥云光泽）
3. shadow - 暗影刃（紫黑+残影拖尾）
4. sakura - 樱花镖（花瓣形状+粉色旋转）
5. cyber - 数据碎片（青色+数字雨效果）
6. phoenix - 火羽镖（火焰形状+燃烧尾迹）
7. ice - 冰晶镖（六角雪花+冰蓝闪烁）
"""
import pygame
import math
import random

# 子弹涂装主题
ORIGAMI_BULLET_THEMES = [
    "origami_default",
    "origami_golden",
    "origami_shadow", 
    "origami_sakura",
    "origami_cyber",
    "origami_phoenix",
    "origami_ice"
]


def get_bullet_theme_colors(theme, frame):
    """获取子弹涂装颜色配置"""
    hue = (frame * 5) % 360
    rainbow = (
        int(200 + 55 * math.sin(math.radians(hue))),
        int(200 + 55 * math.sin(math.radians(hue + 120))),
        int(200 + 55 * math.sin(math.radians(hue + 240)))
    )
    
    themes = {
        "origami_default": {
            "main": rainbow,
            "edge": (255, 255, 255),
            "glow": rainbow,
            "trail": None
        },
        "origami_golden": {
            "main": (255, 215, 80),
            "edge": (255, 240, 150),
            "glow": (255, 200, 50),
            "trail": (255, 230, 100)
        },
        "origami_shadow": {
            "main": (80, 50, 120),
            "edge": (150, 100, 200),
            "glow": (120, 80, 180),
            "trail": (100, 60, 150)
        },
        "origami_sakura": {
            "main": (255, 180, 200),
            "edge": (255, 220, 230),
            "glow": (255, 150, 180),
            "trail": (255, 200, 210)
        },
        "origami_cyber": {
            "main": (0, 200, 255),
            "edge": (100, 255, 255),
            "glow": (0, 150, 255),
            "trail": (50, 200, 255)
        },
        "origami_phoenix": {
            "main": (255, 120, 30),
            "edge": (255, 200, 100),
            "glow": (255, 80, 20),
            "trail": (255, 150, 50)
        },
        "origami_ice": {
            "main": (180, 220, 255),
            "edge": (220, 240, 255),
            "glow": (150, 200, 255),
            "trail": (200, 230, 255)
        }
    }
    
    return themes.get(theme, themes["origami_default"])


class OrigamiBlade(pygame.sprite.Sprite):
    """折纸刃子弹 - 扇形散射 + 三段弹射 + 7种涂装"""
    
    def __init__(self, x, y, angle, damage, owner=None, bounce_count=3, speed=10, theme="origami_default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.speed = speed
        self.angle = angle
        self.bounce_count = bounce_count
        self.hit_enemies = set()
        self.theme = theme
        
        # 从owner获取涂装
        if owner and hasattr(owner, 'bullet_theme'):
            bt = owner.bullet_theme
            # bullet_theme 可能是字典或字符串
            if bt:
                if isinstance(bt, dict):
                    # 如果是字典，检查shape字段
                    shape = bt.get("shape", "")
                    if isinstance(shape, str) and shape.startswith("origami_"):
                        self.theme = shape
                elif isinstance(bt, str) and bt.startswith("origami_"):
                    self.theme = bt
        
        # 同时检查owner是否有bullet_theme_id属性
        if owner and hasattr(owner, 'bullet_theme_id'):
            btid = owner.bullet_theme_id
            if isinstance(btid, str) and btid.startswith("origami_"):
                self.theme = btid
        
        # 动画帧
        self.frame = 0
        self.spin_angle = 0
        
        # 位置和速度
        self.float_x = float(x)
        self.float_y = float(y)
        rad = math.radians(angle)
        self.vx = math.cos(rad) * speed
        self.vy = math.sin(rad) * speed
        
        # 拖尾系统
        self.trail_positions = []
        self.max_trail = 8
        
        # 创建图像
        self.size = 16
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self._draw_blade()
        self.rect = self.image.get_rect(center=(x, y))
        
        # 生命周期
        self.lifetime = 180
    
    def _draw_blade(self):
        """绘制折纸飞镖 - 7种独特涂装"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size, self.size
        
        # 获取涂装颜色
        colors = get_bullet_theme_colors(self.theme, self.frame)
        main_color = colors["main"]
        edge_color = colors["edge"]
        glow_color = colors["glow"]
        
        # 根据涂装选择不同的绘制方式
        if self.theme == "origami_sakura":
            self._draw_sakura_blade(cx, cy, main_color, edge_color, glow_color)
        elif self.theme == "origami_phoenix":
            self._draw_phoenix_blade(cx, cy, main_color, edge_color, glow_color)
        elif self.theme == "origami_ice":
            self._draw_ice_blade(cx, cy, main_color, edge_color, glow_color)
        elif self.theme == "origami_cyber":
            self._draw_cyber_blade(cx, cy, main_color, edge_color, glow_color)
        elif self.theme == "origami_shadow":
            self._draw_shadow_blade(cx, cy, main_color, edge_color, glow_color)
        elif self.theme == "origami_golden":
            self._draw_golden_blade(cx, cy, main_color, edge_color, glow_color)
        else:
            self._draw_default_blade(cx, cy, main_color, edge_color, glow_color)
    
    def _draw_default_blade(self, cx, cy, main_color, edge_color, glow_color):
        """默认虹彩飞镖"""
        points = []
        for i in range(4):
            a = self.spin_angle + i * 90
            px = cx + math.cos(math.radians(a)) * 12
            py = cy + math.sin(math.radians(a)) * 12
            points.append((px, py))
            a2 = self.spin_angle + i * 90 + 45
            px2 = cx + math.cos(math.radians(a2)) * 5
            py2 = cy + math.sin(math.radians(a2)) * 5
            points.append((px2, py2))
        
        pygame.draw.polygon(self.image, main_color, points)
        pygame.draw.polygon(self.image, edge_color, points, 1)
        
        glow_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*glow_color, 150), (5, 5), 5)
        self.image.blit(glow_surf, (cx - 5, cy - 5))
    
    def _draw_golden_blade(self, cx, cy, main_color, edge_color, glow_color):
        """金箔飞镖 - 带祥云光泽"""
        points = []
        for i in range(4):
            a = self.spin_angle + i * 90
            px = cx + math.cos(math.radians(a)) * 12
            py = cy + math.sin(math.radians(a)) * 12
            points.append((px, py))
            a2 = self.spin_angle + i * 90 + 45
            px2 = cx + math.cos(math.radians(a2)) * 5
            py2 = cy + math.sin(math.radians(a2)) * 5
            points.append((px2, py2))
        
        pygame.draw.polygon(self.image, main_color, points)
        pygame.draw.polygon(self.image, edge_color, points, 2)
        
        # 金色光泽条纹
        shimmer = int(128 + 127 * math.sin(self.frame * 0.2))
        for i in range(2):
            shine_angle = self.spin_angle + i * 180
            sx = cx + math.cos(math.radians(shine_angle)) * 6
            sy = cy + math.sin(math.radians(shine_angle)) * 6
            shine_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(shine_surf, (255, 255, shimmer, 180), (3, 3), 3)
            self.image.blit(shine_surf, (sx - 3, sy - 3))
        
        # 中心宝石
        pygame.draw.circle(self.image, (255, 200, 100), (cx, cy), 4)
        pygame.draw.circle(self.image, (255, 255, 200), (cx - 1, cy - 1), 2)
    
    def _draw_shadow_blade(self, cx, cy, main_color, edge_color, glow_color):
        """暗影刃 - 带残影效果"""
        # 残影层
        for i in range(3):
            shadow_alpha = 80 - i * 25
            offset = (i + 1) * 2
            shadow_pts = []
            for j in range(4):
                a = self.spin_angle - offset * 5 + j * 90
                px = cx + math.cos(math.radians(a)) * (12 - i)
                py = cy + math.sin(math.radians(a)) * (12 - i)
                shadow_pts.append((px, py))
                a2 = self.spin_angle - offset * 5 + j * 90 + 45
                px2 = cx + math.cos(math.radians(a2)) * (5 - i * 0.5)
                py2 = cy + math.sin(math.radians(a2)) * (5 - i * 0.5)
                shadow_pts.append((px2, py2))
            
            shadow_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.polygon(shadow_surf, (*main_color, shadow_alpha), shadow_pts)
            self.image.blit(shadow_surf, (0, 0))
        
        # 主体
        points = []
        for i in range(4):
            a = self.spin_angle + i * 90
            px = cx + math.cos(math.radians(a)) * 12
            py = cy + math.sin(math.radians(a)) * 12
            points.append((px, py))
            a2 = self.spin_angle + i * 90 + 45
            px2 = cx + math.cos(math.radians(a2)) * 5
            py2 = cy + math.sin(math.radians(a2)) * 5
            points.append((px2, py2))
        
        pygame.draw.polygon(self.image, main_color, points)
        pygame.draw.polygon(self.image, edge_color, points, 1)
        
        # 紫色核心脉冲
        pulse = int(100 + 55 * math.sin(self.frame * 0.3))
        pygame.draw.circle(self.image, (150, pulse, 255), (cx, cy), 3)
    
    def _draw_sakura_blade(self, cx, cy, main_color, edge_color, glow_color):
        """樱花镖 - 花瓣形状"""
        # 5瓣花瓣形状
        for i in range(5):
            petal_angle = self.spin_angle + i * 72
            rad = math.radians(petal_angle)
            
            # 花瓣外形
            tip_x = cx + math.cos(rad) * 12
            tip_y = cy + math.sin(rad) * 12
            
            # 花瓣两侧
            side1_rad = math.radians(petal_angle - 25)
            side2_rad = math.radians(petal_angle + 25)
            s1x = cx + math.cos(side1_rad) * 6
            s1y = cy + math.sin(side1_rad) * 6
            s2x = cx + math.cos(side2_rad) * 6
            s2y = cy + math.sin(side2_rad) * 6
            
            petal = [(cx, cy), (s1x, s1y), (tip_x, tip_y), (s2x, s2y)]
            pygame.draw.polygon(self.image, main_color, petal)
            pygame.draw.polygon(self.image, edge_color, petal, 1)
        
        # 花蕊
        pygame.draw.circle(self.image, (255, 220, 100), (cx, cy), 3)
        pygame.draw.circle(self.image, (255, 255, 200), (cx, cy), 2)
    
    def _draw_cyber_blade(self, cx, cy, main_color, edge_color, glow_color):
        """数据碎片 - 数字雨效果"""
        # 六边形数据碎片
        hex_points = []
        for i in range(6):
            a = self.spin_angle + i * 60
            px = cx + math.cos(math.radians(a)) * 11
            py = cy + math.sin(math.radians(a)) * 11
            hex_points.append((px, py))
        
        pygame.draw.polygon(self.image, main_color, hex_points)
        pygame.draw.polygon(self.image, edge_color, hex_points, 2)
        
        # 内部数据线
        for i in range(3):
            a1 = self.spin_angle + i * 60
            a2 = self.spin_angle + (i + 3) * 60
            x1 = cx + math.cos(math.radians(a1)) * 8
            y1 = cy + math.sin(math.radians(a1)) * 8
            x2 = cx + math.cos(math.radians(a2)) * 8
            y2 = cy + math.sin(math.radians(a2)) * 8
            pygame.draw.line(self.image, edge_color, (x1, y1), (x2, y2), 1)
        
        # 闪烁的数据点
        for i in range(4):
            if (self.frame + i * 5) % 20 < 10:
                data_angle = self.spin_angle + i * 90 + 45
                dx = cx + math.cos(math.radians(data_angle)) * 6
                dy = cy + math.sin(math.radians(data_angle)) * 6
                pygame.draw.circle(self.image, (255, 255, 255), (int(dx), int(dy)), 2)
    
    def _draw_phoenix_blade(self, cx, cy, main_color, edge_color, glow_color):
        """火羽镖 - 火焰形状"""
        # 火焰主体 - 不规则四角
        flame_points = []
        for i in range(4):
            a = self.spin_angle + i * 90
            # 火焰尖端有波动
            flicker = 2 * math.sin(self.frame * 0.5 + i * 1.5)
            px = cx + math.cos(math.radians(a)) * (12 + flicker)
            py = cy + math.sin(math.radians(a)) * (12 + flicker)
            flame_points.append((px, py))
            
            # 内凹
            a2 = self.spin_angle + i * 90 + 45
            px2 = cx + math.cos(math.radians(a2)) * 4
            py2 = cy + math.sin(math.radians(a2)) * 4
            flame_points.append((px2, py2))
        
        # 外焰 - 橙红色
        pygame.draw.polygon(self.image, main_color, flame_points)
        
        # 内焰 - 黄色
        inner_points = []
        for i in range(4):
            a = self.spin_angle + i * 90
            px = cx + math.cos(math.radians(a)) * 7
            py = cy + math.sin(math.radians(a)) * 7
            inner_points.append((px, py))
            a2 = self.spin_angle + i * 90 + 45
            px2 = cx + math.cos(math.radians(a2)) * 3
            py2 = cy + math.sin(math.radians(a2)) * 3
            inner_points.append((px2, py2))
        pygame.draw.polygon(self.image, edge_color, inner_points)
        
        # 火焰核心
        pygame.draw.circle(self.image, (255, 255, 200), (cx, cy), 3)
        
        # 火星
        for i in range(3):
            spark_a = self.spin_angle + i * 120 + self.frame * 2
            spark_d = 10 + (self.frame + i * 10) % 5
            sx = cx + math.cos(math.radians(spark_a)) * spark_d
            sy = cy + math.sin(math.radians(spark_a)) * spark_d
            if 0 <= sx < self.size * 2 and 0 <= sy < self.size * 2:
                pygame.draw.circle(self.image, (255, 200, 50), (int(sx), int(sy)), 1)
    
    def _draw_ice_blade(self, cx, cy, main_color, edge_color, glow_color):
        """冰晶镖 - 六角雪花"""
        # 六角雪花主体
        for i in range(6):
            branch_angle = self.spin_angle + i * 60
            rad = math.radians(branch_angle)
            
            # 主枝
            end_x = cx + math.cos(rad) * 12
            end_y = cy + math.sin(rad) * 12
            pygame.draw.line(self.image, main_color, (cx, cy), (end_x, end_y), 2)
            
            # 侧枝
            for j in range(2):
                branch_dist = 5 + j * 3
                bx = cx + math.cos(rad) * branch_dist
                by = cy + math.sin(rad) * branch_dist
                
                for side in [-1, 1]:
                    side_rad = math.radians(branch_angle + side * 60)
                    side_len = 4 - j
                    sx = bx + math.cos(side_rad) * side_len
                    sy = by + math.sin(side_rad) * side_len
                    pygame.draw.line(self.image, main_color, (bx, by), (sx, sy), 1)
        
        # 中心冰晶
        pygame.draw.circle(self.image, edge_color, (cx, cy), 4)
        
        # 闪烁光点
        sparkle = int(200 + 55 * math.sin(self.frame * 0.2))
        pygame.draw.circle(self.image, (sparkle, sparkle, 255), (cx, cy), 2)
    
    def update(self):
        """更新子弹状态"""
        self.frame += 1
        self.spin_angle += 15
        
        # 记录拖尾位置
        self.trail_positions.append((self.float_x, self.float_y))
        if len(self.trail_positions) > self.max_trail:
            self.trail_positions.pop(0)
        
        # 移动
        self.float_x += self.vx
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 重绘
        self._draw_blade()
        
        # 生命周期
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        
        # 边界检测（用于弹射）
        if self.rect.left < 0 or self.rect.right > 540:
            self.vx = -self.vx
            self.bounce_count -= 1
            if self.bounce_count < 0:
                self.kill()
        
        if self.rect.top < 0 or self.rect.bottom > 800:
            self.vy = -self.vy
            self.bounce_count -= 1
            if self.bounce_count < 0:
                self.kill()
    
    def on_hit_enemy(self, enemy, all_enemies=None):
        """命中敌人时的弹射逻辑"""
        if id(enemy) in self.hit_enemies:
            return False
        
        self.hit_enemies.add(id(enemy))
        
        # 还有弹射次数，寻找下一个目标
        if self.bounce_count > 0 and all_enemies:
            self.bounce_count -= 1
            
            # 寻找最近的未击中敌人
            nearest = None
            nearest_dist = 999999
            
            for e in all_enemies:
                if id(e) not in self.hit_enemies and e.rect.centery > 0:
                    dist = math.hypot(e.rect.centerx - self.rect.centerx,
                                     e.rect.centery - self.rect.centery)
                    if dist < nearest_dist and dist < 300:
                        nearest_dist = dist
                        nearest = e
            
            if nearest:
                # 转向新目标
                dx = nearest.rect.centerx - self.rect.centerx
                dy = nearest.rect.centery - self.rect.centery
                dist = max(1, math.hypot(dx, dy))
                self.vx = (dx / dist) * self.speed
                self.vy = (dy / dist) * self.speed
                self.angle = math.degrees(math.atan2(self.vy, self.vx))
                return True
        
        return True


class OrigamiCrane(pygame.sprite.Sprite):
    """纸鹤无人机 - 大招召唤的AI伙伴"""
    
    def __init__(self, x, y, owner, crane_id, damage_multiplier=0.3):
        super().__init__()
        self.owner = owner
        self.crane_id = crane_id
        self.damage_mult = damage_multiplier
        
        # 位置和移动
        self.float_x = float(x)
        self.float_y = float(y)
        self.target_x = x
        self.target_y = y
        
        # 动画
        self.frame = 0
        self.wing_angle = random.uniform(0, math.pi * 2)
        
        # 攻击
        self.fire_timer = random.randint(0, 30)  # 随机化攻击时机
        self.fire_interval = 45  # 攻击间隔
        
        # 生命周期
        self.lifetime = 360  # 6秒
        self.alpha = 255
        
        # 创建图像
        self.size = 24
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self._draw_crane()
        self.rect = self.image.get_rect(center=(x, y))
    
    def _draw_crane(self):
        """绘制迷你纸鹤"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size, self.size
        
        # 翅膀扇动
        wing_offset = math.sin(self.wing_angle) * 3
        
        # 虹彩颜色
        hue_shift = (self.frame * 3 + self.crane_id * 50) % 360
        r = int(200 + 55 * math.sin(math.radians(hue_shift)))
        g = int(200 + 55 * math.sin(math.radians(hue_shift + 120)))
        b = int(200 + 55 * math.sin(math.radians(hue_shift + 240)))
        crane_color = (r, g, b, self.alpha)
        white = (245, 245, 250, self.alpha)
        
        # 机身
        body = [
            (cx, cy - 10),
            (cx - 6, cy),
            (cx, cy + 5),
            (cx + 6, cy)
        ]
        pygame.draw.polygon(self.image, white, body)
        
        # 左翅膀
        left_wing = [
            (cx - 6, cy),
            (cx - 18 - wing_offset, cy - 2),
            (cx - 15 - wing_offset, cy + 5)
        ]
        pygame.draw.polygon(self.image, white, left_wing)
        
        # 右翅膀
        right_wing = [
            (cx + 6, cy),
            (cx + 18 + wing_offset, cy - 2),
            (cx + 15 + wing_offset, cy + 5)
        ]
        pygame.draw.polygon(self.image, white, right_wing)
        
        # 折痕
        pygame.draw.line(self.image, crane_color[:3], (cx, cy - 8), (cx, cy + 4), 1)
        pygame.draw.line(self.image, crane_color[:3], (cx - 5, cy), (cx - 15 - wing_offset, cy + 2), 1)
        pygame.draw.line(self.image, crane_color[:3], (cx + 5, cy), (cx + 15 + wing_offset, cy + 2), 1)
    
    def update(self):
        """更新纸鹤状态"""
        self.frame += 1
        self.wing_angle += 0.3
        
        # 跟随玩家，保持阵型
        if self.owner and hasattr(self.owner, 'rect'):
            # 7只纸鹤的阵型位置
            formation_angle = (self.crane_id / 7) * math.pi * 2 + self.frame * 0.02
            formation_radius = 50 + math.sin(self.frame * 0.05) * 10
            
            self.target_x = self.owner.rect.centerx + math.cos(formation_angle) * formation_radius
            self.target_y = self.owner.rect.centery - 30 + math.sin(formation_angle) * formation_radius * 0.5
        
        # 平滑移动
        self.float_x += (self.target_x - self.float_x) * 0.1
        self.float_y += (self.target_y - self.float_y) * 0.1
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 生命周期和淡出
        self.lifetime -= 1
        if self.lifetime < 60:
            self.alpha = int(255 * (self.lifetime / 60))
        
        if self.lifetime <= 0:
            self.kill()
        
        # 重绘
        self._draw_crane()
        
        # 攻击计时
        self.fire_timer += 1
    
    def should_fire(self):
        """是否应该发射子弹"""
        if self.fire_timer >= self.fire_interval:
            self.fire_timer = 0
            return True
        return False
    
    def get_bullet_damage(self, base_damage):
        """获取子弹伤害"""
        return int(base_damage * self.damage_mult)


class FeatherWall(pygame.sprite.Sprite):
    """千羽护盾 - 羽毛形成的移动切割墙"""
    
    def __init__(self, x, y, owner, direction="horizontal"):
        super().__init__()
        self.owner = owner
        self.direction = direction
        
        # 羽毛数量
        self.feather_count = 50  # 简化为50根，每根代表20根
        self.feathers = []
        
        # 生成羽毛
        if direction == "horizontal":
            for i in range(self.feather_count):
                fx = x - 200 + i * 8
                fy = y + random.uniform(-10, 10)
                self.feathers.append({
                    'x': fx, 'y': fy,
                    'angle': random.uniform(-30, 30),
                    'phase': random.uniform(0, math.pi * 2)
                })
            self.width = 400
            self.height = 40
        else:  # vertical
            for i in range(self.feather_count):
                fx = x + random.uniform(-10, 10)
                fy = y - 200 + i * 8
                self.feathers.append({
                    'x': fx, 'y': fy,
                    'angle': random.uniform(60, 120),
                    'phase': random.uniform(0, math.pi * 2)
                })
            self.width = 40
            self.height = 400
        
        # 动画
        self.frame = 0
        self.lifetime = 180  # 3秒
        self.alpha = 255
        
        # 伤害
        self.damage = 8
        self.hit_cooldown = {}  # 每个敌人的伤害冷却
        
        # 创建图像
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._draw_wall()
        self.rect = self.image.get_rect(center=(x, y))
        
        # 移动
        self.float_x = float(x)
        self.float_y = float(y)
        self.move_speed = 2
    
    def _draw_wall(self):
        """绘制羽毛墙"""
        self.image.fill((0, 0, 0, 0))
        
        # 基于方向计算偏移
        if self.direction == "horizontal":
            ox, oy = self.width // 2, self.height // 2
        else:
            ox, oy = self.width // 2, self.height // 2
        
        for i, f in enumerate(self.feathers):
            # 羽毛位置（相对于护盾中心）
            if self.direction == "horizontal":
                fx = (f['x'] - self.rect.centerx + ox) if hasattr(self, 'rect') else i * 8
                fy = self.height // 2 + math.sin(f['phase'] + self.frame * 0.1) * 5
            else:
                fx = self.width // 2 + math.sin(f['phase'] + self.frame * 0.1) * 5
                fy = (f['y'] - self.rect.centery + oy) if hasattr(self, 'rect') else i * 8
            
            # 虹彩颜色
            hue_shift = (self.frame * 2 + i * 10) % 360
            r = int(200 + 55 * math.sin(math.radians(hue_shift)))
            g = int(200 + 55 * math.sin(math.radians(hue_shift + 120)))
            b = int(200 + 55 * math.sin(math.radians(hue_shift + 240)))
            color = (r, g, b, self.alpha)
            
            # 绘制羽毛（简化为细长菱形）
            angle = f['angle'] + math.sin(self.frame * 0.05 + i * 0.1) * 10
            rad = math.radians(angle)
            length = 12
            
            points = [
                (fx + math.cos(rad) * length, fy + math.sin(rad) * length),
                (fx + math.cos(rad + math.pi/2) * 2, fy + math.sin(rad + math.pi/2) * 2),
                (fx - math.cos(rad) * length * 0.3, fy - math.sin(rad) * length * 0.3),
                (fx - math.cos(rad + math.pi/2) * 2, fy - math.sin(rad + math.pi/2) * 2)
            ]
            
            # 边界检查
            valid = True
            for px, py in points:
                if px < 0 or px >= self.width or py < 0 or py >= self.height:
                    valid = False
                    break
            
            if valid:
                pygame.draw.polygon(self.image, color[:3], points)
    
    def update(self):
        """更新护盾状态"""
        self.frame += 1
        
        # 跟随玩家
        if self.owner and hasattr(self.owner, 'rect'):
            if self.direction == "horizontal":
                self.float_x = self.owner.rect.centerx
                self.float_y = self.owner.rect.centery - 60
            else:
                self.float_x = self.owner.rect.centerx
                self.float_y = self.owner.rect.centery
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 更新羽毛位置
        for f in self.feathers:
            if self.direction == "horizontal":
                f['x'] = self.rect.centerx - 200 + self.feathers.index(f) * 8
            else:
                f['y'] = self.rect.centery - 200 + self.feathers.index(f) * 8
        
        # 生命周期
        self.lifetime -= 1
        if self.lifetime < 30:
            self.alpha = int(255 * (self.lifetime / 30))
        
        if self.lifetime <= 0:
            self.kill()
        
        # 更新冷却
        for enemy_id in list(self.hit_cooldown.keys()):
            self.hit_cooldown[enemy_id] -= 1
            if self.hit_cooldown[enemy_id] <= 0:
                del self.hit_cooldown[enemy_id]
        
        # 重绘
        self._draw_wall()
    
    def can_damage(self, enemy):
        """检查是否可以对敌人造成伤害"""
        enemy_id = id(enemy)
        if enemy_id in self.hit_cooldown:
            return False
        self.hit_cooldown[enemy_id] = 15  # 15帧冷却
        return True


class CraneBullet(pygame.sprite.Sprite):
    """纸鹤子弹 - 纸鹤发射的小型折纸镖"""
    
    def __init__(self, x, y, target_x, target_y, damage):
        super().__init__()
        self.damage = damage
        
        # 计算方向
        dx = target_x - x
        dy = target_y - y
        dist = max(1, math.hypot(dx, dy))
        self.speed = 8
        self.vx = (dx / dist) * self.speed
        self.vy = (dy / dist) * self.speed
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        # 动画
        self.frame = 0
        self.spin = 0
        
        # 创建图像
        self.size = 8
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self._draw()
        self.rect = self.image.get_rect(center=(x, y))
        
        self.lifetime = 120
    
    def _draw(self):
        """绘制迷你纸镖"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size, self.size
        
        # 虹彩
        hue = (self.frame * 8) % 360
        r = int(200 + 55 * math.sin(math.radians(hue)))
        g = int(200 + 55 * math.sin(math.radians(hue + 120)))
        b = int(200 + 55 * math.sin(math.radians(hue + 240)))
        
        # 小型四角星
        points = []
        for i in range(4):
            a = self.spin + i * 90
            px = cx + math.cos(math.radians(a)) * 6
            py = cy + math.sin(math.radians(a)) * 6
            points.append((px, py))
            a2 = self.spin + i * 90 + 45
            px2 = cx + math.cos(math.radians(a2)) * 3
            py2 = cy + math.sin(math.radians(a2)) * 3
            points.append((px2, py2))
        
        pygame.draw.polygon(self.image, (r, g, b), points)
    
    def update(self):
        self.frame += 1
        self.spin += 20
        
        self.float_x += self.vx
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        self._draw()
        
        self.lifetime -= 1
        if self.lifetime <= 0 or self.rect.bottom < -20 or self.rect.top > 820:
            self.kill()


# ==============================================================================
#   子弹预览渲染函数
# ==============================================================================

def render_origami_bullet(surface, effects, color, center_x, center_y, size, x, y):
    """
    渲染Origami子弹涂装预览效果 - 折纸飞镖特效
    
    Args:
        surface: pygame绘图表面
        effects: 效果列表
        color: 主题颜色
        center_x, center_y: 中心坐标
        size: 预览大小
        x, y: 左上角坐标
    
    Returns:
        bool: 如果渲染了效果返回True，否则False
    """
    t = pygame.time.get_ticks() / 1000.0
    
    # 检查是否是Origami子弹涂装
    origami_effects = [
        "origami_rainbow", "origami_golden", "origami_shadow",
        "origami_sakura", "origami_cyber", "origami_phoenix", "origami_ice"
    ]
    
    matched_effect = None
    for effect in origami_effects:
        if effect in effects:
            matched_effect = effect
            break
    
    if not matched_effect:
        return False
    
    # 根据效果类型绘制不同的预览
    blade_size = size // 3
    spin = t * 180  # 旋转动画
    
    if matched_effect == "origami_rainbow" or matched_effect == "origami_default":
        _draw_preview_default(surface, center_x, center_y, blade_size, spin, t)
    elif matched_effect == "origami_golden":
        _draw_preview_golden(surface, center_x, center_y, blade_size, spin, t)
    elif matched_effect == "origami_shadow":
        _draw_preview_shadow(surface, center_x, center_y, blade_size, spin, t)
    elif matched_effect == "origami_sakura":
        _draw_preview_sakura(surface, center_x, center_y, blade_size, spin, t)
    elif matched_effect == "origami_cyber":
        _draw_preview_cyber(surface, center_x, center_y, blade_size, spin, t)
    elif matched_effect == "origami_phoenix":
        _draw_preview_phoenix(surface, center_x, center_y, blade_size, spin, t)
    elif matched_effect == "origami_ice":
        _draw_preview_ice(surface, center_x, center_y, blade_size, spin, t)
    else:
        _draw_preview_default(surface, center_x, center_y, blade_size, spin, t)
    
    return True


def _draw_preview_default(surface, cx, cy, size, spin, t):
    """虹彩飞镖预览"""
    hue = (t * 180) % 360
    r = int(200 + 55 * math.sin(math.radians(hue)))
    g = int(200 + 55 * math.sin(math.radians(hue + 120)))
    b = int(200 + 55 * math.sin(math.radians(hue + 240)))
    
    # 四角星手里剑
    points = []
    for i in range(4):
        a = spin + i * 90
        px = cx + math.cos(math.radians(a)) * size
        py = cy + math.sin(math.radians(a)) * size
        points.append((px, py))
        a2 = spin + i * 90 + 45
        px2 = cx + math.cos(math.radians(a2)) * (size * 0.4)
        py2 = cy + math.sin(math.radians(a2)) * (size * 0.4)
        points.append((px2, py2))
    
    pygame.draw.polygon(surface, (r, g, b), points)
    pygame.draw.polygon(surface, (255, 255, 255), points, 2)
    
    # 中心光芒
    pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(cy)), size // 4)


def _draw_preview_golden(surface, cx, cy, size, spin, t):
    """金箔飞镖预览"""
    gold = (255, 215, 80)
    light_gold = (255, 240, 150)
    
    # 四角星
    points = []
    for i in range(4):
        a = spin + i * 90
        px = cx + math.cos(math.radians(a)) * size
        py = cy + math.sin(math.radians(a)) * size
        points.append((px, py))
        a2 = spin + i * 90 + 45
        px2 = cx + math.cos(math.radians(a2)) * (size * 0.4)
        py2 = cy + math.sin(math.radians(a2)) * (size * 0.4)
        points.append((px2, py2))
    
    pygame.draw.polygon(surface, gold, points)
    pygame.draw.polygon(surface, light_gold, points, 2)
    
    # 金色光泽
    shimmer = int(128 + 127 * math.sin(t * 3))
    for i in range(2):
        shine_angle = spin + i * 180
        sx = cx + math.cos(math.radians(shine_angle)) * (size * 0.5)
        sy = cy + math.sin(math.radians(shine_angle)) * (size * 0.5)
        pygame.draw.circle(surface, (255, 255, shimmer), (int(sx), int(sy)), 4)
    
    # 中心宝石
    pygame.draw.circle(surface, (255, 200, 100), (int(cx), int(cy)), size // 3)
    pygame.draw.circle(surface, (255, 255, 200), (int(cx) - 2, int(cy) - 2), size // 6)


def _draw_preview_shadow(surface, cx, cy, size, spin, t):
    """暗影刃预览"""
    purple = (80, 50, 120)
    light_purple = (150, 100, 200)
    
    # 残影层
    for i in range(3):
        shadow_alpha = 120 - i * 35
        offset = (i + 1) * 8
        shadow_pts = []
        for j in range(4):
            a = spin - offset * 2 + j * 90
            px = cx + math.cos(math.radians(a)) * (size - i * 2)
            py = cy + math.sin(math.radians(a)) * (size - i * 2)
            shadow_pts.append((px, py))
            a2 = spin - offset * 2 + j * 90 + 45
            px2 = cx + math.cos(math.radians(a2)) * ((size - i * 2) * 0.4)
            py2 = cy + math.sin(math.radians(a2)) * ((size - i * 2) * 0.4)
            shadow_pts.append((px2, py2))
        
        shadow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        pygame.draw.polygon(shadow_surf, (*purple, shadow_alpha), 
                           [(p[0] - cx + size * 2, p[1] - cy + size * 2) for p in shadow_pts])
        surface.blit(shadow_surf, (cx - size * 2, cy - size * 2))
    
    # 主体
    points = []
    for i in range(4):
        a = spin + i * 90
        px = cx + math.cos(math.radians(a)) * size
        py = cy + math.sin(math.radians(a)) * size
        points.append((px, py))
        a2 = spin + i * 90 + 45
        px2 = cx + math.cos(math.radians(a2)) * (size * 0.4)
        py2 = cy + math.sin(math.radians(a2)) * (size * 0.4)
        points.append((px2, py2))
    
    pygame.draw.polygon(surface, purple, points)
    pygame.draw.polygon(surface, light_purple, points, 1)
    
    # 脉冲核心
    pulse = int(100 + 55 * math.sin(t * 4))
    pygame.draw.circle(surface, (150, pulse, 255), (int(cx), int(cy)), size // 4)


def _draw_preview_sakura(surface, cx, cy, size, spin, t):
    """樱花镖预览"""
    pink = (255, 180, 200)
    light_pink = (255, 220, 230)
    
    # 5瓣花瓣形状
    for i in range(5):
        petal_angle = spin + i * 72
        rad = math.radians(petal_angle)
        
        tip_x = cx + math.cos(rad) * size
        tip_y = cy + math.sin(rad) * size
        
        side1_rad = math.radians(petal_angle - 25)
        side2_rad = math.radians(petal_angle + 25)
        s1x = cx + math.cos(side1_rad) * (size * 0.5)
        s1y = cy + math.sin(side1_rad) * (size * 0.5)
        s2x = cx + math.cos(side2_rad) * (size * 0.5)
        s2y = cy + math.sin(side2_rad) * (size * 0.5)
        
        petal = [(cx, cy), (s1x, s1y), (tip_x, tip_y), (s2x, s2y)]
        pygame.draw.polygon(surface, pink, petal)
        pygame.draw.polygon(surface, light_pink, petal, 1)
    
    # 花蕊
    pygame.draw.circle(surface, (255, 220, 100), (int(cx), int(cy)), size // 4)
    pygame.draw.circle(surface, (255, 255, 200), (int(cx), int(cy)), size // 6)


def _draw_preview_cyber(surface, cx, cy, size, spin, t):
    """数据碎片预览"""
    cyan = (0, 200, 255)
    light_cyan = (100, 255, 255)
    
    # 六边形
    hex_points = []
    for i in range(6):
        a = spin + i * 60
        px = cx + math.cos(math.radians(a)) * size
        py = cy + math.sin(math.radians(a)) * size
        hex_points.append((px, py))
    
    pygame.draw.polygon(surface, cyan, hex_points)
    pygame.draw.polygon(surface, light_cyan, hex_points, 2)
    
    # 内部数据线
    for i in range(3):
        a1 = spin + i * 60
        a2 = spin + (i + 3) * 60
        x1 = cx + math.cos(math.radians(a1)) * (size * 0.7)
        y1 = cy + math.sin(math.radians(a1)) * (size * 0.7)
        x2 = cx + math.cos(math.radians(a2)) * (size * 0.7)
        y2 = cy + math.sin(math.radians(a2)) * (size * 0.7)
        pygame.draw.line(surface, light_cyan, (x1, y1), (x2, y2), 1)
    
    # 闪烁的数据点
    frame = int(t * 20)
    for i in range(4):
        if (frame + i * 5) % 20 < 10:
            data_angle = spin + i * 90 + 45
            dx = cx + math.cos(math.radians(data_angle)) * (size * 0.5)
            dy = cy + math.sin(math.radians(data_angle)) * (size * 0.5)
            pygame.draw.circle(surface, (255, 255, 255), (int(dx), int(dy)), 3)


def _draw_preview_phoenix(surface, cx, cy, size, spin, t):
    """火羽镖预览"""
    orange = (255, 120, 30)
    yellow = (255, 200, 100)
    
    # 火焰主体
    flame_points = []
    for i in range(4):
        a = spin + i * 90
        flicker = 3 * math.sin(t * 8 + i * 1.5)
        px = cx + math.cos(math.radians(a)) * (size + flicker)
        py = cy + math.sin(math.radians(a)) * (size + flicker)
        flame_points.append((px, py))
        
        a2 = spin + i * 90 + 45
        px2 = cx + math.cos(math.radians(a2)) * (size * 0.3)
        py2 = cy + math.sin(math.radians(a2)) * (size * 0.3)
        flame_points.append((px2, py2))
    
    pygame.draw.polygon(surface, orange, flame_points)
    
    # 内焰
    inner_points = []
    for i in range(4):
        a = spin + i * 90
        px = cx + math.cos(math.radians(a)) * (size * 0.6)
        py = cy + math.sin(math.radians(a)) * (size * 0.6)
        inner_points.append((px, py))
        a2 = spin + i * 90 + 45
        px2 = cx + math.cos(math.radians(a2)) * (size * 0.25)
        py2 = cy + math.sin(math.radians(a2)) * (size * 0.25)
        inner_points.append((px2, py2))
    pygame.draw.polygon(surface, yellow, inner_points)
    
    # 火焰核心
    pygame.draw.circle(surface, (255, 255, 200), (int(cx), int(cy)), size // 4)
    
    # 火星
    for i in range(4):
        spark_a = spin + i * 90 + t * 200
        spark_d = size * 0.8 + (int(t * 10) + i * 3) % 5
        sx = cx + math.cos(math.radians(spark_a)) * spark_d
        sy = cy + math.sin(math.radians(spark_a)) * spark_d
        pygame.draw.circle(surface, (255, 200, 50), (int(sx), int(sy)), 2)


def _draw_preview_ice(surface, cx, cy, size, spin, t):
    """冰晶镖预览"""
    ice_blue = (180, 220, 255)
    white = (220, 240, 255)
    
    # 六角雪花主体
    for i in range(6):
        branch_angle = spin + i * 60
        rad = math.radians(branch_angle)
        
        # 主枝
        end_x = cx + math.cos(rad) * size
        end_y = cy + math.sin(rad) * size
        pygame.draw.line(surface, ice_blue, (cx, cy), (end_x, end_y), 3)
        
        # 侧枝
        for j in range(2):
            branch_dist = size * 0.4 + j * (size * 0.25)
            bx = cx + math.cos(rad) * branch_dist
            by = cy + math.sin(rad) * branch_dist
            
            for side in [-1, 1]:
                side_rad = math.radians(branch_angle + side * 60)
                side_len = size * 0.3 - j * (size * 0.1)
                sx = bx + math.cos(side_rad) * side_len
                sy = by + math.sin(side_rad) * side_len
                pygame.draw.line(surface, ice_blue, (bx, by), (sx, sy), 2)
    
    # 中心冰晶
    pygame.draw.circle(surface, white, (int(cx), int(cy)), size // 3)
    
    # 闪烁光点
    sparkle = int(200 + 55 * math.sin(t * 4))
    pygame.draw.circle(surface, (sparkle, sparkle, 255), (int(cx), int(cy)), size // 5)
