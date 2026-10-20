class BasePlayer:
    """A computer player. Registers itself with the game, which calls take_turn() whenever it is this player's move."""

    def __init__(self, game, player):
        self.game = game
        self.player = player
        game.players[player.index] = self

    def take_turn(self):
        raise NotImplementedError
