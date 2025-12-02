"""
敌人类型管理器 - 用于机密档案系统
提供敌人类型信息的查询和管理
"""
from config import *

class EnemyTypeManager:
    """敌人类型管理器"""
    
    def __init__(self):
        """初始化敌人类型数据"""
        self.enemy_types = [
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
                "id": "tank",
                "name": "重装坦克",
                "desc": "装甲厚重的敌方单位，移动缓慢但血量极高",
                "hp": 200,
                "speed": 1,
                "score": 300,
                "color": (100, 100, 200),
                "threat_level": 3,
                "abilities": ["重装甲", "缓慢移动", "强力炮击"],
            },
            {
                "id": "sniper",
                "name": "狙击机",
                "desc": "远程精确打击型敌机，攻击力高但防御薄弱",
                "hp": 40,
                "speed": 2,
                "score": 200,
                "color": (200, 200, 100),
                "threat_level": 3,
                "abilities": ["精确射击", "远程攻击", "锁定"],
            },
            {
                "id": "bomber",
                "name": "轰炸机",
                "desc": "大范围轰炸型敌机，造成区域伤害",
                "hp": 80,
                "speed": 1.5,
                "score": 250,
                "color": (200, 100, 200),
                "threat_level": 3,
                "abilities": ["投掷炸弹", "区域伤害"],
            },
            {
                "id": "elite",
                "name": "精英战机",
                "desc": "敌方精锐部队，全面强化的战斗单位",
                "hp": 150,
                "speed": 3,
                "score": 500,
                "color": (255, 150, 50),
                "threat_level": 4,
                "abilities": ["强化攻击", "闪避", "护盾"],
            },
            {
                "id": "kamikaze",
                "name": "自爆机",
                "desc": "冲向玩家自爆的敌机，速度快但易碎",
                "hp": 20,
                "speed": 5,
                "score": 150,
                "color": (255, 100, 100),
                "threat_level": 2,
                "abilities": ["高速冲撞", "自爆", "追踪"],
            },
            {
                "id": "carrier",
                "name": "母舰",
                "desc": "能够释放小型敌机的大型单位",
                "hp": 300,
                "speed": 1,
                "score": 800,
                "color": (150, 150, 255),
                "threat_level": 5,
                "abilities": ["召唤敌机", "重装甲", "多管炮塔"],
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
