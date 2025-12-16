import random
from flask import Flask, request, render_template, session, redirect, url_for

# Initialize the Flask application
app = Flask(__name__)
# Secret key is mandatory for using sessions (to store game state)
app.secret_key = 'hangman_secret_key_123' # **IMPORTANT: Change this!**

# --- Game Configuration ---
WORD_LIST = ['rainbow', 'computer', 'science', 'programming',
             'python', 'mathematics', 'player', 'condition',
             'reverse', 'water', 'board', 'geeks', 'hangman']
MAX_TURNS = 10 # Slightly reduced from 12 for typical hangman style

# --- Helper Functions ---

def initialize_game():
    """Sets up the initial state for a new game."""
    word = random.choice(WORD_LIST)
    session['word'] = word.lower()
    session['guesses'] = [] # List of characters already guessed
    session['turns'] = MAX_TURNS
    session['game_over'] = False
    session['win'] = False
    session['message'] = "Start guessing! Choose a letter."
    session['current_word_display'] = "_ " * len(word)
    # The 'failed' count from your original code is implicitly handled by 'turns'

def get_word_display(word, guesses):
    """Generates the hidden word string (e.g., P Y T _ O N)"""
    display = ""
    hidden_count = 0
    for char in word:
        if char in guesses:
            display += char.upper() + " "
        else:
            display += "_ "
            hidden_count += 1
    return display, hidden_count

# --- Routes and Game Logic ---

@app.route('/')
def index():
    """Initializes and displays the game board."""
    if 'word' not in session or session['game_over']:
        initialize_game()
        
    word = session['word']
    guesses = session['guesses']
    
    current_word_display, _ = get_word_display(word, guesses)
    session['current_word_display'] = current_word_display
    
    return render_template('index.html', 
                           name=session.get('player_name', 'Player'),
                           word_display=current_word_display,
                           turns=session['turns'],
                           guesses=guesses,
                           message=session['message'],
                           game_over=session['game_over'],
                           win=session['win'])

@app.route('/guess', methods=['POST'])
def guess_letter():
    """Handles a player's letter submission."""
    if session['game_over']:
        return redirect(url_for('index'))

    # Get the player's guess
    guess = request.form.get('guess', '').strip().lower()
    
    if len(guess) != 1 or not guess.isalpha():
        session['message'] = "Invalid input. Please guess a single letter."
        return redirect(url_for('index'))

    if guess in session['guesses']:
        session['message'] = f"You already guessed '{guess.upper()}'! Try another letter."
        return redirect(url_for('index'))
    
    # Add the new guess to the list
    session['guesses'].append(guess)
    word = session['word']
    turns = session['turns']
    
    if guess in word:
        session['message'] = f"Yes! '{guess.upper()}' is in the word."
    else:
        turns -= 1
        session['turns'] = turns
        session['message'] = f"Wrong guess. '{guess.upper()}' is NOT in the word."

    # Update word display and check for win/loss
    current_word_display, hidden_count = get_word_display(word, session['guesses'])
    session['current_word_display'] = current_word_display
    
    if hidden_count == 0:
        # Win condition
        session['game_over'] = True
        session['win'] = True
        session['message'] = f"🎉 Congratulations, you win! The word was **{word.upper()}**."
    elif session['turns'] <= 0:
        # Loss condition
        session['game_over'] = True
        session['win'] = False
        session['message'] = f"😞 You lose! You ran out of turns. The word was **{word.upper()}**."
        
    return redirect(url_for('index'))

@app.route('/restart')
def restart():
    """Clears the session and redirects to the start page."""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # You might prompt for the name here or handle it in a separate initial route
    # For simplicity, we use a default name.
    app.run(debug=True)