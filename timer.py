#!/usr/bin/env python3
"""Focus Timer — a terminal Pomodoro timer with live progress bar."""

import time
import sys
import os
import json
from datetime import datetime, timedelta

WORK_MINUTES = 25
SHORT_BREAK = 5
LONG_BREAK = 15
SESSIONS_BEFORE_LONG_BREAK = 4

STATS_FILE = os.path.join(os.path.dirname(__file__), "stats.json")

COLORS = {
    "red":    "\033[91m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "blue":   "\033[94m",
    "cyan":   "\033[96m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "reset":  "\033[0m",
}

def c(color, text):
    return f"{COLORS[color]}{text}{COLORS['reset']}"

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE) as f:
            return json.load(f)
    return {"total_sessions": 0, "total_minutes": 0, "streak_date": None, "streak": 0}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def update_streak(stats):
    today = datetime.now().strftime("%Y-%m-%d")
    if stats["streak_date"] == today:
        pass
    elif stats["streak_date"] == (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"):
        stats["streak"] += 1
    else:
        stats["streak"] = 1
    stats["streak_date"] = today

def draw_progress_bar(elapsed, total, width=40):
    filled = int(width * elapsed / total)
    bar = "█" * filled + "░" * (width - filled)
    pct = int(100 * elapsed / total)
    return f"[{bar}] {pct:3d}%"

def countdown(label, minutes, color="cyan"):
    total = minutes * 60
    print()
    try:
        for elapsed in range(total + 1):
            remaining = total - elapsed
            mins, secs = divmod(remaining, 60)
            bar = draw_progress_bar(elapsed, total)
            line = (
                f"\r  {c(color, c('bold', label))}  "
                f"{c('bold', f'{mins:02d}:{secs:02d}')}  "
                f"{c('dim', bar)}"
            )
            print(line, end="", flush=True)
            if elapsed < total:
                time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n  {c('yellow', 'Timer paused. Press Enter to continue or Ctrl+C again to quit.')}")
        try:
            input()
            # Resume by recursing with remaining time
            remaining_mins = (total - elapsed) / 60
            countdown(label, remaining_mins, color)
            return
        except KeyboardInterrupt:
            print(f"\n\n  {c('red', 'Session cancelled.')}\n")
            sys.exit(0)

    # Done — ring the bell
    print(f"\r  {c(color, c('bold', label))}  {c('green', '✓ Done!')}  {c('dim', draw_progress_bar(total, total))}")
    sys.stdout.write("\a")
    sys.stdout.flush()

def print_header(session_num, stats):
    os.system("clear" if os.name != "nt" else "cls")
    streak_text = f"🔥 {stats['streak']}-day streak" if stats["streak"] > 1 else ""
    print()
    print(c("bold", "  ┌─────────────────────────────────────┐"))
    print(c("bold", "  │") + c("cyan", c("bold", "          🍅  FOCUS TIMER              ")) + c("bold", "│"))
    print(c("bold", "  └─────────────────────────────────────┘"))
    print()
    print(f"  Session {c('bold', str(session_num))}  •  "
          f"All-time: {c('cyan', str(stats['total_sessions']))} sessions  "
          f"{c('yellow', streak_text)}")
    print()

def prompt_continue(message):
    print(f"\n  {c('dim', message)}", end="")
    try:
        input()
    except KeyboardInterrupt:
        print(f"\n\n  {c('yellow', 'Goodbye! Great work today.')}\n")
        sys.exit(0)

def main():
    stats = load_stats()
    session_num = stats["total_sessions"] + 1

    print_header(session_num, stats)
    print(f"  {c('dim', 'Work: 25 min  |  Short break: 5 min  |  Long break: 15 min (every 4 sessions)')}")
    print(f"\n  {c('dim', 'Press Enter to start your focus session...')}", end="")
    try:
        input()
    except KeyboardInterrupt:
        print()
        sys.exit(0)

    cycle_position = ((session_num - 1) % SESSIONS_BEFORE_LONG_BREAK) + 1

    while True:
        print_header(session_num, stats)
        print(f"  {c('dim', f'Session {cycle_position}/{SESSIONS_BEFORE_LONG_BREAK} before long break')}")

        countdown("FOCUS", WORK_MINUTES, color="cyan")

        stats["total_sessions"] += 1
        stats["total_minutes"] += WORK_MINUTES
        update_streak(stats)
        save_stats(stats)
        session_num += 1

        if cycle_position == SESSIONS_BEFORE_LONG_BREAK:
            prompt_continue(f"  Great work! Take a {LONG_BREAK}-min long break. Press Enter when ready...")
            print_header(session_num, stats)
            countdown("LONG BREAK", LONG_BREAK, color="green")
            cycle_position = 1
        else:
            prompt_continue(f"  Nice! Take a {SHORT_BREAK}-min short break. Press Enter when ready...")
            print_header(session_num, stats)
            countdown("SHORT BREAK", SHORT_BREAK, color="yellow")
            cycle_position += 1

        prompt_continue("  Break's over! Press Enter to start the next focus session...")

if __name__ == "__main__":
    main()
