"""Heuristic evaluation of a material matrix (see KaitoGame.material_matrix)."""

WIN_SCORE = 1000  # Score of a won game for the search players; larger than any heuristic evaluation


def material_evaluation(matrix):
    """Higher is better for the player in row 0.

    Only call this for unfinished games: Katana and Kabuto counts must be > 0.
    Finished games are scored by the search itself (see AlphaBetaPlayer).
    The 1/count terms make losing the last pieces of a type increasingly expensive.
    """
    own, opponent = matrix[0], matrix[1]
    katanas, kabutos = 0, 1
    return -1 / own[katanas] + 1 / opponent[katanas] - 1 / own[kabutos] + 1 / opponent[kabutos]
