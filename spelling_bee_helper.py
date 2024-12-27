#!/usr/bin/env python3

import argparse
import csv

from rich.console import Console
from rich.table import Table

console = Console()

def parse_args():
    """
    Parse command-line arguments for the Spelling Bee helper.
    Example usage:
        python spelling_bee_helper.py \
            --center a \
            --others bcdert \
            --dictionary words_alpha.txt \
            --csv out.csv
    """
    parser = argparse.ArgumentParser(
        description="NYT Spelling Bee Solver with scoring, pangram detection, and optional CSV export."
    )
    parser.add_argument(
        "-c", "--center",
        required=True,
        help="Center letter for Spelling Bee puzzle (required)."
    )
    parser.add_argument(
        "-o", "--others",
        required=True,
        help="6 other letters for Spelling Bee puzzle (required)."
    )
    parser.add_argument(
        "-d", "--dictionary",
        default="words.txt",
        help="Path to dictionary file (default: words.txt)."
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        default=None,
        help="Optional path to output CSV file with results."
    )
    return parser.parse_args()

def load_dictionary(dictionary_path: str) -> list:
    """Loads words from a text file, returning them as a list of lowercase words."""
    with open(dictionary_path, 'r', encoding='utf-8') as f:
        words = [w.strip().lower() for w in f if w.strip()]
    return words

def is_valid_word(word: str, center: str, letters_set: set) -> bool:
    """
    A valid Spelling Bee word must:
      1. Be at least 4 letters long.
      2. Contain the center letter at least once.
      3. Use only letters from the letters_set (no outside letters).
    """
    if len(word) < 4:
        return False
    if center not in word:
        return False
    return all(char in letters_set for char in word)

def is_pangram(word: str, letters_set: set) -> bool:
    """
    Returns True if 'word' contains ALL letters in letters_set at least once,
    i.e., it uses all 7 letters -> pangram.
    """
    return all(letter in word for letter in letters_set)

def compute_score(word: str, letters_set: set) -> int:
    """
    Compute a Spelling Bee style score:
      - 4-letter word => 1 point
      - 5-letter word => 2 points, etc. (i.e., word length - 3)
      - If the word is a pangram, add +7 bonus points.
    """
    base_score = max(1, len(word) - 3)  # At least 1 point for 4-letter words
    if is_pangram(word, letters_set):
        base_score += 7
    return base_score

def gather_statistics(valid_words, letters_set):
    """
    Gathers additional stats:
      - Total words
      - Number of pangrams
      - Average word length
      - Sum of scores
    """
    total_words = len(valid_words)
    pangrams_count = sum(is_pangram(w, letters_set) for w, s in valid_words)
    avg_length = sum(len(w) for w, s in valid_words) / total_words if total_words else 0
    total_points = sum(s for w, s in valid_words)

    return {
        "total_words": total_words,
        "pangrams_count": pangrams_count,
        "avg_length": avg_length,
        "total_points": total_points,
    }

def find_spelling_bee_words(dictionary_path: str, center: str, other_letters: str, csv_path: str = None):
    """
    1. Loads the dictionary.
    2. Filters valid words based on Spelling Bee constraints.
    3. Calculates each word's score.
    4. Prints the results sorted by descending score, then length, then alphabetical.
    5. Optionally writes the results to CSV if csv_path is provided.
    """
    # Normalize letters to lowercase
    center = center.lower()
    other_letters = other_letters.lower()

    # Build the set of 7 letters
    letters_set = set(center + other_letters)

    # Load all dictionary words
    word_list = load_dictionary(dictionary_path)

    # Filter valid words and compute their scores
    valid_words = []
    for word in word_list:
        if is_valid_word(word, center, letters_set):
            score = compute_score(word, letters_set)
            valid_words.append((word, score))

    # Sort by descending score, then by descending word length, then alphabetically
    valid_words.sort(key=lambda ws: (-ws[1], -len(ws[0]), ws[0]))

    # Gather additional statistics
    stats = gather_statistics(valid_words, letters_set)

    # --- PRINTING RESULTS (with Rich) ---
    table = Table(title="Spelling Bee Results")
    table.add_column("Word", justify="left", style="cyan", no_wrap=True)
    table.add_column("Score", justify="right", style="magenta")
    table.add_column("Pangram?", justify="center", style="green")

    # Build table rows
    for (w, s) in valid_words:
        pangram_flag = "Yes" if is_pangram(w, letters_set) else ""
        table.add_row(w, str(s), pangram_flag)

    # Print summary info above the table
    console.print("============================================", style="bold yellow")
    console.print(f"Letters Used     : {', '.join(sorted(letters_set))} (Center = '{center}')", style="bold white")
    console.print(f"Dictionary       : {dictionary_path}", style="bold white")
    console.print(f"Total words      : {stats['total_words']}", style="bold white")
    console.print(f"Number pangrams  : {stats['pangrams_count']}", style="bold white")
    console.print(f"Average length   : {stats['avg_length']:.2f}", style="bold white")
    console.print(f"Sum of all scores: {stats['total_points']}", style="bold white")
    console.print("============================================", style="bold yellow")

    # Print the table of words
    console.print(table)

    # --- OPTIONAL CSV EXPORT ---
    if csv_path:
        try:
            with open(csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["word", "score", "pangram"])
                for (w, s) in valid_words:
                    writer.writerow([w, s, "Yes" if is_pangram(w, letters_set) else "No"])
            console.print(f"\n[green]Results successfully written to {csv_path}![/green]")
        except Exception as e:
            console.print(f"[red]Failed to write CSV file: {e}[/red]")

def main():
    args = parse_args()
    find_spelling_bee_words(
        dictionary_path=args.dictionary,
        center=args.center,
        other_letters=args.others,
        csv_path=args.csv_path,
    )

if __name__ == "__main__":
    main()
