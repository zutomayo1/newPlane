# -*- coding: utf-8 -*-
"""
晶体粉碎者·CRUSHER 弹幕系统
重型钻机 + 冲撞 + 牵引

技能列表：
- F技能：相位冲撞 (Warp Dash) - 向前冲刺，撞碎敌人护盾
- G技能：牵引光束 (Tractor Beam) - 扇形光波，拉拽敌人
- C技能：共振破碎 (Resonance Break) - 全屏高频音波，粉碎一切
"""
import pygame
import math
import random
from config import WIDTH, HEIGHT, all_sprites, bullets, mobs, enemy_bullets

_TRANSPARENT = (0, 0, 0, 0)

# ==================== 颜色定义 ====================
CRYSTAL_PURPLE = (138, 43, 226)
CRYSTAL_BRIGHT = (180, 120, 255)
LASER_GLOW = (230, 230, 250)
VOID_PURPLE = (75, 0, 130)

# ==================== 预缓存 ====================
_bullet_cache = {}

def _get_drill_bullet(size=14):
    """获取钻头形子弹图像"""
    cache_key = ("drill", size)
    if cache_key not in _bullet_cache:
        surf = pygame.Surface((size, size * 2), pygame.SRCALPHA)
        # 钻头形状
        pts = [
            (size // 2, 0),
            (size - 2, size),
            (size // 2, size * 2 - 2),
            (2, size),
        ]
        pygame.draw.polygon(surf, CRYSTAL_PURPLE, pts)
        pygame.draw.polygon(surf, CRYSTAL_BRIGHT, pts, 1)
        # 中心亮点
        pygame.draw.circle(surf, LASER_GLOW, (size // 2, size), size // 4)
        _bullet_cache[cache_key] = surf
    return _bullet_cache[cache_key]


def _can_convert_alpha():
    return pygame.display.get_init() and pygame.display.get_surface() is not None


def _make_sheet_frames(frame_w, frame_h, frame_count):
    """创建按帧垂直堆叠的 sprite sheet，并返回 (sheet, frames)"""
    sheet = pygame.Surface((frame_w, frame_h * frame_count), pygame.SRCALPHA)
    if _can_convert_alpha():
        sheet = sheet.convert_alpha()
    frames = [sheet.subsurface(pygame.Rect(0, i * frame_h, frame_w, frame_h)) for i in range(frame_count)]
    return sheet, frames


# ==================== 主武器：毁灭射线 ====================
class DesolationBeamBullet(pygame.sprite.Sprite):
    """
    毁灭射线 - 瞬发穿透激光
    特性：无飞行时间，穿透无限，超粗光束
    """
    
    def __init__(self, x, y, damage, owner=None, style="crusher_default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.is_enemy = False
        self.style = style
        
        self.x = float(x)
        self.y = float(y)
        self.lifetime = 15  # 更长显示时间
        self.max_life = 15
        self.hit_set = set()
        
        # 射线参数 - 更粗更明显
        self.beam_width = 20  # 更粗的光束
        self.beam_length = y + 50
        
        # 预渲染帧动画（性能关键：普攻会高频触发）
        canvas_width = 120
        frame_h = int(self.beam_length) + 60
        self.cx = canvas_width // 2
        self._sheet, self._frames = _make_sheet_frames(canvas_width, frame_h, self.max_life)
        self.image = self._frames[0]
        self.rect = self.image.get_rect(midbottom=(int(x), int(y) + 30))

        # 实例级确定性随机：保证观感仍然“抖动闪烁”，但不在 update 每帧调用 random
        self._rng = random.Random(random.randrange(1 << 30))

        # 生成电弧（固定结构）
        self.arcs = []
        for _ in range(6):
            self.arcs.append({
                'offset': self._rng.randint(-25, 25),
                'y': self._rng.randint(50, max(60, int(self.beam_length) - 50)),
                'length': self._rng.randint(20, 40)
            })

        # 预生成每帧抖动/亮度
        self._arc_flicker = [[self._rng.uniform(0.5, 1.0) for _ in range(len(self.arcs))] for _ in range(self.max_life)]
        self._arc_jitter = [[self._rng.randint(-8, 8) for _ in range(len(self.arcs))] for _ in range(self.max_life)]

        # 预渲染所有帧
        for fi in range(self.max_life):
            lifetime = self.max_life - fi
            self._draw_beam(self._frames[fi], lifetime, fi)
        
        # 屏幕微震
        try:
            from sprites import screen_shake
            screen_shake(3, 2)
        except:
            pass
        
        # 瞬间命中所有敌人
        self._hit_all_enemies()
        
        all_sprites.add(self)
        bullets.add(self)
    
    def _hit_all_enemies(self):
        """瞬间命中射线路径上的所有敌人"""
        beam_left = self.x - self.beam_width * 2
        beam_right = self.x + self.beam_width * 2
        
        for m in mobs:
            if m.alive():
                mx = m.rect.centerx
                my = m.rect.centery
                if beam_left <= mx <= beam_right and my < self.y:
                    if id(m) not in self.hit_set:
                        m.take_damage(self.damage)
                        self.hit_set.add(id(m))
                        BeamHitEffect(mx, my)
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return

        idx = self.max_life - self.lifetime
        if 0 <= idx < self.max_life:
            self.image = self._frames[idx]
    
    def _draw_beam(self, target_surf, lifetime, frame_index):
        """绘制超强光束效果"""
        target_surf.fill(_TRANSPARENT)

        progress = 1 - lifetime / self.max_life
        pulse = abs(math.sin(lifetime * 0.4))
        cx = self.cx
        length = int(self.beam_length)
        offset_y = 30  # 画布偏移
        
        # === 第1层：扩散光晕 ===
        outer_width = int(20 + pulse * 6)
        outer_alpha = int(60 * (1 - progress * 0.6))
        pygame.draw.line(target_surf, (*CRYSTAL_PURPLE, outer_alpha), 
                        (cx, offset_y), (cx, length + offset_y), outer_width)
        
        # === 第2层：能量场 ===
        field_width = int(14 + pulse * 4)
        field_alpha = int(100 * (1 - progress * 0.5))
        pygame.draw.line(target_surf, (*LASER_GLOW, field_alpha), 
                        (cx, offset_y), (cx, length + offset_y), field_width)
        
        # === 第3层：主光束 ===
        core_width = int(8 + pulse * 3)
        pygame.draw.line(target_surf, CRYSTAL_BRIGHT, 
                        (cx, offset_y), (cx, length + offset_y), core_width)
        
        # === 第4层：白热核心 ===
        inner_width = int(3 + pulse * 2)
        pygame.draw.line(target_surf, (255, 255, 255), 
                        (cx, offset_y), (cx, length + offset_y), inner_width)
        
        # === 侧翼电弧 ===
        flicker_row = self._arc_flicker[frame_index]
        jitter_row = self._arc_jitter[frame_index]
        for ai, arc in enumerate(self.arcs):
            arc_alpha = int(180 * (1 - progress * 0.5) * flicker_row[ai])
            arc_y = arc['y'] + offset_y
            j = jitter_row[ai]
            # 左侧电弧
            pygame.draw.line(target_surf, (*CRYSTAL_BRIGHT, arc_alpha),
                           (cx - 6, arc_y), (cx - 6 - arc['length'], arc_y + j), 2)
            # 右侧电弧
            pygame.draw.line(target_surf, (*CRYSTAL_BRIGHT, arc_alpha),
                           (cx + 6, arc_y), (cx + 6 + arc['length'], arc_y - j), 2)
        
        # === 能量球沿光束上升 ===
        for i in range(3):
            p_phase = ((lifetime * 0.12 + i * 0.33) % 1.0)
            p_y = int(length * (1 - p_phase)) + offset_y
            p_size = int(1 + pulse * 1)
            p_alpha = int(200 * (1 - progress * 0.4))

            pygame.draw.circle(target_surf, (255, 255, 255, p_alpha), (cx, p_y), p_size)
            pygame.draw.circle(target_surf, (*CRYSTAL_BRIGHT, p_alpha // 2), (cx, p_y), p_size + 1)
        
        # === 顶端冲击波 ===
        if lifetime > self.max_life - 5:
            burst_progress = (self.max_life - lifetime) / 5
            burst_r = int(10 + burst_progress * 12)
            burst_alpha = int(200 * (1 - burst_progress))
            pygame.draw.circle(target_surf, (*LASER_GLOW, burst_alpha), (cx, offset_y + 5), burst_r)
            pygame.draw.circle(target_surf, (255, 255, 255, burst_alpha), (cx, offset_y + 5), burst_r // 2)
            
            # 爆发射线
            for i in range(6):
                angle = i * (math.pi / 3) + lifetime * 0.2
                ray_len = burst_r * 1.2
                rx = cx + math.cos(angle) * ray_len
                ry = offset_y + 5 + math.sin(angle) * ray_len
                pygame.draw.line(target_surf, (*CRYSTAL_BRIGHT, burst_alpha), 
                               (cx, offset_y + 5), (int(rx), int(ry)), 2)
        
        # === 底部发射口 ===
        muzzle_y = length + offset_y
        muzzle_pulse = abs(math.sin(lifetime * 0.6))
        
        # 多层发射光环
        for ring in range(2):
            ring_r = int((10 - ring * 3) + muzzle_pulse * 3)
            ring_alpha = int((150 - ring * 50) * (1 - progress * 0.5))
            pygame.draw.circle(target_surf, (*LASER_GLOW, ring_alpha), (cx, muzzle_y), ring_r)
        
        # 核心高亮
        pygame.draw.circle(target_surf, (255, 255, 255), (cx, muzzle_y), int(12 + muzzle_pulse * 5))


class BeamHitEffect(pygame.sprite.Sprite):
    """射线命中效果 - 超强版"""
    
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.lifetime = 25  # 更长
        self.max_life = 25

        # 预渲染帧动画
        self._sheet, self._frames = _make_sheet_frames(160, 160, self.max_life)
        self.image = self._frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        
        # 生成更多碎片
        self.fragments = []
        for i in range(16):
            angle = i * (math.pi / 8) + random.uniform(-0.15, 0.15)
            speed = random.uniform(4, 10)
            self.fragments.append({
                'angle': angle,
                'speed': speed,
                'size': random.randint(4, 10),
                'type': random.choice(['circle', 'diamond'])
            })
        
        # 光线
        self.rays = []
        for i in range(8):
            self.rays.append({
                'angle': i * (math.pi / 4) + random.uniform(-0.1, 0.1),
                'length': random.randint(50, 80)
            })
        
        all_sprites.add(self)

        # 预渲染所有帧
        for fi in range(self.max_life):
            lifetime = self.max_life - fi
            self._draw_frame(self._frames[fi], lifetime)
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return

        idx = self.max_life - self.lifetime
        if 0 <= idx < self.max_life:
            self.image = self._frames[idx]

    def _draw_frame(self, target_surf, lifetime):
        progress = 1 - lifetime / self.max_life

        target_surf.fill(_TRANSPARENT)
        cx, cy = 80, 80

        # === 中心大爆发 ===
        if progress < 0.25:
            flash_intensity = 1 - progress / 0.25
            flash_r = int(40 * flash_intensity)
            pygame.draw.circle(target_surf, (255, 255, 255), (cx, cy), flash_r)
            pygame.draw.circle(target_surf, (*LASER_GLOW, int(200 * flash_intensity)), (cx, cy), flash_r + 15)
            pygame.draw.circle(target_surf, (*CRYSTAL_PURPLE, int(150 * flash_intensity)), (cx, cy), flash_r + 30)

        # === 放射光线 ===
        if progress < 0.6:
            ray_alpha = int(200 * (1 - progress / 0.6))
            ray_length = 60 + progress * 30
            for ray in self.rays:
                rx = cx + math.cos(ray['angle']) * ray_length
                ry = cy + math.sin(ray['angle']) * ray_length
                pygame.draw.line(target_surf, (*CRYSTAL_BRIGHT, ray_alpha), (cx, cy), (int(rx), int(ry)), 4)
                pygame.draw.line(target_surf, (255, 255, 255, ray_alpha // 2), (cx, cy), (int(rx), int(ry)), 2)

        # === 多层冲击波 ===
        for wave in range(4):
            wave_delay = wave * 0.08
            wave_progress = max(0, progress - wave_delay)
            if 0 < wave_progress < 0.8:
                wave_r = int(10 + wave_progress * 70)
                wave_alpha = int((220 - wave * 40) * (1 - wave_progress / 0.8))
                thickness = max(2, 5 - wave)
                pygame.draw.circle(target_surf, (*LASER_GLOW, wave_alpha), (cx, cy), wave_r, thickness)

        # === 飞散晶体碎片 ===
        for frag in self.fragments:
            frag_dist = progress * 50 * frag['speed'] / 6
            frag_x = cx + math.cos(frag['angle']) * frag_dist
            frag_y = cy + math.sin(frag['angle']) * frag_dist
            frag_alpha = int(255 * (1 - progress * 0.8))
            frag_size = int(frag['size'] * (1 - progress * 0.4))

            if frag_size > 1 and 0 <= frag_x < 160 and 0 <= frag_y < 160:
                if frag['type'] == 'circle':
                    pygame.draw.circle(target_surf, (*CRYSTAL_BRIGHT, frag_alpha), (int(frag_x), int(frag_y)), frag_size)
                else:
                    pts = [
                        (int(frag_x), int(frag_y - frag_size)),
                        (int(frag_x + frag_size), int(frag_y)),
                        (int(frag_x), int(frag_y + frag_size)),
                        (int(frag_x - frag_size), int(frag_y)),
                    ]
                    pygame.draw.polygon(target_surf, (*CRYSTAL_BRIGHT, frag_alpha), pts)

                tail_x = frag_x - math.cos(frag['angle']) * frag_size * 2
                tail_y = frag_y - math.sin(frag['angle']) * frag_size * 2
                pygame.draw.line(target_surf, (*LASER_GLOW, frag_alpha // 2), (int(frag_x), int(frag_y)), (int(tail_x), int(tail_y)), 2)

        # === 残留能量核心 ===
        if 0.3 < progress < 0.9:
            core_alpha = int(150 * (1 - (progress - 0.3) / 0.6))
            core_r = int(12 * (1 - (progress - 0.3) / 0.6))
            if core_r > 2:
                pygame.draw.circle(target_surf, (*LASER_GLOW, core_alpha), (cx, cy), core_r)
                pygame.draw.circle(target_surf, (255, 255, 255, core_alpha), (cx, cy), core_r // 2)


# ==================== F技能：相位冲撞 ====================
class WarpDashEffect(pygame.sprite.Sprite):
    """
    相位冲撞 - F技能
    向前高速冲刺，撞碎敌人护盾，无视碰撞
    """
    
    def __init__(self, player, damage, style="crusher_default"):
        super().__init__()
        self.player = player
        self.damage = damage
        self.style = style
        
        self.dash_distance = 200
        self.dash_speed = 25
        self.dash_progress = 0
        self.start_x = player.rect.centerx
        self.start_y = player.rect.centery
        self.target_y = max(50, player.rect.centery - self.dash_distance)
        
        self.hit_set = set()
        self.active = True
        
        # 冲刺轨迹帧动画（冲刺期间每帧重绘也会抖 CPU，这里做预渲染）
        self._frame_count = max(8, int(math.ceil(self.dash_distance / max(1, self.dash_speed))) + 2)
        self._sheet, self._frames = _make_sheet_frames(80, 250, self._frame_count)
        self.image = self._frames[0]
        self.rect = self.image.get_rect(center=(self.start_x, self.start_y))

        self._rng = random.Random(random.randrange(1 << 30))
        self._tail_jitter = [[(self._rng.randint(-10, 10), self._rng.randint(-2, 2)) for _ in range(6)] for _ in range(self._frame_count)]
        
        # 让玩家无敌
        if hasattr(player, 'invincible_timer'):
            player.invincible_timer = max(player.invincible_timer, 30)
        
        all_sprites.add(self)
        bullets.add(self)
    
    def update(self):
        if not self.active:
            self.kill()
            return
        
        # 冲刺进度
        self.dash_progress += self.dash_speed
        current_y = self.start_y - self.dash_progress
        
        if current_y <= self.target_y:
            current_y = self.target_y
            self.active = False
        
        # 移动玩家
        if self.player and self.player.alive():
            self.player.rect.centery = int(current_y)
        
        # 碰撞检测 - 冲撞路径上的敌人
        dash_rect = pygame.Rect(self.start_x - 35, current_y - 20, 70, 40)
        
        for m in mobs:
            if m.alive() and id(m) not in self.hit_set:
                if dash_rect.colliderect(m.rect):
                    # 造成伤害
                    m.take_damage(self.damage)
                    self.hit_set.add(id(m))
                    
                    # 破盾效果
                    if hasattr(m, 'shield') and m.shield > 0:
                        m.shield = 0  # 直接破盾
                    
                    # 击退
                    if hasattr(m, 'rect'):
                        m.rect.y += 30
                    
                    # 冲撞火花
                    CrushSpark(m.rect.centerx, m.rect.centery)
        
        # 绘制冲刺轨迹
        frame_index = min(self._frame_count - 1, int(self.dash_progress / max(1, self.dash_speed)))
        # 预渲染帧在这里按“当前 trail_length”近似；视觉一致性优先，不做动态裁切
        self._draw_trail_to_frame(self._frames[frame_index], current_y, frame_index)
        self.image = self._frames[frame_index]
        self.rect.center = (self.start_x, (self.start_y + current_y) // 2)
    
    def _draw_trail_to_frame(self, target_surf, current_y, frame_index):
        """绘制冲刺轨迹 - 增强版"""
        target_surf.fill(_TRANSPARENT)
        
        cx = 40
        trail_length = self.start_y - current_y
        pulse = abs(math.sin(self.dash_progress * 0.15))
        
        # 外层能量光芒（渐变紫色）
        for i in range(8):
            alpha = int((180 - i * 20) * (0.6 + pulse * 0.4))
            width = 50 - i * 5
            if alpha > 10:
                pygame.draw.rect(self.image, (*CRYSTAL_PURPLE, alpha),
                               (cx - width // 2, 125 - trail_length // 2, width, trail_length + 20))
        
        # 能量核心光束
        pygame.draw.rect(target_surf, (*LASER_GLOW, 220), 
                        (cx - 8, 125 - trail_length // 2, 16, trail_length + 10))
        pygame.draw.rect(target_surf, (*CRYSTAL_BRIGHT, 255), 
                        (cx - 4, 125 - trail_length // 2, 8, trail_length + 10))
        
        # 钻头图形 - 更大更锐利
        drill_y = 125 - trail_length // 2
        # 外层钻头轮廓
        outer_pts = [
            (cx, drill_y - 35),
            (cx - 25, drill_y + 5),
            (cx - 18, drill_y + 25),
            (cx + 18, drill_y + 25),
            (cx + 25, drill_y + 5),
        ]
        pygame.draw.polygon(target_surf, (*CRYSTAL_PURPLE, 200), outer_pts)
        
        # 内层钻头核心
        inner_pts = [
            (cx, drill_y - 25),
            (cx - 15, drill_y),
            (cx - 10, drill_y + 18),
            (cx + 10, drill_y + 18),
            (cx + 15, drill_y),
        ]
        pygame.draw.polygon(target_surf, CRYSTAL_BRIGHT, inner_pts)
        pygame.draw.polygon(target_surf, (255, 255, 255), inner_pts, 2)
        
        # 钻头中心高亮
        pygame.draw.circle(target_surf, (255, 255, 255), (cx, drill_y - 5), 6)
        pygame.draw.circle(target_surf, LASER_GLOW, (cx, drill_y - 5), 10, 2)
        
        # 侧翼能量条纹
        for side in [-1, 1]:
            for i in range(4):
                stripe_y = drill_y + 30 + i * 25
                stripe_alpha = int(150 - i * 30)
                if stripe_y < 125 + trail_length // 2:
                    pygame.draw.line(self.image, (*LASER_GLOW, stripe_alpha),
                                    (cx + side * 20, stripe_y), (cx + side * 35, stripe_y + 15), 3)
        
        # 尾焰粒子效果
        jitter = self._tail_jitter[frame_index]
        for i in range(6):
            p_y = 125 + trail_length // 2 - i * 15
            p_alpha = 200 - i * 30
            p_size = 8 - i
            if p_size > 0 and p_alpha > 0:
                dx, dy = jitter[i]
                pygame.draw.circle(target_surf, (*CRYSTAL_BRIGHT, p_alpha), (cx + dx, p_y + dy), p_size)


class CrushSpark(pygame.sprite.Sprite):
    """冲撞火花效果"""
    
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.lifetime = 15
        self.max_life = 15
        
        self._sheet, self._frames = _make_sheet_frames(60, 60, self.max_life)
        self.image = self._frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        
        all_sprites.add(self)

        for fi in range(self.max_life):
            lifetime = self.max_life - fi
            self._draw_frame(self._frames[fi], lifetime)
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return

        idx = self.max_life - self.lifetime
        if 0 <= idx < self.max_life:
            self.image = self._frames[idx]

    def _draw_frame(self, target_surf, lifetime):
        progress = 1 - lifetime / self.max_life
        target_surf.fill(_TRANSPARENT)
        cx, cy = 30, 30

        for i in range(8):
            angle = i * math.pi / 4 + progress * 2
            dist = 5 + progress * 20
            sx = cx + math.cos(angle) * dist
            sy = cy + math.sin(angle) * dist
            size = int(6 * (1 - progress * 0.7))
            alpha = int(255 * (1 - progress))

            if size > 0 and alpha > 0:
                pts = [
                    (sx, sy - size),
                    (sx + size * 0.6, sy),
                    (sx, sy + size * 0.5),
                    (sx - size * 0.6, sy),
                ]
                pts = [(int(p[0]), int(p[1])) for p in pts]
                pygame.draw.polygon(target_surf, (*CRYSTAL_PURPLE, alpha), pts)

        if lifetime > 8:
            flash_alpha = int(255 * (lifetime - 8) / 7)
            pygame.draw.circle(target_surf, (*LASER_GLOW, flash_alpha), (cx, cy), 10)


# ==================== G技能：牵引光束 ====================
class TractorBeamEffect(pygame.sprite.Sprite):
    """
    牵引光束 - G技能
    发射360°环形紫色引力波，将所有敌人拉向自己并造成持续伤害
    """
    
    def __init__(self, player, damage, style="crusher_default"):
        super().__init__()
        self.player = player
        self.damage = damage
        self.style = style
        
        self.lifetime = 90  # 1.5秒持续时间
        self.max_life = 90
        self.pull_strength = 8  # 增强拉拽
        self.range = 400
        self.damage_tick = 0

        # 性能优化：牵引光束实际绘制半径有限（range 附近），无需每帧重绘整屏 Surface。
        # 这里改为以玩家为中心的局部 Surface，视觉不变但减少 fill + draw 的像素量。
        # 最大绘制半径估计：外圈≈range，粒子尾迹≈range+20，线宽/发光留余量≈50
        self._draw_radius = int(self.range + 80)
        self._surf_size = max(240, self._draw_radius * 2)
        self.image = pygame.Surface((self._surf_size, self._surf_size), pygame.SRCALPHA)
        # 在已设置显示模式的情况下，convert_alpha 通常能加速 blit
        if pygame.display.get_init() and pygame.display.get_surface() is not None:
            self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect(center=(player.rect.centerx, player.rect.centery))
        
        # 音效
        try:
            from utils.audio import sound_mgr
            sound_mgr.play("beam")
        except:
            pass
        
        # 不在这里添加精灵组，由sprites.py调用时添加
        
        # 给玩家添加无敌保护
        if self.player:
            self.player.tractor_immune = True
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            # 结束时移除无敌
            if self.player and hasattr(self.player, 'tractor_immune'):
                self.player.tractor_immune = False
            self.kill()
            return
        
        if not self.player or not self.player.alive():
            self.kill()
            return
        
        # 持续保持无敌状态
        self.player.tractor_immune = True
        
        px = self.player.rect.centerx
        py = self.player.rect.centery

        # 局部 Surface 以玩家为中心
        self.rect.center = (px, py)
        
        # 伤害计时器
        self.damage_tick += 1
        
        # 安全距离 - 不把敌人拉得太近
        safe_dist = 80
        
        # 360°环形拉拽所有范围内的敌人
        range_sq = self.range * self.range
        safe_sq = safe_dist * safe_dist
        min_sq = 30 * 30
        for m in mobs:
            if not m.alive():
                continue
            dx = m.rect.centerx - px
            dy = m.rect.centery - py
            dist_sq = dx * dx + dy * dy

            # 在范围内且大于安全距离：牵引
            if min_sq < dist_sq < range_sq and dist_sq > safe_sq:
                dist = math.sqrt(dist_sq)
                # 拉向玩家（越近拉力越强）
                pull_factor = 1.0 + (1.0 - dist / self.range) * 0.5
                inv_dist = 1.0 / max(1e-6, dist)
                pull_x = -dx * inv_dist * self.pull_strength * pull_factor
                pull_y = -dy * inv_dist * self.pull_strength * pull_factor

                # 确保不会拉得太近
                new_dx = dx + pull_x
                new_dy = dy + pull_y
                if (new_dx * new_dx + new_dy * new_dy) >= safe_sq:
                    m.rect.x += int(pull_x)
                    m.rect.y += int(pull_y)

                # 每15帧造成一次伤害
                if self.damage_tick % 15 == 0 and hasattr(m, 'hp'):
                    tick_dmg = self.damage * 0.15
                    m.hp -= tick_dmg
                    from sprites import DamageNumber
                    DamageNumber(m.rect.centerx, m.rect.top, int(tick_dmg), is_crit=False)

            # 在安全距离边缘：高伤害
            elif min_sq < dist_sq <= safe_sq and self.damage_tick % 10 == 0 and hasattr(m, 'hp'):
                crush_dmg = self.damage * 0.25
                m.hp -= crush_dmg
                from sprites import DamageNumber
                DamageNumber(m.rect.centerx, m.rect.top, int(crush_dmg), is_crit=True)
        
        # 清除范围内的敌方子弹
        r = self.range
        for eb in enemy_bullets:
            if not eb.alive():
                continue
            edx = eb.rect.centerx - px
            if edx > r or edx < -r:
                continue
            edy = eb.rect.centery - py
            if edy > r or edy < -r:
                continue
            if edx * edx + edy * edy < range_sq:
                eb.kill()
        
        # 绘制牵引光束效果
        self._draw_beam()
    
    def _draw_beam(self):
        """绘制360°环形牵引光束 - 增强版"""
        self.image.fill(_TRANSPARENT)

        px = self._surf_size // 2
        py = self._surf_size // 2
        
        pulse = abs(math.sin(self.lifetime * 0.12))
        beam_range = self.range * (0.85 + pulse * 0.15)
        rotation = self.lifetime * 0.08
        
        # 外层引力场光环（5层渐变）
        for layer in range(5):
            layer_range = beam_range * (1 - layer * 0.15)
            alpha = int((140 - layer * 25) * (0.6 + pulse * 0.4))
            thickness = 5 - layer
            if alpha > 10 and layer_range > 30:
                pygame.draw.circle(self.image, (*CRYSTAL_PURPLE, alpha), (px, py), int(layer_range), max(2, thickness))
        
        # 旋转的引力漩涡线（8条螺旋）
        for i in range(8):
            base_angle = i * (math.pi / 4) + rotation
            points = []
            for seg in range(15):
                seg_ratio = seg / 14.0
                spiral_r = beam_range * (1 - seg_ratio * 0.75)
                spiral_angle = base_angle + seg_ratio * math.pi * 0.8
                x = px + math.cos(spiral_angle) * spiral_r
                y = py + math.sin(spiral_angle) * spiral_r
                points.append((int(x), int(y)))
            
            if len(points) >= 2:
                line_alpha = int(130 * (0.5 + pulse * 0.5))
                pygame.draw.lines(self.image, (*CRYSTAL_BRIGHT, line_alpha), False, points, 2)
        
        # 流入粒子环（16个）
        for i in range(16):
            particle_angle = i * (math.pi / 8) + rotation * 0.6
            particle_phase = ((self.lifetime * 0.06 + i * 0.12) % 1.0)
            particle_dist = beam_range * (1 - particle_phase * 0.85)
            
            if particle_dist > 50:
                particle_x = px + math.cos(particle_angle) * particle_dist
                particle_y = py + math.sin(particle_angle) * particle_dist
                size = int(3 + particle_phase * 6)
                alpha = int(200 * particle_phase)
                pygame.draw.circle(self.image, (*CRYSTAL_BRIGHT, alpha), 
                                  (int(particle_x), int(particle_y)), size)
                # 粒子拖尾
                tail_x = px + math.cos(particle_angle) * (particle_dist + 20)
                tail_y = py + math.sin(particle_angle) * (particle_dist + 20)
                pygame.draw.line(self.image, (*LASER_GLOW, alpha // 2),
                               (int(particle_x), int(particle_y)), (int(tail_x), int(tail_y)), 2)
        
        # 中心能量核心（多层发光）
        core_pulse = abs(math.sin(self.lifetime * 0.2))
        for i in range(5):
            core_r = int((45 - i * 8) * (0.8 + core_pulse * 0.2))
            core_alpha = int((220 - i * 40) * (0.7 + core_pulse * 0.3))
            if core_r > 0 and core_alpha > 0:
                pygame.draw.circle(self.image, (*LASER_GLOW, core_alpha), (px, py), core_r)
        
        # 核心高亮
        pygame.draw.circle(self.image, CRYSTAL_BRIGHT, (px, py), int(15 + core_pulse * 8))
        pygame.draw.circle(self.image, (255, 255, 255), (px, py), int(8 + core_pulse * 4))
        
        # 十字能量光芒
        cross_len = int(60 + core_pulse * 20)
        for angle in [0, math.pi/2, math.pi, math.pi*1.5]:
            end_x = px + math.cos(angle) * cross_len
            end_y = py + math.sin(angle) * cross_len
            pygame.draw.line(self.image, (*CRYSTAL_BRIGHT, 180), (px, py), (int(end_x), int(end_y)), 3)


# ==================== C技能：共振破碎 ====================
class ResonanceBreakEffect(pygame.sprite.Sprite):
    """
    共振破碎 - C技能
    发出高频音波，全屏晶体物质破碎
    对所有敌人造成伤害，并清除敌方子弹
    """
    
    def __init__(self, player, damage, style="crusher_default"):
        super().__init__()
        self.player = player
        self.damage = damage
        self.style = style
        
        self.lifetime = 40
        self.max_life = 40
        self.hit_frame = 10  # 第10帧造成伤害
        self.has_hit = False
        
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))

        # 性能优化：除“全屏强闪光”阶段外，绝大多数绘制都围绕玩家中心（半径约 500）。
        # 用脏矩形仅清理上一帧绘制区域，避免每帧整屏 clear。
        # 波纹最大≈500，余波射线最大≈350，留余量避免线宽裁切
        self._local_radius = 520
        self._local_size = self._local_radius * 2
        self._local_surf = pygame.Surface((self._local_size, self._local_size), pygame.SRCALPHA)
        if pygame.display.get_init() and pygame.display.get_surface() is not None:
            self._local_surf = self._local_surf.convert_alpha()
        self._dirty_rect = None
        
        # 不在这里添加精灵组，由sprites.py调用时添加
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        
        # 在特定帧造成伤害
        if self.lifetime == self.max_life - self.hit_frame and not self.has_hit:
            self._deal_damage()
            self.has_hit = True
        
        # 绘制效果
        self._draw_effect()
    
    def _deal_damage(self):
        """对全屏敌人造成伤害"""
        from sprites import DamageNumber, FloatingText, screen_shake
        
        # 屏幕震动
        screen_shake(12, 8)
        
        # 伤害所有敌人
        hit_count = 0
        for m in mobs:
            if m.alive() and hasattr(m, 'hp'):
                # 直接扣血
                m.hp -= self.damage
                hit_count += 1
                # 创建破碎效果
                CrystalShatterEffect(m.rect.centerx, m.rect.centery)
                # 伤害数字
                DamageNumber(m.rect.centerx, m.rect.top - 10, int(self.damage), is_crit=True)
        
        # 清除敌方子弹
        bullet_count = 0
        for eb in list(enemy_bullets):
            if eb.alive():
                # 创建小破碎效果
                MiniShatter(eb.rect.centerx, eb.rect.centery)
                eb.kill()
                bullet_count += 1
        
        # 显示命中信息
        if self.player and self.player.alive():
            if hit_count > 0:
                FloatingText(self.player.rect.centerx, self.player.rect.top - 70, 
                           f"共振命中 ×{hit_count}", (200, 100, 255))
    
    def _draw_effect(self):
        """绘制共振波效果 - 增强版"""
        progress = 1 - self.lifetime / self.max_life

        if not self.player or not self.player.alive():
            # 清掉上一帧遗留绘制区域
            if self._dirty_rect is not None:
                self.image.fill(_TRANSPARENT, self._dirty_rect)
                self._dirty_rect = None
            return

        px = self.player.rect.centerx
        py = self.player.rect.centery
        
        # 震荡波纹（6层扩散波）
        for wave in range(6):
            wave_phase = (progress * 2.5 + wave * 0.15) % 1.0
            wave_r = int(wave_phase * 500)
            wave_alpha = int(180 * (1 - wave_phase))
            thickness = int(6 - wave_phase * 4)
            
            if wave_alpha > 10 and wave_r > 20:
                pygame.draw.circle(self.image, (*CRYSTAL_PURPLE, wave_alpha), (px, py), wave_r, max(2, thickness))
        
        # 中央共振核心（蓄力效果）
        if progress < 0.35:
            charge = progress / 0.35
            core_pulse = abs(math.sin(self.lifetime * 0.6))
            
            # 多层发光核心
            for i in range(6):
                core_r = int((50 - i * 7) * (0.5 + charge * 0.5) * (0.8 + core_pulse * 0.2))
                core_alpha = int((250 - i * 40) * (0.6 + core_pulse * 0.4))
                if core_r > 0 and core_alpha > 0:
                    pygame.draw.circle(self.image, (*LASER_GLOW, core_alpha), (px, py), core_r)
            
            # 核心高亮
            pygame.draw.circle(self.image, CRYSTAL_BRIGHT, (px, py), int(20 + core_pulse * 10))
            pygame.draw.circle(self.image, (255, 255, 255), (px, py), int(10 + core_pulse * 5))
            
            # 蓄力粒子向内聚集
            for i in range(12):
                angle = i * (math.pi / 6) + self.lifetime * 0.1
                p_dist = 120 * (1 - charge) + 30
                p_x = px + math.cos(angle) * p_dist
                p_y = py + math.sin(angle) * p_dist
                p_size = int(4 + charge * 4)
                pygame.draw.circle(self.image, (*CRYSTAL_BRIGHT, int(200 * charge)), (int(p_x), int(p_y)), p_size)
        
        # 命中时全屏强闪光 + 裂纹效果
        hit_time = self.max_life - self.hit_frame
        if self.lifetime >= hit_time - 3 and self.lifetime <= hit_time + 3:
            flash_intensity = 1.0 - abs(self.lifetime - hit_time) / 3
            flash_alpha = int(180 * flash_intensity)
            self.image.fill((*CRYSTAL_BRIGHT, flash_alpha))
            self._dirty_rect = self.rect.copy()
            
            # 放射状裂纹
            for i in range(16):
                angle = i * (math.pi / 8)
                length = 300 + random.randint(-50, 50)
                end_x = px + math.cos(angle) * length
                end_y = py + math.sin(angle) * length
                pygame.draw.line(self.image, (*LASER_GLOW, int(200 * flash_intensity)), 
                               (px, py), (int(end_x), int(end_y)), 3)
            return

        # 非全屏闪光阶段：仅清理/重绘局部区域
        if self._dirty_rect is not None:
            self.image.fill(_TRANSPARENT, self._dirty_rect)

        self._local_surf.fill(_TRANSPARENT)
        lc = self._local_radius

        # 震荡波纹（6层扩散波）
        for wave in range(6):
            wave_phase = (progress * 2.5 + wave * 0.15) % 1.0
            wave_r = int(wave_phase * 500)
            wave_alpha = int(180 * (1 - wave_phase))
            thickness = int(6 - wave_phase * 4)

            if wave_alpha > 10 and wave_r > 20:
                pygame.draw.circle(self._local_surf, (*CRYSTAL_PURPLE, wave_alpha), (lc, lc), wave_r, max(2, thickness))

        # 中央共振核心（蓄力效果）
        if progress < 0.35:
            charge = progress / 0.35
            core_pulse = abs(math.sin(self.lifetime * 0.6))

            # 多层发光核心
            for i in range(6):
                core_r = int((50 - i * 7) * (0.5 + charge * 0.5) * (0.8 + core_pulse * 0.2))
                core_alpha = int((250 - i * 40) * (0.6 + core_pulse * 0.4))
                if core_r > 0 and core_alpha > 0:
                    pygame.draw.circle(self._local_surf, (*LASER_GLOW, core_alpha), (lc, lc), core_r)

            # 核心高亮
            pygame.draw.circle(self._local_surf, CRYSTAL_BRIGHT, (lc, lc), int(20 + core_pulse * 10))
            pygame.draw.circle(self._local_surf, (255, 255, 255), (lc, lc), int(10 + core_pulse * 5))

            # 蓄力粒子向内聚集
            for i in range(12):
                angle = i * (math.pi / 6) + self.lifetime * 0.1
                p_dist = 120 * (1 - charge) + 30
                p_x = lc + math.cos(angle) * p_dist
                p_y = lc + math.sin(angle) * p_dist
                p_size = int(4 + charge * 4)
                pygame.draw.circle(self._local_surf, (*CRYSTAL_BRIGHT, int(200 * charge)), (int(p_x), int(p_y)), p_size)

        # 爆发后的余波
        if progress > 0.35:
            aftershock = (progress - 0.35) / 0.65
            for i in range(8):
                angle = i * (math.pi / 4) + aftershock * 2
                length = 150 + aftershock * 200
                alpha = int(120 * (1 - aftershock))
                if alpha > 10:
                    end_x = lc + math.cos(angle) * length
                    end_y = lc + math.sin(angle) * length
                    pygame.draw.line(self._local_surf, (*CRYSTAL_PURPLE, alpha), (lc, lc), (int(end_x), int(end_y)), 4)

        blit_x = int(px - lc)
        blit_y = int(py - lc)
        self.image.blit(self._local_surf, (blit_x, blit_y))
        self._dirty_rect = pygame.Rect(blit_x, blit_y, self._local_size, self._local_size).clip(self.rect)
        
        # 爆发后的余波
        if progress > 0.35:
            aftershock = (progress - 0.35) / 0.65
            for i in range(8):
                angle = i * (math.pi / 4) + aftershock * 2
                length = 150 + aftershock * 200
                alpha = int(120 * (1 - aftershock))
                if alpha > 10:
                    end_x = px + math.cos(angle) * length
                    end_y = py + math.sin(angle) * length
                    pygame.draw.line(self.image, (*CRYSTAL_PURPLE, alpha), (px, py), (int(end_x), int(end_y)), 4)


class CrystalShatterEffect(pygame.sprite.Sprite):
    """水晶破碎效果（大）"""
    
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.lifetime = 25
        self.max_life = 25
        
        # 生成碎片
        self.shards = []
        for i in range(12):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 8)
            size = random.randint(4, 10)
            rot = random.uniform(-0.3, 0.3)
            self.shards.append({
                'angle': angle,
                'speed': speed,
                'size': size,
                'rot': rot,
                'dist': 0,
            })
        
        self.image = pygame.Surface((120, 120), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        all_sprites.add(self)
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        
        progress = 1 - self.lifetime / self.max_life
        self.image.fill((0, 0, 0, 0))
        cx, cy = 60, 60
        
        # 中心闪光
        if self.lifetime > 18:
            flash_r = int(25 * (self.lifetime - 18) / 7)
            pygame.draw.circle(self.image, LASER_GLOW, (cx, cy), flash_r)
        
        # 飞散碎片
        for shard in self.shards:
            shard['dist'] += shard['speed']
            sx = cx + math.cos(shard['angle']) * shard['dist']
            sy = cy + math.sin(shard['angle']) * shard['dist']
            
            size = int(shard['size'] * (1 - progress * 0.7))
            alpha = int(255 * (1 - progress))
            
            if size > 1 and alpha > 0:
                # 菱形碎片
                rot = shard['rot'] * self.lifetime
                pts = [
                    (sx + math.cos(rot) * size, sy + math.sin(rot) * size),
                    (sx + math.cos(rot + math.pi/2) * size * 0.5, sy + math.sin(rot + math.pi/2) * size * 0.5),
                    (sx + math.cos(rot + math.pi) * size, sy + math.sin(rot + math.pi) * size),
                    (sx + math.cos(rot - math.pi/2) * size * 0.5, sy + math.sin(rot - math.pi/2) * size * 0.5),
                ]
                pts = [(int(p[0]), int(p[1])) for p in pts]
                pygame.draw.polygon(self.image, (*CRYSTAL_PURPLE, alpha), pts)


class MiniShatter(pygame.sprite.Sprite):
    """小型破碎效果（子弹消除用）"""
    
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.lifetime = 10
        
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        all_sprites.add(self)
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        
        progress = 1 - self.lifetime / 10
        self.image.fill((0, 0, 0, 0))
        
        # 简单扩散环
        ring_r = int(3 + progress * 8)
        ring_alpha = int(200 * (1 - progress))
        pygame.draw.circle(self.image, (*CRYSTAL_BRIGHT, ring_alpha), (10, 10), ring_r, 1)


# ==================== R技能：次元坍缩 ====================
class CoreMeltdownEffect(pygame.sprite.Sprite):
    """
    【次元坍缩】R技能 - 终极毁灭技能
    - 巨型晶体钻头从天而降，撞击全屏
    - 护甲层数越高：钻头越大、伤害越高、裂隙越多
    - 三阶段：警告 -> 天降 -> 爆裂
    """
    
    def __init__(self, owner, base_damage, style="crusher_default", armor_stacks=0):
        super().__init__()
        self.owner = owner
        self.base_damage = base_damage
        self.style = style
        self.armor_stacks = min(armor_stacks, 20)
        
        # 护甲层数爆发倍率（每层+20%伤害，满层4倍）
        self.damage_mult = 1.0 + self.armor_stacks * 0.2
        self.damage = int(base_damage * self.damage_mult)
        
        # 颜色配置
        self.primary = CRYSTAL_PURPLE
        self.secondary = LASER_GLOW
        self.accent = CRYSTAL_BRIGHT
        self.void_color = (30, 0, 50)
        self._apply_style_colors()
        
        # 状态
        self.lifetime = 240  # 4秒
        self.max_life = 240
        self.phase = "warning"  # warning -> descend -> impact -> devastation
        self.warning_frames = 45
        self.descend_frames = 35
        self.impact_frames = 30
        self.devastation_frames = 130
        
        # 巨型钻头参数（基于护甲层数）
        self.drill_base_size = 120
        self.drill_max_size = self.drill_base_size + self.armor_stacks * 12  # 满层360
        self.drill_y = -200
        self.drill_target_y = HEIGHT // 2
        self.drill_rotation = 0
        self.drill_speed = 0

        # 实例级 RNG：避免每帧全局 random 带来的抖动开销，并保持观感稳定
        self._rng = random.Random(random.randrange(1 << 30))

        # 预渲染：钻头主体（叶片/轮廓/能量线）
        # 最重的部分是每帧绘制 8 片多边形叶片；这里改成初始化绘制一次，再每帧 transform+blit。
        self._drill_body_base_size = 240
        self._drill_body_base = self._build_drill_body_base(self._drill_body_base_size)

        # 预生成每帧火花随机参数（保持“随机感”，但不在 draw 中调用 random）
        self._spark_params = []
        for _ in range(self.max_life):
            frame_params = []
            for __ in range(12):
                frame_params.append({
                    'dist_jitter': self._rng.randint(0, 30),
                    'alpha': self._rng.randint(100, 200),
                    'radius': self._rng.randint(3, 6),
                })
            self._spark_params.append(frame_params)
        
        # 冲击波参数
        self.shockwave_radius = 0
        self.shockwave_max = WIDTH + 200
        
        # 裂隙系统（护甲越高裂隙越多）
        self.rifts = []
        self.rift_count = 6 + self.armor_stacks  # 6~26条裂隙
        
        # 落雷效果
        self.lightning_bolts = []
        
        # 屏幕震动
        self.screen_shake = 0
        
        # 伤害记录
        self.impact_dealt = False
        
        # 屏幕级Surface
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        
        all_sprites.add(self)

    def _build_drill_body_base(self, size):
        """预渲染钻头主体（叶片/轮廓/能量线），rot=0、以中心绘制。"""
        # 叶片尖端约 size*0.95，再留边距
        dim = int(size * 2.4)
        dim = max(320, dim)
        surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
        if _can_convert_alpha():
            surf = surf.convert_alpha()

        cx = dim // 2
        cy = dim // 2
        rot = 0.0

        # 钻头主体 - 8片叶片
        for blade in range(8):
            angle = rot + blade * math.pi / 4

            tip_dist = size * 0.95
            base_dist = size * 0.15
            spread = 0.3

            tip_x = cx + math.cos(angle) * tip_dist
            tip_y = cy + math.sin(angle) * tip_dist

            left_x = cx + math.cos(angle - spread) * base_dist
            left_y = cy + math.sin(angle - spread) * base_dist
            right_x = cx + math.cos(angle + spread) * base_dist
            right_y = cy + math.sin(angle + spread) * base_dist

            points = [(int(left_x), int(left_y)), (int(tip_x), int(tip_y)), (int(right_x), int(right_y))]

            # 用一个固定的亮度（动态脉冲在外层光晕/火花里体现，主体保持稳定）
            pygame.draw.polygon(surf, (*self.secondary, 230), points)
            pygame.draw.polygon(surf, (*self.accent, 255), points, 3)

            pygame.draw.line(surf, (*self.accent, 200), (cx, cy), (int(tip_x), int(tip_y)), 2)

        return surf
    
    def _apply_style_colors(self):
        """应用涂装颜色"""
        if "crimson" in self.style:
            self.primary = (220, 20, 60)
            self.secondary = (255, 69, 0)
            self.accent = (255, 200, 100)
            self.void_color = (60, 0, 0)
        elif "azure" in self.style:
            self.primary = (0, 150, 255)
            self.secondary = (200, 240, 255)
            self.accent = (255, 255, 255)
            self.void_color = (0, 20, 50)
        elif "emerald" in self.style:
            self.primary = (0, 220, 100)
            self.secondary = (180, 255, 180)
            self.accent = (255, 255, 150)
            self.void_color = (0, 30, 15)
        elif "golden" in self.style:
            self.primary = (255, 200, 50)
            self.secondary = (255, 255, 200)
            self.accent = (255, 255, 255)
            self.void_color = (40, 30, 0)
        elif "void" in self.style:
            self.primary = (100, 0, 150)
            self.secondary = (180, 100, 255)
            self.accent = (255, 150, 255)
            self.void_color = (20, 0, 30)
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        
        elapsed = self.max_life - self.lifetime
        
        # 阶段判断
        if elapsed < self.warning_frames:
            self.phase = "warning"
            self._update_warning(elapsed)
        elif elapsed < self.warning_frames + self.descend_frames:
            self.phase = "descend"
            self._update_descend(elapsed - self.warning_frames)
        elif elapsed < self.warning_frames + self.descend_frames + self.impact_frames:
            self.phase = "impact"
            self._update_impact(elapsed - self.warning_frames - self.descend_frames)
        else:
            self.phase = "devastation"
            self._update_devastation(elapsed - self.warning_frames - self.descend_frames - self.impact_frames)
        
        # 更新裂隙
        for rift in self.rifts[:]:
            rift['life'] -= 1
            if rift['life'] <= 0:
                self.rifts.remove(rift)
            else:
                self._deal_rift_damage(rift)
        
        # 更新闪电
        self.lightning_bolts = [b for b in self.lightning_bolts if b['life'] > 0]
        for bolt in self.lightning_bolts:
            bolt['life'] -= 1
        
        # 屏幕震动衰减
        if self.screen_shake > 0:
            self.screen_shake -= 1
        
        self._draw_effect()
    
    def _update_warning(self, elapsed):
        """警告阶段：地面出现裂缝预警"""
        progress = elapsed / self.warning_frames
        
        # 钻头开始旋转
        self.drill_rotation += 5 + progress * 15
        self.drill_y = -200 + progress * 50  # 略微下降
        
        # 生成警告闪电
        if elapsed % 8 == 0:
            self._spawn_warning_lightning()
    
    def _update_descend(self, elapsed):
        """下降阶段：钻头加速坠落"""
        progress = elapsed / self.descend_frames
        eased = progress * progress * (3 - 2 * progress)  # smoothstep
        
        # 加速旋转
        self.drill_rotation += 20 + progress * 30
        
        # 加速下降
        self.drill_y = -150 + eased * (self.drill_target_y + 150)
        
        # 钻头逐渐变大
        self.drill_size = int(self.drill_base_size + (self.drill_max_size - self.drill_base_size) * progress)
        
        # 震动预警
        self.screen_shake = int(5 * progress)
        
        # 下降时产生的能量波
        if elapsed % 3 == 0:
            self._spawn_descend_spark()
    
    def _update_impact(self, elapsed):
        """撞击阶段：全屏爆炸"""
        progress = elapsed / self.impact_frames
        
        # 第一帧造成伤害
        if elapsed == 1 and not self.impact_dealt:
            self._deal_impact_damage()
            self.impact_dealt = True
            self.screen_shake = 30
        
        # 冲击波扩散
        self.shockwave_radius = int(progress * self.shockwave_max)
        
        # 钻头震颤
        self.drill_rotation += 50
        
        # 生成裂隙
        if elapsed == 1:
            self._spawn_rifts()
    
    def _update_devastation(self, elapsed):
        """毁灭阶段：持续裂隙伤害"""
        progress = elapsed / self.devastation_frames
        
        # 钻头逐渐消散
        self.drill_size = int(self.drill_max_size * (1 - progress * 0.7))
        self.drill_rotation += 10 * (1 - progress)
        
        # 冲击波消散
        self.shockwave_radius = int(self.shockwave_max * (1 - progress * 0.5))
        
        # 持续震动
        if elapsed < 40:
            self.screen_shake = int(15 * (1 - elapsed / 40))
        
        # 随机闪电
        if self._rng.random() < 0.15 * (1 - progress):
            self._spawn_random_lightning()
    
    def _deal_impact_damage(self):
        """撞击伤害 - 全屏毁灭"""
        if not self.owner or not self.owner.alive():
            return
        
        for mob in list(mobs):
            if not mob.alive():
                continue
            
            # 距离撞击点越近伤害越高
            dist = math.hypot(mob.rect.centerx - WIDTH // 2, mob.rect.centery - self.drill_target_y)
            dist_mult = max(0.5, 1.5 - dist / 400)  # 近距离1.5倍，远距离0.5倍
            
            damage = int(self.damage * dist_mult)
            mob.hp -= damage
            
            # 击退
            if dist > 0:
                dx = (mob.rect.centerx - WIDTH // 2) / max(1, dist)
                dy = (mob.rect.centery - self.drill_target_y) / max(1, dist)
                knockback = int(30 * dist_mult)
                mob.rect.centerx += int(dx * knockback)
                mob.rect.centery += int(dy * knockback)
            
            # 特效
            CrystalShatterEffect(mob.rect.centerx, mob.rect.centery)
        
        # 清除所有敌弹
        for eb in list(enemy_bullets):
            MiniShatter(eb.rect.centerx, eb.rect.centery)
            eb.kill()
    
    def _spawn_rifts(self):
        """生成晶体裂隙"""
        cx, cy = WIDTH // 2, self.drill_target_y
        
        for i in range(self.rift_count):
            angle = (i / self.rift_count) * math.pi * 2 + self._rng.uniform(-0.2, 0.2)
            length = self._rng.randint(150, 400)
            
            self.rifts.append({
                'x': cx,
                'y': cy,
                'angle': angle,
                'length': length,
                'life': 90 + self._rng.randint(0, 40),
                'max_life': 130,
                'width': self._rng.randint(3, 8),
            })
    
    def _deal_rift_damage(self, rift):
        """裂隙持续伤害"""
        rx, ry = rift['x'], rift['y']
        angle = rift['angle']
        length = rift['length']
        
        # 计算裂隙线段
        ex = rx + math.cos(angle) * length
        ey = ry + math.sin(angle) * length
        
        for mob in list(mobs):
            if not mob.alive():
                continue
            
            # 点到线段距离
            mx, my = mob.rect.centerx, mob.rect.centery
            dist = self._point_to_line_dist(mx, my, rx, ry, ex, ey)
            
            if dist < 40:
                mob.hp -= max(2, self.damage // 15)
                if self._rng.random() < 0.1:
                    CrushSpark(mob.rect.centerx, mob.rect.centery)
    
    def _point_to_line_dist(self, px, py, x1, y1, x2, y2):
        """点到线段距离"""
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(px - proj_x, py - proj_y)
    
    def _spawn_warning_lightning(self):
        """生成警告闪电"""
        self.lightning_bolts.append({
            'x1': WIDTH // 2 + self._rng.randint(-100, 100),
            'y1': 0,
            'x2': WIDTH // 2 + self._rng.randint(-150, 150),
            'y2': HEIGHT // 2 + self._rng.randint(-50, 50),
            'life': 8,
            'segments': self._generate_lightning_segments(
                WIDTH // 2, 0, WIDTH // 2, HEIGHT // 2, 6
            )
        })
    
    def _spawn_descend_spark(self):
        """生成下降火花"""
        x = WIDTH // 2 + self._rng.randint(-50, 50)
        y = int(self.drill_y) + self._rng.randint(-30, 30)
        CrushSpark(x, y)
    
    def _spawn_random_lightning(self):
        """生成随机闪电"""
        cx, cy = WIDTH // 2, self.drill_target_y
        angle = self._rng.uniform(0, math.pi * 2)
        dist = self._rng.randint(100, 300)
        ex = cx + math.cos(angle) * dist
        ey = cy + math.sin(angle) * dist
        
        self.lightning_bolts.append({
            'x1': cx, 'y1': cy, 'x2': ex, 'y2': ey,
            'life': 6,
            'segments': self._generate_lightning_segments(cx, cy, ex, ey, 4)
        })
    
    def _generate_lightning_segments(self, x1, y1, x2, y2, depth):
        """生成锯齿闪电段"""
        if depth <= 0:
            return [(x1, y1), (x2, y2)]
        
        mx = (x1 + x2) / 2 + self._rng.randint(-20, 20)
        my = (y1 + y2) / 2 + self._rng.randint(-20, 20)
        
        left = self._generate_lightning_segments(x1, y1, mx, my, depth - 1)
        right = self._generate_lightning_segments(mx, my, x2, y2, depth - 1)
        
        return left + right[1:]
    
    def _draw_effect(self):
        """绘制次元坍缩效果"""
        # 性能优化：避免每帧先清空再叠加整屏暗化（重复 fill）。
        elapsed = self.max_life - self.lifetime
        cx, cy = WIDTH // 2, self.drill_target_y
        
        # === 背景暗化 ===
        if self.phase in ["descend", "impact", "devastation"]:
            if self.phase == "descend":
                dark_alpha = int(80 * (elapsed - self.warning_frames) / self.descend_frames)
            elif self.phase == "impact":
                dark_alpha = 80
            else:
                progress = (elapsed - self.warning_frames - self.descend_frames - self.impact_frames) / self.devastation_frames
                dark_alpha = int(80 * (1 - progress))
            self.image.fill((*self.void_color, dark_alpha))
        else:
            self.image.fill(_TRANSPARENT)
        
        # === 警告阶段：地面裂缝预警 ===
        if self.phase == "warning":
            progress = elapsed / self.warning_frames
            self._draw_warning_cracks(cx, cy, progress)
        
        # === 冲击波 ===
        if self.shockwave_radius > 0:
            self._draw_shockwave(cx, cy)
        
        # === 裂隙 ===
        for rift in self.rifts:
            self._draw_rift(rift, cx, cy)
        
        # === 闪电 ===
        for bolt in self.lightning_bolts:
            self._draw_lightning(bolt)
        
        # === 巨型钻头 ===
        if self.phase != "warning" or elapsed > self.warning_frames * 0.5:
            self._draw_mega_drill()
        
        # === 撞击闪光 ===
        if self.phase == "impact":
            progress = (elapsed - self.warning_frames - self.descend_frames) / self.impact_frames
            if progress < 0.4:
                flash_alpha = int(200 * (1 - progress / 0.4))
                self.image.fill((255, 255, 255, flash_alpha))
    
    def _draw_warning_cracks(self, cx, cy, progress):
        """绘制警告裂缝"""
        num_cracks = 8
        for i in range(num_cracks):
            angle = (i / num_cracks) * math.pi * 2
            length = progress * 200
            
            # 裂缝线
            ex = cx + math.cos(angle) * length
            ey = cy + math.sin(angle) * length
            
            crack_alpha = int(150 * progress)
            pygame.draw.line(self.image, (*self.primary, crack_alpha), (cx, cy), (ex, ey), 3)
            
            # 裂缝发光
            glow_alpha = int(80 * progress * abs(math.sin(self.lifetime * 0.3 + i)))
            pygame.draw.line(self.image, (*self.accent, glow_alpha), (cx, cy), (ex, ey), 6)
        
        # 中心警告圈
        warn_r = int(50 + 30 * abs(math.sin(self.lifetime * 0.2)))
        warn_alpha = int(120 * progress)
        pygame.draw.circle(self.image, (*self.accent, warn_alpha), (cx, cy), warn_r, 4)
    
    def _draw_shockwave(self, cx, cy):
        """绘制冲击波 - 增强版"""
        max_rings = 6
        for ring in range(max_rings):
            r = self.shockwave_radius - ring * 25
            if r > 0:
                progress = self.shockwave_radius / self.shockwave_max
                alpha = int((150 - ring * 20) * (1 - progress * 0.7))
                thickness = max(2, 5 - ring)
                if alpha > 0:
                    pygame.draw.circle(self.image, (*self.secondary, alpha), (cx, cy), r, thickness)
        
        # 冲击波能量碎片
        if self.shockwave_radius > 50 and self.shockwave_radius < self.shockwave_max * 0.8:
            num_fragments = 16
            for i in range(num_fragments):
                angle = i * (math.pi * 2 / num_fragments) + self.shockwave_radius * 0.01
                frag_r = self.shockwave_radius - 10
                fx = cx + math.cos(angle) * frag_r
                fy = cy + math.sin(angle) * frag_r
                frag_alpha = int(180 * (1 - self.shockwave_radius / self.shockwave_max))
                frag_size = int(8 - self.shockwave_radius / self.shockwave_max * 5)
                if frag_size > 2:
                    pygame.draw.circle(self.image, (*self.accent, frag_alpha), (int(fx), int(fy)), frag_size)
    
    def _draw_rift(self, rift, cx, cy):
        """绘制晶体裂隙"""
        life_ratio = rift['life'] / rift['max_life']
        angle = rift['angle']
        length = rift['length'] * life_ratio
        width = rift['width']
        
        # 裂隙起点到终点
        ex = cx + math.cos(angle) * length
        ey = cy + math.sin(angle) * length
        
        # 主裂缝
        alpha = int(200 * life_ratio)
        pygame.draw.line(self.image, (*self.primary, alpha), (cx, cy), (ex, ey), width)
        
        # 发光边缘
        glow_alpha = int(100 * life_ratio * abs(math.sin(self.lifetime * 0.1 + angle)))
        pygame.draw.line(self.image, (*self.accent, glow_alpha), (cx, cy), (ex, ey), width + 4)
        
        # 裂隙末端火花
        if life_ratio > 0.3 and self._rng.random() < 0.05:
            CrushSpark(int(ex), int(ey))
    
    def _draw_lightning(self, bolt):
        """绘制闪电"""
        if len(bolt['segments']) < 2:
            return
        
        alpha = int(255 * (bolt['life'] / 8))
        points = [(int(p[0]), int(p[1])) for p in bolt['segments']]
        
        # 主闪电
        pygame.draw.lines(self.image, (*self.accent, alpha), False, points, 3)
        # 发光
        pygame.draw.lines(self.image, (*self.secondary, alpha // 2), False, points, 6)
    
    def _draw_mega_drill(self):
        """绘制巨型钻头 - 增强版"""
        dx = WIDTH // 2
        dy = int(self.drill_y)
        size = getattr(self, 'drill_size', self.drill_base_size)
        rot = math.radians(self.drill_rotation)

        # === 预渲染主体（叶片）===
        # 用 transform 代替每帧重画多边形叶片
        scale = max(0.05, size / float(self._drill_body_base_size))
        body = pygame.transform.rotozoom(self._drill_body_base, -self.drill_rotation, scale)
        bx = dx - body.get_width() // 2
        by = dy - body.get_height() // 2
        self.image.blit(body, (bx, by))
        
        # 外层能量旋涡
        for ring in range(8):
            r = int(size * (1.4 - ring * 0.1))
            ring_pulse = abs(math.sin(self.lifetime * 0.08 + ring * 0.5))
            ring_alpha = int((80 - ring * 8) * (0.6 + ring_pulse * 0.4))
            if r > 0 and ring_alpha > 0:
                pygame.draw.circle(self.image, (*self.primary, ring_alpha), (dx, dy), r, 3)
        
        # 旋转能量环
        spiral_count = 4
        for s in range(spiral_count):
            spiral_angle = rot * 1.5 + s * (math.pi / 2)
            for seg in range(12):
                seg_r = size * (0.9 - seg * 0.05)
                seg_angle = spiral_angle + seg * 0.15
                sx = dx + math.cos(seg_angle) * seg_r
                sy = dy + math.sin(seg_angle) * seg_r
                seg_alpha = int(150 - seg * 10)
                if seg_alpha > 20:
                    pygame.draw.circle(self.image, (*self.accent, seg_alpha), (int(sx), int(sy)), 4)
        
        # (主体叶片已由预渲染层绘制)
        
        # 叶片间隙发光
        for gap in range(8):
            gap_angle = rot + gap * math.pi / 4 + math.pi / 8
            gap_len = size * 0.7
            gx = dx + math.cos(gap_angle) * gap_len
            gy = dy + math.sin(gap_angle) * gap_len
            gap_alpha = int(100 * abs(math.sin(self.lifetime * 0.15 + gap)))
            pygame.draw.line(self.image, (*self.primary, gap_alpha), (dx, dy), (int(gx), int(gy)), 4)
        
        # 中心晶核 - 多层发光
        core_pulse = abs(math.sin(self.lifetime * 0.12))
        core_size = int(size * 0.28 + core_pulse * size * 0.1)
        
        # 核心外层光晕
        for i in range(4):
            halo_r = core_size + 15 - i * 4
            halo_alpha = int((150 - i * 30) * (0.7 + core_pulse * 0.3))
            pygame.draw.circle(self.image, (*self.primary, halo_alpha), (dx, dy), halo_r)
        
        # 核心主体
        pygame.draw.circle(self.image, self.accent, (dx, dy), core_size)
        pygame.draw.circle(self.image, (255, 255, 255), (dx, dy), core_size - 8)
        
        # 核心十字高光
        cross_len = core_size + 10
        for angle in [0, math.pi/2]:
            a = angle + rot * 0.5
            x1 = dx + math.cos(a) * cross_len
            y1 = dy + math.sin(a) * cross_len
            x2 = dx - math.cos(a) * cross_len
            y2 = dy - math.sin(a) * cross_len
            pygame.draw.line(self.image, (*self.accent, 180), (int(x1), int(y1)), (int(x2), int(y2)), 3)
        
        # 外围能量飞散
        if self.phase in ["impact", "devastation"]:
            elapsed = self.max_life - self.lifetime
            params = self._spark_params[min(max(elapsed, 0), self.max_life - 1)]
            for i in range(12):
                spark_angle = rot * 2 + i * (math.pi / 6)
                spark_dist = size * 1.2 + params[i]['dist_jitter']
                spark_x = dx + math.cos(spark_angle) * spark_dist
                spark_y = dy + math.sin(spark_angle) * spark_dist
                pygame.draw.circle(self.image, (*self.accent, params[i]['alpha']), (int(spark_x), int(spark_y)), params[i]['radius'])


# ==================== 导出列表 ====================
__all__ = [
    'DesolationBeamBullet',
    'BeamHitEffect',
    'WarpDashEffect',
    'CrushSpark',
    'TractorBeamEffect',
    'ResonanceBreakEffect',
    'CrystalShatterEffect',
    'MiniShatter',
    'CoreMeltdownEffect',
]
