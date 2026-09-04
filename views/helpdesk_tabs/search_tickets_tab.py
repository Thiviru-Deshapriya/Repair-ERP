import customtkinter as ctk
from typing import TYPE_CHECKING
from views.helpdesk_tabs.all_tickets_tab import _TICKET_HEADERS, _TICKET_WIDTHS, _TICKET_ROW_H, _HDR_H, _sc

if TYPE_CHECKING:
    from main import RepairERP

class SearchTicketsTab(ctk.CTkFrame):
    def __init__(self, parent, app: "RepairERP", dashboard):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.dashboard = dashboard
        self._build()

    def _build(self):
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Search Tickets",
                     font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
                     anchor="w",
                     ).grid(row=0, column=0, padx=28, pady=(22, 4), sticky="w")
        ctk.CTkFrame(self, height=2, fg_color=("gray78", "gray30"), corner_radius=1,
                     ).grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 12))

        srow = ctk.CTkFrame(self, fg_color="transparent")
        srow.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 8))
        srow.grid_columnconfigure(0, weight=1)

        self._st_search = ctk.CTkEntry(
            srow,
            placeholder_text="Filter by ticket ID, customer, phone, device, status or technician…",
            height=48, font=ctk.CTkFont(family="Segoe UI", size=15),
            corner_radius=10,
        )
        self._st_search.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self._st_search.bind("<KeyRelease>", lambda e: self._filter_search_tickets())

        ctk.CTkButton(
            srow, text="Search", width=110, height=48,
            font=ctk.CTkFont(family="Segoe UI", size=15),
            corner_radius=10, command=self._filter_search_tickets,
        ).grid(row=0, column=1)

        self._st_scroll = ctk.CTkScrollableFrame(self, corner_radius=8)
        self._st_scroll.grid(row=3, column=0, sticky="nsew", padx=28, pady=(0, 20))
        self._st_scroll.grid_columnconfigure(0, weight=1)

    def refresh(self):
        res = self.app.api.get_tickets()
        if res["status"] == "success":
            self.dashboard._all_ticket_cache = res["data"]
        self._st_search.delete(0, "end")
        self._render_search_results(self.dashboard._all_ticket_cache)

    def reset_state(self):
        self._st_search.delete(0, "end")

    def _filter_search_tickets(self):
        if not self.dashboard._all_ticket_cache:
            res = self.app.api.get_tickets()
            if res["status"] == "success":
                self.dashboard._all_ticket_cache = res["data"]
        term = self._st_search.get().strip().lower()
        filtered = [
            t for t in self.dashboard._all_ticket_cache
            if not term or any(
                term in str(v).lower()
                for v in [t["id"], t["customer"], t["phone"],
                          t["device"], t["status"], t["tech"]]
            )
        ]
        self._render_search_results(filtered)

    def _render_search_results(self, tickets: list[dict]):
        frame = self._st_scroll
        for w in frame.winfo_children():
            w.destroy()

        if not tickets:
            self.dashboard.empty_label(frame, "No matching tickets.")
            return

        extended_headers = _TICKET_HEADERS + ["Created"]
        extended_widths  = _TICKET_WIDTHS  + [145]

        hdr_row = ctk.CTkFrame(frame, fg_color=("gray82", "gray20"),
                               height=_HDR_H, corner_radius=6)
        hdr_row.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        hdr_row.grid_propagate(False)
        self.dashboard.table_header_row(hdr_row, extended_headers, extended_widths)

        for idx, t in enumerate(tickets):
            bg  = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")
            row = ctk.CTkFrame(frame, fg_color=bg, corner_radius=6, height=_TICKET_ROW_H)
            row.grid(row=idx + 1, column=0, sticky="ew", pady=2)
            row.grid_propagate(False)
            vals = [t["id"], t["customer"], t["phone"],
                    t["device"], t["status"], t["tech"], t["created"]]
            for i, (val, w) in enumerate(zip(vals, extended_widths)):
                lbl = ctk.CTkLabel(
                    row, text=str(val),
                    font=ctk.CTkFont(family="Segoe UI", size=14),
                    width=w, anchor="w")
                if i == 4:
                    lbl.configure(text_color=_sc(val))
                lbl.grid(row=0, column=i, padx=(14 if i == 0 else 6, 6), sticky="w")
