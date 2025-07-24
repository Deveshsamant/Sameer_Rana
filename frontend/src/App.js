import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// News Component
const NewsSection = () => {
  const [articles, setArticles] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('sports');
  const [loading, setLoading] = useState(false);

  const categories = [
    { key: 'sports', label: 'Sports' },
    { key: 'esports', label: 'Esports' },
    { key: 'international', label: 'International' },
    { key: 'national', label: 'National' },
    { key: 'politics', label: 'Politics' },
    { key: 'tech', label: 'Tech' }
  ];

  const fetchNews = async (category) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/news`, {
        category: category
      });
      setArticles(response.data.articles || []);
    } catch (error) {
      console.error('Error fetching news:', error);
      setArticles([]);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchNews(selectedCategory);
  }, [selectedCategory]);

  return (
    <div className="news-section">
      <h2>📰 Latest News</h2>
      
      <div className="category-buttons">
        {categories.map(cat => (
          <button
            key={cat.key}
            onClick={() => setSelectedCategory(cat.key)}
            className={`category-btn ${selectedCategory === cat.key ? 'active' : ''}`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="loading">Loading news...</div>
      ) : (
        <div className="articles-grid">
          {articles.length > 0 ? articles.map((article, index) => (
            <div key={article.id || index} className="article-card">
              {article.image && (
                <img src={article.image} alt={article.title} className="article-image" />
              )}
              <div className="article-content">
                <h3 className="article-title">{article.title}</h3>
                <p className="article-description">
                  {article.description && article.description.length > 150 
                    ? `${article.description.substring(0, 150)}...` 
                    : article.description}
                </p>
                <div className="article-meta">
                  <span className="article-source">{article.source}</span>
                  <a href={article.url} target="_blank" rel="noopener noreferrer" className="read-more">
                    Read More →
                  </a>
                </div>
              </div>
            </div>
          )) : (
            <div className="no-articles">No articles found for this category.</div>
          )}
        </div>
      )}
    </div>
  );
};

// Tic Tac Toe Game
const TicTacToe = () => {
  const [gameId, setGameId] = useState(null);
  const [board, setBoard] = useState(Array(9).fill(''));
  const [currentPlayer, setCurrentPlayer] = useState('X');
  const [winner, setWinner] = useState(null);
  const [gameOver, setGameOver] = useState(false);

  const startNewGame = async () => {
    try {
      const response = await axios.post(`${API}/games/tictactoe/new`);
      const { gameId, state } = response.data;
      setGameId(gameId);
      setBoard(state.board);
      setCurrentPlayer(state.currentPlayer);
      setWinner(state.winner);
      setGameOver(state.gameOver);
    } catch (error) {
      console.error('Error starting new game:', error);
    }
  };

  const makeMove = async (position) => {
    if (!gameId || gameOver || board[position] !== '') return;

    try {
      const response = await axios.post(`${API}/games/tictactoe/${gameId}/move`, {
        position: position
      });
      
      const { state } = response.data;
      setBoard(state.board);
      setCurrentPlayer(state.currentPlayer);
      setWinner(state.winner);
      setGameOver(state.gameOver);
    } catch (error) {
      console.error('Error making move:', error);
    }
  };

  useEffect(() => {
    startNewGame();
  }, []);

  return (
    <div className="game-container">
      <h3>🎮 Tic Tac Toe</h3>
      
      <div className="game-info">
        {gameOver ? (
          <div className="game-result">
            {winner === 'tie' ? "It's a tie! 🤝" : `Player ${winner} wins! 🏆`}
          </div>
        ) : (
          <div className="current-player">Current Player: {currentPlayer}</div>
        )}
      </div>

      <div className="tic-tac-toe-board">
        {board.map((cell, index) => (
          <button
            key={index}
            className="tic-tac-toe-cell"
            onClick={() => makeMove(index)}
            disabled={gameOver || cell !== ''}
          >
            {cell}
          </button>
        ))}
      </div>

      <button onClick={startNewGame} className="new-game-btn">
        New Game
      </button>
    </div>
  );
};

// Sudoku Game
const Sudoku = () => {
  const [gameId, setGameId] = useState(null);
  const [puzzle, setPuzzle] = useState([]);
  const [currentGrid, setCurrentGrid] = useState([]);
  const [completed, setCompleted] = useState(false);
  const [errors, setErrors] = useState(0);

  const startNewGame = async () => {
    try {
      const response = await axios.post(`${API}/games/sudoku/new`);
      const { gameId, state } = response.data;
      setGameId(gameId);
      setPuzzle(state.puzzle);
      setCurrentGrid(state.currentGrid);
      setCompleted(state.completed);
      setErrors(state.errors);
    } catch (error) {
      console.error('Error starting new Sudoku game:', error);
    }
  };

  const makeMove = async (row, col, value) => {
    if (!gameId || completed || puzzle[row][col] !== 0) return;

    try {
      const response = await axios.post(`${API}/games/sudoku/${gameId}/move`, {
        row, col, value: parseInt(value) || 0
      });
      
      const { state } = response.data;
      setCurrentGrid(state.currentGrid);
      setCompleted(state.completed);
      setErrors(state.errors);
    } catch (error) {
      console.error('Error making Sudoku move:', error);
    }
  };

  useEffect(() => {
    startNewGame();
  }, []);

  return (
    <div className="game-container">
      <h3>🧩 Sudoku (4x4)</h3>
      
      <div className="game-info">
        <div>Errors: {errors}</div>
        {completed && <div className="game-result">Puzzle Completed! 🎉</div>}
      </div>

      <div className="sudoku-grid">
        {currentGrid.map((row, rowIndex) => (
          <div key={rowIndex} className="sudoku-row">
            {row.map((cell, colIndex) => (
              <input
                key={`${rowIndex}-${colIndex}`}
                type="number"
                min="1"
                max="4"
                value={cell || ''}
                onChange={(e) => makeMove(rowIndex, colIndex, e.target.value)}
                className={`sudoku-cell ${puzzle[rowIndex][colIndex] !== 0 ? 'prefilled' : ''}`}
                disabled={puzzle[rowIndex][colIndex] !== 0 || completed}
              />
            ))}
          </div>
        ))}
      </div>

      <button onClick={startNewGame} className="new-game-btn">
        New Game
      </button>
    </div>
  );
};

// Snakes and Ladders Game
const SnakesAndLadders = () => {
  const [gameId, setGameId] = useState(null);
  const [playerPosition, setPlayerPosition] = useState(0);
  const [gameWon, setGameWon] = useState(false);
  const [lastRoll, setLastRoll] = useState(0);
  const [moves, setMoves] = useState(0);

  const startNewGame = async () => {
    try {
      const response = await axios.post(`${API}/games/snakeladder/new`);
      const { gameId, state } = response.data;
      setGameId(gameId);
      setPlayerPosition(state.playerPosition);
      setGameWon(state.gameWon);
      setLastRoll(state.lastRoll);
      setMoves(state.moves);
    } catch (error) {
      console.error('Error starting new Snakes and Ladders game:', error);
    }
  };

  const rollDice = async () => {
    if (!gameId || gameWon) return;

    try {
      const response = await axios.post(`${API}/games/snakeladder/${gameId}/roll`);
      const { state } = response.data;
      setPlayerPosition(state.playerPosition);
      setGameWon(state.gameWon);
      setLastRoll(state.lastRoll);
      setMoves(state.moves);
    } catch (error) {
      console.error('Error rolling dice:', error);
    }
  };

  useEffect(() => {
    startNewGame();
  }, []);

  return (
    <div className="game-container">
      <h3>🐍 Snakes and Ladders</h3>
      
      <div className="game-info">
        <div>Position: {playerPosition}/100</div>
        <div>Moves: {moves}</div>
        {lastRoll > 0 && <div>Last Roll: {lastRoll}</div>}
        {gameWon && <div className="game-result">You Won! 🏆</div>}
      </div>

      <div className="snakes-ladders-board">
        <div className="position-display">
          Current Position: {playerPosition}
        </div>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${playerPosition}%` }}
          ></div>
        </div>
      </div>

      <button 
        onClick={rollDice} 
        className="roll-dice-btn"
        disabled={gameWon}
      >
        🎲 Roll Dice
      </button>

      <button onClick={startNewGame} className="new-game-btn">
        New Game
      </button>
    </div>
  );
};

// Main App Component
const App = () => {
  const [activeSection, setActiveSection] = useState('news');

  const sections = [
    { key: 'news', label: '📰 News', component: NewsSection },
    { key: 'tictactoe', label: '⭕ Tic Tac Toe', component: TicTacToe },
    { key: 'sudoku', label: '🧩 Sudoku', component: Sudoku },
    { key: 'snakeladder', label: '🐍 Snakes & Ladders', component: SnakesAndLadders }
  ];

  const ActiveComponent = sections.find(s => s.key === activeSection)?.component || NewsSection;

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎯 News & Games Hub</h1>
        <nav className="nav-tabs">
          {sections.map(section => (
            <button
              key={section.key}
              onClick={() => setActiveSection(section.key)}
              className={`nav-tab ${activeSection === section.key ? 'active' : ''}`}
            >
              {section.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="app-main">
        <ActiveComponent />
      </main>
    </div>
  );
};

export default App;