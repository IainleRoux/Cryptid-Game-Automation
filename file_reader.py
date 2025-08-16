import re

from board import init_board


def read_info_file(file_name):
    board_orders = None
    structure_placement = None

    with open(file_name) as file:
        board_orders = read_board_orders(file)
        
    with open(file_name) as file:
        structure_placement = read_structure_placement(file)

    with open(file_name) as file:
        player_clues = read_player_clues(file)

    cell_list = init_board(board_orders, structure_placement)

    return cell_list, player_clues


def read_board_orders(file):
    result = []

    found = False
    for line in file.readlines():
        if found and len(result) < 6:
            result.append(line.strip())
        
        if found and len(result) >= 6:
            return result

        if line.startswith('## Board Order:'):
            found = True


def read_structure_placement(file):
    result = {}

    found = False
    for line in file.readlines():
        if found and len(result) < 6:
            key = line[0:3]
            value = line[line.index(":", line.index(":") + 1) + 2:].strip()

            result.update({key: value})
        
        if found and len(result) >= 6:
            return result

        if line.startswith('## Structure Placement:'):
            found = True


def read_player_clues(file):
    found = False
    current_player = None
    clue_pattern = r'- (.*?):'
    player_pattern = r'### (.*?):'
    player_clues: dict[str, set[str]] = {}

    for line in file.readlines():
        if found and line.startswith('### All Clues'):
            break

        if found and line.startswith('###'):
            current_player = re.match(player_pattern, line).group(1)
            player_clues[current_player] = set()
            continue

        if found and current_player and line == '\n':
            current_player = None
            continue

        if found and current_player:
            clue = re.search(clue_pattern, line).group(1)
            player_clues[current_player].add(clue)

        if line.startswith('## Player Clues:'):
            found = True

    return player_clues