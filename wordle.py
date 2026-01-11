
import pygame
import random
import os
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 800
SCREEN_TITLE = "Wordle in Python"
FPS = 60

# Colors (NYT Dark Theme)
COLOR_BG = (18, 18, 19)
COLOR_EMPTY = (58, 58, 60)
COLOR_FILLED_BORDER = (86, 87, 88) 
COLOR_CORRECT = (83, 141, 78)       # Green
COLOR_PRESENT = (181, 159, 59)      # Yellow
COLOR_ABSENT = (58, 58, 60)         # Gray
COLOR_TEXT = (255, 255, 255)
COLOR_KEY_BG = (129, 131, 132)
COLOR_OVERLAY = (0, 0, 0, 128)

# Game Settings
GRID_ROWS = 6
GRID_COLS = 5
TILE_SIZE = 60
TILE_PADDING = 5
GRID_WIDTH = (TILE_SIZE + TILE_PADDING) * GRID_COLS - TILE_PADDING
GRID_HEIGHT = (TILE_SIZE + TILE_PADDING) * GRID_ROWS - TILE_PADDING
START_X = (WIDTH - GRID_WIDTH) // 2
START_Y = 100

# Keyboard Settings
KEY_WIDTH = 40
KEY_HEIGHT = 55
KEY_PADDING = 5
KEY_START_Y = START_Y + GRID_HEIGHT + 50

# Animation Settings
ANIMATION_DURATION = 300 # ms per tile flip
SHAKE_DURATION = 400
SHAKE_AMPLITUDE = 1

# Fonts
FONT_PATH = "fonts/wordle.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = None # Fallback

def get_font(name, size):
    if FONT_PATH:
        try:
            return pygame.font.Font(FONT_PATH, size)
        except:
             pass
    return pygame.font.SysFont("ariel", int(size*0.8), bold=True)

FONT_TILE = get_font("wordle.ttf", 45)
FONT_KEY = get_font("wordle.ttf", 20)
FONT_MSG = get_font("wordle.ttf", 25)
FONT_TITLE = get_font("wordle.ttf", 60)

class WordleGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)
        self.clock = pygame.time.Clock()
        
        # Load words
        self.answers = self.load_words("wordle_answers.txt")
        self.guesses = self.load_words("wordle_guesses.txt")
        self.all_valid_words = set(self.answers + self.guesses)
        
        self.reset_game()
        
    def load_words(self, filename):
        words = []
        try:
            with open(filename, "r") as f:
                for line in f:
                    word = line.strip().lower()
                    if len(word) == 5:
                        words.append(word)
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
            sys.exit()
        return words

    def reset_game(self):
        self.target_word = random.choice(self.answers)
        print(f"Target Word: {self.target_word}") 
        self.guesses_made = [] # List of strings
        self.current_guess = ""
        self.game_over = False
        self.won = False
        self.message = ""
        self.message_timer = 0
        
        self.key_states = {} 
        for char in "abcdefghijklmnopqrstuvwxyz":
            self.key_states[char] = 'unused'
            
        # Animation State
        self.revealing_row = -1
        self.current_reveal_col = 0
        self.animation_start_time = 0
        
        # Shake State
        self.is_shaking = False
        self.shake_start_time = 0

    def handle_input(self, event):
        if self.revealing_row != -1 or self.is_shaking: # Block input during animation
            return

        if self.game_over and event.key == pygame.K_RETURN:
            self.reset_game()
            return

        if self.game_over:
            return

        if event.key == pygame.K_BACKSPACE:
            if len(self.current_guess) > 0:
                self.current_guess = self.current_guess[:-1]
        elif event.key == pygame.K_RETURN:
            self.submit_guess()
        elif event.unicode.isalpha() and len(self.current_guess) < 5:
            self.current_guess += event.unicode.lower()

    def submit_guess(self):
        guess = self.current_guess.lower()
        if len(guess) != 5:
            self.trigger_shake()
            self.show_message("Not enough letters")
            return
        if guess not in self.all_valid_words:
            self.trigger_shake()
            self.show_message("Not in word list")
            return
            
        self.guesses_made.append(guess)
        self.current_guess = ""
        
        # Start reveal animation
        self.revealing_row = len(self.guesses_made) - 1
        self.current_reveal_col = 0
        self.animation_start_time = pygame.time.get_ticks()
        
    def trigger_shake(self):
        self.is_shaking = True
        self.shake_start_time = pygame.time.get_ticks()

    def show_message(self, msg, duration=1000):
        self.message = msg
        self.message_timer = pygame.time.get_ticks() + duration

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Shake Animation Logic
        if self.is_shaking:
            elapsed = current_time - self.shake_start_time
            if elapsed >= SHAKE_DURATION:
                self.is_shaking = False
        
        # Reveal Animation Logic
        if self.revealing_row != -1:
            elapsed = current_time - self.animation_start_time
            
            if elapsed >= ANIMATION_DURATION:
                guess = self.guesses_made[self.revealing_row]
                letter = guess[self.current_reveal_col]
                status = self.get_letter_status(guess, self.target_word, self.current_reveal_col)
                
                # Update key state
                current_key_status = self.key_states[letter]
                if status == 'correct':
                    self.key_states[letter] = 'correct'
                elif status == 'present' and current_key_status != 'correct':
                    self.key_states[letter] = 'present'
                elif status == 'absent' and current_key_status not in ('correct', 'present'):
                     self.key_states[letter] = 'absent'

                self.current_reveal_col += 1
                self.animation_start_time = current_time
                
                if self.current_reveal_col >= 5:
                    self.revealing_row = -1
                    self.check_game_state()

    def check_game_state(self):
        last_guess = self.guesses_made[-1]
        if last_guess == self.target_word:
            self.game_over = True
            self.won = True
            self.show_message("Splendid!", 5000)
        elif len(self.guesses_made) >= 6:
            self.game_over = True
            self.show_message(self.target_word.upper(), 500000)

    def get_letter_status(self, guess, target, index):
        letter = guess[index]
        if letter == target[index]:
            return 'correct'
        if letter not in target:
            return 'absent'
        
        target_count = target.count(letter)
        correct_placements = 0
        for i in range(5):
            if guess[i] == target[i] and guess[i] == letter:
                correct_placements += 1
                
        non_green_target_count = target_count - correct_placements
        if non_green_target_count <= 0:
            return 'absent'
            
        previous_non_green_guesses_of_letter = 0
        for i in range(index):
            if guess[i] == letter and guess[i] != target[i]:
                previous_non_green_guesses_of_letter += 1
                
        if previous_non_green_guesses_of_letter < non_green_target_count:
            return 'present'
        return 'absent'

    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # Title
        title_surf = FONT_TITLE.render("WORDLE", True, COLOR_TEXT)
        self.screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 10))
        
        # Calculate shake offset
        shake_offset = 0
        if self.is_shaking:
            elapsed = pygame.time.get_ticks() - self.shake_start_time
            # Sine wave logic for shake
            shake_offset = math.sin(elapsed * 0.1) * SHAKE_AMPLITUDE * 2
        
        # Grid
        for row in range(GRID_ROWS):
            row_offset = 0
            # Apply shake to the current typing row
            if row == len(self.guesses_made) and self.is_shaking:
                row_offset = shake_offset
                
            for col in range(GRID_COLS):
                x = START_X + col * (TILE_SIZE + TILE_PADDING) + row_offset
                y = START_Y + row * (TILE_SIZE + TILE_PADDING)
                
                rect_y = y
                rect_h = TILE_SIZE
                
                letter = ""
                color_bg = COLOR_BG
                color_border = COLOR_EMPTY
                text_color = COLOR_TEXT
                
                # Logic for "committed" rows
                if row < len(self.guesses_made):
                    guess = self.guesses_made[row]
                    letter = guess[col]
                    
                    # Animation Handling
                    if row == self.revealing_row and col == self.current_reveal_col:
                        # Animating Tile
                        elapsed = pygame.time.get_ticks() - self.animation_start_time
                        progress = min(1.0, elapsed / ANIMATION_DURATION)
                        
                        scale = abs(1 - progress * 2)
                        rect_h = int(TILE_SIZE * scale)
                        rect_y = y + (TILE_SIZE - rect_h) // 2

                        if progress < 0.5:
                            color_bg = COLOR_BG
                            color_border = COLOR_FILLED_BORDER
                        else:
                            status = self.get_letter_status(guess, self.target_word, col)
                            if status == 'correct': color_bg = COLOR_CORRECT
                            elif status == 'present': color_bg = COLOR_PRESENT
                            else: color_bg = COLOR_ABSENT
                            color_border = color_bg
                            
                    elif row == self.revealing_row and col > self.current_reveal_col:
                        color_bg = COLOR_BG
                        color_border = COLOR_FILLED_BORDER
                    else:
                        status = self.get_letter_status(guess, self.target_word, col)
                        if status == 'correct': color_bg = COLOR_CORRECT
                        elif status == 'present': color_bg = COLOR_PRESENT
                        else: color_bg = COLOR_ABSENT
                        color_border = color_bg
                        
                elif row == len(self.guesses_made):
                    # Current typing row
                    if col < len(self.current_guess):
                        letter = self.current_guess[col]
                        color_border = COLOR_FILLED_BORDER
                        
                # Draw Tile
                rect = pygame.Rect(x, rect_y, TILE_SIZE, rect_h)
                
                if color_bg != COLOR_BG:
                    pygame.draw.rect(self.screen, color_bg, rect)
                else:
                    pygame.draw.rect(self.screen, color_border, rect, 2)
                    
                if letter:
                    text_surf = FONT_TILE.render(letter.upper(), True, text_color)
                    if rect_h > 5:
                         self.screen.blit(text_surf, (
                            x + TILE_SIZE//2 - text_surf.get_width()//2,
                            y + TILE_SIZE//2 - text_surf.get_height()//2
                        ))

        # Keyboard
        keys = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
        for i, row_keys in enumerate(keys):
            row_width = len(row_keys) * (KEY_WIDTH + KEY_PADDING) - KEY_PADDING
            start_x = (WIDTH - row_width) // 2
            
            for j, char in enumerate(row_keys):
                x = start_x + j * (KEY_WIDTH + KEY_PADDING)
                y = KEY_START_Y + i * (KEY_HEIGHT + KEY_PADDING)
                
                rect = pygame.Rect(x, y, KEY_WIDTH, KEY_HEIGHT)
                
                state = self.key_states[char]
                color = COLOR_KEY_BG
                if state == 'correct': color = COLOR_CORRECT
                elif state == 'present': color = COLOR_PRESENT
                elif state == 'absent': color = COLOR_ABSENT
                
                pygame.draw.rect(self.screen, color, rect, border_radius=4)
                
                text_surf = FONT_KEY.render(char.upper(), True, COLOR_TEXT)
                self.screen.blit(text_surf, (
                    x + KEY_WIDTH//2 - text_surf.get_width()//2,
                    y + KEY_HEIGHT//2 - text_surf.get_height()//2
                ))
        
        # Message
        current_time = pygame.time.get_ticks()
        if self.message and current_time < self.message_timer:
            msg_surf = FONT_MSG.render(self.message, True, (0,0,0))
            bg_rect = msg_surf.get_rect(center=(WIDTH//2, 130))
            bg_rect.inflate_ip(30, 20)
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, border_radius=5)
            self.screen.blit(msg_surf, msg_surf.get_rect(center=bg_rect.center))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_input(event)
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = WordleGame()
    game.run()
