from cli import interactive_mode
import subprocess

def main():
    choice = input("Choose application mode: (1) Console (2) GUI [default: 1]: ").strip() or "1"
    if choice == "2":
        subprocess.run(["python", "gui_spelling_bee.py"])
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
