import tkinter as tk
from tkinter import messagebox
from spelling_bee.cli import run_spelling_bee_query, export_to_csv, SpellingBeeCLI
from spelling_bee.solver import gather_statistics
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("gui_spelling_bee.log"),
        logging.StreamHandler()
    ]
)

class SpellingBeeGUI:
    def __init__(self):
        """
        Initializes the Spelling Bee GUI application.
        """
        try:
            import tkinter as tk
            from tkinter import messagebox
        except ImportError as e:
            logging.error("tkinter is not installed or configured correctly. Please ensure it is installed.")
            print("tkinter is not installed or configured correctly. Please ensure it is installed.")
            raise e

        self.tk = tk
        self.messagebox = messagebox
        self.default_values = {}
        self.setup_gui()

    def setup_gui(self) -> None:
        """
        Sets up the GUI components.
        """
        self.root = self.tk.Tk()
        self.root.title("Spelling Bee Solver")
        self.root.geometry("800x600")

        # Create a canvas and a scrollbar
        canvas = self.tk.Canvas(self.root, bg="#FFD700")
        scrollbar = self.tk.Scrollbar(self.root, orient=self.tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=self.tk.RIGHT, fill=self.tk.Y)
        canvas.pack(side=self.tk.LEFT, fill=self.tk.BOTH, expand=True)

        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas
        frame = self.tk.Frame(canvas, bg="#FFD700")
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Title
        title = self.tk.Label(
            frame,
            text="Spelling Bee Solver",
            font=("Helvetica", 24, "bold"),
            bg="#FFD700",
            fg="black"
        )
        title.grid(row=0, column=0, columnspan=2, pady=10)

        # Input Fields
        self.create_input_fields(frame)

        # Buttons
        button_check = self.tk.Button(
            frame,
            highlightbackground="#FFD700",
            text="Check Words",
            command=self.on_check_words,
            bg="white",
            fg="black"
        )
        button_check.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        button_export = self.tk.Button(
            frame,
            highlightbackground="#FFD700",
            text="Export to File",
            command=self.on_export_csv,
            bg="white",
            fg="black"
        )
        button_export.grid(row=11, column=0, columnspan=2, pady=10)

        # Results and Statistics
        self.create_results_section(frame)

        # Bind events
        self.bind_events()

        # Start the GUI event loop
        self.root.mainloop()

    def create_input_fields(self, frame: tk.Frame) -> None:
        """
        Creates input fields for the GUI.
        """
        fields = [
            ("Dictionary Path:", "words_alpha.txt"),
            ("Center Letter:", ""),
            ("Other Letters:", ""),
            ("Minimum Word Length:", "4"),
            ("Maximum Word Length:", "12"),
            ("Must Contain Substring:", ""),
        ]

        for idx, (label_text, default) in enumerate(fields, start=1):
            self.tk.Label(
                frame,
                text=label_text,
                bg="#FFD700",
                fg="black"
            ).grid(row=idx, column=0, sticky=self.tk.W, padx=10, pady=5)

            entry = self.tk.Entry(
                frame,
                width=50,
                bg="lightgrey",
                fg="darkgrey" if default else "black"
            )
            entry.insert(0, default)
            self.default_values[entry] = default
            entry.grid(row=idx, column=1, padx=10, pady=5)

            if default:
                entry.config(fg="darkgrey")

        # File Export Path
        self.tk.Label(
            frame,
            text="File Export Path:",
            bg="#FFD700",
            fg="black"
        ).grid(row=10, column=0, sticky=self.tk.W, padx=10, pady=5)
        self.entry_csv_path = self.tk.Entry(
            frame,
            width=50,
            bg="lightgrey",
            fg="darkgrey"
        )
        self.entry_csv_path.insert(0, "./output.csv")
        self.default_values[self.entry_csv_path] = "./output.csv"
        self.entry_csv_path.grid(row=10, column=1, padx=10, pady=5)

    def create_results_section(self, frame: tk.Frame) -> None:
        """
        Creates the results display and statistics labels.
        """
        self.tk.Label(
            frame,
            text="Results:",
            bg="#FFD700",
            fg="black"
        ).grid(row=8, column=0, sticky=self.tk.W, padx=10, pady=5)
        self.result_text = self.tk.Text(
            frame,
            height=10,
            width=65,
            bg="lightgrey",
            fg="black"
        )
        self.result_text.grid(row=9, column=1, columnspan=2, pady=5)

        # Statistics
        self.tk.Label(
            frame,
            text="Statistics:",
            bg="#FFD700",
            fg="black",
            font=("Helvetica", 14, "bold")
        ).grid(row=12, column=0, sticky=self.tk.W, padx=10, pady=10)
        self.label_total_words = self.tk.Label(
            frame,
            text="Total Words: 0",
            bg="#FFD700",
            fg="black"
        )
        self.label_total_words.grid(row=13, column=0, sticky=self.tk.W, padx=10, pady=2)

        self.label_pangrams = self.tk.Label(
            frame,
            text="Pangrams: 0",
            bg="#FFD700",
            fg="black"
        )
        self.label_pangrams.grid(row=14, column=0, sticky=self.tk.W, padx=10, pady=2)

        self.label_avg_length = self.tk.Label(
            frame,
            text="Average Length: 0",
            bg="#FFD700",
            fg="black"
        )  # Changed from "0.00" to "0"
        self.label_avg_length.grid(row=15, column=0, sticky=self.tk.W, padx=10, pady=2)

        self.label_sum_scores = self.tk.Label(
            frame,
            text="Sum of Scores: 0",
            bg="#FFD700",
            fg="black"
        )
        self.label_sum_scores.grid(row=16, column=0, sticky=self.tk.W, padx=10, pady=2)

    def bind_events(self) -> None:
        """
        Binds focus and key events to input fields.
        """
        for entry, default in self.default_values.items():
            entry.bind("<FocusIn>", self.on_focus_in)
            entry.bind("<FocusOut>", self.on_focus_out)
            entry.bind("<KeyRelease>", self.on_key_release)

    def on_check_words(self) -> None:
        """
        Handles the 'Check Words' button click event.
        """
        center = self.entry_center.get().strip().lower()
        other_letters = self.entry_other_letters.get().strip().lower()
        min_length = int(self.entry_min_length.get().strip() or 4)
        max_length = int(self.entry_max_length.get().strip() or 0)
        must_contain = self.entry_must_contain.get().strip().lower()
        dictionary_path = self.entry_dictionary_path.get().strip() or "words.txt"

        if len(center) != 1 or len(other_letters) != 6:
            self.messagebox.showerror("Input Error", "Please provide exactly one center letter and six other letters.")
            logging.warning("Invalid input: Center letter length or other letters length incorrect.")
            return

        try:
            valid_words, letters_set = run_spelling_bee_query(
                dictionary_path=dictionary_path,
                center=center,
                other_letters=other_letters,
                min_length=min_length,
                max_length=max_length,
                must_contain=must_contain,
            )

            self.result_text.delete(1.0, self.tk.END)
            for word, score in valid_words:
                self.result_text.insert(self.tk.END, f"{word}\n")

            stats = gather_statistics(valid_words, letters_set)  # Pass letters_set
            self.label_total_words.config(text=f"Total Words: {stats['total_words']:,}")
            self.label_pangrams.config(text=f"Pangrams: {stats['pangrams_count']:,}")
            self.label_avg_length.config(text=f"Average Length: {int(stats['avg_length'])}")
            self.label_sum_scores.config(text=f"Sum of Scores: {stats['total_points']:.2f}")
            logging.info(f"Checked words with center '{center}' and letters '{other_letters}'.")
        except Exception as e:
            logging.error(f"Error checking words: {e}")

    def on_export_csv(self) -> None:
        """
        Handles the 'Export to File' button click event.
        """
        csv_path = self.entry_csv_path.get().strip() or "results.csv"
        center = self.entry_center.get().strip().lower()
        other_letters = self.entry_other_letters.get().strip().lower()
        min_length = int(self.entry_min_length.get().strip() or 4)
        max_length = int(self.entry_max_length.get().strip() or 0)
        must_contain = self.entry_must_contain.get().strip().lower()
        dictionary_path = self.entry_dictionary_path.get().strip() or "words.txt"

        try:
            valid_words, letters_set = run_spelling_bee_query(
                dictionary_path=dictionary_path,
                center=center,
                other_letters=other_letters,
                min_length=min_length,
                max_length=max_length,
                must_contain=must_contain,
            )

            export_to_csv(valid_words, letters_set, csv_path)
            self.messagebox.showinfo("Export Success", f"Results successfully written to {csv_path}!")
            logging.info(f"Exported results to {csv_path}.")
        except Exception as e:
            logging.error(f"Failed to export CSV: {e}")
            self.messagebox.showerror("Export Failed", f"Failed to write CSV file: {e}")

        stats = gather_statistics(valid_words, letters_set)  # Pass letters_set
        self.label_total_words.config(text=f"Total Words: {stats['total_words']:,}")
        self.label_pangrams.config(text=f"Pangrams: {stats['pangrams_count']:,}")
        self.label_avg_length.config(text=f"Average Length: {int(stats['avg_length'])}")
        self.label_sum_scores.config(text=f"Sum of Scores: {stats['total_points']:.2f}")

    def on_focus_in(self, event: tk.Event) -> None:
        """
        Handles focus in event for entry widgets.
        """
        widget = event.widget
        if widget.get() == self.default_values.get(widget, ""):
            widget.delete(0, self.tk.END)
            widget.config(fg="black")

    def on_focus_out(self, event: tk.Event) -> None:
        """
        Handles focus out event for entry widgets.
        """
        widget = event.widget
        if not widget.get():
            default_value = self.default_values.get(widget, "")
            widget.insert(0, default_value)
            widget.config(fg="darkgrey")

    def on_key_release(self, event: tk.Event) -> None:
        """
        Handles key release event for entry widgets.
        """
        widget = event.widget
        if widget.get() != self.default_values.get(widget, ""):
            widget.config(fg="black")

if __name__ == "__main__":
    SpellingBeeGUI()

# Ensure that SpellingBeeGUI is available for import
__all__ = ['SpellingBeeGUI']