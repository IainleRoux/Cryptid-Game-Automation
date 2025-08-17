import re

from board import init_board

SETUP_INFO_FILE = ".setup/info.md"
INFO_FILE = "info.md"


def read_info_file(file_name = INFO_FILE):
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
        if found and line.startswith('### Possible Cryptid Cells:'):
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


def write_to_possible_cells_to_info_file(cells: set):
    lines = None

    with open(INFO_FILE, "r") as f:
        lines = f.readlines()

    with open(INFO_FILE, "w") as f:
        found = False
        wrote_lines = False

        for line in lines:
            if not found:
                f.write(line)

            if found and wrote_lines and line.startswith('### All Clues'):
                f.write(line)
                found = False

            if found and not wrote_lines:
                if len(cells) == 108:
                    f.write(f"- All states\n\n")
                    wrote_lines = True
                    continue

                for i in range(1, 7):
                    filtered_cells = list(filter(lambda x: int(x[0]) == i, cells))

                    for j, cell in enumerate(filtered_cells):
                        if j == 0:
                            f.write(f"- ")

                        f.write(f"{cell}")

                        if j < len(filtered_cells) - 1:
                            f.write(f", ")

                    if filtered_cells:
                        f.write(f"\n")

                f.write(f"\n")
                wrote_lines = True

            if line.startswith('### Possible Cryptid Cells:'):
                found = True


def reset_game_info():
    lines = None

    with open(SETUP_INFO_FILE, "r") as setup_file:
        lines = setup_file.readlines()

    with open(INFO_FILE, "w") as info_file:
        info_file.writelines(lines)
