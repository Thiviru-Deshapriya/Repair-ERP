import customtkinter as ctk
from tkinter import messagebox

_PART_STATUS_COLORS = {
    "Draft": "#3498db", "Installed": "#e67e22", "Confirmed": "#27ae60"
}

class InProgressTab(ctk.CTkFrame):
    def __init__(self, master, app, dashboard, on_ticket_completed):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.dashboard = dashboard
        self.on_ticket_completed = on_ticket_completed
        self.active_ticket = None
        self._init_ui()

    def _init_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

                                                                         
        banner = ctk.CTkFrame(self, corner_radius=10, border_width=1,
                              fg_color=("gray92", "gray18"))
        banner.grid(row=0, column=0, columnspan=2, sticky="ew",
                    padx=24, pady=(18, 10))
        banner.grid_columnconfigure(0, weight=1)

        self._ip_ticket_label = ctk.CTkLabel(
            banner,
            text="No ticket selected \u2014 go to My Tickets and click Manage Parts.",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color="gray", anchor="w",
        )
        self._ip_ticket_label.grid(row=0, column=0, padx=20, pady=14, sticky="w")

                                                                         
        left = ctk.CTkFrame(self, corner_radius=12, border_width=1)
        left.grid(row=1, column=0, sticky="nsew", padx=(24, 10), pady=(0, 10))
        left.grid_rowconfigure(2, weight=1)
        left.grid_columnconfigure(0, weight=1)

        left_hdr = ctk.CTkFrame(left, fg_color=("gray85", "gray20"),
                                height=52, corner_radius=0)
        left_hdr.grid(row=0, column=0, sticky="ew")
        left_hdr.grid_propagate(False)
        ctk.CTkLabel(left_hdr, text="\U0001f4e6  New Parts (Inventory)",
                     font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                     anchor="w",
                     ).grid(row=0, column=0, padx=16, sticky="w")

        self._new_search = ctk.CTkEntry(
            left, placeholder_text="Search parts\u2026",
            height=42, font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=8,
        )
        self._new_search.grid(row=1, column=0, padx=12, pady=8, sticky="ew")
        self._new_search.bind("<KeyRelease>", lambda e: self._search_new_parts())

        self._new_parts_scroll = ctk.CTkScrollableFrame(left, corner_radius=6)
        self._new_parts_scroll.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self._new_parts_scroll.grid_columnconfigure(0, weight=1)

                                                                         
        right = ctk.CTkFrame(self, corner_radius=12, border_width=1)
        right.grid(row=1, column=1, sticky="nsew", padx=(10, 24), pady=(0, 10))
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        right_hdr = ctk.CTkFrame(right, fg_color=("gray85", "gray20"),
                                 height=52, corner_radius=0)
        right_hdr.grid(row=0, column=0, sticky="ew")
        right_hdr.grid_propagate(False)
        ctk.CTkLabel(right_hdr, text="\U0001f9e9  Donor Components",
                     font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                     anchor="w",
                     ).grid(row=0, column=0, padx=16, sticky="w")

        self._donor_search = ctk.CTkEntry(
            right, placeholder_text="Search donor parts\u2026",
            height=42, font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=8,
        )
        self._donor_search.grid(row=1, column=0, padx=12, pady=8, sticky="ew")
        self._donor_search.bind("<KeyRelease>", lambda e: self._search_donor_parts())

        self._donor_parts_scroll = ctk.CTkScrollableFrame(right, corner_radius=6)
        self._donor_parts_scroll.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self._donor_parts_scroll.grid_columnconfigure(0, weight=1)

                                                                         
        bottom = ctk.CTkFrame(self, corner_radius=12, border_width=1)
        bottom.grid(row=2, column=0, columnspan=2, sticky="ew",
                    padx=24, pady=(0, 16))
        bottom.grid_columnconfigure(0, weight=1)

        alloc_hdr = ctk.CTkFrame(bottom, fg_color=("gray85", "gray20"),
                                 height=52, corner_radius=0)
        alloc_hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        alloc_hdr.grid_propagate(False)
        alloc_hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(alloc_hdr, text="\U0001f4cb  Parts Allocated to This Ticket",
                     font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                     anchor="w",
                     ).grid(row=0, column=0, padx=16, sticky="w")
        ctk.CTkButton(alloc_hdr, text="Refresh", width=100, height=34,
                      font=ctk.CTkFont(family="Segoe UI", size=13),
                      fg_color="transparent", border_width=1,
                      command=self._refresh_allocated_parts,
                      ).grid(row=0, column=1, padx=17)

        self._ip_total_cost_label = ctk.CTkLabel(
            alloc_hdr, text="Total Parts Cost: Rs.0.00",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#e67e22"
        )
        self._ip_total_cost_label.grid(row=0, column=2, padx=20, sticky="e")
        alloc_hdr.grid_columnconfigure(2, weight=1)                                         

        self._allocated_scroll = ctk.CTkScrollableFrame(bottom, height=170, corner_radius=6)
        self._allocated_scroll.grid(row=1, column=0, columnspan=2,
                                    sticky="ew", padx=12, pady=8)
        self._allocated_scroll.grid_columnconfigure(0, weight=1)

                                   
        actions = ctk.CTkFrame(bottom, fg_color="transparent")
        actions.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))

        ctk.CTkLabel(actions, text="Service Charge (Rs.):",
                     font=ctk.CTkFont(family="Segoe UI", size=15),
                     ).grid(row=0, column=0, padx=(0, 10))

        self._ip_charge_entry = ctk.CTkEntry(
            actions, placeholder_text="e.g. 2500",
            width=190, height=46, corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=15),
        )
        self._ip_charge_entry.grid(row=0, column=1, padx=(0, 14))

        ctk.CTkButton(
            actions, text="\u2713  Finalize & Complete Ticket",
            height=46, width=290,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            corner_radius=8, fg_color="#27ae60", hover_color="#1e8449",
            command=self._do_complete_ticket,
        ).grid(row=0, column=2, padx=4)

        self._ip_status = ctk.CTkLabel(
            actions, text="", font=ctk.CTkFont(family="Segoe UI", size=15))
        self._ip_status.grid(row=0, column=3, padx=16)

    def set_ticket(self, ticket):
        self.active_ticket = ticket
        self._refresh_inprogress()

    def reset_state(self):
        self.active_ticket = None
        self._ip_ticket_label.configure(
            text="No ticket selected \u2014 go to My Tickets and click Manage Parts.",
            text_color="gray",
        )
        self._ip_charge_entry.delete(0, "end")
        self._ip_status.configure(text="")
        self._new_search.delete(0, "end")
        self._donor_search.delete(0, "end")
        for w in self._allocated_scroll.winfo_children():
            w.destroy()

    def _refresh_inprogress(self):
        if not self.active_ticket:
            self._ip_ticket_label.configure(
                text="No ticket selected \u2014 go to My Tickets and click Manage Parts.",
                text_color="gray",
            )
            return
        t = self.active_ticket
        self._ip_ticket_label.configure(
            text=(f"  Ticket {t['id']}  \u2022  {t['device']}"
                  f"  \u2022  Issue: {t['issue']}  \u2022  Status: {t['status']}"),
            text_color=("gray20", "gray80"),
        )
        self._search_new_parts()
        self._search_donor_parts()
        self._refresh_allocated_parts()

    def _search_new_parts(self):
        term = self._new_search.get().strip()
        res  = self.app.api.search_new_inventory(term)
        frame = self._new_parts_scroll
        for w in frame.winfo_children():
            w.destroy()

        if res["status"] != "success" or not res["data"]:
            self.dashboard.empty_label(frame, "No parts in inventory.")
            return

        for idx, p in enumerate(res["data"]):
            row = ctk.CTkFrame(
                frame,
                fg_color=("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23"),
                corner_radius=6, height=42,
            )
            row.grid(row=idx, column=0, sticky="ew", pady=2)
            row.grid_propagate(False)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                row,
                text=f"{p['name']}  [{p['compatibility']}]  Rs.{p['cost']:.0f}  (stock: {p['stock']})",
                font=ctk.CTkFont(family="Segoe UI", size=13), anchor="w",
            ).grid(row=0, column=0, padx=12, sticky="w")

            ctk.CTkButton(row, text="+ Add", width=80, height=30,
                          font=ctk.CTkFont(family="Segoe UI", size=13),
                          corner_radius=6,
                          command=lambda part=p: self._draft_new_part(part),
                          ).grid(row=0, column=1, padx=8)

    def _search_donor_parts(self):
        term = self._donor_search.get().strip()
        res  = self.app.api.search_donor_inventory(term)
        frame = self._donor_parts_scroll
        for w in frame.winfo_children():
            w.destroy()

        if res["status"] != "success" or not res["data"]:
            self.dashboard.empty_label(frame, "No donor parts available.")
            return

        for idx, p in enumerate(res["data"]):
            row = ctk.CTkFrame(
                frame,
                fg_color=("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23"),
                corner_radius=6, height=42,
            )
            row.grid(row=idx, column=0, sticky="ew", pady=2)
            row.grid_propagate(False)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                row,
                text=f"{p['name']}  \u2014 {p['source_brand']} {p['source_model']} ({p['source_serial']})",
                font=ctk.CTkFont(family="Segoe UI", size=13), anchor="w",
            ).grid(row=0, column=0, padx=12, sticky="w")

            ctk.CTkButton(row, text="+ Add", width=80, height=30,
                          font=ctk.CTkFont(family="Segoe UI", size=13),
                          fg_color="#9b59b6", hover_color="#7d3c98",
                          corner_radius=6,
                          command=lambda part=p: self._draft_donor_part(part),
                          ).grid(row=0, column=1, padx=(8, 4))

            ctk.CTkButton(row, text="\U0001f6a9 Flag", width=84, height=30,
                          font=ctk.CTkFont(family="Segoe UI", size=13),
                          fg_color="#c0392b", hover_color="#922b21",
                          corner_radius=6,
                          command=lambda part=p: self._show_flag_dialog(part),
                          ).grid(row=0, column=2, padx=(0, 8))

    def _show_flag_dialog(self, part: dict):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Flag Component as Damaged")
        dialog.geometry("480x340")
        dialog.resizable(False, False)
        dialog.grab_set()                                            
        dialog.lift()
        dialog.focus_force()

                                                                                     
        hdr = ctk.CTkFrame(dialog, fg_color="#c0392b", corner_radius=0, height=54)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(
            hdr,
            text="\U0001f6a9  Flag Component as Damaged",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="white", anchor="w",
        ).pack(side="left", padx=18, pady=14)

                                                                                    
        info_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        info_frame.pack(fill="x", padx=22, pady=(16, 0))
        ctk.CTkLabel(
            info_frame,
            text=f"Part  :  {part['name']}",
            font=ctk.CTkFont(family="Segoe UI", size=14), anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            info_frame,
            text=f"Source:  {part['source_brand']} {part['source_model']}  ({part['source_serial']})",
            font=ctk.CTkFont(family="Segoe UI", size=13), text_color="gray", anchor="w",
        ).pack(fill="x", pady=(2, 0))

                                                                                   
        ctk.CTkLabel(
            dialog,
            text="Technician Notes  (required):",
            font=ctk.CTkFont(family="Segoe UI", size=14), anchor="w",
        ).pack(fill="x", padx=22, pady=(18, 4))

        notes_box = ctk.CTkTextbox(
            dialog, height=80,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            corner_radius=8, border_width=1,
        )
        notes_box.pack(fill="x", padx=22)

                                                                                  
        status_lbl = ctk.CTkLabel(
            dialog, text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            wraplength=430, anchor="w",
        )

        def _submit():
            notes = notes_box.get("1.0", "end").strip()
            if not notes:
                status_lbl.configure(
                    text="Please enter technician notes before flagging.",
                    text_color="#e05c5c"
                )
                return

            result = self.app.api.flag_donor_part(
                tech_id=self.app.session.get("id"),
                component_id=part["id"],
                notes=notes,
            )

            if result["status"] == "success":
                status_lbl.configure(
                    text=result["message"],
                    text_color="#27ae60"
                )
                self._search_donor_parts()
                dialog.after(1800, dialog.destroy)
            else:
                status_lbl.configure(
                    text=result.get("message", "An unexpected error occurred."),
                    text_color="#e05c5c"
                )

                                                                                   
        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(fill="x", padx=22, pady=(12, 0))

        ctk.CTkButton(
            btn_row, text="\U0001f6a9  Confirm Flag",
            width=160, height=48,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#c0392b", hover_color="#922b21", corner_radius=8,
            command=_submit,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row, text="Cancel",
            width=110, height=48,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="transparent", border_width=1,
            corner_radius=8,
            command=dialog.destroy,
        ).pack(side="right", padx=(12, 0))

                                                                                   
        status_lbl.pack(fill="x", padx=22, pady=(12, 10))

    def _draft_new_part(self, part: dict):
        if not self.active_ticket:
            messagebox.showwarning("No Ticket", "Select a ticket from My Tickets first.")
            return
        result = self.app.api.allocate_draft_parts(
            tech_id=self.app.session.get("id"),
            ticket_raw_id=self.active_ticket["raw_id"],
            parts_data=[{"type": "new", "id": part["id"]}],
        )
        if result["status"] == "success":
            self.active_ticket["status"] = "In-Progress"
            self._ip_status.configure(text=f"\u2713  Added: {part['name']}", text_color="#27ae60")
            self._refresh_allocated_parts()
            self._search_new_parts()
        else:
            self._ip_status.configure(
                text=result.get("message", "Error adding part."), text_color="#e05c5c")

    def _draft_donor_part(self, part: dict):
        if not self.active_ticket:
            messagebox.showwarning("No Ticket", "Select a ticket from My Tickets first.")
            return
        result = self.app.api.allocate_draft_parts(
            tech_id=self.app.session.get("id"),
            ticket_raw_id=self.active_ticket["raw_id"],
            parts_data=[{"type": "donor", "id": part["id"]}],
        )
        if result["status"] == "success":
            self.active_ticket["status"] = "In-Progress"
            self._ip_status.configure(text=f"\u2713  Added donor: {part['name']}", text_color="#27ae60")
            self._refresh_allocated_parts()
            self._search_donor_parts()
        else:
            self._ip_status.configure(
                text=result.get("message", "Error adding part."), text_color="#e05c5c")

    def _refresh_allocated_parts(self):
        frame = self._allocated_scroll
        for w in frame.winfo_children():
            w.destroy()

        if not self.active_ticket:
            if hasattr(self, '_ip_total_cost_label'):
                self._ip_total_cost_label.configure(text="Total Parts Cost: Rs.0.00")
            return

        res = self.app.api.get_ticket_parts(self.active_ticket["raw_id"])

        if res["status"] != "success" or not res["data"]:
            self.dashboard.empty_label(frame, "No parts allocated yet.")
            self._ip_total_cost_label.configure(text="Total Parts Cost: Rs.0.00")
            return

        total_cost = sum(p["cost"] for p in res["data"])
        self._ip_total_cost_label.configure(text=f"Total Parts Cost: Rs.{total_cost:.2f}")

        _hdrs   = ["#", "Type", "Part Name", "Cost", "Status", "Actions"]
        _widths = [36, 82, 285, 105, 120, 270]

        hdr_row = ctk.CTkFrame(frame, fg_color=("gray80", "gray22"),
                               height=36, corner_radius=6)
        hdr_row.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        hdr_row.grid_propagate(False)
        self.dashboard.table_header_row(hdr_row, _hdrs, _widths)

        for idx, p in enumerate(res["data"]):
            bg  = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")
            row = ctk.CTkFrame(frame, fg_color=bg, corner_radius=6, height=40)
            row.grid(row=idx + 1, column=0, sticky="ew", pady=1)
            row.grid_propagate(False)

            for i, (val, w) in enumerate(
                zip([str(idx + 1), p["type"].upper(), p["name"],
                     f"Rs.{p['cost']:.0f}", p["status"]], _widths[:5])
            ):
                lbl = ctk.CTkLabel(row, text=str(val),
                                   font=ctk.CTkFont(family="Segoe UI", size=14),
                                   width=w, anchor="w")
                if i == 4:
                    lbl.configure(text_color=_PART_STATUS_COLORS.get(val, "#888"))
                lbl.grid(row=0, column=i, padx=(14 if i == 0 else 5, 5), sticky="w")

            if p["status"] == "Draft":
                cell = ctk.CTkFrame(row, fg_color="transparent", width=_widths[5])
                cell.grid(row=0, column=5, padx=4, sticky="w")

                ctk.CTkButton(
                    cell, text="Mark Installed", width=138, height=30,
                    font=ctk.CTkFont(family="Segoe UI", size=13),
                    fg_color="#e67e22", hover_color="#d35400", corner_radius=6,
                    command=lambda uid=p["usage_id"]: self._do_mark_installed(uid),
                ).grid(row=0, column=0, padx=2)

                ctk.CTkButton(
                    cell, text="Remove", width=90, height=30,
                    font=ctk.CTkFont(family="Segoe UI", size=13),
                    fg_color=("#e05c5c", "#a93226"),
                    hover_color=("#c0392b", "#922b21"), corner_radius=6,
                    command=lambda uid=p["usage_id"]: self._do_remove_part(uid),
                ).grid(row=0, column=1, padx=2)

    def _do_mark_installed(self, usage_id: int):
        result = self.app.api.mark_part_installed(
            tech_id=self.app.session.get("id"), usage_id=usage_id)
        if result["status"] == "success":
            self._ip_status.configure(text="Part marked as Installed.", text_color="#e67e22")
            self._refresh_allocated_parts()
        else:
            messagebox.showerror("Error", result.get("message", "Could not mark part installed."))

    def _do_remove_part(self, usage_id: int):
        result = self.app.api.remove_ticket_part(
            user_id=self.app.session.get("id"), usage_id=usage_id)
        if result["status"] == "success":
            self._ip_status.configure(text="Part removed.", text_color="#3498db")
            self._refresh_allocated_parts()
            self._search_donor_parts()
        else:
            messagebox.showerror("Error", result.get("message", "Could not remove part."))

    def _do_complete_ticket(self):
        if not self.active_ticket:
            messagebox.showwarning("No Ticket", "No ticket is currently selected.")
            return

        charge = self._ip_charge_entry.get().strip()
        if not charge:
            self._ip_status.configure(
                text="Enter service charge before completing.", text_color="#e05c5c")
            return
        try:
            float(charge)                            
        except ValueError:
            self._ip_status.configure(text="Service charge must be a number.", text_color="#e05c5c")
            return

        confirm = messagebox.askyesno(
            "Complete Ticket",
            f"Finalize {self.active_ticket['id']}?\n\n"
            f"Service charge: Rs.{charge}\n\n"
            "All parts will be confirmed and stock deducted.\nThis cannot be undone.",
        )
        if not confirm:
            return

        result = self.app.api.complete_ticket(
            tech_id=self.app.session.get("id"),
            ticket_raw_id=self.active_ticket["raw_id"],
            service_charge=charge,
        )
        if result["status"] == "success":
            tid = self.active_ticket["id"]
            self.active_ticket = None                                             
            self._ip_ticket_label.configure(
                text=f"\u2713  Ticket {tid} completed! Select another ticket from My Tickets.",
                text_color="#27ae60",
            )
            self._ip_charge_entry.delete(0, "end")
            self._ip_status.configure(text="")
                                         
            for w in self._allocated_scroll.winfo_children():
                w.destroy()
            for w in self._new_parts_scroll.winfo_children():
                w.destroy()
            for w in self._donor_parts_scroll.winfo_children():
                w.destroy()
            
            self.on_ticket_completed()
        else:
            messagebox.showerror("Error", result.get("message", "Could not complete ticket."))
