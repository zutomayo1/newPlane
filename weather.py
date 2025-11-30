"""
动态天气和环境效果系统 (精简版 - 禁用天气以优化性能)
"""

import pygame
from enum import Enum

class WeatherType(Enum):
    """天气类型枚举"""
    CLEAR = 0
    RAIN = 1
    SNOW = 2
    METEOR = 3
    WIND = 4
    SANDSTORM = 5

class WeatherSystem:
    """精简版天气系统管理器 (不执行任何逻辑)"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_weather = WeatherType.CLEAR
        
        # 天气影响参数 (保持默认值)
        self.visibility = 1.0
        self.player_speed_modifier = 1.0
        self.bullet_damage_modifier = 1.0
    
    def update(self):
        """不执行任何更新"""
        pass
        
    def draw(self, screen):
        """不绘制任何内容"""
        pass
        
    def apply_weather_effects_to_bullets(self, bullets):
        """不应用任何效果"""
        pass
        
    def check_meteor_impact(self, player_rect):
        """不检测陨石碰撞"""
        return False
