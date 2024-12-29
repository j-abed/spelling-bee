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

def on_focus_in(event):
    if event.widget.get() in default_values.values():
        event.widget.delete(0, tk.END)
        event.widget.config(fg="black")

def on_focus_out(event):
    if not event.widget.get():
        default_value = default_values.get(event.widget)
        event.widget.insert(0, default_value)
        event.widget.config(fg="darkgrey")

def on_key_release(event):
    if event.widget.get() not in default_values.values():
        event.widget.config(fg="black")

# Create the main application window
root = tk.Tk()
root.title("Spelling Bee Solver")
root.geometry("800x600")

# Create a canvas and a scrollbar
canvas = tk.Canvas(root, bg="#FFD700")
scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Configure the canvas
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Create a frame inside the canvas
frame = tk.Frame(canvas, bg="#FFD700")
canvas.create_window((0, 0), window=frame, anchor="nw")

title = tk.Label(frame, text="Spelling Bee Solver", font=("Helvetica", 24, "bold"), bg="#FFD700", fg="black")
title.grid(row=0, column=0, columnspan=2, pady=10)

default_values = {}

tk.Label(frame, text="Dictionary Path:", bg="#FFD700", fg="black").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
entry_dictionary_path = tk.Entry(frame, width=50, bg="lightgrey", fg="darkgrey")
default_values[entry_dictionary_path] = "words_alpha.txt"
entry_dictionary_path.insert(0, "words_alpha.txt")
entry_dictionary_path.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame, text="Center Letter:", bg="#FFD700", fg="black").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
entry_center = tk.Entry(frame, width=50, bg="lightgrey", fg="black")
entry_center.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frame, text="Other Letters:", bg="#FFD700", fg="black").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
entry_other_letters = tk.Entry(frame, width=50, bg="lightgrey", fg="black")
entry_other_letters.grid(row=3, column=1, padx=10, pady=5)

tk.Label(frame, text="Minimum Word Length:", bg="#FFD700", fg="black").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
entry_min_length = tk.Entry(frame, width=50, bg="lightgrey", fg="darkgrey")
default_values[entry_min_length] = "4"
entry_min_length.insert(0, "4")
entry_min_length.grid(row=4, column=1, padx=10, pady=5)

tk.Label(frame, text="Maximum Word Length:", bg="#FFD700", fg="black").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
entry_max_length = tk.Entry(frame, width=50, bg="lightgrey", fg="darkgrey")
default_values[entry_max_length] = "12"
entry_max_length.insert(0, "12")
entry_max_length.grid(row=5, column=1, padx=10, pady=5)

tk.Label(frame, text="Must Contain Substring:", bg="#FFD700", fg="black").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
entry_must_contain = tk.Entry(frame, width=50, bg="lightgrey", fg="black")
entry_must_contain.grid(row=6, column=1, padx=10, pady=5)

button_check = tk.Button(frame,highlightbackground="#FFD700", text="Check Words", command=on_check_words, bg="white", fg="black")
button_check.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

tk.Label(frame, text="Results:", bg="#FFD700", fg="black").grid(row=8, column=0, sticky=tk.W, padx=10, pady=5)
result_text = tk.Text(frame, height=10, width=65, bg="lightgrey", fg="black")
result_text.grid(row=9, column=1, columnspan=2, pady=5)

tk.Label(frame, text="File Export Path:", bg="#FFD700", fg="black").grid(row=10, column=0, sticky=tk.W, padx=10, pady=5)
entry_csv_path = tk.Entry(frame, width=50, bg="lightgrey", fg="darkgrey")
default_values[entry_csv_path] = "./"
entry_csv_path.insert(0, "./output.csv")
entry_csv_path.grid(row=10, column=1, padx=10, pady=5)

button_export = tk.Button(frame, highlightbackground="#FFD700", text="Export to File", command=on_export_csv, bg="white", fg="black")
button_export.grid(row=11, column=0, columnspan=2, pady=10)

# Bind focus in, focus out, and key release events
for entry in default_values.keys():
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    entry.bind("<KeyRelease>", on_key_release)

# Start the GUI event loop
root.mainloop()
