#!/usr/bin/env python3
import sys
import random
import logging
from sgfmill import boards

# Configure logging to stderr so it shows up in gtp2ogs logs
logging.basicConfig(
    level=logging.INFO, stream=sys.stderr, format="%(levelname)s: %(message)s"
)


def main() -> None:
    board_size = 19
    board = boards.Board(board_size)

    letters = "ABCDEFGHJKLMNOPQRST"

    def _get_coord_str(c: int, r: int) -> str:
        return f"{letters[c]}{r+1}"

    while True:
        line = sys.stdin.readline()
        if not line:
            break

        line = line.strip()
        if not line:
            continue

        logging.debug(f"Received: {line}")

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
            print(f"={cmdid} 0.3\n")
        elif command == "list_methods" or command == "list_commands":
            print(
                f"={cmdid} protocol_version\nname\nversion\nlist_commands\nboardsize\nclear_board\nplay\ngenmove\nkomi\nfixed_handicap\nplace_free_handicap\nset_free_handicap\ntime_settings\ntime_left\nquit\n"
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
        elif command == "komi":
            try:
                # We just accept it, don't need to store it for random moves
                print(f"={cmdid}\n")
            except Exception:
                print(f"?{cmdid} invalid komi\n")
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

                    # Idempotent play: if the stone is already there, don't error
                    if board.get(c, r) == color:
                        logging.debug(f"Idempotent play at {coord}")
                    else:
                        board.play(c, r, color)
                print(f"={cmdid}\n")
            except Exception as e:
                print(f"?{cmdid} illegal move: {str(e)}\n")
        elif command == "genmove":
            color = "b" if args[0].lower() == "black" else "w"

            legal_moves = []
            for r in range(board_size):
                for c in range(board_size):
                    if board.get(c, r) is None:
                        test_board = board.copy()
                        try:
                            test_board.play(c, r, color)
                            if test_board.get(c, r) is None:
                                continue
                            legal_moves.append((c, r))
                        except ValueError:
                            continue

            if not legal_moves:
                move_str = "pass"
            else:
                c, r = random.choice(legal_moves)
                move_str = _get_coord_str(c, r)
                board.play(c, r, color)

            print(f"={cmdid} {move_str}\n")
        elif command == "fixed_handicap":
            # fixed_handicap returns coordinates of placed stones
            # For simplicity, we just return empty list or pick N random ones
            try:
                n = int(args[0])
                empty_points = [
                    (c, r)
                    for r in range(board_size)
                    for c in range(board_size)
                    if board.get(c, r) is None
                ]
                if len(empty_points) < n:
                    print(f"?{cmdid} not enough space for handicap\n")
                else:
                    chosen = random.sample(empty_points, n)
                    coords = []
                    for c, r in chosen:
                        board.play(c, r, "b")
                        coords.append(_get_coord_str(c, r))
                    print(f"={cmdid} {' '.join(coords)}\n")
            except Exception:
                print(f"?{cmdid} error in handicap\n")
        elif command == "place_free_handicap":
            try:
                n = int(args[0])
                empty_points = [
                    (c, r)
                    for r in range(board_size)
                    for c in range(board_size)
                    if board.get(c, r) is None
                ]
                chosen = random.sample(empty_points, min(n, len(empty_points)))
                coords = []
                for c, r in chosen:
                    board.play(c, r, "b")
                    coords.append(_get_coord_str(c, r))
                print(f"={cmdid} {' '.join(coords)}\n")
            except Exception:
                print(f"?{cmdid} error in free handicap\n")
        elif command == "set_free_handicap":
            try:
                for coord in args:
                    coord = coord.upper()
                    col_str = coord[0]
                    row_str = coord[1:]
                    c = letters.index(col_str)
                    r = int(row_str) - 1
                    board.play(c, r, "b")
                print(f"={cmdid}\n")
            except Exception:
                print(f"?{cmdid} error in set free handicap\n")
        elif command in ["time_settings", "time_left"]:
            print(f"={cmdid}\n")
        elif command == "quit":
            print(f"={cmdid}\n")
            break
        else:
            logging.warning(f"Unknown command: {command}")
            print(f"?{cmdid} unknown command\n")

        sys.stdout.flush()


if __name__ == "__main__":
    main()
