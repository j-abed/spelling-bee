from rich.console import Console
from rich.table import Table
import csv
from typing import List, Tuple, Set
from .solver import (
    SpellingBeeSolver,
    gather_statistics,  # Ensure this is correctly imported
    compute_score,      # Ensure this is correctly imported
)

def run_spelling_bee_query(
    dictionary_path: str,
    center: str,
    other_letters: str,
    min_length: int = 4,
    max_length: int = 10,
    must_contain: str = ""
) -> Tuple[List[Tuple[str, float]], Set[str]]:
    """
    Runs the Spelling Bee query and returns valid words and the letters set.
    """
    solver = SpellingBeeSolver(dictionary_path)
    return solver.find_spelling_bee_words(center, other_letters, min_length, max_length, must_contain)

def export_to_csv(valid_words: List[Tuple[str, float]], letters_set: Set[str], csv_path: str) -> None:
    """
    Exports the valid words and their scores to a CSV file.
    """
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Word', 'Score'])
        for word, score in valid_words:
            writer.writerow([word, score])

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("cli.log"),
        logging.StreamHandler()
    ]
)

class SpellingBeeCLI:
    def __init__(self):
        """
        Initializes the CLI with a console for rich output.
        """
        self.console = Console()
        self.solver = SpellingBeeSolver("words_alpha.txt")

    def print_results(
        self,
        valid_words: list[tuple[str, float]],
        letters_set: set,
        dictionary_path: str,
        min_length: int,
        max_length: int,
        must_contain: str,
        center: str
    ) -> None:
        """
        Prints results in a rich-formatted table and summary statistics.
        """
        stats = self.solver.gather_statistics(valid_words, letters_set)  # Pass letters_set

        table = Table(title="Spelling Bee Results")
        table.add_column("Word", justify="left", style="cyan", no_wrap=True)
        table.add_column("Score", justify="right", style="magenta")
        table.add_column("Pangram?", justify="center", style="green")

        for word, score in valid_words:
            pangram_flag = "Yes" if self.solver.is_pangram(word, letters_set) else ""
            table.add_row(word, f"{score:.2f}", pangram_flag)

        self.console.print("============================================", style="bold yellow")
        self.console.print(f"Dictionary       : {dictionary_path}", style="bold white")
        self.console.print(f"Letters Used     : {', '.join(sorted(letters_set))} (Center = '{center}')", style="bold white")
        self.console.print(f"Min length       : {min_length}", style="bold white")
        self.console.print(f"Max length       : {max_length if max_length else 'No limit'}", style="bold white")
        self.console.print(f"Must contain     : '{must_contain}'" if must_contain else "Must contain     : None", style="bold white")
        self.console.print("============================================", style="bold yellow")
        self.console.print(f"Total words      : {stats['total_words']:,}", style="bold white")
        self.console.print(f"Number pangrams  : {stats['pangrams_count']:,}", style="bold white")
        self.console.print(f"Average length   : {int(stats['avg_length'])}", style="bold white")
        self.console.print(f"Sum of all scores: {stats['total_points']:.2f}", style="bold white")
        self.console.print("============================================", style="bold yellow")
        self.console.print(table)

    def export_to_csv(self, valid_words: list[tuple[str, float]], letters_set: set, csv_path: str) -> None:
        """
        Writes the results to a CSV file, including pangram info and statistical scores.
        """
        try:
            with open(csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["word", "score", "pangram"])
                for word, score in valid_words:
                    pangram_flag = "Yes" if self.solver.is_pangram(word, letters_set) else "No"
                    writer.writerow([word, f"{score:.2f}", pangram_flag])

                stats = self.solver.gather_statistics(valid_words)
                writer.writerow([])
                writer.writerow(["Total Words", f"{stats['total_words']:,}"])
                writer.writerow(["Number of Pangrams", f"{stats['pangrams_count']:,}"])
                writer.writerow(["Average Word Length", f"{int(stats['avg_length'])}"])
                writer.writerow(["Sum of All Scores", f"{stats['total_points']:.2f}"])

            logging.info(f"Results successfully written to {csv_path}!")
            self.console.print(f"\n[green]Results successfully written to {csv_path}![/green]")
        except Exception as e:
            logging.error(f"Failed to write CSV file: {e}")
            self.console.print(f"[red]Failed to write CSV file: {e}[/red]")

    def display_and_optionally_export_results(
        self,
        valid_words: list[tuple[str, float]],
        letters_set: set,
        dictionary_path: str,
        min_length: int,
        max_length: int,
        must_contain: str,
        center: str
    ) -> None:
        """
        Displays results and optionally exports them to a CSV file based on user input.
        """
        self.print_results(valid_words, letters_set, dictionary_path, min_length, max_length, must_contain, center)
        csv_choice = self.console.input("Export to CSV? (y/n) [default: n]: ").lower()
        if csv_choice.startswith("y"):
            csv_path = self.console.input("Enter CSV file name [default: results.csv]: ").strip()
            csv_path = csv_path if csv_path else "results.csv"
            self.export_to_csv(valid_words, letters_set, csv_path)

    def get_input_parameters(self) -> tuple[str, str, int, int, str]:
        """
        Collects Spelling Bee parameters from user input.
        """
        center = self.console.input("\nEnter the center letter (required): ").strip().lower()
        other_letters = self.console.input("Enter the other 6 letters (required): ").strip().lower()
        min_length_str = self.console.input("Minimum word length? [default: 4]: ")
        max_length_str = self.console.input("Maximum word length? [default: 0 = no limit]: ")
        must_contain = self.console.input("Must contain substring (optional): ").strip().lower()

        min_len = int(min_length_str) if min_length_str.isdigit() else 4
        max_len = int(max_length_str) if max_length_str.isdigit() else 0

        return center, other_letters, min_len, max_len, must_contain

    def run_spelling_bee_query(
        self,
        dictionary_path: str,
        center: str,
        other_letters: str,
        min_length: int,
        max_length: int,
        must_contain: str
    ) -> tuple[list[tuple[str, float]], set]:
        """
        Executes the Spelling Bee query using the solver.
        """
        return self.solver.find_spelling_bee_words(center, other_letters, min_length, max_length, must_contain)

    def interactive_mode(self) -> None:
        """
        Runs an interactive CLI session for Spelling Bee queries.
        """
        self.console.print("[bold yellow]Welcome to the Enhanced Spelling Bee Helper![/bold yellow]\n")
        
        dictionary_path = self.console.input("Enter path to dictionary file [default: words.txt]: ").strip()
        dictionary_path = dictionary_path if dictionary_path else "words.txt"

        while True:
            center, other_letters, min_len, max_len, must_contain = self.get_input_parameters()
            valid_words, letters_set = self.run_spelling_bee_query(
                dictionary_path, center, other_letters, min_len, max_len, must_contain
            )
            self.display_and_optionally_export_results(
                valid_words, letters_set, dictionary_path, min_len, max_len, must_contain, center
            )

            again = self.console.input("\nDo you want to run another query? (y/n) [default: y]: ").lower()
            if again.startswith("n"):
                self.console.print("\n[bold green]Goodbye![/bold green]")
                break

    def interactive_spelling_bee_solver(self) -> None:
        """
        Runs the spelling bee solver in interactive mode.
        """
        letters_input = input("Enter all 7 letters (no spaces): ").strip().lower()
        center_letter = input("Enter the center letter: ").strip().lower()
        letters = set(letters_input)

        results = self.solver.find_valid_words(letters, center_letter)
        self.display_and_optionally_export_results(
            results[:20], letters, "words_alpha.txt", 4, 0, "", center_letter
        )

def main() -> None:
    """
    Entry point for the CLI application.
    """
    cli = SpellingBeeCLI()
    # Choose which mode to run
    mode = input("Select mode: (1) Interactive Mode, (2) Solver Mode [default: 1]: ").strip()
    if mode == "2":
        cli.interactive_spelling_bee_solver()
    else:
        cli.interactive_mode()

if __name__ == "__main__":
    main()