import customtkinter as ctk
from typing import TYPE_CHECKING
from views.helpdesk_tabs.all_tickets_tab import _HDR_H, _TICKET_ROW_H

if TYPE_CHECKING:
    from main import RepairERP

class CustomerPickupTab(ctk.CTkFrame):
    def __init__(self, parent, app: "RepairERP", dashboard):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.dashboard = dashboard
        self._build()

    def _build(self):
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Notify Customers / Pickup",
                     font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
                     anchor="w",
                     ).grid(row=0, column=0, padx=28, pady=(22, 4), sticky="w")
        ctk.CTkLabel(
            self, text="Completed tickets that are pending customer notification",
            font=ctk.CTkFont(family="Segoe UI", size=15), text_color="gray",
            anchor="w",
        ).grid(row=1, column=0, padx=28, pady=(0, 4), sticky="w")
        ctk.CTkFrame(self, height=2, fg_color=("gray78", "gray30"), corner_radius=1,
                     ).grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 10))

        _notify_hdrs   = ["Ticket ID", "Customer", "Phone", "Device", "Action"]
        _notify_widths = [110, 210, 148, 228, 170]

        col_hdr = ctk.CTkFrame(self, fg_color=("gray82", "gray20"),
                               height=_HDR_H, corner_radius=8)
        col_hdr.grid(row=2, column=0, sticky="ew", padx=28, pady=(6, 0))
        col_hdr.grid_propagate(False)
        self.dashboard.table_header_row(col_hdr, _notify_hdrs, _notify_widths)

        self._notify_scroll = ctk.CTkScrollableFrame(self, corner_radius=8)
        self._notify_scroll.grid(row=3, column=0, sticky="nsew", padx=28, pady=(4, 20))
        self._notify_scroll.grid_columnconfigure(0, weight=1)

        self._notify_hdrs   = _notify_hdrs
        self._notify_widths = _notify_widths

    def refresh(self):
        frame = self._notify_scroll
        for w in frame.winfo_children():
            w.destroy()

        res = self.app.api.get_tickets()
        if res["status"] != "success":
            return

        pending = [t for t in res["data"]
                   if t["status"] == "Completed" and not t["notified"]]

        if not pending:
            self.dashboard.empty_label(frame, "✓  All customers have been notified.")
            return

        for idx, t in enumerate(pending):
            bg  = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")
            row = ctk.CTkFrame(frame, fg_color=bg, corner_radius=6, height=_TICKET_ROW_H)
            row.grid(row=idx, column=0, sticky="ew", pady=2)
            row.grid_propagate(False)

            for i, (val, w) in enumerate(
                zip([t["id"], t["customer"], t["phone"], t["device"]],
                    self._notify_widths[:4])
            ):
                ctk.CTkLabel(
                    row, text=str(val),
                    font=ctk.CTkFont(family="Segoe UI", size=14), width=w, anchor="w",
                ).grid(row=0, column=i, padx=(14 if i == 0 else 6, 6), sticky="w")

            ctk.CTkButton(
                row, text="✔  Mark Notified", width=155, height=34,
                font=ctk.CTkFont(family="Segoe UI", size=14),
                fg_color="#27ae60", hover_color="#1e8449",
                corner_radius=8,
                command=lambda raw_id=t["raw_id"]: self._do_notify(raw_id),
            ).grid(row=0, column=4, padx=8)

    def _do_notify(self, ticket_raw_id: int):
        result = self.app.api.notify_customer(
            user_id=self.app.session.get("id"),
            ticket_id=ticket_raw_id,
        )
        if result["status"] == "success":
            self.refresh()
            self.dashboard._all_ticket_cache = []
            if hasattr(self.dashboard, "all_tickets_tab"):
                self.dashboard.all_tickets_tab.refresh()
