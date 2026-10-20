import numpy as np
import pytest

from kaito.board import NUMBER_OF_CELLS, index_to_position, position_to_index
from kaito.game import GameState, KaitoGame
from kaito.pieces import EMPTY_TILE, INITIAL_COUNTS, PieceType, Player, Tile
from kaito.players import AlphaBetaPlayer, MatrixSearchPlayer, RandomPlayer


@pytest.fixture
def game():
    np.random.seed(0)
    return KaitoGame()


def test_index_position_round_trip():
    for index in range(NUMBER_OF_CELLS):
        assert position_to_index(*index_to_position(index)) == index
    assert index_to_position(0) == (1, 1)
    assert index_to_position(7) == (2, 2)


def test_initial_board(game):
    tiles = game.state.tiles
    assert len(tiles) == NUMBER_OF_CELLS
    assert tiles.count(EMPTY_TILE) == 2
    assert tiles[game.state.cursor].is_empty
    assert tiles.count(Tile(Player.RED, PieceType.KATANA)) == INITIAL_COUNTS[0]
    assert tiles.count(Tile(Player.BLACK, PieceType.KABUTO)) == INITIAL_COUNTS[1]


def test_legal_moves_follow_row_and_column(game):
    cursor_column, cursor_row = index_to_position(game.state.cursor)
    moves = game.legal_moves()
    assert moves
    for move in moves:
        column, row = index_to_position(move)
        assert (column == cursor_column) != (row == cursor_row)
        assert not game.state.tiles[move].is_empty


def _state_with(tile_at_target):
    tiles = [Tile(Player.BLACK, PieceType.MON1)] * NUMBER_OF_CELLS
    tiles[0] = EMPTY_TILE
    tiles[1] = tile_at_target
    return GameState(tiles=list(tiles), cursor=0)


def test_capturing_own_mon_earns_mon(game):
    game.state = _state_with(Tile(Player.RED, PieceType.MON3))
    game.apply_move(game.state, 1)
    assert game.state.mon_balance == [3, 0]
    assert game.state.cursor == 1
    assert game.state.tiles[1].is_empty


def test_capturing_opponent_piece_reduces_its_count(game):
    game.state = _state_with(Tile(Player.BLACK, PieceType.KATANA))
    game.apply_move(game.state, 1)
    assert game.state.piece_counts[Player.BLACK.index, 0] == INITIAL_COUNTS[0] - 1
    assert game.state.mon_balance == [0, 0]


def test_buying_costs_mon(game):
    game.state.mon_balance = [9, 0]
    game.buy_piece(PieceType.KABUTO)
    game.buy_piece(PieceType.KATANA)
    assert game.state.mon_balance == [0, 0]


def test_losing_all_katanas_ends_game(game):
    game.state.piece_counts[Player.RED.index, 0] = 0
    game.check_winner()
    assert game.state.winner is Player.BLACK


def test_players_register_in_their_slot(game):
    red = RandomPlayer(game, Player.RED)
    black = AlphaBetaPlayer(game, Player.BLACK)
    assert game.players == [red, black]


@pytest.mark.parametrize("black_type", [RandomPlayer, AlphaBetaPlayer, MatrixSearchPlayer])
def test_full_game_finishes(black_type):
    np.random.seed(1)
    game = KaitoGame()
    RandomPlayer(game, Player.RED)
    black = black_type(game, Player.BLACK)
    if hasattr(black, "search_depth"):
        black.search_depth = 2
    game.start_game()
    assert game.state.is_finished
