"""Play Kaito in the GUI as red against the computer (black): python -m kaito"""
import logging
import sys

from PyQt6 import QtWidgets

from kaito.pieces import Player
from kaito.players import MatrixSearchPlayer
from kaito.ui.main_window import KaitoWindow


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    app = QtWidgets.QApplication(sys.argv)
    window = KaitoWindow()
    MatrixSearchPlayer(window.game, Player.BLACK)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
