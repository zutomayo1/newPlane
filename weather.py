"""
动态天气和环境效果系统
支持雨、雪、流星、风等多种环境效果
"""

import pygame
import math
import random
from enum import Enum


class WeatherType(Enum):
    """天气类型枚举"""
    CLEAR = 0  # 晴空
    RAIN = 1  # 雨
    SNOW = 2  # 雪
    METEOR = 3  # 流星雨
    WIND = 4  # 强风
    SANDSTORM = 5  # 沙暴


class Raindrop:
    """雨滴粒子"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = random.uniform(8, 15)  # 下降速度
        self.length = random.uniform(15, 30)  # 雨线长度
        self.wind_effect = random.uniform(-3, 3)  # 风的影响
        self.opacity = 180
    
    def update(self):
        """更新雨滴位置"""
        self.y += self.speed
        self.x += self.wind_effect * 0.5
        # 超出屏幕则重置
        if self.y > self.height or self.x < -20 or self.x > self.width + 20:
            self.reset(self.width, self.height)
    
    def reset(self, width, height):
        """重置雨滴位置"""
        self.x = random.uniform(-20, width + 20)
        self.y = random.uniform(-50, 0)
        self.speed = random.uniform(8, 15)
        self.wind_effect = random.uniform(-3, 3)
        self.opacity = 180
    
    def draw(self, surface):
        """绘制雨线"""
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # 绘制半透明雨线
        end_x = self.x + self.wind_effect * self.length / 15
        end_y = self.y + self.length
        pygame.draw.line(s, (200, 220, 255, self.opacity), 
                        (self.x, self.y), (end_x, end_y), 2)
        surface.blit(s, (0, 0))


class Snowflake:
    """雪花粒子"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = random.uniform(2, 5)  # 下降速度（缓慢）
        self.size = random.uniform(2, 8)  # 雪花大小
        self.wind_effect = random.uniform(-2, 2)  # 风的影响
        self.oscillation = random.uniform(0, math.pi * 2)  # 摇晃角度
        self.opacity = 200
    
    def update(self):
        """更新雪花位置"""
        self.y += self.speed
        self.oscillation += random.uniform(0.05, 0.15)
        self.x += math.sin(self.oscillation) * 0.5 + self.wind_effect * 0.3
        
        if self.y > self.height or self.x < -20 or self.x > self.width + 20:
            self.reset(self.width, self.height)
    
    def reset(self, width, height):
        """重置雪花位置"""
        self.x = random.uniform(-20, width + 20)
        self.y = random.uniform(-50, 0)
        self.speed = random.uniform(2, 5)
        self.size = random.uniform(2, 8)
        self.wind_effect = random.uniform(-2, 2)
        self.oscillation = random.uniform(0, math.pi * 2)
        self.opacity = 200
    
    def draw(self, surface):
        """绘制雪花"""
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # 绘制白色雪花圆形
        pygame.draw.circle(s, (255, 255, 255, self.opacity), 
                          (int(self.x), int(self.y)), int(self.size))
        # 添加冰晶光晕
        if self.size > 3:
            pygame.draw.circle(s, (220, 240, 255, self.opacity // 2), 
                              (int(self.x), int(self.y)), int(self.size + 2), 1)
        surface.blit(s, (0, 0))


class Meteor:
    """流星粒子"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx = random.uniform(-8, -2)  # 向左下飞行
        self.vy = random.uniform(8, 15)  # 向下飞行
        self.size = random.uniform(3, 12)
        self.trail_length = int(self.size * 3)  # 尾焰长度
        self.opacity = 255
        self.life = random.randint(100, 300)  # 存活时间
    
    def update(self):
        """更新流星位置"""
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        
        if self.life <= 0 or self.y > self.height or self.x < -30:
            self.reset(self.width, self.height)
    
    def reset(self, width, height):
        """重置流星位置"""
        self.x = random.uniform(width + 30, width + 200)
        self.y = random.uniform(-50, -100)
        self.vx = random.uniform(-8, -2)
        self.vy = random.uniform(8, 15)
        self.size = random.uniform(3, 12)
        self.trail_length = int(self.size * 3)
        self.opacity = 255
        self.life = random.randint(100, 300)
    
    def draw(self, surface):
        """绘制流星和尾焰"""
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # 计算流星头部颜色（黄->白->橙）
        head_color = (255, 200, 50, self.opacity)
        
        # 绘制流星尾焰（逐渐淡化）
        for i in range(self.trail_length):
            trail_alpha = int(self.opacity * (1 - i / self.trail_length))
            trail_x = self.x + self.vx * i / 2
            trail_y = self.y + self.vy * i / 2
            trail_size = max(1, int(self.size * (1 - i / self.trail_length)))
            if trail_size > 0:
                pygame.draw.circle(s, (255, 150, 0, trail_alpha), 
                                  (int(trail_x), int(trail_y)), trail_size)
        
        # 绘制流星头部
        pygame.draw.circle(s, head_color, (int(self.x), int(self.y)), int(self.size))
        
        # 添加流星光晕
        pygame.draw.circle(s, (255, 220, 100, self.opacity // 2), 
                          (int(self.x), int(self.y)), int(self.size + 3), 1)
        
        surface.blit(s, (0, 0))
    
    def get_impact_pos(self):
        """获取流星将要撞击的位置（用于生成爆炸）"""
        return (self.x, self.y)


class WindEffect:
    """风效应"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.wind_strength = 1.0  # 风力强度 (0-2)
        self.wind_direction = 0  # 风向 (0-360度)
        self.time = 0
        self.particles = []
        self.particle_count = 25
        self._init_particles()
    
    def _init_particles(self):
        """初始化风粒子"""
        self.particles = []
        for _ in range(self.particle_count):
            self.particles.append({
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height),
                'size': random.uniform(1, 3),
                'opacity': random.uniform(50, 150)
            })
    
    def update(self):
        """更新风效应"""
        self.time += 1
        # 风向和强度随时间变化
        self.wind_direction = (self.time / 10) % 360
        self.wind_strength = 0.5 + 0.5 * math.sin(self.time / 100)
        
        # 更新粒子
        for particle in self.particles:
            # 风吹动粒子
            particle['x'] += self.wind_strength * 3
            particle['y'] += random.uniform(-1, 1)
            
            # 超出屏幕则重置
            if particle['x'] > self.width + 20:
                particle['x'] = -20
                particle['y'] = random.uniform(0, self.height)
    
    def draw(self, surface):
        """绘制风粒子"""
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        for particle in self.particles:
            pygame.draw.circle(s, (200, 200, 200, particle['opacity']), 
                              (int(particle['x']), int(particle['y'])), 
                              int(particle['size']))
        
        surface.blit(s, (0, 0))
    
    def apply_to_bullet(self, bullet):
        """对子弹应用风力影响"""
        angle_rad = self.wind_direction / 180 * math.pi
        wind_x = self.wind_strength * 3 * math.cos(angle_rad)
        wind_y = self.wind_strength * 3 * math.sin(angle_rad)
        bullet.rect.x += wind_x
        bullet.rect.y += wind_y


class Sandstorm:
    """沙暴效应"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.time = 0
        self.particles = []
        self.particle_count = 40
        self._init_particles()
    
    def _init_particles(self):
        """初始化沙粒"""
        self.particles = []
        for _ in range(self.particle_count):
            self.particles.append({
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height),
                'vx': random.uniform(2, 8),
                'vy': random.uniform(-1, 2),
                'size': random.uniform(1, 4),
                'opacity': random.uniform(100, 200)
            })
    
    def update(self):
        """更新沙暴效应"""
        self.time += 1
        
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # 风强度随时间变化
            particle['vx'] += random.uniform(-0.2, 0.2)
            particle['vx'] = max(2, min(8, particle['vx']))
            
            # 超出屏幕则重置
            if particle['x'] > self.width + 20:
                particle['x'] = -20
                particle['y'] = random.uniform(0, self.height)
    
    def draw(self, surface):
        """绘制沙暴"""
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        for particle in self.particles:
            color = (220, 180, 100, particle['opacity'])
            pygame.draw.circle(s, color, 
                              (int(particle['x']), int(particle['y'])), 
                              int(particle['size']))
        
        # 添加整体沙暴雾霾层
        fog_alpha = int(50 * abs(math.sin(self.time / 100)))
        fog = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(fog, (200, 160, 80, fog_alpha), fog.get_rect())
        s.blit(fog, (0, 0))
        
        surface.blit(s, (0, 0))


class WeatherSystem:
    """完整天气系统管理器"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_weather = WeatherType.CLEAR
        self.weather_timer = 0
        self.weather_duration = 600  # 天气持续时间（帧数）
        self.transition_timer = 0  # 过渡计时器
        self.transition_duration = 60  # 过渡持续时间（帧数）
        
        # 天气特定对象
        self.raindrops = []
        self.snowflakes = []
        self.meteors = []
        self.wind_effect = WindEffect(width, height)
        self.sandstorm = Sandstorm(width, height)
        
        # 初始化雨滴和雪花
        self._init_rain()
        self._init_snow()
        
        # 天气影响参数
        self.visibility = 1.0  # 能见度（0-1）
        self.player_speed_modifier = 1.0  # 玩家速度修饰符
        self.bullet_damage_modifier = 1.0  # 子弹伤害修饰符
        
        # 天气变化队列
        self.weather_queue = []
        self._generate_weather_schedule()
    
    def _init_rain(self):
        """初始化雨滴"""
        self.raindrops = [Raindrop(random.uniform(0, self.width), 
                                   random.uniform(0, self.height),
                                   self.width, self.height) 
                         for _ in range(40)]
    
    def _init_snow(self):
        """初始化雪花"""
        self.snowflakes = [Snowflake(random.uniform(0, self.width), 
                                     random.uniform(0, self.height),
                                     self.width, self.height) 
                          for _ in range(30)]
    
    def _generate_weather_schedule(self):
        """生成天气变化计划"""
        weather_types = [WeatherType.CLEAR, WeatherType.RAIN, WeatherType.SNOW, 
                        WeatherType.METEOR, WeatherType.WIND, WeatherType.SANDSTORM]
        # 每波可能性不同
        self.weather_queue = [random.choice(weather_types) for _ in range(10)]
    
    def update(self):
        """更新天气系统"""
        self.weather_timer += 1
        
        # 处理天气过渡
        if self.weather_timer >= self.weather_duration:
            self._change_weather()
            self.weather_timer = 0
        
        # 更新当前天气效果
        if self.current_weather == WeatherType.RAIN:
            for raindrop in self.raindrops:
                raindrop.update()
            self.visibility = 0.7
            self.player_speed_modifier = 0.85  # 雨中稍微变慢
            self.bullet_damage_modifier = 0.95
        
        elif self.current_weather == WeatherType.SNOW:
            for snowflake in self.snowflakes:
                snowflake.update()
            self.visibility = 0.6
            self.player_speed_modifier = 0.75  # 雪中更慢
            self.bullet_damage_modifier = 0.9
        
        elif self.current_weather == WeatherType.METEOR:
            # 流星定期生成，限制最大数量
            if random.random() < 0.015 and len(self.meteors) < 20:  # 降低生成概率，限制最多20个流星
                self.meteors.append(Meteor(random.uniform(self.width, self.width + 100), 
                                          random.uniform(-50, 0),
                                          self.width, self.height))
            # 更新流星并清理超出屏幕的
            self.meteors = [m for m in self.meteors if m.life > 0]
            for meteor in self.meteors:
                meteor.update()
            self.visibility = 0.8
            self.player_speed_modifier = 1.0
            self.bullet_damage_modifier = 1.0
        
        elif self.current_weather == WeatherType.WIND:
            self.wind_effect.update()
            self.visibility = 0.9
            self.player_speed_modifier = 0.8  # 风中更难控制
            self.bullet_damage_modifier = 0.85
        
        elif self.current_weather == WeatherType.SANDSTORM:
            self.sandstorm.update()
            self.visibility = 0.5  # 沙暴视线最差
            self.player_speed_modifier = 0.7
            self.bullet_damage_modifier = 0.8
        
        else:  # CLEAR
            self.visibility = 1.0
            self.player_speed_modifier = 1.0
            self.bullet_damage_modifier = 1.0
    
    def _change_weather(self):
        """切换天气"""
        if self.weather_queue:
            self.current_weather = self.weather_queue.pop(0)
            # 清理流星列表（节省内存）
            self.meteors = []
            if not self.weather_queue:
                self._generate_weather_schedule()
    
    def draw(self, surface):
        """绘制所有天气效果"""
        if self.current_weather == WeatherType.RAIN:
            for raindrop in self.raindrops:
                raindrop.draw(surface)
        
        elif self.current_weather == WeatherType.SNOW:
            for snowflake in self.snowflakes:
                snowflake.draw(surface)
        
        elif self.current_weather == WeatherType.METEOR:
            for meteor in self.meteors:
                meteor.draw(surface)
        
        elif self.current_weather == WeatherType.WIND:
            self.wind_effect.draw(surface)
        
        elif self.current_weather == WeatherType.SANDSTORM:
            self.sandstorm.draw(surface)
        
        # 绘制天气信息（左上角）
        self._draw_weather_info(surface)
    
    def _draw_weather_info(self, surface):
        """绘制天气信息"""
        font = pygame.font.Font(None, 24)
        weather_names = {
            WeatherType.CLEAR: "晴空",
            WeatherType.RAIN: "降雨",
            WeatherType.SNOW: "降雪",
            WeatherType.METEOR: "流星雨",
            WeatherType.WIND: "强风",
            WeatherType.SANDSTORM: "沙暴"
        }
        
        text = f"天气: {weather_names[self.current_weather]}"
        # 根据天气类型选择颜色
        color_map = {
            WeatherType.CLEAR: (100, 200, 255),
            WeatherType.RAIN: (100, 150, 255),
            WeatherType.SNOW: (200, 220, 255),
            WeatherType.METEOR: (255, 150, 0),
            WeatherType.WIND: (150, 200, 220),
            WeatherType.SANDSTORM: (200, 160, 80)
        }
        color = color_map[self.current_weather]
        
        surf = font.render(text, True, color)
        surface.blit(surf, (10, 10))
        
        # 显示进度条
        progress = self.weather_timer / self.weather_duration
        bar_width = 200
        bar_height = 6
        bar_x, bar_y = 10, 40
        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, color, (bar_x, bar_y, int(bar_width * progress), bar_height))
    
    def get_weather_name(self):
        """获取当前天气名称"""
        names = {
            WeatherType.CLEAR: "晴空",
            WeatherType.RAIN: "降雨",
            WeatherType.SNOW: "降雪",
            WeatherType.METEOR: "流星雨",
            WeatherType.WIND: "强风",
            WeatherType.SANDSTORM: "沙暴"
        }
        return names.get(self.current_weather, "未知")
    
    def check_meteor_impact(self, rect):
        """检查是否被流星击中（用于伤害判定）"""
        damage_radius = 40
        for meteor in self.meteors:
            dx = meteor.x - rect.centerx
            dy = meteor.y - rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < damage_radius:
                return True
        return False
    
    def apply_weather_effects_to_bullets(self, bullets):
        """对所有子弹应用天气影响"""
        if self.current_weather == WeatherType.WIND:
            for bullet in bullets:
                self.wind_effect.apply_to_bullet(bullet)
