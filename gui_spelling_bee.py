try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError as e:
    print("tkinter is not installed or configured correctly. Please ensure it is installed.")
    raise e

from enhanced_spelling_bee import get_dictionary, find_spelling_bee_words, print_results, export_to_csv

def on_check_words():
    center = entry_center.get().strip().lower()
    other_letters = entry_other_letters.get().strip().lower()
    min_length = int(entry_min_length.get().strip() or 4)
    max_length = int(entry_max_length.get().strip() or 0)
    must_contain = entry_must_contain.get().strip().lower()
    dictionary_path = entry_dictionary_path.get().strip() or "words.txt"

    if len(center) != 1 or len(other_letters) != 6:
        messagebox.showerror("Input Error", "Please provide exactly one center letter and six other letters.")
        return

    valid_words, letters_set = find_spelling_bee_words(
        dictionary_path=dictionary_path,
        center=center,
        other_letters=other_letters,
        min_length=min_length,
        max_length=max_length,
        must_contain=must_contain,
    )

    result_text.delete(1.0, tk.END)
    for word, score in valid_words:
        result_text.insert(tk.END, f"{word} (Score: {score})\n")

def on_export_csv():
    csv_path = entry_csv_path.get().strip() or "results.csv"
    center = entry_center.get().strip().lower()
    other_letters = entry_other_letters.get().strip().lower()
    min_length = int(entry_min_length.get().strip() or 4)
    max_length = int(entry_max_length.get().strip() or 0)
    must_contain = entry_must_contain.get().strip().lower()
    dictionary_path = entry_dictionary_path.get().strip() or "words.txt"

    valid_words, letters_set = find_spelling_bee_words(
        dictionary_path=dictionary_path,
        center=center,
        other_letters=other_letters,
        min_length=min_length,
        max_length=max_length,
        must_contain=must_contain,
    )

    export_to_csv(valid_words, letters_set, csv_path)
    messagebox.showinfo("Export Success", f"Results successfully written to {csv_path}!")

# Create the main application window
root = tk.Tk()
root.title("Enhanced Spelling Bee Checker")
root.geometry("600x600")  # Set the window size

# Create and place the widgets
frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

tk.Label(frame, text="Dictionary Path:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
entry_dictionary_path = tk.Entry(frame, width=50)
entry_dictionary_path.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame, text="Center Letter:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
entry_center = tk.Entry(frame, width=50)
entry_center.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame, text="Other Letters:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
entry_other_letters = tk.Entry(frame, width=50)
entry_other_letters.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frame, text="Minimum Word Length:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
entry_min_length = tk.Entry(frame, width=50)
entry_min_length.grid(row=3, column=1, padx=10, pady=5)

tk.Label(frame, text="Maximum Word Length:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
entry_max_length = tk.Entry(frame, width=50)
entry_max_length.grid(row=4, column=1, padx=10, pady=5)

tk.Label(frame, text="Must Contain Substring:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
entry_must_contain = tk.Entry(frame, width=50)
entry_must_contain.grid(row=5, column=1, padx=10, pady=5)

button_check = tk.Button(frame, text="Check Words", command=on_check_words)
button_check.grid(row=6, column=0, columnspan=2, pady=10)

tk.Label(frame, text="Results:").grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
result_text = tk.Text(frame, height=10, width=50)
result_text.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

tk.Label(frame, text="CSV Export Path:").grid(row=9, column=0, sticky=tk.W, padx=10, pady=5)
entry_csv_path = tk.Entry(frame, width=50)
entry_csv_path.grid(row=9, column=1, padx=10, pady=5)

button_export = tk.Button(frame, text="Export to CSV", command=on_export_csv)
button_export.grid(row=10, column=0, columnspan=2, pady=10)

# Start the GUI event loop
root.mainloop()
