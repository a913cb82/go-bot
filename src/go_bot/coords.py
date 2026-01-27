from typing import Tuple


def ogs_to_gtp(row: int, col: int, board_size: int) -> str:
    """
    Convert OGS (row, col) to GTP coordinates (e.g., "Q16").
    OGS (0,0) is top-left.
    GTP (0,0) is bottom-left (but uses letters for columns).
    'I' is skipped in GTP column letters.
    """
    letters = "ABCDEFGHJKLMNOPQRST"
    column_letter = letters[col]
    # OGS row 0 is top. GTP row 1 is bottom.
    # So GTP row = board_size - row
    gtp_row = board_size - row
    return f"{column_letter}{gtp_row}"


def gtp_to_ogs(gtp_coord: str, board_size: int) -> Tuple[int, int]:
    """
    Convert GTP coordinates (e.g., "Q16") to OGS (row, col).
    """
    if gtp_coord.upper() == "PASS":
        return (-1, -1)  # Using (-1, -1) as a sentinel for pass

    col_str = gtp_coord[0].upper()
    row_str = gtp_coord[1:]

    letters = "ABCDEFGHJKLMNOPQRST"
    col = letters.index(col_str)

    gtp_row = int(row_str)
    row = board_size - gtp_row

    return row, col


def ogs_coords_to_int(row: int, col: int, board_size: int) -> int:
    """
    Some OGS events use a single integer for coordinates: row * board_size + col.
    """
    if row == -1:
        return -1
    return row * board_size + col


def int_to_ogs_coords(pos: int, board_size: int) -> Tuple[int, int]:
    """
    Convert OGS integer position back to (row, col).
    """
    if pos == -1:
        return (-1, -1)
    return divmod(pos, board_size)
