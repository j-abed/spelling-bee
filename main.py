from spelling_bee.cli import SpellingBeeCLI
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("main.log"),
        logging.StreamHandler()
    ]
)

def main() -> None:
    """
    Entry point for the Spelling Bee application.
    """
    cli = SpellingBeeCLI()
    # Run interactive mode
    cli.interactive_mode()
    # Alternatively, run solver mode
    # cli.interactive_spelling_bee_solver()

if __name__ == "__main__":
    logging.info("Spelling Bee application started.")
    main()
    logging.info("Spelling Bee application terminated.")