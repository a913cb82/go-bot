#!/usr/bin/env python3
import sys


def main() -> None:
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue

        if "quit" in line:
            # Be unresponsive or crash
            sys.exit(1)
        elif "genmove" in line:
            # Send garbage then a valid response
            print("? invalid command")
            print("")
            sys.stdout.flush()
        elif "boardsize" in line:
            # Send partial response then close
            print("= ")
            # No newline
            sys.exit(0)
        else:
            print("= \n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
