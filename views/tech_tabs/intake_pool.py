import customtkinter as ctk
from tkinter import messagebox

_ROW_H = 46
_HDR_H = 44

class IntakePoolTab(ctk.CTkFrame):
    def __init__(self, master, app, dashboard, on_ticket_accepted):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.dashboard = dashboard
        self.on_ticket_accepted = on_ticket_accepted
        self._init_ui()

    def _init_ui(self):
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

                
        ctk.CTkLabel(self, text="Intake Pool",
                     font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
                     anchor="w",
                     ).grid(row=0, column=0, padx=28, pady=(22, 4), sticky="w")
        ctk.CTkLabel(self, text="Unassigned tickets waiting to be picked up",
                     font=ctk.CTkFont(family="Segoe UI", size=15), text_color="gray",
                     anchor="w",
                     ).grid(row=1, column=0, padx=28, pady=(0, 4), sticky="w")
        ctk.CTkFrame(self, height=2, fg_color=("gray78", "gray30"), corner_radius=1,
                     ).grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 0))

        _hdrs   = ["Ticket ID", "Device", "Issue Summary", "Created", "Action"]
        _widths = [110, 240, 370, 190, 130]

        col_hdr = ctk.CTkFrame(self, fg_color=("gray82", "gray20"),
                               height=_HDR_H, corner_radius=8)
        col_hdr.grid(row=2, column=0, sticky="ew", padx=28, pady=(6, 0))
        col_hdr.grid_propagate(False)
        self.dashboard.table_header_row(col_hdr, _hdrs, _widths)

        self._intake_scroll = ctk.CTkScrollableFrame(self, corner_radius=8)
        self._intake_scroll.grid(row=3, column=0, sticky="nsew", padx=28, pady=(4, 20))
        self._intake_scroll.grid_columnconfigure(0, weight=1)

        self._intake_widths = _widths

    def _refresh_intake(self):
        frame = self._intake_scroll
        for w in frame.winfo_children():
            w.destroy()

        res = self.app.api.get_intake_pool()
        if res["status"] != "success" or not res["data"]:
            self.dashboard.empty_label(frame, "No tickets in the intake pool.")
            return

        widths = self._intake_widths
        for idx, t in enumerate(res["data"]):
            bg  = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")
            row = ctk.CTkFrame(frame, fg_color=bg, corner_radius=6, height=_ROW_H)
            row.grid(row=idx, column=0, sticky="ew", pady=2)
            row.grid_propagate(False)

            for i, (val, w) in enumerate(
                zip([t["id"], t["device"], t["issue"], t["created"]], widths[:4])
            ):
                ctk.CTkLabel(
                    row, text=str(val),
                    font=ctk.CTkFont(family="Segoe UI", size=14), width=w, anchor="w",
                ).grid(row=0, column=i, padx=(14 if i == 0 else 6, 6), sticky="w")

            ctk.CTkButton(
                row, text="Accept", width=110, height=34,
                font=ctk.CTkFont(family="Segoe UI", size=14),
                fg_color="#3498db", hover_color="#2980b9",
                corner_radius=8,
                command=lambda ticket=t: self._do_accept(ticket),
            ).grid(row=0, column=4, padx=8)

    def _do_accept(self, ticket: dict):
        confirm = messagebox.askyesno(
            "Accept Ticket",
            f"Accept {ticket['id']} \u2014 {ticket['device']}?\n\nIssue: {ticket['issue']}",
        )
        if not confirm:
            return
        result = self.app.api.accept_ticket(
            tech_id=self.app.session.get("id"),
            ticket_raw_id=ticket["raw_id"],
        )
        if result["status"] == "success":
            self.on_ticket_accepted()
        else:
            messagebox.showerror("Error", result.get("message", "Failed to accept ticket."))
