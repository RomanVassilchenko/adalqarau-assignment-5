import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from processor import summarize


class SummarizeTests(unittest.TestCase):
    def test_groups_and_sorts_years(self):
        data = io.StringIO(
            "contract_id,contract_date,amount_kzt\n"
            "B,2025-01-01,9\nA,2024-12-31,3\nC,2025-02-01,1\n"
        )
        self.assertEqual(summarize(data), [(2024, 1, 3), (2025, 2, 10)])

    def test_rejects_duplicate_ids_and_invalid_amounts(self):
        for rows in (
            "A,2025-01-01,1\nA,2025-01-02,2\n",
            "A,2025-01-01,-1\n",
            "A,2025-02-30,1\n",
            "A,2025-01-01,01\n",
        ):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                summarize(io.StringIO("contract_id,contract_date,amount_kzt\n" + rows))

    def test_rejects_wrong_header(self):
        with self.assertRaises(ValueError):
            summarize(io.StringIO("id,date,amount\n"))

    def test_header_only_and_zero_amount(self):
        self.assertEqual(summarize(io.StringIO("contract_id,contract_date,amount_kzt\n")), [])
        self.assertEqual(
            summarize(io.StringIO("contract_id,contract_date,amount_kzt\nA,2025-01-01,0\n")),
            [(2025, 1, 0)],
        )

    def test_rejects_extra_and_missing_fields(self):
        for record in ("A,2025-01-01,1,unexpected\n", "A,2025-01-01\n"):
            with self.subTest(record=record), self.assertRaises(ValueError):
                summarize(io.StringIO("contract_id,contract_date,amount_kzt\n" + record))

    def test_cli_refuses_to_overwrite_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.csv"
            original = b"contract_id,contract_date,amount_kzt\nA,2025-01-01,1\n"
            path.write_bytes(original)
            result = subprocess.run(
                [sys.executable, Path(__file__).with_name("processor.py"), str(path), str(path)],
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
