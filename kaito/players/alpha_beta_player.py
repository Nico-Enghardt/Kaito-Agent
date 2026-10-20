import copy
import logging

import numpy as np

from kaito.evaluation import WIN_SCORE, material_evaluation
from kaito.players.base import BasePlayer

logger = logging.getLogger(__name__)


class AlphaBetaPlayer(BasePlayer):
    """Minimax search with alpha-beta pruning on full game states, scored by material_evaluation at the leaves."""

    def __init__(self, game, player, search_depth=6):
        super().__init__(game, player)
        self.search_depth = search_depth
        self.total_iterations = 0

    def take_turn(self):
        self.total_iterations = 0
        move, evaluation = self._alpha_beta(copy.deepcopy(self.game.state))
        logger.info("Total iterations needed for tree search: %d", self.total_iterations)
        logger.info("Evaluated my position as: %s", evaluation)
        self.game.show_evaluation(evaluation)
        self.game.play_move(move)

    def _alpha_beta(self, state, depth=0, alpha=-np.inf, beta=np.inf):
        """Returns (best move, its value from this player's point of view). Mutates `state` (winner)."""
        self.total_iterations += 1

        self.game.check_winner(state)
        if state.is_finished:
            score = WIN_SCORE - depth  # Prefer faster wins and slower losses
            return None, score if state.winner is self.player else -score

        if depth > self.search_depth:
            return None, material_evaluation(self.game.material_matrix(state, self.player))

        maximizing = self.game.current_player(state) is self.player
        best_value = -np.inf if maximizing else np.inf
        best_move = None

        for move in self.game.legal_moves(state):
            next_state = self.game.apply_move(copy.deepcopy(state), move)
            _, value = self._alpha_beta(next_state, depth + 1, alpha, beta)

            if maximizing and value > best_value:
                best_value, best_move = value, move
                alpha = max(alpha, best_value)
            elif not maximizing and value < best_value:
                best_value, best_move = value, move
                beta = min(beta, best_value)

            if alpha >= beta:
                break

        return best_move, best_value
