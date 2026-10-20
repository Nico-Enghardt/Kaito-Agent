import logging
from pathlib import Path

import numpy as np
from PyQt6 import QtCore, QtGui, QtWidgets, uic

from kaito.board import NUMBER_OF_CELLS, cell_name, index_to_position
from kaito.game import KaitoGame
from kaito.pieces import BUY_COST, PieceType, Player

logger = logging.getLogger(__name__)

UI_FILE = Path(__file__).with_name("main_window.ui")
ICON_DIR = Path(__file__).resolve().parents[2] / "assets" / "icons"
ICON_SIZE = QtCore.QSize(76, 76)
PLAYER_COLORS = {Player.RED: "red", Player.BLACK: "darkgray"}


class KaitoWindow(QtWidgets.QMainWindow):
    """Board view for a human player. Widgets come from main_window.ui (cell1_1 .. cell6_6, buy buttons, labels)."""

    def __init__(self):
        super().__init__()
        uic.loadUi(UI_FILE, self)
        self.show()

        self.game = KaitoGame(view=self)

        self.buyKabutoButton.clicked.connect(lambda: self.game.buy_piece(PieceType.KABUTO))
        self.buyKatanaButton.clicked.connect(lambda: self.game.buy_piece(PieceType.KATANA))

        self.cells = [getattr(self, cell_name(index)) for index in range(NUMBER_OF_CELLS)]
        for index, cell in enumerate(self.cells):
            cell.setText("")
            cell.setIconSize(ICON_SIZE)
            # Keep the grid slot when the cell is hidden, so empty rows/columns don't collapse.
            policy = cell.sizePolicy()
            policy.setRetainSizeWhenHidden(True)
            cell.setSizePolicy(policy)
            cell.clicked.connect(lambda _checked=False, index=index: self.on_cell_clicked(index))

        self.redMonCount.setStyleSheet(" color: red")
        self.redMonLabel.setStyleSheet(" color: red")

        self.draw()

    def on_cell_clicked(self, index):
        self.game.play_move(index)
        self.draw()

    def show_evaluation(self, evaluation):
        # Values outside the bar's range would be ignored by setValue, so clamp them
        bar = self.evaluationBar
        bar.setValue(int(np.clip(evaluation, bar.minimum(), bar.maximum())))

    def draw(self):
        state = self.game.state
        current_player = self.game.current_player()

        self.redMonCount.setText(str(state.mon_balance[Player.RED.index]))
        self.blackMonCount.setText(str(state.mon_balance[Player.BLACK.index]))

        balance = state.mon_balance[current_player.index]
        self.buyKatanaButton.setEnabled(balance >= BUY_COST[PieceType.KATANA])
        self.buyKabutoButton.setEnabled(balance >= BUY_COST[PieceType.KABUTO])

        if state.is_finished:
            logger.info("Game is finished.")
            self.resultLabel.setText("Red wins!" if state.winner is Player.RED else "Black wins!")

        cursor_column, cursor_row = index_to_position(state.cursor)
        color = PLAYER_COLORS[current_player]

        for index, cell in enumerate(self.cells):
            tile = state.tiles[index]
            column, row = index_to_position(index)

            icon = QtGui.QIcon() if tile.is_empty else QtGui.QIcon(str(ICON_DIR / f"{tile.icon_name}.jpg"))
            cell.setIcon(icon)

            reachable = (cursor_column == column) != (cursor_row == row)
            if reachable and not tile.is_empty:
                cell.setStyleSheet(f":active{{background-color: {color}}} :hover {{  background-color: white}}")
            else:
                cell.setStyleSheet(" background-color: rgb(240,240,240)")

            cell.setVisible(not tile.is_empty and not state.is_finished)
