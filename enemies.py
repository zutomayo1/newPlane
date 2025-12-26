"""
Data-driven enemy system (minimal rebuild)
- Three starter enemy archetypes with procedural visuals
- Simple behaviors (downward, sine drift, orbit)
- Factory-based creation from JSON with safe defaults
"""
from __future__ import annotations

import json
import math
import random
from typing import Any, Dict, Optional, Tuple

import pygame

from config import (
    BLACK,
    CYAN,
    ORANGE,
    RED,
    WHITE,
    WIDTH,
    HEIGHT,
    all_sprites,
    enemy_bullets,
    mobs,
)

# ---------------------------------------------------------------------------
# Built-in fallback data (used if JSON is missing)
# ---------------------------------------------------------------------------
BUILTIN_ENEMIES: Dict[str, Dict[str, Any]] = {
    "wisp": {
        "name": "霓虹侦察·WISP",
        "description": "轻型侦察机，蛇形推进，快速单发压制。",
        "hp": 80,
        "speed": 3.6,
        "radius": 16,
        "score": 90,
        "color": [120, 220, 255],
        "bullet_color": [0, 255, 200],
        "behavior": "sine",
        "behavior_params": {"amplitude": 90, "frequency": 0.018},
        "attack_pattern": "single",
        "attack_interval": 42,
        "attack_params": {"angles": [86, 94], "bullet_speed": 7.0},
    },
    "bulwark": {
        "name": "熔核重甲·BULWARK",
        "description": "慢速装甲舰，正面推进，三向压制火力。",
        "hp": 180,
        "speed": 1.6,
        "radius": 22,
        "score": 160,
        "color": [255, 140, 90],
        "bullet_color": [255, 190, 120],
        "behavior": "drift",
        "behavior_params": {"veer": 0.4},
        "attack_pattern": "spread",
        "attack_interval": 78,
        "attack_params": {"angles": [72, 90, 108], "bullet_speed": 5.2},
    },
    "orbiter": {
        "name": "相位轨道·ORBITER",
        "description": "中型环轨机，侧滑并释放环形弹幕。",
        "hp": 130,
        "speed": 2.3,
        "radius": 19,
        "score": 130,
        "color": [180, 120, 255],
        "bullet_color": [210, 170, 255],
        "behavior": "orbit",
        "behavior_params": {"radius": 120, "angular_speed": 1.3, "fall_speed": 1.4},
        "attack_pattern": "burst_circle",
        "attack_interval": 110,
        "attack_params": {"count": 8, "bullet_speed": 4.6},
        "threat": 2,
    },
    "void_hunter": {
        "name": "虚空猎手·VOID HUNTER",
        "description": "极度流线的深海掠食者机体，黑色吸光外壳与紫色灯带，拖曳触手并以回旋刃袭杀。",
        "hp": 120,
        "speed": 3.8,
        "radius": 18,
        "score": 170,
        "color": [90, 40, 150],
        "bullet_color": [180, 80, 255],
        "behavior": "sine",
        "behavior_params": {"amplitude": 110, "frequency": 0.022},
        "attack_pattern": "spread",
        "attack_interval": 54,
        "attack_params": {"angles": [82, 90, 98], "bullet_speed": 6.2},
        "threat": 3,
    },
    "armored_centurion": {
        "name": "重装百夫长·ARMORED CENTURION",
        "description": "悬空的堡垒方块，塔盾符文闪烁，顶置短炮与沉重锁链形成近距压迫。",
        "hp": 260,
        "speed": 1.2,
        "radius": 24,
        "score": 210,
        "color": [190, 150, 80],
        "bullet_color": [255, 200, 120],
        "behavior": "drift",
        "behavior_params": {"veer": 0.25},
        "attack_pattern": "spread",
        "attack_interval": 90,
        "attack_params": {"angles": [75, 90, 105], "bullet_speed": 4.8},
        "threat": 3,
        "has_armor": True,
    },
    "plague_drone": {
        "name": "瘟疫工蜂·PLAGUE DRONE",
        "description": "复眼与透明毒囊的生化蜂机，油污与锈迹斑斑，振动翼与注射腿散播毒液。",
        "hp": 95,
        "speed": 2.9,
        "radius": 17,
        "score": 150,
        "color": [110, 210, 110],
        "bullet_color": [130, 255, 150],
        "behavior": "sine",
        "behavior_params": {"amplitude": 70, "frequency": 0.03},
        "attack_pattern": "burst_circle",
        "attack_interval": 70,
        "attack_params": {"count": 6, "bullet_speed": 4.6},
        "threat": 2,
    },
    "prism_watcher": {
        "name": "棱镜监视者·PRISM WATCHER",
        "description": "由三重分离金属环与中心变色棱晶组成的几何体，洁白陶瓷镶金纹，停转对齐后爆发光束。",
        "hp": 150,
        "speed": 1.8,
        "radius": 20,
        "score": 200,
        "color": [235, 240, 255],
        "bullet_color": [140, 210, 255],
        "behavior": "orbit",
        "behavior_params": {"radius": 130, "angular_speed": 1.6, "fall_speed": 0.8},
        "attack_pattern": "burst_circle",
        "attack_interval": 85,
        "attack_params": {"count": 10, "bullet_speed": 5.0},
        "threat": 3,
    },
    "skeletal_interceptor": {
        "name": "骸骨截击机·SKELETAL INTERCEPTOR",
        "description": "白骨脊柱与张开的肋骨为框架，骷髅头口含激光炮，扭动前行并喷射鬼火推进。",
        "hp": 140,
        "speed": 3.1,
        "radius": 20,
        "score": 190,
        "color": [230, 230, 220],
        "bullet_color": [190, 90, 90],
        "behavior": "sine",
        "behavior_params": {"amplitude": 80, "frequency": 0.018},
        "attack_pattern": "spread",
        "attack_interval": 62,
        "attack_params": {"angles": [78, 90, 102], "bullet_speed": 5.4},
        "threat": 3,
    },
    "frost_webber": {
        "name": "霜寒织网者·FROST WEBBER",
        "description": "冰蓝蛛形无人机，抛洒减速冰网并射出冰锥。",
        "hp": 110,
        "speed": 2.6,
        "radius": 18,
        "score": 170,
        "color": [120, 200, 255],
        "bullet_color": [150, 230, 255],
        "behavior": "sine",
        "behavior_params": {"amplitude": 70, "frequency": 0.022},
        "attack_pattern": "spread",
        "attack_interval": 68,
        "attack_params": {"angles": [85, 90, 95], "bullet_speed": 5.2},
        "threat": 2,
    },
    "storm_javelin": {
        "name": "雷鸣投矛手·STORM JAVELIN",
        "description": "长矛状特斯拉飞矛，高速冲刺后投掷穿透电矛。",
        "hp": 125,
        "speed": 3.4,
        "radius": 18,
        "score": 185,
        "color": [90, 180, 255],
        "bullet_color": [120, 220, 255],
        "behavior": "drift",
        "behavior_params": {"veer": 0.6},
        "attack_pattern": "single",
        "attack_interval": 64,
        "attack_params": {"angles": [88, 90, 92], "bullet_speed": 7.0},
        "threat": 3,
    },
    "phantasmal_splitter": {
        "name": "幻影裂变者·PHANTASMAL SPLITTER",
        "description": "半透明幽影机，分裂幻影交叉扫射并发出缓慢追踪弹。",
        "hp": 115,
        "speed": 2.4,
        "radius": 19,
        "score": 190,
        "color": [150, 120, 255],
        "bullet_color": [200, 180, 255],
        "behavior": "sine",
        "behavior_params": {"amplitude": 60, "frequency": 0.02},
        "attack_pattern": "burst_circle",
        "attack_interval": 78,
        "attack_params": {"count": 6, "bullet_speed": 4.4},
        "threat": 3,
    },
    "rail_shredder": {
        "name": "磁轨破片舰·RAIL SHREDDER",
        "description": "双轨炮工业舰首，穿透点射后释放碎片环。",
        "hp": 180,
        "speed": 2.0,
        "radius": 22,
        "score": 210,
        "color": [200, 80, 80],
        "bullet_color": [255, 160, 120],
        "behavior": "drift",
        "behavior_params": {"veer": 0.35},
        "attack_pattern": "spread",
        "attack_interval": 82,
        "attack_params": {"angles": [85, 90, 95], "bullet_speed": 6.6},
        "threat": 3,
        "has_armor": True,
    },
    "solar_arc_rider": {
        "name": "太阳风弧骑·SOLAR ARC RIDER",
        "description": "金色护罩弧翼，沿弧线机动并释放炽热弧形弹幕。",
        "hp": 150,
        "speed": 2.8,
        "radius": 20,
        "score": 205,
        "color": [255, 200, 120],
        "bullet_color": [255, 170, 90],
        "behavior": "orbit",
        "behavior_params": {"radius": 120, "angular_speed": 1.8, "fall_speed": 1.0},
        "attack_pattern": "spread",
        "attack_interval": 74,
        "attack_params": {"angles": [82, 90, 98], "bullet_speed": 6.0},
        "threat": 3,
    },
    "steel_falcon": {
        "name": "钢羽猎隼·STEEL FALCON",
        "description": "高速俯冲的刀翼猛禽，回旋抛射金属羽。",
        "hp": 85,
        "speed": 3.8,
        "radius": 17,
        "score": 140,
        "color": [200, 220, 240],
        "bullet_color": [255, 180, 120],
        "behavior": "sine",
        "behavior_params": {"amplitude": 90, "frequency": 0.022},
        "attack_pattern": "custom",
        "attack_interval": 70,
        "attack_params": {"angles": [80, 90, 100], "bullet_speed": 6.4},
        "threat": 2,
    },
    "mire_sprayer": {
        "name": "毒雾散射·MIRE SPRAYER",
        "description": "缓慢漂移的毒雾艇，留下腐蚀尾迹并喷洒毒液墙。",
        "hp": 120,
        "speed": 2.0,
        "radius": 19,
        "score": 150,
        "color": [140, 210, 120],
        "bullet_color": [110, 220, 140],
        "behavior": "drift",
        "behavior_params": {"veer": 0.5},
        "attack_pattern": "custom",
        "attack_interval": 80,
        "attack_params": {"angles": [60, 90, 120], "bullet_speed": 3.6},
        "threat": 2,
    },
    "pulse_weaver": {
        "name": "脉冲编织·PULSE WEAVER",
        "description": "三环脉冲球，生成交叉光墙封锁走位。",
        "hp": 110,
        "speed": 1.8,
        "radius": 18,
        "score": 160,
        "color": [170, 140, 255],
        "bullet_color": [190, 170, 255],
        "behavior": "orbit",
        "behavior_params": {"radius": 90, "angular_speed": 1.4, "fall_speed": 0.8},
        "attack_pattern": "custom",
        "attack_interval": 90,
        "attack_params": {"angles": [0, 45, 90, 135, 180, 225, 270, 315], "bullet_speed": 4.0},
        "threat": 2,
    },
    "thorn_gaoler": {
        "name": "荆棘锁链·THORN GAOLER",
        "description": "锁链刑具式飞棺，抓取束缚后近身绞杀。",
        "hp": 150,
        "speed": 2.4,
        "radius": 20,
        "score": 180,
        "color": [160, 120, 110],
        "bullet_color": [220, 180, 140],
        "behavior": "drift",
        "behavior_params": {"veer": 0.2},
        "attack_pattern": "custom",
        "attack_interval": 72,
        "attack_params": {"angles": [88, 90, 92], "bullet_speed": 7.5},
        "threat": 2,
    },
    "astra_fragger": {
        "name": "碎星榴霰·ASTRA FRAGGER",
        "description": "磁轨迫击舰抛洒簇状星芒炸弹，空中裂解为多层弹片雨。",
        "hp": 210,
        "speed": 2.5,
        "radius": 22,
        "score": 260,
        "color": [255, 210, 150],
        "bullet_color": [255, 240, 150],
        "behavior": "drift",
        "behavior_params": {"veer": 0.35},
        "attack_pattern": "custom",
        "attack_interval": 78,
        "attack_params": {"clusters": 3, "shrapnel": 6},
        "threat": 4,
    },
    "ember_siege": {
        "name": "燧火攻垒·EMBER SIEGE",
        "description": "重型熔渣投射塔，抛掷燃岩迫击炮并在地面铺展岩浆。",
        "hp": 260,
        "speed": 1.5,
        "radius": 24,
        "score": 280,
        "color": [255, 140, 90],
        "bullet_color": [255, 170, 120],
        "behavior": "drift",
        "behavior_params": {"veer": 0.18},
        "attack_pattern": "custom",
        "attack_interval": 96,
        "attack_params": {"pools": 2},
        "threat": 4,
    },
    "ion_veil": {
        "name": "离子帷幕·ION VEIL",
        "description": "发射硬光护盾并为附近机体覆盖离子护幕，死亡后爆发EMP冲击。",
        "hp": 230,
        "speed": 1.8,
        "radius": 24,
        "score": 300,
        "color": [140, 210, 255],
        "bullet_color": [120, 240, 255],
        "behavior": "orbit",
        "behavior_params": {"radius": 80, "angular_speed": 0.8, "fall_speed": 0.9},
        "attack_pattern": "custom",
        "attack_interval": 90,
        "attack_params": {"nodes": 3},
        "threat": 4,
    },
    "resonance_breaker": {
        "name": "谐振裁断·RESONANCE BREAKER",
        "description": "声波刃舰压缩空气形成贯穿束，命中后削弱护甲与火力。",
        "hp": 190,
        "speed": 2.6,
        "radius": 20,
        "score": 250,
        "color": [200, 170, 255],
        "bullet_color": [200, 240, 255],
        "behavior": "sine",
        "behavior_params": {"amplitude": 70, "frequency": 0.022},
        "attack_pattern": "custom",
        "attack_interval": 82,
        "attack_params": {"beam_width": 26, "beam_length": 320},
        "threat": 4,
    },
    "cryo_lancer": {
        "name": "霜脉狙矛·CRYO LANCER",
        "description": "多节冰棱机翼喷吐极寒光束，并立起冻结屏障断绝路线。",
        "hp": 205,
        "speed": 2.3,
        "radius": 21,
        "score": 255,
        "color": [170, 220, 255],
        "bullet_color": [150, 230, 255],
        "behavior": "sine",
        "behavior_params": {"amplitude": 60, "frequency": 0.02},
        "attack_pattern": "custom",
        "attack_interval": 88,
        "attack_params": {"wall_length": 200},
        "threat": 4,
    },
    "arc_overseer": {
        "name": "雷锁戍卫·ARC OVERSEER",
        "description": "多臂伏特节点监视器，发射会优先链向僚机的束缚闪电。",
        "hp": 220,
        "speed": 2.2,
        "radius": 22,
        "score": 275,
        "color": [120, 170, 255],
        "bullet_color": [150, 220, 255],
        "behavior": "drift",
        "behavior_params": {"veer": 0.4},
        "attack_pattern": "custom",
        "attack_interval": 76,
        "attack_params": {"jumps": 3},
        "threat": 4,
    },
    "lumen_shade": {
        "name": "虚光魅影·LUMEN SHADE",
        "description": "折叠光幕化作隐形斩翼，潜行后突然于侧翼爆发刃雨。",
        "hp": 175,
        "speed": 3.0,
        "radius": 19,
        "score": 260,
        "color": [210, 210, 255],
        "bullet_color": [255, 255, 190],
        "behavior": "sine",
        "behavior_params": {"amplitude": 90, "frequency": 0.025},
        "attack_pattern": "custom",
        "attack_interval": 70,
        "attack_params": {"daggers": 6},
        "threat": 4,
    },
    "quantum_cleaver": {
        "name": "量子斩舰·QUANTUM CLEAVER",
        "description": "五折相位刃舰，折叠显形后劈出扇形量子光刃，命中会破甲并扭曲时间。",
        "hp": 320,
        "speed": 2.8,
        "radius": 24,
        "score": 420,
        "color": [120, 210, 255],
        "bullet_color": [130, 255, 255],
        "behavior": "sine",
        "behavior_params": {"amplitude": 130, "frequency": 0.02},
        "attack_pattern": "custom",
        "attack_interval": 68,
        "attack_params": {"slash_angles": [60, 72, 84, 96, 108, 120], "slash_speed": 7.2, "slash_damage": 28, "armor_break": 150},
        "threat": 5,
        "is_elite": True,
    },
    "umbra_tormentor": {
        "name": "熵蚀织母·ENTROPIC MATRON",
        "description": "熵蚀孢丝织成的母巢舰体，拖曳网状刻痕与囊泡孢巢，外壳渗出不稳定裂光。",
        "hp": 300,
        "speed": 3.2,
        "radius": 23,
        "score": 410,
        "color": [255, 110, 180],
        "bullet_color": [255, 120, 200],
        "behavior": "sine",
        "behavior_params": {"amplitude": 110, "frequency": 0.024},
        "attack_pattern": "custom",
        "attack_interval": 62,
        "attack_params": {"slash_angles": [70, 80, 90, 100, 110], "slash_speed": 7.6, "slash_damage": 26, "armor_break": 130},
        "threat": 5,
        "is_elite": True,
    },
    "voidfold_mirror": {
        "name": "虚空折镜·VOID MIRROR",
        "description": "折叠镜阵在轨道上交错，扭曲射线令视界白化并反向辐射。",
        "hp": 360,
        "speed": 2.2,
        "radius": 26,
        "score": 430,
        "color": [120, 120, 180],
        "bullet_color": [200, 200, 255],
        "behavior": "orbit",
        "behavior_params": {"radius": 140, "angular_speed": 1.4, "fall_speed": 0.9},
        "attack_pattern": "custom",
        "attack_interval": 80,
        "attack_params": {"whiteout_radius": 150, "whiteout_duration": 150, "whiteout_intensity": 0.85, "beam_count": 5, "damage": 26},
        "threat": 5,
        "is_elite": True,
    },
    "prismatic_overseer": {
        "name": "轨道支援·ORBITAL AIDE",
        "description": "轨道支援单元下沉锁定，外置阵列与伴飞节点组成拦截网，投射校准光束覆盖战区。",
        "hp": 340,
        "speed": 2.4,
        "radius": 25,
        "score": 430,
        "color": [240, 240, 255],
        "bullet_color": [255, 220, 200],
        "behavior": "orbit",
        "behavior_params": {"radius": 150, "angular_speed": 1.2, "fall_speed": 0.9},
        "attack_pattern": "custom",
        "attack_interval": 85,
        "attack_params": {"whiteout_radius": 170, "whiteout_duration": 170, "whiteout_intensity": 0.95, "beam_count": 7, "damage": 24},
        "threat": 5,
        "is_elite": True,
    },
    "chrono_interdictor": {
        "name": "时序干扰·TEMPUS JAMMER",
        "description": "时序干扰器以栅格扰动压制战区节拍，放出干涉环与冻结脉冲，令动作与弹道失衡。",
        "hp": 350,
        "speed": 2.0,
        "radius": 26,
        "score": 440,
        "color": [130, 200, 255],
        "bullet_color": [150, 230, 255],
        "behavior": "drift",
        "behavior_params": {"veer": 0.3},
        "attack_pattern": "custom",
        "attack_interval": 90,
        "attack_params": {"shock_radius": 150, "time_slow": 0.6, "freeze_duration": 80, "damage": 24},
        "threat": 5,
        "is_elite": True,
    },
    "rift_parasite": {
        "name": "裂隙寄生·RIFT PARASITE",
        "description": "胃囊化的裂隙孢巢，喷出携带寄生孢子的缓速瘴弹并铺开绿潮。",
        "hp": 330,
        "speed": 2.4,
        "radius": 24,
        "score": 420,
        "color": [110, 190, 140],
        "bullet_color": [150, 255, 170],
        "behavior": "sine",
        "behavior_params": {"amplitude": 100, "frequency": 0.018},
        "attack_pattern": "custom",
        "attack_interval": 88,
        "attack_params": {"pod_angles": [70, 85, 100], "tick_damage": 5, "duration": 240, "damage": 18},
        "threat": 5,
        "is_elite": True,
    },
    "solar_arc_rider_prime": {
        "name": "太阳风弧骑·SOLAR ARC RIDER",
        "description": "太阳风弧骑拖曳日冕弧面与白障余辉，双层光帆掠过时洒落炙热碎片。",
        "hp": 360,
        "speed": 3.0,
        "radius": 23,
        "score": 450,
        "color": [255, 210, 150],
        "bullet_color": [255, 190, 110],
        "behavior": "orbit",
        "behavior_params": {"radius": 140, "angular_speed": 2.0, "fall_speed": 1.1},
        "attack_pattern": "custom",
        "attack_interval": 70,
        "attack_params": {"arc_count": 2, "whiteout_radius": 120, "damage": 26},
        "threat": 5,
        "is_elite": True,
    },
}

_ENEMY_DATA_CACHE: Optional[Dict[str, Dict[str, Any]]] = None


# ---------------------------------------------------------------------------
# Utility: enemy projectile
# ---------------------------------------------------------------------------
class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self, pos: Tuple[float, float], angle_deg: float, speed: float, color: Tuple[int, int, int]):
        super().__init__()
        self.is_enemy = True
        self.color = color
        self.speed = speed
        self.frozen = False
        self.damage = 20
        self.effect_data: Dict[str, Any] = {}

        size = 12
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        pygame.draw.circle(self.image, WHITE, (size // 2, size // 2), size // 4)
        self.rect = self.image.get_rect(center=pos)
        self.radius = size // 2  # for collide_circle

        rad = math.radians(angle_deg)
        self.velocity = pygame.Vector2(math.cos(rad), math.sin(rad)) * speed

        enemy_bullets.add(self)
        all_sprites.add(self)

    def update(self) -> None:
        if self.frozen:
            return
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Cull when off-screen
        if (
            self.rect.right < -40
            or self.rect.left > WIDTH + 40
            or self.rect.bottom < -40
            or self.rect.top > HEIGHT + 40
        ):
            self.kill()


class HazardZone(pygame.sprite.Sprite):
    """Stationary hazard with a limited lifetime and optional status payload."""

    def __init__(
        self,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        duration: int,
        color: Tuple[int, int, int],
        alpha: int = 120,
        effect_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__()
        w, h = size
        self.effect_data = effect_data or {}
        self.type = self.effect_data.get("visual_type", self.effect_data.get("type", "generic"))
        self.alpha = alpha
        self.image = self._build_surface(w, h, color)
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.radius = max(w, h) // 2
        self.timer = duration
        self.life = duration
        self.damage = self.effect_data.get("damage", 20)
        self.persistent = self.effect_data.get("persistent", True)
        self._hit_cd = 0
        self.hit_cooldown = self.effect_data.get("hit_cooldown", 12)
        self._anim_phase = random.random() * math.tau
        self._wall_offset = random.uniform(0, 12) if self.type == "wall" else 0.0
        self._grab_nodes: list[Tuple[float, float]] = []
        if self.type == "grab":
            node_count = max(1, h // 18)
            for _ in range(node_count):
                # phase offset, sway amplitude
                self._grab_nodes.append((random.random() * math.tau, random.uniform(3, 7)))
        enemy_bullets.add(self)
        all_sprites.add(self)

    def update(self) -> None:
        if self._hit_cd > 0:
            self._hit_cd -= 1
        self._anim_phase += 0.08
        self._apply_animation()
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

    def _build_surface(self, w: int, h: int, color: Tuple[int, int, int]) -> pygame.Surface:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        if self.type == "poison":
            center = (w // 2, h // 2)
            radius = min(w, h) // 2
            for i in range(3):
                alpha = max(40, self.alpha - i * 30)
                pygame.draw.circle(surf, (*color, alpha), center, max(8, radius - i * 4))
            for swirl in range(4):
                ang = swirl * (math.pi / 2)
                vec = (center[0] + math.cos(ang) * radius * 0.6, center[1] + math.sin(ang) * radius * 0.6)
                pygame.draw.circle(surf, (150, 255, 160, 90), vec, 5)
        elif self.type == "wall":
            core = pygame.Surface((w, h), pygame.SRCALPHA)
            for x in range(w):
                ratio = abs((x / max(1, w)) - 0.5) * 2
                alpha = max(40, int(self.alpha * (1.0 - 0.5 * ratio)))
                pygame.draw.line(core, (*color, alpha), (x, 0), (x, h))
            surf.blit(core, (0, 0))
        elif self.type == "parasite":
            swarm = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(swarm, (40, 60, 40, int(self.alpha * 0.6)), (0, 0, w, h))
            center = (w // 2, h // 2)
            pygame.draw.circle(swarm, (90, 140, 70, self.alpha), center, max(6, min(w, h) // 3), 2)
            for i in range(8):
                ang = math.radians(i * 45)
                px = center[0] + int(math.cos(ang) * (max(w, h) // 3))
                py = center[1] + int(math.sin(ang) * (max(w, h) // 3))
                pygame.draw.circle(swarm, (150, 220, 140, 160), (px, py), 4)
            surf.blit(swarm, (0, 0))
        elif self.type == "impact":
            center = (w // 2, h // 2)
            radius = min(w, h) // 2
            pygame.draw.circle(surf, (*color, self.alpha), center, radius)
            pygame.draw.circle(surf, (*WHITE, 200), center, max(2, radius // 2), 2)
        elif self.type == "burn":
            lava = pygame.Surface((w, h), pygame.SRCALPHA)
            for i in range(6):
                offset = random.randint(-6, 6)
                rect = pygame.Rect(0, 0, w, max(6, h // 4))
                rect.center = (w // 2 + offset, h // 2 + i * 3 - 8)
                pygame.draw.ellipse(lava, (255, 120 + i * 10, 80, 80 + i * 20), rect)
            pygame.draw.rect(lava, (255, 200, 120, 50), (0, h // 4, w, h // 2))
            surf.blit(lava, (0, 0))
            pygame.draw.rect(surf, (255, 160, 100, 120), (0, 0, w, h), 2)
        elif self.type == "freeze":
            panel = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(panel, (180, 220, 255, 140), (0, 0, w, h))
            pygame.draw.rect(panel, (255, 255, 255, 200), (2, 2, w - 4, h - 4), 2)
            for x in range(0, w, 8):
                pygame.draw.line(panel, (140, 200, 255, 100), (x, 0), (x + 4, h), 1)
            surf.blit(panel, (0, 0))
        elif self.type == "shield":
            ring = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*color, 160), (w // 2, h // 2), min(w, h) // 2, 3)
            pygame.draw.circle(ring, (255, 255, 255, 120), (w // 2, h // 2), max(8, min(w, h) // 3), 1)
            surf.blit(ring, (0, 0))
        elif self.type == "emp":
            core = pygame.Surface((w, h), pygame.SRCALPHA)
            center = (w // 2, h // 2)
            radius = min(w, h) // 2
            pygame.draw.circle(core, (100, 200, 255, 80), center, radius)
            return core
        elif self.type == "mirror":
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            center = (w // 2, h // 2)
            radius = min(w, h) // 2
            pygame.draw.circle(surf, (210, 230, 255, self.alpha), center, radius, 3)
            pygame.draw.circle(surf, (180, 200, 235, self.alpha // 2), center, max(6, radius - 8), 2)
            grid = pygame.Surface((w, h), pygame.SRCALPHA)
            step = max(6, radius // 4)
            for x in range(0, w, step):
                pygame.draw.line(grid, (180, 210, 240, 80), (x, 0), (x, h), 1)
            for y in range(0, h, step):
                pygame.draw.line(grid, (180, 210, 240, 80), (0, y), (w, y), 1)
            surf.blit(grid, (0, 0))
            # radial prism streaks
            for i in range(12):
                ang = math.radians(i * 30)
                px = center[0] + int(math.cos(ang) * radius)
                py = center[1] + int(math.sin(ang) * radius)
                pygame.draw.line(surf, (255, 255, 255, 70), center, (px, py), 1)
            glow = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 255, 255, 60), center, max(4, radius - 4))
            surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)
            return surf
        elif self.type == "timeslip":
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            center = (w // 2, h // 2)
            radius = min(w, h) // 2
            pygame.draw.circle(surf, (150, 220, 255, self.alpha), center, radius, 2)
            pygame.draw.circle(surf, (255, 255, 255, 90), center, max(6, radius - 10), 1)
            for i in range(6):
                ang = math.radians(i * 60)
                px = center[0] + int(math.cos(ang) * radius)
                py = center[1] + int(math.sin(ang) * radius)
                pygame.draw.line(surf, (180, 230, 255, 120), center, (px, py), 2)
            # inner spiral ticks
            for i in range(10):
                ang = math.radians(i * 36 + 12)
                r = radius * 0.55
                px = center[0] + int(math.cos(ang) * r)
                py = center[1] + int(math.sin(ang) * r)
                pygame.draw.circle(surf, (200, 240, 255, 120), (px, py), 2)
            return surf
        elif self.type == "phase_lock":
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            center = (w // 2, h // 2)
            radius = min(w, h) // 2
            pygame.draw.rect(surf, (170, 210, 255, self.alpha), (0, 0, w, h), 2)
            pygame.draw.circle(surf, (140, 200, 255, self.alpha), center, max(6, radius - 6), 2)
            pygame.draw.circle(surf, (255, 255, 255, 120), center, 4)
            # crosshair and diagonals
            pygame.draw.line(surf, (140, 200, 255, 140), (0, center[1]), (w, center[1]), 1)
            pygame.draw.line(surf, (140, 200, 255, 140), (center[0], 0), (center[0], h), 1)
            pygame.draw.line(surf, (160, 220, 255, 90), (0, 0), (w, h), 1)
            pygame.draw.line(surf, (160, 220, 255, 90), (w, 0), (0, h), 1)
            return surf
        elif self.type == "spore_root":
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            center = (w // 2, h // 2)
            radius = min(w, h) // 2
            pygame.draw.rect(surf, (80, 140, 100, int(self.alpha * 0.8)), (0, 0, w, h))
            for i in range(7):
                ang = math.radians(i * 50 + 12)
                px = center[0] + int(math.cos(ang) * radius * 0.8)
                py = center[1] + int(math.sin(ang) * radius * 0.8)
                pygame.draw.line(surf, (120, 200, 150, 180), center, (px, py), 2)
                pygame.draw.circle(surf, (150, 220, 170, 180), (px, py), 3)
            # spores
            for i in range(18):
                ang = math.radians(i * 20 + 8)
                r = radius * 0.5 + (i % 3) * 3
                px = center[0] + int(math.cos(ang) * r)
                py = center[1] + int(math.sin(ang) * r)
                pygame.draw.circle(surf, (180, 240, 190, 110), (px, py), 2)
            return surf
        elif self.type == "solar_burn":
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            grad = pygame.Surface((w, h), pygame.SRCALPHA)
            for y in range(h):
                alpha = max(40, int(self.alpha * (1 - y / max(1, h))))
                pygame.draw.line(grad, (255, 190, 120, alpha), (0, y), (w, y), 1)
            surf.blit(grad, (0, 0))
            glow = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 220, 150, 120), (0, 0, w, h), 2)
            # heat columns
            col_step = max(10, w // 4)
            for x in range(0, w, col_step):
                pygame.draw.rect(glow, (255, 170, 90, 90), (x, 0, 4, h))
            surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)
            return surf
        elif self.type == "whiteout":
            surf = self.base_image.copy()
            pulse = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(self._anim_phase * 2.0))
            overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, int(110 * pulse)))
            surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
            streaks = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            offset = int((self._anim_phase * 8) % surf.get_height())
            pygame.draw.rect(streaks, (255, 255, 255, 90), (0, offset, surf.get_width(), 6))
            surf.blit(streaks, (0, 0), special_flags=pygame.BLEND_ADD)
            self.image = surf
        elif self.type == "parasite":
            surf = self.base_image.copy()
            tendrils = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            for i in range(6):
                ang = self._anim_phase * 1.6 + i * 1.05
                radius = max(4, self.radius - 4)
                px = surf.get_width() // 2 + int(math.cos(ang) * radius)
                py = surf.get_height() // 2 + int(math.sin(ang) * radius)
                pygame.draw.circle(tendrils, (140, 230, 130, 170), (px, py), 3)
            surf.blit(tendrils, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)
            self.image = surf
            pygame.draw.circle(core, (40, 160, 255, 140), center, max(10, radius - 12), 2)
            surf.blit(core, (0, 0))
        elif self.type == "sonic":
            beam = pygame.Surface((w, h), pygame.SRCALPHA)
            for y in range(0, h, 6):
                alpha = 120 + int(80 * math.sin((y / max(1, h)) * math.pi))
                pygame.draw.line(beam, (200, 230, 255, alpha), (0, y), (w, y), 2)
            surf.blit(beam, (0, 0))
            pygame.draw.rect(surf, (255, 255, 255, 140), (0, 0, w, h), 1)
        elif self.type == "shrapnel":
            center = (w // 2, h // 2)
            for i in range(8):
                ang = math.radians(i * 45)
                length = min(w, h) // 2
                end = (center[0] + int(math.cos(ang) * length), center[1] + int(math.sin(ang) * length))
                pygame.draw.line(surf, (*color, 180), center, end, 2)
            pygame.draw.circle(surf, (255, 255, 255, 200), center, 6, 1)
        elif self.type == "whiteout":
            flare = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(flare, (255, 255, 255, max(120, self.alpha)), (0, 0, w, h))
            vignette = pygame.Surface((w, h), pygame.SRCALPHA)
            radius = max(w, h) // 2
            pygame.draw.circle(vignette, (255, 255, 200, min(220, self.alpha + 60)), (w // 2, h // 2), radius)
            flare.blit(vignette, (0, 0), special_flags=pygame.BLEND_ADD)
            streaks = pygame.Surface((w, h), pygame.SRCALPHA)
            for i in range(5):
                offset = i * 6
                pygame.draw.line(streaks, (255, 255, 255, 80), (0, offset), (w, offset + 6), 3)
            surf.blit(flare, (0, 0))
            surf.blit(streaks, (0, 0), special_flags=pygame.BLEND_ADD)
        elif self.type == "parasite":
            swarm = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(swarm, (40, 60, 40, int(self.alpha * 0.6)), (0, 0, w, h))
            center = (w // 2, h // 2)
            pygame.draw.circle(swarm, (90, 140, 70, self.alpha), center, max(6, min(w, h) // 3), 2)
            for i in range(8):
                ang = math.radians(i * 45)
                px = center[0] + int(math.cos(ang) * (max(w, h) // 3))
                py = center[1] + int(math.sin(ang) * (max(w, h) // 3))
                pygame.draw.circle(swarm, (150, 220, 140, 160), (px, py), 4)
            surf.blit(swarm, (0, 0))
        else:
            pygame.draw.rect(surf, (*color, self.alpha), (0, 0, w, h))
            pygame.draw.rect(surf, (*WHITE, min(220, self.alpha + 40)), (0, 0, w, h), 1)
        return surf

    def _apply_animation(self) -> None:
        if self.type == "poison":
            surf = self.base_image.copy()
            overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            center = (overlay.get_width() // 2, overlay.get_height() // 2)
            radius = min(center) - 2
            arc_start = self._anim_phase
            pygame.draw.arc(
                overlay,
                (180, 255, 200, 120),
                (center[0] - radius, center[1] - radius, radius * 2, radius * 2),
                arc_start,
                arc_start + math.pi / 1.5,
                3,
            )
            surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)
            self.image = surf
        elif self.type == "wall":
            surf = self.base_image.copy()
            glow = 80 + int(60 * (0.5 + 0.5 * math.sin(self._anim_phase * 1.8)))
            scan = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            spacing = 14
            offset = (self._wall_offset + self._anim_phase * 10) % spacing
            for y in range(-spacing, surf.get_height() + spacing, spacing):
                pygame.draw.line(
                    scan,
                    (190, 240, 255, 150),
                    (0, y + offset),
                    (surf.get_width(), y + offset + 6),
                    3,
                )
            surf.blit(scan, (0, 0), special_flags=pygame.BLEND_ADD)
            pulse = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(pulse, (255, 255, 255, glow), pulse.get_rect(), 2)
            core = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            shrink = max(2, surf.get_width() // 5)
            pygame.draw.rect(core, (150, 220, 255, glow), core.get_rect().inflate(-shrink, 0))
            surf.blit(core, (0, 0), special_flags=pygame.BLEND_ADD)
            surf.blit(pulse, (0, 0))
            self.image = surf
        elif self.type == "grab":
            surf = self.base_image.copy()
            overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            width = surf.get_width()
            nodes = self._grab_nodes if self._grab_nodes else [(0.0, 4.0)]
            for idx, y in enumerate(range(6, surf.get_height(), 16)):
                phase, sway_amt = nodes[idx % len(nodes)]
                sway = math.sin(self._anim_phase * 2.2 + phase) * sway_amt
                pygame.draw.circle(
                    overlay,
                    (190, 255, 210, 220),
                    (width // 2 + int(sway), y),
                    5,
                    2,
                )
                pygame.draw.line(
                    overlay,
                    (160, 255, 200, 180),
                    (width // 2 - 10 + int(sway * 0.5), y),
                    (width // 2 + 10 + int(sway * 0.5), y + 6),
                    2,
                )
            vines = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            for side in (-1, 1):
                points: list[Tuple[int, int]] = []
                for seg_idx, y in enumerate(range(0, surf.get_height() + 18, 18)):
                    phase, sway_amt = nodes[seg_idx % len(nodes)]
                    sway = math.sin(self._anim_phase * 1.5 + phase + side * 0.4) * sway_amt
                    offset = side * (12 + sway)
                    points.append((width // 2 + int(offset), y))
                if len(points) >= 2:
                    pygame.draw.lines(vines, (140, 230, 160, 200), False, points, 3)
            surf.blit(vines, (0, 0), special_flags=pygame.BLEND_ADD)
            surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)
            pulse = 0.5 + 0.5 * math.sin(self._anim_phase * 3)
            pygame.draw.rect(surf, (120, 200, 130, int(90 * pulse)), surf.get_rect(), 2)
            self.image = surf
        elif self.type == "impact":
            scale = max(0.4, self.timer / max(1, self.life))
            radius = max(4, int(min(self.rect.width, self.rect.height) * 0.3 * scale))
            surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            center = (surf.get_width() // 2, surf.get_height() // 2)
            pygame.draw.circle(surf, (255, 230, 180, 200), center, radius)
            pygame.draw.circle(surf, (255, 255, 255, 180), center, max(2, radius // 2))
            self.image = surf
        elif self.type == "burn":
            surf = self.base_image.copy()
            glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            pulse = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(self._anim_phase * 1.5))
            pygame.draw.ellipse(glow, (255, 200, 120, int(120 * pulse)), glow.get_rect())
            surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)
            self.image = surf
        elif self.type == "freeze":
            surf = self.base_image.copy()
            frost = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            for x in range(0, frost.get_width(), 10):
                jitter = int(3 * math.sin(self._anim_phase + x * 0.1))
                pygame.draw.line(frost, (200, 240, 255, 140), (x, 0), (x + jitter, frost.get_height()), 1)
            surf.blit(frost, (0, 0), special_flags=pygame.BLEND_ADD)
            self.image = surf
        elif self.type == "shield":
            surf = self.base_image.copy()
            ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            radius = min(surf.get_width(), surf.get_height()) // 2 - 3
            thickness = 2 + int(1 + math.sin(self._anim_phase * 2))
            pygame.draw.circle(ring, (180, 240, 255, 150), (surf.get_width() // 2, surf.get_height() // 2), radius, thickness)
            surf.blit(ring, (0, 0))
            self.image = surf
        elif self.type == "emp":
            surf = self.base_image.copy()
            ripple = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            radius = max(6, int((self.life - self.timer) * (max(surf.get_width(), surf.get_height()) / max(1, self.life))))
            pygame.draw.circle(ripple, (120, 200, 255, 160), (surf.get_width() // 2, surf.get_height() // 2), radius, 2)
            surf.blit(ripple, (0, 0), special_flags=pygame.BLEND_ADD)
            self.image = surf
        elif self.type == "mirror":
            surf = self.base_image.copy()
            halo = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            pulse = 0.5 + 0.5 * math.sin(self._anim_phase * 2.3)
            center = (surf.get_width() // 2, surf.get_height() // 2)
            pygame.draw.circle(halo, (255, 255, 255, int(80 * pulse)), center, max(4, self.radius - 4))
            # rotating spokes
            spoke = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            for i in range(6):
                ang = self._anim_phase * 1.6 + i * math.tau / 6
                px = center[0] + int(math.cos(ang) * (self.radius - 2))
                py = center[1] + int(math.sin(ang) * (self.radius - 2))
                pygame.draw.line(spoke, (200, 230, 255, 90), center, (px, py), 2)
            surf.blit(spoke, (0, 0), special_flags=pygame.BLEND_ADD)
            surf.blit(halo, (0, 0), special_flags=pygame.BLEND_ADD)
            self.image = surf
        elif self.type == "timeslip":
            surf = self.base_image.copy()
            spin = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            center = (surf.get_width() // 2, surf.get_height() // 2)
            radius = min(center) - 2
            for i in range(8):
                ang = self._anim_phase * 2.2 + i * math.pi / 4
                px = center[0] + int(math.cos(ang) * radius)
                py = center[1] + int(math.sin(ang) * radius)
                pygame.draw.line(spin, (200, 240, 255, 140), center, (px, py), 2)
            ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            ring_radius = max(6, radius - 6 + int(2 * math.sin(self._anim_phase * 3)))
            pygame.draw.circle(ring, (180, 230, 255, 100), center, ring_radius, 1)
            surf.blit(ring, (0, 0), special_flags=pygame.BLEND_ADD)
            surf.blit(spin, (0, 0), special_flags=pygame.BLEND_ADD)
            self.image = surf
        elif self.type == "phase_lock":
            surf = self.base_image.copy()
            glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            pulse = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(self._anim_phase * 3.0))
            pygame.draw.rect(glow, (180, 230, 255, int(140 * pulse)), glow.get_rect(), 2)
            # rotating corner markers
            corner = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            off = 4 + int(2 * math.sin(self._anim_phase * 2.5))
            for dx, dy in ((off, off), (surf.get_width() - off, off), (off, surf.get_height() - off), (surf.get_width() - off, surf.get_height() - off)):
                pygame.draw.circle(corner, (150, 210, 255, 160), (dx, dy), 2)
            surf.blit(corner, (0, 0), special_flags=pygame.BLEND_ADD)
            surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)
            self.image = surf
        elif self.type == "spore_root":
            surf = self.base_image.copy()
            shimmer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            jitter = int(2 * math.sin(self._anim_phase * 2.1))
            pygame.draw.rect(shimmer, (150, 230, 170, 120), shimmer.get_rect().inflate(-4 + jitter, -4 + jitter), 2)
            # drifting spores
            spores = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            for i in range(10):
                ang = self._anim_phase * 1.5 + i * 0.6
                r = (self.radius // 2) + i
                px = surf.get_width() // 2 + int(math.cos(ang) * r)
                py = surf.get_height() // 2 + int(math.sin(ang) * r)
                pygame.draw.circle(spores, (180, 240, 200, 90), (px, py), 2)
            surf.blit(spores, (0, 0), special_flags=pygame.BLEND_ADD)
            surf.blit(shimmer, (0, 0), special_flags=pygame.BLEND_ADD)
            self.image = surf
        elif self.type == "solar_burn":
            surf = self.base_image.copy()
            flicker = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(self._anim_phase * 4.0))
            pygame.draw.rect(flicker, (255, 200, 120, int(120 * pulse)), flicker.get_rect(), 2)
            waves = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            wave_count = 3
            for i in range(wave_count):
                offset = int((self._anim_phase * 6 + i * 10) % surf.get_height())
                pygame.draw.rect(waves, (255, 180, 100, 70), (0, offset, surf.get_width(), 4))
            surf.blit(waves, (0, 0), special_flags=pygame.BLEND_ADD)
            surf.blit(flicker, (0, 0), special_flags=pygame.BLEND_ADD)
            self.image = surf
        elif self.type == "sonic":
            surf = self.base_image.copy()
            scan = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            offset = (self._anim_phase * 12) % surf.get_height()
            pygame.draw.rect(scan, (200, 240, 255, 80), (0, offset, surf.get_width(), 8))
            surf.blit(scan, (0, 0), special_flags=pygame.BLEND_ADD)
            self.image = surf
        elif self.type == "shrapnel":
            surf = self.base_image.copy()
            sparks = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            for i in range(5):
                ang = self._anim_phase * 3 + i * 1.2
                px = surf.get_width() // 2 + int(math.cos(ang) * (self.radius - 4))
                py = surf.get_height() // 2 + int(math.sin(ang) * (self.radius - 4))
                pygame.draw.circle(sparks, (255, 230, 180, 200), (px, py), 2)
            surf.blit(sparks, (0, 0), special_flags=pygame.BLEND_ADD)
            self.image = surf


# ---------------------------------------------------------------------------
# Enemy core
# ---------------------------------------------------------------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(
        self,
        enemy_id: str,
        config: Dict[str, Any],
        spawn_pos: Optional[Tuple[int, int]] = None,
        preview: bool = False,
        render_scale: float = 1.0,
    ):
        super().__init__()

        self.preview = preview
        if not preview:
            mobs.add(self)
            all_sprites.add(self)

        self.type = enemy_id
        self.name = config.get("name", enemy_id)
        self.description = config.get("description", "")

        self.hp = float(config.get("hp", 60))
        self.max_hp = self.hp
        self.damage = float(config.get("damage", 10))
        self.score = int(config.get("score", 100))
        self.base_speed = float(config.get("speed", 2.0))
        self.radius = int(config.get("radius", 18))
        if self.preview and render_scale != 1.0:
            self.radius = max(4, int(self.radius * render_scale))
        self.is_elite = bool(config.get("is_elite", False))

        self.behavior = config.get("behavior", "down")
        self.behavior_params = config.get("behavior_params", {})
        self.attack_pattern = config.get("attack_pattern", None)
        self.attack_interval = max(12, int(config.get("attack_interval", 60)))
        self.attack_params = config.get("attack_params", {})
        self.bullet_color = tuple(config.get("bullet_color", [255, 80, 80]))

        self.timer = 0.0
        self.attack_timer = 0.0
        self.phase = random.random() * 360
        self._alt_fire = False  # alternate fire modes for certain enemies
        self._trail_timer = 0
        self._grab_cooldown = 0
        self.ally_shield_timer = 0
        self.ally_shield_strength = 0.0
        self._support_timer = 0
        self._stealth_timer = random.randint(60, 140)
        self._stealth_cooldown = random.randint(90, 150)
        self._stealthed = False
        self._pending_relocate = False

        # Status flags used elsewhere in main.py
        self.time_slow_factor = 1.0
        self.frozen_timer = 0
        self.poison_timer = 0
        self.aurora_slow = 0
        self.entangle_timer = 0
        self.has_armor = bool(config.get("has_armor", False))

        self.image = self._build_image(color=tuple(config.get("color", [255, 120, 120])))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect()
        if spawn_pos:
            self.rect.center = spawn_pos
        else:
            self.rect.centerx = random.randint(60, WIDTH - 60)
            self.rect.centery = random.randint(-80, -40)

        # Movement bookkeeping
        self._orbit_anchor = pygame.Vector2(self.rect.center)
        self._orbit_angle = random.random() * 360

    # ------------------------------------------------------------------
    # Visuals
    def _apply_elite_signature(self, surf: pygame.Surface) -> None:
        """Apply a consistent elite-grade visual signature overlay."""
        w, h = surf.get_size()
        if w <= 0 or h <= 0:
            return
        c = w // 2
        r = self.radius

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)

        # Pulsing halo ring
        pulse = 0.6 + 0.4 * math.sin(self.timer * 0.16)
        halo_alpha = int(40 + 55 * pulse)
        halo_r = int(r + 18 + 2 * math.sin(self.timer * 0.08))
        pygame.draw.circle(overlay, (255, 255, 255, halo_alpha), (c, h // 2), halo_r, 2)
        pygame.draw.circle(overlay, (120, 200, 255, int(22 + 28 * pulse)), (c, h // 2), halo_r + 8, 1)

        # Corner brackets (UI-like frame hints)
        bracket = int(max(10, r * 0.9))
        pad = int(max(6, r * 0.55))
        col = (255, 255, 255, int(90 + 60 * pulse))
        for sx in (-1, 1):
            for sy in (-1, 1):
                x0 = c + sx * (r + pad)
                y0 = h // 2 + sy * (r + pad)
                pygame.draw.line(overlay, col, (x0, y0), (x0 + sx * bracket, y0), 2)
                pygame.draw.line(overlay, col, (x0, y0), (x0, y0 + sy * bracket), 2)

        # Center insignia (star/diamond)
        insignia = pygame.Surface((w, h), pygame.SRCALPHA)
        star_r = max(6, r // 2)
        pts = []
        for i in range(10):
            ang = math.radians(i * 36 - 90)
            rad = star_r if i % 2 == 0 else max(4, star_r // 2)
            pts.append((c + int(math.cos(ang) * rad), h // 2 + int(math.sin(ang) * rad)))
        pygame.draw.polygon(insignia, (255, 255, 255, int(70 + 80 * pulse)), pts, 1)
        pygame.draw.circle(insignia, (255, 255, 255, int(90 + 90 * pulse)), (c, h // 2), 2)
        overlay.blit(insignia, (0, 0), special_flags=pygame.BLEND_ADD)

        surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)

    def _build_image(self, color: Tuple[int, int, int]) -> pygame.Surface:
        size = max(54, self.radius * 3)
        surf = pygame.Surface((size, size), pygame.SRCALPHA)

        if self.type == "wisp":
            return self._draw_wisp(surf, color)
        if self.type == "bulwark":
            return self._draw_bulwark(surf, color)
        if self.type == "orbiter":
            return self._draw_orbiter(surf, color)
        if self.type == "void_hunter":
            return self._draw_void_hunter(surf, color)
        if self.type == "armored_centurion":
            return self._draw_centurion(surf, color)
        if self.type == "plague_drone":
            return self._draw_plague_drone(surf, color)
        if self.type == "prism_watcher":
            return self._draw_prism_watcher(surf, color)
        if self.type == "skeletal_interceptor":
            return self._draw_skeletal_interceptor(surf, color)
        if self.type == "frost_webber":
            return self._draw_frost_webber(surf, color)
        if self.type == "storm_javelin":
            return self._draw_storm_javelin(surf, color)
        if self.type == "phantasmal_splitter":
            return self._draw_phantasmal_splitter(surf, color)
        if self.type == "rail_shredder":
            return self._draw_rail_shredder(surf, color)
        if self.type == "solar_arc_rider":
            return self._draw_solar_arc_rider(surf, color)
        if self.type == "steel_falcon":
            return self._draw_steel_falcon(surf, color)
        if self.type == "mire_sprayer":
            return self._draw_mire_sprayer(surf, color)
        if self.type == "pulse_weaver":
            return self._draw_pulse_weaver(surf, color)
        if self.type == "thorn_gaoler":
            return self._draw_thorn_gaoler(surf, color)
        if self.type == "astra_fragger":
            return self._draw_astra_fragger(surf, color)
        if self.type == "ember_siege":
            return self._draw_ember_siege(surf, color)
        if self.type == "ion_veil":
            return self._draw_ion_veil(surf, color)
        if self.type == "resonance_breaker":
            return self._draw_resonance_breaker(surf, color)
        if self.type == "cryo_lancer":
            return self._draw_cryo_lancer(surf, color)
        if self.type == "arc_overseer":
            return self._draw_arc_overseer(surf, color)
        if self.type == "lumen_shade":
            return self._draw_lumen_shade(surf, color)
        if self.type == "quantum_cleaver":
            return self._draw_quantum_slasher(surf, color)
        if self.type == "umbra_tormentor":
            return self._draw_entropic_matron(surf, color)
        if self.type == "voidfold_mirror":
            return self._draw_voidfold_construct(surf, color)
        if self.type == "prismatic_overseer":
            return self._draw_orbital_aide(surf, color)
        if self.type == "chrono_interdictor":
            return self._draw_chrono_interdictor(surf, color)
        if self.type == "rift_parasite":
            return self._draw_rift_parasite(surf, color)
        if self.type == "solar_arc_rider_prime":
            return self._draw_solar_arc_prime(surf, color)

        # Fallback: sharpened tri-dart
        return self._draw_wisp(surf, color)

    def _draw_wisp(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius
        nose = (c, c - r - 10)
        tail = (c, c + r + 12)

        # Layered fuselage
        hull = [(c - r - 6, c + r // 2), (c, tail[1]), (c + r + 6, c + r // 2), nose]
        pygame.draw.polygon(surf, (*color, 230), hull)
        pygame.draw.polygon(surf, WHITE, hull, 2)

        inner_color = (max(0, color[0] - 40), min(255, color[1] + 30), min(255, color[2] + 50))
        spine = [(c - r // 2, c + r // 3), (c, c - r // 3), (c + r // 2, c + r // 3)]
        pygame.draw.polygon(surf, inner_color, spine)

        # Side fins with double arcs
        fin_span = r + 14
        for side in (-1, 1):
            arc_rect = pygame.Rect(c - fin_span, c - 10, fin_span * 2, 30)
            pygame.draw.arc(surf, (*CYAN, 180), arc_rect, math.pi * (0.05 if side == -1 else 1.05), math.pi * (0.95 if side == -1 else 1.95), 3)
            fin_pts = [(c + side * (r - 4), c - 4), (c + side * fin_span, c + 6), (c + side * (r - 2), c + 20)]
            pygame.draw.polygon(surf, (*color, 200), fin_pts)
            pygame.draw.lines(surf, WHITE, True, fin_pts, 1)

        # Dorsal spines and vent cuts
        for i in range(5):
            alpha = 180 - i * 28
            pygame.draw.line(surf, (*CYAN, alpha), (c, c - r + i * 6), (c, c + r // 2 + i * 4), 2)
            pygame.draw.line(surf, (*WHITE, 120), (c - 8 + i * 4, c + r // 3 + i), (c - 8 + i * 4, c + r // 3 + 6 + i), 1)

        # Exhaust plume (feathered)
        for i in range(7):
            spread = 10 + i * 5
            alpha = 150 - i * 18
            plume = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.polygon(plume, (*CYAN, alpha), [(c - spread, c + r // 2 + i * 4), (c, tail[1] + i * 6), (c + spread, c + r // 2 + i * 4)])
            surf.blit(plume, (0, 0))

        # Canopy glint + aggression halo
        pygame.draw.circle(surf, (*WHITE, 210), (c, c - r // 2), 5)
        pygame.draw.circle(surf, (*RED, 110), (c, c), r + 14, 2)
        pygame.draw.circle(surf, (*ORANGE, 160), nose, 3)
        return surf

    def _draw_bulwark(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        # Outer armor shell with inner shadow
        shell_rect = pygame.Rect(0, 0, r * 2 + 22, r * 2 + 10)
        shell_rect.center = (c, c)
        pygame.draw.ellipse(surf, (*color, 235), shell_rect)
        pygame.draw.ellipse(surf, (*BLACK, 120), shell_rect.inflate(-6, -6))
        pygame.draw.ellipse(surf, WHITE, shell_rect, 2)

        # Segment bands and vents
        for offset in (-12, -2, 8):
            pygame.draw.line(surf, (*BLACK, 200), (shell_rect.left + 8, c + offset), (shell_rect.right - 8, c + offset), 3)
            for tick in range(6):
                tx = shell_rect.left + 10 + tick * (shell_rect.width // 6)
                pygame.draw.line(surf, (*WHITE, 140), (tx, c + offset - 3), (tx + 4, c + offset + 3), 1)

        # Hex plating nodes
        hex_r = r + 4
        hex_pts = [(c + int(hex_r * math.cos(math.radians(60 * i + 30))), c + int(hex_r * math.sin(math.radians(60 * i + 30)))) for i in range(6)]
        pygame.draw.polygon(surf, (*WHITE, 140), hex_pts, 1)
        for px, py in hex_pts:
            pygame.draw.circle(surf, (*CYAN, 180), (px, py), 3)

        # Core iris with glass sheen
        eye_r = r // 2 + 2
        pygame.draw.circle(surf, (*WHITE, 220), (c, c - 2), eye_r)
        pygame.draw.circle(surf, (*RED, 210), (c, c - 2), eye_r - 4)
        pygame.draw.circle(surf, (*ORANGE, 230), (c, c - 2), 6)
        pygame.draw.circle(surf, (*CYAN, 160), (c, c - 2), eye_r + 6, 2)

        # Studs and rim glow
        for i in range(10):
            ang = math.radians(i * 36)
            px = c + int(math.cos(ang) * (r + 8))
            py = c + int(math.sin(ang) * (r + 8))
            pygame.draw.circle(surf, (*WHITE, 200), (px, py), 2)

        pygame.draw.circle(surf, (*RED, 150), (c, c), r + 16, 3)
        pygame.draw.circle(surf, (*ORANGE, 190), (c, c), r + 22, 2)
        pygame.draw.circle(surf, (*CYAN, 120), (c, c), r + 26, 1)
        return surf

    def _draw_orbiter(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        # Core with inner glow
        core_r = r // 2 + 5
        pygame.draw.circle(surf, (*color, 230), (c, c), core_r)
        pygame.draw.circle(surf, (*WHITE, 210), (c, c), core_r, 2)
        for i in range(3):
            alpha = 140 - i * 30
            pygame.draw.circle(surf, (*CYAN, alpha), (c, c), core_r - 2 - i * 3, 0)

        # Dual rings
        inner_ring = r + 8
        outer_ring = r + 18
        pygame.draw.circle(surf, (*color, 180), (c, c), inner_ring, 3)
        pygame.draw.circle(surf, (*WHITE, 150), (c, c), inner_ring + 4, 1)
        pygame.draw.circle(surf, (*CYAN, 140), (c, c), outer_ring, 2)
        pygame.draw.circle(surf, (*WHITE, 100), (c, c), outer_ring + 4, 1)

        # Arc segments imply spin
        for i in range(5):
            start = math.radians(18 + i * 72)
            end = start + math.radians(48)
            pygame.draw.arc(surf, (*ORANGE, 180), (c - inner_ring, c - inner_ring, inner_ring * 2, inner_ring * 2), start, end, 3)
            pygame.draw.arc(surf, (*RED, 140), (c - outer_ring, c - outer_ring, outer_ring * 2, outer_ring * 2), start + 0.08, end - 0.06, 2)

        # Orbiting satellites with flares
        for i in range(4):
            ang = math.radians((self.phase * 3 + i * 90 + 20) % 360)
            px = c + int(math.cos(ang) * inner_ring)
            py = c + int(math.sin(ang) * inner_ring)
            pygame.draw.line(surf, (*ORANGE, 170), (c, c), (px, py), 2)
            pygame.draw.circle(surf, (*color, 220), (px, py), 5)
            pygame.draw.circle(surf, (*WHITE, 200), (px, py), 3)
            flare_len = 12
            fx = px + int(math.cos(ang) * flare_len)
            fy = py + int(math.sin(ang) * flare_len)
            pygame.draw.line(surf, (*CYAN, 160), (px, py), (fx, fy), 2)

        # Starburst threat halo
        for ang in range(0, 360, 30):
            rad = math.radians(ang)
            x1 = c + int(math.cos(rad) * (r - 2))
            y1 = c + int(math.sin(rad) * (r - 2))
            x2 = c + int(math.cos(rad) * (outer_ring + 8))
            y2 = c + int(math.sin(rad) * (outer_ring + 8))
            pygame.draw.line(surf, (*WHITE, 140), (x1, y1), (x2, y2), 1)

        pygame.draw.circle(surf, (*RED, 110), (c, c), outer_ring + 12, 2)
        pygame.draw.circle(surf, (*ORANGE, 90), (c, c), outer_ring + 18, 1)
        return surf

    def _draw_void_hunter(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        shell = [(c, c - r - 12), (c - r + 2, c + r // 2), (c, c + r + 10), (c + r - 2, c + r // 2)]
        dark = (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40))
        pygame.draw.polygon(surf, (*dark, 230), shell)
        pygame.draw.polygon(surf, (*color, 200), shell, 2)

        nose = (c, c - r - 14)
        pygame.draw.line(surf, (*RED, 200), nose, (c, c - r + 6), 4)
        for i in range(4):
            ang = math.radians(-12 + i * 8)
            px = c + int(math.sin(ang) * 8)
            py = c - r + int(math.cos(ang) * 8)
            pygame.draw.circle(surf, (*RED, 220), (px, py), 3)

        neon = [(c - r // 2, c - 6), (c, c - r // 3), (c + r // 2, c - 6), (c, c + r // 3)]
        pygame.draw.polygon(surf, (*color, 180), neon, 0)
        pygame.draw.lines(surf, (*WHITE, 180), True, neon, 1)

        for i in range(5):
            alpha = 110 - i * 18
            spread = r + 6 + i * 4
            tail = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.line(tail, (80, 160, 220, alpha), (c, c + r // 2 + i * 6), (c - spread, c + r + 12 + i * 5), 3)
            pygame.draw.line(tail, (80, 160, 220, alpha), (c, c + r // 2 + i * 6), (c + spread, c + r + 12 + i * 5), 3)
            surf.blit(tail, (0, 0))

        for i in range(2):
            ang = math.radians(self.phase * 2 + i * 140)
            blade_r = r + 10
            bx = c + int(math.cos(ang) * blade_r)
            by = c + int(math.sin(ang) * blade_r)
            pts = [(bx - 10, by - 4), (bx + 8, by), (bx - 10, by + 4)] if i % 2 == 0 else [(bx + 10, by - 4), (bx - 8, by), (bx + 10, by + 4)]
            pygame.draw.polygon(surf, (*color, 210), pts)
            pygame.draw.polygon(surf, WHITE, pts, 1)
        return surf

    def _draw_centurion(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        core_rect = pygame.Rect(0, 0, r * 2, r * 2)
        core_rect.center = (c, c)
        pygame.draw.rect(surf, (*color, 230), core_rect)
        pygame.draw.rect(surf, (*BLACK, 160), core_rect.inflate(-8, -8))
        pygame.draw.rect(surf, WHITE, core_rect, 2)

        shield = [(core_rect.left - 12, core_rect.top + 6), (core_rect.left + r // 2, core_rect.centery), (core_rect.left - 12, core_rect.bottom - 6)]
        pygame.draw.polygon(surf, (*color, 220), shield)
        pygame.draw.polygon(surf, (*CYAN, 140), shield, 2)
        pygame.draw.circle(surf, (*ORANGE, 200), (core_rect.left + 4, core_rect.centery), 5)

        turret = pygame.Rect(0, 0, r // 2 + 6, r // 2)
        turret.center = (c, core_rect.top + 6)
        pygame.draw.rect(surf, (*BLACK, 200), turret)
        pygame.draw.rect(surf, (*RED, 160), turret, 1)
        pygame.draw.rect(surf, (*ORANGE, 200), turret.move(0, -4).inflate(-turret.width // 3, -turret.height // 3))

        for offset in (-10, 10):
            chain_x = core_rect.centerx + offset
            pygame.draw.line(surf, (*BLACK, 220), (chain_x, core_rect.bottom), (chain_x, core_rect.bottom + 12), 3)
            ball_center = (chain_x, core_rect.bottom + 18)
            pygame.draw.circle(surf, (*color, 210), ball_center, 6)
            pygame.draw.circle(surf, (*WHITE, 150), ball_center, 6, 1)

        for i in range(3):
            pygame.draw.line(surf, (*ORANGE, 140), (core_rect.left + 6, core_rect.top + 6 + i * 8), (core_rect.right - 6, core_rect.top + 6 + i * 8), 2)
        return surf

    def _draw_plague_drone(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        eye_r = r // 2 + 3
        pygame.draw.circle(surf, (*color, 220), (c, c - r // 2), eye_r)
        pygame.draw.circle(surf, (*BLACK, 200), (c, c - r // 2), eye_r - 4)
        pygame.draw.circle(surf, (*CYAN, 200), (c, c - r // 2), 4)

        belly = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(belly, (color[0], color[1], color[2], 120), (c - r, c - r // 2, r * 2, r * 2))
        pygame.draw.ellipse(belly, (*WHITE, 160), (c - r, c - r // 2, r * 2, r * 2), 2)
        for i in range(4):
            bx = c + random.randint(-r // 2, r // 2)
            by = c + random.randint(-r // 4, r)
            pygame.draw.circle(belly, (120, 255, 140, 140), (bx, by), 4)
        surf.blit(belly, (0, 0))

        wing_span = r + 10
        for side in (-1, 1):
            pts = [(c, c - r // 3), (c + side * wing_span, c - r), (c + side * (wing_span + 4), c - r + 10), (c + side * wing_span, c - r + 18)]
            pygame.draw.polygon(surf, (*WHITE, 160), pts, 1)
            pygame.draw.polygon(surf, (*color, 140), pts, 0)

        for i in range(6):
            lx = c - r + i * (r // 2)
            pygame.draw.line(surf, (*BLACK, 200), (lx, c + r // 2), (lx, c + r + 12), 2)
            pygame.draw.circle(surf, (*WHITE, 180), (lx, c + r + 14), 2)
        return surf

    def _draw_steel_falcon(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        wing_span = r + 24
        body = [(c, c - r - 8), (c - 6, c), (c, c + r + 10), (c + 6, c)]
        pygame.draw.polygon(surf, (*color, 230), body)
        pygame.draw.polygon(surf, WHITE, body, 2)

        for side in (-1, 1):
            wing = [(c, c - r // 2), (c + side * wing_span, c), (c, c + r // 2)]
            pygame.draw.polygon(surf, (*color, 200), wing)
            pygame.draw.lines(surf, (*WHITE, 160), False, wing, 1)
        pygame.draw.circle(surf, RED, (c, c - r - 4), 4)
        pygame.draw.circle(surf, WHITE, (c, c - r - 4), 2)
        return surf

    def _draw_mire_sprayer(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        hull = pygame.Rect(c - r - 6, c - r // 2, r * 2 + 12, r + 18)
        pygame.draw.ellipse(surf, (*color, 220), hull)
        pygame.draw.ellipse(surf, (*BLACK, 140), hull.inflate(-8, -8))
        pygame.draw.ellipse(surf, WHITE, hull, 2)

        sac = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(sac, (color[0], color[1]+20, color[2], 120), (c - r, c, r * 2, r))
        pygame.draw.ellipse(sac, (*WHITE, 120), (c - r, c, r * 2, r), 2)
        surf.blit(sac, (0, 0))
        for i in range(4):
            drop_x = c - r + i * (r // 2)
            pygame.draw.circle(surf, (110, 220, 140, 180), (drop_x, c + r // 2 + i), 2)
        return surf

    def _draw_pulse_weaver(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        for ring, alpha in [(r, 200), (r + 8, 140), (r + 16, 90)]:
            pygame.draw.circle(surf, (*color, alpha), (c, c), ring, 2)
        pygame.draw.circle(surf, (*WHITE, 220), (c, c), 4)
        for ang in range(0, 360, 60):
            rad = math.radians(ang)
            x = c + int(math.cos(rad) * (r + 12))
            y = c + int(math.sin(rad) * (r + 12))
            pygame.draw.line(surf, (*CYAN, 180), (c, c), (x, y), 2)
        return surf

    def _draw_thorn_gaoler(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        body = pygame.Rect(c - r // 2, c - r, r, r * 2 + 8)
        pygame.draw.rect(surf, (*color, 230), body)
        pygame.draw.rect(surf, (*BLACK, 170), body.inflate(-6, -6))
        pygame.draw.rect(surf, WHITE, body, 2)
        for i in range(6):
            y = body.top + 6 + i * (body.height // 6)
            pygame.draw.line(surf, (*RED, 180), (body.left - 8, y), (body.right + 8, y), 2)
        for side in (-1, 1):
            chain = [(body.centerx + side * (r + 4), body.bottom - 6), (body.centerx + side * (r + 12), body.bottom + 12), (body.centerx + side * (r + 2), body.bottom + 18)]
            pygame.draw.lines(surf, (*WHITE, 200), False, chain, 2)
        face_rect = pygame.Rect(0, 0, r // 2, r // 2)
        face_rect.center = (c, c)
        pygame.draw.rect(surf, (*BLACK, 200), face_rect)
        pygame.draw.rect(surf, (*RED, 180), face_rect, 1)
        return surf

    def _draw_prism_watcher(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        prism = [(c, c - r // 2 - 4), (c - r + 4, c + r // 2 + 4), (c + r - 4, c + r // 2 + 4)]
        pygame.draw.polygon(surf, (*WHITE, 230), prism)
        pygame.draw.polygon(surf, (*color, 180), prism, 2)
        pygame.draw.circle(surf, (*CYAN, 170), (c, c + 2), 4)

        rings = [r + 6, r + 14, r + 22]
        for idx, ring in enumerate(rings):
            alpha = 180 - idx * 40
            pygame.draw.circle(surf, (*color, alpha), (c, c), ring, 2)
            pygame.draw.arc(surf, (*ORANGE, alpha), (c - ring, c - ring, ring * 2, ring * 2), 0.2, 1.1, 3)

        for i in range(6):
            ang = math.radians(i * 60)
            pygame.draw.line(surf, (*WHITE, 120), (c, c), (c + int(math.cos(ang) * (r + 26)), c + int(math.sin(ang) * (r + 26))), 1)
        return surf

    def _draw_skeletal_interceptor(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        spine_len = r + 12
        for i in range(6):
            y = c - spine_len // 2 + i * (spine_len // 5)
            pygame.draw.line(surf, (*color, 220), (c, y), (c, y + 6), 3)
            rib_span = r - 2 + i * 2
            pygame.draw.arc(surf, (*RED, 140), (c - rib_span, y, rib_span * 2, 10), math.pi, 2 * math.pi, 2)

        skull_rect = pygame.Rect(0, 0, r + 12, r // 2 + 10)
        skull_rect.center = (c, c - spine_len // 2 - 4)
        pygame.draw.rect(surf, (*color, 220), skull_rect)
        pygame.draw.rect(surf, (*BLACK, 200), skull_rect.inflate(-6, -6))
        pygame.draw.rect(surf, (*RED, 180), skull_rect.inflate(-10, -10))
        pygame.draw.rect(surf, WHITE, skull_rect, 2)
        pygame.draw.rect(surf, (*CYAN, 170), (skull_rect.centerx - 2, skull_rect.bottom - 2, 4, 8))

        flame = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.polygon(flame, (80, 200, 200, 140), [(c - 6, c + spine_len // 2 + 6), (c + 6, c + spine_len // 2 + 6), (c, c + spine_len // 2 + 20)])
        surf.blit(flame, (0, 0))
        return surf

    def _draw_frost_webber(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        # 八条不对称晶腿
        legs = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(8):
            ang = math.radians(i * 45 + 12)
            length = r + 20 + (i % 3) * 6
            base = (c + int(math.cos(ang) * (r * 0.5)), c + int(math.sin(ang) * (r * 0.5)))
            tip = (c + int(math.cos(ang) * length), c + int(math.sin(ang) * length))
            pygame.draw.line(legs, (180, 230, 255, 190), base, tip, 3)
            pygame.draw.line(legs, (220, 255, 255, 180), base, tip, 1)
            nozzle = pygame.Rect(0, 0, 6, 6)
            nozzle.center = tip
            pygame.draw.ellipse(legs, (200, 240, 255, 180), nozzle)
        surf.blit(legs, (0, 0))

        # 核心冰晶 + 脑组织脉冲
        shell = []
        for i in range(7):
            ang = math.radians(60 * i - 20)
            shell.append((c + int(math.cos(ang) * (r + 4)), c + int(math.sin(ang) * (r + 4))))
        pygame.draw.polygon(surf, (150, 220, 255, 230), shell)
        pygame.draw.polygon(surf, WHITE, shell, 2)

        brain = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(brain, (200, 120, 200, 160), (c, c), r // 2)
        pygame.draw.circle(brain, (255, 180, 255, 180), (c + 2, c - 2), r // 3)
        pygame.draw.line(brain, (120, 200, 255, 180), (c - r // 3, c), (c + r // 3, c), 2)
        surf.blit(brain, (0, 0))

        # 冰网雾气与雪花拖尾
        web = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(8):
            ang = math.radians(45 * i)
            end = (c + int(math.cos(ang) * (r + 12)), c + int(math.sin(ang) * (r + 12)))
            pygame.draw.line(web, (160, 220, 255, 140), (c, c), end, 2)
        pygame.draw.circle(web, (150, 210, 255, 60), (c, c), r + 24, 2)
        surf.blit(web, (0, 0))

        frost = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(12):
            ang = math.radians(i * 30)
            dot = (c + int(math.cos(ang) * (r + 18)), c + int(math.sin(ang) * (r + 18)))
            pygame.draw.circle(frost, (230, 250, 255, 90), dot, 2)
        surf.blit(frost, (0, 0))
        return surf

    def _draw_storm_javelin(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        # 长标枪身：铜线圈包裹的轨道管
        shaft = [(c, c - r - 14), (c - 7, c + r + 22), (c + 7, c + r + 22)]
        pygame.draw.polygon(surf, (120, 90, 60, 230), shaft)
        pygame.draw.polygon(surf, WHITE, shaft, 2)

        coils = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(6):
            y = c - r + i * (r // 2)
            pygame.draw.ellipse(coils, (190, 120, 60, 160), (c - r // 2, y, r, 10), 2)
        surf.blit(coils, (0, 0))

        # 三叉戟放电头
        tip = [(c, c - r - 26), (c - 16, c - r + 4), (c + 16, c - r + 4)]
        pygame.draw.polygon(surf, (*WHITE, 245), tip)
        for side in (-1, 0, 1):
            arc = [(c + side * 6, c - r - 8), (c + side * 10, c - r + 2), (c + side * 2, c - r + 12)]
            pygame.draw.lines(surf, (255, 215, 90, 220), False, arc, 2)

        # 悬浮菱形护盾
        shields = pygame.Surface((size, size), pygame.SRCALPHA)
        for side in (-1, 1):
            rh = [(c + side * (r + 8), c - 6), (c + side * (r + 20), c + 4), (c + side * (r + 8), c + 16), (c + side * (r - 4), c + 4)]
            pygame.draw.polygon(shields, (80, 180, 255, 120), rh)
            pygame.draw.polygon(shields, (255, 255, 255, 160), rh, 1)
        surf.blit(shields, (0, 0))

        # 尾部特斯拉球与闪电
        tail = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(tail, (180, 120, 60, 200), (c, c + r + 12), 8)
        for side in (-1, 1):
            bolt = [(c, c + r), (c + side * 10, c + r + 14), (c + side * 4, c + r + 26), (c + side * 16, c + r + 34)]
            pygame.draw.lines(tail, (120, 200, 255, 200), False, bolt, 2)
        surf.blit(tail, (0, 0))

        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(glow, (120, 200, 255, 70), (c, c), r + 22, 2)
        surf.blit(glow, (0, 0))
        return surf

    def _draw_phantasmal_splitter(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        # 故障质块与偏色残影
        ghost = pygame.Surface((size, size), pygame.SRCALPHA)
        for dx, col in [(-6, (80, 200, 255, 110)), (6, (255, 120, 160, 110)), (0, (120, 255, 180, 90))]:
            for _ in range(4):
                w = random.randint(r // 2, r)
                h = random.randint(r // 2, r)
                rx = c + dx + random.randint(-4, 4)
                ry = c + random.randint(-6, 6)
                rect = pygame.Rect(rx - w // 2, ry - h // 2, w, h)
                pygame.draw.rect(ghost, col, rect)
        surf.blit(ghost, (0, 0))

        # 主体黑紫立方聚合
        body = pygame.Surface((size, size), pygame.SRCALPHA)
        for _ in range(8):
            w = random.randint(r // 2, r)
            h = random.randint(r // 2, r)
            rx = c + random.randint(-6, 6)
            ry = c + random.randint(-6, 6)
            rect = pygame.Rect(rx - w // 2, ry - h // 2, w, h)
            pygame.draw.rect(body, (40, 20, 60, 220), rect)
            pygame.draw.rect(body, (180, 140, 255, 140), rect, 1)
        surf.blit(body, (0, 0))

        # 分裂中的高亮碎片
        shards = pygame.Surface((size, size), pygame.SRCALPHA)
        for _ in range(10):
            px = c + random.randint(-r, r)
            py = c + random.randint(-r, r)
            pygame.draw.rect(shards, (200, 180, 255, 160), (px, py, 2, 2))
        surf.blit(shards, (0, 0))

        # 核心光点
        pygame.draw.circle(surf, (255, 255, 255, 240), (c, c), 6)
        pygame.draw.circle(surf, (120, 200, 255, 190), (c, c), 3)
        return surf

    def _draw_rail_shredder(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        # 生锈工业平台
        chassis = pygame.Rect(0, 0, r * 2 + 22, r + 18)
        chassis.center = (c, c)
        pygame.draw.rect(surf, (160, 120, 70, 230), chassis, border_radius=6)
        pygame.draw.rect(surf, WHITE, chassis, 2, border_radius=6)

        armor = pygame.Rect(0, 0, r * 2 + 14, r + 12)
        armor.center = (c, c)
        pygame.draw.rect(surf, (40, 40, 40, 200), armor, 0, border_radius=8)
        pygame.draw.rect(surf, (255, 180, 60, 160), armor.inflate(-6, -6), 1, border_radius=6)

        # 磁悬浮双轨 + 锯片
        for offset in (-10, 10):
            rail = pygame.Rect(0, 0, r * 2 + 10, 8)
            rail.center = (c, c + offset)
            pygame.draw.rect(surf, (230, 150, 70, 230), rail, border_radius=3)
            pygame.draw.rect(surf, (30, 30, 30, 230), rail.inflate(-8, -3), border_radius=2)
            for i in range(-2, 3):
                blade_x = rail.left + rail.width // 2 + i * (rail.width // 5)
                pygame.draw.line(surf, (255, 220, 180, 200), (blade_x, rail.centery - 8), (blade_x, rail.centery + 8), 2)

        # 旋转锯片环
        ring = pygame.Surface((size, size), pygame.SRCALPHA)
        ring_rect = pygame.Rect(0, 0, r * 2 + 30, r * 2 + 22)
        ring_rect.center = (c, c)
        pygame.draw.ellipse(ring, (120, 80, 40, 120), ring_rect, 3)
        for i in range(12):
            ang = math.radians(i * 30)
            rx = c + int(math.cos(ang) * (ring_rect.width // 2))
            ry = c + int(math.sin(ang) * (ring_rect.height // 2))
            pygame.draw.line(ring, (255, 200, 140, 200), (rx, ry), (rx + int(math.cos(ang) * 8), ry + int(math.sin(ang) * 8)), 2)
        surf.blit(ring, (0, 0))

        # 多重滚轴入口
        maw = pygame.Rect(0, 0, r + 12, r // 2 + 6)
        maw.midleft = (chassis.left + 6, c)
        pygame.draw.rect(surf, (100, 50, 30, 230), maw)
        pygame.draw.rect(surf, (255, 120, 60, 180), maw, 2)
        for i in range(4):
            pygame.draw.line(surf, (255, 180, 120, 200), (maw.left + 4, maw.top + 4 + i * 4), (maw.right - 4, maw.top + 6 + i * 4), 2)

        # 铆钉与光效
        bolts = pygame.Surface((size, size), pygame.SRCALPHA)
        for dx in (-r // 2, 0, r // 2):
            for dy in (-r // 3, r // 3):
                pygame.draw.circle(bolts, (255, 230, 200, 180), (c + dx, c + dy), 2)
        surf.blit(bolts, (0, 0))

        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(glow, (255, 150, 80, 80), chassis.inflate(8, 6), 2, border_radius=8)
        surf.blit(glow, (0, 0))
        return surf

    def _draw_solar_arc_rider(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        gold = (235, 200, 110)
        gold2 = (255, 235, 190)
        ember = (255, 150, 80)

        # 弯月光能滑板
        arc_rect = pygame.Rect(0, 0, (r + 20) * 2, (r + 12) * 2)
        arc_rect.center = (c, c + 10)
        pygame.draw.arc(surf, (255, 210, 140, 235), arc_rect, math.pi * 0.18, math.pi * 0.82, 10)
        pygame.draw.arc(surf, (255, 140, 90, 210), arc_rect.inflate(-10, -10), math.pi * 0.2, math.pi * 0.8, 5)
        pygame.draw.arc(surf, (255, 255, 255, 160), arc_rect.inflate(-16, -14), math.pi * 0.22, math.pi * 0.78, 2)

        # 金色人形骑士（头盔+胸甲+披风轮廓）
        rider = pygame.Surface((size, size), pygame.SRCALPHA)
        torso = pygame.Rect(0, 0, 12, 16)
        torso.center = (c, c - 6)
        pygame.draw.rect(rider, (*gold, 220), torso, border_radius=3)
        pygame.draw.rect(rider, (120, 90, 40, 210), torso.inflate(-6, -6), border_radius=2)
        helm = pygame.Rect(0, 0, 10, 10)
        helm.center = (c, c - 18)
        pygame.draw.ellipse(rider, (*gold2, 230), helm)
        pygame.draw.ellipse(rider, (255, 255, 255, 210), helm.inflate(-6, -6))
        # 护肩
        pygame.draw.polygon(rider, (*gold, 210), [(c - 10, c - 12), (c - 2, c - 10), (c - 6, c - 2)])
        pygame.draw.polygon(rider, (*gold, 210), [(c + 10, c - 12), (c + 2, c - 10), (c + 6, c - 2)])
        # 腿部落点（连接到滑板）
        pygame.draw.line(rider, (255, 220, 150, 210), (c - 2, torso.bottom - 1), (c - 6, c + 6), 3)
        pygame.draw.line(rider, (255, 220, 150, 210), (c + 2, torso.bottom - 1), (c + 6, c + 6), 3)
        # 披风（扇形剪影）
        cape = [(c, c - 8), (c - 18, c + 6), (c, c + 10), (c + 10, c + 2)]
        pygame.draw.polygon(rider, (255, 170, 120, 80), cape)
        surf.blit(rider, (0, 0))

        # 扇形硬光光帆（巨大、偏扇面）
        sail = pygame.Surface((size, size), pygame.SRCALPHA)
        apex = (c - 10, c - r - 12)
        base1 = (c - r - 22, c + 6)
        base2 = (c + r + 28, c + 12)
        sail_poly = [apex, base1, base2]
        pygame.draw.polygon(sail, (255, 235, 170, 110), sail_poly)
        pygame.draw.polygon(sail, (255, 190, 120, 170), sail_poly, 2)
        for i in range(7):
            t = i / 6.0
            ix = int(base1[0] * (1 - t) + base2[0] * t)
            iy = int(base1[1] * (1 - t) + base2[1] * t)
            pygame.draw.line(sail, (255, 210, 150, 120), apex, (ix, iy), 1)
        surf.blit(sail, (0, 0), special_flags=pygame.BLEND_ADD)

        # 彩虹尾迹（沿弧线多层叠色）
        tail = pygame.Surface((size, size), pygame.SRCALPHA)
        for idx, col in enumerate(((200, 180, 255), (120, 210, 255), (150, 255, 210))):
            pygame.draw.arc(
                tail,
                (*col, 70),
                arc_rect.inflate(12 + idx * 6, 10 + idx * 4),
                math.pi * (0.18 + 0.02 * idx),
                math.pi * (0.82 - 0.02 * idx),
                6 - idx,
            )
        flare = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(flare, (*ember, 85), (c - r, c + 10, r * 2, r))
        pygame.draw.ellipse(flare, (255, 240, 200, 70), (c - r // 2, c - r // 4, r, r))
        surf.blit(flare, (0, 0), special_flags=pygame.BLEND_ADD)
        surf.blit(tail, (0, 0), special_flags=pygame.BLEND_ADD)
        return surf

    def _draw_quantum_slasher(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        # 目标外形：巨型人型机甲上半身 + 黑金配色 + 双手巨剑 + 背部相位装置
        obsidian = (18, 18, 24)
        obsidian2 = (34, 34, 44)
        gold = (235, 200, 90)
        gold2 = (255, 235, 190)
        phase_glow = (min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40))

        def _pt(x: float, y: float) -> Tuple[int, int]:
            return (int(x), int(y))

        def _draw_sword(layer: pygame.Surface, base: Tuple[float, float], angle_deg: float, length: float, width: float) -> None:
            ang = math.radians(angle_deg)
            dx = math.cos(ang) * length
            dy = math.sin(ang) * length
            px = -math.sin(ang)
            py = math.cos(ang)
            w = width / 2.0

            tip = (base[0] + dx, base[1] + dy)
            p1 = (base[0] + px * w, base[1] + py * w)
            p2 = (tip[0] + px * (w * 0.35), tip[1] + py * (w * 0.35))
            p3 = (tip[0] - px * (w * 0.35), tip[1] - py * (w * 0.35))
            p4 = (base[0] - px * w, base[1] - py * w)
            blade = [_pt(*p1), _pt(*p2), _pt(*p3), _pt(*p4)]
            pygame.draw.polygon(layer, (160, 170, 190, 220), blade)
            pygame.draw.polygon(layer, (90, 100, 120, 200), blade, 2)
            pygame.draw.line(layer, (255, 255, 255, 170), _pt(base[0], base[1]), _pt(tip[0], tip[1]), 1)

            # 护手/握柄
            guard_w = width * 0.9
            guard = [
                _pt(base[0] + px * guard_w, base[1] + py * guard_w),
                _pt(base[0] - px * guard_w, base[1] - py * guard_w),
                _pt(base[0] - px * guard_w + dx * 0.05, base[1] - py * guard_w + dy * 0.05),
                _pt(base[0] + px * guard_w + dx * 0.05, base[1] + py * guard_w + dy * 0.05),
            ]
            pygame.draw.polygon(layer, (*gold, 220), guard)
            hilt_end = (base[0] - dx * 0.12, base[1] - dy * 0.12)
            pygame.draw.line(layer, (60, 60, 70, 230), _pt(*base), _pt(*hilt_end), max(2, int(width * 0.25)))
            pygame.draw.circle(layer, (*gold2, 220), _pt(*hilt_end), max(2, int(width * 0.25)))

        body = pygame.Surface((size, size), pygame.SRCALPHA)

        # 背部相位装置（在最底层）
        back = pygame.Surface((size, size), pygame.SRCALPHA)
        ring_r = r + 20
        ring_center = (c, c - 12)
        pygame.draw.circle(back, (*phase_glow, 40), ring_center, ring_r + 10)
        pygame.draw.circle(back, (*phase_glow, 120), ring_center, ring_r, 3)
        pygame.draw.circle(back, (255, 255, 255, 140), ring_center, ring_r - 8, 1)
        for i in range(10):
            ang = math.radians(i * 36 - self.phase * 1.4)
            x1 = ring_center[0] + int(math.cos(ang) * (ring_r - 6))
            y1 = ring_center[1] + int(math.sin(ang) * (ring_r - 6))
            x2 = ring_center[0] + int(math.cos(ang) * (ring_r + 6))
            y2 = ring_center[1] + int(math.sin(ang) * (ring_r + 6))
            pygame.draw.line(back, (*phase_glow, 120), (x1, y1), (x2, y2), 2)
        body.blit(back, (0, 0), special_flags=pygame.BLEND_ADD)

        # 机甲上半身（黑金）
        torso = pygame.Surface((size, size), pygame.SRCALPHA)
        chest = [(c - 18, c - 10), (c - 30, c + 12), (c, c + 28), (c + 30, c + 12), (c + 18, c - 10), (c, c - 24)]
        pygame.draw.polygon(torso, (*obsidian2, 235), chest)
        pygame.draw.polygon(torso, (*obsidian, 235), [(c - 8, c - 18), (c - 18, c + 10), (c, c + 18), (c + 18, c + 10), (c + 8, c - 18)])
        pygame.draw.polygon(torso, (*gold, 210), chest, 2)
        # 肩甲
        for side in (-1, 1):
            pad = pygame.Rect(0, 0, 22, 14)
            pad.center = (c + side * 24, c - 18)
            pygame.draw.rect(torso, (*obsidian2, 235), pad, border_radius=4)
            pygame.draw.rect(torso, (*gold, 210), pad, 2, border_radius=4)
            pygame.draw.circle(torso, (*gold2, 170), (pad.centerx, pad.centery), 2)
        # 头部
        head = pygame.Rect(0, 0, 18, 16)
        head.center = (c, c - 34)
        pygame.draw.rect(torso, (*obsidian2, 235), head, border_radius=4)
        pygame.draw.rect(torso, (*gold, 210), head, 2, border_radius=4)
        visor = pygame.Rect(0, 0, 12, 6)
        visor.center = (c, c - 34)
        pygame.draw.rect(torso, (*phase_glow, 160), visor, border_radius=3)
        pygame.draw.rect(torso, (255, 255, 255, 160), visor.inflate(-6, -2), border_radius=2)
        body.blit(torso, (0, 0))

        # 双手巨剑（斜向交叉）
        swords = pygame.Surface((size, size), pygame.SRCALPHA)
        grip_y = c + 2
        left_grip = (c - 22, grip_y)
        right_grip = (c + 22, grip_y)
        sway = 8 * math.sin(self.timer * 0.06)
        _draw_sword(swords, left_grip, -55 + sway, r + 70, 10)
        _draw_sword(swords, right_grip, 235 - sway, r + 70, 10)
        # 手臂连接
        pygame.draw.line(swords, (*gold, 200), (c - 16, c - 6), _pt(*left_grip), 4)
        pygame.draw.line(swords, (*gold, 200), (c + 16, c - 6), _pt(*right_grip), 4)
        pygame.draw.line(swords, (60, 60, 70, 220), (c - 16, c - 6), _pt(*left_grip), 2)
        pygame.draw.line(swords, (60, 60, 70, 220), (c + 16, c - 6), _pt(*right_grip), 2)
        body.blit(swords, (0, 0))

        # 相位能量刻线（胸口）
        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*phase_glow, 120), (c, c - 6), 10)
        pygame.draw.circle(glow, (255, 255, 255, 220), (c, c - 6), 4)
        for i in range(3):
            pygame.draw.line(glow, (*phase_glow, 90), (c - 14, c + 6 + i * 3), (c + 14, c + 6 + i * 3), 1)
        body.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

        self._apply_material_texture(body, (80, 80, 96))
        surf.blit(body, (0, 0))
        return surf

    def _draw_entropic_matron(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        # 目标外形：异虫肉块 + 眼睛触手 + 排卵口滴粘液
        flesh = (max(80, min(255, color[0])), max(40, min(255, color[1] - 40)), max(80, min(255, color[2])))
        bruise = (max(0, flesh[0] - 70), max(0, flesh[1] - 40), max(0, flesh[2] - 70))
        slime = (120, 240, 170)
        tendon = (80, 50, 70)

        body = pygame.Surface((size, size), pygame.SRCALPHA)

        # 肉块主体（多团叠加形成不规则）
        blobs = [
            (c - 10, c + 8, r + 22),
            (c + 14, c + 6, r + 18),
            (c - 2, c - 8, r + 16),
            (c + 4, c + 20, r + 14),
        ]
        for bx, by, br in blobs:
            pygame.draw.circle(body, (*flesh, 235), (bx, by), br)
            pygame.draw.circle(body, (*bruise, 210), (bx, by), max(6, br - 10))

        # 皱褶/筋膜纹理
        folds = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(10):
            ang = math.radians(i * 36 + self.phase * 0.9)
            x1 = c + int(math.cos(ang) * 8)
            y1 = c + 12 + int(math.sin(ang) * 8)
            x2 = c + int(math.cos(ang) * (r + 32))
            y2 = c + 12 + int(math.sin(ang) * (r + 26))
            pygame.draw.line(folds, (*tendon, 85), (x1, y1), (x2, y2), 2)
            pygame.draw.line(folds, (255, 200, 220, 55), (x1, y1), (x2, y2), 1)
        body.blit(folds, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

        # 复数眼球
        eyes = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(5):
            ex = c + int((i - 2) * 12 + 6 * math.sin(self.timer * 0.04 + i))
            ey = c - 12 + int(8 * math.cos(self.timer * 0.05 + i * 0.8))
            pygame.draw.circle(eyes, (255, 255, 255, 220), (ex, ey), 6)
            pygame.draw.circle(eyes, (140, 70, 180, 220), (ex + 1, ey + 1), 3)
            pygame.draw.circle(eyes, (0, 0, 0, 220), (ex + 1, ey + 1), 1)
            pygame.draw.circle(eyes, (255, 255, 255, 140), (ex - 2, ey - 2), 2)
        body.blit(eyes, (0, 0))

        # 触手（眼柄/触手）
        tent = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(8):
            ang = math.radians(i * 45 - 20)
            base = (c, c + 6)
            mid = (c + int(math.cos(ang) * (r + 18)), c + 6 + int(math.sin(ang) * (r + 12)))
            tip = (c + int(math.cos(ang) * (r + 36)), c + 6 + int(math.sin(ang) * (r + 26)))
            pygame.draw.lines(tent, (50, 30, 40, 220), False, [base, mid, tip], 4)
            pygame.draw.lines(tent, (*slime, 90), False, [base, mid, tip], 1)
            pygame.draw.circle(tent, (*slime, 120), tip, 4)
        body.blit(tent, (0, 0))

        # 排卵口（腹部下方）+ 滴落粘液
        maw = pygame.Surface((size, size), pygame.SRCALPHA)
        mouth_rect = pygame.Rect(0, 0, r + 26, r // 2 + 18)
        mouth_rect.center = (c + 6, c + r + 8)
        pygame.draw.ellipse(maw, (60, 20, 30, 230), mouth_rect)
        pygame.draw.ellipse(maw, (255, 120, 160, 160), mouth_rect, 2)
        for i in range(6):
            tx = mouth_rect.left + 8 + i * 6
            pygame.draw.line(maw, (255, 190, 210, 140), (tx, mouth_rect.centery), (tx, mouth_rect.bottom - 4), 2)
        # 粘液滴
        drip_x = mouth_rect.centerx + int(6 * math.sin(self.timer * 0.08))
        drip_y = mouth_rect.bottom + 4
        pygame.draw.circle(maw, (*slime, 150), (drip_x, drip_y), 6)
        pygame.draw.circle(maw, (255, 255, 255, 140), (drip_x - 2, drip_y - 2), 2)
        pygame.draw.ellipse(maw, (*slime, 90), (drip_x - 3, drip_y + 6, 6, 12))
        body.blit(maw, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

        # 腐蚀/孢光晕
        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*slime, 60), (c, c + 10), r + 26, 4)
        pygame.draw.circle(glow, (*slime, 90), (c, c + 10), r + 10, 2)
        body.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

        self._apply_material_texture(body, (max(30, flesh[0] - 60), max(20, flesh[1] - 40), max(30, flesh[2] - 60)))
        surf.blit(body, (0, 0))
        return surf

    def _draw_voidfold_construct(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        # 目标外形：破碎紫水晶镜面 + 虚空碎片 + 镜中漩涡
        is_prismatic = self.type == "prismatic_overseer"
        violet = (170, 110, 255) if not is_prismatic else (255, 240, 210)
        violet2 = (220, 190, 255) if not is_prismatic else (255, 255, 255)
        dark = (max(0, color[0] - 110), max(0, color[1] - 110), max(0, color[2] - 110))

        body = pygame.Surface((size, size), pygame.SRCALPHA)

        # 镜面主体（紫晶镜）
        mirror = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(mirror, (*color, 150), (c, c), r + 4)
        pygame.draw.circle(mirror, (*dark, 180), (c, c), r - 6)
        pygame.draw.circle(mirror, (255, 255, 255, 160), (c, c), r + 4, 2)
        pygame.draw.circle(mirror, (*violet2, 70), (c - 6, c - 8), r - 10)
        body.blit(mirror, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

        # 裂纹（破碎镜面）
        cracks = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(9):
            ang = math.radians(i * 40 + 12)
            x1 = c + int(math.cos(ang) * 6)
            y1 = c + int(math.sin(ang) * 6)
            x2 = c + int(math.cos(ang) * (r + 10))
            y2 = c + int(math.sin(ang) * (r + 10))
            pygame.draw.line(cracks, (255, 255, 255, 120), (x1, y1), (x2, y2), 1)
            # 小分叉
            ang2 = ang + math.radians(18 if i % 2 == 0 else -18)
            xb = c + int(math.cos(ang2) * (r * 0.55))
            yb = c + int(math.sin(ang2) * (r * 0.55))
            xb2 = c + int(math.cos(ang2) * (r + 6))
            yb2 = c + int(math.sin(ang2) * (r + 6))
            pygame.draw.line(cracks, (*violet2, 90), (xb, yb), (xb2, yb2), 1)
        body.blit(cracks, (0, 0), special_flags=pygame.BLEND_ADD)

        # 破碎晶体碎片（环绕）
        shards = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(10):
            ang = math.radians(i * 36 + self.phase * 0.6)
            dist = r + 18 + 6 * math.sin(i * 1.2)
            px = c + int(math.cos(ang) * dist)
            py = c + int(math.sin(ang) * dist)
            tip = (px + int(math.cos(ang) * 10), py + int(math.sin(ang) * 10))
            left = (px + int(math.cos(ang + 1.7) * 8), py + int(math.sin(ang + 1.7) * 8))
            right = (px + int(math.cos(ang - 1.7) * 8), py + int(math.sin(ang - 1.7) * 8))
            poly = [tip, left, right]
            pygame.draw.polygon(shards, (*violet, 170), poly)
            pygame.draw.polygon(shards, (255, 255, 255, 140), poly, 1)
        body.blit(shards, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

        # 镜中漩涡（中心虚空旋涡）
        vortex = pygame.Surface((size, size), pygame.SRCALPHA)
        for k in range(7):
            rr = max(6, r - k * 4)
            a = 120 - k * 12
            rect = pygame.Rect(0, 0, rr * 2, rr * 2)
            rect.center = (c + int(2 * math.sin(self.timer * 0.04 + k)), c + int(2 * math.cos(self.timer * 0.05 + k)))
            pygame.draw.arc(vortex, (10, 10, 20, a), rect, math.pi * 0.2 + self.phase * 0.02, math.pi * 1.6 + self.phase * 0.02, 3)
        pygame.draw.circle(vortex, (0, 0, 0, 200), (c, c), max(6, r // 3))
        pygame.draw.circle(vortex, (*violet2, 90), (c, c), max(6, r // 3) + 6, 2)
        body.blit(vortex, (0, 0), special_flags=pygame.BLEND_ADD)

        self._apply_material_texture(body, (max(30, color[0] - 40), max(30, color[1] - 40), max(40, color[2] - 10)))
        surf.blit(body, (0, 0))
        return surf

    def _draw_orbital_aide(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        # 目标外形：球体核心 + 4 Bits 行星环高速旋转
        accent = (150, 220, 255)
        warm = (255, 230, 190)
        dark = (max(0, color[0] - 110), max(0, color[1] - 110), max(0, color[2] - 110))

        body = pygame.Surface((size, size), pygame.SRCALPHA)

        # 球体核心（分层阴影）
        core_r = r + 10
        pygame.draw.circle(body, (*color, 230), (c, c), core_r)
        pygame.draw.circle(body, (*dark, 210), (c + 6, c + 6), core_r - 8)
        pygame.draw.circle(body, WHITE, (c, c), core_r, 2)
        pygame.draw.circle(body, (*warm, 120), (c - 8, c - 10), max(6, core_r - 14))
        pygame.draw.circle(body, (255, 255, 255, 220), (c - 10, c - 12), 6)

        # 行星环（高速旋转：多层椭圆模糊）
        ring = pygame.Surface((size, size), pygame.SRCALPHA)
        ring_rect = pygame.Rect(0, 0, (core_r + 24) * 2, (core_r + 10) * 2)
        ring_rect.center = (c, c)
        for k in range(4):
            a = 80 - k * 15
            pygame.draw.ellipse(ring, (*accent, a), ring_rect.inflate(k * 6, -k * 2), 3)
        body.blit(ring, (0, 0), special_flags=pygame.BLEND_ADD)

        # 4 个 Bits（环上）
        bits = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(4):
            ang = math.radians(i * 90 - self.phase * 1.4)
            px = c + int(math.cos(ang) * (core_r + 18))
            py = c + int(math.sin(ang) * (core_r + 6))
            brect = pygame.Rect(0, 0, 14, 14)
            brect.center = (px, py)
            pygame.draw.rect(bits, (70, 90, 120, 230), brect, border_radius=4)
            pygame.draw.rect(bits, (*accent, 170), brect, 2, border_radius=4)
            pygame.draw.circle(bits, (255, 255, 255, 210), (px, py), 2)
            # 速度拖尾
            tx = px - int(math.cos(ang) * 10)
            ty = py - int(math.sin(ang) * 4)
            pygame.draw.line(bits, (*accent, 90), (tx, ty), (px, py), 3)
        body.blit(bits, (0, 0), special_flags=pygame.BLEND_ADD)

        # 上方校准小天线（保留一点“支援单元”味道）
        rig = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.line(rig, (*warm, 170), (c, c - core_r - 18), (c, c - core_r + 2), 3)
        pygame.draw.circle(rig, (255, 255, 255, 220), (c, c - core_r - 18), 4)
        pygame.draw.circle(rig, (*accent, 160), (c, c - core_r - 18), 7, 2)
        body.blit(rig, (0, 0), special_flags=pygame.BLEND_ADD)

        self._apply_material_texture(body, color)
        surf.blit(body, (0, 0))
        return surf

    def _draw_chrono_interdictor(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        # 目标外形：金色机械沙漏 + 逆时针齿轮表盘 + 沙向上流
        accent = (150, 220, 255)
        brass = (255, 210, 140)
        brass2 = (255, 240, 200)
        dark = (max(0, color[0] - 110), max(0, color[1] - 110), max(0, color[2] - 110))

        body = pygame.Surface((size, size), pygame.SRCALPHA)

        # 外圈齿轮表盘（逆时针旋转感：齿轮刻线方向按 -phase）
        dial = pygame.Surface((size, size), pygame.SRCALPHA)
        dial_r = r + 14
        pygame.draw.circle(dial, (*brass, 150), (c, c), dial_r, 3)
        pygame.draw.circle(dial, (255, 255, 255, 120), (c, c), dial_r - 10, 1)
        for i in range(18):
            ang = math.radians(i * 20 - self.phase * 1.2)
            inner = dial_r - (10 if i % 3 == 0 else 6)
            outer = dial_r + 6
            p1 = (c + int(math.cos(ang) * inner), c + int(math.sin(ang) * inner))
            p2 = (c + int(math.cos(ang) * outer), c + int(math.sin(ang) * outer))
            pygame.draw.line(dial, (255, 255, 255, 120 if i % 3 == 0 else 80), p1, p2, 2 if i % 3 == 0 else 1)
        # 齿
        for i in range(12):
            ang = math.radians(i * 30 - self.phase * 0.9)
            px = c + int(math.cos(ang) * (dial_r + 8))
            py = c + int(math.sin(ang) * (dial_r + 8))
            tx = -math.sin(ang)
            ty = math.cos(ang)
            tooth = [
                (px + int(tx * 4), py + int(ty * 4)),
                (px - int(tx * 4), py - int(ty * 4)),
                (px - int(tx * 4) + int(math.cos(ang) * 8), py - int(ty * 4) + int(math.sin(ang) * 8)),
                (px + int(tx * 4) + int(math.cos(ang) * 8), py + int(ty * 4) + int(math.sin(ang) * 8)),
            ]
            pygame.draw.polygon(dial, (*brass2, 140), tooth)
        body.blit(dial, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

        # 金色机械沙漏框架
        hour = pygame.Surface((size, size), pygame.SRCALPHA)
        frame_rect = pygame.Rect(0, 0, r + 28, (r + 10) * 2)
        frame_rect.center = (c, c)
        pygame.draw.rect(hour, (*brass, 170), frame_rect, 2, border_radius=10)
        pygame.draw.rect(hour, (120, 90, 40, 140), frame_rect.inflate(-10, -10), 0, border_radius=8)

        top_tri = [(c - 16, c - 10), (c + 16, c - 10), (c, c - r + 8)]
        bot_tri = [(c - 16, c + 12), (c + 16, c + 12), (c, c + r - 8)]
        pygame.draw.polygon(hour, (60, 70, 90, 140), top_tri)
        pygame.draw.polygon(hour, (60, 70, 90, 140), bot_tri)
        pygame.draw.polygon(hour, (255, 255, 255, 120), top_tri, 1)
        pygame.draw.polygon(hour, (255, 255, 255, 120), bot_tri, 1)

        # 上流沙（从下往上）
        sand = pygame.Surface((size, size), pygame.SRCALPHA)
        flow = (self.timer * 0.06) % 1.0
        for i in range(28):
            t = (i / 28.0 + flow) % 1.0
            y = int(c + r - 16 - t * (r * 1.8))
            x = int(c + 2 * math.sin(t * 8 + self.phase * 0.02))
            pygame.draw.circle(sand, (255, 230, 160, 160), (x, y), 2)
        # 堆积层（上方逐渐变厚）
        pile = pygame.Rect(0, 0, r // 2 + 14, r // 2)
        pile.center = (c, c - r + 18)
        pygame.draw.ellipse(sand, (255, 230, 160, 120), pile)
        sand.blit(sand, (0, 0), special_flags=pygame.BLEND_ADD)
        hour.blit(sand, (0, 0), special_flags=pygame.BLEND_ADD)
        body.blit(hour, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

        # 冷色时间刻痕（与外形一致，轻量）
        mark = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(mark, (*accent, 90), (c, c), r - 6, 2)
        pygame.draw.circle(mark, (255, 255, 255, 140), (c, c), 6)
        body.blit(mark, (0, 0), special_flags=pygame.BLEND_ADD)

        self._apply_material_texture(body, color)
        surf.blit(body, (0, 0))
        return surf

    def _draw_rift_parasite(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        r = self.radius

        # 目标外形：金属节肢机械蠕虫 + 吸盘口器内锯齿
        steel = (110, 120, 140)
        steel2 = (170, 180, 200)
        dark = (max(0, color[0] - 110), max(0, color[1] - 110), max(0, color[2] - 110))
        acid = (120, 240, 170)

        body = pygame.Surface((size, size), pygame.SRCALPHA)

        # 分节蠕虫（沿轻微 S 曲线）
        seg_count = 7
        phase = self.timer * 0.06
        pts: list[Tuple[int, int]] = []
        for i in range(seg_count):
            t = i / (seg_count - 1)
            x = c + int((t - 0.5) * (r + 34) + 10 * math.sin(phase + t * 5))
            y = c + int((0.2 - t) * (r + 12) + 10 * math.sin(phase * 0.8 + t * 3))
            pts.append((x, y))

        # 身体节段
        for i, (x, y) in enumerate(pts[::-1]):
            idx = seg_count - 1 - i
            seg_r = max(8, int(r * (0.75 - 0.06 * idx)))
            pygame.draw.circle(body, (*steel, 235), (x, y), seg_r)
            pygame.draw.circle(body, (*dark, 210), (x + 3, y + 3), max(6, seg_r - 6))
            pygame.draw.circle(body, (255, 255, 255, 140), (x, y), seg_r, 2)
            # 机械缝线
            pygame.draw.arc(body, (255, 255, 255, 90), (x - seg_r + 2, y - seg_r + 2, (seg_r - 2) * 2, (seg_r - 2) * 2), 0.2, 2.4, 1)

            # 节肢小腿
            if idx < seg_count - 1:
                for side in (-1, 1):
                    lx = x + side * (seg_r + 4)
                    ly = y + 4
                    tip = (lx + side * 10, ly + 10)
                    pygame.draw.line(body, (50, 60, 70, 220), (x + side * (seg_r - 2), y + 2), tip, 3)
                    pygame.draw.circle(body, (*steel2, 160), tip, 2)

        # 吸盘口器（头部在 pts[0]）
        hx, hy = pts[0]
        mouth = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(mouth, (40, 40, 50, 230), (hx, hy), r // 2 + 8)
        pygame.draw.circle(mouth, (*steel2, 180), (hx, hy), r // 2 + 8, 3)
        pygame.draw.circle(mouth, (0, 0, 0, 220), (hx, hy), r // 2)
        # 内锯齿
        tooth_n = 10
        for i in range(tooth_n):
            ang = math.radians(i * (360 / tooth_n) + self.phase)
            x1 = hx + int(math.cos(ang) * (r // 2 - 2))
            y1 = hy + int(math.sin(ang) * (r // 2 - 2))
            x2 = hx + int(math.cos(ang) * (r // 2 + 6))
            y2 = hy + int(math.sin(ang) * (r // 2 + 6))
            pygame.draw.line(mouth, (255, 255, 255, 150), (x1, y1), (x2, y2), 2)
        pygame.draw.circle(mouth, (*acid, 120), (hx, hy), r // 2 + 16, 2)
        body.blit(mouth, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

        self._apply_material_texture(body, steel)
        surf.blit(body, (0, 0))
        return surf

    def _draw_solar_arc_prime(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        base = self._draw_solar_arc_rider(surf.copy(), color)
        size = base.get_width()
        c = size // 2
        r = self.radius

        # 追加第二层光帆与冠冕
        sail = pygame.Surface((size, size), pygame.SRCALPHA)
        upper = [(c, c - r - 16), (c - r - 18, c - 6), (c + r + 22, c + 4)]
        pygame.draw.polygon(sail, (255, 240, 200, 95), upper)
        pygame.draw.polygon(sail, (255, 200, 120, 140), upper, 2)
        crest = [(c, c - r - 22), (c - 10, c - r - 6), (c + 10, c - r - 6)]
        pygame.draw.polygon(sail, (255, 255, 255, 160), crest)
        base.blit(sail, (0, 0), special_flags=pygame.BLEND_ADD)

        # 日冕环 + 透镜光斑（动态放在 dynamic effects 里，这里提供静态层次）
        aura = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.arc(aura, (255, 240, 200, 120), (c - r - 10, c - r - 2, (r + 10) * 2, (r + 18)), math.pi * 0.2, math.pi * 0.8, 6)
        pygame.draw.arc(aura, (255, 160, 120, 90), (c - r - 18, c - r - 10, (r + 18) * 2, (r + 28)), math.pi * 0.18, math.pi * 0.82, 4)
        base.blit(aura, (0, 0), special_flags=pygame.BLEND_ADD)
        return base

    def _draw_astra_fragger(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        nose = (c, c - self.radius - 14)
        stern = (c, c + self.radius + 14)

        hull = [
            (c - self.radius - 14, c + self.radius // 2),
            (c - 10, c + self.radius + 10),
            (c + 10, c + self.radius + 10),
            (c + self.radius + 14, c + self.radius // 2),
        ]
        pygame.draw.polygon(surf, (*color, 235), hull + [nose])

        plating = pygame.Surface((size, size), pygame.SRCALPHA)
        darker = (max(20, color[0] - 60), max(20, color[1] - 30), max(20, color[2] - 10), 180)
        for i in range(4):
            inset = i * 6
            strip = [
                (hull[0][0] + inset, hull[0][1] - inset // 2),
                (hull[-1][0] - inset, hull[-1][1] - inset // 2),
                (c + 4, stern[1] - inset),
                (c - 4, stern[1] - inset),
            ]
            pygame.draw.polygon(plating, darker, strip, 0)
        surf.blit(plating, (0, 0))

        rails = pygame.Surface((size, size), pygame.SRCALPHA)
        for side in (-1, 1):
            pygame.draw.line(rails, (*WHITE, 180), (c + side * (self.radius // 2), stern[1] - 4), (nose[0] + side * 6, nose[1] + 8), 2)
            pygame.draw.line(rails, (*ORANGE, 180), (c + side * (self.radius // 2), stern[1] + 4), (nose[0] + side * 4, nose[1] + 18), 1)
        surf.blit(rails, (0, 0))

        pod_color = (255, 240, 150, 230)
        glow_color = (255, 170, 60, 130)
        for idx, offset in enumerate((-self.radius, -self.radius // 3, self.radius // 3, self.radius)):
            pod_rect = pygame.Rect(0, 0, 14, 24)
            pod_rect.center = (int(c + offset * 0.6), c)
            pygame.draw.ellipse(surf, pod_color, pod_rect)
            pygame.draw.ellipse(surf, WHITE, pod_rect, 1)
            flame = pygame.Surface((size, size), pygame.SRCALPHA)
            spread = 10 + idx * 2
            pygame.draw.polygon(flame, glow_color, [(pod_rect.centerx - spread, stern[1] - 8), (pod_rect.centerx, stern[1] + 18), (pod_rect.centerx + spread, stern[1] - 8)])
            surf.blit(flame, (0, 0))

        canopy = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(canopy, (255, 240, 210, 230), (c, c - self.radius // 2), 8)
        pygame.draw.circle(canopy, (255, 150, 90, 180), (c + 2, c - self.radius // 2 - 2), 4)
        pygame.draw.circle(canopy, WHITE, (c, c - self.radius // 2), 8, 1)
        surf.blit(canopy, (0, 0))

        insignia = pygame.Surface((size, size), pygame.SRCALPHA)
        star_r = self.radius // 2
        star_pts = []
        for i in range(5):
            ang = math.radians(i * 72 - 90)
            star_pts.append((c + int(math.cos(ang) * star_r), c + int(math.sin(ang) * star_r)))
        pygame.draw.polygon(insignia, (*WHITE, 80), star_pts, 1)
        surf.blit(insignia, (0, 0))

        pygame.draw.lines(surf, WHITE, True, hull + [nose], 2)
        pygame.draw.circle(surf, (255, 200, 120, 210), nose, 5)
        pygame.draw.circle(surf, (*ORANGE, 140), stern, 4)
        self._apply_material_texture(surf, color)
        return surf

    def _draw_ember_siege(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        base = pygame.Rect(c - self.radius - 14, c - self.radius // 2, (self.radius + 14) * 2, self.radius + 24)
        pygame.draw.rect(surf, (*color, 235), base, border_radius=8)
        pygame.draw.rect(surf, (*BLACK, 160), base.inflate(-10, -10), border_radius=6)

        brace = pygame.Surface((size, size), pygame.SRCALPHA)
        for side in (-1, 1):
            leg = pygame.Rect(0, 0, 12, self.radius + 24)
            leg.center = (c + side * (self.radius + 10), c + 4)
            pygame.draw.rect(brace, (90, 60, 40, 220), leg, border_radius=4)
            pygame.draw.rect(brace, (255, 180, 120, 120), leg.inflate(-4, -4), 1, border_radius=3)
        surf.blit(brace, (0, 0))

        furnace = pygame.Surface((size, size), pygame.SRCALPHA)
        core_rect = pygame.Rect(0, 0, base.width - 28, base.height - 22)
        core_rect.center = (c, c + 6)
        pygame.draw.rect(furnace, (120, 40, 0, 220), core_rect, border_radius=6)
        pygame.draw.rect(furnace, (255, 120, 40, 220), core_rect.inflate(-8, -8), border_radius=4)
        for i in range(4):
            slit = pygame.Rect(0, 0, core_rect.width - 16, 6)
            slit.center = (c, core_rect.top + 10 + i * 10)
            pygame.draw.rect(furnace, (255, 200, 120, 160), slit, border_radius=3)
        surf.blit(furnace, (0, 0))

        turret = pygame.Surface((size, size), pygame.SRCALPHA)
        gun_base = pygame.Rect(0, 0, self.radius + 6, self.radius // 2 + 10)
        gun_base.midtop = (c, base.top - 14)
        pygame.draw.rect(turret, (255, 210, 170, 240), gun_base, border_radius=6)
        barrel = pygame.Rect(0, 0, 16, 34)
        barrel.midtop = (c, gun_base.top - 12)
        pygame.draw.rect(turret, (200, 90, 50, 240), barrel, border_radius=4)
        muzzle = pygame.Rect(0, 0, 20, 12)
        muzzle.midtop = (c, barrel.top - 4)
        pygame.draw.rect(turret, (255, 150, 80, 220), muzzle, border_radius=3)
        pygame.draw.rect(turret, WHITE, gun_base, 2, border_radius=6)
        surf.blit(turret, (0, 0))

        hazard = pygame.Surface((size, size), pygame.SRCALPHA)
        for step in range(5):
            glow_rect = base.inflate(step * 6, step * 4)
            pygame.draw.rect(hazard, (255, 90, 30, max(10, 80 - step * 14)), glow_rect, 2, border_radius=10)
        surf.blit(hazard, (0, 0))

        ember_layer = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(14):
            px = random.randint(base.left + 8, base.right - 8)
            py = random.randint(base.bottom - 6, base.bottom + 18)
            pygame.draw.circle(ember_layer, (255, 140, 60, 140), (px, py), random.randint(2, 4))
        surf.blit(ember_layer, (0, 0))
        pygame.draw.rect(surf, WHITE, base, 2, border_radius=8)
        self._apply_material_texture(surf, color)
        return surf

    def _draw_ion_veil(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        core = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(core, (120, 220, 255, 240), (c, c), self.radius // 2)
        pygame.draw.circle(core, (255, 255, 255, 200), (c, c), self.radius // 2, 2)

        halo = pygame.Surface((size, size), pygame.SRCALPHA)
        for ring in range(4):
            rr = self.radius + ring * 6
            alpha = max(20, 120 - ring * 24)
            pygame.draw.circle(halo, (color[0], color[1], 255, alpha), (c, c), rr, 2)
        surf.blit(halo, (0, 0))
        surf.blit(core, (0, 0))

        shard_layer = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(6):
            ang = math.radians(i * 60 + 30)
            px = c + int(math.cos(ang) * (self.radius + 12))
            py = c + int(math.sin(ang) * (self.radius + 12))
            shard = [
                (px, py),
                (int(px + math.cos(ang + 0.2) * 18), int(py + math.sin(ang + 0.2) * 18)),
                (int(px + math.cos(ang - 0.2) * 18), int(py + math.sin(ang - 0.2) * 18)),
            ]
            pygame.draw.polygon(shard_layer, (color[0], color[1], color[2], 160), shard)
            pygame.draw.polygon(shard_layer, WHITE, shard, 1)
        surf.blit(shard_layer, (0, 0))

        for i in range(3):
            ang = math.radians(i * 120 + 30)
            px = c + int(math.cos(ang) * (self.radius + 8))
            py = c + int(math.sin(ang) * (self.radius + 8))
            pygame.draw.circle(surf, (*color, 220), (px, py), 8)
            pygame.draw.circle(surf, WHITE, (px, py), 8, 2)
            pygame.draw.line(surf, (*color, 190), (c, c), (px, py), 3)

        grid = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(12):
            ang = math.radians(i * 30)
            pygame.draw.arc(grid, (*CYAN, 90), (c - self.radius - 16, c - self.radius - 16, (self.radius + 16) * 2, (self.radius + 16) * 2), ang, ang + 0.3, 2)
        surf.blit(grid, (0, 0))
        self._apply_material_texture(surf, color)
        return surf

    def _draw_resonance_breaker(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        spine = [(c, c - self.radius - 12), (c - 10, c + self.radius + 14), (c + 10, c + self.radius + 14)]
        pygame.draw.polygon(surf, (*color, 235), spine)

        ribs = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(6):
            arc_rect = pygame.Rect(c - self.radius - 10, c - 10 + i * 8, (self.radius + 10) * 2, 24)
            alpha = max(30, 180 - i * 24)
            pygame.draw.arc(ribs, (200, 240, 255, alpha), arc_rect, math.pi, 2 * math.pi, 3)
        surf.blit(ribs, (0, 0))

        emitter = pygame.Surface((size, size), pygame.SRCALPHA)
        for side in (-1, 1):
            beam = [
                (c + side * (self.radius // 3), c - self.radius - 6),
                (c + side * (self.radius + 26), c - self.radius + 18),
                (c + side * (self.radius // 3), c - self.radius + 30),
            ]
            pygame.draw.polygon(emitter, (255, 255, 255, 160), beam)
            pygame.draw.polygon(emitter, (180, 210, 255, 140), beam, 2)
        surf.blit(emitter, (0, 0))

        spine_detail = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.lines(spine_detail, WHITE, True, spine, 2)
        for i in range(5):
            pygame.draw.line(spine_detail, (*CYAN, 150), (c - 6, c - self.radius + i * 12), (c + 6, c - self.radius + i * 12), 2)
        surf.blit(spine_detail, (0, 0))

        echo = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(4):
            line_width = 2 + i
            pygame.draw.circle(echo, (255, 255, 255, 40), (c, c - self.radius - 18), self.radius + i * 10, line_width)
        surf.blit(echo, (0, 0))
        self._apply_material_texture(surf, color)
        return surf

    def _draw_cryo_lancer(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        shard_color = (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 60))
        body = [(c, c - self.radius - 18), (c - 14, c + self.radius + 12), (c + 14, c + self.radius + 12)]
        pygame.draw.polygon(surf, (*shard_color, 230), body)

        facets = pygame.Surface((size, size), pygame.SRCALPHA)
        for offset in (-self.radius // 2, 0, self.radius // 2):
            fin = [
                (c + offset // 2, c - 6),
                (c + offset, c + self.radius // 2),
                (c + offset // 4, c + self.radius + 6),
            ]
            pygame.draw.polygon(facets, (color[0], color[1], 255, 150), fin)
            pygame.draw.polygon(facets, WHITE, fin, 1)
        surf.blit(facets, (0, 0))

        core = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.line(core, (200, 240, 255, 220), (c, c - self.radius - 10), (c, c + self.radius + 6), 3)
        pygame.draw.circle(core, (255, 255, 255, 220), (c, c - self.radius - 22), 6)
        pygame.draw.circle(core, (120, 200, 255, 180), (c, c - self.radius - 22), 3)
        surf.blit(core, (0, 0))

        frost = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(20):
            ang = random.random() * math.tau
            dist = random.randint(self.radius // 2, self.radius + 18)
            px = c + int(math.cos(ang) * dist)
            py = c + int(math.sin(ang) * dist)
            pygame.draw.circle(frost, (200, 240, 255, 100), (px, py), 2)
        surf.blit(frost, (0, 0))
        pygame.draw.lines(surf, WHITE, True, body, 2)
        self._apply_material_texture(surf, color)
        return surf

    def _draw_arc_overseer(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        core = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(core, (*color, 235), (c, c), self.radius // 2)
        pygame.draw.circle(core, WHITE, (c, c), self.radius // 2, 2)
        surf.blit(core, (0, 0))

        ring = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(ring, (100, 160, 255, 140), (c, c), self.radius + 6, 2)
        pygame.draw.circle(ring, (50, 80, 120, 120), (c, c), self.radius + 16, 2)
        surf.blit(ring, (0, 0))

        for i in range(4):
            ang = math.radians(i * 90 + 45)
            arm_start = (c + int(math.cos(ang) * (self.radius // 3)), c + int(math.sin(ang) * (self.radius // 3)))
            arm_end = (c + int(math.cos(ang) * (self.radius + 14)), c + int(math.sin(ang) * (self.radius + 14)))
            pygame.draw.line(surf, (*color, 220), arm_start, arm_end, 4)
            pygame.draw.circle(surf, (*color, 220), arm_end, 8, 2)
            coil = pygame.Surface((size, size), pygame.SRCALPHA)
            for step in range(3):
                t = step / 3.0
                mid = (
                    arm_start[0] + (arm_end[0] - arm_start[0]) * t,
                    arm_start[1] + (arm_end[1] - arm_start[1]) * t,
                )
                pygame.draw.circle(coil, (120, 200, 255, 150), (int(mid[0]), int(mid[1])), 4 - step)
            surf.blit(coil, (0, 0))

        lightning = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(8):
            ang = math.radians(i * 45)
            outer = (c + int(math.cos(ang) * (self.radius + 18)), c + int(math.sin(ang) * (self.radius + 18)))
            pygame.draw.line(lightning, (150, 220, 255, 120), (c, c), outer, 1)
        surf.blit(lightning, (0, 0))
        self._apply_material_texture(surf, color)
        return surf

    def _draw_lumen_shade(self, surf: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
        size = surf.get_width()
        c = size // 2
        wing_span = self.radius + 28
        ghost = pygame.Surface((size, size), pygame.SRCALPHA)
        for side in (-1, 1):
            wing = [
                (c, c - self.radius - 4),
                (c + side * wing_span, c),
                (c, c + self.radius + 10),
            ]
            pygame.draw.polygon(ghost, (*color, 150), wing)
            inner = [(int(x * 0.9 + c * 0.1), int(y * 0.9 + c * 0.1)) for x, y in wing]
            pygame.draw.polygon(ghost, (*WHITE, 40), inner)
            pygame.draw.lines(ghost, WHITE, False, wing, 2)
        surf.blit(ghost, (0, 0))

        shimmer = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(6):
            ang = math.radians(i * 60)
            px = c + int(math.cos(ang) * (self.radius + 10))
            py = c + int(math.sin(ang) * (self.radius + 10))
            pygame.draw.circle(shimmer, (255, 255, 200, 90), (px, py), 6)
        surf.blit(shimmer, (0, 0))

        eye = pygame.Surface((size, size), pygame.SRCALPHA)
        iris = pygame.Rect(0, 0, 18, 26)
        iris.center = (c, c)
        pygame.draw.ellipse(eye, (255, 255, 210, 230), iris)
        pygame.draw.ellipse(eye, WHITE, iris, 2)
        pygame.draw.circle(eye, (120, 200, 255, 220), (c, c - 2), 6)
        pygame.draw.circle(eye, (10, 10, 30, 200), (c, c - 2), 3)
        surf.blit(eye, (0, 0))

        cloak = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(3):
            alpha = 40 - i * 10
            spread = wing_span + i * 8
            pygame.draw.arc(cloak, (255, 255, 255, alpha), (c - spread, c - spread, spread * 2, spread * 2), math.pi * 0.1, math.pi * 0.9, 2)
        surf.blit(cloak, (0, 0))
        self._apply_material_texture(surf, color)
        return surf

    def _apply_material_texture(self, surf: pygame.Surface, tint: Tuple[int, int, int]) -> None:
        """Overlay brushed金属/陶瓷纹理，统一高级敌人的质感。"""
        w, h = surf.get_size()
        if w == 0 or h == 0:
            return
        texture = pygame.Surface((w, h), pygame.SRCALPHA)
        key = f"{self.type}-{self.radius}-{int(self.hp)}"
        seed = 0
        for ch in key:
            seed = (seed * 131 + ord(ch)) & 0xFFFFFFFF
        rng = random.Random(seed)

        highlight = (min(255, tint[0] + 60), min(255, tint[1] + 60), min(255, tint[2] + 60), 55)
        shadow = (max(0, tint[0] - 90), max(0, tint[1] - 90), max(0, tint[2] - 90), 45)

        scratch_count = max(18, self.radius // 2)
        for _ in range(scratch_count):
            x1 = rng.randint(-w // 4, w + w // 4)
            y1 = rng.randint(-h // 4, h + h // 4)
            angle = rng.uniform(-0.6, 0.6)
            length = rng.randint(w // 3, int(w * 0.7))
            x2 = int(x1 + math.cos(angle) * length)
            y2 = int(y1 + math.sin(angle) * length)
            pygame.draw.line(texture, highlight, (x1, y1), (x2, y2), 1)

        grain_count = max(32, self.radius)
        for _ in range(grain_count):
            px = rng.randint(0, w - 1)
            py = rng.randint(0, h - 1)
            size = rng.randint(1, 2)
            pygame.draw.rect(texture, shadow, (px, py, size, size))

        bolts = max(6, self.radius // 3)
        bolt_color = (min(255, tint[0] + 20), min(255, tint[1] + 20), min(255, tint[2] + 20), 70)
        for _ in range(bolts):
            px = rng.randint(w // 2 - self.radius, w // 2 + self.radius)
            py = rng.randint(h // 2 - self.radius, h // 2 + self.radius)
            pygame.draw.circle(texture, bolt_color, (px, py), 2)

        surf.blit(texture, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

    # ------------------------------------------------------------------
    # Core update
    def update(self) -> None:
        if self.frozen_timer > 0:
            self.frozen_timer -= 1
            return

        effective_dt = max(0.0, self.time_slow_factor)
        self.time_slow_factor = 1.0  # reset each frame; external effects reapply

        if self.ally_shield_timer > 0:
            self.ally_shield_timer = max(0.0, self.ally_shield_timer - effective_dt)
            if self.ally_shield_timer <= 0:
                self.ally_shield_strength = 0.0

        self.timer += effective_dt
        self.attack_timer += effective_dt

        self._apply_behavior(effective_dt)
        self._apply_dynamic_effects()
        self._apply_support_auras()
        self._maybe_attack()

        # 边界检测：飞出屏幕的敌人自动移除
        if (
            self.rect.top > HEIGHT + 100
            or self.rect.bottom < -100
            or self.rect.left > WIDTH + 100
            or self.rect.right < -100
        ):
            self.kill()

    # ------------------------------------------------------------------
    # Movement behaviors
    def _apply_behavior(self, dt: float) -> None:
        # Custom motions
        if self.type == "void_hunter":
            amp = float(self.behavior_params.get("amplitude", 110))
            freq = float(self.behavior_params.get("frequency", 0.022))
            speed_mult = 1.0 + 0.6 * math.sin(self.timer * 0.15)
            self.rect.x += int(math.sin(self.timer * freq + self.phase) * amp * 0.04)
            self.rect.y += int(self.base_speed * speed_mult * dt)
        elif self.type == "armored_centurion":
            veer = float(self.behavior_params.get("veer", 0.25))
            self.rect.x += int(veer * math.sin(self.timer * 0.02))
            self.rect.y += int(self.base_speed * 0.6 * dt)
        elif self.type == "plague_drone":
            amp = float(self.behavior_params.get("amplitude", 70))
            freq = float(self.behavior_params.get("frequency", 0.03))
            jitter = random.uniform(-0.5, 0.5)
            self.rect.x += int(math.sin(self.timer * freq + self.phase) * amp * 0.04 + jitter)
            self.rect.y += int(self.base_speed * dt)
        elif self.type == "prism_watcher":
            radius = float(self.behavior_params.get("radius", 130))
            angular_speed = float(self.behavior_params.get("angular_speed", 1.6))
            fall_speed = float(self.behavior_params.get("fall_speed", 0.8))
            self._orbit_angle = (self._orbit_angle + angular_speed * dt) % 360
            rad = math.radians(self._orbit_angle)
            offset = pygame.Vector2(math.cos(rad), math.sin(rad)) * radius
            self._orbit_anchor.y += fall_speed * dt
            pos = self._orbit_anchor + offset
            self.rect.centerx = int(pos.x)
            self.rect.centery = int(pos.y)
        elif self.type == "skeletal_interceptor":
            amp = float(self.behavior_params.get("amplitude", 80))
            freq = float(self.behavior_params.get("frequency", 0.018))
            sway = math.sin(self.timer * freq + self.phase)
            self.rect.x += int(sway * amp * 0.05)
            self.rect.y += int(self.base_speed * (1.0 + 0.2 * math.sin(self.timer * 0.1)) * dt)
        elif self.type == "frost_webber":
            amp = float(self.behavior_params.get("amplitude", 70))
            freq = float(self.behavior_params.get("frequency", 0.022))
            pulse = 1.0 + 0.3 * math.sin(self.timer * 0.12)
            self.rect.x += int(math.sin(self.timer * freq + self.phase) * amp * 0.04)
            self.rect.y += int(self.base_speed * pulse * dt)
        elif self.type == "storm_javelin":
            # Dash-and-pause rhythm
            cycle = 140.0
            t_mod = self.timer % cycle
            if t_mod < 36:
                speed_mult = 1.9
            elif t_mod < 56:
                speed_mult = 0.6
            else:
                speed_mult = 1.1
            veer = float(self.behavior_params.get("veer", 0.6))
            self.rect.x += int(veer * math.sin(self.timer * 0.05))
            self.rect.y += int(self.base_speed * speed_mult * dt)
        elif self.type == "phantasmal_splitter":
            amp = float(self.behavior_params.get("amplitude", 60))
            freq = float(self.behavior_params.get("frequency", 0.02))
            sway = math.sin(self.timer * freq + self.phase)
            self.rect.x += int(sway * amp * 0.05)
            self.rect.y += int(self.base_speed * dt)
        elif self.type == "rail_shredder":
            veer = float(self.behavior_params.get("veer", 0.35))
            sidestep = math.sin(self.timer * 0.04 + self.phase) * veer
            self.rect.x += int(sidestep)
            self.rect.y += int(self.base_speed * dt)
        elif self.type == "solar_arc_rider":
            radius = float(self.behavior_params.get("radius", 120))
            ang_speed = float(self.behavior_params.get("angular_speed", 1.8))
            fall_speed = float(self.behavior_params.get("fall_speed", 1.0))
            self._orbit_angle = (self._orbit_angle + ang_speed * dt) % 360
            rad = math.radians(self._orbit_angle)
            offset = pygame.Vector2(math.cos(rad), math.sin(rad)) * radius
            self._orbit_anchor.y += fall_speed * dt
            pos = self._orbit_anchor + offset
            self.rect.centerx = int(pos.x)
            self.rect.centery = int(pos.y)
        elif self.type == "steel_falcon":
            # Glide with periodic dive bursts
            cycle = 120.0
            t_mod = self.timer % cycle
            horiz = math.sin(self.timer * 0.05 + self.phase) * 2.5
            self.rect.x += int(horiz)
            if t_mod < 36:
                self.rect.y += int(self.base_speed * 2.4 * dt)
                self._trail_timer += 1
                if self._trail_timer % 6 == 0:
                    HazardZone(
                        self.rect.center,
                        (self.radius * 2, self.radius * 2),
                        14,
                        self.bullet_color,
                        effect_data={"type": "impact", "damage": 26, "hit_cooldown": 8, "persistent": False},
                    )
            else:
                self.rect.y += int(self.base_speed * 0.7 * dt)
                self._trail_timer = 0
        elif self.type == "mire_sprayer":
            # Slow horizontal sweeps
            veer = float(self.behavior_params.get("veer", 0.5))
            self.rect.x += int(veer * math.sin(self.timer * 0.02))
            self.rect.y += int(self.base_speed * dt)
            self._trail_timer += 1
            if self._trail_timer % 12 == 0:
                HazardZone(
                    self.rect.center,
                    (self.radius * 2 + 8, self.radius * 2 + 8),
                    120,
                    (100, 170, 120),
                    effect_data={
                        "type": "poison",
                        "damage": 10,
                        "slow_mult": 0.7,
                        "slow_duration": 90,
                        "dot_damage": 3,
                        "dot_duration": 120,
                        "tick_cd": 18,
                        "hit_cooldown": 18,
                    },
                )
        elif self.type == "pulse_weaver":
            radius = float(self.behavior_params.get("radius", 90))
            angular_speed = float(self.behavior_params.get("angular_speed", 1.4))
            fall_speed = float(self.behavior_params.get("fall_speed", 0.8))
            self._orbit_angle = (self._orbit_angle + angular_speed * dt) % 360
            rad = math.radians(self._orbit_angle)
            offset = pygame.Vector2(math.cos(rad), math.sin(rad)) * radius
            self._orbit_anchor.y += fall_speed * dt
            pos = self._orbit_anchor + offset
            self.rect.centerx = int(pos.x)
            self.rect.centery = int(pos.y)
        elif self.type == "thorn_gaoler":
            # Direct pursuit drift with mild veer
            veer = float(self.behavior_params.get("veer", 0.2))
            self.rect.x += int(veer * math.sin(self.timer * 0.05))
            self.rect.y += int(self.base_speed * 1.1 * dt)
        elif self.type == "astra_fragger":
            sway = math.sin(self.timer * 0.03 + self.phase) * 3.5
            burst_cycle = 160.0
            cycle_time = self.timer % burst_cycle
            speed_mult = 1.7 if cycle_time < 36 else 0.85
            self.rect.x += int(sway * 4)
            self.rect.y += int(self.base_speed * speed_mult * dt)
        elif self.type == "ember_siege":
            veer = float(self.behavior_params.get("veer", 0.18))
            self.rect.x += int(math.sin(self.timer * 0.015) * veer * 60)
            self.rect.y += int(self.base_speed * 0.9 * dt)
        elif self.type == "ion_veil":
            radius = float(self.behavior_params.get("radius", 80))
            angular_speed = float(self.behavior_params.get("angular_speed", 0.8))
            fall_speed = float(self.behavior_params.get("fall_speed", 0.9))
            self._orbit_angle = (self._orbit_angle + angular_speed * dt) % 360
            rad = math.radians(self._orbit_angle)
            offset = pygame.Vector2(math.cos(rad), math.sin(rad)) * radius
            self._orbit_anchor.y += fall_speed * dt
            pos = self._orbit_anchor + offset
            self.rect.centerx = int(pos.x)
            self.rect.centery = int(pos.y)
        elif self.type == "resonance_breaker":
            amp = float(self.behavior_params.get("amplitude", 70))
            freq = float(self.behavior_params.get("frequency", 0.022))
            sway = math.sin(self.timer * freq + self.phase)
            self.rect.x += int(sway * amp * 0.05)
            self.rect.y += int(self.base_speed * (1.0 + 0.15 * math.sin(self.timer * 0.18)) * dt)
        elif self.type == "cryo_lancer":
            amp = float(self.behavior_params.get("amplitude", 60))
            freq = float(self.behavior_params.get("frequency", 0.02))
            self.rect.x += int(math.sin(self.timer * freq + self.phase) * amp * 0.04)
            bob = 1.0 + 0.2 * math.sin(self.timer * 0.12)
            self.rect.y += int(self.base_speed * bob * dt)
        elif self.type == "arc_overseer":
            veer = float(self.behavior_params.get("veer", 0.4))
            orbit = math.sin(self.timer * 0.025 + self.phase)
            self.rect.x += int(veer * orbit * 30)
            self.rect.y += int(self.base_speed * (1.0 + 0.1 * math.cos(self.timer * 0.08)) * dt)
        elif self.type == "lumen_shade":
            if self._stealth_timer > 0:
                self._stealth_timer -= dt
            else:
                self._stealthed = not self._stealthed
                if self._stealthed:
                    self._pending_relocate = True
                    self._stealth_timer = 60
                else:
                    self._stealth_timer = self._stealth_cooldown
            if self._pending_relocate and self._stealthed and not self.preview:
                self.rect.centerx = random.randint(80, WIDTH - 80)
                self._pending_relocate = False
            sway = math.sin(self.timer * 0.04 + self.phase) * (6 if not self._stealthed else 3)
            speed_mult = 0.5 if self._stealthed else 1.4
            self.rect.x += int(sway)
            self.rect.y += int(self.base_speed * speed_mult * dt)
        elif self.type in ("quantum_cleaver", "umbra_tormentor"):
            amp = float(self.behavior_params.get("amplitude", 120))
            freq = float(self.behavior_params.get("frequency", 0.02))
            sway = math.sin(self.timer * freq + self.phase) * amp * 0.05
            dash_cycle = 150.0
            phase = self.timer % dash_cycle
            speed_mult = 2.0 if phase < 24 else 1.0
            if phase < 6 and not self.preview:
                self.rect.centerx = random.randint(70, WIDTH - 70)
            self.rect.x += int(sway)
            self.rect.y += int(self.base_speed * speed_mult * dt)
        elif self.type in ("voidfold_mirror", "prismatic_overseer"):
            radius = float(self.behavior_params.get("radius", 150))
            angular_speed = float(self.behavior_params.get("angular_speed", 1.3))
            fall_speed = float(self.behavior_params.get("fall_speed", 0.9))
            self._orbit_angle = (self._orbit_angle + angular_speed * dt) % 360
            rad = math.radians(self._orbit_angle)
            offset = pygame.Vector2(math.cos(rad), math.sin(rad)) * radius
            self._orbit_anchor.y += fall_speed * dt
            pos = self._orbit_anchor + offset
            self.rect.centerx = int(pos.x)
            self.rect.centery = int(pos.y)
        elif self.type == "chrono_interdictor":
            veer = float(self.behavior_params.get("veer", 0.3))
            sway = math.sin(self.timer * 0.03 + self.phase) * veer * 40
            bob = 1.0 + 0.2 * math.sin(self.timer * 0.08)
            self.rect.x += int(sway)
            self.rect.y += int(self.base_speed * bob * dt)
        elif self.type == "rift_parasite":
            amp = float(self.behavior_params.get("amplitude", 100))
            freq = float(self.behavior_params.get("frequency", 0.018))
            drift = math.sin(self.timer * freq + self.phase) * amp * 0.04
            rush_cycle = self.timer % 140
            speed_mult = 1.8 if rush_cycle < 28 else 0.9
            self.rect.x += int(drift)
            self.rect.y += int(self.base_speed * speed_mult * dt)
            if rush_cycle < 6 and not self.preview:
                HazardZone(
                    (self.rect.centerx, self.rect.centery + self.radius + 20),
                    (self.radius * 2, self.radius),
                    40,
                    (110, 190, 140),
                    120,
                    effect_data={"type": "parasite", "damage": 0, "tick_cd": 30, "persistent": False},
                )
        elif self.type == "solar_arc_rider_prime":
            radius = float(self.behavior_params.get("radius", 140))
            ang_speed = float(self.behavior_params.get("angular_speed", 2.0))
            fall_speed = float(self.behavior_params.get("fall_speed", 1.1))
            self._orbit_angle = (self._orbit_angle + ang_speed * dt) % 360
            rad = math.radians(self._orbit_angle)
            offset = pygame.Vector2(math.cos(rad), math.sin(rad)) * radius
            self._orbit_anchor.y += fall_speed * dt
            pos = self._orbit_anchor + offset
            self.rect.centerx = int(pos.x)
            self.rect.centery = int(pos.y)
        else:
            # Default motions
            if self.behavior == "sine":
                amp = float(self.behavior_params.get("amplitude", 80))
                freq = float(self.behavior_params.get("frequency", 0.02))
                self.rect.x += int(math.sin(self.timer * freq + self.phase) * amp * 0.04)
                self.rect.y += int(self.base_speed * dt)
            elif self.behavior == "orbit":
                radius = float(self.behavior_params.get("radius", 110))
                angular_speed = float(self.behavior_params.get("angular_speed", 1.2))
                fall_speed = float(self.behavior_params.get("fall_speed", 1.2))
                self._orbit_angle = (self._orbit_angle + angular_speed * dt) % 360
                rad = math.radians(self._orbit_angle)
                offset = pygame.Vector2(math.cos(rad), math.sin(rad)) * radius
                self._orbit_anchor.y += fall_speed * dt
                pos = self._orbit_anchor + offset
                self.rect.centerx = int(pos.x)
                self.rect.centery = int(pos.y)
            else:  # drift / down
                veer = float(self.behavior_params.get("veer", 0.0))
                self.rect.x += int(veer * math.sin(self.timer * 0.03))
                self.rect.y += int(self.base_speed * dt)

        # Keep some on-screen bias
        if self.rect.left < -80:
            self.rect.left = -80
        if self.rect.right > WIDTH + 80:
            self.rect.right = WIDTH + 80

    def _apply_dynamic_effects(self) -> None:
        """Lightweight per-frame visual overlays for specific enemies."""
        # Start from the clean base image
        self.image = self.base_image.copy()

        # Selective dynamics: keep effects lightweight to save cost
        if self.type == "frost_webber":
            surf = self.image
            c = surf.get_width() // 2
            pulse = 0.5 + 0.5 * math.sin(self.timer * 0.12)
            fog_alpha = int(60 + 70 * pulse)
            ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            pygame.draw.circle(ring, (160, 220, 255, fog_alpha), (c, c), int(self.radius * 1.4), 2)
            for i in range(6):
                ang = math.radians(i * 60 + self.timer * 2)
                dot = (c + int(math.cos(ang) * (self.radius + 16)), c + int(math.sin(ang) * (self.radius + 16)))
                pygame.draw.circle(ring, (230, 250, 255, 110), dot, 2)
            surf.blit(ring, (0, 0))

        elif self.type == "storm_javelin":
            surf = self.image
            c = surf.get_width() // 2
            coil = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            glow = 90 + int(80 * (0.5 + 0.5 * math.sin(self.timer * 0.18)))
            for i in range(3):
                y = c - self.radius // 2 + i * (self.radius // 2)
                pygame.draw.ellipse(coil, (255, 210, 120, glow), (c - self.radius // 2, y - 4, self.radius, 10), 1)
            # crackling tips
            for side in (-1, 1):
                jitter = int(3 * math.sin(self.timer * 0.35 + side))
                pts = [(c + side * 6, c - self.radius - 10), (c + side * 10, c - self.radius + 2 + jitter), (c + side * 2, c - self.radius + 14)]
                pygame.draw.lines(coil, (255, 240, 180, 180), False, pts, 2)
            surf.blit(coil, (0, 0))

        elif self.type == "phantasmal_splitter":
            surf = self.image
            w, h = surf.get_size()
            ghost = pygame.Surface((w, h), pygame.SRCALPHA)
            phase = self.timer * 0.4
            for dx, col in [(-4, (80, 200, 255, 80)), (4, (255, 120, 160, 80))]:
                offset = int(3 * math.sin(phase + dx))
                ghost.blit(surf, (dx, offset))
                ghost.blit(surf, (-dx, -offset))
            surf.blit(ghost, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)

            noise = pygame.Surface((w, h), pygame.SRCALPHA)
            for _ in range(6):
                x = random.randint(w // 2 - self.radius, w // 2 + self.radius)
                y = random.randint(h // 2 - self.radius, h // 2 + self.radius)
                pygame.draw.rect(noise, (200, 180, 255, 140), (x, y, 2, 2))
            surf.blit(noise, (0, 0))

        elif self.type == "rail_shredder":
            surf = self.image
            w, h = surf.get_size()
            c = w // 2
            sparks = pygame.Surface((w, h), pygame.SRCALPHA)
            spin_ang = self.timer * 0.25
            for i in range(6):
                ang = spin_ang + i * (math.pi / 3)
                x = c + int(math.cos(ang) * (self.radius + 10))
                y = h // 2 + int(math.sin(ang) * (self.radius + 6))
                pygame.draw.line(sparks, (255, 210, 140, 180), (x, y), (x + int(math.cos(ang) * 6), y + int(math.sin(ang) * 6)), 2)
            surf.blit(sparks, (0, 0))

        elif self.type == "solar_arc_rider":
            surf = self.image
            w, h = surf.get_size()
            c = w // 2
            tail = pygame.Surface((w, h), pygame.SRCALPHA)
            pulse = 0.6 + 0.4 * math.sin(self.timer * 0.16)
            pygame.draw.arc(tail, (255, 200, 140, int(80 * pulse)), (c - self.radius, h // 2, self.radius * 2, self.radius), math.pi * 0.25, math.pi * 0.75, 4)
            pygame.draw.arc(tail, (120, 200, 255, int(60 * pulse)), (c - self.radius - 6, h // 2 + 2, self.radius * 2 + 12, self.radius + 6), math.pi * 0.2, math.pi * 0.8, 3)
            surf.blit(tail, (0, 0))
        elif self.type == "astra_fragger":
            surf = self.image
            overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            spin = self.timer * 0.2
            for i in range(4):
                ang = spin + i * (math.pi / 2)
                px = surf.get_width() // 2 + int(math.cos(ang) * (self.radius + 6))
                py = surf.get_height() // 2 + int(math.sin(ang) * (self.radius + 6))
                pygame.draw.circle(overlay, (255, 240, 150, 160), (px, py), 4)
            surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        elif self.type == "ember_siege":
            surf = self.image
            smoke = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            for i in range(3):
                radius = self.radius + 8 + i * 4
                alpha = 60 - i * 10
                pygame.draw.circle(smoke, (255, 120, 80, alpha), (surf.get_width() // 2, surf.get_height() // 2 + 6), radius, 2)
            surf.blit(smoke, (0, 0))
        elif self.type == "ion_veil":
            surf = self.image
            aura = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            glow = 0.5 + 0.5 * math.sin(self.timer * 0.1)
            pygame.draw.circle(
                aura,
                (120, 220, 255, int(80 + 80 * glow)),
                (surf.get_width() // 2, surf.get_height() // 2),
                self.radius + 12,
                2,
            )
            surf.blit(aura, (0, 0))
        elif self.type == "resonance_breaker":
            surf = self.image
            ripple = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            for offset in (-8, 0, 8):
                pygame.draw.arc(
                    ripple,
                    (200, 240, 255, 120),
                    (surf.get_width() // 2 - self.radius, surf.get_height() // 2 + offset, self.radius * 2, self.radius),
                    0,
                    math.pi,
                    2,
                )
            surf.blit(ripple, (0, 0))
        elif self.type == "cryo_lancer":
            surf = self.image
            frost = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            for i in range(4):
                ang = math.radians(self.timer * 3 + i * 90)
                px = surf.get_width() // 2 + int(math.cos(ang) * (self.radius + 4))
                py = surf.get_height() // 2 + int(math.sin(ang) * (self.radius + 4))
                pygame.draw.circle(frost, (200, 240, 255, 150), (px, py), 3)
            surf.blit(frost, (0, 0))
        elif self.type == "arc_overseer":
            surf = self.image
            arcs = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            center = (surf.get_width() // 2, surf.get_height() // 2)
            for i in range(3):
                ang = self.timer * 0.3 + i * 2
                end = (
                    center[0] + int(math.cos(ang) * (self.radius + 10)),
                    center[1] + int(math.sin(ang) * (self.radius + 10)),
                )
                pygame.draw.line(arcs, (150, 220, 255, 180), center, end, 2)
            surf.blit(arcs, (0, 0), special_flags=pygame.BLEND_ADD)
        elif self.type == "lumen_shade":
            surf = self.image
            if self._stealthed:
                dim = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
                dim.fill((30, 30, 60, 160))
                surf.blit(dim, (0, 0), special_flags=pygame.BLEND_MULT)

        elif self.type == "quantum_cleaver":
            surf = self.image
            w, h = surf.get_size()
            c = w // 2
            accent = (120, 240, 255)
            pulse = 0.6 + 0.4 * math.sin(self.timer * 0.18)
            glow = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*accent, int(70 * pulse)), (c, h // 2 - 4), self.radius + 10, 2)
            for i in range(6):
                ang = math.radians(i * 60 + self.timer * 2.2)
                px = c + int(math.cos(ang) * (self.radius + 16))
                py = h // 2 + int(math.sin(ang) * (self.radius + 14))
                pygame.draw.circle(glow, (*accent, int(90 * pulse)), (px, py), 2)
            surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)

        elif self.type == "umbra_tormentor":
            # 熵蚀织母：网状脉冲 + 孢丝漂浮
            surf = self.image
            w, h = surf.get_size()
            c = w // 2
            pulse = 0.5 + 0.5 * math.sin(self.timer * 0.14)
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            # 网环
            for k in range(3):
                rr = self.radius + 10 + k * 7
                alpha = max(0, min(255, int(60 * pulse) - k * 8))
                pygame.draw.circle(overlay, (170, 255, 210, alpha), (c, h // 2 + 10), rr, 1)
            # 漂浮孢丝
            for _ in range(6):
                x = random.randint(c - self.radius - 10, c + self.radius + 10)
                y = random.randint(h // 2 - self.radius, h // 2 + self.radius + 18)
                pygame.draw.line(overlay, (200, 255, 230, int(80 * pulse)), (x, y), (x + 3, y - 6), 1)
                pygame.draw.circle(overlay, (120, 220, 160, int(110 * pulse)), (x, y), 1)
            surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)

        elif self.type == "voidfold_mirror":
            surf = self.image
            w, h = surf.get_size()
            c = w // 2
            accent = (200, 200, 255)
            spin = self.timer * 0.22
            ring = pygame.Surface((w, h), pygame.SRCALPHA)
            for i in range(3):
                ang = spin + i * (math.pi / 3)
                x = c + int(math.cos(ang) * (self.radius + 10))
                y = h // 2 + int(math.sin(ang) * (self.radius + 8))
                pygame.draw.line(ring, (*accent, 140), (c, h // 2), (x, y), 2)
                pygame.draw.circle(ring, (255, 255, 255, 160), (x, y), 2)
            pygame.draw.circle(ring, (*accent, 70), (c, h // 2), self.radius + 14, 2)
            surf.blit(ring, (0, 0), special_flags=pygame.BLEND_ADD)

        elif self.type == "prismatic_overseer":
            # 轨道支援：伴飞节点环绕 + 目标校准圈
            surf = self.image
            w, h = surf.get_size()
            c = w // 2
            accent = (150, 220, 255)
            pulse = 0.55 + 0.45 * math.sin(self.timer * 0.16)
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.circle(overlay, (*accent, int(90 * pulse)), (c, h // 2), self.radius + 16, 2)
            pygame.draw.circle(overlay, (255, 230, 190, int(70 * pulse)), (c, h // 2), self.radius + 26, 1)
            spin = self.timer * 0.35
            for i in range(4):
                ang = spin + i * (math.pi / 2)
                px = c + int(math.cos(ang) * (self.radius + 20))
                py = h // 2 + int(math.sin(ang) * (self.radius + 16))
                pygame.draw.circle(overlay, (*accent, int(120 * pulse)), (px, py), 3)
                pygame.draw.line(overlay, (*accent, 110), (c, h // 2), (px, py), 1)
            surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)

        elif self.type == "chrono_interdictor":
            surf = self.image
            w, h = surf.get_size()
            c = w // 2
            accent = (150, 220, 255)
            t = self.timer
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            # rotating hands
            for speed, length, alpha, width in [(0.8, self.radius + 10, 150, 3), (1.6, self.radius + 4, 110, 2)]:
                ang = math.radians((t * speed * 30) % 360)
                x = c + int(math.cos(ang) * length)
                y = h // 2 + int(math.sin(ang) * length)
                pygame.draw.line(overlay, (*accent, alpha), (c, h // 2), (x, y), width)
            pygame.draw.circle(overlay, (255, 255, 255, 210), (c, h // 2), 3)
            # subtle scanline pulses
            scan = int((h // 2 + math.sin(t * 0.22) * (self.radius + 10)))
            pygame.draw.line(overlay, (200, 240, 255, 80), (c - self.radius - 16, scan), (c + self.radius + 16, scan), 2)
            surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)

        elif self.type == "rift_parasite":
            surf = self.image
            w, h = surf.get_size()
            c = w // 2
            pulse = 0.5 + 0.5 * math.sin(self.timer * 0.16)
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            # sac shimmer
            for i in range(6):
                px = c + (i - 2.5) * 10
                py = h // 2 + 10 + i * 3
                pygame.draw.circle(overlay, (200, 255, 220, int(70 * pulse)), (int(px), int(py)), 7, 2)
            # spore motes
            for _ in range(5):
                x = random.randint(c - self.radius, c + self.radius)
                y = random.randint(h // 2 - self.radius, h // 2 + self.radius)
                pygame.draw.circle(overlay, (160, 255, 180, int(90 * pulse)), (x, y), 1)
            surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)

        elif self.type == "solar_arc_rider_prime":
            surf = self.image
            w, h = surf.get_size()
            c = w // 2
            pulse = 0.55 + 0.45 * math.sin(self.timer * 0.18)
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.arc(
                overlay,
                (255, 240, 200, int(120 * pulse)),
                (c - self.radius - 10, h // 2 - self.radius, (self.radius + 10) * 2, (self.radius + 18)),
                math.pi * 0.2,
                math.pi * 0.8,
                6,
            )
            pygame.draw.arc(
                overlay,
                (120, 200, 255, int(70 * pulse)),
                (c - self.radius - 18, h // 2 - self.radius + 2, (self.radius + 18) * 2, (self.radius + 24)),
                math.pi * 0.2,
                math.pi * 0.8,
                3,
            )
            pygame.draw.circle(overlay, (255, 255, 255, int(90 * pulse)), (c + 10, h // 2 - 8), 6)
            surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)

        # Elite signature should be on top of all other dynamics
        if getattr(self, "is_elite", False):
            self._apply_elite_signature(self.image)

    def _apply_support_auras(self) -> None:
        if self.preview:
            return
        if self.type == "ion_veil":
            self._support_timer += 1
            if self._support_timer % 18 != 0:
                return
            boost_radius = 200
            for ally in mobs:
                if ally is self or getattr(ally, "hp", 1) <= 0:
                    continue
                dist = math.hypot(ally.rect.centerx - self.rect.centerx, ally.rect.centery - self.rect.centery)
                if dist <= boost_radius:
                    ally.ally_shield_timer = max(getattr(ally, "ally_shield_timer", 0.0), 45.0)
                    ally.ally_shield_strength = max(getattr(ally, "ally_shield_strength", 0.0), 0.25)

    # ------------------------------------------------------------------
    # Attacks
    def _maybe_attack(self) -> None:
        if self.attack_timer < self.attack_interval:
            return

        # Custom fire patterns for new enemies
        if self.type == "void_hunter":
            self.attack_timer = 0.0
            speeds = self.attack_params.get("bullet_speed", 6.2)
            # Twin blade arcs + center shot
            for ang in (82, 90, 98, 60, 120):
                EnemyProjectile(self.rect.center, ang, speeds, self.bullet_color)
        elif self.type == "armored_centurion":
            self.attack_timer = 0.0
            # Short mortar fan
            for ang in (80, 88, 92, 96, 100):
                EnemyProjectile(self.rect.center, ang, 4.6, self.bullet_color)
            # Chain bombs (drop slightly offset)
            left = (self.rect.centerx - 18, self.rect.centery + 6)
            right = (self.rect.centerx + 18, self.rect.centery + 6)
            for pos in (left, right):
                EnemyProjectile(pos, 90, 4.0, self.bullet_color)
        elif self.type == "plague_drone":
            self.attack_timer = 0.0
            # Poison ring
            for i in range(8):
                EnemyProjectile(self.rect.center, i * 45, 3.8, self.bullet_color)
            # Stinger burst
            for ang in (85, 90, 95):
                EnemyProjectile(self.rect.center, ang, 6.0, self.bullet_color)
        elif self.type == "prism_watcher":
            self.attack_timer = 0.0
            self._alt_fire = not self._alt_fire
            if self._alt_fire:
                # Stop-and-burst prism beams
                for i in range(6):
                    EnemyProjectile(self.rect.center, i * 60, 5.6, self.bullet_color)
            else:
                for ang in (88, 90, 92):
                    EnemyProjectile(self.rect.center, ang, 7.0, self.bullet_color)
        elif self.type == "skeletal_interceptor":
            self.attack_timer = 0.0
            # Forward fangs
            for ang in (84, 90, 96):
                EnemyProjectile(self.rect.center, ang, 6.2, self.bullet_color)
            # Ghostfire arc
            for i in range(6):
                EnemyProjectile(self.rect.center, 60 + i * 15, 4.2, self.bullet_color)
        elif self.type == "frost_webber":
            self.attack_timer = 0.0
            # Ice web ring (slow) + triple icicle
            for i in range(10):
                EnemyProjectile(self.rect.center, i * 36, 3.5, self.bullet_color)
            for ang in (84, 90, 96):
                EnemyProjectile(self.rect.center, ang, 5.6, self.bullet_color)
        elif self.type == "storm_javelin":
            self.attack_timer = 0.0
            # Central spear + side shocks
            EnemyProjectile(self.rect.center, 90, 7.4, self.bullet_color)
            for ang in (70, 110):
                EnemyProjectile(self.rect.center, ang, 6.2, self.bullet_color)
            # Small lightning fan
            for ang in (60, 75, 105, 120):
                EnemyProjectile(self.rect.center, ang, 4.8, self.bullet_color)
        elif self.type == "phantasmal_splitter":
            self.attack_timer = 0.0
            # Slow tracking-like spread (simulate with dense angles)
            for ang in (70, 80, 90, 100, 110):
                EnemyProjectile(self.rect.center, ang, 4.2, self.bullet_color)
            # Cross beams
            for ang in (45, 135):
                EnemyProjectile(self.rect.center, ang, 5.0, self.bullet_color)
        elif self.type == "rail_shredder":
            self.attack_timer = 0.0
            # Dual rail shots (fast)
            for ang in (86, 90, 94):
                EnemyProjectile(self.rect.center, ang, 7.2, self.bullet_color)
            # Fragment arc
            for i in range(8):
                EnemyProjectile(self.rect.center, 50 + i * 10, 4.6, self.bullet_color)
        elif self.type == "steel_falcon":
            self.attack_timer = 0.0
            # Feather rang after dive
            angles = self.attack_params.get("angles", [80, 90, 100])
            speed = float(self.attack_params.get("bullet_speed", 6.4))
            for ang in angles:
                EnemyProjectile(self.rect.center, ang, speed, self.bullet_color)
        elif self.type == "mire_sprayer":
            self.attack_timer = 0.0
            # Wide spray low-speed wall
            angles = self.attack_params.get("angles", [60, 90, 120])
            speed = float(self.attack_params.get("bullet_speed", 3.6))
            for ang in angles:
                EnemyProjectile(self.rect.center, ang, speed, self.bullet_color)
            # Drip tail downward
            EnemyProjectile(self.rect.center, 90, 2.2, self.bullet_color)
            # Lingering toxic puddle at current position
            HazardZone(
                self.rect.center,
                (self.radius * 2 + 14, self.radius * 2 + 14),
                140,
                (100, 170, 120),
                150,
                effect_data={
                    "type": "poison",
                    "damage": 12,
                    "slow_mult": 0.65,
                    "slow_duration": 110,
                    "dot_damage": 4,
                    "dot_duration": 150,
                    "tick_cd": 16,
                    "hit_cooldown": 16,
                },
            )
        elif self.type == "pulse_weaver":
            self.attack_timer = 0.0
            # Persistent cross walls
            span = 240
            thickness = 14
            HazardZone(
                self.rect.center,
                (span, thickness),
                160,
                self.bullet_color,
                110,
                effect_data={"type": "wall", "damage": 18, "hit_cooldown": 14},
            )
            HazardZone(
                self.rect.center,
                (thickness, span),
                160,
                self.bullet_color,
                110,
                effect_data={"type": "wall", "damage": 18, "hit_cooldown": 14},
            )
            # Soft 8-way burst to telegraph
            angles = self.attack_params.get("angles", [0, 45, 90, 135, 180, 225, 270, 315])
            speed = float(self.attack_params.get("bullet_speed", 4.0))
            for ang in angles:
                EnemyProjectile(self.rect.center, ang, speed, self.bullet_color)
        elif self.type == "thorn_gaoler":
            self.attack_timer = 0.0
            # Fast hook forward + slight spread
            EnemyProjectile(self.rect.center, 90, float(self.attack_params.get("bullet_speed", 7.5)), self.bullet_color)
            # Chain hazard in front to simulate drag/bind
            chain_len = 140
            HazardZone(
                (self.rect.centerx, self.rect.centery + chain_len // 2),
                (18, chain_len),
                40,
                (80, 140, 90),
                160,
                effect_data={
                    "type": "grab",
                    "damage": 12,
                    "grab_duration": 60,
                    "grab_pull": 3.5,
                    "hit_cooldown": 20,
                },
            )
            for ang in (82, 98):
                EnemyProjectile(self.rect.center, ang, 6.2, self.bullet_color)
        elif self.type == "solar_arc_rider":
            self.attack_timer = 0.0
            self._alt_fire = not self._alt_fire
            if self._alt_fire:
                # Wide heat arc
                for ang in range(60, 121, 10):
                    EnemyProjectile(self.rect.center, ang, 5.4, self.bullet_color)
            else:
                # Piercing beam trio
                for ang in (88, 90, 92):
                    EnemyProjectile(self.rect.center, ang, 7.0, self.bullet_color)
        elif self.type == "astra_fragger":
            self.attack_timer = 0.0
            clusters = int(self.attack_params.get("clusters", 3))
            spread = max(1, clusters - 1)
            for i in range(clusters):
                lerp = i / spread if spread else 0.5
                ang = 80 + lerp * 20
                proj = EnemyProjectile(self.rect.center, ang, 4.4, self.bullet_color)
                proj.effect_data = {"type": "impact", "damage": 24}
            shard_count = int(self.attack_params.get("shrapnel", 6))
            for _ in range(shard_count):
                offset_x = random.randint(-90, 90)
                offset_y = random.randint(120, 220)
                HazardZone(
                    (self.rect.centerx + offset_x, self.rect.centery + offset_y),
                    (40, 40),
                    50,
                    self.bullet_color,
                    150,
                    effect_data={"type": "shrapnel", "damage": 18, "hit_cooldown": 4, "persistent": False},
                )
        elif self.type == "ember_siege":
            self.attack_timer = 0.0
            pools = int(self.attack_params.get("pools", 2))
            for _ in range(pools):
                offset_x = random.randint(-110, 110)
                drop_center = (
                    self.rect.centerx + offset_x,
                    self.rect.centery + random.randint(150, 240),
                )
                HazardZone(
                    drop_center,
                    (96, 36),
                    220,
                    (255, 150, 90),
                    150,
                    effect_data={
                        "type": "burn",
                        "damage": 20,
                        "dot_damage": 5,
                        "dot_duration": 180,
                        "tick_cd": 18,
                        "slow_mult": 0.8,
                        "slow_duration": 90,
                        "hit_cooldown": 14,
                    },
                )
            EnemyProjectile(self.rect.center, 90, 3.2, self.bullet_color)
        elif self.type == "ion_veil":
            self.attack_timer = 0.0
            nodes = int(self.attack_params.get("nodes", 3))
            radius = self.radius + 40
            for i in range(nodes):
                ang = math.radians((self.timer * 2 + i * (360 / nodes)) % 360)
                pos = (
                    self.rect.centerx + int(math.cos(ang) * radius),
                    self.rect.centery + int(math.sin(ang) * radius),
                )
                HazardZone(
                    pos,
                    (60, 60),
                    80,
                    self.bullet_color,
                    130,
                    effect_data={"type": "shield", "damage": 14, "hit_cooldown": 10},
                )
        elif self.type == "resonance_breaker":
            self.attack_timer = 0.0
            width = int(self.attack_params.get("beam_width", 26))
            length = int(self.attack_params.get("beam_length", 320))
            HazardZone(
                (self.rect.centerx, self.rect.centery + length // 2),
                (width, length),
                52,
                self.bullet_color,
                150,
                effect_data={
                    "type": "sonic",
                    "damage": 24,
                    "slow_mult": 0.6,
                    "slow_duration": 80,
                    "armor_break": 90,
                    "silence_duration": 60,
                },
            )
        elif self.type == "cryo_lancer":
            self.attack_timer = 0.0
            for ang in (84, 90, 96):
                projectile = EnemyProjectile(self.rect.center, ang, 5.4, self.bullet_color)
                projectile.effect_data = {"type": "freeze", "freeze_duration": 90, "damage": 22}
            wall_len = int(self.attack_params.get("wall_length", 200))
            HazardZone(
                (self.rect.centerx, self.rect.centery + wall_len // 2),
                (18, wall_len),
                130,
                (170, 220, 255),
                150,
                effect_data={
                    "type": "freeze",
                    "damage": 12,
                    "freeze_duration": 60,
                    "slow_mult": 0.5,
                    "slow_duration": 120,
                },
            )
        elif self.type == "arc_overseer":
            self.attack_timer = 0.0
            orb = EnemyProjectile(self.rect.center, 90, 5.2, self.bullet_color)
            orb.effect_data = {
                "type": "chain",
                "damage": 22,
                "player_damage": 18,
                "minion_damage": 20,
                "jumps": int(self.attack_params.get("jumps", 3)),
            }
            for ang in (70, 110):
                bolt = EnemyProjectile(self.rect.center, ang, 6.4, self.bullet_color)
                bolt.effect_data = {"type": "chain", "damage": 16, "player_damage": 12, "minion_damage": 16, "jumps": 1}
        elif self.type == "lumen_shade":
            self.attack_timer = 0.0
            if self._stealthed:
                self._stealthed = False
                self._stealth_timer = self._stealth_cooldown
            daggers = int(self.attack_params.get("daggers", 6))
            spread = max(1, daggers - 1)
            for i in range(daggers):
                lerp = i / spread if spread else 0.5
                angle = 60 + lerp * 60
                blade = EnemyProjectile(self.rect.center, angle, 7.2, self.bullet_color)
                blade.effect_data = {"type": "impact", "damage": 20}
            HazardZone(
                self.rect.center,
                (80, 80),
                40,
                (200, 200, 255),
                120,
                effect_data={"type": "impact", "damage": 18, "hit_cooldown": 8},
            )
        elif self.type == "quantum_cleaver":
            self.attack_timer = 0.0
            params = self.attack_params
            angles = params.get("slash_angles", [60, 72, 84, 96, 108, 120])
            speed = float(params.get("slash_speed", 7.2))
            slash_damage = int(params.get("slash_damage", 28))
            armor_break = int(params.get("armor_break", 150))
            for ang in angles:
                blade = EnemyProjectile(self.rect.center, ang, speed, self.bullet_color)
                blade.effect_data = {
                    "type": "sonic",
                    "damage": slash_damage,
                    "armor_break": armor_break,
                    "slow_mult": 0.72,
                    "slow_duration": 90,
                    "silence_duration": 50,
                }
            HazardZone(
                self.rect.center,
                (self.radius * 3, self.radius * 3),
                36,
                (120, 210, 255),
                150,
                effect_data={
                    "type": "whiteout",
                    "damage": slash_damage // 2,
                    "whiteout_duration": 110,
                    "whiteout_intensity": 0.7,
                    "slow_mult": 0.85,
                    "slow_duration": 70,
                    "hit_cooldown": 6,
                },
            )
        elif self.type == "umbra_tormentor":
            self.attack_timer = 0.0
            params = self.attack_params
            angles = params.get("slash_angles", [70, 80, 90, 100, 110])
            speed = float(params.get("slash_speed", 7.6))
            slash_damage = int(params.get("slash_damage", 26))
            armor_break = int(params.get("armor_break", 130))
            for ang in angles:
                blade = EnemyProjectile(self.rect.center, ang + random.uniform(-1.5, 1.5), speed, self.bullet_color)
                blade.effect_data = {
                    "type": "sonic",
                    "damage": slash_damage,
                    "armor_break": armor_break,
                    "slow_mult": 0.78,
                    "slow_duration": 80,
                }
            HazardZone(
                (self.rect.centerx, self.rect.centery + self.radius + 10),
                (self.radius * 3, self.radius * 2),
                48,
                (255, 110, 180),
                160,
                effect_data={
                    "type": "grab",
                    "damage": max(12, slash_damage // 2),
                    "grab_duration": 50,
                    "grab_pull": 3.2,
                    "hit_cooldown": 14,
                },
            )
        elif self.type == "voidfold_mirror":
            self.attack_timer = 0.0
            params = self.attack_params
            radius = int(params.get("whiteout_radius", 150))
            duration = int(params.get("whiteout_duration", 150))
            intensity = float(params.get("whiteout_intensity", 0.85))
            damage = int(params.get("damage", 26))
            beam_count = max(1, int(params.get("beam_count", 5)))
            HazardZone(
                self.rect.center,
                (radius * 2, radius * 2),
                120,
                (150, 150, 220),
                140,
                effect_data={
                    "type": "whiteout",
                    "damage": damage,
                    "whiteout_duration": duration,
                    "whiteout_intensity": intensity,
                    "slow_mult": 0.8,
                    "slow_duration": 90,
                    "hit_cooldown": 8,
                },
            )
            mirror_duration = int(params.get("mirror_duration", 180))
            mirror_tick_cd = max(8, int(params.get("mirror_tick_cd", 18)))
            feedback = int(params.get("mirror_feedback_damage", params.get("mirror_tick_damage", max(8, damage // 2))))
            HazardZone(
                self.rect.center,
                (radius * 2 - 40, radius * 2 - 40),
                160,
                (180, 210, 240),
                140,
                effect_data={
                    "type": "mirror",
                    "damage": max(6, damage // 2),
                    "mirror_duration": mirror_duration,
                    "feedback_damage": feedback,
                    "tick_cd": mirror_tick_cd,
                    "hit_cooldown": mirror_tick_cd,
                },
            )
            spread = 100
            start = 90 - spread // 2
            step = spread / beam_count if beam_count > 1 else 0
            for i in range(beam_count):
                ang = start + i * step + random.uniform(-3, 3)
                beam = EnemyProjectile(self.rect.center, ang, 5.0, self.bullet_color)
                beam.effect_data = {
                    "type": "whiteout",
                    "damage": damage,
                    "whiteout_duration": duration,
                    "whiteout_intensity": intensity,
                    "slow_mult": 0.82,
                    "slow_duration": 80,
                }
        elif self.type == "prismatic_overseer":
            self.attack_timer = 0.0
            params = self.attack_params
            radius = int(params.get("whiteout_radius", 170))
            duration = int(params.get("whiteout_duration", 170))
            intensity = float(params.get("whiteout_intensity", 0.95))
            damage = int(params.get("damage", 24))
            beam_count = max(1, int(params.get("beam_count", 7)))
            HazardZone(
                self.rect.center,
                (radius * 2, radius * 2),
                140,
                (240, 240, 255),
                150,
                effect_data={
                    "type": "whiteout",
                    "damage": damage,
                    "whiteout_duration": duration,
                    "whiteout_intensity": intensity,
                    "slow_mult": 0.75,
                    "slow_duration": 110,
                    "hit_cooldown": 8,
                },
            )
            lock_duration = int(params.get("phase_duration", params.get("mirror_duration", 120)))
            displacement = float(params.get("phase_displacement", params.get("phase_lock_displacement", 28.0)))
            pulse_cd = max(8, int(params.get("phase_pulse_cd", params.get("mirror_tick_cd", 18))))
            node_count = max(2, int(params.get("bit_wall_count", 2)))
            anchors: list[tuple[int, int]] = []
            for i in range(node_count):
                t = (i / max(1, node_count - 1)) - 0.5
                anchors.append((self.rect.centerx + int(t * radius), self.rect.centery + radius // 2))
            for anchor in anchors:
                HazardZone(
                    anchor,
                    (70, 70),
                    140,
                    (160, 210, 255),
                    130,
                    effect_data={
                        "type": "phase_lock",
                        "damage": max(6, int(params.get("mirror_tick_damage", damage // 2))),
                        "duration": lock_duration,
                        "displacement": displacement,
                        "pulse_cd": pulse_cd,
                        "anchor": anchor,
                        "invert": False,
                        "hit_cooldown": pulse_cd,
                    },
                )
            spread = 130
            start = 90 - spread // 2
            step = spread / beam_count if beam_count > 1 else 0
            for i in range(beam_count):
                ang = start + i * step
                beam = EnemyProjectile(self.rect.center, ang, 5.4, self.bullet_color)
                beam.effect_data = {
                    "type": "whiteout",
                    "damage": damage,
                    "whiteout_duration": duration,
                    "whiteout_intensity": min(1.0, intensity + 0.05),
                    "slow_mult": 0.78,
                    "slow_duration": 100,
                }
        elif self.type == "chrono_interdictor":
            self.attack_timer = 0.0
            params = self.attack_params
            radius = int(params.get("shock_radius", 150))
            time_slow = float(params.get("time_slow", 0.6))
            freeze_duration = int(params.get("freeze_duration", 80))
            damage = int(params.get("damage", 24))
            HazardZone(
                self.rect.center,
                (radius * 2, radius * 2),
                90,
                (150, 220, 255),
                150,
                effect_data={
                    "type": "freeze",
                    "damage": damage,
                    "freeze_duration": freeze_duration,
                    "slow_mult": time_slow,
                    "slow_duration": freeze_duration + 40,
                    "hit_cooldown": 10,
                },
            )
            HazardZone(
                self.rect.center,
                (radius * 2 - 40, radius * 2 - 40),
                140,
                (120, 200, 255),
                150,
                effect_data={
                    "type": "freeze",
                    "visual_type": "timeslip",
                    "damage": max(8, damage // 2),
                    "freeze_duration": max(30, freeze_duration // 2),
                    "slow_mult": min(0.7, time_slow + 0.1),
                    "slow_duration": freeze_duration,
                    "hit_cooldown": 10,
                },
            )
            for offset in (-40, 0, 40):
                orb = EnemyProjectile((self.rect.centerx + offset, self.rect.centery), 90, 3.6, self.bullet_color)
                orb.effect_data = {
                    "type": "freeze",
                    "damage": max(12, damage // 2),
                    "freeze_duration": freeze_duration // 2,
                    "slow_mult": min(0.85, time_slow + 0.15),
                    "slow_duration": freeze_duration,
                }
        elif self.type == "rift_parasite":
            self.attack_timer = 0.0
            params = self.attack_params
            angles = params.get("pod_angles", [70, 85, 100])
            tick_damage = int(params.get("tick_damage", 5))
            duration = int(params.get("duration", 240))
            damage = int(params.get("damage", 18))
            for ang in angles:
                pod = EnemyProjectile(self.rect.center, ang + random.uniform(-2, 2), 4.2, self.bullet_color)
                pod.effect_data = {
                    "type": "parasite",
                    "damage": damage,
                    "duration": duration,
                    "tick_damage": tick_damage,
                    "tick_cd": 26,
                }
            HazardZone(
                self.rect.center,
                (self.radius * 2 + 40, self.radius * 2 + 40),
                140,
                (110, 190, 140),
                140,
                effect_data={
                    "type": "parasite",
                    "damage": max(8, damage // 2),
                    "duration": duration,
                    "tick_damage": tick_damage,
                    "tick_cd": 24,
                    "hit_cooldown": 18,
                },
            )
            root_duration = int(params.get("root_duration", params.get("spore_root_duration", 200)))
            root_tick = max(8, int(params.get("root_tick_cd", params.get("spore_root_tick_cd", 22))))
            root_damage = int(params.get("root_damage", params.get("spore_root_damage", tick_damage + 2)))
            HazardZone(
                (self.rect.centerx, self.rect.centery + self.radius + 20),
                (self.radius * 2 + 80, self.radius * 2 + 80),
                160,
                (130, 210, 150),
                150,
                effect_data={
                    "type": "spore_root",
                    "damage": max(4, damage // 3),
                    "duration": root_duration,
                    "tick_damage": root_damage,
                    "tick_cd": root_tick,
                    "slow_mult": params.get("root_slow", params.get("spore_root_slow_mult", 0.75)),
                    "hit_cooldown": root_tick,
                },
            )
        elif self.type == "solar_arc_rider_prime":
            self.attack_timer = 0.0
            params = self.attack_params
            arc_count = max(1, int(params.get("arc_count", 2)))
            damage = int(params.get("damage", 26))
            radius = int(params.get("whiteout_radius", 120))
            for arc in range(arc_count):
                offset = arc * 4
                for ang in range(60 - offset, 121 + offset, 10):
                    proj = EnemyProjectile(self.rect.center, ang, 5.6 + arc * 0.3, self.bullet_color)
                    proj.effect_data = {
                        "type": "whiteout",
                        "damage": damage,
                        "whiteout_duration": 110 + arc * 10,
                        "whiteout_intensity": 0.7 + arc * 0.1,
                        "slow_mult": 0.85,
                        "slow_duration": 80,
                    }
            HazardZone(
                self.rect.center,
                (radius * 2, radius * 2),
                100,
                (255, 210, 150),
                150,
                effect_data={
                    "type": "whiteout",
                    "damage": damage,
                    "whiteout_duration": 140,
                    "whiteout_intensity": 0.8,
                    "hit_cooldown": 8,
                },
            )
            burn_duration = int(params.get("burn_duration", params.get("solar_burn_duration", 180)))
            burn_tick = max(4, int(params.get("burn_tick_cd", params.get("solar_burn_tick_cd", 12))))
            burn_damage = int(params.get("burn_tick_damage", params.get("solar_burn_damage", damage // 3)))
            firewall_segments = max(2, int(params.get("firewall_segments", 2)))
            firewall_width = int(params.get("firewall_width", 160))
            offsets = []
            for i in range(firewall_segments):
                t = (i / max(1, firewall_segments - 1)) - 0.5
                offsets.append(int(t * firewall_width))
            for offset in offsets:
                HazardZone(
                    (self.rect.centerx + offset, HEIGHT // 2),
                    (48, HEIGHT),
                    160,
                    (255, 180, 120),
                    150,
                    effect_data={
                        "type": "solar_burn",
                        "damage": max(6, damage // 2),
                        "duration": burn_duration,
                        "tick_damage": burn_damage,
                        "tick_cd": burn_tick,
                        "hit_cooldown": burn_tick,
                    },
                )
        else:
            if not self.attack_pattern:
                return
            if self.attack_timer < self.attack_interval:
                return
            self.attack_timer = 0.0

            if self.attack_pattern == "single":
                angles = self.attack_params.get("angles", [90])
                speed = float(self.attack_params.get("bullet_speed", 6.0))
                for ang in angles:
                    EnemyProjectile(self.rect.center, ang, speed, self.bullet_color)
            elif self.attack_pattern == "spread":
                angles = self.attack_params.get("angles", [75, 90, 105])
                speed = float(self.attack_params.get("bullet_speed", 5.0))
                for ang in angles:
                    EnemyProjectile(self.rect.center, ang, speed, self.bullet_color)
            elif self.attack_pattern == "burst_circle":
                count = int(self.attack_params.get("count", 8))
                speed = float(self.attack_params.get("bullet_speed", 4.2))
                for i in range(count):
                    EnemyProjectile(self.rect.center, i * (360 / count), speed, self.bullet_color)


    # ------------------------------------------------------------------
    # Damage entry point (compat)
    def take_damage(self, damage: float) -> bool:
        self.hp -= damage
        return self.hp > 0

    def kill(self) -> None:
        if not getattr(self, "_death_effect_done", False) and not self.preview and getattr(self, "hp", 1) <= 0:
            self._trigger_death_effect()
            self._death_effect_done = True
        super().kill()

    def _trigger_death_effect(self) -> None:
        if self.type == "ember_siege":
            HazardZone(
                self.rect.center,
                (140, 48),
                240,
                (255, 150, 90),
                150,
                effect_data={
                    "type": "burn",
                    "damage": 24,
                    "dot_damage": 6,
                    "dot_duration": 200,
                    "tick_cd": 16,
                    "slow_mult": 0.75,
                    "slow_duration": 120,
                    "hit_cooldown": 14,
                },
            )
        elif self.type == "ion_veil":
            HazardZone(
                self.rect.center,
                (220, 220),
                90,
                (120, 220, 255),
                120,
                effect_data={"type": "emp", "damage": 0, "emp_duration": 120, "drain_energy": 40},
            )
        elif self.type == "lumen_shade":
            HazardZone(
                self.rect.center,
                (90, 90),
                60,
                (200, 200, 255),
                140,
                effect_data={"type": "impact", "damage": 20, "hit_cooldown": 6},
            )


# ---------------------------------------------------------------------------
# Helpers for previews
# ---------------------------------------------------------------------------
def _load_enemy_data() -> Dict[str, Dict[str, Any]]:
    """Load enemy configs once for gameplay and previews."""
    global _ENEMY_DATA_CACHE
    if _ENEMY_DATA_CACHE is not None:
        return _ENEMY_DATA_CACHE

    try:
        with open("data/enemies/enemy_types.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        _ENEMY_DATA_CACHE = data.get("enemies", BUILTIN_ENEMIES)
    except Exception:
        _ENEMY_DATA_CACHE = BUILTIN_ENEMIES
    return _ENEMY_DATA_CACHE


# 预览图缓存 - 避免每帧重新创建Enemy对象
_PREVIEW_SURFACE_CACHE: Dict[Tuple[str, int, Optional[Tuple[int, int, int]]], pygame.Surface] = {}


def build_enemy_preview_surface(
    enemy_id: str,
    t: float = 0.0,
    box: int = 150,
    color_override: Optional[Tuple[int, int, int]] = None,
    supersample: float = 2.0,
) -> pygame.Surface:
    """Render a high-fidelity enemy preview using real visuals/dynamics (with caching)."""
    # 使用缓存键（不包含t，因为静态预览足够）
    cache_key = (enemy_id, box, color_override)
    if cache_key in _PREVIEW_SURFACE_CACHE:
        return _PREVIEW_SURFACE_CACHE[cache_key]
    
    data = _load_enemy_data()
    config = data.get(enemy_id) or BUILTIN_ENEMIES.get(enemy_id)
    if not config:
        return pygame.Surface((box, box), pygame.SRCALPHA)

    cfg = dict(config)
    if color_override:
        cfg["color"] = list(color_override)

    render_scale = max(1.0, min(3.0, supersample))
    enemy = Enemy(enemy_id, cfg, spawn_pos=(box // 2, box // 2), preview=True, render_scale=render_scale)
    enemy.timer = t
    enemy._apply_dynamic_effects()
    src = enemy.image
    iw, ih = src.get_size()
    target = max(16, box - 12)
    scale = min(target / max(iw, ih), 2.5)
    scale = max(scale, 0.5)

    if abs(scale - 1.0) > 0.01:
        sw, sh = max(1, int(iw * scale)), max(1, int(ih * scale))
        src = pygame.transform.smoothscale(src, (sw, sh))

    surf = pygame.Surface((box, box), pygame.SRCALPHA)
    rect = src.get_rect(center=(box // 2, box // 2))
    surf.blit(src, rect)
    
    # 缓存结果
    _PREVIEW_SURFACE_CACHE[cache_key] = surf
    return surf


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------
class EnemyFactory:
    def __init__(self) -> None:
        self.enemy_configs: Dict[str, Dict[str, Any]] = {}
        # Preload defaults so the game stays playable even without JSON
        self.load_from_dict(BUILTIN_ENEMIES)

    def load_from_dict(self, configs: Dict[str, Dict[str, Any]]) -> None:
        self.enemy_configs.update(configs)

    def load_from_json(self, json_path: str) -> bool:
        import json

        try:
            with open(json_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if "enemies" in data:
                self.enemy_configs.clear()
                self.load_from_dict(data["enemies"])
                return True
        except Exception as exc:  # noqa: BLE001 (surface error)
            print(f"[enemy_factory] failed to load {json_path}: {exc}")
        return False

    def create_enemy(
        self,
        type_id: str,
        spawn_pos: Optional[Tuple[int, int]] = None,
        override_config: Optional[Dict[str, Any]] = None,
    ) -> Optional[Enemy]:
        config = self.enemy_configs.get(type_id)
        if not config:
            return None
        merged = dict(config)
        if override_config:
            merged.update(override_config)
        return Enemy(type_id, merged, spawn_pos)

    def get_all_types(self) -> Dict[str, Dict[str, Any]]:
        return dict(self.enemy_configs)


enemy_factory = EnemyFactory()


def init_enemy_system() -> None:
    """Placeholder for compatibility with existing imports."""
    return None
