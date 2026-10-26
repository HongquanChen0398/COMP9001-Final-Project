# Builds the Tkinter user interface.

# Import the GUI tools and system class.
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from system import CATEGORIES, REPORT_TYPES, STATUSES, LostAndFoundSystem


# Build the main window and page navigation.
class LostAndFoundGUI:
    # Set up the window and show the first page.
    def __init__(self, root: tk.Tk, system: LostAndFoundSystem) -> None:
        self.root = root
        self.system = system
        self.pages = {}
        self.navigation_buttons = {}
        self.current_page = ""
        self.editing_id = None
        self.status_text = tk.StringVar()
        self.record_count_text = tk.StringVar()

        self.root.title("Campus Lost and Found Matcher")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)

        self.configure_styles()
        self.create_layout()
        self.create_navigation()
        self.create_pages()
        self.show_dashboard()

        if self.system.load_errors:
            self.root.after_idle(self.show_load_errors)

    # Apply readable fonts and consistent colours.
    def configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 11), padding=(12, 9))
        style.configure("Content.TFrame", background="#F5F7FA")
        style.configure("Content.TLabel", background="#F5F7FA")
        style.configure(
            "Heading.TLabel", background="#F5F7FA", font=("Arial", 22, "bold")
        )
        style.configure("Sidebar.TFrame", background="#FFFFFF")
        style.configure(
            "Brand.TLabel", background="#FFFFFF", font=("Arial", 16, "bold")
        )
        style.configure("Nav.TButton", anchor="w", background="#FFFFFF")
        style.configure("Selected.TButton", anchor="w", background="#DBEAFE")
        style.map("Selected.TButton", background=[("active", "#BFDBFE")])

    # Create the sidebar, content area, and status bar.
    def create_layout(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.sidebar = ttk.Frame(self.root, width=190, style="Sidebar.TFrame")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.columnconfigure(0, weight=1)
        self.sidebar.rowconfigure(7, weight=1)

        self.content = ttk.Frame(self.root, padding=24, style="Content.TFrame")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        status_bar = ttk.Frame(self.root, padding=(12, 6))
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        status_bar.columnconfigure(0, weight=1)
        ttk.Label(status_bar, textvariable=self.status_text).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(status_bar, textvariable=self.record_count_text).grid(
            row=0, column=1, sticky="e"
        )

    # Add navigation buttons with named event handlers.
    def create_navigation(self) -> None:
        ttk.Label(
            self.sidebar, text="Campus\nLost & Found", style="Brand.TLabel"
        ).grid(row=0, column=0, padx=16, pady=24, sticky="w")
        ttk.Separator(self.sidebar).grid(row=1, column=0, sticky="ew", padx=12)

        navigation = [
            ("Dashboard", self.show_dashboard),
            ("Report Item", self.show_report_item),
            ("Records", self.show_records),
            ("Matches", self.show_matches),
            ("Statistics", self.show_statistics),
        ]

        for row, navigation_item in enumerate(navigation, start=2):
            page_name, handler = navigation_item
            button = ttk.Button(
                self.sidebar, text=page_name, command=handler, style="Nav.TButton"
            )
            button.grid(row=row, column=0, padx=12, pady=5, sticky="ew")
            self.navigation_buttons[page_name] = button

        ttk.Button(
            self.sidebar, text="Exit", command=self.close_application,
            style="Nav.TButton"
        ).grid(row=8, column=0, padx=12, pady=16, sticky="ew")

    # Create a frame for each page in the development plan.
    def create_pages(self) -> None:
        descriptions = {
            "Dashboard": "Overview of your campus reports.",
            "Report Item": "Report a lost or found item on campus.",
            "Records": "Search and manage your item reports.",
            "Matches": "Find possible matches and review their scores.",
            "Statistics": "View report counts and common categories.",
        }

        for page_name, description in descriptions.items():
            page = ttk.Frame(self.content, style="Content.TFrame")
            page.grid(row=0, column=0, sticky="nsew")
            page.columnconfigure(0, weight=1)

            ttk.Label(page, text=page_name, style="Heading.TLabel").grid(
                row=0, column=0, sticky="w", pady=(0, 8)
            )
            ttk.Label(page, text=description, style="Content.TLabel").grid(
                row=1, column=0, sticky="w", pady=(0, 20)
            )
            ttk.Separator(page).grid(row=2, column=0, sticky="ew")
            self.pages[page_name] = page

        self.create_report_page()
        self.create_records_page()
        self.create_matches_page()
        self.create_dashboard_page()
        self.create_statistics_page()

    # Create statistic cards and return their display variables.
    def create_statistic_cards(self, parent, fields, columns):
        values = {}
        for index, field in enumerate(fields):
            name, label = field
            column = index % columns
            parent.columnconfigure(column, weight=1, uniform="cards")
            card = ttk.LabelFrame(parent, text=label, padding=10)
            card.grid(row=index // columns, column=column, sticky="nsew", padx=4, pady=4)
            value = tk.StringVar(value="0")
            ttk.Label(card, textvariable=value, font=("Arial", 22, "bold")).pack(anchor="w")
            values[name] = value
        return values

    # Build summary cards, shortcuts, and the recent reports table.
    def create_dashboard_page(self) -> None:
        page = self.pages["Dashboard"]
        page.rowconfigure(3, weight=1)
        body = ttk.Frame(page, style="Content.TFrame", padding=(0, 12))
        body.grid(row=3, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(4, weight=1)
        cards = ttk.Frame(body, style="Content.TFrame")
        cards.grid(row=0, column=0, sticky="ew")
        self.dashboard_values = self.create_statistic_cards(cards, [
            ("total_lost", "Total Lost"), ("total_found", "Total Found"),
            ("open_cases", "Open Cases"), ("returned_items", "Returned"),
            ("high_match_count", "High Matches"),
        ], 5)

        shortcuts = ttk.Frame(body, style="Content.TFrame")
        shortcuts.grid(row=1, column=0, sticky="w", pady=14)
        for label, handler in [
            ("Report Lost Item", self.start_lost_report),
            ("Report Found Item", self.start_found_report),
            ("Find Matches", self.show_matches),
        ]:
            ttk.Button(shortcuts, text=label, command=handler).pack(side="left", padx=(0, 8))
        ttk.Label(body, text="Recent Reports", style="Content.TLabel", font=("Arial", 13, "bold")).grid(
            row=2, column=0, sticky="w"
        )
        ttk.Label(body, text="Latest report dates first. Double-click to view details.", style="Content.TLabel").grid(
            row=3, column=0, sticky="w", pady=(4, 8)
        )
        table_frame = ttk.Frame(body)
        table_frame.grid(row=4, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        columns = ("report_id", "report_type", "item_name", "report_date", "status")
        self.recent_table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse", height=5)
        for name, label, width in [
            ("report_id", "ID", 65), ("report_type", "Type", 65),
            ("item_name", "Item", 150), ("report_date", "Date", 110), ("status", "Status", 140),
        ]:
            self.recent_table.heading(name, text=label)
            self.recent_table.column(name, width=width, minwidth=60)
        self.recent_table.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(table_frame, command=self.recent_table.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.recent_table.configure(yscrollcommand=scrollbar.set)
        self.recent_table.bind("<Double-1>", self.open_recent_details)
        self.dashboard_message = tk.StringVar()
        ttk.Label(body, textvariable=self.dashboard_message, style="Content.TLabel").grid(
            row=5, column=0, sticky="w", pady=8
        )

    # Start a new Lost report from the Dashboard.
    def start_lost_report(self) -> None:
        self.clear_form()
        self.report_type.set("Lost")
        self.show_report_item()

    # Start a new Found report from the Dashboard.
    def start_found_report(self) -> None:
        self.clear_form()
        self.report_type.set("Found")
        self.show_report_item()

    # Return the date used to sort recent reports.
    def recent_report_key(self, item):
        return item.report_date

    # Refresh summary values and the five latest dated reports.
    def refresh_dashboard(self) -> None:
        statistics = self.system.get_statistics()
        for name, variable in self.dashboard_values.items():
            variable.set(str(statistics[name]))
        for row in self.recent_table.get_children():
            self.recent_table.delete(row)
        recent_items = sorted(reversed(self.system.items), key=self.recent_report_key, reverse=True)
        for item in recent_items[:5]:
            self.recent_table.insert("", "end", iid=item.report_id, values=(
                item.report_id, item.report_type, item.item_name, item.report_date, item.status
            ))
        if recent_items:
            self.dashboard_message.set(f"Showing {min(5, len(recent_items))} recent report(s).")
        else:
            self.dashboard_message.set("No reports yet. Report a lost or found item to get started.")

    # Open a recent report using the existing details window.
    def open_recent_details(self, event) -> None:
        row = self.recent_table.identify_row(event.y)
        if row:
            self.reset_search()
            self.records_table.selection_set(row)
            self.view_details()

    # Build the statistics summary and category counts table.
    def create_statistics_page(self) -> None:
        page = self.pages["Statistics"]
        page.rowconfigure(3, weight=1)
        body = ttk.Frame(page, style="Content.TFrame", padding=(0, 12))
        body.grid(row=3, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(4, weight=1)
        cards = ttk.Frame(body, style="Content.TFrame")
        cards.grid(row=0, column=0, sticky="ew")
        self.statistics_values = self.create_statistic_cards(cards, [
            ("total_lost", "Total Lost"), ("total_found", "Total Found"),
            ("open_cases", "Open Cases"), ("returned_items", "Returned Reports"),
            ("successful_matches", "Successful Matches"), ("high_match_count", "High Matches"),
        ], 3)
        self.common_category = tk.StringVar()
        self.common_location = tk.StringVar()
        ttk.Label(body, textvariable=self.common_category, style="Content.TLabel", wraplength=620).grid(
            row=1, column=0, sticky="w", pady=(8, 4)
        )
        ttk.Label(body, textvariable=self.common_location, style="Content.TLabel", wraplength=620).grid(
            row=2, column=0, sticky="w", pady=(0, 8)
        )
        ttk.Label(body, text="Reports by Category", style="Content.TLabel", font=("Arial", 13, "bold")).grid(
            row=3, column=0, sticky="w", pady=(0, 6)
        )
        table_frame = ttk.Frame(body)
        table_frame.grid(row=4, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.category_table = ttk.Treeview(table_frame, columns=("category", "count"), show="headings", height=4)
        self.category_table.heading("category", text="Category")
        self.category_table.heading("count", text="Reports")
        self.category_table.column("category", width=300)
        self.category_table.column("count", width=90, anchor="center")
        self.category_table.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(table_frame, command=self.category_table.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.category_table.configure(yscrollcommand=scrollbar.set)
        ttk.Label(
            body, text="Open cases include Possible Match. Successful matches count returned Lost reports.",
            style="Content.TLabel", wraplength=620
        ).grid(row=5, column=0, sticky="w", pady=8)

    # Refresh statistics whenever the page is opened.
    def refresh_statistics(self) -> None:
        statistics = self.system.get_statistics()
        for name, variable in self.statistics_values.items():
            variable.set(str(statistics[name]))
        category = statistics["most_common_category"] or "No data"
        location = statistics["most_common_location"] or "No data"
        self.common_category.set("Most common category: " + category)
        self.common_location.set("Most common location: " + location)
        for row in self.category_table.get_children():
            self.category_table.delete(row)
        for category in CATEGORIES:
            count = statistics["category_counts"].get(category, 0)
            self.category_table.insert("", "end", iid=category, values=(category, count))

    # Build the report selector, match table, and details area.
    def create_matches_page(self) -> None:
        page = self.pages["Matches"]
        page.rowconfigure(3, weight=1)
        body = ttk.Frame(page, style="Content.TFrame", padding=(0, 12))
        body.grid(row=3, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        controls = ttk.Frame(body, style="Content.TFrame")
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="Report ID", style="Content.TLabel").grid(row=0, column=0, padx=(0, 8))
        self.match_report_id = tk.StringVar()
        self.match_selector = ttk.Combobox(
            controls, textvariable=self.match_report_id, state="readonly", width=12
        )
        self.match_selector.grid(row=0, column=1, sticky="ew")
        self.match_selector.bind("<<ComboboxSelected>>", self.clear_match_results)
        ttk.Button(controls, text="Find Matches", command=self.run_match_search).grid(row=0, column=2, padx=(8, 0))

        panels = ttk.Panedwindow(body, orient="horizontal")
        panels.grid(row=1, column=0, sticky="nsew")
        table_frame = ttk.Frame(panels, padding=4)
        details_frame = ttk.Frame(panels, padding=4)
        panels.add(table_frame, weight=1)
        panels.add(details_frame, weight=1)
        for frame in (table_frame, details_frame):
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)

        columns = ("report_id", "item_name", "score", "match_level")
        self.matches_table = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse"
        )
        for name, label, width in [
            ("report_id", "Matched ID", 85), ("item_name", "Item", 120),
            ("score", "Score", 55), ("match_level", "Match Level", 125),
        ]:
            self.matches_table.heading(name, text=label)
            self.matches_table.column(name, width=width, minwidth=width)
        self.matches_table.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(table_frame, command=self.matches_table.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(table_frame, orient="horizontal", command=self.matches_table.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.matches_table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.matches_table.tag_configure("high", background="#DCFCE7")
        self.matches_table.bind("<<TreeviewSelect>>", self.show_match_details)

        self.match_details = tk.Text(
            details_frame, width=30, height=8, wrap="word", font=("Arial", 11),
            padx=10, pady=10, state="disabled"
        )
        self.match_details.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(details_frame, command=self.match_details.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.match_details.configure(yscrollcommand=scrollbar.set)

        self.match_message = tk.StringVar()
        ttk.Label(body, textvariable=self.match_message, style="Content.TLabel").grid(row=2, column=0, sticky="w", pady=8)
        actions = ttk.Frame(body, style="Content.TFrame")
        actions.grid(row=3, column=0, sticky="w")
        self.possible_match_button = ttk.Button(
            actions, text="Mark as Possible Match", command=self.mark_possible_match, state="disabled"
        )
        self.possible_match_button.pack(side="left", padx=(0, 8))
        self.returned_match_button = ttk.Button(
            actions, text="Mark as Returned", command=self.mark_match_returned, state="disabled"
        )
        self.returned_match_button.pack(side="left")
        self.refresh_match_choices()
        self.clear_match_results()

    # Refresh report IDs after records change.
    def refresh_match_choices(self) -> None:
        report_ids = []
        for item in self.system.items:
            report_ids.append(item.report_id)
        self.match_selector.configure(values=report_ids)
        if self.match_report_id.get() not in report_ids:
            self.match_report_id.set(report_ids[0] if report_ids else "")

    # Clear stale results when another report is selected.
    def clear_match_results(self, event=None) -> None:
        self.match_results = {}
        for row in self.matches_table.get_children():
            self.matches_table.delete(row)
        self.match_details.configure(state="normal")
        self.match_details.delete("1.0", "end")
        self.match_details.insert("end", "Select a report and click Find Matches.")
        self.match_details.configure(state="disabled")
        self.possible_match_button.configure(state="disabled")
        self.returned_match_button.configure(state="disabled")
        if self.system.items:
            self.match_message.set("Results with a score of 50 or higher are shown.")
        else:
            self.match_message.set("No reports yet. Add a Lost or Found report first.")

    # Find possible matches using the system layer.
    def run_match_search(self) -> None:
        self.clear_match_results()
        report_id = self.match_report_id.get()
        if not report_id:
            messagebox.showinfo("Select a report", "Please select a Report ID first.", parent=self.root)
            return
        results = self.system.find_matches(report_id)
        for index, result in enumerate(results):
            row_id = str(index)
            self.match_results[row_id] = result
            if result.lost_item.report_id == report_id:
                matched_item = result.found_item
            else:
                matched_item = result.lost_item
            tags = ("high",) if result.match_level == "High Match" else ()
            self.matches_table.insert(
                "", "end", iid=row_id, tags=tags,
                values=(matched_item.report_id, matched_item.item_name, result.score, result.match_level)
            )
        if results:
            self.match_message.set(f"{len(results)} possible match(es), sorted by score.")
            self.matches_table.selection_set("0")
            self.show_match_details()
        else:
            self.match_message.set("No possible matches found.")

    # Display both reports and the selected result's score reasons.
    def show_match_details(self, event=None) -> None:
        selection = self.matches_table.selection()
        if not selection or selection[0] not in self.match_results:
            return
        result = self.match_results[selection[0]]
        self.match_details.configure(state="normal")
        self.match_details.delete("1.0", "end")
        self.match_details.insert("end", f"Score: {result.score}/100\nLevel: {result.match_level}\n\nScore Breakdown\n")
        for reason in result.reasons:
            self.match_details.insert("end", reason + "\n")
        self.match_details.insert("end", "Other unmatched attributes score 0.\n")
        for item in (result.lost_item, result.found_item):
            self.match_details.insert("end", f"\n{item.report_type} Report\n")
            for name, value in item.to_csv_row().items():
                self.match_details.insert("end", name.replace("_", " ").title() + ": " + value + "\n")
        self.match_details.configure(state="disabled")
        self.possible_match_button.configure(state="normal")
        self.returned_match_button.configure(state="normal")

    # Mark both reports as a possible match.
    def mark_possible_match(self) -> None:
        self.update_selected_match("Possible Match")

    # Mark both reports as returned.
    def mark_match_returned(self) -> None:
        self.update_selected_match("Returned")

    # Confirm and save a status change for the selected pair.
    def update_selected_match(self, status: str) -> None:
        selection = self.matches_table.selection()
        if not selection or selection[0] not in self.match_results:
            messagebox.showinfo("Select a match", "Please select a match first.", parent=self.root)
            return
        result = self.match_results[selection[0]]
        confirmed = messagebox.askyesno(
            "Update match", f"Mark {result.lost_item.report_id} and {result.found_item.report_id} as {status}?",
            parent=self.root
        )
        if not confirmed:
            return
        try:
            self.system.update_match_status(result.lost_item.report_id, result.found_item.report_id, status)
        except (ValueError, OSError, UnicodeError) as error:
            messagebox.showerror("Match update error", str(error), parent=self.root)
            return
        self.refresh_all_pages()
        self.run_match_search()
        messagebox.showinfo("Updated", f"Both reports marked as {status}.", parent=self.root)

    # Build the report form used for new reports and editing.
    def create_report_page(self) -> None:
        page = self.pages["Report Item"]
        page.rowconfigure(3, weight=1)
        form = ttk.Frame(page, style="Content.TFrame", padding=(0, 12))
        form.grid(row=3, column=0, sticky="nsew")
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        form.rowconfigure(6, weight=1)

        self.form_title = tk.StringVar(value="New report")
        ttk.Label(form, textvariable=self.form_title, style="Content.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        self.report_type = tk.StringVar(value="Lost")
        type_frame = ttk.Frame(form, style="Content.TFrame")
        type_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=8)
        self.type_buttons = []
        for report_type in REPORT_TYPES:
            button = ttk.Radiobutton(
                type_frame, text="Report " + report_type + " Item",
                value=report_type, variable=self.report_type
            )
            button.pack(side="left", padx=(0, 20))
            self.type_buttons.append(button)

        self.form_values = {}
        fields = [
            ("item_name", "Item Name *"), ("category", "Category *"),
            ("colour", "Colour"), ("brand", "Brand"),
            ("location", "Location *"), ("report_date", "Date * (YYYY-MM-DD)"),
            ("contact", "Contact"),
        ]
        for index, field in enumerate(fields):
            name, label = field
            cell = ttk.Frame(form, style="Content.TFrame")
            cell.grid(row=2 + index // 2, column=index % 2, sticky="ew", padx=(0, 12), pady=5)
            cell.columnconfigure(0, weight=1)
            ttk.Label(cell, text=label, style="Content.TLabel").grid(row=0, column=0, sticky="w")
            value = tk.StringVar()
            self.form_values[name] = value
            if name == "category":
                widget = ttk.Combobox(cell, textvariable=value, values=CATEGORIES, state="readonly")
            else:
                widget = ttk.Entry(cell, textvariable=value)
            widget.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        description_frame = ttk.Frame(form, style="Content.TFrame")
        description_frame.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=8)
        description_frame.columnconfigure(0, weight=1)
        description_frame.rowconfigure(1, weight=1)
        ttk.Label(description_frame, text="Description", style="Content.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.description_text = tk.Text(description_frame, height=4, wrap="word", font=("Arial", 11))
        self.description_text.grid(row=1, column=0, sticky="nsew", pady=4)
        scrollbar = ttk.Scrollbar(description_frame, command=self.description_text.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.description_text.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(form, style="Content.TFrame")
        actions.grid(row=7, column=0, columnspan=2, sticky="w")
        self.save_button = ttk.Button(actions, text="Save Report", command=self.save_report)
        self.save_button.pack(side="left", padx=(0, 10))
        self.clear_button = ttk.Button(actions, text="Clear Form", command=self.clear_form)
        self.clear_button.pack(side="left")
        self.clear_form()

    # Reset the form and leave editing mode.
    def clear_form(self) -> None:
        was_editing = self.editing_id is not None
        self.editing_id = None
        self.form_title.set("New report")
        self.report_type.set("Lost")
        for value in self.form_values.values():
            value.set("")
        self.form_values["brand"].set("Unknown")
        self.form_values["report_date"].set(date.today().isoformat())
        self.description_text.delete("1.0", "end")
        for button in self.type_buttons:
            button.configure(state="normal")
        self.save_button.configure(text="Save Report")
        self.clear_button.configure(text="Clear Form")
        if was_editing:
            self.show_records()

    # Validate and save the form through the system layer.
    def save_report(self) -> None:
        values = {}
        for name, variable in self.form_values.items():
            values[name] = variable.get().strip()
        values["description"] = self.description_text.get("1.0", "end-1c").strip()
        missing = []
        for name in ("item_name", "category", "location", "report_date"):
            if not values[name]:
                missing.append(name.replace("_", " "))
        if missing:
            messagebox.showerror("Required fields", "Please enter: " + ", ".join(missing), parent=self.root)
            return

        previous_items = list(self.system.items)
        was_editing = self.editing_id is not None
        try:
            if was_editing:
                item = self.system.edit_item(self.editing_id, **values)
            else:
                item = self.system.add_item(self.report_type.get(), **values)
        except (ValueError, OSError, UnicodeError) as error:
            self.system.items = previous_items
            messagebox.showerror("Save error", str(error), parent=self.root)
            return

        self.clear_form()
        self.refresh_all_pages()
        messagebox.showinfo("Saved", f"Report {item.report_id} saved successfully.", parent=self.root)
        if not was_editing:
            matches = self.system.find_matches(item.report_id)
            if matches:
                messagebox.showinfo(
                    "Possible matches", f"Found {len(matches)} possible match(es) for {item.report_id}.",
                    parent=self.root
                )

    # Build search controls and the records table.
    def create_records_page(self) -> None:
        page = self.pages["Records"]
        page.rowconfigure(3, weight=1)
        body = ttk.Frame(page, style="Content.TFrame", padding=(0, 12))
        body.grid(row=3, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(2, weight=1)

        search = ttk.Frame(body, style="Content.TFrame")
        search.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        search.columnconfigure(1, weight=1)
        ttk.Label(search, text="Search", style="Content.TLabel").grid(row=0, column=0, padx=(0, 8))
        self.search_text = tk.StringVar()
        search_entry = ttk.Entry(search, textvariable=self.search_text)
        search_entry.grid(row=0, column=1, sticky="ew")
        search_entry.bind("<Return>", self.search_on_enter)
        ttk.Button(search, text="Search", command=self.refresh_records).grid(row=0, column=2, padx=8)
        ttk.Button(search, text="Reset", command=self.reset_search).grid(row=0, column=3)

        filters = ttk.Frame(body, style="Content.TFrame")
        filters.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.filter_values = {}
        filter_options = [
            ("report_type", "Type", ("All",) + REPORT_TYPES),
            ("category", "Category", ("All",) + CATEGORIES),
            ("status", "Status", ("All",) + STATUSES),
            ("report_date", "Date (YYYY-MM-DD)", None),
        ]
        for column, option in enumerate(filter_options):
            name, label, options = option
            filters.columnconfigure(column, weight=1)
            cell = ttk.Frame(filters, style="Content.TFrame")
            cell.grid(row=0, column=column, sticky="ew", padx=(0, 8))
            cell.columnconfigure(0, weight=1)
            ttk.Label(cell, text=label, style="Content.TLabel").grid(row=0, column=0, sticky="w")
            value = tk.StringVar(value="All" if options else "")
            self.filter_values[name] = value
            if options:
                widget = ttk.Combobox(cell, textvariable=value, values=options, state="readonly", width=14)
                widget.bind("<<ComboboxSelected>>", self.search_on_enter)
            else:
                widget = ttk.Entry(cell, textvariable=value, width=14)
                widget.bind("<Return>", self.search_on_enter)
            widget.grid(row=1, column=0, sticky="ew", pady=4)

        table_frame = ttk.Frame(body)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        columns = ("report_id", "report_type", "item_name", "category", "colour", "location", "report_date", "status")
        self.records_table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = ("ID", "Type", "Item Name", "Category", "Colour", "Location", "Date", "Status")
        widths = (65, 65, 140, 150, 80, 150, 100, 130)
        for name, heading, width in zip(columns, headings, widths):
            self.records_table.heading(name, text=heading)
            self.records_table.column(name, width=width, minwidth=width, stretch=True)
        self.records_table.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(table_frame, orient="vertical", command=self.records_table.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(table_frame, orient="horizontal", command=self.records_table.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.records_table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.records_table.bind("<<TreeviewSelect>>", self.update_record_buttons)
        self.records_table.bind("<Double-1>", self.open_details_on_double_click)

        self.records_message = tk.StringVar()
        ttk.Label(body, textvariable=self.records_message, style="Content.TLabel").grid(
            row=3, column=0, sticky="w", pady=8
        )
        actions = ttk.Frame(body, style="Content.TFrame")
        actions.grid(row=4, column=0, sticky="w")
        self.record_buttons = []
        for label, handler in [
            ("View Details", self.view_details), ("Edit", self.edit_record),
            ("Update Status", self.open_status_dialog), ("Delete", self.delete_record),
        ]:
            button = ttk.Button(actions, text=label, command=handler, state="disabled")
            button.pack(side="left", padx=(0, 8))
            self.record_buttons.append(button)
        self.refresh_records()

    # Apply search and filter settings to the table.
    def refresh_records(self) -> None:
        filters = {}
        for name, variable in self.filter_values.items():
            value = variable.get().strip()
            filters[name] = "" if value == "All" else value
        try:
            results = self.system.search_items(self.search_text.get(), **filters)
        except ValueError as error:
            messagebox.showerror("Search error", str(error), parent=self.root)
            return
        for row in self.records_table.get_children():
            self.records_table.delete(row)
        for item in results:
            values = (
                item.report_id, item.report_type, item.item_name, item.category,
                item.colour, item.location, item.report_date, item.status,
            )
            self.records_table.insert("", "end", iid=item.report_id, values=values)
        if results:
            self.records_message.set(f"{len(results)} report(s). Double-click to view details.")
        else:
            self.records_message.set("No records found.")
        self.update_record_buttons()
        self.record_count_text.set(f"{len(self.system.items)} reports loaded")

    # Run a search after Enter or a filter selection.
    def search_on_enter(self, event=None) -> None:
        self.refresh_records()

    # Clear all search filters.
    def reset_search(self) -> None:
        self.search_text.set("")
        for name, variable in self.filter_values.items():
            variable.set("" if name == "report_date" else "All")
        self.refresh_records()

    # Enable record actions only when a row is selected.
    def update_record_buttons(self, event=None) -> None:
        state = "normal" if self.records_table.selection() else "disabled"
        for button in self.record_buttons:
            button.configure(state=state)

    # Return the selected report or explain the missing selection.
    def get_selected_record(self):
        selection = self.records_table.selection()
        if not selection:
            messagebox.showinfo("Select a report", "Please select a record first.", parent=self.root)
            return None
        item = self.system.get_item(selection[0])
        if item is None:
            messagebox.showinfo("Report unavailable", "This report no longer exists.", parent=self.root)
            self.refresh_records()
        return item

    # Display every field in a scrollable read-only window.
    def view_details(self) -> None:
        item = self.get_selected_record()
        if item is None:
            return
        window = tk.Toplevel(self.root)
        window.title(f"Report Details - {item.report_id}")
        window.geometry("560x500")
        window.minsize(400, 300)
        window.transient(self.root)
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        text = tk.Text(window, wrap="word", font=("Arial", 11), padx=16, pady=16)
        text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(window, command=text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        text.configure(yscrollcommand=scrollbar.set)
        for name, value in item.to_csv_row().items():
            text.insert("end", name.replace("_", " ").title() + ": " + value + "\n\n")
        text.configure(state="disabled")
        ttk.Button(window, text="Close", command=window.destroy).grid(row=1, column=0, pady=10)

    # Open details only when a table row is double-clicked.
    def open_details_on_double_click(self, event) -> None:
        row = self.records_table.identify_row(event.y)
        if row:
            self.records_table.selection_set(row)
            self.view_details()

    # Fill the report form with the selected record.
    def edit_record(self) -> None:
        item = self.get_selected_record()
        if item is None:
            return
        self.editing_id = item.report_id
        self.form_title.set(f"Editing {item.report_id} | Status: {item.status}")
        self.report_type.set(item.report_type)
        for name, variable in self.form_values.items():
            variable.set(getattr(item, name))
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", item.description)
        for button in self.type_buttons:
            button.configure(state="disabled")
        self.save_button.configure(text="Save Changes")
        self.clear_button.configure(text="Cancel Edit")
        self.show_report_item()

    # Open a small window for choosing a report status.
    def open_status_dialog(self) -> None:
        item = self.get_selected_record()
        if item is None:
            return
        self.status_report_id = item.report_id
        self.status_window = tk.Toplevel(self.root)
        self.status_window.title("Update Status")
        self.status_window.resizable(False, False)
        self.status_window.transient(self.root)
        self.status_window.grab_set()
        ttk.Label(self.status_window, text=f"Status for {item.report_id}").grid(row=0, column=0, padx=20, pady=12)
        self.new_status = tk.StringVar(value=item.status)
        ttk.Combobox(self.status_window, textvariable=self.new_status, values=STATUSES, state="readonly").grid(
            row=1, column=0, padx=20, pady=8
        )
        ttk.Button(self.status_window, text="Save Status", command=self.save_status).grid(row=2, column=0, padx=20, pady=12)

    # Save the selected status and refresh the table.
    def save_status(self) -> None:
        item = self.system.get_item(self.status_report_id)
        if item is None:
            messagebox.showinfo("Report unavailable", "This report no longer exists.", parent=self.status_window)
            self.status_window.destroy()
            return
        old_status = item.status
        try:
            self.system.update_status(item.report_id, self.new_status.get())
        except (ValueError, OSError, UnicodeError) as error:
            item.status = old_status
            messagebox.showerror("Status error", str(error), parent=self.status_window)
            return
        self.status_window.destroy()
        self.refresh_all_pages()
        messagebox.showinfo("Updated", "Report status updated successfully.", parent=self.root)

    # Confirm deletion before removing the selected report.
    def delete_record(self) -> None:
        item = self.get_selected_record()
        if item is None:
            return
        confirmed = messagebox.askyesno("Delete report", f"Delete {item.report_id}: {item.item_name}?", parent=self.root)
        if not confirmed:
            return
        previous_items = list(self.system.items)
        try:
            self.system.delete_item(item.report_id)
        except (ValueError, OSError, UnicodeError) as error:
            self.system.items = previous_items
            messagebox.showerror("Delete error", str(error), parent=self.root)
            return
        if self.editing_id == item.report_id:
            self.clear_form()
        self.refresh_all_pages()
        messagebox.showinfo("Deleted", "Report deleted successfully.", parent=self.root)

    # Keep tables, summaries, and match choices consistent after changes.
    def refresh_all_pages(self) -> None:
        self.refresh_records()
        self.refresh_dashboard()
        self.refresh_statistics()
        self.refresh_match_choices()
        self.clear_match_results()

    # Switch pages and refresh navigation and record counts.
    def show_page(self, page_name: str) -> None:
        self.pages[page_name].tkraise()
        self.current_page = page_name

        for name, button in self.navigation_buttons.items():
            if name == page_name:
                button.configure(style="Selected.TButton")
            else:
                button.configure(style="Nav.TButton")

        self.status_text.set(f"Ready | {page_name}")
        self.record_count_text.set(f"{len(self.system.items)} reports loaded")

    # Open the Dashboard page.
    def show_dashboard(self) -> None:
        self.refresh_dashboard()
        self.show_page("Dashboard")

    # Open the Report Item page.
    def show_report_item(self) -> None:
        self.show_page("Report Item")

    # Open the Records page.
    def show_records(self) -> None:
        self.refresh_records()
        self.show_page("Records")

    # Open the Matches page.
    def show_matches(self) -> None:
        self.refresh_match_choices()
        selection = self.records_table.selection()
        if selection:
            self.match_report_id.set(selection[0])
        self.clear_match_results()
        self.show_page("Matches")

    # Open the Statistics page.
    def show_statistics(self) -> None:
        self.refresh_statistics()
        self.show_page("Statistics")

    # Explain problems found while loading the CSV file.
    def show_load_errors(self) -> None:
        messagebox.showwarning(
            "Data loading warning",
            "Some CSV data could not be loaded.\n" + "\n".join(self.system.load_errors[:10]),
            parent=self.root
        )

    # Ask for confirmation before closing the application.
    def close_application(self) -> None:
        confirmed = messagebox.askyesno(
            "Exit", "Close Campus Lost and Found Matcher?", parent=self.root
        )
        if confirmed:
            self.root.destroy()
