from constants import ABANDONED_SHACK, ANIMAL, BEAR, BLUE, BOTTOM_RIGHT, COLOUR, COLUMNS, COUGAR, DESERT, DISTANCES, DOWN, DOWN_RIGHT, FOREST, GREEN, ID, INVERSE, LEFT, MOUNTAIN, REGULAR, RIGHT, ROWS, STANDING_STONE, STRUCTURE, SWAMP, TERRAIN, TOP_LEFT, UP, UP_LEFT, WATER, WHITE

import json

# Where the board json file is stored (relative to this file)
BOARDS_FILE_NAME = "boards.json"

# The names used in the info file
STRUCTURE_MAP = {
    "bss": (BLUE, STANDING_STONE),
    "bas": (BLUE, ABANDONED_SHACK),
    "wss": (WHITE, STANDING_STONE),
    "was": (WHITE, ABANDONED_SHACK),
    "gss": (GREEN, STANDING_STONE),
    "gas": (GREEN, ABANDONED_SHACK),
}

# The maximum distances that matter for each landmark
MAX_DISTANCES = {
    FOREST: 1,
    DESERT: 1,
    WATER: 1,
    SWAMP: 1,
    MOUNTAIN: 1,
    COUGAR: 2,
    BEAR: 2,
    ABANDONED_SHACK: 2,
    STANDING_STONE: 2,
    BLUE: 3,
    WHITE: 3,
    GREEN: 3
}

# (cell id, cell object)
CELLS: dict[str, dict[str, str]] = {}

# Shows if a board is inverted or not (board number 1-6, true if upright and false otherwise)
BOARD_ORIENTATION: dict[int, bool] = {}

# The order that the board are in (board number 1-6 (name of the board), board order 0-5 (where the board is starting top left and going to bottom right in a z shape))
BOARD_ORDERS: dict[int, int] = {}

# The reverse mapping of BOARD_ORDERS
BOARD_ORDERS_REVERSED: dict[int, int] = {}

# All the boards from the board json file
BOARDS = None

# Reads the board json file
def read_boards(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)


# Initialises the board with distances and structures
def init_board(board_orders: list[str], structure_placement: dict[str, str]):
    global BOARD_ORIENTATION, BOARD_ORDERS, BOARDS

    # A list of cells
    board: list[dict[str, str]] = []

    boards = read_boards(BOARDS_FILE_NAME)
    BOARDS = boards

    for k, board_order in enumerate(board_orders):
        board_index = int(board_order[0]) - 1
        rotation = board_order[1:]

        BOARD_ORIENTATION[int(board_order[0])] = rotation == TOP_LEFT 
        BOARD_ORDERS[int(board_order[0])] = k
        BOARD_ORDERS_REVERSED[k] = int(board_order[0])

        board_details = boards[board_index]

        for i, row in enumerate(board_details[ROWS]):
            for j, column in enumerate(row[COLUMNS]):
                column[ID] = f'{board_index+1}{i+1}{j+1}'
                CELLS[column[ID]] = column

        for key, value in structure_placement.items():
            if value.startswith(board_order[0]):
                row = int(value[1]) - 1
                column = int(value[2]) - 1
                colour = STRUCTURE_MAP[key][0]
                structure = STRUCTURE_MAP[key][1]

                board_details[ROWS][row][COLUMNS][column][COLOUR] = colour
                board_details[ROWS][row][COLUMNS][column][STRUCTURE] = structure


        if rotation == BOTTOM_RIGHT:
            new_board_details = {
                ROWS: []
            }

            for row in board_details[ROWS][::-1]:
                new_board_details[ROWS].append({COLUMNS: row[COLUMNS][::-1]})
            
            board_details = new_board_details
    

        for row in board_details[ROWS]:
            for column in row[COLUMNS]:
                state = column

                board.append(state)
    
    board = apply_locality_data(board)

    return board
    

# Determines distances from landmarks based on neighbours
def apply_locality_data(board: list[dict[str, str]]):
    for cell in board:
        cell[DISTANCES] = {}
    
        cell[DISTANCES][cell[TERRAIN]] = 0
        
        if ANIMAL in cell:
            cell[DISTANCES][cell[ANIMAL]] = 0

        if STRUCTURE in cell:
            cell[DISTANCES][cell[STRUCTURE]] = 0
        
        if COLOUR in cell:
            cell[DISTANCES][cell[COLOUR]] = 0
    
    for i in range(3):
        for cell in board:
            neighbours = get_neighbours(cell[ID])

            for neighbour in neighbours:
                distances: dict = neighbour[DISTANCES]

                for key, value in distances.items():
                    if key not in cell[DISTANCES]:
                        cell[DISTANCES][key] = value + 1
                        continue

                    cell[DISTANCES][key] = min(cell[DISTANCES][key], value + 1)

    for cell in board:
        distances = cell[DISTANCES]

        new_distances = {}
        for key, value in distances.items():
            if value > MAX_DISTANCES[key]:  
                continue

            new_distances[key] = value
        
        cell[DISTANCES] = new_distances

    return board


# Gets the tile as a neighbour and accounts for the beighbour being from a different board tile
def get_off_tile_neighbour(board_index, row, column):

    # Normal cells part of the same board tile
    if row >= 1 and row <= 3 and column >= 1 and column <= 6:
        return f"{board_index}{row}{column}"


    # (where the neighbouring board is, (direction to the neighour relative to the cell, to inverse columns / row) * 2
    # The first tuple is if the neighbouring board is upright, the second is otherwise
    # E.g) (UP_LEFT, (UP_LEFT, REGULAR), (UP_LEFT, INVERSE)) => the neighbouring board is up left, if the neighbouring board is upright then the neighbour is up left and regular otherwise the neighbour is up left but inverse the ros/columns
    def get_settings(is_upright, row, column):
        if row <= 0 and column <= 0:
            return (UP_LEFT, (UP_LEFT, REGULAR), (UP_LEFT, INVERSE)) if is_upright else (DOWN_RIGHT, (UP_LEFT, INVERSE), (UP_LEFT, REGULAR))
        if row >= 4 and column >= 7:
            return (DOWN_RIGHT, (DOWN_RIGHT, REGULAR), (DOWN_RIGHT, INVERSE)) if is_upright else (UP_LEFT, (DOWN_RIGHT, INVERSE), (DOWN_RIGHT, REGULAR))
        if row <= 0:
            return (UP, (UP, REGULAR), (UP, INVERSE)) if is_upright else (DOWN, (UP, INVERSE), (UP, REGULAR))
        elif row >= 4:
            return (DOWN, (DOWN, REGULAR), (DOWN, INVERSE)) if is_upright else (UP, (DOWN, INVERSE), (DOWN, REGULAR))
        elif column <= 0:
            return (LEFT, (LEFT, REGULAR), (LEFT, INVERSE)) if is_upright else (RIGHT, (LEFT, INVERSE), (LEFT, REGULAR))
        elif column >= 7:
            return (RIGHT, (RIGHT, REGULAR), (RIGHT, INVERSE)) if is_upright else (LEFT, (RIGHT, INVERSE), (RIGHT, REGULAR))

    is_upright = BOARD_ORIENTATION[board_index]

    # Determines if the given board index (board number 1-6) has a board in that direction
    has_board_functions = {
        UP: lambda board_index: BOARD_ORDERS[board_index] >= 2,
        DOWN: lambda board_index: BOARD_ORDERS[board_index] <= 3,
        LEFT: lambda board_index: BOARD_ORDERS[board_index] % 2 == 1,
        RIGHT: lambda board_index: BOARD_ORDERS[board_index] % 2 == 0,
        UP_LEFT: lambda board_index: has_board_functions[UP](board_index) and has_board_functions[LEFT](board_index),
        DOWN_RIGHT: lambda board_index: has_board_functions[DOWN](board_index) and has_board_functions[RIGHT](board_index)
    }

    # Determines the neighbouring board given the direction and board number (1-6)
    get_board_functions = {
        UP: lambda board_index: BOARD_ORDERS_REVERSED[BOARD_ORDERS[board_index] - 2],
        DOWN: lambda board_index: BOARD_ORDERS_REVERSED[BOARD_ORDERS[board_index] + 2],
        LEFT: lambda board_index: BOARD_ORDERS_REVERSED[BOARD_ORDERS[board_index] - 1],
        RIGHT: lambda board_index: BOARD_ORDERS_REVERSED[BOARD_ORDERS[board_index] + 1],
        UP_LEFT: lambda board_index: BOARD_ORDERS_REVERSED[BOARD_ORDERS[board_index] - 3],
        DOWN_RIGHT: lambda board_index: BOARD_ORDERS_REVERSED[BOARD_ORDERS[board_index] + 3]
    }

    # How to find the neighbour given the settings and current cell location
    direction_to_index = {
        (DOWN, REGULAR): (1, column),
        (DOWN, INVERSE): (3, 7 - column),
        (UP, REGULAR): (3, column),
        (UP, INVERSE): (1, 7 - column),
        (RIGHT, REGULAR): (row, 1),
        (RIGHT, INVERSE): (4 - row, 6),
        (LEFT, REGULAR): (row, 6),
        (LEFT, INVERSE): (4 - row, 1),
        (UP_LEFT, REGULAR): (3, 6),
        (UP_LEFT, INVERSE): (1, 1),
        (DOWN_RIGHT, REGULAR): (1, 1),
        (DOWN_RIGHT, INVERSE): (3, 6)
    }

    (a, (b, c), (d, e)) = get_settings(is_upright, row, column)

    if not has_board_functions[a](board_index):
        return None
    
    board_board_index = get_board_functions[a](board_index)

    if BOARD_ORIENTATION[board_board_index]:
        x, y = direction_to_index[(b, c)]
        return f"{board_board_index}{x}{y}"
    else:
        x, y = direction_to_index[(d, e)]
        return f"{board_board_index}{x}{y}"


# Get the neighbours of a given cell id
def get_neighbours(id: str):
    board_index = int(id[0])
    row = int(id[1])
    column = int(id[2])

    print(f"getting neighbours for: ({board_index}, {row}, {column})")

    neighbours = []

    neighbours.append(f"{board_index}{row}{column - 1}")
    neighbours.append(f"{board_index}{row}{column + 1}")
    
    neighbours.append(f"{board_index}{row - 1}{column}")
    neighbours.append(f"{board_index}{row + 1}{column}")

    # Cells that are odd are adjacent to the previous row (other than the obvious above)
    # Cells that are even are adjacent to the next row
    if (column % 2 == 1):
        neighbours.append(f"{board_index}{row - 1}{column - 1}")
        neighbours.append(f"{board_index}{row - 1}{column + 1}")
    else:
        neighbours.append(f"{board_index}{row + 1}{column - 1}")
        neighbours.append(f"{board_index}{row + 1}{column + 1}")
    
    neighbours_off_tile_fixed = map(lambda x: get_off_tile_neighbour(int(x[0]), int(x[1]), int(x[2])), neighbours)

    neighbours = map(lambda x: CELLS[x], filter(lambda x: x is not None, neighbours_off_tile_fixed))

    return neighbours