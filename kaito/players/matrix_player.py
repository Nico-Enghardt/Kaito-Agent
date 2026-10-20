import dataclasses
import logging

import numpy as np

from kaito.board import NUMBER_OF_CELLS
from kaito.evaluation import WIN_SCORE
from kaito.pieces import PieceType
from kaito.players.base import BasePlayer

logger = logging.getLogger(__name__)


def tile_weight(tile):
    """Signed piece value: black pieces positive, red pieces negative, empty 0."""
    if tile.is_empty:
        return 0
    return tile.owner.sign * tile.piece.value


class MatrixSearchPlayer(BasePlayer):
    """Alpha-beta search on a compact board: a (36x36 matrix, cursor) pair.

    Diagonal entries hold the signed piece weight of each cell, off-diagonal
    entries are 1 where the stone can move from the row's cell to the column's cell.
    Capturing a cell zeroes its column. Mon collection is not modelled.
    """

    def __init__(self, game, player, search_depth=7):
        super().__init__(game, player)
        self.search_depth = search_depth
        self.total_iterations = 0

    def _build_board(self):
        state = self.game.state
        matrix = np.zeros((NUMBER_OF_CELLS, NUMBER_OF_CELLS), dtype="int")
        for cursor in range(NUMBER_OF_CELLS):
            state_at_cursor = dataclasses.replace(state, cursor=cursor)
            matrix[cursor, self.game.legal_moves(state_at_cursor)] = 1
            matrix[cursor, cursor] = tile_weight(state.tiles[cursor])
        return matrix, state.cursor

    def take_turn(self):
        self.total_iterations = 0

        move, evaluation = self._alpha_beta(self._build_board())

        logger.info("Decided on move %s capturing a %s", move, self.game.state.tiles[move])
        logger.info("Total iterations needed for tree search: %d", self.total_iterations)
        logger.info("Evaluated my position as: %s", evaluation)

        self.game.show_evaluation(evaluation)
        self.game.play_move(move)

    @staticmethod
    def _legal_moves(board):
        matrix, cursor = board
        return [move for move in np.nonzero(matrix[cursor])[0] if move != cursor]  # Diagonal is the piece weight

    def _winner(self, board, player_to_move):
        """The winning Player, or None while the game goes on."""
        matrix, _ = board
        weights = set(np.diagonal(matrix))
        katana, kabuto = PieceType.KATANA.value, PieceType.KABUTO.value
        for loser in (player_to_move, player_to_move.opponent):
            if loser.sign * katana not in weights or loser.sign * kabuto not in weights:
                return loser.opponent
        if not self._legal_moves(board):
            return player_to_move.opponent
        return None

    def _alpha_beta(self, board, depth=0, alpha=-np.inf, beta=np.inf):
        """Returns (best move, its value). Even depths are this player's moves (maximizing)."""
        self.total_iterations += 1
        matrix, cursor = board

        maximizing = depth % 2 == 0
        player_to_move = self.player if maximizing else self.player.opponent

        winner = self._winner(board, player_to_move)
        if winner:
            score = WIN_SCORE - depth  # Prefer faster wins and slower losses
            return None, score if winner is self.player else -score

        if depth > self.search_depth:
            return None, np.trace(matrix) * self.player.sign  # Material balance

        best_value = -np.inf if maximizing else np.inf
        best_move = None

        for move in self._legal_moves(board):
            next_matrix = matrix.copy()
            next_matrix[:, move] = 0
            _, value = self._alpha_beta((next_matrix, move), depth + 1, alpha, beta)

            if depth == 0:
                logger.debug("Move: %s   Evaluation: %s", move, value)

            if maximizing and value > best_value:
                best_value, best_move = value, move
                alpha = max(alpha, best_value)
            elif not maximizing and value < best_value:
                best_value, best_move = value, move
                beta = min(beta, best_value)

            if alpha >= beta:
                break

        return best_move, best_value
