"""
敌人类型管理器 - 用于机密档案系统
提供敌人类型信息的查询和管理
"""
from config import *
import json

class EnemyTypeManager:
    """敌人类型管理器"""
    
    def __init__(self):
        """初始化敌人类型数据"""
        self.enemy_types = self._load_enemy_types()
    
    def _load_enemy_types(self):
        """从 JSON 和内置数据加载敌人类型"""
        enemies = []

        try:
            with open('enemy_types.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            source = data.get('enemies', {})
        except Exception as e:
            print(f"警告：加载 enemy_types.json 失败 ({e})，使用默认敌人")
            from enemies import BUILTIN_ENEMIES

            source = BUILTIN_ENEMIES

        for enemy_id, config in source.items():
            enemies.append({
                "id": enemy_id,
                "name": config.get('name', '未知'),
                "desc": config.get('description', ''),
                "hp": config.get('hp', 50),
                "speed": config.get('speed', 2.0),
                "score": config.get('score', 100),
                "color": tuple(config.get('color', [100, 100, 100])),
                "threat_level": config.get('threat', 1),
                "abilities": [
                    f"移动: {config.get('behavior', 'down')}",
                    f"攻击: {config.get('attack_pattern', 'single')}"
                ],
                "special": config.get('special', None),
            })

        return enemies
    
    def _get_default_enemies(self):
        """默认敌人列表（备用）"""
        return [
            {
                "id": "wisp",
                "name": "霓虹侦察·WISP",
                "desc": "蛇形推进的轻型侦察机，保持高速贴脸压制。",
                "hp": 80,
                "speed": 3.6,
                "score": 90,
                "color": (120, 220, 255),
                "threat_level": 1,
                "abilities": ["蛇形移动", "多点单发"],
            },
            {
                "id": "bulwark",
                "name": "熔核重甲·BULWARK",
                "desc": "厚甲突进的重型单位，三向压制火力封锁通道。",
                "hp": 180,
                "speed": 1.6,
                "score": 160,
                "color": (255, 140, 90),
                "threat_level": 2,
                "abilities": ["稳步推进", "三向压制"],
            },
            {
                "id": "orbiter",
                "name": "相位轨道·ORBITER",
                "desc": "侧滑环绕的中型机体，定期爆发环形弹幕。",
                "hp": 130,
                "speed": 2.3,
                "score": 130,
                "color": (180, 120, 255),
                "threat_level": 2,
                "abilities": ["轨道移动", "环形弹幕"],
            },
        ]
    
    def get_all_types(self):
        """获取所有敌人类型"""
        return self.enemy_types
    
    def get_type_by_id(self, enemy_id):
        """根据ID获取敌人类型"""
        for enemy in self.enemy_types:
            if enemy["id"] == enemy_id:
                return enemy
        return None
    
    def get_boss_types(self):
        """获取所有BOSS类型"""
        return [e for e in self.enemy_types if e.get("is_boss", False)]
    
    def get_regular_types(self):
        """获取所有普通敌人类型"""
        return [e for e in self.enemy_types if not e.get("is_boss", False)]

# 创建全局实例
enemy_type_manager = EnemyTypeManager()
