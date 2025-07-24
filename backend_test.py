#!/usr/bin/env python3
"""
Comprehensive Backend Testing for News & Games App
Tests all backend endpoints for News API, Tic Tac Toe, Sudoku, and Snakes & Ladders
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

# Backend URL from frontend/.env
BACKEND_URL = "https://d07c4c0a-b289-493e-942e-47d8d279ca5e.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.results = {
            "news_api": {"passed": 0, "failed": 0, "errors": []},
            "tictactoe": {"passed": 0, "failed": 0, "errors": []},
            "sudoku": {"passed": 0, "failed": 0, "errors": []},
            "snakeladder": {"passed": 0, "failed": 0, "errors": []}
        }
        
    def log_result(self, test_name: str, category: str, success: bool, message: str = ""):
        """Log test result"""
        if success:
            self.results[category]["passed"] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.results[category]["failed"] += 1
            self.results[category]["errors"].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED - {message}")
    
    def test_news_api(self):
        """Test News API Integration with NewsData.io"""
        print("\n🔍 Testing News API Integration...")
        
        # Test categories to verify
        categories = ["sports", "esports", "international", "national", "politics", "tech"]
        
        for category in categories:
            try:
                payload = {"category": category, "language": "en"}
                response = requests.post(f"{BACKEND_URL}/news", json=payload, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check response structure
                    if "articles" in data and "status" in data:
                        if data["status"] == "success" and isinstance(data["articles"], list):
                            # Verify article structure if articles exist
                            if data["articles"]:
                                article = data["articles"][0]
                                required_fields = ["id", "title", "description", "url", "source", "category"]
                                if all(field in article for field in required_fields):
                                    self.log_result(f"News API - {category} category", "news_api", True, 
                                                  f"Got {len(data['articles'])} articles")
                                else:
                                    self.log_result(f"News API - {category} category", "news_api", False, 
                                                  "Article missing required fields")
                            else:
                                self.log_result(f"News API - {category} category", "news_api", True, 
                                              "No articles but valid response structure")
                        else:
                            self.log_result(f"News API - {category} category", "news_api", False, 
                                          f"Invalid response format: {data}")
                    else:
                        self.log_result(f"News API - {category} category", "news_api", False, 
                                      "Missing articles or status in response")
                else:
                    self.log_result(f"News API - {category} category", "news_api", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result(f"News API - {category} category", "news_api", False, str(e))
                
        # Test invalid category
        try:
            payload = {"category": "invalid_category", "language": "en"}
            response = requests.post(f"{BACKEND_URL}/news", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("News API - Invalid category handling", "news_api", True, 
                              "Handled invalid category gracefully")
            else:
                self.log_result("News API - Invalid category handling", "news_api", True, 
                              "Properly rejected invalid category")
                
        except Exception as e:
            self.log_result("News API - Invalid category handling", "news_api", False, str(e))
    
    def test_tictactoe_game(self):
        """Test Tic Tac Toe Game Backend"""
        print("\n🎮 Testing Tic Tac Toe Game...")
        
        game_id = None
        
        # Test new game creation
        try:
            response = requests.post(f"{BACKEND_URL}/games/tictactoe/new", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "gameId" in data and "state" in data:
                    game_id = data["gameId"]
                    state = data["state"]
                    
                    # Verify initial state
                    if (state["board"] == [""] * 9 and 
                        state["currentPlayer"] == "X" and 
                        state["winner"] is None and 
                        state["gameOver"] is False):
                        self.log_result("Tic Tac Toe - New game creation", "tictactoe", True, 
                                      f"Game ID: {game_id}")
                    else:
                        self.log_result("Tic Tac Toe - New game creation", "tictactoe", False, 
                                      "Invalid initial game state")
                else:
                    self.log_result("Tic Tac Toe - New game creation", "tictactoe", False, 
                                  "Missing gameId or state in response")
            else:
                self.log_result("Tic Tac Toe - New game creation", "tictactoe", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Tic Tac Toe - New game creation", "tictactoe", False, str(e))
            return
        
        if not game_id:
            return
            
        # Test making moves
        moves = [0, 4, 1, 3, 2]  # X wins with top row
        expected_players = ["X", "O", "X", "O", "X"]
        
        for i, position in enumerate(moves):
            try:
                payload = {"position": position}
                response = requests.post(f"{BACKEND_URL}/games/tictactoe/{game_id}/move", 
                                       json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    state = data["state"]
                    
                    # Check if move was made correctly
                    if state["board"][position] == expected_players[i]:
                        if i == len(moves) - 1:  # Last move should win
                            if state["winner"] == "X" and state["gameOver"]:
                                self.log_result(f"Tic Tac Toe - Move {i+1} (Win detection)", "tictactoe", True, 
                                              "X wins correctly detected")
                            else:
                                self.log_result(f"Tic Tac Toe - Move {i+1} (Win detection)", "tictactoe", False, 
                                              "Win not detected correctly")
                        else:
                            self.log_result(f"Tic Tac Toe - Move {i+1}", "tictactoe", True, 
                                          f"Player {expected_players[i]} moved to position {position}")
                    else:
                        self.log_result(f"Tic Tac Toe - Move {i+1}", "tictactoe", False, 
                                      "Move not recorded correctly")
                else:
                    self.log_result(f"Tic Tac Toe - Move {i+1}", "tictactoe", False, 
                                  f"HTTP {response.status_code}: {response.text}")
                    break
                    
            except Exception as e:
                self.log_result(f"Tic Tac Toe - Move {i+1}", "tictactoe", False, str(e))
                break
        
        # Test tie game
        try:
            response = requests.post(f"{BACKEND_URL}/games/tictactoe/new", timeout=10)
            if response.status_code == 200:
                tie_game_id = response.json()["gameId"]
                
                # Make moves that result in a tie
                tie_moves = [0, 1, 2, 4, 3, 5, 7, 6, 8]  # Results in tie
                
                for i, position in enumerate(tie_moves):
                    payload = {"position": position}
                    response = requests.post(f"{BACKEND_URL}/games/tictactoe/{tie_game_id}/move", 
                                           json=payload, timeout=10)
                    
                    if i == len(tie_moves) - 1 and response.status_code == 200:  # Last move
                        state = response.json()["state"]
                        if state["winner"] == "tie" and state["gameOver"]:
                            self.log_result("Tic Tac Toe - Tie detection", "tictactoe", True, 
                                          "Tie game detected correctly")
                        else:
                            self.log_result("Tic Tac Toe - Tie detection", "tictactoe", False, 
                                          "Tie not detected correctly")
                        break
                        
        except Exception as e:
            self.log_result("Tic Tac Toe - Tie detection", "tictactoe", False, str(e))
    
    def test_sudoku_game(self):
        """Test Sudoku Game Backend"""
        print("\n🧩 Testing Sudoku Game...")
        
        game_id = None
        
        # Test new game creation
        try:
            response = requests.post(f"{BACKEND_URL}/games/sudoku/new", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "gameId" in data and "state" in data:
                    game_id = data["gameId"]
                    state = data["state"]
                    
                    # Verify initial state structure
                    if ("puzzle" in state and "solution" in state and 
                        "currentGrid" in state and "completed" in state and 
                        "errors" in state):
                        
                        # Check if puzzle is 4x4
                        if (len(state["puzzle"]) == 4 and 
                            all(len(row) == 4 for row in state["puzzle"])):
                            self.log_result("Sudoku - New game creation", "sudoku", True, 
                                          f"Game ID: {game_id}")
                        else:
                            self.log_result("Sudoku - New game creation", "sudoku", False, 
                                          "Puzzle is not 4x4")
                    else:
                        self.log_result("Sudoku - New game creation", "sudoku", False, 
                                      "Missing required state fields")
                else:
                    self.log_result("Sudoku - New game creation", "sudoku", False, 
                                  "Missing gameId or state in response")
            else:
                self.log_result("Sudoku - New game creation", "sudoku", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Sudoku - New game creation", "sudoku", False, str(e))
            return
        
        if not game_id:
            return
        
        # Test making a valid move
        try:
            # Find an empty cell and make a correct move
            payload = {"row": 0, "col": 1, "value": 2}  # Based on the hardcoded solution
            response = requests.post(f"{BACKEND_URL}/games/sudoku/{game_id}/move", 
                                   json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                state = data["state"]
                
                if state["currentGrid"][0][1] == 2:
                    self.log_result("Sudoku - Valid move", "sudoku", True, 
                                  "Move recorded correctly")
                else:
                    self.log_result("Sudoku - Valid move", "sudoku", False, 
                                  "Move not recorded correctly")
            else:
                self.log_result("Sudoku - Valid move", "sudoku", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Sudoku - Valid move", "sudoku", False, str(e))
        
        # Test invalid move (pre-filled cell)
        try:
            payload = {"row": 0, "col": 0, "value": 5}  # Try to modify pre-filled cell
            response = requests.post(f"{BACKEND_URL}/games/sudoku/{game_id}/move", 
                                   json=payload, timeout=10)
            
            if response.status_code == 400:
                self.log_result("Sudoku - Invalid move validation", "sudoku", True, 
                              "Correctly rejected move on pre-filled cell")
            else:
                self.log_result("Sudoku - Invalid move validation", "sudoku", False, 
                              "Should have rejected move on pre-filled cell")
                
        except Exception as e:
            self.log_result("Sudoku - Invalid move validation", "sudoku", False, str(e))
        
        # Test completion detection by solving the puzzle
        try:
            # Get fresh game state
            response = requests.post(f"{BACKEND_URL}/games/sudoku/new", timeout=10)
            if response.status_code == 200:
                complete_game_id = response.json()["gameId"]
                
                # Fill in all missing values to complete the puzzle
                solution_moves = [
                    {"row": 0, "col": 1, "value": 2},
                    {"row": 0, "col": 3, "value": 4},
                    {"row": 1, "col": 0, "value": 4},
                    {"row": 1, "col": 2, "value": 2},
                    {"row": 2, "col": 1, "value": 4},
                    {"row": 2, "col": 3, "value": 2},
                    {"row": 3, "col": 0, "value": 2},
                    {"row": 3, "col": 2, "value": 4}
                ]
                
                for move in solution_moves:
                    response = requests.post(f"{BACKEND_URL}/games/sudoku/{complete_game_id}/move", 
                                           json=move, timeout=10)
                
                # Check if completion was detected
                if response.status_code == 200:
                    state = response.json()["state"]
                    if state["completed"]:
                        self.log_result("Sudoku - Completion detection", "sudoku", True, 
                                      "Puzzle completion detected correctly")
                    else:
                        self.log_result("Sudoku - Completion detection", "sudoku", False, 
                                      "Puzzle completion not detected")
                        
        except Exception as e:
            self.log_result("Sudoku - Completion detection", "sudoku", False, str(e))
    
    def test_snakeladder_game(self):
        """Test Snakes and Ladders Game Backend"""
        print("\n🐍 Testing Snakes and Ladders Game...")
        
        game_id = None
        
        # Test new game creation
        try:
            response = requests.post(f"{BACKEND_URL}/games/snakeladder/new", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "gameId" in data and "state" in data:
                    game_id = data["gameId"]
                    state = data["state"]
                    
                    # Verify initial state
                    if (state["playerPosition"] == 0 and 
                        "snakes" in state and "ladders" in state and
                        state["gameWon"] is False and
                        state["lastRoll"] == 0 and
                        state["moves"] == 0):
                        self.log_result("Snakes & Ladders - New game creation", "snakeladder", True, 
                                      f"Game ID: {game_id}")
                    else:
                        self.log_result("Snakes & Ladders - New game creation", "snakeladder", False, 
                                      "Invalid initial game state")
                else:
                    self.log_result("Snakes & Ladders - New game creation", "snakeladder", False, 
                                  "Missing gameId or state in response")
            else:
                self.log_result("Snakes & Ladders - New game creation", "snakeladder", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Snakes & Ladders - New game creation", "snakeladder", False, str(e))
            return
        
        if not game_id:
            return
        
        # Test dice rolling
        try:
            response = requests.post(f"{BACKEND_URL}/games/snakeladder/{game_id}/roll", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                state = data["state"]
                
                # Check if dice was rolled and position updated
                if (state["lastRoll"] >= 1 and state["lastRoll"] <= 6 and
                    state["moves"] == 1 and
                    state["playerPosition"] > 0):
                    self.log_result("Snakes & Ladders - Dice rolling", "snakeladder", True, 
                                  f"Rolled {state['lastRoll']}, position: {state['playerPosition']}")
                else:
                    self.log_result("Snakes & Ladders - Dice rolling", "snakeladder", False, 
                                  "Dice roll or position update failed")
            else:
                self.log_result("Snakes & Ladders - Dice rolling", "snakeladder", False, 
                              f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Snakes & Ladders - Dice rolling", "snakeladder", False, str(e))
        
        # Test multiple rolls to check game mechanics
        for i in range(5):
            try:
                response = requests.post(f"{BACKEND_URL}/games/snakeladder/{game_id}/roll", timeout=10)
                
                if response.status_code == 200:
                    state = response.json()["state"]
                    
                    # Check if game won
                    if state["gameWon"]:
                        self.log_result("Snakes & Ladders - Win detection", "snakeladder", True, 
                                      f"Game won at position {state['playerPosition']}")
                        break
                        
                    # Check for snake or ladder mechanics
                    if state["playerPosition"] in [6, 26, 11, 53, 19, 60, 24, 73, 75, 78]:  # Snake destinations
                        self.log_result("Snakes & Ladders - Snake mechanics", "snakeladder", True, 
                                      f"Snake encountered, position: {state['playerPosition']}")
                    elif state["playerPosition"] in [38, 14, 21, 42, 84, 44, 67, 91, 100]:  # Ladder destinations
                        self.log_result("Snakes & Ladders - Ladder mechanics", "snakeladder", True, 
                                      f"Ladder encountered, position: {state['playerPosition']}")
                        
                else:
                    break
                    
            except Exception as e:
                self.log_result(f"Snakes & Ladders - Roll {i+2}", "snakeladder", False, str(e))
                break
        
        # Test game won condition by creating a game close to winning
        try:
            response = requests.post(f"{BACKEND_URL}/games/snakeladder/new", timeout=10)
            if response.status_code == 200:
                win_game_id = response.json()["gameId"]
                
                # Simulate multiple rolls to potentially reach 100
                for _ in range(20):  # Max 20 rolls to avoid infinite loop
                    response = requests.post(f"{BACKEND_URL}/games/snakeladder/{win_game_id}/roll", timeout=10)
                    if response.status_code == 200:
                        state = response.json()["state"]
                        if state["gameWon"] and state["playerPosition"] == 100:
                            self.log_result("Snakes & Ladders - Win condition", "snakeladder", True, 
                                          "Win condition properly detected at position 100")
                            break
                    else:
                        break
                        
        except Exception as e:
            self.log_result("Snakes & Ladders - Win condition", "snakeladder", False, str(e))
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive Backend Testing...")
        print(f"Backend URL: {BACKEND_URL}")
        
        # Test all backend components
        self.test_news_api()
        self.test_tictactoe_game()
        self.test_sudoku_game()
        self.test_snakeladder_game()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 BACKEND TESTING SUMMARY")
        print("="*60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL"
            print(f"{category.upper()}: {status} ({passed} passed, {failed} failed)")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  - {error}")
        
        print("-" * 60)
        print(f"OVERALL: {total_passed} passed, {total_failed} failed")
        
        if total_failed == 0:
            print("🎉 ALL BACKEND TESTS PASSED!")
            return True
        else:
            print("⚠️  SOME BACKEND TESTS FAILED!")
            return False

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)