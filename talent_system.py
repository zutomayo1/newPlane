"""
星轨天赋阵系统
- 天赋管理器
- 存档系统
- 效果计算
"""

import json
import os
from config import TALENT_TREE, ULTIMATE_CORES, PATH_RESONANCE, TALENT_SAVE_FILE

class TalentManager:
    """天赋系统管理器"""
    
    def __init__(self):
        self.data = self._load_data()
    
    def _default_data(self):
        """默认存档数据"""
        return {
            "version": 1,
            "currencies": {
                "cores": 100,  # 初始核心
                "chips": 5     # 初始芯片
            },
            "talents": {
                "destruction": {},
                "guardian": {},
                "destiny": {}
            },
            "ultimates": {
                "destruction": False,
                "guardian": False,
                "destiny": False
            },
            "awakened": [],
            "ultimate_core": None,
            "resonance": {
                "destruction": False,
                "guardian": False,
                "destiny": False
            },
            "statistics": {
                "total_points_spent": 0,
                "total_cores_spent": 0,
                "total_chips_spent": 0,
                "resets": 0
            }
        }
    
    def _load_data(self):
        """加载存档"""
        try:
            if os.path.exists(TALENT_SAVE_FILE):
                with open(TALENT_SAVE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 版本兼容处理
                    default = self._default_data()
                    for key in default:
                        if key not in data:
                            data[key] = default[key]
                    return data
        except Exception as e:
            print(f"[TalentManager] 加载存档失败: {e}")
        return self._default_data()
    
    def save(self):
        """保存存档"""
        try:
            with open(TALENT_SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[TalentManager] 保存失败: {e}")
            return False
    
    # ==================== 货币系统 ====================
    
    @property
    def cores(self):
        return self.data["currencies"]["cores"]
    
    @property
    def chips(self):
        return self.data["currencies"]["chips"]
    
    def add_cores(self, amount):
        """增加核心"""
        self.data["currencies"]["cores"] += amount
        self.save()
    
    def add_chips(self, amount):
        """增加芯片"""
        self.data["currencies"]["chips"] += amount
        self.save()
    
    def spend_cores(self, amount):
        """消耗核心"""
        if self.cores >= amount:
            self.data["currencies"]["cores"] -= amount
            self.data["statistics"]["total_cores_spent"] += amount
            return True
        return False
    
    def spend_chips(self, amount):
        """消耗芯片"""
        if self.chips >= amount:
            self.data["currencies"]["chips"] -= amount
            self.data["statistics"]["total_chips_spent"] += amount
            return True
        return False
    
    # ==================== 天赋操作 ====================
    
    def get_talent_level(self, path, talent_id):
        """获取天赋等级"""
        return self.data["talents"].get(path, {}).get(talent_id, 0)
    
    def get_talent_info(self, path, branch, talent_id):
        """获取天赋信息"""
        try:
            return TALENT_TREE[path]["branches"][branch]["talents"][talent_id]
        except KeyError:
            return None
    
    def find_talent_branch(self, path, talent_id):
        """查找天赋所在分支"""
        for branch_id, branch in TALENT_TREE[path]["branches"].items():
            if talent_id in branch["talents"]:
                return branch_id
        return None
    
    def can_unlock_talent(self, path, talent_id):
        """检查是否可以解锁天赋"""
        branch_id = self.find_talent_branch(path, talent_id)
        if not branch_id:
            return False, "天赋不存在"
        
        talent = TALENT_TREE[path]["branches"][branch_id]["talents"][talent_id]
        current_level = self.get_talent_level(path, talent_id)
        
        # 已满级
        if current_level >= talent["max_level"]:
            return False, "已达最高等级"
        
        # 检查前置天赋
        if "requires" in talent:
            req_level = self.get_talent_level(path, talent["requires"])
            req_talent = TALENT_TREE[path]["branches"][branch_id]["talents"][talent["requires"]]
            if req_level < req_talent["max_level"]:
                return False, f"需要先点满 {req_talent['name']}"
        
        # 检查消耗
        cost = talent["costs"][current_level]
        if self.cores < cost:
            return False, f"核心不足 (需要{cost})"
        
        return True, "可以解锁"
    
    def upgrade_talent(self, path, talent_id):
        """升级天赋（消耗核心）"""
        can_unlock, msg = self.can_unlock_talent(path, talent_id)
        if not can_unlock:
            return False, msg
        
        branch_id = self.find_talent_branch(path, talent_id)
        talent = TALENT_TREE[path]["branches"][branch_id]["talents"][talent_id]
        current_level = self.get_talent_level(path, talent_id)
        cost = talent["costs"][current_level]
        
        # 扣除核心
        if not self.spend_cores(cost):
            return False, "核心不足"
        
        # 升级
        if path not in self.data["talents"]:
            self.data["talents"][path] = {}
        self.data["talents"][path][talent_id] = current_level + 1
        self.data["statistics"]["total_points_spent"] += 1
        
        # 检查是否解锁路线共鸣
        self._check_resonance(path)
        
        self.save()
        return True, f"{talent['name']} 升级到 {current_level + 1} 级"
    
    def upgrade_talent_max(self, path, talent_id):
        """直接升满天赋（消耗芯片）"""
        branch_id = self.find_talent_branch(path, talent_id)
        if not branch_id:
            return False, "天赋不存在"
        
        talent = TALENT_TREE[path]["branches"][branch_id]["talents"][talent_id]
        current_level = self.get_talent_level(path, talent_id)
        
        if current_level >= talent["max_level"]:
            return False, "已达最高等级"
        
        # 检查前置
        if "requires" in talent:
            req_level = self.get_talent_level(path, talent["requires"])
            req_talent = TALENT_TREE[path]["branches"][branch_id]["talents"][talent["requires"]]
            if req_level < req_talent["max_level"]:
                return False, f"需要先点满 {req_talent['name']}"
        
        # 消耗芯片
        if not self.spend_chips(3):
            return False, "芯片不足 (需要3)"
        
        # 直接满级
        if path not in self.data["talents"]:
            self.data["talents"][path] = {}
        points_gained = talent["max_level"] - current_level
        self.data["talents"][path][talent_id] = talent["max_level"]
        self.data["statistics"]["total_points_spent"] += points_gained
        
        self._check_resonance(path)
        self.save()
        return True, f"{talent['name']} 直接升满！"
    
    def _check_resonance(self, path):
        """检查是否解锁路线共鸣"""
        points = self.get_path_points(path)
        if points >= PATH_RESONANCE[path]["requires_points"]:
            self.data["resonance"][path] = True
    
    # ==================== 终极天赋 ====================
    
    def can_unlock_ultimate(self, path):
        """检查是否可以解锁路线终极"""
        if self.data["ultimates"].get(path, False):
            return False, "已解锁"
        
        # 检查是否有任意分支T4满级
        for branch_id, branch in TALENT_TREE[path]["branches"].items():
            for talent_id, talent in branch["talents"].items():
                if talent["tier"] == 4:
                    if self.get_talent_level(path, talent_id) >= talent["max_level"]:
                        return True, "可以解锁"
        
        return False, "需要任意T4天赋满级"
    
    def unlock_ultimate(self, path):
        """解锁路线终极"""
        can_unlock, msg = self.can_unlock_ultimate(path)
        if not can_unlock:
            return False, msg
        
        self.data["ultimates"][path] = True
        self.save()
        return True, f"解锁 {TALENT_TREE[path]['ultimate']['name']}！"
    
    def can_unlock_core(self, core_id):
        """检查是否可以解锁超限核心"""
        if self.data["ultimate_core"]:
            return False, "已选择超限核心"
        
        core = ULTIMATE_CORES.get(core_id)
        if not core:
            return False, "核心不存在"
        
        total_points = sum(self.get_path_points(p) for p in ["destruction", "guardian", "destiny"])
        if total_points < core["requires_points"]:
            return False, f"需要总计{core['requires_points']}点天赋"
        
        return True, "可以解锁"
    
    def unlock_core(self, core_id):
        """解锁超限核心"""
        can_unlock, msg = self.can_unlock_core(core_id)
        if not can_unlock:
            return False, msg
        
        self.data["ultimate_core"] = core_id
        self.save()
        return True, f"解锁 {ULTIMATE_CORES[core_id]['name']}！"
    
    # ==================== 统计查询 ====================
    
    def get_path_points(self, path):
        """获取路线已投入点数"""
        total = 0
        for talent_id, level in self.data["talents"].get(path, {}).items():
            total += level
        return total
    
    def get_total_points(self):
        """获取总投入点数"""
        return sum(self.get_path_points(p) for p in ["destruction", "guardian", "destiny"])
    
    def get_branch_progress(self, path, branch_id):
        """获取分支进度 (已点/总计)"""
        branch = TALENT_TREE[path]["branches"][branch_id]
        total = sum(t["max_level"] for t in branch["talents"].values())
        current = sum(self.get_talent_level(path, tid) for tid in branch["talents"])
        return current, total
    
    # ==================== 效果计算 ====================
    
    def calculate_effects(self):
        """计算所有天赋效果（用于应用到玩家）"""
        effects = {}
        
        for path_id, path_data in TALENT_TREE.items():
            for branch_id, branch in path_data["branches"].items():
                for talent_id, talent in branch["talents"].items():
                    level = self.get_talent_level(path_id, talent_id)
                    if level > 0:
                        for effect_key, effect_values in talent["effect"].items():
                            value = effect_values[level - 1]
                            if effect_key in effects:
                                effects[effect_key] += value
                            else:
                                effects[effect_key] = value
        
        # 应用超限核心加成
        if self.data["ultimate_core"] == "star_resonance":
            boost = ULTIMATE_CORES["star_resonance"]["effect"]["talent_boost"]
            for key in effects:
                effects[key] *= (1 + boost)
        
        # 添加终极效果
        for path_id in ["destruction", "guardian", "destiny"]:
            if self.data["ultimates"].get(path_id, False):
                ultimate = TALENT_TREE[path_id]["ultimate"]
                for eff_key, eff_val in ultimate["effect"].items():
                    effects[f"ultimate_{path_id}_{eff_key}"] = eff_val
        
        # 添加共鸣效果
        for path_id in ["destruction", "guardian", "destiny"]:
            if self.data["resonance"].get(path_id, False):
                resonance = PATH_RESONANCE[path_id]
                for eff_key, eff_val in resonance["effect"].items():
                    effects[f"resonance_{path_id}_{eff_key}"] = eff_val
        
        # 添加超限核心效果
        if self.data["ultimate_core"]:
            core = ULTIMATE_CORES[self.data["ultimate_core"]]
            for eff_key, eff_val in core["effect"].items():
                if eff_key != "talent_boost":  # 这个已经应用过了
                    effects[f"core_{eff_key}"] = eff_val
        
        return effects
    
    # ==================== 重置系统 ====================
    
    def reset_all(self):
        """重置所有天赋（消耗200核心）"""
        if self.cores < 200:
            return False, "核心不足 (需要200)"
        
        # 计算返还点数
        total_spent = self.data["statistics"]["total_cores_spent"]
        refund = int(total_spent * 0.8)  # 返还80%
        
        # 重置
        self.spend_cores(200)
        self.data["talents"] = {"destruction": {}, "guardian": {}, "destiny": {}}
        self.data["ultimates"] = {"destruction": False, "guardian": False, "destiny": False}
        self.data["resonance"] = {"destruction": False, "guardian": False, "destiny": False}
        self.data["awakened"] = []
        self.data["ultimate_core"] = None
        self.data["statistics"]["resets"] += 1
        
        # 返还核心
        self.add_cores(refund)
        
        self.save()
        return True, f"天赋已重置，返还 {refund} 核心"
    
    def reset_path(self, path):
        """重置单条路线（消耗50核心）"""
        if self.cores < 50:
            return False, "核心不足 (需要50)"
        
        # 计算该路线消耗
        path_spent = 0
        for talent_id, level in self.data["talents"].get(path, {}).items():
            branch_id = self.find_talent_branch(path, talent_id)
            talent = TALENT_TREE[path]["branches"][branch_id]["talents"][talent_id]
            for i in range(level):
                path_spent += talent["costs"][i]
        
        refund = int(path_spent * 0.8)
        
        # 重置
        self.spend_cores(50)
        self.data["talents"][path] = {}
        self.data["ultimates"][path] = False
        self.data["resonance"][path] = False
        self.data["awakened"] = [a for a in self.data["awakened"] if not a.startswith(path)]
        
        self.add_cores(refund)
        self.save()
        return True, f"{TALENT_TREE[path]['name']} 已重置，返还 {refund} 核心"


# 全局实例
talent_manager = TalentManager()
