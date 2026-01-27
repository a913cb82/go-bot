#!/usr/bin/env python3
import sys
import random
from sgfmill import boards


def main() -> None:
    board_size = 19
    board = boards.Board(board_size)

    letters = "ABCDEFGHJKLMNOPQRST"

    while True:
        line = sys.stdin.readline()
        if not line:
            break

        line = line.strip()
        if not line:
            continue

        parts = line.split()
        cmdid = ""
        if parts[0].isdigit():
            cmdid = parts[0]
            parts = parts[1:]

        command = parts[0]
        args = parts[1:]

        if command == "protocol_version":
            print(f"={cmdid} 2\n")
        elif command == "name":
            print(f"={cmdid} RandomGTP\n")
        elif command == "version":
            print(f"={cmdid} 0.1\n")
        elif command == "list_methods" or command == "list_commands":
            print(
                f"={cmdid} protocol_version\nname\nversion\nlist_commands\nboardsize\nclear_board\nplay\ngenmove\nquit\n"
            )
        elif command == "boardsize":
            try:
                board_size = int(args[0])
                board = boards.Board(board_size)
                print(f"={cmdid}\n")
            except Exception:
                print(f"?{cmdid} invalid boardsize\n")
        elif command == "clear_board":
            board = boards.Board(board_size)
            print(f"={cmdid}\n")
        elif command == "play":
            try:
                color = "b" if args[0].lower() == "black" else "w"
                coord = args[1].upper()
                if coord != "PASS":
                    col_str = coord[0]
                    row_str = coord[1:]
                    if col_str not in letters:
                        raise ValueError("Invalid column")
                    c = letters.index(col_str)
                    r = int(row_str) - 1
                    board.play(c, r, color)
                print(f"={cmdid}\n")
            except Exception as e:
                # GTP standard says to return error for illegal moves
                print(f"?{cmdid} illegal move: {str(e)}\n")
        elif command == "genmove":
            color = "b" if args[0].lower() == "black" else "w"

            legal_moves = []
            for r in range(board_size):
                for c in range(board_size):
                    if board.get(c, r) is None:
                        # Test if move is legal by trying to play it on a copy
                        test_board = board.copy()
                        try:
                            test_board.play(c, r, color)
                            # Suicide check: if the point we just played is empty,
                            # it means it was captured (suicide) because sgfmill allows it.
                            if test_board.get(c, r) is None:
                                continue
                            legal_moves.append((c, r))
                        except ValueError:
                            # Illegal move (Ko)
                            continue

            if not legal_moves:
                move_str = "pass"
            else:
                c, r = random.choice(legal_moves)
                move_str = f"{letters[c]}{r+1}"
                board.play(c, r, color)

            print(f"={cmdid} {move_str}\n")
        elif command == "quit":
            print(f"={cmdid}\n")
            break
        else:
            print(f"?{cmdid} unknown command\n")

        sys.stdout.flush()


if __name__ == "__main__":
    main()
