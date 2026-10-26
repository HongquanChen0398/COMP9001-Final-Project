# Calculates lost-and-found match scores.

# Import standard-library tools and project models.
from datetime import datetime
import re

from models import Item, MatchResult


# Define words ignored during keyword matching.
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "was",
    "were",
    "with",
}

ACTIVE_STATUSES = {"open", "possible match"}


# Convert text to lowercase words without punctuation.
def normalise_text(value: str) -> str:
    words = re.findall(r"[a-z0-9]+", str(value).casefold())
    return " ".join(words)


# Extract useful keywords from names and descriptions.
def extract_keywords(*values: str) -> set[str]:
    words = set()
    for value in values:
        words.update(normalise_text(value).split())
    return words - STOP_WORDS


# Calculate the shared keyword score out of 20.
def _keyword_score(lost_item: Item, found_item: Item) -> int:
    lost_words = extract_keywords(lost_item.item_name, lost_item.description)
    found_words = extract_keywords(found_item.item_name, found_item.description)
    all_words = lost_words | found_words

    if not all_words:
        return 0

    shared_proportion = len(lost_words & found_words) / len(all_words)
    return round(shared_proportion * 20)


# Calculate the location score out of 20.
def _location_score(lost_location: str, found_location: str) -> int:
    lost_value = normalise_text(lost_location)
    found_value = normalise_text(found_location)

    if not lost_value or not found_value:
        return 0
    if lost_value == found_value:
        return 20
    if lost_value in found_value or found_value in lost_value:
        return 10
    return 0


# Calculate the date score out of 15 and return its explanation.
def _date_score(lost_date: str, found_date: str) -> tuple[int, str]:
    try:
        lost_value = datetime.strptime(lost_date, "%Y-%m-%d").date()
        found_value = datetime.strptime(found_date, "%Y-%m-%d").date()
    except ValueError:
        return 0, "Invalid date format +0"

    if found_value < lost_value:
        return 0, "Found date is earlier than Lost date +0"

    difference = (found_value - lost_value).days
    if difference == 0:
        return 15, "Same date +15"
    if difference <= 3:
        return 10, f"Date difference {difference} day(s) +10"
    if difference <= 7:
        return 5, f"Date difference {difference} days +5"
    return 0, f"Date difference {difference} days +0"


# Convert a score to its required match level.
def get_match_level(score: int) -> str:
    if score >= 80:
        return "High Match"
    if score >= 50:
        return "Possible Match"
    return "Low Match"


# Calculate one Lost and Found pair's score and reasons.
def calculate_match(first_item: Item, second_item: Item) -> MatchResult:
    first_type = normalise_text(first_item.report_type)
    second_type = normalise_text(second_item.report_type)

    if first_type == "lost" and second_type == "found":
        lost_item, found_item = first_item, second_item
    elif first_type == "found" and second_type == "lost":
        lost_item, found_item = second_item, first_item
    else:
        raise ValueError("A match requires one Lost report and one Found report.")

    score = 0
    reasons = []

    lost_category = normalise_text(lost_item.category)
    found_category = normalise_text(found_item.category)
    if lost_category and lost_category == found_category:
        score += 25
        reasons.append("Same category +25")

    keyword_score = _keyword_score(lost_item, found_item)
    if keyword_score:
        score += keyword_score
        reasons.append(f"Shared name and description keywords +{keyword_score}")

    location_score = _location_score(lost_item.location, found_item.location)
    if location_score:
        score += location_score
        label = "Same location" if location_score == 20 else "Related location"
        reasons.append(f"{label} +{location_score}")

    date_score, date_reason = _date_score(lost_item.report_date, found_item.report_date)
    score += date_score
    reasons.append(date_reason)

    if normalise_text(lost_item.colour) and (
        normalise_text(lost_item.colour) == normalise_text(found_item.colour)
    ):
        score += 10
        reasons.append("Same colour +10")

    lost_brand = normalise_text(lost_item.brand)
    found_brand = normalise_text(found_item.brand)
    if (
        lost_brand
        and found_brand
        and lost_brand != "unknown"
        and found_brand != "unknown"
        and lost_brand == found_brand
    ):
        score += 10
        reasons.append("Same brand +10")

    return MatchResult(
        lost_item=lost_item,
        found_item=found_item,
        score=score,
        match_level=get_match_level(score),
        reasons=reasons,
    )


# Check whether a report can participate in matching.
def _is_active(item: Item) -> bool:
    return normalise_text(item.status) in ACTIVE_STATUSES


# Build the sorting values for one match result.
def _match_sort_key(result: MatchResult) -> tuple[int, str, str]:
    return (
        -result.score,
        result.lost_item.report_id,
        result.found_item.report_id,
    )


# Find active matches and sort them by descending score.
def find_matches(
    items: list[Item],
    selected_item: Item | None = None,
    minimum_score: int = 50,
) -> list[MatchResult]:
    active_items = [item for item in items if _is_active(item)]
    results = []

    if selected_item is not None:
        if not _is_active(selected_item):
            return []

        selected_type = normalise_text(selected_item.report_type)
        for item in active_items:
            if item.report_id == selected_item.report_id:
                continue
            if normalise_text(item.report_type) == selected_type:
                continue

            try:
                result = calculate_match(selected_item, item)
            except ValueError:
                continue

            if result.score >= minimum_score:
                results.append(result)
    else:
        lost_items = [
            item for item in active_items if normalise_text(item.report_type) == "lost"
        ]
        found_items = [
            item for item in active_items if normalise_text(item.report_type) == "found"
        ]

        for lost_item in lost_items:
            for found_item in found_items:
                result = calculate_match(lost_item, found_item)
                if result.score >= minimum_score:
                    results.append(result)

    return sorted(results, key=_match_sort_key)
