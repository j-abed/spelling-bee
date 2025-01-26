import csv
import re
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
corpus = re.sub(r'[^a-z\s]', '', corpus)

# Bigram and trigram frequencies
bigram_freq = Counter(corpus[i:i+2] for i in range(len(corpus) - 1))
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
        return _DICTIONARY_CACHE
    
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
    return len(word) >= 4 and center in word and all(char in letters_set for char in word)

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
    Combine bigram and trigram scores with a weighted average and normalize by word length.
    """
    score_b = bigram_score(word, bigram_freq)
    score_t = trigram_score(word, trigram_freq)
    combined = score_b * weight + score_t * (1 - weight)
    return combined / len(word)  # Normalize by word length

def normalize_scores(valid_words):
    """
    Normalize scores to a scale of 0 to 100.
    """
    if not valid_words:
        return valid_words

    max_score = max(score for _, score in valid_words)
    if max_score == 0:
        return valid_words

    return [(word, (score / max_score) * 100) for word, score in valid_words]

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

def find_valid_words(letters, center_letter, dictionary, bigram_freq, trigram_freq):
    """
    Find valid Spelling Bee words and rank them by combined score.
    """
    candidates = [
        word for word in dictionary
        if is_valid_word(word, center_letter, letters)
    ]
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
    center = center.lower()
    other_letters = other_letters.lower()
    letters_set = set(center + other_letters)
    word_list = get_dictionary(dictionary_path)

    valid_words = [
        (word, combined_score(word, bigram_freq, trigram_freq))
        for word in word_list
        if is_valid_word(word, center, letters_set)
        and len(word) >= min_length
        and (max_length == 0 or len(word) <= max_length)
        and (not must_contain or must_contain.lower() in word)
    ]

    valid_words.sort(key=lambda ws: (-ws[1], -len(ws[0]), ws[0]))
    valid_words = normalize_scores(valid_words)

    return valid_words, letters_set

def print_results(valid_words, letters_set, dictionary_path, min_length, max_length, must_contain, center):
    """
    Prints results in a rich-formatted table and summary statistics.
    """
    stats = gather_statistics(valid_words, letters_set)

    table = Table(title="Spelling Bee Results")
    table.add_column("Word", justify="left", style="cyan", no_wrap=True)
    table.add_column("Score", justify="right", style="magenta")
    table.add_column("Pangram?", justify="center", style="green")

    for (w, s) in valid_words:
        pangram_flag = "Yes" if is_pangram(w, letters_set) else ""
        table.add_row(w, f"{s:.2f}", pangram_flag)

    console.print("============================================", style="bold yellow")
    console.print(f"Dictionary       : {dictionary_path}", style="bold white")
    console.print(f"Letters Used     : {', '.join(sorted(letters_set))} (Center = '{center}')", style="bold white")
    console.print(f"Min length       : {min_length}", style="bold white")
    console.print(f"Max length       : {max_length if max_length else 'No limit'}", style="bold white")
    console.print(f"Must contain     : '{must_contain}'" if must_contain else "Must contain     : None", style="bold white")
    console.print("============================================", style="bold yellow")
    console.print(f"Total words      : {stats['total_words']}", style="bold white")
    console.print(f"Number pangrams  : {stats['pangrams_count']}", style="bold white")
    console.print(f"Average length   : {stats['avg_length']:.0f}", style="bold white")
    console.print("============================================", style="bold yellow")

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
                writer.writerow([w, f"{s:.2f}", pangram_flag])
        console.print(f"\n[green]Results successfully written to {csv_path}![/green]")
    except Exception as e:
        console.print(f"[red]Failed to write CSV file: {e}[/red]")

# ------------------------ INTERACTIVE MODE ------------------------

def interactive_mode():
    """
    Runs an interactive session to collect user inputs and display Spelling Bee results.
    """
    console.print("[bold yellow]Welcome to the Enhanced Spelling Bee Helper![/bold yellow]\n")

    # Default inputs
    default_dictionary_path = "words_alpha.txt"
    default_center = "f"
    default_other_letters = "laping"
    default_min_length = 4
    default_max_length = 12
    default_must_contain = ""

    dictionary_path = console.input(f"Enter path to dictionary file [default: {default_dictionary_path}]: ") or default_dictionary_path
    center = console.input(f"\nEnter the center letter (required) [default: {default_center}]: ").strip().lower() or default_center
    other_letters = console.input(f"Enter the other 6 letters (required) [default: {default_other_letters}]: ").strip().lower() or default_other_letters
    min_length = int(console.input(f"Minimum word length? [default: {default_min_length}]: ").strip() or default_min_length)
    max_length = int(console.input(f"Maximum word length? [0 = no limit] [default: {default_max_length}]: ").strip() or default_max_length)
    must_contain = console.input(f"Must contain substring (optional) [default: {default_must_contain}]: ").strip().lower() or default_must_contain

    while True:
        valid_words, letters_set = find_spelling_bee_words(
            dictionary_path=dictionary_path,
            center=center,
            other_letters=other_letters,
            min_length=min_length,
            max_length=max_length,
            must_contain=must_contain,
        )

        print_results(valid_words, letters_set, dictionary_path, min_length, max_length, must_contain, center)

        if console.input("Export to CSV? (y/n) [default: n]: ").strip().lower().startswith("y"):
            csv_path = console.input("Enter CSV file name [default: results.csv]: ").strip() or "results.csv"
            export_to_csv(valid_words, letters_set, csv_path)

        if console.input("\nDo you want to run another query? (y/n) [default: y]: ").strip().lower().startswith("n"):
            console.print("\n[bold green]Goodbye![/bold green]")
            break

#-------------------------Interactive Mode II --------------------------#

def interactive_spelling_bee_solver():
    word_list = get_dictionary("words_alpha.txt")
    letters_input = console.input("Enter all 7 letters (no spaces): ").strip().lower()
    center_letter = console.input("Enter the center letter: ").strip().lower()

    letters = set(letters_input)

    results = find_valid_words(letters, center_letter, word_list, bigram_freq, trigram_freq)

    console.print("\n[bold yellow]Top valid words:[/bold yellow]")
    for word, score in results[:20]:  # Display top 20
        console.print(f"{word} (score={score:.2f})", style="bold cyan")

# ------------------------ MAIN ----------------------------------------#
def main():
    interactive_mode()

if __name__ == "__main__":
    main()

