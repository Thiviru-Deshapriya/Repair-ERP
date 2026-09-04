from __future__ import annotations
from tkinter import messagebox
from datetime import date, timedelta
from typing import TYPE_CHECKING
import customtkinter as ctk

if TYPE_CHECKING:
    from main import RepairERP

                                                                                
                                                
                                                                                
_BLUE   = ("#2980b9", "#2471a3")
_GREEN  = ("#27ae60", "#1e8449")
_ORANGE = ("#e67e22", "#d35400")
_RED    = ("#e74c3c", "#a93226")
_PURPLE = ("#8e44ad", "#6c3483")
_TEAL   = ("#16a085", "#117a65")

_ROW_H = 38
_HDR_H = 36

                                                                                
                               
                                                                                
def _metric_box(parent, col: int, label: str, value: str, color: str):
    box = ctk.CTkFrame(parent, fg_color=color, corner_radius=12)
    box.grid(row=0, column=col, padx=8, pady=8, sticky="ew")
    box.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(box, text=value,
                 font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                 text_color="white").grid(row=0, column=0, padx=16, pady=(14, 2))
    ctk.CTkLabel(box, text=label,
                 font=ctk.CTkFont(family="Segoe UI", size=12),
                 text_color="white",
                 ).grid(row=1, column=0, padx=16, pady=(0, 14))

                                                                                
                           
                                                                                
def _table_header(parent, headers: list[str], widths: list[int]):
    for i, (h, w) in enumerate(zip(headers, widths)):
        ctk.CTkLabel(
            parent, text=h, width=w,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            anchor="w",
        ).grid(row=0, column=i, padx=(14 if i == 0 else 6, 6), sticky="w")

                                                                                
                                 
                                                                                
def _date_range_row(parent, row: int):
    fr = ctk.CTkFrame(parent, fg_color=("gray90", "gray18"), corner_radius=10)
    fr.grid(row=row, column=0, sticky="ew", padx=24, pady=(12, 0))
    fr.grid_columnconfigure(4, weight=1)

    today = date.today()
    first_of_month = today.replace(day=1)

    start_var = ctk.StringVar(value=first_of_month.strftime("%Y-%m-%d"))
    end_var   = ctk.StringVar(value=today.strftime("%Y-%m-%d"))

    ctk.CTkLabel(fr, text="From:",
                 font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
                 ).grid(row=0, column=0, padx=(14, 4), pady=10, sticky="w")
    ctk.CTkEntry(fr, textvariable=start_var, width=110, height=36,
                 font=ctk.CTkFont(family="Segoe UI", size=13),
                 corner_radius=8
                 ).grid(row=0, column=1, padx=(0, 10), pady=10)

    ctk.CTkLabel(fr, text="To:",
                 font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
                 ).grid(row=0, column=2, padx=(0, 4), pady=10, sticky="w")
    ctk.CTkEntry(fr, textvariable=end_var, width=110, height=36,
                 font=ctk.CTkFont(family="Segoe UI", size=13),
                 corner_radius=8
                 ).grid(row=0, column=3, padx=(0, 16), pady=10)

    def _quick(choice):
        t = date.today()
        if choice == "This Month":
            start_var.set(t.replace(day=1).strftime("%Y-%m-%d"))
            end_var.set(t.strftime("%Y-%m-%d"))
        elif choice == "Last 30 Days":
            start_var.set((t - timedelta(days=30)).strftime("%Y-%m-%d"))
            end_var.set(t.strftime("%Y-%m-%d"))
        elif choice == "Last 90 Days":
            start_var.set((t - timedelta(days=90)).strftime("%Y-%m-%d"))
            end_var.set(t.strftime("%Y-%m-%d"))
        elif choice == "This Year":
            start_var.set(t.replace(month=1, day=1).strftime("%Y-%m-%d"))
            end_var.set(t.strftime("%Y-%m-%d"))

    quick_var = ctk.StringVar(value="Quick Select")
    ctk.CTkOptionMenu(fr, values=["This Month", "Last 30 Days", "Last 90 Days", "This Year"],
                      variable=quick_var,
                      width=150, height=36,
                      font=ctk.CTkFont(family="Segoe UI", size=13),
                      corner_radius=8,
                      command=_quick,
                      ).grid(row=0, column=5, padx=(0, 14), pady=10)

    return start_var, end_var, fr

                                                                                
                         
                                                                                
_REPORT_CARDS = [
                                                      
    ("System Reports", "💰", "Financial Summary",
     "Total revenue, service charges, parts cost & net profit by date range.",
     _BLUE, "financial"),

    ("System Reports", "🏦", "Inventory Valuation",
     "Total cash locked in new parts stock + donor components on the shelf.",
     _TEAL, "valuation"),

    ("System Reports", "🚦", "Ticket Pipeline Snapshot",
     "Real-time count of tickets in each status - floor congestion at a glance.",
     _PURPLE, "pipeline"),

    ("System Reports", "📱", "Device & Repair Trends",
     "Most repaired models and most-used parts over the last 6–12 months.",
     _ORANGE, "trends"),
]

                                                                                
       
                                                                                
class ReportsTab(ctk.CTkFrame):

                                                                                
    def __init__(self, parent, app, admin_view):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.admin_view = admin_view
        tab = self
        self.pack(expand=True, fill="both")
        tab.grid_rowconfigure(2, weight=1)
        tab.grid_columnconfigure(0, weight=1)

                
        ctk.CTkLabel(
            tab, text="📊  Reports & Analytics",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=28, pady=(22, 2), sticky="w")

        ctk.CTkLabel(
            tab, text="Generate, filter, and export business intelligence reports",
            font=ctk.CTkFont(family="Segoe UI", size=14), text_color="gray",
            anchor="w",
        ).grid(row=1, column=0, padx=28, pady=(0, 10), sticky="w")

        scroll = ctk.CTkFrame(tab, corner_radius=0, fg_color="transparent")
        scroll.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        scroll.grid_columnconfigure((0, 1), weight=1)

                                
        sections: dict[str, list] = {}
        for card in _REPORT_CARDS:
            sections.setdefault(card[0], []).append(card)

        grid_row = 0
        for section_name, cards in sections.items():
                             
            ctk.CTkFrame(scroll, height=1,
                         fg_color=("gray78", "gray30"), corner_radius=0,
                         ).grid(row=grid_row, column=0, columnspan=2,
                                sticky="ew", padx=28, pady=(18, 4))
            grid_row += 1

                               
            col = 0
            for _, icon, title, desc, accent, key in cards:
                self._make_report_card(scroll, grid_row, col,
                                       icon, title, desc, accent, key)
                col += 1
                if col == 2:
                    col = 0
                    grid_row += 1

            if col != 0:
                grid_row += 1

                        
        ctk.CTkLabel(scroll, text="").grid(row=grid_row, column=0, pady=12)

                                                                                
    def _make_report_card(self, parent, row, col,
                          icon, title, desc, accent, key):
        card = ctk.CTkFrame(parent, corner_radius=14, border_width=1)
        card.grid(row=row, column=col, padx=(28 if col == 0 else 8, 8),
                  pady=6, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.grid(row=1, column=0, sticky="ew", padx=18, pady=(14, 16))
        body.grid_columnconfigure(0, weight=1)

                      
        title_row = ctk.CTkFrame(body, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(title_row, text=icon,
                     font=ctk.CTkFont(family="Segoe UI", size=22),
                     ).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(title_row, text=title,
                     font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                     anchor="w",
                     ).pack(side="left")

                     
        ctk.CTkLabel(body, text=desc,
                     font=ctk.CTkFont(family="Segoe UI", size=12),
                     text_color="gray", anchor="w",
                     wraplength=240, justify="left",
                     ).grid(row=1, column=0, sticky="w", pady=(8, 16))

                         
        dispatch = {
            "financial":  self._open_financial_report,
            "valuation":  self._open_valuation_report,
            "pipeline":   self._open_pipeline_report,
            "trends":     self._open_trends_report,
        }

        ctk.CTkButton(
            body, text="Generate Report ›", height=38,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=8,
            fg_color=accent,
            hover_color=accent,
            command=dispatch[key],
        ).grid(row=2, column=0, sticky="ew")

                                                                                
                              
                                                                                
    def _make_report_popup(self, title: str, accent, width=1080, height=680):
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry(f"{width}x{height}")
        popup.minsize(700, 500)
        popup.grab_set()
        popup.lift()
        popup.focus_force()
        popup.grid_rowconfigure(1, weight=1)
        popup.grid_columnconfigure(0, weight=1)

                
        banner = ctk.CTkFrame(popup, fg_color=accent, corner_radius=0, height=56)
        banner.grid(row=0, column=0, sticky="ew")
        banner.grid_propagate(False)
        banner.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(banner, text=title,
                     font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
                     text_color="white", anchor="w",
                     ).grid(row=0, column=0, padx=22, sticky="w",pady=10)

        body = ctk.CTkFrame(popup, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(99, weight=1)

        return popup, body, banner

                                                                                
                          
                                                                                
    def _open_financial_report(self):
        popup, body, banner = self._make_report_popup(
            "💰  Financial Summary Report", _BLUE[0])

        start_var, end_var, _ = _date_range_row(body, 0)

        def _run():
            res = self.app.api.get_financial_summary(
                start_var.get(), end_var.get())
            if res["status"] != "success":
                messagebox.showerror("Error", res.get("message"), parent=popup)
                return
            s = res["summary"]

                                  
            for w in metrics_frame.winfo_children():
                w.destroy()
            _metric_box(metrics_frame, 0, "Tickets Completed",
                        str(s["ticket_count"]), _BLUE[0])
            _metric_box(metrics_frame, 1, "Total Revenue",
                        f"Rs. {s['total_revenue']:,.0f}", _GREEN[0])
            _metric_box(metrics_frame, 2, "Total Parts Cost",
                        f"Rs. {s['total_parts']:,.0f}", _ORANGE[0])
            _metric_box(metrics_frame, 3, "Net Profit",
                        f"Rs. {s['total_profit']:,.0f}", _PURPLE[0])

                           
            for w in table_scroll.winfo_children():
                w.destroy()
            if not res["rows"]:
                ctk.CTkLabel(table_scroll,
                             text="No completed tickets in this date range.",
                             font=ctk.CTkFont(family="Segoe UI", size=13),
                             text_color="gray").pack(pady=30)
                return

            _hdrs = ["Ticket", "Customer", "Device", "Completed",
                     "Service Charge", "Parts Cost", "Net Profit"]
            _wids = [90, 170, 160, 100, 120, 110, 110]

            hdr_bar = ctk.CTkFrame(table_scroll,
                                   fg_color=("gray82", "gray20"), height=_HDR_H,
                                   corner_radius=6)
            hdr_bar.pack(fill="x", pady=(0, 2))
            hdr_bar.pack_propagate(False)
            _table_header(hdr_bar, _hdrs, _wids)

            for idx, r in enumerate(res["rows"]):
                bg = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")
                row_fr = ctk.CTkFrame(table_scroll, fg_color=bg,
                                      corner_radius=6, height=_ROW_H)
                row_fr.pack(fill="x", pady=1)
                row_fr.pack_propagate(False)

                vals = [r["ticket_id"], r["customer"], r["device"],
                        r["completed_at"],
                        f"Rs. {r['service_charge']:,.0f}",
                        f"Rs. {r['parts_cost']:,.0f}",
                        f"Rs. {r['net_profit']:,.0f}"]
                for ci, (v, w) in enumerate(zip(vals, _wids)):
                    lbl = ctk.CTkLabel(row_fr, text=v, width=w, anchor="w",
                                       font=ctk.CTkFont(family="Segoe UI", size=13))
                    if ci == 6:
                        color = _GREEN[0] if r["net_profit"] >= 0 else _RED[0]
                        lbl.configure(text_color=color,
                                      font=ctk.CTkFont(family="Segoe UI",
                                                        size=13, weight="bold"))
                    lbl.grid(row=0, column=ci,
                             padx=(14 if ci == 0 else 6, 6), sticky="w")

                    
        ctk.CTkButton(body, text="▶  Run Query", height=40, width=130,
                      font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                      fg_color=_BLUE, corner_radius=8,
                      command=_run,
                      ).grid(row=1, column=0, padx=24, pady=(8, 12), sticky="w")

                      
        metrics_frame = ctk.CTkFrame(body, fg_color="transparent")
        metrics_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

               
        table_scroll = ctk.CTkScrollableFrame(body, corner_radius=8)
        table_scroll.grid(row=3, column=0, sticky="nsew", padx=24, pady=(0, 20))
        body.grid_rowconfigure(3, weight=1)

        _run()                           

                                                                                
                            
                                                                                
    def _open_valuation_report(self):
        popup, body, banner = self._make_report_popup(
            "🏦  Inventory Valuation Report", _TEAL[0], width=960)

        res = self.app.api.get_inventory_valuation()
        if res["status"] != "success":
            ctk.CTkLabel(body, text=f"Error: {res.get('message')}",
                         text_color=_RED[0]).grid(row=0, column=0, padx=24, pady=20)
            return

        new_d   = res["new_parts"]
        donor_d = res["donor_parts"]

                 
        mf = ctk.CTkFrame(body, fg_color="transparent")
        mf.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        mf.grid_columnconfigure((0, 1, 2), weight=1)
        _metric_box(mf, 0, "New Parts Value",
                    f"Rs. {new_d['total']:,.0f}", _BLUE[0])
        _metric_box(mf, 1, "Donor Parts Value",
                    f"Rs. {donor_d['total']:,.0f}", _TEAL[0])
        _metric_box(mf, 2, "Grand Total",
                    f"Rs. {res['grand_total']:,.0f}", _GREEN[0])

                            
        tab_view = ctk.CTkTabview(body, height=400)
        tab_view.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 20))
        body.grid_rowconfigure(1, weight=1)

        tab_new   = tab_view.add(f"New Parts ({new_d['count']})")
        tab_donor = tab_view.add(f"Donor Components ({donor_d['count']})")

                         
        tab_new.grid_rowconfigure(0, weight=1)
        tab_new.grid_columnconfigure(0, weight=1)
        scr_new = ctk.CTkScrollableFrame(tab_new, corner_radius=8)
        scr_new.grid(row=0, column=0, sticky="nsew")

        _hdrs_n = ["Part ID", "Part Name", "Brand", "Stock", "Unit Cost", "Line Value"]
        _wids_n = [80, 220, 130, 70, 110, 120]
        hb = ctk.CTkFrame(scr_new, fg_color=("gray82", "gray20"),
                          height=_HDR_H, corner_radius=6)
        hb.pack(fill="x", pady=(0, 2))
        hb.pack_propagate(False)
        _table_header(hb, _hdrs_n, _wids_n)

        for idx, r in enumerate(new_d["rows"]):
            bg = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")
            row_fr = ctk.CTkFrame(scr_new, fg_color=bg,
                                  corner_radius=6, height=_ROW_H)
            row_fr.pack(fill="x", pady=1)
            row_fr.pack_propagate(False)
            vals = [r["part_id"], r["name"], r["brand"], str(r["stock"]),
                    f"Rs. {r['unit_cost']:.2f}", f"Rs. {r['value']:,.0f}"]
            for ci, (v, w) in enumerate(zip(vals, _wids_n)):
                ctk.CTkLabel(row_fr, text=v, width=w, anchor="w",
                             font=ctk.CTkFont(family="Segoe UI", size=13)
                             ).grid(row=0, column=ci,
                                    padx=(14 if ci == 0 else 6, 6), sticky="w")

                           
        tab_donor.grid_rowconfigure(0, weight=1)
        tab_donor.grid_columnconfigure(0, weight=1)
        scr_don = ctk.CTkScrollableFrame(tab_donor, corner_radius=8)
        scr_don.grid(row=0, column=0, sticky="nsew")

        _hdrs_d = ["Component", "Part Name", "Brand", "Model", "Est. Value"]
        _wids_d = [100, 220, 120, 150, 120]
        hbd = ctk.CTkFrame(scr_don, fg_color=("gray82", "gray20"),
                           height=_HDR_H, corner_radius=6)
        hbd.pack(fill="x", pady=(0, 2))
        hbd.pack_propagate(False)
        _table_header(hbd, _hdrs_d, _wids_d)

        for idx, r in enumerate(donor_d["rows"]):
            bg = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")
            row_fr = ctk.CTkFrame(scr_don, fg_color=bg,
                                  corner_radius=6, height=_ROW_H)
            row_fr.pack(fill="x", pady=1)
            row_fr.pack_propagate(False)
            vals = [r["component_id"], r["name"], r["brand"],
                    r["model"], f"Rs. {r['est_value']:,.0f}"]
            for ci, (v, w) in enumerate(zip(vals, _wids_d)):
                ctk.CTkLabel(row_fr, text=v, width=w, anchor="w",
                             font=ctk.CTkFont(family="Segoe UI", size=13)
                             ).grid(row=0, column=ci,
                                    padx=(14 if ci == 0 else 6, 6), sticky="w")

                                                                                
                                 
                                                                                
    def _open_pipeline_report(self):
        popup, body, banner = self._make_report_popup(
            "🚦  Ticket Pipeline Snapshot", _BLUE[0], width=700, height=520)

        res = self.app.api.get_ticket_pipeline()
        if res["status"] != "success":
            ctk.CTkLabel(body, text=f"Error: {res.get('message')}",
                         text_color=_RED[0]).grid(row=0, column=0, padx=24, pady=20)
            return

        pipeline = res["pipeline"]
        status_colors = {
            "Intake":      _BLUE[0],
            "In-Progress": _ORANGE[0],
        }

        mf = ctk.CTkFrame(body, fg_color="transparent")
        mf.grid(row=0, column=0, sticky="ew", padx=16, pady=(20, 10))
        mf.grid_columnconfigure((0, 1, 2), weight=1)

        _metric_box(mf, 0, "Total Active",
                    str(res["total_active"]), _BLUE[0])
        _metric_box(mf, 1, "Awaiting Pickup",
                    str(res["awaiting_pickup"]), _ORANGE[0])
        _metric_box(mf, 2, "Total Completed (All Time)",
                    str(res["total_completed"]), _GREEN[0])

                     
        bars_frame = ctk.CTkFrame(body, fg_color=("gray93", "gray17"),
                                  corner_radius=12)
        bars_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=(10, 20))
        bars_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(bars_frame, text="Current Status Breakdown",
                     font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                     anchor="w").grid(row=0, column=0, padx=18, pady=(14, 8),
                                      sticky="w")

        for i, (status, count) in enumerate(pipeline.items()):
            color = status_colors.get(status, _TEAL[0])
            row_fr = ctk.CTkFrame(bars_frame, fg_color="transparent")
            row_fr.grid(row=i + 1, column=0, sticky="ew",
                        padx=18, pady=(0, 10))
            row_fr.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row_fr, text=status, width=130,
                         font=ctk.CTkFont(family="Segoe UI", size=13,
                                           weight="bold"),
                         text_color=color, anchor="w",
                         ).grid(row=0, column=0, sticky="w")

            max_count = max(pipeline.values()) if pipeline else 1
            bar_width = max(int((count / max_count) * 380), 6)

            bar_bg = ctk.CTkFrame(row_fr, fg_color=("gray80", "gray30"),
                                  corner_radius=6, height=26)
            bar_bg.grid(row=0, column=1, sticky="ew", padx=(8, 16))
            bar_fill = ctk.CTkFrame(bar_bg, fg_color=color,
                                    corner_radius=6, width=bar_width, height=26)
            bar_fill.place(x=0, y=0)

            ctk.CTkLabel(row_fr, text=str(count), width=40,
                         font=ctk.CTkFont(family="Segoe UI", size=13,
                                           weight="bold"),
                         ).grid(row=0, column=2, sticky="e")

        if not pipeline:
            ctk.CTkLabel(bars_frame,
                         text="No active tickets at this time. 🎉",
                         text_color="gray").grid(row=1, column=0, pady=20)

                                                                                
                               
                                                                                
    def _open_trends_report(self):
        popup, body, banner = self._make_report_popup(
            "📱  Device & Repair Trends", _ORANGE[0], width=960, height=700)

                         
        ctrl = ctk.CTkFrame(body, fg_color=("gray90", "gray18"), corner_radius=10)
        ctrl.grid(row=0, column=0, sticky="ew", padx=24, pady=(14, 0))
        ctk.CTkLabel(ctrl, text="Look-back period:",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     ).pack(side="left", padx=(14, 8), pady=10)
        months_var = ctk.StringVar(value="6 Months")
        ctk.CTkOptionMenu(ctrl,
                          values=["3 Months", "6 Months", "12 Months"],
                          variable=months_var,
                          width=130, height=36,
                          font=ctk.CTkFont(family="Segoe UI", size=13),
                          corner_radius=8,
                          ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(ctrl, text="▶  Run", height=36, width=90,
                      font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                      fg_color=_ORANGE, corner_radius=8,
                      command=lambda: _run(int(months_var.get().split()[0])),
                      ).pack(side="left", padx=(0, 14), pady=8)

                            
        cards_row = ctk.CTkFrame(body, fg_color="transparent")
        cards_row.grid(row=1, column=0, sticky="nsew", padx=24, pady=(12, 20))
        body.grid_rowconfigure(1, weight=1)
        cards_row.grid_columnconfigure((0, 1, 2), weight=1)
        cards_row.grid_rowconfigure(0, weight=1)

        def _make_list_card(parent, col, title, color):
            frame = ctk.CTkFrame(parent, corner_radius=12, border_width=1)
            frame.grid(row=0, column=col,
                       padx=(0 if col == 0 else 8, 8 if col < 2 else 0),
                       pady=0, sticky="nsew")
            frame.grid_rowconfigure(1, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            hdr = ctk.CTkFrame(frame, fg_color=color, corner_radius=0, height=42)
            hdr.grid(row=0, column=0, sticky="ew")
            hdr.grid_propagate(False)
            hdr.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(hdr, text=title,
                         font=ctk.CTkFont(family="Segoe UI", size=13,
                                           weight="bold"),
                         text_color="white", anchor="w",
                         ).grid(row=0, column=0, padx=14, sticky="w")
            scr = ctk.CTkScrollableFrame(frame, corner_radius=0,
                                          fg_color=("gray96", "gray15"))
            scr.grid(row=1, column=0, sticky="nsew")
            scr.grid_columnconfigure(0, weight=1)
            return scr

        scr_devices = _make_list_card(cards_row, 0,
                                       "📱  Top Device Models", _BLUE[0])
        scr_parts   = _make_list_card(cards_row, 1,
                                       "🔩  Top New Parts Used", _GREEN[0])
        scr_donor   = _make_list_card(cards_row, 2,
                                       "♻️  Top Donor Parts Used", _TEAL[0])

        def _populate_list(scroll_frame, items, key_field, val_field, accent):
            for w in scroll_frame.winfo_children():
                w.destroy()
            if not items:
                ctk.CTkLabel(scroll_frame,
                             text="No data yet.",
                             text_color="gray").pack(pady=20)
                return
            max_val = max(r[val_field] for r in items) if items else 1
            for rank, r in enumerate(items, 1):
                row_fr = ctk.CTkFrame(scroll_frame,
                                       fg_color=("gray92", "gray18") if rank % 2 == 0
                                       else ("gray88", "gray22"),
                                       corner_radius=8, height=48)
                row_fr.pack(fill="x", padx=4, pady=2)
                row_fr.pack_propagate(False)
                row_fr.grid_columnconfigure(1, weight=1)

                ctk.CTkLabel(row_fr,
                             text=f" #{rank} ",
                             font=ctk.CTkFont(family="Segoe UI", size=11,
                                               weight="bold"),
                             fg_color=accent, text_color="white",
                             corner_radius=4, width=32,
                             ).grid(row=0, column=0, padx=(10, 8), pady=10,
                                    sticky="w")
                ctk.CTkLabel(row_fr, text=r[key_field],
                             font=ctk.CTkFont(family="Segoe UI", size=13),
                             anchor="w",
                             ).grid(row=0, column=1, sticky="w")
                ctk.CTkLabel(row_fr,
                             text=f"×{r[val_field]}",
                             font=ctk.CTkFont(family="Segoe UI", size=13,
                                               weight="bold"),
                             text_color=accent,
                             ).grid(row=0, column=2, padx=(0, 12), sticky="e")

        def _run(months=6):
            res = self.app.api.get_device_trends(months)
            if res["status"] != "success":
                messagebox.showerror("Error", res.get("message"), parent=popup)
                return
            _populate_list(scr_devices, res["device_trends"],
                           "device", "count", _BLUE[0])
            _populate_list(scr_parts, res["top_parts"],
                           "part", "count", _GREEN[0])
            _populate_list(scr_donor, res["top_donor_parts"],
                           "part", "count", _TEAL[0])

        _run()