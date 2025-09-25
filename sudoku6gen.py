import streamlit as st
import numpy as np
import random
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

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

# --- PDF Generation using reportlab ---
def create_sudoku_pdf_bytes(grid_data, title):
    """Generates a PDF for the Sudoku grid and returns it as bytes."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width / 2, height - inch, title)

    # Grid Drawing
    cell_size = 0.75 * inch
    grid_width = GRID_SIZE * cell_size
    grid_height = GRID_SIZE * cell_size
    x_start = (width - grid_width) / 2
    y_start = height - 2 * inch - grid_height
    
    p.setFont("Helvetica", 24)
    
    # Draw numbers
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            num = grid_data[r, c]
            x = x_start + c * cell_size
            y = y_start + (GRID_SIZE - 1 - r) * cell_size 

            if num != 0:
                p.drawCentredString(x + cell_size / 2, y + cell_size / 2 - 10, str(num))
    
    # Draw grid lines
    p.setLineWidth(1)
    for i in range(GRID_SIZE + 1):
        p.line(x_start + i * cell_size, y_start, x_start + i * cell_size, y_start + grid_height)
        p.line(x_start, y_start + i * cell_size, x_start + grid_width, y_start + i * cell_size)

    # Draw thicker box lines
    p.setLineWidth(2.5)
    for i in range(0, GRID_SIZE + 1, BOX_COLS):
        p.line(x_start + i * cell_size, y_start, x_start + i * cell_size, y_start + grid_height)
    for i in range(0, GRID_SIZE + 1, BOX_ROWS):
        p.line(x_start, y_start + i * cell_size, x_start + grid_width, y_start + i * cell_size)

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.getvalue()


# --- Streamlit UI Components ---
def get_grid_html(grid, container_id):
    """Generates the HTML for a single Sudoku grid for on-screen display."""
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

# Inject CSS for on-screen grid display
st.markdown("""
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
</style>
""", unsafe_allow_html=True)


st.title("🔢 6x6 Sudoku Puzzle Generator")
st.write("Create a new puzzle to solve on screen and view or download as a PDF.")

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
            # Generate PDF data and store in session state
            st.session_state.puzzle_pdf = create_sudoku_pdf_bytes(puzzle, "Sudoku Puzzle")
            st.session_state.solution_pdf = create_sudoku_pdf_bytes(solution, "Sudoku Solution")

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.header("Puzzle")
    if 'puzzle' in st.session_state:
        st.markdown(get_grid_html(st.session_state.puzzle, "puzzle-grid"), unsafe_allow_html=True)
        st.pdf(st.session_state.puzzle_pdf, height=500)
        st.download_button(
            label="Download Puzzle PDF",
            data=st.session_state.puzzle_pdf,
            file_name="sudoku_puzzle.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Click 'Generate New Puzzle' in the sidebar to start.")

with col2:
    if 'puzzle' in st.session_state:
        st.header("Solution")
        if st.button("Toggle Solution"):
            st.session_state.show_solution = not st.session_state.get('show_solution', False)
        
        if st.session_state.get('show_solution', False):
            st.markdown(get_grid_html(st.session_state.solution, "solution-grid"), unsafe_allow_html=True)
            st.pdf(st.session_state.solution_pdf, height=500)
            st.download_button(
                label="Download Solution PDF",
                data=st.session_state.solution_pdf,
                file_name="sudoku_solution.pdf",
                mime="application/pdf"
            )

