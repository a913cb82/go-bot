from go_bot.coords import (
    ogs_to_gtp,
    gtp_to_ogs,
    int_to_ogs_coords,
    ogs_coords_to_int,
    ogs_to_str,
    str_to_ogs,
)
from go_bot.session import GameSession


def test_coordinate_conversion() -> None:
    # 19x19 board
    # OGS (0,0) top-left -> GTP A19 (wait, column A is index 0, letters[0])
    # letters = "ABCDEFGHJKLMNOPQRST" (no I)
    assert ogs_to_gtp(0, 0, 19) == "A19"
    assert ogs_to_gtp(18, 0, 19) == "A1"
    assert ogs_to_gtp(0, 18, 19) == "T19"
    assert ogs_to_gtp(3, 3, 19) == "D16"

    assert gtp_to_ogs("A19", 19) == (0, 0)
    assert gtp_to_ogs("D16", 19) == (3, 3)
    assert gtp_to_ogs("PASS", 19) == (-1, -1)


def test_int_coords() -> None:
    assert ogs_coords_to_int(0, 5, 19) == 5
    assert ogs_coords_to_int(1, 0, 19) == 19
    assert int_to_ogs_coords(19, 19) == (1, 0)


def test_ogs_string_coords() -> None:
    assert ogs_to_str(0, 0) == "aa"
    assert ogs_to_str(3, 15) == "pd"
    assert ogs_to_str(-1, -1) == ""

    assert str_to_ogs("aa") == (0, 0)
    assert str_to_ogs("pd") == (3, 15)
    assert str_to_ogs("") == (-1, -1)


def test_game_session() -> None:
    session = GameSession("test_game", 19)
    session.apply_move("black", 3, 3)  # D16
    session.apply_move("white", 15, 15)  # Q4

    history = session.get_gtp_history()
    assert history == ["play black D16", "play white Q4"]
    assert session.turn == "black"  # Started black, played B then W, now B turn
