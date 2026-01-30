#!/usr/bin/env python3
import sys
import time
import subprocess
import statistics
from typing import List, Sequence


def run_benchmark(command: Sequence[str], moves: int = 20) -> float:
    print(f"Benchmarking command: {' '.join(command)}")

    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
        )
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}")
        return 0.0

    def send_command(cmd: str) -> None:
        assert process.stdin is not None
        process.stdin.write(f"{cmd}\n")
        process.stdin.flush()

    def read_response() -> List[str]:
        assert process.stdout is not None
        response: List[str] = []
        while True:
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip()
            if line == "":
                if response:  # Empty line marks end of response
                    break
                else:  # Skip leading empty lines
                    continue
            response.append(line)
        return response

    # Initialize
    send_command("name")
    read_response()
    send_command("boardsize 19")
    read_response()
    send_command("komi 7.5")
    read_response()
    send_command("clear_board")
    read_response()

    latencies: List[float] = []

    print(f"Running {moves} genmove commands...")
    for i in range(moves):
        color = "black" if i % 2 == 0 else "white"

        start_time = time.time()
        send_command(f"genmove {color}")
        resp = read_response()
        end_time = time.time()

        duration_ms = (end_time - start_time) * 1000
        latencies.append(duration_ms)

        # Parse move to play it (so the game advances and doesn't just play on empty board every time if stateless)
        # Though for simple benchmarking, just genmove is mostly okay, but playing it keeps board state valid-ish.
        # GTP response format: "= Q16"
        if resp and resp[0].startswith("="):
            move = resp[0][2:].strip()
            # We don't strictly need to 'play' the move if the bot updates its own state on genmove,
            # but standard GTP implies genmove updates state.
            # If the bot is stateless (rare), we'd need to send 'play'.
            # KataGo and our RandomBot update state on genmove.
            print(f"Move {i+1}: {move} ({duration_ms:.2f}ms)")
        else:
            print(f"Error response: {resp}")

    # Cleanup
    send_command("quit")
    assert process.stdin is not None
    assert process.stdout is not None
    assert process.stderr is not None
    process.stdin.close()
    process.stdout.close()
    process.stderr.close()
    process.wait()

    if latencies:
        avg = statistics.mean(latencies)
        median = statistics.median(latencies)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        _min = min(latencies)
        _max = max(latencies)

        print("-" * 40)
        print(f"Statistics for {len(latencies)} moves:")
        print(f"  Min:    {_min:.2f} ms")
        print(f"  Max:    {_max:.2f} ms")
        print(f"  Avg:    {avg:.2f} ms")
        print(f"  Median: {median:.2f} ms")
        print(f"  95th%:  {p95:.2f} ms")
        print("-" * 40)

        return float(median)
    else:
        print("No latencies measured.")
        return 0.0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 benchmark_bot.py <bot_command> [args...]")
        sys.exit(1)

    run_benchmark(sys.argv[1:])
