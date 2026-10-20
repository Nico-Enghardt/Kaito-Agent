"""Players, piece types and the static piece configuration of Kaito."""
from enum import Enum

import numpy as np


class Player(Enum):
    RED = "red"
    BLACK = "black"

    @property
    def index(self):
        """Slot of this player in per-player arrays: red = 0, black = 1."""
        return 0 if self is Player.RED else 1

    @property
    def sign(self):
        """Score sign used by the search players: black = +1, red = -1."""
        return 1 if self is Player.BLACK else -1

    @property
    def opponent(self):
        return Player.BLACK if self is Player.RED else Player.RED

    @staticmethod
    def from_index(index):
        return Player.RED if index == 0 else Player.BLACK


class PieceType(Enum):
    # The value doubles as the piece's weight in the matrix search player.
    EMPTY = 0
    MON1 = 1
    MON2 = 2
    MON3 = 3
    KATANA = 4
    KABUTO = 5

    @property
    def is_mon(self):
        return self in (PieceType.MON1, PieceType.MON2, PieceType.MON3)

    @property
    def mon_value(self):
        return self.value if self.is_mon else 0


# Order of the columns in GameState.piece_counts
COUNTED_PIECES = [PieceType.KATANA, PieceType.KABUTO, PieceType.MON3, PieceType.MON2, PieceType.MON1]
INITIAL_COUNTS = np.array([7, 3, 2, 2, 3])
NUMBER_OF_EMPTY_TILES = 2

BUY_COST = {PieceType.KABUTO: 5, PieceType.KATANA: 4}


class Tile:
    """A board cell: an owned piece, or empty (owner None)."""

    __slots__ = ("owner", "piece")

    def __init__(self, owner, piece):
        self.owner = owner
        self.piece = piece

    @property
    def is_empty(self):
        return self.piece is PieceType.EMPTY

    @property
    def icon_name(self):
        return f"{self.owner.value}_{self.piece.name.lower()}"

    def __eq__(self, other):
        return isinstance(other, Tile) and (self.owner, self.piece) == (other.owner, other.piece)

    def __hash__(self):
        return hash((self.owner, self.piece))

    def __deepcopy__(self, memo):
        # Tiles are never mutated, so game-state copies can share them.
        return self

    def __repr__(self):
        return "empty" if self.is_empty else self.icon_name


EMPTY_TILE = Tile(None, PieceType.EMPTY)
