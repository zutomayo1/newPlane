# -*- coding: utf-8 -*-
"""S.D.M.G. Bio-System STAR-DOLPHIN 专属弹幕模块"""
import math
import random
import pygame

from config import WIDTH, HEIGHT, all_sprites, bullets, mobs

try:
    from utils.planes.skins_sdmg import SDMG_THEMES, get_sdmg_theme
except Exception:  # pragma: no cover - 兜底以防涂装模块缺失
    SDMG_THEMES = {
        "default": {
            "armor": (192, 192, 192),
            "energy": (0, 255, 255),
            "shell": (255, 215, 0),
            "accent": (100, 180, 255),
            "glow": (150, 255, 255),
            "tube": (0, 200, 200),
            "muzzle": (255, 200, 100),
        }
    }

    def get_sdmg_theme(style):  # type: ignore
        key = style[5:] if style.startswith("sdmg_") else style
        return SDMG_THEMES.get(key, SDMG_THEMES["default"])


SDMG_BULLET_THEMES = {f"sdmg_{name}": data for name, data in SDMG_THEMES.items()}


def _ensure_style(style: str | None) -> str:
    if not style:
        return "sdmg_default"
    if style.startswith("sdmg_"):
        key = style[5:]
    else:
        key = style
    return f"sdmg_{key}" if key in SDMG_THEMES else "sdmg_default"


def _get_theme(style: str | None):
    return get_sdmg_theme(_ensure_style(style))


def _spawn_particle(pos, color, mode="spark", count=1):
    from sprites import Particle

    for _ in range(count):
        Particle(pos, color, mode=mode)


def _floating_text(x, y, text, color):
    from sprites import FloatingText

    FloatingText(int(x), int(y), text, color)


def _damage_enemy(enemy, dmg):
    if hasattr(enemy, "take_damage"):
        enemy.take_damage(dmg)
    else:
        enemy.hp -= dmg


class OverheatManager:
    """单例化的过热/超频控制器"""

    _instances: dict[object, "OverheatManager"] = {}

    def __init__(self, owner):
        self.owner = owner
        self.heat = 0.0
        self.max_heat = 120.0
        self.base_gain = 6.5
        self.cool_rate = 0.45
        self.recovery_rate = 0.25
        self.overheated = False
        self.overheat_timer = 0
        self.overheat_cooldown = 180
        self.overcharge_timer = 0
        self.overcharge_bonus = 0.5

    @classmethod
    def get_instance(cls, owner):
        if owner not in cls._instances:
            cls._instances[owner] = cls(owner)
        return cls._instances[owner]

    def reset(self):
        self.heat = 0
        self.overheated = False
        self.overheat_timer = 0
        self.overcharge_timer = 0

    def update(self):
        if self.overcharged:
            self.overcharge_timer = max(0, self.overcharge_timer - 1)

        if self.overheated:
            self.overheat_timer = max(0, self.overheat_timer - 1)
            self.heat = max(0.0, self.heat - self.recovery_rate)
            if self.overheat_timer <= 0 and self.heat <= self.max_heat * 0.4:
                self.overheated = False
            return

        if self.heat > 0:
            decay = self.cool_rate
            if getattr(self.owner, "is_moving", False):
                decay *= 0.8
            self.heat = max(0.0, self.heat - decay)

    def add_heat(self, amount: float | None = None):
        if self.overheated:
            return
        gain = amount if amount is not None else self.base_gain
        if self.overcharged:
            gain *= 0.4
        self.heat = min(self.max_heat, self.heat + gain)
        if self.heat >= self.max_heat:
            self.overheated = True
            self.overheat_timer = self.overheat_cooldown
            _floating_text(self.owner.rect.centerx, self.owner.rect.top - 30, "过热!", (255, 120, 80))
            callback = getattr(self.owner, "on_sdmg_overheat", None)
            if callable(callback):
                try:
                    callback()
                except Exception:
                    pass

    def trigger_overcharge(self, duration=240):
        self.overcharge_timer = max(self.overcharge_timer, duration)
        self.overheated = False
        self.heat = min(self.heat, self.max_heat * 0.85)
        _floating_text(self.owner.rect.centerx, self.owner.rect.top - 20, "超频上线!", (0, 255, 255))

    def get_spread_penalty(self):
        ratio = self.heat / self.max_heat
        penalty = 1.5 + ratio * 4.5
        if self.overheated:
            penalty += 2.0
        elif 0.5 <= ratio < 0.9:
            penalty *= 1.2
        return penalty

    @property
    def is_overheated(self):
        return self.overheated

    @property
    def is_overcharge_active(self):
        return self.overcharged

    @property
    def overcharged(self):
        return self.overcharge_timer > 0


class TracerHitEffect(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.color = color
        self.frame = 0
        all_sprites.add(self)

    def update(self):
        self.frame += 1
        radius = max(1, 12 - self.frame)
        alpha = max(0, 180 - self.frame * 15)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (*self.color, alpha), (12, 12), radius, 2)
        if alpha <= 0:
            self.kill()


class ChlorophyteTracerBullet(pygame.sprite.Sprite):
    """星际海豚主炮：叶绿曳光弹"""

    def __init__(self, x, y, damage, owner=None, style="sdmg_default", spread=0.0):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = _ensure_style(style)
        self.theme = _get_theme(self.style)
        self.color = self.theme.get("energy", (0, 255, 255))
        self.bullet_theme = self.style
        self.b_type = "chlorophyte_tracer"
        self.is_enemy = False
        self.is_special_bullet = False
        self.piercing = 1
        self.damage_mult = 1.0
        self.speed = 15.0
        self.homing_strength = 0.08
        self.float_x = float(x)
        self.float_y = float(y)
        self.vx = math.sin(math.radians(spread)) * self.speed
        self.vy = -math.cos(math.radians(spread)) * self.speed
        self.frame = 0
        self.target = None
        self.trail = []
        self.image = pygame.Surface((18, 36), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self._render()
        all_sprites.add(self)
        bullets.add(self)

    def update(self):
        self.frame += 1
        self._acquire_target()
        self._steer()
        self.float_x += self.vx
        self.float_y += self.vy
        self.rect.center = (int(self.float_x), int(self.float_y))
        self._record_trail()
        self._render()
        if (self.rect.bottom < -40 or self.rect.top > HEIGHT + 40 or
                self.rect.right < -40 or self.rect.left > WIDTH + 40):
            self.kill()

    def _acquire_target(self):
        if self.target and self.target.alive():
            return
        closest = None
        min_dist = 420
        for mob in mobs:
            if not mob.alive():
                continue
            dist = math.hypot(mob.rect.centerx - self.float_x,
                              mob.rect.centery - self.float_y)
            if dist < min_dist:
                min_dist = dist
                closest = mob
        self.target = closest

    def _steer(self):
        if not self.target or not self.target.alive():
            return
        dx = self.target.rect.centerx - self.float_x
        dy = self.target.rect.centery - self.float_y
        dist = math.hypot(dx, dy)
        if dist <= 1:
            return
        nx, ny = dx / dist, dy / dist
        self.vx += nx * self.homing_strength
        self.vy += ny * self.homing_strength
        speed = math.hypot(self.vx, self.vy)
        if speed > 0:
            scale = self.speed / speed
            self.vx *= scale
            self.vy *= scale

    def _record_trail(self):
        if self.frame % 2 == 0:
            self.trail.append((self.rect.centerx, self.rect.centery, 18))
            if len(self.trail) > 8:
                self.trail.pop(0)
        self.trail = [(x, y, max(0, life - 2)) for x, y, life in self.trail if life > 0]

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 9, 18
        for i, (tx, ty, life) in enumerate(self.trail):
            alpha = max(0, 80 - i * 12)
            pygame.draw.circle(self.image, (*self.color, alpha),
                               (tx - self.rect.left, ty - self.rect.top),
                               max(1, life // 6))
        body_color = self.theme.get("armor", (180, 220, 255))
        glow = self.theme.get("glow", (150, 255, 255))
        pygame.draw.rect(self.image, body_color, (6, 6, 6, 24), border_radius=3)
        pygame.draw.rect(self.image, glow, (7, 2, 4, 10), border_radius=2)
        if self.frame % 3 == 0:
            TracerHitEffect(self.rect.centerx, self.rect.centery - 10, glow)


class StarfishMine(pygame.sprite.Sprite):
    """F技能：可附着海星地雷"""

    def __init__(self, x, y, damage, owner, style="sdmg_default"):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = _ensure_style(style)
        self.theme = _get_theme(self.style)
        self.is_enemy = False
        self.is_special_bullet = True
        self.attach_target = None
        self.attach_offset = (0, 0)
        self.state = "seeking"
        self.arm_timer = 90
        self.fuse_timer = 240
        self.float_x = float(x)
        self.float_y = float(y)
        self.vx = 0
        self.vy = -4
        self.frame = 0
        self.size = 46
        self.rings: list[tuple[float, int]] = []
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self._render()
        all_sprites.add(self)

    def update(self):
        self.frame += 1
        if self.state == "seeking":
            self.vy = min(2, self.vy + 0.15)
            self.float_x += self.vx
            self.float_y += self.vy
            self.rect.center = (int(self.float_x), int(self.float_y))
            self._seek_target()
            if self.frame % 4 == 0:
                self._emit_thruster()
        elif self.state == "attached":
            if not self.attach_target or not self.attach_target.alive():
                self.state = "seeking"
                self.attach_target = None
                self.arm_timer = 60
            else:
                tx, ty = self.attach_target.rect.center
                self.float_x = tx + self.attach_offset[0]
                self.float_y = ty + self.attach_offset[1]
                self.rect.center = (int(self.float_x), int(self.float_y))
                self.arm_timer -= 1
                if self.frame % 5 == 0:
                    _spawn_particle(self.rect.center, self.theme.get("energy", (0, 255, 255)))
                if self.frame % 8 == 0:
                    self.rings.append((12.0, 200))
                if self.arm_timer <= 0:
                    self._explode()
        self.fuse_timer -= 1
        if self.fuse_timer <= 0:
            self._explode()
        if self.rect.top > HEIGHT + 60:
            self.kill()
        self._update_rings()
        self._render()

    def _seek_target(self):
        for mob in mobs:
            if self.rect.colliderect(mob.rect):
                self.attach_target = mob
                self.attach_offset = (self.rect.centerx - mob.rect.centerx,
                                      self.rect.centery - mob.rect.centery)
                self.state = "attached"
                self.arm_timer = 75
                self.fuse_timer = 150
                break

    def _explode(self):
        if not self.alive():
            return
        StarfishExplosion(self.rect.centerx, self.rect.centery, self.damage, self.theme)
        self.kill()

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx = cy = self.size // 2
        arm_color = self.theme.get("energy", (0, 255, 255))
        glow_color = self.theme.get("glow", (150, 255, 255))
        pulse = 1 + math.sin(self.frame * 0.1) * 0.3
        pygame.draw.circle(self.image, (*glow_color, 90), (cx, cy), int(20 * pulse))
        for radius, alpha in self.rings:
            pygame.draw.circle(self.image, (*glow_color, alpha), (cx, cy), int(radius), 1)
        for i in range(5):
            angle = math.radians(72 * i + self.frame * 2)
            end = (int(cx + math.cos(angle) * 18), int(cy + math.sin(angle) * 18))
            width = 4 if self.state == "attached" else 3
            pygame.draw.line(self.image, arm_color, (cx, cy), end, width)
        pygame.draw.circle(self.image, self.theme.get("armor", (200, 200, 200)), (cx, cy), 9)

    def _emit_thruster(self):
        color = self.theme.get("tube", (0, 200, 200))
        offset = (
            self.rect.centerx + random.randint(-6, 6),
            self.rect.centery + random.randint(10, 16),
        )
        _spawn_particle(offset, color, count=2)

    def _update_rings(self):
        updated = []
        for radius, alpha in self.rings:
            radius += 1.8
            alpha = max(0, alpha - 8)
            if alpha > 0:
                updated.append((radius, alpha))
        if self.frame % 14 == 0:
            updated.append((10.0, 180))
        self.rings = updated


class StarfishExplosion(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, theme):
        super().__init__()
        self.frame = 0
        self.damage = damage
        self.radius = 90
        self.theme = theme
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self._damage()
        all_sprites.add(self)
        _spawn_particle((x, y), theme.get("glow", (150, 255, 255)), mode="shockwave", count=4)
        for _ in range(10):
            StarfishShard(x, y, theme)

    def _damage(self):
        cx, cy = self.rect.center
        for mob in list(mobs):
            if not mob.alive():
                continue
            dist = math.hypot(mob.rect.centerx - cx, mob.rect.centery - cy)
            if dist <= self.radius:
                _damage_enemy(mob, self.damage)

    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        alpha = max(0, 180 - self.frame * 20)
        pygame.draw.circle(self.image, (*self.theme.get("energy", (0, 255, 255)), alpha),
                           (self.radius, self.radius), max(0, self.radius - self.frame * 6), 4)
        sub_alpha = max(0, alpha - 40)
        if sub_alpha:
            pygame.draw.circle(self.image, (*self.theme.get("glow", (150, 255, 255)), sub_alpha),
                               (self.radius, self.radius), max(0, self.radius - self.frame * 10), 2)
        if alpha <= 0:
            self.kill()


class StarfishShard(pygame.sprite.Sprite):
    """F技能爆炸后的水晶碎屑"""

    def __init__(self, x, y, theme):
        super().__init__()
        self.theme = theme
        self.frame = 0
        angle = random.uniform(0, math.tau)
        speed = random.uniform(3, 7)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.float_x = float(x)
        self.float_y = float(y)
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self._render()
        all_sprites.add(self)

    def _render(self):
        pygame.draw.polygon(
            self.image,
            self.theme.get("shell", (255, 215, 0)),
            [(6, 0), (12, 6), (6, 12), (0, 6)],
        )

    def update(self):
        self.frame += 1
        self.float_x += self.vx
        self.float_y += self.vy
        self.vx *= 0.96
        self.vy *= 0.96
        self.rect.center = (int(self.float_x), int(self.float_y))
        if self.frame > 22:
            self.kill()


class SharknadoMissile(pygame.sprite.Sprite):
    def __init__(self, owner, damage, angle, spiral_index, style):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.angle = angle
        self.spiral_index = spiral_index
        self.style = _ensure_style(style)
        self.theme = _get_theme(self.style)
        self.radius = 20 + spiral_index * 4
        self.height = owner.rect.centery
        self.speed = 6 + spiral_index * 0.2
        self.float_x = float(owner.rect.centerx)
        self.float_y = float(owner.rect.centery)
        self.frame = 0
        self.color = self.theme.get("energy", (0, 255, 255))
        self.is_enemy = False
        self.is_special_bullet = False
        self.bullet_theme = self.style
        self.b_type = "sharknado"
        self.piercing = 2
        self.damage_mult = 1.3
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=owner.rect.center)
        self.afterimage_interval = 3
        self.ripple_interval = 8
        self._render()
        all_sprites.add(self)
        bullets.add(self)

    def update(self):
        if not self.owner or not self.owner.alive():
            self.kill()
            return
        self.frame += 1
        self.angle += 8
        self.radius += 0.3
        self.float_x = self.owner.rect.centerx + math.cos(math.radians(self.angle)) * self.radius
        self.float_y -= self.speed
        self.rect.center = (int(self.float_x), int(self.float_y))
        if self.rect.bottom < -80:
            self.kill()
        if self.frame % 4 == 0:
            _spawn_particle(self.rect.center, self.color)
        if self.frame % self.afterimage_interval == 0:
            SharknadoAfterimage(self.rect.center, self.theme)
        if self.frame % self.ripple_interval == 0:
            WaterRippleEffect(self.rect.center, self.theme)
        self._render()

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        points = []
        for i in range(3):
            angle = math.radians(self.angle + i * 120)
            px = 16 + math.cos(angle) * 12
            py = 16 + math.sin(angle) * 8
            points.append((px, py))
        pygame.draw.polygon(self.image, self.color, points)
        pygame.draw.circle(self.image, (255, 255, 255), (16, 16), 3)


class SharkHitEffect(pygame.sprite.Sprite):
    def __init__(self, x, y, theme):
        super().__init__()
        self.frame = 0
        self.theme = theme
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        all_sprites.add(self)

    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        alpha = max(0, 200 - self.frame * 25)
        pygame.draw.circle(self.image, (*self.theme.get("energy", (0, 255, 255)), alpha), (20, 20), 18 - self.frame)
        if alpha <= 0:
            self.kill()


class SharknadoAfterimage(pygame.sprite.Sprite):
    def __init__(self, center, theme):
        super().__init__()
        self.theme = theme
        self.frame = 0
        self.image = pygame.Surface((34, 34), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self._render()
        all_sprites.add(self)

    def _render(self):
        color = self.theme.get("energy", (0, 255, 255))
        pygame.draw.polygon(
            self.image,
            (*color, 120),
            [(17, 4), (30, 17), (17, 30), (4, 17)],
        )

    def update(self):
        self.frame += 1
        alpha = max(0, 120 - self.frame * 20)
        self.image.set_alpha(alpha)
        if alpha <= 0:
            self.kill()


class WaterRippleEffect(pygame.sprite.Sprite):
    def __init__(self, center, theme):
        super().__init__()
        self.theme = theme
        self.frame = 0
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        all_sprites.add(self)

    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        radius = 10 + self.frame * 2
        alpha = max(0, 100 - self.frame * 12)
        pygame.draw.circle(
            self.image,
            (*self.theme.get("glow", (150, 255, 255)), alpha),
            (30, 30),
            radius,
            2,
        )
        if alpha <= 0:
            self.kill()


class SharknadoSkill:
    @staticmethod
    def activate(owner, style="sdmg_default"):
        style = _ensure_style(style)
        for i in range(18):
            SharknadoMissile(owner, owner.damage * 1.2, angle=i * 20, spiral_index=i % 6, style=style)


class MoonLordHand(pygame.sprite.Sprite):
    def __init__(self, owner, offset, style):
        super().__init__()
        self.owner = owner
        self.offset = offset
        self.style = _ensure_style(style)
        self.theme = _get_theme(self.style)
        self.frame = 0
        self.fire_interval = 15
        self.duration = 420
        self.aura_phase = random.uniform(0, math.tau)
        self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=owner.rect.center)
        all_sprites.add(self)

    def update(self):
        if not self.owner or not self.owner.alive():
            self.kill()
            return
        self.frame += 1
        if self.frame >= self.duration:
            self.kill()
            return
        offset_x = math.sin(self.frame * 0.08 + self.offset) * 40
        offset_y = math.cos(self.frame * 0.05 + self.offset) * 30 - 60
        self.rect.centerx = self.owner.rect.centerx + int(offset_x)
        self.rect.centery = self.owner.rect.centery + int(offset_y)
        if self.frame % self.fire_interval == 0:
            PhantasmOrb(self.rect.centerx, self.rect.centery, self.owner.damage * 1.1, self.owner, self.style)
            MoonRuneEffect(self.rect.center, self.theme)
        if self.frame % 12 == 0:
            MoonRuneEffect(self.rect.center, self.theme)
        self._render()

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        glow = self.theme.get("glow", (150, 255, 255))
        pulse = 16 + math.sin(self.frame * 0.15 + self.aura_phase) * 2
        pygame.draw.circle(self.image, (*glow, 160), (24, 24), int(pulse))
        pygame.draw.circle(self.image, (255, 255, 255), (24, 24), 6)


class PhantasmOrb(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, owner, style):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = _ensure_style(style)
        self.theme = _get_theme(self.style)
        self.float_x = float(x)
        self.float_y = float(y)
        self.angle = -90
        self.speed = 9
        self.is_enemy = False
        self.is_special_bullet = False
        self.piercing = 3
        self.damage_mult = 1.4
        self.bullet_theme = self.style
        self.b_type = "phantasm_orb"
        self.image = pygame.Surface((26, 26), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.frame = 0
        self._render()
        all_sprites.add(self)
        bullets.add(self)

    def update(self):
        self.frame += 1
        self.float_y -= self.speed
        self.rect.center = (int(self.float_x), int(self.float_y))
        if self.frame % 2 == 0:
            self._render()
        if self.rect.bottom < -60:
            self.kill()

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        glow = self.theme.get("energy", (0, 255, 255))
        pygame.draw.circle(self.image, (*glow, 200), (13, 13), 12)
        angle = math.radians(self.frame * 12)
        for i in range(2):
            start = angle + i * math.pi
            end = start + math.pi * 0.6
            pygame.draw.arc(self.image, (255, 255, 255), (3, 3, 20, 20), start, end, 2)
        pygame.draw.circle(self.image, (255, 255, 255), (13, 13), 6)


class MoonLordGazeSkill:
    @staticmethod
    def activate(owner, style="sdmg_default"):
        style = _ensure_style(style)
        existing = getattr(owner, "moonlord_hands", [])
        for hand in existing:
            if hand and hand.alive():
                hand.kill()
        hand_left = MoonLordHand(owner, 0, style)
        hand_right = MoonLordHand(owner, math.pi, style)
        owner.moonlord_hands = [hand_left, hand_right]
        owner.ult3_cooldown = max(60, getattr(owner, "ult3_cooldown", 0))


class MoonRuneEffect(pygame.sprite.Sprite):
    """月球领主之凝视的符文脉冲"""

    def __init__(self, center, theme):
        super().__init__()
        self.theme = theme
        self.frame = 0
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        all_sprites.add(self)

    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        alpha = max(0, 180 - self.frame * 12)
        scale = 20 + self.frame
        color = (*self.theme.get("energy", (0, 255, 255)), alpha)
        pygame.draw.circle(self.image, color, (40, 40), scale, 1)
        for i in range(4):
            angle = math.radians(self.frame * 6 + i * 90)
            start = (40 + math.cos(angle) * scale, 40 + math.sin(angle) * scale)
            end = (40 + math.cos(angle + 0.8) * scale, 40 + math.sin(angle + 0.8) * scale)
            pygame.draw.line(self.image, color, start, end, 2)
        if alpha <= 0:
            self.kill()


class OrbitalStrikeBeam(pygame.sprite.Sprite):
    def __init__(self, owner, damage, style, spawn_x, delay):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.style = _ensure_style(style)
        self.theme = _get_theme(self.style)
        self.spawn_x = spawn_x
        self.delay = delay
        self.frame = 0
        self.duration = 90
        self.active_time = 30
        self.hit_rect = pygame.Rect(spawn_x - 40, 0, 80, HEIGHT)
        self.image = pygame.Surface((80, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(spawn_x - 40, 0))
        self.marker = OrbitalStrikeMarker(spawn_x, self.theme, delay)
        self.has_activated = False
        all_sprites.add(self)

    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        if self.marker:
            self.marker.set_progress(self.frame, self.delay)
        if self.frame < self.delay:
            alpha = 60 + int(40 * math.sin(self.frame * 0.2))
            pygame.draw.rect(self.image, (*self.theme.get("energy", (0, 255, 255)), alpha), (0, 0, 80, HEIGHT), 2)
            return
        active_frame = self.frame - self.delay
        if not self.has_activated and self.marker:
            self.marker.activate()
            self.has_activated = True
        if active_frame <= self.active_time:
            pygame.draw.rect(self.image, (*self.theme.get("glow", (150, 255, 255)), 120), (18, 0, 44, HEIGHT))
            flicker = 12 + math.sin(active_frame * 0.6) * 6
            pygame.draw.rect(self.image, (255, 255, 255, 180), (30, 0, 20, HEIGHT), int(max(1, flicker)))
            if active_frame % 4 == 0:
                self._strike_damage()
        else:
            fade_alpha = max(0, 120 - (active_frame - self.active_time) * 10)
            if fade_alpha:
                pygame.draw.rect(self.image, (*self.theme.get("energy", (0, 255, 255)), fade_alpha), (0, 0, 80, HEIGHT), 1)
        if active_frame > self.duration:
            if self.marker:
                self.marker.fade_out()
                self.marker = None
            self.kill()

    def _strike_damage(self):
        for mob in list(mobs):
            if self.hit_rect.colliderect(mob.rect):
                _damage_enemy(mob, self.damage)
                _spawn_particle(mob.rect.center, self.theme.get("muzzle", (255, 200, 100)))


class OrbitalStrikeSkill:
    @staticmethod
    def activate(owner, style="sdmg_default"):
        style = _ensure_style(style)
        mgr = OverheatManager.get_instance(owner)
        mgr.trigger_overcharge(360)
        try:
            from utils import sound_mgr
            sound_mgr.play("warning")
        except Exception:
            pass
        ping_color = _get_theme(style).get("energy", (0, 255, 255))
        for _ in range(3):
            _spawn_particle((owner.rect.centerx, owner.rect.centery - 30), ping_color, mode="pulse")
        _floating_text(owner.rect.centerx, owner.rect.top - 80, "声呐锁定", ping_color)
        for i in range(6):
            x = random.randint(80, WIDTH - 80)
            delay = i * 12
            OrbitalStrikeBeam(owner, owner.damage * 3, style, x, delay)
        _floating_text(owner.rect.centerx, owner.rect.top - 60, "轨道轰炸!", (255, 200, 120))


class OrbitalStrikeMarker(pygame.sprite.Sprite):
    """轨道轰炸前的地面预兆"""

    def __init__(self, center_x, theme, delay):
        super().__init__()
        self.theme = theme
        self.delay = max(1, delay)
        self.frame = 0
        self.progress = 0.0
        self.state = "charging"
        self.image = pygame.Surface((160, 220), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(center_x, HEIGHT - 110))
        all_sprites.add(self)

    def set_progress(self, frame, delay):
        self.progress = min(1.0, frame / max(1, delay))

    def activate(self):
        self.state = "active"

    def fade_out(self):
        self.state = "fading"

    def update(self):
        self.frame += 1
        self.image.fill((0, 0, 0, 0))
        self.image.set_alpha(255)
        base = self.theme.get("energy", (0, 255, 255))
        accent = self.theme.get("muzzle", (255, 200, 100))
        alpha = 80 + int(100 * self.progress)
        pygame.draw.circle(self.image, (*base, alpha), (80, 200), 50 + int(self.progress * 30), 2)
        pygame.draw.circle(self.image, (*accent, alpha), (80, 200), 20 + int(self.progress * 20), 1)
        pygame.draw.line(self.image, (*accent, alpha), (80, 0), (80, 200), 1)
        if self.state == "active":
            pulse = 20 + int(math.sin(self.frame * 0.4) * 6)
            pygame.draw.rect(self.image, (*base, 160), (74, 0, 12, 200), 0)
            pygame.draw.circle(self.image, (*accent, 160), (80, 200), pulse, 3)
        elif self.state == "fading":
            fade = max(0, 180 - self.frame * 12)
            self.image.set_alpha(fade)
            if fade <= 0:
                self.kill()
