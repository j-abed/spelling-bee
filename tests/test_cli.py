import unittest
from unittest.mock import patch, mock_open
from spelling_bee.cli import SpellingBeeCLI  # Removed is_pangram import

class TestSpellingBeeCLI(unittest.TestCase):
    """Unit tests for the SpellingBeeCLI class."""

    @patch('spelling_bee.solver.nltk.download')  # Mock nltk.download
    @patch('builtins.open', new_callable=mock_open, read_data="apple\nbanana\nexample\nflying\npangram\n")
    def setUp(self, mock_file, mock_nltk_download):
        """Set up a SpellingBeeCLI instance with mocked dictionary data."""
        mock_nltk_download.return_value = True
        self.cli = SpellingBeeCLI()

    @patch('builtins.input', side_effect=['a', 'elpx', '', '', '', ''])
    def test_get_input_parameters(self, mock_input):
        """Test retrieving input parameters with default values."""
        center, other_letters, min_len, max_len, must_contain = self.cli.get_input_parameters()
        self.assertEqual(center, 'a')
        self.assertEqual(other_letters, 'elpx')
        self.assertEqual(min_len, 4)
        self.assertEqual(max_len, 0)
        self.assertEqual(must_contain, '')

    @patch('builtins.input', side_effect=['n'])
    def test_display_and_optionally_export_results_no_export(self, mock_input):
        """Test displaying results without exporting to CSV."""
        valid_words = [("apple", 1.0)]
        letters_set = set("aelpx")
        dictionary_path = "test_dict.txt"
        min_length = 4
        max_length = 0
        must_contain = ""
        center = "a"

        with patch.object(self.cli, 'print_results') as mock_print:
            self.cli.display_and_optionally_export_results(
                valid_words,
                letters_set,
                dictionary_path,
                min_length,
                max_length,
                must_contain,
                center
            )
            mock_print.assert_called_with(
                valid_words,
                letters_set,
                dictionary_path,
                min_length,
                max_length,
                must_contain,
                center
            )

    @patch('builtins.input', side_effect=['y', 'output.csv'])
    @patch('spelling_bee.cli.SpellingBeeCLI.export_to_csv')
    def test_display_and_optionally_export_results_with_export(self, mock_export, mock_input):
        """Test displaying results and exporting to CSV when user opts to export."""
        valid_words = [("apple", 1.0)]
        letters_set = set("aelpx")
        dictionary_path = "test_dict.txt"
        min_length = 4
        max_length = 0
        must_contain = ""
        center = "a"

        with patch.object(self.cli, 'print_results') as mock_print:
            self.cli.display_and_optionally_export_results(
                valid_words,
                letters_set,
                dictionary_path,
                min_length,
                max_length,
                must_contain,
                center
            )
            mock_print.assert_called_with(
                valid_words,
                letters_set,
                dictionary_path,
                min_length,
                max_length,
                must_contain,
                center
            )
            mock_export.assert_called_with(valid_words, letters_set, 'output.csv')

    @patch('spelling_bee.cli.SpellingBeeSolver.find_spelling_bee_words', return_value=([], set()))
    def test_run_spelling_bee_query(self, mock_query):
        """Test running a Spelling Bee query and returning results."""
        result = self.cli.run_spelling_bee_query("test_dict.txt", "a", "elpx", 4, 0, "")
        self.assertEqual(result, ([], set()))
        mock_query.assert_called_with("a", "elpx", 4, 0, "")

if __name__ == '__main__':
    unittest.main()
    unittest.main()