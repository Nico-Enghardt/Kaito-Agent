import random

from kaito.players.base import BasePlayer


class RandomPlayer(BasePlayer):
    """Plays a uniformly random legal move."""

    def take_turn(self):
        move = random.choice(self.game.legal_moves())
        self.game.play_move(move)
