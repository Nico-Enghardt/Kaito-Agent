"""Play headless games between computer players: python -m kaito.simulate --games 10 --red random --black alphabeta"""
import argparse
import logging

from kaito.game import KaitoGame
from kaito.pieces import Player
from kaito.players import AlphaBetaPlayer, MatrixSearchPlayer, RandomPlayer

PLAYER_TYPES = {"random": RandomPlayer, "alphabeta": AlphaBetaPlayer, "matrix": MatrixSearchPlayer}


def play_games(number_of_games, red_player_type, black_player_type, verbose=False):
    """Returns the number of wins as [red, black]."""
    wins = [0, 0]
    for game_number in range(number_of_games):
        game = KaitoGame()
        red_player_type(game, Player.RED)
        black_player_type(game, Player.BLACK)

        if verbose:
            print(f"Started game no. {game_number}")
        game.start_game()

        if game.state.winner:
            wins[game.state.winner.index] += 1

    if verbose:
        print("Wins [red, black]:", wins)
    return wins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--red", choices=PLAYER_TYPES, default="random")
    parser.add_argument("--black", choices=PLAYER_TYPES, default="alphabeta")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    play_games(args.games, PLAYER_TYPES[args.red], PLAYER_TYPES[args.black], verbose=True)


if __name__ == "__main__":
    main()
