import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import main


class ExpenseTrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.expenses_file = Path(self.temp_directory.name) / "expenses.json"
        self.expenses_file.write_text('["12.50", "7.50"]', encoding="utf-8")
        self.expenses_file_patch = patch.object(
            main, "EXPENSES_FILE", str(self.expenses_file)
        )
        self.expenses_file_patch.start()

    def tearDown(self):
        self.expenses_file_patch.stop()
        self.temp_directory.cleanup()

    def test_load_expenses_returns_saved_list(self):
        self.assertEqual(main.load_expenses(), ["12.50", "7.50"])

    def test_load_expenses_returns_empty_list_for_missing_or_invalid_file(self):
        self.expenses_file.unlink()
        self.assertEqual(main.load_expenses(), [])

        self.expenses_file.write_text("{not valid json", encoding="utf-8")
        self.assertEqual(main.load_expenses(), [])

        self.expenses_file.write_text('{"amount": 10}', encoding="utf-8")
        self.assertEqual(main.load_expenses(), [])

    def test_save_expenses_writes_indented_json(self):
        expenses = ["25", "10.75"]

        main.save_expenses(expenses)

        self.assertEqual(json.loads(self.expenses_file.read_text()), expenses)
        self.assertIn("\n  ", self.expenses_file.read_text())

    @patch("builtins.input", return_value="30")
    def test_add_expense_appends_and_persists_expense(self, mock_input):
        expenses = ["10"]
        output = StringIO()

        with redirect_stdout(output):
            main.add_expense(expenses)

        mock_input.assert_called_once_with("enter expense: ")
        self.assertEqual(expenses, ["10", "30"])
        self.assertEqual(main.load_expenses(), ["10", "30"])
        self.assertIn("expense 30 added successfully", output.getvalue())

    def test_view_expense_reports_empty_list(self):
        output = StringIO()

        with redirect_stdout(output):
            main.view_expense([])

        self.assertEqual(output.getvalue(), "no expenses to view\n")

    @patch("builtins.input", return_value="2")
    def test_split_expense_prints_equal_share(self, mock_input):
        output = StringIO()

        with redirect_stdout(output):
            main.split_expense(["10", "5"])

        mock_input.assert_called_once_with(
            "enter number of people to split the expense: "
        )
        self.assertIn("total expense: 15.0", output.getvalue())
        self.assertIn("each person should pay: 7.5", output.getvalue())

    @patch("builtins.input", return_value="0")
    def test_split_expense_rejects_non_positive_people_count(self, mock_input):
        output = StringIO()

        with redirect_stdout(output):
            main.split_expense(["10"])

        self.assertIn("number of people must be greater than zero", output.getvalue())

    @patch("builtins.input", side_effect=["9", "3"])
    def test_main_exits_after_requested_choice(self, mock_input):
        output = StringIO()

        with redirect_stdout(output):
            main.main()

        self.assertIn("invalid choice", output.getvalue())
        self.assertIn("exiting the program", output.getvalue())
        self.assertEqual(mock_input.call_count, 2)


if __name__ == "__main__":
    unittest.main()
