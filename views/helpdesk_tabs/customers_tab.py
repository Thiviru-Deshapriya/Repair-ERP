import customtkinter as ctk
from typing import TYPE_CHECKING
from views.helpdesk_tabs.all_tickets_tab import _sc

if TYPE_CHECKING:
    from main import RepairERP

class CustomersTab(ctk.CTkFrame):
    def __init__(self, parent, app: "RepairERP", dashboard):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.dashboard = dashboard
        self._build()

    def _build(self):
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Customer Search",
                     font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
                     anchor="w",
                     ).grid(row=0, column=0, padx=28, pady=(22, 4), sticky="w")
        ctk.CTkFrame(self, height=2, fg_color=("gray78", "gray30"), corner_radius=1,
                     ).grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 12))

        srow = ctk.CTkFrame(self, fg_color="transparent")
        srow.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 8))
        srow.grid_columnconfigure(0, weight=1)

        self._cust_search = ctk.CTkEntry(
            srow, placeholder_text="Search by name, phone, or email…",
            height=48, font=ctk.CTkFont(family="Segoe UI", size=15),
            corner_radius=10,
        )
        self._cust_search.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self._cust_search.bind("<KeyRelease>", lambda e: self._filter_customers())

        ctk.CTkButton(
            srow, text="Search", width=110, height=48,
            font=ctk.CTkFont(family="Segoe UI", size=15),
            corner_radius=10, command=self._filter_customers,
        ).grid(row=0, column=1)

        self._cust_scroll = ctk.CTkScrollableFrame(self, corner_radius=8)
        self._cust_scroll.grid(row=3, column=0, sticky="nsew", padx=28, pady=(0, 20))
        self._cust_scroll.grid_columnconfigure(0, weight=1)

    def refresh(self):
        res = self.app.api.get_customers()
        self.dashboard._customer_cache = res["data"] if res["status"] == "success" else []
        self._filter_customers()

    def reset_state(self):
        self._cust_search.delete(0, "end")

    def _filter_customers(self):
        term = self._cust_search.get().strip().lower()
        filtered = [
            c for c in self.dashboard._customer_cache
            if not term or any(
                term in str(v).lower()
                for v in [c["name"], c["phone"], c.get("email", "")]
            )
        ]
        self._render_customers(filtered)

    def _render_customers(self, customers: list[dict]):
        frame = self._cust_scroll
        for w in frame.winfo_children():
            w.destroy()

        if not customers:
            self.dashboard.empty_label(frame, "No customers found.")
            return

        for idx, c in enumerate(customers):
            card = ctk.CTkFrame(frame, corner_radius=10, border_width=1)
            card.grid(row=idx, column=0, sticky="ew", pady=5, padx=2)
            card.grid_columnconfigure(0, weight=1)

            chdr = ctk.CTkFrame(card, fg_color=("gray85", "gray22"),
                                corner_radius=6, height=48)
            chdr.grid(row=0, column=0, sticky="ew")
            chdr.grid_propagate(False)
            chdr.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                chdr, text=c["name"],
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                anchor="w",
            ).grid(row=0, column=0, padx=16, sticky="w")
            ctk.CTkLabel(
                chdr, text=f"{c['phone']}  |  {c.get('email', 'No email')}",
                font=ctk.CTkFont(family="Segoe UI", size=14), text_color="gray",
                anchor="e",
            ).grid(row=0, column=1, padx=16, sticky="e")

            if c["tickets"]:
                for ti, t in enumerate(c["tickets"]):
                    tr = ctk.CTkFrame(card, fg_color="transparent", height=36)
                    tr.grid(row=ti + 1, column=0, sticky="ew", padx=10, pady=2)
                    tr.grid_propagate(False)
                    tr.grid_columnconfigure(4, weight=1)
                    for col_i, (val, w) in enumerate(
                        zip([t["id"], t["device"], t["status"], t["created"]],
                            [95, 200, 130, 130])
                    ):
                        lbl = ctk.CTkLabel(tr, text=str(val),
                                           font=ctk.CTkFont(family="Segoe UI", size=14),
                                           width=w, anchor="w")
                        if col_i == 2:
                            lbl.configure(text_color=_sc(val))
                        lbl.grid(row=0, column=col_i, padx=5)
                    ctk.CTkLabel(
                        tr, text=t.get("issue", ""),
                        font=ctk.CTkFont(family="Segoe UI", size=14),
                        text_color="gray", anchor="w",
                    ).grid(row=0, column=4, padx=5, sticky="ew")
            else:
                ctk.CTkLabel(
                    card, text="No tickets yet.",
                    font=ctk.CTkFont(family="Segoe UI", size=14), text_color="gray",
                ).grid(row=1, column=0, padx=16, pady=8, sticky="w")
