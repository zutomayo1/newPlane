"""
资产管理系统 - 统一管理游戏资源

功能：
- 懒加载：按需加载资源
- 缓存：避免重复加载
- 热重载：开发模式支持实时更新
- 回退：缺失资源使用程序化生成替代

使用方式：
    from utils.asset_manager import asset_manager
    
    # 获取精灵
    sprite = asset_manager.get_sprite("sprites/planes/striker/default.png")
    
    # 获取配置数据
    plane_config = asset_manager.get_plane_config("striker")
    
    # 获取颜色
    color = asset_manager.get_color("primary_cyan")
"""
import os
import json
import pygame
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

from utils.core import log_error, log_info


class AssetManager:
    """
    单例资产管理器
    
    管理所有游戏资源的加载、缓存和访问
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # 路径配置
        self.base_path = Path(__file__).parent.parent
        self.assets_path = self.base_path / "assets"
        self.data_path = self.base_path / "data"
        
        # 缓存
        self._sprite_cache: Dict[str, pygame.Surface] = {}
        self._sound_cache: Dict[str, pygame.mixer.Sound] = {}
        self._data_cache: Dict[str, dict] = {}
        self._font_cache: Dict[tuple, pygame.font.Font] = {}
        
        # 颜色配置
        self.colors: Dict[str, Tuple[int, int, int]] = {}
        
        # 配置
        self.dev_mode = os.environ.get("DEV_MODE", "0") == "1"
        
        # 初始化
        self._ensure_directories()
        self._load_color_palette()
        
        log_info("AssetManager initialized")
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.assets_path / "sprites" / "planes",
            self.assets_path / "sprites" / "bullets",
            self.assets_path / "sprites" / "enemies",
            self.assets_path / "sprites" / "effects",
            self.assets_path / "sprites" / "ui",
            self.assets_path / "audio" / "sfx",
            self.assets_path / "audio" / "bgm",
            self.assets_path / "fonts",
            self.data_path / "planes",
            self.data_path / "skins",
            self.data_path / "ui",
            self.data_path / "enemies",
        ]
        for dir_path in directories:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    # ==================== 精灵加载 ====================
    
    def get_sprite(self, path: str, scale: float = 1.0) -> Optional[pygame.Surface]:
        """
        获取精灵图像
        
        Args:
            path: 相对于assets目录的路径
            scale: 缩放比例
        
        Returns:
            pygame.Surface 或 None（如果不存在）
        """
        cache_key = f"{path}@{scale}"
        
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]
        
        full_path = self.assets_path / path
        
        if not full_path.exists():
            return None  # 返回None让调用者决定如何回退
        
        try:
            surface = pygame.image.load(str(full_path))
            if pygame.display.get_surface():
                surface = surface.convert_alpha()
            
            if scale != 1.0:
                new_size = (int(surface.get_width() * scale),
                           int(surface.get_height() * scale))
                surface = pygame.transform.scale(surface, new_size)
            
            self._sprite_cache[cache_key] = surface
            return surface
        except Exception as e:
            log_error(f"Failed to load sprite {path}: {e}")
            return None
    
    def has_sprite(self, path: str) -> bool:
        """检查精灵文件是否存在"""
        return (self.assets_path / path).exists()
    
    def get_sprite_sheet(self, path: str, frame_size: Tuple[int, int], 
                         frame_count: int) -> Optional[List[pygame.Surface]]:
        """
        加载精灵表并切割为帧列表
        
        Args:
            path: 精灵表路径
            frame_size: 单帧尺寸 (width, height)
            frame_count: 帧数量
        
        Returns:
            帧列表或None
        """
        sheet = self.get_sprite(path)
        if sheet is None:
            return None
        
        frames = []
        for i in range(frame_count):
            frame = pygame.Surface(frame_size, pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), 
                      (i * frame_size[0], 0, frame_size[0], frame_size[1]))
            frames.append(frame)
        
        return frames
    
    def save_sprite(self, surface: pygame.Surface, path: str) -> bool:
        """
        保存精灵到文件
        
        Args:
            surface: 要保存的Surface
            path: 相对于assets目录的路径
        
        Returns:
            是否成功
        """
        full_path = self.assets_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            pygame.image.save(surface, str(full_path))
            log_info(f"Saved sprite: {path}")
            return True
        except Exception as e:
            log_error(f"Failed to save sprite {path}: {e}")
            return False
    
    # ==================== 数据加载 ====================
    
    def get_data(self, path: str) -> dict:
        """
        获取JSON数据配置
        
        Args:
            path: 相对于data目录的路径
        
        Returns:
            解析后的字典，不存在则返回空字典
        """
        # 开发模式下不使用缓存（支持热重载）
        if path in self._data_cache and not self.dev_mode:
            return self._data_cache[path].copy()
        
        full_path = self.data_path / path
        
        if not full_path.exists():
            return {}
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._data_cache[path] = data
            return data.copy()
        except Exception as e:
            log_error(f"Failed to load data {path}: {e}")
            return {}
    
    def save_data(self, path: str, data: dict) -> bool:
        """
        保存数据到JSON文件
        
        Args:
            path: 相对于data目录的路径
            data: 要保存的数据
        
        Returns:
            是否成功
        """
        full_path = self.data_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            # 更新缓存
            self._data_cache[path] = data
            return True
        except Exception as e:
            log_error(f"Failed to save data {path}: {e}")
            return False
    
    def get_plane_config(self, plane_id: str) -> dict:
        """获取机体配置"""
        return self.get_data(f"planes/{plane_id}.json")
    
    def get_skin_config(self, plane_id: str) -> dict:
        """获取涂装配置"""
        return self.get_data(f"skins/{plane_id}_skins.json")
    
    def get_all_plane_ids(self) -> List[str]:
        """获取所有机体ID列表"""
        planes_dir = self.data_path / "planes"
        if not planes_dir.exists():
            return []
        return [f.stem for f in planes_dir.glob("*.json") 
                if not f.name.startswith("_")]
    
    def get_boss_config(self, boss_id: str) -> dict:
        """获取 Boss 配置"""
        return self.get_data(f"bosses/{boss_id}.json")
    
    def get_all_boss_ids(self) -> List[str]:
        """获取所有 Boss ID 列表"""
        bosses_dir = self.data_path / "bosses"
        if not bosses_dir.exists():
            return []
        return [f.stem for f in bosses_dir.glob("*.json") 
                if not f.name.startswith("_")]
    
    # ==================== 音频加载 ====================
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """
        获取音效
        
        Args:
            name: 音效名称（不含扩展名）
        
        Returns:
            Sound对象或None
        """
        if name in self._sound_cache:
            return self._sound_cache[name]
        
        # 尝试多种扩展名
        for ext in [".wav", ".ogg", ".mp3"]:
            file_path = self.assets_path / "audio" / "sfx" / f"{name}{ext}"
            if file_path.exists():
                try:
                    sound = pygame.mixer.Sound(str(file_path))
                    self._sound_cache[name] = sound
                    return sound
                except Exception as e:
                    log_error(f"Failed to load sound {name}: {e}")
        
        return None
    
    def has_sound(self, name: str) -> bool:
        """检查音效是否存在"""
        for ext in [".wav", ".ogg", ".mp3"]:
            if (self.assets_path / "audio" / "sfx" / f"{name}{ext}").exists():
                return True
        return False
    
    def get_music_path(self, name: str) -> Optional[str]:
        """
        获取BGM文件路径
        
        Args:
            name: BGM名称（不含扩展名）
        
        Returns:
            文件路径或None
        """
        for ext in [".ogg", ".mp3", ".wav"]:
            file_path = self.assets_path / "audio" / "bgm" / f"{name}{ext}"
            if file_path.exists():
                return str(file_path)
        return None
    
    # ==================== 字体加载 ====================
    
    def get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        """
        获取字体
        
        Args:
            size: 字体大小
            bold: 是否加粗
        
        Returns:
            Font对象
        """
        cache_key = (size, bold)
        
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        # 尝试加载自定义字体
        font_path = self.assets_path / "fonts" / "main_font.ttf"
        
        try:
            if font_path.exists():
                font = pygame.font.Font(str(font_path), size)
            else:
                # 回退到系统字体
                font = pygame.font.SysFont(
                    ["microsoftyahei", "simhei", "arial"], 
                    size, bold=bold
                )
            self._font_cache[cache_key] = font
            return font
        except:
            return pygame.font.Font(None, size)
    
    # ==================== 颜色系统 ====================
    
    def _load_color_palette(self):
        """加载颜色配置"""
        data = self.get_data("ui/colors.json")
        if data:
            self._parse_colors(data.get("palette", {}))
        
        # 始终添加默认颜色作为回退
        self._add_default_colors()
    
    def _parse_colors(self, palette: dict, prefix: str = ""):
        """递归解析颜色配置"""
        for key, value in palette.items():
            full_key = f"{prefix}_{key}" if prefix else key
            if isinstance(value, dict):
                self._parse_colors(value, full_key)
            elif isinstance(value, str) and value.startswith("#"):
                self.colors[full_key] = self._hex_to_rgb(value)
            elif isinstance(value, (list, tuple)) and len(value) >= 3:
                self.colors[full_key] = tuple(value[:3])
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """将十六进制颜色转换为RGB"""
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    
    def _add_default_colors(self):
        """添加默认颜色（作为回退）"""
        defaults = {
            "primary_cyan": (0, 255, 255),
            "primary_cyan_bright": (0, 229, 255),
            "accent_amber": (255, 215, 0),
            "accent_lime": (0, 255, 0),
            "accent_magenta": (255, 0, 255),
            "alert_red": (255, 51, 51),
            "alert_danger": (255, 0, 0),
            "background_deep_black": (5, 10, 20),
            "background_midnight": (0, 5, 16),
            "ui_text_primary": (255, 255, 255),
            "ui_text_secondary": (144, 164, 174),
            "rarity_common": (150, 150, 150),
            "rarity_rare": (100, 200, 255),
            "rarity_epic": (200, 100, 255),
            "rarity_legendary": (255, 200, 50),
            "rarity_mythic": (255, 100, 200),
            "rarity_supreme": (255, 255, 255),
        }
        # 只添加不存在的颜色
        for key, value in defaults.items():
            if key not in self.colors:
                self.colors[key] = value
    
    def get_color(self, name: str, default: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[int, int, int]:
        """
        获取颜色
        
        Args:
            name: 颜色名称
            default: 默认颜色
        
        Returns:
            RGB颜色元组
        """
        return self.colors.get(name, default)
    
    # ==================== 缓存管理 ====================
    
    def clear_cache(self, cache_type: str = "all"):
        """
        清理缓存
        
        Args:
            cache_type: 缓存类型 ("all", "sprites", "sounds", "data", "fonts")
        """
        if cache_type in ("all", "sprites"):
            self._sprite_cache.clear()
        if cache_type in ("all", "sounds"):
            self._sound_cache.clear()
        if cache_type in ("all", "data"):
            self._data_cache.clear()
        if cache_type in ("all", "fonts"):
            self._font_cache.clear()
        
        log_info(f"Cache cleared: {cache_type}")
    
    def preload_essential(self):
        """预加载核心资源"""
        # 预加载颜色配置
        self._load_color_palette()
        
        # 预加载常用音效
        essential_sounds = ["shoot", "hit", "explosion", "select", "confirm"]
        for name in essential_sounds:
            self.get_sound(name)
        
        log_info("Essential assets preloaded")
    
    def get_memory_usage(self) -> dict:
        """获取缓存使用情况"""
        return {
            "sprites": len(self._sprite_cache),
            "sounds": len(self._sound_cache),
            "data": len(self._data_cache),
            "fonts": len(self._font_cache),
        }
    
    def get_stats(self) -> str:
        """获取资产统计信息"""
        usage = self.get_memory_usage()
        return (
            f"AssetManager Stats:\n"
            f"  Sprites cached: {usage['sprites']}\n"
            f"  Sounds cached: {usage['sounds']}\n"
            f"  Data cached: {usage['data']}\n"
            f"  Fonts cached: {usage['fonts']}\n"
            f"  Dev mode: {self.dev_mode}"
        )
    
    # ==================== 机体配置兼容层 ====================
    
    def load_planes_dict(self, fallback_planes: dict = None) -> dict:
        """
        加载所有机体配置并转换为旧格式 PLANES 字典
        
        这是一个兼容层，将新的 JSON 格式转换回 config.py 使用的旧格式。
        如果 JSON 不存在或加载失败，使用 fallback_planes。
        
        保持 fallback_planes 的原始顺序（如果提供），确保机体选择界面顺序一致。
        
        Args:
            fallback_planes: 备用的硬编码 PLANES 字典（也用于确定顺序）
        
        Returns:
            PLANES 格式的字典
        """
        planes = {}
        
        # 使用 fallback 的顺序，而不是文件系统字母顺序
        if fallback_planes:
            plane_ids = list(fallback_planes.keys())
        else:
            plane_ids = self.get_all_plane_ids()
        
        if not plane_ids:
            log_info("No plane IDs found, using fallback")
            return fallback_planes or {}
        
        for plane_id in plane_ids:
            try:
                config = self.get_plane_config(plane_id)
                if not config:
                    # JSON 不存在，使用 fallback
                    if fallback_planes and plane_id in fallback_planes:
                        planes[plane_id] = fallback_planes[plane_id]
                    continue
                
                # 转换为旧格式
                old_format = self._convert_plane_to_old_format(plane_id, config, fallback_planes)
                if old_format:
                    planes[plane_id] = old_format
            except Exception as e:
                log_error(f"Failed to convert plane {plane_id}: {e}")
                # 使用备用数据
                if fallback_planes and plane_id in fallback_planes:
                    planes[plane_id] = fallback_planes[plane_id]
        
        log_info(f"Loaded {len(planes)} planes from JSON")
        return planes
    
    def _convert_plane_to_old_format(self, plane_id: str, config: dict, fallback: dict = None) -> dict:
        """
        将新 JSON 格式转换为旧 PLANES 字典格式
        
        新格式 (JSON):
        {
            "id": "striker",
            "name": "霓虹突击者",
            "description": "...",
            "stats": {"hp": 260, "speed": 4.0, "damage": 18, "fire_rate": 180, ...},
            "visuals": {"colors": {"primary": "#00E5FF", ...}},
            "abilities": {"ultimate": {"name": "...", "color": "#00FFFF"}},
            "bullet": {"type": "beam"}
        }
        
        旧格式 (config.py):
        {
            "name": "霓虹突击者",
            "desc": "...",
            "hp": 260, "speed": 4.0, "damage": 18, "delay": 180,
            "color": (0, 229, 255),
            "ult_name": "...", "ult_color": (0, 255, 255),
            "bullet_type": "beam",
            "visual": {...},
            "skills": {...}  # 可选
        }
        """
        stats = config.get("stats", {})
        visuals = config.get("visuals", {})
        colors = visuals.get("colors", {})
        abilities = config.get("abilities", {})
        ultimate = abilities.get("ultimate", {})
        passive = abilities.get("passive", {})
        bullet = config.get("bullet", {})
        
        # 基础字段
        result = {
            "name": config.get("name", plane_id),
            "desc": config.get("description", ""),
            "hp": stats.get("hp", 260),
            "speed": stats.get("speed", 4.0),
            "damage": stats.get("damage", 18),
            "delay": stats.get("fire_rate", 180),
            "color": self._hex_to_rgb(colors.get("primary", "#FFFFFF")),
            "ult_name": ultimate.get("name", ""),
            "ult_color": self._hex_to_rgb(ultimate.get("color", "#FFFFFF")),
            "bullet_type": bullet.get("type", "beam"),
        }
        
        # ult_charge_rate (如果存在)
        if "ult_charge_rate" in stats:
            result["ult_charge_rate"] = stats["ult_charge_rate"]
        
        # visual 字段
        if colors or passive.get("id"):
            result["visual"] = {
                "neon_color": self._hex_to_rgb(colors.get("glow", colors.get("primary", "#FFFFFF"))),
                "accent_color": self._hex_to_rgb(colors.get("secondary", "#FFFFFF")),
                "trail_color": self._hex_to_rgb(colors.get("trail", colors.get("primary", "#FFFFFF"))),
            }
            if passive.get("id"):
                result["visual"]["ability"] = passive["id"]
        
        # skills 字段 - 优先从 JSON 加载，否则从 fallback 获取
        skills_data = config.get("skills", {})
        if skills_data:
            result["skills"] = skills_data
        elif fallback and plane_id in fallback and "skills" in fallback[plane_id]:
            # JSON 中没有 skills，从 fallback 获取
            result["skills"] = fallback[plane_id]["skills"]
        
        return result
    
    # ==================== Boss 配置兼容层 ====================
    
    def load_boss_db(self, fallback_bosses: dict = None) -> dict:
        """
        加载所有 Boss 配置并转换为旧格式 BOSS_DB 字典
        
        Args:
            fallback_bosses: 备用的硬编码 BOSS_DB 字典（也用于确定顺序）
        
        Returns:
            BOSS_DB 格式的字典
        """
        bosses = {}
        
        # 使用 fallback 的顺序
        if fallback_bosses:
            boss_ids = list(fallback_bosses.keys())
        else:
            boss_ids = self.get_all_boss_ids()
        
        if not boss_ids:
            log_info("No boss IDs found, using fallback")
            return fallback_bosses or {}
        
        for boss_id in boss_ids:
            try:
                config = self.get_boss_config(boss_id)
                if not config:
                    if fallback_bosses and boss_id in fallback_bosses:
                        bosses[boss_id] = fallback_bosses[boss_id]
                    continue
                
                old_format = self._convert_boss_to_old_format(boss_id, config)
                if old_format:
                    bosses[boss_id] = old_format
            except Exception as e:
                log_error(f"Failed to convert boss {boss_id}: {e}")
                if fallback_bosses and boss_id in fallback_bosses:
                    bosses[boss_id] = fallback_bosses[boss_id]
        
        log_info(f"Loaded {len(bosses)} bosses from JSON")
        return bosses
    
    def _convert_boss_to_old_format(self, boss_id: str, config: dict) -> dict:
        """
        将新 JSON 格式转换为旧 BOSS_DB 字典格式
        """
        stats = config.get("stats", {})
        visuals = config.get("visuals", {})
        colors = visuals.get("colors", {})
        
        result = {
            "name": config.get("name", boss_id),
            "desc": config.get("description", ""),
            "color": self._hex_to_rgb(colors.get("primary", "#FFFFFF")),
            "stats": [
                ("装甲", stats.get("armor", 100)),
                ("毁灭", stats.get("damage", 100)),
                ("机动", stats.get("mobility", 50)),
            ],
            "visual": {
                "core_color": self._hex_to_rgb(colors.get("core", colors.get("primary", "#FFFFFF"))),
                "aura": self._hex_to_rgb(colors.get("aura", "#FFFFFF")),
                "phase_effect": visuals.get("phase_effect", ""),
            },
            "phases": config.get("phases", []),
        }
        
        return result


# 全局单例实例
asset_manager = AssetManager()
