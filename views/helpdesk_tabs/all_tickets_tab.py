import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import RepairERP

STATUS_COLORS: dict[str, str] = {
    "Intake":      "#3498db",
    "In-Progress": "#e67e22",
    "Completed":   "#27ae60",
}

def _sc(status: str) -> str:
    return STATUS_COLORS.get(status, "#888")

_TICKET_HEADERS = ["Ticket ID", "Customer", "Phone", "Device", "Status", "Technician"]
_TICKET_WIDTHS  = [110, 200, 170, 250, 110, 110]
_TICKET_ROW_H   = 46
_HDR_H          = 44

class AllTicketsTab(ctk.CTkFrame):
    def __init__(self, parent, app: "RepairERP", dashboard):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.dashboard = dashboard
        self._build()

    def _build(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(self, fg_color="transparent", height=68)
        hdr.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 0))
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr, text="All Repair Tickets",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

      

        ctk.CTkFrame(self, height=2, fg_color=("gray78", "gray30"), corner_radius=1,
                     ).grid(row=1, column=0, sticky="ew", padx=24, pady=(8, 0))

        col_hdr = ctk.CTkFrame(self, fg_color=("gray82", "gray20"),
                               height=_HDR_H, corner_radius=8)
        col_hdr.grid(row=1, column=0, sticky="ew", padx=24, pady=(4, 0))
        col_hdr.grid_propagate(False)
        self.dashboard.table_header_row(col_hdr, _TICKET_HEADERS, _TICKET_WIDTHS)

        self._all_tickets_scroll = ctk.CTkScrollableFrame(self, corner_radius=8)
        self._all_tickets_scroll.grid(row=2, column=0, sticky="nsew", padx=24, pady=(4, 20))
        self._all_tickets_scroll.grid_columnconfigure(0, weight=1)

    def refresh(self):
        frame = self._all_tickets_scroll
        for w in frame.winfo_children():
            w.destroy()

        result = self.app.api.get_tickets()
        if result["status"] != "success":
            self.dashboard.empty_label(frame, "Failed to load tickets.")
            return

        tickets = result["data"]
                                
        self.dashboard._all_ticket_cache = tickets

        if not tickets:
            self.dashboard.empty_label(frame, "No tickets found.")
            return

        for idx, t in enumerate(tickets):
            bg  = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")
            row = ctk.CTkFrame(frame, fg_color=bg, corner_radius=6, height=_TICKET_ROW_H)
            row.grid(row=idx, column=0, sticky="ew", pady=2)
            row.grid_propagate(False)
            vals = [t["id"], t["customer"], t["phone"], t["device"], t["status"], t["tech"]]
            for i, (val, w) in enumerate(zip(vals, _TICKET_WIDTHS)):
                lbl = ctk.CTkLabel(
                    row, text=str(val),
                    font=ctk.CTkFont(family="Segoe UI", size=14),
                    width=w, anchor="w",
                )
                if i == 4:
                    lbl.configure(text_color=_sc(val))
                lbl.grid(row=0, column=i, padx=(14 if i == 0 else 6, 6), sticky="w")
