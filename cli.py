from rich.console import Console
from enhanced_spelling_bee import find_spelling_bee_words, print_results, export_to_csv

console = Console()

def get_user_input(prompt, default):
    return console.input(f"{prompt} [default: {default}]: ").strip() or default

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

    dictionary_path = get_user_input("Enter path to dictionary file", default_dictionary_path)
    center = get_user_input("Enter the center letter (required)", default_center).lower()
    other_letters = get_user_input("Enter the other 6 letters (required)", default_other_letters).lower()
    min_length = int(get_user_input("Minimum word length?", default_min_length))
    max_length = int(get_user_input("Maximum word length? [0 = no limit]", default_max_length))
    must_contain = get_user_input("Must contain substring (optional)", default_must_contain).lower()

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

        if get_user_input("Export to CSV? (y/n)", "n").lower().startswith("y"):
            csv_path = get_user_input("Enter CSV file name", "results.csv")
            export_to_csv(valid_words, letters_set, csv_path)

        if get_user_input("Do you want to run another query? (y/n)", "y").lower().startswith("n"):
            console.print("\n[bold green]Goodbye![/bold green]")
            break
