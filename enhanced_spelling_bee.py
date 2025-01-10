
import csv
import nltk
from rich.console import Console
from rich.table import Table
from collections import Counter

console = Console()

#-------------------------Download and process corpus-------------------------

nltk.download('gutenberg')
from nltk.corpus import gutenberg

# Combine all words in Gutenberg corpus
corpus = " ".join(gutenberg.words()).lower()

# Remove non-alphabetic characters
import re
corpus = re.sub(r'[^a-z\s]', '', corpus)

from collections import Counter

# Bigram frequencies
bigram_freq = Counter(corpus[i:i+2] for i in range(len(corpus) - 1))
# Trigram frequencies
trigram_freq = Counter(corpus[i:i+3] for i in range(len(corpus) - 2))

# ------------------------ GLOBAL CACHE ------------------------
_DICTIONARY_CACHE = None

def get_dictionary(dictionary_path: str):
    """
    Loads and caches the dictionary so we don't repeatedly read from disk.
    Returns a list of lowercase words.
    """
    global _DICTIONARY_CACHE
    if _DICTIONARY_CACHE is not None:
        # Already loaded; no need to load again
        return _DICTIONARY_CACHE
    
    # Otherwise, load from file
    try:
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            words = [w.strip().lower() for w in f if w.strip()]
        _DICTIONARY_CACHE = words
        return words
    except Exception as e:
        console.print(f"[red]Failed to load dictionary: {e}[/red]")
        return []

# ------------------------ SPELLING BEE LOGIC ------------------------

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

def bigram_score(word, bigram_freq):
    """
    Calculate a score for the word based on bigram frequencies.
    """
    return sum(bigram_freq.get(word[i:i+2], 0) for i in range(len(word) - 1))

def trigram_score(word, trigram_freq):
    """
    Calculate a score for the word based on trigram frequencies.
    """
    return sum(trigram_freq.get(word[i:i+3], 0) for i in range(len(word) - 2))

def combined_score(word, bigram_freq, trigram_freq, weight=0.5):
    """
    Combine bigram and trigram scores with a weighted average.
    """
    score_b = bigram_score(word, bigram_freq)
    score_t = trigram_score(word, trigram_freq)
    return score_b * weight + score_t * (1 - weight)

def compute_score(word: str, letters_set: set) -> int:
    """
    Compute a NYT Spelling Bee style score:
      - 4-letter word => 1 point
      - 5-letter word => 2 points
      - 6-letter word => 3 points
      - 7-letter word => 4 points
      - etc. => word length - 3
      - If the word is a pangram, add +7 bonus points.
    """
    # For words of length >= 4, score = (length - 3)
    base_score = max(1, len(word) - 3)
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
def is_valid_for_spelling_bee(word, letters, center_letter):
    """
    Check if a word is valid for Spelling Bee:
    - Contains the center letter.
    - Only uses the provided 7 letters.
    - Has a minimum length of 4.
    """
    return (
        len(word) >= 4 and
        center_letter in word and
        all(c in letters for c in word)
    )

def find_valid_words(letters, center_letter, dictionary, bigram_freq, trigram_freq):
    """
    Find valid Spelling Bee words and rank them by combined score.
    """
    candidates = [
        word for word in dictionary
        if is_valid_for_spelling_bee(word, letters, center_letter)
    ]
    # Score and sort candidates
    scored_candidates = [
        (word, combined_score(word, bigram_freq, trigram_freq))
        for word in candidates
    ]
    return sorted(scored_candidates, key=lambda x: x[1], reverse=True)

def find_spelling_bee_words(
    dictionary_path: str,
    center: str,
    other_letters: str,
    min_length: int = 4,
    max_length: int = 0,
    must_contain: str = "",
):
    """
    1. Loads (and caches) the dictionary from disk.
    2. Filters valid words based on Spelling Bee constraints.
    3. Applies additional filters:
       - min_length
       - max_length (0 = no max)
       - must_contain (partial substring)
    4. Calculates each word's score and returns the list of (word, score).
    """
    # Normalize letters to lowercase
    center = center.lower()
    other_letters = other_letters.lower()

    # Build the set of 7 letters
    letters_set = set(center + other_letters)

    # Get the dictionary (cached)
    word_list = get_dictionary(dictionary_path)

    # Filter valid words and compute their scores
    valid_words = []
    for word in word_list:
        if not is_valid_word(word, center, letters_set):
            continue
        # Check min_length
        if len(word) < min_length:
            continue
        # Check max_length (if > 0 means we have a limit)
        if max_length > 0 and len(word) > max_length:
            continue
        # Check must_contain substring
        if must_contain and must_contain.lower() not in word:
            continue
        
        score = compute_score(word, letters_set)
        valid_words.append((word, score))

    # Sort by descending score, then by descending word length, then alphabetical
    valid_words.sort(key=lambda ws: (-ws[1], -len(ws[0]), ws[0]))

    return valid_words, letters_set

def print_results(valid_words, letters_set, dictionary_path, min_length, max_length, must_contain,center):
    """
    Prints results in a rich-formatted table and summary statistics.
    """
    # Gather additional statistics
    stats = gather_statistics(valid_words, letters_set)

    # Build a Rich table
    table = Table(title="Spelling Bee Results")
    table.add_column("Word", justify="left", style="cyan", no_wrap=True)
    table.add_column("Score", justify="right", style="magenta")
    table.add_column("Pangram?", justify="center", style="green")

    for (w, s) in valid_words:
        pangram_flag = "Yes" if is_pangram(w, letters_set) else ""
        table.add_row(w, str(s), pangram_flag)

    # Print summary info above the table
    console.print("============================================", style="bold yellow")
    console.print(f"Dictionary       : {dictionary_path}", style="bold white")
    console.print(f"Letters Used     : {', '.join(sorted(letters_set))} (Center = '{center}')", style="bold white")
    console.print(f"Min length       : {min_length}", style="bold white")
    console.print(f"Max length       : {max_length if max_length else 'No limit'}", style="bold white")
    console.print(f"Must contain     : '{must_contain}'" if must_contain else "Must contain     : None", style="bold white")
    console.print("============================================", style="bold yellow")
    console.print(f"Total words      : {stats['total_words']}", style="bold white")
    console.print(f"Number pangrams  : {stats['pangrams_count']}", style="bold white")
    console.print(f"Average length   : {stats['avg_length']:.2f}", style="bold white")
    console.print(f"Sum of all scores: {stats['total_points']}", style="bold white")
    console.print("============================================", style="bold yellow")

    # Print the table of words
    console.print(table)

def export_to_csv(valid_words, letters_set, csv_path: str):
    """
    Writes the results to a CSV file, including pangram info.
    """
    try:
        with open(csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["word", "score", "pangram"])
            for (w, s) in valid_words:
                pangram_flag = "Yes" if is_pangram(w, letters_set) else "No"
                writer.writerow([w, s, pangram_flag])
        console.print(f"\n[green]Results successfully written to {csv_path}![/green]")
    except Exception as e:
        console.print(f"[red]Failed to write CSV file: {e}[/red]")

# ------------------------ INTERACTIVE MODE ------------------------

def interactive_mode():
    """
    Runs an interactive session to collect user inputs and display Spelling Bee results.
    """
    console.print("[bold yellow]Welcome to the Enhanced Spelling Bee Helper![/bold yellow]\n")

    # Prompt for dictionary path
    dictionary_path = console.input("Enter path to dictionary file [default: words.txt]: ")
    if not dictionary_path.strip():
        dictionary_path = "words.txt"  # fallback

    while True:
        # Prompt for center letter
        center = console.input("\nEnter the center letter (required): ").strip().lower()
        if not center or len(center) != 1:
            console.print("[red]Please provide exactly one center letter.[/red]")
            continue

        # Prompt for other letters
        other_letters = console.input("Enter the other 6 letters (required): ").strip().lower()
        if len(other_letters) != 6:
            console.print("[red]Please provide exactly six other letters.[/red]")
            continue

        # Prompt for min_length
        min_length_str = console.input("Minimum word length? [default: 4]: ")
        min_length = 4
        if min_length_str.strip().isdigit():
            min_length = int(min_length_str)

        # Prompt for max_length
        max_length_str = console.input("Maximum word length? [0 = no limit]: ")
        max_length = 0
        if max_length_str.strip().isdigit():
            max_length = int(max_length_str)

        # Prompt for must_contain substring
        must_contain = console.input("Must contain substring (optional): ").strip().lower()

        # -- Perform search --
        valid_words, letters_set = find_spelling_bee_words(
            dictionary_path=dictionary_path,
            center=center,
            other_letters=other_letters,
            min_length=min_length,
            max_length=max_length,
            must_contain=must_contain,
        )

        # -- Print results --
        print_results(valid_words, letters_set, dictionary_path, min_length, max_length, must_contain, center)

        # Optional CSV export
        csv_choice = console.input("Export to CSV? (y/n) [default: n]: ").lower()
        if csv_choice.startswith("y"):
            csv_path = console.input("Enter CSV file name [default: results.csv]: ")
            if not csv_path.strip():
                csv_path = "results.csv"
            export_to_csv(valid_words, letters_set, csv_path)

        # Ask if the user wants to do another query or exit
        again = console.input("\nDo you want to run another query? (y/n) [default: y]: ").lower()
        if again.startswith("n"):
            console.print("\n[bold green]Goodbye![/bold green]")
            break

#-------------------------Interactive Mode II --------------------------#

def interactive_spelling_bee_solver():
    word_list = get_dictionary("words_alpha.txt")
    # Get input from the user
    letters_input = input("Enter all 7 letters (no spaces): ").strip().lower()
    center_letter = input("Enter the center letter: ").strip().lower()

    # Convert letters to a set
    letters = set(letters_input)

    # Find and rank valid words
    results = find_valid_words(letters, center_letter, word_fondlist, bigram_freq, trigram_freq)

    # Display top results
    print("\nTop valid words:")
    for word, score in results[:20]:  # Display top 20
        print(f"{word} (score={score:.2f})")

# ------------------------ MAIN ----------------------------------------#
def main():
    # Just run interactive mode in this example
    # interactive_mode()

    # Just run interactive_spelling_bee_solver()
    interactive_spelling_bee_solver()

if __name__ == "__main__":
    main()

