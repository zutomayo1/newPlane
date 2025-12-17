"""
亵渎天神·普罗维登斯 (Providence) 弹幕系统
原型：Terraria Calamity Mod - Providence, the Profaned Goddess
核心机制：神圣碎片(定点炸弹) + 亵渎之矛(无限穿透) + 茧化模式(静止治愈)
"""

import pygame
import math
import random
from config import WIDTH, HEIGHT, all_sprites, bullets, mobs, enemy_bullets

# ==================== 导入涂装主题 ====================
try:
    from utils.planes.skins_providence import get_providence_theme, PROVIDENCE_THEMES
except ImportError:
    PROVIDENCE_THEMES = {
        "default": {
            "name": "亵渎天神",
            "armor": (255, 215, 0),
            "crystal": (255, 105, 180),
            "core": (255, 200, 100),
            "flame": (255, 165, 0),
            "glow": (255, 223, 128),
            "border": (200, 150, 50),
        }
    }
    def get_providence_theme(style):
        return PROVIDENCE_THEMES.get(style, PROVIDENCE_THEMES["default"])


def get_theme(style):
    """获取涂装主题"""
    return get_providence_theme(style)


# ==================== 主武器：神圣碎片 ====================
class HolyShardBullet(pygame.sprite.Sprite):
    """
    神圣碎片 - 主武器
    发射后在目标位置悬停，延迟后爆炸造成范围伤害
    """
    
    def __init__(self, x, y, damage, angle=-90, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        # 不加入bullets组，避免主循环碰撞检测
        # 爆炸伤害在 _explode 中自己处理
        self.piercing = 0
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = angle
        self.speed = 12
        
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed
        
        self.frame = 0
        self.phase = "travel"  # travel -> hover -> explode
        self.travel_frames = 25  # 飞行时间
        self.hover_frames = 40  # 悬停时间
        self.explode_radius = 60  # 爆炸范围
        
        # 悬停位置
        self.hover_x = 0
        self.hover_y = 0
        
        self.size = 36
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        # 注意：不加入 bullets 组，主循环不检测碰撞
    
    def update(self):
        self.frame += 1
        
        if self.phase == "travel":
            # 飞行阶段
            self.float_x += self.vx
            self.float_y += self.vy
            
            if self.frame >= self.travel_frames:
                self.phase = "hover"
                self.hover_x = self.float_x
                self.hover_y = self.float_y
                self.frame = 0
        
        elif self.phase == "hover":
            # 悬停阶段 - 轻微浮动
            self.float_x = self.hover_x + 3 * math.sin(self.frame * 0.15)
            self.float_y = self.hover_y + 2 * math.cos(self.frame * 0.2)
            
            if self.frame >= self.hover_frames:
                self._explode()
                return
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 出界检测
        if self.float_y < -100 or self.float_y > HEIGHT + 100:
            self.kill()
            return
        
        self._render()
    
    def _explode(self):
        """爆炸处理 - 包含完整击杀逻辑"""
        from sprites import FloatingText, Particle, ExperienceOrb
        
        # 范围伤害 - 用list()复制避免迭代时修改
        for mob in list(mobs):
            dist = math.hypot(mob.rect.centerx - self.float_x,
                            mob.rect.centery - self.float_y)
            if dist <= self.explode_radius:
                # 距离越近伤害越高
                dmg_mult = 1.0 - (dist / self.explode_radius) * 0.5
                final_damage = int(self.damage * 1.5 * dmg_mult)
                mob.hp -= final_damage
                
                # 伤害数字
                FloatingText(mob.rect.centerx, mob.rect.top - 10, 
                           f"-{final_damage}", (255, 215, 0))
                
                # 命中特效
                Particle(mob.rect.center, (255, 200, 100))
                
                # 技能充能
                if self.owner and hasattr(self.owner, 'ult_charge'):
                    ult_charge_rate = getattr(self.owner, 'ult_charge_rate', 1.0)
                    ult_charge_gain = (final_damage / 10) * ult_charge_rate
                    self.owner.ult_charge = min(self.owner.max_ult_charge, self.owner.ult_charge + ult_charge_gain)
                    self.owner.ult2_charge = min(self.owner.max_ult2_charge, self.owner.ult2_charge + ult_charge_gain * 0.8)
                    self.owner.ult3_charge = min(self.owner.max_ult3_charge, self.owner.ult3_charge + ult_charge_gain * 0.6)
                
                # 死亡处理 - 完整逻辑
                if mob.hp <= 0:
                    # 分数
                    try:
                        import main
                        main.score += 100 if getattr(mob, 'is_elite', False) else 20
                    except:
                        pass
                    
                    # 击杀特效
                    for _ in range(5):
                        Particle(mob.rect.center, (0, 255, 255))
                    
                    # 经验球
                    xp = 15 if getattr(mob, 'is_elite', False) else 8
                    ExperienceOrb(mob.rect.centerx, mob.rect.centery, xp)
                    FloatingText(mob.rect.centerx, mob.rect.top - 30, f"经验+{xp}", (0, 255, 0))
                    
                    # 物品掉落
                    try:
                        import main
                        if main.item_manager:
                            main.item_manager.try_spawn_drop(mob.rect.centerx, mob.rect.centery)
                    except:
                        pass
                    
                    # 统计
                    if self.owner and hasattr(self.owner, 'stats'):
                        self.owner.stats['kills'] = self.owner.stats.get('kills', 0) + 1
                    
                    mob.kill()
        
        # 生成爆炸特效
        HolyExplosion(self.float_x, self.float_y, self.style)
        self.kill()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.15
        
        crystal = self.theme["crystal"]
        core = self.theme["core"]
        glow = self.theme["glow"]
        flame = self.theme["flame"]
        armor = self.theme["armor"]
        
        # ==================== 涂装专属渲染 ====================
        style = self.style
        
        if style == "providence_night":
            # 夜殿守护 - 月光碎片，新月形态
            # 外层月光晕
            pulse = 0.5 + 0.5 * math.sin(t * 3)
            for i in range(4):
                moon_alpha = int((90 - i * 20) * pulse)
                pygame.draw.circle(self.image, (*glow, moon_alpha), (cx, cy), 14 - i * 2)
            
            # 新月形状 - 用两个圆做差集效果
            moon_size = 10
            offset = 4
            pygame.draw.circle(self.image, crystal, (cx - offset // 2, cy), moon_size)
            pygame.draw.circle(self.image, (0, 0, 0, 0), (cx + offset, cy), moon_size - 2)
            
            # 星点装饰
            for i in range(5):
                star_angle = t * 2 + i * 1.26
                star_dist = 8 + 3 * math.sin(t + i)
                sx = cx + int(math.cos(star_angle) * star_dist)
                sy = cy + int(math.sin(star_angle) * star_dist)
                pygame.draw.circle(self.image, (255, 255, 255, 200), (sx, sy), 1)
            
            # 核心
            pygame.draw.circle(self.image, core, (cx - 2, cy), 4)
            
        elif style == "providence_abyss":
            # 深渊圣殿 - 水滴形深海晶体
            # 深海光晕 - 波动效果
            wave = math.sin(t * 2)
            for i in range(3):
                wave_r = int(12 + 4 * wave - i * 2)
                wave_alpha = 70 - i * 20
                if wave_r > 0:
                    pygame.draw.circle(self.image, (*glow, wave_alpha), (cx, cy), wave_r)
            
            # 水滴形主体
            drop_pts = [
                (cx, cy - 12),  # 顶点
                (cx + 7, cy + 2),
                (cx + 5, cy + 8),
                (cx, cy + 10),
                (cx - 5, cy + 8),
                (cx - 7, cy + 2),
            ]
            pygame.draw.polygon(self.image, crystal, drop_pts)
            pygame.draw.polygon(self.image, glow, drop_pts, 2)
            
            # 内部气泡
            bubble_y = cy - 3 + int(3 * math.sin(t * 4))
            pygame.draw.circle(self.image, (255, 255, 255, 150), (cx, bubble_y), 3)
            pygame.draw.circle(self.image, core, (cx, cy + 2), 4)
            
        elif style == "providence_crystal":
            # 棱镜女皇 - 多面体棱镜，彩虹折射
            # 棱镜光晕 - 彩虹效果
            for i in range(3):
                hue_shift = (t * 50 + i * 40) % 360
                rainbow = self._hsv_to_rgb(hue_shift, 0.5, 1.0)
                pygame.draw.circle(self.image, (*rainbow, 50 - i * 15), (cx, cy), 15 - i * 3)
            
            # 八面体形状
            size = 10
            rot = t * 0.5
            pts = []
            for i in range(8):
                angle = rot + i * 0.785
                r = size if i % 2 == 0 else size * 0.6
                pts.append((cx + int(math.cos(angle) * r), cy + int(math.sin(angle) * r)))
            pygame.draw.polygon(self.image, crystal, pts)
            
            # 棱镜内部折射线
            for i in range(4):
                angle = rot + i * 1.57
                lx = cx + int(math.cos(angle) * 6)
                ly = cy + int(math.sin(angle) * 6)
                pygame.draw.line(self.image, (255, 255, 255, 180), (cx, cy), (lx, ly), 1)
            
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 3)
            
        elif style == "providence_magma":
            # 熔岩神使 - 熔岩块，流动裂纹
            # 熔岩光晕
            pulse = 0.6 + 0.4 * math.sin(t * 5)
            for i in range(3):
                lava_alpha = int((100 - i * 30) * pulse)
                pygame.draw.circle(self.image, (*flame, lava_alpha), (cx, cy), 14 - i * 3)
            
            # 不规则熔岩块
            lava_pts = []
            for i in range(7):
                angle = i * 0.9 + t * 0.3
                r = 9 + 3 * math.sin(angle * 2 + t)
                lava_pts.append((cx + int(math.cos(angle) * r), cy + int(math.sin(angle) * r)))
            pygame.draw.polygon(self.image, crystal, lava_pts)
            
            # 表面裂纹 - 发光
            for i in range(3):
                crack_angle = t * 0.5 + i * 2.1
                c1x = cx + int(math.cos(crack_angle) * 2)
                c1y = cy + int(math.sin(crack_angle) * 2)
                c2x = cx + int(math.cos(crack_angle) * 8)
                c2y = cy + int(math.sin(crack_angle) * 8)
                pygame.draw.line(self.image, (255, 255, 200, 220), (c1x, c1y), (c2x, c2y), 2)
            
            # 白热核心
            pygame.draw.circle(self.image, core, (cx, cy), 5)
            pygame.draw.circle(self.image, (255, 255, 220), (cx, cy), 3)
            
        elif style == "providence_frost":
            # 永冻圣典 - 雪花晶体
            # 冰霜光晕
            frost_pulse = 0.7 + 0.3 * math.sin(t * 2)
            for i in range(3):
                frost_alpha = int((80 - i * 25) * frost_pulse)
                pygame.draw.circle(self.image, (*glow, frost_alpha), (cx, cy), 14 - i * 3)
            
            # 六瓣雪花
            for i in range(6):
                angle = i * 1.047 + t * 0.2
                # 主枝
                ex = cx + int(math.cos(angle) * 10)
                ey = cy + int(math.sin(angle) * 10)
                pygame.draw.line(self.image, crystal, (cx, cy), (ex, ey), 2)
                # 侧枝
                for side in [-0.5, 0.5]:
                    bx = cx + int(math.cos(angle) * 6)
                    by = cy + int(math.sin(angle) * 6)
                    branch_angle = angle + side
                    bbx = bx + int(math.cos(branch_angle) * 4)
                    bby = by + int(math.sin(branch_angle) * 4)
                    pygame.draw.line(self.image, glow, (bx, by), (bbx, bby), 1)
            
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 3)
            
        elif style == "providence_void":
            # 虚空审判 - 虚空裂隙
            # 虚空扭曲光晕
            void_pulse = 0.5 + 0.5 * math.sin(t * 4)
            for i in range(4):
                void_alpha = int((100 - i * 20) * void_pulse)
                pygame.draw.circle(self.image, (*glow, void_alpha), (cx, cy), 15 - i * 2)
            
            # 扭曲的菱形 - 呼吸效果
            size = 8 + 2 * math.sin(t * 3)
            rot = t * 0.8
            pts = [
                (cx, cy - int(size * 1.3)),
                (cx + int(size * 0.8), cy),
                (cx, cy + int(size * 1.3)),
                (cx - int(size * 0.8), cy)
            ]
            pygame.draw.polygon(self.image, crystal, pts)
            
            # 虚空裂缝
            for i in range(4):
                crack_angle = rot + i * 1.57
                c_len = 6 + 2 * math.sin(t * 2 + i)
                c1x = cx + int(math.cos(crack_angle) * 2)
                c1y = cy + int(math.sin(crack_angle) * 2)
                c2x = cx + int(math.cos(crack_angle) * c_len)
                c2y = cy + int(math.sin(crack_angle) * c_len)
                pygame.draw.line(self.image, (*core, 200), (c1x, c1y), (c2x, c2y), 1)
            
            pygame.draw.circle(self.image, core, (cx, cy), 4)
            pygame.draw.circle(self.image, (0, 0, 0), (cx, cy), 2)  # 虚空黑心
            
        elif style == "providence_nature":
            # 丛林神殿 - 叶形晶体
            # 自然光晕
            for i in range(3):
                nature_alpha = 60 - i * 18
                pygame.draw.circle(self.image, (*glow, nature_alpha), (cx, cy), 13 - i * 3)
            
            # 叶片形状
            leaf_pts = [
                (cx, cy - 11),
                (cx + 5, cy - 5),
                (cx + 7, cy + 2),
                (cx + 4, cy + 8),
                (cx, cy + 10),
                (cx - 4, cy + 8),
                (cx - 7, cy + 2),
                (cx - 5, cy - 5),
            ]
            pygame.draw.polygon(self.image, crystal, leaf_pts)
            pygame.draw.polygon(self.image, glow, leaf_pts, 1)
            
            # 叶脉
            pygame.draw.line(self.image, (*armor, 180), (cx, cy - 8), (cx, cy + 7), 1)
            for i in range(3):
                vy = cy - 4 + i * 4
                pygame.draw.line(self.image, (*armor, 150), (cx, vy), (cx + 4, vy + 2), 1)
                pygame.draw.line(self.image, (*armor, 150), (cx, vy), (cx - 4, vy + 2), 1)
            
            pygame.draw.circle(self.image, core, (cx, cy - 3), 3)
            
        elif style == "providence_storm":
            # 雷霆圣裁 - 雷电球
            # 电弧光晕
            spark = 0.3 + 0.7 * random.random()
            for i in range(3):
                storm_alpha = int((100 - i * 30) * spark)
                pygame.draw.circle(self.image, (*glow, storm_alpha), (cx, cy), 14 - i * 3)
            
            # 核心球
            pygame.draw.circle(self.image, crystal, (cx, cy), 8)
            
            # 电弧
            for i in range(4):
                arc_angle = t * 3 + i * 1.57
                arc_pts = [(cx, cy)]
                for j in range(4):
                    dist = (j + 1) * 3
                    jitter_x = random.randint(-2, 2)
                    jitter_y = random.randint(-2, 2)
                    ax = cx + int(math.cos(arc_angle) * dist) + jitter_x
                    ay = cy + int(math.sin(arc_angle) * dist) + jitter_y
                    arc_pts.append((ax, ay))
                if len(arc_pts) > 1:
                    pygame.draw.lines(self.image, (255, 255, 255, 220), False, arc_pts, 1)
            
            pygame.draw.circle(self.image, core, (cx, cy), 5)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 2)
            
        elif style == "providence_blood":
            # 血月祭司 - 血滴晶体
            # 血光晕
            blood_pulse = 0.6 + 0.4 * math.sin(t * 4)
            for i in range(3):
                blood_alpha = int((90 - i * 25) * blood_pulse)
                pygame.draw.circle(self.image, (*glow, blood_alpha), (cx, cy), 13 - i * 3)
            
            # 血滴形状
            drop_size = 9 + int(2 * math.sin(t * 3))
            drop_pts = [
                (cx, cy - drop_size),
                (cx + int(drop_size * 0.7), cy),
                (cx + int(drop_size * 0.5), cy + int(drop_size * 0.6)),
                (cx, cy + int(drop_size * 0.8)),
                (cx - int(drop_size * 0.5), cy + int(drop_size * 0.6)),
                (cx - int(drop_size * 0.7), cy),
            ]
            pygame.draw.polygon(self.image, crystal, drop_pts)
            pygame.draw.polygon(self.image, glow, drop_pts, 1)
            
            # 血丝纹理
            for i in range(3):
                vein_y = cy - 5 + i * 4
                vein_len = 3 + i
                pygame.draw.line(self.image, (*flame, 180), (cx - vein_len, vein_y), (cx + vein_len, vein_y), 1)
            
            pygame.draw.circle(self.image, core, (cx, cy), 4)
            
        elif style == "providence_gold":
            # 皇金审判 - 皇冠晶体
            # 金光晕
            gold_pulse = 0.7 + 0.3 * math.sin(t * 2.5)
            for i in range(4):
                gold_alpha = int((100 - i * 22) * gold_pulse)
                pygame.draw.circle(self.image, (*glow, gold_alpha), (cx, cy), 15 - i * 2)
            
            # 皇冠形状
            crown_pts = [
                (cx - 8, cy + 5),
                (cx - 8, cy),
                (cx - 5, cy - 3),
                (cx - 3, cy - 8),
                (cx, cy - 4),
                (cx + 3, cy - 8),
                (cx + 5, cy - 3),
                (cx + 8, cy),
                (cx + 8, cy + 5),
            ]
            pygame.draw.polygon(self.image, crystal, crown_pts)
            pygame.draw.polygon(self.image, armor, crown_pts, 2)
            
            # 顶部宝石
            for i, gem_x in enumerate([cx - 3, cx, cx + 3]):
                gem_color = [(255, 100, 100), (100, 255, 100), (100, 100, 255)][i]
                pygame.draw.circle(self.image, gem_color, (gem_x, cy - 8 if i == 1 else cy - 3), 2)
            
            pygame.draw.circle(self.image, core, (cx, cy + 1), 3)
            
        elif style == "providence_aurora":
            # 极光圣典 - 流动极光
            # 极光光晕 - 多色流动
            for i in range(4):
                hue = (t * 30 + i * 60) % 360
                aurora_color = self._hsv_to_rgb(hue, 0.6, 0.9)
                aurora_alpha = 70 - i * 15
                pygame.draw.circle(self.image, (*aurora_color, aurora_alpha), (cx, cy + i - 2), 14 - i * 2)
            
            # 流动菱形
            size = 9 + 2 * math.sin(t * 2)
            hue_main = (t * 40) % 360
            main_color = self._hsv_to_rgb(hue_main, 0.5, 1.0)
            
            pts = [
                (cx, cy - int(size * 1.2)),
                (cx + int(size * 0.7), cy),
                (cx, cy + int(size * 1.2)),
                (cx - int(size * 0.7), cy)
            ]
            pygame.draw.polygon(self.image, main_color, pts)
            pygame.draw.polygon(self.image, glow, pts, 2)
            
            # 内部光波
            for i in range(3):
                wave_y = cy - 4 + i * 4
                wave_color = self._hsv_to_rgb((hue_main + i * 40) % 360, 0.4, 1.0)
                pygame.draw.line(self.image, (*wave_color, 180), (cx - 4, wave_y), (cx + 4, wave_y), 1)
            
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 3)
            
        else:
            # 默认涂装 - 经典神圣碎片
            # 光晕
            if self.phase == "hover":
                pulse = 0.5 + 0.5 * math.sin(t * 4)
                glow_r = int(14 + 4 * pulse)
                for i in range(3):
                    r = glow_r - i * 3
                    a = max(0, 80 - i * 25)
                    if r > 0:
                        pygame.draw.circle(self.image, (*glow, a), (cx, cy), r)
            
            # 菱形晶体
            size_mult = 1.0 if self.phase == "travel" else 1.0 + 0.2 * math.sin(t * 5)
            pts = [
                (cx, cy - int(10 * size_mult)),
                (cx + int(6 * size_mult), cy),
                (cx, cy + int(10 * size_mult)),
                (cx - int(6 * size_mult), cy)
            ]
            pygame.draw.polygon(self.image, crystal, pts)
            pygame.draw.polygon(self.image, glow, pts, 2)
            
            # 核心
            pygame.draw.circle(self.image, core, (cx, cy), 4)
            pygame.draw.circle(self.image, (255, 255, 220), (cx, cy), 2)
    
    def _hsv_to_rgb(self, h, s, v):
        """HSV转RGB辅助函数"""
        h = h / 360.0
        if s == 0.0:
            return (int(v * 255), int(v * 255), int(v * 255))
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        if i == 0: return (int(v * 255), int(t * 255), int(p * 255))
        if i == 1: return (int(q * 255), int(v * 255), int(p * 255))
        if i == 2: return (int(p * 255), int(v * 255), int(t * 255))
        if i == 3: return (int(p * 255), int(q * 255), int(v * 255))
        if i == 4: return (int(t * 255), int(p * 255), int(v * 255))
        return (int(v * 255), int(p * 255), int(q * 255))


# ==================== 神圣爆炸特效 ====================
class HolyExplosion(pygame.sprite.Sprite):
    """神圣碎片爆炸特效"""
    
    def __init__(self, x, y, style="default"):
        super().__init__()
        self.float_x = float(x)
        self.float_y = float(y)
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.lifetime = 20
        
        self.size = 120
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        if self.frame > self.lifetime:
            self.kill()
            return
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        
        progress = self.frame / self.lifetime
        
        crystal = self.theme["crystal"]
        glow = self.theme["glow"]
        core = self.theme["core"]
        
        # 扩散光环
        max_r = 50
        r = int(max_r * progress)
        alpha = int(200 * (1 - progress))
        if r > 0 and alpha > 0:
            pygame.draw.circle(self.image, (*glow, alpha), (cx, cy), r, 3)
        
        # 内层爆炸
        inner_r = int(30 * (0.5 + 0.5 * progress))
        inner_a = int(150 * (1 - progress))
        if inner_r > 0 and inner_a > 0:
            pygame.draw.circle(self.image, (*crystal, inner_a), (cx, cy), inner_r)
        
        # 碎片飞散
        for i in range(8):
            angle = i * 0.785 + progress * 2
            dist = 10 + 35 * progress
            px = cx + int(math.cos(angle) * dist)
            py = cy + int(math.sin(angle) * dist)
            size = int(4 * (1 - progress))
            if size > 0:
                pygame.draw.circle(self.image, (*core, int(200 * (1 - progress))), (px, py), size)


# ==================== 副武器：亵渎之矛 ====================
class ProfanedSpearBullet(pygame.sprite.Sprite):
    """
    亵渎之矛 - 副武器
    无限穿透的能量矛，命中敌人不消失
    """
    
    def __init__(self, x, y, damage, angle=-90, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        # 高穿透值，让主循环正常处理碰撞
        self.piercing = 999
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = angle
        self.speed = 16
        
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed
        
        self.frame = 0
        self.lifetime = 120
        self.hit_enemies = set()  # 已命中的敌人（用于防止同一敌人重复伤害）
        self.hit_cooldown = {}  # 命中冷却
        
        # 拖尾
        self.trail = []
        self.max_trail = 12
        
        self.size = 50
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        
        # 移动
        self.float_x += self.vx
        self.float_y += self.vy
        
        # 添加拖尾
        if self.frame % 2 == 0:
            self.trail.append({'x': self.float_x, 'y': self.float_y, 'alpha': 255})
            if len(self.trail) > self.max_trail:
                self.trail.pop(0)
        
        # 更新拖尾
        for t in self.trail:
            t['alpha'] = max(0, t['alpha'] - 20)
        
        # 更新冷却
        for enemy_id in list(self.hit_cooldown.keys()):
            self.hit_cooldown[enemy_id] -= 1
            if self.hit_cooldown[enemy_id] <= 0:
                del self.hit_cooldown[enemy_id]
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 出界
        if (self.float_y < -100 or self.float_y > HEIGHT + 100 or
            self.float_x < -100 or self.float_x > WIDTH + 100 or
            self.frame > self.lifetime):
            self.kill()
            return
        
        # 主循环会处理碰撞，这里只渲染
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.2
        
        flame = self.theme["flame"]
        crystal = self.theme["crystal"]
        core = self.theme["core"]
        glow = self.theme["glow"]
        armor = self.theme["armor"]
        
        # 计算方向
        dir_x = self.vx / self.speed if self.speed > 0 else 0
        dir_y = self.vy / self.speed if self.speed > 0 else -1
        perp_x = -dir_y
        perp_y = dir_x
        
        style = self.style
        
        # ==================== 涂装专属渲染 ====================
        if style == "providence_night":
            # 夜殿守护 - 月光镰刀
            # 拖尾 - 星光轨迹
            for i, tr in enumerate(self.trail):
                if tr['alpha'] > 0:
                    tx = int(tr['x'] - self.float_x + cx)
                    ty = int(tr['y'] - self.float_y + cy)
                    if 0 < tx < self.size and 0 < ty < self.size:
                        pygame.draw.circle(self.image, (*glow, int(tr['alpha'] * 0.6)), (tx, ty), 4 - i // 3)
                        if i % 3 == 0:
                            pygame.draw.circle(self.image, (255, 255, 255, tr['alpha'] // 2), (tx, ty), 1)
            
            # 弯月刃形状
            spear_len = 16
            curve_pts = [
                (cx + int(dir_x * spear_len), cy + int(dir_y * spear_len)),  # 尖端
                (cx + int(perp_x * 10) + int(dir_x * 5), cy + int(perp_y * 10) + int(dir_y * 5)),
                (cx + int(perp_x * 8) - int(dir_x * 8), cy + int(perp_y * 8) - int(dir_y * 8)),
                (cx - int(dir_x * 5), cy - int(dir_y * 5)),
                (cx - int(perp_x * 8) - int(dir_x * 8), cy - int(perp_y * 8) - int(dir_y * 8)),
                (cx - int(perp_x * 10) + int(dir_x * 5), cy - int(perp_y * 10) + int(dir_y * 5)),
            ]
            pygame.draw.polygon(self.image, crystal, curve_pts)
            pygame.draw.polygon(self.image, glow, curve_pts, 2)
            pygame.draw.circle(self.image, core, (cx, cy), 4)
            
        elif style == "providence_abyss":
            # 深渊圣殿 - 鱼叉
            # 拖尾 - 气泡效果
            for i, tr in enumerate(self.trail):
                if tr['alpha'] > 0:
                    tx = int(tr['x'] - self.float_x + cx)
                    ty = int(tr['y'] - self.float_y + cy)
                    if 0 < tx < self.size and 0 < ty < self.size:
                        bubble_r = 4 - i // 4
                        if bubble_r > 0:
                            pygame.draw.circle(self.image, (*glow, int(tr['alpha'] * 0.4)), (tx, ty), bubble_r)
                            pygame.draw.circle(self.image, (*glow, int(tr['alpha'] * 0.6)), (tx, ty), bubble_r, 1)
            
            # 三叉戟形状
            spear_len = 16
            prong_spread = 6
            # 中叉
            pygame.draw.line(self.image, crystal, (cx, cy), 
                           (cx + int(dir_x * spear_len), cy + int(dir_y * spear_len)), 3)
            # 左右叉
            for side in [-1, 1]:
                px = cx + int(perp_x * prong_spread * side) + int(dir_x * 3)
                py = cy + int(perp_y * prong_spread * side) + int(dir_y * 3)
                ex = px + int(dir_x * (spear_len - 5))
                ey = py + int(dir_y * (spear_len - 5))
                pygame.draw.line(self.image, crystal, (px, py), (ex, ey), 2)
            
            pygame.draw.polygon(self.image, glow, [
                (cx + int(dir_x * spear_len), cy + int(dir_y * spear_len)),
                (cx + int(perp_x * 4), cy + int(perp_y * 4)),
                (cx - int(perp_x * 4), cy - int(perp_y * 4)),
            ], 1)
            pygame.draw.circle(self.image, core, (cx - int(dir_x * 5), cy - int(dir_y * 5)), 4)
            
        elif style == "providence_crystal":
            # 棱镜女皇 - 棱镜箭
            # 拖尾 - 彩虹光带
            for i, tr in enumerate(self.trail):
                if tr['alpha'] > 0:
                    tx = int(tr['x'] - self.float_x + cx)
                    ty = int(tr['y'] - self.float_y + cy)
                    if 0 < tx < self.size and 0 < ty < self.size:
                        hue = (t * 60 + i * 30) % 360
                        rainbow = self._hsv_to_rgb(hue, 0.6, 1.0)
                        pygame.draw.circle(self.image, (*rainbow, int(tr['alpha'] * 0.7)), (tx, ty), 4 - i // 4)
            
            # 多面体箭头
            spear_len = 18
            pts = [
                (cx + int(dir_x * spear_len), cy + int(dir_y * spear_len)),
                (cx + int(perp_x * 7), cy + int(perp_y * 7)),
                (cx + int(perp_x * 3) - int(dir_x * 10), cy + int(perp_y * 3) - int(dir_y * 10)),
                (cx - int(perp_x * 3) - int(dir_x * 10), cy - int(perp_y * 3) - int(dir_y * 10)),
                (cx - int(perp_x * 7), cy - int(perp_y * 7)),
            ]
            hue_main = (t * 40) % 360
            main_color = self._hsv_to_rgb(hue_main, 0.4, 1.0)
            pygame.draw.polygon(self.image, main_color, pts)
            pygame.draw.polygon(self.image, (255, 255, 255), pts, 2)
            
            # 内部折射
            pygame.draw.line(self.image, (255, 255, 255, 200), (cx, cy), 
                           (cx + int(dir_x * 10), cy + int(dir_y * 10)), 1)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 3)
            
        elif style == "providence_magma":
            # 熔岩神使 - 熔岩矛
            # 拖尾 - 熔岩流
            for i, tr in enumerate(self.trail):
                if tr['alpha'] > 0:
                    tx = int(tr['x'] - self.float_x + cx)
                    ty = int(tr['y'] - self.float_y + cy)
                    if 0 < tx < self.size and 0 < ty < self.size:
                        r = 6 - i * 0.4
                        if r > 0:
                            pygame.draw.circle(self.image, (*flame, tr['alpha']), (tx, ty), int(r))
                            if i < 4:
                                pygame.draw.circle(self.image, (255, 200, 100, tr['alpha'] // 2), (tx, ty), int(r * 0.6))
            
            # 熔岩矛头 - 不规则边缘
            spear_len = 18
            pts = [
                (cx + int(dir_x * spear_len), cy + int(dir_y * spear_len)),
                (cx + int(perp_x * 9) + int(dir_x * 2), cy + int(perp_y * 9) + int(dir_y * 2)),
                (cx + int(perp_x * 6) - int(dir_x * 6), cy + int(perp_y * 6) - int(dir_y * 6)),
                (cx - int(perp_x * 6) - int(dir_x * 6), cy - int(perp_y * 6) - int(dir_y * 6)),
                (cx - int(perp_x * 9) + int(dir_x * 2), cy - int(perp_y * 9) + int(dir_y * 2)),
            ]
            pygame.draw.polygon(self.image, crystal, pts)
            # 熔岩裂纹
            pygame.draw.line(self.image, (255, 255, 200), (cx, cy), 
                           (cx + int(dir_x * 12), cy + int(dir_y * 12)), 2)
            pygame.draw.circle(self.image, core, (cx, cy), 5)
            pygame.draw.circle(self.image, (255, 255, 220), (cx, cy), 3)
            
        elif style == "providence_frost":
            # 永冻圣典 - 冰锥
            # 拖尾 - 冰晶碎片
            for i, tr in enumerate(self.trail):
                if tr['alpha'] > 0:
                    tx = int(tr['x'] - self.float_x + cx)
                    ty = int(tr['y'] - self.float_y + cy)
                    if 0 < tx < self.size and 0 < ty < self.size:
                        ice_size = 3 - i // 4
                        if ice_size > 0:
                            pygame.draw.rect(self.image, (*glow, int(tr['alpha'] * 0.5)), 
                                           (tx - ice_size, ty - ice_size, ice_size * 2, ice_size * 2))
            
            # 冰锥形状 - 六边形截面
            spear_len = 20
            hex_size = 6
            tip_x = cx + int(dir_x * spear_len)
            tip_y = cy + int(dir_y * spear_len)
            
            # 六棱冰锥
            for i in range(6):
                angle = i * 1.047 + t * 0.1
                hx = cx + int(math.cos(angle) * hex_size * abs(perp_x + 0.5))
                hy = cy + int(math.sin(angle) * hex_size * abs(perp_y + 0.5))
                pygame.draw.polygon(self.image, crystal, [(tip_x, tip_y), (hx, hy), (cx, cy)])
            
            pygame.draw.circle(self.image, glow, (cx, cy), 4)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 2)
            
        elif style == "providence_void":
            # 虚空审判 - 虚空刺
            # 拖尾 - 虚空裂隙
            for i, tr in enumerate(self.trail):
                if tr['alpha'] > 0:
                    tx = int(tr['x'] - self.float_x + cx)
                    ty = int(tr['y'] - self.float_y + cy)
                    if 0 < tx < self.size and 0 < ty < self.size:
                        void_pulse = 0.5 + 0.5 * math.sin(t * 3 + i)
                        pygame.draw.circle(self.image, (*glow, int(tr['alpha'] * 0.4 * void_pulse)), 
                                         (tx, ty), 5 - i // 3)
            
            # 虚空刺 - 扭曲形态
            spear_len = 18
            distort = 2 * math.sin(t * 4)
            pts = [
                (cx + int(dir_x * spear_len), cy + int(dir_y * spear_len)),
                (cx + int(perp_x * (7 + distort)), cy + int(perp_y * (7 + distort))),
                (cx - int(dir_x * 8), cy - int(dir_y * 8)),
                (cx - int(perp_x * (7 - distort)), cy - int(perp_y * (7 - distort))),
            ]
            pygame.draw.polygon(self.image, crystal, pts)
            pygame.draw.polygon(self.image, glow, pts, 2)
            pygame.draw.circle(self.image, core, (cx, cy), 4)
            pygame.draw.circle(self.image, (0, 0, 0), (cx, cy), 2)
            
        elif style == "providence_nature":
            # 丛林神殿 - 荆棘矛
            # 拖尾 - 叶片
            for i, tr in enumerate(self.trail):
                if tr['alpha'] > 0:
                    tx = int(tr['x'] - self.float_x + cx)
                    ty = int(tr['y'] - self.float_y + cy)
                    if 0 < tx < self.size and 0 < ty < self.size:
                        leaf_angle = t * 2 + i * 0.5
                        leaf_size = 3 - i // 4
                        if leaf_size > 0:
                            lx = tx + int(math.cos(leaf_angle) * leaf_size)
                            ly = ty + int(math.sin(leaf_angle) * leaf_size)
                            pygame.draw.line(self.image, (*glow, int(tr['alpha'] * 0.6)), (tx, ty), (lx, ly), 1)
            
            # 荆棘矛 - 带刺
            spear_len = 18
            pts = [
                (cx + int(dir_x * spear_len), cy + int(dir_y * spear_len)),
                (cx + int(perp_x * 6), cy + int(perp_y * 6)),
                (cx - int(dir_x * 6), cy - int(dir_y * 6)),
                (cx - int(perp_x * 6), cy - int(perp_y * 6)),
            ]
            pygame.draw.polygon(self.image, crystal, pts)
            
            # 荆刺
            for i in range(3):
                thorn_pos = 0.3 + i * 0.25
                for side in [-1, 1]:
                    bx = cx + int(dir_x * spear_len * thorn_pos)
                    by = cy + int(dir_y * spear_len * thorn_pos)
                    tx = bx + int(perp_x * 5 * side) + int(dir_x * -3)
                    ty = by + int(perp_y * 5 * side) + int(dir_y * -3)
                    pygame.draw.line(self.image, armor, (bx, by), (tx, ty), 2)
            
            pygame.draw.circle(self.image, core, (cx - int(dir_x * 3), cy - int(dir_y * 3)), 4)
            
        elif style == "providence_storm":
            # 雷霆圣裁 - 雷电枪
            # 拖尾 - 电弧
            for i, tr in enumerate(self.trail):
                if tr['alpha'] > 0:
                    tx = int(tr['x'] - self.float_x + cx)
                    ty = int(tr['y'] - self.float_y + cy)
                    if 0 < tx < self.size and 0 < ty < self.size:
                        jitter_x = random.randint(-2, 2)
                        jitter_y = random.randint(-2, 2)
                        pygame.draw.circle(self.image, (*glow, int(tr['alpha'] * 0.8)), 
                                         (tx + jitter_x, ty + jitter_y), 3)
            
            # 雷电枪头
            spear_len = 18
            pts = [
                (cx + int(dir_x * spear_len), cy + int(dir_y * spear_len)),
                (cx + int(perp_x * 8), cy + int(perp_y * 8)),
                (cx - int(dir_x * 5), cy - int(dir_y * 5)),
                (cx - int(perp_x * 8), cy - int(perp_y * 8)),
            ]
            pygame.draw.polygon(self.image, crystal, pts)
            pygame.draw.polygon(self.image, (255, 255, 255), pts, 2)
            
            # 电弧闪烁
            for _ in range(2):
                arc_x = cx + random.randint(-8, 8)
                arc_y = cy + random.randint(-8, 8)
                pygame.draw.circle(self.image, (255, 255, 255, 200), (arc_x, arc_y), 1)
            
            pygame.draw.circle(self.image, core, (cx, cy), 5)
            
        elif style == "providence_blood":
            # 血月祭司 - 血刃
            # 拖尾 - 血滴
            for i, tr in enumerate(self.trail):
                if tr['alpha'] > 0:
                    tx = int(tr['x'] - self.float_x + cx)
                    ty = int(tr['y'] - self.float_y + cy)
                    if 0 < tx < self.size and 0 < ty < self.size:
                        drip = i * 0.3
                        pygame.draw.circle(self.image, (*flame, int(tr['alpha'] * 0.7)), 
                                         (tx, ty + int(drip)), 4 - i // 3)
            
            # 血刃 - 曲刃
            spear_len = 18
            curve_offset = 3 * math.sin(t * 2)
            pts = [
                (cx + int(dir_x * spear_len), cy + int(dir_y * spear_len)),
                (cx + int(perp_x * (8 + curve_offset)) + int(dir_x * 4), 
                 cy + int(perp_y * (8 + curve_offset)) + int(dir_y * 4)),
                (cx + int(perp_x * 4) - int(dir_x * 6), cy + int(perp_y * 4) - int(dir_y * 6)),
                (cx - int(perp_x * 4) - int(dir_x * 6), cy - int(perp_y * 4) - int(dir_y * 6)),
                (cx - int(perp_x * (8 - curve_offset)) + int(dir_x * 4), 
                 cy - int(perp_y * (8 - curve_offset)) + int(dir_y * 4)),
            ]
            pygame.draw.polygon(self.image, crystal, pts)
            pygame.draw.polygon(self.image, glow, pts, 2)
            pygame.draw.circle(self.image, core, (cx, cy), 4)
            
        elif style == "providence_gold":
            # 皇金审判 - 皇金枪
            # 拖尾 - 金光
            for i, tr in enumerate(self.trail):
                if tr['alpha'] > 0:
                    tx = int(tr['x'] - self.float_x + cx)
                    ty = int(tr['y'] - self.float_y + cy)
                    if 0 < tx < self.size and 0 < ty < self.size:
                        pygame.draw.circle(self.image, (*glow, int(tr['alpha'] * 0.6)), (tx, ty), 5 - i // 3)
            
            # 皇金枪头 - 华丽形状
            spear_len = 20
            pts = [
                (cx + int(dir_x * spear_len), cy + int(dir_y * spear_len)),
                (cx + int(perp_x * 5) + int(dir_x * 12), cy + int(perp_y * 5) + int(dir_y * 12)),
                (cx + int(perp_x * 10), cy + int(perp_y * 10)),
                (cx + int(perp_x * 4) - int(dir_x * 5), cy + int(perp_y * 4) - int(dir_y * 5)),
                (cx - int(perp_x * 4) - int(dir_x * 5), cy - int(perp_y * 4) - int(dir_y * 5)),
                (cx - int(perp_x * 10), cy - int(perp_y * 10)),
                (cx - int(perp_x * 5) + int(dir_x * 12), cy - int(perp_y * 5) + int(dir_y * 12)),
            ]
            pygame.draw.polygon(self.image, crystal, pts)
            pygame.draw.polygon(self.image, armor, pts, 2)
            
            # 中心宝石
            pygame.draw.circle(self.image, (255, 100, 100), (cx + int(dir_x * 5), cy + int(dir_y * 5)), 3)
            pygame.draw.circle(self.image, core, (cx - int(dir_x * 3), cy - int(dir_y * 3)), 4)
            
        elif style == "providence_aurora":
            # 极光圣典 - 极光箭
            # 拖尾 - 极光带
            for i, tr in enumerate(self.trail):
                if tr['alpha'] > 0:
                    tx = int(tr['x'] - self.float_x + cx)
                    ty = int(tr['y'] - self.float_y + cy)
                    if 0 < tx < self.size and 0 < ty < self.size:
                        hue = (t * 50 + i * 25) % 360
                        aurora = self._hsv_to_rgb(hue, 0.5, 0.9)
                        pygame.draw.circle(self.image, (*aurora, int(tr['alpha'] * 0.6)), (tx, ty), 4 - i // 4)
            
            # 极光箭头
            spear_len = 18
            hue_main = (t * 30) % 360
            main_color = self._hsv_to_rgb(hue_main, 0.5, 1.0)
            
            pts = [
                (cx + int(dir_x * spear_len), cy + int(dir_y * spear_len)),
                (cx + int(perp_x * 8), cy + int(perp_y * 8)),
                (cx - int(dir_x * 6), cy - int(dir_y * 6)),
                (cx - int(perp_x * 8), cy - int(perp_y * 8)),
            ]
            pygame.draw.polygon(self.image, main_color, pts)
            pygame.draw.polygon(self.image, glow, pts, 2)
            
            # 极光波纹
            for i in range(3):
                wave_offset = i * 4
                wave_hue = (hue_main + i * 40) % 360
                wave_color = self._hsv_to_rgb(wave_hue, 0.4, 1.0)
                wx = cx + int(dir_x * wave_offset)
                wy = cy + int(dir_y * wave_offset)
                pygame.draw.circle(self.image, (*wave_color, 150), (wx, wy), 2)
            
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 3)
            
        else:
            # 默认涂装
            # 绘制拖尾
            for i, tr in enumerate(self.trail):
                if tr['alpha'] > 0:
                    tx = int(tr['x'] - self.float_x + cx)
                    ty = int(tr['y'] - self.float_y + cy)
                    r = 5 - i * 0.3
                    if 0 < tx < self.size and 0 < ty < self.size and r > 0:
                        pygame.draw.circle(self.image, (*flame, tr['alpha']), (tx, ty), int(r))
            
            # 矛头 - 三角形
            spear_len = 18
            spear_width = 8
            tip_x = cx + int(dir_x * spear_len)
            tip_y = cy + int(dir_y * spear_len)
            
            pts = [
                (tip_x, tip_y),
                (cx + int(perp_x * spear_width) - int(dir_x * 5), 
                 cy + int(perp_y * spear_width) - int(dir_y * 5)),
                (cx - int(perp_x * spear_width) - int(dir_x * 5), 
                 cy - int(perp_y * spear_width) - int(dir_y * 5))
            ]
            pygame.draw.polygon(self.image, crystal, pts)
            pygame.draw.polygon(self.image, glow, pts, 2)
            
            # 核心光点
            pygame.draw.circle(self.image, core, (cx, cy), 5)
            pygame.draw.circle(self.image, (255, 255, 220), (cx, cy), 3)
            
            # 能量光芒
            for i in range(4):
                angle = t * 3 + i * 1.57
                px = cx + int(math.cos(angle) * 8)
                py = cy + int(math.sin(angle) * 8)
                pygame.draw.circle(self.image, (*glow, 150), (px, py), 2)
    
    def _hsv_to_rgb(self, h, s, v):
        """HSV转RGB辅助函数"""
        h = h / 360.0
        if s == 0.0:
            return (int(v * 255), int(v * 255), int(v * 255))
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        if i == 0: return (int(v * 255), int(t * 255), int(p * 255))
        if i == 1: return (int(q * 255), int(v * 255), int(p * 255))
        if i == 2: return (int(p * 255), int(v * 255), int(t * 255))
        if i == 3: return (int(p * 255), int(q * 255), int(v * 255))
        if i == 4: return (int(t * 255), int(p * 255), int(v * 255))
        return (int(v * 255), int(p * 255), int(q * 255))


# ==================== 治愈守卫浮游炮 ====================
class HealerGuardian(pygame.sprite.Sprite):
    """
    治愈守卫 - 茧化模式激活的浮游炮
    环绕玩家并发射治愈光波，同时提供护盾
    """
    
    def __init__(self, owner, orbit_index=0, total_guardians=4, style="default"):
        super().__init__()
        self.owner = owner
        self.orbit_index = orbit_index
        self.total_guardians = total_guardians
        self.style = style
        self.theme = get_theme(style)
        
        self.orbit_radius = 55
        self.orbit_speed = 0.03
        self.orbit_angle = (orbit_index / total_guardians) * math.pi * 2
        
        self.frame = 0
        self.active = True
        self.lifetime = 300  # 5秒
        
        # 攻击参数
        self.attack_cooldown = 0
        self.attack_delay = 45
        
        self.size = 28
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # 初始位置
        ox = owner.rect.centerx if owner else WIDTH // 2
        oy = owner.rect.centery if owner else HEIGHT // 2
        self.float_x = ox + math.cos(self.orbit_angle) * self.orbit_radius
        self.float_y = oy + math.sin(self.orbit_angle) * self.orbit_radius
        
        self.rect = self.image.get_rect(center=(int(self.float_x), int(self.float_y)))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        
        if not self.active or self.frame > self.lifetime:
            self.kill()
            return
        
        if not self.owner or not self.owner.alive():
            self.kill()
            return
        
        # 轨道运动
        self.orbit_angle += self.orbit_speed
        ox = self.owner.rect.centerx
        oy = self.owner.rect.centery
        
        target_x = ox + math.cos(self.orbit_angle) * self.orbit_radius
        target_y = oy + math.sin(self.orbit_angle) * self.orbit_radius
        
        # 平滑跟随
        self.float_x += (target_x - self.float_x) * 0.15
        self.float_y += (target_y - self.float_y) * 0.15
        
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 攻击
        self.attack_cooldown -= 1
        if self.attack_cooldown <= 0:
            self._attack()
            self.attack_cooldown = self.attack_delay
        
        self._render()
    
    def _attack(self):
        """发射治愈光波"""
        # 寻找最近敌人
        target = None
        min_dist = float('inf')
        for mob in mobs:
            dist = math.hypot(mob.rect.centerx - self.float_x,
                            mob.rect.centery - self.float_y)
            if dist < min_dist:
                min_dist = dist
                target = mob
        
        if target:
            # 计算角度
            dx = target.rect.centerx - self.float_x
            dy = target.rect.centery - self.float_y
            angle = math.degrees(math.atan2(dy, dx))
            
            # 发射光波
            HealingWave(self.float_x, self.float_y, 15, angle, self.owner, self.style)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.1
        
        crystal = self.theme["crystal"]
        core = self.theme["core"]
        glow = self.theme["glow"]
        armor = self.theme["armor"]
        
        # 外层光环
        pulse = 0.7 + 0.3 * math.sin(t * 3)
        for i in range(2):
            r = int((10 + i * 3) * pulse)
            a = max(0, 60 - i * 25)
            if r > 0:
                pygame.draw.circle(self.image, (*glow, a), (cx, cy), r)
        
        # 八角形护盾
        pts = []
        for i in range(8):
            angle = t * 2 + i * 0.785
            r = 8 * pulse
            px = cx + int(math.cos(angle) * r)
            py = cy + int(math.sin(angle) * r)
            pts.append((px, py))
        pygame.draw.polygon(self.image, armor, pts)
        pygame.draw.polygon(self.image, crystal, pts, 2)
        
        # 核心
        pygame.draw.circle(self.image, core, (cx, cy), 4)
        pygame.draw.circle(self.image, (255, 255, 220), (cx, cy), 2)


# ==================== 治愈光波 ====================
class HealingWave(pygame.sprite.Sprite):
    """治愈守卫发射的光波弹"""
    
    def __init__(self, x, y, damage, angle, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.theme = get_theme(style)
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = angle
        self.speed = 10
        
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed
        
        self.frame = 0
        self.lifetime = 60
        
        self.size = 24
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        self.frame += 1
        
        self.float_x += self.vx
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        if (self.frame > self.lifetime or
            self.float_x < -30 or self.float_x > WIDTH + 30 or
            self.float_y < -30 or self.float_y > HEIGHT + 30):
            self.kill()
            return
        
        # 碰撞
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                if hasattr(mob, 'take_damage'):
                    mob.take_damage(self.damage)
                self.kill()
                return
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.3
        
        glow = self.theme["glow"]
        crystal = self.theme["crystal"]
        
        # 光波圆环
        pulse = 0.8 + 0.2 * math.sin(t * 5)
        r = int(8 * pulse)
        pygame.draw.circle(self.image, glow, (cx, cy), r)
        pygame.draw.circle(self.image, crystal, (cx, cy), r - 2)
        pygame.draw.circle(self.image, (255, 255, 220), (cx, cy), 3)


# ==================== 茧化模式护盾效果 ====================
class CocoonShield(pygame.sprite.Sprite):
    """茧化模式的护盾视觉效果"""
    
    def __init__(self, owner, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.active = True
        
        self.size = 80
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=owner.rect.center if owner else (WIDTH//2, HEIGHT//2))
        
        all_sprites.add(self)
    
    def update(self):
        self.frame += 1
        
        if not self.active:
            self.kill()
            return
        
        if self.owner and self.owner.alive():
            self.rect.center = self.owner.rect.center
        else:
            self.kill()
            return
        
        self._render()
    
    def deactivate(self):
        self.active = False
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.size // 2, self.size // 2
        t = self.frame * 0.08
        
        crystal = self.theme["crystal"]
        glow = self.theme["glow"]
        armor = self.theme["armor"]
        
        # 多层护盾
        for i in range(4):
            r = 28 + i * 6 + int(3 * math.sin(t * 2 + i))
            alpha = max(0, 60 - i * 12)
            if r > 0 and alpha > 0:
                pygame.draw.circle(self.image, (*glow, alpha), (cx, cy), r, 2)
        
        # 旋转符文
        for i in range(6):
            angle = t * 1.5 + i * 1.047
            rx = cx + int(math.cos(angle) * 30)
            ry = cy + int(math.sin(angle) * 30)
            rune_pts = [
                (rx, ry - 5), (rx + 4, ry), (rx, ry + 5), (rx - 4, ry)
            ]
            rune_alpha = int(120 + 60 * math.sin(t * 3 + i))
            pygame.draw.polygon(self.image, (*crystal, min(255, rune_alpha)), rune_pts)


# ==================== 终极技能1：熔融之雨 (F技能) ====================
class MoltenRainStorm(pygame.sprite.Sprite):
    """
    熔融之雨 - F技能 (克苏鲁级质量)
    
    三阶段大招：
    第一阶段 (1s): 天际裂隙 - 天空撕裂，熔岩涌出预警
    第二阶段 (3s): 熔岩倾泻 - 大量熔岩球从裂隙落下，带燃烧轨迹
    第三阶段 (1s): 终焉冲击 - 最后一波巨型熔岩+地面岩浆波
    """
    
    def __init__(self, owner, damage, style="default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.total_frame = 0
        self.phase = 0
        self.phase_duration = [60, 180, 60]  # 1s, 3s, 1s
        
        # 天空裂隙
        self.rifts = []
        self.rift_particles = []
        
        # 熔岩球
        self.molten_globs = []
        
        # 地面岩浆
        self.ground_lava = []
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        self.rift_particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size
        })
    
    def update(self):
        self.total_frame += 1
        
        # 确定当前阶段
        phase_start = 0
        for i, dur in enumerate(self.phase_duration):
            if self.total_frame <= phase_start + dur:
                self.phase = i
                self.frame = self.total_frame - phase_start
                break
            phase_start += dur
        else:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        if self.phase == 0:
            self._phase1_sky_rift()
        elif self.phase == 1:
            self._phase2_molten_rain()
        elif self.phase == 2:
            self._phase3_final_impact()
        
        self._update_particles()
        self._update_molten_globs()
        self._update_ground_lava()
    
    def _phase1_sky_rift(self):
        """第一阶段：天际裂隙 - 天空撕裂预警"""
        progress = self.frame / self.phase_duration[0]
        
        flame = self.theme.get("flame", (255, 165, 0))
        core = self.theme.get("core", (255, 200, 100))
        glow = self.theme.get("glow", (255, 223, 128))
        
        # 天空变红 - 渐变效果
        for y in range(0, HEIGHT // 3):
            red_alpha = int(40 * progress * (1 - y / (HEIGHT // 3)))
            pygame.draw.line(self.image, (120, 40, 20, red_alpha), (0, y), (WIDTH, y))
        
        # 生成裂隙
        if self.frame == 1:
            for i in range(5):
                self.rifts.append({
                    'x': 100 + i * (WIDTH - 200) // 4,
                    'width': 0,
                    'max_width': random.randint(80, 120),
                    'height': random.randint(40, 60),
                    'glow': 0,
                    'shake': random.uniform(0, 6.28)
                })
        
        # 裂隙撕裂动画
        for rift in self.rifts:
            if rift['width'] < rift['max_width']:
                rift['width'] += rift['max_width'] / 25
            rift['glow'] = min(1.0, rift['glow'] + 0.04)
            
            rx = rift['x'] + int(3 * math.sin(self.frame * 0.3 + rift['shake']))
            rw, rh = int(rift['width']), rift['height']
            
            # 裂隙外层光晕 - 多层渐变
            for i in range(5):
                glow_w = rw + i * 15
                glow_h = rh + i * 8
                glow_alpha = int((100 - i * 18) * rift['glow'])
                color = (255, 80 + i * 20, 30)
                pygame.draw.ellipse(self.image, (*color, glow_alpha),
                                   (rx - glow_w//2, 30 - glow_h//2, glow_w, glow_h))
            
            # 裂隙中层 - 岩浆色
            pygame.draw.ellipse(self.image, (*flame, int(200 * rift['glow'])),
                               (rx - rw//2, 30 - rh//2, rw, rh))
            
            # 裂隙核心 - 白热
            core_w, core_h = int(rw * 0.6), int(rh * 0.5)
            pygame.draw.ellipse(self.image, (*core, int(255 * rift['glow'])),
                               (rx - core_w//2, 30 - core_h//2, core_w, core_h))
            
            # 裂隙边缘 - 撕裂效果
            for edge in range(8):
                edge_angle = edge * 0.785 + self.frame * 0.1
                edge_len = rw * 0.3 + 10 * math.sin(self.frame * 0.2 + edge)
                ex = rx + int(math.cos(edge_angle) * (rw * 0.4 + edge_len * 0.5))
                ey = 30 + int(math.sin(edge_angle) * (rh * 0.3))
                pygame.draw.line(self.image, (*glow, int(180 * rift['glow'])),
                               (rx, 30), (ex, ey), 2)
            
            # 预警线 - 落点指示
            if progress > 0.4:
                warn_alpha = int(180 * (progress - 0.4) / 0.6 * (0.5 + 0.5 * math.sin(self.frame * 0.3)))
                for i in range(3):
                    line_x = rx + (i - 1) * 2
                    pygame.draw.line(self.image, (255, 100, 100, warn_alpha),
                                   (line_x, 50), (line_x, HEIGHT), 1)
                # 落点圆圈
                pygame.draw.circle(self.image, (255, 100, 100, warn_alpha),
                                 (rx, HEIGHT - 30), 25 + int(10 * math.sin(self.frame * 0.2)), 2)
            
            # 火花粒子从裂隙喷出
            if random.random() < 0.4 * rift['glow']:
                for _ in range(2):
                    self._add_particle(
                        rx + random.randint(-rw//3, rw//3), 
                        30 + random.randint(-5, 10),
                        random.uniform(-2, 2), 
                        random.uniform(2, 6),
                        (255, random.randint(120, 200), random.randint(30, 80)), 
                        random.randint(25, 45), 
                        random.randint(3, 6)
                    )
    
    def _phase2_molten_rain(self):
        """第二阶段：熔岩倾泻 - 大量熔岩球落下"""
        progress = self.frame / self.phase_duration[1]
        
        flame = self.theme.get("flame", (255, 165, 0))
        
        # 持续的红色天空
        for y in range(0, HEIGHT // 4):
            alpha = int(50 * (1 - y / (HEIGHT // 4)))
            pygame.draw.line(self.image, (100, 30, 15, alpha), (0, y), (WIDTH, y))
        
        # 绘制裂隙（持续发光脉动）
        for rift in self.rifts:
            rx = rift['x'] + int(4 * math.sin(self.frame * 0.25 + rift['shake']))
            rw, rh = int(rift['max_width']), rift['height']
            pulse = 0.6 + 0.4 * math.sin(self.frame * 0.15)
            
            # 光晕
            for i in range(4):
                glow_alpha = int((70 - i * 15) * pulse)
                pygame.draw.ellipse(self.image, (255, 100, 50, glow_alpha),
                                   (rx - rw//2 - i*8, 30 - rh//2 - i*3, rw + i*16, rh + i*6))
            
            # 核心
            pygame.draw.ellipse(self.image, (*flame, int(200 * pulse)),
                               (rx - rw//2, 30 - rh//2, rw, rh))
            pygame.draw.ellipse(self.image, (255, 220, 150, int(255 * pulse)),
                               (rx - rw//3, 30 - rh//3, int(rw * 0.66), int(rh * 0.66)))
        
        # 生成熔岩球 - 随时间加密
        spawn_rate = 6 if progress < 0.5 else 4 if progress < 0.8 else 3
        if self.frame % spawn_rate == 0:
            rift = random.choice(self.rifts)
            size = random.randint(18, 35)
            self.molten_globs.append({
                'x': rift['x'] + random.randint(-40, 40),
                'y': 50,
                'vx': random.uniform(-1.5, 1.5),
                'vy': random.uniform(5, 9),
                'size': size,
                'rotation': random.uniform(0, 6.28),
                'rot_speed': random.uniform(-0.15, 0.15),
                'trail': [],
                'alive': True,
                'pulse_offset': random.uniform(0, 6.28)
            })
    
    def _phase3_final_impact(self):
        """第三阶段：终焉冲击 - 巨型熔岩+岩浆波"""
        progress = self.frame / self.phase_duration[2]
        
        flame = self.theme.get("flame", (255, 165, 0))
        core = self.theme.get("core", (255, 200, 100))
        
        # 生成巨型熔岩
        if self.frame == 1:
            for rift in self.rifts:
                self.molten_globs.append({
                    'x': rift['x'],
                    'y': 50,
                    'vx': 0,
                    'vy': 14,
                    'size': 55,
                    'rotation': 0,
                    'rot_speed': 0.08,
                    'trail': [],
                    'alive': True,
                    'is_giant': True,
                    'pulse_offset': 0
                })
        
        # 地面岩浆波
        if progress > 0.3:
            wave_progress = (progress - 0.3) / 0.7
            wave_height = int(40 * wave_progress)
            
            # 岩浆波纹
            for x in range(0, WIDTH, 15):
                wave_offset = 12 * math.sin(x * 0.04 + self.frame * 0.15)
                wave_y = HEIGHT - wave_height + int(wave_offset)
                
                # 多层岩浆
                pygame.draw.ellipse(self.image, (200, 60, 30, 180),
                                   (x - 12, wave_y - 5, 24, wave_height + 10))
            
            # 岩浆表面高光
            surface_y = HEIGHT - wave_height + 5
            for x in range(0, WIDTH, 8):
                surf_wave = 8 * math.sin(x * 0.06 + self.frame * 0.2)
                pygame.draw.ellipse(self.image, (*core, 200),
                                   (x - 6, surface_y + int(surf_wave), 12, 8))
            
            # 岩浆主体
            pygame.draw.rect(self.image, (*flame, 220),
                            (0, HEIGHT - wave_height + 15, WIDTH, wave_height))
            
            # 对地面敌人造成伤害
            if self.frame % 8 == 0:
                for mob in mobs:
                    if mob.rect.bottom > HEIGHT - wave_height:
                        if hasattr(mob, 'take_damage'):
                            mob.take_damage(self.damage * 0.4)
    
    def _update_particles(self):
        """更新粒子效果"""
        for p in self.rift_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.12  # 重力
            p['life'] -= 1
            
            if p['life'] <= 0 or p['y'] > HEIGHT:
                self.rift_particles.remove(p)
                continue
            
            # 渐变消失
            life_ratio = p['life'] / p['max_life']
            alpha = int(255 * life_ratio)
            size = max(1, int(p['size'] * (0.3 + 0.7 * life_ratio)))
            
            # 绘制粒子
            pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                             (int(p['x']), int(p['y'])), size)
            # 粒子光晕
            if size > 2:
                pygame.draw.circle(self.image, (*p['color'][:3], alpha // 3),
                                 (int(p['x']), int(p['y'])), size + 2)
    
    def _update_molten_globs(self):
        """更新熔岩球"""
        flame = self.theme.get("flame", (255, 165, 0))
        core = self.theme.get("core", (255, 200, 100))
        glow = self.theme.get("glow", (255, 223, 128))
        
        for glob in self.molten_globs[:]:
            if not glob['alive']:
                self.molten_globs.remove(glob)
                continue
            
            # 物理更新
            glob['x'] += glob['vx']
            glob['y'] += glob['vy']
            glob['vy'] += 0.25  # 重力加速
            glob['rotation'] += glob['rot_speed']
            
            # 拖尾记录
            glob['trail'].append((glob['x'], glob['y']))
            if len(glob['trail']) > 15:
                glob['trail'].pop(0)
            
            gx, gy = int(glob['x']), int(glob['y'])
            size = glob['size']
            is_giant = glob.get('is_giant', False)
            t = self.total_frame * 0.15 + glob['pulse_offset']
            pulse = 0.85 + 0.15 * math.sin(t * 3)
            
            # 绘制拖尾 - 火焰轨迹
            for i, (tx, ty) in enumerate(glob['trail']):
                trail_progress = i / len(glob['trail'])
                trail_alpha = int(180 * trail_progress)
                trail_size = int(size * 0.5 * trail_progress)
                
                if trail_size > 1:
                    # 拖尾渐变色
                    tr = int(255)
                    tg = int(100 + 80 * trail_progress)
                    tb = int(30 + 40 * (1 - trail_progress))
                    pygame.draw.circle(self.image, (tr, tg, tb, trail_alpha),
                                     (int(tx), int(ty)), trail_size)
            
            # 外层光晕
            for i in range(4):
                glow_r = int((size + i * 8) * pulse)
                glow_alpha = 60 - i * 12
                pygame.draw.circle(self.image, (*glow, glow_alpha), (gx, gy), glow_r)
            
            # 熔岩表面 - 不规则多边形
            points = []
            num_points = 10 if is_giant else 8
            for i in range(num_points):
                angle = glob['rotation'] + i * (6.28 / num_points)
                # 不规则半径
                r = size * pulse * (0.75 + 0.25 * math.sin(angle * 3 + t * 2))
                points.append((gx + int(math.cos(angle) * r), 
                              gy + int(math.sin(angle) * r)))
            pygame.draw.polygon(self.image, flame, points)
            
            # 熔岩内核
            inner_size = int(size * 0.65 * pulse)
            pygame.draw.circle(self.image, core, (gx, gy), inner_size)
            
            # 白热中心
            hot_size = int(size * 0.35 * pulse)
            pygame.draw.circle(self.image, (255, 255, 220), (gx, gy), hot_size)
            
            # 表面裂纹 - 岩浆流动
            for i in range(5 if is_giant else 3):
                crack_angle = glob['rotation'] * 2 + i * (6.28 / (5 if is_giant else 3))
                c1x = gx + int(math.cos(crack_angle) * size * 0.25)
                c1y = gy + int(math.sin(crack_angle) * size * 0.25)
                c2x = gx + int(math.cos(crack_angle) * size * 0.85)
                c2y = gy + int(math.sin(crack_angle) * size * 0.85)
                pygame.draw.line(self.image, (255, 255, 180, 200), (c1x, c1y), (c2x, c2y), 2)
            
            # 喷溅火花
            if random.random() < 0.2:
                spark_angle = random.uniform(0, 6.28)
                self._add_particle(
                    gx + math.cos(spark_angle) * size * 0.5,
                    gy + math.sin(spark_angle) * size * 0.5,
                    math.cos(spark_angle) * 2 + glob['vx'] * 0.5,
                    math.sin(spark_angle) * 2 - 2,
                    (255, random.randint(150, 220), random.randint(50, 100)),
                    random.randint(15, 30), random.randint(2, 4)
                )
            
            # 碰撞检测 - 地面
            if glob['y'] > HEIGHT - 15:
                glob['alive'] = False
                self._create_impact(gx, HEIGHT - 10, size, is_giant)
                continue
            
            # 碰撞检测 - 敌人
            for mob in mobs:
                dist = math.hypot(mob.rect.centerx - gx, mob.rect.centery - gy)
                if dist < size + 25:
                    if hasattr(mob, 'take_damage'):
                        dmg = self.damage * (2.5 if is_giant else 1.0)
                        mob.take_damage(dmg)
                    glob['alive'] = False
                    self._create_impact(gx, gy, size, is_giant)
                    break
    
    def _create_impact(self, x, y, size, is_giant):
        """创建撞击效果"""
        # 地面岩浆池
        self.ground_lava.append({
            'x': x, 'y': y,
            'radius': size * (3.5 if is_giant else 2),
            'life': 80 if is_giant else 50,
            'max_life': 80 if is_giant else 50
        })
        
        # 粒子爆发
        count = 30 if is_giant else 15
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(4, 12 if is_giant else 8)
            self._add_particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed - 4,
                (255, random.randint(100, 200), random.randint(30, 80)),
                random.randint(25, 50),
                random.randint(3, 7 if is_giant else 5)
            )
    
    def _update_ground_lava(self):
        """更新地面岩浆池"""
        flame = self.theme.get("flame", (255, 165, 0))
        core = self.theme.get("core", (255, 200, 100))
        
        for lava in self.ground_lava[:]:
            lava['life'] -= 1
            if lava['life'] <= 0:
                self.ground_lava.remove(lava)
                continue
            
            life_ratio = lava['life'] / lava['max_life']
            r = int(lava['radius'] * (0.4 + 0.6 * life_ratio))
            
            # 岩浆池 - 椭圆形
            pool_h = int(r * 0.4)
            alpha = int(200 * life_ratio)
            
            # 外层光晕
            pygame.draw.ellipse(self.image, (180, 60, 30, int(alpha * 0.5)),
                               (int(lava['x'] - r - 10), int(lava['y'] - pool_h - 5), 
                                (r + 10) * 2, (pool_h + 5) * 2))
            
            # 主体
            pygame.draw.ellipse(self.image, (*flame, alpha),
                               (int(lava['x'] - r), int(lava['y'] - pool_h), r * 2, pool_h * 2))
            
            # 高亮中心
            inner_r = int(r * 0.6)
            inner_h = int(pool_h * 0.6)
            pygame.draw.ellipse(self.image, (*core, int(alpha * 0.8)),
                               (int(lava['x'] - inner_r), int(lava['y'] - inner_h), 
                                inner_r * 2, inner_h * 2))
            
            # 气泡效果
            if random.random() < 0.15 * life_ratio:
                bx = lava['x'] + random.randint(-int(r * 0.7), int(r * 0.7))
                by = lava['y'] + random.randint(-int(pool_h * 0.5), int(pool_h * 0.3))
                pygame.draw.circle(self.image, (255, 220, 150, int(alpha * 0.8)),
                                 (int(bx), int(by)), random.randint(2, 4))


# ==================== 终极技能2：神圣射线 (G技能) ====================
class HolyRay(pygame.sprite.Sprite):
    """
    神圣射线 - G技能 (克苏鲁级质量)
    
    三阶段大招：
    第一阶段 (0.8s): 圣光凝聚 - 玩家上方形成棱镜阵列
    第二阶段 (2.5s): 光芒扫射 - 多道圣光射线扫射全场
    第三阶段 (0.7s): 圣光爆发 - 所有射线汇聚中心爆发
    """
    
    def __init__(self, owner, damage, style="default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.total_frame = 0
        self.phase = 0
        self.phase_duration = [48, 150, 42]  # 0.8s, 2.5s, 0.7s
        
        # 棱镜阵列
        self.prisms = []
        
        # 射线
        self.rays = []
        
        # 粒子
        self.particles = []
        
        # 核心位置
        self.core_x = WIDTH // 2
        self.core_y = 120
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size
        })
    
    def update(self):
        self.total_frame += 1
        
        # 确定当前阶段
        phase_start = 0
        for i, dur in enumerate(self.phase_duration):
            if self.total_frame <= phase_start + dur:
                self.phase = i
                self.frame = self.total_frame - phase_start
                break
            phase_start += dur
        else:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        if self.phase == 0:
            self._phase1_prism_formation()
        elif self.phase == 1:
            self._phase2_ray_sweep()
        elif self.phase == 2:
            self._phase3_convergence()
        
        self._update_particles()
        self._draw_prisms()
    
    def _phase1_prism_formation(self):
        """第一阶段：圣光凝聚 - 棱镜阵列形成"""
        progress = self.frame / self.phase_duration[0]
        
        glow = self.theme.get("glow", (255, 223, 128))
        crystal = self.theme.get("crystal", (255, 200, 100))
        core = self.theme.get("core", (255, 180, 80))
        
        # 初始化棱镜
        if self.frame == 1:
            # 中心主棱镜
            self.prisms.append({
                'x': self.core_x, 'y': self.core_y,
                'size': 0, 'target_size': 50,
                'rotation': 0, 'rot_speed': 0.03,
                'is_main': True, 'glow': 0
            })
            # 环绕棱镜
            for i in range(6):
                angle = i * math.pi / 3
                self.prisms.append({
                    'x': self.core_x + math.cos(angle) * 100,
                    'y': self.core_y + math.sin(angle) * 60,
                    'size': 0, 'target_size': 30,
                    'rotation': random.uniform(0, 6.28),
                    'rot_speed': 0.05 * (1 if i % 2 == 0 else -1),
                    'is_main': False, 'glow': 0,
                    'orbit_angle': angle, 'orbit_speed': 0.02
                })
        
        # 棱镜生长动画
        for prism in self.prisms:
            grow_speed = prism['target_size'] / 30
            if prism['size'] < prism['target_size']:
                prism['size'] += grow_speed
            prism['glow'] = min(1.0, prism['glow'] + 0.04)
            prism['rotation'] += prism['rot_speed']
        
        # 聚光效果 - 光线从四周汇聚
        if progress > 0.3:
            num_beams = int(12 * (progress - 0.3) / 0.7)
            for i in range(num_beams):
                angle = i * (6.28 / 12) + self.frame * 0.05
                start_dist = 400
                sx = self.core_x + math.cos(angle) * start_dist
                sy = self.core_y + math.sin(angle) * start_dist * 0.6
                
                # 渐变光线
                beam_alpha = int(100 * ((progress - 0.3) / 0.7))
                pygame.draw.line(self.image, (*glow, beam_alpha),
                               (int(sx), int(sy)), (self.core_x, self.core_y), 2)
        
        # 核心光球生长
        core_size = int(25 * progress)
        if core_size > 0:
            for i in range(4):
                pygame.draw.circle(self.image, (*glow, 40 - i * 8),
                                 (self.core_x, self.core_y), core_size + i * 12)
            pygame.draw.circle(self.image, (*crystal, 200),
                             (self.core_x, self.core_y), core_size)
            pygame.draw.circle(self.image, (255, 255, 240, 255),
                             (self.core_x, self.core_y), int(core_size * 0.5))
    
    def _phase2_ray_sweep(self):
        """第二阶段：光芒扫射 - 射线扫射全场"""
        progress = self.frame / self.phase_duration[1]
        
        glow = self.theme.get("glow", (255, 223, 128))
        crystal = self.theme.get("crystal", (255, 200, 100))
        flame = self.theme.get("flame", (255, 165, 0))
        
        # 更新棱镜轨道
        for prism in self.prisms:
            prism['rotation'] += prism['rot_speed']
            if not prism['is_main'] and 'orbit_angle' in prism:
                prism['orbit_angle'] += prism['orbit_speed']
                prism['x'] = self.core_x + math.cos(prism['orbit_angle']) * 100
                prism['y'] = self.core_y + math.sin(prism['orbit_angle']) * 60
        
        # 初始化射线
        if self.frame == 1:
            # 创建7道扫射射线
            for i in range(7):
                start_angle = -0.5 + i * 0.15  # 初始角度分散
                self.rays.append({
                    'angle': start_angle,
                    'sweep_dir': 1 if i % 2 == 0 else -1,
                    'sweep_speed': 0.015 + random.uniform(-0.003, 0.003),
                    'width': random.randint(15, 25),
                    'length': HEIGHT + 100,
                    'origin_prism': i % len(self.prisms),
                    'color_offset': random.uniform(0, 6.28)
                })
        
        # 绘制扫射射线
        for ray in self.rays:
            # 更新扫射角度
            ray['angle'] += ray['sweep_dir'] * ray['sweep_speed']
            
            # 边界反弹
            if ray['angle'] > 1.2 or ray['angle'] < -1.2:
                ray['sweep_dir'] *= -1
            
            # 获取发射源棱镜
            prism = self.prisms[ray['origin_prism'] % len(self.prisms)]
            ox, oy = int(prism['x']), int(prism['y'])
            
            # 射线终点
            end_x = ox + math.sin(ray['angle']) * ray['length']
            end_y = oy + math.cos(ray['angle']) * ray['length']
            
            # 动态颜色 - 棱镜折射效果
            t = self.total_frame * 0.1 + ray['color_offset']
            color_shift = (0.5 + 0.5 * math.sin(t)) 
            ray_color = (
                int(glow[0] * 0.8 + crystal[0] * 0.2 * color_shift),
                int(glow[1] * 0.7 + flame[1] * 0.3 * color_shift),
                int(glow[2] * 0.6 + crystal[2] * 0.4 * (1 - color_shift))
            )
            
            # 多层射线绘制
            for layer in range(5):
                layer_width = ray['width'] - layer * 4
                layer_alpha = 180 - layer * 35
                if layer_width > 0:
                    pygame.draw.line(self.image, (*ray_color, layer_alpha),
                                   (ox, oy), (int(end_x), int(end_y)), layer_width)
            
            # 射线核心 - 最亮
            pygame.draw.line(self.image, (255, 255, 240, 255),
                           (ox, oy), (int(end_x), int(end_y)), 3)
            
            # 射线粒子效果
            if random.random() < 0.3:
                dist = random.uniform(50, ray['length'] * 0.8)
                px = ox + math.sin(ray['angle']) * dist
                py = oy + math.cos(ray['angle']) * dist
                self._add_particle(
                    px + random.uniform(-10, 10),
                    py + random.uniform(-10, 10),
                    random.uniform(-1, 1),
                    random.uniform(-1, 1),
                    ray_color, random.randint(15, 30), random.randint(2, 5)
                )
            
            # 射线伤害检测
            if self.frame % 6 == 0:
                self._ray_damage(ox, oy, ray['angle'], ray['length'], ray['width'])
        
        # 中心光球脉动
        pulse = 0.8 + 0.2 * math.sin(self.frame * 0.2)
        core_size = int(35 * pulse)
        for i in range(4):
            pygame.draw.circle(self.image, (*glow, 50 - i * 10),
                             (self.core_x, self.core_y), core_size + i * 15)
        pygame.draw.circle(self.image, crystal, (self.core_x, self.core_y), core_size)
    
    def _phase3_convergence(self):
        """第三阶段：圣光爆发 - 射线汇聚爆发"""
        progress = self.frame / self.phase_duration[2]
        
        glow = self.theme.get("glow", (255, 223, 128))
        crystal = self.theme.get("crystal", (255, 200, 100))
        core = self.theme.get("core", (255, 180, 80))
        
        # 射线收束
        for i, ray in enumerate(self.rays):
            # 角度向中心收束
            target_angle = 0
            ray['angle'] += (target_angle - ray['angle']) * 0.15
            ray['width'] = int(ray['width'] * 1.05)  # 宽度增加
            
            prism = self.prisms[ray['origin_prism'] % len(self.prisms)]
            ox, oy = int(prism['x']), int(prism['y'])
            
            end_x = ox + math.sin(ray['angle']) * ray['length']
            end_y = oy + math.cos(ray['angle']) * ray['length']
            
            # 收束时增强亮度
            alpha_boost = int(50 * progress)
            for layer in range(5):
                layer_width = ray['width'] - layer * 5
                layer_alpha = min(255, 200 + alpha_boost - layer * 30)
                if layer_width > 0:
                    pygame.draw.line(self.image, (*glow, layer_alpha),
                                   (ox, oy), (int(end_x), int(end_y)), layer_width)
        
        # 中心爆发
        if progress > 0.4:
            burst_progress = (progress - 0.4) / 0.6
            burst_radius = int(300 * burst_progress)
            
            # 爆发冲击波
            for i in range(5):
                wave_r = burst_radius - i * 20
                if wave_r > 0:
                    wave_alpha = int((150 - i * 25) * (1 - burst_progress * 0.5))
                    pygame.draw.circle(self.image, (*crystal, wave_alpha),
                                     (self.core_x, self.core_y), wave_r, 4 - i)
            
            # 光芒四射
            for i in range(16):
                angle = i * (6.28 / 16) + self.frame * 0.05
                ray_len = burst_radius * 1.5
                ex = self.core_x + math.cos(angle) * ray_len
                ey = self.core_y + math.sin(angle) * ray_len
                ray_alpha = int(200 * (1 - burst_progress * 0.3))
                pygame.draw.line(self.image, (*glow, ray_alpha),
                               (self.core_x, self.core_y), (int(ex), int(ey)), 3)
            
            # 爆发伤害
            if self.frame % 5 == 0:
                for mob in mobs:
                    dist = math.hypot(mob.rect.centerx - self.core_x,
                                    mob.rect.centery - self.core_y)
                    if dist < burst_radius:
                        if hasattr(mob, 'take_damage'):
                            dmg = self.damage * 1.5 * (1 - dist / burst_radius)
                            mob.take_damage(dmg)
            
            # 爆发粒子
            if random.random() < 0.6:
                angle = random.uniform(0, 6.28)
                speed = random.uniform(5, 15)
                self._add_particle(
                    self.core_x, self.core_y,
                    math.cos(angle) * speed, math.sin(angle) * speed,
                    (255, random.randint(200, 255), random.randint(100, 180)),
                    random.randint(20, 40), random.randint(3, 7)
                )
        
        # 棱镜收缩消失
        for prism in self.prisms:
            prism['size'] *= 0.95
            prism['glow'] *= 0.95
    
    def _ray_damage(self, ox, oy, angle, length, width):
        """射线伤害检测"""
        for mob in mobs:
            mx, my = mob.rect.centerx, mob.rect.centery
            
            # 计算点到射线的距离
            dx = mx - ox
            dy = my - oy
            
            # 射线方向
            ray_dx = math.sin(angle)
            ray_dy = math.cos(angle)
            
            # 投影长度
            proj = dx * ray_dx + dy * ray_dy
            
            if proj > 0 and proj < length:
                # 垂直距离
                perp_dist = abs(dx * ray_dy - dy * ray_dx)
                if perp_dist < width + 20:
                    if hasattr(mob, 'take_damage'):
                        mob.take_damage(self.damage * 0.6)
    
    def _draw_prisms(self):
        """绘制棱镜"""
        glow = self.theme.get("glow", (255, 223, 128))
        crystal = self.theme.get("crystal", (255, 200, 100))
        
        for prism in self.prisms:
            if prism['size'] < 2:
                continue
            
            px, py = int(prism['x']), int(prism['y'])
            size = int(prism['size'])
            rot = prism['rotation']
            
            # 外层光晕
            glow_alpha = int(80 * prism['glow'])
            for i in range(3):
                pygame.draw.circle(self.image, (*glow, glow_alpha - i * 20),
                                 (px, py), size + i * 8)
            
            # 棱镜主体 - 六边形
            points = []
            num_sides = 6
            for i in range(num_sides):
                angle = rot + i * (6.28 / num_sides)
                points.append((
                    px + int(math.cos(angle) * size),
                    py + int(math.sin(angle) * size * 0.7)  # 透视压缩
                ))
            pygame.draw.polygon(self.image, (*crystal, int(200 * prism['glow'])), points)
            
            # 棱镜边框
            pygame.draw.polygon(self.image, (*glow, int(255 * prism['glow'])), points, 2)
            
            # 内部结构 - 折射线
            inner_size = size * 0.5
            for i in range(3):
                angle1 = rot + i * (6.28 / 3)
                angle2 = rot + (i + 1.5) * (6.28 / 3)
                x1 = px + int(math.cos(angle1) * inner_size)
                y1 = py + int(math.sin(angle1) * inner_size * 0.7)
                x2 = px + int(math.cos(angle2) * inner_size)
                y2 = py + int(math.sin(angle2) * inner_size * 0.7)
                line_alpha = int(150 * prism['glow'])
                pygame.draw.line(self.image, (255, 255, 220, line_alpha),
                               (x1, y1), (x2, y2), 1)
            
            # 核心高光
            if prism['is_main']:
                pygame.draw.circle(self.image, (255, 255, 240, int(255 * prism['glow'])),
                                 (px, py), int(size * 0.3))
    
    def _update_particles(self):
        """更新粒子"""
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            
            life_ratio = p['life'] / p['max_life']
            alpha = int(255 * life_ratio)
            size = max(1, int(p['size'] * life_ratio))
            
            pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                             (int(p['x']), int(p['y'])), size)
            if size > 2:
                pygame.draw.circle(self.image, (*p['color'][:3], alpha // 3),
                                 (int(p['x']), int(p['y'])), size + 2)


# ==================== 终极技能3：超新星爆发 (C技能) ====================
class SupernovaExplosion(pygame.sprite.Sprite):
    """
    超新星爆发 - C技能 (克苏鲁级质量)
    
    三阶段大招：
    第一阶段 (1.2s): 星核凝聚 - 六芒星阵法形成，能量汇聚
    第二阶段 (0.5s): 超新星爆发 - 中心剧烈爆炸，冲击波扩散
    第三阶段 (1.8s): 星尘余烬 - 大量星尘子弹向四周散射
    """
    
    def __init__(self, owner, damage, style="default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = style
        self.theme = get_theme(style)
        
        self.frame = 0
        self.total_frame = 0
        self.phase = 0
        self.phase_duration = [72, 30, 108]  # 1.2s, 0.5s, 1.8s
        
        # 核心位置（玩家位置）
        self.core_x = owner.rect.centerx if owner else WIDTH // 2
        self.core_y = owner.rect.centery if owner else HEIGHT // 2
        
        # 六芒星阵法
        self.hexagram_rotation = 0
        self.hexagram_size = 0
        
        # 能量环
        self.energy_rings = []
        
        # 粒子
        self.particles = []
        
        # 星尘子弹
        self.stardust_bullets = []
        
        # 爆炸状态
        self.explosion_radius = 0
        self.shockwaves = []
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life, 'size': size
        })
    
    def update(self):
        self.total_frame += 1
        
        # 更新核心位置跟随玩家
        if self.phase == 0 and self.owner:
            self.core_x = self.owner.rect.centerx
            self.core_y = self.owner.rect.centery
        
        # 确定当前阶段
        phase_start = 0
        for i, dur in enumerate(self.phase_duration):
            if self.total_frame <= phase_start + dur:
                self.phase = i
                self.frame = self.total_frame - phase_start
                break
            phase_start += dur
        else:
            self.kill()
            return
        
        self.image.fill((0, 0, 0, 0))
        
        if self.phase == 0:
            self._phase1_star_formation()
        elif self.phase == 1:
            self._phase2_supernova()
        elif self.phase == 2:
            self._phase3_stardust()
        
        self._update_particles()
    
    def _phase1_star_formation(self):
        """第一阶段：星核凝聚 - 六芒星阵法形成"""
        progress = self.frame / self.phase_duration[0]
        
        glow = self.theme.get("glow", (255, 223, 128))
        crystal = self.theme.get("crystal", (255, 200, 100))
        flame = self.theme.get("flame", (255, 165, 0))
        core_color = self.theme.get("core", (255, 180, 80))
        
        cx, cy = self.core_x, self.core_y
        
        # 六芒星成长
        self.hexagram_size = min(150, 150 * progress * 1.2)
        self.hexagram_rotation += 0.02
        
        # 绘制外层能量场
        field_alpha = int(30 * progress)
        field_radius = int(180 * progress)
        for i in range(4):
            pygame.draw.circle(self.image, (*glow, field_alpha - i * 6),
                             (cx, cy), field_radius + i * 15)
        
        # 绘制六芒星（两个重叠三角形）
        if self.hexagram_size > 10:
            size = self.hexagram_size
            rot = self.hexagram_rotation
            
            # 上三角
            tri1 = []
            for i in range(3):
                angle = rot + i * (6.28 / 3) - math.pi / 2
                tri1.append((
                    cx + int(math.cos(angle) * size),
                    cy + int(math.sin(angle) * size)
                ))
            
            # 下三角（旋转180度）
            tri2 = []
            for i in range(3):
                angle = rot + i * (6.28 / 3) + math.pi / 2
                tri2.append((
                    cx + int(math.cos(angle) * size),
                    cy + int(math.sin(angle) * size)
                ))
            
            # 绘制六芒星光晕
            star_alpha = int(150 * min(1.0, progress * 1.5))
            pygame.draw.polygon(self.image, (*crystal, star_alpha // 2), tri1)
            pygame.draw.polygon(self.image, (*crystal, star_alpha // 2), tri2)
            
            # 六芒星边框 - 多层
            for layer in range(3):
                layer_alpha = star_alpha - layer * 40
                if layer_alpha > 0:
                    pygame.draw.polygon(self.image, (*glow, layer_alpha), tri1, 3 - layer)
                    pygame.draw.polygon(self.image, (*glow, layer_alpha), tri2, 3 - layer)
            
            # 六个顶点的能量节点
            all_vertices = tri1 + tri2
            for vx, vy in all_vertices:
                node_pulse = 0.7 + 0.3 * math.sin(self.frame * 0.15 + vx * 0.01)
                node_size = int(12 * node_pulse * progress)
                if node_size > 2:
                    pygame.draw.circle(self.image, (*flame, int(200 * progress)),
                                     (vx, vy), node_size)
                    pygame.draw.circle(self.image, (255, 255, 220, int(255 * progress)),
                                     (vx, vy), int(node_size * 0.5))
        
        # 能量汇聚线
        if progress > 0.3:
            num_lines = int(12 * (progress - 0.3) / 0.7)
            for i in range(num_lines):
                angle = i * (6.28 / 12) + self.frame * 0.08
                # 从远处汇聚
                outer_dist = 250 - 100 * ((progress - 0.3) / 0.7)
                inner_dist = 30 * progress
                
                ox = cx + int(math.cos(angle) * outer_dist)
                oy = cy + int(math.sin(angle) * outer_dist)
                ix = cx + int(math.cos(angle) * inner_dist)
                iy = cy + int(math.sin(angle) * inner_dist)
                
                line_alpha = int(180 * (progress - 0.3) / 0.7)
                pygame.draw.line(self.image, (*glow, line_alpha), (ox, oy), (ix, iy), 2)
                
                # 汇聚粒子
                if random.random() < 0.2:
                    self._add_particle(
                        ox, oy,
                        (ix - ox) * 0.05, (iy - oy) * 0.05,
                        glow, random.randint(15, 25), random.randint(2, 4)
                    )
        
        # 中心核心
        core_pulse = 0.6 + 0.4 * math.sin(self.frame * 0.2)
        core_size = int(40 * progress * core_pulse)
        if core_size > 3:
            # 核心光晕
            for i in range(5):
                pygame.draw.circle(self.image, (*flame, 60 - i * 10),
                                 (cx, cy), core_size + i * 10)
            # 核心主体
            pygame.draw.circle(self.image, core_color, (cx, cy), core_size)
            # 白热中心
            pygame.draw.circle(self.image, (255, 255, 240), (cx, cy), int(core_size * 0.4))
        
        # 旋转能量环
        if progress > 0.5:
            ring_progress = (progress - 0.5) / 0.5
            for ring_i in range(3):
                ring_rot = self.hexagram_rotation * (2 + ring_i * 0.5)
                ring_radius = 60 + ring_i * 35
                ring_alpha = int(120 * ring_progress)
                
                # 绘制点阵环
                num_dots = 16 + ring_i * 4
                for d in range(num_dots):
                    dot_angle = ring_rot + d * (6.28 / num_dots)
                    dx = cx + int(math.cos(dot_angle) * ring_radius)
                    dy = cy + int(math.sin(dot_angle) * ring_radius)
                    dot_size = 3 + int(2 * math.sin(self.frame * 0.1 + d))
                    pygame.draw.circle(self.image, (*crystal, ring_alpha),
                                     (dx, dy), dot_size)
    
    def _phase2_supernova(self):
        """第二阶段：超新星爆发 - 剧烈爆炸"""
        progress = self.frame / self.phase_duration[1]
        
        glow = self.theme.get("glow", (255, 223, 128))
        crystal = self.theme.get("crystal", (255, 200, 100))
        flame = self.theme.get("flame", (255, 165, 0))
        
        cx, cy = self.core_x, self.core_y
        
        # 爆炸扩张
        self.explosion_radius = int(400 * progress)
        
        # 生成冲击波
        if self.frame == 1:
            for i in range(4):
                self.shockwaves.append({
                    'radius': 0,
                    'max_radius': 350 + i * 50,
                    'speed': 20 + i * 3,
                    'alpha': 200 - i * 30,
                    'width': 8 - i
                })
        
        # 绘制冲击波
        for wave in self.shockwaves:
            wave['radius'] += wave['speed']
            if wave['radius'] < wave['max_radius']:
                wave_alpha = int(wave['alpha'] * (1 - wave['radius'] / wave['max_radius']))
                if wave_alpha > 0:
                    pygame.draw.circle(self.image, (*glow, wave_alpha),
                                     (cx, cy), int(wave['radius']), max(1, wave['width']))
        
        # 核心白光闪烁
        flash_alpha = int(255 * (1 - progress * 0.5))
        flash_radius = int(80 + 120 * progress)
        pygame.draw.circle(self.image, (255, 255, 255, flash_alpha), (cx, cy), flash_radius)
        pygame.draw.circle(self.image, (*glow, flash_alpha // 2), (cx, cy), flash_radius + 30)
        
        # 爆炸光芒
        num_rays = 24
        for i in range(num_rays):
            angle = i * (6.28 / num_rays) + self.frame * 0.1
            ray_length = self.explosion_radius * (0.8 + 0.4 * math.sin(angle * 3 + self.frame * 0.2))
            
            ex = cx + int(math.cos(angle) * ray_length)
            ey = cy + int(math.sin(angle) * ray_length)
            
            ray_width = int(8 * (1 - progress * 0.5))
            ray_alpha = int(200 * (1 - progress * 0.3))
            
            # 多层射线
            for layer in range(3):
                w = ray_width - layer * 2
                a = ray_alpha - layer * 50
                if w > 0 and a > 0:
                    pygame.draw.line(self.image, (*crystal, a), (cx, cy), (ex, ey), w)
        
        # 六芒星崩解
        if self.hexagram_size > 0:
            self.hexagram_size *= 1.15
            hex_alpha = int(150 * (1 - progress))
            size = self.hexagram_size
            rot = self.hexagram_rotation
            
            for tri_offset in [-math.pi / 2, math.pi / 2]:
                tri = []
                for i in range(3):
                    angle = rot + i * (6.28 / 3) + tri_offset
                    tri.append((
                        cx + int(math.cos(angle) * size),
                        cy + int(math.sin(angle) * size)
                    ))
                if hex_alpha > 10:
                    pygame.draw.polygon(self.image, (*glow, hex_alpha), tri, 2)
        
        # 大量爆炸粒子
        if self.frame <= 15:
            for _ in range(25):
                angle = random.uniform(0, 6.28)
                speed = random.uniform(8, 25)
                self._add_particle(
                    cx, cy,
                    math.cos(angle) * speed, math.sin(angle) * speed,
                    (255, random.randint(180, 255), random.randint(80, 180)),
                    random.randint(30, 60), random.randint(4, 10)
                )
        
        # 爆炸伤害
        if self.frame % 3 == 0:
            for mob in mobs:
                dist = math.hypot(mob.rect.centerx - cx, mob.rect.centery - cy)
                if dist < self.explosion_radius:
                    if hasattr(mob, 'take_damage'):
                        # 中心伤害更高
                        dmg_mult = 1.5 * (1 - dist / self.explosion_radius * 0.5)
                        mob.take_damage(self.damage * dmg_mult)
    
    def _phase3_stardust(self):
        """第三阶段：星尘余烬 - 星尘子弹散射"""
        progress = self.frame / self.phase_duration[2]
        
        glow = self.theme.get("glow", (255, 223, 128))
        crystal = self.theme.get("crystal", (255, 200, 100))
        flame = self.theme.get("flame", (255, 165, 0))
        
        cx, cy = self.core_x, self.core_y
        
        # 持续生成星尘子弹
        if self.frame % 4 == 0 and progress < 0.7:
            num_bullets = 8 if self.frame < 30 else 5
            for i in range(num_bullets):
                angle = random.uniform(0, 6.28)
                speed = random.uniform(4, 8)
                
                # 随机颜色变化
                color_choice = random.choice([glow, crystal, flame])
                
                self.stardust_bullets.append({
                    'x': cx + random.randint(-30, 30),
                    'y': cy + random.randint(-30, 30),
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'size': random.randint(8, 15),
                    'color': color_choice,
                    'rotation': random.uniform(0, 6.28),
                    'rot_speed': random.uniform(-0.1, 0.1),
                    'trail': [],
                    'alive': True,
                    'life': 120
                })
        
        # 更新和绘制星尘子弹
        for bullet in self.stardust_bullets[:]:
            if not bullet['alive']:
                self.stardust_bullets.remove(bullet)
                continue
            
            bullet['life'] -= 1
            if bullet['life'] <= 0:
                bullet['alive'] = False
                continue
            
            # 物理更新
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            bullet['rotation'] += bullet['rot_speed']
            
            # 轻微减速
            bullet['vx'] *= 0.995
            bullet['vy'] *= 0.995
            
            # 记录拖尾
            bullet['trail'].append((bullet['x'], bullet['y']))
            if len(bullet['trail']) > 10:
                bullet['trail'].pop(0)
            
            bx, by = int(bullet['x']), int(bullet['y'])
            size = bullet['size']
            color = bullet['color']
            life_ratio = bullet['life'] / 120
            
            # 绘制拖尾
            for i, (tx, ty) in enumerate(bullet['trail']):
                trail_progress = i / len(bullet['trail'])
                trail_alpha = int(100 * trail_progress * life_ratio)
                trail_size = int(size * 0.4 * trail_progress)
                if trail_size > 0:
                    pygame.draw.circle(self.image, (*color, trail_alpha),
                                     (int(tx), int(ty)), trail_size)
            
            # 子弹光晕
            glow_alpha = int(60 * life_ratio)
            pygame.draw.circle(self.image, (*color, glow_alpha), (bx, by), size + 5)
            
            # 子弹主体 - 星形
            star_points = []
            num_points = 5
            for i in range(num_points * 2):
                angle = bullet['rotation'] + i * (6.28 / (num_points * 2))
                r = size if i % 2 == 0 else size * 0.5
                star_points.append((
                    bx + int(math.cos(angle) * r),
                    by + int(math.sin(angle) * r)
                ))
            body_alpha = int(220 * life_ratio)
            pygame.draw.polygon(self.image, (*color, body_alpha), star_points)
            
            # 核心高光
            pygame.draw.circle(self.image, (255, 255, 240, int(255 * life_ratio)),
                             (bx, by), int(size * 0.3))
            
            # 边界检查
            if bx < -50 or bx > WIDTH + 50 or by < -50 or by > HEIGHT + 50:
                bullet['alive'] = False
                continue
            
            # 敌人碰撞检测
            for mob in mobs:
                dist = math.hypot(mob.rect.centerx - bx, mob.rect.centery - by)
                if dist < size + 20:
                    if hasattr(mob, 'take_damage'):
                        mob.take_damage(self.damage * 0.5)
                    bullet['alive'] = False
                    # 碰撞粒子
                    for _ in range(5):
                        self._add_particle(
                            bx, by,
                            random.uniform(-3, 3), random.uniform(-3, 3),
                            color, random.randint(10, 20), random.randint(2, 4)
                        )
                    break
        
        # 残余核心 - 渐渐消散
        if progress < 0.5:
            core_alpha = int(150 * (1 - progress * 2))
            core_size = int(50 * (1 - progress))
            if core_size > 5:
                pygame.draw.circle(self.image, (*flame, core_alpha), (cx, cy), core_size)
                pygame.draw.circle(self.image, (*glow, core_alpha // 2), (cx, cy), core_size + 15)
        
        # 背景星尘效果
        for _ in range(2):
            sx = random.randint(0, WIDTH)
            sy = random.randint(0, HEIGHT)
            self._add_particle(
                sx, sy, 0, 0,
                (255, 255, random.randint(200, 255)),
                random.randint(10, 25), random.randint(1, 3)
            )
    
    def _update_particles(self):
        """更新粒子"""
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= 0.98
            p['vy'] *= 0.98
            p['life'] -= 1
            
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            
            life_ratio = p['life'] / p['max_life']
            alpha = int(255 * life_ratio)
            size = max(1, int(p['size'] * (0.3 + 0.7 * life_ratio)))
            
            pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                             (int(p['x']), int(p['y'])), size)
            if size > 2:
                pygame.draw.circle(self.image, (*p['color'][:3], alpha // 3),
                                 (int(p['x']), int(p['y'])), size + 3)


# ===== 工厂函数 =====

def create_holy_shard(x, y, damage, angle=-90, owner=None, style="default"):
    """创建神圣碎片"""
    return HolyShardBullet(x, y, damage, angle, owner, style)

def create_profaned_spear(x, y, damage, angle=-90, owner=None, style="default"):
    """创建亵渎长矛"""
    return ProfanedSpearBullet(x, y, damage, angle, owner, style)

def create_healer_guardian(owner, style="default"):
    """创建治愈守卫"""
    return HealerGuardian(owner, style)

def create_cocoon_shield(owner, style="default"):
    """创建茧壳护盾"""
    return CocoonShield(owner, style)

def create_molten_rain(owner, damage, style="default", count=15):
    """创建熔融之雨"""
    return MoltenRainStorm(owner, damage, style)

def create_holy_ray(owner, damage, style="default"):
    """创建神圣射线"""
    return HolyRay(owner, damage, style)

def create_supernova(owner, damage, style="default"):
    """创建超新星爆发"""
    return SupernovaExplosion(owner, damage, style)


# ========== 子弹涂装预览渲染器 ==========

def render_providence_bullet_preview(surface, effects, color, center_x, center_y, size, x, y, plane_id=None):
    """
    渲染亵渎天神·普罗维登斯子弹预览效果
    根据涂装类型渲染不同形状的子弹预览
    
    Returns:
        bool: 如果渲染了效果返回True，否则False
    """
    # Providence相关effects列表
    providence_effects = [
        # 12种涂装的effects
        "holy_glow", "crystal_pulse",          # providence_holy_shard (default)
        "moonlight_glow", "star_scatter",      # providence_night_shard
        "bubble_rise", "deep_glow",            # providence_abyss_shard
        "rainbow_refract", "prism_glow",       # providence_crystal_shard
        "lava_crack", "ember_trail",           # providence_magma_shard
        "frost_glow", "ice_shatter",           # providence_frost_shard
        "void_distort", "dark_pulse",          # providence_void_shard
        "nature_glow", "petal_scatter",        # providence_nature_shard
        "lightning_arc", "storm_pulse",        # providence_storm_shard
        "blood_pulse", "crimson_trail",        # providence_blood_shard
        "royal_glow", "gem_sparkle",           # providence_gold_shard
        "aurora_flow", "rainbow_pulse",        # providence_aurora_shard
    ]
    
    has_providence_effect = any(effect in effects for effect in providence_effects)
    is_providence_plane = (plane_id == "providence")
    
    if not has_providence_effect and not is_providence_plane:
        return False
    
    t = pygame.time.get_ticks() / 1000.0
    bullet_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    cx, cy = size, size
    pulse = abs(math.sin(t * 3)) * 0.2 + 0.9
    
    # ===== 默认涂装 - 神圣菱形 =====
    if "holy_glow" in effects or "crystal_pulse" in effects or (is_providence_plane and not has_providence_effect):
        gold = (255, 215, 0)
        white = (255, 250, 220)
        
        # 外层光晕
        for i in range(3):
            glow_r = int((size // 3 + i * 4) * pulse)
            pygame.draw.circle(bullet_surf, (*gold, 80 - i * 20), (cx, cy), glow_r)
        
        # 菱形核心
        r = int(size // 4 * pulse)
        points = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        pygame.draw.polygon(bullet_surf, gold, points)
        pygame.draw.polygon(bullet_surf, white, points, 2)
        
        # 内部十字光芒
        pygame.draw.line(bullet_surf, white, (cx - r//2, cy), (cx + r//2, cy), 2)
        pygame.draw.line(bullet_surf, white, (cx, cy - r//2), (cx, cy + r//2), 2)
    
    # ===== 月夜涂装 - 新月形 =====
    elif "moonlight_glow" in effects or "star_scatter" in effects:
        night_purple = (80, 60, 120)
        moon_silver = (200, 200, 230)
        
        r = int(size // 4 * pulse)
        # 主圆
        pygame.draw.circle(bullet_surf, moon_silver, (cx, cy), r)
        # 遮挡圆形成新月
        pygame.draw.circle(bullet_surf, (0, 0, 0, 0), (cx + r//2, cy), int(r * 0.8))
        # 边缘光晕
        pygame.draw.circle(bullet_surf, (*night_purple, 100), (cx, cy), r + 4, 2)
        
        # 环绕星点
        for i in range(5):
            angle = t + i * math.pi * 2 / 5
            sx = cx + math.cos(angle) * (r + 8)
            sy = cy + math.sin(angle) * (r + 8)
            pygame.draw.circle(bullet_surf, moon_silver, (int(sx), int(sy)), 2)
    
    # ===== 深渊涂装 - 水滴形 =====
    elif "bubble_rise" in effects or "deep_glow" in effects:
        abyss_blue = (30, 50, 80)
        water_cyan = (100, 180, 200)
        
        r = int(size // 4 * pulse)
        # 水滴形状
        points = [
            (cx, cy - r),  # 顶点
            (cx + r * 0.6, cy + r * 0.3),
            (cx, cy + r),
            (cx - r * 0.6, cy + r * 0.3)
        ]
        pygame.draw.polygon(bullet_surf, water_cyan, [(int(p[0]), int(p[1])) for p in points])
        pygame.draw.polygon(bullet_surf, (200, 230, 255), [(int(p[0]), int(p[1])) for p in points], 2)
        
        # 气泡
        for i in range(3):
            by = cy + r - (t * 30 + i * 10) % (r * 2)
            bx = cx + math.sin(t + i) * 5
            pygame.draw.circle(bullet_surf, (*water_cyan, 150), (int(bx), int(by)), 3, 1)
    
    # ===== 水晶涂装 - 八面体棱镜 =====
    elif "rainbow_refract" in effects or "prism_glow" in effects:
        crystal_white = (220, 220, 240)
        r = int(size // 4 * pulse)
        
        # 八边形
        points = []
        for i in range(8):
            angle = i * math.pi / 4 + t * 0.5
            px = cx + math.cos(angle) * r
            py = cy + math.sin(angle) * r
            points.append((int(px), int(py)))
        pygame.draw.polygon(bullet_surf, crystal_white, points)
        
        # 彩虹折射线
        colors = [(255, 100, 100), (255, 255, 100), (100, 255, 100), (100, 100, 255)]
        for i, col in enumerate(colors):
            angle = t + i * math.pi / 2
            lx = cx + math.cos(angle) * r * 0.7
            ly = cy + math.sin(angle) * r * 0.7
            pygame.draw.line(bullet_surf, (*col, 150), (cx, cy), (int(lx), int(ly)), 2)
    
    # ===== 熔岩涂装 - 不规则熔岩块 =====
    elif "lava_crack" in effects or "ember_trail" in effects:
        lava_red = (180, 80, 30)
        lava_orange = (255, 150, 80)
        
        r = int(size // 4 * pulse)
        # 不规则多边形
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            dist = r * (0.8 + random.random() * 0.4) if i % 2 == 0 else r
            px = cx + math.cos(angle) * dist
            py = cy + math.sin(angle) * dist
            points.append((int(px), int(py)))
        pygame.draw.polygon(bullet_surf, lava_red, points)
        
        # 裂纹
        pygame.draw.line(bullet_surf, lava_orange, (cx - r//2, cy), (cx + r//2, cy - r//3), 2)
        pygame.draw.line(bullet_surf, lava_orange, (cx, cy - r//2), (cx - r//3, cy + r//2), 2)
    
    # ===== 霜冻涂装 - 六瓣雪花 =====
    elif "frost_glow" in effects or "ice_shatter" in effects:
        ice_blue = (180, 220, 255)
        ice_white = (240, 250, 255)
        
        r = int(size // 4 * pulse)
        # 六条放射线形成雪花
        for i in range(6):
            angle = i * math.pi / 3 + t * 0.3
            ex = cx + math.cos(angle) * r
            ey = cy + math.sin(angle) * r
            pygame.draw.line(bullet_surf, ice_white, (cx, cy), (int(ex), int(ey)), 2)
            # 分支
            bx = cx + math.cos(angle) * r * 0.6
            by = cy + math.sin(angle) * r * 0.6
            for j in [-0.3, 0.3]:
                branch_angle = angle + j
                bex = bx + math.cos(branch_angle) * r * 0.3
                bey = by + math.sin(branch_angle) * r * 0.3
                pygame.draw.line(bullet_surf, ice_blue, (int(bx), int(by)), (int(bex), int(bey)), 1)
        
        # 中心
        pygame.draw.circle(bullet_surf, ice_white, (cx, cy), 3)
    
    # ===== 虚空涂装 - 扭曲菱形 =====
    elif "void_distort" in effects or "dark_pulse" in effects:
        void_purple = (40, 20, 60)
        void_glow = (120, 80, 180)
        
        r = int(size // 4 * pulse)
        # 扭曲的菱形
        offset = math.sin(t * 5) * 3
        points = [
            (cx + offset, cy - r),
            (cx + r, cy + offset),
            (cx - offset, cy + r),
            (cx - r, cy - offset)
        ]
        pygame.draw.polygon(bullet_surf, void_purple, [(int(p[0]), int(p[1])) for p in points])
        pygame.draw.polygon(bullet_surf, void_glow, [(int(p[0]), int(p[1])) for p in points], 2)
        
        # 裂隙效果
        for i in range(3):
            rift_y = cy - r//2 + i * r//2
            pygame.draw.line(bullet_surf, void_glow, (cx - 3, int(rift_y)), (cx + 3, int(rift_y)), 1)
    
    # ===== 自然涂装 - 叶形 =====
    elif "nature_glow" in effects or "petal_scatter" in effects:
        leaf_green = (80, 140, 60)
        leaf_light = (150, 220, 100)
        
        r = int(size // 4 * pulse)
        # 叶形
        points = [
            (cx, cy - r),
            (cx + r * 0.5, cy - r * 0.3),
            (cx + r * 0.3, cy + r * 0.5),
            (cx, cy + r),
            (cx - r * 0.3, cy + r * 0.5),
            (cx - r * 0.5, cy - r * 0.3)
        ]
        pygame.draw.polygon(bullet_surf, leaf_green, [(int(p[0]), int(p[1])) for p in points])
        # 叶脉
        pygame.draw.line(bullet_surf, leaf_light, (cx, int(cy - r)), (cx, int(cy + r)), 2)
        pygame.draw.line(bullet_surf, leaf_light, (cx, cy), (int(cx + r * 0.4), int(cy - r * 0.2)), 1)
        pygame.draw.line(bullet_surf, leaf_light, (cx, cy), (int(cx - r * 0.4), int(cy - r * 0.2)), 1)
    
    # ===== 风暴涂装 - 雷电球 =====
    elif "lightning_arc" in effects or "storm_pulse" in effects:
        storm_gray = (100, 100, 150)
        lightning_white = (220, 220, 255)
        
        r = int(size // 4 * pulse)
        # 核心球
        pygame.draw.circle(bullet_surf, storm_gray, (cx, cy), r)
        pygame.draw.circle(bullet_surf, lightning_white, (cx, cy), r, 2)
        
        # 闪电弧
        for i in range(4):
            angle = t * 3 + i * math.pi / 2
            ex = cx + math.cos(angle) * (r + 6)
            ey = cy + math.sin(angle) * (r + 6)
            # Z字形闪电
            mid_x = cx + math.cos(angle) * (r + 3) + math.sin(t * 10) * 2
            mid_y = cy + math.sin(angle) * (r + 3)
            pygame.draw.line(bullet_surf, lightning_white, (int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)), 
                           (int(mid_x), int(mid_y)), 2)
            pygame.draw.line(bullet_surf, lightning_white, (int(mid_x), int(mid_y)), (int(ex), int(ey)), 2)
    
    # ===== 血月涂装 - 血滴 =====
    elif "blood_pulse" in effects or "crimson_trail" in effects:
        blood_red = (150, 30, 50)
        blood_dark = (100, 20, 30)
        
        r = int(size // 4 * pulse)
        # 血滴形状
        pygame.draw.circle(bullet_surf, blood_red, (cx, int(cy + r * 0.3)), int(r * 0.8))
        # 顶部尖角
        points = [(cx, cy - r), (cx + r * 0.5, int(cy + r * 0.3)), (cx - r * 0.5, int(cy + r * 0.3))]
        pygame.draw.polygon(bullet_surf, blood_red, [(int(p[0]), int(p[1])) for p in points])
        # 血丝
        for i in range(3):
            vein_y = cy - r * 0.3 + i * r * 0.4
            pygame.draw.line(bullet_surf, blood_dark, (int(cx - r * 0.3), int(vein_y)), 
                           (int(cx + r * 0.3), int(vein_y + 2)), 1)
    
    # ===== 黄金涂装 - 皇冠 =====
    elif "royal_glow" in effects or "gem_sparkle" in effects:
        gold = (255, 200, 50)
        gold_light = (255, 240, 180)
        
        r = int(size // 4 * pulse)
        # 皇冠底座
        pygame.draw.rect(bullet_surf, gold, (int(cx - r), int(cy), int(r * 2), int(r * 0.6)))
        # 三个尖角
        for i, offset in enumerate([-r * 0.6, 0, r * 0.6]):
            peak_x = int(cx + offset)
            pygame.draw.polygon(bullet_surf, gold, [
                (peak_x - r * 0.25, cy),
                (peak_x, int(cy - r * 0.8)),
                (int(peak_x + r * 0.25), cy)
            ])
        # 宝石
        gem_colors = [(255, 50, 50), (50, 255, 50), (50, 50, 255)]
        for i, col in enumerate(gem_colors):
            gx = int(cx - r * 0.6 + i * r * 0.6)
            pygame.draw.circle(bullet_surf, col, (gx, int(cy - r * 0.4)), 3)
    
    # ===== 极光涂装 - 流动菱形 =====
    elif "aurora_flow" in effects or "rainbow_pulse" in effects:
        r = int(size // 4 * pulse)
        
        # 多层渐变菱形
        aurora_colors = [
            (100, 255, 200),  # 青绿
            (150, 200, 255),  # 淡蓝
            (200, 150, 255),  # 淡紫
            (255, 200, 150),  # 橙粉
            (150, 255, 150),  # 淡绿
        ]
        
        for i, col in enumerate(aurora_colors):
            offset = (t + i * 0.3) % 1.0
            layer_r = r * (0.6 + offset * 0.4)
            alpha = int(150 * (1 - offset))
            points = [
                (cx, cy - layer_r),
                (cx + layer_r, cy),
                (cx, cy + layer_r),
                (cx - layer_r, cy)
            ]
            pygame.draw.polygon(bullet_surf, (*col, alpha), [(int(p[0]), int(p[1])) for p in points], 2)
        
        # 核心
        pygame.draw.circle(bullet_surf, (200, 255, 220), (cx, cy), r // 3)
    
    # 绘制到目标表面
    surface.blit(bullet_surf, (x - size // 2, y - size // 2))
    return True




