import re
import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import RepairERP

class CreateTicketTab(ctk.CTkFrame):
    def __init__(self, parent, app: "RepairERP", dashboard):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.dashboard = dashboard
        self._build()

    def _build(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="Create New Repair Ticket",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, padx=28, pady=(10, 2), sticky="w")
        ctk.CTkFrame(self, height=2, fg_color=("gray78", "gray30"), corner_radius=1,
                     ).grid(row=1, column=0, columnspan=2, sticky="ew", padx=28, pady=(0, 6))

        card = ctk.CTkFrame(self, corner_radius=14, border_width=1)
        card.grid(row=2, column=0, columnspan=2, padx=28, pady=(0, 8), sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)
        
        for _r in (0, 2, 4, 6, 8, 10, 11):
            card.grid_rowconfigure(_r, weight=1)
        for _r in (1, 3, 5, 7):
            card.grid_rowconfigure(_r, weight=2)
        card.grid_rowconfigure(9, weight=3)

        fields_left  = [("Phone Number *", "phone"), ("Device Brand *", "brand"),
                        ("IMEI / Serial *", "imei")]
        fields_right = [("Customer Name *", "name"), ("Device Model *", "model"),
                        ("Advance Deposit (Rs.)", "deposit")]
        self._ct_entries: dict[str, ctk.CTkEntry] = {}

        for i, (label, key) in enumerate(fields_left):
            rr = i * 2
            ctk.CTkLabel(card, text=label,
                         font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                         anchor="w",
                         ).grid(row=rr, column=0, padx=(24, 12), pady=(8, 0), sticky="w")
            e = ctk.CTkEntry(card, height=50, corner_radius=10,
                             font=ctk.CTkFont(family="Segoe UI", size=16))
            e.grid(row=rr + 1, column=0, padx=(24, 12), pady=(4, 0), sticky="ew")
            self._ct_entries[key] = e

        for i, (label, key) in enumerate(fields_right):
            rr = i * 2
            ctk.CTkLabel(card, text=label,
                         font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                         anchor="w",
                         ).grid(row=rr, column=1, padx=(12, 24), pady=(8, 0), sticky="w")
            e = ctk.CTkEntry(card, height=50, corner_radius=10,
                             font=ctk.CTkFont(family="Segoe UI", size=16))
            e.grid(row=rr + 1, column=1, padx=(12, 24), pady=(4, 0), sticky="ew")
            self._ct_entries[key] = e

        ctk.CTkLabel(card, text="Email",
                     font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                     anchor="w",
                     ).grid(row=6, column=0, columnspan=2, padx=24, pady=(8, 0), sticky="w")
        self._ct_entries["email"] = ctk.CTkEntry(
            card, height=50, corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=16))
        self._ct_entries["email"].grid(row=7, column=0, columnspan=2,
                                       padx=24, pady=(4, 0), sticky="ew")

        ctk.CTkLabel(card, text="Issue Description *",
                     font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                     anchor="w",
                     ).grid(row=8, column=0, columnspan=2, padx=24, pady=(8, 0), sticky="w")
        self._ct_issue = ctk.CTkTextbox(
            card, height=90, corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=16))
        self._ct_issue.grid(row=9, column=0, columnspan=2,
                            padx=24, pady=(4, 0), sticky="ew")

        ctk.CTkButton(
            card, text="Create Ticket", height=54,
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            corner_radius=10, command=self._do_create_ticket,
        ).grid(row=10, column=0, columnspan=2, padx=24, pady=(10, 6), sticky="ew")

        self._ct_status = ctk.CTkLabel(
            card, text="", font=ctk.CTkFont(family="Segoe UI", size=15))
        self._ct_status.grid(row=11, column=0, columnspan=2,
                             padx=24, pady=(0, 8), sticky="w")

    def reset_state(self):
        for e in self._ct_entries.values():
            e.delete(0, "end")
        self._ct_issue.delete("1.0", "end")
        self._ct_status.configure(text="")

    def _do_create_ticket(self):
        vals  = {k: e.get().strip() for k, e in self._ct_entries.items()}
        issue = self._ct_issue.get("1.0", "end").strip()

                                                                            
        if not all(vals.get(k) for k in ["phone", "name", "brand", "model", "imei"]) or not issue:
            self._ct_status.configure(
                text="Please fill all required (*) fields.", text_color="#e05c5c")
            return

                                                                           
        if not re.fullmatch(r"\d{10}", vals["phone"]):
            self._ct_status.configure(
                text="Phone: must be exactly 10 digits (e.g. 9876543210).",
                text_color="#e05c5c")
            return

                                                                            
        email = vals.get("email", "")
        if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            self._ct_status.configure(
                text="Email: must be a valid address (e.g. user@example.com).",
                text_color="#e05c5c")
            return

                                                                            
        raw_deposit = vals.get("deposit", "")
        if raw_deposit:
            try:
                if float(raw_deposit) < 0:
                    raise ValueError
            except ValueError:
                self._ct_status.configure(
                    text="Advance Deposit must be a valid non-negative number (e.g. 500).",
                    text_color="#e05c5c")
                return

        result = self.app.api.create_ticket(
            user_id=self.app.session.get("id"),
            phone=vals["phone"], name=vals["name"], email=vals.get("email", ""),
            brand=vals["brand"], model=vals["model"], imei=vals["imei"],
            issue=issue, deposit=vals.get("deposit") or "0",
        )
        if result["status"] == "success":
            self._ct_status.configure(
                text=f"✓  Ticket {result['ticket_id']} created successfully!",
                text_color="#27ae60")
            for e in self._ct_entries.values():
                e.delete(0, "end")
            self._ct_issue.delete("1.0", "end")
            
            self.dashboard._all_ticket_cache = []
            if hasattr(self.dashboard, "all_tickets_tab"):
                self.dashboard.all_tickets_tab.refresh()
            if hasattr(self.dashboard, "search_tickets_tab"):
                self.dashboard.search_tickets_tab.refresh()
        else:
            self._ct_status.configure(
                text=result.get("message", "Failed to create ticket."),
                text_color="#e05c5c")
