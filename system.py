# Manages records, storage, search, and statistics.

import csv
import os
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path

from matching import find_matches as calculate_matches
from models import CSV_FIELDS, Item, MatchResult


# Define the allowed categories and statuses.
CATEGORIES = (
    "Electronics",
    "Cards and Documents",
    "Bags",
    "Clothing",
    "Keys",
    "Books",
    "Accessories",
    "Other",
)

STATUSES = ("Open", "Possible Match", "Returned", "Closed")
REPORT_TYPES = ("Lost", "Found")


# Manage all item reports and file operations.
class LostAndFoundSystem:
    # Create the system and load saved records.
    def __init__(self, data_file: str | Path | None = None) -> None:
        if data_file is None:
            project_folder = Path(__file__).resolve().parent
            self.data_file = project_folder / "data" / "items.csv"
        else:
            self.data_file = Path(data_file)

        self.items: list[Item] = []
        self.load_errors: list[str] = []
        self.invalid_header = False
        self.load_items()

    # Check that a date uses the required format.
    def _validate_date(self, report_date: str) -> None:
        try:
            parsed_date = datetime.strptime(report_date, "%Y-%m-%d")
            if parsed_date.strftime("%Y-%m-%d") != report_date:
                raise ValueError("Invalid date format.")
        except ValueError as error:
            raise ValueError("Date must use YYYY-MM-DD format.") from error

    # Check the required values of one item.
    def _validate_item(self, item: Item) -> None:
        if item.report_type not in REPORT_TYPES:
            raise ValueError("Report type must be Lost or Found.")

        expected_prefix = "L" if item.report_type == "Lost" else "F"
        if (
            not item.report_id.startswith(expected_prefix)
            or not item.report_id[1:].isdigit()
        ):
            raise ValueError("Report ID has an invalid format.")
        if not item.item_name:
            raise ValueError("Item name is required.")
        if item.category not in CATEGORIES:
            raise ValueError("Select a valid category.")
        if not item.location:
            raise ValueError("Location is required.")
        if item.status not in STATUSES:
            raise ValueError("Select a valid status.")

        self._validate_date(item.report_date)

    # Create the data folder and CSV file when missing.
    def _create_data_file(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists() or self.data_file.stat().st_size == 0:
            with self.data_file.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
                writer.writeheader()

    # Load valid records while skipping damaged rows.
    def load_items(self) -> None:
        self.items = []
        self.load_errors = []
        self.invalid_header = False
        self._create_data_file()

        with self.data_file.open("r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file, strict=True)
            field_names = reader.fieldnames or []
            missing_fields = [name for name in CSV_FIELDS if name not in field_names]

            if missing_fields:
                self.invalid_header = True
                self.load_errors.append(
                    f"Missing CSV fields: {', '.join(missing_fields)}"
                )
                return

            used_ids = set()
            while True:
                try:
                    row = next(reader)
                except StopIteration:
                    break
                except csv.Error as error:
                    self.load_errors.append(f"Row {reader.line_num}: {error}")
                    continue

                try:
                    if None in row or any(value is None for value in row.values()):
                        raise ValueError("Incorrect number of CSV fields.")
                    item = Item.from_csv_row(row)
                    self._validate_item(item)

                    if not item.report_id:
                        raise ValueError("Report ID is required.")
                    if item.report_id in used_ids:
                        raise ValueError("Duplicate report ID.")

                    self.items.append(item)
                    used_ids.add(item.report_id)
                except (TypeError, ValueError) as error:
                    self.load_errors.append(f"Row {reader.line_num}: {error}")

    # Save all current records to the CSV file.
    def save_items(self) -> None:
        if self.invalid_header:
            raise ValueError("CSV header is invalid. Correct the header and restart before saving.")
        used_ids = set()
        for item in self.items:
            self._validate_item(item)
            if item.report_id in used_ids:
                raise ValueError("Duplicate report ID. Existing records cannot be overwritten.")
            used_ids.add(item.report_id)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        # Replace the original only after the temporary file is complete.
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", newline="", encoding="utf-8", dir=self.data_file.parent,
                prefix="items_", suffix=".tmp", delete=False
            ) as file:
                temporary_path = Path(file.name)
                writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
                writer.writeheader()
                for item in self.items:
                    writer.writerow(item.to_csv_row())
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary_path, self.data_file)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

    # Generate the next Lost or Found report ID.
    def generate_report_id(self, report_type: str) -> str:
        if report_type not in REPORT_TYPES:
            raise ValueError("Report type must be Lost or Found.")

        prefix = "L" if report_type == "Lost" else "F"
        highest_number = 0

        for item in self.items:
            report_id = item.report_id
            if report_id.startswith(prefix) and report_id[1:].isdigit():
                number = int(report_id[1:])
                if number > highest_number:
                    highest_number = number

        return f"{prefix}{highest_number + 1:03d}"

    # Return one item by its report ID.
    def get_item(self, report_id: str) -> Item | None:
        wanted_id = report_id.strip().casefold()
        for item in self.items:
            if item.report_id.casefold() == wanted_id:
                return item
        return None

    # Add and save a new report.
    def add_item(
        self,
        report_type: str,
        item_name: str,
        category: str,
        colour: str = "",
        brand: str = "Unknown",
        location: str = "",
        report_date: str = "",
        description: str = "",
        contact: str = "",
    ) -> Item:
        item = Item(
            report_id=self.generate_report_id(report_type),
            report_type=report_type,
            item_name=item_name,
            category=category,
            colour=colour,
            brand=brand,
            location=location,
            report_date=report_date,
            description=description,
            contact=contact,
            status="Open",
        )

        self._validate_item(item)
        self.items.append(item)
        try:
            self.save_items()
        except (ValueError, OSError, UnicodeError):
            self.items.remove(item)
            raise
        return item

    # Edit and save an existing report.
    def edit_item(
        self,
        report_id: str,
        item_name: str,
        category: str,
        colour: str = "",
        brand: str = "Unknown",
        location: str = "",
        report_date: str = "",
        description: str = "",
        contact: str = "",
    ) -> Item:
        item = self.get_item(report_id)
        if item is None:
            raise ValueError("Report ID was not found.")

        updated_item = Item(
            report_id=item.report_id,
            report_type=item.report_type,
            item_name=item_name,
            category=category,
            colour=colour,
            brand=brand,
            location=location,
            report_date=report_date,
            description=description,
            contact=contact,
            status=item.status,
        )

        self._validate_item(updated_item)
        item_index = self.items.index(item)
        self.items[item_index] = updated_item
        try:
            self.save_items()
        except (ValueError, OSError, UnicodeError):
            self.items[item_index] = item
            raise
        return updated_item

    # Change and save a report status.
    def update_status(self, report_id: str, status: str) -> Item:
        item = self.get_item(report_id)
        if item is None:
            raise ValueError("Report ID was not found.")
        if status not in STATUSES:
            raise ValueError("Select a valid status.")

        old_status = item.status
        item.status = status
        try:
            self.save_items()
        except (ValueError, OSError, UnicodeError):
            item.status = old_status
            raise
        return item

    # Update both reports in a match and save them together.
    def update_match_status(self, lost_id: str, found_id: str, status: str) -> None:
        lost_item = self.get_item(lost_id)
        found_item = self.get_item(found_id)
        if lost_item is None or found_item is None:
            raise ValueError("One of the reports was not found.")
        if lost_item.report_type != "Lost" or found_item.report_type != "Found":
            raise ValueError("Select one Lost report and one Found report.")
        if status not in ("Possible Match", "Returned"):
            raise ValueError("Match status must be Possible Match or Returned.")
        if (
            lost_item.status not in ("Open", "Possible Match")
            or found_item.status not in ("Open", "Possible Match")
        ):
            raise ValueError("Only active reports can be updated as a match.")

        old_lost_status = lost_item.status
        old_found_status = found_item.status
        lost_item.status = status
        found_item.status = status
        try:
            self.save_items()
        except (ValueError, OSError, UnicodeError):
            lost_item.status = old_lost_status
            found_item.status = old_found_status
            raise

    # Delete and save one report.
    def delete_item(self, report_id: str) -> bool:
        item = self.get_item(report_id)
        if item is None:
            return False

        item_index = self.items.index(item)
        self.items.remove(item)
        try:
            self.save_items()
        except (ValueError, OSError, UnicodeError):
            self.items.insert(item_index, item)
            raise
        return True

    # Search text and apply optional record filters.
    def search_items(
        self,
        query: str = "",
        report_type: str = "",
        category: str = "",
        status: str = "",
        report_date: str = "",
    ) -> list[Item]:
        query_value = query.strip().casefold()
        if report_date:
            self._validate_date(report_date)
        results = []

        for item in self.items:
            searchable_text = " ".join(
                [
                    item.report_id,
                    item.item_name,
                    item.description,
                    item.location,
                ]
            ).casefold()

            if query_value and query_value not in searchable_text:
                continue
            if report_type and item.report_type.casefold() != report_type.casefold():
                continue
            if category and item.category.casefold() != category.casefold():
                continue
            if status and item.status.casefold() != status.casefold():
                continue
            if report_date and item.report_date != report_date:
                continue

            results.append(item)

        return results

    # Find matches for one report or all active reports.
    def find_matches(
        self,
        report_id: str | None = None,
        minimum_score: int = 50,
    ) -> list[MatchResult]:
        if report_id is None:
            return calculate_matches(self.items, minimum_score=minimum_score)

        selected_item = self.get_item(report_id)
        if selected_item is None:
            return []

        return calculate_matches(
            self.items,
            selected_item=selected_item,
            minimum_score=minimum_score,
        )

    # Calculate the values shown on statistics pages.
    def get_statistics(self) -> dict[str, object]:
        category_counts = Counter(item.category for item in self.items)
        location_counts = Counter(item.location for item in self.items)

        total_lost = sum(item.report_type == "Lost" for item in self.items)
        total_found = sum(item.report_type == "Found" for item in self.items)
        open_cases = sum(
            item.status in ("Open", "Possible Match") for item in self.items
        )
        returned_items = sum(item.status == "Returned" for item in self.items)
        # Count recovered Lost reports without counting both sides twice.
        successful_matches = 0
        for item in self.items:
            if item.report_type == "Lost" and item.status == "Returned":
                successful_matches += 1
        high_matches = self.find_matches(minimum_score=80)

        most_common_category = ""
        if category_counts:
            most_common_category = category_counts.most_common(1)[0][0]

        most_common_location = ""
        if location_counts:
            most_common_location = location_counts.most_common(1)[0][0]

        return {
            "total_lost": total_lost,
            "total_found": total_found,
            "open_cases": open_cases,
            "returned_items": returned_items,
            "successful_matches": successful_matches,
            "high_match_count": len(high_matches),
            "most_common_category": most_common_category,
            "most_common_location": most_common_location,
            "category_counts": dict(category_counts),
        }
