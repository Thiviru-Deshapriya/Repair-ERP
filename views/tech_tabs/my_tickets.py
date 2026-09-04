import customtkinter as ctk

_ROW_H = 46
_HDR_H = 44

STATUS_COLORS: dict[str, str] = {
    "Intake":      "#3498db",
    "In-Progress": "#e67e22",
    "Completed":   "#27ae60",
}

class MyTicketsTab(ctk.CTkFrame):
    def __init__(self, master, app, dashboard, on_manage_parts):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.dashboard = dashboard
        self.on_manage_parts = on_manage_parts
        self._init_ui()

    def _init_ui(self):
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="My Tickets",
                     font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
                     anchor="w",
                     ).grid(row=0, column=0, padx=28, pady=(22, 4), sticky="w")
        ctk.CTkLabel(self, text="Tickets currently assigned to you",
                     font=ctk.CTkFont(family="Segoe UI", size=15), text_color="gray",
                     anchor="w",
                     ).grid(row=1, column=0, padx=28, pady=(0, 4), sticky="w")
        ctk.CTkFrame(self, height=2, fg_color=("gray78", "gray30"), corner_radius=1,
                     ).grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 0))

        _hdrs   = ["Ticket ID", "Device", "Issue Summary", "Status", "Created", "Action"]
        _widths = [110, 235, 330, 140, 175, 160]

        col_hdr = ctk.CTkFrame(self, fg_color=("gray82", "gray20"),
                               height=_HDR_H, corner_radius=8)
        col_hdr.grid(row=2, column=0, sticky="ew", padx=28, pady=(6, 0))
        col_hdr.grid_propagate(False)
        self.dashboard.table_header_row(col_hdr, _hdrs, _widths)

        self._mt_scroll = ctk.CTkScrollableFrame(self, corner_radius=8)
        self._mt_scroll.grid(row=3, column=0, sticky="nsew", padx=28, pady=(4, 20))
        self._mt_scroll.grid_columnconfigure(0, weight=1)

        self._mt_widths = _widths

    def _refresh_my_tickets(self):
        frame = self._mt_scroll
        for w in frame.winfo_children():
            w.destroy()

        tech_id = self.app.session.get("id")
        if not tech_id:
            return

        res = self.app.api.get_my_tickets(tech_id)
        if res["status"] != "success" or not res["data"]:
            self.dashboard.empty_label(frame, "No tickets assigned to you yet.")
            return

        widths = self._mt_widths
        for idx, t in enumerate(res["data"]):
            bg  = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")
            row = ctk.CTkFrame(frame, fg_color=bg, corner_radius=6, height=_ROW_H)
            row.grid(row=idx, column=0, sticky="ew", pady=2)
            row.grid_propagate(False)

            for i, (val, w) in enumerate(
                zip([t["id"], t["device"], t["issue"], t["status"], t["created"]], widths[:5])
            ):
                lbl = ctk.CTkLabel(
                    row, text=str(val),
                    font=ctk.CTkFont(family="Segoe UI", size=14), width=w, anchor="w")
                if i == 3:
                    lbl.configure(text_color=STATUS_COLORS.get(val, "#888"))
                lbl.grid(row=0, column=i, padx=(14 if i == 0 else 6, 6), sticky="w")

            if t["status"] != "Completed":
                ctk.CTkButton(
                    row, text="\u2699  Manage Parts", width=148, height=34,
                    font=ctk.CTkFont(family="Segoe UI", size=14),
                    fg_color="#e67e22", hover_color="#d35400",
                    corner_radius=8,
                    command=lambda ticket=t: self.on_manage_parts(ticket),
                ).grid(row=0, column=5, padx=8,pady=6)
