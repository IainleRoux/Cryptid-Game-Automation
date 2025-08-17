
from sys import argv
from board import DISTANCES
from constants import ABANDONED_SHACK, BEAR, BLUE, COUGAR, DESERT, FOREST, GREEN, ID, MOUNTAIN, STANDING_STONE, SWAMP, WATER, WHITE
from file_reader import read_info_file, reset_game_info, write_to_possible_cells_to_info_file


def get_predicate1(criteria: str, distance: int):
    return lambda cell: criteria in cell[DISTANCES] and cell[DISTANCES][criteria] <= distance


def get_predicate2(criteria1: str, criteria2: str, distance: int):
    return lambda cell: (criteria1 in cell[DISTANCES] and cell[DISTANCES][criteria1] <= distance) or (criteria2 in cell[DISTANCES] and cell[DISTANCES][criteria2] <= distance)


CLUE_PREDICATE_MAP = {
    'ofod': get_predicate2(FOREST, DESERT, 0),
    'ofow': get_predicate2(FOREST, WATER, 0),
    'ofos': get_predicate2(FOREST, SWAMP, 0),
    'ofom': get_predicate2(FOREST, MOUNTAIN, 0),
    'odow': get_predicate2(DESERT, WATER, 0),
    'odos': get_predicate2(DESERT, SWAMP, 0),
    'odom': get_predicate2(DESERT, MOUNTAIN, 0),
    'owos': get_predicate2(WATER, SWAMP, 0),
    'owom': get_predicate2(WATER, MOUNTAIN, 0),
    'osom': get_predicate2(SWAMP, MOUNTAIN, 0),
    'wosof': get_predicate1(FOREST, 1),
    'wosod': get_predicate1(DESERT, 1),
    'wosos': get_predicate1(SWAMP, 1),
    'wosom': get_predicate1(MOUNTAIN, 1),
    'wosow': get_predicate1(WATER, 1),
    'wosoeat': get_predicate2(BEAR, COUGAR, 1),
    'wtsoass': get_predicate1(STANDING_STONE, 2),
    'stsoaas': get_predicate1(ABANDONED_SHACK, 2),
    'wtsoabt': get_predicate1(BEAR, 2),
    'wtsoact': get_predicate1(COUGAR, 2),
    'wtsoabs': get_predicate1(BLUE, 2),
    'wtsoaws': get_predicate1(WHITE, 2),
    'wtsoags': get_predicate1(GREEN, 2)
}


def init():
    cell_list, player_clues = read_info_file()

    return cell_list, player_clues

def get_possible_cells(board, player_clues):
    player_possible_cells: dict[str, set[str]] = {}

    known_player_clues = set()

    for player_name, player_clue_set in player_clues.items():
        if len(player_clue_set) == 1:
            known_player_clues.union(player_clue_set)

    for player_name, player_clue_set in player_clues.items():
        player_possible_cells[player_name] = set()

        for cell in board:
            if any(map(lambda clue: CLUE_PREDICATE_MAP[clue](cell), filter(lambda x: x not in known_player_clues or len(player_clue_set) > 1, player_clue_set))):
                player_possible_cells[player_name].add(cell[ID])

    for player_name, cells in player_possible_cells.items():
        print(f"Possible cells for {player_name} ({len(cells)}): {cells}")
        print()

    intersetion_of_player_cells = None

    for _, possible_cells in player_possible_cells.items():
        if intersetion_of_player_cells is None:
            intersetion_of_player_cells = possible_cells
            continue

        intersetion_of_player_cells = intersetion_of_player_cells.intersection(possible_cells)

    return intersetion_of_player_cells


def update_game():
    cell_list, player_clues = init()

    possible_cells = get_possible_cells(cell_list, player_clues)

    print(f"Possible cryptid cells ({len(possible_cells)}): {possible_cells}")

    write_to_possible_cells_to_info_file(possible_cells)


def play_game():
    print("Starting the game...")
    reset_game_info()

    print("Game setup...")
    update_game()

    while True:
        next_move = input('Enter next move: ')

        if next_move in ['exit', 'quit']:
            print("Exiting the game.")
            break

        print("TODO: Implement game logic based on the next move.")


if __name__ == "__main__":
    if len(argv) > 1 and argv[1] in ['reset', 'setup']:
        reset_game_info()
        exit

    if len(argv) > 1 and argv[1] == 'update':
        update_game()
        exit
    
    if len(argv) > 1 and argv[1] == 'play':
        play_game()
        exit
    
    update_game()
