import csv
import nltk
import re
from collections import Counter
import logging
import hashlib  # Added import for hashlib
from typing import Tuple, List, Set

# ------------------------ GLOBAL CACHE ------------------------
_DICTIONARY_CACHE = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("solver.log"),
        logging.StreamHandler()
    ]
)

class SpellingBeeSolver:
    def __init__(self, dictionary_path: str):
        """
        Initializes the SpellingBeeSolver with a dictionary and computes bigram and trigram frequencies.
        """
        self.dictionary = self.get_dictionary(dictionary_path)
        self.bigram_freq, self.trigram_freq = self.compute_ngrams()

    def get_dictionary(self, dictionary_path: str) -> List[str]:
        """
        Loads and caches the dictionary to avoid repeated disk reads.
        """
        global _DICTIONARY_CACHE
        if (_DICTIONARY_CACHE is not None):
            return _DICTIONARY_CACHE

        try:
            with open(dictionary_path, 'r', encoding='utf-8') as file:
                words = [word.strip().lower() for word in file.readlines()]
            _DICTIONARY_CACHE = words
            return words
        except FileNotFoundError:
            logging.error(f"Dictionary file not found: {dictionary_path}")
            return []

    def compute_ngrams(self) -> Tuple[Counter, Counter]:
        """
        Computes bigram and trigram frequencies from the dictionary.
        """
        # Ensure nltk resources are downloaded
        nltk.download('gutenberg', quiet=True)
        from nltk.corpus import gutenberg

        bigram_freq = Counter()
        trigram_freq = Counter()
        for word in gutenberg.words():
            if isinstance(word, bytes):
                word = word.decode('utf-8').lower()
            else:
                word = word.lower()
            for i in range(len(word) - 1):
                bigram = word[i:i+2]
                bigram_freq[bigram] += 1
            for i in range(len(word) - 2):
                trigram = word[i:i+3]
                trigram_freq[trigram] += 1
        return bigram_freq, trigram_freq

    def is_valid_word(self, word: str, center: str, letters_set: set) -> bool:
        """
        Determines if a word is valid based on Spelling Bee rules.
        """
        if len(word) < 4:
            return False
        if center not in word:
            return False
        if not set(word).issubset(letters_set):
            return False
        return True

    def is_pangram(self, word: str, letters_set: set) -> bool:
        """
        Checks if a word is a pangram (uses all 7 letters).
        """
        return letters_set.issubset(set(word))

    def compute_score(self, word: str, letters_set: set) -> float:
        """
        Computes a normalized score for a word based on length, pangram status, and n-gram scores.
        """
        score = len(word)
        if self.is_pangram(word, letters_set):
            score += 7
        # Include bigram and trigram scores
        score += self.combined_score(word)
        return score

    def gather_statistics(self, valid_words: List[Tuple[str, float]], letters_set: set) -> dict:
        """
        Gathers statistics from the list of valid words.
        """
        total_words = len(valid_words)
        pangrams = sum(1 for word, _ in valid_words if self.is_pangram(word, letters_set))
        avg_length = sum(len(word) for word, _ in valid_words) / total_words if total_words else 0
        total_points = sum(score for _, score in valid_words)
        return {
            'total_words': total_words,
            'pangrams_count': pangrams,
            'avg_length': avg_length,
            'total_points': total_points
        }

    def filter_candidates(
        self,
        center_letter: str,
        other_letters: str,
        min_length: int = 4,
        max_length: int = 0,
        must_contain: str = "",
    ) -> list[str]:
        """
        Filters dictionary words based on Spelling Bee constraints.
        """
        letters_set = set(center_letter + other_letters)
        candidates = [
            word for word in self.dictionary
            if self.is_valid_word(word, center_letter, letters_set)
            and len(word) >= min_length
            and (len(word) <= max_length if max_length > 0 else True)
            and (must_contain in word if must_contain else True)
        ]
        return candidates

    def find_spelling_bee_words(
        self,
        center: str,
        other_letters: str,
        min_length: int = 4,
        max_length: int = 0,
        must_contain: str = "",
    ) -> tuple[list[tuple[str, float]], set]:
        """
        Finds and scores valid Spelling Bee words.
        """
        letters_set = set(center + other_letters)
        filtered = self.filter_candidates(center, other_letters, min_length, max_length, must_contain)
        valid_words = [
            (word, self.compute_score(word, letters_set)) for word in filtered
        ]
        valid_words.sort(key=lambda ws: (-ws[1], -len(ws[0]), ws[0]))
        return valid_words, letters_set

    def find_valid_words(self, letters: set, center_letter: str) -> list[tuple[str, float]]:
        """
        Finds and ranks valid words based on combined bigram and trigram scores.
        """
        filtered = [
            word for word in self.dictionary
            if self.is_valid_word(word, center_letter, letters)
        ]
        return sorted(
            [
                (word, self.combined_score(word))
                for word in filtered
            ],
            key=lambda x: x[1],
            reverse=True
        )

    def bigram_score(self, word: str) -> float:
        """
        Calculates bigram score for a word.
        """
        return sum(self.bigram_freq.get(word[i:i+2], 0) for i in range(len(word) - 1))

    def trigram_score(self, word: str) -> float:
        """
        Calculates trigram score for a word.
        """
        return sum(self.trigram_freq.get(word[i:i+3], 0) for i in range(len(word) - 2))

    def combined_score(self, word: str, weight: float = 0.5) -> float:
        """
        Combines bigram and trigram scores with a weighted average.
        """
        score_b = self.bigram_score(word)
        score_t = self.trigram_score(word)
        return score_b * weight + score_t * (1 - weight)

    def md5_hexdigest(self, filepath: str) -> str:
        """
        Computes the MD5 hexdigest of a file.
        """
        md5_digest = hashlib.md5()
        with open(filepath, 'rb') as infile:
            for block in iter(lambda: infile.read(4096), b""):
                md5_digest.update(block)
        return md5_digest.hexdigest()

# Ensure gather_statistics is available for import
def gather_statistics(valid_words: List[Tuple[str, float]], letters_set: set) -> dict:
    solver = SpellingBeeSolver("")
    return solver.gather_statistics(valid_words, letters_set)

# Ensure compute_score is available for import
def compute_score(word: str, letters_set: set) -> float:
    solver = SpellingBeeSolver("")
    return solver.compute_score(word, letters_set)