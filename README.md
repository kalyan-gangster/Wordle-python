# Python Wordle Clone

A lightweight, terminal-based clone of the popular word-guessing game **Wordle**, built entirely in Python. This project mimics the original game mechanics, including color-coded feedback and a daily-resetting word logic (or random selection).

## 🚀 Features

* **Classic Gameplay**: 6 attempts to guess a hidden 5-letter word.
* **Color-Coded Feedback**: 
    * 🟩 **Green**: Correct letter, correct spot.
    * 🟨 **Yellow**: Correct letter, wrong spot.
    * ⬛ **Gray**: Letter not in the word.
* **Input Validation**: Ensures only 5-letter English words are accepted.
* **Win/Loss Stats**: Displays the hidden word upon game over.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kalyan-gangster/Wordle-python.git
    cd python-wordle
    ```

2.  **Ensure you have Python installed:**
    This game requires Python 3.6 or higher. Check your version with:
    ```bash
    python --version
    ```

3.   **Install dependencies:**
    If your version uses libraries like `pygame`
    ```bash
    pip install pygame
    ```

## 🎮 How to Play

Run the game directly from your terminal:

```bash
python wordle.py
