# Test the core item matching logic.

# Import testing tools and project code.
import tempfile
import csv
import unittest
from unittest.mock import patch
from pathlib import Path

from matching import calculate_match, find_matches
from models import CSV_FIELDS, Item
from system import LostAndFoundSystem


# Check the core test scenarios.
class MatchingTests(unittest.TestCase):
    # Create a test item with default values.
    def make_item(
        self,
        report_id: str,
        report_type: str,
        item_name: str = "AirPods",
        category: str = "Electronics",
        colour: str = "Black",
        brand: str = "Apple",
        location: str = "Fisher Library",
        report_date: str = "2026-10-20",
        description: str = "Black case with a scratch",
        status: str = "Open",
    ) -> Item:
        return Item(
            report_id=report_id,
            report_type=report_type,
            item_name=item_name,
            category=category,
            colour=colour,
            brand=brand,
            location=location,
            report_date=report_date,
            description=description,
            contact="student@example.com",
            status=status,
        )

    # Check that identical items receive a full score.
    def test_identical_items(self) -> None:
        lost_item = self.make_item("L001", "Lost")
        found_item = self.make_item("F001", "Found")

        result = calculate_match(lost_item, found_item)

        self.assertEqual(result.score, 100)
        self.assertEqual(result.match_level, "High Match")

    # Check that different items receive a low match score.
    def test_completely_different_items(self) -> None:
        lost_item = self.make_item("L001", "Lost")
        found_item = self.make_item(
            "F001",
            "Found",
            item_name="Notebook",
            category="Books",
            colour="Blue",
            brand="Moleskine",
            location="Sports Centre",
            report_date="2026-11-20",
            description="Lined pages with a red bookmark",
        )

        result = calculate_match(lost_item, found_item)

        self.assertLess(result.score, 50)
        self.assertEqual(result.match_level, "Low Match")

    # Check that letter case does not affect matching.
    def test_case_insensitive_matching(self) -> None:
        lost_item = self.make_item("L001", "Lost")
        found_item = self.make_item(
            "F001",
            "Found",
            item_name="AIRPODS",
            category="electronics",
            colour="black",
            brand="APPLE",
            location="fisher library",
            description="BLACK CASE WITH A SCRATCH",
        )

        result = calculate_match(lost_item, found_item)

        self.assertEqual(result.score, 100)

    # Check scores for different date intervals.
    def test_date_scores(self) -> None:
        lost_item = self.make_item(
            "L001",
            "Lost",
            item_name="Phone",
            category="Electronics",
            colour="Black",
            brand="Apple",
            location="North Building",
            report_date="2026-10-20",
            description="Cracked screen",
        )

        date_cases = [
            ("2026-10-21", 10),
            ("2026-10-25", 5),
            ("2026-10-30", 0),
        ]

        for index, date_case in enumerate(date_cases, start=1):
            found_date, expected_score = date_case
            found_item = self.make_item(
                f"F{index:03d}",
                "Found",
                item_name="Notebook",
                category="Books",
                colour="White",
                brand="Campus",
                location="South Building",
                report_date=found_date,
                description="Plain lined pages",
            )

            result = calculate_match(lost_item, found_item)
            self.assertEqual(result.score, expected_score)

    # Check that an earlier Found date earns no date points.
    def test_found_date_before_lost_date(self) -> None:
        lost_item = self.make_item(
            "L001",
            "Lost",
            item_name="Phone",
            category="Electronics",
            location="North Building",
            report_date="2026-10-20",
            description="Cracked screen",
        )
        found_item = self.make_item(
            "F001",
            "Found",
            item_name="Notebook",
            category="Books",
            colour="White",
            brand="Campus",
            location="South Building",
            report_date="2026-10-19",
            description="Plain lined pages",
        )

        result = calculate_match(lost_item, found_item)

        self.assertEqual(result.score, 0)
        self.assertTrue(any("earlier" in reason for reason in result.reasons))

    # Check that returned items are excluded from matching.
    def test_returned_report_is_excluded(self) -> None:
        lost_item = self.make_item("L001", "Lost")
        found_item = self.make_item("F001", "Found", status="Returned")

        results = find_matches([lost_item, found_item])

        self.assertEqual(results, [])

    # Check that a missing data file is created automatically.
    def test_missing_csv_file_is_created(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            data_file = Path(folder) / "data" / "items.csv"

            system = LostAndFoundSystem(data_file)

            self.assertTrue(data_file.exists())
            self.assertEqual(system.items, [])
            with data_file.open("r", encoding="utf-8") as file:
                self.assertEqual(file.readline().strip(), ",".join(CSV_FIELDS))

    # Check that an invalid report ID returns an empty result.
    def test_invalid_report_id(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            data_file = Path(folder) / "items.csv"
            system = LostAndFoundSystem(data_file)

            self.assertIsNone(system.get_item("BAD"))
            self.assertEqual(system.find_matches("BAD"), [])

    # Check that an unsuccessful search returns an empty list.
    def test_no_search_results(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            data_file = Path(folder) / "items.csv"
            system = LostAndFoundSystem(data_file)
            system.add_item(
                "Lost",
                "Keys",
                "Keys",
                "Silver",
                "Unknown",
                "Library",
                "2026-10-20",
                "Two keys on a ring",
                "student@example.com",
            )

            results = system.search_items("umbrella")

            self.assertEqual(results, [])

    # Check that matches are sorted by descending score.
    def test_multiple_results_are_sorted(self) -> None:
        lost_item = self.make_item("L001", "Lost")
        high_match = self.make_item("F001", "Found")
        possible_match = self.make_item(
            "F002",
            "Found",
            item_name="Calculator",
            category="Electronics",
            colour="White",
            brand="Casio",
            location="Fisher Library",
            description="Scientific calculator",
        )

        results = find_matches([lost_item, possible_match, high_match])

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].found_item.report_id, "F001")
        self.assertGreaterEqual(results[0].score, results[1].score)


# Test file errors and integrated record operations.
class SystemErrorTests(unittest.TestCase):
    # Use a separate temporary file for each test.
    def setUp(self) -> None:
        self.folder = tempfile.TemporaryDirectory()
        self.data_file = Path(self.folder.name) / "items.csv"
        self.system = LostAndFoundSystem(self.data_file)

    # Remove temporary test files.
    def tearDown(self) -> None:
        self.folder.cleanup()

    # Add a valid report for error handling tests.
    def add_report(self, report_type="Lost"):
        return self.system.add_item(
            report_type, "Phone", "Electronics", "Black", "Apple",
            "Library", "2026-10-01", "Black case"
        )

    # Reject invalid dates and required fields before saving.
    def test_invalid_input_keeps_data_unchanged(self) -> None:
        for report_date in ("2026-1-1", "2026-02-30", "invalid", ""):
            with self.subTest(report_date=report_date):
                with self.assertRaises(ValueError):
                    self.system.add_item("Lost", "Phone", "Electronics", location="Library", report_date=report_date)
        with self.assertRaises(ValueError):
            self.system.add_item("Lost", "", "Electronics", location="Library", report_date="2026-10-01")
        self.assertEqual(self.system.items, [])

    # Skip duplicate and incomplete rows, and accept a UTF-8 BOM.
    def test_damaged_rows_and_duplicate_ids(self) -> None:
        item = self.add_report()
        with self.data_file.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_FIELDS)
            writer.writerow(item.to_csv_row().values())
            writer.writerow(item.to_csv_row().values())
            writer.writerow(["L002", "Lost"])
        loaded = LostAndFoundSystem(self.data_file)
        self.assertEqual(len(loaded.items), 1)
        self.assertEqual(len(loaded.load_errors), 2)

    # Skip a malformed quoted row and load the next valid row.
    def test_malformed_csv_row(self) -> None:
        item = self.add_report()
        with self.data_file.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_FIELDS)
            file.write('"broken"unexpected,Lost\n')
            writer.writerow(item.to_csv_row().values())
        loaded = LostAndFoundSystem(self.data_file)
        self.assertEqual(len(loaded.items), 1)
        self.assertTrue(loaded.load_errors)

    # Preserve files with invalid headers instead of overwriting them.
    def test_invalid_header_blocks_saving(self) -> None:
        with self.data_file.open("w", encoding="utf-8") as file:
            file.write("wrong,header\nimportant,data\n")
        original = self.data_file.read_bytes()
        self.system = LostAndFoundSystem(self.data_file)
        with self.assertRaises(ValueError):
            self.add_report()
        self.assertEqual(self.data_file.read_bytes(), original)
        self.assertEqual(self.system.items, [])

    # Restore memory and keep the original CSV after a save failure.
    def test_failed_operations_restore_original_data(self) -> None:
        lost = self.add_report()
        found = self.add_report("Found")
        original = self.data_file.read_bytes()
        with patch("system.os.replace", side_effect=PermissionError("File is locked")):
            with self.assertRaises(OSError):
                self.add_report()
            self.assertEqual(len(self.system.items), 2)
            with self.assertRaises(OSError):
                self.system.edit_item(lost.report_id, "New phone", "Electronics", location="Library", report_date="2026-10-01")
            self.assertEqual(self.system.get_item(lost.report_id).item_name, "Phone")
            with self.assertRaises(OSError):
                self.system.update_status(lost.report_id, "Closed")
            self.assertEqual(lost.status, "Open")
            with self.assertRaises(OSError):
                self.system.delete_item(lost.report_id)
            self.assertIs(self.system.get_item(lost.report_id), lost)
            with self.assertRaises(OSError):
                self.system.update_match_status(lost.report_id, found.report_id, "Returned")
            self.assertEqual(lost.status, "Open")
            self.assertEqual(found.status, "Open")
        self.assertEqual(self.data_file.read_bytes(), original)
        self.assertEqual(list(self.data_file.parent.glob("*.tmp")), [])

    # Reject duplicate IDs before any file is replaced.
    def test_duplicate_id_cannot_overwrite_csv(self) -> None:
        item = self.add_report()
        original = self.data_file.read_bytes()
        self.system.items.append(item)
        with self.assertRaises(ValueError):
            self.system.save_items()
        self.assertEqual(self.data_file.read_bytes(), original)

    # Validate optional search dates.
    def test_invalid_search_date(self) -> None:
        with self.assertRaises(ValueError):
            self.system.search_items(report_date="2026-1-1")

    # Save paired status changes and exclude closed or returned reports.
    def test_status_persistence_and_statistics(self) -> None:
        lost = self.add_report()
        found = self.add_report("Found")
        self.system.update_status(found.report_id, "Closed")
        self.assertEqual(self.system.find_matches(), [])
        self.system.update_status(found.report_id, "Open")
        self.system.update_match_status(lost.report_id, found.report_id, "Returned")
        loaded = LostAndFoundSystem(self.data_file)
        self.assertEqual(loaded.find_matches(), [])
        self.assertEqual(loaded.get_statistics()["returned_items"], 2)
        self.assertEqual(loaded.get_statistics()["successful_matches"], 1)


# Run the tests when this file is executed directly.
if __name__ == "__main__":
    unittest.main()
