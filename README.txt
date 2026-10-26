Campus Lost and Found Matcher

Requirements
- Python 3.10+ with Tkinter and a desktop display.
- Write permission for the project folder.
- No third-party packages or pip installation required.
- Tested on Windows with Python 3.11.1.

How to Run
1. Download and extract the project.
2. Open a terminal in the folder containing main.py.
3. Run: python main.py
   Use python3 instead of python if needed.

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
