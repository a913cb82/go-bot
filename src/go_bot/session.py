from typing import List, Tuple, cast
from sgfmill import boards, ascii_boards
from go_bot.coords import ogs_to_gtp


class GameSession:
    def __init__(self, game_id: str, board_size: int = 19):
        self.game_id = game_id
        self.board_size = board_size
        self.board = boards.Board(board_size)
        self.moves: List[Tuple[str, int, int]] = []  # List of (color, row, col)
        self.turn = "black"  # OGS usually starts with black

    def apply_move(self, color: str, row: int, col: int) -> None:
        """
        Applies a move to the board.
        color: 'black' or 'white'
        row, col: OGS coordinates (0-indexed from top-left). -1 for pass.
        """
        color_code = "b" if color.lower() == "black" else "w"
        if row == -1 and col == -1:
            self.moves.append((color.lower(), -1, -1))
        else:
            self.board.play(col, self.board_size - 1 - row, color_code)
            self.moves.append((color.lower(), row, col))

        self.turn = "white" if color.lower() == "black" else "black"

    def get_gtp_history(self) -> List[str]:
        """
        Returns the history of moves in GTP format: ["play black Q16", "play white D4", ...]
        """
        history = []
        for color, row, col in self.moves:
            if row == -1:
                coord = "pass"
            else:
                coord = ogs_to_gtp(row, col, self.board_size)
            history.append(f"play {color} {coord}")
        return history

    def __str__(self) -> str:
        return cast(str, ascii_boards.render_board(self.board))
