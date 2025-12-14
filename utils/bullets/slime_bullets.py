# -*- coding: utf-8 -*-
"""
末世星凝·史莱姆 - 专属子弹模块
星凝弹远程链式，重力域吸附叠层，凝胶子核链式追踪

特性：
- 星凝弹：1.4屏射程，命中后展开「重力域」
- 重力域：留场2.5s，持续吸扯+发射小星凝弹追踪
- 星凝debuff：远程易伤+10%，上限5层
- 凝胶分裂：满5层时爆炸生成凝胶子核再次展开小域

大招：
- 星凝暴雨：连续7道星凝域
- 重力漩涡：大范围减速+追踪弹+真伤爆炸
- 末世星坠：悬浮无敌+超大末世星域+双倍星凝核拾取
"""
import pygame
import math
import random
from config import all_sprites, mobs, WIDTH, HEIGHT, enemy_bullets, bullets

# ==================== 主题配色 ====================
SLIME_BULLET_THEMES = {
    "default": {
        "core": (120, 80, 200),        # 星凝紫
        "gel": (60, 140, 220),         # 凝胶蓝
        "pulse": (180, 120, 255),      # 脉冲亮紫
        "trail": (100, 160, 255),      # 轨迹蓝
        "domain": (150, 100, 230),     # 域场紫
        "star": (200, 180, 255),       # 星尘
    },
    "cosmic": {
        "core": (80, 40, 160),
        "gel": (40, 100, 180),
        "pulse": (150, 100, 255),
        "trail": (100, 150, 220),
        "domain": (120, 80, 200),
        "star": (200, 150, 255),
    },
    "void": {
        "core": (60, 30, 100),
        "gel": (30, 15, 60),
        "pulse": (100, 50, 180),
        "trail": (80, 40, 140),
        "domain": (80, 50, 130),
        "star": (180, 80, 255),
    },
    "crystal": {
        "core": (150, 180, 255),
        "gel": (180, 200, 255),
        "pulse": (220, 230, 255),
        "trail": (200, 220, 255),
        "domain": (170, 190, 255),
        "star": (240, 245, 255),
    },
    "toxic": {
        "core": (80, 200, 60),
        "gel": (60, 180, 40),
        "pulse": (160, 255, 100),
        "trail": (100, 220, 80),
        "domain": (100, 200, 70),
        "star": (180, 255, 120),
    },
    "royal": {
        "core": (140, 80, 180),
        "gel": (180, 100, 200),
        "pulse": (255, 200, 80),
        "trail": (200, 150, 255),
        "domain": (160, 100, 200),
        "star": (255, 215, 100),
    },
    "blood": {
        "core": (120, 20, 40),
        "gel": (80, 10, 30),
        "pulse": (255, 100, 120),
        "trail": (180, 40, 60),
        "domain": (140, 30, 50),
        "star": (255, 150, 170),
    },
    "ice": {
        "core": (150, 200, 255),
        "gel": (180, 220, 255),
        "pulse": (220, 240, 255),
        "trail": (200, 230, 255),
        "domain": (160, 210, 255),
        "star": (240, 250, 255),
    },
    "flame": {
        "core": (200, 80, 30),
        "gel": (180, 60, 20),
        "pulse": (255, 200, 100),
        "trail": (255, 150, 50),
        "domain": (220, 100, 40),
        "star": (255, 220, 150),
    },
    "phantom": {
        "core": (100, 150, 200),
        "gel": (120, 170, 220),
        "pulse": (180, 220, 255),
        "trail": (150, 200, 255),
        "domain": (130, 180, 230),
        "star": (200, 230, 255),
    },
    "rainbow": {
        "core": (200, 150, 255),
        "gel": (150, 200, 255),
        "pulse": (255, 200, 200),
        "trail": (200, 255, 200),
        "domain": (180, 180, 255),
        "star": (255, 255, 200),
    },
    "abyss": {
        "core": (50, 30, 80),
        "gel": (40, 20, 60),
        "pulse": (150, 100, 200),
        "trail": (100, 60, 140),
        "domain": (80, 50, 110),
        "star": (200, 150, 255),
    },
}


def get_theme(style):
    """获取主题配色"""
    return SLIME_BULLET_THEMES.get(style, SLIME_BULLET_THEMES["default"])


# ==================== 星凝弹（主武器）====================
class StarGelBullet(pygame.sprite.Sprite):
    """星凝弹 - 主武器，1.4屏射程，命中生成重力域"""
    
    def __init__(self, x, y, damage, owner=None, style="default"):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 1
        self.style = style
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 18
        self.max_range = HEIGHT * 1.4  # 1.4屏射程
        self.traveled = 0
        
        self.frame = 0
        self.angle = -math.pi / 2  # 向上
        
        # 轨迹粒子
        self.trail = []
        
        # 改为正方形以显示圆形凝胶球
        self.image = pygame.Surface((36, 36), pygame.SRCALPHA)
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
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        # 超出射程或出界
        if self.traveled > self.max_range or self.float_y < -60:
            self.kill()
            return
        
        # 命中检测
        self._check_hit()
        
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _check_hit(self):
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                mob.take_damage(self.damage)
                self._spawn_gravity_domain()
                self._spawn_hit_effect()
                self.kill()
                return
    
    def _spawn_gravity_domain(self):
        """命中时生成重力域"""
        domain = GravityDomain(self.float_x, self.float_y, self.owner, self.style)
        all_sprites.add(domain)
    
    def _spawn_hit_effect(self):
        effect = StarGelHitEffect(self.float_x, self.float_y, self.style)
        all_sprites.add(effect)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        core = theme["core"]
        gel = theme["gel"]
        pulse_col = theme["pulse"]
        star = theme["star"]
        
        # 36x36 正方形的中心
        cx, cy = 18, 18
        
        # 脉动效果
        pulse_scale = math.sin(self.frame * 0.4) * 0.15 + 1.0
        t = self.frame * 0.1
        
        # ========== 根据涂装渲染不同形状 ==========
        if self.style == "cosmic":
            # 星河漩涡 - 银河螺旋+星尘拖尾
            # 外层银河晕
            for i in range(4):
                glow_r = int((12 + i * 3) * pulse_scale)
                alpha = 100 - i * 20
                pygame.draw.circle(self.image, (*gel, alpha), (cx, cy), glow_r)
            
            # 螺旋星尘
            for arm in range(3):
                for seg in range(5):
                    prog = seg / 5
                    spiral_angle = t * 0.8 + arm * math.pi * 2 / 3 + prog * math.pi
                    spiral_r = 4 + prog * 8
                    sx = cx + math.cos(spiral_angle) * spiral_r * pulse_scale
                    sy = cy + math.sin(spiral_angle) * spiral_r * 0.7 * pulse_scale
                    seg_alpha = int(200 * (1 - prog * 0.5))
                    pygame.draw.circle(self.image, (*star, seg_alpha), (int(sx), int(sy)), 2)
            
            # 核心
            pygame.draw.circle(self.image, core, (cx, cy), int(7 * pulse_scale))
            pygame.draw.circle(self.image, pulse_col, (cx, cy), int(4 * pulse_scale))
            pygame.draw.circle(self.image, (255, 255, 255), (cx - 2, cy - 2), 2)
        
        elif self.style == "void":
            # 虚空引力 - 黑洞吸收+事件视界
            # 事件视界环
            for i in range(3):
                ev_r = int((10 + i * 4) * pulse_scale)
                ev_alpha = 80 - i * 20
                pygame.draw.circle(self.image, (*gel, ev_alpha), (cx, cy), ev_r, 2)
            
            # 虚空核心（黑洞）
            pygame.draw.circle(self.image, (20, 10, 40), (cx, cy), int(8 * pulse_scale))
            pygame.draw.circle(self.image, core, (cx, cy), int(6 * pulse_scale))
            
            # 吸入粒子
            for i in range(6):
                p_angle = t + i * math.pi / 3
                p_r = 12 + math.sin(t * 2 + i) * 3
                px = cx + math.cos(p_angle) * p_r
                py = cy + math.sin(p_angle) * p_r * 0.6
                pygame.draw.circle(self.image, (*pulse_col, 150), (int(px), int(py)), 2)
            
            # 虚空裂隙
            for i in range(4):
                rift_angle = i * math.pi / 2 + t * 0.5
                rx = cx + math.cos(rift_angle) * 5
                ry = cy + math.sin(rift_angle) * 5
                pygame.draw.line(self.image, (*star, 180), (cx, cy), (int(rx), int(ry)), 1)
        
        elif self.style == "crystal":
            # 水晶棱镜 - 六边形晶体+折射光
            # 棱镜光晕
            for i in range(3):
                prism_r = int((9 + i * 4) * pulse_scale)
                pygame.draw.circle(self.image, (*gel, 80 - i * 20), (cx, cy), prism_r)
            
            # 六边形晶体
            hex_r = int(8 * pulse_scale)
            hex_pts = []
            for i in range(6):
                angle = i * math.pi / 3 - math.pi / 6
                hx = cx + math.cos(angle) * hex_r
                hy = cy + math.sin(angle) * hex_r * 0.8
                hex_pts.append((int(hx), int(hy)))
            pygame.draw.polygon(self.image, core, hex_pts)
            pygame.draw.polygon(self.image, pulse_col, hex_pts, 1)
            
            # 折射彩光
            rainbow = [(255, 100, 100), (255, 200, 100), (100, 255, 150), 
                      (100, 200, 255), (150, 100, 255)]
            for i, col in enumerate(rainbow):
                ray_angle = t * 0.5 + i * math.pi * 2 / 5
                ray_len = 8 + math.sin(t + i) * 2
                rx = cx + math.cos(ray_angle) * ray_len
                ry = cy + math.sin(ray_angle) * ray_len
                pygame.draw.line(self.image, (*col, 150), (cx, cy), (int(rx), int(ry)), 2)
            
            # 中心亮点
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 3)
        
        elif self.style == "toxic":
            # 剧毒腐蚀 - 毒液滴落+腐蚀气泡
            # 毒雾光晕
            for i in range(3):
                toxic_r = int((10 + i * 4) * pulse_scale)
                pygame.draw.circle(self.image, (*gel, 70 - i * 18), (cx, cy), toxic_r)
            
            # 毒液主体（不规则）
            jiggle = math.sin(t * 0.8) * 2
            toxic_pts = [
                (cx, cy - int(10 * pulse_scale)),
                (cx + 6 + jiggle, cy - 3),
                (cx + 5, cy + 5),
                (cx, cy + int(8 * pulse_scale)),
                (cx - 5, cy + 5),
                (cx - 6 - jiggle, cy - 3),
            ]
            pygame.draw.polygon(self.image, core, [(int(p[0]), int(p[1])) for p in toxic_pts])
            
            # 腐蚀气泡
            for i in range(4):
                b_angle = t * 0.6 + i * math.pi / 2
                b_r = 8 + math.sin(t + i) * 2
                bx = cx + math.cos(b_angle) * b_r
                by = cy + math.sin(b_angle) * b_r * 0.7
                b_size = 2 + int(math.sin(t * 2 + i) > 0)
                pygame.draw.circle(self.image, pulse_col, (int(bx), int(by)), b_size)
            
            # 滴落效果
            drip_y = cy + 10 + abs(math.sin(t * 0.4)) * 5
            pygame.draw.circle(self.image, core, (cx, int(drip_y)), 2)
        
        elif self.style == "royal":
            # 皇室尊荣 - 皇冠形状+金光
            # 金色光晕
            for i in range(3):
                glow_r = int((10 + i * 4) * pulse_scale)
                pygame.draw.circle(self.image, (*gel, 80 - i * 20), (cx, cy), glow_r)
            
            # 皇冠形弹头
            crown_pts = [
                (cx, cy - int(12 * pulse_scale)),  # 顶尖
                (cx + 3, cy - 6),
                (cx + 6, cy - int(8 * pulse_scale)),  # 右尖
                (cx + 5, cy),
                (cx + 6, cy + 4),
                (cx, cy + 6),
                (cx - 6, cy + 4),
                (cx - 5, cy),
                (cx - 6, cy - int(8 * pulse_scale)),  # 左尖
                (cx - 3, cy - 6),
            ]
            pygame.draw.polygon(self.image, core, [(int(p[0]), int(p[1])) for p in crown_pts])
            pygame.draw.polygon(self.image, (255, 240, 150), [(int(p[0]), int(p[1])) for p in crown_pts], 1)
            
            # 宝石
            pygame.draw.circle(self.image, (255, 80, 120), (cx, cy - 3), 3)
            pygame.draw.circle(self.image, (255, 255, 255), (cx - 1, cy - 4), 1)
            
            # 金粒子
            for i in range(4):
                g_angle = t * 0.5 + i * math.pi / 2
                gx = cx + math.cos(g_angle) * 10
                gy = cy + math.sin(g_angle) * 6
                pygame.draw.circle(self.image, star, (int(gx), int(gy)), 2)
        
        elif self.style == "blood":
            # 血染凝核 - 血滴形状+脉动
            heartbeat = abs(math.sin(t * 0.5)) * 0.2
            
            # 血雾光晕
            for i in range(3):
                blood_r = int((10 + i * 4) * (pulse_scale + heartbeat))
                pygame.draw.circle(self.image, (*gel, 80 - i * 25), (cx, cy), blood_r)
            
            # 血滴形状
            drop_h = int(14 * (pulse_scale + heartbeat))
            drop_pts = [
                (cx, cy - drop_h),
                (cx + 7, cy),
                (cx + 5, cy + 5),
                (cx, cy + 7),
                (cx - 5, cy + 5),
                (cx - 7, cy),
            ]
            pygame.draw.polygon(self.image, core, [(int(p[0]), int(p[1])) for p in drop_pts])
            
            # 血管纹路
            for i in range(3):
                vein_angle = i * math.pi / 3 + 0.5
                vx = cx + math.cos(vein_angle) * 4
                vy = cy + math.sin(vein_angle) * 4
                pygame.draw.line(self.image, pulse_col, (cx, cy), (int(vx), int(vy)), 1)
            
            # 血珠高光
            pygame.draw.circle(self.image, (255, 200, 200), (cx - 2, cy - 3), 2)
        
        elif self.style == "ice":
            # 冰霜凝核 - 冰晶形状+霜雾
            # 冷雾光晕
            for i in range(4):
                frost_r = int((9 + i * 3) * pulse_scale)
                pygame.draw.circle(self.image, (*gel, 60 - i * 12), (cx, cy), frost_r)
            
            # 六角冰晶
            for layer in range(2):
                ice_r = int((7 - layer * 2) * pulse_scale)
                for i in range(6):
                    angle = i * math.pi / 3 + layer * math.pi / 6
                    ix = cx + math.cos(angle) * ice_r
                    iy = cy + math.sin(angle) * ice_r * 0.8
                    ix2 = cx + math.cos(angle) * (ice_r * 1.5)
                    iy2 = cy + math.sin(angle) * (ice_r * 1.5) * 0.8
                    col = core if layer == 0 else pulse_col
                    pygame.draw.line(self.image, col, (int(ix), int(iy)), (int(ix2), int(iy2)), 2)
            
            # 中心冰核
            pygame.draw.circle(self.image, core, (cx, cy), int(5 * pulse_scale))
            pygame.draw.circle(self.image, (255, 255, 255), (cx - 1, cy - 1), 2)
            
            # 飘散冰屑
            for i in range(3):
                f_phase = (t * 0.3 + i * 0.33) % 1.0
                fx = cx + (i - 1) * 5
                fy = cy - 5 - f_phase * 10
                pygame.draw.circle(self.image, (*star, int(200 * (1 - f_phase))), (int(fx), int(fy)), 1)
        
        elif self.style == "flame":
            # 炽焰凝核 - 火焰形状+余烬
            # 热浪光晕
            for i in range(3):
                flame_r = int((10 + i * 4) * pulse_scale)
                pygame.draw.circle(self.image, (*gel, 70 - i * 18), (cx, cy), flame_r)
            
            # 火焰形状
            wave = math.sin(t * 1.2) * 2
            flame_pts = [
                (cx, cy - int(14 * pulse_scale)),
                (cx + 4 + wave, cy - 8),
                (cx + 7, cy - 2),
                (cx + 5, cy + 4),
                (cx, cy + 6),
                (cx - 5, cy + 4),
                (cx - 7, cy - 2),
                (cx - 4 - wave, cy - 8),
            ]
            pygame.draw.polygon(self.image, core, [(int(p[0]), int(p[1])) for p in flame_pts])
            
            # 内焰
            inner_pts = [
                (cx, cy - 8),
                (cx + 3, cy - 2),
                (cx, cy + 2),
                (cx - 3, cy - 2),
            ]
            pygame.draw.polygon(self.image, pulse_col, [(int(p[0]), int(p[1])) for p in inner_pts])
            pygame.draw.polygon(self.image, (255, 255, 200), [(int(p[0]), int(p[1])) for p in inner_pts], 1)
            
            # 余烬粒子
            for i in range(3):
                e_phase = (t * 0.4 + i * 0.33) % 1.0
                ex = cx + (i - 1) * 4 + math.sin(t + i) * 2
                ey = cy - 5 - e_phase * 12
                pygame.draw.circle(self.image, (*star, int(200 * (1 - e_phase))), (int(ex), int(ey)), 2)
        
        elif self.style == "phantom":
            # 幽魂凝胶 - 透明飘忽+魂火
            ghost_alpha = int(150 + 50 * math.sin(t * 0.5))
            
            # 以太光晕
            for i in range(3):
                ether_r = int((10 + i * 4) * pulse_scale)
                pygame.draw.circle(self.image, (*gel, max(10, 60 - i * 15 - (255 - ghost_alpha) // 5)), 
                                 (cx, cy), ether_r)
            
            # 幽魂主体
            pygame.draw.ellipse(self.image, (*core, ghost_alpha), 
                              (cx - 7, cy - 9, 14, 18))
            pygame.draw.ellipse(self.image, (*pulse_col, ghost_alpha // 2), 
                              (cx - 5, cy - 7, 10, 12))
            
            # 魂火飘散
            for i in range(4):
                s_angle = t * 0.4 + i * math.pi / 2
                sx = cx + math.cos(s_angle) * (8 + math.sin(t + i) * 2)
                sy = cy + math.sin(s_angle) * 5
                pygame.draw.circle(self.image, (*star, ghost_alpha // 2), (int(sx), int(sy)), 2)
            
            # 透明核心
            pygame.draw.circle(self.image, (255, 255, 255, ghost_alpha // 2), (cx - 2, cy - 3), 2)
        
        elif self.style == "rainbow":
            # 彩虹凝核 - 七彩循环+棱镜
            rainbow_cols = [
                (255, 80, 80), (255, 160, 60), (255, 240, 80),
                (80, 255, 130), (80, 180, 255), (130, 100, 255), (200, 100, 255)
            ]
            color_idx = int(t * 2) % 7
            
            # 彩虹光晕
            for i in range(3):
                r_col = rainbow_cols[(color_idx + i) % 7]
                glow_r = int((9 + i * 3) * pulse_scale)
                pygame.draw.circle(self.image, (*r_col, 80 - i * 20), (cx, cy), glow_r)
            
            # 七彩核心（分层）
            for i, col in enumerate(rainbow_cols):
                layer_h = 2
                layer_y = cy - 7 + i * 2
                pygame.draw.rect(self.image, col, (cx - 5, int(layer_y), 10, layer_h + 1))
            
            # 棱镜光芒
            for i in range(7):
                ray_angle = t * 0.3 + i * math.pi * 2 / 7
                ray_len = 10 + math.sin(t + i) * 2
                rx = cx + math.cos(ray_angle) * ray_len
                ry = cy + math.sin(ray_angle) * ray_len * 0.6
                pygame.draw.line(self.image, rainbow_cols[i], (cx, cy), (int(rx), int(ry)), 1)
            
            # 白光核心
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 3)
        
        elif self.style == "abyss":
            # 深渊星陨 - 末世裂隙+流星尾
            # 末世光晕
            for i in range(3):
                doom_r = int((10 + i * 4) * pulse_scale)
                pygame.draw.circle(self.image, (*gel, 60 - i * 15), (cx, cy), doom_r)
            
            # 裂隙核心
            pygame.draw.circle(self.image, (20, 10, 40), (cx, cy), int(8 * pulse_scale))
            pygame.draw.circle(self.image, core, (cx, cy), int(6 * pulse_scale))
            
            # 次元裂隙
            for i in range(5):
                crack_angle = t * 0.3 + i * math.pi * 2 / 5
                jitter = math.sin(t * 2 + i) * 2
                cx1 = cx + math.cos(crack_angle) * 3
                cy1 = cy + math.sin(crack_angle) * 3
                cx2 = cx + math.cos(crack_angle) * (8 + jitter)
                cy2 = cy + math.sin(crack_angle) * (6 + jitter) * 0.7
                pygame.draw.line(self.image, pulse_col, (int(cx1), int(cy1)), (int(cx2), int(cy2)), 2)
            
            # 流星尾迹
            for i in range(4):
                trail_y = cy + 5 + i * 4
                trail_alpha = 150 - i * 35
                trail_r = 4 - i
                if trail_r > 0 and trail_alpha > 0:
                    pygame.draw.circle(self.image, (*star, trail_alpha), (cx, int(trail_y)), trail_r)
            
            # 末世脉冲
            if int(t * 3) % 10 < 3:
                pygame.draw.circle(self.image, (*star, 100), (cx, cy), int(12 * pulse_scale), 1)
        
        else:
            # 默认 - 星凝紫基础形态
            # 外层光晕
            for i in range(3):
                glow_r = int((10 + i * 4) * pulse_scale)
                alpha = 80 - i * 20
                pygame.draw.circle(self.image, (*gel, alpha), (cx, cy), glow_r)
            
            # 核心
            core_r = int(8 * pulse_scale)
            pygame.draw.circle(self.image, core, (cx, cy), core_r)
            pygame.draw.circle(self.image, pulse_col, (cx, cy), core_r - 3)
            
            # 高光
            pygame.draw.circle(self.image, (255, 255, 255, 200), (cx - 3, cy - 3), 3)
            
            # 星芒
            for i in range(4):
                angle = i * math.pi / 2 + self.frame * 0.1
                ray_len = 6 + int(pulse_scale * 2)
                rx = cx + math.cos(angle) * ray_len
                ry = cy + math.sin(angle) * ray_len
                pygame.draw.line(self.image, (*star, 180), (cx, cy), (int(rx), int(ry)), 2)
            
            # 尖端
            tip_pts = [
                (cx, cy - int(12 * pulse_scale)),
                (cx - 4, cy - 5),
                (cx + 4, cy - 5),
            ]
            pygame.draw.polygon(self.image, pulse_col, tip_pts)


# ==================== 重力域（留场实体）====================
class GravityDomain(pygame.sprite.Sprite):
    """重力域 - 留场2.5s，吸扯敌人+发射小星凝弹+叠加debuff"""
    
    def __init__(self, x, y, owner=None, style="default", is_small=False, chain_count=0):
        super().__init__()
        self.owner = owner
        self.is_enemy = False
        self.damage = 0
        self.style = style
        self.is_small = is_small  # 凝胶子核生成的小域
        self.chain_count = chain_count  # 链式层数（最多2次）
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        # 生命周期
        self.lifetime = 120 if is_small else 150  # 小域2秒，大域2.5秒
        self.frame = 0
        self.active = True
        self.exploded = False
        
        # 吸扯范围
        self.pull_radius = 80 if is_small else 120
        self.pull_strength = 2.0 if is_small else 2.5
        
        # 小星凝弹发射
        self.shot_timer = 0
        self.shot_interval = 25 if is_small else 30
        
        # 旋转和粒子
        self.rotation = 0
        self.particles = []
        
        # 标记的敌人debuff层数
        self.marked_enemies = {}  # enemy_id: layer_count
        
        # 注册到owner
        if owner and hasattr(owner, 'active_domains'):
            owner.active_domains.append(self)
        
        size = 120 if is_small else 180
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self._explode()
            return
        
        if not self.active:
            return
        
        self.rotation += 0.1
        
        # 吸扯敌人并叠加debuff
        self._pull_and_mark_enemies()
        
        # 发射小星凝弹
        self.shot_timer += 1
        if self.shot_timer >= self.shot_interval:
            self.shot_timer = 0
            self._fire_mini_star()
        
        # 更新粒子
        self._update_particles()
        
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _pull_and_mark_enemies(self):
        """吸扯范围内敌人并叠加星凝debuff"""
        for enemy in mobs:
            dx = self.float_x - enemy.rect.centerx
            dy = self.float_y - enemy.rect.centery
            dist = math.hypot(dx, dy)
            
            if dist < self.pull_radius and dist > 10:
                # 吸扯
                pull_x = (dx / dist) * self.pull_strength
                pull_y = (dy / dist) * self.pull_strength
                enemy.rect.x += int(pull_x)
                enemy.rect.y += int(pull_y)
                
                # 叠加星凝debuff（每秒叠1层）
                enemy_id = id(enemy)
                if self.frame % 60 == 0:  # 每秒
                    current = self.marked_enemies.get(enemy_id, 0)
                    if current < 5:
                        self.marked_enemies[enemy_id] = current + 1
                        # 应用易伤效果到敌人
                        if hasattr(enemy, 'star_gel_debuff'):
                            enemy.star_gel_debuff = min(5, enemy.star_gel_debuff + 1)
                        else:
                            enemy.star_gel_debuff = 1
                        enemy.star_gel_debuff_timer = 180  # 3秒刷新
    
    def _fire_mini_star(self):
        """发射小星凝弹追踪"""
        target = None
        min_dist = float('inf')
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x,
                            enemy.rect.centery - self.float_y)
            if dist < 250 and dist < min_dist:
                min_dist = dist
                target = enemy
        
        if target:
            angle = math.atan2(target.rect.centery - self.float_y,
                             target.rect.centerx - self.float_x)
        else:
            angle = -math.pi / 2 + random.uniform(-0.5, 0.5)
        
        damage = (self.owner.damage * 0.3 if self.owner else 8) * (0.7 if self.is_small else 1.0)
        mini = MiniStarGelBullet(self.float_x, self.float_y - 20, damage, self.owner, self.style, angle)
        all_sprites.add(mini)
    
    def activate_explosion(self):
        """玩家再次普攻触发爆炸"""
        if self.exploded:
            return
        self._explode(activated=True)
    
    def _explode(self, activated=False):
        """爆炸"""
        if self.exploded:
            return
        self.exploded = True
        self.active = False
        
        # 爆炸真伤
        damage = (self.owner.damage * 1.2 if self.owner else 30) * (0.6 if self.is_small else 1.0)
        max_debuff_enemy = None
        max_debuff = 0
        
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x,
                            enemy.rect.centery - self.float_y)
            if dist < self.pull_radius * 1.2:
                enemy.take_damage(damage, true_damage=True)
                
                # 检查是否有满层debuff敌人
                enemy_id = id(enemy)
                debuff_count = self.marked_enemies.get(enemy_id, 0)
                if hasattr(enemy, 'star_gel_debuff'):
                    debuff_count = max(debuff_count, enemy.star_gel_debuff)
                if debuff_count > max_debuff:
                    max_debuff = debuff_count
                    max_debuff_enemy = enemy
        
        # 满5层时生成凝胶子核
        if max_debuff >= 5 and self.chain_count < 2 and not self.is_small:
            self._spawn_gel_cores()
        
        # 掉落星凝核拾取物
        pickup = StarGelPickup(self.float_x, self.float_y, self.owner)
        all_sprites.add(pickup)
        
        # 爆炸特效
        effect = DomainExplosion(self.float_x, self.float_y, self.style, self.is_small)
        all_sprites.add(effect)
        
        # 从owner移除
        if self.owner and hasattr(self.owner, 'active_domains'):
            if self in self.owner.active_domains:
                self.owner.active_domains.remove(self)
        
        self.kill()
    
    def _spawn_gel_cores(self):
        """生成3枚凝胶子核"""
        for i in range(3):
            angle = i * math.pi * 2 / 3 + random.uniform(-0.3, 0.3)
            dist = 50
            cx = self.float_x + math.cos(angle) * dist
            cy = self.float_y + math.sin(angle) * dist
            
            core = GelCoreBullet(cx, cy, self.owner, self.style, self.chain_count + 1)
            all_sprites.add(core)
    
    def _update_particles(self):
        """星凝粒子"""
        if self.frame % 4 == 0:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(self.pull_radius * 0.5, self.pull_radius)
            self.particles.append({
                'x': math.cos(angle) * dist,
                'y': math.sin(angle) * dist,
                'vx': -math.cos(angle) * 1.5,
                'vy': -math.sin(angle) * 1.5,
                'life': random.randint(20, 35),
                'size': random.uniform(2, 5)
            })
        
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        domain = theme["domain"]
        core = theme["core"]
        gel = theme["gel"]
        star = theme["star"]
        pulse = theme["pulse"]
        
        size = self.image.get_width()
        cx, cy = size // 2, size // 2
        t = self.frame * 0.1
        
        # ========== 根据涂装渲染不同域效果 ==========
        if self.style == "cosmic":
            # 星河漩涡域 - 银河螺旋
            for arm in range(8):
                arm_offset = arm * math.pi / 4 + self.rotation
                for seg in range(15):
                    prog = seg / 15
                    spiral_angle = arm_offset + prog * math.pi * 2
                    spiral_r = self.pull_radius * 0.2 + self.pull_radius * 0.8 * prog
                    sx = cx + math.cos(spiral_angle) * spiral_r
                    sy = cy + math.sin(spiral_angle) * spiral_r
                    alpha = int(140 * (1 - prog * 0.5))
                    r = int(5 * (1 - prog * 0.4))
                    if r > 0:
                        pygame.draw.circle(self.image, (*domain, alpha), (int(sx), int(sy)), r)
            
            # 银河光环
            for i in range(4):
                ring_r = int(self.pull_radius - i * 10)
                pygame.draw.circle(self.image, (*gel, 60 - i * 12), (cx, cy), ring_r, 2)
            
            # 脉冲星核心
            core_pulse = abs(math.sin(t * 1.5)) * 0.4 + 0.6
            core_r = int(22 * core_pulse) if not self.is_small else int(16 * core_pulse)
            pygame.draw.circle(self.image, core, (cx, cy), core_r)
            pygame.draw.circle(self.image, pulse, (cx, cy), core_r - 5)
            pygame.draw.circle(self.image, (255, 255, 255), (cx - 4, cy - 4), core_r // 4)
        
        elif self.style == "void":
            # 虚空引力域 - 黑洞吸收
            # 事件视界
            for i in range(5):
                ev_r = int(self.pull_radius - i * 12)
                ev_alpha = 100 - i * 18
                pygame.draw.circle(self.image, (*gel, ev_alpha), (cx, cy), ev_r, 3)
            
            # 吸入漩涡
            for arm in range(6):
                arm_offset = arm * math.pi / 3 + self.rotation * 1.5
                for seg in range(10):
                    prog = seg / 10
                    spiral_angle = arm_offset + prog * math.pi * 1.2
                    spiral_r = self.pull_radius * (1 - prog * 0.8)
                    sx = cx + math.cos(spiral_angle) * spiral_r
                    sy = cy + math.sin(spiral_angle) * spiral_r
                    pygame.draw.circle(self.image, (*domain, int(150 * prog)), (int(sx), int(sy)), 3)
            
            # 黑洞核心
            core_r = 25 if not self.is_small else 18
            pygame.draw.circle(self.image, (15, 8, 30), (cx, cy), core_r)
            pygame.draw.circle(self.image, core, (cx, cy), core_r, 3)
            pygame.draw.circle(self.image, pulse, (cx, cy), core_r // 2)
        
        elif self.style == "crystal":
            # 水晶棱镜域 - 六边形晶格
            # 棱镜光环
            for i in range(4):
                prism_r = int(self.pull_radius - i * 15)
                pygame.draw.circle(self.image, (*gel, 70 - i * 15), (cx, cy), prism_r, 2)
            
            # 晶格结构
            for ring in range(3):
                ring_r = self.pull_radius * (0.3 + ring * 0.25)
                for i in range(6):
                    angle = i * math.pi / 3 + self.rotation + ring * 0.1
                    hx = cx + math.cos(angle) * ring_r
                    hy = cy + math.sin(angle) * ring_r
                    pygame.draw.circle(self.image, (*domain, 150 - ring * 30), (int(hx), int(hy)), 5 - ring)
                    # 连线
                    next_angle = (i + 1) * math.pi / 3 + self.rotation + ring * 0.1
                    nx = cx + math.cos(next_angle) * ring_r
                    ny = cy + math.sin(next_angle) * ring_r
                    pygame.draw.line(self.image, (*domain, 100 - ring * 25), 
                                   (int(hx), int(hy)), (int(nx), int(ny)), 2)
            
            # 棱镜核心
            core_r = 20 if not self.is_small else 14
            pygame.draw.circle(self.image, core, (cx, cy), core_r)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), core_r // 2)
        
        elif self.style == "toxic":
            # 剧毒腐蚀域 - 毒气扩散
            # 毒雾层
            for i in range(5):
                toxic_r = int(self.pull_radius - i * 12 + math.sin(t + i) * 5)
                pygame.draw.circle(self.image, (*gel, 50 - i * 8), (cx, cy), toxic_r)
            
            # 毒泡漂浮
            for i in range(12):
                b_angle = self.rotation + i * math.pi / 6
                b_r = self.pull_radius * (0.4 + 0.5 * abs(math.sin(t + i * 0.5)))
                bx = cx + math.cos(b_angle) * b_r
                by = cy + math.sin(b_angle) * b_r
                b_size = 4 + int(math.sin(t * 2 + i) * 2)
                pygame.draw.circle(self.image, (*domain, 150), (int(bx), int(by)), b_size)
                pygame.draw.circle(self.image, (*pulse, 100), (int(bx), int(by)), b_size, 1)
            
            # 毒核
            core_r = 22 if not self.is_small else 16
            pygame.draw.circle(self.image, core, (cx, cy), core_r)
            pygame.draw.circle(self.image, pulse, (cx, cy), core_r - 6)
        
        elif self.style == "royal":
            # 皇室尊荣域 - 金光普照
            # 金色光环
            for i in range(4):
                ring_r = int(self.pull_radius - i * 12)
                pygame.draw.circle(self.image, (*gel, 80 - i * 15), (cx, cy), ring_r, 3)
            
            # 皇家光芒
            for i in range(8):
                ray_angle = self.rotation + i * math.pi / 4
                ray_len = self.pull_radius * 0.9
                rx = cx + math.cos(ray_angle) * ray_len
                ry = cy + math.sin(ray_angle) * ray_len
                pygame.draw.line(self.image, (*domain, 120), (cx, cy), (int(rx), int(ry)), 3)
            
            # 金粒子环绕
            for i in range(10):
                g_angle = self.rotation * 0.8 + i * math.pi / 5
                g_r = self.pull_radius * 0.6
                gx = cx + math.cos(g_angle) * g_r
                gy = cy + math.sin(g_angle) * g_r
                pygame.draw.circle(self.image, star, (int(gx), int(gy)), 4)
            
            # 皇冠核心
            core_r = 24 if not self.is_small else 17
            pygame.draw.circle(self.image, core, (cx, cy), core_r)
            pygame.draw.circle(self.image, (255, 240, 150), (cx - 5, cy - 5), core_r // 3)
        
        elif self.style == "blood":
            # 血染凝核域 - 血浪脉动
            heartbeat = abs(math.sin(t * 0.8))
            
            # 血浪扩散
            for i in range(4):
                wave_r = int((self.pull_radius - i * 15) * (1 + heartbeat * 0.1))
                pygame.draw.circle(self.image, (*gel, 70 - i * 15), (cx, cy), wave_r, 3)
            
            # 血脉纹路
            for i in range(6):
                vein_angle = self.rotation * 0.5 + i * math.pi / 3
                for seg in range(8):
                    prog = seg / 8
                    vx = cx + math.cos(vein_angle) * self.pull_radius * prog * 0.85
                    vy = cy + math.sin(vein_angle) * self.pull_radius * prog * 0.85
                    pygame.draw.circle(self.image, (*domain, int(180 * (1 - prog * 0.5))), 
                                     (int(vx), int(vy)), 3 - int(prog * 2))
            
            # 心脏核心
            core_r = int(22 * (1 + heartbeat * 0.15)) if not self.is_small else int(16 * (1 + heartbeat * 0.15))
            pygame.draw.circle(self.image, core, (cx, cy), core_r)
            pygame.draw.circle(self.image, pulse, (cx, cy), core_r - 5)
        
        elif self.style == "ice":
            # 冰霜凝核域 - 冰晶扩散
            # 冷雾
            for i in range(4):
                frost_r = int(self.pull_radius - i * 12)
                pygame.draw.circle(self.image, (*gel, 50 - i * 10), (cx, cy), frost_r)
            
            # 冰晶结构
            for ring in range(2):
                ring_r = self.pull_radius * (0.5 + ring * 0.35)
                for i in range(6):
                    angle = i * math.pi / 3 + self.rotation * 0.5
                    ix = cx + math.cos(angle) * ring_r
                    iy = cy + math.sin(angle) * ring_r
                    # 六角星
                    for j in range(6):
                        spike_angle = j * math.pi / 3
                        spike_len = 8 - ring * 3
                        sx = ix + math.cos(spike_angle) * spike_len
                        sy = iy + math.sin(spike_angle) * spike_len
                        pygame.draw.line(self.image, (*domain, 180 - ring * 40), 
                                       (int(ix), int(iy)), (int(sx), int(sy)), 2)
            
            # 冰核
            core_r = 20 if not self.is_small else 14
            pygame.draw.circle(self.image, core, (cx, cy), core_r)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), core_r // 2)
        
        elif self.style == "flame":
            # 炽焰凝核域 - 火焰漩涡
            # 热浪
            for i in range(4):
                heat_r = int(self.pull_radius - i * 10 + math.sin(t * 2 + i) * 5)
                pygame.draw.circle(self.image, (*gel, 60 - i * 12), (cx, cy), heat_r)
            
            # 火焰臂
            for arm in range(6):
                arm_offset = arm * math.pi / 3 + self.rotation * 1.2
                for seg in range(10):
                    prog = seg / 10
                    flame_angle = arm_offset + prog * 0.8
                    flame_r = self.pull_radius * (0.3 + prog * 0.65)
                    fx = cx + math.cos(flame_angle) * flame_r
                    fy = cy + math.sin(flame_angle) * flame_r
                    f_size = int(6 * (1 - prog * 0.5))
                    pygame.draw.circle(self.image, (*domain, int(180 * (1 - prog * 0.4))), 
                                     (int(fx), int(fy)), f_size)
            
            # 炎核
            core_r = 22 if not self.is_small else 16
            pygame.draw.circle(self.image, core, (cx, cy), core_r)
            pygame.draw.circle(self.image, (255, 255, 200), (cx, cy), core_r // 2)
        
        elif self.style == "phantom":
            # 幽魂凝胶域 - 灵魂漩涡
            ghost_alpha = int(100 + 50 * math.sin(t * 0.5))
            
            # 以太场
            for i in range(4):
                ether_r = int(self.pull_radius - i * 12)
                pygame.draw.circle(self.image, (*gel, max(20, ghost_alpha // 2 - i * 10)), (cx, cy), ether_r)
            
            # 魂火环绕
            for i in range(8):
                soul_angle = self.rotation + i * math.pi / 4
                soul_r = self.pull_radius * 0.65 + math.sin(t + i) * 10
                sx = cx + math.cos(soul_angle) * soul_r
                sy = cy + math.sin(soul_angle) * soul_r
                pygame.draw.circle(self.image, (*domain, ghost_alpha), (int(sx), int(sy)), 6)
                pygame.draw.circle(self.image, (*star, ghost_alpha // 2), (int(sx), int(sy)), 3)
            
            # 魂核
            core_r = 20 if not self.is_small else 14
            pygame.draw.circle(self.image, (*core, ghost_alpha), (cx, cy), core_r)
            pygame.draw.circle(self.image, (*pulse, ghost_alpha), (cx, cy), core_r - 5)
        
        elif self.style == "rainbow":
            # 彩虹凝核域 - 七彩漩涡
            rainbow = [(255, 80, 80), (255, 160, 60), (255, 240, 80),
                      (80, 255, 130), (80, 180, 255), (130, 100, 255), (200, 100, 255)]
            
            # 彩虹光环
            for i, col in enumerate(rainbow):
                ring_r = int(self.pull_radius - i * 10)
                pygame.draw.circle(self.image, (*col, 100), (cx, cy), ring_r, 3)
            
            # 彩虹螺旋
            for arm in range(7):
                arm_offset = arm * math.pi * 2 / 7 + self.rotation
                col = rainbow[arm]
                for seg in range(10):
                    prog = seg / 10
                    spiral_angle = arm_offset + prog * math.pi * 1.5
                    spiral_r = self.pull_radius * 0.25 + self.pull_radius * 0.7 * prog
                    sx = cx + math.cos(spiral_angle) * spiral_r
                    sy = cy + math.sin(spiral_angle) * spiral_r
                    pygame.draw.circle(self.image, (*col, int(200 * (1 - prog * 0.5))), 
                                     (int(sx), int(sy)), 4)
            
            # 白光核心
            core_r = 22 if not self.is_small else 16
            color_idx = int(t * 2) % 7
            pygame.draw.circle(self.image, rainbow[color_idx], (cx, cy), core_r)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), core_r // 2)
        
        elif self.style == "abyss":
            # 深渊星陨域 - 末世裂隙
            # 末世压迫
            for i in range(5):
                doom_r = int(self.pull_radius - i * 10)
                pygame.draw.circle(self.image, (*gel, 60 - i * 10), (cx, cy), doom_r)
            
            # 次元裂隙
            for i in range(8):
                crack_angle = self.rotation * 0.6 + i * math.pi / 4
                crack_len = self.pull_radius * 0.9
                points = [(cx, cy)]
                for seg in range(5):
                    prog = (seg + 1) / 5
                    jitter = math.sin(t * 2 + i + seg) * 8 * prog
                    px = cx + math.cos(crack_angle) * crack_len * prog + jitter
                    py = cy + math.sin(crack_angle) * crack_len * prog
                    points.append((int(px), int(py)))
                pygame.draw.lines(self.image, (*domain, 150), False, points, 2)
            
            # 流星粒子
            for i in range(10):
                m_angle = self.rotation + i * math.pi / 5
                m_r = self.pull_radius * 0.5 + math.sin(t + i) * 15
                mx = cx + math.cos(m_angle) * m_r
                my = cy + math.sin(m_angle) * m_r
                pygame.draw.circle(self.image, star, (int(mx), int(my)), 3)
            
            # 末世核心
            core_r = 24 if not self.is_small else 17
            pygame.draw.circle(self.image, (20, 10, 40), (cx, cy), core_r)
            pygame.draw.circle(self.image, core, (cx, cy), core_r, 3)
            pygame.draw.circle(self.image, pulse, (cx, cy), core_r // 2)
        
        else:
            # 默认 - 星凝域
            # 外层漩涡
            for arm in range(6):
                arm_offset = arm * math.pi / 3 + self.rotation
                for seg in range(12):
                    prog = seg / 12
                    spiral_angle = arm_offset + prog * math.pi * 1.5
                    spiral_r = self.pull_radius * 0.3 + self.pull_radius * 0.7 * prog
                    sx = cx + math.cos(spiral_angle) * spiral_r
                    sy = cy + math.sin(spiral_angle) * spiral_r
                    alpha = int(120 * (1 - prog * 0.6))
                    r = int(4 * (1 - prog * 0.5))
                    if r > 0:
                        pygame.draw.circle(self.image, (*domain, alpha), (int(sx), int(sy)), r)
            
            # 吸引场边界
            for i in range(3):
                ring_r = int(self.pull_radius - i * 8)
                ring_alpha = 80 - i * 20
                pygame.draw.circle(self.image, (*gel, ring_alpha), (cx, cy), ring_r, 2)
            
            # 核心脉动
            core_pulse = abs(math.sin(t * 1.5)) * 0.3 + 0.7
            core_r = int(20 * core_pulse) if not self.is_small else int(14 * core_pulse)
            pygame.draw.circle(self.image, core, (cx, cy), core_r)
            pygame.draw.circle(self.image, pulse, (cx, cy), core_r - 4)
            pygame.draw.circle(self.image, (255, 255, 255, 180), (cx - 5, cy - 5), core_r // 3)
        
        # 通用星凝粒子
        for p in self.particles:
            px = cx + p['x']
            py = cy + p['y']
            if 0 <= px < size and 0 <= py < size:
                p_alpha = int(200 * p['life'] / 35)
                pygame.draw.circle(self.image, (*star, p_alpha),
                                 (int(px), int(py)), int(p['size']))


# ==================== 小星凝弹追踪 ====================
class MiniStarGelBullet(pygame.sprite.Sprite):
    """小星凝弹 - 追踪弹"""
    
    def __init__(self, x, y, damage, owner=None, style="default", angle=-math.pi/2):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.is_enemy = False
        self.piercing = 1
        self.style = style
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = angle
        self.speed = 9
        self.turn_rate = 0.07
        
        self.frame = 0
        self.lifetime = 100
        
        self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0 or self.float_y < -20 or self.float_y > HEIGHT + 20:
            self.kill()
            return
        
        # 追踪
        target = self._find_target()
        if target:
            tx, ty = target.rect.center
            target_angle = math.atan2(ty - self.float_y, tx - self.float_x)
            angle_diff = target_angle - self.angle
            while angle_diff > math.pi: angle_diff -= math.pi * 2
            while angle_diff < -math.pi: angle_diff += math.pi * 2
            self.angle += max(-self.turn_rate, min(self.turn_rate, angle_diff))
        
        # 移动
        self.float_x += math.cos(self.angle) * self.speed
        self.float_y += math.sin(self.angle) * self.speed
        
        # 命中检测
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                # 应用星凝易伤
                actual_damage = self.damage
                if hasattr(mob, 'star_gel_debuff') and mob.star_gel_debuff > 0:
                    actual_damage *= (1 + mob.star_gel_debuff * 0.1)  # 每层+10%
                mob.take_damage(actual_damage)
                self.kill()
                return
        
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _find_target(self):
        min_dist = 180
        target = None
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x,
                            enemy.rect.centery - self.float_y)
            if dist < min_dist:
                min_dist = dist
                target = enemy
        return target
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        core = theme["core"]
        pulse = theme["pulse"]
        star = theme["star"]
        gel = theme["gel"]
        
        cx, cy = 7, 7
        t = self.frame * 0.15
        
        # ========== 根据涂装渲染不同效果 ==========
        if self.style == "cosmic":
            # 微型星云
            pygame.draw.circle(self.image, (*gel, 80), (cx, cy), 6)
            pygame.draw.circle(self.image, core, (cx, cy), 4)
            for i in range(3):
                s_angle = t + i * math.pi * 2 / 3
                sx = cx + math.cos(s_angle) * 4
                sy = cy + math.sin(s_angle) * 4
                pygame.draw.circle(self.image, (*star, 180), (int(sx), int(sy)), 1)
        
        elif self.style == "void":
            # 微型黑洞
            pygame.draw.circle(self.image, (20, 10, 40), (cx, cy), 5)
            pygame.draw.circle(self.image, core, (cx, cy), 4, 1)
            pygame.draw.circle(self.image, pulse, (cx, cy), 2)
        
        elif self.style == "crystal":
            # 微型棱镜
            hex_pts = [(cx + math.cos(i * math.pi / 3) * 4, 
                       cy + math.sin(i * math.pi / 3) * 4) for i in range(6)]
            pygame.draw.polygon(self.image, core, [(int(p[0]), int(p[1])) for p in hex_pts])
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 2)
        
        elif self.style == "toxic":
            # 毒液球
            jiggle = math.sin(t * 2) * 1
            pygame.draw.ellipse(self.image, core, (cx - 4 + int(jiggle), cy - 4, 8 - int(jiggle), 8))
            pygame.draw.circle(self.image, pulse, (cx, cy - 1), 2)
        
        elif self.style == "royal":
            # 金色珠
            pygame.draw.circle(self.image, (*gel, 100), (cx, cy), 6)
            pygame.draw.circle(self.image, core, (cx, cy), 4)
            pygame.draw.circle(self.image, (255, 240, 150), (cx - 1, cy - 1), 2)
        
        elif self.style == "blood":
            # 血珠
            pygame.draw.circle(self.image, (*gel, 80), (cx, cy), 5)
            pygame.draw.circle(self.image, core, (cx, cy), 4)
            pygame.draw.circle(self.image, (255, 200, 200), (cx - 1, cy - 1), 1)
        
        elif self.style == "ice":
            # 冰屑
            pygame.draw.circle(self.image, (*gel, 100), (cx, cy), 5)
            for i in range(3):
                angle = i * math.pi * 2 / 3
                ix = cx + math.cos(angle) * 4
                iy = cy + math.sin(angle) * 4
                pygame.draw.line(self.image, core, (cx, cy), (int(ix), int(iy)), 2)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 2)
        
        elif self.style == "flame":
            # 火星
            pygame.draw.circle(self.image, (*gel, 80), (cx, cy), 5)
            pygame.draw.circle(self.image, core, (cx, cy), 4)
            pygame.draw.circle(self.image, (255, 255, 200), (cx, cy), 2)
            # 小火焰
            flame_h = 3 + int(math.sin(t * 3) * 1)
            pygame.draw.polygon(self.image, pulse, [(cx, cy - flame_h), (cx - 2, cy), (cx + 2, cy)])
        
        elif self.style == "phantom":
            # 魂火
            alpha = int(150 + 50 * math.sin(t))
            pygame.draw.circle(self.image, (*core, alpha), (cx, cy), 5)
            pygame.draw.circle(self.image, (*pulse, alpha // 2), (cx, cy), 3)
        
        elif self.style == "rainbow":
            # 彩虹珠
            rainbow = [(255, 80, 80), (255, 200, 80), (80, 255, 130), 
                      (80, 180, 255), (180, 100, 255)]
            col = rainbow[int(t * 2) % 5]
            pygame.draw.circle(self.image, col, (cx, cy), 4)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 2)
        
        elif self.style == "abyss":
            # 末世碎片
            pygame.draw.circle(self.image, (30, 15, 50), (cx, cy), 5)
            pygame.draw.circle(self.image, core, (cx, cy), 4, 1)
            pygame.draw.circle(self.image, pulse, (cx, cy), 2)
            # 裂隙
            for i in range(3):
                c_angle = i * math.pi * 2 / 3 + t * 0.5
                cx2 = cx + math.cos(c_angle) * 4
                cy2 = cy + math.sin(c_angle) * 4
                pygame.draw.line(self.image, star, (cx, cy), (int(cx2), int(cy2)), 1)
        
        else:
            # 默认
            pygame.draw.circle(self.image, (*core, 100), (cx, cy), 6)
            pygame.draw.circle(self.image, pulse, (cx, cy), 4)
            pygame.draw.circle(self.image, star, (cx, cy), 2)
        
        # 通用尾迹
        trail_x = cx - math.cos(self.angle) * 5
        trail_y = cy - math.sin(self.angle) * 5
        pygame.draw.circle(self.image, (*core, 100), (int(trail_x), int(trail_y)), 2)


# ==================== 凝胶子核（链式追踪）====================
class GelCoreBullet(pygame.sprite.Sprite):
    """凝胶子核 - 追踪敌人后展开小域"""
    
    def __init__(self, x, y, owner=None, style="default", chain_count=1):
        super().__init__()
        self.owner = owner
        self.is_enemy = False
        self.style = style
        self.chain_count = chain_count
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.speed = 7
        self.turn_rate = 0.08
        
        self.frame = 0
        self.lifetime = 150
        self.angle = random.uniform(-math.pi, math.pi)
        
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 追踪
        target = self._find_target()
        if target:
            tx, ty = target.rect.center
            target_angle = math.atan2(ty - self.float_y, tx - self.float_x)
            angle_diff = target_angle - self.angle
            while angle_diff > math.pi: angle_diff -= math.pi * 2
            while angle_diff < -math.pi: angle_diff += math.pi * 2
            self.angle += max(-self.turn_rate, min(self.turn_rate, angle_diff))
        
        # 移动
        self.float_x += math.cos(self.angle) * self.speed
        self.float_y += math.sin(self.angle) * self.speed
        
        # 命中展开小域
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                self._spawn_small_domain()
                self.kill()
                return
        
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _find_target(self):
        min_dist = 300
        target = None
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x,
                            enemy.rect.centery - self.float_y)
            if dist < min_dist:
                min_dist = dist
                target = enemy
        return target
    
    def _spawn_small_domain(self):
        """生成小型重力域"""
        domain = GravityDomain(self.float_x, self.float_y, self.owner, 
                              self.style, is_small=True, chain_count=self.chain_count)
        all_sprites.add(domain)
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        gel = theme["gel"]
        pulse = theme["pulse"]
        
        cx, cy = 10, 10
        t = self.frame * 0.15
        
        # 凝胶外形 - 弹性变形
        jiggle = math.sin(self.frame * 0.3) * 2
        
        # ========== 根据涂装渲染不同效果 ==========
        if self.style == "cosmic":
            # 微型星云凝胶
            pygame.draw.ellipse(self.image, (*gel, 180), 
                               (cx - 8 + int(jiggle), cy - 7, 16 - int(jiggle), 14))
            # 星尘内部
            for i in range(3):
                s_angle = t + i * math.pi * 2 / 3
                sx = cx + math.cos(s_angle) * 4
                sy = cy + math.sin(s_angle) * 3
                pygame.draw.circle(self.image, (*theme["star"], 200), (int(sx), int(sy)), 2)
            pygame.draw.circle(self.image, pulse, (cx, cy), 4)
        
        elif self.style == "void":
            # 虚空凝胶
            pygame.draw.ellipse(self.image, (20, 10, 40), 
                               (cx - 8 + int(jiggle), cy - 7, 16 - int(jiggle), 14))
            pygame.draw.ellipse(self.image, (*gel, 150), 
                               (cx - 8 + int(jiggle), cy - 7, 16 - int(jiggle), 14), 2)
            pygame.draw.circle(self.image, pulse, (cx, cy), 4)
        
        elif self.style == "crystal":
            # 水晶凝胶
            hex_pts = [(cx + math.cos(i * math.pi / 3 + jiggle * 0.1) * 7, 
                       cy + math.sin(i * math.pi / 3 + jiggle * 0.1) * 6) for i in range(6)]
            pygame.draw.polygon(self.image, gel, [(int(p[0]), int(p[1])) for p in hex_pts])
            pygame.draw.polygon(self.image, pulse, [(int(p[0]), int(p[1])) for p in hex_pts], 1)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 3)
        
        elif self.style == "toxic":
            # 毒液凝胶
            pygame.draw.ellipse(self.image, gel, 
                               (cx - 9 + int(jiggle * 1.5), cy - 7, 18 - int(jiggle), 14))
            # 气泡
            for i in range(2):
                bx = cx + (i - 0.5) * 5
                by = cy - 3 + math.sin(t + i) * 2
                pygame.draw.circle(self.image, (*pulse, 180), (int(bx), int(by)), 2)
            pygame.draw.circle(self.image, pulse, (cx, cy + 1), 4)
        
        elif self.style == "royal":
            # 皇家凝胶
            pygame.draw.ellipse(self.image, gel, 
                               (cx - 8 + int(jiggle), cy - 7, 16 - int(jiggle), 14))
            pygame.draw.ellipse(self.image, (255, 240, 150), 
                               (cx - 8 + int(jiggle), cy - 7, 16 - int(jiggle), 14), 1)
            pygame.draw.circle(self.image, (255, 200, 80), (cx, cy), 5)
            pygame.draw.circle(self.image, (255, 255, 200), (cx - 2, cy - 2), 2)
        
        elif self.style == "blood":
            # 血液凝胶
            heartbeat = abs(math.sin(t * 0.8)) * 2
            pygame.draw.ellipse(self.image, gel, 
                               (cx - 8 + int(jiggle) - int(heartbeat), cy - 7 - int(heartbeat * 0.5), 
                                16 - int(jiggle) + int(heartbeat * 2), 14 + int(heartbeat)))
            pygame.draw.circle(self.image, pulse, (cx, cy), 4)
            pygame.draw.circle(self.image, (255, 200, 200), (cx - 2, cy - 2), 1)
        
        elif self.style == "ice":
            # 冰霜凝胶
            pygame.draw.ellipse(self.image, (*gel, 200), 
                               (cx - 8 + int(jiggle), cy - 7, 16 - int(jiggle), 14))
            # 冰晶纹
            for i in range(3):
                angle = i * math.pi * 2 / 3
                ix = cx + math.cos(angle) * 5
                iy = cy + math.sin(angle) * 4
                pygame.draw.line(self.image, (255, 255, 255), (cx, cy), (int(ix), int(iy)), 1)
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 3)
        
        elif self.style == "flame":
            # 熔岩凝胶
            pygame.draw.ellipse(self.image, gel, 
                               (cx - 8 + int(jiggle), cy - 6, 16 - int(jiggle), 12))
            # 火焰顶
            flame_h = 4 + int(math.sin(t * 3) * 2)
            pygame.draw.polygon(self.image, pulse, 
                              [(cx, cy - 6 - flame_h), (cx - 3, cy - 4), (cx + 3, cy - 4)])
            pygame.draw.circle(self.image, (255, 255, 200), (cx, cy), 3)
        
        elif self.style == "phantom":
            # 幽魂凝胶
            alpha = int(150 + 50 * math.sin(t))
            pygame.draw.ellipse(self.image, (*gel, alpha), 
                               (cx - 8 + int(jiggle), cy - 7, 16 - int(jiggle), 14))
            pygame.draw.circle(self.image, (*pulse, alpha), (cx, cy), 4)
            # 魂尾
            for i in range(3):
                tail_y = cy + 5 + i * 3
                tail_alpha = alpha - i * 40
                if tail_alpha > 0:
                    pygame.draw.ellipse(self.image, (*gel, tail_alpha), 
                                       (cx - 4 + i, int(tail_y), 8 - i * 2, 4))
        
        elif self.style == "rainbow":
            # 彩虹凝胶
            rainbow = [(255, 80, 80), (255, 200, 80), (80, 255, 130), 
                      (80, 180, 255), (180, 100, 255)]
            color_idx = int(t * 2) % 5
            pygame.draw.ellipse(self.image, rainbow[color_idx], 
                               (cx - 8 + int(jiggle), cy - 7, 16 - int(jiggle), 14))
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), 4)
        
        elif self.style == "abyss":
            # 末世凝胶
            pygame.draw.ellipse(self.image, (20, 10, 40), 
                               (cx - 8 + int(jiggle), cy - 7, 16 - int(jiggle), 14))
            pygame.draw.ellipse(self.image, (*gel, 180), 
                               (cx - 8 + int(jiggle), cy - 7, 16 - int(jiggle), 14), 2)
            # 裂隙
            for i in range(3):
                c_angle = i * math.pi * 2 / 3 + t * 0.3
                cx2 = cx + math.cos(c_angle) * 5
                cy2 = cy + math.sin(c_angle) * 4
                pygame.draw.line(self.image, pulse, (cx, cy), (int(cx2), int(cy2)), 1)
            pygame.draw.circle(self.image, pulse, (cx, cy), 3)
        
        else:
            # 默认
            pygame.draw.ellipse(self.image, gel, 
                               (cx - 8 + int(jiggle), cy - 7, 16 - int(jiggle), 14))
            pygame.draw.circle(self.image, pulse, (cx, cy), 5)
            pygame.draw.circle(self.image, (255, 255, 255, 180), (cx - 3, cy - 3), 2)


# ==================== 星凝核拾取物 ====================
class StarGelPickup(pygame.sprite.Sprite):
    """星凝核拾取 - 回复10能量"""
    
    def __init__(self, x, y, owner=None):
        super().__init__()
        self.owner = owner
        self.float_x = float(x)
        self.float_y = float(y)
        self.energy_value = 10
        
        self.frame = 0
        self.lifetime = 300
        
        self.image = pygame.Surface((26, 26), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 漂浮
        self.float_y += math.sin(self.frame * 0.1) * 0.25
        
        # 拾取检测
        if self.owner and self.rect.colliderect(self.owner.rect):
            self._pickup()
            return
        
        self._render()
        self.rect.center = (int(self.float_x), int(self.float_y))
    
    def _pickup(self):
        if self.owner:
            if hasattr(self.owner, 'energy'):
                self.owner.energy = min(getattr(self.owner, 'max_energy', 100),
                                       self.owner.energy + self.energy_value)
        self.kill()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 13, 13
        
        flash = abs(math.sin(self.frame * 0.15))
        
        # 外光晕
        r = 10 + int(flash * 3)
        pygame.draw.circle(self.image, (150, 100, 230, 100), (cx, cy), r)
        pygame.draw.circle(self.image, (180, 140, 255, 150), (cx, cy), r, 2)
        
        # 内核
        pygame.draw.circle(self.image, (200, 160, 255), (cx, cy), 6)
        pygame.draw.circle(self.image, (255, 255, 255, 200), (cx - 2, cy - 2), 2)
        
        # 快消失闪烁
        if self.lifetime < 60 and self.frame % 10 < 5:
            pygame.draw.circle(self.image, (255, 255, 150, 150), (cx, cy), r + 2, 2)


# ==================== 特效类 ====================
class StarGelHitEffect(pygame.sprite.Sprite):
    """星凝弹命中特效"""
    def __init__(self, x, y, style="default"):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 25
        self.style = style
        
        self.splashes = []
        for i in range(8):
            angle = i * math.pi / 4 + random.uniform(-0.2, 0.2)
            speed = random.uniform(3, 6)
            self.splashes.append({
                'angle': angle, 'speed': speed, 'dist': 0,
                'size': random.uniform(3, 6)
            })
        
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        
        for s in self.splashes:
            s['dist'] += s['speed'] * (1 - self.frame / self.lifetime)
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        cx, cy = 40, 40
        progress = self.frame / self.lifetime
        
        # 波纹扩散
        for wave in range(3):
            wave_r = int(progress * 35 + wave * 5)
            wave_alpha = int(150 * (1 - progress) * (1 - wave * 0.25))
            if wave_r > 0 and wave_alpha > 0:
                pygame.draw.circle(self.image, (*theme["pulse"], wave_alpha),
                                 (cx, cy), wave_r, 2)
        
        # 星凝溅射
        for s in self.splashes:
            sx = cx + math.cos(s['angle']) * s['dist']
            sy = cy + math.sin(s['angle']) * s['dist']
            s_alpha = int(255 * (1 - progress) * (1 - s['dist'] / 40))
            if s_alpha > 0 and 0 <= sx < 80 and 0 <= sy < 80:
                size = int(s['size'] * (1 - progress * 0.5))
                if size > 0:
                    pygame.draw.circle(self.image, (*theme["star"], s_alpha),
                                     (int(sx), int(sy)), size)


class DomainExplosion(pygame.sprite.Sprite):
    """重力域爆炸特效"""
    def __init__(self, x, y, style="default", is_small=False):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 35
        self.style = style
        self.is_small = is_small
        
        self.image = pygame.Surface((200, 200) if not is_small else (140, 140), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        size = self.image.get_width()
        cx, cy = size // 2, size // 2
        progress = self.frame / self.lifetime
        
        max_r = 80 if not self.is_small else 55
        
        # 爆炸冲击波
        for wave in range(4):
            wave_prog = min(1.0, progress * 1.5 - wave * 0.15)
            if wave_prog > 0:
                wave_r = int(wave_prog * max_r)
                wave_alpha = int(200 * (1 - wave_prog) * (1 - wave * 0.2))
                if wave_r > 0 and wave_alpha > 0:
                    pygame.draw.circle(self.image, (*theme["domain"], wave_alpha),
                                     (cx, cy), wave_r, 3)
        
        # 中心闪光
        if progress < 0.3:
            flash_alpha = int(255 * (1 - progress / 0.3))
            flash_r = int(20 * (1 - progress / 0.3))
            pygame.draw.circle(self.image, (*theme["pulse"], flash_alpha), (cx, cy), flash_r)


# ==================== 大招技能（高质量版 - 参考克苏鲁风格）====================

class StarStompSkill(pygame.sprite.Sprite):
    """【星陨降临】F键大招 - 三阶段大招（性能优化版）"""
    
    def __init__(self, x, y, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.start_x = float(x)
        self.start_y = float(y)
        
        # 阶段系统
        self.phase = 0
        self.frame = 0
        self.phase_duration = [90, 150, 180]  # 缩短时间
        
        # 陨石数据
        self.meteors = []
        
        # 凝胶漩涡
        self.vortex_angle = 0
        self.absorbed_energy = 0
        
        # 粒子系统（限制数量）
        self.particles = []
        self.max_particles = 30
        
        # 重力场
        self.gravity_wells = []
        
        # 无敌
        if owner:
            owner.invincible = True
            owner.invincible_timer = 480
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        """添加粒子（带数量限制）"""
        if len(self.particles) < self.max_particles:
            self.particles.append({
                'x': x, 'y': y, 'vx': vx, 'vy': vy,
                'color': color, 'life': life, 'max_life': life, 'size': size
            })
    
    def _update_particles(self):
        """更新并绘制粒子"""
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            alpha = int(255 * p['life'] / p['max_life'])
            size = int(p['size'] * p['life'] / p['max_life'])
            if size > 0:
                pygame.draw.circle(self.image, (*p['color'][:3], alpha),
                                 (int(p['x']), int(p['y'])), size)
    
    def _phase1_gel_convergence(self):
        """第一阶段：凝胶聚变 - 全屏吸收能量"""
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        progress = self.frame / self.phase_duration[0]
        ox, oy = int(self.start_x), int(self.start_y)
        
        # 简化漩涡效果（减少层数和粒子）
        self.vortex_angle += 0.08
        for layer in range(3):
            layer_r = 60 + layer * 35 - progress * 20
            for i in range(6):
                angle = self.vortex_angle + i * math.pi / 3 + layer * 0.3
                spiral_r = layer_r * (1 - progress * 0.5)
                px = ox + int(math.cos(angle) * spiral_r)
                py = oy + int(math.sin(angle) * spiral_r)
                gel_size = max(1, 6 - layer)
                pygame.draw.circle(self.image, theme["gel"], (px, py), gel_size)
        
        # 吸收敌弹（简化）
        for bullet in list(enemy_bullets)[:10]:  # 限制处理数量
            dist = math.hypot(bullet.rect.centerx - ox, bullet.rect.centery - oy)
            if dist < 200 and dist > 0:
                dx = ox - bullet.rect.centerx
                dy = oy - bullet.rect.centery
                bullet.rect.x += int(dx / dist * 5)
                bullet.rect.y += int(dy / dist * 5)
                if dist < 50:
                    bullet.kill()
                    self.absorbed_energy += 5
        
        # 中心核心（简化层数）
        core_pulse = abs(math.sin(self.frame * 0.15)) * 0.3 + 0.7
        core_r = int((35 + self.absorbed_energy * 0.3) * core_pulse)
        pygame.draw.circle(self.image, (*theme["domain"], 100), (ox, oy), core_r + 20, 3)
        pygame.draw.circle(self.image, theme["core"], (ox, oy), core_r)
        pygame.draw.circle(self.image, (255, 255, 255), (ox, oy), max(3, core_r // 3))
        
        # 减速效果（每15帧检查一次）
        if self.frame % 15 == 0:
            for enemy in mobs:
                dist = math.hypot(enemy.rect.centerx - ox, enemy.rect.centery - oy)
                if dist < 200:
                    if not hasattr(enemy, 'slowed'):
                        enemy.slowed = 0
                    enemy.slowed = max(enemy.slowed, 30)
        
        # 能量火花（降低频率）
        if self.frame % 10 == 0:
            for _ in range(3):
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(100, 200)
                px = ox + math.cos(angle) * dist
                py = oy + math.sin(angle) * dist
                self._add_particle(px, py, (ox - px) * 0.03, (oy - py) * 0.03,
                                 theme["star"], random.randint(20, 40), 4)
        
        self._update_particles()
    
    def _phase2_meteor_storm(self):
        """第二阶段：星陨轰击 - 巨型凝胶陨石"""
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        
        # 深空背景
        pygame.draw.rect(self.image, (10, 5, 25, 50), (0, 0, WIDTH, HEIGHT))
        
        # 生成陨石（共6颗，间隔生成）
        if len(self.meteors) < 6 and self.frame % 30 == 1:
            meteor = {
                'x': random.randint(80, WIDTH - 80),
                'y': -60,
                'target_x': random.randint(100, WIDTH - 100),
                'target_y': random.randint(200, HEIGHT - 100),
                'phase': 'descend',  # descend -> impact
                'size': random.randint(35, 50),
                'rotation': random.uniform(0, math.pi * 2),
                'trail': [],
            }
            self.meteors.append(meteor)
        
        # 更新和绘制陨石
        for m in self.meteors[:]:
            if m['phase'] == 'descend':
                # 追踪下降
                dx = m['target_x'] - m['x']
                dy = m['target_y'] - m['y']
                dist = math.hypot(dx, dy)
                if dist > 10:
                    m['x'] += dx / dist * 8
                    m['y'] += dy / dist * 8
                    m['rotation'] += 0.15
                    # 简化拖尾
                    if len(m['trail']) < 8:
                        m['trail'].append((m['x'], m['y']))
                    else:
                        m['trail'].pop(0)
                        m['trail'].append((m['x'], m['y']))
                else:
                    m['phase'] = 'impact'
                    self._meteor_impact(m)
                
                # 绘制简化拖尾
                for i, (tx, ty) in enumerate(m['trail']):
                    trail_size = max(1, int(m['size'] * 0.3 * i / len(m['trail'])))
                    pygame.draw.circle(self.image, theme["domain"], (int(tx), int(ty)), trail_size)
                
                # 绘制陨石
                self._draw_meteor(m, theme)
        
        # 玩家防护罩
        ox, oy = int(self.start_x), int(self.start_y)
        pygame.draw.circle(self.image, (*theme["pulse"], 80), (ox, oy), 50, 3)
        
        self._update_particles()
    
    def _draw_meteor(self, m, theme):
        """绘制陨石（简化版）"""
        x, y = int(m['x']), int(m['y'])
        size = m['size']
        
        # 简化：直接画圆+光晕
        pygame.draw.circle(self.image, (*theme["domain"], 80), (x, y), size + 10)
        pygame.draw.circle(self.image, theme["core"], (x, y), size)
        pygame.draw.circle(self.image, theme["star"], (x, y), size // 2)
        pygame.draw.circle(self.image, (255, 255, 255), (x, y), size // 4)
    
    def _meteor_impact(self, m):
        """陨石撞击"""
        x, y = m['x'], m['y']
        damage = self.owner.damage * 2.5 if self.owner else 60
        
        # 范围伤害
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - x, enemy.rect.centery - y)
            if dist < 100:
                enemy.take_damage(damage * (1 - dist / 120), true_damage=True)
        
        # 爆炸粒子（减少数量）
        theme = get_theme(self.style)
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 8)
            self._add_particle(x, y, math.cos(angle) * speed, math.sin(angle) * speed,
                             theme["pulse"], random.randint(15, 30), 5)
        
        # 生成追踪弹（减少数量）
        for i in range(2):
            angle = i * math.pi + random.uniform(-0.3, 0.3)
            gel = MiniStarGelBullet(x, y, angle, self.owner)
            all_sprites.add(gel)
            bullets.add(gel)
    
    def _phase3_apocalypse(self):
        """第三阶段：末世降临（简化版）"""
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        progress = self.frame / self.phase_duration[2]
        
        # 重力场初始化（减少数量）
        if self.frame == 1:
            for _ in range(2):
                self.gravity_wells.append({
                    'x': random.randint(150, WIDTH - 150),
                    'y': random.randint(150, HEIGHT - 150),
                    'strength': 1.0,
                })
        
        # 更新重力场
        for well in self.gravity_wells:
            wx, wy = int(well['x']), int(well['y'])
            
            # 简化视觉（只画2个圆环）
            pulse = abs(math.sin(self.frame * 0.1)) * 0.3 + 0.7
            pygame.draw.circle(self.image, (*theme["domain"], 80), (wx, wy), int(60 * pulse), 3)
            pygame.draw.circle(self.image, (*theme["pulse"], 60), (wx, wy), int(100 * pulse), 2)
            
            # 吸引敌人（每3帧处理一次）
            if self.frame % 3 == 0:
                for enemy in mobs:
                    dist = math.hypot(enemy.rect.centerx - wx, enemy.rect.centery - wy)
                    if dist < 120 and dist > 0:
                        enemy.rect.x += int((wx - enemy.rect.centerx) / dist * 2)
                        enemy.rect.y += int((wy - enemy.rect.centery) / dist * 2)
            
            # 伤害（每30帧）
            if self.frame % 30 == 0:
                for enemy in mobs:
                    dist = math.hypot(enemy.rect.centerx - wx, enemy.rect.centery - wy)
                    if dist < 100:
                        damage = self.owner.damage * 0.5 if self.owner else 15
                        enemy.take_damage(damage, true_damage=True)
        
        # 简化全屏风暴（减少数量）
        if self.frame % 2 == 0:
            for _ in range(5):
                sx = random.randint(0, WIDTH)
                sy = random.randint(0, HEIGHT)
                streak_len = random.randint(20, 40)
                angle = random.uniform(0, math.pi * 2)
                ex = sx + int(math.cos(angle) * streak_len)
                ey = sy + int(math.sin(angle) * streak_len)
                pygame.draw.line(self.image, theme["gel"], (sx, sy), (ex, ey), 2)
        
        # 玩家核心（简化）
        ox, oy = int(self.start_x), int(self.start_y)
        core_pulse = abs(math.sin(self.frame * 0.12)) * 0.3 + 0.7
        
        # 只画2层能量场
        pygame.draw.circle(self.image, (*theme["domain"], 80), (ox, oy), int(60 * core_pulse), 3)
        pygame.draw.circle(self.image, (*theme["pulse"], 60), (ox, oy), int(90 * core_pulse), 2)
        
        # 简化符文环（6个点代替12个星形）
        for i in range(6):
            rune_angle = self.frame * 0.03 + i * math.pi / 3
            rune_r = 80 * core_pulse
            rx = ox + int(math.cos(rune_angle) * rune_r)
            ry = oy + int(math.sin(rune_angle) * rune_r)
            pygame.draw.circle(self.image, theme["star"], (rx, ry), 5)
        
        # 中心核心（简化巨眼为圆形）
        pygame.draw.circle(self.image, (200, 180, 220), (ox, oy), int(30 * core_pulse))
        pygame.draw.circle(self.image, theme["core"], (ox, oy), int(15 * core_pulse))
        pygame.draw.circle(self.image, (10, 10, 20), (ox, oy), int(8 * core_pulse))
        
        self._update_particles()
    
    def update(self):
        self.frame += 1
        
        if self.phase == 0:
            self._phase1_gel_convergence()
            if self.frame >= self.phase_duration[0]:
                self.phase = 1
                self.frame = 0
        
        elif self.phase == 1:
            self._phase2_meteor_storm()
            if self.frame >= self.phase_duration[1]:
                self.phase = 2
                self.frame = 0
                self.meteors.clear()
        
        elif self.phase == 2:
            self._phase3_apocalypse()
            if self.frame >= self.phase_duration[2]:
                if self.owner:
                    self.owner.invincible = False
                self.kill()


class AstralLaser(pygame.sprite.Sprite):
    """星体激光 - 踩踏后散射的激光"""
    
    def __init__(self, x, y, angle, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = angle
        self.speed = 14
        self.damage = owner.damage * 0.8 if owner else 20
        self.is_enemy = False
        self.frame = 0
        self.lifetime = 60
        
        self.image = pygame.Surface((40, 12), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        self.float_x += math.cos(self.angle) * self.speed
        self.float_y += math.sin(self.angle) * self.speed
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        if self.frame >= self.lifetime or not (0 < self.float_x < WIDTH and 0 < self.float_y < HEIGHT):
            self.kill()
            return
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        # 激光条
        pygame.draw.rect(self.image, theme["pulse"], (0, 3, 40, 6))
        pygame.draw.rect(self.image, (255, 255, 255), (5, 4, 30, 4))
        # 旋转
        rotated = pygame.transform.rotate(self.image, -math.degrees(self.angle))
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.image.blit(rotated, rotated.get_rect(center=(20, 20)))


class StompShockwave(pygame.sprite.Sprite):
    """踩踏冲击波特效"""
    
    def __init__(self, x, y, style="default"):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.style = style
        self.frame = 0
        self.lifetime = 30
        self.image = pygame.Surface((400, 400), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        cx, cy = 200, 200
        prog = self.frame / self.lifetime
        
        # 扩散环
        for i in range(3):
            ring_r = int(50 + prog * 150 + i * 20)
            alpha = int(200 * (1 - prog) * (1 - i * 0.25))
            if alpha > 0:
                pygame.draw.circle(self.image, (*theme["domain"], alpha), (cx, cy), ring_r, 4 - i)
        
        # 裂纹
        for i in range(8):
            angle = i * math.pi / 4
            crack_len = 30 + prog * 120
            cx2 = cx + math.cos(angle) * crack_len
            cy2 = cy + math.sin(angle) * crack_len
            pygame.draw.line(self.image, (*theme["pulse"], int(180 * (1 - prog))), (cx, cy), (int(cx2), int(cy2)), 3)


class AstralCrystalSkill(pygame.sprite.Sprite):
    """【深渊凝触】G键大招 - 三阶段触手攻击（参考克苏鲁深渊触手）
    
    第一阶段 (2s): 触手萌生 - 从玩家周围生长8条凝胶触手
    第二阶段 (4s): 狂暴抓取 - 触手自动追踪抓取敌人+持续伤害
    第三阶段 (2s): 凝胶爆发 - 触手末端释放追踪水晶弹幕
    """
    
    def __init__(self, x, y, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.center_x = float(x)
        self.center_y = float(y)
        
        # 阶段系统
        self.phase = 0
        self.frame = 0
        self.phase_duration = [120, 240, 120]  # 2秒、4秒、2秒
        
        # 触手数据
        self.tentacles = []
        self._init_tentacles()
        
        # 粒子
        self.particles = []
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _init_tentacles(self):
        """初始化触手（减少到5条）"""
        for i in range(5):
            angle = i * math.pi * 2 / 5
            self.tentacles.append({
                'base_angle': angle,
                'angle': angle,
                'length': 0,
                'max_length': 160,
                'target': None,
                'grab_timer': 0,
                'phase_offset': random.uniform(0, math.pi * 2),
                'thickness': 8,
            })
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        if len(self.particles) < 20:
            self.particles.append({
                'x': x, 'y': y, 'vx': vx, 'vy': vy,
                'color': color, 'life': life, 'max_life': life, 'size': size
            })
    
    def _update_particles(self):
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            size = max(1, int(p['size'] * p['life'] / p['max_life']))
            pygame.draw.circle(self.image, p['color'], (int(p['x']), int(p['y'])), size)
    
    def _find_target(self, tentacle):
        """寻找目标（简化）"""
        for enemy in list(mobs)[:5]:  # 只检查前5个敌人
            dist = math.hypot(enemy.rect.centerx - self.center_x, enemy.rect.centery - self.center_y)
            if dist < 200:
                return enemy
        return None
    
    def _phase1_growth(self):
        """第一阶段：触手萌生（简化）"""
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        progress = self.frame / self.phase_duration[0]
        
        # 触手生长
        for t in self.tentacles:
            t['length'] = min(t['max_length'] * progress * 1.2, t['max_length'])
            self._draw_tentacle(t, theme)
        
        # 中心核心
        ox, oy = int(self.center_x), int(self.center_y)
        pygame.draw.circle(self.image, (*theme["domain"], 80), (ox, oy), 40, 3)
        pygame.draw.circle(self.image, theme["core"], (ox, oy), 25)
        pygame.draw.circle(self.image, (255, 255, 255), (ox, oy), 10)
        
        self._update_particles()
    
    def _phase2_grab(self):
        """第二阶段：狂暴抓取"""
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        
        # 深渊背景
        pygame.draw.rect(self.image, (10, 5, 20, 50), (0, 0, WIDTH, HEIGHT))
        
        damage = self.owner.damage * 0.3 if self.owner else 10
        
        for t in self.tentacles:
            # 寻找目标
            if t['target'] is None and self.frame % 30 == 0:
                t['target'] = self._find_target(t)
            
            # 计算触手末端
            tip_x = self.center_x + math.cos(t['angle']) * t['length']
            tip_y = self.center_y + math.sin(t['angle']) * t['length']
            
            # 追踪目标
            if t['target'] and t['target'].alive():
                target_angle = math.atan2(t['target'].rect.centery - self.center_y,
                                         t['target'].rect.centerx - self.center_x)
                # 缓慢转向
                angle_diff = target_angle - t['angle']
                while angle_diff > math.pi: angle_diff -= 2 * math.pi
                while angle_diff < -math.pi: angle_diff += 2 * math.pi
                t['angle'] += angle_diff * 0.08
                
                # 检测抓取
                grab_dist = math.hypot(t['target'].rect.centerx - tip_x,
                                      t['target'].rect.centery - tip_y)
                if grab_dist < 40:
                    t['grab_timer'] += 1
                    # 抓取伤害
                    if t['grab_timer'] % 15 == 0:
                        t['target'].take_damage(damage, true_damage=True)
                    # 拉扯效果
                    pull_strength = 2
                    t['target'].rect.x += int((self.center_x - t['target'].rect.centerx) * 0.03)
                    t['target'].rect.y += int((self.center_y - t['target'].rect.centery) * 0.03)
                else:
                    t['grab_timer'] = 0
            else:
                # 回归基础角度
                angle_diff = t['base_angle'] - t['angle']
                while angle_diff > math.pi: angle_diff -= 2 * math.pi
                while angle_diff < -math.pi: angle_diff += 2 * math.pi
                t['angle'] += angle_diff * 0.02
                t['target'] = None
            
            self._draw_tentacle(t, theme, grabbing=t['grab_timer'] > 0)
        
        # 中心
        ox, oy = int(self.center_x), int(self.center_y)
        pygame.draw.circle(self.image, theme["core"], (ox, oy), 30)
        pygame.draw.circle(self.image, theme["pulse"], (ox, oy), 18)
        
        self._update_particles()
    
    def _phase3_burst(self):
        """第三阶段：凝胶爆发"""
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        progress = self.frame / self.phase_duration[2]
        
        # 触手收缩并释放弹幕
        for i, t in enumerate(self.tentacles):
            t['length'] = t['max_length'] * (1 - progress * 0.5)
            
            # 释放水晶弹幕
            if self.frame == 30 + i * 10:  # 间隔加大
                tip_x = self.center_x + math.cos(t['angle']) * t['length']
                tip_y = self.center_y + math.sin(t['angle']) * t['length']
                
                # 只发射2颗
                for j in range(2):
                    angle = t['angle'] + (j - 0.5) * 0.3
                    crystal = TentacleCrystal(tip_x, tip_y, angle, self.owner, self.style)
                    all_sprites.add(crystal)
                    bullets.add(crystal)
            
            self._draw_tentacle(t, theme)
        
        # 简化爆发光效
        ox, oy = int(self.center_x), int(self.center_y)
        if progress < 0.3:
            pygame.draw.circle(self.image, (*theme["star"], 100), (ox, oy), int(60 + progress * 80), 4)
        
        self._update_particles()
    
    def _draw_tentacle(self, t, theme, grabbing=False):
        """绘制触手（简化版 - 减少分段）"""
        segments = 6  # 从16减到6
        points = []
        
        for i in range(segments + 1):
            prog = i / segments
            base_r = t['length'] * prog
            wave = math.sin(self.frame * 0.1 + prog * 3 + t['phase_offset']) * 8 * prog
            
            px = self.center_x + math.cos(t['angle']) * base_r
            py = self.center_y + math.sin(t['angle']) * base_r
            
            perp_angle = t['angle'] + math.pi / 2
            px += math.cos(perp_angle) * wave
            py += math.sin(perp_angle) * wave
            
            points.append((int(px), int(py)))
        
        # 绘制触手（简化：只画线条）
        if len(points) >= 2:
            color = theme["core"] if not grabbing else (255, 100, 120)
            for i in range(len(points) - 1):
                thick = max(2, t['thickness'] - i * 2)
                pygame.draw.line(self.image, color, points[i], points[i + 1], thick)
        
        # 简化末端（圆球代替眼球）
        if t['length'] > 30 and len(points) > 0:
            tip = points[-1]
            pygame.draw.circle(self.image, theme["pulse"], tip, 8)
            pygame.draw.circle(self.image, (255, 255, 255), tip, 4)
    
    def update(self):
        self.frame += 1
        
        # 跟随玩家
        if self.owner:
            self.center_x = self.owner.rect.centerx
            self.center_y = self.owner.rect.centery
        
        if self.phase == 0:
            self._phase1_growth()
            if self.frame >= self.phase_duration[0]:
                self.phase = 1
                self.frame = 0
        
        elif self.phase == 1:
            self._phase2_grab()
            if self.frame >= self.phase_duration[1]:
                self.phase = 2
                self.frame = 0
        
        elif self.phase == 2:
            self._phase3_burst()
            if self.frame >= self.phase_duration[2]:
                self.kill()


class TentacleCrystal(pygame.sprite.Sprite):
    """触手释放的追踪水晶弹"""
    
    def __init__(self, x, y, angle, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.is_enemy = False
        self.damage = owner.damage * 0.8 if owner else 20
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = angle
        self.speed = 5
        self.frame = 0
        self.lifetime = 180
        self.target = None
        
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        
        # 追踪
        if self.frame > 30:
            if not self.target or not self.target.alive():
                min_dist = float('inf')
                for enemy in mobs:
                    dist = math.hypot(enemy.rect.centerx - self.float_x, enemy.rect.centery - self.float_y)
                    if dist < min_dist:
                        min_dist = dist
                        self.target = enemy
            
            if self.target and self.target.alive():
                target_angle = math.atan2(self.target.rect.centery - self.float_y,
                                         self.target.rect.centerx - self.float_x)
                angle_diff = target_angle - self.angle
                while angle_diff > math.pi: angle_diff -= 2 * math.pi
                while angle_diff < -math.pi: angle_diff += 2 * math.pi
                self.angle += angle_diff * 0.08
        
        self.speed = min(12, self.speed + 0.05)
        self.float_x += math.cos(self.angle) * self.speed
        self.float_y += math.sin(self.angle) * self.speed
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        if self.frame >= self.lifetime or not (0 < self.float_x < WIDTH and 0 < self.float_y < HEIGHT):
            self.kill()
            return
        
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        # 简化水晶
        pygame.draw.circle(self.image, theme["core"], (15, 15), 8)
        pygame.draw.circle(self.image, (255, 255, 255), (15, 15), 4)


class AureusSpawnSkill(pygame.sprite.Sprite):
    """【疯狂凝域】C键大招（性能优化版）"""
    
    def __init__(self, x, y, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.center_x = float(x)
        self.center_y = float(y)
        
        # 阶段系统
        self.phase = 0
        self.frame = 0
        self.phase_duration = [80, 200, 80]  # 缩短时间
        
        # 波动数据
        self.waves = []
        self.wave_interval = 30
        
        # 子体军团（减少数量）
        self.spawns = []
        self.spawn_limit = 6
        
        # 粒子（限制）
        self.particles = []
        self.max_particles = 20
        
        # 无敌
        if owner:
            owner.invincible = True
            owner.invincible_timer = 400
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)
    
    def _add_particle(self, x, y, vx, vy, color, life, size=3):
        if len(self.particles) < self.max_particles:
            self.particles.append({
                'x': x, 'y': y, 'vx': vx, 'vy': vy,
                'color': color, 'life': life, 'max_life': life, 'size': size
            })
    
    def _update_particles(self):
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            size = max(1, int(p['size'] * p['life'] / p['max_life']))
            pygame.draw.circle(self.image, p['color'], (int(p['x']), int(p['y'])), size)
    
    def _phase1_expansion(self):
        """第一阶段：凝域扩张（简化）"""
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        
        # 跟随玩家
        if self.owner:
            self.center_x = self.owner.rect.centerx
            self.center_y = self.owner.rect.centery
        
        ox, oy = int(self.center_x), int(self.center_y)
        
        # 释放凝胶波动
        if self.frame % self.wave_interval == 0:
            self.waves.append({'radius': 30, 'max_radius': 250})
        
        # 更新波动（简化）
        for wave in self.waves[:]:
            wave['radius'] += 5
            if wave['radius'] >= wave['max_radius']:
                self.waves.remove(wave)
                continue
            
            # 简化波动圈
            alpha = int(150 * (1 - wave['radius'] / wave['max_radius']))
            pygame.draw.circle(self.image, (*theme["domain"], alpha), (ox, oy), int(wave['radius']), 3)
            
            # 减速（每5帧检查）
            if self.frame % 5 == 0:
                for enemy in list(mobs)[:10]:
                    dist = math.hypot(enemy.rect.centerx - ox, enemy.rect.centery - oy)
                    if abs(dist - wave['radius']) < 30:
                        if not hasattr(enemy, 'slowed'):
                            enemy.slowed = 0
                        enemy.slowed = max(enemy.slowed, 30)
        
        # 中心核心（简化）
        pygame.draw.circle(self.image, (*theme["pulse"], 100), (ox, oy), 50, 3)
        pygame.draw.circle(self.image, theme["core"], (ox, oy), 30)
        pygame.draw.circle(self.image, (255, 255, 255), (ox, oy), 12)
        
        self._update_particles()
    
    def _phase2_legion(self):
        """第二阶段：星凝军团（简化）"""
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        
        if self.owner:
            self.center_x = self.owner.rect.centerx
            self.center_y = self.owner.rect.centery
        
        ox, oy = int(self.center_x), int(self.center_y)
        
        # 召唤子体（减少频率）
        if len(self.spawns) < self.spawn_limit and self.frame % 35 == 1:
            angle = len(self.spawns) * math.pi * 2 / self.spawn_limit
            dist = 100
            sx = ox + int(math.cos(angle) * dist)
            sy = oy + int(math.sin(angle) * dist)
            
            spawn = SlimeLegionSpawn(sx, sy, self.owner, self.style)
            all_sprites.add(spawn)
            self.spawns.append(spawn)
        
        # 减速（每10帧检查）
        if self.frame % 10 == 0:
            for enemy in list(mobs)[:10]:
                if not hasattr(enemy, 'slowed'):
                    enemy.slowed = 0
                enemy.slowed = max(enemy.slowed, 20)
        
        # 简化波动
        if self.frame % 50 == 0:
            self.waves.append({'radius': 30, 'max_radius': 200})
        
        for wave in self.waves[:]:
            wave['radius'] += 4
            if wave['radius'] >= wave['max_radius']:
                self.waves.remove(wave)
                continue
            alpha = int(100 * (1 - wave['radius'] / wave['max_radius']))
            pygame.draw.circle(self.image, (*theme["domain"], alpha), (ox, oy), int(wave['radius']), 3)
        
        # 简化中心效果
        pygame.draw.circle(self.image, (*theme["pulse"], 80), (ox, oy), 60, 3)
        pygame.draw.circle(self.image, theme["core"], (ox, oy), 25)
        pygame.draw.circle(self.image, (255, 255, 255), (ox, oy), 10)
        
        self._update_particles()
    
    def _phase3_finisher(self):
        """第三阶段：终焉爆发（简化）"""
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        progress = self.frame / self.phase_duration[2]
        
        if self.owner:
            self.center_x = self.owner.rect.centerx
            self.center_y = self.owner.rect.centery
        ox, oy = int(self.center_x), int(self.center_y)
        
        # 引爆所有子体
        if self.frame == 1:
            for spawn in self.spawns:
                if spawn.alive():
                    spawn._explode()
            
            # 全屏真伤
            damage = self.owner.damage * 2.0 if self.owner else 50
            for enemy in mobs:
                enemy.take_damage(damage, true_damage=True)
        
        # 简化爆发效果
        if progress < 0.5:
            burst_r = int(50 + progress * 150)
            pygame.draw.circle(self.image, (*theme["star"], int(150 * (1 - progress * 2))), (ox, oy), burst_r, 5)
        
        # 多层爆发波
        for i in range(5):
            wave_r = int(50 + progress * 300 + i * 30)
            wave_alpha = int(180 * (1 - progress) * (1 - i * 0.15))
            if wave_alpha > 0:
                pygame.draw.circle(self.image, (*theme["pulse"], wave_alpha), (ox, oy), wave_r, 5)
        
        # 能量余波
        if progress < 0.6:
            for i in range(12):
                angle = i * 30 + self.frame * 2
                ray_len = 100 + progress * 250
                rx = ox + math.cos(math.radians(angle)) * ray_len
                ry = oy + math.sin(math.radians(angle)) * ray_len
                pygame.draw.line(self.image, (*theme["star"], int(200 * (1 - progress))),
                               (ox, oy), (int(rx), int(ry)), 3)
        
        self._update_particles()
    
    def update(self):
        self.frame += 1
        
        if self.phase == 0:
            self._phase1_expansion()
            if self.frame >= self.phase_duration[0]:
                self.phase = 1
                self.frame = 0
        
        elif self.phase == 1:
            self._phase2_legion()
            if self.frame >= self.phase_duration[1]:
                self.phase = 2
                self.frame = 0
        
        elif self.phase == 2:
            self._phase3_finisher()
            if self.frame >= self.phase_duration[2]:
                if self.owner:
                    self.owner.invincible = False
                self.kill()


class SlimeLegionSpawn(pygame.sprite.Sprite):
    """星凝军团子体 - 自主追踪的自爆凝胶"""
    
    def __init__(self, x, y, owner=None, style="default"):
        super().__init__()
        self.owner = owner
        self.style = style
        self.is_enemy = False
        self.damage = owner.damage * 1.8 if owner else 45
        
        self.float_x = float(x)
        self.float_y = float(y)
        self.vx = 0
        self.vy = 0
        
        self.frame = 0
        self.lifetime = 360
        self.chase_delay = 40
        self.target = None
        self.exploded = False
        self.pulse = random.uniform(0, math.pi * 2)
        
        # 每个子体有独特的颜色变化
        self.color_shift = random.uniform(0, 1)
        
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        self.pulse += 0.12
        
        if self.frame > self.chase_delay:
            self._find_and_chase()
        else:
            # 初始漂浮
            self.float_x += math.sin(self.frame * 0.15 + self.color_shift) * 0.8
            self.float_y += math.cos(self.frame * 0.12 + self.color_shift) * 0.6
        
        self.float_x += self.vx
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        
        # 碰撞检测
        for enemy in mobs:
            if self.rect.colliderect(enemy.rect):
                self._explode()
                return
        
        if self.frame >= self.lifetime:
            self._explode()
            return
        
        self._render()
    
    def _find_and_chase(self):
        if not self.target or not self.target.alive():
            min_dist = float('inf')
            for enemy in mobs:
                dist = math.hypot(enemy.rect.centerx - self.float_x, enemy.rect.centery - self.float_y)
                if dist < min_dist:
                    min_dist = dist
                    self.target = enemy
        
        if self.target and self.target.alive():
            dx = self.target.rect.centerx - self.float_x
            dy = self.target.rect.centery - self.float_y
            dist = math.hypot(dx, dy)
            if dist > 0:
                accel = 0.25 + (self.frame - self.chase_delay) * 0.003
                self.vx += (dx / dist) * accel
                self.vy += (dy / dist) * accel
                
                speed = math.hypot(self.vx, self.vy)
                max_spd = 10 + (self.frame - self.chase_delay) * 0.015
                if speed > max_spd:
                    self.vx = self.vx / speed * max_spd
                    self.vy = self.vy / speed * max_spd
    
    def _explode(self):
        if self.exploded:
            return
        self.exploded = True
        
        for enemy in mobs:
            dist = math.hypot(enemy.rect.centerx - self.float_x, enemy.rect.centery - self.float_y)
            if dist < 100:
                enemy.take_damage(self.damage * (1 - dist / 120), true_damage=True)
        
        effect = SpawnExplosion(self.float_x, self.float_y, self.style)
        all_sprites.add(effect)
        
        self.kill()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        cx, cy = 30, 30
        
        is_chasing = self.frame > self.chase_delay
        
        # 外层光晕
        pulse_scale = 1.0 + 0.2 * math.sin(self.pulse * 2)
        for i in range(4):
            glow_r = int((18 + i * 6) * pulse_scale)
            glow_col = (255, 120, 120) if is_chasing else theme["domain"]
            alpha = 100 - i * 22
            pygame.draw.circle(self.image, (*glow_col, alpha), (cx, cy), glow_r)
        
        # 凝胶主体
        body_r = int(16 * pulse_scale)
        pygame.draw.circle(self.image, theme["core"], (cx, cy), body_r)
        
        # 内部纹理
        for i in range(4):
            inner_angle = self.pulse + i * math.pi / 2
            inner_r = body_r * 0.6
            ix = cx + math.cos(inner_angle) * inner_r * 0.5
            iy = cy + math.sin(inner_angle) * inner_r * 0.5
            pygame.draw.circle(self.image, (*theme["pulse"], 150), (int(ix), int(iy)), 4)
        
        pygame.draw.circle(self.image, theme["pulse"], (cx, cy), body_r - 5)
        
        # 眼睛
        eye_y = cy - 3
        pygame.draw.circle(self.image, (255, 255, 255), (cx - 5, eye_y), 4)
        pygame.draw.circle(self.image, (255, 255, 255), (cx + 5, eye_y), 4)
        
        # 瞳孔朝向目标
        look_x, look_y = 0, 0
        if self.target and self.target.alive():
            dx = self.target.rect.centerx - self.float_x
            dy = self.target.rect.centery - self.float_y
            d = math.hypot(dx, dy)
            if d > 0:
                look_x = dx / d * 1.5
                look_y = dy / d * 1.5
        
        pygame.draw.circle(self.image, (0, 0, 0), (int(cx - 5 + look_x), int(eye_y + look_y)), 2)
        pygame.draw.circle(self.image, (0, 0, 0), (int(cx + 5 + look_x), int(eye_y + look_y)), 2)
        
        # 追踪时的怒气
        if is_chasing:
            anger_pulse = abs(math.sin(self.pulse * 3)) * 0.5 + 0.5
            pygame.draw.line(self.image, (255, int(50 * anger_pulse), 50),
                           (cx - 6, cy - 14), (cx + 6, cy - 11), 2)
            pygame.draw.line(self.image, (255, int(50 * anger_pulse), 50),
                           (cx - 6, cy - 11), (cx + 6, cy - 14), 2)
        self.rect = self.image.get_rect(center=(int(self.float_x), int(self.float_y)))
    
    def update(self):
        self.frame += 1
        
        # 传送闪烁
        if self.frame <= self.teleport_flash:
            self._render_teleport()
            return
        
        # 生成子体
        if self.spawns_created < self.max_spawns:
            if (self.frame - self.teleport_flash) % self.spawn_interval == 0:
                angle = self.spawns_created * math.pi * 2 / self.max_spawns
                dist = 60
                sx = self.float_x + math.cos(angle) * dist
                sy = self.float_y + math.sin(angle) * dist
                spawn = SlimeLegionSpawn(sx, sy, self.owner, self.style)
                all_sprites.add(spawn)
                self.spawns_created += 1
        
        self._render()
        
        if self.spawns_created >= self.max_spawns and self.frame > 100:
            self.kill()
    
    def _render_teleport(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        cx, cy = 50, 50
        prog = self.frame / self.teleport_flash
        
        # 传送光环
        flash_alpha = int(255 * (1 - prog))
        ring_r = int(30 + prog * 40)
        pygame.draw.circle(self.image, (*theme["pulse"], flash_alpha), (cx, cy), ring_r, 4)
        pygame.draw.circle(self.image, (*theme["star"], flash_alpha), (cx, cy), int(ring_r * 0.6))
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        cx, cy = 50, 50
        t = self.frame * 0.1
        
        # 召唤阵
        pulse = abs(math.sin(t)) * 0.2 + 0.8
        for i in range(3):
            ring_r = int((30 + i * 15) * pulse)
            pygame.draw.circle(self.image, (*theme["domain"], 100 - i * 25), (cx, cy), ring_r, 2)
        
        # 五芒星
        for i in range(5):
            angle = i * math.pi * 2 / 5 - math.pi / 2 + t * 0.3
            px = cx + math.cos(angle) * 35
            py = cy + math.sin(angle) * 35
            pygame.draw.circle(self.image, theme["star"], (int(px), int(py)), 4)


class SpawnExplosion(pygame.sprite.Sprite):
    """子体自爆特效"""
    
    def __init__(self, x, y, style="default"):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.style = style
        self.frame = 0
        self.lifetime = 25
        self.image = pygame.Surface((180, 180), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        cx, cy = 90, 90
        prog = self.frame / self.lifetime
        
        # 爆炸扩散
        for i in range(4):
            ring_r = int(20 + prog * 60 + i * 10)
            alpha = int(220 * (1 - prog) * (1 - i * 0.2))
            if alpha > 0:
                pygame.draw.circle(self.image, (*theme["pulse"], alpha), (cx, cy), ring_r, 3)
        
        # 核心闪光
        if prog < 0.3:
            flash_r = int(30 * (1 - prog / 0.3))
            pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), flash_r)
        
        # 飞溅凝胶
        for i in range(8):
            angle = i * math.pi / 4
            splash_dist = prog * 70
            sx = cx + math.cos(angle) * splash_dist
            sy = cy + math.sin(angle) * splash_dist
            splash_r = int(8 * (1 - prog))
            if splash_r > 0:
                pygame.draw.circle(self.image, (*theme["core"], int(200 * (1 - prog))), (int(sx), int(sy)), splash_r)


# ==================== 辅助特效类 ====================

class StarDustTrail(pygame.sprite.Sprite):
    """星尘拖尾特效"""
    def __init__(self, x, y, style="default"):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 20
        self.style = style
        
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        cx, cy = 40, 40
        progress = self.frame / self.lifetime
        alpha = int(200 * (1 - progress))
        t = self.frame * 0.2
        
        # ========== 根据涂装渲染不同的拖尾特效 ==========
        if self.style == "cosmic":
            # 星河拖尾 - 螺旋星尘
            for i in range(5):
                r = int((18 - i * 3) * (1 - progress * 0.5))
                if r > 0:
                    pygame.draw.circle(self.image, (*theme["gel"], alpha - i * 30), (cx, cy), r)
            for i in range(6):
                s_angle = t + i * math.pi / 3
                s_r = 20 * (1 - progress)
                sx = cx + math.cos(s_angle) * s_r
                sy = cy + math.sin(s_angle) * s_r
                pygame.draw.circle(self.image, (*theme["star"], alpha // 2), (int(sx), int(sy)), 2)
        
        elif self.style == "void":
            # 虚空拖尾 - 黑暗涟漪
            for i in range(4):
                r = int((20 - i * 4) * (1 - progress * 0.4))
                if r > 0:
                    pygame.draw.circle(self.image, (*theme["gel"], alpha - i * 40), (cx, cy), r, 2)
            pygame.draw.circle(self.image, (20, 10, 40, alpha), (cx, cy), int(10 * (1 - progress)))
        
        elif self.style == "crystal":
            # 水晶拖尾 - 棱镜碎片
            for i in range(6):
                angle = i * math.pi / 3 + t
                r = 15 * (1 - progress)
                px = cx + math.cos(angle) * r
                py = cy + math.sin(angle) * r
                pygame.draw.polygon(self.image, (*theme["star"], alpha - 30), [
                    (int(px), int(py - 4)), (int(px + 3), int(py + 2)), (int(px - 3), int(py + 2))
                ])
            pygame.draw.circle(self.image, (*theme["pulse"], alpha), (cx, cy), int(8 * (1 - progress * 0.5)))
        
        elif self.style == "flame":
            # 炽焰拖尾 - 火焰余烬
            for i in range(5):
                r = int((16 - i * 3) * (1 - progress * 0.4))
                if r > 0:
                    pygame.draw.circle(self.image, (*theme["gel"], alpha - i * 35), (cx, cy), r)
            # 火星
            for i in range(4):
                spark_x = cx + (random.random() - 0.5) * 20
                spark_y = cy + (random.random() - 0.5) * 20
                pygame.draw.circle(self.image, (*theme["star"], alpha // 2), (int(spark_x), int(spark_y)), 2)
        
        elif self.style == "rainbow":
            # 彩虹拖尾 - 七彩光斑
            rainbow = [(255, 80, 80), (255, 160, 60), (255, 240, 80),
                      (80, 255, 130), (80, 180, 255), (130, 100, 255), (200, 100, 255)]
            for i in range(5):
                r = int((18 - i * 3) * (1 - progress * 0.5))
                if r > 0:
                    col = rainbow[(i + int(t)) % 7]
                    pygame.draw.circle(self.image, (*col, alpha - i * 30), (cx, cy), r)
        
        else:
            # 默认拖尾
            for i in range(5):
                r = int((15 - i * 3) * (1 - progress * 0.5))
                if r > 0:
                    pygame.draw.circle(self.image, (*theme["star"], alpha - i * 30), (cx, cy), r)


# ==================== 击杀特效 ====================
class StarSlimeDownEffect(pygame.sprite.Sprite):
    """击杀彩蛋特效 - Star Slime Down!"""
    
    def __init__(self, x, y, style="default"):
        super().__init__()
        self.float_x, self.float_y = x, y
        self.frame = 0
        self.lifetime = 60
        self.style = style
        
        self.image = pygame.Surface((240, 140), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.frame += 1
        if self.frame >= self.lifetime:
            self.kill()
            return
        self._render()
    
    def _render(self):
        self.image.fill((0, 0, 0, 0))
        theme = get_theme(self.style)
        progress = self.frame / self.lifetime
        cx, cy = 120, 70
        t = self.frame * 0.15
        alpha = int(255 * (1 - progress))
        
        # ========== 根据涂装渲染不同的击杀特效 ==========
        if self.style == "cosmic":
            # 星河爆发 - 超新星
            for ring in range(4):
                ring_r = int(30 + ring * 20 + progress * 50)
                ring_alpha = max(0, alpha - ring * 50)
                if ring_alpha > 0:
                    pygame.draw.circle(self.image, (*theme["domain"], ring_alpha), (cx, cy), ring_r, 2)
            
            for i in range(12):
                angle = i * math.pi / 6 + t
                ray_len = 80 * (1 - progress * 0.3)
                rx = cx + math.cos(angle) * ray_len
                ry = cy + math.sin(angle) * ray_len
                pygame.draw.line(self.image, (*theme["star"], alpha), (cx, cy), (int(rx), int(ry)), 3)
                # 星尘端点
                pygame.draw.circle(self.image, (*theme["pulse"], alpha // 2), (int(rx), int(ry)), 4)
            
            flash_r = int(40 * (1 - progress * 0.7))
            if flash_r > 0:
                pygame.draw.circle(self.image, theme["core"], (cx, cy), flash_r)
                pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), flash_r // 2)
        
        elif self.style == "void":
            # 虚空坍缩 - 黑洞吞噬
            for ring in range(5):
                ring_r = int(50 - ring * 8 - progress * 20)
                if ring_r > 0:
                    pygame.draw.circle(self.image, (*theme["gel"], alpha - ring * 40), (cx, cy), ring_r, 3)
            
            # 吸入碎片
            for i in range(10):
                p_angle = t + i * math.pi / 5
                p_r = 60 * (1 - progress)
                px = cx + math.cos(p_angle) * p_r
                py = cy + math.sin(p_angle) * p_r
                pygame.draw.circle(self.image, (*theme["domain"], alpha // 2), (int(px), int(py)), 3)
            
            core_r = int(25 * (1 - progress))
            if core_r > 0:
                pygame.draw.circle(self.image, (10, 5, 25), (cx, cy), core_r)
                pygame.draw.circle(self.image, theme["pulse"], (cx, cy), core_r, 2)
        
        elif self.style == "crystal":
            # 水晶碎裂 - 棱镜爆发
            for i in range(8):
                angle = i * math.pi / 4 + progress * 0.5
                shard_dist = 30 + progress * 60
                sx = cx + math.cos(angle) * shard_dist
                sy = cy + math.sin(angle) * shard_dist
                shard_size = int(12 * (1 - progress * 0.5))
                if shard_size > 2:
                    pygame.draw.polygon(self.image, (*theme["star"], alpha), [
                        (int(sx), int(sy - shard_size)),
                        (int(sx + shard_size * 0.6), int(sy + shard_size * 0.3)),
                        (int(sx - shard_size * 0.6), int(sy + shard_size * 0.3))
                    ])
            
            flash_r = int(35 * (1 - progress * 0.6))
            if flash_r > 0:
                pygame.draw.circle(self.image, theme["core"], (cx, cy), flash_r)
                pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), flash_r // 2)
        
        elif self.style == "flame":
            # 炽焰爆炸 - 火焰风暴
            for ring in range(3):
                ring_r = int(25 + ring * 15 + progress * 40)
                ring_alpha = max(0, alpha - ring * 60)
                if ring_alpha > 0:
                    pygame.draw.circle(self.image, (*theme["gel"], ring_alpha), (cx, cy), ring_r)
            
            for i in range(10):
                flame_angle = i * math.pi / 5 + t
                flame_len = 50 + int(math.sin(t * 2 + i) * 15)
                flame_len = int(flame_len * (1 - progress * 0.4))
                fx = cx + math.cos(flame_angle) * 20
                fy = cy + math.sin(flame_angle) * 20
                pygame.draw.polygon(self.image, (*theme["domain"], alpha), [
                    (int(fx), int(fy)),
                    (int(fx + math.cos(flame_angle) * flame_len), int(fy + math.sin(flame_angle) * flame_len)),
                    (int(fx + math.cos(flame_angle + 0.2) * 8), int(fy + math.sin(flame_angle + 0.2) * 8))
                ])
            
            flash_r = int(35 * (1 - progress * 0.5))
            if flash_r > 0:
                pygame.draw.circle(self.image, theme["core"], (cx, cy), flash_r)
                pygame.draw.circle(self.image, (255, 255, 200), (cx, cy), flash_r // 2)
        
        elif self.style == "rainbow":
            # 彩虹爆发 - 七彩光芒
            rainbow = [(255, 80, 80), (255, 160, 60), (255, 240, 80),
                      (80, 255, 130), (80, 180, 255), (130, 100, 255), (200, 100, 255)]
            
            for i, col in enumerate(rainbow):
                ring_r = int(25 + i * 10 + progress * 40)
                ring_alpha = max(0, alpha - i * 25)
                if ring_alpha > 0:
                    pygame.draw.circle(self.image, (*col, ring_alpha), (cx, cy), ring_r, 3)
            
            for i in range(14):
                angle = i * math.pi / 7 + t
                ray_len = 70 * (1 - progress * 0.3)
                rx = cx + math.cos(angle) * ray_len
                ry = cy + math.sin(angle) * ray_len
                col = rainbow[i % 7]
                pygame.draw.line(self.image, (*col, alpha), (cx, cy), (int(rx), int(ry)), 2)
            
            color_idx = int(t * 2) % 7
            flash_r = int(30 * (1 - progress * 0.5))
            if flash_r > 0:
                pygame.draw.circle(self.image, rainbow[color_idx], (cx, cy), flash_r)
                pygame.draw.circle(self.image, (255, 255, 255), (cx, cy), flash_r // 2)
        
        else:
            # 默认击杀特效
            for i in range(8):
                angle = i * math.pi / 4 + t
                ray_len = 60 * (1 - progress * 0.5)
                rx = cx + math.cos(angle) * ray_len
                ry = cy + math.sin(angle) * ray_len
                pygame.draw.line(self.image, (*theme["star"], alpha), (cx, cy), (int(rx), int(ry)), 3)
            
            flash_r = int(30 * (1 - progress))
            if flash_r > 0:
                pygame.draw.circle(self.image, (*theme["pulse"], alpha), (cx, cy), flash_r)


# ==================== 子弹涂装预览 ====================
def render_slime_bullet_preview(surface, effects, color, center_x, center_y, size, x, y, plane_id=None):
    """
    渲染末世星凝·史莱姆子弹预览效果
    
    Args:
        surface: pygame绘图表面
        effects: 效果列表
        color: 主题颜色
        center_x, center_y: 中心坐标
        size: 预览尺寸
        x, y: 左上角坐标
        plane_id: 机体ID，用于判断是否渲染该机体的默认子弹样式
    
    Returns:
        bool: 如果渲染了效果返回True，否则False
    """
    # 检查是否是Slime相关效果
    slime_effects = [
        # 子弹主题effects
        "gravity_pulse", "gel_flow",          # slime_star_gel (default)
        "nebula_swirl", "cosmic_trail",       # slime_cosmic_gel
        "void_consume", "dark_matter",        # slime_void_gel
        "prism_refract", "crystal_scatter",   # slime_crystal_gel
        "acid_erosion", "toxic_bubble",       # slime_toxic_gel
        "royal_aura", "golden_trail",         # slime_royal_gel
        "blood_drip", "crimson_pulse",        # slime_blood_gel
        "ice_crystal", "freeze_trail",        # slime_ice_gel
        "magma_flow", "fire_burst",           # slime_flame_gel
        "phase_flicker", "ghost_fade",        # slime_phantom_gel
        "rainbow_shift", "prismatic_burst",   # slime_rainbow_gel
        "apocalypse_rift", "doom_pulse",      # slime_abyss_gel
    ]
    
    # 检查是否有Slime效果，或者当前机体是slime（使用非专属涂装时也渲染默认样式）
    has_slime_effect = any(effect in effects for effect in slime_effects)
    is_slime_plane = (plane_id == "slime")
    
    if not has_slime_effect and not is_slime_plane:
        return False
    
    t = pygame.time.get_ticks() / 1000.0
    frame = int(t * 30)
    
    # 渲染子弹效果
    bullet_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    cx, cy = size, size
    
    # 动态脉冲
    pulse = abs(math.sin(t * 3)) * 0.2 + 0.9
    
    # ===== 判断子弹类型并渲染对应效果 =====
    
    # 宇宙星云 - 星云凝胶
    if "nebula_swirl" in effects or "cosmic_trail" in effects:
        cosmic_purple = (180, 100, 255)
        cosmic_blue = (100, 80, 200)
        
        # 星云光晕
        for i in range(4):
            glow_r = int((size // 3 + i * 4) * pulse)
            alpha = 100 - i * 20
            pygame.draw.circle(bullet_surf, (*cosmic_purple, alpha), (cx, cy), glow_r)
        
        # 凝胶核心
        core_r = int(size // 4 * pulse)
        pygame.draw.circle(bullet_surf, cosmic_purple, (cx, cy), core_r)
        pygame.draw.circle(bullet_surf, (255, 200, 255), (cx, cy), core_r // 2)
        
        # 星尘环绕
        for i in range(6):
            angle = t * 2 + i * math.pi / 3
            dist = size // 4 + math.sin(t * 3 + i) * 4
            sx = cx + math.cos(angle) * dist
            sy = cy + math.sin(angle) * dist
            pygame.draw.circle(bullet_surf, (255, 220, 255, 180), (int(sx), int(sy)), 3)
        
        # 螺旋星云
        for arm in range(3):
            for seg in range(5):
                prog = seg / 5
                spiral_angle = t + arm * math.pi * 2 / 3 + prog * math.pi
                spiral_r = size // 6 + prog * size // 4
                sx = cx + math.cos(spiral_angle) * spiral_r
                sy = cy + math.sin(spiral_angle) * spiral_r
                pygame.draw.circle(bullet_surf, (*cosmic_blue, int(150 * (1 - prog))), 
                                 (int(sx), int(sy)), 2)
    
    # 虚空深渊 - 黑洞凝胶
    elif "void_consume" in effects or "dark_matter" in effects:
        void_purple = (80, 40, 120)
        void_black = (20, 10, 40)
        
        # 事件视界光环
        for i in range(3):
            ev_r = int((size // 3 + i * 5) * pulse)
            pygame.draw.circle(bullet_surf, (*void_purple, 80 - i * 20), (cx, cy), ev_r, 2)
        
        # 黑洞核心
        pygame.draw.circle(bullet_surf, void_black, (cx, cy), int(size // 4))
        pygame.draw.circle(bullet_surf, void_purple, (cx, cy), int(size // 4), 2)
        
        # 被吸入的粒子
        for i in range(8):
            p_angle = t * 1.5 + i * math.pi / 4
            p_r = size // 3 - (t * 20 + i * 5) % (size // 4)
            px = cx + math.cos(p_angle) * p_r
            py = cy + math.sin(p_angle) * p_r
            pygame.draw.circle(bullet_surf, (*void_purple, 150), (int(px), int(py)), 2)
    
    # 晶体凝华 - 水晶凝胶
    elif "prism_refract" in effects or "crystal_scatter" in effects:
        crystal_blue = (150, 200, 255)
        crystal_white = (220, 240, 255)
        
        # 棱镜光芒
        for i in range(6):
            angle = i * math.pi / 3 + t * 0.5
            ray_len = size // 3 * pulse
            rx = cx + math.cos(angle) * ray_len
            ry = cy + math.sin(angle) * ray_len
            pygame.draw.line(bullet_surf, (*crystal_blue, 150), (cx, cy), (int(rx), int(ry)), 2)
        
        # 六边形晶体
        hex_r = int(size // 4 * pulse)
        hex_points = []
        for i in range(6):
            angle = i * math.pi / 3 + t * 0.3
            hx = cx + math.cos(angle) * hex_r
            hy = cy + math.sin(angle) * hex_r
            hex_points.append((int(hx), int(hy)))
        pygame.draw.polygon(bullet_surf, crystal_blue, hex_points)
        pygame.draw.polygon(bullet_surf, crystal_white, hex_points, 2)
        
        # 内核
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx, cy), int(size // 8))
    
    # 剧毒腐蚀 - 酸液凝胶
    elif "acid_erosion" in effects or "toxic_bubble" in effects:
        toxic_green = (100, 200, 50)
        acid_yellow = (180, 220, 50)
        
        # 毒雾光晕
        for i in range(3):
            fog_r = int((size // 3 + i * 5 + math.sin(t * 2 + i) * 3) * pulse)
            pygame.draw.circle(bullet_surf, (*toxic_green, 70 - i * 15), (cx, cy), fog_r)
        
        # 凝胶核心
        core_r = int(size // 4 * pulse)
        pygame.draw.circle(bullet_surf, toxic_green, (cx, cy), core_r)
        pygame.draw.circle(bullet_surf, acid_yellow, (cx, cy), core_r - 4)
        
        # 酸液气泡
        for i in range(5):
            b_angle = t * 1.5 + i * math.pi * 0.4
            b_r = size // 4 + math.sin(t * 3 + i) * 5
            bx = cx + math.cos(b_angle) * b_r
            by = cy + math.sin(b_angle) * b_r
            bubble_size = 4 + int(math.sin(t * 4 + i) * 2)
            pygame.draw.circle(bullet_surf, (*toxic_green, 150), (int(bx), int(by)), bubble_size)
    
    # 皇家至尊 - 王冠凝胶
    elif "royal_aura" in effects or "golden_trail" in effects:
        royal_purple = (160, 80, 200)
        royal_gold = (255, 215, 0)
        
        # 皇家光芒
        for i in range(8):
            angle = i * math.pi / 4 + t * 0.5
            ray_len = size // 3 + math.sin(t * 2 + i) * 5
            rx = cx + math.cos(angle) * ray_len
            ry = cy + math.sin(angle) * ray_len
            pygame.draw.line(bullet_surf, (*royal_gold, 180), (cx, cy), (int(rx), int(ry)), 2)
        
        # 凝胶核心
        core_r = int(size // 4 * pulse)
        pygame.draw.circle(bullet_surf, royal_purple, (cx, cy), core_r)
        
        # 王冠
        crown_y = cy - core_r - 5
        pygame.draw.polygon(bullet_surf, royal_gold, [
            (cx - 8, crown_y + 8), (cx - 6, crown_y), (cx, crown_y + 5),
            (cx + 6, crown_y), (cx + 8, crown_y + 8)
        ])
        pygame.draw.circle(bullet_surf, royal_gold, (cx, crown_y - 2), 3)
    
    # 血月猩红 - 血染凝胶
    elif "blood_drip" in effects or "crimson_pulse" in effects:
        blood_red = (200, 40, 60)
        blood_dark = (150, 20, 80)
        
        # 血色光晕
        for i in range(3):
            pulse_r = int((size // 3 + i * 4) * pulse)
            pygame.draw.circle(bullet_surf, (*blood_red, 90 - i * 25), (cx, cy), pulse_r)
        
        # 凝胶核心
        core_r = int(size // 4 * pulse)
        pygame.draw.circle(bullet_surf, blood_red, (cx, cy), core_r)
        pygame.draw.circle(bullet_surf, blood_dark, (cx, cy), core_r - 4)
        
        # 滴血效果
        drip_y = cy + core_r + abs(math.sin(t * 4)) * 6
        pygame.draw.circle(bullet_surf, blood_red, (cx, int(drip_y)), 4)
        pygame.draw.ellipse(bullet_surf, blood_red, (cx - 3, cy + core_r - 2, 6, 8))
    
    # 极寒冰霜 - 冰晶凝胶
    elif "ice_crystal" in effects or "freeze_trail" in effects:
        ice_blue = (100, 200, 255)
        frost_white = (200, 240, 255)
        
        # 冰霜光晕
        for i in range(3):
            frost_r = int((size // 3 + i * 5) * pulse)
            pygame.draw.circle(bullet_surf, (*ice_blue, 80 - i * 20), (cx, cy), frost_r)
        
        # 六边形冰晶
        crystal_r = int(size // 4 * pulse)
        for i in range(6):
            angle = i * math.pi / 3 + t * 0.3
            x1 = cx + math.cos(angle) * crystal_r
            y1 = cy + math.sin(angle) * crystal_r
            x2 = cx + math.cos(angle + math.pi / 3) * crystal_r
            y2 = cy + math.sin(angle + math.pi / 3) * crystal_r
            pygame.draw.line(bullet_surf, ice_blue, (int(x1), int(y1)), (int(x2), int(y2)), 2)
        
        # 冰晶刺
        for i in range(6):
            spike_angle = i * math.pi / 3 + t * 0.3
            spike_len = crystal_r + 8 + math.sin(t * 2 + i) * 3
            sx = cx + math.cos(spike_angle) * spike_len
            sy = cy + math.sin(spike_angle) * spike_len
            pygame.draw.line(bullet_surf, frost_white, (cx, cy), (int(sx), int(sy)), 1)
        
        # 内核
        pygame.draw.circle(bullet_surf, frost_white, (cx, cy), int(size // 8))
    
    # 烈焰熔岩 - 火焰凝胶
    elif "magma_flow" in effects or "fire_burst" in effects:
        flame_orange = (255, 120, 30)
        magma_red = (255, 60, 20)
        
        # 火焰光晕
        for i in range(4):
            heat_r = int((size // 3 + i * 4 + math.sin(t * 3 + i) * 3) * pulse)
            pygame.draw.circle(bullet_surf, (*flame_orange, 80 - i * 18), (cx, cy), heat_r)
        
        # 凝胶核心
        core_r = int(size // 4 * pulse)
        pygame.draw.circle(bullet_surf, magma_red, (cx, cy), core_r)
        pygame.draw.circle(bullet_surf, (255, 200, 100), (cx, cy), core_r // 2)
        
        # 火焰舞动
        for i in range(6):
            flame_angle = i * math.pi / 3 + math.sin(t * 4 + i) * 0.3
            flame_h = 10 + int(math.sin(t * 5 + i) * 5)
            fx = cx + math.cos(flame_angle) * (core_r + 2)
            fy = cy + math.sin(flame_angle) * (core_r + 2)
            pygame.draw.polygon(bullet_surf, flame_orange, [
                (int(fx), int(fy)),
                (int(fx + math.cos(flame_angle) * flame_h), int(fy + math.sin(flame_angle) * flame_h)),
                (int(fx + math.cos(flame_angle + 0.3) * 4), int(fy + math.sin(flame_angle + 0.3) * 4))
            ])
    
    # 幽灵虚影 - 幽影凝胶
    elif "phase_flicker" in effects or "ghost_fade" in effects:
        ghost_gray = (120, 140, 160)
        ghost_green = (100, 200, 150)
        
        # 幽影光晕（闪烁）
        flicker_alpha = int(60 + 40 * math.sin(t * 8))
        for i in range(3):
            ghost_r = int((size // 3 + i * 5) * pulse)
            pygame.draw.circle(bullet_surf, (*ghost_gray, flicker_alpha - i * 15), (cx, cy), ghost_r)
        
        # 凝胶核心（半透明）
        core_r = int(size // 4 * pulse)
        core_alpha = int(150 + 50 * math.sin(t * 6))
        ghost_surf = pygame.Surface((core_r * 2, core_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(ghost_surf, (*ghost_gray, core_alpha), (core_r, core_r), core_r)
        pygame.draw.circle(ghost_surf, (*ghost_green, core_alpha // 2), (core_r, core_r), core_r // 2)
        bullet_surf.blit(ghost_surf, (cx - core_r, cy - core_r))
        
        # 鬼火粒子
        for i in range(4):
            g_angle = t * 1.5 + i * math.pi / 2
            g_r = size // 4 + math.sin(t * 3 + i) * 5
            gx = cx + math.cos(g_angle) * g_r
            gy = cy + math.sin(g_angle) * g_r
            pygame.draw.circle(bullet_surf, (*ghost_green, 120), (int(gx), int(gy)), 3)
    
    # 彩虹凝华 - 七彩凝胶
    elif "rainbow_shift" in effects or "prismatic_burst" in effects:
        rainbow = [(255, 80, 80), (255, 160, 60), (255, 240, 80),
                  (80, 255, 130), (80, 180, 255), (130, 100, 255), (200, 100, 255)]
        
        # 彩虹光环
        for i, col in enumerate(rainbow):
            ring_r = int((size // 6 + i * 4) * pulse)
            pygame.draw.circle(bullet_surf, (*col, 140), (cx, cy), ring_r, 2)
        
        # 流转核心
        color_idx = int(t * 3) % 7
        core_r = int(size // 4 * pulse)
        pygame.draw.circle(bullet_surf, rainbow[color_idx], (cx, cy), core_r)
        pygame.draw.circle(bullet_surf, rainbow[(color_idx + 3) % 7], (cx, cy), core_r // 2)
        pygame.draw.circle(bullet_surf, (255, 255, 255), (cx, cy), core_r // 4)
        
        # 彩虹粒子
        for i in range(7):
            p_angle = t + i * math.pi * 2 / 7
            p_r = size // 3
            px = cx + math.cos(p_angle) * p_r
            py = cy + math.sin(p_angle) * p_r
            pygame.draw.circle(bullet_surf, rainbow[i], (int(px), int(py)), 3)
    
    # 末世终焉 - 末世凝胶
    elif "apocalypse_rift" in effects or "doom_pulse" in effects:
        abyss_purple = (80, 40, 140)
        abyss_black = (30, 20, 60)
        
        # 末世光晕
        for i in range(4):
            doom_r = int((size // 3 + i * 5) * pulse)
            pygame.draw.circle(bullet_surf, (*abyss_purple, 100 - i * 22), (cx, cy), doom_r)
        
        # 裂隙效果
        for i in range(6):
            rift_angle = i * math.pi / 3 + t * 0.8
            rift_len = size // 3 + math.sin(t * 2 + i) * 5
            rx = cx + math.cos(rift_angle) * rift_len
            ry = cy + math.sin(rift_angle) * rift_len
            pygame.draw.line(bullet_surf, abyss_purple, (cx, cy), (int(rx), int(ry)), 3)
            pygame.draw.line(bullet_surf, abyss_black, (cx, cy), 
                           (int(cx + math.cos(rift_angle) * rift_len * 0.6), 
                            int(cy + math.sin(rift_angle) * rift_len * 0.6)), 1)
        
        # 末世核心
        core_r = int(size // 4 * pulse)
        pygame.draw.circle(bullet_surf, abyss_black, (cx, cy), core_r)
        pygame.draw.circle(bullet_surf, abyss_purple, (cx, cy), core_r, 2)
        pygame.draw.circle(bullet_surf, (120, 80, 180), (cx, cy), core_r // 2)
    
    # 默认 - 星凝原质
    else:
        gel_purple = (120, 80, 200)
        gel_blue = (60, 140, 220)
        
        # 引力光晕
        for i in range(3):
            glow_r = int((size // 3 + i * 5) * pulse)
            pygame.draw.circle(bullet_surf, (*gel_purple, 80 - i * 20), (cx, cy), glow_r)
        
        # 凝胶核心
        core_r = int(size // 4 * pulse)
        pygame.draw.circle(bullet_surf, gel_purple, (cx, cy), core_r)
        pygame.draw.circle(bullet_surf, gel_blue, (cx, cy), core_r - 4)
        pygame.draw.circle(bullet_surf, (200, 180, 255), (cx - 4, cy - 4), 4)
        
        # 流动纹理
        for i in range(4):
            flow_angle = t + i * math.pi / 2
            flow_r = core_r - 3
            fx = cx + math.cos(flow_angle) * flow_r * 0.5
            fy = cy + math.sin(flow_angle) * flow_r * 0.5
            pygame.draw.circle(bullet_surf, (*gel_blue, 150), (int(fx), int(fy)), 2)
    
    # 绘制到目标表面
    surface.blit(bullet_surf, (x - size // 2, y - size // 2))
    return True
