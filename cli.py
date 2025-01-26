from rich.console import Console
from enhanced_spelling_bee import find_spelling_bee_words, print_results, export_to_csv

console = Console()

def interactive_mode():
    """
    Runs an interactive session to collect user inputs and display Spelling Bee results.
    """
    console.print("[bold yellow]Welcome to the Enhanced Spelling Bee Helper![/bold yellow]\n")

    # Default inputs
    default_dictionary_path = "words_alpha.txt"
    default_center = "a"
    default_other_letters = "bcdefg"
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
