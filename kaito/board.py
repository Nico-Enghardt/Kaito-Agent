"""Conversion between flat cell indices (0..35) and 1-based (column, row) positions."""

BOARD_SIZE = 6
NUMBER_OF_CELLS = BOARD_SIZE * BOARD_SIZE


def index_to_position(index):
    row, column = divmod(index, BOARD_SIZE)
    return column + 1, row + 1


def position_to_index(column, row):
    return (row - 1) * BOARD_SIZE + column - 1


def cell_name(index):
    """Name of the cell's button in main_window.ui, e.g. 'cell3_5'."""
    column, row = index_to_position(index)
    return f"cell{column}_{row}"
