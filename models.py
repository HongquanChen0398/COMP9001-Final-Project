# Defines the project data models.

from typing import Mapping


# Define the CSV column names and order.
CSV_FIELDS = (
    "report_id",
    "report_type",
    "item_name",
    "category",
    "colour",
    "brand",
    "location",
    "report_date",
    "description",
    "contact",
    "status",
)

# Convert a value to stripped text.
def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


# Represent one lost or found item report.
class Item:
    # Create and clean an item report.
    def __init__(
        self,
        report_id: str,
        report_type: str,
        item_name: str,
        category: str,
        colour: str = "",
        brand: str = "Unknown",
        location: str = "",
        report_date: str = "",
        description: str = "",
        contact: str = "",
        status: str = "Open",
    ) -> None:
        self.report_id = _clean(report_id)
        self.report_type = _clean(report_type)
        self.item_name = _clean(item_name)
        self.category = _clean(category)
        self.colour = _clean(colour)
        self.brand = _clean(brand) or "Unknown"
        self.location = _clean(location)
        self.report_date = _clean(report_date)
        self.description = _clean(description)
        self.contact = _clean(contact)
        self.status = _clean(status) or "Open"

    # Convert the item to a CSV-compatible row.
    def to_csv_row(self) -> dict[str, str]:
        return {field_name: getattr(self, field_name) for field_name in CSV_FIELDS}

    # Create an item from a CSV row.
    @classmethod
    def from_csv_row(cls, row: Mapping[str, object]) -> "Item":
        missing_fields = [field_name for field_name in CSV_FIELDS if field_name not in row]
        if missing_fields:
            raise ValueError(f"Missing CSV fields: {', '.join(missing_fields)}")

        return cls(**{field_name: _clean(row[field_name]) for field_name in CSV_FIELDS})

    # Compare two items by their stored field values.
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Item):
            return False

        return self.to_csv_row() == other.to_csv_row()


# Store one lost-and-found matching result.
class MatchResult:
    # Create a match result with an independent reasons list.
    def __init__(
        self,
        lost_item: Item,
        found_item: Item,
        score: int,
        match_level: str,
        reasons: list[str] | None = None,
    ) -> None:
        self.lost_item = lost_item
        self.found_item = found_item
        self.score = score
        self.match_level = match_level
        self.reasons = list(reasons) if reasons is not None else []

    # Compare two matching results by their stored values.
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MatchResult):
            return False

        return (
            self.lost_item == other.lost_item
            and self.found_item == other.found_item
            and self.score == other.score
            and self.match_level == other.match_level
            and self.reasons == other.reasons
        )
