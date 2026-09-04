from __future__ import annotations
import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import RepairERP
    from views.admin_view import AdminView

_STATUS_COLORS: dict[str, str] = {
    "Intake":      "#3498db",
    "In-Progress": "#e67e22",
    "Completed":   "#27ae60",
    "Cancelled":   "#c0392b",
}
_PART_STATUS_COLORS = {
    "Draft": "#3498db", "Installed": "#e67e22", "Confirmed": "#27ae60"
}
_TICKET_HEADERS = ["Ticket ID", "Customer", "Phone", "Device", "Status", "Technician", "Created"]
_TICKET_WIDTHS  = [100, 180, 130, 210, 120, 150, 155]
_ROW_H          = 46
_HDR_H          = 44

class TicketsTab(ctk.CTkFrame):
    def __init__(self, parent, app: "RepairERP", admin_view: "AdminView"):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.admin_view = admin_view

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

                                                                        
        ctk.CTkLabel(
            self, text="All Tickets",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=28, pady=(22, 2), sticky="w")

        ctk.CTkLabel(
            self, text="System-wide repair tickets - click any row for full details",
            font=ctk.CTkFont(family="Segoe UI", size=14), text_color="gray",
            anchor="w",
        ).grid(row=1, column=0, padx=28, pady=(0, 8), sticky="w")

                                                                        
        search_row = ctk.CTkFrame(self, fg_color="transparent")
        search_row.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 6))
        search_row.grid_columnconfigure(0, weight=1)

        self._at_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="🔍  Search by ticket ID, customer, phone, device, status, technician…",
            textvariable=self._at_search_var,
            height=44,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=10,
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_all_tickets())

        ctk.CTkButton(
            search_row, text="⟳  Refresh", width=110, height=44,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=10,
            command=self.refresh_all_tickets,
        ).grid(row=0, column=1)

                                                                        
        col_hdr = ctk.CTkFrame(
            self, fg_color=("gray82", "gray20"), height=_HDR_H, corner_radius=8
        )
        col_hdr.grid(row=3, column=0, sticky="ew", padx=28, pady=(0, 2))
        col_hdr.grid_propagate(False)
        self.admin_view.table_header_row(col_hdr, _TICKET_HEADERS, _TICKET_WIDTHS)

                                                                         
        self._at_scroll = ctk.CTkScrollableFrame(self, corner_radius=8)
        self._at_scroll.grid(row=4, column=0, sticky="nsew", padx=28, pady=(0, 20))
        self._at_scroll.grid_columnconfigure(0, weight=1)

                      
        self.refresh_all_tickets()

    def refresh_all_tickets(self):
        frame = self._at_scroll
        for w in frame.winfo_children():
            w.destroy()

        term = self._at_search_var.get().strip()
        res  = self.app.api.get_all_tickets_admin(search_term=term)

        if res["status"] != "success":
            self.admin_view.empty_label(frame, f"Error loading tickets: {res.get('message')}")
            return

        tickets = res["data"]
        if not tickets:
            self.admin_view.empty_label(frame, "No tickets found." if not term else f"No results for \"{term}\".")
            return

        for idx, t in enumerate(tickets):
            bg = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")
            row = ctk.CTkFrame(frame, fg_color=bg, corner_radius=6, height=_ROW_H)
            row.grid(row=idx, column=0, sticky="ew", pady=2)
            row.grid_propagate(False)

                        
            cell_values = [
                t["id"], t["customer"], t["phone"],
                t["device"], t["status"], t["tech"], t["created"][:10],
            ]
            for i, (val, w) in enumerate(zip(cell_values, _TICKET_WIDTHS)):
                lbl = ctk.CTkLabel(
                    row, text=str(val),
                    font=ctk.CTkFont(family="Segoe UI", size=14),
                    width=w, anchor="w",
                )
                if i == 4:                 
                    lbl.configure(text_color=_STATUS_COLORS.get(val, "#888"))
                lbl.grid(row=0, column=i, padx=(14 if i == 0 else 6, 6), sticky="w")

                                                                            
            for widget in [row] + list(row.winfo_children()):
                widget.bind("<Button-1>", lambda e, ticket=t: self._show_ticket_detail(ticket))
                widget.configure(cursor="hand2")

    def _show_ticket_detail(self, ticket: dict):
        res = self.app.api.get_ticket_detail(ticket["raw_id"])
        if res["status"] != "success":
            messagebox.showerror("Error", res.get("message", "Could not load ticket details."))
            return
        d = res["data"]

        popup = ctk.CTkToplevel(self)
        popup.title(f"Ticket Detail - {d['id']}")
        popup.geometry("860x720")
        popup.minsize(760, 600)
        popup.grab_set()
        popup.lift()
        popup.focus_force()

        popup.grid_rowconfigure(1, weight=1)
        popup.grid_columnconfigure(0, weight=1)

        status_color = _STATUS_COLORS.get(d["status"], "#555")
        banner = ctk.CTkFrame(popup, fg_color=status_color, corner_radius=0, height=62)
        banner.grid(row=0, column=0, sticky="ew")
        banner.grid_propagate(False)
        banner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            banner,
            text=f"🎫  {d['id']}   ·   {d['device_brand']} {d['device_model']}   ·   {d['status']}",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="white", anchor="w",
        ).grid(row=0, column=0, padx=22, sticky="w")

        ctk.CTkLabel(
            banner,
            text=f"Tech: {d['tech_username']}",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="white", anchor="e",
        ).grid(row=0, column=1, padx=22, sticky="e")

                                                                        
        if d["status"] == "In-Progress":
            ctk.CTkButton(
                banner,
                text="🚫  Cancel Ticket",
                width=160, height=36,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                corner_radius=8,
                fg_color="#7f1d1d",
                hover_color="#991b1b",
                text_color="white",
                command=lambda: self._confirm_cancel_ticket(d, popup),
            ).grid(row=0, column=2, padx=(8, 18), sticky="e")

        body = ctk.CTkScrollableFrame(popup, corner_radius=0, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        body.grid_columnconfigure(0, weight=1)

        row_ptr = [0]                       

        def section_title(text: str):
            ctk.CTkLabel(
                body, text=text,
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                anchor="w",
            ).grid(row=row_ptr[0], column=0, padx=22, pady=(18, 4), sticky="w")
            ctk.CTkFrame(body, height=1, fg_color=("gray75", "gray35"), corner_radius=0,
                         ).grid(row=row_ptr[0] + 1, column=0, sticky="ew", padx=22)
            row_ptr[0] += 2

        def info_grid(pairs: list[tuple[str, str]]):
            card = ctk.CTkFrame(body, corner_radius=10, border_width=1)
            card.grid(row=row_ptr[0], column=0, sticky="ew", padx=22, pady=(6, 0))
            card.grid_columnconfigure((0, 1, 2, 3), weight=1)
            for i, (k, v) in enumerate(pairs):
                col_k = (i % 2) * 2
                col_v = col_k + 1
                row_i = i // 2
                ctk.CTkLabel(
                    card, text=k + ":",
                    font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                    text_color=("gray40", "gray60"), anchor="w",
                ).grid(row=row_i, column=col_k, padx=(16, 4), pady=8, sticky="w")
                ctk.CTkLabel(
                    card, text=str(v),
                    font=ctk.CTkFont(family="Segoe UI", size=13),
                    anchor="w", wraplength=280,
                ).grid(row=row_i, column=col_v, padx=(0, 16), pady=8, sticky="w")
            row_ptr[0] += 1

        section_title("👤  Customer & Device")
        info_grid([
            ("Customer",     d["customer_name"]),
            ("Phone",        d["customer_phone"]),
            ("Email",        d["customer_email"]),
            ("Device",       f"{d['device_brand']} {d['device_model']}"),
            ("IMEI / Serial", d["imei"]),
        ])

        section_title("📋  Ticket Details")
        info_grid([
            ("Ticket ID",    d["id"]),
            ("Status",       d["status"]),
            ("Created",      d["created"]),
            ("Completed",    d["completed"]),
            ("Technician",   d["tech_username"]),
            ("Customer Notified", "✓ Yes" if d["notified"] else "✗ No"),
            ("Notified At",  d["notified_at"]),
        ])

        section_title("🔧  Issue Description")
        issue_card = ctk.CTkFrame(body, corner_radius=10, border_width=1)
        issue_card.grid(row=row_ptr[0], column=0, sticky="ew", padx=22, pady=(6, 0))
        issue_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            issue_card, text=d["issue"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            anchor="w", wraplength=770, justify="left",
        ).grid(row=0, column=0, padx=16, pady=12, sticky="w")
        row_ptr[0] += 1

        section_title("💰  Financials")
        info_grid([
            ("Advance Deposit", f"Rs. {d['deposit']:.2f}"),
            ("Service Charge",  f"Rs. {d['charge']:.2f}"),
            ("Net Profit",      f"Rs. {d['profit']:.2f}"),
        ])

        section_title("📦  Parts Allocated")
        if not d["parts"]:
            no_parts = ctk.CTkFrame(body, corner_radius=10, border_width=1)
            no_parts.grid(row=row_ptr[0], column=0, sticky="ew", padx=22, pady=(6, 0))
            ctk.CTkLabel(
                no_parts, text="No parts allocated to this ticket.",
                font=ctk.CTkFont(family="Segoe UI", size=13), text_color="gray",
            ).grid(row=0, column=0, padx=16, pady=12)
            row_ptr[0] += 1
        else:
            parts_card = ctk.CTkFrame(body, corner_radius=10, border_width=1)
            parts_card.grid(row=row_ptr[0], column=0, sticky="ew", padx=22, pady=(6, 0))
            parts_card.grid_columnconfigure(0, weight=1)

            ph = ctk.CTkFrame(parts_card, fg_color=("gray82", "gray22"),
                              height=34, corner_radius=0)
            ph.grid(row=0, column=0, sticky="ew")
            ph.grid_propagate(False)
            _ph = ["Part Name", "Source", "Cost", "Status"]
            _pw = [240, 220, 100, 120]
            self.admin_view.table_header_row(ph, _ph, _pw)

            for pi, p in enumerate(d["parts"]):
                bg = ("gray93", "gray19") if pi % 2 == 0 else ("gray88", "gray23")
                pr = ctk.CTkFrame(parts_card, fg_color=bg, corner_radius=0, height=36)
                pr.grid(row=pi + 1, column=0, sticky="ew")
                pr.grid_propagate(False)
                pvals = [p["name"], p["source"], f"Rs.{p['cost']:.0f}", p["status"]]
                for ci, (pv, pw) in enumerate(zip(pvals, _pw)):
                    lbl = ctk.CTkLabel(
                        pr, text=str(pv),
                        font=ctk.CTkFont(family="Segoe UI", size=13),
                        width=pw, anchor="w",
                    )
                    if ci == 3:
                        lbl.configure(text_color=_PART_STATUS_COLORS.get(pv, "#888"))
                    lbl.grid(row=0, column=ci, padx=(14 if ci == 0 else 6, 6), sticky="w")
            row_ptr[0] += 1

        section_title("📜  Audit Log  (most recent first)")
        if not d["audit_log"]:
            no_log = ctk.CTkFrame(body, corner_radius=10, border_width=1)
            no_log.grid(row=row_ptr[0], column=0, sticky="ew", padx=22, pady=(6, 0))
            ctk.CTkLabel(
                no_log, text="No audit entries found for this ticket.",
                font=ctk.CTkFont(family="Segoe UI", size=13), text_color="gray",
            ).grid(row=0, column=0, padx=16, pady=12)
            row_ptr[0] += 1
        else:
            log_card = ctk.CTkFrame(body, corner_radius=10, border_width=1)
            log_card.grid(row=row_ptr[0], column=0, sticky="ew", padx=22, pady=(6, 0))
            log_card.grid_columnconfigure(0, weight=1)

            lh = ctk.CTkFrame(log_card, fg_color=("gray82", "gray22"),
                              height=34, corner_radius=0)
            lh.grid(row=0, column=0, sticky="ew")
            lh.grid_propagate(False)
            _lh = ["Timestamp", "Action", "Performed By", "Notes"]
            _lw = [155, 175, 130, 270]
            self.admin_view.table_header_row(lh, _lh, _lw)

            for li, log in enumerate(d["audit_log"]):
                bg = ("gray93", "gray19") if li % 2 == 0 else ("gray88", "gray23")
                lr = ctk.CTkFrame(log_card, fg_color=bg, corner_radius=0, height=36)
                lr.grid(row=li + 1, column=0, sticky="ew")
                lr.grid_propagate(False)
                lvals = [
                    log["timestamp"][:16] if len(log["timestamp"]) > 16 else log["timestamp"],
                    log["action"],
                    log["performed_by"],
                    log["notes"],
                ]
                for ci, (lv, lw) in enumerate(zip(lvals, _lw)):
                    ctk.CTkLabel(
                        lr, text=str(lv),
                        font=ctk.CTkFont(family="Segoe UI", size=12),
                        width=lw, anchor="w",
                    ).grid(row=0, column=ci, padx=(14 if ci == 0 else 6, 6), sticky="w")
            row_ptr[0] += 1

        ctk.CTkButton(
            body, text="✕  Close",
            height=46, width=200,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            corner_radius=10,
            fg_color=("gray75", "gray25"), hover_color=("gray65", "gray30"),
            command=popup.destroy,
        ).grid(row=row_ptr[0], column=0, pady=(22, 24))

                                                                        
    def _confirm_cancel_ticket(self, d: dict, parent_popup):
        ticket_id    = d["raw_id"]
        ticket_label = d["id"]
        parts        = d.get("parts", [])

        installed = [p for p in parts if p["status"] == "Installed"]
        draft     = [p for p in parts if p["status"] == "Draft"]

        installed_total = sum(p["cost"] for p in installed)
        draft_total     = sum(p["cost"] for p in draft)

                                                                        
        confirm = ctk.CTkToplevel(parent_popup)
        confirm.title("Confirm Ticket Cancellation")
        confirm.geometry("560x580")
        confirm.minsize(500, 460)
        confirm.grab_set()
        confirm.lift()
        confirm.focus_force()
        confirm.grid_columnconfigure(0, weight=1)
        confirm.grid_rowconfigure(1, weight=1)

                                                                        
        hdr = ctk.CTkFrame(confirm, fg_color="#7f1d1d", corner_radius=0, height=58)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            hdr,
            text=f"⚠️  Cancel {ticket_label}?",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color="white", anchor="w",
        ).grid(row=0, column=0, padx=20, sticky="w")
        ctk.CTkLabel(
            hdr,
            text="This action is irreversible",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#fca5a5", anchor="e",
        ).grid(row=0, column=1, padx=20, sticky="e")

                                                                        
        body = ctk.CTkScrollableFrame(confirm, corner_radius=0, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)

        row_i = [0]

        def sep():
            ctk.CTkFrame(
                body, height=1, fg_color=("gray75", "gray35"), corner_radius=0
            ).grid(row=row_i[0], column=0, sticky="ew", padx=18, pady=(10, 0))
            row_i[0] += 1

        def section_lbl(text, color):
            ctk.CTkLabel(
                body, text=text,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=color, anchor="w",
            ).grid(row=row_i[0], column=0, padx=20, pady=(12, 2), sticky="w")
            row_i[0] += 1

                                                                        
        if installed:
            section_lbl(
                f"🔴  {len(installed)} Installed part(s) - written off as loss",
                "#f87171",
            )
            loss_card = ctk.CTkFrame(
                body, corner_radius=10, border_width=1,
                border_color="#dc2626", fg_color=("#fef2f2", "#1c0606"),
            )
            loss_card.grid(row=row_i[0], column=0, sticky="ew", padx=16, pady=(0, 4))
            loss_card.grid_columnconfigure(1, weight=1)
            row_i[0] += 1

                            
            for ci, (htext, anchor) in enumerate(
                [("Part", "w"), ("Cost", "e")]
            ):
                ctk.CTkLabel(
                    loss_card, text=htext,
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color=("gray50", "gray55"), anchor=anchor,
                ).grid(row=0, column=ci, padx=(14 if ci == 0 else 6, 14), pady=(8, 2), sticky=anchor)

            for pi, p in enumerate(installed):
                ctk.CTkLabel(
                    loss_card, text=p["name"],
                    font=ctk.CTkFont(family="Segoe UI", size=13),
                    text_color="#f87171", anchor="w",
                ).grid(row=pi + 1, column=0, padx=14, pady=3, sticky="w")
                ctk.CTkLabel(
                    loss_card, text=f"-Rs.{p['cost']:.2f}",
                    font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                    text_color="#f87171", anchor="e",
                ).grid(row=pi + 1, column=1, padx=14, pady=3, sticky="e")

                            
            ctk.CTkFrame(
                loss_card, height=1, fg_color="#dc2626", corner_radius=0
            ).grid(
                row=len(installed) + 1, column=0, columnspan=2,
                sticky="ew", padx=10, pady=(4, 0)
            )
            ctk.CTkLabel(
                loss_card, text="Total write-off loss:",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color="#fca5a5", anchor="w",
            ).grid(row=len(installed) + 2, column=0, padx=14, pady=(4, 10), sticky="w")
            ctk.CTkLabel(
                loss_card,
                text=f"-Rs.{installed_total:.2f}",
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color="#f87171", anchor="e",
            ).grid(row=len(installed) + 2, column=1, padx=14, pady=(4, 10), sticky="e")

                                                                        
        if draft:
            sep()
            section_lbl(
                f"📦  {len(draft)} Draft part(s) - returned to inventory",
                "#86efac",
            )
            draft_card = ctk.CTkFrame(
                body, corner_radius=10, border_width=1,
                border_color="#16a34a", fg_color=("#f0fdf4", "#071a0e"),
            )
            draft_card.grid(row=row_i[0], column=0, sticky="ew", padx=16, pady=(0, 4))
            draft_card.grid_columnconfigure(1, weight=1)
            row_i[0] += 1

            for pi, p in enumerate(draft):
                ctk.CTkLabel(
                    draft_card, text=f"✓  {p['name']}",
                    font=ctk.CTkFont(family="Segoe UI", size=13),
                    text_color="#86efac", anchor="w",
                ).grid(row=pi, column=0, padx=14, pady=3, sticky="w")
                ctk.CTkLabel(
                    draft_card, text=f"+Rs.{p['cost']:.2f} back",
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    text_color="#6ee7b7", anchor="e",
                ).grid(row=pi, column=1, padx=14, pady=3, sticky="e")

        if not parts:
            ctk.CTkLabel(
                body, text="ℹ️  No parts allocated to this ticket.",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color="gray", anchor="w",
            ).grid(row=row_i[0], column=0, padx=20, pady=(14, 0), sticky="w")
            row_i[0] += 1

                                                                        
        if installed or draft:
            sep()
            summary_card = ctk.CTkFrame(
                body, corner_radius=10, border_width=1,
                border_color=("gray70", "gray35"),
            )
            summary_card.grid(row=row_i[0], column=0, sticky="ew", padx=16, pady=(8, 4))
            summary_card.grid_columnconfigure(1, weight=1)
            row_i[0] += 1

            ctk.CTkLabel(
                summary_card, text="📊  Financial Impact",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                anchor="w",
            ).grid(row=0, column=0, columnspan=2, padx=14, pady=(10, 6), sticky="w")

            fin_rows = []
            if installed:
                fin_rows.append(
                    (f"  Installed parts loss ({len(installed)} item(s)):",
                     f"-Rs.{installed_total:.2f}", "#f87171")
                )
            if draft:
                fin_rows.append(
                    (f"  Draft parts recovered ({len(draft)} item(s)):",
                     f"+Rs.{draft_total:.2f}", "#86efac")
                )
            net = draft_total - installed_total
            net_color = "#86efac" if net >= 0 else "#f87171"
            fin_rows.append(("  Net impact:", f"Rs.{net:+.2f}", net_color))

            for fi, (label, value, color) in enumerate(fin_rows):
                ctk.CTkLabel(
                    summary_card, text=label,
                    font=ctk.CTkFont(family="Segoe UI", size=12),
                    anchor="w",
                ).grid(row=fi + 1, column=0, padx=14, pady=2, sticky="w")
                ctk.CTkLabel(
                    summary_card, text=value,
                    font=ctk.CTkFont(
                        family="Segoe UI", size=12,
                        weight="bold" if "Net" in label else "normal"
                    ),
                    text_color=color, anchor="e",
                ).grid(row=fi + 1, column=1, padx=14, pady=2, sticky="e")

                    
            ctk.CTkLabel(summary_card, text="").grid(
                row=len(fin_rows) + 1, column=0, pady=(0, 6)
            )

                                                                        
        sep()
        ctk.CTkLabel(
            body,
            text=(
                "Installed parts will be logged as a negative-profit entry in Audit Logs.\n"
                "Draft parts will be returned to inventory automatically."
            ),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray45", "gray55"),
            anchor="w", wraplength=490, justify="left",
        ).grid(row=row_i[0], column=0, padx=20, pady=(8, 4), sticky="w")
        row_i[0] += 1

                                                                        
        btn_frame = ctk.CTkFrame(confirm, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=(8, 18), padx=20, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        def do_cancel():
            admin_id = self.app.session.get("id")
            res = self.app.api.cancel_ticket(admin_id, ticket_id)

            if res["status"] == "success":
                loss = res.get("installed_loss", 0.0)
                msg = res["message"]
                if loss > 0:
                    msg += f"\n\n⚠ Financial loss of Rs.{loss:.2f} recorded in Audit Logs."
                messagebox.showinfo("Ticket Cancelled", msg, parent=confirm)
                confirm.destroy()
                parent_popup.destroy()
                self.refresh_all_tickets()
            else:
                messagebox.showerror(
                    "Error",
                    f"An unexpected error occurred:\n{res.get('message', 'Unknown error')}",
                    parent=confirm,
                )

        ctk.CTkButton(
            btn_frame,
            text="✓  Confirm Cancellation",
            height=44,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            corner_radius=10,
            fg_color="#b91c1c",
            hover_color="#991b1b",
            command=do_cancel,
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="✕  Back",
            height=44,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=10,
            fg_color=("gray75", "gray25"),
            hover_color=("gray65", "gray30"),
            command=confirm.destroy,
        ).grid(row=0, column=1, padx=(6, 0), sticky="ew")
