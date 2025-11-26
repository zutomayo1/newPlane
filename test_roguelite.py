#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
肉鸽系统完整验证脚本
Testing all roguelite systems end-to-end
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test 1: Module imports"""
    print("[TEST 1] Module imports...")
    try:
        import pygame
        pygame.init()
        pygame.display.set_mode((100, 100))
        
        import config
        from utils import sound_mgr, log_error
        from sprites import Player, Enemy, Bullet
        from roguelite import UpgradeManager, ExperienceSystem, BuffProcessor, BUFF_LIBRARY
        
        print("[PASS] All modules imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_buff_library():
    """Test 2: Buff library integrity"""
    print("\n[TEST 2] Buff library integrity...")
    try:
        from roguelite import BUFF_LIBRARY
        
        required_fields = {'name', 'desc', 'rarity', 'type', 'apply'}
        valid_rarities = {0, 1, 2, 3}
        
        buff_count = 0
        for buff_id, buff_data in BUFF_LIBRARY.items():
            # Check fields
            if not all(field in buff_data for field in required_fields):
                raise ValueError(f"Buff '{buff_id}' missing fields")
            
            # Check rarity
            if buff_data['rarity'] not in valid_rarities:
                raise ValueError(f"Buff '{buff_id}' invalid rarity")
            
            # Check apply is callable
            if not callable(buff_data['apply']):
                raise ValueError(f"Buff '{buff_id}' apply is not callable")
            
            buff_count += 1
        
        print(f"[PASS] BUFF_LIBRARY validated: {buff_count} buffs")
        rarity_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for b in BUFF_LIBRARY.values():
            rarity_counts[b['rarity']] += 1
        
        print(f"       Common: {rarity_counts[0]}")
        print(f"       Rare: {rarity_counts[1]}")
        print(f"       Epic: {rarity_counts[2]}")
        print(f"       Legendary: {rarity_counts[3]}")
        return True
    except Exception as e:
        print(f"[FAIL] Buff library error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_player_initialization():
    """Test 3: Player class initialization"""
    print("\n[TEST 3] Player initialization...")
    try:
        import pygame
        pygame.init()
        pygame.display.set_mode((100, 100))
        
        from sprites import Player
        
        player = Player("striker")
        
        # Check basic attributes
        assert player.hp > 0, "Player HP should be > 0"
        assert player.max_hp > 0, "Player max_hp should be > 0"
        assert player.damage > 0, "Player damage should be > 0"
        assert player.level == 1, "Player should start at level 1"
        
        # Check roguelite attributes
        assert hasattr(player, 'pickup_range'), "Missing pickup_range"
        assert hasattr(player, 'execute_threshold'), "Missing execute_threshold"
        assert hasattr(player, 'has_regen'), "Missing has_regen flag"
        assert hasattr(player, 'has_frost'), "Missing has_frost flag"
        
        print(f"[PASS] Player initialized correctly")
        print(f"       HP: {player.hp}/{player.max_hp}")
        print(f"       DMG: {player.damage}")
        print(f"       Level: {player.level}")
        return True
    except Exception as e:
        print(f"[FAIL] Player initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_roguelite_systems():
    """Test 4: Roguelite systems initialization"""
    print("\n[TEST 4] Roguelite systems initialization...")
    try:
        import pygame
        pygame.init()
        pygame.display.set_mode((100, 100))
        
        from sprites import Player
        
        player = Player("striker")
        player.init_roguelite_systems()
        
        assert player.upgrade_manager is not None, "upgrade_manager not initialized"
        assert player.exp_system is not None, "exp_system not initialized"
        assert player.buff_processor is not None, "buff_processor not initialized"
        
        print(f"[PASS] All roguelite systems initialized")
        print(f"       upgrade_manager: OK")
        print(f"       exp_system: OK")
        print(f"       buff_processor: OK")
        return True
    except Exception as e:
        print(f"[FAIL] Roguelite systems error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_xp_system():
    """Test 5: XP and leveling"""
    print("\n[TEST 5] XP and leveling system...")
    try:
        import pygame
        pygame.init()
        pygame.display.set_mode((100, 100))
        
        from sprites import Player
        
        player = Player("striker")
        player.init_roguelite_systems()
        
        initial_level = player.level
        initial_xp = player.xp
        
        # Add XP
        player.add_xp(50)
        assert player.xp >= 50, "XP not added correctly"
        
        # Trigger level up
        player.add_xp(100)
        assert player.level > initial_level, "Level not increased"
        
        # Check upgrade options
        assert player.upgrade_manager.upgrade_choice is not None, "No upgrade options"
        assert len(player.upgrade_manager.upgrade_choice) == 3, "Should have 3 upgrade options"
        
        print(f"[PASS] XP system working correctly")
        print(f"       Initial: Level {initial_level}, XP 0")
        print(f"       After 150 XP: Level {player.level}, XP {player.xp}")
        print(f"       Upgrade options: {player.upgrade_manager.upgrade_choice}")
        return True
    except Exception as e:
        print(f"[FAIL] XP system error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_buff_application():
    """Test 6: Buff application"""
    print("\n[TEST 6] Buff application...")
    try:
        import pygame
        pygame.init()
        pygame.display.set_mode((100, 100))
        
        from sprites import Player
        
        player = Player("striker")
        player.init_roguelite_systems()
        
        # Test damage buff
        initial_dmg = player.damage
        result = player.apply_buff("dmg")
        assert result == True, "Buff application failed"
        assert player.damage > initial_dmg, "Damage not increased"
        
        # Test HP buff
        initial_max_hp = player.max_hp
        player.apply_buff("hp_max")
        assert player.max_hp > initial_max_hp, "Max HP not increased"
        
        # Test passive flag
        player.apply_buff("regen")
        assert player.has_regen == True, "Regen flag not set"
        
        print(f"[PASS] Buff application working correctly")
        print(f"       dmg: {initial_dmg} -> {player.damage}")
        print(f"       hp_max: {initial_max_hp} -> {player.max_hp}")
        print(f"       Passive flags working")
        return True
    except Exception as e:
        print(f"[FAIL] Buff application error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_game_loop_simulation():
    """Test 7: Game loop simulation"""
    print("\n[TEST 7] Game loop simulation...")
    try:
        import pygame
        pygame.init()
        pygame.display.set_mode((100, 100))
        
        from sprites import Player, Enemy
        
        player = Player("striker")
        player.init_roguelite_systems()
        
        # Simulate combat
        for _ in range(3):
            enemy = Enemy("chaser")
            enemy.hp -= player.damage
            
            if enemy.hp <= 0:
                player.add_xp(5)
        
        # Update passive effects
        player.update_buffs()
        
        print(f"[PASS] Game loop simulation successful")
        print(f"       Final level: {player.level}")
        print(f"       Final XP: {player.xp}/{player.next_level_xp}")
        return True
    except Exception as e:
        print(f"[FAIL] Game loop simulation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Roguelite System Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_buff_library,
        test_player_initialization,
        test_roguelite_systems,
        test_xp_system,
        test_buff_application,
        test_game_loop_simulation,
    ]
    
    results = []
    for test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"[ERROR] {test_func.__name__}: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! System is ready for production.")
        return 0
    else:
        print(f"[WARNING] {total - passed} test(s) failed. Please review.")
        return 1

if __name__ == "__main__":
    exit(main())
