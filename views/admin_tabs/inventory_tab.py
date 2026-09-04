from __future__ import annotations
import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING
import sqlite3

if TYPE_CHECKING:
    from main import RepairERP
    from views.admin_view import AdminView

_ROW_H = 46
_HDR_H = 44

class InventoryTab(ctk.CTkFrame):
    def __init__(self, parent, app: "RepairERP", admin_view: "AdminView"):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.admin_view = admin_view

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

                                                                        
        ctk.CTkLabel(
            self, text="📦  Manage Inventory",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=28, pady=(22, 2), sticky="w")

        ctk.CTkLabel(
            self, text="Track stock levels, restock parts, and add new part types - sorted by lowest stock first",
            font=ctk.CTkFont(family="Segoe UI", size=14), text_color="gray",
            anchor="w",
        ).grid(row=1, column=0, padx=28, pady=(0, 8), sticky="w")

                                                                        
        search_row = ctk.CTkFrame(self, fg_color="transparent")
        search_row.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 6))
        search_row.grid_columnconfigure(0, weight=1)

        self._inv_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="🔍  Search by part name or brand…",
            textvariable=self._inv_search_var,
            height=44,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=10,
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_inventory())

                         
        self._inv_filter_var = ctk.StringVar(value="All Parts")
        filter_menu = ctk.CTkOptionMenu(
            search_row,
            values=["All Parts", "Low Stock (< 5)", "Out of Stock"],
            variable=self._inv_filter_var,
            height=44, width=180,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=10,
            command=lambda _: self.refresh_inventory(),
        )
        filter_menu.grid(row=0, column=1, padx=(0, 10))

        ctk.CTkButton(
            search_row, text="⟳  Refresh", width=110, height=44,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=10,
            command=self.refresh_inventory,
        ).grid(row=0, column=2, padx=(0, 10))

        ctk.CTkButton(
            search_row, text="＋ Add New Part Type", width=200, height=44,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            corner_radius=10,
            fg_color=("#27ae60", "#1e8449"),
            hover_color=("#229954", "#1a7640"),
            command=self._show_add_part_popup,
        ).grid(row=0, column=3)

                                                                        
        _inv_headers = ["Part ID", "Part Name", "Brand", "Unit Cost", "Stock", "Actions"]
        _inv_widths  = [100, 240, 160, 110, 90, 90, 210]

        col_hdr = ctk.CTkFrame(
            self, fg_color=("gray82", "gray20"), height=_HDR_H, corner_radius=8
        )
        col_hdr.grid(row=3, column=0, sticky="ew", padx=28, pady=(0, 2))
        col_hdr.grid_propagate(False)
        self.admin_view.table_header_row(col_hdr, _inv_headers, _inv_widths)

        self._inv_widths = _inv_widths

                                                                        
        self._inv_scroll = ctk.CTkScrollableFrame(self, corner_radius=8)
        self._inv_scroll.grid(row=4, column=0, sticky="nsew", padx=28, pady=(0, 20))
        self._inv_scroll.grid_columnconfigure(0, weight=1)

                      
        self.refresh_inventory()

    def refresh_inventory(self):
        frame = self._inv_scroll
        for w in frame.winfo_children():
            w.destroy()

        search = self._inv_search_var.get().strip()
        filter_val = self._inv_filter_var.get()

        stock_filter = "all"
        if "Low" in filter_val:
            stock_filter = "low"
        elif "Out" in filter_val:
            stock_filter = "out"

        res = self.app.api.get_all_inventory(search_term=search, stock_filter=stock_filter)

        if res["status"] != "success":
            self.admin_view.empty_label(frame, f"Error loading inventory: {res.get('message')}")
            return

        parts = res["data"]
        if not parts:
            msg = "No parts in inventory." if not search else f'No results for "{search}".'
            if stock_filter == "low":
                msg = "No parts with low stock. 🎉"
            elif stock_filter == "out":
                msg = "No parts are out of stock. 🎉"
            self.admin_view.empty_label(frame, msg)
            return

        widths = self._inv_widths
        for idx, p in enumerate(parts):
            bg = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")
            row = ctk.CTkFrame(frame, fg_color=bg, corner_radius=6, height=_ROW_H)
            row.grid(row=idx, column=0, sticky="ew", pady=2)
            row.grid_propagate(False)

            
            cell_values = [
                f"P-{p['part_id']:04d}",
                p["part_name"],
                p["brand"],
                f"Rs. {p['unit_cost']:.2f}",
                str(p["current_stock"]),
                
            ]

            for i, (val, w) in enumerate(zip(cell_values, widths[:-1])):
                lbl = ctk.CTkLabel(
                    row, text=val,
                    font=ctk.CTkFont(family="Segoe UI", size=14),
                    width=w, anchor="w",
                )
                if i == 5:
                    lbl.configure(
                        text_color=stock_color,
                        font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                    )
                lbl.grid(row=0, column=i, padx=(14 if i == 0 else 6, 6), sticky="w")

            actions = ctk.CTkFrame(row, fg_color="transparent", width=widths[-1])
            actions.grid(row=0, column=len(widths) - 1, padx=(6, 12), sticky="w")

            ctk.CTkButton(
                actions, text="＋ Restock", width=90, height=32,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                corner_radius=6,
                fg_color=("#3498db", "#2471a3"),
                hover_color=("#2980b9", "#1f618d"),
                command=lambda pid=p["part_id"], pname=p["part_name"],
                               pcost=p["unit_cost"]: self._show_restock_dialog(pid, pname, pcost),
            ).pack(side="left", padx=(0, 6), pady=6)

            ctk.CTkButton(
                actions, text="✎ Edit", width=80, height=32,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                corner_radius=6,
                fg_color=("gray70", "gray30"),
                hover_color=("gray60", "gray35"),
                command=lambda pid=p["part_id"], pname=p["part_name"],
                               pbrand=p["brand"], pcost=p["unit_cost"]: self._show_edit_part_dialog(pid, pname, pbrand, pcost),
            ).pack(side="left", pady=6)

    def _show_restock_dialog(self, part_id: int, part_name: str, current_cost: float):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Restock - {part_name}")
        popup.geometry("440x340")
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()
        popup.focus_force()

        popup.grid_columnconfigure(0, weight=1)

        banner = ctk.CTkFrame(popup, fg_color=("#3498db", "#2471a3"), corner_radius=0, height=54)
        banner.grid(row=0, column=0, sticky="ew")
        banner.grid_propagate(False)
        banner.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            banner, text=f"＋  Restock: {part_name}",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="white", anchor="w",
        ).grid(row=0, column=0, padx=18, sticky="w")

        body = ctk.CTkFrame(popup, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        body.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            body, text="Quantity to Add *",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        qty_entry = ctk.CTkEntry(
            body, height=42, placeholder_text="e.g. 10",
            font=ctk.CTkFont(family="Segoe UI", size=14), corner_radius=8,
        )
        qty_entry.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(
            body, text=f"New Unit Cost  (current: Rs. {current_cost:.2f})  - optional",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), anchor="w",
        ).grid(row=2, column=0, sticky="w", pady=(0, 4))

        cost_entry = ctk.CTkEntry(
            body, height=42, placeholder_text="Leave blank to keep current cost",
            font=ctk.CTkFont(family="Segoe UI", size=14), corner_radius=8,
        )
        cost_entry.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        status_lbl = ctk.CTkLabel(
            body, text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        status_lbl.grid(row=4, column=0, sticky="w")

        def _do_restock():
            raw_qty = qty_entry.get().strip()
            if not raw_qty or not raw_qty.isdigit() or int(raw_qty) <= 0:
                status_lbl.configure(text="Enter a valid positive quantity.", text_color="#e05c5c")
                return

            added = int(raw_qty)
            new_cost = None
            raw_cost = cost_entry.get().strip()
            if raw_cost:
                try:
                    new_cost = float(raw_cost)
                    if new_cost < 0:
                        raise ValueError
                except ValueError:
                    status_lbl.configure(text="Enter a valid cost or leave blank.", text_color="#e05c5c")
                    return

            result = self.app.api.restock_existing_part(
                admin_id=self.app.session.get("id"),
                part_id=part_id,
                added_quantity=added,
                new_cost=new_cost,
            )

            if result["status"] == "success":
                messagebox.showinfo("Restocked", f"Added {added} units to \"{part_name}\" successfully.")
                popup.destroy()
                self.refresh_inventory()
            else:
                status_lbl.configure(text=result.get("message", "Restock failed."), text_color="#e05c5c")

        ctk.CTkButton(
            body, text="✔  Save Restock", height=44,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            corner_radius=10,
            fg_color=("#3498db", "#2471a3"),
            hover_color=("#2980b9", "#1f618d"),
            command=_do_restock,
        ).grid(row=5, column=0, sticky="ew", pady=(8, 0))

    def _show_edit_part_dialog(self, part_id: int, part_name: str, brand: str, unit_cost: float):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Edit Part - P-{part_id:04d}")
        popup.geometry("460x420")
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()
        popup.focus_force()

        popup.grid_columnconfigure(0, weight=1)

        banner = ctk.CTkFrame(popup, fg_color=("gray65", "gray25"), corner_radius=0, height=54)
        banner.grid(row=0, column=0, sticky="ew")
        banner.grid_propagate(False)
        banner.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            banner, text=f"✎  Edit Part: P-{part_id:04d}",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="white", anchor="w",
        ).grid(row=0, column=0, padx=18, sticky="w")

        body = ctk.CTkFrame(popup, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        body.grid_columnconfigure(0, weight=1)

        fields = [("Part Name", part_name), ("Brand", brand), ("Unit Cost", f"{unit_cost:.2f}")]
        entries = {}

        for i, (label, val) in enumerate(fields):
            ctk.CTkLabel(
                body, text=label,
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), anchor="w",
            ).grid(row=i * 2, column=0, sticky="w", pady=(0 if i == 0 else 8, 4))

            e = ctk.CTkEntry(
                body, height=42,
                font=ctk.CTkFont(family="Segoe UI", size=14), corner_radius=8,
            )
            e.insert(0, val)
            e.grid(row=i * 2 + 1, column=0, sticky="ew")
            entries[label] = e

        status_lbl = ctk.CTkLabel(
            body, text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        status_lbl.grid(row=6, column=0, sticky="w", pady=(8, 0))

        def _do_edit():
            new_name  = entries["Part Name"].get().strip()
            new_brand = entries["Brand"].get().strip()
            raw_cost  = entries["Unit Cost"].get().strip()

            if not new_name:
                status_lbl.configure(text="Part name is required.", text_color="#e05c5c")
                return
            try:
                new_cost = float(raw_cost)
                if new_cost < 0:
                    raise ValueError
            except ValueError:
                status_lbl.configure(text="Enter a valid unit cost.", text_color="#e05c5c")
                return

            conn = sqlite3.connect('repair_erp.db')
            c = conn.cursor()
            try:
                c.execute(
                    "UPDATE Parts_Inventory SET part_name=?, brand_compatibility=?, unit_cost=? WHERE part_id=?",
                    (new_name, new_brand, new_cost, part_id)
                )
                from datetime import datetime
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute(
                    "INSERT INTO AuditLogs (user_id, action_type, target_id, timestamp, notes) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (self.app.session.get("id"), 'Inventory: Part Edited', f"PART-{part_id}", now,
                     f"Edited part P-{part_id:04d}: name='{new_name}', brand='{new_brand}', cost=Rs.{new_cost:.2f}")
                )
                conn.commit()
                messagebox.showinfo("Updated", f"Part P-{part_id:04d} updated successfully.")
                popup.destroy()
                self.refresh_inventory()
            except Exception as ex:
                status_lbl.configure(text=str(ex), text_color="#e05c5c")
            finally:
                conn.close()

        ctk.CTkButton(
            body, text="💾  Save Changes", height=44,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            corner_radius=10,
            command=_do_edit,
        ).grid(row=7, column=0, sticky="ew", pady=(0, 0))

    def _show_add_part_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add New Part Type")
        popup.geometry("480x500")
        popup.resizable(False, False)
        popup.grab_set()
        popup.lift()
        popup.focus_force()

        popup.grid_columnconfigure(0, weight=1)

        banner = ctk.CTkFrame(popup, fg_color=("#27ae60", "#1e8449"), corner_radius=0, height=54)
        banner.grid(row=0, column=0, sticky="ew")
        banner.grid_propagate(False)
        banner.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            banner, text="＋  Add New Part Type",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="white", anchor="w",
        ).grid(row=0, column=0, padx=18, sticky="w")

        body = ctk.CTkFrame(popup, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        body.grid_columnconfigure(0, weight=1)

        labels = ["Part Name", "Brand / Compatibility", "Unit Cost (Rs.)", "Initial Stock"]
        placeholders = [
            "e.g. iPhone 16 Screen",
            "e.g. Apple",
            "e.g. 2500.00",
            "e.g. 10",
        ]
        entries: dict[str, ctk.CTkEntry] = {}

        for i, (label, ph) in enumerate(zip(labels, placeholders)):
            ctk.CTkLabel(
                body, text=label,
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), anchor="w",
            ).grid(row=i * 2, column=0, sticky="w", pady=(0 if i == 0 else 8, 4))

            e = ctk.CTkEntry(
                body, height=42, placeholder_text=ph,
                font=ctk.CTkFont(family="Segoe UI", size=14), corner_radius=8,
            )
            e.grid(row=i * 2 + 1, column=0, sticky="ew")
            entries[label] = e

        status_lbl = ctk.CTkLabel(
            body, text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        status_lbl.grid(row=8, column=0, sticky="w", pady=(8, 0))

        def _do_add():
            name  = entries["Part Name"].get().strip()
            brand = entries["Brand / Compatibility"].get().strip()
            raw_cost  = entries["Unit Cost (Rs.)"].get().strip()
            raw_stock = entries["Initial Stock"].get().strip()

            if not name:
                status_lbl.configure(text="Part name is required.", text_color="#e05c5c")
                return
            if not brand:
                status_lbl.configure(text="Brand is required.", text_color="#e05c5c")
                return
            try:
                cost = float(raw_cost)
                if cost < 0:
                    raise ValueError
            except ValueError:
                status_lbl.configure(text="Enter a valid unit cost.", text_color="#e05c5c")
                return
            try:
                stock = int(raw_stock)
                if stock < 0:
                    raise ValueError
            except ValueError:
                status_lbl.configure(text="Enter a valid stock quantity.", text_color="#e05c5c")
                return

            result = self.app.api.add_new_part_type(
                admin_id=self.app.session.get("id"),
                name=name, brand=brand, cost=cost, initial_stock=stock,
            )

            if result["status"] == "success":
                messagebox.showinfo(
                    "Part Added",
                    f"New part \"{name}\" (P-{result['part_id']:04d}) added with {stock} units."
                )
                popup.destroy()
                self.refresh_inventory()
            else:
                status_lbl.configure(
                    text=result.get("message", "Failed to add part."),
                    text_color="#e05c5c",
                )

        ctk.CTkButton(
            body, text="✔  Add to Inventory", height=46,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            corner_radius=10,
            fg_color=("#27ae60", "#1e8449"),
            hover_color=("#229954", "#1a7640"),
            command=_do_add,
        ).grid(row=9, column=0, sticky="ew", pady=(10, 0))

class DonorBoardTab(ctk.CTkFrame):
    def __init__(self, parent, app: "RepairERP", admin_view: "AdminView"):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.admin_view = admin_view

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

                                                                        
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=28, pady=(22, 0))
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr, text="📱  Register Donor Board",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"), anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            hdr,
            text="Identify the dead device, load its part template, tick what's salvageable, then register.",
            font=ctk.CTkFont(family="Segoe UI", size=14), text_color="gray", anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(2, 14))

                                                                        
                                          
                                                                        
        box1 = ctk.CTkFrame(self, corner_radius=14, border_width=1)
        box1.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 10))
        box1.grid_columnconfigure((0, 1, 2, 3), weight=1)

                            
        b1_hdr = ctk.CTkFrame(box1, corner_radius=0, height=46,
                               fg_color=("gray86", "gray20"))
        b1_hdr.grid(row=0, column=0, columnspan=4, sticky="ew")
        b1_hdr.grid_propagate(False)
        b1_hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            b1_hdr, text="📋  Board Details",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), anchor="w",
        ).grid(row=0, column=0, padx=18, sticky="w")

                                                           
        self._db_entries: dict[str, ctk.CTkEntry] = {}
        _fields = [
            ("Brand",               "e.g.  Apple",             0),
            ("Model",               "e.g.  iPhone 13",         1),
            ("Serial Number / IMEI","e.g.  F2LXX000XXXX",      2),
            ("Acquisition Cost (Rs.)","e.g.  3500",            3),
        ]
        for label, ph, col in _fields:
            cell = ctk.CTkFrame(box1, fg_color="transparent")
            cell.grid(row=1, column=col, sticky="ew",
                      padx=(18 if col == 0 else 8, 18 if col == 3 else 8),
                      pady=(12, 14))
            cell.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                cell, text=label,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), anchor="w",
            ).grid(row=0, column=0, sticky="w", pady=(0, 3))
            e = ctk.CTkEntry(cell, height=40, placeholder_text=ph,
                             font=ctk.CTkFont(family="Segoe UI", size=13),
                             corner_radius=8)
            e.grid(row=1, column=0, sticky="ew")
            self._db_entries[label] = e

                                                                              
        ctk.CTkButton(
            box1, text="🔍  Load Template", height=40, width=150,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=8,
            fg_color=("gray70", "gray30"), hover_color=("gray60", "gray35"),
            command=self._db_load_template,
        ).grid(row=2, column=3, padx=(8, 18), pady=(0, 14), sticky="e")

                                                                        
                                            
                                                                        
        box2 = ctk.CTkFrame(self, corner_radius=14, border_width=1)
        box2.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 8))
        box2.grid_columnconfigure(0, weight=1)
        box2.grid_rowconfigure(1, weight=1)

                            
        b2_hdr = ctk.CTkFrame(box2, corner_radius=0, height=46,
                               fg_color=("gray86", "gray20"))
        b2_hdr.grid(row=0, column=0, sticky="ew")
        b2_hdr.grid_propagate(False)
        b2_hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            b2_hdr, text="🔩  Harvest Checklist  -  Tick parts that are salvageable",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), anchor="w",
        ).grid(row=0, column=0, padx=18, sticky="w")

                                        
        col_hdr = ctk.CTkFrame(box2, fg_color=("gray82", "gray22"), height=34, corner_radius=0)
        col_hdr.grid(row=1, column=0, sticky="ew")
        col_hdr.grid_propagate(False)
        _col_labels = [("", 42), ("Part Name", 280), ("Est. Value", 130), ("Source", 100)]
        _cx = 0
        for txt, w in _col_labels:
            ctk.CTkLabel(col_hdr, text=txt, width=w,
                         font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                         anchor="w").place(x=_cx + 8, rely=0.5, anchor="w")
            _cx += w

                                    
        self._db_checklist_scroll = ctk.CTkScrollableFrame(
            box2, corner_radius=0, fg_color=("gray96", "gray14"))
        self._db_checklist_scroll.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        self._db_checklist_scroll.grid_columnconfigure(0, weight=1)

                     
        self._db_checklist_placeholder = ctk.CTkLabel(
            self._db_checklist_scroll,
            text="Enter a Brand and Model above, then click  🔍 Load Template.",
            font=ctk.CTkFont(family="Segoe UI", size=13), text_color=("gray55", "gray55"),
        )
        self._db_checklist_placeholder.grid(row=0, column=0, pady=40)

                                                                                        
        self._db_checklist_items: list[dict] = []

                                 
        self._db_status_lbl = ctk.CTkLabel(
            box2, text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self._db_status_lbl.grid(row=3, column=0, sticky="w", padx=18, pady=(4, 0))

                                                          
        actions_row = ctk.CTkFrame(box2, fg_color="transparent")
        actions_row.grid(row=4, column=0, sticky="ew", padx=18, pady=(4, 12))

        self._db_add_missing_btn = ctk.CTkButton(
            actions_row, text="＋  Add Missing Part", width=180, height=36,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=8, state="disabled",
            fg_color=("gray70", "gray30"), hover_color=("gray60", "gray35"),
            command=self._db_add_part_dialog,
        )
        self._db_add_missing_btn.pack(side="left", padx=(0, 10))

        self._db_select_all_btn = ctk.CTkButton(
            actions_row, text="☑  Select All", width=120, height=36,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            corner_radius=8, state="disabled",
            fg_color=("gray70", "gray30"), hover_color=("gray60", "gray35"),
            command=lambda: self._db_toggle_all(True),
        )
        self._db_select_all_btn.pack(side="left", padx=(0, 6))

        self._db_deselect_all_btn = ctk.CTkButton(
            actions_row, text="☐  Deselect All", width=130, height=36,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            corner_radius=8, state="disabled",
            fg_color=("gray70", "gray30"), hover_color=("gray60", "gray35"),
            command=lambda: self._db_toggle_all(False),
        )
        self._db_deselect_all_btn.pack(side="left")

                                                                        
                             
                                                                        
        self._db_register_btn = ctk.CTkButton(
            self,
            text="✅  Confirm & Register Donor Board",
            height=54, state="disabled",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            corner_radius=12,
            fg_color=("gray60", "gray35"),
            hover_color=("gray50", "gray30"),
            command=self._do_register_donor_board,
        )
        self._db_register_btn.grid(row=3, column=0, sticky="ew", padx=28, pady=(4, 22))

                                                              
        self._db_loaded_model: str = ""
        self._db_loaded_brand: str = ""

    def _db_load_template(self):
        brand = self._db_entries["Brand"].get().strip()
        model = self._db_entries["Model"].get().strip()

        if not brand or not model:
            self._db_status_lbl.configure(
                text="⚠  Please fill in both Brand and Model before loading a template.",
                text_color="#e67e22")
            return

        self._db_status_lbl.configure(text="")
        res = self.app.api.get_model_template(brand, model)

        if res["status"] != "success":
            self._db_status_lbl.configure(
                text=f"Error: {res.get('message')}", text_color="#e05c5c")
            return

        parts = res["data"]
        if not parts:
            self._db_status_lbl.configure(
                text=f'ℹ  No template found for "{model}". Opening Template Builder…',
                text_color="#3498db")
            self.after(200, lambda: self._db_show_new_template_popup(brand, model))
        else:
            self._db_loaded_brand = brand
            self._db_loaded_model = model
            self._db_populate_checklist(parts)
            self._db_status_lbl.configure(
                text=f"✓  Loaded {len(parts)} parts from template for {brand} {model}.",
                text_color="#27ae60")

    def _db_populate_checklist(self, parts: list[dict], append: bool = False):
        frame = self._db_checklist_scroll

        if not append:
            for item in self._db_checklist_items:
                item["row_frame"].destroy()
            self._db_checklist_items.clear()
            self._db_checklist_placeholder.grid_remove()

        for part in parts:
            idx = len(self._db_checklist_items)
            bg = ("gray93", "gray18") if idx % 2 == 0 else ("gray88", "gray22")
            row = ctk.CTkFrame(frame, fg_color=bg, corner_radius=8, height=44)
            row.grid(row=idx, column=0, sticky="ew", pady=2, padx=4)
            row.grid_propagate(False)

            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(
                row, text="", variable=var, width=32,
                checkbox_width=20, checkbox_height=20,
                fg_color=("#27ae60", "#1e8449"),
                hover_color=("#229954", "#1a7640"),
            )
            cb.place(x=10, rely=0.5, anchor="w")

            ctk.CTkLabel(
                row, text=part["part_name"], width=280,
                font=ctk.CTkFont(family="Segoe UI", size=14), anchor="w",
            ).place(x=50, rely=0.5, anchor="w")

            est = part.get("estimated_value", 0.0)
            ctk.CTkLabel(
                row, text=f"Rs. {float(est):.0f}", width=130,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=("#27ae60", "#2ecc71"), anchor="w",
            ).place(x=330, rely=0.5, anchor="w")

            source = part.get("source", "Template")
            src_color = "#3498db" if source == "Template" else "#e67e22"
            ctk.CTkLabel(
                row,
                text=f"  {source}  ",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                fg_color=src_color, text_color="white", corner_radius=6,
            ).place(x=462, rely=0.5, anchor="w")

            self._db_checklist_items.append({
                "var": var, "part_name": part["part_name"],
                "est_value": float(est), "row_frame": row,
                "source": source,
            })

        for btn in (self._db_add_missing_btn, self._db_select_all_btn,
                    self._db_deselect_all_btn):
            btn.configure(state="normal")

        self._db_register_btn.configure(
            state="normal",
            fg_color=("green3", "#1e8449"),
            hover_color=("#229954", "#1a7640"),
        )

    def _db_toggle_all(self, checked: bool):
        for item in self._db_checklist_items:
            item["var"].set(checked)

    def _db_add_part_dialog(self):
        if not self._db_loaded_model:
            self._db_status_lbl.configure(
                text="Load a template first before adding missing parts.",
                text_color="#e05c5c")
            return

        dlg = ctk.CTkToplevel(self)
        dlg.title("Add Missing Part")
        dlg.geometry("440x350")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.lift()
        dlg.focus_force()
        dlg.grid_columnconfigure(0, weight=1)

        banner = ctk.CTkFrame(dlg, fg_color=("#e67e22", "#d35400"),
                               corner_radius=0, height=50)
        banner.grid(row=0, column=0, sticky="ew")
        banner.grid_propagate(False)
        banner.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            banner, text="＋  Add Missing Part to Template",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="white", anchor="w",
        ).grid(row=0, column=0, padx=18, sticky="w")

        body = ctk.CTkFrame(dlg, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=22, pady=16)
        body.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(body, text="Part Name *",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 3))
        name_e = ctk.CTkEntry(body, height=40,
                               placeholder_text="e.g.  Taptic Engine",
                               font=ctk.CTkFont(family="Segoe UI", size=13),
                               corner_radius=8)
        name_e.grid(row=1, column=0, sticky="ew")

        ctk.CTkLabel(body, text="Estimated Value (Rs.) *",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").grid(row=2, column=0, sticky="w", pady=(10, 3))
        val_e = ctk.CTkEntry(body, height=40,
                              placeholder_text="e.g.  800",
                              font=ctk.CTkFont(family="Segoe UI", size=13),
                              corner_radius=8)
        val_e.grid(row=3, column=0, sticky="ew")

        err_lbl = ctk.CTkLabel(body, text="",
                                font=ctk.CTkFont(family="Segoe UI", size=12))
        err_lbl.grid(row=4, column=0, sticky="w", pady=(6, 0))

        def _save():
            pname = name_e.get().strip()
            raw   = val_e.get().strip()
            if not pname:
                err_lbl.configure(text="Part name is required.", text_color="#e05c5c")
                return
            try:
                est = float(raw)
                if est < 0:
                    raise ValueError
            except ValueError:
                err_lbl.configure(text="Enter a valid positive value (or 0).",
                                   text_color="#e05c5c")
                return

            result = self.app.api.add_part_to_template(
                brand=self._db_loaded_brand,
                model=self._db_loaded_model,
                part_name=pname,
                estimated_value=est,
            )
            if result["status"] != "success":
                err_lbl.configure(
                    text=result.get("message", "Failed to save."),
                    text_color="#e05c5c")
                return

            self._db_populate_checklist(
                [{"part_name": pname, "estimated_value": est, "source": "Added"}],
                append=True,
            )
            self._db_status_lbl.configure(
                text=f'✓  "{pname}" added to template and checklist.',
                text_color="#27ae60")
            dlg.destroy()

        ctk.CTkButton(
            body, text="💾  Save & Add to List", height=42,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            corner_radius=8,
            fg_color=("#e67e22", "#d35400"),
            hover_color=("#d35400", "#b03000"),
            command=_save,
        ).grid(row=5, column=0, sticky="ew", pady=(10, 0))

    def _db_show_new_template_popup(self, brand: str, model: str):
        popup = ctk.CTkToplevel(self)
        popup.title(f"New Template - {brand} {model}")
        popup.geometry("600x620")
        popup.minsize(520, 500)
        popup.grab_set()
        popup.lift()
        popup.focus_force()
        popup.grid_rowconfigure(1, weight=1)
        popup.grid_columnconfigure(0, weight=1)

        banner = ctk.CTkFrame(popup, fg_color=("#3498db", "#2471a3"),
                               corner_radius=0, height=60)
        banner.grid(row=0, column=0, sticky="ew")
        banner.grid_propagate(False)
        banner.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            banner, text=f"🆕  Define Default Template for: {brand} {model}",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="white", anchor="w",
        ).grid(row=0, column=0, padx=18, sticky="w")
        ctk.CTkLabel(
            banner,
            text="These parts become the standard baseline for every future board of this model.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("#dde", "#ccd"), anchor="w",
        ).grid(row=1, column=0, padx=18, sticky="w")

        body = ctk.CTkFrame(popup, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=22, pady=16)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(4, weight=1)

        input_row = ctk.CTkFrame(body, fg_color="transparent")
        input_row.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        input_row.grid_columnconfigure(0, weight=2)
        input_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(input_row, text="Part Name",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 3))
        ctk.CTkLabel(input_row, text="Est. Value (Rs.)",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                     anchor="w").grid(row=0, column=1, sticky="w", padx=(8, 0), pady=(0, 3))

        tp_name_e = ctk.CTkEntry(input_row, height=40,
                                  placeholder_text="e.g.  OLED Screen",
                                  font=ctk.CTkFont(family="Segoe UI", size=13),
                                  corner_radius=8)
        tp_name_e.grid(row=1, column=0, sticky="ew")

        tp_val_e = ctk.CTkEntry(input_row, height=40, width=140,
                                 placeholder_text="e.g.  4500",
                                 font=ctk.CTkFont(family="Segoe UI", size=13),
                                 corner_radius=8)
        tp_val_e.grid(row=1, column=1, sticky="ew", padx=(8, 0))

        err_lbl = ctk.CTkLabel(body, text="",
                                font=ctk.CTkFont(family="Segoe UI", size=12))
        err_lbl.grid(row=2, column=0, sticky="w")

        ctk.CTkFrame(body, height=1, fg_color=("gray75", "gray35"),
                     corner_radius=0).grid(row=3, column=0, sticky="ew", pady=(0, 6))

        staged_scroll = ctk.CTkScrollableFrame(body, corner_radius=8,
                                                fg_color=("gray96", "gray15"))
        staged_scroll.grid(row=4, column=0, sticky="nsew")
        staged_scroll.grid_columnconfigure(0, weight=1)

        tp_staged_placeholder = ctk.CTkLabel(
            staged_scroll,
            text="No parts defined yet.  Add at least one part above.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=("gray55", "gray55"),
        )
        tp_staged_placeholder.grid(row=0, column=0, pady=20)

        tp_staged: list[dict] = []

        def _tp_add():
            pname = tp_name_e.get().strip()
            raw   = tp_val_e.get().strip()
            if not pname:
                err_lbl.configure(text="Part name is required.", text_color="#e05c5c")
                return
            try:
                est = float(raw) if raw else 0.0
                if est < 0:
                    raise ValueError
            except ValueError:
                err_lbl.configure(text="Enter a valid value (≥ 0).", text_color="#e05c5c")
                return

            err_lbl.configure(text="")
            tp_staged_placeholder.grid_remove()

            idx = len(tp_staged)
            bg = ("gray90", "gray19") if idx % 2 == 0 else ("gray85", "gray23")
            row = ctk.CTkFrame(staged_scroll, fg_color=bg, corner_radius=8, height=40)
            row.grid(row=idx, column=0, sticky="ew", pady=2, padx=4)
            row.grid_propagate(False)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text=f"  {idx+1}.",
                         font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                         text_color=("gray45", "gray60"),
                         width=30, anchor="e").grid(row=0, column=0, padx=(6, 4), sticky="e")
            ctk.CTkLabel(row, text=pname,
                         font=ctk.CTkFont(family="Segoe UI", size=13), anchor="w",
                         ).grid(row=0, column=1, sticky="w")
            ctk.CTkLabel(row, text=f"Rs. {est:.0f}",
                         font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                         text_color=("#27ae60", "#2ecc71"), width=110, anchor="e",
                         ).grid(row=0, column=2, padx=(0, 8), sticky="e")

            tp_staged.append({"part_name": pname, "estimated_value": est, "row_frame": row})
            tp_name_e.delete(0, "end")
            tp_val_e.delete(0, "end")
            tp_name_e.focus()

        add_btn = ctk.CTkButton(
            body, text="＋  Add to Template", height=38,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=8,
            fg_color=("gray70", "gray30"), hover_color=("gray60", "gray35"),
            command=_tp_add
        )
        add_btn.grid(row=1, column=0, sticky="w", pady=(0, 10))

        tp_name_e.bind("<Return>", lambda e: _tp_add())
        tp_val_e.bind("<Return>",  lambda e: _tp_add())

        def _tp_save():
            if not tp_staged:
                err_lbl.configure(
                    text="Add at least one part to the template before saving.",
                    text_color="#e05c5c")
                return

            parts = [{"part_name": p["part_name"],
                      "estimated_value": p["estimated_value"]} for p in tp_staged]

            res = self.app.api.create_model_template(brand=brand, model=model, parts=parts)
            if res["status"] != "success":
                err_lbl.configure(
                    text=res.get("message", "Failed to save template."),
                    text_color="#e05c5c")
                return

            popup.destroy()
            self._db_loaded_brand = brand
            self._db_loaded_model = model
            populated = [{"part_name": p["part_name"],
                          "estimated_value": p["estimated_value"],
                          "source": "Template"} for p in parts]
            self._db_populate_checklist(populated)
            self._db_status_lbl.configure(
                text=f"✓  New template for {brand} {model} saved. {len(parts)} parts loaded.",
                text_color="#27ae60")

        ctk.CTkButton(
            popup, text="💾  Save Master Template",
            height=50,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            corner_radius=0,
            fg_color=("#3498db", "#2471a3"),
            hover_color=("#2980b9", "#1f618d"),
            command=_tp_save,
        ).grid(row=2, column=0, sticky="ew", padx=0, pady=(8, 0))

    def _do_register_donor_board(self):
        brand  = self._db_entries["Brand"].get().strip()
        model  = self._db_entries["Model"].get().strip()
        serial = self._db_entries["Serial Number / IMEI"].get().strip()
        raw_cost = self._db_entries["Acquisition Cost (Rs.)"].get().strip()

        if not brand:
            self._db_status_lbl.configure(text="Brand is required.", text_color="#e05c5c"); return
        if not model:
            self._db_status_lbl.configure(text="Model is required.", text_color="#e05c5c"); return
        if not serial:
            self._db_status_lbl.configure(
                text="Serial Number / IMEI is required.", text_color="#e05c5c"); return
        try:
            cost = float(raw_cost)
            if cost < 0:
                raise ValueError
        except ValueError:
            self._db_status_lbl.configure(
                text="Enter a valid Acquisition Cost (≥ 0).", text_color="#e05c5c"); return

        selected = [
            {"part_name": it["part_name"], "est_value": it["est_value"]}
            for it in self._db_checklist_items if it["var"].get()
        ]
        if not selected:
            self._db_status_lbl.configure(
                text="⚠  Select at least one salvageable part before registering.",
                text_color="#e67e22")
            return

        result = self.app.api.register_donor_board(
            admin_id=self.app.session.get("id"),
            brand=brand, model=model,
            serial_number=serial,
            acquisition_cost=cost,
            selected_components=selected,
        )

        if result["status"] == "success":
            bid  = result["board_id"]
            cnt  = result["components_added"]
            messagebox.showinfo(
                "Board Registered",
                f"✔  Donor Board DB-{bid:04d} registered!\n\n"
                f"   {cnt} component(s) are now in the donor pool.",
            )
            for e in self._db_entries.values():
                e.delete(0, "end")
            for it in self._db_checklist_items:
                it["row_frame"].destroy()
            self._db_checklist_items.clear()
            self._db_loaded_model = ""
            self._db_loaded_brand = ""
            self._db_checklist_placeholder.grid(row=0, column=0, pady=40)
            for btn in (self._db_add_missing_btn, self._db_select_all_btn,
                        self._db_deselect_all_btn):
                btn.configure(state="disabled")
            self._db_register_btn.configure(
                state="disabled",
                fg_color=("gray60", "gray35"),
                hover_color=("gray50", "gray30"),
            )
            self._db_status_lbl.configure(
                text=f"✓  Board DB-{bid:04d} registered with {cnt} component(s).",
                text_color="#27ae60")
        else:
            self._db_status_lbl.configure(
                text=result.get("message", "Registration failed."),
                text_color="#e05c5c")
