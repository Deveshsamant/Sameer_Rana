from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import requests
import random
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class NewsRequest(BaseModel):
    category: str
    language: str = "en"

class GameState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    game_type: str
    state: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)

# News API Integration
@api_router.post("/news")
async def get_news(request: NewsRequest):
    """Fetch news articles by category"""
    try:
        # Map frontend categories to API categories
        category_map = {
            "sports": "sports",
            "esports": "technology",  # NewsData.io doesn't have esports, use tech
            "international": "world",
            "national": "domestic",
            "politics": "politics",
            "tech": "technology"
        }
        
        api_category = category_map.get(request.category, "general")
        api_key = os.environ.get('NEWS_API_KEY')
        
        url = f"https://newsdata.io/api/1/news?apikey={api_key}&category={api_category}&language={request.language}&size=10"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch news")
        
        data = response.json()
        articles = data.get('results', [])
        
        # Format articles for frontend
        formatted_articles = []
        for article in articles:
            formatted_articles.append({
                "id": article.get('article_id', str(uuid.uuid4())),
                "title": article.get('title', 'No title'),
                "description": article.get('description', 'No description available'),
                "url": article.get('link', ''),
                "image": article.get('image_url', ''),
                "source": article.get('source_name', 'Unknown'),
                "published": article.get('pubDate', ''),
                "category": request.category
            })
        
        return {"articles": formatted_articles, "status": "success"}
    
    except Exception as e:
        logging.error(f"News API error: {str(e)}")
        return {"articles": [], "status": "error", "message": str(e)}

# Tic Tac Toe Game
@api_router.post("/games/tictactoe/new")
async def new_tictactoe_game():
    """Start a new Tic Tac Toe game"""
    game_state = {
        "board": [""] * 9,
        "currentPlayer": "X",
        "winner": None,
        "gameOver": False
    }
    
    game = GameState(game_type="tictactoe", state=game_state)
    await db.games.insert_one(game.dict())
    
    return {"gameId": game.id, "state": game_state}

@api_router.post("/games/tictactoe/{game_id}/move")
async def make_tictactoe_move(game_id: str, move: Dict[str, int]):
    """Make a move in Tic Tac Toe"""
    game = await db.games.find_one({"id": game_id, "game_type": "tictactoe"})
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    state = game["state"]
    position = move["position"]
    
    if state["gameOver"] or state["board"][position] != "":
        raise HTTPException(status_code=400, detail="Invalid move")
    
    # Make move
    state["board"][position] = state["currentPlayer"]
    
    # Check for winner
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
        [0, 4, 8], [2, 4, 6]              # diagonals
    ]
    
    for combo in winning_combinations:
        if (state["board"][combo[0]] == state["board"][combo[1]] == 
            state["board"][combo[2]] != ""):
            state["winner"] = state["currentPlayer"]
            state["gameOver"] = True
            break
    
    # Check for tie
    if not state["gameOver"] and "" not in state["board"]:
        state["gameOver"] = True
        state["winner"] = "tie"
    
    # Switch player
    if not state["gameOver"]:
        state["currentPlayer"] = "O" if state["currentPlayer"] == "X" else "X"
    
    # Update game in database
    await db.games.update_one(
        {"id": game_id}, 
        {"$set": {"state": state}}
    )
    
    return {"state": state}

# Sudoku Game
def generate_sudoku():
    """Generate a simple Sudoku puzzle"""
    # Create a simple 4x4 Sudoku for demo
    puzzle = [
        [1, 0, 3, 0],
        [0, 3, 0, 1],
        [3, 0, 1, 0],
        [0, 1, 0, 3]
    ]
    solution = [
        [1, 2, 3, 4],
        [4, 3, 2, 1],
        [3, 4, 1, 2],
        [2, 1, 4, 3]
    ]
    return puzzle, solution

@api_router.post("/games/sudoku/new")
async def new_sudoku_game():
    """Start a new Sudoku game"""
    puzzle, solution = generate_sudoku()
    
    game_state = {
        "puzzle": puzzle,
        "solution": solution,
        "currentGrid": [row[:] for row in puzzle],
        "completed": False,
        "errors": 0
    }
    
    game = GameState(game_type="sudoku", state=game_state)
    await db.games.insert_one(game.dict())
    
    return {"gameId": game.id, "state": game_state}

@api_router.post("/games/sudoku/{game_id}/move")
async def make_sudoku_move(game_id: str, move: Dict[str, Any]):
    """Make a move in Sudoku"""
    game = await db.games.find_one({"id": game_id, "game_type": "sudoku"})
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    state = game["state"]
    row, col, value = move["row"], move["col"], move["value"]
    
    # Check if move is valid (not a pre-filled cell)
    if state["puzzle"][row][col] != 0:
        raise HTTPException(status_code=400, detail="Cannot modify pre-filled cell")
    
    # Make move
    state["currentGrid"][row][col] = value
    
    # Check if move is correct
    if value != 0 and value != state["solution"][row][col]:
        state["errors"] += 1
    
    # Check if puzzle is completed
    if state["currentGrid"] == state["solution"]:
        state["completed"] = True
    
    # Update game in database
    await db.games.update_one(
        {"id": game_id}, 
        {"$set": {"state": state}}
    )
    
    return {"state": state}

# Snakes and Ladders Game
def create_snakes_and_ladders_board():
    """Create a Snakes and Ladders board with snakes and ladders"""
    snakes = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
    ladders = {1: 38, 4: 14, 9: 21, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 100}
    return snakes, ladders

@api_router.post("/games/snakeladder/new")
async def new_snakeladder_game():
    """Start a new Snakes and Ladders game"""
    snakes, ladders = create_snakes_and_ladders_board()
    
    game_state = {
        "playerPosition": 0,
        "snakes": snakes,
        "ladders": ladders,
        "gameWon": False,
        "lastRoll": 0,
        "moves": 0
    }
    
    game = GameState(game_type="snakeladder", state=game_state)
    await db.games.insert_one(game.dict())
    
    return {"gameId": game.id, "state": game_state}

@api_router.post("/games/snakeladder/{game_id}/roll")
async def roll_dice_snakeladder(game_id: str):
    """Roll dice in Snakes and Ladders"""
    game = await db.games.find_one({"id": game_id, "game_type": "snakeladder"})
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    state = game["state"]
    
    if state["gameWon"]:
        raise HTTPException(status_code=400, detail="Game already won")
    
    # Roll dice
    dice_roll = random.randint(1, 6)
    state["lastRoll"] = dice_roll
    state["moves"] += 1
    
    # Move player
    new_position = state["playerPosition"] + dice_roll
    
    # Check if player wins
    if new_position >= 100:
        state["playerPosition"] = 100
        state["gameWon"] = True
    else:
        state["playerPosition"] = new_position
        
        # Check for snakes
        if new_position in state["snakes"]:
            state["playerPosition"] = state["snakes"][new_position]
        
        # Check for ladders
        elif new_position in state["ladders"]:
            state["playerPosition"] = state["ladders"][new_position]
    
    # Update game in database
    await db.games.update_one(
        {"id": game_id}, 
        {"$set": {"state": state}}
    )
    
    return {"state": state}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()