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
        """从 JSON 和硬编码数据加载敌人类型"""
        enemies = []
        
        # 首先尝试从 enemy_types.json 加载新敌人
        try:
            with open('enemy_types.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 将 JSON 中的敌人转换为机密档案格式
            for enemy_id, config in data.get('enemies', {}).items():
                threat_level = 1
                category = config.get('category', '')
                if '高级' in category:
                    threat_level = 3
                elif '顶级' in category:
                    threat_level = 5
                
                enemies.append({
                    "id": enemy_id,
                    "name": config.get('name', '未知'),
                    "desc": config.get('description', ''),
                    "hp": config.get('hp', 50),
                    "speed": config.get('speed', 2.0),
                    "score": config.get('score', 100),
                    "color": tuple(config.get('color', [100, 100, 100])),
                    "threat_level": threat_level,
                    "abilities": [
                        f"AI: {config.get('ai_behavior', 'straight')}",
                        f"攻击: {config.get('attack_pattern', 'single')}"
                    ],
                    "special": config.get('special_ability', None),
                })
        except Exception as e:
            # 如果加载失败，使用默认敌人
            print(f"警告：加载 enemy_types.json 失败 ({e})，使用默认敌人")
            enemies = self._get_default_enemies()
        
        return enemies
    
    def _get_default_enemies(self):
        """默认敌人列表（备用）"""
        return [
            {
                "id": "basic",
                "name": "基础敌机",
                "desc": "标准型号的敌方战机，速度中等，耐久较低",
                "hp": 50,
                "speed": 2,
                "score": 100,
                "color": (200, 100, 100),
                "threat_level": 1,
                "abilities": ["直线移动", "基础射击"],
            },
            {
                "id": "fast",
                "name": "疾风战机",
                "desc": "高速机动型敌机，难以命中但脆弱",
                "hp": 30,
                "speed": 4,
                "score": 150,
                "color": (100, 200, 100),
                "threat_level": 2,
                "abilities": ["高速移动", "闪避", "快速射击"],
            },
            {
                "id": "boss_1",
                "name": "钢铁巨兽",
                "desc": "第一关BOSS，装甲厚重的机械巨兽",
                "hp": 5000,
                "speed": 0.5,
                "score": 10000,
                "color": (180, 180, 180),
                "threat_level": 10,
                "abilities": ["多阶段形态", "导弹雨", "激光炮", "召唤支援"],
                "is_boss": True,
            },
            {
                "id": "boss_2",
                "name": "量子幽灵",
                "desc": "第二关BOSS，能够相位转移的神秘实体",
                "hp": 6000,
                "speed": 2,
                "score": 15000,
                "color": (150, 255, 255),
                "threat_level": 10,
                "abilities": ["相位转移", "分身", "能量弹幕", "时空扭曲"],
                "is_boss": True,
            },
            {
                "id": "boss_3",
                "name": "熔岩泰坦",
                "desc": "第三关BOSS，火焰与熔岩的化身",
                "hp": 8000,
                "speed": 1,
                "score": 20000,
                "color": (255, 100, 0),
                "threat_level": 10,
                "abilities": ["火焰风暴", "岩浆喷发", "燃烧光环", "陨石召唤"],
                "is_boss": True,
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
