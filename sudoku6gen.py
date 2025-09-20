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
    if num in grid[row, :] or num in grid[:, col]:
        return False
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
        return True
    else:
        row, col = find

    nums = list(range(1, GRID_SIZE + 1))
    random.shuffle(nums)

    for num in nums:
        if is_safe(grid, row, col, num):
            grid[row, col] = num
            if solve_grid(grid):
                return True
            grid[row, col] = 0
    return False

def generate_puzzle(difficulty):
    """Generates a new puzzle with a unique solution."""
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    solve_grid(grid)
    solution = grid.copy()

    puzzle = grid.copy()
    num_to_remove = DIFFICULTY_LEVELS.get(difficulty, 18)
    
    cells_removed = 0
    attempts = 0
    while cells_removed < num_to_remove and attempts < 1000:
        row, col = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        if puzzle[row, col] != 0:
            puzzle[row, col] = 0
            cells_removed += 1
        attempts += 1
        
    return puzzle, solution

# --- Streamlit UI Components ---

def get_page_setup_html():
    """Returns a single HTML block with all necessary CSS and JavaScript for the page."""
    return """
    <style>
        /* Styles for the grid displayed on the page */
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
            background-color: #fff;
        }
        .sudoku-cell {
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: clamp(1rem, 4vmin, 1.8rem);
            font-weight: bold;
            color: #333;
            border: 1px solid #ccc;
        }
        .sudoku-cell:nth-child(3n) { border-right: 2px solid #555; }
        .sudoku-cell:nth-child(6n) { border-right: 1px solid #ccc; }
        .sudoku-container > div:nth-child(2n) .sudoku-cell { border-bottom: 2px solid #555; }
        .sudoku-container > div:nth-child(6n) .sudoku-cell { border-bottom: 1px solid #ccc; }

        /* Custom Print Button Styles */
        .print-button {
            display: inline-block;
            padding: 0.5em 1em;
            font-size: 16px;
            font-weight: 500;
            color: #0F1116;
            background-color: #FFFFFF;
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            cursor: pointer;
            margin-top: 10px;
            text-align: center;
            text-decoration: none;
            transition: all 0.2s ease-in-out;
        }
        .print-button:hover {
            color: #FFFFFF;
            border-color: #FF4B4B;
            background-color: #FF4B4B;
        }

        /* New Print Styles - Hides everything except the target element */
        @media print {
            /* Add a class to the body when printing is active */
            body.sudoku-printing-mode > * {
                visibility: hidden !important;
            }
            body.sudoku-printing-mode .sudoku-print-target,
            body.sudoku-printing-mode .sudoku-print-target * {
                visibility: visible !important;
            }
            body.sudoku-printing-mode .sudoku-print-target {
                position: absolute !important;
                left: 0 !important;
                top: 0 !important;
                width: 100% !important;
            }
        }
    </style>
    <script>
        function printElement(elementId, title) {
            const gridElement = document.getElementById(elementId);
            if (!gridElement) {
                console.error('Element to print not found:', elementId);
                return;
            }

            // Add classes to activate the print-specific CSS
            document.body.classList.add('sudoku-printing-mode');
            gridElement.classList.add('sudoku-print-target');

            // Define a function to clean up classes after printing
            const cleanupAfterPrint = () => {
                document.body.classList.remove('sudoku-printing-mode');
                gridElement.classList.remove('sudoku-print-target');
                window.removeEventListener('afterprint', cleanupAfterPrint);
            };

            // Listen for the 'afterprint' event to run cleanup
            window.addEventListener('afterprint', cleanupAfterPrint);

            // Trigger the browser's print dialog
            window.print();
        }
    </script>
    """

def get_grid_html(grid, container_id):
    """Generates the HTML for a single Sudoku grid."""
    html = f'<div id="{container_id}"><div class="sudoku-container">'
    for r in range(GRID_SIZE):
        html += '<div style="display: contents;">'
        for c in range(GRID_SIZE):
            num = grid[r, c]
            display_num = str(num) if num != 0 else ""
            html += f'<div class="sudoku-cell">{display_num}</div>'
        html += '</div>'
    html += "</div></div>"
    return html

# --- Main Application ---

st.set_page_config(page_title="6x6 Sudoku Generator", layout="wide")

# Inject all CSS and JavaScript at once.
st.markdown(get_page_setup_html(), unsafe_allow_html=True)

st.title("🔢 6x6 Sudoku Puzzle Generator")
st.write("Create a new puzzle to solve on screen or print out.")

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
col1, col2 = st.columns([0.65, 0.35])

with col1:
    st.header("Puzzle")
    if 'puzzle' in st.session_state:
        st.markdown(get_grid_html(st.session_state.puzzle, "puzzle-grid"), unsafe_allow_html=True)
        st.markdown('<button onclick="printElement(\'puzzle-grid\', \'Sudoku Puzzle\')" class="print-button">🖨️ Print Puzzle</button>', unsafe_allow_html=True)
    else:
        st.info("Click 'Generate New Puzzle' in the sidebar to start.")

with col2:
    if 'puzzle' in st.session_state:
        st.header("Solution")
        if st.button("Toggle Solution"):
            st.session_state.show_solution = not st.session_state.get('show_solution', False)
        
        if st.session_state.get('show_solution', False):
            st.markdown(get_grid_html(st.session_state.solution, "solution-grid"), unsafe_allow_html=True)
            st.markdown('<button onclick="printElement(\'solution-grid\', \'Sudoku Solution\')" class="print-button">🖨️ Print Solution</button>', unsafe_allow_html=True)

