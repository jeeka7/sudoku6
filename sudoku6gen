import streamlit as st
import numpy as np
import random

# --- Constants ---
GRID_SIZE = 6
BOX_ROWS = 2
BOX_COLS = 3

DIFFICULTY_LEVELS = {
    "Medium": 18,  # Number of cells to leave blank
    "Hard": 22     # Number of cells to leave blank
}

# --- Core Sudoku Logic ---

def is_safe(grid, row, col, num):
    """Checks if it's safe to place a number in a given cell."""
    # Check row
    if num in grid[row, :]:
        return False
    # Check column
    if num in grid[:, col]:
        return False
    # Check 2x3 box
    start_row, start_col = BOX_ROWS * (row // BOX_ROWS), BOX_COLS * (col // BOX_COLS)
    if num in grid[start_row:start_row + BOX_ROWS, start_col:start_col + BOX_COLS]:
        return False
    return True

def find_empty(grid):
    """Finds the first empty cell (represented by 0)."""
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i, j] == 0:
                return (i, j)
    return None

def solve_grid(grid):
    """Solves the Sudoku grid using backtracking."""
    find = find_empty(grid)
    if not find:
        return True  # Puzzle is solved
    else:
        row, col = find

    nums = list(range(1, GRID_SIZE + 1))
    random.shuffle(nums) # Ensures different solutions each time

    for num in nums:
        if is_safe(grid, row, col, num):
            grid[row, col] = num
            if solve_grid(grid):
                return True
            grid[row, col] = 0  # Backtrack
    return False

def generate_puzzle(difficulty):
    """Generates a new puzzle with a unique solution."""
    # 1. Create a full, solved grid
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    solve_grid(grid)
    solution = grid.copy()

    # 2. Poke holes in the grid
    puzzle = grid.copy()
    num_to_remove = DIFFICULTY_LEVELS.get(difficulty, 18)
    
    attempts = 0
    while np.count_nonzero(puzzle) > (GRID_SIZE * GRID_SIZE) - num_to_remove and attempts < 100:
        row, col = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        if puzzle[row, col] != 0:
            puzzle[row, col] = 0
        attempts += 1
        
    return puzzle, solution

# --- Streamlit UI Components ---

def get_grid_html(grid):
    """Generates the HTML and CSS for displaying the Sudoku grid."""
    html = """
    <style>
        .sudoku-container {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            grid-template-rows: repeat(6, 1fr);
            border: 3px solid #333;
            width: 90vmin;
            height: 60vmin;
            max-width: 450px;
            max-height: 300px;
            margin: 20px auto;
            font-family: 'Arial', sans-serif;
        }
        .sudoku-cell {
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 1.5em;
            border: 1px solid #ccc;
        }
        /* Thick borders for the 2x3 boxes */
        .sudoku-cell:nth-child(3n) { border-right: 2px solid #555; }
        .sudoku-cell:nth-child(6n) { border-right: 1px solid #ccc; }
        .sudoku-row:nth-child(2n) .sudoku-cell { border-bottom: 2px solid #555; }
        .sudoku-row:nth-child(6n) .sudoku-cell { border-bottom: 1px solid #ccc; }
    </style>
    <div id="printable-sudoku">
        <div class="sudoku-container">
    """
    for r in range(GRID_SIZE):
        html += f'<div class="sudoku-row" style="display: contents;">'
        for c in range(GRID_SIZE):
            num = grid[r, c]
            display_num = num if num != 0 else ""
            html += f'<div class="sudoku-cell">{display_num}</div>'
        html += f'</div>'
    html += "</div></div>"
    return html

def get_print_script():
    """Generates the JavaScript and CSS for the print functionality."""
    print_script = """
    <style>
        @media print {
            /* Hide everything on the page */
            body * {
                visibility: hidden;
            }
            /* Make the printable area and its children visible */
            #printable-sudoku, #printable-sudoku * {
                visibility: visible;
            }
            /* Position the printable area on the page */
            #printable-sudoku {
                position: absolute;
                left: 50%;
                top: 50%;
                transform: translate(-50%, -50%);
            }
            .stButton { display: none; }
        }
    </style>
    <script>
        function printSudoku() {
            window.print();
        }
    </script>
    """
    return print_script

# --- Main Application ---

st.set_page_config(page_title="6x6 Sudoku Generator", layout="wide")

st.title("🔢 6x6 Sudoku Puzzle Generator")
st.write("Create a new 6x6 Sudoku puzzle. Choose your difficulty and click 'Generate'.")

# Sidebar for controls
with st.sidebar:
    st.header("Controls")
    difficulty = st.selectbox("Select Difficulty", options=list(DIFFICULTY_LEVELS.keys()), index=0)
    
    if st.button("Generate New Puzzle", type="primary"):
        with st.spinner("Generating..."):
            puzzle, solution = generate_puzzle(difficulty)
            st.session_state.puzzle = puzzle
            st.session_state.solution = solution
            st.session_state.show_solution = False

# Main content area
col1, col2 = st.columns([0.7, 0.3])

with col1:
    if 'puzzle' in st.session_state:
        st.markdown(get_grid_html(st.session_state.puzzle), unsafe_allow_html=True)
        st.markdown(get_print_script(), unsafe_allow_html=True)
        st.button("🖨️ Print Puzzle", on_click=st.components.v1.html, args=('<script>parent.printSudoku()</script>', 50, 50))

    else:
        st.info("Click 'Generate New Puzzle' in the sidebar to start.")

with col2:
    if 'puzzle' in st.session_state:
        st.subheader("Solution")
        if st.checkbox("Show Solution"):
             st.session_state.show_solution = True
        
        if st.session_state.get('show_solution', False):
            # Display solution as a simple table for clarity
            solution_grid = st.session_state.solution
            st.table(solution_grid.astype(str).replace('0', ''))
