from __future__ import annotations
import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import RepairERP
    from views.admin_view import AdminView

class DashboardTab(ctk.CTkFrame):
    def __init__(self, parent, app: "RepairERP", admin_view: "AdminView"):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.admin_view = admin_view
        
        self.grid_rowconfigure(3, weight=1)                
        self.grid_rowconfigure(6, weight=1)                   
        self.grid_columnconfigure(0, weight=1)

                                                                        
        ctk.CTkLabel(
            self, text="🚨  Action Center",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=28, pady=(22, 2), sticky="w")

        self._alerts_subtitle = ctk.CTkLabel(
            self, text="Resolve low stock warnings and flagged components - all in one place",
            font=ctk.CTkFont(family="Segoe UI", size=14), text_color="gray",
            anchor="w",
        )
        self._alerts_subtitle.grid(row=1, column=0, padx=28, pady=(0, 12), sticky="w")

                                                                          
                                                              
                                                                          
        top_hdr_row = ctk.CTkFrame(self, fg_color="transparent")
        top_hdr_row.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 4))
        top_hdr_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top_hdr_row,
            text="📦  Inventory Warnings  -  Low Stock (< 5 units)",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self._low_stock_count_lbl = ctk.CTkLabel(
            top_hdr_row, text="",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#e74c3c", text_color="white", corner_radius=8,
            width=32, height=22,
        )
        self._low_stock_count_lbl.grid(row=0, column=1, padx=(8, 0), sticky="e")

                                             
        self._alerts_scroll_top = ctk.CTkScrollableFrame(
            self, corner_radius=8, fg_color=("gray96", "gray16"),
        )
        self._alerts_scroll_top.grid(row=3, column=0, sticky="nsew", padx=28, pady=(0, 8))
        self._alerts_scroll_top.grid_columnconfigure(0, weight=1)

                                                                          
                                                                          
                                                                          
        sep = ctk.CTkFrame(self, height=2, fg_color=("gray75", "gray30"), corner_radius=0)
        sep.grid(row=4, column=0, sticky="ew", padx=28, pady=(4, 8))

        bot_hdr_row = ctk.CTkFrame(self, fg_color="transparent")
        bot_hdr_row.grid(row=5, column=0, sticky="ew", padx=28, pady=(0, 4))
        bot_hdr_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            bot_hdr_row,
            text="⚠️  Quality Control  -  Flagged Donor Components",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self._flagged_count_lbl = ctk.CTkLabel(
            bot_hdr_row, text="",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#e67e22", text_color="white", corner_radius=8,
            width=32, height=22,
        )
        self._flagged_count_lbl.grid(row=0, column=1, padx=(8, 0), sticky="e")

                                                     
        self._alerts_scroll_bot = ctk.CTkScrollableFrame(
            self, corner_radius=8, fg_color=("gray96", "gray16"),
        )
        self._alerts_scroll_bot.grid(row=6, column=0, sticky="nsew", padx=28, pady=(0, 20))
        self._alerts_scroll_bot.grid_columnconfigure(0, weight=1)

                      
        self.refresh_alerts()

    def refresh_alert_badge(self):
        res = self.app.api.get_alert_counts()
        if res["status"] == "success":
            total = res["low_stock"] + res["flagged"]
            self.admin_view.update_nav_badge(self.admin_view._ALERTS_NAV_LABEL, total)

    def refresh_alerts(self):
        self.refresh_alert_badge()
        self._populate_low_stock()
        self._populate_flagged()

    def _populate_low_stock(self):
        frame = self._alerts_scroll_top
        for w in frame.winfo_children():
            w.destroy()

        res = self.app.api.get_low_stock_alerts()
        if res["status"] != "success":
            self.admin_view.empty_label(frame, f"Error: {res.get('message')}")
            return

        parts = res["data"]
        count = len(parts)
        if count:
            self._low_stock_count_lbl.configure(text=f" {count} ")
            self._low_stock_count_lbl.grid()
        else:
            self._low_stock_count_lbl.grid_remove()

        if not parts:
            self.admin_view.empty_label(frame, "No low-stock items. All inventory levels are healthy. 🎉")
            return

        for idx, p in enumerate(parts):
            stock = p["current_stock"]
            
            if stock == 0:
                accent = "#e74c3c"                              
                badge_text = "OUT OF STOCK"
            elif stock <= 2:
                accent = "#e74c3c"                          
                badge_text = f"Only {stock} left!"
            else:
                accent = "#e67e22"                            
                badge_text = f"Only {stock} left"

            bg = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")
            
                                                                 
            card = ctk.CTkFrame(frame, fg_color=bg, corner_radius=10, border_width=1,
                                border_color=(accent, accent), height=10)
            card.grid(row=idx, column=0, sticky="ew", pady=3, padx=4)
            card.grid_propagate(False)                                               

                                
            bar = ctk.CTkFrame(card, width=6, fg_color=accent, corner_radius=4)
            bar.pack(side="left", fill="y", padx=(6, 8), pady=4)

                                        
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", padx=(4, 10), pady=4)

            ctk.CTkLabel(
                info, text=p["part_name"],
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                info, text=f"Brand: {p['brand']}   ·   Unit Cost: Rs. {p['unit_cost']:.2f}",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=("gray45", "gray60"), anchor="w",
            ).pack(anchor="w", pady=(2, 0))

                                                             
            ctk.CTkLabel(
                card, text=f"  {badge_text}  ",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                fg_color=accent, text_color="white", corner_radius=6,
            ).pack(side="left", padx=10)

                                                                      
            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.pack(side="right", padx=(0, 12))

            qty_entry = ctk.CTkEntry(
                actions, placeholder_text="Qty", width=50, height=26,
                font=ctk.CTkFont(family="Segoe UI", size=12), corner_radius=8,
            )
            qty_entry.pack(side="left", padx=(0, 6))

            ctk.CTkButton(
                actions, text="＋ Restock", width=80, height=26,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                corner_radius=8,
                fg_color=("#3498db", "#2471a3"),
                hover_color=("#2980b9", "#1f618d"),
                command=lambda pid=p["part_id"], pname=p["part_name"],
                               pcost=p["unit_cost"], qe=qty_entry:
                    self._quick_restock(pid, pname, pcost, qe),
            ).pack(side="left")

    def _quick_restock(self, part_id: int, part_name: str,
                       current_cost: float, qty_entry: ctk.CTkEntry):
        raw = qty_entry.get().strip()
        if not raw or not raw.isdigit() or int(raw) <= 0:
            messagebox.showerror(
                "Invalid Quantity",
                "Please enter a positive whole number in the Qty field.",
            )
            return

        added = int(raw)
        result = self.app.api.restock_existing_part(
            admin_id=self.app.session.get("id"),
            part_id=part_id,
            added_quantity=added,
            new_cost=None,
        )
        if result["status"] == "success":
            messagebox.showinfo(
                "Restocked",
                f"Added {added} unit(s) to \"{part_name}\" successfully.",
            )
            self.refresh_alerts()
        else:
            messagebox.showerror(
                "Restock Failed",
                result.get("message", "An unknown error occurred."),
            )

    def _populate_flagged(self):
        frame = self._alerts_scroll_bot
        for w in frame.winfo_children():
            w.destroy()

        res = self.app.api.get_flagged_components()
        if res["status"] != "success":
            self.admin_view.empty_label(frame, f"Error: {res.get('message')}")
            return

        items = res["data"]
        count = len(items)
        if count:
            self._flagged_count_lbl.configure(text=f" {count} ")
            self._flagged_count_lbl.grid()
        else:
            self._flagged_count_lbl.grid_remove()

        if not items:
            self.admin_view.empty_label(frame, "No flagged components. All donor parts are clear. ✅")
            return

        for idx, item in enumerate(items):
            bg = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")
            card = ctk.CTkFrame(frame, fg_color=bg, corner_radius=10, border_width=1,
                                border_color=("#e67e22", "#e67e22"))
            card.grid(row=idx, column=0, sticky="ew", pady=4, padx=4)
            card.grid_columnconfigure(1, weight=1)

                                      
            bar = ctk.CTkFrame(card, width=6, fg_color="#e67e22", corner_radius=4)
            bar.grid(row=0, column=0, rowspan=3, sticky="ns", padx=(6, 8), pady=8)

                                           
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.grid(row=0, column=1, sticky="ew", padx=10, pady=(10, 0))
            info.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                info, text=f"C-{item['component_id']:04d}  ·  {item['part_name']}",
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                anchor="w",
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                info,
                text=f"Source Board: {item['board_brand']} {item['board_model']}   ·   "
                     f"Flagged by: {item['flagged_by']}   ·   {item['flagged_at'][:16] if len(item['flagged_at']) > 16 else item['flagged_at']}",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=("gray45", "gray60"), anchor="w",
            ).grid(row=1, column=0, sticky="w", pady=(2, 0))

                                            
            notes_frame = ctk.CTkFrame(card, fg_color=("gray88", "gray22"), corner_radius=8)
            notes_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=(6, 0))
            notes_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                notes_frame,
                text=f"📝 Tech Notes:  \"{item['tech_notes']}\"",
                font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic"),
                anchor="w", wraplength=500, justify="left",
            ).grid(row=0, column=0, padx=12, pady=8, sticky="w")

                                
            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.grid(row=2, column=1, sticky="w", padx=0, pady=(6, 10))

            ctk.CTkButton(
                btn_row, text="✔  Restore to Stock", width=160, height=36,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                corner_radius=8,
                fg_color=("#27ae60", "#1e8449"),
                hover_color=("#229954", "#1a7640"),
                command=lambda cid=item["component_id"], cname=item["part_name"]:
                    self._resolve_flag(cid, cname, "Available"),
            ).pack(side="left", padx=(0, 10))

            ctk.CTkButton(
                btn_row, text="✕  Confirm Damaged", width=160, height=36,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                corner_radius=8,
                fg_color=("#e74c3c", "#a93226"),
                hover_color=("#c0392b", "#922b21"),
                command=lambda cid=item["component_id"], cname=item["part_name"]:
                    self._resolve_flag(cid, cname, "Damaged"),
            ).pack(side="left")

    def _resolve_flag(self, component_id: int, part_name: str, decision: str):
        if decision == "Damaged":
            msg = (f'Confirm that "{part_name}" (C-{component_id:04d}) is damaged?\n\n'
                   f'This will permanently write off the component.')
        else:
            msg = (f'Restore "{part_name}" (C-{component_id:04d}) back to Available stock?\n\n'
                   f'The component will become usable again.')

        confirmed = messagebox.askyesno(
            f"{'Confirm Damage' if decision == 'Damaged' else 'Restore Component'}",
            msg, icon="warning",
        )
        if not confirmed:
            return

        result = self.app.api.resolve_flagged_component(
            admin_id=self.app.session.get("id"),
            component_id=component_id,
            decision=decision,
        )

        if result["status"] == "success":
            messagebox.showinfo("Resolved", result["message"])
            self.refresh_alerts()
        else:
            messagebox.showerror("Error", result.get("message", "Failed to resolve flag."))
