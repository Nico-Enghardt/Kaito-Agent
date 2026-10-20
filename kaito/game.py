"""Kaito game rules and state."""
import copy
import logging
from dataclasses import dataclass, field

import numpy as np

from kaito.board import NUMBER_OF_CELLS, index_to_position
from kaito.pieces import (
    BUY_COST,
    COUNTED_PIECES,
    EMPTY_TILE,
    INITIAL_COUNTS,
    NUMBER_OF_EMPTY_TILES,
    Player,
    Tile,
)

logger = logging.getLogger(__name__)


@dataclass
class GameState:
    tiles: list  # Tile per cell index 0..35
    piece_counts: np.ndarray = field(default_factory=lambda: np.stack((INITIAL_COUNTS, INITIAL_COUNTS)))  # [red, black] x COUNTED_PIECES
    mon_balance: list = field(default_factory=lambda: [0, 0])  # [red, black]
    cursor: int = -1  # Index of the cell the game stone currently stands on
    move_number: int = 0
    winner: Player = None

    @property
    def is_finished(self):
        return self.winner is not None


def initial_tiles():
    tiles = []
    for piece, count in zip(COUNTED_PIECES, INITIAL_COUNTS):
        for owner in (Player.RED, Player.BLACK):
            tiles += [Tile(owner, piece) for _ in range(count)]
    tiles += [EMPTY_TILE] * NUMBER_OF_EMPTY_TILES
    np.random.shuffle(tiles)
    return tiles


class KaitoGame:
    """Holds the current GameState, enforces the rules and hands the turn to the registered players."""

    def __init__(self, view=None):
        self.players = [None, None]  # Computer players [red, black]; None means a human plays via the view
        self.state = GameState(tiles=initial_tiles())
        self.state.cursor = self.state.tiles.index(EMPTY_TILE)
        self.move_history = []  # [state before the move, move index] for every move played
        self.view = view

    def start_game(self):
        if self.players[0]:
            self.players[0].take_turn()

    def legal_moves(self, state=None):
        state = state or self.state
        return [index for index in range(NUMBER_OF_CELLS) if self.is_legal_move(state, index)]

    def is_legal_move(self, state, index):
        """The stone moves along its row or column, onto a non-empty cell."""
        move_column, move_row = index_to_position(index)
        cursor_column, cursor_row = index_to_position(state.cursor)
        on_line = (move_column == cursor_column) != (move_row == cursor_row)
        return on_line and not state.tiles[index].is_empty

    def current_player(self, state=None):
        """The player whose turn it is in `state` (default: the live game)."""
        state = state or self.state
        return Player.from_index(state.move_number % 2)

    def buy_piece(self, piece):
        """Spend Mon to put a new Katana or Kabuto on the cursor cell."""
        player = self.current_player()
        if self.state.mon_balance[player.index] < BUY_COST[piece]:
            logger.warning("%s cannot afford a %s.", player.value, piece.name.lower())
            return
        self.state.tiles[self.state.cursor] = Tile(player, piece)
        self.state.mon_balance[player.index] -= BUY_COST[piece]
        self.state.piece_counts[player.index, COUNTED_PIECES.index(piece)] += 1
        if self.view:
            self.view.draw()

    def play_move(self, index):
        if self.is_legal_move(self.state, index):
            self.move_history.append([copy.deepcopy(self.state), index])

        new_state = self.apply_move(self.state, index)
        if not new_state:
            return
        self.state = new_state

        player_to_move = self.players[self.current_player().index]
        self.check_winner(verbose=True)

        if self.view:
            self.view.draw()

        if player_to_move and not self.state.is_finished:
            player_to_move.take_turn()

    def show_evaluation(self, evaluation):
        if self.view:
            self.view.show_evaluation(evaluation)

    def collect_mon(self, owner, piece, state=None):
        """Mon balance after capturing a tile: capturing an own Mon tile earns its value."""
        state = state or self.state
        new_balance = state.mon_balance.copy()
        player = self.current_player(state)
        if player is owner and piece.is_mon:
            new_balance[player.index] += piece.mon_value
        return new_balance

    def check_winner(self, state=None, verbose=False):
        """Sets state.winner if a player lost all Katanas or Kabutos, or has no legal move left."""
        if state is None:
            state = self.state

        message = ""
        for loser in (Player.RED, Player.BLACK):
            katanas, kabutos = state.piece_counts[loser.index, :2]
            if katanas <= 0 or kabutos <= 0:
                state.winner = loser.opponent
                lost_piece = "Katanas" if katanas <= 0 else "Kabutos"
                message = f"{loser.value.capitalize()} lost all {lost_piece}. {state.winner.value.capitalize()} wins."

        if not state.is_finished and len(self.legal_moves(state)) == 0:
            loser = self.current_player(state)
            state.winner = loser.opponent
            message = f"{loser.value.capitalize()} has no legal move. {state.winner.value.capitalize()} wins."

        if verbose and message:
            logger.info(message)

    def apply_move(self, state, index):
        """Plays the move on `state` in place and returns it, or None if the move is illegal."""
        tile = state.tiles[index]
        if not self.is_legal_move(state, index):
            logger.warning("Suggested move to play was illegal!")
            return None

        state.mon_balance = self.collect_mon(tile.owner, tile.piece, state)
        if not tile.is_empty:
            state.piece_counts[tile.owner.index, COUNTED_PIECES.index(tile.piece)] -= 1

        state.tiles[index] = EMPTY_TILE
        state.cursor = index
        state.move_number += 1
        return state

    def material_matrix(self, state=None, perspective=Player.RED):
        """2x6 matrix [own, opponent] x (COUNTED_PIECES counts..., Mon balance)."""
        state = state or self.state
        matrix = np.concatenate((state.piece_counts, np.expand_dims(state.mon_balance, axis=1)), axis=1)
        if perspective is Player.BLACK:
            matrix = np.stack((matrix[1], matrix[0]), axis=0)
        return matrix
