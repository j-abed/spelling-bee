import unittest
from unittest.mock import patch, MagicMock, mock_open
from spelling_bee.gui_spelling_bee import SpellingBeeGUI  # Ensure correct import

class TestSpellingBeeGUI(unittest.TestCase):
    """Unit tests for the SpellingBeeGUI class."""

    @patch('spelling_bee.gui_spelling_bee.SpellingBeeGUI.on_check_words')
    @patch('spelling_bee.gui_spelling_bee.SpellingBeeGUI.on_export_csv')
    def setUp(self, mock_export_csv, mock_on_check_words):
        """Set up a SpellingBeeGUI instance with mocked methods."""
        self.gui = SpellingBeeGUI()

    @patch('spelling_bee.gui_spelling_bee.run_spelling_bee_query')
    @patch('spelling_bee.gui_spelling_bee.export_to_csv')
    def test_on_check_words_valid_input(self, mock_export, mock_query):
        """Test handling of valid input in on_check_words."""
        self.gui.entry_center = MagicMock(get=MagicMock(return_value='a'))
        self.gui.entry_other_letters = MagicMock(get=MagicMock(return_value='elpxyz'))
        self.gui.entry_min_length = MagicMock(get=MagicMock(return_value='4'))
        self.gui.entry_max_length = MagicMock(get=MagicMock(return_value='0'))
        self.gui.entry_must_contain = MagicMock(get=MagicMock(return_value=''))
        self.gui.entry_dictionary_path = MagicMock(get=MagicMock(return_value='words_alpha.txt'))

        self.gui.on_check_words()

        mock_query.assert_called_with(
            dictionary_path='words_alpha.txt',
            center='a',
            other_letters='elpxyz',
            min_length=4,
            max_length=0,
            must_contain=''
        )
        self.gui.result_text.delete.assert_called_with(1.0, self.gui.tk.END)

    def test_on_check_words_invalid_input(self):
        """Test handling of invalid input in on_check_words."""
        self.gui.entry_center = MagicMock(get=MagicMock(return_value='ab'))
        self.gui.entry_other_letters = MagicMock(get=MagicMock(return_value='elpxyz'))

        self.gui.on_check_words()

        self.gui.messagebox.showerror.assert_called_with(
            "Input Error",
            "Please provide exactly one center letter and six other letters."
        )

    @patch('spelling_bee.gui_spelling_bee.run_spelling_bee_query', side_effect=Exception("Error"))
    def test_on_export_csv_failure(self, mock_query):
        """Test failure during export to CSV."""
        self.gui.entry_csv_path = MagicMock(get=MagicMock(return_value='results.csv'))
        self.gui.entry_center = MagicMock(get=MagicMock(return_value='a'))
        self.gui.entry_other_letters = MagicMock(get=MagicMock(return_value='elpxyz'))
        self.gui.entry_min_length = MagicMock(get=MagicMock(return_value='4'))
        self.gui.entry_max_length = MagicMock(get=MagicMock(return_value='0'))
        self.gui.entry_must_contain = MagicMock(get=MagicMock(return_value=''))
        self.gui.entry_dictionary_path = MagicMock(get=MagicMock(return_value='words_alpha.txt'))

        self.gui.on_export_csv()

        self.gui.messagebox.showerror.assert_called_with(
            "Export Failed",
            "Failed to write CSV file: Error"
        )

    @patch('spelling_bee.gui_spelling_bee.run_spelling_bee_query')
    @patch('spelling_bee.gui_spelling_bee.export_to_csv')
    def test_on_export_csv_success(self, mock_export, mock_query):
        """Test successful export to CSV."""
        mock_query.return_value = ([], set())
        self.gui.entry_csv_path = MagicMock(get=MagicMock(return_value='results.csv'))
        self.gui.entry_center = MagicMock(get=MagicMock(return_value='a'))
        self.gui.entry_other_letters = MagicMock(get=MagicMock(return_value='elpxyz'))
        self.gui.entry_min_length = MagicMock(get=MagicMock(return_value='4'))
        self.gui.entry_max_length = MagicMock(get=MagicMock(return_value='0'))
        self.gui.entry_must_contain = MagicMock(get=MagicMock(return_value=''))
        self.gui.entry_dictionary_path = MagicMock(get=MagicMock(return_value='words_alpha.txt'))

        self.gui.on_export_csv()

        mock_export.assert_called_with([], set(), 'results.csv')
        self.gui.messagebox.showinfo.assert_called_with(
            "Export Success",
            "Results successfully written to results.csv!"
        )

if __name__ == '__main__':
    unittest.main()