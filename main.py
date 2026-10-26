# Starts the Campus Lost and Found application.

# Import the window and application classes.
import tkinter as tk
import csv
from tkinter import messagebox

from gui import LostAndFoundGUI
from system import LostAndFoundSystem


# Load records, build the window, and start the application.
def main() -> None:
    try:
        root = tk.Tk()
    except tk.TclError as error:
        print(f"Unable to open the GUI. Check that Tkinter and a desktop display are available.\n{error}")
        return
    root.withdraw()

    try:
        system = LostAndFoundSystem()
    except (OSError, UnicodeError, csv.Error) as error:
        messagebox.showerror(
            "Startup error", f"Unable to load the data file.\n{error}", parent=root
        )
        root.destroy()
        return

    application = LostAndFoundGUI(root, system)
    root.deiconify()
    root.mainloop()


# Run the application when this file is executed directly.
if __name__ == "__main__":
    main()
