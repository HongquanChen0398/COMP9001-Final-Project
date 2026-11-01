Campus Lost and Found Matcher

Requirements
- Python 3.10+ with Tkinter and a desktop display.
- Write permission for the project folder.
- No third-party packages or pip installation required.
- Tested on Windows with Python 3.11.1.

Imported Libraries
All imports below are from Python's standard library:
- tkinter, tkinter.ttk, tkinter.messagebox: windows, widgets, and dialogs.
- csv: reads and writes report records.
- datetime (date, datetime): default dates, validation, and date comparisons.
- os: safely replaces the CSV file after writing.
- tempfile: creates temporary files for saving and testing.
- collections (Counter): counts categories and locations.
- pathlib (Path): manages file and directory paths.
- re: extracts and normalises text for matching.
- typing (Mapping): describes CSV row types.
- unittest, unittest.mock (patch): runs tests and simulates save failures.

unittest and unittest.mock are used only by test_matching.py.
gui, system, matching, and models are local project modules, not libraries
to install. Keep their Python files together with main.py.
Some Linux installations require the operating system's Tkinter package.

How to Run
1. Download and extract the project.
2. Open a terminal in the folder containing main.py.
3. Run: python main.py
   Use python3 instead of python if needed.

How to Use Each Function

Dashboard
1. Click Dashboard to view Lost, Found, Open, Returned, and High Match counts.
2. Double-click a recent report to view its details.
3. Use Report Lost Item, Report Found Item, or Find Matches as shortcuts.

Create a Report
1. Click Report Item and choose Lost or Found.
2. Enter Item Name, Category, Location, and Date (YYYY-MM-DD).
3. Optionally enter Colour, Brand, Contact, and Description.
4. Click Save Report. An ID is generated and the record is saved immediately.
   The form clears; a notification appears if possible matches exist.
5. Click Clear Form to reset unsaved input without deleting saved reports.

Search and Filter
1. Click Records and enter an ID, item name, description, or location in Search.
2. Optionally select Type, Category, Status, and an exact Date (YYYY-MM-DD).
3. Click Search. Text searches ignore letter case.
4. Click Reset to clear all conditions and show every record.

View and Edit a Report
1. In Records, select a row and click View Details, or double-click the row.
2. To edit, select a row and click Edit. Change the form fields.
3. Click Save Changes to save, or Cancel Edit to discard changes.
   The report ID, type, and status remain unchanged when editing the form.

Update a Report's Status
1. In Records, select a row and click Update Status.
2. Choose Open, Possible Match, Returned, or Closed.
3. Click Save Status. This changes only the selected report.
   Returned and Closed reports are excluded from matching.

Delete a Report
1. In Records, select a row and click Delete.
2. Confirm to permanently remove the record, or decline to keep it.

Find Matches
1. Click Matches, select a Report ID, and click Find Matches.
   Alternatively, select a row in Records before opening Matches.
2. Select a result to view both reports and the score explanation.
   Scores of 50+ are shown, highest first; 80+ means High Match.
3. Click Mark as Possible Match and confirm to update both reports.
4. After verifying ownership and returning the item, select the match and
   click Mark as Returned, then confirm. Both reports stop appearing in matches.
   The application suggests matches; it does not verify ownership or send messages.

Statistics
1. Click Statistics to view totals, active cases, returned reports, high
   matches, common category/location, and the category counts table.
2. Reopen the page after changes to view refreshed statistics.
   Successful Matches counts Lost reports marked Returned, not saved pair history.

Exit and Reload
1. Click Exit or the window close button and confirm.
2. Run python main.py again to reload previously saved records.

Python Files
- main.py: Starts the application.
- models.py: Defines report and match-result data models.
- system.py: Manages records, validation, CSV storage, search, and statistics.
- matching.py: Calculates, explains, and sorts match scores.
- gui.py: Builds the five pages and handles user actions.
- test_matching.py: Tests matching logic and data handling.

Data
Records are saved automatically in data/items.csv.
The data folder and file are created if missing.
Keep this file to retain saved records.

Tests
Run: python -m unittest test_matching.py -v
Expected: 18 tests pass. Tests do not change saved records.

Note
This GUI requires a desktop session and cannot run in the Ed code runner.
Check Tkinter with: python -m tkinter

GitHub Repository
https://github.com/HongquanChen0398/COMP9001-Final-Project
